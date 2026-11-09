#!/usr/bin/env python3
"""Eight lessons that deepen A2: one per unit, across the four skills the
course was thin in. Each one takes the grammar the unit teaches and asks the
learner to use it in a message, a conversation, a label or a plan."""

from course_kit import gap, lesson, listen, mcq, passage, say, write

EXTRA = {
    "a2-u1": [
        lesson(
            "a2-u1-l4", "writing",
            ("A message about what happened",
             "پیامی دربارهٔ آنچه رخ داد"),
            ("Write a short narrative message in the past simple, in order.",
             "پیام روایی کوتاهی با گذشتهٔ ساده و به ترتیب بنویس."),
            [
                ("A message about something that happened needs three things: "
                 "when it happened, what happened first, and how it ended. The "
                 "past simple carries the events; time words (then, after "
                 "that, in the end) carry the order.",
                 "پیام دربارهٔ رویدادی سه چیز لازم دارد: کِی رخ داد، اول چه شد و "
                 "چطور تمام شد. گذشتهٔ ساده رویدادها را حمل می‌کند و واژه‌های "
                 "زمان (then، after that، in the end) ترتیب را."),
                ("Keep one event per sentence. A sentence with three verbs "
                 "joined by and is hard to follow in a message; three short "
                 "sentences are easy, and the reader can see the order.",
                 "در هر جمله یک رویداد بگذار. جمله‌ای با سه فعلِ وصل‌شده با and در "
                 "پیام سخت دنبال می‌شود؛ سه جملهٔ کوتاه آسان است و خواننده "
                 "ترتیب را می‌بیند."),
            ],
            [
                ("I missed the bus, so I walked to work.",
                 "اتوبوس را از دست دادم، پس پیاده به کار رفتم."),
                ("First we waited, then we called a taxi.",
                 "اول منتظر ماندیم، بعد تاکسی گرفتیم."),
                ("In the end it was fine.", "در پایان همه‌چیز خوب بود."),
            ],
            [
                mcq("Which word shows the order of events?", "کدام واژه ترتیب "
                    "رویدادها را نشان می‌دهد؟",
                    ["because", "then", "very", "always"], 1,
                    "Then moves the story forward.", "then داستان را جلو "
                    "می‌برد."),
                mcq("A message about the past uses ___.", "پیام دربارهٔ گذشته "
                    "از ___ استفاده می‌کند.",
                    ["present simple", "past simple", "will", "can"], 1,
                    "Events that finished take the past simple.",
                    "رویدادهای تمام‌شده گذشتهٔ ساده می‌گیرند."),
            ],
            [
                write("Write a message of about 45 words to a friend. Tell "
                      "them what happened yesterday: what you planned, what "
                      "went wrong, and how it ended. Use three time words.",
                      "پیامی حدود ۴۵ واژه به دوستی بنویس. بگو دیروز چه شد: چه "
                      "برنامه‌ای داشتی، چه خراب شد و چطور تمام شد. سه واژهٔ زمان "
                      "به کار ببر.",
                      45, ["then", "because"],
                      "Past simple throughout, one event per sentence, three "
                      "time words, and an ending.",
                      "گذشتهٔ ساده در همه‌جا، در هر جمله یک رویداد، سه واژهٔ زمان و "
                      "یک پایان."),
                gap("I ___ (not / catch) the train.", ["didn't catch"],
                    "Negative past: didn't + base verb.",
                    "منفی گذشته: didn't + صورت پایه.", "two words"),
                mcq("Which sentence is in the past simple?", "کدام جمله در "
                    "گذشتهٔ ساده است؟",
                    ["I am late.", "I was late.", "I will be late.",
                     "I am being late."], 1,
                    "Was is the past of am.", "was گذشتهٔ am است."),
            ],
        ),
    ],
    "a2-u2": [
        lesson(
            "a2-u2-l4", "reading",
            ("The train that did not come",
             "قطاری که نیامد"),
            ("Read a narrative and separate the background action from the "
             "event that interrupted it.",
             "روایتی را بخوان و کنش پس‌زمینه را از رویدادی که قطعش کرد جدا "
             "کن."),
            [
                ("In a past narrative the past continuous sets the scene and "
                 "the past simple brings the event: I was waiting on the "
                 "platform when the announcement came. The thing that was "
                 "happening is background; the thing that happened is news.",
                 "در روایت گذشته، گذشتهٔ استمراری صحنه را می‌سازد و گذشتهٔ ساده "
                 "رویداد را می‌آورد: I was waiting on the platform when the "
                 "announcement came. آنچه در جریان بود پس‌زمینه است و آنچه رخ "
                 "داد خبر."),
                ("Questions about this text usually ask what was happening "
                 "at a particular moment, not what happened in the end. Read "
                 "the moment, not the summary.",
                 "پرسش‌های چنین متنی معمولاً می‌پرسند در لحظهٔ خاصی چه در جریان "
                 "بود، نه پایان ماجرا. لحظه را بخوان، نه خلاصه را."),
            ],
            [
                ("I was reading when the phone rang.",
                 "داشتم می‌خواندم که تلفن زنگ زد."),
                ("While we were waiting, it started to rain.",
                 "وقتی منتظر بودیم، باران شروع شد."),
            ],
            [
                mcq("What was the writer doing at nine?", "ساعت نُه نویسنده چه "
                    "می‌کرد؟",
                    ["sleeping", "waiting on the platform", "reading",
                     "walking home"], 1,
                    "The text says he was waiting at nine.",
                    "متن می‌گوید ساعت نُه منتظر بود."),
                mcq("What interrupted the waiting?", "چه چیزی انتظار را قطع "
                    "کرد؟",
                    ["the rain", "an announcement", "a phone call", "a train"],
                    1, "The announcement came at half past nine.",
                    "اعلام ساعت نُه و نیم آمد."),
            ],
            [
                mcq("Which sentence is background, not news?", "کدام جمله "
                    "پس‌زمینه است و نه خبر؟",
                    ["The train stopped.", "I got on.", "I was standing near "
                     "the door.", "She waved."], 2,
                    "Continuous describes what was going on.",
                    "استمراری می‌گوید چه در جریان بود."),
                mcq("How long did the writer wait?", "نویسنده چقدر منتظر "
                    "ماند؟",
                    ["ten minutes", "about an hour", "three hours",
                     "all day"], 1,
                    "He arrived at nine and left after ten.",
                    "ساعت نُه رسید و بعد از ده رفت."),
            ],
            passage=passage(
                ("The train that did not come", "قطاری که نیامد"),
                ("I arrived at the station at nine and the board said the "
                 "train was on time. At half past nine I was standing near the "
                 "door with my bag when an announcement said the train had "
                 "been canceled. While everyone was asking the guard what had "
                 "happened, I looked at the line for the buses outside and "
                 "decided to walk. I was still walking at eleven, and the rain "
                 "had started, and I was laughing at myself for believing a "
                 "board.",
                 "ساعت نُه به ایستگاه رسیدم و تابلوی اعلانات می‌گفت قطار "
                 "به‌موقع است. ساعت نُه و نیم با کیفم نزدیک در ایستاده بودم که "
                 "اعلامی گفت قطار لغو شده است. وقتی همه از نگهبان می‌پرسیدند چه "
                 "شده، من به صف اتوبوس‌های بیرون نگاه کردم و تصمیم گرفتم پیاده "
                 "بروم. ساعت یازده هنوز پیاده می‌رفتم و باران شروع شده بود و به "
                 "خودم می‌خندیدم که تابلویی را باور کرده بودم."),
            ),
        ),
    ],
    "a2-u3": [
        lesson(
            "a2-u3-l4", "listening",
            ("Have you ever?", "تا حالا؟"),
            ("Follow a conversation about experiences and hear who has done "
             "what.",
             "گفت‌وگویی دربارهٔ تجربه‌ها را دنبال کن و بشنو هر کس چه کرده است."),
            [
                ("Have you ever asks about any time up to now, so the answer "
                 "never has a date. If the answer has a date, English switches "
                 "to the past simple: I went there in 2019.",
                 "Have you ever دربارهٔ هر زمانی تا حالا می‌پرسد، پس پاسخ هرگز "
                 "تاریخ ندارد. اگر پاسخ تاریخ داشته باشد، انگلیسی به گذشتهٔ ساده "
                 "می‌رود: I went there in 2019."),
                ("Listen for never and not yet: they answer the question "
                 "without a story, and they are common in this kind of "
                 "conversation.",
                 "به never و not yet گوش کن: پرسش را بی‌داستان پاسخ می‌دهند و در "
                 "این نوع گفت‌وگو رایج‌اند."),
            ],
            [
                ("Have you ever been to Istanbul? — No, never.",
                 "تا حالا استانبول بوده‌ای؟ — نه، هرگز."),
                ("I have just finished the book.", "تازه کتاب را تمام کرده‌ام."),
            ],
            [
                mcq("Has the woman been to Istanbul?", "آیا زن استانبول بوده "
                    "است؟",
                    ["yes, last year", "no, never", "yes, twice",
                     "she does not say"], 1,
                    "She answers never.", "پاسخ می‌دهد never."),
                mcq("What has the man just done?", "مرد تازه چه کرده است؟",
                    ["started a course", "finished a book", "bought a "
                     "ticket", "moved house"], 1,
                    "He has just finished the book.",
                    "تازه کتاب را تمام کرده است."),
            ],
            [
                listen("Have you ever eaten there? — Yes, I have. I went "
                       "there in May.",
                       "When did she go?", "کِی رفته است؟",
                       ["last year", "in May", "never", "yesterday"], 1,
                       "A date switches to the past simple.",
                       "تاریخ جمله را به گذشتهٔ ساده می‌برد."),
                listen("I have never seen the sea. I would like to.",
                       "What has he never done?", "چه کاری هرگز نکرده است؟",
                       ["eaten fish", "seen the sea", "flown",
                        "left his town"], 1,
                       "He has never seen the sea.", "هرگز دریا را ندیده است."),
                listen("Have you finished the report? — Not yet. I need one "
                       "more day.",
                       "Has he finished?", "آیا تمام کرده است؟",
                       ["yes", "no, not yet", "he does not know",
                        "he finished yesterday"], 1,
                       "Not yet means not finished.", "not yet یعنی هنوز نه."),
            ],
        ),
    ],
    "a2-u4": [
        lesson(
            "a2-u4-l4", "speaking",
            ("Fixing an arrangement out loud",
             "هماهنگ‌کردن قرار با صدای بلند"),
            ("Make, move and confirm an arrangement in a short spoken exchange.",
             "قرار گذاشتن، جابه‌جا کردن و تأیید آن را در گفت‌وگویی کوتاه انجام "
             "بده."),
            [
                ("An arrangement has four moves: suggest, check, confirm and "
                 "repeat. Should we meet at six? Does that work for you? "
                 "Perfect. So, six at the cafe.",
                 "قرار چهار حرکت دارد: پیشنهاد، بررسی، تأیید و تکرار. Should we "
                 "meet at six? Does that work for you? Perfect. So, six at the "
                 "cafe."),
                ("When you move a plan, say the new time and the reason in one "
                 "sentence: Can we make it seven instead? I am finishing late. "
                 "That is softer than canceling and starting again.",
                 "وقتی قراری را جابه‌جا می‌کنی، زمان تازه و دلیل را در یک جمله "
                 "بگو: Can we make it seven instead? I am finishing late. این "
                 "از لغو کردن و از نو شروع کردن نرم‌تر است."),
            ],
            [
                ("Should we meet at six?", "ساعت شش همدیگر را ببینیم؟"),
                ("Can we make it seven instead?", "می‌شود به‌جایش هفت بگذاریم؟"),
                ("So, seven at the cafe. See you then.",
                 "پس هفت در کافه. آن‌وقت می‌بینمت."),
            ],
            [
                mcq("Which word makes a suggestion?", "کدام واژه پیشنهاد "
                    "می‌سازد؟",
                    ["Should", "Must", "Do", "Are"], 0,
                    "Should we is the standard suggestion.", "Should we پیشنهاد "
                    "استاندارد است."),
                mcq("The last move in an arrangement is ___.", "آخرین حرکت در "
                    "قرار ___ است.",
                    ["suggesting", "repeating the details", "canceling",
                     "apologizing"], 1,
                    "Repeating confirms both sides heard the same thing.",
                    "تکرار تأیید می‌کند که هر دو یک چیز شنیده‌اند."),
            ],
            [
                say("Should we meet at six at the cafe?",
                    "ساعت شش در کافه همدیگر را ببینیم؟"),
                say("Can we make it seven instead? I am finishing work late.",
                    "می‌شود به‌جایش هفت بگذاریم؟ کارم دیر تمام می‌شود."),
                say("So, seven at the cafe, on Friday. See you then.",
                    "پس جمعه ساعت هفت در کافه. آن‌وقت می‌بینمت."),
            ],
        ),
    ],
    "a2-u5": [
        lesson(
            "a2-u5-l4", "writing",
            ("The complaint that gets the refund",
             "شکایتی که پول را برمی‌گرداند"),
            ("Write a short complaint that states the facts, the ask and the "
             "deadline.",
             "شکایت کوتاهی بنویس که واقعیت‌ها، خواسته و مهلت را بگوید."),
            [
                ("A complaint works when it is boring. Say what you bought, "
                 "when, what is wrong, what you want, and by when. No "
                 "adjectives about the company: the facts are the argument.",
                 "شکایت وقتی کار می‌کند که خسته‌کننده باشد. بگو چه خریدی، کِی، "
                 "چه ایرادی دارد، چه می‌خواهی و تا کِی. هیچ صفتی دربارهٔ شرکت "
                 "نیاور: واقعیت‌ها خودشان استدلال‌اند."),
                ("The polite frame is not weakness. I am writing about... and "
                 "I would like... keep the letter formal while the request "
                 "stays exact.",
                 "چارچوب مؤدب ضعف نیست. I am writing about… و I would like… "
                 "نامه را رسمی نگه می‌دارند در حالی که درخواست دقیق می‌ماند."),
            ],
            [
                ("I am writing about a kettle I bought on May 3.",
                 "دربارهٔ کتری‌ای می‌نویسم که سوم مه خریدم."),
                ("I would like a refund, not a replacement.",
                 "پول را می‌خواهم، نه تعویض."),
            ],
            [
                mcq("A complaint should start with ___.", "شکایت باید با ___ "
                    "آغاز شود.",
                    ["an opinion of the company", "the facts of the purchase",
                     "a threat", "an apology"], 1,
                    "Facts first; they are the argument.",
                    "اول واقعیت‌ها که خودشان استدلال‌اند."),
                mcq("'I would like a refund' is ___.", "«I would like a "
                    "refund» ___ است.",
                    ["rude", "polite and exact", "unclear", "informal"], 1,
                    "It names the request without softening the substance.",
                    "درخواست را بی‌نرم کردن جانِ مطلب نام می‌برد."),
            ],
            [
                write("Write a complaint of about 50 words about a kettle you "
                      "bought three weeks ago that stopped working. Give the "
                      "date, the fault, what you want and a deadline.",
                      "شکایتی حدود ۵۰ واژه بنویس دربارهٔ کتری‌ای که سه هفته پیش "
                      "خریدی و از کار افتاد. تاریخ، ایراد، خواسته و مهلت را "
                      "بیاور.",
                      50, ["because"], "Facts, fault, request, deadline; "
                      "formal frame; no insults and no adjectives about the "
                      "company.", "واقعیت، ایراد، درخواست، مهلت؛ چارچوب رسمی؛ "
                      "بدون توهین و صفت دربارهٔ شرکت."),
                gap("I am writing ___ a kettle I bought in May.",
                    ["about"], "Write about + topic.", "write about + موضوع.",
                    "one word"),
                mcq("Which sentence gives a deadline?", "کدام جمله مهلت "
                    "می‌دهد؟",
                    ["The kettle is bad.", "Please reply by June 20.",
                     "I bought it in May.", "It does not work."], 1,
                    "By + date is a deadline.", "by + تاریخ یعنی مهلت."),
            ],
        ),
    ],
    "a2-u6": [
        lesson(
            "a2-u6-l4", "reading",
            ("The label on the medicine", "برچسب دارو"),
            ("Read a medicine label and find the dose, the limit and the "
             "warning.",
             "برچسب دارو را بخوان و مقدار، محدودیت و هشدار را پیدا کن."),
            [
                ("A medicine label is written in short lines and the "
                 "important information is in three places: how much to take, "
                 "how often, and what not to do. Read those three before "
                 "anything else.",
                 "برچسب دارو در خط‌های کوتاه نوشته می‌شود و اطلاعات مهم در سه "
                 "جاست: چه مقدار، هر چند وقت و چه کاری نکن. پیش از هر چیز این "
                 "سه را بخوان."),
                ("Quantities use both countable and uncountable forms: two "
                 "tablets, some water, not more than four times a day. The "
                 "limit is the number you must not pass.",
                 "مقدارها هم شمردنی و هم غیرقابل‌شمارش‌اند: two tablets، some "
                 "water، not more than four times a day. محدودیت عددی است که "
                 "نباید از آن بگذری."),
            ],
            [
                ("Take two tablets with water.", "دو قرص با آب بخور."),
                ("Do not take more than four times a day.",
                 "بیش از چهار بار در روز مصرف نکن."),
            ],
            [
                mcq("How many tablets is one dose?", "یک نوبت چند قرص است؟",
                    ["one", "two", "three", "four"], 1,
                    "Take two tablets.", "دو قرص بخور."),
                mcq("What is the daily limit?", "محدودیت روزانه چیست؟",
                    ["two times", "three times", "four times", "six times"],
                    2, "Not more than four times a day.",
                    "بیش از چهار بار در روز نه."),
            ],
            [
                mcq("What should you take the tablets with?",
                    "قرص‌ها را با چه بخوری؟",
                    ["milk", "water", "tea", "juice"], 1,
                    "With water.", "با آب."),
                mcq("Who should ask a doctor first?", "چه کسی باید اول از "
                    "پزشک بپرسد؟",
                    ["everyone", "people taking other medicine",
                     "children over twelve", "nobody"], 1,
                    "The warning names other medicine.",
                    "هشدار داروهای دیگر را نام می‌برد."),
            ],
            passage=passage(
                ("Pain relief tablets", "قرص مسکن"),
                ("Adults: take two tablets with water, every six hours.\n"
                 "Do not take more than four times in 24 hours.\n"
                 "Do not take with other pain medicine.\n"
                 "If you are pregnant, ask a doctor before taking.\n"
                 "Keep out of reach of children.",
                 "بزرگسالان: هر شش ساعت دو قرص با آب مصرف کنند.\n"
                 "در ۲۴ ساعت بیش از چهار نوبت مصرف نشود.\n"
                 "با مسکن دیگر مصرف نشود.\n"
                 "در بارداری پیش از مصرف با پزشک مشورت شود.\n"
                 "دور از دسترس کودکان نگهداری شود."),
            ),
        ),
    ],
    "a2-u7": [
        lesson(
            "a2-u7-l4", "speaking",
            ("Can you help me with this?",
             "می‌توانی با این کمکم کنی؟"),
            ("Ask for help with a device, describe the problem, and understand "
             "the instruction.",
             "برای وسیله‌ای کمک بخواه، مشکل را توصیف کن و دستور را بفهم."),
            [
                ("Three sentences get you help: what you want, what is wrong, "
                 "and what you have already tried. Could you help me with this "
                 "phone? It will not charge. I have tried two cables.",
                 "سه جمله کمکت را می‌گیرد: چه می‌خواهی، چه ایرادی هست و چه چیزی "
                 "را امتحان کرده‌ای. Could you help me with this phone? It will "
                 "not charge. I have tried two cables."),
                ("When you receive an instruction, repeat the key verb: So I "
                 "press this and hold it? That is how you check without "
                 "pretending to understand.",
                 "وقتی دستوری می‌گیری، فعل کلیدی را تکرار کن: So I press this "
                 "and hold it? این‌گونه بررسی می‌کنی بی‌آنکه ادای فهمیدن درآوری."),
            ],
            [
                ("Could you help me with this laptop?",
                 "می‌توانی با این لپ‌تاپ کمکم کنی؟"),
                ("It will not turn on. I have charged it.",
                 "روشن نمی‌شود. شارژش کرده‌ام."),
                ("So I press this button and wait?",
                 "پس این دکمه را می‌زنم و صبر می‌کنم؟"),
            ],
            [
                mcq("Which sentence describes the problem?", "کدام جمله مشکل "
                    "را توصیف می‌کند؟",
                    ["Could you help me?", "It will not turn on.",
                     "Thank you.", "So I press this?"], 1,
                    "It names what fails.", "نام می‌برد چه چیزی کار نمی‌کند."),
                mcq("Repeating the instruction shows ___.", "تکرار دستور نشان "
                    "می‌دهد ___.",
                    ["you are bored", "you are checking you understood",
                     "you disagree", "you are in a hurry"], 1,
                    "It checks understanding honestly.", "فهمیدن را صادقانه "
                    "بررسی می‌کند."),
            ],
            [
                say("Could you help me with this phone? It will not charge.",
                    "می‌توانی با این تلفن کمکم کنی؟ شارژ نمی‌شود."),
                say("I have tried two cables and a different socket.",
                    "دو کابل و یک پریز دیگر را امتحان کرده‌ام."),
                say("So I press this button and hold it for ten seconds?",
                    "پس این دکمه را می‌زنم و ده ثانیه نگه می‌دارم؟"),
            ],
        ),
    ],
    "a2-u8": [
        lesson(
            "a2-u8-l4", "speaking",
            ("If it rains, we will stay in",
             "اگر باران بیاید، می‌مانیم"),
            ("Talk through a plan with two branches, using if and unless.",
             "طرحی با دو شاخه را با if و unless بگو."),
            [
                ("A first conditional plan has two halves: the condition in "
                 "the if-clause (present simple) and the result in the main "
                 "clause (will or can). If the weather is good, we will walk.",
                 "طرح شرطی نوع اول دو نیمه دارد: شرط در بند if (حال ساده) و "
                 "نتیجه در بند اصلی (will یا can). If the weather is good, we "
                 "will walk."),
                ("Unless means if not, so never use both: unless it rains, we "
                 "will walk — not unless it does not rain.",
                 "unless یعنی if not، پس هر دو را با هم به کار نبر: unless it "
                 "rains, we will walk — نه unless it does not rain."),
            ],
            [
                ("If it rains, we will stay in.", "اگر باران بیاید، می‌مانیم."),
                ("Unless the bus is late, we will be there by six.",
                 "اگر اتوبوس دیر نکند، تا شش آنجا هستیم."),
                ("If you come early, we can have lunch first.",
                 "اگر زود بیایی، می‌توانیم اول ناهار بخوریم."),
            ],
            [
                mcq("If it ___ tomorrow, we will stay in.", "اگر فردا ___، "
                    "می‌مانیم.",
                    ["will rain", "rains", "rained", "is raining"], 1,
                    "The if-clause stays in the present simple.",
                    "بند if در حال ساده می‌ماند."),
                mcq("Unless means ___.", "unless یعنی ___.",
                    ["if", "if not", "because", "when"], 1,
                    "Unless = if not.", "unless به معنای if not است."),
            ],
            [
                say("If the weather is good, we will walk to the park.",
                    "اگر هوا خوب باشد، پیاده به پارک می‌رویم."),
                say("Unless the bus is late, we will be there by six.",
                    "اگر اتوبوس دیر نکند، تا شش آنجا هستیم."),
                say("If you finish early, call me and we can start without "
                    "you.", "اگر زود تمام کردی زنگ بزن و می‌توانیم بی‌تو شروع "
                    "کنیم."),
            ],
        ),
    ],
}
