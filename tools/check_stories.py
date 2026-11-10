#!/usr/bin/env python3
"""The Mini stories panel: is the content complete, and is it wired?

What this guards, in the order a failure is easiest to read.

First, freshness: stories.json is generated from tools/mini_stories.py, and a
stale JSON is a story whose answers belong to the previous draft.

Second, completeness. Every story must carry the eleven things the section
promises - title and level, the whole English text, a Persian line under every
sentence, vocabulary with meanings and examples, expressions, grammar points,
five choice questions, three true/false, three blanks, two open questions, and
answers with explanations. The build script enforces this too; this check
enforces it on the shipped file, which is what the page actually reads.

Third, wiring: the header tile, the panel markup, the Panels maps, the on-open
hook, the /api/stories route, the intent that opens it, and the APK's copy.

    python3 tools/check_stories.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "stories.json"
PAGE = ROOT / "webapp.py"
BUILDER = ROOT / "tools/build_stories.py"
BUILD = ROOT / "build_apk_ui.py"
APK_DATA = ROOT / "android/app/src/main/assets/www/data/stories.json"

FA = re.compile(r"[\u0600-\u06FF]")
problems: list[str] = []


def check(ok: bool, what: str) -> bool:
    if not ok:
        problems.append(what)
    return ok


def load() -> dict | None:
    if not DOC.exists():
        problems.append("stories.json is missing (run tools/build_stories.py)")
        return None
    try:
        return json.loads(DOC.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        problems.append(f"stories.json does not parse: {e}")
        return None


def check_fresh() -> None:
    proc = subprocess.run([sys.executable, str(BUILDER), "--check"],
                          cwd=ROOT, capture_output=True, text=True)
    check(proc.returncode == 0,
          "stories.json is out of date with tools/mini_stories.py "
          "(run python3 tools/build_stories.py)")


def check_content(doc: dict) -> dict:
    stories = doc.get("stories")
    if not check(isinstance(stories, list) and stories,
                 "stories.json has no stories"):
        return {"stories": 0, "sentences": 0, "questions": 0}

    credit = doc.get("credit") or {}
    check(bool(FA.search(credit.get("fa", ""))) and bool(credit.get("en")),
          "the panel has no bilingual credit for the English source")
    check(isinstance(credit.get("url"), str) and credit["url"].startswith("http"),
          "the credit does not link to the source")
    levels = {lv.get("id") for lv in doc.get("levels") or []}
    check(bool(levels), "no levels are declared")

    ids = set()
    sentences = questions = 0
    for s in stories:
        sid = s.get("id")
        if not check(bool(sid) and sid not in ids, f"duplicate story id {sid!r}"):
            continue
        ids.add(sid)
        if not check(s.get("level") in levels, f"{sid}: unknown level"):
            continue

        for part in ("title", "blurb"):
            got = s.get(part) or {}
            check(bool(FA.search(got.get("fa", ""))) and bool(got.get("en")),
                  f"{sid}: {part} is missing a language")

        chapters = s.get("chapters") or []
        check(len(chapters) >= 1, f"{sid}: no chapters")
        count = 0
        for ci, ch in enumerate(chapters, 1):
            check(bool(FA.search((ch.get("title") or {}).get("fa", ""))),
                  f"{sid} chapter {ci}: the title has no Persian")
            pairs = ch.get("pairs") or []
            check(len(pairs) >= 3, f"{sid} chapter {ci}: fewer than three sentences")
            for pi, pair in enumerate(pairs, 1):
                if not check(isinstance(pair, dict), f"{sid}: a sentence is not a pair"):
                    continue
                check(bool(pair.get("en", "").strip()),
                      f"{sid} chapter {ci} sentence {pi}: no English")
                check(bool(FA.search(pair.get("fa", ""))),
                      f"{sid} chapter {ci} sentence {pi}: no Persian translation")
            count += len(pairs)
        sentences += count
        check(s.get("sentences") == count,
              f"{sid}: the sentence count is stale")

        plain = s.get("text") or ""
        check(len(plain.split()) >= 60,
              f"{sid}: the story is too short to be a story")
        check(s.get("words") == len(re.findall(r"[A-Za-z'\u2019\-]+", plain)),
              f"{sid}: the word count is stale")
        check(s.get("minutes") == max(1, round(s["words"] / 170)),
              f"{sid}: the reading time does not match the text")

        vocab = s.get("vocab") or []
        check(len(vocab) >= 6, f"{sid}: {len(vocab)} vocabulary items, want 6+")
        for v in vocab:
            word = v.get("word", "")
            check(bool(word) and word.lower() in plain.lower(),
                  f"{sid}: vocabulary {word!r} is not in the story")
            check(v.get("pos") in ("n.", "v.", "adj.", "adv.", "phr."),
                  f"{sid}: vocabulary {word!r} has no part of speech")
            check(bool(FA.search((v.get("meaning") or {}).get("fa", ""))),
                  f"{sid}: vocabulary {word!r} has no Persian meaning")
            check(bool(v.get("example")) and
                  bool(FA.search(v.get("exampleFa", ""))),
                  f"{sid}: vocabulary {word!r} has no bilingual example")

        exprs = s.get("expressions") or []
        check(len(exprs) >= 4, f"{sid}: {len(exprs)} expressions, want 4+")
        for e in exprs:
            phrase = e.get("phrase", "")
            # An expression is a dictionary head ("try on"), so it need not
            # appear word for word in a past-tense sentence ("tried on").
            check(bool(phrase) and len(phrase.split()) >= 1,
                  f"{sid}: an expression has no phrase")
            check(bool(FA.search((e.get("meaning") or {}).get("fa", ""))),
                  f"{sid}: expression {phrase!r} has no Persian meaning")
            check(bool(e.get("example")) and bool(FA.search(e.get("exampleFa", ""))),
                  f"{sid}: expression {phrase!r} has no bilingual example")

        gram = s.get("grammar") or []
        check(len(gram) >= 3, f"{sid}: {len(gram)} grammar points, want 3+")
        for g in gram:
            check(bool(FA.search((g.get("name") or {}).get("fa", ""))),
                  f"{sid}: a grammar point has no Persian name")
            check(bool(g.get("example")), f"{sid}: a grammar point has no example")
            check(bool(FA.search((g.get("note") or {}).get("fa", ""))),
                  f"{sid}: a grammar note has no Persian")

        q = s.get("questions") or {}
        counts = {"mcq": 5, "truefalse": 3, "blanks": 3, "open": 2}
        for kind, want in counts.items():
            got = len(q.get(kind) or [])
            check(got >= want, f"{sid}: {got} {kind}, want {want}")
            questions += got

        for i, item in enumerate(q.get("mcq") or [], 1):
            opts = item.get("options") or []
            check(len(opts) == 4, f"{sid} mcq {i}: {len(opts)} options")
            check(isinstance(item.get("answer"), int) and 0 <= item["answer"] < 4,
                  f"{sid} mcq {i}: the key points outside the options")
            check(bool(FA.search((item.get("why") or {}).get("fa", ""))),
                  f"{sid} mcq {i}: the explanation has no Persian")
        for i, item in enumerate(q.get("truefalse") or [], 1):
            check(isinstance(item.get("answer"), bool),
                  f"{sid} truefalse {i}: the key is not a boolean")
            check(bool(FA.search((item.get("why") or {}).get("fa", ""))),
                  f"{sid} truefalse {i}: the explanation has no Persian")
        for i, item in enumerate(q.get("blanks") or [], 1):
            check("___" in item.get("sentence", ""),
                  f"{sid} blank {i}: no gap")
            check(item.get("answer", "").lower() in plain.lower(),
                  f"{sid} blank {i}: the answer is not in the story")
            check(bool(FA.search((item.get("hint") or {}).get("fa", ""))),
                  f"{sid} blank {i}: the hint has no Persian")
        for i, item in enumerate(q.get("open") or [], 1):
            check(bool((item.get("model") or {}).get("en")),
                  f"{sid} open {i}: no model answer")
            check(bool(FA.search((item.get("model") or {}).get("fa", ""))),
                  f"{sid} open {i}: the model answer has no Persian")
            check(bool(FA.search((item.get("tip") or {}).get("fa", ""))),
                  f"{sid} open {i}: the tip has no Persian")

        mcq_keys = [i["answer"] for i in q.get("mcq") or []]
        check(len(set(mcq_keys)) >= 3,
              f"{sid}: the choice keys sit on fewer than three letters")
        tf_keys = [i["answer"] for i in q.get("truefalse") or []]
        check(True in tf_keys and False in tf_keys,
              f"{sid}: true/false never varies")

        sumq = sum(len(q.get(k) or []) for k in counts)
        check(s.get("counts", {}).get("all") == sumq,
              f"{sid}: the question count is stale")

    totals = doc.get("totals") or {}
    check(totals.get("stories") == len(stories), "totals.stories is stale")
    check(totals.get("sentences") == sentences, "totals.sentences is stale")
    check(totals.get("questions") == questions, "totals.questions is stale")

    return {"stories": len(stories), "sentences": sentences,
            "questions": questions}


def check_panel() -> None:
    src = PAGE.read_text(encoding="utf-8")
    check('id="stoggle"' in src, "the Mini stories tile is not in the header")
    check('id="stpanel"' in src, "the Mini stories panel is not in the markup")
    check(re.search(r"stpanel:\s*'stoggle'", src) is not None,
          "Panels.TILES does not map the stories panel to its tile")
    # an adult still gets Stories.mount(); a kid account gets the kid story
    # reader from the same hook, so the adult call is what has to be there.
    check(re.search(r"stpanel:\s*\(\)\s*=>.*?Stories\.mount\(\)", src) is not None,
          "the stories panel has no on-open hook, so it opens blank")
    check("document.getElementById('stoggle').onclick" in src,
          "the header tile is not wired to togglePanel")
    check('startswith("/api/stories")' in src,
          "there is no /api/stories route for the page to read")
    check(re.search(r"stories:\s*\{[^}]*panel:\s*'stpanel'", src, re.S) is not None,
          "typing 'story' does not open the panel")
    check(re.search(r"#stpanel\.open\s*\{[^}]*display:\s*block", src) is not None,
          "#stpanel has no rule that shows it when open")
    check(re.search(r"#vpanel[^{]*#stpanel[^{]*\{\s*display:\s*none", src) is not None,
          "#stpanel is never hidden, so it sits in the page flow")
    # The reader must be able to hide the Persian and get the English alone.
    check(".stbody.hidefa .sts .fa" in src,
          "there is no way to hide the Persian beside the sentences")
    # The three marked sets are what progress and the result box are built on.
    check("const GROUPS = ['mcq', 'truefalse', 'blanks'];" in src,
          "the stories module does not mark the three question sets")


def check_offline() -> None:
    build = BUILD.read_text(encoding="utf-8")
    check('"stories.json"' in build,
          "the APK build does not bundle stories.json")
    if APK_DATA.exists():
        try:
            doc = json.loads(APK_DATA.read_text(encoding="utf-8"))
            check(bool(doc.get("stories")),
                  "the APK's copy of stories.json has no stories")
        except json.JSONDecodeError:
            problems.append("the APK's copy of stories.json does not parse")


def main() -> int:
    check_fresh()
    doc = load()
    stats = check_content(doc) if doc else {"stories": 0, "sentences": 0,
                                            "questions": 0}
    check_panel()
    check_offline()

    if problems:
        for p in problems[:40]:
            print("FAIL  " + p)
        if len(problems) > 40:
            print(f"      ... and {len(problems) - 40} more")
        print(f"\nFAIL  {len(problems)} problem(s) with the mini stories")
        return 1

    print(f"PASS  {stats['stories']} stories, {stats['sentences']} sentences "
          f"each with its Persian, {stats['questions']} questions with answers "
          f"and explanations; the panel, the route and the APK bundle are wired")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
