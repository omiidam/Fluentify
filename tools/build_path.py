#!/usr/bin/env python3
"""Write the A2 and B1 courses into path.json.

path.json is the single source of the learning path: a list of the seven level
spaces and a `courses` map keyed by level id. A1 was written by hand; A2 and B1
are built from `course_a2.py` and `course_b1.py` so their twenty-four lessons
each stay readable as content. A1 is never touched — it is read, kept, and
written back unchanged.

Run: python3 tools/build_path.py
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from course_a2 import COURSE as A2  # noqa: E402
from course_b1 import COURSE as B1  # noqa: E402


def main() -> int:
    path = os.path.join(ROOT, "path.json")
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)

    courses = doc.setdefault("courses", {})
    before = json.dumps(courses.get("A1"), sort_keys=True)

    courses["A2"] = A2
    courses["B1"] = B1

    for level in doc.get("levels", []):
        if level.get("id") in ("A2", "B1"):
            level["course"] = level["id"]

    after = json.dumps(courses["A1"], sort_keys=True)
    if before != after:
        print("A1 changed — refusing to write", file=sys.stderr)
        return 1

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")

    for key in ("A1", "A2", "B1"):
        course = courses[key]
        lessons = sum(len(u["lessons"]) for u in course["units"])
        exercises = sum(len(l["exercises"]) for u in course["units"] for l in u["lessons"])
        print(f"{key}: {len(course['units'])} units, {lessons} lessons, {exercises} exercises")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
