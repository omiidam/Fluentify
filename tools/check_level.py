#!/usr/bin/env python3
"""What the level assessment has to be true of, before anyone sits it.

  * the bank - every item carries the metadata the report needs, every band
    has a full block for every assessed skill, every Persian line is Persian;
  * the wiring - a tile, a panel, a route, a retake window, and the offline
    APK carrying the file;
  * the engine - the module's own staircase is run in node over synthetic
    learners: a perfect one, a hopeless one, one who is exactly B1, and one who
    should never see the same question twice. A placement test whose bands do
    not move is a quiz with a diagram.
"""

from __future__ import annotations

import json
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
    check(assessed == ["grammar", "vocabulary", "reading", "listening"],
          f"assessed skills are {assessed}")
    check([s["id"] for s in skills if not s.get("assessed")] == ["writing", "speaking"],
          "writing and speaking are not the practice-only skills")
    for s in skills:
        check(bool(FA.search(s.get("blurb", {}).get("fa", ""))),
              f"skill {s['id']}: the blurb has no Persian")

    bands = [b.get("id") for b in doc.get("bands") or []]
    check(bands == ["PRE"] + BANDS + ["C2"], f"bands are {bands}")
    check(doc.get("testedBands") == BANDS, "the tested bands are not A1 to C1")

    bp = doc.get("blueprint") or {}
    check(bp.get("blocks") == 3 and bp.get("perBlock") == 3,
          "the blueprint is not three blocks of three")
    check(bp.get("startBand") in BANDS, "the start band is not a tested band")
    check(bp.get("passRatio") == [2, 3], "a block is not decided at two thirds")

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

    check(len(items) >= 60, f"only {len(items)} items in the bank")
    check(len(kinds) >= 5, f"only {len(kinds)} question formats")
    check(kinds.get("mcq", 0) < len(items) * 0.65,
          "the bank is mostly multiple choice")
    for skill in assessed:
        for band in BANDS:
            n = by_band[(skill, band)]
            check(n == bp.get("perBlock"),
                  f"{skill}/{band}: {n} items, a block needs {bp.get('perBlock')}")
    check(by_skill["writing"] >= 2 and by_skill["speaking"] >= 2,
          "fewer than two productive tasks per practice skill")
    check(sum(by_skill[s] for s in bp.get("assessed", [])) >=
          bp.get("blocks", 3) * bp.get("perBlock", 3) * 4,
          "the bank cannot fill three rounds for four skills")

    passages = {p["id"]: p for p in doc.get("passages") or []}
    check(len(passages) >= 5, "fewer than five reading passages")
    for pid, p in passages.items():
        check(bool(FA.search(p["text"]["fa"])), f"passage {pid}: no Persian")
        words = len(p["text"]["en"].split())
        floor = 20 if p["band"] == "A1" else 60
        check(words >= floor, f"passage {pid}: {words} words, below {floor}")
        asked = sum(1 for it in items if it.get("passage") == pid)
        check(asked == 3, f"passage {pid}: {asked} questions, expected 3")
    for it in items:
        if it.get("passage"):
            check(it["passage"] in passages,
                  f"{it['id']}: points at a passage that is not there")

    check(len(set(keys)) >= 3, "the answer keys use fewer than three letters")
    if keys:
        check(Counter(keys).most_common(1)[0][1] <= len(keys) * 0.55,
              "one answer letter dominates the test")

    total_session = bp.get("blocks", 3) * bp.get("perBlock", 3) * len(assessed)
    check(total_session == 36, f"a full session is {total_session} questions")
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
        ("adjustBand(", "nothing moves the difficulty between blocks"),
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
    check("function planBlock(bank, attempt)" in module,
          "the engine no longer plans blocks")
    check("function adjustBand(bank, attempt)" in module,
          "the engine no longer adjusts the band")

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

/* A synthetic learner: `good(item)` decides each answer. This runs the real
   planBlock/adjustBand staircase, not a copy of it. */
function session(good) {
  const a = Level.blankAttempt(bank, null);
  const seen = [];
  for (let block = 0; block < bank.blueprint.blocks; block++) {
    Level.planBlock(bank, a);
    if (!a.current.length) break;
    a.current.forEach((id) => {
      const item = bank.items.find((i) => i.id === id);
      seen.push(id);
      a.answers[id] = good(item) ? right(item) : wrong(item);
      (a.asked[item.skill] = a.asked[item.skill] || []).push(id);
    });
    Level.adjustBand(bank, a);
  }
  a.finishedAt = a.startedAt + 12 * 60 * 1000;
  return {result: Level.compute(bank, a), seen, attempt: a};
}

let problems = 0;
const say = (ok, line) => { if (!ok) problems++; console.log(`${ok ? '  ok  ' : '  FAIL'}  ${line}`); };
const overall = (r) => r.overall || 'Pre-A1';

const perfect = session(() => true);
say(overall(perfect.result) === 'C1', `an advanced learner placed at C1 (got ${overall(perfect.result)})`);
say(perfect.result.skills.grammar.band === 'C1', 'advanced learner cleared grammar at C1');
say(perfect.result.questions === 36, `a full session asks 36 questions (asked ${perfect.result.questions})`);
say(new Set(perfect.seen).size === perfect.seen.length, 'no question is asked twice');

const hopeless = session(() => false);
say(overall(hopeless.result) === 'Pre-A1', `a beginner placed at Pre-A1 (got ${overall(hopeless.result)})`);

const b1 = session((item) => ['A1', 'A2', 'B1'].includes(item.band));
say(overall(b1.result) === 'B1', `a B1 learner placed at B1 (got ${overall(b1.result)})`);
say(b1.result.skills.listening.band === 'B1', 'each skill is placed on its own evidence');

const first = Level.blankAttempt(bank, null);
const opened = Level.planBlock(bank, first);
say(opened.length === 12, `round one is twelve questions (got ${opened.length})`);
say(opened.every((x) => bank.items.find((i) => i.id === x.id).band === bank.blueprint.startBand),
    'round one opens at the start band');

const twoSteps = Level.blankAttempt(bank, null);
Level.planBlock(bank, twoSteps);
twoSteps.current.forEach((id) => {
  const item = bank.items.find((i) => i.id === id);
  twoSteps.answers[id] = right(item);
  (twoSteps.asked[item.skill] = twoSteps.asked[item.skill] || []).push(id);
});
Level.adjustBand(bank, twoSteps);
say(Object.values(twoSteps.bands).every((b) => b === 'B2'),
    `a perfect block moves one band up (now ${Object.values(twoSteps.bands).join(',')})`);

const half = Level.blankAttempt(bank, null);
Level.planBlock(bank, half);
half.current.forEach((id) => {
  const item = bank.items.find((i) => i.id === id);
  half.answers[id] = wrong(item);
  (half.asked[item.skill] = half.asked[item.skill] || []).push(id);
});
Level.adjustBand(bank, half);
say(Object.values(half.bands).every((b) => b === 'A2'),
    `three misses move one band down (now ${Object.values(half.bands).join(',')})`);

const almost = Level.blankAttempt(bank, null);
Level.planBlock(bank, almost);
almost.current.forEach((id, k) => {
  const item = bank.items.find((i) => i.id === id);
  almost.answers[id] = k % 3 === 0 ? right(item) : wrong(item);
  (almost.asked[item.skill] = almost.asked[item.skill] || []).push(id);
});
Level.adjustBand(bank, almost);
say(Object.values(almost.bands).every((b) => b === 'A2'),
    'one of three right still moves down, not up');

// The four assessed skills only: writing and speaking cannot reach a band.
say(!('writing' in perfect.result.skills) && !('speaking' in perfect.result.skills),
    'writing and speaking are absent from the scored skills');
say(perfect.result.practice.writing.total === 2, 'writing tasks are counted as practice');

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
