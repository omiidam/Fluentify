#!/usr/bin/env python3
"""Pre-A1, units 3 and 4: people, and the things you eat."""

from course_kit import dialogue, gap, lesson, listen, mcq, passage, say, unit, write

U3 = unit(
    "pre-u3",
    ("People and things", "آدم‌ها و چیزها"),
    ("Point at people and things, and say whose they are.",
     "به آدم‌ها و چیزها اشاره کن و بگو از آنِ کیست."),
    [
        lesson(
            "pre-u3-l1", "grammar",
            ("My, your, his, her", "My، your، his، her"),
            ("Use this and that to point, and my and her to say whose.",
             "با this و that اشاره کن و با my و her بگو از آنِ کیست."),
            [
                ("This is for something near you; that is for something far. "
                 "This is my pen. That is your book.",
                 "this برای چیز نزدیک است و that برای دور: This is my pen، "
                 "That is your book."),
                ("The possessive word comes before the noun: my bag, your "
                 "phone, his car, her coat. There is no word for 'the'. Say my "
                 "book, not the my book.",
                 "واژهٔ مالکیت پیش از اسم می‌آید: my bag، your phone، his car، "
                 "her coat. «the» با آن نمی‌آید: بگو my book نه the my book."),
            ],
            [
                ("This is my bag.", "این کیف من است."),
                ("That is her coat.", "آن مانتوی اوست."),
                ("Is this your phone?", "این تلفن توست؟"),
            ],
            [
                mcq("This is ___ book. (I own it.)", "این کتاب ___ است.",
                    ["my", "me", "I", "mine book"], 0,
                    "My comes before a noun.", "my پیش از اسم می‌آید."),
                mcq("___ is her coat. (far from you)", "___ مانتوی اوست.",
                    ["This", "That", "These", "They"], 1,
                    "That points to something far.", "that به چیز دور اشاره "
                    "می‌کند."),
            ],
            [
                mcq("He has a car. It is ___ car.", "او ماشین دارد. ___ ماشین "
                    "اوست.",
                    ["her", "his", "my", "your"], 1,
                    "He takes his.", "he با his می‌آید."),
                gap("This is ___ pen. (you own it)", ["your"],
                    "Your is the possessive of you.", "your مالکیت you است.",
                    "one word"),
                gap("___ is my sister. (near me)", ["This", "She"],
                    "This points; she names.", "this اشاره می‌کند و she نام "
                    "می‌برد.", "one word"),
            ],
        ),
        lesson(
            "pre-u3-l2", "vocabulary",
            ("Family and everyday things", "خانواده و چیزهای روزمره"),
            ("Name the people in a family and ten objects you use daily.",
             "افراد خانواده و ده شیء روزمره را نام ببر."),
            [
                ("Family words: mother, father, sister, brother, son, daughter. "
                 "Mother and father are also mum and dad in speech.",
                 "واژه‌های خانواده: mother، father، sister، brother، son، "
                 "daughter. در گفتار mother و father را mum و dad هم می‌گویند."),
                ("Objects you will use in every lesson: book, pen, phone, bag, "
                 "table, chair, door, window, key, cup. Notice that phone is "
                 "said with a long o and the ph is an f sound.",
                 "چیزهایی که در هر درس به کار می‌آیند: book، pen، phone، bag، "
                 "table، chair، door، window، key، cup. phone با o کشیده و "
                 "صدای ph برابر f است."),
            ],
            [
                ("My sister is a teacher.", "خواهرم معلم است."),
                ("The keys are on the table.", "کلیدها روی میز هستند."),
                ("Please close the window.", "لطفاً پنجره را ببند."),
            ],
            [
                mcq("My father's daughter is my ___.", "دختر پدرم ___ من است.",
                    ["mother", "sister", "son", "brother"], 1,
                    "Your father's daughter is your sister (or you).",
                    "دختر پدرت خواهرت است (یا خودت)."),
                mcq("Which is a thing, not a person?", "کدام شیء است نه شخص؟",
                    ["brother", "daughter", "window", "mother"], 2,
                    "A window is an object.", "window یک شیء است."),
            ],
            [
                mcq("You write with a ___.", "با ___ می‌نویسی.",
                    ["cup", "pen", "door", "key"], 1,
                    "A pen writes.", "با pen می‌نویسند."),
                gap("Please open the ___.", ["door", "window"],
                    "Doors and windows open.", "در و پنجره باز می‌شوند.",
                    "one word"),
                mcq("My mother's son is my ___.", "پسر مادرم ___ من است.",
                    ["brother", "sister", "father", "uncle"], 0,
                    "Your mother's son is your brother.", "پسر مادرت برادرت "
                    "است."),
            ],
        ),
        lesson(
            "pre-u3-l3", "listening",
            ("A photo of a family", "عکسی از یک خانواده"),
            ("Listen to someone describe a photo and find who is who.",
             "به توصیف کسی از یک عکس گوش کن و بفهم هر کس کیست."),
            [
                ("When someone describes a photo, the useful words are this "
                 "is and that is, plus the family word right after them. "
                 "Listen for the family word, not for the name.",
                 "وقتی کسی عکسی را توصیف می‌کند، واژه‌های سودمند this is و that "
                 "is هستند و پس از آن‌ها واژهٔ خانواده می‌آید. به واژهٔ خانواده "
                 "گوش کن، نه به نام."),
                ("Numbers help: three people, two children. If you hear a "
                 "number, count the people in the next sentence.",
                 "عددها کمک می‌کنند: three people، two children. اگر عددی "
                 "شنیدی، افراد جملهٔ بعد را بشمار."),
            ],
            [
                ("This is my mother. That is my brother. He is twelve.",
                 "این مادرم است. آن برادرم است. او دوازده ساله است."),
                ("These are my two sisters.", "این‌ها دو خواهر من هستند."),
            ],
            [
                mcq("How old is the brother?", "برادر چند ساله است؟",
                    ["two", "ten", "twelve", "twenty"], 2,
                    "He is twelve.", "او دوازده ساله است."),
                mcq("How many sisters are there?", "چند خواهر هست؟",
                    ["one", "two", "three", "four"], 1,
                    "Two sisters.", "دو خواهر."),
            ],
            [
                listen("This is my father. He is a driver. This is my sister. "
                       "She is a student.",
                       "What is the father's job?", "شغل پدر چیست؟",
                       ["a teacher", "a driver", "a doctor", "a student"], 1,
                       "He is a driver.", "او راننده است."),
                listen("That is my brother. He is ten. This is my mother.",
                       "How old is the brother?", "برادر چند ساله است؟",
                       ["ten", "twelve", "two", "twenty"], 0,
                       "He is ten.", "او ده ساله است."),
                listen("My sister has a phone. It is in her bag.",
                       "Where is the phone?", "تلفن کجاست؟",
                       ["on the table", "in her bag", "in the car",
                        "on the chair"], 1,
                       "It is in her bag.", "در کیف اوست."),
            ],
        ),
        lesson(
            "pre-u3-l4", "speaking",
            ("Tell me about your family", "از خانواده‌ات بگو"),
            ("Describe three people in your family in one sentence each.",
             "سه نفر از خانواده‌ات را هر یک در یک جمله توصیف کن."),
            [
                ("One person, one sentence: This is my mother. She is a "
                 "teacher. Two sentences per person is also fine, but keep "
                 "them short.",
                 "یک نفر، یک جمله: This is my mother. She is a teacher. دو جمله "
                 "برای هر نفر هم خوب است، ولی کوتاه نگه دار."),
                ("Say he or she, not 'it', for people. It is for things only, "
                 "and using it for a person is a real mistake in English.",
                 "برای آدم‌ها he یا she بگو، نه it. it فقط برای چیزهاست و به کار "
                 "بردنش برای آدم در انگلیسی خطای واقعی است."),
            ],
            [
                ("This is my brother. He is a student.",
                 "این برادرم است. او دانش‌آموز است."),
                ("This is my sister. She is ten.",
                 "این خواهرم است. او ده ساله است."),
            ],
            [
                mcq("For your mother you say ___.", "برای مادرت می‌گویی ___.",
                    ["it is", "she is", "he is", "they is"], 1,
                    "A person takes he or she.", "آدم he یا she می‌گیرد."),
                mcq("How many sentences per person?", "برای هر نفر چند جمله؟",
                    ["one or two", "five", "ten", "at least seven"],
                    0, "Short is better here.", "کوتاه بهتر است."),
            ],
            [
                say("This is my mother. She is a teacher.",
                    "این مادرم است. او معلم است."),
                say("This is my brother. He is twelve. He is a student.",
                    "این برادرم است. او دوازده ساله است. دانش‌آموز است."),
                say("These are my two sisters. They are students.",
                    "این‌ها دو خواهر من هستند. آن‌ها دانش‌آموزند."),
            ],
            dialogue=dialogue([
                ("Sara", "Who is this?", "این کیست؟"),
                ("Ali", "This is my brother. He is ten.",
                 "این برادرم است. او ده ساله است."),
                ("Sara", "And that?", "و آن؟"),
                ("Ali", "That is my mother. She is a doctor.",
                 "آن مادرم است. او پزشک است."),
            ]),
        ),
    ],
)

U4 = unit(
    "pre-u4",
    ("Food and drink", "خوراک و نوشیدنی"),
    ("Say what you like and do not like, and order something simple.",
     "بگو چه دوست داری و چه نه، و چیزی ساده سفارش بده."),
    [
        lesson(
            "pre-u4-l1", "grammar",
            ("I like, I don't like", "I like، I don't like"),
            ("Say what you like, what you do not like, and ask someone else.",
             "بگو چه دوست داری و چه نه و از دیگری بپرس."),
            [
                ("Like is a verb, so it needs a subject: I like tea. Do not "
                 "say 'I am like tea' — that means you resemble tea.",
                 "like فعل است و نهاد می‌خواهد: I like tea. نگو «I am like "
                 "tea» که یعنی شبیه چای هستی."),
                ("The negative is do not like, shortened to don't like. The "
                 "question is Do you like ...? with the answer Yes, I do or No, "
                 "I don't.",
                 "منفی do not like است و کوتاهش don't like. پرسش Do you "
                 "like ...? و پاسخ Yes, I do یا No, I don't."),
            ],
            [
                ("I like tea.", "چای دوست دارم."),
                ("I don't like coffee.", "قهوه دوست ندارم."),
                ("Do you like bread? — Yes, I do.",
                 "نان دوست داری؟ — بله، دوست دارم."),
            ],
            [
                mcq("I ___ rice.", "برنج دوست دارم.",
                    ["like", "am like", "likes", "do like"], 0,
                    "Like takes I directly.", "like با I مستقیم می‌آید."),
                mcq("___ you like fish?", "ماهی دوست داری؟",
                    ["Do", "Are", "Is", "Does"], 0,
                    "Questions with I/you/we/they take do.",
                    "پرسش با I/you/we/they با do ساخته می‌شود."),
            ],
            [
                mcq("I ___ like milk.", "شیر دوست ندارم.",
                    ["don't", "not", "no", "am not"], 0,
                    "The negative is don't + verb.", "منفی don't + فعل است."),
                gap("I like tea, but I ___ like coffee.",
                    ["don't", "do not"], "Negative of like.",
                    "منفی like.", "one or two words"),
                mcq("Do you like apples? — No, I ___.", "سیب دوست داری؟ — نه.",
                    ["don't", "not", "am not", "do no"], 0,
                    "Short answer: No, I don't.", "پاسخ کوتاه: No, I don't."),
            ],
        ),
        lesson(
            "pre-u4-l2", "vocabulary",
            ("Bread, rice, water, tea", "نان، برنج، آب، چای"),
            ("Name ten foods and drinks, and use a cup of and a glass of.",
             "ده خوراکی و نوشیدنی را نام ببر و a cup of و a glass of را به کار "
             "ببر."),
            [
                ("Food: bread, rice, egg, fish, meat, cheese, apple, orange. "
                 "Drink: water, tea, milk, coffee. Say a glass of water and a "
                 "cup of tea: the container word comes before of.",
                 "خوراکی: bread، rice، egg، fish، meat، cheese، apple، orange. "
                 "نوشیدنی: water، tea، milk، coffee. بگو a glass of water و a "
                 "cup of tea: واژهٔ ظرف پیش از of می‌آید."),
                ("Some words are uncountable and take no plural in this "
                 "sense: water, rice, bread, tea. You say some water, not two "
                 "waters.",
                 "بعضی واژه‌ها در این معنا جمع نمی‌گیرند: water، rice، bread، "
                 "tea. می‌گویی some water نه two waters."),
            ],
            [
                ("I would like a cup of tea.", "یک فنجان چای می‌خواهم."),
                ("We have bread and cheese.", "نان و پنیر داریم."),
                ("Can I have a glass of water?", "می‌توانم یک لیوان آب "
                 "بگیرم؟"),
            ],
            [
                mcq("You drink ___.", "___ را می‌نوشی.",
                    ["bread", "water", "rice", "cheese"], 1,
                    "Water is a drink.", "water نوشیدنی است."),
                mcq("A ___ of tea.", "یک ___ چای.",
                    ["glass", "cup", "plate", "bowl"], 1,
                    "Tea comes in a cup.", "چای در فنجان می‌آید."),
            ],
            [
                mcq("Which is uncountable in this sense?", "کدام در این معنا "
                    "شمردنی نیست؟",
                    ["apple", "egg", "rice", "orange"], 2,
                    "We say some rice, not two rices.",
                    "می‌گوییم some rice نه two rices."),
                gap("Can I have a ___ of water?", ["glass", "cup"],
                    "Water comes in a glass.", "آب در لیوان می‌آید.",
                    "one word"),
                mcq("Which is a food, not a drink?", "کدام خوراکی است نه "
                    "نوشیدنی؟",
                    ["milk", "coffee", "cheese", "tea"], 2,
                    "Cheese is eaten.", "پنیر خورده می‌شود."),
            ],
        ),
        lesson(
            "pre-u4-l3", "reading",
            ("At the cafe", "در کافه"),
            ("Read a short order and find what each person wants.",
             "سفارش کوتاهی را بخوان و بفهم هر کس چه می‌خواهد."),
            [
                ("A menu at this level is a list, and a reading text is a "
                 "small set of orders. Read for who and what: Sara wants tea, "
                 "Ali wants water.",
                 "منو در این سطح فهرستی است و متن خواندن مجموعهٔ کوچکی از "
                 "سفارش‌ها. برای «کی» و «چه» بخوان: سارا چای می‌خواهد و علی "
                 "آب."),
                ("The phrase I would like is the polite form of I want. In a "
                 "cafe, always use I would like.",
                 "عبارت I would like شکل مؤدب I want است. در کافه همیشه I would "
                 "like بگو."),
            ],
            [
                ("Sara: I would like a cup of tea, please.",
                 "سارا: یک فنجان چای می‌خواهم، لطفاً."),
                ("Ali: Can I have a glass of water? I don't like coffee.",
                 "علی: می‌توانم یک لیوان آب بگیرم؟ قهوه دوست ندارم."),
            ],
            [
                mcq("What does Sara want?", "سارا چه می‌خواهد؟",
                    ["coffee", "tea", "water", "bread"], 1,
                    "A cup of tea.", "یک فنجان چای."),
                mcq("What does Ali not like?", "علی چه را دوست ندارد؟",
                    ["tea", "water", "coffee", "cheese"], 2,
                    "He says I don't like coffee.",
                    "می‌گوید I don't like coffee."),
            ],
            [
                mcq("How many things does Ali order?", "علی چند چیز سفارش "
                    "می‌دهد؟",
                    ["one", "two", "three", "none"], 0,
                    "Only water.", "فقط آب."),
                mcq("Which word makes the order polite?", "کدام واژه سفارش را "
                    "مؤدب می‌کند؟",
                    ["want", "would like", "have", "can"], 1,
                    "I would like is the polite form.", "I would like شکل "
                    "مؤدب است."),
            ],
            passage=passage(
                ("At the cafe", "در کافه"),
                ("Sara: Good morning. I would like a cup of tea, please.\n"
                 "Waiter: With milk?\n"
                 "Sara: No, thank you. No milk.\n"
                 "Ali: Can I have a glass of water? I don't like coffee.\n"
                 "Waiter: Of course. Anything to eat?\n"
                 "Ali: Some bread and cheese, please.",
                 "سارا: صبح بخیر. یک فنجان چای می‌خواهم، لطفاً.\n"
                 "پیشخدمت: با شیر؟\n"
                 "سارا: نه، ممنون. بدون شیر.\n"
                 "علی: می‌توانم یک لیوان آب بگیرم؟ قهوه دوست ندارم.\n"
                 "پیشخدمت: البته. چیزی برای خوردن؟\n"
                 "علی: کمی نان و پنیر، لطفاً."),
            ),
        ),
        lesson(
            "pre-u4-l4", "writing",
            ("My breakfast", "صبحانهٔ من"),
            ("Write four sentences about what you eat and drink in the "
             "morning.",
             "چهار جمله بنویس دربارهٔ آنچه صبح می‌خوری و می‌نوشی."),
            [
                ("Use the pattern I have ... for food and I drink ... for "
                 "drink. Two sentences about food and two about drink is "
                 "enough.",
                 "برای خوراکی از I have ... و برای نوشیدنی از I drink ... "
                 "استفاده کن. دو جمله دربارهٔ خوراکی و دو تا دربارهٔ نوشیدنی "
                 "کافی است."),
                ("Add please and thank you only when you are asking someone. "
                 "In a description of your own breakfast you do not need them.",
                 "please و thank you را تنها وقتی به کار ببر که از کسی چیزی "
                 "می‌خواهی. در توصیف صبحانهٔ خودت لازم نیستند."),
            ],
            [
                ("I have bread and cheese.", "نان و پنیر می‌خورم."),
                ("I drink a glass of milk.", "یک لیوان شیر می‌نوشم."),
            ],
            [
                mcq("Which sentence describes a drink?", "کدام جمله نوشیدنی را "
                    "توصیف می‌کند؟",
                    ["I have an egg.", "I drink tea.", "I like bread.",
                     "I have cheese."], 1, "Drink takes tea.",
                    "drink با tea می‌آید."),
                mcq("Which is the correct pattern?", "کدام الگو درست است؟",
                    ["I have a bread.", "I have some bread.",
                     "I have breads.", "I have two bread."], 1,
                    "Bread is uncountable: some bread.", "bread شمردنی نیست: "
                    "some bread."),
            ],
            [
                write("Write four sentences about your breakfast. Use I have "
                      "for food and I drink for drink. Say one thing you do "
                      "not like.",
                      "چهار جمله دربارهٔ صبحانه‌ات بنویس. برای خوراکی I have و "
                      "برای نوشیدنی I drink به کار ببر. یک چیز را که دوست نداری "
                      "بگو.",
                      30, ["and"], "Four short sentences, one negative with "
                      "don't, no plurals on uncountable nouns.",
                      "چهار جملهٔ کوتاه، یک منفی با don't، بدون جمع بستن "
                      "اسم‌های غیرقابل‌شمارش."),
                gap("I ___ tea in the morning.", ["drink", "have"],
                    "Drink for liquids.", "drink برای مایعات.", "one word"),
                mcq("Which is a negative sentence?", "کدام جمله منفی است؟",
                    ["I like tea.", "I don't like coffee.", "I have bread.",
                     "I drink milk."], 1, "Don't marks the negative.",
                    "don't نشانهٔ منفی است."),
            ],
        ),
    ],
)
