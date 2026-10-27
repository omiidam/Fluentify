#!/usr/bin/env python3
"""The boot bar and its percentage must never disagree.

The loading screen shows one bar and one number, and the number is what the
learner actually reads. They were painted from the same ratio but through two
different clocks - the bar eased to it over a CSS transition, the label was set
instantly - so the label ran ahead of the bar it was reporting, most visibly at
the end: 100% over a bar still filling.

This runs the Boot module *as shipped* (sliced out of webapp.py's template, not
copied) against a two-element DOM stub, and asserts the four things that matter:

    0% and an empty bar before any section lands
    the label is always Math.round(bar * 100) - never one without the other
    the bar never goes backwards while sections land
    the last section lands on exactly 100% and a full bar

It also asserts that the overlay does not leave while the bar is short of
100%: the number has to finish before the screen does.

    python3 tools/check_boot.py
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEBAPP = ROOT / "webapp.py"
CACHE = ROOT / "tools/.cache"


def slice_boot(src: str) -> str:
    """The Boot IIFE, exactly as it appears in the page."""
    start = src.index("const Boot = (() => {")
    end = src.index("\n})();", start) + len("\n})();")
    return src[start:end]


HARNESS = r"""
/* Two elements and the four globals Boot touches. Nothing else is stubbed, so
   anything the module starts reaching for fails loudly here rather than in the
   app. */
const makeEl = (tag) => ({
  tagName: tag.toUpperCase(), style: {}, textContent: '', className: '',
  parentNode: { removeChild() {} },
  classList: { add() {}, remove() {}, contains: () => false },
});
const fill = makeEl('i');
const pct = makeEl('span');
const bootEl = makeEl('div');
const boot = makeEl('div');

global.document = {
  hidden: false,
  getElementById: (id) => ({
    bootfill: fill, bootpct: pct, boot: bootEl, input: makeEl('input'),
  })[id] || null,
  createElement: makeEl,
  addEventListener() {},
};
global.window = {
  matchMedia: () => ({ matches: false }),
  addEventListener() {},
};
global.input = makeEl('input');
global.performance = { now: () => Date.now() };

const problems = [];
const check = (ok, what) => { if (!ok) problems.push(what); return ok; };

__BOOT__

const bar = () => parseFloat((fill.style.transform.match(/scaleX\(([\d.]+)\)/) || [0, '0'])[1]);
const say = () => pct.textContent;
const states = [];
let watcher = setInterval(() => {
  states.push({bar: bar(), label: say()});
  if (states.length > 400) clearInterval(watcher);
}, 10);

const wait = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  /* before a single section has landed */
  check(say() === '0%', 'the label starts at ' + say() + ', not 0%');
  check(bar() === 0, 'the bar starts at ' + bar() + ', not empty');

  /* seven sections, landing the way the real boot lands them */
  for (let i = 1; i <= 7; i++) {
    Boot.step(i, 7);
    await wait(120);
  }
  await wait(900);
  clearInterval(watcher);

  const worst = states.find((s) => parseFloat(s.label) !== Math.round(s.bar * 100));
  check(!worst, 'label ' + (worst && worst.label) + ' over a bar at ' +
        (worst && worst.bar) + ': the two are on different clocks');

  let back = null;
  for (let i = 1; i < states.length; i++)
    if (states[i].bar < states[i - 1].bar - 1e-9) back = states[i].bar;
  check(!back, 'the bar went backwards, to ' + back);

  check(say() === '100%', 'the boot finished on ' + say() + ', not 100%');
  check(Math.abs(bar() - 1) < 1e-9, 'the boot finished with the bar at ' + bar());

  /* and it is still up: the 5s floor has not passed, so nothing has left */
  check(!global.__hidden, 'the overlay left before its floor');

  console.log(JSON.stringify({
    paints: states.length, problems,
    first: states[0], last: states[states.length - 1],
  }));
  process.exit(problems.length ? 1 : 0);
})();
"""


def main() -> int:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else WEBAPP
    src = target.read_text(encoding="utf-8")
    try:
        boot = slice_boot(src)
    except ValueError:
        print("FAIL  the Boot module is not where this check looks for it")
        return 1

    if "step(done, total)" not in boot or "paint()" not in boot:
        print("FAIL  the Boot module no longer exposes step() / paint()")
        return 1

    # The running check below cannot see the stylesheet, and the bug this file
    # exists for lived there as much as in the script: the bar eased to its new
    # value over a CSS transition while the label was set at once, so a JS-only
    # check passed while the screen disagreed with itself. Two structural
    # guards, because they are what makes the runtime assertions meaningful:
    # one writer for both readouts, and no transition on the bar.
    problems = []
    body = boot[boot.index("function paint()"):]
    body = body[:body.index("\n  }")]
    for what, needle in (("the bar", "fill.style.transform"),
                         ("the label", "pct.textContent")):
        if needle not in body:
            problems.append(f"paint() no longer writes {what}")
    for what, needle in (("the bar", "fill.style.transform"),
                         ("the label", "pct.textContent")):
        if boot.count(needle) != 1:
            problems.append(
                f"{needle} is written in {boot.count(needle)} places: the bar "
                f"and the percentage have two clocks again")

    track = re.search(r"\.boot-track i \{[^}]*\}", src)
    if not track:
        problems.append("the .boot-track i rule is gone")
    elif "transition" in track.group(0):
        problems.append("the bar transitions again: it eases while the "
                        "percentage jumps, which is the bug")

    if problems:
        for p in problems:
            print("FAIL  " + p)
        return 1

    if not shutil.which("node"):
        # Not a build gate: the APK build runs node --check on the page already.
        # Saying so is better than a suite that quietly proves nothing.
        print("SKIP  node is not installed - the boot bar was not exercised")
        return 0

    CACHE.mkdir(parents=True, exist_ok=True)
    script = CACHE / "boot_check.js"
    script.write_text(HARNESS.replace("__BOOT__", boot), encoding="utf-8")

    proc = subprocess.run(["node", str(script)], capture_output=True, text=True)
    out = proc.stdout.strip().split("\n")[-1] if proc.stdout.strip() else ""
    if proc.returncode != 0:
        detail = ""
        try:
            payload = json.loads(out)
            detail = "; ".join(payload.get("problems", []))
        except json.JSONDecodeError:
            detail = (proc.stderr or out).strip()[:400]
        print("FAIL  " + (detail or "the boot bar check did not pass"))
        return 1

    payload = json.loads(out)
    print(f"PASS  the bar and the percentage agree over {payload['paints']} paints, "
          f"0% -> 100%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
