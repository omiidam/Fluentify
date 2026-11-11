#!/usr/bin/env python3
"""Build travel.json from tools/travel_content.txt.

    python3 tools/build_travel.py

The content file is one item per line with pipe-separated fields:

    C|id|emoji|title_en|title_fa|level|desc_en|desc_fa        a category
    S|cat|en|fa|use_en|use_fa|level|politeness|alt_en|alt_fa  a sentence
    V|cat|en|fa|def_en|pos|example_en                          a word
    D|cat|title_en|title_fa|who|en|fa                          a dialogue line
    P|cat|frame|example_en|note_en|note_fa                     a pattern

Flat files cannot be mis-bracketed, and a bad row stops the build with its line
number instead of shipping a half-empty category.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "travel_content.txt"
OUT = ROOT / "travel.json"
POLITE = {"n": ("neutral", "خنثی"), "p": ("polite", "مؤدبانه"), "i": ("informal", "خودی")}
LEVELS = {"A1", "A2", "B1", "B2", "C1", "C2"}


def rows():
    for n, line in enumerate(SRC.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|")
        if parts[0] not in {"C", "S", "V", "D", "P"}:
            raise SystemExit(f"{SRC.name}:{n}: unknown row {parts[0]!r}")
        yield n, parts


def build():
    cats = {}
    order = []
    dialogue = {}          # cat -> {"title_en", "title_fa", "lines": []}
    for n, p in rows():
        kind = p[0]
        if kind == "C":
            _, cid, emoji, en, fa, level, desc_en, desc_fa = p
            if cid in cats:
                raise SystemExit(f"{SRC.name}:{n}: duplicate category {cid}")
            if level not in LEVELS:
                raise SystemExit(f"{SRC.name}:{n}: bad level {level}")
            order.append(cid)
            cats[cid] = {"id": cid, "emoji": emoji, "title_en": en, "title_fa": fa,
                         "desc_en": desc_en, "desc_fa": desc_fa, "level": level,
                         "sentences": [], "vocab": [], "dialogue": None,
                         "pattern": None}
        elif kind == "S":
            _, cid, en, fa, use_en, use_fa, level, pol, alt_en, alt_fa = p
            if level not in LEVELS or pol not in POLITE:
                raise SystemExit(f"{SRC.name}:{n}: bad level or politeness")
            s = cats[cid]["sentences"]
            s.append({"id": f"{cid}-{len(s) + 1}", "en": en, "fa": fa,
                      "use_en": use_en, "use_fa": use_fa, "level": level,
                      "polite": pol, "polite_en": POLITE[pol][0],
                      "polite_fa": POLITE[pol][1],
                      "alt": [{"en": alt_en, "fa": alt_fa}] if alt_en else []})
        elif kind == "V":
            _, cid, en, fa, definition, pos, example = p
            cats[cid]["vocab"].append({"en": en, "fa": fa, "def_en": definition,
                                       "pos": pos, "example_en": example})
        elif kind == "D":
            _, cid, title_en, title_fa, who, en, fa = p
            d = dialogue.get(cid)
            if d is None:
                d = dialogue[cid] = {"title_en": title_en, "title_fa": title_fa,
                                     "lines": []}
            d["lines"].append({"who": who, "en": en, "fa": fa})
        elif kind == "P":
            _, cid, frame, example, note_en, note_fa = p
            cats[cid]["pattern"] = {"frame": frame, "example_en": example,
                                    "note_en": note_en, "note_fa": note_fa}

    for cid in order:
        cats[cid]["dialogue"] = dialogue.get(cid)
        c = cats[cid]
        if len(c["sentences"]) < 4:
            raise SystemExit(f"{cid}: only {len(c['sentences'])} sentences")
        if len(c["vocab"]) < 4:
            raise SystemExit(f"{cid}: only {len(c['vocab'])} words")
        if not c["dialogue"] or len(c["dialogue"]["lines"]) < 4:
            raise SystemExit(f"{cid}: dialogue missing or too short")

    order_levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
    levels_in_use = sorted({s["level"] for c in order for s in cats[c]["sentences"]},
                           key=order_levels.index)

    doc = {
        "_meta": {
            "version": 1, "title_en": "Travel English", "title_fa": "انگلیسی سفر",
            "intro_en": "The English you need from the first booking to the last "
                        "check-out: sentences, vocabulary, and the dialogues they "
                        "live in. Everything here works offline.",
            "intro_fa": "انگلیسی‌ای که از نخستین رزرو تا آخرین تخلیه لازم داری: "
                        "جمله‌ها، واژه‌ها و گفت‌وگوهایی که در آن‌ها به کار می‌روند. "
                        "همه‌چیز آفلاین کار می‌کند.",
            "levels": levels_in_use,
            "note_en": "This is language for travel, not legal, immigration or "
                       "medical advice. Rules differ by country: ask the official "
                       "in front of you.",
            "note_fa": "این‌ها زبان سفر است، نه مشاورهٔ حقوقی، مهاجرتی یا پزشکی. "
                       "قواعد هر کشور فرق دارد؛ از مأمور رسمی بپرس.",
            "sources": "Original sentences written for Fluentify, in American "
                       "English, with British wording noted where it differs.",
        },
        "categories": [cats[cid] for cid in order],
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    ns = sum(len(c["sentences"]) for c in doc["categories"])
    nv = sum(len(c["vocab"]) for c in doc["categories"])
    print(f"wrote {OUT.name}: {len(doc['categories'])} categories, {ns} sentences, "
          f"{nv} words, {len(doc['categories'])} dialogues")


if __name__ == "__main__":
    build()
