#!/usr/bin/env python3
"""Fluentify — a bilingual (English/Persian) chatbot with preloaded memory.

Memory model inspired by:
  * gunthercox/chatterbot-corpus   — daily conversation phrases (English)
  * Microsoft PersonalityChat      — small-talk scenario set
  * Mahdi-Razaghi/tajan            — bilingual (FA/EN) intent structure
  * Persian-Caesar/chatbot         — Persian daily-talk phrasing
"""

import json
import math
import os
import random
import re
import sys
from datetime import date, datetime
from pathlib import Path

MEMORY_FILE = Path(__file__).parent / "memory.json"
GLOSSARY_FILE = Path(__file__).parent / "glossary.json"
PHRASES_FILE = Path(__file__).parent / "phrases.json"
GRAMMAR_FILE = Path(__file__).parent / "grammar.json"
JOKES_FILE = Path(__file__).parent / "jokes.json"
LISTENING_FILE = Path(__file__).parent / "listening.json"
DISTINCTIONS_FILE = Path(__file__).parent / "distinctions.json"
IDIOMS_FILE = Path(__file__).parent / "idioms.json"
# The slang and idiom bank (tools/build_slang.py): modern slang from SlangLane,
# Wiktionary idioms from IdiomX, Persian idioms from the Idiom_Translation
# parallel corpus, and the Persian glosses none of them carry.
SLANG_FILE = Path(__file__).parent / "slang.json"

# Persian is typed two ways: with the Arabic yeh and kaf, and with the Persian
# ones (and often with a zero-width non-joiner where a space belongs). Dadma
# Tools' normaliser settles on the Persian forms; so does this, and for the
# same reason - "دست خود را جايي بند كردن" has to match the idiom as stored.
FA_FOLD = str.maketrans({"ي": "ی", "ك": "ک", "ۀ": "ه", "أ": "ا",
                         "إ": "ا", "ؤ": "و", "\u200c": " ", "\u200f": " ",
                         "\u200e": " ", "\u0640": ""})

# Register and category labels, translated once here: a reply that says
# "informal" to a Persian learner has explained the slang in the wrong
# language.
SLANG_REG_FA = {"informal": "عامیانه", "slang": "خودمانی", "formal": "رسمی",
                "neutral": "خنثی", "idiom": "اصطلاح", "archaic": "کهن"}
SLANG_CAT_FA = {"internet": "اینترنت", "social": "روابط اجتماعی",
                "communication": "ارتباط", "workplace": "محیط کار",
                "texting": "چت و پیامک", "gaming": "بازی",
                "regional": "انگلیسی محلی", "fandom": "فندام",
                "digital": "دنیای دیجیتال", "aesthetics": "سبک",
                "pets": "حیوانات"}
REGISTER_FILE = Path(__file__).parent / "register.json"
CORRECTIONS_FILE = Path(__file__).parent / "corrections.json"
PHONETICS_FILE = Path(__file__).parent / "phonetics.json"
DAILY_FILE = Path(__file__).parent / "daily.json"
# The dictionary is a directory of shards, not a file: see tools/build_lexicon.py
LEXICON_DIR = Path(__file__).parent / "lexicon"

# The daily rotation counts *calendar* days from one fixed date, so a given
# local date always yields the same three items - in this engine, in the APK
# engine, and after any restart. Calendar dates rather than elapsed hours
# because a 23- or 25-hour day across a daylight-saving change still counts as
# one day, which is what "a new day" means to the person holding the phone.
DAILY_EPOCH = date(2024, 1, 1)

# One salt per category, so the word, the expression and the conversation do
# not march through their catalogues in step with each other.
DAILY_SALTS = {"words": 3, "expressions": 11, "conversations": 5}


def daily_day_number(date_key: str) -> int:
    """How many days after the epoch a YYYY-MM-DD local date is."""
    return (date.fromisoformat(date_key) - DAILY_EPOCH).days


def daily_step(size: int, salt: int) -> int:
    """A step that is coprime with the catalogue size.

    With a coprime step, `day * step % size` walks every entry before it comes
    back to one it has used, whatever the size is - so nothing repeats inside a
    full rotation and the two engines cannot diverge on how they walk.
    """
    if size <= 1:
        return 1
    step = 1 + (salt % 9)
    while math.gcd(step, size) != 1:
        step += 1
        if step > size + 1:
            return 1
    return step


def daily_index(day: int, size: int, salt: int) -> int:
    """The catalogue slot for a day, or 0 when there is nothing to pick."""
    if size <= 0:
        return 0
    return (day * daily_step(size, salt) + salt) % size

PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
PERSIAN_TO_ASCII = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")

HELP_TEXT = {
    "en": (
        "I can do all of this:\n"
        "- Chat about daily things (how are you, I'm bored, tell me a joke...)\n"
        "- English alphabet  → ask: 'english alphabet'\n"
        "- Persian alphabet  → ask: 'persian alphabet' or 'الفبای فارسی'\n"
        "- Letter lookup      → ask: 'what letter is A' or 'حرف ب'\n"
        "- Translate words    → ask: 'translate apple' or 'سیب به انگلیسی'\n"
        "- Define words       → ask: 'what does خوشحال mean' or 'define شیر'\n"
        "- Vocabulary domains → ask: 'what are the colors' or 'حیوانات'\n"
        "- Grammar lessons    → ask: 'grammar', then 'simple present' or 'حال ساده'\n"
        "- Everyday sentences → ask: 'travel sentences' or 'جملات سفر'\n"
        "- Grammar practice   → ask: 'simple present exercises' or 'تمرین حال ساده'\n"
        "- Pronunciation      → ask: 'how do you pronounce hospital'\n"
        "- Register           → ask: 'how do I say sorry formally'\n"
        "- Listening practice → ask: 'listen A1' or 'گوش دادن A1'\n"
        "- Sounds guide       → ask: 'phonetics' or 'تلفظ'\n"
        "- Current time/date  → ask: 'what time is it' or 'ساعت چنده'\n"
        "- Remember your name → say: 'my name is ...' or 'اسم من ... است'\n"
        "Type 'bye' to exit."
    ),
    "fa": (
        "من این کارها رو بلدم:\n"
        "- مکالمه روزمره (حال تو چطوره، جوک بگو، حوصله‌ام سر رفته...)\n"
        "- الفبای انگلیسی  → بپرس: 'english alphabet'\n"
        "- الفبای فارسی    → بپرس: 'الفبای فارسی'\n"
        "- جست‌وجوی حرف     → بپرس: 'حرف ب' یا 'what letter is A'\n"
        "- ترجمه کلمات     → بپرس: 'سیب به انگلیسی' یا 'translate apple'\n"
        "- معنی کلمات      → بپرس: 'معنی خوشحال چیه' یا 'what does شیر mean'\n"
        "- دامنه‌های واژگان → بپرس: 'رنگها' یا 'what are the animals'\n"
        "- درس گرامر        → بپرس: 'گرامر' بعد 'حال ساده' یا 'simple present'\n"
        "- جملات کاربردی    → بپرس: 'جملات سفر' یا 'daily routine'\n"
        "- تمرین گرامر      → بپرس: 'تمرین حال ساده' یا 'simple present exercises'\n"
        "- تلفظ             → بپرس: 'تلفظ hospital' یا 'how do you pronounce hospital'\n"
        "- سطح رسمیت        → بپرس: 'چطور بگم ببخشید دیر کردم رسمی'\n"
        "- تمرین شنیدن      → بپرس: 'گوش دادن A1' یا 'listen A1'\n"
        "- راهنمای صداها    → بپرس: 'تلفظ' یا 'phonetics'\n"
        "- ساعت و تاریخ     → بپرس: 'ساعت چنده' یا 'what time is it'\n"
        "- یادآوری اسمت    → بگو: 'اسم من ... است' یا 'my name is ...'\n"
        "برای خروج 'bye' یا 'خروج' رو بنویس."
    ),
}


def detect_lang(text: str) -> str:
    """Return 'fa' if the text contains Persian characters, else 'en'."""
    return "fa" if re.search(r"[\u0600-\u06FF]", text) else "en"


def to_persian_digits(n) -> str:
    return str(n).translate(PERSIAN_DIGITS)


# ---------------------------------------------------------------- numbers
UNITS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19,
}
TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
    "seventy": 70, "eighty": 80, "ninety": 90,
}
SCALES = {
    "hundred": 100, "thousand": 1_000, "million": 1_000_000,
    "billion": 1_000_000_000,
}
ENGLISH_ONES = ["zero", "one", "two", "three", "four", "five", "six",
                "seven", "eight", "nine", "ten", "eleven", "twelve",
                "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
                "eighteen", "nineteen"]
ENGLISH_TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty",
                "seventy", "eighty", "ninety"]


def to_english_digits(n: int) -> str:
    """123 → 'one hundred and twenty-three'."""
    if n < 20:
        return ENGLISH_ONES[n]
    if n < 100:
        head, tail = divmod(n, 10)
        return ENGLISH_TENS[head] + (f"-{ENGLISH_ONES[tail]}" if tail else "")
    if n < 1000:
        head, tail = divmod(n, 100)
        rest = f" and {to_english_digits(tail)}" if tail else ""
        return f"{ENGLISH_ONES[head]} hundred{rest}"
    for scale in (10**9, 10**6, 1000):
        if n >= scale:
            head, tail = divmod(n, scale)
            rest = f" {to_english_digits(tail)}" if tail else ""
            name = {10**9: "billion", 10**6: "million", 1000: "thousand"}[scale]
            return f"{to_english_digits(head)} {name}{rest}"
    return str(n)


PAST_PARTICIPLES = {
    "went": "gone", "gone": "gone", "ate": "eaten", "saw": "seen",
    "made": "made", "took": "taken", "said": "said", "came": "come",
    "did": "done", "got": "got", "found": "found", "knew": "known",
    "thought": "thought", "bought": "bought", "gave": "given",
    "wrote": "written", "spoke": "spoken", "drove": "driven",
    "broke": "broken", "felt": "felt", "kept": "kept", "left": "left",
    "met": "met", "paid": "paid", "put": "put", "set": "set",
    "sat": "sat", "stood": "stood", "understood": "understood",
    "worn": "worn", "run": "run", "ran": "run", "written": "written",
    "chosen": "chosen", "eaten": "eaten", "seen": "seen", "hidden": "hidden",
    "built": "built", "sent": "sent", "spent": "spent", "lost": "lost",
    "won": "won", "taught": "taught", "caught": "caught", "sought": "sought",
    "brought": "brought", "sang": "sung", "drank": "drunk", "swam": "swum",
    "began": "begun", "rose": "risen", "fell": "fallen", "felt": "felt",
    "led": "led", "fed": "fed", "flew": "flown", "threw": "thrown",
    "grew": "grown", "knew": "known", "blew": "blown", "drew": "drawn",
    "wore": "worn", "tore": "torn", "shook": "shook", "stole": "stolen",
}


BASE_FORMS = {
    "went": "go", "came": "come", "saw": "see", "ate": "eat", "made": "make",
    "took": "take", "said": "say", "got": "get", "gave": "give",
    "knew": "know", "thought": "think", "bought": "buy", "wrote": "write",
    "spoke": "speak", "drove": "drive", "broke": "break", "felt": "feel",
    "kept": "keep", "left": "leave", "met": "meet", "had": "have",
    "did": "do", "was": "were", "gone": "go", "eaten": "eat", "seen": "see",
    "taken": "take", "given": "give", "known": "know", "written": "write",
    "spoken": "speak", "driven": "drive", "broken": "break",
    "informations": "information", "knowledges": "knowledge",
    "equipments": "equipment", "furnitures": "furniture",
    "advices": "advice", "softwares": "software",
    "researches": "research", "homeworks": "homework",
}

IRREGULAR_PLURALS = set(BASE_FORMS) | {"peoples", "childrens", "informations"}

VOWEL_SOUND_EXCEPTIONS = ("s", "x", "z", "ch", "sh")


def singular(word: str) -> str:
    """A crude but safe singulariser for the handful of nouns we police."""
    w = word.lower()
    if w in BASE_FORMS:
        return BASE_FORMS[w]
    if w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"
    if w.endswith("sses") or w.endswith("shes") or w.endswith("ches"):
        return w[:-2]
    if w.endswith("s") and not w.endswith("ss"):
        return w[:-1]
    return word


def third_person(verb: str) -> str:
    """'go' → 'goes', 'watch' → 'watches', 'study' → 'studies'."""
    v = verb.lower()
    if v.endswith(VOWEL_SOUND_EXCEPTIONS) or v.endswith("o"):
        return v + "es"
    if v.endswith("y") and len(v) > 1 and v[-2] not in "aeiou":
        return v[:-1] + "ies"
    return v + "s"


# ------------------------------------------------------------------ stress
VOWELS = set("aeiouy")

# Endings that pull the stress onto the syllable before them.
STRESS_BEFORE = ("ical", "tion", "sion", "ture", "sure", "ity", "ial",
                 "ious", "eous", "ian", "uous", "ify", "ise", "ize", "ate",
                 "ogy", "ology", "graphy", "meter", "itude", "ative")
# Prefixes English normally leaves unstressed.
UNSTRESSED_PREFIXES = ("be", "con", "com", "de", "dis", "en", "em", "ex",
                        "im", "in", "mis", "per", "pre", "pro", "re", "sub",
                        "sur", "un", "up", "ob", "for", "fore", "with")

VOICELESS = set("ptkfvszxcgq")          # no voice on them
VOICED = set("bdjlmnrwygv")             # voice on them


def syllables(word: str) -> list[str]:
    """Split an English word into rough syllables ('hospital' → 3 parts).

    Good enough to place a stress mark, which is what a learner needs; it is
    not a pronunciation dictionary.
    """
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return []
    if len(w) <= 2:
        return [w]
    groups = [m for m in re.finditer(r"[aeiouy]+", w)]
    if not groups:
        return [w]
    # a final "e" after a consonant is silent and does not start a syllable
    ends = list(groups)
    if (w.endswith("e") and not w.endswith(("le", "ee", "ye"))
            and not w.endswith("e" + "e")):
        if ends and ends[-1].group(0) == "e" and ends[-1].start() == len(w) - 1:
            ends.pop()
    if not ends:
        return [w]
    parts, prev = [], 0
    for i, g in enumerate(ends):
        # the last syllable runs to the end of the word, so it keeps any
        # trailing consonants ('hospital' -> ho | spi | tal)
        end = g.end() if i < len(ends) - 1 else len(w)
        parts.append(w[prev:end])
        prev = g.end()
    return [p for p in parts if p]


def stress_index(word: str) -> int:
    """Which syllable carries the main beat."""
    parts = syllables(word)
    n = len(parts)
    if n <= 1:
        return 0
    w = word.lower()
    idx = 0
    for suffix in STRESS_BEFORE:
        if w.endswith(suffix) and n >= 2:
            idx = n - 2
            break
    else:
        head = parts[0]
        for p in UNSTRESSED_PREFIXES:
            if head.startswith(p) and len(head) >= len(p) and len(head) > 1:
                idx = 1
                break
        if w.endswith(("ee", "eer", "eese", "ette")):
            idx = 0
    return min(idx, n - 1)


def mark_stress(word: str) -> str:
    """'hospital' → 'HOS-pi-tal' — the cap shows where the beat falls."""
    parts = syllables(word)
    if not parts:
        return word
    i = stress_index(word)
    out = []
    for k, p in enumerate(parts):
        if k == i:
            out.append(p.upper())
        elif k == 0:
            out.append(p.capitalize())
        else:
            out.append(p)
    return "-".join(out)


def first_sound_note(word: str) -> str:
    """A one-line hint about the very first sound, in the learner's terms."""
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return ""
    ch = w[0]
    if ch in VOICELESS:
        return (f"it starts with /{ch}/ — no voice on your throat, "
                "just airflow")
    if ch in VOICED:
        return f"it starts with /{ch}/ — put your voice on it"
    if ch in "aeiou":
        return f"it starts with the vowel /{ch}/ — open your mouth on it"
    if ch == "y":
        return "it starts with /y/ — your tongue is already in place"
    return f"it starts with /{ch}/"


# Past-simple forms that are NOT also participles. "I have seen" is right, so
# the present-perfect rule must only fire on these - on "seen" or "gone" the
# learner already used the participle and there is nothing to correct.
PAST_SIMPLE_ONLY = {
    "went", "ate", "saw", "came", "did", "got", "found", "knew", "thought",
    "bought", "gave", "wrote", "spoke", "drove", "broke", "left", "met",
    "ran", "wore", "tore", "stole", "sang", "drank", "swam", "began", "rose",
    "fell", "fed", "flew", "threw", "grew", "blew", "drew", "shook", "hid",
    "bit", "hung", "rode", "woke", "froze", "stole", "struck", "hid",
    "brought", "caught", "taught", "sought", "thought", "understood",
}


def past_participle(verb: str) -> str:
    """'went' → 'gone'. Regular verbs just add -ed; we leave those alone."""
    v = verb.lower().strip("'")
    if v in PAST_PARTICIPLES:
        return PAST_PARTICIPLES[v]
    if v.endswith("e"):
        return v + "d"
    if len(v) > 2 and v[-1] == "y" and v[-2] not in "aeiou":
        return v[:-1] + "ied"
    return v + "ed"


def number_from_words(phrase: str) -> int | None:
    """'twenty one' → 21. Returns None if it isn't a plain number phrase."""
    words = [w for w in re.split(r"[\s-]+", phrase.strip().lower()) if w]
    if not words or len(words) > 8:
        return None
    if words == ["a", "hundred"]:
        return 100
    total = 0
    current = 0
    seen = False
    for w in words:
        if w == "and":
            continue
        if w in UNITS:
            current += UNITS[w]
            seen = True
        elif w in TENS:
            current += TENS[w]
            seen = True
        elif w in SCALES:
            scale = SCALES[w]
            current = (current or 1) * scale
            total += current
            current = 0
            seen = True
        else:
            return None
    return total + current if seen else None


def normalize_fa(text: str) -> str:
    """Normalize Persian text: unify ي/ك, drop ZWNJ, spaces, diacritics, digits."""
    text = text.translate(PERSIAN_TO_ASCII)
    text = text.replace("\u200c", "").replace("ي", "ی").replace("ك", "ک")
    text = re.sub(r"[\u064b-\u0652\u0670]", "", text)  # harakat
    text = re.sub(r"\s+", "", text)
    return text.strip()


def normalize_en(text: str) -> str:
    """Lowercase and strip punctuation for English lookups."""
    return re.sub(r"[^\w\s']", "", text.lower()).strip()


# Writing variations that carry no meaning: ZWNJ ("می‌خواهم" vs "میخواهم"),
# the Arabic yeh/kaf and heh forms, and the bidi marks a phone keyboard
# sometimes pastes in. Learners type all of them; intent keywords are written
# in whichever form came to hand.
FA_FOLD_TABLE = str.maketrans({
    "ي": "ی", "ك": "ک", "ۀ": "ه", "ة": "ه",
    "\u200c": "", "\u200d": "", "\u200e": "", "\u200f": "",
})


def fold_fa(text: str) -> str:
    """Fold Persian writing variations so both sides compare equal.

    Applied to the message and to every keyword, so it can only ever add
    matches: a keyword that matched before still matches, and
    "از حرف زدن می‌ترسم" now also answers "از حرف زدن میترسم".
    """
    return text.translate(FA_FOLD_TABLE)


CORE_PHRASES = {
    "thank you": ("Thank you.", "ممنونم."),
    "thanks": ("Thanks!", "مرسی!"),
    "hello": ("Hello!", "سلام!"),
    "hi": ("Hi!", "سلام!"),
    "goodbye": ("Goodbye!", "خداحافظ!"),
    "bye": ("Bye!", "خداحافظ!"),
    "excuse me": ("Excuse me.", "ببخشید."),
    "sorry": ("Sorry.", "ببخشید."),
    "please": ("Please.", "لطفاً."),
    "yes": ("Yes.", "بله."),
    "no": ("No.", "نه."),
    "of course": ("Of course.", "البته."),
    "you are welcome": ("You're welcome.", "خواهش می‌کنم."),
    "how are you": ("How are you?", "حالت چطور است؟"),
    "how are you today": ("How are you today?", "امروز حالت چطور است؟"),
    "see you": ("See you later.", "بدرود."),
    "good luck": ("Good luck!", "موفق باشی!"),
    "welcome": ("Welcome!", "خوش آمدی!"),
    "i am sorry": ("I'm sorry.", "متأسفم."),
    "nice to meet you": ("Nice to meet you.", "خوشحالم که آشنا شدیم."),
    "no problem": ("No problem.", "اشکالی ندارد."),
    "good morning": ("Good morning.", "صبح بخیر."),
    "good night": ("Good night.", "شب بخیر."),
    "how do you do": ("How do you do?", "حالت چطور است؟"),
    "what do you do": ("What do you do?", "چه کار می‌کنی؟"),
    "long time no see": ("Long time no see!", "دیر کردی!"),
    "see you tomorrow": ("See you tomorrow.", "فردا می‌بینمت."),
    "i am hungry": ("I'm hungry.", "گرسنه‌ام."),
    "i am thirsty": ("I'm thirsty.", "تشنه‌ام."),
    "i am tired": ("I'm tired.", "خسته‌ام."),
    "how old are you": ("How old are you?", "چند سالته؟"),
    "what time is it": ("What time is it?", "ساعت چند است؟"),
}


def strip_article(word: str) -> str:
    """'the last straw' and 'last straw' name the same idiom."""
    return re.sub(r"^(?:a|an|the)\s+", "", word.strip(), flags=re.IGNORECASE)


def normalize_word(text: str) -> str:
    """Combined normalization used for glossary lookups (handles mixed input)."""
    text = normalize_fa(text)
    return normalize_en(text)


def edit_distance(a: str, b: str) -> int:
    """Levenshtein distance, shared with the JavaScript engine."""
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(
                previous[j] + 1,
                current[j - 1] + 1,
                previous[j - 1] + (ca != cb),
            ))
        previous = current
    return previous[-1]


def is_subsequence(short: str, long: str) -> bool:
    """Is `short` a message `long` with letters missing?

    "resilent" is one edit from both "resident" (a substitution) and
    "resilient" (a dropped letter), and distance alone cannot choose. A dropped
    letter is the commoner typo of the two, so the candidate that keeps every
    letter the learner typed, in order, is offered first.
    """
    it = iter(long)
    return all(ch in it for ch in short)


REGISTER_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "in", "on", "at", "to",
    "for", "of", "with", "from", "by", "as", "is", "am", "are", "was",
    "were", "be", "been", "being", "do", "does", "did", "have", "has",
    "had", "i", "me", "my", "we", "us", "our", "you", "your", "he",
    "him", "his", "she", "her", "it", "its", "they", "them", "their",
    "this", "that", "these", "those", "please", "can", "could", "would",
    "should", "will", "just", "very", "really", "so", "not", "no",
}


# --------------------------------------------------------------------------
# Dictionary — lexical knowledge, sharded (see tools/build_lexicon.py)
# --------------------------------------------------------------------------
# The dictionary is not a new surface. It is another source of knowledge behind
# the same chat: a lookup the glossary cannot answer now falls through to it,
# and four things the glossary never could answer (synonyms, opposites, forms,
# one word's meaning in a sentence) are read from it directly.
LEX_POS_FA = {"noun": "اسم", "verb": "فعل", "adjective": "صفت",
              "adverb": "قید"}

# The source labels every inflected form it stores, so a question about one
# form is answered by lookup rather than by guessing from the ending.
LEX_FORM_LABEL = {"past": "past", "past_participle": "past participle",
                  "3rd_present": "3rd person", "gerund": "-ing form",
                  "plural": "plural", "comparative": "comparative",
                  "superlative": "superlative",
                  "non_3rd_present": "present"}


def lex_shard_names(word: str) -> list[str]:
    """Which shard files a word could live in, most specific first.

    Two letters normally, three for the crowded buckets the build splits, so
    the reader does not have to know which choice the build made.
    """
    w = re.sub(r"[^a-z]", "", (word or "").lower())
    if len(w) >= 3:
        return [w[:3], w[:2]]
    if len(w) == 2:
        return [w]
    if len(w) == 1:
        return [w + "_"]
    return []


# "what does X mean" is a request for a *definition*; the glossary holds a
# translation, which is a different answer. The dictionary is asked first for
# these, and the glossary keeps every other lookup exactly as it was.
DEFINITION_ASK_RE = re.compile(
    r"\b(?:define|definition of|meaning of|what does|what's the meaning|"
    r"what is the meaning)\b", re.IGNORECASE)

LEX_SYNONYMS_RE = re.compile(
    r"\b(?:synonyms?|similar words?|other words? for|another word for|"
    r"words? like)\b", re.IGNORECASE)
LEX_SYNONYMS_FA = ("مترادف", "هم معنی", "هم‌معنی", "هممعنی")
LEX_ANTONYMS_RE = re.compile(
    r"\b(?:antonyms?|opposite of|opposite to|opposites|contrary of)\b",
    re.IGNORECASE)
LEX_ANTONYMS_FA = ("متضاد", "مخالف", "برعکس")
LEX_FORMS_RE = re.compile(
    r"\b(?:forms? of|inflections? of|verb forms? of)\b", re.IGNORECASE)
# Ordered: "past participle of" must be read before "past tense of" can claim
# the word "past".
LEX_FORM_ASKS = [
    (re.compile(r"\bpast participle of\b", re.IGNORECASE), "past_participle"),
    (re.compile(r"\bpast (?:simple|tense|form) of\b", re.IGNORECASE), "past"),
    (re.compile(r"\b(?:plural|plural form) of\b", re.IGNORECASE), "plural"),
    (re.compile(r"\b(?:ing form|-ing form|gerund) of\b", re.IGNORECASE), "gerund"),
    (re.compile(r"\bcomparative of\b", re.IGNORECASE), "comparative"),
    (re.compile(r"\bsuperlative of\b", re.IGNORECASE), "superlative"),
    (re.compile(r"\bthird person(?: singular)?(?: form)? of\b", re.IGNORECASE),
     "3rd_present"),
]
# "what does bank mean in river bank" - the sentence is the whole point of the
# question, so it is kept and used to choose a sense.
LEX_CONTEXT_RE = re.compile(
    r"\b(?:in|inside|within)\s+(?:the\s+|a\s+|an\s+)?(.{2,50})$", re.IGNORECASE)

LEX_SYN_PATTERNS = [
    r"synonyms? (?:of|for)\s+(?P<t>.+)",
    r"(?:similar|other) words? (?:for|to)\s+(?P<t>.+)",
    r"another word for\s+(?P<t>.+)",
    r"words? like\s+(?P<t>.+)",
    r"(?:مترادف|هم‌?معنی)\s*(?:های|ها|ی|کلمه|واژه)?\s*(?P<t>.+)",
]
LEX_ANT_PATTERNS = [
    r"antonyms? (?:of|for)\s+(?P<t>.+)",
    r"(?:opposite|contrary) (?:of|to)\s+(?P<t>.+)",
    r"(?:متضاد|مخالف|برعکس)\s*(?:های|ها|ی|کلمه|واژه)?\s*(?P<t>.+)",
]
LEX_EXAMPLE_PATTERNS = [
    r"examples? (?:with|of|for|using)\s+(?P<t>.+)",
    r"sentences? (?:with|using)\s+(?P<t>.+)",
    r"(?:use|using) (?P<t>.+?) in (?:a|the|one) sentence",
    r"\u0686\u0646\u062f \u0645\u062b\u0627\u0644 \u0628\u0627\s+(?P<t>.+)",
    r"\u0645\u062b\u0627\u0644(?:\u06cc|\u0647\u0627\u06cc)? \u0628\u0627\s+(?P<t>.+)",
]

LEX_FORM_PATTERNS = {
    "past": [r"past (?:simple|tense|form) of\s+(?P<t>.+)",
             r"(?:ماضی|گذشته)\s*(?P<t>.+)"],
    "past_participle": [r"past participle of\s+(?P<t>.+)",
                        r"اسم مفعول\s*(?P<t>.+)"],
    "plural": [r"plural of\s+(?P<t>.+)", r"جمع\s*(?P<t>.+)"],
    "gerund": [r"(?:ing form|-ing form|gerund) of\s+(?P<t>.+)"],
    "comparative": [r"comparative of\s+(?P<t>.+)"],
    "superlative": [r"superlative of\s+(?P<t>.+)"],
    "3rd_present": [r"third person(?: singular)?(?: form)? of\s+(?P<t>.+)"],
}
# Trailing Persian question furniture, trimmed off a target over and over:
# «مترادف کلمه beautiful رو بگو» must reduce to "beautiful".
# Words that carry the question rather than the meaning when a sentence is
# used to pick a sense out of the dictionary.
LEX_STOP = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "of", "to",
    "for", "with", "from", "by", "as", "is", "are", "was", "were", "be",
    "been", "being", "it", "its", "this", "that", "these", "those", "i",
    "you", "he", "she", "we", "they", "my", "your", "his", "her", "our",
    "their", "me", "him", "them", "do", "does", "did", "what", "which",
    "mean", "means", "meaning", "word", "sentence", "use", "used", "using",
    "say", "said", "tell", "explain", "please", "can", "could", "would",
    "should", "how", "when", "where", "why", "there", "here", "not",
}

LEX_TARGET_TRIM = re.compile(
    r"\s*(?:رو\s*)?(?:بگو|بگویید|بگین|بگید|چیه|چیست|چی|هست|را|کلمه|واژه|یعنی|چه)\s*$",
    re.UNICODE)


def content_tokens(text: str) -> set[str]:
    """Content words for register matching, with a tiny plural fold."""
    words = re.findall(r"[a-z]+", text.lower())
    out = set()
    for word in words:
        if len(word) <= 2 or word in REGISTER_STOPWORDS:
            continue
        if len(word) > 4 and word.endswith("s"):
            word = word[:-1]
        out.add(word)
    return out


# Stopwords that should never be treated as glossary lookup targets
LOOKUP_STOPWORDS = {
    "it", "this", "that", "is", "are", "mean", "means", "the", "a", "an",
    "what", "which", "word", "translate", "define",
    "این", "اون", "است", "چیه", "چیست", "کلمه", "معنی",
    "اسمت", "نامت", "اسم", "تو", "شما", "من", "خودت",
    # the verb of asking is not a word to translate: "به فارسی بگو" (say it in
    # Persian) is a request about the reply, not a lookup for «بگو»
    "بگو", "بگویم", "بگم", "بگید", "بگین", "بگویید",
}

# A message that names the lookup it wants ("translate X", "معنی X") asks for
# a word, not for a phrase bank that happens to share the word. The English
# side uses a regex; the Persian side is a substring test, because \b is
# ASCII-only in JavaScript and the two engines have to agree.
LOOKUP_ASK_RE = re.compile(
    r"\b(?:translate|define|definition of|meaning of|what does|means)\b")
LOOKUP_ASK_FA = ("معنی", "ترجمه", "به انگلیسی")

# "speak english", "reply in persian", "english please" — a request about the
# language of the answer, not a word to translate.
SWITCH_ASK_RE = re.compile(
    r"^\s*(?:please\s+)?(?:speak|reply|answer|respond|write|talk|continue)\b"
    r"[^.!?]*?\bin\s+(?:english|persian|farsi)\b"
    r"|^\s*(?:english|persian|farsi)\s+please\b",
    re.IGNORECASE)


def is_lookup_ask(text: str, lowered: str) -> bool:
    return bool(LOOKUP_ASK_RE.search(lowered)) or any(w in text for w in LOOKUP_ASK_FA)

# Pattern (lang, regex) lists to extract a target word from lookup requests
EN_LOOKUP_PATTERNS = [
    r"explain (?:the )?(?:word |meaning of )?(?P<t>.+)",
    r"what is the (?:english|persian|farsi) (?:word|translation) for\s+(?P<t>.+)",
    r"how do (?:i|you) say\s+(?P<t>.+?)\s+in\s+(?:english|persian|farsi)",
    r"what does\s+(?P<t>.+?)\s+means?\b",
    r"meaning of\s+(?P<t>.+)",
    r"define\s+(?P<t>.+)",
    r"translate\s+(?P<t>.+?)(?:\s+(?:to|in)\s+(?:english|persian|farsi))?$",
    r"what(?:'s| is| are)\s+(?P<t>.+?)\s+in\s+(english|persian|farsi)\s*[?.!]*$",
    r"(?P<t>.+?)\s+in\s+(english|persian|farsi)\s*[?.!]*$",
]
FA_LOOKUP_PATTERNS = [
    r"معنی\s+(?P<t>.+?)\s*(?:چیه|چیست|هست)",
    r"معنی\s+(?P<t>.+)",
    r"(?P<t>.+?)\s*یعنی\s*چه",
    r"(?:چطوری|چطور|چجوری)\s+(?P<t>.+?)\s*بگم",
    r"(?P<t>.+?)\s*رو\s*(?:بگو|بگویم|بگید|بگین)\s*[؟?.!]*$",
    r"ترجمه\s+(?P<t>.+)",
    r"کلمه\s+(?P<t>.+?)\s*(?:چیه|چیست)",
    r"(?P<t>.+?)\s+به\s+(?:انگلیسی|فارسی)",
    r"به\s+(?:انگلیسی|فارسی)\s+(?P<t>.+)",
    r"(?P<t>.+?)\s*(?:چیه|چیست)$",
]

# Deictic questions such as "what does that mean?" have no lookup target.
# They need a precise clarification, not a joke-shaped answer.
VAGUE_MEANING_EN = re.compile(
    r"^(?:what(?:'s|s| is)?\s+(?:the\s+)?meaning(?:\s+of\s+(?:this|that|it))?"
    r"|what\s+does\s+(?:this|that|it|this\s+word|that\s+word)\s+mean"
    r"|what\s+do\s+you\s+mean(?:\s+by\s+(?:this|that|it))?)\s*[?.!]*$",
    re.IGNORECASE,
)
VAGUE_MEANING_FA = re.compile(
    r"^(?:(?:این|اون|آن)\s*یعنی\s*(?:چی|چه)"
    r"|یعنی\s*(?:چی|چه)"
    r"|معنی\s*(?:این|اون|آن)\s*(?:چیه|چیست|هست)"
    r"|منظورت\s*(?:از\s*(?:این|اون|آن))?\s*(?:چیه|چیست))\s*[؟?.!]*$"
)

# --------------------------------------------------------------------------
# Daily English — the questions that ask for today's three items
# --------------------------------------------------------------------------
# Deliberately narrow. "practice" alone belongs to the grammar session and
# "lesson" alone to the grammar menu; only the phrases below name the daily
# rotation, so none of them can take a request away from the section that
# already owned it.
DAILY_WORD_RE = re.compile(
    r"\b(?:today'?s? word|word of the day"
    r"|(?:today'?s?|the) vocabulary word|daily word)\b")
DAILY_EXPRESSION_RE = re.compile(
    r"\b(?:today'?s? (?:expression|phrase|sentence)"
    r"|(?:expression|phrase|sentence|idiom) of the day|daily (?:expression|phrase))\b")
DAILY_CONVERSATION_RE = re.compile(
    r"\b(?:today'?s? (?:conversation|dialogue)"
    r"|(?:conversation|dialogue) of the day"
    r"|daily (?:conversation|dialogue))\b")
DAILY_ANY_RE = re.compile(
    r"\b(?:daily english|daily lesson|daily practice|english of the day"
    r"|today'?s? (?:lesson|english)|what(?:'s| is) today)\b")
DAILY_WORD_FA = ("لغت امروز", "کلمه امروز", "واژه امروز", "لغت روز",
                 "کلمهٔ امروز", "واژهٔ امروز")
DAILY_EXPRESSION_FA = ("عبارت امروز", "جمله امروز", "اصطلاح امروز", "عبارت روز",
                       "جملهٔ امروز", "عبارت امروز چیه")
DAILY_CONVERSATION_FA = ("مکالمه امروز", "گفتگوی امروز", "مکالمه روز",
                         "دیالوگ امروز", "مکالمهٔ امروز")
DAILY_ANY_FA = ("انگلیسی روزانه", "انگلیسی امروز", "درس امروز", "روزانه چی",
                "امروز چی یاد", "امروز چی بخونم")
PRACTICE_ASK = ("practice", "roleplay", "role play", "drill",
                "تمرین", "باهام", "با من", "نقش بازی")
EXAMPLES_ASK = ("example", "examples", "sentence", "sentence with",
                "مثال", "جمله بساز", "چند جمله")


def same_spoken(spoken: str, expected: str) -> bool:
    """Does what the learner said count as the dialogue's line?

    Exact match is too strict for a spoken drill and substring is too loose, so
    the line passes when either contains the other or when four fifths of the
    expected words are there. Punctuation and case are ignored - nobody says a
    full stop.
    """
    def norm(s: str) -> str:
        s = re.sub(r"[^\w' ]+", " ", s.lower(), flags=re.UNICODE)
        return re.sub(r"\s+", " ", s).strip()

    said, want = norm(spoken), norm(expected)
    if not said or not want:
        return False
    if said == want or want in said:
        return True
    have, need = set(said.split()), set(want.split())
    return len(have & need) / max(1, len(need)) >= 0.8


class ChatBot:
    def __init__(
        self,
        memory_path: Path = MEMORY_FILE,
        glossary_path: Path = GLOSSARY_FILE,
        grammar_path: Path = GRAMMAR_FILE,
        phrases_path: Path = PHRASES_FILE,
        listening_path: Path = LISTENING_FILE,
        distinctions_path: Path = DISTINCTIONS_FILE,
        idioms_path: Path = IDIOMS_FILE,
        slang_path: Path = SLANG_FILE,
        corrections_path: Path = CORRECTIONS_FILE,
        phonetics_path: Path = PHONETICS_FILE,
        register_path: Path = REGISTER_FILE,
        daily_path: Path = DAILY_FILE,
        lexicon_path: Path = LEXICON_DIR,
        today: str | None = None,
    ):
        self.lexicon_path = lexicon_path
        # Shards are read on demand and kept: a message usually touches one or
        # two, so a session holds a few thousand words, never twenty thousand.
        self._lex_shards: dict[str, dict | None] = {}
        self._lex_fa_cache: dict[str, list[str]] | None = None
        with open(memory_path, encoding="utf-8") as f:
            self.memory = json.load(f)
        self.user_name = None
        self.history = []          # short-term memory: recent user messages
        self.intents = self.memory["intents"]
        self._load_glossary(glossary_path)
        with open(grammar_path, encoding="utf-8") as f:
            self.grammar = json.load(f)["topics"]
        self.exercise = None       # active grammar session (practice | exam)
        self.exercise_score = 0
        self.practice_done: set = set()   # topics whose practice stage is cleared
        self.phrases = {}          # practical sentence banks (phrases.json)
        if PHRASES_FILE.exists():
            with open(phrases_path, encoding="utf-8") as f:
                self.phrases = json.load(f)["topics"]
        self.listening = []         # CEFR A1-C2 listening sentences
        if LISTENING_FILE.exists():
            with open(listening_path, encoding="utf-8") as f:
                self.listening = json.load(f)["levels"]
        self.jokes = []            # bilingual joke library
        self.last_joke_id = None   # avoid repeating the same joke twice in a row
        # What the learner is looking at right now. Without this, "exercises"
        # after a lesson is a dictionary miss instead of "start that lesson".
        self.last_lesson: str | None = None
        self.last_phrase: str | None = None
        self.last_level: str | None = None
        self.last_examples = []
        if JOKES_FILE.exists():
            with open(JOKES_FILE, encoding="utf-8") as f:
                self.jokes = json.load(f)
        self.distinctions = {}     # confusable pairs ("affect / effect")
        if distinctions_path.exists():
            with open(distinctions_path, encoding="utf-8") as f:
                self.distinctions = {t["id"]: t for t in json.load(f)["topics"]}
        self.idioms = {}           # figurative English with no literal gloss
        if idioms_path.exists():
            with open(idioms_path, encoding="utf-8") as f:
                self.idioms = {t["id"]: t for t in json.load(f)["topics"]}
        # The bank is content, not a panel: it is read at startup and answers
        # through the same conversation as everything else, so a learner who
        # types "no cap" gets the entry that explains it rather than a miss.
        self.slang_rows: list[dict] = []
        self.slang_index: dict[str, dict] = {}
        self.fa_idioms: list[dict] = []
        self.fa_idiom_index: dict[str, dict] = {}
        if slang_path.exists():
            self._load_slang(slang_path)
        self.corrections = []      # rule-based checker for common learner errors
        if corrections_path.exists():
            with open(corrections_path, encoding="utf-8") as f:
                self.corrections = json.load(f)["rules"]
        self.register = {}          # register.json - formal / everyday / casual
        if register_path.exists():
            with open(register_path, encoding="utf-8") as f:
                self.register = json.load(f)
        self.phonetics = []        # phonetics.json sections (titled listing)
        if phonetics_path.exists():
            with open(phonetics_path, encoding="utf-8") as f:
                self.phonetics = json.load(f).get("sections", [])
        self.daily = {"version": 1, "words": [], "expressions": [],
                      "conversations": []}
        if daily_path.exists():
            with open(daily_path, encoding="utf-8") as f:
                self.daily = json.load(f)
        # "today" is normally the device's own local date. It is injectable so
        # the tests can walk a year across a daylight-saving boundary without
        # waiting for one or touching the system clock.
        self.today = today
        self.daily_practice = None   # active conversation walk-through
        self._clean_answers()   # last: it reads the loaded topics



    def _clean_answers(self) -> None:
        """Drop blank answer slots at load time.

        An empty string in a question's answers is invisible in the JSON but
        very visible to a learner: "show answer" printed " / no article / zero"
        with a leading blank. A blank is also never something anyone can type,
        so in the data it can only ever be a mistake.
        """
        for topic in self.grammar.values():
            for stage in ("practice", "exam"):
                for q in topic.get(stage, []):
                    answers = q.get("a")
                    if not isinstance(answers, list):
                        continue
                    cleaned = [str(a).strip() for a in answers
                               if str(a).strip()]
                    if cleaned and cleaned != [str(a) for a in answers]:
                        q["a"] = cleaned
    def _load_glossary(self, path: Path) -> None:
        """Load glossary.json and build fast lookup indices."""
        with open(path, encoding="utf-8") as f:
            self.glossary = json.load(f)["domains"]
        # "_groups" is panel layout metadata, not a vocabulary domain
        self.glossary_groups = self.glossary.pop("_groups", [])
        self.glossary_en: dict[str, list] = {}
        self.glossary_fa: dict[str, list] = {}
        for dom_id, dom in self.glossary.items():
            for word in dom["words"]:
                en, fa = word[0], word[1]
                entry = (dom_id, en, fa)
                self.glossary_en.setdefault(normalize_word(en), []).append(entry)
                self.glossary_fa.setdefault(normalize_word(fa), []).append(entry)
                if len(word) > 2:  # optional digit alias, e.g. ["five", "پنج", "5"]
                    alias = normalize_word(word[2])
                    self.glossary_en.setdefault(alias, []).append(entry)

    def lookup_word(self, target: str):
        """Find glossary entries for a word (English, Persian, or digit)."""
        key = normalize_word(target)
        if not key:
            return []
        entries = self.glossary_en.get(key) or self.glossary_fa.get(key) or []
        # de-duplicate while keeping order
        seen, unique = set(), []
        for e in entries:
            if e not in seen:
                seen.add(e)
                unique.append(e)
        return unique

    # ------------------------------------------------------------------ #
    #  Dictionary — sharded lexical knowledge (tools/build_lexicon.py)
    # ------------------------------------------------------------------ #
    def _lex_shard(self, name: str) -> dict | None:
        """One shard, read once. A missing shard is a cached None, never a
        raise: the chat has to keep working if the dictionary is absent."""
        if name in self._lex_shards:
            return self._lex_shards[name]
        shard = None
        try:
            with open(self.lexicon_path / f"{name}.json", encoding="utf-8") as f:
                shard = json.load(f)
        except (OSError, ValueError):
            shard = None
        self._lex_shards[name] = shard
        return shard

    def lex_prefetch(self, text: str) -> None:
        """Read the shards this message could need, and nothing else."""
        for word in re.findall(r"[A-Za-z][A-Za-z'’-]*", text or ""):
            for name in lex_shard_names(word):
                self._lex_shard(name)

    def lex_find(self, word: str):
        """(headword, entry) for a word or one of its inflected forms."""
        key = normalize_word(word)
        if not key or not re.fullmatch(r"[a-z][a-z' -]*", key):
            return None
        for name in lex_shard_names(key):
            shard = self._lex_shard(name)
            if shard and key in shard["w"]:
                return key, shard["w"][key]
        for name in lex_shard_names(key):
            shard = self._lex_shard(name)
            if not shard:
                continue
            base = shard["f"].get(key)
            if base and base in shard["w"]:
                return base, shard["w"][base]
        return None

    def lex_near(self, word: str, limit: int = 3) -> list[str]:
        """Close headwords for a typo, bounded to the shards the word is in."""
        key = normalize_word(word)
        if len(key) < 3:
            return []
        max_dist = 1 if len(key) <= 5 else 2
        found = []
        for name in lex_shard_names(key):
            shard = self._lex_shard(name)
            if not shard:
                continue
            for candidate in shard["w"]:
                if abs(len(candidate) - len(key)) > max_dist:
                    continue
                dist = edit_distance(key, candidate)
                if dist and dist <= max_dist:
                    # "resilent" is one edit from both "resident" and
                    # "resilient"; the longer shared prefix is the one the
                    # learner was typing towards.
                    shared = 0
                    for a, b in zip(key, candidate):
                        if a != b:
                            break
                        shared += 1
                    dropped = is_subsequence(key, candidate)
                    found.append((dist, -dropped, -shared, candidate))
        found.sort()
        out: list[str] = []
        for _dist, _dropped, _shared, candidate in found:
            if candidate not in out:
                out.append(candidate)
            if len(out) == limit:
                break
        return out

    def lex_persian(self, word: str) -> list[str]:
        """English headwords for a Persian meaning.

        Only one-word meanings are keys - "بودن (صفت را دنبال می‌کند)" is a
        gloss, and treating it as a headword would be invention.
        """
        if self._lex_fa_cache is None:
            try:
                with open(self.lexicon_path / "_fa.json", encoding="utf-8") as f:
                    self._lex_fa_cache = json.load(f)["p"]
            except (OSError, ValueError):
                self._lex_fa_cache = {}
        key = normalize_fa(word)
        return self._lex_fa_cache.get(key) or []

    # ------------------------------------------------------- dictionary text
    @staticmethod
    def _lex_pos_text(entry: dict, lang: str) -> str:
        pos = entry.get("p") or []
        if not pos:
            return ""
        if lang == "fa":
            return "، ".join(LEX_POS_FA.get(p, p) for p in pos)
        return ", ".join(pos)

    @staticmethod
    def _lex_ipa(entry: dict) -> str:
        ipa = entry.get("i") or {}
        us, uk = ipa.get("us"), ipa.get("uk")
        if us and uk and us != uk:
            return f" /{us}/ (US) · /{uk}/ (UK)"
        if us or uk:
            return f" /{us or uk}/"
        return ""

    @staticmethod
    def _lex_sense_score(sense: list, tokens: set[str]) -> int:
        hay = " ".join([sense[1] or "", sense[3] or "", sense[2] or ""])
        return len(tokens & set(re.findall(r"[a-z']{2,}", hay.lower())))

    def format_lex_entry(self, head: str, entry: dict, asked: str,
                         lang: str, context: set[str] | None = None,
                         context_text: str = "") -> str:
        """One headword: pronunciation, part of speech, then its senses.

        `context` is the rest of the learner's sentence. With it, the sense
        that mentions those words is shown first and marked - "bank" in "I
        deposited money in the bank" must not open with a river.
        """
        senses = entry.get("s") or []
        best = None
        if context:
            scored = sorted(((self._lex_sense_score(senses[i], context), i)
                             for i in range(len(senses))), key=lambda t: (-t[0], t[1]))
            if scored and scored[0][0] > 0:
                best = scored[0][1]

        asked_norm = normalize_word(asked)
        label = f"**{head}**" if asked_norm == head else f"**{asked}** → **{head}**"
        line = f"📖 {label}{self._lex_ipa(entry)}"
        pos_text = self._lex_pos_text(entry, lang)
        if pos_text:
            line += f" — {pos_text}"
        if len(senses) > 1:
            line += (f" · {to_persian_digits(len(senses))} معنی" if lang == "fa"
                     else f" · {len(senses)} meanings")
        lines = [line]

        # Senses keep the source's order - renumbering them so the matching one
        # comes first made "sense 4 fits best" point at a line numbered 1. The
        # matching sense is shown, and marked, in the place it really has.
        shown_count = min(len(senses), max(3, (best or 0) + 1))
        for shown, i in enumerate(range(shown_count), start=1):
            sense = (senses[i] + [""] * 5)[:5]
            _pos, definition, meaning, example = sense[:4]
            # Two scripts, two lines. "بانک — a financial institution" was one
            # line, and a line whose first strong character is Persian is laid
            # out right to left - which reversed the English definition after
            # the dash. One language per line keeps each direction honest, and
            # it is how the learner reads it anyway: the meaning, then the
            # English definition under it.
            mark = " ★" if best is not None and i == best else ""
            num = to_persian_digits(shown) if lang == "fa" else str(shown)
            if meaning and definition:
                lines.append(f"   {num}. {meaning}{mark}")
                lines.append(f"      {definition}")
            else:
                lines.append(f"   {num}. {(meaning or definition)}{mark}")
            if example:
                lines.append(f"      ▸ {example}")
        if context and best is not None:
            num = to_persian_digits(best + 1) if lang == "fa" else str(best + 1)
            lines.append(
                f"   ↲ در جمله تو، معنی {num} مناسب‌تر است." if lang == "fa"
                else f"   ↲ In your sentence, sense {num} fits best.")
        elif context:
            # The learner named a sentence and none of the stored senses
            # mentions it. Saying so is the answer; picking the closest anyway
            # would be a guess dressed as a definition.
            said = context_text.strip(" .?!؟،")
            if lang == "fa":
                lines.append(f"   ↲ برای «{said}» معنی‌ای ثبت نکرده‌ام — این‌ها معنی‌های موجودند.")
            else:
                lines.append(f"   ↲ I have no sense recorded for \u201c{said}\u201d "
                             f"— these are the meanings I have.")
        return "\n".join(lines)

    def format_lex_relations(self, head: str, entry: dict, lang: str,
                             kind: str) -> str:
        """Synonyms (kind='y') or opposites (kind='a'), grouped by word class."""
        groups = entry.get(kind) or {}
        syn = kind == "y"
        if lang == "fa":
            title = ("🔗 مترادف‌های" if syn else "⚖️ متضادهای") + f" **{head}**"
            empty = "   ↲ در واژه‌نامه ثبت نشده است."
        else:
            title = ("🔗 synonyms of" if syn else "⚖️ opposites of") + f" **{head}**"
            empty = "   ↲ none are recorded in my dictionary."
        if not groups:
            return title + "\n" + empty
        lines = [title]
        for pos, words in groups.items():
            if not words:
                continue
            label = LEX_POS_FA.get(pos, pos) if lang == "fa" else pos
            lines.append(f"   • ({label}) " + " · ".join(words[:8]))
        return "\n".join(lines)

    def format_lex_examples(self, head: str, entry: dict, lang: str) -> str:
        """The worked sentences the source stored for a word.

        English only. The source's Persian sentence for a sense is an
        independent sentence about the word, not a translation of its English
        example - "I sautéed the mushroom with garlic and butter" sat above
        "I bought mushrooms at the market yesterday" - and printed underneath
        the English one it read as a mistranslation. A learner asking for an
        example wants a correct one, not a second sentence beside it.
        """
        examples = [s[3] for s in entry.get("s") or [] if s[3]]
        if not examples:
            return (f"🔎 برای **{head}** جمله‌ای ثبت نشده." if lang == "fa"
                    else f"🔎 My dictionary records no example sentence for **{head}**.")
        title = (f"📖 **{head}** — مثال‌ها" if lang == "fa"
                 else f"📖 **{head}** — examples")
        lines = [title]
        for example in examples[:2]:
            lines.append(f"   ▸ {example}")
        return "\n".join(lines)

    def format_lex_forms(self, head: str, entry: dict, lang: str,
                         only: str | None = None) -> str:
        forms = entry.get("f") or []
        if only:
            hits = [f[0] for f in forms if f[1] == only]
            label = LEX_FORM_LABEL.get(only, only)
            if hits:
                if lang == "fa":
                    return f"🔤 **{head}** — {label}: " + "، ".join(hits)
                return f"🔤 {label} of **{head}** → " + ", ".join(hits)
            return (f"🔤 برای **{head}** شکل «{label}» ثبت نشده." if lang == "fa"
                    else f"🔤 My dictionary records no {label} for **{head}**.")
        if not forms:
            return (f"🔤 برای **{head}** شکلی ثبت نشده." if lang == "fa"
                    else f"🔤 My dictionary records no inflected forms for **{head}**.")
        head_line = ("🔤 صورت‌های" if lang == "fa" else "🔤 forms of")
        lines = [f"{head_line} **{head}**"]
        for name, ftype in forms[:8]:
            label = LEX_FORM_LABEL.get(ftype, ftype or "form")
            lines.append(f"   • {label}: {name}")
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    #  Memory helpers
    # ------------------------------------------------------------------ #
    def remember(self, text: str) -> None:
        self.history.append(text)
        if len(self.history) > 100:
            self.history.pop(0)

    def learn_name(self, text: str) -> bool:
        match = re.search(
            r"(?:my name is|call me|اسم من|اسمم|من هستم)\s+([^\s.,!?؟]+(?:\s+[^\s.,!?؟]+)?)",
            text,
            re.IGNORECASE,
        )
        if match:
            name = match.group(1).strip()
            name = re.sub(r"\s+(است|هستم|is)$", "", name, flags=re.IGNORECASE)
            if name:
                self.user_name = name
                return True
        return False

    # ------------------------------------------------------------------ #
    #  Intent matching (score-based: most matched keywords wins)
    # ------------------------------------------------------------------ #
    def match_intent(self, text: str, lang: str):
        lowered = text.lower()
        folded_fa = fold_fa(text)
        best_intent, best_score = None, 0
        for intent in self.intents:
            score = 0
            for kw in intent["keywords"].get(lang, []):
                # phrases are more specific than single words → higher score
                weight = 3 if len(kw.split()) > 1 else 2
                if lang == "en":
                    # word-boundary match so "hi" doesn't hit "this";
                    # allow simple plurals ("joke" matches "jokes")
                    suffix = r"(?:s|es)?" if len(kw) >= 3 else ""
                    if re.search(rf"\b{re.escape(kw)}{suffix}\b", lowered):
                        score += weight
                elif fold_fa(kw) in folded_fa:  # Persian is agglutinative — substring is safer
                    score += weight
            if score > best_score:
                best_intent, best_score = intent, score
        return best_intent if best_score >= 2 else None

    def reply_from_intent(self, intent, lang: str) -> str:
        responses = intent["responses"].get(lang) or intent["responses"]["en"]
        reply = random.choice(responses)
        name = self.user_name or ("دوست من" if lang == "fa" else "friend")

        if intent["name"] == "greeting" and self.user_name:
            reply = reply.rstrip("!؛. ") + f" {self.user_name}!"
        if intent["name"] == "time":
            now = datetime.now()
            if lang == "fa":
                fa_time = now.strftime("%H:%M").translate(PERSIAN_DIGITS)
                return f"الان ساعت {fa_time} است."
            return f"It's {now.strftime('%I:%M %p').lstrip('0')}."
        if intent["name"] == "date":
            now = datetime.now()
            if lang == "fa":
                fa_date = now.strftime("%Y/%m/%d").translate(PERSIAN_DIGITS)
                return f"امروز {fa_date} است."
            return f"Today is {now.strftime('%A, %B %d, %Y')}."
        if intent["name"] == "help":
            return HELP_TEXT[lang]
        if intent["name"] in ("yes", "no") and self.user_name:
            reply += f" {name}"
        return reply

    # ------------------------------------------------------------------ #
    #  Alphabet helpers (structured knowledge)
    # ------------------------------------------------------------------ #
    def letters(self, language: str) -> str:
        info = self.memory["alphabets"][language]
        return f"{info['description_en']} ({info['description_fa']})\n{' '.join(info['letters'])}"

    def handle_alphabet(self, text: str, lowered: str) -> str | None:
        # Some Persian grammar words contain "حروف" (= letters), e.g. "حروف تعیین"
        # (articles) and "حروف ربط" (conjunctions). A specific grammar request wins.
        if self.match_grammar_topic(text, lowered, "fa") or self.match_grammar_topic(
            text, lowered, "en"
        ):
            return None
        wants_persian = "persian" in lowered or "farsi" in lowered or "فارسی" in text
        wants_english = "english" in lowered or "انگلیسی" in text
        wants_alphabet = any(w in lowered for w in ("alphabet", "letters", "abc", "abjad")) or any(
            w in text for w in ("الفبا", "حروف", "ابجد")
        )
        if not wants_alphabet:
            return None
        if wants_persian and not wants_english:
            return self.letters("persian")
        if wants_english and not wants_persian:
            return self.letters("english")
        return f"English: {self.letters('english')}\n\nPersian: {self.letters('persian')}"

    def handle_letter_lookup(self, text: str) -> str | None:
        match = re.search(
            r"(?:letter|حرف)\s+(?:is\s+)?([a-z]|[\u0600-\u06FF])\b",
            text,
            re.IGNORECASE,
        )
        if not match:
            return None
        ch = match.group(1)
        if ch.isascii() and ch.isalpha():
            letters = self.memory["alphabets"]["english"]["letters"]
            if ch.upper() in letters:
                idx = letters.index(ch.upper()) + 1
                return f"'{ch.upper()}' is letter number {idx} in the English alphabet."
        elif "\u0600" <= ch <= "\u06FF":
            letters = self.memory["alphabets"]["persian"]["letters"]
            if ch in letters:
                idx = to_persian_digits(letters.index(ch) + 1)
                return f"«{ch}» حرف شماره {idx} در الفبای فارسی است."
            return f"«{ch}» در الفبای فارسی وجود ندارد."
        return None

    # ------------------------------------------------------------------ #
    #  Section names — the terminal has no top bar, so the bot must show
    #  the content itself instead of pointing at a panel that isn't there.
    # ------------------------------------------------------------------ #
    SECTION_WORDS = {
        "vocabulary": ("📚 Vocabulary", "واژگان", "📚"),
        "words": ("📚 Vocabulary", "واژگان", "📚"),
        "واژگان": ("📚 Vocabulary", "واژگان", "📚"),
        "کلمات": ("📚 Vocabulary", "واژگان", "📚"),
        "sentences": ("💬 Sentence banks", "جملات", "💬"),
        "phrases": ("💬 Sentence banks", "جملات", "💬"),
        "جملات": ("💬 Sentence banks", "جملات", "💬"),
        "جمله": ("💬 Sentence banks", "جملات", "💬"),
        "phonetics": ("🗣 Sounds & phonetics", "تلفظ", "🗣"),
        "تلفظ": ("🗣 Sounds & phonetics", "تلفظ", "🗣"),
        "آوا": ("🗣 Sounds & phonetics", "تلفظ", "🗣"),
        "grammar": ("📘 Grammar lessons", "گرامر", "📘"),
        "گرامر": ("📘 Grammar lessons", "گرامر", "📘"),
        "listening": ("🎧 Listening", "شنیدن", "🎧"),
        "شنیدن": ("🎧 Listening", "شنیدن", "🎧"),
    }

    def handle_section(self, text: str, lowered: str, lang: str) -> str | None:
        """A bare section name has to return content, not a panel hint."""
        s = re.sub(r"[.!?؟,;:\"'«»()\[\]]", "", lowered).strip()
        s = re.sub(r"^(?:open|show|باز کن|نشان بده|نمایش)\s+", "", s,
                   flags=re.IGNORECASE).strip()
        key = self.SECTION_WORDS.get(s)
        if not key:
            return None
        title, title_fa, icon = key

        if title.startswith("📚"):
            groups = self.glossary_groups or [
                {"id": "all", "en": "All domains", "fa": "همه دامنه‌ها",
                 "domains": [d for d in self.glossary]}]
            lines = [f"{title} — {title_fa} · "
                     f"{len(self.glossary)} domains, "
                     f"{sum(len(d['words']) for d in self.glossary.values())} words"]
            for g in groups[:8]:
                names = [self.glossary[d]["label"]["en"]
                         for d in g["domains"] if d in self.glossary]
                if not names:
                    continue
                lines.append(f"   • {g['en']}: {', '.join(names[:6])}"
                             + ("…" if len(names) > 6 else ""))
            lines.append("")
            lines.append("Ask for one by name — 'fruits', 'colors', 'advanced adjectives'.")
            return "\n".join(lines)

        if title.startswith("💬"):
            lines = [f"{title} — {title_fa} · {len(self.phrases)} banks"]
            for tid, topic in self.phrases.items():
                lines.append(f"   • {topic['title']['en']} ({topic['title']['fa']})")
            lines.append("")
            lines.append("Ask for one by name — 'travel sentences', 'daily routine'.")
            return "\n".join(lines)

        if title.startswith("🗣"):
            lines = [f"{title} — {title_fa} · {len(self.phonetics)} sections"]
            for sec in self.phonetics:
                ts = sec.get("title", {})
                lines.append(f"   {sec.get('icon', '•')} {ts.get('en', '?')} "
                             f"({ts.get('fa', '')}) — {sec.get('level', '')}")
            lines.append("")
            lines.append("Open 🗣 Sounds in the app for the rows and the audio.")
            return "\n".join(lines)

        # grammar and listening already have their own menus; reuse them
        if title.startswith("📘"):
            return self.handle_grammar(text, lowered, lang)
        if title.startswith("🎧"):
            return self.handle_listening(text, lowered, lang)
        return None

    # ------------------------------------------------------------------ #
    #  Contextual follow-ups — "exercises" after a lesson, "another one"
    #  after a joke. A learner thinks in sequences, not in commands.
    # ------------------------------------------------------------------ #
    BARE_EXERCISE = {
        "exercises": "practice", "exercise": "practice", "practice": "practice",
        "lets practice": "practice", "let us practice": "practice",
        "i want to practice": "practice", "start practice": "practice",
        "begin practice": "practice", "practice exercises": "practice",
        "quiz": "exam", "exam": "exam", "test": "exam",
        "lets take the exam": "exam", "i want the exam": "exam",
        "give me the exam": "exam", "final exam": "exam",
        "تمرین": "practice", "تمرین کن": "practice", "تمرین بده": "practice",
        "امتحان": "exam", "آزمون": "exam", "آزمون بده": "exam",
    }
    BARE_CANCEL = {
        "cancel", "stop", "quit", "exit", "close", "enough", "never mind",
        "nevermind", "end", "finish", "i give up", "give up",
        "بیخیال", "لغو", "کنسل", "بس کن", "توقف", "رد کن",
    }
    BARE_NEXT = {
        "next", "next question", "next one", "continue", "go on", "skip",
        "skip this", "another question",
        "بعدی", "سوال بعدی", "ادامه", "برو بعدی", "رد کن اینو",
    }
    BARE_AGAIN = {
        "another one", "again", "one more", "another joke", "tell me another",
        "tell me another joke", "another", "more jokes", "again please",
        "یکی دیگه", "یکی دیگه بگو", "دوباره", "جوک دیگه", "یه جوک دیگه",
    }
    BARE_REPEAT = {
        "repeat that", "say that again", "say it again", "again please",
        "one more time", "pardon", "come again", "what did you say",
        "what", "听不懂", "دوباره بگو", "تکرار کن", "چی گفتی",
    }
    BARE_SHOW = {
        "show answer", "the answer", "answer please", "what is the answer",
        "give me the answer", "answer", "solution",
        "جواب", "جواب بده", "پاسخ", "پاسخ درست",
    }
    BARE_EXAMPLES = {
        "examples", "more examples", "give me examples", "show examples",
        "another example", "example sentences", "more examples please",
        "مثال", "مثال بیشتر", "مثال بده",
    }

    @staticmethod
    def _bare(lowered: str, table) -> str | None:
        """Match a follow-up word for word.

        Bare words need an exact hit: 'next' must not fire inside 'what is the
        next colour', or the bot would skip ahead while answering a question.
        The table may be a dict (value = what to do) or a plain set.
        """
        s = re.sub(r"[.!?؟,;:\"'«»()\[\]]", "", lowered).strip()
        if s in table:
            return table[s] if isinstance(table, dict) else s
        if re.fullmatch(r"(?:please\s+)?(?:can you\s+|could you\s+)?"
                        r"(?:give me|tell me|show me|let me|start|begin|open)\s+"
                        r"[\w' ]{0,24}", s) and s.split()[-1] in table:
            hit = s.split()[-1]
            return table[hit] if isinstance(table, dict) else hit
        return None

    def handle_followup(self, text: str, lowered: str, lang: str) -> str | None:
        """One-word commands that act on whatever the learner just opened."""
        if self.exercise:
            return None        # a live quiz owns every message already

        which = self._bare(lowered, self.BARE_EXERCISE)
        if which:
            topic_id = self.last_lesson
            if topic_id is None:
                return ("Open a lesson first, then say 'exercises'.\n"
                        "   ↲ اول یک درس را باز کن، بعد بنویس «تمرین».\n"
                        "   Write 'grammar' for the list of lessons."
                        if lang == "en" else
                        "اول یک درس را باز کن، بعد بنویس «تمرین».\n"
                        "   For the list of lessons write 'گرامر'.")
            return self.start_grammar_session(topic_id, which, lang)

        if self._bare(lowered, self.BARE_CANCEL):
            self.last_lesson = None
            self.last_examples = []
            return ("👍 Canceled. / لغو شد." if lang == "en"
                    else "👍 لغو شد. / Canceled.")

        which = self._bare(lowered, self.BARE_SHOW)
        if which:
            if self.last_examples:
                answer = " / ".join(self.last_examples)
                return (f"💡 Answer: {answer}\n   ↲ جواب: {answer}"
                        if lang == "en" else f"💡 جواب: {answer}\n   Answer: {answer}")
            if self.last_level:
                return self.format_listening_level(self.last_level)
            return ("Nothing to reveal yet — open a lesson or ask me a question.\n"
                    "   ↲ هنوز چیزی برای نمایش نیست — یک درس را باز کن."
                    if lang == "en" else
                    "هنوز چیزی برای نمایش نیست — یک درس را باز کن.")

        which = self._bare(lowered, self.BARE_EXAMPLES)
        if which:
            topic = self.grammar.get(self.last_lesson or "", None)
            if topic:
                rows = topic.get("examples", [])
                self.last_examples = self._example_answers(topic)
                return ("📝 More examples — مثال‌های بیشتر:\n" + "\n".join(
                    f"   {i + 1}. {r['en']}\n      ↲ {r['fa']}"
                    for i, r in enumerate(rows)))
            return ("Open a lesson first and ask for examples.\n"
                    "   ↲ اول یک درس را باز کن.")

        which = self._bare(lowered, self.BARE_AGAIN)
        if which:
            return self.tell_joke(text, lang)

        which = self._bare(lowered, self.BARE_REPEAT)
        if which:
            if self.last_level:
                return self.format_listening_level(self.last_level)
            if self.last_phrase:
                topic = self.phrases.get(self.last_phrase)
                if topic:
                    return ("Say it again — دوباره گوش کن:\n" + "\n".join(
                        f"   • {r['en']}\n     ↲ {r['fa']}"
                        for r in topic["phrases"][:4]))
            return ("Tell me what to repeat — a listening band or a sentence bank.\n"
                    "   ↲ بگو کدام را تکرار کنم." if lang == "en" else
                    "بگو کدام را تکرار کنم.")

        if self._bare(lowered, self.BARE_NEXT):
            topic_id = self.last_lesson
            if topic_id is None:
                return None
            return self.start_grammar_session(topic_id, "practice", lang)

        return None

    # ------------------------------------------------------------------ #
    #  Numbers written in words ("twenty one" → ۲۱)
    # ------------------------------------------------------------------ #
    def handle_number(self, text: str, lang: str) -> str | None:
        """Read an English number phrase and give the digits in both scripts.

        A learner asking "twenty one" wants the number, not a dictionary
        miss, so this runs before the glossary lookup.
        """
        m = re.fullmatch(
            r"\s*(?:what(?:'s| is)|چند است|چنده)?\s*"
            r"(?:the number\s+)?([a-z\- ]+?)\s*"
            r"(?:in (?:english|فارسی))?\s*[?!؟]*\s*",
            text, re.IGNORECASE,
        )
        if not m:
            return None
        phrase = m.group(1).strip().lower()
        value = number_from_words(phrase)
        if value is None:
            return None
        en = f"{value}"
        fa = to_persian_digits(value)
        if lang == "fa":
            return f"«{phrase}» → {fa}  ({en})\nعدد {en} به فارسی: {fa}"
        return f'"{phrase}" → {en} ({fa})\n' + to_english_digits(value)

    # ------------------------------------------------------------------ #
    #  Confusable pairs — "what's the difference between X and Y?"
    # ------------------------------------------------------------------ #
    def match_distinction(self, text: str, lowered: str):
        """The pair a learner is asking about, or None.

        Keywords like "affect or effect" carry more weight than a bare word
        match, so the explicit phrasings are tried first.
        """
        best, best_score = None, 0
        for topic_id, topic in self.distinctions.items():
            for score, kws in ((3, topic["keywords"]["en"]),
                               (2, topic["keywords"]["fa"])):
                for kw in kws:
                    if normalize_fa(kw) in normalize_fa(text):
                        if score > best_score:
                            best, best_score = topic_id, score
        return best

    def format_distinction(self, topic_id: str, lang: str) -> str:
        topic = self.distinctions[topic_id]
        title = topic["title"]["en"]
        lines = [f"⚖️  {title}  ·  ({topic['title']['fa']})",
                 f"   ↲ سطح: {topic['level']}", "",
                 f"{topic['why']}"]
        for side in topic["sides"]:
            lines.append("")
            lines.append(f"  • {side['en']}")
            if side.get("fa"):
                lines.append(f"    ↲ {side['fa']}")
        return "\n".join(lines)

    def handle_distinction(self, text: str, lowered: str, lang: str) -> str | None:
        if not re.search(
            r"\b(difference|differ|confus|compare|versus|vs\b|"
            r"which one|tell .*\bfrom\b|when (?:do|should|would) (?:i|we) use|"
            r"when to use|usage of|"
            r"تفاوت|فرق|کدام|چه تفاوتی|کی به کار ببرم)",
            lowered + " " + text,
        ):
            return None
        topic_id = self.match_distinction(text, lowered)
        if topic_id:
            return self.format_distinction(topic_id, lang)
        names = " · ".join(
            t["title"]["en"] for t in list(self.distinctions.values())[:8])
        return (
            f"⚖️  Confusable pairs I can explain — جفت‌هایی که قاطی می‌شوند:\n{names}\n"
            "Ask: 'difference between affect and effect' or 'تفاوت since و for'"
        )

    # ------------------------------------------------------------------ #
    #  Idioms — figurative English with no literal gloss
    # ------------------------------------------------------------------ #
    def match_idiom(self, word: str) -> dict | None:
        key = normalize_word(word)
        if not key:
            return None
        bare = normalize_word(strip_article(word))
        for topic in self.idioms.values():
            for row in topic["idioms"]:
                row_key = normalize_word(row["en"])
                if row_key == key or (
                        bare and normalize_word(strip_article(row["en"])) == bare):
                    return row
                # partial: "spill beans" should still find "spill the beans"
                head = key.split()
                if len(head) >= 2 and normalize_word(row["en"]).startswith(
                        " ".join(head[:1])) and set(head) <= set(
                        normalize_word(row["en"]).split()):
                    return row
        return None

    def format_idiom(self, row: dict) -> str:
        return (f"🗯  “{row['en']}” — {row['fa']}\n"
                f"   ↲ {row['meaning']}\n"
                f"   e.g. {row['example']}")

    def handle_idioms(self, text: str, lowered: str, lang: str) -> str | None:
        # The idiom on its own is a question about it. "Break a leg" is what
        # somebody types after hearing it — and "break a leg" is a wish for a
        # good performance, never an instruction about a leg. Without this it
        # came back as "I'm not sure I understand", with the entry that
        # explains it sitting two lines below in the same table.
        bare = re.sub(r"[^\w' \-]+", " ", lowered).strip()
        if len(bare.split()) >= 2:
            row = self.match_idiom(bare)
            if row:
                return self.format_idiom(row)
        target = None
        m = re.search(
            r"(?:meaning|mean|means|idiom|یعنی|معنی|معنی اصطلاح)\s*(?:of\s*)?"
            r"[\"'‘’]?([a-z][a-z' \-]{2,30}?)[\"'‘’]?\s*[?!.؟]*\s*$",
            lowered.strip(), re.IGNORECASE,
        )
        if m:
            target = m.group(1)
        else:
            m = re.search(r"[\"'‘’]([a-z][a-z' \-]{2,30}?)[\"'’]", lowered)
            if m:
                target = m.group(1)
        if not target:
            m = re.search(
                r"^\s*(?:what is|what are|what's)\s+"
                r"[\"'‘’]?([a-z][a-z' \-]{2,30}?)[\"'‘’]?\s*[?!.؟]*\s*$",
                lowered, re.IGNORECASE,
            )
            if m and self.match_idiom(m.group(1)):
                target = m.group(1)
        if not target:
            m = re.search(
                r"(?:what (?:does|do|is|are) |meaning of |"
                r"یعنی |معنی |معنیِ )[\"'‘’]?"
                r"([a-z][a-z' \-]{2,30}?)[\"'‘’]?"
                r"\s+(?:mean|means|یعنی|چه معنی)",
                lowered.strip(), re.IGNORECASE,
            )
            if m:
                target = m.group(1)
        if target:
            target = re.sub(r"^(?:the\s+|what(?:'s| is| does)?\s+|"
                            r"meaning of\s+|mean\s+|یعنی\s+|معنی\s+)", "",
                            target.strip(), flags=re.IGNORECASE)
            row = self.match_idiom(target)
            if row:
                return self.format_idiom(row)
            return None

        wants_list = bool(re.search(
            r"\b(idioms?|sayings?|phrases? (?:in english|list))\b", lowered)
        ) or any(w in text for w in ("اصطلاح", "ضرب المثل انگلیسی"))
        if not wants_list:
            return None
        rows = [r for t in self.idioms.values() for r in t["idioms"]]
        lines = ["🗯  Idioms & sayings — اصطلاح‌ها و ضرب‌المثل‌ها:"]
        for row in rows:
            lines.append(f"   • {row['en']}  —  {row['fa']}")
        lines.append("")
        lines.append("Ask: 'meaning of once in a blue moon' or 'معنی hit the books'")
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    #  The slang and idiom bank — modern usage in both directions
    # ------------------------------------------------------------------ #
    @staticmethod
    def _slang_key(text: str) -> str:
        """The shape a term is looked up under: lower case, no articles."""
        s = text.lower().replace("’", "'").replace("`", "'")
        s = re.sub(r"[^a-z0-9' \-]+", " ", s)
        s = " ".join(s.split())
        return re.sub(r"^(?:the|a|an) ", "", s)

    @staticmethod
    def _fa_key(text: str) -> str:
        s = re.sub(r"[«»\"'?؟!.,،:؛]+", " ", text)
        return " ".join(s.translate(FA_FOLD).split())

    def _load_slang(self, path: Path) -> None:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for row in data.get("slang") or []:
            entry = {"kind": "slang", "term": row.get("t", ""),
                     "gloss": row.get("en", ""), "fa": row.get("fa", ""),
                     "reg": row.get("reg", ""), "cat": row.get("cat", ""),
                     "ex": "", "exfa": "", "al": row.get("al") or []}
            self.slang_rows.append(entry)
            for key in [entry["term"], *entry["al"]]:
                k = self._slang_key(key)
                if k:
                    self.slang_index.setdefault(k, entry)
        for row in data.get("idioms") or []:
            entry = {"kind": "idiom", "term": row.get("en", ""),
                     "gloss": row.get("meaning", ""), "fa": row.get("fa", ""),
                     "reg": row.get("reg", ""), "cat": "",
                     "ex": row.get("ex", ""), "exfa": row.get("exfa", ""),
                     "al": []}
            if not entry["term"]:
                continue
            self.slang_rows.append(entry)
            k = self._slang_key(entry["term"])
            if k:
                self.slang_index.setdefault(k, entry)
        for row in data.get("fa_idioms") or []:
            key = self._fa_key(row.get("fa", ""))
            if not key:
                continue
            self.fa_idioms.append(row)
            self.fa_idiom_index.setdefault(key, row)

    @staticmethod
    def _bank_tag(row: dict) -> str:
        reg = SLANG_REG_FA.get(row.get("reg", ""), "")
        cat = SLANG_CAT_FA.get(row.get("cat", ""), "")
        return " · ".join(x for x in (reg, cat) if x)

    def format_bank(self, row: dict) -> str:
        head = f"🗯  “{row['term']}”"
        if row.get("fa"):
            head += f" — {row['fa']}"
        lines = [head]
        if row.get("gloss"):
            lines.append(f"   ↲ {row['gloss']}")
        if row.get("ex"):
            lines.append(f"   e.g. {row['ex']}")
        if row.get("exfa"):
            lines.append(f"   در جمله: {row['exfa']}")
        tag = self._bank_tag(row)
        if tag:
            lines.append(f"   🏷 {tag}")
        return "\n".join(lines)

    def format_fa_idiom(self, row: dict) -> str:
        lines = [f"🗯  «{row['fa']}»"]
        if row.get("exfa"):
            lines.append(f"   ↲ در جمله: {row['exfa']}")
        if row.get("exen"):
            lines.append(f"   ↗ به انگلیسی: {row['exen']}")
        return "\n".join(lines)

    def match_bank(self, word: str) -> dict | None:
        key = self._slang_key(word)
        if not key:
            return None
        row = self.slang_index.get(key)
        if row:
            return row
        # "spill beans" should find "spill the beans", as match_idiom does
        parts = set(key.split())
        if len(parts) >= 2:
            for k, cand in self.slang_index.items():
                if set(k.split()) == parts:
                    return cand
        return None

    def match_fa_idiom(self, text: str) -> dict | None:
        key = self._fa_key(text)
        if not key:
            return None
        row = self.fa_idiom_index.get(key)
        if row:
            return row
        # idioms are stored the way the corpus wrote them; a learner adds a
        # subject or a verb ending around them, so a whole-phrase match either
        # way is the useful reading
        for k, cand in self.fa_idiom_index.items():
            if len(k.split()) >= 2 and (k in key or key in k):
                return cand
        return None

    @staticmethod
    def _bank_target(text: str, lowered: str) -> str | None:
        m = re.search(
            r"(?:what (?:does|do|is|are) |what's |meaning of |mean by )"
            r"[\"'‘“]?([a-z][a-z' \-]{1,40}?)[\"'’”]?\s*"
            r"(?:mean|means|stand for)?\s*[?!.]*$", lowered.strip())
        if m:
            return m.group(1)
        m = re.search(
            r"(?:معنی|یعنی|مفهوم)\s*[\"'«]?([a-z][a-z' \-]{1,40}?)"
            r"[\"'»]?\s*(?:چیست|چیه|چی|یعنی)?\s*[؟?!.]*$", text.strip())
        if m:
            return m.group(1)
        # the other way round: "ghosting یعنی چی" asks about a word it has
        # already said, which is how most Persian speakers phrase it
        m = re.search(
            r"(?:^|\s)([a-z][a-z' \-]{1,40}?)\s*"
            r"(?:یعنی|به معنی|چه معنی|چه معنی‌ای)\s*(?:چی|چیه|چیست|دارد)?\s*[؟?!.]*$",
            lowered.strip())
        if m:
            return m.group(1)
        m = re.search(r"[\"'“‘]([a-z][a-z' \-]{1,40})[\"'”’]", lowered)
        if m:
            return m.group(1)
        return None

    def handle_slang(self, text: str, lowered: str, lang: str) -> str | None:
        # A Persian idiom asked about in Persian is its own lookup: the answer
        # is the English the learner would actually say.
        fa_row = self.match_fa_idiom(text)
        if fa_row:
            return self.format_fa_idiom(fa_row)

        bare = self._slang_key(lowered)
        # A phrase on its own is a question about it. A single word is only a
        # question when it is asked about - "fire", "bet" and "good" are
        # ordinary words too, and a tutor that answered them with a slang
        # entry would be pushing slang into every second message.
        if len(bare.split()) >= 2:
            row = self.match_bank(bare)
            if row:
                return self.format_bank(row)

        target = self._bank_target(text, lowered)
        if target:
            row = self.match_bank(target)
            if row:
                return self.format_bank(row)
            return None

        wants = bool(re.search(
            r"\b(slang|street words?|internet words?)\b", lowered))
        wants = wants or any(w in text for w in ("اسلنگ", "عامیانه", "خودمانی"))
        if not wants:
            return None
        rows = [r for r in self.slang_rows if r["kind"] == "slang"]
        lines = ["💬 Slang — اصطلاح‌های عامیانه:"]
        for row in rows[:40]:
            fa = f"  —  {row['fa']}" if row["fa"] else ""
            lines.append(f"   • {row['term']}{fa}")
        if len(rows) > 40:
            lines.append(f"   … و {len(rows) - 40} مورد دیگر")
        lines.append("")
        lines.append("Ask: 'what does no cap mean' or 'معنی bruh'")
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    #  Grammar checker — fix the errors a learner actually makes
    # ------------------------------------------------------------------ #
    def check_grammar(self, sentence: str) -> list[dict]:
        """Return the rules this sentence breaks: [{label, fix, why, was}]."""
        found, seen = [], set()
        for rule in self.corrections:
            m = re.search(rule["pattern"], sentence, re.IGNORECASE)
            if not m:
                continue
            if "{sg}" in rule["fix"] and not m.group(0).lower().endswith("s"):
                continue
            if "{pp}" in rule["fix"]:
                # only fire when the verb is a past simple that is not also a
                # participle - "have seen" and "have gone" are both correct
                hit = re.findall(r"[a-z']+", m.group(0).lower())
                if not hit or hit[-1] not in PAST_SIMPLE_ONLY:
                    continue
            key = rule["label"]
            if key in seen:
                continue
            seen.add(key)
            was = " ".join(m.group(0).split())
            fix = self._render_fix(rule["fix"], m, sentence)
            whole = self._apply_fix(sentence, m, rule["fix"])
            if whole and "{sg}" in rule["fix"]:
                # "many informations" → "much information": the determiner
                # changes with the noun, and that is the part learners miss.
                whole = re.sub(
                    r"\b(many|a|an|several|few)\s+(information|advice|"
                    r"equipment|furniture|software|research|homework|"
                    r"knowledge)\b",
                    lambda mm: ("much " if mm.group(1).lower() == "many"
                                else "some ") + mm.group(2),
                    whole, flags=re.IGNORECASE)
            found.append({
                "label": rule["label"],
                "fix": fix,
                "why": rule["why"],
                "was": was,
                "whole": whole,
            })
        return found

    def _render_fix(self, fix: str, m, sentence: str) -> str:
        """Turn a fix template into the words a learner should actually write.

        {0} {1} {2} are the match's capture groups (falling back to the first,
        last word of the match), and {pp} is the past participle of the verb
        that was used - so "have went" becomes "have gone", not "have {pp}".
        """
        if "{" not in fix:
            return fix
        groups = [g for g in m.groups() if g is not None]
        words = re.findall(r"[a-z']+", m.group(0), re.IGNORECASE)

        def pick(i: int, fallback: str = "") -> str:
            if i < len(groups):
                return groups[i].strip()
            if not words:
                return fallback
            idx = i if i < len(words) else len(words) - 1
            return words[idx]

        verb = words[-1] if words else ""
        out = fix
        for i in (2, 1, 0):
            out = out.replace("{%d}" % i, pick(i))
        out = out.replace("{base}", BASE_FORMS.get(verb.lower(), verb))
        out = out.replace("{pp}", past_participle(verb))
        out = out.replace("{sg}", singular(verb))
        out = out.replace("{th}", third_person(pick(1)))
        return re.sub(r"\s{2,}", " ", out).strip()

    def _apply_fix(self, sentence: str, m, fix: str) -> str:
        """The learner's own sentence, with just this error repaired."""
        if "reorder" in fix or " / " in fix or not m.group(0).strip():
            return ""
        rendered = self._render_fix(fix, m, sentence)
        if "{" in rendered or not rendered:
            return ""
        start, end = m.span()
        return (sentence[:start] + rendered + sentence[end:]).replace("  ", " ").strip()

    def handle_correction(self, text: str, lowered: str, lang: str) -> str | None:
        # "میشه" (could you) opens any polite Persian request, so it is not a
        # check-this-sentence marker: "میشه present perfect رو برام explain
        # کنی؟" is a question about English, not an English sentence to mark.
        asked = bool(re.search(
            r"\b(is (?:this|that|it) (?:correct|right|wrong)|check my|"
            r"correct (?:my|this|these|the)|fix (?:my|this|my sentence)|"
            r"is this ok|grammatically|درسته|درست است|غلطه)",
            lowered)) or "درسته" in text or "غلط" in text
        # a bare English sentence is an implicit request to check it
        sentence = re.sub(
            r"^\s*(?:is (?:this|that|it) (?:sentence )?"
            r"(?:correct|right|ok|wrong)\b[?:]?|"
            r"(?:please\s+)?correct (?:this|my|these|the)?\s*"
            r"(?:sentence|text)?\b[:]?|"
            r"check (?:this|that|my)\s*(?:sentence|text)?\b[:]?|"
            r"fix (?:my|this)\s*(?:sentence)?\b[:]?|"
            r"آیا این جمله درسته[؟?]?)\s*",
            "", text, flags=re.IGNORECASE).strip(" .?!؟،,")
        if not sentence or re.search(r"[\u0600-\u06FF]", sentence):
            if not asked:
                return None
        # The rules are English rules. A Persian-dominant message asks *about*
        # English; it is not an English sentence to mark, and answering it with
        # "this sentence is correct English" was the wrong reply.
        latin = len(re.findall(r"[A-Za-z]", sentence))
        persian = len(re.findall(r"[\u0600-\u06FF]", sentence))
        if persian and latin < persian:
            if asked:
                return ("Send me the English sentence and I'll mark it. / "
                        "جملهٔ انگلیسی را بفرست تا بررسی کنم.")
            return None
        looks_like_question = "?" in sentence or "؟" in sentence
        # The rules are specific enough to be their own signal: if one fires
        # on a plain English sentence, the learner wants it checked whether or
        # not they remembered to ask.
        problems = [] if asked else self.check_grammar(sentence)
        if not asked and not problems:
            return None
        if looks_like_question and not asked:
            return None
        if not asked and len(sentence.split()) < 2:
            return None
        if asked:
            problems = self.check_grammar(sentence)
        if not problems:
            if asked:
                alt = second_opinion(sentence)
                lead = ("✅ That sentence is correct English.  ↲ این جمله درست است."
                        if lang == "en" else
                        "✅ این جمله درست است. / That sentence is correct English.")
                return lead + (("\n\n" + alt) if alt else "")
            return None
        head = ("✏️  A couple of things to fix — چند نکته برای اصلاح:"
                if len(problems) > 1 else
                "✏️  One thing to fix — یک نکته برای اصلاح:")
        lines = [head]
        for p in problems:
            lines.append(f"   • {p['was']}  →  {p['fix']}")
            lines.append(f"     {p['why']}")
        whole = next((p["whole"] for p in problems if p.get("whole")), "")
        if whole:
            lines.append("")
            lines.append(f"✅ Better: {whole}")
        alt = second_opinion(sentence)
        if alt:
            lines.append("")
            lines.append(alt)
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    #  Pronunciation — how do you SAY it
    # ------------------------------------------------------------------ #
    def lookup_phrase(self, phrase: str) -> dict | None:
        """Find a whole sentence in phrases.json so 'thank you' still answers.

        Prefers the shortest sentence containing the phrase, so "thank you"
        lands on "Thank you." rather than a long line that happens to use it.
        """
        key = " ".join(normalize_word(phrase).split())
        bare = " ".join(normalize_word(strip_article(phrase)).split())
        if not key or len(key) < 3:
            return None
        core = next((v for k, v in CORE_PHRASES.items()
                     if normalize_word(k) in (key, bare)), None)
        if core:
            return {"en": core[0], "fa": core[1]}
        best = None
        for topic in self.phrases.values():
            for line in topic["phrases"]:
                norm = " ".join(normalize_word(line["en"]).split())
                if norm == key:
                    return line
                if key in norm:
                    if best is None or len(norm) < len(best[0]):
                        best = (norm, line)
        return best[1] if best else None

    def handle_pronounce(self, text: str, lowered: str, lang: str) -> str | None:
        """'how do you say X' — say it slowly, mark the stress, name the sound."""
        m = re.search(
            r"(?:how (?:do (?:you|i|we) )?(?:say|pronounce|read)|"
            r"how to (?:say|pronounce)|"
            r"تلفظ|چطور\s*(?:بگویم|بگم)|چگونه\s*بگویم)\s*"
            r"(?:کلمه|the word|word)?\s*"
            r"[\"'‘’]?([^\"'‘’]*?)[\"'‘’]?\s*[?!.؟]*\s*$",
            lowered, re.IGNORECASE,
        )
        if m:
            word = m.group(1).strip()
            word = re.sub(r"^(?:the\s+|word\s+|کلمه\s+|این\s+کلمه\s+)", "",
                          word, flags=re.IGNORECASE).strip()
        else:
            # a Persian request: take the Persian token as the target
            if not re.search(r"(تلفظ|چطور\s*(?:بگویم|بگم)|چگونه\s*بگویم)",
                             text):
                return None
            fa = re.search(r"[\u0600-\u06FF]{2,20}", text)
            if not fa:
                return None
            word = fa.group(0)

        tokens = [w for w in word.split() if w]
        if not tokens or all(w.lower() in LOOKUP_STOPWORDS or
                             w.lower() in ("word", "words", "this", "that", "it")
                             for w in tokens):
            return (
                "🗣  Give me the word and I'll help you say it.\n"
                "   ↲ کلمه را بگو تا با هم تلفظش کنیم.\n"
                "   Try: 'how do you pronounce hospital'"
            )

        key = normalize_word(word)
        entries = self.lookup_word(key)
        if entries:
            _, en, fa = entries[0]
            lines = [f"🗣  {en}  —  {fa}",
                     f"   Say it slowly: {en[0].upper()} · {' · '.join(en[1:])}",
                     f"   Stress: {mark_stress(en)} — the capital part carries "
                     f"the beat"]
            note = first_sound_note(en)
            if note:
                lines.append(f"   Tip: {note}.")
            lines.append("   ↲ For the full guide ask: 'phonetics'")
            return "\n".join(lines)

        phrase = self.lookup_phrase(key)
        if phrase:
            lines = [f"🗣  “{phrase['en']}”",
                     f"   ↲ {phrase['fa']}",
                     *([f"   Say it slowly: {' · '.join(phrase['en'])}"]
                       if len(phrase["en"]) <= 24 else []),
                     "   ↲ For the full guide ask: 'phonetics'"]
            return "\n".join(lines)

        # Not in the dictionary — say something useful instead of dropping the
        # learner's question on the floor.
        return (
            f"🗣  “{word}” is not in my vocabulary list yet, so I cannot give "
            f"you its Persian meaning.\n"
            f"   ↲ «{word}» هنوز در واژگان من نیست.\n"
            f"   Say it slowly: {' · '.join(word)} · stress: {mark_stress(key)}\n"
            f"   Ask 'idioms' or 'difference between {word} and ...' to look it "
            f"up from another angle."
        )

    # ------------------------------------------------------------------ #
    #  How much do you know? — a small, honest stat
    # ------------------------------------------------------------------ #
    def handle_stat(self, text: str, lowered: str, lang: str) -> str | None:
        if not re.search(r"how many (words|things|sentences|lessons)|"
                         r"what can you do|your (vocabulary|stats|abilities)|"
                         r"چند (کلمه|لغت|جمله)|چه کارهایی|توانایی|آمار|"
                         r"your vocabulary", lowered + " " + text):
            return None
        words = sum(len(d["words"]) for d in self.glossary.values())
        domains = len(self.glossary)
        topics = len(self.grammar)
        qs = sum(len(t.get("practice", [])) + len(t.get("exam", []))
                 for t in self.grammar.values())
        return (
            f"📊 What I know — چه چیزهایی می‌دانم:\n"
            f"   • Vocabulary: {to_persian_digits(words) if lang == 'fa' else words} "
            f"words in {to_persian_digits(domains) if lang == 'fa' else domains} domains "
            f"(A1 → C2)\n"
            f"   • Grammar: {to_persian_digits(topics) if lang == 'fa' else topics} lessons, "
            f"{to_persian_digits(qs) if lang == 'fa' else qs} exercises\n"
            f"   • Phrases: {len(self.phrases)} banks · Listening: {len(self.listening)} levels\n"
            f"   • Idioms: {sum(len(t['idioms']) for t in self.idioms.values())} · "
            f"Distinctions: {len(self.distinctions)} confusable pairs"
        )

    # ------------------------------------------------------------------ #
    #  Grammar (structure → function → examples → exercises)
    # ------------------------------------------------------------------ #
    def match_grammar_topic(self, text: str, lowered: str, lang: str):
        """Return the best-matching topic. Longer keywords win, so
        'present perfect continuous' doesn't get swallowed by 'present perfect'."""
        best = None
        best_len = -1
        for topic_id, topic in self.grammar.items():
            for kw in topic["keywords"].get(lang, []):
                if lang == "en":
                    hit = bool(re.search(rf"\b{re.escape(kw)}\b", lowered))
                    # "I have to go now" is a learner leaving, not a request for
                    # the modals lesson: a keyword that names a verb phrase
                    # stops naming the topic once a subject stands in front.
                    if hit and re.search(
                            rf"\b(?:i|you|we|they|he|she|it)\s+{re.escape(kw)}\b",
                            lowered):
                        hit = False
                else:
                    hit = kw in text
                if hit and len(kw) > best_len:
                    best, best_len = (topic_id, topic), len(kw)
        return best

    @staticmethod
    def wants_grammar_menu(text: str, lowered: str, lang: str) -> bool:
        if lang == "en":
            return any(re.search(rf"\b{kw}\b", lowered) for kw in ("grammar", "grammer"))
        return any(kw in text for kw in ("گرامر", "دستور زبان", "قواعد"))

    @staticmethod
    def wants_exercises(text: str, lowered: str, lang: str) -> bool:
        if lang == "en":
            return any(w in lowered for w in ("exercise", "practice", "quiz", "problem"))
        return any(w in text for w in ("تمرین", "تست"))

    def format_grammar_menu(self, lang: str) -> str:
        lines = []
        for topic in self.grammar.values():
            en, fa = topic["title"]["en"], topic["title"]["fa"]
            lines.append(f"• {en} / {fa}")
        if lang == "fa":
            return (
                "📗 موضوعات گرامر انگلیسی:\n" + "\n".join(lines) +
                "\n\nبرای دیدن درس بنویس: 'simple present' یا 'حال ساده'\n"
                "برای تمرین: 'تمرین حال ساده'"
            )
        return (
            "📗 English grammar topics:\n" + "\n".join(lines) +
            "\n\nAsk for a lesson: 'simple present'\n"
            "Practice it: 'simple present exercises'"
        )

    def format_topic(self, topic, lang: str, topic_id: str = "") -> str:
        """English grammar content first, with the Persian translation
        under each line (structure · function · examples)."""
        long = topic.get("title_long", topic["title"])
        head = f"📘 English Grammar — {long['en']} ({long['fa']})"
        parts = [head]

        parts.append("\n1️⃣ Structure / ساختار")
        parts.extend(f"• {s['en']}\n  ↲ {s['fa']}" for s in topic["structure"])
        if topic.get("tip"):
            parts.append(f"\n💡 Tip: {topic['tip']['en']}\n   ↲ {topic['tip']['fa']}")

        notes = topic.get("explain") or []
        if notes:
            parts.append("\n2️⃣ Explanation / توضیح")
            parts.extend(f"• {n['en']}\n  ↲ {n['fa']}" for n in notes)

        parts.append("\n3️⃣ Function / کاربرد")
        parts.extend(f"• {f['en']}\n  ↲ {f['fa']}" for f in topic["function"])

        parts.append("\n4️⃣ Examples / مثال‌ها")
        parts.extend(
            f"{i}. {e['en']}\n   ↲ {e['fa']}"
            for i, e in enumerate(topic["examples"], 1)
        )

        practice_n = len(topic.get("practice", []))
        exam_n = len(topic.get("exam", topic.get("exercises", [])))
        done = self._unlocked(topic_id)
        parts.append("\n5️⃣ Exercises / تمرین")
        if lang == "fa":
            p_s, e_s = to_persian_digits(practice_n), to_persian_digits(exam_n)
            parts.append(
                f"۱) تمرین: {p_s} سوال — بنویس: 'تمرین {topic['title']['fa']}'"
            )
            parts.append(
                f"۲) آزمون: {e_s} سوال (🔒 تا وقتی تمرین رو تموم کنی)"
                if not done else
                f"۲) آزمون: {e_s} سوال — بنویس: 'آزمون {topic['title']['fa']}'"
            )
        else:
            parts.append(f"1) Practice: {practice_n} questions — type: '{topic['title']['en'].lower()} exercises'")
            parts.append(
                f"2) Exam: {exam_n} questions 🔒 (finish the practice first)"
                if not done else
                f"2) Exam: {exam_n} questions — type: '{topic['title']['en'].lower()} exam'"
            )
        return "\n".join(parts)

    def _unlocked(self, topic_id: str) -> bool:
        return topic_id in self.practice_done

    def practice_unlocked(self, topic, lang: str) -> str:
        """Message shown when the practice stage is cleared and the exam opens."""
        exam_n = len(topic.get("exam", []))
        if lang == "fa":
            return (
                "✅ تمرین تمام شد! آزمون باز شد. 🎓\n"
                f"{'─' * 30}\n"
                f"{to_persian_digits(exam_n)} سوال باقی مانده — بنویس: 'آزمون {topic['title']['fa']}'\n"
                "هر پاسخ درست یک امتیاز. آخرش کارت نتیجه با سطح می‌گیری."
            )
        return (
            "✅ Practice complete! Your exam is now open. 🎓\n"
            f"{'─' * 30}\n"
            f"{exam_n} questions to go — type: '{topic['title']['en'].lower()} exam'\n"
            "Each correct answer scores a point; you'll get a graded result card at the end."
        )

    def practice_retry(self, topic, score: int, total: int, lang: str) -> str:
        """The practice is over but not perfect, so the exam stays shut."""
        if lang == "fa":
            s, t = to_persian_digits(score), to_persian_digits(total)
            return (
                f"🔒 تمرین تمام شد، ولی نمره‌ات {s} از {t} است.\n"
                f"{'─' * 30}\n"
                "آزمون فقط وقتی باز می‌شود که همه‌ی پاسخ‌ها درست باشند.\n"
                f"دوباره تلاش کن: 'تمرین {topic['title']['fa']}'"
            )
        return (
            f"🔒 Practice finished — {score}/{total} correct.\n"
            f"{'─' * 30}\n"
            "The exam opens only after a perfect run: every answer right.\n"
            f"Try again: '{topic['title']['en'].lower()} exercises'"
        )

    def format_exercise_card(self, topic, index: int, lang: str, stage: str = "practice") -> str:
        questions = topic.get("exam", []) if stage == "exam" else topic.get("practice", [])
        q = questions[index]
        total = len(questions)
        n = to_persian_digits(index + 1) if lang == "fa" else str(index + 1)
        total_s = to_persian_digits(total) if lang == "fa" else str(total)
        question = q["q"].get(lang, q["q"]["en"])
        if lang == "fa":
            head = "🎓 آزمون" if stage == "exam" else "✏️ تمرین"
            hint = "پاسخ خودت رو بنویس. ('جواب' برای دیدن جواب، 'گرامر' برای خروج)"
            return f"{head} {n} از {total_s}\n{question}\n{hint}"
        head = "🎓 Exam" if stage == "exam" else "✏️ Practice"
        hint = "Type your answer. ('show answer' to reveal it, 'grammar' to exit)"
        return f"{head} {n}/{total_s}\n{question}\n{hint}"

    @staticmethod
    def norm_answer(s: str) -> str:
        """Normalise an exercise answer: lowercase, drop punctuation and
        apostrophes (so "wasn't" == "wasnt"), collapse whitespace."""
        s = s.lower().replace("’", "'").replace("‘", "'")
        s = re.sub(r"['`]", "", s)  # wasn't -> wasnt, don't -> dont
        s = re.sub(r"[^\w\s]", " ", s, flags=re.UNICODE)
        return re.sub(r"\s+", " ", s).strip()

    @staticmethod
    def answer_matches(guess: str, expected: list[str]) -> bool:
        """Compare an answer to the accepted ones. Multi-blank questions are
        matched on the *set* of words, so word order doesn't matter."""
        if guess in expected:
            return True
        g = set(guess.split())
        return any(set(e.split()) == g for e in expected if len(e.split()) > 1)

    def wants_exam(self, text: str, lowered: str, lang: str) -> bool:
        if lang == "en":
            return any(w in lowered for w in ("exam", "test", "final test"))
        return any(w in text for w in ("آزمون", "امتحان", "تست نهایی"))

    @staticmethod
    def _example_answers(topic: dict) -> list[str]:
        """The taught forms inside a lesson's examples, for 'show answer'.

        Each example is written as 'He **goes** to work.' so the bolded span
        is the answer; if an example has no bold, the whole line is offered.
        """
        out = []
        for row in topic.get("examples", [])[:4]:
            en = row.get("en", "")
            bold = re.findall(r"\*\*(.+?)\*\*", en)
            if bold:
                out.append(" / ".join(bold))
            elif en:
                out.append(en.rstrip("."))
        return out

    def start_grammar_session(self, topic_id: str, stage: str,
                              lang: str) -> str:
        """Open the practice or the exam for a topic the learner has opened.

        Both the named route ("simple present exercises") and the bare route
        ("exercises" after reading that lesson) come through here, so the
        practice→exam gate can never be bypassed by the shorter path.
        """
        topic = self.grammar[topic_id]
        self.last_lesson = topic_id
        if stage == "exam":
            if topic_id not in self.practice_done:
                n = (to_persian_digits(len(topic.get("practice", [])))
                     if lang == "fa" else str(len(topic.get("practice", []))))
                title = topic["title"]["fa"] if lang == "fa" else topic["title"]["en"]
                return (
                    f"🔒 آزمون قفل است — اول تمرین ({n} سوال) را کامل کن.\n"
                    f"بنویس: 'تمرین {title}'"
                    if lang == "fa" else
                    f"🔒 The exam is locked — finish the practice first ({n} questions).\n"
                    f"Type: '{topic['title']['en'].lower()} exercises'"
                )
            intro = (f"🎓 شروع آزمون «{topic['title']['fa']}» — موفق باشی!\n"
                     if lang == "fa"
                     else f"🎓 Starting the '{topic['title']['en']}' exam — good luck!\n")
        else:
            intro = (f"✏️ شروع تمرین «{topic['title']['fa']}» — موفق باشی!\n"
                     if lang == "fa"
                     else f"✏️ Starting '{topic['title']['en']}' practice — good luck!\n")
        self.exercise = {"topic": topic_id, "index": 0, "lang": lang,
                         "stage": stage}
        self.exercise_score = 0
        return intro + self.format_exercise_card(topic, 0, lang, stage)

    def handle_grammar(self, text: str, lowered: str, lang: str) -> str | None:
        # A Persian question can name an English grammar term — "میشه present
        # perfect رو برام explain کنی؟" — so try the detected language first
        # and the other one after it. The lesson itself still renders in the
        # language of the question.
        found = (self.match_grammar_topic(text, lowered, lang)
                 or self.match_grammar_topic(text, lowered,
                                             "en" if lang == "fa" else "fa"))
        if found:
            topic_id, topic = found
            exam = self.wants_exam(text, lowered, lang)
            practice = self.wants_exercises(text, lowered, lang)

            if exam:
                return self.start_grammar_session(topic_id, "exam", lang)
            if practice:
                return self.start_grammar_session(topic_id, "practice", lang)
            # remember what they are reading, so "exercises" and
            # "show answer" work on the next message
            self.last_lesson = topic_id
            self.last_examples = self._example_answers(topic)
            return self.format_topic(topic, lang, topic_id)
        if self.wants_grammar_menu(text, lowered, lang):
            return self.format_grammar_menu(lang)
        return None

    # Words that end the current exercise session and fall through to normal chat
    EXIT_WORDS = (
        "bye", "goodbye", "exit", "quit", "stop", "cancel", "help", "joke",
        "menu", "thanks",
    )
    EXIT_WORDS_FA = ("خروج", "خداحافظ", "لغو", "متوقف", "توقف", "راهنما", "جوک", "مرسی")
    SHOW_WORDS = ("show answer", "answer", "skip", "next", "reveal", "solution")
    SHOW_WORDS_FA = ("جواب", "حل کن", "بعدی", "نشون بده", "رد شو")

    def looks_like_answer(self, text: str, lowered: str, lang: str) -> bool:
        """Is this message an attempt at the current exercise?

        Without this, anything typed mid-quiz ("what's the capital of
        France?") is rejected with "Not quite" instead of being answered.
        A question, or anything another handler recognises (intent, phrase
        bank, grammar topic, vocabulary domain), is clearly not an answer.
        """
        if "?" in text or "؟" in text:
            return False
        if self.match_phrase_topic(text, lowered):
            return False
        if self.match_grammar_topic(text, lowered, "en") or self.match_grammar_topic(
            text, lowered, "fa"
        ):
            return False
        if self.handle_domain_list(text, lowered, lang):
            return False
        if self.match_intent(text, lang):
            return False
        return True

    def is_show_command(self, text: str, lowered: str) -> bool:
        """True only for an explicit reveal request.

        Substring matching was too loose: "notananswer at all here" contains
        "answer" and used to reveal the solution.
        """
        stripped = re.sub(r"[.!?؟,;:\"'«»()\[\]]", "", lowered).strip()
        if not stripped:
            return False
        if stripped in self.SHOW_WORDS or stripped in self.SHOW_WORDS_FA:
            return True
        return any(
            stripped.startswith(w + " ") or stripped == w
            for w in ("show answer", "reveal answer", "show me", "help me answer")
        ) or any(stripped.startswith(w) for w in ("نشون بده", "جواب بده"))

    def is_exit_command(self, text: str, lowered: str) -> bool:
        """True when the message is a command to leave the exercise, rather
        than an attempt at the answer."""
        return bool(
            any(re.search(rf"\b{w}\b", lowered) for w in self.EXIT_WORDS)
            or any(w in text for w in self.EXIT_WORDS_FA)
        )

    def handle_exercise(self, text: str, lowered: str, lang: str) -> str | None:
        """If a grammar exercise session is active, treat the message as an answer.

        Rendering language follows the session's language (answers are English
        verbs even inside a Persian exercise), while exit/show hints are
        recognized in both languages.
        """
        if not self.exercise:
            return None

        topic_id = self.exercise["topic"]
        topic = self.grammar[topic_id]
        stage = self.exercise.get("stage", "practice")
        questions = topic.get("exam", []) if stage == "exam" else topic.get("practice", [])
        sess_lang = self.exercise.get("lang", lang)
        index = self.exercise["index"]
        question = questions[index]

        # A correct answer always wins — some legit answers ARE command words
        # ("cancel" is the answer to a phrasal-verb question, "stop" to another).
        guess = self.norm_answer(text)
        expected = [self.norm_answer(a) for a in question["a"]]
        if self.answer_matches(guess, expected):
            self.exercise_score += 1
            praise = (
                random.choice(["✅ آفرین!", "✅ درسته!", "✅ عالی!"])
                if sess_lang == "fa"
                else random.choice(["✅ Correct!", "✅ Well done!", "✅ Exactly!"])
            )
            return praise + "\n" + self._advance_exercise(topic, sess_lang, topic_id, stage)

        # Leaving the exercise: exit words (either language), or switching
        # to a grammar menu / another topic
        if self.is_exit_command(text, lowered):
            self.exercise = None
            # A real goodbye still deserves the farewell; anything else just
            # closes the practice instead of falling through to the glossary.
            if re.search(r"\b(bye|goodbye|خداحافظ)\b", lowered) or "خداحافظ" in text:
                return None
            # "tell me a joke" / "help" are exit words *and* real requests —
            # close the quiz but still answer them properly.
            if not self.looks_like_answer(text, lowered, lang):
                return None
            score = self.exercise_score
            self.exercise_score = 0
            return (
                f"📘 تمرین لغو شد — از {to_persian_digits(score)} پاسخ درست خوش آمدی! بنویس 'grammar' برای منو / type 'grammar' for the menu"
                if sess_lang == "fa"
                else f"📘 Practice closed — {score} correct answer(s). Type 'grammar' for the menu"
            )
        if (
            self.match_grammar_topic(text, lowered, "en")
            or self.match_grammar_topic(text, lowered, "fa")
            or self.wants_grammar_menu(text, lowered, "en")
            or self.wants_grammar_menu(text, lowered, "fa")
        ):
            self.exercise = None
            return None

        # Reveal / skip (either language)
        reveal = self.is_show_command(text, lowered)
        if not reveal:
            # Only treat it as a wrong answer if it reads like one; otherwise
            # let the normal handlers answer it and keep the quiz open.
            if not self.looks_like_answer(text, lowered, lang):
                return None
            if sess_lang == "fa":
                return "❌ نه، درست نیست. دوباره امتحان کن — یا بنویس 'جواب'."
            return "❌ Not quite. Try again — or type 'show answer'."

        # Reveal the answer, then advance
        answer = " / ".join(question["a"])
        reveal_msg = f"💡 جواب: {answer}" if sess_lang == "fa" else f"💡 Answer: {answer}"
        return reveal_msg + "\n" + self._advance_exercise(topic, sess_lang, topic_id, stage)

    def _advance_exercise(self, topic, lang: str, topic_id: str, stage: str = "practice") -> str:
        self.exercise["index"] += 1
        index = self.exercise["index"]
        questions = topic.get("exam", []) if stage == "exam" else topic.get("practice", [])
        if index >= len(questions):
            total = len(questions)
            score = self.exercise_score
            self.exercise = None
            if stage == "practice":
                # The gate is real: a reveal or a retry leaves the score short
                # and the exam closed. Only a clean run opens it.
                if score < total:
                    return self.practice_retry(topic, score, total, lang)
                self.practice_done.add(topic_id)
                return self.practice_unlocked(topic, lang)
            return self.format_score_report(topic, score, total, lang, stage)
        return self.format_exercise_card(topic, index, lang, stage)

    # Score bands — each result gets its own "theme"
    SCORE_BANDS = (
        (90, "🌟", "Excellent", "عالی",
         "Outstanding — this grammar is yours. / فوق‌العاده — این گرامر مال توئه."),
        (75, "🌿", "Very good", "خیلی خوب",
         "Strong and accurate. / قوی و دقیق."),
        (60, "💧", "Good", "خوب",
         "Solid, with a few slips to polish. / خوب، فقط چند نکته برای صیقل."),
        (40, "🔥", "Almost there", "نزدیک شدی",
         "You have the idea — another round will lock it in. / ایده رو داری — یه دور دیگه کاملش می‌کنه."),
        (0, "🌱", "Keep going", "ادامه بده",
         "Every expert started here. Read the lesson again and retry. / هر متخصصی از همین‌جا شروع کرد."),
    )

    def format_score_report(self, topic, score: int, total: int, lang: str, stage: str = "exam") -> str:
        """A proper end-of-quiz report: score, band, breakdown and next step."""
        pct = round(score / total * 100) if total else 0
        for cut, icon, en, fa, note in self.SCORE_BANDS:
            if pct >= cut:
                break
        bar_len = 20
        filled = max(0, min(bar_len, round(pct / 100 * bar_len)))
        bar = "█" * filled + "░" * (bar_len - filled)

        if lang == "fa":
            pct_s = to_persian_digits(pct)
            score_s = to_persian_digits(score)
            total_s = to_persian_digits(total)
            pct_sign = "٪"
            head = f"{icon} نتیجه آزمون — {topic['title']['fa']}"
            return (
                f"{head}\n"
                f"{'─' * 34}\n"
                f"امتیاز:  {score_s} / {total_s}   ({pct_s}{pct_sign})\n"
                f"{bar}\n"
                f"سطح: {fa}\n"
                f"{note}\n"
                f"برای درس برگرد: 'گرامر' — یا دوباره: 'آزمون {topic['title']['fa']}'"
            )
        head = f"{icon} Exam result — {topic['title']['en']}"
        return (
            f"{head}\n"
            f"{'─' * 34}\n"
            f"Score:   {score}/{total}   ({pct}%)\n"
            f"{bar}\n"
            f"Level:   {en}\n"
            f"{note}\n"
            f"Back to lessons: 'grammar' — or retry: '{topic['title']['en'].lower()} exam'"
        )

    # ------------------------------------------------------------------ #
    #  Jokes (bilingual library from jokes.json)
    # ------------------------------------------------------------------ #
    def _joke_matches(self, joke, text: str, lowered: str) -> bool:
        for kw in joke.get("keywords", []):
            if any("\u0600" <= c <= "\u06FF" for c in kw):
                if kw in text:
                    return True
            elif re.search(rf"\b{re.escape(kw)}\b", lowered):
                return True
        return False

    def tell_joke(self, text: str, lang: str) -> str:
        """Pick a random joke, filtered by category keywords when given."""
        if not self.jokes:
            # fall back to the small inline list in memory.json
            joke_intent = next((i for i in self.intents if i["name"] == "joke"), None)
            if joke_intent:
                responses = joke_intent["responses"]
                return random.choice(responses.get(lang) or responses["en"])
            return "😄"

        lowered = text.lower()
        candidates = [j for j in self.jokes if self._joke_matches(j, text, lowered)]
        if not candidates:
            candidates = self.jokes
        fresh = [j for j in candidates if j["id"] != self.last_joke_id]
        joke = random.choice(fresh or candidates)
        self.last_joke_id = joke["id"]

        if lang == "fa":
            setup = joke["translation"]["setup"]
            punchline = joke["translation"].get("punchline", "")
            category = joke.get("category_fa", joke["category"])
            parts = [f"😂 {setup}"]
            if punchline:
                parts.append(punchline)
            parts.append(f"🏷️ {category}")
            return "\n".join(parts)

        setup = joke["setup"]
        punchline = joke.get("punchline", "")
        parts = [f"😂 {setup}"]
        if punchline:
            parts.append(punchline)
        parts.append(f"🏷️ {joke['category']}")
        return "\n".join(parts)

    # ------------------------------------------------------------------ #
    # ------------------------------------------------------------------ #
    #  Everyday phrases (practical sentence banks from phrases.json)
    # ------------------------------------------------------------------ #
    def match_phrase_topic(self, text: str, lowered: str) -> tuple[str, dict] | None:
        """Match a phrase-bank topic. Phrases run before intent matching, so
        the keywords must stay specific enough not to swallow common requests
        like 'help' or 'where is the bank'."""
        norm_text = normalize_word(text)
        # "translate interview" asks for one word, and 'interview' is also a
        # keyword of the job-hunting bank. A message that names the lookup it
        # wants is a glossary request; a single-word keyword must not take it.
        lookup_ask = is_lookup_ask(text, lowered)
        for topic_id, topic in self.phrases.items():
            for lang in ("en", "fa"):
                for kw in topic["keywords"].get(lang, []):
                    if lang == "en":
                        if re.search(rf"\b{re.escape(kw)}\b", lowered):
                            if lookup_ask and " " not in kw.strip():
                                continue
                            return topic_id, topic
                    elif normalize_word(kw) in norm_text:
                        return topic_id, topic
        return None

    @staticmethod
    def format_phrase_topic(topic, lang: str) -> str:
        """English sentence first, Persian translation beneath it."""
        parts = [f"💬 {topic['title']['en']} ({topic['title']['fa']})"]
        for line in topic["phrases"]:
            parts.append(f"• {line['en']}\n  ↲ {line['fa']}")
        return "\n".join(parts)

    def handle_phrases(self, text: str, lowered: str, lang: str) -> str | None:
        found = self.match_phrase_topic(text, lowered)
        if found:
            topic_id, topic = found
            self.last_phrase = topic_id
            return self.format_phrase_topic(topic, lang)
        return None

    # ------------------------------------------------------------------ #
    #  Listening (CEFR A1-C2 sentences to hear read aloud)
    # ------------------------------------------------------------------ #
    def match_listening_level(self, text: str, lowered: str):
        for level in self.listening:
            lid = level["id"].lower()
            if re.search(rf"\b{lid}\b", lowered):
                return level
            if re.search(rf"(?:listen|speak|say|audio|voice)\s+{lid}\b", lowered):
                return level
        return None

    @staticmethod
    def format_listening_level(level) -> str:
        head = f"\U0001f3a7 {level['title']['en']} ({level['title']['fa']})"
        parts = [head, f"{level['blurb']['en']} / {level['blurb']['fa']}"]
        for i, s in enumerate(level["sentences"], 1):
            parts.append(f"{i}. {s['en']}\n   \u21b2 {s['fa']}")
        return "\n".join(parts)

    def handle_listening(self, text: str, lowered: str, lang: str) -> str | None:
        # "speak" and the Persian verb of asking are not listening words:
        # "speak english" is a switch request and "speak more slowly" is a
        # speed request, and the band list is the wrong answer for both. They
        # count only when a band is named with them — "speak A1", "B1 رو بگو" — or
        # "سطح b1 چیه" would come back as a listening lesson instead of the CEFR
        # explanation it asked for.
        level = self.match_listening_level(text, lowered)
        asked = bool(re.search(r"\b(listen|listening|audio|voice)\b", lowered)) \
            or any(w in text for w in ("گوش دادن", "آواز")) \
            or (level is not None
                and (re.search(r"\bspeak\b", lowered) or "بگو" in text))
        # a learner often just types the band itself: "A1", "b2", "C2"
        bare = re.fullmatch(r"\s*([abc][12])\s*[?!.؟]*\s*", lowered)
        if not asked and not bare:
            return None
        if level is None and bare:
            level = self.match_listening_level(bare.group(1), bare.group(1))
        if level:
            self.last_level = level
            return self.format_listening_level(level)
        if asked or bare:
            names = " · ".join(l["title"]["en"].split(" · ")[0] for l in self.listening)
            return (
                f"\U0001f3a7 Listening levels — سطح شنیدن: {names}\n"
                "Ask: 'listen A1' or 'گوش دادن A1'"
            )
        return None

    # ------------------------------------------------------------------ #
    #  Daily English — one word, one expression, one conversation a day
    # ------------------------------------------------------------------ #
    def daily_key(self, date_key: str | None = None) -> str:
        """The local calendar date the rotation is on, as YYYY-MM-DD."""
        return date_key or self.today or datetime.now().date().isoformat()

    def daily_selection(self, date_key: str | None = None) -> dict:
        """Today's three items. Selection is a pure function of the date, so
        the CLI, the web preview and the offline APK all show the same card."""
        key = self.daily_key(date_key)
        day = daily_day_number(key)
        picked = {"date": key, "version": self.daily.get("version", 1)}
        for name, salt in DAILY_SALTS.items():
            rows = self.daily.get(name) or []
            picked[name] = rows[daily_index(day, len(rows), salt)] if rows else None
        return picked

    @staticmethod
    def _examples_block(entry: dict, lang: str, head: str) -> list[str]:
        lines = [head]
        for i, ex in enumerate(entry.get("examples", []), 1):
            lines.append(f"   {i}. {ex['en']}")
            lines.append(f"      ↲ {ex['fa']}")
        return lines

    def format_daily_word(self, entry: dict, lang: str) -> str:
        head = ("\U0001f4c5  Word of the Day — لغت امروز" if lang == "en"
                else "\U0001f4c5  لغت امروز — Word of the Day")
        lines = [head, ""]
        lines.append(f"  {entry['en']}   {entry.get('ipa', '')}".rstrip())
        meta = " · ".join(x for x in (entry.get("pos", ""), entry.get("level", ""))
                          if x)
        if meta:
            lines.append(f"  {meta}")
        lines.append(f"  ↲ {entry['fa']}")
        definition = entry.get("def") or {}
        if definition:
            lines.append(f"  {definition.get('en', '')}")
            lines.append(f"  ↲ {definition.get('fa', '')}")
        lines.append("")
        lines += self._examples_block(
            entry, lang,
            "  Examples — مثال‌ها:" if lang == "en" else "  مثال‌ها — Examples:")
        if entry.get("syn"):
            lines.append("  Synonyms — مترادف: " + " · ".join(entry["syn"]))
        if entry.get("ant"):
            lines.append("  Antonyms — متضاد: " + " · ".join(entry["ant"]))
        return "\n".join(lines)

    def format_daily_expression(self, entry: dict, lang: str,
                               examples_only: bool = False) -> str:
        head = ("\U0001f4c5  Expression of the Day — عبارت امروز" if lang == "en"
                else "\U0001f4c5  عبارت امروز — Expression of the Day")
        meta = " · ".join(x for x in (entry.get("register", ""),
                                      entry.get("level", "")) if x)
        lines = [head, ""]
        lines.append(f"  “{entry['en']}”")
        lines.append(f"  ↲ {entry['fa']}")
        if meta:
            lines.append(f"  {meta}")
        if not examples_only:
            for field, label in (("use", "Means"), ("when", "When")):
                body = entry.get(field) or {}
                if body:
                    lines.append("")
                    lines.append(f"  {label}: {body.get('en', '')}")
                    lines.append(f"  ↲ {body.get('fa', '')}")
        lines.append("")
        lines += self._examples_block(
            entry, lang,
            "  Examples — مثال‌ها:" if lang == "en" else "  مثال‌ها — Examples:")
        alt = entry.get("alt") or {}
        if alt:
            lines.append("")
            lines.append(f"  Also say: “{alt.get('en', '')}”")
            lines.append(f"  ↲ {alt.get('fa', '')}")
        return "\n".join(lines)

    def format_daily_conversation(self, entry: dict, lang: str) -> str:
        head = ("\U0001f4c5  Conversation of the Day — مکالمه امروز" if lang == "en"
                else "\U0001f4c5  مکالمه امروز — Conversation of the Day")
        topic = entry.get("topic") or {}
        setting = entry.get("setting") or {}
        lines = [head, ""]
        lines.append(f"  {topic.get('en', '')} — {topic.get('fa', '')}"
                     f"   ({entry.get('level', '')})")
        if setting:
            lines.append(f"  {setting.get('en', '')}")
            lines.append(f"  ↲ {setting.get('fa', '')}")
        lines.append("")
        for turn in entry.get("turns", []):
            lines.append(f"  {turn['who']}: {turn['en']}")
            lines.append(f"      ↲ {turn['fa']}")
        if entry.get("key"):
            lines.append("")
            lines.append("  Useful phrases — عبارت‌های کلیدی:" if lang == "en"
                         else "  عبارت‌های کلیدی — Useful phrases:")
            for row in entry["key"]:
                lines.append(f"   • {row['en']}  —  {row['fa']}")
        for note in entry.get("notes", []):
            lines.append(f"  ↲ {note['en']}")
            lines.append(f"    ↲ {note['fa']}")
        lines.append("")
        lines.append("  Practice it: ‘practice today's conversation’" if lang == "en"
                     else "  تمرینش کن: «مکالمه امروز رو باهام تمرین کن»")
        return "\n".join(lines)

    def format_daily_digest(self, picked: dict, lang: str) -> str:
        """All three at once, which is what the panel shows as three cards."""
        head = ("\U0001f4c5  Today's English — انگلیسی امروز" if lang == "en"
                else "\U0001f4c5  انگلیسی امروز — Today's English")
        parts = [head, f"  {picked['date']}", ""]
        word = picked.get("words")
        if word:
            parts.append(f"\U0001f9e0  {word['en']}  {word.get('ipa', '')}  —  {word['fa']}")
        expr = picked.get("expressions")
        if expr:
            parts.append(f"\U0001f5e3  “{expr['en']}”  —  {expr['fa']}")
        conv = picked.get("conversations")
        if conv:
            topic = conv.get("topic") or {}
            parts.append(f"\U0001f4ac  {topic.get('en', '')}  —  {topic.get('fa', '')}"
                         f"   ({conv.get('level', '')})")
        parts.append("")
        if lang == "en":
            parts.append("Ask: ‘explain today's word’, ‘today's expression’, "
                         "‘today's conversation’")
            parts.append("   ↲ بپرس: «لغت امروز»، «عبارت امروز»، «مکالمه امروز»")
        else:
            parts.append("بپرس: «لغت امروز»، «عبارت امروز»، «مکالمه امروز»")
            parts.append("   ↲ Or in English: today's word / expression / conversation")
        return "\n".join(parts)

    def wants_daily(self, text: str, lowered: str) -> str | None:
        """Which daily item the message asks for: word | expression |
        conversation | all, or None when it is not a daily request."""
        if DAILY_WORD_RE.search(lowered) or any(w in text for w in DAILY_WORD_FA):
            return "word"
        if DAILY_EXPRESSION_RE.search(lowered) or any(w in text for w in DAILY_EXPRESSION_FA):
            return "expression"
        if DAILY_CONVERSATION_RE.search(lowered) or any(w in text for w in DAILY_CONVERSATION_FA):
            return "conversation"
        if DAILY_ANY_RE.search(lowered) or any(w in text for w in DAILY_ANY_FA):
            return "all"
        return None

    def handle_daily(self, text: str, lowered: str, lang: str) -> str | None:
        which = self.wants_daily(text, lowered)
        if not which:
            return None
        picked = self.daily_selection()
        wants_practice = any(w in lowered for w in PRACTICE_ASK) \
            or any(w in text for w in PRACTICE_ASK)
        wants_more = any(w in lowered for w in EXAMPLES_ASK) \
            or any(w in text for w in EXAMPLES_ASK)
        if which == "word" and picked.get("words"):
            return self.format_daily_word(picked["words"], lang)
        if which == "expression" and picked.get("expressions"):
            return self.format_daily_expression(picked["expressions"], lang,
                                                examples_only=wants_more)
        if which == "conversation" and picked.get("conversations"):
            if wants_practice:
                return self.start_daily_practice(picked["conversations"], lang)
            return self.format_daily_conversation(picked["conversations"], lang)
        if not any(picked.get(k) for k in DAILY_SALTS):
            return ("The daily catalogue is empty. / کاتالوگ روزانه خالی است.")
        return self.format_daily_digest(picked, lang)

    def start_daily_practice(self, entry: dict, lang: str) -> str:
        """Walk the dialogue: the bot says a line, the learner says the next."""
        turns = entry.get("turns") or []
        if len(turns) < 2:
            self.daily_practice = None
            return self.format_daily_conversation(entry, lang)
        self.daily_practice = {"id": entry["id"], "turn": 1, "right": 0,
                               "said": 0}
        topic = entry.get("topic") or {}
        head = ("\U0001f5e3  Practice — تمرین مکالمه" if lang == "en"
                else "\U0001f5e3  تمرین مکالمه — Practice")
        first, mine = turns[0], turns[1]
        return "\n".join([
            head, "",
            f"  {topic.get('en', '')} — {topic.get('fa', '')}",
            "",
            f"  {first['who']}: {first['en']}",
            f"      ↲ {first['fa']}",
            "",
            f"  Your line — {mine['who']} چه می‌گوید؟" if lang == "fa"
            else f"  Your line — what does {mine['who']} say?",
            "  (say ‘stop’ to leave / برای خروج بنویس «متوقف»)",
        ])

    def handle_daily_practice(self, text: str, lowered: str,
                              lang: str) -> str | None:
        """The active conversation drill owns the next message, the way an
        active grammar exercise does."""
        if not self.daily_practice:
            return None
        session = self.daily_practice
        entry = next((c for c in self.daily.get("conversations", [])
                      if c.get("id") == session["id"]), None)
        if entry is None:
            self.daily_practice = None
            return None
        if lowered.strip() in self.EXIT_WORDS \
                or any(w in text for w in self.EXIT_WORDS_FA):
            self.daily_practice = None
            return ("\U0001f44d Practice ended. / تمرین تمام شد." if lang == "en"
                    else "\U0001f44d تمرین تمام شد. / Practice ended.")
        # A new daily question leaves the drill rather than being graded as an
        # answer to the line on screen: somebody reading the cards can ask
        # "لغت امروز" half way through the dialogue, and "not quite" is the
        # wrong answer to a question.
        if self.wants_daily(text, lowered):
            self.daily_practice = None
            return None
        turns = entry.get("turns") or []
        index = session["turn"]
        if index >= len(turns):
            self.daily_practice = None
            return None
        expected = turns[index]["en"]
        session["said"] += 1
        lines = []
        if same_spoken(text, expected):
            session["right"] += 1
            lines.append("\u2705 Well said — آفرین." if lang == "en"
                         else "\u2705 آفرین — well said.")
        else:
            lines.append("\u274c Not quite — نه دقیقاً. "
                         f"{turns[index]['who']}: {expected}"
                         if lang == "en" else
                         "\u274c نه دقیقاً — not quite. "
                         f"{turns[index]['who']}: {expected}")
            lines.append(f"      ↲ {turns[index]['fa']}")
        follow = index + 1
        if follow + 1 < len(turns):
            session["turn"] = follow + 1
            lines += [
                "",
                f"  {turns[follow]['who']}: {turns[follow]['en']}",
                f"      ↲ {turns[follow]['fa']}",
                "",
                (f"  Your line — {turns[follow + 1]['who']} چه می‌گوید؟"
                 if lang == "fa" else
                 f"  Your line — what does {turns[follow + 1]['who']} say?"),
            ]
        else:
            self.daily_practice = None
            done = f"{session['right']}/{session['said']}"
            lines += ["",
                      "\U0001f389 Conversation complete — مکالمه تمام شد." if lang == "en"
                      else "\U0001f389 مکالمه تمام شد — conversation complete.",
                      f"  Lines said back: {done}"]
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    #  Glossary (vocabulary domains + word lookup)
    # ------------------------------------------------------------------ #
    def handle_domain_list(self, text: str, lowered: str, lang: str) -> str | None:
        """If the user asks for a vocabulary domain, list it bilingually."""
        norm_text = normalize_word(text)
        for dom_id, dom in self.glossary.items():
            for kw in dom["keywords"].get(lang, []):
                key = normalize_word(kw)
                if lang == "en":
                    matched = re.search(rf"\b{re.escape(kw)}(?:s|es)?\b", lowered)
                else:
                    # Order-independent: every content token of the keyword
                    # must appear somewhere in the query, so "هتل کلمات"
                    # matches the keyword "کلمات هتل" regardless of word order.
                    # normalize_word() collapses spaces, so tokenize the raw
                    # lowered text instead.
                    clean = re.sub(r"[.!?،،;:\"«»()\[\]]", " ", lowered)
                    text_toks = [t for t in clean.split() if t]
                    kw_toks = [t for t in kw.split() if t]
                    matched = bool(kw_toks) and all(t in text_toks for t in kw_toks)
                if matched:
                    return self.format_domain(dom, lang)
        return None

    @staticmethod
    def format_domain(dom, lang: str) -> str:
        words = dom["words"]
        list_label = dom["list_label"][lang]
        count = to_persian_digits(len(words)) if lang == "fa" else str(len(words))
        lines = [f"{list_label} ({count}):" if lang == "fa" else f"{list_label} ({count}):"]
        for w in words:
            en, fa = w[0], w[1]
            lines.append(f"{fa} — {en}" if lang == "fa" else f"{en} — {fa}")
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    #  Dictionary asks the glossary never answered
    # ------------------------------------------------------------------ #
    def extract_lookup_target(self, text: str, lang: str) -> str | None:
        """The word a lookup question is about, in either language."""
        if lang == "fa":
            patterns = FA_LOOKUP_PATTERNS + EN_LOOKUP_PATTERNS
        else:
            patterns = EN_LOOKUP_PATTERNS + FA_LOOKUP_PATTERNS
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                target = match.group("t").strip(" .?!؟،,;:\"'«»()[]").strip()
                if target:
                    return target
        return None

    @staticmethod
    def _lex_target(text: str, patterns) -> str | None:
        """The word after a trigger phrase, with the question trimmed off."""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if not match:
                continue
            target = match.group("t").strip(" .?!؟،,;:\"'«»()[]")
            for _ in range(3):
                trimmed = LEX_TARGET_TRIM.sub("", target).strip()
                if trimmed == target:
                    break
                target = trimmed
            if target:
                return target
        return None

    def _lex_resolve(self, target: str):
        """(asked, head, entry) for a target, falling back to its last word.

        "مترادف کلمه beautiful رو بگو" leaves a target with Persian furniture
        around it, so the words are tried from the end, where the English one
        is.
        """
        for candidate in [target] + list(reversed(target.split())):
            found = self.lex_find(candidate)
            if found:
                head, entry = found
                return candidate, head, entry
        return None

    def lex_or_not_found(self, word: str, lang: str) -> str:
        """A word the glossary does not hold: try the dictionary, then say so."""
        found = self.lex_find(word)
        if found:
            head, entry = found
            return self.format_lex_entry(head, entry, word, lang)
        if detect_lang(word) == "fa":
            heads = self.lex_persian(word)
            if heads:
                found = self.lex_find(heads[0])
                if found:
                    head, entry = found
                    return self.format_lex_entry(head, entry, word, lang)
        near = self.lex_near(word)
        if near:
            found = self.lex_find(near[0])
            if found:
                head, entry = found
                if lang == "fa":
                    lead = f"🤔 «{word}» را ندارم — منظورت **{head}** بود؟"
                else:
                    lead = (f'🤔 I don\'t have "{word}" — did you mean '
                            f'**{head}**?')
                return lead + "\n" + self.format_lex_entry(head, entry, head, lang)
        return self.not_found_msg(word, lang)

    def handle_lexicon(self, text: str, lowered: str, lang: str) -> str | None:
        """Synonyms, opposites, forms, and a word read in its sentence."""
        # 0) the word in a sentence: "examples with achieve"
        target = self._lex_target(text, LEX_EXAMPLE_PATTERNS)
        if target:
            resolved = self._lex_resolve(target)
            if resolved:
                _asked, head, entry = resolved
                return self.format_lex_examples(head, entry, lang)
        # 1) a form of the word: "past tense of seek"
        for pattern, form_type in LEX_FORM_ASKS:
            if not pattern.search(text):
                continue
            target = self._lex_target(text, LEX_FORM_PATTERNS.get(form_type, []))
            resolved = self._lex_resolve(target) if target else None
            if not resolved:
                continue
            _asked, head, entry = resolved
            return self.format_lex_forms(head, entry, lang, only=form_type)
        # 2) every form the dictionary holds
        if LEX_FORMS_RE.search(text) or "صورت‌های" in text:
            target = self._lex_target(text, [r"forms? of\s+(?P<t>.+)",
                                             r"inflections? of\s+(?P<t>.+)"])
            resolved = self._lex_resolve(target) if target else None
            if resolved:
                _asked, head, entry = resolved
                return self.format_lex_forms(head, entry, lang)
        # 3) synonyms and opposites
        for patterns, kind, marker, marker_fa in (
                (LEX_SYN_PATTERNS, "y", LEX_SYNONYMS_RE, LEX_SYNONYMS_FA),
                (LEX_ANT_PATTERNS, "a", LEX_ANTONYMS_RE, LEX_ANTONYMS_FA)):
            asked_now = marker.search(text) or any(w in text for w in marker_fa)
            if not asked_now:
                continue
            target = self._lex_target(text, patterns)
            resolved = self._lex_resolve(target) if target else None
            if resolved:
                _asked, head, entry = resolved
                return self.format_lex_relations(head, entry, lang, kind)
        # 4) "what does bank mean in river bank" - a sentence picks the sense
        if is_lookup_ask(text, lowered):
            context = LEX_CONTEXT_RE.search(text)
            target = self.extract_lookup_target(text, lang)
            if context and target and len(target.split()) == 1:
                found = self.lex_find(target)
                if found and len(found[1].get("s") or []) > 1:
                    head, entry = found
                    # The word itself is not context: "run" appears inside the
                    # gloss "cut and run", which used to make a sentence about
                    # a business match the fleeing sense.
                    tokens = (set(re.findall(r"[a-z']{2,}",
                                             context.group(1).lower()))
                              - LEX_STOP - {normalize_word(target)})
                    if tokens:
                        return self.format_lex_entry(head, entry, target, lang,
                                                     context=tokens,
                                                     context_text=context.group(1))
        return None

    def handle_glossary_lookup(self, text: str, lang: str) -> str | None:
        """Translate/define a word: 'translate apple', 'سیب به انگلیسی', ..."""
        # Philosophy, not vocabulary: otherwise "meaning of life" becomes a
        # failed lookup for the word "life".
        if re.search(r"\b(?:meaning|purpose) of life\b", text, re.IGNORECASE):
            return None
        # "reply in english" is a request about the reply, not a lookup for the
        # word "reply" — the "<X> in <language>" pattern would otherwise
        # translate it. The language-switch intents own this phrasing.
        if SWITCH_ASK_RE.search(text):
            return None
        target = None
        # Try the natural patterns for the detected language first,
        # then fall back to the other set (handles mixed-language text
        # like "what does خوشحال mean")
        if lang == "fa":
            patterns = FA_LOOKUP_PATTERNS + EN_LOOKUP_PATTERNS
        else:
            patterns = EN_LOOKUP_PATTERNS + FA_LOOKUP_PATTERNS
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                target = match.group("t").strip()
                break
        if not target:
            return None
        target = target.strip(" .?!؟،,;:\"'«»()[]").strip()
        if not target or normalize_word(target) in LOOKUP_STOPWORDS:
            return None

        if (DEFINITION_ASK_RE.search(text) or "معنی" in text) \
                and len(target.split()) == 1 and detect_lang(target) != "fa":
            found = self.lex_find(target)
            if found:
                head, entry = found
                return self.format_lex_entry(head, entry, target, lang)

        entries = self.lookup_word(target)
        if not entries:
            # Multi-word targets are probably not vocab lookups at all
            # ("help me in english") → let the intent matcher handle them
            if len(target.split()) > 1:
                return None
            # The glossary is the curated core; the dictionary behind it covers
            # the rest of English, including the typo suggestion at the end.
            return self.lex_or_not_found(target, lang)
        return self.format_lookup(target, entries, lang)

    def _suggest_words(self, target: str, limit: int = 3) -> list[str]:
        """Close glossary words for a typo. Deterministic in Python and JS."""
        key = normalize_word(target)
        if not key:
            return []
        target_fa = detect_lang(target) == "fa"
        pool = self.glossary_fa if target_fa else self.glossary_en
        max_dist = 1 if len(key) <= 5 else 2
        found = []
        for normalized, entries in pool.items():
            if not normalized or abs(len(normalized) - len(key)) > max_dist:
                continue
            dist = edit_distance(key, normalized)
            if not dist or dist > max_dist:
                continue
            for entry in entries:
                display = entry[2] if target_fa else entry[1]
                # "aple" should lead to "apple", not the phrase "a pile".
                if display and (" " in target or " " not in display):
                    found.append((dist, " " in display, display.lower(), display))
        found.sort()
        out, seen = [], set()
        for _, _, folded, display in found:
            if folded in seen:
                continue
            seen.add(folded)
            out.append(display)
            if len(out) == limit:
                break
        return out

    def not_found_msg(self, target: str, lang: str) -> str:
        suggestions = self._suggest_words(target)
        if lang == "fa":
            if suggestions:
                names = "، ".join(f"«{s}»" for s in suggestions)
                hint = f"منظورت {names} بود؟"
                example = f" این‌طور بپرس: «معنی {suggestions[0]} چیه»."
            else:
                hint = ("شکل ساده کلمه را امتحان کن (مثلاً go به‌جای went) "
                        "یا یک دامنه بپرس: رنگ‌ها، حیوانات، میوه‌ها.")
                example = ""
            return f"«{target}» توی واژه‌نامه من نیست 📚\n   ↲ {hint}{example}"
        if suggestions:
            names = ", ".join(f'"{s}"' for s in suggestions)
            hint = f"Did you mean {names}?"
            example = f" Ask: 'translate {suggestions[0]}'."
        else:
            hint = ("Try the base form (e.g. 'go', not 'went'), or ask for a "
                    "domain: colors, animals, fruits, numbers.")
            example = ""
        return f"I don't have \"{target}\" in my glossary yet 📚\n   ↲ {hint}{example}"

    def format_lookup(self, target: str, entries, lang: str) -> str:
        dom_id, en, fa = entries[0]
        label = self.glossary[dom_id]["label"]
        if lang == "fa":
            extra = (
                f" — چند معنی دیگر: {', '.join(e[1] + '، ' + e[2] for e in entries[1:3])}"
                if len(entries) > 1 else ""
            )
            return f"«{target}» → {en} / {fa} ({label['fa']} / {label['en']}){extra}"
        extra = (
            f" — also: {', '.join(e[1] + ' (' + e[2] + ')' for e in entries[1:3])}"
            if len(entries) > 1 else ""
        )
        return f'"{target}" → {fa}  ({label["en"]} / {label["fa"]}){extra}'

    # ------------------------------------------------------------------ #
    #  Core
    # ------------------------------------------------------------------ #
    # ------------------------------------------------------------------ #
    #  Register — the same idea at three levels of formality
    # ------------------------------------------------------------------ #
    def _reg_label(self, key: str) -> str:
        reg = (self.register.get("registers") or {}).get(key) or {}
        lab = reg.get("label") or {}
        return f"{lab.get('en', key)} / {lab.get('fa', key)}"

    def _reg_render_pair(self, pair: dict, only: str | None = None) -> str:
        """Render one pair at three registers, or just the one asked for."""
        keys = [only] if only in ("formal", "casual", "consultative") \
            else ["formal", "consultative", "casual"]
        out = [f"“{pair['meaning']['en']}” — {pair['meaning']['fa']}", ""]
        for k in keys:
            body = pair.get(k)
            if not body:
                continue
            out.append(f"{self._reg_label(k)}")
            out.append(f"  {body['en']}")
            out.append(f"  ↲ {body['fa']}")
            out.append("")
        if not only and pair.get("note"):
            out.append(f"↲ {pair['note']['en']}")
            out.append(f"↲ {pair['note']['fa']}")
        return "\n".join(out).rstrip()

    def _reg_match(self, thing: str) -> dict | None:
        """Find a pair by its meaning, in either language.

        Scored on character bigrams rather than whole words. Word overlap
        works in English and fails in Persian, where the inflected form of a
        word rarely matches the form used in the stored meaning - "دیر کردن"
        against "ببخشید دیر کردم" shares a stem but no token. Bigrams compare
        shape instead, and need no stemmer for either script.
        """
        t = re.sub(r"[^\w\s]", " ", thing.lower())
        t = re.sub(r"\s+", " ", t).strip()
        if len(t) < 2:
            return None

        def grams(text: str) -> set[str]:
            flat = text.replace(" ", "")
            return {flat[i:i + 2] for i in range(len(flat) - 1)}

        probe = grams(t)
        if not probe:
            return None
        probe_words = content_tokens(t)
        best, score = None, 0.0
        for pair in self.register.get("pairs", []):
            hay = (pair["meaning"]["en"] + " " + pair["meaning"]["fa"]).lower()
            if t in hay:
                s = 1.0
            else:
                target = grams(hay)
                shared = len(probe & target)
                s = shared / len(probe)
                if shared < 3:
                    s = 0.0          # too little signal to be a match
                # Bigrams alone match short courtesy phrases to unrelated
                # sentences ("thank you" vs "can you help me"). Require at
                # least one real content word in common for Latin text.
                if s and probe_words and not (probe_words & content_tokens(hay)):
                    s = 0.0
            if s > score:
                best, score = pair, s
        # 0.45 keeps "I need to leave early" matching "I have to leave early"
        # while "help me" does not drag in an unrelated pair.
        return best if score >= 0.45 else None

    def handle_register(self, text: str, lowered: str, lang: str) -> str | None:
        if not self.register:
            return None

        # a situation: "what do I say in a job interview"
        m = re.search(r"(?:\bin\b|\bat\b|\bduring\b|\bfor\b)\s+"
                      r"(?:a|an|the)?\s*([\w\s]{3,40}?)\s*[?.!]?$", lowered)
        if m and re.search(r"\b(interview|meeting|email|class|conference|"
                           r"restaurant|shop|doctor|manager|boss|professor)s?\b",
                           m.group(1)):
            asked = m.group(1).split()
            for sit in self.register.get("situations", []):
                blob = (sit["situation"]["en"] + " " + sit["situation"]["fa"]).lower()
                # "at a doctors appointment" has to reach "a visit to the
                # doctor": learners type the plural and the app stores the
                # singular.
                if any(v in blob for w in asked
                       for v in (w, re.sub(r"s$", "", w))):
                    return (f"“{sit['situation']['en']}” — {sit['situation']['fa']}\n"
                            f"→ {self._reg_label(sit['register'])}\n"
                            f"{sit['note']['en']}\n"
                            f"↲ {sit['note']['fa']}")
            return None

        # "how do I say <thing> formally / casually"
        m = re.search(r"(?:how (?:do|can|should) (?:i|you|we) say|how to say|how would you say|"
                      r"what (?:do|should) i say|چطور بگم|چطور بگویم|چی بگم)"
                      r"\s+(.+?)\s*"
                      r"(formally|informally|casually|polite|politely|official|"
                      r"رسمی|رسمیانه|خودمانی|محاوره|مؤدبانه)?\s*[?.!]*$", lowered)
        if m:
            thing = re.sub(r"\s+(formally|informally|casually|polite|politely|official|"
                           r"رسمی|رسمیانه|خودمانی|محاوره|مؤدبانه)$", "",
                           m.group(1).strip()).strip(" ?")
            tail = m.group(2) or ""
            only = None
            if tail in ("formally", "informally", "casually", "official",
                        "رسمی", "رسمیانه"):
                only = "casual" if tail in ("informally", "casually", "محاوره") \
                    else "formal"
            elif tail in ("polite", "politely", "مؤدبانه", "خودمانی"):
                only = "consultative" if tail != "خودمانی" else "casual"
            # A dictionary word or a stored phrase is a pronunciation
            # question, not a register request: "how do you say thank you".
            if not tail and (self.lookup_word(thing)
                             or self.lookup_phrase(normalize_word(thing))):
                return None
            pair = self._reg_match(thing)
            if pair:
                return self._reg_render_pair(pair, only)
            # Only claim the query when it actually named a register. "How do
            # you say a word" is a pronunciation question, and swallowing it
            # here took the stress marks with it.
            if not tail:
                return None
            available = ", ".join(f"*{p['meaning']['en']}*" for p in
                                  self.register.get("pairs", [])[:6])
            return (f'I do not have "{thing}" in the register list yet.\n'
                    f"I do have: {available}\n"
                    f"↲ هنوز این مورد را ندارم.")

        # a bare ask: register / formal vs casual / سطح رسمیت
        if re.search(r"\bregisters?\b|formal vs|formal or casual|"
                     r"سطح رسمیت|رسمی یا محاوره|محاوره یا رسمی", lowered):
            lines = ["**Register** — one meaning, three ways to say it. / "
                     "**سطح رسمیت** — یک معنا، سه راه برای گفتن.", ""]
            for c in self.register.get("channels", []):
                lines.append(f"• **{c['title']['en']}** — {c['blurb']['en']}")
                lines.append(f"  ↲ {c['title']['fa']}: {c['blurb']['fa']}")
            pairs = self.register.get("pairs", [])
            if pairs:
                lines.append("")
                lines.append("Try: " + ", ".join(
                    f"*{p['meaning']['en']}*" for p in pairs[:4]))
            return "\n".join(lines)

        return None

    def handle_life_meaning(self, text: str, lang: str) -> str | None:
        """Route the philosophical question before broad vocabulary keywords."""
        if not (re.search(r"\b(?:meaning|purpose) of life\b|\bwhy are we here\b",
                          text, re.IGNORECASE)
                or any(p in text for p in ("معنی زندگی", "هدف زندگی",
                                           "برای چی اومدیم"))):
            return None
        for intent in self.intents:
            if intent["name"] == "meaning":
                return self.reply_from_intent(intent, lang)
        return None

    def handle_vague_meaning(self, text: str, lang: str) -> str | None:
        """Ask which word the learner means instead of inventing an answer."""
        cleaned = re.sub(r"\s+", " ", text.strip())
        if not (VAGUE_MEANING_EN.match(cleaned)
                or VAGUE_MEANING_FA.match(cleaned)):
            return None
        if lang == "fa":
            return ("کدام کلمه یا جمله را می‌پرسید؟ این‌طور بنویسید: "
                    "«معنی <کلمه> چیه» یا «<کلمه> به انگلیسی» "
                    "تا معنی دقیق و مثال بدهم.")
        return ("Which word or sentence do you mean? Send it like this: "
                "\"define <word>\" or \"what does <word> mean\" — "
                "then I can give the exact meaning and an example.")

    def respond(self, user_input: str) -> str:
        text = user_input.strip()
        self.remember(text)
        if not text:
            return "Please say something 🙂 / یه چیزی بگو 🙂"

        lang = detect_lang(text)
        lowered = text.lower()

        # An active grammar exercise session takes priority: the next
        # message is treated as the answer to the current question
        exercise_reply = self.handle_exercise(text, lowered, lang)
        if exercise_reply is not None:
            return exercise_reply

        # ...and so does the conversation drill, for the same reason
        daily_drill = self.handle_daily_practice(text, lowered, lang)
        if daily_drill is not None:
            return daily_drill

        learned = self.learn_name(text)

        # Structured knowledge first
        section = self.handle_section(text, lowered, lang)
        if section is not None:
            return section

        followup = self.handle_followup(text, lowered, lang)
        if followup is not None:
            return followup

        # Daily English asks are specific phrases ("today's word"), so they can
        # sit this early without taking anything from the panels below - and
        # they must, because "conversation" and "lesson" belong to sections
        # that would otherwise answer first with a list of everything.
        daily = self.handle_daily(text, lowered, lang)
        if daily is not None:
            return daily

        result = self.handle_alphabet(text, lowered)
        if result is None:
            result = self.handle_letter_lookup(text)
        if result is None:
            result = self.handle_number(text, lang)
        # The dictionary answers four asks nothing above it had: synonyms,
        # opposites, a word's inflected forms, and one word's meaning read in
        # the learner's own sentence. It runs here, ahead of the panels that
        # claim nearby words - "similar words" is a distinction topic, "past
        # tense" is a grammar lesson, but "synonyms for X" and "past tense of
        # seek" are lookups, and the phrase has to win over the topic.
        if result is None:
            self.lex_prefetch(text)
            result = self.handle_lexicon(text, lowered, lang)
        # ahead of handle_pronounce, which also answers "how do I say X" -
        # a register question is the more specific reading of that phrase
        if result is None:
            result = self.handle_register(text, lowered, lang)
        if result is None:
            result = self.handle_pronounce(text, lowered, lang)
        if result is None:
            result = self.handle_distinction(text, lowered, lang)
        if result is None:
            result = self.handle_life_meaning(text, lang)
        # the bank comes first: it is where a phrase is looked up, and the
        # curated idiom table is a listing surface that answers "اصطلاحات"
        # with everything it has - which is the wrong reply to "معنی اصطلاح
        # دل به دریا زدن یعنی چی", a question about one idiom
        if result is None:
            result = self.handle_slang(text, lowered, lang)
        if result is None:
            result = self.handle_idioms(text, lowered, lang)
        if result is None:
            result = self.handle_correction(text, lowered, lang)
        if result is None:
            result = self.handle_stat(text, lowered, lang)
        if result is None:
            result = self.handle_grammar(text, lowered, lang)
        if result is None:
            result = self.handle_phrases(text, lowered, lang)
        if result is None:
            result = self.handle_listening(text, lowered, lang)
        if result is None:
            result = self.handle_glossary_lookup(text, lang)
        if result is None:
            result = self.handle_vague_meaning(text, lang)
        if result is None:
            result = self.handle_domain_list(text, lowered, lang)
        if result:
            if learned:
                greet = f"\nNice to meet you, {self.user_name}!" if lang == "en" else f"\nخوشبختم {self.user_name}!"
                result += greet
            return result

        if learned:
            return (
                f"Nice to meet you, {self.user_name}!"
                if lang == "en"
                else f"خوشبختم {self.user_name} جان!"
            )

        intent = self.match_intent(text, lang)
        if intent:
            if intent["name"] == "joke":
                return self.tell_joke(text, lang)
            return self.reply_from_intent(intent, lang)

        # A single word on its own → treat as a vocabulary lookup
        # ("مدرسه", "table", "کیک" → translation + domain)
        if len(text.split()) == 1:
            word = text.strip(" .!?؟،\"'«»")
            entries = self.lookup_word(word)
            if entries:
                return self.format_lookup(word, entries, lang)
            if word and normalize_word(word):
                return self.lex_or_not_found(word, lang)

        # Language-specific fallbacks. The exact phrases "I'm not sure I
        # understand" / "متوجه نشدم" are kept as flow-test markers; the rest
        # is a precise menu instead of a generic "try something else".
        if lang == "fa":
            return (
                "متوجه نشدم 😅 ترجیح می‌دهم حدس نزنم. یکی از این‌ها را امتحان کن:\n"
                "   • ترجمه کلمه → «سیب به انگلیسی»\n"
                "   • واژگان → «رنگ‌ها» یا «حیوانات»\n"
                "   • گرامر → «حال ساده» یا «گرامر»\n"
                "   • تلفظ → «تلفظ hospital»\n"
                "   • فهرست کامل → «راهنما»"
            )
        return (
            "I'm not sure I understand yet — I'd rather ask than guess. 😊\n"
            "   Try one of these:\n"
            "   • translate a word → 'translate apple'\n"
            "   • vocabulary → 'colors' or 'what are the fruits'\n"
            "   • grammar → 'simple present' or 'grammar'\n"
            "   • pronunciation → 'how do you pronounce hospital'\n"
            "   • full menu → 'help'"
        )


def second_opinion(sentence: str) -> str:
    """A correction from GEC-BART Base, when it has been switched on.

    Off unless FLUENTIFY_GEC is set. The rule set above is what ships: the APK
    runs its own JavaScript port, that port cannot load a 558 MB BART, and
    `tests_js_vs_python.py` holds the two engines to the same words - so a
    model line on the default path would be drift by construction. Asked for
    explicitly, it is a second opinion beside the rules, never instead of them.

    The import is inside the function on purpose: this file stays stdlib-only
    and the 2 GB dependency is never touched unless the learner opts in.
    """
    try:
        tools = str(Path(__file__).resolve().parent / "tools")
        if tools not in sys.path:
            sys.path.insert(0, tools)
        import gec  # noqa: PLC0415 - optional, and deliberately late

        fixed = gec.second_opinion(sentence)
    except Exception:  # no model, no venv, no transformers: just the rules
        return ""
    if not fixed:
        return ""
    return f"🧠 Local GEC model — مدل محلی: {fixed}"


def plain(reply: str) -> str:
    """Strip the **bold** markers for a terminal.

    The data marks the taught word with **like this** so the web and the app
    can render it bold; a terminal has no bold, and printing the asterisks
    makes every example look broken.
    """
    return re.sub(r"\*\*(.+?)\*\*", r"\1", reply)


def main() -> None:
    bot = ChatBot()
    print("Fluentify — English & Persian (type 'help' for options, 'bye' to exit)")
    print("-" * 60)
    while True:
        try:
            user_input = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nBot: Goodbye! / خداحافظ!")
            break
        if user_input.strip().lower() in ("bye", "exit", "quit", "خروج"):
            print(f"Bot: {plain(bot.respond(user_input))}")
            break
        print(f"Bot: {plain(bot.respond(user_input))}")


if __name__ == "__main__":
    main()
