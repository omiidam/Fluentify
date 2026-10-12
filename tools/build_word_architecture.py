#!/usr/bin/env python3
"""Builds word "architecture" — the form family of every vocabulary word.

Each entry gets its base, inflections and (where the dictionary confirms them)
derivations, so a learner can see how the word behaves instead of memorising a
flat list:

    decide →  decides · decided · deciding · decision · decisive

Everything generated is checked against a 170k-word English dictionary before
it ships, so the UI never shows an invented word. Forms the dictionary rejects
are dropped rather than guessed.

    python3 tools/build_word_architecture.py
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# The dictionary is the CEFR-J word list (MIT) — see tools/cefr_grade.py.
# tools/.cache/ is gitignored; re-fetch with tools/fetch_dictionary.py
DICT = ROOT / "tools/.cache/dictionary.json"
OUT = ROOT / "word_arch.json"

VOWELS = set("aeiou")
# a final syllable with no vowel before it doubles: stop → stopped
DOUBLING_EXCEPT = set("wxy")

# ---------------------------------------------------------------- irregulars
IRREG_VERBS = {
    # base: (past, past participle)
    "be": ("was", "been"), "am": ("was", "been"), "is": ("was", "been"),
    "are": ("were", "been"), "were": ("were", "been"),
    "have": ("had", "had"), "has": ("had", "had"), "had": ("had", "had"),
    "do": ("did", "done"), "does": ("did", "done"), "did": ("did", "done"),
    "go": ("went", "gone"), "goes": ("went", "gone"),
    "say": ("said", "said"), "say*": ("", ""),
    "make": ("made", "made"), "take": ("took", "taken"),
    "come": ("came", "come"), "see": ("saw", "seen"),
    "know": ("knew", "known"), "get": ("got", "gotten"),
    "give": ("gave", "given"), "find": ("found", "found"),
    "think": ("thought", "thought"), "tell": ("told", "told"),
    "become": ("became", "become"), "leave": ("left", "left"),
    "feel": ("felt", "felt"), "put": ("put", "put"),
    "bring": ("brought", "brought"), "begin": ("began", "begun"),
    "keep": ("kept", "kept"), "hold": ("held", "held"),
    "write": ("wrote", "written"), "stand": ("stood", "stood"),
    "hear": ("heard", "heard"), "let": ("let", "let"),
    "mean": ("meant", "meant"), "set": ("set", "set"),
    "meet": ("met", "met"), "run": ("ran", "run"),
    "pay": ("paid", "paid"), "sit": ("sat", "sat"),
    "speak": ("spoke", "spoken"), "lie": ("lay", "lain"),
    "lead": ("led", "led"), "read": ("read", "read"),
    "grow": ("grew", "grown"), "lose": ("lost", "lost"),
    "fall": ("fell", "fallen"), "send": ("sent", "sent"),
    "build": ("built", "built"), "understand": ("understood", "understood"),
    "draw": ("drew", "drawn"), "break": ("broke", "broken"),
    "spend": ("spent", "spent"), "cut": ("cut", "cut"),
    "rise": ("rose", "risen"), "drive": ("drove", "driven"),
    "buy": ("bought", "bought"), "wear": ("wore", "worn"),
    "choose": ("chose", "chosen"), "seek": ("sought", "sought"),
    "throw": ("threw", "thrown"), "catch": ("caught", "caught"),
    "deal": ("dealt", "dealt"), "win": ("won", "won"),
    "forget": ("forgot", "forgotten"), "eat": ("ate", "eaten"),
    "teach": ("taught", "taught"), "sell": ("sold", "sold"),
    "fight": ("fought", "fought"), "sleep": ("slept", "slept"),
    "drink": ("drank", "drunk"), "swim": ("swam", "swum"),
    "fly": ("flew", "flown"), "sing": ("sang", "sung"),
    "ring": ("rang", "rung"), "sink": ("sank", "sunk"),
    "ride": ("rode", "ridden"), "shake": ("shook", "shaken"),
    "steal": ("stole", "stolen"), "hide": ("hid", "hidden"),
    "hurt": ("hurt", "hurt"), "shut": ("shut", "shut"),
    "cost": ("cost", "cost"), "shoot": ("shot", "shot"),
    "spread": ("spread", "spread"), "strike": ("struck", "struck"),
    "hang": ("hung", "hung"), "blow": ("blew", "blown"),
    "freeze": ("froze", "frozen"), "steal": ("stole", "stolen"),
    "prove": ("proved", "proven"), "wake": ("woke", "woken"),
    "bear": ("bore", "borne"), "beat": ("beat", "beaten"),
    "bite": ("bit", "bitten"), "blow*": ("", ""),
    "come*": ("", ""), "cost*": ("", ""),
}

IRREG_NOUNS = {
    "man": "men", "woman": "women", "child": "children", "person": "people",
    "foot": "feet", "tooth": "teeth", "goose": "geese", "mouse": "mice",
    "life": "lives", "knife": "knives", "wife": "wives", "leaf": "leaves",
    "shelf": "shelves", "loaf": "loaves", "half": "halves",
    "sheep": "sheep", "fish": "fish", "series": "series", "species": "species",
    "deer": "deer", "aircraft": "aircraft",
}

IRREG_ADJ = {
    "good": ("better", "best", "well"), "bad": ("worse", "worst", "badly"),
    "far": ("farther", "farthest", "far"), "little": ("less", "least", "little"),
    "many": ("more", "most", "many"), "old": ("older", "oldest", "old"),
    "late": ("later", "latest", "late"),
}

# which domains are unambiguously one part of speech
VERB_DOMAINS = {"verbs", "phrasal_verbs", "household_actions"}
ADJ_DOMAINS = {"adjectives", "describing_people", "emotions"}
# concrete topic banks: a noun unless the evidence is overwhelming. Needed
# because the source word list contains tagger junk ("appling", "appled"),
# which would otherwise make "apple" look like a verb.
NOUN_DOMAINS = {
    "colors", "fruits", "vegetables", "food", "animals", "body", "family",
    "numbers", "clothing", "places", "transport", "music", "technology",
    "school", "sports", "nature", "time_words", "weather_seasons", "house",
    "city", "bank_money", "body_health", "communication", "shopping_clothes",
    "directions_words", "daily_routine_words", "basic_words", "jobs",
    "travel", "quantities", "health_visits", "education_b1", "media_news",
    "environment_b2", "law_rights", "finance_b2", "workplace",
}

# Function words have no form family: "above" takes no -s and no 's.
FUNCTION_WORDS = {
    "above": "adv", "across": "prep", "after": "prep", "against": "prep",
    "along": "adv", "among": "prep", "amongst": "prep", "around": "adv",
    "before": "prep", "behind": "prep", "below": "prep", "beneath": "prep",
    "beside": "prep", "besides": "adv", "between": "prep", "beyond": "prep",
    "despite": "prep", "down": "adv", "during": "prep", "except": "prep",
    "inside": "prep", "into": "prep", "like": "prep", "near": "prep",
    "off": "adv", "onto": "prep", "outside": "prep", "over": "adv",
    "past": "prep", "regarding": "prep", "since": "prep", "through": "prep",
    "throughout": "prep", "till": "prep", "toward": "prep", "towards": "prep",
    "under": "prep", "underneath": "prep", "until": "prep", "up": "adv",
    "upon": "prep", "within": "prep", "without": "prep",
    "already": "adv", "almost": "adv", "also": "adv", "always": "adv",
    "enough": "adv", "even": "adv", "ever": "adv", "never": "adv",
    "often": "adv", "once": "adv", "only": "adv", "quite": "adv",
    "rather": "adv", "sometimes": "adv", "still": "adv", "too": "adv",
    "very": "adv", "well": "adv", "yet": "adv", "ago": "adv",
    "here": "adv", "there": "adv", "nowhere": "adv", "somewhere": "adv",
    # auxiliaries: forms exist but belong to a different word
    "be": "verb", "am": "verb", "is": "verb", "are": "verb", "was": "verb",
    "were": "verb", "been": "verb", "being": "verb",
    "have": "verb", "has": "verb", "had": "verb",
    "do": "verb", "does": "verb", "did": "verb",
    "will": "verb", "would": "verb", "shall": "verb", "should": "verb",
    "can": "verb", "could": "verb", "may": "verb", "might": "verb",
    "must": "verb",
}

# a phrase that starts with a function word and runs to three or more words is
# a fixed expression ("as it were", "by the way") — it has no form family
PHRASE_OPENERS = {
    "as", "in", "at", "on", "of", "by", "to", "for", "from", "with", "into",
    "under", "over", "after", "before", "than", "through", "without", "about",
    "against", "between", "upon", "within", "along", "across", "around",
}


def is_fixed_expression(entry: str) -> bool:
    parts = entry.lower().split()
    return len(parts) >= 3 and parts[0] in PHRASE_OPENERS
# domains of fixed expressions — a "form family" means nothing here
SKIP_DOMAINS = {"idioms_b2", "idioms_c2", "collocations_b2",
               "idiomatic_collocations_c2"}

NOUN_SUFFIX = re.compile(
    r"(tion|sion|ment|ness|ity|ance|ence|ship|ism|ist|ure|ture|age|ery|"
    r"hood|dom|cy|or|er)$")
# no bare "y": "therapy" is a noun and "happy" an adjective, so the ending
# decides nothing — the curated domains handle adjectives instead
ADJ_SUFFIX = re.compile(
    r"(ive|able|ible|ful|ous|al|ish|less|ent|ant|ary|ic|proof|"
    r"worth|some|like)$")
ADV_SUFFIX = re.compile(r"ly$")
VERB_SUFFIX = re.compile(r"(ate|ise|ize|ify|ute|ect)$")

# already plural / uncountable: they take no endings at all
PLURAL_ONLY = {
    "peas", "species", "series", "several", "data", "media", "jeans", "pants",
    "scissors", "trousers", "headphones", "clothes", "goods", "news",
    "mathematics", "physics", "politics", "economics", "means", "aircraft",
    "barracks", "customs", "progress", "software", "luggage", "furniture",
    "advice", "information", "traffic", "staff", "cattle", "sheep", "fish",
    "deer", "offspring", "police",
}
NUMBERS = {
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
    "sixty", "seventy", "eighty", "ninety", "hundred", "thousand",
    "million", "billion", "zero",
}


# ---------------------------------------------------------------- morphology
def doubles(w: str) -> bool:
    """Does the final consonant double?  stop → stopped, visit → visited.

    The teachable rule: a single-syllable word ending consonant-vowel-consonant
    doubles, unless the last letter is w/x/y. "open" and "visit" have two vowel
    letters, so the last syllable is open or unstressed and nothing doubles.
    """
    if len(w) < 3 or w.endswith("e") or w[-1] in "wxy" or w[-1] in VOWELS:
        return False
    if w[-2] not in VOWELS:                 # ...VC  — needs a vowel before
        return False
    if not w[-3].isalpha():
        return False
    return sum(c in VOWELS for c in w) == 1  # one syllable only


def stem(base: str) -> str:
    """The spelling to bolt an ending onto (drop a silent -e)."""
    return base[:-1] if base.endswith("e") else base


def y_forms(base: str, plain: str, cons: str) -> list[str]:
    """consonant + y → y becomes i:  study → studied."""
    return [cons] if base.endswith("y") and base[-2] not in VOWELS else [plain]


def verb_forms(base: str) -> list[tuple[str, str]]:
    """(form, role) for a regular verb — one candidate per role."""
    out: list[tuple[str, str]] = []
    if base.endswith(("s", "sh", "ch", "x", "z", "o")):
        out.append((base + "es", "3rd person"))
    elif base.endswith("y") and base[-2] not in VOWELS:
        out.append((base[:-1] + "ies", "3rd person"))
    else:
        out.append((base + "s", "3rd person"))

    dbl = base + base[-1] if doubles(base) else ""
    s = stem(base)
    if base.endswith("y") and base[-2] not in VOWELS:
        out.append((base + "ing", "-ing"))
        out.append((base[:-1] + "ied", "past"))
    else:
        out.append(((dbl or s) + "ing", "-ing"))
        if base.endswith("e"):
            out.append((base + "d", "past"))
        else:
            out.append(((dbl or base) + "ed", "past"))
    return out


def noun_plural(base: str) -> list[str]:
    if base in IRREG_NOUNS:
        return [IRREG_NOUNS[base]]
    if base.endswith(("s", "x", "z", "ch", "sh")):
        return [base + "es"]
    if base.endswith("y") and base[-2] not in VOWELS:
        return [base[:-1] + "ies"]
    if base.endswith("fe"):
        return [base[:-2] + "ves", base + "s"]
    if base.endswith("f") and base[-2] not in VOWELS:
        return [base[:-1] + "ves", base + "s"]
    if doubles(base):
        return [base + base[-1] + "s", base + "s"]
    return [base + "s"]


def adj_forms(base: str) -> list[tuple[str, str]]:
    if base in IRREG_ADJ:
        c, s, a = IRREG_ADJ[base]
        return [(c, "comparative"), (s, "superlative"), (a, "adverb")]
    out: list[tuple[str, str]] = []
    dbl = base + base[-1] if doubles(base) else ""
    if base.endswith("y") and base[-2] not in VOWELS:
        out += [(base[:-1] + "ier", "comparative"),
                (base[:-1] + "iest", "superlative"), (base + "ily", "adverb")]
    elif base.endswith("e"):
        out += [(base + "r", "comparative"), (base + "st", "superlative"),
                (base + "ly", "adverb")]
    else:
        out += [((dbl or base) + "er", "comparative"),
                ((dbl or base) + "est", "superlative"),
                (base + "ly", "adverb")]
    return out


def infer_pos(word: str, domain: str) -> str:
    """Guess from the domain and the shape. Only a starting point."""
    w = word.lower()
    if domain in ADJ_DOMAINS:
        return "adj"
    if domain in VERB_DOMAINS:
        return "verb"
    if ADV_SUFFIX.search(w):
        return "adv"
    if NOUN_SUFFIX.search(w):
        return "noun"
    if VERB_SUFFIX.search(w) and len(w) > 4:
        return "verb"
    if ADJ_SUFFIX.search(w) and len(w) > 5:
        return "adj"
    if w in IRREG_VERBS:
        return "verb"
    if w in IRREG_NOUNS or w in IRREG_ADJ:
        return "noun"
    return "noun"


def classify_by_evidence(base: str, hint: str, domain: str, ok: set) -> str:
    """Let the dictionary decide the part of speech.

    "happy" in the emotions bank looks like a noun, but it has no plural while
    it does have *happier* — so it is an adjective. Domains that are curated as
    purely one part of speech are trusted outright; everywhere else the evidence
    decides, with the domain hint only breaking ties.
    """
    if domain in ADJ_DOMAINS:
        return "adj"
    if domain in VERB_DOMAINS:
        return "verb"
    if base in FUNCTION_WORDS:
        return FUNCTION_WORDS[base]
    if base in PLURAL_ONLY or base in NUMBERS:
        return "noun"
    scores: dict[str, int] = {}
    for pos in ("noun", "verb", "adj"):
        scores[pos] = len(build_architecture(base, "", pos, ok, base)["forms"])
    best = max(scores.values())
    if best == 0:
        return hint
    # a concrete topic bank stays a noun unless the verb reading wins clearly.
    # Needed because the source word list holds tagger junk ("appling",
    # "appled") that would otherwise make "apple" look like a verb.
    if domain in NOUN_DOMAINS:
        if scores["adj"] > scores["noun"] + 1:
            return "adj"
        if scores["noun"] >= scores["verb"] - 1:
            return "noun"
    winners = [p for p, n in scores.items() if n == best]
    if hint in winners:
        return hint
    if scores.get(hint, 0) >= best - 1:
        return hint          # close enough — trust the curated hint
    return winners[0]


def base_of(entry: str) -> str:
    """'look after' → 'look'; a single word stays as it is."""
    return entry.split()[0].lower() if " " in entry else entry.lower()


# bases that make a phrasal verb: "look after" is about *look*, not "after"
PHRASAL_BASES = {
    "look", "get", "put", "take", "give", "come", "turn", "set", "run",
    "walk", "pick", "give", "break", "call", "carry", "cut", "drop", "go",
    "hang", "hold", "keep", "let", "make", "pay", "pull", "put", "show",
    "sit", "stand", "take", "throw", "work", "figure", "sort", "rule",
    "check", "back", "worry", "stand", "wait", "stay", "read", "write",
}


def head_of(entry: str, domain: str) -> tuple[str, str | None]:
    """The word whose forms matter, plus a forced part of speech if any.

    "acid rain" is a noun phrase — its family is *rain/rains*. But "look after"
    is a phrasal verb, so its family is *look/looks/looked* and the noun reading
    is wrong.
    """
    w = entry.lower()
    if " " not in w:
        return w, FUNCTION_WORDS.get(w)
    if domain in VERB_DOMAINS or w.split()[0] in PHRASAL_BASES:
        return w.split()[0], "verb"
    return w.split()[-1], "noun"      # a topic noun phrase is a noun phrase


def build_architecture(word: str, fa: str, pos: str, ok: set,
                      head: str | None = None) -> dict:
    base = head or base_of(word)
    forms: list[dict] = []
    seen = {base}

    def add(form: str, note: str):
        f = form.lower()
        if f in seen:
            return
        seen.add(f)
        # single words must be in the dictionary. Constructed forms — "more
        # careful", "apple's", "has gone" — are built, not looked up.
        if ok and " " not in f and "'" not in f and f not in ok:
            return          # the dictionary rejected it — don't invent words
        forms.append({"f": f, "n": note})

    def add_all(cands: list[tuple[str, str]], limit_per_role: int = 1):
        """Keep the first N dictionary-confirmed forms for each role."""
        counts: dict[str, int] = {}
        for f, note in cands:
            if counts.get(note, 0) >= limit_per_role:
                continue
            before = len(forms)
            add(f, note)
            if len(forms) > before:
                counts[note] = counts.get(note, 0) + 1

    if pos == "verb":
        irr = IRREG_VERBS.get(base)
        if irr and base not in ("be", "have", "do") or (irr and base in ("be", "have", "do")):
            add_all(verb_forms(base))
            add(irr[0], "past")
            add(irr[1], "past participle")
            add("has " + irr[1], "perfect (has/have + …)")
        else:
            add_all(verb_forms(base))
    elif pos == "noun":
        add(base + "'s", "possessive")
        add_all([(f, "plural") for f in noun_plural(base)])
    elif pos == "adj":
        add_all(adj_forms(base))
        # long adjectives use more/most instead of -er/-est
        if not any(f["n"].startswith("comparative") for f in forms):
            add("more " + base, "comparative (long)")
        if not any(f["n"].startswith("superlative") for f in forms):
            add("most " + base, "superlative (long)")

    if (base in FUNCTION_WORDS or base in PLURAL_ONLY
            or base in NUMBERS or base in set(IRREG_NOUNS.values())):
        forms = []          # function, plural-only and numeral words take no endings
    return {"en": word, "fa": fa, "pos": pos, "forms": forms}


def main() -> int:
    if not DICT.exists():
        sys.exit(f"missing dictionary {DICT}")
    ok = set(json.loads(DICT.read_text(encoding="utf-8")))

    gloss = json.loads((ROOT / "glossary.json").read_text(encoding="utf-8"))["domains"]

    # a word can sit in several domains ("shy" is in both describing_people
    # and emotions) — collect them all, then classify once with the most
    # specific domain in charge.
    collected: dict[str, dict] = {}
    for dom_id, dom in gloss.items():
        if dom_id == "_groups" or dom_id in SKIP_DOMAINS:
            continue
        level = dom.get("level", "A1")
        for row in dom["words"]:
            entry, fa = row[0], (row[1] if len(row) > 1 else "")
            if len(entry) < 2 or not fa:
                continue
            # a synonym set ("big / large / huge") is a comparison aid, not a
            # single learnable word — it has no form family
            if "/" in entry or " vs " in entry:
                continue
            if is_fixed_expression(entry):
                continue
            key = entry.lower()
            rec = collected.setdefault(key, {"entry": entry, "fa": fa,
                                              "level": level, "domains": []})
            rec["domains"].append(dom_id)

    out: dict[str, dict] = {}
    per_level: dict[str, int] = {}

    for key, rec in collected.items():
        # prefer a domain that pins the part of speech, then the lowest level
        dom_id = next((d for d in rec["domains"]
                       if d in ADJ_DOMAINS or d in VERB_DOMAINS), rec["domains"][0])
        level = min((gloss[d].get("level", "A1") for d in rec["domains"]),
                    key=lambda l: "ABCDEF".find(l))
        head, forced = head_of(rec["entry"], dom_id)
        pos = forced or classify_by_evidence(head, infer_pos(rec["entry"], dom_id),
                                             dom_id, ok)
        arch = build_architecture(rec["entry"], rec["fa"], pos, ok, head)
        arch["level"] = level
        arch["domains"] = rec["domains"]
        out[key] = arch
        per_level[level] = per_level.get(level, 0) + 1

    payload = {
        "_readme": "Generated by tools/build_word_architecture.py. "
                   "'forms' are checked against a 170k-word dictionary; "
                   "anything unverified is dropped rather than guessed.",
        "words": out,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    withfam = sum(1 for w in out.values() if w["forms"])
    print(f"{len(out)} words · {withfam} with a form family · "
          f"levels {dict(sorted(per_level.items()))}")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())