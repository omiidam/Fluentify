#!/usr/bin/env python3
"""Build reading.json from the strategy content in reading_src.py.

The Reading panel is only as good as its questions, and a question with the
wrong answer key teaches the wrong thing silently. This script refuses to write
the file if a question is unanswerable: every blank must appear in its passage,
every multiple-choice key must be one of its options, every strategy must carry
all four question types and a reading that uses it.

    python3 tools/build_reading.py           # write reading.json
    python3 tools/build_reading.py --check   # fail if reading.json is stale
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reading_src import STRATEGIES  # noqa: E402

OUT = ROOT / "reading.json"
KINDS = ("blanks", "mcq", "truefalse", "essay")
MIN_WORDS, MAX_WORDS = 110, 280


def words(text: str) -> int:
    return len(re.findall(r"[A-Za-z'’-]+", text))


def fail(msg: str) -> None:
    sys.exit("build_reading: " + msg)


# A 24-question set takes this cycle exactly six times, so a full set places
# the key on A, B, C and D equally often.
KEYS = (1, 2, 0, 3)


def build() -> dict:
    seen_ids = set()
    key_index = [0]
    out = []
    for s in STRATEGIES:
        sid = s["id"]
        if sid in seen_ids:
            fail(f"two strategies share the id {sid!r}")
        seen_ids.add(sid)
        for key in ("title", "blurb", "what", "why"):
            if not s.get(key) or not s[key]["en"].strip() or not s[key]["fa"].strip():
                fail(f"{sid}: {key} needs both an English and a Persian line")
        if len(s["steps"]) < 3:
            fail(f"{sid}: a strategy without steps explains nothing")
        for step in s["steps"]:
            if not step["en"].strip() or not step["fa"].strip():
                fail(f"{sid}: a step is missing one of its two languages")

        r = s["reading"]
        text = " ".join(r["paragraphs"])
        n = words(text)
        if not MIN_WORDS <= n <= MAX_WORDS:
            fail(f"{sid}: the reading is {n} words, outside {MIN_WORDS}-{MAX_WORDS}")
        if not r.get("title", {}).get("en"):
            fail(f"{sid}: the reading has no title")
        if not r["summary"]["en"].strip() or not r["summary"]["fa"].strip():
            fail(f"{sid}: the reading summary needs both languages")

        q = s["questions"]
        for kind in KINDS:
            if not q.get(kind):
                fail(f"{sid}: no {kind} questions")

        for item in q["blanks"]:
            if "___" not in item["sentence"]:
                fail(f"{sid}: a fill-in question has no ___ gap")
            if item["answer"].lower() not in text.lower():
                fail(f"{sid}: the blank answer {item['answer']!r} is not in the passage")
            if not item["hint"]["en"].strip() or not item["hint"]["fa"].strip():
                fail(f"{sid}: a blank hint is missing a language")

        for item in q["mcq"]:
            if len(item["options"]) != 4:
                fail(f"{sid}: a multiple-choice question has {len(item['options'])} options")
            if not 0 <= item["answer"] < len(item["options"]):
                fail(f"{sid}: a multiple-choice answer key points outside its options")
            # Writers put the right answer second, because that is where it
            # reads best while you are writing. Shipped like that, two thirds
            # of the keys sit on B and a learner can score without reading the
            # passage. The correct option is moved onto a balanced slot and the
            # other three keep their order; the answer itself never changes.
            want = KEYS[(key_index[0]) % len(KEYS)]
            key_index[0] += 1
            correct = item["options"][item["answer"]]
            rest = [o for k, o in enumerate(item["options"]) if k != item["answer"]]
            rest.insert(want, correct)
            if rest[want] != correct:
                fail(f"{sid}: could not balance a key")
            item["options"] = rest
            item["answer"] = want
            for opt in item["options"]:
                if not opt.strip():
                    fail(f"{sid}: a multiple-choice option is empty")
            if not item["why"]["en"].strip() or not item["why"]["fa"].strip():
                fail(f"{sid}: a multiple-choice explanation is missing a language")

        for item in q["truefalse"]:
            if not isinstance(item["answer"], bool):
                fail(f"{sid}: a true/false answer is not a boolean")
            if not item["why"]["en"].strip() or not item["why"]["fa"].strip():
                fail(f"{sid}: a true/false explanation is missing a language")

        for item in q["essay"]:
            if not item["model"]["en"].strip() or not item["prompt"]["fa"].strip():
                fail(f"{sid}: an essay question is missing its prompt or model answer")

        out.append({
            "id": sid,
            "icon": s.get("icon", "📖"),
            "level": s["level"],
            "title": s["title"],
            "blurb": s["blurb"],
            "what": s["what"],
            "why": s["why"],
            "steps": s["steps"],
            "reading": {
                "title": r["title"],
                "level": r.get("level", s["level"]),
                "words": n,
                "paragraphs": r["paragraphs"],
                "summary": r["summary"],
                "note": r.get("note", {"en": "", "fa": ""}),
            },
            "questions": q,
            "counts": {
                "blanks": len(q["blanks"]),
                "mcq": len(q["mcq"]),
                "truefalse": len(q["truefalse"]),
                "essay": len(q["essay"]),
            },
        })
    return {
        "version": 1,
        "intro": {
            "en": "Six reading strategies, each explained, then used on a real "
                  "passage with four kinds of questions.",
            "fa": "شش راهبرد خواندن؛ هر کدام توضیح داده شده و بعد روی یک متن واقعی "
                  "با چهار نوع سؤال تمرین می‌شود.",
        },
        "strategies": out,
    }


def main() -> None:
    doc = build()
    body = json.dumps(doc, ensure_ascii=False, indent=1) + "\n"
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != body:
            sys.exit("build_reading: reading.json is out of date - run "
                     "python3 tools/build_reading.py")
        print("reading.json matches its source")
        return
    OUT.write_text(body, encoding="utf-8")
    n = sum(sum(s["counts"].values()) for s in doc["strategies"])
    print(f"wrote reading.json: {len(doc['strategies'])} strategies, "
          f"{n} questions, {OUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
