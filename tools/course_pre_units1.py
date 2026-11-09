#!/usr/bin/env python3
"""Pre-A1, units 1 and 2: hello, and the first numbers."""

from course_kit import gap, lesson, listen, mcq, passage, say, unit, write

U1 = unit(
    "pre-u1",
    ("Hello", "سلام"),
    ("Say hello, give your name, and ask someone their name.",
     "سلام کن، نامت را بگو و نام کسی را بپرس."),
    [
        lesson(
            "pre-u1-l1", "grammar",
            ("I am, you are", "I am، you are"),
            ("Join a person to a name or a place with am, is and are.",
             "شخص را با am، is و are به نام یا جا وصل کن."),
            [
                ("English sentences need a verb. The verb to be is the one "
                 "that says who someone is or where they are. I am Sara. You "
                 "are Ali. He is a teacher.",
                 "جملهٔ انگلیسی فعل لازم دارد. فعل to be می‌گوید کسی چه کسی است "
                 "یا کجاست: I am Sara، You are Ali، He is a teacher."),
                ("Use am with I, are with you, we and they, and is with he, "
                 "she and it. In speech people say the short form: I'm, you're, "
                 "he's, she's, it's.",
                 "با I از am، با you/we/they از are و با he/she/it از is استفاده "
                 "کن. در گفتار کوتاه می‌شود: I'm، you're، he's، she's، it's."),
            ],
            [
                ("I am from Iran.", "من اهل ایرانم."),
                ("You are my friend.", "تو دوست منی."),
                ("She is a student.", "او دانش‌آموز است."),
            ],
            [
                mcq("I ___ a student.", "من دانش‌آموزم.",
                    ["am", "is", "are", "be"], 0,
                    "I always takes am.", "I همیشه am می‌گیرد."),
                mcq("They ___ here.", "آن‌ها اینجا هستند.",
                    ["am", "is", "are", "be"], 2,
                    "We and they take are.", "we و they با are می‌آیند."),
            ],
            [
                mcq("He ___ Ali.", "او علی است.", ["am", "is", "are", "be"], 1,
                    "He and she take is.", "he و she با is می‌آیند."),
                gap("We ___ ready.", ["are"], "We takes are.",
                    "we با are می‌آید.", "one word"),
                gap("I ___ Maria.", ["am", "I'm"], "I takes am; I'm is the "
                    "short form.", "I با am می‌آید و I'm کوتاه آن است.",
                    "one word"),
            ],
        ),
        lesson(
            "pre-u1-l2", "vocabulary",
            ("Hello, goodbye, thank you", "Hello، goodbye، thank you"),
            ("Use the five words you need in every first conversation.",
             "پنج واژه‌ای را به کار ببر که در هر گفت‌وگوی اول لازم است."),
            [
                ("Say hello in the morning with good morning, in the "
                 "afternoon with good afternoon, and at night with good "
                 "evening. Hello and hi work at any time. Say goodbye when you "
                 "leave.",
                 "صبح بگو good morning، بعدازظهر good afternoon و شب good "
                 "evening. hello و hi هر وقتی به کار می‌روند. وقتی می‌روی "
                 "goodbye بگو."),
                ("Please and thank you are not decoration: in English, asking "
                 "without please sounds like an order. Say thank you when you "
                 "receive something, and say you're welcome when someone "
                 "thanks you.",
                 "please و thank you تزیین نیستند: در انگلیسی درخواست بی "
                 "please مثل دستور است. وقتی چیزی می‌گیری thank you بگو و وقتی "
                 "کسی تشکر می‌کند you're welcome."),
            ],
            [
                ("Good morning, Sara.", "صبح بخیر، سارا."),
                ("Thank you. — You're welcome.", "متشکرم. — خواهش می‌کنم."),
                ("Goodbye. See you tomorrow.", "خداحافظ. فردا می‌بینمت."),
            ],
            [
                mcq("It is 8 a.m. You say ___.", "ساعت ۸ صبح است. می‌گویی ___.",
                    ["good night", "good morning", "good evening",
                     "goodbye"], 1, "Morning is before twelve.",
                    "صبح پیش از دوازده است."),
                mcq("Someone says thank you. You say ___.", "کسی می‌گوید "
                    "thank you. می‌گویی ___.",
                    ["please", "you're welcome", "hello", "sorry"], 1,
                    "You're welcome answers thanks.", "you're welcome پاسخ "
                    "تشکر است."),
            ],
            [
                mcq("Which word do you use when you ask for something?",
                    "وقتی چیزی می‌خواهی کدام واژه را به کار می‌بری؟",
                    ["please", "thanks", "goodbye", "hi"], 0,
                    "Please makes a request polite.", "please درخواست را "
                    "مؤدب می‌کند."),
                gap("Good ___. See you tomorrow.", ["night", "bye"],
                    "Good bye is goodbye; good night is at night.",
                    "good bye همان goodbye است و good night شب است.",
                    "one word"),
                mcq("You meet a friend at 7 p.m. You say ___.",
                    "ساعت ۷ شب دوستی را می‌بینی. می‌گویی ___.",
                    ["good morning", "good evening", "good night", "good "
                     "afternoon"], 1, "Evening greeting, not a goodnight.",
                    "سلام شب، نه خداحافظی شب."),
            ],
        ),
        lesson(
            "pre-u1-l3", "listening",
            ("Hear the name", "نام را بشنو"),
            ("Understand a short introduction and pick out the name and the "
             "country.",
             "یک معرفی کوتاه را بفهم و نام و کشور را جدا کن."),
            [
                ("Listen for three things in a first meeting: the greeting, "
                 "the name, and the country. The name comes after I am or my "
                 "name is, and the country comes after from.",
                 "در نخستین دیدار سه چیز را بشنو: سلام، نام و کشور. نام پس از "
                 "I am یا my name is می‌آید و کشور پس از from."),
                ("You do not need every word. If you hear two of the three, "
                 "you can answer.",
                 "به همهٔ واژه‌ها نیاز نداری. اگر دو تا از سه را بشنوی می‌توانی "
                 "پاسخ دهی."),
            ],
            [
                ("Hello. I am Sara. I am from Iran.",
                 "سلام. من سارا هستم. اهل ایرانم."),
                ("Hi. My name is Tom. I am from Canada.",
                 "سلام. نام من تام است. اهل کانادا هستم."),
            ],
            [
                mcq("Sara is from ___.", "سارا اهل ___ است.",
                    ["Iran", "Canada", "Turkey", "Italy"], 0,
                    "She says I am from Iran.", "می‌گوید I am from Iran."),
                mcq("Tom's name is ___.", "نام تام ___ است.",
                    ["Sara", "Tom", "Ali", "Maria"], 1,
                    "He says my name is Tom.", "می‌گوید my name is Tom."),
            ],
            [
                listen("Good morning. My name is Maria. I am from Italy.",
                       "Where is Maria from?", "ماریا اهل کجاست؟",
                       ["Iran", "Italy", "Canada", "Turkey"], 1,
                       "She says from Italy.", "می‌گوید from Italy."),
                listen("Hello, I am Ali. I am a teacher.",
                       "What is Ali's job?", "شغل علی چیست؟",
                       ["a student", "a teacher", "a doctor", "a driver"], 1,
                       "He says I am a teacher.", "می‌گوید I am a teacher."),
                listen("Hi, I am Tom. This is Sara. She is my friend.",
                       "Who is Sara?", "سارا کیست؟",
                       ["Tom's teacher", "Tom's friend", "Tom's sister",
                        "Tom's mother"], 1,
                       "He says she is my friend.", "می‌گوید she is my friend."),
            ],
        ),
        lesson(
            "pre-u1-l4", "speaking",
            ("Say your name", "نامت را بگو"),
            ("Introduce yourself in three short sentences, out loud.",
             "خودت را در سه جملهٔ کوتاه با صدای بلند معرفی کن."),
            [
                ("Three sentences are enough for a first introduction: a "
                 "greeting, your name, and where you are from. Say them "
                 "slowly. Speed is not fluency at this level; being understood "
                 "is.",
                 "برای نخستین معرفی سه جمله کافی است: سلام، نام و جایی که از "
                 "آن آمدی. آرام بگو. در این سطح سرعت نشانهٔ روانی نیست؛ "
                 "فهمیده شدن است."),
                ("The rhythm of I am from Iran has one stress: Iran. Do not "
                 "put stress on every word.",
                 "آهنگ I am from Iran یک تکیه دارد: Iran. روی هر واژه تکیه "
                 "نگذار."),
            ],
            [
                ("Hello. I am Sara. I am from Iran.",
                 "سلام. من سارا هستم. اهل ایرانم."),
                ("Hi. My name is Tom. I am from Canada.",
                 "سلام. نام من تام است. اهل کانادا هستم."),
            ],
            [
                mcq("Which is a good first sentence?", "کدام جملهٔ اول خوب "
                    "است؟",
                    ["I am from Iran.", "Hello.", "My name is Sara.",
                     "Thank you."], 1, "A greeting comes first.",
                    "سلام اول می‌آید."),
                mcq("How many sentences do you need at this level?",
                    "در این سطح چند جمله لازم داری؟",
                    ["one long one", "three short ones", "ten",
                     "none"], 1, "Greeting, name, country.",
                    "سلام، نام، کشور."),
            ],
            [
                say("Hello. I am Sara. I am from Iran.",
                    "سلام. من سارا هستم. اهل ایرانم."),
                say("Hi. My name is Ali. I am a student.",
                    "سلام. نام من علی است. من دانش‌آموزم."),
                say("Good morning. I am Maria. I am from Italy. Nice to meet "
                    "you.", "صبح بخیر. من ماریا هستم. اهل ایتالیایم. از "
                    "آشنایی خوشحالم."),
            ],
        ),
    ],
)

U2 = unit(
    "pre-u2",
    ("One, two, three", "یک، دو، سه"),
    ("Count to twenty, use a and an, and say what day it is.",
     "تا بیست بشمار، a و an را به کار ببر و بگو چه روزی است."),
    [
        lesson(
            "pre-u2-l1", "grammar",
            ("A book, two books", "A book، two books"),
            ("Use a and an with one thing, and add -s for more than one.",
             "برای یک چیز a و an و برای بیش از یکی -s به کار ببر."),
            [
                ("One thing takes a before a consonant sound and an before a "
                 "vowel sound: a book, a pen, an apple, an egg. You do not use "
                 "a or an with a plural.",
                 "یک چیز پیش از صدای همخوان a و پیش از صدای مصوت an می‌گیرد: a "
                 "book، a pen، an apple، an egg. با جمع، a یا an نمی‌آید."),
                ("More than one usually adds -s: book → books, pen → pens. "
                 "Some words add -es: box → boxes. A few are irregular: one "
                 "man, two men; one child, two children.",
                 "بیش از یکی معمولاً -s می‌گیرد: book → books. بعضی واژه‌ها -es "
                 "می‌گیرند: box → boxes. چند تا بی‌قاعده‌اند: one man، two men؛ "
                 "one child، two children."),
            ],
            [
                ("This is a book.", "این یک کتاب است."),
                ("These are three books.", "این‌ها سه کتاب‌اند."),
                ("I have an apple and two eggs.",
                 "من یک سیب و دو تخم‌مرغ دارم."),
            ],
            [
                mcq("I have ___ apple.", "من یک سیب دارم.",
                    ["a", "an", "two", "the"], 1,
                    "Apple starts with a vowel sound.", "apple با صدای مصوت "
                    "آغاز می‌شود."),
                mcq("Two ___ are on the table.", "دو کتاب روی میز است.",
                    ["book", "books", "a book", "an book"], 1,
                    "Two needs a plural.", "two جمع می‌خواهد."),
            ],
            [
                mcq("She has ___ egg.", "او یک تخم‌مرغ دارد.",
                    ["a", "an", "some", "two"], 1,
                    "Egg starts with a vowel.", "egg با مصوت آغاز می‌شود."),
                gap("I see four ___.", ["books", "cars", "pens"],
                    "Numbers above one take a plural.",
                    "عددهای بالاتر از یک جمع می‌گیرند.", "one word"),
                gap("This is ___ pen.", ["a"], "Pen starts with a consonant.",
                    "pen با همخوان آغاز می‌شود.", "one word"),
            ],
        ),
        lesson(
            "pre-u2-l2", "vocabulary",
            ("Numbers and days", "عددها و روزها"),
            ("Count from one to twenty and name the seven days.",
             "از یک تا بیست بشمار و هفت روز را نام ببر."),
            [
                ("The numbers you need first: one, two, three, four, five, "
                 "six, seven, eight, nine, ten. Then eleven and twelve, then "
                 "thirteen to nineteen with -teen, then twenty.",
                 "عددهای نخست: one تا ten. بعد eleven و twelve، بعد سیزده تا "
                 "نوزده با -teen و بعد twenty."),
                ("The days are Monday, Tuesday, Wednesday, Thursday, Friday, "
                 "Saturday and Sunday. Wednesday is said WENZ-day: the first d "
                 "is silent.",
                 "روزها Monday تا Sunday هستند. Wednesday را WENZ-day می‌گویند: "
                 "d اول تلفظ نمی‌شود."),
            ],
            [
                ("Today is Monday.", "امروز دوشنبه است."),
                ("I have five books and twelve pens.",
                 "من پنج کتاب و دوازده خودکار دارم."),
                ("Saturday and Sunday are the weekend.",
                 "شنبه و یکشنبه آخر هفته‌اند."),
            ],
            [
                mcq("Which number is 13?", "کدام عدد ۱۳ است؟",
                    ["thirty", "thirteen", "three", "twelfth"], 1,
                    "Thirteen ends in -teen.", "thirteen به -teen ختم می‌شود."),
                mcq("The day after Tuesday is ___.", "روز پس از سه‌شنبه ___ "
                    "است.",
                    ["Monday", "Wednesday", "Friday", "Sunday"], 1,
                    "Monday, Tuesday, Wednesday.", "دوشنبه، سه‌شنبه، "
                    "چهارشنبه."),
            ],
            [
                gap("Ten and ten is ___.", ["twenty"], "10 + 10 = 20.",
                    "۱۰ + ۱۰ = ۲۰.", "one word"),
                mcq("Which day comes first in the week?", "کدام روز اول هفته "
                    "است؟",
                    ["Sunday", "Monday", "Saturday", "Friday"], 1,
                    "English weeks usually begin on Monday.",
                    "هفتهٔ انگلیسی معمولاً با دوشنبه آغاز می‌شود."),
                gap("There are ___ days in a week.", ["seven", "7"],
                    "Monday to Sunday.", "دوشنبه تا یکشنبه.", "one word"),
            ],
        ),
        lesson(
            "pre-u2-l3", "reading",
            ("My class", "کلاس من"),
            ("Read six short sentences and answer with the numbers in them.",
             "شش جملهٔ کوتاه را بخوان و با عددهای درونشان پاسخ بده."),
            [
                ("Read slowly and point at each number. The question words "
                 "you need here are how many and what.",
                 "آرام بخوان و به هر عدد اشاره کن. واژه‌های پرسشی که اینجا "
                 "لازم داری how many و what هستند."),
                ("A number in a sentence is a fact you can check: count the "
                 "items named next to it.",
                 "عدد در جمله واقعیتی است که می‌توانی بررسی کنی: اقلام کنارش "
                 "را بشمار."),
            ],
            [
                ("My name is Ali. I am a student. My class has twelve "
                 "students.", "نام من علی است. دانش‌آموزم. کلاسم دوازده "
                 "دانش‌آموز دارد."),
                ("Our teacher is Mrs Karimi. She is from Shiraz.",
                 "معلم ما خانم کریمی است. اهل شیراز است."),
            ],
            [
                mcq("How many students are in the class?", "کلاس چند "
                    "دانش‌آموز دارد؟",
                    ["two", "ten", "twelve", "twenty"], 2,
                    "The text says twelve students.", "متن می‌گوید twelve "
                    "students."),
                mcq("Where is the teacher from?", "معلم اهل کجاست؟",
                    ["Shiraz", "Tehran", "Italy", "Canada"], 0,
                    "She is from Shiraz.", "او اهل شیراز است."),
            ],
            [
                mcq("What is the writer's name?", "نام نویسنده چیست؟",
                    ["Karimi", "Ali", "Sara", "Tom"], 1,
                    "The first sentence gives the name.",
                    "جملهٔ اول نام را می‌دهد."),
                mcq("Who is Mrs Karimi?", "خانم کریمی کیست؟",
                    ["a student", "the teacher", "a friend", "the writer"],
                    1, "Our teacher is Mrs Karimi.", "معلم ما خانم کریمی است."),
            ],
            passage=passage(
                ("My class", "کلاس من"),
                ("My name is Ali. I am a student. My class has twelve "
                 "students. Our teacher is Mrs Karimi. She is from Shiraz. We "
                 "have five books and one computer.",
                 "نام من علی است. دانش‌آموزم. کلاسم دوازده دانش‌آموز دارد. معلم "
                 "ما خانم کریمی است. اهل شیراز است. ما پنج کتاب و یک رایانه "
                 "داریم."),
            ),
        ),
        lesson(
            "pre-u2-l4", "writing",
            ("Four sentences about your class",
             "چهار جمله دربارهٔ کلاس تو"),
            ("Write four short sentences with a number in each.",
             "چهار جملهٔ کوتاه بنویس که در هرکدام عددی باشد."),
            [
                ("At this level a good sentence is short, complete and true: "
                 "My class has twelve students. It needs a subject (my class), "
                 "a verb (has) and a number.",
                 "در این سطح جملهٔ خوب کوتاه، کامل و درست است: My class has "
                 "twelve students. به نهاد (my class)، فعل (has) و عدد نیاز "
                 "دارد."),
                ("Write the number in words, not digits, when the number is "
                 "small: five books, not 5 books. Both are correct; words are "
                 "better practice now.",
                 "عدد کوچک را با واژه بنویس، نه رقم: five books نه 5 books. هر "
                 "دو درست‌اند و واژه تمرین بهتری است."),
            ],
            [
                ("My class has twelve students.", "کلاسم دوازده دانش‌آموز دارد."),
                ("I have two books.", "من دو کتاب دارم."),
            ],
            [
                mcq("Which sentence is complete?", "کدام جمله کامل است؟",
                    ["Twelve students.", "My class has twelve students.",
                     "Has twelve.", "My class twelve students."], 1,
                    "It has a subject and a verb.", "نهاد و فعل دارد."),
                mcq("Write the number 7 as a word.", "عدد ۷ را با واژه بنویس.",
                    ["seventy", "seventeen", "seven", "seventh"], 2,
                    "Seven is 7.", "seven همان ۷ است."),
            ],
            [
                write("Write four sentences about your class. Use a number in "
                      "each one. Say how many students, how many books, how "
                      "many teachers, and one more thing.",
                      "چهار جمله دربارهٔ کلاس خودت بنویس. در هر جمله عددی به "
                      "کار ببر. بگو چند دانش‌آموز، چند کتاب، چند معلم و یک چیز "
                      "دیگر.",
                      30, ["and"], "Four short sentences, each with a number "
                      "written as a word.", "چهار جملهٔ کوتاه که در هرکدام "
                      "عددی با واژه نوشته شده."),
                gap("My class ___ ten students.", ["has"], "Have/has for "
                    "possession.", "have/has برای داشتن.", "one word"),
                mcq("Which is a number word?", "کدام واژه عدد است؟",
                    ["book", "three", "class", "teacher"], 1,
                    "Three is 3.", "three همان ۳ است."),
            ],
        ),
    ],
)
