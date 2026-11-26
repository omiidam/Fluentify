#!/usr/bin/env python3
"""The chat's own knowledge, checked against the knowledge the app teaches.

The tutor answers out of four places: the 70,000-word dictionary, the lesson's
glossary (2,240 taught words), senses.json (a definition and a Persian for each
of them) and vocab_examples.json (examples). Where those overlap, the same word
used to be described twice and differently - the Vocabulary card said سیب and
the chat said a botanical phrase - so a learner could look one word up in two
places in the same app and be told two things.

The lesson is the authority for a taught word. This check holds the chat to
that: every taught word gets a card, every card has a definition and exactly
one Persian, that Persian is the one the card prints, and no line of a card
mixes the two scripts (a line that starts in English and ends in Persian is
laid out left to right and the Persian reverses).

The kids' side is checked too: the curriculum in kids.json is the single
source for a child's word, with the hand-written bank kept only for words it
does not hold, and the card prints the definition and example the curriculum
already gives.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from chatbot import ChatBot  # noqa: E402

WEBAPP = ROOT / "webapp.py"
KIDS = ROOT / "kids.json"
VOCAB = ROOT / "vocab_examples.json"
GLOSSARY = ROOT / "glossary.json"

PASS = 0
FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  ok   {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}" + (f"\n       {detail}" if detail else ""))


FA = re.compile(r"[\u0600-\u06FF]")
EN = re.compile(r"[A-Za-z]")


def mixed(line):
    return bool(FA.search(line)) and bool(EN.search(line))


def lesson_glosses():
    """word -> the one Persian the lesson teaches for it.

    vocab_examples.json is the vocabulary list: one word, one meaning, and the
    examples written to fit it. Some words really are homonyms in the glossary
    (light is both روشن and سبک) - the lesson picks one, and that pick is the
    meaning everything else has to agree with.
    """
    data = json.load(open(VOCAB, encoding="utf-8"))["words"]
    return {w.lower(): (rec.get("fa") or "") for w, rec in data.items()}


def glossary_glosses():
    """word -> every Persian the glossary holds for it."""
    data = json.load(open(GLOSSARY, encoding="utf-8"))["domains"]
    out = {}
    for dom in data.values():
        if not isinstance(dom, dict):
            continue
        for pair in dom.get("words") or []:
            if pair and pair[0] and len(pair) > 1:
                out.setdefault(str(pair[0]).lower(), []).append(pair[1])
    return out


def main():
    print("chat knowledge")
    bot = ChatBot()
    words = list(json.load(open(VOCAB, encoding="utf-8"))["words"])
    cards = {}

    missing, no_def, no_fa = [], [], []
    for word in words:
        card = bot.taught_entry(word)
        if not card:
            missing.append(word)
            continue
        cards[word] = card
        if not card["def_en"].strip():
            no_def.append(word)
        if not card["fa"].strip():
            no_fa.append(word)

    check(f"every one of the {len(words)} taught words has a card",
          not missing, f"{len(missing)} without: {missing[:6]}")
    check("every card carries an English definition", not no_def,
          f"{len(no_def)} without: {no_def[:6]}")
    check("every card carries a Persian gloss", not no_fa,
          f"{len(no_fa)} without: {no_fa[:6]}")

    # One meaning per taught word: the Persian is the card's, not a second
    # gloss invented by the dictionary. (The dictionary keeps its own senses;
    # this is about what the chat *shows* for a taught word.)
    taught_fa = lesson_glosses()
    wrong = [(w, cards[w]["fa"], taught_fa[w.lower()])
             for w in cards
             if w.lower() in taught_fa
             and cards[w]["fa"].strip() != taught_fa[w.lower()].strip()]
    check("a taught word says what its Vocabulary card says",
          not wrong, f"{len(wrong)} disagree: {wrong[:4]}")

    # ... and the meaning it says is a meaning the glossary already holds, so a
    # word never carries a third gloss that only the chat knows about.
    known = glossary_glosses()
    invented = [(w, cards[w]["fa"], known.get(w.lower()))
                for w in cards
                if w.lower() in known
                and cards[w]["fa"].strip()
                not in [str(g).strip() for g in known[w.lower()]]]
    check("the chat's meaning is one the glossary already teaches",
          not invented, f"{len(invented)}: {invented[:4]}")

    # Two scripts, two lines.
    mixed_lines = []
    for word, card in cards.items():
        text = bot.format_taught_entry(card, "fa")
        for line in text.split("\n")[1:]:
            if mixed(line):
                mixed_lines.append((word, line.strip()))
    check("no card line mixes Persian and English", not mixed_lines,
          f"{len(mixed_lines)} mixed: {mixed_lines[:4]}")

    # A definition ask reaches the card, in both languages, for phrases too.
    probes = ["a blessing", "a dozen eggs", "a bunch of keys", "a far cry from"]
    bad = []
    for word in probes:
        for question in (f"معنی {word}", f"what does {word} mean"):
            reply = bot.respond(question)
            card = cards.get(word)
            if not card:
                continue
            if card["fa"] and card["fa"] not in reply:
                bad.append((question, reply.split("\n")[0]))
            if card["def_en"] and card["def_en"] not in reply:
                bad.append((question, "definition missing"))
    check("a definition question is answered by the lesson", not bad,
          f"{len(bad)}: {bad[:4]}")

    # ---- the kids' side -------------------------------------------------
    kids = json.load(open(KIDS, encoding="utf-8"))
    kid_words = [w for theme in kids["words"] for w in theme.get("words") or []]
    no_kid_def = [w.get("word") for w in kid_words
                  if not str(w.get("def_en") or "").strip()]
    no_kid_fa = [w.get("word") for w in kid_words
                 if not str(w.get("fa") or "").strip()]
    no_kid_ex = [w.get("word") for w in kid_words
                 if not str(w.get("example_en") or "").strip()
                 or not str(w.get("example_fa") or "").strip()]
    check(f"all {len(kid_words)} curriculum words have a definition",
          not no_kid_def, f"{len(no_kid_def)}: {no_kid_def[:6]}")
    check("all curriculum words have a Persian gloss", not no_kid_fa,
          f"{len(no_kid_fa)}: {no_kid_fa[:6]}")
    check("all curriculum words have an example both ways", not no_kid_ex,
          f"{len(no_kid_ex)}: {no_kid_ex[:6]}")

    page = WEBAPP.read_text(encoding="utf-8")
    check("the child's lookup reads the curriculum first",
          "function kWords()" in page
          and "((doc && doc.words) || []).forEach" in page,
          "kWords() no longer builds from kids.json")
    check("the hand-written bank no longer answers for a taught word",
          "const key = String(w.en || '').toLowerCase();\n"
          "      if (!key || seen[key]) return;   // the curriculum already owns it"
          in page,
          "the guard that drops duplicated KID_KB words is gone")
    check("the child's search bank is built from kWords()",
          "words: kWords().map(" in page,
          "kBank still maps KID_KB")
    check("a child's card prints the definition and the example",
          "if (w.def) out +=" in page and "if (w.ex) out +=" in page,
          "kWordCard no longer prints them")
    check("the child's card keeps one language per line",
          "if (w.exFa) out +=" in page
          and "w.fa + (w.say ? ' — بگو: ' + w.say : '')" in page,
          "the card puts a Persian and an English run on one line")

    print(f"\n{'PASS' if not FAIL else 'FAIL'}  {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
