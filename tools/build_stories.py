#!/usr/bin/env python3
"""Build stories.json for the Mini stories panel.

The English texts are the graded retellings published by Nathan Schaumann
(github.com/nathanschaumann/graded-readers, CC BY 4.0); the Persian beside
each line, the vocabulary, the grammar notes and every question are written
here. This script checks each story before writing, so a half-finished story
can never reach the page.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from mini_stories import LEVELS, STORIES, CREDIT

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "stories.json"


class BuildError(Exception):
    pass


def bad(where: str, why: str) -> None:
    raise BuildError(f"build_stories: {where}: {why}")


def words(text: str) -> int:
    return len(re.findall(r"[A-Za-z'’\-]+", text))


def need(cond: bool, where: str, why: str) -> None:
    if not cond:
        bad(where, why)


def has_persian(text: str) -> bool:
    return bool(re.search(r"[\u0600-\u06FF]", text or ""))


def check_bilingual(where: str, part: dict, field: str = "") -> None:
    tag = f"{where} {field}".strip()
    need(isinstance(part, dict), tag, "is not a bilingual pair")
    need(bool(str(part.get("en", "")).strip()), tag, "has no English")
    need(has_persian(part.get("fa", "")), tag, "has no Persian")


def build_story(s: dict, seen: set[str]) -> dict:
    sid = s.get("id", "")
    need(bool(sid) and sid not in seen, "story", f"duplicate or missing id {sid!r}")
    seen.add(sid)
    where = sid

    check_bilingual(where, s.get("title"), "title")
    level = s.get("level")
    need(level in {lv["id"] for lv in LEVELS}, where, f"unknown level {level!r}")
    check_bilingual(where, s.get("blurb"), "blurb")

    chapters = s.get("chapters") or []
    need(len(chapters) >= 1, where, "has no chapters")
    total_words = 0
    sentences = 0
    for ci, ch in enumerate(chapters, 1):
        cw = f"{where} chapter {ci}"
        check_bilingual(cw, ch.get("title"), "title")
        pairs = ch.get("pairs") or []
        need(len(pairs) >= 3, cw, "has fewer than three sentences")
        for pi, pair in enumerate(pairs, 1):
            check_bilingual(cw, pair, f"sentence {pi}")
            sentence = pair["en"].strip()
            need(bool(sentence) and sentence[-1] in ".!?\"'", cw,
                 f"sentence {pi} has no closing punctuation")
            need(len(sentence.split()) <= 30, cw,
                 f"sentence {pi} is {len(sentence.split())} words long")
            total_words += words(sentence)
        sentences += len(pairs)
    plain = " ".join(p["en"] for ch in chapters for p in ch["pairs"])

    vocab = s.get("vocab") or []
    need(len(vocab) >= 6, where, f"{len(vocab)} vocabulary items, want 6 or more")
    for item in vocab:
        vw = f"{where} vocab {item.get('word')!r}"
        need(bool(item.get("word")), vw, "has no word")
        need(item["word"].lower() in plain.lower(), vw,
             "the word never appears in the story")
        need(item.get("pos") in ("n.", "v.", "adj.", "adv.", "phr."), vw,
             "has no part of speech")
        check_bilingual(vw, item.get("meaning"), "meaning")
        need(bool(item.get("example")), vw, "has no example")
        need(has_persian(item.get("exampleFa", "")), vw, "example has no Persian")

    expressions = s.get("expressions") or []
    need(len(expressions) >= 4, where,
         f"{len(expressions)} expressions, want 4 or more")
    for item in expressions:
        ew = f"{where} expression {item.get('phrase')!r}"
        need(bool(item.get("phrase")), ew, "has no phrase")
        check_bilingual(ew, item.get("meaning"), "meaning")
        need(bool(item.get("example")), ew, "has no example")
        need(has_persian(item.get("exampleFa", "")), ew, "example has no Persian")

    grammar = s.get("grammar") or []
    need(len(grammar) >= 3, where, f"{len(grammar)} grammar points, want 3 or more")
    for item in grammar:
        gw = f"{where} grammar {item.get('name', {}).get('en')!r}"
        check_bilingual(gw, item.get("name"), "name")
        need(bool(item.get("example")), gw, "has no example")
        check_bilingual(gw, item.get("note"), "note")

    q = s.get("questions") or {}
    for kind_q, least in (("mcq", 5), ("truefalse", 3), ("blanks", 3), ("open", 2)):
        need(len(q.get(kind_q) or []) >= least, where,
             f"{len(q.get(kind_q) or [])} {kind_q}, want {least}")

    for n, item in enumerate(q["mcq"], 1):
        mw = f"{where} mcq {n}"
        check_bilingual(mw, item.get("q"), "question")
        opts = item.get("options") or []
        need(len(opts) == 4, mw, f"has {len(opts)} options")
        need(len({o.strip().lower() for o in opts}) == 4, mw, "repeats an option")
        need(isinstance(item.get("answer"), int) and 0 <= item["answer"] < 4,
             mw, "key points outside the options")
        check_bilingual(mw, item.get("why"), "explanation")

    for n, item in enumerate(q["truefalse"], 1):
        tw = f"{where} truefalse {n}"
        check_bilingual(tw, item.get("q"), "statement")
        need(isinstance(item.get("answer"), bool), tw, "answer is not a boolean")
        check_bilingual(tw, item.get("why"), "explanation")

    for n, item in enumerate(q["blanks"], 1):
        bw = f"{where} blank {n}"
        need("___" in item.get("sentence", ""), bw, "has no gap")
        need(item.get("answer", "").lower() in plain.lower(), bw,
             f"the answer {item.get('answer')!r} is not in the text")
        check_bilingual(bw, item.get("hint"), "hint")

    for n, item in enumerate(q["open"], 1):
        ow = f"{where} open {n}"
        check_bilingual(ow, item.get("q"), "question")
        check_bilingual(ow, item.get("model"), "model answer")
        check_bilingual(ow, item.get("tip"), "tip")

    mcq_keys = [i["answer"] for i in q["mcq"]]
    tf_keys = [i["answer"] for i in q["truefalse"]]
    need(len(set(mcq_keys)) >= 3, where,
         "the choice keys sit on fewer than three letters")
    need(tf_keys.count(True) >= 1 and tf_keys.count(False) >= 1, where,
         "true/false never varies")

    minutes = max(1, round(total_words / 170))
    counts = {k: len(q[k]) for k in ("mcq", "truefalse", "blanks", "open")}
    counts["all"] = sum(counts.values())

    story = {
        "id": sid,
        "title": s["title"],
        "level": level,
        "blurb": s["blurb"],
        "words": total_words,
        "minutes": minutes,
        "sentences": sentences,
        "chapters": chapters,
        "text": plain,
        "vocab": vocab,
        "expressions": expressions,
        "grammar": grammar,
        "questions": q,
        "counts": counts,
    }
    return story


def main(argv: list[str]) -> int:
    seen: set[str] = set()
    built = [build_story(s, seen) for s in STORIES]

    order = [lv["id"] for lv in LEVELS]
    built.sort(key=lambda s: (order.index(s["level"]), s["words"]))

    doc = {
        "version": 1,
        "credit": CREDIT,
        "levels": LEVELS,
        "totals": {
            "stories": len(built),
            "words": sum(s["words"] for s in built),
            "questions": sum(s["counts"]["all"] for s in built),
            "sentences": sum(s["sentences"] for s in built),
        },
        "stories": built,
    }

    text = json.dumps(doc, ensure_ascii=False, indent=1) + "\n"

    if "--check" in argv:
        # The test suite asks whether the file on disk still matches the
        # source, without rewriting it: a stale JSON is a story whose answers
        # belong to yesterday.
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print("stories.json is out of date with tools/mini_stories.py")
            return 1
        return 0

    OUT.write_text(text, encoding="utf-8")
    print(f"wrote stories.json: {doc['totals']['stories']} stories, "
          f"{doc['totals']['sentences']} sentences, "
          f"{doc['totals']['questions']} questions, "
          f"{OUT.stat().st_size:,} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
