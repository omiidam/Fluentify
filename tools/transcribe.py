#!/usr/bin/env python3
"""Transcribe audio to text from the command line, then grade it.

    python3 tools/transcribe.py --check
    python3 tools/transcribe.py lesson.mp3
    python3 tools/transcribe.py lesson.mp3 --model small --format srt
    python3 tools/transcribe.py https://…/clip.mp3 --lang en

Backends are probed, never assumed. Nothing is installed by default in this
repo, so the tool says what is missing and how to add it instead of failing
silently:

    pip install faster-whisper     best quality, int8, CPU-only works
    pip install openai-whisper     the reference implementation
    pip install vosk               lightest, good offline accuracy

Audio: WAV is read with the stdlib. MP3 length is probed by parsing frames, so
you get told the duration before a model starts. Anything else is passed
through to ffmpeg if it happens to be installed.

The transcript is then graded A2→C1 with listening_grade.py — the same
grader that grades the BBC catalogue, so a clip you record yourself lands on
the same scale.
"""

from __future__ import annotations

import argparse
import json
import re
import struct
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from listening_grade import grade_text, load_cefr  # noqa: E402

CONFIG = ROOT / "stt.json"
CACHE = ROOT / "tools/.cache"

BACKEND_HINTS = {
    "faster-whisper": "pip install faster-whisper",
    "whisper": "pip install openai-whisper",
    "vosk": "pip install vosk",
}


# --------------------------------------------------------------------------
# config
# --------------------------------------------------------------------------
def load_config() -> dict:
    if not CONFIG.exists():
        return {}
    return json.loads(CONFIG.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# backends
# --------------------------------------------------------------------------
def probe() -> dict:
    """Which transcription backends are importable right now."""
    import importlib.util

    found = {}
    for name, module in (("faster-whisper", "faster_whisper"),
                         ("whisper", "whisper"),
                         ("vosk", "vosk")):
        try:
            found[name] = importlib.util.find_spec(module) is not None
        except (ImportError, ValueError):
            found[name] = False
    found["ffmpeg"] = _which("ffmpeg") is not None
    return found


def _which(cmd: str) -> str | None:
    from shutil import which

    return which(cmd)


def transcribe(path: Path, cfg: dict, model: str | None, lang: str | None):
    """Run whichever backend is available, newest interface first."""
    cli_cfg = cfg.get("cli", {})
    model = model or cli_cfg.get("model", "base")
    lang = lang or cli_cfg.get("language", "en")
    have = probe()

    if have["faster-whisper"]:
        return _faster_whisper(path, model, lang, cli_cfg)
    if have["whisper"]:
        return _whisper(path, model, lang, cli_cfg)
    if have["vosk"]:
        return _vosk(path, lang, cli_cfg)

    missing = [BACKEND_HINTS[b] for b in ("faster-whisper", "whisper", "vosk")
               if not have[b]]
    sys.exit(
        "No speech-to-text backend is installed.\n"
        "  Install one of:\n    " + "\n    ".join(missing) +
        "\n  Then re-run. `python3 tools/transcribe.py --check` shows the state."
    )


def _faster_whisper(path: Path, model: str, lang: str, cli_cfg: dict):
    from faster_whisper import WhisperModel

    cache = Path(cli_cfg.get("model_dir", str(CACHE / "models")))
    cache.mkdir(parents=True, exist_ok=True)
    print(f"loading faster-whisper '{model}' …")
    wm = WhisperModel(model, device="auto", compute_type=cli_cfg.get("compute_type", "int8"),
                      download_root=str(cache))
    segments, info = wm.transcribe(
        str(path), language=None if lang == "auto" else lang,
        beam_size=cli_cfg.get("beam_size", 5),
        vad_filter=cli_cfg.get("vad_filter", True))
    out = []
    for seg in segments:
        out.append({"start": round(seg.start, 2), "end": round(seg.end, 2),
                    "text": seg.text.strip()})
    return out, {"language": info.language, "probability": round(info.language_probability, 3)}


def _whisper(path: Path, model: str, lang: str, cli_cfg: dict):
    import whisper

    cache = Path(cli_cfg.get("model_dir", str(CACHE / "models")))
    cache.mkdir(parents=True, exist_ok=True)
    print(f"loading openai-whisper '{model}' …")
    wm = whisper.load_model(model, download_root=str(cache))
    result = wm.transcribe(str(path), language=None if lang == "auto" else lang)
    out = [{"start": round(s["start"], 2), "end": round(s["end"], 2),
            "text": s["text"].strip()} for s in result.get("segments", [])]
    return out, {"language": result.get("language")}


def _vosk(path: Path, lang: str, cli_cfg: dict):
    import json as _json

    import wave

    from vosk import KaldiRecognizer, Model

    models = Path(cli_cfg.get("model_dir", str(CACHE / "models")))
    mdir = next((p for p in models.glob(f"vosk-model-*") if p.is_dir()), None)
    if not mdir:
        sys.exit(f"no vosk model in {models} — download one, e.g.\n"
                 "  wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
    if path.suffix.lower() != ".wav":
        sys.exit("vosk reads WAV only — convert first, or use faster-whisper")
    model = Model(str(mdir))
    rec = KaldiRecognizer(model, 16000)
    rec.SetWords(True)
    words = []
    with wave.open(str(path), "rb") as w:
        while True:
            data = w.readframes(4000)
            if not data:
                break
            if rec.AcceptWaveform(data):
                words.extend(_json.loads(rec.Result()).get("result", []))
        words.extend(_json.loads(rec.FinalResult()).get("result", []))
    out, cur = [], []
    for w_ in words:
        cur.append(w_)
        if w_.get("end", 0) - (cur[0].get("start", 0)) > 8:
            out.append({"start": cur[0]["start"], "end": cur[-1]["end"],
                        "text": " ".join(x["word"] for x in cur)})
            cur = []
    if cur:
        out.append({"start": cur[0]["start"], "end": cur[-1]["end"],
                    "text": " ".join(x["word"] for x in cur)})
    return out, {"model": mdir.name}


# --------------------------------------------------------------------------
# audio
# --------------------------------------------------------------------------
def fetch(url: str) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    dest = CACHE / re.sub(r"[^A-Za-z0-9._-]", "_", url.split("/")[-1]) or "clip.mp3"
    if not dest.exists() or dest.stat().st_size < 1000:
        print(f"downloading {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "Fluentify/1.0"})
        with urllib.request.urlopen(req, timeout=90) as r:
            dest.write_bytes(r.read())
    return dest


def probe_duration(path: Path) -> tuple[float, str]:
    """(seconds, format) using only the stdlib where possible."""
    import wave

    if path.suffix.lower() == ".wav":
        try:
            with wave.open(str(path), "rb") as w:
                return w.getnframes() / float(w.getframerate()), "wav"
        except wave.Error:
            pass
    head = path.open("rb").read(4096)
    if head[:3] == b"ID3" or (len(head) > 1 and head[0] == 0xFF and head[1] & 0xE0 == 0xE0):
        return _mp3_duration(path), "mp3"
    if _which("ffmpeg"):
        try:
            out = subprocess.run(
                ["ffmpeg", "-i", str(path)], capture_output=True, text=True, timeout=30).stderr
            m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", out)
            if m:
                h, mi, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
                return h * 3600 + mi * 60 + s, "ffmpeg"
        except (subprocess.SubprocessError, OSError):
            pass
    return 0.0, "unknown"


_MP3_BITRATES = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0]
_MP3_RATES = {0: [44100, 48000, 32000], 2: [22050, 24000, 16000], 3: [11025, 12000, 8000]}


def _mp3_header(data: bytes, i: int):
    """Validate a frame header at offset i, or return None.

    0xFF bytes occur constantly inside the audio payload, so a single header
    match is not a frame. Returning None on a mismatch is what keeps the walk
    from inventing eight minutes of silence.
    """
    if i + 4 > len(data):
        return None
    h = data[i:i + 4]
    if h[0] != 0xFF or (h[1] & 0xE0) != 0xE0:
        return None
    ver = (h[1] >> 3) & 3
    layer = (h[1] >> 1) & 3
    if ver == 1 or layer == 0:          # reserved MPEG version / layer
        return None
    br_idx = (h[2] >> 4) & 0xF
    sr_idx = (h[2] >> 2) & 3
    if br_idx in (0, 15) or sr_idx == 3:   # free-form / bad bitrate / bad rate
        return None
    rates = _MPG_RATES.get(ver, _MPP_RATES)
    rate = rates[sr_idx]
    bitrate = _MP3_BITRATES[br_idx] * 1000
    samples = 1152 if ver == 3 else 576
    return samples, rate, bitrate, samples * bitrate // rate // 8


# Where the Xing/Info tag sits after a frame header, by MPEG version and
# channel mode. It carries the true frame count, which is the only reliable
# duration for a variable-bitrate file.
_XING_OFFSET = {(3, 0): 21, (3, 1): 36, (2, 0): 13, (2, 1): 21}


def _first_frame(data: bytes) -> int:
    """Offset of the first real frame, skipping any ID3v2 tag."""
    i = 0
    if data[:3] == b"ID3" and len(data) > 10:
        size = ((data[6] & 0x7F) << 21 | (data[7] & 0x7F) << 14
                | (data[8] & 0x7F) << 7 | (data[9] & 0x7F))
        i = 10 + size
    return i


def _xing_frames(data: bytes) -> int | None:
    """Frame count from the Xing/Info VBR header, or None.

    The tag sits *inside* the first frame, at an offset that depends on the
    MPEG version and channel mode, so it has to be read from that frame's own
    header rather than guessed at a fixed position.
    """
    base = _first_frame(data)
    h = data[base + 1:base + 4]
    if len(h) < 3 or h[0] & 0xE0 != 0xE0:
        return None
    version = (h[0] >> 3) & 3
    mode = (h[2] >> 6) & 3          # 0 = stereo, 3 = mono
    side_info = _XING_OFFSET.get((version, 0 if mode == 3 else 1))
    if side_info is None:
        return None
    off = base + side_info
    if data[off:off + 4] not in (b"Xing", b"Info"):
        return None
    flags = struct.unpack(">I", data[off + 4:off + 8])[0]
    if flags & 1:
        return struct.unpack(">I", data[off + 8:off + 12])[0]
    return None


def _mp3_duration(path: Path) -> float:
    """Duration of an MP3 without ffmpeg.

    Variable bitrate is the normal case for spoken-word files, so a bitrate
    estimate is hopeless here: this file's frames step through 128, 224, 256
    and 192 kbit/s. The Xing header's frame count is exact, and the frame walk
    is only the fallback for files that carry no VBR header.
    """
    data = path.read_bytes()

    i = _first_frame(data)
    frames = _xing_frames(data)
    frame = _mp3_header(data, i)
    if frames and frame:
        samples, rate = frame[0], frame[1]
        return frames * samples / rate

    total = 0.0
    guard = 0
    while i + 4 <= len(data) and guard < 4_000_000:
        guard += 1
        frame = _mp3_header(data, i)
        if frame is None:
            nxt = data.find(b"\xff", i + 1)
            if nxt < 0:
                break
            i = nxt
            continue
        samples, rate, bitrate, length = frame
        nxt = _mp3_header(data, i + length)
        if nxt is None and length > 0:
            # allow one gap, then resync from the next candidate
            scan = data.find(b"\xff", i + length)
            if scan < 0:
                break
            i = scan
            continue
        total += samples * 8 / rate
        i += max(1, length)
    return total


_MPG_RATES = {3: [44100, 48000, 32000]}
_MPP_RATES = {2: [22050, 24000, 16000], 0: [11025, 12000, 8000]}


# --------------------------------------------------------------------------
# output
# --------------------------------------------------------------------------
def _ts(seconds: float, comma: bool = True) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{',' if comma else '.'}{ms:03d}"


def render(segments: list[dict], fmt: str, meta: dict) -> str:
    if fmt == "txt":
        return "\n".join(s["text"] for s in segments)
    if fmt == "json":
        return json.dumps({"segments": segments, **meta}, ensure_ascii=False, indent=2)
    if fmt == "srt":
        sep, end = "\n\n", lambda s: _ts(s, True)
        counter = iter(range(1, len(segments) + 1))
        return sep.join(f"{next(counter)}\n{end(s['start'])} --> {end(s['end'])}\n{s['text']}"
                        for s in segments)
    if fmt == "vtt":
        head = "WEBVTT\n\n"
        return head + "\n\n".join(f"{_ts(s['start'], False)} --> {_ts(s['end'], False)}\n{s['text']}"
                                 for s in segments)
    raise SystemExit(f"unknown format {fmt!r}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audio", nargs="?", help="a local file or an http(s) URL")
    ap.add_argument("--model", help="override the model in stt.json")
    ap.add_argument("--lang", help="language code, or 'auto'")
    ap.add_argument("--format", "-f", default="txt",
                    help="txt | srt | vtt | json (default txt)")
    ap.add_argument("--out", "-o", help="write here instead of stdout")
    ap.add_argument("--check", action="store_true",
                    help="report which backends and models are available")
    args = ap.parse_args()

    cfg = load_config()

    if args.check:
        have = probe()
        print("speech-to-text backends")
        for name in ("faster-whisper", "whisper", "vosk"):
            mark = "available" if have[name] else "not installed"
            print(f"  {name:<16} {mark:<14} {BACKEND_HINTS[name]}")
        print(f"  {'ffmpeg':<16} {'available' if have['ffmpeg'] else 'not installed':<14} "
              "only needed for formats other than wav/mp3")
        print(f"\nconfig: {CONFIG.relative_to(ROOT)} "
              f"(model={cfg.get('cli', {}).get('model')}, "
              f"language={cfg.get('cli', {}).get('language')})")
        print("the web app and the Android app need none of these - they use "
              "the browser's\nWeb Speech API and Android's on-device recogniser.")
        return 0

    if not args.audio:
        ap.error("an audio file or URL is required (or use --check)")

    started = time.time()
    path = fetch(args.audio) if args.audio.startswith(("http://", "https://")) \
        else Path(args.audio)
    if not path.exists():
        sys.exit(f"no such file: {path}")

    seconds, fmt = probe_duration(path)
    print(f"audio: {path.name}  {seconds:.1f}s  ({fmt})")
    if seconds:
        print(f"speaking rate will be reported against {seconds:.0f}s of audio")

    segments, meta = transcribe(path, cfg, args.model, args.lang)
    text = render(segments, args.format, meta)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(text)

    took = time.time() - started
    print(f"\n{len(segments)} segments in {took:.1f}s"
          + (f" ({len(text.split()) / took:.1f}x real time)" if took else ""),
          file=sys.stderr)

    if cfg.get("cli", {}).get("grade_transcript", True):
        cefr = load_cefr()
        grade = grade_text(" ".join(s["text"] for s in segments), cefr,
                           wpm=(len(" ".join(s["text"] for s in segments).split())
                                / max(1.0, seconds) * 60 if seconds else None))
        print(f"\nCEFR: {grade.get('level')}", file=sys.stderr)
        for key in ("avg_sentence", "clauses_per_sentence", "challenge_pct",
                    "c1c2_pct", "unique_content", "total_words"):
            if key in grade:
                print(f"  {key:<20} {grade[key]}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())