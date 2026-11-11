#!/usr/bin/env python3
"""Is the Travel curriculum real, complete and wired into both experiences?

    python3 tools/check_travel.py

The travel bank is generated from tools/travel_content.txt by
tools/build_travel.py, so this reads the generated file the page actually
fetches and asks the questions a learner would: is every mandatory situation
there, does every sentence carry all ten teaching fields, is the Persian
genuinely Persian, does each category have its words and its dialogue, and is
the thing reachable from Useful Sentences in both the web page and the APK.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRAVEL = ROOT / "travel.json"
WEBAPP = ROOT / "webapp.py"
BUILD = ROOT / "build_apk_ui.py"
BUNDLE = ROOT / "android/app/src/main/assets/www"

PERSIAN = re.compile(r"[\u0600-\u06FF]")
LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
POLITE = {"n", "p", "i"}
REQUIRED = ["planning", "airport", "security", "onboard", "arrival", "transport",
            "directions", "hotel", "restaurant", "shopping", "sightseeing",
            "technology", "health", "emergency", "problems", "accessibility",
            "family", "returning"]

problems = []
stats = {}


def check(cond, line):
    if not cond:
        problems.append(line)
    print(f"  {'ok  ' if cond else 'FAIL'}  {line}")
    return cond


def norm(s):
    return re.sub(r"[^0-9a-z]+", " ", str(s or "").lower()).strip()


def check_sentences(cat):
    name = cat.get("id")
    seen = set()
    for s in cat.get("sentences") or []:
        where = f"{name}/{s.get('id') or '?'}"
        check(bool(s.get("id")) and s["id"] not in seen, f"{where}: the id is missing or repeated")
        seen.add(s.get("id"))
        check(bool(s.get("en")), f"{where}: no English sentence")
        check(bool(PERSIAN.search(s.get("fa") or "")), f"{where}: the Persian is missing")
        check(bool((s.get("use_en") or "").strip()), f"{where}: no explanation of what it is for")
        check(bool(PERSIAN.search(s.get("use_fa") or "")), f"{where}: the explanation is not translated")
        check(s.get("level") in LEVELS, f"{where}: the level {s.get('level')!r} is not a CEFR band")
        check(s.get("polite") in POLITE, f"{where}: politeness {s.get('polite')!r} is not n/p/i")
        check(bool(s.get("polite_en")) and bool(s.get("polite_fa")),
              f"{where}: the politeness label is not bilingual")
        alts = s.get("alt") or []
        check(isinstance(alts, list), f"{where}: alternatives are not a list")
        for a in alts:
            check(bool(a.get("en")) and bool(PERSIAN.search(a.get("fa") or "")),
                  f"{where}: an alternative is not bilingual")
        check(not re.search(r"\s{2,}", s.get("en") or ""), f"{where}: double spaces in the English")


def check_vocab(cat):
    for w in cat.get("vocab") or []:
        where = f"{cat.get('id')}/{w.get('en') or '?'}"
        check(bool(w.get("en")), f"{where}: a word has no English form")
        check(bool(PERSIAN.search(w.get("fa") or "")), f"{where}: the word has no Persian")
        check(bool((w.get("def_en") or "").strip()), f"{where}: no definition")
        check((w.get("pos") or "") in ("noun", "verb", "adjective", "adverb", "phrase"),
              f"{where}: part of speech {w.get('pos')!r} is not one the page knows")
        example = w.get("example_en") or ""
        check(w.get("en", "").split()[0].lower() in example.lower(),
              f"{where}: the example does not use the word")


def check_dialogue(cat):
    d = cat.get("dialogue") or {}
    where = f"{cat.get('id')}/dialogue"
    check(bool(d.get("title_en")) and bool(PERSIAN.search(d.get("title_fa") or "")),
          f"{where}: the dialogue has no bilingual title")
    lines = d.get("lines") or []
    check(len(lines) >= 4, f"{where}: {len(lines)} lines, expected at least 4")
    who = set()
    for line in lines:
        check(bool(line.get("who")), f"{where}: a line has no speaker")
        who.add(line.get("who"))
        check(bool(line.get("en")) and bool(PERSIAN.search(line.get("fa") or "")),
              f"{where}: a line is not bilingual")
    check(len(who) >= 2, f"{where}: a dialogue needs at least two speakers")


def check_pattern(cat):
    p = cat.get("pattern")
    if not p:
        return
    where = f"{cat.get('id')}/pattern"
    check("+" in p.get("frame", ""), f"{where}: the frame does not show what can be swapped")
    check(bool(p.get("example_en")), f"{where}: no worked example")
    check(bool(p.get("note_en")) and bool(PERSIAN.search(p.get("note_fa") or "")),
          f"{where}: the note is not bilingual")


def check_wiring(src, build):
    check("const Travel = (() => {" in src, "the travel layer is not on the page")
    check("loadJSON('travel')" in src, "the page never reads the travel bank")
    check('"/api/travel"' in src or "'/api/travel'" in src,
          "the server does not serve the travel bank")
    check("Travel.card(" in src, "Useful Sentences has no travel entry point")
    check("Travel.open(" in src, "nothing opens the travel experience")
    check('"travel.json"' in build or "'travel.json'" in build,
          "the APK bundle does not carry travel.json")
    kids = src[src.index("async function phrases()"):]
    kids = kids[:kids.index("\n  }\n")]
    check("Travel.card(true)" in kids,
          "the kids sentence list has no travel entry")
    adults = src[src.index("async function loadPhrases()"):]
    adults = adults[:adults.index("\n}\n")]
    check("Travel.card(false)" in adults,
          "the adult sentence panel has no travel entry")
    for name in ("Travel.openCat", "Travel.practice", "Travel.search"):
        check(name in src or name.split(".")[1] in src, f"{name} is missing")


def main():
    if not TRAVEL.exists():
        print("FAIL  travel.json does not exist - run tools/build_travel.py")
        return 1
    doc = json.loads(TRAVEL.read_text(encoding="utf-8"))
    src = WEBAPP.read_text(encoding="utf-8")
    build = BUILD.read_text(encoding="utf-8")
    cats = doc.get("categories") or []
    meta = doc.get("_meta") or {}

    print("the travel bank")
    ids = [c.get("id") for c in cats]
    check(len(cats) == 18, f"the bank has {len(cats)} categories, expected 18")
    for cid in REQUIRED:
        check(cid in ids, f"the mandatory category {cid} is missing")
    check(len(set(ids)) == len(ids), "two categories share an id")

    seen_en = {}
    for cat in cats:
        name = cat.get("id")
        check(bool(cat.get("emoji")), f"{name}: the category has no picture")
        check(bool(cat.get("title_en")) and bool(PERSIAN.search(cat.get("title_fa") or "")),
              f"{name}: the title is not bilingual")
        check(bool(cat.get("desc_en")) and bool(PERSIAN.search(cat.get("desc_fa") or "")),
              f"{name}: the description is not bilingual")
        check(cat.get("level") in LEVELS, f"{name}: the category level is not a CEFR band")
        check(len(cat.get("sentences") or []) >= 4,
              f"{name}: {len(cat.get('sentences') or [])} sentences, expected at least 4")
        check(len(cat.get("vocab") or []) >= 4,
              f"{name}: {len(cat.get('vocab') or [])} words, expected at least 4")
        check_sentences(cat)
        check_vocab(cat)
        check_dialogue(cat)
        check_pattern(cat)
        for s in cat.get("sentences") or []:
            key = norm(s.get("en"))
            if key in seen_en and seen_en[key] != s.get("id"):
                check(False, f"{name}: '{s.get('en')}' repeats {seen_en[key]}")
            seen_en[key] = s.get("id")

    levels = sorted({s["level"] for c in cats for s in c.get("sentences") or []},
                    key=LEVELS.index)
    check(levels == meta.get("levels"),
          f"the level list {meta.get('levels')} does not match the sentences {levels}")
    check("B2" in levels and "C1" in levels,
          f"the bank stops at {levels[-1]}: the brief asks for B2 and C1 composition")
    check(bool(PERSIAN.search(meta.get("intro_fa") or "")), "the intro is not translated")
    check("not legal" in (meta.get("note_en") or "").lower()
          and "medical" in (meta.get("note_en") or "").lower(),
          "the note does not say this is not legal or medical advice")

    print("\nthe page and the bundle")
    check_wiring(src, build)
    check((BUNDLE / "data/travel.json").exists(),
          "the APK bundle has no travel.json - run build_apk_ui.py")
    if (BUNDLE / "data/travel.json").exists():
        bundled = json.loads((BUNDLE / "data/travel.json").read_text(encoding="utf-8"))
        check(bundled == doc, "the bundled travel.json is stale - run build_apk_ui.py")
    empty = re.findall(r"tr-[a-z]+ \{\}", src)
    check(not empty, f"empty travel rules on the page: {empty[:3]}")

    stats["cats"] = len(cats)
    stats["sentences"] = sum(len(c.get("sentences") or []) for c in cats)
    stats["vocab"] = sum(len(c.get("vocab") or []) for c in cats)
    stats["dialogues"] = sum(1 for c in cats if c.get("dialogue"))
    stats["levels"] = levels

    if problems:
        print()
        for p in problems[:40]:
            print("FAIL  " + p)
        if len(problems) > 40:
            print(f"      ... and {len(problems) - 40} more")
        print(f"\nFAIL  {len(problems)} problem(s) in the travel bank")
        return 1

    print(f"\nPASS  {stats['cats']} travel categories with {stats['sentences']} sentences, "
          f"{stats['vocab']} words and {stats['dialogues']} dialogues, levels "
          f"{' '.join(stats['levels'])}, reachable from Useful Sentences in the page and "
          "carried in the APK bundle")
    return 0


if __name__ == "__main__":
    sys.exit(main())
