#!/usr/bin/env python3
"""Builds spell.json: the English dictionary the composer's red lines use.

One file, read the same way by the web page and the APK (loadJSON('spell')), so
the two builds cannot disagree about what a word is. It carries:

  aff    the Hunspell affix rules from spell/en_US.aff
  dic    the Hunspell word list from spell/en_US.dic
  extra  the words Fluentify itself teaches, so "punctual", "temperament" and
         the inflections in word_arch.json are never underlined as mistakes

The dictionary is nspell's own input format; nspell applies the affixes, so
"walked", "studies" and "redder" are recognised without the list containing
them. Both files are the SCOWL en_US set (see spell/README.md), which is why
this needs no network at build time or at run time.

    python3 tools/build_spell.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPELL = ROOT / "spell"
OUT = ROOT / "spell.json"

# A word the page should treat as English even though the dictionary has never
# heard of it: the app's own name, the places its sentences keep naming, and the
# script names a learner types when they ask about them.
ALWAYS = [
    "fluentify", "tehran", "iran", "iranian", "persian", "farsi", "nowruz",
    "yaldā", "yazd", "isfahan", "esfahan", "shiraz", "tabriz", "mashhad",
    "telegram", "whatsapp", "instagram", "youtube", "google", "android",
    "iphone", "wifi", "wi-fi", "email", "online", "offline", "ok", "okay",
]

WORD = re.compile(r"[A-Za-z][A-Za-z'\-]*$")


def main() -> None:
    aff = (SPELL / "en_US.aff").read_text(encoding="utf-8")
    dic = (SPELL / "en_US.dic").read_text(encoding="utf-8")

    extra: set[str] = set(ALWAYS)
    arch = json.loads((ROOT / "word_arch.json").read_text(encoding="utf-8"))
    for entry in arch.get("words", {}).values():
        for word in [entry.get("en", "")] + [
            f.get("f", "") for f in entry.get("forms", []) or []
        ]:
            word = (word or "").strip()
            if WORD.match(word):
                extra.add(word.lower())

    payload = {"v": 1, "aff": aff, "dic": dic, "extra": sorted(extra)}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
                   encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB, "
          f"{len(extra)} taught words)")


if __name__ == "__main__":
    main()
