#!/usr/bin/env python3
"""Write chapter seventeen of the grammar book into books.json.

    python3 tools/chapter17.py

Chapter seventeen of *Understanding and Using English Grammar* is Adverb
Clauses. The book shipped with one placeholder section for it; this replaces it
with the chapter's eleven charts, written out like chapters three to sixteen: the
rule, the form, examples in both languages, three guided exercises and a
three-question check for each.

The sentences and explanations are written for this app. The book is the
reference text, and nothing in this file is transcribed from it.

It is idempotent: chapter seventeen is always rebuilt from this script.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "books.json"

CHAPTER = "Chapter 17"


def ex(prompt, answer, why_en, why_fa):
    return {"prompt": prompt, "answer": answer, "why_en": why_en, "why_fa": why_fa}


def q(text, options, answer, why_en, why_fa):
    assert answer in options and len(options) == 3, text
    return {"q": text, "options": options, "answer": answer,
            "why_en": why_en, "why_fa": why_fa}


LESSONS = [
    {
        "section": "17-1",
        "title": "Adverb clauses: a dependent clause that tells when, why or under what condition",
        "title_fa": "جمله‌های قیدی: جمله‌ای وابسته که زمان، دلیل یا شرط را می‌گوید",
        "use_en": "An adverb clause is a clause that cannot stand alone and answers how, when, why or under what condition the main clause happens. It begins with a subordinator such as when, because, although, if or unless. When the clause comes first, a comma follows it; when it comes second, no comma is needed. The subordinator never takes that away: the dependent clause keeps its own subject and verb.",
        "use_fa": "جملهٔ قیدی جمله‌ای است که به‌تنهایی نمی‌ایستد و می‌گوید جملهٔ اصلی چگونه، کِی، چرا یا در چه شرطی رخ می‌دهد. با حرف ربط وابسته‌سازی مانند when، because، although، if یا unless آغاز می‌شود. اگر جمله اول بیاید پس از آن ویرگول می‌آید و اگر دوم بیاید ویرگول لازم نیست. حرف ربط فاعل و فعل جمله را حذف نمی‌کند.",
        "form_en": "subordinator + subject + verb, + main clause  ·  main clause + subordinator + subject + verb",
        "examples": [
            {"en": "When the rain stopped, we went outside.",
             "fa": "وقتی باران بند آمد، بیرون رفتیم."},
            {"en": "She stayed home because she was ill.",
             "fa": "خانه ماند چون بیمار بود."},
            {"en": "Although it was late, they kept working.",
             "fa": "با اینکه دیر بود، به کار ادامه دادند."},
        ],
        "exercises": [
            ex("___ it was cold, we went for a walk. (contrast)", "Although",
               "A dependent clause opening the sentence takes a subordinator and a comma.",
               "جملهٔ وابسته در آغاز، حرف ربط و ویرگول می‌گیرد."),
            ex("We left early ___ the traffic was heavy. (reason)", "because",
               "Because introduces the reason inside the same sentence.",
               "because دلیل را در همان جمله می‌آورد."),
            ex("I will call you ___ I arrive. (time)", "when",
               "When puts the two events in time order.",
               "when دو رویداد را در زمان مرتب می‌کند."),
        ],
        "exam": [
            q("Which is an adverb clause?",
              ["because she was tired", "she was tired", "her tiredness"],
              "because she was tired",
              "The subordinator marks the dependent clause.",
              "حرف ربط جملهٔ وابسته را نشان می‌دهد."),
            q("___ the film started, we sat down.",
              ["When", "Because of", "Despite"], "When",
              "A clause of time takes when.",
              "جملهٔ زمان when می‌گیرد."),
            q("Where does the comma go when the adverb clause comes first?",
              ["After the clause", "Before the clause", "Nowhere"],
              "After the clause",
              "The opening clause is followed by a comma.",
              "جملهٔ آغازین با ویرگول دنبال می‌شود."),
        ],
    },
    {
        "section": "17-2",
        "title": "Adverb clauses of time: when, while, before, after, until, as soon as",
        "title_fa": "جمله‌های قیدی زمان: when، while، before، after، until، as soon as",
        "use_en": "Time clauses place one action against another: when for a point, while for something in progress, before and after for order, until for the end of a period, as soon as for the moment something is complete, and since for a starting point. The time clause takes the present tense even when the meaning is future: I will call you when I arrive, never when I will arrive.",
        "use_fa": "جمله‌های زمانی یک کار را در برابر کار دیگر می‌گذارند: when برای یک نقطه، while برای کار در جریان، before و after برای ترتیب، until برای پایان یک دوره، as soon as برای لحظهٔ کامل شدن کاری و since برای نقطهٔ آغاز. جملهٔ زمانی حتی وقتی معنا آینده است فعل حال می‌گیرد: I will call you when I arrive و هرگز when I will arrive.",
        "form_en": "time clause in the present + main clause with will  ·  while / until / before / after / as soon as",
        "examples": [
            {"en": "I will call you when I arrive.",
             "fa": "وقتی رسیدم به تو زنگ می‌زنم."},
            {"en": "While she was cooking, the phone rang.",
             "fa": "وقتی داشت آشپزی می‌کرد تلفن زنگ زد."},
            {"en": "Wait here until the bus comes.",
             "fa": "اینجا منتظر بمان تا اتوبوس بیاید."},
        ],
        "exercises": [
            ex("We will start as soon as everyone ___ here. (be)", "is",
               "A future time clause keeps the present tense.",
               "جملهٔ زمانی آینده فعل حال را نگه می‌دارد."),
            ex("___ I was reading, she was writing. (same time)", "While",
               "While marks an action in progress beside another.",
               "while کار در جریان را در کنار کار دیگر می‌گذارد."),
            ex("Don't leave ___ I come back. (end of the period)", "until",
               "Until marks the end of the waiting.",
               "until پایان انتظار را نشان می‌دهد."),
        ],
        "exam": [
            q("I'll call you ___ I get home.",
              ["when", "while", "until"], "when",
              "A point in time after arriving takes when.",
              "نقطه‌ای در زمان پس از رسیدن when می‌گیرد."),
            q("She was cooking ___ the lights went out.",
              ["while", "as soon as", "since"], "while",
              "An action in progress takes while.",
              "کار در جریان while می‌گیرد."),
            q("Which sentence is correct?",
              ["We will go when the rain stops.", "We will go when the rain will stop.",
               "We will go when the rain stopping."], "We will go when the rain stops.",
              "The time clause stays in the present after will.",
              "جملهٔ زمانی پس از will در حال می‌ماند."),
        ],
    },
    {
        "section": "17-3",
        "title": "Adverb clauses of cause: because, since, as",
        "title_fa": "جمله‌های قیدی دلیل: because، since، as",
        "use_en": "Because gives the reason and is the most direct of the three. Since and as also give a reason and often suggest that the reader already knows it: since you are here, you can help. Because of and due to are not clause markers; they take a noun: because of the rain. A reason clause answers why, so it cannot be replaced by a phrase without changing the grammar of the sentence.",
        "use_fa": "because دلیل را می‌گوید و مستقیم‌ترین این سه است. since و as هم دلیل را می‌گویند و معمولاً نشان می‌دهند که خواننده از پیش آن را می‌داند: since you are here, you can help. because of و due to نشانهٔ جمله نیستند و اسم می‌گیرند: because of the rain. جملهٔ دلیل به «چرا» پاسخ می‌دهد، پس با عبارت جایگزین نمی‌شود مگر ساختار جمله عوض شود.",
        "form_en": "because / since / as + subject + verb  ·  because of / due to + noun",
        "examples": [
            {"en": "We stayed inside because the wind was strong.",
             "fa": "داخل ماندیم چون باد شدید بود."},
            {"en": "Since you are here, you can help me.",
             "fa": "حالا که اینجایی می‌توانی کمکم کنی."},
            {"en": "The match was cancelled because of the rain.",
             "fa": "مسابقه به دلیل باران لغو شد."},
        ],
        "exercises": [
            ex("___ she had studied, she passed easily. (known reason)", "Since",
               "Since gives a reason the reader already accepts.",
               "since دلیلی می‌دهد که خواننده می‌پذیرد."),
            ex("The flight was delayed ___ the storm. (before a noun)", "because of",
               "Before a noun the phrase is because of.",
               "پیش از اسم عبارت because of می‌آید."),
            ex("He left early ___ he felt ill. (direct reason)", "because",
               "Because answers why in a clause.",
               "because در جمله به «چرا» پاسخ می‌دهد."),
        ],
        "exam": [
            q("We cancelled the picnic ___ the weather.",
              ["because of", "because", "since"], "because of",
              "A noun follows because of, not a clause.",
              "پس از because of اسم می‌آید نه جمله."),
            q("___ it was raining, we took a taxi.",
              ["Because", "Because of", "Due to"], "Because",
              "A clause takes because.",
              "جمله because می‌گیرد."),
            q("Which sentence is correct?",
              ["He was late because the bus broke down.",
               "He was late because of the bus broke down.",
               "He was late because the bus broke down it."],
              "He was late because the bus broke down.",
              "Because introduces a full clause.",
              "because جملهٔ کامل می‌گیرد."),
        ],
    },
    {
        "section": "17-4",
        "title": "Unexpected result: even though, although, though",
        "title_fa": "نتیجهٔ غیرمنتظره: even though، although، though",
        "use_en": "These three clauses say that the result is surprising given the information: although it rained, the match continued. Even though is the strongest and underlines the contrast; although is neutral and slightly formal; though is the most conversational and can also end a sentence. None of them takes a comma inside the clause, and none of them is followed by but.",
        "use_fa": "این سه جمله می‌گویند نتیجه با توجه به اطلاعات غافلگیرکننده است: although it rained, the match continued. even though قوی‌ترین است و بر تضاد تأکید می‌کند، although خنثی و کمی رسمی است و though گفتاری‌ترین است و می‌تواند در پایان جمله هم بیاید. هیچ‌کدام درون جمله ویرگول نمی‌گیرند و هیچ‌کدام با but نمی‌آیند.",
        "form_en": "although / even though / though + subject + verb  ·  no but after the clause",
        "examples": [
            {"en": "Although it rained, the match continued.",
             "fa": "با اینکه باران می‌بارید، مسابقه ادامه یافت."},
            {"en": "Even though she was tired, she finished the report.",
             "fa": "حتی با اینکه خسته بود، گزارش را تمام کرد."},
            {"en": "He came, though he was not invited.",
             "fa": "آمد، هرچند دعوت نشده بود."},
        ],
        "exercises": [
            ex("___ he studied hard, he failed the exam. (strong contrast)", "Even though",
               "Even though strengthens the contrast.",
               "even though تضاد را قوی‌تر می‌کند."),
            ex("The plan worked, ___ nobody expected it. (end of sentence)", "though",
               "Though can close a sentence in speech.",
               "though می‌تواند در گفتار جمله را ببندد."),
            ex("___ the price was high, they bought it. (neutral)", "Although",
               "Although reports the contrast without emphasis.",
               "although تضاد را بی تأکید می‌گوید."),
        ],
        "exam": [
            q("___ it was cold, they went swimming.",
              ["Although", "Despite", "Because of"], "Although",
              "A clause of unexpected result takes although.",
              "جملهٔ نتیجهٔ غیرمنتظره although می‌گیرد."),
            q("Which sentence is wrong?",
              ["Although it rained, but we went out.", "Although it rained, we went out.",
               "Even though it rained, we went out."], "Although it rained, but we went out.",
              "Although and but do not appear together.",
              "although و but با هم نمی‌آیند."),
            q("___ he apologised, she was still upset.",
              ["Even though", "Even", "Though of"], "Even though",
              "The strong contrast is even though.",
              "تضاد قوی even though است."),
        ],
    },
    {
        "section": "17-5",
        "title": "Direct contrast: while and whereas",
        "title_fa": "تضاد مستقیم: while و whereas",
        "use_en": "While and whereas place two facts side by side without calling either surprising: my sister plays tennis, while I prefer swimming. Whereas is the more formal of the two and appears mostly in writing. While also carries a time meaning, so in a sentence about two periods it can be read either way; whereas can only mean contrast, which makes it the clearer choice in an argument.",
        "use_fa": "while و whereas دو واقعیت را بی آنکه یکی را غافلگیرکننده بخوانند کنار هم می‌گذارند: my sister plays tennis, while I prefer swimming. whereas رسمی‌تر است و بیشتر در نوشتار می‌آید. while معنای زمان هم دارد، پس در جمله‌ای دربارهٔ دو دورهٔ زمانی دو معنا می‌تواند داشته باشد؛ whereas تنها تضاد می‌گوید و در استدلال روشن‌تر است.",
        "form_en": "clause, + while / whereas + clause  ·  whereas is formal and contrast only",
        "examples": [
            {"en": "My sister plays tennis, while I prefer swimming.",
             "fa": "خواهرم تنیس بازی می‌کند، در حالی که من شنا را ترجیح می‌دهم."},
            {"en": "The north is wet, whereas the south is dry.",
             "fa": "شمال پرباران است، در حالی که جنوب خشک است."},
            {"en": "While he works in an office, she works outdoors.",
             "fa": "او در دفتر کار می‌کند، در حالی که او بیرون کار می‌کند."},
        ],
        "exercises": [
            ex("Tea is cheap, ___ coffee is expensive. (formal contrast)", "whereas",
               "Whereas marks a formal direct contrast.",
               "whereas تضاد مستقیم رسمی را نشان می‌دهد."),
            ex("___ I like the city, my brother prefers the countryside. (contrast)", "While",
               "While places two facts side by side.",
               "while دو واقعیت را کنار هم می‌گذارد."),
            ex("She studied medicine, ___ her sister studied law. (contrast)", "whereas",
               "Whereas joins two parallel facts with a contrast.",
               "whereas دو واقعیت موازی را با تضاد به هم می‌پیوندد."),
        ],
        "exam": [
            q("Which word can only mean contrast?",
              ["whereas", "while", "when"], "whereas",
              "While can also mark time; whereas cannot.",
              "while زمان هم می‌گوید و whereas تنها تضاد."),
            q("___ the first plan was cheap, the second was safer.",
              ["Whereas", "Because of", "So that"], "Whereas",
              "A direct contrast takes whereas.",
              "تضاد مستقیم whereas می‌گیرد."),
            q("Which sentence is correct?",
              ["He drives, while she takes the train.", "He drives, while she taking the train.",
               "He drives while, she takes the train."], "He drives, while she takes the train.",
              "Both sides are full clauses with a comma before while.",
              "هر دو طرف جملهٔ کامل‌اند و پیش از while ویرگول می‌آید."),
        ],
    },
    {
        "section": "17-6",
        "title": "Conditions in adverb clauses: if",
        "title_fa": "شرط در جمله‌های قیدی: if",
        "use_en": "An if-clause states the condition for the main clause to happen: if it rains, we will stay home. The if-clause takes the present tense when the main clause is about the future, and the main clause carries will. The comma separates the clause when it comes first, and the order can be reversed without changing the meaning.",
        "use_fa": "جملهٔ if شرطی را می‌گوید که جملهٔ اصلی به آن بستگی دارد: if it rains, we will stay home. جملهٔ if وقتی جملهٔ اصلی دربارهٔ آینده است فعل حال می‌گیرد و جملهٔ اصلی will دارد. اگر جملهٔ شرط اول بیاید ویرگول جدا می‌کند و جابه‌جایی ترتیب معنا را عوض نمی‌کند.",
        "form_en": "if + present, + main clause with will  ·  main clause + if + present",
        "examples": [
            {"en": "If it rains, we will stay home.",
             "fa": "اگر باران ببارد، خانه می‌مانیم."},
            {"en": "We will stay home if it rains.",
             "fa": "اگر باران ببارد خانه می‌مانیم."},
            {"en": "If you need help, call me.",
             "fa": "اگر کمک لازم داشتی به من زنگ بزن."},
        ],
        "exercises": [
            ex("If the train ___ late, we will miss the film. (be)", "is",
               "An if-clause about the future stays in the present.",
               "جملهٔ if دربارهٔ آینده در حال می‌ماند."),
            ex("We will cancel the trip if it ___ . (snow)", "snows",
               "The present simple carries the future meaning.",
               "حال ساده معنای آینده را می‌رساند."),
            ex("If you ___ tired, go to bed. (feel)", "feel",
               "An instruction after if also takes the present.",
               "دستور پس از if هم حال می‌گیرد."),
        ],
        "exam": [
            q("If it ___ tomorrow, we will go out.",
              ["does not rain", "will not rain", "not rain"], "does not rain",
              "The condition stays in the present.",
              "شرط در زمان حال می‌ماند."),
            q("I will help you if you ___ me.",
              ["ask", "will ask", "asked"], "ask",
              "A present verb follows if in a real condition.",
              "در شرط واقعی پس از if فعل حال می‌آید."),
            q("Which sentence is correct?",
              ["If you are late, we will start without you.",
               "If you will be late, we will start without you.",
               "If you be late, we will start without you."],
              "If you are late, we will start without you.",
              "No will inside the if-clause.",
              "در جملهٔ if هیچ will نمی‌آید."),
        ],
    },
    {
        "section": "17-7",
        "title": "Shortened if-clauses: if necessary, if possible",
        "title_fa": "جمله‌های if کوتاه‌شده: if necessary، if possible",
        "use_en": "When the subject and the verb be would repeat what is already understood, an if-clause can shrink to if plus an adjective or a participle: if necessary, if possible, if needed, if required, if not, if so. These are fixed phrases rather than new grammar, and they keep the sentence short without losing the condition.",
        "use_fa": "وقتی فاعل و فعل be چیزی را تکرار می‌کنند که از پیش روشن است، جملهٔ if می‌تواند به if و یک صفت یا اسم مفعول کوتاه شود: if necessary، if possible، if needed، if required، if not، if so. این‌ها عبارت‌های ثابت‌اند نه دستور تازه، و جمله را کوتاه نگه می‌دارند بی‌آنکه شرط از دست برود.",
        "form_en": "if + adjective / participle  ·  if necessary, if possible, if needed, if not",
        "examples": [
            {"en": "Call me if necessary.",
             "fa": "اگر لازم شد به من زنگ بزن."},
            {"en": "We will send the file today, if possible.",
             "fa": "اگر ممکن باشد امروز فایل را می‌فرستیم."},
            {"en": "Take an umbrella, if needed.",
             "fa": "اگر لازم شد چتر بردار."},
        ],
        "exercises": [
            ex("Finish it today if ___ . (possible)", "possible",
               "The shortened clause keeps only the adjective.",
               "جملهٔ کوتاه‌شده تنها صفت را نگه می‌دارد."),
            ex("We can meet tomorrow if ___ . (necessary)", "necessary",
               "If plus an adjective replaces the full clause.",
               "if و صفت جای جملهٔ کامل را می‌گیرد."),
            ex("Bring your passport, if ___ . (require)", "required",
               "A participle can follow if in the shortened form.",
               "اسم مفعول می‌تواند در شکل کوتاه پس از if بیاید."),
        ],
        "exam": [
            q("Send the report today if ___.",
              ["possible", "it possible", "is possible"], "possible",
              "The shortened clause drops the subject and be.",
              "جملهٔ کوتاه‌شده فاعل و be را حذف می‌کند."),
            q("Which phrase is a shortened if-clause?",
              ["if necessary", "if it necessaries", "if the necessary"], "if necessary",
              "The fixed phrase keeps only the adjective.",
              "عبارت ثابت تنها صفت را نگه می‌دارد."),
            q("We will pay extra if ___.",
              ["required", "requiring", "require"], "required",
              "A past participle fits the shortened condition.",
              "اسم مفعول در شرط کوتاه می‌آید."),
        ],
    },
    {
        "section": "17-8",
        "title": "Whether or not and even if",
        "title_fa": "whether or not و even if",
        "use_en": "Whether or not says that the result stands in both cases: whether or not it rains, the match will be played. It is not the same as if, which leaves the result open. Even if accepts the condition and says the result does not change: even if you pay me, I will not do it. The clause still takes the present tense when the main clause is in the future.",
        "use_fa": "whether or not می‌گوید نتیجه در هر دو حالت برقرار است: whether or not it rains, the match will be played. این با if یکی نیست، چون if نتیجه را باز می‌گذارد. even if شرط را می‌پذیرد و می‌گوید نتیجه عوض نمی‌شود: even if you pay me, I will not do it. جمله هنوز وقتی جملهٔ اصلی آینده است فعل حال می‌گیرد.",
        "form_en": "whether or not + subject + verb  ·  even if + subject + verb",
        "examples": [
            {"en": "Whether or not it rains, the match will be played.",
             "fa": "چه باران ببارد چه نه، مسابقه برگزار می‌شود."},
            {"en": "Even if you pay me, I will not do it.",
             "fa": "حتی اگر پول هم بدهی این کار را نمی‌کنم."},
            {"en": "I will go, even if nobody comes with me.",
             "fa": "می‌روم، حتی اگر هیچ‌کس همراهم نیاید."},
        ],
        "exercises": [
            ex("___ or not she agrees, the plan goes ahead. (both cases)", "Whether",
               "Both outcomes standing takes whether or not.",
               "برقراری هر دو حالت whether or not می‌گیرد."),
            ex("___ if it costs more, we need the better model. (result unchanged)", "Even",
               "Even if says the result does not change.",
               "even if می‌گوید نتیجه عوض نمی‌شود."),
            ex("Whether or not you ___ , call me tonight. (come)", "come",
               "The clause stays in the present tense.",
               "جمله در زمان حال می‌ماند."),
        ],
        "exam": [
            q("___ or not he calls, we will leave at six.",
              ["Whether", "Even", "If"], "Whether",
              "Both cases take whether or not.",
              "هر دو حالت whether or not می‌گیرد."),
            q("___ if it rains, the event will go on.",
              ["Even", "Whether", "Unless"], "Even",
              "The result is unchanged, so even if.",
              "نتیجه عوض نمی‌شود، پس even if."),
            q("Which sentence is correct?",
              ["I will finish it whether or not you help me.",
               "I will finish it whether or not you will help me.",
               "I will finish it whether or not you helping me."],
              "I will finish it whether or not you help me.",
              "The condition clause stays in the present.",
              "جملهٔ شرط در حال می‌ماند."),
        ],
    },
    {
        "section": "17-9",
        "title": "In case: doing something to be ready",
        "title_fa": "in case: کاری برای آماده بودن",
        "use_en": "In case says that you take an action because something might happen later: take an umbrella in case it rains. It is not the same as if. If reports a condition that decides the action; in case reports a precaution, and the action happens whether or not the event does. In case is never followed by will, and it is never written as two words meaning if.",
        "use_fa": "in case می‌گوید کاری می‌کنید چون ممکن است بعداً چیزی رخ دهد: take an umbrella in case it rains. این با if یکی نیست. if شرطی را می‌گوید که تصمیم را تعیین می‌کند و in case احتیاطی را می‌گوید؛ کار انجام می‌شود، خواه آن رویداد رخ دهد خواه نه. پس از in case هرگز will نمی‌آید.",
        "form_en": "action + in case + subject + verb (present)  ·  not a substitute for if",
        "examples": [
            {"en": "Take an umbrella in case it rains.",
             "fa": "چتر بردار که مبادا باران ببارد."},
            {"en": "I will leave early in case the roads are busy.",
             "fa": "زود راه می‌افتم که مبادا جاده‌ها شلوغ باشند."},
            {"en": "Write it down in case you forget.",
             "fa": "یادداشتش کن که مبادا فراموش کنی."},
        ],
        "exercises": [
            ex("Take some money ___ you need a taxi. (precaution)", "in case",
               "A precaution takes in case.",
               "احتیاط in case می‌گیرد."),
            ex("I'll charge the phone ___ the battery runs out. (precaution)", "in case",
               "In case introduces what might happen later.",
               "in case چیزی را می‌آورد که ممکن است بعداً رخ دهد."),
            ex("Bring a jacket ___ it gets cold. (precaution)", "in case",
               "In case does not decide the action, it prepares for it.",
               "in case تصمیم را تعیین نمی‌کند، آماده می‌کند."),
        ],
        "exam": [
            q("Take a map ___ you get lost.",
              ["in case", "if", "unless"], "in case",
              "A precaution for something possible is in case.",
              "احتیاط برای امر ممکن in case است."),
            q("Which sentence is correct?",
              ["I'll wait here in case she comes.", "I'll wait here in case she will come.",
               "I'll wait here in case she coming."],
              "I'll wait here in case she comes.",
              "In case is followed by the present tense.",
              "پس از in case فعل حال می‌آید."),
            q("How is in case different from if?",
              ["It describes a precaution, not a condition.",
               "It is more formal.", "It means unless."],
              "It describes a precaution, not a condition.",
              "The action happens either way.",
              "کار در هر حال انجام می‌شود."),
        ],
    },
    {
        "section": "17-10",
        "title": "Unless: if not",
        "title_fa": "unless: اگر نه",
        "use_en": "Unless means if not and carries the negative itself, so the clause after it stays positive: we will go unless it rains, not unless it does not rain. It is common in speech and in rules, and it is best avoided when the sentence already has another negative, because two negatives make the meaning hard to follow.",
        "use_fa": "unless یعنی «اگر نه» و خودش منفی را با خود دارد، پس جملهٔ پس از آن مثبت می‌ماند: we will go unless it rains و نه unless it does not rain. در گفتار و در قاعده‌ها رایج است و بهتر است وقتی جمله منفی دیگری دارد به کار نرود، چون دو منفی معنا را سخت می‌کند.",
        "form_en": "unless + positive clause  ·  unless = if not",
        "examples": [
            {"en": "We will go unless it rains.",
             "fa": "اگر باران نبارد می‌رویم."},
            {"en": "You cannot enter unless you have a ticket.",
             "fa": "بدون بلیت نمی‌توانی وارد شوی."},
            {"en": "Unless she calls, we will start without her.",
             "fa": "اگر زنگ نزند بی او شروع می‌کنیم."},
        ],
        "exercises": [
            ex("I won't go ___ you come with me. (if not)", "unless",
               "Unless carries the negative meaning.",
               "unless معنای منفی را با خود دارد."),
            ex("___ you hurry, you will miss the train. (if not)", "Unless",
               "The clause after unless stays positive.",
               "جملهٔ پس از unless مثبت می‌ماند."),
            ex("We cannot finish ___ we get more time. (if not)", "unless",
               "Unless replaces if not in one word.",
               "unless جای if not را می‌گیرد."),
        ],
        "exam": [
            q("___ you study, you will not pass.",
              ["Unless", "If", "In case"], "Unless",
              "The meaning is if not, so unless.",
              "معنا «اگر نه» است، پس unless."),
            q("Which sentence is correct?",
              ["We will go unless it rains.", "We will go unless it does not rain.",
               "We will go unless it will rain."], "We will go unless it rains.",
              "Unless already means if not, and takes the present.",
              "unless خودش «اگر نه» است و حال می‌گیرد."),
            q("Unless is closest in meaning to ___.",
              ["if not", "even if", "in case"], "if not",
              "Unless is the negative of if.",
              "unless منفیِ if است."),
        ],
    },
    {
        "section": "17-11",
        "title": "Only if: one condition and no other",
        "title_fa": "only if: تنها یک شرط و نه هیچ شرط دیگر",
        "use_en": "Only if narrows the condition to one: you can borrow the car only if you fill the tank. When only if opens the sentence, the main clause takes inverted word order: only if you fill the tank can you borrow the car. It is stronger than if, and it is the opposite of even if, which accepts conditions without changing the result.",
        "use_fa": "only if شرط را به یکی محدود می‌کند: you can borrow the car only if you fill the tank. اگر only if جمله را آغاز کند، جملهٔ اصلی ترتیب وارونه می‌گیرد: only if you fill the tank can you borrow the car. این از if قوی‌تر است و متضاد even if است که شرط را می‌پذیرد بی‌آنکه نتیجه عوض شود.",
        "form_en": "main clause + only if + condition  ·  only if + condition, + inverted main clause",
        "examples": [
            {"en": "You can borrow the car only if you fill the tank.",
             "fa": "تنها اگر باک را پر کنی می‌توانی ماشین را قرض بگیری."},
            {"en": "Only if you fill the tank can you borrow the car.",
             "fa": "تنها در صورتی که باک را پر کنی می‌توانی ماشین را بگیری."},
            {"en": "The plan works only if everyone agrees.",
             "fa": "طرح تنها وقتی جواب می‌دهد که همه موافق باشند."},
        ],
        "exercises": [
            ex("You may leave only ___ you finish the work. (one condition)", "if",
               "Only if restricts the condition to one.",
               "only if شرط را به یکی محدود می‌کند."),
            ex("Only if we leave now ___ we catch the train. (inverted)", "can",
               "An opening only if inverts the main clause.",
               "only if در آغاز جملهٔ اصلی را وارونه می‌کند."),
            ex("She speaks only ___ she has something to say. (condition)", "if",
               "Only if states the single condition.",
               "only if شرط یگانه را می‌گوید."),
        ],
        "exam": [
            q("___ if you book early can you get a discount.",
              ["Only", "Even", "Unless"], "Only",
              "Only if opens the sentence and inverts the clause.",
              "only if جمله را باز می‌کند و آن را وارونه می‌سازد."),
            q("Which sentence is correct?",
              ["Only if you ask will she help.", "Only if you ask she will help.",
               "Only if you will ask she helps."], "Only if you ask will she help.",
              "The opening only if takes inverted order.",
              "only if در آغاز ترتیب وارونه می‌گیرد."),
            q("Only if is the opposite of ___.",
              ["even if", "unless", "in case"], "even if",
              "Only if restricts; even if accepts the condition without changing the result.",
              "only if محدود می‌کند و even if شرط را می‌پذیرد."),
        ],
    },
]


def main() -> int:
    data = json.loads(BOOKS.read_text(encoding="utf-8"))
    book = next(b for b in data["books"] if b.get("kind") == "grammar")

    old = [l for l in book["lessons"] if l.get("chapter") == CHAPTER]
    assert old, "chapter seventeen is not in the book"

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
    print(f"chapter seventeen: {len(LESSONS)} charts, {size} structures in the book")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
