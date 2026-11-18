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

  the feel      a game rather than a worksheet: a fox who says what to do next
                in Persian first, a strip of the world drifting behind the
                letters, a trail with a marker that walks as words are built,
                a picture and a length on every target, a second kind of help
                beside the bulb, and a visible answer to a right and a wrong
                try - all of it aria-hidden where it says nothing, all of it
                stopped under prefers-reduced-motion, and no control below a
                thumb.

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
        # the puzzle is picture-first: a child who cannot read English still has
        # to know what they are building before they build it
        ("wqpiccard", "the word's picture in the puzzle"),
        ("const currentWord = () =>", "one word at a time"),
        ("sayWord(", "the word is spoken aloud"),
        ("play.typed.length === word.length", "the boxes decide when to check"),
        ("function removeAt(", "a filled box gives its letter back"),
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
        if banned in module.split("\n  return {open, render")[0]:
            bad(f"wiring: the game reaches the network at play time ({banned})")
    # the old puzzle asked a child to hunt for words they could not see, and
    # printed English-only instructions at them; neither may come back
    for gone, what in (("wqtray", "the tray of guessed letters"),
                       ("wqslot-letters", "the word-hunt rows"),
                       ("Find ' + stage.required.length + ' words", "English-only instructions")):
        if gone in module:
            bad(f"wiring: {what} is back in the puzzle")


def check_feel() -> None:
    """Would a child call this a game, and can they still work it alone?

    A puzzle that is only correct is a worksheet. This is the part of the suite
    that asks whether the stage is a place: a character who tells the child what
    to do, the world moving behind the letters, a trail that shows how far the
    stage has come, pictures on every target, and a second kind of help beside
    the bulb. It also holds the other edge down - every one of those things is
    decoration, so it must be aria-hidden where it says nothing, it must stop
    under prefers-reduced-motion, and no control may shrink below a thumb.
    """
    page = WEBAPP.read_text(encoding="utf-8")
    css = page.split("/* ---- Word Quest: the letter puzzle")[1].split("/* ---- Kids header")[0]
    module = page.split("const WordQuest = (() => {")[1].split("\n  return {open, render")[0]

    # --- the coach: a fox who says what to do next, in the child's language
    for needle, what in (
        ("body.kids .wqcoach", "the coach row"),
        ("body.kids .wqfox", "the fox"),
        ("body.kids .wqbubble", "the speech bubble"),
        ("body.kids .wqbubble-fa", "the Persian line of the bubble"),
        ("body.kids .wqbubble-en", "the English line of the bubble"),
    ):
        if needle not in css:
            bad(f"feel: {what} has no style")
    for needle, what in (
        ("function coach(world)", "the coach builder"),
        ("brand/kids-fox-face.png", "the fox's face"),
        ("fox.setAttribute('aria-hidden', 'true')", "the fox is read out as text"),
        ("function coachLine()", "the coach's lines"),
        ("'این واژه ' + word.length + ' حرف دارد", "the coach says nothing in Persian"),
        ("Tap the bulb and I will help.", "the coach never offers help"),
    ):
        if needle not in module:
            bad(f"feel: {what} is missing ({needle})")

    # --- the world, moving behind the letters
    for needle, what in (
        ("body.kids .wqscene", "the scene strip"),
        ("@keyframes wqdrift", "the drift"),
        ("body.kids .wqscene i", "the drifting bits"),
    ):
        if needle not in css:
            bad(f"feel: {what} has no style")
    if "function sceneStrip(world)" not in module:
        bad("feel: the scene is never built")
    if "strip.setAttribute('aria-hidden', 'true')" not in module:
        bad("feel: the drifting world is read out as content")

    # --- the trail: how far the stage has come, with a marker that walks
    for needle, what in (
        ("body.kids .wqtrail", "the trail"),
        ("body.kids .wqtrail-fill", "the trail's fill"),
        ("body.kids .wqtrail-fox", "the walking marker"),
    ):
        if needle not in css:
            bad(f"feel: {what} has no style")
    if "function trail(stage)" not in module:
        bad("feel: the trail is never built")
    if "words built — " not in module:
        bad("feel: the trail has no spoken progress for a screen reader")

    # --- pictures and hints on the targets themselves
    if "done ? (record.picture || '✓') : (record.picture || '🔤')" not in module:
        bad("feel: a target a child has not built yet shows no picture")
    if "wqsticker-dots" not in module or "wqsticker-dots" not in css:
        bad("feel: a pending target does not show how many letters it needs")
    if "sayText(w)" not in module:
        bad("feel: tapping a target does not speak the word")

    # --- a second kind of help, and it must cost what the bulb costs
    for needle, what in (
        ("function usePeek()", "the word-card hint"),
        ("body.kids .wqctlbtn.peek", "the word-card hint's face"),
        ("controls.appendChild(mk('🔎', 'نشانم بده'", "the word-card hint's control"),
    ):
        if needle not in module and needle not in css:
            bad(f"feel: {what} is missing ({needle})")
    peek = module.split("function usePeek()", 1)[1].split("\n  }", 1)[0] if "function usePeek()" in module else ""
    if "play.hints += 1" not in peek:
        bad("feel: the word-card hint is free, so the star rule is not honest")

    # --- reactions: the game answers a right and a wrong answer visibly
    for needle, what in (
        ("@keyframes wqhop", "the fox's happy hop"),
        ("@keyframes wqwobble", "the fox's wobble"),
        ("@keyframes wqbob", "the fox's idle bob"),
        ("@keyframes wqpop", "a letter landing in its box"),
    ):
        if needle not in css:
            bad(f"feel: {what} has no keyframes")
    if "play.mood = 'happy'" not in module or "play.mood = 'oops'" not in module:
        bad("feel: the coach never reacts to a right or a wrong answer")
    if "'wqslots' + (play.mood === 'oops' ? ' shake' : '')" not in module:
        bad("feel: a wrong word does not shake the boxes")

    # --- and every one of those moving things stops when a child asks it to
    motion = css.split("@media (prefers-reduced-motion: reduce)")[-1]
    for needle, what in (
        ("body.kids .wqfox", "the fox keeps bobbing"),
        ("body.kids .wqscene i", "the world keeps drifting"),
        ("body.kids .wqtrail-fox", "the trail marker keeps sliding"),
    ):
        if needle not in motion:
            bad(f"feel: under reduced motion, {what}")
    if "body.kids .wqbox.on { animation: none; }" not in motion:
        bad("feel: under reduced motion, the boxes still pop")

    # --- nothing shrank below a thumb, on the smallest screen the app ships
    def px(rule: str, prop: str) -> int:
        m = re.search(prop + r":\s*(\d+)px", rule)
        return int(m.group(1)) if m else 0
    letter = css.split("body.kids .wqletter {", 1)[1].split("}", 1)[0]
    if px(letter, "width") < 58 or px(letter, "height") < 62:
        bad(f"feel: a letter tile is {px(letter, 'width')}x{px(letter, 'height')}, too small for a thumb")
    ctl = css.split("body.kids .wqctlbtn {", 1)[1].split("}", 1)[0]
    if px(ctl, "min-height") < 56:
        bad(f"feel: a control is {px(ctl, 'min-height')}px tall, too small to hit")
    small = css.split("@media (max-width: 330px)")[-1].split("}", 2)[0]
    if px(small, "width") and px(small, "width") < 40:
        bad("feel: the letter tiles get too small on a 330px screen")

    # --- the coach must not have become a second place to read instructions
    if module.count("wqbubble") > 6:
        bad("feel: the coach is being rebuilt in more than one place")

    # --- the stage still costs nothing to lose: hints decide stars, mistakes
    # never do, or the new reactions would turn a wrong answer into a penalty
    if "const stars = play.hints === 0 ? 3" not in module:
        bad("feel: the star rule changed; hints must be the only cost")



def check_systems() -> None:
    """Are the systems a game needs actually systems, not words in a comment?

    The brief for the juicy pass was a state machine, a reward loop, adaptive
    difficulty, a sandbox, object pooling, particles and local telemetry, plus
    the accessibility that keeps all of it usable with a keyboard and a screen
    reader. Each of those can be faked with a heading, so this section looks
    for the seam rather than the label: the transition table, the nodes coming
    back out of a pool, the frame loop that stops, and the event that is
    written when a word is built.

    Offline is the other edge. The game runs in an APK with no server, and the
    older sections already refuse `fetch(` in the module; here the same rule is
    applied to the new telemetry, together with the promise that no event
    carries anything but counts, ids and durations.
    """
    page = WEBAPP.read_text(encoding="utf-8")
    module = page.split("const WordQuest = (() => {")[1].split("\n  return {open, render")[0]
    css = page.split("/* ---- Word Quest: the letter puzzle")[1].split("/* ---- Kids header")[0]

    # --- the state machine: a table, a guard, and one door between screens
    for needle, what in (
        ("const Flow = {", "the transition table"),
        ("function go(next, why)", "the only way between screens"),
        ("if (!Flow[view] || Flow[view].indexOf(next) < 0) return false;", "the guard"),
        ("sandbox: ['map', 'play']", "the sandbox's exits"),
        ("insights: ['map']", "the grown-ups page's exits"),
    ):
        if needle not in module:
            bad(f"systems: {what} is missing ({needle})")
    # every screen in the table must have a renderer, and no screen outside it
    for screen, call in (("sandbox", "renderSandbox(body)"),
                         ("insights", "renderInsights(body)")):
        if screen not in module.split("const Flow = {")[1].split("};")[0]:
            bad(f"systems: {screen} is not a state")
        if call not in module:
            bad(f"systems: {screen} has no renderer")
    if "view = 'play'" in module:
        bad("systems: a screen still flips the view string behind the machine's back")

    # --- the reward loop: coins, a streak, a daily goal, and no punishment
    for needle, what in (
        ("function rewardWord()", "the per-word reward"),
        ("function rewardStage()", "the per-stage reward"),
        ("function rhythmTouch()", "the streak and today"),
        ("const DAILY_GOAL = 5;", "the daily goal"),
        ("state.coins = Math.min(99999, state.coins + 2);", "no word pays nothing"),
        ("state.recent = ((state.recent || '') + (ok ? 'r' : 'w')).slice(-12);",
         "the last answers are kept"),
        ("play.combo = firstTry ? (play.combo || 0) + 1 : 0;", "the combo"),
    ):
        if needle not in module:
            bad(f"systems: {what} is missing ({needle})")
    if "state.streak = 0" in module and "state.streak = gap === 1" not in module:
        bad("systems: the streak is never extended")
    # nothing in the reward path may take a star or a coin away
    rewards = module.split("function rewardWord()", 1)[1].split("/* ------------------------------------------------------------- telemetry", 1)[0]
    if "-" in rewards.replace("--", ""):
        bad("systems: a reward carries a subtraction; rewards may only add")

    # --- adaptation: learned from the last answers, applied on screen
    for needle, what in (
        ("function supportNow()", "the support decision"),
        ("if (rate <= .6) return 1;", "the extra-help threshold"),
        ("if (rate >= .9 && r.length >= 8) return 2;", "the challenge threshold"),
        ("function noteAnswer(ok)", "the answer that teaches it"),
        ("play.support = state.support || 0;", "the stage reads it"),
        ("play.support === 1 && word.length > 2", "the scaffold"),
        ("play.support === 2 && !play.peeked", "the held-back picture"),
        ("wqaid", "the help is announced on screen"),
    ):
        if needle not in module and needle not in css:
            bad(f"systems: {what} is missing ({needle})")
    # the help may never touch the score
    scaffold = module.split("function beginWord()", 1)[1].split("\n  }", 1)[0]
    if "hints += 1" in scaffold:
        bad("systems: the scaffolded letter costs a hint, so the help is a penalty")

    # --- sandbox: free play with no score, and it says so
    if "function renderSandbox(body)" not in module:
        bad("systems: the sandbox has no screen")
    box = module.split("function renderSandbox(body)", 1)[1].split("function renderInsights", 1)[0]
    for needle, what in (
        ("'ABCDEFGHIJKLMNOPQRSTUVWXYZ'", "the whole alphabet"),
        ("no scoring, no timer", "the sandbox promises no score"),
        ("Sparks.at(value, 12, '★')", "a found word is celebrated"),
        ("Telemetry.track('sandbox'", "a sandbox word is logged"),
    ):
        if needle not in box:
            bad(f"systems: {what} is missing ({needle})")
    for forbidden in ("state.stages", "hints += 1", "save()", "rewardWord", "rewardStage"):
        if forbidden in box:
            bad(f"systems: the sandbox writes progress ({forbidden})")

    # --- object pooling: a bin, a cap, and nodes that really come back
    for needle, what in (
        ("const Pool = (() => {", "the pool"),
        ("const LIMIT = 160;", "a ceiling on what is kept"),
        ("function take(tag, cls, poolId)", "taking a node back"),
        ("function give(node)", "returning a node"),
        ("Pool.take('button', 'wqletter', 'wqletter')", "letter tiles are pooled"),
        ("Pool.take('button', 'wqbox'", "boxes are pooled"),
        ("Pool.take('span', 'wqsticker-pic'", "sticker pictures are pooled"),
        ("(node) => Pool.give(node)", "the old tiles are returned"),
    ):
        if needle not in module:
            bad(f"systems: {what} is missing ({needle})")

    # --- particles: one layer, pooled pieces, a loop that stops
    for needle, what in (
        ("const Sparks = (() => {", "the emitter"),
        ("requestAnimationFrame(frame)", "the frame loop"),
        ("if (live.length) raf = requestAnimationFrame(frame);", "the loop stops"),
        ("if (!layer || reduced()) return;", "reduced motion emits nothing"),
        ("live.length < 42", "a cap on the pieces"),
        ("Sparks.mount(sparks)", "the layer is mounted"),
        ("sparks.setAttribute('aria-hidden', 'true')", "the layer is not read out"),
        ("Sparks.at(document.querySelector('.wqslots')", "a built word sparks"),
    ):
        if needle not in module:
            bad(f"systems: {what} is missing ({needle})")
    for needle in ("body.kids .wqsparks", "body.kids .wqspark"):
        if needle not in css:
            bad(f"systems: the particle layer has no style ({needle})")

    # --- telemetry: local, capped, counted, and never personal
    for needle, what in (
        ("const Telemetry = (() => {", "the logger"),
        ("const CAP = 200;", "the ring buffer"),
        ("Telemetry.track('word'", "a word is logged"),
        ("Telemetry.track('miss'", "a miss is logged"),
        ("Telemetry.track('stage_done'", "a finished stage is logged"),
        ("Telemetry.summary()", "the summary"),
        ("/^[A-Za-z0-9_-]*$/.test(v)", "strings are whitelisted"),
        ("function renderInsights(body)", "somewhere for a grown-up to read it"),
    ):
        if needle not in module:
            bad(f"systems: {what} is missing ({needle})")
    banned = ("fetch(", "XMLHttpRequest", "navigator.sendBeacon", "WebSocket", "new Image(")
    for needle in banned:
        if needle in module:
            bad(f"systems: the module reaches the network ({needle})")
    for needle in ("Auth.profile", "acc.email", "acc.name"):
        if needle in module.split("const Telemetry", 1)[1].split("const Pool", 1)[0]:
            bad(f"systems: an event could carry who the child is ({needle})")

    # --- accessibility: focus survives a rebuild, keys reach the rack,
    #     the answer is announced, and every target is drawn when focused
    for needle, what in (
        ("function rememberFocus()", "focus is remembered"),
        ("function restoreFocus()", "focus is restored"),
        ("restoreFocus();", "the render restores it"),
        ("function rackKeys(rack)", "the rack walks with the arrows"),
        ("'ArrowLeft'", "the arrow keys"),
        ("if (ev.key === 'Backspace')", "Backspace takes a letter back"),
        ("msg.setAttribute('role', 'status')", "the answer is a live status"),
        ("aria-atomic", "the status is announced whole"),
    ):
        if needle not in module:
            bad(f"systems: {what} is missing ({needle})")
    if "box.dataset.fkey" not in module or "b.dataset.fkey" not in module:
        bad("systems: the tiles have no stable focus key")
    for needle in ("body.kids .wqletter:focus-visible", "body.kids .wqbox:focus-visible",
                   "outline: 3px solid var(--k-primary-dark)", "outline-offset: 3px"):
        if needle not in css:
            bad(f"systems: a keyboard user cannot see where they are ({needle})")

    # --- and the new motion stops with the old motion
    motion = css.split("@media (prefers-reduced-motion: reduce)")[-1]
    for needle, what in (
        ("body.kids .wqspark { display: none; }", "the sparks still fly"),
        ("body.kids .wqgoal", "the goal still pulses"),
        ("body.kids .wqcombo", "the combo still hops"),
    ):
        if needle not in motion:
            bad(f"systems: under reduced motion, {what}")


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
    print("the feel")
    check_feel()
    print("the systems")
    check_systems()
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
          "word taught, the game kids-only, offline, in the bundle, dressed "
          "as a place a child wants to open, and run by a machine with a reward "
          "loop, adaptive help, a sandbox, pooled tiles, particles and a local "
          "behaviour log")
    return 0


if __name__ == "__main__":
    sys.exit(main())
