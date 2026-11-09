#!/usr/bin/env python3
"""Weekly quiz: the Iranian week, the Friday window, and the paper itself.

The quiz is a Friday morning review of the week an Iranian learner just
finished, so two things have to be exactly right and both are easy to get
subtly wrong:

  the clock    09:00 to midnight in Tehran, not wherever the device is. That is
               05:30 to 20:30 UTC, and it must not move when the phone's own
               zone does, nor on the two nights a year a zone changes its
               offset.
  the week     Friday to Thursday. A word met on the quiz Friday belongs to the
               *next* paper; the paper asks the seven days that ended on
               Thursday.

Then the paper is the same paper every time it is opened in one week and a
different one the next Friday, every question traces back to the catalog, and
a score cannot be earned without an answer. All of that is arithmetic over the
daily store, so this suite runs the page's own block in node - twice, in two
timezones - and compares.

    python3 tools/check_weekly.py
"""

import json
import os
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
const outPath = process.argv[3];

const mem = {};
global.localStorage = {
  getItem: (k) => (k in mem ? mem[k] : null),
  setItem: (k, v) => { mem[k] = String(v); },
  removeItem: (k) => { delete mem[k]; },
};

__BLOCK__

const cat = JSON.parse(fs.readFileSync(root + '/daily.json', 'utf8'));
const problems = [];
const check = (ok, what) => { if (!ok) problems.push(what); return ok; };
const out = {tz: (process.env.TZ || 'unset')};

/* ---- the clock: 09:00 to midnight, Tehran -------------------------------- */
{
  const at = (iso) => new Date(iso);
  out.tehran = [
    WeeklyQuiz.tehranKey(at('2026-11-06T05:29:00Z')),   // Fri 08:59 Tehran
    WeeklyQuiz.tehranKey(at('2026-11-06T05:30:00Z')),   // Fri 09:00
    WeeklyQuiz.tehranKey(at('2026-11-06T20:29:00Z')),   // Fri 23:59
    WeeklyQuiz.tehranKey(at('2026-11-06T20:30:00Z')),   // Sat 00:00
  ];
  check(out.tehran[0] === '2026-11-06', 'the Tehran date is wrong before nine');
  check(out.tehran[3] === '2026-11-07', 'the Tehran date did not turn at midnight');

  check(!WeeklyQuiz.isOpen(at('2026-11-06T05:29:00Z')),
    'the quiz opened before 09:00 Tehran');
  check(WeeklyQuiz.isOpen(at('2026-11-06T05:30:00Z')),
    'the quiz did not open at 09:00 Tehran (05:30 UTC)');
  check(WeeklyQuiz.isOpen(at('2026-11-06T20:29:00Z')),
    'the quiz closed before midnight Tehran');
  check(!WeeklyQuiz.isOpen(at('2026-11-06T20:30:00Z')),
    'the quiz stayed open past midnight Tehran (20:30 UTC)');
  check(!WeeklyQuiz.isOpen(at('2026-11-07T05:30:00Z')),
    'the quiz opened on a Saturday');
  check(!WeeklyQuiz.isOpen(at('2026-11-05T05:30:00Z')),
    'the quiz opened on a Thursday');
  out.open = WeeklyQuiz.isOpen(at('2026-11-06T09:00:00Z'));
}

/* ---- the week is Friday to Thursday -------------------------------------- */
{
  out.periods = [
    WeeklyQuiz.periodStart(new Date('2026-11-06T10:00:00Z')),   // Friday
    WeeklyQuiz.periodStart(new Date('2026-11-07T10:00:00Z')),   // Saturday
    WeeklyQuiz.periodStart(new Date('2026-11-12T10:00:00Z')),   // Thursday
    WeeklyQuiz.periodStart(new Date('2026-11-13T10:00:00Z')),   // next Friday
    WeeklyQuiz.periodStart(new Date('2026-11-20T10:00:00Z')),   // Friday after
  ];
  check(out.periods[0] === '2026-11-06', 'a Friday is not its own period');
  check(out.periods[1] === '2026-11-06', 'Saturday moved to a new period');
  check(out.periods[2] === '2026-11-06', 'Thursday did not belong to the Friday before it');
  check(out.periods[3] === '2026-11-13', 'the next Friday did not open a new period');

  const win = WeeklyQuiz.contentWindow('2026-11-06');
  out.window = win;
  check(win.length === 7, 'the week is not seven days: ' + win.length);
  check(win[0] === '2026-10-30', 'the week does not start on the previous Friday: ' + win[0]);
  check(win[6] === '2026-11-05', 'the week does not end on Thursday: ' + win[6]);

  const next = WeeklyQuiz.contentWindow('2026-11-13');
  check(next[0] === '2026-11-06' && next[6] === '2026-11-12',
    'the next quiz does not cover this Friday to Thursday');
}

/* ---- opensAt: the timer the page sets ------------------------------------ */
{
  const from = (iso) => WeeklyQuiz.opensAt(new Date(iso)).toISOString();
  out.opens = [
    from('2026-11-07T10:00:00Z'),   // Saturday noon -> next Friday 05:30
    from('2026-11-06T06:00:00Z'),   // Friday 09:30 Tehran -> next week
    from('2026-11-06T04:00:00Z'),   // Friday 07:30 Tehran -> today 05:30
    from('2026-11-12T22:00:00Z'),   // Thursday -> tomorrow morning
  ];
  check(out.opens[0] === '2026-11-13T05:30:00.000Z',
    'the next opening from a Saturday is wrong: ' + out.opens[0]);
  check(out.opens[1] === '2026-11-13T05:30:00.000Z',
    'a Friday after nine scheduled the same morning again: ' + out.opens[1]);
  check(out.opens[2] === '2026-11-06T05:30:00.000Z',
    'a Friday before nine did not schedule today: ' + out.opens[2]);
  check(out.opens[3] === '2026-11-13T05:30:00.000Z',
    'a Thursday did not schedule the next morning: ' + out.opens[3]);
  check(WeeklyQuiz.opensAt(new Date('2026-11-07T10:00:00Z')).getTime() > Date.now() - 86400000,
    'opensAt answered with something in the past');
}

/* ---- what counts as content --------------------------------------------- */
const friday = new Date('2026-11-06T10:00:00Z');
const days = {
  '2026-10-30': ['w001', 'e001'],       // the week's first day
  '2026-11-02': ['w002', 'w002', 'c001'],
  '2026-11-05': ['w003', 'e002'],       // Thursday, the last day
  '2026-11-06': ['w004'],               // the quiz Friday: belongs to next week
  '2026-10-29': ['w005'],               // the Thursday before: last week's quiz
};
const items = WeeklyQuiz.eligible(days, friday);
{
  const ids = items.map((i) => i.id);
  out.eligible = ids;
  check(ids.indexOf('c001') === -1, 'a conversation became quiz content');
  check(ids.filter((id) => id === 'w002').length === 1, 'the same item was counted twice');
  check(ids.indexOf('w001') !== -1, 'the first day of the week was not included');
  check(ids.indexOf('w003') !== -1, 'Thursday was not included');
  check(ids.indexOf('w004') === -1,
    'a word met on the quiz Friday was asked on the same Friday');
  check(ids.indexOf('w005') === -1, 'last week\'s Thursday leaked into this paper');
  check(items.every((i) => i.kind === 'word' || i.kind === 'expression'),
    'an item with no kind reached the paper');
}

/* ---- the paper ----------------------------------------------------------- */
const period = '2026-11-06';
const quiz = WeeklyQuiz.build(cat, items, period, '2026-11-06');
check(!!quiz, 'a week with six learned items built no paper');
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

  quiz.questions.forEach((q) => {
    check(q.options.length === 4, q.id + ': not four options');
    check(new Set(q.options).size === q.options.length, q.id + ': two identical options');
    check(q.answer >= 0 && q.answer < q.options.length, q.id + ': the key is not an option');
    check(!!q.prompt.en && !!q.prompt.fa, q.id + ': a prompt has only one language');
    const rows = cat[q.kind === 'word' ? 'words' : 'expressions'];
    const row = rows.find((r) => r.id === q.item);
    check(!!row, q.id + ': the item is not in the daily catalogue');
    if (row) {
      check(q.options[q.answer] === row.en || q.options[q.answer] === row.fa,
        q.id + ': the key is not the item\'s own English or Persian');
    }
  });
}

/* ---- the same week, the same paper -------------------------------------- */
{
  const again = WeeklyQuiz.build(cat, WeeklyQuiz.eligible(days, friday), period, '2026-11-06');
  check(JSON.stringify(again) === JSON.stringify(quiz),
    'rebuilding the same week drew a different paper');
  const reversed = WeeklyQuiz.build(cat, WeeklyQuiz.eligible(days, friday).slice().reverse(),
    period, '2026-11-06');
  check(JSON.stringify(reversed) === JSON.stringify(quiz),
    'the paper depends on the order the store happened to return');
}

/* ---- too little, and scoring -------------------------------------------- */
{
  const few = WeeklyQuiz.eligible({'2026-11-05': ['w001', 'w002', 'e001']}, friday);
  check(WeeklyQuiz.build(cat, few, period, '2026-11-06') === null,
    'a paper was built from three items');
}
if (quiz) {
  const all = {}, none = {}, half = {};
  quiz.questions.forEach((q, i) => {
    all[i] = q.answer;
    half[i] = i % 2 ? q.answer : (q.answer + 1) % q.options.length;
  });
  const rAll = WeeklyQuiz.grade(quiz, all);
  const rNone = WeeklyQuiz.grade(quiz, none);
  const rHalf = WeeklyQuiz.grade(quiz, half);
  check(rAll.right === rAll.total && rAll.percent === 100, 'every answer right did not score 100');
  check(rNone.right === 0 && rNone.percent === 0, 'no answer scored above zero');
  check(rNone.missed.length === quiz.questions.length, 'an unanswered question was not counted wrong');
  check(rHalf.right === Math.floor(quiz.questions.length / 2),
    'a paper answered wrongly on every even question did not score half');
}

/* ---- the record ---------------------------------------------------------- */
{
  let st = WeeklyQuiz.read();
  check(Object.keys(st.periods).length === 0, 'a fresh install already has a period');
  st = WeeklyQuiz.write(WeeklyQuiz.setStarted(st, period, quiz));
  st = WeeklyQuiz.read();
  check(st.periods[period] && st.periods[period].status === 'started',
    'starting a week did not survive a write/read');
  check(st.periods[period].quiz.questions.length === quiz.questions.length,
    'the frozen paper was lost on the way through storage');
  check(WeeklyQuiz.setSkipped.length === 2, 'setSkipped grew a second, on/off argument');
  let skipped = WeeklyQuiz.write(WeeklyQuiz.setSkipped(WeeklyQuiz.read(), period));
  skipped = WeeklyQuiz.read();
  check(skipped.periods[period].status === 'skipped', 'a skip did not stick');
  check(!skipped.periods[period].result, 'skipping a week recorded a result');

  const result = WeeklyQuiz.grade(quiz, {});
  let done = WeeklyQuiz.write(WeeklyQuiz.setCompleted(skipped, period, quiz, {}, result));
  done = WeeklyQuiz.read();
  check(done.periods[period].status === 'completed', 'a finished week did not stay finished');

  let many = WeeklyQuiz.read();
  for (let i = 0; i < 40; i++) {
    many = WeeklyQuiz.setSkipped(many, WeeklyQuiz.addDays('2025-01-02', i * 7));
  }
  many = WeeklyQuiz.write(many);
  check(Object.keys(many.periods).length === WeeklyQuiz.KEEP,
    'periods were not pruned to ' + WeeklyQuiz.KEEP);
  check(Object.keys(many.periods).indexOf('2025-01-02') === -1,
    'pruning kept the oldest period instead of the newest');

  mem[WeeklyQuiz.KEY] = 'not json';
  check(Object.keys(WeeklyQuiz.read().periods).length === 0, 'a corrupt record threw');
}

check(!/fetch\s*\(/.test(__SOURCE__), 'the quiz block makes a network request');
check(!/XMLHttpRequest/.test(__SOURCE__), 'the quiz block opens an XHR');

out.problems = problems;
fs.writeFileSync(outPath, JSON.stringify(out));
console.log('checked', out.questions, 'questions over', out.eligible.length, 'eligible items');
"""


def run_block(tz: str) -> dict:
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
    tag = tz.replace("/", "_")
    script = CACHE / f"weekly_check_{tag}.js"
    script.write_text(HARNESS.replace("__BLOCK__", body)
                      .replace("__SOURCE__", json.dumps(body)), encoding="utf-8")
    out = CACHE / f"weekly_out_{tag}.json"
    env = dict(os.environ, TZ=tz)
    proc = subprocess.run(["node", str(script), str(ROOT), str(out)],
                          capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        fail("node failed on the quiz block: " +
             (proc.stderr or proc.stdout).strip()[:400])
        return {}
    payload = json.loads(out.read_text())
    for p in payload.get("problems") or []:
        fail(f"[{tz}] {p}")
    for f in (script, out):
        f.unlink(missing_ok=True)
    return payload


def wiring() -> None:
    src = WEBAPP.read_text(encoding="utf-8")
    check('id="wqpanel"' in src, "the quiz has no sheet to open in")
    check("wqpanel: null" in src,
          "the quiz sheet is not registered with Panels, so it has no close button")
    check("WeeklyQuiz.isOpen(new Date())" in src,
          "the card is mounted without asking whether it is Friday morning")
    check("WeeklyQuiz.opensAt(" in src, "nothing schedules the card for Friday morning")
    check("this.contentWindow(this.periodStart(now))" in src,
          "the paper is not drawn from the week")
    check("WeeklyQuiz.setCompleted(" in src, "a finished quiz is never recorded")
    check('data-wq="start"' in src, "the card has no Start quiz button")
    check('data-wq="skip"' in src, "the card has no Skip button")
    check("isSkipped" in src and "status === 'skipped'" in src,
          "a skipped week is not honored on the next paint")
    check("weeklyquiz" in src, "there is no card on the landing page")
    check("wqtoggle" not in src,
          "the quiz grew a toolbar tile - it belongs on the landing card")
    if BUILT.exists():
        built = BUILT.read_text(encoding="utf-8")
        check('id="wqpanel"' in built, "the built page has no quiz sheet")
        check("WeeklyQuiz" in built, "the built page does not carry the quiz")
        check("weeklyquiz" in built, "the built page has no weekly card")


def main() -> int:
    cat = json.loads(DAILY.read_text(encoding="utf-8"))
    ids = {r["id"] for r in cat.get("words", [])} | {r["id"] for r in cat.get("expressions", [])}
    check(len(ids) >= 20, "the daily catalog is too small to draw distractors from")
    first = run_block("Asia/Tehran")
    second = run_block("America/New_York")
    if first and second:
        for key in ("tehran", "periods", "window", "opens", "eligible", "open"):
            check(json.dumps(first.get(key)) == json.dumps(second.get(key)),
                  f"the quiz's {key} depends on the device's own timezone")
    wiring()
    if problems:
        for p in problems[:40]:
            print("FAIL  " + p)
        print(f"\nFAIL  {len(problems)} problem(s) with the weekly quiz")
        return 1
    print("PASS  weekly quiz: opens Friday 09:00-24:00 Tehran whatever the device's "
          "zone, asks the Friday-to-Thursday week that just closed, builds the same "
          "paper for the same week, and scores nothing without an answer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
