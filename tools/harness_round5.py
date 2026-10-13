#!/usr/bin/env python3
"""Harness round 5 — data integrity and adversarial input.

Rounds 1-3 added knowledge, round 4 measured accuracy. Round 5 checks the
things that make a tutor feel broken regardless of how good the English is:

  1. Empty answer strings. 'articles' had ["", "no article", "zero"], so
     revealing the answer printed "Answer:  / no article / zero" and a
     learner told to answer "no article" saw a stray blank option.
  2. Malformed rows anywhere in the content files.
  3. Adversarial input — long strings, injection attempts, regex bait, mixed
     scripts, emoji — must never crash or hang the bot.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from chatbot import ChatBot, plain  # noqa: E402

GRAMMAR = json.loads((ROOT / "grammar.json").read_text(encoding="utf-8"))["topics"]
GLOSSARY = json.loads((ROOT / "glossary.json").read_text(encoding="utf-8"))["domains"]
PHRASES = json.loads((ROOT / "phrases.json").read_text(encoding="utf-8"))["topics"]
LISTENING = json.loads((ROOT / "listening.json").read_text(encoding="utf-8"))["levels"]
IDIOMS = json.loads((ROOT / "idioms.json").read_text(encoding="utf-8"))["topics"]
DISTINCTIONS = json.loads(
    (ROOT / "distinctions.json").read_text(encoding="utf-8"))["topics"]

ADVERSARIAL = [
    ("x" * 5000, "very long latin"),
    ("سلام " * 500, "very long persian"),
    ("a" * 200 + " " + "b" * 200, "two long tokens"),
    (".*+?^$[]{}()|\\", "regex metacharacters as a word"),
    ("translate .*", "regex as a lookup target"),
    ("<?php echo 1; ?>", "code injection"),
    ("<script>alert(1)</script>", "script tag"),
    ("'; DROP TABLE words; --", "sql injection"),
    ("__import__('os').system('ls')", "python injection"),
    ("translate ../../etc/passwd", "path traversal"),
    ("🙂🙃😀🎉", "emoji only"),
    ("translate 🙂", "emoji as a lookup target"),
    ("apple 🙂🙃", "word plus emoji"),
    ("A" * 100 + " translate apple", "long prefix then a real query"),
    ("translate apple " + "!" * 500, "punctuation flood"),
    ("Simple Present SIMPLE PRESENT simple present", "keyword repeated"),
    ("difference between a and a", "same word on both sides"),
    ("how do you say " + "x" * 200, "long pronounce target"),
    ("is this correct: " + "bad " * 200, "long broken sentence"),
    ("'\"\\/", "lone punctuation"),
    ("translate\ttab\tseparated", "tabs"),
    ("define nbsp", "non-breaking space"),
    ("\n\n\n\n", "newlines only"),
    ("‮mirrored", "bidi override"),
    ("0" * 300, "many zeros"),
    ("1/0", "division by zero"),
    ("{}[]()<>", "brackets only"),
    ("translate 👨‍👩‍👧‍👦", "zwj emoji"),
]

FAILURES: list[str] = []


def fail(msg: str) -> None:
    FAILURES.append(msg)


def check_integrity() -> int:
    """Every answer must be a non-empty string the learner could actually type."""
    checks = 0
    for tid, topic in GRAMMAR.items():
        for stage in ("practice", "exam"):
            for i, q in enumerate(topic.get(stage, [])):
                checks += 1
                answers = q.get("a") or []
                empties = [a for a in answers if not str(a).strip()]
                if empties:
                    fail(f"{tid}/{stage}[{i}] has an empty answer slot: {answers!r}")
                if not answers:
                    fail(f"{tid}/{stage}[{i}] has no answer at all")
                # a blank option is what a learner sees after 'show answer'
                if answers and any(str(a).startswith(" ") for a in answers):
                    fail(f"{tid}/{stage}[{i}] has an answer with a stray space: {answers!r}")
        # every lesson must be walkable end to end
        for stage in ("practice", "exam"):
            if not topic.get(stage):
                fail(f"{tid} has no {stage} questions")
    return checks


def check_content() -> int:
    checks = 0
    for topic in DISTINCTIONS:
        checks += 1
        if not topic.get("why"):
            fail(f"distinction {topic['id']} has no explanation")
        if not topic.get("sides"):
            fail(f"distinction {topic['id']} has no examples")
        for side in topic.get("sides", []):
            if not side.get("en") or not side.get("fa"):
                fail(f"distinction {topic['id']} has an untranslated side: {side!r}")
            if side.get("en", "").count("**") % 2:
                fail(f"distinction {topic['id']} has unbalanced bold markers: {side!r}")
    for topic in IDIOMS:
        for row in topic.get("idioms", []):
            checks += 1
            for key in ("en", "fa", "meaning", "example"):
                if not row.get(key):
                    fail(f"idiom {row.get('en')!r} has no {key}")
    for lv in LISTENING:
        for i, s in enumerate(lv.get("sentences", [])):
            checks += 1
            if not s.get("en") or not s.get("fa"):
                fail(f"listening {lv['id']}[{i}] is untranslated")
    for did, dom in GLOSSARY.items():
        if did == "_groups":
            continue
        for w in dom["words"]:
            checks += 1
            if len(w) < 2 or not str(w[0]).strip() or not str(w[1]).strip():
                fail(f"glossary {did} has a malformed row: {w!r}")
    for tid, topic in PHRASES.items():
        for line in topic.get("phrases", []):
            checks += 1
            if not line.get("en") or not line.get("fa"):
                fail(f"phrases {tid} has an untranslated line: {line!r}")
    return checks


def check_adversarial() -> int:
    bot = ChatBot()
    for text, label in ADVERSARIAL:
        try:
            reply = bot.respond(text)
        except Exception as exc:  # noqa: BLE001
            fail(f"adversarial {label}: CRASH {type(exc).__name__}: {exc}")
            continue
        if not reply or not str(reply).strip():
            fail(f"adversarial {label}: empty reply")
            continue
        r = plain(reply)
        if "Traceback" in r:
            fail(f"adversarial {label}: traceback leaked")
        if "None" in r or "{'" in r:
            fail(f"adversarial {label}: python repr leaked")
        # the reply must stay a sane length, not echo a megabyte back
        if len(r) > 20000:
            fail(f"adversarial {label}: reply is {len(r)} chars")
    return len(ADVERSARIAL)


def main() -> int:
    integrity = check_integrity()
    content = check_content()
    adversarial = check_adversarial()
    total = integrity + content + adversarial
    if FAILURES:
        print(f"FAIL  {len(FAILURES)} of {total} checks\n")
        for msg in FAILURES[:40]:
            print(f"  {msg}")
        if len(FAILURES) > 40:
            print(f"  ... and {len(FAILURES) - 40} more")
        return 1
    print(f"PASS  all {total} checks "
          f"({integrity} answers, {content} rows, {adversarial} adversarial)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())