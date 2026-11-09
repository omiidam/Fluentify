#!/usr/bin/env python3
"""Add the A1 expansion to path.json.

A1 is the one course written by hand in path.json. Its fourteen new lessons —
one in each of the six units, and two new units of four — live in
`course_a1_extra.py`, and this script merges them without touching anything
else in the file. Running it twice changes nothing.

Run: python3 tools/extend_a1.py
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from course_a1_extra import EXTRA, U7, U8  # noqa: E402


def main() -> int:
    path = os.path.join(ROOT, "path.json")
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)

    course = doc.get("courses", {}).get("A1")
    if not course:
        print("there is no A1 course to extend", file=sys.stderr)
        return 1

    added = 0
    units = course.setdefault("units", [])
    by_id = {u["id"]: u for u in units}

    for uid, rows in EXTRA.items():
        unit = by_id.get(uid)
        if unit is None:
            print(f"no A1 unit {uid}", file=sys.stderr)
            return 1
        for row in rows:
            for i, old in enumerate(unit["lessons"]):
                if old["id"] == row["id"]:
                    if old != row:
                        unit["lessons"][i] = row
                        added += 1
                    break
            else:
                unit["lessons"].append(row)
                added += 1

    for fresh in (U7, U8):
        for i, old in enumerate(units):
            if old["id"] == fresh["id"]:
                if old != fresh:
                    units[i] = fresh
                    added += 1
                break
        else:
            units.append(fresh)
            added += 1

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")

    lessons = sum(len(u["lessons"]) for u in units)
    print(f"A1: {len(units)} units, {lessons} lessons ({added} change(s) this run)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
