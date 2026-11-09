#!/usr/bin/env python3
"""Rewrites the pronunciation handbook (phonetics.json) for General American.

The handbook was written around British symbols: /ɒ/ for hot, /əʊ/ for go, and
no r after a vowel. None of those describe the voice the app now speaks with,
so the rows, the model words and the notes are converted here in one place,
with an assert on every replacement so a later edit cannot silently skip one.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

PAIRS = [
    # ---- vowels: the symbol inventory
    ('"ip": "/e/ vs /æ/"', '"ip": "/ɛ/ vs /æ/"'),
    ('"ip": "/ɑː/",\n              "sub": "back vowel, long",\n              "say": "car",\n              "words": "park·star · hard·harm"',
     '"ip": "/ɑr/",\n              "sub": "rhotic — the r is pronounced",\n              "say": "car",\n              "words": "park·star · hard·harm"'),
    ('"ip": "/ɜː/",\n              "sub": "like /a/ with a smile",\n              "say": "bird",\n              "words": "first·person · turn·turtle"',
     '"ip": "/ɝː/",\n              "sub": "r-colored, as in bird",\n              "say": "bird",\n              "words": "first·person · turn·turtle"'),
    ('"ip": "/ɒ/",\n              "sub": "short, rounded",\n              "say": "hot",\n              "words": "not·note · lost·lost"',
     '"ip": "/ɑ/",\n              "sub": "open, unrounded",\n              "say": "hot",\n              "words": "not·nut · lost·last"'),
    ('"ip": "/ɔː/",\n              "sub": "long, rounded",\n              "say": "door",\n              "words": "all·awful · walk·talk"',
     '"ip": "/ɔr/",\n              "sub": "r-colored, rounded",\n              "say": "door",\n              "words": "call·tall · door·more"'),
    ('"ip": "/əʊ/"', '"ip": "/oʊ/"'),
    ('"ip": "/ɪə/",\n              "sub": "ear"', '"ip": "/ɪr/",\n              "sub": "ear + r"'),
    ('"ip": "/eə/",\n              "sub": "air"', '"ip": "/ɛr/",\n              "sub": "air, as in hair"'),
    ('/ɑː/ in \\"car\\" (mouth relaxed, long)',
     '/ɑr/ in \\"car\\" — the r is always pronounced'),
    # ---- -s and -ed
    ('\\"buses\\" is /ˈbjuːzɪz/', '\\"buses\\" is /ˈbʌsɪz/'),
    ('want → /ˈwɒntɪd/', 'want → /ˈwɑntɪd/'),
    ('walked → /wɔːkt/', 'walked → /wɔrkt/'),
    # ---- numbers, dates, money
    ('"2005",\n              "sub": "two thousand and five",\n              "say": "two thousand and five",\n              "note": "British English keeps \'and\'; American English often drops it"',
     '"2005",\n              "sub": "two thousand five",\n              "say": "two thousand five",\n              "note": "American English usually drops \'and\' after thousand"'),
    ('"ip": "March 3",\n              "sub": "the third of March",\n              "say": "the third of March",\n              "note": "write 3/3? British and American readers reverse day and month"',
     '"ip": "March 3",\n              "sub": "March third",\n              "say": "March third",\n              "note": "American dates put the month first: March 3, 2026"'),
    ('"ip": "7.30"', '"ip": "7:30"'),
    ('"ip": "$2.99",\n              "sub": "two pounds ninety-nine",\n              "say": "two pounds ninety-nine",\n              "words": "$1.50 · $10.99"',
     '"ip": "$2.99",\n              "sub": "two dollars ninety-nine",\n              "say": "two dollars ninety-nine",\n              "words": "$1.50 · $10.99"'),
    ('"sub": "nought point five",\n              "say": "nought point five",\n              "note": "American English says \'zero point five\'"',
     '"sub": "zero point five",\n              "say": "zero point five",\n              "note": "say \'zero\', not \'oh\', inside a decimal"'),
    # ---- letters and spelling aloud: Zed stays as a labeled comparison
    ('"note": "American English says \'zee\'; British English says \'zed\'"',
     '"note": "American English says \'zee\' — the model here; British English says \'zed\'"'),
    # ---- schwa model words
    ('"words": "holiday · memory · very · money"',
     '"words": "vacation · memory · very · money"'),
    # ---- /r/ is a full consonant in General American
    ('"note": "the tip of the tongue floats; it never curls back"',
     '"note": "the tongue body pulls back; the tip stays down and never touches the roof"'),
    # ---- final clusters
    ('"sub": "/ɑːskt/ — one syllable"', '"sub": "/æskt/ — one syllable"'),
    ('"sub": "/wɜːkt/ — k + t"', '"sub": "/wɝːkt/ — k + t"'),
    ('"sub": "/wɜːldz/ — l + d + z"', '"sub": "/wɝːldz/ — l + d + z"'),
    # ---- weak forms
    ('"ip": "was / were → /wəz/ /wə/"', '"ip": "was / were → /wəz/ /wɚ/"'),
    ('"sub": "/əˈnaʊə/"', '"sub": "/ən ˈaʊɚ/"'),
    ('"sub": "/ˈwɒtʃə/"', '"sub": "/ˈwʌtʃə/"'),
    ('"sub": "/kʌˈmɒn/"', '"sub": "/kəˈmɑn/"'),
    ('"sub": "/əˈlɌɒv/"', '"sub": "/əˈlɑt əv/"'),
    # ---- spelling patterns
    ('cough /ɒf/', 'cough /kɔf/'),
    ('heart /ɑː/', 'heart /hɑrt/'),
]


def main() -> int:
    path = ROOT / "phonetics.json"
    text = path.read_text(encoding="utf-8")
    missing = []
    for old, new in PAIRS:
        if old not in text:
            missing.append(old[:70])
            continue
        text = text.replace(old, new)
    if missing:
        print("american_phonetics: these anchors no longer exist:")
        for m in missing:
            print("  " + m)
        return 1
    data = json.loads(text)
    path.write_text(text, encoding="utf-8")
    print(f"rewrote the pronunciation handbook ({len(PAIRS)} edits, "
          f"{len(data['sections'])} sections)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
