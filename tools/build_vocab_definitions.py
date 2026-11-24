#!/usr/bin/env python3
"""Give every taught word a dictionary entry, including the 537 the lexicon lacks.

`tools/build_vocab_senses.py` only writes entries for the words the lexicon
holds; a word it does not hold got `{"senses": [], "review":
"not-in-dictionary"}`, which the word card rendered as "The dictionary has no
entry for this word yet." — and, because the card returned early on that path,
the word lost its Examples link too. 221 of those words are phrases ("a
blessing in disguise"), the rest are compounds and closed-class words ("alarm
clock", "albeit"), none of which a general dictionary file of content words
carries.

This reads the hand-written entries in tools/vocab_definitions/*.json and adds
them to senses.json, one sense per word: the part of speech and the English
definition from the authored file and the Persian meaning the course already
teaches (glossary.json). The example stays empty: vocab_examples.json reads
every sense's example, so a sentence written here would come straight back as
a "source" and push the bilingual pairs out of that file. It
never touches an entry the lexicon supplied, and it rebuilds the ones it wrote
itself, so editing a definition and running it again is enough.

    python3 tools/build_vocab_definitions.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SENSES = ROOT / "senses.json"
GLOSSARY = ROOT / "glossary.json"
ARCH = ROOT / "word_arch.json"
AUTHORED = ROOT / "tools/vocab_definitions"
MARK = "authored"

# The senses file names a part of speech in full; the authored files are short.
LONG_POS = {
    "noun": "noun", "verb": "verb", "adj": "adjective", "adv": "adverb",
    "prep": "preposition", "conj": "conjunction", "pron": "pronoun",
    "det": "determiner", "num": "number", "interj": "interjection",
    "phrase": "phrase",
}


def taught() -> dict[str, str]:
    """word -> the Persian gloss the course teaches for it."""
    out: dict[str, str] = {}
    domains = json.loads(GLOSSARY.read_text(encoding="utf-8"))["domains"]
    for value in domains.values():
        if not isinstance(value, dict):
            continue
        for pair in value.get("words") or []:
            word = str(pair[0]).strip().lower()
            gloss = str(pair[1]).strip() if len(pair) > 1 else ""
            out.setdefault(word, gloss)
    return out


def authored() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for path in sorted(AUTHORED.glob("*.json")):
        for word, row in json.loads(path.read_text(encoding="utf-8")).items():
            if word.startswith("_"):
                continue
            pos, definition = row
            if pos not in LONG_POS:
                raise SystemExit(f"{path.name}: {word!r} has the unknown part "
                                 f"of speech {pos!r}")
            if not definition.strip():
                raise SystemExit(f"{path.name}: {word!r} has no definition")
            out.setdefault(word.strip().lower(), {
                "pos": LONG_POS[pos], "def": definition.strip()})
    return out


def main() -> int:
    senses = json.loads(SENSES.read_text(encoding="utf-8"))
    words = senses["words"]
    gloss = taught()
    mine = authored()
    arch = json.loads(ARCH.read_text(encoding="utf-8")).get("words") or {}

    added = 0
    unknown = sorted(set(mine) - set(gloss))
    if unknown:
        raise SystemExit(f"authored words that no domain teaches: {unknown[:6]}")

    for word, entry in mine.items():
        current = words.get(word) or {}
        if current.get("senses") and current.get("defined") != MARK:
            continue                       # the lexicon's entry, left alone
        record = {
            # The example stays empty: vocab_examples.json reads every sense's
            # example, so filling this one from that file would feed the
            # builder its own output and push out the bilingual pairs it found.
            "senses": [[entry["pos"], entry["def"], gloss.get(word, ""), ""]],
            "primary": 0,
            "defined": MARK,
        }
        if (arch.get(word) or {}).get("forms"):
            record["forms"] = arch[word]["forms"]
        words[word] = record
        added += 1

    # 227 entries come from the lexicon with an empty Persian column: the
    # English definition is there and the course's own gloss is not, so the
    # card showed a meaning only in the line above the list. The taught gloss
    # is already written for every one of those words; put it on the sense the
    # card opens, and leave the senses that really have no Persian flagged.
    filled = 0
    for word, entry in words.items():
        taught_fa = gloss.get(word, "")
        rows = entry.get("senses") or []
        if not taught_fa or not rows:
            continue
        if any(str(row[2] or "").strip() for row in rows):
            continue
        rows[0][2] = taught_fa
        if entry.get("en_only"):
            left = [i for i in entry["en_only"] if i != 0]
            if left:
                entry["en_only"] = left
            else:
                entry.pop("en_only", None)
        filled += 1

    # A word the course teaches must never be left pointing at nothing.
    still = sorted(w for w in gloss if not (words.get(w) or {}).get("senses"))
    if still:
        raise SystemExit(f"{len(still)} taught word(s) still have no entry: "
                         f"{still[:6]}")

    total = sum(len(e.get("senses") or []) for e in words.values())
    meta = senses.setdefault("_meta", {})
    meta["words"] = len(words)
    meta["taught"] = len(gloss)
    meta["with_senses"] = sum(1 for e in words.values() if e.get("senses"))
    meta["senses"] = total
    meta["unverified"] = 0
    meta["defined_here"] = sum(1 for e in words.values()
                               if e.get("defined") == MARK)
    meta["multi_sense"] = sum(1 for e in words.values()
                              if len(e.get("senses") or []) > 1)
    meta["persian_filled"] = filled
    meta["multi_pos"] = sum(1 for e in words.values()
                            if len({r[0] for r in (e.get("senses") or [])}) > 1)

    SENSES.write_text(json.dumps(senses, ensure_ascii=False,
                                 separators=(",", ":")) + "\n",
                      encoding="utf-8")
    print(f"PASS  {len(words)} words, {total} senses, {meta['defined_here']} "
          f"defined here ({added} written this run), {filled} Persian meanings "
          f"brought over from the course")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
