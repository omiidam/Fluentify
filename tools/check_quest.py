#!/usr/bin/env python3
"""Is Hero Quest a real game, and can a child finish one without the network?

    python3 tools/check_quest.py

The game is small on purpose, and every part of it has to be true at once:

  the content   six ranks in order, three missions each, six or so challenges
                per mission, every reference into kids.json pointing at
                something that exists, and every answer key consistent - a
                multiple choice whose answer is not one of its options is a
                question a child cannot win.

  the wiring    one header tile, one full page, a panel with a hook, and the
                whole thing behind Experience.kids() so an adult never sees it.

  the offline   the page must reach the game the same way in the browser and
                inside the APK: heroquest.json in the bundle, read through
                loadJSON, no fetch('/api/...') left in the built page.

  the sync      the merge that makes a replayed request harmless. This runs the
                server's own merge_quest_events() rather than a copy, because
                the property that matters is idempotence, not shape.

The JavaScript engine itself is exercised by the browser; what a static suite
can pin is the data it reads and the seams it hangs from.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEBAPP = ROOT / "webapp.py"
QUEST = ROOT / "heroquest.json"
KIDS = ROOT / "kids.json"
BUILD = ROOT / "build_apk_ui.py"
BUNDLE = ROOT / "android/app/src/main/assets/www"

problems = []
stats = {}

PERSIAN = re.compile(r"[\u0600-\u06FF]")


def check(cond, line):
    if not cond:
        problems.append(line)
    print(f"  {'ok  ' if cond else 'FAIL'}  {line}")
    return cond


def three_options(item, label, key="options"):
    options = item.get(key) or []
    if not check(len(options) == 3, f"{label}: needs three options, got {len(options)}"):
        return False
    if not check(len(set(options)) == 3, f"{label}: two options are the same"):
        return False
    return check(item.get("answer") in options,
                 f"{label}: the answer is not one of its options")


def check_content(doc, kids):
    ranks = doc.get("ranks") or []
    missions = doc.get("missions") or []
    check(len(ranks) == 6, f"the adventure needs six ranks, got {len(ranks)}")
    expected = ["Brave Beginner", "Word Explorer", "Sentence Builder",
                "Grammar Guardian", "Story Hero", "English Champion"]
    check([r.get("name_en") for r in ranks] == expected,
          "the ranks are not the six named ones, in order")
    for rank in ranks:
        for key in ("name_fa", "cefr", "place_en", "place_fa", "story_en", "story_fa", "emoji"):
            check(bool(rank.get(key)), f"{rank.get('id')}: the rank is missing {key}")
        check(bool(PERSIAN.search(rank.get("story_fa") or "")),
              f"{rank.get('id')}: the rank story has no Persian")

    check(len(missions) == 18, f"eighteen missions expected, got {len(missions)}")
    check(len({m.get("id") for m in missions}) == len(missions),
          "two missions share an id")
    for rank in ranks:
        mine = [m for m in missions if m.get("rank") == rank.get("id")]
        check(len(mine) == 3, f"{rank.get('id')}: {len(mine)} missions instead of three")
        check([m.get("order") for m in mine] == [1, 2, 3],
              f"{rank.get('id')}: the mission order is not 1, 2, 3")

    themes = {t.get("id") for t in kids.get("words") or []}
    lessons = {g.get("id") for g in kids.get("grammar") or []}
    phrases = {p.get("id") for p in kids.get("phrases") or []}
    passages = {r.get("id") for r in kids.get("reading") or []}
    clips = {c.get("id") for c in kids.get("listening") or []}

    for mission in missions:
        mid = mission.get("id")
        for key in ("title_en", "title_fa", "place_en", "place_fa", "objective_en",
                    "objective_fa", "cefr", "emoji"):
            check(bool(mission.get(key)), f"{mid}: missing {key}")
        check(bool(mission.get("skills")), f"{mid}: no skill is named")
        check(bool(PERSIAN.search(mission.get("objective_fa") or "")),
              f"{mid}: the objective has no Persian")

        # what the recipe adds up to, without running the page's builder
        slots = 0
        for step in mission.get("build") or []:
            kind = step.get("type")
            if kind == "vocab":
                check(step.get("theme") in themes,
                      f"{mid}: vocab theme {step.get('theme')!r} is not in kids.json")
                slots += int(step.get("n") or 0)
            elif kind == "match":
                check(step.get("theme") in themes,
                      f"{mid}: match theme {step.get('theme')!r} is not in kids.json")
                slots += 1
            elif kind == "grammar":
                check(step.get("lesson") in lessons,
                      f"{mid}: grammar lesson {step.get('lesson')!r} is not in kids.json")
                slots += 1
            elif kind == "order":
                check(step.get("lesson") in lessons,
                      f"{mid}: order lesson {step.get('lesson')!r} is not in kids.json")
                slots += 1
            elif kind == "phrase":
                check(step.get("set") in phrases,
                      f"{mid}: phrase set {step.get('set')!r} is not in kids.json")
                slots += 1
            elif kind == "read":
                check(step.get("passage") in passages,
                      f"{mid}: passage {step.get('passage')!r} is not in kids.json")
                slots += 1
            elif kind == "listen":
                check(step.get("clip") in clips,
                      f"{mid}: clip {step.get('clip')!r} is not in kids.json")
                slots += 1
            else:
                check(False, f"{mid}: unknown build step {kind!r}")

        authored = mission.get("authored") or []
        slots += len(authored)
        check(5 <= slots <= 8,
              f"{mid}: {slots} challenges; a mission should hold five to eight")

        for i, item in enumerate(authored):
            label = f"{mid} authored #{i + 1}"
            kind = item.get("t")
            check(kind in ("choice", "error", "fill", "order", "read", "listen"),
                  f"{label}: unknown challenge type {kind!r}")
            # order challenges are prompted by the engine ("put the words in
            # order"), so only the other types carry their own question
            check(bool(item.get("q")) or kind == "order", f"{label}: no question")
            check(bool(item.get("why_en")) and bool(item.get("why_fa")),
                  f"{label}: the explanation is not in both languages")
            check(bool(PERSIAN.search(item.get("why_fa") or "")),
                  f"{label}: the Persian explanation is not Persian")
            if kind in ("choice", "error", "read", "listen"):
                three_options(item, label)
            if kind == "fill":
                accept = item.get("accept") or []
                check(bool(item.get("answer")), f"{label}: no answer")
                check(item.get("answer") in accept,
                      f"{label}: the answer is not in its accepted list")
            if kind == "order":
                check(len(str(item.get("answer") or "").split()) >= 3,
                      f"{label}: an ordering challenge needs at least three words")
            if kind == "read":
                check(bool(item.get("passage_en")) and bool(item.get("passage_fa")),
                      f"{label}: the passage is not in both languages")
                check(bool(PERSIAN.search(item.get("passage_fa") or "")),
                      f"{label}: the Persian passage is not Persian")
            if kind == "listen":
                check(len(item.get("lines") or []) >= 2,
                      f"{label}: a listening clip needs at least two lines")

    # the difficulty has to rise: the authored material must not be all A1
    cefr = [m.get("cefr") for m in missions]
    check(cefr[0] == "A1", "the first mission is not A1")
    check(any("B" in (c or "") for c in cefr), "nothing in the game reaches B level")
    check(sum(1 for m in missions if m.get("authored")) >= 9,
          "fewer than nine missions carry their own written challenges")

    stats["missions"] = len(missions)
    stats["authored"] = sum(len(m.get("authored") or []) for m in missions)


def check_page(src):
    check("const Quest = (() => {" in src, "there is no quest module on the page")
    check('id="hqtoggle"' in src, "the header has no Hero Quest tile")
    check('id="hqpanel"' in src, "the game has no page of its own")
    check('id="hqbody"' in src, "the game page has no body to draw into")
    check("hqpanel: 'hqtoggle'," in src, "the panel is not tied to its tile")
    check("hqpanel: () => { if (Experience.kids()) Quest.open(); }" in src,
          "the game panel has no kids-gated open hook")
    check("hqtoggle: 'Quest'," in src, "the kids toolbar does not label the game")
    check("hqpanel: ['Hero Quest', 'سفر قهرمان', '🗺️']," in src,
          "the game is not one of the sections a child can return to")
    check("document.getElementById('hqtoggle').onclick" in src,
          "the tile does not open anything")
    check("body:not(.kids) #hqtoggle, body:not(.kids) #hqpanel { display: none !important; }" in src,
          "an adult can see the game tile or its page")
    check("if (Panels.isOpen() === 'hqpanel') Panels.set('hqpanel', false);" in src,
          "leaving the kids band does not close the game")
    check("const on = () => typeof Experience !== 'undefined' && Experience.kids();" in src,
          "the game does not read the experience band")

    # the ranks are game progress, not CEFR: the level check picks the start
    check("RANK_OF_LEVEL" in src and "placement()" in src,
          "the game does not place a child from the level check")
    check("B1: 3" in src, "a B1 child does not start above the beginner ranks")
    check("localStorage.getItem('fluentify.level.v2.result')" in src,
          "the placement does not read the level result")
    check("localStorage.getItem('fluentify.path.v1')" in src,
          "the placement does not read the learning path")
    check("unlockedCount" in src and "rankDone" in src,
          "ranks do not unlock through finished missions")

    # every quest rule is scoped like the rest of the kids layer
    start = src.index("  /* ---------- Hero Quest")
    end = src.index("  body.kids .hqmap { grid-template-columns: 1fr 1fr; }", start)
    block = src[start:end]
    unscoped = []
    for line in block.splitlines():
        if "{" not in line or "body.kids" in line or line.strip().startswith(("@", "}", "/*", "*")):
            continue
        selector = line.split("{", 1)[0].strip()
        if selector.startswith(".") or selector.startswith("#"):
            unscoped.append(selector)
    check(not unscoped, f"quest rules reach adult markup: {unscoped[:5]}")

    # a tick and a cross, so an answer is not colour alone
    check("o.textContent = (right ? '✓ ' : (o === b ? '✗ ' : ''))" in src,
          "the quiz result is left to colour alone")

    # every mission saves one event with its own id
    check("const eid = mission.id" in src, "a finished mission has no event id")
    check("merge([{id: eid, m: mission.id, s: stars, at: at}])" in src,
          "the result is not recorded as an event")
    check("state.dirty = true" in src, "the result is not queued for sync")


def check_offline(src, build):
    check('"heroquest.json"' in build, "the offline bundle does not carry heroquest.json")
    check("loadJSON('heroquest')" in src, "the page does not read the game by name")
    check("/api/heroquest" in src, "the web build has no route for the game")
    if BUNDLE.exists():
        page = (BUNDLE / "index.html").read_text(encoding="utf-8")
        check("loadJSON('heroquest')" in page,
              "the built page does not read the game")
        check("data/' + name" in page or "data/heroquest.json" in page,
              "the built page does not read data/ files")
        data = BUNDLE / "data/heroquest.json"
        check(data.exists(), "the built bundle has no heroquest.json")
        if data.exists():
            try:
                json.loads(data.read_text(encoding="utf-8"))
            except ValueError:
                check(False, "the bundled heroquest.json is not valid JSON")
        check(not re.search(r"fetch\(\s*['\"]/api/", page),
              "the built page still fetches a server endpoint")
        check("location.protocol !== 'file:'" in page,
              "the page does not know when there is no server to sync with")


def check_sync():
    sys.path.insert(0, str(ROOT))
    try:
        import webapp
    except Exception as err:            # noqa: BLE001 - report, never crash the suite
        check(False, f"the sync merge could not be imported: {err}")
        return
    merge = getattr(webapp, "merge_quest_events", None)
    if not check(callable(merge), "the server has no quest merge"):
        return
    a = {"id": "e1", "m": "r1m1", "s": 2, "at": 100}
    b = {"id": "e2", "m": "r1m2", "s": 3, "at": 200}
    check([x["id"] for x in merge([], [a, b])] == ["e1", "e2"],
          "the merge loses a fresh event")
    check([x["id"] for x in merge([a], [a, b])] == ["e1", "e2"],
          "the merge keeps a duplicate")
    check([x["id"] for x in merge([a, b], [])] == ["e1", "e2"],
          "the merge loses what the server already had")
    clamped = {e["id"]: e["s"] for e in
               merge([a], [{"id": "e3", "m": "r2m1", "s": 99, "at": 50}])}
    check(clamped.get("e3") == 3, "the merge does not clamp stars")
    check(list(clamped) == ["e3", "e1"], "the merge does not keep the log in time order")
    check(merge([a], [{"id": "e1", "m": "r1m1", "s": 3, "at": 999}])[0]["s"] == 2,
          "a resent id overwrote the stored event")
    check(merge([a], [{"id": "", "m": "r1m1", "s": 1}]) == [a],
          "the merge accepted an event without an id")
    check(len(merge([], [{"id": f"e{i}", "m": "r1m1", "s": 1, "at": i} for i in range(600)])) == 500,
          "the merge does not cap the log")

    src = WEBAPP.read_text(encoding="utf-8")
    check("def do_POST(self):" in src and "/api/quest/sync" in src,
          "the server has no sync endpoint")
    check("re.fullmatch(r\"[A-Za-z0-9_-]{8,64}\", key)" in src,
          "the sync key is not validated")
    check("tmp.replace(path)" in src, "the sync write is not atomic")
    check("131072" in src, "the sync body has no size limit")


def main():
    doc = json.loads(QUEST.read_text(encoding="utf-8"))
    kids = json.loads(KIDS.read_text(encoding="utf-8"))
    src = WEBAPP.read_text(encoding="utf-8")
    build = BUILD.read_text(encoding="utf-8")

    print("the content")
    check_content(doc, kids)

    print("\nthe page")
    check_page(src)

    print("\noffline and the apk")
    check_offline(src, build)

    print("\nsync")
    check_sync()

    if problems:
        print()
        for p in problems[:40]:
            print("FAIL  " + p)
        if len(problems) > 40:
            print(f"      ... and {len(problems) - 40} more")
        print(f"\nFAIL  {len(problems)} problem(s) in hero quest")
        return 1

    print(f"\nPASS  {stats['missions']} missions in 6 ranks with "
          f"{stats['authored']} written challenges and the rest drawn from the "
          "kids bank; the game is placed from the level check, opens only for a "
          "child, ships inside the offline bundle and syncs by event id")
    return 0


if __name__ == "__main__":
    sys.exit(main())
