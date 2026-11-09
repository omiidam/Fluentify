#!/usr/bin/env python3
"""Error log: does a mistake the app already diagnosed ever add up?

The app has always known more about a learner's mistakes than it showed: a level
item carries its subskill, the weekly quiz knows which word it asked, a drill
knows which partner it wanted. Each was rendered once and forgotten. This suite
runs the page's ledger in node and checks the parts that would fail silently:

  note      one miss is one event, and the card behind it is kept so the drill
            can ask the same question again
  rank      classes are ordered by count, then by recency; the label travels
  drill     the newest cards for one class, and never another class's cards
  bounded   four hundred events and eighty cards: a drill on a phone must not
            grow a record that cannot be rewritten
  corrupt   a rubbish record reads as empty instead of taking the panel down
  wiring    the level check, the weekly quiz and the drills all write here, and
            the account panel and the sheet both read it

    python3 tools/check_errors.py
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEBAPP = ROOT / "webapp.py"
BUILT = ROOT / "android/app/src/main/assets/www/index.html"
CACHE = ROOT / "tools/.cache"

problems: list[str] = []


def fail(what: str) -> None:
    problems.append(what)


def check(ok: bool, what: str) -> bool:
    if not ok:
        fail(what)
    return ok


def block(src: str) -> str:
    start = src.index("/* --- error log: pure")
    end = src.index("/* --- end error log", start)
    return src[start:end]


HARNESS = r"""
const fs = require('fs');
const vm = require('vm');
const outPath = process.argv[2];

const mem = {};
global.localStorage = {
  getItem: (k) => (k in mem ? mem[k] : null),
  setItem: (k, v) => { mem[k] = String(v); },
  removeItem: (k) => { delete mem[k]; },
};

__BLOCK__

const problems = [];
const check = (ok, what) => { if (!ok) problems.push(what); return ok; };
const out = {};

const card = (id, en) => ({
  id: id, kind: 'choice',
  prompt: {en: en, fa: 'فا'}, options: ['a', 'b', 'c'], answer: 1,
  why: {en: 'because', fa: ''}, detail: {en: 'detail', fa: ''},
});
const cls = (key, en) => ({key: key, en: en, fa: 'فا'});

{
  let st = ErrorLog.read();
  check(Object.keys(st.cards).length === 0 && st.events.length === 0,
    'a fresh install already has a record');
  check(ErrorLog.total(st) === 0, 'a fresh install already counts misses');

  st = ErrorLog.note(st, cls('grammar:articles', 'Articles'), card('i1', 'A cat'), '2026-11-01');
  st = ErrorLog.note(st, cls('grammar:articles', 'Articles'), card('i2', 'An apple'), '2026-11-02');
  st = ErrorLog.note(st, cls('collocation', 'Word partners'), card('c1', 'heavy rain'), '2026-11-03');
  st = ErrorLog.write(st);
  st = ErrorLog.read();

  check(st.events.length === 3, 'three misses did not make three events');
  check(ErrorLog.total(st) === 3, 'the total does not match the events');
  const ranked = ErrorLog.rank(st);
  out.ranked = ranked.map((r) => [r.key, r.count]);
  check(ranked.length === 2, 'two classes were reported as ' + ranked.length);
  check(ranked[0].key === 'grammar:articles' && ranked[0].count === 2,
    'the more frequent class is not first');
  check(ranked[0].en === 'Articles', 'the class label did not travel with the count');
  check(ranked[1].key === 'collocation', 'the second class is wrong: ' + ranked[1].key);

  const drill = ErrorLog.drill(st, 'grammar:articles', 5);
  check(drill.length === 2, 'the drill did not return both questions for the class');
  check(drill.every((c) => c.c === 'grammar:articles'), 'the drill mixed two classes');
  check(drill[0].id === 'i2', 'the drill is not newest-first: ' + drill[0].id);
  check(drill[0].options.length === 3 && drill[0].answer === 1,
    'the card lost its options or its key');
  check(ErrorLog.drill(st, 'nothing', 5).length === 0, 'an empty class returned cards');

  /* the same question missed twice is one card, not two */
  st = ErrorLog.note(st, cls('grammar:articles', 'Articles'), card('i1', 'A cat'), '2026-11-04');
  check(Object.keys(st.cards).length === 3, 'the same question was stored twice');
  const again = ErrorLog.drill(st, 'grammar:articles', 5);
  check(again[0].id === 'i1', 'the repeated question did not move to the front');
  check(st.events.length === 4, 'a repeat did not count as a second miss');
}

/* ---- bounded ------------------------------------------------------------- */
{
  let st = ErrorLog.read();
  for (let i = 0; i < ErrorLog.EVENTS + 60; i++) {
    st = ErrorLog.note(st, cls('x', 'X'), card('q' + i, 'q'), '2026-01-01');
  }
  st = ErrorLog.write(st);
  check(st.events.length === ErrorLog.EVENTS,
    'events were not capped at ' + ErrorLog.EVENTS + ': ' + st.events.length);
  check(Object.keys(st.cards).length === ErrorLog.CARDS,
    'cards were not capped at ' + ErrorLog.CARDS + ': ' + Object.keys(st.cards).length);
  check(!Object.keys(st.cards).some((k) => k === 'x|q0'),
    'the cap kept the oldest question instead of the newest');
}

/* ---- corrupt ------------------------------------------------------------- */
{
  mem[ErrorLog.KEY] = 'not json';
  check(ErrorLog.read().events.length === 0, 'a corrupt record threw');
  mem[ErrorLog.KEY] = '{"events":[{"c":"ok","d":"2026-01-01"},{"nope":1}],"cards":{"a":{"prompt":{}}}}';
  const odd = ErrorLog.read();
  check(odd.events.length === 1, 'a malformed event survived the read');
  check(Object.keys(odd.cards).length === 1, 'a card with no prompt was dropped as if valid');
  check(odd.cards.a.kind === 'choice', 'a card with no kind was not normalised');
}

out.problems = problems;
fs.writeFileSync(outPath, JSON.stringify(out));
console.log('ranked', (out.ranked || []).length, 'classes');
"""


def run_block() -> dict:
    if not shutil.which("node"):
        print("SKIP  node is not installed - the error log was not exercised")
        return {}
    src = WEBAPP.read_text(encoding="utf-8")
    try:
        body = block(src)
    except ValueError:
        fail("webapp.py: the error log block markers are gone")
        return {}
    CACHE.mkdir(parents=True, exist_ok=True)
    script = CACHE / "errors_check.js"
    script.write_text(HARNESS.replace("__BLOCK__", body), encoding="utf-8")
    out = CACHE / "errors_out.json"
    proc = subprocess.run(["node", str(script), str(out)], capture_output=True, text=True)
    if proc.returncode != 0:
        fail("node failed on the error log block: " +
             (proc.stderr or proc.stdout).strip()[:400])
        return {}
    payload = json.loads(out.read_text())
    for p in payload.get("problems") or []:
        fail(p)
    for f in (script, out):
        f.unlink(missing_ok=True)
    return payload


def wiring() -> None:
    src = WEBAPP.read_text(encoding="utf-8")
    check("const ErrorLog = {" in src, "the error log is not in the page")
    check("ErrorLog.note(log," in src, "the level check does not record its misses")
    check("recordMisses(a);" in src, "finishing the level check does not call the recorder")
    check("recordWeek(quiz, picks);" in src, "the weekly quiz does not record its misses")
    check("ErrorLog.drill(" in src, "nothing can ask the missed questions again")
    check('id="acslip"' in src, "the account panel has no place for the profile")
    check("Slip.html()" in src, "the profile is never painted into the account panel")
    check("Practice.open('slip'" in src, "the profile's Practice button goes nowhere")
    check("fluentify.errors.v1" in src, "the log has no storage key")
    if BUILT.exists():
        built = BUILT.read_text(encoding="utf-8")
        check("ErrorLog" in built, "the built page does not carry the error log")
        check('id="acslip"' in built, "the built page has no profile block")


def main() -> int:
    run_block()
    wiring()
    if problems:
        for p in problems[:40]:
            print("FAIL  " + p)
        print(f"\nFAIL  {len(problems)} problem(s) with the error log")
        return 1
    print("PASS  error log: the level check, the weekly quiz and the drills all write "
          "one record, classes rank by how often they happen, the drill re-asks the "
          "questions that were missed, and the account panel shows the result")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
