#!/usr/bin/env python3
"""Vocabulary Discover: four shortcuts, three sections, one dialogue per domain.

The section had a dialogue list that belonged to nobody, collections that
opened the whole shelf, and dialogues that were one generic conversation with
the nouns swapped. This suite checks the relationships themselves, in the file
the page reads:

  shortcuts   the four shortcuts are Discover, Review, Practice, Progress, in
              that order, each with its own icon
  sequence    Discover opens on collections plus the whole directory, then a
              collection's domains, then the domain's dialogue, its question
              and its new words, then the words, then meaning and examples
  coverage    every domain has one dialogue and no domain has two; every
              collection names only real domains, and together the collections
              cover the whole shelf
  dialogue    a dialogue is a real conversation - two roles, at least four
              lines, a scenario nobody else uses, and a script nobody else has
  targets     its target words are the domain's own words, actually said in
              the lines, re-derived here rather than trusted
  filtering   a collection page renders only the ids it names, and the shelf
              is hidden on it - no fallback to the global directory

    python3 tools/check_vocab_dialogues.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import build_vocab_use as BUILD  # noqa: E402
import vocab_use_src as SRC  # noqa: E402

KB = ROOT / "vocab_use.json"
GLOSS = ROOT / "glossary.json"
WEBAPP = ROOT / "webapp.py"

problems: list[str] = []


def check(ok: bool, what: str, detail: str = "") -> bool:
    if not ok:
        problems.append(f"{what}" + (f" ({detail})" if detail else ""))
        print(f"  FAIL  {what}" + (f"  {detail}" if detail else ""))
    else:
        print(f"  ok    {what}")
    return ok


def flat(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", text.lower())).strip()


def main() -> int:
    kb = json.loads(KB.read_text(encoding="utf-8"))
    gloss = json.loads(GLOSS.read_text(encoding="utf-8"))["domains"]
    domains = {k: v for k, v in gloss.items() if k != "_groups"}
    dl = kb.get("dialogues") or {}
    cols = kb.get("collections") or []
    words = kb["words"]
    src = WEBAPP.read_text(encoding="utf-8")

    print("shortcuts and sequence")
    order = ["Discover", "Review", "Practice", "Progress"]
    chips = re.search(r"box\.appendChild\(chips\(view, \[(.*?)\],\s*\(", src, re.S)
    labels = re.findall(r"'([^']*) (Discover|Review|Practice|Progress)'", chips.group(1)) if chips else []
    check(bool(chips), "the tab row is built from one list")
    check([b for _a, b in labels] == order, "the four shortcuts are in the required order",
          str(labels))
    check(all(a.strip() for a, _b in labels), "each shortcut has its own icon",
          str([a for a, _b in labels]))
    # the page order the section asks for: collections, then domains, then the
    # domain's dialogue + question + new words, then the words, then the word
    home = src.index("function homePage(body)")
    coll = src.index("sectionHead('', 'Collections'", home)
    allb = src.index("el('button', 'vldomall')", coll)
    check(coll < allb, "Discover opens on the collections, then the whole directory")
    check(src.find("el('button', 'vldomall')") > 0, "there is an all-domains way in")
    dpage = src.index("function domainPage(body, id)")
    d1 = src.index("sectionHead('1', 'Dialogue'", dpage)
    d2 = src.index("sectionHead('2', 'Question about the dialogue'", d1)
    d3 = src.index("sectionHead('3', 'New words'", d2)
    d4 = src.index("sectionHead('4', 'Words'", d3)
    check(d1 < d2 < d3 < d4,
          "a domain page is dialogue, question, new words, then the words")
    check("Vocab.openDomain(dom, () => {" in src,
          "the words of a domain open as the next page, with a way back")

    print("\ncoverage")
    check(sorted(dl) == sorted(domains), "every domain has exactly one dialogue",
          f"missing {sorted(set(domains) - set(dl))} extra {sorted(set(dl) - set(domains))}")
    check(len(cols) >= 2, "there is more than one collection", str(len(cols)))
    seen: dict[str, list] = {}
    for col in cols:
        check(bool(col.get("domains")), f"collection {col['id']} maps domains")
        check(len(set(col["domains"])) == len(col["domains"]),
              f"collection {col['id']} lists no domain twice")
        bad = [d for d in col["domains"] if d not in domains]
        check(not bad, f"collection {col['id']} names only real domains", str(bad))
        check(bool((col.get("blurb") or {}).get("en")), f"collection {col['id']} has a description")
        for d in col["domains"]:
            seen.setdefault(d, []).append(col["id"])
    uncovered = [d for d in domains if d not in seen]
    check(not uncovered, "together the collections cover every domain", str(uncovered))
    check(all(len(v) == len(set(v)) for v in seen.values()), "no domain repeats inside a collection")

    print("\ndialogue")
    scenarios = {}
    scripts = {}
    for dom, d in sorted(dl.items()):
        check(d.get("domain") == dom, f"{dom}: id and key agree")
        check(d.get("level") == domains[dom].get("level", "A1"),
              f"{dom}: the band is the domain's band", d.get("level"))
        check(len(d.get("roles") or []) >= 2, f"{dom}: at least two participants")
        check(len(d.get("lines") or []) >= 4, f"{dom}: at least four lines",
              str(len(d.get("lines") or [])))
        check(all(line.get("who") in d["roles"] for line in d["lines"]),
              f"{dom}: every speaker is a declared role")
        check(all(line.get("en", "").strip() for line in d["lines"]),
              f"{dom}: no empty lines")
        check(bool(d["scenario"]["en"].strip()) and bool(d["scenario"]["fa"].strip()),
              f"{dom}: a scenario in both languages")
        scenarios.setdefault(flat(d["scenario"]["en"]), []).append(dom)
        scripts.setdefault(flat(" ".join(l["en"] for l in d["lines"])), []).append(dom)
        # targets are re-derived, never trusted
        text = " ".join(l["en"] for l in d["lines"])
        own = [str(p[0]) for p in domains[dom]["words"]]
        derived = BUILD.dialogue_targets(own, text)
        check(derived == d.get("targets"),
              f"{dom}: the targets are the domain words the lines use",
              f"{d.get('targets')} vs {derived}")
        check(len(d.get("targets") or []) >= 3, f"{dom}: at least three target words",
              str(len(d.get("targets") or [])))
        check(all(t in own for t in d.get("targets") or []),
              f"{dom}: every target belongs to the domain")
        said = BUILD.tokens(text)
        lower = text.lower()

        def used(target: str) -> bool:
            """A target is used when one of its spellings is - "big / large"
            counts when the line says "big", not only when it says both."""
            for alt in [target] + ([x.strip() for x in target.split("/")] if "/" in target else []):
                if not alt:
                    continue
                if " " in alt and alt.lower() in lower:
                    return True
                if " " not in alt and BUILD.forms(alt) & said:
                    return True
            return False

        check(all(used(t) for t in d.get("targets") or []),
              f"{dom}: every target is said in the lines")
        check(all(t.lower() in words for t in d.get("targets") or []),
              f"{dom}: every target is a word in the knowledge base")
    prompts = {}
    for dom, d in sorted(dl.items()):
        q = d.get("question") or {}
        opts = q.get("options") or []
        check(bool(str(q.get("prompt") or "").strip()),
              f"{dom}: the dialogue has a question")
        check(len(opts) == 3, f"{dom}: the question has three options", str(len(opts)))
        check(isinstance(q.get("answer"), int) and 0 <= q["answer"] < len(opts),
              f"{dom}: the answer points at one option", str(q.get("answer")))
        check(bool(str(q.get("why") or "").strip()),
              f"{dom}: the question explains its answer")
        check(len({o.strip().lower() for o in opts}) == len(opts),
              f"{dom}: the options are not the same")
        prompts.setdefault(flat(str(q.get("prompt") or "")), []).append(dom)
    dupq = {k: v for k, v in prompts.items() if len(v) > 1}
    check(not dupq, "no two domains ask the same question", str(dupq))

    shared = {k: v for k, v in scenarios.items() if len(v) > 1}
    check(not shared, "no two domains share a scenario", str(shared))
    same = {k: v for k, v in scripts.items() if len(v) > 1}
    check(not same, "no two domains share a script", str(list(same.values())))

    print("\nfiltering")
    check("col.domains.forEach((id) => {" in src and "if (byId[id]) grid.appendChild" in src,
          "a collection page renders only the ids it maps")
    check("Missing from the shelf:" in src,
          "a mapped domain that is missing is reported, not replaced")
    check("This collection names no domain that exists in the shelf." in src,
          "an empty collection says so")
    check("if (shelfBox) shelfBox.hidden = true;" in src,
          "the adult Discover pages do not borrow the shelf")
    check("function setChrome(label, fn)" in src and 'id="vchrome"' in src,
          "the way back sits in the panel header, above the scrolling page")
    check("else if (route.kind === 'all') setChrome('Contents', backToHome);" in src,
          "the all-domains page returns to the contents page without a reload")
    check('class="pchrome" id="vchrome"' in src and
          'if (pageCtl) tools.appendChild(pageCtl);' in src and
          'class="psearch vsearchrow"' not in src,
          "the way back is a chip beside the search pill, never inside it")
    check("b.title = 'Back to ' + label;" in src and
          'class="pchrome" id="vchrome"' in src,
          "the way back is a glyph with a tooltip, not a word")
    check('.ptools.hasback { justify-content: flex-start; }' in src and
          "input.setAttribute('aria-label', placeholder);" in src and
          "input.placeholder = placeholder;" not in src,
          "the header row is three steady icons and the search keeps only its label")
    check("if (painted) return;" in src,
          "a search keystroke re-reads the shelf without repainting the page")
    check("if (route.kind === 'all') paint(search.value);" in src,
          "the all-domains page filters its own cards as the learner types")
    check("Vocab.showOnly" not in src.split("function openCollection")[1][:400]
          if "function openCollection" in src else True,
          "opening a collection does not fall back to filtering the shelf")
    check("openDomainPage(d, from)" in src,
          "a domain card opens the domain page and remembers where it came from")

    print(f"\nchecked {len(dl)} dialogues over {len(cols)} collections "
          f"and {len(domains)} domains")
    if problems:
        print(f"\nFAIL  {len(problems)} problems\n")
        for p in problems:
            print(f"  {p}")
        return 1
    print("PASS  collections, then domains, then a dialogue with its question, "
          "then the words - one distinct dialogue per domain")
    return 0


if __name__ == "__main__":
    sys.exit(main())
