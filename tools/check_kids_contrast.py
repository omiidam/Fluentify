#!/usr/bin/env python3
"""Are the Kids colours readable, or only pretty?

    python3 tools/check_kids_contrast.py

The Kids palette is built from washes and inks: a pale tint for a surface and
a dark ink for the words on it. That pairing is what makes the interface
colourful without making it unreadable, and it is exactly the kind of thing
that drifts - somebody lightens a wash to "feel friendlier" and a definition
goes to 3.9:1.

Kids have one theme now - the light one - so there is one skin to check. This
computes the real WCAG 2.2 contrast ratio for every pair that skin renders, and
it fails if a dark kid palette ever comes back, because a second theme is a
second set of colours nobody re-measured:

  * each section ink on its own wash (blue, purple, orange, pink, sun, coral,
    teal, lime) and navy on its wash
  * body text on the page, on a card, and the secondary text on both
  * what sits on a filled button (--k-on-primary on --k-primary)
  * the two status pairs, correct and incorrect

WCAG AA wants 4.5:1 for body text and 3:1 for large text. Every pair below
carries text at body size somewhere in the app, so the bar is 4.5:1 for all of
them. A failure names the pair and the ratio, so the fix is a shade, not a
guess.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "webapp.py"
AA = 4.5

# ink token -> what sits under it
PAIRS = [
    ("--k-primary-dark", "--k-primary-wash", "navy text on the navy wash"),
    ("--k-blue-ink", "--k-blue-wash", "words: ink on its wash"),
    ("--k-purple-ink", "--k-purple-wash", "grammar: ink on its wash"),
    ("--k-orange-ink", "--k-orange-wash", "hero quest: ink on its wash"),
    ("--k-pink-ink", "--k-pink-wash", "stories: ink on its wash"),
    ("--k-sun-ink", "--k-sun-wash", "sentences: ink on its wash"),
    ("--k-coral-ink", "--k-coral-wash", "reading: ink on its wash"),
    ("--k-teal-ink", "--k-teal-wash", "listening: ink on its wash"),
    ("--k-lime-ink", "--k-lime-wash", "word quest: ink on its wash"),
    ("--k-ink", "--k-bg", "body text on the page"),
    ("--k-ink", "--k-surface", "body text on a card"),
    ("--k-ink", "--k-surface-2", "body text on a raised card"),
    ("--k-ink-2", "--k-bg", "secondary text on the page"),
    ("--k-ink-2", "--k-surface", "secondary text on a card"),
    ("--k-on-primary", "--k-primary", "button label on a filled button"),
    ("--k-good", "--k-good-wash", "correct: ink on its wash"),
    ("--k-bad", "--k-bad-wash", "incorrect: ink on its wash"),
]

FAIL = []


def lum(hexcolour: str) -> float:
    h = hexcolour.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def ratio(a: str, b: str) -> float:
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def block(src: str, selector: str) -> str:
    """The CSS text of one rule, by brace matching (the palette is one rule)."""
    at = src.find(selector)
    if at < 0:
        return ""
    start = src.find("{", at)
    if start < 0:
        return ""
    depth = 0
    for i in range(start, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[start + 1:i]
    return ""


def tokens(css: str) -> dict:
    return dict(re.findall(r"(--k-[a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{3,8})", css))


def check(toks: dict) -> None:
    for ink, wash, what in PAIRS:
        a, b = toks.get(ink), toks.get(wash)
        if not a or not b:
            FAIL.append(f"{what} has no colour ({ink} / {wash})")
            continue
        r = ratio(a, b)
        status = "ok  " if r >= AA else "FAIL"
        print(f"  {status}  {r:5.2f}:1  {what}")
        if r < AA:
            FAIL.append(f"{what} is {r:.2f}:1, under {AA}:1 ({a} on {b})")


def main() -> int:
    src = PAGE.read_text(encoding="utf-8")
    if '[data-theme="dark"] body.kids' in src:
        print("FAIL  kids are back to two themes, and only the light one is measured")
        return 1
    light = tokens(block(src, "body.kids {"))
    if not light:
        print("FAIL  the kids palette could not be read from webapp.py")
        return 1
    print(f"Kids colour contrast, WCAG AA ({AA}:1 for text)\n")
    check(light)
    print()
    if FAIL:
        print(f"FAIL  {len(FAIL)} contrast problem(s)")
        for line in FAIL:
            print("  -", line)
        return 1
    print(f"PASS  {len(PAIRS)} colour pairs clear {AA}:1 in the one kids skin")
    return 0


if __name__ == "__main__":
    sys.exit(main())
