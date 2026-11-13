#!/usr/bin/env python3
"""What the kids curriculum actually holds, section by section and level by level.

    python3 tools/audit_kids_content.py [--json]

This is the content inventory the curriculum is planned from: how many items
each section has, which CEFR levels they claim, and every hole a child would
fall into - a missing Persian line, a missing answer key, an answer that is not
one of its options. It reads the shipped file, so it cannot drift from it.
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KIDS = ROOT / "kids.json"
LEVELS = ["Pre-A1", "A1", "A2", "B1", "B2", "C1", "C2"]


def drawn_words():
    """Every word the kids art map actually draws, read from the shipped page."""
    page = (ROOT / "webapp.py").read_text(encoding="utf-8")
    start = page.find("const KID_ART = {")
    end = page.find("const KID_GENERIC", start)
    if start < 0 or end < 0:
        return set()
    return set(re.findall(r"^    '([a-z]+)':", page[start:end], re.M))


def items(doc):
    """Every teachable item, with the level it claims and its own checkers."""
    out = []
    art = drawn_words()
    for theme in doc.get("words") or []:
        for w in theme.get("words") or []:
            word = str(w.get("word") or "").lower()
            out.append(("vocabulary", w.get("level") or theme.get("cefr") or "A1",
                        w.get("word"),
                        [("Persian", bool(w.get("fa"))),
                         ("definition", bool(w.get("def_en"))),
                         ("example", bool(w.get("example_en"))),
                         ("example in Persian", bool(w.get("example_fa"))),
                         ("IPA", bool(w.get("ipa"))),
                         ("part of speech", bool(w.get("pos"))),
                         ("drawing", word in art)]))

    for sec, key, label in (("grammar", "quiz", "lesson"),
                            ("reading", "questions", "passage"),
                            ("listening", "questions", "clip"),
                            ("stories", "questions", "story")):
        for entry in doc.get(sec) or []:
            qs = entry.get(key) or []
            checks = [("Persian title", bool(entry.get("title_fa"))),
                      ("at least one question", len(qs) > 0)]
            out.append((sec, entry.get("cefr") or "A1", entry.get("id"), checks))
            for q in qs:
                opts = q.get("options") or []
                out.append((sec + " q", entry.get("cefr") or "A1",
                            entry.get("id") + ":" + str(q.get("q"))[:32],
                            [("answer key", q.get("answer") in opts),
                             ("explanation", bool(q.get("why_en"))),
                             ("explanation in Persian", bool(q.get("why_fa")))]))
    for sec in ("phrases",):
        for entry in doc.get(sec) or []:
            out.append((sec, entry.get("cefr") or "A1", entry.get("id"),
                        [("items", bool(entry.get("items"))),
                         ("Persian title", bool(entry.get("title_fa")))]))
    return out


def main(argv):
    doc = json.loads(KIDS.read_text(encoding="utf-8"))
    rows = items(doc)
    by_section = Counter()
    by_level = defaultdict(Counter)
    holes = []
    for section, level, ident, checks in rows:
        by_section[section] += 1
        by_level[level][section] += 1
        for what, ok in checks:
            if not ok:
                holes.append(f"{section} {ident}: missing {what}")

    if "--json" in argv:
        print(json.dumps({"sections": by_section, "levels": by_level,
                          "holes": holes}, ensure_ascii=False, indent=2))
        return 1 if holes else 0

    print("Content inventory\n")
    for section in sorted(by_section):
        print(f"  {section:14s} {by_section[section]:3d} items")
    print("\nLevel coverage\n")
    header = "  level   " + "".join(f"{s:>14s}" for s in sorted(by_section))
    print(header)
    for level in LEVELS:
        if level not in by_level:
            print(f"  {level:7s} " + "".join(f"{'-':>14s}" for _ in sorted(by_section))
                  + "   (nothing)")
            continue
        print(f"  {level:7s} " + "".join(
            f"{by_level[level].get(s, 0):>14d}" for s in sorted(by_section)))
    print("\nHoles\n")
    if not holes:
        print("  none: every item carries its translation, definition, example "
              "and a verified answer key")
        return 0
    for hole in holes:
        print("  - " + hole)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
