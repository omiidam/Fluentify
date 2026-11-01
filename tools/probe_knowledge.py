#!/usr/bin/env python3
"""What does the tutor know about words, and which of it can you not reach?

The app has one page of panels and one conversation. The panels show the
course books, the day's set, the sentence bank, the vocabulary domains, the
grammar topics, the pronunciation rail, the listening library and the saved
words. Everything else the tutor knows - the dictionary shards, the slang and
idiom bank, the word distinctions, the register pairs, the correction rules,
the jokes - is reachable only by asking, and nothing anywhere lists it.

So this walks every knowledge file, works out which surface can reach it, and
measures what each one holds:

  * rows, and how many carry a Persian side;
  * strings that put Persian and English on the *same* line, which is the
    shape that reads badly in both scripts and is the thing the layout rules
    exist to prevent;
  * the same question asked of the engine: real answers to real prompts,
    scanned line by line, because a formatter can join two readers inside one
    f-string and no amount of clean JSON will show it.

    python3 tools/probe_knowledge.py               # the report
    python3 tools/probe_knowledge.py --json        # the same, machine-readable
    python3 tools/probe_knowledge.py --strict      # exit 1 on a mixed line
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "tools/.cache"

ARABIC = re.compile(r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]")
LATIN = re.compile(r"[A-Za-z]")

# Which surface can reach each file. "panel" means a button in the top bar
# loads it through an /api/ endpoint (the endpoint is named); "chat" means the
# only way in is to ask. The endpoint names are checked against webapp.py at
# run time, so a surface that loses its endpoint shows up instead of quietly
# staying "panel".
SURFACES = {
    "glossary.json":       ("panel+chat", "/api/vocabulary", "Vocabulary panel, and word lookup in chat"),
    "phrases.json":        ("panel+chat", "/api/phrases", "Say panel, and phrase lookup in chat"),
    "grammar.json":        ("panel+chat", "/api/grammar", "Grammar panel and lessons in chat"),
    "phonetics.json":      ("panel+chat", "/api/phonetics", "Sounds panel"),
    "daily.json":          ("panel+chat", "/api/daily", "Today's English"),
    "books.json":          ("panel+chat", "/api/books", "Books panel"),
    "bbc_6min.json":       ("panel", "/api/bbc", "Listen panel"),
    "listening.json":      ("panel+chat", "/api/listening", "Listen panel levels"),
    "word_arch.json":      ("panel+chat", "/api/wordarch", "Vocabulary detail"),
    "slang.json":          ("chat", None, "slang words, English idioms, Persian idioms"),
    "idioms.json":         ("chat", None, "idiom topics"),
    "distinctions.json":   ("chat", None, "look-alike word pairs"),
    "register.json":       ("chat", None, "the same idea at three formalities"),
    "corrections.json":    ("chat", None, "the mistake rules behind a correction"),
    "jokes.json":          ("chat", None, "jokes with a translation"),
    "memory.json":         ("panel+chat", None, "Review panel and the intents"),
}

# The dictionary is a directory of shards, not one file.
DICTIONARY_DIR = "lexicon"

PROMPTS = [
    # the glossary path, which has its own one-line formatter
    "bank", "spring", "light", "معنی bank", "رنگ‌ها",
    # the dictionary shards
    "define voracious", "what does ubiquitous mean", "معنی ubiquitous",
    "bank meaning in a sentence: I deposited money in the bank",
    # slang and idioms
    "what does bruh mean", "slang for money", "break the ice",
    "معنی break a leg", "ضرب‌المثل",
    # distinctions and register
    "difference between affect and effect", "lay or lie",
    "formal way to say sorry", "register of get",
    # corrections
    "correct: he go to school yesterday",
    # jokes
    "tell me a joke", "یک جوک بگو",
    # phrases, books, daily, listening for contrast
    "how do I order coffee", "today's word", "listen A2",
]


def strings_in(node, path=""):
    """Every string in a JSON document, with the path that led to it."""
    if isinstance(node, dict):
        for k, v in node.items():
            yield from strings_in(v, f"{path}.{k}" if path else str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from strings_in(v, f"{path}[{i}]")
    elif isinstance(node, str):
        yield path, node


def rows_in(node) -> int:
    """How many records a document holds, whatever its shape."""
    if isinstance(node, list):
        return len(node)
    if isinstance(node, dict):
        total = 0
        for v in node.values():
            if isinstance(v, list):
                total += len(v)
            elif isinstance(v, dict):
                total += rows_in(v)
            elif isinstance(v, str):
                total += 1
        return total
    return 1


def scan_file(path: Path) -> dict:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return {"file": path.name, "error": str(exc)[:120]}
    rows = persian = mixed = 0
    samples = []
    for where, text in strings_in(doc):
        rows += 1
        has_fa, has_en = bool(ARABIC.search(text)), bool(LATIN.search(text))
        persian += has_fa
        # A line that carries both scripts is not a mistake in itself - the
        # catalogue note is bilingual on purpose - but it is the shape that
        # needs an isolation rule, so it is counted and shown.
        if has_fa and has_en and " " in text:
            mixed += 1
            if len(samples) < 4:
                samples.append(text[:90])
    return {"file": path.name, "rows": rows, "persian": persian,
            "mixed": mixed, "samples": samples}


def dictionary_stats() -> dict:
    d = ROOT / DICTIONARY_DIR
    if not d.is_dir():
        return {}
    shards = sorted(d.glob("*.json"))
    heads = senses = with_fa = 0
    for shard in shards:
        try:
            doc = json.loads(shard.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        entries = doc.get("w") or doc.get("words") or doc
        if not isinstance(entries, dict):
            continue
        heads += len(entries)
        for head, entry in entries.items():
            senses_list = entry.get("s") if isinstance(entry, dict) else None
            if not isinstance(senses_list, list):
                continue
            senses += len(senses_list)
            for sense in senses_list:
                if isinstance(sense, list) and len(sense) > 2 and sense[2]:
                    with_fa += 1
    return {"file": "lexicon/", "shards": len(shards), "rows": heads,
            "senses": senses, "persian": with_fa,
            "mixed": 0, "samples": []}


def endpoint_exists(webapp: str, endpoint: str) -> bool:
    return endpoint is None or f'"{endpoint}"' in webapp


# Bracketed and quoted spans are set aside before a line is judged. A source
# note in brackets - "AFK - دور از کیبورد (away from keyboard)" - and a quoted
# sample - Ask: 'what does bruh mean' - are meant to sit where they sit; it is
# the line's own words that have to keep one direction.
ASIDE = re.compile(r"\([^()]*\)|\[[^\[\]]*\]|«[^»]*»")
RUN = re.compile(r"[A-Za-z\u0600-\u06FF\u0750-\u077F]+")


def interleaved(line: str) -> bool:
    """Two scripts that alternate three or more times, which reads as scrambled.

    A bilingual line is not the problem. "Word of the Day — لغت امروز" is a
    heading in the order both readers scan it; "🔤 صورت‌های go" puts the
    Persian label where the Persian eye starts and keeps the headword Latin.
    Those are two runs, and two runs have one boundary to cross.

    A line that goes English, Persian, English again - or Persian, English,
    Persian - makes the reader jump back over their own eye, and that is what
    "\"bank\" → بانک (place / مکانی) — also: bank (بانک)" did.
    """
    body = ASIDE.sub(" ", line)
    runs = ["fa" if ARABIC.match(tok) else "en" for tok in RUN.findall(body)]
    flips = sum(1 for a, b in zip(runs, runs[1:]) if a != b)
    return flips >= 2


def audit_answers() -> list[dict]:
    """Ask the engine, then look at the lines it writes back."""
    sys.path.insert(0, str(ROOT))
    try:
        import chatbot
    except Exception as exc:                    # pragma: no cover - env problem
        return [{"error": f"could not import the engine: {exc}"}]
    bot = chatbot.ChatBot()
    out = []
    for prompt in PROMPTS:
        try:
            answer = bot.respond(prompt)
        except Exception as exc:                # pragma: no cover - engine bug
            out.append({"prompt": prompt, "error": f"{type(exc).__name__}: {exc}"})
            continue
        bad = []
        for line in str(answer).split("\n"):
            if line.strip() and interleaved(line):
                bad.append(line.strip()[:110])
        out.append({"prompt": prompt,
                    "lines": len(str(answer).split("\n")),
                    "mixed": bad})
    return out


def main(argv: list[str]) -> int:
    webapp = (ROOT / "webapp.py").read_text(encoding="utf-8")
    files = [p for p in ROOT.glob("*.json") if p.name in SURFACES]
    stop = ROOT / "stt.json"
    report = {"files": [], "chat_only": [], "answers": [], "problems": []}

    for path in sorted(files):
        stats = scan_file(path)
        surface, endpoint, what = SURFACES[path.name]
        stats["surface"] = surface
        stats["endpoint"] = endpoint
        stats["what"] = what
        if not endpoint_exists(webapp, endpoint):
            report["problems"].append(
                f"{path.name}: the {endpoint} endpoint the panel uses is gone")
        if surface == "chat":
            report["chat_only"].append(stats)
        report["files"].append(stats)

    lex = dictionary_stats()
    if lex:
        lex.update({"surface": "chat", "endpoint": None,
                    "what": "the dictionary shards behind word lookup"})
        report["files"].append(lex)
        report["chat_only"].append(lex)
    if not stop.exists():
        report["problems"].append("stt.json is missing")

    report["answers"] = audit_answers()

    if "--strict" in argv:
        for row in report["answers"]:
            for line in row.get("mixed") or []:
                report["problems"].append(f"one line, two scripts: {line}")

    if "--json" in argv:
        print(json.dumps(report, ensure_ascii=False, indent=1))
        return 1 if report["problems"] and "--strict" in argv else 0

    print("KNOWLEDGE THE PANELS CAN SHOW")
    print(f"  {'file':18} {'rows':>7} {'Persian':>8} {'mixed':>6}  surface")
    for f in report["files"]:
        if f.get("surface") == "chat":
            continue
        print(f"  {f['file']:18} {f['rows']:>7} {f['persian']:>8} {f['mixed']:>6}  "
              f"{f.get('surface')} {f.get('endpoint') or ''}")

    print("\nONLY THE CONVERSATION CAN REACH THESE")
    for f in report["chat_only"]:
        print(f"  {f['file']:18} {f['rows']:>7} {f['persian']:>8} {f['mixed']:>6}  "
              f"{f.get('what','')}")
        for s in f.get("samples") or []:
            print(f"      e.g. {s}")

    print("\nANSWERS THAT PUT BOTH SCRIPTS ON ONE LINE")
    bad_total = 0
    for row in report["answers"]:
        if row.get("error"):
            print(f"  ! {row['prompt']}: {row['error']}")
            continue
        if not row["mixed"]:
            continue
        bad_total += len(row["mixed"])
        print(f"  {row['prompt']!r} ({len(row['mixed'])} line(s))")
        for line in row["mixed"]:
            print(f"      {line}")
    if not bad_total:
        print("  none - every answer keeps one language per line")

    if report["problems"] and "--strict" not in argv:
        print("\nNOTES")
        for p in report["problems"]:
            print(f"  - {p}")

    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / "knowledge_probe.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 1 if report["problems"] and "--strict" in argv else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
