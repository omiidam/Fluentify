#!/usr/bin/env python3
"""What the learning path has to be true of, before anyone walks it.

  * the path - seven CEFR spaces in order, each with an English and a Persian
    name and a line about what the level can do, and five of them with a course
    (A1 to C1). A second course is a second entry, not a second page;
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
# What each written course is: units, lessons, exercises. A1 is the reference
# course and must not change; A2 and B1 came next, then B2 and C1.
COURSE_SHAPE = {"A1": (6, 18, 67), "A2": (8, 24, 95), "B1": (8, 24, 94),
                "B2": (8, 24, 94), "C1": (8, 24, 89)}
# The length a writing task may ask for. A1 to B1 write a short paragraph; B2 and
# C1 write a report or an essay, and marking a hundred and fifty words against a
# sixty-word ceiling would fail every correct answer.
WRITE_CAP = {"A1": 60, "A2": 60, "B1": 60, "B2": 160, "C1": 160}


def word_cap(lid: str) -> int:
    return WRITE_CAP.get(lid, 60)

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
    written = [lv.get("id") for lv in levels if lv.get("course")]
    check(list(courses) == written,
          f"the courses {list(courses)} do not match the levels claiming one ({written})")
    for lid, course in courses.items():
        row = next((lv for lv in levels if lv.get("id") == lid), None)
        check(bool(row), f"a course was written for {lid}, which is not a level")
        check(bool(row) and row.get("course") == lid,
              f"level {lid} does not point at its own course")
        check(len(course.get("units") or []) >= 6, f"{lid} has fewer than six units")
    for lid in ("A1", "A2", "B1", "B2", "C1"):
        check(lid in courses, f"{lid} has no course")
    check("C2" not in courses,
          "C2 was implemented, and this task stops at C1")

    return {"levels": len(levels), "courses": list(courses)}


def check_one_course(lid: str, course: dict) -> dict:
    want_units, want_lessons, want_exercises = COURSE_SHAPE.get(lid, (6, 18, 67))
    fa_pair(True, f"the {lid} title", course.get("title"))
    fa_pair(True, f"the {lid} blurb", course.get("blurb"))

    units = course.get("units") or []
    check(len(units) == want_units, f"{lid} has {len(units)} units, not {want_units}")

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
            lesson_id = lesson.get("id") or f"unit{ui}.lesson?"
            lw = f"lesson {lesson_id}"
            check(lesson_id not in ids, f"{lw} appears twice")
            ids.add(lesson_id)
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
                grammars.append(lesson_id)
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
                    check(0 < int(e.get("words") or 0) <= word_cap(lid),
                          f"{ew} asks for {e.get('words')} words")
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
        check(by_skill.get(skill, 0) >= 1, f"no {skill} lesson in the {lid} course")
    check(lessons == want_lessons, f"{lid} has {lessons} lessons, not {want_lessons}")
    check(exercises == want_exercises,
          f"{lid} has {exercises} exercises, not {want_exercises}")
    check(by_skill.get("grammar", 0) >= 6, f"the {lid} grammar thread is thinner than six lessons")
    check(by_skill.get("vocabulary", 0) >= 5, f"the {lid} vocabulary thread is thinner than five lessons")

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
                check(0 < int(item.get("words") or 0) <= word_cap(lid),
                      f"{iw} asks for {item.get('words')} words")
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
    stats["id"] = lid
    stats["ids"] = ids
    stats["titles"] = [l.get("title", {}).get("en", "") for u in units for l in u["lessons"]]
    stats["lines"] = [p.get("en", "") for u in units for l in u["lessons"]
                      for p in (l.get("explain") or [])]
    return stats


def check_course(doc: dict) -> dict:
    """Every course on its own, then all of them against each other."""
    courses = doc.get("courses") or {}
    total = {"units": 0, "lessons": 0, "exercises": 0, "guided": 0,
             "exam": 0, "by_skill": {}}
    ids: set[str] = set()
    titles: dict[str, str] = {}
    lines: dict[str, str] = {}

    for lid, course in courses.items():
        stats = check_one_course(lid, course)
        for key in ("units", "lessons", "exercises", "guided", "exam"):
            total[key] += stats[key]
        for skill, n in stats["by_skill"].items():
            total["by_skill"][skill] = total["by_skill"].get(skill, 0) + n

        for lesson_id in stats["ids"]:
            check(lesson_id not in ids, f"lesson id {lesson_id} is reused across courses")
            ids.add(lesson_id)
        for title in stats["titles"]:
            if not title:
                continue
            check(title not in titles,
                  f"{lid} repeats the lesson title {title!r} from {titles.get(title)}")
            titles.setdefault(title, lid)
        for line in stats["lines"]:
            if not line.strip():
                continue
            check(line not in lines,
                  f"{lid} repeats an explanation from {lines.get(line)}")
            lines.setdefault(line, lid)

    return total


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
    'passing A1 does not make an unwritten A2 the next level');
say(PathModel.status('A2', 'A1', false, false, false) === 'locked',
    'A2 opens before A1 is passed');
say(PathModel.status('A2', 'A1', true, false, false) === 'locked',
    'a written A2 is open to an A1 learner who has not passed A1');

/* ---- the progression A2 and B1 exist for ---- */
say(PathModel.status('A2', 'A1', true, false, true) === 'available',
    'passing A1 does not open the A2 course');
say(PathModel.status('B1', 'A1', true, false, false) === 'locked',
    'a pass at A1 opens B1 directly');
say(PathModel.status('B1', 'A2', true, false, true) === 'available',
    'passing A2 does not open the B1 course');
say(PathModel.status('B2', 'B1', false, false, true) === 'awaiting',
    'passing B1 does not make an unwritten B2 the next level');
/* From B2 upwards the courses exist, so the pass above opens the next one by
   name - and C2, the only space with no curriculum, stays a space. */
say(PathModel.status('B2', 'B1', true, false, true) === 'available',
    'passing B1 does not open the B2 course');
say(PathModel.status('C1', 'B2', true, false, true) === 'available',
    'passing B2 does not open the C1 course');
say(PathModel.status('C1', 'B1', true, false, false) === 'locked',
    'C1 is open two levels early');
say(PathModel.status('C2', 'C1', false, false, true) === 'awaiting',
    'passing C1 does not leave C2 waiting for its curriculum');
say(PathModel.status('B2', 'B2', true, false) === 'current',
    'an assessed B2 learner does not start on B2');
say(PathModel.status('C1', 'C1', true, false) === 'current',
    'an assessed C1 learner does not start on C1');
say(PathModel.status('B1', 'C1', true, false) === 'available',
    'a C1 learner cannot go back to the B1 course');
say(PathModel.status('B2', 'B1', false, false, false) === 'locked',
    'B2 opens before B1 is passed');

/* An assessed A2 or B1 learner starts there, not at A1. */
say(PathModel.status('A2', 'A2', true, false) === 'current',
    'an assessed A2 learner does not start on A2');
say(PathModel.status('B1', 'B1', true, false) === 'current',
    'an assessed B1 learner does not start on B1');
say(PathModel.status('A1', 'B1', true, false) === 'available',
    'a B1 learner cannot go back to the A1 course');

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

/* Every written course is walked with the same expectations: the paper is the
   same thirty-three marks, the pass rule is the same, and a course that cannot
   be completed and passed is not a course. */
const runCourse = (lid, course) => {
const exam = course.exam;
const fresh = {lessons: {}, passed: false};
const total = PathModel.lessons(course).length;

/* ---- progress ---- */
const s0 = PathModel.stats(course, fresh);
say(s0.total === total, `${lid} counts ${s0.total} lessons, not ${total}`);
say(s0.done === 0 && s0.share === 0, `a fresh ${lid} course already has progress`);
say(s0.complete === false, `a fresh ${lid} course reads as complete`);
say(PathModel.SKILLS.every((k) => s0.bySkill[k].total > 0),
    `a skill has no lesson in the ${lid} progress rows`);

const oneLesson = PathModel.lessons(course)[0].lesson;
const part = {lessons: {[oneLesson.id]: {done: true, at: '2026-01-01', right: 4, total: 5}},
              passed: false};
const s1 = PathModel.stats(course, part);
say(s1.done === 1, 'one marked lesson does not count as one');
say(Math.abs(s1.share - 1 / total) < 1e-9,
    `one of ${total} is not the share it reports`);
say(s1.bySkill[oneLesson.skill].done === 1, 'the skill bar did not move');

/* ---- the paper ---- */
const paper = PathModel.paper(exam);
const ids = new Set(paper.map((q) => q.id));
say(paper.length === 33, `the ${lid} paper is ${paper.length} questions, not thirty-three`);
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
  'In the evening I read a book and I go to bed at eleven.',
  'Last summer I travelled to the north with two friends.'];
const CLAUSE = {
  like: 'I like my room very much.',
  every: 'I study English every day.',
  there: 'There is a desk in my room.',
  in: 'My books are in the box.',
  went: 'I went there by train and stayed four days.',
  because: 'I chose the early train because it was cheaper.',
  could: 'Could you send me the address?',
  if: 'If the weather is good, we will walk to the village.',
  would: 'I would like to go back next spring.',
  worth: 'The old market is worth a visit in the morning.',
  although: 'Although the hotel was small, the staff were helpful.',
  so: 'It was raining, so we stayed inside.',
  but: 'The food was good, but the music was too loud.',
};
/* A model answer per writing task, built from that task's own required link
   words: the paper asks for different things in its two tasks, and a marker
   that cannot give full marks to an answer written to the brief is a marker
   nobody can pass. */
const EXTRA = [
  'The report was written after the meeting and the figures were checked twice.',
  'Although the trial was short, the effect was consistent at every site.',
  'What matters most is not the cost but the assumption behind the plan.',
  'Having read both proposals, the committee recommended the cheaper one.',
  'The evidence suggests a modest improvement, though the sample was small.',
  'Far from settling the question, the second study widened it considerably.',
  'The pilot ran for six weeks before anyone asked whether it had worked.',
];
const wordCount = (t) => t.split(/\s+/).filter(Boolean).length;
const compose = (item) => {
  let text = BASE.concat(
    (item.needs || []).filter((n) => !BASE.join(' ').toLowerCase().includes(n))
      .map((n) => CLAUSE[n] || (n + ' is here.'))).join(' ');
  /* A B2 or C1 report asks for more words than the base paragraph carries; the
     model answer has to be written to the brief, not to A1's. */
  for (let i = 0; wordCount(text) < (item.words || 30) && i < 40; i += 1) {
    text += ' ' + EXTRA[i % EXTRA.length];
  }
  return text;
};
const answers = {};
paper.forEach((q) => {
  if (q.kind === 'gap') answers[q.id] = q.item.answer[0];
  else if (q.kind !== 'write' && q.kind !== 'say') answers[q.id] = q.item.answer;
});
const writing = exam.sections.find((x) => x.skill === 'writing').items;
const texts = writing.map((item) => compose(item));
const heard = paper.filter((q) => q.skill === 'speaking').map((q) => q.item.say);

const good = PathModel.grade(exam, answers, texts, heard);
say(good.pass === true, `a perfect ${lid} paper does not pass`);
say(good.missing.length === 0, `a perfect ${lid} paper is missing ${good.missing}`);
say(Math.abs(good.overall - 1) < 1e-9, `a perfect ${lid} paper scores ${good.overall}`);

const blank = PathModel.grade(exam, {}, [], []);
say(blank.pass === false, `an untouched ${lid} paper passes`);
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
};

Object.keys(doc.courses).forEach((lid) => runCourse(lid, doc.courses[lid]));

if (problems.length) {
  problems.forEach((p) => console.log('FAIL  ' + p));
  process.exit(1);
}
const courses = Object.keys(doc.courses);
const lessons = courses.reduce((n, id) => n + PathModel.lessons(doc.courses[id]).length, 0);
console.log(`PASS  ${courses.length} courses (${courses.join(', ')}), ${lessons} lessons, ` +
  `33 marks each, one pass rule`);
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
