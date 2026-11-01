#!/usr/bin/env python3
"""Add a local folder of BBC 6 Minute English episodes to the catalogue.

Why this exists
---------------
bbc_6min.json is built from the two BBC RSS feeds, so it only ever knows the
episodes BBC still lists. The 2008 run of 6 Minute English has been dropped
from those feeds entirely, and the only copy on this machine is a folder of
pairs: a 3 MB mp3 and the printed worksheet page as a PDF.

This turns each pair into the same thing the mirror tool produces - audio and
read-along text in the bucket, one episode in the catalogue - so the 2008
episodes appear in the app beside the ones fetched from the feed, with the
same play button, the same transcript reader and the same level tabs.

    python3 tools/add_bbc_2008.py --dir "/path/to/6 Minute English 2008 [www.languagecentre.ir]/6 Minute English 2008 [www.languagecentre.ir]"
    python3 tools/add_bbc_2008.py --dir ... --dry-run     # show the plan
    python3 tools/add_bbc_2008.py --verify                # catalogue vs bucket

On the audio: these mp3s are already mono 64 kb/s, which is exactly what
mirror_bbc_audio.py encodes to, so the bytes are uploaded as they are. Running
them through ffmpeg would spend twenty minutes to re-encode 64 kb/s to 64 kb/s
and lose a little to generation loss on the way.

On the transcript: the 2008 pages print the introduction, the question and the
"Vocabulary from the programme" list, not a verbatim script - the scripts only
started with the relaunch. So the reader shows what the page actually has,
which is still the useful half: every phrase with its explanation and example.
The page is a browser printout, so it arrives wrapped in site navigation; the
boilerplate is stripped in clean_page() below rather than shown to the reader.

Credentials come from .bbc-storage.env (gitignored) or the environment, the
same four names mirror_bbc_audio.py uses. Never hardcode them: webapp.py's
HTML is bundled into the APK, so a key in a tracked file ships inside the app.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOGUE = ROOT / "bbc_6min.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mirror_bbc_audio as mirror  # noqa: E402  (connect, load_env, key rules)
from listening_grade import grade_text, load_cefr  # noqa: E402

SERIES = "6 Minute English"
SERIES_EXPECTED = "B1-B2"
# 2008 files are named "2008-03-12 - 6 Minute English - Air travel.mp3", with
# the languagecentre suffix on some of them and not on others.
NAME = re.compile(r"^(\d{4}-\d{2}-\d{2}) - 6 Minute English - (?P<title>.+?)"
                  r"(?: \[www\.languagecentre\.ir\])?$")

# Every line of a printed BBC page that is not part of the episode.
BOILERPLATE = [
    re.compile(p) for p in (
        r"^BBC World Service \| Learning English",
        r"^This page has been archived",
        r"^Find out more about page archiving",
        r"^(Home|News|Sport|Radio|TV|Weather|Languages)(\s+(Home|News|Sport|Radio|TV|Weather|Languages))*$",
        r"^More 6 Minute English$",
        r"^[A-Z][a-z]+ (-|–) [A-Z][a-z]+ \d{4}$",
        r"^-+$",
        r"^- .+$",
        r"^Listen$",
        r"^\[an error occurred while processing this directive\]$",
        r"^Download this programme",
        r"^Extras$",
        r"^\*?The BBC is not responsible for the content",
        r"^\^+ ?Back to top.*$",
        r"^\d+ of \d+$",
        r"^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} [AP]M$",
        r"^http://www\.bbc\.co\.uk/.*$",
        r"^https?://.*$",
        r"^Page last updated.*$",
    )
]


def clean_page(text: str, title: str) -> str:
    """The episode page with the site furniture taken off it.

    The PDF is a browser printout, so pdftotext -layout returns the navigation
    columns, the archived-page banner, the footer with "1 of 2" and a
    timestamp, and the episode buried in the right-hand column four hundred
    spaces in. Everything is left-aligned and blank lines are collapsed, which
    is what makes it readable in a phone-width reader.
    """
    lines = []
    for raw in text.replace("\f", "\n").splitlines():
        line = " ".join(raw.split())
        if not line:
            continue
        if any(p.match(line) for p in BOILERPLATE):
            continue
        lines.append(line)

    # The navigation lists the other episodes above the title; the title line
    # is the start of the page proper. If it never turns up, keep everything
    # rather than guessing at a trim.
    for i, line in enumerate(lines):
        if line.lower() == title.lower():
            lines = lines[i:]
            break

    out, blank = [], False
    for line in lines:
        out.append(line)
        blank = False
    return "\n".join(out).strip()


def read_pdf(path: Path, title: str) -> str:
    """Readable text out of the worksheet PDF.

    pdftotext does the job here and is already a system dependency; the
    project's own reader (transcript_text.py) reconstructs the column layout
    of the newer BBC PDFs and turns these older ones into runs of "000034" -
    it was reading the layout operators, not the text, because these pages
    carry their text as a compressed object stream it does not walk.
    """
    try:
        r = subprocess.run(["pdftotext", "-layout", str(path), "-"],
                           capture_output=True, text=True, timeout=120)
        if r.returncode == 0 and r.stdout.strip():
            return clean_page(r.stdout, title)
    except (OSError, subprocess.TimeoutExpired):
        pass
    return ""


def slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s or "episode"


def episode_id(date: str, title: str) -> str:
    return f"{SERIES}-{date}-{slug(title)}"


def blurb_from(text: str, title: str) -> str:
    """The introduction paragraph, trimmed to something a list row can hold."""
    body = [l for l in text.splitlines() if l.lower() != title.lower()]
    para = ""
    for line in body:
        if line.lower().startswith(("this week's question", "vocabulary from")):
            break
        para = (para + " " + line).strip()
        if len(para) > 240:
            break
    if len(para) > 240:
        para = para[:237].rsplit(" ", 1)[0] + "..."
    return para


def duration_of(size: int, kbps: int = 64) -> str:
    """m:ss from the file size, for the bitrate these files ship at."""
    seconds = int(size * 8 / (kbps * 1000))
    return f"{seconds // 60}:{seconds % 60:02d}"


def pairs(folder: Path) -> list[tuple[Path, Path, str, str]]:
    """(mp3, pdf-or-None, date, title) for every audio file in the folder."""
    found = {}
    for p in sorted(folder.iterdir()):
        m = NAME.match(p.stem)
        if not m:
            continue
        key = (m.group(1), m.group("title"))
        found.setdefault(key, {})[p.suffix.lower()] = p
    out = []
    for (date, title), files in sorted(found.items()):
        mp3 = files.get(".mp3")
        if not mp3:
            continue
        out.append((mp3, files.get(".pdf"), date, title))
    return out


def build(folder: Path, cefr: dict, limit: int = 0) -> list[dict]:
    """Catalogue entries for the folder, graded and with the text attached."""
    entries = []
    for mp3, pdf, date, title in pairs(folder):
        text = read_pdf(pdf, title) if pdf else ""
        grade = grade_text(text, cefr) if len(text.split()) >= 60 else {}
        level = grade.get("level") or SERIES_EXPECTED.split("-")[0]
        entries.append({
            "id": episode_id(date, title),
            "title": title,
            "blurb": blurb_from(text, title),
            "url": "",
            "year": "2008",
            "series": SERIES,
            "series_expected": SERIES_EXPECTED,
            "level": level,
            "duration": duration_of(mp3.stat().st_size),
            "source_file": mp3.name,
            "transcript_words": len(text.split()),
            "_text": text,
        })
        if limit and len(entries) >= limit:
            break
    return entries


def stored_size(s3, bucket: str, key: str) -> int:
    """Size of an object already in the bucket, or 0 if it is not there."""
    try:
        return int(s3.head_object(Bucket=bucket, Key=key)["ContentLength"])
    except Exception:                                  # noqa: BLE001
        return 0


def upload(s3, bucket: str, public: str, mp3: Path, ep: dict) -> bool:
    """Put the bytes and the text in the bucket and point the entry at them.

    A run that dies on the twentieth file should not re-send nineteen files, so
    an object already stored at the same size is left alone. Returns True when
    something was actually written.
    """
    # Key, not id: mirror_bbc_audio.key_for() squashes the spaces in
    # "6 Minute English-2008-..." into dashes, because a space in an object
    # key becomes %20 in every URL the app builds and one of them will be
    # the one that does not get encoded.
    key = mirror.key_for(ep)
    size = mp3.stat().st_size
    wrote = False
    if stored_size(s3, bucket, key) != size:
        s3.put_object(
            Bucket=bucket, Key=key, Body=mp3.read_bytes(),
            ContentType="audio/mpeg",
            CacheControl="public, max-age=31536000, immutable",
            ACL="public-read")
        wrote = True
    ep["audio"] = f"{public}/{key}"

    text = ep.pop("_text", "")
    if len(text.split()) >= 40:
        tkey = key.replace(".mp3", ".txt")
        body = text.encode("utf-8")
        if stored_size(s3, bucket, tkey) != len(body):
            s3.put_object(
                Bucket=bucket, Key=tkey, Body=body,
                ContentType="text/plain; charset=utf-8",
                CacheControl="public, max-age=31536000, immutable",
                ACL="public-read")
            wrote = True
        ep["transcript_text"] = f"{public}/{tkey}"
        ep["transcript_words"] = len(text.split())
    return wrote


def merge(doc: dict, entries: list[dict]) -> tuple[int, int]:
    """Fold the entries into the catalogue, keeping one entry per id.

    New 2008 episodes go after the last episode of the same series rather than
    at the end of the file, so the section stays grouped by series instead of
    interleaving a decade of 6 Minute English with The English We Speak.
    """
    episodes = doc.setdefault("episodes", [])
    by_id = {e.get("id"): i for i, e in enumerate(episodes)}
    added = updated = 0
    for ep in entries:
        if ep["id"] in by_id:
            episodes[by_id[ep["id"]]] = ep
            updated += 1
    fresh = [e for e in entries if e["id"] not in by_id]
    if fresh:
        last = max((i for i, e in enumerate(episodes) if e.get("series") == SERIES),
                   default=len(episodes) - 1)
        episodes[last + 1:last + 1] = fresh
        added = len(fresh)
    doc["count"] = len(episodes)
    return added, updated


def verify(doc: dict) -> int:
    """Does every episode that claims a mirror actually resolve?"""
    import urllib.request
    bad = 0
    for ep in doc.get("episodes", []):
        for field in ("audio", "transcript_text"):
            url = ep.get(field) or ""
            if "arvanstorage" not in url:
                continue
            try:
                req = urllib.request.Request(url, method="HEAD")
                with urllib.request.urlopen(req, timeout=20) as r:
                    ok = r.status == 200
                    size = r.headers.get("Content-Length", "?")
            except Exception as exc:                   # noqa: BLE001
                ok, size = False, type(exc).__name__
            if not ok:
                bad += 1
                print(f"  ! {ep['id']} {field}: {size}")
    total = len(doc.get("episodes", []))
    print(f"{total - bad}/{total} mirrored objects resolve" if bad
          else f"all {total} episodes resolve in the bucket")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, type=Path,
                    help="folder holding the mp3/PDF pairs")
    ap.add_argument("--dry-run", action="store_true",
                    help="read and grade the folder, change nothing, upload nothing")
    ap.add_argument("--limit", type=int, default=0, help="how many pairs to take")
    ap.add_argument("--no-upload", action="store_true",
                    help="write the catalogue without touching the bucket")
    ap.add_argument("--verify", action="store_true",
                    help="check every mirrored URL in the catalogue")
    ap.add_argument("--delay", type=float, default=0.4,
                    help="seconds between uploads")
    args = ap.parse_args()

    doc = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    if args.verify:
        return verify(doc)

    folder = args.dir.expanduser()
    if not folder.is_dir():
        sys.exit(f"not a folder: {folder}")

    entries = build(folder, load_cefr(), args.limit)
    if not entries:
        sys.exit(f"no '*.mp3' / '*.pdf' pairs found in {folder}")

    print(f"{len(entries)} episodes in {folder.name}")
    for ep in entries[:3]:
        print(f"  {ep['id']:<52} {ep['level']}  {ep['duration']:>5}  "
              f"{ep['transcript_words']:>4} words")
    if len(entries) > 3:
        print(f"  ... and {len(entries) - 3} more")
    if args.dry_run:
        return 0

    if not args.no_upload:
        s3, bucket, public = mirror.connect()
        print(f"uploading to {bucket}/bbc/")
        for n, ep in enumerate(entries, 1):
            mp3 = folder / ep["source_file"]
            try:
                wrote = upload(s3, bucket, public, mp3, ep)
            except Exception as exc:                   # noqa: BLE001
                print(f"  ! {ep['id']}: {type(exc).__name__} {exc}", file=sys.stderr)
                continue
            print(f"  [{n}/{len(entries)}] {ep['id']}"
                  f"{' (stored)' if not wrote else ''}", flush=True)
            if wrote:
                time.sleep(args.delay)

    added, updated = merge(doc, entries)
    CATALOGUE.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                         encoding="utf-8")
    print(f"catalogue: {added} added, {updated} updated, "
          f"{len(doc['episodes'])} episodes total")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
