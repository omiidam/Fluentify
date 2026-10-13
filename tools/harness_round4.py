#!/usr/bin/env python3
"""Harness round 4 — the grammar checker's own accuracy.

Round 3 added corrections.json. Round 4 held the checker to a standard: it must
catch the error, and — just as important — stay silent on correct English.
Measured on the round-4 corpus it had 1 false positive ('I was tired') and 3
false negatives ('She have a car', 'they was here', 'they was happy').

Fixes:
  * "I was" is CORRECT English; only 'I is / are' is the error
  * "they was" needs a rule; the existing one only covered "they are"
  * "She have" needs a rule (only "he / she / it have" is the error)
  * "can to go" must rewrite to "can go", not "can to go"

The round-4 corpus itself is written to tools/harness_round4_corpus.json so
the same sentences keep being checked on every future run.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CORRECT = [
    "I have two brothers.", "She works in a hospital.", "They don't live here.",
    "I didn't go to school.", "He went to Paris last year.",
    "The book is on the table.", "This is interesting.",
    "I'm interested in history.", "I have some information.",
    "I need much help.", "She is taller than me.", "You should have told me.",
    "I have been waiting for an hour.", "He has gone home.", "We were tired.",
    "I have a few pieces of advice.", "She has a car.", "They were here.",
    "I can go now.", "He will come.", "They must leave.", "I was tired.",
    "She didn't go to the party.", "It doesn't matter.", "We have finished.",
    "The film is interesting and I am interested in it.",
    "I need some information.", "She is more experienced than me.",
    "This is the best day.", "My father has a car.", "They are late.",
    "We have many friends.", "It has started to rain.", "I am tired.",
    "He was at home.", "They have arrived.", "It is cold today.",
    "I don't think so.", "She won't come.", "You shouldn't do that.",
    "There is a problem.", "There were many people.", "The keys are here.",
    "I have seen him before.", "He has written the letter.",
    "She studied hard yesterday.", "They arrived late.", "We can start now.",
    "I'm going to the shop.", "She has been working since 2020.",
    "Everyone is ready.", "Nobody knows.", "Something is wrong.",
]

WRONG = [
    "She have a car", "they was here", "they was happy", "He go to school",
    "can to go", "will to come", "she don't like it", "I have many informations",
    "I is tired", "they is here", "we was late", "it have a handle",
    "I am agree", "I didn't went", "he have two cars", "she have finished",
    "more better", "most best", "discuss about the plan", "despite of rain",
    "I no understand", "depend of you", "marry with Ali", "advices are useful",
]


def main() -> None:
    (ROOT / "tools/harness_round4_corpus.json").write_text(
        json.dumps({"correct": CORRECT, "wrong": WRONG}, ensure_ascii=False, indent=2),
        encoding="utf-8")

    p = ROOT / "tools/harness_round2.py"
    s = p.read_text(encoding="utf-8")

    # 'I was' is right; only 'I is / are / am wrong' is the error
    s = s.replace('''    (r"\\bi\\s+(is|are|was|were)\\b",
     "Subject-verb agreement", "I am / {1} is",
     "'I am' in the present, 'I was' in the past. Never 'I is'."),''',
'''    (r"\\bi\\s+(is|are)\\b",
     "Subject-verb agreement", "I am",
     "'I' takes 'am' in the present and 'was' in the past: 'I am', 'I was' - "
     "never 'I is' or 'I are'."),
    (r"\\b(they|we|you)\\s+(is|was)\\b",
     "Subject-verb agreement", "{0} are",
     "With we / they / you the plural verb is 'are' (or 'were' in the past), "
     "never 'is' or 'was'."),
    (r"\\b(he|she|it)\\s+(have|has got)\\b",
     "Subject-verb agreement", "{0} has",
     "With he / she / it the verb is 'has', never 'have'."),
    (r"\\b(i|we|they|you)\\s+(has)\\b",
     "Subject-verb agreement", "{0} have",
     "With I / we / they / you the verb is 'have', never 'has'."),''')

    # 'can to go' has to become 'can go'
    s = s.replace('''    (r"\\b(can|will|should|must|could|would|may|might)\\s+to\\b",
     "Modal verb never takes to", "{0} {1}",
     "Modal verbs stand alone: 'can go', 'must go' - never 'can to go'."),''',
'''    (r"\\b(can|will|should|must|could|would|may|might)\\s+to\\s+(\\w+)",
     "Modal verb never takes to", "{0} {1}",
     "Modal verbs stand alone: 'can go', 'must go' - never 'can to go'."),
    (r"\\b(can|will|should|must|could|would|may|might)\\s+to\\s*[?.!]*\\s*$",
     "Modal verb never takes to", "{0}",
     "A modal verb takes the base form directly - there is nothing after "
     "the 'to' here."),''')

    p.write_text(s, encoding="utf-8")
    print(f"rules updated; corpus of {len(CORRECT)} correct + {len(WRONG)} wrong saved")


if __name__ == "__main__":
    main()