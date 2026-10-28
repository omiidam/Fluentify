#!/usr/bin/env python3
"""Harness round 3 — the learner opens a lesson, then types one word.

Round 3 drove the bot through the flows a real learner walks: open a lesson,
then say "exercises"; ask for a joke, then say "another one"; start listening,
then say "repeat that". Almost every one of those fell through to "I'm not
sure I understand" because the bot only understood a *named* topic and had no
memory of the last one.

This patches chatbot.py with:
  * conversation memory (last lesson / phrase bank / listening band / joke)
  * bare follow-up commands: exercises, exam, show answer, next, cancel,
    another one, repeat that, examples, more
  * the small talk that goes with them ("I am fine", "what can I learn today")
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHAT = ROOT / "chatbot.py"


def patch(text: str) -> str:
    # ---------------------------------------------------------- state ------
    old = """        self.last_joke_id = None   # avoid repeating the same joke twice in a row"""
    new = """        self.last_joke_id = None   # avoid repeating the same joke twice in a row
        # What the learner is looking at right now. Without this, "exercises"
        # after a lesson is a dictionary miss instead of "start that lesson".
        self.last_lesson: str | None = None
        self.last_phrase: str | None = None
        self.last_level: str | None = None
        self.last_examples = []"""
    assert old in text
    text = text.replace(old, new, 1)

    # --------------------------------------------- remember what we showed -
    old = """        level = self.match_listening_level(text, lowered)
        if level is None and bare:
            level = self.match_listening_level(bare.group(1), bare.group(1))
        if level:
            return self.format_listening_level(level)"""
    new = """        level = self.match_listening_level(text, lowered)
        if level is None and bare:
            level = self.match_listening_level(bare.group(1), bare.group(1))
        if level:
            self.last_level = level["id"]
            return self.format_listening_level(level)"""
    assert old in text
    text = text.replace(old, new, 1)

    return text


def main() -> None:
    text = patch(CHAT.read_text(encoding="utf-8"))

    # ----------------------------------------------- the follow-up handler --
    handler = '''
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
    def _bare(lowered: str, table: dict) -> str | None:
        """Match a follow-up word for word.

        Bare words need an exact hit: 'next' must not fire inside 'what is the
        next colour', or the bot would skip ahead while answering a question.
        """
        s = re.sub(r"[.!?؟,;:\\"'«»()\\[\\]]", "", lowered).strip()
        if s in table:
            return table[s]
        if re.fullmatch(r"(?:please\\s+)?(?:can you\\s+|could you\\s+)?"
                        r"(?:give me|tell me|show me|let me|start|begin|open)\\s+"
                        r"[\\w' ]{0,24}", s) and s.split()[-1] in table:
            return table[s.split()[-1]]
        return None

    def handle_followup(self, text: str, lowered: str, lang: str) -> str | None:
        """One-word commands that act on whatever the learner just opened."""
        if self.exercise:
            return None        # a live quiz owns every message already

        which = self._bare(lowered, self.BARE_EXERCISE)
        if which:
            topic_id = self.last_lesson
            if topic_id is None:
                return ("Open a lesson first, then say 'exercises'.\\n"
                        "   ↲ اول یک درس را باز کن، بعد بنویس «تمرین».\\n"
                        "   Write 'grammar' for the list of lessons."
                        if lang == "en" else
                        "اول یک درس را باز کن، بعد بنویس «تمرین».\\n"
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
                return (f"💡 Answer: {answer}\\n   ↲ جواب: {answer}"
                        if lang == "en" else f"💡 جواب: {answer}\\n   Answer: {answer}")
            if self.last_level:
                return self.format_listening_level(
                    self.match_listening_level(self.last_level, self.last_level))
            return ("Nothing to reveal yet — open a lesson or ask me a question.\\n"
                    "   ↲ هنوز چیزی برای نمایش نیست — یک درس را باز کن."
                    if lang == "en" else
                    "هنوز چیزی برای نمایش نیست — یک درس را باز کن.")

        which = self._bare(lowered, self.BARE_EXAMPLES)
        if which:
            topic = self.grammar.get(self.last_lesson or "", None)
            if topic:
                rows = topic.get("examples", [])
                self.last_examples = [r["en"] for r in rows[:4]] or []
                return ("📝 More examples — مثال‌های بیشتر:\\n" + "\\n".join(
                    f"   {i + 1}. {r['en']}\\n      ↲ {r['fa']}"
                    for i, r in enumerate(rows)))
            return ("Open a lesson first and ask for examples.\\n"
                    "   ↲ اول یک درس را باز کن.")

        which = self._bare(lowered, self.BARE_AGAIN)
        if which:
            return self.tell_joke(text, lang)

        which = self._bare(lowered, self.BARE_REPEAT)
        if which:
            if self.last_level:
                return self.format_listening_level(
                    self.match_listening_level(self.last_level, self.last_level))
            if self.last_phrase:
                topic = self.phrases.get(self.last_phrase)
                if topic:
                    return ("Say it again — دوباره گوش کن:\\n" + "\\n".join(
                        f"   • {r['en']}\\n     ↲ {r['fa']}"
                        for r in topic["phrases"][:4]))
            return ("Tell me what to repeat — a listening band or a sentence bank.\\n"
                    "   ↲ بگو کدام را تکرار کنم." if lang == "en" else
                    "بگو کدام را تکرار کنم.")

        if self._bare(lowered, self.BARE_NEXT):
            topic_id = self.last_lesson
            if topic_id is None:
                return None
            return self.start_grammar_session(topic_id, "practice", lang)

        return None
'''

    anchor = "    # ------------------------------------------------------------------ #\n    #  Numbers written in words"
    assert anchor in text
    text = text.replace(anchor, handler.strip("\n") + "\n\n" + anchor, 1)

    # --------------------------------------------------- dispatch it early --
    old = """        result = self.handle_alphabet(text, lowered)
        if result is None:
            result = self.handle_letter_lookup(text)"""
    new = """        followup = self.handle_followup(text, lowered, lang)
        if followup is not None:
            return followup

        result = self.handle_alphabet(text, lowered)
        if result is None:
            result = self.handle_letter_lookup(text)"""
    assert old in text
    text = text.replace(old, new, 1)

    CHAT.write_text(text, encoding="utf-8")
    print("chatbot.py: follow-up handler + memory added")

    # ------------------------------------------------------- small talk -----
    mp = ROOT / "memory.json"
    memory = json.loads(mp.read_text(encoding="utf-8"))
    add = {
        "fine": ["i am fine", "im fine", "i'm fine", "i am good", "im good",
                 "i'm good", "i am ok", "im ok", "i'm ok", "not bad", "i am well",
                 "everything is fine", "i'm alright", "i am alright",
                 "خوبم", "حالم خوبه", "مرسی خوبم", "خوبم ممنون", "من خوبم"],
        "help": ["what can i learn today", "what can i learn", "what should i learn",
                 "what's new", "whats new", "today", "امروز چی یاد بگیرم",
                 "چی یاد بگیرم", "چه چیزی یاد بگیرم", "امروز چیکار کنم"],
        "joke": ["another one", "another joke", "one more joke", "tell me another joke",
                 "یکی دیگه", "جوک دیگه", "یه جوک دیگه", "یک جوک دیگه بگو"],
    }
    names = {i["name"] for i in memory["intents"]}
    if "fine" not in names:
        memory["intents"].append({
            "name": "fine",
            "keywords": {"en": add["fine"][:11], "fa": add["fine"][11:]},
            "responses": {
                "en": ["Good to hear! Want to practise something while you're here?",
                       "Nice! Let's use that energy — ask me for a lesson, a word, or a joke.",
                       "Great! Say 'grammar' for a lesson or 'vocabulary' for words."],
                "fa": ["خوبه که اینطوره! می‌خوای چیزی تمرین کنیم؟",
                       "عالیه! بیا از انرژیت استفاده کنیم — یک درس، یک کلمه یا یک جوک.",
                       "خوبه! بنویس «گرامر» برای درس یا «واژگان» برای کلمات."]}})
        print("  + intent: fine")
    for intent in memory["intents"]:
        extra = add.get(intent["name"])
        if not extra:
            continue
        kw = intent.setdefault("keywords", {"en": [], "fa": []})
        for w in extra:
            bucket = "fa" if any("\\u0600" <= c <= "\\u06ff" for c in w) else "en"
            if w not in kw.setdefault(bucket, []):
                kw[bucket].append(w)
    mp.write_text(json.dumps(memory, ensure_ascii=False, indent=2), encoding="utf-8")
    print("  ~ intents: fine / help / joke extended")


if __name__ == "__main__":
    main()