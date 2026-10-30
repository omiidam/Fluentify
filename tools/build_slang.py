#!/usr/bin/env python3
"""Builds slang.json - the bilingual slang and idiom bank the chat reads.

Four sources feed it, and each one contributes the piece the others lack:

  SlangLane        modern internet and street slang, daily-checked, CC-BY-4.0.
                   Gives the term, its category, its register and a plain
                   English gloss. No Persian, no examples.
  IdiomX           idioms with Wiktionary-sourced meanings and real example
                   sentences (kaikki/Wiktionary, CC-BY-SA-4.0 inside an MIT
                   repo). English only: its other language is Arabic.
  Idiom_Translation  Persian and English idioms in parallel, with the sentence
                   each one was used in and its human translation. This is the
                   only source that carries Persian idiom language, so it is
                   what makes the bank bilingual in both directions.
  DadmaTools       not data but the Persian normalisation rules the matcher
                   uses (Arabic yeh and kaf to their Persian forms), so an
                   idiom typed the way people actually type it still matches.

Persian glosses for the slang terms come from tools/slang_fa.json, written for
this app: none of the four sources translate slang into Persian, and a
half-English reply is not what a bilingual tutor should give.

The downloads are cached under tools/.cache/slang, so a rebuild is offline once
they are here. slang.json is committed: the app needs the content, not the
network.

    python3 tools/build_slang.py
    python3 tools/build_slang.py --refresh     # re-download the sources
"""

from __future__ import annotations

import csv
import io
import json
import sys
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "tools/.cache/slang"
OUT = ROOT / "slang.json"
AUTHORED = ROOT / "tools/slang_fa.json"
CURATED = ROOT / "idioms.json"

SLANGLANE = "https://slanglane.com/api/dataset.jsonl"
SARA_EN_FA = ("https://raw.githubusercontent.com/Sara-Rezaeimanesh/"
              "Idiom_Translation/main/Parallel%20Data/En_Fa.csv")
SARA_FA_EN = ("https://raw.githubusercontent.com/Sara-Rezaeimanesh/"
              "Idiom_Translation/main/Parallel%20Data/Fa_En.csv")
IDIOMX = ("https://huggingface.co/datasets/aymansharara/IdiomX/resolve/main/"
          "idiomx_full.parquet")

# The bank is a language tutor's, not an archive: slang the source itself flags
# as mature stays out, and so does a short list of slurs and sexual coinages
# that would be worse served than omitted. Everything else is carried whole.
DENY = {
    "glowfaggot", "jailbait", "goonjuice", "goonrod", "goon cave", "gooner",
    "gooner bait", "goonette", "gooning", "goon", "dickflation", "grapey",
    "genayatollah", "brick up", "cornstar", "goy", "goybeam", "hivemind",
    "ML", "grv", "DF", "Brisket", "rope bunny", "R34", "Rule 34",
}

# Persian idiom matching folds these, so ی/ي and ک/ك spellings are one key.
FA_FOLD = str.maketrans({"ي": "ی", "ك": "ک", "ۀ": "ه", "أ": "ا", "إ": "ا",
                         "ؤ": "و", "\u200c": " ", "\u200f": " ", "\u200e": " "})


def fetch(url: str, name: str, refresh: bool) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / name
    if path.exists() and not refresh:
        return path
    print(f"  fetching {name} ...")
    # Hugging Face refuses a bare urllib agent, and every source here is a
    # plain public GET, so one honest name is all the request needs
    req = urllib.request.Request(
        url, headers={"User-Agent": "fluentify-slang-build/1.0"})
    with urllib.request.urlopen(req, timeout=300) as r, open(path, "wb") as f:
        f.write(r.read())
    return path


def fold(text: str) -> str:
    return " ".join(text.translate(FA_FOLD).lower().split())


# SlangLane's register is a phrase, not an enum: "informal conversational",
# "Critical · derogatory", "context-dependent". The bank needs a value both
# engines can translate for the learner, so the phrase is reduced to one of
# these and the original is kept beside it in "tone".
# "informal" has to be tested before "formal": it contains it, and the first
# version of this list labelled every informal term as formal.
REG_KEYS = ("archaic", "informal", "slang", "neutral", "idiom", "formal")


def reg_key(raw: str) -> str:
    text = (raw or "").lower()
    for key in REG_KEYS:
        if key in text:
            return key
    return "informal"


def build_slang(refresh: bool) -> tuple[list[dict], dict]:
    raw = fetch(SLANGLANE, "slanglane.jsonl", refresh).read_text(encoding="utf-8")
    rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
    authored = json.loads(AUTHORED.read_text(encoding="utf-8"))
    out, skipped = [], 0
    for r in rows:
        term = (r.get("term") or "").strip()
        if not term or r.get("maturity") == "mature" or term in DENY:
            skipped += 1
            continue
        summary = (r.get("summary") or "").strip()
        # the source repeats the term in front of the gloss more often than
        # not - "bruh: that's stupid" - and repeating it in the reply reads
        # as a stutter, so the head is peeled off when it is the term again
        for lead in (f"{term}: ", f"{term}:", f"In plain English, “{term}”: ",
                     f"In plain English, “{term}”:", f"In plain English, ”{term}“: "):
            if summary.startswith(lead):
                summary = summary[len(lead):]
                break
        out.append({
            "t": term,
            "al": r.get("aliases") or [],
            "cat": r.get("category") or "",
            "reg": reg_key(r.get("register") or ""),
            "tone": r.get("register") or "",
            "en": summary,
            "fa": authored.get(term, ""),
        })
    out.sort(key=lambda x: x["t"].lower())
    return out, {"read": len(rows), "used": len(out), "skipped": skipped}


def build_idioms(refresh: bool) -> tuple[list[dict], dict]:
    idioms: dict[str, dict] = {}

    for topic in json.loads(CURATED.read_text(encoding="utf-8"))["topics"]:
        for row in topic["idioms"]:
            key = fold(row["en"])
            idioms.setdefault(key, {
                "en": row["en"], "meaning": row.get("meaning", ""),
                "reg": "idiom", "ex": row.get("example", ""),
                "fa": row.get("fa", ""), "src": "curated",
            })

    idiomx_n = 0
    try:
        import pyarrow.parquet as pq  # noqa: PLC0415 - only needed to rebuild
    except ImportError:
        print("  ! pyarrow is not installed: the IdiomX layer is skipped")
        print("    /tmp/pq/bin/pip install pyarrow   (or any venv) to include it")
    else:
        path = fetch(IDIOMX, "idiomx.parquet", refresh)
        table = pq.read_table(path, columns=[
            "idiom_canonical", "idiom_canonical_meaning", "example",
            "idiom_register", "offensive_flag", "source", "is_generated_example",
        ])
        d = table.to_pydict()
        for i in range(table.num_rows):
            if d["source"][i] not in ("kaikki_wiktionary",
                                      "wiktionary_slang_kaikki"):
                continue
            if d["idiom_register"][i] not in ("slang", "informal"):
                continue
            if d["offensive_flag"][i] not in (None, False, "False", 0):
                continue
            en = (d["idiom_canonical"][i] or "").strip()
            meaning = (d["idiom_canonical_meaning"][i] or "").strip()
            example = (d["example"][i] or "").strip()
            if not en or not meaning:
                continue
            # "(my|your|his) two cents" is a Wiktionary article title, not
            # something a learner says; parenthesised forms and pipes are the
            # giveaway, and they would fail a literal match anyway
            if any(ch in en for ch in "()|{}[]") or len(en.split()) > 5:
                continue
            if len(en) < 3 or len(meaning) < 10 or len(meaning) > 260:
                continue
            if len(example) < 15 or len(example) > 200:
                example = ""
            key = fold(en)
            if key in idioms:
                continue
            idioms[key] = {
                "en": en, "meaning": meaning,
                "reg": d["idiom_register"][i], "ex": example, "fa": "",
                "src": "idiomx",
            }
            idiomx_n += 1

    # The parallel corpus is the only Persian idiom language there is. An
    # English idiom that appears in it gains the sentence it was used in and
    # the human Persian translation of that sentence.
    sara_n = 0
    en_fa = list(csv.DictReader(io.StringIO(
        fetch(SARA_EN_FA, "en_fa.csv", refresh).read_text(encoding="utf-8"))))
    for row in en_fa:
        key = fold(row.get("idiom") or "")
        if not key:
            continue
        entry = idioms.get(key)
        if entry is None:
            idioms[key] = {
                "en": row["idiom"].strip(), "meaning": "", "reg": "idiom",
                "ex": row.get("sentence", "").strip(), "fa": "",
                "exfa": row.get("gold translation", "").strip(),
                "src": "parallel",
            }
        elif not entry.get("exfa"):
            entry["exfa"] = row.get("gold translation", "").strip()
            if not entry.get("ex"):
                entry["ex"] = row.get("sentence", "").strip()
        sara_n += 1

    out = sorted(idioms.values(), key=lambda x: x["en"].lower())
    return out, {"curated": sum(1 for v in out if v["src"] == "curated"),
                 "idiomx": idiomx_n, "parallel": sara_n, "total": len(out)}


def build_fa_idioms(refresh: bool) -> tuple[list[dict], int]:
    rows = list(csv.DictReader(io.StringIO(
        fetch(SARA_FA_EN, "fa_en.csv", refresh).read_text(encoding="utf-8"))))
    out, seen = [], set()
    for row in rows:
        fa = (row.get("idiom") or "").strip()
        key = fold(fa)
        if not fa or key in seen:
            continue
        seen.add(key)
        out.append({
            "fa": fa,
            "exfa": (row.get("sentence") or "").strip(),
            "exen": (row.get("gold translation") or "").strip(),
        })
    out.sort(key=lambda x: x["fa"])
    return out, len(rows)


def main() -> int:
    refresh = "--refresh" in sys.argv
    print("building slang.json")
    slang, slang_stats = build_slang(refresh)
    idioms, idiom_stats = build_idioms(refresh)
    fa_idioms, fa_rows = build_fa_idioms(refresh)

    data = {
        "_meta": {
            "built": date.today().isoformat(),
            "sources": [
                {"name": "SlangLane", "url": "https://slanglane.com/data",
                 "license": "CC-BY-4.0",
                 "used": f'{slang_stats["used"]} slang terms'},
                {"name": "IdiomX", "url": "https://github.com/aymanshar/idiomx-dataset",
                 "license": "MIT repo; Wiktionary rows CC-BY-SA-4.0",
                 "used": f'{idiom_stats["idiomx"]} English slang idioms'},
                {"name": "Idiom_Translation (Sara Rezaeimanesh)",
                 "url": "https://github.com/Sara-Rezaeimanesh/Idiom_Translation",
                 "license": "see the repository",
                 "used": f"{fa_rows} parallel Persian idioms"},
                {"name": "DadmaTools", "url": "https://github.com/Dadmatech/DadmaTools",
                 "license": "MIT",
                 "used": "Persian character normalisation for matching"},
            ],
            "counts": {
                "slang": len(slang), "slang_with_fa": sum(1 for s in slang if s["fa"]),
                "idioms": len(idioms),
                "idioms_with_fa": sum(1 for i in idioms if i.get("fa")),
                "idioms_with_fa_example": sum(1 for i in idioms if i.get("exfa")),
                "fa_idioms": len(fa_idioms),
            },
            "note": ("Persian glosses for the slang terms are authored in "
                     "tools/slang_fa.json: the sources are English-only. "
                     "Mature-flagged slang is not carried."),
        },
        "slang": slang,
        "idioms": idioms,
        "fa_idioms": fa_idioms,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    size = OUT.stat().st_size / 1024
    c = data["_meta"]["counts"]
    print(f"  {c['slang']} slang ({c['slang_with_fa']} with Persian), "
          f"{c['idioms']} idioms ({c['idioms_with_fa']} with a Persian "
          f"equivalent, {c['idioms_with_fa_example']} with a Persian example), "
          f"{c['fa_idioms']} Persian idioms")
    print(f"  wrote {OUT.relative_to(ROOT)} ({size:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
