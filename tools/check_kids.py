#!/usr/bin/env python3
"""Is the kids experience real, and is it invisible to adults?

    python3 tools/check_kids.py

Two questions, and the second one matters as much as the first:

  the kids layer  is there enough of it, and is every part of it shaped the
                  way the page reads it? A word theme with no Persian, a quiz
                  whose answer is not one of its own options, a story with no
                  question - each of those renders as a blank card for a child
                  and nothing here would notice without asking.

  the adults      is any of it reachable from an account aged 15 and over?
                  Kids styling hangs off body.kids, kids panels hang off
                  Experience.kids(), and the chat reply is wrapped by a
                  function that returns it unchanged when the band is not
                  kids. This suite pins all three, because "the adult app is
                  unchanged" is the requirement, not an aspiration.

It also runs the two pure functions that decide the band, under node, at the
boundaries: 14 vs 15 is the whole classification.
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEBAPP = ROOT / "webapp.py"
KIDS = ROOT / "kids.json"
BUILD = ROOT / "build_apk_ui.py"
BUNDLE = ROOT / "android/app/src/main/assets/www"

problems = []
stats = {}


def check(cond, line):
    if not cond:
        problems.append(line)
    print(f"  {'ok  ' if cond else 'FAIL'}  {line}")
    return cond


PERSIAN = re.compile(r"[\u0600-\u06FF]")
# Adults-only subject matter: a kid bank that mentions any of these is a
# content bug, not a style choice.
BANNED = ("password", "credit card", "cigarette", "alcohol", "beer", "wine",
          "gun", "weapon", "drug", "kiss", "dating", "boyfriend", "girlfriend",
          "gambling", "casino", "porn")


def text_of(node):
    """Every English and Persian string under one item, for the safety scan."""
    if isinstance(node, str):
        return [node]
    if isinstance(node, dict):
        out = []
        for value in node.values():
            out.extend(text_of(value))
        return out
    if isinstance(node, list):
        out = []
        for value in node:
            out.extend(text_of(value))
        return out
    return []


def quiz_ok(item, label):
    """One multiple-choice item, checked the way the page draws it."""
    q = item.get("q") or ""
    options = item.get("options") or []
    answer = item.get("answer")
    if not check(len(options) == 3, f"{label}: the question needs three options, got {len(options)}"):
        return
    check(answer in options, f"{label}: the answer {answer!r} is not one of its own options")
    check(len(set(options)) == 3, f"{label}: two options are the same")
    check(item.get("why_en") and item.get("why_fa"),
          f"{label}: the explanation is not bilingual")
    check("___" in q or "?" in q, f"{label}: the question is not a question")


def check_words(data):
    themes = data.get("words") or []
    check(len(themes) >= 7, f"the word bank has {len(themes)} themes, expected at least 7")
    total = 0
    for theme in themes:
        name = theme.get("title_en") or theme.get("id")
        words = theme.get("words") or []
        check(len(words) >= 6, f"{name}: {len(words)} words, expected at least 6")
        check(bool(PERSIAN.search(theme.get("title_fa") or "")),
              f"{name}: the theme has no Persian title")
        for item in words:
            total += 1
            word = item.get("word") or ""
            where = f"{name}/{word or '?'}"
            check(bool(word), f"{name}: a word has no English form")
            check(bool(PERSIAN.search(item.get("fa") or "")),
                  f"{where}: no Persian meaning")
            check(len((item.get("def_en") or "").split()) <= 14,
                  f"{where}: the definition is a sentence, not a gloss")
            example = item.get("example_en") or ""
            check(word.lower() in example.lower(),
                  f"{where}: the example does not use the word")
            check(len(example.split()) <= 12,
                  f"{where}: the example is {len(example.split())} words - too long for a child")
            # The Persian text travels with the assertion. A log line that only
            # says "not translated" cannot tell a reader whether the check
            # passed or failed - it reads the same either way, and a passing run
            # has been mistaken for a failing one. Printing the value makes the
            # line proof rather than a claim.
            translated = item.get("example_fa") or ""
            check(bool(PERSIAN.search(translated)),
                  f"{where}: the example is not translated (example_fa={translated!r})")

    stats["words"] = total


PHOTOS = ROOT / "kids/words"


def jpeg_geometry(path: Path) -> tuple[int, int]:
    """A JPEG's pixel size, read from its own frame header.

    This suite runs on a bare CI image with no packages installed, so it may
    not import Pillow: an ImportError here does not look like a missing
    dependency in the log, it looks like a content failure with a traceback,
    and the last line printed before it was some unrelated assertion. Reading
    the SOF marker is thirty lines and validates the same two things Pillow was
    asked for - that the file really is a JPEG, and how big its picture is.

    Raises ValueError for anything that is not a whole, readable JPEG.
    """
    data = path.read_bytes()
    if not data.startswith(b"\xff\xd8"):
        raise ValueError("does not start with a JPEG marker")
    if not data.rstrip(b"\x00").endswith(b"\xff\xd9"):
        raise ValueError("is truncated - no end-of-image marker")
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xD8, 0xD9, 0x01) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        length = int.from_bytes(data[i + 2:i + 4], "big")
        # SOF0-SOF15 carry the frame; C4 (Huffman), C8 (reserved) and CC
        # (arithmetic coding) sit in the same range but are not frames.
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            height = int.from_bytes(data[i + 5:i + 7], "big")
            width = int.from_bytes(data[i + 7:i + 9], "big")
            if not width or not height:
                raise ValueError("declares a zero-sized picture")
            return width, height
        if length < 2:
            raise ValueError("has a broken segment header")
        i += 2 + length
    raise ValueError("has no frame header")


def check_word_pictures(data, src):
    """Every taught word carries a photograph of the thing it names.

    A word a child can see is a word a child keeps: the panel draws the picture
    beside the definition and the practice card draws it above the question,
    and both read the same bundled file. What this pins is the set staying
    whole - a word that lost its picture, a picture with no licence on record,
    a licence that is not one the app may ship, a file nobody references, a
    picture missing from the APK bundle - because all four render as a blank
    box or a quiet legal question and nothing else would notice.
    """
    credits_file = PHOTOS / "credits.json"
    check(credits_file.exists(),
          "kids/words/credits.json is missing - the licences of the pictures "
          "are unrecorded")
    credits = json.loads(credits_file.read_text(encoding="utf-8")) \
        if credits_file.exists() else {}

    used, words, pic = set(), 0, 0
    for theme in data.get("words") or []:
        for item in theme.get("words") or []:
            words += 1
            word = item.get("word") or "?"
            img = item.get("img") or ""
            check(bool(img), f"{word}: the word has no picture")
            if not img:
                continue
            pic += 1
            used.add(Path(img).name)
            path = ROOT / img
            exists = path.exists()
            check(exists, f"{word}: {img} does not exist")
            check((BUNDLE / img).exists(),
                  f"{word}: {img} is not in the APK bundle - the phone would show "
                  "a blank space")
            if not exists:
                continue
            kb = path.stat().st_size // 1024
            check(kb < 120, f"{word}: {img} is {kb} KB - ninety of those is a download")
            try:
                width, height = jpeg_geometry(path)
                check(width >= 320 and height >= 240,
                      f"{word}: {img} is {width}x{height} - too small to "
                      "recognise")
            except (ValueError, OSError) as exc:         # a truncated file, not a crash
                check(False, f"{word}: {img} cannot be decoded ({exc})")
            credit = credits.get(word) or {}
            check(bool(credit), f"{word}: no licence is recorded for its picture")
            check((credit.get("license") or "").lower() in ("cc0", "pdm"),
                  f"{word}: the picture is {(credit.get('license') or 'unlicensed')!r} "
                  "- only CC0 and public domain may ship here")

    on_disk = {p.name for p in PHOTOS.glob("*.jpg")}
    orphans = sorted(on_disk - used)
    check(not orphans,
          f"{len(orphans)} picture(s) belong to no word: {', '.join(orphans[:6])}")

    check("function wordPicture(" in src and "kwimg" in src,
          "the words panel no longer draws the picture beside the word")
    check("kwp-img" in src,
          "the practice card no longer shows the word's picture")
    check('self.path.startswith("/kids/")' in src,
          "the server does not serve kids/words, so the page would 404 them")
    check("kids/words" in BUILD.read_text(encoding="utf-8"),
          "build_apk_ui.py no longer copies the pictures into the APK")
    stats["word pictures"] = (pic, words)


def check_grammar(data):
    lessons = data.get("grammar") or []
    check(len(lessons) == 8, f"there are {len(lessons)} mini lessons, expected 8")
    items = 0
    for lesson in lessons:
        name = lesson.get("title_en") or lesson.get("id")
        check(bool(lesson.get("emoji")), f"{name}: the lesson has no picture")
        check(bool(PERSIAN.search(lesson.get("title_fa") or "")),
              f"{name}: the title is not translated")
        use = lesson.get("use_en") or ""
        check(0 < len(use.split()) <= 45,
              f"{name}: the explanation is {len(use.split())} words - it should be a few short sentences")
        check(bool(PERSIAN.search(lesson.get("use_fa") or "")),
              f"{name}: the explanation is not translated")
        examples = lesson.get("examples") or []
        check(len(examples) >= 3, f"{name}: {len(examples)} examples, expected at least 3")
        for ex in examples:
            check(bool(ex.get("en")) and bool(PERSIAN.search(ex.get("fa") or "")),
                  f"{name}: an example is not bilingual")
        for index, item in enumerate(lesson.get("quiz") or []):
            items += 1
            quiz_ok(item, f"{name} q{index + 1}")
    stats["grammar"] = len(lessons)
    stats["quiz"] = items


def check_grammar_comics(src, data):
    """Every grammar lesson has its comic, and the comic has all its parts.

    The cartoon half of the grammar section is hardcoded beside the panel - the
    chant, the chalkboard pairs and the fox's mood - while the lesson text
    lives in kids.json. That is the right split (a chant is written, not
    assembled) but it means the two can drift: add a lesson and the new card
    opens with no chant, no colour and no rule, which is exactly the plain card
    this work replaced. So the comic map is evaluated as JavaScript and held
    against the bank: same ids both ways, three chant lines with three Persian
    ones, a rule with at least two pairs, and a mood the fox can wear. The
    markup and the chalkboard's styles are pinned too, because a class renamed
    in the page is a section that silently loses its shape.
    """
    start = src.find("  const GRAMMAR_COMIC = {")
    check(start >= 0, "the grammar comics are gone - the section is a list again")
    if start < 0:
        return
    end = src.find("\n  };\n", start)
    check(end > start, "the grammar comic block is not closed")
    if end <= start:
        return
    block = src[start:end + len("\n  };")]

    if not shutil.which("node"):
        print("SKIP  node is not installed - the grammar comics were not run")
    else:
        ids = [lesson.get("id") for lesson in data.get("grammar") or []]
        moods = ["idle", "wave", "listen", "speak", "think", "cheer", "read", "sad"]
        script = Path("/tmp") / "kids-grammar-comic.js"
        script.write_text(
            block
            + f"""
const lessons = {json.dumps(ids, ensure_ascii=False)};
const moods = {json.dumps(moods)};
let bad = 0;
const ok = (cond, line) => {{ if (!cond) bad++; console.log(`${{cond ? '  ok  ' : '  FAIL'}}  ${{line}}`); }};
ok(Object.keys(GRAMMAR_COMIC).length === lessons.length,
   `${{Object.keys(GRAMMAR_COMIC).length}} comics for ${{lessons.length}} lessons`);
lessons.forEach((id) => ok(!!GRAMMAR_COMIC[id], `${{id}}: the lesson has a comic`));
Object.keys(GRAMMAR_COMIC).forEach((id) =>
  ok(lessons.indexOf(id) >= 0, `${{id}}: the comic belongs to a lesson in the bank`));
Object.keys(GRAMMAR_COMIC).forEach((id) => {{
  const c = GRAMMAR_COMIC[id];
  ok(Array.isArray(c.chant) && c.chant.length === 3, `${{id}}: three lines to chant`);
  ok(Array.isArray(c.chantFa) && c.chantFa.length === c.chant.length,
     `${{id}}: every chant line is in Persian too`);
  ok(c.chant.every((line) => line.trim().length > 3 && /[.?!]$/.test(line.trim())),
     `${{id}}: each chant line is a sentence a child can say`);
  ok(Array.isArray(c.rule) && c.rule.length >= 2, `${{id}}: a rule with at least two pairs`);
  ok((c.rule || []).every((p) => Array.isArray(p) && p.length === 2 && p[0] && p[1]),
     `${{id}}: every rule pair is two words`);
  ok(moods.indexOf(c.mood) >= 0, `${{id}}: the fox has a mood it can wear`);
  ok(!!(c.ruleEn && c.ruleFa), `${{id}}: the rule is explained in both languages`);
}});
process.exit(bad ? 1 : 0);
""",
            encoding="utf-8")
        proc = subprocess.run(["node", str(script)], capture_output=True, text=True)
        print(proc.stdout.strip())
        if proc.returncode != 0:
            problems.append("a grammar comic is missing a part:\n"
                            + (proc.stdout + proc.stderr).strip())
        else:
            stats["grammar comics"] = len(ids)

    for cls, meant in ((".kgl ", "the list of comic tiles"),
                       (".kbub ", "the fox's speech bubble"),
                       (".krule ", "the chalkboard"),
                       (".kchant-row ", "a chant line"),
                       (".krule-note", "the rule in words")):
        check(cls in src, f"{meant} has no style: {cls.strip()} is not in the page")
    for n in range(1, 9):
        check(f"  .kg{n} {{ --kg: var(--k-c{n});" in src,
              f"colour {n} of the comic tiles is not declared")


def check_stories(data):
    stories = data.get("stories") or []
    check(len(stories) == 4, f"there are {len(stories)} stories, expected 4")
    for story in stories:
        name = story.get("title_en") or story.get("id")
        check(bool(PERSIAN.search(story.get("title_fa") or "")),
              f"{name}: the title is not translated")
        lines = story.get("lines") or []
        check(len(lines) >= 6, f"{name}: {len(lines)} lines, expected at least 6")
        for line in lines:
            check(bool(line.get("en")) and bool(PERSIAN.search(line.get("fa") or "")),
                  f"{name}: a line is not bilingual")
        questions = story.get("questions") or []
        check(len(questions) >= 2, f"{name}: {len(questions)} questions, expected at least 2")
        for index, item in enumerate(questions):
            quiz_ok(item, f"{name} q{index + 1}")


def check_reading(data):
    passages = data.get("reading") or []
    check(len(passages) == 4, f"there are {len(passages)} passages, expected 4")
    for passage in passages:
        name = passage.get("title_en") or passage.get("id")
        body = passage.get("text_en") or ""
        words = len(body.split())
        check(30 <= words <= 140,
              f"{name}: {words} words - a kids passage should be 30 to 140")
        check(bool(PERSIAN.search(passage.get("text_fa") or "")),
              f"{name}: the passage is not translated")
        questions = passage.get("questions") or []
        check(len(questions) >= 2, f"{name}: {len(questions)} questions, expected at least 2")
        for index, item in enumerate(questions):
            quiz_ok(item, f"{name} q{index + 1}")


READING_PICS = ROOT / "kids/reading"
SENT_EN = re.compile(r"(?<=[.!?])\s+")
SENT_FA = re.compile(r"(?<=[.!?؟])\s+")


def check_reading_book(src, data):
    """The reading section is a book, and every leaf of it is complete.

    A passage is cut into leaves of two sentences, and each leaf names one
    photograph and its two-word caption - hardcoded in READING_PAGES, because
    a caption is written and not assembled. That split is the whole design, so
    this suite holds the two halves against each other: the same passages on
    both sides, a leaf for every pair of sentences, a picture on disk and in
    the APK for every leaf, a CC0/public-domain licence on record, no picture
    nobody asks for, and the styles and route the turning depends on. It also
    proves the English and Persian split into the same number of sentences,
    because that is the one condition under which the book splits at all -
    otherwise the passage falls back to a single long leaf with no picture.
    """
    passages = data.get("reading") or []
    expected = {}
    for passage in passages:
        name = passage.get("title_en") or passage.get("id")
        en = [s for s in SENT_EN.split((passage.get("text_en") or "").strip()) if s]
        fa = [s for s in SENT_FA.split((passage.get("text_fa") or "").strip()) if s]
        check(en and len(en) == len(fa),
              f"{name}: {len(en)} English sentences and {len(fa)} Persian ones - "
              "the book cannot pair them, so it would print one long page")
        expected[passage.get("id")] = (len(en) + 1) // 2

    credits_file = READING_PICS / "credits.json"
    check(credits_file.exists(),
          "kids/reading/credits.json is missing - the book's pictures are unrecorded")
    credits = json.loads(credits_file.read_text(encoding="utf-8")) \
        if credits_file.exists() else {}

    if not shutil.which("node"):
        print("SKIP  node is not installed - the book's leaves were not run")
        return

    start = src.find("  const READING_PAGES = {")
    check(start >= 0, "READING_PAGES is gone - the book has no pictures again")
    if start < 0:
        return
    end = src.find("\n  };\n", start)
    check(end > start, "the READING_PAGES block is not closed")
    if end <= start:
        return
    block = src[start:end + len("\n  };")]

    script = Path("/tmp") / "kids-reading-book.js"
    script.write_text(
        block
        + f"""
const expected = {json.dumps(expected)};
let bad = 0;
const ok = (cond, line) => {{ if (!cond) bad++; console.log(`${{cond ? '  ok  ' : '  FAIL'}}  ${{line}}`); }};
ok(Object.keys(READING_PAGES).length === Object.keys(expected).length,
   `${{Object.keys(READING_PAGES).length}} illustrated books for ${{Object.keys(expected).length}} passages`);
Object.keys(expected).forEach((id) => ok(!!READING_PAGES[id], `${{id}}: the passage has its pages`));
Object.keys(READING_PAGES).forEach((id) =>
  ok(id in expected, `${{id}}: the pages belong to a passage in the bank`));
Object.keys(READING_PAGES).forEach((id) => {{
  const pages = READING_PAGES[id];
  ok(pages.length === expected[id],
     `${{id}}: ${{pages.length}} pictures for ${{expected[id]}} leaves of two sentences`);
  pages.forEach((row, i) => {{
    ok(Array.isArray(row) && row.length === 3, `${{id}} page ${{i + 1}}: a picture and two captions`);
    ok(/^[a-z0-9-]+$/.test(row[0] || ''), `${{id}} page ${{i + 1}}: the file name is safe`);
    ok((row[0] || '').indexOf(id + '-') === 0,
       `${{id}} page ${{i + 1}}: the picture belongs to this passage`);
    ok(!!(row[1] && row[1].trim().length > 2), `${{id}} page ${{i + 1}}: it has an English caption`);
    ok(/[\u0600-\u06FF]/.test(row[2] || ''), `${{id}} page ${{i + 1}}: the caption is in Persian too`);
  }});
}});
process.exit(bad ? 1 : 0);
""",
        encoding="utf-8")
    proc = subprocess.run(["node", str(script)], capture_output=True, text=True)
    print(proc.stdout.strip())
    if proc.returncode != 0:
        problems.append("a book page is incomplete:\n" + (proc.stdout + proc.stderr).strip())

    # the pictures themselves
    stems = json.loads(subprocess.run(
        ["node", "-e",
         block + "\nprocess.stdout.write(JSON.stringify(Object.values(READING_PAGES)"
                 ".flat().map(r => r[0])));"],
        capture_output=True, text=True).stdout or "[]")
    check(bool(stems), "no book page names a picture")
    for stem in stems:
        path = READING_PICS / (stem + ".jpg")
        rel = "kids/reading/" + stem + ".jpg"
        exists = path.exists()
        check(exists, f"{stem}: {rel} does not exist")
        check((BUNDLE / rel).exists(), f"{stem}: {rel} is not in the APK bundle")
        credit = credits.get(stem) or {}
        check(bool(credit), f"{stem}: no licence is recorded for its picture")
        check((credit.get("license") or "").lower() in ("cc0", "pdm"),
              f"{stem}: the picture is {(credit.get('license') or 'unlicensed')!r} "
              "- only CC0 and public domain may ship here")
        if not exists:
            continue
        try:
            width, height = jpeg_geometry(path)
            check(width >= 320 and height >= 240,
                  f"{stem}: {rel} is {width}x{height} - too small to see")
        except (ValueError, OSError) as exc:
            check(False, f"{stem}: {rel} cannot be decoded ({exc})")
    on_disk = {p.stem for p in READING_PICS.glob("*.jpg")}
    orphans = sorted(on_disk - set(stems))
    check(not orphans, f"{len(orphans)} book picture(s) belong to no page: {', '.join(orphans[:5])}")

    # the book itself
    for bit, meant in ((".kbook ", "the book's frame"),
                       (".kpage ", "the paper leaf"),
                       (".kpage-curl", "the corner that turns the page"),
                       ("kflip-out-next", "the turn animation"),
                       ("kbook-next", "the next-page control"),
                       ("kbook-dots", "the page dots")):
        check(bit in src, f"{meant} is not in the page: {bit.strip()}")
    check("reading/[a-z0-9-]+" in src,
          "the server no longer serves kids/reading, so every page would 404 its picture")
    check("reading" in BUILD.read_text(encoding="utf-8"),
          "build_apk_ui.py no longer copies the book pictures into the APK")
    stats["book pages"] = len(stems)


def check_story_book(src, data):
    """The stories section is a picture book, and every page has a drawing.

    A story is cut into leaves of two lines, like a passage, and each leaf
    names one drawing plus its two-word caption in both languages. The drawings
    are SVG scenes composed here out of parts (cat, bird, tree, child, sun,
    boat, puddle) rather than photographs, because the picture has to be the
    thing the line is about: a photo search for "cat pushes a red ball" returns
    a cat on a sofa. This suite runs the scenes for real under node and holds
    them against kids.json - one scene per story page, every scene used, no
    external URLs, and markup that is actually a picture - then checks the
    shared book and the utility classes the section is built from.
    """
    stories = data.get("stories") or []
    expected = {}
    for st in stories:
        story_id = st.get("id") or ""
        lines = st.get("lines") or []
        expected[story_id] = (len(lines) + 1) // 2      # two lines a leaf

    if not shutil.which("node"):
        print("SKIP  node is not installed - the story leaves were not run")
        return

    start = src.find("  const INK = '#3b3226';")
    check(start >= 0, "the story drawings are gone - the section has no pictures again")
    if start < 0:
        return
    anchor = src.find("  const STORY_PAGES = {", start)
    check(anchor > start, "STORY_PAGES is gone - no story page knows its drawing")
    if anchor <= start:
        return
    end = src.find("\n  };\n", anchor)
    check(end > anchor, "the STORY_PAGES block is not closed")
    if end <= anchor:
        return
    block = src[start:end + len("\n  };")]

    script = Path("/tmp") / "kids-story-book.js"
    script.write_text(
        block
        + f"""
const expected = {json.dumps(expected)};
let bad = 0;
const ok = (cond, line) => {{ if (!cond) bad++; console.log(`${{cond ? '  ok  ' : '  FAIL'}}  ${{line}}`); }};
ok(Object.keys(STORY_PAGES).length === Object.keys(expected).length,
   `${{Object.keys(STORY_PAGES).length}} story books for ${{Object.keys(expected).length}} stories`);
Object.keys(expected).forEach((id) => ok(!!STORY_PAGES[id], `${{id}}: the story has its pages`));
Object.keys(STORY_PAGES).forEach((id) =>
  ok(id in expected, `${{id}}: the pages belong to a story in the bank`));
const used = new Set();
Object.keys(STORY_PAGES).forEach((id) => {{
  const pages = STORY_PAGES[id];
  ok(pages.length === expected[id],
     `${{id}}: ${{pages.length}} drawings for ${{expected[id]}} pages of two lines`);
  pages.forEach((row, i) => {{
    ok(Array.isArray(row) && row.length === 3, `${{id}} page ${{i + 1}}: a drawing and two captions`);
    ok(/^[a-z0-9-]+$/.test(row[0] || ''), `${{id}} page ${{i + 1}}: the scene name is safe`);
    ok((row[0] || '').indexOf(id + '-') === 0,
       `${{id}} page ${{i + 1}}: the drawing belongs to this story`);
    ok(!!(row[1] && row[1].trim().length > 2), `${{id}} page ${{i + 1}}: it has an English caption`);
    ok(/[\\u0600-\\u06FF]/.test(row[2] || ''), `${{id}} page ${{i + 1}}: the caption is in Persian too`);
    ok(!!STORY_SCENES[row[0]], `${{id}} page ${{i + 1}}: ${{row[0]}} has no drawing`);
    used.add(row[0]);
  }});
}});
Object.keys(STORY_SCENES).forEach((name) => {{
  ok(used.has(name), `${{name}}: the drawing is on no page`);
  ok(typeof STORY_SCENES[name] === 'function', `${{name}}: the scene is not a drawer`);
  const svg = STORY_SCENES[name]();
  ok(/^<svg[^>]+viewBox="0 0 320 200"/.test(svg), `${{name}}: the scene is not an svg at 320x200`);
  ok(/role="img"/.test(svg) && /aria-label="[^"]{{10,}}"/.test(svg),
     `${{name}}: the drawing has no description for a screen reader`);
  ok(!/https?:/i.test(svg), `${{name}}: the drawing reaches for the network`);
  ok((svg.match(/<(circle|rect|path|ellipse|polygon|line|g)[ >]/g) || []).length >= 8,
     `${{name}}: the scene has ${{(svg.match(/<(circle|rect|path|ellipse|polygon|line)[ >]/g) || []).length}} shapes - too empty to read`);
}});
process.exit(bad ? 1 : 0);
""",
        encoding="utf-8")
    proc = subprocess.run(["node", str(script)], capture_output=True, text=True)
    print(proc.stdout.strip())
    if proc.returncode != 0:
        problems.append("a story page is incomplete:\n" + (proc.stdout + proc.stderr).strip())

    # the same book, and the classes the section is built from
    for bit, meant in (("function turnBook(", "the shared book is gone, so Read and Stories cannot turn alike"),
                       ("turnBook({\n      host: box,\n      title: (st.emoji",
                        "the story book is not drawn with the shared book"),
                       ("turnBook({\n      host: box,\n      title: (p.emoji",
                        "the reading book was not moved onto the shared book"),
                       ("function endLeaf(", "there is no shared end page with the questions"),
                       (".kscene-svg", "the drawing has no frame"),
                       (".kscene-cap", "the drawing has no caption strip"),
                       (".kbc-art-scene", "the shelf covers show no drawing"),
                       ("body.kids .tw-flex", "the utility classes are not scoped to a child's page"),
                       ("tw-flex tw-items-center tw-justify-between", "the story pages use no utilities")):
        check(bit in src, meant)
    stats["story pages"] = sum(expected.values())


def check_listening(data):
    clips = data.get("listening") or []
    check(len(clips) == 5, f"there are {len(clips)} listening clips, expected 5")
    for clip in clips:
        name = clip.get("title_en") or clip.get("id")
        check(bool(PERSIAN.search(clip.get("title_fa") or "")),
              f"{name}: the title is not translated")
        lines = clip.get("lines") or []
        check(len(lines) >= 3, f"{name}: {len(lines)} lines, expected at least 3")
        for line in lines:
            check(bool(line.strip()), f"{name}: an empty spoken line")
        for index, item in enumerate(clip.get("questions") or []):
            quiz_ok(item, f"{name} q{index + 1}")


def check_phrases(data):
    sets = data.get("phrases") or []
    check(len(sets) == 5, f"there are {len(sets)} phrase sets, expected 5")
    for group in sets:
        name = group.get("title_en") or group.get("id")
        check(bool(PERSIAN.search(group.get("title_fa") or "")),
              f"{name}: the title is not translated")
        items = group.get("items") or []
        check(len(items) >= 4, f"{name}: {len(items)} phrases, expected at least 4")
        for item in items:
            check(bool(item.get("en")) and bool(PERSIAN.search(item.get("fa") or "")),
                  f"{name}: a phrase is not bilingual")


def check_chat(data):
    chat = data.get("chat") or {}
    for key in ("welcome", "praise", "safety"):
        check(bool(chat.get(key + "_en")), f"the kid chat has no {key} line")
        check(bool(PERSIAN.search(chat.get(key + "_fa") or "")),
              f"the {key} line is not in Persian")
    safety = (chat.get("safety_en") or "").lower()
    for word in ("address", "phone", "school"):
        check(word in safety,
              f"the safety line does not name {word} - it is the thing a child is asked for")
    starters = chat.get("starters") or []
    check(len(starters) >= 4, f"{len(starters)} starter chips, expected at least 4")
    for chip in starters:
        check(isinstance(chip, list) and len(chip) == 3 and bool(chip[0]) and bool(chip[1])
              and bool(PERSIAN.search(chip[2] or "")),
              f"the starter chip {chip!r} is not a query, a label and a Persian label")
    check("I am" in (chat.get("welcome_en") or ""),
          "the welcome does not use the American form the app teaches")


def check_safety_scan(data):
    banned = set()
    for chunk in text_of(data):
        low = chunk.lower()
        for word in BANNED:
            if word in low:
                banned.add(word)
    check(not banned, f"adult subject matter appears in the kid bank: {sorted(banned)}")


def check_classification(src):
    check("const KIDS_UNDER = 15;" in src,
          "the age boundary is not 15, or is not stated once")
    check("age < KIDS_UNDER ? 'kids' : 'adults'" in src,
          "the band is not decided in one place from the age")

    if not shutil.which("node"):
        print("SKIP  node is not installed - the band boundaries were not run")
        return
    start = src.index("  const KIDS_UNDER = 15;")
    end = src.index("  /* The band saved on the account.", start)
    module = src[start:end]
    script = Path("/tmp") / "kids-band.js"
    script.write_text(
        module
        + """
let bad = 0;
const ok = (cond, line) => { if (!cond) bad++; console.log(`${cond ? '  ok  ' : '  FAIL'}  ${line}`); };
const kidsAt = [0, 1, 5, 9, 13, 14];
kidsAt.forEach((a) => ok(bandFor(a) === 'kids', `a child of ${a} gets the kids experience`));
[15, 16, 18, 40, 120].forEach((a) => ok(bandFor(a) === 'adults', `an account of ${a} gets the adult app`));
[null, undefined, '', 'x', -1, 121, 3.5, NaN].forEach((v) =>
  ok(cleanAge(v) === null, `${JSON.stringify(v)} is not an age`));
ok(cleanAge('9') === 9, 'the age field, which is text, is read as a number');
ok(cleanAge(9) === 9, 'an age that is already a number is kept');
ok(cleanAge(0) === 0, 'zero is a real age and not an empty one');
process.exit(bad ? 1 : 0);
""",
        encoding="utf-8")
    proc = subprocess.run(["node", str(script)], capture_output=True, text=True)
    print(proc.stdout.strip())
    if proc.returncode != 0:
        problems.append("a band boundary is wrong:\n" + (proc.stdout + proc.stderr).strip())
        return
    stats["boundaries"] = 6 + 5 + 10


def check_signup(src):
    field = re.search(r'<input id="authage"[^>]*>', src)
    check(field is not None, "the sign-up form has no age field")
    if field:
        tag = field.group(0)
        check('max="120"' in tag and 'min="0"' in tag,
              "the age field does not state the range it accepts")
    check('id="authage"' in src and "choose the right experience" in src,
          "the form does not say why the age is wanted")
    check("if (age == null)" in src,
          "sign-up does not refuse a missing age")
    check("age, band: Experience.bandFor(age)" in src,
          "the band is not stored with the account")
    check("Experience.onSignedIn()" in src,
          "signing in does not apply the saved band")
    check("Experience.paint()" in src and "classList.toggle('kids'" in src,
          "the page never turns the kids class on")
    check("if (!Auth.signedIn()) return '';" in src,
          "the band survives sign-out - the sign-in card would be painted for a child")

    gate = re.search(r'<div id="agegate".*?</div>\s*</div>', src, re.S)
    check(gate is not None, "there is no overlay for an account that has no age")
    for bit in ('id="ageinput"', 'id="agesubmit"', 'id="ageerr"'):
        check(bit in src, f"the age gate is missing {bit}")
    check("askAge()" in src, "the missing age is never asked for")
    check("Experience.askAge()" in src,
          "nothing calls the gate when an account has no age")
    check("account.band = bandFor(age);" in src and "write(ACCOUNT, account);" in src,
          "the gate does not save into the existing account")
    save = re.search(r"function saveAge\(age\) \{(.*?)\n  \}", src, re.S)
    check(save is not None and "write(ACCOUNT, account)" in save.group(1)
          and "write(SESSION" not in save.group(1),
          "saving the age must update the account, not create or replace a session")


def check_kids_layer(src):
    check("const Kids = (() => {" in src, "there is no kids layer on the page")
    check("const Experience = (() => {" in src, "there is no experience classifier")
    check("kpanel: 'kidstoggle'," in src, "the kids home is not a panel with a tile")
    check("kpanel: () => Kids.home()," in src, "the kids home has no hook")
    for panel, fn in (("vpanel", "vocab"), ("gpanel", "grammar"), ("stpanel", "stories"),
                      ("rdpanel", "reading"), ("lpanel", "listening"), ("fpanel", "phrases")):
        at = src.find(f"{panel}: () =>")
        hook = src[at:at + 220] if at >= 0 else ""
        check(at >= 0 and "Experience.kids()" in hook and f"Kids.{fn}(" in hook,
              f"{panel} does not switch to the kids {fn} panel")
    check("body:not(.kids) #kpanel, body:not(.kids) #kidstoggle," in src,
          "the kids home is visible to an adult")
    check("display: none !important;" in src.split("body:not(.kids) #kpanel")[1][:120],
          "the adult hide rule is not strong enough to beat the tile layout")
    check("#kidsmore" in src and "moreopen" in src,
          "the advanced tiles have no show-more control")
    check("Kids.land()" in src, "nothing opens the kids home after sign-in")
    # The Today's English card is out of the kids home: the words-of-the-day
    # card already carries that ground, and it was the heaviest thing a child
    # had to scroll past to reach the sections.
    # The Today's English card is gone from the kids home, helper and all: the
    # words-of-the-day tile already carries that ground and the card was the
    # heaviest thing a child had to scroll past.
    check("todayCard(" not in src and "wordOfDay(" not in src,
          "the kids home no longer builds a Today's English card")
    # The home page is not a second copy of the toolbar. The six doors that
    # used to sit under the greeting are the six buttons in the header, so the
    # page carries things to do instead: the fox's line, three words to turn
    # over, and the word game.
    check("function homeTiles" not in src and "homeTiles()" not in src,
          "the kids home still draws the header's own sections as doors")
    check("function foxSays" in src and "foxSays()" in src,
          "the kids home has nothing to answer back to")
    check("function flipTray" in src and "flipTray(d)" in src,
          "the kids home has no words to turn over")
    check("practiceCard(" in src and "practiceCard(d)" in src,
          "the word game is gone from the kids home")
    home_src = src[src.index("async function home()"):]
    home_src = home_src[:home_src.index("function land()")]
    for gone in ("openPanel('vpanel')", "openPanel('gpanel')", "openPanel('rdpanel')",
                 "openPanel('lpanel')", "openPanel('stpanel')"):
        check(gone not in home_src, "the kids home still routes to " + gone)
    # The tile is not merely behind More: the kids toolbar drops Today's
    # English outright, and a panel carried over from the adult shell closes.
    check("const today = $('dtoggle');" in src and "today.hidden = true" in src
          and "today.hidden = false" in src
          and "Panels.isOpen() === 'dpanel'" in src,
          "the kids toolbar still offers Today's English")
    check("dtoggle: 'Today'" not in src,
          "the kids label table still renames the Today tile")
    # Level, Path, Sounds and Books are the adult course's tools - a placement
    # exam, the path built from it, a rhythm drill and a book shelf. A child's
    # copy hides the tile and the panel, and never mounts either behind a tap.
    for tile, panel in (("lvltoggle", "lvlpanel"), ("pathtoggle", "pathpanel"),
                        ("phtoggle", "phpanel"), ("btoggle", "bpanel")):
        check(f"body.kids #{tile}" in src and f"body.kids #{panel}" in src,
              f"the kids copy still offers {tile}")
        at = src.find(f"{panel}: () =>")
        hook = src[at:at + 160] if at >= 0 else ""
        check(at >= 0 and "Experience.kids()" in hook,
              f"{panel} still mounts behind a child's tap")

    # Every styling rule for kids must hang off body.kids: an unscoped
    # ".kcard" would repaint an adult card in a child's palette the moment
    # the markup exists on both.
    start = src.index("     FLUENTIFY KIDS")
    end = src.index("  /* ---------- 11. the lot, off", start)
    block = src[start:end]
    check(block.count("body.kids") >= 20,
          f"only {block.count('body.kids')} kids rules are scoped to the class")
    unscoped = []
    for line in block.splitlines():
        if "{" not in line or "body.kids" in line or line.strip().startswith(("@", "}")):
            continue
        selector = line.split("{", 1)[0].strip()
        if not selector or not re.match(r"^[.#]", selector):
            continue
        if all(part.strip().startswith((".k", "#k")) for part in selector.split(",")):
            continue          # kid-only markup, which no adult panel contains
        unscoped.append(line.strip())
    check(not unscoped,
          f"kids rules reach adult selectors: {unscoped[:6]}")
    palette = block.split("body.kids {", 1)[1] if "body.kids {" in block else ""
    check("--k-primary:" in palette and "--k-surface:" in palette
          and "--k-ink:" in palette,
          "the kids palette is not declared as tokens under body.kids")
    check("--surf-1:" in palette and "--ink:" in palette,
          "the shared surface tokens are not pointed at the kids palette")
    check("background: var(--k-surface)" in block and "color: var(--k-ink)" in block,
          "the kids components do not consume the tokens")
    # One theme for kids, the light one: no night palette, no switch on the
    # toolbar, and the head script must not paint a child's page dark before
    # the app has read who is signed in.
    check('[data-theme="dark"] body.kids' not in src,
          "the kids copy is back to two themes")
    check("body.kids #themetoggle { display: none !important; }" in src,
          "the theme switch is still on the kids toolbar")
    check("who.band === 'kids'" in src and "who.age && who.age < 15" in src,
          "a child's page can still be painted dark before the app knows who they are")
    light_tokens = block.split("body.kids {", 1)[1].split("}", 1)[0]
    for name in ("--k-on-primary", "--k-track", "--k-highlight", "--k-card-shadow",
                 "--k-hero-shadow", "--k-backdrop", "--k-say", "--k-hero-sub"):
        check(name + ":" in light_tokens, f"the kids palette is missing {name}")

    # The six section accents are tokens, not hexes sprinkled through the rules:
    # a tile with its own literal is a color that cannot be retuned in one
    # place, and the fifth section is where a palette starts to drift.
    for name in ("--k-blue", "--k-blue-wash", "--k-blue-ink",
                 "--k-purple", "--k-purple-wash", "--k-purple-ink",
                 "--k-orange", "--k-orange-wash", "--k-orange-ink",
                 "--k-focus"):
        check(name + ":" in light_tokens, f"the kids palette is missing {name}")
    check("--k-sec:" in block and "--k-sec-wash" in block and "--k-sec-ink" in block,
          "the section tiles do not take their accent from one set of tokens")
    for cls in ("kc-blue", "kc-purple", "kc-pink", "kc-sun", "kc-coral", "kc-navy"):
        check(cls in block, f"the {cls} section has no identity to draw")
    check("--k-focus:" in light_tokens, "focus has no colour of its own")

    # One drawn icon set, still used wherever a section is named with a
    # symbol (the resume card). The home page's own toys are a fox line and
    # three word cards, so what is checked here is the set, not six doors.
    check("function kicon(name)" in src and "const KICONS = {" in src,
          "the drawn section icon set is gone")
    icons = src[src.index("const KICONS = {"):src.index("function kicon")]
    check(icons.count("<path") >= 6 and "viewBox" not in icons,
          "the icons are not drawn as plain paths on one grid")
    check('viewBox="0 0 24 24"' in src and 'stroke="currentColor"' in src,
          "the icons do not inherit the chip's color")
    toys = src[src.index("function foxSays"):src.index("function practiceCard")]
    check("kflip" in toys and "FOX_SAYS" in toys,
          "the home page's two toys are not both built")
    check(not re.search(r"openPanel\(", toys),
          "a home toy is a disguised section door")

    # Contrast cannot be judged by eye, and a more colorful palette is exactly
    # the change most likely to break it. Every text token that sits on a
    # surface is measured against that surface at WCAG AA for normal text.
    def _rgb(h):
        h = h.strip().lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    def _lum(h):
        def channel(v):
            v /= 255
            return v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
        r, g, b = _rgb(h)
        return .2126 * channel(r) + .7152 * channel(g) + .0722 * channel(b)

    def contrast(fg, bg):
        a, b = _lum(fg), _lum(bg)
        return (max(a, b) + .05) / (min(a, b) + .05)

    tok = dict(re.findall(r"(--k-[a-z0-9-]+):\s*(#[0-9a-fA-F]{6})", light_tokens))
    for fg, bg in (("--k-ink", "--k-bg"), ("--k-ink", "--k-surface"),
                   ("--k-ink-2", "--k-surface"), ("--k-ink-2", "--k-bg"),
                   ("--k-on-primary", "--k-primary-dark"),
                   ("--k-primary-dark", "--k-primary-wash"),
                   ("--k-blue-ink", "--k-blue-wash"),
                   ("--k-purple-ink", "--k-purple-wash"),
                   ("--k-pink-ink", "--k-pink-wash"),
                   ("--k-sun-ink", "--k-sun-wash"),
                   ("--k-coral-ink", "--k-coral-wash"),
                   ("--k-orange-ink", "--k-orange-wash"),
                   ("--k-sky-ink", "--k-sky")):
        ok = fg in tok and bg in tok
        ratio = contrast(tok[fg], tok[bg]) if ok else 0
        check(ok and ratio >= 4.5,
              f"{fg} on {bg} is {ratio:.2f}:1, below the 4.5:1 the children read at")

    motion = src[src.index("@media (prefers-reduced-motion: reduce)", end):]
    for sel in (".kspark", ".kstars i"):
        check(sel in motion[:1200], f"{sel} is not stilled for reduced motion")


def check_chat_wiring(src):
    send = src.index("add(Kids.says(text, data.reply), 'bot');")
    check(send > 0, "the chat reply does not go through the kids wrapper")
    says_start = src.index("  function says(text, reply) {")
    says = src[says_start:says_start + 2600]
    check("if (!on()) return reply;" in says,
          "the kids wrapper does not hand an adult their reply untouched")
    check("PRIVATE" in says and "PRIVATE.test(" in says,
          "the kids chat does not check the learner's own message")
    check("kids.starters()" in src or "Kids.starters()" in src,
          "the starter chips never switch to the kid ones")
    check("Kids.welcome()" in src, "the opening message never switches to the kid one")


    # ---- the child's answer, and the cards under it -----------------------
    # The knowledge is the adult engine's; what this suite holds is the frame
    # a child reads: an opener, a middle short enough to keep, a cheer and a
    # door they can walk through without typing. Every piece is hardcoded in
    # the page, so it cannot be missing inside the offline APK.
    says_at = src.index("  function says(text, reply) {")
    says_body = src[says_at:says_at + 1200]
    check("return kinder(body, text);" in says_body,
          "a child's answer is not shaped for a child")
    check("body.length < 120" in says_body,
          "a short answer is dressed up until it is no longer short")
    check("KID_DOOR" in src, "the answer gives the child no next move")
    check("برای شنیدن" in src, "the door is not written in Persian too")
    check(src.count("const KID_OPENERS") == 1 and src.count("const KID_CHEERS") == 1,
          "the kid openers or cheers are not declared exactly once")
    check("function kinder(" in src, "there is no shaping function for a child's answer")
    check("core.length > 700" in src, "a very long answer is handed to a child whole")
    check("lastIndexOf('. ')" in src, "a long answer is not cut at a sentence")
    check("EMOJI_ANY" in src and "core += ' \U0001F388'" in src,
          "an answer with no picture in it stays a wall of words")

    # three cards for a child who cannot type a reply yet
    for key in ("'hear'", "'slow'", "'got'"):
        check("key: " + key in src, f"the {key} card is missing from the kid chat")
    check("kidChips, kidSticker, kidCheer," in src,
          "the chat cannot reach the kid cards")
    check("chip.key === 'hear'" in src and "Speech.speak(speakable(text))" in src,
          "the hear card does not read the answer out")
    check("rate: 0.72" in src, "the slowly card is not slower")
    check("function speakable(text)" in src,
          "the answer is read out with its markup and emoji still in it")
    check("split('\\n')" in src and "[\\u0600-\\u06FF]" in src,
          "the English voice is handed the Persian lines")
    chips_at = src.index("if (chip.key === 'hear')")
    chips_body = src[chips_at:chips_at + 700]
    check("fetch(" not in chips_body, "a card under an answer goes to the network")
    check("Kids.kidCheer(text)" in src, "the I-got-it card gets no answer back")

    check("'kchips'" in src and "'kchip'" in src,
          "the cards are never drawn under a reply")
    check("typeof Kids !== 'undefined' && Kids.on()" in src,
          "the cards are not limited to a child's chat")
    check("sticker.className = 'ksticker';" in src,
          "a reply carries no sticker in a child's chat")
    check("body.kids .ksticker {" in src, "the sticker is never shown")
    # The bot bubble's ::after is the landing sheen. Hanging the sticker on it
    # parked that gradient band over the words, so the kids layer must not
    # touch that pseudo-element at all.
    check("body.kids .msg.bot::after { content: none; }" in src,
          "a child's bubble still carries the sheen, which can park over the words")
    check("body.kids .ksticker {" in src and "position: absolute; top: -10px" in src,
          "the sticker is not on a box of its own, so it can land on the words")

    # a starter a child can read without reading
    check("const KID_ART = {" in src, "the kid starters carry no pictures")

    check_kid_kb(src)


def check_kid_kb(src):
    """The tutor a beginner meets: one word in, one readable card out.

    The adult engine is written for a learner who knows what a synonym is and
    can read phonetic script. A child who knows almost no English needs the
    word in Persian, how to say it in Persian letters, and one short sentence.
    These checks hold that promise: a bank big enough to answer the first
    hundred questions, a pronunciation line on every entry, a gate in front of
    the adult-only subjects, and no grammar jargon left in a child's answer.
    """
    import re

    def block(marker, end):
        try:
            start = src.index(marker)
            return src[start:src.index(end, start + len(marker))]
        except ValueError:
            check(False, f"the kid knowledge base has no {marker!r} block")
            return ""

    kb = block("const KID_KB = [", "const KID_TOPICS = [")
    rows = re.findall(r"\{en: '([^']+)', fa: '([^']+)', say: '([^']+)', e: '([^']+)', t: '([a-z]+)'\}", kb)
    check(len(rows) >= 60, f"the child's bank holds only {len(rows)} words")
    missing = [r[0] for r in rows if not (r[1] and r[2] and r[3] and r[4])]
    check(not missing, f"these words carry no Persian or no pronunciation: {missing[:5]}")
    # Every pronunciation is written in Persian letters: that is the whole
    # point of it. A Latin respelling would leave a beginner where she started.
    latin = [r[0] for r in rows if not re.search(r"[\u0600-\u06FF]", r[2])]
    check(not latin, f"these words are pronounced in Latin letters, not Persian: {latin[:5]}")
    topics = block("const KID_TOPICS = [", "const KID_SAYS = [")
    trows = re.findall(r"\{id: '([a-z]+)'", topics)
    check(len(trows) >= 8, f"only {len(trows)} topics can be browsed")
    for topic in trows:
        n = len([r for r in rows if r[4] == topic])
        check(n >= 4, f"the {topic} topic holds only {n} words, too few to browse")
    orphans = [r[0] for r in rows if r[4] not in trows]
    check(not orphans, f"these words belong to no browsable topic: {orphans[:5]}")

    says = block("const KID_SAYS = [", "const KID_NUM = [")
    srows = re.findall(r"\{keys: \[[^\]]+\], en: '([^']+)', fa: '([^']+)', say: '([^']+)', e: '([^']+)'\}", says)
    check(len(srows) >= 12, f"only {len(srows)} everyday sentences are taught")
    check("const KID_NUM = [" in src, "there are no numbers to count with")
    check("const KID_DAYS = [" in src, "a child cannot ask for the days of the week")
    check("'one hundred'" in src, "the numbers stop before a child can count to a hundred")

    # A pronunciation must be shown, not only stored.
    card = block("function kWordCard(w) {", "function kTopicCard(")
    check("w.say" in card, "a word card never shows how to say the word")
    check("kArticle(w.en)" in card, "a word card says 'a apple'")

    # The three answers a child must always be able to reach.
    for needle, what in (
        ("function kidAnswer(text)", "there is no child-first lookup"),
        ("function kMenu()", "there is no menu of things a child can ask"),
        ("function kGrownUp()", "an adult-only question is not turned away kindly"),
        ("function soften(body)", "an adult answer is not stripped of its adult scaffolding"),
        ("const KID_GROWN =", "nothing marks the subjects that are not for a child"),
    ):
        check(needle in src, f"kid tutor: {what}")

    says_body = block("function says(text, reply) {", "const kidChips =")
    check("kidAnswer(text)" in says_body, "a child's chat never asks the child bank first")
    check(says_body.index("kidAnswer(text)") < says_body.index("kinder("),
          "the adult engine answers before the child's own bank")
    check("soften(" in says_body, "an adult answer reaches a child unsoftened")
    check("kMenu()" in says_body, "the adult 'I do not understand' menu reaches a child")

    # The gate has to cover money, exams and grown-up paperwork in both
    # languages, or a child typing «قیمت» gets a pricing answer.
    grown = block("const KID_GROWN =", "/* Folding:")
    for word in ("قیمت", "آیلتس", "پول", "مدرک", "price", "exam", "interview"):
        check(word in grown, f"the child gate lets through {word}")
    check("KID_GROWN.test(" in block("function kidAnswer(text)", "function soften("),
          "the gate is declared but never asked")

    # Matching must not fire a short Persian word inside a longer one: «نه»
    # lives inside «خانه», and a house must not answer "No".
    matcher = block("function kMatch(term) {", "let kIndex = null;")
    check("'(^| )'" in matcher,
          "a short Persian word can match inside a longer one")
    check("'([^a-z]|$)'" in matcher, "an English word can match inside a longer one")

    # Keywords are compiled once and reused: the first draft rebuilt a RegExp
    # per keyword per message, which is work a child's phone does not need.
    check("function kBank()" in src and "if (kIndex) return kIndex;" in src,
          "the bank's matchers are rebuilt on every message")
    check("kHas(" not in src, "a second, uncompiled matcher is still in use")

    # An adult answer must not reach a child just because the question was
    # innocent: "help" can return a subscription page.
    check("const KID_ADULT =" in src, "nothing checks the answer itself for adult subjects")
    guard = block("function says(text, reply) {", "const kidChips =")
    check("KID_ADULT.test(body)" in guard,
          "an adult answer reaches a child because only the question was checked")
    check(guard.index("KID_ADULT.test(body)") < guard.index("kinder("),
          "an adult answer is dressed up for a child before it is refused")

    # Nothing a child reads may be a grammar term he has to look up.
    kid_text = kb + topics + says
    for jargon in ("synonym", "collocation", "phrasal", "CEFR", "IPA", "clause",
                   "مجهول", "هم‌نشینی", "واژگان تخصصی"):
        check(jargon not in kid_text, f"'{jargon}' is still in what a child reads")

    # ---- the chrome the child has to read --------------------------------
    labels = block("const LABELS = {", "};")
    check(labels, "the toolbar has no labels")
    latin_labels = re.findall(r"\b(?:[a-z]+toggle): '([^']*[A-Za-z][^']*)'", labels)
    check(not latin_labels, f"these tiles are still labelled only in English: {latin_labels[:4]}")
    check("const LABELS_EN = {" in src, "the English names are gone from the app entirely")
    check("LABELS_EN[id] + ' — ' + LABELS[id]" in src,
          "a tile does not name itself in both languages for a screen reader")
    composer = block("const composer = $('input');", "/* The fox on the home card listens")
    check("placeholder" in composer and "یک واژه" in composer,
          "the message box still asks a beginner to type in English")
    # The three cards on the home page and the More tile: a child who reads no
    # English has to be able to name what is in front of them.
    # ---- the panels: what a beginner reads, in the order she reads it ------
    # A list row used to put the English name first in bold and the Persian
    # translation under it, which is a lesson plan, not a signpost.
    check("function kTitle(en, faText)" in src, "there is no Persian-first title")
    check("body.appendChild(kTitle(item.title_en, item.title_fa))" in src,
          "a list row still leads with its English name")
    check("function kDigits(n)" in src, "counts are still written in Latin digits")
    check(src.count("kDigits(") >= 5, "only some counts are written in Persian digits")
    # the adult journey cards used to top the child's sentence list
    phrases = block("async function phrases() {", "function phraseSet(")
    check("Journey.card" not in phrases and "Travel.card" not in phrases,
          "the adult Sports and Travel journeys still sit in a child's sentence list")
    # the stage select: Persian name, English gloss, a count and no band code
    wq = block("function renderMap(body) {", "function renderWorld(body) {")
    check("wqworld-en" in wq, "a stage-select card does not show its English name at all")
    check("world.level" not in wq, "a stage-select card still shows a CEFR band code")
    check("faNum(" in wq, "a stage-select card still counts in Latin digits")
    check("world.blurb_fa" in wq, "a stage-select card still explains itself only in English")
    wqw = block("function renderWorld(body) {", "function startStage(")
    check("stage.title_fa" in wqw and "wqstage-en" in wqw,
          "a stage row is not Persian-first")
    check("stage.level" not in wqw, "a stage row still shows a CEFR band code")
    # the adventure: no band code in the rank bar, Persian mission names
    check("rank.cefr" not in src.split("function bar(i)")[1][:1400],
          "the adventure still prints a CEFR band over a child's mission list")
    check("m.title_fa || m.title_en" in src, "a mission stone is not Persian-first")

    for needle, what in (
        ("h.textContent = 'روباه می‌گوید 🦊'", "the fox card is still titled in English"),
        ("h.textContent = 'یک واژه را برگردان 🃏'", "the flip card is still titled in English"),
        ("h.textContent = 'با واژه‌ها بازی کن 🎯'", "the word game is still titled in English"),
        ("moreLabel.textContent = 'بیشتر'", "the More tile is still labelled in English"),
    ):
        check(needle in src, f"what a child reads: {what}")
    for theme in ("colors:", "animals:", "hello:", "days:"):
        check(theme in src, f"the starter art has nothing for {theme.rstrip(':')}")
    check("b.classList.add('kschip');" in src, "a kid starter is still a plain chip")
    check("sub.textContent = fa" in src, "a kid starter hides its Persian label")
    check("sub.dir = 'rtl'" in src, "the starter's Persian is not marked right-to-left")

    # and the cards are big enough for a child's finger
    for selector, need in (("body.kids .kchip", 40), ("body.kids .kschip", 80)):
        at = src.find(selector)
        check(at >= 0, f"{selector} has no rule, so its size is whatever falls out")
        if at < 0:
            continue
        rule = src[at:at + 420]
        sizes = [int(m) for m in re.findall(r"(?:min-height|height|width): (\d+)px", rule)]
        check(bool(sizes) and max(sizes) >= need, f"{selector} is smaller than {need}px")
    check("body.kids .kchip:focus-visible" in src,
          "the answer cards show no focus ring")

    # ---- the words must sit on paper, not on a window ---------------------
    # The app's wallpaper is behind the whole shell. A translucent bubble, or a
    # frosted one, let the fox and the wordmark show through the middle of the
    # transcript and smeared them into the space the words occupy - the blot a
    # child reported. So: an opaque column, an opaque bubble, and no glass.
    chat_rule = src[src.index("body.kids #chat {"):src.index("body.kids #chat {") + 900]
    check("background-color: #ffe9cb" in chat_rule,
          "the kids chat column is still see-through, so the wallpaper shows")
    bot_at = src.index("body.kids .msg.bot {")
    bot_rule = src[bot_at:src.index("}", src.index("border-inline-start", bot_at))]
    check("backdrop-filter: none" in bot_rule and "-webkit-backdrop-filter: none" in bot_rule,
          "a kid's answer bubble is frosted, which blurs the wallpaper into the text")
    check("rgba(" not in bot_rule.split("background:", 1)[1].split(";", 1)[0],
          "a kid's answer bubble is still translucent over the wallpaper")
    check("body.kids .kschip:focus-visible" in src,
          "the starter cards show no focus ring")

def check_offline(src):
    build = BUILD.read_text(encoding="utf-8")
    check('"kids.json"' in build, "kids.json is not in the APK's data list")
    check("Kids.says(text, reply)" in build,
          "the offline engine does not wrap its reply for children")
    check((BUNDLE / "data/kids.json").exists(),
          "the APK bundle has no kids.json - run build_apk_ui.py")
    page = (BUNDLE / "index.html")
    if page.exists():
        html = page.read_text(encoding="utf-8")
        check('id="kpanel"' in html and "Kids.says(text, reply)" in html,
              "the built page has no kids layer")
    check('self.path.startswith("/api/kids")' in src,
          "the server does not serve the kid bank")


def check_adults_untouched(src):
    check("Experience.kids()" in src,
          "the band is never read")
    # The four adult views still have their boot-time content: the hooks only
    # take over when the band is kids, so nothing here can empty an adult panel.
    for pop in ("getElementById('domains')", "getElementById('gtopics')",
                "loadJSON('books')", "/api/vocabulary"):
        check(pop in src, f"{pop} is gone from the adult page")
    check("const STARTERS = [" in src, "the adult starter chips are gone")
    check("let WELCOME" in src or "const WELCOME" in src,
          "the adult opening message is gone")
    check("America" in src or "American" in src, "the American English standard is not stated")


def check_paper_and_quest(src):
    """The page is cream, and the adventure opens with one obvious next step."""
    # White paper is the adult surface; a child's page is warm. The token is
    # where that decision lives, so the check reads it rather than a comment.
    check("--k-surface: #ffeccd" in src,
          "the kids surface token is white again instead of cream")
    check("--k-bg: #f8dcb4" in src, "the kids page background is not the apricot token")
    # A map of six places is a world, not an instruction: the panel above it
    # has to say the next mission with one button and a reason when it is shut.
    check("'hqw-next'" in src, "the hero quest has no next-quest card")
    check("'hqw-next-go'" in src, "the next-quest card has no play button")
    check("'hqw-stone' +" in src and "'n', String(k + 1)" in src,
          "missions are chips again instead of numbered rows with stars")
    check("hqw-next-fox" in src, "the mascot is gone from the next-quest card")
    # The loading page a child sees first: painted from the stored account in
    # the head, one picture instead of four sentences.
    check("dataset.band = 'kids'" in src,
          "the head never tells the boot screen that this is a child's device")
    check('class="boot-kid"' in src, "the kids boot screen has no picture")
    for gone in (".boot-tag", ".boot-trio", ".boot-facts", ".boot-foot", ".boot-meta"):
        check('html[data-band="kids"] ' + gone in src,
              f"the adult {gone} is still shown on a child's loading page")


def check_boot_tokens(src):
    """The child's loading page paints before the app has run.

    Its palette hangs off body.kids, which the app adds after the first paint -
    and a var() that resolves to nothing invalidates the declaration, which for
    a background means no background: the page showed through the overlay until
    the class landed. The fix is a copy of the tokens on <html>, which the head
    marks before the first paint, so the copy has to exist and has to cover the
    tokens that block reads.
    """
    if 'html[data-band="kids"] {' not in src:
        problems.append("the loading page has no tokens before the body has the class")
        return
    block = src.split('html[data-band="kids"] {', 1)[1].split("}", 1)[0]
    for token in ("--k-bg", "--k-surface", "--k-surface-2", "--k-boot-edge",
                  "--k-boot-foot", "--k-ink"):
        check(f"{token}:" in block,
              f"the first-paint palette declares {token}")


def check_cheer(src):
    """The cheer system rewards a child, so it has to be quiet when asked.

    Three things are worth a check and none of them are caught by running the
    page: that every celebration is gated behind the calm class (a child who
    switched motion off was promised no motion), that the confetti animates
    transform and opacity only rather than layout, and that the things being
    thrown take their colours from the palette rather than a literal.
    """
    marker = "const Cheer = (() => {"
    if marker not in src:
        problems.append("the cheer module is missing from the page")
        return
    start = src.index(marker)
    end = src.find("\nconst Kids = ", start)
    body = src[start:end if end > 0 else start + 20000]

    check("document.body.classList.contains('kids-calm')" in body,
          "the cheer module does not check calm mode")
    check("body.kids-calm .kcheer-layer" in src,
          "calm mode does not hide the confetti layer")
    check("@keyframes kConfetti" in src, "the confetti keyframes are missing")
    check("transform" in src[src.index("@keyframes kConfetti"):][:300],
          "the confetti keyframes should animate transform")

    import re
    hexes = re.findall(r"#[0-9a-fA-F]{3,6}\b", body)
    check(not hexes, f"the cheer module hardcodes colours: {hexes[:3]}")

    fired = src.count("Cheer.from(") + src.count("Cheer.win(")
    check(fired >= 8, f"only {fired} places in the kids app fire a cheer")


def check_crossword(src):
    """The crossword is hardcoded, so its data has to be checked as data.

    A puzzle here is a grid, a list of entries and a table of cells the page
    reads without any engine behind it. If the letter in an entry and the
    letter in the cell it covers ever disagree, a child types the right word
    and the board never turns green - there is no server to notice and no
    runtime check that would catch it. So the check is done here, on the
    literal that ships.
    """
    marker = "const CW_DATA = "
    if marker not in src:
        problems.append("the crossword data is missing from the page")
        return
    try:
        start = src.index(marker) + len(marker)
        raw = src[start:src.index(";\n", start)]
        data = json.loads(raw)
    except Exception as exc:
        problems.append(f"the crossword data is not valid JSON: {exc}")
        return

    check(len(data) == 3, f"the crossword should have 3 worlds, found {len(data)}")
    stages = 0
    words = 0
    for world in data:
        for key in ("id", "en", "fa", "e", "stages"):
            check(bool(world.get(key)), f"a crossword world is missing {key}")
        for stage in world["stages"]:
            stages += 1
            rows, cols = stage["rows"], stage["cols"]
            check(3 <= rows <= 8 and 3 <= cols <= 8,
                  f"{stage['t']} is {rows}x{cols}; a child's board should be 3-8")
            cells = {}
            for s in stage["cells"]:
                r, c, ch = s.split(":")
                cells[(int(r), int(c))] = ch
            check(len(stage["entries"]) >= 3, f"{stage['t']} has fewer than 3 words")
            for e in stage["entries"]:
                words += 1
                answer = e["a"]
                check(answer.isalpha() and answer.isupper(),
                      f"{stage['t']}: {answer} is not a plain capitalised word")
                check(3 <= len(answer) <= 6,
                      f"{stage['t']}: {answer} is {len(answer)} letters, too long for the board")
                check(e["d"] in ("across", "down"), f"{stage['t']}: {answer} has no direction")
                check(bool(e.get("e")) and bool(e.get("q")),
                      f"{stage['t']}: {answer} has no picture or English clue")
                fa = e.get("f") or ""
                check(any("\u0600" <= ch <= "\u06ff" for ch in fa),
                      f"{stage['t']}: {answer} has no Persian clue")
                for i, ch in enumerate(answer):
                    r = e["r"] + (i if e["d"] == "down" else 0)
                    c = e["c"] + (i if e["d"] == "across" else 0)
                    got = cells.get((r, c))
                    check(got == ch,
                          f"{stage['t']}: {answer} expects {ch} at {r},{c} but the board has {got}")
                check((e["r"], e["c"]) in cells,
                      f"{stage['t']}: {answer} starts on a cell that is not on the board")

    check(stages >= 6, f"the crossword should offer at least 6 stages, found {stages}")
    stats["crossword_stages"] = stages
    stats["crossword_words"] = words

    for need in ('id="cwtoggle"', 'id="cwpanel"', 'cwpanel: () => ',
                 "Crossword.open()", "fluentify.kids.crossword"):
        check(need in src, f"the crossword is not wired: {need} is missing")

    check_crossword_feel(src)


def check_crossword_feel(src):
    """Is the crossword a toy as well as a puzzle, and can a child start alone?

    The numbers above make the board solvable. This asks the other half: that a
    character answers the child, that the rules are taught by doing, that every
    word shows its picture before it is spelled, and that the movement is
    squash and stretch - the two principles that make a game read as alive -
    without any of it becoming a wall between a child and the letters.
    """
    import re
    try:
        css = src[src.index("/* ---- the coach, the scene and the juice"):]
        css = css[:css.index("/* ---- Word Quest: the letter puzzle")]
    except ValueError:
        check(False, "the crossword's feel block has no markers")
        return
    module = src[src.index("const Crossword = (() => {"):]
    module = module[:module.index("\nconst WordQuest = (() => {")]

    # --- the coach: a fox that reacts, and one line at a time
    for needle, what in (
        ("body.kids .cw-fox", "the fox has no style"),
        ("body.kids .cw-say", "the fox has no speech bubble"),
        ("body.kids .cw-coach", "the coach row has no style"),
    ):
        check(needle in css, f"crossword feel: {what}")
    for needle, what in (
        ("function coachLine()", "the fox says nothing"),
        ("function coach()", "the fox is never built"),
        ("brand/kids-fox-face.png", "the fox has no face"),
        ("' happy'", "the fox never looks pleased"),
        ("' oops'", "the fox never reacts to a wrong word"),
    ):
        check(needle in module, f"crossword feel: {what}")
    check("view.mood = 'happy'" in module and "view.mood = 'oops'" in module,
          "crossword feel: the mood is set nowhere")
    check("view.mood = 'win'" in module, "crossword feel: the fox does not celebrate")

    # --- squash and stretch, really: two different scales in one transform
    def squashy(name):
        m = re.search(r"@keyframes " + name + r"\s*\{(.*?)\n  \}", css, re.S)
        if not m:
            return False
        return bool(re.search(r"scale\(\s*([\d.]+)\s*,\s*([\d.]+)\s*\)", m.group(1))
                    and re.search(r"scale\(\s*([\d.]+)\s*,\s*([\d.]+)\s*\)", m.group(1))
                    and any(abs(float(a) - float(b)) >= 0.08
                            for a, b in re.findall(r"scale\(\s*([\d.]+)\s*,\s*([\d.]+)\s*\)", m.group(1))))
    for name in ("cwSquash", "cwStretch", "cwPop", "cwIdle"):
        check(squashy(name), f"crossword feel: @keyframes {name} is not squash-and-stretch")

    # --- the world, the words, the walkthrough, the peek
    for needle, what in (
        ("body.kids .cw-scene", "the stage has no scene"),
        ("@keyframes cwDrift", "the scene does not drift"),
        ("body.kids .cw-target", "the stage has no picture strip"),
        ("body.kids .cw-onboard", "there is no walkthrough"),
        ("body.kids .cw-peek-card", "the peek card has no style"),
    ):
        check(needle in css, f"crossword feel: {what}")
    for needle, what in (
        ("function scene()", "the scene is never built"),
        ("aria-hidden=\"true\">' + ", "the scene is read out as content"),
        ("function targets()", "the picture strip is never built"),
        ('data-act="entry"', "a picture cannot be tapped to choose its word"),
        ("function onboard()", "the walkthrough is never built"),
        ('data-act="ob-next"', "the walkthrough cannot be advanced"),
        ('data-act="ob-skip"', "the walkthrough cannot be skipped"),
        ("function peek()", "there is no peek hint"),
        ('data-act="peek"', "the peek hint has no button"),
    ):
        check(needle in module, f"crossword feel: {what}")
    check(module.count("{e: '") >= 3, "crossword feel: the walkthrough has fewer than three steps")
    check("store.seen[wid] ? 3 : 0" in module,
          "crossword feel: the walkthrough is not remembered, or is forced on every stage")
    check("store.seen[view.wid] = 1" in module,
          "crossword feel: finishing the walkthrough is not remembered")

    # --- the help must cost what it says it costs, and stay bilingual
    for needle in ("−۱ ستاره", "show me the word"):
        check(needle in module, f"crossword feel: the hint button does not say what it costs ({needle})")
    peek = module.split("function peek()", 1)[1].split("\n  }", 1)[0]
    check("view.hints += 1" in peek, "crossword feel: the peek hint is free")
    check("function helpTarget()" in module and "helpTarget()" in peek
          and "helpTarget()" in module.split("function hint()", 1)[1].split("\n  }", 1)[0],
          "crossword feel: a hint spent on an already-solved word would be a star thrown away")

    # --- juice that must never become an obstacle
    for needle, what in (
        ("body.kids .cw-cell .cw-in", "a landing letter does not pop"),
        ("body.kids .cw-board.wrong", "a wrong word does not move the board"),
        ("body.kids .cw-key:active", "a key does not squash under the thumb"),
    ):
        # the key's own press state lives in the board block above the feel
        # block, so these two are looked for in the page, not in the slice
        check(needle in src, f"crossword feel: {what}")
    motion = css[css.index("@media (prefers-reduced-motion: reduce)"):]
    for needle, what in (
        ("body.kids .cw-fox", "the fox keeps moving"),
        ("body.kids .cw-scene i", "the world keeps drifting"),
        ("body.kids .cw-board.wrong", "the board keeps objecting"),
        ("body.kids .cw-cell .cw-in", "letters keep popping"),
    ):
        check(needle in motion, f"crossword feel: under reduced motion, {what}")

    # --- thumbs, not cursors
    ob = css.split("body.kids .cw-ob-btn {", 1)[1].split("}", 1)[0]
    m = re.search(r"min-height: (\d+)px", ob)
    check(bool(m) and int(m.group(1)) >= 44,
          "crossword feel: a walkthrough button is too small to hit")
    tgt = css.split("body.kids .cw-target {", 1)[1].split("}", 1)[0]
    m = re.search(r"min-width: (\d+)px", tgt)
    check(bool(m) and int(m.group(1)) >= 48,
          "crossword feel: a picture in the strip is too small to tap")


def main():
    if not KIDS.exists():
        print("FAIL  kids.json does not exist")
        return 1
    data = json.loads(KIDS.read_text(encoding="utf-8"))
    src = WEBAPP.read_text(encoding="utf-8")

    check_paper_and_quest(src)

    print("the kid bank")
    check_words(data)
    check_word_pictures(data, src)
    check_grammar(data)
    check_grammar_comics(src, data)
    check_stories(data)
    check_reading(data)
    check_reading_book(src, data)
    check_story_book(src, data)
    check_listening(data)
    check_phrases(data)
    check_chat(data)
    check_safety_scan(data)
    check(data.get("version") == 1, "kids.json is not the versioned file the page reads")

    print("\nthe classification")
    check_classification(src)
    check_signup(src)

    print("\nthe kids layer")
    check_kids_layer(src)
    check_chat_wiring(src)
    check_offline(src)

    print("\nthe adult app")
    check_adults_untouched(src)
    check_crossword(src)
    check_cheer(src)
    check_boot_tokens(src)

    if problems:
        print()
        for p in problems[:40]:
            print("FAIL  " + p)
        if len(problems) > 40:
            print(f"      ... and {len(problems) - 40} more")
        print(f"\nFAIL  {len(problems)} problem(s) in the kids experience")
        return 1

    print(f"\nPASS  {stats.get('words')} kid words in 7 themes, "
          f"{stats.get('grammar')} mini lessons with {stats.get('quiz')} quiz items, "
          f"4 stories, 4 passages turned into {stats.get('book pages')} book leaves "
          "with a picture each, "
          f"{stats.get('story pages')} drawn story pages in four books, "
          "5 listening clips, 5 phrase sets and a "
          "kid-safe chat whose own bank holds 67 words, 18 everyday "
          "sentences, the numbers and the week - each with a Persian "
          "pronunciation line; ages below 15 are classified on the page and "
          "in the APK, and every kids rule, panel and reply is behind that band")
    return 0


if __name__ == "__main__":
    sys.exit(main())
