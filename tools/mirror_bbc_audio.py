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
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOGUE = ROOT / "bbc_6min.json"
ENVFILE = ROOT / ".bbc-storage.env"
CACHE = ROOT / "tools/.cache"

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
        config=Config(signature_version="s3v4",
                      retries={"max_attempts": 3, "mode": "standard"}),
    )
    bucket = get("BBC_S3_BUCKET")
    base = get("BBC_PUBLIC_BASE") or f"{get('BBC_S3_ENDPOINT').rstrip('/')}/{bucket}"
    return s3, bucket, base.rstrip("/")


def key_for(ep: dict) -> str:
    """A stable object name. The catalogue id already encodes series and date,
    so it survives a rebuild and a re-run."""
    ident = str(ep.get("id") or ep.get("slug") or "").strip()
    ident = "".join(c if c.isalnum() or c in "-_." else "-" for c in ident)
    return f"bbc/{ident or 'unknown'}.mp3"


def download(url: str, dest: Path, timeout: int = 90) -> int:
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
    args = ap.parse_args()

    doc = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    episodes = doc.get("episodes") or []

    # Episodes with audio, in catalogue order so a partial run is a stable
    # subset rather than whichever the network happened to favour.
    todo = [e for e in episodes if e.get("audio")][:args.limit]

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
    done = missing = failed = 0
    bytes_up = 0
    t0 = time.time()

    for i, ep in enumerate(todo, 1):
        key = key_for(ep)
        local = CACHE / key

        try:
            head = s3.head_object(Bucket=bucket, Key=key)
            remote = head["ContentLength"]
            if not local.exists() or local.stat().st_size != remote:
                download(ep["audio"], local)
            size = remote
        except s3.exceptions.ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            if code not in ("404", "NoSuchKey", "NotFound"):
                print(f"  ! {key}: {code}", file=sys.stderr)
                failed += 1
                continue
            size = download(ep["audio"], local)
            bytes_up += size
            s3.upload_file(
                str(local), bucket, key,
                ExtraArgs={"ContentType": "audio/mpeg",
                           "CacheControl": "public, max-age=31536000, immutable",
                           "ACL": "public-read"},
            )
        except Exception as exc:                       # network, DNS, timeout
            print(f"  ! {key}: {type(exc).__name__}: {exc}", file=sys.stderr)
            failed += 1
            continue

        ep["audio_source"] = "mirror"
        ep["audio"] = f"{public}/{key}"
        done += 1

        if i % 10 == 0 or i == len(todo):
            rate = bytes_up / max(0.001, time.time() - t0)
            print(f"  {i}/{len(todo)}  {done} mirrored  {human(bytes_up)} up "
                  f"({human(rate)}/s)", flush=True)

    doc["mirrored"] = {
        "bucket": bucket,
        "public_base": public,
        "episodes": done,
        "note": "audio served from storage; `audio_source` is 'mirror' for "
                "these and 'bbc' for the rest",
    }
    CATALOGUE.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\nmirrored {done} of {len(todo)}  ({human(bytes_up)} uploaded)"
          f"{f', {failed} failed' if failed else ''}")
    print(f"catalogue updated: {done} episodes now stream from {public}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())