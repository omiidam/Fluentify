#!/usr/bin/env python3
"""Build vocab_use.json: the word-knowledge layer the Vocabulary panel reads.

The panel already had two halves of an entry and showed neither of them
together: a headword with a Persian gloss (glossary.json), and, behind a tap,
the dictionary senses and examples (senses.json, vocab_examples.json). What it
did not have was the third dimension the brief calls use - the family, the
collocations, the grammatical patterns, the register, the mistakes - and no
part of it said when a word is due, or whether the learner can do anything
with it.

This file is the merge. It never invents a meaning or a pronunciation: the
senses, the Persian gloss and the IPA come from the files above. What it adds
is the curated layer from tools/vocab_use_src.py, the collocations that
already existed in collocations.json (indexed by the word they belong to), and
two facts read off the IPA - how many syllables the word has, and which one is
stressed.

    python3 tools/build_vocab_use.py
    python3 tools/check_vocab_use.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import vocab_use_src as SRC  # noqa: E402

OUT = ROOT / "vocab_use.json"
BANDS = ["A1", "A2", "B1", "B2", "C1", "C2"]

# IPA vowels, including the length mark's base letters. A diphthong is one
# nucleus, not two, which is the only reason this is a scanner and not a
# character count.
VOWELS = set("aeiouyɑɒɔæəɜɛɪʊʌɐɚɝɞɘɵøœɨʉɯɤ")
DIPHTHONGS = {"aɪ", "eɪ", "ɔɪ", "aʊ", "oʊ", "əʊ", "ɪə", "eə", "ʊə", "ɑɪ", "ɑʊ", "ɔə"}
# A syllabic consonant is a nucleus on its own (button = ˈbʌt.n̩). These are
# two-codepoint sequences - the letter plus U+0329 - so they must be matched as
# strings; a set() of that literal would split into bare l, n, m and r and
# count an extra syllable at every one of them.
SYLLABIC = ("l̩", "n̩", "m̩", "r̩")


def syllables(ipa: str) -> int:
    """How many vowel nuclei the transcription has."""
    s = ipa.replace("ˈ", "").replace("ˌ", "").replace(".", "")
    count, i = 0, 0
    while i < len(s):
        pair = s[i:i + 2]
        if pair in DIPHTHONGS:
            count += 1
            i += 2
            continue
        syllable_consonant = next((x for x in SYLLABIC if s.startswith(x, i)), None)
        if syllable_consonant:
            count += 1
            i += len(syllable_consonant)
            continue
        if s[i] in VOWELS:
            count += 1
        i += 1
    return count


def stress(ipa: str) -> int:
    """Which syllable carries the primary stress, 1-based; 0 if unmarked."""
    at = ipa.find("ˈ")
    if at < 0:
        return 0
    return syllables(ipa[:at]) + 1


def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def domain_index(glossary: dict) -> dict:
    """word -> [{domain, fa, level}], in the order the shelf lists domains."""
    out: dict[str, list] = {}
    for dom_id, dom in glossary["domains"].items():
        if dom_id == "_groups":
            continue
        for pair in dom.get("words") or []:
            name = str(pair[0]).strip()
            out.setdefault(name.lower(), []).append({
                "domain": dom_id,
                "fa": str(pair[1]).strip(),
                "level": dom.get("level", "A1"),
            })
    return out


def collocation_index(entries: list) -> dict:
    """The word each collocation is filed under.

    verb+noun  -> the verb ("make" for "make a decision")
    adj+noun   -> the noun ("rain" for "heavy rain")
    verb+prep  -> the verb ("depend" for "depend on")
    """
    out: dict[str, list] = {}
    for e in entries:
        phrase = str(e.get("phrase") or "").strip()
        if not phrase:
            continue
        words = phrase.split()
        tag = e.get("tag")
        if tag == "adj+noun":
            key = words[-1]
        elif tag == "verb+prep":
            key = words[0]
        else:
            key = str(e.get("answer") or words[0]).strip() or words[0]
        row = {"en": phrase, "fa": e.get("fa") or ""}
        if e.get("example"):
            row["ex"] = e["example"].get("en") or ""
        out.setdefault(key.lower(), []).append(row)
    return out



STOP = set("a an the of to in on at for with and or but".split())


def forms(word: str) -> set:
    """The shapes a headword takes in running text, so a dialogue can say
    "cherries" and still be counted as teaching "cherry"."""
    w = word.lower().strip()
    out = {w, w + "s", w + "es", w + "'s", w + "d", w + "ed", w + "ing"}
    if w.endswith("y"):
        out.add(w[:-1] + "ies")
        out.add(w[:-1] + "ied")
    if w.endswith("e"):
        out.add(w[:-1] + "ing")
        out.add(w[:-1] + "ed")
    return out


def tokens(text: str) -> set:
    cleaned = "".join(c.lower() if (c.isalnum() or c == "'") else " " for c in text)
    return set(cleaned.split())


def dialogue_targets(domain_words: list, text: str) -> list:
    """Which of this domain's own words the dialogue actually says.

    Derived, never hand-picked: a dialogue cannot claim a target it does not
    use, and editing a line immediately changes its targets.
    """
    said = tokens(text)
    flat = text.lower()
    hits = []
    for word in domain_words:
        w = str(word).strip()
        if not w:
            continue
        # "big / large / huge" is one entry with three spellings; any of them
        # counts as the entry being used.
        alternatives = [w] + ([a.strip() for a in w.split("/")] if "/" in w else [])
        found = False
        for alt in alternatives:
            if not alt:
                continue
            if " " in alt:
                found = found or alt.lower() in flat
            else:
                found = found or bool(forms(alt) & said)
        if found:
            hits.append(w)
    return hits


def build_dialogues(glossary: dict, level_of: dict) -> dict:
    """One dialogue per domain, keyed by domain id, with its targets derived."""
    dom_words = {}
    for dom_id, dom in glossary["domains"].items():
        if dom_id == "_groups":
            continue
        dom_words[dom_id] = [str(p[0]) for p in (dom.get("words") or [])]
    out = {}
    for dom_id, spec in SRC.DIALOGUES.items():
        if dom_id not in dom_words:
            raise SystemExit(f"build_vocab_use: dialogue for unknown domain {dom_id}")
        roles = spec["roles"]
        lines = spec["lines"]
        if len(roles) < 2:
            raise SystemExit(f"build_vocab_use: dialogue {dom_id} needs two roles")
        if len(lines) < 4:
            raise SystemExit(f"build_vocab_use: dialogue {dom_id} has fewer than 4 lines")
        text = " ".join(line for _who, line in lines)
        targets = dialogue_targets(dom_words[dom_id], text)
        if len(targets) < 3:
            raise SystemExit(f"build_vocab_use: dialogue {dom_id} uses only "
                             f"{len(targets)} of its own domain words: {targets}")
        q = SRC.QUESTIONS.get(dom_id)
        if not q:
            raise SystemExit(f"build_vocab_use: dialogue {dom_id} has no question")
        prompt, options, answer, why = q
        if len(options) != 3:
            raise SystemExit(f"build_vocab_use: {dom_id} question needs three options")
        if not 0 <= int(answer) < 3:
            raise SystemExit(f"build_vocab_use: {dom_id} question answer is out of range")
        if not str(prompt).strip() or not str(why).strip():
            raise SystemExit(f"build_vocab_use: {dom_id} question is not complete")
        out[dom_id] = {
            "id": "dlg-" + dom_id,
            "domain": dom_id,
            "level": level_of.get(dom_id, "A1"),
            "scenario": {"en": spec["scenario"][0], "fa": spec["scenario"][1]},
            "roles": roles,
            "lines": [{"who": who, "en": line} for who, line in lines],
            "targets": targets,
            "question": {
                "prompt": str(prompt).strip(),
                "options": [str(o).strip() for o in options],
                "answer": int(answer),
                "why": str(why).strip(),
            },
            "note": spec.get("note") or "",
        }
    return out



def main() -> int:
    glossary = load("glossary.json")
    senses = load("senses.json")["words"]
    colls = collocation_index(load("collocations.json")["entries"])
    domains = domain_index(glossary)

    level_of = {k: v.get("level", "A1")
                for k, v in glossary["domains"].items() if k != "_groups"}
    # a word sits at the earliest band it is taught at, which is when the
    # learner first meets it - not the highest domain that happens to list it
    words: dict[str, dict] = {}
    wild_by_word: dict[str, list] = {}
    for passage in SRC.WILD:
        for w in passage["words"]:
            wild_by_word.setdefault(w.lower(), []).append(passage["id"])

    for name, rows in sorted(domains.items()):
        rows = sorted(rows, key=lambda r: BANDS.index(r["level"])
                      if r["level"] in BANDS else 99)
        first = rows[0]
        rec: dict = {
            "w": name,
            "fa": first["fa"],
            "level": first["level"],
            "domains": [r["domain"] for r in rows],
        }
        if len({r["fa"] for r in rows}) > 1:
            # the same word means slightly different things in different
            # domains; the shelf's own gloss for each is kept, in order
            rec["glosses"] = [{"domain": r["domain"], "fa": r["fa"]} for r in rows]
        s = senses.get(name) or {}
        if s.get("ipa"):
            rec["ipa"] = s["ipa"]
            rec["syl"] = syllables(s["ipa"])
            rec["stress"] = stress(s["ipa"])
        if s.get("pos"):
            rec["pos"] = s["pos"][0]
        if colls.get(name):
            rec["colls"] = colls[name]
        if wild_by_word.get(name):
            rec["wild"] = wild_by_word[name]
        extra = SRC.WORDS.get(name)
        if extra:
            for key, value in extra.items():
                if key == "fam":
                    # a family does not contain the headword itself
                    value = [f for f in value if f.get("w", "").lower() != name]
                if value:
                    rec[key] = value
            rec["curated"] = True
        words[name] = rec

    collections = []
    for col in SRC.COLLECTIONS:
        missing = [d for d in col["domains"] if d not in level_of]
        if missing:
            raise SystemExit(f"build_vocab_use: collection {col['id']} names "
                             f"unknown domains {missing}")
        collections.append({
            "id": col["id"], "en": col["en"], "fa": col["fa"],
            "blurb": col["blurb"], "domains": col["domains"],
            "levels": sorted({level_of[d] for d in col["domains"]},
                             key=lambda b: BANDS.index(b) if b in BANDS else 99),
        })

    dialogues = build_dialogues(glossary, level_of)
    uncatalogued = [d for d in level_of if d not in dialogues]
    if uncatalogued:
        raise SystemExit("build_vocab_use: domains with no dialogue "
                         f"{uncatalogued}")
    curated = sum(1 for w in words.values() if w.get("curated"))
    doc = {
        "_meta": {
            "readme": (
                "The word-knowledge base behind the Vocabulary panel. Per word: "
                "the Persian gloss and band it is taught at (glossary.json), its "
                "IPA and syllable/stress count (senses.json, counted by "
                "tools/build_vocab_use.py), the collocations already in "
                "collocations.json, and the curated use layer - family, "
                "patterns, register, mistakes, Persian Bridge, wild passages and "
                "production prompts - from tools/vocab_use_src.py. No meaning, "
                "pronunciation or example is invented here: everything not "
                "authored is copied from a file that already shipped."
            ),
            "built_by": "tools/build_vocab_use.py",
            "sources": [
                {"name": "glossary.json", "what": "gloss + band"},
                {"name": "senses.json", "what": "IPA, parts of speech, senses"},
                {"name": "collocations.json", "what": "natural combinations"},
                {"name": "tools/vocab_use_src.py", "what": "curated use layer"},
            ],
            "bands": BANDS,
        },
        "words": words,
        "bridge": SRC.BRIDGE,
        "wild": SRC.WILD,
        "collections": collections,
        "dialogues": dialogues,
        "stats": {
            "words": len(words),
            "with_ipa": sum(1 for w in words.values() if w.get("ipa")),
            "with_collocations": sum(1 for w in words.values() if w.get("colls")),
            "curated": curated,
            "bridge": len(SRC.BRIDGE),
            "wild": len(SRC.WILD),
            "collections": len(collections),
            "dialogues": len(dialogues),
            "dialogue_targets_min": min((len(d["targets"])
                                        for d in dialogues.values()), default=0),
        },
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    s = doc["stats"]
    print(f"wrote {OUT.name}: {s['words']} words ({s['curated']} curated), "
          f"{s['with_ipa']} with IPA, {s['with_collocations']} with "
          f"collocations, {s['bridge']} bridge traps, {s['wild']} passages")
    print(f"{s['collections']} collections, {s['dialogues']} domain "
          f"dialogues (fewest targets: {s['dialogue_targets_min']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
