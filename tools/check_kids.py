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
    check(len(themes) == 6, f"the word bank has {len(themes)} themes, expected 6")
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


def check_grammar(data):
    lessons = data.get("grammar") or []
    check(len(lessons) == 6, f"there are {len(lessons)} mini lessons, expected 6")
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


def check_stories(data):
    stories = data.get("stories") or []
    check(len(stories) == 3, f"there are {len(stories)} stories, expected 3")
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
    check(len(passages) == 3, f"there are {len(passages)} passages, expected 3")
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
    check(len(clips) == 4, f"there are {len(clips)} listening clips, expected 4")
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
    check(len(sets) == 4, f"there are {len(sets)} phrase sets, expected 4")
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
    dark = block.split('[data-theme="dark"] body.kids {', 1)
    check(len(dark) == 2 and "--k-bg:" in dark[1].split("}", 1)[0]
          and "--k-on-primary:" in dark[1].split("}", 1)[0],
          "the kids palette has no dark theme of its own")
    check("--surf-1:" in dark[1].split("}", 1)[0]
          and "--ink:" in dark[1].split("}", 1)[0],
          "the dark kids theme leaves the shared surface tokens light")
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
    for cls in ("kc-blue", "kc-purple", "kc-mint", "kc-sun", "kc-coral", "kc-teal"):
        check(cls in block, f"the {cls} section has no identity to draw")
    check("--k-focus:" in dark[1].split("}", 1)[0],
          "focus is not repainted for the dark kids theme")

    # One drawn icon set for the six doors. The tiles used to borrow an emoji
    # each, which is six illustrators' idea of a book in six weights and
    # palettes - the one thing a children's app cannot get away with.
    check("function kicon(name)" in src and "const KICONS = {" in src,
          "the home tiles have no icon set of their own")
    icons = src[src.index("const KICONS = {"):src.index("function kicon")]
    check(icons.count("<path") >= 6 and "viewBox" not in icons,
          "the icons are not drawn as plain paths on one grid")
    check('viewBox="0 0 24 24"' in src and 'stroke="currentColor"' in src,
          "the icons do not inherit the chip's color")
    tiles_src = src[src.index("function homeTiles"):]
    tiles_src = tiles_src[:tiles_src.index("tiles.forEach")]
    check("i.innerHTML = kicon(ico);" in src,
          "the home tiles still paint an emoji instead of the drawn set")
    check(not re.search(r"'[\U0001F300-\U0001FAFF\u2600-\u27BF]", tiles_src),
          "a home tile is back to an emoji")
    for key in ("words", "grammar", "read", "listen", "stories", "chat"):
        check(f"['{key}'," in tiles_src, f"the {key} tile has no icon of its own")

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
                   ("--k-mint-ink", "--k-mint"),
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


def main():
    if not KIDS.exists():
        print("FAIL  kids.json does not exist")
        return 1
    data = json.loads(KIDS.read_text(encoding="utf-8"))
    src = WEBAPP.read_text(encoding="utf-8")

    print("the kid bank")
    check_words(data)
    check_grammar(data)
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

    if problems:
        print()
        for p in problems[:40]:
            print("FAIL  " + p)
        if len(problems) > 40:
            print(f"      ... and {len(problems) - 40} more")
        print(f"\nFAIL  {len(problems)} problem(s) in the kids experience")
        return 1

    print(f"\nPASS  {stats.get('words')} kid words in 6 themes, "
          f"{stats.get('grammar')} mini lessons with {stats.get('quiz')} quiz items, "
          f"3 stories, 3 passages, 4 listening clips, 4 phrase sets and a "
          "kid-safe chat; ages below 15 are classified on the page and in the "
          "APK, and every kids rule, panel and reply is behind that band")
    return 0


if __name__ == "__main__":
    sys.exit(main())
