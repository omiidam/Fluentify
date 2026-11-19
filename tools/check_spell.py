#!/usr/bin/env python3
"""Is the composer's spelling layer complete, offline, and wired to the field?

    python3 tools/check_spell.py

What this can prove without a browser:

  * the dictionary is here, is the one build_spell.py compiles, and carries
    both the Hunspell affix rules and Fluentify's own taught words;
  * the checker is nspell, bundled into one local script - no CDN, no API, no
    key, nothing that needs a network on a plane;
  * the page loads that script before its own, keeps a real textarea (so the
    platform's own long-press selection and clipboard still work), and draws
    the lines from a mirror rather than by replacing the field;
  * the rules include the pair the brief is built around - "I will meat you
    tomorrow" - and mark the wrong word, not the phrase around it;
  * nothing is replaced while typing: the learner has to open the card and
    choose, which is the point of a learning app;
  * Ignore lasts the session and only the personal dictionary is written to
    storage, so a tap cannot quietly rewrite what the word list says.

What it cannot prove - and a browser still has to - is that the lines sit
under the right glyphs in every font size, and that a tap lands on the word
under the finger on a real phone.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = (ROOT / "webapp.py").read_text(encoding="utf-8")
APK = (ROOT / "build_apk_ui.py").read_text(encoding="utf-8")

fails: list[str] = []
passes = 0


def check(label: str, ok: bool, why: str = "") -> None:
    global passes
    if ok:
        passes += 1
    else:
        fails.append(f"{label}" + (f" — {why}" if why else ""))


def html() -> str:
    m = re.search(r'HTML_TEMPLATE = r"""(.*?)"""', PAGE, re.S)
    if not m:
        print("could not find HTML_TEMPLATE in webapp.py")
        raise SystemExit(1)
    return m.group(1)


page = html()

# ---------------------------------------------------------------- dictionary --
aff = ROOT / "spell" / "en_US.aff"
dic = ROOT / "spell" / "en_US.dic"
check("the Hunspell affix rules are in the repository", aff.exists())
check("the Hunspell word list is in the repository", dic.exists())

if aff.exists() and dic.exists():
    aff_text = aff.read_text(encoding="utf-8")
    dic_lines = dic.read_text(encoding="utf-8").strip().splitlines()
    check("the affix file declares UTF-8, so Persian-adjacent text cannot mangle",
          "SET UTF-8" in aff_text, "an 8-bit dictionary would drop the ’ conversion")
    check("the word list is a dictionary, not a sample",
          len(dic_lines) > 40_000, f"{len(dic_lines)} entries")
    check("the affix file carries the English rules the forms depend on",
          "SFX" in aff_text and "PFX" in aff_text,
          "without SFX/PFX, walked and studies are not words")

    built = ROOT / "spell.json"
    check("spell.json has been built", built.exists(),
          "run python3 tools/build_spell.py")
    if built.exists():
        doc = json.loads(built.read_text(encoding="utf-8"))
        check("spell.json carries the affix rules the repository holds",
              doc.get("aff") == aff_text,
              "a stale spell.json is a dictionary the page checks against "
              "but nobody can see - rebuild it")
        check("spell.json carries the word list the repository holds",
              doc.get("dic", "").strip() == dic.read_text(encoding="utf-8").strip(),
              "rebuild spell.json")
        extra = set(doc.get("extra") or [])
        for word in ("punctual", "temperament", "fluentify"):
            check(f"{word} is recognised as Fluentify vocabulary",
                  word in extra,
                  "taught words must not be underlined as mistakes")
        check("the taught vocabulary is large enough to matter",
              len(extra) > 4000, f"{len(extra)} words")

# ------------------------------------------------------------------ the code --
check("the checker is nspell", (ROOT / "spell" / "nspell.js").exists())
if (ROOT / "spell" / "nspell.js").exists():
    js = (ROOT / "spell" / "nspell.js").read_text(encoding="utf-8", errors="replace")
    # The license header carries a URL and that is fine; what must not be here
    # is code that would call out when the page runs.
    check("nspell is bundled as one local script",
          "NSpell" in js and not re.search(
              r"\bfetch\(|XMLHttpRequest|WebSocket|sendBeacon", js),
          "a CDN or an API would stop working offline")
    check("the bundle is a library, not a corpus",
          len(js) < 80_000, f"{len(js)} bytes")

check("the page loads the checker before its own script",
      '<script src="spell.js"></script>' in page
      and page.index('<script src="spell.js"></script>')
      < page.index("<script>\n/* Fluentify's mascot"),
      "after the page script, the first keystroke would race the loader")
check("the field is still a textarea", '<textarea id="input"' in page)
composer = re.search(r'<textarea id="input".*?>', page, re.S)
check("the field never turns the platform's own spellcheck off",
      composer is not None and 'spellcheck="false"' not in composer.group(0)
      and "getElementById('input').spellcheck" not in page,
      "Android's keyboard checker is the other half of this feature; the "
      "account fields and the quest answer box may opt out, the composer must not")
check("a mirror sits behind the field for the lines",
      'class="spellmirror"' in page and ".spellmirror {" in page,
      "a textarea cannot hold spans, so the text is drawn twice")
check("the mirror cannot take a tap or a selection",
      re.search(r"\.spellmirror \{[^}]*pointer-events: none", page) is not None
      and re.search(r"\.spellmirror \{[^}]*user-select: none", page) is not None,
      "it is decoration; the field under it owns the pointer")
check("the spelling line is red and wavy",
      re.search(r"\.spellmirror \.miss \{[^}]*text-decoration-style: wavy", page) is not None
      and       re.search(r"\.spellmirror \.miss \{[^}]*text-decoration-color: var\(--spell-bad",
                page) is not None)
check("the contextual line is told apart from the spelling one",
      re.search(r"\.miss\.ctxt \{ text-decoration-color: var\(--spell-ctx", page) is not None,
      "a wrong word that is spelled right is a different mistake")
check("both lines have a value in the light and the dark palette",
      page.count("--spell-bad:") >= 2 and page.count("--spell-ctx:") >= 2,
      "a hard-coded red is invisible in one of the two themes")
check("the dictionary is read through loadJSON, so both builds find it",
      "loadJSON('spell')" in page,
      "the APK rewrites loadJSON to data/*.json; anything else would be web-only")

# the module itself
m = re.search(r"const Spell = \(\(\) => \{(.*?)\n\}\)\(\);", page, re.S)
check("the checker is a self-contained module", m is not None)
if m:
    mod = m.group(1)
    check("nothing in the checker reaches the network",
          not re.search(r"fetch\('https?:|XMLHttpRequest|WebSocket", mod),
          "this feature must work with the radio off")
    check("only the personal dictionary is written to storage",
          mod.count("localStorage.setItem") == 1
          and "fluentify.spell.words" in mod,
          "Ignore is a session decision, not a setting")
    check("a misspelled word offers at most three suggestions",
          ".slice(0, 3)" in mod)
    check("the card offers Replace, Ignore and Add to my words",
          "Ignore — نادیده بگیر" in mod and "Add to my words — افزودن" in mod)
    check("the wrong half of a meat/meet sentence is what gets underlined",
          re.search(r"label: 'meat / meet', at: \d", mod) is not None,
          "the rule has to read the words around it, the line goes under one")
    check("an apostrophe is what someone types, not a typographic one",
          "replace(/’/g, \"'\")" in mod,
          "the dictionary has no ’ in it; the keyboard does")
    check("names, addresses and abbreviations are left alone",
          "https?:\\/\\/" in mod and "@" in mod and "toUpperCase()" in mod,
          "a name is not a mistake")
    check("a capital mid-sentence is treated as a name",
          "const fresh" in mod and "/[.!?:\\n\\r]$/" in mod,
          "Ali and Tehran are not misspellings; a capital at a full stop is checked")
    check("a tap opens the card, a long press is left to the selection",
          "Date.now() - pressAt > 650" in mod,
          "the platform's own selection handles must keep the long press")
    check("nothing is replaced from an input event",
          re.search(r"function schedule\(\) \{\s*clearTimeout\(timer\);\s*"
                    r"timer = setTimeout\(refresh, 140\);\s*\}", mod) is not None
          and re.search(r"function schedule\(\) \{[^}]*apply\(", mod) is None,
          "typing must never rewrite the learner's words")

# corrections.json is the app's own knowledge, not a second hand-written list
check("the tutor's correction rules are reused",
      "fromCorrections" in page and "corrections" in page,
      "the composer and the tutor should teach the same corrections")

# --------------------------------------------------------------- the APK side --
check("the APK gets the checker itself",
      'shutil.copyfile(ROOT / "spell" / "nspell.js"' in APK,
      "the offline page loads spell.js from its own assets")
check("the APK carries the dictionary",
      '"spell.json"' in APK,
      "the offline page has no /api/spell to ask")
check("the dictionary is not on the boot path",
      APK.index('"spell.json"') > APK.index("LAZY_DATA = ["),
      "971 KB behind a loading screen is a slow start for a word nobody typed")

for f in fails:
    print(f"  FAIL {f}")
print(f"\n{'PASS' if not fails else 'FAIL'} all {passes + len(fails)} spell checks"
      f" ({passes} passed" + (f", {len(fails)} failed)" if fails else ")"))
sys.exit(1 if fails else 0)
