# Fluentify

<p align="center">
  <img src="docs/bird.svg" width="96" alt="Fluentify mascot — a cute pink bird">
</p>

A bilingual (English / Persian) language tutor — greetings, small talk, jokes, a
1000+ word glossary, 25 banks of practical sentences and 31 English grammar
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
| 💬 Small talk | 42 bilingual intents: feelings, health, work, boredom, encouragement, riddles, fun facts… |
| 📚 Vocabulary | 1,052 words across 33 grouped domains, translate & define in both languages |
| 📘 Grammar | 31 lessons (A1→B2) — structure → function → **20 scored tests** each, with a themed result card |
| 💬 Sentences | 277 ready-to-use sentences across 25 real-life situations |
| 🎧 Listening | 48 spoken sentences graded A1 → C2, read aloud offline (tap ▶ to play) |
| 🌱 Daily seed | 20 tokens per session; the session rolls over at **03:30 GMT**, fill the seed and the bird blooms |
| 😂 Jokes | 10 bilingual jokes with category filtering (`programming joke`, `جوک ربات`) |
| 🔤 Alphabets | English + Persian alphabet, and single-letter lookup (`what letter is A`, `حرف ب`) |

Every lesson and sentence is shown **English first with the Persian translation
directly underneath**, so the two languages reinforce each other instead of
living in separate sections.

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
python3 tests_js_vs_python.py   # 61/61 replies identical
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
glossary.json               1,052 words in 33 domains
grammar.json                31 lessons with exercises
phrases.json                277 sentences in 25 situations
jokes.json                  10 bilingual jokes
listening.json              48 spoken sentences graded A1 → C2

android/                    Gradle project for the APK
  app/src/main/assets/www/    index.html (generated) · bot.js · data/*.json
.github/workflows/build-apk.yml
```

## Practice scoring

Each lesson ends with 20 tests. The result is graded into a themed band:

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
  `structure`, `function`, `examples` (wrap the taught part in `**like this**`) and `exercises`
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