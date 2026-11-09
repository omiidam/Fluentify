#!/usr/bin/env python3
"""A1, deepened: one more lesson in each of the six units, and two new units.

A1 is the one course written by hand inside path.json, so these lessons are
merged by `tools/extend_a1.py` rather than by build_path.py.
"""

from course_kit import (dialogue, gap, lesson, listen, mcq, passage, say, unit,
                       write)

EXTRA = {
    "u1": [
        lesson(
            "a1-u1-l4", "listening",
            ("Where are you from?", "اهل کجایی؟"),
            ("Hear a name, a country and a job in a short introduction.",
             "در یک معرفی کوتاه نام، کشور و شغل را بشنو."),
            [
                ("The three pieces in a first introduction come in a "
                 "predictable order: name, country, job. I am Nima. I am from "
                 "Iran. I am a student.",
                 "سه قطعهٔ نخستین معرفی ترتیب قابل پیش‌بینی دارند: نام، کشور، "
                 "شغل. I am Nima. I am from Iran. I am a student."),
                ("Country names take from, and jobs take a or an: from "
                 "Turkey, a teacher. Listen for from and a, because they tell "
                 "you which piece is coming.",
                 "نام کشور from می‌گیرد و شغل a یا an: from Turkey، a teacher. به "
                 "from و a گوش کن، چون می‌گویند کدام قطعه می‌آید."),
            ],
            [
                ("I am Nima. I am from Iran. I am a student.",
                 "من نیما هستم. اهل ایرانم. دانش‌آموزم."),
                ("She is from Turkey. She is a teacher.",
                 "او اهل ترکیه است. معلم است."),
            ],
            [
                mcq("Where is Nima from?", "نیما اهل کجاست؟",
                    ["Turkey", "Iran", "Italy", "Canada"], 1,
                    "He says from Iran.", "می‌گوید from Iran."),
                mcq("What is his job?", "شغلش چیست؟",
                    ["teacher", "student", "driver", "doctor"], 1,
                    "He is a student.", "دانش‌آموز است."),
            ],
            [
                listen("Hello. I am Leyla. I am from Turkey. I am a teacher.",
                       "What is Leyla's job?", "شغل لیلا چیست؟",
                       ["student", "teacher", "doctor", "driver"], 1,
                       "She says a teacher.", "می‌گوید a teacher."),
                listen("This is my friend Tom. He is from Canada. He is a "
                       "driver.", "Where is Tom from?", "تام اهل کجاست؟",
                       ["Iran", "Canada", "Turkey", "Italy"], 1,
                       "He is from Canada.", "اهل کاناداست."),
            ],
        ),
    ],
    "u2": [
        lesson(
            "a1-u2-l4", "writing",
            ("Four sentences about your family",
             "چهار جمله دربارهٔ خانواده‌ات"),
            ("Describe three people with have or has and one possession each.",
             "سه نفر را با have یا has و یک دارایی برای هرکدام توصیف کن."),
            [
                ("Have got is the everyday way to say what someone owns or "
                 "has: she has got two brothers. In negatives and questions it "
                 "behaves like have: she hasn't got a car, has he got a phone?",
                 "have got راه روزمرهٔ گفتن دارایی است: she has got two "
                 "brothers. در منفی و پرسش مثل have رفتار می‌کند: she hasn't "
                 "got a car، has he got a phone?"),
                ("Keep one person per sentence and put the number or the "
                 "object at the end: My sister has a new phone. The end of "
                 "the sentence is where English puts the new information.",
                 "در هر جمله یک نفر و عدد یا شیء را در پایان بگذار: My sister "
                 "has got a new phone. انگلیسی اطلاعات تازه را در پایان "
                 "می‌گذارد."),
            ],
            [
                ("My brother has a bike.", "برادرم دوچرخه دارد."),
                ("My parents have a small shop.",
                 "پدر و مادرم مغازهٔ کوچکی دارند."),
            ],
            [
                mcq("She ___ two sisters.", "او دو خواهر دارد.",
                    ["have", "has", "is", "are"], 1,
                    "She takes has.", "she با has می‌آید."),
                mcq("Which sentence is correct?", "کدام جمله درست است؟",
                    ["My brother have a bike.", "My brother has got a "
                     "bike.", "My brother has get a bike.", "My brother got "
                     "have a bike."], 1,
                    "He takes has.", "he با has می‌آید."),
            ],
            [
                write("Write four sentences about your family. Use have got "
                      "for each person, and put the thing they have at the end "
                      "of the sentence.",
                      "چهار جمله دربارهٔ خانواده‌ات بنویس. برای هر نفر have got به "
                      "کار ببر و چیزی که دارد را در پایان جمله بگذار.",
                      40, ["and"], "Four sentences, one person each, have got "
                      "correct, the object last.", "چهار جمله، در هر یک یک نفر، "
                      "have got درست و شیء در پایان."),
                gap("My sister ___ a new phone.", ["has"],
                    "Third person takes has.", "سوم‌شخص has می‌گیرد.", "one word"),
                mcq("Which is a question with have?", "کدام پرسش با have "
                    "got است؟",
                    ["Does he have a car?", "He has a car?", "Does he got a "
                     "car?", "Is he got a car?"], 0,
                    "Has comes first in the question.",
                    "has در پرسش اول می‌آید."),
            ],
        ),
    ],
    "u3": [
        lesson(
            "a1-u3-l4", "listening",
            ("What time does it open?",
             "چه ساعتی باز می‌شود؟"),
            ("Understand opening times and simple schedules.",
             "ساعت باز شدن و جدول‌های زمانی ساده را بفهم."),
            [
                ("Times are said two ways: seven o'clock and seven. For "
                 "half past, use half past seven; for fifteen minutes, a "
                 "quarter past or a quarter to.",
                 "ساعت‌ها دو جور گفته می‌شوند: seven o'clock و seven. برای نیم، "
                 "half past seven و برای ربع، a quarter past یا a quarter to."),
                ("A schedule question usually asks about the difference "
                 "between two times: it opens at nine and closes at five is "
                 "eight hours.",
                 "پرسش جدول زمانی معمولاً تفاوت دو ساعت را می‌پرسد: از نُه باز "
                 "می‌شود و پنج بسته می‌شود، یعنی هشت ساعت."),
            ],
            [
                ("The shop opens at nine o'clock.", "مغازه ساعت نُه باز "
                 "می‌شود."),
                ("The class starts at half past eight.",
                 "کلاس ساعت هشت و نیم شروع می‌شود."),
            ],
            [
                mcq("When does the shop open?", "مغازه کِی باز می‌شود؟",
                    ["eight", "nine", "half past nine", "ten"], 1,
                    "At nine o'clock.", "ساعت نُه."),
                mcq("'Half past eight' is ___.", "«half past eight» یعنی ___.",
                    ["8:15", "8:30", "8:45", "9:30"], 1,
                    "Half past is thirty minutes after.",
                    "half past یعنی سی دقیقه پس از ساعت."),
            ],
            [
                listen("The bank opens at nine and closes at four.",
                       "How long is the bank open?",
                       "بانک چند ساعت باز است؟",
                       ["six hours", "seven hours", "eight hours",
                        "nine hours"], 1,
                       "Nine to four is seven hours.", "نُه تا چهار هفت ساعت "
                       "است."),
                listen("The cafe opens at ten, not at nine.",
                       "When does the cafe open?", "کافه کِی باز می‌شود؟",
                       ["nine", "ten", "eleven", "half past ten"], 1,
                       "At ten.", "ساعت ده."),
            ],
        ),
    ],
    "u4": [
        lesson(
            "a1-u4-l4", "speaking",
            ("Two coffees, please", "دو قهوه، لطفاً"),
            ("Order food and drink, ask the price, and pay.",
             "خوراکی و نوشیدنی سفارش بده، قیمت بپرس و پول بده."),
            [
                ("An order has three sentences: what you want, how many, and "
                 "the polite tag. Two coffees, please. Can I have a glass of "
                 "water? How much is it?",
                 "سفارش سه جمله دارد: چه می‌خواهی، چند تا و مؤدبانه‌اش. Two "
                 "coffees, please. Can I have a glass of water? How much is "
                 "it?"),
                ("For the price, say how much is it? and answer with it's plus "
                 "the amount. In a shop the assistant may ask anything else? "
                 "which means 'do you want more?'",
                 "برای قیمت بگو how much is it? و با it's و مبلغ پاسخ بده. در "
                 "مغازه فروشنده ممکن است بپرسد anything else? یعنی «چیز دیگری "
                 "می‌خواهی؟»"),
            ],
            [
                ("Two coffees, please.", "دو قهوه، لطفاً."),
                ("How much is it? — It's four pounds.",
                 "چند است؟ — چهار پوند."),
                ("Can I have the bill, please?", "می‌شود صورتحساب را بیاورید؟"),
            ],
            [
                mcq("Which sentence asks the price?", "کدام جمله قیمت "
                    "می‌پرسد؟",
                    ["How many is it?", "How much is it?", "What is it cost?",
                     "How is it?"], 1,
                    "How much asks a price.", "how much قیمت را می‌پرسد."),
                mcq("'Anything else?' means ___.", "«Anything else?» یعنی ___.",
                    ["is that all you want", "do you want more", "the bill",
                     "the price"], 1,
                    "It offers more, not fewer.", "بیشتر پیشنهاد می‌دهد، نه "
                    "کمتر."),
            ],
            [
                say("Two coffees, please, and a glass of water.",
                    "دو قهوه لطفاً و یک لیوان آب."),
                say("How much is it? — It's four pounds.",
                    "چند است؟ — چهار پوند."),
                say("Can I have the bill, please?",
                    "می‌شود صورتحساب را بیاورید؟"),
            ],
            dialogue=dialogue([
                ("Assistant", "Good morning. What would you like?",
                 "صبح بخیر. چه میل دارید؟"),
                ("You", "Two coffees, please.", "دو قهوه، لطفاً."),
                ("Assistant", "Anything else?", "چیز دیگری؟"),
                ("You", "No, thank you. How much is it?",
                 "نه، ممنون. چند است؟"),
            ]),
        ),
    ],
    "u5": [
        lesson(
            "a1-u5-l4", "writing",
            ("A postcard in forty words",
             "کارت‌پستالی در چهل واژه"),
            ("Write a short postcard that says where you are and what you "
             "have done.",
             "کارت‌پستال کوتاهی بنویس که بگوید کجایی و چه کرده‌ای."),
            [
                ("A postcard has four moves: where you are, who you are with, "
                 "one thing you did, and a closing line. Forty words is "
                 "enough for all four.",
                 "کارت‌پستال چهار حرکت دارد: کجایی، با کی هستی، یک کار که کردی و "
                 "یک جملهٔ پایانی. چهل واژه برای هر چهار کافی است."),
                ("Use the present for where you are and the past for what you "
                 "did: I am in Shiraz. We visited the garden yesterday.",
                 "برای مکان از حال و برای کار گذشته از گذشته استفاده کن: I am "
                 "in Shiraz. We visited the garden yesterday."),
            ],
            [
                ("I am in Shiraz with my family.",
                 "با خانواده‌ام در شیرازم."),
                ("Yesterday we visited the garden. See you soon!",
                 "دیروز باغ را دیدیم. به‌زودی می‌بینمت!"),
            ],
            [
                mcq("Which sentence says what you did?", "کدام جمله می‌گوید چه "
                    "کردی؟",
                    ["I am in Shiraz.", "We visited the garden yesterday.",
                     "It is hot here.", "See you soon."], 1,
                    "Past simple reports the activity.",
                    "گذشتهٔ ساده فعالیت را می‌گوید."),
                mcq("A postcard should include ___.", "کارت‌پستال باید ___ را "
                    "داشته باشد.",
                    ["a list of prices", "where you are and one thing you did",
                     "a full diary", "an address in every line"], 1,
                    "Place and one activity.", "مکان و یک فعالیت."),
            ],
            [
                write("Write a postcard of about 40 words from a place you "
                      "know or imagine. Say where you are, who with, one thing "
                      "you did, and close with a greeting.",
                      "کارت‌پستالی حدود ۴۰ واژه از جایی که می‌شناسی یا تصور "
                      "می‌کنی بنویس. بگو کجایی، با کی، یک کار که کردی و با سلامی "
                      "تمام کن.",
                      40, ["and"], "Present for place, past for activity, one "
                      "greeting at the end.", "حال برای مکان، گذشته برای فعالیت "
                      "و یک سلام در پایان."),
                gap("Yesterday we ___ (visit) the garden.", ["visited"],
                    "Regular past adds -ed.", "گذشتهٔ باقاعده -ed می‌گیرد.",
                    "one word"),
                mcq("Which closing is suitable for a postcard?",
                    "کدام پایان برای کارت‌پستال مناسب است؟",
                    ["Yours faithfully,", "See you soon!", "Dear Sir,",
                     "I remain yours,"], 1,
                    "Postcards are informal.", "کارت‌پستال غیررسمی است."),
            ],
        ),
    ],
    "u6": [
        lesson(
            "a1-u6-l4", "speaking",
            ("What did you do on the weekend?",
             "آخر هفته چه کردی؟"),
            ("Talk about a past weekend with three short sentences.",
             "دربارهٔ آخر هفتهٔ گذشته با سه جملهٔ کوتاه حرف بزن."),
            [
                ("A weekend answer needs a day, an activity and a comment: on "
                 "Saturday I went to the market, and it was very busy.",
                 "پاسخ آخر هفته به یک روز، یک فعالیت و یک نظر نیاز دارد: on "
                 "Saturday I went to the market, and it was very busy."),
                ("Days take on: on Saturday, on Sunday. The past forms you "
                 "need most are went, saw, ate, met and was.",
                 "روزها on می‌گیرند: on Saturday، on Sunday. پرکاربردترین "
                 "گذشته‌ها went، saw، ate، met و was هستند."),
            ],
            [
                ("On Saturday I went to the market.",
                 "شنبه به بازار رفتم."),
                ("I met my friend and we ate lunch.",
                 "دوستم را دیدم و ناهار خوردیم."),
            ],
            [
                mcq("Which is the past of go?", "گذشتهٔ go کدام است؟",
                    ["goed", "went", "gone", "going"], 1,
                    "Go is irregular: went.", "go بی‌قاعده است: went."),
                mcq("Days take ___.", "روزها ___ می‌گیرند.",
                    ["in", "on", "at", "to"], 1,
                    "On Saturday.", "با on Saturday."),
            ],
            [
                say("On Saturday I went to the market with my sister.",
                    "شنبه با خواهرم به بازار رفتم."),
                say("We saw a movie and ate lunch near the park.",
                    "فیلمی دیدیم و نزدیک پارک ناهار خوردیم."),
                say("On Sunday I stayed at home because it was raining.",
                    "یکشنبه خانه ماندم چون باران می‌آمد."),
            ],
        ),
    ],
}

U7 = unit(
    "u7",
    ("Shopping and money", "خرید و پول"),
    ("Ask for what you want in a shop, ask the price, and choose between two "
     "things.",
     "در مغازه آنچه می‌خواهی بخواه، قیمت بپرس و بین دو چیز انتخاب کن."),
    [
        lesson(
            "a1-u7-l1", "grammar",
            ("This one, those ones, I would like",
             "This one، those ones، I would like"),
            ("Point at the thing you want without repeating its name.",
             "به چیزی که می‌خواهی اشاره کن بی‌آنکه نامش را تکرار کنی."),
            [
                ("One replaces a singular noun and ones replaces a plural: "
                 "this shirt is large, do you have a smaller one? The blue "
                 "shoes are nice; I like those ones.",
                 "one جای اسم مفرد و ones جای اسم جمع می‌نشیند: this shirt is "
                 "large, do you have a smaller one? The blue shoes are nice; "
                 "I like those ones."),
                ("I would like is the polite way to ask for something in a "
                 "shop, and it is followed by a noun or by one: I would like "
                 "this one, please.",
                 "I would like راه مؤدب خواستن چیزی در مغازه است و پس از آن اسم "
                 "یا one می‌آید: I would like this one, please."),
            ],
            [
                ("I would like a smaller one, please.",
                 "یک کوچک‌تر می‌خواهم، لطفاً."),
                ("These are nice, but I prefer those ones.",
                 "این‌ها خوب‌اند، ولی آن‌ها را ترجیح می‌دهم."),
            ],
            [
                mcq("Do you have a smaller ___?", "کوچک‌ترش را دارید؟",
                    ["one", "ones", "it", "them"], 0,
                    "One replaces a singular noun.", "one جای اسم مفرد است."),
                mcq("I like those ___.", "آن‌ها را دوست دارم.",
                    ["one", "ones", "it", "shoe"], 1,
                    "Those is plural, so ones.", "those جمع است، پس ones."),
            ],
            [
                mcq("Which is the polite request?", "کدام درخواست مؤدب "
                    "است؟",
                    ["Give me that one.", "I would like that one, please.",
                     "That one now.", "I want it."], 1,
                    "I would like + please.", "ساخت «I would like» به‌همراه please."),
                gap("These shoes are too big. Have you got smaller ___?",
                    ["ones"], "Shoes is plural.", "shoes جمع است.",
                    "one word"),
                mcq("___ shirt is small. I need a bigger one.",
                    "این پیراهن کوچک است. بزرگ‌تری لازم دارم.",
                    ["These", "This", "Those", "They"], 1,
                    "One shirt takes this.", "یک پیراهن this می‌گیرد."),
            ],
        ),
        lesson(
            "a1-u7-l2", "vocabulary",
            ("Clothes, sizes and prices", "لباس، اندازه و قیمت"),
            ("Name ten clothes words and ask for a size and a price.",
             "ده واژهٔ لباس را نام ببر و اندازه و قیمت بپرس."),
            [
                ("Clothes: shirt, T-shirt, trousers, jeans, shoes, coat, "
                 "jacket, hat, dress, skirt. Trousers and jeans are always "
                 "plural in English: they are nice, not it is nice.",
                 "لباس‌ها: shirt، T-shirt، trousers، jeans، shoes، coat، "
                 "jacket، hat، dress، skirt. trousers و jeans در انگلیسی همیشه "
                 "جمع‌اند: they are nice نه it is nice."),
                ("Sizes are small, medium and large, shortened to S, M and L. "
                 "Prices are said with the currency after the number: twelve "
                 "pounds, or twelve pounds fifty.",
                 "اندازه‌ها small، medium و large هستند و به S، M و L کوتاه "
                 "می‌شوند. قیمت با واحد پس از عدد گفته می‌شود: twelve pounds یا "
                 "twelve pounds fifty."),
            ],
            [
                ("Do you have this jacket in medium?",
                 "این کاپشن را در سایز متوسط دارید؟"),
                ("The trousers are forty pounds.",
                 "شلوار چهل پوند است."),
            ],
            [
                mcq("Trousers are ___.", "trousers ___ است.",
                    ["singular", "plural", "uncountable", "a verb"], 1,
                    "They take a plural verb.", "فعل جمع می‌گیرند."),
                mcq("M is the short form of ___.", "M کوتاه‌شدهٔ ___ است.",
                    ["small", "medium", "many", "money"], 1,
                    "S, M, L: small, medium, large.", "S، M، L: small، medium، "
                    "large."),
            ],
            [
                mcq("Which is a piece of clothing?", "کدام لباس است؟",
                    ["price", "jacket", "size", "shop"], 1,
                    "A jacket is worn.", "jacket پوشیده می‌شود."),
                gap("Do you have this shirt in ___?", ["medium", "large",
                    "small"], "Sizes take in.", "اندازه‌ها in می‌گیرند.",
                    "one word"),
                mcq("Which sentence is correct?", "کدام جمله درست است؟",
                    ["The jeans is nice.", "The jeans are nice.",
                     "The jeans am nice.", "A jeans are nice."], 1,
                    "Jeans is plural.", "jeans جمع است."),
            ],
        ),
        lesson(
            "a1-u7-l3", "listening",
            ("At the shop", "در مغازه"),
            ("Follow a shop conversation and note the size, color and price.",
             "گفت‌وگوی مغازه را دنبال کن و اندازه، رنگ و قیمت را یادداشت کن."),
            [
                ("Shop conversations have a fixed shape: what you want, the "
                 "size or color, the price, and the payment. You only need "
                 "to catch one detail per turn.",
                 "گفت‌وگوی مغازه شکل ثابتی دارد: چه می‌خواهی، اندازه یا رنگ، قیمت "
                 "و پرداخت. در هر نوبت فقط یک جزئیات را باید بگیرت."),
                ("Colors come before the noun: a blue shirt, black shoes. "
                 "Sizes come after in: in medium.",
                 "رنگ‌ها پیش از اسم می‌آیند: a blue shirt، black shoes. اندازه‌ها "
                 "پس از in: in medium."),
            ],
            [
                ("I would like this shirt in medium.",
                 "این پیراهن را در سایز متوسط می‌خواهم."),
                ("It is twenty-five pounds.", "بیست‌وپنج پوند است."),
            ],
            [
                mcq("What size does the customer want?", "مشتری چه سایزی "
                    "می‌خواهد؟",
                    ["small", "medium", "large", "extra large"], 1,
                    "She asks for medium.", "سایز متوسط می‌خواهد."),
                mcq("How much is it?", "چند است؟",
                    ["fifteen pounds", "twenty pounds", "twenty-five "
                     "pounds", "fifty pounds"], 2,
                    "Twenty-five pounds.", "بیست‌وپنج پوند."),
            ],
            [
                listen("I would like these shoes in black, size forty.",
                       "What color?", "چه رنگی؟",
                       ["blue", "black", "brown", "white"], 1,
                       "Black, size forty.", "مشکی، سایز چهل."),
                listen("The coat is sixty pounds and the hat is twelve.",
                       "How much is the hat?", "کلاه چند است؟",
                       ["twelve pounds", "sixty pounds", "twenty pounds",
                        "sixteen pounds"], 0,
                       "The hat is twelve.", "کلاه دوازده است."),
            ],
        ),
        lesson(
            "a1-u7-l4", "speaking",
            ("Buying something, out loud", "چیزی خریدن، با صدای بلند"),
            ("Do a whole shop exchange in five short turns.",
             "یک گفت‌وگوی کامل مغازه را در پنج نوبت کوتاه انجام بده."),
            [
                ("The five turns: greet, ask for the thing, give the size or "
                 "color, ask the price, pay and thank. You can do all five "
                 "with the phrases you already have.",
                 "پنج نوبت: سلام، خواستن چیزی، گفتن اندازه یا رنگ، پرسیدن قیمت، "
                 "پرداخت و تشکر. هر پنج را با عبارت‌هایی که داری می‌توانی "
                 "انجام دهی."),
                ("Say the thing twice if you are not understood: the first "
                 "time normally, the second time more slowly with the size. "
                 "That is what fluent speakers do too.",
                 "اگر فهمیده نشدی، خواسته را دو بار بگو: بار اول معمولی و بار "
                 "دوم آهسته‌تر با اندازه. گویشوران روان هم همین کار را "
                 "می‌کنند."),
            ],
            [
                ("Good morning. I would like this jacket, please.",
                 "صبح بخیر. این کاپشن را می‌خواهم، لطفاً."),
                ("In medium. How much is it?",
                 "سایز متوسط. چند است؟"),
            ],
            [
                mcq("Which turn asks the price?", "کدام نوبت قیمت می‌پرسد؟",
                    ["I would like this jacket.", "How much is it?",
                     "In medium.", "Thank you."], 1,
                    "How much asks the price.", "how much قیمت را می‌پرسد."),
                mcq("If you are not understood, you should ___.",
                    "اگر فهمیده نشدی باید ___.",
                    ["leave", "repeat more slowly", "speak faster",
                     "change language"], 1,
                    "Slower with the size is the repair.",
                    "آهسته‌تر با اندازه، ترمیم است."),
            ],
            [
                say("Good morning. I would like this shirt, please.",
                    "صبح بخیر. این پیراهن را می‌خواهم، لطفاً."),
                say("In medium, in blue. How much is it?",
                    "سایز متوسط، آبی. چند است؟"),
                say("Thank you. Can I pay by card?",
                    "ممنون. می‌توانم با کارت پرداخت کنم؟"),
            ],
            dialogue=dialogue([
                ("Assistant", "Good morning. Can I help you?",
                 "صبح بخیر. کمکی می‌توانم بکنم؟"),
                ("You", "Yes, I would like this jacket in medium.",
                 "بله، این کاپشن را در سایز متوسط می‌خواهم."),
                ("Assistant", "Here you are. It is forty pounds.",
                 "بفرمایید. چهل پوند است."),
                ("You", "Thank you. Can I pay by card?",
                 "ممنون. با کارت می‌توانم پرداخت کنم؟"),
            ]),
        ),
    ],
)

U8 = unit(
    "u8",
    ("Yesterday and tomorrow", "دیروز و فردا"),
    ("Talk about the past with was, were and the past simple, and say when.",
     "با was، were و گذشتهٔ ساده از گذشته بگو و زمانش را بگو."),
    [
        lesson(
            "a1-u8-l1", "grammar",
            ("Was, were and the -ed past", "Was، were و گذشتهٔ -ed"),
            ("Use was and were for states, and the past simple for actions.",
             "برای حالت‌ها was و were و برای کارها گذشتهٔ ساده را به کار ببر."),
            [
                ("Was and were are the past of am, is and are: I was tired, "
                 "they were at home, it was cold. They describe a state, not "
                 "an action.",
                 "was و were گذشتهٔ am، is و are هستند: I was tired، they were "
                 "at home، it was cold. حالت را توصیف می‌کنند، نه کار را."),
                ("Actions take the past simple: I visited my aunt, we played "
                 "football. Regular verbs add -ed; a few common ones are "
                 "irregular: go → went, see → saw, have → had.",
                 "کارها گذشتهٔ ساده می‌گیرند: I visited my aunt، we played "
                 "football. فعل‌های باقاعده -ed می‌گیرند و چند فعل رایج بی‌قاعده‌اند: "
                 "go → went، see → saw، have → had."),
            ],
            [
                ("I was at home yesterday.", "دیروز خانه بودم."),
                ("We visited my aunt on Sunday.",
                 "یکشنبه خاله‌ام را دیدیم."),
                ("They went to the park.", "آن‌ها به پارک رفتند."),
            ],
            [
                mcq("I ___ tired yesterday.", "دیروز خسته بودم.",
                    ["am", "was", "were", "be"], 1,
                    "I takes was.", "I با was می‌آید."),
                mcq("They ___ at home.", "آن‌ها خانه بودند.",
                    ["was", "were", "are", "is"], 1,
                    "They takes were.", "they با were می‌آید."),
            ],
            [
                mcq("Which is the past of see?", "گذشتهٔ see کدام است؟",
                    ["seed", "saw", "seen", "seeing"], 1,
                    "See is irregular: saw.", "see بی‌قاعده است: saw."),
                gap("We ___ (play) football on Friday.", ["played"],
                    "Regular past adds -ed.", "گذشتهٔ باقاعده -ed می‌گیرد.",
                    "one word"),
                gap("It ___ cold last night.", ["was"], "It takes was.",
                    "it با was می‌آید.", "one word"),
            ],
        ),
        lesson(
            "a1-u8-l2", "vocabulary",
            ("Yesterday, last week, tomorrow",
             "Yesterday، last week، tomorrow"),
            ("Place past and future events in time with the right phrase.",
             "رویدادهای گذشته و آینده را با عبارت درست در زمان بگذار."),
            [
                ("Past time phrases: yesterday, last night, last week, two "
                 "days ago. Ago comes after the length of time: three days "
                 "ago, not ago three days.",
                 "عبارت‌های زمان گذشته: yesterday، last night، last week، two "
                 "days ago. ago پس از مدت می‌آید: three days ago، نه ago three "
                 "days."),
                ("Future time phrases: tomorrow, next week, on Monday, in two "
                 "days. Notice that next week has no the, but on Monday "
                 "does.",
                 "عبارت‌های زمان آینده: tomorrow، next week، on Monday، in two "
                 "days. دقت کن next week بدون the می‌آید ولی on Monday با آن."),
            ],
            [
                ("I saw her three days ago.", "سه روز پیش او را دیدم."),
                ("We are going next week.", "هفتهٔ بعد می‌رویم."),
                ("I will call you tomorrow.", "فردا زنگ می‌زنم."),
            ],
            [
                mcq("Which phrase is in the past?", "کدام عبارت در گذشته "
                    "است؟",
                    ["tomorrow", "next week", "last night", "in two days"],
                    2, "Last night has gone.", "last night گذشته است."),
                mcq("The correct order is ___.", "ترتیب درست ___ است.",
                    ["ago three days", "three days ago", "three ago days",
                     "days three ago"], 1,
                    "Ago follows the length of time.",
                    "ago پس از مدت می‌آید."),
            ],
            [
                mcq("Which phrase is in the future?", "کدام عبارت در آینده "
                    "است؟",
                    ["yesterday", "last week", "tomorrow", "two days ago"],
                    2, "Tomorrow has not happened.", "tomorrow رخ نداده است."),
                gap("I met him two weeks ___.", ["ago"],
                    "Ago marks the distance back.", "ago فاصلهٔ عقب را نشان "
                    "می‌دهد.", "one word"),
                mcq("Which is correct?", "کدام درست است؟",
                    ["next the week", "in next week", "next week",
                     "on next week"], 2,
                    "Next week takes no preposition.", "next week حرف اضافه "
                    "نمی‌گیرد."),
            ],
        ),
        lesson(
            "a1-u8-l3", "reading",
            ("A page of a diary", "یک صفحه از دفتر خاطرات"),
            ("Read a short diary entry and put its events in order.",
             "یادداشت کوتاه روزانه را بخوان و رویدادهایش را به ترتیب بگذار."),
            [
                ("A diary entry mixes states and actions: it was cold (state), "
                 "I walked to work (action). Both are past, and the order words "
                 "are usually first, then and after that.",
                 "یادداشت روزانه حالت و کار را درهم می‌آمیزد: it was cold (حالت) "
                 "و I walked to work (کار). هر دو گذشته‌اند و واژه‌های ترتیب "
                 "معمولاً first، then و after that هستند."),
                ("Read for the order, not for every word: the question will "
                 "usually ask what happened first or what happened after a "
                 "named event.",
                 "برای ترتیب بخوان، نه برای هر واژه: پرسش معمولاً می‌پرسد اول چه "
                 "شد یا پس از رویدادی نام‌برده چه شد."),
            ],
            [
                ("First I had breakfast, then I walked to work.",
                 "اول صبحانه خوردم، بعد پیاده به کار رفتم."),
                ("After that it was quiet all afternoon.",
                 "بعد از آن تمام بعدازظهر ساکت بود."),
            ],
            [
                mcq("What happened first?", "اول چه شد؟",
                    ["she walked to work", "she had breakfast",
                     "she met Ali", "she went home"], 1,
                    "Breakfast came before the walk.",
                    "صبحانه پیش از پیاده‌روی بود."),
                mcq("How was the weather?", "هوا چطور بود؟",
                    ["hot", "cold and wet", "sunny", "windy"], 1,
                    "It was cold and wet.", "سرد و خیس بود."),
            ],
            [
                mcq("What did she do after work?", "پس از کار چه کرد؟",
                    ["went home", "met Ali for coffee", "went shopping",
                     "visited her aunt"], 1,
                    "She met Ali for coffee.", "با علی قهوه خورد."),
                mcq("Which sentence describes a state?", "کدام جمله حالت را "
                    "توصیف می‌کند؟",
                    ["I walked to work.", "It was cold.", "I met Ali.",
                     "We drank coffee."], 1,
                    "Was + adjective is a state.", "was + صفت حالت است."),
            ],
            passage=passage(
                ("Monday", "دوشنبه"),
                ("It was cold and wet on Monday. First I had breakfast at "
                 "home, then I walked to work because the bus was late. The "
                 "morning was busy and the afternoon was quiet. After work I "
                 "met Ali for coffee near the station. We talked about the "
                 "weekend and then I went home at eight.",
                 "دوشنبه سرد و خیس بود. اول خانه صبحانه خوردم، بعد چون اتوبوس "
                 "دیر کرده بود پیاده به کار رفتم. صبح شلوغ بود و بعدازظهر ساکت. "
                 "پس از کار با علی نزدیک ایستگاه قهوه خوردم. دربارهٔ آخر هفته حرف "
                 "زدیم و بعد ساعت هشت خانه رفتم."),
            ),
        ),
        lesson(
            "a1-u8-l4", "writing",
            ("What I did yesterday", "دیروز چه کردم"),
            ("Write five past sentences with one time phrase each.",
             "پنج جملهٔ گذشته بنویس که در هر یک یک عبارت زمانی باشد."),
            [
                ("Use was for how things were and a past verb for what you "
                 "did. Five sentences is enough: morning, afternoon, evening, "
                 "one person, and one comment.",
                 "برای چگونگی از was و برای کار از فعل گذشته استفاده کن. پنج "
                 "جمله کافی است: صبح، بعدازظهر، عصر، یک نفر و یک نظر."),
                ("Put the time phrase first or last, but not in the middle: "
                 "Yesterday I went shopping, or I went shopping yesterday.",
                 "عبارت زمانی را اول یا آخر بگذار، نه در میانه: Yesterday I went "
                 "shopping یا I went shopping yesterday."),
            ],
            [
                ("Yesterday I visited my grandmother.",
                 "دیروز مادربزرگم را دیدم."),
                ("In the evening I watched a movie.", "عصر فیلمی دیدم."),
            ],
            [
                mcq("Which sentence is in the past?", "کدام جمله در گذشته "
                    "است؟",
                    ["I go shopping.", "I went shopping.", "I will go "
                     "shopping.", "I am shopping."], 1,
                    "Went is the past of go.", "went گذشتهٔ go است."),
                mcq("Which time phrase fits a past sentence?",
                    "کدام عبارت زمانی با جملهٔ گذشته می‌خواند؟",
                    ["tomorrow", "next week", "yesterday", "in two days"],
                    2, "Yesterday is past.", "yesterday گذشته است."),
            ],
            [
                write("Write five sentences about yesterday. Use was once and "
                      "a past verb in every other sentence. Include one time "
                      "phrase and one person.",
                      "پنج جمله دربارهٔ دیروز بنویس. یک بار was و در بقیه فعل "
                      "گذشته به کار ببر. یک عبارت زمانی و یک نفر را بیاور.",
                      45, ["and"],
                      "Five past sentences, one was, one time phrase, one "
                      "person, no present tense.",
                      "پنج جملهٔ گذشته، یک was، یک عبارت زمانی، یک نفر و بدون "
                      "حال."),
                gap("I ___ (watch) a movie in the evening.", ["watched"],
                    "Regular past adds -ed.", "گذشتهٔ باقاعده -ed می‌گیرد.",
                    "one word"),
                mcq("Which is a past sentence with a state?", "کدام جملهٔ "
                    "گذشته حالت دارد؟",
                    ["I played football.", "It was very hot.",
                     "I visited my aunt.", "We ate at eight."], 1,
                    "Was + adjective is a state.", "was + صفت حالت است."),
            ],
        ),
    ],
)
