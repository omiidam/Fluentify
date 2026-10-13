#!/usr/bin/env python3
"""Generates the offline Android UI (assets/www/index.html) from webapp.py.

The Python preview talks to /api/chat, /api/grammar, /api/phrases and
/api/vocabulary. The APK has no server, so those four calls are rewritten to
use the bundled bot.js engine and the JSON files in assets/www/data.
Keeping one source of truth means the desktop preview and the app never drift.
"""

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
    "stt.json", "bbc_6min.json",
]

src = (ROOT / "webapp.py").read_text(encoding="utf-8")
html = re.search(r'HTML_TEMPLATE = r"""(.*?)"""', src, re.S).group(1)

# the offline build has the config file in its own data/ folder, so the marker
# becomes a plain fetch-free assignment filled from that file at boot
html = html.replace("/*__STT_CONFIG__*/", "")

# 1) send(): call the local engine instead of the HTTP endpoint
#
# This used to be an exact string copy of the web send() body, which meant any
# edit to the catch block in webapp.py broke the APK build with a bare
# assertion - and the offline build silently kept the old behaviour until
# someone noticed. It is matched structurally now: the engine call and the
# failure handling are rewritten where they are, and anything else in the
# function is left alone. The two builds cannot drift on this path.
m = re.search(r"(  showTyping\(\);\n  try \{\n)(.*?)(\n  \} catch \(e\) \{\n)(.*?)(\n  \}\n)", html, re.S)
if not m:
    sys.exit("could not find the send() try/catch in the template")

engine = """    await sleep(160);                       // a beat so the typing dots show
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

html = html.replace(
    """    const r = await fetch('/api/grammar');
    const topics = await r.json();""",
    """    const topics = grammarTopics;""")
html = html.replace(
    """    const r = await fetch('/api/phrases');
    const topics = await r.json();""",
    """    const topics = phraseTopics;""")
html = html.replace(
    """    const r = await fetch('/api/vocabulary');
    const groups = await r.json();""",
    """    const groups = vocabGroups;""")
html = html.replace(
    """    const r = await fetch('/api/listening');
    const levels = await r.json();""",
    """    const levels = listeningLevels;""")
html = html.replace(
    """    const r = await fetch('/api/phonetics');
    sections = await r.json();""",
    """    sections = phoneticSections;""")
html = html.replace(
    """    const bands = wordArchBands;""",
    """    const bands = wordArchBands;""")
# every occurrence, not just the first: loadWordArch has a second call site
html = html.replace(
    """    const r = await fetch('/api/wordarch');
    const bands = await r.json();""",
    """    const bands = wordArchBands;""")
html = html.replace(
    """    const r = await fetch('/api/bbc');
    const doc = await r.json();""",
    """    const doc = bbcCatalogue;""")

# keep the Object.assign line that follows, so the offline copy fills the cache
html = html.replace(
    """    Object.assign(wordArch, bands);
    wordArchLoaded = true;""",
    """    Object.assign(wordArch, bands);
    wordArchLoaded = true;""")

# 3) boot: load the data, build the bot, then populate the panels
html = html.replace(
    """loadGrammar();
loadPhrases();
loadVocabulary();""",
    """/* offline boot: load the bundled data, build the engine, fill the panels */
let bot, grammarTopics, phraseTopics, vocabGroups, listeningLevels, phoneticSections;
let bbcCatalogue = {episodes: [], count: 0};
let wordArchBands = {};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const loadJSON = (name) => fetch('data/' + name + '.json').then((r) => r.json());

Promise.all([loadJSON('memory'), loadJSON('glossary'), loadJSON('grammar'),
             loadJSON('phrases'), loadJSON('jokes'), loadJSON('listening'),
             loadJSON('phonetics'), loadJSON('word_arch'),
             loadJSON('distinctions'), loadJSON('idioms'),
             loadJSON('corrections'), loadJSON('stt'),
             loadJSON('bbc_6min')])
  .then(([memory, glossary, grammar, phrases, jokes, listening, phonetics, wordArch,
          distinctions, idioms, corrections, stt, bbc]) => {
    // every file the engine can read must be handed to it, or a section
    // silently comes back empty offline
    bot = new Fluentify({memory, glossary, grammar, phrases, jokes, listening,
                         phonetics, distinctions, idioms, corrections});

    listeningLevels = listening.levels.map((lv) => ({
      id: lv.id, title_en: lv.title.en, title_fa: lv.title.fa,
      blurb_en: lv.blurb.en, blurb_fa: lv.blurb.fa, sentences: lv.sentences,
    }));
    // word architecture, grouped by CEFR level for the Sentences panel
    Object.entries(wordArch.words).forEach(([, e]) => {
      (wordArchBands[e.level || 'A1'] = wordArchBands[e.level || 'A1'] || [])
        .push({en: e.en, fa: e.fa, pos: e.pos, forms: e.forms,
               level: e.level, domains: e.domains || []});
    });
    Object.values(wordArchBands).forEach((v) => v.sort((a, b) => a.en < b.en ? -1 : 1));

    phoneticSections = phonetics.sections.map((s) => ({
      id: s.id, icon: s.icon || '🔊', level: s.level || 'A1',
      title_en: s.title.en, title_fa: s.title.fa,
      blurb_en: s.blurb.en, blurb_fa: s.blurb.fa,
      tip_en: (s.tip || {}).en || '', tip_fa: (s.tip || {}).fa || '',
      groups: (s.groups || []).map((g) => ({
        name_en: g.name.en, name_fa: g.name.fa, rows: g.rows || [],
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

    // speech-to-text settings, straight from the same stt.json the CLI reads
    window.STT_CONFIG = stt;
    // the graded BBC catalogue: links and levels only, the audio streams
    bbcCatalogue = {episodes: (bbc.episodes || []).map((e) => ({
      id: e.id, title: e.title, blurb: e.blurb, year: e.year,
      level: e.level, duration: e.duration, url: e.url, audio: e.audio,
      transcript_url: e.transcript_url, worksheet_url: e.worksheet_url,
      stats: e.stats,
    })), count: bbc.count || (bbc.episodes || []).length,
      distribution: bbc.distribution || {}};

    loadGrammar();
    loadPhrases();
    loadVocabulary();
    loadListening();
    loadPhonetics();
    mountMic();
  })
  .catch((e) => add('⚠️ could not load the language data: ' + e.message, 'bot', {err: true}));""")

# 3b) the panels are already loaded inside the offline boot block; the
# top-level calls that follow it would run before the data has resolved
before = """});
loadListening();
loadPhonetics();
"""
after = """});
"""
assert before in html, "offline tail not found — update build_apk_ui.py"
html = html.replace(before, after, 1)

# 4) load bot.js before the page script
assert "\n<script>\n" in html
html = html.replace("\n<script>\n", '\n<script src="bot.js"></script>\n<script>\n', 1)

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(html, encoding="utf-8")
print("wrote", OUT, len(html), "chars")

# ---------------------------------------------------------------------------
# sync the data files
# ---------------------------------------------------------------------------
DATA.mkdir(parents=True, exist_ok=True)
missing = []
for name in BUNDLED_DATA:
    src = ROOT / name
    dest = DATA / name
    if not src.exists():
        missing.append(name)
        continue
    shutil.copyfile(src, dest)
print(f"synced {len(BUNDLED_DATA) - len(missing)}/{len(BUNDLED_DATA)} data files -> {DATA}")
if missing:
    for name in missing:
        print(f"  ! {name} is missing from the repository root")
    print("  the APK will fail to start until these exist "
          "(tools/fetch_bbc_6min.py builds bbc_6min.json)")
    raise SystemExit(1)

# the offline page must not reference a server endpoint
leftovers = re.findall(r"fetch\(\s*['\"](/api/[^'\"]+)", html)
if leftovers:
    raise SystemExit("offline page still calls the server: " + ", ".join(set(leftovers)))

# ---------------------------------------------------------------------------
# parse the page before shipping it
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