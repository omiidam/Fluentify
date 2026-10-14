#!/usr/bin/env python3
"""Compares the Python bot and the JS engine on the same inputs.

The JS engine is what ships inside the APK, so the two must agree. Inputs that
are randomised (jokes, time, date) are compared on *kind* rather than text.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent

CASES = [
    # register — the one capability whose whole output is built at runtime,
    # so it needs parity coverage like any other reply path
    "register", "formal vs casual",
    "how do I say i need to leave early",
    "how do I say sorry I'm late formally",
    "how do i say i don't agree casually",
    "چطور بگم نفهمیدم مؤدبانه",
    "چطور بگم به نظر من رسمی",
    "what do I say in a job interview",
    "how would you say help me formally",
    "how do I say turn on the light casually",
    "hello", "how are you", "الفبای فارسی", "english alphabet", "حرف ب",
    "what letter is A", "translate apple", "سیب به انگلیسی", "معنی خوشحال چیه",
    "define شیر", "رنگها", "حیوانات", "حیوان", "مدرسه", "سیب", "رنگها رو بگو",
    "grammar", "گرامر", "simple present", "حال ساده", "present perfect continuous",
    "future perfect", "گذشته کامل", "passive voice", "حروف تعیین", "حروف ربط",
    "simple present exercises", "تمرین حال ساده", "phrasal verbs exercises",
    "travel sentences", "جملات سفر", "daily routine", "small talk", "معما",
    "help", "راهنما", "my name is Ali", "سلام", "متوجه نشدم", "I feel stressed",
    "استرس دارم", "merci", "house words", "bank sentences", "politely complaining",
    "سفر و فرودگاه", "تکراری", "abjad", "پنج", "5", "translate قهوه",
    "خوشبختصبح", "yes", "no", "thanks", "درمان",
    "listen", "listen A2", "گوش دادن C1", "بگو B1", "listening levels",
    # practice -> exam gate (each topic starts locked)
    "simple present exam", "آزمون حال ساده", "future perfect exam",
    "simple present test", "past perfect exam", "articles exam", "to be exam",
    # the exam-unlock / lock messages
    "simple present", "future perfect", "passive voice", "articles",
    # numbers written in words + a bare CEFR band
    "twenty one", "one hundred", "two hundred and fifty", "seven", "apple",
    "A1", "C2", "listen B2",
    # confusable pairs
    "difference between say and tell", "difference between a and an",
    "tell me the difference between affect and effect", "when do we use since and for",
    "difference between in and on", "difference between interesting and interested",
    "تفاوت since و for", "فرق say و tell",
    "difference between although and though", "difference between few and a few",
    "difference between used to and get used to",
    "difference between present perfect and past simple",
    "difference between because and since", "what is the difference",
    # idioms
    "what does 'spill the beans' mean", "meaning of once in a blue moon",
    "what does hit the books mean", "what is a piece of cake",
    "meaning of under the weather", "what does the last straw mean",
    "معنی break the ice", "idioms", "اصطلاح",
    # the grammar checker
    "is this correct? I have went there", "correct this sentence: he don't like it",
    "I didn't went to school", "they doesn't like it", "I have many informations",
    "is this correct: he go to school", "I no understand this",
    "I am agree with you", "despite of the rain", "I have more better ideas",
    "is this sentence right: I no understand", "She doesn't watch TV",
    "She watches TV every day", "The book is on the table",
    # pronunciation
    "how do you pronounce apple", "how do you say hospital",
    "تلفظ کلمه apple", "how do you pronounce zebra", "how do you say a word",
    "how do you say thank you", "how do you say good night",
    # meta
    "how many words do you know",
    # the confused / help intents the probes added
    "I don't know", "i have no idea", "گیج شدم", "i don't understand",
    # round 3: contextual follow-ups after opening something
    "exercises", "exam", "show answer", "examples", "cancel", "next",
    "another one", "repeat that", "vocabulary", "words", "sentences",
    "phonetics", "واژگان", "جملات", "تلفظ", "I am fine", "I'm good",
    "what can I learn today", "save apple to review", "what did you say",
    # round 4: checker accuracy - correct English must stay untouched
    "I have seen him before", "I have been waiting", "He has written the letter",
    "It doesn't matter", "We have finished", "There were many people",
    "I need much help", "She is more experienced than me", "I was tired",
    # round 4: errors the checker must catch
    "She have a car", "they was here", "they was happy", "they is here",
    "I were tired", "we was late", "he have two cars", "she have finished",
    "I is tired", "it have a handle", "can to go", "will to come",
    "I have a few pieces of advice", "I have many informations",
]


def normalise(reply: str) -> str:
    """Blur out the parts that legitimately differ between runtimes."""
    out = reply.strip()
    if "😂" in out:  # jokes are randomly picked
        return "<joke>"
    if out.startswith("الان ساعت") or out.startswith("It's "):
        return "<time>"
    if out.startswith("امروز") or out.startswith("Today is"):
        return "<date>"
    # small talk picks a random canned response — compare the *kind* of reply
    base = out.split(" ")[0]
    if any(base in r for r in ALL_REPLY_TEXTS):
        return "<intent-reply>"
    return out


def _collect_replies() -> list[str]:
    replies: list[str] = []
    for intent in json.loads((ROOT / "memory.json").read_text(encoding="utf-8"))["intents"]:
        replies.extend(intent["responses"]["en"])
        replies.extend(intent["responses"]["fa"])
    return replies


ALL_REPLY_TEXTS = _collect_replies()


def main() -> int:
    cases_file = ROOT / ".cases.json"
    py_out = ROOT / ".py_replies.json"
    js_out = ROOT / ".js_replies.json"
    cases_file.write_text(
        json.dumps([{"input": c} for c in CASES], ensure_ascii=False))

    subprocess.run(
        ["node", str(ROOT / "tools/js_engine.js"), str(cases_file), str(js_out)],
        check=True,
    )

    sys.path.insert(0, str(ROOT))
    from chatbot import ChatBot  # noqa: E402

    # A fresh bot per case: the JS side does the same, and without it one
    # case that starts a quiz (e.g. "articles exam") poisons every later one
    # with "Not quite" and hides real mismatches.
    py = [ChatBot().respond(c) for c in CASES]
    js = json.loads(js_out.read_text())

    mismatches = 0
    for case, p, j in zip(CASES, py, js):
        np_, nj = normalise(p), normalise(j)
        if np_ != nj:
            mismatches += 1
            print("MISMATCH for", repr(case))
            print("  py:", np_[:150].replace("\n", "\\n"))
            print("  js:", nj[:150].replace("\n", "\\n"))

    print(f"\n{len(CASES) - mismatches}/{len(CASES)} replies identical")
    for f in (cases_file, py_out, js_out):
        f.unlink(missing_ok=True)
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())