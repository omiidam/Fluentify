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
  } catch (e) {
    hideTyping();
    add('⚠️ something went wrong — ' + e.message, 'bot', {err: true});
  }"""
assert old_send in html
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

# 3) boot: load the data, build the bot, then populate the panels
html = html.replace(
    """loadGrammar();
loadPhrases();
loadVocabulary();""",
    """/* offline boot: load the bundled data, build the engine, fill the panels */
let bot, grammarTopics, phraseTopics, vocabGroups, listeningLevels;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const loadJSON = (name) => fetch('data/' + name + '.json').then((r) => r.json());

Promise.all([loadJSON('memory'), loadJSON('glossary'), loadJSON('grammar'),
             loadJSON('phrases'), loadJSON('jokes'), loadJSON('listening')])
  .then(([memory, glossary, grammar, phrases, jokes, listening]) => {
    bot = new Fluentify({memory, glossary, grammar, phrases, jokes});

    listeningLevels = listening.levels.map((lv) => ({
      id: lv.id, title_en: lv.title.en, title_fa: lv.title.fa,
      blurb_en: lv.blurb.en, blurb_fa: lv.blurb.fa, sentences: lv.sentences,
    }));

    // Use the engine's own unwrapped maps so panel data always matches the
    // structures bot.js actually uses.
    grammarTopics = Object.values(bot.grammar).map((t) => ({
      title_en: t.title.en, title_fa: t.title.fa, level: t.level || '',
      query_en: t.keywords.en[0],
      practice_en: t.keywords.en[0] + ' exercises',
    }));
    phraseTopics = Object.values(bot.phrases).map((t) => ({
      title_en: t.title.en, title_fa: t.title.fa,
      query: t.keywords.en[0], count: t.phrases.length,
    }));
    vocabGroups = bot.glossaryGroups.map((g) => ({
      en: g.en, fa: g.fa,
      items: g.domains.map((id) => {
        const d = bot.glossary[id];
        return {
          title_en: d.list_label.en, title_fa: d.list_label.fa,
          query_en: d.keywords.en[0], query_fa: d.keywords.fa[0],
          count: d.words.length,
        };
      }),
    }));

    loadGrammar();
    loadPhrases();
    loadVocabulary();
    loadListening();
  })
  .catch((e) => add('⚠️ could not load the language data: ' + e.message, 'bot', {err: true}));""")

# 4) load bot.js before the page script
assert "\n<script>\n" in html
html = html.replace("\n<script>\n", '\n<script src="bot.js"></script>\n<script>\n', 1)

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(html, encoding="utf-8")
print("wrote", OUT, len(html), "chars")