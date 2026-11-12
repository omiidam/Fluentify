#!/usr/bin/env python3
"""Write chapter eighteen of the grammar book into books.json.

    python3 tools/chapter18.py

Chapter eighteen of *Understanding and Using English Grammar* is the reduction
of adverb clauses to modifying phrases. The book shipped with one placeholder
section for it; this replaces it with the chapter's five charts, written out like
chapters three to seventeen: the rule, the form, examples in both languages,
three guided exercises and a three-question check for each.

The sentences and explanations are written for this app. The book is the
reference text, and nothing in this file is transcribed from it.

It is idempotent: chapter eighteen is always rebuilt from this script.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "books.json"

CHAPTER = "Chapter 18"


def ex(prompt, answer, why_en, why_fa):
    return {"prompt": prompt, "answer": answer, "why_en": why_en, "why_fa": why_fa}


def q(text, options, answer, why_en, why_fa):
    assert answer in options and len(options) == 3, text
    return {"q": text, "options": options, "answer": answer,
            "why_en": why_en, "why_fa": why_fa}


LESSONS = [
    {
        "section": "18-1",
        "title": "Reducing an adverb clause to a phrase: an introduction",
        "title_fa": "کوتاه‌کردن جملهٔ قیدی به عبارت: درآمد",
        "use_en": "When the subject of the adverb clause is the same as the subject of the main clause, the clause can lose its subject and its verb be, or its subordinator and its subject, and become a phrase: while I was walking home becomes while walking home. The phrase keeps a participle and the meaning of the clause. If the two subjects are different, the reduction is not possible, because the reader would attach the phrase to the wrong person.",
        "use_fa": "وقتی فاعل جملهٔ قیدی با فاعل جملهٔ اصلی یکی است، جمله می‌تواند فاعل و فعل be خود را از دست بدهد، یا حرف ربط و فاعلش را، و به عبارت تبدیل شود: while I was walking home به while walking home تبدیل می‌شود. عبارت اسم مفعول یا اسم فاعل را نگه می‌دارد و معنای جمله را. اگر فاعل‌ها متفاوت باشند کوتاه‌سازی ممکن نیست، چون خواننده عبارت را به شخص نادرست نسبت می‌دهد.",
        "form_en": "while / when / because / after + subject + be → conjunction + -ing  ·  same subject required",
        "examples": [
            {"en": "While walking home, I met an old friend.",
             "fa": "در راه خانه دوست قدیمی‌ای دیدم."},
            {"en": "Because she was tired, she went to bed early.",
             "fa": "چون خسته بود زود به رختخواب رفت."},
            {"en": "After finishing the report, he called his manager.",
             "fa": "پس از تمام کردن گزارش به مدیرش زنگ زد."},
        ],
        "exercises": [
            ex("While ___ for the bus, I read the news. (wait)", "waiting",
               "The clause loses its subject and be, keeping the participle.",
               "جمله فاعل و be را از دست می‌دهد و اسم فاعل می‌ماند."),
            ex("Before ___ the meeting, she checked her notes. (start)", "starting",
               "Before plus a gerund replaces the clause.",
               "before و اسم مصدر جای جمله را می‌گیرد."),
            ex("The phrase only works when the two subjects are ___ .", "the same",
               "A different subject makes the phrase ambiguous.",
               "فاعل متفاوت عبارت را مبهم می‌کند."),
        ],
        "exam": [
            q("Which sentence can be reduced?",
              ["While I was waiting, I read a book.", "While I waited, she read a book.",
               "She read while I waited."], "While I was waiting, I read a book.",
              "The two subjects are the same, so the clause can shrink.",
              "دو فاعل یکی‌اند، پس جمله کوتاه می‌شود."),
            q("After ___ the letter, he posted it.",
              ["writing", "write", "wrote"], "writing",
              "The reduced clause keeps the -ing form.",
              "جملهٔ کوتاه‌شده شکل ing- را نگه می‌دارد."),
            q("Why can a phrase be wrong here? — While driving home, the tree fell.",
              ["The tree was not driving.", "The sentence has no verb.",
               "Driving is not a participle."], "The tree was not driving.",
              "The subject of the phrase must be the subject of the sentence.",
              "فاعل عبارت باید فاعل جمله باشد."),
        ],
    },
    {
        "section": "18-2",
        "title": "Turning a time clause into a modifying phrase",
        "title_fa": "تبدیل جملهٔ زمانی به عبارت وصفی",
        "use_en": "When the time clause has the same subject and a form of be, drop both and keep the -ing form: when he was leaving the office, he saw the message becomes leaving the office, he saw the message. The subordinator can stay for clarity: while leaving the office, he saw the message. The phrase describes when the main action happened, and it sits at the front or the end of the sentence.",
        "use_fa": "وقتی جملهٔ زمانی فاعل یکسان و شکلی از be دارد، هر دو را حذف کنید و شکل ing- را نگه دارید: when he was leaving the office, he saw the message به leaving the office, he saw the message تبدیل می‌شود. حرف ربط می‌تواند برای روشنی بماند: while leaving the office, he saw the message. عبارت می‌گوید کار اصلی کِی رخ داد و در آغاز یا پایان جمله می‌نشیند.",
        "form_en": "when / while + subject + be + -ing → (while) + -ing  ·  phrase at either end",
        "examples": [
            {"en": "Leaving the office, he saw the message.",
             "fa": "در حال ترک دفتر، پیام را دید."},
            {"en": "While leaving the office, he saw the message.",
             "fa": "هنگام ترک دفتر پیام را دید."},
            {"en": "She hurt her ankle while playing tennis.",
             "fa": "هنگام تنیس بازی کردن مچ پایش آسیب دید."},
        ],
        "exercises": [
            ex("When ___ the room, she turned off the lights. (leave)", "leaving",
               "The reduced time clause keeps the -ing form.",
               "جملهٔ زمانی کوتاه‌شده شکل ing- را نگه می‌دارد."),
            ex("___ walking to work, I listen to podcasts. (time)", "While",
               "While can stay in the phrase for clarity.",
               "while می‌تواند برای روشنی در عبارت بماند."),
            ex("He fell asleep ___ watching television. (time)", "while",
               "While marks the action in progress.",
               "while کار در جریان را نشان می‌دهد."),
        ],
        "exam": [
            q("___ entering the building, she showed her pass.",
              ["When", "When she", "When was"], "When",
              "The reduced clause keeps the subordinator and the participle.",
              "جملهٔ کوتاه‌شده حرف ربط و اسم فاعل را نگه می‌دارد."),
            q("Which phrase is correct?",
              ["Walking home, I saw a friend.", "Walk home, I saw a friend.",
               "Walked home, I saw a friend."], "Walking home, I saw a friend.",
              "An active time clause reduces to -ing.",
              "جملهٔ زمانی معلوم به ing- کوتاه می‌شود."),
            q("While ___ the dishes, he dropped a glass.",
              ["washing", "wash", "washed"], "washing",
              "The action in progress takes the -ing form.",
              "کار در جریان شکل ing- می‌گیرد."),
        ],
    },
    {
        "section": "18-3",
        "title": "Phrases that say two things happened at the same time",
        "title_fa": "عبارت‌هایی که می‌گویند دو کار هم‌زمان رخ داد",
        "use_en": "Two actions by the same person at the same moment can be expressed with one -ing phrase and one main verb: she sat at the desk reading a letter, or reading a letter, she sat at the desk. While or as can make the simultaneity explicit. A sentence with two -ing phrases is possible but heavy, and English usually keeps one action in the main verb.",
        "use_fa": "دو کار یک شخص در یک لحظه را می‌توان با یک عبارت ing- و یک فعل اصلی گفت: she sat at the desk reading a letter، یا reading a letter, she sat at the desk. while یا as هم‌زمانی را روشن‌تر می‌کند. جمله با دو عبارت ing- ممکن است اما سنگین است و انگلیسی معمولاً یک کار را در فعل اصلی نگه می‌دارد.",
        "form_en": "main clause + -ing phrase (same time)  ·  (while / as) + -ing, + main clause",
        "examples": [
            {"en": "She sat at the desk reading a letter.",
             "fa": "پشت میز نشسته بود و نامه می‌خواند."},
            {"en": "Reading a letter, she sat at the desk.",
             "fa": "در حال خواندن نامه، پشت میز نشست."},
            {"en": "He listened to music while cooking dinner.",
             "fa": "هنگام پختن شام موسیقی گوش می‌داد."},
        ],
        "exercises": [
            ex("She stood by the window ___ the rain. (watch)", "watching",
               "The same-time action takes the -ing phrase.",
               "کار هم‌زمان عبارت ing- می‌گیرد."),
            ex("He whistled ___ working. (same time)", "while",
               "While makes the simultaneity explicit.",
               "while هم‌زمانی را روشن می‌کند."),
            ex("___ dinner, they talked about the trip. (cook)", "Cooking",
               "The phrase at the front names the simultaneous action.",
               "عبارت در آغاز کار هم‌زمان را می‌گوید."),
        ],
        "exam": [
            q("She sat by the fire ___ a book.",
              ["reading", "read", "to read"], "reading",
              "Two simultaneous actions take one -ing phrase.",
              "دو کار هم‌زمان یک عبارت ing- می‌گیرند."),
            q("Which sentence says the two actions happened together?",
              ["He sang while washing the car.", "He sang, then washed the car.",
               "He sang before washing the car."], "He sang while washing the car.",
              "While marks the same time.",
              "while هم‌زمانی را نشان می‌دهد."),
            q("___ the news, she started to cry.",
              ["Hearing", "Heard", "Hear"], "Hearing",
              "The same-time action is an -ing phrase.",
              "کار هم‌زمان عبارت ing- است."),
        ],
    },
    {
        "section": "18-4",
        "title": "Cause-and-effect phrases: having finished, not knowing",
        "title_fa": "عبارت‌های علت و اثر: having finished، not knowing",
        "use_en": "A reason clause can also be reduced: because she had finished the report becomes having finished the report, and because he did not know the way becomes not knowing the way. Having plus a past participle puts the cause before the main action, and the negative is not plus the -ing form. These phrases belong to writing, where they save a clause without losing the reason.",
        "use_fa": "جملهٔ دلیل هم می‌تواند کوتاه شود: because she had finished the report به having finished the report و because he did not know the way به not knowing the way تبدیل می‌شود. having و اسم مفعول علت را پیش از کار اصلی می‌گذارد و منفی آن not و شکل ing- است. این عبارت‌ها به نوشتار تعلق دارند، جایی که یک جمله را بی از دست دادن دلیل کوتاه می‌کنند.",
        "form_en": "having + past participle (earlier cause)  ·  not + -ing (negative cause)",
        "examples": [
            {"en": "Having finished the report, she went home.",
             "fa": "پس از تمام کردن گزارش به خانه رفت."},
            {"en": "Not knowing the way, he asked a policeman.",
             "fa": "چون راه را نمی‌دانست از پلیسی پرسید."},
            {"en": "Having missed the bus, they walked.",
             "fa": "چون اتوبوس را از دست داده بودند پیاده رفتند."},
        ],
        "exercises": [
            ex("___ eaten, we paid the bill. (earlier cause)", "Having",
               "The earlier cause takes having plus the participle.",
               "علت پیش‌تر having و اسم مفعول می‌گیرد."),
            ex("___ knowing the answer, she said nothing. (negative)", "Not",
               "The negative cause begins with not.",
               "علت منفی با not آغاز می‌شود."),
            ex("___ finished the work, he left early. (cause)", "Having",
               "Having plus the participle reports a completed action.",
               "having و اسم مفعول کار تمام‌شده را می‌گوید."),
        ],
        "exam": [
            q("___ lost the keys, she called a locksmith.",
              ["Having", "Have", "To have"], "Having",
              "A cause that happened first takes having.",
              "علتی که پیش‌تر رخ داده having می‌گیرد."),
            q("___ feeling well, he stayed home.",
              ["Not", "No", "None"], "Not",
              "The negative phrase begins with not.",
              "عبارت منفی با not آغاز می‌شود."),
            q("Which sentence gives the cause in a phrase?",
              ["Having missed the train, they waited.", "They missed the train and waited.",
               "They waited because the train."], "Having missed the train, they waited.",
              "The phrase states the reason for waiting.",
              "عبارت دلیل انتظار را می‌گوید."),
        ],
    },
    {
        "section": "18-5",
        "title": "Upon + -ing: as soon as one thing happened",
        "title_fa": "upon + ing-: به محض رخ دادن چیزی",
        "use_en": "Upon plus a gerund means immediately after, and it is the formal way of saying as soon as: upon arriving, he called his family. On works the same way and is a little less formal. The pattern is common in reports and stories, and it always describes the same subject as the main clause, so the two must match.",
        "use_fa": "upon به‌همراه اسم مصدر یعنی «بلافاصله پس از» و شکل رسمی as soon as است: upon arriving, he called his family. on هم همین کار را می‌کند و کمی کم‌رسمی‌تر است. این الگو در گزارش‌ها و داستان‌ها رایج است و همیشه همان فاعل جملهٔ اصلی را می‌گوید، پس دو فاعل باید یکی باشند.",
        "form_en": "upon / on + -ing  ·  same subject as the main clause",
        "examples": [
            {"en": "Upon arriving, he called his family.",
             "fa": "به محض رسیدن به خانواده‌اش زنگ زد."},
            {"en": "On hearing the news, she left immediately.",
             "fa": "به محض شنیدن خبر فوراً رفت."},
            {"en": "Upon finishing the course, they received a certificate.",
             "fa": "به محض تمام کردن دوره گواهی گرفتند."},
        ],
        "exercises": [
            ex("___ receiving the letter, she replied. (immediately after)", "Upon",
               "Upon plus the gerund means immediately after.",
               "upon و اسم مصدر یعنی بلافاصله پس از."),
            ex("___ arriving at the hotel, we checked in. (formal)", "Upon",
               "The formal form of as soon as is upon.",
               "شکل رسمی as soon as همان upon است."),
            ex("She smiled ___ seeing the photograph. (immediately after)", "on",
               "On plus the gerund is the less formal form.",
               "on و اسم مصدر شکل کم‌رسمی‌تر است."),
        ],
        "exam": [
            q("___ opening the box, he found the letter.",
              ["Upon", "While", "During"], "Upon",
              "Immediately after an action takes upon.",
              "بلافاصله پس از کار upon می‌گیرد."),
            q("Which phrase means as soon as he arrived?",
              ["Upon arriving", "While arriving", "Before arriving"], "Upon arriving",
              "Upon marks the moment right after.",
              "upon لحظهٔ بلافاصله پس از را نشان می‌دهد."),
            q("___ hearing the alarm, everyone left the building.",
              ["On", "In", "At"], "On",
              "On plus the gerund means immediately after.",
              "on و اسم مصدر یعنی بلافاصله پس از."),
        ],
    },
]


def main() -> int:
    data = json.loads(BOOKS.read_text(encoding="utf-8"))
    book = next(b for b in data["books"] if b.get("kind") == "grammar")

    old = [l for l in book["lessons"] if l.get("chapter") == CHAPTER]
    assert old, "chapter eighteen is not in the book"

    lessons = []
    for lesson in book["lessons"]:
        if lesson.get("chapter") == CHAPTER:
            if lesson is old[0]:
                for item in LESSONS:
                    lessons.append({
                        "n": 0, "title": item["title"], "title_fa": item["title_fa"],
                        "chapter": CHAPTER, "section": item["section"],
                        "use_en": item["use_en"], "use_fa": item["use_fa"],
                        "form_en": item["form_en"], "examples": item["examples"],
                        "exercises": item["exercises"], "exam": item["exam"],
                    })
            continue
        lessons.append(lesson)

    for i, lesson in enumerate(lessons, 1):
        lesson["n"] = i
    book["lessons"] = lessons

    size = len(lessons)

    BOOKS.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")
    print(f"chapter eighteen: {len(LESSONS)} charts, {size} structures in the book")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
