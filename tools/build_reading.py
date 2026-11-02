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
from reading_src import EVIDENCE, EXTRAS, ORDER, STRATEGIES  # noqa: E402

OUT = ROOT / "reading.json"
KINDS = ("blanks", "mcq", "truefalse", "essay")
MIN_WORDS, MAX_WORDS = 110, 280
# A B1 reader moves at roughly 150-180 words a minute; the panel shows the
# figure the learner can plan with, not a stopwatch.
WPM = 170


def words(text: str) -> int:
    return len(re.findall(r"[A-Za-z'’-]+", text))


QUOTED = re.compile(r"'([^']{10,})'|\u2018([^\u2019]{10,})\u2019")


def locate(item: dict, reading: dict) -> int | None:
    """Which paragraph proves this answer? One match, or no answer at all."""
    paras = [" ".join(p.split()) for p in reading["paragraphs"]]

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


def fail(msg: str) -> None:
    sys.exit("build_reading: " + msg)


# A 24-question set takes this cycle exactly six times, so a full set places
# the key on A, B, C and D equally often.
KEYS = (1, 2, 0, 3)


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
            if not s.get(key) or not s[key]["en"].strip() or not s[key]["fa"].strip():
                fail(f"{sid}: {key} needs both an English and a Persian line")
        if len(s["steps"]) < 3:
            fail(f"{sid}: a strategy without steps explains nothing")
        for step in s["steps"]:
            if not step["en"].strip() or not step["fa"].strip():
                fail(f"{sid}: a step is missing one of its two languages")

        ex = s.get("example") or {}
        if len((ex.get("text") or "").split()) < 25:
            fail(f"{sid}: the worked example is too short to demonstrate anything")
        if len(ex.get("steps") or []) < 2:
            fail(f"{sid}: the worked example is shown but never analysed")
        for line in ex["steps"]:
            if not line["en"].strip() or not line["fa"].strip():
                fail(f"{sid}: a worked-example line is missing a language")
        for field, least in (("mistakes", 2), ("tips", 2), ("checklist", 3)):
            rows = s.get(field) or []
            if len(rows) < least:
                fail(f"{sid}: {field} needs at least {least} entries")
            for row in rows:
                if not row["en"].strip() or not row["fa"].strip():
                    fail(f"{sid}: a {field} entry is missing a language")
        if not isinstance(s.get("minutes"), int) or s["minutes"] < 3:
            fail(f"{sid}: the lesson has no estimated learning time")

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
            for alt in item.get("also") or []:
                if not alt.strip():
                    fail(f"{sid}: an accepted alternative is empty")
            item.setdefault("also", [])

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

        # Evidence: an objective question says which paragraph answers it, so
        # feedback can point at the paragraph instead of only saying "wrong".
        paragraphs = len(r["paragraphs"])
        for kind in ("blanks", "mcq", "truefalse"):
            for qi, item in enumerate(q[kind]):
                para = item.get("para")
                if para is None:
                    para = EVIDENCE.get(sid, {}).get(kind, {}).get(qi)
                if para is None:
                    # The first six strategies were written without evidence
                    # numbers. Their explanations already quote the text, so
                    # the paragraph is taken from the quote - and only when
                    # exactly one paragraph contains it, because a guess here
                    # would point a learner at the wrong place.
                    para = locate(item, r)
                item["para"] = para
                if para is not None and not 1 <= para <= paragraphs:
                    fail(f"{sid}: {kind} question points at paragraph {para}, "
                         f"but the passage has {paragraphs}")

        for item in q["essay"]:
            if not item["model"]["en"].strip() or not item["prompt"]["fa"].strip():
                fail(f"{sid}: an essay question is missing its prompt or model answer")
            item.setdefault("min_words", 50)

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
            "reading": {
                "title": r["title"],
                "level": r.get("level", s["level"]),
                "genre": r.get("genre", {"en": "", "fa": ""}),
                "words": n,
                "minutes": max(1, round(n / WPM)),
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
    # The order a learner should meet them in, not the order they were written
    # in: survey before skim, skim before scan, and summarising last because it
    # is the only strategy that needs the other nine.
    rank = {sid: i for i, sid in enumerate(ORDER)}
    out.sort(key=lambda s: rank.get(s["id"], len(ORDER)))

    words_total = sum(s["reading"]["words"] for s in out)
    return {
        "version": 2,
        "intro": {
            "en": f"{len(out)} reading strategies. Each one is a lesson, then a "
                  "passage written to be read that way, then questions.",
            "fa": f"{len(out)} راهبرد خواندن. هر کدام یک درس است، بعد متنی که "
                  "برای همان راهبرد نوشته شده، بعد سؤال‌ها.",
        },
        "totals": {
            "strategies": len(out),
            "words": words_total,
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
          f"{n} questions, {OUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
