#!/usr/bin/env python3
"""Every word in the Vocabulary panel gets at least two example sentences.

The panel's domains live in glossary.json: 71 domains, 2241 distinct words,
each tagged with a CEFR level. A word page used to show whatever sentences the
dictionary happened to keep for it, and most words had none, one, or an
ungraded handful. This builds one file, vocab_examples.json, that holds at
least two examples for every word, each carrying the level it reads at.

Where the sentences come from, in the order they are preferred:

    1. tools/vocab_examples/*.json   written by hand, for the words nothing
                                     else covers; these are the last resort
                                     and the only ones with no source
    2. daily.json                    a word's own two examples, bilingual
    3. books.json                    the 504 / academic lesson examples
    4. senses.json                   one example per sense
    5. lexicon/*.json                the dictionary's own example sentence
    6. the app's prose               sentences out of the reading, story,
                                     travel, journey, phrase and grammar files

A sentence's level is the level of the hardest taught word in it: if it uses a
C1 word, it reads at C1. That is how the examples stay level-centred - a word
at B2 is shown B2 sentences first, then its neighbours, and never a C2 anatomy
of the word it is trying to illustrate.

The build is a gate: it exits non-zero if any word comes out with fewer than
two examples, so a word can never be added to a domain and reach the app with
an empty Examples page.

    python3 tools/build_vocab_examples.py
"""

import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "vocab_examples.json"
AUTHORED = ROOT / "tools/vocab_examples"
TRANSLATED = ROOT / "tools/vocab_translations"

LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
LEVEL_AT = {l: i for i, l in enumerate(LEVELS)}

# The app's own prose. README and docs are deliberately absent: their
# sentences are about the app ("the loading card is the first thing anyone
# sees"), which is not an example of how a learner uses the word.
PROSE = ["reading.json", "stories.json", "journeys.json", "travel.json",
         "phrases.json", "grammar.json", "collocations.json", "idioms.json",
         "distinctions.json", "slang.json", "books.json", "daily.json",
         "level_test.json", "path.json", "kids.json", "bbc_6min.json",
         "jokes.json", "memory.json", "wordquest.json", "corrections.json",
         "register.json", "heroquest.json"]

# Function words do not decide a sentence's level, and a sentence is not an
# example of "a" or "of".
STOP = set("""a an the and or but if of to in on at by for with from as is are
was were be been being do does did have has had will would can could may might
must shall should it its this that these those there here he she they we you
i me my your his her their our not no so than then too very just also only
into over under about after before between out up down off again more most
some any all each other such own same""".split())

ARTICLES = {"a", "an", "the", "your", "my", "someone", "somebody", "something",
            "yourself", "myself", "himself", "herself", "itself", "ourselves",
            "themselves", "it", "them", "him", "her", "us", "me"}

MIN_WORDS, MAX_WORDS = 4, 26
MIN_CHARS, MAX_CHARS = 15, 150
CAP = 6                      # examples kept per word

WORD_RE = re.compile(r"[a-z][a-z'’-]*")
PERSIAN = re.compile(r"[\u0600-\u06FF]")
BAD = re.compile(r"https?://|→|<-|\[|/api/|\.json\b|--")

# A fill-in-the-blank drill is a question, not an example. The app's own prose
# files carry exercise banks - stories.json's comprehension items, path.json's
# practice prompts - and their prompts were being harvested as examples for
# the word they test, so the Vocabulary page printed "He wants to be ___
# architect." with the answer cut out, and the Persian line had the same hole.
# A run of underscores is the tell: no sentence in these sources uses one for
# anything else. Refused here, at the single gate every source passes through,
# so a prompt cannot come back by adding another file to PROSE.
BLANK = re.compile(r"_{2,}")


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def clean(text):
    text = re.sub(r"\s+", " ", str(text)).strip()
    return text


GLOSS = re.compile(r"^(to be|to do|to make|to have|to give|to take|refers to|said to|"
                   r"the person|the amount|the act|the state|the fact|a person who|"
                   r"able to|slightly|someone who|something that|a thing that|"
                   r"not |no one |used to |makes? )", re.I)


def prose_ok(text):
    """A sentence from the app's prose, not a definition or a grammar note.

    The prose files mix example sentences with the dictionary-shaped glosses
    that sit beside them ("To be extremely frightened or scared."), and a
    page of examples built out of definitions is worse than no page at all.
    """
    if GLOSS.match(text) or " ..." in text or text.endswith("..."):
        return False
    return True


def usable(text):
    """A sentence a learner can be shown, not a label, path or Persian line."""
    if not text or PERSIAN.search(text) or BAD.search(text):
        return False
    if BLANK.search(text):
        return False      # a drill prompt, with its answer cut out
    if not MIN_CHARS <= len(text) <= MAX_CHARS:
        return False
    words = text.split()
    if not MIN_WORDS <= len(words) <= MAX_WORDS:
        return False
    return text[-1] in ".!?" and text[0].isupper()


def tokens(text):
    return WORD_RE.findall(text.lower().replace("-", " ").replace("\u2014", " "))


# ---------------------------------------------------------------- vocabulary

def vocabulary():
    """word -> {fa, level, domains}. The panel's own list, not a copy."""
    domains = load("glossary.json")["domains"]
    arch = {w["en"].lower(): w for w in load("word_arch.json")["words"].values()}
    out = {}
    for dom_id, dom in domains.items():
        if not isinstance(dom, dict):
            continue          # _groups is the shelf's order, not a domain
        dom_level = dom.get("level", "A1")
        for pair in dom["words"]:
            en, fa = (pair[0], pair[1] if len(pair) > 1 else "")
            word = clean(en).lower()
            if not word:
                continue
            # the word's own band when the architecture knows it; the domain's
            # band is the fallback for the words it does not
            level = (arch.get(word) or {}).get("level") or dom_level
            rec = out.setdefault(word, {"fa": fa, "level": level, "domains": []})
            if not rec["fa"] and fa:
                rec["fa"] = fa
            if dom_id not in rec["domains"]:
                rec["domains"].append(dom_id)
    return out


# ------------------------------------------------------------------ forms

POS = {}


def forms_of():
    """base word -> the inflections a sentence may use instead of it."""
    forms = {}
    POS.clear()
    for path in glob.glob(str(ROOT / "lexicon" / "*.json")):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        for word, entry in data.get("w", {}).items():
            POS[word] = set(entry.get("p") or [])
            got = {word}
            for form in entry.get("f") or []:
                if form and isinstance(form[0], str):
                    got.add(form[0].lower())
            forms[word] = got
    return forms


def carries(sentence, parts, forms, gap=4):
    """The phrase's words, in order, with at most `gap` words between them.

    A phrase is not its words in any order: "used to get up early" carries
    "get", "used" and "to", but it is not an example of "get used to" - the
    words have to come in that order, as they do in "you get used to it" or
    "she got used to the noise".
    """
    words = tokens(sentence)
    sets = [mark_forms(p, forms) for p in parts]

    def walk(k, i):
        if k == len(parts):
            return True
        # the first word may sit anywhere; every later word has `gap` words of
        # room in front of it, which is what "let the cat out of the bag" and
        # "cut the meeting short" need without matching any sentence that
        # merely mentions the words in another order
        limit = len(words) if k == 0 else min(len(words), i + gap + 1)
        for j in range(i, limit):
            if words[j] in sets[k] and walk(k + 1, j + 1):
                return True
        return False

    return walk(0, 0)


def seen_words(text):
    """The words of a sentence, with a possessive read as its noun."""
    out = set()
    for word in tokens(text):
        out.add(word)
        for tail in ("'s", "\u2019s"):
            if word.endswith(tail):
                out.add(word[: -len(tail)])
    return out


def carries_text(word, text, forms):
    """Is this sentence an example of this word?

    Slash entries are alternatives ("see / observe / notice"); everything else
    is the word itself, its dictionary forms and its regular endings, in order
    for a phrase. The builder and the checker both call this, so a sentence
    that ships is one the gate has already accepted.
    """
    for variant in ([v.strip() for v in word.split("/")] if "/" in word else [word]):
        # "something" and "a bunch" are made only of words that are normally
        # dropped from a phrase, and dropping them leaves nothing to match
        parts = phrase_parts(variant) or tokens(variant)
        if not parts:
            continue
        if len(parts) == 1:
            if mark_forms(parts[0], forms) & seen_words(text):
                return True
        elif carries(text, parts, forms):
            return True
    return False


def phrase_parts(text):
    out = []
    for part in tokens(text):
        head = part.split("'")[0].split("\u2019")[0]
        if head in ARTICLES:
            continue
        out.append(part)
    return out


def mark_forms(word, forms):
    """The spellings of this word a sentence may use, for highlighting it.

    Only what English really does to a word: the dictionary's own table when
    it has one, and the plural/third-person endings by rule. The generator's
    other guesswork ("tigered") is fine for finding a sentence and wrong to
    show a learner as a form of the word.
    """
    out = {word}
    out |= forms.get(word, set())
    if len(word) > 2 and word.endswith("y") and word[-2] not in "aeiou":
        out |= {word[:-1] + "ies", word[:-1] + "ied"}
    if word.endswith(("s", "x", "z", "ch", "sh")):
        out.add(word + "es")
    out.add(word + "s")
    if word.endswith("o"):
        out.add(word + "es")
    if word.endswith("s") and not word.endswith("ss"):
        out.add(word[:-1])
    # a verb takes -ed and -ing; a word the dictionary has never seen may be
    # one, so it gets the benefit of the doubt. A noun the dictionary knows is
    # a noun ("tigered") does not.
    known = POS.get(word)
    if known is None or "verb" in known:
        out.add(word + "ing" if not word.endswith("e") else word[:-1] + "ing")
        out.add(word + "ed" if not word.endswith("e") else word + "d")
    return {w for w in out if w}


def inflect(word):
    """What English would do to a word it has no table for."""
    out = {word}
    if len(word) > 2 and word.endswith("y") and word[-2] not in "aeiou":
        out |= {word[:-1] + "ies", word[:-1] + "ied"}
    if word.endswith(("s", "x", "z", "ch", "sh")):
        out.add(word + "es")
    out |= {word + "s", word + "ed", word + "d", word + "ing"}
    return out


_TRANSLATIONS = None


def translations():
    """English sentence -> Persian, for the sentences no source translated."""
    global _TRANSLATIONS
    if _TRANSLATIONS is None:
        _TRANSLATIONS = {}
        for path in sorted(glob.glob(str(TRANSLATED / "*.json"))):
            for en, fa in json.loads(Path(path).read_text(encoding="utf-8")).items():
                if not en.startswith("_"):
                    _TRANSLATIONS[en] = fa
    return _TRANSLATIONS


# ------------------------------------------------------------------ harvest

def harvest(vocab, forms):
    """word -> [(sentence, level, source)], curated sources first."""
    found = {}

    def add(word, text, level, src, fa=""):
        text = clean(text)
        fa = fa or translations().get(text, "")
        if not usable(text) or not carries_text(word, text, forms):
            return
        item = {"en": text, "level": level if level in LEVEL_AT else "B1", "src": src}
        if fa:
            item["fa"] = clean(fa)
        bucket = found.setdefault(word, [])
        if all(x["en"] != text for x in bucket):
            bucket.append(item)

    # 1. the hand-written ones, for the words no source covers
    for path in sorted(glob.glob(str(AUTHORED / "*.json"))):
        for word, examples in json.loads(Path(path).read_text(encoding="utf-8")).items():
            word = clean(word).lower()
            if word not in vocab:
                continue
            level = vocab[word]["level"]
            for ex in examples:
                if isinstance(ex, str):
                    add(word, ex, level, "authored")
                else:
                    add(word, ex.get("en", ""), ex.get("level", level),
                        "authored", ex.get("fa", ""))

    # 2. a word's own daily examples, with their Persian
    for entry in load("daily.json")["words"]:
        word = clean(entry["en"]).lower()
        if word not in vocab:
            continue
        for ex in entry.get("examples") or []:
            add(word, ex.get("en", ""), entry.get("level", vocab[word]["level"]),
                "daily", ex.get("fa", ""))

    # 3. the library's lesson words
    for book in load("books.json")["books"]:
        for lesson in book.get("lessons", []):
            for entry in lesson.get("words") or []:
                word = clean(entry.get("word", "")).lower()
                if word not in vocab:
                    continue
                for ex in entry.get("examples") or []:
                    add(word, ex, vocab[word]["level"], "books")

    # 4. one example per sense
    for word, entry in load("senses.json")["words"].items():
        word = clean(word).lower()
        if word not in vocab:
            continue
        for sense in entry.get("senses") or []:
            if len(sense) > 3 and sense[3]:
                add(word, sense[3], vocab[word]["level"], "senses")

    # 5. the dictionary's own example
    for path in glob.glob(str(ROOT / "lexicon" / "*.json")):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        for word, entry in data.get("w", {}).items():
            if word not in vocab:
                continue
            for sense in entry.get("s") or []:
                if len(sense) > 3 and sense[3]:
                    add(word, sense[3], vocab[word]["level"], "lexicon")

    # 6. the app's own bilingual sentences: stories, travel, journeys and the
    #    daily card keep the English and its Persian beside each other, so an
    #    example from them can be shown in both languages rather than one.
    BILINGUAL = ["stories.json", "travel.json", "journeys.json", "daily.json",
                 "reading.json", "phrases.json", "books.json", "path.json"]
    pairs = []
    for name in BILINGUAL:
        try:
            node = load(name)
        except (FileNotFoundError, json.JSONDecodeError):
            continue
        stack = [node]
        while stack:
            cur = stack.pop()
            if isinstance(cur, dict):
                en = next((cur.get(k) for k in
                           ("example_en", "en", "sentence", "ex_en") if isinstance(cur.get(k), str)), "")
                fa = next((cur.get(k) for k in
                           ("example_fa", "fa", "sentence_fa", "ex_fa") if isinstance(cur.get(k), str)), "")
                if PERSIAN.search(fa) and usable(clean(en)):
                    pairs.append((clean(en), clean(fa), cur.get("level")))
                stack.extend(cur.values())
            elif isinstance(cur, list):
                stack.extend(cur)

    pair_index = {}
    for en_text, fa_text, level in pairs:
        for tok in set(tokens(en_text)):
            pair_index.setdefault(tok, []).append((en_text, fa_text, level))

    for word, rec in vocab.items():
        variants = ([v.strip() for v in word.split("/")] if "/" in word else [word])
        seen = set()
        for variant in variants:
            parts = phrase_parts(variant)
            if not parts:
                continue
            pool = {}
            for part in parts:
                for sentence, fa_text, level in pair_index.get(part, []):
                    pool.setdefault(sentence, (sentence, fa_text, level))
            for sentence, fa_text, level in pool.values():
                if sentence in seen:
                    continue
                if not prose_ok(sentence):
                    continue
                if len(parts) == 1:
                    ok = any(mark_forms(word, forms) & set(tokens(sentence)))
                else:
                    ok = carries(sentence, parts, forms)
                if ok:
                    seen.add(sentence)
                    add(word, sentence, level or rec["level"], "app", fa_text)

    # 7. the app's prose, levelled by its hardest taught word
    #
    # A word the learner met in the first week does not make a sentence hard:
    # the course's own band for "get" is C1, and taking the maximum over every
    # taught token turned "I'll get the coach." into a C1 example. The most
    # common 600 words are ignored for grading, so the band comes from the
    # words that actually decide whether a sentence reads easily.
    rank = {}
    for path in glob.glob(str(ROOT / "lexicon" / "*.json")):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        for word, entry in data.get("w", {}).items():
            if isinstance(entry.get("r"), int):
                rank[word] = entry["r"]
    common = {w for w, r in rank.items() if r < 600}
    level_of = {}
    for word, rec in vocab.items():
        level_of[word] = rec["level"]
    for base, got in forms.items():
        if base in level_of:
            for form in got:
                level_of.setdefault(form, level_of[base])

    def sentence_level(text):
        hardest = -1
        for tok in tokens(text):
            if tok in STOP or tok in common:
                continue
            level = level_of.get(tok)
            if level:
                hardest = max(hardest, LEVEL_AT[level])
        return LEVELS[hardest] if hardest >= 0 else None

    # every sentence once, indexed by the words it uses, so a domain of 40
    # words does not walk 40,000 sentences 40 times
    index = {}
    for name in PROSE:
        try:
            chunks = []
            walk(load(name), chunks)
        except (FileNotFoundError, json.JSONDecodeError):
            continue
        for chunk in chunks:
            for raw in re.split(r"(?<=[.!?])\s+", clean(chunk)):
                sentence = clean(raw)
                if not usable(sentence):
                    continue
                level = sentence_level(sentence)
                for tok in set(tokens(sentence)):
                    index.setdefault(tok, []).append((sentence, level))

    for word, rec in vocab.items():
        variants = ([v.strip() for v in word.split("/")] if "/" in word else [word])
        pool = {}
        for variant in variants:
            parts = phrase_parts(variant)
            if not parts:
                continue
            if len(parts) == 1:
                for form in mark_forms(parts[0], forms):
                    for sentence, level in index.get(form, []):
                        pool.setdefault(sentence, (sentence, level))
            else:
                # "get up" is two words or it is not the phrase: dropping the
                # particle because it is also a function word matched "I'll get
                # the coach." and showed an A1 learner a sentence with no "up".
                cands = {}
                for part in parts:
                    for sentence, level in index.get(part, []):
                        cands.setdefault(sentence, (sentence, level))
                for sentence, level in cands.values():
                    if carries(sentence, parts, forms):
                        pool.setdefault(sentence, (sentence, level))
        got = list(pool.values())
        for sentence, level in got[:80]:
            if not prose_ok(sentence):
                continue
            # a sentence whose words the course never teaches has no measured
            # band; it is still an example of this word, so it takes the word's
            add(word, sentence, level or rec["level"], "app")
    return found


def walk(node, out):
    if isinstance(node, str):
        out.append(node)
    elif isinstance(node, dict):
        for value in node.values():
            walk(value, out)
    elif isinstance(node, list):
        for value in node:
            walk(value, out)


def pick(entries, level):
    """The word's own level first, then the nearest bands, never further out."""
    want = LEVEL_AT[level]
    # A translated example is worth more than a nearer band: no example ships
    # without its Persian, so the ones that have a meaning are chosen first.
    ranked = sorted(
        entries,
        key=lambda e: (0 if e.get("fa") else 1,
                       abs(LEVEL_AT[e["level"]] - want), LEVEL_AT[e["level"]],
                       1 if e["src"] == "authored" else 0, len(e["en"])),
    )
    out, seen = [], set()
    for entry in ranked:
        if entry["en"] in seen:
            continue
        seen.add(entry["en"])
        out.append(entry)
        if len(out) >= CAP:
            break
    return out


def ipa_of():
    """word -> its American IPA, from the dictionary the app already ships."""
    out = {}
    for path in glob.glob(str(ROOT / "lexicon" / "*.json")):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        for word, entry in data.get("w", {}).items():
            us = (entry.get("i") or {}).get("us")
            if us:
                out[word] = us
    return out


def main():
    vocab = vocabulary()
    forms = forms_of()
    ipa = ipa_of()
    found = harvest(vocab, forms)

    words, missing, total = {}, [], 0
    for word in sorted(vocab):
        entries = pick(found.get(word, []), vocab[word]["level"])
        # A sentence without its Persian is a sentence half the learners here
        # cannot use. Where two translated examples exist, the rest go: no
        # example ships without a meaning once a word can show two that have one.
        bilingual = [e for e in entries if e.get("fa")]
        if len(bilingual) >= 2:
            entries = bilingual
        if len(entries) < 2:
            missing.append(word)
        marks = sorted(mark_forms(word, forms))
        words[word] = {"level": vocab[word]["level"],
                       "fa": vocab[word]["fa"],
                       "ipa": ipa.get(word, ""),
                       "marks": marks,
                       "examples": entries}
        total += len(entries)

    authored = sum(1 for w in words.values() for e in w["examples"]
                   if e["src"] == "authored")
    translated = sum(1 for w in words.values() for e in w["examples"] if e.get("fa"))
    pending = sum(1 for w in words.values() for e in w["examples"] if not e.get("fa"))
    doc = {
        "_readme": ("Examples for every word in the Vocabulary panel, at least "
                    "two each, each tagged with the level it reads at. Built by "
                    "tools/build_vocab_examples.py from the app's own content and "
                    "the hand-written sentences in tools/vocab_examples/. Do not "
                    "edit by hand; re-run the builder."),
        "v": 1,
        "words": words,
        "stats": {"words": len(words), "examples": total, "authored": authored,
                  "translated": translated, "pending": pending,
                  "min_per_word": min(len(w["examples"]) for w in words.values())},
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")

    if missing:
        print(f"FAIL  {len(missing)} words have fewer than two examples")
        for word in missing:
            print("  " + word)
        return 1
    print(f"PASS  {len(words)} words, {total} examples "
          f"({authored} hand-written), at least {doc['stats']['min_per_word']} each; "
          f"{translated} with a Persian line, {pending} still without one")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
