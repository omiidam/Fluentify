#!/usr/bin/env python3
"""Write chapter thirteen of the grammar book into books.json.

    python3 tools/chapter13.py

Chapter thirteen of *Understanding and Using English Grammar* is Adjective
Clauses. The book shipped with two placeholder sections for it; this replaces
them with the chapter's eleven charts, written out like chapters three to twelve:
the rule, the form, examples in both languages, three guided exercises and a
three-question check for each.

The sentences and explanations are written for this app. The book is the
reference text, and nothing in this file is transcribed from it.

It is idempotent: chapter thirteen is always rebuilt from this script.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "books.json"

CHAPTER = "Chapter 13"


def ex(prompt, answer, why_en, why_fa):
    return {"prompt": prompt, "answer": answer, "why_en": why_en, "why_fa": why_fa}


def q(text, options, answer, why_en, why_fa):
    assert answer in options and len(options) == 3, text
    return {"q": text, "options": options, "answer": answer,
            "why_en": why_en, "why_fa": why_fa}


LESSONS = [
    {
        "section": "13-1",
        "title": "Adjective clause pronouns as the subject: who and which",
        "title_fa": "ضمیرهای جملهٔ وصفی در جایگاه فاعل: who و which",
        "use_en": "An adjective clause describes the noun in front of it, and its pronoun replaces that noun inside the clause. When the noun is a person the pronoun is who; when it is a thing the pronoun is which; that works for both. If the pronoun is the subject of the clause, it cannot be left out: the man who lives next door, the book which is on the table.",
        "use_fa": "جملهٔ وصفی اسم پیش از خود را توصیف می‌کند و ضمیر آن اسم را درون جمله جای می‌گیرد. اگر اسم شخص باشد ضمیر who است، اگر چیز باشد which، و that برای هر دو کار می‌کند. اگر ضمیر فاعل جمله باشد حذف‌شدنی نیست: the man who lives next door، the book which is on the table.",
        "form_en": "noun (person) + who + verb  ·  noun (thing) + which + verb  ·  that for both",
        "examples": [
            {"en": "The man who lives next door is a doctor.",
             "fa": "مردی که همسایهٔ ماست پزشک است."},
            {"en": "The book which is on the table is mine.",
             "fa": "کتابی که روی میز است مال من است."},
            {"en": "I know a shop that sells old maps.",
             "fa": "مغازه‌ای می‌شناسم که نقشه‌های قدیمی می‌فروشد."},
        ],
        "exercises": [
            ex("The woman ___ teaches us French is from Lyon.", "who",
               "A person as the subject of the clause takes who.",
               "شخص در جایگاه فاعل جمله who می‌گیرد."),
            ex("The train ___ goes to Isfahan leaves at six.", "which",
               "A thing as the subject of the clause takes which.",
               "چیز در جایگاه فاعل جمله which می‌گیرد."),
            ex("People ___ work here start early.", "who",
               "A plural person subject still takes who.",
               "شخص جمع در جایگاه فاعل هم who می‌گیرد."),
        ],
        "exam": [
            q("The film ___ won the prize is in Persian.",
              ["which", "who", "whose"], "which",
              "The film is a thing and the subject of the clause.",
              "فیلم چیز است و فاعل جملهٔ وصفی."),
            q("The students ___ passed were happy.",
              ["who", "which", "whom"], "who",
              "The students are the subject of passed, so who.",
              "دانش‌آموزان فاعل passed هستند، پس who."),
            q("Which pronoun can never be left out here? — The car ___ is parked outside is new.",
              ["which", "that", "either one"], "which",
              "A subject pronoun must be present, so which or that is required.",
              "ضمیر فاعل باید باشد، پس which یا that لازم است."),
        ],
    },
    {
        "section": "13-2",
        "title": "Adjective clause pronouns as the object of a verb",
        "title_fa": "ضمیرهای جملهٔ وصفی در جایگاه مفعول فعل",
        "use_en": "When the pronoun is the object of the clause's verb, it can be whom, who, that or nothing at all: the film that we watched, the film we watched. Leaving it out is the usual choice in speech and is perfectly correct. Whom belongs to formal writing and to use after a preposition. The clause still keeps its own subject and verb, so the order inside it never changes.",
        "use_fa": "وقتی ضمیر مفعول فعلِ جمله باشد می‌تواند whom، who، that یا هیچ باشد: the film that we watched، the film we watched. حذف کردن آن در گفتار رایج و کاملاً درست است. whom به نوشتار رسمی و به کاربرد پس از حرف اضافه تعلق دارد. جمله هنوز فاعل و فعل خود را دارد، پس ترتیب درون آن هرگز تغییر نمی‌کند.",
        "form_en": "noun + (whom / who / that) + subject + verb  ·  the pronoun may be omitted",
        "examples": [
            {"en": "The film that we watched was long.",
             "fa": "فیلمی که دیدیم طولانی بود."},
            {"en": "The woman we met at the station was a teacher.",
             "fa": "زنی که در ایستگاه دیدیم معلم بود."},
            {"en": "The report which they sent was incomplete.",
             "fa": "گزارشی که فرستادند ناقص بود."},
        ],
        "exercises": [
            ex("The song ___ we heard last night is on the radio. (formal)", "which",
               "A thing as the object can take which.",
               "چیز در جایگاه مفعول می‌تواند which بگیرد."),
            ex("The man ___ I called was very helpful. (formal, person)", "whom",
               "Whom is the formal object form for a person.",
               "whom شکل مفعولی رسمی برای شخص است."),
            ex("The keys ___ I lost were in my bag all along. (omitted pronoun)", "that",
               "That may stand in for the omitted object pronoun.",
               "that می‌تواند جای ضمیر مفعولی حذف‌شده را بگیرد."),
        ],
        "exam": [
            q("The book ___ I bought yesterday is excellent.",
              ["which", "who", "whose"], "which",
              "A thing as the object of bought takes which or nothing.",
              "چیز در جایگاه مفعول bought می‌تواند which یا هیچ بگیرد."),
            q("The people ___ we invited arrived early.",
              ["whom", "which", "whose"], "whom",
              "People as the object take whom in careful writing.",
              "اشخاص در جایگاه مفعول در نوشتار دقیق whom می‌گیرند."),
            q("Which sentence is correct?",
              ["The car I sold was old.", "The car who I sold was old.",
               "The car I sold it was old."], "The car I sold was old.",
              "The object pronoun can be omitted, and the noun is not repeated.",
              "ضمیر مفعولی حذف می‌شود و اسم تکرار نمی‌شود."),
        ],
    },
    {
        "section": "13-3",
        "title": "Adjective clause pronouns as the object of a preposition",
        "title_fa": "ضمیرهای جملهٔ وصفی در جایگاه مفعول حرف اضافه",
        "use_en": "When the clause needs a preposition, the preposition can stay at the end and the pronoun can be that, which, who or nothing: the city that I grew up in, the city I grew up in. In formal writing the preposition moves to the front with which or whom: the city in which I grew up, the colleague to whom I spoke. The meaning is the same; only the register changes.",
        "use_fa": "وقتی جمله حرف اضافه لازم دارد، حرف اضافه می‌تواند در پایان بماند و ضمیر that، which، who یا هیچ باشد: the city that I grew up in، the city I grew up in. در نوشتار رسمی حرف اضافه با which یا whom به آغاز می‌رود: the city in which I grew up، the colleague to whom I spoke. معنا یکی است و تنها لحن تغییر می‌کند.",
        "form_en": "noun + (that / which / who) + ... + preposition  ·  noun + preposition + which / whom",
        "examples": [
            {"en": "The city that I grew up in has changed.",
             "fa": "شهری که در آن بزرگ شدم تغییر کرده است."},
            {"en": "The colleague to whom I spoke was helpful.",
             "fa": "همکاری که با او صحبت کردم کمک‌کننده بود."},
            {"en": "This is the pen I write with.",
             "fa": "این همان خودکاری است که با آن می‌نویسم."},
        ],
        "exercises": [
            ex("The house ___ we lived in was small. (a thing)", "which",
               "A thing before a preposition takes which.",
               "چیز پیش از حرف اضافه which می‌گیرد."),
            ex("The friend ___ whom I travelled is a nurse. (formal)", "with",
               "The preposition moves to the front with whom.",
               "حرف اضافه با whom به آغاز می‌رود."),
            ex("The topic ___ which they argued was money. (formal)", "about",
               "Formal style puts the preposition before which.",
               "سبک رسمی حرف اضافه را پیش از which می‌آورد."),
        ],
        "exam": [
            q("The chair ___ I sat on was broken.",
              ["that", "who", "whose"], "that",
              "A thing with a stranded preposition takes that or which.",
              "چیز با حرف اضافهٔ پایانی that یا which می‌گیرد."),
            q("The person ___ whom I spoke was the manager.",
              ["to", "with", "for"], "to",
              "Speak to somebody keeps to before whom.",
              "speak to somebody حرف to را پیش از whom نگه می‌دارد."),
            q("Which sentence is the formal version?",
              ["The town in which she lives is quiet.", "The town which she lives in is quiet.",
               "The town she lives is quiet."], "The town in which she lives is quiet.",
              "Formal writing fronts the preposition with which.",
              "نوشتار رسمی حرف اضافه را با which به آغاز می‌آورد."),
        ],
    },
    {
        "section": "13-4",
        "title": "Whose: the possessive in an adjective clause",
        "title_fa": "whose: حالت مالکیت در جملهٔ وصفی",
        "use_en": "Whose replaces a possessive, not a person: the student whose essay won, the house whose roof leaks. It works for people and for things, which is why it saves a clumsy of which. The noun after whose takes no article, and whose can never be left out of the clause.",
        "use_fa": "whose جای حالت مالکیت را می‌گیرد نه جای شخص: the student whose essay won، the house whose roof leaks. برای اشخاص و اشیاء کار می‌کند و همین آن را از of which دست‌وپاگیر نجات می‌دهد. اسم پس از whose حرف تعریف نمی‌گیرد و whose هرگز از جمله حذف نمی‌شود.",
        "form_en": "noun + whose + noun + verb",
        "examples": [
            {"en": "The student whose essay won is in my class.",
             "fa": "دانش‌آموزی که مقاله‌اش برنده شد در کلاس من است."},
            {"en": "I met a writer whose books I admire.",
             "fa": "نویسنده‌ای دیدم که کتاب‌هایش را می‌ستایم."},
            {"en": "The house whose roof leaks is empty.",
             "fa": "خانه‌ای که سقفش چکه می‌کند خالی است."},
        ],
        "exercises": [
            ex("The girl ___ father is a pilot sits next to me.", "whose",
               "Possession in the clause is whose.",
               "مالکیت در جمله با whose بیان می‌شود."),
            ex("I know a man ___ shop sells old clocks. (possessive)", "whose",
               "The shop belongs to the man, so whose.",
               "مغازه مال آن مرد است، پس whose."),
            ex("The company ___ products we use is local. (possessive)", "whose",
               "Whose also works for things.",
               "whose برای اشیاء هم کار می‌کند."),
        ],
        "exam": [
            q("The teacher ___ class I enjoyed has retired.",
              ["whose", "who", "which"], "whose",
              "The class belongs to the teacher, so whose.",
              "کلاس مال معلم است، پس whose."),
            q("This is the dog ___ owner moved away.",
              ["whose", "who", "whom"], "whose",
              "Owner is a possession, so whose.",
              "owner مالکیت است، پس whose."),
            q("Which sentence is correct?",
              ["The man whose car was stolen called the police.",
               "The man whose the car was stolen called the police.",
               "The man who car was stolen called the police."],
              "The man whose car was stolen called the police.",
              "Whose is followed directly by the noun it possesses.",
              "پس از whose بی‌واسطه اسمی می‌آید که مال اوست."),
        ],
    },
    {
        "section": "13-5",
        "title": "Where in adjective clauses",
        "title_fa": "where در جمله‌های وصفی",
        "use_en": "Where replaces a preposition and a place: the house where I was born means the house in which I was born. It follows a place noun, never a time noun, and it cannot be left out. If the clause already has a preposition, where is not used: the office that I work in, not the office where I work in.",
        "use_fa": "where جای حرف اضافه و مکان را می‌گیرد: the house where I was born یعنی the house in which I was born. پس از اسم مکان می‌آید، هرگز پس از اسم زمان، و حذف‌شدنی نیست. اگر جمله از پیش حرف اضافه داشته باشد where نمی‌آید: the office that I work in و نه the office where I work in.",
        "form_en": "place noun + where + subject + verb",
        "examples": [
            {"en": "The house where I was born is still standing.",
             "fa": "خانه‌ای که در آن به دنیا آمدم هنوز پابرجاست."},
            {"en": "This is the café where we first met.",
             "fa": "این همان کافه‌ای است که نخستین بار همدیگر را دیدیم."},
            {"en": "The town where she works is two hours away.",
             "fa": "شهری که در آن کار می‌کند دو ساعت فاصله دارد."},
        ],
        "exercises": [
            ex("The school ___ I studied is now a museum.", "where",
               "A place takes where instead of in which.",
               "مکان به‌جای in which از where استفاده می‌کند."),
            ex("That is the village ___ they live. (place)", "where",
               "Where replaces the preposition of place.",
               "where جای حرف اضافهٔ مکان را می‌گیرد."),
            ex("The shop ___ we bought the shoes has closed.", "where",
               "Where follows a place noun.",
               "where پس از اسم مکان می‌آید."),
        ],
        "exam": [
            q("The city ___ I was born has grown.",
              ["where", "which", "when"], "where",
              "A place with no stated preposition takes where.",
              "مکان بدون حرف اضافهٔ گفته‌شده where می‌گیرد."),
            q("Which sentence is wrong?",
              ["The office where I work in is small.", "The office where I work is small.",
               "The office that I work in is small."],
              "The office where I work in is small.",
              "Where already carries the preposition, so in is extra.",
              "where خودش حرف اضافه دارد، پس in اضافه است."),
            q("The park ___ we play football is near the river.",
              ["where", "which", "who"], "where",
              "A place noun takes where.",
              "اسم مکان where می‌گیرد."),
        ],
    },
    {
        "section": "13-6",
        "title": "When in adjective clauses",
        "title_fa": "when در جمله‌های وصفی",
        "use_en": "When replaces a preposition and a time: the year when we met means the year in which we met. It follows a time noun such as day, year, moment or period, and like where it cannot be left out. English often drops the whole clause and keeps the noun, so the day we met is equally good, and that is the form speech prefers.",
        "use_fa": "when جای حرف اضافه و زمان را می‌گیرد: the year when we met یعنی the year in which we met. پس از اسم زمان مانند day، year، moment یا period می‌آید و مانند where حذف‌شدنی نیست. انگلیسی اغلب کل جمله را حذف می‌کند و اسم را نگه می‌دارد، پس the day we met هم درست است و گفتار آن را ترجیح می‌دهد.",
        "form_en": "time noun + when + subject + verb  ·  or the pronoun is dropped: the day we met",
        "examples": [
            {"en": "I still remember the day when we first met.",
             "fa": "هنوز روزی را که نخستین بار دیدار کردیم به یاد دارم."},
            {"en": "The year when the war ended was 1945.",
             "fa": "سالی که جنگ پایان یافت ۱۹۴۵ بود."},
            {"en": "There are moments when silence is the best answer.",
             "fa": "لحظه‌هایی هست که سکوت بهترین پاسخ است."},
        ],
        "exercises": [
            ex("I remember the morning ___ the phone rang. (time)", "when",
               "A time noun takes when.",
               "اسم زمان when می‌گیرد."),
            ex("The week ___ we moved was very busy. (time)", "when",
               "When replaces in which for a period.",
               "when برای یک دوره جای in which را می‌گیرد."),
            ex("Do you recall the moment ___ he said it? (time)", "when",
               "A moment in time takes when.",
               "لحظه‌ای در زمان when می‌گیرد."),
        ],
        "exam": [
            q("The day ___ we arrived was rainy.",
              ["when", "where", "which"], "when",
              "A day is a time noun, so when.",
              "روز اسم زمان است، پس when."),
            q("Which sentence is natural in speech?",
              ["The day we met was sunny.", "The day when we met it was sunny.",
               "The day which we met was sunny."], "The day we met was sunny.",
              "Speech drops the relative pronoun after a time noun.",
              "گفتار ضمیر موصولی را پس از اسم زمان حذف می‌کند."),
            q("There are times ___ patience is everything.",
              ["when", "which", "where"], "when",
              "Times is a time noun, so when.",
              "times اسم زمان است، پس when."),
        ],
    },
    {
        "section": "13-7",
        "title": "Adjective clauses that modify pronouns",
        "title_fa": "جمله‌های وصفی که ضمیر را توصیف می‌کنند",
        "use_en": "Indefinite pronouns take an adjective clause too, and the pronoun inside it is that rather than who or which: everyone who came, everything that happened, the only one that worked. The exception is a pronoun ending in -body or -one, which takes who because it means a person. These clauses are always essential, so they never take commas.",
        "use_fa": "ضمیرهای نامعین هم جملهٔ وصفی می‌گیرند و ضمیر درون آن that است نه who یا which: everyone who came، everything that happened، the only one that worked. استثنا ضمیری است که به body- یا one- پایان می‌یابد و چون به شخص اشاره دارد who می‌گیرد. این جمله‌ها همیشه لازم‌اند، پس هرگز ویرگول نمی‌گیرند.",
        "form_en": "everyone / someone + who + verb  ·  everything / nothing / all + that + verb",
        "examples": [
            {"en": "Everyone who came received a small gift.",
             "fa": "هر کسی که آمد هدیهٔ کوچکی گرفت."},
            {"en": "Everything that he told us was true.",
             "fa": "هر چه به ما گفت درست بود."},
            {"en": "This is the only one that fits.",
             "fa": "این تنها موردی است که جا می‌شود."},
        ],
        "exercises": [
            ex("Everything ___ he said was recorded.", "that",
               "A thing pronoun takes that, not which.",
               "ضمیر شیء that می‌گیرد نه which."),
            ex("Someone ___ knows the answer should speak. (person)", "who",
               "Someone means a person, so who.",
               "someone به شخص اشاره دارد، پس who."),
            ex("Nothing ___ she tried worked.", "that",
               "Nothing is a thing pronoun and takes that.",
               "nothing ضمیر شیء است و that می‌گیرد."),
        ],
        "exam": [
            q("All ___ we need is time.",
              ["that", "who", "which"], "that",
              "All as a pronoun takes that.",
              "all در جایگاه ضمیر that می‌گیرد."),
            q("Anyone ___ wants to join can sign here.",
              ["who", "which", "that"], "who",
              "Anyone means a person, so who.",
              "anyone به شخص اشاره دارد، پس who."),
            q("Which sentence needs no comma?",
              ["Everything that he said was true.", "My father, who is a doctor, works here.",
               "Paris, which I love, is far."], "Everything that he said was true.",
              "A clause after everything is essential and takes no comma.",
              "جمله پس از everything لازم است و ویرگول نمی‌گیرد."),
        ],
    },
    {
        "section": "13-8",
        "title": "Punctuating adjective clauses: commas that change the meaning",
        "title_fa": "نگارش جمله‌های وصفی: ویرگول‌هایی که معنا را عوض می‌کنند",
        "use_en": "An essential clause tells the reader which one is meant and takes no commas: the students who studied passed. A non-essential clause adds information about something already identified and sits between commas: the students, who had studied, passed. Only a non-essential clause can be removed without breaking the sentence, and in careful writing that clause takes which for a thing, never that.",
        "use_fa": "جملهٔ لازم می‌گوید کدام یک منظور است و ویرگول نمی‌گیرد: the students who studied passed. جملهٔ غیرلازم اطلاعاتی دربارهٔ چیزی که از پیش مشخص است می‌افزاید و میان دو ویرگول می‌نشیند: the students, who had studied, passed. تنها جملهٔ غیرلازم را می‌توان بی‌آنکه جمله بشکند حذف کرد و در نوشتار دقیق آن جمله برای چیز which می‌گیرد، هرگز that.",
        "form_en": "essential: noun + who/that + clause (no commas)  ·  non-essential: noun, which/who + clause,",
        "examples": [
            {"en": "The players who trained hard won the match.",
             "fa": "بازیکنانی که سخت تمرین کردند مسابقه را بردند."},
            {"en": "My brother, who lives in Berlin, is visiting.",
             "fa": "برادرم که در برلین زندگی می‌کند به دیدار ما می‌آید."},
            {"en": "The museum, which opened last year, is free.",
             "fa": "موزه که سال گذشته باز شد رایگان است."},
        ],
        "exercises": [
            ex("My mother, ___ was born in Shiraz, speaks Persian. (non-essential person)",
               "who",
               "A non-essential person clause takes who between commas.",
               "جملهٔ غیرلازم برای شخص میان ویرگول‌ها who می‌گیرد."),
            ex("The letter that arrived today is from Ali. Here that is correct because the clause is ___.",
               "essential",
               "Without the clause the reader cannot tell which letter.",
               "بی این جمله خواننده نمی‌داند کدام نامه است."),
            ex("The car, ___ I bought last year, needs service. (non-essential thing)",
               "which",
               "A non-essential thing clause takes which, not that.",
               "جملهٔ غیرلازم برای چیز which می‌گیرد نه that."),
        ],
        "exam": [
            q("Which sentence says all the students studied?",
              ["The students, who studied, passed.", "The students who studied passed.",
               "The students that studied passed."],
              "The students, who studied, passed.",
              "The commas make the clause true of all of them.",
              "ویرگول‌ها جمله را دربارهٔ همه درست می‌کنند."),
            q("In this essential clause, the book ___ I borrowed from you was excellent.",
              ["that", ", which,", ", that,"], "that",
              "An essential clause takes that without commas.",
              "جملهٔ لازم that می‌گیرد بی ویرگول."),
            q("Where do commas go in a non-essential clause?",
              ["Before and after the clause", "Only before it", "Nowhere"],
              "Before and after the clause",
              "The clause interrupts the sentence and closes with a comma.",
              "جمله جمله را می‌شکند و با ویرگول بسته می‌شود."),
        ],
    },
    {
        "section": "13-9",
        "title": "Expressions of quantity in adjective clauses",
        "title_fa": "عبارت‌های مقدار در جمله‌های وصفی",
        "use_en": "A quantity word can open the clause with of whom or of which: the students, most of whom passed; the books, some of which are new. The pattern carries all, most, many, some, few, none, both, either, neither and the numbers. The clause is almost always non-essential, so it takes commas, and whom is used for people, which for things.",
        "use_fa": "واژهٔ مقدار می‌تواند جمله را با of whom یا of which باز کند: the students, most of whom passed؛ the books, some of which are new. این الگو all، most، many، some، few، none، both، either، neither و عددها را در خود دارد. جمله تقریباً همیشه غیرلازم است، پس ویرگول می‌گیرد، و whom برای اشخاص و which برای اشیاء به کار می‌رود.",
        "form_en": "noun + , + quantity + of whom / of which + verb",
        "examples": [
            {"en": "The class has thirty students, most of whom are beginners.",
             "fa": "کلاس سی دانش‌آموز دارد که بیشترشان مبتدی‌اند."},
            {"en": "She wrote four novels, two of which were translated.",
             "fa": "چهار رمان نوشت که دو تایشان ترجمه شد."},
            {"en": "He has three brothers, all of whom live abroad.",
             "fa": "سه برادر دارد که همه‌شان خارج از کشور زندگی می‌کنند."},
        ],
        "exercises": [
            ex("The team has eleven players, all of ___ train daily. (people)", "whom",
               "People take of whom.",
               "اشخاص of whom می‌گیرند."),
            ex("I read two reports, neither of ___ was useful. (things)", "which",
               "Things take of which.",
               "اشیاء of which می‌گیرند."),
            ex("There were ten questions, some of ___ were difficult. (things)", "which",
               "A quantity of things takes of which.",
               "مقداری از اشیاء of which می‌گیرد."),
        ],
        "exam": [
            q("The village has 200 people, many of ___ work in the city.",
              ["whom", "which", "who"], "whom",
              "People after a quantity take of whom.",
              "اشخاص پس از مقدار of whom می‌گیرند."),
            q("She bought three dresses, one of ___ was blue.",
              ["which", "whom", "who"], "which",
              "Things after a quantity take of which.",
              "اشیاء پس از مقدار of which می‌گیرند."),
            q("Which sentence is correctly punctuated?",
              ["The students, most of whom passed, were happy.",
               "The students most of whom passed were happy.",
               "The students, most of who passed, were happy."],
              "The students, most of whom passed, were happy.",
              "The clause is non-essential and takes whom after of.",
              "جمله غیرلازم است و پس از of از whom استفاده می‌کند."),
        ],
    },
    {
        "section": "13-10",
        "title": "Which to modify a whole sentence",
        "title_fa": "which برای توصیف تمام جمله",
        "use_en": "A clause with which can comment on the whole sentence in front of it rather than on one noun: he arrived late, which annoyed everyone. The comma is required, which is the only pronoun allowed here, and that is impossible. The comment can sit at the end or, more formally, after the subject: the plan, which surprised us all, worked.",
        "use_fa": "جمله‌ای با which می‌تواند دربارهٔ تمام جملهٔ پیش از خود نظر بدهد نه دربارهٔ یک اسم: he arrived late, which annoyed everyone. ویرگول لازم است، which تنها ضمیر مجاز در این جایگاه است و that ممکن نیست. این نظر می‌تواند در پایان بیاید یا به شکلی رسمی‌تر پس از فاعل: the plan, which surprised us all, worked.",
        "form_en": "sentence + , which + verb ...  ·  subject + , which + verb, + rest",
        "examples": [
            {"en": "He arrived late, which annoyed everyone.",
             "fa": "دیر رسید که همه را آزرد."},
            {"en": "The plan worked, which surprised us all.",
             "fa": "طرح جواب داد که همه‌مان را غافلگیر کرد."},
            {"en": "She passed the exam, which made her parents proud.",
             "fa": "در امتحان قبول شد که پدر و مادرش را سربلند کرد."},
        ],
        "exercises": [
            ex("It rained all week, ___ ruined our trip.", "which",
               "A comment on the whole sentence takes which.",
               "نظر دربارهٔ تمام جمله which می‌گیرد."),
            ex("The train was late, ___ meant we missed the start.", "which",
               "The comma and which introduce the consequence.",
               "ویرگول و which نتیجه را می‌آورند."),
            ex("He forgot my name, ___ was embarrassing. (whole sentence)", "which",
               "Only which can modify a sentence.",
               "تنها which می‌تواند جمله را توصیف کند."),
        ],
        "exam": [
            q("She spoke first, ___ impressed the audience.",
              ["which", "that", "who"], "which",
              "A whole-sentence comment takes which.",
              "نظر دربارهٔ تمام جمله which می‌گیرد."),
            q("Which pronoun is impossible here? — He lied, ___ surprised nobody.",
              ["that", "which", "either one"], "that",
              "That cannot modify a whole sentence.",
              "that نمی‌تواند تمام جمله را توصیف کند."),
            q("Where must the comma go?",
              ["Before which", "Nowhere", "After which only"], "Before which",
              "The comment is non-essential and starts with a comma.",
              "نظر غیرلازم است و با ویرگول آغاز می‌شود."),
        ],
    },
    {
        "section": "13-11",
        "title": "Reducing adjective clauses to adjective phrases",
        "title_fa": "کوتاه‌کردن جمله‌های وصفی به عبارت وصفی",
        "use_en": "An adjective clause can lose its pronoun and its be verb, leaving a phrase: the man who is standing there becomes the man standing there; the car which was stolen becomes the car stolen. An active clause keeps its -ing form; a passive clause keeps its past participle. If the clause has no be, the reduction usually does not work, and an essential clause can be reduced while a non-essential one keeps its commas.",
        "use_fa": "جملهٔ وصفی می‌تواند ضمیر و فعل be خود را از دست بدهد و به عبارت تبدیل شود: the man who is standing there به the man standing there و the car which was stolen به the car stolen بدل می‌شود. جملهٔ معلوم شکل ing- را نگه می‌دارد و جملهٔ مجهول اسم مفعول را. اگر جمله be نداشته باشد کوتاه‌سازی معمولاً ممکن نیست، و جملهٔ لازم کوتاه می‌شود در حالی که جملهٔ غیرلازم ویرگول‌هایش را نگه می‌دارد.",
        "form_en": "who / which + be + -ing → -ing phrase  ·  who / which + be + past participle → past participle phrase",
        "examples": [
            {"en": "The man standing by the door is my uncle.",
             "fa": "مردی که کنار در ایستاده عموی من است."},
            {"en": "The car stolen last night was found today.",
             "fa": "ماشینی که دیشب دزدیده شد امروز پیدا شد."},
            {"en": "The students sitting at the back are new.",
             "fa": "دانش‌آموزانی که عقب نشسته‌اند تازه‌واردند."},
        ],
        "exercises": [
            ex("The girl who is singing on stage is my sister. → The girl ___ on stage is my sister.",
               "singing",
               "An active be clause reduces to the -ing form.",
               "جملهٔ معلوم با be به شکل ing- کوتاه می‌شود."),
            ex("The letters which were written by hand were kept. → The letters ___ by hand were kept.",
               "written",
               "A passive be clause reduces to the past participle.",
               "جملهٔ مجهول با be به اسم مفعول کوتاه می‌شود."),
            ex("The house which was built in 1900 is famous. → The house ___ in 1900 is famous.",
               "built",
               "The passive participle replaces which was.",
               "اسم مفعول جای which was را می‌گیرد."),
        ],
        "exam": [
            q("The woman ___ next to me was a doctor.",
              ["sitting", "sat", "who sitting"], "sitting",
              "An active clause with be reduces to -ing.",
              "جملهٔ معلوم با be به ing- کوتاه می‌شود."),
            q("The letters ___ yesterday arrived today.",
              ["sent", "sending", "were sent"], "sent",
              "A passive clause reduces to the past participle.",
              "جملهٔ مجهول به اسم مفعول کوتاه می‌شود."),
            q("Which clause cannot be reduced?",
              ["The man who owns the shop", "The man who is standing there",
               "The car which was stolen"], "The man who owns the shop",
              "There is no be to remove and the verb is not a participle.",
              "be ای نیست که حذف شود و فعل اسم مفعول نیست."),
        ],
    },
]


def main() -> int:
    data = json.loads(BOOKS.read_text(encoding="utf-8"))
    book = next(b for b in data["books"] if b.get("kind") == "grammar")

    old = [l for l in book["lessons"] if l.get("chapter") == CHAPTER]
    assert old, "chapter thirteen is not in the book"

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
        f"thirteen are complete, chart 1-1 to 13-11. The explanations and sentences "
        f"are written for this app; the book is the reference text."
    )
    book["about_fa"] = (
        f"دستور زبان تمام دوره، فصل به فصل و نمودار به نمودار: {size} ساختار از "
        f"بیست فصل کتاب، هر یک با قاعده، الگو، مثال، تمرین و یک آزمون کوتاه. "
        f"فصل‌های یک تا سیزده کامل‌اند، از نمودار ۱-۱ تا ۱۳-۱۱. توضیح‌ها و جمله‌ها "
        f"برای همین برنامه نوشته شده‌اند و کتاب متن مرجع است."
    )

    BOOKS.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")
    print(f"chapter thirteen: {len(LESSONS)} charts, {size} structures in the book")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
