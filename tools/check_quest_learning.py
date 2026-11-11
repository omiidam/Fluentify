#!/usr/bin/env python3
"""The learning mechanics are in the game, and the report cannot invent data.

    python3 tools/check_quest_learning.py
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = (ROOT / "webapp.py").read_text(encoding="utf-8")
TOOL = ROOT / "tools" / "quest_learning.py"
DOC = ROOT / "docs" / "heroquest-assessment.md"

problems = []


def check(ok, line):
    if not ok:
        problems.append(line)
    print(f"  {'ok  ' if ok else 'FAIL'}  {line}")


quest = SRC[SRC.index("const Quest = (() => {"):]
quest = quest[:quest.index("\n})();")]

check("function noteItem(" in quest and "function dueItems(" in quest,
      "the game remembers each item, not only each mission's stars")
check("st.items" in quest and "row.r += 1" in quest and "row.w += 1" in quest,
      "right and wrong answers are counted per item")
check("t - it.at > 3 * DAY_MS" in quest,
      "a known item comes back after three days, not never")
check("it.w > it.r" in quest,
      "an item still wrong more often than right stays in the review queue")
check("function vocabGap(" in quest and "word.example_en" in quest
      and "sentence.replace(wordRe, '___')" in quest,
      "vocabulary is also recalled inside a sentence, not only translated")
check("k === 0 ? vocabGap(w, local + k) : null" in quest,
      "every mission opens with one recall task and one recognition task")
check("due.has('w:' + b.word)" in quest,
      "a due word is preferred when the mission picks its vocabulary")
check("function mountGapWords(" in quest and "ch.t === 'gap'" in quest,
      "the recall board is mounted by the play screen")
check("b.classList.add(ok ? 'right' : 'wrong')" in quest
      and "if (right) right.classList.add('right')" in quest,
      "the recall board marks the right word, not only the wrong one")
check("if (!ok) {\n      const retry" in quest,
      "every challenge kind offers another attempt")
check("ch.t === 'fill' || ch.t === 'order' || ch.t === 'match'" not in quest,
      "the old tap-only retry list is gone")
check("if (ch.item && !ch.counted)" in quest,
      "a retry is practice: the item is counted once, on the first attempt")
for prefix, what in (("'w:' + word.word", "a word"),
                     ("'g:' + lesson.id", "a grammar lesson"),
                     ("'p:' + item.en", "a phrase"),
                     ("'r:' + passage.id", "a passage")):
    check(prefix in quest, f"{what} answers carry an item id")

check(TOOL.exists(), "the learning report tool exists")
check(DOC.exists() and "delayed7" in DOC.read_text(encoding="utf-8"),
      "the protocol names the delayed retention check")

run = subprocess.run([sys.executable, str(TOOL)], capture_output=True, text=True)
check(run.returncode == 0, "the report runs without a data file")
check("No assessment data yet" in run.stdout,
      "with no data it reports no data rather than a result")

synthetic = '{"items": {"w:bridge": {"r": 3, "w": 0, "at": 1}}, "assessments": [' \
            '{"phase": "baseline", "ok": false}, {"phase": "baseline", "ok": true},' \
            '{"phase": "immediate", "ok": true}, {"phase": "immediate", "ok": true},' \
            '{"phase": "delayed7", "ok": false}]}'
import json
import tempfile
with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
    fh.write(synthetic)
    path = fh.name
run2 = subprocess.run([sys.executable, str(TOOL), path], capture_output=True, text=True)
check(run2.returncode == 0 and "delayed7" in run2.stdout,
      "a real export is summarised phase by phase")
check("too few to call a rate" in run2.stdout,
      "a two-answer phase is not dressed up as a percentage")

print()
if problems:
    print(f"{len(problems)} problem(s) with the learning mechanics")
    for p in problems:
        print("   - " + p)
    sys.exit(1)
print("PASS  item memory, spaced review, recall in context, retry everywhere, "
      "and a report that will not invent a number")
