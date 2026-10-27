# Fluentify

<p align="center">
  <img src="docs/bird.svg" width="96" alt="Fluentify mascot — a cute pink bird">
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
| 📅 Daily English | one word + one expression + one conversation per **local calendar day**, from a curated catalogue (60 / 55 / 24), with audio and a per-day tick |
| 💬 Small talk | 42 bilingual intents: feelings, health, work, boredom, encouragement, riddles, fun facts… |
| 📚 Vocabulary | 2,314 words across 64 grouped domains, translate & define in both languages |
| 📘 Grammar | 48 lessons (A1→C2) — structure → explanation → function → **6 practice questions the exam gate waits on → a 20-question exam**, with a themed result card |
| 💬 Sentences | 517 ready-to-use sentences across 45 real-life situations |
| 🎧 Listening | 48 spoken sentences graded A1 → C2, read aloud offline (tap ▶ to play) |
| 🌱 Daily seed | 20 tokens per session; the session rolls over at **03:30 GMT**, fill the seed and the bird blooms |
| 😂 Jokes | 10 bilingual jokes with category filtering (`programming joke`, `جوک ربات`) |
| 🔤 Alphabets | English + Persian alphabet, and single-letter lookup (`what letter is A`, `حرف ب`) |

Every lesson and sentence is shown **English first with the Persian translation
directly underneath**, so the two languages reinforce each other instead of
living in separate sections.

### Daily English

Three fresh items at the start of every local day — one word, one expression and
one conversation — in the **Today** panel, each with audio and a tick, plus the
same three available in chat (`today's word`, `لغت امروز`).

The choice is a pure function of the local date: `daily_index()` in
`chatbot.py`, `dailyIndex` in `bot.js` and `dayIndex` in the page walk the same
catalogue from the same epoch, so the CLI, the web preview and the offline APK
show the same three items on the same day with no server involved.
`tools/check_daily.py` compares all three over 365 dates and five timezones,
including both 2026 daylight-saving nights, where the wait to midnight is not
24 hours.

The catalogue in `daily.json` is curated, never generated at runtime: 60 words,
55 expressions, 24 conversations. To be exact about coverage, that is **not**
365 distinct entries per category — a word returns after 60 days and a
conversation after 24 — while the whole word + expression + conversation set
does not repeat for **1,320 days**. Extending the catalogue only lengthens the
cycle, and each category steps through every entry before reusing one.
Completion is stored per date (`fluentify.daily.v1` in `localStorage`) and is
never cleared, so yesterday's ticks survive the new day.

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

Five suites:

| suite | what it asks |
| --- | --- |
| content & input integrity | are the data files well-formed, and does hostile input get a clean answer? |
| capability harness | can the bot answer what a learner actually asks? |
| Python/JS message parity | do the CLI and the APK engine agree, message for message? |
| Python/JS conversation parity | do they agree over a *conversation*? Memory only shows up across several messages. |
| BBC grader & speech-to-text | is the CEFR grader still calibrated, is `stt.json` still what all three surfaces read, and does the offline bundle actually start? |

That last one matters more than its size suggests. A duplicate top-level name
between the page and `bot.js` is a SyntaxError that kills the whole inline
script: the APK installs, launches, logs nothing, and is blank. It shipped
once, and the web build could never catch it because the web page does not
load `bot.js`. `build_apk_ui.py` now parses both together and exits 1 rather
than ship an app that cannot start.
