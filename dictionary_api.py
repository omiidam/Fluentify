#!/usr/bin/env python3
"""Free dictionary fallback for words the local library does not hold.

The bundled dictionary (lexicon/) and the glossary are curated: they cover the
words this tutor teaches, and nothing else. A learner who asks about a real
word outside that set used to be told the word did not exist. This module asks
dictionaryapi.dev - free, no key, English Wiktionary underneath (CC BY-SA 3.0)
- and the answer is cached on disk, so the second ask is local again.

Deliberately narrow:

  * one word, Latin letters only. A phrase or a Persian word is somebody
    else's question.
  * miss and error are different. A 404 is an answer and is remembered; a
    timeout is not, so a flaky network cannot poison the cache.
  * FLUENTIFY_NO_WEB_DICT=1 turns the network off entirely (tests, offline).

Definitions come back in English only. There is no Persian gloss here, and
none is invented for it.
"""

import json
import os
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/{}"
CACHE_PATH = Path(os.environ.get(
    "FLUENTIFY_DICT_CACHE",
    str(Path(__file__).resolve().parent / "dictionary_cache.json")))
CACHE_MAX = 800          # entries kept before the oldest are dropped
MISS_SECONDS = 7 * 24 * 3600   # a word Wiktionary lacked is re-asked weekly
TIMEOUT = 3.5
MAX_MEANINGS = 3
MAX_SENSES = 3

_LOCK = threading.Lock()
_CACHE: dict | None = None


def enabled() -> bool:
    return os.environ.get("FLUENTIFY_NO_WEB_DICT", "") not in ("1", "true", "yes")


def clean(word: str) -> str:
    """The dictionary key for a word, or "" when it is not a word to ask about.

    Kept in step with cleanWord() in bot.js: the APK has to ask for exactly the
    same key, or the two caches never share a hit.
    """
    raw = (word or "").strip().lower()
    # A phrase is not this API's question, and stripping the space out of
    # "ice cream" would ask it about "icecream" instead.
    if not raw or any(ch.isspace() for ch in raw):
        return ""
    key = re.sub(r"[^a-z'\-]", "", raw)
    if not re.fullmatch(r"[a-z][a-z'\-]*", key):
        return ""
    return key


def _load() -> dict:
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    try:
        with open(CACHE_PATH, encoding="utf-8") as f:
            data = json.load(f)
        _CACHE = data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        _CACHE = {}
    return _CACHE


def _save(cache: dict) -> None:
    """Write through a temp file: a half-written cache must never be read."""
    if len(cache) > CACHE_MAX:
        keep = sorted(cache.items(), key=lambda kv: kv[1].get("at", 0))
        cache = dict(keep[-CACHE_MAX:])
    tmp = CACHE_PATH.with_suffix(".tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, separators=(",", ":"))
        os.replace(tmp, CACHE_PATH)
    except OSError:
        pass


def _normalize(payload) -> dict | None:
    """The API's array reduced to what a learner is shown."""
    if not isinstance(payload, list) or not payload:
        return None
    first = None
    for item in payload:
        if isinstance(item, dict) and item.get("meanings"):
            first = item
            break
    if not first:
        return None

    phonetic = (first.get("phonetic") or "").strip()
    if not phonetic:
        for p in first.get("phonetics") or []:
            if isinstance(p, dict) and (p.get("text") or "").strip():
                phonetic = p["text"].strip()
                break

    meanings = []
    for meaning in (first.get("meanings") or [])[:MAX_MEANINGS]:
        if not isinstance(meaning, dict):
            continue
        senses = []
        for d in (meaning.get("definitions") or [])[:MAX_SENSES]:
            if not isinstance(d, dict):
                continue
            text = (d.get("definition") or "").strip()
            if not text:
                continue
            senses.append({"d": text,
                           "ex": (d.get("example") or "").strip()})
        if senses:
            meanings.append({"pos": (meaning.get("partOfSpeech") or "").strip(),
                             "senses": senses})
    if not meanings:
        return None
    return {"word": (first.get("word") or "").strip(), "ipa": phonetic,
            "meanings": meanings}


def lookup(word: str) -> dict | None:
    """A word's entry, from the cache or the API. None when there is none."""
    key = clean(word)
    if not key or not enabled():
        return None

    with _LOCK:
        cache = _load()
        hit = cache.get(key)
    if hit is not None:
        if hit.get("entry"):
            return hit["entry"]
        if time.time() - hit.get("at", 0) < MISS_SECONDS:
            return None

    url = API_URL.format(urllib.parse.quote(key))
    request = urllib.request.Request(url, headers={
        "User-Agent": "Fluentify-tutor/1.0 (vocabulary lookup)",
        "Accept": "application/json",
    })
    entry = None
    known_miss = False
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            entry = _normalize(json.load(response))
        known_miss = entry is None
    except urllib.error.HTTPError as err:
        # 404 is the API saying "no such word" - an answer worth remembering.
        known_miss = err.code == 404
        entry = None
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        # The network failed. Say nothing and remember nothing.
        return None

    if entry is None and not known_miss:
        return None

    with _LOCK:
        cache = _load()
        cache[key] = {"at": time.time(), "entry": entry}
        _save(cache)
    return entry
