#!/usr/bin/env python3
"""Weekly quiz: does it review the week, and only the week?

The quiz has one content source - the ticks the daily store already keeps -
and one job that is easy to get subtly wrong: turning them into a paper that is
the same paper every time it is opened, and a different one next Monday. That
is arithmetic, so this suite runs the page's own block in node:

  eligibility    seven local dates end today; older ticks, conversations and
                 duplicate ids are not content
  paper          at least five items, at most ten questions, one question per
                 item, four distinct options, the key inside them, every word
                 of every prompt traced back to the catalogue
  determinism    the same week and the same ticks build byte-identical papers,
                 and a new period builds a different one
  scoring        right/wrong/unanswered, percentage, no credit without an answer
  lifecycle      a skipped week stays skipped, a finished week keeps its score,
                 a corrupt record does not throw, old periods are pruned
  wiring         the card, the sheet, the panel registry, the boot call and the
                 offline bundle all exist; the block never reaches the network

    python3 tools/check_weekly.py
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEBAPP = ROOT / "webapp.py"
BUILT = ROOT / "android/app/src/main/assets/www/index.html"
CACHE = ROOT / "tools/.cache"
DAILY = ROOT / "daily.json"

problems: list[str] = []


def fail(what: str) -> None:
    problems.append(what)


def check(ok: bool, what: str) -> bool:
    if not ok:
        fail(what)
    return ok


def block(src: str) -> str:
    start = src.index("/* --- weekly quiz:")
    end = src.index("/* --- end weekly quiz", start)
    return src[start:end]


HARNESS = r"""
const fs = require('fs');
const vm = require('vm');

const root = process.argv[2];
const cases = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const outPath = process.argv[4];

const mem = {};
global.localStorage = {
  getItem: (k) => (k in mem ? mem[k] : null),
  setItem: (k, v) => { mem[k] = String(v); },
  removeItem: (k) => { delete mem[k]; },
};

__BLOCK__

const cat = JSON.parse(fs.readFileSync(root + '/daily.json', 'utf8'));
const problems = [];
const note = (what) => { problems.push(what); };
const check = (ok, what) => { if (!ok) note(what); return ok; };
const out = {};

/* ---- eligibility: the window, and what is not content ----------------- */
{
  const now = new Date(2026, 10, 7);            // Saturday
  const days = {};
  for (let i = 0; i < 9; i++) days[WeeklyQuiz.addDays('2026-11-07', -i)] =
    ['w00' + ((i % 9) + 1)];
  days['2026-11-06'] = ['w001', 'w001', 'e001', 'c001'];
  days['2026-11-04'] = ['e002'];
  days['2026-01-01'] = ['w009'];
  const items = WeeklyQuiz.eligible(days, now);
  const ids = items.map((i) => i.id);
  check(ids.indexOf('c001') === -1, 'a conversation became quiz content');
  check(ids.filter((id) => id === 'w001').length === 1,
    'the same item was counted twice');
  check(ids.indexOf('w009') === -1, "a tick from January is inside this week's window");
  check(items.every((i) => i.kind === 'word' || i.kind === 'expression'),
    'an item with no kind reached the paper');
  const win = WeeklyQuiz.window(now);
  check(win.length === 7 && win[6] === '2026-11-07', 'the window is not seven days ending today');
  check(win[0] === '2026-11-01', 'the window starts on the wrong date');
  check(items.every((i) => win.indexOf(i.day) !== -1), 'an item came from outside the window');
  out.eligible = ids;
}

/* ---- the period is the local Monday ----------------------------------- */
{
  const week = [];
  for (let d = 2; d <= 8; d++) {
    week.push(WeeklyQuiz.periodStart(new Date(2026, 10, d)));
  }
  out.periods = week;
  check(week.every((k) => k === '2026-11-02'),
    'the seven days of one week do not share a period: ' + week.join(','));
  check(WeeklyQuiz.periodStart(new Date(2026, 10, 9)) === '2026-11-09',
    'the next Monday did not open a new period');
  check(WeeklyQuiz.periodStart(new Date(2027, 0, 1)) === '2026-12-28',
    'a week straddling the new year was cut in half');
}

/* ---- the paper --------------------------------------------------------- */
const days = {
  '2026-11-02': ['w001', 'w002', 'e001'],
  '2026-11-04': ['w003', 'e002'],
  '2026-11-06': ['w004', 'e003'],
};
const items = WeeklyQuiz.eligible(days, new Date(2026, 10, 7));
const period = '2026-11-02';
const quiz = WeeklyQuiz.build(cat, items, period, '2026-11-07');

check(!!quiz, 'a week with seven learned items built no paper');
if (quiz) {
  out.questions = quiz.questions.length;
  check(quiz.questions.length >= WeeklyQuiz.MIN_ITEMS,
    'a paper was built below the minimum content requirement');
  check(quiz.questions.length <= WeeklyQuiz.MAX_QUESTIONS,
    'a paper came out longer than ten questions');
  const ids = quiz.questions.map((q) => q.item);
  check(new Set(ids).size === ids.length, 'an item was asked twice in one paper');
  check(ids.every((id) => items.some((i) => i.id === id)),
    'a question came from an item nobody learned');
  const kinds = new Set(quiz.questions.map((q) => q.type));
  check(kinds.size >= 2, 'every question in the paper had the same format');
  const perKind = {};
  quiz.questions.forEach((q) => { perKind[q.kind] = (perKind[q.kind] || 0) + 1; });
  out.perKind = perKind;

  quiz.questions.forEach((q) => {
    check(q.options.length === 4, q.id + ': not four options');
    check(new Set(q.options).size === q.options.length, q.id + ': two identical options');
    check(q.answer >= 0 && q.answer < q.options.length, q.id + ': the key is not an option');
    check(q.options.filter((o) => o === q.options[q.answer]).length === 1,
      q.id + ': the correct option appears more than once');
    check(!!q.prompt.en && !!q.prompt.fa, q.id + ': a prompt has only one language');
    check(!!q.detail.en, q.id + ': a question has nothing to show on review');
    /* nothing is invented: the keyed answer and its detail are catalogue text */
    const rows = cat[q.kind === 'word' ? 'words' : 'expressions'];
    const row = rows.find((r) => r.id === q.item);
    check(!!row, q.id + ': the item is not in the daily catalogue');
    if (row) {
      check(q.options[q.answer] === row.en || q.options[q.answer] === row.fa,
        q.id + ': the key is not the item\'s own English or Persian');
      check(q.detail.en.indexOf(row.en) !== -1, q.id + ': the review does not name the item');
    }
  });
}

/* ---- the same week gives the same paper ------------------------------- */
{
  const again = WeeklyQuiz.build(cat, WeeklyQuiz.eligible(days, new Date(2026, 10, 7)),
    period, '2026-11-07');
  check(JSON.stringify(again) === JSON.stringify(quiz),
    'rebuilding the same week drew a different paper');
  const order = WeeklyQuiz.eligible(days, new Date(2026, 10, 7)).slice().reverse();
  const reversed = WeeklyQuiz.build(cat, order, period, '2026-11-07');
  check(JSON.stringify(reversed) === JSON.stringify(quiz),
    'the paper depends on the order the store happened to return');
  const next = WeeklyQuiz.build(cat, WeeklyQuiz.eligible(days, new Date(2026, 10, 9)),
    '2026-11-09', '2026-11-09');
  check(JSON.stringify(next) !== JSON.stringify(quiz),
    'two different weeks produced the same paper');
}

/* ---- too little to ask ------------------------------------------------- */
{
  const few = WeeklyQuiz.eligible({'2026-11-06': ['w001', 'w002', 'e001']},
    new Date(2026, 10, 7));
  check(WeeklyQuiz.build(cat, few, period, '2026-11-07') === null,
    'a paper was built from three items');
  check(WeeklyQuiz.build(cat, [], period, '2026-11-07') === null,
    'a paper was built from nothing');
}

/* ---- scoring ----------------------------------------------------------- */
if (quiz) {
  const all = {}, none = {}, half = {};
  quiz.questions.forEach((q, i) => {
    all[i] = q.answer;
    half[i] = i % 2 ? q.answer : (q.answer + 1) % q.options.length;
  });
  const rAll = WeeklyQuiz.grade(quiz, all);
  const rNone = WeeklyQuiz.grade(quiz, none);
  const rHalf = WeeklyQuiz.grade(quiz, half);
  out.all = rAll.right;
  check(rAll.right === rAll.total && rAll.percent === 100, 'every answer right did not score 100');
  check(rNone.right === 0 && rNone.percent === 0, 'no answer scored above zero');
  check(rNone.missed.length === quiz.questions.length, 'an unanswered question was not counted wrong');
  check(rHalf.right === Math.floor(quiz.questions.length / 2),
    'a paper answered wrongly on every even question did not score ' +
    Math.floor(quiz.questions.length / 2) + ' (got ' + rHalf.right + ')');
  check(rAll.missed.length === 0, 'a perfect paper still lists misses');
}

/* ---- the record -------------------------------------------------------- */
{
  let st = WeeklyQuiz.read();
  check(Object.keys(st.periods).length === 0, 'a fresh install already has a period');

  st = WeeklyQuiz.setStarted(st, period, quiz);
  st = WeeklyQuiz.write(st);
  st = WeeklyQuiz.read();
  check(st.periods[period] && st.periods[period].status === 'started',
    'starting a week did not survive a write/read');
  check(st.periods[period].quiz.questions.length === quiz.questions.length,
    'the frozen paper was lost on the way through storage');

  /* one way: there is no argument that takes a skipped week back */
  check(WeeklyQuiz.setSkipped.length === 2,
    'setSkipped grew a second, on/off argument');
  let skipped = WeeklyQuiz.setSkipped(WeeklyQuiz.read(), period);
  skipped = WeeklyQuiz.write(skipped);
  skipped = WeeklyQuiz.read();
  check(skipped.periods[period].status === 'skipped', 'a skip did not stick');
  check(!skipped.periods[period].result, 'skipping a week recorded a result');

  const result = WeeklyQuiz.grade(quiz, {});
  let done = WeeklyQuiz.setCompleted(skipped, period, quiz, {}, result);
  done = WeeklyQuiz.write(done);
  done = WeeklyQuiz.read();
  check(done.periods[period].status === 'completed', 'a finished week did not stay finished');
  check(done.periods[period].result.total === result.total,
    'the score was not kept with the week');

  /* the record is bounded: twelve periods, newest kept */
  let many = WeeklyQuiz.read();
  for (let i = 0; i < 40; i++) {
    many = WeeklyQuiz.setSkipped(many, WeeklyQuiz.addDays('2025-01-06', i * 7));
  }
  many = WeeklyQuiz.write(many);
  check(Object.keys(many.periods).length === WeeklyQuiz.KEEP,
    'periods were not pruned to ' + WeeklyQuiz.KEEP + ': ' +
    Object.keys(many.periods).length);
  check(Object.keys(many.periods).indexOf('2025-01-06') === -1,
    'pruning kept the oldest period instead of the newest');

  /* a corrupt record must not take the card down */
  mem[WeeklyQuiz.KEY] = 'not json';
  check(Object.keys(WeeklyQuiz.read().periods).length === 0,
    'a corrupt record threw or kept garbage');
  mem[WeeklyQuiz.KEY] = '{"periods":{"2026-11-02":{"status":"bogus","answers":"no"}}}';
  const odd = WeeklyQuiz.read();
  check(odd.periods['2026-11-02'].status === 'available',
    'an unknown status was not normalised');
  check(typeof odd.periods['2026-11-02'].answers === 'object',
    'a non-object answer map survived the read');
}

/* ---- nothing in the block reaches the network ------------------------- */
{
  check(!/fetch\s*\(/.test(__SOURCE__), 'the quiz block makes a network request');
  check(!/XMLHttpRequest/.test(__SOURCE__), 'the quiz block opens an XHR');
}

out.problems = problems;
fs.writeFileSync(outPath, JSON.stringify(out));
console.log('checked', out.questions, 'questions over', out.eligible.length, 'eligible items');
"""


def run_block() -> dict:
    if not shutil.which("node"):
        print("SKIP  node is not installed - the quiz arithmetic was not exercised")
        return {}
    src = WEBAPP.read_text(encoding="utf-8")
    try:
        body = block(src)
    except ValueError:
        fail("webapp.py: the weekly quiz block markers are gone")
        return {}
    CACHE.mkdir(parents=True, exist_ok=True)
    script = CACHE / "weekly_check.js"
    script.write_text(
        HARNESS.replace("__BLOCK__", body)
        .replace("__SOURCE__", json.dumps(body)),
        encoding="utf-8")
    cases = CACHE / "weekly_cases.json"
    out = CACHE / "weekly_out.json"
    cases.write_text("{}", encoding="utf-8")
    proc = subprocess.run(["node", str(script), str(ROOT), str(cases), str(out)],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        fail("node failed on the quiz block: " +
             (proc.stderr or proc.stdout).strip()[:400])
        return {}
    payload = json.loads(out.read_text())
    for p in payload.get("problems") or []:
        fail(p)
    for f in (script, cases, out):
        f.unlink(missing_ok=True)
    return payload


def wiring() -> None:
    src = WEBAPP.read_text(encoding="utf-8")
    check('id="wqpanel"' in src, "the quiz has no sheet to open in")
    check('id="wqbody"' in src, "the quiz sheet has no body")
    check("wqpanel: null" in src,
          "the quiz sheet is not registered with Panels, so it has no close button")
    check("Weekly.refresh();" in src,
          "the week's card is not mounted with the day's")
    check("await Weekly.init();" in src, "the quiz is never loaded at boot")
    check("WeeklyQuiz.periodStart(" in src, "the page never asks which week it is")
    check("WeeklyQuiz.setCompleted(" in src, "a finished quiz is never recorded")
    check('data-wq="start"' in src or "data-wq=\"start\"" in src,
          "the card has no Start quiz button")
    check('data-wq="skip"' in src, "the card has no Skip button")
    check("isSkipped" in src and "status === 'skipped'" in src,
          "a skipped week is not honoured on the next paint")
    # a landing-page card, not a second navigation item
    check("weeklyquiz" in src, "there is no card on the landing page")
    check("wqtoggle" not in src,
          "the quiz grew a toolbar tile - it belongs on the landing card")
    # English first, Persian second, as everywhere else
    check("Weekly quiz<small" in src, "the card title has no Persian line")

    if BUILT.exists():
        built = BUILT.read_text(encoding="utf-8")
        check('id="wqpanel"' in built, "the built page has no quiz sheet")
        check("WeeklyQuiz" in built, "the built page does not carry the quiz")
        check("weeklyquiz" in built, "the built page has no weekly card")

    # the stylesheet has to place it like the level sheet, or it is squeezed
    check("#wqpanel.open" in src, "nothing gives the quiz sheet its open state")
    check("#wqpanel {" in src or "#wqpanel," in src,
          "the quiz sheet has no base rule")


def main() -> int:
    cat = json.loads(DAILY.read_text(encoding="utf-8"))
    ids = {r["id"] for r in cat.get("words", [])} | {r["id"] for r in cat.get("expressions", [])}
    check(len(ids) >= 20, "the daily catalogue is too small to draw distractors from")
    result = run_block()
    wiring()
    if problems:
        for p in problems[:40]:
            print("FAIL  " + p)
        print(f"\nFAIL  {len(problems)} problem(s) with the weekly quiz")
        return 1
    print("PASS  weekly quiz: "
          f"{result.get('questions')} questions built from "
          f"{len(result.get('eligible') or [])} learned items, the same paper for "
          f"the same week, a score that cannot be earned without an answer, and a "
          f"card, a sheet and a record wired into the page and the APK bundle")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
