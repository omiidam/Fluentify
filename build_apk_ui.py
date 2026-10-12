#!/usr/bin/env python3
"""Generates the offline Android UI (assets/www/index.html) from webapp.py.

The Python preview talks to /api/chat, /api/grammar, /api/phrases and
/api/vocabulary. The APK has no server, so those four calls are rewritten to
use the bundled bot.js engine and the JSON files in assets/www/data.
Keeping one source of truth means the desktop preview and the app never drift.
"""

import re
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "android/app/src/main/assets/www/index.html"

src = (ROOT / "webapp.py").read_text(encoding="utf-8")
html = re.search(r'HTML = r"""(.*?)"""', src, re.S).group(1)

# 1) send(): call the local engine instead of the HTTP endpoint
old_send = """  showTyping();
  try {
    const r = await fetch('/api/chat?message=' + encodeURIComponent(text));
    const data = await r.json();
    hideTyping();
    add(data.reply, 'bot');
    // finishing a practice unlocks that topic's exam — refresh the panel so
    // the 🎓 button stops showing the lock
    if (/exam is now open|آزمون باز شد/i.test(data.reply) &&
        document.getElementById('gpanel').classList.contains('open')) {
      loadGrammar();
    }
  } catch (e) {
    hideTyping();
    add('⚠️ connection lost — is the server running?', 'bot', {err: true});
  }"""
new_send = """  showTyping();
  try {
    await sleep(160);                       // a beat so the typing dots show
    const reply = bot.respond(text);
    hideTyping();
    add(reply, 'bot');
    // finishing a practice unlocks that topic's exam — refresh the panel so
    // the 🎓 button stops showing the lock
    if (/exam is now open|آزمون باز شد/i.test(reply) &&
        document.getElementById('gpanel').classList.contains('open')) {
      loadGrammar();
    }
  } catch (e) {
    hideTyping();
    add('⚠️ something went wrong — ' + e.message, 'bot', {err: true});
  }"""
assert old_send in html, "send() block not found — update build_apk_ui.py"
html = html.replace(old_send, new_send)

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
    """    const sections = phoneticSections;""")
html = html.replace(
    """    const r = await fetch('/api/wordarch');
    const bands = await r.json();""",
    """    const bands = wordArchBands;""")

# 3) boot: load the data, build the bot, then populate the panels
html = html.replace(
    """loadGrammar();
loadPhrases();
loadVocabulary();""",
    """/* offline boot: load the bundled data, build the engine, fill the panels */
let bot, grammarTopics, phraseTopics, vocabGroups, listeningLevels, phoneticSections;
let wordArchBands = {};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const loadJSON = (name) => fetch('data/' + name + '.json').then((r) => r.json());

Promise.all([loadJSON('memory'), loadJSON('glossary'), loadJSON('grammar'),
             loadJSON('phrases'), loadJSON('jokes'), loadJSON('listening'),
             loadJSON('phonetics'), loadJSON('word_arch')])
  .then(([memory, glossary, grammar, phrases, jokes, listening, phonetics, wordArch]) => {
    bot = new Fluentify({memory, glossary, grammar, phrases, jokes});

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

    loadGrammar();
    loadPhrases();
    loadVocabulary();
    loadListening();
    loadPhonetics();
  })
  .catch((e) => add('⚠️ could not load the language data: ' + e.message, 'bot', {err: true}));""")

# 4) load bot.js before the page script
assert "\n<script>\n" in html
html = html.replace("\n<script>\n", '\n<script src="bot.js"></script>\n<script>\n', 1)

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(html, encoding="utf-8")
print("wrote", OUT, len(html), "chars")