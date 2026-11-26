#!/usr/bin/env python3
"""The greeting's shortcut chips: a week of drills that answers what it offers.

The chips under the greeting used to be the same four forever. They are now a
week: four drills for each weekday, and a new week shows the same four in a new
order. This checks three things about that:

  1. The plan is a week: 28 adult chips, four per weekday, no query twice, and
     every query lowercase (the query is echoed as the learner's own sentence,
     so a capital would show a sentence nobody typed).

  2. Every chip answers. A shortcut that lands on "I'm not sure I understand"
     is worse than no shortcut, so each query is put to the engine here.

  3. The schedule itself, by running the page's own functions in node: each
     weekday of a week gets a different four, every day gets four, and the same
     weekday is re-ordered in the next week.

    python3 tools/check_starters.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "webapp.py"

problems: list[str] = []


def check(ok: bool, what: str) -> bool:
    if not ok:
        problems.append(what)
    return ok


def block(src: str, start: str) -> str:
    """From a declaration to its closing `];`, keeping nested brackets."""
    at = src.find(start)
    if at < 0:
        return ""
    i = src.index("[", at)
    depth = 0
    for j in range(i, len(src)):
        c = src[j]
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return src[i:j + 1]
    return ""


ENTRY = re.compile(r"\[\s*'([^']*)'\s*,\s*'([^']*)'\s*,\s*'([^']*)'\s*\]")


def check_plan(src: str) -> list[tuple[str, str, str]]:
    raw = block(src, "const STARTERS = [")
    if not check(bool(raw), "the adult starter plan is gone"):
        return []
    entries = ENTRY.findall(raw)
    check(len(entries) == 28,
          f"{len(entries)} adult chips, want 28 - four for each of seven days")
    queries = [q for q, _, _ in entries]
    check(len(set(queries)) == len(queries), "a starter query is offered twice")
    check(all(q == q.lower() for q in queries),
          "a starter query is capitalised, so the echoed sentence is not what the chip says")
    check(all(label.strip() for _, label, _ in entries), "a starter chip has no label")
    check(all(re.search(r"[\u0600-\u06FF]", fa) for _, _, fa in entries),
          "a starter chip has no Persian")
    # four to a weekday, in the order the schedule reads them
    for d in range(0, len(entries), 4):
        group = entries[d:d + 4]
        check(len(group) == 4, f"weekday group {d // 4} is short")
    return entries


def check_answers(entries: list[tuple[str, str, str]]) -> None:
    sys.path.insert(0, str(ROOT))
    try:
        from chatbot import ChatBot
    except Exception as e:  # pragma: no cover - import failure is the message
        problems.append(f"chatbot could not be imported: {e}")
        return
    bot = ChatBot()
    for query, label, _ in entries:
        try:
            reply = bot.respond(query)
        except Exception as e:
            problems.append(f"{label!r}: the engine raised {e}")
            continue
        check(bool(reply) and len(reply) > 80,
              f"{label!r} answers with almost nothing, so the chip is a dead end")
        check("I'm not sure I understand" not in reply,
              f"{label!r} lands on \"I'm not sure I understand\"")


def check_kids(src: str) -> None:
    raw = block(src, "const KID_STARTERS = [")
    if not check(bool(raw), "the kid starter plan is gone"):
        return
    entries = ENTRY.findall(raw)
    check(len(entries) >= 12,
          f"{len(entries)} kid drills, want at least 12 so a week of fours can differ")
    queries = [q for q, _, _ in entries]
    check(len(set(queries)) == len(queries), "a kid drill is offered twice")
    check(all(q == q.lower() for q in queries), "a kid drill query is capitalised")
    check(all(re.search(r"[\u0600-\u06FF]", fa) for _, _, fa in entries),
          "a kid drill has no Persian")
    check("own.concat(KID_STARTERS)" in src,
          "the kid pool no longer merges the file's starters with the bank")


def check_wiring(src: str) -> None:
    check("function startersToday(" in src, "there is no schedule to read the plan with")
    check("starterDayIndex(" in src, "the day index is gone, so the chips cannot follow the calendar")
    check("startersToday(STARTERS, 4)" in src,
          "the adult chips are not taken from today's window")
    check("startersToday(Kids.starters(), 2)" in src,
          "the kid chips are not taken from today's window")
    check("visibilitychange" in src and "renderStarters();" in src,
          "a page left open overnight would keep yesterday's drills")


def run_schedule(src: str) -> None:
    """Run the page's own schedule in node, over real dates."""
    pool = "const STARTERS = " + block(src, "const STARTERS = [")
    m = re.search(r"const STARTER_DAY_MS = .*?\n\}\n\n/\* A phone left open", src, re.S)
    if not check(bool(m), "the schedule functions could not be read out of the page"):
        return
    fns = m.group(0).split("\n\n/* A phone left open")[0]
    script = "\n".join([
        pool, fns,
        """
const names = (arr) => arr.map((x) => x[1]);
const weekOf = (y, m, d) => Array.from({length: 7}, (_, i) => new Date(y, m, d + i));
const A = weekOf(2026, 10, 22);          // a Sunday
const days = A.map((d) => names(startersToday(STARTERS, 4, d)).join(','));
console.log('distinct', new Set(days).size);
console.log('sizes', [...new Set(days.map((d) => d.split(',').length))].join(','));
const mondays = Array.from({length: 8}, (_, w) =>
  names(startersToday(STARTERS, 4, new Date(2026, 10, 23 + 7 * w))).join(','));
console.log('weeks', mondays.map((m) => new Set(m.split(',')).size).join(','));
console.log('ordered', mondays.every((m, i) => i === 0 || m !== mondays[i - 1]));
// the same weekday must keep the same four, only the order may move
const groups = mondays.map((m) => [...new Set(m.split(','))].sort().join(','));
console.log('samefour', new Set(groups).size === 1);
""",
    ])
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(script)
        path = fh.name
    try:
        out = subprocess.run(["node", path], capture_output=True, text=True,
                             timeout=30)
    except (OSError, subprocess.SubprocessError) as e:
        problems.append(f"node could not run the schedule: {e}")
        return
    if out.returncode != 0:
        problems.append("the schedule does not run: " + (out.stderr or "").strip()[:200])
        return
    lines = dict(line.split(" ", 1) for line in out.stdout.strip().splitlines() if " " in line)
    check(lines.get("distinct") == "7",
          f"a week gives {lines.get('distinct')} different day sets, want 7")
    check(lines.get("sizes") == "4", f"a day offers {lines.get('sizes')} chips, want 4")
    check(lines.get("ordered") == "true",
          "the same weekday is laid out the same way in consecutive weeks")
    check(lines.get("samefour") == "true",
          "a weekday's four drills change from week to week, instead of just their order")
    try:
        Path(path).unlink()
    except OSError:
        pass


def main() -> int:
    src = PAGE.read_text(encoding="utf-8")
    entries = check_plan(src)
    if entries:
        check_answers(entries)
    check_kids(src)
    check_wiring(src)
    run_schedule(src)

    if problems:
        for p in problems[:30]:
            print("FAIL  " + p)
        print(f"\nFAIL  {len(problems)} problem(s) with the starter chips")
        return 1
    print(f"PASS  7 days of {len(entries)} adult drills, four a day, each one answered by "
          f"the engine; a new week re-orders the same four; the kid pool has its own "
          f"week and both follow the calendar")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
