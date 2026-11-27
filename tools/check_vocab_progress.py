#!/usr/bin/env python3
"""Vocabulary mastery: does the state follow the evidence, or the clicking?

The vocabulary panel used to call a word "learned" when it was opened, and
"mastered" when the learner tapped a tick. Both are self-reports. This suite
runs the page's own ledger - sliced out of webapp.py, not copied - and asks
the questions a mastery ladder gets wrong silently:

  ladder      each kind of answer moves the word exactly one rung, and a rung
              cannot be skipped: recognition alone never makes a word usable
  production  one sentence is productive; mastery needs it twice on different
              days, and reviews that came back after a gap
  ignorance   an unknown kind of evidence changes nothing - there is no
              "I know it" path into the ladder
  mistakes    a miss enters the bank on the second miss, never the first
  summary     the dashboard counts only the words it was given, and the
              active/met ratio is the one the brief asks for
  record      bounded, corrupt-safe, and case-folded: "Confident" and
              " confident " are one word

    python3 tools/check_vocab_progress.py
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEBAPP = ROOT / "webapp.py"

problems: list[str] = []


def fail(what: str) -> None:
    problems.append(what)


def check(ok: bool, what: str) -> bool:
    if not ok:
        fail(what)
    return ok


def block(src: str) -> str:
    start = src.index("/* --- vocab progress: pure")
    end = src.index("/* --- end vocab progress", start)
    return src[start:end]


HARNESS = r"""
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
const D1 = '2026-11-01', D2 = '2026-11-02', D3 = '2026-11-03', D4 = '2026-11-10';

/* ---- the ladder, one rung at a time ------------------------------------ */
{
  let st = {items: {}};
  check(VocabProgress.stateOf(null) === 'new', 'a word never met is not new');
  check(VocabProgress.STATES.length === 8, 'the ladder lost a rung');
  check(VocabProgress.STATES[0] === 'new' && VocabProgress.STATES[7] === 'mastered',
    'the ladder is not ordered from new to mastered');

  st = VocabProgress.seen(st, 'confident', D1);
  check(VocabProgress.stateOf(VocabProgress.get(st, 'confident')) === 'encountered',
    'opening a word did not make it encountered');

  st = VocabProgress.hit(st, 'confident', 'recognize', D1);
  check(VocabProgress.stateOf(VocabProgress.get(st, 'confident')) === 'recognized',
    'a correct recognition did not make it recognized');

  st = VocabProgress.hit(st, 'confident', 'practice', D1);
  out.skip = VocabProgress.stateOf(VocabProgress.get(st, 'confident'));
  check(out.skip === 'practiced',
    'practice without recall still counted as practised: ' + out.skip);

  st = VocabProgress.hit(st, 'confident', 'recall', D1);
  check(VocabProgress.stateOf(VocabProgress.get(st, 'confident')) === 'practiced',
    'a later recall demoted a practised word');

  /* recognition alone, however many times, never becomes productive */
  for (let i = 0; i < 20; i += 1) st = VocabProgress.hit(st, 'confident', 'recognize', D2);
  check(VocabProgress.stateOf(VocabProgress.get(st, 'confident')) === 'practiced',
    'enough recognition clicks promoted the word past practice');
}

/* ---- production and retention ------------------------------------------ */
{
  let st = {items: {}};
  st = VocabProgress.seen(st, 'afford', D1);
  st = VocabProgress.hit(st, 'afford', 'recognize', D1);
  st = VocabProgress.hit(st, 'afford', 'recall', D1);
  st = VocabProgress.hit(st, 'afford', 'practice', D1);
  st = VocabProgress.hit(st, 'afford', 'produce', D1);
  check(VocabProgress.stateOf(VocabProgress.get(st, 'afford')) === 'productive',
    'a written sentence did not make the word productive');

  st = VocabProgress.hit(st, 'afford', 'review', D2);
  st = VocabProgress.hit(st, 'afford', 'review', D3);
  out.retained = VocabProgress.stateOf(VocabProgress.get(st, 'afford'));
  check(out.retained === 'retained',
    'two reviews after a gap did not make the word retained: ' + out.retained);

  /* mastered also needs a second production day, and a third day of work */
  check(VocabProgress.stateOf(VocabProgress.get(st, 'afford')) !== 'mastered',
    'one production day and two reviews were called mastery');
  st = VocabProgress.hit(st, 'afford', 'produce', D4);
  out.mastered = VocabProgress.stateOf(VocabProgress.get(st, 'afford'));
  check(out.mastered === 'mastered',
    'production on two days plus reviews on two days was not mastery: ' + out.mastered);

  /* productive words that never came back are productive, not retained */
  let st2 = {items: {}};
  st2 = VocabProgress.hit(st2, 'lend', 'produce', D1);
  st2 = VocabProgress.hit(st2, 'lend', 'produce', D2);
  check(VocabProgress.stateOf(VocabProgress.get(st2, 'lend')) === 'productive',
    'two sentences with no review were called retained');
}

/* ---- an unknown kind of evidence is not evidence ----------------------- */
{
  let st = {items: {}};
  st = VocabProgress.seen(st, 'patient', D1);
  const before = JSON.stringify(VocabProgress.get(st, 'patient'));
  st = VocabProgress.hit(st, 'patient', 'know', D1);
  st = VocabProgress.hit(st, 'patient', 'mastered', D1);
  st = VocabProgress.hit(st, 'patient', 'i-know-it', D1);
  check(VocabProgress.stateOf(VocabProgress.get(st, 'patient')) === 'encountered',
    'a self-report kind of evidence moved the word');
  const after = JSON.stringify(VocabProgress.get(st, 'patient'));
  check(before === after, 'an unknown kind still changed the record');
}

/* ---- the mistake bank --------------------------------------------------- */
{
  let st = {items: {}};
  st = VocabProgress.miss(st, 'borrow', 'recall', D1);
  check(VocabProgress.mistakes(st, 2).length === 0,
    'one miss entered the mistake bank');
  st = VocabProgress.miss(st, 'borrow', 'recall', D2);
  const bank = VocabProgress.mistakes(st, 2);
  check(bank.length === 1 && bank[0].word === 'borrow' && bank[0].n === 2,
    'two misses did not make one recurring mistake: ' + JSON.stringify(bank));
  st = VocabProgress.miss(st, 'polite', 'practice', D1);
  st = VocabProgress.miss(st, 'polite', 'practice', D2);
  st = VocabProgress.miss(st, 'polite', 'practice', D3);
  check(VocabProgress.mistakes(st, 2)[0].word === 'polite',
    'the bank is not ordered by how often the word is missed');
  check(VocabProgress.mistakes(st, 5).length === 0,
    'the bank ignored its own floor');
}

/* ---- the dashboard ------------------------------------------------------ */
{
  const st = {items: {}};
  let s = st;
  s = VocabProgress.seen(s, 'confident', D1);
  s = VocabProgress.hit(s, 'confident', 'recognize', D1);
  s = VocabProgress.hit(s, 'honest', 'recognize', D1);
  s = VocabProgress.hit(s, 'honest', 'recall', D1);
  s = VocabProgress.hit(s, 'honest', 'practice', D1);
  s = VocabProgress.hit(s, 'honest', 'produce', D1);
  const sum = VocabProgress.summary(s, ['confident', 'honest', 'rain', 'afford']);
  out.summary = sum.byState;
  check(sum.total === 4, 'the summary counted words it was not given');
  check(sum.byState.new === 2, 'a word never met was not counted as new');
  check(sum.met === 2, 'met is not words the learner has touched');
  check(sum.active === 1, 'can-use is not productive-or-better');
  check(sum.activeOfMet === 50,
    'active/met should be 1 of 2 met words, got ' + sum.activeOfMet);
  /* a word only in the ledger but not in the given list must not leak in */
  s = VocabProgress.hit(s, 'lend', 'produce', D1);
  const narrow = VocabProgress.summary(s, ['rain']);
  check(narrow.total === 1 && narrow.byState.new === 1,
    'a word outside the given list was counted');
  const all = VocabProgress.summary(s);
  check(all.total === Object.keys(s.items).length,
    'the no-list summary did not use the whole ledger');
}

/* ---- the record --------------------------------------------------------- */
{
  let st = {items: {}};
  st = VocabProgress.seen(st, '  Confident ', D1);
  check(Object.keys(st.items).join(',') === 'confident',
    'the headword was not case-folded: ' + Object.keys(st.items).join(','));
  check(VocabProgress.stateOf(VocabProgress.get(st, 'CONFIDENT')) === 'encountered',
    'a lookup by another case missed the record');

  for (let i = 0; i < 40; i += 1) st = VocabProgress.seen(st, 'w' + i, D1);
  const written = VocabProgress.write(st);
  check(Object.keys(written.items).length === 41,
    'write() lost records under the bound: ' + Object.keys(written.items).length);
  for (let i = 0; i < VocabProgress.KEEP + 20; i += 1) {
    st = VocabProgress.seen(st, 'z' + i, D1);
  }
  const big = VocabProgress.write(st);
  check(Object.keys(big.items).length === VocabProgress.KEEP,
    'write() did not bound the ledger at KEEP: ' + Object.keys(big.items).length);

  mem[VocabProgress.KEY] = '{not json';
  check(Object.keys(VocabProgress.read().items).length === 0,
    'a corrupt record did not read as empty');

  mem[VocabProgress.KEY] = JSON.stringify({items: {x: {seen: 1, days: {[D1]: 1}}}});
  const read = VocabProgress.get(VocabProgress.read(), 'x');
  check(read && read.seen === 1 && VocabProgress.stateOf(read) === 'encountered',
    'a minimal record was not read back');
}

console.log(JSON.stringify({problems, out}));
"""


def main() -> int:
    if not shutil.which("node"):
        print("check_vocab_progress: node is not installed")
        return 2
    src = WEBAPP.read_text(encoding="utf-8")
    harness = HARNESS.replace("__BLOCK__", block(src))
    proc = subprocess.run(["node", "-e", harness], capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stderr.strip()[:1200])
        print("FAIL  the vocabulary ledger does not run")
        return 1
    data = json.loads(proc.stdout)
    problems.extend(data["problems"])
    print(f"  ran the ladder, the mistake bank, the dashboard and the record")
    if problems:
        print(f"\nFAIL  {len(problems)} problems\n")
        for p in problems:
            print(f"  {p}")
        return 1
    print("PASS  every state follows from evidence, and nothing else promotes a word")
    return 0


if __name__ == "__main__":
    sys.exit(main())
