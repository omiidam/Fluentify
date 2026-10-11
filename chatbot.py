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
    ):
        with open(memory_path, encoding="utf-8") as f:
            self.memory = json.load(f)
        self.user_name = None
        self.history = []          # short-term memory: recent user messages
        self.intents = self.memory["intents"]
        self._load_glossary(glossary_path)
        with open(grammar_path, encoding="utf-8") as f:
            self.grammar = json.load(f)["topics"]
        self.exercise = None       # active grammar exercise session
        self.exercise_score = 0
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

    def format_topic(self, topic, lang: str) -> str:
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

        count = to_persian_digits(len(topic["exercises"])) if lang == "fa" else len(topic["exercises"])
        parts.append("\n4️⃣ Exercises / تمرین")
        if lang == "fa":
            parts.append(f"{count} سوال آماده دارم — بنویس: 'تمرین {topic['title']['fa']}'")
        else:
            parts.append(f"{count} questions ready — type: '{topic['title']['en'].lower()} exercises'")
        return "\n".join(parts)

    def format_exercise_card(self, topic, index: int, lang: str) -> str:
        q = topic["exercises"][index]
        total = len(topic["exercises"])
        n = to_persian_digits(index + 1) if lang == "fa" else str(index + 1)
        total_s = to_persian_digits(total) if lang == "fa" else str(total)
        question = q["q"].get(lang, q["q"]["en"])
        if lang == "fa":
            hint = "پاسخ خودت رو بنویس. ('جواب' برای دیدن جواب، 'گرامر' برای خروج)"
            return f"✏️ تمرین {n} از {total_s}\n{question}\n{hint}"
        hint = "Type your answer. ('show answer' to reveal it, 'grammar' to exit)"
        return f"✏️ Exercise {n}/{total_s}\n{question}\n{hint}"

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

    def handle_grammar(self, text: str, lowered: str, lang: str) -> str | None:
        found = self.match_grammar_topic(text, lowered, lang)
        if found:
            topic_id, topic = found
            if self.wants_exercises(text, lowered, lang):
                self.exercise = {"topic": topic_id, "index": 0, "lang": lang}
                self.exercise_score = 0
                intro = (
                    f"🎯 شروع تمرین «{topic['title']['fa']}» — موفق باشی!\n"
                    if lang == "fa"
                    else f"🎯 Starting '{topic['title']['en']}' practice — good luck!\n"
                )
                return intro + self.format_exercise_card(topic, 0, lang)
            return self.format_topic(topic, lang)
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
        sess_lang = self.exercise.get("lang", lang)
        index = self.exercise["index"]
        question = topic["exercises"][index]

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
            return praise + "\n" + self._advance_exercise(topic, sess_lang)

        # Leaving the exercise: exit words (either language), or switching
        # to a grammar menu / another topic
        if self.is_exit_command(text, lowered):
            self.exercise = None
            # A real goodbye still deserves the farewell; anything else just
            # closes the practice instead of falling through to the glossary.
            if re.search(r"\b(bye|goodbye|خداحافظ)\b", lowered) or "خداحافظ" in text:
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
        reveal = any(w in lowered for w in self.SHOW_WORDS) or any(
            w in text for w in self.SHOW_WORDS_FA
        )
        if not reveal:
            if sess_lang == "fa":
                return "❌ نه، درست نیست. دوباره امتحان کن — یا بنویس 'جواب'."
            return "❌ Not quite. Try again — or type 'show answer'."

        # Reveal the answer, then advance
        answer = " / ".join(question["a"])
        reveal_msg = f"💡 جواب: {answer}" if sess_lang == "fa" else f"💡 Answer: {answer}"
        return reveal_msg + "\n" + self._advance_exercise(topic, sess_lang)

    def _advance_exercise(self, topic, lang: str) -> str:
        self.exercise["index"] += 1
        index = self.exercise["index"]
        if index >= len(topic["exercises"]):
            total = len(topic["exercises"])
            score = self.exercise_score
            self.exercise = None
            return self.format_score_report(topic, score, total, lang)
        return self.format_exercise_card(topic, index, lang)

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

    def format_score_report(self, topic, score: int, total: int, lang: str) -> str:
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
            head = f"{icon} نتیجه تمرین — {topic['title']['fa']}"
            return (
                f"{head}\n"
                f"{'─' * 34}\n"
                f"امتیاز:  {score_s} / {total_s}   ({pct_s}{pct_sign})\n"
                f"{bar}\n"
                f"سطح: {fa}\n"
                f"{note}\n"
                f"برای درس برگرد: 'گرامر' — یا دوباره: 'تمرین {topic['title']['fa']}'"
            )
        head = f"{icon} Practice result — {topic['title']['en']}"
        return (
            f"{head}\n"
            f"{'─' * 34}\n"
            f"Score:   {score}/{total}   ({pct}%)\n"
            f"{bar}\n"
            f"Level:   {en}\n"
            f"{note}\n"
            f"Back to lessons: 'grammar' — or retry: '{topic['title']['en'].lower()} exercises'"
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
        if not re.search(r"\b(listen|listening|audio|voice|speak)\b", lowered) and not any(
            w in text for w in ("گوش دادن", "آواز", "بگو")
        ):
            return None
        level = self.match_listening_level(text, lowered)
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
            print(f"Bot: {bot.respond(user_input)}")
            break
        print(f"Bot: {bot.respond(user_input)}")


if __name__ == "__main__":
    main()
