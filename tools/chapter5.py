#!/usr/bin/env python3
"""Write chapter five of the grammar book into books.json.

    python3 tools/chapter5.py

Chapter five of *Understanding and Using English Grammar* is Subject-Verb
Agreement. The book shipped with one section for it ("5-2 Subject-verb
agreement"); this replaces it with six charts, written out like chapters one
to four: the rule, the form, examples in both languages, three guided
exercises and a three-question check for each.

It is idempotent: chapter five is always rebuilt from this script.
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
        "section": "5-1",
        "title": "Basic agreement: one subject, one verb",
        "title_fa": "تطابق پایه: یک فاعل، یک فعل",
        "use_en": "In the present, a singular subject takes a singular verb and a plural subject takes a plural verb. Only the third person singular adds -s: I play, she plays, they play. With be the whole word changes: I am, he is, they are. The rule is about grammar, not about how many people you can see — the subject decides.",
        "use_fa": "در زمان حال، فاعل مفرد فعل مفرد و فاعل جمع فعل جمع می‌گیرد. تنها سوم‌شخص مفرد -s می‌گیرد: I play، she plays، they play. با فعل be کل واژه تغییر می‌کند: I am، he is، they are. این قاعده دربارهٔ دستور است، نه دربارهٔ تعداد آدم‌هایی که می‌بینی — فاعل تعیین می‌کند.",
        "form_en": "singular subject + verb-s  ·  plural subject + verb  ·  I am / you are / he-she-it is",
        "examples": [
            {"en": "The boy plays football after school.",
             "fa": "پسر بعد از مدرسه فوتبال بازی می‌کند."},
            {"en": "The boys play football after school.",
             "fa": "پسرها بعد از مدرسه فوتبال بازی می‌کنند."},
            {"en": "My sister is a nurse, and my brothers are teachers.",
             "fa": "خواهرم پرستار است و برادرانم معلم‌اند."},
        ],
        "exercises": [
            ex("The girl ___ (read) a story every night.", "reads",
               "The subject is one girl, so the present takes -s.",
               "فاعل یک دختر است، پس حال -s می‌گیرد."),
            ex("The girl and her brother ___ (read) together.", "read",
               "Two subjects make a plural subject, so the verb has no -s.",
               "دو فاعل، فاعل جمع می‌سازند، پس فعل -s ندارد."),
            ex("My mother ___ (be) a doctor.", "is",
               "She is singular, so the form of be is is.",
               "فاعل مفرد است، پس شکل be می‌شود is."),
        ],
        "exam": [
            q("The cat ___ on the sofa every afternoon.",
              ["sleeps", "sleep", "are sleeping"], "sleeps",
              "One cat is singular and the sentence is a habit.",
              "یک گربه مفرد است و جمله عادت را می‌گوید."),
            q("My friends ___ in Tehran.",
              ["live", "lives", "is living"], "live",
              "Friends is plural, so the verb has no -s.",
              "friends جمع است، پس فعل -s ندارد."),
            q("You ___ very kind.",
              ["are", "is", "am"], "are",
              "You always takes are, singular or plural.",
              "you همیشه are می‌گیرد، مفرد یا جمع."),
        ],
    },
    {
        "section": "5-2",
        "title": "Final -s and -es: nouns and verbs",
        "title_fa": "پایانهٔ -s و -es: اسم‌ها و فعل‌ها",
        "use_en": "The same ending does two opposite jobs: on a noun, -s or -es makes it plural; on a verb, it makes the third person singular. So the student reads and the students read. Words ending in -ch, -sh, -ss, -x, -s or -o add -es, a consonant plus y changes to -ies, and a vowel plus y just adds -s.",
        "use_fa": "همین پایانه دو کار متضاد می‌کند: روی اسم، آن را جمع می‌کند؛ روی فعل، سوم‌شخص مفرد می‌سازد. پس the student reads و the students read. واژه‌های پایانه‌یافته به ch، sh، ss، x، s یا o، پسوند es می‌گیرند، حرف بی‌صدا + y به ies تبدیل می‌شود و حرف صدادار + y تنها s می‌گیرد.",
        "form_en": "noun: box → boxes, city → cities  ·  verb: watch → watches, study → studies",
        "examples": [
            {"en": "The bus stops at the corner, and the buses stop here too.",
             "fa": "اتوبوس سر خیابان می‌ایستد و اتوبوس‌ها هم اینجا می‌ایستند."},
            {"en": "My friend watches two movies every week.",
             "fa": "دوستم هر هفته دو فیلم می‌بیند."},
            {"en": "The city has many parks, and the cities around it have more.",
             "fa": "این شهر پارک‌های زیادی دارد و شهرهای اطرافش بیشتر."},
        ],
        "exercises": [
            ex("My sister ___ (study) English at university.", "studies",
               "A consonant plus y changes to -ies in the third person singular.",
               "حرف بی‌صدا + y در سوم‌شخص مفرد به ies تبدیل می‌شود."),
            ex("There are three ___ (city) in this province.", "cities",
               "Three makes the noun plural, so city becomes cities.",
               "سه، اسم را جمع می‌کند، پس city می‌شود cities."),
            ex("He ___ (watch) the news before dinner.", "watches",
               "A verb ending in -ch takes -es with he.",
               "فعل پایانه‌یافته به ch با he پسوند es می‌گیرد."),
        ],
        "exam": [
            q("The teacher ___ the question twice.",
              ["explains", "explain", "explaines"], "explains",
              "One teacher is singular, and explain simply adds -s.",
              "یک معلم مفرد است و explain تنها s می‌گیرد."),
            q("There are two ___ on the shelf.",
              ["boxes", "boxs", "boxies"], "boxes",
              "A noun ending in -x takes -es in the plural.",
              "اسم پایانه‌یافته به x در جمع es می‌گیرد."),
            q("The boys ___ football in the street.",
              ["play", "plays", "playes"], "play",
              "A plural subject takes the verb without -s.",
              "فاعل جمع فعل بدون s می‌گیرد."),
        ],
    },
    {
        "section": "5-3",
        "title": "Subjects joined by and, or and nor",
        "title_fa": "فاعل‌های پیوندیافته با and، or و nor",
        "use_en": "Two subjects joined by and make a plural subject: Ali and Reza are friends. When the two things are one idea or one unit, the verb stays singular: bread and butter is enough. With or, nor, either … or and neither … nor, the verb agrees with the subject nearer to it: neither the teacher nor the students were ready.",
        "use_fa": "دو فاعل که با and به هم می‌پیوندند فاعل جمع می‌سازند: Ali and Reza are friends. وقتی دو چیز یک اندیشه یا یک واحد باشند، فعل مفرد می‌ماند: bread and butter is enough. با or، nor، either … or و neither … nor فعل با فاعلی که به آن نزدیک‌تر است هم‌خوان می‌شود: neither the teacher nor the students were ready.",
        "form_en": "A and B + plural verb  ·  either A or B / neither A nor B + verb agreeing with B",
        "examples": [
            {"en": "Ali and Reza are cousins.",
             "fa": "علی و رضا پسرخاله‌اند."},
            {"en": "Rice and yogurt is my favorite lunch.",
             "fa": "برنج و ماست ناهار موردعلاقهٔ من است."},
            {"en": "Neither the manager nor the employees were told.",
             "fa": "نه مدیر و نه کارمندان خبر نداشتند."},
        ],
        "exercises": [
            ex("My brother and I ___ (be) in the same class.", "are",
               "Two subjects joined by and make a plural subject.",
               "دو فاعل با and فاعل جمع می‌سازند."),
            ex("Either the twins or Sara ___ (have) the key.", "has",
               "The verb agrees with the nearer subject, Sara, which is singular.",
               "فعل با فاعل نزدیک‌تر، Sara، هم‌خوان می‌شود که مفرد است."),
            ex("Neither the students nor the teacher ___ (know) the answer.", "knows",
               "The nearer subject is the teacher, which is singular.",
               "فاعل نزدیک‌تر the teacher است که مفرد است."),
        ],
        "exam": [
            q("My father and my uncle ___ engineers.",
              ["are", "is", "was"], "are",
              "Two subjects with and take a plural verb.",
              "دو فاعل با and فعل جمع می‌گیرند."),
            q("Neither the children nor their mother ___ at home.",
              ["was", "were", "are"], "was",
              "The nearer subject is mother, which is singular.",
              "فاعل نزدیک‌تر mother است که مفرد است."),
            q("Two hours and a good book ___ all I need.",
              ["is", "are", "were"], "is",
              "The two things form one idea, so the verb is singular.",
              "این دو چیز یک اندیشه می‌سازند، پس فعل مفرد است."),
        ],
    },
    {
        "section": "5-4",
        "title": "Prepositional phrases after the subject",
        "title_fa": "عبارت‌های حرف اضافه پس از فاعل",
        "use_en": "The verb agrees with the subject, not with a noun inside a phrase that follows it. In the box of books is heavy, the subject is the box; of books is only a phrase. The same is true of along with, as well as, together with and including: they add information, they do not make a singular subject plural.",
        "use_fa": "فعل با فاعل هم‌خوان می‌شود، نه با اسمی در عبارتی که پس از آن می‌آید. در the box of books is heavy فاعل the box است و of books تنها یک عبارت است. همین دربارهٔ along with، as well as، together with و including هم برجاست: اطلاعات اضافه می‌کنند و فاعل مفرد را جمع نمی‌کنند.",
        "form_en": "subject (+ phrase) + verb agreeing with the subject  ·  The box of books is heavy.",
        "examples": [
            {"en": "The box of books is heavy.",
             "fa": "جعبهٔ کتاب‌ها سنگین است."},
            {"en": "The students in the hall are noisy.",
             "fa": "دانش‌آموزان در سالن پرسروصدا هستند."},
            {"en": "The teacher, as well as the students, was surprised.",
             "fa": "معلم هم مثل دانش‌آموزان شگفت‌زده بود."},
        ],
        "exercises": [
            ex("The list of names ___ (be) on the desk.", "is",
               "The subject is the list, not names, so the verb is singular.",
               "فاعل the list است نه names، پس فعل مفرد است."),
            ex("The keys to the office ___ (be) in my bag.", "are",
               "The subject is the keys, which is plural.",
               "فاعل keys است که جمع است."),
            ex("My friend, together with her parents, ___ (travel) every summer.", "travels",
               "Together with adds information; the subject is still my friend.",
               "together with اطلاعات اضافه می‌کند و فاعل هنوز my friend است."),
        ],
        "exam": [
            q("The bag of oranges ___ on the table.",
              ["is", "are", "were"], "is",
              "The subject is the bag, so the verb is singular.",
              "فاعل the bag است، پس فعل مفرد است."),
            q("The players on the field ___ warming up.",
              ["are", "is", "was"], "are",
              "The subject is the players, which is plural.",
              "فاعل the players است که جمع است."),
            q("The director, along with the actors, ___ arrived.",
              ["has", "have", "are"], "has",
              "Along with does not change the singular subject.",
              "along with فاعل مفرد را تغییر نمی‌دهد."),
        ],
    },
    {
        "section": "5-5",
        "title": "There is and there are; amounts, titles and times",
        "title_fa": "there is و there are؛ مقدارها، عنوان‌ها و زمان‌ها",
        "use_en": "With there is and there are, the verb agrees with the noun that follows: there is a book, there are three chairs. A period of time, a distance, a sum of money or a weight treated as one unit takes a singular verb: ten dollars is enough. The title of a book, play or film is singular even when it is plural in form.",
        "use_fa": "با there is و there are فعل با اسمی که پس از آن می‌آید هم‌خوان می‌شود: there is a book، there are three chairs. بازهٔ زمانی، مسافت، مبلغ پول یا وزن که یک واحد شمرده شود فعل مفرد می‌گیرد: ten dollars is enough. عنوان کتاب، نمایش یا فیلم حتی اگر جمع باشد مفرد است.",
        "form_en": "There is + singular / noncount  ·  There are + plural  ·  Ten dollars is …  ·  The Times is …",
        "examples": [
            {"en": "There is a notebook in my bag, and there are two pens.",
             "fa": "در کیفم یک دفتر است و دو خودکار."},
            {"en": "Twenty minutes is enough for this walk.",
             "fa": "بیست دقیقه برای این پیاده‌روی کافی است."},
            {"en": "The Arabian Nights is on the shelf.",
             "fa": "کتاب هزار و یک شب روی قفسه است."},
        ],
        "exercises": [
            ex("There ___ (be) three windows in this room.", "are",
               "The noun after there is windows, which is plural.",
               "اسم پس از there واژهٔ windows است که جمع است."),
            ex("There ___ (be) a cat under the table.", "is",
               "The noun after there is a cat, which is singular.",
               "اسم پس از there واژهٔ a cat است که مفرد است."),
            ex("Fifty dollars ___ (be) too much for a shirt.", "is",
               "A sum of money treated as one amount takes a singular verb.",
               "مبلغی که یک واحد شمرده شود فعل مفرد می‌گیرد."),
        ],
        "exam": [
            q("There ___ many reasons to learn a language.",
              ["are", "is", "was"], "are",
              "Reasons is plural, so there are is used.",
              "reasons جمع است، پس there are به کار می‌رود."),
            q("Ten kilometers ___ a long walk.",
              ["is", "are", "were"], "is",
              "A distance is treated as one amount.",
              "مسافت یک مقدار شمرده می‌شود."),
            q("There ___ a letter for you on the table.",
              ["is", "are", "have"], "is",
              "The noun after there is singular.",
              "اسم پس از there مفرد است."),
        ],
    },
    {
        "section": "5-6",
        "title": "Indefinite pronouns, collective nouns and quantities",
        "title_fa": "ضمیرهای نامعین، اسم‌های جمعی و مقدارها",
        "use_en": "Everyone, everybody, someone, nobody, each, either and neither are singular: everyone has a ticket. Collective nouns such as team, family and class are singular in American English: the team is winning. With some of, most of, all of and none of, the verb follows the noun after of. A number of people are … but the number of people is …",
        "use_fa": "everyone، everybody، someone، nobody، each، either و neither مفردند: everyone has a ticket. اسم‌های جمعی مانند team، family و class در انگلیسی آمریکایی مفردند: the team is winning. با some of، most of، all of و none of فعل از اسم پس از of پیروی می‌کند. a number of people are … اما the number of people is …",
        "form_en": "everyone / each / nobody + singular verb  ·  some of + plural noun → plural verb  ·  the team is",
        "examples": [
            {"en": "Everyone in the class has a notebook.",
             "fa": "همهٔ افراد کلاس دفتر دارند."},
            {"en": "Some of the water is cold, and some of the apples are green.",
             "fa": "بخشی از آب سرد است و برخی از سیب‌ها سبزند."},
            {"en": "The team is practicing for the final.",
             "fa": "تیم برای فینال تمرین می‌کند."},
        ],
        "exercises": [
            ex("Everyone ___ (need) a password.", "needs",
               "Everyone is grammatically singular, whatever it means.",
               "everyone از نظر دستوری مفرد است، هر چه معنا داشته باشد."),
            ex("Most of the students ___ (be) ready.", "are",
               "The noun after of is plural, so the verb is plural.",
               "اسم پس از of جمع است، پس فعل جمع است."),
            ex("The family ___ (be) at the table.", "is",
               "A collective noun is singular in American English.",
               "اسم جمعی در انگلیسی آمریکایی مفرد است."),
        ],
        "exam": [
            q("Nobody ___ the answer.",
              ["knows", "know", "are knowing"], "knows",
              "Nobody is singular, so the verb takes -s.",
              "nobody مفرد است، پس فعل -s می‌گیرد."),
            q("Some of the cake ___ left.",
              ["is", "are", "were"], "is",
              "Cake is noncount, so the verb is singular.",
              "cake غیرقابل‌شمارش است، پس فعل مفرد است."),
            q("The number of students ___ growing.",
              ["is", "are", "were"], "is",
              "The number of is singular; a number of would be plural.",
              "the number of مفرد است؛ a number of جمع می‌شد."),
        ],
    },
]

ABOUT_EN = ("The grammar of the whole course, chapter by chapter and chart by chart: "
            "fifty-nine structures from the book's twenty chapters, each with the rule, "
            "a pattern, examples of it, exercises and a short exam. Chapters one to five "
            "are complete, chart 1-1 to 5-6. The explanations and sentences are written "
            "for this app; the book is the reference text.")
ABOUT_FA = ("دستور زبان تمام دوره، فصل به فصل و نمودار به نمودار: پنجاه‌ونه ساختار از "
            "بیست فصل کتاب، هر یک با قاعده، الگو، مثال، تمرین و یک آزمون کوتاه. فصل‌های "
            "یک تا پنج کامل‌اند، از نمودار ۱-۱ تا ۵-۶. توضیح‌ها و جمله‌ها برای همین "
            "برنامه نوشته شده‌اند و کتاب متن مرجع است.")


def main() -> int:
    data = json.loads(BOOKS.read_text(encoding="utf-8"))
    book = next(b for b in data["books"] if b.get("kind") == "grammar")

    old = [l for l in book["lessons"] if l.get("chapter") == "Chapter 5"]
    assert old, "chapter five is not in the book"
    first = book["lessons"].index(old[0])
    rest = [l for l in book["lessons"] if l.get("chapter") != "Chapter 5"]

    chapter5 = []
    for lesson in LESSONS:
        chapter5.append({
            "n": 0, "title": lesson["title"], "title_fa": lesson["title_fa"],
            "chapter": "Chapter 5", "section": lesson["section"],
            "use_en": lesson["use_en"], "use_fa": lesson["use_fa"],
            "form_en": lesson["form_en"], "examples": lesson["examples"],
            "exercises": lesson["exercises"], "exam": lesson["exam"],
        })

    lessons = rest[:first] + chapter5 + rest[first:]
    for i, lesson in enumerate(lessons, 1):
        lesson["n"] = i
    book["lessons"] = lessons
    book["about_en"] = ABOUT_EN
    book["about_fa"] = ABOUT_FA

    BOOKS.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")
    print(f"chapter five: {len(chapter5)} charts, {len(lessons)} structures in the book")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
