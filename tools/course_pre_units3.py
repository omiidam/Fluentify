#!/usr/bin/env python3
"""Pre-A1, units 5 and 6: places around you, and the shape of a day."""

from course_kit import dialogue, gap, lesson, listen, mcq, passage, say, unit, write

U5 = unit(
    "pre-u5",
    ("Places", "جاها"),
    ("Find your way round a street: what there is, and where it is.",
     "در یک خیابان راه پیدا کن: چه چیزی هست و کجاست."),
    [
        lesson(
            "pre-u5-l1", "grammar",
            ("There is, there are, in, on, under",
             "There is، there are، in، on، under"),
            ("Say that something exists, and put it in the right place.",
             "بگو چیزی وجود دارد و آن را در جای درست بگذار."),
            [
                ("Use there is for one thing and there are for more than one. "
                 "There is a shop. There are two shops.",
                 "برای یک چیز there is و برای بیشتر از یکی there are به کار "
                 "ببر: There is a shop، There are two shops."),
                ("The place words: in is inside, on is on top of, under is "
                 "below. The book is on the table. The cat is under the table.",
                 "واژه‌های مکان: in یعنی درون، on یعنی روی و under یعنی زیر. The "
                 "book is on the table، The cat is under the table."),
            ],
            [
                ("There is a park near my house.", "نزدیک خانه‌ام پارکی هست."),
                ("There are three shops on this street.",
                 "در این خیابان سه مغازه هست."),
                ("The keys are in my bag.", "کلیدها در کیف من هستند."),
            ],
            [
                mcq("___ a bank near here?", "نزدیک اینجا بانکی هست؟",
                    ["Is there", "Are there", "There is", "Has"], 0,
                    "One thing takes is there.", "یک چیز is there می‌گیرد."),
                mcq("There ___ two schools here.", "اینجا دو مدرسه هست.",
                    ["is", "are", "be", "has"], 1,
                    "Two schools is plural: there are.",
                    "دو مدرسه جمع است: there are."),
            ],
            [
                mcq("The cat is ___ the table. (under it)",
                    "گربه ___ میز است.", ["on", "in", "under", "at"], 2,
                    "Under means below.", "under یعنی زیر."),
                gap("There ___ a hospital near my house.", ["is"],
                    "One hospital is singular.", "یک بیمارستان مفرد است.",
                    "one word"),
                gap("My phone is ___ my bag. (inside)", ["in"],
                    "Inside is in.", "درون یعنی in.", "one word"),
            ],
        ),
        lesson(
            "pre-u5-l2", "vocabulary",
            ("Shop, school, park, bank", "Shop، school، park، bank"),
            ("Name eight places and four direction words.",
             "هشت جا و چهار واژهٔ جهت را نام ببر."),
            [
                ("Places you can walk to: shop, school, park, bank, hospital, "
                 "bus stop, cafe, house. The stress is on the first syllable: "
                 "HOS-pital, BUS stop.",
                 "جاهایی که پیاده می‌شود رفت: shop، school، park، bank، "
                 "hospital، bus stop، cafe، house. تکیه روی هجای اول است: "
                 "HOS-pital، BUS stop."),
                ("Directions: left, right, near, far. On the left means at "
                 "your left side. Turn left is the instruction for walking or "
                 "driving.",
                 "جهت‌ها: left، right، near، far. On the left یعنی در سمت چپ تو. "
                 "Turn left دستور حرکت است."),
            ],
            [
                ("The bank is on the left.", "بانک در سمت چپ است."),
                ("The park is near the school.", "پارک نزدیک مدرسه است."),
                ("Is the hospital far from here?",
                 "بیمارستان از اینجا دور است؟"),
            ],
            [
                mcq("You buy bread at a ___.", "نان را از ___ می‌خری.",
                    ["bank", "shop", "hospital", "park"], 1,
                    "A shop sells bread.", "مغازه نان می‌فروشد."),
                mcq("The opposite of near is ___.", "متضاد near ___ است.",
                    ["left", "far", "right", "under"], 1,
                    "Near and far are a pair.", "near و far یک جفت‌اند."),
            ],
            [
                mcq("You see a doctor at a ___.", "پزشک را در ___ می‌بینی.",
                    ["park", "bank", "hospital", "cafe"], 2,
                    "Hospitals have doctors.", "بیمارستان پزشک دارد."),
                gap("Turn ___, and the bank is on your right.",
                    ["left", "right"], "Either direction fits the sentence.",
                    "هر جهتی در این جمله جا می‌شود.", "one word"),
                mcq("You wait for a bus at a ___.", "برای اتوبوس در ___ "
                    "منتظر می‌مانی.",
                    ["bus stop", "bank", "park", "shop"], 0,
                    "A bus stop is where buses stop.", "bus stop جای ایستادن "
                    "اتوبوس است."),
            ],
        ),
        lesson(
            "pre-u5-l3", "listening",
            ("Turn left at the bank", "سر بانک به چپ بپیچ"),
            ("Follow two short directions and arrive at the right place.",
             "دو مسیر کوتاه را دنبال کن و به جای درست برس."),
            [
                ("Directions come in a fixed order: go straight, turn left or "
                 "right, and then look for the place. Listen for the place "
                 "name last.",
                 "مسیرها ترتیب ثابتی دارند: go straight، turn left یا right و "
                 "بعد جای مورد نظر را ببین. نام مکان را آخر بشنو."),
                ("Near and far are relative: near here means a short walk, far "
                 "means you need a bus or a car.",
                 "near و far نسبی‌اند: near here یعنی پیادهٔ کوتاه و far یعنی "
                 "اتوبوس یا ماشین لازم داری."),
            ],
            [
                ("Go straight, then turn left at the bank.",
                 "مستقیم برو، بعد سر بانک به چپ بپیچ."),
                ("The hospital is far from here. Take a bus.",
                 "بیمارستان از اینجا دور است. سوار اتوبوس شو."),
            ],
            [
                mcq("Where do you turn?", "کجا می‌پیچی؟",
                    ["at the park", "at the bank", "at the school",
                     "at the shop"], 1, "Turn left at the bank.",
                    "سر بانک به چپ بپیچ."),
                mcq("Is the hospital near?", "بیمارستان نزدیک است؟",
                    ["yes", "no, it is far", "it is here", "no, it is "
                     "closed"], 1, "Take a bus: it is far.",
                    "سوار اتوبوس شو: دور است."),
            ],
            [
                listen("The shop is near the school. Go straight and turn "
                       "right.",
                       "Where is the shop?", "مغازه کجاست؟",
                       ["near the park", "near the school", "near the bank",
                        "far from here"], 1,
                       "It is near the school.", "نزدیک مدرسه است."),
                listen("The bank is on the left. The cafe is on the right.",
                       "Where is the cafe?", "کافه کجاست؟",
                       ["on the left", "on the right", "near the bank",
                        "under the school"], 1,
                       "The cafe is on the right.", "کافه سمت راست است."),
                listen("Go straight. The bus stop is in front of the park.",
                       "What is in front of the park?", "چه چیزی جلوی پارک "
                       "است؟",
                       ["the bank", "the school", "the bus stop", "the shop"],
                       2, "The bus stop is in front of the park.",
                       "ایستگاه اتوبوس جلوی پارک است."),
            ],
        ),
        lesson(
            "pre-u5-l4", "speaking",
            ("Where is the bank?", "بانک کجاست؟"),
            ("Ask for a place and understand the answer.",
             "جای یک مکان را بپرس و پاسخ را بفهم."),
            [
                ("The question has two forms: Where is the bank? for one "
                 "place, and Where are the shops? for many. Add please at the "
                 "end to be polite.",
                 "پرسش دو شکل دارد: Where is the bank? برای یک جا و Where are "
                 "the shops? برای چند جا. برای ادب please را آخر بگذار."),
                ("Thank the person, and repeat the key word: The bank, on the "
                 "left? This checks that you understood, and it is what fluent "
                 "speakers do too.",
                 "از طرف تشکر کن و واژهٔ کلیدی را تکرار کن: The bank, on the "
                 "left? این فهمیدن را بررسی می‌کند و گویشوران روان هم همین "
                 "کار را می‌کنند."),
            ],
            [
                ("Excuse me, where is the bank, please?",
                 "ببخشید، بانک کجاست، لطفاً؟"),
                ("Go straight and turn left. — Thank you.",
                 "مستقیم برو و به چپ بپیچ. — متشکرم."),
            ],
            [
                mcq("Which question is polite?", "کدام پرسش مؤدب است؟",
                    ["Where bank?", "Bank where?", "Excuse me, where is the "
                     "bank, please?", "The bank."], 2,
                    "Excuse me and please make it polite.",
                    "Excuse me و please آن را مؤدب می‌کنند."),
                mcq("For many shops you ask ___.", "برای چند مغازه می‌پرسی "
                    "___.",
                    ["where is the shops", "where are the shops",
                     "where the shops", "where shops is"], 1,
                    "Plural takes are.", "جمع are می‌گیرد."),
            ],
            [
                say("Excuse me, where is the bank, please?",
                    "ببخشید، بانک کجاست، لطفاً؟"),
                say("Go straight and turn left. The bank is on the right.",
                    "مستقیم برو و به چپ بپیچ. بانک سمت راست است."),
                say("Thank you. The bank, on the right?",
                    "متشکرم. بانک، سمت راست؟"),
            ],
            dialogue=dialogue([
                ("You", "Excuse me, where is the hospital, please?",
                 "ببخشید، بیمارستان کجاست، لطفاً؟"),
                ("Woman", "Go straight, then turn right at the park.",
                 "مستقیم برو، بعد سر پارک به راست بپیچ."),
                ("You", "Is it far?", "دور است؟"),
                ("Woman", "No, five minutes.", "نه، پنج دقیقه."),
            ]),
        ),
    ],
)

U6 = unit(
    "pre-u6",
    ("Every day", "هر روز"),
    ("Talk about your day: what you do, and when.",
     "از روزت بگو: چه می‌کنی و کِی."),
    [
        lesson(
            "pre-u6-l1", "grammar",
            ("I work, I study, I live", "I work، I study، I live"),
            ("Use the present simple for things you do every day.",
             "برای کارهایی که هر روز می‌کنی حال ساده را به کار ببر."),
            [
                ("The present simple describes habits and facts: I work in a "
                 "shop. We live in Tehran. The verb does not change with I, "
                 "you, we and they.",
                 "حال ساده عادت و واقعیت را می‌گوید: I work in a shop، We live "
                 "in Tehran. فعل با I/you/we/they عوض نمی‌شود."),
                ("For he, she and it, add -s: she works, he lives. This is the "
                 "one change you must not forget.",
                 "با he/she/it یک -s اضافه می‌شود: she works، he lives. این "
                 "تنها تغییری است که نباید فراموش شود."),
            ],
            [
                ("I study English every day.", "هر روز انگلیسی می‌خوانم."),
                ("She works in a hospital.", "او در بیمارستان کار می‌کند."),
                ("They live near the park.", "آن‌ها نزدیک پارک زندگی می‌کنند."),
            ],
            [
                mcq("He ___ in a bank.", "او در بانک کار می‌کند.",
                    ["work", "works", "working", "is work"], 1,
                    "He takes -s.", "he با -s می‌آید."),
                mcq("I ___ English.", "انگلیسی می‌خوانم.",
                    ["studies", "study", "studying", "am study"], 1,
                    "I takes the base form.", "I صورت پایه می‌گیرد."),
            ],
            [
                mcq("She ___ near the school.", "او نزدیک مدرسه زندگی می‌کند.",
                    ["live", "lives", "living", "is live"], 1,
                    "She takes -s.", "she با -s می‌آید."),
                gap("We ___ in Shiraz.", ["live"], "We takes the base form.",
                    "we صورت پایه می‌گیرد.", "one word"),
                gap("My brother ___ every day.", ["works", "studies"],
                    "He is third person: add -s.", "سوم‌شخص است: -s بگیرد.",
                    "one word"),
            ],
        ),
        lesson(
            "pre-u6-l2", "vocabulary",
            ("Wake up, eat, work, sleep", "Wake up، eat، work، sleep"),
            ("Name eight daily actions and the parts of the day.",
             "هشت کار روزانه و بخش‌های روز را نام ببر."),
            [
                ("A day in order: wake up, get up, eat breakfast, go to work "
                 "or school, eat lunch, come home, eat dinner, sleep. Wake up "
                 "is opening your eyes; get up is leaving the bed.",
                 "یک روز به ترتیب: wake up، get up، eat breakfast، go to work، "
                 "eat lunch، come home، eat dinner، sleep. wake up باز کردن "
                 "چشم است و get up بیرون آمدن از تخت."),
                ("Parts of the day: morning, afternoon, evening, night. In the "
                 "morning, in the afternoon, in the evening, but at night.",
                 "بخش‌های روز: morning، afternoon، evening، night. با in the "
                 "morning/afternoon/evening ولی at night."),
            ],
            [
                ("I wake up at seven.", "ساعت هفت بیدار می‌شوم."),
                ("She works in the morning.", "او صبح کار می‌کند."),
                ("We eat dinner at night.", "ما شب شام می‌خوریم."),
            ],
            [
                mcq("You ___ at seven and get out of bed.",
                    "ساعت هفت ___ و از تخت بیرون می‌آیی.",
                    ["wake up", "sleep", "eat", "work"], 0,
                    "Waking comes before getting up.", "بیدار شدن پیش از "
                    "برخاستن است."),
                mcq("The meal in the evening is ___.", "وعدهٔ شب ___ است.",
                    ["breakfast", "lunch", "dinner", "tea"], 2,
                    "Dinner is the evening meal.", "dinner وعدهٔ شب است."),
            ],
            [
                mcq("Which comes first in the day?", "کدام اول روز می‌آید؟",
                    ["dinner", "lunch", "breakfast", "night"], 2,
                    "Breakfast is the first meal.", "breakfast نخستین وعده "
                    "است."),
                gap("I go to work in the ___.", ["morning", "afternoon"],
                    "Either part of the day fits.", "هر بخشی از روز جا می‌شود.",
                    "one word"),
                mcq("At 11 p.m. you ___.", "ساعت ۱۱ شب ___.",
                    ["eat breakfast", "sleep", "go to school", "wake up"],
                    1, "Late night is for sleeping.", "شب دیر برای خوابیدن "
                    "است."),
            ],
        ),
        lesson(
            "pre-u6-l3", "reading",
            ("My day", "روز من"),
            ("Read a short description of a day and put the actions in order.",
             "توصیف کوتاهی از یک روز را بخوان و کارها را به ترتیب بگذار."),
            [
                ("Read for times and actions. Every sentence in a description "
                 "like this has one action and often one time.",
                 "برای زمان‌ها و کارها بخوان. هر جمله در چنین توصیفی یک کار و "
                 "اغلب یک زمان دارد."),
                ("At seven, at eight: at is the word for clock time. In the "
                 "morning is for the part of the day.",
                 "At seven، at eight: at برای ساعت است. in the morning برای بخش "
                 "روز."),
            ],
            [
                ("I wake up at seven. I eat breakfast at eight.",
                 "ساعت هفت بیدار می‌شوم. ساعت هشت صبحانه می‌خورم."),
                ("I work in the morning and study in the evening.",
                 "صبح کار می‌کنم و عصر درس می‌خوانم."),
            ],
            [
                mcq("What time does the writer wake up?", "نویسنده چه ساعتی "
                    "بیدار می‌شود؟",
                    ["six", "seven", "eight", "nine"], 1,
                    "I wake up at seven.", "ساعت هفت بیدار می‌شوم."),
                mcq("What does the writer do in the evening?",
                    "نویسنده عصر چه می‌کند؟",
                    ["works", "studies", "sleeps", "cooks"], 1,
                    "Study is in the evening.", "درس خواندن عصر است."),
            ],
            [
                mcq("When does the writer eat breakfast?",
                    "نویسنده کِی صبحانه می‌خورد؟",
                    ["at six", "at seven", "at eight", "at nine"], 2,
                    "I eat breakfast at eight.", "ساعت هشت صبحانه می‌خورم."),
                mcq("How many times does the writer eat in the text?",
                    "نویسنده در متن چند بار غذا می‌خورد؟",
                    ["once", "twice", "three times", "never"], 2,
                    "Breakfast, lunch and dinner are mentioned.",
                    "صبحانه، ناهار و شام هر سه در متن آمده‌اند."),
            ],
            passage=passage(
                ("My day", "روز من"),
                ("My name is Sara. I wake up at seven. I eat breakfast at "
                 "eight: bread, cheese and tea. I work in a shop in the "
                 "morning. I eat lunch at one. In the evening I study English. "
                 "I eat dinner at eight and I sleep at eleven.",
                 "نام من سارا است. ساعت هفت بیدار می‌شوم. ساعت هشت صبحانه "
                 "می‌خورم: نان، پنیر و چای. صبح در مغازه کار می‌کنم. ساعت یک "
                 "ناهار می‌خورم. عصر انگلیسی می‌خوانم. ساعت هشت شام می‌خورم و "
                 "ساعت یازده می‌خوابم."),
            ),
        ),
        lesson(
            "pre-u6-l4", "writing",
            ("Four sentences about my day",
             "چهار جمله دربارهٔ روز من"),
            ("Write four sentences with a time and an action in each.",
             "چهار جمله بنویس که در هرکدام زمانی و کاری باشد."),
            [
                ("Pattern: time first or last. I wake up at seven. At seven, I "
                 "wake up. Both are correct; the first is easier.",
                 "الگو: زمان اول یا آخر. I wake up at seven. At seven, I wake "
                 "up. هر دو درست‌اند و اولی آسان‌تر است."),
                ("Use at for clock times and in the morning for parts of the "
                 "day. Do not write at the morning.",
                 "برای ساعت at و برای بخش روز in the morning به کار ببر. «at "
                 "the morning» ننویس."),
            ],
            [
                ("I wake up at six.", "ساعت شش بیدار می‌شوم."),
                ("I work in the morning.", "صبح کار می‌کنم."),
            ],
            [
                mcq("Which is correct?", "کدام درست است؟",
                    ["I wake up at the morning.", "I wake up in the morning.",
                     "I wake up on morning.", "I wake up to morning."], 1,
                    "Parts of the day take in.", "بخش‌های روز in می‌گیرند."),
                mcq("Which sentence has a time and an action?",
                    "کدام جمله زمان و کار دارد؟",
                    ["My day.", "I eat lunch at one.", "Lunch.", "At one."],
                    1, "It has both a time and a verb.", "هم زمان دارد هم فعل."),
            ],
            [
                write("Write four sentences about your day. Use at with clock "
                      "times. Say when you wake up, when you eat, what you do "
                      "in the morning, and when you sleep.",
                      "چهار جمله دربارهٔ روزت بنویس. با ساعت‌ها at به کار ببر. "
                      "بگو کِی بیدار می‌شوی، کِی غذا می‌خوری، صبح چه می‌کنی و "
                      "کِی می‌خوابی.",
                      30, ["and"], "Four sentences, each with at + time, "
                      "present simple, no -s mistakes with I.",
                      "چهار جمله، هر یک با at + زمان، حال ساده، بدون خطای -s "
                      "با I."),
                gap("I sleep ___ eleven.", ["at"], "Clock times take at.",
                    "ساعت‌ها at می‌گیرند.", "one word"),
                mcq("Which verb is a daily action?", "کدام فعل کار روزانه "
                    "است؟",
                    ["window", "study", "table", "bank"], 1,
                    "Study is a verb.", "study فعل است."),
            ],
        ),
    ],
)
