#!/usr/bin/env python3
"""Write chapter nineteen of the grammar book into books.json.

    python3 tools/chapter19.py

Chapter nineteen of *Understanding and Using English Grammar* is Connectives
that Express Cause and Effect, Contrast, and Condition. The book shipped with one
placeholder section for it; this replaces it with the chapter's nine charts,
written out like chapters three to eighteen: the rule, the form, examples in both
languages, three guided exercises and a three-question check for each.

The sentences and explanations are written for this app. The book is the
reference text, and nothing in this file is transcribed from it.

It is idempotent: chapter nineteen is always rebuilt from this script.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "books.json"

CHAPTER = "Chapter 19"


def ex(prompt, answer, why_en, why_fa):
    return {"prompt": prompt, "answer": answer, "why_en": why_en, "why_fa": why_fa}


def q(text, options, answer, why_en, why_fa):
    assert answer in options and len(options) == 3, text
    return {"q": text, "options": options, "answer": answer,
            "why_en": why_en, "why_fa": why_fa}


LESSONS = [
    {
        "section": "19-1",
        "title": "Connectives: linking a cause to its result",
        "title_fa": "واژه‌های پیوند: پیوند دادن علت به نتیجه",
        "use_en": "A cause and its result can be joined in three ways, and the grammar decides the punctuation. A clause with because keeps both parts in one sentence. A phrase with because of needs a noun. A connective such as therefore starts a new sentence or follows a semicolon. Choosing among them is a question of how much weight the result deserves, not of formality alone.",
        "use_fa": "علت و نتیجه را می‌توان به سه شکل به هم پیوند داد و دستور، نگارش را تعیین می‌کند. جمله با because هر دو بخش را در یک جمله نگه می‌دارد. عبارت با because of اسم لازم دارد. واژه‌ای مانند therefore جملهٔ تازه‌ای آغاز می‌کند یا پس از نقطه‌ویرگول می‌آید. انتخاب میان آن‌ها پرسش وزن نتیجه است، نه تنها رسمیت.",
        "form_en": "clause + because + clause  ·  because of + noun  ·  clause; therefore, + clause",
        "examples": [
            {"en": "The flight was cancelled because the airport was closed.",
             "fa": "پرواز لغو شد چون فرودگاه بسته بود."},
            {"en": "The flight was cancelled because of the snow.",
             "fa": "پرواز به دلیل برف لغو شد."},
            {"en": "The airport was closed; therefore, the flight was cancelled.",
             "fa": "فرودگاه بسته بود؛ بنابراین پرواز لغو شد."},
        ],
        "exercises": [
            ex("The game stopped ___ the rain. (before a noun)", "because of",
               "A noun needs because of.",
               "اسم because of می‌خواهد."),
            ex("He was late ___ the bus broke down. (clause)", "because",
               "A clause needs because.",
               "جمله because می‌خواهد."),
            ex("The road was flooded; ___ , we turned back. (result)", "therefore",
               "Therefore opens the result after a semicolon.",
               "therefore نتیجه را پس از نقطه‌ویرگول می‌آورد."),
        ],
        "exam": [
            q("Which sentence is correct?",
              ["We stayed in because of the storm.", "We stayed in because of it stormed.",
               "We stayed in because the storm."], "We stayed in because of the storm.",
              "Because of takes a noun phrase.",
              "because of عبارت اسمی می‌گیرد."),
            q("She missed the train, ___ she took a taxi.",
              ["so", "because of", "due to"], "so",
              "A result inside one sentence takes so.",
              "نتیجه در یک جمله so می‌گیرد."),
            q("Which connective begins a new sentence?",
              ["Therefore", "Because", "Although"], "Therefore",
              "Therefore can open a sentence or follow a semicolon.",
              "therefore می‌تواند جمله را باز کند یا پس از نقطه‌ویرگول بیاید."),
        ],
    },
    {
        "section": "19-2",
        "title": "Because of and due to before a noun",
        "title_fa": "because of و due to پیش از اسم",
        "use_en": "Because of and due to both introduce a noun or a noun phrase and give the cause: because of the delay, due to bad weather. Due to is the more formal of the two and is common in reports and notices. Neither can be followed by a clause, and the pair is never written as because of the fact that when a single phrase will do.",
        "use_fa": "because of و due to هر دو اسم یا عبارت اسمی می‌آورند و علت را می‌گویند: because of the delay، due to bad weather. due to رسمی‌تر است و در گزارش‌ها و اطلاعیه‌ها رایج. هیچ‌کدام جمله نمی‌گیرند و این جفت هرگز به شکل because of the fact that نوشته نمی‌شود وقتی یک عبارت کوتاه کافی است.",
        "form_en": "because of / due to + noun or noun phrase (never a clause)",
        "examples": [
            {"en": "The match was delayed because of the heat.",
             "fa": "مسابقه به دلیل گرما به تأخیر افتاد."},
            {"en": "Due to staff shortages, the office closes early.",
             "fa": "به دلیل کمبود کارکنان دفتر زودتر بسته می‌شود."},
            {"en": "We could not see anything because of the fog.",
             "fa": "به دلیل مه هیچ چیز نمی‌دیدیم."},
        ],
        "exercises": [
            ex("The train was late ___ technical problems. (formal)", "due to",
               "Due to is the formal choice before a noun.",
               "due to انتخاب رسمی پیش از اسم است."),
            ex("She stayed home ___ a bad cold. (cause before a noun)", "because of",
               "Because of introduces the noun cause.",
               "because of علت اسمی را می‌آورد."),
            ex("___ the noise, we could not concentrate. (cause)", "Because of",
               "A noun phrase after the cause takes because of.",
               "عبارت اسمی پس از علت because of می‌گیرد."),
        ],
        "exam": [
            q("The event was cancelled ___ the weather.",
              ["because of", "because", "so"], "because of",
              "A noun follows the cause phrase.",
              "پس از عبارت علت اسم می‌آید."),
            q("Which sentence is wrong?",
              ["We left because of it was late.", "We left because of the time.",
               "We left due to the time."], "We left because of it was late.",
              "Because of cannot take a clause.",
              "because of جمله نمی‌گیرد."),
            q("___ heavy traffic, she missed her appointment.",
              ["Due to", "Due", "Because"], "Due to",
              "The cause of a noun phrase takes due to.",
              "علت عبارت اسمی due to می‌گیرد."),
        ],
    },
    {
        "section": "19-3",
        "title": "Therefore, consequently and so: the result in a new clause",
        "title_fa": "therefore، consequently و so: نتیجه در جمله‌ای تازه",
        "use_en": "These three connectives introduce the result rather than the cause. So is the conversational one and joins two clauses with a comma: it rained, so we stayed in. Therefore and consequently are formal, take a comma after them and usually follow a semicolon or a full stop: it rained; therefore, we stayed in. They cannot join two clauses with a comma alone.",
        "use_fa": "این سه پیوند نتیجه را می‌آورند نه علت. so گفتاری است و دو جمله را با ویرگول به هم می‌پیوندد: it rained, so we stayed in. therefore و consequently رسمی‌اند، پس از خود ویرگول می‌گیرند و معمولاً پس از نقطه‌ویرگول یا نقطه می‌آیند: it rained; therefore, we stayed in. آن‌ها نمی‌توانند دو جمله را تنها با ویرگول به هم بپیوندند.",
        "form_en": "clause, + so + clause  ·  clause; therefore, + clause  ·  clause. Consequently, + clause",
        "examples": [
            {"en": "It rained all day, so we stayed inside.",
             "fa": "تمام روز باران بارید، پس داخل ماندیم."},
            {"en": "The roads were icy; therefore, the school closed.",
             "fa": "جاده‌ها یخ‌زده بود؛ بنابراین مدرسه تعطیل شد."},
            {"en": "He missed the deadline. Consequently, he lost the contract.",
             "fa": "مهلت را از دست داد. در نتیجه قرارداد را باخت."},
        ],
        "exercises": [
            ex("She studied every day, ___ she passed easily. (conversational result)", "so",
               "So joins a result inside one sentence.",
               "so نتیجه را در یک جمله می‌آورد."),
            ex("The shop was closed; ___ , we went home. (formal result)", "therefore",
               "Therefore follows a semicolon and takes a comma.",
               "therefore پس از نقطه‌ویرگول و با ویرگول می‌آید."),
            ex("The team lost three matches. ___ , they were relegated. (formal)", "Consequently",
               "Consequently opens a sentence and takes a comma.",
               "consequently جمله را باز می‌کند و ویرگول می‌گیرد."),
        ],
        "exam": [
            q("The traffic was terrible, ___ we arrived late.",
              ["so", "therefore", "because of"], "so",
              "A comma joins the two clauses with so.",
              "ویرگول دو جمله را با so پیوند می‌دهد."),
            q("Which sentence is punctuated correctly?",
              ["It snowed; therefore, we stayed home.", "It snowed, therefore we stayed home.",
               "It snowed therefore, we stayed home."], "It snowed; therefore, we stayed home.",
              "Therefore needs a semicolon before and a comma after.",
              "therefore پیش از خود نقطه‌ویرگول و پس از خود ویرگول می‌خواهد."),
            q("He forgot his passport. ___, he missed the flight.",
              ["Consequently", "Because", "Although"], "Consequently",
              "The result opens the second sentence.",
              "نتیجه جملهٔ دوم را باز می‌کند."),
        ],
    },
    {
        "section": "19-4",
        "title": "Patterns and punctuation for cause and effect",
        "title_fa": "الگوها و نگارش علت و اثر",
        "use_en": "The punctuation follows the connective, not the meaning. A subordinator inside one sentence needs no punctuation when it comes second and a comma when it comes first. A transition word needs a semicolon or a full stop before it and a comma after. A coordinating conjunction needs a comma before it. Mixing these up produces the comma splice, which is the most common error in this chapter.",
        "use_fa": "نگارش از پیوند پیروی می‌کند نه از معنا. حرف ربط وابسته‌ساز درون یک جمله اگر دوم بیاید ویرگول نمی‌خواهد و اگر اول بیاید ویرگول می‌خواهد. واژهٔ گذار پیش از خود نقطه‌ویرگول یا نقطه و پس از خود ویرگول می‌خواهد. حرف ربط هم‌پایه پیش از خود ویرگول می‌خواهد. جابه‌جا کردن این‌ها «ویرگول چسبان» می‌سازد که رایج‌ترین خطای این فصل است.",
        "form_en": "subordinator: no comma second · transition: ; … , · coordinator: , + and/but/so",
        "examples": [
            {"en": "Because the road was closed, we took a longer route.",
             "fa": "چون جاده بسته بود راه طولانی‌تری رفتیم."},
            {"en": "We took a longer route because the road was closed.",
             "fa": "راه طولانی‌تری رفتیم چون جاده بسته بود."},
            {"en": "The road was closed; as a result, we took a longer route.",
             "fa": "جاده بسته بود؛ در نتیجه راه طولانی‌تری رفتیم."},
        ],
        "exercises": [
            ex("Because the shop was shut, we ___ home. (main clause)", "went",
               "The comma separates the opening clause from the main one.",
               "ویرگول جملهٔ آغازین را از جملهٔ اصلی جدا می‌کند."),
            ex("We stayed home because it ___ . (rain)", "rained",
               "No comma is needed when the clause comes second.",
               "وقتی جمله دوم بیاید ویرگول لازم نیست."),
            ex("The delay was long; ___ , we missed the connection. (result)", "consequently",
               "A transition follows a semicolon and takes a comma.",
               "واژهٔ گذار پس از نقطه‌ویرگول و با ویرگول می‌آید."),
        ],
        "exam": [
            q("Which sentence needs a comma?",
              ["Because it was late, we left.", "We left because it was late.",
               "We left because of the time."], "Because it was late, we left.",
              "The opening clause takes a comma after it.",
              "جملهٔ آغازین پس از خود ویرگول می‌گیرد."),
            q("A transition word such as however needs ___ before it.",
              ["a semicolon", "a comma", "nothing"], "a semicolon",
              "Two clauses joined by a transition take a semicolon.",
              "دو جمله با واژهٔ گذار نقطه‌ویرگول می‌گیرند."),
            q("Which sentence contains a comma splice?",
              ["It rained, we stayed in.", "It rained, so we stayed in.",
               "It rained; we stayed in."], "It rained, we stayed in.",
              "Two clauses joined by a comma alone.",
              "دو جمله تنها با ویرگول به هم پیوسته‌اند."),
        ],
    },
    {
        "section": "19-5",
        "title": "Such ... that and so ... that",
        "title_fa": "such ... that و so ... that",
        "use_en": "Both patterns lead to a result. So comes before an adjective or an adverb: the film was so long that we left early. Such comes before a noun phrase, with a or an when the noun is singular countable: it was such a long film that we left early. The that-clause names the result, and that can be dropped in speech.",
        "use_fa": "هر دو الگو به نتیجه می‌رسند. so پیش از صفت یا قید می‌آید: the film was so long that we left early. such پیش از عبارت اسمی می‌آید و با اسم مفرد قابل‌شمارش a یا an می‌گیرد: it was such a long film that we left early. جملهٔ that نتیجه را می‌گوید و در گفتار می‌تواند حذف شود.",
        "form_en": "so + adjective / adverb + that  ·  such + (a/an) + adjective + noun + that",
        "examples": [
            {"en": "The film was so long that we left early.",
             "fa": "فیلم چنان طولانی بود که زود بیرون آمدیم."},
            {"en": "It was such a long film that we left early.",
             "fa": "فیلم چنان طولانی بود که زود بیرون آمدیم."},
            {"en": "She spoke so quietly that nobody heard her.",
             "fa": "چنان آهسته حرف زد که هیچ‌کس نشنید."},
        ],
        "exercises": [
            ex("The box was ___ heavy that I could not lift it. (before an adjective)", "so",
               "An adjective after the intensifier takes so.",
               "صفت پس از تشدیدکننده so می‌گیرد."),
            ex("It was ___ a good film that we watched it twice. (before a noun phrase)", "such",
               "A noun phrase with an article takes such.",
               "عبارت اسمی با حرف تعریف such می‌گیرد."),
            ex("They had ___ terrible weather that the trip was cancelled. (uncountable)", "such",
               "Uncountable nouns take such without an article.",
               "اسم غیرقابل‌شمارش such بی حرف تعریف می‌گیرد."),
        ],
        "exam": [
            q("The coffee was ___ hot that I burned my tongue.",
              ["so", "such", "very"], "so",
              "An adjective takes so before that.",
              "صفت پیش از that با so می‌آید."),
            q("It was ___ an interesting book that I finished it in a day.",
              ["such", "so", "too"], "such",
              "A singular countable noun takes such an.",
              "اسم مفرد قابل‌شمارش such an می‌گیرد."),
            q("Which sentence is correct?",
              ["She is so kind that everyone likes her.", "She is such kind that everyone likes her.",
               "She is so a kind person that everyone likes her."],
              "She is so kind that everyone likes her.",
              "So goes before the adjective, with no article.",
              "so پیش از صفت می‌آید و حرف تعریف ندارد."),
        ],
    },
    {
        "section": "19-6",
        "title": "Purpose with so that",
        "title_fa": "هدف با so that",
        "use_en": "So that introduces the purpose of an action and takes a clause, usually with can, could, will or would: I left early so that I could catch the train. In speech that is often dropped, leaving so. In order that is the formal version. The purpose clause looks forward, so a past main verb usually brings could or would into the purpose.",
        "use_fa": "so that هدف یک کار را می‌آورد و جمله می‌گیرد، معمولاً با can، could، will یا would: I left early so that I could catch the train. در گفتار that اغلب حذف می‌شود و so می‌ماند. in order that شکل رسمی است. جملهٔ هدف به آینده نگاه می‌کند، پس فعل اصلی گذشته معمولاً could یا would را به جملهٔ هدف می‌آورد.",
        "form_en": "so that + subject + can / could / will / would + verb",
        "examples": [
            {"en": "I left early so that I could catch the train.",
             "fa": "زود رفتم تا به قطار برسم."},
            {"en": "She spoke slowly so that everyone could understand.",
             "fa": "آهسته حرف زد تا همه بفهمند."},
            {"en": "We saved money so that we would be ready.",
             "fa": "پول جمع کردیم تا آماده باشیم."},
        ],
        "exercises": [
            ex("He whispered so that nobody ___ hear. (past ability)", "could",
               "A past purpose takes could.",
               "هدف گذشته could می‌گیرد."),
            ex("I will write it down so that I ___ forget. (negative, future)", "won't",
               "A future purpose can take will not.",
               "هدف آینده می‌تواند will not بگیرد."),
            ex("She studies hard so ___ she can pass. (purpose)", "that",
               "So that introduces the purpose clause.",
               "so that جملهٔ هدف را می‌آورد."),
        ],
        "exam": [
            q("He locked the door so that nobody ___ enter.",
              ["could", "can to", "would to"], "could",
              "A past main verb takes could in the purpose.",
              "فعل اصلی گذشته در هدف could می‌گیرد."),
            q("Which phrase introduces a purpose clause?",
              ["so that", "so", "such that"], "so that",
              "The clause form is so that.",
              "شکل جمله‌ای so that است."),
            q("We moved closer ___ we could see better.",
              ["so that", "because of", "although"], "so that",
              "Purpose takes so that.",
              "هدف so that می‌گیرد."),
        ],
    },
    {
        "section": "19-7",
        "title": "Contrast with an unexpected result: although, though, even though",
        "title_fa": "تضاد با نتیجهٔ غیرمنتظره: although، though، even though",
        "use_en": "These subordinators present a fact that makes the main clause surprising, and they work inside one sentence: although the team played well, they lost. Even though is the strongest. Despite and in spite of carry the same contrast but take a noun: despite playing well. A sentence cannot use although and but together, which is the error to watch for.",
        "use_fa": "این حروف ربط واقعیتی را می‌آورند که جملهٔ اصلی را غافلگیرکننده می‌کند و درون یک جمله کار می‌کنند: although the team played well, they lost. even though قوی‌ترین است. despite و in spite of همین تضاد را دارند اما اسم می‌گیرند: despite playing well. یک جمله نمی‌تواند although و but را با هم داشته باشد و این خطایی است که باید مراقبش بود.",
        "form_en": "although / even though + clause  ·  despite / in spite of + noun or -ing",
        "examples": [
            {"en": "Although the team played well, they lost.",
             "fa": "با اینکه تیم خوب بازی کرد، باخت."},
            {"en": "Even though he was injured, he finished the race.",
             "fa": "حتی با اینکه مصدوم بود مسابقه را تمام کرد."},
            {"en": "Despite playing well, they lost.",
             "fa": "با وجود بازی خوب، باختند."},
        ],
        "exercises": [
            ex("___ the weather was bad, we enjoyed the trip. (contrast)", "Although",
               "A clause of unexpected result takes although.",
               "جملهٔ نتیجهٔ غیرمنتظره although می‌گیرد."),
            ex("___ the bad weather, we enjoyed the trip. (before a noun)", "Despite",
               "A noun phrase takes despite.",
               "عبارت اسمی despite می‌گیرد."),
            ex("___ though she was tired, she kept working. (strongest form)", "Even",
               "Even though is the strongest contrast.",
               "even though قوی‌ترین تضاد است."),
        ],
        "exam": [
            q("___ it was expensive, they bought the house.",
              ["Although", "Despite", "Because of"], "Although",
              "A clause needs although.",
              "جمله although می‌خواهد."),
            q("Which sentence is wrong?",
              ["Although it was late, but we continued.", "Although it was late, we continued.",
               "Despite the hour, we continued."], "Although it was late, but we continued.",
              "Although and but cannot share a sentence.",
              "although و but در یک جمله نمی‌آیند."),
            q("___ the noise, she kept reading.",
              ["Despite", "Although", "Even though"], "Despite",
              "A noun after the contrast takes despite.",
              "اسم پس از تضاد despite می‌گیرد."),
        ],
    },
    {
        "section": "19-8",
        "title": "Direct contrast: while, whereas, in contrast",
        "title_fa": "تضاد مستقیم: while، whereas، in contrast",
        "use_en": "A direct contrast places two facts side by side without saying either is surprising. While and whereas join clauses: while the north is wet, the south is dry. In contrast and on the other hand are transitions and need a semicolon or a full stop before them. These connectives compare; the unexpected-result group argues.",
        "use_fa": "تضاد مستقیم دو واقعیت را کنار هم می‌گذارد بی‌آنکه یکی را غافلگیرکننده بخواند. while و whereas جمله‌ها را به هم می‌پیوندند: while the north is wet, the south is dry. in contrast و on the other hand واژهٔ گذارند و پیش از خود نقطه‌ویرگول یا نقطه می‌خواهند. این‌ها مقایسه می‌کنند و گروه نتیجهٔ غیرمنتظره استدلال.",
        "form_en": "clause + while / whereas + clause  ·  clause; in contrast, + clause",
        "examples": [
            {"en": "While the north is wet, the south is dry.",
             "fa": "شمال پرباران است، در حالی که جنوب خشک است."},
            {"en": "Whereas the first plan was cheap, the second was safe.",
             "fa": "در حالی که طرح اول ارزان بود، دومی ایمن بود."},
            {"en": "The city is crowded; in contrast, the village is quiet.",
             "fa": "شهر شلوغ است؛ در مقابل، روستا آرام است."},
        ],
        "exercises": [
            ex("The first option is cheap, ___ the second is reliable. (direct contrast)", "whereas",
               "Whereas marks a formal direct contrast.",
               "whereas تضاد مستقیم رسمی را نشان می‌دهد."),
            ex("___ trains are fast, buses are cheaper. (contrast)", "While",
               "While places two facts side by side.",
               "while دو واقعیت را کنار هم می‌گذارد."),
            ex("Sales rose in June; ___ contrast, they fell in July. (transition)", "in",
               "The fixed transition is in contrast.",
               "واژهٔ گذار ثابت in contrast است."),
        ],
        "exam": [
            q("___ the old system was slow, the new one is quick.",
              ["Whereas", "Because of", "So that"], "Whereas",
              "A direct contrast between clauses takes whereas.",
              "تضاد مستقیم میان دو جمله whereas می‌گیرد."),
            q("Which connective needs a semicolon before it?",
              ["in contrast", "while", "whereas"], "in contrast",
              "A transition word joins sentences, not clauses with a comma.",
              "واژهٔ گذار جمله‌ها را به هم می‌پیوندد نه جمله‌واره‌ها با ویرگول."),
            q("Which sentence is correct?",
              ["While he plays tennis, she plays golf.", "While he plays tennis, but she plays golf.",
               "While he plays tennis; she plays golf."], "While he plays tennis, she plays golf.",
              "While joins two clauses with a comma.",
              "while دو جمله را با ویرگول به هم می‌پیوندد."),
        ],
    },
    {
        "section": "19-9",
        "title": "Conditions with otherwise and or else",
        "title_fa": "شرط با otherwise و or else",
        "use_en": "Otherwise says what happens if a condition is not met: leave now, otherwise you will miss the train. Or else says the same thing and is more conversational, sometimes with a warning tone. Both join two clauses and take a comma before them. They are the negative side of a condition, so the second clause names the bad result of not acting.",
        "use_fa": "otherwise می‌گوید اگر شرط برآورده نشود چه می‌شود: leave now, otherwise you will miss the train. or else همین را می‌گوید و گفتاری‌تر است و گاه لحن هشدار دارد. هر دو دو جمله را به هم می‌پیوندند و پیش از خود ویرگول می‌گیرند. این‌ها سوی منفی شرط‌اند، پس جملهٔ دوم نتیجهٔ بدِ عمل نکردن را می‌گوید.",
        "form_en": "imperative or clause, + otherwise / or else + clause",
        "examples": [
            {"en": "Leave now, otherwise you will miss the train.",
             "fa": "الان راه بیفت، وگرنه قطار را از دست می‌دهی."},
            {"en": "Write it down, or else you will forget.",
             "fa": "یادداشتش کن، وگرنه فراموش می‌کنی."},
            {"en": "We must book early; otherwise, there will be no seats.",
             "fa": "باید زود رزرو کنیم؛ وگرنه صندلی نخواهد بود."},
        ],
        "exercises": [
            ex("Hurry up, ___ we will be late. (negative condition)", "otherwise",
               "Otherwise names the result of not acting.",
               "otherwise نتیجهٔ عمل نکردن را می‌گوید."),
            ex("Take a coat, ___ else you will be cold. (conversational)", "or",
               "The conversational pair is or else.",
               "جفت گفتاری or else است."),
            ex("Study tonight; ___ , you will fail. (negative condition)", "otherwise",
               "Otherwise follows a semicolon and takes a comma.",
               "otherwise پس از نقطه‌ویرگول و با ویرگول می‌آید."),
        ],
        "exam": [
            q("Leave now, ___ you will miss the bus.",
              ["otherwise", "because", "so that"], "otherwise",
              "The bad result of not acting takes otherwise.",
              "نتیجهٔ بدِ عمل نکردن otherwise می‌گیرد."),
            q("Which phrase is the conversational form?",
              ["or else", "other wise", "otherwise that"], "or else",
              "Or else is the informal pair.",
              "or else جفت غیررسمی است."),
            q("Book the tickets today; ___, they will be sold out.",
              ["otherwise", "although", "despite"], "otherwise",
              "A negative condition after a semicolon takes otherwise.",
              "شرط منفی پس از نقطه‌ویرگول otherwise می‌گیرد."),
        ],
    },
]


def main() -> int:
    data = json.loads(BOOKS.read_text(encoding="utf-8"))
    book = next(b for b in data["books"] if b.get("kind") == "grammar")

    old = [l for l in book["lessons"] if l.get("chapter") == CHAPTER]
    assert old, "chapter nineteen is not in the book"

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
    print(f"chapter nineteen: {len(LESSONS)} charts, {size} structures in the book")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
