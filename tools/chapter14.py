#!/usr/bin/env python3
"""Write chapter fourteen of the grammar book into books.json.

    python3 tools/chapter14.py

Chapter fourteen of *Understanding and Using English Grammar* is Gerunds and
Infinitives, Part 1. The book shipped with one placeholder section for it; this
replaces it with the chapter's twelve charts, written out like chapters three to
thirteen: the rule, the form, examples in both languages, three guided exercises
and a three-question check for each.

The sentences and explanations are written for this app. The book is the
reference text, and nothing in this file is transcribed from it.

It is idempotent: chapter fourteen is always rebuilt from this script.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "books.json"

CHAPTER = "Chapter 14"


def ex(prompt, answer, why_en, why_fa):
    return {"prompt": prompt, "answer": answer, "why_en": why_en, "why_fa": why_fa}


def q(text, options, answer, why_en, why_fa):
    assert answer in options and len(options) == 3, text
    return {"q": text, "options": options, "answer": answer,
            "why_en": why_en, "why_fa": why_fa}


LESSONS = [
    {
        "section": "14-1",
        "title": "Gerunds and infinitives: two verb forms after one verb",
        "title_fa": "اسم مصدر و مصدر: دو شکل فعل پس از یک فعل",
        "use_en": "A gerund is a verb with -ing used as a noun: swimming is good exercise. An infinitive is to plus the base verb, used as a noun or to show purpose: I want to swim. Both can be the subject or the object of a sentence. Because a gerund is a noun, it can follow a preposition; an infinitive cannot. The verb in front decides which form comes next, and that choice belongs to the verb, not to the meaning.",
        "use_fa": "اسم مصدر فعلی با ing- است که نقش اسم دارد: swimming is good exercise. مصدر to به‌همراه فعل ساده است که نقش اسم دارد یا هدف را می‌گوید: I want to swim. هر دو می‌توانند فاعل یا مفعول جمله باشند. چون اسم مصدر اسم است، می‌تواند پس از حرف اضافه بیاید و مصدر نمی‌تواند. فعل پیشین تعیین می‌کند کدام شکل بیاید و این انتخاب به فعل تعلق دارد نه به معنا.",
        "form_en": "gerund: verb + -ing (a noun)  ·  infinitive: to + base verb",
        "examples": [
            {"en": "Reading before bed helps me sleep.",
             "fa": "خواندن پیش از خواب به خوابم کمک می‌کند."},
            {"en": "She wants to learn Japanese.",
             "fa": "او می‌خواهد ژاپنی یاد بگیرد."},
            {"en": "My favourite hobby is cooking.",
             "fa": "سرگرمی محبوب من آشپزی است."},
        ],
        "exercises": [
            ex("___ is good exercise. (swim, as the subject)", "Swimming",
               "A gerund can be the subject of a sentence.",
               "اسم مصدر می‌تواند فاعل جمله باشد."),
            ex("I want ___ a new language. (learn)", "to learn",
               "Want is followed by an infinitive.",
               "پس از want مصدر می‌آید."),
            ex("She is afraid of ___ in deep water. (swim, after a preposition)", "swimming",
               "After a preposition only the gerund works.",
               "پس از حرف اضافه تنها اسم مصدر می‌آید."),
        ],
        "exam": [
            q("___ a car in this city is difficult.",
              ["Driving", "To driving", "Drive"], "Driving",
              "A subject before is takes the gerund or a full infinitive.",
              "فاعل پیش از is اسم مصدر یا مصدر کامل می‌گیرد."),
            q("They decided ___ the early train.",
              ["to take", "taking", "take"], "to take",
              "Decide takes an infinitive.",
              "decide مصدر می‌گیرد."),
            q("Which form can follow a preposition?",
              ["The gerund", "The infinitive", "The base verb"], "The gerund",
              "Only a noun form can follow a preposition.",
              "تنها شکل اسمی می‌تواند پس از حرف اضافه بیاید."),
        ],
    },
    {
        "section": "14-2",
        "title": "Verbs followed by a gerund",
        "title_fa": "فعل‌هایی که اسم مصدر می‌گیرند",
        "use_en": "Some verbs take a gerund and nothing else: enjoy, mind, finish, avoid, consider, suggest, keep, admit, deny, postpone, practise, quit, recommend, risk, tolerate, appreciate, dislike, miss, imagine, discuss, mention and understand. A few phrases behave the same way: can't help, feel like, be used to, look forward to and insist on. Putting an infinitive after one of these is the mistake to watch for.",
        "use_fa": "برخی فعل‌ها فقط اسم مصدر می‌گیرند: enjoy، mind، finish، avoid، consider، suggest، keep، admit، deny، postpone، practise، quit، recommend، risk، tolerate، appreciate، dislike، miss، imagine، discuss، mention و understand. چند عبارت هم همین رفتار را دارند: can't help، feel like، be used to، look forward to و insist on. گذاشتن مصدر پس از یکی از این‌ها خطایی است که باید مراقبش بود.",
        "form_en": "verb + gerund  ·  enjoy / avoid / finish / suggest / keep / mind + -ing",
        "examples": [
            {"en": "I enjoy swimming in the sea.",
             "fa": "از شنا در دریا لذت می‌برم."},
            {"en": "She finished writing the report at midnight.",
             "fa": "نیمه‌شب نوشتن گزارش را تمام کرد."},
            {"en": "We avoided driving through the city centre.",
             "fa": "از رانندگی در مرکز شهر پرهیز کردیم."},
        ],
        "exercises": [
            ex("I don't mind ___ early. (get up)", "getting up",
               "Mind takes a gerund.",
               "mind اسم مصدر می‌گیرد."),
            ex("He suggested ___ a taxi. (take)", "taking",
               "Suggest is followed by a gerund.",
               "پس از suggest اسم مصدر می‌آید."),
            ex("They postponed ___ the decision. (make)", "making",
               "Postpone takes a gerund, not an infinitive.",
               "postpone اسم مصدر می‌گیرد نه مصدر."),
        ],
        "exam": [
            q("She enjoys ___ to music while she works.",
              ["listening", "to listen", "listen"], "listening",
              "Enjoy always takes a gerund.",
              "enjoy همیشه اسم مصدر می‌گیرد."),
            q("We kept ___ until the lights went out.",
              ["talking", "to talk", "talk"], "talking",
              "Keep in this sense takes a gerund.",
              "keep با این معنا اسم مصدر می‌گیرد."),
            q("Which verb does not take a gerund? — I ___ to leave.",
              ["want", "avoid", "finish"], "want",
              "Want takes an infinitive, the others take gerunds.",
              "want مصدر می‌گیرد و دو فعل دیگر اسم مصدر."),
        ],
    },
    {
        "section": "14-3",
        "title": "Verbs followed by an infinitive",
        "title_fa": "فعل‌هایی که مصدر می‌گیرند",
        "use_en": "Another group takes to plus the base verb: want, need, hope, plan, decide, expect, promise, agree, refuse, offer, learn, manage, afford, seem, pretend, choose, fail, arrange, deserve, intend, threaten, hesitate and would like. These verbs point forward, towards something not yet done, which is why the to form fits them. A gerund after one of them sounds wrong to a native ear even when the meaning is clear.",
        "use_fa": "گروه دیگری to و فعل ساده می‌گیرد: want، need، hope، plan، decide، expect، promise، agree، refuse، offer، learn، manage، afford، seem، pretend، choose، fail، arrange، deserve، intend، threaten، hesitate و would like. این فعل‌ها به آینده و کاری که هنوز انجام نشده اشاره می‌کنند و همین شکل to را مناسب آن‌ها می‌کند. اسم مصدر پس از یکی از این‌ها برای گوش بومی نادرست است، حتی اگر معنا روشن باشد.",
        "form_en": "verb + to + base verb  ·  want / hope / decide / promise / refuse + to do",
        "examples": [
            {"en": "They decided to move abroad.",
             "fa": "تصمیم گرفتند به خارج نقل مکان کنند."},
            {"en": "I hope to see you soon.",
             "fa": "امیدوارم به‌زودی ببینمت."},
            {"en": "He refused to answer the question.",
             "fa": "از پاسخ دادن به پرسش سر باز زد."},
        ],
        "exercises": [
            ex("She promised ___ on time. (arrive)", "to arrive",
               "Promise takes an infinitive.",
               "promise مصدر می‌گیرد."),
            ex("I can't afford ___ a new car. (buy)", "to buy",
               "Afford is followed by an infinitive.",
               "پس از afford مصدر می‌آید."),
            ex("He managed ___ the last bus. (catch)", "to catch",
               "Manage takes an infinitive.",
               "manage مصدر می‌گیرد."),
        ],
        "exam": [
            q("We plan ___ in June.",
              ["to travel", "travelling", "travel"], "to travel",
              "Plan is followed by an infinitive.",
              "پس از plan مصدر می‌آید."),
            q("She pretended ___ asleep.",
              ["to be", "being", "be"], "to be",
              "Pretend takes an infinitive.",
              "pretend مصدر می‌گیرد."),
            q("Which sentence is correct?",
              ["He offered to help us.", "He offered helping us.",
               "He offered help us."], "He offered to help us.",
              "Offer takes an infinitive.",
              "offer مصدر می‌گیرد."),
        ],
    },
    {
        "section": "14-4",
        "title": "Infinitives with objects: ask someone to do",
        "title_fa": "مصدر با مفعول: ask someone to do",
        "use_en": "Many verbs put a person between themselves and the infinitive: ask, tell, want, need, expect, invite, remind, advise, encourage, permit, allow, force, persuade, teach and would like. The person is the object of the first verb and the doer of the second: she asked me to wait. Allow and permit change shape without a person and take a gerund instead: smoking is not allowed.",
        "use_fa": "بسیاری از فعل‌ها شخصی میان خود و مصدر می‌گذارند: ask، tell، want، need، expect، invite، remind، advise، encourage، permit، allow، force، persuade، teach و would like. آن شخص مفعول فعل اول و انجام‌دهندهٔ فعل دوم است: she asked me to wait. allow و permit بدون شخص شکل عوض می‌کنند و اسم مصدر می‌گیرند: smoking is not allowed.",
        "form_en": "verb + person + to + base verb  ·  allow / permit + gerund (no person)",
        "examples": [
            {"en": "She asked me to wait outside.",
             "fa": "از من خواست بیرون منتظر بمانم."},
            {"en": "They invited us to stay for dinner.",
             "fa": "ما را دعوت کردند که برای شام بمانیم."},
            {"en": "He reminded me to call my mother.",
             "fa": "یادم انداخت که به مادرم زنگ بزنم."},
        ],
        "exercises": [
            ex("The teacher told us ___ the exercise at home. (finish)", "to finish",
               "Tell takes a person and then an infinitive.",
               "tell شخص و سپس مصدر می‌گیرد."),
            ex("I want you ___ careful. (be)", "to be",
               "Want puts the person before the infinitive.",
               "want شخص را پیش از مصدر می‌آورد."),
            ex("Photography is not ___ in this museum. (allow, no person)", "allowed",
               "Without a person, allow takes the passive gerund form.",
               "بدون شخص، allow شکل مجهول می‌گیرد."),
        ],
        "exam": [
            q("She encouraged him ___ the course.",
              ["to take", "taking", "take"], "to take",
              "Encourage takes a person and an infinitive.",
              "encourage شخص و مصدر می‌گیرد."),
            q("They invited ___ to the wedding.",
              ["us", "we", "our"], "us",
              "The object before the infinitive is an object pronoun.",
              "مفعول پیش از مصدر ضمیر مفعولی است."),
            q("Which sentence is correct?",
              ["Smoking is not permitted here.", "To smoke is not permitted here.",
               "Smoke is not permitted here."], "Smoking is not permitted here.",
              "Permit without a person takes a gerund.",
              "permit بدون شخص اسم مصدر می‌گیرد."),
        ],
    },
    {
        "section": "14-5",
        "title": "Verbs that take either form: remember, stop, try",
        "title_fa": "فعل‌هایی که هر دو شکل را می‌پذیرند: remember، stop، try",
        "use_en": "A few verbs take both forms and the meaning changes. Remember to lock the door is a duty ahead; I remember locking the door is a memory behind. Stop to rest pauses in order to rest; stop resting ends the rest. Try to open it is an attempt; try opening it is an experiment. Regret, go on, mean and need behave the same way, so the form is the meaning.",
        "use_fa": "چند فعل هر دو شکل را می‌پذیرند و معنا عوض می‌شود. Remember to lock the door وظیفه‌ای در پیش است و I remember locking the door خاطره‌ای در گذشته. Stop to rest برای استراحت توقف می‌کند و stop resting استراحت را پایان می‌دهد. Try to open it تلاش است و try opening it آزمایش. regret، go on، mean و need هم همین‌گونه‌اند، پس شکل همان معناست.",
        "form_en": "remember / forget / stop / try / regret + to do (ahead)  ·  + doing (behind or in progress)",
        "examples": [
            {"en": "I stopped smoking last year.",
             "fa": "سال گذشته سیگار کشیدن را ترک کردم."},
            {"en": "We stopped to buy bread on the way home.",
             "fa": "در راه خانه برای خرید نان توقف کردیم."},
            {"en": "Remember to lock the door when you leave.",
             "fa": "یادت باشد وقتی رفتی در را قفل کنی."},
        ],
        "exercises": [
            ex("I clearly remember ___ the key on the table. (put)", "putting",
               "A memory of a past action takes the gerund.",
               "خاطرهٔ کار گذشته اسم مصدر می‌گیرد."),
            ex("Remember ___ the stove before you go out. (turn off)", "to turn off",
               "A duty ahead takes the infinitive.",
               "وظیفهٔ پیش‌رو مصدر می‌گیرد."),
            ex("He stopped ___ a cigarette. (smoke, in order to)", "to smoke",
               "Stopping in order to do something takes the infinitive.",
               "توقف برای انجام کاری مصدر می‌گیرد."),
        ],
        "exam": [
            q("She stopped ___ years ago and feels better.",
              ["smoking", "to smoke", "smoke"], "smoking",
              "The habit ended, so the gerund is right.",
              "عادت پایان یافته، پس اسم مصدر درست است."),
            q("I don't remember ___ him before.",
              ["meeting", "to meet", "meet"], "meeting",
              "A memory behind takes the gerund.",
              "خاطرهٔ گذشته اسم مصدر می‌گیرد."),
            q("Try ___ this button; the machine may start.",
              ["pressing", "to press", "press"], "pressing",
              "An experiment takes the gerund.",
              "آزمایش کردن اسم مصدر می‌گیرد."),
        ],
    },
    {
        "section": "14-6",
        "title": "Gerunds after prepositions",
        "title_fa": "اسم مصدر پس از حرف اضافه",
        "use_en": "A preposition is always followed by a noun, and a gerund is the noun form of a verb, so the pattern is fixed: good at drawing, interested in history, tired of waiting, instead of calling, without asking, thank you for helping. The same rule covers the multi-word prepositions: look forward to hearing, insist on paying, apologize for being late, in spite of being tired.",
        "use_fa": "حرف اضافه همیشه اسم می‌گیرد و اسم مصدر شکل اسمی فعل است، پس الگو ثابت است: good at drawing، interested in history، tired of waiting، instead of calling، without asking، thank you for helping. همین قاعده حرف اضافه‌های چندواژه‌ای را هم در بر می‌گیرد: look forward to hearing، insist on paying، apologize for being late، in spite of being tired.",
        "form_en": "preposition + gerund  ·  good at / interested in / instead of / without + -ing",
        "examples": [
            {"en": "She is good at solving problems.",
             "fa": "در حل مسئله خوب است."},
            {"en": "Thank you for helping us.",
             "fa": "ممنون که به ما کمک کردی."},
            {"en": "He left without saying goodbye.",
             "fa": "بی‌آنکه خداحافظی کند رفت."},
        ],
        "exercises": [
            ex("I am tired of ___ the same thing. (repeat)", "repeating",
               "The preposition of takes a gerund.",
               "حرف اضافهٔ of اسم مصدر می‌گیرد."),
            ex("She apologized for ___ late. (be)", "being",
               "For before a verb takes the gerund.",
               "for پیش از فعل اسم مصدر می‌گیرد."),
            ex("We talked about ___ a new house. (buy)", "buying",
               "About takes the gerund.",
               "about اسم مصدر می‌گیرد."),
        ],
        "exam": [
            q("He is interested in ___ old films.",
              ["collecting", "to collect", "collect"], "collecting",
              "In before a verb takes the gerund.",
              "in پیش از فعل اسم مصدر می‌گیرد."),
            q("Instead of ___ , she called a taxi.",
              ["walking", "to walk", "walk"], "walking",
              "Instead of is a preposition and takes the gerund.",
              "instead of حرف اضافه است و اسم مصدر می‌گیرد."),
            q("I'm looking forward to ___ from you.",
              ["hearing", "hear", "to hear"], "hearing",
              "The to here is a preposition, so the gerund follows.",
              "to اینجا حرف اضافه است، پس اسم مصدر می‌آید."),
        ],
    },
    {
        "section": "14-7",
        "title": "Go + gerund: go swimming, go shopping",
        "title_fa": "go + اسم مصدر: go swimming، go shopping",
        "use_en": "Go with a gerund names a leisure activity that involves moving to do it: go swimming, go shopping, go fishing, go skiing, go hiking, go jogging, go camping, go dancing, go sightseeing, go running. The pattern is not open to every verb: you go swimming but you do not go eating. When the activity has its own verb, use that verb instead: go to bed, not go sleeping.",
        "use_fa": "go با اسم مصدر فعالیتی فراغتی را می‌گوید که برای انجامش جابه‌جا می‌شوید: go swimming، go shopping، go fishing، go skiing، go hiking، go jogging، go camping، go dancing، go sightseeing، go running. این الگو برای هر فعلی باز نیست: go swimming درست است و go eating نه. وقتی فعالیت فعل خودش را دارد، همان فعل را به کار ببرید: go to bed و نه go sleeping.",
        "form_en": "go + -ing (an activity you travel to do)  ·  go swimming / shopping / hiking",
        "examples": [
            {"en": "We went hiking last weekend.",
             "fa": "آخر هفتهٔ گذشته به کوه‌پیمایی رفتیم."},
            {"en": "They go dancing every Friday.",
             "fa": "هر جمعه به رقص می‌روند."},
            {"en": "Let's go shopping this afternoon.",
             "fa": "بیا بعدازظهر برویم خرید."},
        ],
        "exercises": [
            ex("We went ___ in the lake last summer. (swim)", "swimming",
               "Go takes the gerund for the activity.",
               "go برای فعالیت اسم مصدر می‌گیرد."),
            ex("They go ___ in the mountains every winter. (ski)", "skiing",
               "The activity after go is a gerund.",
               "فعالیت پس از go اسم مصدر است."),
            ex("Let's go ___ for the party. (shop)", "shopping",
               "Shopping is the fixed activity with go.",
               "shopping فعالیت ثابت با go است."),
        ],
        "exam": [
            q("We went ___ along the coast.",
              ["sailing", "to sail", "sail"], "sailing",
              "Go plus an activity takes the gerund.",
              "go با فعالیت اسم مصدر می‌گیرد."),
            q("Which phrase is wrong?",
              ["go eating", "go fishing", "go camping"], "go eating",
              "Not every verb forms a go activity.",
              "هر فعلی فعالیت go نمی‌سازد."),
            q("They go ___ every Saturday morning.",
              ["jogging", "to jog", "jog"], "jogging",
              "A repeated activity with go is a gerund.",
              "فعالیت تکرارشده با go اسم مصدر است."),
        ],
    },
    {
        "section": "14-8",
        "title": "Special expressions followed by -ing",
        "title_fa": "عبارت‌های ویژه‌ای که ing- می‌گیرند",
        "use_en": "A set of fixed expressions ends in a noun slot and therefore takes the gerund: can't help laughing, can't stand waiting, don't mind helping, it's no use arguing, it's worth trying, have trouble sleeping, spend time reading, waste time worrying, be busy working, feel like leaving, there's no point in calling. The -ing form here is not a progressive verb; it is the noun the expression needs.",
        "use_fa": "مجموعه‌ای از عبارت‌های ثابت به جایگاه اسم می‌رسند و از این رو اسم مصدر می‌گیرند: can't help laughing، can't stand waiting، don't mind helping، it's no use arguing، it's worth trying، have trouble sleeping، spend time reading، waste time worrying، be busy working، feel like leaving، there's no point in calling. شکل ing- اینجا فعل استمراری نیست؛ اسمی است که عبارت لازم دارد.",
        "form_en": "expression + gerund  ·  can't help / it's no use / be busy / spend time + -ing",
        "examples": [
            {"en": "I can't help laughing when he tells that story.",
             "fa": "وقتی آن ماجرا را می‌گوید نمی‌توانم جلوی خنده‌ام را بگیرم."},
            {"en": "It's no use arguing with him.",
             "fa": "بحث کردن با او بی‌فایده است."},
            {"en": "She spends hours practising the piano.",
             "fa": "ساعت‌ها پیانو تمرین می‌کند."},
        ],
        "exercises": [
            ex("It's no use ___ about it now. (worry)", "worrying",
               "No use takes the gerund.",
               "no use اسم مصدر می‌گیرد."),
            ex("I can't stand ___ in a queue. (wait)", "waiting",
               "Can't stand takes the gerund.",
               "can't stand اسم مصدر می‌گیرد."),
            ex("He is busy ___ for the exam. (prepare)", "preparing",
               "Busy before a verb takes the gerund.",
               "busy پیش از فعل اسم مصدر می‌گیرد."),
        ],
        "exam": [
            q("It's worth ___ this book twice.",
              ["reading", "to read", "read"], "reading",
              "Worth takes the gerund.",
              "worth اسم مصدر می‌گیرد."),
            q("I have trouble ___ his handwriting.",
              ["reading", "to read", "read"], "reading",
              "Have trouble takes the gerund.",
              "have trouble اسم مصدر می‌گیرد."),
            q("Which sentence is correct?",
              ["She wasted time complaining.", "She wasted time to complain.",
               "She wasted time complain."], "She wasted time complaining.",
              "Waste time takes the gerund.",
              "waste time اسم مصدر می‌گیرد."),
        ],
    },
    {
        "section": "14-9",
        "title": "It + infinitive; gerunds and infinitives as subjects",
        "title_fa": "it + مصدر؛ اسم مصدر و مصدر در جایگاه فاعل",
        "use_en": "An infinitive can be the subject, but English prefers to hold the place with it and move the infinitive to the end: it is easy to make mistakes. A gerund as the subject is shorter and more common in speech: learning a language takes time. Both appear after be: the hardest part is finding a quiet place. It plus an adjective plus an infinitive also carries a comment on a person: it was kind of you to help.",
        "use_fa": "مصدر می‌تواند فاعل باشد، اما انگلیسی ترجیح می‌دهد جای آن را با it نگه دارد و مصدر را به پایان ببرد: it is easy to make mistakes. اسم مصدر در جایگاه فاعل کوتاه‌تر و در گفتار رایج‌تر است: learning a language takes time. هر دو پس از be می‌آیند: the hardest part is finding a quiet place. it و صفت و مصدر هم نظری دربارهٔ شخص می‌دهد: it was kind of you to help.",
        "form_en": "it + be + adjective + to + verb  ·  gerund + verb  ·  be + gerund / infinitive",
        "examples": [
            {"en": "It is easy to make mistakes when you are tired.",
             "fa": "وقتی خسته‌اید اشتباه کردن آسان است."},
            {"en": "Learning a language takes time.",
             "fa": "یادگیری یک زبان زمان می‌برد."},
            {"en": "It was kind of you to help.",
             "fa": "لطف کردی که کمک کردی."},
        ],
        "exercises": [
            ex("___ is difficult to change a habit. (empty subject)", "It",
               "English holds the subject place with it.",
               "انگلیسی جای فاعل را با it نگه می‌دارد."),
            ex("___ in the morning is my favourite habit. (walk, subject)", "Walking",
               "A habit as the subject is natural as a gerund.",
               "عادت در جایگاه فاعل با اسم مصدر طبیعی است."),
            ex("It is important ___ the instructions. (read)", "to read",
               "It is important is followed by an infinitive.",
               "پس از it is important مصدر می‌آید."),
        ],
        "exam": [
            q("___ is hard to say goodbye.",
              ["It", "That", "There"], "It",
              "The infinitive moves to the end behind it.",
              "مصدر پشت it به پایان می‌رود."),
            q("___ a car in this traffic is stressful.",
              ["Driving", "To driving", "Drive"], "Driving",
              "A gerund can be the subject.",
              "اسم مصدر می‌تواند فاعل باشد."),
            q("The best part was ___ the sea again.",
              ["seeing", "to seeing", "see"], "seeing",
              "After be, a gerund names the activity.",
              "پس از be اسم مصدر فعالیت را می‌گوید."),
        ],
    },
    {
        "section": "14-10",
        "title": "Reference list of verbs followed by infinitives",
        "title_fa": "فهرست مرجع فعل‌هایی که مصدر می‌گیرند",
        "use_en": "This chart is a list to return to rather than a rule to learn: agree, appear, arrange, attempt, care, choose, decide, demand, deserve, expect, fail, forget, hesitate, hope, intend, learn, manage, mean, need, offer, plan, prepare, pretend, promise, refuse, remember, seem, tend, threaten, want and wish all take to plus the base verb. When a verb is new, check it here before writing the second verb.",
        "use_fa": "این نمودار فهرستی است برای مراجعه نه قاعده‌ای برای حفظ: agree، appear، arrange، attempt، care، choose، decide، demand، deserve، expect، fail، forget، hesitate، hope، intend، learn، manage، mean، need، offer، plan، prepare، pretend، promise، refuse، remember، seem، tend، threaten، want و wish همگی to و فعل ساده می‌گیرند. هرگاه فعلی تازه بود، پیش از نوشتن فعل دوم آن را اینجا ببینید.",
        "form_en": "verb + to + base verb (a reference list, not a meaning rule)",
        "examples": [
            {"en": "He tends to arrive early.",
             "fa": "او معمولاً زود می‌رسد."},
            {"en": "She hesitated to ask for help.",
             "fa": "برای درخواست کمک تردید کرد."},
            {"en": "They arranged to meet at six.",
             "fa": "ترتیب دادند که ساعت شش همدیگر را ببینند."},
        ],
        "exercises": [
            ex("She seems ___ tired today. (be)", "to be",
               "Seem belongs to the infinitive list.",
               "seem در فهرست مصدر است."),
            ex("We expect ___ the results tomorrow. (get)", "to get",
               "Expect is followed by an infinitive.",
               "expect مصدر می‌گیرد."),
            ex("He failed ___ the deadline. (meet)", "to meet",
               "Fail is followed by an infinitive.",
               "fail مصدر می‌گیرد."),
        ],
        "exam": [
            q("They agreed ___ the costs.",
              ["to share", "sharing", "share"], "to share",
              "Agree takes an infinitive.",
              "agree مصدر می‌گیرد."),
            q("The window appears ___ broken.",
              ["to be", "being", "be"], "to be",
              "Appear takes an infinitive.",
              "appear مصدر می‌گیرد."),
            q("Which verb is not on the infinitive list?",
              ["enjoy", "intend", "deserve"], "enjoy",
              "Enjoy takes a gerund.",
              "enjoy اسم مصدر می‌گیرد."),
        ],
    },
    {
        "section": "14-11",
        "title": "Reference list of verbs followed by gerunds",
        "title_fa": "فهرست مرجع فعل‌هایی که اسم مصدر می‌گیرند",
        "use_en": "The matching list for the other form: admit, advise, appreciate, avoid, consider, delay, deny, discuss, dislike, enjoy, finish, imagine, mention, mind, miss, permit, postpone, practise, quit, recommend, regret, risk, suggest, tolerate and understand take -ing. Several of them also report something said or thought, which is why deny taking and admit making are so common in careful writing.",
        "use_fa": "فهرست متناظر برای شکل دیگر: admit، advise، appreciate، avoid، consider، delay، deny، discuss، dislike، enjoy، finish، imagine، mention، mind، miss، permit، postpone، practise، quit، recommend، regret، risk، suggest، tolerate و understand شکل ing- می‌گیرند. چند تایشان چیزی گفته یا اندیشیده را هم نقل می‌کنند و همین deny taking و admit making را در نوشتار دقیق رایج می‌کند.",
        "form_en": "verb + gerund (a reference list)  ·  deny / admit / suggest / recommend + -ing",
        "examples": [
            {"en": "I miss living near the sea.",
             "fa": "زندگی نزدیک دریا را دلم می‌خواهد."},
            {"en": "He denied taking the money.",
             "fa": "انکار کرد که پول را برداشته است."},
            {"en": "We discussed moving house.",
             "fa": "دربارهٔ اسباب‌کشی صحبت کردیم."},
        ],
        "exercises": [
            ex("She admitted ___ the window. (break)", "breaking",
               "Admit takes the gerund.",
               "admit اسم مصدر می‌گیرد."),
            ex("They considered ___ the offer. (accept)", "accepting",
               "Consider takes the gerund.",
               "consider اسم مصدر می‌گیرد."),
            ex("He risked ___ his job. (lose)", "losing",
               "Risk takes the gerund.",
               "risk اسم مصدر می‌گیرد."),
        ],
        "exam": [
            q("She mentioned ___ the film before.",
              ["seeing", "to see", "see"], "seeing",
              "Mention takes a gerund.",
              "mention اسم مصدر می‌گیرد."),
            q("They delayed ___ the decision.",
              ["making", "to make", "make"], "making",
              "Delay takes a gerund.",
              "delay اسم مصدر می‌گیرد."),
            q("Which sentence is correct?",
              ["I don't tolerate rudeness.", "I don't tolerate to be rude.",
               "I don't tolerate be rude."], "I don't tolerate rudeness.",
              "Tolerate takes a noun or a gerund.",
              "tolerate اسم یا اسم مصدر می‌گیرد."),
        ],
    },
    {
        "section": "14-12",
        "title": "Reference list of preposition combinations followed by gerunds",
        "title_fa": "فهرست مرجع ترکیب‌های حرف اضافه با اسم مصدر",
        "use_en": "These pairs of a word and a preposition always end in a gerund: accuse someone of, apologize for, approve of, believe in, complain about, concentrate on, depend on, dream of, insist on, object to, prevent someone from, succeed in, think of, worry about, look forward to, get used to, be afraid of, be guilty of, be proud of, be responsible for. Memorise the pair, because the preposition is not predictable from the verb.",
        "use_fa": "این جفت‌های واژه و حرف اضافه همیشه با اسم مصدر تمام می‌شوند: accuse someone of، apologize for، approve of، believe in، complain about، concentrate on، depend on، dream of، insist on، object to، prevent someone from، succeed in، think of، worry about، look forward to، get used to، be afraid of، be guilty of، be proud of، be responsible for. جفت را حفظ کنید، چون حرف اضافه از فعل قابل پیش‌بینی نیست.",
        "form_en": "word + preposition + gerund  ·  apologize for / insist on / succeed in / look forward to + -ing",
        "examples": [
            {"en": "She apologized for being late.",
             "fa": "برای دیر رسیدن عذرخواهی کرد."},
            {"en": "They insisted on paying for dinner.",
             "fa": "اصرار کردند که هزینهٔ شام را بپردازند."},
            {"en": "I'm looking forward to hearing from you.",
             "fa": "منتظر شنیدن خبر از شما هستم."},
        ],
        "exercises": [
            ex("He succeeded in ___ the exam. (pass)", "passing",
               "Succeed in takes the gerund.",
               "succeed in اسم مصدر می‌گیرد."),
            ex("We complained about ___ so long. (wait)", "waiting",
               "Complain about takes the gerund.",
               "complain about اسم مصدر می‌گیرد."),
            ex("She is proud of ___ her degree. (finish)", "finishing",
               "Proud of takes the gerund.",
               "proud of اسم مصدر می‌گیرد."),
        ],
        "exam": [
            q("They prevented him from ___.",
              ["leaving", "to leave", "leave"], "leaving",
              "Prevent from takes the gerund.",
              "prevent from اسم مصدر می‌گیرد."),
            q("I'm used to ___ up early.",
              ["getting", "get", "to get"], "getting",
              "Be used to ends in a preposition, so the gerund follows.",
              "be used to به حرف اضافه ختم می‌شود، پس اسم مصدر می‌آید."),
            q("Which pair is correct?",
              ["depend on hearing", "depend on to hear", "depend hearing"],
              "depend on hearing",
              "The pair depend on takes the gerund.",
              "جفت depend on اسم مصدر می‌گیرد."),
        ],
    },
]


def main() -> int:
    data = json.loads(BOOKS.read_text(encoding="utf-8"))
    book = next(b for b in data["books"] if b.get("kind") == "grammar")

    old = [l for l in book["lessons"] if l.get("chapter") == CHAPTER]
    assert old, "chapter fourteen is not in the book"

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
    print(f"chapter fourteen: {len(LESSONS)} charts, {size} structures in the book")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
