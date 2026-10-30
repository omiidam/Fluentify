#!/usr/bin/env python3
"""Generates the offline Android UI (assets/www/index.html) from webapp.py.

The Python preview talks to /api/chat, /api/grammar, /api/phrases and
/api/vocabulary. The APK has no server, so those four calls are rewritten to
use the bundled bot.js engine and the JSON files in assets/www/data.
Keeping one source of truth means the desktop preview and the app never drift.
"""

import hashlib
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "android/app/src/main/assets/www/index.html"
DATA = OUT.parent / "data"

# Every file the offline boot Promise.all() asks for. If one is missing the
# whole bundle fails to start with "could not load the language data", which
# is a blank app and a confusing error - so the list is declared here, once,
# next to the code that fetches them, and checked on every build.
BUNDLED_DATA = [
    "memory.json", "glossary.json", "grammar.json", "phrases.json",
    "jokes.json", "listening.json", "phonetics.json", "word_arch.json",
    "distinctions.json", "idioms.json", "corrections.json",
    "stt.json", "bbc_6min.json", "register.json", "foxes.json",
    "daily.json",
]

# Files a panel fetches the first time it is opened, not at boot. The library
# reads books.json when the Books panel opens, so a copy here is what makes
# lesson words available offline without costing every start-up the read.
LAZY_DATA = [
    "books.json",
]

src = (ROOT / "webapp.py").read_text(encoding="utf-8")
html = re.search(r'HTML_TEMPLATE = r"""(.*?)"""', src, re.S).group(1)

def sub(text: str, old: str, new: str, what: str,
        count: int = -1, required: bool = True) -> str:
    """html.replace, but it refuses to fail quietly.

    str.replace returns the input unchanged when the pattern is absent and
    raises nothing, so an edit to webapp.py that moves one of these anchors
    silently ships an APK with that piece missing. It happened: dropping a
    boot call made the data-loading rewrite a no-op and the offline app shipped
    with no engine, no data and no panels, while the build still passed.
    """
    if old not in text:
        if required:
            sys.exit(
                f"build_apk_ui: cannot rewrite {what}\n"
                f"  the offline build and webapp.py have drifted apart - the "
                f"pattern this step replaces no longer exists in the page.\n"
                f"  expected to find: {old[:110]!r}"
            )
        return text
    return text.replace(old, new, count)


# the offline build has the config file in its own data/ folder, so the marker
# becomes a plain fetch-free assignment filled from that file at boot
html = sub(html, "/*__STT_CONFIG__*/", "", "the STT config marker")

# The corrector is server-side now. GEC-BART Base is a 558 MB BART and runs in
# the Python service, so no weights ship in the APK - what ships is the rule
# engine bot.js already carries. The pen button asks the backend when one was
# configured at build time and falls back to those rules when it cannot.
GEC_API = os.environ.get("FLUENTIFY_GEC_API", "").strip().rstrip("/")
if GEC_API and not GEC_API.startswith("https://"):
    sys.exit("build_apk_ui: FLUENTIFY_GEC_API must be the public https:// backend")
if any(h in GEC_API for h in ("127.0.0.1", "localhost", "10.0.2.2")):
    sys.exit("build_apk_ui: FLUENTIFY_GEC_API is a loopback address - the phone "
             "cannot reach this machine, so leave it unset to use the rules")
# A model in the bundle is a 558 MB app and a correction that runs on the
# phone. Both are wrong for this build, and it should fail here rather than in
# an APK nobody inspects.
_stray = [p.relative_to(ROOT) for p in
          (ROOT / "android/app/src/main/assets/www").rglob("*")
          if p.suffix in (".onnx", ".safetensors", ".wasm") or p.name == "pytorch_model.bin"]
if _stray:
    sys.exit(f"build_apk_ui: model weights are in the offline bundle: {_stray[:3]}")

# 1) send(): call the local engine instead of the HTTP endpoint
#
# Matched structurally rather than as an exact copy of the web body, which
# used to break the build on any edit to the catch block in webapp.py while
# leaving the offline copy silently out of date.
m = re.search(r"(  showTyping\(\);\n  try \{\n)(.*?)(\n  \} catch \(e\) \{\n)(.*?)(\n  \}\n)", html, re.S)
if not m:
    sys.exit("could not find the send() try/catch in the template")

engine = """    await sleep(160);                       // a beat so the typing dots show
    // the dictionary is 335 shards, so only the ones this message can touch
    // are read - and they are read before respond(), which is synchronous
    await bot.loadLexiconFor(text);
    const reply = bot.respond(text);
    hideTyping();
    add(reply, 'bot');
    // finishing a practice unlocks that topic's exam — refresh the panel so
    // the 🎓 button stops showing the lock
    if (/exam is now open|آزمون باز شد/i.test(reply) &&
        document.getElementById('gpanel').classList.contains('open')) {
      loadGrammar();
    }"""

# The offline app has no server to lose, so it reports the engine's own error
# rather than "is the server running". Everything else about the failure path
# is identical to the web build on purpose: nothing is charged, and the words
# go back in the box.
failure = """    hideTyping();
    // Nothing was taught, so nothing should have been charged. The seed is
    // added before the request to keep the meter moving while it is in flight;
    // a message that never produced a reply must not cost one of the fifty.
    Seed.add(-1);

    // The composer was already cleared, so the words are gone from the screen
    // unless we put them back.
    input.value = text;
    add('⚠️ Something went wrong — ' + e.message +
        `\\nYour message is back in the box, and none of your ${SEED_GOAL} ` +
        'daily messages was used.\\nپیام شما به کادر برگشت و از سهم امروز کم نشد.',
        'bot', {err: true});"""

html = html[:m.start()] + m.group(1) + engine + m.group(3) + failure + m.group(5) + html[m.end():]

# 2) the three panels: read from the bundled JSON instead of the API
for fn, api, expr in [
    ("loadGrammar", "/api/grammar", "grammarTopics"),
    ("loadPhrases", "/api/phrases", "phraseTopics"),
    ("loadVocabulary", "/api/vocabulary", "vocabGroups"),
]:
    old = f"""    const r = await fetch('{api}');
    const topics = await r.json();"""
    # each loader names its variable differently; handle generically below
    del old, fn, api, expr

html = sub(
    html,
    """    const r = await fetch('/api/grammar');
    const topics = await r.json();""",
    """    const topics = grammarTopics;""",
    "loadGrammar's fetch")
html = sub(
    html,
    """    const r = await fetch('/api/phrases');
    const topics = await r.json();""",
    """    const topics = phraseTopics;""",
    "loadPhrases's fetch")
html = sub(
    html,
    """    const r = await fetch('/api/vocabulary');
    const groups = await r.json();""",
    """    const groups = vocabGroups;""",
    "loadVocabulary's fetch")
html = sub(
    html,
    """    const r = await fetch('/api/listening');
    const levels = await r.json();""",
    """    const levels = listeningLevels;""",
    "loadListening's fetch")
html = sub(
    html,
    """    const r = await fetch('/api/phonetics');
    sections = await r.json();""",
    """    sections = phoneticSections;""",
    "loadPhonetics's fetch")
# every occurrence, not just the first: loadWordArch has a second call site
html = sub(
    html,
    """    const r = await fetch('/api/wordarch');
    const bands = await r.json();""",
    """    const bands = await wordArchBands();""",
    "loadWordArch's fetch")
# bbcDoc() is the cached reader, not a loader of its own: the fetch lives on
# one line and loadBBC() only awaits it. Rewritten where it actually is.
html = sub(
    html,
    """  bbcDocCache ||= fetch('/api/bbc').then((r) => r.json());""",
    """  bbcDocCache ||= bbcCatalogue();""",
    "bbcDoc's fetch")

# The Object.assign below the rewritten fetch is left alone on purpose: it is
# what fills the offline cache.

# 2b) the emoji picker's data loader: data/*.json instead of /api/emojis
#
# The web build has no data/ directory, so it reads a file by name over the
# API; the offline page has the directory and no server.
html = sub(
    html,
    """const _json = {};
const loadJSON = (name) => (_json[name] ||= fetch('/api/' + name).then((r) => {
  if (!r.ok) throw new Error(name + ' could not be read (HTTP ' + r.status + ')');
  return r.json();
}));""",
    """const _json = {};
const loadJSON = (name) => (_json[name] ||= fetch('data/' + name + '.json').then((r) => {
  if (!r.ok) throw new Error(name + '.json could not be read (HTTP ' + r.status + ')');
  return r.json();
}));""",
    "the emoji data loader")

# 3) boot: read every bundled file, build the engine, then fill the panels
#
# The web build boots on one line - loadAllSections(), behind a loading screen
# that is held for five seconds whatever the machine does. The offline page
# boots on the same call: the only difference is where the sections' contents
# come from. They are not fetched from /api/* any more (the rewrites above), so
# the data has to come out of assets/www/data and the engine has to be built
# from it before loadAllSections() has anything to draw.
#
# The anchor is that one boot line, matched in webapp.py and not in any of the
# text the rewrites above produce. An anchor built out of rewritten text is an
# anchor that vanishes the day a rewrite changes shape, and this build has
# already shipped once because an earlier anchor stopped matching.
_offline_boot = "loadAllSections().finally(() => Boot.ready());"

_offline_block = r"""/* offline boot: read every bundled file, build the engine, and then run the
   web build's own loadAllSections() behind the loading screen.

   Every file is read here, including bbc_6min.json and word_arch.json. They
   used to be deferred to the first tap on Listen or Sentences, which was a
   sensible idea before the loading screen existed and is a pointless one now:
   the screen is held for five seconds regardless, so reading 1.4 MB behind it
   costs the user nothing and saves the first tap a stall. It also means the
   progress bar counts real reads rather than idling at one number. */
let bot = null, grammarTopics, phraseTopics, vocabGroups, listeningLevels,
    phoneticSections;
/* Filled by the boot below, read by the two helpers the panel loaders call.
   Plain values rather than promises: by the time a loader can reach them the
   files are already in hand, and a promise here would only invite a load
   before the boot has finished handing them over. */
let _bbc = null, _bands = null;
const bbcCatalogue = () => _bbc;
const wordArchBands = () => _bands;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
/* loadJSON, _json and the emoji picker's cache live in the page script above,
   rewritten in step 2b to read data/*.json. Declaring them again here would be
   two top-level consts of the same name in one script - a SyntaxError that
   takes the whole page down. */

/* The eleven files the engine is built from, then the four that only fill the
   UI. Every name here is the name of the file it came from, and the same
   names, in the same order, are destructured on the other side of the .then.
   That is not a style preference: tools/check_ui.py compares the two lists,
   because a dropped name in the destructure shifts every name after it by one
   and the engine then builds out of the wrong files without saying so. */
Promise.all([loadJSON('memory'), loadJSON('glossary'), loadJSON('grammar'),
             loadJSON('phrases'), loadJSON('jokes'), loadJSON('listening'),
             loadJSON('phonetics'), loadJSON('distinctions'), loadJSON('idioms'),
             loadJSON('corrections'), loadJSON('stt'), loadJSON('register'),
             loadJSON('foxes'), loadJSON('bbc_6min'), loadJSON('word_arch'),
             loadJSON('daily')])
  .then(([memory, glossary, grammar, phrases, jokes, listening, phonetics,
          distinctions, idioms, corrections, stt, register, foxes, bbc_6min,
          word_arch, daily]) => {
    // every file the engine can read must be handed to it, or a section
    // silently comes back empty offline
    bot = new Fluentify({memory, glossary, grammar, phrases, jokes, listening,
                         phonetics, distinctions, idioms, corrections, register,
                         daily});

    // The Listen panel's catalogue, links only: no transcript is ever served.
    _bbc = bbc_6min;

    // The Sentences panel's word chips, banded by level. Built here rather
    // than on first open so that open is a repaint and nothing else.
    _bands = (() => {
      const bands = {};
      Object.entries(word_arch.words).forEach(([, e]) => {
        (bands[e.level || 'A1'] = bands[e.level || 'A1'] || [])
          .push({en: e.en, fa: e.fa, pos: e.pos, forms: e.forms,
                 level: e.level, domains: e.domains || []});
      });
      Object.values(bands).forEach((v) => v.sort((a, b) => (a.en < b.en ? -1 : 1)));
      return bands;
    })();

    listeningLevels = listening.levels.map((lv) => ({
      id: lv.id, title_en: lv.title.en, title_fa: lv.title.fa,
      blurb_en: lv.blurb.en, blurb_fa: lv.blurb.fa, sentences: lv.sentences,
    }));
    phoneticSections = phonetics.sections.map((s) => ({
      id: s.id, icon: s.icon || '🔊', level: s.level || 'A1',
      title_en: s.title.en, title_fa: s.title.fa,
      blurb_en: s.blurb.en,
      tip_en: (s.tip || {}).en || '',
      groups: (s.groups || []).map((g) => ({
        name_en: g.name.en, rows: g.rows || [],
      })),
    }));

    // Use the engine's own unwrapped maps so panel data always matches the
    // structures bot.js actually uses.
    grammarTopics = Object.entries(bot.grammar).map(([id, t]) => ({
      id, title_en: t.title.en, title_fa: t.title.fa, level: t.level || '',
      query_en: t.keywords.en[0],
      practice_en: t.keywords.en[0] + ' exercises',
      exam_en: t.keywords.en[0] + ' exam',
      practice_n: (t.practice || []).length,
      exam_n: (t.exam || []).length,
    }));
    phraseTopics = Object.values(bot.phrases).map((t) => ({
      title_en: t.title.en, title_fa: t.title.fa, level: t.level || 'A1',
      query: t.keywords.en[0], count: t.phrases.length,
    }));
    vocabGroups = bot.glossaryGroups.map((g) => ({
      en: g.en, fa: g.fa,
      items: g.domains.map((id) => {
        const d = bot.glossary[id];
        return {
          id, title_en: d.list_label.en, title_fa: d.list_label.fa,
          level: d.level || 'A1',
          query_en: d.keywords.en[0], query_fa: d.keywords.fa[0],
          count: d.words.length,
        };
      }),
    }));

    // speech-to-text settings, straight from the same stt.json the CLI reads.
    // STT.cfg is read once, when STT is declared - which is above this block -
    // so setting window.STT_CONFIG alone would leave the offline app reading
    // an empty config and falling back to the browser's defaults.
    window.STT_CONFIG = stt;
    STT.cfg = stt;

    /* Every section, now, while the loading screen is up. The web build does
       exactly this and the offline build used to do its own smaller version
       of it: one boot, one place to look when a section comes back empty. */
    return loadAllSections();
  })
  .then(() => Boot.ready())
  .catch((e) => {
    add('⚠️ could not load the language data: ' + e.message, 'bot', {err: true});
    // The screen still has to come down. A caught rejection is not an
    // unhandled one, so nothing else will dismiss it, and the ceiling timer
    // is twenty seconds away.
    Boot.ready();
  });"""
html = sub(html, _offline_boot, _offline_block, "the offline boot block")

# Nothing else is needed to make the page tail work: it no longer calls the
# panel loaders itself, because loadAllSections() does and the offline page
# reuses that same call.

# 4) load bot.js before the page script
assert "\n<script>\n" in html
# bot.js gets a content hash. Without one the browser keeps serving the
# previous engine after a rebuild, and the offline app silently runs old
# behaviour against new data - which is exactly how the register feature
# looked absent on the offline bundle when the file on disk plainly had it.
_bot_file = ROOT / "android/app/src/main/assets/www/bot.js"
_bot_sha = hashlib.sha1(_bot_file.read_bytes()).hexdigest()[:8] \
    if _bot_file.exists() else "dev"
html = sub(html, "\n<script>\n",
           f'\n<script src="bot.js?v={_bot_sha}"></script>\n<script>\n',
           "the inline script tag", 1)

OUT.parent.mkdir(parents=True, exist_ok=True)
# The offline page has no server, so the corrector's fetch becomes one function
# that tries a configured backend and otherwise answers from the rules. The
# button keeps its behaviour: it never charges a daily message and never edits
# the conversation.
CORRECTOR = r'''/* Correction. The app holds no model: the corrector is 558 MB and runs on the
   server. If a backend was configured at build time (FLUENTIFY_GEC_API) the
   sentence goes there; otherwise the rule engine bot.js already carries
   answers, so the pen still works with the phone in airplane mode. */
const GEC_API = '__GEC_API__';
const localCorrect = (text) => {
  const problems = bot.checkGrammar(text);
  const whole = problems.map((p) => p.whole).find(Boolean);
  if (!whole) {
    return {available: true, input: text, output: text, changed: false,
            refused: null, local: true};
  }
  const out = whole.charAt(0).toUpperCase() + whole.slice(1);
  return {available: true, input: text, output: out, refused: null, local: true,
          changed: out.toLowerCase() !== text.toLowerCase()};
};
async function correctSentence(text) {
  if (GEC_API) {
    try {
      const ctl = new AbortController();
      const timer = setTimeout(() => ctl.abort(), 8000);
      const r = await fetch(GEC_API + '/api/correct?message=' + encodeURIComponent(text),
                            {signal: ctl.signal});
      clearTimeout(timer);
      const data = await r.json();
      if (data && data.available !== false) return data;
    } catch (e) { /* offline, or the backend is down: the rules answer */ }
  }
  return localCorrect(text);
}

'''
html = sub(html, "async function checkEnglish(text) {",
           CORRECTOR.replace("__GEC_API__", GEC_API) + "async function checkEnglish(text) {",
           "the checkEnglish declaration")
html = sub(html,
           "    const r = await fetch('/api/correct?message=' + encodeURIComponent(text));\n"
           "    data = await r.json();",
           "    data = await correctSentence(text);",
           "the corrector's server call")

OUT.write_text(html, encoding="utf-8")
print("wrote", OUT, len(html), "chars")

# ---------------------------------------------------------------------------
# sync the data files
# ---------------------------------------------------------------------------
DATA.mkdir(parents=True, exist_ok=True)
missing = []
for name in BUNDLED_DATA + LAZY_DATA:
    src = ROOT / name
    dest = DATA / name
    if not src.exists():
        missing.append(name)
        continue
    shutil.copyfile(src, dest)
print(f"synced {len(BUNDLED_DATA) + len(LAZY_DATA) - len(missing)}"
      f"/{len(BUNDLED_DATA) + len(LAZY_DATA)} data files -> {DATA}")
if missing:
    for name in missing:
        print(f"  ! {name} is missing from the repository root")
    print("  the APK will fail to start until these exist "
          "(tools/fetch_bbc_6min.py builds bbc_6min.json)")
    raise SystemExit(1)

# ---------------------------------------------------------------------------
# sync the dictionary
# ---------------------------------------------------------------------------
# The dictionary ships as shards under data/lex/, next to the other data files,
# because that is where the engine's loader looks: it asks for one shard per
# word of the current message and caches what it read, so the app never parses
# 12 MB at boot and a lookup costs one small file. Every shard is copied - a
# missing one is not a crash, it is a word that silently has no meaning.
LEX_SRC = ROOT / "lexicon"
LEX_DEST = DATA / "lex"
shards = sorted(LEX_SRC.glob("*.json")) if LEX_SRC.exists() else []
if not shards:
    raise SystemExit("build_apk_ui: lexicon/ is empty - run tools/build_lexicon.py")
LEX_DEST.mkdir(parents=True, exist_ok=True)
for stale in LEX_DEST.glob("*.json"):
    stale.unlink()
for shard in shards:
    shutil.copyfile(shard, LEX_DEST / shard.name)
print(f"synced {len(shards)} dictionary shards "
      f"({sum(s.stat().st_size for s in shards) / (1024*1024):.1f} MB) -> {LEX_DEST}")



# the offline page must not reference a server endpoint
leftovers = re.findall(r"fetch\(\s*['\"](/api/[^'\"]+)", html)
if leftovers:
    raise SystemExit("offline page still calls the server: " + ", ".join(set(leftovers)))

# ---------------------------------------------------------------------------
# parse the page before shipping it
# ---------------------------------------------------------------------------
# sync the two faces the page is set in. They live next to index.html so the
# relative url() in @font-face resolves over file:// as well as over http, and
# the offline app keeps the theme's typography instead of falling back to
# whatever the phone happens to ship.
FONT_DIR = ROOT / "fonts"
# The two licences travel with the files: both faces are SIL OFL, and the
# terms require the licence to ship wherever the font is redistributed.
FONTS = ["baloo2-latin.woff2", "kalam-latin.woff2",
         "OFL-baloo2.txt", "OFL-kalam.txt"]
missing_fonts = [f for f in FONTS if not (FONT_DIR / f).exists()]
if missing_fonts:
    raise SystemExit("build_apk_ui: fonts missing from fonts/: "
                     + ", ".join(missing_fonts))
font_out = OUT.parent / "fonts"
font_out.mkdir(parents=True, exist_ok=True)
for name in FONTS:
    shutil.copyfile(FONT_DIR / name, font_out / name)
print(f"synced {len(FONTS)} font files -> {font_out}")

# ---------------------------------------------------------------------------
# the mascot
# ---------------------------------------------------------------------------
# The boot screen, the header and every message row draw brand/fox-*.png. They
# have to travel with the page for the same reason the fonts do: relative urls,
# no server. Both are produced from one source by tools/build_brand.py, so this
# only copies - a missing file is a build failure, not a mascot that quietly
# turns into a broken image inside the app.
BRAND_DIR = ROOT / "brand"
BRAND_FILES = ["fox-mark.png", "fox-face.png"]
missing_brand = [f for f in BRAND_FILES if not (BRAND_DIR / f).exists()]
if missing_brand:
    raise SystemExit("build_apk_ui: brand art missing from brand/: "
                     + ", ".join(missing_brand)
                     + " - run: python3 tools/build_brand.py")
brand_out = OUT.parent / "brand"
brand_out.mkdir(parents=True, exist_ok=True)
for name in BRAND_FILES:
    shutil.copyfile(BRAND_DIR / name, brand_out / name)
print(f"synced {len(BRAND_FILES)} brand files -> {brand_out}")

# ---------------------------------------------------------------------------
# the offline grammar engine
# ---------------------------------------------------------------------------
# The page analyses a sentence with a tagger that has to be in the APK: there
# is no server inside the app and no network to fetch one from. It sits in
# nlp/ next to index.html, and the WebView serves everything under
# assets/www through WebViewAssetLoader, so the page's relative url resolves
# inside the app exactly as it does over http. That is what makes the web
# build and the APK run the same file rather than two copies of it - and it
# needs no change to the WebView's settings or permissions.
NLP_FILE = ROOT / "nlp" / "fluentify-nlp.js"
if not NLP_FILE.exists():
    raise SystemExit("build_apk_ui: nlp/fluentify-nlp.js is missing - "
                     "run: cd nlp && npm install && npm run build")
nlp_out = OUT.parent / "nlp"
nlp_out.mkdir(parents=True, exist_ok=True)
shutil.copyfile(NLP_FILE, nlp_out / NLP_FILE.name)
# The MIT notices travel with the model: they are embedded in the bundle's
# first lines as well, and this is the readable copy for whoever opens the APK.
notices = ROOT / "nlp" / "THIRD-PARTY-NOTICES.md"
if notices.exists():
    shutil.copyfile(notices, nlp_out / "THIRD-PARTY-NOTICES.md")
print(f"synced the grammar engine ({NLP_FILE.stat().st_size / (1024*1024):.2f} MB) -> {nlp_out}")

# ---------------------------------------------------------------------------
# A duplicate top-level declaration between the page and bot.js - a `function
# esc` beside bot.js's `const esc` - is a SyntaxError that kills the entire
# inline script. The result is a silently blank app: nothing renders, nothing
# logs, and the APK builds fine. Chrome simply refuses to run the file.
#
# This exact bug shipped once, and only a real browser caught it, because the
# web build does not load bot.js and so never hit it. So the build parses the
# page now, with node, and refuses to produce an APK that cannot start.
import shutil
import subprocess

script = re.search(r"<script>\n(.*)\n</script>", html, re.S)
if not script:
    raise SystemExit("could not find the page script to parse")
# Both scripts share one global scope, so the collision only appears when
# they are checked together - which is exactly why checking the page on its
# own would have missed this.
bot_src = OUT.parent / "bot.js"
combined = ""
if bot_src.exists():
    combined += bot_src.read_text(encoding="utf-8") + "\n;"
combined += script.group(1)
check = ROOT / "tools/.cache/apk_page_check.js"
check.parent.mkdir(parents=True, exist_ok=True)
check.write_text(combined, encoding="utf-8")
if shutil.which("node"):
    parsed = subprocess.run(["node", "--check", str(check)],
                            capture_output=True, text=True)
    if parsed.returncode != 0:
        print(parsed.stderr[:2000])
        raise SystemExit(
            "the generated page is not valid JavaScript - refusing to ship an "
            "APK that cannot start. Watch for a top-level name declared twice "
            "across the page and bot.js."
        )
    print("page parses clean (node --check)")
else:
    print("node not found - skipped the page parse check")