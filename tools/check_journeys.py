#!/usr/bin/env python3
"""Checks the Journey framework and the Travel journey that fills it.

A journey is a topic taught in stages. The stages live in journeys.json; the
words, sentences and dialogues they teach stay in travel.json and are joined by
category id, so there is one copy of the bank and one set of ids. This suite
holds the file to its own shape, holds the join to the real bank, and holds the
page to the parts a learner touches: the entry from Useful Sentences, the stage
page, progress, favourites and the quick reference.

Run: python3 tools/check_journeys.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JOURNEY_FILE = ROOT / "journeys.json"
TRAVEL_FILE = ROOT / "travel.json"
WEBAPP = ROOT / "webapp.py"
BUILDER = ROOT / "build_apk_ui.py"
ASSETS = ROOT / "android/app/src/main/assets/www"

CEFR = {"A1", "A2", "B1", "B2", "C1", "C2"}
KINDS = {"expression", "idiom", "phrasal_verb", "collocation"}
PERSIAN = re.compile(r"[\u0600-\u06FF]")
PIPE = "|"

fails: list[str] = []
notes: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    if ok:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}" + (f"  — {detail}" if detail else ""))
        fails.append(name)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    if not JOURNEY_FILE.exists():
        print("  FAIL  journeys.json exists  — run tools/build_journeys.py")
        return 1
    doc = load(JOURNEY_FILE)
    bank = load(TRAVEL_FILE)
    cats = {c["id"]: c for c in bank.get("categories", [])}
    journeys = doc.get("journeys") or []
    src = WEBAPP.read_text(encoding="utf-8")

    # ---------------------------------------------------------- the shape --
    check("journeys.json holds at least one journey", len(journeys) >= 1)
    j = journeys[0]
    for key in ("id", "topic", "title_en", "title_fa", "blurb_en", "blurb_fa", "audiences"):
        check(f"the journey declares {key}", bool(j.get(key)), str(j.get(key)))
    check("the journey is offered to both experiences",
          set(j.get("audiences") or []) == {"kids", "adults"},
          str(j.get("audiences")))
    check("the journey is travel", j.get("id") == "travel" and j.get("topic") == "travel")

    stages = j.get("stages") or []
    check("the travel journey has its twelve stages", len(stages) == 12, str(len(stages)))
    check("stage order is 1..12 without a hole",
          [s.get("order") for s in stages] == list(range(1, 13)),
          str([s.get("order") for s in stages]))
    ids = [s.get("id") for s in stages]
    check("stage ids are unique", len(set(ids)) == len(ids), str(ids))

    # Every journey is a sequence of the same seven kinds of work, whatever the
    # topic: the words, the expressions, the patterns, the sentences, the
    # conversation, the situation, the check.
    check("every stage teaches objectives, expressions, patterns, sentences,"
          " a dialogue, scenarios and practice",
          all((s.get("objectives") and s.get("expressions") and s.get("patterns")
               and s.get("sentences") and s.get("dialogue") and s.get("scenarios")
               and s.get("practice")) for s in stages))

    # ------------------------------------------------------------ content --
    empty_fa = []
    for s in stages:
        sid = s.get("id", "?")
        check(f"{sid}: has a title and a Persian title",
              bool(s.get("title_en")) and bool(s.get("title_fa")))
        check(f"{sid}: has a blurb in both languages",
              bool(s.get("blurb_en")) and bool(s.get("blurb_fa")))
        obj = s.get("objectives") or []
        check(f"{sid}: at least 3 learning objectives", len(obj) >= 3, str(len(obj)))
        if any(not (o.get("en") and o.get("fa")) for o in obj):
            empty_fa.append(f"{sid} objectives")

        exprs = s.get("expressions") or []
        check(f"{sid}: at least 4 expressions and idioms", len(exprs) >= 4, str(len(exprs)))
        kinds = {x.get("kind") for x in exprs}
        check(f"{sid}: uses a known expression kind", kinds <= KINDS, str(kinds))
        check(f"{sid}: teaches at least one idiom or phrasal verb",
              bool({"idiom", "phrasal_verb"} & kinds), str(kinds))
        for x in exprs:
            if not (x.get("en") and x.get("fa") and x.get("meaning_en")
                    and x.get("meaning_fa") and x.get("register")):
                empty_fa.append(f"{sid} expression {x.get('en', '?')}")

        pats = s.get("patterns") or []
        check(f"{sid}: at least 2 patterns", len(pats) >= 2, str(len(pats)))
        check(f"{sid}: every pattern has a variable slot",
              all(("[" in p.get("frame", "") or "+" in p.get("frame", ""))
                  for p in pats),
              str([p.get("frame") for p in pats]))

        sents = s.get("sentences") or []
        check(f"{sid}: at least 2 sentences of its own", len(sents) >= 2, str(len(sents)))
        bad_lvl = [x.get("en") for x in sents if x.get("level") not in CEFR]
        check(f"{sid}: every sentence carries a CEFR level", not bad_lvl, str(bad_lvl))
        for x in sents:
            if not (x.get("en") and x.get("fa") and x.get("use_en") and x.get("use_fa")):
                empty_fa.append(f"{sid} sentence {x.get('en', '?')}")

        d = s.get("dialogue") or {}
        lines = d.get("lines") or []
        who = {ln.get("who") for ln in lines}
        check(f"{sid}: the conversation has at least 6 lines", len(lines) >= 6, str(len(lines)))
        check(f"{sid}: the conversation has at least 2 speakers", len(who) >= 2, str(who))
        check(f"{sid}: every line is translated",
              all(ln.get("en") and ln.get("fa") and ln.get("who") for ln in lines))

        scn = s.get("scenarios") or []
        check(f"{sid}: at least 2 practical scenarios", len(scn) >= 2, str(len(scn)))
        check(f"{sid}: every scenario has a task and a model answer",
              all(c.get("task_en") and c.get("answer_en") and c.get("situation_en")
                  for c in scn))

        prac = s.get("practice") or []
        check(f"{sid}: at least 3 practice items", len(prac) >= 3, str(len(prac)))
        check(f"{sid}: every practice item has its answer among the options",
              all(p.get("answer") in (p.get("options") or []) for p in prac))
        check(f"{sid}: every practice item explains its answer",
              all(p.get("why_en") and p.get("why_fa") for p in prac))

    check("no journey field is missing its Persian", not empty_fa, ", ".join(empty_fa[:4]))

    # --------------------------------------------------------------- join --
    check("no stage carries its own word list",
          all("vocab" not in s for s in stages),
          "words must come from travel.json, or there are two dictionaries")
    refs = [c for s in stages for c in (s.get("refs") or [])]
    check("every stage points at bank categories", all(s.get("refs") for s in stages))
    unknown = [r for r in refs if r not in cats]
    check("every category id exists in travel.json", not unknown, str(unknown))
    reached = set(refs)
    joined_sent = sum(len(cats[r].get("sentences") or []) for r in reached)
    joined_words = sum(len(cats[r].get("vocab") or []) for r in reached)
    bank_sent = sum(len(c.get("sentences") or []) for c in cats.values())
    bank_words = sum(len(c.get("vocab") or []) for c in cats.values())
    # Most of the bank must be reachable from a stage, or the journey is a
    # sample of the bank rather than the way into it.
    check("the join reaches most of the travel bank",
          joined_sent >= bank_sent * 0.85 and joined_words >= bank_words * 0.85,
          f"{joined_sent}/{bank_sent} sentences, {joined_words}/{bank_words} words")
    check("the journey does not repeat a category id inside one stage",
          all(len(s.get("refs") or []) == len(set(s.get("refs") or [])) for s in stages))

    # ------------------------------------------------------------ the text --
    text = JOURNEY_FILE.read_text(encoding="utf-8")
    check("no field leaks its pipe delimiter", PIPE not in
          "".join(str(v) for s in stages for v in
                  [s.get("title_en", ""), s.get("title_fa", ""), s.get("blurb_en", "")]))
    fa_fields = [s.get("title_fa", "") for s in stages]
    check("the Persian text is Persian",
          all(PERSIAN.search(t or "") for t in fa_fields),
          str([t for t in fa_fields if not PERSIAN.search(t or "")][:3]))
    check("the file records its own statistics", bool((doc.get("_meta") or {}).get("stats")))

    # ------------------------------------------------------------- the page --
    check("the page defines the Journey module",
          src.count("const Journey = (() => {") == 1)
    check("the Useful Sentences card opens the journey",
          "b.onclick = () => Journey.open(isKid);" in src)
    check("the flat bank survives as a browse view",
          "function openBrowse(kidsFlag)" in src and "Travel.openBrowse(" in src)
    check("the journey page renders into the Sentences panel",
          "document.getElementById('ftopics')" in src)
    check("a stage opens from the overview and from a result",
          "card.onclick = () => stagePage(s.id);" in src and "function stagePage(id)" in src)
    check("progress is written to one local key",
          "fluentify.journey.v1" in src and "function markDone(" in src)
    check("favourites are written to one local key",
          "fluentify.journey.v1" != "fluentify.journey.fav.v1"
          and "fluentify.journey.fav.v1" in src)
    check("the overview offers continue and quick reference",
          "Continue: " in src and "Quick reference" in src)
    check("the quick reference answers with a next step",
          "Next step: " in src and "next: c.answer_en" in src)
    check("the quick reference searches English and Persian",
          "fold([r.en, r.fa, r.use, r.useFa" in src)
    check("every stage has practice with feedback",
          "classList.add('ok')" in src and "jn-why" in src)
    check("audio goes through the existing speech engine",
          "Speech.speak" in src and "jn-play" in src)
    css_block = (src.split("journeys: one topic")[1].split("FLUENTIFY KIDS")[0]
                 if "journeys: one topic" in src else "")
    check("the journey styles exist", bool(css_block.strip()))
    check("the journey styles use theme tokens only",
          not re.search(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(", css_block),
          "a literal colour would not follow the dark theme")
    check("the kids shell gets its own scale",
          "body.kids .jn-" in src)
    check("the route serves the journey file",
          '"/api/journeys"' in src and 'ROOT / "journeys.json"' in src)

    # ------------------------------------------------------------- the APK --
    builder = BUILDER.read_text(encoding="utf-8")
    check("the APK bundles journeys.json", '"journeys.json"' in builder)
    bundled = ASSETS / "data" / "journeys.json"
    check("the bundled copy is there", bundled.exists(), str(bundled))
    if bundled.exists():
        check("the bundled copy is the built file",
              bundled.read_bytes() == JOURNEY_FILE.read_bytes(),
              "run python3 build_apk_ui.py")

    # --------------------------------------------------------------- count --
    exprs = sum(len(s["expressions"]) for s in stages)
    pats = sum(len(s["patterns"]) for s in stages)
    own = sum(len(s["sentences"]) for s in stages)
    prac = sum(len(s["practice"]) for s in stages)
    notes.append(f"{len(stages)} stages, {exprs} expressions and idioms, "
                 f"{pats} patterns, {own} own sentences, {prac} practice items; "
                 f"joins {joined_sent} bank sentences and {joined_words} bank words")

    print()
    if fails:
        print(f"  {len(fails)} journey check(s) failed")
        return 1
    print("  PASS  " + " ".join(notes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
