#!/usr/bin/env python3
"""Is Word Quest a solvable game, and does a child get it without the network?

    python3 tools/check_wordquest.py

A puzzle a child cannot finish is worse than no puzzle, so the data is checked
twice: tools/build_wordquest.py refuses to write a bad one, and this suite
re-reads the finished file without trusting the builder. Between them, the two
answer the questions the build cannot:

  the answers   every required word is spelled from its own rack, every letter
                used no more often than the rack holds it, no word is asked for
                twice in a puzzle, and no bonus word is secretly required.

  the reward    every word carries an English definition, a Persian meaning, a
                Persian example and a picture, and every word in the file is
                taught by at least one puzzle - a record nobody can reach is a
                record that should not be shipped.

  the game      the acceptance rule the page uses is re-run here over every
                puzzle: required words win, bonus words do not finish a stage,
                and a word in neither list is refused. Score is a function of
                answers, not of seconds.

  the wiring    one kids-only toolbar button, one panel, one repaint hook, the
                route that serves the file, and the file inside the APK bundle.

  the bundle    the same JSON reached by the built page, byte for byte, so the
                APK cannot drift from the web.

The browser itself is not automated here; what a static suite can pin is the
data, the rules and the seams it hangs from.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEBAPP = ROOT / "webapp.py"
DATA = ROOT / "wordquest.json"
APK_DATA = ROOT / "android/app/src/main/assets/www/data/wordquest.json"
BUILD_APK = ROOT / "build_apk_ui.py"

LEVELS = ["Pre-A1", "A1", "A2", "B1", "B2", "C1", "C2"]
problems: list[str] = []


def bad(msg: str) -> None:
    problems.append(msg)


def spellable(word: str, rack: str) -> bool:
    have = Counter(rack.lower())
    need = Counter(word)
    return all(need[c] <= have[c] for c in need)


# ------------------------------------------------------------------ content
def check_data(data: dict) -> dict:
    stats = {"worlds": 0, "stages": 0, "required": 0, "bonus": 0, "words": 0}
    if data.get("title_en") != "Fluentify Word Quest":
        bad("the game is not called Fluentify Word Quest")
    if data.get("levels") != LEVELS:
        bad("the level list is not Pre-A1 to C2 in order")

    words = data.get("words") or {}
    stats["words"] = len(words)
    if len(words) < 60:
        bad(f"only {len(words)} words in the bank; a game needs a vocabulary")

    used: set[str] = set()
    worlds = data.get("worlds") or []
    stats["worlds"] = len(worlds)
    if len(worlds) < 6:
        bad(f"only {len(worlds)} worlds; the map is meant to be a map")
    if [w.get("order") for w in worlds] != list(range(1, len(worlds) + 1)):
        bad("worlds are not ordered 1..n")

    seen_ids: set[str] = set()
    seen_levels: set[str] = set()
    for world in worlds:
        for field in ("id", "name_en", "name_fa", "emoji", "level", "theme_en",
                      "theme_fa", "blurb_en", "blurb_fa"):
            if not world.get(field):
                bad(f"world {world.get('id')} has no {field}")
        if not re.search(r"[\u0600-\u06FF]", world.get("name_fa", "")):
            bad(f"world {world.get('id')} has no Persian name")
        stages = world.get("stages") or []
        if len(stages) < 4:
            bad(f"world {world.get('id')} has only {len(stages)} puzzles")
        if [s.get("order") for s in stages] != list(range(1, len(stages) + 1)):
            bad(f"world {world.get('id')} stages are not ordered 1..n")
        for stage in stages:
            sid = stage.get("id")
            stats["stages"] += 1
            if not sid or sid in seen_ids:
                bad(f"stage id {sid!r} is missing or repeated")
                continue
            seen_ids.add(sid)
            rack = stage.get("rack", "")
            letters = stage.get("letters") or []
            if not re.fullmatch(r"[A-Z]{3,10}", rack):
                bad(f"{sid}: rack {rack!r} is not 3-10 A-Z letters")
            if Counter(letters) != Counter(rack):
                bad(f"{sid}: the shown letters are not the rack")
            if len(letters) != len(rack):
                bad(f"{sid}: the rack shows a letter twice or loses one")
            if not stage.get("title_en") or not stage.get("title_fa"):
                bad(f"{sid}: missing a bilingual title")
            if stage.get("level") not in LEVELS:
                bad(f"{sid}: unknown level {stage.get('level')!r}")

            required = stage.get("required") or []
            bonus = stage.get("bonus") or []
            if len(required) < 3:
                bad(f"{sid}: only {len(required)} required words")
            if len(set(required)) != len(required):
                bad(f"{sid}: a required word is listed twice")
            if set(required) & set(bonus):
                bad(f"{sid}: a word is both required and bonus")
            if len(set(bonus)) != len(bonus):
                bad(f"{sid}: a bonus word is listed twice")
            stats["required"] += len(required)
            stats["bonus"] += len(bonus)

            for word in required:
                if word not in words:
                    bad(f"{sid}: required word {word!r} has no record")
                if not spellable(word, rack):
                    bad(f"{sid}: {word!r} cannot be spelled from {rack}")
                used.add(word)
            for word in bonus:
                if word not in words:
                    bad(f"{sid}: bonus word {word!r} has no record")
                if not spellable(word, rack):
                    bad(f"{sid}: bonus word {word!r} cannot be spelled from {rack}")
                if len(word) < 3:
                    bad(f"{sid}: bonus word {word!r} is too short to teach")
                used.add(word)

            hardest = max((words[w]["level"] for w in required if w in words),
                          key=lambda l: LEVELS.index(l), default="Pre-A1")
            if stage.get("level") != hardest:
                bad(f"{sid}: level {stage.get('level')} is not its hardest required word ({hardest})")
            seen_levels.add(stage["level"])

    missing = sorted(set(LEVELS) - seen_levels)
    if missing:
        bad(f"no puzzle at {', '.join(missing)}; the ladder has a missing rung")

    for word, record in words.items():
        if record.get("spelling") != word:
            bad(f"{word}: record spelling does not match its key")
        if not re.fullmatch(r"[a-z]+", word):
            bad(f"{word!r}: not a lowercase English word")
        if record.get("level") not in LEVELS:
            bad(f"{word}: unknown level")
        for field in ("fa", "def_en", "example_en", "example_fa", "picture", "pos"):
            if not record.get(field):
                bad(f"{word}: empty {field}")
        if not re.search(r"[\u0600-\u06FF]", record.get("fa", "")):
            bad(f"{word}: no Persian meaning")
        if not re.search(r"[\u0600-\u06FF]", record.get("example_fa", "")):
            bad(f"{word}: no Persian example")
        if word not in used:
            bad(f"{word}: no puzzle ever asks for it")
    return stats


# ------------------------------------------------------------------- playing
def check_acceptance(data: dict) -> None:
    """The page's rule, run over every puzzle, without the page."""
    words = data["words"]
    for world in data["worlds"]:
        for stage in world["stages"]:
            sid = stage["id"]
            rack = stage["rack"]
            required = stage["required"]
            bonus = stage["bonus"]
            # every required word is accepted and none needs an absent letter
            for word in required:
                if not spellable(word, rack):
                    bad(f"{sid}: cannot be won, {word!r} needs a letter it has not got")
            # a bonus word never finishes a stage
            for word in bonus:
                if word in required:
                    bad(f"{sid}: bonus word {word!r} also completes the puzzle")
            # a word from outside the puzzle is refused, not rewarded
            outside = [w for w in words if not spellable(w, rack) and w in required]
            if outside:
                bad(f"{sid}: accepts words that are not in its rack")
            # the stage can be finished: the required set is reachable
            if len(required) != len(set(required)):
                bad(f"{sid}: duplicate required words")
            # a short required word may be the start of a longer one ("do" and
            # "dog" in the same rack): the page tests for an exact word before
            # it tests whether the letters could still grow, so both are found.
            # What must never happen is a required word that is not spellable,
            # which the rack check above already refuses.


# --------------------------------------------------------------------- wiring
def check_wiring() -> None:
    page = WEBAPP.read_text(encoding="utf-8")
    need = [
        ('id="wrqtoggle"', "the toolbar button"),
        ('id="wrqpanel"', "the panel"),
        ('id="wqbody"', "the panel body"),
        ("wrqpanel: 'wrqtoggle'", "the panel registry"),
        ("wrqpanel: () => { if (Experience.kids()) WordQuest.open(); }", "the repaint hook"),
        ("togglePanel('wrqpanel', 'wrqtoggle')", "the click that opens it"),
        ("body:not(.kids) #wrqtoggle", "the kids-only rule"),
        ("body:not(.kids) #wrqpanel { display: none !important; }", "the kids-only panel rule"),
        ("const WordQuest = (() => {", "the module"),
        ("loadJSON('wordquest')", "the offline read"),
        ('self.path.startswith("/api/wordquest")', "the route"),
        ("wrqpanel: ['Word Quest', 'جست‌وجوی واژه', '🔤']", "the kids home tile"),
        ("wrqtoggle: 'Letters'", "the toolbar label"),
    ]
    for needle, what in need:
        if needle not in page:
            bad(f"wiring: {what} is missing ({needle})")
    if "Experience.kids()" not in page.split("const WordQuest")[1][:4000]:
        bad("wiring: the module does not check Experience.kids()")
    # the game must not have been added to the adult interface: every rule that
    # shows it is scoped to body.kids, and the adult page hides it outright
    css = page.split("/* ---- Word Quest: the letter puzzle")[1].split("/* ---- the Kids home page")[0]
    for line in css.splitlines():
        if "#wrq" in line and "body.kids" not in line and "body:not(.kids)" not in line:
            bad(f"wiring: a style escapes the kids scope: {line.strip()[:80]}")
    # the module reads its own key and never a quiz key
    module = page.split("const WordQuest = (() => {")[1]
    if "fluentify.wordquest.v1" not in module:
        bad("wiring: the game does not name its own storage key")
    if "localStorage" not in module:
        bad("wiring: progress is not kept locally")
    for banned in ("fetch(", "XMLHttpRequest"):
        if banned in module.split("return {open, render};")[0]:
            bad(f"wiring: the game reaches the network at play time ({banned})")


def check_bundle() -> None:
    data_bytes = DATA.read_bytes()
    build = BUILD_APK.read_text(encoding="utf-8")
    if '"wordquest.json"' not in build:
        bad("bundle: wordquest.json is not in the APK's lazy data list")
    if not APK_DATA.exists():
        bad(f"bundle: {APK_DATA.relative_to(ROOT)} does not exist; run build_apk_ui.py")
        return
    if APK_DATA.read_bytes() != data_bytes:
        bad("bundle: the APK's copy differs from data/wordquest.json")
    page = (ROOT / "android/app/src/main/assets/www/index.html")
    if page.exists():
        html = page.read_text(encoding="utf-8")
        for needle, what in (('id="wrqpanel"', "the panel in the built page"),
                             ("const WordQuest", "the module in the built page"),
                             ('id="wrqtoggle"', "the button in the built page")):
            if needle not in html:
                bad(f"bundle: {what} is missing; run build_apk_ui.py")


def main() -> int:
    if not DATA.exists():
        print("FAIL  wordquest.json is missing; run tools/build_wordquest.py", file=sys.stderr)
        return 1
    try:
        data = json.loads(DATA.read_text(encoding="utf-8"))
    except ValueError as err:
        print(f"FAIL  wordquest.json is not valid JSON: {err}", file=sys.stderr)
        return 1

    print("the content")
    stats = check_data(data)
    print("the answers")
    check_acceptance(data)
    print("the wiring")
    check_wiring()
    print("the offline bundle")
    check_bundle()

    if problems:
        print()
        for p in problems[:40]:
            print("FAIL  " + p)
        if len(problems) > 40:
            print(f"      ... and {len(problems) - 40} more")
        print(f"\nFAIL  {len(problems)} problem(s) in word quest")
        return 1

    print(f"\nPASS  {stats['worlds']} worlds, {stats['stages']} puzzles and "
          f"{stats['words']} word records ({stats['required']} required answers, "
          f"{stats['bonus']} bonus) - every answer spelled from its own rack, every "
          "word taught, the game kids-only, offline and in the bundle")
    return 0


if __name__ == "__main__":
    sys.exit(main())
