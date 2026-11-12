#!/usr/bin/env python3
"""Write chapter eleven of the grammar book into books.json.

    python3 tools/chapter11.py

Chapter eleven of *Understanding and Using English Grammar* is The Passive.
The book shipped with two placeholder sections for it; this replaces them with
the chapter's eight charts, written out like chapters three to ten: the rule, the
form, examples in both languages, three guided exercises and a three-question
check for each.

The sentences and explanations are written for this app. The book is the
reference text, and nothing in this file is transcribed from it.

It is idempotent: chapter eleven is always rebuilt from this script.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "books.json"

CHAPTER = "Chapter 11"


def ex(prompt, answer, why_en, why_fa):
    return {"prompt": prompt, "answer": answer, "why_en": why_en, "why_fa": why_fa}


def q(text, options, answer, why_en, why_fa):
    assert answer in options and len(options) == 3, text
    return {"q": text, "options": options, "answer": answer,
            "why_en": why_en, "why_fa": why_fa}


LESSONS = [
    {
        "section": "11-1",
        "title": "Active and passive: who does it and what happens",
        "title_fa": "معلوم و مجهول: چه کسی انجام می‌دهد و چه اتفاقی می‌افتد",
        "use_en": "The active sentence puts the doer first: the neighbour painted the fence. The passive sentence puts the receiver of the action first and moves the doer out of the way: the fence was painted. Both describe the same event; the choice says what the sentence is about. The doer can come back after by, but only when the reader needs to know who it was. The passive is not a more polite or more advanced active: it is a different starting point.",
        "use_fa": "جملهٔ معلوم انجام‌دهنده را اول می‌آورد: the neighbour painted the fence. جملهٔ مجهول گیرندهٔ کار را اول می‌آورد و انجام‌دهنده را کنار می‌گذارد: the fence was painted. هر دو یک رویداد را می‌گویند و انتخاب میان آن‌ها نشان می‌دهد جمله دربارهٔ چه چیزی است. انجام‌دهنده می‌تواند پس از by برگردد، اما تنها وقتی خواننده باید بداند کار را چه کسی کرد. مجهول مؤدبانه‌تر یا پیشرفته‌تر از معلوم نیست؛ نقطهٔ شروع دیگری است.",
        "form_en": "active: subject + verb + object  ·  passive: object + be + past participle (+ by + doer)",
        "examples": [
            {"en": "Someone broke the window last night.",
             "fa": "دیشب کسی پنجره را شکست."},
            {"en": "The window was broken last night.",
             "fa": "پنجره دیشب شکسته شد."},
            {"en": "The novel was written by a teacher from Tabriz.",
             "fa": "آن رمان را معلمی از تبریز نوشت."},
        ],
        "exercises": [
            ex("The chef cooked the meal. → The meal ___ cooked by the chef.", "was",
               "The passive of a past action takes was with the past participle.",
               "مجهولِ کار گذشته was و اسم مفعول می‌گیرد."),
            ex("Someone stole my bike. → My bike ___ stolen.", "was",
               "The passive keeps the tense of the active: past stays past.",
               "مجهول زمان جملهٔ معلوم را نگه می‌دارد: گذشته گذشته می‌ماند."),
            ex("The company employs two hundred people. → Two hundred people ___ employed.",
               "are",
               "A plural receiver takes are in the present passive.",
               "گیرندهٔ جمع در مجهول حال are می‌گیرد."),
        ],
        "exam": [
            q("Which sentence is passive?",
              ["The letter was sent yesterday.", "She sent the letter yesterday.",
               "She is sending the letter."], "The letter was sent yesterday.",
              "The receiver leads and the verb is be plus the past participle.",
              "گیرنده اول آمده و فعل be و اسم مفعول است."),
            q("The bridge ___ in 1998.",
              ["was built", "built", "was building"], "was built",
              "A finished past action on the receiver is was built.",
              "کار گذشتهٔ تمام‌شده روی گیرنده was built است."),
            q("Which passive keeps the doer because the doer matters?",
              ["The song was written by a student.", "The song was written last year.",
               "The song was written quickly."], "The song was written by a student.",
              "Only by plus a person answers the question of who did it.",
              "تنها by به‌همراه شخص پاسخ می‌دهد که کار را چه کسی کرد."),
        ],
    },
    {
        "section": "11-2",
        "title": "The tense forms of the passive: be + past participle",
        "title_fa": "زمان‌های مجهول: be + اسم مفعول",
        "use_en": "In the passive the tense lives in be and the past participle never changes: is cleaned, was cleaned, is being cleaned, has been cleaned, will be cleaned. Once the pattern is clear, every tense you already know carries over without a new form to learn. The perfect progressive passive is so heavy that English avoids it and rewrites the sentence instead.",
        "use_fa": "در مجهول، زمان در be زندگی می‌کند و اسم مفعول هرگز تغییر نمی‌کند: is cleaned، was cleaned، is being cleaned، has been cleaned، will be cleaned. وقتی الگو روشن شود، هر زمانی که می‌دانید بدون شکل تازه‌ای منتقل می‌شود. مجهولِ کامل استمراری چنان سنگین است که انگلیسی از آن پرهیز می‌کند و جمله را بازنویسی می‌کند.",
        "form_en": "present is/are + pp · past was/were + pp · progressive is being + pp · perfect has been + pp · future will be + pp",
        "examples": [
            {"en": "The office is cleaned every evening.",
             "fa": "دفتر هر عصر تمیز می‌شود."},
            {"en": "The road was being repaired when we drove past.",
             "fa": "وقتی از آنجا گذشتیم جاده در دست تعمیر بود."},
            {"en": "The results have been announced.",
             "fa": "نتایج اعلام شده‌اند."},
        ],
        "exercises": [
            ex("The forms ___ (send) last week.", "were sent",
               "A plural receiver in the past takes were plus the participle.",
               "گیرندهٔ جمع در گذشته were و اسم مفعول می‌گیرد."),
            ex("The bridge ___ (repair) at the moment.", "is being repaired",
               "An action in progress now is is being plus the participle.",
               "کار در حال انجام اکنون is being و اسم مفعول است."),
            ex("The new library ___ (open) next month.", "will be opened",
               "A future passive is will be plus the participle.",
               "مجهول آینده will be و اسم مفعول است."),
        ],
        "exam": [
            q("The room ___ every morning.",
              ["is cleaned", "cleans", "is cleaning"], "is cleaned",
              "A daily routine on the room is the present passive.",
              "روتین روزانه روی اتاق مجهول حال است."),
            q("The letter ___ yesterday.",
              ["was sent", "sent", "is sent"], "was sent",
              "Yesterday puts the passive in the past.",
              "yesterday مجهول را به گذشته می‌برد."),
            q("The work ___ by Friday.",
              ["will be finished", "will finish", "finishes"], "will be finished",
              "The future passive is will be finished.",
              "مجهول آینده will be finished است."),
        ],
    },
    {
        "section": "11-3",
        "title": "Using the passive: when the doer does not matter",
        "title_fa": "کاربرد مجهول: وقتی انجام‌دهنده مهم نیست",
        "use_en": "English chooses the passive for four reasons: the doer is unknown, the doer is obvious, the doer is unimportant, or the receiver is the topic the paragraph is following. News reports, instructions and scientific writing use it for the same reasons. Outside those four cases the active is shorter and clearer, and a passive that hides a doer the reader needs is a weakness rather than a style.",
        "use_fa": "انگلیسی مجهول را به چهار دلیل انتخاب می‌کند: انجام‌دهنده ناشناس است، آشکار است، بی‌اهمیت است، یا گیرنده موضوعِ پاراگراف است. گزارش خبری، دستور کار و نوشتار علمی به همین دلیل‌ها از آن استفاده می‌کنند. بیرون از این چهار حالت، معلوم کوتاه‌تر و روشن‌تر است و مجهولی که انجام‌دهندهٔ لازم را پنهان کند ضعف است نه سبک.",
        "form_en": "passive for: unknown doer · obvious doer · unimportant doer · receiver as topic",
        "examples": [
            {"en": "My wallet was stolen on the bus.",
             "fa": "کیف پولم در اتوبوس دزدیده شد."},
            {"en": "English is spoken in many countries.",
             "fa": "انگلیسی در بسیاری از کشورها صحبت می‌شود."},
            {"en": "The building was designed in 1930.",
             "fa": "ساختمان در سال ۱۹۳۰ طراحی شد."},
        ],
        "exercises": [
            ex("The doer is unknown: someone has taken my umbrella. → My umbrella ___ been taken.",
               "has",
               "An unknown doer leaves the passive without by.",
               "انجام‌دهندهٔ ناشناس مجهول را بی by می‌گذارد."),
            ex("The doer is obvious: the postman delivers the mail. → The mail ___ delivered every day.",
               "is",
               "When everyone knows the doer, the passive drops it.",
               "وقتی همه انجام‌دهنده را می‌دانند، مجهول او را حذف می‌کند."),
            ex("Keep the doer: the storm destroyed the roof. → The roof was destroyed ___ the storm.",
               "by",
               "By introduces the doer when it still matters.",
               "by انجام‌دهنده را وقتی هنوز مهم است معرفی می‌کند."),
        ],
        "exam": [
            q("Which passive is right when the doer is unknown?",
              ["My phone was stolen.", "Someone stole my phone.", "My phone stole."],
              "My phone was stolen.",
              "No doer is known, so the passive leaves it out.",
              "انجام‌دهنده شناخته نیست، پس مجهول او را حذف می‌کند."),
            q("Which sentence hides a doer the reader needs?",
              ["The report was written.", "The report was written by Sara.",
               "Sara wrote the report."], "The report was written.",
              "The reader needs to know who wrote it, and the passive hides it.",
              "خواننده باید بداند چه کسی نوشت و مجهول آن را پنهان می‌کند."),
            q("Why do instructions use the passive? — The form must be signed.",
              ["The doer is obvious.", "The doer is unknown.",
               "The action is in the past."], "The doer is obvious.",
              "Anyone filling the form signs it, so the doer adds nothing.",
              "هر کسی فرم را پر کند امضا می‌کند، پس انجام‌دهنده چیزی نمی‌افزاید."),
        ],
    },
    {
        "section": "11-4",
        "title": "The passive with modals and phrasal modals",
        "title_fa": "مجهول با افعال وجهی و وجهی‌های عبارتی",
        "use_en": "A modal keeps its shape and be follows it: the report must be finished. Phrasal modals keep their own endings and their own to: has to be finished, is going to be finished, ought to be finished. A modal in the past takes the perfect passive, should have been finished, and the pattern holds for every modal in chapter ten.",
        "use_fa": "فعل وجهی شکل خود را نگه می‌دارد و be پس از آن می‌آید: the report must be finished. وجهی‌های عبارتی پایانه‌ها و to خود را نگه می‌دارند: has to be finished، is going to be finished، ought to be finished. وجهی در گذشته مجهول کامل می‌گیرد، should have been finished، و این الگو برای هر وجهی فصل ده برقرار است.",
        "form_en": "modal + be + past participle  ·  have to / be going to + be + pp  ·  should have been + pp",
        "examples": [
            {"en": "The report must be finished today.",
             "fa": "گزارش باید امروز تمام شود."},
            {"en": "The rules have to be followed by everyone.",
             "fa": "قوانین باید از سوی همه رعایت شوند."},
            {"en": "The keys should have been returned to the desk.",
             "fa": "کلیدها باید به پذیرش برگردانده می‌شدند."},
        ],
        "exercises": [
            ex("The door ___ be locked at night. (must)", "must",
               "The modal comes first and be follows it.",
               "وجهی اول می‌آید و be پس از آن."),
            ex("The forms have to ___ signed by Friday.", "be",
               "Have to keeps its own to and be follows.",
               "have to خودِ to را نگه می‌دارد و be پس از آن می‌آید."),
            ex("The email should have ___ sent yesterday.", "been",
               "The perfect passive of a modal is have been plus the participle.",
               "مجهول کامل وجهی have been و اسم مفعول است."),
        ],
        "exam": [
            q("The package ___ delivered tomorrow.",
              ["will be", "will", "is"], "will be",
              "A future passive is will be plus the participle.",
              "مجهول آینده will be و اسم مفعول است."),
            q("The bill ___ paid before we leave.",
              ["has to be", "has to", "have to"], "has to be",
              "Have to is a phrasal modal, so be still follows.",
              "have to وجهی عبارتی است، پس be باز هم می‌آید."),
            q("The window ___ repaired last week.",
              ["should have been", "should be", "should have"], "should have been",
              "A missed past obligation takes the perfect passive.",
              "وظیفهٔ گذشتهٔ انجام‌نشده مجهول کامل می‌گیرد."),
        ],
    },
    {
        "section": "11-5",
        "title": "The stative passive: be + participle as a description",
        "title_fa": "مجهول حالتی: be + اسم مفعول به‌عنوان توصیف",
        "use_en": "Not every be plus participle reports an action. In the shop is closed the participle describes a state, like an adjective, and no one is closing anything at that moment. The same words with by and an agent describe an event: the shop was closed by the manager at six. Stative passives usually take a fixed preposition, and the pair is learned as one item: interested in, married to, covered with.",
        "use_fa": "هر be به‌همراه اسم مفعول رویداد را گزارش نمی‌کند. در the shop is closed اسم مفعول حالتی را مانند صفت توصیف می‌کند و در آن لحظه کسی چیزی را نمی‌بندد. همین واژه‌ها با by و انجام‌دهنده رویداد را می‌گویند: the shop was closed by the manager at six. مجهول حالتی معمولاً حرف اضافهٔ ثابتی می‌گیرد و این جفت یک واحد آموخته می‌شود: interested in، married to، covered with.",
        "form_en": "subject + be + past participle (a state)  ·  often + a fixed preposition",
        "examples": [
            {"en": "The shop is closed on Sundays.",
             "fa": "فروشگاه یکشنبه‌ها بسته است."},
            {"en": "We are worried about the exam.",
             "fa": "ما نگران امتحان هستیم."},
            {"en": "The table was covered with papers.",
             "fa": "میز پوشیده از کاغذ بود."},
        ],
        "exercises": [
            ex("The window ___ broken, so we need a new one.", "is",
               "A state now takes the present of be.",
               "حالت اکنون حالِ be را می‌گیرد."),
            ex("She is married ___ an engineer.", "to",
               "Married to is a fixed pair.",
               "married to جفتی ثابت است."),
            ex("I am interested ___ history.", "in",
               "Interested in is a fixed pair.",
               "interested in جفتی ثابت است."),
        ],
        "exam": [
            q("Which sentence describes a state, not an action?",
              ["The door is locked.", "The guard locked the door.",
               "The guard is locking the door."], "The door is locked.",
              "No one is doing anything; the participle describes the door.",
              "کسی کاری نمی‌کند؛ اسم مفعول در را توصیف می‌کند."),
            q("The children were ___ in the game.",
              ["interested", "interesting", "interest"], "interested",
              "People feel interested; the game is interesting.",
              "افراد interested حس می‌کنند و بازی interesting است."),
            q("The room was filled ___ smoke.",
              ["with", "of", "by"], "with",
              "Filled with is the fixed pair.",
              "filled with جفت ثابت است."),
        ],
    },
    {
        "section": "11-6",
        "title": "Common stative passive verbs with prepositions",
        "title_fa": "مجهول‌های حالتی رایج با حرف اضافه",
        "use_en": "A small set of participles lives with one preposition and means something different from the verb alone: be accustomed to, be addicted to, be acquainted with, be composed of, be devoted to, be engaged in, be equipped with, be exposed to, be filled with, be involved in, be made of or from, be prepared for, be related to, be satisfied with, be scared of, be tired of. Learn the participle and the preposition together, because the preposition cannot be guessed.",
        "use_fa": "مجموعهٔ کوچکی از اسم‌های مفعول با یک حرف اضافه زندگی می‌کنند و معنایی متفاوت از فعل تنها دارند: be accustomed to، be addicted to، be acquainted with، be composed of، be devoted to، be engaged in، be equipped with، be exposed to، be filled with، be involved in، be made of یا from، be prepared for، be related to، be satisfied with، be scared of، be tired of. اسم مفعول و حرف اضافه را با هم بیاموزید، چون حرف اضافه حدس‌زدنی نیست.",
        "form_en": "be + participle + fixed preposition (one item, learned together)",
        "examples": [
            {"en": "The team is composed of eleven players.",
             "fa": "تیم از یازده بازیکن تشکیل شده است."},
            {"en": "The room was filled with smoke.",
             "fa": "اتاق پر از دود بود."},
            {"en": "I am tired of waiting for an answer.",
             "fa": "از انتظار برای پاسخ خسته شده‌ام."},
        ],
        "exercises": [
            ex("The cake is made ___ flour, eggs and sugar.", "from",
               "Made from names the material that has been changed.",
               "made from ماده‌ای را می‌گوید که تغییر کرده است."),
            ex("She is satisfied ___ her results.", "with",
               "Satisfied with is the fixed pair.",
               "satisfied with جفت ثابت است."),
            ex("He is accustomed ___ working nights.", "to",
               "Accustomed to is the fixed pair.",
               "accustomed to جفت ثابت است."),
        ],
        "exam": [
            q("The desk is made ___ wood.",
              ["of", "from", "with"], "of",
              "Made of names the material you can still see.",
              "made of ماده‌ای را می‌گوید که هنوز دیده می‌شود."),
            q("She was scared ___ the dark.",
              ["of", "from", "to"], "of",
              "Scared of is the fixed pair.",
              "scared of جفت ثابت است."),
            q("Everyone was involved ___ the project.",
              ["in", "with", "at"], "in",
              "Involved in is the fixed pair.",
              "involved in جفت ثابت است."),
        ],
    },
    {
        "section": "11-7",
        "title": "The passive with get",
        "title_fa": "مجهول با get",
        "use_en": "Get plus a past participle reports a change of state, and it belongs to speech rather than to reports: he got fired, we got lost, she got hurt, they got married. It carries the idea of becoming, which be does not. It is not used for a state that simply is, and it is out of place in formal writing, where be is the safer choice.",
        "use_fa": "get به‌همراه اسم مفعول تغییر حالت را می‌گوید و به گفتار تعلق دارد نه به گزارش رسمی: he got fired، we got lost، she got hurt، they got married. ایدهٔ «شدن» را دارد که be ندارد. برای حالتی که فقط هست به کار نمی‌رود و در نوشتار رسمی جایی ندارد، جایی که be انتخاب مطمئن‌تر است.",
        "form_en": "get + past participle (a change of state, informal)",
        "examples": [
            {"en": "He got fired last month.",
             "fa": "ماه گذشته اخراج شد."},
            {"en": "We got lost on the way to the village.",
             "fa": "در راه روستا گم شدیم."},
            {"en": "She got her hair cut before the wedding.",
             "fa": "پیش از عروسی موهایش را کوتاه کرد."},
        ],
        "exercises": [
            ex("My phone ___ stolen at the market yesterday.", "got",
               "A change of state in speech takes got.",
               "تغییر حالت در گفتار got می‌گیرد."),
            ex("They ___ married in June.", "got",
               "Married with get reports the change, not the state.",
               "married با get تغییر را می‌گوید نه حالت را."),
            ex("He ___ hurt during the match.", "got",
               "An injury that happened is got hurt in speech.",
               "آسیبی که رخ داد در گفتار got hurt است."),
        ],
        "exam": [
            q("Which sentence is informal speech?",
              ["She got promoted.", "She was promoted.",
               "She is promoted."], "She got promoted.",
              "Get plus participle belongs to speech.",
              "get و اسم مفعول به گفتار تعلق دارد."),
            q("The lights ___ turned off at ten.",
              ["get", "gets", "getting"], "get",
              "A plural subject takes get without -s.",
              "فاعل جمع get می‌گیرد بی s."),
            q("Where is get plus a participle out of place?",
              ["In a formal report", "In a conversation", "In a text message"],
              "In a formal report",
              "Formal writing prefers be plus the participle.",
              "نوشتار رسمی be و اسم مفعول را ترجیح می‌دهد."),
        ],
    },
    {
        "section": "11-8",
        "title": "Participial adjectives: -ed and -ing",
        "title_fa": "صفت‌های اسم مفعولی: ed- و ing-",
        "use_en": "The two endings do different jobs. The -ed form says how a person feels: I was bored. The -ing form says what caused the feeling: the lesson was boring. The same pair runs through interested and interesting, tired and tiring, excited and exciting, confused and confusing, embarrassed and embarrassing, disappointed and disappointing. A thing is almost never bored; a person is almost never boring by accident.",
        "use_fa": "این دو پایانه دو کار متفاوت می‌کنند. شکل ed- می‌گوید شخص چه حسی داشت: I was bored. شکل ing- می‌گوید چه چیزی آن حس را ساخت: the lesson was boring. همین جفت در interested و interesting، tired و tiring، excited و exciting، confused و confusing، embarrassed و embarrassing، disappointed و disappointing تکرار می‌شود. یک چیز تقریباً هرگز bored نیست و یک شخص تقریباً هرگز به‌طور تصادفی boring نیست.",
        "form_en": "-ed adjective: how someone feels  ·  -ing adjective: what causes the feeling",
        "examples": [
            {"en": "The lesson was boring, so the students were bored.",
             "fa": "درس خسته‌کننده بود، پس دانش‌آموزان خسته شدند."},
            {"en": "The news was surprising.",
             "fa": "آن خبر غافلگیرکننده بود."},
            {"en": "I was surprised by the news.",
             "fa": "از آن خبر غافلگیر شدم."},
        ],
        "exercises": [
            ex("The film was ___ (bore), so we left early.", "boring",
               "The film causes the feeling, so it takes -ing.",
               "فیلم حس را می‌سازد، پس ing- می‌گیرد."),
            ex("We were ___ (tire) after the long trip.", "tired",
               "The people feel it, so they take -ed.",
               "افراد حس را دارند، پس ed- می‌گیرند."),
            ex("His answer was ___ (confuse).", "confusing",
               "The answer causes the confusion, so it takes -ing.",
               "پاسخ سردرگمی را می‌سازد، پس ing- می‌گیرد."),
        ],
        "exam": [
            q("The children were ___ by the noise.",
              ["frightened", "frightening", "frighten"], "frightened",
              "The children feel it, so -ed.",
              "کودکان حس را دارند، پس ed-."),
            q("The results were ___.",
              ["disappointing", "disappointed", "disappoint"], "disappointing",
              "The results cause the feeling, so -ing.",
              "نتایج حس را می‌سازند، پس ing-."),
            q("Which sentence is correct?",
              ["I am interested in music.", "I am interesting in music.",
               "Music is interested."], "I am interested in music.",
              "A person feels interested; music is interesting.",
              "شخص interested حس می‌کند و موسیقی interesting است."),
        ],
    },
]


def main() -> int:
    data = json.loads(BOOKS.read_text(encoding="utf-8"))
    book = next(b for b in data["books"] if b.get("kind") == "grammar")

    old = [l for l in book["lessons"] if l.get("chapter") == CHAPTER]
    assert old, "chapter eleven is not in the book"

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
    print(f"chapter eleven: {len(LESSONS)} charts, {size} structures in the book")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
