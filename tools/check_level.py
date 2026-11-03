#!/usr/bin/env python3
"""What the level check has to be true of, before anyone sits it.

Three things are checked:

  * the bank itself - every band reachable, every key inside its options,
    every Persian line actually Persian, a reading question that belongs to a
    passage that exists;
  * the wiring - a tile, a panel, a route, a retake window, and the offline
    APK carrying the file;
  * the marking - the module's own score() is run in node over synthetic
    attempts, because a placement test that quietly rounds every band up to
    the top is worse than no test at all.
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
BUILDERS = ROOT / "build_apk_ui.py"
CACHE = Path("/tmp/fluentify-level-check")
BANDS = ["A1", "A2", "B1", "B2", "C1"]
FA = re.compile(r"[\u0600-\u06FF]")

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
    check(isinstance(doc.get("minutes"), int) and 5 <= doc["minutes"] <= 60,
          "the stated duration is not believable")

    bands = [b.get("id") for b in doc.get("bands") or []]
    check(bands == BANDS, f"bands are {bands}, expected {BANDS}")
    for band in doc.get("bands") or []:
        check(bool(FA.search(band.get("can", {}).get("fa", ""))),
              f"{band.get('id')}: the can-do line has no Persian")

    sections = doc.get("sections") or []
    check([s.get("id") for s in sections] ==
          ["use", "reading", "listening", "writing", "speaking"],
          "the five skills are not the five sections")

    total = 0
    keys: list[int] = []
    per_band: Counter[str] = Counter()
    per_skill: dict[str, set[str]] = {}

    for sec in sections:
        sid = sec.get("id")
        items = sec.get("items") or []
        total += len(items)
        per_skill[sid] = {it.get("band") for it in items}

        if sid == "reading":
            passages = {p.get("id"): p for p in sec.get("passages") or []}
            check(len(passages) >= 3, "reading has fewer than three passages")
            for pid, p in passages.items():
                words = len((p.get("text", {}).get("en") or "").split())
                # A1 reading is a handful of sentences by design; every other
                # band needs a passage long enough to have structure.
                floor = 20 if p.get("band") == "A1" else 60
                check(words >= floor,
                      f"reading/{pid}: only {words} words of English, "
                      f"below the {floor} this band needs")
                check(bool(FA.search(p.get("text", {}).get("fa", ""))),
                      f"reading/{pid}: no Persian translation")
                asked = sum(1 for it in items if it.get("passage") == pid)
                check(asked >= 3, f"reading/{pid}: only {asked} questions")

        for i, it in enumerate(items):
            where = f"{sid}[{i}]"
            check(it.get("band") in BANDS, f"{where}: band {it.get('band')}")
            per_band[it.get("band")] += 1
            for field in ("stem", "prompt"):
                if field in it:
                    check(bool(FA.search(it[field].get("fa", ""))),
                          f"{where}: {field} has no Persian")

            if sid == "listening":
                check(len((it.get("say") or "").split()) >= 6,
                      f"{where}: spoken text is too short to test")

            if sid in ("writing", "speaking"):
                rub = it.get("rubric") or []
                check([r.get("points") for r in rub] == [1, 2, 3, 4],
                      f"{where}: the rubric does not run 1 to 4")
                for r in rub:
                    check(bool(FA.search(r.get("text", {}).get("fa", ""))),
                          f"{where}: rubric {r.get('points')} has no Persian")
                continue

            opts = it.get("options") or []
            check(len(opts) == 4, f"{where}: {len(opts)} options")
            check(len(set(opts)) == len(opts), f"{where}: two identical options")
            if 0 <= (it.get("answer") if isinstance(it.get("answer"), int) else -1) < 4:
                keys.append(it["answer"])
            else:
                problems.append(f"{where}: answer key is not one of the options")
            check(bool(FA.search(it.get("why", {}).get("fa", ""))),
                  f"{where}: the explanation has no Persian")
            if sid == "reading":
                ids = {p.get("id") for p in sec.get("passages") or []}
                check(it.get("passage") in ids,
                      f"{where}: points at a passage that is not there")

    check(total >= 40, f"only {total} questions in the bank")
    for band in BANDS:
        check(per_band[band] >= 3, f"band {band} has {per_band[band]} questions")
    for sid in ("use", "reading", "listening"):
        missing = [b for b in BANDS if b not in (per_skill.get(sid) or set())]
        check(not missing, f"{sid} has no {', '.join(missing)} item, so its top "
                           "band is unreachable")
    check(len(set(keys)) >= 3,
          f"the answer keys use only {len(set(keys))} letters of four")
    if keys:
        top = Counter(keys).most_common(1)[0][1]
        check(top <= len(keys) * 0.6, "one answer letter dominates the test")

    return {"total": total, "scored": len(keys), "per_band": per_band}


def check_wiring() -> None:
    src = WEBAPP.read_text(encoding="utf-8")
    for needle, what in (
        ('id="lvltoggle"', "the header has no Level tile"),
        ('id="lvlpanel"', "there is no level panel"),
        ('id="lvlbody"', "the level panel has nowhere to draw"),
        ('lvlpanel: \'lvltoggle\'', "the panel is not registered with the tiles"),
        ("lvlpanel: () => Level.mount()", "opening the panel never mounts it"),
        ("document.getElementById('lvltoggle').onclick", "the tile is not wired"),
        ('self.path.startswith("/api/level_test")', "the web build has no route"),
        ("Level.paintBadge();", "the tile badge is never painted from a stored result"),
        ("openLevel(level)", "the report cannot filter the story shelf"),
        ('#lvlpanel.open', "the panel never becomes visible"),
        ("fluentify.level.result", "nothing is stored under the result key"),
        ("fluentify.level.draft", "a half-finished check has nowhere to live"),
    ):
        check(needle in src, what)

    check("level_test.json" in BUILDERS.read_text(encoding="utf-8"),
          "the offline build does not ship the question bank")
    data = ROOT / "android/app/src/main/assets/www/data/level_test.json"
    check(data.exists(), "the built APK data folder has no level_test.json")

    # The retake window has to be one number, used by the panel, not a literal
    # repeated in three places.
    check(src.count("doc.retakeDays") >= 3,
          "the retake window is hard-coded instead of read from the bank")


def check_marking() -> None:
    if not shutil.which("node"):
        print("SKIP  node is not installed - the marking was not exercised")
        return

    src = WEBAPP.read_text(encoding="utf-8")
    start = src.index("const Level = (() => {")
    end = src.index("\n})();", start) + len("\n})();")
    module = src[start:end]
    check("compute(snapshot, bank)" in module,
          "compute() no longer takes a snapshot and a bank")

    CACHE.mkdir(parents=True, exist_ok=True)
    script = CACHE / "level_check.js"
    script.write_text(HARNESS.replace("__MODULE__", module), encoding="utf-8")

    proc = subprocess.run(["node", str(script), str(DOC)],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        problems.append("the marking harness failed:\n" + (proc.stdout + proc.stderr).strip())
        return
    print(proc.stdout.strip())


HARNESS = r"""
const fs = require('fs');
const bank = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
__MODULE__

const IDS = ['A1', 'A2', 'B1', 'B2', 'C1'];

/* An attempt: answers for every objective item, and rubric picks for the two
   rated sections. `right(band)` decides whether an item of that band is
   answered correctly. */
function attempt(rightBand, points) {
  const answers = {}, self = {};
  bank.sections.forEach((sec) => {
    sec.items.forEach((it, i) => {
      const key = sec.id + ':' + i;
      if ('options' in it) answers[key] = rightBand(it, sec, i) ? it.answer : (it.answer + 1) % 4;
      else if (points) self[key] = points(sec, i);
    });
  });
  return {answers, self};
}

const cases = [
  ['everything right, rubric 3',
   attempt(() => true, () => 3), 'C1', {use: 'C1', reading: 'C1', listening: 'C1'}],
  ['nothing right, no rubric',
   attempt(() => false, null), null, {use: null, reading: null, listening: null}],
  ['A1 only, rubric 1',
   attempt((it) => it.band === 'A1', () => 1), 'A1', {use: 'A1', writing: 'A1'}],
  ['A1 and A2 right, B1 wrong',
   attempt((it) => ['A1', 'A2'].includes(it.band), null), 'A2', {use: 'A2', listening: 'A2'}],
  ['two of three in A1 still passes',
   attempt((it, sec, i) => it.band === 'A1' && i < 2, null), 'A1',
   {use: 'A1', reading: 'A1', listening: 'A1'}],
  ['one of three in A1 is not enough',
   attempt((it) => false, null), null, {use: null}],
  ['C1 objective, no rubric at all',
   attempt(() => true, null), 'C1', {writing: null, speaking: null}],
  ['strong objective, weak rubric is still the median',
   attempt(() => true, () => 2), 'C1', {writing: 'A2', use: 'C1'}],
];

let problems = 0;
console.log(`marking: ${cases.length} attempts`);
for (const [name, snap, overall, expect] of cases) {
  const got = Level.compute(snap, bank);
  const label = got.overall || 'Pre-A1';
  if (label !== (overall || 'Pre-A1')) {
    console.log(`  FAIL  ${name}: expected ${overall || 'Pre-A1'}, got ${label}`);
    problems++;
    continue;
  }
  let bad = 0;
  for (const [skill, want] of Object.entries(expect)) {
    const have = got.skills[skill] || null;
    if (want === null && have !== null) bad++;
    if (want !== null && have !== want) bad++;
  }
  if (bad) {
    console.log(`  FAIL  ${name}: skill levels ${JSON.stringify(got.skills)}`);
    problems++;
  } else {
    console.log(`  ok    ${name} -> ${label}`);
  }
}
process.exit(problems ? 1 : 0);
"""


def main() -> int:
    doc = load()
    check_fresh()
    if doc:
        stats = check_content(doc)
    else:
        stats = {}
    check_wiring()
    check_marking()

    if problems:
        for p in problems:
            print("FAIL  " + p)
        print(f"\n{len(problems)} problem(s) with the level check")
        return 1

    bands = " ".join(f"{b}:{stats['per_band'][b]}" for b in BANDS)
    print(f"PASS  {stats['total']} questions, {stats['scored']} marked, five skills")
    print(f"      bands {bands}; retake window 30 days")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
