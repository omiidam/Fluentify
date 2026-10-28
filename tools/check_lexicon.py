#!/usr/bin/env python3
"""The dictionary: is the data sound, does it answer, and is it invisible?

The dictionary is knowledge, not a feature. It has no page, no panel, no tab and
no route: a lookup the glossary cannot answer now falls through to it, and four
asks the glossary never could answer (synonyms, opposites, inflected forms, and
one word's meaning read inside the learner's own sentence) are read from it. So
this suite checks three different things:

  data         every shard parses, every entry is the shape the engine reads,
               senses are well-formed, nothing claims a field it does not have,
               and the counts in _meta.json are the counts on disk
  answers      the questions from the feature brief, in English and Persian,
               answered from the lexicon - multiple senses kept apart, a sentence
               picking a sense, a typo offered the right word, a Persian meaning
               leading back to the English headword
  no new UI    no /api/lexicon route, no dictionary panel or nav item, and the
               page still boots without the dictionary present

    python3 tools/check_lexicon.py
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEXICON = ROOT / "lexicon"
WEBAPP = ROOT / "webapp.py"
BOT = ROOT / "android/app/src/main/assets/www/bot.js"
BUILD = ROOT / "build_apk_ui.py"

POS = {"noun", "verb", "adjective", "adverb"}
PERSIAN = re.compile(r"[\u0600-\u06FF]")
LATIN = re.compile(r"[A-Za-z]")

problems: list[str] = []


def fail(what: str) -> None:
    problems.append(what)


def check(ok: bool, what: str) -> bool:
    if not ok:
        fail(what)
    return ok


def load_shards() -> dict[str, dict]:
    return {
        p.stem: json.loads(p.read_text(encoding="utf-8"))
        for p in sorted(LEXICON.glob("*.json"))
        if not p.stem.startswith("_")
    }


def check_data(shards: dict[str, dict]) -> dict:
    meta = json.loads((LEXICON / "_meta.json").read_text(encoding="utf-8"))
    stats = {"words": 0, "senses": 0, "fa": 0, "examples": 0, "ipa": 0,
             "forms": 0}
    for name, shard in shards.items():
        # a shard the reader asks for by name must be self-identifying: the
        # loader caches by filename, and a mismatch means a word in the wrong
        # bucket, i.e. a lookup that depends on the file being right by luck
        check(shard.get("_shard") == name,
              f"shard {name}.json says it is {shard.get('_shard')!r}")
        check(isinstance(shard.get("w"), dict) and isinstance(shard.get("f"), dict),
              f"shard {name}.json has no w/f maps")
        for key, entry in shard["w"].items():
            stats["words"] += 1
            check(key == key.lower().strip(), f"{name}: key {key!r} is not normalised")
            check(bool(LATIN.search(key)), f"{name}: key {key!r} is not English")
            pos = entry.get("p") or []
            check(bool(pos) and set(pos) <= POS,
                  f"{name}/{key}: parts of speech {pos!r} are not the four the "
                  f"engine labels")
            senses = entry.get("s") or []
            check(bool(senses), f"{name}/{key}: no senses - nothing to answer with")
            check(len(senses) <= 4, f"{name}/{key}: {len(senses)} senses, the "
                                    f"reader prints the first four")
            for sense in senses:
                check(isinstance(sense, list) and len(sense) == 5,
                      f"{name}/{key}: sense is not [pos, def, fa, ex, ex_fa]")
                if not (isinstance(sense, list) and len(sense) == 5):
                    continue
                check(sense[0] in POS, f"{name}/{key}: sense pos {sense[0]!r}")
                check(bool(sense[1]), f"{name}/{key}: empty English definition")
                # A Persian column that is missing is honest; a Persian column
                # holding English is not.
                check(not sense[2] or bool(PERSIAN.search(sense[2])),
                      f"{name}/{key}: Persian meaning {sense[2]!r} has no Persian")
                stats["senses"] += 1
                if sense[2]:
                    stats["fa"] += 1
                if sense[3]:
                    stats["examples"] += 1
                    check(bool(LATIN.search(sense[3])),
                          f"{name}/{key}: example {sense[3][:40]!r} is not English")
                    check(not sense[4] or bool(PERSIAN.search(sense[4])),
                          f"{name}/{key}: example translation {sense[4][:40]!r} "
                          f"has no Persian")
            if entry.get("i"):
                stats["ipa"] += 1
                check(any((entry["i"] or {}).values()),
                      f"{name}/{key}: IPA block is empty")
            for pair in entry.get("f") or []:
                check(isinstance(pair, list) and len(pair) == 2,
                      f"{name}/{key}: inflected form {pair!r} is not [form, label]")
                if isinstance(pair, list) and len(pair) == 2:
                    stats["forms"] += 1
                    # One form can belong to two headwords - "leaves" is both
                    # the plural of leaf and the verb leave, "foregoing" both
                    # forgo and forego - so the shard keeps one target. What
                    # must hold is that the target is a real headword in this
                    # shard, not a misspelling of one.
                    target = shard["f"].get(pair[0])
                    check(isinstance(target, str) and target in shard["w"],
                          f"{name}: form {pair[0]!r} resolves to {target!r}, "
                          f"which is not in this shard")

    # the meta file is what the README and the report quote, so it has to be the
    # truth on disk rather than a number someone typed once
    check(meta.get("headwords") == stats["words"],
          f"_meta.json claims {meta.get('headwords')} headwords, "
          f"the shards hold {stats['words']}")
    check(meta.get("senses") == stats["senses"],
          f"_meta.json claims {meta.get('senses')} senses, "
          f"the shards hold {stats['senses']}")
    check(meta.get("persian_meanings") == stats["fa"],
          f"_meta.json claims {meta.get('persian_meanings')} Persian meanings, "
          f"the shards hold {stats['fa']}")
    check(meta.get("shards") == len(shards),
          f"_meta.json claims {meta.get('shards')} shards, found {len(shards)}")
    check(stats["words"] > 15000, f"only {stats['words']} headwords")
    check(stats["fa"] > 0.95 * stats["senses"],
          f"only {stats['fa']}/{stats['senses']} senses have a Persian meaning")

    # the licence and provenance travel with the data: the import is only
    # legitimate while the notice that says where it came from ships with it
    check(bool(meta.get("sources")), "_meta.json carries no source block")
    for src in (meta.get("sources") or []):
        check(bool(src.get("name")) and bool(src.get("licence")),
              f"source {src.get('name')!r} has no licence recorded")
        check("wordnet" in (src.get("licence", "") + src.get("notice", "")).lower()
              or "mit" in (src.get("licence", "")).lower(),
              f"source {src.get('name')!r} is neither MIT nor WordNet-licensed")
    return stats


def check_answers() -> int:
    sys.path.insert(0, str(ROOT))
    from chatbot import ChatBot

    bot = ChatBot()
    answers = 0

    def ask(text: str) -> str:
        nonlocal answers
        reply = bot.respond(text) or ""
        answers += 1
        return reply

    # a definition, with the word, the pronunciation, the part of speech and a
    # Persian meaning
    reply = ask("define achievement")
    check("achievement" in reply, "define achievement: no headword in the answer")
    check("əˈʧivmənt" in reply or "/" in reply, "define achievement: no IPA")
    check(bool(PERSIAN.search(reply)), "define achievement: no Persian meaning")

    # a second language for the same ask
    reply = ask("معنی achievement چیه")
    check(bool(PERSIAN.search(reply)) and "achievement" in reply,
          "Persian definition ask did not answer bilingually")

    # multiple senses are kept apart, not merged
    reply = ask("what does bank mean")
    check("bank" in reply, "bank: no headword")
    check(len(re.findall(r"^\s+\d+\.", reply, re.M)) >= 2,
          "bank: fewer than two senses - meanings were merged")
    check("بانک" in reply, "bank: the financial sense is missing")
    check("کنار رودخانه" in reply or "رودخانه" in reply,
          "bank: the river sense is missing")

    # a sentence picks the sense (both answers must be the dictionary's own)
    reply = ask("what does bank mean in river bank")
    check("رودخانه" in reply.split("\n")[0] or "رودخانه" in reply[:200],
          "river bank: the sentence did not steer the answer to the river sense")

    # synonyms and antonyms, read from the semantic relations
    reply = ask("give me synonyms for beautiful")
    check("beautiful" in reply and "fair" in reply,
          "synonyms for beautiful: no synonyms in the answer")
    reply = ask("what is the opposite of generous")
    check("generous" in reply and "stingy" in reply,
          "opposite of generous: no antonym in the answer")
    reply = ask("مترادف کلمه beautiful رو بگو")
    check(bool(PERSIAN.search(reply)), "Persian synonym ask answered in English only")

    # inflected forms come from the dictionary, not from a guessed ending
    reply = ask("what is the past tense of seek")
    check("sought" in reply, "past of seek: no inflected form")

    # examples with the Persian translation beside them
    reply = ask("give me examples with achieve")
    check("achieve" in reply and "▸" in reply, "examples with achieve: none")

    # a typo is offered the word it was aiming at - and when the word it was
    # aiming at is not in the source, the engine says which word it lacks
    # instead of answering as though it had one ("resilient" is a known gap:
    # the source ships "resilience" but not the adjective)
    reply = ask("what does achievment mean")
    check("achievement" in reply, "achievment: no correction offered")
    reply = ask("what does resilent mean")
    check("resilent" in reply, "resilent: the word was not named in the answer")
    check("resident" in reply or "resilience" in reply,
          "resilent: the nearest held word was not offered")

    # a Persian meaning leads back to the English headword
    heads = bot.lex_persian("شجاعت")
    check("courage" in heads or "bravery" in heads,
          f"Persian index for شجاعت returned {heads[:4]!r}")

    # a word that is genuinely absent is reported, never invented
    reply = ask("what does qzxwv mean")
    check("qzxwv" in reply, "an absent word was not named in the answer")
    check(not re.search(r"\bmean(?:ing)?\b.*\b(?:is|means)\b", reply)
          or "don't have" in reply or "ندارم" in reply,
          "an absent word was answered as if it existed")

    # the dictionary must not take over knowledge the glossary already had
    for text, marker in (("translate apple", "سیب"),
                         ("how do you pronounce apple", "say it slowly"),
                         ("break the ice", "یخ"),
                         ("simple present", "present")):
        reply = ask(text)
        check(marker in reply.lower(),
              f"{text!r} stopped being answered by its own source")

    return answers


def check_no_new_ui() -> None:
    webapp = WEBAPP.read_text(encoding="utf-8")
    bot = BOT.read_text(encoding="utf-8")
    build = BUILD.read_text(encoding="utf-8")

    # the dictionary is knowledge behind the chat: no route, no panel, no nav
    check("/api/lexicon" not in webapp,
          "webapp.py grew a /api/lexicon route - the dictionary is not a page")
    for label in ("dictionary", "lexicon", "واژه\u200cنامه", "دیکشنری"):
        for pattern in (rf'id="{label}panel"', rf"id=\"nav-{label}\"",
                        rf'data-panel="{label}"'):
            check(not re.search(pattern, webapp, re.IGNORECASE),
                  f"the page grew a dictionary surface ({pattern})")

    # the offline bundle: shards are fetched through the engine's own loader,
    # after it is asked which ones the message needs
    check("loadLexiconFor" in bot and "lexShardNames" in bot,
          "bot.js has no lazy shard loader - the APK would load 12 MB at boot")
    check("await bot.loadLexiconFor(text)" in build,
          "the offline send() does not await the shards before respond()")
    check("lexicon" in build and "data/lex" in build.replace("\\", "/")
          or "LEX_DEST" in build,
          "build_apk_ui.py does not package the dictionary into the APK")


def main() -> int:
    for needed in (LEXICON / "_meta.json", LEXICON / "_fa.json"):
        if not needed.exists():
            print(f"FAIL  {needed.name} is missing - run tools/build_lexicon.py")
            return 1

    shards = load_shards()
    # The client asks only for shards this file names. A shard missing from it
    # is a word the app can never find, which looks exactly like a word the
    # dictionary does not have.
    index = json.loads((LEXICON / "_index.json").read_text(encoding="utf-8"))
    check(set(index.get("names") or []) == set(shards),
          "_index.json does not list exactly the shards on disk "
          f"({len(index.get('names') or [])} listed, {len(shards)} present)")
    stats = check_data(shards)
    fa = json.loads((LEXICON / "_fa.json").read_text(encoding="utf-8"))["p"]
    check(len(fa) > 1000, f"the Persian index holds only {len(fa)} keys")
    for meaning, heads in fa.items():
        check(bool(PERSIAN.search(meaning)),
              f"Persian index key {meaning!r} has no Persian in it")
        check(bool(heads) and all(h == h.lower() for h in heads),
              f"Persian index {meaning!r} -> {heads[:3]!r}")
    answers = check_answers()
    check_no_new_ui()

    if problems:
        for p in problems[:40]:
            print("FAIL  " + p)
        if len(problems) > 40:
            print(f"      ... and {len(problems) - 40} more")
        print(f"\nFAIL  {len(problems)} problem(s) with the dictionary")
        return 1

    print(f"PASS  {stats['words']} headwords, {stats['senses']} senses "
          f"({stats['fa']} with a Persian meaning), {stats['examples']} examples, "
          f"{stats['ipa']} with IPA, {len(fa)} Persian lookup keys; "
          f"{answers} questions answered through the existing chat")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
