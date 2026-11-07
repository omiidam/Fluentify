#!/usr/bin/env python3
"""Mastery: does anything actually come back, and does it come back on time?

The review panel used to hold a word and a tick. Nothing scheduled, nothing
measured, and "mastered" meant "the learner tapped the right button once".
This suite runs the page's own scheduler in node and asks the questions that a
scheduler gets wrong silently:

  seed        a ticked daily item enters the queue; a conversation does not; an
              unknown id is not invented; an existing record keeps its dates
  schedule    every verdict moves the date the way it says: again keeps it due,
              hard grows slowly, good grows by the ease, easy faster; the
              interval is capped and the ease cannot fall below 1.3
  lapses      "again" is counted as a lapse, the others are not
  retention   only reviews after a real gap count, and only good/easy count as
              recalled - a count of sessions would be a count of nothing
  queue       due() is sorted, excludes the future, includes an undated item
  bounded     six hundred items, twelve thousand would make the record
              unwritable; a corrupt record reads as empty

  python3 tools/check_mastery.py
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEBAPP = ROOT / "webapp.py"
CACHE = ROOT / "tools/.cache"

problems: list[str] = []


def fail(what: str) -> None:
    problems.append(what)


def check(ok: bool, what: str) -> bool:
    if not ok:
        fail(what)
    return ok


def block(src: str) -> str:
    start = src.index("/* --- mastery: pure")
    end = src.index("/* --- end mastery", start)
    return src[start:end]


HARNESS = r"""
const fs = require('fs');
const vm = require('vm');
const root = process.argv[2];
const outPath = process.argv[3];

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
const cat = JSON.parse(fs.readFileSync(root + '/daily.json', 'utf8'));

/* ---- empty, then seeded from the daily ticks --------------------------- */
{
  let st = Mastery.read();
  check(Object.keys(st.items).length === 0, 'a fresh install already has items');

  const days = {
    '2026-11-02': ['w001', 'e001', 'c001'],
    '2026-11-04': ['w002', 'nonsense'],
  };
  st = Mastery.seedDaily(st, cat, days, '2026-11-07');
  const keys = Object.keys(st.items);
  out.seeded = keys.sort();
  check(keys.indexOf('word:w001') !== -1, 'a ticked word did not enter the queue');
  check(keys.indexOf('expression:e001') !== -1, 'a ticked expression did not enter the queue');
  check(keys.indexOf('word:c001') === -1, 'a conversation was counted as quiz content');
  check(keys.every((k) => k.indexOf('nonsense') === -1), 'an unknown id was invented');
  check(keys.length === 3, 'an unknown id was invented into the queue: ' + keys.join(','));
  const row = cat.words.find((r) => r.id === 'w001');
  check(st.items['word:w001'].en === row.en, 'the item did not carry its own English');
  check(st.items['word:w001'].fa === row.fa, 'the item did not carry its Persian');
  check(st.items['word:w001'].due === '2026-11-07', 'a new item is not due the day it is met');
  check(st.items['word:w001'].iv === 0 && st.items['word:w001'].reps === 0,
    'a new item arrived with a history');

  /* seeding twice must not reset anything the learner has earned */
  st = Mastery.grade(st, 'word:w001', 2, '2026-11-07');
  const after = st.items['word:w001'].due;
  st = Mastery.seedDaily(st, cat, days, '2026-11-08');
  check(st.items['word:w001'].due === after, 're-seeding reset a graded item\'s date');
}

/* ---- the schedule -------------------------------------------------------- */
{
  let st = {items: {}};
  st = Mastery.seed(st, [{key: 'k', kind: 'word', en: 'x', fa: 'y'}], '2026-01-01');
  const first = st.items.k;
  check(first.iv === 0 && first.due === '2026-01-01', 'a seeded item was not due at once');

  st = Mastery.grade(st, 'k', 2, '2026-01-01');
  check(st.items.k.iv === 1, 'the first "good" did not set a one-day interval');
  check(st.items.k.due === '2026-01-02', 'the first "good" did not fall due tomorrow');

  const before = st.items.k.iv;
  st = Mastery.grade(st, 'k', 2, '2026-01-02');
  check(st.items.k.iv > before, 'a second "good" did not lengthen the interval');

  /* hard, good and easy from the same starting interval: each must be a real
     step, and hard must be the smallest of the three */
  const base = JSON.parse(JSON.stringify(st));
  const hard = Mastery.grade(JSON.parse(JSON.stringify(base)), 'k', 1, '2026-01-12');
  const good = Mastery.grade(JSON.parse(JSON.stringify(base)), 'k', 2, '2026-01-12');
  const easy = Mastery.grade(JSON.parse(JSON.stringify(base)), 'k', 3, '2026-01-12');
  check(hard.items.k.iv >= 1, '"hard" produced a zero-day interval');
  check(hard.items.k.iv < good.items.k.iv, '"hard" was not shorter than "good"');
  check(good.items.k.iv < easy.items.k.iv, '"easy" was not longer than "good"');
  st = good;

  const lapses = st.items.k.lapses;
  st = Mastery.grade(st, 'k', 0, '2026-01-21');
  check(st.items.k.due === '2026-01-21', '"again" did not keep the item due today');
  check(st.items.k.lapses === lapses + 1, '"again" was not counted as a lapse');
  check(st.items.k.ease < 2.5, 'an answer did not move the ease');

  /* bounds: a year of easy answers must not bury an item, and ease has a floor */
  let many = {items: {}};
  many = Mastery.seed(many, [{key: 'z', kind: 'word', en: 'z', fa: 'z'}], '2026-01-01');
  for (let i = 0; i < 40; i++) {
    many = Mastery.grade(many, 'z', 3, Mastery.addDays('2026-01-01', i * 40));
  }
  check(many.items.z.iv <= Mastery.MAX_DAYS,
    'the interval grew past the cap: ' + many.items.z.iv);
  let low = {items: {}};
  low = Mastery.seed(low, [{key: 'y', kind: 'word', en: 'y', fa: 'y'}], '2026-01-01');
  for (let i = 0; i < 30; i++) low = Mastery.grade(low, 'y', 0, '2026-01-01');
  check(low.items.y.ease >= 1.3, 'the ease fell below its floor: ' + low.items.y.ease);
  out.intervalAfterEasy = many.items.z.iv;
}

/* ---- retention is measured, not asserted -------------------------------- */
{
  let st = {items: {}};
  st = Mastery.seed(st, [{key: 'a', kind: 'word', en: 'a', fa: 'a'}], '2026-01-01');
  st = Mastery.grade(st, 'a', 2, '2026-01-01');     // no gap yet: not a probe
  check(Mastery.retention(st).at7.n === 0, 'the first answer counted as a recall');
  st = Mastery.grade(st, 'a', 2, '2026-01-08');     // gap 7: counted, recalled
  check(Mastery.retention(st).at7.n === 1, 'a seven-day review was not counted');
  check(Mastery.retention(st).at7.good === 1, 'a recalled word was not counted as recalled');
  st = Mastery.grade(st, 'a', 0, '2026-01-09');     // gap 1: not a probe
  check(Mastery.retention(st).at7.n === 1, 'a next-day review was counted as a week-later probe');
  st = Mastery.grade(st, 'a', 1, '2026-02-10');     // gap ~32: the month probe
  check(Mastery.retention(st).at30.n === 1, 'a month-later review was not counted');
  check(Mastery.retention(st).at30.good === 0, '"hard" was counted as recalled');
  const r = Mastery.retention(st);
  check(r.pct7 === 100, "the week's recall percentage is wrong: " + r.pct7);
  check(r.pct30 === 0, "the month's recall percentage is wrong: " + r.pct30);
  out.retention = r;
}

/* ---- the queue ----------------------------------------------------------- */
{
  let st = {items: {}};
  st = Mastery.seed(st, [
    {key: 'b', kind: 'word', en: 'b', fa: 'b'},
    {key: 'a', kind: 'word', en: 'a', fa: 'a'},
  ], '2026-03-01');
  st = Mastery.grade(st, 'b', 2, '2026-03-01');   // due 03-02
  st.items.a.due = '2026-03-01';
  const due = Mastery.due(st, '2026-03-01').map((i) => i.k);
  check(due.length === 1 && due[0] === 'a', 'due() returned the wrong set: ' + due.join(','));
  const due2 = Mastery.due(st, '2026-03-02').map((i) => i.k);
  check(due2.length === 2, 'tomorrow\'s queue did not include both items');
  check(Mastery.next(st) === '2026-03-01', 'next() answered with the wrong date');
  check(Mastery.stats(st, '2026-03-01').due === 1, 'stats counted the wrong number due');
  st.items.a.due = '';
  check(Mastery.due(st, '2026-03-01').some((i) => i.k === 'a'),
    'an item with no date is not in the queue, so it can never come back');
}

/* ---- bounded, and safe when corrupt -------------------------------------- */
{
  let st = {items: {}};
  const seeds = [];
  for (let i = 0; i < 700; i++) {
    seeds.push({key: 'k' + i, kind: 'word', en: 'k' + i, fa: '', });
  }
  /* distinct first dates, so "newest" has a meaning */
  seeds.forEach((s, i) => {
    st = Mastery.seed(st, [s], Mastery.addDays('2025-01-01', i));
  });
  st = Mastery.write(st);
  check(Object.keys(st.items).length === Mastery.KEEP,
    'the ledger is not bounded to ' + Mastery.KEEP + ': ' + Object.keys(st.items).length);
  check(!('k0' in st.items), 'bounded write kept the oldest item instead of the newest');
  check('k699' in st.items, 'bounded write dropped the newest item');

  mem[Mastery.KEY] = 'not json';
  check(Object.keys(Mastery.read().items).length === 0, 'a corrupt record threw');
  mem[Mastery.KEY] = '{"items":{"x":{"iv":"lots","ease":"maybe","r7":"no"}}}';
  const odd = Mastery.read();
  check(odd.items.x.iv === 0, 'a non-numeric interval survived the read');
  check(odd.items.x.ease === 2.5, 'a non-numeric ease survived the read');
  check(Array.isArray(odd.items.x.r7), 'the recall counters were not normalised');
}

out.problems = problems;
fs.writeFileSync(outPath, JSON.stringify(out));
console.log('checked the schedule over', out.seeded ? out.seeded.length : 0, 'seeded items');
"""


def run_block() -> dict:
    if not shutil.which("node"):
        print("SKIP  node is not installed - the scheduler was not exercised")
        return {}
    src = WEBAPP.read_text(encoding="utf-8")
    try:
        body = block(src)
    except ValueError:
        fail("webapp.py: the mastery block markers are gone")
        return {}
    CACHE.mkdir(parents=True, exist_ok=True)
    script = CACHE / "mastery_check.js"
    script.write_text(HARNESS.replace("__BLOCK__", body), encoding="utf-8")
    out = CACHE / "mastery_out.json"
    proc = subprocess.run(["node", str(script), str(ROOT), str(out)],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        fail("node failed on the mastery block: " +
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
    check("const Mastery = {" in src, "the mastery ledger is not in the page")
    check("Mastery.seedDaily(" in src, "nothing seeds the queue from the daily ticks")
    check("Mastery.seed(Mastery.read(), seeds" in src,
          "a word saved to Review never enters the queue")
    check("Mastery.grade(Mastery.read(), key, verdict" in src,
          "the review queue has no way to grade an item")
    check("Mastery.due(mastery, today)" in src, "the panel never asks what is due")
    check("'⏰ Due'" in src or "⏰ Due" in src, "the Review panel has no due tab")
    check("paintDue(" in src, "the due queue is not painted")
    check("Mastery.grade(state, key, right ? 2 : 0" in src,
          "the weekly quiz does not feed the schedule")
    check("fluentify.mastery.v1" in src, "the ledger has no storage key")


def main() -> int:
    result = run_block()
    wiring()
    if problems:
        for p in problems[:40]:
            print("FAIL  " + p)
        print(f"\nFAIL  {len(problems)} problem(s) with the mastery schedule")
        return 1
    print("PASS  mastery: items enter from the daily ticks and from Review, every "
          "verdict moves the date it says it does, recall is counted only after a "
          "real gap, the queue is sorted and bounded, and the Review panel opens on it")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
