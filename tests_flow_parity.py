#!/usr/bin/env python3
"""Compares the two engines on *sequences*, not single messages.

Rounds 1-2 added capabilities; round 3 added memory, and memory only shows up
when you send several messages in a row. A single-message parity test cannot
see "exercises" working only after a lesson was opened — or quietly broken by
a state leak — so this walks both engines down the same flows.

    python3 tests_flow_parity.py
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Each flow is a sequence a learner actually walks.
FLOWS = [
    ["simple present", "exercises", "go", "he go to work", "show answer",
     "cancel", "exam"],
    ["future perfect", "exam", "exercises"] + ["will have"] * 7 +
    ["exam"] + ["will have finished"] * 20,
    ["tell me a joke", "another one", "another one"],
    ["listen A1", "repeat that", "say that again", "A2", "repeat that"],
    ["daily routine", "repeat that"],
    ["vocabulary", "words", "sentences", "phonetics"],
    ["translate apple", "define apple", "how do you pronounce apple",
     "difference between say and tell", "idioms", "meaning of piece of cake"],
    ["I am fine", "what can I learn today", "thanks", "bye"],
    ["simple present", "examples", "show answer", "next", "cancel"],
    ["my name is Sara", "nice to meet you", "I am Sara from Tehran"],
    ["is this correct? I have went there", "I didn't went", "they doesn't"],
    ["simple present", "vocabulary", "fruits", "apple", "سیب به انگلیسی"],
    ["twenty one", "one hundred", "A1", "C2", "difference between in and on"],
    # the checker's corpus, walked one message at a time like a learner would
['I have two brothers.', 'She works in a hospital.', "They don't live here.", "I didn't go to school.", 'He went to Paris last year.', 'The book is on the table.', 'This is interesting.', "I'm interested in history.", 'I have some information.', 'I need much help.', 'She is taller than me.', 'You should have told me.', 'I have been waiting for an hour.', 'He has gone home.', 'We were tired.', 'I have a few pieces of advice.', 'She has a car.', 'They were here.', 'I can go now.', 'He will come.', 'They must leave.', 'I was tired.', "She didn't go to the party.", "It doesn't matter.", 'We have finished.', 'The film is interesting and I am interested in it.', 'I need some information.', 'She is more experienced than me.', 'This is the best day.', 'My father has a car.', 'They are late.', 'We have many friends.', 'It has started to rain.', 'I am tired.', 'He was at home.', 'They have arrived.', 'It is cold today.', "I don't think so.", "She won't come.", "You shouldn't do that.", 'There is a problem.', 'There were many people.', 'The keys are here.', 'I have seen him before.', 'He has written the letter.', 'She studied hard yesterday.', 'They arrived late.', 'We can start now.', "I'm going to the shop.", 'She has been working since 2020.', 'Everyone is ready.', 'Nobody knows.', 'Something is wrong.', 'She have a car', 'they was here', 'they was happy', 'He go to school', 'can to go', 'will to come', "she don't like it", 'I have many informations', 'I is tired', 'they is here', 'we was late', 'it have a handle', 'I am agree', "I didn't went", 'he have two cars', 'she have finished', 'more better', 'most best', 'discuss about the plan', 'despite of rain', 'I no understand', 'depend of you', 'marry with Ali', 'advices are useful']
]

# Replies that legitimately vary between runs get blurred out: jokes, the
# clock, the date, and small talk (which picks a random canned response).
VOLATILE = ("😂", "It's ", "الان ساعت", "Today is", "امروز")


def _canned_replies() -> list[str]:
    texts = []
    memory = json.loads((ROOT / "memory.json").read_text(encoding="utf-8"))
    for intent in memory["intents"]:
        texts.extend(intent["responses"]["en"])
        texts.extend(intent["responses"]["fa"])
    return texts


CANNED = _canned_replies()


def normalise(reply: str) -> str:
    out = (reply or "").strip()
    if any(v in out for v in VOLATILE):
        return "<volatile>"
    if any(out.split(" ")[0] in r for r in CANNED):
        return "<intent-reply>"
    return out


def main() -> int:
    cases = [{"flow": flow} for flow in FLOWS]
    cases_file = ROOT / ".flow_cases.json"
    js_out = ROOT / ".flow_js.json"
    cases_file.write_text(json.dumps(cases, ensure_ascii=False))

    subprocess.run(["node", str(ROOT / "tools/js_engine.js"), str(cases_file),
                    str(js_out)], check=True)

    sys.path.insert(0, str(ROOT))
    from chatbot import ChatBot  # noqa: E402

    js_flows = json.loads(js_out.read_text())
    mismatches = 0
    checked = 0

    for flow, js_replies in zip(FLOWS, js_flows):
        bot = ChatBot()
        for step, (msg, js) in enumerate(zip(flow, js_replies)):
            py = bot.respond(msg)
            checked += 1
            if normalise(py) != normalise(js):
                mismatches += 1
                print(f"MISMATCH  step {step} of {len(flow)}  {msg!r}")
                print("  py:", normalise(py)[:130].replace("\n", "\\n"))
                print("  js:", normalise(js)[:130].replace("\n", "\\n"))

    print(f"\n{checked - mismatches}/{checked} replies identical "
          f"across {len(FLOWS)} flows")
    for f in (cases_file, js_out):
        f.unlink(missing_ok=True)
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())