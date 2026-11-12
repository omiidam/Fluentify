#!/usr/bin/env python3
"""Build data/wordquest.json from the authored sources in tools/.

Three source files, all hand-written:

  tools/wordquest_words.txt    the word bank (pre-A1 to B1)
  tools/wordquest_words2.txt   the short CVC and function words
  tools/wordquest_words3.txt   the upper-level words
  tools/wordquest_puzzles.txt  the worlds and their racks

Nothing about the game is generated at runtime: this script produces the whole
puzzle set, checks every claim in it, and fails loudly rather than shipping a
puzzle a child cannot solve. Run it after touching any source file, then
tools/check_wordquest.py, which re-checks the finished JSON without trusting it.
"""
from __future__ import annotations

import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
OUT = ROOT / "wordquest.json"

LEVELS = ["Pre-A1", "A1", "A2", "B1", "B2", "C1", "C2"]
LEVEL_RANK = {name: i for i, name in enumerate(LEVELS)}
FIELDS = ("word", "level", "pos", "fa", "def_en", "example_en", "example_fa", "picture")
# a ninth field is optional: IPA, when somebody has checked one for the word


class BuildError(Exception):
    pass


def fail(msg: str) -> None:
    raise BuildError(msg)


# --------------------------------------------------------------------------- bank
def read_bank() -> dict[str, dict]:
    files = sorted(TOOLS.glob("wordquest_words*.txt"))
    if not files:
        fail("no word bank files found")
    bank: dict[str, dict] = {}
    for path in files:
        for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("|")
            where = f"{path.name}:{number}"
            if len(parts) not in (len(FIELDS), len(FIELDS) + 1):
                fail(f"{where}: {len(parts)} fields, expected {len(FIELDS)}")
            record = dict(zip(FIELDS, (p.strip() for p in parts)))
            record["ipa"] = parts[-1].strip() if len(parts) == len(FIELDS) + 1 else ""
            word = record["word"]
            if not re.fullmatch(r"[a-z]+", word):
                fail(f"{where}: '{word}' is not a lowercase a-z word")
            if record["level"] not in LEVEL_RANK:
                fail(f"{where}: unknown CEFR level '{record['level']}'")
            if record["word"] in bank:
                fail(f"{where}: '{word}' appears twice in the bank")
            for field in ("fa", "def_en", "example_en", "example_fa", "picture", "pos"):
                if not record[field]:
                    fail(f"{where}: '{word}' has an empty {field}")
            if len(record["def_en"]) < 12:
                fail(f"{where}: '{word}' definition is too short to teach anything")
            if not re.search(r"[A-Za-z]", record["def_en"]):
                fail(f"{where}: '{word}' definition has no English")
            if not re.search(r"[\u0600-\u06FF]", record["fa"]):
                fail(f"{where}: '{word}' has no Persian translation")
            if not re.search(r"[\u0600-\u06FF]", record["example_fa"]):
                fail(f"{where}: '{word}' has no Persian example")
            bank[word] = record
    if len(bank) < 60:
        fail(f"the bank has only {len(bank)} words; a game needs more")
    return bank


# ------------------------------------------------------------------------ puzzles
WORLD_FIELDS = ("id", "order", "name_en", "name_fa", "emoji", "level",
                "theme_en", "theme_fa", "blurb_en", "blurb_fa")
STAGE_FIELDS = ("world", "order", "rack", "required", "title_en", "title_fa")


def read_puzzles() -> tuple[list[dict], list[dict]]:
    path = TOOLS / "wordquest_puzzles.txt"
    worlds: list[dict] = []
    stages: list[dict] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        where = f"wordquest_puzzles.txt:{number}"
        if parts[0] == "W":
            if len(parts) != 1 + len(WORLD_FIELDS):
                fail(f"{where}: a world needs {len(WORLD_FIELDS)} fields")
            worlds.append(dict(zip(WORLD_FIELDS, parts[1:])))
        elif parts[0] == "P":
            if len(parts) != 1 + len(STAGE_FIELDS):
                fail(f"{where}: a puzzle needs {len(STAGE_FIELDS)} fields")
            stages.append(dict(zip(STAGE_FIELDS, parts[1:])))
        else:
            fail(f"{where}: unknown row type '{parts[0]}'")
    if not worlds or not stages:
        fail("the map is empty")
    return worlds, stages


def spellable(word: str, rack: str) -> bool:
    have = Counter(rack.lower())
    need = Counter(word)
    return all(need[letter] <= have[letter] for letter in need) and len(word) <= len(rack)


def ipa_map() -> dict[str, str]:
    """IPA the bank itself supplied, nothing guessed.

    The app's dictionary (senses.json) stores senses as [part of speech,
    definition, Persian, example] with no pronunciation, so there is no IPA to
    inherit. A record may carry one as its ninth field; the UI simply hides the
    IPA line for words that do not have one.
    """
    return {}


# ------------------------------------------------------------------------- build
def build() -> dict:
    bank = read_bank()
    worlds, stages = read_puzzles()

    world_ids = [w["id"] for w in worlds]
    if len(set(world_ids)) != len(world_ids):
        fail("two worlds share an id")
    orders = sorted(int(w["order"]) for w in worlds)
    if orders != list(range(1, len(worlds) + 1)):
        fail(f"world order is not 1..{len(worlds)}: {orders}")

    seen_ids: set[str] = set()
    used: Counter = Counter()
    by_world: dict[str, list[dict]] = {wid: [] for wid in world_ids}

    for stage in stages:
        world = stage["world"]
        if world not in by_world:
            fail(f"puzzle '{stage['title_en']}' names an unknown world '{world}'")
        rack = stage["rack"].upper()
        if not re.fullmatch(r"[A-Z]{3,10}", rack):
            fail(f"'{stage['title_en']}': rack '{stage['rack']}' is not 3-10 A-Z letters")
        if rack.isupper() is False:
            fail("unreachable")
        required = [w.strip().lower() for w in stage["required"].split(",") if w.strip()]
        if len(required) < 3:
            fail(f"'{stage['title_en']}': a puzzle needs at least three required words")
        if len(set(required)) != len(required):
            fail(f"'{stage['title_en']}': a required word is listed twice")
        for word in required:
            if word not in bank:
                fail(f"'{stage['title_en']}': '{word}' has no record in the bank")
            if not spellable(word, rack):
                fail(f"'{stage['title_en']}': '{word}' cannot be spelled from {rack}")

        # every other bank word the rack can spell is a bonus word, so a bonus
        # word always carries the same verified record as a required one
        # "as" and "in" are two letters, so they are never offered as a bonus
        # word: three letters is the floor for a discovery to feel like one
        bonus = sorted(
            (w for w in bank if w not in required and len(w) >= 3 and spellable(w, rack)),
            key=lambda w: (len(w), w),
        )

        stage_id = f"{world}-{stage['order']}"
        if stage_id in seen_ids:
            fail(f"duplicate stage id {stage_id}")
        seen_ids.add(stage_id)
        stage_level = max((bank[w]["level"] for w in required), key=lambda l: LEVEL_RANK[l])

        # a stable shuffle: the same rack looks the same on every device and in
        # the APK, and a rebuilt JSON differs only where a word changed
        letters = list(rack)
        random.Random(f"wordquest:{stage_id}").shuffle(letters)

        used.update(required)
        used.update(bonus)

        by_world[world].append({
            "id": stage_id,
            "world": world,
            "order": int(stage["order"]),
            "title_en": stage["title_en"],
            "title_fa": stage["title_fa"],
            "letters": letters,
            "rack": rack,
            "level": stage_level,
            "required": required,
            "bonus": bonus,
        })

    for wid in world_ids:
        group = by_world[wid]
        if not group:
            fail(f"world '{wid}' has no puzzles")
        group.sort(key=lambda s: s["order"])
        got = [s["order"] for s in group]
        if got != list(range(1, len(group) + 1)):
            fail(f"world '{wid}' stage order is {got}, expected 1..{len(group)}")

    unused = sorted(w for w in bank if not used[w])
    ipa = ipa_map()

    words_out = {}
    for word in sorted(bank):
        record = bank[word]
        words_out[word] = {
            "spelling": word,
            "level": record["level"],
            "pos": record["pos"],
            "fa": record["fa"],
            "def_en": record["def_en"],
            "example_en": record["example_en"],
            "example_fa": record["example_fa"],
            "picture": record["picture"],
            "ipa": record.get("ipa", "") or ipa.get(word, ""),
        }

    levels = Counter()
    for wid in world_ids:
        for stage in by_world[wid]:
            levels[stage["level"]] += 1

    badges = []
    for world in sorted(worlds, key=lambda w: int(w["order"])):
        badges.append({
            "id": f"world-{world['id']}",
            "name_en": f"{world['name_en']} cleared",
            "name_fa": f"{world['name_fa']} کامل شد",
            "emoji": world["emoji"],
            "kind": "world",
            "world": world["id"],
            "need": len(by_world[world['id']]),
        })
    badges += [
        {"id": "first-word", "name_en": "First word found", "name_fa": "نخستین واژه",
         "emoji": "🌟", "kind": "words", "need": 1},
        {"id": "ten-words", "name_en": "Ten words", "name_fa": "ده واژه",
         "emoji": "📚", "kind": "words", "need": 10},
        {"id": "fifty-words", "name_en": "Fifty words", "name_fa": "پنجاه واژه",
         "emoji": "🧠", "kind": "words", "need": 50},
        {"id": "every-word", "name_en": "Every word in the world",
         "name_fa": "همهٔ واژه‌ها", "emoji": "🏆", "kind": "all", "need": len(words_out)},
    ]

    return {
        "version": 1,
        "title_en": "Fluentify Word Quest",
        "title_fa": "جست‌وجوی واژه",
        "tagline_en": "Find the hidden words, one letter at a time.",
        "tagline_fa": "واژه‌های پنهان را پیدا کن، حرف به حرف.",
        "levels": LEVELS,
        "worlds": [
            {
                "id": w["id"],
                "order": int(w["order"]),
                "name_en": w["name_en"],
                "name_fa": w["name_fa"],
                "emoji": w["emoji"],
                "level": w["level"],
                "theme_en": w["theme_en"],
                "theme_fa": w["theme_fa"],
                "blurb_en": w["blurb_en"],
                "blurb_fa": w["blurb_fa"],
                "stages": by_world[w["id"]],
            }
            for w in sorted(worlds, key=lambda w: int(w["order"]))
        ],
        "words": words_out,
        "badges": badges,
        "_meta": {
            "source": ["tools/wordquest_words*.txt", "tools/wordquest_puzzles.txt"],
            "word_count": len(words_out),
            "stage_count": len(seen_ids),
            "world_count": len(worlds),
            "stages_per_level": {lvl: levels[lvl] for lvl in LEVELS if levels[lvl]},
            "ipa_count": sum(1 for w in words_out.values() if w["ipa"]),
            "unused_words": unused,
            "built_by": "tools/build_wordquest.py",
        },
    }


def main() -> int:
    try:
        data = build()
    except BuildError as err:
        print(f"wordquest build failed: {err}", file=sys.stderr)
        return 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1, sort_keys=False) + "\n",
                   encoding="utf-8")
    meta = data["_meta"]
    print(f"wrote {OUT.relative_to(ROOT)}: {meta['world_count']} worlds, "
          f"{meta['stage_count']} puzzles, {meta['word_count']} words")
    print(f"  stages per level: {meta['stages_per_level']}")
    print(f"  IPA available for {meta['ipa_count']} words")
    if meta["unused_words"]:
        print(f"  NOT USED by any puzzle ({len(meta['unused_words'])}): "
              f"{' '.join(meta['unused_words'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
