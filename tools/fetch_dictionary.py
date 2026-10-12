#!/usr/bin/env python3
"""Fetches the CEFR-J English word list used to verify word forms.

Source: Maximax67/Words-CEFR-Dataset (MIT licence) — 170k+ English words, each
tagged with the CEFR band it first appears in. We only use it as a
"is this a real word?" oracle, never as content.

    python3 tools/fetch_dictionary.py     → tools/.cache/dictionary.json
"""

import csv
import json
import sys
import urllib.request
from pathlib import Path

CACHE = Path(__file__).resolve().parent / ".cache"
BASE = "https://raw.githubusercontent.com/Maximax67/Words-CEFR-Dataset/master/csv"
FILES = {"words.csv": "cefr_words.csv", "word_pos.csv": "cefr_wordpos.csv"}
OUT = CACHE / "dictionary.json"


def fetch(name: str, dest: Path) -> None:
    if dest.exists() and dest.stat().st_size > 1000:
        print(f"  have {dest.name}")
        return
    print(f"  fetching {name} …")
    with urllib.request.urlopen(f"{BASE}/{name}", timeout=300) as r:
        dest.write_bytes(r.read())


def main() -> int:
    CACHE.mkdir(parents=True, exist_ok=True)
    for remote, local in FILES.items():
        fetch(remote, CACHE / local)
    if OUT.exists() and OUT.stat().st_size > 1000:
        print(f"have {OUT.name} ({len(json.loads(OUT.read_text()) )} words)")
        return 0

    words = {}
    with (CACHE / "cefr_words.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            words[row["word_id"]] = row["word"].strip()

    best = {}
    with (CACHE / "cefr_wordpos.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            w, lvl = words.get(row["word_id"]), row["level"]
            if not w or not lvl:
                continue
            w, lv = w.lower(), int(float(lvl))
            if w not in best or lv < best[w]:
                best[w] = lv

    OUT.write_text(json.dumps(best, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {OUT} ({len(best)} words)")
    return 0


if __name__ == "__main__":
    sys.exit(main())