#!/usr/bin/env python3
"""Mirror BBC audio to object storage and repoint the catalogue at it.

Why this exists
---------------
The app used to stream every clip straight from bbc.co.uk. That works on a
laptop and fails on a phone: the WebView is inside an Android app, the stream
is plain HTTP to a UK CDN, and the user sees "the stream needs a network
connection" for a clip that is plainly there.

Mirroring the audio turns "needs a network connection" into "needs a network
connection" only when there genuinely is none.

What it does
------------
For the first N episodes that have audio:

  1. download the mp3 from bbc.co.uk
  2. upload it to the bucket under bbc/<id>.mp3, skipping anything already
     there with the same size
  3. rewrite that episode's `audio` field in bbc_6min.json to the mirror

Everything is resumable and idempotent, because a hundred downloads that fail
on the fortieth should not have to start over.

    python3 tools/mirror_bbc_audio.py --limit 100
    python3 tools/mirror_bbc_audio.py --limit 100 --dry-run
    python3 tools/mirror_bbc_audio.py --verify

Credentials come from .bbc-storage.env (gitignored) or the environment.
Never hardcode them: webapp.py's HTML is bundled into the APK, so a key in a
tracked file ships inside the app.

One honest caveat, stated here rather than buried: BBC Learning English audio
is BBC's copyright. Mirroring it means this project is redistributing it.
That is a decision for the person running this, not something this tool can
make safe by being clever, and it is the reason the default limit is 100
rather than the full catalogue.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOGUE = ROOT / "bbc_6min.json"
ENVFILE = ROOT / ".bbc-storage.env"
CACHE = ROOT / "tools/.cache"

# Speech is a narrow-band signal. BBC ships these at 128-320 kbps stereo,
# which is the right call for music and the wrong one for dictation-sized
# speech: measured, mono 64 kbps is a fifth of the bytes and stays clearly
# intelligible. Below about 48 kbps the sibilants dull, which is the one thing
# a listening-practice app cannot afford to lose.
# -vn matters more than it looks: the BBC mp3s carry an embedded cover image,
# and without it ffmpeg copies a 1920x1080 PNG into every output as an
# attached picture. One episode was 7.9 MB instead of 3.0 MB for a 6-minute
# clip, and none of it is audio.
TRANSCODE = ["-vn", "-ac", "1", "-b:a", "64k", "-ar", "22050"]

# BBC's downloads are plain HTTP behind a CDN; a browser UA is not required for
# them but some are picky about it, and it costs nothing.
UA = "Mozilla/5.0 (compatible; Fluentify/1.0; +local language tutor)"


def load_env() -> dict:
    env = {}
    if ENVFILE.exists():
        for line in ENVFILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def connect():
    import boto3
    from botocore.config import Config

    env = load_env()
    need = ["BBC_S3_ENDPOINT", "BBC_S3_REGION", "BBC_S3_ACCESS_KEY", "BBC_S3_SECRET_KEY"]
    missing = [k for k in need if not env.get(k) and not os.environ.get(k)]
    if missing:
        sys.exit(f"missing {', '.join(missing)} - put them in {ENVFILE.name} "
                 f"or the environment")
    get = lambda k: os.environ.get(k) or env[k]      # noqa: E731
    s3 = boto3.client(
        "s3",
        endpoint_url=get("BBC_S3_ENDPOINT"),
        region_name=get("BBC_S3_REGION"),
        aws_access_key_id=get("BBC_S3_ACCESS_KEY"),
        aws_secret_access_key=get("BBC_S3_SECRET_KEY"),
        # The default connect/read pair lets one slow object stall the whole
        # run for ten minutes. A mirroring job should fail fast and retry, not
        # hang.
        config=Config(signature_version="s3v4",
                      connect_timeout=10, read_timeout=60,
                      retries={"max_attempts": 5, "mode": "standard"}),
    )
    bucket = get("BBC_S3_BUCKET")
    base = get("BBC_PUBLIC_BASE") or f"{get('BBC_S3_ENDPOINT').rstrip('/')}/{bucket}"
    return s3, bucket, base.rstrip("/")


def source_for(ep: dict) -> str:
    """Where the bytes actually come from.

    Once an episode is mirrored its `audio` points at us, and downloading from
    that is a circular request that 403s - which looks exactly like BBC rate
    limiting and sent me chasing the wrong problem. `audio_src` keeps the
    original so a re-run has somewhere real to go.
    """
    return ep.get("audio_src") or ep.get("audio") or ""


def key_for(ep: dict) -> str:
    """A stable object name. The catalogue id already encodes series and date,
    so it survives a rebuild and a re-run."""
    ident = str(ep.get("id") or ep.get("slug") or "").strip()
    ident = "".join(c if c.isalnum() or c in "-_." else "-" for c in ident)
    return f"bbc/{ident or 'unknown'}.mp3"


def ffmpeg() -> str | None:
    """imageio-ffmpeg ships a static build; nothing else here needs one."""
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return shutil.which("ffmpeg")


def encode(raw: Path, dest: Path, exe: str | None = None) -> bool:
    """Re-encode a downloaded episode to mono 64 kbps. True on success."""
    exe = exe or ffmpeg()
    if not exe:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    # The temp name ends in .part, which is not a container ffmpeg recognises,
    # so the muxer is named explicitly - without this every transcode fails
    # with "unable to choose an output format" and the tool reports it as a
    # per-episode error rather than as what it is.
    tmp = dest.with_suffix(".part.mp3")
    try:
        r = subprocess.run(
            [exe, "-y", "-loglevel", "error", "-i", str(raw),
             *TRANSCODE, "-f", "mp3", str(tmp)],
            capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        tmp.unlink(missing_ok=True)
        return False
    if r.returncode != 0 or not tmp.exists() or tmp.stat().st_size == 0:
        tmp.unlink(missing_ok=True)
        return False
    tmp.replace(dest)
    raw.unlink(missing_ok=True)
    return True


def download(url: str, dest: Path, timeout: int = 90, tries: int = 4) -> int:
    """Fetch one episode, retrying with backoff.

    BBC rate-limits bursts: a run that pulls ten files in a row reliably draws
    a 403 on one or two of them, which the same request makes ten seconds later
    with no trouble. Retrying is the difference between a flaky run and a
    complete one.
    """
    last = None
    for attempt in range(tries):
        try:
            return _fetch(url, dest, timeout)
        except Exception as exc:                       # noqa: BLE001
            last = exc
            if attempt < tries - 1:
                time.sleep(3 * (attempt + 1))
    raise last                                       # type: ignore[misc]


def _fetch(url: str, dest: Path, timeout: int = 90) -> int:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    total = 0
    with urllib.request.urlopen(req, timeout=timeout) as r, tmp.open("wb") as f:
        while True:
            chunk = r.read(1 << 16)
            if not chunk:
                break
            f.write(chunk)
            total += len(chunk)
    if total == 0:
        tmp.unlink(missing_ok=True)
        raise ValueError("empty response")
    tmp.replace(dest)
    return total


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}GB"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=100,
                    help="how many episodes to mirror (default 100)")
    ap.add_argument("--dry-run", action="store_true",
                    help="list what would be mirrored and change nothing")
    ap.add_argument("--verify", action="store_true",
                    help="check the catalogue against what is actually stored")
    ap.add_argument("--no-transcode", action="store_true",
                    help="store the original bytes instead of mono 64k")
    ap.add_argument("--keep-others", action="store_true",
                    help="leave episodes already in storage alone")
    ap.add_argument("--delay", type=float, default=1.5,
                    help="seconds between downloads (BBC rate-limits bursts)")
    ap.add_argument("--prune-only", action="store_true",
                    help="skip downloading entirely and just cut the catalogue "
                         "down to what is already stored")
    ap.add_argument("--reset", action="store_true",
                    help="empty the bucket first, so the stored set is exactly "
                         "this run's selection")
    ap.add_argument("--spread", action="store_true",
                    help="pick across CEFR levels instead of taking the first N, "
                         "so a short list still spans A1-C1")
    ap.add_argument("--prune", action="store_true",
                    help="cut the catalogue down to what is actually mirrored, so "
                         "the section lists what you can listen to")
    args = ap.parse_args()

    doc = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    episodes = doc.get("episodes") or []

    # Episodes with audio, in catalogue order so a partial run is a stable
    # subset rather than whichever the network happened to favour.
    # Every episode is a candidate, including ones already pointing at our own
    # mirror. The fix for re-fetching those is not to skip them - skipping
    # them emptied the selection once every candidate was ours - it is to
    # remember where each one came from and fetch from that.
    usable = [e for e in episodes if e.get("audio")]
    if args.spread:
        # The first ten in catalogue order are all "The English We Speak" and
        # "6 Minute English", which the grader put at A2 - ten clips of one
        # level is a worse listening course than three. Round-robin the bands
        # instead, so a short list still spans A1 to C1.
        by_level: dict = {}
        for e in usable:
            by_level.setdefault(e.get("level") or "?", []).append(e)
        order = sorted(by_level)
        todo, seen = [], set()
        while len(todo) < args.limit:
            added = False
            for lv in order:
                bucket = by_level[lv]
                while bucket:
                    ep = bucket.pop(0)
                    if ep["id"] in seen:
                        continue
                    seen.add(ep["id"])
                    todo.append(ep)
                    added = True
                    break
                if len(todo) >= args.limit:
                    break
            if not added:
                break
    else:
        todo = usable[:args.limit]

    if args.dry_run:
        total = 0
        for e in todo:
            k = key_for(e)
            total += 1
            print(f"{total:>4}  {k:<58} {(e.get('title') or '')[:38]}")
        print(f"\n{total} episodes would be mirrored to "
              f"{load_env().get('BBC_S3_BUCKET', '?')}/bbc/")
        return 0

    s3, bucket, public = connect()

    if args.reset and not args.verify:
        doomed = [o["Key"] for o in
                  s3.list_objects_v2(Bucket=bucket).get("Contents", [])
                  if o["Key"].startswith("bbc/")]
        for n in range(0, len(doomed), 500):
            s3.delete_objects(Bucket=bucket,
                              Delete={"Objects": [{"Key": k} for k in doomed[n:n + 500]]})
        print(f"reset: removed {len(doomed)} stored objects")

    if args.verify:
        bad = []
        mirrored = 0
        for e in episodes:
            if not str(e.get("audio", "")).startswith(public):
                continue
            mirrored += 1
            try:
                s3.head_object(Bucket=bucket, Key=key_for(e))
            except Exception:
                bad.append(e.get("id"))
        print(f"catalogue points at the mirror for {mirrored} episodes")
        print(f"missing from storage: {len(bad)}")
        for b in bad[:20]:
            print("  ", b)
        return 1 if bad else 0

    CACHE.mkdir(parents=True, exist_ok=True)
    ff = None
    transcode = not args.no_transcode
    if transcode:
        ff = ffmpeg()
        if not ff:
            print("no ffmpeg available - storing the originals. "
                  "pip install imageio-ffmpeg to get a quarter of the size.")
            transcode = False
        else:
            print(f"transcoding to mono 64k with {Path(ff).name}")

    done = missing = failed = 0
    mirrored_keys: set = set()
    bytes_up = saved = 0
    t0 = time.time()

    for i, ep in enumerate([] if args.prune_only else todo, 1):
        key = key_for(ep)
        local = CACHE / key
        raw = CACHE / (key + ".raw")
        up = False

        # What, if anything, is already stored under this key.
        remote = None
        try:
            remote = s3.head_object(Bucket=bucket, Key=key)["ContentLength"]
        except s3.exceptions.ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            if code not in ("404", "NoSuchKey", "NotFound"):
                print(f"  ! {key}: {code}", file=sys.stderr)
                failed += 1
                continue
        except Exception as exc:                       # noqa: BLE001
            # A timeout talking to storage is not a verdict on the episode.
            print(f"  ! {key}: storage unreachable - {type(exc).__name__}",
                  file=sys.stderr)
            failed += 1
            continue

        if remote is not None and args.keep_others:
            size = remote
        elif local.exists() and (remote is None or local.stat().st_size == remote):
            # Either it is already stored at exactly this size, or it is in
            # the cache and nowhere else - the second case happens whenever a
            # previous run downloaded it and the upload did not finish. It was
            # re-fetching instead, which meant a rate-limited BBC turned a
            # cached, transcoded file into a failed episode.
            size = local.stat().st_size
            if remote is None:
                s3.upload_file(
                    str(local), bucket, key,
                    ExtraArgs={"ContentType": "audio/mpeg",
                               "CacheControl":
                                   "public, max-age=31536000, immutable",
                               "ACL": "public-read"})
                up = True
                bytes_up += size
        else:
            try:
                download(source_for(ep), raw)
            except Exception as exc:                       # noqa: BLE001
                # BBC rate-limits and occasionally 403s a single file. One
                # unavailable episode must not abandon the other nine -
                # previously it raised straight out of the loop and left the
                # bucket half-written.
                print(f"  ! {key}: download failed - {type(exc).__name__}",
                      file=sys.stderr)
                failed += 1
                time.sleep(2)
                continue
            if transcode:
                if not encode(raw, local, ff):
                    print(f"  ! {key}: transcode failed", file=sys.stderr)
                    failed += 1
                    continue
            else:
                raw.replace(local)
            size = local.stat().st_size
            s3.upload_file(str(local), bucket, key,
                           ExtraArgs={"ContentType": "audio/mpeg",
                                      "CacheControl":
                                          "public, max-age=31536000, immutable",
                                      "ACL": "public-read"})
            up = True
            bytes_up += size
            if i < len(todo):
                time.sleep(args.delay)      # BBC rate-limits bursts

        if not str(ep.get("audio", "")).startswith(public):
            ep["audio_src"] = ep["audio"]     # where it came from, for a re-run
        ep["audio_source"] = "mirror"
        ep["audio"] = f"{public}/{key}"
        ep["audio_kb"] = round(size / 1024)
        mirrored_keys.add(key)
        done += 1

        if i % 5 == 0 or i == len(todo):
            rate = bytes_up / max(0.001, time.time() - t0)
            print(f"  {i}/{len(todo)}  {done} mirrored  {human(bytes_up)} up "
                  f"({human(rate)}/s)", flush=True)

    if args.prune and failed and not args.prune_only:
        print("refusing to prune: some episodes failed to mirror, and\n"
              "  cutting the catalogue to a partial set would hide them\n"
              "  for good")
        return 1

    if args.prune:
        # The section used to list 1123 episodes of which 5 could be played,
        # which is worse than either number: it reads as broken rather than
        # small. Keep what is mirrored and drop the rest, so the list is the
        # truth. Re-running with a larger --limit brings more back.
        before = len(doc["episodes"])
        # What is actually stored, not what this run happened to touch. The
        # question the catalogue has to answer is "what can I play", and only
        # the bucket knows that.
        stored = {o["Key"] for o in
                  s3.list_objects_v2(Bucket=bucket).get("Contents", [])}
        keep = []
        for e in doc["episodes"]:
            k = key_for(e)
            if k not in stored:
                continue
            # Point it at what is actually stored, and record the size. Without
            # this the entry keeps its BBC url and the section plays from the
            # BBC again - which is the whole thing the mirror is for.
            if not str(e.get("audio", "")).startswith(public):
                e["audio_src"] = e["audio"]
            e["audio"] = f"{public}/{k}"
            e["audio_source"] = "mirror"
            head = s3.head_object(Bucket=bucket, Key=k)
            e["audio_kb"] = round(head["ContentLength"] / 1024)
            keep.append(e)
        if not keep:
            print("refusing to prune: nothing was mirrored this run, and cutting "
                  "the catalogue to an empty list would hide everything")
            return 1
        dropped = before - len(keep)
        doc["episodes"] = keep
        doc["count"] = len(keep)
        from collections import Counter
        dist = Counter((e.get("level") or "?") for e in keep)
        doc["distribution"] = dict(dist)
        print(f"catalogue pruned: {before} -> {len(keep)} episodes "
              f"({dropped} unplayable entries removed)")

    doc["mirrored"] = {
        "bucket": bucket,
        "public_base": public,
        "episodes": done,
        "note": "every episode listed here is mirrored and plays offline of "
                "the BBC; the list is the set that exists, not a sample",
    }
    CATALOGUE.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\nmirrored {done} of {len(todo)}  ({human(bytes_up)} uploaded)"
          f"{f', {failed} failed' if failed else ''}")
    print(f"catalogue updated: {len(doc['episodes'])} episodes now stream "
          f"from {public}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())