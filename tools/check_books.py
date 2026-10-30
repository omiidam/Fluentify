#!/usr/bin/env python3
"""The library: are the books sound, and is the panel wired to them?

books.json is content, so the first thing this suite does is read it the way a
learner would: a book has lessons, a lesson has words, and a word has a Persian
meaning, an English definition and sentences that use it. A word with no
example is a word the page can only show half of, and that is the kind of gap
that is invisible in a diff and obvious on the screen.

The second half is the wiring, because the panel is built from four separate
anchors - the tile in the header, the entry in Panels.TILES, the rule that
shows it, and the loader that fetches the catalogue - and any one of them going
missing leaves a button that does nothing or a panel that opens blank. That has
happened once here already, to the Review panel.

The third is the offline build. The APK has no server, so the panel reads
data/books.json out of its own assets; if the file is not copied into the
bundle the panel works on the web and fails on the phone.

    python3 tools/check_books.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "books.json"
PAGE = ROOT / "webapp.py"
BUILD = ROOT / "build_apk_ui.py"
BUILT = ROOT / "android/app/src/main/assets/www/index.html"
APK_DATA = ROOT / "android/app/src/main/assets/www/data/books.json"

# Persian letters, without the digits and punctuation that share the block: a
# meaning made of "۳" alone would not be a translation.
FA_LETTER = re.compile(r"[\u0621-\u064A\u066E-\u06D3\u06FA-\u06FF]")
LATIN = re.compile(r"[A-Za-z]")
WORD_SHAPE = re.compile(r"^[a-z][a-z'’\- ]*[a-z]$")

# The lessons this panel was built for, in the book's own order. A mistyped or
# missing headword passes every shape check and only a reader would notice, so
# the roster is pinned here and compared word by word.
PINNED_LESSONS = {
    1: [
        "abandon", "keen", "jealous", "tact", "oath", "vacant",
        "hardship", "gallant", "data", "unaccustomed", "bachelor", "qualify",
    ],
    2: [
        "dismal", "wager", "peril", "recline", "shriek", "sinister",
        "conceal", "inhabit", "frigid", "numb", "corpse", "tempt",
    ],
    3: [
        "annual", "blend", "minimum", "talent", "persuade", "visible",
        "typical", "devise", "essential", "wholesale", "scarce", "expensive",
    ],
    4: [
        "humid", "vanish", "dense", "predict", "villain", "vapor",
        "enormous", "theory", "utilize", "descend", "eliminate", "circulate",
    ],
    5: [
        "rural", "campus", "evade", "majority", "assemble", "tradition",
        "burden", "explore", "reform", "topic", "probe", "debate",
    ],
    6: [
        "thorough", "undoubtedly", "approach", "popular", "neglect",
        "employee", "defect", "deceive", "defraud", "detect", "client",
        "comprehensive",
    ],
    7: [
        "preserve", "gloomy", "consent", "unique", "resent", "denounce",
        "molest", "unforeseen", "torrent", "postpone", "capsule", "massive",
    ],
    8: [
        "weird", "valid", "obvious", "mediocre", "reluctant", "exaggerate",
        "security", "bulky", "amateur", "variety", "prominent", "survive",
    ],
    9: [
        "vicinity", "document", "century", "conclude", "undeniable", "resist",
        "lack", "ignore", "challenge", "miniature", "source", "rage",
    ],
    10: [
        "excel", "feminine", "mount", "compete", "dread", "masculine",
        "menace", "tendency", "underestimate", "victorious", "numerous",
        "flexible",
    ],
    11: [
        "evidence", "solitary", "vision", "frequent", "glimpse", "recent",
        "decade", "hesitate", "absurd", "conflict", "minority", "fiction",
    ],
    12: [
        "frank", "audible", "urgent", "urban", "ignite", "prohibit",
        "pollute", "decrease", "abolish", "population", "reveal", "adequate",
    ],
    13: [
        "commence", "migrate", "gleam", "famine", "vessel", "identify",
        "observant", "editor", "revive", "persist", "hazy", "journalist",
    ],
    14: [
        "unruly", "rival", "violent", "brutal", "opponent", "brawl",
        "duplicate", "vicious", "whirling", "underdog", "thrust",
        "bewildered",
    ],
    15: [
        "expand", "alter", "mature", "sacred", "revise", "pledge",
        "casual", "pursue", "unanimous", "fortunate", "pioneer",
        "innovative",
    ],
    16: [
        "grateful", "doubt", "slender", "cautious", "accurate", "penetrate",
        "pierce", "vast", "surpass", "capacity", "confident", "microscope",
    ],
    17: [
        "avoid", "aware", "quantity", "appeal", "wretched", "harsh",
        "misfortune", "opt", "wary", "keg", "nourish", "addict",
    ],
    18: [
        "reckless", "ingenious", "economical", "rave", "glance", "budget",
        "manipulate", "lubricate", "tragedy", "horrid", "pedestrian",
        "nimble",
    ],
    19: [
        "ban", "quota", "abundant", "absorbed", "appropriate", "estimate",
        "uneasy", "panic", "harvest", "calculated", "morsel", "threat",
    ],
    20: [
        "perish", "jagged", "captive", "crafty", "linger", "defiant",
        "ambush", "prosper", "emerge", "devour", "vigor", "fragile",
    ],
    21: [
        "transmit", "confirm", "verify", "detour", "weary", "merit",
        "plea", "collide", "relieve", "dilemma", "baffle", "anticipate",
    ],
    22: [
        "delinquent", "penalize", "vocation", "homicide", "acknowledge",
        "reject", "warden", "spouse", "unstable", "deprived", "justice",
        "beneficiary",
    ],
    23: [
        "embrace", "forbid", "proceed", "reptile", "partial", "logical",
        "rarely", "exhibit", "prior", "precaution", "valiant", "extract",
    ],
    24: [
        "authority", "encourage", "symbol", "vermin", "neutral", "consider",
        "fierce", "wail", "trifle", "detest", "scowl", "sneer",
    ],
    25: [
        "baggage", "calamity", "pauper", "collapse", "architect",
        "prosecute", "squander", "fugitive", "bigamy", "abroad", "envy",
        "matrimony",
    ],
    26: [
        "quench", "guide", "respond", "beckon", "venture", "compel",
        "awesome", "betray", "possible", "pacify", "utter", "awkward",
    ],
    27: [
        "feeble", "cease", "rash", "exhausted", "monarch", "disrupt",
        "thrifty", "rapidly", "severity", "unite", "despite", "miserly",
    ],
    28: [
        "undernourished", "disclose", "disaster", "outlaw", "excessive",
        "culprit", "promote", "illustrate", "insist", "censor", "juvenile",
        "bait",
    ],
    29: [
        "exempt", "repetition", "blunder", "comprehend", "toil", "maim",
        "commend", "final", "mourning", "vain", "subside", "daze",
    ],
    30: [
        "appoint", "mortal", "occupant", "depict", "site", "verse",
        "quarter", "quote", "novel", "attract", "morality", "roam",
    ],
    31: [
        "idle", "dispute", "commuter", "valor", "vein", "uneventful",
        "lunatic", "jest", "confine", "patriotic", "fertile", "idol",
    ],
    32: [
        "distress", "maximum", "flee", "torment", "loyalty", "apologize",
        "colleague", "signify", "refer", "diminish", "mythology",
        "vulnerable",
    ],
    33: [
        "mumble", "wad", "retain", "volunteer", "jolly", "prejudice",
        "hinder", "mute", "abuse", "shrill", "lecture", "witty",
    ],
    34: [
        "adolescent", "candidate", "radical", "spontaneous", "vaccinate",
        "utensil", "sensitive", "temperate", "untidy", "coeducational",
        "precede", "skim",
    ],
    35: [
        "lottery", "obtain", "cinema", "event", "soar", "stationary",
        "subsequent", "discard", "relate", "vague", "finance", "elevate",
    ],
    36: [
        "prompt", "soothe", "redeem", "refrain", "harmony", "hasty",
        "tempest", "scorch", "sympathetic", "resume", "illegal", "narcotic",
    ],
    37: [
        "dwindle", "heir", "deliberate", "surplus", "heed", "unify",
        "vandal", "abide", "drought", "summit", "traitor", "majestic",
    ],
    38: [
        "tumult", "swarm", "verdict", "biography", "recede", "charity",
        "kneel", "dejected", "tyrant", "drench", "wobble", "obedient",
    ],
    39: [
        "depart", "cancel", "placard", "contagious", "unearth", "customary",
        "scald", "transparent", "legible", "clergy", "debtor", "coincide",
    ],
    40: [
        "obesity", "epidemic", "chiropractor", "ventilated", "oral",
        "magnifying", "obstacle", "pension", "jeopardize", "negative",
        "municipal", "vital",
    ],
    41: [
        "wasp", "parole", "rehabilitate", "multitude", "potential",
        "upholstery", "indifference", "preoccupied", "vertical", "nominate",
        "morgue", "complacent",
    ],
    42: [
        "snub", "wrath", "ponder", "maintain", "endure", "expose", "legend",
        "ballot", "wharf", "resign", "amend", "drastic",
    ],
}

# The second book is organised by week; each week is four days of five words.
PINNED_1100 = {
    1: ["voracious", "indiscriminate", "eminent", "steeped", "replete",
        "abound", "technology", "prognosticate", "automaton", "matron",
        "paradox", "realm", "annals", "compound", "tinge",
        "badger", "implore", "drudgery", "interminable", "perceive"],
    2: ["laconic", "throng", "intrepid", "accost", "reticent",
        "furtive", "felon", "plethora", "hapless", "irate",
        "pretext", "fabricate", "adroit", "gesticulate", "vigilant",
        "avid", "cajole", "rudimentary", "enhance", "nuance"],
    3: ["loathe", "reprimand", "lackluster", "caustic", "wrest",
        "infamous", "jostle", "dupe", "incipient", "inadvertent",
        "ominous", "tremulous", "repudiate", "cessation", "bristle",
        "euphemism", "mundane", "incongruous", "condolence", "stipulate"],
    4: ["alacrity", "disdain", "belligerent", "intimidate", "feint",
        "pugnacious", "promulgate", "brash", "scoff", "belittle",
        "tangible", "laceration", "castigate", "sordid", "octogenarian",
        "solace", "aspirant", "dregs", "frenzy", "scurrilous"],
    5: ["rampant", "inane", "ethics", "concur", "clandestine",
        "flagrant", "admonish", "duress", "culprit", "inexorable",
        "egregious", "distraught", "duplicity", "acrimonious", "paucity",
        "elicit", "pernicious", "tolerate", "construe", "impunity"],
    6: ["affluent", "feasible", "discern", "sally", "consternation",
        "precocious", "perfunctory", "chagrin", "perverse", "deride",
        "disparage", "laudable", "fiasco", "masticate", "eschew",
        "quell", "voluble", "confidant", "obsolescence", "dubious"],
    7: ["implacable", "paroxysm", "reprehensible", "jurisdiction",
        "skirmish", "harass", "monolithic", "indigent", "arbitrary", "fray",
        "stymie", "effigy", "flout", "cognizant", "turbulent",
        "terminate", "forthwith", "exacerbate", "revert", "oust"],
}
POS = {"noun", "verb", "adjective", "adverb", "preposition", "conjunction",
       "pronoun", "determiner", "interjection", "phrase", "expression"}

problems: list[str] = []


def fail(what: str) -> None:
    problems.append(what)


def check(ok: bool, what: str) -> bool:
    if not ok:
        fail(what)
    return ok


def load() -> dict:
    try:
        return json.loads(BOOKS.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail("books.json is missing from the repository root")
    except json.JSONDecodeError as exc:
        fail(f"books.json does not parse: {exc}")
    return {}


def check_catalogue(data: dict) -> dict:
    """Every book, lesson and word, field by field."""
    books = data.get("books")
    if not check(isinstance(books, list) and books, "books.json has no books"):
        return {"books": 0, "lessons": 0, "words": 0}

    ids: set[str] = set()
    stats = {"books": 0, "lessons": 0, "words": 0}

    for book in books:
        bid = book.get("id") or "<no id>"
        stats["books"] += 1
        check(isinstance(book.get("id"), str)
              and re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", book["id"] or "") is not None,
              f"{bid}: the id is not a lowercase slug")
        check(bid not in ids, f"{bid}: the id is used twice")
        ids.add(bid)
        check(bool((book.get("title") or "").strip()),
              f"{bid}: no English title")
        check(bool(FA_LETTER.search(book.get("title_fa") or "")),
              f"{bid}: the Persian title has no Persian letters")
        check(bool(book.get("author")), f"{bid}: no author")
        check(bool(FA_LETTER.search(book.get("about_fa") or "")),
              f"{bid}: the Persian blurb has no Persian letters")

        lessons = book.get("lessons")
        if not check(isinstance(lessons, list) and lessons,
                     f"{bid}: has no lessons"):
            continue

        numbers = [l.get("n") for l in lessons]
        check(numbers == list(range(1, len(lessons) + 1)),
              f"{bid}: lessons are not numbered 1..{len(lessons)} in order "
              f"(got {numbers})")

        seen_words: dict[str, int] = {}
        for lesson in lessons:
            stats["lessons"] += 1
            where = f"{bid} lesson {lesson.get('n')}"
            check(bool((lesson.get("title") or "").strip()),
                  f"{where}: no title")
            check(bool(FA_LETTER.search(lesson.get("title_fa") or "")),
                  f"{where}: the Persian title has no Persian letters")

            words = lesson.get("words")
            if not check(isinstance(words, list) and words,
                         f"{where}: has no words"):
                continue

            for w in words:
                stats["words"] += 1
                headword = (w.get("word") or "")
                label = f"{where}: {headword or '<no word>'}"
                check(isinstance(headword, str)
                      and WORD_SHAPE.fullmatch(headword or "") is not None
                      and headword == headword.lower(),
                      f"{label}: the headword is not a plain lowercase English word")
                low = headword.lower()
                check(low not in seen_words,
                      f"{label}: the word appears twice in the book "
                      f"(also lesson {seen_words.get(low)})")
                seen_words[low] = lesson.get("n")

                check(bool(FA_LETTER.search(w.get("fa") or "")),
                      f"{label}: no Persian meaning")
                check(bool(LATIN.search(w.get("def_en") or ""))
                      and len((w.get("def_en") or "").split()) >= 3,
                      f"{label}: the English definition is missing or too short")
                check(w.get("pos") in POS,
                      f"{label}: part of speech is {w.get('pos')!r}, "
                      f"not one of {sorted(POS)}")
                ipa = w.get("ipa") or ""
                check(not ipa or ipa.startswith("/") and ipa.endswith("/"),
                      f"{label}: the IPA {ipa!r} is not wrapped in slashes")

                examples = w.get("examples")
                if not check(isinstance(examples, list) and len(examples) >= 2,
                             f"{label}: fewer than two example sentences"):
                    continue
                stem = low[:4]
                for sentence in examples:
                    check(isinstance(sentence, str) and len(sentence.split()) >= 4,
                          f"{label}: an example is too short ({sentence!r})")
                    check(str(sentence).rstrip()[-1:] in ".?!",
                          f"{label}: an example does not end in punctuation "
                          f"({sentence!r})")
                    # the sentence has to actually use the word, or it is an
                    # example of something else
                    check(stem in str(sentence).lower(),
                          f"{label}: the example does not contain the word "
                          f"({sentence!r})")
    return stats


def check_panel() -> None:
    """The four anchors that make the tile open a filled panel."""
    src = PAGE.read_text(encoding="utf-8")

    check('id="btoggle"' in src, "there is no Books tile in the header")
    check('id="bpanel"' in src, "there is no #bpanel in the markup")
    check('id="bbooks"' in src, "the panel has no slot to draw the shelf into")

    tiles = re.search(r"const TILES = \{(.*?)\};", src, re.S)
    check(bool(tiles) and "bpanel: 'btoggle'" in (tiles.group(1) if tiles else ""),
          "Panels.TILES does not map bpanel to btoggle, so the tile cannot "
          "open or close the panel")

    check("getElementById('btoggle').onclick" in src,
          "the Books tile has no click handler")
    check(re.search(r"bpanel: \(\) => Books\.load\(\)", src) is not None,
          "opening the panel does not load the catalogue")
    check(re.search(r"loadJSON\('books'\)", src) is not None,
          "the panel does not read books.json")

    # hidden until opened, and shown when it is - both halves, because a panel
    # in only one of the two lists is either always on screen or never is
    hidden = re.findall(r"#bpanel\b[^{]*\{\s*display:\s*none", src)
    check(bool(hidden), "no rule hides #bpanel, so it would sit in the flow")
    shown = re.search(r"#bpanel\.open[^{]*\{\s*display:\s*block", src)
    check(bool(shown), "#bpanel is hidden but nothing shows it when it opens")
    check(re.search(r"#bpanel \{\s*display:\s*none", src) is None
          or bool(shown), "#bpanel.open never overrides the hidden state")

    # direction is declared per element in this panel: the whole point of the
    # dictionary bug was that a mixed line is laid out by its first strong
    # character, so a Persian meaning must be its own rtl block
    check("fa.dir = 'rtl'" in src,
          "the Persian meaning is not marked rtl in the library")
    check("def.dir = 'ltr'" in src,
          "the English definition is not marked ltr in the library")

    # the route has to precede the chat fallback or every request becomes a reply
    route = src.find('"/api/books"')
    check(route != -1, "there is no /api/books route")
    if route != -1:
        chat = src.find('elif self.path.startswith("/api/chat")')
        check(chat == -1 or route < chat,
              "the /api/books route sits after the chat fallback")

    # typed navigation: "open books" / "کتاب‌ها را باز کن"
    check(re.search(r"\bbooks: \{\s*panel: 'bpanel'", src) is not None,
          "the library is not reachable by typing its name")


def check_offline() -> None:
    """The APK has no server, so the same file has to be in its assets."""
    build = BUILD.read_text(encoding="utf-8")
    check('"books.json"' in build,
          "build_apk_ui.py does not copy books.json into the offline bundle")
    check("LAZY_DATA" in build,
          "the offline build has no place for a lazily-read data file")

    if BUILT.exists():
        built = BUILT.read_text(encoding="utf-8")
        check("loadJSON('books')" in built,
              "the built page does not read books.json from its own assets")
        check('id="bpanel"' in built,
              "the built page has no Books panel")
        check("id=\"btoggle\"" in built,
              "the built page has no Books tile")
    if APK_DATA.exists() and BOOKS.exists():
        check(APK_DATA.read_bytes() == BOOKS.read_bytes(),
              "the APK's copy of books.json is out of date - "
              "run python3 build_apk_ui.py")


def main() -> int:
    data = load()
    stats = check_catalogue(data) if data else {"books": 0, "lessons": 0, "words": 0}

    other = next((b for b in data.get("books", []) if b.get("id") == "1100-words"),
                 None)
    if check(other is not None, "the 1100 book is not in the library"):
        lessons = {l.get("n"): l for l in other.get("lessons") or []}
        for number, roster in PINNED_1100.items():
            lesson = lessons.get(number)
            if not check(lesson is not None,
                         f"1100 week {number} is missing"):
                continue
            words = [w.get("word") for w in lesson.get("words") or []]
            check(words == roster,
                  f"1100 week {number} is not its words in order: {words}")
            days = {w.get("day") for w in lesson.get("words") or []}
            check(days and None not in days,
                  f"1100 week {number} has words with no day")

    book = next((b for b in data.get("books", []) if b.get("id") == "essential-504"), None)
    if check(book is not None, "the 504 book is not in the library"):
        lessons = {l.get("n"): l for l in book.get("lessons") or []}
        for number, roster in PINNED_LESSONS.items():
            lesson = lessons.get(number)
            if not check(lesson is not None,
                         f"504 lesson {number} is missing from the book"):
                continue
            words = [w.get("word") for w in lesson.get("words") or []]
            check(words == roster,
                  f"504 lesson {number} is not the book's twelve words in "
                  f"order: {words}")

    check_panel()
    check_offline()

    if problems:
        for p in problems[:40]:
            print("FAIL  " + p)
        if len(problems) > 40:
            print(f"      ... and {len(problems) - 40} more")
        print(f"\nFAIL  {len(problems)} problem(s) with the library")
        return 1

    print(f"PASS  {stats['books']} book(s), {stats['lessons']} lesson(s), "
          f"{stats['words']} words with a meaning, a definition and examples; "
          f"the panel is wired to them on the page and in the APK bundle")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
