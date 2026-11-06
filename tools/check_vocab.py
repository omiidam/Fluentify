#!/usr/bin/env python3
"""The vocabulary panel: seventy domains, and does every one of them answer?

The Vocabulary tile is a list of domains, and each domain is a promise: tap
"Vegetables" and you get vegetables. Nothing enforces that. A domain can keep
its title and lose its words, a Persian gloss can be left empty so Arabic
answers read as blanks, a keyword can be misspelled so the tap falls through to
the tutor's catch-all - and the panel still renders, the button still looks
right, and the learner gets a polite sentence about something else.

So this suite probes each domain **on its own**, in both languages, through the
same `respond()` the page calls: the answer must carry that domain's heading,
its whole word list, and its count, and it must not be one of the fallbacks.
Then it checks the shape the content depends on: every pair is two languages,
no word repeats inside a domain, every level is a CEFR band, and the panel's
groups list every domain exactly once.

    python3 tools/check_vocab.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GLOSSARY = ROOT / "glossary.json"
PAGE = ROOT / "webapp.py"

FA = re.compile(r"[\u0621-\u064A\u066E-\u06D3\u06FA-\u06FF]")
LATIN = re.compile(r"[A-Za-z]")
BANDS = {"A1", "A2", "B1", "B2", "C1", "C2"}

# A domain is a study unit, not a sample: fewer than this and "learn the words
# of this domain" is a page you finish in a minute and never open again.
FLOOR_WORDS = 30

problems: list[str] = []
notes: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> bool:
    if ok:
        print(f"  ok    {label}" + (f" ({detail})" if detail else ""))
    else:
        problems.append(label + (f": {detail}" if detail else ""))
        print(f"  FAIL  {label}" + (f" ({detail})" if detail else ""))
    return ok


def main() -> int:
    doc = json.loads(GLOSSARY.read_text(encoding="utf-8"))
    domains = dict(doc["domains"])
    groups = domains.pop("_groups", [])

    check("the file carries the domains and their panel groups",
          bool(domains) and bool(groups),
          f"{len(domains)} domains in {len(groups)} groups")

    # ------------------------------------------------------------- content --
    thin, empty_fa, no_kw, bad_level = [], [], [], []
    dupes: list[str] = []
    total = 0
    for dom_id, dom in domains.items():
        words = dom.get("words") or []
        total += len(words)
        for key in ("label", "list_label", "keywords"):
            block = dom.get(key) or {}
            for lang in ("en", "fa"):
                if not (block.get(lang) or ""):
                    no_kw.append(f"{dom_id}.{key}.{lang}")
        if dom.get("level") not in BANDS:
            bad_level.append(f"{dom_id}:{dom.get('level')}")
        if len(words) < FLOOR_WORDS:
            thin.append(f"{dom_id}({len(words)})")
        seen = set()
        for pair in words:
            if not isinstance(pair, list) or len(pair) < 2:
                problems.append(f"{dom_id}: malformed row {pair!r}")
                continue
            en, fa = str(pair[0]).strip(), str(pair[1]).strip()
            if not en or not LATIN.search(en):
                problems.append(f"{dom_id}: not an English word {pair!r}")
            if not fa or not FA.search(fa):
                empty_fa.append(f"{dom_id}:{en}")
            key = en.lower()
            if key in seen:
                dupes.append(f"{dom_id}:{en}")
            seen.add(key)

    check("every domain is a study unit, not a sample", not thin,
          ", ".join(thin) if thin else f"floor {FLOOR_WORDS}, smallest "
          f"{min(len(d['words']) for d in domains.values())}")
    check("every word carries its Persian", not empty_fa,
          ", ".join(empty_fa[:6]) if empty_fa else f"{total} pairs")
    check("no word repeats inside a domain", not dupes,
          ", ".join(dupes[:6]) if dupes else "0 duplicates")
    check("every domain names itself in both languages and has keywords",
          not no_kw, ", ".join(no_kw[:6]))
    check("every domain sits on a CEFR band", not bad_level,
          ", ".join(bad_level) if bad_level else "A1 → C2")

    listed = [d for g in groups for d in (g.get("domains") or [])]
    check("the panel lists every domain exactly once",
          sorted(listed) == sorted(domains) and len(listed) == len(set(listed)),
          f"{len(listed)} rows for {len(domains)} domains")
    for g in groups:
        for lang in ("en", "fa"):
            if not (g.get(lang) or "").strip():
                problems.append(f"group without a {lang} name: {g.get('id')}")

    # -------------------------------------------------------------- probing --
    # The real test: ask the bot for each domain by the keyword the panel sends,
    # in both languages, and read the answer the way a learner would.
    sys.path.insert(0, str(ROOT))
    from chatbot import ChatBot  # noqa: E402  (after the path is set)

    bot = ChatBot()
    misses, short, wrong = [], [], []
    for dom_id, dom in domains.items():
        words = dom["words"]
        for lang in ("en", "fa"):
            keyword = (dom["keywords"].get(lang) or [""])[0]
            if not keyword:
                continue
            reply = bot.respond(keyword)
            heading = dom["list_label"][lang]
            if heading not in reply:
                # The keyword answered something else - or nothing at all.
                (wrong if reply.strip() else misses).append(f"{dom_id}/{lang}")
                continue
            missing = [en for en, fa in ((w[0], w[1]) for w in words)
                       if (fa if lang == "fa" else en) not in reply]
            if missing:
                short.append(f"{dom_id}/{lang}:{len(missing)}")
    check("every domain answers to its own keyword", not wrong and not misses,
          ", ".join((wrong + misses)[:8]) if (wrong or misses)
          else f"{len(domains) * 2} probes")
    check("every domain's answer carries its whole word list", not short,
          ", ".join(short[:8]) if short else "all pairs printed")
    check("the fallback never answers a domain", not wrong,
          ", ".join(wrong[:8]))

    # A domain's heading carries its count, and the count is the list's length.
    count_bad = []
    for dom_id, dom in domains.items():
        reply = bot.respond(dom["keywords"]["en"][0])
        m = re.match(rf"{re.escape(dom['list_label']['en'])} \((\d+)\):", reply)
        if not m or int(m.group(1)) != len(dom["words"]):
            count_bad.append(dom_id)
    check("the heading's count is the number of words printed", not count_bad,
          ", ".join(count_bad[:8]))

    # The offline build reads the same file, so it must reach the same words.
    apk = ROOT / "android/app/src/main/assets/www/data/glossary.json"
    if apk.exists():
        same = json.loads(apk.read_text(encoding="utf-8"))["domains"]
        def counts(block: dict) -> dict:
            return {k: len(v["words"]) for k, v in block.items()
                    if k != "_groups"}

        web, offline = counts(domains), counts(same)
        check("the APK bundle carries the same domains", web == offline,
              f"{len(web)} domains, the same counts in both" if web == offline
              else f"web {len(web)}, APK {len(offline)} domains; counts differ")
    else:
        notes.append("the APK bundle has not been built; run build_apk_ui.py")

    print()
    if notes:
        print("  note  " + "\n        ".join(notes))
    if problems:
        print(f"\n{len(problems)} problem(s) with the vocabulary domains")
        for p in problems:
            print("   - " + p)
        return 1
    print(f"PASS  {len(domains)} domains, {total} words, "
          f"{len(domains) * 2} keyword probes, all answered in full")
    return 0


if __name__ == "__main__":
    sys.exit(main())
