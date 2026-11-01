#!/usr/bin/env python3
"""Is the free-dictionary fallback honest, cheap, and the same in both engines?

The tutor's dictionary is curated - the words it teaches and nothing else - so
a word outside it used to be "I don't have that word". dictionary_api.py asks
dictionaryapi.dev instead. That is a network call in the middle of a chat,
which is exactly the kind of thing that quietly goes wrong, so this suite
answers four questions:

  * does it only ever ask about one real word? ("ice cream" must not become a
    request for "icecream", and Persian is not its business)
  * is a miss remembered while a failure is not? A 404 cached means no repeat
    request; a timeout cached would hide the word for a week.
  * does the reply say where the senses came from, and stop short of inventing
    a Persian gloss it does not have?
  * do the Python bot and the APK engine format the same entry identically?
    The APK asks from the page and answers from a cache, so the two formatters
    are separate code and would drift silently.

No request leaves this machine: urllib is replaced with a stub per check.
"""

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CACHE = ROOT / "tools/.cache/web_dict_check.json"
CACHE.parent.mkdir(parents=True, exist_ok=True)
CACHE.unlink(missing_ok=True)
os.environ["FLUENTIFY_DICT_CACHE"] = str(CACHE)
os.environ.pop("FLUENTIFY_NO_WEB_DICT", None)

import dictionary_api  # noqa: E402
from chatbot import ChatBot  # noqa: E402

CHECKS = 0
FAILURES = []


def check(name: str, ok: bool, detail: str = "") -> None:
    global CHECKS
    CHECKS += 1
    if not ok:
        FAILURES.append(f"{name}{': ' + detail if detail else ''}")


ENTRY = {
    "word": "serendipity",
    "ipa": "/ˌsɛɹənˈdɪpɪti/",
    "meanings": [
        {"pos": "noun", "senses": [
            {"d": "A combination of events which happen by chance.",
             "ex": "Meeting her was pure serendipity."},
            {"d": "An unsought, unintended discovery.", "ex": ""}]},
        {"pos": "verb", "senses": [{"d": "To find by happy accident.", "ex": ""}]},
    ],
}

# What the service actually sends back, cut down to the parts that are read.
PAYLOAD = [{
    "word": "serendipity",
    "phonetic": "/ˌsɛɹənˈdɪpɪti/",
    "phonetics": [{"text": "/ˌsɛɹənˈdɪpɪti/", "audio": ""}],
    "meanings": [
        {"partOfSpeech": "noun", "definitions": [
            {"definition": "A combination of events which happen by chance.",
             "example": "Meeting her was pure serendipity.",
             "synonyms": [], "antonyms": []},
            {"definition": "An unsought, unintended discovery."}]},
        {"partOfSpeech": "verb", "definitions": [
            {"definition": "To find by happy accident."}]},
    ],
    "license": {"name": "CC BY-SA 3.0", "url": "https://creativecommons.org/licenses/by-sa/3.0"},
    "sourceUrls": ["https://en.wiktionary.org/wiki/serendipity"],
}]


class _Response:
    def __init__(self, payload):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _serve(payload):
    calls = []

    def fake(request, timeout=None):
        calls.append(getattr(request, "full_url", str(request)))
        return _Response(payload)

    urllib.request.urlopen = fake
    return calls


def _fail_404():
    def fake(request, timeout=None):
        raise urllib.error.HTTPError(
            getattr(request, "full_url", "url"), 404, "Not Found", None, None)

    urllib.request.urlopen = fake


def _fail_network():
    """The request goes out and the network is down, as it is on a train."""
    def fake(request, timeout=None):
        raise urllib.error.URLError("network is unreachable")

    urllib.request.urlopen = fake


def _fail_offline(marker="no request should have been made"):
    def fake(request, timeout=None):
        raise AssertionError(marker)

    urllib.request.urlopen = fake


def main() -> int:
    # 1. which strings count as a word to ask about
    check("a word, cleaned", dictionary_api.clean("  Serendipity! ") == "serendipity")
    check("a hyphenated word kept", dictionary_api.clean("well-known") == "well-known")
    check("a phrase rejected", dictionary_api.clean("ice cream") == "")
    check("a phrase is not mashed into a word",
          dictionary_api.clean("a lot") != "alot")
    check("persian rejected", dictionary_api.clean("زبان") == "")
    check("digits rejected", dictionary_api.clean("2024") == "")
    check("empty rejected", dictionary_api.clean("  ") == "")

    # 2. the payload, reduced to what a learner is shown
    normalised = dictionary_api._normalize(PAYLOAD)
    check("payload normalised", bool(normalised) and normalised["word"] == "serendipity")
    check("phonetic kept", normalised and normalised["ipa"] == "/ˌsɛɹənˈdɪpɪti/")
    check("meanings kept", normalised and len(normalised["meanings"]) == 2)
    check("example kept",
          normalised and normalised["meanings"][0]["senses"][0]["ex"]
          == "Meeting her was pure serendipity.")
    check("empty payload refused", dictionary_api._normalize([]) is None)
    check("junk payload refused", dictionary_api._normalize("nope") is None)
    check("definitions-less payload refused",
          dictionary_api._normalize([{"word": "x"}]) is None)

    # 3. a hit is fetched once and then served from the cache
    calls = _serve(PAYLOAD)
    entry = dictionary_api.lookup("serendipity")
    check("hit returned", bool(entry) and entry["word"] == "serendipity")
    check("hit fetched once", len(calls) == 1, f"{len(calls)} request(s)")
    _fail_offline("a cached hit must not be fetched again")
    check("hit served from the cache",
          (dictionary_api.lookup("serendipity") or {}).get("word") == "serendipity")

    # 4. a 404 is an answer and is remembered; a network failure is not
    _fail_404()
    check("404 is a miss", dictionary_api.lookup("quokka") is None)
    _fail_offline("a remembered miss must not be fetched again")
    check("miss remembered", dictionary_api.lookup("quokka") is None)
    with open(CACHE, encoding="utf-8") as f:
        saved = json.load(f)
    check("miss cached as a miss", "quokka" in saved and saved["quokka"]["entry"] is None)

    _fail_network()
    check("offline is silent", dictionary_api.lookup("zeppelin") is None)
    with open(CACHE, encoding="utf-8") as f:
        saved = json.load(f)
    check("a failure is not cached", "zeppelin" not in saved)

    # 5. the switch really switches it off
    os.environ["FLUENTIFY_NO_WEB_DICT"] = "1"
    _fail_offline("the switch must stop the request")
    check("switch disables lookups", dictionary_api.lookup("serendipity") is None)
    os.environ.pop("FLUENTIFY_NO_WEB_DICT", None)

    # 6. the reply: senses, attribution, and no invented Persian
    bot = ChatBot()
    en = bot.format_api_entry("serendipity", ENTRY, "serendipity", "en")
    fa = bot.format_api_entry("serendipity", ENTRY, "serendipity", "fa")
    check("english names the word", "**serendipity**" in en)
    check("english shows the phonetic", "/ˌsɛɹənˈdɪpɪti/" in en)
    check("english shows the parts of speech", "— noun, verb" in en)
    check("english numbers the senses", "   1. " in en and "   2. " in en)
    check("english shows an example", "▸ Meeting her was pure serendipity." in en)
    check("english says where it came from", "dictionaryapi.dev" in en and "CC BY-SA" in en)
    check("english admits the missing gloss", "no Persian gloss" in en)
    check("persian uses persian digits", "   ۱. " in fa and "   ۲. " in fa)
    check("persian says where it came from", "ویکی‌واژه" in fa)
    check("persian admits the missing gloss", "ترجمه فارسی‌اش را ندارم" in fa)

    # 7. the APK engine formats the same entry identically
    entry_file = CACHE.parent / "web_dict_entry.json"
    entry_file.write_text(json.dumps(ENTRY, ensure_ascii=False), encoding="utf-8")
    proc = subprocess.run(
        ["node", "tools/js_web_dict.js", str(entry_file), "serendipity"],
        cwd=ROOT, capture_output=True, text=True)
    check("the apk engine ran", proc.returncode == 0, proc.stderr.strip()[-200:])
    js = json.loads(proc.stdout) if proc.returncode == 0 else {}
    check("english format identical", js.get("en") == en,
          f"\n    py: {en!r}\n    js: {js.get('en')!r}")
    check("persian format identical", js.get("fa") == fa,
          f"\n    py: {fa!r}\n    js: {js.get('fa')!r}")
    keys = js.get("keys") or {}
    check("apk rejects a phrase too", keys.get("phrase") == "")
    check("apk cleans a word too", keys.get("word") == "serendipity")
    check("apk rejects persian too", keys.get("persian") == "")
    check("apk rejects empty too", keys.get("empty") == "")
    targets = js.get("targets") or {}
    check("apk prefetches a bare word", targets.get("bare") == "quokka")
    check("apk prefetches an asked word", targets.get("ask") == "quokka")
    check("apk does not prefetch a phrase", targets.get("phrase") is None)
    check("apk prefetches the word in a persian question",
          targets.get("persian") == "quokka")
    check("apk does not prefetch a stopword", targets.get("stopword") is None)

    # 8. the wiring: asked from the page, answered before the typo suggestion
    bot_js = (ROOT / "android/app/src/main/assets/www/bot.js").read_text(encoding="utf-8")
    page = (ROOT / "android/app/src/main/assets/www/index.html").read_text(encoding="utf-8")
    build = (ROOT / "build_apk_ui.py").read_text(encoding="utf-8")
    chat = (ROOT / "chatbot.py").read_text(encoding="utf-8")
    check("the apk engine has the prefetch", "async loadWordApiFor(text)" in bot_js)
    check("the page calls it", "await bot.loadWordApiFor(text)" in page)
    check("the build writes that call", "await bot.loadWordApiFor(text)" in build)
    lex_miss = bot_js.split("  lexOrNotFound(word, lang) {", 1)[-1]
    body = lex_miss.split("\n  }\n", 1)[0]
    check("the apk asks the web dictionary before the typo suggestion",
          "this.apiLookup(word)" in body
          and body.index("this.apiLookup(word)") < body.index("this.lexNear(word)"))
    py_miss = chat.split("def lex_or_not_found(", 1)[-1]
    py_body = py_miss.split("\n    def ", 1)[0]
    check("the bot asks the web dictionary before the typo suggestion",
          "dictionary_api.lookup(word)" in py_body
          and py_body.index("dictionary_api.lookup(word)") < py_body.index("lex_near("))
    check("the cache is not committed",
          "dictionary_cache.json" in (ROOT / ".gitignore").read_text(encoding="utf-8"))

    CACHE.unlink(missing_ok=True)
    entry_file.unlink(missing_ok=True)

    if FAILURES:
        print(f"FAIL  {len(FAILURES)} of {CHECKS} web-dictionary checks\n")
        for f in FAILURES:
            print(f"  {f}")
        print()
        return 1
    print(f"PASS  all {CHECKS} web-dictionary checks (python and the APK engine "
          "format one entry identically, no request made)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
