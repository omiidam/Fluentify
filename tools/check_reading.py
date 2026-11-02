#!/usr/bin/env python3
"""The Reading panel: is the content sound, and is the panel wired to it?

Three questions, in the order that makes a failure easy to read.

First, does reading.json match the source it is generated from? The passages
and their answer keys live in tools/reading_src.py; a stale JSON is a lesson
with yesterday's answers, which is worse than no lesson.

Second, is the content teachable? Every strategy must explain itself in both
languages, carry a passage long enough to practise on, and hold all four
question types. A multiple-choice key must point at one of its own options, a
blank's answer must actually occur in the passage it is asked about, and no
question may be answered correctly by picking the same letter every time -
a learner who notices that stops reading the passage.

Third, is the panel wired? Four separate anchors make it work - the tile, the
Panels.TILES entry, the on-open hook that loads the file, and the route that
serves it - and the APK needs its own copy of the JSON, because the phone has
no server.

    python3 tools/check_reading.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "reading.json"
PAGE = ROOT / "webapp.py"
BUILDER = ROOT / "tools/build_reading.py"
BUILD = ROOT / "build_apk_ui.py"
APK_DATA = ROOT / "android/app/src/main/assets/www/data/reading.json"

FA = re.compile(r"[\u0621-\u064A\u066E-\u06D3\u06FA-\u06FF]")
problems: list[str] = []


def check(ok: bool, what: str) -> bool:
    if not ok:
        problems.append(what)
    return ok


def load() -> dict:
    try:
        return json.loads(DOC.read_text(encoding="utf-8"))
    except FileNotFoundError:
        problems.append("reading.json is missing - run tools/build_reading.py")
    except json.JSONDecodeError as exc:
        problems.append(f"reading.json does not parse: {exc}")
    return {}


def check_fresh() -> None:
    proc = subprocess.run([sys.executable, str(BUILDER), "--check"],
                          cwd=ROOT, capture_output=True, text=True)
    check(proc.returncode == 0,
          "reading.json is out of date with tools/reading_src.py "
          "(run python3 tools/build_reading.py)")


def check_content(doc: dict) -> dict:
    strategies = doc.get("strategies")
    if not check(isinstance(strategies, list) and strategies,
                 "reading.json has no strategies"):
        return {"strategies": 0, "questions": 0, "words": 0}

    keys = Counter()
    ids = set()
    for s in strategies:
        sid = s.get("id")
        check(bool(sid) and sid not in ids, f"duplicate or missing strategy id {sid!r}")
        ids.add(sid)
        for field in ("title", "blurb", "what", "why"):
            part = s.get(field) or {}
            check(bool(FA.search(part.get("fa", ""))),
                  f"{sid}: {field} has no Persian line")
            check(bool(part.get("en", "").strip()),
                  f"{sid}: {field} has no English line")

        check(len(s.get("steps") or []) >= 3, f"{sid}: fewer than three steps")
        for step in s.get("steps") or []:
            check(bool(FA.search(step.get("fa", ""))),
                  f"{sid}: a step has no Persian")

        r = s.get("reading") or {}
        text = " ".join(r.get("paragraphs") or [])
        n = len(re.findall(r"[A-Za-z'’-]+", text))
        check(120 <= n <= 300, f"{sid}: the passage is {n} words")
        check(all(len(p) > 80 for p in r.get("paragraphs") or []),
              f"{sid}: a passage paragraph is a fragment")
        check(bool(r.get("title", {}).get("en")), f"{sid}: the passage has no title")
        check(bool(FA.search((r.get("summary") or {}).get("fa", ""))),
              f"{sid}: the passage has no Persian summary")
        check(r.get("words") == n, f"{sid}: the word count is stale ({r.get('words')} vs {n})")

        q = s.get("questions") or {}
        for kind in ("blanks", "mcq", "truefalse", "essay"):
            check(bool(q.get(kind)), f"{sid}: no {kind} questions")
        check(len(q.get("blanks") or []) >= 3, f"{sid}: fewer than three blanks")
        check(len(q.get("mcq") or []) >= 3, f"{sid}: fewer than three choice questions")
        check(len(q.get("truefalse") or []) >= 3, f"{sid}: fewer than three true/false")
        check(len(q.get("essay") or []) >= 1, f"{sid}: no writing task")

        for b in q.get("blanks") or []:
            check("___" in b.get("sentence", ""), f"{sid}: a blank has no gap")
            check(b.get("answer", "").lower() in text.lower(),
                  f"{sid}: the answer {b.get('answer')!r} never appears in the passage")
            keys[b.get("answer")] += 1

        for m in q.get("mcq") or []:
            opts = m.get("options") or []
            check(len(opts) == 4, f"{sid}: a choice question has {len(opts)} options")
            check(isinstance(m.get("answer"), int) and 0 <= m["answer"] < len(opts),
                  f"{sid}: a choice key points outside its options")
            check(bool(FA.search((m.get("why") or {}).get("fa", ""))),
                  f"{sid}: a choice explanation has no Persian")
            keys["mcq" + "ABCD"[m["answer"]]] += 1

        for t in q.get("truefalse") or []:
            check(isinstance(t.get("answer"), bool),
                  f"{sid}: a true/false key is not a boolean")
            keys["tf" + ("T" if t.get("answer") else "F")] += 1

        for e in q.get("essay") or []:
            model = e.get("model") or {}
            check(len(model.get("en", "").split()) >= 30,
                  f"{sid}: a model answer is too short to model anything")
            check(bool(FA.search(model.get("fa", ""))),
                  f"{sid}: a model answer has no Persian")
            check(bool(e.get("tips")), f"{sid}: a writing task has no tips")

    # A key that always sits on the same letter teaches pattern-spotting, not
    # reading. True/false is held to the same rule for the same reason.
    letters = {k[-1]: v for k, v in keys.items() if k.startswith("mcq")}
    if letters:
        top = max(letters.values())
        check(top / sum(letters.values()) <= 0.5,
              f"half the choice keys sit on one letter: {letters}")
    tf = {k[-1]: v for k, v in keys.items() if k.startswith("tf")}
    if tf:
        check(min(tf.values()) / sum(tf.values()) >= 0.3,
              f"true/false is lopsided: {tf}")

    return {
        "strategies": len(strategies),
        "questions": sum(sum((s.get("counts") or {}).values()) for s in strategies),
        "words": sum((s.get("reading") or {}).get("words", 0) for s in strategies),
    }


def check_panel() -> None:
    src = PAGE.read_text(encoding="utf-8")
    check('id="rdtoggle"' in src, "the Reading tile is not in the header")
    check('id="rdpanel"' in src, "the Reading panel is not in the markup")
    check(re.search(r"rdpanel:\s*'rdtoggle'", src) is not None,
          "Panels.TILES does not map the Reading panel to its tile")
    check(re.search(r"rdpanel:\s*\(\)\s*=>\s*Reading\.mount\(\)", src) is not None,
          "the Reading panel has no on-open hook, so it opens blank")
    check('startswith("/api/reading")' in src,
          "there is no /api/reading route for the page to read")
    check(re.search(r"reading:\s*\{[^}]*panel:\s*'rdpanel'", src, re.S) is not None,
          "typing 'reading' does not open the panel")
    check(re.search(r"#rdpanel\.open\s*\{[^}]*display:\s*block", src) is not None,
          "#rdpanel has no rule that shows it when open")


def check_offline() -> None:
    build = BUILD.read_text(encoding="utf-8")
    check('"reading.json"' in build,
          "the APK build does not bundle reading.json")
    if APK_DATA.exists():
        try:
            doc = json.loads(APK_DATA.read_text(encoding="utf-8"))
            check(bool(doc.get("strategies")),
                  "the APK's copy of reading.json has no strategies")
        except json.JSONDecodeError:
            problems.append("the APK's copy of reading.json does not parse")


def main() -> int:
    check_fresh()
    doc = load()
    stats = check_content(doc) if doc else {"strategies": 0, "questions": 0, "words": 0}
    check_panel()
    check_offline()

    if problems:
        for p in problems[:40]:
            print("FAIL  " + p)
        if len(problems) > 40:
            print(f"      ... and {len(problems) - 40} more")
        print(f"\nFAIL  {len(problems)} problem(s) with the reading strategies")
        return 1

    print(f"PASS  {stats['strategies']} strategies, {stats['questions']} questions "
          f"over {stats['words']} words of reading; every key is answerable from "
          f"its passage, and the panel, the route and the APK bundle are wired")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
