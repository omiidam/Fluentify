# Fluentify

<p align="center">
  <img src="brand/fox-mark.png" width="128" alt="Fluentify's mascot — a scholarly fox in a beret and spectacles">
</p>

A bilingual (English / Persian) language tutor — greetings, small talk, jokes, a
1000+ word glossary, 25 banks of practical sentences and 48 English grammar
lessons with interactive exercises. It runs **completely offline**: no API keys,
no network calls, no tracking.

<p align="center">
  <b>Desktop</b> · pure Python standard library — <code>python3 webapp.py</code><br>
  <b>Android</b> · installable APK built by GitHub Actions (see below)
</p>

---

## What's inside

| Area | Details |
|---|---|
| 📅 Daily English | one word + one expression + one conversation per **local calendar day**, from a curated catalogue (60 / 55 / 24), with a per-day tick — reading only, no audio |
| 💬 Small talk | 42 bilingual intents: feelings, health, work, boredom, encouragement, riddles, fun facts… |
| 📚 Vocabulary | 2,314 curated words across 64 grouped domains, translate & define in both languages — and behind them a **20,602-headword dictionary** with definitions, Persian meanings, IPA, inflected forms, synonyms/antonyms and examples, all offline |
| 📘 Grammar | 48 lessons (A1→C2) — structure → explanation → function → **6 practice questions the exam gate waits on → a 20-question exam**, with a themed result card |
| 🔬 Analyse | an **offline grammar analyser**: parts of speech, lemmas and the tense/aspect a sentence carries, word by word, on the device — a real tagger bundled in the page and the APK, with no server |
| 💬 Sentences | 517 ready-to-use sentences across 45 real-life situations |
| 🎧 Listening | 48 spoken sentences graded A1 → C2, read aloud offline (tap ▶ to play) |
| 🌱 Daily seed | 20 tokens per session; the session rolls over at **03:30 GMT**, fill the seed and the bird blooms |
| 🦊 Fox stickers | thirty-six flat fox stickers in the composer's picker, searchable in English and Persian |
| 😂 Jokes | 10 bilingual jokes with category filtering (`programming joke`, `جوک ربات`) |
| 🔤 Alphabets | English + Persian alphabet, and single-letter lookup (`what letter is A`, `حرف ب`) |

Every lesson and sentence is shown **English first with the Persian translation
directly underneath**, so the two languages reinforce each other instead of
living in separate sections.

### Dictionary

A lookup the curated glossary cannot answer falls through to a dictionary of
**20,602 headwords / 35,110 senses** (35,097 of them with a Persian meaning,
18,426 with IPA, 20,601 with a worked example). It is knowledge behind the same
chat, not a page: there is no dictionary tab, panel, button or route.

```
define achievement            what does bank mean in river bank
give me synonyms for beautiful  what is the past tense of seek
what is the opposite of generous  what does achievment mean   ← typo, offered the word
معنی courage چیه              مترادف کلمه beautiful رو بگو
```

It also answers four things the glossary never could: synonyms, opposites, the
inflected forms a word actually has, and one word's meaning **read inside the
learner's own sentence** ("what does run mean in run a business"). Multiple
meanings are kept apart, never merged: `bank` answers river bank and financial
bank separately, and a sentence picks the sense by scoring the entry's own
glosses against it. If no sense matches the sentence, the answer says so instead
of guessing.

Sources and licences (full text in `lexicon/_meta.json`, which the suite
cross-checks against the shards on disk):

| source | licence | what came from it |
|---|---|---|
| [OpenJam](https://github.com/amirj4m/openjam) | MIT, data included | lemmas, senses, definitions, examples, Persian sense translations, IPA, inflected forms |
| [Princeton WordNet 3.1](https://wordnet.princeton.edu/) | WordNet (BSD-style) | synonyms and antonyms |

Deliberately **not** imported: the English–Persian dataset with no licence, the
VahidN dictionaries whose individual contents publish none, and the Wiktionary
extract whose CC BY-SA share-alike would relicense the app's data. Nothing the
sources lack is invented — no entry carries a CEFR level (OpenJam's field is
just a frequency band), and an entry with no Persian meaning says nothing
rather than printing an English gloss under a Persian label.

Storage is **333 shards**, not one file: the page fetches the shards for the
words of the current message (`data/lex/<prefix>.json`, 10.2 MB in total,
~3 MB compressed into the APK) and caches them, so startup parses nothing and
lookup cost is one small file. `lexicon/_index.json` lists which shards exist,
because English is not spread evenly. Persian questions read `_fa.json` once.

```bash
python3 tools/build_lexicon.py     # rebuild from the cached sources (~2 s)
python3 tools/check_lexicon.py     # data, answers, and "still invisible"
```

Known gaps, measured rather than papered over: the source does not carry every
lemma, so a few words are simply absent — `resilient` is one (its noun
`resilience` is there). The answer names the word it lacks and offers the
closest one it has.

### Daily English

Three fresh items at the start of every local day — one word, one expression and
one conversation — offered as **a small card inside the conversation**, not as a
section that takes the chat away: three one-line rows that open in place, a tick
per row, and a progress count. The **Today** panel holds the full material
(examples and the whole dialogue) and is opened on demand. The section has no
voice: a speaker under every line turned a reading card into a player, and this
app already has a Listening panel where audio is the point.

The daily set is a suggestion, so turning it down is one tap and nothing is
punished: **✕** removes the card for the rest of that day, and **Don't show
again** keeps it out of the chat entirely, reversible from the panel's own
switch. A skipped day stays skipped — there is no un-skip control, and the page
will not redraw the card on a repaint, a resume or the next launch; tomorrow
offers a new day. **Read all three** opens the rows where they sit, so the day
is readable without leaving the conversation. Completion is kept per day either
way, so skipping reads as skipping, not as failing. The same three are also
available in chat (`today's word`, `لغت امروز`).

The choice is a pure function of the local date: `daily_index()` in
`chatbot.py`, `dailyIndex` in `bot.js` and `dayIndex` in the page walk the same
catalogue from the same epoch, so the CLI, the web preview and the offline APK
show the same three items on the same day with no server involved.
`tools/check_daily.py` compares all three over 365 dates and five timezones,
including both 2026 daylight-saving nights, where the wait to midnight is not
24 hours. It also exercises the skip / switch-off store: skipping one day must
skip one day and stay skipped (the store has no un-skip to call), a corrupt
record must not hide the feature, and the per-day list is pruned so years of
daily use cannot fill storage.

The catalogue in `daily.json` is curated, never generated at runtime: 60 words,
55 expressions, 24 conversations. To be exact about coverage, that is **not**
365 distinct entries per category — a word returns after 60 days and a
conversation after 24 — while the whole word + expression + conversation set
does not repeat for **1,320 days**. Extending the catalogue only lengthens the
cycle, and each category steps through every entry before reusing one.
Completion is stored per date (`fluentify.daily.v1` in `localStorage`) and is
never cleared, so yesterday's ticks survive the new day.

### Fox stickers

The composer's picker holds thirty-six fox stickers instead of the usual unicode
palette — the whole reference sheet, six rows of six. One flat style, composed
from a single front head, a single side head and four bodies, so the set reads
as one hand rather than thirty-six.

`foxes.json` is the whole catalogue — id, English name, Persian name, search
keywords and the finished SVG — so the page never draws a fox itself. The
finished SVG is generated: `tools/build_foxes.py` holds the poses and writes the
file, which is why the palette and the eyes are one constant each. Edit a pose
there and re-run it rather than hand-patching a path. Search works in both
languages: `sleep` and «خواب» find the same sticker.

A sticker is a picture and the composer is a text field, so a picked fox goes in
as `[fox:cute]` and is expanded back into the drawing when the message renders —
after the text has been escaped, so the artwork always comes from the catalogue
and never from what someone typed. The drawings are original: the reference set
that prompted the feature is a watermarked stock sheet, so nothing is traced or
copied from it. `tools/check_ui.py` fails if a sticker id could not survive its
`[fox:id]` token, or if any entry ever carries a script, an `href` or an event
handler, because those strings are inserted with `innerHTML`.

### The mascot

One illustration, one pipeline. `brand/fox-source.png` is the artwork, and
`python3 tools/build_brand.py` cuts everything the app draws from it: the round
portrait in `brand/` (boot screen, header, message rows, tab icon) and all
twelve launcher PNGs plus the three adaptive foregrounds under
`android/app/src/main/res/mipmap-*`. Re-cutting a crop is an edit to that file,
not a new drawing.

Nothing is redrawn per surface. That is the point: the mascot was a hand-drawn
SVG for a while, and the boot screen carried a second copy of it that had to be
kept identical by a test. A picture cannot drift from itself — and the launcher
icon is generated at exactly 48/72/96/144/192 px (the adaptive layer at 108 dp,
art at 72 dp of it, so no mask shape crops the fox) instead of being scaled by
the launcher. `tools/check_manifest.py` fails if a density is stale or the set
is half-regenerated.

### Offline grammar analyser

Ask for it and the sentence is taken apart on the device:

```
analyse this sentence: She has been learning English.
این جمله رو از نظر گرامری تحلیل کن: She has been learning English.
```

Both answer with a table — each word, its part of speech in English *and*
Persian, its lemma, and whether it is the subject or the object — followed by
the structures the sentence carries (here: Declarative, Present Perfect
Continuous, Pronouns), a lesson chip per structure that opens the matching
lesson from the Knowledge Base, and a plain statement of what the method cannot
do. The same analysis is kept in the **Analyse** panel, where a sentence can
also be typed or picked from an example.

The engine is [winkNLP](https://github.com/winkjs/wink-nlp) 2.4.0 with the
English web model [wink-eng-lite-web-model](https://github.com/winkjs/wink-eng-lite-web-model)
1.8.1, bundled into one 3.5 MB file ([nlp/fluentify-nlp.js](nlp/fluentify-nlp.js))
by `cd nlp && npm run build`. Both are MIT and the notices ship with the file —
see [nlp/THIRD-PARTY-NOTICES.md](nlp/THIRD-PARTY-NOTICES.md).

What that buys, and what it does not:

* **Tokenising, sentence splitting, parts of speech, lemmas, negation and
  contraction flags** come from the bundled model.
* **Tenses, aspect, voice, conditionals, gerunds/infinitives** come from
  explicit rules in [nlp/src/analyser.js](nlp/src/analyser.js) that read the
  surface form against the lemma. They are asserted, and wrong answers are
  asserted *against*, in [tools/check_analyser.py](tools/check_analyser.py) —
  `reads` is present simple, `finished` after `have` is a past participle,
  `will have finished` is the future perfect.
* **There is no dependency parser**, and the app never pretends there is: no
  `nsubj`, `dobj` or `ROOT` is ever emitted, the only roles reported are
  subject and object inferred from word order, and every one of them is marked
  `roleStatus: "inferred"` in both languages. A suite that finds a dependency
  label, an offset that does not slice back to its token, or a lesson chip
  whose topic the Knowledge Base cannot answer fails the build.
* **Ambiguity is stated, not hidden** — a second sentence in the box, a paste
  longer than 40 words, a word the tagger could not read, or a verb spelled the
  same in the present and the past (`read`, `put`, `cut`) each add a line to
  the analysis saying so.

The model is built on the first analysis (~70 ms, once) and cached; after that
a bounded sentence costs under a millisecond. The file itself is fetched
lazily on the first request, never at boot, and every analysis is computed
locally — the browser test for this feature runs with **no `/api/` request at
all**, and the copied bundle inside the APK is the same file the web build
serves.

---

## Look and feel

Warm paper, navy ink and a gold spark: the page is cream (`#faf4e8`), the
mascot and the room's only dark surface are navy (`#1b2d52`), and gold
(`#f1c15a`) marks what the tutor is pointing at. **Baloo 2** carries headings
and the top-bar buttons, **Kalam** carries the transcript — the two faces of the
reference design, both SIL OFL and vendored in `fonts/` so the APK has them
offline.

Every colour and both families live in one `:root` block at the top of
[webapp.py](webapp.py); nothing downstream hard-codes a hue, so re-theming is a
single edit. [tools/check_ui.py](tools/check_ui.py) asserts the structural rules
the design depends on — tile hairlines, the borderless composer controls, the
contrast pairs, the disabled watermark — so a later tweak cannot quietly undo
them.

---

## Run it on the desktop

```bash
python3 chatbot.py     # terminal chat
python3 webapp.py      # browser UI → http://localhost:8765
```

No dependencies — Python 3.9+ standard library only.

## Build the Android APK

The APK is produced by CI, so you don't need Android Studio:

1. Push a change, or run the workflow manually (**Actions → Build Android APK → Run workflow**).
2. Download the artifact: `Fluentify-apk` → `app-debug.apk`.
3. Copy it to your phone and install it (allow "install from unknown sources").

The app is a WebView that loads `android/app/src/main/assets/www/`:
the UI is generated from `webapp.py` and the chatbot engine is a faithful
JavaScript port (`bot.js`). `tests_js_vs_python.py` asserts the two engines
produce identical replies, so the phone behaves exactly like the desktop.

```bash
python3 tests_js_vs_python.py   # 72/72 replies identical
```

Speech is native on Android (`MainActivity.kt` bridges the page to Android's
built-in `TextToSpeech`), so the listening practice is offline and needs no
network. In a desktop browser the same panel falls back to the Web Speech API.

---

## Layout

```
chatbot.py                  the bot (Python, stdlib only)
webapp.py                   desktop UI + HTTP server
build_apk_ui.py             generates the offline app UI from webapp.py
tests_js_vs_python.py       Python ⇄ JavaScript engine parity test
tools/js_engine.js          headless harness for the JS engine
tools/build_brand.py        cuts every mascot picture + the launcher icons
brand/                      fox-source.png (art) → fox-mark/fox-face (the app)
tools/build_lexicon.py      builds lexicon/ from the cached sources
tools/check_lexicon.py      the dictionary's data, answers and invisibility

lexicon/                    generated dictionary: 333 shards + _meta/_fa/_index
  <prefix>.json               headwords, forms, senses for one prefix
  _fa.json                    Persian meaning → English headwords
  _meta.json                  counts, sources, licences

memory.json                 42 intents + both alphabets
glossary.json               2,314 words in 64 domains
grammar.json                48 lessons: explanation, practice + exam question sets
phrases.json                517 sentences in 45 situations
jokes.json                  10 bilingual jokes
listening.json              48 spoken sentences graded A1 → C2

android/                    Gradle project for the APK
  app/src/main/assets/www/    index.html (generated) · bot.js · data/*.json
.github/workflows/build-apk.yml
```

## Practice scoring

Each lesson has **two** stages. You start with a short guided **practice** set of
6 questions; once you clear it the 🔒 on that lesson's exam is lifted:

```bash
# locked
> simple present exam
🔒 The exam is locked — finish the practice first (6 questions).
Type: 'simple present exercises'

# stage 1
> simple present exercises
✏️ Starting 'Simple Present' practice — good luck!
...
✅ Practice complete! Your exam is now open. 🎓

# a revealed answer or a miss keeps it shut
> simple present exercises
...
🔒 Practice finished — 5/6 correct.
The exam opens only after a perfect run: every answer right.

# stage 2
> simple present exam
🎓 Starting the 'Simple Present' exam — good luck!
```

In Persian: `تمرین حال ساده` then `آزمون حال ساده`. The same gate appears on the
grammar panel's 🎓 button.

The 20-question exam is graded into a themed band:

| Score | | |
|---|---|---|
| 90–100% | 🌟 Excellent |Outstanding — this grammar is yours. |
| 75–89% | 🌿 Very good | Strong and accurate. |
| 60–74% | 💧 Good | Solid, with a few slips to polish. |
| 40–59% | 🔥 Almost there | You have the idea — another round will lock it in. |
| 0–39% | 🌱 Keep going | Every expert started here. |

Revealing an answer with *show answer* moves on **without** scoring it, so the
number reflects what you actually got right.

## Adding content

Everything lives in JSON — no code changes needed:

* **a word** → append `["english", "فارسی"]` to any `words` list in `glossary.json`
* **a sentence** → append `{"en": "...", "fa": "..."}` to a topic in `phrases.json`
* **a grammar lesson** → add a topic to `grammar.json` with `title`, `keywords`, `level`,
  `structure`, `explain` (the deeper "why it works" notes), `function`, `examples`
  (wrap the taught part in `**like this**`), `practice` (the 6 warm-up questions the
  exam gate waits on) and `exam` (the 20 scored ones)
* **small talk** → add an intent to `memory.json` with EN/FA keywords and responses

Then re-run `python3 build_apk_ui.py` and `cp *.json android/app/src/main/assets/www/data/`.

## Credits

Memory and content structures were informed by these open-source projects:
[gunthercox/chatterbot-corpus](https://github.com/gunthercox/chatterbot-corpus),
[Mahdi-Razaghi/tajan](https://github.com/Mahdi-Razaghi/tajan),
[Persian-Caesar/chatbot](https://github.com/Persian-Caesar/chatbot),
[Nikola-Ver/English-grammar-tree](https://github.com/Nikola-Ver/English-grammar-tree) and
[guilherme-reis/English-Grammar-Mental-Map-In-Markdown](https://github.com/guilherme-reis/English-Grammar-Mental-Map-In-Markdown).

The dictionary's content comes from [OpenJam](https://github.com/amirj4m/openjam)
(MIT, data included) and [Princeton WordNet 3.1](https://wordnet.princeton.edu/)
(WordNet licence, BSD-style); the notices travel with the data in
`lexicon/_meta.json`.

## License

MIT

## 🎧 BBC listening, graded A2 → C1

The 🎧 Listening panel carries a catalogue of **BBC Learning English** episodes,
each graded by how hard it is to *hear*, not just to read.

### Three series, because one is not enough

> **On the name.** BBC ran a series called *5 Minute English* until 2014 and
> relaunched it as *6 Minute English*. That series is indexed here — but it is
> only one of three, and it is **intermediate throughout**. A single series
> cannot give a graded spread, so the catalogue takes all three that BBC runs at
> different levels:

| series | episodes | BBC targets | what it is |
| --- | --- | --- | --- |
| **Real Easy English** | 124 | A1–A2 | deliberately simple, slow, everyday |
| **6 Minute English** | 501 | B1–B2 | the former 5 Minute English — news and chat |
| **The English We Speak** | 501 | B2–C1 | idioms and phrasal verbs, upper level |

> **On the audio.** Every clip, transcript and worksheet is BBC copyright. The
> repository stores **links only**, and no BBC media is committed to git or
> bundled into the APK. The 20 episodes in the shipped catalogue are mirrored to
> an ArvanCloud storage bucket for reliable streaming; the app still keeps the
> canonical BBC page URL for each episode.

```bash
python3 tools/fetch_bbc_6min.py --fetch all     # index + grade the archive
python3 tools/fetch_bbc_6min.py --audit         # grade vs BBC's own level tag
python3 tools/fetch_bbc_6min.py --report        # level distribution
```

Downloads are resumable — per-episode pages and PDFs are cached under
`tools/.cache/` (gitignored). The output is `bbc_6min.json`.

### How an episode is graded

`tools/listening_grade.py` blends four things, because listening difficulty is
not reading difficulty — a BBC presenter delivers ~150 words a minute with
contractions and reductions, so a passage you could read comfortably can still
be a hard listening task.

| signal | what it captures |
| --- | --- |
| **stretch** | 75th percentile of content-word CEFR levels — the vocabulary you must already own |
| **challenge** | share of content tokens at B2 or above — how much is *new* work |
| **syntax** | sentence length and clause density — what makes a listener lose the thread |
| **density** | words per minute — separates a slow careful read from a fast discussion |

Word levels come from the CEFR-J list already used for the rest of the app
(`Maximax67/Words-CEFR-Dataset`, MIT).

The grader is independent of BBC, so it can disagree with them. `--audit` tries
to check it against BBC's own level tag, and the result is worth reading:

```
audited 603 tagged episodes
  BBC's own tags: {'intermediate': 603}
  per series (grader vs BBC's tag):
    6 Minute English         inside 152/264 ( 57%)   grader: A1:72 A2:39 B1:137 B2:15 C1:1
    The English We Speak     inside 134/339 ( 39%)   grader: A1:11 A2:193 B1:114 B2:20 C1:1
```

**BBC tags all three series "intermediate"**, including Real Easy English,
whose whole premise is deliberately simple speech. So their tag is a
course-track label, not a difficulty measurement, and it cannot validate a
graded catalogue — the low numbers above are the tag being too coarse, not the
grader being wrong.

The grader is validated by `tools/harness_stt.py` instead, on properties that
do not depend on BBC:

- harder text must never grade easier than easier text
- a one-line blurb must not be graded at all, rather than guessed at
- function words must not drag a passage down
- the bands line up with where each series is actually pitched
  (Real Easy English → A1–A2, 6 Minute English → B1–B2, The English We Speak → B2–C1)
audited 501 tagged episodes
  inside BBC's own band  : 100% (100%)
```

## 🎙 Speech to text

Dictation in the composer. Three surfaces, one config.

| surface | engine | needs |
| --- | --- | --- |
| web | Web Speech API | a Chromium or Safari browser |
| Android | `RecognizerIntent` (ships with the OS) | nothing — no model, no key |
| CLI | faster-whisper / openai-whisper / vosk | `pip install faster-whisper` |

`stt.json` configures all three — languages, auto-stop, interim results, output
formats, privacy notes — so they cannot drift apart.

```bash
python3 tools/transcribe.py --check                    # what is installed
python3 tools/transcribe.py lesson.mp3                 # transcribe
python3 tools/transcribe.py lesson.mp3 -f srt          # subtitles
python3 tools/transcribe.py clip.mp3 --model small     # better accuracy
```

The CLI also grades its own output with the same CEFR grader, so a clip you
record yourself lands on the same scale as the BBC catalogue.

Nothing is uploaded by this project: recognition is done by the browser or the
OS. `tools/transcribe.py` says plainly which backends are missing instead of
failing quietly.

## Checks

```bash
python3 tools/check_all.py
```

Twelve suites:

| suite | what it asks |
| --- | --- |
| content & input integrity | are the data files well-formed, and does hostile input get a clean answer? |
| capability harness | can the bot answer what a learner actually asks? |
| Python/JS message parity | do the CLI and the APK engine agree, message for message? |
| Python/JS conversation parity | do they agree over a *conversation*? Memory only shows up across several messages. |
| BBC grader & speech-to-text | is the CEFR grader still calibrated, is `stt.json` still what all three surfaces read, and does the offline bundle actually start? |
| offline grammar analyser | is the bundled tagger accurate and honest? It runs the shipped 3.5 MB file over the sentences the feature was specified against plus contractions, unpunctuated input, unknown names and mixed script, and refuses a fabricated dependency label, a bad offset, a lesson chip the Knowledge Base cannot answer, or a request whose sentence it cannot find. |
| dictionary knowledge | is every shard the shape the engine reads, does every count in `_meta.json` match the files, are the licences still recorded, do the brief's questions answer through the *existing* chat, and is there still no dictionary route, panel or tab? |

That last one matters more than its size suggests. A duplicate top-level name
between the page and `bot.js` is a SyntaxError that kills the whole inline
script: the APK installs, launches, logs nothing, and is blank. It shipped
once, and the web build could never catch it because the web page does not
load `bot.js`. `build_apk_ui.py` now parses both together and exits 1 rather
than ship an app that cannot start.
