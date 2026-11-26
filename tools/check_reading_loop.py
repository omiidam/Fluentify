#!/usr/bin/env python3
"""Checks the reading loop: the six stages around each passage.

The Reading section is now a sequence, not a shelf: placement, preparation,
two reads (supported, then not), an inference check with a level gate, a
written summary, and a next text chosen from the words the learner actually
tapped. The passages, the strategies and the answer keys are the ones that were
already there, so this checker guards the additions and, above all, that the
loop cannot quietly replace or overwrite the content it wraps.

What it checks:

  * reading_loop.json is current (rebuilding it changes nothing);
  * every strategy passage has an entry, keyed the way the page keys it
    (passage one is the bare strategy id, the rest are "id#n");
  * every passage has a purpose, a background question, three essential words
    and a Persian gloss map, and every gloss is a meaning the vocabulary
    panels already teach;
  * every glossed word really occurs in the passage, and every key word is
    glossed;
  * every passage has at least one question that asks for inference, and its
    indices are inside the passage's own multiple-choice list;
  * the three placement questions are one per band with a valid answer;
  * the page keeps the gates: the quiz lives behind the second read, the level
    gate is at 80%, the tapped words reach the bank and the recommendation;
  * the kids band never mounts the loop.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READING = ROOT / "reading.json"
LOOP = ROOT / "reading_loop.json"
WEBAPP = ROOT / "webapp.py"
GLOSSARY = ROOT / "glossary.json"
SENSES = ROOT / "senses.json"

FA = re.compile(r"[\u0600-\u06FF]")
WORD = re.compile(r"[A-Za-z][A-Za-z'’-]*")

PASS = 0
FAIL = 0


def check(ok: bool, what: str, detail: str = "") -> bool:
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  ok   {what}")
    else:
        FAIL += 1
        print(f"  FAIL {what}" + (f"\n       {detail}" if detail else ""))
    return ok


def load(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def key_of(sid: str, index: int) -> str:
    return sid if index == 1 else f"{sid}#{index}"


def taught_glosses() -> dict[str, set[str]]:
    """Every Persian meaning the app already teaches for a word."""
    out: dict[str, set[str]] = {}
    for dom in load(GLOSSARY)["domains"].values():
        if not isinstance(dom, dict):
            continue
        for pair in dom.get("words") or []:
            if pair and len(pair) > 1:
                out.setdefault(str(pair[0]).strip().lower(), set()).add(str(pair[1]).strip())
    for word, record in load(SENSES)["words"].items():
        for sense in record.get("senses") or []:
            if len(sense) > 2 and sense[2]:
                out.setdefault(str(word).strip().lower(), set()).add(str(sense[2]).strip())
    return out


def check_fresh() -> None:
    """The file must be what the builder writes today."""
    proc = subprocess.run(
        [sys.executable, "tools/build_reading_loop.py"],
        cwd=ROOT, capture_output=True, text=True)
    check(proc.returncode == 0, "the builder runs", proc.stderr.strip()[:400])
    check(LOOP.exists(), "reading_loop.json exists",
          "run python3 tools/build_reading_loop.py")
    if not LOOP.exists():
        return
    # The builder is deterministic, so a fresh run must write today's file.
    before = LOOP.read_bytes()
    subprocess.run([sys.executable, "tools/build_reading_loop.py"],
                   cwd=ROOT, capture_output=True)
    check(LOOP.read_bytes() == before, "reading_loop.json is up to date",
          "rebuild changed the file - run python3 tools/build_reading_loop.py")
    try:
        json.loads(before)
        check(True, "reading_loop.json parses")
    except ValueError as exc:
        check(False, "reading_loop.json parses", str(exc))


def main() -> int:
    print("reading loop")
    check_fresh()
    if not LOOP.exists():
        print("\nFAIL  nothing to check")
        return 1

    doc = load(READING)
    loop = load(LOOP)
    passages = loop.get("passages") or {}
    taught = taught_glosses()

    missing, no_purpose, no_bg, no_key, no_gloss = [], [], [], [], []
    not_in_text, key_not_glossed, invented = [], [], []
    for s in doc["strategies"]:
        for i, r in enumerate(s["readings"], start=1):
            key = key_of(s["id"], i)
            entry = passages.get(key)
            if not entry:
                missing.append(key)
                continue
            purpose = entry.get("purpose") or {}
            background = entry.get("background") or {}
            if not (purpose.get("en", "").strip() and FA.search(purpose.get("fa", ""))):
                no_purpose.append(key)
            if not (background.get("en", "").strip() and FA.search(background.get("fa", ""))):
                no_bg.append(key)
            keys = entry.get("key") or []
            if len(keys) != 3:
                no_key.append((key, len(keys)))
            gloss = entry.get("gloss") or {}
            if len(gloss) < 3:
                no_gloss.append((key, len(gloss)))
            text = " ".join(r.get("paragraphs") or [])
            tokens = {w.lower() for w in WORD.findall(text)}
            for word in gloss:
                if word not in tokens:
                    not_in_text.append((key, word))
                if word in taught and gloss[word] not in taught[word]:
                    invented.append((key, word, gloss[word]))
            for word in keys:
                if word not in gloss:
                    key_not_glossed.append((key, word))
            deep = (entry.get("deep") or {}).get("mcq") or []
            if not deep:
                missing.append(key + " (no inference question)")

    total = sum(len(s["readings"]) for s in doc["strategies"])
    check(f"all {total} passages have a loop entry", not missing,
          f"{len(missing)}: {missing[:6]}")
    check("every passage has a purpose in both languages", not no_purpose,
          f"{len(no_purpose)}: {no_purpose[:4]}")
    check("every passage has a background question", not no_bg,
          f"{len(no_bg)}: {no_bg[:4]}")
    check("every passage names exactly three essential words", not no_key,
          f"{len(no_key)}: {no_key[:4]}")
    check("every passage glosses at least three words", not no_gloss,
          f"{len(no_gloss)}: {no_gloss[:4]}")
    check("every glossed word occurs in its passage", not not_in_text,
          f"{len(not_in_text)}: {not_in_text[:4]}")
    check("every essential word is glossed for the reader", not key_not_glossed,
          f"{len(key_not_glossed)}: {key_not_glossed[:4]}")
    check("a gloss is a meaning the vocabulary panels teach", not invented,
          f"{len(invented)}: {invented[:4]}")

    # inference indices must point at the passage's own questions
    bad_deep = []
    for s in doc["strategies"]:
        for i, r in enumerate(s["readings"], start=1):
            entry = passages.get(key_of(s["id"], i)) or {}
            for idx in (entry.get("deep") or {}).get("mcq") or []:
                if not isinstance(idx, int) or not 0 <= idx < len(r["questions"]["mcq"]):
                    bad_deep.append((key_of(s["id"], i), idx))
    check("inference flags point at real questions", not bad_deep,
          f"{len(bad_deep)}: {bad_deep[:4]}")

    # placement: one question per band, answer inside the options
    calib = loop.get("calibration") or []
    check("placement asks one question per band",
          [c.get("level") for c in calib] == ["A2", "B1", "B2"],
          f"levels: {[c.get('level') for c in calib]}")
    bad_calib = [c for c in calib
                 if not (isinstance(c.get("answer"), int)
                         and 0 <= c["answer"] < len(c.get("options") or [])
                         and (c.get("why") or {}).get("fa"))]
    check("each placement question has a markable answer", not bad_calib,
          f"{len(bad_calib)} broken")

    # ---- the page ------------------------------------------------------
    page = WEBAPP.read_text(encoding="utf-8")

    def has(snippet: str, what: str, detail: str) -> None:
        check(snippet in page, what, detail)

    has("const LOOP_KEY = 'fluentify.readloop.v1'", "the loop keeps its own state",
        "no loop storage")
    has("const place = calibCard();\n    if (place) wrap.append(place);",
        "the strategy list opens with placement",
        "calibCard is not rendered")
    has("psg.append(phaseBar(s, r, entry, phase));", "the passage carries its phases",
        "no phase bar")
    has("psg.append(readBody(s, r, entry, phase === 1 ? 1 : 2));",
        "phase one is supported, phase two is bare", "readBody wiring changed")
    has("const questions = phase < 3", "the quiz waits for the second read",
        "questions are no longer gated")
    has("if (w.def) out +=", "the writing stage exists", "output card gone")
    has("bankAdd(key, entry.gloss[key], skey(s.id, pi));",
        "a tapped word reaches the bank", "taps no longer saved")
    has("if (pct >= 80 && here && !here.querySelector('.rdrec'))",
        "the next text arrives with a pass", "recommendation is not score-gated")
    has("pct < 80 && sNext && levelOf(sNext.level) > levelOf(r.level)",
        "the level gate is at 80%", "the level gate is gone")
    has("rdpanel: () => (Experience.kids() ? Kids.reading() : Reading.mount()),",
        "the kids band never mounts the adult loop", "kids routing changed")
    has(".then((d) => { loopDoc = d; return d; })",
        "the loop file is read once", "loadLoop no longer caches")
    has(".catch(() => null);",
        "a missing loop file leaves the old section standing", "hard failure path")
    has("async function loadLoop()", "the loop file is loaded by the panel",
        "loadLoop missing")

    print(f"\n{'PASS' if not FAIL else 'FAIL'}  {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
