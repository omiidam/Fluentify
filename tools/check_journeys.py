#!/usr/bin/env python3
"""Checks the Journey framework and the journeys that fill it.

A journey is a topic taught in stages. The stages live in journeys.json; the
travel stages join travel.json by category id, and the sports stages carry their
own words, because this project has no general sports dictionary and inventing
one to duplicate would be worse than owning the words. This suite holds both
kinds of journey to their own shape, holds the sports profiles to their fields,
and holds the page to the parts a learner touches: the entry from Useful
Sentences, the stage page, the pictures, progress, favourites and the quick
reference.

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
SENSES_FILE = ROOT / "senses.json"
WEBAPP = ROOT / "webapp.py"
BUILDER = ROOT / "build_apk_ui.py"
ASSETS = ROOT / "android/app/src/main/assets/www"

CEFR = {"A1", "A2", "B1", "B2", "C1", "C2"}
KINDS = {"expression", "idiom", "phrasal_verb", "collocation"}
PERSIAN = re.compile(r"[\u0600-\u06FF]")
IPA = re.compile(r"/[^/]+/")

# The sports the brief names, by the ids the profiles use.
REQUIRED_SPORTS = [
    "soccer", "football", "basketball", "volleyball", "rugby", "cricket",
    "baseball", "softball", "handball", "fieldhockey", "icehockey",
    "tennis", "tabletennis", "badminton", "squash", "padel",
    "running", "marathon", "longjump", "highjump", "gymnastics",
    "weightlifting", "golf", "archery", "bowling",
    "swimming", "diving", "waterpolo", "surfing", "sailing", "rowing", "kayaking",
    "boxing", "wrestling", "judo", "karate", "taekwondo", "fencing",
    "cycling", "mountainbike", "climbing", "skiing", "snowboarding",
    "iceskating", "skateboarding", "horse",
]

fails: list[str] = []
notes: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    if ok:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}" + (f"  - {detail}" if detail else ""))
        fails.append(name)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check_stage(sid: str, st: dict, needs_refs: bool, needs_words: bool) -> None:
    check(f"{sid}: has a title and a Persian title",
          bool(st.get("title_en")) and bool(st.get("title_fa")))
    check(f"{sid}: has a blurb in both languages",
          bool(st.get("blurb_en")) and bool(st.get("blurb_fa")))
    obj = st.get("objectives") or []
    check(f"{sid}: at least 3 learning objectives", len(obj) >= 3, str(len(obj)))
    check(f"{sid}: every objective is translated",
          all(o.get("en") and o.get("fa") for o in obj))

    exprs = st.get("expressions") or []
    check(f"{sid}: at least 4 expressions and idioms", len(exprs) >= 4, str(len(exprs)))
    kinds = {x.get("kind") for x in exprs}
    check(f"{sid}: uses known expression kinds", kinds <= KINDS, str(kinds))
    check(f"{sid}: every expression has a meaning, a register and a Persian",
          all(x.get("en") and x.get("fa") and x.get("meaning_en")
              and x.get("meaning_fa") and x.get("register") for x in exprs))

    pats = st.get("patterns") or []
    check(f"{sid}: at least 2 patterns", len(pats) >= 2, str(len(pats)))
    check(f"{sid}: every pattern has a variable slot",
          all(("[" in p.get("frame", "") or "+" in p.get("frame", "")) for p in pats),
          str([p.get("frame") for p in pats]))

    sents = st.get("sentences") or []
    check(f"{sid}: at least 2 sentences of its own", len(sents) >= 2, str(len(sents)))
    bad_lvl = [x.get("en") for x in sents if x.get("level") not in CEFR]
    check(f"{sid}: every sentence carries a CEFR level", not bad_lvl, str(bad_lvl))
    check(f"{sid}: every sentence is explained and translated",
          all(x.get("en") and x.get("fa") and x.get("use_en") and x.get("use_fa")
              for x in sents))

    d = st.get("dialogue") or {}
    lines = d.get("lines") or []
    who = {ln.get("who") for ln in lines}
    check(f"{sid}: the conversation has at least 6 lines", len(lines) >= 6, str(len(lines)))
    check(f"{sid}: the conversation has at least 2 speakers", len(who) >= 2, str(who))
    check(f"{sid}: every line is translated",
          all(ln.get("en") and ln.get("fa") and ln.get("who") for ln in lines))

    scn = st.get("scenarios") or []
    check(f"{sid}: at least 2 practical scenarios", len(scn) >= 2, str(len(scn)))
    check(f"{sid}: every scenario has a task and a model answer",
          all(c.get("task_en") and c.get("answer_en") and c.get("situation_en")
              for c in scn))

    prac = st.get("practice") or []
    check(f"{sid}: at least 3 practice items", len(prac) >= 3, str(len(prac)))
    check(f"{sid}: every practice item has its answer among the options",
          all(p.get("answer") in (p.get("options") or []) for p in prac))
    check(f"{sid}: every practice item explains its answer",
          all(p.get("why_en") and p.get("why_fa") for p in prac))

    if needs_words:
        words = st.get("words") or []
        check(f"{sid}: at least 4 words of its own", len(words) >= 4, str(len(words)))
        check(f"{sid}: every word has a reading", all(w.get("ipa") for w in words))
        check(f"{sid}: every word's reading is IPA in slashes",
              all(IPA.search(w.get("ipa") or "") for w in words),
              str([w.get("ipa") for w in words if not IPA.search(w.get("ipa") or "")][:3]))
        check(f"{sid}: every word has a part of speech",
              all(w.get("pos") for w in words))
        check(f"{sid}: every word has a Persian and a definition",
              all(w.get("fa") and w.get("def_en") for w in words))
        check(f"{sid}: every word has an example and its Persian",
              all(w.get("example_en") and w.get("example_fa") for w in words))
        check(f"{sid}: every word carries a CEFR level",
              all(w.get("level") in CEFR for w in words))
        check(f"{sid}: every word says which sport it belongs to",
              all(w.get("sport") for w in words))
        check(f"{sid}: every word has a picture key", all(w.get("icon") for w in words))
    if needs_refs:
        check(f"{sid}: names travel categories", bool(st.get("refs")))


def main() -> int:
    if not JOURNEY_FILE.exists():
        print("  FAIL  journeys.json exists  - run tools/build_journeys.py")
        return 1
    doc = load(JOURNEY_FILE)
    bank = load(TRAVEL_FILE)
    senses = load(SENSES_FILE).get("words", {})
    cats = {c["id"]: c for c in bank.get("categories", [])}
    src = WEBAPP.read_text(encoding="utf-8")

    journeys = doc.get("journeys") or []
    by_id = {j.get("id"): j for j in journeys}
    check("the file holds the travel and sports journeys",
          {"travel", "sports"} <= set(by_id), str(sorted(by_id)))

    for jid in ("travel", "sports"):
        j = by_id.get(jid)
        if not j:
            continue
        for key in ("topic", "title_en", "title_fa", "blurb_en", "blurb_fa"):
            check(f"{jid}: declares {key}", bool(j.get(key)))
        check(f"{jid}: offered to both experiences",
              set(j.get("audiences") or []) == {"kids", "adults"},
              str(j.get("audiences")))
        check(f"{jid}: is not the other journey's title",
              j["title_en"] != (by_id.get("sports" if jid == "travel" else "travel") or {}).get("title_en"))

    travel = by_id.get("travel") or {"stages": []}
    sports = by_id.get("sports") or {"stages": []}
    tstages = travel.get("stages") or []
    sstages = sports.get("stages") or []

    check("the travel journey still has its twelve stages", len(tstages) == 12, str(len(tstages)))
    check("travel stage order is 1..12",
          [s.get("order") for s in tstages] == list(range(1, 13)),
          str([s.get("order") for s in tstages]))
    check("the sports journey has fourteen stages", len(sstages) == 14, str(len(sstages)))
    check("sports stage order is 1..14",
          [s.get("order") for s in sstages] == list(range(1, 15)),
          str([s.get("order") for s in sstages]))
    for jid, stages in (("travel", tstages), ("sports", sstages)):
        ids = [s.get("id") for s in stages]
        check(f"{jid}: stage ids are unique", len(set(ids)) == len(ids), str(ids))
        check(f"{jid}: every stage declares its audience",
              all(s.get("audiences") for s in stages))

    # ------------------------------------------------------------ the stages --
    for st in tstages:
        check_stage(st["id"], st, needs_refs=True, needs_words=False)
    for st in sstages:
        check_stage(st["id"], st, needs_refs=False, needs_words=True)

    # ------------------------------------------------------- the travel join --
    check("no travel stage carries its own word list",
          all("vocab" not in s for s in tstages))
    refs = [c for s in tstages for c in (s.get("refs") or [])]
    unknown = [r for r in refs if r not in cats]
    check("every travel stage category exists in travel.json", not unknown, str(unknown))
    reached = set(refs)
    joined_sent = sum(len(cats[r].get("sentences") or []) for r in reached)
    joined_words = sum(len(cats[r].get("vocab") or []) for r in reached)
    bank_sent = sum(len(c.get("sentences") or []) for c in cats.values())
    bank_words = sum(len(c.get("vocab") or []) for c in cats.values())
    check("the travel join reaches most of its bank",
          joined_sent >= bank_sent * 0.85 and joined_words >= bank_words * 0.85,
          f"{joined_sent}/{bank_sent} sentences, {joined_words}/{bank_words} words")

    # ---------------------------------------------------------- the profiles --
    profiles = sports.get("sports") or []
    ids = [p.get("id") for p in profiles]
    check("every named sport has a profile",
          all(s in ids for s in REQUIRED_SPORTS),
          str([s for s in REQUIRED_SPORTS if s not in ids]))
    check("sport ids are unique", len(set(ids)) == len(ids))
    check("sports count is reported", (sports.get("stats") or {}).get("sports") == len(profiles),
          str((sports.get("stats") or {}).get("sports")))
    for p in profiles:
        pid = p.get("id")
        check(f"{pid}: has a name, a Persian and a reading",
              bool(p.get("en")) and bool(p.get("fa")) and bool(IPA.search(p.get("ipa", ""))))
        check(f"{pid}: is classified", bool(p.get("category")))
        check(f"{pid}: has a definition and a place", bool(p.get("def_en")) and bool(p.get("venue")))
        check(f"{pid}: has equipment and actions",
              bool(p.get("equipment")) and bool(p.get("actions")))
        check(f"{pid}: has an example sentence and a Persian",
              bool(p.get("sentence_en")) and bool(p.get("sentence_fa")))
        check(f"{pid}: has an exchange you could say",
              bool(p.get("exchange_en")) and bool(p.get("exchange_fa")))
        check(f"{pid}: has a picture key", bool(p.get("icon")))
        check(f"{pid}: terms are translated",
              all(t.get("term") and t.get("fa") and t.get("meaning_en")
                  for t in (p.get("terms") or [])))

    shown = {s for st in sstages for s in (st.get("sportRefs") or [])}
    check("every profiled sport is reachable from a stage",
          shown == set(ids), str(sorted(set(ids) - shown)))
    terms = sum(len(p.get("terms") or []) for p in profiles)
    check("the profiles carry their own terminology", terms >= 40, str(terms))

    # -------------------------------------------------------------- the idioms --
    idioms = [x for x in (by_id.get("sports", {}).get("stages") or [])
              for x in (x.get("expressions") or []) if x.get("kind") == "idiom"]
    check("the sports journey teaches at least 12 idioms", len(idioms) >= 12, str(len(idioms)))
    def both_readings(x: dict) -> bool:
        """The word 'literally', or the sport it came from, then the figurative use."""
        m = x.get("meaning_en") or ""
        literal = "iterally" in m or m.lstrip().startswith("From ")
        return literal and "iguratively" in m

    check("every idiom separates the literal reading from the figurative one",
          all(both_readings(x) for x in idioms),
          str([x.get("en") for x in idioms if not both_readings(x)][:4]))
    check("every idiom has an example in context",
          all(x.get("example_en") and x.get("example_fa") for x in idioms))
    check("every idiom is labelled for register",
          all(x.get("register") for x in idioms))
    check("phrasal verbs are labelled as phrasal verbs",
          any(x.get("kind") == "phrasal_verb"
              for s in (by_id.get("sports", {}).get("stages") or [])
              for x in (s.get("expressions") or [])))

    # ----------------------------------------------------------- the pictures --
    art_block = src[src.index("const ART = {"):src.index("function art(key, label)")]
    art_keys = set(re.findall(r"^\s{4}([a-z]+):", art_block, re.M))
    used = {j.get("art") for j in journeys}
    used |= {s.get("icon") for j in journeys for s in (j.get("stages") or [])}
    used |= {w.get("icon") for j in journeys for s in (j.get("stages") or [])
             for w in (s.get("words") or [])}
    used |= {p.get("icon") for p in profiles}
    missing = sorted(k for k in used if k and k not in art_keys and len(k) > 2
                     and not k.isascii() is False and not re.search(r"[^\x00-\x7F]", k))
    check("every picture key is drawn in the page", not missing, str(missing))
    check("the page draws the sport pictograms",
          {"soccer", "basketball", "swimming", "tennis", "bike", "gymnastics"} <= art_keys,
          str(sorted({"soccer", "basketball", "swimming", "tennis", "bike", "gymnastics"} - art_keys)))
    check("the pictures carry an accessible name",
          'role="img" aria-label="' in src)
    check("a picture is drawn, not fetched", "<svg viewBox=\"0 0 32 32\"" in src)
    check("the stage page shows the sport cards", "function sportCard(" in src
          and "sportsSection(st)" in src)
    check("the words are shown with their reading", "'jn-ipa', w.ipa" in src)

    # --------------------------------------------------------------- the page --
    check("the page defines the Journey module", src.count("const Journey = (() => {") == 1)
    check("Useful Sentences offers the Sports journey",
          "Journey.card('sports', false)" in src and "Journey.card('sports', true)" in src)
    check("the travel card still opens the travel journey",
          "b.onclick = () => Journey.open(isKid);" in src)
    check("an entry card can open a named journey",
          "function card(id, kidsFlag)" in src and "open(isKid, id)" in src)
    check("a journey is chosen by id", "let currentId =" in src
          and "find((j) => j.id === currentId)" in src)
    check("the flat travel list survives", "function openBrowse(kidsFlag)" in src
          and "Travel.openBrowse(" in src)
    check("progress and favourites keep one local key each",
          "fluentify.journey.v1" in src and "fluentify.journey.fav.v1" in src)
    check("the quick reference searches words, sports and idioms",
          "kind: 'sport'" in src and "kind: 'term'" in src and "kind: 'word', en: w.en" in src)
    check("the quick reference filters by stage and level",
          "searchRows(q, stageSel.value, lvlSel.value)" in src)
    check("the route serves the journey file",
          '"/api/journeys"' in src and 'ROOT / "journeys.json"' in src)

    # ---------------------------------------------------------------- the APK --
    check("the APK bundles journeys.json",
          '"journeys.json"' in BUILDER.read_text(encoding="utf-8"))
    bundled = ASSETS / "data" / "journeys.json"
    check("the bundled copy is there", bundled.exists(), str(bundled))
    if bundled.exists():
        check("the bundled copy is the built file",
              bundled.read_bytes() == JOURNEY_FILE.read_bytes(),
              "run python3 build_apk_ui.py")

    # ---------------------------------------------------------------- text ----
    check("the Persian in the sports journey is Persian",
          all(PERSIAN.search(s.get("title_fa") or "") for s in sstages))
    check("the file records its own statistics",
          bool((doc.get("_meta") or {}).get("stats")))

    exprs = sum(len(s["expressions"]) for s in sstages)
    words = sum(len(s["words"]) for s in sstages)
    sents = sum(len(s["sentences"]) for s in sstages)
    prac = sum(len(s["practice"]) for s in sstages)
    notes.append(f"sports: {len(sstages)} stages, {words} words with IPA, {exprs} expressions "
                 f"and idioms ({len(idioms)} idioms), {len(profiles)} sport profiles with "
                 f"{terms} key terms, {sents} own sentences, {prac} practice items; "
                 f"travel: {len(tstages)} stages joining {joined_sent} bank sentences")

    print()
    if fails:
        print(f"  {len(fails)} journey check(s) failed")
        return 1
    print("  PASS  " + " ".join(notes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
