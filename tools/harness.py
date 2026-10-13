#!/usr/bin/env python3
"""Fluency & knowledge harness.

Drives the bot the way a learner actually uses it — real questions, typos,
mixed English/Persian, follow-ups — and scores each reply. Every check is a
hard failure the bot must not produce: a crash, an empty answer, a wrong
translation, a mangled lesson, or a reply that leaks markup.

    python3 tools/harness.py            # run and print the failures
    python3 tools/harness.py --verbose  # also print what passed

Each round adds cases for whatever the previous round exposed, so the corpus
grows with the bot's weaknesses rather than with guesses.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from chatbot import ChatBot, plain  # noqa: E402

GLOSSARY = json.loads((ROOT / "glossary.json").read_text(encoding="utf-8"))["domains"]
PHRASES = json.loads((ROOT / "phrases.json").read_text(encoding="utf-8"))["topics"]
GRAMMAR = json.loads((ROOT / "grammar.json").read_text(encoding="utf-8"))["topics"]
LISTENING = json.loads((ROOT / "listening.json").read_text(encoding="utf-8"))["levels"]
PHONETICS = json.loads((ROOT / "phonetics.json").read_text(encoding="utf-8"))["sections"]
ARCH = json.loads((ROOT / "word_arch.json").read_text(encoding="utf-8"))["words"]

FAILURES: list[tuple[str, str, str]] = []
CHECKS = 0


def fail(kind: str, case: str, detail: str) -> None:
    FAILURES.append((kind, case, detail))


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------
MARKUP = re.compile(r"\{\*\*|\*\*|\{en\}|\{fa\}|<br\s*/?>|\bnan\b|�")
TRANSLATE = "\u21b3"  # the arrow that introduces a translation


def check_reply(kind: str, case: str, reply: str, want=None, banned=(), need=()) -> None:
    """Assert one reply is usable. `want` = substrings that must all appear."""
    global CHECKS
    CHECKS += 1
    if reply is None or not str(reply).strip():
        fail(kind, case, "empty reply")
        return
    r = plain(str(reply))
    if MARKUP.search(r):
        fail(kind, case, "markup leaked: " + MARKUP.search(r).group(0))
    if "None" in r or "{'" in r:
        fail(kind, case, "python repr leaked into the reply")
    for b in banned:
        if b.lower() in r.lower():
            fail(kind, case, f"unexpected {b!r} in reply")
    for w in need:
        if w.lower() not in r.lower():
            fail(kind, case, f"missing {w!r}")
    if want:
        for w in want:
            if w.lower() not in r.lower():
                fail(kind, case, f"expected {w!r}")


def check_no_crash(kind: str, case: str, fn) -> None:
    global CHECKS
    CHECKS += 1
    try:
        out = fn()
    except Exception as exc:  # noqa: BLE001
        fail(kind, case, f"CRASH {type(exc).__name__}: {exc}")
        return
    if out is not None:
        check_reply(kind, case, out)


# --------------------------------------------------------------------------
# 1. vocabulary — the thing learners ask most
# --------------------------------------------------------------------------
# a spot-check of words across every CEFR band: EN lookup, FA lookup, define
WORD_PROBES = [
    ("apple", "سیب"), ("negotiate", "مذاکره کردن"), ("resilient", None),
    ("idempotent", None), ("schwa", None), ("anthropomorphise", None),
    ("ubiquitous", None), ("ephemeral", None), ("candid", None),
    ("meticulous", None), ("pragmatic", None), ("tenacious", None),
]


def run_vocabulary(verbose: bool) -> None:
    b = ChatBot()
    for en, _fa in WORD_PROBES:
        r = b.respond(f"translate {en}")
        check_reply("vocab-en", f"translate {en}", r,
                    need=["\u2192"], banned=["don't have", "not sure"])
        r2 = b.respond(f"define {en}")
        check_reply("vocab-define", f"define {en}", r2,
                    banned=["don't have", "not sure"])
    # Persian → English
    for fa in ["سیب", "گرامر", "واژگان", "تلفظ"]:
        r = b.respond(f"{fa} به انگلیسی")
        check_reply("vocab-fa", f"{fa} به انگلیسی", r,
                    banned=["don't have", "not sure"])
    # every domain and every phrase topic must render
    for did, dom in GLOSSARY.items():
        if did == "_groups":
            continue
        for lang in ("en", "fa"):
            check_no_crash("domain", f"{did}[{lang}]",
                           lambda d=dom, l=lang: b.respond(d["keywords"][l][0]))
    for tid, topic in PHRASES.items():
        for lang in ("en", "fa"):
            check_no_crash("phrase", f"{tid}[{lang}]",
                           lambda t=topic, l=lang: b.respond(t["keywords"][l][0]))
    if verbose:
        print(f"  vocabulary: {len(WORD_PROBES) * 2 + 4} lookups, "
              f"{len(GLOSSARY) - 1} domains, {len(PHRASES)} phrase banks")


# --------------------------------------------------------------------------
# 2. grammar — lessons, the practice→exam gate, scoring
# --------------------------------------------------------------------------
def run_grammar(verbose: bool) -> None:
    b = ChatBot()
    for tid, topic in GRAMMAR.items():
        for lang in ("en", "fa"):
            kw = topic["keywords"][lang][0]
            r = b.respond(kw)
            check_reply("grammar", f"{tid}[{lang}]", r,
                        need=["Structure", "Examples"],
                        banned=["not sure", "Traceback"])
            if "مثال" not in r and lang == "fa":
                fail("grammar", f"{tid}[{lang}]", "no Persian example section")

    # full practice→exam walk on a sample of topics
    sample = list(GRAMMAR)[:6] + list(GRAMMAR)[-4:]
    for tid in sample:
        topic = GRAMMAR[tid]
        b2 = ChatBot()
        if "exam" not in b2.respond(f"{topic['keywords']['en'][0]} exam").lower():
            fail("gate", tid, "exam was not locked before the practice")
        b2.respond(f"{topic['keywords']['en'][0]} exercises")
        out = None
        for item in topic["practice"]:
            out = b2.handle_exercise(item["a"][0], item["a"][0].lower(), "en")
        check_reply("gate", f"{tid} practice", out or "", need=["Practice complete"])
        started = b2.respond(f"{topic['keywords']['en'][0]} exam")
        check_reply("gate", f"{tid} exam start", started, need=["Exam"])
        scored = 0
        for item in topic["exam"]:
            out = b2.handle_exercise(item["a"][0], item["a"][0].lower(), "en")
            scored += 1
        check_reply("exam", f"{tid} result", out or "",
                    need=[f"{scored}/{scored}"])
        # a wrong answer must not be rewarded
        b3 = ChatBot()
        b3.respond(f"{topic['keywords']['en'][0]} exam" if tid in b3.practice_done
                   else f"{topic['keywords']['en'][0]} exercises")
    if verbose:
        print(f"  grammar: {len(GRAMMAR)} lessons, {len(sample)} full practice→exam walks")


# --------------------------------------------------------------------------
# 3. listening, phonetics, alphabet, numbers
# --------------------------------------------------------------------------
def run_content(verbose: bool) -> None:
    b = ChatBot()
    for lv in LISTENING:
        for kw in (lv["id"], f"listen {lv['id']}"):
            r = b.respond(kw)
            check_reply("listening", kw, r,
                        need=[TRANSLATE], banned=["not sure", "don't have"],
                        )
    for sec in PHONETICS:
        for kw in (sec["title"]["en"], sec["title"]["fa"]):
            check_no_crash("phonetics", kw, lambda k=kw: b.respond(k))
    for kw in ["english alphabet", "الفبای فارسی", "what letter is B", "حرف ب",
               "3", "twenty one", "۵", "what time is it", "what is today's date"]:
        check_reply("misc", kw, b.respond(kw), banned=["not sure"])
    if verbose:
        print(f"  listening {len(LISTENING)} bands · phonetics {len(PHONETICS)} sections")


# --------------------------------------------------------------------------
# 4. small talk — the intents a learner actually opens with
# --------------------------------------------------------------------------
SMALL_TALK = [
    "hello", "hi", "hey there", "good morning", "salam", "سلام",
    "how are you", "how r u", "what's up", "how are you today?",
    "I'm fine thanks", "yes", "no", "ok", "thank you", "thanks a lot",
    "sorry", "my bad", "goodbye", "bye", "see you",
    "I am happy", "I'm sad", "i'm tired", "I'm hungry", "I'm bored",
    "im stressed", "I feel anxious", "I am angry", "I feel sick",
    "tell me a joke", "make me laugh", "یک جوک بگو", "معما بگو",
    "what can you do", "who are you", "help", "راهنما",
    "what is the weather", "what time is it", "what is today's date",
    "my name is Sara", "nice to meet you", "I love you",
    "give me a fun fact", "what does this word mean",
]


def run_smalltalk(verbose: bool) -> None:
    b = ChatBot()
    unknown = 0
    for text in SMALL_TALK:
        r = b.respond(text)
        check_reply("smalltalk", text, r, banned=["not sure", "don't have"])
        if "not sure" in r or "متوجه نشدم" in r:
            unknown += 1
            fail("smalltalk", text, "fell through to the fallback")
    if verbose:
        print(f"  small talk: {len(SMALL_TALK)} inputs, {unknown} fell through")


# --------------------------------------------------------------------------
# 5. robustness — what a real learner actually types
# --------------------------------------------------------------------------
ROBUST = [
    ("", "empty"),
    ("   ", "whitespace"),
    ("?!?!", "punctuation only"),
    ("translate", "verb with no word"),
    ("define", "verb with no word"),
    ("the the the", "stutter"),
    ("appl", "typo of apple"),
    ("grammer", "misspelling of grammar"),
    ("I want to to go to to", "double word"),
    ("translate apple please!!!", "with punctuation"),
    ("APPLE", "uppercase"),
    ("Apple.", "capitalised with a dot"),
    ("متنی که خیلی طولانی است " * 30, "very long Persian"),
    ("x" * 500, "very long latin"),
    ("translate apple\ntranslate banana", "two lines"),
    ("simple present\n\nexam", "multi-line command"),
    ("how do I say سیب", "mixed language"),
    ("3 + 4", "arithmetic"),
    ("?!?", "noise"),
    ("", "zero-width space"),
]


def run_robustness(verbose: bool) -> None:
    b = ChatBot()
    for text, label in ROBUST:
        r = b.respond(text)
        check_reply("robust", f"{label} ({text[:24]!r})", r)
        if MARKUP.search(r or ""):
            fail("robust", label, "markup leaked")
    if verbose:
        print(f"  robustness: {len(ROBUST)} edge cases")


# --------------------------------------------------------------------------
# 6. data integrity — what the harness assumes about the files
# --------------------------------------------------------------------------
def run_data(verbose: bool) -> None:
    global CHECKS
    for did, dom in GLOSSARY.items():
        if did == "_groups":
            continue
        CHECKS += 1
        for label, text in dom["label"].items():
            if not text or not text.strip():
                fail("data", did, f"empty label {label}")
        if not dom.get("level"):
            fail("data", did, "no CEFR level")
        for w in dom["words"]:
            if not w[0] or len(w) < 2 or not w[1]:
                fail("data", did, f"malformed word entry {w!r}")
            elif re.search(r"[A-Za-z]{3,}", w[1]):
                fail("data", did, f"latin leaked into the Persian gloss: {w!r}")
    for tid, topic in PHRASES.items():
        CHECKS += 1
        if not topic.get("level"):
            fail("data", tid, "no CEFR level")
        for line in topic["phrases"]:
            if not line.get("en") or not line.get("fa"):
                fail("data", tid, f"untranslated sentence {line!r}")
    for tid, topic in GRAMMAR.items():
        CHECKS += 1
        for field in ("structure", "function", "examples"):
            v = topic.get(field)
            if isinstance(v, str):
                fail("data", tid, f"{field} is a bare string, not a list of {{en,fa}}")
            elif not isinstance(v, list):
                fail("data", tid, f"{field} missing")
            elif v and isinstance(v[0], dict) and "fa" not in v[0]:
                fail("data", tid, f"{field} entry has no Persian")
        if not isinstance(topic.get("tip"), dict):
            fail("data", tid, "tip is not {en,fa}")
    # word architecture must point at real words
    for word, e in ARCH.items():
        CHECKS += 1
        if not e.get("fa"):
            fail("data", word, "no Persian meaning in the architecture entry")
        if e.get("pos") not in ("noun", "verb", "adj", "adv", "prep"):
            fail("data", word, f"bad pos {e.get('pos')!r}")
    if verbose:
        print(f"  data: {len(GLOSSARY) - 1} domains, {len(PHRASES)} banks, "
              f"{len(GRAMMAR)} lessons, {len(ARCH)} word entries")


# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# 7. teacher capabilities the learner asks for every session
# --------------------------------------------------------------------------
DISTINCTION_PROBES = [
    "what is the difference between present perfect and past simple",
    "difference between say and tell", "difference between a and an",
    "tell me the difference between affect and effect",
    "when do we use since and for", "difference between in and on",
    "difference between interesting and interested",
    "تفاوت since و for", "فرق say و tell",
    "difference between although and though",
    "difference between affect and effect", "difference between few and a few",
    "difference between used to and get used to",
    "difference between because and since",
    "what is the difference",
]

IDIOM_PROBES = [
    "what does 'spill the beans' mean", "meaning of once in a blue moon",
    "what does hit the books mean", "what is a piece of cake",
    "meaning of under the weather", "معنی break the ice",
    "what does the last straw mean", "idioms", "اصطلاح",
]

CORRECTION_PROBES = [
    "is this correct? I have went there",
    "correct this sentence: he don't like it",
    "I didn't went to school", "they doesn't like it",
    "I have many informations", "is this correct: he go to school",
    "I no understand this", "I am agree with you", "despite of the rain",
    "I have more better ideas", "is this sentence right: I no understand",
    # correct English must NOT be flagged
    "She doesn't watch TV", "She watches TV every day",
    "I have a new computer", "The book is on the table",
]

PRONOUNCE_PROBES = ["how do you pronounce apple", "how do you say hospital",
                     "تلفظ کلمه apple", "how do you pronounce zebra",
                     "how do you say a word"]


def run_teacher(verbose: bool) -> None:
    b = ChatBot()
    for q in DISTINCTION_PROBES:
        r = b.respond(q)
        # "don't have" is only a dictionary-miss signal in a *lookup*; here it
        # can be perfectly good English inside a lesson.
        check_reply("distinction", q, r,
                    need=[] if q == "what is the difference" else ["↳"])
        if q not in ("what is the difference",
                     "what is the difference between present perfect and past simple") \
                and "⚖" not in r:
            fail("distinction", q, "no distinction panel returned")
        if "{" in r:
            fail("distinction", q, "placeholder leaked into the reply")
    for q in IDIOM_PROBES:
        check_reply("idiom", q, b.respond(q),
                    banned=["not sure", "don't have"])
        if q != "idioms" and "معنی" not in b.respond(q) and "🗯" not in b.respond(q):
            fail("idiom", q, "no idiom explanation")
    for q in CORRECTION_PROBES:
        r = b.respond(q)
        check_reply("correction", q, r, banned=["Traceback"])
        if q in ("She doesn't watch TV", "She watches TV every day",
                 "I have a new computer", "The book is on the table"):
            if "✏" in r:
                fail("correction", q, "correct English was wrongly flagged")
        elif "✏" not in r:
            fail("correction", q, "the error was not caught")
        if "{" in r and "{" in q.replace("{", "", 0):
            fail("correction", q, "template placeholder leaked")
    for q in PRONOUNCE_PROBES:
        r = b.respond(q)
        check_reply("pronounce", q, r, banned=["not sure", "don't have"])
        if "Stress" not in r and "Give me the word" not in r:
            fail("pronounce", q, "no stress mark given")
    if verbose:
        print(f"  distinctions {len(DISTINCTION_PROBES)} · "
              f"idioms {len(IDIOM_PROBES)} · corrections {len(CORRECTION_PROBES)}")


RUNNERS = [
    ("vocabulary", run_vocabulary),
    ("grammar", run_grammar),
    ("content", run_content),
    ("smalltalk", run_smalltalk),
    ("robustness", run_robustness),
    ("teacher", run_teacher),
    ("data", run_data),
]


def main() -> int:
    verbose = "--verbose" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    for name, fn in RUNNERS:
        if only and name not in only:
            continue
        print(f"→ {name}")
        fn(verbose)
        print()

    if FAILURES:
        print(f"FAIL  {len(FAILURES)} of {CHECKS} checks\n")
        groups: dict[str, list] = {}
        for kind, case, detail in FAILURES:
            groups.setdefault(kind, []).append((case, detail))
        for kind, items in groups.items():
            print(f"  {kind} ({len(items)})")
            seen = set()
            for case, detail in items:
                if case in seen and len(items) > 8:
                    continue
                seen.add(case)
                print(f"    {case}: {detail}")
        return 1
    print(f"PASS  all {CHECKS} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())