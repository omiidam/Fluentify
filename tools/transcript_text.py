#!/usr/bin/env python3
"""Readable text out of a BBC transcript PDF, without a PDF library.

    python3 tools/transcript_text.py tools/.cache/bbc/6 Minute English-250403.pdf

Why this exists
---------------
fetch_bbc_6min.py already has pdf_to_text(), and it is good enough for what it
is for: counting words and scoring vocabulary, where a stray space between two
letters costs nothing. It is not good enough to put in front of a reader - it
pulls the text literals out of the content stream with no idea where they are
on the page, so it returns

    "Beth Hello and welcome to 6 Minute English from BBC Learning English. I
     ' m Beth ."

One letter per fragment, in the order the fragments were written rather than
the order they appear, with the side column folded into the middle of the
sentence. It graded the episodes; nobody was supposed to read it.

These PDFs are simple enough to read properly without a dependency: one text
layer, no rotation, no tables, and every fragment is placed by an explicit Tm.
So this walks the content stream properly instead:

  * the CTM, so text is positioned where it lands on the page rather than in
    the local space of whichever text box it was written in - without this,
    two pages of the transcript land on top of each other
  * the text matrix, which is where BBC does its font scaling (Tf is 1 for
    every font; the size is in Tm), so a glyph width can be estimated
  * the page, because every page numbers its lines from the same origin
  * the column, because the vocabulary box sits beside the dialogue at the
    same height and folding it in turns a sentence into gibberish

The result is the transcript as printed: a heading, then the dialogue, with
the vocabulary beside it.
"""

from __future__ import annotations

import re
import sys
import zlib
from pathlib import Path

# A number, a name, or an operator. The tokenizer walks these rather than
# regexing for one operator, because a regex over a content stream that
# interleaves three megabytes of font program with two hundred bytes of text
# is how you get a tool that takes forty seconds per episode.
NUMBER = re.compile(r"[-+]?\d*\.?\d+")
OPERATOR = re.compile(r"[A-Za-z*'\"]+")

# More than this fraction of printable bytes and it is a content stream. Font
# programs and images inflate to megabytes of binary that happens to contain
# the two letters "BT", and feeding one of those to the interpreter produces
# lines of pure noise at the end of the transcript.
PRINTABLE = 0.95
MAX_STREAM = 2_000_000


def _is_text(blob: bytes) -> bool:
    if not blob or len(blob) > MAX_STREAM:
        return False
    ok = sum(1 for b in blob if 32 <= b < 127 or b in (9, 10, 13))
    return ok / len(blob) >= PRINTABLE


def _macroman(chars: list[str]) -> str:
    """The text bytes back out of the latin-1 view of the stream.

    The stream is read as latin-1 so that every byte survives as one char and
    the tokenizer can walk it. PDF string literals are then MacRoman unless a
    font says otherwise, and these PDFs' fonts only ever override the space -
    the ToUnicode CMap in one of them maps 0x21 and stops.
    """
    try:
        raw = bytes(ord(c) for c in chars)
    except ValueError:
        return "".join(chars)
    return raw.decode("mac_roman", "replace")


def _mul(m: tuple, n: tuple) -> tuple:
    """m then n, in the row-vector convention PDF matrices use."""
    a1, b1, c1, d1, e1, f1 = m
    a2, b2, c2, d2, e2, f2 = n
    return (a1 * a2 + b1 * c2, a1 * b2 + b1 * d2,
            c1 * a2 + d1 * c2, c1 * b2 + d1 * d2,
            e1 * a2 + f1 * c2 + e2, e1 * b2 + f1 * d2 + f2)


def _fonts(data: bytes) -> dict[str, dict[int, int]]:
    """/TT5 -> {character code: advance in 1/1000 em}, from /Widths.

    Without this the only way to know whether two fragments are one word or two
    is to guess at how wide a character is, and every guess is wrong somewhere
    that shows: estimating half an em puts "Yeah,so" and "dairyso" in the
    transcript. The widths are in the file, so they are read from the file.

    The font resource dictionaries are per page and these PDFs reuse the same
    subset on every page, so one merged table is enough. A PDF that gave two
    pages different subsets under the same name would need the page number in
    the key; none of these do, and guessing per character is worse than
    inheriting a table that is right 99% of the time.
    """
    objects = {int(m.group(1)): m.group(2)
               for m in re.finditer(rb"(\d+) 0 obj(.*?)endobj", data, re.S)}
    widths: dict[int, dict[int, int]] = {}
    for num, body in objects.items():
        if b"/Font" not in body:
            continue
        raw = re.search(rb"/Widths\s*\[([^\]]*)\]", body)
        first = re.search(rb"/FirstChar\s+(\d+)", body)
        if not raw or not first:
            continue
        base = int(first.group(1))
        vals = [int(v) for v in raw.group(1).split()]
        widths[num] = {base + i: v for i, v in enumerate(vals) if v >= 0}

    table: dict[str, dict[int, int]] = {}
    for m in re.finditer(rb"/Font\s*<<(.*?)>>", data, re.S):
        for name, ref in re.findall(rb"/(\w+)\s+(\d+)\s+0\s+R", m.group(1)):
            if int(ref) in widths:
                table[name.decode("latin-1")] = widths[int(ref)]
    return table


def _apply(m: tuple, x: float, y: float) -> tuple[float, float]:
    a, b, c, d, e, f = m
    return a * x + c * y + e, b * x + d * y + f


def _page_runs(stream: bytes, fonts: dict[str, dict[int, int]] | None = None,
               scale: float = 1.0) -> list[tuple[float, float, float, float, str]]:
    """[(y, x, size, width, text)] for one content stream, page coordinates."""
    fonts = fonts or {}
    out: list[tuple[float, float, float, float, str]] = []
    text = stream.decode("latin-1")
    ctm = (1, 0, 0, 1, 0, 0)
    saved: list[tuple] = []
    tm: tuple = (1, 0, 0, 1, 0, 0)
    size = 1.0
    font = ""
    ops: list = []
    i, n = 0, len(text)

    while i < n:
        ch = text[i]
        if ch.isdigit() or ch in "+-.":
            j = i
            while j < n and (text[j].isdigit() or text[j] in "+-.eE"):
                j += 1
            try:
                ops.append(float(text[i:j]))
            except ValueError:
                pass
            i = j
            continue
        if ch == "(":
            depth, k, buf = 1, i + 1, []
            while k < n and depth:
                c = text[k]
                if c == "\\":
                    k += 1
                    if k < n:
                        buf.append(text[k])
                elif c == "(":
                    depth += 1
                    buf.append(c)
                elif c == ")":
                    depth -= 1
                    if depth:
                        buf.append(c)
                else:
                    buf.append(c)
                k += 1
            ops.append(("s", _macroman(buf)))
            i = k
            continue
        if ch == "/":
            # A name object. It has to be read rather than skipped: "/TT5 1 Tf"
            # is the only thing that says which font the widths belong to.
            m = re.match(r"/([^\s/\[\]<>(){}]*)", text[i:])
            if m:
                ops.append(("n", m.group(1)))
                i += m.end()
            else:
                i += 1
            continue
        if ch == "[":
            ops.append(("[", None))
            i += 1
            continue
        if ch == "]":
            ops.append(("]", None))
            i += 1
            continue
        m = OPERATOR.match(text, i)
        if not m:
            i += 1
            continue
        op = m.group(0)
        i = m.end()

        if op == "q":
            saved.append(ctm)
        elif op == "Q":
            if saved:
                ctm = saved.pop()
        elif op == "cm" and len(ops) >= 6:
            ctm = _mul(tuple(ops[-6:]), ctm)
        elif op == "Tm" and len(ops) >= 6:
            tm = tuple(ops[-6:])
        elif op == "Tf":
            for v in reversed(ops):
                if isinstance(v, tuple) and v[0] == "n":
                    font = v[1]
                    break
            for v in reversed(ops):
                if isinstance(v, float):
                    size = v
                    break
        elif op in ("Tj", "TJ", "'", '"'):
            if op in ("'", '"'):
                tm = (size, 0, 0, size, tm[4], tm[5])
            buf = ""
            for v in ops:
                if isinstance(v, tuple) and v[0] == "s":
                    buf += v[1]
                elif isinstance(v, float) and v <= -100:
                    # A wide negative number inside a TJ array is a word
                    # space that the typesetter expressed as a gap rather
                    # than as a space character.
                    buf += " "
            if buf.strip():
                x, y = _apply(_mul(tm, ctm), 0, 0)
                # The drawn size is Tf scaled by Tm and then by the CTM. BBC
                # sets every font to 1 and scales in Tm, so using Tf alone -
                # or Tm alone - puts every width estimate fifty times out.
                drawn = abs(size * tm[0] * ctm[0]) or 1.0
                # How far this run actually reaches, in the same units as x.
                table = fonts.get(font) or {}
                advance = sum(table.get(ord(c), 500) for c in buf if c != " ")
                wide = advance / 1000.0 * size * abs(tm[0] * ctm[0])
                out.append((round(y, 1), round(x, 1), drawn, wide, buf))
            if op in ("'", '"'):
                tm = (size, 0, 0, size, tm[4], tm[5] - size * 1.2)
        ops = []
    return out


def _join_row(runs: list[tuple[float, float, float, str]]) -> list[str]:
    """One printed line can be two columns. Keep them apart."""
    lines: list[str] = []
    column: list[str] = []
    last = ""
    prev_end: float | None = None
    for x, size, width, txt in runs:
        em = max(size, 1.0)
        if prev_end is not None:
            # Six ems is a jump from one column of the page to another. The
            # smaller gaps are ordinary typesetting: a fragment boundary
            # inside a sentence, or a word the layout engine placed on its
            # own.
            if x - prev_end > em * 6:
                lines.append("".join(column))
                column = []
                prev_end = None
                last = ""
            elif (x - prev_end > em * 0.1
                  and txt[:1] not in ",.;:!?)'”’"):
                # ...and never before punctuation: "I" and "'m" are one word
                # that the text layer cut in half, and it is the apostrophe
                # that shows up most often.
                #
                # Nor between a lone capital and a lowercase run. BBC splits
                # "Allergies" as "A" + "llergies" with a gap the width of a
                # space, so the geometry alone says word; the letter says
                # otherwise. "I" is left out of the class - "I am" really is
                # two words, and it is the only capital that is one letter and
                # a word at the same time.
                if not (re.search(r"(?:\A|\s)[A-HJ-Z]$", last)
                        and txt[:1].islower()):
                    column.append(" ")
        column.append(txt)
        last = txt
        prev_end = x + width
    lines.append("".join(column))
    return lines


def pdf_to_lines(data: bytes) -> list[str]:
    """The transcript, as printed, one entry per printed line."""
    fonts = _fonts(data)
    pages: list[list[str]] = []
    for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", data, re.S):
        blob = m.group(1)
        try:
            blob = zlib.decompress(blob)
        except zlib.error:
            pass
        if not _is_text(blob):
            continue
        runs = _page_runs(blob, fonts)
        if not runs:
            continue
        # Every page counts its lines down from its own origin, so rows are
        # grouped per page. Merging them across pages puts the vocabulary box
        # of page one in the middle of the dialogue on page two.
        rows: dict[float, list[tuple[float, float, float, str]]] = {}
        for y, x, size, width, txt in runs:
            rows.setdefault(y, []).append((x, size, width, txt))
        page: list[str] = []
        for y in sorted(rows, reverse=True):
            for line in _join_row(sorted(rows[y])):
                line = re.sub(r"[ \t]{2,}", " ", line).strip()
                if line:
                    page.append(line)
        pages.append(page)

    out: list[str] = []
    for page in pages:
        out.extend(page)
    return out


def clean(text: str) -> str:
    """Tidy one extracted line without losing where it breaks."""
    text = text.replace("\u00ad", "")                 # soft hyphen
    text = re.sub(r"([a-z])- ([a-z])", r"\1\2 ", text)  # end-of-line hyphen
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"\(\s*\)", "", text)               # an empty speaker slot
    return re.sub(r"\s{2,}", " ", text).strip()


# What BBC prints on every page that is not the transcript: the running foot,
# the page number, and the little "!" that stands in for the audio icon.
FURNITURE = re.compile(
    r"^(?:!+$|Page \d+ of \d+|©\s*British Broadcasting Corporation.*"
    r"|bbclearningenglish\.com|\d+ Minute English\s*)$",
    re.I)


def pdf_to_text_readable(data: bytes) -> str:
    """The transcript as a reader wants it: blank line between paragraphs."""
    lines = [clean(l) for l in pdf_to_lines(data)]
    lines = [l for l in lines if l and not FURNITURE.match(l)]
    out: list[str] = []
    for line in lines:
        if out and not out[-1] and line[:1].islower():
            continue                     # a continuation of the line above
        out.append(line)
        # A line that ends a sentence and the next that starts a capital is a
        # new speaker, a new paragraph, or a heading. BBC separates all three
        # with vertical space that the text layer does not carry.
        if out and line.endswith((".", "?", "!", ":")):
            out.append("")
    while out and not out[-1]:
        out.pop()
    return "\n".join(out)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        path = Path(arg)
        print(f"===== {path.name}")
        print(pdf_to_text_readable(path.read_bytes())[:4000])