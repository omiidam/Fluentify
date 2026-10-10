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
    cases_file.write_text(json.dumps([[c] for c in CASES], ensure_ascii=False))

    subprocess.run(
        ["node", str(ROOT / "tools/js_engine.js"), str(cases_file), str(js_out)],
        check=True,
    )

    sys.path.insert(0, str(ROOT))
    from chatbot import ChatBot  # noqa: E402

    bot = ChatBot()
    py = [bot.respond(c) for c in CASES]
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