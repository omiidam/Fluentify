#!/usr/bin/env python3
"""Fluentify — a bilingual (English/Persian) chatbot with preloaded memory.

Memory model inspired by:
  * gunthercox/chatterbot-corpus   — daily conversation phrases (English)
  * Microsoft PersonalityChat      — small-talk scenario set
  * Mahdi-Razaghi/tajan            — bilingual (FA/EN) intent structure
  * Persian-Caesar/chatbot         — Persian daily-talk phrasing
"""

import json
import random
import re
import sys
from datetime import datetime
from pathlib import Path

MEMORY_FILE = Path(__file__).parent / "memory.json"
GLOSSARY_FILE = Path(__file__).parent / "glossary.json"
PHRASES_FILE = Path(__file__).parent / "phrases.json"
GRAMMAR_FILE = Path(__file__).parent / "grammar.json"
JOKES_FILE = Path(__file__).parent / "jokes.json"
LISTENING_FILE = Path(__file__).parent / "listening.json"
DISTINCTIONS_FILE = Path(__file__).parent / "distinctions.json"
IDIOMS_FILE = Path(__file__).parent / "idioms.json"
CORRECTIONS_FILE = Path(__file__).parent / "corrections.json"

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


# Stopwords that should never be treated as glossary lookup targets
LOOKUP_STOPWORDS = {
    "it", "this", "that", "is", "are", "mean", "means", "the", "a", "an",
    "what", "which", "word", "translate", "define",
    "این", "اون", "است", "چیه", "چیست", "کلمه", "معنی",
    "اسمت", "نامت", "اسم", "تو", "شما", "من", "خودت",
}

# Pattern (lang, regex) lists to extract a target word from lookup requests
EN_LOOKUP_PATTERNS = [
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
    r"(?P<t>.+?)\s*یعنی\s*چه",
    r"(?:چطوری|چطور|چجوری)\s+(?P<t>.+?)\s*بگم",
    r"ترجمه\s+(?P<t>.+)",
    r"کلمه\s+(?P<t>.+?)\s*(?:چیه|چیست)",
    r"(?P<t>.+?)\s+به\s+(?:انگلیسی|فارسی)",
    r"به\s+(?:انگلیسی|فارسی)\s+(?P<t>.+)",
    r"(?P<t>.+?)\s*(?:چیه|چیست)$",
]


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
        corrections_path: Path = CORRECTIONS_FILE,
    ):
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
        self.corrections = []      # rule-based checker for common learner errors
        if corrections_path.exists():
            with open(corrections_path, encoding="utf-8") as f:
                self.corrections = json.load(f)["rules"]

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
                elif kw in text:  # Persian is agglutinative — substring is safer
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
                 f"   ↳ سطح: {topic['level']}", "",
                 f"{topic['why']}"]
        for side in topic["sides"]:
            lines.append("")
            lines.append(f"  • {side['en']}")
            if side.get("fa"):
                lines.append(f"    ↳ {side['fa']}")
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
                f"   ↳ {row['meaning']}\n"
                f"   e.g. {row['example']}")

    def handle_idioms(self, text: str, lowered: str, lang: str) -> str | None:
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
        asked = bool(re.search(
            r"\b(is (?:this|that|it) (?:correct|right|wrong)|check my|"
            r"correct (?:my|this|these|the)|fix (?:my|this|my sentence)|"
            r"is this ok|grammatically|درسته|درست است|میشه|غلطه)",
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
                return ("✅ That sentence is correct English.  ↳ این جمله درست است."
                        if lang == "en" else
                        "✅ این جمله درست است. / That sentence is correct English.")
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
                "   ↳ کلمه را بگو تا با هم تلفظش کنیم.\n"
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
            lines.append("   ↳ For the full guide ask: 'phonetics'")
            return "\n".join(lines)

        phrase = self.lookup_phrase(key)
        if phrase:
            lines = [f"🗣  “{phrase['en']}”",
                     f"   ↳ {phrase['fa']}",
                     *([f"   Say it slowly: {' · '.join(phrase['en'])}"]
                       if len(phrase["en"]) <= 24 else []),
                     "   ↳ For the full guide ask: 'phonetics'"]
            return "\n".join(lines)

        # Not in the dictionary — say something useful instead of dropping the
        # learner's question on the floor.
        return (
            f"🗣  “{word}” is not in my vocabulary list yet, so I cannot give "
            f"you its Persian meaning.\n"
            f"   ↳ «{word}» هنوز در واژگان من نیست.\n"
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
                hit = (
                    bool(re.search(rf"\b{re.escape(kw)}\b", lowered))
                    if lang == "en"
                    else kw in text
                )
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
        parts.extend(f"• {s['en']}\n  ↳ {s['fa']}" for s in topic["structure"])
        if topic.get("tip"):
            parts.append(f"\n💡 Tip: {topic['tip']['en']}\n   ↳ {topic['tip']['fa']}")

        parts.append("\n2️⃣ Function / کاربرد")
        parts.extend(f"• {f['en']}\n  ↳ {f['fa']}" for f in topic["function"])

        parts.append("\n3️⃣ Examples / مثال‌ها")
        parts.extend(
            f"{i}. {e['en']}\n   ↳ {e['fa']}"
            for i, e in enumerate(topic["examples"], 1)
        )

        practice_n = len(topic.get("practice", []))
        exam_n = len(topic.get("exam", topic.get("exercises", [])))
        done = self._unlocked(topic_id)
        parts.append("\n4️⃣ Exercises / تمرین")
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

    def handle_grammar(self, text: str, lowered: str, lang: str) -> str | None:
        found = self.match_grammar_topic(text, lowered, lang)
        if found:
            topic_id, topic = found
            exam = self.wants_exam(text, lowered, lang)
            practice = self.wants_exercises(text, lowered, lang)

            if exam:
                if topic_id not in self.practice_done:
                    n = to_persian_digits(len(topic.get("practice", []))) if lang == "fa" \
                        else str(len(topic.get("practice", [])))
                    title = topic["title"]["fa"] if lang == "fa" else topic["title"]["en"]
                    return (
                        f"🔒 آزمون قفل است — اول تمرین ({n} سوال) را کامل کن.\n"
                        f"بنویس: 'تمرین {title}'"
                        if lang == "fa" else
                        f"🔒 The exam is locked — finish the practice first ({n} questions).\n"
                        f"Type: '{topic['title']['en'].lower()} exercises'"
                    )
                self.exercise = {"topic": topic_id, "index": 0, "lang": lang,
                                 "stage": "exam"}
                self.exercise_score = 0
                intro = (
                    f"🎓 شروع آزمون «{topic['title']['fa']}» — موفق باشی!\n"
                    if lang == "fa"
                    else f"🎓 Starting the '{topic['title']['en']}' exam — good luck!\n"
                )
                return intro + self.format_exercise_card(topic, 0, lang, "exam")

            if practice:
                self.exercise = {"topic": topic_id, "index": 0, "lang": lang,
                                 "stage": "practice"}
                self.exercise_score = 0
                intro = (
                    f"✏️ شروع تمرین «{topic['title']['fa']}» — موفق باشی!\n"
                    if lang == "fa"
                    else f"✏️ Starting '{topic['title']['en']}' practice — good luck!\n"
                )
                return intro + self.format_exercise_card(topic, 0, lang, "practice")
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
        for topic_id, topic in self.phrases.items():
            for lang in ("en", "fa"):
                for kw in topic["keywords"].get(lang, []):
                    if lang == "en":
                        if re.search(rf"\b{re.escape(kw)}\b", lowered):
                            return topic_id, topic
                    elif normalize_word(kw) in norm_text:
                        return topic_id, topic
        return None

    @staticmethod
    def format_phrase_topic(topic, lang: str) -> str:
        """English sentence first, Persian translation beneath it."""
        parts = [f"💬 {topic['title']['en']} ({topic['title']['fa']})"]
        for line in topic["phrases"]:
            parts.append(f"• {line['en']}\n  ↳ {line['fa']}")
        return "\n".join(parts)

    def handle_phrases(self, text: str, lowered: str, lang: str) -> str | None:
        found = self.match_phrase_topic(text, lowered)
        if found:
            _, topic = found
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
            parts.append(f"{i}. {s['en']}\n   \u21b3 {s['fa']}")
        return "\n".join(parts)

    def handle_listening(self, text: str, lowered: str, lang: str) -> str | None:
        asked = bool(re.search(r"\b(listen|listening|audio|voice|speak)\b", lowered)) \
            or any(w in text for w in ("گوش دادن", "آواز", "بگو"))
        # a learner often just types the band itself: "A1", "b2", "C2"
        bare = re.fullmatch(r"\s*([abc][12])\s*[?!.؟]*\s*", lowered)
        if not asked and not bare:
            return None
        level = self.match_listening_level(text, lowered)
        if level is None and bare:
            level = self.match_listening_level(bare.group(1), bare.group(1))
        if level:
            return self.format_listening_level(level)
        if re.search(r"\b(listen|listening|audio|voice)\b", lowered) or any(
            w in text for w in ("گوش دادن", "آواز", "بگو")
        ):
            names = " · ".join(l["title"]["en"].split(" · ")[0] for l in self.listening)
            return (
                f"\U0001f3a7 Listening levels — سطح شنیدن: {names}\n"
                "Ask: 'listen A1' or 'گوش دادن A1'"
            )
        return None

    # ------------------------------------------------------------------ #
    #  Glossary (vocabulary domains + word lookup)
    # ------------------------------------------------------------------ #
    def handle_domain_list(self, text: str, lowered: str, lang: str) -> str | None:
        """If the user asks for a vocabulary domain, list it bilingually."""
        norm_text = normalize_word(text)
        for dom_id, dom in self.glossary.items():
            for kw in dom["keywords"].get(lang, []):
                key = normalize_word(kw)
                matched = (
                    re.search(rf"\b{re.escape(kw)}(?:s|es)?\b", lowered)
                    if lang == "en"
                    else key in norm_text
                )
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

    def handle_glossary_lookup(self, text: str, lang: str) -> str | None:
        """Translate/define a word: 'translate apple', 'سیب به انگلیسی', ..."""
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

        entries = self.lookup_word(target)
        if not entries:
            # Multi-word targets are probably not vocab lookups at all
            # ("help me in english") → let the intent matcher handle them
            if len(target.split()) > 1:
                return None
            return self.not_found_msg(target, lang)
        return self.format_lookup(target, entries, lang)

    @staticmethod
    def not_found_msg(target: str, lang: str) -> str:
        if lang == "fa":
            return (
                f"«{target}» توی واژه‌نامه من نیست هنوز 📚 "
                "یکی از این دامنه‌ها رو امتحان کن: رنگها، حیوانات، میوهها، اعداد، مشاغل."
            )
        return (
            f"I don't have \"{target}\" in my glossary yet 📚 "
            "Try one of my domains: colors, animals, fruits, numbers, jobs, sports..."
        )

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

        learned = self.learn_name(text)

        # Structured knowledge first
        result = self.handle_alphabet(text, lowered)
        if result is None:
            result = self.handle_letter_lookup(text)
        if result is None:
            result = self.handle_number(text, lang)
        if result is None:
            result = self.handle_pronounce(text, lowered, lang)
        if result is None:
            result = self.handle_distinction(text, lowered, lang)
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
                return self.not_found_msg(word, lang)

        # Language-specific fallbacks
        if lang == "fa":
            return (
                "متوجه نشدم 😅 می‌تونی درباره الفبای فارسی، جوک، ساعت، ترجمه کلمات "
                "(مثل 'سیب به انگلیسی') یا واژگان (مثل 'رنگها' و 'حیوانات') بپرسی. "
                "برای راهنما بنویس 'راهنما'."
            )
        return (
            "I'm not sure I understand 😅 Try asking about the alphabets, a joke, "
            "translating a word ('translate apple'), a vocabulary domain "
            "('what are the colors'), or the time. Type 'help' for options."
        )


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
