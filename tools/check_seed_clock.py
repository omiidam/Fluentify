#!/usr/bin/env python3
"""The daily-seed clock, under a pinned clock.

The composer locks at fifty messages until 03:30 GMT, and the countdown under
the rail is the only thing telling a learner when that is. It is easy to get
wrong in ways nothing else notices:

  * the session day and the countdown were computed from two different ideas
    of the boundary, so the meter could reset while the note still counted
    hours;
  * the countdown was written once, when a message was sent, so a screen left
    open overnight showed the number from the evening before;
  * the reset was only ever re-read on a send, and a locked composer cannot
    send, so the app never unlocked itself at 03:30 GMT at all.

This runs the shipped Seed code - sliced out of webapp.py, not copied - against
a fake clock and compares it to an independent calculation of "the next 03:30
UTC" for a day of instants, including both sides of the boundary.

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

# The session rolls over at 03:30 UTC, in the app's own words.
RESET = (3, 30)

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
    # The object reads SEED_GOAL and SEED_RESET_UTC, which are declared beside
    # it; taking the object alone would throw on the first call.
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
    """The next 03:30 UTC after this instant, and its countdown in words."""
    t = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    boundary = t.replace(hour=RESET[0], minute=RESET[1], second=0, microsecond=0)
    if boundary <= t:
        boundary += timedelta(days=1)
    ms = int((boundary - t).total_seconds() * 1000)
    if ms < 60000:
        text = "under a minute"
    else:
        mins = ms // 60000
        h, m = divmod(mins, 60)
        text = f"{h}h {m:02d}m" if h else f"{m}m"
    # the session day is the UTC date of (now - 3h30m)
    day = (t - timedelta(hours=RESET[0], minutes=RESET[1])).date().isoformat()
    return day, ms, text


def main() -> int:
    if not shutil.which("node"):
        print("check_seed_clock: node is not installed")
        return 2
    src = WEBAPP.read_text(encoding="utf-8")

    problems: list[str] = []

    # ---- the clock itself, at every hour of a day plus both edges ----------
    cases = [f"2026-10-28T{h:02d}:00:00Z" for h in range(24)]
    cases += [
        "2026-10-28T02:59:59Z",   # a minute before the roll, still yesterday
        "2026-10-28T03:29:00Z",   # under the last hour of the session
        "2026-10-28T03:29:59Z",
        "2026-10-28T03:30:00Z",   # exactly the boundary: a fresh session
        "2026-10-28T03:30:31Z",   # just after it
        "2026-10-28T20:13:00Z",
        "2026-03-29T01:15:00Z",   # a European DST night, which is not UTC's
        "2026-12-31T23:59:59Z",   # a year boundary
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
                "the day has to roll at 03:30 GMT, not at midnight")
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
            "a tab that was asleep at 03:30 comes back to a locked composer "
            "until it is reloaded")
    # The tick has to be able to unlock: rolling the day must repaint.
    tick = re.search(r"tick\(\) \{(.*?)\n  \},", src, re.S)
    if not tick or "rollDay()" not in tick.group(1) or "paint()" not in tick.group(1):
        problems.append(
            "tick() does not roll the day and repaint, so 03:30 GMT arrives "
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

    print(f"checked the seed clock at {len(got)} instants (03:30 GMT reset)")
    if problems:
        print(f"\nFAIL  {len(problems)} problems\n")
        for p in problems:
            print(f"  {p}")
        return 1
    print("PASS  the session rolls at 03:30 GMT and the countdown matches it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
