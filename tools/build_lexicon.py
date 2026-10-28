#!/usr/bin/env python3
"""Build Fluentify's dictionary from open, redistributable lexical sources.

    python3 tools/build_lexicon.py            # uses (and fills) the source cache

Output is a sharded lexicon, not one file:

    lexicon/<aa>.json      one shard per two-letter prefix of the headword
    lexicon/_meta.json     counts, source versions, licences, attribution

Sharding is the point of the whole design. The page fetches the shard for the
words in the current message and nothing else, so the dictionary never has to
be parsed at startup and a phone never holds more than a few hundred thousand
characters of it. The engines in chatbot.py and bot.js both read this same
layout, so a lookup is identical on the command line, in the browser and in the
APK.

Sources (both allow redistribution; the notices are reproduced in
lexicon/_meta.json and in the app's About/help text):

  OpenJam            MIT.  English lemmas, senses, definitions, examples,
                     Persian sense translations, IPA, inflected forms.
                     https://github.com/amirj4m/openjam
  Princeton WordNet  WordNet licence (BSD-style).  Synonyms and antonyms.
                     Copyright 2006, 2011 by Princeton University.

Not imported, deliberately: the English-Persian compilation whose README warns
that its upstream sources carry unnamed licences, and the VahidN dictionary
collection whose repository is Apache-2.0 but whose individual dictionaries
publish no licence of their own. Two sources we can stand behind beat five we
cannot.

What the source does *not* provide, this file does not invent: no entry gets a
CEFR level, a synonym, an example or an antonym that the data does not contain.

A note on `level`: OpenJam ships a CEFR field, but its buckets are exactly the
frequency bands (A1 is rank <= 500, A2 <= 1500, ... C2 is everything above
7000). The rank already carries that information, so the field is imported as
`r` alone - publishing the derived label as a proficiency claim would be
inventing data the source does not have.
"""

from __future__ import annotations

import argparse
import json
import re
import tarfile
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "lexicon"
CACHE = ROOT / "tools" / ".cache" / "sources"

OPENJAM = "https://raw.githubusercontent.com/amirj4m/openjam/main/data/json"
OPENJAM_FILES = ("words_en.json", "translations_fa.json", "phonetics.json",
                 "word_forms.json")
WN_URL = "https://wordnetcode.princeton.edu/wn3.1.dict.tar.gz"

MAX_SENSES = 4          # the source's longest entry is 8; 4 is past the tail
POS_ORDER = {"noun": 0, "verb": 1, "adjective": 2, "adverb": 3}
PERSIAN_CHAR = re.compile(r"[\u0600-\u06FF]")


def persian_only(text: str) -> str:
    """A Persian column, or nothing at all.

    The translation table is community-built and a handful of its rows hold an
    English gloss or a Chinese string where the meaning should be ("raincoat
    waterproof", "被告"). Passing one through would print something that is not
    a Persian meaning under a Persian label, which is worse than printing
    nothing: the field stays empty and the entry is honest about what it has.
    """
    text = (text or "").strip()
    return text if text and PERSIAN_CHAR.search(text) else ""

# --------------------------------------------------------------- source cache


def fetch(url: str, dest: Path) -> Path:
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        print(f"  downloading {url}")
        with urllib.request.urlopen(url, timeout=300) as r, dest.open("wb") as f:
            f.write(r.read())
    return dest


def openjam_json(name: str):
    path = fetch(f"{OPENJAM}/{name}", CACHE / "openjam" / name)
    return json.loads(path.read_text(encoding="utf-8"))


def wordnet_dir() -> Path:
    base = CACHE / "wordnet"
    if not (base / "data.noun").exists():
        tarball = fetch(WN_URL, CACHE / "wn3.1.dict.tar.gz")
        with tarfile.open(tarball) as tf:
            tf.extractall(base.parent)
        (base.parent / "dict").rename(base)
    return base


# --------------------------------------------------------------------- wordnet
#
# data.<pos> is one synset per line:
#     offset lex_id ss_type w_cnt  word lex_id  [word lex_id ...] |
#     pointer_letter target_offset target_pos source_word target_word ...
#     | gloss
# Synonyms are the other words on the synset's own line. Antonyms are `!`
# pointers, and the target word is picked by the pointer's last field.

WN_POS = {"n": "noun", "v": "verb", "a": "adjective", "s": "adjective",
          "r": "adverb"}


def wordnet_relations(lemmas: set[str]) -> dict[str, dict]:
    """lemma -> {"y": {pos: [synonyms]}, "a": {pos: [antonyms]}}"""
    base = wordnet_dir()
    # offset -> (pos, [words]) so an antonym pointer can be resolved
    synsets: dict[str, tuple[str, list[str]]] = {}
    rows: list[tuple[str, str, list[str], list[tuple[str, str, int, int]]]] = []

    for fname, poskey in (("data.noun", "n"), ("data.verb", "v"),
                          ("data.adj", "a"), ("data.adv", "r")):
        path = base / fname
        if not path.exists():
            raise SystemExit(f"wordnet file missing: {path}")
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line or line.startswith("  "):
                continue          # the licence header
            head, _, _gloss = line.partition(" | ")
            blocks = head.split()
            if len(blocks) < 6:
                continue
            # w_cnt is a two-digit *hexadecimal* count - synsets with eleven
            # words read "0b", not "11"
            offset, _lex, ss_type, w_cnt = (blocks[0], blocks[1], blocks[2],
                                            int(blocks[3], 16))
            words, pos = [], 4
            for _ in range(w_cnt):
                w = blocks[pos].replace("_", " ")
                words.append(w)
                pos += 2
            # A three-digit pointer *count* follows the words, then that many
            # four-field pointers. Reading the count as a pointer is why every
            # antonym used to come back empty.
            try:
                p_cnt = int(blocks[pos])
            except (ValueError, IndexError):
                p_cnt = 0
            pos += 1
            pointers = []
            for _ in range(p_cnt):
                if pos + 3 >= len(blocks):
                    break
                sym = blocks[pos]
                # The fourth field packs both word numbers into four hex
                # digits: "0202" is source word 2 -> target word 2. Reading it
                # as one decimal integer is why every antonym pointer used to
                # resolve to nothing.
                nums = blocks[pos + 3]
                if len(nums) != 4:
                    break
                try:
                    src, tgt = int(nums[:2], 16), int(nums[2:], 16)
                except ValueError:
                    break
                pointers.append((sym, blocks[pos + 1], src, tgt))
                pos += 4
            synsets[offset] = (WN_POS.get(ss_type, poskey), words)
            rows.append((offset, WN_POS.get(ss_type, poskey), words, pointers))

    want = {w.lower() for w in lemmas}
    syn: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    ant: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))

    for offset, pos, words, pointers in rows:
        low = [w.lower() for w in words]
        for i, w in enumerate(low):
            if w not in want:
                continue
            for other in low:
                if other != w and other not in syn[w][pos]:
                    syn[w][pos].append(other)
            for sym, tgt_off, src, tgt in pointers:
                # '!' is an antonym. '&' is "similar to", which WordNet only
                # uses between adjectives - "beautiful" has no other member in
                # its own synset, but it is similar to "beauteous". A learner
                # asking for a synonym means either.
                if sym == "&" and pos == "adjective":
                    target = synsets.get(tgt_off)
                    if target:
                        for other in target[1]:
                            # NOT `low`: that name holds the synset's word list
                            # in the enclosing loop, and shadowing it made the
                            # next iteration walk the letters of one word.
                            near = other.lower()
                            if near != w and near not in syn[w][pos]:
                                syn[w][pos].append(near)
                    continue
                if sym != "!":
                    continue
                target = synsets.get(tgt_off)
                if not target:
                    continue
                t_words = target[1]
                idx = max(0, min(len(t_words) - 1, tgt - 1))
                a = t_words[idx].lower()
                if a != w and a not in ant[w][pos]:
                    ant[w][pos].append(a)

    out: dict[str, dict] = {}
    for w in want:
        row: dict[str, dict] = {}
        if syn.get(w):
            row["y"] = {p: v[:6] for p, v in syn[w].items() if v}
        if ant.get(w):
            row["a"] = {p: v[:6] for p, v in ant[w].items() if v}
        if row:
            out[w] = row
    return out


# ------------------------------------------------------------------ the build

PREFIX_RE = re.compile(r"^[a-z]{2}")

# The same normalisation chatbot.py applies to a Persian word before a lookup:
# unify the Arabic yeh/kaf, drop the zero-width joiners and the harakat, and
# drop every space. A key built with different rules than the reader's would
# never match, and Persian has more spelling variation than English.
FA_MAP = str.maketrans({"ي": "ی", "ك": "ک", "ۀ": "ه", "ة": "ه",
                        "۰": "0", "۱": "1", "۲": "2", "۳": "3",
                        "۴": "4", "۵": "5", "۶": "6", "۷": "7",
                        "۸": "8", "۹": "9",
                        "\u200c": "", "\u200d": "", "\u200e": "",
                        "\u200f": ""})


def norm_fa(text: str) -> str:
    t = text.translate(FA_MAP)
    t = re.sub(r"[\u064b-\u0652\u0670]", "", t)
    return re.sub(r"\s+", "", t).strip()


def shard_name(word: str) -> str:
    return PREFIX_RE.match(word).group(0) if PREFIX_RE.match(word) else word[:1] + "_"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all-examples", action="store_true",
                    help="keep an example for every sense, not just the first "
                         "(adds about 4 MB)")
    args = ap.parse_args()

    print("reading sources")
    words = openjam_json("words_en.json")
    translations = openjam_json("translations_fa.json")
    phonetics = openjam_json("phonetics.json")
    forms = openjam_json("word_forms.json")

    tr_by_sense = {t["sense_id"]: t for t in translations if t.get("sense_id")}
    ipa_by_word: dict[str, dict[str, str]] = defaultdict(dict)
    for p in phonetics:
        if p.get("ipa"):
            ipa_by_word[p["word_id"]][p.get("variant") or "us"] = p["ipa"]
    forms_by_word: dict[str, list[list[str]]] = defaultdict(list)
    for f in forms:
        name = (f.get("form") or "").strip()
        if name:
            forms_by_word[f["word_id"]].append([name, f.get("form_type") or ""])

    print(f"wordnet relations for {len(words)} lemmas")
    rel = wordnet_relations({w["english"] for w in words})

    print("building entries")
    entries: dict[str, dict] = {}
    dropped_no_definition = dropped_duplicate = 0
    stats = {"senses": 0, "fa": 0, "en_examples": 0, "fa_examples": 0,
             "ipa": 0, "synonym_words": 0, "antonym_words": 0, "forms": 0}

    for row in sorted(words, key=lambda r: (r.get("frequency_rank") or 10 ** 9,
                                            r["english"])):
        key = (row.get("english") or "").strip().lower()
        if not key:
            continue
        senses_in = sorted(row.get("senses") or [],
                           key=lambda s: s.get("sense_order") or 0)
        senses = []
        for sense_i, s in enumerate(senses_in[:MAX_SENSES]):
            en_def = (s.get("definition_en") or "").strip()
            if not en_def:
                continue
            pos = s.get("part_of_speech") or ""
            fa = tr_by_sense.get(s.get("id")) or {}
            sense = [pos, en_def]
            meaning = persian_only(fa.get("meaning"))
            example = (s.get("example_en") or "").strip()
            fa_example = persian_only(fa.get("example"))
            # Trailing fields stay empty rather than being dropped, so the
            # array positions mean one fixed thing in both engines.
            sense.append(meaning)
            sense.append(example)
            # One worked example per headword, on its primary sense. Every
            # sense carrying both an English and a Persian sentence cost 4 MB
            # of APK for sentences a learner reads once.
            keep_example = args.all_examples or sense_i == 0
            sense.append(fa_example if keep_example else "")
            if not keep_example:
                sense[3] = ""
            senses.append(sense)
            stats["senses"] += 1
            stats["fa"] += bool(meaning)
            stats["en_examples"] += bool(example)
            stats["fa_examples"] += bool(sense[4])
        if not senses:
            dropped_no_definition += 1
            continue
        if key in entries:
            dropped_duplicate += 1
            continue

        entry: dict = {}
        if row.get("frequency_rank"):
            entry["r"] = row["frequency_rank"]
        pos_list = []
        for s in senses:
            if s[0] and s[0] not in pos_list:
                pos_list.append(s[0])
        pos_list.sort(key=lambda p: POS_ORDER.get(p, 9))
        if pos_list:
            entry["p"] = pos_list
        ipa = ipa_by_word.get(row["id"]) or {}
        if ipa:
            entry["i"] = dict(sorted(ipa.items()))
            stats["ipa"] += 1
        # [form, form_type]: "sought" is only an answer to "past tense of
        # seek" while its type is kept, and the source labels every form.
        seen_forms, word_forms = set(), []
        for name, ftype in forms_by_word.get(row["id"]) or []:
            if name.lower() in seen_forms:
                continue
            seen_forms.add(name.lower())
            word_forms.append([name, ftype])
        if word_forms:
            entry["f"] = word_forms[:8]
            stats["forms"] += len(entry["f"])
        entry["s"] = senses
        relation = rel.get(key) or {}
        if relation.get("y"):
            entry["y"] = {p: v for p, v in sorted(relation["y"].items())
                          if p in pos_list or not pos_list}
            stats["synonym_words"] += sum(len(v) for v in entry["y"].values())
        if relation.get("a"):
            entry["a"] = {p: v for p, v in sorted(relation["a"].items())
                          if p in pos_list or not pos_list}
            stats["antonym_words"] += sum(len(v) for v in entry["a"].values())
        for optional in ("y", "a"):
            if optional in entry and not entry[optional]:
                entry.pop(optional)
        entries[key] = entry

    print(f"  {len(entries)} headwords, {stats['senses']} senses, "
          f"{dropped_no_definition} dropped (no definition), "
          f"{dropped_duplicate} duplicate headwords")

    # ---------------------------------------------------------------- shards
    #
    # Two letters keeps almost every shard small, but English is not spread
    # evenly: "co", "re", "in" and "un" would each be a quarter of a
    # megabyte, and that is one fetch to parse for a single word. Any bucket
    # over SPLIT_AT entries is cut a letter finer, and the loader tries three
    # letters before two.
    SPLIT_AT = 800
    wide = {shard_name(w) for w in entries}
    counts: dict[str, int] = defaultdict(int)
    for key in entries:
        counts[shard_name(key)] += 1
    wide = {p for p in wide if counts[p] > SPLIT_AT}

    def shard_for(word: str) -> str:
        prefix = shard_name(word)
        return word[:3] if prefix in wide and len(word) >= 3 else prefix

    shards: dict[str, dict] = defaultdict(lambda: {"w": {}, "f": {}})
    for key, entry in entries.items():
        shard = shards[shard_for(key)]
        shard["w"][key] = entry
        for form in entry.get("f") or []:
            norm = form[0].strip().lower()
            if norm and norm != key and norm not in shard["f"]:
                shard["f"][norm] = key

    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.json"):
        old.unlink()

    # A Persian question has no prefix to shard on, so the reverse index is one
    # small file, read only when someone asks in Persian. Only single-word
    # meanings can be keys; "بودن (صفت را دنبال می‌کند)" is a gloss, not a
    # lookup key, and turning it into one would invent a headword.
    fa_index: dict[str, list[str]] = {}
    for key, entry in entries.items():
        for sense in entry["s"]:
            meaning = (sense[2] or "").strip()
            if not meaning or " " in meaning or "(" in meaning:
                continue
            bucket = fa_index.setdefault(norm_fa(meaning), [])
            if len(bucket) < 4 and key not in bucket:
                bucket.append(key)
    body = json.dumps({"_readme": "Persian single-word meaning -> English "
                                  "headwords, by first sense order.",
                       "p": dict(sorted(fa_index.items()))},
                      ensure_ascii=False, separators=(",", ":"))
    (OUT / "_fa.json").write_text(body, encoding="utf-8")
    print(f"  Persian reverse index: {len(fa_index)} meanings, "
          f"{len(body.encode('utf-8')) / 1024:.0f} KB")

    total = 0
    for prefix in sorted(shards):
        payload = {
            "_shard": prefix,
            "w": dict(sorted(shards[prefix]["w"].items())),
            "f": dict(sorted(shards[prefix]["f"].items())),
        }
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        (OUT / f"{prefix}.json").write_text(body, encoding="utf-8")
        total += len(body.encode("utf-8"))

    # The shard names, as one small file. English is not spread evenly ("co",
    # "re", "in", "un" carry a quarter of the words), so only some three-letter
    # prefixes have a shard of their own. Without this list the reader has to
    # ask for both candidates and accept a miss, which in the app is a 404 per
    # word per message - noise in the console and a wasted round trip.
    index = {"_readme": "Shard names present in this directory.",
             "names": sorted(shards)}
    (OUT / "_index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    meta = {
        "_readme": (
            "Fluentify's dictionary, generated by tools/build_lexicon.py. Each "
            "shard holds the headwords starting with that two-letter prefix, "
            "the inflected forms that resolve to them, and the Persian "
            "meanings that can be looked up from Persian. Shard layout: "
            "w = headword -> entry, f = form -> headword, p = Persian -> "
            "headwords. Entry layout: r frequency rank, p parts of speech, "
            "i IPA by region, f inflected forms, s senses as "
            "[pos, English definition, Persian meaning, English example, "
            "Persian example] (empty string where the source has none), "
            "y synonyms by part of speech, a antonyms by part of speech. "
            "Nothing here is inferred: a field is present only when the "
            "source provided it."),
        "version": 1,
        "shards": len(shards),
        "shard_names": sorted(shards),
        "persian_index": len(fa_index),
        "headwords": len(entries),
        "senses": stats["senses"],
        "persian_meanings": stats["fa"],
        "english_examples": stats["en_examples"],
        "persian_examples": stats["fa_examples"],
        "ipa_entries": stats["ipa"],
        "inflected_forms": stats["forms"],
        "synonym_words": stats["synonym_words"],
        "antonym_words": stats["antonym_words"],
        "bytes": total,
        "sources": [
            {"name": "OpenJam", "url": "https://github.com/amirj4m/openjam",
             "used_for": "lemmas, senses, definitions, examples, Persian "
                         "sense translations, IPA, inflected forms",
             "licence": "MIT License",
             "notice": "Copyright (c) Openjam contributors. MIT-licensed, "
                       "including the data."},
            {"name": "Princeton WordNet 3.1",
             "url": "https://wordnet.princeton.edu/",
             "used_for": "synonyms and antonyms",
             "licence": "WordNet License (BSD-style), redistribution "
                        "permitted with notice",
             "notice": "WordNet 3.0/3.1 Copyright 2006, 2011 by Princeton "
                       "University. All rights reserved. Provided AS IS, "
                       "without warranty; Princeton makes no representations "
                       "of merchantability or fitness for purpose."},
        ],
        "not_used": [
            "english-persian-dictionary-dataset: no dataset licence, and its "
            "README warns that upstream dictionaries carry unnamed licences.",
            "EnglishToPersianDictionaries: repository is Apache-2.0, but the "
            "individual dictionaries publish no licence of their own.",
            "kaikki.org / Wiktionary: CC BY-SA 4.0, whose share-alike terms "
            "would relicense the whole app's data; also a 3.2 GB extract.",
        ],
    }
    (OUT / "_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print(f"wrote {len(shards)} shards, {total / 1024:.0f} KB of JSON "
          f"({len(entries)} headwords, {stats['senses']} senses, "
          f"{stats['fa']} Persian meanings)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
