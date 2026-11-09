#!/usr/bin/env python3
"""A2 · units 3-4: experience without a date, and arrangements with one.

Unit 3 adds the present perfect for 'at some time in my life', and asks the
learner to say it out loud. Unit 4 turns to the future, first as meaning
(going to, will, present continuous) and then as the email that fixes a plan.
"""

from course_kit import dialogue, gap, lesson, listen, mcq, say, unit, write

U3 = unit(
    "a2-u3",
    ("Have you ever…", "تا حالا…"),
    ("Talk about life experience without saying when, and order a meal in a restaurant.", "دربارهٔ تجربهٔ زندگی بدون گفتن زمان حرف بزن و در رستوران غذا سفارش بده."),
    [
        lesson(
            "a2-u3-l1",
            "grammar",
            ("Present perfect for experience: ever, never, just, already, yet", "حال کامل برای تجربه: ever، never، just، already، yet"),
            ("Say that something has or has not happened in your life, without a finished time.", "بگو چیزی در زندگی‌ات اتفاق افتاده یا نه، بدون زمان تمام‌شده."),
            [
                ("The present perfect is have/has + past participle: I have visited, she has eaten. Use it when the time is not finished or not important: I have been to Istanbul. The experience is in your life, not on a date.", "حال کامل have/has + اسم مفعول است: I have visited، she has eaten. وقتی زمان تمام نشده یا مهم نیست از آن استفاده کن: I have been to Istanbul. تجربه در زندگی توست، نه روی یک تاریخ."),
                ("Ever asks the question, never answers it: Have you ever eaten sushi? No, I've never eaten it. Ever and never sit before the participle.", "ever پرسش را می‌سازد و never پاسخ منفی می‌دهد: Have you ever eaten sushi? No, I've never eaten it. ever و never قبل از اسم مفعول می‌آیند."),
                ("Just means a moment ago, already means sooner than expected, yet means up to now in a negative or question: I've just finished. She has already left. Have you finished yet?", "just یعنی همین حالا، already یعنی زودتر از انتظار و yet در منفی و پرسشی یعنی تا حالا: I've just finished. She has already left. Have you finished yet?"),
                ("When the time is finished, use the past simple, not the perfect: I saw him yesterday, not 'I have seen him yesterday'.", "وقتی زمان تمام شده است، گذشتهٔ ساده به کار ببر، نه حال کامل: I saw him yesterday، نه «I have seen him yesterday»."),
            ],
            [
                ("Have you ever been to the north of Iran?", "تا حالا به شمال ایران رفته‌ای؟"),
                ("I've never tried English tea, but I'd like to.", "تا حالا چای انگلیسی را امتحان نکرده‌ام، اما دوست دارم."),
                ("She has just sent the message, so wait a minute.", "همین حالا پیام را فرستاده، یک دقیقه صبر کن."),
                ("We haven't booked the table yet.", "هنوز میز رزرو نکرده‌ایم."),
                ("He has already eaten, so he isn't hungry.", "او قبلاً غذا خورده، پس گرسنه نیست."),
            ],
            [
                mcq("___ you ever ___ a horse?", "تا حالا سوار اسب ___ ای؟", ["Did / ride", "Have / ridden", "Have / rode", "Has / ride"], 1,
                    "Experience questions use have + past participle: have you ever ridden.", "پرسش تجربه با have + اسم مفعول ساخته می‌شود: have you ever ridden."),
                mcq("I ___ my keys, so I can't open the door.", "کلیدهایم را ___ و نمی‌توانم در را باز کنم.", ["lose", "lost", "have lost", "have lose"], 2,
                    "The result matters now, so the present perfect fits: have lost.", "نتیجه الان مهم است، پس حال کامل مناسب است: have lost."),
            ],
            [
                gap("She ___ (never / eat) meat, so ask for the vegetarian dish.", ["has never eaten"], "She + has + never + participle.", "She + has + never + اسم مفعول."),
                gap("We haven't finished the exercise ___ .", ["yet"], "yet, at the end of a negative sentence.", "yet در پایان جملهٔ منفی می‌آید."),
                mcq("Which sentence is correct?", "کدام جمله درست است؟", ["I have seen him yesterday.", "I saw him yesterday.", "I have saw him yesterday.", "I seen him yesterday."], 1,
                    "Yesterday is a finished time, so the past simple is required.", "yesterday زمان تمام‌شده است، پس گذشتهٔ ساده لازم است."),
                listen("I've just come back from Shiraz. I went there for a wedding and stayed four days.", "When did she go to Shiraz?", "کِی به شیراز رفت؟", ["she has never been", "she went recently, for a wedding", "she is going next week", "she lives there"], 1,
                       "She has just come back, and went for a wedding.", "همین حالا برگشته و برای عروسی رفته بود."),
            ],
        ),
        lesson(
            "a2-u3-l2",
            "vocabulary",
            ("Food, cooking and the restaurant", "غذا، آشپزی و رستوران"),
            ("Read a recipe, describe how a dish is made, and get through a meal out.", "دستور پخت را بخوان، بگو غذایی چطور پخته می‌شود و یک وعده در رستوران را جلو ببر."),
            [
                ("Cooking verbs are specific: boil (in water), fry (in oil), roast (in an oven), bake (bread and cakes), grill (over heat), chop and slice (cut). The recipe lists ingredients and steps; a spoonful, a pinch and a handful give the amounts.", "فعل‌های آشپزی دقیق‌اند: boil (در آب)، fry (در روغن)، roast (در فر)، bake (نان و کیک)، grill (روی حرارت)، chop و slice (بریدن). دستور پخت مواد لازم و مرحله‌ها را می‌آورد؛ a spoonful، a pinch و a handful مقدار را می‌گویند."),
                ("A meal out has its own order: you book a table, look at the menu, order a starter and a main course, ask for the bill and leave a tip. Still or sparkling water; rare, medium or well done for meat.", "وعده در بیرون ترتیب خودش را دارد: میز رزرو می‌کنی، منو را می‌بینی، پیش‌غذا و غذای اصلی سفارش می‌دهی، صورت‌حساب می‌خواهی و انعام می‌گذاری. آب still یا sparkling؛ گوشت rare، medium یا well done."),
                ("Taste words are useful adjectives: it's delicious, salty, spicy, mild, fresh, undercooked. 'It tastes good' is about the food; 'I like it' is about you.", "واژه‌های مزه صفت‌های کاربردی‌اند: delicious، salty، spicy، mild، fresh، undercooked. «It tastes good» دربارهٔ غذاست و «I like it» دربارهٔ تو."),
            ],
            [
                ("First boil the rice for ten minutes, then drain it.", "اول برنج را ده دقیقه بجوشان و بعد آبکش کن."),
                ("Fry the onions in a little oil until they are golden.", "پیازها را در کمی روغن تفت بده تا طلایی شوند."),
                ("Could we have the bill, please? And the food was delicious.", "می‌شود صورتحساب را بیاورید؟ و غذا خوشمزه بود."),
                ("I'd like the chicken, please — is it spicy?", "مرغ را می‌خواهم؛ تند است؟"),
            ],
            [
                mcq("You cook bread and cakes in an oven. The verb is ___.", "نان و کیک را در فر می‌پزی. فعل ___ است.", ["boil", "bake", "fry", "grill"], 1,
                    "Bake is for bread, cakes and pastries.", "bake برای نان، کیک و شیرینی است."),
                mcq("The list of food you need for a dish is the ___.", "فهرست غذایی که برای یک غذا لازم است ___ است.", ["menu", "recipe's ingredients", "bill", "starter"], 1,
                    "A recipe lists its ingredients.", "دستور پخت مواد لازمش را فهرست می‌کند."),
            ],
            [
                gap("___ the potatoes for twenty minutes until they are soft.", ["Boil"], "Water and heat: boil.", "آب و حرارت: boil."),
                gap("Could we have the ___ , please? We'd like to pay.", ["bill", "check"], "In a restaurant you ask for the bill (check in the US).", "در رستوران bill (در آمریکا check) می‌خواهی."),
                mcq("'It's a bit too salty' means ___.", "«It's a bit too salty» یعنی ___.", ["it needs more salt", "there is too much salt in it", "it is very sweet", "it is cold"], 1,
                    "Too salty means it has more salt than you want.", "too salty یعنی نمکش بیشتر از حد دلخواه است."),
                mcq("Which is the first course of a meal?", "کدام اولین غذای وعده است؟", ["main course", "dessert", "starter", "bill"], 2,
                    "The starter comes before the main course.", "starter قبل از غذای اصلی می‌آید."),
            ],
        ),
        lesson(
            "a2-u3-l3",
            "speaking",
            ("Ask about experiences", "دربارهٔ تجربه‌ها بپرس"),
            ("Run a short conversation of questions and answers about what someone has done.", "گفت‌وگوی کوتاهی از پرسش و پاسخ دربارهٔ کارهایی که کسی انجام داده اجرا کن."),
            [
                ("The pattern is short: Have you ever …? — Yes, I have. / No, I've never … . Then add one detail in the past simple, because the detail has a time: I have been to Turkey. I went there in 2019.", "الگو کوتاه است: Have you ever …? — Yes, I have. / No, I've never … . بعد یک جزئیات با گذشتهٔ ساده اضافه کن، چون جزئیات زمان دارد: I have been to Turkey. I went there in 2019."),
                ("Keep the conversation moving with a follow-up: Really? How was it? Who did you go with? Would you go again? One question about the answer is worth three new topics.", "گفت‌وگو را با پرسش بعدی ادامه بده: Really? How was it? Who did you go with? Would you go again? یک پرسش دربارهٔ پاسخ، از سه موضوع تازه بهتر است."),
                ("Say the whole sentence, not one word. 'Yes' ends the conversation; 'Yes, I have — twice, actually' opens it. Stress the important word: I've never eaten *sushi*.", "جملهٔ کامل بگو، نه یک واژه. «Yes» گفت‌وگو را تمام می‌کند؛ «Yes, I have — twice, actually» آن را باز می‌کند. روی واژهٔ مهم تأکید کن: I've never eaten *sushi*."),
            ],
            [
                ("Have you ever tried Iranian food? — Yes, I have. I had ghormeh sabzi in Tehran last year.", "تا حالا غذای ایرانی امتحان کرده‌ای؟ — بله. سال گذشته در تهران قرمه‌سبزی خوردم."),
                ("Have you ever been to a concert? — No, I've never been to one, but I'd love to.", "تا حالا کنسرت رفته‌ای؟ — نه، هرگز نرفته‌ام، اما خیلی دوست دارم."),
                ("How was it? — It was amazing, but the tickets were expensive.", "چطور بود؟ — فوق‌العاده بود، اما بلیت‌ها گران بودند."),
            ],
            [
                mcq("Which answer keeps the conversation going?", "کدام پاسخ گفت‌وگو را ادامه می‌دهد؟", ["Yes.", "Yes, I have — twice, actually.", "No idea.", "What?"], 1,
                    "A detail invites the next question; a bare 'yes' closes the topic.", "جزئیات پرسش بعدی را دعوت می‌کند؛ «yes» تنها موضوع را می‌بندد."),
                mcq("After 'Have you ever been to Turkey?', which detail fits?", "بعد از «Have you ever been to Turkey?» کدام جزئیات مناسب است؟", ["I go there every year.", "I went there in 2019.", "I will go there.", "I am going there."], 1,
                    "The trip is finished, so the detail takes the past simple.", "سفر تمام شده است، پس جزئیات گذشتهٔ ساده می‌گیرد."),
            ],
            [
                say("No, I've never tried sushi, but I'd like to.", "نه، تا حالا سوشی امتحان نکرده‌ام، اما دوست دارم."),
                say("I have been to the north of Iran twice.", "دو بار به شمال ایران رفته‌ام."),
                say("Who did you go with?", "با چه کسی رفتی؟"),
                say("That sounds interesting. Tell me more.", "جالب به نظر می‌رسد. بیشتر بگو."),
            ],
            dialogue=dialogue([
                ("A", "Have you ever been to another country?", "تا حالا به کشور دیگری رفته‌ای؟"),
                ("B", "Yes, I have. I went to Turkey in 2019.", "بله. سال ۲۰۱۹ به ترکیه رفتم."),
                ("A", "Really? How was it?", "واقعاً؟ چطور بود؟"),
                ("B", "It was great. The food was amazing, but it was very hot.", "عالی بود. غذا فوق‌العاده بود، اما هوا خیلی گرم بود."),
                ("A", "Would you go again?", "دوباره می‌روی؟"),
                ("B", "Definitely. I'd like to go in spring next time.", "حتماً. دفعهٔ بعد دوست دارم بهار بروم."),
            ]),
        ),
    ],
)

U4 = unit(
    "a2-u4",
    ("Next week", "هفتهٔ آینده"),
    ("Talk about plans, arrangements and decisions, then put an arrangement in an email.", "دربارهٔ برنامه‌ها، قرارها و تصمیم‌ها حرف بزن و بعد یک قرار را در ایمیل بنویس."),
    [
        lesson(
            "a2-u4-l1",
            "grammar",
            ("Future: going to, present continuous, will", "آینده: going to، حال استمراری، will"),
            ("Choose the future form by meaning: a plan, an arrangement, or a decision made now.", "شکل آینده را بر اساس معنا انتخاب کن: برنامه، قرار یا تصمیمی که همین حالا گرفته می‌شود."),
            [
                ("Going to is for an intention or a plan you have already made: I'm going to study tonight. It also predicts from what you can see: look at those clouds — it's going to rain.", "going to برای قصد یا برنامه‌ای است که قبلاً گرفته‌ای: I'm going to study tonight. همچنین پیش‌بینی بر اساس چیزی که می‌بینی: look at those clouds — it's going to rain."),
                ("The present continuous is for an arrangement: a time and usually another person are fixed. I'm meeting Sara at six. We're flying on Friday. Going to is the plan; the continuous is the diary entry.", "حال استمراری برای قرار است: زمان و معمولاً شخص دیگری ثابت شده‌اند. I'm meeting Sara at six. We're flying on Friday. going to برنامه است و حال استمراری ثبت در دفترچه."),
                ("Will is for a decision made at the moment of speaking, an offer or a promise: The phone's ringing — I'll get it. I'll help you with that. It also makes a general prediction: I think it will be cold.", "will برای تصمیمی است که همان لحظهٔ صحبت گرفته می‌شود، پیشنهاد یا قول: The phone's ringing — I'll get it. I'll help you with that. همچنین پیش‌بینی کلی: I think it will be cold."),
                ("Time clauses stay in the present: when I arrive, before we leave, after she calls — never 'when I will arrive'.", "بندهای زمانی در حال می‌مانند: when I arrive، before we leave، after she calls — نه «when I will arrive»."),
            ],
            [
                ("I'm going to look for a new job this year.", "امسال می‌خواهم دنبال کار تازه‌ای بگردم."),
                ("We're having dinner with my parents on Friday.", "جمعه با پدر و مادرم شام می‌خوریم."),
                ("Don't worry about the bill — I'll pay.", "نگران صورتحساب نباش، من می‌پردازم."),
                ("I think the exam will be easier than last year.", "فکر می‌کنم امتحان از سال گذشته آسان‌تر خواهد بود."),
                ("I'll call you when I get home.", "وقتی رسیدم خانه زنگ می‌زنم."),
            ],
            [
                mcq("The phone is ringing. — Don't worry, I ___ it.", "تلفن زنگ می‌زند. — نگران نباش، ___ .", ["am getting", "get", "will get", "'m going to get"], 2,
                    "A decision at the moment of speaking takes will.", "تصمیم در لحظهٔ صحبت با will گفته می‌شود."),
                mcq("We ___ the 7:30 train tomorrow; the tickets are booked.", "فردا با قطار ۷:۳۰ ___؛ بلیت‌ها خریداری شده‌اند.", ["are taking", "take", "will take", "took"], 0,
                    "A fixed arrangement takes the present continuous: are taking.", "قرار ثابت با حال استمراری: are taking."),
            ],
            [
                gap("I ___ (meet) Reza at the library at five — we agreed yesterday.", ["am meeting", "'m meeting"], "Fixed arrangement: present continuous.", "قرار ثابت: حال استمراری."),
                gap("Look at those clouds. It ___ (rain).", ["is going to rain", "'s going to rain"], "Prediction from evidence: going to.", "پیش‌بینی از شواهد: going to."),
                gap("I'll text you when I ___ (arrive).", ["arrive"], "After when, use the present simple.", "بعد از when حال ساده بیاور."),
                mcq("Which is a promise?", "کدام قول است؟", ["I'm going to study.", "I'm studying at six.", "I'll help you.", "I study every day."], 2,
                    "'I'll help you' is a promise made now.", "«I'll help you» قولی است که همین حالا داده می‌شود."),
            ],
        ),
        lesson(
            "a2-u4-l2",
            "vocabulary",
            ("Work, study and what you are responsible for", "کار، درس و مسئولیت‌هایت"),
            ("Describe a job or a course with the phrases people actually use at work.", "کار یا دوره‌ای را با عبارت‌هایی توصیف کن که در محل کار واقعاً به کار می‌روند."),
            [
                ("Jobs are described by duty, not only by title: I'm responsible for the morning orders. I deal with customers. I work in a team of five. The verb changes with the preposition, so learn them together.", "کارها با وظیفه توصیف می‌شوند، نه فقط عنوان: I'm responsible for the morning orders. I deal with customers. I work in a team of five. فعل با حرف اضافه عوض می‌شود، پس آن‌ها را با هم یاد بگیر."),
                ("Study has its own set: apply for a course, enroll on a course, attend a class, hand in an assignment, take an exam, pass or fail it. You apply *for* a job and *to* a university.", "درس مجموعهٔ خودش را دارد: apply for a course، enroll on a course، attend a class، hand in an assignment، take an exam، pass یا fail. برای کار apply for و برای دانشگاه apply to می‌گوییم."),
                ("Time at work: a deadline is the last day, a shift is your block of hours, overtime is extra hours, a day off is a free day. Part-time is fewer hours; full-time is the whole week.", "زمان در کار: deadline آخرین روز، shift بلوک کاری تو، overtime ساعت اضافه و a day off روز آزاد است. part-time ساعت کمتر و full-time تمام هفته است."),
            ],
            [
                ("I'm responsible for training the new staff.", "مسئول آموزش کارکنان تازه هستم."),
                ("She applied for a scholarship and got it.", "برای بورس درخواست داد و گرفت."),
                ("The deadline is Friday, so I'm working late all week.", "مهلت جمعه است، پس تمام هفته تا دیر وقت کار می‌کنم."),
                ("I work part-time and study in the evenings.", "نیمه‌وقت کار می‌کنم و عصرها درس می‌خوانم."),
            ],
            [
                mcq("You ___ an assignment to your teacher.", "تکلیف را به معلم ___ .", ["hand in", "hand out", "hand over", "hand up"], 0,
                    "Hand in means to give finished work to the person who asked for it.", "hand in یعنی کار تمام‌شده را به کسی دادن که خواسته است."),
                mcq("The last day to finish something is the ___.", "آخرین روز برای تمام کردن کاری ___ است.", ["shift", "deadline", "day off", "overtime"], 1,
                    "The deadline is the final date.", "deadline تاریخ نهایی است."),
            ],
            [
                gap("I ___ for a new job last week and they called me yesterday.", ["applied"], "apply for a job, past simple applied.", "apply for a job و گذشتهٔ آن applied."),
                gap("She is ___ for the whole sales team this month.", ["responsible"], "be responsible for.", "be responsible for یعنی مسئول چیزی بودن."),
                mcq("'I'm on the night shift' means ___.", "«I'm on the night shift» یعنی ___.", ["I finish at night", "I work during the night", "I sleep at night", "I have the night off"], 1,
                    "A shift is the block of hours you work.", "shift بلوک ساعتی است که کار می‌کنی."),
                listen("I'm sorry, I can't come on Thursday. I have to hand in my project by Friday and I'm still working on it.", "Why can't she come on Thursday?", "چرا پنجشنبه نمی‌تواند بیاید؟", ["she is on vacation", "she has to finish a project for Friday", "she is ill", "she is working overtime on Friday"], 1,
                       "Her project is due on Friday and it is not finished.", "پروژه‌اش جمعه موعد دارد و تمام نشده است."),
            ],
        ),
        lesson(
            "a2-u4-l3",
            "writing",
            ("An email that fixes an arrangement", "ایمیلی که یک قرار را ثابت می‌کند"),
            ("Write a short email that confirms a time, a place and what each person will do.", "ایمیل کوتاهی بنویس که زمان، مکان و کار هر کس را تأیید کند."),
            [
                ("An arrangement email has three jobs: confirm the time and place, say what you will do, and ask one question so the other person can answer. Subject line: 'Friday dinner — time?' is enough.", "ایمیل قرار سه کار دارد: زمان و مکان را تأیید کن، بگو تو چه می‌کنی و یک پرسش بپرس تا طرف بتواند پاسخ دهد. موضوع «Friday dinner — time?» کافی است."),
                ("Open informally with Hi Sara, close with Best wishes or See you Friday. Use contractions in a friendly email, and put the arrangement in the future: I'm meeting you at seven, I'll bring the tickets.", "با Hi Sara شروع کن و با Best wishes یا See you Friday تمام کن. در ایمیل دوستانه شکل کوتاه به کار ببر و قرار را در آینده بگذار: I'm meeting you at seven، I'll bring the tickets."),
                ("Link the sentences so the email reads as one message: first, then, after that, because, but, so. Three short paragraphs beat one long one.", "جمله‌ها را به هم وصل کن تا ایمیل یک پیام به نظر برسد: first، then، after that، because، but، so. سه پاراگراف کوتاه از یک پاراگراف بلند بهتر است."),
            ],
            [
                ("Subject: Friday dinner — time?", "موضوع: شام جمعه — ساعت؟"),
                ("We're meeting at the restaurant at seven, and I've booked a table for four.", "ساعت هفت در رستوران همدیگر را می‌بینیم و میز چهارنفره رزرو کرده‌ام."),
                ("I'll bring the tickets, so you don't need to print anything.", "بلیت‌ها را می‌آورم، پس لازم نیست چیزی چاپ کنی."),
                ("Could you let me know if you're coming by car?", "می‌شود خبر بدهی با ماشین می‌آیی؟"),
            ],
            [
                mcq("Which is the best subject line for a message about a meeting?", "کدام موضوع برای پیامی دربارهٔ یک جلسه بهترین است؟", ["Hello", "Meeting on Tuesday — 10 a.m.?", "Very important!!!", "My email"], 1,
                    "A subject line says the topic and the question.", "موضوع ایمیل باید موضوع و پرسش را بگوید."),
                mcq("Which closing fits a friend?", "کدام پایان برای دوست مناسب است؟", ["Yours faithfully", "Dear Sir", "See you Friday", "I remain yours"], 2,
                    "Informal closings fit friends: See you Friday.", "پایان غیررسمی برای دوستان مناسب است: See you Friday."),
            ],
            [
                write("Write an email to a friend about Saturday. Say what time you are meeting, where, what you will bring, and ask one question. Use one of because, so or but.",
                       "ایمیل کوتاهی برای دوستت دربارهٔ شنبه بنویس. بگو چه ساعتی و کجا همدیگر را می‌بینید، چه چیزی می‌آوری و یک پرسش بپرس. یک بار از because، so یا but استفاده کن.",
                       35, ["because", "so", "but"],
                       "Start with Hi + name, keep three short paragraphs, finish with See you Saturday.",
                       "با Hi و نام شروع کن، سه پاراگراف کوتاه بنویس و با See you Saturday تمام کن."),
                mcq("Where does the time of the arrangement belong?", "زمان قرار کجا باید بیاید؟", ["only in the subject", "in the first paragraph", "at the very end", "nowhere"], 1,
                    "Confirm the time early so the reader sees it at once.", "زمان را زود تأیید کن تا خواننده فوراً ببیند."),
                gap("I'll bring the tickets, ___ you don't need to print anything.", ["so"], "The second clause is the result of the first.", "بند دوم نتیجهٔ بند اول است."),
            ],
        ),
    ],
)
