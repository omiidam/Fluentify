#!/usr/bin/env python3
"""Eight lessons that deepen B1: one per unit, so every unit ends in a skill
the learner has to perform rather than a rule they have to recognize."""

from course_kit import gap, lesson, listen, mcq, passage, say, write

EXTRA = {
    "b1-u1": [
        lesson(
            "b1-u1-l4", "speaking",
            ("The turning point, told aloud",
             "نقطهٔ چرخش، با صدای بلند"),
            ("Tell the story of a change with a before, a moment and an after.",
             "داستان یک تغییر را با «پیش از»، «لحظه» و «پس از» بگو."),
            [
                ("A turning point is told in three parts, and the middle one "
                "is short: how things were, the moment that changed them, and "
                "how things are now. The present perfect is for the third "
                "part, because its effect is still open.",
                 "نقطهٔ چرخش در سه بخش گفته می‌شود و بخش میانی کوتاه است: وضع "
                 "پیشین، لحظه‌ای که آن را عوض کرد و وضع کنونی. حال کامل برای "
                 "بخش سوم است، چون اثرش هنوز باز است."),
                ("The moment itself takes the past simple and a specific "
                "detail: the day I got the letter, the evening she called. A "
                 "story without one detail is a summary.",
                 "خودِ لحظه گذشتهٔ ساده و جزئیاتی مشخص می‌گیرد: روزی که نامه "
                 "رسید، شبی که زنگ زد. داستان بییک جزئیات خلاصه است."),
            ],
            [
                ("I had worked in the same shop for six years.",
                 "شش سال در همان مغازه کار کرده بودم."),
                ("Then one Tuesday the owner told us he was selling.",
                 "بعد یک سه‌شنبه صاحبش گفت دارد می‌فروشد."),
                ("Since then I have worked in three different places.",
                 "از آن زمان در سه جای مختلف کار کرده‌ام."),
            ],
            [
                mcq("Which tense carries the 'now' part?", "کدام زمان بخش «حالا» "
                    "را حمل می‌کند؟",
                    ["past simple", "past perfect", "present perfect",
                     "future"], 2,
                    "The effect is still open, so present perfect.",
                    "اثر هنوز باز است، پس حال کامل."),
                mcq("The moment of change needs ___.", "لحظهٔ تغییر نیاز دارد "
                    "به ___.",
                    ["a general statement", "one specific detail",
                     "three examples", "a question"], 1,
                    "A detail makes it a story.", "جزئیات آن را داستان می‌کند."),
            ],
            [
                say("For six years I worked in the same shop, and I thought I "
                    "would stay.", "شش سال در همان مغازه کار کردم و فکر "
                    "می‌کردم می‌مانم."),
                say("Then one Tuesday the owner told us he was selling, and "
                    "nobody said anything for a while.",
                    "بعد یک سه‌شنبه صاحبش گفت دارد می‌فروشد و مدتی هیچ‌کس چیزی "
                    "نگفت."),
                say("Since then I have worked in three places, and I have "
                    "learned more in two years than in the six before.",
                    "از آن زمان در سه جا کار کرده‌ام و در دو سال بیشتر از شش سال "
                    "پیش یاد گرفته‌ام."),
            ],
        ),
    ],
    "b1-u2": [
        lesson(
            "b1-u2-l4", "writing",
            ("The letter that answers the advert",
             "نامه‌ای که به آگهی پاسخ می‌دهد"),
            ("Write a short application that answers the advert line by line.",
             "درخواست کوتاهی بنویس که آگهی را سطر به سطر پاسخ دهد."),
            [
                ("An application is read against the advert, not against your "
                 "life. Take the three things the advert asks for and answer "
                 "each in one sentence with an example: they ask for weekend "
                 "availability, and I have worked Saturdays for two years.",
                 "درخواست در برابر آگهی خوانده می‌شود، نه در برابر زندگی تو. سه "
                 "چیزی را که آگهی می‌خواهد بردار و هر یک را در یک جمله با مثال "
                 "پاسخ بده: آنها کار آخر هفته می‌خواهند و من دو سال شنبه‌ها کار "
                 "کرده‌ام."),
                ("The second conditional is useful for the closing line, "
                 "because it is polite and hypothetical: if I were offered the "
                 "post, I would start in June. Do not use it for facts.",
                 "شرطی نوع دوم برای جملهٔ پایانی سودمند است، چون مؤدب و فرضی "
                 "است: if I were offered the post, I would start in June. آن را "
                 "برای واقعیت‌ها به کار نبر."),
            ],
            [
                ("I am writing to apply for the position of sales associate.",
                 "برای شغل دستیار فروش درخواست می‌دهم."),
                ("I have worked in a shop for two years, mostly on weekends.",
                 "دو سال در مغازه کار کرده‌ام، بیشتر آخر هفته‌ها."),
                ("If I were offered the post, I could start on June 1.",
                 "اگر این شغل به من پیشنهاد شود، می‌توانم اول ژوئن شروع کنم."),
            ],
            [
                mcq("An application should answer ___.", "درخواست باید ___ را "
                    "پاسخ دهد.",
                    ["your whole career", "the advert's requirements",
                     "the company's history", "your hobbies"], 1,
                    "The advert is the question.", "آگهی همان پرسش است."),
                mcq("Which sentence is hypothetical and polite?", "کدام جمله "
                    "فرضی و مؤدب است؟",
                    ["I want the job.", "If I were offered the post, I would "
                     "start in June.", "I am the best.", "Give me a chance."],
                    1, "Second conditional with were.", "شرطی نوع دوم با were."),
            ],
            [
                write("Write an application of about 55 words for a weekend "
                      "shop assistant post. Answer two requirements with an "
                      "example each, and end with one polite hypothetical "
                      "sentence about starting.",
                      "درخواستی حدود ۵۵ واژه برای شغل دستیار فروش آخر هفته بنویس. "
                      "دو شرط را هر یک با مثالی پاسخ بده و با یک جملهٔ فرضی مؤدب "
                      "دربارهٔ شروع تمام کن.",
                      55, ["because"], "Two requirements, two examples, one "
                      "second-conditional closing, no adjectives about "
                      "yourself.", "دو شرط، دو مثال، یک جملهٔ پایانی شرطی نوع "
                      "دوم، بدون صفت دربارهٔ خودت."),
                gap("If I ___ offered the post, I would accept.",
                    ["were", "was"], "Second conditional uses were (or was in "
                    "speech).", "شرطی نوع دوم were می‌گیرد (در گفتار was هم "
                    "می‌آید).", "one word"),
                mcq("Which is a fact, not a hypothesis?", "کدام واقعیت است، نه "
                    "فرض؟",
                    ["If I were taller...", "I have worked there for two "
                     "years.", "If I had known...", "I would start in June."],
                    1, "Present perfect states a fact.", "حال کامل واقعیت را "
                    "می‌گوید."),
            ],
        ),
    ],
    "b1-u3": [
        lesson(
            "b1-u3-l4", "listening",
            ("How the bridge was built",
             "پل چگونه ساخته شد"),
            ("Follow a short process description and hear the order of the "
             "stages.",
             "توصیف کوتاه یک فرایند را دنبال کن و ترتیب مراحل را بشنو."),
            [
                ("A process description is passive because the process, not "
                 "the person, is the subject: the ground was measured, the "
                 "towers were built, the road was added. Listen for the verb "
                 "ending, not for the name of a company.",
                 "توصیف فرایند مجهول است چون فرایند موضوع است نه شخص: زمین "
                 "اندازه‌گیری شد، برج‌ها ساخته شدند، جاده افزوده شد. به پایان "
                 "فعل گوش کن، نه به نام شرکت."),
                ("Order markers are the whole answer to most questions: "
                 "first, then, after that, finally. One marker per stage.",
                 "نشانه‌های ترتیب پاسخ بیشتر پرسش‌ها هستند: first، then، after "
                 "that، finally. برای هر مرحله یک نشانه."),
            ],
            [
                ("First the river bed was surveyed.", "اول بستر رود بررسی شد."),
                ("After that, the two towers were built.",
                 "بعد از آن، دو برج ساخته شد."),
            ],
            [
                mcq("What was done first?", "اول چه کاری انجام شد؟",
                    ["the towers were built", "the river bed was surveyed",
                     "the road was added", "the bridge was painted"], 1,
                    "First the river bed was surveyed.",
                    "اول بستر رود بررسی شد."),
                mcq("The description is passive because ___.", "توصیف مجهول "
                    "است چون ___.",
                    ["the writer is unknown", "the process is the subject",
                     "it is old", "it is formal"], 1,
                    "The process, not a person, is the topic.",
                    "فرایند موضوع است، نه شخص."),
            ],
            [
                listen("First the old road was closed. Then the surface was "
                       "removed, and after that a new layer was laid.",
                       "What happened after the old road was closed?",
                       "پس از بسته شدن جادهٔ قدیمی چه شد؟",
                       ["the surface was removed", "the bridge was painted",
                        "the road was opened", "the signs were changed"], 0,
                       "Then the surface was removed.",
                       "بعد سطح برداشته شد."),
                listen("The parts were made in a factory and brought here by "
                       "truck. They were put together on site.",
                       "Where were the parts made?", "قطعات کجا ساخته شدند؟",
                       ["on site", "in a factory", "in a shop", "abroad"], 1,
                       "Made in a factory.", "در کارخانه ساخته شدند."),
                listen("Finally the road was tested for two weeks before it "
                       "was opened.",
                       "What happened before the road was opened?",
                       "پیش از باز شدن جاده چه شد؟",
                       ["it was painted", "it was tested for two weeks",
                        "it was sold", "it was closed"], 1,
                       "Tested for two weeks.", "دو هفته آزموده شد."),
            ],
        ),
    ],
    "b1-u4": [
        lesson(
            "b1-u4-l4", "reading",
            ("The series that split the family",
             "سریالی که خانواده را دو نیم کرد"),
            ("Read a review that gives a verdict and find the reasons for it.",
             "نقدی را بخوان که داوری می‌کند و دلیل‌هایش را پیدا کن."),
            [
                ("A review has a verdict and reasons, and the verdict is "
                 "usually in the last line, not the first. The reasons are the "
                 "middle: what the series does, and whether it earns what it "
                 "asks of the viewer.",
                 "نقد داوری و دلیل دارد و داوری معمولاً در سطر آخر است، نه اول. "
                 "دلیل‌ها میانه‌اند: سریال چه می‌کند و آیا آنچه از بیننده "
                 "می‌خواهد را به دست می‌آورد."),
                ("Relative clauses keep the review compact: the episode which "
                 "everyone argues about, the actor whose scenes are the best. "
                 "They let one sentence carry a fact and a judgment.",
                 "بندهای موصولی نقد را جمع‌وجور نگه می‌دارند: the episode which "
                 "everyone argues about، the actor whose scenes are the best. "
                 "یک جمله را حامل واقعیت و داوری می‌کنند."),
            ],
            [
                ("The episode that everyone argues about is the fourth.",
                 "قسمتی که همه سرش بحث می‌کنند چهارمی است."),
                ("It is a series whose ending you will discuss for weeks.",
                 "سریالی است که هفته‌ها دربارهٔ پایانش حرف می‌زنید."),
            ],
            [
                mcq("Where is the verdict?", "داوری کجاست؟",
                    ["the first line", "the middle", "the last line",
                     "the title"], 2,
                    "The closing line gives the judgment.",
                    "سطر پایانی داوری را می‌دهد."),
                mcq("What do the two viewers disagree about?",
                    "دو بیننده بر سر چه اختلاف دارند؟",
                    ["the acting", "whether the ending earns the slow middle",
                     "the music", "the length"], 1,
                    "They split on whether the ending pays for the pacing.",
                    "بر سر این اختلاف دارند که آیا پایان، کندی میانه را جبران "
                    "می‌کند."),
            ],
            [
                mcq("The review's own verdict is that the series is ___.",
                    "داوری خود نقد این است که سریال ___ است.",
                    ["a failure", "worth the argument it starts",
                     "too short", "badly acted"], 1,
                    "The last line says it earns the argument.",
                    "سطر آخر می‌گوید ارزش بحث را دارد."),
                mcq("'The episode which everyone argues about' is a ___.",
                    "«The episode which everyone argues about» یک ___ است.",
                    ["reported question", "relative clause", "conditional",
                     "passive"], 1,
                    "Which introduces a defining relative clause.",
                    "which بند موصولی وصفی می‌آورد."),
            ],
            passage=passage(
                ("The series that split the family",
                 "سریالی که خانواده را دو نیم کرد"),
                ("We watched it in three sittings, which is two more than we "
                 "usually manage, and the argument started before the credits "
                 "of the fourth episode. That episode, which everyone will "
                 "argue about, slows down exactly where a series is supposed "
                 "to speed up: two people sit in a kitchen for forty minutes "
                 "and say almost nothing. My brother found it unbearable. I "
                 "found it the only honest scene in the season, because it is "
                 "the one place where the program stops explaining and lets "
                 "the silence work.\n\n"
                "The last episode pays for that patience, and whether it pays "
                "enough is the real disagreement. It is a series whose ending "
                "you will discuss for weeks, and that is a compliment of a "
                "specific kind: not that it is good, but that it is worth "
                "arguing about. Recommended, with one condition — do not "
                "watch it in a hurry.",
                "آن را در سه نشست دیدیم، که دو نشست بیشتر از همیشه است، و بحث "
                "پیش از تیتراژ قسمت چهارم شروع شد. همان قسمتی که همه سرش بحث "
                "خواهند کرد، دقیقاً جایی کند می‌شود که سریال باید تند شود: دو "
                "نفر چهل دقیقه در آشپزخانه می‌نشینند و تقریباً هیچ نمی‌گویند. "
                "برادرم آن را تحمل‌ناپذیر یافت. من آن را تنها صحنهٔ صادق فصل "
                "یافتم، چون تنها جایی است که برنامه از توضیح دادن دست می‌کشد و "
                "می‌گذارد سکوت کار کند.\n\n"
                "قسمت آخر پاداش این صبر را می‌دهد و اینکه آیا پاداش کافی است "
                "همان اختلاف واقعی است. سریالی است که هفته‌ها دربارهٔ پایانش حرف "
                "می‌زنید و این تعریفی از نوعی خاص است: نه اینکه خوب است، بلکه "
                "اینکه ارزش بحث دارد. پیشنهاد می‌شود، با یک شرط — با عجله "
                "نبینید."),
            ),
        ),
    ],
    "b1-u5": [
        lesson(
            "b1-u5-l4", "speaking",
            ("Reporting a conversation without repeating it",
             "نقل گفت‌وگو بی‌آنکه تکرارش کنی"),
            ("Report what people said, and shift the tense and the pronouns "
             "correctly.",
             "بگو دیگران چه گفتند و زمان و ضمیرها را درست جابه‌جا کن."),
            [
                ("When you report, three things move: the tense goes back one "
                 "step, the pronouns change, and the time word changes. I will "
                 "call you tomorrow becomes he said he would call me the next "
                 "day.",
                 "وقتی نقل می‌کنی سه چیز جابه‌جا می‌شود: زمان یک پله عقب "
                 "می‌رود، ضمیرها عوض می‌شوند و واژهٔ زمان تغییر می‌کند. I will "
                 "call you tomorrow می‌شود he said he would call me the next "
                 "day."),
                ("You do not have to report every word. Report the decision "
                 "and the reason: she said she would move the meeting because "
                 "two people were away. That is what the listener needs.",
                 "لازم نیست هر واژه را نقل کنی. تصمیم و دلیل را نقل کن: she said "
                 "she would move the meeting because two people were away. "
                 "شنونده همین را می‌خواهد."),
            ],
            [
                ("She said she would send the file that evening.",
                 "گفت فایل را همان شب می‌فرستد."),
                ("He asked whether we had finished.",
                 "پرسید آیا تمام کرده‌ایم."),
            ],
            [
                mcq("'I will call you tomorrow' becomes ___.", "«I will call "
                    "you tomorrow» می‌شود ___.",
                    ["he said he will call me tomorrow",
                     "he said he would call me the next day",
                     "he says he called me", "he said I will call him"],
                    1, "Will becomes would and tomorrow becomes the next day.",
                    "will می‌شود would و tomorrow می‌شود the next day."),
                mcq("A reported question uses ___.", "پرسش نقل‌شده از ___ "
                    "استفاده می‌کند.",
                    ["question word order", "statement word order", "do/does",
                     "a question mark"], 1,
                    "He asked whether we had finished: no inversion.",
                    "He asked whether we had finished: بدون جابه‌جایی."),
            ],
            [
                say("She said she would send the file that evening.",
                    "گفت فایل را همان شب می‌فرستد."),
                say("He asked whether we had finished the report, and I said "
                    "we had.", "پرسید آیا گزارش را تمام کرده‌ایم و گفتم بله."),
                say("They told me the meeting had been moved because two "
                    "people were away.",
                    "گفتند جلسه جابه‌جا شده چون دو نفر نبودند."),
            ],
        ),
    ],
    "b1-u6": [
        lesson(
            "b1-u6-l4", "reading",
            ("The town that stopped walking",
             "شهری که از راه رفتن دست کشید"),
            ("Read about a change in habit and pick out what caused it.",
             "دربارهٔ تغییر یک عادت بخوان و علتش را جدا کن."),
            [
                ("Used to describes a habit that has stopped, and the text "
                 "will usually tell you why it stopped. The cause is the "
                 "interesting part of the reading: a new road, a supermarket, "
                 "a decision by a council.",
                 "used to عادتی را می‌گوید که تمام شده و متن معمولاً می‌گوید چرا "
                 "تمام شد. علت بخش جالب خواندن است: جاده‌ای تازه، سوپرمارکتی، "
                 "تصمیمی از شورا."),
                ("Be careful with the negative: did not use to, not did not "
                 "used to. In writing, the correct form is visible and the "
                 "wrong one is a mark lost.",
                 "به منفی دقت کن: did not use to، نه did not used to. در نوشتار "
                 "صورت درست دیده می‌شود و نادرست نمره می‌سوزاند."),
            ],
            [
                ("People used to walk to the shops.", "مردم پیاده به مغازه‌ها "
                 "می‌رفتند."),
                ("They did not use to lock their doors.",
                 "درها را قفل نمی‌کردند."),
            ],
            [
                mcq("What did people use to do?", "مردم چه می‌کردند؟",
                    ["drive to work", "walk to the shops", "meet on Fridays",
                     "work from home"], 1,
                    "They used to walk to the shops.",
                    "پیاده به مغازه‌ها می‌رفتند."),
                mcq("Why did the habit stop?", "چرا عادت تمام شد؟",
                    ["the shops closed", "a new road was built",
                     "the town grew", "people moved away"], 1,
                    "The bypass road moved the traffic and the walk.",
                    "جادهٔ کمربندی ترافیک و پیاده‌روی را جابه‌جا کرد."),
            ],
            [
                mcq("The correct negative is ___.", "منفی درست ___ است.",
                    ["did not used to", "did not use to", "does not used to",
                     "not used to"], 1,
                    "After did, use the base form.", "پس از did صورت پایه "
                    "می‌آید."),
                mcq("'Used to' describes ___.", "«used to» ___ را توصیف "
                    "می‌کند.",
                    ["a present habit", "a stopped habit", "a future plan",
                     "a single event"], 1,
                    "The habit is over.", "عادت تمام شده است."),
            ],
            passage=passage(
                ("The town that stopped walking",
                 "شهری که از راه رفتن دست کشید"),
                ("My grandmother used to walk to the shops every morning, and "
                 "so did most of the street. There was a baker, a butcher and "
                 "a small supermarket within four hundred meters, and the walk "
                 "was part of the morning rather than a way of getting "
                 "somewhere. Then the bypass was built in 1998, and the traffic "
                 "that used to come through the center went round it. The shops "
                 "lost the passing trade, the baker closed, and the supermarket "
                 "moved to a retail park two kilometers away.\n\n"
                "People did not stop shopping. They started driving, because "
                 "the walk now ended at an empty building. What the bypass "
                 "improved was the air and the noise. What it cost was the "
                 "habit of walking, which nobody had thought to put in the "
                 "budget. My grandmother still says she used to know everyone "
                 "on that street, and she says it in the past tense without "
                 "noticing.",
                "مادربزرگم هر صبح پیاده به مغازه‌ها می‌رفت و بیشتر کوچه هم "
                "همین‌طور. در چهارصد متری نانوایی، قصابی و سوپرمارکتی کوچک بود و "
                "پیاده‌روی بخشی از صبح بود نه راهی برای رسیدن به جایی. بعد در "
                "۱۹۹۸ جادهٔ کمربندی ساخته شد و ترافیکی که از مرکز می‌گذشت دور آن "
                "را گرفت. مغازه‌ها مشتری گذری را از دست دادند، نانوایی بسته شد و "
                "سوپرمارکت به مجتمعی در دو کیلومتری رفت.\n\n"
                "مردم خرید را رها نکردند. رانندگی را شروع کردند، چون پیاده‌روی "
                "حالا به ساختمانی خالی می‌رسید. کمربندی هوا و صدا را بهتر کرد. "
                "هزینه‌اش عادت پیاده‌روی بود که کسی به فکر گذاشتنش در بودجه "
                "نبود. مادربزرگم هنوز می‌گوید همهٔ آن کوچه را می‌شناخت و این را "
                "در زمان گذشته می‌گوید بی‌آنکه متوجه شود."),
            ),
        ),
    ],
    "b1-u7": [
        lesson(
            "b1-u7-l4", "writing",
            ("The complaint that gets an answer",
             "شکایتی که پاسخ می‌گیرد"),
            ("Write a formal complaint with a clear sequence, a request and a "
             "record of what you have already tried.",
             "شکایت رسمی بنویس با ترتیب روشن، یک درخواست و ثبت آنچه آزموده‌ای."),
            [
                ("A formal complaint is a record as much as a request. Date "
                 "the events, name the people you spoke to, and say what you "
                 "were told. If the company replies, this is the document that "
                 "decides who is right.",
                 "شکایت رسمی به‌اندازهٔ درخواست، ثبت است. رویدادها را تاریخ بزن، "
                 "نام کسانی را که با آن‌ها حرف زدی بیاور و بگو چه به تو گفتند. "
                 "اگر شرکت پاسخ دهد، همین سند تعیین می‌کند حق با کیست."),
                ("Modal verbs set the tone: I must ask you to... is firm; "
                 "you should have told me is an accusation. Choose the first "
                 "unless you want the second.",
                 "وجه‌ها لحن را می‌سازند: I must ask you to… محکم است و you "
                 "should have told me اتهام. اولی را انتخاب کن، مگر آنکه دومی "
                 "را بخواهی."),
            ],
            [
                ("On May 3 I was told the repair would take two days.",
                 "سوم مه به من گفتند تعمیر دو روز طول می‌کشد."),
                ("I must ask you to confirm a date in writing.",
                 "باید بخواهم تاریخ را کتبی تأیید کنید."),
            ],
            [
                mcq("Which sentence is firm without accusing?",
                    "کدام جمله محکم است بی‌آنکه متهم کند؟",
                    ["You lied to me.", "I must ask you to confirm a date in "
                     "writing.", "You should have called.", "This is "
                     "ridiculous."], 1,
                    "Must ask is firm and impersonal.", "must ask محکم و "
                    "بی‌شخص است."),
                mcq("A complaint should include ___.", "شکایت باید ___ را در "
                    "برداشته باشد.",
                    ["your opinion of the staff", "dates and what you were "
                     "told", "a threat", "your other complaints"], 1,
                    "The record is what settles it.", "ثبت همان چیزی است که "
                    "فیصله می‌دهد."),
            ],
            [
                write("Write a complaint of about 60 words about a repair that "
                      "was promised in two days and has taken three weeks. "
                      "Give two dates, what you were told, and one request.",
                      "شکایتی حدود ۶۰ واژه بنویس دربارهٔ تعمیری که قرار بود دو "
                      "روز طول بکشد و سه هفته شده است. دو تاریخ، آنچه به تو "
                      "گفتند و یک درخواست را بیاور.",
                      60, ["although"], "Two dates, what you were told, one "
                      "firm request, no accusation and no adjectives about "
                      "the company.", "دو تاریخ، آنچه گفته شد، یک درخواست محکم، "
                      "بدون اتهام و صفت دربارهٔ شرکت."),
                gap("I ___ ask you to confirm the date in writing.",
                    ["must", "would"], "Either keeps the request firm.",
                    "هر دو درخواست را محکم نگه می‌دارند.", "one word"),
                mcq("Which is a request, not a complaint?", "کدام درخواست است، "
                    "نه شکایت؟",
                    ["The service was terrible.", "Please confirm a date in "
                     "writing.", "Nobody called me.", "I am angry."], 1,
                    "Please + verb is a request.", "please + فعل درخواست است."),
            ],
        ),
    ],
    "b1-u8": [
        lesson(
            "b1-u8-l4", "speaking",
            ("An environmental choice, argued",
             "یک انتخاب زیست‌محیطی، با استدلال"),
            ("Give an opinion about an everyday choice, support it, and answer "
             "one objection.",
             "دربارهٔ یک انتخاب روزمره نظر بده، پشتیبانی کن و به یک اعتراض "
             "پاسخ بده."),
            [
                ("An opinion with reasons has three sentences: the position, "
                 "the reason, and the limit. I think cities should charge for "
                 "parking, because it moves short trips onto buses, though it "
                 "only works if the buses are frequent.",
                 "نظر با دلیل سه جمله دارد: موضع، دلیل و محدودیت. I think cities "
                 "should charge for parking, because it moves short trips onto "
                 "buses, though it only works if the buses are frequent."),
                ("Answering an objection is not conceding. It is one sentence "
                 "that names the objection and one that answers it: people say "
                 "it costs too much, and the answer is that the charge is "
                 "smaller than the bus fare it replaces.",
                 "پاسخ به اعتراض واگذاری نیست. یک جمله اعتراض را نام می‌برد و "
                 "یکی پاسخش را: people say it costs too much, and the answer "
                 "is that the charge is smaller than the bus fare it "
                 "replaces."),
            ],
            [
                ("I think plastic bags should be charged.",
                 "فکر می‌کنم باید برای کیسه‌های پلاستیکی پول گرفت."),
                ("Though it is unpopular, it works.", "هرچند محبوب نیست، کار "
                 "می‌کند."),
            ],
            [
                mcq("Which sentence gives a limit?", "کدام جمله محدودیت "
                    "می‌دهد؟",
                    ["I think it is good.", "Because it works.",
                     "Though it only works if buses are frequent.",
                     "Everybody agrees."], 2,
                    "Though introduces the limit.", "though محدودیت را "
                    "می‌آورد."),
                mcq("Answering an objection means ___.",
                    "پاسخ به اعتراض یعنی ___.",
                    ["changing your opinion", "naming it and answering it",
                     "ignoring it", "repeating your reason"], 1,
                    "Name it, then answer it.", "اول نامش ببر، بعد پاسخ بده."),
            ],
            [
                say("I think cities should charge for parking in the center.",
                    "فکر می‌کنم شهرها باید برای پارکینگ مرکز شهر پول بگیرند."),
                say("It works because it moves short trips onto buses, and "
                    "short trips are most of the traffic.",
                    "کار می‌کند چون سفرهای کوتاه را به اتوبوس می‌برد و بیشتر "
                    "ترافیک همان سفرهای کوتاه است."),
                say("People say it costs families too much, and the answer is "
                    "that the charge is smaller than the bus fare it replaces.",
                    "می‌گویند برای خانواده‌ها گران است و پاسخ این است که پول "
                    "پارکینگ از کرایهٔ اتوبوسی که جایگزینش می‌شود کمتر است."),
            ],
        ),
    ],
}
