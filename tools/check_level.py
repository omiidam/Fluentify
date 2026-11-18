#!/usr/bin/env python3
"""What the level assessment has to be true of, before anyone sits it.

  * the bank - every item carries the metadata the report needs, every band
    has a full block for every assessed skill, every Persian line is Persian;
  * the wiring - a tile, a panel, a route, a retake window, and the offline
    APK carrying the file;
  * the bank's provenance - every item carries a domain, a task type, a CEFR
    descriptor, an accessibility line, rights, a version and a review date,
    and the scenarios and documents it renders are data, never markup;
  * the engine - the module's own adaptive route and marking are run in node
    over synthetic learners: a perfect one, a hopeless one, one who is exactly
    B1, and one who stops after the first part. The paper has to climb only
    when the evidence supports it, a short route must not claim a band it did
    not test, and unanswered questions have to count as wrong.
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
    check(doc.get("version") == 3, "the bank is not the third-format bank")

    skills = doc.get("skills") or []
    assessed = [s["id"] for s in skills if s.get("assessed")]
    check(assessed == ["grammar", "vocabulary", "reading", "listening",
                       "interaction", "mediation", "writing"],
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
    check(bp.get("questions") == 65, f"the paper is {bp.get('questions')} questions")
    check(bp.get("core") == BANDS[:3] and bp.get("upper") == BANDS[3:],
          f"the adaptive route is {bp.get('core')} then {bp.get('upper')}")
    check(sum((bp.get("perBand") or {}).values()) == bp.get("perBandTotal"),
          "the per-band counts do not add up to a band")
    check(bp.get("perBandTotal") * len(BANDS) == bp.get("questions"),
          "thirteen questions a band does not make the paper")
    check((bp.get("perBand") or {}).get("interaction") == 1
          and (bp.get("perBand") or {}).get("mediation") == 1,
          f"the blueprint spends {bp.get('perBand')} on interaction and mediation")
    check(bp.get("objective") == [s for s in assessed if s != "writing"],
          f"the recognition questions are {bp.get('objective')}")
    check(bp.get("writingPoints") == 4, "a writing task is not worth four points")
    cut = bp.get("cutoffs") or []
    check(len(cut) == len(BANDS) and cut == sorted(cut) and all(0 < c < 1 for c in cut),
          f"the cutoffs are {cut}")
    # The cutoffs are shares, so the count a band needs is the first whole
    # question at or above it: 8.8 of 55 is nine right, 48.4 is forty-nine.
    check(math.ceil(cut[0] * 65) == 11 and math.ceil(cut[4] * 65) == 58,
          f"the first cutoff is {math.ceil(cut[0] * 65)} of 65, "
          f"the last {math.ceil(cut[4] * 65)}")
    content = doc.get("content") or {}
    check(bool(content.get("version")), "the bank has no content version")
    check(bool(content.get("owner")), "the bank has no review owner")
    check((content.get("reviewCycleDays") or 0) >= 90,
          "the review cycle is shorter than a quarter")
    check(bool(content.get("reviewLog")), "the bank has no review log")
    try:
        from datetime import date
        due = date.fromisoformat(str(content.get("nextReview")))
        check(due >= date.today(),
              f"the content package is overdue for review (due {due.isoformat()})")
        published = date.fromisoformat(str(content.get("published")))
        for entry in content.get("reviewLog") or []:
            check(bool(entry.get("on")) and bool(entry.get("what")),
                  "a review-log entry is missing its date or its reason")
            check(date.fromisoformat(str(entry["on"])) >= published - (due - due),
                  "a review-log entry predates the package")
        for it in doc.get("items") or []:
            check(date.fromisoformat(str(it.get("nextReview"))) >= date.today(),
                  f"{it.get('id')}: item review is overdue")
    except (ValueError, TypeError) as exc:
        check(False, f"the review dates do not parse: {exc}")

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
                      "ability", "prompt", "why", "weight", "source", "review",
                      "domain", "taskType", "descriptor", "accessibility",
                      "rights", "itemVersion", "status", "reviewedOn", "nextReview"):
            check(field in it, f"{where}: no {field}")
        check(it.get("status") in ("reviewed", "approved"), f"{where}: not approved")
        check(bool(it.get("rights")), f"{where}: no rights")
        check(bool(FA.search((it.get("descriptor") or {}).get("fa", ""))),
              f"{where}: the CEFR descriptor has no Persian")
        check(bool(FA.search((it.get("accessibility") or {}).get("fa", ""))),
              f"{where}: the accessibility note has no Persian")
        check(re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(it.get("reviewedOn", ""))) is not None,
              f"{where}: review date {it.get('reviewedOn')!r}")
        check(re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(it.get("nextReview", ""))) is not None,
              f"{where}: next review {it.get('nextReview')!r}")
        raw = json.dumps(it.get("stimulus"), ensure_ascii=False) if it.get("stimulus") else ""
        check("<script" not in raw.lower() and not re.search(r"\son\w+=", raw),
              f"{where}: the stimulus carries markup")
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

    check(len(items) >= 64, f"only {len(items)} items in the bank")
    domains = Counter(it.get("domain") for it in items)
    check(len(domains) >= 5, f"only {len(domains)} real-world domains")
    check(max(domains.values()) <= len(items) * 0.4,
          f"one domain holds {max(domains.values())} of {len(items)} items")
    check(sum(1 for it in items if it.get("scenario")) >= 8,
          "fewer than eight scenario items")
    check(sum(1 for it in items if it.get("stimulus")) >= 3,
          "fewer than three visual stimuli")
    prompts = Counter(it["prompt"]["en"].strip().lower() for it in items)
    check(not [p for p, n in prompts.items() if n > 1], "a prompt is repeated")
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
    check(by_band[("interaction", "C1")] == 1 and by_band[("mediation", "C1")] == 1,
          "the top band has no interaction or mediation item")
    for s_ in skills:
        if s_.get("assessed"):
            check(len(s_.get("canDo") or {}) == len(BANDS),
                  f"skill {s_['id']}: {len(s_.get('canDo') or {})} can-do lines")
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

    # The level check is the adult course's placement exam: a child's copy of
    # the app hides the tile and the panel, so the hook mounts the panel for
    # everyone else and deliberately does nothing for a kid.
    check('lvlpanel: () => Level.mount()' in src
          or 'lvlpanel: () => { if (!Experience.kids()) Level.mount(); }' in src,
          "opening the panel never mounts it")

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

/* A model answer per band, written to earn all four rubric points. */
const MODEL = {
  A1: 'My family is small and we are close. I live with my mother and my sister in a flat near the park. We cook dinner together on Friday and then we watch a movie.',
  A2: 'Last weekend I went to the park with my friend. We walked by the river and then we ate lunch outside. The weather was sunny and warm. I liked the afternoon because we talked for hours.',
  B1: 'The old bazaar is the best place to start because the building is beautiful. Then walk down to the river and take a boat for an hour. The food near the bridge is cheap and very good. Visit the museum if it rains, since it is indoors. Two days is enough for all of this.',
  B2: 'I think phones should be banned in classrooms. They distract students and they stop conversation between lessons. However, a phone is a useful tool for research when the teacher allows it. Most schools already have laptops, so the loss is small. A ban with clear exceptions is better than a total one, although it needs enforcing. Teachers should decide when a screen is allowed. That keeps the rule simple and it keeps the lesson moving.',
  C1: 'Remote work arguably harms young employees, although the effect is not uniform. Junior staff may miss the informal learning that happens in an office, and they might not build the networks that promotion depends on. However, to some extent this reflects poor management rather than remote work itself. Companies that invest in mentoring tend to keep their young staff, and those that do not lose them whether the desk is at home or in the building. The problem is solvable, but not by attendance alone. Training does more than proximity, and it can be measured.',
};

/* Sits the paper, answering `good(item)` correctly. The loop asks the engine
   for the next part each time, because the route grows as the answers come
   in - a fixed 0..4 loop would sit the old fixed paper. */
function sit(good, stopAfterPart) {
  const a = Level.blankAttempt();
  const seen = [];
  for (let p = 0; p < Level.partCount(bank, a); p++) {
    if (stopAfterPart != null && p > stopAfterPart) break;
    Level.partIds(bank, p, a).forEach((id) => {
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

/* ---- the bank and the route ------------------------------------------- */
const ids = Level.paper(bank);
say(ids.length === 60, `the objective bank is sixty questions (got ${ids.length})`);
say(new Set(ids).size === ids.length, 'no question appears twice');

const blank = Level.blankAttempt();
say(Level.route(bank, blank).join(',') === 'A1,A2,B1',
    `a blank paper starts on the core route (got ${Level.route(bank, blank)})`);
say(Level.partCount(bank, blank) === 3, `the core route is three parts (got ${Level.partCount(bank, blank)})`);
say(Level.partIds(bank, 0, blank).length === 12,
    `a band part is twelve questions (got ${Level.partIds(bank, 0, blank).length})`);
say(Level.partIds(bank, 0, blank).every((id) => bank.items.find((i) => i.id === id).band === 'A1'),
    'the first part is the A1 band');

/* A core answered perfectly has earned the climb; a B2 that is answered
   perfectly has earned the next one. */
const strong = Level.blankAttempt();
Level.partIds(bank, 0, strong).forEach((id) => strong.answers[id] = right(bank.items.find((i) => i.id === id)));
Level.partIds(bank, 1, strong).forEach((id) => strong.answers[id] = right(bank.items.find((i) => i.id === id)));
Level.partIds(bank, 2, strong).forEach((id) => strong.answers[id] = right(bank.items.find((i) => i.id === id)));
say(Level.route(bank, strong).join(',') === 'A1,A2,B1,B2',
    `a perfect core opens B2 only (got ${Level.route(bank, strong)})`);

const weakCore = Level.blankAttempt();
say(Level.route(bank, weakCore).join(',') === 'A1,A2,B1',
    'an unanswered core does not open the upper bands');

/* ---- the count still means what the report says ----------------------- */
const cut = bank.blueprint.cutoffs;
const at = (n) => Level.levelFromCorrect(n, 65, cut) || 'Pre-A1';
[[0, 'Pre-A1'], [10, 'Pre-A1'], [11, 'A1'], [22, 'A1'], [23, 'A2'], [33, 'A2'],
 [34, 'B1'], [45, 'B1'], [46, 'B2'], [57, 'B2'], [58, 'C1'], [60, 'C1']]
  .forEach(([n, band]) => say(at(n) === band, `${n} of 65 is ${band} (got ${at(n)})`));

/* ---- four learners ---------------------------------------------------- */
const perfect = sit(() => true);
say(perfect.result.right === 60, `a perfect paper scores 60 (got ${perfect.result.right})`);
say(perfect.result.paper === 65, `the full route is 65 questions with writing (got ${perfect.result.paper})`);
say(overall(perfect.result) === 'C1', `an advanced learner is placed at C1 (got ${overall(perfect.result)})`);
say(perfect.result.route === 'full', `an advanced learner sits the full route (got ${perfect.result.route})`);
say(perfect.result.completion === 'complete', 'a full paper is reported as complete');
say(perfect.result.questions === 65, `all sixty answers and five tasks are counted (got ${perfect.result.questions})`);

const hopeless = sit(() => false);
say(hopeless.result.right === 0, `an empty paper scores 0 (got ${hopeless.result.right})`);
say(overall(hopeless.result) === 'Pre-A1', `a beginner is placed at Pre-A1 (got ${overall(hopeless.result)})`);
say(hopeless.result.stoppedEarly === true, 'the paper stops climbing for a beginner');
say(hopeless.result.paper === 41, `the core route is 41 questions with writing (got ${hopeless.result.paper})`);
say(hopeless.result.asked === 36, `the core route asks 36 objective questions (got ${hopeless.result.asked})`);

const b1 = sit((item) => ['A1', 'A2', 'B1'].includes(item.band));
say(b1.result.right === 36, `a B1 learner is right thirty-six times (got ${b1.result.right})`);
say(overall(b1.result) === 'B1', `a B1 learner is placed at B1 (got ${overall(b1.result)})`);
say(b1.result.route === 'plus-B2', `B1 evidence opens B2 and stops (got ${b1.result.route})`);
say(b1.result.skills.listening.band === 'B1', 'each skill is read on its own count');
say(b1.result.skills.grammar.total === 15 && b1.result.skills.grammar.asked === 12,
    `grammar is out of fifteen with twelve asked across four bands (got ${b1.result.skills.grammar.asked})`);
say(b1.result.skills.interaction.total === 5 && b1.result.skills.mediation.total === 5,
    'interaction and mediation are read on their own five');

const part = sit(() => true, 0);
say(part.result.questions === 12, `a learner who stops early answered 12 (got ${part.result.questions})`);
say(part.result.right === 12, `only twelve answers are credited (got ${part.result.right})`);
say(overall(part.result) === 'A1', `twelve of 65 reads as A1, not as a perfect part (got ${overall(part.result)})`);
say(part.result.completion === 'partial', 'a half-finished paper is reported as partial');
say(part.result.stoppedEarly === true, 'a half-finished paper never claims an upper band');

/* A short route must not invent a band: the same core, marked perfect, is
   worth exactly 36 of 65 and cannot pass the B1 cutoff. */
const short = sit(() => true, 2);
say(overall(short.result) === 'B1',
    `a perfect A1-B1 core reads B1, not B2 (got ${overall(short.result)})`);
say(short.result.skills.grammar.band === 'B1',
    `a skill on a short route is capped too (got ${short.result.skills.grammar.band})`);

/* ---- writing ---------------------------------------------------------- */
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

const a1 = bank.items.find((i) => i.id === 'w-a1-1');
const empty = Level.markWriting(bank, a1, '');
const stub = Level.markWriting(bank, a1, 'i like cats');
say(empty.points === 0, `an empty task scores nothing (got ${empty.points})`);
say(stub.points <= 1, `a three-word answer cannot score (got ${stub.points})`);
say(Level.markWriting(bank, a1, MODEL.A1).points === 4, 'the A1 model answer earns four points');
say(JSON.stringify(Level.markWriting(bank, a1, MODEL.A1)) ===
    JSON.stringify(Level.markWriting(bank, a1, MODEL.A1)), 'the mark is deterministic');

const noWriting = sit(() => true, 4);
say(noWriting.result.earned === 60 && noWriting.result.outOf === 65,
    `sixty right and nothing written is 60 of 65 (got ${noWriting.result.earned} of ${noWriting.result.outOf})`);
say(overall(noWriting.result) === 'C1', 'sixty right still reads as C1 with writing blank');

say(perfect.result.startedAt === undefined, 'the report carries no raw attempt state');

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
