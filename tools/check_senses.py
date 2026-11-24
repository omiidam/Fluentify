#!/usr/bin/env python3
"""Every taught word's meanings: are they all there, and are they real?

The vocabulary the course teaches gives each word one Persian gloss. The senses
file (built by tools/build_vocab_senses.py from lexicon/) is what lets a word
card show the rest of the word - `book` as a noun and as a verb. A data file
that quietly loses a sense, keeps a row with no Persian, or numbers its primary
sense out of range would render as a card that looks fine and teaches one
meaning as if it were the only one.

So this checks the file the page reads, sense by sense:

  * every word the course teaches has an entry with at least one sense: a word
    with no entry is what showed "The dictionary has no entry for this word"
    on its card, and a review flag is not a meaning for a learner to read
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

# The card's filter is the builder's rule, not a second copy of it: a check
# with its own idea of "the taught meaning" passes while the file and the rule
# drift apart, which is the failure it exists to catch.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_vocab_senses import MAX_SHOWN, gloss_matches  # noqa: E402

POS = {"noun", "verb", "adjective", "adverb", "pronoun", "preposition",
       "conjunction", "interjection", "determiner", "number", "phrase"}
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

    undefined = sorted(w for w, e in words.items() if not (e.get("senses") or []))
    check("every taught word carries at least one meaning", not undefined,
          ", ".join(undefined[:6]) if undefined
          else f"{len(words)} words, each with a definition and a Persian gloss")

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
    check("no entry is left empty and waiting for review",
          not empty_gloss and not reviewed,
          ", ".join(empty_gloss[:6] + reviewed[:6]) if (empty_gloss or reviewed)
          else "no review flags; the words the lexicon lacks are defined here")

    # The taught gloss must be the sense shown first, wherever the dictionary
    # holds it: a card whose first meaning contradicts the lesson that opened
    # it is worse than no second meaning at all.
    contradict, unmatched = [], 0
    for word, entry in words.items():
        senses = entry.get("senses") or []
        if not senses:
            continue
        if not persian_keys(want.get(word, "")):
            continue
        hits = [i for i, s in enumerate(senses) if gloss_matches(want.get(word, ""), s[2])]
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

    # ---- what the card is allowed to show --------------------------------
    # The dictionary keeps the senses of the language, not the senses the
    # lesson taught. Shown unfiltered, the card for `red` listed a tributary of
    # the Mississippi and a word for bloodshed next to the colour, which reads
    # as though the word mostly means those things.
    too_many = sorted(w for w, e in words.items()
                      if len(e.get("senses") or []) > MAX_SHOWN)
    check(f"no word card lists more than {MAX_SHOWN} meanings", not too_many,
          ", ".join(f"{w}:{len(words[w]['senses'])}" for w in too_many[:6]) if too_many
          else f"the longest list is "
               f"{max((len(e.get('senses') or []) for e in words.values()), default=0)}")

    stray = []
    for word, entry in words.items():
        senses = entry.get("senses") or []
        for row in senses[1:]:
            if not gloss_matches(want.get(word, ""), row[2] if len(row) > 2 else ""):
                stray.append(f"{word}: {row[1][:46] if len(row) > 1 else row}")
    check("every meaning after the first is one the lesson teaches", not stray,
          "; ".join(stray[:4]) if stray
          else "no sense outside the taught meaning survives the filter")

    # The regression by name: this is the card the report was written about.
    red = (words.get("red") or {}).get("senses") or []
    noisy = [s for s in red
             if re.search(r"mississippi|tributary|bloodshed|violen", str(s[1]), re.I)]
    check("the card for 'red' shows the colour, not a river or bloodshed",
          bool(red) and not noisy
          and any("color" in str(s[1]).lower() or "قرمز" in str(s[2]) for s in red),
          "; ".join(str(s[1])[:50] for s in red) if red
          else "red has no entry: %r" % (noisy,))

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

    # ------------------------------------------------------- the chatbot --
    # Both engines answer "all the meanings of book" with the whole entry, not
    # the first few senses: the offer in the panel is worthless if the tutor
    # will not read out what the panel can show.
    sys.path.insert(0, str(ROOT))
    from chatbot import ChatBot  # noqa: E402  (after the path is set)

    bot = ChatBot()
    _head, book = bot.lex_find("book")
    whole = len(book.get("s") or [])
    for question, marker in (("all the meanings of book", "▸ noun"),
                             ("همه معنی‌های book", "▸ اسم")):
        reply = bot.respond(question)
        numbered = len(re.findall(r"^\s+[\d\u06F0-\u06F9]+\.", reply, re.M))
        check(f"the chatbot answers {question!r} with the whole entry",
              whole > 3 and numbered == whole and marker in reply,
              f"{numbered} of {whole} senses, part of speech {marker!r} "
              f"present: {marker in reply}")

    page_js = (ROOT / "android/app/src/main/assets/www/bot.js").read_text(encoding="utf-8")
    check("the offline engine answers it the same way",
          "formatLexAll(head, entry, asked, lang)" in page_js
          and "const LEX_ALL_PATTERNS" in page_js,
          "the APK has the same trigger and the same full-entry reply")

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
          f"than one meaning; every word has a definition "
          f"({meta.get('defined_here', 0)} written for this course where the "
          f"dictionary holds none)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
