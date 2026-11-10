#!/usr/bin/env python3
"""Write chapter eight of the grammar book into books.json.

    python3 tools/chapter8.py

Chapter eight of *Understanding and Using English Grammar* is Pronouns. The
book shipped with two sections for it (8-1 pronouns and possessives, 8-4
reflexives); this replaces them with the chapter's nine charts, written out
like chapters one to seven: the rule, the form, examples in both languages,
three guided exercises and a three-question check for each.

It is idempotent: chapter eight is always rebuilt from this script.
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
        "section": "8-1",
        "title": "Personal pronouns: subject and object",
        "title_fa": "ضمیرهای شخصی: فاعلی و مفعولی",
        "use_en": "A pronoun replaces a noun so it does not have to be repeated. Subject pronouns do the action: I, you, he, she, it, we, they. Object pronouns receive it: me, you, him, her, it, us, them. English keeps the subject even when the verb is obvious, and a pronoun must agree with the noun it replaces in number and gender.",
        "use_fa": "ضمیر جای اسم می‌نشیند تا لازم نباشد تکرار شود. ضمیر فاعلی کار را انجام می‌دهد: I، you، he، she، it، we، they. ضمیر مفعولی آن را می‌گیرد: me، you، him، her، it، us، them. انگلیسی فاعل را حتی وقتی فعل روشن است نگه می‌دارد و ضمیر باید در شمار و جنس با اسمی که جای آن آمده هم‌خوان باشد.",
        "form_en": "subject: I / you / he / she / it / we / they  ·  object: me / you / him / her / it / us / them",
        "examples": [
            {"en": "My brother is a teacher. He works in a small school.",
             "fa": "برادرم معلم است. او در مدرسهٔ کوچکی کار می‌کند."},
            {"en": "I called Sara and told her the news.",
             "fa": "به سارا زنگ زدم و خبر را به او گفتم."},
            {"en": "The keys are on the table. Can you bring them?",
             "fa": "کلیدها روی میز است. می‌توانی آن‌ها را بیاوری؟"},
        ],
        "exercises": [
            ex("Ali is late. ___ is still at work.", "He",
               "Ali is male and singular, and the pronoun is the subject.",
               "علی مذکر و مفرد است و ضمیر فاعل است."),
            ex("I saw Maryam yesterday and gave ___ the book.", "her",
               "The pronoun is the indirect object and Maryam is female.",
               "ضمیر مفعول غیرمستقیم است و مریم مؤنث."),
            ex("The children are tired. Please help ___.", "them",
               "Children is plural and the pronoun is the object.",
               "children جمع است و ضمیر مفعول است."),
        ],
        "exam": [
            q("My parents are visiting. I am cooking for ___ .",
              ["them", "they", "their"], "them",
              "After a preposition the object pronoun is used.",
              "پس از حرف اضافه ضمیر مفعولی می‌آید."),
            q("The book is interesting. ___ was written in 1990.",
              ["It", "He", "She"], "It",
              "A book is a thing, so the pronoun is it.",
              "کتاب شیء است، پس ضمیر it است."),
            q("Sara and I are ready. ___ can leave now.",
              ["We", "Us", "Them"], "We",
              "Sara and I together make we, and it is the subject.",
              "سارا و من با هم we می‌شوند و فاعل است."),
        ],
    },
    {
        "section": "8-2",
        "title": "Possessive adjectives and possessive pronouns",
        "title_fa": "صفت‌های ملکی و ضمیرهای ملکی",
        "use_en": "A possessive adjective stands before a noun: my book, your car, their house. A possessive pronoun stands alone and names the thing itself: mine, yours, his, hers, ours, theirs. English has no apostrophe in any of them: its is possessive, it's means it is.",
        "use_fa": "صفت ملکی پیش از اسم می‌آید: my book، your car، their house. ضمیر ملکی تنها می‌آید و خودِ چیز را نام می‌برد: mine، yours، his، hers، ours، theirs. هیچ‌کدام آپاستروف ندارند: its ملکی است و it's یعنی it is.",
        "form_en": "adjective + noun: my / your / his / her / its / our / their  ·  pronoun alone: mine / yours / his / hers / its / ours / theirs",
        "examples": [
            {"en": "This is my bag, and that one is yours.",
             "fa": "این کیف من است و آن یکی مال تو."},
            {"en": "Their house is bigger than ours.",
             "fa": "خانهٔ آن‌ها از خانهٔ ما بزرگ‌تر است."},
            {"en": "The cat licked its paw.",
             "fa": "گربه پنجه‌اش را لیسید."},
        ],
        "exercises": [
            ex("This is Sara's notebook; that one is ___ (I).", "mine",
               "A possessive pronoun stands alone, and I becomes mine.",
               "ضمیر ملکی تنها می‌آید و I به mine تبدیل می‌شود."),
            ex("The students forgot ___ books at home.", "their",
               "A possessive adjective before a noun agrees with students.",
               "صفت ملکی پیش از اسم با students هم‌خوان است."),
            ex("The dog hurt ___ leg.", "its",
               "Its is the possessive of it, with no apostrophe.",
               "its ملکیِ it است و آپاستروف ندارد."),
        ],
        "exam": [
            q("Is this pen ___ ?",
              ["yours", "your", "you"], "yours",
              "Nothing follows, so the possessive pronoun is needed.",
              "چیزی پس از آن نمی‌آید، پس ضمیر ملکی لازم است."),
            q("Sara invited ___ friends to dinner.",
              ["her", "hers", "she"], "her",
              "A possessive adjective stands before the noun friends.",
              "صفت ملکی پیش از اسم friends می‌آید."),
            q("The company changed ___ name last year.",
              ["its", "it's", "their"], "its",
              "Its is possessive; it's is only a contraction of it is.",
              "its ملکی است؛ it's تنها کوتاه‌شدهٔ it is است."),
        ],
    },
    {
        "section": "8-3",
        "title": "Reflexive pronouns: myself, yourself, themselves",
        "title_fa": "ضمیرهای انعکاسی: myself، yourself، themselves",
        "use_en": "A reflexive pronoun points back to the subject: I taught myself, she hurt herself, they enjoyed themselves. The forms are myself, yourself, himself, herself, itself, ourselves, yourselves, themselves — never hisself or theirselves. Use a reflexive only when the subject and the object are the same person.",
        "use_fa": "ضمیر انعکاسی به فاعل بازمی‌گردد: I taught myself، she hurt herself، they enjoyed themselves. شکل‌ها عبارت‌اند از myself، yourself، himself، herself، itself، ourselves، yourselves، themselves — هرگز hisself یا theirselves. ضمیر انعکاسی را تنها وقتی به کار ببر که فاعل و مفعول یک نفر باشند.",
        "form_en": "subject + verb + -self / -selves  (myself, yourself, himself, herself, itself, ourselves, yourselves, themselves)",
        "examples": [
            {"en": "I cut myself while cooking.",
             "fa": "هنگام آشپزی دستم را بریدم."},
            {"en": "The children dressed themselves.",
             "fa": "بچه‌ها خودشان لباس پوشیدند."},
            {"en": "She taught herself to play the piano.",
             "fa": "او خودش نواختن پیانو را یاد گرفت."},
        ],
        "exercises": [
            ex("He hurt ___ while playing football.", "himself",
               "The subject and the object are the same male person.",
               "فاعل و مفعول یک مرد است."),
            ex("We enjoyed ___ at the party.", "ourselves",
               "The subject is we, so the reflexive is ourselves.",
               "فاعل we است، پس ضمیر انعکاسی ourselves است."),
            ex("Please help ___ to some tea.", "yourselves",
               "The subject is plural you, so yourselves.",
               "فاعل you جمع است، پس yourselves."),
        ],
        "exam": [
            q("She looked at ___ in the mirror.",
              ["herself", "her", "hisself"], "herself",
              "The subject and the object are the same woman.",
              "فاعل و مفعول یک زن است."),
            q("The boys built the treehouse ___ .",
              ["themselves", "theirselves", "them"], "themselves",
              "The correct plural reflexive is themselves.",
              "شکل درست جمع، themselves است."),
            q("I made this cake ___ .",
              ["myself", "me", "mine"], "myself",
              "The subject I and the object are the same person.",
              "فاعل I و مفعول یک نفرند."),
        ],
    },
    {
        "section": "8-4",
        "title": "Pronouns in agreement: everyone, one and they",
        "title_fa": "تطابق ضمیرها: everyone، one و they",
        "use_en": "Everyone, everybody, someone and nobody are grammatically singular, so they take a singular verb: everyone has a ticket. When the sex is unknown, English now uses they for the later pronoun: someone left their bag. In formal writing, one can be used for people in general, with one or one's later.",
        "use_fa": "everyone، everybody، someone و nobody از نظر دستوری مفردند، پس فعل مفرد می‌گیرند: everyone has a ticket. وقتی جنسیت معلوم نیست، انگلیسی امروز برای ضمیر بعدی they را به کار می‌برد: someone left their bag. در نوشتار رسمی می‌توان one را برای مردم به‌طور کلی به کار برد و بعداً one یا one's آورد.",
        "form_en": "everyone / someone / nobody + singular verb  ·  later pronoun: they / their",
        "examples": [
            {"en": "Everyone has brought their own lunch.",
             "fa": "هر کسی ناهار خودش را آورده است."},
            {"en": "Someone left their umbrella in the hall.",
             "fa": "کسی چترش را در راهرو جا گذاشته است."},
            {"en": "One should always check one's work.",
             "fa": "آدم باید همیشه کارش را بررسی کند."},
        ],
        "exercises": [
            ex("Everyone ___ (need) a password.", "needs",
               "Everyone is grammatically singular, so the verb takes -s.",
               "everyone از نظر دستوری مفرد است، پس فعل -s می‌گیرد."),
            ex("Nobody called, did ___ ?", "they",
               "The tag question uses they when the subject's sex is unknown.",
               "پرسش تأکیدی با they می‌آید چون جنسیت فاعل معلوم نیست."),
            ex("Someone has left ___ coat on the chair.", "their",
               "Modern English uses their for a person of unknown sex.",
               "انگلیسی امروز برای شخص نامعلوم their را به کار می‌برد."),
        ],
        "exam": [
            q("Everybody ___ finished the exercise.",
              ["has", "have", "are"], "has",
              "Everybody is singular despite meaning many people.",
              "everybody با وجود معنای جمع، مفرد است."),
            q("If anyone calls, tell ___ I am out.",
              ["them", "him", "us"], "them",
              "The sex of the caller is unknown, so they is used.",
              "جنسیت تماس‌گیرنده معلوم نیست، پس they به کار می‌رود."),
            q("___ should respect other people's time.",
              ["One", "They", "You"], "One",
              "One is the formal pronoun for people in general.",
              "one ضمیر رسمی برای مردم به‌طور کلی است."),
        ],
    },
    {
        "section": "8-5",
        "title": "Indefinite pronouns: someone, anyone, no one, everyone",
        "title_fa": "ضمیرهای نامعین: someone، anyone، no one، everyone",
        "use_en": "Someone and somebody are used in affirmative sentences, anyone and anybody in questions and negatives, and no one and nobody in a negative meaning with a positive verb. They are all singular and are written as two words with no one. A phrase can follow them: someone in the office.",
        "use_fa": "someone و somebody در جملهٔ مثبت، anyone و anybody در پرسش و منفی، و no one و nobody برای معنای منفی با فعل مثبت به کار می‌روند. همه مفردند و no one جدا نوشته می‌شود. می‌توان عبارتی پس از آن‌ها آورد: someone in the office.",
        "form_en": "affirmative: someone / somebody  ·  question or negative: anyone / anybody  ·  negative meaning: no one / nobody",
        "examples": [
            {"en": "Someone is waiting at the door.",
             "fa": "کسی پشت در منتظر است."},
            {"en": "Did anyone see my keys?",
             "fa": "کسی کلیدهای من را دید؟"},
            {"en": "No one knows the answer.",
             "fa": "هیچ‌کس جواب را نمی‌داند."},
        ],
        "exercises": [
            ex("I did not meet ___ at the station.", "anyone",
               "A negative sentence takes anyone, not someone.",
               "جملهٔ منفی anyone می‌گیرد، نه someone."),
            ex("___ left a message for you this morning.", "Someone",
               "An affirmative statement takes someone.",
               "جملهٔ مثبت someone می‌گیرد."),
            ex("___ one was at home when I called.", "No",
               "No one is written as two words and means nobody.",
               "no one جدا نوشته می‌شود و معنای nobody دارد."),
        ],
        "exam": [
            q("Is there ___ in the office?",
              ["anyone", "someone", "no one"], "anyone",
              "A question takes anyone.",
              "پرسش anyone می‌گیرد."),
            q("___ knows where he went.",
              ["Nobody", "Anybody", "Somebody"], "Nobody",
              "A negative meaning with a positive verb is nobody.",
              "معنای منفی با فعل مثبت با nobody می‌آید."),
            q("I have ___ to tell you.",
              ["something", "anything", "nothing"], "something",
              "An affirmative sentence takes something.",
              "جملهٔ مثبت something می‌گیرد."),
        ],
    },
    {
        "section": "8-6",
        "title": "One and ones: replacing a noun",
        "title_fa": "one و ones: جانشین اسم",
        "use_en": "One replaces a singular count noun that is already understood, and ones replaces a plural one: the red shirt or the blue one, these apples or those ones. They cannot replace a noncount noun: the water, not the one. Without an adjective, one is usually left out: which book? This one.",
        "use_fa": "one جانشین اسم قابل‌شمارش مفردِ شناخته‌شده می‌شود و ones جانشین جمع: the red shirt or the blue one، these apples or those ones. جانشین اسم غیرقابل‌شمارش نمی‌شوند: the water، نه the one. بدون صفت معمولاً one حذف می‌شود: which book? This one.",
        "form_en": "adjective + one / ones  ·  not used for noncount nouns",
        "examples": [
            {"en": "I like the red shirt more than the blue one.",
             "fa": "پیراهن قرمز را بیشتر از آبی دوست دارم."},
            {"en": "These apples are sweeter than those ones.",
             "fa": "این سیب‌ها از آن‌ها شیرین‌ترند."},
            {"en": "Which book do you want? This one.",
             "fa": "کدام کتاب را می‌خواهی؟ همین یکی."},
        ],
        "exercises": [
            ex("I prefer the small car to the big ___.", "one",
               "One replaces the singular count noun car.",
               "one جانشین اسم قابل‌شمارش مفرد car می‌شود."),
            ex("She bought fresh flowers, not the old ___.", "ones",
               "Ones replaces the plural count noun flowers.",
               "ones جانشین اسم قابل‌شمارش جمع flowers می‌شود."),
            ex("The water in this glass is colder than the ___ in that one.", "water",
               "A noncount noun is repeated or left out, never replaced by one.",
               "اسم غیرقابل‌شمارش تکرار یا حذف می‌شود و با one جانشین نمی‌شود."),
        ],
        "exam": [
            q("These shoes are cheaper than those ___ .",
              ["ones", "one", "shoe"], "ones",
              "Shoes is plural, so ones.",
              "shoes جمع است، پس ones."),
            q("I need a pen. Do you have a blue ___ ?",
              ["one", "ones", "it"], "one",
              "Pen is singular and countable, so one.",
              "pen مفرد و قابل‌شمارش است، پس one."),
            q("The coffee here is better than the ___ at the other shop.",
              ["coffee", "one", "ones"], "coffee",
              "Coffee is noncount and cannot be replaced by one.",
              "coffee غیرقابل‌شمارش است و با one جانشین نمی‌شود."),
        ],
    },
    {
        "section": "8-7",
        "title": "There and it as empty subjects",
        "title_fa": "there و it به‌عنوان فاعل صوری",
        "use_en": "There introduces that something exists: there is a problem, there are two chairs. It talks about time, weather, distance and a whole situation: it is late, it is raining, it is ten kilometers from here. Neither word means anything by itself, and neither can be left out: English needs a subject.",
        "use_fa": "there وجود چیزی را معرفی می‌کند: there is a problem، there are two chairs. it دربارهٔ زمان، هوا، مسافت و یک وضعیت کلی می‌گوید: it is late، it is raining، it is ten kilometers from here. هیچ‌کدام به‌تنهایی معنا ندارند و هیچ‌کدام را نمی‌توان حذف کرد: انگلیسی به فاعل نیاز دارد.",
        "form_en": "There is / There are + noun  ·  It is + time / weather / distance",
        "examples": [
            {"en": "There is a bank on the corner.",
             "fa": "سر خیابان یک بانک هست."},
            {"en": "It is raining, so take an umbrella.",
             "fa": "باران می‌بارد، پس چتر بردار."},
            {"en": "It is five kilometers to the station.",
             "fa": "تا ایستگاه پنج کیلومتر است."},
        ],
        "exercises": [
            ex("___ is a pharmacy near my house.", "There",
               "Existence is introduced with there.",
               "وجود با there معرفی می‌شود."),
            ex("___ is very cold today.", "It",
               "Weather takes the empty subject it.",
               "هوا فاعل صوری it می‌گیرد."),
            ex("___ are three books on the shelf.", "There",
               "The plural noun after the verb needs there are.",
               "اسم جمع پس از فعل با there are می‌آید."),
        ],
        "exam": [
            q("___ is a good movie at the cinema this week.",
              ["There", "It", "This"], "There",
              "Existence is introduced by there is.",
              "وجود با there is معرفی می‌شود."),
            q("___ is two o'clock already.",
              ["It", "There", "That"], "It",
              "The time is expressed with it is.",
              "زمان با it is بیان می‌شود."),
            q("___ are many reasons to learn English.",
              ["There", "It", "They"], "There",
              "A plural noun follows there are.",
              "اسم جمع پس از there are می‌آید."),
        ],
    },
    {
        "section": "8-8",
        "title": "Question pronouns: who, whom, whose, which and what",
        "title_fa": "ضمیرهای پرسشی: who، whom، whose، which و what",
        "use_en": "Who asks about a person as the subject, whom about a person as the object (formal; who is common in speech), and whose about possession: whose bag is this? Which chooses from a known set, and what asks from an open one. Whose is never written who's, which means who is.",
        "use_fa": "who دربارهٔ شخص به‌عنوان فاعل می‌پرسد، whom دربارهٔ شخص به‌عنوان مفعول (رسمی؛ در گفتار who رایج است) و whose دربارهٔ مالکیت: whose bag is this? which از میان مجموعه‌ای شناخته‌شده انتخاب می‌کند و what از میان مجموعه‌ای باز. whose هرگز who's نوشته نمی‌شود که یعنی who is.",
        "form_en": "who (subject) / whom (object) / whose (possessive)  ·  which (from a set) / what (open)",
        "examples": [
            {"en": "Who called you last night?",
             "fa": "دیشب چه کسی به تو زنگ زد؟"},
            {"en": "Whose coat is this?",
             "fa": "این کت چه کسی است؟"},
            {"en": "Which of these two shirts do you like?",
             "fa": "کدام یک از این دو پیراهن را دوست داری؟"},
        ],
        "exercises": [
            ex("___ did you invite to the party?", "Who",
               "Who is the object here in everyday English.",
               "who در انگلیسی روزمره مفعول است."),
            ex("With ___ did you travel?", "whom",
               "After a preposition the formal object form whom is used.",
               "پس از حرف اضافه شکل مفعولی رسمی whom می‌آید."),
            ex("___ car is parked outside?", "Whose",
               "Possession is asked with whose.",
               "مالکیت با whose پرسیده می‌شود."),
        ],
        "exam": [
            q("___ is knocking at the door?",
              ["Who", "Whom", "Whose"], "Who",
              "The person is the subject, so who.",
              "شخص فاعل است، پس who."),
            q("___ of the three colors do you prefer?",
              ["Which", "What", "Who"], "Which",
              "A choice inside a known set takes which.",
              "انتخاب از مجموعه‌ای شناخته‌شده which می‌گیرد."),
            q("___ bag is on my chair?",
              ["Whose", "Who's", "Whom"], "Whose",
              "Whose is possessive; who's means who is.",
              "whose ملکی است؛ who's یعنی who is."),
        ],
    },
    {
        "section": "8-9",
        "title": "Common pronoun mistakes: between you and me, its and it's",
        "title_fa": "خطاهای رایج ضمیر: between you and me، its و it's",
        "use_en": "After a preposition, use the object pronoun: between you and me, not between you and I; with him and her, not with he and she. Its is possessive and it's means it is. Theirs, ours and yours never take an apostrophe. And a reflexive cannot replace a subject: my friend and I went, not my friend and myself.",
        "use_fa": "پس از حرف اضافه ضمیر مفعولی می‌آید: between you and me، نه between you and I؛ with him and her، نه with he and she. its ملکی است و it's یعنی it is. theirs، ours و yours هرگز آپاستروف نمی‌گیرند. ضمیر انعکاسی جای فاعل نمی‌نشیند: my friend and I went، نه my friend and myself.",
        "form_en": "preposition + object pronoun  ·  its (possessive) / it's (it is)  ·  subject: my friend and I",
        "examples": [
            {"en": "This is between you and me.",
             "fa": "این بین من و تو می‌ماند."},
            {"en": "The team changed its schedule.",
             "fa": "تیم برنامهٔ خود را تغییر داد."},
            {"en": "My friend and I went to the museum.",
             "fa": "من و دوستم به موزه رفتیم."},
        ],
        "exercises": [
            ex("Keep this secret between you and ___ .", "me",
               "A preposition takes the object pronoun me, not I.",
               "پس از حرف اضافه ضمیر مفعولی me می‌آید، نه I."),
            ex("The city has changed ___ transport system.", "its",
               "Its is the possessive form, with no apostrophe.",
               "its شکل ملکی است و آپاستروف ندارد."),
            ex("___ is going to rain soon.", "It's",
               "It's is the contraction of it is.",
               "it's کوتاه‌شدهٔ it is است."),
        ],
        "exam": [
            q("She sat between Sara and ___ .",
              ["me", "I", "myself"], "me",
              "After between the object pronoun is used.",
              "پس از between ضمیر مفعولی می‌آید."),
            q("The dog wagged ___ tail.",
              ["its", "it's", "it"], "its",
              "Possession takes its without an apostrophe.",
              "مالکیت با its و بدون آپاستروف بیان می‌شود."),
            q("My brother and ___ painted the room.",
              ["I", "me", "myself"], "I",
              "The pronoun is part of the subject, so I.",
              "ضمیر بخشی از فاعل است، پس I."),
        ],
    },
]

ABOUT_EN = ("The grammar of the whole course, chapter by chapter and chart by chart: "
            "eighty-two structures from the book's twenty chapters, each with the "
            "rule, a pattern, examples of it, exercises and a short exam. Chapters one "
            "to eight are complete, chart 1-1 to 8-9. The explanations and sentences "
            "are written for this app; the book is the reference text.")
ABOUT_FA = ("دستور زبان تمام دوره، فصل به فصل و نمودار به نمودار: هشتاد‌و‌دو ساختار از "
            "بیست فصل کتاب، هر یک با قاعده، الگو، مثال، تمرین و یک آزمون کوتاه. "
            "فصل‌های یک تا هشت کامل‌اند، از نمودار ۱-۱ تا ۸-۹. توضیح‌ها و جمله‌ها برای "
            "همین برنامه نوشته شده‌اند و کتاب متن مرجع است.")


def main() -> int:
    data = json.loads(BOOKS.read_text(encoding="utf-8"))
    book = next(b for b in data["books"] if b.get("kind") == "grammar")

    old = [l for l in book["lessons"] if l.get("chapter") == "Chapter 8"]
    assert old, "chapter eight is not in the book"
    first = book["lessons"].index(old[0])
    rest = [l for l in book["lessons"] if l.get("chapter") != "Chapter 8"]

    chapter8 = []
    for lesson in LESSONS:
        chapter8.append({
            "n": 0, "title": lesson["title"], "title_fa": lesson["title_fa"],
            "chapter": "Chapter 8", "section": lesson["section"],
            "use_en": lesson["use_en"], "use_fa": lesson["use_fa"],
            "form_en": lesson["form_en"], "examples": lesson["examples"],
            "exercises": lesson["exercises"], "exam": lesson["exam"],
        })

    lessons = rest[:first] + chapter8 + rest[first:]
    for i, lesson in enumerate(lessons, 1):
        lesson["n"] = i
    book["lessons"] = lessons
    book["about_en"] = ABOUT_EN
    book["about_fa"] = ABOUT_FA

    BOOKS.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")
    print(f"chapter eight: {len(chapter8)} charts, {len(lessons)} structures in the book")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
