#!/usr/bin/env python3
"""Write chapter twelve of the grammar book into books.json.

    python3 tools/chapter12.py

Chapter twelve of *Understanding and Using English Grammar* is Noun Clauses.
The book shipped with two placeholder sections for it; this replaces them with
the chapter's nine charts, written out like chapters three to eleven: the rule,
the form, examples in both languages, three guided exercises and a three-question
check for each.

The sentences and explanations are written for this app. The book is the
reference text, and nothing in this file is transcribed from it.

It is idempotent: chapter twelve is always rebuilt from this script.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "books.json"

CHAPTER = "Chapter 12"


def ex(prompt, answer, why_en, why_fa):
    return {"prompt": prompt, "answer": answer, "why_en": why_en, "why_fa": why_fa}


def q(text, options, answer, why_en, why_fa):
    assert answer in options and len(options) == 3, text
    return {"q": text, "options": options, "answer": answer,
            "why_en": why_en, "why_fa": why_fa}


LESSONS = [
    {
        "section": "12-1",
        "title": "Noun clauses: a sentence inside a sentence",
        "title_fa": "جمله‌های اسمی: جمله‌ای درون جمله",
        "use_en": "A noun clause does the work of a noun: it can be the subject, the object of a verb, the object of a preposition or the complement after be. What makes it a clause is that it keeps its own subject and verb. Inside the clause the word order is the order of a statement, not of a question, and there is no do or did: I know where she lives, never I know where does she live.",
        "use_fa": "جملهٔ اسمی کار اسم را می‌کند: می‌تواند فاعل، مفعول فعل، مفعول حرف اضافه یا متمم پس از be باشد. چیزی که آن را جمله می‌کند داشتن فاعل و فعل خودش است. درون جمله، ترتیب واژه‌ها ترتیب جملهٔ خبری است نه پرسشی، و do یا did نمی‌آید: I know where she lives و هرگز I know where does she live.",
        "form_en": "noun clause = question word + subject + verb (statement order, no do/did)",
        "examples": [
            {"en": "What he said was true.",
             "fa": "آنچه گفت درست بود."},
            {"en": "I know where she lives.",
             "fa": "می‌دانم کجا زندگی می‌کند."},
            {"en": "The problem is that we are late.",
             "fa": "مشکل این است که دیر کرده‌ایم."},
        ],
        "exercises": [
            ex("___ she said surprised everyone. (the thing)", "What",
               "A clause used as the subject can begin with what.",
               "جمله‌ای که فاعل است می‌تواند با what شروع شود."),
            ex("I don't know ___ he is coming or not. (two choices)", "whether",
               "Two possibilities are joined by whether.",
               "دو احتمال با whether به هم می‌پیوندند."),
            ex("The truth is ___ we tried our best.", "that",
               "A clause after be can begin with that.",
               "جملهٔ پس از be می‌تواند با that شروع شود."),
        ],
        "exam": [
            q("Which sentence keeps statement order in the clause?",
              ["I know where he went.", "I know where did he go.",
               "I know where went he."], "I know where he went.",
              "A noun clause has no do and no inversion.",
              "جملهٔ اسمی do و جابه‌جایی ندارد."),
            q("___ she told me was a surprise.",
              ["What", "That", "Which"], "What",
              "The clause is the subject and means the thing.",
              "جمله فاعل است و معنای «آنچه» دارد."),
            q("Nobody knows ___ the train leaves.",
              ["when", "when does", "when do"], "when",
              "After a question word the subject comes before the verb.",
              "پس از واژهٔ پرسشی فاعل پیش از فعل می‌آید."),
        ],
    },
    {
        "section": "12-2",
        "title": "Noun clauses with question words",
        "title_fa": "جمله‌های اسمی با واژه‌های پرسشی",
        "use_en": "The question words that open a noun clause are the same ones that open a question: what, who, whom, whose, which, when, where, why, how, how much and how many. The clause takes the place of the answer, so the question disappears: where did he go becomes I don't remember where he went. Who as the subject of the clause is not changed to whom, and the verb after it agrees with the answer, not with who.",
        "use_fa": "واژه‌های پرسشی که جملهٔ اسمی را باز می‌کنند همان‌هایی هستند که پرسش را باز می‌کنند: what، who، whom، whose، which، when، where، why، how، how much و how many. جمله جای پاسخ را می‌گیرد، پس پرسش ناپدید می‌شود: where did he go به I don't remember where he went تبدیل می‌شود. who اگر فاعل جمله باشد به whom تبدیل نمی‌شود و فعل پس از آن با پاسخ مطابقت می‌کند نه با who.",
        "form_en": "question word + subject + verb  ·  who + plural verb when the answer is plural",
        "examples": [
            {"en": "I don't remember where he went.",
             "fa": "یادم نیست کجا رفت."},
            {"en": "Tell me what you need.",
             "fa": "بگو چه لازم داری."},
            {"en": "She asked who was at the door.",
             "fa": "پرسید چه کسی پشت در بود."},
        ],
        "exercises": [
            ex("Do you know ___ the meeting starts? (time)", "when",
               "A time question becomes a when clause.",
               "پرسش زمان به جملهٔ when تبدیل می‌شود."),
            ex("I can't imagine ___ he did it. (reason)", "why",
               "A reason question becomes a why clause.",
               "پرسش دلیل به جملهٔ why تبدیل می‌شود."),
            ex("She asked ___ was calling. (person as subject)", "who",
               "The subject of the clause stays who.",
               "فاعل جمله who می‌ماند."),
        ],
        "exam": [
            q("I don't know ___.",
              ["where she works", "where does she work", "where works she"],
              "where she works",
              "Statement order follows the question word.",
              "پس از واژهٔ پرسشی ترتیب خبری می‌آید."),
            q("He asked me ___ I wanted.",
              ["what", "what did", "that what"], "what",
              "One question word opens the clause; did disappears.",
              "یک واژهٔ پرسشی جمله را باز می‌کند و did حذف می‌شود."),
            q("Nobody told us ___ the tickets cost.",
              ["how much", "how many", "how"], "how much",
              "Cost is uncountable, so how much.",
              "cost غیرقابل‌شمارش است، پس how much."),
        ],
    },
    {
        "section": "12-3",
        "title": "Noun clauses with whether or if",
        "title_fa": "جمله‌های اسمی با whether و if",
        "use_en": "A yes-or-no question becomes a clause with whether or if: is he coming becomes I wonder whether he is coming. Whether is the safer choice in writing, and it is the only one that can take or not, can be followed by an infinitive, and can follow a preposition. If belongs to speech and to the middle of a sentence, never to the subject position.",
        "use_fa": "پرسش بله‌یا‌خیر به جمله‌ای با whether یا if تبدیل می‌شود: is he coming به I wonder whether he is coming. whether در نوشتار انتخاب مطمئن‌تر است و تنها گزینه‌ای است که or not می‌گیرد، می‌تواند پیش از مصدر بیاید و پس از حرف اضافه قرار گیرد. if به گفتار و میان جمله تعلق دارد و هرگز در جایگاه فاعل نمی‌آید.",
        "form_en": "whether / if + subject + verb  ·  whether + to + verb  ·  whether ... or not",
        "examples": [
            {"en": "I wonder whether he is coming.",
             "fa": "نمی‌دانم آیا می‌آید."},
            {"en": "She hasn't decided whether to accept the offer.",
             "fa": "تصمیم نگرفته است که پیشنهاد را بپذیرد یا نه."},
            {"en": "We talked about whether the plan would work.",
             "fa": "دربارهٔ اینکه آیا طرح کار می‌کند صحبت کردیم."},
        ],
        "exercises": [
            ex("I don't know ___ or not she passed. (formal)", "whether",
               "Or not is possible only after whether.",
               "or not تنها پس از whether می‌آید."),
            ex("He asked ___ I had finished. (yes or no, speech)", "if",
               "If introduces a yes-or-no clause in speech.",
               "if در گفتار جملهٔ بله‌یا‌خیر را می‌آورد."),
            ex("___ to go or stay is the question. (subject position)", "Whether",
               "In the subject position only whether works.",
               "در جایگاه فاعل تنها whether کار می‌کند."),
        ],
        "exam": [
            q("___ she will come is still unclear.",
              ["Whether", "If", "That"], "Whether",
              "A yes-or-no clause as the subject takes whether.",
              "جملهٔ بله‌یا‌خیر در جایگاه فاعل whether می‌گیرد."),
            q("I asked him ___ he had a minute.",
              ["if", "whether or", "that"], "if",
              "Yes-or-no in speech takes if.",
              "بله‌یا‌خیر در گفتار if می‌گیرد."),
            q("We discussed ___ to change the date.",
              ["whether", "if", "that"], "whether",
              "Only whether can be followed by an infinitive.",
              "تنها whether می‌تواند مصدر بگیرد."),
        ],
    },
    {
        "section": "12-4",
        "title": "Question words followed by infinitives",
        "title_fa": "واژه‌های پرسشی پیش از مصدر",
        "use_en": "A question word and an infinitive can replace a whole clause and shorten it: I don't know what I should do becomes I don't know what to do. The infinitive follows what, who, whom, which, when, where, how and whether, and it carries the idea of should or could. The pattern is common after know, decide, ask, tell, explain, learn and wonder.",
        "use_fa": "واژهٔ پرسشی و مصدر می‌توانند جای تمام جمله را بگیرند و آن را کوتاه کنند: I don't know what I should do به I don't know what to do تبدیل می‌شود. مصدر پس از what، who، whom، which، when، where، how و whether می‌آید و ایدهٔ should یا could را با خود دارد. این الگو پس از know، decide، ask، tell، explain، learn و wonder رایج است.",
        "form_en": "question word + to + base verb  ·  whether + to + base verb",
        "examples": [
            {"en": "I don't know what to do next.",
             "fa": "نمی‌دانم بعد چه کنم."},
            {"en": "Could you tell me how to get to the station?",
             "fa": "می‌گویید چطور به ایستگاه بروم؟"},
            {"en": "She asked where to sit.",
             "fa": "پرسید کجا بنشیند."},
        ],
        "exercises": [
            ex("I don't know ___ to say. (the thing)", "what",
               "The thing to say is what plus an infinitive.",
               "چیزی که باید گفت what و مصدر است."),
            ex("He showed me how ___ open the box.", "to",
               "The infinitive marker follows the question word.",
               "نشانهٔ مصدر پس از واژهٔ پرسشی می‌آید."),
            ex("We couldn't decide whether ___ wait.", "to",
               "Whether plus to plus base verb keeps the choice open.",
               "whether و to و فعل ساده انتخاب را باز نگه می‌دارد."),
        ],
        "exam": [
            q("She asked me ___ to use the machine.",
              ["how", "how to", "what"], "how",
              "One question word, then the infinitive with to.",
              "یک واژهٔ پرسشی و سپس مصدر با to."),
            q("I don't know ___ to invite.",
              ["who", "whose", "which to"], "who",
              "The person is asked for with who plus an infinitive.",
              "شخص با who و مصدر پرسیده می‌شود."),
            q("We need to decide ___ to leave or stay.",
              ["whether", "if", "that"], "whether",
              "Before an infinitive only whether works.",
              "پیش از مصدر تنها whether کار می‌کند."),
        ],
    },
    {
        "section": "12-5",
        "title": "Noun clauses with that",
        "title_fa": "جمله‌های اسمی با that",
        "use_en": "A statement can become a clause with that: he is right becomes I think that he is right. After think, say, believe, hope, know and guess, that is usually dropped in speech, and keeping it makes the sentence a little more formal. A that clause as the subject is heavy, so English moves it to the end and puts it in front: it is clear that he tried. The fact that is the phrase that keeps a subject clause in place.",
        "use_fa": "جملهٔ خبری می‌تواند با that به جملهٔ اسمی تبدیل شود: he is right به I think that he is right. پس از think، say، believe، hope، know و guess، that در گفتار معمولاً حذف می‌شود و نگه داشتنش جمله را کمی رسمی‌تر می‌کند. جملهٔ that در جایگاه فاعل سنگین است، پس انگلیسی آن را به پایان می‌برد و it را اول می‌آورد: it is clear that he tried. عبارت the fact that فاعل را سر جای خود نگه می‌دارد.",
        "form_en": "that + subject + verb  ·  it + be + adjective + that clause  ·  the fact that + clause",
        "examples": [
            {"en": "I think that he is right.",
             "fa": "فکر می‌کنم که او درست می‌گوید."},
            {"en": "It is clear that she tried her best.",
             "fa": "روشن است که او نهایت تلاشش را کرد."},
            {"en": "The fact that they agreed surprised me.",
             "fa": "اینکه آن‌ها موافقت کردند مرا غافلگیر کرد."},
        ],
        "exercises": [
            ex("I believe ___ she is honest.", "that",
               "That introduces the statement after believe.",
               "that جملهٔ خبری را پس از believe می‌آورد."),
            ex("It is obvious ___ he needs help.", "that",
               "The clause moves to the end after it is obvious.",
               "جمله پس از it is obvious به پایان می‌رود."),
            ex("The fact ___ we finished early helped.", "that",
               "The fact that keeps the clause in the subject.",
               "the fact that جمله را در جایگاه فاعل نگه می‌دارد."),
        ],
        "exam": [
            q("Which sentence is the most formal?",
              ["I think that he is right.", "I think he's right.",
               "I think he right."], "I think that he is right.",
              "Keeping that makes a spoken sentence formal.",
              "نگه داشتن that جملهٔ گفتاری را رسمی می‌کند."),
            q("___ is important that everyone attends.",
              ["It", "That", "There"], "It",
              "A heavy that clause moves behind the empty it.",
              "جملهٔ سنگین that پس از it تهی می‌آید."),
            q("The news ___ she passed made us happy.",
              ["that", "what", "if"], "that",
              "A statement after the news takes that.",
              "جملهٔ خبری پس از the news با that می‌آید."),
        ],
    },
    {
        "section": "12-6",
        "title": "Quoted speech: the exact words",
        "title_fa": "نقل قول مستقیم: واژه‌های دقیق",
        "use_en": "Quoted speech repeats what someone said inside quotation marks, with no change to the words or the tense: she said, I am tired. A comma follows the reporting phrase, the first word of the quotation keeps its capital, and the period or question mark sits inside the closing mark. Tenses in the quotation are the tenses of the moment it was said.",
        "use_fa": "نقل قول مستقیم واژه‌های کسی را درون گیومه تکرار می‌کند، بدون تغییر واژه‌ها یا زمان: she said, I am tired. پس از عبارت نقل، ویرگول می‌آید، نخستین واژهٔ نقل حرف بزرگ دارد و نقطه یا علامت پرسش درون گیومهٔ پایانی می‌نشیند. زمان‌های درون نقل، زمان‌های لحظهٔ گفته شدن‌اند.",
        "form_en": "reporting phrase + comma + quoted words in quotation marks",
        "examples": [
            {"en": "She said, \"I am tired,\" and closed her eyes.",
             "fa": "او گفت: «خسته‌ام» و چشمانش را بست."},
            {"en": "\"Where are you going?\" he asked.",
             "fa": "«کجا می‌روی؟» پرسید."},
            {"en": "He said, \"I will call you tomorrow,\" and left.",
             "fa": "گفت: «فردا به تو زنگ می‌زنم» و رفت."},
        ],
        "exercises": [
            ex("She said, \"I ___ ready.\" (the exact words)", "am",
               "Quoted speech keeps the tense of the moment.",
               "نقل مستقیم زمان لحظهٔ گفته را نگه می‌دارد."),
            ex("He said, \"I ___ finish it today.\" (the exact words)", "will",
               "The quotation keeps will, not would.",
               "نقل will را نگه می‌دارد نه would."),
            ex("___ said, \"Come in.\" (reporting phrase)", "She",
               "A reporting phrase comes before the quotation.",
               "عبارت نقل پیش از نقل قول می‌آید."),
        ],
        "exam": [
            q("Which quotation is punctuated correctly?",
              ["She said, \"I am late.\"", "She said \"I am late\".",
               "She said, I am late."], "She said, \"I am late.\"",
              "Comma after the reporting phrase, marks around the words.",
              "ویرگول پس از عبارت نقل و گیومه گرد واژه‌ها."),
            q("\"Are you ready?\" she ___.",
              ["asked", "said", "told"], "asked",
              "A question in quotation marks goes with asked.",
              "پرسش در گیومه با asked می‌آید."),
            q("In quoted speech, the closing quotation mark comes ___ the period.",
              ["after", "before", "instead of"], "after",
              "The period sits inside the quotation mark, so the mark closes after it.",
              "نقطه درون گیومه می‌نشیند، پس گیومه پس از آن بسته می‌شود."),
        ],
    },
    {
        "section": "12-7",
        "title": "Reported speech: the words after the fact",
        "title_fa": "نقل قول غیرمستقیم: واژه‌ها پس از رویداد",
        "use_en": "Reported speech turns a quotation into a noun clause and moves the tense back: I am tired becomes she said she was tired; I saw him becomes she said she had seen him. Pronouns and time words move too, because the speaker is no longer the one talking: today becomes that day, here becomes there, this becomes that. Say takes a clause; tell needs a person first: she told me she was tired.",
        "use_fa": "نقل قول غیرمستقیم نقل را به جملهٔ اسمی تبدیل می‌کند و زمان را یک پله عقب می‌برد: I am tired به she said she was tired و I saw him به she said she had seen him تبدیل می‌شود. ضمیرها و واژه‌های زمان هم جابه‌جا می‌شوند، چون گوینده دیگر همان شخص نیست: today به that day، here به there و this به that. say جمله می‌گیرد و tell اول شخص: she told me she was tired.",
        "form_en": "say (that) + clause  ·  tell + person + (that) + clause  ·  one tense back",
        "examples": [
            {"en": "She said she was tired.",
             "fa": "گفت خسته است."},
            {"en": "He told me he had seen the film.",
             "fa": "به من گفت فیلم را دیده بود."},
            {"en": "They said they would arrive that evening.",
             "fa": "گفتند آن شب می‌رسند."},
        ],
        "exercises": [
            ex("Direct: I am busy. Reported: She said she ___ busy.", "was",
               "A present tense moves back one step after a past report.",
               "زمان حال پس از نقل گذشته یک پله عقب می‌رود."),
            ex("Direct: I saw him. Reported: She said she ___ seen him.", "had",
               "A simple past becomes the past perfect.",
               "گذشتهٔ ساده به گذشتهٔ کامل تبدیل می‌شود."),
            ex("He ___ me he was leaving. (a person follows)", "told",
               "Tell takes the listener before the clause.",
               "tell شنونده را پیش از جمله می‌گیرد."),
        ],
        "exam": [
            q("She said she ___ finish the report.",
              ["would", "will", "would have"], "would",
              "Will becomes would in a past report.",
              "will در نقل گذشته would می‌شود."),
            q("He ___ me he had lost the keys.",
              ["told", "said", "spoke"], "told",
              "Tell needs the person it was said to.",
              "tell شخصی را که به او گفته شد لازم دارد."),
            q("Direct: I will call today. Reported: He said he would call ___.",
              ["that day", "today", "this day"], "that day",
              "Today becomes that day when the day has passed.",
              "today وقتی آن روز گذشته باشد that day می‌شود."),
        ],
    },
    {
        "section": "12-8",
        "title": "Reported speech: modal verbs in noun clauses",
        "title_fa": "نقل قول غیرمستقیم: افعال وجهی در جمله‌های اسمی",
        "use_en": "Modals move back in a report the same way tenses do: will becomes would, can becomes could, may becomes might, and must usually becomes had to. Should, could, would, might and ought to have no past form, so they stay as they are. The change happens because the report sits in the past, not because the modal means something different.",
        "use_fa": "افعال وجهی در نقل قول مانند زمان‌ها عقب می‌روند: will به would، can به could، may به might و must معمولاً به had to تبدیل می‌شود. should، could، would، might و ought to شکل گذشته ندارند، پس همان‌گونه می‌مانند. این تغییر از آن روست که نقل در گذشته نشسته است، نه از آن رو که وجهی معنای دیگری یافته.",
        "form_en": "will → would · can → could · may → might · must → had to · should / could / would stay",
        "examples": [
            {"en": "She said she could swim.",
             "fa": "گفت می‌تواند شنا کند."},
            {"en": "He said he had to leave early.",
             "fa": "گفت باید زود برود."},
            {"en": "They said we should wait.",
             "fa": "گفتند باید صبر کنیم."},
        ],
        "exercises": [
            ex("Direct: I can help. Reported: She said she ___ help.", "could",
               "Can moves back to could.",
               "can به could عقب می‌رود."),
            ex("Direct: You must wait. Reported: He said I ___ wait.", "had to",
               "Must usually becomes had to in a report.",
               "must در نقل معمولاً had to می‌شود."),
            ex("Direct: I might come. Reported: She said she ___ come.", "might",
               "Might has no past form and stays.",
               "might شکل گذشته ندارد و می‌ماند."),
        ],
        "exam": [
            q("Direct: I will be late. Reported: He said he ___ be late.",
              ["would", "will", "would have"], "would",
              "Will becomes would after a past report.",
              "will پس از نقل گذشته would می‌شود."),
            q("Direct: You should rest. Reported: She said I ___ rest.",
              ["should", "shall", "should have"], "should",
              "Should has no past form, so it stays.",
              "should شکل گذشته ندارد، پس می‌ماند."),
            q("Direct: I may move. Reported: He said he ___ move.",
              ["might", "may", "must"], "might",
              "May becomes might in reported speech.",
              "may در نقل غیرمستقیم might می‌شود."),
        ],
    },
    {
        "section": "12-9",
        "title": "The subjunctive in noun clauses: insist that he be",
        "title_fa": "وجه شرطی در جمله‌های اسمی: insist that he be",
        "use_en": "After a small group of verbs that push for something, the clause takes the base form of the verb for every subject: the doctor insisted that he rest, the board recommended that she be hired. The verbs are insist, demand, request, recommend, suggest, propose, ask and require. The same base form follows adjectives of importance: it is essential that he be told. In speech a should often replaces it.",
        "use_fa": "پس از گروه کوچکی از فعل‌ها که چیزی را می‌خواهند، جمله برای هر فاعلی شکل سادهٔ فعل می‌گیرد: the doctor insisted that he rest، the board recommended that she be hired. این فعل‌ها insist، demand، request، recommend، suggest، propose، ask و require هستند. همین شکل ساده پس از صفت‌های اهمیت می‌آید: it is essential that he be told. در گفتار often should جای آن را می‌گیرد.",
        "form_en": "insist / demand / recommend / request + that + subject + base verb (no -s, no was)",
        "examples": [
            {"en": "The doctor insisted that he rest for a week.",
             "fa": "پزشک اصرار کرد که یک هفته استراحت کند."},
            {"en": "They recommended that she be hired.",
             "fa": "توصیه کردند که او استخدام شود."},
            {"en": "It is essential that everyone be present.",
             "fa": "ضروری است که همه حاضر باشند."},
        ],
        "exercises": [
            ex("She insisted that he ___ the truth. (be, base form)", "tell",
               "The subjunctive uses the base verb with every subject.",
               "وجه شرطی با هر فاعلی فعل ساده می‌گیرد."),
            ex("The board recommended that she ___ appointed.", "be",
               "The passive subjunctive is be plus the participle.",
               "وجه شرطی مجهول be و اسم مفعول است."),
            ex("It is important that he ___ on time. (base form)", "arrive",
               "Adjectives of importance also take the base form.",
               "صفت‌های اهمیت هم فعل ساده می‌گیرند."),
        ],
        "exam": [
            q("They demanded that the report ___ by Friday.",
              ["be finished", "is finished", "was finished"], "be finished",
              "Demand takes that plus the base form, here passive.",
              "demand جمله با فعل ساده می‌گیرد، اینجا مجهول."),
            q("The teacher suggested that he ___ more.",
              ["practise", "practises", "practised"], "practise",
              "No -s in the subjunctive, even with he.",
              "در وجه شرطی حتی با he هیچ s- نمی‌آید."),
            q("It is necessary that she ___ informed.",
              ["be", "is", "was"], "be",
              "Necessary that takes the base form be.",
              "necessary that شکل سادهٔ be می‌گیرد."),
        ],
    },
]


def main() -> int:
    data = json.loads(BOOKS.read_text(encoding="utf-8"))
    book = next(b for b in data["books"] if b.get("kind") == "grammar")

    old = [l for l in book["lessons"] if l.get("chapter") == CHAPTER]
    assert old, "chapter twelve is not in the book"

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
    print(f"chapter twelve: {len(LESSONS)} charts, {size} structures in the book")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
