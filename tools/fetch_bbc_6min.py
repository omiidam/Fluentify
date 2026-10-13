#!/usr/bin/env python3
"""Build the graded catalogue of BBC Learning English listening episodes.

    python3 tools/fetch_bbc_6min.py                 # index + grade, write bbc_6min.json
    python3 tools/fetch_bbc_6min.py --fetch 40      # download transcripts (resumable)
    python3 tools/fetch_bbc_6min.py --fetch all     # the whole archive
    python3 tools/fetch_bbc_6min.py --audit         # grade vs BBC's own level tag
    python3 tools/fetch_bbc_6min.py --report        # level distribution

On the series name: BBC Learning English ran "5 Minute English" until 2014 and
relaunched it as "6 Minute English". Same archive, longer episodes, weekly.

On the audio: every clip, transcript and worksheet is BBC copyright. This tool
stores a *catalogue* - title, blurb, year, and the canonical BBC URLs - and
the app plays from those URLs. Nothing BBC publishes is copied into this
repository or into the APK. Per-episode pages and PDFs are cached under
tools/.cache/ (gitignored) purely so re-running is fast and offline.

Grading lives in listening_grade.py and is audited against BBC's own level tag
with --audit.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from listening_grade import (  # noqa: E402
    bbc_level_from_page, grade_text, in_band_range, load_cefr,
)

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "tools/.cache/bbc"
OUT = ROOT / "bbc_6min.json"

# Three series, chosen because between them they span A1 → C1. BBC runs each
# of them at a single level, which is why one series alone cannot give a
# graded spread: 6 Minute English is intermediate throughout.
SERIES = {
    "Real Easy English": (
        "https://feeds.bbci.co.uk/learningenglish/english/features/real-easy-english/rss",
        "A1-A2"),
    "6 Minute English": (
        "https://feeds.bbci.co.uk/learningenglish/english/features/6-minute-english/rss",
        "B1-B2"),
    "The English We Speak": (
        "https://feeds.bbci.co.uk/learningenglish/english/features/the-english-we-speak/rss",
        "B2-C1"),
}
FEED = "https://feeds.bbci.co.uk/learningenglish/english/features/6-minute-english/rss"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/120 Safari/537.36 Fluentify/1.0")
LEVELS = ["A2", "B1", "B2", "C1"]
MIN_SECONDS_BETWEEN = 0.35


# Every failure this fetcher has ever hit in the wild, in one place:
#   URLError           DNS failure, refused connection, HTTP 4xx/5xx
#   HTTPError          a subclass of URLError, but named separately in tracebacks
#   TimeoutError       an OSError since 3.10
#   ConnectionResetError / ConnectionError / socket.timeout
#   InvalidURL, OSError("URL can't contain control characters")  a ValueError
# The first three run-endering crashes in this file were all one of these
# slipping past a narrower except clause, so they are caught as one class.
NET_ERRORS = (OSError, ValueError)


def http_get(url: str, timeout: int = 40, attempts: int = 3) -> bytes:
    """Fetch a URL, retrying the transient failures.

    BBC resets the connection often enough that a single try loses episodes
    to no fault of the URL, so transient errors are retried with a backoff.
    A URL that is simply gone (404) is not retried - that is not going to
    change.
    """
    # BBC's older transcript links contain a literal space
    # ("180607_6_minute_english_talking_to machines.pdf"). urllib rejects
    # those outright, and the one episode that hit it took the whole run down.
    url = url.replace(" ", "%20")
    last: Exception | None = None
    for attempt in range(attempts):
        req = urllib.request.Request(url, headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/pdf,*/*;q=0.8",
            "Accept-Language": "en-GB,en;q=0.9",
        })
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as exc:
            if exc.code in (404, 410):
                raise
            last = exc
        except NET_ERRORS as exc:
            last = exc
        if attempt < attempts - 1:
            time.sleep(1.5 * (attempt + 1))
    assert last is not None
    raise last


def parse_feed(xml: str, series: str = "6 Minute English") -> list[dict]:
    items = re.findall(r"<item>(.*?)</item>", xml, re.S)
    out = []
    prefix = re.compile(rf"^BBC Learning English\s*-\s*{re.escape(series)}\s*/\s*")
    for raw in items:
        def tag(name: str) -> str:
            m = re.search(rf"<{name}[^>]*>(.*?)</{name}>", raw, re.S)
            if not m:
                return ""
            v = re.sub(r"^<!\[CDATA\[(.*?)\]\]>$", r"\1", m.group(1).strip(), flags=re.S)
            return " ".join(v.split())

        link = tag("link")
        if not link:
            continue
        title = prefix.sub("", tag("title"))
        ym = re.search(r"[_/](20\d\d)/", link)
        out.append({
            "id": link.rstrip("/").split("/")[-1],
            "title": title,
            "blurb": tag("description"),
            "url": link,
            "year": ym.group(1) if ym else "",
        })
    return out


def parse_episode_page(html: str) -> dict:
    """Pull the media URLs out of an episode page.

    Two page templates live in the archive. Recent pages link a downloads.bbc
    mp3 and name the PDFs "..._transcript.pdf". Older ones are a different
    template with no audio link at all - BBC retired that player - and their
    transcript PDF is named after the episode's topic instead, e.g.
    "201029_6min_english_walkman.pdf". So the fallback is any 6-minute PDF,
    and http:// counts as well as https:// for the older pages.
    """
    audio = transcript = worksheet = any_pdf = ""
    m = re.search(r'https?://downloads\.bbc\.co\.uk/[^"\']+?\.mp3', html)
    if m:
        audio = m.group(0)
    for href in re.findall(r'href="(https?://[^"]+\.pdf)"', html):
        low = href.lower()
        if "transcript" in low and not transcript:
            transcript = href
        elif "worksheet" in low and not worksheet:
            worksheet = href
        elif not any_pdf:
            any_pdf = href
    if not transcript:
        # older pages: the topic-named PDF is the transcript
        transcript = any_pdf
    dur = ""
    d = re.search(r'data-audio-duration="(\d+)"', html)
    if d:
        dur = str(int(int(d.group(1)) / 1000))
    return {
        "audio": audio, "transcript_url": transcript,
        "worksheet_url": worksheet, "duration": dur,
        "bbc_tag": bbc_level_from_page(html),
    }


# The podcast feed carries an audio enclosure and a duration for episodes the
# site no longer links. Both sides publish the same title, so that is the join.
PODCAST_FEEDS = {
    # Only 6 Minute English needs this. Real Easy English and The English We
    # Speak still link their audio from the episode page; 6 Minute English is
    # the series whose older pages lost their player.
    "6 Minute English": "https://podcasts.files.bbci.co.uk/p02pc9tn.rss",
}


def _title_key(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def podcast_audio() -> dict:
    """title key -> {audio, duration}, from the podcast feeds."""
    out: dict = {}
    for name, url in PODCAST_FEEDS.items():
        try:
            xml = http_get(url, timeout=60).decode("utf-8", "replace")
        except NET_ERRORS as exc:
            print(f"  ! podcast feed {name}: {exc}")
            continue
        hits = 0
        for item in re.findall(r"<item>(.*?)</item>", xml, re.S):
            tm = re.search(r"<title>(.*?)</title>", item, re.S)
            em = re.search(r'<enclosure[^>]+url="([^"]+)"', item)
            dm = re.search(r"<itunes:duration>(\d+)</itunes:duration>", item)
            if not (tm and em):
                continue
            title = re.sub(r"^BBC Learning English\s*-\s*", "", tm.group(1)).strip()
            out.setdefault(_title_key(title), {
                "audio": em.group(1),
                "duration": str(int(dm.group(1))) if dm else "",
            })
            hits += 1
        print(f"  podcast {name:<22} {hits} episodes")
    return out



def _pdf_strings(blob: bytes) -> list[str]:
    r"""Pull the text literals out of a PDF content stream, in one pass.

    A regex like r"\[((?:\\.|[^\[\]])*)\]\\s*TJ" looks equivalent and is
    not: when a stream has a '[' with no matching ']', the engine retries every
    split and the cost explodes. BBC's transcripts embed font programs of
    several megabytes, so this hung on real files rather than theoretical ones.

    So this walks the bytes instead. Inside a literal string a backslash escapes
    the next byte; outside one, "Tj" and "TJ" mark where the string we have
    been building is shown, which is what we want to keep.
    """
    out: list[str] = []
    buf: list[str] = []
    i, n = 0, len(blob)
    depth = 0
    in_array = False
    while i < n:
        c = blob[i]
        if depth:
            if c == 0x5C:          # backslash: the next byte is literal
                i += 1
                if i < n:
                    buf.append(chr(blob[i]))
            elif c == 0x28:         # '('
                depth += 1
                buf.append("(")
            elif c == 0x29:         # ')'
                depth -= 1
                if depth:
                    buf.append(")")
            else:
                buf.append(chr(c))
        elif c == 0x5B:             # "[" - a TJ array opens
            in_array = True
        elif c == 0x5D:             # "]" - the array closes
            in_array = False
        elif c == 0x28:             # opening a literal string
            depth = 1
            buf = []
        elif c == 0x54 and i + 1 < n and blob[i + 1] == 0x6A:   # "Tj"
            if buf:
                out.append("".join(buf))
            buf = []
            i += 1
        elif c == 0x54 and i + 1 < n and blob[i + 1] == 0x4A:   # "TJ"
            # The run ends here. Whether the pieces were glued or spaced
            # depends on whether they sat inside one TJ array.
            if buf:
                out.append("".join(buf) if in_array else " ".join(buf))
            buf = []
            i += 1
        i += 1
    return out


def pdf_to_text(data: bytes) -> str:  # noqa: D401
    """Read a BBC transcript PDF without a PDF library.

    The transcripts carry a single text layer; we only need the words, so
    pulling the literals out of the content streams is enough. Embedded font
    programs run to several megabytes and contain no text-showing operators, so
    they are skipped by size rather than scanned.
    """
    chunks: list[bytes] = []
    for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", data, re.S):
        blob = m.group(1)
        try:
            blob = zlib.decompress(blob)
        except zlib.error:
            pass
        if len(blob) <= 2_000_000:
            chunks.append(blob)
    text: list[str] = []
    for blob in chunks:
        text.extend(_pdf_strings(blob))
    raw = " ".join(text)
    return raw.replace("\\n", "\n").replace("\\r", "\n").replace("\\t", " ")


def fetch_episode(ep: dict, cefr: dict[str, int], keep_text: bool,
                  pod: dict | None = None) -> dict:
    """One episode: page -> asset URLs + transcript -> grade. Cached on disk.

    `pod` is the title -> {audio, duration} map from the podcast feeds, which
    is where audio comes from for the older episodes whose pages no longer
    link any. Without it those episodes are indexed but unplayable.
    """
    CACHE.mkdir(parents=True, exist_ok=True)
    meta_path = CACHE / f"{ep['id']}.json"
    meta = {}
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            meta = {}

    # Re-parse when the cached page yielded nothing useful: an older template
    # means no audio link, and the transcript is named after the topic. The
    # `page_parsed` marker is what stops this refetching on every single run -
    # without it, each of the ~250 old-template pages costs a round trip
    # forever, for ever the same answer.
    stale = (not meta.get("audio") and not meta.get("transcript_url")
             and not meta.get("page_parsed"))
    if not meta or stale:
        try:
            page = http_get(ep["url"]).decode("utf-8", "replace")
        except NET_ERRORS as exc:
            return {**ep, "error": f"page: {exc}"}
        meta.update(parse_episode_page(page))
        meta["page_parsed"] = True
        time.sleep(MIN_SECONDS_BETWEEN)

    # audio the site will not link, from BBC's own podcast feed
    if not meta.get("audio") and pod:
        hit = pod.get(_title_key(ep["title"]))
        if hit:
            meta["audio"] = hit["audio"]
            meta["audio_from"] = "podcast"
            if not meta.get("duration") and hit.get("duration"):
                meta["duration"] = hit["duration"]

    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2),
                         encoding="utf-8")

    transcript = ""
    if meta.get("transcript_url"):
        pdf_path = CACHE / f"{ep['id']}.pdf"
        if not pdf_path.exists():
            try:
                pdf_path.write_bytes(http_get(meta["transcript_url"]))
                time.sleep(MIN_SECONDS_BETWEEN)
            except NET_ERRORS as exc:
                meta["transcript_error"] = str(exc)
        if pdf_path.exists():
            transcript = pdf_to_text(pdf_path.read_bytes())

    duration = meta.get("duration") or ""
    wpm = None
    grade = grade_text(transcript or ep["blurb"], cefr, wpm=wpm)
    if not grade.get("level"):
        grade = grade_text(ep["blurb"], cefr, wpm=wpm)

    out = {
        **ep,
        "level": grade.get("level"),
        "duration": duration,
        "audio": meta.get("audio", ""),
        "transcript_url": meta.get("transcript_url", ""),
        "worksheet_url": meta.get("worksheet_url", ""),
        "bbc_tag": meta.get("bbc_tag"),
        "graded_from": "transcript" if transcript else "blurb",
        "stats": grade,
    }
    if keep_text and transcript:
        out["transcript"] = transcript
    return out


def audit(episodes: list[dict]) -> None:
    """Compare the grader with BBC's own level tag on the same episode.

    BBC's tags are course ranges ("intermediate" = B1-B2), so the honest test
    is containment, not equality. A grader that disagrees is only wrong if it
    lands outside the range the publisher themselves gave.
    """
    from collections import Counter

    tagged = [e for e in episodes if e.get("level") and e.get("bbc_tag")]
    if not tagged:
        print("  no episodes carry BBC's level tag — nothing to audit against")
        return
    inside = sum(1 for e in tagged if in_band_range(e["level"], e["bbc_tag"]))
    print(f"  audited {len(tagged)} tagged episodes")
    print(f"    inside BBC's own band  : {inside}/{len(tagged)} "
          f"({100 * inside // len(tagged)}%)")
    off = [e for e in tagged if not in_band_range(e["level"], e["bbc_tag"])]
    for e in off[:8]:
        print(f"      outside: {e['level']} vs BBC {e['bbc_tag']}"
              f"  {e['title'][:40]}")
    print("    (mine, theirs) ->", dict(Counter(
        (e["level"], e["bbc_tag"]) for e in tagged).most_common(8)))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fetch", default="0",
                    help="N episodes to download transcripts for, or 'all'")
    ap.add_argument("--no-transcripts", action="store_true",
                    help="keep the catalogue small: no transcript text")
    ap.add_argument("--audit", action="store_true", help="grade vs BBC's tag")
    ap.add_argument("--report", action="store_true", help="print and exit")
    args = ap.parse_args()

    cefr = load_cefr()
    print(f"CEFR table: {len(cefr)} words")

    print("reading the feeds …")
    seen, unique = set(), []
    for name, (url, expected) in SERIES.items():
        try:
            eps = parse_feed(http_get(url).decode("utf-8", "replace"), name)
        except (urllib.error.URLError, TimeoutError) as exc:
            print(f"  ! {name}: {exc}")
            continue
        fresh = 0
        for ep in eps:
            ep["series"] = name
            ep["series_expected"] = expected
            if ep["url"] in seen:
                continue
            seen.add(ep["url"])
            ep["id"] = f"{name}-{ep['id']}"
            unique.append(ep)
            fresh += 1
        print(f"  {name:<22} {fresh:>4} episodes  (BBC targets {expected})")
    print(f"  {len(unique)} unique in total")

    limit = len(unique)
    if args.fetch != "0":
        limit = len(unique) if args.fetch == "all" else int(args.fetch)

    print("reading the podcast feeds …")
    pod = podcast_audio()

    keep_text = not args.no_transcripts
    graded, failed = [], 0
    for i, ep in enumerate(unique[:limit], 1):
        row = fetch_episode(ep, cefr, keep_text, pod)
        if row.get("error"):
            failed += 1
            if failed <= 3:
                print(f"  ! {ep['id']}: {row['error']}")
            continue
        graded.append(row)
        if i % 25 == 0 or i == limit:
            print(f"  {i}/{limit} graded "
                  f"(have transcript: {sum(1 for g in graded if g['graded_from'] == 'transcript')})")

    if args.audit:
        audit(graded)

    from collections import Counter
    dist = Counter(e["level"] or "?" for e in graded)
    print("distribution:", dict(sorted(dist.items())))

    if args.report:
        for e in graded[:15]:
            s = e["stats"]
            print(f"  {e['level'] or '?':3} (BBC {e.get('bbc_tag') or '-':16}) "
                  f"{e['title'][:48]:50} {s.get('total_words', 0):>5}w")
        return 0

    graded.sort(key=lambda e: (LEVELS.index(e["level"]) if e.get("level") in LEVELS else 9,
                               e.get("year", ""), e["title"]))
    doc = {
        "_readme": (
            "BBC Learning English — 6 Minute English (called 5 Minute English "
            "until 2014). A catalogue only: the audio, transcripts and "
            "worksheets stay on BBC's servers and the app plays from these "
            "canonical URLs. No BBC media is stored in this repository or "
            "shipped in the APK. Rebuild with tools/fetch_bbc_6min.py --fetch N."
        ),
        "_grading": (
            "tools/listening_grade.py — CEFR-J word list "
            "(Maximax67/Words-CEFR-Dataset, MIT). A passage's band blends the "
            "75th percentile of its content-word levels, the share of B2+ "
            "vocabulary, sentence length and clause density, and speaking "
            "rate. Audited against BBC's own level tag with --audit."
        ),
        "levels": LEVELS,
        "episodes": graded,
        "distribution": dict(sorted(dist.items())),
        "count": len(graded),
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {OUT.name}: {len(graded)} episodes, {OUT.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())