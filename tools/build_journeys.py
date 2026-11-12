#!/usr/bin/env python3
"""Build journeys.json from the journey sources.

    python3 tools/build_journeys.py

A journey is one topic taught in stages. The source files in tools/ are flat
pipe rows, one row per fact, because a nested JSON literal is impossible to
diff and easy to break by hand:

    J | id | order | icon | title_en | title_fa | audiences | categories | blurb_en | blurb_fa
    O | stage | objective_en | objective_fa
    X | stage | kind | en | fa | meaning_en | meaning_fa | register | example_en | example_fa | alternative
    P | stage | frame | example_en | example_fa | note_en | note_fa
    S | stage | en | fa | use_en | use_fa | level | politeness
    D | stage | title_en | title_fa | speaker_a | speaker_b
    L | stage | speaker | en | fa
    C | stage | title_en | title_fa | situation_en | situation_fa | task_en | task_fa | answer_en | answer_fa
    Q | stage | question_en | question_fa | right | wrong_a | wrong_b | why_en | why_fa

A stage does not carry its vocabulary, sentences and dialogue. It names the
travel categories it teaches, and the client joins them by id at run time, so
there is exactly one copy of the travel bank and one set of ids. Everything a
journey adds of its own - expressions, idioms, patterns, extra sentences,
dialogues, scenarios, practice - lives here.

The build fails loudly rather than writing a journey with a hole in it.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRAVEL = ROOT / "travel.json"
OUT = ROOT / "journeys.json"
SOURCES = [ROOT / "tools" / "journeys_travel_a.txt",
           ROOT / "tools" / "journeys_travel_b.txt"]

KINDS = {"expression", "idiom", "phrasal_verb", "collocation"}
LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
MIN_OBJECTIVES = 3
MIN_EXPRESSIONS = 4
MIN_PATTERNS = 2
MIN_SENTENCES = 2
MIN_DIALOGUE_LINES = 6
MIN_SCENARIOS = 2
MIN_PRACTICE = 3


def die(msg):
    print("FAIL  " + msg)
    raise SystemExit(1)


def split(row, where):
    parts = [p.strip() for p in row.split("|")]
    return parts, where


def main() -> int:
    travel = json.loads(TRAVEL.read_text(encoding="utf-8"))
    categories = {c["id"]: c for c in travel["categories"]}

    stages = []
    by_id = {}
    current = None

    for path in SOURCES:
        if not path.exists():
            die(f"missing source {path.name}")
        for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            where = f"{path.name}:{n}"
            tag, _, rest = line.partition("|")
            tag = tag.strip()
            f = [p.strip() for p in rest.split("|")]

            if tag == "J":
                if len(f) != 9:
                    die(f"{where}: a stage header needs 9 fields, got {len(f)}")
                ident, order, icon, en, fa, aud, cats, blurb_en, blurb_fa = f
                if ident in by_id:
                    die(f"{where}: stage {ident} is declared twice")
                refs = [c.strip() for c in cats.split(",") if c.strip()]
                for r in refs:
                    if r not in categories:
                        die(f"{where}: stage {ident} names unknown category {r!r}")
                current = {
                    "id": ident, "order": int(order), "icon": icon,
                    "title_en": en, "title_fa": fa,
                    "audiences": [a.strip() for a in aud.split(",") if a.strip()],
                    "refs": refs,
                    "blurb_en": blurb_en, "blurb_fa": blurb_fa,
                    "objectives": [], "expressions": [], "patterns": [],
                    "sentences": [], "dialogue": None,
                    "scenarios": [], "practice": [],
                }
                if not current["audiences"]:
                    die(f"{where}: stage {ident} has no audience")
                stages.append(current)
                by_id[ident] = current
                continue

            if current is None:
                die(f"{where}: row before any J header")

            # A row may repeat the stage id as its first field. Both forms are
            # allowed so a long source file stays readable, and the id is
            # dropped here so every tag has one field count to check against.
            if f and f[0] == current["id"]:
                f = f[1:]

            if tag == "O":
                if len(f) != 2:
                    die(f"{where}: an objective needs 2 fields")
                current["objectives"].append({"en": f[0], "fa": f[1]})
            elif tag == "X":
                if len(f) != 9:
                    die(f"{where}: an expression needs 9 fields, got {len(f)}")
                kind, en, fa, men, mfa, reg, ex, exfa, alt = f
                if kind not in KINDS:
                    die(f"{where}: unknown expression kind {kind!r}")
                current["expressions"].append({
                    "id": f"{current['id']}-x{len(current['expressions']) + 1}",
                    "kind": kind, "en": en, "fa": fa,
                    "meaning_en": men, "meaning_fa": mfa,
                    "register": reg, "example_en": ex, "example_fa": exfa,
                    "alt": alt,
                })
            elif tag == "P":
                # A pattern with a Persian note carries one field more; both
                # forms are legal because the note is optional content.
                if len(f) not in (4, 5):
                    die(f"{where}: a pattern needs 4 or 5 fields, got {len(f)}")
                current["patterns"].append({
                    "frame": f[0], "example_en": f[1], "example_fa": f[2],
                    "note_en": f[3], "note_fa": f[4] if len(f) == 5 else "",
                })
            elif tag == "PF":
                if len(f) != 5:
                    die(f"{where}: a pattern with a Persian note needs 5 fields")
                current["patterns"].append({
                    "frame": f[0], "example_en": f[1], "example_fa": f[2],
                    "note_en": f[3], "note_fa": f[4],
                })
            elif tag == "S":
                if len(f) != 7:
                    die(f"{where}: a sentence needs 7 fields, got {len(f)}")
                en, fa, use_en, use_fa, level, polite, alt = f
                if level not in LEVELS:
                    die(f"{where}: unknown level {level!r}")
                current["sentences"].append({
                    "id": f"{current['id']}-s{len(current['sentences']) + 1}",
                    "en": en, "fa": fa, "use_en": use_en, "use_fa": use_fa,
                    "level": level, "polite": polite, "alt": alt,
                })
            elif tag == "D":
                if len(f) != 4:
                    die(f"{where}: a dialogue header needs 4 fields")
                if current["dialogue"]:
                    die(f"{where}: stage {current['id']} already has a dialogue")
                current["dialogue"] = {
                    "title_en": f[0], "title_fa": f[1],
                    "speakers": [f[2], f[3]], "lines": [],
                }
            elif tag == "L":
                if len(f) != 3:
                    die(f"{where}: a dialogue line needs 3 fields")
                if not current["dialogue"]:
                    die(f"{where}: line before any D header")
                if f[0] not in current["dialogue"]["speakers"]:
                    die(f"{where}: speaker {f[0]!r} is not in the D header")
                current["dialogue"]["lines"].append(
                    {"who": f[0], "en": f[1], "fa": f[2]})
            elif tag == "C":
                if len(f) != 8:
                    die(f"{where}: a scenario needs 8 fields, got {len(f)}")
                current["scenarios"].append({
                    "title_en": f[0], "title_fa": f[1],
                    "situation_en": f[2], "situation_fa": f[3],
                    "task_en": f[4], "task_fa": f[5],
                    "answer_en": f[6], "answer_fa": f[7],
                })
            elif tag == "Q":
                if len(f) != 7:
                    die(f"{where}: a practice item needs 7 fields, got {len(f)}")
                qen, qfa, right, w1, w2, why_en, why_fa = f
                if len({right, w1, w2}) != 3:
                    die(f"{where}: the three practice options are not distinct")
                current["practice"].append({
                    "id": f"{current['id']}-q{len(current['practice']) + 1}",
                    "q_en": qen, "q_fa": qfa,
                    "options": [right, w1, w2], "answer": right,
                    "why_en": why_en, "why_fa": why_fa,
                })
            else:
                die(f"{where}: unknown row tag {tag!r}")

    if not stages:
        die("no stages were read")

    for st in stages:
        sid = st["id"]
        if len(st["objectives"]) < MIN_OBJECTIVES:
            die(f"{sid}: fewer than {MIN_OBJECTIVES} objectives")
        if len(st["expressions"]) < MIN_EXPRESSIONS:
            die(f"{sid}: fewer than {MIN_EXPRESSIONS} expressions or idioms")
        if len(st["patterns"]) < MIN_PATTERNS:
            die(f"{sid}: fewer than {MIN_PATTERNS} reusable patterns")
        if len(st["sentences"]) < MIN_SENTENCES:
            die(f"{sid}: fewer than {MIN_SENTENCES} sentences of its own")
        if len(st["scenarios"]) < MIN_SCENARIOS:
            die(f"{sid}: fewer than {MIN_SCENARIOS} scenarios")
        if len(st["practice"]) < MIN_PRACTICE:
            die(f"{sid}: fewer than {MIN_PRACTICE} practice items")
        d = st["dialogue"]
        if not d:
            die(f"{sid}: no dialogue")
        if len(d["lines"]) < MIN_DIALOGUE_LINES:
            die(f"{sid}: dialogue is shorter than {MIN_DIALOGUE_LINES} lines")
        if len({l['who'] for l in d['lines']}) < 2:
            die(f"{sid}: dialogue has one speaker")
        if not st["refs"]:
            die(f"{sid}: names no travel categories to teach from")

    stages.sort(key=lambda s: s["order"])
    orders = [s["order"] for s in stages]
    if orders != list(range(1, len(stages) + 1)):
        die(f"stage order is not 1..{len(stages)}: {orders}")

    levels = sorted({s["level"] for st in stages for s in st["sentences"]})
    # Count what the journey actually reaches, once: a category two stages both
    # point at is one set of sentences, not two.
    reached = sorted({c for st in stages for c in st["refs"]})
    vocab_refs = sum(len(categories[c]["vocab"]) for c in reached)
    sentence_refs = sum(len(categories[c]["sentences"]) for c in reached)
    bank_vocab = sum(len(c["vocab"]) for c in categories.values())
    bank_sentence = sum(len(c["sentences"]) for c in categories.values())

    out = {
        "_meta": {
            "version": 1,
            "title_en": "Fluentify Journeys",
            "title_fa": "سفرهای فلوئنتیفای",
            "intro_en": ("One topic, taught in the order you meet it: what it is, "
                         "the words, the expressions people really use, the "
                         "sentences, the conversations, and then the situations "
                         "where you have to answer yourself."),
            "intro_fa": ("یک موضوع، به همان ترتیبی که در واقعیت با آن روبه‌رو "
                         "می‌شوی: تعریف، واژه‌ها، عبارت‌هایی که مردم واقعاً به کار "
                         "می‌برند، جمله‌ها، گفت‌وگوها و سپس موقعیت‌هایی که باید خودت "
                         "پاسخ بدهی."),
            "note_en": ("These are language lessons, not legal, immigration or "
                        "medical advice. Rules differ by country: ask the "
                        "official in front of you."),
            "note_fa": ("این‌ها درس زبان‌اند، نه مشاورهٔ حقوقی، مهاجرتی یا پزشکی. "
                        "قاعده‌های هر کشور فرق دارد؛ از مأمور رسمی بپرس."),
            "sources": ("Original material written for Fluentify in American "
                        "English. Vocabulary, sentences and dialogue bank: "
                        "travel.json, joined by id rather than copied."),
            "levels": levels,
            "stats": {
                "stages": len(stages),
                "expressions": sum(len(s["expressions"]) for s in stages),
                "patterns": sum(len(s["patterns"]) for s in stages),
                "sentences": sum(len(s["sentences"]) for s in stages),
                "dialogues": len(stages),
                "scenarios": sum(len(s["scenarios"]) for s in stages),
                "practice": sum(len(s["practice"]) for s in stages),
                "bank_sentences": sentence_refs,
                "bank_words": vocab_refs,
            },
        },
        "journeys": [{
            "id": "travel",
            "topic": "travel",
            "title_en": "Travel Journey",
            "title_fa": "سفر: از رزرو تا بازگشت",
            "icon": "🧳",
            "audiences": ["kids", "adults"],
            "blurb_en": ("From the first booking to the last check-out, in the "
                         "order the journey happens."),
            "blurb_fa": ("از نخستین رزرو تا آخرین تخلیه، به همان ترتیبی که سفر "
                         "پیش می‌رود."),
            "stages": stages,
        }],
    }

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    st = out["journeys"][0]
    print(f"PASS  travel journey: {len(stages)} stages, "
          f"{out['_meta']['stats']['expressions']} expressions and idioms, "
          f"{out['_meta']['stats']['patterns']} patterns, "
          f"{out['_meta']['stats']['sentences']} own sentences, "
          f"{out['_meta']['stats']['dialogues']} dialogues, "
          f"{out['_meta']['stats']['scenarios']} scenarios, "
          f"{out['_meta']['stats']['practice']} practice items; joins "
          f"{sentence_refs} bank sentences and {vocab_refs} bank words")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
