#!/usr/bin/env python3
"""Write chapter four of the grammar book into books.json.

    python3 tools/chapter4.py

Chapter four of *Understanding and Using English Grammar* is Review of Verb
Tenses. The book shipped with one summary section for it (section "4"); this
replaces it with the chapter's five review charts, written out like chapters
one to three: the rule, the form, examples in both languages, three guided
exercises and a three-question check for each.

It is idempotent: chapter four is always rebuilt from this script.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "books.json"


def ex(prompt, answer, why_en, why_fa):
    return {"prompt": prompt, "answer": answer, "why_en": why_en, "why_fa": why_fa}


def q(text, options, answer, why_en, why_fa):
    assert answer in options and len(options) == 3, text
    return {"q": text, "options": options, "answer": answer,
            "why_en": why_en, "why_fa": why_fa}


LESSONS = [
    {
        "section": "4-1",
        "title": "Simple tenses: present, past and future",
        "title_fa": "زمان‌های ساده: حال، گذشته و آینده",
        "use_en": "The simple tenses state facts. The simple present is a habit or a general truth; the simple past is a finished action at a known past time; the future with will is a prediction, a promise or a decision. None of the three says that an action was or will be in progress, and none of them connects two times.",
        "use_fa": "زمان‌های ساده واقعیت را می‌گویند. حال ساده عادت یا حقیقت کلی است؛ گذشتهٔ ساده کاری تمام‌شده در زمانی مشخص در گذشته است؛ آینده با will پیش‌بینی، قول یا تصمیم است. هیچ‌کدام نمی‌گوید کار در جریان بوده یا خواهد بود و هیچ‌کدام دو زمان را به هم پیوند نمی‌دهد.",
        "form_en": "present: verb / verb-s  ·  past: verb-ed / irregular  ·  future: will + base verb",
        "examples": [
            {"en": "I drink tea every morning.",
             "fa": "من هر صبح چای می‌نوشم."},
            {"en": "I drank tea with breakfast yesterday.",
             "fa": "دیروز صبحانه چای نوشیدم."},
            {"en": "I will drink tea with my guests tonight.",
             "fa": "امشب با مهمان‌هایم چای می‌نوشم."},
        ],
        "exercises": [
            ex("She ___ (walk) to school every day.", "walks",
               "Every day marks a habit, and she takes -s.",
               "every day عادت را نشان می‌دهد و با she فعل -s می‌گیرد."),
            ex("We ___ (visit) the museum last Friday.", "visited",
               "Last Friday is a finished past time, so the simple past.",
               "last Friday زمانی تمام‌شده در گذشته است، پس گذشتهٔ ساده."),
            ex("I think it ___ (snow) tomorrow.", "will snow",
               "A prediction about the future takes will and the base verb.",
               "پیش‌بینی دربارهٔ آینده با will و فعل ساده می‌آید."),
        ],
        "exam": [
            q("My father ___ the newspaper every evening.",
              ["reads", "is reading", "read"], "reads",
              "Every evening is a habit, and the subject is singular.",
              "every evening عادت است و فاعل مفرد."),
            q("They ___ the match two days ago.",
              ["lost", "have lost", "lose"], "lost",
              "Two days ago is a finished past time, so the simple past.",
              "two days ago زمانی تمام‌شده در گذشته است، پس گذشتهٔ ساده."),
            q("Don't worry, I ___ you tomorrow morning.",
              ["will call", "call", "called"], "will call",
              "A promise about the future takes will.",
              "قولی دربارهٔ آینده با will می‌آید."),
        ],
    },
    {
        "section": "4-2",
        "title": "Progressive tenses: an action in progress",
        "title_fa": "زمان‌های استمراری: کاری در جریان",
        "use_en": "The progressive tenses put an action in the middle of happening. The present progressive is happening now; the past progressive was happening at a past moment; the future progressive will be happening at a future moment. Each is a form of be plus the -ing form, and each usually answers “what was going on at that time?”",
        "use_fa": "زمان‌های استمراری کار را در میانهٔ انجام نشان می‌دهند. حال استمراری همین حالا در جریان است؛ گذشتهٔ استمراری در لحظه‌ای در گذشته در جریان بود؛ آیندهٔ استمراری در لحظه‌ای در آینده در جریان خواهد بود. هر یک با شکلی از be و فرم ing ساخته می‌شود و معمولاً پاسخ «آن لحظه چه کاری در جریان بود؟» است.",
        "form_en": "am / is / are + -ing  ·  was / were + -ing  ·  will be + -ing",
        "examples": [
            {"en": "Please be quiet; the baby is sleeping.",
             "fa": "لطفاً ساکت باش؛ نوزاد خواب است."},
            {"en": "At eight last night I was studying.",
             "fa": "دیشب ساعت هشت درس می‌خواندم."},
            {"en": "This time tomorrow we will be flying to Shiraz.",
             "fa": "فردا همین وقت به شیراز پرواز می‌کنیم."},
        ],
        "exercises": [
            ex("Look! The children ___ (play) in the yard.", "are playing",
               "The action is happening at the moment of speaking.",
               "کار در لحظهٔ گفتن در جریان است."),
            ex("When the phone rang, I ___ (cook) dinner.", "was cooking",
               "The cooking was in progress when the phone rang.",
               "آشپزی هنگام زنگ تلفن در جریان بود."),
            ex("At nine tomorrow, she ___ (teach) her first class.", "will be teaching",
               "An action in progress at a future moment takes will be + -ing.",
               "کاری که در لحظه‌ای در آینده در جریان است با will be + ing می‌آید."),
        ],
        "exam": [
            q("Why ___ you laughing?",
              ["are", "do", "is"], "are",
              "The present progressive question puts are before you.",
              "پرسش حال استمراری are را پیش از you می‌آورد."),
            q("While we ___ dinner, the lights went out.",
              ["were having", "had", "have had"], "were having",
              "The dinner was in progress when the lights went out.",
              "شام هنگام قطع برق در جریان بود."),
            q("Don't call at seven; we ___ dinner then.",
              ["will be having", "will have", "have"], "will be having",
              "The dinner will be in progress at that future time.",
              "شام در آن لحظهٔ آینده در جریان خواهد بود."),
        ],
    },
    {
        "section": "4-3",
        "title": "Perfect tenses: looking back from a point in time",
        "title_fa": "زمان‌های کامل: نگاه به عقب از یک نقطه در زمان",
        "use_en": "The perfect tenses connect two times. The present perfect (have or has plus the past participle) looks back from now: an experience, a repeated event, or something that started in the past and still matters. The past perfect (had plus the participle) looks back from a past moment, and the future perfect (will have plus the participle) looks back from a future one.",
        "use_fa": "زمان‌های کامل دو زمان را به هم پیوند می‌دهند. حال کامل (have یا has و اسم مفعول) از «اکنون» به عقب نگاه می‌کند: تجربه، رویداد تکراری، یا چیزی که در گذشته آغاز شده و هنوز مهم است. گذشتهٔ کامل (had و اسم مفعول) از لحظه‌ای در گذشته به عقب نگاه می‌کند و آیندهٔ کامل (will have و اسم مفعول) از لحظه‌ای در آینده.",
        "form_en": "have / has + past participle  ·  had + past participle  ·  will have + past participle",
        "examples": [
            {"en": "I have visited Isfahan three times.",
             "fa": "سه بار اصفهان رفته‌ام."},
            {"en": "When we arrived, the train had already left.",
             "fa": "وقتی رسیدیم، قطار پیش‌تر رفته بود."},
            {"en": "By next June, she will have finished the course.",
             "fa": "تا ژوئن آینده، او دوره را تمام کرده است."},
        ],
        "exercises": [
            ex("He ___ (live) in this city since 2018.", "has lived",
               "Since 2018 reaches from the past up to now, so the present perfect.",
               "since 2018 از گذشته تا حال ادامه دارد، پس حال کامل."),
            ex("The movie ___ (start) before we got to the cinema.", "had started",
               "The starting came before another past action.",
               "شروع فیلم پیش از رسیدن ما بود."),
            ex("By Friday, they ___ (finish) the project.", "will have finished",
               "By Friday looks back from a future point.",
               "by Friday از نقطه‌ای در آینده به عقب نگاه می‌کند."),
        ],
        "exam": [
            q("I ___ that movie, so I know the ending.",
              ["have seen", "saw", "had seen"], "have seen",
              "The experience matters now, so the present perfect.",
              "تجربه اکنون مهم است، پس حال کامل."),
            q("She ___ the letter before he called.",
              ["had written", "has written", "wrote"], "had written",
              "The writing came before another past action.",
              "نوشتن پیش از تماس او بود."),
            q("By 2030, the city ___ a new airport.",
              ["will have built", "will build", "has built"], "will have built",
              "By 2030 looks back from a future point, so the future perfect.",
              "by 2030 از نقطه‌ای در آینده به عقب نگاه می‌کند، پس آیندهٔ کامل."),
        ],
    },
    {
        "section": "4-4",
        "title": "Perfect progressive: how long an action has lasted",
        "title_fa": "کامل استمراری: مدتِ ادامهٔ یک کار",
        "use_en": "The perfect progressive measures a duration up to a point: have been with -ing up to now, had been with -ing up to a past moment, will have been with -ing up to a future one. It answers “how long?”. Verbs of state such as know, own and believe do not take the progressive, so they use the simple perfect instead: I have known her for years.",
        "use_fa": "کامل استمراری مدتِ ادامهٔ کار تا یک نقطه را می‌سنجد: have been با ing تا اکنون، had been با ing تا لحظه‌ای در گذشته، will have been با ing تا لحظه‌ای در آینده. پاسخ «چه مدت؟» است. افعال حالتی مانند know، own و believe استمراری نمی‌گیرند و به‌جای آن کامل ساده می‌آیند: I have known her for years.",
        "form_en": "have / has been + -ing  ·  had been + -ing  ·  will have been + -ing",
        "examples": [
            {"en": "They have been waiting for an hour.",
             "fa": "یک ساعت است که منتظرند."},
            {"en": "She had been working there for ten years when she resigned.",
             "fa": "ده سال آنجا کار کرده بود که استعفا داد."},
            {"en": "Next month I will have been teaching for twenty years.",
             "fa": "ماه آینده بیست سال است که درس می‌دهم."},
        ],
        "exercises": [
            ex("It ___ (rain) since morning.", "has been raining",
               "The rain started in the morning and is still going.",
               "باران از صبح شروع شده و هنوز ادامه دارد."),
            ex("He ___ (drive) for six hours when he stopped for fuel.", "had been driving",
               "The driving lasted up to the stop in the past.",
               "رانندگی تا توقف در گذشته ادامه داشت."),
            ex("By December, we ___ (work) on this for a year.", "will have been working",
               "A duration measured up to a future point.",
               "مدتی که تا نقطه‌ای در آینده سنجیده می‌شود."),
        ],
        "exam": [
            q("I ___ English for three years.",
              ["have been learning", "learn", "am learning"], "have been learning",
              "A duration continuing up to now takes the present perfect progressive.",
              "مدتی که تا اکنون ادامه دارد، حال کامل استمراری می‌گیرد."),
            q("They ___ for two hours when the bus finally came.",
              ["had been waiting", "have been waiting", "waited"], "had been waiting",
              "The waiting lasted up to a past moment.",
              "انتظار تا لحظه‌ای در گذشته ادامه داشت."),
            q("I ___ her since we were children.",
              ["have known", "have been knowing", "know"], "have known",
              "Know is a state, so it takes the simple perfect, not the progressive.",
              "know فعل حالتی است، پس کامل ساده می‌گیرد نه استمراری."),
        ],
    },
    {
        "section": "4-5",
        "title": "Choosing the tense: a review",
        "title_fa": "انتخاب زمان: یک مرور",
        "use_en": "Choose the tense from the time in the sentence, not from the language you are translating from. A finished past time (yesterday, last week, in 2019) takes the simple past. A connection to now, or a duration up to now, takes a present perfect. An action in progress at a moment takes a progressive. An action finished before another past action takes the past perfect. A habit or a general truth takes the simple present.",
        "use_fa": "زمان را از روی زمانِ جمله انتخاب کن، نه از روی زبانی که از آن ترجمه می‌کنی. زمان گذشتهٔ تمام‌شده (yesterday، last week، in 2019) گذشتهٔ ساده می‌گیرد. پیوند با اکنون یا مدتی تا اکنون، حال کامل می‌گیرد. کاری که در لحظه‌ای در جریان است، استمراری می‌گیرد. کاری که پیش از کار گذشتهٔ دیگری تمام شده، گذشتهٔ کامل می‌گیرد. عادت یا حقیقت کلی، حال ساده می‌گیرد.",
        "form_en": "finished past time → simple past  ·  link to now → present perfect  ·  in progress → progressive  ·  before a past point → past perfect",
        "examples": [
            {"en": "I saw him yesterday. I have seen him twice this week.",
             "fa": "دیروز او را دیدم. این هفته دو بار او را دیده‌ام."},
            {"en": "She was reading when I called, and she had finished the book by noon.",
             "fa": "وقتی زنگ زدم داشت می‌خواند و تا ظهر کتاب را تمام کرده بود."},
            {"en": "Water boils at 100 degrees.",
             "fa": "آب در صد درجه می‌جوشد."},
        ],
        "exercises": [
            ex("I ___ (see) that film last night.", "saw",
               "Last night is a finished past time, so the simple past.",
               "last night زمانی تمام‌شده در گذشته است، پس گذشتهٔ ساده."),
            ex("We ___ (know) each other for ten years.", "have known",
               "A duration up to now with a state verb takes the present perfect.",
               "مدت تا اکنون با فعل حالتی، حال کامل می‌گیرد."),
            ex("By the time the guests arrived, we ___ (prepare) everything.", "had prepared",
               "The preparing was complete before the guests arrived.",
               "آماده‌سازی پیش از رسیدن مهمان‌ها تمام شده بود."),
        ],
        "exam": [
            q("She ___ to Paris in 2019.",
              ["went", "has gone", "had gone"], "went",
              "A finished year in the past takes the simple past.",
              "سال تمام‌شده در گذشته گذشتهٔ ساده می‌گیرد."),
            q("I ___ here since eight o'clock.",
              ["have been sitting", "sit", "sat"], "have been sitting",
              "A duration continuing to now takes the present perfect progressive.",
              "مدتی که تا اکنون ادامه دارد، حال کامل استمراری می‌گیرد."),
            q("When I got home, my brother ___ dinner.",
              ["was cooking", "cooks", "has cooked"], "was cooking",
              "The cooking was in progress when I got home.",
              "آشپزی هنگام رسیدن من در جریان بود."),
        ],
    },
]

ABOUT_EN = ("The grammar of the whole course, chapter by chapter and chart by chart: "
            "fifty-four structures from the book's twenty chapters, each with the rule, "
            "a pattern, examples of it, exercises and a short exam. Chapters one to four "
            "are complete, chart 1-1 to 4-5. The explanations and sentences are written "
            "for this app; the book is the reference text.")
ABOUT_FA = ("دستور زبان تمام دوره، فصل به فصل و نمودار به نمودار: پنجاه‌وچهار ساختار از "
            "بیست فصل کتاب، هر یک با قاعده، الگو، مثال، تمرین و یک آزمون کوتاه. فصل‌های "
            "یک تا چهار کامل‌اند، از نمودار ۱-۱ تا ۴-۵. توضیح‌ها و جمله‌ها برای همین "
            "برنامه نوشته شده‌اند و کتاب متن مرجع است.")


def main() -> int:
    data = json.loads(BOOKS.read_text(encoding="utf-8"))
    book = next(b for b in data["books"] if b.get("kind") == "grammar")

    old = [l for l in book["lessons"] if l.get("chapter") == "Chapter 4"]
    assert old, "chapter four is not in the book"
    first = book["lessons"].index(old[0])
    rest = [l for l in book["lessons"] if l.get("chapter") != "Chapter 4"]

    chapter4 = []
    for lesson in LESSONS:
        chapter4.append({
            "n": 0, "title": lesson["title"], "title_fa": lesson["title_fa"],
            "chapter": "Chapter 4", "section": lesson["section"],
            "use_en": lesson["use_en"], "use_fa": lesson["use_fa"],
            "form_en": lesson["form_en"], "examples": lesson["examples"],
            "exercises": lesson["exercises"], "exam": lesson["exam"],
        })

    lessons = rest[:first] + chapter4 + rest[first:]
    for i, lesson in enumerate(lessons, 1):
        lesson["n"] = i
    book["lessons"] = lessons
    book["about_en"] = ABOUT_EN
    book["about_fa"] = ABOUT_FA

    BOOKS.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")
    print(f"chapter four: {len(chapter4)} charts, {len(lessons)} structures in the book")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
