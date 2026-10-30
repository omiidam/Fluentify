#!/usr/bin/env python3
"""The slang and idiom bank: is it sound, bilingual, and wired to the chat?

slang.json is assembled from four sources by tools/build_slang.py, and every
way that assembly can go wrong is silent. A term whose Persian gloss was never
written still answers, just in English only. An idiom whose meaning was peeled
off its Wiktionary article title still matches, just wrongly. A row the source
marked mature can arrive in a language tutor's bot because one filter compared
a string to a bool. None of that raises; it ships.

So this suite checks the content against the promises the file makes about
itself, then checks that the two engines actually read it: the Python bot and
the offline bot.js, which have to answer the same way or the app teaches one
thing on the web and another on the phone.

    python3 tools/check_slang.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANK = ROOT / "slang.json"
BUILDER = ROOT / "tools/build_slang.py"
AUTHORED = ROOT / "tools/slang_fa.json"
PY = ROOT / "chatbot.py"
JS = ROOT / "android/app/src/main/assets/www/bot.js"
BUILD = ROOT / "build_apk_ui.py"
ENGINE_JS = ROOT / "tools/js_engine.js"

FA = re.compile(r"[\u0621-\u064A\u066E-\u06D3\u06FA-\u06FF]")
LATIN = re.compile(r"[A-Za-z]")
REGS = {"informal", "slang", "formal", "neutral", "idiom", "archaic"}
CATS = {"internet", "social", "communication", "workplace", "texting",
        "gaming", "regional", "fandom", "digital", "aesthetics", "pets"}

# What the build is expected to have taken from each source. The floors are
# what the sources hold today, not aspirations: a drop means a filter started
# eating rows, and the reply for those terms quietly became a miss.
FLOOR_SLANG = 330
FLOOR_SLANG_FA = 320
FLOOR_IDIOMS = 2800
FLOOR_FA_IDIOMS = 190

problems: list[str] = []


def fail(what: str) -> None:
    problems.append(what)


def check(ok: bool, what: str) -> bool:
    if not ok:
        fail(what)
    return ok


def check_bank(data: dict) -> dict:
    meta = data.get("_meta") or {}
    counts = meta.get("counts") or {}
    slang = data.get("slang") or []
    idioms = data.get("idioms") or []
    fa_idioms = data.get("fa_idioms") or []

    check(bool(meta.get("sources")), "the bank does not record where it came from")
    names = " ".join(s.get("name", "") for s in meta.get("sources") or [])
    for source in ("SlangLane", "IdiomX", "Idiom_Translation", "DadmaTools"):
        check(source in names, f"{source} is not credited in the bank's sources")
    for s in meta.get("sources") or []:
        check(bool(s.get("license")), f"{s.get('name')} has no licence recorded")

    check(len(slang) >= FLOOR_SLANG,
          f"only {len(slang)} slang terms, the source holds {FLOOR_SLANG}+")
    check(sum(1 for s in slang if s.get("fa")) >= FLOOR_SLANG_FA,
          "too few slang terms carry a Persian gloss - the bank is bilingual "
          "in name only")
    check(len(idioms) >= FLOOR_IDIOMS, f"only {len(idioms)} idioms in the bank")
    check(len(fa_idioms) >= FLOOR_FA_IDIOMS,
          f"only {len(fa_idioms)} Persian idioms in the bank")

    for key, actual in (("slang", len(slang)), ("idioms", len(idioms)),
                        ("fa_idioms", len(fa_idioms))):
        if key in counts:
            check(counts[key] == actual,
                  f"_meta says {counts[key]} {key} but the file holds {actual}")

    # The source's register is a phrase, and the build reduces it to a key. A
    # substring test over those phrases labelled every "informal" term as
    # "formal" once, because "informal" contains "formal"; the bank has to
    # look like the thing it describes.
    regs = {"informal": 0, "slang": 0, "formal": 0, "neutral": 0}
    for row in slang:
        regs[row.get("reg", "")] = regs.get(row.get("reg", ""), 0) + 1
    check(regs.get("formal", 0) < len(slang) // 2,
          f"{regs.get('formal', 0)} of {len(slang)} slang terms are labelled "
          "formal: the register mapping is matching the wrong substring")
    check(regs.get("informal", 0) + regs.get("slang", 0) > len(slang) // 2,
          "most of the bank is not marked informal or slang")

    seen: dict[str, str] = {}
    for row in slang:
        term = row.get("t") or ""
        label = f"slang {term!r}"
        check(bool(term), "a slang row has no term")
        check(term.lower() not in seen,
              f"{label} appears twice (also as {seen.get(term.lower())})")
        seen[term.lower()] = label
        check(bool(row.get("en")), f"{label} has no English gloss")
        check(row.get("reg") in REGS,
              f"{label} has register {row.get('reg')!r}")
        check(row.get("cat") in CATS,
              f"{label} has category {row.get('cat')!r}")
        fa = row.get("fa") or ""
        if fa:
            check(bool(FA.search(fa)), f"{label} has a Persian gloss with no "
                                       "Persian letters in it")
            # a gloss may carry the English it is translating in brackets —
            # "دور از کیبورد (away from keyboard)" is the point, not the bug —
            # but the Persian part itself must be Persian
            check(not LATIN.search(re.sub(r"\([^)]*\)", "", fa)),
                  f"{label} has a Latin gloss where Persian was expected: {fa!r}")

    seen_i: dict[str, int] = {}
    for row in idioms:
        en = row.get("en") or ""
        label = f"idiom {en!r}"
        check(bool(en), "an idiom row has no headword")
        low = en.lower()
        check(seen_i.get(low, 0) < 1, f"{label} appears twice")
        seen_i[low] = seen_i.get(low, 0) + 1
        check(bool(row.get("meaning") or row.get("exfa")),
              f"{label} has neither a meaning nor a translated example")
        check(row.get("reg") in REGS, f"{label} has register {row.get('reg')!r}")
        check(len(en.split()) <= 8, f"{label} is a sentence, not an idiom")
        if row.get("fa"):
            check(bool(FA.search(row["fa"])), f"{label} has a Persian gloss "
                                              "with no Persian letters")
        if row.get("exfa"):
            check(bool(FA.search(row["exfa"])),
                  f"{label} has a Persian example with no Persian letters")

    for row in fa_idioms:
        fa = row.get("fa") or ""
        label = f"Persian idiom {fa!r}"
        check(bool(FA.search(fa)), f"{label} has no Persian letters")
        # the corpus calls them idioms, and some are single colloquial words
        # ("عمرا", "زارت"): the bank carries them the way people say them
        check(len(fa) >= 3, f"{label} is too short to be a phrase")
        check(bool(row.get("exfa")), f"{label} has no example sentence")
        check(bool(LATIN.search(row.get("exen") or "")),
              f"{label} has no English rendering")

    return {"slang": len(slang), "fa": sum(1 for s in slang if s.get("fa")),
            "idioms": len(idioms), "fa_idioms": len(fa_idioms)}


def check_curation(data: dict) -> None:
    """A tutor is not an archive: the terms the build leaves out stay out."""
    builder = BUILDER.read_text(encoding="utf-8")
    check("maturity" in builder and "mature" in builder,
          "the builder does not filter the source's mature flag")
    check("DENY" in builder, "there is no denylist for slurs and sexual slang")
    terms = {str(r.get("t", "")).lower() for r in data.get("slang") or []}
    for banned in ("bdsm", "jailbait", "gooning", "booty call", "sexting"):
        check(banned not in terms, f"{banned!r} reached the bank")

    authored = json.loads(AUTHORED.read_text(encoding="utf-8"))
    glosses = {k: v for k, v in authored.items() if not k.startswith("_")}
    check(len(glosses) >= FLOOR_SLANG_FA,
          f"only {len(glosses)} Persian glosses are authored")
    for term, gloss in glosses.items():
        check(bool(FA.search(gloss)), f"the gloss for {term!r} has no Persian")
    # a gloss for a term the bank dropped is dead weight, not a bug: the
    # source changes daily and the build keeps what it can still match


def check_wiring() -> None:
    py = PY.read_text(encoding="utf-8")
    check('SLANG_FILE = Path(__file__).parent / "slang.json"' in py,
          "the Python bot has no path for the bank")
    check("self._load_slang(slang_path)" in py,
          "the Python bot never loads the bank")
    check("def handle_slang" in py, "the Python bot has no slang handler")
    # the bank answers before the idiom listing: "معنی اصطلاح X یعنی چی" is a
    # question about one idiom, and the listing replies with all of them
    slang_at = py.find("result = self.handle_slang(")
    idioms_at = py.find("result = self.handle_idioms(")
    check(slang_at != -1 and idioms_at != -1 and slang_at < idioms_at,
          "the slang handler does not run before the idiom listing")
    check("FA_FOLD" in py, "no Persian folding for the idiom keys")

    js = JS.read_text(encoding="utf-8")
    check("handleSlang(" in js, "the offline engine has no slang handler")
    check("this.loadSlang(data.slang)" in js,
          "the offline engine never loads the bank")
    check("SLANG_FA_FOLD" in js, "the offline engine has no Persian folding")
    js_slang = js.find("this.handleSlang(")
    js_idioms = js.find("this.handleIdioms(text, lowered, lang)")
    check(js_slang != -1 and js_idioms != -1 and js_slang < js_idioms,
          "the offline engine answers the idiom listing before the bank")

    # same reply text on both sides, or the phone and the web disagree
    for literal in ("“${row.term}”", "   ↲ در جمله: ", "   ↗ به انگلیسی: ",
                    "💬 Slang — اصطلاح‌های عامیانه:", "   🏷 "):
        check(literal in js, f"the offline engine lost the reply line {literal!r}")
    for literal in ("🗯  “{row['term']}”", "   🏷 ", "   ↲ در جمله: ",
                    "💬 Slang — اصطلاح‌های عامیانه:"):
        check(literal in py,
              f"the Python bot lost the reply line {literal!r}")

    build = BUILD.read_text(encoding="utf-8")
    check('"slang.json"' in build,
          "build_apk_ui.py does not copy the bank into the offline bundle")
    check("loadJSON('slang')" in build,
          "the offline boot does not read the bank")
    check("daily, slang})" in build,
          "the offline engine is not handed the bank")
    engine = ENGINE_JS.read_text(encoding="utf-8")
    check("slang: JSON.parse" in engine,
          "the parity harness does not load the bank for the JS engine")


def main() -> int:
    try:
        data = json.loads(BANK.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print("FAIL  slang.json is missing - run tools/build_slang.py")
        return 1
    except json.JSONDecodeError as exc:
        print(f"FAIL  slang.json does not parse: {exc}")
        return 1

    stats = check_bank(data)
    check_curation(data)
    check_wiring()

    if problems:
        for p in problems[:40]:
            print("FAIL  " + p)
        if len(problems) > 40:
            print(f"      ... and {len(problems) - 40} more")
        print(f"\nFAIL  {len(problems)} problem(s) with the slang bank")
        return 1

    print(f"PASS  {stats['slang']} slang terms ({stats['fa']} with a Persian "
          f"gloss), {stats['idioms']} English idioms, {stats['fa_idioms']} "
          f"Persian idioms; both engines answer from it")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
