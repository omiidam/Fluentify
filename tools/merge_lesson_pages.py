"""Merge authored page content into grammar.json.

Each lesson gained three things the pages need and the old data did not carry:
a scene for the In-context page, the Persian/English pairs the contrast page
prints side by side, and the last two mistakes of the five the mistakes page
shows. The batches live in tools/pages/batch*.py as plain data; this writes
them in, idempotently, so a batch can be edited and merged again.

    python3 tools/merge_lesson_pages.py tools/pages/batch1.py ...

"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(path):
    spec = importlib.util.spec_from_file_location("batch", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.P


def merge(pages):
    path = ROOT / "grammar.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    topics = data["topics"]
    added = {"scene": 0, "pairs": 0, "mistakes": 0}
    for key, page in pages.items():
        if key not in topics:
            raise SystemExit(f"no such lesson: {key}")
        t = topics[key]
        if "scene" in page:
            en, fa = page["scene"]
            if not en.strip() or not fa.strip():
                raise SystemExit(f"{key}: a scene needs both languages")
            t["scene"] = {"en": en, "fa": fa}
            added["scene"] += 1
        if "pairs" in page:
            pairs = []
            for fa, literal, en, why_en, why_fa in page["pairs"]:
                pairs.append({"fa": fa, "literal": literal, "en": en,
                              "why": {"en": why_en, "fa": why_fa}})
            t.setdefault("contrast", {})["pairs"] = pairs
            added["pairs"] += len(pairs)
        if "mistakes" in page:
            have = {m.get("wrong") for m in t.get("mistakes", [])}
            for row in page["mistakes"]:
                wrong, right, why_en, why_fa = row[:4]
                tag = row[4] if len(row) > 4 else ""

                if wrong in have:
                    continue
                t.setdefault("mistakes", []).append({
                    "wrong": wrong, "right": right,
                    "why": {"en": why_en, "fa": why_fa}, "tag": tag,
                })
                have.add(wrong)
                added["mistakes"] += 1
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n",
                    encoding="utf-8")
    return added


def main(argv):
    if not argv:
        raise SystemExit(__doc__)
    for p in argv:
        print(p, merge(load(p)))


if __name__ == "__main__":
    main(sys.argv[1:])
