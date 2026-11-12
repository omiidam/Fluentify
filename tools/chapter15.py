#!/usr/bin/env python3
"""Write chapter fifteen of the grammar book into books.json.

    python3 tools/chapter15.py

Chapter fifteen of *Understanding and Using English Grammar* is Gerunds and
Infinitives, Part 2. The book shipped with one placeholder section for it; this
replaces it with the chapter's ten charts, written out like chapters three to
fourteen: the rule, the form, examples in both languages, three guided exercises
and a three-question check for each.

The sentences and explanations are written for this app. The book is the
reference text, and nothing in this file is transcribed from it.

It is idempotent: chapter fifteen is always rebuilt from this script.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "books.json"

CHAPTER = "Chapter 15"


def ex(prompt, answer, why_en, why_fa):
    return {"prompt": prompt, "answer": answer, "why_en": why_en, "why_fa": why_fa}


def q(text, options, answer, why_en, why_fa):
    assert answer in options and len(options) == 3, text
    return {"q": text, "options": options, "answer": answer,
            "why_en": why_en, "why_fa": why_fa}


LESSONS = [
    {
        "section": "15-1",
        "title": "The infinitive of purpose: in order to",
        "title_fa": "مصدر هدف: in order to",
        "use_en": "To plus a verb answers the question why: I went out to buy bread. In order to says the same thing with more weight, and so as to is the third form. The negative is in order not to or so as not to, never to not. Before a noun or a gerund, for does the work instead: I went out for bread, thank you for coming.",
        "use_fa": "to به‌همراه فعل به پرسش «چرا» پاسخ می‌دهد: I went out to buy bread. in order to همین را با تأکید بیشتر می‌گوید و so as to شکل سوم است. منفی آن in order not to یا so as not to است، هرگز to not. پیش از اسم یا اسم مصدر، for این کار را می‌کند: I went out for bread، thank you for coming.",
        "form_en": "to + verb  ·  in order to / so as to + verb  ·  in order not to + verb  ·  for + noun",
        "examples": [
            {"en": "I went out to buy bread.",
             "fa": "برای خرید نان بیرون رفتم."},
            {"en": "She left early in order to catch the train.",
             "fa": "زود رفت تا به قطار برسد."},
            {"en": "He whispered so as not to wake the baby.",
             "fa": "آهسته حرف زد تا نوزاد را بیدار نکند."},
        ],
        "exercises": [
            ex("I called ___ ask about the job. (purpose)", "to",
               "Purpose before a verb takes to.",
               "هدف پیش از فعل با to می‌آید."),
            ex("We left early in order ___ miss the train. (negative purpose)", "not to",
               "The negative purpose is in order not to.",
               "هدف منفی in order not to است."),
            ex("Thank you ___ your help. (before a noun)", "for",
               "Before a noun, for carries the purpose.",
               "پیش از اسم، for هدف را می‌آورد."),
        ],
        "exam": [
            q("She saved money ___ buy a car.",
              ["to", "for", "for to"], "to",
              "Purpose before a verb takes to.",
              "هدف پیش از فعل to می‌گیرد."),
            q("He spoke quietly so as ___ wake anyone.",
              ["not to", "to not", "no to"], "not to",
              "The negative of so as to is so as not to.",
              "منفی so as to همان so as not to است."),
            q("We stopped ___ a coffee.",
              ["for", "to", "for to"], "for",
              "A noun after the purpose takes for.",
              "اسم پس از هدف for می‌گیرد."),
        ],
    },
    {
        "section": "15-2",
        "title": "Adjectives followed by infinitives",
        "title_fa": "صفت‌هایی که مصدر می‌گیرند",
        "use_en": "Many adjectives that describe a feeling or a readiness take an infinitive: glad, happy, sorry, sad, ready, eager, willing, reluctant, afraid, lucky, proud, surprised, able, unable, free, busy, careful, difficult and easy. The pattern is be plus adjective plus to plus verb: I am glad to help. When the person is named, of comes first: it was kind of you to call.",
        "use_fa": "بسیاری از صفت‌هایی که حس یا آمادگی را توصیف می‌کنند مصدر می‌گیرند: glad، happy، sorry، sad، ready، eager، willing، reluctant، afraid، lucky، proud، surprised، able، unable، free، busy، careful، difficult و easy. الگو be و صفت و to و فعل است: I am glad to help. اگر شخص نام برده شود، of اول می‌آید: it was kind of you to call.",
        "form_en": "be + adjective + to + base verb  ·  it + be + adjective + of + person + to + verb",
        "examples": [
            {"en": "I am glad to help.",
             "fa": "خوشحالم که کمک می‌کنم."},
            {"en": "She was eager to start the course.",
             "fa": "برای شروع دوره بی‌تاب بود."},
            {"en": "It was kind of you to call.",
             "fa": "لطف کردی که زنگ زدی."},
        ],
        "exercises": [
            ex("We are ready ___ the results. (hear)", "to hear",
               "Ready is followed by an infinitive.",
               "ready مصدر می‌گیرد."),
            ex("He was unable ___ the meeting. (attend)", "to attend",
               "Unable takes an infinitive.",
               "unable مصدر می‌گیرد."),
            ex("It was careless ___ him to forget the keys. (person)", "of",
               "A comment on a person takes of before the pronoun.",
               "نظر دربارهٔ شخص of را پیش از ضمیر می‌آورد."),
        ],
        "exam": [
            q("She is afraid ___ the truth.",
              ["to tell", "telling", "tell"], "to tell",
              "Afraid of an action takes the infinitive.",
              "afraid برای کار مصدر می‌گیرد."),
            q("It was generous ___ them to pay.",
              ["of", "for", "to"], "of",
              "A judgement of a person takes of.",
              "داوری دربارهٔ شخص of می‌گیرد."),
            q("I'm sorry ___ you waiting.",
              ["to keep", "keeping", "keep"], "to keep",
              "Sorry before an action takes the infinitive.",
              "sorry پیش از کار مصدر می‌گیرد."),
        ],
    },
    {
        "section": "15-3",
        "title": "Too and enough with infinitives",
        "title_fa": "too و enough با مصدر",
        "use_en": "Too before an adjective means more than is wanted, and the infinitive says what the excess prevents: the box was too heavy to lift. Enough comes after an adjective and before a noun, and the infinitive says what it makes possible: she is old enough to drive, we have enough time to finish. The two are opposites, and mixing their order is the usual mistake.",
        "use_fa": "too پیش از صفت یعنی بیش از حد لازم و مصدر می‌گوید آن زیادی مانع چه چیزی است: the box was too heavy to lift. enough پس از صفت و پیش از اسم می‌آید و مصدر می‌گوید چه چیزی را ممکن می‌کند: she is old enough to drive، we have enough time to finish. این دو متضادند و جابه‌جا کردن ترتیبشان خطای رایج است.",
        "form_en": "too + adjective + to + verb  ·  adjective + enough + to + verb  ·  enough + noun + to + verb",
        "examples": [
            {"en": "The box was too heavy to lift.",
             "fa": "جعبه برای بلند کردن بیش از حد سنگین بود."},
            {"en": "She is old enough to drive.",
             "fa": "به اندازهٔ کافی بزرگ است که رانندگی کند."},
            {"en": "We have enough time to finish.",
             "fa": "وقت کافی برای تمام کردن داریم."},
        ],
        "exercises": [
            ex("The coffee was too hot ___ drink. (verb)", "to",
               "Too plus an adjective is followed by to and a verb.",
               "too و صفت با to و فعل ادامه می‌یابد."),
            ex("He isn't tall ___ to reach the shelf. (after an adjective)", "enough",
               "Enough follows the adjective.",
               "enough پس از صفت می‌آید."),
            ex("We don't have ___ money to buy it. (before a noun)", "enough",
               "Enough comes before the noun.",
               "enough پیش از اسم می‌آید."),
        ],
        "exam": [
            q("The room was too small ___ five people.",
              ["to hold", "holding", "hold"], "to hold",
              "Too plus an adjective takes the infinitive.",
              "too و صفت مصدر می‌گیرد."),
            q("She spoke ___ quietly to be heard.",
              ["too", "enough", "very"], "too",
              "Too before the adjective explains the failure.",
              "too پیش از صفت دلیل ناکامی را می‌گوید."),
            q("Which sentence is correct?",
              ["He is strong enough to carry it.", "He is enough strong to carry it.",
               "He is strong to enough carry it."], "He is strong enough to carry it.",
              "Enough follows the adjective.",
              "enough پس از صفت می‌آید."),
        ],
    },
    {
        "section": "15-4",
        "title": "Passive infinitives and gerunds: present",
        "title_fa": "مصدر و اسم مصدر مجهول: زمان حال",
        "use_en": "When the person or thing in front of the verb receives the action rather than doing it, the infinitive becomes to be plus the past participle and the gerund becomes being plus the past participle: she expects to be promoted, he enjoys being praised. The active forms would say she expects to promote someone, which is a different sentence.",
        "use_fa": "وقتی شخص یا چیز پیش از فعل کار را می‌پذیرد نه انجام می‌دهد، مصدر to be و اسم مفعول می‌شود و اسم مصدر being و اسم مفعول: she expects to be promoted، he enjoys being praised. شکل‌های معلوم معنای دیگری می‌دهند: she expects to promote someone جملهٔ دیگری است.",
        "form_en": "passive infinitive: to be + past participle  ·  passive gerund: being + past participle",
        "examples": [
            {"en": "She expects to be promoted this year.",
             "fa": "انتظار دارد امسال ارتقا بگیرد."},
            {"en": "He enjoys being praised.",
             "fa": "از تعریف شدن لذت می‌برد."},
            {"en": "Nobody likes being ignored.",
             "fa": "هیچ‌کس دوست ندارد نادیده گرفته شود."},
        ],
        "exercises": [
            ex("The report needs to ___ finished today. (passive)", "be",
               "The passive infinitive is to be plus the participle.",
               "مصدر مجهول to be و اسم مفعول است."),
            ex("She hates ___ told what to do. (passive gerund)", "being",
               "The passive gerund begins with being.",
               "اسم مصدر مجهول با being آغاز می‌شود."),
            ex("They hope ___ invited to the wedding. (passive)", "to be",
               "Hope takes a passive infinitive here.",
               "hope اینجا مصدر مجهول می‌گیرد."),
        ],
        "exam": [
            q("The car needs to ___ washed.",
              ["be", "being", "been"], "be",
              "The passive infinitive is to be washed.",
              "مصدر مجهول to be washed است."),
            q("He doesn't like ___ interrupted.",
              ["being", "to be", "be"], "being",
              "After like, the passive gerund is being interrupted.",
              "پس از like اسم مصدر مجهول being interrupted است."),
            q("Which sentence is passive?",
              ["She wants to be informed.", "She wants to inform us.",
               "She wants informing."], "She wants to be informed.",
              "The subject receives the action, so the infinitive is passive.",
              "فاعل کار را می‌پذیرد، پس مصدر مجهول است."),
        ],
    },
    {
        "section": "15-5",
        "title": "Past forms of infinitives and gerunds",
        "title_fa": "شکل‌های گذشتهٔ مصدر و اسم مصدر",
        "use_en": "To have plus a past participle puts the infinitive before the main verb in time: he seems to have forgotten. Having plus a past participle does the same for the gerund: having finished the report, she went home. The passive versions are to have been done and having been done. These forms are common in writing and rare in speech, where a second clause is easier.",
        "use_fa": "to have و اسم مفعول، مصدر را در زمان پیش از فعل اصلی می‌گذارد: he seems to have forgotten. having و اسم مفعول همین کار را برای اسم مصدر می‌کند: having finished the report, she went home. شکل‌های مجهول to have been done و having been done هستند. این شکل‌ها در نوشتار رایج‌اند و در گفتار کم، جایی که جملهٔ دوم آسان‌تر است.",
        "form_en": "to have + past participle  ·  having + past participle  ·  to have been / having been + past participle",
        "examples": [
            {"en": "He seems to have forgotten our meeting.",
             "fa": "به نظر می‌رسد قرار ما را فراموش کرده است."},
            {"en": "Having finished the report, she went home.",
             "fa": "پس از تمام کردن گزارش به خانه رفت."},
            {"en": "The letter seems to have been opened.",
             "fa": "به نظر می‌رسد نامه باز شده است."},
        ],
        "exercises": [
            ex("She appears ___ lost her keys. (past infinitive)", "to have",
               "A past infinitive begins with to have.",
               "مصدر گذشته با to have آغاز می‌شود."),
            ex("___ eaten, we left the restaurant. (past gerund)", "Having",
               "The past gerund begins with having.",
               "اسم مصدر گذشته با having آغاز می‌شود."),
            ex("The window seems to have ___ broken. (passive past)", "been",
               "The passive past infinitive is to have been plus the participle.",
               "مصدر گذشتهٔ مجهول to have been و اسم مفعول است."),
        ],
        "exam": [
            q("He claims ___ the film before.",
              ["to have seen", "to see", "seeing"], "to have seen",
              "The seeing happened earlier, so the past infinitive is used.",
              "دیدن پیش‌تر رخ داده، پس مصدر گذشته می‌آید."),
            q("___ arrived early, we had time for coffee.",
              ["Having", "Have", "To have"], "Having",
              "The past gerund opens the phrase.",
              "اسم مصدر گذشته عبارت را باز می‌کند."),
            q("The package appears ___ damaged in transit.",
              ["to have been", "to be", "having been"], "to have been",
              "A past passive infinitive is to have been plus the participle.",
              "مصدر گذشتهٔ مجهول to have been و اسم مفعول است."),
        ],
    },
    {
        "section": "15-6",
        "title": "Need with a gerund or a passive infinitive",
        "title_fa": "need با اسم مصدر یا مصدر مجهول",
        "use_en": "Need followed by a gerund carries a passive meaning: the car needs washing means the car needs to be washed. Both forms are correct and the gerund is the shorter one. The same pattern works with want in British English and with a few other verbs, but need is the one learners meet most. Do not read the gerund as active: nobody is washing the car in that sentence.",
        "use_fa": "need به‌همراه اسم مصدر معنای مجهول دارد: the car needs washing یعنی the car needs to be washed. هر دو شکل درست‌اند و اسم مصدر کوتاه‌تر است. همین الگو با want در انگلیسی بریتانیایی و چند فعل دیگر کار می‌کند، اما need رایج‌ترین است. اسم مصدر را معلوم نخوانید: در آن جمله کسی ماشین را نمی‌شوید.",
        "form_en": "need + gerund (passive meaning)  ·  need + to be + past participle",
        "examples": [
            {"en": "The car needs washing.",
             "fa": "ماشین باید شسته شود."},
            {"en": "The car needs to be washed.",
             "fa": "ماشین باید شسته شود."},
            {"en": "These shoes need repairing.",
             "fa": "این کفش‌ها باید تعمیر شوند."},
        ],
        "exercises": [
            ex("The room needs ___ before the guests arrive. (clean, gerund)", "cleaning",
               "Need plus a gerund has a passive meaning.",
               "need با اسم مصدر معنای مجهول دارد."),
            ex("The form needs to ___ signed. (passive)", "be",
               "The passive infinitive after need is to be signed.",
               "مصدر مجهول پس از need همان to be signed است."),
            ex("My bike needs ___ . (repair, gerund)", "repairing",
               "The gerund after need means it must be repaired.",
               "اسم مصدر پس از need یعنی باید تعمیر شود."),
        ],
        "exam": [
            q("The garden needs ___.",
              ["watering", "to water", "water"], "watering",
              "Need plus a gerund means the garden must be watered.",
              "need با اسم مصدر یعنی باغ باید آبیاری شود."),
            q("The windows need to ___ cleaned.",
              ["be", "being", "been"], "be",
              "The passive infinitive is to be cleaned.",
              "مصدر مجهول to be cleaned است."),
            q("Which sentence means the same as the car needs washing?",
              ["The car needs to be washed.", "The car needs to wash.",
               "The car is washing."], "The car needs to be washed.",
              "Both forms describe the car receiving the action.",
              "هر دو شکل می‌گویند ماشین کار را می‌پذیرد."),
        ],
    },
    {
        "section": "15-7",
        "title": "Verbs of perception: see, hear, watch, feel",
        "title_fa": "فعل‌های ادراک: see، hear، watch، feel",
        "use_en": "See, hear, watch, feel, notice and observe can take a person and then either the base verb or the -ing form. The base verb reports the whole action from start to finish: I saw him cross the road. The -ing form reports a moment in the middle of it: I saw him crossing the road. The difference is not tense but how much of the action was seen.",
        "use_fa": "see، hear، watch، feel، notice و observe می‌توانند شخص و سپس فعل ساده یا شکل ing- بگیرند. فعل ساده تمام کار را از آغاز تا پایان گزارش می‌کند: I saw him cross the road. شکل ing- لحظه‌ای از میانهٔ کار را می‌گوید: I saw him crossing the road. تفاوت در زمان نیست، در این است که چه اندازه از کار دیده شد.",
        "form_en": "see / hear / watch + person + base verb (whole action)  ·  + -ing (in progress)",
        "examples": [
            {"en": "I saw him cross the road.",
             "fa": "دیدم که از خیابان گذشت."},
            {"en": "I saw him crossing the road.",
             "fa": "دیدم که داشت از خیابان می‌گذشت."},
            {"en": "We heard her singing in the next room.",
             "fa": "شنیدیم که در اتاق کناری آواز می‌خواند."},
        ],
        "exercises": [
            ex("I watched the children ___ in the garden. (play, in progress)", "playing",
               "The -ing form shows the action in progress.",
               "شکل ing- کار در حال انجام را نشان می‌دهد."),
            ex("She saw the man ___ the door and leave. (open, whole action)", "open",
               "The base verb reports the whole action.",
               "فعل ساده تمام کار را گزارش می‌کند."),
            ex("We heard someone ___ at the door. (knock, in progress)", "knocking",
               "A sound in progress takes the -ing form.",
               "صدای در حال انجام شکل ing- می‌گیرد."),
        ],
        "exam": [
            q("I saw her ___ the street and disappear.",
              ["cross", "crossing", "to cross"], "cross",
              "The whole action from start to finish takes the base verb.",
              "تمام کار از آغاز تا پایان فعل ساده می‌گیرد."),
            q("We watched the game ___ on television.",
              ["being played", "play", "to play"], "being played",
              "A passive action in progress takes being plus the participle.",
              "کار مجهول در حال انجام being و اسم مفعول می‌گیرد."),
            q("Which verb is not a verb of perception?",
              ["decide", "notice", "observe"], "decide",
              "Decide is not about seeing or hearing.",
              "decide دربارهٔ دیدن یا شنیدن نیست."),
        ],
    },
    {
        "section": "15-8",
        "title": "The simple form after let and help",
        "title_fa": "فعل ساده پس از let و help",
        "use_en": "Let takes a person and then the base verb with no to: let me go, let him try. Help works the same way and also accepts to, so both help me carry and help me to carry are correct, with the shorter form more common in speech. Neither verb takes -ing, and neither takes a past form in the second verb.",
        "use_fa": "let شخص و سپس فعل ساده بی to می‌گیرد: let me go، let him try. help همین‌گونه است و to را هم می‌پذیرد، پس هم help me carry و هم help me to carry درست است و شکل کوتاه‌تر در گفتار رایج‌تر. هیچ‌کدام ing- نمی‌گیرند و هیچ‌کدام فعل دوم را گذشته نمی‌کنند.",
        "form_en": "let + person + base verb  ·  help + person + (to) + base verb",
        "examples": [
            {"en": "Let me help you with that.",
             "fa": "بگذار در آن کار کمکت کنم."},
            {"en": "She helped me carry the boxes.",
             "fa": "کمکم کرد جعبه‌ها را ببرم."},
            {"en": "They let us use their kitchen.",
             "fa": "اجازه دادند از آشپزخانه‌شان استفاده کنیم."},
        ],
        "exercises": [
            ex("Let me ___ you the way. (show)", "show",
               "Let takes the base verb with no to.",
               "let فعل ساده بی to می‌گیرد."),
            ex("She helped us ___ the table. (set)", "set",
               "Help takes the base verb, with or without to.",
               "help فعل ساده با یا بی to می‌گیرد."),
            ex("They didn't let him ___ the room. (leave)", "leave",
               "The negative does not change the base form.",
               "منفی شکل ساده را تغییر نمی‌دهد."),
        ],
        "exam": [
            q("Let him ___ first.",
              ["speak", "to speak", "speaking"], "speak",
              "Let takes the base verb.",
              "let فعل ساده می‌گیرد."),
            q("Can you help me ___ this bag?",
              ["carry", "carrying", "carried"], "carry",
              "Help takes the base verb.",
              "help فعل ساده می‌گیرد."),
            q("Which sentence is correct?",
              ["She let me borrow her car.", "She let me to borrow her car.",
               "She let me borrowing her car."], "She let me borrow her car.",
              "No to and no -ing after let.",
              "پس از let نه to می‌آید نه ing-."),
        ],
    },
    {
        "section": "15-9",
        "title": "Causative verbs: make, have, get",
        "title_fa": "فعل‌های سببی: make، have، get",
        "use_en": "These verbs say that one person causes another to act, and each takes a different form. Make and have take the base verb: she made him apologise, I had the mechanic check the brakes. Get takes an infinitive: I got him to help. When the object receives the action instead of doing it, all three take a past participle: I had my hair cut, she got the window fixed.",
        "use_fa": "این فعل‌ها می‌گویند شخصی سبب می‌شود شخص دیگر کاری کند و هر یک شکلی متفاوت می‌گیرد. make و have فعل ساده می‌گیرند: she made him apologise، I had the mechanic check the brakes. get مصدر می‌گیرد: I got him to help. وقتی مفعول کار را می‌پذیرد نه انجام می‌دهد، هر سه اسم مفعول می‌گیرند: I had my hair cut، she got the window fixed.",
        "form_en": "make / have + person + base verb  ·  get + person + to + verb  ·  have / get + object + past participle",
        "examples": [
            {"en": "She made him apologise.",
             "fa": "او را وادار کرد عذرخواهی کند."},
            {"en": "I had the mechanic check the brakes.",
             "fa": "از مکانیک خواستم ترمزها را بررسی کند."},
            {"en": "I had my hair cut yesterday.",
             "fa": "دیروز موهایم را کوتاه کردم."},
        ],
        "exercises": [
            ex("The teacher made us ___ the poem. (learn)", "learn",
               "Make takes the base verb.",
               "make فعل ساده می‌گیرد."),
            ex("I got my brother ___ the shelf. (fix)", "to fix",
               "Get takes an infinitive.",
               "get مصدر می‌گیرد."),
            ex("She had her car ___ last week. (repair, passive)", "repaired",
               "A passive object after have takes the past participle.",
               "مفعول مجهول پس از have اسم مفعول می‌گیرد."),
        ],
        "exam": [
            q("They made him ___ the truth.",
              ["tell", "to tell", "telling"], "tell",
              "Make takes the base verb.",
              "make فعل ساده می‌گیرد."),
            q("We got the plumber ___ the leak.",
              ["to fix", "fix", "fixing"], "to fix",
              "Get takes an infinitive.",
              "get مصدر می‌گیرد."),
            q("I need to have my passport ___.",
              ["renewed", "renew", "to renew"], "renewed",
              "The passport receives the action, so the participle is used.",
              "پاسپورت کار را می‌پذیرد، پس اسم مفعول می‌آید."),
        ],
    },
    {
        "section": "15-10",
        "title": "A possessive before a gerund",
        "title_fa": "حالت مالکیت پیش از اسم مصدر",
        "use_en": "Because a gerund is a noun, the person doing it can be shown with a possessive: I don't like his smoking, would you mind my opening the window, we were surprised by their leaving early. In informal speech the object form often replaces it: I don't like him smoking. The possessive is the careful choice in writing, and it removes the ambiguity of who is doing what.",
        "use_fa": "چون اسم مصدر اسم است، انجام‌دهندهٔ آن می‌تواند با حالت مالکیت بیاید: I don't like his smoking، would you mind my opening the window، we were surprised by their leaving early. در گفتار غیررسمی شکل مفعولی جای آن را می‌گیرد: I don't like him smoking. حالت مالکیت در نوشتار انتخاب دقیق‌تر است و ابهام انجام‌دهنده را برمی‌دارد.",
        "form_en": "possessive + gerund  ·  his / her / my / their / our + -ing",
        "examples": [
            {"en": "I don't like his smoking in the kitchen.",
             "fa": "دوست ندارم او در آشپزخانه سیگار بکشد."},
            {"en": "Would you mind my opening the window?",
             "fa": "اشکالی ندارد اگر پنجره را باز کنم؟"},
            {"en": "We were surprised by their leaving early.",
             "fa": "از رفتن زودهنگام آن‌ها غافلگیر شدیم."},
        ],
        "exercises": [
            ex("Would you mind ___ closing the door? (I)", "my",
               "The doer of the gerund takes the possessive.",
               "انجام‌دهندهٔ اسم مصدر حالت مالکیت می‌گیرد."),
            ex("I was annoyed by ___ arriving late. (they)", "their",
               "Their marks who did the arriving.",
               "their نشان می‌دهد چه کسی رسید."),
            ex("She doesn't like ___ singing in the shower. (he)", "his",
               "The possessive his comes before the gerund.",
               "حالت مالکیت his پیش از اسم مصدر می‌آید."),
        ],
        "exam": [
            q("I appreciate ___ helping me.",
              ["your", "you", "yours"], "your",
              "The doer of the gerund takes the possessive.",
              "انجام‌دهندهٔ اسم مصدر حالت مالکیت می‌گیرد."),
            q("Would you mind ___ sitting here?",
              ["my", "me", "mine"], "my",
              "Careful writing uses the possessive before the gerund.",
              "نوشتار دقیق پیش از اسم مصدر حالت مالکیت می‌آورد."),
            q("Which sentence is the careful written form?",
              ["We objected to their smoking indoors.", "We objected to them smoking indoors.",
               "We objected to they smoking indoors."],
              "We objected to their smoking indoors.",
              "The possessive is the formal choice.",
              "حالت مالکیت انتخاب رسمی است."),
        ],
    },
]


def main() -> int:
    data = json.loads(BOOKS.read_text(encoding="utf-8"))
    book = next(b for b in data["books"] if b.get("kind") == "grammar")

    old = [l for l in book["lessons"] if l.get("chapter") == CHAPTER]
    assert old, "chapter fifteen is not in the book"

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
    print(f"chapter fifteen: {len(LESSONS)} charts, {size} structures in the book")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
