#!/usr/bin/env python3
"""What the learning path has to be true of, before anyone walks it.

  * the path - seven CEFR spaces in order, each with an English and a Persian
    name and a line about what the level can do, and exactly one of them with a
    course. A second course is a second entry, not a second page;
  * the course - six units, eighteen lessons, every one with an explanation, an
    example, guided practice and exercises, all six skills represented, and no
    lesson anywhere that is a heading with nothing under it;
  * the paper - six sections, thirty-three marks, every question carrying its
    answer and its Persian prompt, and every answer in range;
  * the engine - the model is run in node: where a learner starts, what a
    level's status is, what a lesson is worth, and the exam's own passing rule,
    including the one case that matters most - a speaking section nobody could
    hear is not a pass;
  * the wiring - a tile behind the level check, a panel, a route, the offline
    APK, and the place in the level check's own completion where the tile
    appears.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "path.json"
WEBAPP = ROOT / "webapp.py"
BUILDER = ROOT / "build_apk_ui.py"
CACHE = Path("/tmp/fluentify-path-check")
FA = re.compile(r"[\u0600-\u06FF]")
SKILLS = ["grammar", "vocabulary", "reading", "listening", "writing", "speaking"]
KINDS = {"mcq", "gap", "listen", "write", "say"}
LEVEL_IDS = ["PRE", "A1", "A2", "B1", "B2", "C1", "C2"]

problems: list[str] = []


def check(ok: bool, what: str) -> bool:
    if not ok:
        problems.append(what)
    return ok


def load() -> dict | None:
    if not DOC.exists():
        problems.append("path.json is missing")
        return None
    try:
        return json.loads(DOC.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        problems.append(f"path.json does not parse: {e}")
        return None


def fa_pair(check_ok: bool, where: str, pair: dict | None) -> bool:
    if not check_ok:
        return False
    if not isinstance(pair, dict):
        check(False, f"{where} is not a pair of languages")
        return False
    en, fa = str(pair.get("en") or ""), str(pair.get("fa") or "")
    ok = check(bool(en.strip()), f"{where} has no English") and \
        check(bool(FA.search(fa)), f"{where} has no Persian")
    return ok


def check_shape(doc: dict) -> dict:
    check(doc.get("version") == 1, "the path file is not the first format")

    levels = doc.get("levels") or []
    check([lv.get("id") for lv in levels] == LEVEL_IDS,
          f"levels are {[lv.get('id') for lv in levels]}")
    check(bool(levels) and levels[0].get("id") == "PRE",
          "Pre-A1 is not the first level of the path")
    check(bool(levels) and levels[0].get("label") == "Pre-A1",
          f"the first level is labelled {levels[0].get('label') if levels else None!r}")
    check(bool(levels) and levels[0].get("course") is None,
          "Pre-A1 claims a course it does not have")
    check("PRE" not in (doc.get("courses") or {}),
          "an unwritten Pre-A1 course was invented")

    seen = set()
    for lv in levels:
        lid = lv.get("id")
        where = f"level {lid}"
        check(bool(lv.get("label")), f"{where} has no label")
        check(isinstance(lv.get("name"), dict), f"{where} has no name")
        fa_pair(True, where + " name", lv.get("name"))
        fa_pair(True, where + " can-do line", lv.get("can"))
        check(lid not in seen, f"{where} appears twice")
        seen.add(lid)

    courses = doc.get("courses") or {}
    check(list(courses) == ["A1"],
          f"courses are {list(courses)} - only A1 is written, the rest are spaces")

    return {"levels": len(levels), "courses": list(courses)}


def check_course(doc: dict) -> dict:
    course = (doc.get("courses") or {}).get("A1") or {}
    fa_pair(True, "the A1 title", course.get("title"))
    fa_pair(True, "the A1 blurb", course.get("blurb"))

    units = course.get("units") or []
    check(len(units) == 6, f"A1 has {len(units)} units, not six")

    ids: set[str] = set()
    by_skill: dict[str, int] = {}
    exercises = 0
    guided = 0
    lessons = 0
    grammars: list[str] = []

    for ui, unit in enumerate(units, 1):
        where = f"unit {ui}"
        fa_pair(True, where + " title", unit.get("title"))
        fa_pair(True, where + " goal", unit.get("goal"))
        rows = unit.get("lessons") or []
        check(len(rows) >= 2, f"{where} has {len(rows)} lesson(s)")
        for lesson in rows:
            lessons += 1
            lid = lesson.get("id") or f"unit{ui}.lesson?"
            lw = f"lesson {lid}"
            check(lid not in ids, f"{lw} appears twice")
            ids.add(lid)
            skill = lesson.get("skill")
            check(skill in SKILLS + ["review"], f"{lw} has skill {skill!r}")
            by_skill[skill] = by_skill.get(skill, 0) + 1
            fa_pair(True, lw + " title", lesson.get("title"))
            fa_pair(True, lw + " goal", lesson.get("goal"))

            explain = lesson.get("explain") or []
            check(len(explain) >= 2, f"{lw} explains itself in {len(explain)} line(s)")
            for k, para in enumerate(explain):
                fa_pair(True, f"{lw} explanation {k + 1}", para)

            examples = lesson.get("examples") or []
            check(len(examples) >= 2, f"{lw} has {len(examples)} example(s)")
            for k, ex in enumerate(examples):
                fa_pair(True, f"{lw} example {k + 1}", ex)

            if lesson.get("passage"):
                fa_pair(True, lw + " passage title", lesson["passage"].get("title"))
                fa_pair(True, lw + " passage", lesson["passage"].get("text"))
            if lesson.get("dialogue"):
                check(len(lesson["dialogue"]) >= 2, f"{lw} dialogue is one line")
                for k, line in enumerate(lesson["dialogue"]):
                    check(bool(line.get("who")), f"{lw} dialogue line {k + 1} has no speaker")
                    fa_pair(True, f"{lw} dialogue line {k + 1}", line)

            guides = lesson.get("guided") or []
            check(len(guides) >= 2, f"{lw} has {len(guides)} guided question(s)")
            for k, q in enumerate(guides):
                guided += 1
                fa_pair(True, f"{lw} guided {k + 1} prompt", q.get("prompt"))
                opts = q.get("options") or []
                check(len(opts) == 4, f"{lw} guided {k + 1} has {len(opts)} options")
                check(isinstance(q.get("answer"), int) and 0 <= q["answer"] < len(opts),
                      f"{lw} guided {k + 1} points at no option")
                fa_pair(True, f"{lw} guided {k + 1} answer note", q.get("why"))

            exs = lesson.get("exercises") or []
            check(len(exs) >= 2, f"{lw} has {len(exs)} exercise(s)")
            if skill in ("grammar", "vocabulary"):
                grammars.append(lid)
            for k, e in enumerate(exs):
                exercises += 1
                ew = f"{lw} exercise {k + 1}"
                check(e.get("kind") in KINDS, f"{ew} is a {e.get('kind')!r}")
                if e.get("kind") in ("mcq", "listen"):
                    fa_pair(True, ew + " prompt", e.get("prompt"))
                    opts = e.get("options") or []
                    check(len(opts) == 4, f"{ew} has {len(opts)} options")
                    check(isinstance(e.get("answer"), int) and 0 <= e["answer"] < len(opts),
                          f"{ew} points at no option")
                    fa_pair(True, ew + " answer note", e.get("why"))
                elif e.get("kind") == "gap":
                    check("___" in str(e.get("text")), f"{ew} has no gap to fill")
                    answers = e.get("answer") or []
                    check(bool(answers), f"{ew} accepts no answer")
                    those = [str(a) for a in answers]
                    check(len(set(those)) == len(those), f"{ew} repeats an accepted answer")
                    fa_pair(True, ew + " answer note", e.get("why"))
                elif e.get("kind") == "write":
                    fa_pair(True, ew + " task", e.get("task"))
                    fa_pair(True, ew + " tips", e.get("tips"))
                    check(0 < int(e.get("words") or 0) <= 60, f"{ew} asks for {e.get('words')} words")
                    check(bool(e.get("needs")), f"{ew} does not ask for a link word")
                else:
                    check(bool(str(e.get("say") or "").strip()), f"{ew} has nothing to say")
                    check(bool(FA.search(str(e.get("fa") or ""))), f"{ew} has no Persian")
                if skill == "listening" and e.get("kind") == "listen":
                    check(bool(str(e.get("say") or "").strip()),
                          f"{ew} is a listening exercise with nothing to play")

    stats = {
        "units": len(units), "lessons": lessons, "exercises": exercises,
        "guided": guided, "by_skill": by_skill,
    }

    for skill in SKILLS:
        check(by_skill.get(skill, 0) >= 1, f"no {skill} lesson in the course")
    check(lessons == 18, f"A1 has {lessons} lessons, not eighteen")
    check(exercises == 67, f"A1 has {exercises} exercises, not sixty-seven")
    check(by_skill.get("grammar", 0) >= 6, "the grammar thread is thinner than six lessons")

    exam = course.get("exam") or {}
    check(exam.get("pass") == 0.6, "the pass mark is not 60%")
    check(exam.get("minSkill") == 0.5, "no per-skill minimum is set")
    fa_pair(True, "the exam blurb", exam.get("blurb"))

    sections = exam.get("sections") or []
    check([s.get("skill") for s in sections] == SKILLS,
          f"exam sections are {[s.get('skill') for s in sections]}")

    counts: dict[str, int] = {}
    for section in sections:
        skill = section.get("skill")
        items = section.get("items") or []
        if skill == "reading":
            check(len(items) >= 2, f"the reading section has {len(items)} passage(s)")
            marked = 0
            for gi, group in enumerate(items):
                fa_pair(True, f"reading passage {gi + 1}", group.get("text"))
                qs = group.get("questions") or []
                check(len(qs) >= 3, f"reading passage {gi + 1} asks {len(qs)} question(s)")
                for k, q in enumerate(qs):
                    marked += 1
                    qw = f"reading {gi + 1}.{k + 1}"
                    fa_pair(True, qw + " prompt", q.get("prompt"))
                    opts = q.get("options") or []
                    check(len(opts) == 4, f"{qw} has {len(opts)} options")
                    check(isinstance(q.get("answer"), int) and 0 <= q["answer"] < len(opts),
                          f"{qw} points at no option")
            counts["reading"] = marked
            continue

        counts[skill] = len(items)
        for i, item in enumerate(items):
            iw = f"exam {skill} {i + 1}"
            kind = item.get("kind")
            if kind == "write":
                fa_pair(True, iw + " task", item.get("task"))
                fa_pair(True, iw + " tips", item.get("tips"))
                check(0 < int(item.get("words") or 0) <= 60, f"{iw} asks for {item.get('words')} words")
                check(bool(item.get("needs")), f"{iw} does not ask for a link word")
            elif kind == "say":
                check(bool(str(item.get("say") or "").strip()), f"{iw} has nothing to say")
                check(bool(FA.search(str(item.get("fa") or ""))), f"{iw} has no Persian")
            else:
                fa_pair(True, iw + " prompt", item.get("prompt"))
                opts = item.get("options") or []
                check(len(opts) == 4, f"{iw} has {len(opts)} options")
                check(isinstance(item.get("answer"), int) and 0 <= item["answer"] < len(opts),
                      f"{iw} points at no option")
                fa_pair(True, iw + " answer note", item.get("why"))
                if skill == "listening":
                    check(bool(str(item.get("say") or "").strip()),
                          f"{iw} has nothing to play")

    want = {"grammar": 8, "vocabulary": 8, "reading": 6, "listening": 6,
            "writing": 2, "speaking": 3}
    for skill, n in want.items():
        check(counts.get(skill) == n, f"the exam has {counts.get(skill)} {skill} marks, not {n}")
    stats["paper"] = counts
    stats["exam"] = sum(counts.values())
    return stats


def check_wiring() -> None:
    src = WEBAPP.read_text(encoding="utf-8")
    build = BUILDER.read_text(encoding="utf-8")

    check('id="pathtoggle"' in src, "the header has no tile for the path")
    check('hidden\n              title="Learning path' in src or 'id="pathtoggle" aria-expanded="false" hidden' in src,
          "the path tile is not hidden until a placement exists")
    check('id="pathpanel"' in src, "the panel itself is missing")
    check("pathpanel: 'pathtoggle'," in src, "the panel is not in the tile table")
    check("pathpanel: () => Path.open()," in src, "opening the panel does not load the path")
    check("#pathpanel.open" in src and "display: block" in
          src[src.index("#pathpanel.open"):src.index("#pathpanel.open") + 120],
          "the panel has no rule that shows it")
    check("Path.init();" in src, "the path is never wired at boot")
    check("Path.sync()" in src, "the tile is never shown after the level check")
    check("Level.markWriting" in src or "markWriting(bank" in src,
          "the writing rubric is not the one the level check uses")
    check("/api/path" in src, "there is no route serving path.json")
    check('(ROOT / "path.json").read_bytes()' in src, "the route does not read the file")
    check('"path.json"' in build, "the offline APK does not carry path.json")

    for name in ("Practice", "Level", "Path"):
        check(f"const {name} =" in src, f"the {name} module is missing")
    check(src.index("const PathModel = {") < src.index("const Path = (() => {"),
          "the page is defined before the model it reads")


def check_engine() -> None:
    if not shutil.which("node"):
        print("SKIP  node is not installed - the path model was not exercised")
        return

    src = WEBAPP.read_text(encoding="utf-8")

    def block(opener: str) -> str:
        start = src.index(opener)
        end = src.index("\n})();", start) + len("\n})();")
        return src[start:end]

    say_start = src.index("const SAY_CONTRACTIONS = {")
    say_end = src.index("/* --- end say match", say_start)
    saymatch = src[say_start:say_end]

    model_start = src.index("const PathModel = {")
    model_end = src.index("\n};", model_start) + len("\n};")
    model = src[model_start:model_end]

    CACHE.mkdir(parents=True, exist_ok=True)
    script = CACHE / "path_engine.js"
    script.write_text(
        HARNESS.replace("__SAYMATCH__", saymatch)
               .replace("__LEVEL__", block("const Level = (() => {"))
               .replace("__MODEL__", model),
        encoding="utf-8",
    )

    proc = subprocess.run(["node", str(script), str(DOC)], capture_output=True, text=True)
    if proc.returncode != 0:
        problems.append("the path engine harness failed:\n" + (proc.stdout + proc.stderr).strip())
        return
    print(proc.stdout.strip())


HARNESS = r"""
const fs = require('fs');
const doc = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const LS = {};
global.localStorage = {
  getItem: (k) => (k in LS ? LS[k] : null),
  setItem: (k, v) => { LS[k] = String(v); },
  removeItem: (k) => { delete LS[k]; },
};
global.document = { getElementById: () => null, querySelector: () => null,
  querySelectorAll: () => [], addEventListener: () => {} };

__SAYMATCH__
__LEVEL__
__MODEL__

const say = (ok, what) => { if (!ok) { problems.push(what); } };
const problems = [];

const course = doc.courses.A1;
const exam = course.exam;
const fresh = {lessons: {}, passed: false};

/* ---- where a learner starts: the placement, never a default of A1 ---- */
[[{overall: 'A1'}, 'A1'], [{overall: 'A2'}, 'A2'], [{overall: 'B1'}, 'B1'],
 [{overall: 'B2'}, 'B2'], [{overall: 'C1'}, 'C1'], [{overall: 'C2'}, 'C2'],
 [{overall: 'PRE'}, 'PRE'], [{overall: 'Pre-A1'}, 'PRE'], [{overall: 'PRE-A1'}, 'PRE'],
 [{overall: 'pre-a1'}, 'PRE'], [null, 'PRE'], [{overall: 'X9'}, 'PRE']].forEach(([r, want]) => {
  say(PathModel.startLevel(r) === want,
      `a placement of ${r && r.overall} starts at ${want}, got ${PathModel.startLevel(r)}`);
});

/* ---- what a level's status is ---- */
say(PathModel.status('A1', 'A1', true, false) === 'current', 'A1 is not current for an A1 learner');
say(PathModel.status('A2', 'A2', false, false) === 'awaiting',
    'an assessed level with no course does not read as awaiting');
say(PathModel.status('A2', 'A1', false, false) === 'locked', 'A2 is not locked above an A1 learner');
say(PathModel.status('A2', 'B1', false, false) === 'past', 'A2 below a B1 learner is not behind them');
say(PathModel.status('A1', 'B1', true, false) === 'available',
    'an unwritten lower level with a course is not open');
say(PathModel.status('A1', 'A1', true, true) === 'done', 'a passed level is not done');
say(PathModel.status('C2', 'C2', false, false) === 'awaiting',
    'the assessed top level with no course does not offer its space');
say(PathModel.status('B1', 'PRE', false, false) === 'locked', 'nothing above PRE should be open');
say(PathModel.status('A2', 'A1', false, false, true) === 'awaiting',
    'passing A1 does not make A2 the next level');
say(PathModel.status('A2', 'A1', false, false, false) === 'locked',
    'A2 opens before A1 is passed');
say(PathModel.status('A2', 'A1', true, false, true) === 'locked',
    'a written A2 above an A1 learner is open without the pass');

/* A learner placed on a level whose course is not written has nothing to open,
   so the nearest written level above is offered by name - and the assessed
   card still says its own curriculum is missing. */
say(PathModel.status('PRE', 'PRE', false, false) === 'awaiting',
    'Pre-A1 with no course is not shown as awaiting');
say(PathModel.status('A1', 'PRE', true, false, false, 'A1') === 'available',
    'a Pre-A1 learner is not offered the A1 course');
say(PathModel.status('B1', 'PRE', false, false, false, 'A1') === 'locked',
    'a Pre-A1 learner is offered a level with no course');
say(PathModel.status('A2', 'PRE', true, false, false, 'A1') === 'locked',
    'a Pre-A1 learner is offered a level above the written one');

/* ---- progress ---- */
const s0 = PathModel.stats(course, fresh);
say(s0.total === 18, `the course counts ${s0.total} lessons, not eighteen`);
say(s0.done === 0 && s0.share === 0, 'a fresh course already has progress');
say(s0.complete === false, 'a fresh course reads as complete');
say(PathModel.SKILLS.every((k) => s0.bySkill[k].total > 0),
    'a skill has no lesson in the progress rows');

const oneLesson = PathModel.lessons(course)[0].lesson;
const part = {lessons: {[oneLesson.id]: {done: true, at: '2026-01-01', right: 4, total: 5}},
              passed: false};
const s1 = PathModel.stats(course, part);
say(s1.done === 1, 'one marked lesson does not count as one');
say(Math.abs(s1.share - 1 / 18) < 1e-9, 'one of eighteen is not the share it reports');
say(s1.bySkill[oneLesson.skill].done === 1, 'the skill bar did not move');

/* ---- the paper ---- */
const paper = PathModel.paper(exam);
const ids = new Set(paper.map((q) => q.id));
say(paper.length === 33, `the paper is ${paper.length} questions, not thirty-three`);
say(ids.size === paper.length, 'two questions share an id');
PathModel.SKILLS.forEach((s) => {
  const n = paper.filter((q) => q.skill === s).length;
  say(n > 0, `the paper asks nothing about ${s}`);
});
say(paper.filter((q) => q.skill === 'reading').every((q) => q.passage && q.item),
    'a reading question arrived without its passage');

/* ---- marking an objective answer ---- */
const mcq = paper.find((q) => q.skill === 'listening');
say(mcq && mcq.kind === 'listen', 'the listening marks are not listening questions');
say(PathModel.answerRight(mcq.item, mcq.item.answer), 'the right option was marked wrong');
say(!PathModel.answerRight(mcq.item, (mcq.item.answer + 1) % 4), 'a wrong option was marked right');
say(!PathModel.answerRight(mcq.item, undefined), 'an unanswered question was marked right');

/* ---- a perfect paper, and a blank one ---- */
const BASE = ['My name is Sara and I am from Iran.',
  'I live in a small flat with my family.',
  'I get up at seven and I have breakfast.',
  'I go to school by bus and I come home at four.',
  'In the evening I read a book and I go to bed at eleven.'];
const CLAUSE = {
  like: 'I like my room very much.',
  every: 'I study English every day.',
  there: 'There is a desk in my room.',
  in: 'My books are in the box.',
};
/* A model answer per writing task, built from that task's own required link
   words: the paper asks for different things in its two tasks, and a marker
   that cannot give full marks to an answer written to the brief is a marker
   nobody can pass. */
const compose = (item) => BASE.concat(
  (item.needs || []).filter((n) => !BASE.join(' ').toLowerCase().includes(n))
    .map((n) => CLAUSE[n] || (n + ' is here.'))).join(' ');
const answers = {};
paper.forEach((q) => {
  if (q.kind === 'gap') answers[q.id] = q.item.answer[0];
  else if (q.kind !== 'write' && q.kind !== 'say') answers[q.id] = q.item.answer;
});
const writing = exam.sections.find((x) => x.skill === 'writing').items;
const texts = writing.map((item) => compose(item));
const heard = paper.filter((q) => q.skill === 'speaking').map((q) => q.item.say);

const good = PathModel.grade(exam, answers, texts, heard);
say(good.pass === true, 'a perfect paper does not pass');
say(good.missing.length === 0, `a perfect paper is missing ${good.missing}`);
say(Math.abs(good.overall - 1) < 1e-9, `a perfect paper scores ${good.overall}`);

const blank = PathModel.grade(exam, {}, [], []);
say(blank.pass === false, 'an untouched paper passes');
say(blank.overall < 0.2, `an untouched paper scores ${blank.overall}`);
say(blank.missing.indexOf('speaking') >= 0,
    'a paper with no speaking on it does not report speaking as missing');
say(blank.skills.writing.share === 0, 'blank writing earned something');

/* The one rule this whole section exists for: a skill nobody could hear is
   not a pass, however good the rest of the paper is. */
const noSpeech = PathModel.grade(exam, answers, texts, ['', '', '']);
say(noSpeech.pass === false, 'a paper with no speaking passes');
say(noSpeech.missing.length === 1 && noSpeech.missing[0] === 'speaking',
    `silent speaking reports ${noSpeech.missing}`);
say(noSpeech.skills.speaking.assessed === false, 'silent speaking counts as assessed');
say(noSpeech.skills.grammar.share === 1, 'the grammar marks were lost with the speech');

/* Half of grammar right and everything else perfect is still a fail, because
   the floor is per skill, not only overall. */
const weakGrammar = {};
Object.keys(answers).forEach((k) => { weakGrammar[k] = answers[k]; });
paper.filter((q) => q.skill === 'grammar').slice(0, 5)
  .forEach((q) => { weakGrammar[q.id] = (q.item.answer + 1) % 4; });
const floor = PathModel.grade(exam, weakGrammar, texts, heard);
say(floor.pass === false, 'five of eight in grammar slipped through the per-skill floor');
say(floor.skills.grammar.passed === false, 'a skill under the floor reads as passed');
say(floor.overall > 0.6, 'the fixture is not above the overall pass mark');

/* ---- and the advice it gives back ---- */
const advice = PathModel.recommend(course, fresh, ['grammar']);
say(advice.length > 0, 'a weak skill recommends no lesson');
say(advice.every((l) => l.skill === 'grammar'), 'the advice leaves the weak skill');
const allGrammar = PathModel.lessons(course)
  .filter((r) => r.lesson.skill === 'grammar')
  .map((r) => [r.lesson.id, {done: true}]);
const told = PathModel.recommend(course, {...fresh, lessons: Object.fromEntries(allGrammar)},
  ['grammar']);
say(told.length > 0, 'a weak skill whose lessons are all done gets no advice at all');
say(told.every((l) => l.skill === 'grammar'), 'the advice drifts off the weak skill');
say(PathModel.recommend(course, fresh, ['nothing']).length === 0,
    'a skill the course does not teach produced advice');

if (problems.length) {
  problems.forEach((p) => console.log('FAIL  ' + p));
  process.exit(1);
}
console.log(`PASS  ${paper.length} exam marks over six skills, ` +
  `${PathModel.lessons(course).length} lessons, one pass rule`);
"""


def main() -> int:
    doc = load()
    stats = check_shape(doc) if doc else {}
    if doc:
        stats.update(check_course(doc))
    check_wiring()
    check_engine()

    if problems:
        for p in problems:
            print("FAIL  " + p)
        print(f"\n{len(problems)} problem(s) with the learning path")
        return 1

    print(f"PASS  {stats.get('levels')} level spaces, {stats.get('units')} units, "
          f"{stats.get('lessons')} lessons, {stats.get('exercises')} exercises, "
          f"{stats.get('exam')} exam marks")
    print(f"      skills {dict(sorted((stats.get('by_skill') or {}).items()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
