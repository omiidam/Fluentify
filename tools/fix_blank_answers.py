#!/usr/bin/env python3
"""Repair the blank answer slots the round-5 integrity check found.

'grammar.json' had four questions whose answer list contained an empty string
("no article" questions). The JSON looks fine, but 'show answer' printed
" / no article / zero" with a leading blank, and a blank is never something a
learner can type.

This fixes the four rows in the data AND adds _clean_answers() at load time,
so a blank can never reach a learner again even if someone edits the JSON
later. Run once; the repair is idempotent.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    # ---------------------------------------------------------- the data ----
    p = ROOT / "grammar.json"
    grammar = json.loads(p.read_text(encoding="utf-8"))
    fixed = 0
    for topic in grammar["topics"].values():
        for stage in ("practice", "exam"):
            for q in topic.get(stage, []):
                answers = q.get("a") or []
                cleaned = [str(a).strip() for a in answers if str(a).strip()]
                if not cleaned:
                    # a blank is never a real answer: these questions are all
                    # asking for "no article", so say it in words
                    if re.search(r"no article|the / no", q["q"]["en"], re.I):
                        cleaned = ["no article", "zero article"]
                    else:
                        cleaned = ["no"]
                if cleaned != [str(a) for a in answers]:
                    q["a"] = cleaned
                    fixed += 1
    p.write_text(json.dumps(grammar, ensure_ascii=False, indent=2),
                 encoding="utf-8")
    print(f"grammar.json: {fixed} answer lists cleaned")

    # ------------------------------------------------------ the guard -------
    c = ROOT / "chatbot.py"
    text = c.read_text(encoding="utf-8")
    old = """        with open(grammar_path, encoding="utf-8") as f:
            self.grammar = json.load(f)["topics"]"""
    new = '''        with open(grammar_path, encoding="utf-8") as f:
            self.grammar = json.load(f)["topics"]
        self._clean_answers()

    def _clean_answers(self) -> None:
        """Drop blank answer slots at load time.

        An empty string in a question's answers is invisible in the JSON but
        very visible to a learner: "show answer" printed " / no article / zero"
        with a leading blank. A blank is also never something anyone can type,
        so in the data it can only ever be a mistake.
        """
        for topic in self.grammar.values():
            for stage in ("practice", "exam"):
                for q in topic.get(stage, []):
                    answers = q.get("a")
                    if not isinstance(answers, list):
                        continue
                    cleaned = [str(a).strip() for a in answers
                               if str(a).strip()]
                    if cleaned and cleaned != [str(a) for a in answers]:
                        q["a"] = cleaned'''
    if "_clean_answers" not in text:
        assert old in text, "grammar load block not found"
        c.write_text(text.replace(old, new, 1), encoding="utf-8")
        print("chatbot.py: _clean_answers() guard added")
    else:
        print("chatbot.py: guard already present")


if __name__ == "__main__":
    main()