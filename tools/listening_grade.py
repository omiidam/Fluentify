#!/usr/bin/env python3
"""Grade a spoken English passage A1→C1 from its transcript.

Listening difficulty is not reading difficulty. A BBC presenter delivers
150-odd words a minute with contractions and reductions, so a passage a reader
would call B1 can be a B2 listening task. The score therefore blends:

  stretch      the 75th percentile of content-word CEFR levels - the
               vocabulary you must already have to keep up
  challenge    the share of content tokens at B2 or above - how much of the
               passage is *new* work for a learner
  syntax       sentence length and clause density, the two things that make
               a listener lose the thread
  density      words per minute of the episode, which separates a slow careful
               read from a fast discussion

The blend is calibrated against BBC's own "intermediate" tag on the episodes
where it publishes one: see --audit. The point of an independent grader is
that it can disagree, so the tag is used to check the calibration rather than
to produce the answer.

Word levels come from the CEFR-J list (Maximax67/Words-CEFR-Dataset, MIT),
already cached by fetch_dictionary.py.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

BANDS = {1: "A1", 2: "A2", 3: "B1", 4: "B2", 5: "C1", 6: "C2"}

# Closed-class words carry no difficulty signal and would drag every text down.
FUNCTION_WORDS = {
    "the", "a", "an", "and", "or", "but", "if", "of", "to", "in", "on", "at",
    "for", "with", "is", "are", "was", "were", "be", "been", "being", "am",
    "do", "does", "did", "doing", "have", "has", "had", "having", "will",
    "would", "shall", "can", "could", "should", "may", "might", "must",
    "that", "this", "these", "those", "it", "its", "he", "she", "they", "them",
    "we", "us", "you", "your", "i", "me", "my", "as", "so", "than", "then",
    "not", "no", "yes", "there", "here", "what", "who", "whom", "whose",
    "how", "when", "where", "which", "why", "because", "about", "into",
    "from", "by", "up", "down", "out", "over", "under", "again", "very",
    "just", "too", "also", "even", "well", "back", "still", "such", "own",
    "same", "other", "another", "one", "two", "three", "all", "any", "some",
    "each", "every", "both", "few", "more", "most", "many", "much", "more",
    "get", "got", "go", "goes", "going", "went", "come", "comes", "came",
    "make", "makes", "made", "take", "takes", "took", "know", "knows",
    "knew", "think", "thinks", "thought", "say", "says", "said", "see",
    "sees", "saw", "look", "looks", "looked", "want", "wants", "use", "used",
    "let", "really", "thing", "things", "something", "anything", "nothing",
    "everything", "someone", "anyone", "everyone", "lot", "bit", "gonna",
    "right", "okay", "ok", "yeah", "hello", "hi", "bye",
}

WORD = re.compile(r"[A-Za-z][A-Za-z'-]*")
CLAUSE_MARKER = re.compile(
    r"\b(?:because|although|though|while|whereas|which|who|whom|whose|"
    r"that|if|when|unless|until|so that|even though|as soon as|"
    r"given that|provided that)\b", re.IGNORECASE)

# BBC tags each episode with a course level, and those are RANGES, not
# points: "intermediate" covers B1-B2. Collapsing them to one band would
# manufacture a disagreement that is really a range, so the audit checks
# containment instead. Used only to check the calibration, never to produce
# the grade.
BBC_TAG_RANGE = {
    "elementary": ("A1", "A2"),
    "lower-intermediate": ("A2", "B1"),
    "intermediate": ("B1", "B2"),
    "upper-intermediate": ("B2", "C1"),
}
BAND_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]


def in_band_range(level: str, tag: str | None) -> bool:
    """Is this grade inside the band BBC's own tag implies?"""
    if not level or not tag or tag not in BBC_TAG_RANGE:
        return False
    lo, hi = BBC_TAG_RANGE[tag]
    return BAND_ORDER.index(lo) <= BAND_ORDER.index(level) <= BAND_ORDER.index(hi)


def load_cefr() -> dict[str, int]:
    """word -> lowest CEFR band, reusing fetch_dictionary.py's cache."""
    import json
    import subprocess

    cache = Path(__file__).resolve().parent / ".cache" / "dictionary.json"
    if not cache.exists():
        print("building the CEFR table … (first run only)")
        subprocess.run([sys.executable,
                        str(Path(__file__).resolve().parent / "fetch_dictionary.py")],
                       check=True)
    return json.loads(cache.read_text(encoding="utf-8"))


def tokenise(text: str) -> list[str]:
    return [w.lower() for w in WORD.findall(text)]


def percentile(sorted_values: list[int], pct: float) -> int:
    if not sorted_values:
        return 1
    k = max(0, min(len(sorted_values) - 1, int(round(len(sorted_values) * pct))))
    return sorted_values[k]


def clean_transcript(text: str) -> str:
    """Turn a PDF transcript dump into readable prose.

    The extracted text is a stream of short line fragments with the speakers'
    names repeated and a licence header in front, which wrecks any sentence
    statistic. Joining the fragments and dropping the furniture fixes both.
    """
    # licence / production header, everything before the first real utterance
    cut = re.search(r"(?:^|\s)((?:Hi|Hello|Hello there)[,.]?\s)", text)
    if cut:
        text = text[cut.start(1):]
    # speaker labels sit inline: "Georgie   " / "Vocabulary   "
    text = re.sub(r"\b(?:Vocabulary|VOCABULARY|Transcript|transcript)\b", " ", text)
    # The title block is drawn with letter kerning and extracts as
    # "BBC LEARNI NG ENGLI SH" — drop any stretch where most tokens are a
    # lone letter or a two-letter fragment, which is the kerning signature.
    text = re.sub(r"(?:[A-Za-z]{1,2}\s+){6,}[A-Za-z]{1,2}", " ", text)
    text = re.sub(r"(?<=\s)[A-Za-z](?=\s)", " ", text)
    text = re.sub(r"©\s*[A-Za-z0-9 ,.&-]{0,40}", " ", text)
    # stray page furniture
    text = re.sub(r"\d{1,2}\b", " ", text)
    text = text.replace("\n", " ")
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def _speakers_removed(text: str) -> str:
    """Drop the recurring presenter names that prefix each turn."""
    for name in ("Georgie", "Neil", "Catherine", "Sam", "Beth", "Danny",
                 "Fiona", "Harry", "Rachel", "Jennifer", "Beth", "Sian"):
        text = re.sub(rf"\b{name}\b\s*", " ", text)
    return re.sub(r"\s{2,}", " ", text)


def grade_text(text: str, cefr: dict[str, int], wpm: float | None = None) -> dict:
    """Return {'level': 'B2', ...} for one passage."""
    prose = _speakers_removed(clean_transcript(text))
    words = tokenise(prose)
    n_words = len(words)
    if n_words < 60:
        return {"level": None, "total_words": n_words, "reason": "too short"}

    content_words = [w for w in words if w in cefr and w not in FUNCTION_WORDS]
    levels = [cefr[w] for w in content_words]
    if len(levels) < 40:
        return {"level": None, "total_words": n_words, "reason": "too little vocabulary"}

    levels_sorted = sorted(levels)
    stretch = percentile(levels_sorted, 0.75)
    challenge = sum(1 for lv in levels if lv >= 4) / len(levels)
    top_share = sum(1 for lv in levels if lv >= 5) / len(levels)

    # --- syntax -------------------------------------------------------------
    sentences = [s for s in re.split(r"[.!?]+(?:\s|$)", prose) if s.strip()]
    n_sent = max(1, len(sentences))
    avg_len = n_words / n_sent
    clause_density = len(CLAUSE_MARKER.findall(prose)) / n_sent
    # 12 words/sentence is easy, 26+ is demanding; 0 clauses easy, 0.6+ dense
    syntax = (
        max(1.0, min(6.0, 1 + (avg_len - 10) / 4.0))
        + max(0.0, min(3.0, clause_density * 4.0))
    ) / 1.4

    # --- density -----------------------------------------------------------
    # Words per minute matters more for listening than for reading. Derived
    # from the episode length when known, otherwise assumed BBC pace.
    pace = float(wpm) if wpm else 150.0
    density = max(1.0, min(6.0, 1 + (pace - 110) / 25.0))

    # --- blend -------------------------------------------------------------
    # stretch dominates: the vocabulary you must already own sets the floor.
    score = (0.50 * stretch
             + 0.22 * (1 + challenge * 4)
             + 0.18 * syntax
             + 0.10 * density)
    score += min(0.6, top_share * 3)      # a genuine C2 tail pulls it up

    level_num = max(1, min(6, int(round(score))))

    return {
        "level": BANDS[level_num],
        "score": round(score, 2),
        "stretch": BANDS[stretch],
        "syntax": round(syntax, 2),
        "avg_sentence": round(avg_len, 1),
        "clauses_per_sentence": round(clause_density, 2),
        "challenge_pct": round(100 * challenge),
        "c1c2_pct": round(100 * top_share),
        "wpm": round(pace),
        "total_words": n_words,
        "unique_content": len(set(content_words)),
    }


def bbc_level_from_page(html: str) -> str | None:
    """BBC's own course level for an episode, as a tag like "intermediate".

    Returns the raw tag, not a single band: the tags are course *ranges*, and
    keeping the range is what lets --audit check containment honestly.
    """
    m = re.search(r'id="heading-([a-z\-]+)-level"', html)
    if not m:
        return None
    tag = m.group(1)
    return tag if tag in BBC_TAG_RANGE else None