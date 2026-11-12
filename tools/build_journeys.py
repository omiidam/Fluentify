#!/usr/bin/env python3
"""Build journeys.json from the journey sources.

    python3 tools/build_journeys.py

A journey is one topic taught in stages. The source files in tools/ are flat
pipe rows, one row per fact, because a nested JSON literal is impossible to
diff and easy to break by hand:

    J  | id | order | icon | title_en | title_fa | audiences | categories | blurb_en | blurb_fa
    O  | stage | objective_en | objective_fa
    W  | stage | en | ipa | pos | fa | def_en | sport | icon | level | example_en | example_fa | [ref]
    G  | stage | sport_id, sport_id, ...
    X  | stage | kind | en | fa | meaning_en | meaning_fa | register | example_en | example_fa | alternative
    P  | stage | frame | example_en | example_fa | note_en | [note_fa]
    S  | stage | en | fa | use_en | use_fa | level | politeness
    D  | stage | title_en | title_fa | speaker_a | speaker_b
    L  | stage | speaker | en | fa
    C  | stage | title_en | title_fa | situation_en | situation_fa | task_en | task_fa | answer_en | answer_fa
    Q  | stage | question_en | question_fa | right | wrong_a | wrong_b | why_en | why_fa
    R  | id | en | ipa | fa | category | definition_en | icon | venue | level | equipment | actions | sentence_en | sentence_fa | exchange_en | exchange_fa
    RT | sport | term | fa | meaning_en

Two kinds of vocabulary exist and they are not the same thing:

* A travel stage names the travel categories it teaches, and the client joins
  travel.json by id at run time, so there is exactly one copy of that bank and
  one set of ids.
* A sports stage owns its words with a W row. The sports dictionary does not
  exist in this project, and inventing a second general dictionary to hold it
  would be the duplication the rules forbid, so the words a stage teaches live
  with that stage and carry their own IPA, definition, sport and picture key.
  Where the app's own senses.json already knows the word, the row records its
  key in `ref` so the two say the same thing rather than diverge.

The build fails loudly rather than writing a journey with a hole in it.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRAVEL = ROOT / "travel.json"
SENSES = ROOT / "senses.json"
OUT = ROOT / "journeys.json"

KINDS = {"expression", "idiom", "phrasal_verb", "collocation"}
LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
MIN_OBJECTIVES = 3
MIN_EXPRESSIONS = 4
MIN_PATTERNS = 2
MIN_SENTENCES = 2
MIN_DIALOGUE_LINES = 6
MIN_SCENARIOS = 2
MIN_PRACTICE = 3
MIN_WORDS = 4

# One entry per journey. `sources` are read in order; `refs` says whether a
# stage must name categories of the travel bank.
JOURNEYS = [
    {
        "id": "travel",
        "topic": "travel",
        "title_en": "Travel Journey",
        "title_fa": "سفر: از رزرو تا بازگشت",
        "icon": "🧳",
        "art": "case",
        "audiences": ["kids", "adults"],
        "blurb_en": ("From the first booking to the last check-out, in the "
                     "order the journey happens."),
        "blurb_fa": ("از نخستین رزرو تا آخرین تخلیه، به همان ترتیبی که سفر "
                     "پیش می‌رود."),
        "sources": ["tools/journeys_travel_a.txt", "tools/journeys_travel_b.txt"],
        "uses_refs": True,
        "needs_words": False,
    },
    {
        "id": "sports",
        "topic": "sports",
        "title_en": "Sports Journey",
        "title_fa": "ورزش: از زمین تا گفت‌وگو",
        "icon": "⚽",
        "art": "soccer",
        "audiences": ["kids", "adults"],
        "blurb_en": ("The words players, coaches and fans actually use, from "
                     "naming a sport to arguing about a final."),
        "blurb_fa": ("واژه‌هایی که بازیکن‌ها، مربی‌ها و هوادارها واقعاً به کار "
                     "می‌برند؛ از نام یک ورزش تا بحث دربارهٔ فینال."),
        "sources": ["tools/journeys_sports_a.txt", "tools/journeys_sports_b.txt",
                    "tools/journeys_sports_c.txt"],
        "profiles": "tools/sports_profiles.txt",
        "uses_refs": False,
        "needs_words": True,
    },
]


def die(msg):
    print("FAIL  " + msg)
    raise SystemExit(1)


def read_rows(path):
    if not path.exists():
        die(f"missing source {path.name}")
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        tag, _, rest = line.partition("|")
        yield f"{path.name}:{n}", tag.strip(), [p.strip() for p in rest.split("|")]


def parse(spec, known_words):
    """Read one journey's rows into stages, sports and their terms."""
    stages = []
    by_id = {}
    sports = []
    sport_by_id = {}
    current = None

    def rows():
        for name in spec["sources"]:
            yield from read_rows(ROOT / name)
        if spec.get("profiles"):
            yield from read_rows(ROOT / spec["profiles"])

    for where, tag, f in rows():
        if tag == "J":
            if len(f) != 9:
                die(f"{where}: a stage header needs 9 fields, got {len(f)}")
            ident, order, art, en, fa, aud, cats, blurb_en, blurb_fa = f
            if ident in by_id:
                die(f"{where}: stage {ident} is declared twice")
            refs = [c.strip() for c in cats.split(",") if c.strip()]
            current = {
                "id": ident, "order": int(order), "icon": art,
                "title_en": en, "title_fa": fa,
                "audiences": [a.strip() for a in aud.split(",") if a.strip()],
                "refs": refs,
                "blurb_en": blurb_en, "blurb_fa": blurb_fa,
                "objectives": [], "words": [], "sportRefs": [],
                "expressions": [], "patterns": [], "sentences": [],
                "dialogue": None, "scenarios": [], "practice": [],
            }
            if not current["audiences"]:
                die(f"{where}: stage {ident} has no audience")
            stages.append(current)
            by_id[ident] = current
            continue

        if tag == "R":
            if len(f) != 15:
                die(f"{where}: a sport profile needs 15 fields, got {len(f)}")
            (sid, en, ipa, fa, cat, def_en, art, venue, level,
             gear, acts, sen, sen_fa, talk, talk_fa) = f
            if sid in sport_by_id:
                die(f"{where}: sport {sid} is profiled twice")
            if level not in LEVELS:
                die(f"{where}: unknown level {level!r}")
            if not ipa or not ipa.strip("/"):
                die(f"{where}: {sid} needs an IPA reading")
            prof = {
                "id": sid, "en": en, "ipa": ipa, "fa": fa,
                "category": [c.strip() for c in cat.split(",") if c.strip()],
                "def_en": def_en, "icon": art, "venue": venue,
                "level": level,
                "equipment": [g.strip() for g in gear.split(",") if g.strip()],
                "actions": [a.strip() for a in acts.split(",") if a.strip()],
                "sentence_en": sen, "sentence_fa": sen_fa,
                "exchange_en": talk, "exchange_fa": talk_fa,
                "terms": [],
            }
            sports.append(prof)
            sport_by_id[sid] = prof
            continue

        if tag == "RT":
            if len(f) != 4:
                die(f"{where}: a sport term needs 4 fields")
            sid, term, fa, meaning = f
            if sid not in sport_by_id:
                die(f"{where}: term for unknown sport {sid!r}")
            sport_by_id[sid]["terms"].append(
                {"term": term, "fa": fa, "meaning_en": meaning})
            continue

        if current is None:
            die(f"{where}: row before any J header")

        # A row may repeat the stage id as its first field. Both forms are
        # allowed so a long source file stays readable, and the id is dropped
        # here so every tag has one field count to check against.
        # Word rows are exempt: their first field is the word itself, so a
        # stage called "teamwork" would otherwise eat its own W|teamwork row.
        if tag != "W" and f and f[0] == current["id"]:
            f = f[1:]

        if tag == "O":
            if len(f) != 2:
                die(f"{where}: an objective needs 2 fields")
            current["objectives"].append({"en": f[0], "fa": f[1]})
        elif tag == "W":
            if len(f) not in (11, 12):
                die(f"{where}: a word needs 11 or 12 fields, got {len(f)}")
            en, ipa, pos, fa, def_en, sport, art, level, ex, exfa = f[:10]
            ref = f[10] if len(f) == 11 else f[11]
            if level not in LEVELS:
                die(f"{where}: unknown level {level!r}")
            if not ipa:
                die(f"{where}: {en!r} has no IPA reading")
            if not en or not fa or not def_en or not ex:
                die(f"{where}: {en!r} is missing a definition, a Persian or an example")
            current["words"].append({
                "id": f"{current['id']}-w{len(current['words']) + 1}",
                "en": en, "ipa": ipa, "pos": pos, "fa": fa,
                "def_en": def_en, "sport": sport, "icon": art,
                "level": level, "example_en": ex, "example_fa": exfa,
                "ref": ref,
            })
            if ref:
                known_words.add(ref)
        elif tag == "G":
            if len(f) != 1:
                die(f"{where}: a sports row needs one comma list")
            ids = [s.strip() for s in f[0].split(",") if s.strip()]
            for s in ids:
                if s in current["sportRefs"]:
                    die(f"{where}: stage {current['id']} lists {s} twice")
            current["sportRefs"].extend(ids)
        elif tag == "X":
            # An alternative is useful but not always true: some phrases have
            # no natural second form, and inventing one teaches a phrase nobody
            # says. Eight fields means "no alternative".
            if len(f) not in (8, 9):
                die(f"{where}: an expression needs 8 or 9 fields, got {len(f)}")
            kind, en, fa, men, mfa, reg, ex, exfa = f[:8]
            alt = f[8] if len(f) == 9 else ""
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
        die(f"{spec['id']}: no stages were read")

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
        if spec["needs_words"] and len(st["words"]) < MIN_WORDS:
            die(f"{sid}: fewer than {MIN_WORDS} words")
        d = st["dialogue"]
        if not d:
            die(f"{sid}: no dialogue")
        if len(d["lines"]) < MIN_DIALOGUE_LINES:
            die(f"{sid}: dialogue is shorter than {MIN_DIALOGUE_LINES} lines")
        if len({l['who'] for l in d['lines']}) < 2:
            die(f"{sid}: dialogue has one speaker")
        if spec["uses_refs"] and not st["refs"]:
            die(f"{sid}: names no travel categories to teach from")

    stages.sort(key=lambda s: s["order"])
    orders = [s["order"] for s in stages]
    if orders != list(range(1, len(stages) + 1)):
        die(f"stage order is not 1..{len(stages)}: {orders}")

    # A stage may only show sports that were actually profiled, and a sport
    # profile must reach a stage or nobody can open it.
    profiled = {p["id"] for p in sports}
    for st in stages:
        for s in st["sportRefs"]:
            if s not in profiled:
                die(f"{st['id']}: names unprofiled sport {s!r}")
    shown = {s for st in stages for s in st["sportRefs"]}
    orphan = profiled - shown
    if orphan:
        die(f"sports nobody teaches: {sorted(orphan)}")

    return stages, sports


def main() -> int:
    travel = json.loads(TRAVEL.read_text(encoding="utf-8"))
    categories = {c["id"]: c for c in travel["categories"]}
    senses = json.loads(SENSES.read_text(encoding="utf-8")).get("words", {})

    built = []
    known_words = set()
    for spec in JOURNEYS:
        stages, sports = parse(spec, known_words)
        if spec["uses_refs"]:
            for st in stages:
                for r in st["refs"]:
                    if r not in categories:
                        die(f"{st['id']}: names unknown travel category {r!r}")
        levels = sorted({s["level"] for st in stages for s in st["sentences"]}
                        | {w["level"] for st in stages for w in st["words"]})
        reached = sorted({c for st in stages for c in st["refs"]})
        vocab_refs = sum(len(categories[c]["vocab"]) for c in reached)
        sentence_refs = sum(len(categories[c]["sentences"]) for c in reached)
        journey = {
            "id": spec["id"],
            "topic": spec["topic"],
            "title_en": spec["title_en"],
            "title_fa": spec["title_fa"],
            "icon": spec["icon"],
            "art": spec["art"],
            "audiences": spec["audiences"],
            "blurb_en": spec["blurb_en"],
            "blurb_fa": spec["blurb_fa"],
            "levels": levels,
            "stages": stages,
            "stats": {
                "stages": len(stages),
                "words": sum(len(s["words"]) for s in stages),
                "expressions": sum(len(s["expressions"]) for s in stages),
                "patterns": sum(len(s["patterns"]) for s in stages),
                "sentences": sum(len(s["sentences"]) for s in stages),
                "dialogues": len(stages),
                "scenarios": sum(len(s["scenarios"]) for s in stages),
                "practice": sum(len(s["practice"]) for s in stages),
                "bank_sentences": sentence_refs,
                "bank_words": vocab_refs,
            },
        }
        if sports:
            journey["sports"] = sports
            journey["stats"]["sports"] = len(sports)
            journey["stats"]["sport_terms"] = sum(len(p["terms"]) for p in sports)
        built.append(journey)

    # Every word that claims a dictionary key must really be in the dictionary,
    # or the link is a lie the learner finds by tapping it.
    for journey in built:
        for st in journey["stages"]:
            for w in st["words"]:
                if w["ref"] and w["ref"] not in senses:
                    die(f"{st['id']}: {w['en']!r} claims senses.json key {w['ref']!r}")

    out = {
        "_meta": {
            "version": 2,
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
            "note_en": ("These are language lessons, not legal, immigration, "
                        "medical or coaching advice. Rules differ by country and "
                        "by competition: check the official rulebook."),
            "note_fa": ("این‌ها درس زبان‌اند، نه مشاورهٔ حقوقی، مهاجرتی، پزشکی یا "
                        "مربی‌گری. قاعده‌ها در هر کشور و هر مسابقه فرق دارد؛ "
                        "قانون رسمی را ببین."),
            "sources": ("Original material written for Fluentify in American "
                        "English. Travel vocabulary, sentences and dialogue "
                        "bank: travel.json, joined by id rather than copied. "
                        "Sports words are original and carry their own IPA; "
                        "where senses.json already holds a word, the entry names "
                        "it in `ref` instead of defining it twice."),
            "levels": LEVELS,
            "stats": {
                "journeys": len(built),
                "stages": sum(j["stats"]["stages"] for j in built),
                "words": sum(j["stats"]["words"] for j in built),
                "expressions": sum(j["stats"]["expressions"] for j in built),
                "sports": sum(len(j.get("sports", [])) for j in built),
            },
        },
        "journeys": built,
    }

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    for j in built:
        s = j["stats"]
        extra = f", {s['sports']} sports with {s['sport_terms']} key terms" if "sports" in s else ""
        print(f"PASS  {j['id']} journey: {s['stages']} stages, {s['words']} own words, "
              f"{s['expressions']} expressions and idioms, {s['patterns']} patterns, "
              f"{s['sentences']} sentences, {s['dialogues']} dialogues, "
              f"{s['scenarios']} scenarios, {s['practice']} practice items{extra}; "
              f"joins {s['bank_sentences']} bank sentences and {s['bank_words']} bank words")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
