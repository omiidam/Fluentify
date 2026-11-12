#!/usr/bin/env python3
"""Write chapter sixteen of the grammar book into books.json.

    python3 tools/chapter16.py

Chapter sixteen of *Understanding and Using English Grammar* is Coordinating
Conjunctions. The book shipped with one placeholder section for it; this replaces
it with the chapter's four charts, written out like chapters three to fifteen:
the rule, the form, examples in both languages, three guided exercises and a
three-question check for each.

The sentences and explanations are written for this app. The book is the
reference text, and nothing in this file is transcribed from it.

It is idempotent: chapter sixteen is always rebuilt from this script.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "books.json"

CHAPTER = "Chapter 16"


def ex(prompt, answer, why_en, why_fa):
    return {"prompt": prompt, "answer": answer, "why_en": why_en, "why_fa": why_fa}


def q(text, options, answer, why_en, why_fa):
    assert answer in options and len(options) == 3, text
    return {"q": text, "options": options, "answer": answer,
            "why_en": why_en, "why_fa": why_fa}


LESSONS = [
    {
        "section": "16-1",
        "title": "Parallel structure: matching forms in a list",
        "title_fa": "ساختار موازی: هم‌شکل کردن اجزا در یک فهرست",
        "use_en": "Items joined by and, or or but must have the same grammatical shape. A list of activities stays a list of activities: she likes hiking, swimming and cycling, not she likes hiking, swimming and to cycle. The same rule holds inside a pair: the job requires patience and accuracy, not patience and being accurate. Read the sentence backwards from the conjunction to check that each item matches.",
        "use_fa": "اجزایی که با and، or یا but به هم می‌پیوندند باید شکل دستوری یکسان داشته باشند. فهرست فعالیت‌ها فهرست فعالیت می‌ماند: she likes hiking, swimming and cycling و نه she likes hiking, swimming and to cycle. همین قاعده در یک جفت هم برقرار است: the job requires patience and accuracy و نه patience and being accurate. جمله را از حرف ربط به عقب بخوانید تا هم‌شکلی اجزا را بررسی کنید.",
        "form_en": "word + word  ·  -ing + -ing + -ing  ·  clause + and + clause",
        "examples": [
            {"en": "She likes hiking, swimming and cycling.",
             "fa": "او کوه‌پیمایی، شنا و دوچرخه‌سواری را دوست دارد."},
            {"en": "The job requires patience and accuracy.",
             "fa": "این کار صبر و دقت می‌خواهد."},
            {"en": "He opened the door, turned on the light and sat down.",
             "fa": "در را باز کرد، چراغ را روشن کرد و نشست."},
        ],
        "exercises": [
            ex("She is intelligent, hard-working and ___ (patience).", "patient",
               "An adjective list takes an adjective.",
               "فهرست صفت، صفت می‌گیرد."),
            ex("We spent the day swimming, reading and ___ . (relax)", "relaxing",
               "The list of activities stays in the -ing form.",
               "فهرست فعالیت‌ها در شکل ing- می‌ماند."),
            ex("He wants to travel, to learn and ___ new people. (meet)", "to meet",
               "The infinitives stay parallel.",
               "مصدرها موازی می‌مانند."),
        ],
        "exam": [
            q("Which list is parallel?",
              ["reading, writing and speaking", "reading, writing and to speak",
               "reading, to write and speaking"], "reading, writing and speaking",
              "All three items are gerunds.",
              "هر سه جزء اسم مصدرند."),
            q("The flat is small, quiet and ___.",
              ["cheap", "cheaply", "cheapness"], "cheap",
              "An adjective list needs adjectives.",
              "فهرست صفت به صفت نیاز دارد."),
            q("She came in, sat down and ___ her bag.",
              ["opened", "opening", "to open"], "opened",
              "The past verbs stay parallel.",
              "فعل‌های گذشته موازی می‌مانند."),
        ],
    },
    {
        "section": "16-2",
        "title": "Parallel structure with commas",
        "title_fa": "ساختار موازی با ویرگول",
        "use_en": "A list of three or more parallel items takes a comma between each pair and a comma before the conjunction: we bought bread, cheese, and olives. The final comma is optional in British writing and usual in American writing, but it must be consistent within a document. Two items take no comma at all, and a comma between two items joined by and is a common error.",
        "use_fa": "فهرست سه یا چند جزء موازی میان هر جفت ویرگول می‌گیرد و پیش از حرف ربط هم ویرگول: we bought bread, cheese, and olives. ویرگول آخر در نوشتار بریتانیایی اختیاری و در آمریکایی رایج است، اما باید در یک متن یکدست باشد. دو جزء هیچ ویرگولی نمی‌گیرند و ویرگول میان دو جزءِ پیوسته با and خطایی رایج است.",
        "form_en": "item, item, and item  ·  item and item (no comma)",
        "examples": [
            {"en": "We bought bread, cheese, and olives.",
             "fa": "نان، پنیر و زیتون خریدیم."},
            {"en": "The course covers grammar, writing, and listening.",
             "fa": "دوره دستور زبان، نوشتار و شنیداری را در بر می‌گیرد."},
            {"en": "She plays tennis and volleyball.",
             "fa": "او تنیس و والیبال بازی می‌کند."},
        ],
        "exercises": [
            ex("We need milk ___ eggs and butter. (third item)", "comma",
               "The item before the conjunction takes a comma.",
               "جزء پیش از حرف ربط ویرگول می‌گیرد."),
            ex("Two items joined by and take ___ comma.", "no",
               "A pair needs no comma.",
               "جفت ویرگول لازم ندارد."),
            ex("She speaks French, Spanish ___ Italian. (list of three)", "and",
               "The last item follows the conjunction.",
               "جزء آخر پس از حرف ربط می‌آید."),
        ],
        "exam": [
            q("Which sentence is punctuated correctly?",
              ["He bought a pen, a notebook, and a ruler.",
               "He bought a pen a notebook and a ruler.",
               "He bought a pen, a notebook and, a ruler."],
              "He bought a pen, a notebook, and a ruler.",
              "Commas separate the items and the conjunction closes the list.",
              "ویرگول‌ها اجزا را جدا می‌کنند و حرف ربط فهرست را می‌بندد."),
            q("Two nouns joined by and need ___.",
              ["no comma", "one comma", "two commas"], "no comma",
              "A pair takes no comma.",
              "جفت ویرگول نمی‌گیرد."),
            q("Which list keeps the items parallel?",
              ["soup, salad, and bread", "soup, salad, and some bread to eat",
               "soup, a salad, and breads"], "soup, salad, and bread",
              "Three nouns keep the list parallel.",
              "سه اسم فهرست را موازی نگه می‌دارند."),
        ],
    },
    {
        "section": "16-3",
        "title": "Punctuation between independent clauses: and, but, so",
        "title_fa": "نگارش میان جمله‌های مستقل: and، but، so",
        "use_en": "Two independent clauses joined by and, but, so, or, yet or for need a comma before the conjunction: I was tired, so I went to bed. Without the conjunction the same two clauses need a semicolon or a full stop; a comma alone is a comma splice and is an error. If one side cannot stand alone, no comma is needed: I went to bed because I was tired.",
        "use_fa": "دو جملهٔ مستقل که با and، but، so، or، yet یا for به هم می‌پیوندند پیش از حرف ربط ویرگول می‌گیرند: I was tired, so I went to bed. بدون حرف ربط همان دو جمله نقطه‌ویرگول یا نقطه می‌خواهند و تنها ویرگول خطای «ویرگول چسبان» است. اگر یک طرف به‌تنهایی جمله نباشد ویرگول لازم نیست: I went to bed because I was tired.",
        "form_en": "clause + , + and / but / so + clause  ·  clause; clause  ·  clause + . + Clause",
        "examples": [
            {"en": "I was tired, so I went to bed.",
             "fa": "خسته بودم، پس به رختخواب رفتم."},
            {"en": "She studied hard, but she did not pass.",
             "fa": "سخت درس خواند، اما قبول نشد."},
            {"en": "The rain stopped; we went out.",
             "fa": "باران بند آمد؛ بیرون رفتیم."},
        ],
        "exercises": [
            ex("It was late, ___ we called a taxi. (result)", "so",
               "A result between two clauses takes so after the comma.",
               "نتیجه میان دو جمله پس از ویرگول so می‌گیرد."),
            ex("He wanted to come, ___ he had no time. (contrast)", "but",
               "A contrast between clauses takes but.",
               "تضاد میان دو جمله but می‌گیرد."),
            ex("She opened the window; the room ___ cooler. (second clause)", "became",
               "A semicolon joins two independent clauses.",
               "نقطه‌ویرگول دو جملهٔ مستقل را به هم می‌پیوندد."),
        ],
        "exam": [
            q("Which sentence is correct?",
              ["We were late, so we took a taxi.", "We were late, we took a taxi.",
               "We were late so, we took a taxi."], "We were late, so we took a taxi.",
              "Comma before so, then the second clause.",
              "ویرگول پیش از so و سپس جملهٔ دوم."),
            q("A comma alone between two full clauses is called ___.",
              ["a comma splice", "a semicolon", "a fragment"], "a comma splice",
              "Two independent clauses need a conjunction or a semicolon.",
              "دو جملهٔ مستقل حرف ربط یا نقطه‌ویرگول می‌خواهند."),
            q("Which needs no comma?",
              ["I stayed home because it rained.", "I stayed home, it rained.",
               "It rained, I stayed home."], "I stayed home because it rained.",
              "One side is dependent, so no comma separates them.",
              "یک طرف وابسته است، پس ویرگولی جدا نمی‌کند."),
        ],
    },
    {
        "section": "16-4",
        "title": "Paired conjunctions: both ... and, not only ... but also",
        "title_fa": "حروف ربط جفتی: both ... and، not only ... but also",
        "use_en": "Paired conjunctions join two items of the same kind: both the manager and the staff agreed, she not only sings but also writes songs, either we leave now or we miss the train, neither the food nor the service was good. The verb after either ... or and neither ... nor agrees with the nearer subject. What follows each half of the pair must be parallel.",
        "use_fa": "حروف ربط جفتی دو جزء هم‌نوع را به هم می‌پیوندند: both the manager and the staff agreed، she not only sings but also writes songs، either we leave now or we miss the train، neither the food nor the service was good. فعل پس از either ... or و neither ... nor با فاعل نزدیک‌تر مطابقت می‌کند. آنچه پس از هر نیمهٔ جفت می‌آید باید موازی باشد.",
        "form_en": "both A and B · not only A but also B · either A or B · neither A nor B",
        "examples": [
            {"en": "Both the manager and the staff agreed.",
             "fa": "هم مدیر و هم کارکنان موافقت کردند."},
            {"en": "She not only sings but also writes songs.",
             "fa": "او نه‌تنها می‌خواند بلکه ترانه هم می‌نویسد."},
            {"en": "Neither the food nor the service was good.",
             "fa": "نه غذا خوب بود نه خدمات."},
        ],
        "exercises": [
            ex("___ my brother nor my sister speaks French. (paired negative)", "Neither",
               "The pair neither ... nor joins two negatives.",
               "جفت neither ... nor دو منفی را به هم می‌پیوندد."),
            ex("You can ___ walk or take the bus. (paired choice)", "either",
               "Either ... or offers a choice.",
               "either ... or انتخاب را پیش می‌گذارد."),
            ex("Both the teacher ___ the students were late. (paired affirmative)", "and",
               "Both pairs with and.",
               "both با and جفت می‌شود."),
        ],
        "exam": [
            q("Neither the players nor the coach ___ happy.",
              ["was", "were", "be"], "was",
              "The verb agrees with the nearer subject, the coach.",
              "فعل با فاعل نزدیک‌تر، یعنی coach، مطابقت می‌کند."),
            q("He is not only clever ___ kind.",
              ["but also", "and also", "or also"], "but also",
              "The pair is not only ... but also.",
              "جفت همان not only ... but also است."),
            q("Which sentence keeps the pair parallel?",
              ["She enjoys both reading and writing.", "She enjoys both reading and to write.",
               "She enjoys both to read and writing."], "She enjoys both reading and writing.",
              "Both halves of the pair take the same form.",
              "دو نیمهٔ جفت شکل یکسان می‌گیرند."),
        ],
    },
]


def main() -> int:
    data = json.loads(BOOKS.read_text(encoding="utf-8"))
    book = next(b for b in data["books"] if b.get("kind") == "grammar")

    old = [l for l in book["lessons"] if l.get("chapter") == CHAPTER]
    assert old, "chapter sixteen is not in the book"

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
    book["about_en"] = (
        f"The grammar of the whole course, chapter by chapter and chart by chart: "
        f"{size} structures from the book's twenty chapters, each with the rule, "
        f"a pattern, examples of it, exercises and a short exam. Chapters one to "
        f"sixteen are complete, chart 1-1 to 16-4. The explanations and sentences "
        f"are written for this app; the book is the reference text."
    )
    book["about_fa"] = (
        f"دستور زبان تمام دوره، فصل به فصل و نمودار به نمودار: {size} ساختار از "
        f"بیست فصل کتاب، هر یک با قاعده، الگو، مثال، تمرین و یک آزمون کوتاه. "
        f"فصل‌های یک تا شانزده کامل‌اند، از نمودار ۱-۱ تا ۱۶-۴. توضیح‌ها و جمله‌ها "
        f"برای همین برنامه نوشته شده‌اند و کتاب متن مرجع است."
    )

    BOOKS.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")
    print(f"chapter sixteen: {len(LESSONS)} charts, {size} structures in the book")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
