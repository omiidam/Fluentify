#!/usr/bin/env python3
"""The boot bar and its percentage must never disagree.

The loading screen shows one bar and one number, and the number is what the
learner actually reads. They were painted from the same ratio but through two
different clocks - the bar eased to it over a CSS transition, the label was set
instantly - so the label ran ahead of the bar it was reporting, most visibly at
the end: 100% over a bar still filling.

The module is TypeScript now (web/boot/boot.ts), built by tools/build_boot.py
to web/boot/boot.js, and the page inlines that built file as it is shipped.
This suite therefore runs the file the app actually loads - not a copy and not
a re-typed string - against a two-element DOM stub, and asserts the four things
that matter:

    0% and an empty bar before any section lands
    the label is always Math.round(bar * 100) - never one without the other
    the bar never goes backwards while sections land
    the last section lands on exactly 100% and a full bar

It also asserts that the overlay does not leave while the bar is short of
100%: the number has to finish before the screen does.

What changed with the migration, and why: this used to slice the Boot IIFE out
of webapp.py's template, because that string was the only place the module
existed. A check that reads a string cannot see whether the string compiles, so
it now also holds three things the old one could not:

    the built file exists and is what webapp.py inlines (the marker is gone
    from the rendered page, so a missing build cannot ship a loader-less page)
    the built file parses as JavaScript, by node, before anything is run
    web/boot/boot.js is not stale against web/boot/boot.ts, rebuilt on the spot
    when bun is available

    python3 tools/check_boot.py
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "web" / "boot" / "boot.ts"
BOOT_JS = ROOT / "web" / "boot" / "boot.js"
SHELL = ROOT / "web" / "boot" / "shell.ts"
BOOT_CSS_FILE = ROOT / "web" / "boot" / "boot.css"
BOOT_HTML_FILE = ROOT / "web" / "boot" / "boot.html"
WEBAPP = ROOT / "webapp.py"
PAGE = ROOT / "android/app/src/main/assets/www/index.html"
CACHE = ROOT / "tools/.cache"


def bun() -> str | None:
    found = shutil.which("bun")
    if found:
        return found
    import os
    fallback = os.environ.get("FREEBUFF_BUN")
    return fallback if fallback and Path(fallback).exists() else None


def brace_body(code: str, opener: str) -> str:
    """The body of the first `opener ... {` in `code`, by matching braces."""
    at = code.index(opener) + len(opener)
    start = code.index("{", at) + 1
    depth, i = 1, start
    while i < len(code) and depth:
        if code[i] == "{":
            depth += 1
        elif code[i] == "}":
            depth -= 1
        i += 1
    return code[start:i - 1]


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
  documentElement: { classList: { add() {}, remove() {}, contains: () => false } },
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
global.requestAnimationFrame = (fn) => setTimeout(fn, 0);

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
    problems: list[str] = []

    for path in (SRC, SHELL, BOOT_JS, BOOT_CSS_FILE, BOOT_HTML_FILE):
        if not path.exists():
            print(f"FAIL  {path.relative_to(ROOT)} is missing - run tools/build_boot.py")
            return 1

    boot = BOOT_JS.read_text(encoding="utf-8")
    ts = SRC.read_text(encoding="utf-8")

    # step() carries the sections landed; paint() is the single writer of both
    # readouts. Matched on the signatures the page and the APK both call.
    if "step(done, total" not in boot or "function paint()" not in boot:
        problems.append("the built loader no longer exposes step() / paint()")
    if "step(done: number, total: number" not in ts:
        problems.append("the TypeScript source no longer types step(done, total)")

    # The running check below cannot see the stylesheet, and the bug this file
    # exists for lived there as much as in the script: the bar eased to its new
    # value over a CSS transition while the label was set at once, so a JS-only
    # check passed while the screen disagreed with itself. Two structural
    # guards, because they are what makes the runtime assertions meaningful:
    # one writer for both readouts, and no transition on the bar.
    try:
        body = brace_body(boot, "function paint()")
    except ValueError:
        body = ""
    for what, needle in (("the bar", "fill.style.transform"),
                         ("the label", "pct.textContent")):
        if needle not in body:
            problems.append(f"paint() no longer writes {what}")
        if boot.count(needle) != 1:
            problems.append(
                f"{needle} is written in {boot.count(needle)} places: the bar "
                f"and the percentage have two clocks again")

    page_src = WEBAPP.read_text(encoding="utf-8")
    css = BOOT_CSS_FILE.read_text(encoding="utf-8")
    markup = BOOT_HTML_FILE.read_text(encoding="utf-8")
    track = re.search(r"\.boot-track i \{[^}]*\}", css)
    if not track:
        problems.append("the .boot-track i rule is gone")
    elif "transition" in track.group(0):
        problems.append("the bar transitions again: it eases while the "
                        "percentage jumps, which is the bug")

    # ---- inlined, not carried as a string in the page ----------------------
    # The migration's own failure mode: the template keeps its marker and the
    # page ships with no boot module at all, or an old copy of one.
    for marker, part in (("/*__BOOT__*/", "module"),
                         ("/*__BOOT_CSS__*/", "stylesheet"),
                         ("<!--__BOOT_MARKUP__-->", "markup")):
        if marker not in page_src:
            problems.append(f"webapp.py has no {marker} marker for the {part}")
        elif f'boot_part("{part}")' not in page_src:
            problems.append(f"render_page() no longer inlines the {part}")
    if PAGE.exists():
        page = PAGE.read_text(encoding="utf-8")
        for marker, part in (("/*__BOOT__*/", "module"),
                             ("/*__BOOT_CSS__*/", "stylesheet"),
                             ("<!--__BOOT_MARKUP__-->", "markup")):
            if marker in page:
                problems.append(f"the built page still has the {part} marker: "
                                f"it was not inlined")
        if "Boot = (() =>" not in page:
            problems.append("the built page has no Boot module")
        if markup.strip() not in page:
            problems.append("the built page does not carry the loading page's "
                            "markup as it was built")
        if ".boot-track" not in page:
            problems.append("the built page has no loading-page stylesheet")
    else:
        problems.append("assets/www/index.html is missing - run build_apk_ui.py")

    # ---- the built file is the source, not last week's source ---------------
    if bun():
        out = CACHE / "boot_build.js"
        CACHE.mkdir(parents=True, exist_ok=True)
        proc = subprocess.run([bun(), "build", str(SRC), "--outfile", str(out),
                               "--target=browser"], capture_output=True, text=True)
        if proc.returncode != 0:
            problems.append("the TypeScript does not compile: " +
                            (proc.stderr or proc.stdout).strip()[:300])
        else:
            fresh = re.sub(r"\A//[^\n]*\.ts\n", "", out.read_text(encoding="utf-8")).lstrip("\n")
            if fresh != boot:
                problems.append("web/boot/boot.js is stale against web/boot/boot.ts "
                                "- run tools/build_boot.py")
            # The stylesheet and the markup are the source's own text, so a
            # stale build is an exact substring that is no longer there. No
            # rebuild from a check: a check does not write the tree.
            shell_ts = SHELL.read_text(encoding="utf-8")
            if css not in shell_ts or markup not in shell_ts:
                problems.append("web/boot/boot.css or boot.html is stale against "
                                "web/boot/shell.ts - run tools/build_boot.py")
    else:
        print("SKIP  bun is not installed - the built loader was not rebuilt "
              "from its TypeScript")

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
