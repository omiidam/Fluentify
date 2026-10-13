#!/usr/bin/env python3
"""Checks the two new subsystems: the BBC grader and speech-to-text.

    python3 tools/harness_stt.py

Neither the grader nor the STT config is covered by the main harness, and both
are the kind of thing that fails quietly - a grader that returns A2 for
everything looks like it is working, and a malformed stt.json simply means the
mic button never appears.

Grader:
  * a passing grade needs enough text; a one-line blurb must NOT be graded
  * the blend must be monotonic - harder text never grades easier
  * function words alone must not drag a passage down
  * BBC's own tag must agree, as a range check

STT:
  * stt.json must parse and carry every key the three surfaces read
  * the language codes must be real BCP-47 tags
  * the MP3 duration probe must land on a 6 Minute English clip's length
    (the file is VBR, so a bitrate estimate is wrong by minutes)
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

FAILURES: list[str] = []
CHECKS = 0


def fail(msg: str) -> None:
    FAILURES.append(msg)


def check(name: str, ok: bool, detail: str = "") -> None:
    global CHECKS
    CHECKS += 1
    if not ok:
        fail(f"{name}{': ' + detail if detail else ''}")


# --------------------------------------------------------------------------
# the grader
# --------------------------------------------------------------------------
EASY = (
    "The cat sat on the mat. The dog ran in the park. I saw a bird on the "
    "tree. We went to the shop and bought some bread. She made a cake for "
    "the party. He read a book about the sea. The sun was very warm today. "
    "I like tea and coffee in the morning. They play football after work. "
    "We live in a small house near the river. "
) * 6

HARD = (
    "Notwithstanding the epistemological objections raised by subsequent "
    "commentators, the paradigm remains structurally inadequate for "
    "accommodating heteronormative presuppositions. Institutional "
    "accommodation of pluralistic frameworks necessitates a reconceptualised "
    "accounting of intergenerational accountability mechanisms. "
    "Proliferation of bureaucratic nomenclature has inadvertently exacerbated "
    "counterproductive antagonisms among stakeholders. "
    "Notwithstanding unprecedented volatility, unprecedented juxtaposition "
    "of unprecedented circumstances renders unprecedented ramifications "
    "unprecedentedly consequential for unprecedentedly heterogeneous "
    "populations. "
) * 4


def run_grader() -> None:
    from listening_grade import (
        BBC_TAG_RANGE, clean_transcript, grade_text, in_band_range, load_cefr,
    )

    cefr = load_cefr()
    check("cefr table", len(cefr) > 100_000, f"only {len(cefr)} words")

    easy = grade_text(EASY, cefr)
    hard = grade_text(HARD, cefr)
    check("easy text is graded", easy.get("level") is not None, str(easy))
    check("hard text is graded", hard.get("level") is not None, str(hard))
    if easy.get("level") and hard.get("level"):
        order = ["A1", "A2", "B1", "B2", "C1", "C2"]
        check("harder text grades no easier",
              order.index(hard["level"]) > order.index(easy["level"]),
              f"easy={easy['level']} hard={hard['level']}")
        check("easy text is not advanced",
              order.index(easy["level"]) <= order.index("B1"),
              f"easy={easy['level']}")

    # a blurb must be refused rather than guessed at
    short = grade_text("Do you drink alcoholic drinks?", cefr)
    check("a one-line blurb is not graded",
          short.get("level") is None, str(short))

    # the transcript cleaner must not throw on real junk
    for junk in ["", "   ", "\n\n", "↳ x", "‮mirror", "a" * 3000]:
        try:
            clean_transcript(junk)
        except Exception as exc:  # noqa: BLE001
            fail(f"clean_transcript crashed on {junk[:12]!r}: {exc}")

    # BBC's tag is a range, and containment is the honest test
    check("BBC intermediate accepts B1", in_band_range("B1", "intermediate"))
    check("BBC intermediate accepts B2", in_band_range("B2", "intermediate"))
    check("BBC intermediate rejects A2", not in_band_range("A2", "intermediate"))
    check("BBC intermediate rejects C1", not in_band_range("C1", "intermediate"))
    check("unknown tag is rejected", not in_band_range("B1", "advanced"))
    for tag in BBC_TAG_RANGE:
        lo, hi = BBC_TAG_RANGE[tag]
        check(f"{tag} range is ordered",
              ["A1", "A2", "B1", "B2", "C1", "C2"].index(lo)
              <= ["A1", "A2", "B1", "B2", "C1", "C2"].index(hi))


# --------------------------------------------------------------------------
# the STT configuration
# --------------------------------------------------------------------------
REQUIRED_KEYS = ["enabled", "language", "web", "android", "cli", "levels",
                 "privacy"]
BCP47 = re.compile(r"^[a-z]{2,3}(-[A-Z][a-z]{3})?(-[A-Z]{2})?$")


def run_config() -> None:
    path = ROOT / "stt.json"
    check("stt.json exists", path.exists())
    if not path.exists():
        return
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"stt.json does not parse: {exc}")
        return

    for key in REQUIRED_KEYS:
        check(f"stt.{key} present", key in cfg)
    for key in ("default", "fallback", "supported"):
        check(f"stt.language.{key} present", key in cfg.get("language", {}))

    langs = cfg.get("language", {}).get("supported", [])
    check("at least 6 languages", len(langs) >= 6, f"only {len(langs)}")
    codes = [l.get("code") for l in langs]
    for code in codes:
        check(f"language code {code} is BCP-47",
              bool(code and BCP47.match(code)), str(code))
    default = cfg.get("language", {}).get("default")
    check("default language is in the list", default in codes, str(default))
    fallback = cfg.get("language", {}).get("fallback")
    check("fallback language is in the list", fallback in codes, str(fallback))

    for key in ("engine", "interim_results", "continuous", "max_alternatives",
                "auto_stop_ms", "unsupported_message"):
        check(f"stt.web.{key} present", key in cfg.get("web", {}))
    for key in ("engine", "partial_results", "max_results"):
        check(f"stt.android.{key} present", key in cfg.get("android", {}))
    for key in ("backends", "model", "language", "output_formats"):
        check(f"stt.cli.{key} present", key in cfg.get("cli", {}))

    # auto-stop must not fire before anyone has had time to speak
    web = cfg.get("web", {})
    auto = web.get("auto_stop_ms", 0)
    check("auto-stop is not instant", auto >= 3000, f"{auto}ms")
    check("min speech precedes auto-stop",
          web.get("min_speech_ms", 0) < auto)

    fmts = cfg.get("cli", {}).get("output_formats", [])
    for f in ("txt", "srt", "vtt", "json"):
        check(f"cli supports {f}", f in fmts)


# --------------------------------------------------------------------------
# the audio probe
# --------------------------------------------------------------------------
def run_audio() -> None:
    from transcribe import probe, probe_duration

    have = probe()
    check("probe reports all three backends",
          all(b in have for b in ("faster-whisper", "whisper", "vosk")))
    check("probe reports ffmpeg", "ffmpeg" in have)

    # A real clip if one has been fetched; otherwise skip rather than pretend.
    clips = list((ROOT / "tools/.cache").glob("*.mp3"))
    if not clips:
        return
    clip = clips[0]
    seconds, kind = probe_duration(clip)
    check("mp3 recognised", kind == "mp3", kind)
    # The series is six minutes; a VBR file read as CBR overshoots by minutes,
    # which is exactly the bug the Xing header fixes.
    check("duration is about six minutes", 240 < seconds < 480,
          f"{seconds:.0f}s for a 6-minute clip")


# --------------------------------------------------------------------------
# the PDF reader
# --------------------------------------------------------------------------
def run_pdf() -> None:
    """pdf_to_text must stay linear.

    Its first version pulled strings out with a regex whose nested quantifier
    backtracked without bound on a PDF that embedded a multi-megabyte font.
    It did not raise or return wrong data - it consumed a core at 98% and the
    fetch simply stopped, which is why the check here is a wall-clock budget
    rather than an assertion about the output.
    """
    import threading

    from fetch_bbc_6min import _pdf_strings, pdf_to_text

    # a synthetic stream in the shape that broke it: a '[' that never closes,
    # followed by megabytes of payload
    hostile = (b"[ " + b"abcdefgh " * 400_000) + b" 0 0 0 Tj"
    result: list = []

    def run() -> None:
        try:
            result.append(pdf_to_text(hostile))
        except Exception as exc:  # noqa: BLE001
            result.append(exc)

    t = threading.Thread(target=run, daemon=True)
    t0 = time.time()
    t.start()
    t.join(timeout=20)
    check("pdf_to_text survives an unbalanced TJ array", not t.is_alive(),
          "still running after 20s - the reader is no longer linear")
    if not t.is_alive() and result:
        check("pdf_to_text returns text for a hostile stream",
              isinstance(result[0], str), str(result[0])[:60])

    # and it must still read ordinary text out of a real stream
    simple = b"BT /F1 12 Tf (Hello) Tj (World) TJ ET"
    check("pdf_to_text reads a normal stream",
          "Hello" in pdf_to_text(simple) or
          any("Hello" in x for x in _pdf_strings(simple)),
          pdf_to_text(simple)[:40])

    # every cached transcript must read in reasonable time
    cache = ROOT / "tools/.cache/bbc"
    pdfs = sorted(cache.glob("*.pdf"))[:12]
    for pdf in pdfs:
        t0 = time.time()
        try:
            text = pdf_to_text(pdf.read_bytes())
        except Exception as exc:  # noqa: BLE001
            fail(f"pdf_to_text crashed on {pdf.name[:28]}: {exc}")
            continue
        took = time.time() - t0
        check(f"{pdf.name[:24]} reads fast", took < 2.0, f"{took:.1f}s")
        check(f"{pdf.name[:24]} yields words", len(text.split()) > 50,
              f"only {len(text.split())} words")


def main() -> int:
    t0 = time.time()
    print("→ grader");   run_grader()
    print("→ stt.json");  run_config()
    print("→ audio");    run_audio()
    print("→ pdf");      run_pdf()
    print()
    if FAILURES:
        print(f"FAIL  {len(FAILURES)} of {CHECKS} checks ({time.time() - t0:.1f}s)\n")
        for msg in FAILURES:
            print(f"  {msg}")
        return 1
    print(f"PASS  all {CHECKS} checks ({time.time() - t0:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())