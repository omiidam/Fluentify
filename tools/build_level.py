#!/usr/bin/env python3
"""Validate the level check and write level_test.json.

The gate has to be strict about the things that silently break a test: an
answer key outside its options, two identical options, a reading question
pointing at a passage that is not there, a band with no items, a rubric whose
scores do not run 1 to 4, a Persian line that is still English. It also has to
be strict about the two-thirds rule being *possible* in every band - a band of
three items where two correct is 66.7% passes, but a band of four needs three,
and a band of two would need 1.33 and could never be scored.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from level_test import LEVEL  # noqa: E402

# Option order is shuffled once, here, seeded by the item itself: the same
# build always ships the same bank, but the correct answer is not parked in
# the same slot across a section, which is the cue a learner stops reading the
# options for. The source keeps the author's order, where the distractors were
# written in a deliberate sequence.
import copy  # noqa: E402
import random  # noqa: E402

_bank = copy.deepcopy(LEVEL)
for _sec in _bank["sections"]:
    for _item in _sec["items"]:
        if "options" not in _item:
            continue
        _rng = random.Random(f'{_item["band"]}|{_item["stem"]["en"]}')
        _correct = _item["options"][_item["answer"]]
        _rng.shuffle(_item["options"])
        _item["answer"] = _item["options"].index(_correct)
LEVEL = _bank

OUT = ROOT / "level_test.json"
BANDS = [b["id"] for b in LEVEL["bands"]]
ORDER = {b: i for i, b in enumerate(BANDS)}
OBJECTIVE = {"use", "reading", "listening"}
PERSIAN = re.compile(r"[\u0600-\u06FF]")
EXPECTED = {"use": 15, "reading": 15, "listening": 15, "writing": 4, "speaking": 4}

problems: list[str] = []


def need(cond: bool, msg: str) -> None:
    if not cond:
        problems.append(msg)


def both_lang(value, where: str) -> None:
    need(isinstance(value, dict) and set(value) == {"en", "fa"},
         f"{where}: expected an en/fa pair")
    if not isinstance(value, dict):
        return
    need(len(str(value.get("en", "")).strip()) > 1, f"{where}: English text is empty")
    need(bool(PERSIAN.search(str(value.get("fa", "")))),
         f"{where}: Persian line has no Persian characters")


def main() -> int:
    sections = LEVEL["sections"]
    ids = [s["id"] for s in sections]
    need(ids == ["use", "reading", "listening", "writing", "speaking"],
         f"section order is {ids}")
    need(LEVEL["retakeDays"] == 30, "the retake window is not one month")
    both_lang(LEVEL["title"], "title")
    both_lang(LEVEL["blurb"], "blurb")
    both_lang(LEVEL["method"], "method")

    for band in LEVEL["bands"]:
        need(band["id"] in ORDER, f"unknown band {band['id']}")
        need(len(band["can"]["en"]) > 20, f"{band['id']}: no can-do sentence")
        both_lang(band["name"], f"{band['id']} name")
        both_lang(band["can"], f"{band['id']} can")

    total = 0
    keys: list[int] = []
    band_seen: Counter[str] = Counter()

    for sec in sections:
        sid = sec["id"]
        both_lang(sec["title"], f"{sid} title")
        both_lang(sec["instructions"], f"{sid} instructions")
        items = sec["items"]
        need(len(items) == EXPECTED[sid],
             f"{sid}: {len(items)} items, expected {EXPECTED[sid]}")
        total += len(items)

        if sid == "reading":
            passages = {p["id"]: p for p in sec["passages"]}
            need(len(passages) >= 3, f"reading: only {len(passages)} passages")
            for pid, p in passages.items():
                both_lang(p["title"], f"reading/{pid} title")
                both_lang(p["text"], f"reading/{pid} text")
                # An A1 text is short by design: three or four sentences is
                # the whole of A1 reading. Anything above it needs a real
                # passage, or the questions test guessing rather than reading.
                floor = 20 if p["band"] == "A1" else 60
                need(len(p["text"]["en"].split()) >= floor,
                     f"reading/{pid}: {len(p['text']['en'].split())} words, "
                     f"below the {floor} this band needs")
                need(p["band"] in ORDER, f"reading/{pid}: band {p['band']}")
                used = sum(1 for it in items if it.get("passage") == pid)
                need(used >= 3, f"reading/{pid}: only {used} questions")

        if sid == "listening":
            for i, it in enumerate(items):
                words = len(str(it.get("say", "")).split())
                need(words >= 6, f"listening[{i}]: spoken text is only {words} words")

        if sid in ("writing", "speaking"):
            for i, it in enumerate(items):
                both_lang(it["prompt"], f"{sid}[{i}] prompt")
                both_lang(it.get("hint", {}), f"{sid}[{i}] hint")
                rub = it.get("rubric") or []
                need([r["points"] for r in rub] == [1, 2, 3, 4],
                     f"{sid}[{i}]: rubric points are "
                     f"{[r.get('points') for r in rub]}")
                for r in rub:
                    both_lang(r["text"], f"{sid}[{i}] rubric {r.get('points')}")

        for i, it in enumerate(items):
            where = f"{sid}[{i}]"
            need(it["band"] in ORDER, f"{where}: band {it['band']}")
            band_seen[it["band"]] += 1
            both_lang(it["stem"] if "stem" in it else it["prompt"], f"{where} stem")
            if sid not in OBJECTIVE:
                continue
            opts = it.get("options") or []
            need(len(opts) == 4, f"{where}: {len(opts)} options")
            need(len(set(opts)) == len(opts), f"{where}: duplicate options")
            need(all(isinstance(o, str) and o.strip() for o in opts),
                 f"{where}: empty option")
            need(isinstance(it.get("answer"), int) and 0 <= it["answer"] < 4,
                 f"{where}: answer {it.get('answer')} is not an option")
            if isinstance(it.get("answer"), int) and 0 <= it["answer"] < 4:
                keys.append(it["answer"])
            both_lang(it["why"], f"{where} why")
            if sid == "reading":
                need(it.get("passage") in {p["id"] for p in sec["passages"]},
                     f"{where}: passage {it.get('passage')} is missing")
            if sid == "reading" and it.get("passage"):
                p = next(p for p in sec["passages"] if p["id"] == it["passage"])
                need(ORDER[it["band"]] >= ORDER[p["band"]],
                     f"{where}: {it['band']} question on a {p['band']} passage")

    need(total >= 40, f"only {total} questions in the whole test")
    need(sum(band_seen.values()) == total, "band counting drifted")

    # Every band from A1 to C1 must carry at least three scorable items, or the
    # two-thirds rule either cannot be met or can be met by one lucky guess.
    for band in BANDS:
        n = band_seen[band]
        need(n >= 3, f"band {band} has only {n} questions")
        if n:
            need(n * 2 // 3 >= 1 and n - (n * 2 + 2) // 3 >= 1,
                 f"band {band}: two thirds of {n} is not a whole number of items")

    need(len(set(keys)) >= 3, f"answer keys use only {len(set(keys))} letters")
    if keys:
        need(Counter(keys).most_common(1)[0][1] <= len(keys) * 0.6,
             "one answer letter dominates the multiple choice")

    if problems:
        for p in problems:
            print("FAIL  " + p)
        print(f"\n{len(problems)} problem(s); level_test.json not written")
        return 1

    payload = json.dumps(LEVEL, ensure_ascii=False, separators=(",", ":"))

    # --check lets tools/check_level.py prove the shipped file still matches
    # the source, without this script rewriting it as a side effect.
    if "--check" in sys.argv[1:]:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != payload:
            print("FAIL  level_test.json is out of date with tools/level_test.py")
            return 1
        print("PASS  level_test.json matches tools/level_test.py")
        return 0

    OUT.write_text(payload, encoding="utf-8")
    per_band = " ".join(f"{b}:{band_seen[b]}" for b in BANDS)
    print(f"wrote level_test.json: {total} questions, {len(keys)} scored, "
          f"{len(payload.encode())} bytes")
    print(f"bands  {per_band}")
    print("PASS  the level check holds together")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
