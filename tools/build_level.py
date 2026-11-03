#!/usr/bin/env python3
"""Validate the level assessment and write level_test.json.

The gate is about the things that quietly break an assessment: a band with
too few items to score, an answer key outside its options, a typed item with
no accepted answers, a reading question pointing at a passage that is not
there, an item missing the metadata the report depends on, a skill that is
silently counted as assessed when it has no scorable items.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from level_test import LEVEL  # noqa: E402

# Option order is shuffled once, here, seeded by the item id: the same build
# always ships the same bank, but the correct option is not parked in the same
# slot down a column, which is the cue a learner stops reading options for.
import copy  # noqa: E402
import random  # noqa: E402

_bank = copy.deepcopy(LEVEL)
for _item in _bank["items"]:
    if "options" not in _item:
        continue
    _rng = random.Random(_item["id"])
    _right = _item["options"][_item["answer"]]
    _rng.shuffle(_item["options"])
    _item["answer"] = _item["options"].index(_right)
LEVEL = _bank

OUT = ROOT / "level_test.json"
PERSIAN = re.compile(r"[\u0600-\u06FF]")
KINDS = {"mcq", "cloze", "error", "transform", "order", "shortwriting", "speaking"}
TYPED = {"cloze", "transform", "order"}
DIFFICULTY = {"easy", "medium", "hard"}
NEED_FIELDS = ("id", "skill", "band", "subskill", "kind", "difficulty", "ability",
               "prompt", "why", "weight", "source", "review")

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
    skills = LEVEL["skills"]
    ids = [s["id"] for s in skills]
    need(ids == ["grammar", "vocabulary", "reading", "listening", "writing", "speaking"],
         f"skill order is {ids}")
    assessed = [s["id"] for s in skills if s["assessed"]]
    need(assessed == ["grammar", "vocabulary", "reading", "listening"],
         f"assessed skills are {assessed}")
    for s in skills:
        both_lang(s["title"], f"skill {s['id']} title")
        both_lang(s["blurb"], f"skill {s['id']} blurb")

    bands = [b["id"] for b in LEVEL["bands"]]
    need(bands == ["PRE", "A1", "A2", "B1", "B2", "C1", "C2"],
         f"bands are {bands}")
    tested = LEVEL["testedBands"]
    need(tested == ["A1", "A2", "B1", "B2", "C1"],
         f"tested bands are {tested}")
    for b in LEVEL["bands"]:
        both_lang(b["name"], f"band {b['id']} name")
        both_lang(b["can"], f"band {b['id']} can-do")
        need(b["label"] == b["id"] or b["id"] == "PRE",
             f"band {b['id']} has label {b['label']}")

    bp = LEVEL["blueprint"]
    need(bp["bands"] == tested, "the blueprint tests a different set of bands")
    need(bp["assessed"] == assessed, "the blueprint and the skills disagree")
    need(list(bp["perBand"]) == assessed, "the blueprint does not count each skill")
    need(sum(bp["perBand"].values()) == bp["perBandTotal"],
         "the per-band counts do not add up to the band total")
    need(bp["perBandTotal"] * len(tested) == bp["questions"],
         "the paper is not one band total per band")
    cut = bp["cutoffs"]
    need(len(cut) == len(tested), "there is not one cutoff per band")
    need(all(0 < c < 1 for c in cut), "a cutoff is outside the paper")
    need(cut == sorted(cut) and len(set(cut)) == len(cut),
         "the cutoffs do not climb")

    items = LEVEL["items"]
    seen: set[str] = set()
    per_band_skill: Counter[tuple[str, str]] = Counter()
    kinds: Counter[str] = Counter()
    keys: list[int] = []

    for it in items:
        where = it.get("id") or "an item with no id"
        for field in NEED_FIELDS:
            need(field in it, f"{where}: missing {field}")
        need(it["id"] not in seen, f"{where}: duplicate id")
        seen.add(it["id"])
        need(it["skill"] in ids, f"{where}: unknown skill {it['skill']}")
        need(it["band"] in tested, f"{where}: band {it['band']} is not tested")
        need(it["kind"] in KINDS, f"{where}: unknown kind {it['kind']}")
        need(it["difficulty"] in DIFFICULTY, f"{where}: difficulty {it['difficulty']}")
        need(isinstance(it["weight"], (int, float)) and it["weight"] > 0,
             f"{where}: weight is not positive")
        need(it["review"] == "reviewed", f"{where}: not reviewed")
        need(bool(it["source"].strip()), f"{where}: no source")
        both_lang(it["subskill"], f"{where} subskill")
        both_lang(it["ability"], f"{where} ability")
        both_lang(it["prompt"], f"{where} prompt")
        both_lang(it["why"], f"{where} why")
        kinds[it["kind"]] += 1
        if it["kind"] in ("mcq", "error"):
            opts = it.get("options") or []
            need(len(opts) == 4, f"{where}: {len(opts)} options")
            need(len(set(opts)) == len(opts), f"{where}: duplicate options")
            need(isinstance(it.get("answer"), int) and 0 <= it["answer"] < 4,
                 f"{where}: answer is not one of the options")
            if isinstance(it.get("answer"), int) and 0 <= it["answer"] < 4:
                keys.append(it["answer"])
        if it["kind"] in TYPED:
            accept = it.get("accept") or []
            need(bool(accept), f"{where}: a typed item with nothing accepted")
            need(all(isinstance(a, str) and a.strip() for a in accept),
                 f"{where}: an empty accepted answer")
        if it["kind"] == "order":
            need(4 <= len(it["prompt"]["en"].split()) <= 6,
                 f"{where}: word-order prompt is not a sentence to reorder")
        if it["kind"] == "listening" or it.get("say"):
            need(len((it.get("say") or "").split()) >= 6,
                 f"{where}: spoken text is too short to test")
        if it["skill"] in ("grammar", "vocabulary", "reading", "listening"):
            per_band_skill[(it["skill"], it["band"])] += 1

    need(len(kinds) >= 5, f"only {len(kinds)} question formats")
    need(len(set(keys)) >= 3, f"answer keys use only {len(set(keys))} letters")
    if keys:
        top = Counter(keys).most_common(1)[0][1]
        need(top <= len(keys) * 0.55, "one answer letter dominates the bank")

    # The paper is fixed, so the bank must hold exactly the questions it
    # promises: ten per band, in the four assessed skills.
    total = 0
    for band in tested:
        in_band = 0
        for skill in assessed:
            n = per_band_skill[(skill, band)]
            want = bp["perBand"][skill]
            need(n == want, f"{skill}/{band}: {n} items, blueprint wants {want}")
            in_band += n
        need(in_band == bp["perBandTotal"],
             f"band {band}: {in_band} questions, blueprint wants {bp['perBandTotal']}")
        total += in_band
    need(total == bp["questions"], f"the bank holds {total} questions, not {bp['questions']}")

    passages = {p["id"]: p for p in LEVEL["passages"]}
    need(len(passages) >= 5, f"only {len(passages)} reading passages")
    for pid, p in passages.items():
        both_lang(p["title"], f"passage {pid} title")
        both_lang(p["text"], f"passage {pid} text")
        need(p["band"] in tested, f"passage {pid}: band {p['band']}")
        words = len(p["text"]["en"].split())
        floor = 20 if p["band"] == "A1" else 60
        need(words >= floor, f"passage {pid}: {words} words, below {floor}")
        asked = sum(1 for it in items if it.get("passage") == pid)
        need(asked == bp["perBand"]["reading"],
             f"passage {pid}: {asked} questions, expected {bp['perBand']['reading']}")

    for it in items:
        if it.get("passage"):
            need(it["passage"] in passages,
                 f"{it['id']}: points at missing passage {it['passage']}")
            need(it["skill"] == "reading", f"{it['id']}: passage on a non-reading item")

    for it in items:
        if it["skill"] in ("writing", "speaking"):
            need(it["kind"] in ("shortwriting", "speaking"),
                 f"{it['id']}: a productive skill with a recognition format")
    need(len([i for i in items if i["skill"] == "writing"]) >= 2,
         "fewer than two writing tasks")
    need(len([i for i in items if i["skill"] == "speaking"]) >= 2,
         "fewer than two speaking tasks")

    rubric = LEVEL["rubric"]
    need([r["points"] for r in rubric] == [1, 2, 3, 4], "the rubric does not run 1-4")
    for r in rubric:
        both_lang(r["text"], f"rubric {r['points']}")

    both_lang(LEVEL["title"], "title")
    both_lang(LEVEL["blurb"], "blurb")
    both_lang(LEVEL["method"], "method")
    both_lang(LEVEL["caveat"], "caveat")

    if problems:
        for p in problems:
            print("FAIL  " + p)
        print(f"\n{len(problems)} problem(s); level_test.json not written")
        return 1

    payload = json.dumps(LEVEL, ensure_ascii=False, separators=(",", ":"))

    if "--check" in sys.argv[1:]:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != payload:
            print("FAIL  level_test.json is out of date with tools/level_test.py")
            return 1
        print("PASS  level_test.json matches tools/level_test.py")
        return 0

    OUT.write_text(payload, encoding="utf-8")
    by_skill = defaultdict(int)
    for it in items:
        by_skill[it["skill"]] += 1
    print(f"wrote level_test.json: {len(items)} items, {len(payload.encode())} bytes")
    print("       " + "  ".join(f"{k}:{by_skill[k]}" for k in ids))
    print("       formats " + " ".join(f"{k}:{v}" for k, v in sorted(kinds.items())))
    print("PASS  the bank and the blueprint agree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
