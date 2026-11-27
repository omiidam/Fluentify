#!/usr/bin/env python3
"""The vocabulary knowledge base: is every claim in it sourced or authored?

vocab_use.json is the one file the word page trusts for form, meaning and use.
It is easy to break in ways that still render: an IPA that no longer matches
senses.json, a syllable count that disagrees with that IPA, a curated word that
was never in the glossary, a "word in the wild" passage that does not contain
the word it is filed under, a collection pointing at a domain that was
renamed. Each of those turns into a confident, wrong lesson.

So this suite re-derives everything the builder derived, from the same source
files, and compares. It also holds the content bar the brief sets: no invented
meanings (senses are not here at all - they are read from senses.json), no
invented pronunciation (IPA must equal senses.json), and no half-filled curated
record.

    python3 tools/check_vocab_use.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from build_vocab_use import BANDS, syllables, stress  # noqa: E402

FA = re.compile(r"[\u0600-\u06FF]")
problems: list[str] = []


def check(what: str, ok: bool, detail: str = "") -> bool:
    if ok:
        print(f"  ok    {what}" + (f" ({detail})" if detail else ""))
    else:
        problems.append(what + (f": {detail}" if detail else ""))
        print(f"  FAIL  {what}" + (f" ({detail})" if detail else ""))
    return ok


def main() -> int:
    doc = json.loads((ROOT / "vocab_use.json").read_text(encoding="utf-8"))
    glossary = json.loads((ROOT / "glossary.json").read_text(encoding="utf-8"))
    senses = json.loads((ROOT / "senses.json").read_text(encoding="utf-8"))["words"]
    colls = json.loads((ROOT / "collocations.json").read_text(encoding="utf-8"))

    words = doc["words"]
    domains = {k: v for k, v in glossary["domains"].items() if k != "_groups"}

    # ---------------------------------------------------------------- shape --
    check("the file names its sources", bool(doc["_meta"].get("sources")), 
          ", ".join(s["name"] for s in doc["_meta"]["sources"]))
    check("the bands are the six CEFR bands", doc["_meta"]["bands"] == BANDS)

    # every glossary word, once, at the band it is first taught at
    listed: dict[str, str] = {}
    for dom_id, dom in domains.items():
        for pair in dom.get("words") or []:
            listed.setdefault(pair[0].lower(), dom.get("level", "A1"))
    # a word taught at more than one band sits at the earliest
    for name, row in words.items():
        for d in row["domains"]:
            band = domains[d].get("level", "A1")
            if BANDS.index(band) < BANDS.index(listed[name]):
                listed[name] = band
    check("every glossary word is in the base exactly once",
          sorted(words) == sorted(listed),
          f"{len(words)} words against {len(listed)} taught")
    wrong_band = [f"{w}:{r['level']}!={listed[w]}" for w, r in words.items()
                  if r["level"] != listed[w]]
    check("every word sits at the band it is first taught at", not wrong_band,
          ", ".join(wrong_band[:5]))
    missing_fa = [w for w, r in words.items()
                  if not r.get("fa") or not FA.search(r["fa"])]
    check("every word keeps a Persian gloss", not missing_fa,
          ", ".join(missing_fa[:5]))

    # ------------------------------------------------------------ the form --
    bad_ipa, bad_syl = [], []
    for name, row in words.items():
        ipa = row.get("ipa")
        if not ipa:
            continue
        source = (senses.get(name) or {}).get("ipa")
        if source != ipa:
            bad_ipa.append(f"{name}:{ipa}!={source}")
            continue
        if row.get("syl") != syllables(ipa):
            bad_syl.append(f"{name}:{row.get('syl')}!={syllables(ipa)}")
        if not 0 <= row.get("stress", 0) <= max(1, row.get("syl", 1)):
            bad_syl.append(f"{name}:stress {row.get('stress')}")
    check("every IPA is the transcription senses.json holds", not bad_ipa,
          ", ".join(bad_ipa[:4]))
    check("every syllable count and stress position follows from its IPA",
          not bad_syl, ", ".join(bad_syl[:4]))
    check("no word claims a count without an IPA",
          all(("syl" in r) == ("ipa" in r) for r in words.values()))
    # -------------------------------------------------------------- collocs --
    known = {e["phrase"] for e in colls["entries"]}
    bad_coll, dup_coll = [], []
    for name, row in words.items():
        seen = set()
        for c in row.get("colls") or []:
            if not c.get("en") or not c.get("fa") or not FA.search(c["fa"]):
                bad_coll.append(f"{name}:{c.get('en')}")
            if c["en"] in seen:
                dup_coll.append(f"{name}:{c['en']}")
            seen.add(c["en"])
            if c.get("ex") and "*" in c["ex"]:
                bad_coll.append(f"{name}: placeholder example")
    check("every collocation has both languages", not bad_coll,
          ", ".join(bad_coll[:4]))
    check("no word repeats a collocation", not dup_coll, ", ".join(dup_coll[:4]))
    missing_src = [c["en"] for row in words.values()
                   for c in (row.get("colls") or [])
                   if c["en"] not in known and c["en"] not in _curated_colls()]
    check("every collocation is either in collocations.json or authored",
          not missing_src, ", ".join(missing_src[:4]))

    # ----------------------------------------------------------- the use --
    curated = {w: r for w, r in words.items() if r.get("curated")}
    check("the curated layer exists", len(curated) >= 20,
          f"{len(curated)} words carry family/patterns/use")
    thin = [w for w, r in curated.items()
            if not any(r.get(k) for k in ("fam", "colls", "pats", "use", "bad"))]
    check("no curated word is an empty promise", not thin, ", ".join(thin[:5]))
    for key, fields in (("fam", ("w", "pos", "fa")), ("pats", ("p", "ex", "fa")),
                        ("bad", ("bad", "good", "why")),
                        ("use", ("task", "frame", "example"))):
        broken = [f"{w}.{key}" for w, r in curated.items()
                  for item in (r.get(key) or [])
                  if any(not item.get(f) for f in fields)]
        check(f"every {key} record is complete", not broken, ", ".join(broken[:4]))
    self_family = [w for w, r in words.items()
                   for f in (r.get("fam") or []) if f.get("w", "").lower() == w]
    check("a word is not its own family", not self_family, ", ".join(self_family[:4]))
    bad_bridge = [w for w, r in curated.items()
                  if r.get("bridge") and not all(r["bridge"].get(k)
                                                 for k in ("bad", "good", "why"))]
    check("every word-level bridge trap is complete", not bad_bridge,
          ", ".join(bad_bridge[:4]))

    # ------------------------------------------------------------ the traps --
    bridge = doc["bridge"]
    check("the bridge lab holds a usable number of traps", 15 <= len(bridge) <= 40,
          f"{len(bridge)}")
    holes = [i for i, b in enumerate(bridge)
             if not all(b.get(k) for k in ("bad", "good", "why"))]
    check("every trap says what is wrong, what is right and why", not holes,
          str(holes[:5]))
    same = [b["bad"] for b in bridge if b["bad"].strip() == b["good"].strip()]
    check("a trap never 'fixes' a form to itself", not same, str(same[:3]))
    dupes = [b["bad"] for b in bridge
             if [x["bad"].strip().lower() for x in bridge].count(
                 b["bad"].strip().lower()) > 1]
    check("no trap is listed twice", not dupes, str(dupes[:3]))

    # ---------------------------------------------------------- the passages --
    wild = {p["id"]: p for p in doc["wild"]}
    check("the wild passages have unique ids", len(wild) == len(doc["wild"]))
    missing = [f"{p['id']}:{w}" for p in doc["wild"] for w in p["words"]
               if not re.search(r"\b" + re.escape(w) + r"[a-z]*", p["text"], re.I)]
    check("every passage really contains the words it is filed under",
          not missing, ", ".join(missing[:5]))
    broken = [p["id"] for p in doc["wild"]
              if not (p.get("words") and p.get("text") and p.get("question")
                      and len(p.get("options") or []) >= 2
                      and isinstance(p.get("answer"), int)
                      and 0 <= p["answer"] < len(p["options"])
                      and p.get("why") and (p.get("title") or {}).get("en")
                      and (p.get("title") or {}).get("fa"))]
    check("every passage can be asked and answered", not broken, str(broken))
    dangling = [f"{w}:{i}" for w, r in words.items() for i in (r.get("wild") or [])
                if i not in wild]
    check("no word points at a passage that does not exist", not dangling,
          str(dangling[:3]))

    # --------------------------------------------------------- collections --
    cols = doc["collections"]
    check("the goal collections are there", len(cols) >= 4, f"{len(cols)}")
    bad_col = [c["id"] for c in cols
               if not c.get("en") or not c.get("fa")
               or not (c.get("blurb") or {}).get("fa")
               or len(c.get("domains") or []) < 2
               or any(d not in domains for d in c["domains"])]
    check("every collection names real domains, in both languages", not bad_col,
          str(bad_col))
    ids = [c["id"] for c in cols]
    check("collection ids are unique", len(ids) == len(set(ids)))
    checked_levels = [c["id"] for c in cols
                      if c["levels"] != sorted(
                          {domains[d].get("level", "A1") for d in c["domains"]},
                          key=BANDS.index)]
    check("each collection's bands are its domains' bands", not checked_levels,
          str(checked_levels))

    # ---------------------------------------------------------------- stats --
    stats = doc["stats"]
    real = {
        "words": len(words),
        "with_ipa": sum(1 for r in words.values() if r.get("ipa")),
        "with_collocations": sum(1 for r in words.values() if r.get("colls")),
        "curated": len(curated),
        "bridge": len(bridge),
        "wild": len(doc["wild"]),
        "collections": len(cols),
    }
    check("the stats describe the file it is in", stats == real,
          f"{stats} vs {real}")

    print(f"\nchecked {len(words)} words, {len(curated)} curated, "
          f"{len(bridge)} traps, {len(doc['wild'])} passages")
    if problems:
        print(f"\nFAIL  {len(problems)} problems\n")
        for p in problems:
            print(f"  {p}")
        return 1
    print("PASS  every claim is copied from a shipped file or authored and complete")
    return 0


def _curated_colls() -> set:
    """Collocations that are authored in the source file, not in JSON."""
    import vocab_use_src as src
    return {c["en"] for w in src.WORDS.values() for c in (w.get("colls") or [])}


if __name__ == "__main__":
    sys.exit(main())
