#!/usr/bin/env python3
"""Grades Fluentify's vocabulary and phrase banks against CEFR.

Level data: Maximax67/Words-CEFR-Dataset (MIT), built on the CEFR-J profile —
a word's level is the lowest band it appears in, which is exactly how the CEFR
treats a word: known from the point it is introduced.

    python3 tools/cefr_grade.py --check    # report only
    python3 tools/cefr_grade.py --write    # stamp "level" into the JSON files

Compound nouns ("watermelon", "bank account") are graded from their parts,
because CEFR-J profiles them well above where a learner meets them.
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAP = Path("/tmp/opencode/cefr_map.json")
BANDS = {1: "A1", 2: "A2", 3: "B1", 4: "B2", 5: "C1", 6: "C2"}

# Words CEFR-J never grades, plus multi-word entries: fall back to the head
# noun, which is where a learner actually meets the item.
STOP = {"etc", "us", "uk", "usa"}


def load_map():
    if not MAP.exists():
        sys.exit(f"missing {MAP} — download the CEFR word/word_pos CSVs first")
    return json.loads(MAP.read_text(encoding="utf-8"))


def word_level(text: str, table: dict) -> int | None:
    """Lowest CEFR band for a word or phrase, or None if unknown."""
    w = text.lower().strip()
    if w in table:
        return table[w]
    parts = [p for p in re.split(r"[\s-]+", w) if p]
    parts = [p for p in parts if p not in STOP and len(p) > 1]
    if not parts:
        return None
    known = [table[p] for p in parts if p in table]
    return min(known) if known else None


def percentile(values: list[int], p: float) -> float:
    values = sorted(values)
    if not values:
        return 0.0
    k = (len(values) - 1) * p
    lo = int(k)
    hi = min(lo + 1, len(values) - 1)
    return values[lo] + (values[hi] - values[lo]) * (k - lo)


def grade_item(items: list[str], table: dict) -> tuple[str, int, int]:
    """(band, known, unknown) for a list of English strings."""
    levels = []
    unknown = 0
    for it in items:
        lv = word_level(it, table)
        if lv is None:
            unknown += 1
        else:
            levels.append(lv)
    if not levels:
        return "A1", 0, unknown
    # The mode is the honest signal for a topical bank: one hard word in a list
    # of easy ones does not make the list hard. p40 breaks ties.
    mode = Counter(levels).most_common(1)[0][0]
    return BANDS[int(round(percentile(levels, 0.40)))] if levels.count(mode) < 2 \
        else BANDS[mode], len(levels), unknown


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="stamp level into the JSON")
    args = ap.parse_args()

    table = load_map()["level"]
    glossary_p = ROOT / "glossary.json"
    phrases_p = ROOT / "phrases.json"

    g = json.loads(glossary_p.read_text(encoding="utf-8"))["domains"]
    p = json.loads(phrases_p.read_text(encoding="utf-8"))["topics"]

    print(f"{'':4} {'vocabulary domain':24} {'words':>5}  {'known':>5}")
    g_rows = []
    for key, dom in g.items():
        if key == "_groups":
            continue
        band, known, unk = grade_item([w[0] for w in dom["words"]], table)
        # a hand-assigned level always wins — the grader only fills gaps
        final = dom.get("level") or band
        g_rows.append((key, final, known, unk))
        src = "" if dom.get("level") else "  (auto)"
        print(f"{final:4} {key:24} {len(dom['words']):5}  {known:5}{src}")

    print()
    print(f"{'':4} {'phrase topic':24} {'lines':>5}  {'known':>5}")
    p_rows = []
    for key, topic in p.items():
        band, known, unk = grade_item([line["en"] for line in topic["phrases"]], table)
        final = topic.get("level") or band
        p_rows.append((key, final, known, unk))
        src = "" if topic.get("level") else "  (auto)"
        print(f"{final:4} {key:24} {len(topic['phrases']):5}  {known:5}{src}")

    if args.write:
        for key, band, _, _ in g_rows:
            g[key]["level"] = band
        for key, band, _, _ in p_rows:
            p[key]["level"] = band
        glossary_p.write_text(
            json.dumps({"domains": g}, ensure_ascii=False, indent=2), encoding="utf-8")
        phrases_p.write_text(
            json.dumps({"topics": p}, ensure_ascii=False, indent=2), encoding="utf-8")
        print("\nstamped levels into glossary.json and phrases.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())