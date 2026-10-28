#!/usr/bin/env python3
"""The daily-seed clock, under a pinned clock.

The composer locks at fifty messages until midnight in Tehran (GMT+3:30, which
is 20:30 UTC), and the countdown under the rail is the only thing telling a
learner when that is. It is easy to get wrong in ways nothing else notices:

  * the session day and the countdown were computed from two different ideas
    of the boundary, so the meter could reset while the note still counted
    hours;
  * the countdown was written once, when a message was sent, so a screen left
    open overnight showed the number from the evening before;
  * the reset was only ever re-read on a send, and a locked composer cannot
    send, so the app never unlocked itself at the boundary at all.

This runs the shipped Seed code - sliced out of webapp.py, not copied - against
a fake clock and compares it to an independent calculation of "the next
midnight at GMT+3:30" for a day of instants, including both sides of it.

    python3 tools/check_seed_clock.py
"""

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEBAPP = ROOT / "webapp.py"

# The session rolls over at 00:00 in Tehran. Iran has had no DST since 2022,
# so this is a fixed offset: the boundary instant is 20:30 UTC every day.
TZ_MIN = 210


HARNESS = r"""
let NOW = 0;
class FakeDate extends Date {
  constructor(...a) { if (a.length === 0) super(NOW); else super(...a); }
  static now() { return NOW; }
}
global.Date = FakeDate;
global.document = {
  hidden: false,
  getElementById: () => null,
  addEventListener() {},
};
global.localStorage = { getItem: () => null, setItem() {} };
global.setInterval = () => 0;
global.clearInterval = () => {};
global.input = { disabled: false };
global.sendbtn = { disabled: false };

__SEED__

const out = JSON.parse(process.env.CASES).map((iso) => {
  NOW = Date.parse(iso);
  return { iso, key: Seed.key(), ms: Seed.msLeft(), text: Seed.msText() };
});
console.log(JSON.stringify(out));
"""


def slice_seed(src: str) -> str:
    # The object reads SEED_GOAL and SEED_TZ_MIN, which are declared beside it;
    # taking the object alone would throw on the first call.
    head = "\n".join(re.findall(r"^const SEED_[A-Z_]+ = .*$", src, re.M))
    start = src.index("const Seed = {")
    i = src.index("{", start)
    depth, j = 0, i
    while j < len(src):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                return head + "\n" + src[start:j + 1] + ";"
        j += 1
    raise SystemExit("check_seed_clock: could not find the end of the Seed object")


def expected(iso: str) -> tuple[str, int, str]:
    """The next midnight in Tehran after this instant, and its countdown."""
    t = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    # The local clock, carried as a UTC-labelled datetime: the wall time is what
    # matters here, not the zone it is measured against.
    local = t + timedelta(minutes=TZ_MIN)
    boundary = datetime(local.year, local.month, local.day,
                        tzinfo=timezone.utc) + timedelta(days=1)
    ms = int((boundary - local).total_seconds() * 1000)
    if ms < 60000:
        text = "under a minute"
    else:
        mins = ms // 60000
        h, m = divmod(mins, 60)
        text = f"{h}h {m:02d}m" if h else f"{m}m"
    # the session day is the date on that local clock
    return local.date().isoformat(), ms, text


def main() -> int:
    if not shutil.which("node"):
        print("check_seed_clock: node is not installed")
        return 2
    src = WEBAPP.read_text(encoding="utf-8")

    problems: list[str] = []

    # ---- the clock itself, at every hour of a day plus both edges ----------
    cases = [f"2026-10-28T{h:02d}:00:00Z" for h in range(24)]
    cases += [
        "2026-10-28T20:29:00Z",   # 23:59 Tehran - the last minute of the day
        "2026-10-28T20:29:59Z",   # the instant in the user's own example
        "2026-10-28T20:30:00Z",   # 00:00 Tehran: a fresh session
        "2026-10-28T20:30:31Z",   # just after it
        "2026-10-28T03:30:00Z",   # 07:00 Tehran - mid-morning, mid-session
        "2026-10-28T21:14:00Z",   # 00:44 Tehran, half a day to go
        "2026-10-28T19:59:00Z",   # 23:29 Tehran, under the last half hour
        "2026-03-29T01:15:00Z",   # a European DST night, which is not Iran's
        "2026-12-31T19:45:00Z",   # New Year's Eve, 23:15 in Tehran
        "2026-12-31T20:45:00Z",   # 00:15 on 1 January 2027 in Tehran
    ]
    harness = HARNESS.replace("__SEED__", slice_seed(src))
    proc = subprocess.run(["node", "-e", harness], capture_output=True,
                          text=True, env={**os.environ, "CASES": json.dumps(cases)})
    if proc.returncode != 0:
        print(proc.stderr.strip()[:800])
        print("FAIL  the Seed module does not run under a pinned clock")
        return 1
    got = json.loads(proc.stdout)

    for row in got:
        day, ms, text = expected(row["iso"])
        if row["key"] != day:
            problems.append(
                f"{row['iso']}: session key {row['key']!r}, expected {day!r} - "
                "the day has to roll at midnight in Tehran (20:30 UTC), not at "
                "midnight UTC and not at 03:30")
        if row["ms"] != ms:
            problems.append(
                f"{row['iso']}: countdown {row['ms']} ms, expected {ms} ms - "
                f"that is {row['ms'] / 3600000:.2f}h against {ms / 3600000:.2f}h")
        if row["text"] != text:
            problems.append(
                f"{row['iso']}: says {row['text']!r}, should say {text!r}")
        if row["ms"] < 0 or row["ms"] > 24 * 3600 * 1000:
            problems.append(f"{row['iso']}: countdown out of range: {row['ms']}")

    # ---- and the two things that keep it live ------------------------------
    if "Seed.timer = setInterval(() => Seed.tick(), 30000)" not in src:
        problems.append(
            "nothing repaints the countdown: it is written once per message and "
            "then freezes, which is how a screen read the next morning still "
            "counted the hours from the evening before")
    if not re.search(r"addEventListener\('visibilitychange'.{0,80}Seed\.tick\(\)",
                     src, re.S):
        problems.append(
            "a tab that was asleep at the roll comes back to a locked composer "
            "until it is reloaded")
    # The tick has to be able to unlock: rolling the day must repaint.
    tick = re.search(r"tick\(\) \{(.*?)\n  \},", src, re.S)
    if not tick or "rollDay()" not in tick.group(1) or "paint()" not in tick.group(1):
        problems.append(
            "tick() does not roll the day and repaint, so the boundary arrives "
            "without the composer coming back")

    # ---- the note speaks one language --------------------------------------
    note = re.search(r"noteText\(\) \{(.*?)\n  \},", src, re.S)
    if not note:
        problems.append("there is no noteText() to write the countdown")
    else:
        persian = re.findall(r"[\u0600-\u06FF][\u0600-\u06FF\s]*", note.group(1))
        if persian:
            problems.append(
                "the limit note still carries Persian under the English "
                f"({persian[0][:24]!r}): it is app chrome, not a lesson")

    print(f"checked the seed clock at {len(got)} instants "
          "(00:00 GMT+3:30 reset)")
    if problems:
        print(f"\nFAIL  {len(problems)} problems\n")
        for p in problems:
            print(f"  {p}")
        return 1
    print("PASS  the session rolls at 00:00 GMT+3:30 and the countdown matches it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
