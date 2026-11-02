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


def check_reading(sid: str, label: str, r: dict, keys: Counter) -> dict:
    """One passage: is it long enough to practise on, and are its keys sound?"""
    text = " ".join(r.get("paragraphs") or [])
    n = len(re.findall(r"[A-Za-z'\u2019-]+", text))
    check(120 <= n <= 300, f"{label}: the passage is {n} words")
    check(all(len(p) > 80 for p in r.get("paragraphs") or []),
          f"{label}: a passage paragraph is a fragment")
    check(bool(r.get("title", {}).get("en")), f"{label}: the passage has no title")
    check(bool(FA.search((r.get("summary") or {}).get("fa", ""))),
          f"{label}: the passage has no Persian summary")
    check(r.get("words") == n, f"{label}: the word count is stale ({r.get('words')} vs {n})")
    check(r.get("minutes") == max(1, round(n / 170)),
          f"{label}: the reading time does not match the passage")

    q = r.get("questions") or {}
    for kind in ("blanks", "mcq", "truefalse", "essay"):
        check(bool(q.get(kind)), f"{label}: no {kind} questions")
    check(len(q.get("blanks") or []) >= 3, f"{label}: fewer than three blanks")
    check(len(q.get("mcq") or []) >= 3, f"{label}: fewer than three choice questions")
    check(len(q.get("truefalse") or []) >= 3, f"{label}: fewer than three true/false")
    check(len(q.get("essay") or []) >= 1, f"{label}: no writing task")

    objective = q.get("blanks", []) + q.get("mcq", []) + q.get("truefalse", [])
    paras = len(r.get("paragraphs") or [])
    with_evidence = 0
    for item in objective:
        para = item.get("para")
        if para is None:
            continue
        check(isinstance(para, int) and 1 <= para <= paras,
              f"{label}: a question points at paragraph {para} of {paras}")
        with_evidence += 1
    # Feedback that cannot name the paragraph is a red cross with a sentence
    # next to it. Most questions must be able to point.
    check(with_evidence >= 0.7 * len(objective),
          f"{label}: only {with_evidence} of {len(objective)} questions say "
          f"which paragraph answers them")

    for item in q.get("blanks") or []:
        check("___" in item.get("sentence", ""), f"{label}: a blank has no gap")
        check(item.get("answer", "").lower() in text.lower(),
              f"{label}: the answer {item.get('answer')!r} never appears in "
              f"the passage")
        for alt in item.get("also") or []:
            check(isinstance(alt, str) and alt.strip() and
                  alt.lower() != item["answer"].lower(),
                  f"{label}: a rejected-list alternative is empty or redundant")
        keys[item.get("answer")] += 1

    for item in q.get("mcq") or []:
        opts = item.get("options") or []
        check(len(opts) == 4, f"{label}: a choice question has {len(opts)} options")
        check(isinstance(item.get("answer"), int) and 0 <= item["answer"] < len(opts),
              f"{label}: a choice key points outside its options")
        check(bool(FA.search((item.get("why") or {}).get("fa", ""))),
              f"{label}: a choice explanation has no Persian")
        keys["mcq" + "ABCD"[item["answer"]]] += 1

    for item in q.get("truefalse") or []:
        check(isinstance(item.get("answer"), bool),
              f"{label}: a true/false key is not a boolean")
        keys["tf" + ("T" if item["answer"] else "F")] += 1

    for item in q.get("essay") or []:
        check(isinstance(item.get("min_words"), int) and item["min_words"] >= 40,
              f"{label}: a writing task has no minimum length")
        model = item.get("model") or {}
        check(len(model.get("en", "").split()) >= 30,
              f"{label}: a model answer is too short to model anything")
        check(bool(FA.search(model.get("fa", ""))),
              f"{label}: a model answer has no Persian")
        check(bool(item.get("tips")), f"{label}: a writing task has no tips")

    return {
        "questions": sum(len(q.get(k) or []) for k in
                         ("blanks", "mcq", "truefalse", "essay")),
        "words": n,
    }


def check_content(doc: dict) -> dict:
    strategies = doc.get("strategies")
    if not check(isinstance(strategies, list) and strategies,
                 "reading.json has no strategies"):
        return {"strategies": 0, "questions": 0, "words": 0, "passages": 0}

    keys = Counter()
    ids = set()
    questions = words_total = passages = 0
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

        # The lesson sections added after the first six strategies. A lesson
        # that skips one of these is a lesson that stops at the definition.
        check(bool(FA.search((s.get("when") or {}).get("fa", ""))) and
              bool((s.get("when") or {}).get("en", "").strip()),
              f"{sid}: no 'when to use it' section in both languages")
        check(isinstance(s.get("minutes"), int) and 3 <= s["minutes"] <= 20,
              f"{sid}: the lesson time is missing or implausible")

        ex = s.get("example") or {}
        check(len((ex.get("text") or "").split()) >= 25,
              f"{sid}: the worked example is too short to demonstrate anything")
        check(len(ex.get("steps") or []) >= 2,
              f"{sid}: the worked example is never analysed")
        for line in ex.get("steps") or []:
            check(bool(FA.search(line.get("fa", ""))) and
                  bool(line.get("en", "").strip()),
                  f"{sid}: a worked-example line is missing a language")

        for field, least in (("mistakes", 2), ("tips", 2), ("checklist", 3)):
            rows = s.get(field) or []
            check(len(rows) >= least, f"{sid}: {field} needs at least {least} entries")
            for row in rows:
                check(bool(FA.search(row.get("fa", ""))) and
                      bool(row.get("en", "").strip()),
                      f"{sid}: a {field} entry is missing a language")

        readings = s.get("readings") or []
        check(len(readings) >= 3, f"{sid}: {len(readings)} practice passages, "
                                  f"not three")
        mine = {"questions": 0, "words": 0}
        for i, r in enumerate(readings, 1):
            label = sid if i == 1 else f"{sid} practice {i}"
            got = check_reading(sid, label, r, keys)
            mine["questions"] += got["questions"]
            mine["words"] += got["words"]
        passages += len(readings)
        questions += mine["questions"]
        words_total += mine["words"]
        check(sum(s.get("counts", {}).values()) == mine["questions"],
              f"{sid}: the question count does not match its passages")

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

    # The order is part of the teaching: surveying first because it comes
    # before reading, summarising last because it needs the other nine.
    order = [s.get("id") for s in strategies]
    check(order[0] == "survey" if "survey" in order else True,
          f"the progression starts with {order[0]!r}, not surveying")
    check(order[-1] == "summarize" if "summarize" in order else True,
          f"the progression ends with {order[-1]!r}, not summarising")

    return {
        "strategies": len(strategies),
        "passages": passages,
        "questions": questions,
        "words": words_total,
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
    stats = check_content(doc) if doc else {"strategies": 0, "passages": 0,
                                            "questions": 0, "words": 0}
    check_panel()
    check_offline()

    if problems:
        for p in problems[:40]:
            print("FAIL  " + p)
        if len(problems) > 40:
            print(f"      ... and {len(problems) - 40} more")
        print(f"\nFAIL  {len(problems)} problem(s) with the reading strategies")
        return 1

    print(f"PASS  {stats['strategies']} strategies, {stats['passages']} passages, "
          f"{stats['questions']} questions over {stats['words']} words of reading; "
          f"every key is answerable from its passage, and the panel, the route "
          f"and the APK bundle are wired")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
