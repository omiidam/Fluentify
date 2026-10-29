#!/usr/bin/env python3
"""Both languages on one line: does every character survive, in its own script?

The page renders a line by tokenising it into runs - Persian, Latin, neutral -
and rebuilding it as isolated <bdi> islands. That is the only thing keeping a
Persian parenthesis inside an English sentence from being mirrored to the wrong
end, and an English term inside a Persian sentence from being parked at the far
edge.

Two ways that can go wrong, and neither is visible in a screenshot:

  * a character disappears - the parenthesis version of this shipped once: the
    bracketed Latin group was lifted out as a placeholder and never put back,
    so "(he/she/it)" simply was not on the page;
  * a run is not isolated - the text is all there, in the wrong order.

So this runs the shipped renderer (sliced out of webapp.py, not copied) in node,
and asserts, for real lines: the text content is exactly the input, no
placeholder leaks, every Persian run is a right-to-left island, every Latin run
inside a Persian line is a left-to-right island, and the parts of a mixed line
appear in the order they were written.

    python3 tools/check_bidi.py
"""

from __future__ import annotations

import glob
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEBAPP = ROOT / "webapp.py"
CACHE = ROOT / "tools/.cache"


def fn_body(src: str, name: str) -> str:
    """The body of `name(...)`, braces balanced, without the signature."""
    m = re.search(rf"(?:function\s+)?\b{re.escape(name)}\s*\([^)]*\)\s*\{{", src)
    if not m:
        raise ValueError(f"{name}() is not where this check looks for it")
    start, depth, i = m.end(), 1, m.end()
    while i < len(src) and depth:
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
        i += 1
    return src[m.start():i]


def const_line(src: str, name: str) -> str:
    m = re.search(rf"^const {name} = .*$", src, re.M)
    if not m:
        raise ValueError(f"{name} is not where this check looks for it")
    return m.group(0)


HARNESS = r"""
const problems = [];
const check = (ok, what) => { if (!ok) problems.push(what); return ok; };

/* stickerize() paints [fox:id] tokens; the drawing itself is irrelevant here,
   so it is stubbed and the token path stays exercised. */
const FOX_STICKERS = Object.create(null);
const foxSvg = () => null;

__CODE__

const strip = (h) => h.replace(/<[^>]*>/g, '')
  .replace(/&nbsp;/g, ' ').replace(/&lt;/g, '<')
  .replace(/&gt;/g, '>').replace(/&amp;/g, '&');

const samples = __SAMPLES__;
for (const s of samples) {
  const html = renderText(s.raw);
  const text = strip(html);
  const want = s.raw.replace(/\*\*/g, '');
  check(text === want,
        'text changed: ' + JSON.stringify(s.raw) + ' -> ' + JSON.stringify(text));
  check(!/[\ue000\ue001]/.test(html),
        'a placeholder leaked into ' + JSON.stringify(s.raw));
  check(html.startsWith('<div class="bl" dir="' + s.dir + '"'),
        JSON.stringify(s.raw) + ' was laid out ' + s.dir + ', not ' + s.dir);
  for (const part of (s.has || []))
    check(html.includes(part),
          'missing ' + JSON.stringify(part) + ' for ' + JSON.stringify(s.raw));
  for (const part of (s.hasNot || []))
    check(!html.includes(part),
          'unexpected ' + JSON.stringify(part) + ' for ' + JSON.stringify(s.raw));
  if (s.order) {
    const at = s.order.map((p) => text.indexOf(p));
    const sorted = at.every((v, i) => v >= 0 && (i === 0 || v > at[i - 1]));
    check(sorted, 'wrong order in ' + JSON.stringify(s.raw) + ': ' + JSON.stringify(s.order));
  }
  // every island must declare the direction of the script it holds
  for (const m of html.matchAll(/<bdi class="(fa|lat)"([^>]*)>/g)) {
    const wants = m[1] === 'fa' ? 'dir="rtl"' : 'dir="ltr"';
    check(m[2].includes(wants),
          'a ' + m[1] + ' island without ' + wants + ' in ' + JSON.stringify(s.raw));
  }
}

/* The same guarantee, at scale: every English and Persian string the lessons
   are built from, rendered on its own. A dropped character anywhere in a
   lesson would otherwise only be noticed by someone reading that lesson. */
const lessonLines = __LESSONS__;
for (const raw of lessonLines) {
  const html = renderText(raw);
  check(strip(html) === raw.replace(/\*\*/g, ''), 'lesson text changed: ' + JSON.stringify(raw));
  check(!/[\ue000\ue001]/.test(html), 'a placeholder leaked into ' + JSON.stringify(raw));
}

console.log(JSON.stringify({samples: samples.length, lessons: lessonLines.length, problems}));
process.exit(problems.length ? 1 : 0);
"""


def samples() -> list[dict]:
    """Lines the renderer has actually had to lay out, plus the shapes that
    have broken it: a bracket holding the other script, a Latin run ending a
    Persian sentence, an abbreviation, an unbalanced bracket.

    The word a sample is checked for is cut out of the sample itself rather than
    typed twice: Persian words carry invisible joiners, and two spellings of the
    same phrase are not the same string.
    """
    persian_with_latin = "فقط در سوم‌شخص (he/she/it) می‌آید"
    words = persian_with_latin.split(" ")
    return [
        {   # the shipped bug: a Persian parenthesis inside an English line
            "raw": "English (فعل حال ساده) here", "dir": "ltr",
            "has": ['<bdi class="paren" dir="ltr">(<bdi class="fa" lang="fa" dir="rtl">فعل حال ساده</bdi>)</bdi>'],
            "hasNot": ['<bdi class="lat"'],
            "order": ["English", "(فعل حال ساده)", "here"],
        },
        {   # the mirror case: a Latin parenthesis inside a Persian sentence
            "raw": persian_with_latin, "dir": "rtl",
            "has": ['<bdi class="paren" dir="rtl">(<bdi class="lat" lang="en" dir="ltr">he/she/it</bdi>)</bdi>',
                    '<bdi class="fa" lang="fa" dir="rtl">فقط در سوم‌شخص</bdi>'],
            "order": [words[2], words[3], words[4]],
        },
        {   # the full stop belongs to the Persian sentence, not to the island
            "raw": "مثل he/she/it.", "dir": "rtl",
            "has": ['>he/she/it</bdi>.'],
        },
        {   # an abbreviation keeps its internal dot and gives up only the last
            "raw": "مثلاً e.g. این", "dir": "rtl",
            "has": ['>e.g</bdi>.'],
        },
        {   # the words of one Persian phrase stay one island
            "raw": "فعل پایه + s", "dir": "rtl",
            "has": ['<bdi class="fa" lang="fa" dir="rtl">فعل پایه</bdi>', '<bdi class="lat"'],
        },
        {   # markup in the message is text, never markup
            "raw": "<script>alert(1)</script> سلام", "dir": "ltr",
            "has": ["&lt;/script&gt;", "&lt;script&gt;", "alert", "سلام"],
            "hasNot": ["<script>"],
        },
        {   # an unbalanced bracket must not swallow the rest of the line
            "raw": "سلام (دنیا", "dir": "rtl",
            "has": ["سلام</bdi> (", "دنیا"], "hasNot": ['<bdi class="paren"'],
        },
        {   # bold markers still work around an island
            "raw": "**bank** — بانک (river)", "dir": "ltr",
            "has": ["<b>bank</b>"],
        },
        {   # digits keep their own order on both sides
            "raw": "پیام ۵۰ و 3 new", "dir": "rtl",
            "has": ["۵۰", "3"],
        },
        {   # the translation marker of a lesson line
            "raw": "↲ فقط در سوم‌شخص (he/she/it) می‌آید", "dir": "rtl",
            "has": ['<span class="trm">↲</span>'],
        },
    ]


def lesson_strings() -> list[str]:
    """Every English and Persian string the grammar lessons are built from."""
    paths = [Path(p) for p in glob.glob(str(ROOT / "**/grammar*.json"), recursive=True)
             if "/node_modules/" not in p and not p.endswith("package.json")]
    if not paths:
        return []
    data = json.loads(max(paths, key=lambda p: p.stat().st_size).read_text(encoding="utf-8"))
    out: list[str] = []

    def walk(node) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if k in ("en", "fa") and isinstance(v, str):
                    if v and "\n" not in v:
                        out.append(v)
                else:
                    walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(data)
    return out


def main() -> int:
    src = WEBAPP.read_text(encoding="utf-8")
    try:
        code = "\n".join([
            fn_body(src, "escapeHtml"),
            fn_body(src, "lineDir"),
            fn_body(src, "stickerize"),
            const_line(src, "FA_TOKEN"),
            const_line(src, "EN_TOKEN"),
            const_line(src, "PAREN_OPEN"),
            const_line(src, "PAREN_CLOSE"),
            const_line(src, "TOKEN_RE"),
            fn_body(src, "inlineHtml"),
            fn_body(src, "renderText"),
        ])
    except ValueError as exc:
        print(f"FAIL  {exc}")
        return 1

    # A line's direction has to be written on the line itself. This is the bug
    # that made "nothing has changed" true for two rounds: unicode-bidi picks
    # the paragraph direction, but alignment comes from `direction`, which was
    # inherited left-to-right from the page.
    if 'dir="${dir}"' not in code:
        print("FAIL  renderText no longer writes dir on each line")
        return 1
    if '.bl[dir="rtl"] .lat' not in src:
        print("FAIL  the Latin-inside-Persian rule is gone")
        return 1

    if not shutil.which("node"):
        print("SKIP  node is not installed - mixed lines were not rendered")
        return 0

    CACHE.mkdir(parents=True, exist_ok=True)
    script = CACHE / "bidi_check.js"
    script.write_text(
        HARNESS.replace("__CODE__", code)
               .replace("__SAMPLES__", json.dumps(samples(), ensure_ascii=False))
               .replace("__LESSONS__", json.dumps(lesson_strings(), ensure_ascii=False)),
        encoding="utf-8")

    proc = subprocess.run(["node", str(script)], capture_output=True, text=True)
    out = proc.stdout.strip().split("\n")[-1] if proc.stdout.strip() else ""
    if proc.returncode != 0:
        detail = ""
        try:
            payload = json.loads(out)
            detail = "; ".join(payload.get("problems", [])[:6])
        except json.JSONDecodeError:
            detail = (proc.stderr or out).strip().split("\n")[0][:400]
        print("FAIL  " + (detail or "the mixed-line check did not pass"))
        return 1

    payload = json.loads(out)
    print(f"PASS  {payload['samples']} mixed lines and {payload['lessons']} lesson "
          f"strings keep every character, with Persian right-to-left and Latin "
          f"left-to-right")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
