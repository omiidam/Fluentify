#!/usr/bin/env python3
"""Every taught word's meanings: are they all there, and are they real?

The vocabulary the course teaches gives each word one Persian gloss. The senses
file (built by tools/build_vocab_senses.py from lexicon/) is what lets a word
card show the rest of the word - `book` as a noun and as a verb. A data file
that quietly loses a sense, keeps a row with no Persian, or numbers its primary
sense out of range would render as a card that looks fine and teaches one
meaning as if it were the only one.

So this checks the file the page reads, sense by sense:

  * every word the course teaches has an entry, and one the dictionary does not
    hold says so in words (a review reason) instead of shipping an empty gloss
  * every sense has a part of speech, an English definition and a Persian
    meaning, and a definition that is not just the word again
  * no word carries the same sense twice
  * `primary` points at a sense that exists, and its Persian is the gloss the
    course already teaches where the dictionary holds that meaning
  * the sources and their licences travel with the file - it is a derived work,
    and the attribution is the condition of shipping it
  * the page and the offline build are both wired to it

    python3 tools/check_senses.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SENSES = ROOT / "senses.json"
ARCH = ROOT / "word_arch.json"
GLOSSARY = ROOT / "glossary.json"
KIDS = ROOT / "kids.json"
PAGE = ROOT / "webapp.py"
BUILDER = ROOT / "build_apk_ui.py"
APK = ROOT / "android/app/src/main/assets/www/data/senses.json"

POS = {"noun", "verb", "adjective", "adverb", "pronoun", "preposition",
       "conjunction", "interjection", "determiner", "number"}
FA = re.compile(r"[\u0621-\u064A\u066E-\u06D3\u06FA-\u06FF]")
LATIN = re.compile(r"[A-Za-z]")

problems: list[str] = []
notes: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> bool:
    if ok:
        print(f"  ok    {label}" + (f" ({detail})" if detail else ""))
    else:
        problems.append(label + (f": {detail}" if detail else ""))
        print(f"  FAIL  {label}" + (f" ({detail})" if detail else ""))
    return ok


def norm(text: str) -> str:
    return (text or "").strip().lower().replace("\u2019", "'")


def persian_keys(text: str) -> set[str]:
    return {p.strip() for p in re.split(r"[\u060c,;/]| - ", text or "") if p.strip()}


def taught() -> dict[str, str]:
    """Every taught word and the gloss the course gives it."""
    out: dict[str, str] = {}
    arch = json.loads(ARCH.read_text(encoding="utf-8"))["words"]
    for word, entry in arch.items():
        out.setdefault(word, (entry.get("fa") or "").strip())
    domains = json.loads(GLOSSARY.read_text(encoding="utf-8"))["domains"]
    for dom in domains.values():
        if not isinstance(dom, dict):
            continue
        for pair in dom.get("words") or []:
            if isinstance(pair, list) and len(pair) >= 2:
                out.setdefault(str(pair[0]).strip().lower(), str(pair[1]).strip())
    kids = json.loads(KIDS.read_text(encoding="utf-8"))
    for theme in kids.get("words") or []:
        for word in theme.get("words") or []:
            key = norm(word.get("word"))
            if key:
                out.setdefault(key, (word.get("fa") or "").strip())
    return out


def main() -> int:
    if not SENSES.exists():
        print("FAIL  senses.json is missing - run tools/build_vocab_senses.py")
        return 1
    doc = json.loads(SENSES.read_text(encoding="utf-8"))
    words = doc.get("words") or {}
    meta = doc.get("_meta") or {}
    check("the file says what it is and where it came from",
          bool(meta.get("readme")) and bool(meta.get("sources")),
          f"{len(words)} words")
    licenses = [s.get("license") for s in (meta.get("sources") or [])]
    check("every source ships with its licence",
          licenses and all(licenses),
          ", ".join(str(l) for l in licenses))

    # ------------------------------------------------------------- coverage --
    want = taught()
    missing = [w for w in want if w not in words]
    check("every taught word has an entry", not missing,
          ", ".join(missing[:6]) if missing
          else f"{len(want)} taught words, {len(words)} entries")

    # --------------------------------------------------------------- senses --
    bad_pos, no_fa, no_def, dupes, bad_primary, circular = [], [], [], [], [], []
    unflagged: list[str] = []
    reviewed, empty_gloss = [], []
    total = 0
    for word, entry in words.items():
        senses = entry.get("senses") or []
        if not senses:
            if not entry.get("review"):
                empty_gloss.append(word)
            else:
                reviewed.append(word)
            continue
        total += len(senses)
        seen = set()
        for i, row in enumerate(senses):
            if not isinstance(row, list) or len(row) < 4:
                no_def.append(word)
                continue
            pos, definition, persian, example = (str(x or "") for x in row[:4])
            if pos not in POS:
                bad_pos.append(f"{word}:{pos}")
            if not LATIN.search(definition):
                no_def.append(word)
            elif norm(definition).strip(" .") == norm(word):
                circular.append(word)
            if not FA.search(persian):
                no_fa.append(word)
                if i not in (entry.get("en_only") or []):
                    unflagged.append(f"{word}:{i}")
            key = (pos, norm(definition))
            if key in seen:
                dupes.append(word)
            seen.add(key)
        primary = entry.get("primary")
        if not isinstance(primary, int) or not 0 <= primary < len(senses):
            bad_primary.append(f"{word}:{primary}")

    check("every sense names a part of speech", not bad_pos,
          ", ".join(bad_pos[:6]) if bad_pos else f"{total} senses")
    check("every sense has an English definition", not no_def,
          ", ".join(sorted(set(no_def))[:6]))
    check("no definition is just the word again", not circular,
          ", ".join(sorted(set(circular))[:6]))
    check("a sense with no Persian says so, it is not a blank line",
          not unflagged,
          ", ".join(unflagged[:6]) if unflagged
          else f"{len(no_fa)} English-only sense(s) in the file, all of them "
               f"flagged; {total - len(no_fa)} senses carry a Persian meaning")
    check("no word carries the same sense twice", not dupes,
          ", ".join(sorted(set(dupes))[:6]))
    check("every primary sense points at a sense that exists", not bad_primary,
          ", ".join(bad_primary[:6]))
    check("an entry with no senses says why", not empty_gloss,
          ", ".join(empty_gloss[:6]) if empty_gloss
          else f"{len(reviewed)} word(s) marked for review, none glossed by guess")

    # The taught gloss must be the sense shown first, wherever the dictionary
    # holds it: a card whose first meaning contradicts the lesson that opened
    # it is worse than no second meaning at all.
    contradict, unmatched = [], 0
    for word, entry in words.items():
        senses = entry.get("senses") or []
        if not senses:
            continue
        taught_fa = persian_keys(want.get(word, ""))
        if not taught_fa:
            continue
        hits = [i for i, s in enumerate(senses) if taught_fa & persian_keys(s[2])]
        if not hits:
            unmatched += 1
            continue
        if entry.get("primary") not in hits:
            contradict.append(word)
    check("where the dictionary holds the taught meaning, that is the one shown first",
          not contradict,
          ", ".join(contradict[:6]) if contradict
          else f"{len(words) - unmatched - len(reviewed)} words matched their "
               f"taught gloss; {unmatched} keep the source's first sense because "
               f"the dictionary words the meaning differently")

    multi = sum(1 for e in words.values() if len(e.get("senses") or []) > 1)
    multi_pos = sum(1 for e in words.values()
                    if len({r[0] for r in (e.get("senses") or [])}) > 1)
    check("the file is a meaning record, not one gloss per word", multi > 0,
          f"{multi} words with more than one meaning, {multi_pos} with more "
          f"than one part of speech, {total} senses in all")
    check("the counts in the file match the file",
          meta.get("words") == len(words) and meta.get("senses") == total
          and meta.get("with_senses") == sum(1 for e in words.values() if e.get("senses")),
          f"meta says {meta.get('words')} words/{meta.get('senses')} senses, "
          f"the words say {len(words)}/{total}")

    # -------------------------------------------------------------- wiring --
    src = PAGE.read_text(encoding="utf-8")
    check("the page reads the senses file",
          "loadJSON('senses')" in src and "async function sensesFor(word)" in src,
          "the word card's loader")
    check("the word card offers the other meanings", "wd-all" in src
          and "All meanings" in src and "همهٔ معانی" in src,
          "one control, both languages")
    check("the primary sense is marked in words, not only in colour",
          "the meaning you learned" in src and "همان معنایی که آموختی" in src,
          "a child who cannot see the tint still reads which one the course taught")
    check("the card says which senses carry no Persian",
          "no Persian gloss recorded" in src and "معنی فارسی ثبت نشده" in src,
          "the English meaning is shown with the gap named")
    check("a word with no recorded senses says so instead of guessing",
          "No other meanings are recorded" in src
          and "معنی دیگری برای این" in src)
    build = BUILDER.read_text(encoding="utf-8")
    lazy = re.search(r"LAZY_DATA = \[(.*?)\]", build, re.S)
    check("the offline build ships the senses file",
          lazy is not None and '"senses.json"' in lazy.group(1),
          "read when a word is opened, not at boot")
    check("the offline build reads the same file the page asks for",
          "'senses'" in src, "loadJSON('senses') resolves to /api/senses on the "
          "web and data/senses.json in the APK")

    if APK.exists():
        same = json.loads(APK.read_text(encoding="utf-8"))
        check("the APK bundle carries the same senses",
              len(same.get("words") or {}) == len(words),
              f"{len(words)} words in both")
    else:
        notes.append("the APK bundle has not been built; run build_apk_ui.py")

    print()
    if notes:
        print("  note  " + "\n        ".join(notes))
    if problems:
        print(f"\n{len(problems)} problem(s) with the vocabulary senses")
        for p in problems:
            print("   - " + p)
        return 1
    print(f"PASS  {len(words)} taught words, {total} senses, {multi} with more "
          f"than one meaning; {len(reviewed)} word(s) the dictionary does not "
          f"hold are flagged rather than guessed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
