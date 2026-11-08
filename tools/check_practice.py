#!/usr/bin/env python3
"""Practice: four drills and the word-level comparison behind two of them.

Everything here answers a question the app could not answer before:

  say match    which words of a spoken sentence came back, after normalising
               case, punctuation and contractions, and aligned by longest common
               subsequence so a dropped word does not mark the rest wrong
  word partners a curated bank - heavy rain, make a decision - asked with
               alternatives that are grammatical but not English
  register     one meaning, three levels of formality, and one question with
               one right answer
  ear test     the minimal pairs the phonetics panel only ever listed
  content      every collocation is authored, uses both languages, and its blank
               is completed by its own answer
  wiring       the sheet, the card, the routes, the APK copy and the microphone
               path that does not write into the composer

    python3 tools/check_practice.py
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
COLL = ROOT / "collocations.json"
REGISTER = ROOT / "register.json"
PHON = ROOT / "phonetics.json"
LISTEN = ROOT / "listening.json"

problems: list[str] = []


def fail(what: str) -> None:
    problems.append(what)


def check(ok: bool, what: str) -> bool:
    if not ok:
        fail(what)
    return ok


def block(src: str, start_marker: str, end_marker: str) -> str:
    start = src.index(start_marker)
    end = src.index(end_marker, start)
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

__SAY__
__DRILLS__

const problems = [];
const check = (ok, what) => { if (!ok) problems.push(what); return ok; };
const out = {};

/* ---- what was heard ------------------------------------------------------ */
{
  const same = SayMatch.compare('The weather is cold today.',
    'the weather is cold today');
  check(same.total === 5, 'the sentence split into ' + same.total + ' words');
  check(same.right === 5 && same.percent === 100, 'an exact match did not score 100');
  check(same.missing.length === 0, 'an exact match reported missing words');

  const dropped = SayMatch.compare('I would like a cup of tea please',
    'I would like a cup tea please');
  check(dropped.total === 8, 'the target is not eight words: ' + dropped.total);
  check(dropped.right === 7, 'a dropped word cost more than itself: ' + dropped.right);
  check(dropped.missing.length === 1 && dropped.missing[0] === 'of',
    'the wrong word was reported missing: ' + dropped.missing.join(','));
  check(dropped.percent === 88, 'the percentage is wrong: ' + dropped.percent);

  /* a word inserted in the middle must not shift the rest of the line */
  const inserted = SayMatch.compare('I have two brothers and one sister.',
    'I have two older brothers and one sister');
  check(inserted.right === inserted.total, 'an inserted word broke the alignment');
  check(inserted.extra.length === 1 && inserted.extra[0] === 'older',
    'the inserted word was not reported as extra: ' + inserted.extra.join(','));

  const contraction = SayMatch.compare('I do not understand, can you repeat that?',
    "I don't understand can you repeat that");
  check(contraction.percent === 100, 'a contraction was called a missing word: ' +
    contraction.percent);

  const empty = SayMatch.compare('Good morning', '');
  check(empty.right === 0 && empty.empty, 'an empty recording scored above zero');
  check(SayMatch.compare('', 'anything').total === 0, 'an empty target has words');

  const punct = SayMatch.compare('Where is the station?', 'where is the station');
  check(punct.percent === 100, 'punctuation changed the result');
  out.dropped = dropped.percent;
}

/* ---- word partners ------------------------------------------------------- */
const coll = JSON.parse(fs.readFileSync(__COLL__, 'utf8'));
{
  const q = Drills.collocation(coll, 42);
  check(!!q, 'no collocation question was built');
  if (q) {
    check(q.options.length === 3, 'the drill offered ' + q.options.length + ' options');
    check(new Set(q.options).size === 3, 'two options were the same word');
    check(q.answer >= 0 && q.answer < q.options.length, 'the key is not an option');
    check(q.prompt.en.indexOf(q.options[q.answer]) !== -1 ||
      q.prompt.en.indexOf('___') !== -1, 'the prompt does not show the blank');
    check(q.kind === 'choice' && q.cls.key === 'collocation', 'the question has no class');
    check(q.detail.en.length > 0 && q.why.en.length > 0, 'the answer has no explanation');
    const again = Drills.collocation(coll, 42);
    check(JSON.stringify(again) === JSON.stringify(q),
      'the same seed built a different question');
  }
  const seen = new Set();
  for (let s = 0; s < 40; s++) {
    const one = Drills.collocation(coll, s);
    if (one) seen.add(one.id);
  }
  out.entries = seen.size;
  check(seen.size >= 8, 'forty seeds only ever asked ' + seen.size + ' entries');
  check(Drills.collocation({entries: []}, 1) === null, 'an empty bank built a question');
}

/* ---- register ------------------------------------------------------------ */
const reg = JSON.parse(fs.readFileSync(__REGISTER__, 'utf8'));
{
  const forms = new Set();
  for (let s = 0; s < 12; s++) {
    const q = Drills.register(reg, s);
    check(!!q, 'no register question was built for seed ' + s);
    if (!q) continue;
    forms.add(q.id.split(':').pop() === 'casual' ? 'casual' : 'formal');
    check(q.options.length === 3, 'the register drill offered ' + q.options.length + ' options');
    check(new Set(q.options).size === 3, 'two register options were identical');
    check(q.answer === 2 || q.options[q.answer] !== undefined, 'the key is not an option');
    if (q.prompt.en.indexOf('register') !== -1) {
      check(q.options[q.answer] === 'Casual', 'the casual sentence was not keyed Casual');
      check(q.detail.en.indexOf('(casual)') !== -1, 'the answer does not name the register');
    } else {
      const pair = reg.pairs.find((p) => ('reg:' + p.id) === q.id);
      check(!!pair, 'the question does not trace back to a pair: ' + q.id);
      if (pair) {
        check(q.options[q.answer] === pair.formal.en, 'the formal answer was not the key');
        check(q.detail.en.indexOf(pair.casual.en) !== -1,
          'the answer does not show what the casual form would have been');
      }
    }
  }
  out.registerForms = [...forms].sort();
  check(out.registerForms.length === 2, 'one register question type was never asked');
  check(Drills.register({pairs: []}, 1) === null, 'an empty register bank built a question');
}

/* ---- the ear test -------------------------------------------------------- */
const phon = JSON.parse(fs.readFileSync(__PHON__, 'utf8'));
{
  const bank = Drills.pairs(phon);
  out.pairs = bank.length;
  check(bank.length >= 20, 'only ' + bank.length + ' pairs were found in the phonetics bank');
  check(bank.every((p) => p.a && p.b && p.a !== p.b), 'a pair repeated one word');
  check(bank.every((p) => /^[a-z']+$/.test(p.a) && /^[a-z']+$/.test(p.b)),
    'a pair carried a word that is not one lowercase word');
  const keys = bank.map((p) => p.a + '|' + p.b + '|' + p.b + '|' + p.a);
  check(new Set(bank.map((p) => [p.a, p.b].sort().join('|'))).size === bank.length,
    'the same pair was listed twice');
  const q = Drills.pairQuestion(bank, 5);
  check(!!q, 'no ear-test question was built');
  if (q) {
    check(q.options.indexOf(q.say) !== -1, 'the played word is not an option');
    check(q.options[q.answer] === q.say, 'the key is not the word that was played');
    check(q.options.length === 2, 'the ear test offered more than two words');
  }
}

/* ---- the listening bank ------------------------------------------------
   listening.json is one object, {levels: [...]}, and both dictation and say-it
   read it through Drills.levels. Read as though it were already the array, the
   file looks empty and the sheet says the bank is not on the device - which is
   what it said on every platform until this test existed. */
const listen = JSON.parse(fs.readFileSync(__LISTEN__, 'utf8'));
{
  check(Array.isArray(listen.levels) && listen.levels.length >= 4,
    'listening.json no longer carries a levels array');
  const levels = Drills.levels(listen);
  check(levels.length === (listen.levels || []).length,
    'the unwrapper dropped levels: ' + levels.length);
  check(levels.every((lv) => Array.isArray(lv.sentences) && lv.sentences.length),
    'a level carries no sentences');
  check(levels.every((lv) => lv.sentences.every((s) => s.en && s.fa)),
    'a listening line is missing one of its languages');
  check(Drills.levels(levels) === levels, 'an already-unwrapped bank was rewrapped');
  check(Drills.levels([]).length === 0 && Drills.levels({}).length === 0,
    'an empty bank became something else');
  check(Drills.levels(null).length === 0, 'a missing bank threw');
  out.listenLevels = levels.length;
  out.listenLines = levels.reduce((n, lv) => n + lv.sentences.length, 0);
  check(out.listenLines >= 24, 'the bank is only ' + out.listenLines + ' lines long');
}

out.problems = problems;
fs.writeFileSync(outPath, JSON.stringify(out));
console.log('pairs', out.pairs, 'partners', out.entries);
"""


def run_block() -> dict:
    if not shutil.which("node"):
        print("SKIP  node is not installed - the drills were not exercised")
        return {}
    src = WEBAPP.read_text(encoding="utf-8")
    try:
        say = block(src, "/* --- say match: pure", "/* --- end say match")
        drills = block(src, "/* --- drills: pure", "/* --- end drills")
    except ValueError:
        fail("webapp.py: the say match or drills block markers are gone")
        return {}
    CACHE.mkdir(parents=True, exist_ok=True)
    script = CACHE / "practice_check.js"
    script.write_text(
        HARNESS.replace("__SAY__", say)
        .replace("__DRILLS__", drills)
        .replace("__COLL__", json.dumps(str(COLL)))
        .replace("__REGISTER__", json.dumps(str(REGISTER)))
        .replace("__PHON__", json.dumps(str(PHON)))
        .replace("__LISTEN__", json.dumps(str(LISTEN))),
        encoding="utf-8")
    out = CACHE / "practice_out.json"
    proc = subprocess.run(["node", str(script), str(out)], capture_output=True, text=True)
    if proc.returncode != 0:
        fail("node failed on the practice blocks: " +
             (proc.stderr or proc.stdout).strip()[:400])
        return {}
    payload = json.loads(out.read_text())
    for p in payload.get("problems") or []:
        fail(p)
    for f in (script, out):
        f.unlink(missing_ok=True)
    return payload


def content() -> None:
    data = json.loads(COLL.read_text(encoding="utf-8"))
    entries = data.get("entries") or []
    check(len(entries) >= 60, f"only {len(entries)} collocations - the bank is too thin")
    ids = [e.get("id") for e in entries]
    check(len(set(ids)) == len(ids), "two collocations share an id")
    tags = {"verb+noun", "adj+noun", "verb+prep"}
    levels = {"A1", "A2", "B1", "B2", "C1"}
    for e in entries:
        eid = e.get("id", "?")
        check(bool(e.get("blank")), f"{eid}: no blank, so there is nothing to fill")
        check("___" in (e.get("blank") or ""), f"{eid}: the blank has no gap in it")
        check(bool(e.get("answer")), f"{eid}: no answer")
        wrong = e.get("wrong") or []
        check(len(wrong) == 2, f"{eid}: needs exactly two wrong partners, has {len(wrong)}")
        check(e.get("answer") not in wrong, f"{eid}: the answer is also listed as wrong")
        check(len({e.get("answer"), *wrong}) == 3, f"{eid}: the options are not distinct")
        check(e.get("tag") in tags, f"{eid}: unknown tag {e.get('tag')!r}")
        check(e.get("level") in levels, f"{eid}: unknown level {e.get('level')!r}")
        phrase = e.get("phrase") or ""
        check(bool(phrase), f"{eid}: no finished phrase")
        word = (e.get("answer") or "").lower()
        check(word in phrase.lower(), f"{eid}: the answer does not appear in its phrase")
        check(bool(e.get("fa")), f"{eid}: no Persian for the phrase")
        ex = e.get("example") or {}
        check(bool(ex.get("en")), f"{eid}: no English example")
        check(bool(ex.get("fa")), f"{eid}: no Persian for the example")
        if phrase and ex.get("en"):
            # the example may inflect the verb - "made a decision" - so what
            # has to appear is the partner the collocation is made of, not the
            # dictionary form of the answer
            partners = [w for w in phrase.split()
                        if w.lower() not in ("a", "an", "the", "in", "of", "to")
                        and w.lower() != word]
            # in a verb+preposition pair the answer *is* the partner
            if e.get("tag") == "verb+prep":
                partners.append(word)
            check(any(w.lower().strip(",.") in ex["en"].lower() for w in partners),
                  f"{eid}: the example never uses the collocation")
    kinds = {e.get("tag") for e in entries}
    check(kinds == tags, f"one kind of collocation is missing: {sorted(tags - kinds)}")


def wiring() -> None:
    src = WEBAPP.read_text(encoding="utf-8")
    check("const Practice = (() => {" in src, "the practice sheet is not in the page")
    check('id="prpanel"' in src, "the practice sheet has no markup")
    check("prpanel: null" in src, "the practice sheet is not registered with Panels")
    check("Practice.init()" in src, "the practice card is never mounted")
    # one Practice, one way in: the transcript card was the second interface
    check("practicecard" not in src,
          "the transcript practice card is still here - there must be one way in")
    check("mountPractice" not in src,
          "the practice card is still mounted alongside the drawer")
    check(src.count("const Practice = (() =>") == 1,
          "there is more than one Practice module")
    check(src.count("const PracticeDrawer = (() =>") == 1,
          "there is more than one practice navigation")
    check('#prpanel.open' in src,
          "the practice page is not opened as a section")
    check("data-pr-open" in src, "the card has no way into a drill")
    check("/api/collocations" in src, "the collocation bank has no route")
    check("/api/register" in src, "the register bank has no route")
    check("STT.sink" in src, "the microphone cannot be aimed at a drill instead of the composer")
    check("if (this.sink)" in src, "the transcript is committed to the composer anyway")
    check("SayMatch.compare(" in src, "nothing compares what was heard with the sentence")
    check("Drills.pairQuestion(" in src, "the ear test never asks anything")
    check("Drills.collocation(" in src, "the word-partner drill never asks anything")
    check("Drills.register(" in src, "the register drill never asks anything")
    check("collocations.json" in src, "the bank is not read from a file")
    if BUILT.exists():
        built = BUILT.read_text(encoding="utf-8")
        check("const Practice = (() => {" in built, "the built page has no practice sheet")
        check("practicecard" not in built,
              "the built page still carries the duplicate practice card")
    build = (ROOT / "build_apk_ui.py").read_text(encoding="utf-8")
    check('"collocations.json"' in build, "the APK bundle does not copy the collocation bank")
    check('"listening.json"' in build, "the APK bundle does not copy the listening bank")
    check((ROOT / "android/app/src/main/assets/www/data/listening.json").exists(),
          "the built APK data folder has no listening.json")


def drawer() -> None:
    """One practice navigation: the circle, the list, and a page per activity."""
    src = WEBAPP.read_text(encoding="utf-8")
    start = src.index("const PracticeDrawer = (() => {")
    tail = src[start:]
    board = tail[:tail.index("\n})();")]

    check('id="prdrawer"' in src, "the transcript has no practice drawer")
    check('id="prdnav"' in src, "the drawer has no place for the activities")
    check('id="prfab"' in src, "the transcript has no circular practice control")
    check('aria-controls="prdrawer"' in src,
          "the control does not name what it opens")
    check('aria-expanded' in src, "the control never says whether it is open")

    # the list is the sheet's own list, not a second one
    check("Practice.TABS.map(" in board,
          "the drawer does not build its rows from Practice.TABS")
    check("Practice.open(which)" in board,
          "choosing an activity does not open the practice page")
    check("data-pr-open" in board, "the rows are not wired to an activity")
    check("Panels.onClose(Practice.PANEL" in board,
          "closing a drill does not come back to the list")

    # and it is navigation only: no questions, no textarea, no marking
    for own in ("sheetHtml", "bindTo", "SayMatch.compare(", "Drills.collocation(",
                "Drills.register(", "Drills.pairQuestion(", "<textarea"):
        check(own not in board,
              "the drawer still renders the sheet itself (" + own + ")")

    # the page carries the way back, not a second row of drill tabs
    check("function backRow()" in src, "the drill page has no way back to the list")
    check("tabsHtml" not in src,
          "the drill page still has its own row of tabs beside the drawer")
    check("[data-pr-back]" in src,
          "the way back to the list is not wired to a click")
    check("Panels.set(PANEL, false)" in src,
          "the way back does not leave the page")
    check("PracticeDrawer.paint" not in src,
          "the page still asks the drawer to draw a drill")

    check("e.key !== 'Escape' || !open" in board,
          "Escape does not fold the drawer away")
    check(", true);" in board,
          "the drawer's Escape is not captured before the panel shell's")
    check('data-pr-drawer="close"' in src,
          "the drawer has no close control")
    check("await PracticeDrawer.init()" in src,
          "the drawer is never started")
    check("Panels.onClose" in src and "ON_CLOSE[panelId]()" in src,
          "the panel shell has no close hook")

    # every activity is a page, none is a half-page
    check('id="prpanel"' in src, "there is no practice page")
    check("#prpanel.open { display: block; }" in src or
          "#prpanel.open" in src, "the practice page never becomes a page")
    for panel in ("#prpanel",):
        check(f"{panel} h3" in src, f"{panel} has no page heading")

    if BUILT.exists():
        built = BUILT.read_text(encoding="utf-8")
        check('id="prfab"' in built, "the built page has no practice control")
        check('id="prdrawer"' in built, "the built page has no practice drawer")
        check('id="prdnav"' in built, "the built page has no activity list")


def main() -> int:
    result = run_block()
    content()
    wiring()
    drawer()
    if problems:
        for p in problems[:40]:
            print("FAIL  " + p)
        print(f"\nFAIL  {len(problems)} problem(s) with the practice drills")
        return 1
    print("PASS  practice: what was heard is compared word by word, the word partners "
          "are a curated bank asked with the partners English does not use, register "
          "has one right answer per question, the ear test asks the pairs the "
          "phonetics panel only listed, and the listening bank unwraps to sentences "
          "for dictation and say-it")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
