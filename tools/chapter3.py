#!/usr/bin/env python3
"""Write chapter three of the grammar book into books.json.

    python3 tools/chapter3.py

Chapter three of *Understanding and Using English Grammar* is Future Time,
charts 3-1 to 3-10. The book shipped with three summary sections for it
(3-1, 3-3, 3-5); this replaces them with the book's ten charts, written out
like chapters one and two: the rule, the form, examples in both languages,
three guided exercises and a three-question check for each.

It is idempotent: running it twice gives the same file, because it always
builds chapter three from this script rather than from what is already there.
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
        "n": 17,
        "section": "3-1",
        "title": "Expressing future time: be going to and will",
        "title_fa": "بیان آینده: be going to و will",
        "use_en": "English has no single future tense. The future is expressed with be going to and with will, and both point forward in time. Be going to usually carries a plan made earlier or evidence you can see now; will usually carries a decision made at the moment of speaking, a promise, an offer, or a prediction based on opinion.",
        "use_fa": "انگلیسی زمان آیندهٔ واحدی ندارد؛ آینده با be going to و will بیان می‌شود و هر دو به آینده اشاره می‌کنند. be going to معمولاً برنامه‌ای را نشان می‌دهد که پیش‌تر گرفته شده یا نشانه‌ای که همین حالا دیده می‌شود؛ will معمولاً تصمیمی را نشان می‌دهد که در همان لحظهٔ گفتن گرفته می‌شود، یا قول، پیشنهاد و پیش‌بینی بر پایهٔ نظر گوینده.",
        "form_en": "be going to + base verb  ·  will + base verb",
        "examples": [
            {"en": "We are going to visit my grandmother on Friday. We bought the tickets.",
             "fa": "جمعه به دیدن مادربزرگم می‌رویم. بلیت‌ها را خریده‌ایم."},
            {"en": "The phone is ringing. I will answer it.",
             "fa": "تلفن زنگ می‌زند. من جواب می‌دهم."},
            {"en": "Look at those clouds. It is going to rain.",
             "fa": "به آن ابرها نگاه کن. دارد باران می‌آید."},
        ],
        "exercises": [
            ex("“The bag is heavy.” “I ___ (carry) it for you.”", "will carry",
               "An offer made at the moment of speaking takes will.",
               "پیشنهادی که در همان لحظهٔ گفتن مطرح می‌شود با will می‌آید."),
            ex("We ___ (visit) my aunt on Friday; we bought the tickets yesterday.",
               "are going to visit",
               "The plan existed before this conversation, so be going to.",
               "برنامه پیش از این گفت‌وگو وجود داشته، پس be going to."),
            ex("Look at the sky! It ___ (rain) soon.", "is going to rain",
               "Something you can see now is evidence, and evidence takes be going to.",
               "چیزی که همین حالا دیده می‌شود نشانه است و نشانه با be going to می‌آید."),
        ],
        "exam": [
            q("“I can't open this jar.” “___ help you.”",
              ["I'll", "I'm going to", "I help"], "I'll",
              "The decision is made as you speak, so the contraction of will.",
              "تصمیم در همان لحظه گرفته می‌شود، پس کوتاه‌شدهٔ will."),
            q("Sara ___ study medicine; she has already chosen her university.",
              ["will", "is going to", "goes to"], "is going to",
              "A choice already made is a plan, and plans take be going to.",
              "انتخابی که پیش‌تر انجام شده برنامه است و برنامه با be going to."),
            q("I think our team ___ win on Saturday.",
              ["is going to", "will", "wins"], "will",
              "An opinion about the future, with no evidence, takes will.",
              "نظری دربارهٔ آینده بدون نشانهٔ بیرونی با will می‌آید."),
        ],
    },
    {
        "n": 18,
        "section": "3-2",
        "title": "Forms with be going to",
        "title_fa": "شکل‌های be going to",
        "use_en": "Be going to is the verb be followed by going to and the base verb. Be changes with the subject: am, is, are. The negative puts not after be, and a question moves be in front of the subject. In fast speech going to sounds like gonna, but gonna is not written in careful English.",
        "use_fa": "be going to از فعل be و سپس going to و فعل ساده ساخته می‌شود. be با فاعل تغییر می‌کند: am، is، are. منفی، not را پس از be می‌آورد و پرسش، be را پیش از فاعل می‌گذارد. در گفتار سریع going to مانند gonna شنیده می‌شود، اما gonna در نوشتار رسمی نوشته نمی‌شود.",
        "form_en": "am / is / are + going to + base verb  ·  am / is / are + not + going to + base verb  ·  Am / Is / Are + subject + going to + base verb?",
        "examples": [
            {"en": "She is going to start a new job on Monday.",
             "fa": "او دوشنبه کار تازه‌ای را شروع می‌کند."},
            {"en": "They are not going to move this year.",
             "fa": "آن‌ها امسال اسباب‌کشی نمی‌کنند."},
            {"en": "Are you going to join us for dinner?",
             "fa": "برای شام به ما می‌پیوندی؟"},
        ],
        "exercises": [
            ex("My sisters ___ (be) going to travel to Shiraz in spring.", "are",
               "Sisters is plural, so the form of be is are.",
               "sisters جمع است، پس شکل be می‌شود are."),
            ex("He ___ (not / be) going to sell his bicycle.", "is not",
               "The negative puts not after be, and he takes is.",
               "منفی، not را پس از be می‌آورد و با he فعل is می‌گیرد."),
            ex("___ your father going to cook tonight?", "Is",
               "A question moves be before the subject; father is singular.",
               "پرسش be را پیش از فاعل می‌آورد؛ father مفرد است."),
        ],
        "exam": [
            q("___ they going to close the shop early today?",
              ["Are", "Do", "Is"], "Are",
              "The subject is they, so the question begins with are.",
              "فاعل they است، پس پرسش با are آغاز می‌شود."),
            q("I ___ going to forget this promise.",
              ["am not", "not am", "do not"], "am not",
              "Not follows the form of be, and I takes am.",
              "not پس از شکل be می‌آید و با I فعل am."),
            q("The bus ___ going to be late; the road is closed.",
              ["is", "are", "be"], "is",
              "The bus is singular, so the verb is is.",
              "the bus مفرد است، پس فعل is است."),
        ],
    },
    {
        "n": 19,
        "section": "3-3",
        "title": "Forms with will",
        "title_fa": "شکل‌های will",
        "use_en": "Will is the same for every subject: I will, she will, they will. The base verb follows it with no to and no -s. The negative is will not, shortened to won't, and a question puts will before the subject. Shall is old-fashioned except in offers and suggestions such as Shall I open the window?",
        "use_fa": "will برای همهٔ فاعل‌ها یکسان است: I will، she will، they will. پس از آن فعل ساده می‌آید، بدون to و بدون -s. منفی آن will not است که به won't کوتاه می‌شود و در پرسش، will پیش از فاعل می‌آید. shall جز در پیشنهادهایی مانند Shall I open the window? قدیمی شده است.",
        "form_en": "will + base verb  ·  will not / won't + base verb  ·  Will + subject + base verb?",
        "examples": [
            {"en": "I will call you when I get home.",
             "fa": "وقتی به خانه رسیدم به تو زنگ می‌زنم."},
            {"en": "He won't tell anyone about the surprise.",
             "fa": "او دربارهٔ آن غافلگیری به کسی نمی‌گوید."},
            {"en": "Will the store be open tomorrow?",
             "fa": "فروشگاه فردا باز خواهد بود؟"},
        ],
        "exercises": [
            ex("She ___ (not / come) to the party; she has a fever.", "won't come",
               "The negative of will is won't, followed by the base verb.",
               "منفی will می‌شود won't و پس از آن فعل ساده می‌آید."),
            ex("___ you help me with this box, please?", "Will",
               "A question begins with will, then the subject and the base verb.",
               "پرسش با will آغاز می‌شود، سپس فاعل و فعل ساده."),
            ex("They will ___ (arrive) before noon.", "arrive",
               "Will is followed by the base verb, with no to and no -s.",
               "پس از will فعل ساده می‌آید، بدون to و بدون -s."),
        ],
        "exam": [
            q("I ___ forget your kindness.",
              ["will never", "never will to", "am never"], "will never",
              "Will carries the future and never sits between will and the verb.",
              "will آینده را می‌سازد و never بین will و فعل می‌نشیند."),
            q("___ we meet at the library at four?",
              ["Shall", "Do", "Are"], "Shall",
              "Shall I / we is the polite form for a suggestion.",
              "Shall I / we شکل مؤدبانهٔ پیشنهاد است."),
            q("The children ___ be tired after the trip.",
              ["will", "wills", "are will"], "will",
              "Will never takes -s, whatever the subject.",
              "will هرگز -s نمی‌گیرد، هر چه فاعل باشد."),
        ],
    },
    {
        "n": 20,
        "section": "3-4",
        "title": "Certainty about the future: definitely, probably, maybe",
        "title_fa": "میزان اطمینان دربارهٔ آینده: definitely، probably، maybe",
        "use_en": "Will can be softened or strengthened by an adverb of certainty. Definitely and certainly mean you are sure; probably means it is likely; perhaps and maybe mean it is possible. The adverb usually sits between will and the base verb, or at the beginning of the sentence. Be sure to and be certain to carry the same strong meaning.",
        "use_fa": "will را می‌توان با قید میزان اطمینان ضعیف‌تر یا قوی‌تر کرد. definitely و certainly یعنی مطمئنی؛ probably یعنی احتمال زیاد است؛ perhaps و maybe یعنی ممکن است. این قید معمولاً بین will و فعل ساده می‌آید یا در آغاز جمله. be sure to و be certain to همان معنای قوی را می‌رسانند.",
        "form_en": "subject + will + definitely / probably / maybe + base verb",
        "examples": [
            {"en": "She will definitely pass the exam; she has studied all month.",
             "fa": "او قطعاً در آزمون قبول می‌شود؛ تمام ماه درس خوانده است."},
            {"en": "We will probably take the early train.",
             "fa": "احتمالاً با قطار زودتر می‌رویم."},
            {"en": "Maybe it will snow tonight.",
             "fa": "شاید امشب برف بیاید."},
        ],
        "exercises": [
            ex("He is a careful driver, so he ___ (definitely / not / have) an accident.",
               "definitely won't have",
               "A strong adverb of certainty sits between will and the verb.",
               "قید قوی اطمینان بین will و فعل می‌نشیند."),
            ex("___ (probably) they will arrive after dark.", "Probably",
               "An adverb of certainty can open the sentence before the subject.",
               "قید اطمینان می‌تواند جمله را پیش از فاعل آغاز کند."),
            ex("Take an umbrella; it ___ (be) sure to rain.", "is",
               "Be sure to is a fixed phrase and be agrees with it.",
               "be sure to عبارت ثابت است و be با آن هم‌خوان می‌شود."),
        ],
        "exam": [
            q("The test was easy, so I ___ get a good mark.",
              ["will probably", "probably will to", "am probably"], "will probably",
              "Probably comes between will and the base verb.",
              "probably بین will و فعل ساده می‌آید."),
            q("___ we will never see that old building again.",
              ["Perhaps", "Certain", "Definitely not"], "Perhaps",
              "Perhaps opens a sentence about a possibility.",
              "perhaps جمله‌ای دربارهٔ امکان را آغاز می‌کند."),
            q("She is certain ___ win the race.",
              ["to", "for", "that"], "to",
              "Be certain to is followed by the base verb.",
              "پس از be certain to فعل ساده می‌آید."),
        ],
    },
    {
        "n": 21,
        "section": "3-5",
        "title": "Be going to or will: which one?",
        "title_fa": "be going to یا will: کدام یک؟",
        "use_en": "Use be going to for a plan you made before speaking and for a prediction you can see evidence for. Use will for a decision made as you speak, for a promise, an offer, a refusal and a request, and for a prediction based on what you think or know. When both are possible, be going to sounds more settled and will sounds more immediate.",
        "use_fa": "be going to را برای برنامه‌ای که پیش از گفتن گرفته‌ای و پیش‌بینی‌ای که نشانه‌اش را می‌بینی به کار ببر. will را برای تصمیمی که همان لحظه گرفته می‌شود، قول، پیشنهاد، رد کردن و درخواست، و پیش‌بینی‌ای که بر پایهٔ فکر یا دانستهٔ توست. وقتی هر دو ممکن است، be going to قطعی‌تر و will فوری‌تر به گوش می‌رسد.",
        "form_en": "plan or evidence → be going to + base verb  ·  decision, offer, promise → will + base verb",
        "examples": [
            {"en": "I'm going to paint the kitchen this weekend. I bought the paint.",
             "fa": "این آخر هفته آشپزخانه را رنگ می‌کنم. رنگ را خریده‌ام."},
            {"en": "I'll paint it for you — you look tired.",
             "fa": "من آن را برایت رنگ می‌کنم — خسته به نظر می‌رسی."},
            {"en": "Watch out! You're going to drop those glasses.",
             "fa": "مواظب باش! آن لیوان‌ها را می‌اندازی."},
        ],
        "exercises": [
            ex("The kettle is boiling. ___ (I / make) tea?", "Shall I make",
               "An offer made now takes shall or will, not be going to.",
               "پیشنهاد در همین لحظه با shall یا will می‌آید، نه با be going to."),
            ex("We ___ (take) the six o'clock train; the tickets are in my bag.",
               "are going to take",
               "The arrangement already exists, so be going to.",
               "هماهنگی از پیش انجام شده، پس be going to."),
            ex("“I forgot my pen.” “Don't worry, I ___ (lend) you mine.”", "will lend",
               "A promise made on the spot takes will.",
               "قولی که همان لحظه داده می‌شود با will می‌آید."),
        ],
        "exam": [
            q("Those boxes are heavy. ___ you carry one?",
              ["Will", "Are going to", "Do"], "Will",
              "An offer at the moment of speaking uses will.",
              "پیشنهاد در لحظهٔ گفتن با will می‌آید."),
            q("Next year we ___ live in a smaller apartment; we signed the lease.",
              ["are going to", "will", "would"], "are going to",
              "A signed plan is be going to, not a promise.",
              "برنامهٔ امضاشده با be going to می‌آید، نه با قول."),
            q("Don't call at eight; I ___ have dinner then.",
              ["will", "am going to", "would"], "will",
              "The fact about the future is simply stated with will.",
              "واقعیتی دربارهٔ آینده به‌سادگی با will بیان می‌شود."),
        ],
    },
    {
        "n": 22,
        "section": "3-6",
        "title": "Expressing the future in time clauses",
        "title_fa": "بیان آینده در جمله‌های قیدی زمان",
        "use_en": "After when, before, after, as soon as, until and while, English uses the present, not will, even though the meaning is future. The main clause carries will or be going to. The same rule holds after if in a real condition: If it rains, we will stay home.",
        "use_fa": "پس از when، before، after، as soon as، until و while انگلیسی حال را به کار می‌برد، نه will، هرچند معنا آینده است. جملهٔ اصلی will یا be going to را دارد. همین قاعده پس از if در شرط واقعی هم برجاست: If it rains, we will stay home.",
        "form_en": "main clause (will / be going to) + time clause (present)  ·  When / Before / After / As soon as / Until + present, main clause",
        "examples": [
            {"en": "I will call you as soon as I arrive.",
             "fa": "به‌محض رسیدن به تو زنگ می‌زنم."},
            {"en": "Before you leave, turn off the lights.",
             "fa": "پیش از رفتن، چراغ‌ها را خاموش کن."},
            {"en": "We are going to eat after the movie ends.",
             "fa": "بعد از تمام شدن فیلم غذا می‌خوریم."},
        ],
        "exercises": [
            ex("We ___ (leave) before the traffic gets bad.", "will leave",
               "The main clause carries will; the time clause stays in the present.",
               "جملهٔ اصلی will دارد و جملهٔ قیدی زمان در حال می‌ماند."),
            ex("When she ___ (finish) her homework, she will go out.", "finishes",
               "After when, a future meaning uses the present simple.",
               "پس از when، معنای آینده با حال ساده بیان می‌شود."),
            ex("I will wait here until the bus ___ (come).", "comes",
               "Until is followed by the present, never by will.",
               "پس از until حال می‌آید، هرگز will."),
        ],
        "exam": [
            q("After he ___ the report, he will send it to you.",
              ["writes", "will write", "is writing"], "writes",
              "After introduces a time clause, which takes the present.",
              "after جملهٔ قیدی زمان می‌سازد که حال می‌گیرد."),
            q("___ it rains tomorrow, we will cancel the picnic.",
              ["If", "When", "Whether"], "If",
              "A real condition opens with if and a present verb.",
              "شرط واقعی با if و فعل حال آغاز می‌شود."),
            q("I will text you as soon as I ___ at the airport.",
              ["arrive", "will arrive", "arrived"], "arrive",
              "As soon as is a time clause, so the present is used.",
              "as soon as جملهٔ قیدی زمان است، پس حال به کار می‌رود."),
        ],
    },
    {
        "n": 23,
        "section": "3-7",
        "title": "The present progressive and simple present for future time",
        "title_fa": "حال استمراری و حال ساده برای بیان آینده",
        "use_en": "The present progressive describes a future arrangement: a time and often a place are already fixed. The simple present describes a schedule or timetable that will happen whatever anyone does. Both need a future time expression, or the sentence reads as present.",
        "use_fa": "حال استمراری هماهنگی آینده را بیان می‌کند: زمان و اغلب مکان از پیش مشخص شده است. حال ساده برنامه یا جدول زمانی را می‌گوید که در هر حال انجام می‌شود. هر دو به عبارت زمانی آینده نیاز دارند، وگرنه جمله حال خوانده می‌شود.",
        "form_en": "present progressive + future time (arrangement)  ·  simple present + future time (timetable)",
        "examples": [
            {"en": "I'm meeting Dr. Karimi at three tomorrow.",
             "fa": "فردا ساعت سه با دکتر کریمی ملاقات دارم."},
            {"en": "The train leaves at 7:15 every morning.",
             "fa": "قطار هر روز صبح ساعت ۷:۱۵ حرکت می‌کند."},
            {"en": "Classes start on September 23 this year.",
             "fa": "کلاس‌ها امسال ۲۳ سپتامبر شروع می‌شوند."},
        ],
        "exercises": [
            ex("We ___ (have) lunch with my uncle tomorrow at noon.", "are having",
               "A fixed arrangement with a time takes the present progressive.",
               "هماهنگی قطعی با زمان مشخص، حال استمراری می‌گیرد."),
            ex("The movie ___ (begin) at eight, so let's eat early.", "begins",
               "A timetable uses the simple present for a future event.",
               "جدول زمانی برای رویداد آینده حال ساده می‌گیرد."),
            ex("She ___ (fly) to Tehran on Monday morning; the ticket is booked.",
               "is flying",
               "A booked trip is an arrangement, so the present progressive.",
               "سفر رزروشده هماهنگی است، پس حال استمراری."),
        ],
        "exam": [
            q("The bank ___ at nine tomorrow, as usual.",
              ["opens", "is opening", "will opens"], "opens",
              "A regular timetable is stated in the simple present.",
              "جدول زمانی منظم با حال ساده گفته می‌شود."),
            q("I ___ the dentist at four; I made the appointment last week.",
              ["am seeing", "see", "will seen"], "am seeing",
              "An appointment is a fixed arrangement.",
              "نوبت پزشک هماهنگی قطعی است."),
            q("Our flight ___ at 6:40, so we should leave at four.",
              ["leaves", "is leaving to", "leave"], "leaves",
              "A published schedule takes the simple present, and the flight is singular.",
              "برنامهٔ منتشرشده حال ساده می‌گیرد و flight مفرد است."),
        ],
    },
    {
        "n": 24,
        "section": "3-8",
        "title": "Future progressive",
        "title_fa": "آیندهٔ استمراری",
        "use_en": "The future progressive describes an action that will be in progress at a particular moment in the future. It is will be plus the -ing form. It answers the question “What will you be doing at that time?” and often appears with this time tomorrow, at eight tonight, or all day.",
        "use_fa": "آیندهٔ استمراری کاری را توصیف می‌کند که در لحظهٔ مشخصی در آینده در جریان خواهد بود. با will be و شکل ing ساخته می‌شود و پاسخ پرسش «آن ساعت چه کار خواهی کرد؟» است. اغلب با this time tomorrow، at eight tonight یا all day می‌آید.",
        "form_en": "will + be + verb-ing",
        "examples": [
            {"en": "This time tomorrow we will be flying over the desert.",
             "fa": "فردا همین وقت بر فراز کویر پرواز می‌کنیم."},
            {"en": "Don't call at eight; I will be having dinner.",
             "fa": "ساعت هشت زنگ نزن؛ شام می‌خورم."},
            {"en": "They will be working all weekend on the project.",
             "fa": "آن‌ها تمام آخر هفته روی پروژه کار می‌کنند."},
        ],
        "exercises": [
            ex("At nine tonight I ___ (study) for the exam.", "will be studying",
               "The action is in progress at a future moment.",
               "کار در لحظه‌ای در آینده در جریان است."),
            ex("When you arrive, we ___ (wait) outside the station.", "will be waiting",
               "The waiting will already be happening at that moment.",
               "انتظار در آن لحظه در جریان خواهد بود."),
            ex("She ___ (not / work) tomorrow; the office is closed.", "won't be working",
               "The negative puts not after will, before be.",
               "منفی، not را پس از will و پیش از be می‌آورد."),
        ],
        "exam": [
            q("This time next week I ___ on a beach.",
              ["will be sitting", "will sitting", "am sit"], "will be sitting",
              "The future progressive is will be plus -ing.",
              "آیندهٔ استمراری will be به‌همراه ing است."),
            q("They ___ dinner when we get there.",
              ["will be having", "will have", "are have"], "will be having",
              "The dinner will be in progress when we arrive.",
              "شام هنگام رسیدن ما در جریان خواهد بود."),
            q("What ___ you be doing at noon?",
              ["will", "do", "are"], "will",
              "A question in the future progressive begins with will.",
              "پرسش در آیندهٔ استمراری با will آغاز می‌شود."),
        ],
    },
    {
        "n": 25,
        "section": "3-9",
        "title": "Future perfect",
        "title_fa": "آیندهٔ کامل",
        "use_en": "The future perfect says that an action will be finished before a particular time in the future. It is will have plus the past participle, and it usually appears with by, by the time, or before. The future perfect progressive, will have been + -ing, says how long an action will have been going on.",
        "use_fa": "آیندهٔ کامل می‌گوید کاری پیش از زمانی مشخص در آینده تمام خواهد شد. با will have و اسم مفعول ساخته می‌شود و معمولاً با by، by the time یا before می‌آید. آیندهٔ کامل استمراری، will have been + ing، می‌گوید کاری چه مدت در جریان خواهد بود.",
        "form_en": "will + have + past participle  ·  will + have + been + verb-ing",
        "examples": [
            {"en": "By Friday we will have finished the whole unit.",
             "fa": "تا جمعه تمام آن درس را تمام کرده‌ایم."},
            {"en": "By the time you arrive, she will have left.",
             "fa": "تا وقتی برسی، او رفته است."},
            {"en": "In June I will have been working here for five years.",
             "fa": "در ژوئن پنج سال است که اینجا کار می‌کنم."},
        ],
        "exercises": [
            ex("By next month, they ___ (build) the new bridge.", "will have built",
               "By next month marks completion before a future time.",
               "تا ماه آینده، پایان کار پیش از زمانی در آینده را نشان می‌دهد."),
            ex("Call me after eight; I ___ (finish) my homework by then.",
               "will have finished",
               "The homework will be complete before eight.",
               "تکالیف پیش از ساعت هشت تمام خواهد شد."),
            ex("By 2030 she ___ (teach) for twenty years.", "will have been teaching",
               "How long an action will have lasted takes will have been + -ing.",
               "مدت ادامهٔ کار با will have been + ing بیان می‌شود."),
        ],
        "exam": [
            q("By the time the guests come, we ___ everything.",
              ["will have prepared", "will prepare", "have prepared"], "will have prepared",
              "The preparing finishes before the guests arrive.",
              "آماده‌سازی پیش از رسیدن مهمان‌ها تمام می‌شود."),
            q("She ___ the report by Monday morning.",
              ["will have written", "will writing", "writes have"], "will have written",
              "Will have plus the past participle completes an action by a deadline.",
              "will have به‌همراه اسم مفعول، کار را تا یک مهلت کامل می‌کند."),
            q("Next year he ___ in this office for a decade.",
              ["will have been working", "will be work", "has worked"], "will have been working",
              "A duration up to a future point is the future perfect progressive.",
              "مدت تا نقطه‌ای در آینده، آیندهٔ کامل استمراری است."),
        ],
    },
    {
        "n": 26,
        "section": "3-10",
        "title": "Summary of verb tenses: the twelve tenses at a glance",
        "title_fa": "خلاصهٔ زمان‌های فعل: دوازده زمان در یک نگاه",
        "use_en": "English has twelve tense forms: simple, progressive, perfect and perfect progressive, each in the past, present and future. The simple form states a fact, the progressive shows an action in progress, the perfect looks back from a point in time, and the perfect progressive measures how long. Choosing a tense is choosing where the action sits in time and how the speaker wants to present it.",
        "use_fa": "انگلیسی دوازده شکل زمان دارد: ساده، استمراری، کامل و کامل استمراری، هر یک در گذشته، حال و آینده. شکل ساده واقعیتی را می‌گوید، استمراری کاری در جریان را نشان می‌دهد، کامل از نقطه‌ای در زمان به عقب نگاه می‌کند و کامل استمراری مدت را می‌سنجد. انتخاب زمان، انتخاب جای کار در زمان و شیوهٔ نگاه گوینده است.",
        "form_en": "simple: verb  ·  progressive: be + -ing  ·  perfect: have + participle  ·  perfect progressive: have been + -ing",
        "examples": [
            {"en": "She works here. She is working now. She has worked here for years.",
             "fa": "او اینجا کار می‌کند. الان در حال کار است. سال‌هاست اینجا کار می‌کند."},
            {"en": "They had already eaten when we arrived.",
             "fa": "وقتی رسیدیم، آن‌ها پیش‌تر غذا خورده بودند."},
            {"en": "By next June she will have been teaching for twenty years.",
             "fa": "تا ژوئن آینده بیست سال است که درس می‌دهد."},
        ],
        "exercises": [
            ex("Look! The baby ___ (sleep).", "is sleeping",
               "An action happening now takes the present progressive.",
               "کاری که همین حالا در جریان است، حال استمراری می‌گیرد."),
            ex("We ___ (live) in this town since 2015.", "have lived",
               "Since 2015 reaches from the past up to now, so the present perfect.",
               "since 2015 از گذشته تا حال ادامه دارد، پس حال کامل."),
            ex("By the time we arrived, the film ___ (start).", "had started",
               "One past action finished before another, so the past perfect.",
               "یک کار گذشته پیش از کار گذشتهٔ دیگر تمام شده، پس گذشتهٔ کامل."),
        ],
        "exam": [
            q("He ___ his keys while he was running for the bus.",
              ["lost", "has lost", "had lost"], "lost",
              "A finished past moment takes the simple past.",
              "لحظهٔ گذشتهٔ تمام‌شده حال سادهٔ گذشته می‌گیرد."),
            q("I ___ here since eight o'clock this morning.",
              ["have been waiting", "wait", "waited"], "have been waiting",
              "A duration continuing up to now takes the present perfect progressive.",
              "مدتی که تا حال ادامه دارد، حال کامل استمراری می‌گیرد."),
            q("Next month they ___ married for ten years.",
              ["will have been", "will be", "have been"], "will have been",
              "A duration measured up to a future point is the future perfect.",
              "مدتی که تا نقطه‌ای در آینده سنجیده می‌شود، آیندهٔ کامل است."),
        ],
    },
]

ABOUT_EN = ("The grammar of the whole course, chapter by chapter and chart by chart: "
            "fifty structures from the book's twenty chapters, each with the rule, a "
            "pattern, examples of it, exercises and a short exam. Chapters one to three "
            "are complete, chart 1-1 to 3-10. The explanations and sentences are written "
            "for this app; the book is the reference text.")
ABOUT_FA = ("دستور زبان تمام دوره، فصل به فصل و نمودار به نمودار: پنجاه ساختار از بیست "
            "فصل کتاب، هر یک با قاعده، الگو، مثال، تمرین و یک آزمون کوتاه. فصل‌های یک تا "
            "سه کامل‌اند، از نمودار ۱-۱ تا ۳-۱۰. توضیح‌ها و جمله‌ها برای همین برنامه "
            "نوشته شده‌اند و کتاب متن مرجع است.")


def main() -> int:
    data = json.loads(BOOKS.read_text(encoding="utf-8"))
    book = next(b for b in data["books"] if b.get("kind") == "grammar")

    old = {l.get("section"): l for l in book["lessons"] if l.get("chapter") == "Chapter 3"}
    assert old, "chapter three is not in the book"
    first = book["lessons"].index(min(old.values(), key=lambda l: l["n"]))
    rest = [l for l in book["lessons"] if l.get("chapter") != "Chapter 3"]

    chapter3 = []
    for lesson in LESSONS:
        item = {"n": 0, "title": lesson["title"], "title_fa": lesson["title_fa"],
                "chapter": "Chapter 3", "section": lesson["section"],
                "use_en": lesson["use_en"], "use_fa": lesson["use_fa"],
                "form_en": lesson["form_en"], "examples": lesson["examples"],
                "exercises": lesson["exercises"], "exam": lesson["exam"]}
        chapter3.append(item)

    lessons = rest[:first] + chapter3 + rest[first:]
    for i, lesson in enumerate(lessons, 1):
        lesson["n"] = i
    book["lessons"] = lessons
    book["about_en"] = ABOUT_EN
    book["about_fa"] = ABOUT_FA

    BOOKS.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")
    print(f"chapter three: {len(chapter3)} charts, {len(lessons)} structures in the book")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
