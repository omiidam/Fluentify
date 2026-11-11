#!/usr/bin/env python3
"""Write chapter nine of the grammar book into books.json.

    python3 tools/chapter9.py

Chapter nine of *Understanding and Using English Grammar* is Modals, Part 1.
The book shipped with three sections for it; this replaces them with the
chapter's ten charts, written out like chapters one to eight: the rule, the
form, examples in both languages, three guided exercises and a three-question
check for each.

The sentences and explanations are written for this app. The book is the
reference text, and nothing in this file is transcribed from it.

It is idempotent: chapter nine is always rebuilt from this script.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "books.json"

CHAPTER = "Chapter 9"


def ex(prompt, answer, why_en, why_fa):
    return {"prompt": prompt, "answer": answer, "why_en": why_en, "why_fa": why_fa}


def q(text, options, answer, why_en, why_fa):
    assert answer in options and len(options) == 3, text
    return {"q": text, "options": options, "answer": answer,
            "why_en": why_en, "why_fa": why_fa}


LESSONS = [
    {
        "section": "9-1",
        "title": "What a modal verb is",
        "title_fa": "فعل وجهی چیست",
        "use_en": "A modal is a helping verb that adds a meaning such as ability, permission or advice to the main verb. It comes first, it takes no -s in the third person, and the verb after it stays in the base form: she can swim, never she cans swims. Questions and negatives are built without do or does, so the modal itself moves or takes not.",
        "use_fa": "فعل وجهی فعل کمکی‌ای است که معنایی مانند توانایی، اجازه یا توصیه را به فعل اصلی می‌افزاید. اول می‌آید، در سوم‌شخص -s نمی‌گیرد و فعل پس از آن به شکل ساده می‌ماند: she can swim و هرگز she cans swims. پرسش و منفی بدون do و does ساخته می‌شود، پس خودِ فعل وجهی جابه‌جا می‌شود یا not می‌گیرد.",
        "form_en": "subject + modal + base verb  ·  no -s and no do/does  ·  negative: modal + not",
        "examples": [
            {"en": "She can swim very well for her age.",
             "fa": "او برای سنش خیلی خوب شنا می‌کند."},
            {"en": "You must not smoke inside the building.",
             "fa": "نباید داخل ساختمان سیگار بکشی."},
            {"en": "Could you close the door, please?",
             "fa": "می‌شود لطفاً در را ببندی؟"},
        ],
        "exercises": [
            ex("He ___ (can) speak three languages.", "can",
               "The modal never takes -s, whatever the subject is.",
               "فعل وجهی هر چه فاعل باشد -s نمی‌گیرد."),
            ex("___ you help me with this box?", "Can",
               "A question is made by moving the modal, with no do.",
               "پرسش با جابه‌جایی فعل وجهی ساخته می‌شود، بدون do."),
            ex("We ___ not park here; it is a bus stop.", "must",
               "The negative is the modal plus not, not do not must.",
               "منفی همان فعل وجهی به‌همراه not است، نه do not must."),
        ],
        "exam": [
            q("She ___ play the piano beautifully.",
              ["can", "cans", "can to"], "can",
              "A modal takes no -s, and the next verb has no to.",
              "فعل وجهی -s نمی‌گیرد و فعل بعد از آن to ندارد."),
            q("___ I use your phone for a minute?",
              ["May", "Do may", "Am may"], "May",
              "A question moves the modal to the front, with no do.",
              "پرسش فعل وجهی را به ابتدا می‌برد، بدون do."),
            q("They ___ to wait for the next bus.",
              ["have", "must", "can"], "have",
              "Must and can take no to, so have is the form that fits.",
              "must و can پس از خود to نمی‌پذیرند، پس have درست است."),
        ],
    },
    {
        "section": "9-2",
        "title": "Necessity: must, have to, have got to",
        "title_fa": "ضرورت: must، have to، have got to",
        "use_en": "Must and have to both say that something is necessary. Must carries the speaker's own strong feeling or a rule the speaker is laying down, while have to reports a rule that comes from somewhere else, and it changes with the subject: she has to. Have got to is the spoken form of have to. Must has no past or future, so had to and will have to do that work.",
        "use_fa": "must و have to هر دو می‌گویند کاری لازم است. must حس شدید خودِ گوینده یا قاعده‌ای را می‌رساند که گوینده تعیین می‌کند، در حالی که have to قاعده‌ای را بازگو می‌کند که از جای دیگری آمده و با فاعل تغییر می‌کند: she has to. have got to شکل گفتاری have to است. must گذشته و آینده ندارد، پس had to و will have to آن کار را می‌کنند.",
        "form_en": "must + base verb  ·  have / has to + base verb  ·  have got to + base verb",
        "examples": [
            {"en": "I must finish this report before I leave tonight.",
             "fa": "باید این گزارش را پیش از رفتن امشب تمام کنم."},
            {"en": "She has to wear a uniform at work.",
             "fa": "او باید سر کار لباس فرم بپوشد."},
            {"en": "We have got to hurry, or we will miss the train.",
             "fa": "باید عجله کنیم وگرنه قطار را از دست می‌دهیم."},
        ],
        "exercises": [
            ex("The train leaves at six, so we ___ to get up early.", "have",
               "Have to agrees with we and keeps its base form.",
               "have to با we هم‌خوان است و شکل ساده می‌ماند."),
            ex("My sister ___ to work on Saturdays.", "has",
               "A third-person singular subject takes has to.",
               "فاعل سوم‌شخص مفرد has to می‌گیرد."),
            ex("You ___ show your passport at the desk; it is the rule.", "must",
               "A rule stated by the speaker is natural with must.",
               "قاعده‌ای که گوینده بیان می‌کند با must طبیعی است."),
        ],
        "exam": [
            q("Everyone ___ follow the safety rules in the factory.",
              ["must", "musts", "must to"], "must",
              "Must never takes -s or to.",
              "must هرگز -s یا to نمی‌گیرد."),
            q("Sara ___ to leave early today.",
              ["has", "have", "must"], "has",
              "The subject is third-person singular, so has to.",
              "فاعل سوم‌شخص مفرد است، پس has to."),
            q("I ___ got to call my mother tonight.",
              ["have", "has", "must"], "have",
              "Have got to follows the subject I in the base form.",
              "have got to پس از فاعل I به شکل ساده می‌آید."),
        ],
    },
    {
        "section": "9-3",
        "title": "Not necessary and forbidden: do not have to, must not",
        "title_fa": "لازم نبودن و ممنوع بودن: do not have to و must not",
        "use_en": "Do not have to says that something is not necessary: you may do it, but nobody requires it. Must not says it is forbidden, and cannot does the same in rules. The difference decides the sentence: you do not have to pay is good news, you must not pay is a prohibition. Need not is the formal twin of do not have to and appears mostly in writing.",
        "use_fa": "do not have to می‌گوید کاری لازم نیست: می‌توانی انجام دهی، اما کسی مجبورت نمی‌کند. must not می‌گوید کار ممنوع است و cannot نیز در قاعده‌ها همین کار را می‌کند. این تفاوت معنای جمله را می‌سازد: you do not have to pay خبر خوب است و you must not pay ممنوعیت. need not معادل رسمی do not have to است و بیشتر در نوشتار دیده می‌شود.",
        "form_en": "do / does not have to + base verb (not necessary)  ·  must not + base verb (forbidden)",
        "examples": [
            {"en": "You do not have to bring anything; dinner is ready.",
             "fa": "لازم نیست چیزی بیاوری؛ شام آماده است."},
            {"en": "Passengers must not smoke anywhere on board.",
             "fa": "مسافران نباید هیچ‌جای هواپیما سیگار بکشند."},
            {"en": "She does not have to cook tonight, because we are eating out.",
             "fa": "او امشب لازم نیست آشپزی کند، چون بیرون غذا می‌خوریم."},
        ],
        "exercises": [
            ex("It is a holiday, so we ___ have to work.", "do not",
               "There is no necessity, so do not have to.",
               "ضرورتی نیست، پس do not have to."),
            ex("Visitors ___ not enter the laboratory without permission.", "must",
               "Entry is forbidden, which is must not.",
               "ورود ممنوع است و این must not می‌شود."),
            ex("He ___ have to wear a tie on Fridays.", "does not",
               "The third-person singular negative is does not have to.",
               "منفی سوم‌شخص مفرد does not have to است."),
        ],
        "exam": [
            q("The museum is free, so you ___ pay.",
              ["do not have to", "must not", "cannot"], "do not have to",
              "Paying is not required, which is not the same as forbidden.",
              "پرداخت لازم نیست و این با ممنوع بودن یکی نیست."),
            q("Staff ___ use the back door during the exam.",
              ["must not", "do not have to", "need not"], "must not",
              "The rule forbids the door, so must not.",
              "قاعده استفاده از آن در را ممنوع می‌کند، پس must not."),
            q("We ___ hurry; the film starts at nine.",
              ["do not have to", "must not", "cannot"], "do not have to",
              "There is still time, so there is no necessity.",
              "هنوز وقت هست، پس ضرورتی نیست."),
        ],
    },
    {
        "section": "9-4",
        "title": "Advice: should, ought to, had better, could",
        "title_fa": "توصیه: should، ought to، had better، could",
        "use_en": "Should and ought to give advice: they name the right thing to do without making it a rule. Had better is stronger and carries a warning that something will go wrong if the advice is ignored. Could is the softest of the four and offers an option rather than a duty. After ought to and had better the verb keeps its base form, and had is never past here.",
        "use_fa": "should و ought to توصیه می‌دهند: کار درست را می‌گویند بدون آنکه آن را قاعده کنند. had better قوی‌تر است و هشداری دارد که اگر توصیه نادیده گرفته شود چیزی بد پیش می‌آید. could از همه نرم‌تر است و به‌جای وظیفه یک گزینه پیشنهاد می‌کند. پس از ought to و had better فعل شکل ساده می‌ماند و had در اینجا گذشته نیست.",
        "form_en": "should / ought to / had better / could + base verb",
        "examples": [
            {"en": "You should see a doctor about that cough.",
             "fa": "برای آن سرفه بهتر است به پزشک مراجعه کنی."},
            {"en": "You had better take a jacket; it is cold outside.",
             "fa": "بهتر است کاپشنی برداری؛ بیرون سرد است."},
            {"en": "We could take the earlier train if you prefer.",
             "fa": "اگر ترجیح می‌دهی می‌توانیم قطار زودتر را بگیریم."},
        ],
        "exercises": [
            ex("You look tired. You ___ get some sleep.", "should",
               "A piece of friendly advice takes should.",
               "توصیهٔ دوستانه should می‌گیرد."),
            ex("You ___ better lock the door before you leave.", "had",
               "Had better warns that leaving it unlocked is a risk.",
               "had better هشدار می‌دهد که باز گذاشتن در خطرناک است."),
            ex("We ___ to book the tickets today, or the price will rise.", "ought",
               "Ought to is the advice form that needs to.",
               "ought to شکل توصیه‌ای است که to لازم دارد."),
        ],
        "exam": [
            q("You ___ to apologise to her.",
              ["ought", "should", "had"], "ought",
              "Ought is the form that takes to.",
              "ought شکلی است که to می‌گیرد."),
            q("It is raining. You ___ better take an umbrella.",
              ["had", "would", "must"], "had",
              "Had better is the fixed advice phrase.",
              "had better عبارت ثابت توصیه است."),
            q("You ___ try the soup; it is very good.",
              ["should", "must", "have to"], "should",
              "A suggestion rather than an obligation takes should.",
              "پیشنهاد به‌جای اجبار should می‌گیرد."),
        ],
    },
    {
        "section": "9-5",
        "title": "Expectation: be supposed to and should",
        "title_fa": "انتظار: be supposed to و should",
        "use_en": "Be supposed to reports what other people expect or what was arranged, and it often hints that the expectation is not being met: the train is supposed to arrive at six. Should says the same thing more gently and also predicts that something is likely. In the past, was supposed to usually means the thing did not happen at all.",
        "use_fa": "be supposed to آنچه دیگران انتظار دارند یا قرار گذاشته شده را بازگو می‌کند و اغلب اشاره دارد که انتظار برآورده نمی‌شود: the train is supposed to arrive at six. should همین را نرم‌تر می‌گوید و همچنین پیش‌بینی می‌کند چیزی احتمالاً درست است. در گذشته، was supposed to معمولاً یعنی آن کار هرگز انجام نشد.",
        "form_en": "am / is / are supposed to + base verb  ·  should + base verb",
        "examples": [
            {"en": "The train is supposed to arrive at six, but it is late.",
             "fa": "قرار است قطار ساعت شش برسد، اما تأخیر دارد."},
            {"en": "You are supposed to sign the form at the bottom.",
             "fa": "قرار است فرم را پایین آن امضا کنی."},
            {"en": "She should be at the office by now.",
             "fa": "او باید تا حالا در دفتر باشد."},
        ],
        "exercises": [
            ex("We ___ supposed to hand in the report on Monday.", "are",
               "The plural subject we takes are supposed to.",
               "فاعل جمع we با are supposed to می‌آید."),
            ex("He ___ to call me, but he never did.", "was",
               "The past form reports an arrangement that failed.",
               "شکل گذشته قرار است که انجام نشده را گزارش می‌کند."),
            ex("The shop ___ be open until nine tonight.", "should",
               "Should expresses a likely expectation about tonight.",
               "should انتظاری احتمالی دربارهٔ امشب را بیان می‌کند."),
        ],
        "exam": [
            q("Passengers ___ supposed to keep their seats during take-off.",
              ["are", "is", "be"], "are",
              "The plural passengers take are.",
              "passengers جمع است و are می‌گیرد."),
            q("This medicine ___ be taken after meals.",
              ["is supposed to", "supposes to", "supposed to"], "is supposed to",
              "The passive needs the be of be supposed to.",
              "ساخت مجهول به be در be supposed to نیاز دارد."),
            q("The meeting ___ to start at ten.",
              ["is supposed", "supposes", "is suppose"], "is supposed",
              "Supposed is the fixed participle after be.",
              "supposed شکل ثابت پس از be است."),
        ],
    },
    {
        "section": "9-6",
        "title": "Ability: can, know how to, be able to",
        "title_fa": "توانایی: can، know how to، be able to",
        "use_en": "Can says that someone is able to do something, and know how to says the skill was learned rather than merely possible. Be able to does the same work where can cannot go: after will, after another modal, and in the perfect. Can has no infinitive and no -ing form, so the phrase to be able to stands in for it.",
        "use_fa": "can می‌گوید کسی توان انجام کاری را دارد و know how to می‌گوید مهارت آموخته شده است، نه فقط ممکن. be able to همان کار را جایی می‌کند که can نمی‌تواند بیاید: پس از will، پس از فعل وجهی دیگر و در زمان کامل. can مصدر و شکل -ing ندارد، پس عبارت to be able to جای آن می‌آید.",
        "form_en": "can + base verb  ·  know how to + base verb  ·  be able to + base verb",
        "examples": [
            {"en": "She can speak three languages.",
             "fa": "او می‌تواند سه زبان صحبت کند."},
            {"en": "Do you know how to change a tyre?",
             "fa": "می‌دانی چطور لاستیک عوض کنند؟"},
            {"en": "I will be able to help you tomorrow.",
             "fa": "فردا می‌توانم به تو کمک کنم."},
        ],
        "exercises": [
            ex("He ___ swim very well.", "can",
               "A plain present ability takes can.",
               "توانایی سادهٔ حال can می‌گیرد."),
            ex("Do you ___ how to use this machine?", "know",
               "The learned-skill phrase is know how to.",
               "عبارت مهارت آموخته‌شده know how to است."),
            ex("She will ___ able to join us later.", "be",
               "After will, can becomes be able to.",
               "پس از will، can به be able to تبدیل می‌شود."),
        ],
        "exam": [
            q("I would like to ___ able to play the piano.",
              ["be", "can", "could"], "be",
              "Only be able to can follow the infinitive to.",
              "تنها be able to می‌تواند پس از to بیاید."),
            q("___ you know how to drive?",
              ["Do", "Can", "Are"], "Do",
              "Know is a main verb, so the question takes do.",
              "know فعل اصلی است، پس پرسش با do ساخته می‌شود."),
            q("They ___ speak French fluently.",
              ["can", "cans", "can to"], "can",
              "A modal takes no -s and no to.",
              "فعل وجهی -s و to نمی‌گیرد."),
        ],
    },
    {
        "section": "9-7",
        "title": "Possibility: can, may, might",
        "title_fa": "احتمال: can، may، might",
        "use_en": "May and might say that something is possible, and might is the more hesitant of the two: it may rain, it might rain. Can also expresses possibility, but for things that are generally true rather than for one event: too much sugar can damage your teeth. For a single event in the future, may or might is the natural choice, and the negative is may not or might not.",
        "use_fa": "may و might می‌گویند چیزی ممکن است و might محتاطانه‌تر است: it may rain، it might rain. can نیز احتمال را بیان می‌کند، اما برای چیزهایی که به‌طور کلی درست‌اند نه یک رویداد: too much sugar can damage your teeth. برای یک رویداد در آینده may یا might انتخاب طبیعی است و منفی آن may not یا might not می‌شود.",
        "form_en": "may / might / can + base verb  ·  negative: may not / might not + base verb",
        "examples": [
            {"en": "It may rain later, so take a coat.",
             "fa": "شاید بعداً باران ببارد، پس کت ببر."},
            {"en": "She might not come to the party tonight.",
             "fa": "شاید او امشب به مهمانی نیاید."},
            {"en": "Too much sugar can damage your teeth.",
             "fa": "شکر زیاد می‌تواند به دندان‌هایت آسیب بزند."},
        ],
        "exercises": [
            ex("Take an umbrella; it ___ rain this afternoon.", "may",
               "One possible event in the near future takes may.",
               "یک رویداد احتمالی در آیندهٔ نزدیک may می‌گیرد."),
            ex("He ___ not be at home; he often works late.", "might",
               "A hesitant possibility takes might not.",
               "احتمال محتاطانه might not می‌گیرد."),
            ex("Regular exercise ___ lower your blood pressure.", "can",
               "A general truth about health takes can.",
               "حقیقت کلی دربارهٔ سلامت can می‌گیرد."),
        ],
        "exam": [
            q("The flight ___ be delayed because of the storm.",
              ["might", "mights", "might to"], "might",
              "A modal has no -s and takes no to.",
              "فعل وجهی -s و to ندارد."),
            q("This plant ___ grow in cold weather.",
              ["can", "cans", "can to"], "can",
              "A general possibility takes can.",
              "احتمال کلی can می‌گیرد."),
            q("She ___ not answer; she is very busy.",
              ["may", "mays", "may to"], "may",
              "Might and may take not directly, with no do.",
              "may و might مستقیماً not می‌گیرند، بدون do."),
        ],
    },
    {
        "section": "9-8",
        "title": "Requests with modals and the answers to them",
        "title_fa": "درخواست با افعال وجهی و پاسخ آن‌ها",
        "use_en": "Can you, will you, could you and would you all ask someone to do something, and they run from casual to formal in that order. Could and would are the politer pair and are the safe choice with a stranger. A willing answer is sure, of course or no problem; a refusal usually begins with I am sorry, but. Would you is always followed by a base verb.",
        "use_fa": "can you، will you، could you و would you همه از کسی می‌خواهند کاری انجام دهد و به همین ترتیب از خودمانی به رسمی می‌روند. could و would مؤدبانه‌ترند و با غریبه انتخاب مطمئن‌اند. پاسخ پذیرفتن با sure، of course یا no problem می‌آید و رد کردن معمولاً با I am sorry, but شروع می‌شود. پس از would you همیشه فعل ساده می‌آید.",
        "form_en": "Can / Could / Will / Would + you + base verb  ·  answer: Sure / Of course / I am sorry, but …",
        "examples": [
            {"en": "Could you pass me the salt, please?",
             "fa": "می‌شود لطفاً نمک را به من بدهی؟"},
            {"en": "Would you close the window? It is cold.",
             "fa": "می‌شود پنجره را ببندی؟ هوا سرد است."},
            {"en": "Can you help me carry these boxes?",
             "fa": "می‌توانی در بردن این جعبه‌ها کمکم کنی؟"},
        ],
        "exercises": [
            ex("___ you open the door for me, please?", "Could",
               "Could is the polite opening for a small request.",
               "could آغاز مؤدبانهٔ یک درخواست کوچک است."),
            ex("___ you help me with this bag? (polite)", "Would",
               "Would you is the formal request form.",
               "would you شکل رسمی درخواست است."),
            ex("A: Could you send me the file? B: ___ , of course.", "Sure",
               "A willing answer to a request is sure.",
               "پاسخ پذیرفتن درخواست با sure می‌آید."),
        ],
        "exam": [
            q("___ you tell me where the station is?",
              ["Could", "Should", "Must"], "Could",
              "Should and must cannot open a polite request.",
              "should و must درخواست مؤدبانه را آغاز نمی‌کنند."),
            q("___ you possibly call me back later?",
              ["Could", "Must", "Should"], "Could",
              "A hedged polite request takes could.",
              "درخواست مؤدبانهٔ همراه با تردید could می‌گیرد."),
            q("A: Can you wait a minute? B: ___ , no problem.",
              ["Sure", "Must", "Ought"], "Sure",
              "Sure is the natural acceptance of a request.",
              "sure پذیرش طبیعی یک درخواست است."),
        ],
    },
    {
        "section": "9-9",
        "title": "Polite requests: would you mind",
        "title_fa": "درخواست مؤدبانه: would you mind",
        "use_en": "Would you mind is followed by the -ing form, because the question literally asks whether the action would trouble the person: would you mind opening the window. A willing answer is not at all or of course not, since yes would mean the person does mind. Would you mind if I … takes a past verb after if: would you mind if I opened the window.",
        "use_fa": "پس از would you mind شکل -ing می‌آید، چون پرسش در واقع می‌پرسد آیا آن کار برای طرف ناراحتی دارد: would you mind opening the window. پاسخ پذیرفتن not at all یا of course not است، چون yes یعنی طرف ناراحت می‌شود. در would you mind if I … پس از if فعل گذشته می‌آید: would you mind if I opened the window.",
        "form_en": "Would you mind + -ing  ·  Would you mind if I + past verb  ·  answer: Not at all / Of course not",
        "examples": [
            {"en": "Would you mind opening the window?",
             "fa": "مشکلی داری پنجره را باز کنی؟"},
            {"en": "Would you mind if I sat here?",
             "fa": "اشکالی ندارد اگر اینجا بنشینم؟"},
            {"en": "Would you mind speaking more slowly, please?",
             "fa": "می‌شود لطفاً آهسته‌تر صحبت کنی؟"},
        ],
        "exercises": [
            ex("Would you mind ___ (close) the door?", "closing",
               "Would you mind takes the -ing form of the verb.",
               "پس از would you mind شکل -ing فعل می‌آید."),
            ex("Would you mind if I ___ (use) your phone?", "used",
               "The if-clause after would you mind takes a past verb.",
               "بند if پس از would you mind فعل گذشته می‌گیرد."),
            ex("A: Would you mind waiting? B: Not at ___.", "all",
               "The willing answer is not at all.",
               "پاسخ پذیرفتن not at all است."),
        ],
        "exam": [
            q("Would you mind ___ me a hand?",
              ["giving", "give", "to give"], "giving",
              "The -ing form follows would you mind.",
              "پس از would you mind شکل -ing می‌آید."),
            q("Would you mind if I ___ early today?",
              ["left", "leave", "leaving"], "left",
              "The if-clause takes the past form left.",
              "بند if شکل گذشتهٔ left را می‌گیرد."),
            q("A: Would you mind turning the music down? B: ___ at all.",
              ["Not", "No", "None"], "Not",
              "The polite yes is not at all.",
              "پاسخ مثبت مؤدبانه not at all است."),
        ],
    },
    {
        "section": "9-10",
        "title": "Suggestions: let's, why don't, shall I, how about",
        "title_fa": "پیشنهاد: let's، why don't، shall I، how about",
        "use_en": "Let's includes the speaker in the suggestion: let's take a taxi. Why don't we includes both of you, and why don't you hands the idea to the other person alone. Shall I or shall we offers to do something or asks for a decision, and how about takes the -ing form or a noun. All of them take a base verb except how about and what about.",
        "use_fa": "let's گوینده را نیز در پیشنهاد شریک می‌کند: let's take a taxi. why don't we هر دو نفر را در بر می‌گیرد و why don't you ایده را تنها به طرف مقابل می‌سپارد. shall I یا shall we پیشنهاد انجام کاری یا پرسش برای تصمیم است و how about شکل -ing یا اسم می‌گیرد. همه فعل ساده می‌گیرند جز how about و what about.",
        "form_en": "Let's + base verb  ·  Why don't we / you + base verb  ·  Shall I / we + base verb  ·  How about + -ing",
        "examples": [
            {"en": "Let's meet at the station at seven.",
             "fa": "بیا ساعت هفت در ایستگاه همدیگر را ببینیم."},
            {"en": "Why don't we ask the teacher?",
             "fa": "چرا از معلم نمی‌پرسیم؟"},
            {"en": "Shall I book the tickets now?",
             "fa": "بلیت‌ها را الان رزرو کنم؟"},
        ],
        "exercises": [
            ex("___ go for a walk after dinner.", "Let's",
               "A suggestion that includes the speaker opens with let's.",
               "پیشنهادی که گوینده را شریک می‌کند با let's آغاز می‌شود."),
            ex("Why ___ we take the earlier bus?", "don't",
               "The suggestion pattern is why don't we.",
               "الگوی پیشنهاد why don't we است."),
            ex("How about ___ (eat) outside tonight?", "eating",
               "How about takes the -ing form.",
               "پس از how about شکل -ing می‌آید."),
        ],
        "exam": [
            q("___ I carry that bag for you?",
              ["Shall", "Will", "Do"], "Shall",
              "An offer to help with I takes shall I.",
              "پیشنهاد کمک با I شکل shall I می‌گیرد."),
            q("Why ___ you ask your sister for help?",
              ["don't", "not", "doesn't"], "don't",
              "The suggestion is why don't you.",
              "الگوی پیشنهاد why don't you است."),
            q("Let's ___ the meeting until Monday.",
              ["postpone", "to postpone", "postponing"], "postpone",
              "Let's is followed by the base verb.",
              "پس از let's فعل ساده می‌آید."),
        ],
    },
]


def main() -> int:
    data = json.loads(BOOKS.read_text(encoding="utf-8"))
    book = next(b for b in data["books"] if b.get("kind") == "grammar")

    old = [l for l in book["lessons"] if l.get("chapter") == CHAPTER]
    assert old, "chapter nine is not in the book"
    first = book["lessons"].index(old[0])

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

    assert lessons[first]["section"] == "9-1"
    for i, lesson in enumerate(lessons, 1):
        lesson["n"] = i
    book["lessons"] = lessons

    size = len(lessons)
    book["about_en"] = (
        f"The grammar of the whole course, chapter by chapter and chart by chart: "
        f"{size} structures from the book's twenty chapters, each with the rule, "
        f"a pattern, examples of it, exercises and a short exam. Chapters one to ten "
        f"are complete, chart 1-1 to 10-11. The explanations and sentences are "
        f"written for this app; the book is the reference text."
    )
    book["about_fa"] = (
        f"دستور زبان تمام دوره، فصل به فصل و نمودار به نمودار: {size} ساختار از "
        f"بیست فصل کتاب، هر یک با قاعده، الگو، مثال، تمرین و یک آزمون کوتاه. "
        f"فصل‌های یک تا ده کامل‌اند، از نمودار ۱-۱ تا ۱۰-۱۱. توضیح‌ها و جمله‌ها برای "
        f"همین برنامه نوشته شده‌اند و کتاب متن مرجع است."
    )

    BOOKS.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")
    print(f"chapter nine: {len(LESSONS)} charts, {size} structures in the book")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
