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
            check(bool(PERSIAN.search(item.get("example_fa") or "")),
                  f"{where}: the example is not translated")
    stats["words"] = total


PHOTOS = ROOT / "kids/words"


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
    from PIL import Image

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
                with Image.open(path) as im:
                    check(im.format == "JPEG", f"{word}: {img} is {im.format}, not a JPEG")
                    check(im.size[0] >= 320 and im.size[1] >= 240,
                          f"{word}: {img} is {im.size[0]}x{im.size[1]} - too small to "
                          "recognise")
            except Exception as exc:                    # a truncated file, not a crash
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
          f"4 stories, 4 passages, 5 listening clips, 5 phrase sets and a "
          "kid-safe chat; ages below 15 are classified on the page and in the "
          "APK, and every kids rule, panel and reply is behind that band")
    return 0


if __name__ == "__main__":
    sys.exit(main())
