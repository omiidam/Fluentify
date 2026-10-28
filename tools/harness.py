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
        # one revealed answer is not a clean run: the exam must stay shut
        b4 = ChatBot()
        b4.respond(f"{topic['keywords']['en'][0]} exercises")
        out = None
        for i, item in enumerate(topic["practice"]):
            if i == 0:
                out = b4.handle_exercise("show answer", "show answer", "en")
            else:
                out = b4.handle_exercise(item["a"][0], item["a"][0].lower(), "en")
        check_reply("gate", f"{tid} imperfect practice", out or "",
                    need=["Practice finished"])
        if "locked" not in b4.respond(f"{topic['keywords']['en'][0]} exam").lower():
            fail("gate", f"{tid} imperfect practice",
                 "the exam opened without a perfect run")

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
        # A complete **bold** span is rendered as bold by the page (a dictionary
        # answer bolds the headword), so only a *stray* marker - the "{**" or
        # half-open case this guards against - counts as a leak.
        if MARKUP.search(re.sub(r"\*\*[^*]+\*\*", "", r or "")):
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



# --------------------------------------------------------------------------
# 8. conversation — a learner thinks in sequences, not in commands
# --------------------------------------------------------------------------
FLOWS = [
    # (label, [turns], turn index that must NOT be the fallback)
    ("lesson-then-practice",
     ["simple present", "exercises", "show answer", "cancel", "exam"], None),
    ("lesson-then-examples",
     ["simple present", "examples", "show answer"], None),
    ("joke-then-another",
     ["tell me a joke", "another one", "another one"], None),
    ("listen-then-repeat",
     ["listen A1", "repeat that", "say that again"], None),
    ("phrases-then-repeat",
     ["daily routine", "repeat that"], None),
    # reading today's cards, from the drill, back out of it and on to the
    # expression: the drill must not swallow the questions about the day
    ("daily-then-practice",
     ["today's conversation", "practice today's conversation with me",
      "لغت امروز", "practice today's conversation with me", "stop",
      "today's expression"], None),
    ("fine-then-ask", ["I am fine", "what can I learn today"], None),
    ("no-open-target", ["exercises", "exam", "show answer", "examples"], None),
]

SECTION_PROBES = ["vocabulary", "words", "sentences", "phonetics", "grammar",
                  "listening", "واژگان", "جملات", "تلفظ", "گرامر"]


def run_conversation(verbose: bool) -> None:
    for label, turns, _ in FLOWS:
        b = ChatBot()
        for i, msg in enumerate(turns):
            r = b.respond(msg)
            check_reply("flow", f"{label}[{i}] {msg!r}", r)
            if "not sure I understand" in r or "متوجه نشدم" in r:
                fail("flow", f"{label}[{i}] {msg!r}",
                     "a follow-up command fell through to the fallback")
            if "don't have" in r and "glossary" in r:
                fail("flow", f"{label}[{i}] {msg!r}",
                     "a follow-up command was read as a dictionary lookup")
    for q in SECTION_PROBES:
        r = b.respond(q)
        check_reply("section", q, r, banned=["not sure", "don't have"])
        if len(r.splitlines()) < 2:
            fail("section", q, "no content listed")

    # the practice→exam gate must hold on the bare route too
    b = ChatBot()
    b.respond("future perfect")
    locked = b.respond("exam")
    if "locked" not in locked.lower() and "قفل" not in locked:
        fail("gate", "bare exam after a lesson", "the gate did not hold")
    b.respond("exercises")
    topic = b.grammar["future_perfect"]
    for item in topic["practice"]:
        b.handle_exercise(item["a"][0], item["a"][0].lower(), "en")
    opened = b.respond("exam")
    if "locked" in opened.lower():
        fail("gate", "bare exam after practice", "still locked after the practice")
    if verbose:
        print(f"  flows {len(FLOWS)} · section names {len(SECTION_PROBES)}")



# --------------------------------------------------------------------------
# 9. checker accuracy — it must catch errors AND stay quiet on correct English
# --------------------------------------------------------------------------
CORPUS = json.loads(
    (ROOT / "tools/harness_round4_corpus.json").read_text(encoding="utf-8"))


def run_accuracy(verbose: bool) -> None:
    b = ChatBot()
    false_pos, false_neg = [], []
    for sentence in CORPUS["correct"]:
        if "✏" in b.respond(sentence):
            false_pos.append(sentence)
    for sentence in CORPUS["wrong"]:
        r = b.respond(sentence)
        if "✏" not in r:
            false_neg.append(sentence)
        elif "Better:" not in r:
            fail("accuracy", sentence, "the error was flagged but not repaired")
    for sentence in false_pos:
        detail = next((l for l in b.respond(sentence).splitlines()
                       if l.startswith("   •")), "")
        fail("accuracy", repr(sentence), f"correct English was flagged — {detail.strip()}")
    for sentence in false_neg:
        fail("accuracy", repr(sentence), "the error was not caught")
    if verbose:
        print(f"  checker: {len(CORPUS['correct'])} correct sentences "
              f"({len(false_pos)} flagged wrongly), "
              f"{len(CORPUS['wrong'])} wrong ({len(false_neg)} missed)")
    # the checker must never be the reason a learner's own sentence is lost
    if false_pos or false_neg:
        print(f"  → {len(false_pos)} false positives, {len(false_neg)} false negatives")


# --------------------------------------------------------------------------
# 10. bilingual knowledge — the questions the new banks are meant to answer
# --------------------------------------------------------------------------
# (input, must appear, must not appear). The markers are the distinctive words
# of the entry rather than a whole sentence, so editing the copy does not break
# the check. The banned list carries the sharpest assertions here: the failure
# this suite was written for is a *wrong handler* answering confidently, not a
# plain refusal.
BILINGUAL_CASES = [
    # an idiom is never read as its literal parts
    ("what does break a leg mean", ["good luck", "موفق باشی"], ["شکستگی", "injury is"]),
    ("break a leg", ["موفق باشی"], ["متوجه نشدم"]),
    # contrastive grammar and the structures behind it
    ("difference between make and do", ["make"], ["not sure"]),
    ("difference between present perfect and past simple", ["perfect"], ["not sure"]),
    # a Persian question that names an English grammar term
    ("میشه present perfect رو برام explain کنی؟", ["Present Perfect"],
     ["✅", "correct English"]),
    ("قوانین inversion چیه", ["Inversion"], ["متوجه نشدم"]),
    # register: stored pairs and stored situations
    ("how do I say I have to go now formally", ["I have to go now"],
     ["not in the register list"]),
    ("how do i say please be quiet casually", ["Quiet down"],
     ["not in the register list"]),
    ("what do I say at a doctors appointment", ["doctor"], ["متوجه نشدم"]),
    ("what do I say in a job interview", ["job interview"], ["متوجه نشدم"]),
    # natural Persian requests: a lookup, a slow-down, a language switch
    ("اتوبوس رو بگو", ["bus"], ["واژه‌نامه"]),
    ("آهسته‌تر بگو", [], ["سطح شنیدن", "Listening levels"]),
    ("به فارسی بگو", ["فارسی"], ["واژه‌نامه من نیست"]),
    ("انگلیسی حرف بزن", ["English"], ["فارسی ادامه"]),
    # listening itself must keep working
    ("listen A1", ["A1"], []),
    ("B1 رو بگو", ["B1"], []),
    ("سطح b1 چیه", ["سطح"], ["سطح شنیدن", "Listening levels"]),
    # Persian typed without the zero-width non-joiner still matches
    ("از حرف زدن میترسم", [], ["متوجه نشدم"]),
    ("باید برم", [], ["متوجه نشدم"]),
    # the checker catches a real error and leaves correct English alone
    ("I did a mistake", ["made a mistake"], []),
    ("I made a mistake yesterday", [], ["✏"]),
    # a question *about* English is not an English sentence to mark
    ("میشه این رو توضیح بدی", [], ["درست است", "correct English"]),
]


def run_bilingual(verbose: bool) -> None:
    b = ChatBot()
    for text, need, banned in BILINGUAL_CASES:
        check_reply("bilingual", text, b.respond(text), need=need, banned=banned)
    if verbose:
        print(f"  bilingual: {len(BILINGUAL_CASES)} knowledge cases")


# --------------------------------------------------------------------------
# 10. daily english — one word, one expression, one conversation per day
#
# Pinned to a fixed date, so the answers are the same on every run: the whole
# feature is "the same three items all day", and a suite that used the real
# clock would be checking something else. These cases are about the *chat*;
# tools/check_daily.py owns the catalogue and the three engines.
DAILY_PROBES = [
    ("today's word", ["Word of the Day"], ["متوجه نشدم", "not sure"]),
    ("explain today's word", ["Word of the Day"], ["متوجه نشدم"]),
    ("today's expression", ["Expression of the Day"], ["متوجه نشدم"]),
    ("give me more examples of today's expression", ["Expression of the Day"], []),
    ("today's conversation", ["Conversation of the Day"], []),
    ("what's today's english", ["Today"], []),
    ("daily english", ["Today"], []),
    ("لغت امروز رو توضیح بده", ["لغت امروز"], ["متوجه نشدم"]),
    ("عبارت امروز", ["عبارت امروز"], []),
    ("با عبارت امروز چند جمله بساز", ["عبارت امروز"], []),
    ("مکالمه امروز", ["مکالمه امروز"], []),
    ("انگلیسی روزانه", ["انگلیسی"], ["متوجه نشدم"]),
]


# --------------------------------------------------------------------------
def run_daily(verbose: bool) -> None:
    day = "2026-05-04"
    b = ChatBot(today=day)
    picked = b.daily_selection()
    word, expr, conv = picked["words"], picked["expressions"], picked["conversations"]

    for text, need, banned in DAILY_PROBES:
        check_reply("daily", text, b.respond(text), need=need, banned=banned)

    # The chat has to name the very items the panel is showing - a daily
    # feature that answers with a different word is worse than none.
    for ask, entry, label in (("today's word", word, "word"),
                              ("today's expression", expr, "expression"),
                              ("today's conversation", conv, "conversation")):
        reply = b.respond(ask)
        marker = entry["en"] if "en" in entry else entry["topic"]["en"]
        if marker not in reply:
            fail("daily", ask, f"the reply never names today's {label} {marker!r}")
        if entry.get("fa") and entry["fa"] not in reply:
            fail("daily", ask, f"no Persian for today's {label}")

    # ...and so does the digest, all three at once
    digest = b.respond("today's english")
    for entry, label in ((word, "word"), (expr, "expression"), (conv, "conversation")):
        marker = entry["en"] if "en" in entry else entry["topic"]["en"]
        if marker not in digest:
            fail("daily", "digest", f"the digest omits today's {label} {marker!r}")

    # The same local date is the same three items, whichever process asks, and
    # the next day is a different three. Determinism is the whole promise.
    again = ChatBot(today=day).daily_selection()
    for kind in ("words", "expressions", "conversations"):
        if again[kind]["id"] != picked[kind]["id"]:
            fail("daily", kind, "a second process picked different items for "
                              "the same date")
    nxt = ChatBot(today="2026-05-05").daily_selection()
    same = [k for k in ("words", "expressions", "conversations")
            if nxt[k]["id"] == picked[k]["id"]]
    if same:
        fail("daily", "next day", f"{', '.join(same)} did not change overnight")

    # The drill walks the dialogue turn by turn...
    drill = ChatBot(today=day)
    opening = drill.respond("practice today's conversation with me")
    first = conv["turns"][0]
    if first["en"] not in opening:
        fail("daily", "practice", "the drill does not open with the first line")
    answer = drill.respond(conv["turns"][1]["en"])
    if "Well said" not in answer and "آفرین" not in answer:
        fail("daily", "practice", "saying the expected line back was not accepted")
    if conv["turns"][2]["en"] not in answer:
        fail("daily", "practice",
             "the drill did not show the other speaker's next line")
    # a line that is not the expected one is answered with the line it wanted
    wrong = drill.respond("nonsense")
    if conv["turns"][3]["en"] not in wrong:
        fail("daily", "practice",
             "an unexpected answer was not shown the line the drill expected")
    # ...and a daily question leaves it rather than being graded as an answer
    escaped = drill.respond("لغت امروز رو توضیح بده")
    if "Word of the Day" not in escaped and "لغت امروز" not in escaped:
        fail("daily", "practice escape",
             "a daily question mid-drill was treated as an answer")

    if verbose:
        print(f"  daily: {len(DAILY_PROBES)} asks, "
              f"{word['en']!r} / {expr['en']!r} / {conv['topic']['en']!r}")


RUNNERS = [
    ("bilingual", run_bilingual),
    ("daily english", run_daily),
    ("vocabulary", run_vocabulary),
    ("grammar", run_grammar),
    ("content", run_content),
    ("smalltalk", run_smalltalk),
    ("robustness", run_robustness),
    ("teacher", run_teacher),
    ("conversation", run_conversation),
    ("accuracy", run_accuracy),
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