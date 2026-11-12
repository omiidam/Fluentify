#!/usr/bin/env python3
"""Write chapter seven of the grammar book into books.json.

    python3 tools/chapter7.py

Chapter seven of *Understanding and Using English Grammar* is Articles. The
book shipped with one section for it (7-1 across the three articles); this
replaces it with the chapter's nine charts, written out like chapters one to
six: the rule, the form, examples in both languages, three guided exercises
and a three-question check for each.

It is idempotent: chapter seven is always rebuilt from this script.
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
        "section": "7-1",
        "title": "The three choices: a, an, the or nothing",
        "title_fa": "سه گزینه: a، an، the یا هیچ",
        "use_en": "Before a noun English chooses one of four things: a or an for one thing not yet known, the for something both people can identify, or no article at all. The choice depends on the listener: a book is new information, the book is information we share. Get the listener's knowledge right and the article follows.",
        "use_fa": "پیش از اسم، انگلیسی یکی از چهار گزینه را برمی‌گزیند: a یا an برای چیزی که هنوز شناخته نیست، the برای چیزی که هر دو طرف می‌توانند مشخص کنند، یا هیچ حرف تعریفی. انتخاب به شنونده بستگی دارد: a book اطلاعات تازه است و the book اطلاعات مشترک. اگر بدانی شنونده چه می‌داند، حرف تعریف خودش می‌آید.",
        "form_en": "a / an + singular count noun (new)  ·  the + known noun  ·  no article + plural or noncount",
        "examples": [
            {"en": "I bought a book yesterday. The book is about birds.",
             "fa": "دیروز کتابی خریدم. آن کتاب دربارهٔ پرنده‌هاست."},
            {"en": "Please close the door.",
             "fa": "لطفاً در را ببند."},
            {"en": "Books are expensive in this city.",
             "fa": "کتاب‌ها در این شهر گران‌اند."},
        ],
        "exercises": [
            ex("She has ___ cat and two birds.", "a",
               "One cat, not yet known, begins with a consonant sound.",
               "یک گربه که هنوز شناخته نیست و با صدای بی‌صدا آغاز می‌شود."),
            ex("___ sun rises in the east.", "The",
               "There is only one sun, so both people can identify it.",
               "تنها یک خورشید وجود دارد، پس هر دو طرف آن را می‌شناسند."),
            ex("I like ___ music.", "no article",
               "Music is noncount and used in a general sense, so no article.",
               "music غیرقابل‌شمارش و در معنای کلی است، پس حرف تعریف ندارد."),
        ],
        "exam": [
            q("She is reading ___ newspaper.",
              ["a", "an", "the"], "a",
              "One newspaper, not yet known, and newspaper begins with a consonant.",
              "یک روزنامهٔ ناشناخته و newspaper با حرف بی‌صدا آغاز می‌شود."),
            q("___ moon is bright tonight.",
              ["The", "A", "An"], "The",
              "There is only one moon.",
              "تنها یک ماه وجود دارد."),
            q("We need ___ water.",
              ["some", "a", "an"], "some",
              "Water is noncount, so it takes some rather than an article.",
              "water غیرقابل‌شمارش است، پس some می‌گیرد نه حرف تعریف."),
        ],
    },
    {
        "section": "7-2",
        "title": "A and an: one of many, not known yet",
        "title_fa": "a و an: یکی از بسیاری، هنوز ناشناخته",
        "use_en": "A and an mean one, and they are used only with a singular count noun that the listener cannot yet identify. Choose a before a consonant sound and an before a vowel sound, which is about the sound and not the letter: a university, an hour, a European country.",
        "use_fa": "a و an یعنی «یک» و تنها با اسم قابل‌شمارش مفردی می‌آیند که شنونده هنوز نمی‌تواند مشخص کند. پیش از صدای بی‌صدا a و پیش از صدای صدادار an می‌آید؛ ملاک صدا است نه حرف: a university، an hour، a European country.",
        "form_en": "a + consonant sound  ·  an + vowel sound  ·  singular count nouns only",
        "examples": [
            {"en": "She works in a hospital.",
             "fa": "او در یک بیمارستان کار می‌کند."},
            {"en": "He waited for an hour.",
             "fa": "یک ساعت منتظر ماند."},
            {"en": "My brother studies at a university in Tehran.",
             "fa": "برادرم در دانشگاهی در تهران درس می‌خواند."},
        ],
        "exercises": [
            ex("I need ___ umbrella; it is raining.", "an",
               "Umbrella begins with a vowel sound, so an.",
               "umbrella با صدای صدادار آغاز می‌شود، پس an."),
            ex("She is ___ engineer.", "an",
               "Engineer begins with a vowel sound.",
               "engineer با صدای صدادار آغاز می‌شود."),
            ex("He is ___ university student.", "a",
               "University begins with the consonant sound /j/, so a.",
               "university با صدای بی‌صدای /j/ آغاز می‌شود، پس a."),
        ],
        "exam": [
            q("We need ___ table for four people.",
              ["a", "an", "the"], "a",
              "One table, not yet identified, begins with a consonant sound.",
              "یک میز ناشناخته که با صدای بی‌صدا آغاز می‌شود."),
            q("It took ___ hour to finish.",
              ["an", "a", "the"], "an",
              "Hour begins with a vowel sound, so an.",
              "hour با صدای صدادار آغاز می‌شود، پس an."),
            q("She bought ___ apple.",
              ["an", "a", "some"], "an",
              "One apple, not yet known, begins with a vowel sound.",
              "یک سیب ناشناخته که با صدای صدادار آغاز می‌شود."),
        ],
    },
    {
        "section": "7-3",
        "title": "The: known to both people",
        "title_fa": "the: شناخته‌شده برای هر دو طرف",
        "use_en": "The is used when the listener can identify which one you mean: because it was mentioned before, because there is only one in the situation, or because the rest of the sentence makes it clear. In a room with one window, the window needs no explanation.",
        "use_fa": "the وقتی به کار می‌رود که شنونده بتواند مشخص کند کدام را می‌گویی: چون پیش‌تر گفته شده، چون در آن موقعیت تنها یکی وجود دارد، یا چون ادامهٔ جمله آن را روشن می‌کند. در اتاقی با یک پنجره، the window نیازی به توضیح ندارد.",
        "form_en": "the + noun the listener can identify (shared situation, earlier mention, or a phrase after it)",
        "examples": [
            {"en": "The window is open; could you close it?",
             "fa": "پنجره باز است؛ می‌بندی‌اش؟"},
            {"en": "I saw a dog. The dog was very friendly.",
             "fa": "سگی دیدم. آن سگ خیلی مهربان بود."},
            {"en": "The man in the blue shirt is my teacher.",
             "fa": "مردی که پیراهن آبی دارد معلم من است."},
        ],
        "exercises": [
            ex("There is a cat in the garden. ___ cat is black.", "The",
               "The cat was mentioned in the first sentence, so it is now known.",
               "گربه در جملهٔ اول گفته شد، پس اکنون شناخته است."),
            ex("Please pass me ___ salt.", "the",
               "The salt on the table is identifiable in the situation.",
               "نمک روی میز در آن موقعیت مشخص است."),
            ex("___ woman standing at the door is my aunt.", "The",
               "The phrase after the noun identifies which woman.",
               "عبارت پس از اسم مشخص می‌کند کدام زن."),
        ],
        "exam": [
            q("I bought a pen. ___ pen writes well.",
              ["The", "A", "An"], "The",
              "The second mention is now known, so the.",
              "اشارهٔ دوم شناخته است، پس the."),
            q("Could you turn off ___ light, please?",
              ["the", "a", "an"], "the",
              "The light in this room is identifiable.",
              "چراغ این اتاق مشخص است."),
            q("___ boy who won the race is my cousin.",
              ["The", "A", "An"], "The",
              "The clause after the noun identifies the boy.",
              "جملهٔ پس از اسم پسر را مشخص می‌کند."),
        ],
    },
    {
        "section": "7-4",
        "title": "The: unique things, and the second mention",
        "title_fa": "the: چیزهای یگانه و اشارهٔ دوم",
        "use_en": "The goes with things that are unique in the world or in the context: the sun, the moon, the sky, the internet, the government, the police. It also marks the second mention of something: a story, then the story. The same noun takes a first time and the every time after.",
        "use_fa": "the با چیزهایی می‌آید که در جهان یا در بافت یگانه‌اند: the sun، the moon، the sky، the internet، the government، the police. همچنین اشارهٔ دوم به چیزی را نشان می‌دهد: a story و سپس the story. همان اسم بار اول a و از آن پس the می‌گیرد.",
        "form_en": "the + unique noun  ·  first mention: a / an  ·  later mention: the",
        "examples": [
            {"en": "The sky is clear tonight.",
             "fa": "آسمان امشب صاف است."},
            {"en": "She told me a story. The story was about a fox.",
             "fa": "او برایم داستانی گفت. داستان دربارهٔ یک روباه بود."},
            {"en": "The police are investigating the case.",
             "fa": "پلیس در حال بررسی پرونده است."},
        ],
        "exercises": [
            ex("___ moon looks huge tonight.", "The",
               "There is only one moon in our sky.",
               "در آسمان ما تنها یک ماه هست."),
            ex("He found a key. ___ key opened the old door.", "The",
               "The key is the second mention of the same thing.",
               "کلید همان چیزِ گفته‌شده در جملهٔ پیش است."),
            ex("I read about ___ internet in a magazine.", "the",
               "The internet is unique, so it takes the.",
               "اینترنت یگانه است، پس the می‌گیرد."),
        ],
        "exam": [
            q("___ sun is a star.",
              ["The", "A", "An"], "The",
              "The sun is unique.",
              "خورشید یگانه است."),
            q("They adopted a dog. ___ dog is very small.",
              ["The", "A", "An"], "The",
              "The second mention takes the.",
              "اشارهٔ دوم the می‌گیرد."),
            q("___ government announced a new plan.",
              ["The", "A", "An"], "The",
              "The government of the country is identifiable.",
              "دولت آن کشور مشخص است."),
        ],
    },
    {
        "section": "7-5",
        "title": "No article: plural and noncount general statements",
        "title_fa": "بدون حرف تعریف: جمله‌های کلی با جمع و غیرقابل‌شمارش",
        "use_en": "When a plural count noun or a noncount noun is used in a general sense, English uses no article: books are useful, water is important, life is short. Adding the makes it specific: the books on my desk, the water in this glass. This is the article mistake Persian speakers make most often, because Persian uses a general noun without any marker.",
        "use_fa": "وقتی اسم قابل‌شمارش جمع یا اسم غیرقابل‌شمارش در معنای کلی به کار می‌رود، انگلیسی حرف تعریف نمی‌آورد: books are useful، water is important، life is short. افزودن the آن را مشخص می‌کند: the books on my desk، the water in this glass. این رایج‌ترین خطای حرف تعریف فارسی‌زبانان است، چون فارسی اسم کلی را بدون نشانه می‌آورد.",
        "form_en": "general plural / noncount: no article  ·  specific: the + noun",
        "examples": [
            {"en": "Books are expensive in this city.",
             "fa": "کتاب‌ها در این شهر گران‌اند."},
            {"en": "Water is necessary for life.",
             "fa": "آب برای زندگی ضروری است."},
            {"en": "The books on my desk are new.",
             "fa": "کتاب‌های روی میز من نو هستند."},
        ],
        "exercises": [
            ex("___ life is full of surprises.", "no article",
               "Life is noncount and used generally.",
               "life غیرقابل‌شمارش و در معنای کلی است."),
            ex("___ people in this town are friendly.", "no article",
               "People is plural and general here, so no article.",
               "people جمع و کلی است، پس بدون حرف تعریف."),
            ex("___ water in this bottle is cold.", "The",
               "The phrase after the noun makes the water specific.",
               "عبارت پس از اسم آب را مشخص می‌کند."),
        ],
        "exam": [
            q("___ children need sleep.",
              ["no article", "The", "A"], "no article",
              "A general plural takes no article.",
              "جمع کلی حرف تعریف نمی‌گیرد."),
            q("___ money cannot buy happiness.",
              ["no article", "The", "A"], "no article",
              "Money is noncount and general.",
              "money غیرقابل‌شمارش و کلی است."),
            q("___ fruit in that shop is fresh.",
              ["The", "A", "no article"], "The",
              "The phrase after the noun makes the fruit specific.",
              "عبارت پس از اسم میوه را مشخص می‌کند."),
        ],
    },
    {
        "section": "7-6",
        "title": "A and an with jobs, amounts and rates",
        "title_fa": "a و an با شغل‌ها، مقدارها و نرخ‌ها",
        "use_en": "A or an is required when you say what someone's job is: she is a doctor, he is an engineer. It also appears in expressions of amount and rate: a hundred people, a lot of, twice a week, five dollars a kilo, an hour and a half. These are fixed patterns, not general rules about articles.",
        "use_fa": "هنگام گفتن شغل کسی، a یا an لازم است: she is a doctor، he is an engineer. در عبارت‌های مقدار و نرخ هم می‌آید: a hundred people، a lot of، twice a week، five dollars a kilo، an hour and a half. این‌ها الگوهای ثابت‌اند، نه قاعدهٔ کلی دربارهٔ حرف تعریف.",
        "form_en": "be + a / an + job  ·  a hundred / a lot / twice a week / an hour and a half",
        "examples": [
            {"en": "My mother is a nurse.",
             "fa": "مادرم پرستار است."},
            {"en": "He is an engineer at a car factory.",
             "fa": "او مهندس یک کارخانهٔ خودروسازی است."},
            {"en": "The tomatoes cost two dollars a kilo.",
             "fa": "گوجه‌ها کیلویی دو دلار است."},
        ],
        "exercises": [
            ex("She is ___ doctor in a small clinic.", "a",
               "A job takes a or an, and doctor begins with a consonant sound.",
               "شغل a یا an می‌گیرد و doctor با صدای بی‌صدا آغاز می‌شود."),
            ex("There are ___ hundred students in this school.", "a",
               "A hundred is a fixed amount expression.",
               "a hundred عبارت مقداری ثابت است."),
            ex("We meet twice ___ week.", "a",
               "Twice a week is a rate, and the rate takes a.",
               "twice a week نرخ است و نرخ a می‌گیرد."),
        ],
        "exam": [
            q("He wants to be ___ architect.",
              ["an", "a", "the"], "an",
              "A job takes an before a vowel sound.",
              "شغل پیش از صدای صدادار an می‌گیرد."),
            q("The bus leaves every half ___ hour.",
              ["an", "a", "the"], "an",
              "Half an hour is the fixed expression.",
              "half an hour عبارت ثابت است."),
            q("She earns twenty dollars ___ hour.",
              ["an", "a", "the"], "an",
              "A rate is expressed with a or an, and hour begins with a vowel sound.",
              "نرخ با a یا an بیان می‌شود و hour با صدای صدادار آغاز می‌شود."),
        ],
    },
    {
        "section": "7-7",
        "title": "No article with names, languages, meals and most places",
        "title_fa": "بدون حرف تعریف با نام‌ها، زبان‌ها، وعده‌های غذا و بیشتر مکان‌ها",
        "use_en": "Names of people, languages, school subjects, meals, games, days and months take no article: Ali, Persian, math, breakfast, tennis, Monday. Most countries, cities and streets take none either: Iran, Tehran, Valiasr Street. A few names do take the, and they have to be learned as names: the United States, the Netherlands.",
        "use_fa": "نام افراد، زبان‌ها، درس‌ها، وعده‌های غذا، بازی‌ها، روزها و ماه‌ها حرف تعریف نمی‌گیرند: Ali، Persian، math، breakfast، tennis، Monday. بیشتر کشورها، شهرها و خیابان‌ها هم نمی‌گیرند: Iran، Tehran، Valiasr Street. چند نام the می‌گیرند و باید به‌صورت نام حفظ شوند: the United States، the Netherlands.",
        "form_en": "no article: names, languages, subjects, meals, games, days, most places",
        "examples": [
            {"en": "I study English and math at school.",
             "fa": "در مدرسه انگلیسی و ریاضی می‌خوانم."},
            {"en": "We have breakfast at seven.",
             "fa": "ساعت هفت صبحانه می‌خوریم."},
            {"en": "They live in the United States now.",
             "fa": "آن‌ها اکنون در آمریکا زندگی می‌کنند."},
        ],
        "exercises": [
            ex("She speaks ___ German very well.", "no article",
               "A language takes no article.",
               "نام زبان حرف تعریف نمی‌گیرد."),
            ex("I have ___ lunch at noon.", "no article",
               "A meal takes no article.",
               "وعدهٔ غذا حرف تعریف نمی‌گیرد."),
            ex("___ United States is a large country.", "The",
               "The United States is one of the names that take the.",
               "the United States از نام‌هایی است که the می‌گیرند."),
        ],
        "exam": [
            q("We play ___ football on Fridays.",
              ["no article", "the", "a"], "no article",
              "A game takes no article.",
              "نام بازی حرف تعریف نمی‌گیرد."),
            q("My brother studies ___ history.",
              ["no article", "the", "a"], "no article",
              "A school subject takes no article.",
              "نام درس حرف تعریف نمی‌گیرد."),
            q("She is from ___ Netherlands.",
              ["the", "a", "no article"], "the",
              "The Netherlands is a fixed name with the.",
              "the Netherlands نام ثابتی با the است."),
        ],
    },
    {
        "section": "7-8",
        "title": "The with geography, superlatives and ordinals",
        "title_fa": "the با جغرافیا، صفت‌های عالی و اعداد ترتیبی",
        "use_en": "The is used with rivers, seas, oceans, mountain ranges, groups of islands and deserts: the Karun, the Caspian Sea, the Alborz, the Persian Gulf. It is also used with superlatives and ordinals: the best, the first. A single mountain, a single lake and a single city take no article.",
        "use_fa": "the با رودها، دریاها، اقیانوس‌ها، رشته‌کوه‌ها، گروه جزیره‌ها و بیابان‌ها می‌آید: the Karun، the Caspian Sea، the Alborz، the Persian Gulf. با صفت‌های عالی و اعداد ترتیبی هم می‌آید: the best، the first. یک کوه تنها، یک دریاچهٔ تنها و یک شهر تنها حرف تعریف نمی‌گیرند.",
        "form_en": "the + river / sea / ocean / mountain range / group of islands / desert  ·  the + superlative / ordinal",
        "examples": [
            {"en": "The Karun is the longest river in Iran.",
             "fa": "کارون بلندترین رود ایران است."},
            {"en": "We climbed to the top of the Alborz.",
             "fa": "به قلهٔ البرز صعود کردیم."},
            {"en": "This is the best book I have read.",
             "fa": "این بهترین کتابی است که خوانده‌ام."},
        ],
        "exercises": [
            ex("___ Caspian Sea is the largest lake in the world.", "The",
               "A named sea takes the.",
               "دریای نام‌دار the می‌گیرد."),
            ex("She was ___ first student to finish.", "the",
               "An ordinal takes the.",
               "عدد ترتیبی the می‌گیرد."),
            ex("___ Damavand is a famous mountain.", "no article",
               "A single mountain takes no article.",
               "یک کوه تنها حرف تعریف نمی‌گیرد."),
        ],
        "exam": [
            q("___ Nile is the longest river in Africa.",
              ["The", "A", "no article"], "The",
              "A named river takes the.",
              "رود نام‌دار the می‌گیرد."),
            q("He was ___ third person in line.",
              ["the", "a", "no article"], "the",
              "An ordinal takes the.",
              "عدد ترتیبی the می‌گیرد."),
            q("___ Lake Urmia is in the northwest.",
              ["no article", "The", "A"], "no article",
              "A single lake takes no article.",
              "یک دریاچهٔ تنها حرف تعریف نمی‌گیرد."),
        ],
    },
    {
        "section": "7-9",
        "title": "Common article mistakes: a decision procedure",
        "title_fa": "خطاهای رایج حرف تعریف: یک روش تصمیم‌گیری",
        "use_en": "Ask three questions in order. Is the noun plural or noncount, and general? Then no article. Can the listener identify which one? Then the. Is it one of many, singular and count? Then a or an. Most mistakes come from the first question, and from putting the before a general plural. A few phrases are fixed and are learned whole: go to school, go to bed, at home, in the morning.",
        "use_fa": "به ترتیب سه پرسش بپرس. آیا اسم جمع یا غیرقابل‌شمارش و کلی است؟ پس بدون حرف تعریف. آیا شنونده می‌تواند مشخص کند کدام؟ پس the. آیا یکی از بسیاری، مفرد و قابل‌شمارش است؟ پس a یا an. بیشتر خطاها از پرسش اول می‌آید و از آوردن the پیش از جمع کلی. چند عبارت ثابت‌اند و کامل حفظ می‌شوند: go to school، go to bed، at home، in the morning.",
        "form_en": "general plural or noncount → no article  ·  identifiable → the  ·  one of many, singular count → a / an",
        "examples": [
            {"en": "Cats are independent animals. The cat next door is friendly.",
             "fa": "گربه‌ها جانورانی مستقل‌اند. گربهٔ همسایه مهربان است."},
            {"en": "She goes to school by bus.",
             "fa": "او با اتوبوس به مدرسه می‌رود."},
            {"en": "I read a book about the sea.",
             "fa": "کتابی دربارهٔ دریا خواندم."},
        ],
        "exercises": [
            ex("___ birds can fly, but penguins cannot.", "no article",
               "A general plural takes no article.",
               "جمع کلی حرف تعریف نمی‌گیرد."),
            ex("I left ___ key on the table.", "the",
               "The key is identifiable in the situation.",
               "کلید در آن موقعیت مشخص است."),
            ex("She wants to be ___ artist.", "an",
               "One of many, singular, and artist begins with a vowel sound.",
               "یکی از بسیاری، مفرد، و artist با صدای صدادار آغاز می‌شود."),
        ],
        "exam": [
            q("___ information you gave me was useful.",
              ["The", "A", "no article"], "The",
              "The phrase after the noun makes it specific.",
              "عبارت پس از اسم آن را مشخص می‌کند."),
            q("He goes to ___ bed at ten.",
              ["no article", "the", "a"], "no article",
              "Go to bed is a fixed phrase with no article.",
              "go to bed عبارت ثابتی بدون حرف تعریف است."),
            q("She bought ___ oranges and ___ milk.",
              ["some / some", "the / a", "an / a"], "some / some",
              "An unspecified plural and a noncount noun take some.",
              "جمع نامشخص و اسم غیرقابل‌شمارش some می‌گیرند."),
        ],
    },
]



def main() -> int:
    data = json.loads(BOOKS.read_text(encoding="utf-8"))
    book = next(b for b in data["books"] if b.get("kind") == "grammar")

    old = [l for l in book["lessons"] if l.get("chapter") == "Chapter 7"]
    assert old, "chapter seven is not in the book"
    first = book["lessons"].index(old[0])
    rest = [l for l in book["lessons"] if l.get("chapter") != "Chapter 7"]

    chapter7 = []
    for lesson in LESSONS:
        chapter7.append({
            "n": 0, "title": lesson["title"], "title_fa": lesson["title_fa"],
            "chapter": "Chapter 7", "section": lesson["section"],
            "use_en": lesson["use_en"], "use_fa": lesson["use_fa"],
            "form_en": lesson["form_en"], "examples": lesson["examples"],
            "exercises": lesson["exercises"], "exam": lesson["exam"],
        })

    lessons = rest[:first] + chapter7 + rest[first:]
    for i, lesson in enumerate(lessons, 1):
        lesson["n"] = i
    book["lessons"] = lessons

    BOOKS.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")
    print(f"chapter seven: {len(chapter7)} charts, {len(lessons)} structures in the book")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
