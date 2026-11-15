#!/usr/bin/env python3
"""Fetch one picture for every page of every kids reading passage.

    python3 tools/fetch_reading_images.py            # everything missing
    python3 tools/fetch_reading_images.py park-2     # only these pages
    python3 tools/fetch_reading_images.py --all      # refetch what exists

The reading section is the one place a child sits still for a minute, so each
turn of its page carries a photograph of what that page says: the blue bag, the
lunch box, the swing, the volcano. The pictures are keyed by passage and page
number - "park-3.jpg" is page three of "The park near my home" - which is also
the name the page asks the server for, so a passage gains a page by adding a row
here and one line of text to kids.json.

Everything else is the word fetcher's machinery: Openverse, CC0 and public
domain only, a stock photo preferred over an archive scan, a 480x360 crop
written as a small progressive JPEG. Keep this file next to that one: two
fetchers, one set of rules.
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "kids" / "reading"
CREDITS = OUT / "credits.json"


def _word_tool():
    """The word fetcher, loaded for its index helpers - not for its table."""
    path = ROOT / "tools" / "fetch_kids_word_images.py"
    spec = importlib.util.spec_from_file_location("fetch_kids_word_images", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PICS = _word_tool()

# passage id -> pages in reading order. Each page is (file stem, keyword,
# query): the keyword is what the picture is *of*, the query is how the index
# is asked for it. The stem is the file name without .jpg.
PAGES: dict[str, list[tuple[str, str, str]]] = {
    "school-bag": [
        ("school-bag-1", "backpack", "blue school backpack"),
        ("school-bag-2", "pencils", "school supplies pencils"),
        ("school-bag-3", "sandwich", "sandwich lunch"),
        ("school-bag-4", "backpack", "backpack on a table"),
    ],
    "rainy-day": [
        ("rainy-day-1", "rain", "rain drops on window"),
        ("rainy-day-2", "drawing", "child drawing with colored pencils"),
        ("rainy-day-3", "garden", "garden plants green"),
        ("rainy-day-4", "puddle", "puddle"),
    ],
    "park": [
        ("park-1", "playground", "playground swings slide park"),
        ("park-2", "swing", "child on swing"),
        ("park-3", "bench", "bench"),
        ("park-4", "cat", "cat grass"),
    ],
    "library-card": [
        ("library-card-1", "library", "library shelves books"),
        ("library-card-2", "reading", "child reading book by window"),
        ("library-card-3", "volcano", "volcano lava eruption"),
        ("library-card-4", "books", "books on shelf"),
        ("library-card-5", "reading", "children reading a book together"),
    ],
}

# Pages the index answered badly, pinned to a known picture the way the word
# table pins its own. (query that surfaces it, index id prefix, what it is)
CHOSEN: dict[str, tuple[str, str, str]] = {}


def chosen_item(stem: str) -> dict | None:
    if stem not in CHOSEN:
        return None
    query, prefix, _ = CHOSEN[stem]
    for item in PICS.api(query, "stocksnap,rawpixel"):
        if str(item.get("id") or "").startswith(prefix):
            return item
    return None


def pick(key: str, query: str) -> dict | None:
    """The best candidate, asked for across the sources in priority order."""
    best, best_score = None, -99
    for source, bonus in PICS.SOURCES:
        for item in PICS.api(query, source):
            s = PICS.score(item, key, query) + bonus
            if s > best_score:
                best, best_score = item, s
        if best_score >= 12:
            break
        time.sleep(0.8)
    return best


def load_credits() -> dict:
    if CREDITS.exists():
        try:
            return json.loads(CREDITS.read_text(encoding="utf-8"))
        except ValueError:
            return {}
    return {}


def main(argv: list[str]) -> int:
    every = "--all" in argv
    only = [a for a in argv if not a.startswith("-")]
    OUT.mkdir(parents=True, exist_ok=True)
    credits = load_credits()

    wanted = [(stem, key, query) for pages in PAGES.values() for stem, key, query in pages]
    if only:
        wanted = [row for row in wanted if row[0] in only]
    todo = [row for row in wanted if every or only or not (OUT / (row[0] + ".jpg")).exists()]
    print(f"{len(wanted)} pages in scope, {len(todo)} to fetch")

    done = 0
    for i, (stem, key, query) in enumerate(todo, 1):
        try:
            item = chosen_item(stem) or pick(key, query)
            if not item:
                print(f"  {i:3d}/{len(todo)}  {stem:14s} no result for {query!r}")
                continue
            raw = PICS.download(item.get("thumbnail") or item.get("url"))
            data = PICS.crop(raw)
            (OUT / (stem + ".jpg")).write_bytes(data)
            credits[stem] = {
                "q": query,
                "title": item.get("title") or "",
                "creator": item.get("creator") or "",
                "license": item.get("license") or "",
                "license_version": item.get("license_version") or "",
                "source": item.get("source") or "",
                "page": item.get("foreign_landing_url") or "",
                "file": "kids/reading/" + stem + ".jpg",
            }
            withdrawn = (item.get("license") or "").lower()
            print(f"  {i:3d}/{len(todo)}  {stem:14s} {len(data) // 1024:3d} KB  "
                  f"{withdrawn.upper()}  {item.get('source')}")
            done += 1
        except Exception as exc:                     # a dead thumbnail is not a crash
            print(f"  {i:3d}/{len(todo)}  {stem:14s} failed: {exc}")
        time.sleep(1.0)

    CREDITS.write_text(json.dumps(credits, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                       encoding="utf-8")
    print(f"\n{done} fetched, {len(credits)} credited in kids/reading/credits.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
