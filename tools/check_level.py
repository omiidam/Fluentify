#!/usr/bin/env python3
"""What the level assessment has to be true of, before anyone sits it.

  * the bank - every item carries the metadata the report needs, every band
    has a full block for every assessed skill, every Persian line is Persian;
  * the wiring - a tile, a panel, a route, a retake window, and the offline
    APK carrying the file;
  * the engine - the module's own paper and marking are run in node over
    synthetic learners: a perfect one, a hopeless one, one who is exactly B1,
    and one who stops after the first part. The level has to follow the count,
    and unanswered questions have to count as wrong.
"""

from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "level_test.json"
WEBAPP = ROOT / "webapp.py"
BUILDER = ROOT / "build_apk_ui.py"
CACHE = Path("/tmp/fluentify-level-check")
BANDS = ["A1", "A2", "B1", "B2", "C1"]
FA = re.compile(r"[\u0600-\u06FF]")
KINDS = {"mcq", "cloze", "error", "transform", "order", "shortwriting", "speaking"}

problems: list[str] = []


def check(ok: bool, what: str) -> bool:
    if not ok:
        problems.append(what)
    return ok


def load() -> dict | None:
    if not DOC.exists():
        problems.append("level_test.json is missing (run tools/build_level.py)")
        return None
    try:
        return json.loads(DOC.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        problems.append(f"level_test.json does not parse: {e}")
        return None


def check_fresh() -> None:
    proc = subprocess.run([sys.executable, str(ROOT / "tools/build_level.py"), "--check"],
                          cwd=ROOT, capture_output=True, text=True)
    check(proc.returncode == 0,
          "level_test.json is out of date with tools/level_test.py "
          "(run python3 tools/build_level.py)")


def check_content(doc: dict) -> dict:
    check(doc.get("retakeDays") == 30, "the result is not kept for one month")
    check(doc.get("version") == 2, "the bank is not the second-format bank")

    skills = doc.get("skills") or []
    assessed = [s["id"] for s in skills if s.get("assessed")]
    check(assessed == ["grammar", "vocabulary", "reading", "listening", "writing"],
          f"assessed skills are {assessed}")
    check([s["id"] for s in skills if not s.get("assessed")] == ["speaking"],
          "speaking is not the only practice-only skill")
    for s in skills:
        check(bool(FA.search(s.get("blurb", {}).get("fa", ""))),
              f"skill {s['id']}: the blurb has no Persian")

    bands = [b.get("id") for b in doc.get("bands") or []]
    check(bands == ["PRE"] + BANDS + ["C2"], f"bands are {bands}")
    check(doc.get("testedBands") == BANDS, "the tested bands are not A1 to C1")

    bp = doc.get("blueprint") or {}
    check(bp.get("bands") == BANDS, f"the blueprint tests {bp.get('bands')}")
    check(bp.get("questions") == 55, f"the paper is {bp.get('questions')} questions")
    check(sum((bp.get("perBand") or {}).values()) == bp.get("perBandTotal"),
          "the per-band counts do not add up to a band")
    check(bp.get("perBandTotal") * len(BANDS) == bp.get("questions"),
          "eleven questions a band does not make the paper")
    check(bp.get("objective") == [s for s in assessed if s != "writing"],
          f"the recognition questions are {bp.get('objective')}")
    check(bp.get("writingPoints") == 4, "a writing task is not worth four points")
    cut = bp.get("cutoffs") or []
    check(len(cut) == len(BANDS) and cut == sorted(cut) and all(0 < c < 1 for c in cut),
          f"the cutoffs are {cut}")
    # The cutoffs are shares, so the count a band needs is the first whole
    # question at or above it: 8.8 of 55 is nine right, 48.4 is forty-nine.
    check(math.ceil(cut[0] * 55) == 9 and math.ceil(cut[4] * 55) == 49,
          f"the first cutoff is {math.ceil(cut[0] * 55)} of 55, "
          f"the last {math.ceil(cut[4] * 55)}")
    scale = doc.get("writingScale") or {}
    check(list(scale) == BANDS, f"the writing scale covers {list(scale)}")
    for band, row in scale.items():
        check(row.get("words", 0) >= 20 and row.get("sentences", 0) >= 2,
              f"writing scale {band}: {row} is not a task worth marking")

    items = doc.get("items") or []
    by_skill = Counter(it.get("skill") for it in items)
    by_band = Counter((it.get("skill"), it.get("band")) for it in items)
    kinds = Counter(it.get("kind") for it in items)
    keys = []
    ids = set()

    for it in items:
        where = it.get("id") or "an item with no id"
        check(where not in ids, f"{where}: duplicate id")
        ids.add(where)
        for field in ("id", "skill", "band", "subskill", "kind", "difficulty",
                      "ability", "prompt", "why", "weight", "source", "review"):
            check(field in it, f"{where}: no {field}")
        check(it.get("kind") in KINDS, f"{where}: unknown kind {it.get('kind')}")
        check(it.get("review") == "reviewed", f"{where}: not marked reviewed")
        check(bool(it.get("source")), f"{where}: no source")
        check(it.get("band") in BANDS, f"{where}: band {it.get('band')}")
        for field in ("subskill", "ability", "prompt", "why"):
            check(bool(FA.search(it.get(field, {}).get("fa", ""))),
                  f"{where}: {field} has no Persian")

        if it.get("kind") in ("mcq", "error"):
            opts = it.get("options") or []
            check(len(opts) == 4, f"{where}: {len(opts)} options")
            check(len(set(opts)) == len(opts), f"{where}: duplicate options")
            if isinstance(it.get("answer"), int) and 0 <= it["answer"] < 4:
                keys.append(it["answer"])
            else:
                problems.append(f"{where}: answer is not one of the options")
        if it.get("kind") in ("cloze", "transform", "order"):
            check(bool(it.get("accept")), f"{where}: typed item with nothing accepted")
        if it.get("kind") == "order":
            check(len(it.get("tokens") or []) >= 4, f"{where}: too few tokens to reorder")
        if it.get("say"):
            check(len(it["say"].split()) >= 6, f"{where}: spoken text too short")

    check(len(items) >= 54, f"only {len(items)} items in the bank")
    check(len(kinds) >= 5, f"only {len(kinds)} question formats")
    check(kinds.get("mcq", 0) < len(items) * 0.65,
          "the bank is mostly multiple choice")
    per_band = bp.get("perBand") or {}
    for skill in assessed:
        for band in BANDS:
            n = by_band[(skill, band)]
            check(n == per_band.get(skill),
                  f"{skill}/{band}: {n} items, the paper wants {per_band.get(skill)}")
    for band in BANDS:
        n = sum(by_band[(s, band)] for s in assessed)
        check(n == bp.get("perBandTotal"),
              f"band {band}: {n} questions, the paper wants {bp.get('perBandTotal')}")
    check(by_skill["speaking"] >= 2, "fewer than two speaking tasks")
    # One marked writing task per band, each naming the linking the rubric
    # point is looking for - without it there is nothing to check but length.
    for band in BANDS:
        tasks = [it for it in items
                 if it.get("skill") == "writing" and it.get("band") == band]
        check(len(tasks) == 1, f"band {band} has {len(tasks)} marked writing tasks")
        for task in tasks:
            check(len(task.get("needs") or []) >= 2,
                  f"{task['id']}: no linking words to look for")

    passages = {p["id"]: p for p in doc.get("passages") or []}
    check(len(passages) >= 5, "fewer than five reading passages")
    for pid, p in passages.items():
        check(bool(FA.search(p["text"]["fa"])), f"passage {pid}: no Persian")
        words = len(p["text"]["en"].split())
        floor = 20 if p["band"] == "A1" else 60
        check(words >= floor, f"passage {pid}: {words} words, below {floor}")
        asked = sum(1 for it in items if it.get("passage") == pid)
        check(asked == per_band.get("reading", 2),
              f"passage {pid}: {asked} questions")
    for it in items:
        if it.get("passage"):
            check(it["passage"] in passages,
                  f"{it['id']}: points at a passage that is not there")

    check(len(set(keys)) >= 3, "the answer keys use fewer than three letters")
    if keys:
        check(Counter(keys).most_common(1)[0][1] <= len(keys) * 0.55,
              "one answer letter dominates the test")

    total_session = sum(by_band[(s, b)] for s in assessed for b in BANDS)
    check(total_session == bp.get("questions"),
          f"the bank holds {total_session} questions, the paper is {bp.get('questions')}")
    return {"items": len(items), "kinds": kinds, "session": total_session}


def check_wiring() -> None:
    src = WEBAPP.read_text(encoding="utf-8")
    for needle, what in (
        ('id="lvltoggle"', "the header has no Level tile"),
        ('id="lvlpanel"', "there is no level panel"),
        ('id="lvlbody"', "the level panel has nowhere to draw"),
        ("lvlpanel: 'lvltoggle'", "the panel is not registered with the tiles"),
        ("lvlpanel: () => Level.mount()", "opening the panel never mounts it"),
        ("document.getElementById('lvltoggle').onclick", "the tile is not wired"),
        ('self.path.startswith("/api/level_test")', "the web build has no route"),
        ("Level.paintBadge();", "the tile badge is never painted from a stored result"),
        ("openLevel(level)", "the report cannot filter the story shelf"),
        ('#lvlpanel.open', "the panel never becomes visible"),
        ("fluentify.level.v2.result", "nothing is stored under the result key"),
        ("fluentify.level.v2.attempt", "a half-finished assessment has nowhere to live"),
        ("fluentify.level.items", "item difficulty is not tracked locally"),
        ("levelFromCorrect(", "the reporting never turns a count into a band"),
        ("not assessed", "the report never says which skills were not assessed"),
    ):
        check(needle in src, what)

    check("level_test.json" in BUILDER.read_text(encoding="utf-8"),
          "the offline build does not ship the question bank")
    check((ROOT / "android/app/src/main/assets/www/data/level_test.json").exists(),
          "the built APK data folder has no level_test.json")


def check_engine() -> None:
    if not shutil.which("node"):
        print("SKIP  node is not installed - the staircase was not exercised")
        return

    src = WEBAPP.read_text(encoding="utf-8")
    start = src.index("const Level = (() => {")
    end = src.index("\n})();", start) + len("\n})();")
    module = src[start:end]
    check("function levelFromCorrect(right, total, cutoffs)" in module,
          "the engine no longer turns a count into a band")
    check("function paper(bank)" in module,
          "the engine no longer builds one paper for everyone")

    CACHE.mkdir(parents=True, exist_ok=True)
    script = CACHE / "level_engine.js"
    script.write_text(HARNESS.replace("__MODULE__", module), encoding="utf-8")

    proc = subprocess.run(["node", str(script), str(DOC)],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        problems.append("the engine harness failed:\n" + (proc.stdout + proc.stderr).strip())
        return
    print(proc.stdout.strip())


HARNESS = r"""
const fs = require('fs');
const bank = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
__MODULE__

const right = (item) => item.options ? item.answer : (item.accept || [])[0];
const wrong = (item) => item.options ? (item.answer + 1) % 4 : 'zzz';

/* A model answer per band, written to earn all four rubric points. The
   harness asserts that it does: a marker that cannot give full marks to a
   good paragraph is a marker nobody can pass. */
const MODEL = {
  A1: 'My family is small and we are close. I live with my mother and my sister in a flat near the park. We cook dinner together on Friday and then we watch a movie.',
  A2: 'Last weekend I went to the park with my friend. We walked by the river and then we ate lunch outside. The weather was sunny and warm. I liked the afternoon because we talked for hours.',
  B1: 'The old bazaar is the best place to start because the building is beautiful. Then walk down to the river and take a boat for an hour. The food near the bridge is cheap and very good. Visit the museum if it rains, since it is indoors. Two days is enough for all of this.',
  B2: 'I think phones should be banned in classrooms. They distract students and they stop conversation between lessons. However, a phone is a useful tool for research when the teacher allows it. Most schools already have laptops, so the loss is small. A ban with clear exceptions is better than a total one, although it needs enforcing. Teachers should decide when a screen is allowed. That keeps the rule simple and it keeps the lesson moving.',
  C1: 'Remote work arguably harms young employees, although the effect is not uniform. Junior staff may miss the informal learning that happens in an office, and they might not build the networks that promotion depends on. However, to some extent this reflects poor management rather than remote work itself. Companies that invest in mentoring tend to keep their young staff, and those that do not lose them whether the desk is at home or in the building. The problem is solvable, but not by attendance alone. Training does more than proximity, and it can be measured.',
};

/* Sits the paper, answering `good(item)` correctly, and stopping after part
   `stopAfterPart` when one is given. A full sit also writes the five tasks. */
function sit(good, stopAfterPart) {
  const a = Level.blankAttempt();
  const seen = [];
  for (let p = 0; p < Level.partCount(bank); p++) {
    if (stopAfterPart != null && p > stopAfterPart) break;
    Level.partIds(bank, p).forEach((id) => {
      const item = bank.items.find((i) => i.id === id);
      seen.push(id);
      a.answers[id] = good(item) ? right(item) : wrong(item);
    });
  }
  if (stopAfterPart == null) {
    Level.writingIds(bank).forEach((id) => {
      const item = bank.items.find((i) => i.id === id);
      a.practice.writing[id] = {text: MODEL[item.band]};
    });
  }
  a.finishedAt = a.startedAt + 22 * 60 * 1000;
  return {result: Level.compute(bank, a), seen, attempt: a};
}

let problems = 0;
const say = (ok, line) => { if (!ok) problems++; console.log(`${ok ? '  ok  ' : '  FAIL'}  ${line}`); };
const overall = (r) => r.overall || 'Pre-A1';

const ids = Level.paper(bank);
say(ids.length === 50, `the paper is fifty questions (got ${ids.length})`);
say(new Set(ids).size === ids.length, 'no question appears twice');
say(Level.partCount(bank) === 5, `the paper is in five parts (got ${Level.partCount(bank)})`);
say(Level.partIds(bank, 0).length === 10 && Level.partIds(bank, 4).length === 10,
    'each part is ten questions');
say(Level.partIds(bank, 0).every((id) => bank.items.find((i) => i.id === id).band === 'A1'),
    'the first part is the A1 band');
say(Level.partIds(bank, 4).every((id) => bank.items.find((i) => i.id === id).band === 'C1'),
    'the last part is the C1 band');

/* The count is the whole rule, so the edges of every cutoff are pinned. */
const cut = bank.blueprint.cutoffs;
const at = (n) => Level.levelFromCorrect(n, 50, cut) || 'Pre-A1';
[[0, 'Pre-A1'], [7, 'Pre-A1'], [8, 'A1'], [16, 'A1'], [17, 'A2'], [25, 'A2'],
 [26, 'B1'], [34, 'B1'], [35, 'B2'], [43, 'B2'], [44, 'C1'], [50, 'C1']]
  .forEach(([n, band]) => say(at(n) === band, `${n} of 50 is ${band} (got ${at(n)})`));

const perfect = sit(() => true);
say(perfect.result.right === 50, `a perfect paper scores 50 (got ${perfect.result.right})`);
say(perfect.result.paper === 55, `the paper is 55 questions with writing (got ${perfect.result.paper})`);
say(overall(perfect.result) === 'C1', `an advanced learner is placed at C1 (got ${overall(perfect.result)})`);
say(perfect.result.completion === 'complete', 'a full paper is reported as complete');
say(perfect.result.questions === 55,
    `all fifty answers and five written tasks are counted (got ${perfect.result.questions})`);
say(perfect.result.startedAt === undefined, 'the report carries no raw attempt state');

const hopeless = sit(() => false);
say(hopeless.result.right === 0, `an empty paper scores 0 (got ${hopeless.result.right})`);
say(overall(hopeless.result) === 'Pre-A1', `a beginner is placed at Pre-A1 (got ${overall(hopeless.result)})`);
say(hopeless.result.overall === 'Pre-A1',
    `a paper under the A1 cutoff does not name its band (got ${hopeless.result.overall})`);

const b1 = sit((item) => ['A1', 'A2', 'B1'].includes(item.band));
say(b1.result.right === 30, `a B1 learner is right thirty times (got ${b1.result.right})`);
say(overall(b1.result) === 'B1', `a B1 learner is placed at B1 (got ${overall(b1.result)})`);
say(b1.result.skills.listening.band === 'B1', 'each skill is read on its own count');
say(b1.result.skills.grammar.total === 15 && b1.result.skills.reading.total === 10,
    'grammar is out of fifteen and reading out of ten');

const part = sit(() => true, 0);
say(part.result.questions === 10, `a learner who stops early answered 10 (got ${part.result.questions})`);
say(part.result.right === 10, `only ten answers are credited (got ${part.result.right})`);
say(overall(part.result) === 'A1', `ten of fifty reads as A1, not as a perfect part (got ${overall(part.result)})`);
say(part.result.completion === 'partial', 'a half-finished paper is reported as partial');

say('writing' in perfect.result.skills, 'writing is one of the scored skills');
say(!('speaking' in perfect.result.skills), 'speaking is still absent from the scored skills');
say(perfect.result.skills.writing.total === 20,
    `writing is out of twenty rubric points (got ${perfect.result.skills.writing.total})`);
say(perfect.result.skills.writing.right === 20,
    `a model answer earns every point (got ${perfect.result.skills.writing.right})`);
say(perfect.result.skills.writing.band === 'C1',
    `a full-marks writer is placed at C1 in writing (got ${perfect.result.skills.writing.band})`);
say(perfect.result.skills.writing.scored === 'rubric',
    'the report can tell a rubric mark from a count');

/* The marker itself: an empty task scores nothing, a stub scores little, and
   the same text always earns the same points. */
const a1 = bank.items.find((i) => i.id === 'w-a1-1');
const empty = Level.markWriting(bank, a1, '');
const stub = Level.markWriting(bank, a1, 'i like cats');
say(empty.points === 0, `an empty task scores nothing (got ${empty.points})`);
say(stub.points <= 1, `a three-word answer cannot score (got ${stub.points})`);
say(Level.markWriting(bank, a1, MODEL.A1).points === 4, 'the A1 model answer earns four points');
say(JSON.stringify(Level.markWriting(bank, a1, MODEL.A1)) ===
    JSON.stringify(Level.markWriting(bank, a1, MODEL.A1)), 'the mark is deterministic');

/* Writing has to change the total, or assessing it is decoration. */
const noWriting = sit(() => true, 4);
say(noWriting.result.earned === 50 && noWriting.result.outOf === 55,
    `fifty right and nothing written is 50 of 55 (got ${noWriting.result.earned} of ${noWriting.result.outOf})`);
say(overall(noWriting.result) === 'C1', 'fifty right still reads as C1 with writing blank');

process.exit(problems ? 1 : 0);
"""


def main() -> int:
    doc = load()
    check_fresh()
    stats = check_content(doc) if doc else {}
    check_wiring()
    check_engine()

    if problems:
        for p in problems:
            print("FAIL  " + p)
        print(f"\n{len(problems)} problem(s) with the level assessment")
        return 1

    kinds = stats.get("kinds") or {}
    print(f"PASS  {stats.get('items')} items, {stats.get('session')} questions a session")
    print(f"      formats {dict(sorted(kinds.items()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
