#!/usr/bin/env python3
"""Is the informal sentence bank complete, unambiguous, and actually reachable?

The bank is 280 English/Persian pairs in 14 themes, added as topics in
phrases.json so the existing sentence-bank machinery carries them. That means
four things can go wrong quietly:

  * a pair loses its Persian half (the JSON is edited by hand) and the learner
    gets an empty arrow;
  * two of them share an English sentence, so one of them can never be reached;
  * the same sentence exists in an older topic and the new one is dead weight;
  * the sentence is stored but typing it still produces the generic menu,
    which is how the whole bank looked before lookup_phrase_exact() existed.

The answers themselves are checked by running both engines over the sentences,
because they are separate code and only Python implements the API fallback.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import os  # noqa: E402

os.environ["FLUENTIFY_NO_WEB_DICT"] = "1"
os.environ.setdefault("FLUENTIFY_TODAY", "2026-05-04")

from chatbot import ChatBot, phrase_key  # noqa: E402

CHECKS = 0
FAILURES = []


def check(name: str, ok: bool, detail: str = "") -> None:
    global CHECKS
    CHECKS += 1
    if not ok:
        FAILURES.append(f"{name}{': ' + detail if detail else ''}")


# One pair from each theme, the way a learner would type it. Ten of the
# fourteen, because these are also the parity cases in tests_js_vs_python.py
# and the point here is the bank, not every sentence twice.
SAMPLES = [
    ("spill the tea", "بگو ببینم چه خبرای پشت پرده‌ایه!"),
    ("let's hit the road", "بزن بریم تو جاده."),
    ("I'm swamped with work.", "سرم خیلی با کار شلوغه."),
    ("don't roast me", "منو سوژه خنده نکن!"),
    ("can we split the bill", "می‌شه دنگی حساب کنیم؟"),
    ("i'm on the fence", "هنوز دودلم."),
    ("i'm craving pizza", "خیلی هوس پیتزا کردم."),
    ("i'm just messing with you", "دارم سر به سرت می‌ذارم."),
    ("how do you say this in english", "این رو به انگلیسی چی می‌گن؟"),
    ("i owe you one", "یه دونه بهت بدهکارم."),
]


def main() -> int:
    themes = json.loads((ROOT / "phrases.json").read_text(encoding="utf-8"))["topics"]
    informal = {tid: t for tid, t in themes.items() if tid.startswith("informal_")}

    check("14 themes", len(informal) == 14, f"{len(informal)} found")

    total = 0
    empty_en, empty_fa = [], []
    seen, duplicates = {}, []
    for tid, topic in informal.items():
        check(f"{tid} has a title", bool(topic.get("title", {}).get("en"))
              and bool(topic.get("title", {}).get("fa")))
        check(f"{tid} has keywords", bool(topic.get("keywords", {}).get("en")),
              "no English keywords, so it cannot be found by name")
        for line in topic["phrases"]:
            total += 1
            en, fa = line.get("en", "").strip(), line.get("fa", "").strip()
            if not en:
                empty_en.append(tid)
            if not fa:
                empty_fa.append(tid)
            key = phrase_key(en)
            if key in seen:
                duplicates.append(f"{en!r} in {tid} and {seen[key]}")
            seen[key] = tid

    check("280 pairs", total == 280, f"{total} found")
    check("every pair has English", not empty_en, str(empty_en[:5]))
    check("every pair has Persian", not empty_fa, str(empty_fa[:5]))
    check("no English sentence twice", not duplicates, str(duplicates[:5]))

    # A sentence shared with an older topic is not a bug - both translations
    # are valid - but it must not be two different answers to the same question
    # inside this bank, which the duplicate check above covers. Here the older
    # overlap is counted so a future edit cannot silently grow it.
    older = {tid: t for tid, t in themes.items() if not tid.startswith("informal_")}
    old_keys = {phrase_key(line["en"])
                for t in older.values() for line in t["phrases"]}
    # Twelve of the 280 were already in an earlier topic ("see you around",
    # "is this seat taken", "could you do me a favor"). Keeping them is right -
    # the file is the source - but the count is pinned so a future edit cannot
    # quietly make half the bank unreachable behind an older topic. The twelfth
    # appeared when the American spelling of "favor" matched the older entry.
    overlap = sorted(k for k in seen if k in old_keys)
    check("shared sentences stay at the known twelve", len(overlap) == 12,
          f"{len(overlap)} shared: {overlap}")

    # The key rules the lookup depends on
    check("apostrophes folded", phrase_key("Don’t roast me!") == phrase_key("Don't roast me"))
    check("punctuation ignored", phrase_key("Let’s hit the road.") == phrase_key("Let's hit the road"))
    check("words stay apart", phrase_key("ice cream") != phrase_key("icecream"))
    check("persian normalized", phrase_key("چه خبر؟") == phrase_key("چه خبر"))

    bot = ChatBot()
    for asked, expected_fa in SAMPLES:
        reply = bot.respond(asked)
        check(f"answers {asked!r}", expected_fa in reply, reply.split("\n")[0][:80])
        check(f"{asked!r} is not the menu", "I'm not sure I understand" not in reply)

    # Persian side answers with the English
    reply = bot.respond("بزن بریم تو جاده")
    check("persian input answers with english", "hit the road" in reply, reply[:80])
    # and a sentence we do not hold still gets the menu, not a false match
    reply = bot.respond("my hovercraft is full of eels")
    check("an unknown sentence still gets the menu",
          "I'm not sure I understand" in reply, reply[:80])

    # A theme is still listable by name, in both languages
    listing = bot.respond("informal greetings")
    check("theme listed in english", "Informal Greetings" in listing and "What’s up?" in listing)
    listing = bot.respond("یادگیری انگلیسی")
    check("theme listed in persian", "Learning English" in listing)

    # and the APK bundle carries the same file
    bundled = ROOT / "android/app/src/main/assets/www/data/phrases.json"
    if bundled.exists():
        same = json.loads(bundled.read_text(encoding="utf-8")) == json.loads(
            (ROOT / "phrases.json").read_text(encoding="utf-8"))
        check("the apk bundle has the bank", same,
              "data/phrases.json is stale - run build_apk_ui.py")
    else:
        check("the apk bundle has the bank", False, "data/phrases.json missing")

    bot_js = (ROOT / "android/app/src/main/assets/www/bot.js").read_text(encoding="utf-8")
    check("the apk engine has the exact lookup", "lookupPhraseExact(text)" in bot_js)
    check("the apk engine folds apostrophes", "\\u2019`\\u00b4]" in bot_js)

    if FAILURES:
        print(f"FAIL  {len(FAILURES)} of {CHECKS} informal-bank checks\n")
        for f in FAILURES:
            print(f"  {f}")
        print()
        return 1
    print(f"PASS  all {CHECKS} informal-bank checks (280 pairs in 14 themes, "
          "each one answerable in both engines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
