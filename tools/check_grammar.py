#!/usr/bin/env python3
"""Checks the grammar lessons for arrangement faults.

A lesson is a bilingual document: every English line carries its Persian
under it, in the same order, and the two are supposed to be the same sentence
in two languages. That promise breaks in ways a reader notices and a parser
does not, so this reads all forty-eight lessons and reports:

  * a pair with no Persian, or no English
  * untidy text - leading/trailing spaces, doubled spaces, a space before
    punctuation, an unbalanced **emphasis** marker
  * a fill-in-the-blank question whose Persian has no blank, so a Persian
    learner is shown a complete sentence and asked to fill a hole that is not
    there
  * the two languages disagreeing about how many blanks there are
  * a structure list whose rows are not in teaching order (affirmative,
    negative, question, short answer)
  * colloquial Persian in a lesson that is otherwise written in the formal
    register the rest of the app uses

The last one is reported, not repaired: deciding that "می‌کنه" should read
"می‌کند" is a judgement about a sentence, and a script that makes it blindly
will eventually change a sentence that was quoting speech.

    python3 tools/check_grammar.py           the summary
    python3 tools/check_grammar.py -v        every finding
    python3 tools/check_grammar.py --json    the same, for a fixer to read
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANK = ROOT / "grammar.json"

FA_CHAR = re.compile(r"[\u0600-\u06FF]")
LATIN = re.compile(r"[A-Za-z]")
PAIR_LISTS = ("structure", "explain", "function", "examples")
SINGLE = ("title", "tip")

# The order a lesson argues in: make the form, deny it, ask with it, answer it.
STRUCTURE_ORDER = ["affirmative", "negative", "question", "short answer"]

# Everyday speech the app does not use anywhere else. Each of these has a
# formal twin that the lessons already use, which is what makes the mix visible
# on one screen: examples in "می‌کند" above a practice item in "می‌کنه".
COLLOQUIAL = [
    "می‌کنه", "می‌کنن", "می‌شه", "می‌شن", "می‌ره", "می‌رن", "می‌گه", "می‌گن",
    "می‌خوام", "می‌خوای", "می‌خواد", "نمی‌کنه", "نمی‌کنن", "نمی‌شه", "نمی‌دونم",
    "کتابخونه", "خونه", "یه", "رو", "اون", "اینو", "اونو", "بریم", "بشه",
    "نتونستم", "می‌کشه", "نمی‌کشه", "داره", "دارن", "می‌خونه", "می‌خونن",
]

# "بودن" and "می‌برد" were in this list and are not colloquial at all - one is
# the infinitive of the copula, the other the ordinary present of بردن, and
# flagging them meant flagging "...بالا می‌برد" in a lesson about formal
# register. Only forms with a formal twin that the lessons already use belong
# here.


def pairs_of(topic):
    for section in PAIR_LISTS:
        for index, pair in enumerate(topic.get(section) or []):
            yield f"{section}[{index}]", pair
    for field in SINGLE:
        value = topic.get(field)
        if isinstance(value, dict):
            yield field, value


def tidy_faults(text):
    faults = []
    if text != text.strip():
        faults.append("surrounding space")
    if "  " in text:
        faults.append("doubled space")
    if re.search(r"\s+[.,?!;:](?!\s*\d)", text):
        faults.append("space before punctuation")
    if text.count("**") % 2:
        faults.append("unbalanced **")
    return faults


def report():
    topics = json.loads(BANK.read_text(encoding="utf-8"))["topics"]
    findings = []

    def note(topic, where, kind, detail=""):
        findings.append({"topic": topic, "where": where, "kind": kind, "detail": detail})

    for key, topic in topics.items():
        for where, pair in pairs_of(topic):
            en, fa = pair.get("en"), pair.get("fa")
            if not (isinstance(en, str) and en.strip()):
                note(key, where, "no english")
                continue
            if not (isinstance(fa, str) and fa.strip()):
                note(key, where, "no persian", en[:60])
                continue
            for language, text in (("en", en), ("fa", fa)):
                for fault in tidy_faults(text):
                    note(key, f"{where}.{language}", fault, text[:70])
            if FA_CHAR.search(en) and len(FA_CHAR.findall(en)) > len(LATIN.findall(en)):
                note(key, where, "english line is persian", en[:60])
            # A structure row may legitimately be a formula - "so much / so
            # many" is the same formula in both languages, and inventing a
            # Persian rendering of it would be worse than leaving it.
            formula = any(mark in fa for mark in ("+", "/", "\u2192"))
            if not formula and not FA_CHAR.search(fa) and len(LATIN.findall(fa)) > 15:
                note(key, where, "persian line is english", fa[:60])
            if FA_CHAR.search(fa):
                for word in COLLOQUIAL:
                    if re.search(r"(?<![\u0600-\u06FF])" + re.escape(word) + r"(?![\u0600-\u06FF])", fa):
                        note(key, f"{where}.fa", "colloquial persian", f"{word} in {fa[:60]}")
                        break
            # A full stop is owed by a sentence. A function row or a structure
            # row is a noun phrase or a formula - "Habits and daily routines",
            # "subject + verb" - and punctuating those would be the untidy
            # choice, not the tidy one.
            sentence = where.split("[")[0] in ("examples", "explain", "tip")
            # A closing quotation mark comes after the stop, not instead of
            # it: «It's going to rain.» is punctuated.
            tail = re.sub(r"\s*\([^()]*\)\s*$", "", fa.rstrip())
            tail = tail.rstrip().rstrip("»\"'”’ ")
            if sentence and FA_CHAR.search(fa) and not tail.endswith((".", "!", "?", "؟", "…", ":")):
                note(key, f"{where}.fa", "no final punctuation", fa[-30:])

        # the structure rows, in the order a teacher says them
        labels = []
        for index, row in enumerate(topic.get("structure") or []):
            label = row.get("en", "").split(":")[0].strip().lower()
            if label:
                labels.append((index, label))
        seen = [label for _, label in labels if label in STRUCTURE_ORDER]
        if seen != sorted(seen, key=STRUCTURE_ORDER.index):
            note(key, "structure", "out of teaching order", " → ".join(seen))

        # a fill-in-the-blank the Persian cannot fill
        for section in ("practice", "exam"):
            for index, item in enumerate(topic.get(section) or []):
                en = (item.get("q") or {}).get("en", "")
                fa = (item.get("q") or {}).get("fa", "")
                blanks_en, blanks_fa = en.count("___"), fa.count("___")
                if blanks_en and not blanks_fa:
                    note(key, f"{section}[{index}]", "persian has no blank", fa[:60])
                # Persian packs an auxiliary and its participle into one verb
                # - "have been waiting" is one word - so one Persian blank can
                # honestly stand for two English ones. More blanks than the
                # English is always wrong; fewer is a translation choice.
                elif blanks_fa > blanks_en:
                    note(key, f"{section}[{index}]", "blank counts differ",
                         f"en {blanks_en} / fa {blanks_fa}: {fa[:60]}")

    return topics, findings


def main(argv):
    topics, findings = report()
    kinds = {}
    for finding in findings:
        kinds[finding["kind"]] = kinds.get(finding["kind"], 0) + 1

    if "--json" in argv:
        print(json.dumps(findings, ensure_ascii=False, indent=1))
        return 0 if not findings else 1

    topics_hit = len({f["topic"] for f in findings})
    print(f"grammar: {len(topics)} lessons, {topics_hit} with findings, {len(findings)} findings")
    for kind, count in sorted(kinds.items(), key=lambda kv: -kv[1]):
        print(f"  {count:4d}  {kind}")

    if "-v" in argv:
        print()
        for finding in findings:
            print(f"  {finding['topic']:32s} {finding['where']:18s} {finding['kind']:26s} {finding['detail']}")
    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
