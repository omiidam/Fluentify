#!/usr/bin/env python3
"""Build reading.json from the strategy content in reading_src.py.

The Reading panel is only as good as its questions, and a question with the
wrong answer key teaches the wrong thing silently. This script refuses to write
the file if a question is unanswerable: every blank must appear in its passage,
every multiple-choice key must be one of its options, every strategy must carry
all four question types and three readings that practise it.

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
from reading_src import (  # noqa: E402
    EVIDENCE, EXTRAS, MORE, ORDER, STRATEGIES,
)

OUT = ROOT / "reading.json"
KINDS = ("blanks", "mcq", "truefalse", "essay")
READING_KEYS = ("title", "level", "genre", "paragraphs", "summary", "note")
MIN_WORDS, MAX_WORDS = 110, 290
# A B1 reader moves at roughly 150-180 words a minute; the panel shows the
# figure the learner can plan with, not a stopwatch.
WPM = 170
PRACTICES = 3


def words(text: str) -> int:
    return len(re.findall(r"[A-Za-z'’-]+", text))


def fail(msg: str) -> None:
    sys.exit("build_reading: " + msg)


QUOTED = re.compile(r"'([^']{10,})'|\u2018([^\u2019]{10,})\u2019")


def locate(item: dict, paragraphs: list[str]) -> int | None:
    """Which paragraph proves this answer? One match, or no answer at all."""
    paras = [" ".join(p.split()) for p in paragraphs]

    def where(fragment: str) -> int | None:
        frag = " ".join(fragment.split()).strip(" .,;:").lower()
        if len(frag) < 3:
            return None
        hits = [i for i, p in enumerate(paras, 1) if frag in p.lower()]
        return hits[0] if len(hits) == 1 else None

    if "sentence" in item:                       # a blank: the word itself
        found = where(item["answer"])
        if found:
            return found
    why = (item.get("why") or {}).get("en") or ""
    for match in QUOTED.finditer(why):
        found = where(match.group(1) or match.group(2) or "")
        if found:
            return found
    return None


# A 12-question practice takes this cycle exactly three times, so a full set
# places the key on A, B, C and D equally often.
KEYS = (1, 2, 0, 3)


def checked_text(value, where: str) -> str:
    if not isinstance(value, dict):
        fail(f"{where}: expected a {{'en': ..., 'fa': ...}} line")
    if not value.get("en", "").strip() or not value.get("fa", "").strip():
        fail(f"{where} needs both an English and a Persian line")
    return value["en"]


def build_questions(sid: str, practice: int, q: dict, paragraphs: list[str],
                    text: str, key_index: list) -> dict:
    """Validate one practice's questions and return them with their counts."""
    label = sid if practice == 1 else f"{sid} practice {practice}"
    for kind in KINDS:
        if not q.get(kind):
            fail(f"{label}: no {kind} questions")

    for item in q["blanks"]:
        if "___" not in item["sentence"]:
            fail(f"{label}: a fill-in question has no ___ gap")
        if item["answer"].lower() not in text.lower():
            fail(f"{label}: the blank answer {item['answer']!r} is not in the passage")
        checked_text(item["hint"], f"{label}: a blank hint")
        for alt in item.get("also") or []:
            if not alt.strip():
                fail(f"{label}: an accepted alternative is empty")
        item.setdefault("also", [])

    for item in q["mcq"]:
        if len(item["options"]) != 4:
            fail(f"{label}: a multiple-choice question has "
                 f"{len(item['options'])} options")
        if not 0 <= item["answer"] < len(item["options"]):
            fail(f"{label}: a multiple-choice answer key points outside its options")
        # Writers put the right answer second, because that is where it reads
        # best while you are writing. Shipped like that, most of the keys sit
        # on B and a learner can score without reading the passage. The correct
        # option is moved onto a balanced slot and the other three keep their
        # order; the answer itself never changes.
        want = KEYS[key_index[0] % len(KEYS)]
        key_index[0] += 1
        correct = item["options"][item["answer"]]
        rest = [o for k, o in enumerate(item["options"]) if k != item["answer"]]
        rest.insert(want, correct)
        if rest[want] != correct:
            fail(f"{label}: could not balance a key")
        item["options"] = rest
        item["answer"] = want
        for opt in item["options"]:
            if not opt.strip():
                fail(f"{label}: a multiple-choice option is empty")
        checked_text(item["why"], f"{label}: a multiple-choice explanation")

    for item in q["truefalse"]:
        if not isinstance(item["answer"], bool):
            fail(f"{label}: a true/false answer is not a boolean")
        checked_text(item["why"], f"{label}: a true/false explanation")

    # Evidence: an objective question says which paragraph answers it, so
    # feedback can point at the paragraph instead of only saying "wrong".
    paras = len(paragraphs)
    for kind in ("blanks", "mcq", "truefalse"):
        for qi, item in enumerate(q[kind]):
            para = item.get("para")
            if para is None and practice == 1:
                para = EVIDENCE.get(sid, {}).get(kind, {}).get(qi)
            if para is None:
                # Written before evidence numbers existed: the explanation
                # already quotes the text, so the paragraph is taken from the
                # quote - and only when exactly one paragraph contains it,
                # because a guess here would point a learner at the wrong
                # place.
                para = locate(item, paragraphs)
            item["para"] = para
            if para is not None and not 1 <= para <= paras:
                fail(f"{label}: {kind} question points at paragraph {para}, "
                     f"but the passage has {paras}")

    for item in q["essay"]:
        checked_text(item["prompt"], f"{label}: an essay prompt")
        checked_text(item["model"], f"{label}: an essay model answer")
        if not item.get("tips"):
            fail(f"{label}: an essay has no rubric points")
        item.setdefault("min_words", 50)

    return q


def build() -> dict:
    seen_ids = set()
    key_index = [0]
    out = []
    for base in STRATEGIES:
        sid = base["id"]
        # The six strategies written first carry only what the lesson needed at
        # the time. The rest of each lesson - when to use it, a worked example,
        # the mistakes, the tips, the checklist - lives in EXTRAS, so the whole
        # of one strategy can still be read in one file without the first six
        # being rewritten to make room.
        s = {**(EXTRAS.get(sid) or {}), **base}
        if sid in seen_ids:
            fail(f"two strategies share the id {sid!r}")
        seen_ids.add(sid)
        for key in ("title", "blurb", "what", "why", "when"):
            checked_text(s.get(key), f"{sid}: {key}")
        if len(s["steps"]) < 3:
            fail(f"{sid}: a strategy without steps explains nothing")
        for step in s["steps"]:
            checked_text(step, f"{sid}: a step")

        ex = s.get("example") or {}
        if len((ex.get("text") or "").split()) < 25:
            fail(f"{sid}: the worked example is too short to demonstrate anything")
        if len(ex.get("steps") or []) < 2:
            fail(f"{sid}: the worked example is shown but never analysed")
        for line in ex["steps"]:
            checked_text(line, f"{sid}: a worked-example line")
        for field, least in (("mistakes", 2), ("tips", 2), ("checklist", 3)):
            rows = s.get(field) or []
            if len(rows) < least:
                fail(f"{sid}: {field} needs at least {least} entries")
            for row in rows:
                checked_text(row, f"{sid}: a {field} entry")
        if not isinstance(s.get("minutes"), int) or s["minutes"] < 3:
            fail(f"{sid}: the lesson has no estimated learning time")

        # One lesson, three practices. The first is the passage the strategy
        # was written with; MORE holds the two that follow it.
        blocks = [{"reading": s["reading"], "questions": s["questions"]}]
        for extra in MORE.get(sid) or []:
            blocks.append({"reading": {k: extra[k] for k in READING_KEYS
                                       if k in extra},
                           "questions": extra["questions"]})
        if len(blocks) != PRACTICES:
            fail(f"{sid}: {len(blocks)} readings; the section teaches with "
                 f"{PRACTICES}")

        readings = []
        for i, block in enumerate(blocks, 1):
            r = block["reading"]
            check = f"{sid} practice {i}"
            text = " ".join(r["paragraphs"])
            n = words(text)
            if not MIN_WORDS <= n <= MAX_WORDS:
                fail(f"{check}: the reading is {n} words, outside "
                     f"{MIN_WORDS}-{MAX_WORDS}")
            checked_text(r.get("title"), f"{check}: the reading title")
            checked_text(r.get("summary"), f"{check}: the reading summary")
            q = build_questions(sid, i, block["questions"], r["paragraphs"],
                                text, key_index)
            readings.append({
                "index": i,
                "title": r["title"],
                "level": r.get("level", s["level"]),
                "genre": r.get("genre", {"en": "", "fa": ""}),
                "words": n,
                "minutes": max(1, round(n / WPM)),
                "paragraphs": r["paragraphs"],
                "summary": r["summary"],
                "note": r.get("note", {"en": "", "fa": ""}),
                "questions": q,
                "counts": {
                    "blanks": len(q["blanks"]),
                    "mcq": len(q["mcq"]),
                    "truefalse": len(q["truefalse"]),
                    "essay": len(q["essay"]),
                },
            })

        counts = {k: sum(r["counts"][k] for r in readings) for k in KINDS}
        out.append({
            "id": sid,
            "icon": s.get("icon", "📖"),
            "level": s["level"],
            "title": s["title"],
            "blurb": s["blurb"],
            "what": s["what"],
            "why": s["why"],
            "when": s["when"],
            "steps": s["steps"],
            "example": s["example"],
            "mistakes": s["mistakes"],
            "tips": s["tips"],
            "checklist": s["checklist"],
            "minutes": s["minutes"],
            "readings": readings,
            "counts": counts,
        })
    # The order a learner should meet them in, not the order they were written
    # in: survey before skim, skim before scan, and summarising last because it
    # is the only strategy that needs the other nine.
    rank = {sid: i for i, sid in enumerate(ORDER)}
    out.sort(key=lambda s: rank.get(s["id"], len(ORDER)))

    return {
        "version": 3,
        "intro": {
            "en": f"{len(out)} reading strategies, and {PRACTICES} passages with "
                  "questions for each one. Learn the strategy, then practise it "
                  "on all three.",
            "fa": f"{len(out)} راهبرد خواندن، و برای هر کدام {PRACTICES} متن با "
                  "سؤال. اول راهبرد را یاد بگیر، بعد هر سه متن را تمرین کن.",
        },
        "totals": {
            "strategies": len(out),
            "practices": len(out) * PRACTICES,
            "readings_per_strategy": PRACTICES,
            "words": sum(r["words"] for s in out for r in s["readings"]),
            "questions": sum(sum(s["counts"].values()) for s in out),
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
          f"{doc['totals']['practices']} readings, {n} questions, "
          f"{OUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
