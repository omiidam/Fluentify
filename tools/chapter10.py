#!/usr/bin/env python3
"""Write chapter ten of the grammar book into books.json.

    python3 tools/chapter10.py

Chapter ten of *Understanding and Using English Grammar* is Modals, Part 2.
The book shipped with one section for it; this replaces it with the chapter's
eleven charts, written out like chapters one to nine: the rule, the form,
examples in both languages, three guided exercises and a three-question check
for each.

The sentences and explanations are written for this app. The book is the
reference text, and nothing in this file is transcribed from it.

It is idempotent: chapter ten is always rebuilt from this script.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "books.json"

CHAPTER = "Chapter 10"


def ex(prompt, answer, why_en, why_fa):
    return {"prompt": prompt, "answer": answer, "why_en": why_en, "why_fa": why_fa}


def q(text, options, answer, why_en, why_fa):
    assert answer in options and len(options) == 3, text
    return {"q": text, "options": options, "answer": answer,
            "why_en": why_en, "why_fa": why_fa}


LESSONS = [
    {
        "section": "10-1",
        "title": "Would for a repeated action in the past",
        "title_fa": "would برای کار تکرارشده در گذشته",
        "use_en": "Would can report a habit in the past, and it works much like used to: every summer we would drive to the coast. Both describe repeated actions rather than single events. Would cannot describe a past state, so a sentence about living somewhere or owning something takes used to instead: he used to live by the sea, never he would live by the sea.",
        "use_fa": "would می‌تواند عادتی در گذشته را بازگو کند و تقریباً مانند used to کار می‌کند: every summer we would drive to the coast. هر دو کار تکرارشده را می‌گویند نه یک رویداد تنها. would نمی‌تواند وضعیت گذشته را بیان کند، پس جمله‌ای دربارهٔ زندگی کردن در جایی یا داشتن چیزی used to می‌گیرد: he used to live by the sea و هرگز he would live by the sea.",
        "form_en": "subject + would + base verb (repeated past action)  ·  used to + base verb (repeated action or past state)",
        "examples": [
            {"en": "When I was a child, my grandmother would read to me every night.",
             "fa": "وقتی کودک بودم، مادربزرگم هر شب برایم کتاب می‌خواند."},
            {"en": "We would often walk to school together.",
             "fa": "ما اغلب با هم پیاده به مدرسه می‌رفتیم."},
            {"en": "He used to live in Shiraz before he moved here.",
             "fa": "او پیش از آمدن به اینجا در شیراز زندگی می‌کرد."},
        ],
        "exercises": [
            ex("Every winter my father ___ take us to the mountains.", "would",
               "A repeated past action takes would plus the base verb.",
               "کار تکرارشدهٔ گذشته would و فعل ساده می‌گیرد."),
            ex("She ___ to play the violin when she was young.", "used",
               "The past habit phrase that needs to is used to.",
               "عبارت عادت گذشته که to لازم دارد used to است."),
            ex("In those years we ___ meet at the same café every Friday.", "would",
               "A weekly habit in the past is natural with would.",
               "عادت هفتگی در گذشته با would طبیعی است."),
        ],
        "exam": [
            q("As a boy, he ___ swim in the river every morning.",
              ["would", "will", "must"], "would",
              "A repeated past action takes would.",
              "کار تکرارشدهٔ گذشته would می‌گیرد."),
            q("They ___ to own a small shop in the old town.",
              ["used", "would", "were"], "used",
              "Owning something is a state, so used to is needed.",
              "داشتن چیزی وضعیت است، پس used to لازم است."),
            q("We ___ spend every summer at my aunt's house.",
              ["would", "are", "have"], "would",
              "A summer habit in the past takes would.",
              "عادت تابستانی گذشته would می‌گیرد."),
        ],
    },
    {
        "section": "10-2",
        "title": "The past of necessity, advice and expectation",
        "title_fa": "گذشتهٔ ضرورت، توصیه و انتظار",
        "use_en": "Must has no past form, so had to carries necessity into the past. Should have with a past participle looks back at advice that was not followed and usually carries regret, and ought to have works the same way. Was supposed to reports an arrangement that did not happen. In all three the modal is followed by the perfect form, because the missed action sits before now.",
        "use_fa": "must شکل گذشته ندارد، پس had to ضرورت را به گذشته می‌برد. should have به‌همراه اسم مفعول به توصیه‌ای نگاه می‌کند که اجرا نشد و معمولاً پشیمانی دارد، و ought to have همین کار را می‌کند. was supposed to قرار و ترتیبی را بیان می‌کند که انجام نشد. در هر سه، فعل وجهی با شکل کامل می‌آید چون کار انجام‌نشده پیش از اکنون جای دارد.",
        "form_en": "had to + base verb  ·  should / ought to have + past participle  ·  was / were supposed to + base verb",
        "examples": [
            {"en": "I had to work late every night last week.",
             "fa": "هفتهٔ گذشته هر شب مجبور بودم تا دیروقت کار کنم."},
            {"en": "You should have told me about the meeting.",
             "fa": "باید دربارهٔ جلسه به من می‌گفتی."},
            {"en": "We were supposed to leave at seven, but the car would not start.",
             "fa": "قرار بود ساعت هفت راه بیفتیم، اما ماشین روشن نشد."},
        ],
        "exercises": [
            ex("I ___ to take two buses to get to work last year.", "had",
               "Past necessity is had to, never musted.",
               "ضرورت گذشته had to است و هرگز musted."),
            ex("You ___ have called me; I was worried.", "should",
               "Advice about a missed action takes should have.",
               "توصیه دربارهٔ کار انجام‌نشده should have می‌گیرد."),
            ex("They ___ supposed to arrive before noon.", "were",
               "The plural subject they takes were supposed to.",
               "فاعل جمع they با were supposed to می‌آید."),
        ],
        "exam": [
            q("She ___ to study all weekend for the exam.",
              ["had", "must", "has"], "had",
              "Must has no past form, so had to.",
              "must گذشته ندارد، پس had to."),
            q("He ___ have asked for help sooner.",
              ["should", "shall", "shouldn't"], "should",
              "The missed advice is should have.",
              "توصیهٔ اجرانشده should have است."),
            q("We ___ supposed to meet at the library.",
              ["were", "was", "are"], "were",
              "The plural we takes were.",
              "we جمع است و were می‌گیرد."),
        ],
    },
    {
        "section": "10-3",
        "title": "Past ability: could, was able to, managed to",
        "title_fa": "توانایی در گذشته: could، was able to، managed to",
        "use_en": "Could is the past of can for a general ability: she could read music at four. For one success on one occasion, was able to or managed to is clearer, because could would say only that the ability existed. In the negative, could not and was not able to both report a single failure, and managed to usually adds that the success was difficult.",
        "use_fa": "could گذشتهٔ can برای توانایی کلی است: she could read music at four. برای یک موفقیت در یک موقعیت، was able to یا managed to روشن‌تر است، چون could تنها می‌گوید توانایی وجود داشت. در منفی، could not و was not able to هر دو یک ناکامی را گزارش می‌کنند و managed to معمولاً می‌افزاید که موفقیت دشوار بوده است.",
        "form_en": "could + base verb (general ability)  ·  was / were able to + base verb (one success)  ·  managed to + base verb",
        "examples": [
            {"en": "She could read music before she started school.",
             "fa": "او پیش از رفتن به مدرسه می‌توانست نت بخواند."},
            {"en": "The fire spread fast, but everyone was able to get out.",
             "fa": "آتش سریع پخش شد، اما همه توانستند بیرون بیایند."},
            {"en": "We managed to finish the report on time.",
             "fa": "ما موفق شدیم گزارش را سر وقت تمام کنیم."},
        ],
        "exercises": [
            ex("He ___ swim when he was three years old.", "could",
               "A general past ability takes could.",
               "توانایی کلی گذشته could می‌گیرد."),
            ex("The road was closed, but we ___ to find another way.", "were",
               "One success in the past is were able to.",
               "یک موفقیت در گذشته were able to است."),
            ex("She ___ to convince the manager to change the date.", "managed",
               "A difficult success is natural with managed to.",
               "موفقیت دشوار با managed to طبیعی است."),
        ],
        "exam": [
            q("They ___ see the mountains from their window.",
              ["could", "can", "were able"], "could",
              "A general ability in the past takes could.",
              "توانایی کلی در گذشته could می‌گیرد."),
            q("The exam was hard, but I ___ to pass it.",
              ["was able", "could", "can"], "was able",
              "One success takes was able to.",
              "یک موفقیت was able to می‌گیرد."),
            q("We ___ to catch the last train by running.",
              ["managed", "could", "were"], "managed",
              "The effort in the sentence fits managed to.",
              "تلاش در جمله با managed to می‌آید."),
        ],
    },
    {
        "section": "10-4",
        "title": "Certainty about the present: must be, may be, might be",
        "title_fa": "قطعیت دربارهٔ حال: must be، may be، might be",
        "use_en": "Must be says the speaker is almost sure, because the evidence points that way: the lights are off, so they must be away. May be, might be and could be place the same guess at lower confidence, and might be is the most tentative of the three. The modal takes be for a state and a base verb for an action in progress, which is the progressive form in chapter ten's later chart.",
        "use_fa": "must be می‌گوید گوینده تقریباً مطمئن است، چون شواهد به آن سو اشاره دارد: the lights are off, so they must be away. may be، might be و could be همین حدس را با اطمینان کمتر می‌گویند و might be محتاطانه‌ترین است. فعل وجهی برای وضعیت be می‌گیرد و برای کار در جریان فعل ساده، که شکل استمراری آن در نمودارهای بعدی همین فصل می‌آید.",
        "form_en": "must / may / might / could + be (state)  ·  must / may / might + base verb (action)",
        "examples": [
            {"en": "The lights are off, so they must be away.",
             "fa": "چراغ‌ها خاموش است، پس آن‌ها حتماً بیرون رفته‌اند."},
            {"en": "She may be in a meeting; I am not sure.",
             "fa": "شاید او در جلسه باشد؛ مطمئن نیستم."},
            {"en": "He might be waiting at the wrong gate.",
             "fa": "شاید او پشت درِ اشتباه منتظر باشد."},
        ],
        "exercises": [
            ex("The door is locked and the car is gone; they ___ be out.", "must",
               "The evidence makes the guess almost certain, so must.",
               "شواهد حدس را تقریباً قطعی می‌کند، پس must."),
            ex("I am not sure where Ali is; he ___ be at the gym.", "may",
               "An unsure guess takes may be.",
               "حدس نامطمئن may be می‌گیرد."),
            ex("She ___ be working late again tonight.", "might",
               "A hesitant guess about an action takes might.",
               "حدس محتاطانه دربارهٔ یک کار might می‌گیرد."),
        ],
        "exam": [
            q("You have not slept for two days. You ___ be exhausted.",
              ["must", "can", "should"], "must",
              "Strong evidence with a state takes must be.",
              "شاهد قوی با وضعیت must be می‌گیرد."),
            q("The parcel has not arrived; it ___ be lost.",
              ["might", "must", "can"], "might",
              "An uncertain guess takes might be.",
              "حدس نامطمئن might be می‌گیرد."),
            q("He ___ be at home; I saw his car outside.",
              ["must", "might", "cannot"], "must",
              "Seeing the car is evidence for must be.",
              "دیدن ماشین شاهدی برای must be است."),
        ],
    },
    {
        "section": "10-5",
        "title": "Certainty about the present, negative: can't be, must not be",
        "title_fa": "قطعیت منفی دربارهٔ حال: can't be و must not be",
        "use_en": "Cannot be and could not be say that something is impossible, because the evidence rules it out: that cannot be Sara, she is in Tehran. Must not be also denies a strong belief, but it reads easily as a prohibition, so cannot is the safer choice for impossibility. May not be and might not be only say that something is possibly not true, which is much weaker.",
        "use_fa": "cannot be و could not be می‌گویند چیزی ناممکن است، چون شواهد آن را رد می‌کند: that cannot be Sara, she is in Tehran. must not be نیز باوری قوی را رد می‌کند، اما به‌راحتی ممنوعیت فهمیده می‌شود، پس برای ناممکن بودن cannot انتخاب مطمئن‌تری است. may not be و might not be تنها می‌گویند ممکن است چیزی درست نباشد، که بسیار ضعیف‌تر است.",
        "form_en": "cannot / can't / couldn't + be (impossible)  ·  may not / might not + be (possibly not)",
        "examples": [
            {"en": "That cannot be right; the numbers do not add up.",
             "fa": "این نمی‌تواند درست باشد؛ اعداد با هم نمی‌خوانند."},
            {"en": "He can't be at work, because his office is closed today.",
             "fa": "او نمی‌تواند سر کار باشد، چون دفترش امروز بسته است."},
            {"en": "She might not be ready yet.",
             "fa": "شاید او هنوز آماده نباشد."},
        ],
        "exercises": [
            ex("This ___ be the right address; the street does not exist.", "cannot",
               "The evidence rules the address out, so cannot be.",
               "شواهد آن نشانی را رد می‌کند، پس cannot be."),
            ex("They ___ be home, because all the lights are off.", "can't",
               "Darkness is evidence against their being home.",
               "خاموشی شاهد مخالف بودن آن‌ها در خانه است."),
            ex("He ___ not be interested; he simply has no time.", "might",
               "A possible negative takes might not be.",
               "منفی احتمالی might not be می‌گیرد."),
        ],
        "exam": [
            q("You just ate. You ___ be hungry again.",
              ["can't", "mustn't", "shouldn't"], "can't",
              "Impossibility is expressed with can't be.",
              "ناممکن بودن با can't be بیان می‌شود."),
            q("That ___ be true; I spoke to her an hour ago.",
              ["cannot", "must not", "should not"], "cannot",
              "Cannot is the clear form for impossibility.",
              "cannot شکل روشن ناممکن بودن است."),
            q("She ___ not be coming; she has not answered.",
              ["may", "must", "can"], "may",
              "A possible negative is may not be.",
              "منفی احتمالی may not be است."),
        ],
    },
    {
        "section": "10-6",
        "title": "Certainty about the past: must have, may have, should have",
        "title_fa": "قطعیت دربارهٔ گذشته: must have، may have، should have",
        "use_en": "Must have with a past participle says the speaker concludes that something happened: the ground is wet, so it must have rained. May have, might have and could have lower that confidence. Could have also names a possibility that was never used, and should have points at something that was expected but did not happen. In speech have is often reduced, but it is always written.",
        "use_fa": "must have به‌همراه اسم مفعول می‌گوید گوینده نتیجه می‌گیرد چیزی رخ داده است: the ground is wet, so it must have rained. may have، might have و could have این اطمینان را کم می‌کنند. could have همچنین امکانی را می‌گوید که هرگز به کار نیامد، و should have به چیزی اشاره می‌کند که انتظار می‌رفت اما رخ نداد. در گفتار have کوتاه می‌شود، اما در نوشتار همیشه می‌آید.",
        "form_en": "must / may / might / could have + past participle  ·  should have + past participle (expectation not met)",
        "examples": [
            {"en": "The ground is wet, so it must have rained during the night.",
             "fa": "زمین خیس است، پس حتماً شب باران باریده است."},
            {"en": "She may have missed the bus.",
             "fa": "شاید او اتوبوس را از دست داده باشد."},
            {"en": "They should have arrived by now.",
             "fa": "آن‌ها باید تا حالا رسیده باشند."},
        ],
        "exercises": [
            ex("The window is broken; someone ___ have climbed in.", "must",
               "The broken window is evidence for must have.",
               "پنجرهٔ شکسته شاهدی برای must have است."),
            ex("I do not know why he left; he ___ have had a reason.", "might",
               "An unsure conclusion takes might have.",
               "نتیجه‌گیری نامطمئن might have می‌گیرد."),
            ex("You ___ have told me you were coming.", "should",
               "A missed expectation is should have.",
               "انتظار برآورده‌نشده should have است."),
        ],
        "exam": [
            q("The cake is gone. Someone ___ have eaten it.",
              ["must", "can", "should"], "must",
              "The missing cake is strong evidence for must have.",
              "کیکِ تمام‌شده شاهد قوی برای must have است."),
            q("She ___ have taken the earlier train; I am not certain.",
              ["may", "must", "can"], "may",
              "An uncertain conclusion takes may have.",
              "نتیجه‌گیری نامطمئن may have می‌گیرد."),
            q("We ___ have left earlier; the traffic was terrible.",
              ["should", "must", "can"], "should",
              "The regret points at should have.",
              "پشیمانی به should have اشاره دارد."),
        ],
    },
    {
        "section": "10-7",
        "title": "Certainty about the future: will, should, may, might",
        "title_fa": "قطعیت دربارهٔ آینده: will، should، may، might",
        "use_en": "For the future the scale runs from will, which states the outcome, through should, which expects it, to may and might, which leave it open. Should is the one to use when a plan depends on other people doing their part, and its negative should not warns rather than predicts. May not and might not say that the outcome is possibly not coming.",
        "use_fa": "برای آینده این طیف از will که نتیجه را قطعی می‌گوید، به should که آن را انتظار دارد، و به may و might که آن را باز می‌گذارند می‌رسد. should را وقتی به کار ببر که برنامه به انجام کار از سوی دیگران بستگی دارد و منفی آن should not هشدار می‌دهد نه پیش‌بینی. may not و might not می‌گویند ممکن است نتیجه نیاید.",
        "form_en": "will / should / may / might + base verb  ·  negative: may not / might not / should not + base verb",
        "examples": [
            {"en": "The parcel will arrive tomorrow; I have the tracking number.",
             "fa": "بسته فردا می‌رسد؛ شمارهٔ رهگیری دارم."},
            {"en": "The meeting should finish by noon.",
             "fa": "جلسه باید تا ظهر تمام شود."},
            {"en": "It might snow on the weekend.",
             "fa": "شاید آخر هفته برف ببارد."},
        ],
        "exercises": [
            ex("We ___ be late if the traffic is heavy.", "may",
               "A future outcome left open takes may.",
               "نتیجه‌ای که باز گذاشته شده may می‌گیرد."),
            ex("The train ___ leave on time; there is no announcement yet.", "should",
               "An expectation based on the timetable takes should.",
               "انتظار بر پایهٔ برنامهٔ حرکت should می‌گیرد."),
            ex("She ___ call you tonight; she promised.", "will",
               "A promise about the future is stated with will.",
               "قول دربارهٔ آینده با will بیان می‌شود."),
        ],
        "exam": [
            q("The results ___ be published next week; the date is fixed.",
              ["will", "might", "may"], "will",
              "A fixed date is stated with will.",
              "تاریخ قطعی با will گفته می‌شود."),
            q("Our team ___ win, but the other side is strong.",
              ["might", "will", "must"], "might",
              "An open outcome takes might.",
              "نتیجهٔ باز might می‌گیرد."),
            q("The shop ___ open at nine as usual.",
              ["should", "might", "can"], "should",
              "The usual arrangement is an expectation, so should.",
              "ترتیب معمول انتظار است، پس should."),
        ],
    },
    {
        "section": "10-8",
        "title": "Progressive forms of modals",
        "title_fa": "شکل استمراری افعال وجهی",
        "use_en": "A modal can be followed by be + -ing to describe an action in progress at the moment being discussed: he must be sleeping, she may be working, they should be arriving now. In the past the form is modal + have been + -ing: she must have been waiting for hours. The progressive is chosen for an activity rather than a state, and it makes the guess about what is happening right now.",
        "use_fa": "فعل وجهی می‌تواند با be + -ing بیاید تا کاری را که در همان لحظهٔ مورد بحث در جریان است توصیف کند: he must be sleeping، she may be working، they should be arriving now. در گذشته شکل آن modal + have been + -ing است: she must have been waiting for hours. شکل استمراری برای فعالیت انتخاب می‌شود نه وضعیت، و حدس را دربارهٔ آنچه همین حالا می‌گذرد دقیق‌تر می‌کند.",
        "form_en": "must / may / might + be + -ing  ·  must / may / might + have been + -ing (past)",
        "examples": [
            {"en": "Do not call him now; he must be driving.",
             "fa": "الان به او زنگ نزن؛ حتماً در راه است."},
            {"en": "She may be studying in her room.",
             "fa": "شاید او در اتاقش درس می‌خواند."},
            {"en": "They must have been waiting for over an hour.",
             "fa": "آن‌ها حتماً بیش از یک ساعت منتظر بوده‌اند."},
        ],
        "exercises": [
            ex("The light is on in his office; he ___ be working late.", "must",
               "An action in progress with strong evidence takes must be.",
               "کار در جریان با شاهد قوی must be می‌گیرد."),
            ex("She is not answering; she ___ be sleeping.", "may",
               "An unsure guess about an action takes may be.",
               "حدس نامطمئن دربارهٔ کار may be می‌گیرد."),
            ex("The road was empty; they ___ have been driving for hours.", "must",
               "The past progressive of a modal is must have been.",
               "شکل گذشتهٔ استمراری وجهی must have been است."),
        ],
        "exam": [
            q("Do not disturb her; she ___ be teaching.",
              ["must", "must have", "must to"], "must",
              "The action is happening now, so must be.",
              "کار همین حالا در جریان است، پس must be."),
            q("He looks tired. He ___ have been working all night.",
              ["must", "must be", "can"], "must",
              "The night is over, so the perfect progressive is used.",
              "شب گذشته است، پس کامل استمراری به کار می‌رود."),
            q("They ___ be waiting at the airport by now.",
              ["should", "should have", "should to"], "should",
              "An expectation about now takes should be.",
              "انتظار دربارهٔ اکنون should be می‌گیرد."),
        ],
    },
    {
        "section": "10-9",
        "title": "Combining modals with phrasal modals",
        "title_fa": "ترکیب افعال وجهی با معادل‌های عبارتی",
        "use_en": "Two modals never stand together: will can becomes will be able to, must can becomes have to be able to, and might must becomes might have to. The first modal carries the meaning that comes first in the sentence and the phrasal modal carries the second. The perfect and the progressive of the pair take their own shapes: should have been able to, might have had to.",
        "use_fa": "دو فعل وجهی هرگز کنار هم نمی‌آیند: will can به will be able to تبدیل می‌شود، must can به have to be able to و might must به might have to. فعل وجهی اول معنای اول جمله را می‌رساند و معادل عبارتی معنای دوم را. شکل کامل و استمراری این ترکیب شکل خود را می‌گیرد: should have been able to، might have had to.",
        "form_en": "modal + phrasal modal + base verb  ·  will / might / should + have to / be able to",
        "examples": [
            {"en": "You will have to show your passport at the border.",
             "fa": "باید در مرز گذرنامه‌ات را نشان دهی."},
            {"en": "She might be able to help us tomorrow.",
             "fa": "شاید او فردا بتواند به ما کمک کند."},
            {"en": "We should have been able to finish the work by now.",
             "fa": "باید تا حالا می‌توانستیم کار را تمام کنیم."},
        ],
        "exercises": [
            ex("You will ___ to wait for the next train.", "have",
               "Will must becomes will have to.",
               "will must به will have to تبدیل می‌شود."),
            ex("She might ___ able to translate the letter.", "be",
               "Might can becomes might be able to.",
               "might can به might be able to تبدیل می‌شود."),
            ex("They may ___ to pay a small fee at the desk.", "have",
               "May must becomes may have to.",
               "may must به may have to تبدیل می‌شود."),
        ],
        "exam": [
            q("He will ___ to apply again next year.",
              ["have", "has", "be"], "have",
              "Will must becomes will have to.",
              "will must به will have to تبدیل می‌شود."),
            q("We might not ___ able to come on Friday.",
              ["be", "have", "can"], "be",
              "Might not can becomes might not be able to.",
              "might not can به might not be able to تبدیل می‌شود."),
            q("You should have ___ able to solve it.",
              ["been", "be", "being"], "been",
              "The perfect of be able to is been able to.",
              "شکل کامل be able to همان been able to است."),
        ],
    },
    {
        "section": "10-10",
        "title": "Expressing preference: would rather",
        "title_fa": "بیان ترجیح: would rather",
        "use_en": "Would rather states a preference, and the verb after it is a base form with no to: I would rather stay home. A second choice is introduced by than and another base verb: I would rather walk than wait for a bus. With a different subject the past form follows the phrase, and the negative is would rather not, which is softer than saying no outright.",
        "use_fa": "would rather ترجیح را بیان می‌کند و فعل پس از آن شکل ساده و بی‌to است: I would rather stay home. انتخاب دوم با than و فعل ساده می‌آید: I would rather walk than wait for a bus. اگر فاعل دیگری بیاید، پس از عبارت فعل گذشته می‌آید، و منفی آن would rather not است که نرم‌تر از رد کردن صریح است.",
        "form_en": "would rather + base verb  ·  would rather + base verb + than + base verb  ·  would rather + subject + past verb",
        "examples": [
            {"en": "I would rather take the train than fly.",
             "fa": "ترجیح می‌دهم با قطار بروم تا با هواپیما."},
            {"en": "She would rather not discuss it now.",
             "fa": "او ترجیح می‌دهد الان دربارهٔ آن صحبت نکند."},
            {"en": "I would rather you came with me.",
             "fa": "ترجیح می‌دهم تو با من بیایی."},
        ],
        "exercises": [
            ex("I would rather ___ (walk) than take the bus.", "walk",
               "Would rather takes the base verb with no to.",
               "would rather فعل ساده بی‌to می‌گیرد."),
            ex("They would rather ___ (not, stay) at that hotel.", "not stay",
               "The negative is would rather not plus the base verb.",
               "منفی آن would rather not و فعل ساده است."),
            ex("I would rather you ___ (call) me tomorrow.", "called",
               "A different subject after would rather takes the past form.",
               "فاعل دیگر پس از would rather شکل گذشته می‌گیرد."),
        ],
        "exam": [
            q("I would rather ___ at home tonight.",
              ["stay", "to stay", "staying"], "stay",
              "Would rather takes a base verb with no to.",
              "would rather فعل ساده بی‌to می‌گیرد."),
            q("She would rather read ___ watch television.",
              ["than", "then", "to"], "than",
              "Than introduces the second choice.",
              "than انتخاب دوم را معرفی می‌کند."),
            q("I would rather you ___ the truth.",
              ["told", "tell", "telling"], "told",
              "A different subject takes the past form told.",
              "فاعل دیگر شکل گذشتهٔ told می‌گیرد."),
        ],
    },
    {
        "section": "10-11",
        "title": "Modals in summary: which one does what",
        "title_fa": "خلاصهٔ افعال وجهی: هر کدام چه کار می‌کند",
        "use_en": "The modals are a small set with a large job: can and be able to for ability, may and might for possibility and permission, must and have to for necessity, should and ought to for advice, will for the future and would for the past habit. Similar expressions such as be supposed to, had better and would rather carry the same weight without being modals, and each keeps its own endings and its own to.",
        "use_fa": "افعال وجهی مجموعه‌ای کوچک با کارهایی بزرگ‌اند: can و be able to برای توانایی، may و might برای احتمال و اجازه، must و have to برای ضرورت، should و ought to برای توصیه، will برای آینده و would برای عادت گذشته. عبارت‌های مشابه مانند be supposed to، had better و would rather همین وزن را دارند بدون آنکه فعل وجهی باشند و هر یک پایانه‌ها و to خود را نگه می‌دارد.",
        "form_en": "ability: can  ·  possibility: may / might  ·  necessity: must / have to  ·  advice: should / ought to  ·  future: will  ·  past habit: would",
        "examples": [
            {"en": "She can drive, but she may not drive after dark.",
             "fa": "او می‌تواند رانندگی کند، اما شاید پس از تاریکی رانندگی نکند."},
            {"en": "You should book early, because you will have to pay more later.",
             "fa": "باید زود رزرو کنی، چون بعداً باید بیشتر بپردازی."},
            {"en": "We would rather leave now, so we had better call a taxi.",
             "fa": "ترجیح می‌دهیم الان راه بیفتیم، پس بهتر است تاکسی بگیریم."},
        ],
        "exercises": [
            ex("He ___ be able to come, but he is not sure.", "may",
               "An open possibility takes may.",
               "احتمال باز may می‌گیرد."),
            ex("You ___ not touch the wires; they are live.", "must",
               "A prohibition is must not.",
               "ممنوعیت must not است."),
            ex("We ___ to leave before the storm starts.", "have",
               "Necessity outside the speaker is have to.",
               "ضرورت بیرونی have to است."),
        ],
        "exam": [
            q("Which modal gives advice? — You ___ see a doctor.",
              ["should", "must", "can"], "should",
              "Advice is given with should.",
              "توصیه با should داده می‌شود."),
            q("Which expresses a past habit? — We ___ swim here every summer.",
              ["would", "will", "may"], "would",
              "A repeated past action is would.",
              "کار تکرارشدهٔ گذشته would است."),
            q("Which expresses ability? — She ___ play three instruments.",
              ["can", "must", "should"], "can",
              "Ability is expressed with can.",
              "توانایی با can بیان می‌شود."),
        ],
    },
]


def main() -> int:
    data = json.loads(BOOKS.read_text(encoding="utf-8"))
    book = next(b for b in data["books"] if b.get("kind") == "grammar")

    old = [l for l in book["lessons"] if l.get("chapter") == CHAPTER]
    assert old, "chapter ten is not in the book"

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
    print(f"chapter ten: {len(LESSONS)} charts, {size} structures in the book")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
