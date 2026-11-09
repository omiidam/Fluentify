#!/usr/bin/env python3
"""Rewrites the British IPA in books.json and daily.json as General American.

Two sources, in order:

1. the audio-backed US transcriptions already cached in tools/.cache (openjam,
   variant "us"), keyed by headword. These are rhotic and carry the American
   vowel, so they are used wherever they exist.
2. a symbol conversion of the existing transcription, for headwords the cache
   does not carry. It changes the vowel inventory (ɒ, əʊ, ɜː, e, ɑː, ɔː) and
   restores a final -er, but it does not invent an /r/ in the middle of a word:
   doing that from symbols alone produced falter /ˈfɔrltər/ and wary /ˈwɛrri/.

A short table of exceptions covers headwords where the cached transcription is
wrong or uses a different American reading (numb, thorough, qualify, data).

Run with --check to report; --write to apply.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
CACHE = ROOT / "tools/.cache/sources/openjam"

# General American readings that differ from what a symbol swap would give.
EXCEPTIONS = {
    "data": "ˈdeɪtə", "tomato": "təˈmeɪtoʊ", "either": "ˈiðər",
    "neither": "ˈniðər", "schedule": "ˈskɛdʒuːl", "privacy": "ˈpraɪvəsi",
    "advertisement": "ˌædvərˈtaɪzmənt", "vitamin": "ˈvaɪtəmɪn",
    "leisure": "ˈliːʒər", "route": "ruːt", "progress": "ˈprɑɡrəs",
    "process": "ˈprɑsɛs", "project": "ˈprɑdʒɛkt", "research": "ˈriːsɝːtʃ",
    "detail": "ˈdiːteɪl", "adult": "əˈdʌlt", "address": "ˈædrɛs",
    "garage": "ɡəˈrɑʒ", "herb": "ɝːb", "mobile": "ˈmoʊbəl",
    "sorry": "ˈsɑri", "borrow": "ˈbɑroʊ", "tomorrow": "təˈmɑroʊ",
    "orange": "ˈɔrɪndʒ", "horror": "ˈhɔrər", "forest": "ˈfɔrɪst",
    "moral": "ˈmɔrəl", "squirrel": "ˈskwɝːəl", "hurry": "ˈhɝːi",
    "worry": "ˈwɝːi", "courage": "ˈkɝːɪdʒ", "flourish": "ˈflɝːɪʃ",
    "nourish": "ˈnɝːɪʃ", "bird": "bɝːd", "girl": "ɡɝːl", "work": "wɝːk",
    "word": "wɝːd", "world": "wɝːld", "learn": "lɝːn", "heard": "hɝːd",
    "earth": "ɝːθ", "early": "ˈɝːli", "journey": "ˈdʒɝːni",
    "courtesy": "ˈkɝːtəsi", "numb": "nʌm", "comb": "koʊm", "climb": "klaɪm",
    "doubt": "daʊt", "thorough": "ˈθɝːoʊ", "qualify": "ˈkwɑləˌfaɪ",
    "urban": "ˈɝːbən", "urgent": "ˈɝːdʒənt", "absurd": "əbˈsɝːd",
    "au courant": "ˌoʊ kʊˈrɑ̃", "genre": "ˈʒɑnrə", "milieu": "mɪlˈjɜː",
    "pariah": "pəˈraɪə", "austere": "ɔˈstɪr", "excoriate": "ɛkˈskɔriˌeɪt",
    "bona fide": "ˌboʊnə ˈfaɪdi", "impresario": "ˌɪmprɪˈsɑriˌoʊ",
    "falter": "ˈfɔltər", "chiropractor": "ˈkaɪrəˌpræktər",
}

# Two-letter sequences where the cache's ər stands for the r-colored STRUT
# vowel (urban ˈərbən), which this course writes ɝː.
STRUT = {"urban", "urgent", "absurd", "occur", "burden", "curve", "curl",
         "hurt", "nurse", "purse", "burn", "turn", "return", "concern",
         "journey", "courtesy", "worst", "worth", "work", "word", "world",
         "worse", "search", "research", "person", "certain", "service",
         "version", "perfect", "circumstance", "circuit", "virtue"}


def us_table():
    words = json.loads((CACHE / "words_en.json").read_text(encoding="utf-8"))
    phon = json.loads((CACHE / "phonetics.json").read_text(encoding="utf-8"))
    by_id = {w["id"]: w["english"].lower() for w in words}
    table = {}
    for p in phon:
        if p.get("variant") != "us" or not p.get("ipa"):
            continue
        word = by_id.get(p["word_id"])
        if word:
            table.setdefault(word, p["ipa"])
    return table


def tidy(ipa: str) -> str:
    s = ipa.strip().strip("/")
    s = s.replace("ʤ", "dʒ").replace("ʧ", "tʃ").replace("g", "ɡ")
    s = s.replace("ɚ", "ər")
    return s


def fallback(word: str, ipa: str) -> str:
    """Symbol conversion only, for headwords the cache does not carry."""
    s = ipa.strip().strip("/")
    key = word.lower()
    s = s.replace("əʊ", "oʊ")
    s = s.replace("ɒ", "ɑ")
    s = s.replace("ɜː", "ɝː")
    s = s.replace("ɑː", "ɑ")
    s = s.replace("ɔː", "ɔ")
    s = re.sub(r"e(?!ɪ)", "ɛ", s)
    # the -er / -or / -ar ending
    if re.search(r"(r|re|our|er|or|ar|ure)$", key) and s.endswith("ə"):
        s = s[:-1] + "ər"
    return s


def convert(word: str, ipa: str, table: dict) -> str:
    key = word.lower()
    if key in EXCEPTIONS:
        return "/" + EXCEPTIONS[key] + "/"
    raw = table.get(key)
    if raw:
        return "/" + tidy(raw) + "/"
    return "/" + fallback(word, ipa) + "/"


def walk(node, out, table):
    if isinstance(node, dict):
        word = node.get("word") or node.get("en")
        if isinstance(node.get("ipa"), str) and isinstance(word, str) \
                and len(word) < 30:
            new = convert(word, node["ipa"], table)
            if new != node["ipa"]:
                out.append((word, node["ipa"], new))
        for v in node.values():
            walk(v, out, table)
    elif isinstance(node, list):
        for v in node:
            walk(v, out, table)


def apply_text(path: Path, changes) -> int:
    """Rewrite the raw text rather than re-serialising: the files are hand-
    formatted for review, and a JSON dump would reflow all 550 KB of them."""
    text = path.read_text(encoding="utf-8")
    mapping = {old: new for _word, old, new in changes}
    for old, new in mapping.items():
        token = json.dumps(old, ensure_ascii=False)
        text = text.replace(f'"ipa": {token}',
                            f'"ipa": {json.dumps(new, ensure_ascii=False)}')
    path.write_text(text, encoding="utf-8")
    return len(mapping)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    table = us_table()
    total = 0
    for name in ("books.json", "daily.json"):
        path = ROOT / name
        data = json.loads(path.read_text(encoding="utf-8"))
        changes = []
        walk(data, changes, table)
        total += len(changes)
        print(f"{name}: {len(changes)} transcriptions")
        for word, old, new in changes[:5]:
            print(f"  {word:16} {old:20} -> {new}")
        if args.write and changes:
            apply_text(path, changes)
    print(f"{'rewrote' if args.write else 'would rewrite'} {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
