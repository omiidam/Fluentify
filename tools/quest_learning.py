#!/usr/bin/env python3
"""Did they learn it - and did they still know it seven days later?

    python3 tools/quest_learning.py [export.json] [--json]

Quest records two kinds of evidence on the device: what she answered item by
item (`items`: right/wrong counts and when it last came up) and any assessment
sitting a baseline, an immediate check, a delayed check and a transfer task.

This reads that export and reports it. It does not invent a number: with no
file, or with a phase that has not been sat, it says so and reports nothing.
Small groups are labelled formative on purpose - two children are a pilot, not
a finding, and the report must not read as one.
"""

import json
import sys
from pathlib import Path

PHASES = ("baseline", "immediate", "delayed7", "transfer")
MIN_GROUP = 3          # below this, a percentage is a story, not a measurement
DAY = 86400000


def load(path):
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def pct(ok, n):
    return round(100.0 * ok / n, 1) if n else None


def summarise(doc):
    items = (doc or {}).get("items") or {}
    out = {"items": len(items), "mastered": 0, "shaky": 0, "stale": 0,
           "phases": {}, "deltas": {}, "notes": []}
    now = int((doc or {}).get("now") or 0)
    for row in items.values():
        if not isinstance(row, dict):
            continue
        r, w = int(row.get("r") or 0), int(row.get("w") or 0)
        at = int(row.get("at") or 0)
        if r >= 2 and w == 0:
            out["mastered"] += 1
        if w > r:
            out["shaky"] += 1
        if now and at and now - at > 7 * DAY:
            out["stale"] += 1

    seen = {}
    for rec in (doc or {}).get("assessments") or []:
        phase = str(rec.get("phase") or "")
        if phase not in PHASES:
            continue
        slot = seen.setdefault(phase, [0, 0])
        slot[1] += 1
        if rec.get("ok"):
            slot[0] += 1
    for phase in PHASES:
        ok, n = seen.get(phase, (0, 0))
        out["phases"][phase] = {"n": n, "correct": ok,
                                "pct": pct(ok, n) if n >= MIN_GROUP else None}
    for a, b in (("baseline", "immediate"), ("immediate", "delayed7"),
                 ("baseline", "transfer"), ("baseline", "delayed7")):
        pa, pb = out["phases"][a]["pct"], out["phases"][b]["pct"]
        if pa is not None and pb is not None:
            out["deltas"][f"{a}->{b}"] = round(pb - pa, 1)
    if out["items"]:
        out["notes"].append(
            "These are the learner's own answers, not a controlled comparison.")
    if any(0 < p["n"] < MIN_GROUP for p in out["phases"].values()):
        out["notes"].append(
            f"A phase with fewer than {MIN_GROUP} answers is formative only.")
    return out


def render(s):
    lines = []
    if not s["items"]:
        lines.append("No assessment data yet: run the protocol in "
                     "docs/heroquest-assessment.md and export the device state.")
        return "\n".join(lines)
    lines.append(f"Items recorded: {s['items']}  mastered: {s['mastered']}  "
                 f"shaky: {s['shaky']}  not seen for a week: {s['stale']}")
    for phase in PHASES:
        p = s["phases"][phase]
        if not p["n"]:
            lines.append(f"  {phase:10s} not sat")
        elif p["pct"] is None:
            lines.append(f"  {phase:10s} {p['correct']}/{p['n']} - too few to "
                         f"call a rate")
        else:
            lines.append(f"  {phase:10s} {p['correct']}/{p['n']} = {p['pct']}%")
    for name, delta in s["deltas"].items():
        lines.append(f"  {name:22s} {delta:+.1f} points")
    for note in s["notes"]:
        lines.append("  note: " + note)
    lines.append("Retention is the number that matters: a correct answer in the "
                 "game that is gone a week later is not a learning outcome.")
    return "\n".join(lines)


def main(argv):
    path = next((a for a in argv if not a.startswith("-")), "")
    doc = load(path)
    s = summarise(doc)
    if "--json" in argv:
        print(json.dumps(s, ensure_ascii=False, indent=2))
    else:
        print(render(s))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
