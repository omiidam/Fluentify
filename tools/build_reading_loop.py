#!/usr/bin/env python3
"""Builds reading_loop.json: what a passage needs *around* it.

The Reading section already ships ten strategies and thirty passages with
questions. What it never had is the loop the evidence asks for: something
before the text (a purpose, a schema question, three essential words), support
*inside* the text (Persian for the words that carry the meaning), a second,
unsupported read, an inference check, and a word bank that feeds the next text.

None of that is invented here. The Persian glosses come from glossary.json and
senses.json - the same meanings the vocabulary panels print - the essential
words are the passage's own most-repeated content words, the inference
questions are the passage's existing questions that ask *why* or *what it
suggests* rather than what was literally said, and the output task is the
writing task the passage already poses. The builder only decides *which* of
those to surface, so a word can never be glossed with a meaning the app does
not already teach.

Run: python3 tools/build_reading_loop.py
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READING = ROOT / "reading.json"
GLOSSARY = ROOT / "glossary.json"
SENSES = ROOT / "senses.json"
VOCAB = ROOT / "vocab_examples.json"
OUT = ROOT / "reading_loop.json"

WORD = re.compile(r"[A-Za-z][A-Za-z'’-]*")
FA = re.compile(r"[\u0600-\u06FF]")

# Between them: function words, pronouns, auxiliaries, and the words a reading
# question is built from. A word on this list is never "essential vocabulary".
STOP = set("""
a an the and or but if so because as than then that this these those there
here it its it's they them their theirs we us our you your he him his she her
hers i me my mine one two three first second third next last also not no yes
is are was were be been being am do does did done have has had having will
would can could shall should may might must of in on at to from by with
without for about into over under after before between through during out up
down off again more most less least very too just only own same other another
such all any both each few many some most none what which who whom whose when
where why how while until since though although however therefore thus
per cent percent year years day days time times new old good bad big small
like want wanted need needed get got make made go went going come came see
saw seen say said tell told know knew known think thought use used using
people person thing things way ways part parts place places work works
""".split())

# What the reader is trying to *do* with each strategy. One line each, because
# a purpose has to be concrete: "read this" is not a purpose, "find out how
# the club decides who gets a plot" is.
PURPOSE = {
    "survey": ("Find the shape before the words: how many parts, what kind of "
               "text, and who it was written for.",
               "اول شکل متن را پیدا کن: چند بخش دارد، چه نوع متنی است و برای "
               "چه کسی نوشته شده."),
    "predict": ("Guess what comes next from the title and the first lines, "
                "then read to see if you were right.",
                "از عنوان و سطرهای اول حدس بزن بعدش چه می‌آید، بعد بخوان تا "
                "ببینی درست حدس زده‌ای."),
    "skim": ("In one minute, find out what the text is about without reading "
             "every word.",
             "در یک دقیقه بفهم متن دربارهٔ چیست، بی‌آنکه هر کلمه را بخوانی."),
    "scan": ("Look for one kind of information only - a name, a number, a "
             "price - and ignore the rest.",
             "فقط یک نوع اطلاعات را پیدا کن - یک اسم، یک عدد، یک قیمت - و "
             "بقیه را نادیده بگیر."),
    "context": ("Work out three unknown words from their sentence before you "
                "look anything up.",
                "پیش از نگاه کردن به هر جایی، معنای سه واژهٔ ناشناس را از "
                "جمله‌شان حدس بزن."),
    "mainidea": ("Decide what the text is mostly about, in one sentence you "
                 "could say out loud.",
                 "تصمیم بگیر متن بیشتر دربارهٔ چیست، در یک جمله که بتوانی "
                 "بلند بگویی."),
    "signposts": ("Follow the words that show the way - however, because, for "
                  "example, in the end - and see how the text moves.",
                  "واژه‌هایی را دنبال کن که مسیر را نشان می‌دهند - however، "
                  "because، for example، in the end - و ببین متن چطور پیش "
                  "می‌رود."),
    "summarize": ("Keep the three ideas you would tell someone, and drop the "
                  "rest.",
                  "سه ایده‌ای را نگه دار که به کسی می‌گویی و بقیه را رها کن."),
    "detail": ("Collect the details that support the main idea, and notice "
               "which details are decoration.",
               "جزئیاتی را جمع کن که ایدهٔ اصلی را پشتیبانی می‌کنند و ببین کدام "
               "جزئیات فقط تزیین‌اند."),
    "inference": ("Read what is not written: what the writer implies, and how "
                  "you know.",
                  "آنچه نوشته نشده را بخوان: نویسنده چه را در لفافه می‌گوید و "
                  "از کجا می‌دانی."),
    "reference": ("Follow the words that point back - it, this, they, the "
                  "former - to what they name.",
                  "واژه‌هایی را دنبال کن که به عقب اشاره می‌کنند - it، this، "
                  "they، the former - تا بفهمی به چه چیزی برمی‌گردند."),
    "text-structure": ("See how the parts are joined: cause and effect, "
                       "problem and solution, or a list.",
                       "ببین بخش‌ها چطور به هم وصل شده‌اند: علت و معلول، مشکل و "
                       "راه‌حل، یا یک فهرست."),
}

# Questions that ask for reasoning rather than recall. The wording decides: a
# question that begins with "What" and repeats a sentence is recall; one that
# asks why, what it suggests, or what the writer is doing is inference.
DEEP = re.compile(
    r"\b(why|because|suggest|implies?|infer|infer|purpose|attitude|tone|"
    r"most likely|probably|what does .* (?:mean|show|tell us)|"
    r"what can you (?:tell|learn|conclude)|main idea|best title|"
    r"writer|author|paragraph \d+ (?:do|show|serve))\b", re.I)


def load(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def gloss_table() -> dict[str, str]:
    """word -> one Persian meaning, from the two sources the app teaches from.

    The glossary is the taught vocabulary and wins; senses.json fills the rest.
    A word with two glossary meanings keeps the first, because a reading gloss
    is a reading aid, not a dictionary entry.
    """
    table: dict[str, str] = {}
    for dom in load(GLOSSARY)["domains"].values():
        if not isinstance(dom, dict):
            continue
        for pair in dom.get("words") or []:
            if not pair or len(pair) < 2:
                continue
            word = str(pair[0]).strip().lower()
            fa = str(pair[1]).strip()
            if word and fa and FA.search(fa):
                table.setdefault(word, fa)
    for word, record in load(SENSES)["words"].items():
        senses = record.get("senses") or []
        if not senses:
            continue
        fa = str((senses[record.get("primary") or 0] if len(senses) > (record.get("primary") or 0) else senses[0])[2] or "").strip()
        if fa and FA.search(fa) and len(fa) <= 40:
            table.setdefault(str(word).strip().lower(), fa)
    return table


TIME_WORDS = set("""
january february march april may june july august september october november
 december monday tuesday wednesday thursday friday saturday sunday
christmas easter summer winter spring autumn
""".split())


def entities(text: str) -> list[str]:
    """The names in a text, joined the way they are written.

    "Community Garden" is one name, not two places called Community and
    Garden, and a name is a run of capitalised words rather than each of them
    separately. Weekdays and months are ordinary time words, not entities a
    reader would be lost without.
    """
    found: Counter = Counter()
    keep_out = TIME_WORDS | STOP | {
        "the", "it", "this", "that", "there", "they", "he", "she", "we",
        "at", "not", "today", "tomorrow", "yesterday", "membership",
        "opening", "forty", "thirty", "fifty", "hundred", "thousand",
        "however", "also", "both", "each", "every", "some", "many",
    }
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        run: list[str] = []
        run_at = 0
        words = sentence.split()
        for index, raw in enumerate(words + [""]):
            clean = raw.strip(".,;:!?\"'()")
            capital = len(clean) > 1 and clean[0].isupper() and clean.isalpha()
            if capital:
                if not run:
                    run_at = index
                run.append(clean)
                # "Paris, Berlin" is two cities, not one place called Paris
                # Berlin: a comma ends the name.
                if raw.endswith((",", ";", ":")):
                    found[" ".join(run)] += 1
                    run = []
                continue
            if run:
                # A sentence may start with any capital: a lone one there is
                # grammar, not a name. Two or more joined words always are.
                lone_sentence_start = len(run) == 1 and run_at == 0
                name = " ".join(run)
                def ordinary(word: str) -> bool:
                    low = word.lower()
                    return low in keep_out or low.rstrip("s") in keep_out

                if (not lone_sentence_start
                        and not ordinary(name)
                        and all(not ordinary(w) for w in run)):
                    found[name] += 1
                run = []
    return [w for w, n in found.most_common(6)]


def passage_entry(sid: str, r: dict, table: dict[str, str]) -> dict:
    text = " ".join(r.get("paragraphs") or [])
    tokens = [w.lower() for w in WORD.findall(text)]
    counts = Counter(tokens)
    names = {e.lower() for e in entities(text)}

    # The gloss map is the reader's help: the words that carry meaning, most
    # repeated first, and never a name (a name is a name, not a translation).
    glossable = [(w, n) for w, n in counts.items()
                 if w in table and len(w) >= 3 and w not in STOP
                 and w not in names]
    glossable.sort(key=lambda pair: (-pair[1], -len(pair[0]), pair[0]))
    gloss = {w: table[w] for w, _n in glossable[:60]}

    # Three words to meet before reading. Frequency alone picks scenery; the
    # words a learner actually stumbles over are the ones the passage keeps
    # using *and* the questions keep asking about, so those rank first.
    q = r["questions"]
    asked = " ".join([item.get("q", "") for item in q["mcq"]]
                     + [item.get("statement", "") for item in q.get("truefalse") or []])
    asked_words = set(WORD.findall(asked.lower()))
    scored = [(w, n + (2 if w in asked_words else 0))
              for w, n in glossable if len(w) >= 4]
    scored.sort(key=lambda pair: (-pair[1], pair[0]))
    key = [w for w, _score in scored[:3]]

    deep_mcq = [i for i, item in enumerate(q["mcq"])
                if DEEP.search(item.get("q", ""))]
    deep_tf = [i for i, item in enumerate(q.get("truefalse") or [])
               if DEEP.search(item.get("statement", ""))]
    essay = (q.get("essay") or [{}])[0]
    prompt = essay.get("prompt") or {}
    return {
        "purpose": {"en": PURPOSE.get(sid, ("Read it for its point.", "برای نکته‌اش بخوان."))[0],
                    "fa": PURPOSE.get(sid, ("Read it for its point.", "برای نکته‌اش بخوان."))[1]},
        "background": {
            "en": "Before you read: what do you already know about “%s”? One line is enough." % r["title"]["en"],
            "fa": "پیش از خواندن: دربارهٔ «%s» چه می‌دانی؟ یک خط کافی است." % r["title"]["fa"],
        },
        "entities": entities(text),
        "gloss": gloss,
        "key": key,
        "deep": {"mcq": deep_mcq or list(range(len(q["mcq"]))), "truefalse": deep_tf},
        "output": {
            "en": (prompt.get("en") or "").strip(),
            "fa": (prompt.get("fa") or "").strip(),
            "min_words": 20,
        },
        "reuses": [w for w in key if len(w) > 4],
    }


def calibration(doc: dict) -> list[dict]:
    """Three questions, one per level, for the cold-start check.

    One item from each band's easiest passage: an A2, a B1 and a B2 question,
    each already authored and already answered in the file. The walk is
    adaptive - start at B1, go up on a right answer, down on a wrong one - so
    two questions place most readers.
    """
    out = []
    for level in ("A2", "B1", "B2"):
        for s in doc["strategies"]:
            for r in s["readings"]:
                if r.get("level") != level:
                    continue
                for item in r["questions"]["mcq"]:
                    if item.get("para") and item.get("why"):
                        out.append({
                            "level": level,
                            "title": r["title"]["en"],
                            "q": item["q"],
                            "options": item["options"],
                            "answer": item["answer"],
                            "why": item["why"],
                        })
                        break
                break
            else:
                continue
            break
    return out


def main() -> None:
    doc = load(READING)
    table = gloss_table()
    passages = {}
    for s in doc["strategies"]:
        for i, r in enumerate(s["readings"], start=1):
            # The page keys a passage the way it always has: passage one is the
            # bare strategy id (so every answer given before this file existed
            # is still attached to it), the rest are "id#n".
            key = s["id"] if i == 1 else "%s#%d" % (s["id"], i)
            passages[key] = passage_entry(s["id"], r, table)

    payload = {
        "version": 1,
        "_built_by": "tools/build_reading_loop.py",
        "_readme": ("Per-passage support for the reading loop: the purpose, a "
                    "background question, three essential words, a Persian "
                    "gloss map drawn from the app's own vocabulary, the "
                    "questions that ask for inference, and the output task."),
        "calibration": calibration(doc),
        "passages": passages,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    keys = sum(len(p["gloss"]) for p in passages.values())
    print("%s: %d passages, %d glossed words, %d key words, %d calibration "
          "questions" % (OUT.name, len(passages), keys,
                         sum(len(p["key"]) for p in passages.values()),
                         len(payload["calibration"])))


if __name__ == "__main__":
    main()
