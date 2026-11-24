#!/usr/bin/env python3
"""Every word in the Vocabulary panel has examples worth opening a page for.

The panel now promises a learner three things for every word in every domain:
at least two example sentences, each one carrying the word itself, and each
one tagged with the band it reads at. This suite holds the built file to that
promise, so a word added to a domain cannot reach the app with an empty or
single-example page, and so the "level-centred" part means something.

It reuses the builder's own definitions of a word, a form and a phrase rather
than restating them: a check with a second copy of the rule passes when the
rule and the copy drift apart, which is the failure it exists to catch.

    python3 tools/check_vocab_examples.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_vocab_examples as B          # noqa: E402  (path first)

ROOT = B.ROOT
DOC = ROOT / "vocab_examples.json"
APK = ROOT / "android/app/src/main/assets/www/data/vocab_examples.json"

MIN, MAX = 2, 6


def seen_words(text):
    """The words of a sentence, with a possessive read as its noun."""
    out = set()
    for word in B.tokens(text):
        out.add(word)
        for tail in ("'s", "\u2019s"):
            if word.endswith(tail):
                out.add(word[: -len(tail)])
    return out


def main() -> int:
    if not DOC.exists():
        print("FAIL  vocab_examples.json is missing - run tools/build_vocab_examples.py")
        return 1
    doc = json.loads(DOC.read_text(encoding="utf-8"))
    words = doc.get("words") or {}
    vocab = B.vocabulary()
    forms = B.forms_of()

    problems = []

    def bad(message: str) -> None:
        problems.append(message)

    missing = sorted(set(vocab) - set(words))
    extra = sorted(set(words) - set(vocab))
    if missing:
        bad(f"{len(missing)} vocabulary words have no entry: {missing[:6]}")
    if extra:
        bad(f"{len(extra)} entries are not in any domain: {extra[:6]}")

    for word in sorted(set(vocab) & set(words)):
        rec = words[word]
        examples = rec.get("examples") or []
        level = vocab[word]["level"]

        if rec.get("level") != level:
            bad(f"{word}: band {rec.get('level')!r} contradicts the domain's {level!r}")
        if not rec.get("marks"):
            bad(f"{word}: no forms for the page to mark in a sentence")
        if not MIN <= len(examples) <= MAX:
            bad(f"{word}: {len(examples)} examples, not {MIN}-{MAX}")

        for e in examples:
            text = e.get("en") or ""
            if not B.usable(text):
                bad(f"{word}: not a sentence: {text[:60]!r}")
            if e.get("level") not in B.LEVEL_AT:
                bad(f"{word}: example band {e.get('level')!r} is not a CEFR band")
            if B.PERSIAN.search(text):
                bad(f"{word}: the English line carries Persian: {text[:60]!r}")
            # the sentence has to be an example of *this* word, not a sentence
            # that merely shares a common word with it
            carried = B.carries_text(word, text, forms)
            if not carried:
                bad(f"{word}: the sentence does not carry the word: {text[:60]!r}")
            # and every example has to carry its Persian with it: an example
            # half the learners here cannot read is not an example they can use
            fa = (e.get("fa") or "").strip()
            if not fa:
                bad(f"{word}: the example has no Persian meaning: {text[:60]!r}")
            elif not B.PERSIAN.search(fa):
                bad(f"{word}: the Persian line is not Persian: {fa[:60]!r}")

        # level-centred: translated sentences come first, then the bands run
        # outward from the word's own band, and the first one is never more
        # than one band harder than the word
        if examples and all(e.get("level") in B.LEVEL_AT for e in examples):
            want = B.LEVEL_AT[level]
            dist = [abs(B.LEVEL_AT[e["level"]] - want) for e in examples]
            translated = [bool(e.get("fa")) for e in examples]
            if translated != sorted(translated, reverse=True):
                bad(f"{word}: an untranslated example is listed before a translated one")
            if dist != sorted(dist):
                bad(f"{word}: the bands do not run outward from {level}")
            if dist[0] > 1:
                bad(f"{word}: the easiest example is {dist[0]} bands from {level}")

    stats = doc.get("stats") or {}
    counted = sum(len(v.get("examples") or []) for v in words.values())
    if stats.get("words") != len(words) or stats.get("examples") != counted:
        bad("the header counts do not match the file")
    if stats.get("min_per_word") != min((len(v.get("examples") or [])
                                        for v in words.values()), default=0):
        bad("the header's minimum does not match the file")

    if APK.exists():
        bundled = json.loads(APK.read_text(encoding="utf-8"))
        if bundled.get("words") != words:
            bad("data/vocab_examples.json is stale - run build_apk_ui.py")

    if problems:
        print(f"FAIL  {len(problems)} problems")
        for p in problems[:40]:
            print("  " + p)
        return 1

    bilingual = sum(1 for v in words.values() for e in v.get("examples", [])
                    if e.get("fa"))
    print(f"PASS  {len(words)} words, {counted} examples "
          f"({bilingual} with a Persian line), {MIN}+ each, "
          f"ordered out from the word's band")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
