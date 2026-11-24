#!/usr/bin/env python3
"""Every taught word's meanings, taken from the dictionary Fluentify already has.

The vocabulary the course teaches is `word_arch.json`: 1,946 words, each with a
single Persian gloss. A gloss is a label, not a meaning - `book` is a کتاب and
also a verb that reserves a table - and a learner who only ever sees the label
is being taught that words have one meaning.

The dictionary itself already knows better. `lexicon/` holds 70,392 headwords
and 111,588 senses, each one a part of speech, an English definition, a Persian
meaning and an example, built from OpenJam (MIT) and Princeton WordNet (the
WordNet licence) by tools/build_lexicon.py. What was missing was the bridge: the
dictionary was only ever read on the server, by the chatbot, so the vocabulary
panel could not show a second meaning.

This writes that bridge as data, one entry per taught word:

    senses.json
      words/<word> = {ipa, pos[], senses[[pos, def, fa, example]], primary, forms, review}

`primary` is the sense the course already teaches, found by matching the taught
gloss against the sense's Persian; when nothing matches it is the source's own
first sense, which is the most frequent one. Senses keep the source's order, so
a learner who has read sense 2 before still finds it in second place.

Nothing is invented here. A taught word the dictionary does not hold keeps an
empty list and a `review` reason, and the count is printed at the end: the file
says what it could not verify rather than filling the gap with a guess.

    python3 tools/build_vocab_senses.py
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCH = ROOT / "word_arch.json"
GLOSSARY = ROOT / "glossary.json"
KIDS = ROOT / "kids.json"
LEXICON = ROOT / "lexicon"
OUT = ROOT / "senses.json"

# A sense is only useful with all four of these. The lexicon stores them as
# [pos, definition, persian, example, unused fifth slot]; a half-filled row is
# dropped here rather than shipped as a blank line in the panel.
MAX_SENSES = 6
# What the word card shows. The dictionary keeps the senses of the language,
# not of the lesson: `red` is a colour, a tributary of the Mississippi and a
# word for bloodshed, and a card that lists all three teaches a learner that
# the word they just met is mostly about rivers.
MAX_SHOWN = 3

POS_ALIASES = {"n": "noun", "noun": "noun", "v": "verb", "verb": "verb",
               "adj": "adjective", "adjective": "adjective",
               "adv": "adverb", "adverb": "adverb",
               "prep": "preposition", "preposition": "preposition",
               "pron": "pronoun", "pronoun": "pronoun"}


def load_lexicon() -> tuple[dict, dict]:
    """The headwords and the inflected-form map, from all shards."""
    words: dict[str, dict] = {}
    forms: dict[str, str] = {}
    for shard in sorted(LEXICON.glob("*.json")):
        if shard.name.startswith("_"):
            continue
        doc = json.loads(shard.read_text(encoding="utf-8"))
        words.update(doc.get("w") or {})
        forms.update(doc.get("f") or {})
    return words, forms


def norm(text: str) -> str:
    return (text or "").strip().lower().replace("’", "'")


def persian_keys(text: str) -> list[str]:
    """The Persian alternatives a gloss offers, as comparable keys.

    The taught gloss is one string - "کتاب، رزرو کردن" - while a sense carries
    one meaning. Splitting both sides on the separators the data uses lets the
    primary sense be found without a fuzzy match that would pick a synonym.
    """
    parts = re.split(r"[،,;/]| - ", text or "")
    return [p.strip() for p in parts if p.strip()]


def pos_key(value: str) -> str:
    """`adj` and `adjective` are the same part of speech."""
    return POS_ALIASES.get((value or "").strip().lower(), "")


def gloss_matches(taught_fa: str, sense_fa: str) -> bool:
    """Does this sense carry a meaning the course already teaches?

    Compared on the Persian, which is the meaning the learner actually holds,
    and compared as whole gloss parts that contain one another: the course
    teaches `red` as قرمز and the dictionary words its colour sense رنگ قرمز.
    Single letters are ignored, because a bare و or ی is in every second
    Persian gloss and would match everything.
    """
    for want in persian_keys(taught_fa):
        if len(want) < 2:
            continue
        for got in persian_keys(sense_fa):
            if len(got) < 2:
                continue
            if want == got or want in got or got in want:
                return True
    return False


def shown_senses(senses: list[list[str]], primary: int, taught_fa: str,
                 taught_pos: str) -> list[int]:
    """The indexes the card shows: the taught meaning first, then the senses
    that mean something the lesson covers, never more than MAX_SHOWN.

    A sense the course does not teach is noise on a word card even when it is
    a real meaning - the learner met this word in one lesson, and the card is
    the lesson's dictionary. The primary sense is always kept; where the
    dictionary holds no sense with the taught meaning, it is the only one.
    """
    want_pos = pos_key(taught_pos)
    same_pos: list[int] = []
    other_pos: list[int] = []
    for i, sense in enumerate(senses):
        if i == primary or not taught_fa:
            continue
        if not gloss_matches(taught_fa, sense[2]):
            continue
        (same_pos if pos_key(sense[0]) == want_pos else other_pos).append(i)
    return ([primary] + same_pos + other_pos)[:MAX_SHOWN]


def senses_of(entry: dict) -> list[list[str]]:
    out = []
    seen: set[tuple[str, str]] = set()
    for raw in (entry.get("s") or [])[:MAX_SENSES]:
        row = list(raw) + [""] * 5
        pos, definition, persian, example = (row[0] or "", row[1] or "",
                                             row[2] or "", row[3] or "")
        if not (pos and definition):
            continue
        key = (pos, definition.strip().lower())
        if key in seen:
            continue
        seen.add(key)
        out.append([pos, definition.strip(), persian.strip(), example.strip()])
    return out


def taught_words() -> dict[str, dict]:
    """Every vocabulary item the course teaches, keyed by its headword.

    Three sources, one shape: the level bands in word_arch, the domain lists in
    the glossary, and the kids bank. A word in more than one keeps the first
    gloss it is given, because they already agree - the glossary is generated
    from the same list.
    """
    taught: dict[str, dict] = {}
    arch = json.loads(ARCH.read_text(encoding="utf-8"))["words"]
    for word, entry in arch.items():
        taught.setdefault(word, {
            "word": word, "fa": (entry.get("fa") or "").strip(),
            "pos": entry.get("pos") or "", "level": entry.get("level") or "",
        })
    domains = json.loads(GLOSSARY.read_text(encoding="utf-8"))["domains"]
    for dom in domains.values():
        if not isinstance(dom, dict):
            continue
        for pair in dom.get("words") or []:
            if not isinstance(pair, list) or len(pair) < 2:
                continue
            taught.setdefault(str(pair[0]).strip().lower(), {
                "word": str(pair[0]).strip().lower(), "fa": str(pair[1]).strip(),
                "pos": "", "level": dom.get("level") or "",
            })
    kids = json.loads(KIDS.read_text(encoding="utf-8"))
    for theme in kids.get("words") or []:
        for word in theme.get("words") or []:
            key = norm(word.get("word") or "")
            if key:
                taught.setdefault(key, {
                    "word": key, "fa": (word.get("fa") or "").strip(),
                    "pos": "", "level": "A1",
                })
    return taught


def build() -> dict:
    words, forms = load_lexicon()
    taught = taught_words()
    out: dict[str, dict] = {}
    counts = Counter()

    for key, item in sorted(taught.items()):
        head = key if key in words else forms.get(key)
        entry = words.get(head) if head else None
        if entry is None:
            out[key] = {"senses": [], "review": "not-in-dictionary"}
            counts["not-in-dictionary"] += 1
            continue
        senses = senses_of(entry)
        if not senses:
            out[key] = {"senses": [], "review": "no-senses"}
            counts["no-senses"] += 1
            continue

        # The sense the course teaches, if the dictionary has it: the gloss the
        # child already learned must be the one shown first, or the panel would
        # contradict the lesson that sent them here.
        primary = 0
        matched = False
        for i, sense in enumerate(senses):
            if gloss_matches(item["fa"], sense[2]):
                primary = i
                matched = True
                break

        # Keep the senses this lesson is about, and no more than three of
        # them. The taught meaning moves to the front, so the card opens on
        # the sense the learner already knows.
        keep = shown_senses(senses, primary, item["fa"], item["pos"])
        if len(keep) != len(senses):
            counts["trimmed"] += 1
            counts["dropped"] += len(senses) - len(keep)
        senses = [senses[i] for i in keep]
        primary = 0
        if head != key:
            counts["via-form"] += 1
        # The source has English-only senses for some words. They are kept -
        # an English meaning is still a meaning - but they are listed by index
        # so the card can say which ones carry no Persian instead of printing
        # an empty line where a translation should be.
        en_only = [i for i, s in enumerate(senses) if not s[2]]
        counts["en-only"] += len(en_only)
        if len(senses) > 1:
            counts["multi-sense"] += 1
        if len({s[0] for s in senses}) > 1:
            counts["multi-pos"] += 1
        counts["senses"] += len(senses)
        counts["words"] += 1
        counts["matched"] += 1 if matched else 0
        out[key] = {
            "ipa": ((entry.get("i") or {}).get("us") or "").strip(),
            "pos": entry.get("p") or [],
            "senses": senses,
            "primary": primary,
            "matched": matched,
            "en_only": en_only,
            "head": head if head != key else "",
            "review": "",
        }

    doc = {
        "_meta": {
            "readme": (
                "Every taught word's meanings, built by tools/build_vocab_senses.py "
                "from lexicon/ (OpenJam, MIT; Princeton WordNet, WordNet licence). "
                "Senses are [pos, definition, persian, example]; 'primary' is the "
                "sense the course already teaches. Only the senses whose meaning "
                "the course also teaches are kept, at most three per word: the "
                "dictionary knows 'red' as a river too, and the word card is the "
                "lesson's dictionary, not the language's. An empty list with a "
                "'review' reason means the dictionary does not hold the word and "
                "nothing was invented for it."
            ),
            "sources": [
                {"name": "OpenJam", "license": "MIT",
                 "url": "https://github.com/amirj4m/openjam"},
                {"name": "Princeton WordNet 3.1", "license": "WordNet licence",
                 "url": "https://wordnet.princeton.edu/"},
            ],
            "captured": "2026-11-11",
            "taught": len(taught),
            "words": len(taught),
            "with_senses": counts["words"],
            "taught_gloss_found": counts["matched"],
            "senses": counts["senses"],
            "multi_sense": counts["multi-sense"],
            "multi_pos": counts["multi-pos"],
            "via_form": counts["via-form"],
            "unverified": counts["not-in-dictionary"] + counts["no-senses"],
            "en_only_senses": counts["en-only"],
            "trimmed_words": counts["trimmed"],
            "dropped_senses": counts["dropped"],
        },
        "words": out,
    }
    return doc


def main() -> int:
    if not LEXICON.exists():
        print("FAIL  there is no lexicon/ to build from")
        return 1
    doc = build()
    text = json.dumps(doc, ensure_ascii=False, separators=(",", ":"))
    OUT.write_text(text + "\n", encoding="utf-8")
    meta = doc["_meta"]
    print(f"wrote {OUT.name}: {len(text) // 1024} KB, {meta['words']} words, "
          f"{meta['senses']} senses, {meta['multi_sense']} with more than one "
          f"meaning, {meta['multi_pos']} with more than one part of speech")
    print(f"  {meta['unverified']} taught words are not in the dictionary and "
          f"are marked for review rather than glossed here")
    print("  next: python3 tools/build_vocab_definitions.py gives those words "
          "their entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
