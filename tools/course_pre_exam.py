#!/usr/bin/env python3
"""The Pre-A1 final examination: 33 marks over six sections.

The first paper a learner meets. Every item uses only what the six Pre-A1
units teach: to be, a/an, one and many, there is/are, in/on/under, the present
simple with I and he/she, like, and the first forty words of daily life.
"""

from course_kit import exam, listen, mcq, reading_item, say, section, write

BLURB = (
    "Six skills, each marked on its own. Grammar, vocabulary, reading and "
    "listening are marked from your answers; writing is marked against a "
    "short rubric; speaking is marked from what this device hears you say. You "
    "need 60% overall and at least 50% in every skill.",
    "شش مهارت، هر یک جداگانه. گرامر، واژگان، خواندن و شنیدن از پاسخ‌ها نمره "
    "می‌گیرند؛ نوشتن با معیار کوتاهی سنجیده می‌شود و گفتن از آنچه دستگاه "
    "می‌شنود. برای قبولی ۶۰٪ کل و دست‌کم ۵۰٪ در هر مهارت لازم است.",
)

GRAMMAR = [
    mcq("I ___ from Iran.", "من اهل ایرانم.",
        ["am", "is", "are", "be"], 0,
        "I takes am.", "I با am می‌آید."),
    mcq("She ___ a teacher.", "او معلم است.",
        ["am", "is", "are", "be"], 1,
        "She takes is.", "she با is می‌آید."),
    mcq("This is ___ apple.", "این یک سیب است.",
        ["a", "an", "two", "the"], 1,
        "Apple starts with a vowel sound.", "apple با صدای مصوت آغاز می‌شود."),
    mcq("There ___ two shops here.", "اینجا دو مغازه هست.",
        ["is", "are", "be", "has"], 1,
        "Two shops is plural.", "دو مغازه جمع است."),
    mcq("My keys are ___ my bag.", "کلیدهایم در کیفم هستند.",
        ["in", "on", "at", "to"], 0,
        "Inside is in.", "درون یعنی in."),
    mcq("He ___ in a hospital.", "او در بیمارستان کار می‌کند.",
        ["work", "works", "working", "is work"], 1,
        "He takes -s.", "he با -s می‌آید."),
    mcq("I ___ like coffee.", "قهوه دوست ندارم.",
        ["don't", "not", "no", "am not"], 0,
        "The negative is don't + verb.", "منفی don't + فعل است."),
    mcq("___ you like tea?", "چای دوست داری؟",
        ["Do", "Are", "Is", "Does"], 0,
        "You takes do in questions.", "you در پرسش do می‌گیرد."),
]

VOCABULARY = [
    mcq("You drink ___.", "___ را می‌نوشی.",
        ["bread", "water", "rice", "cheese"], 1,
        "Water is a drink.", "water نوشیدنی است."),
    mcq("My father's daughter is my ___.", "دختر پدرم ___ من است.",
        ["mother", "sister", "son", "brother"], 1,
        "She is your sister.", "او خواهرت است."),
    mcq("You buy bread at a ___.", "نان را از ___ می‌خری.",
        ["bank", "shop", "hospital", "park"], 1,
        "A shop sells food.", "مغازه خوراکی می‌فروشد."),
    mcq("The day after Monday is ___.", "روز پس از دوشنبه ___ است.",
        ["Sunday", "Tuesday", "Friday", "Saturday"], 1,
        "Monday, Tuesday.", "دوشنبه، سه‌شنبه."),
    mcq("Which is a number word?", "کدام واژه عدد است؟",
        ["window", "seven", "sister", "bread"], 1,
        "Seven is 7.", "seven همان ۷ است."),
    mcq("You see a doctor at a ___.", "پزشک را در ___ می‌بینی.",
        ["park", "bank", "hospital", "bus stop"], 2,
        "Hospitals have doctors.", "بیمارستان پزشک دارد."),
    mcq("The opposite of near is ___.", "متضاد near ___ است.",
        ["left", "far", "under", "right"], 1,
        "Near and far are a pair.", "near و far یک جفت‌اند."),
    mcq("At 11 p.m. you ___.", "ساعت ۱۱ شب ___.",
        ["eat breakfast", "sleep", "go to school", "wake up"], 1,
        "Night is for sleeping.", "شب برای خوابیدن است."),
]

READING = [
    reading_item(
        ("My friend", "دوست من"),
        ("This is my friend Maria. She is from Italy. She is a student. She "
         "lives near my house. We study English together.",
         "این دوست من ماریا است. اهل ایتالیاست. دانش‌آموز است. نزدیک خانهٔ من "
         "زندگی می‌کند. با هم انگلیسی می‌خوانیم."),
        [
            mcq("Where is Maria from?", "ماریا اهل کجاست؟",
                ["Iran", "Italy", "Canada", "Turkey"], 1,
                "She is from Italy.", "اهل ایتالیاست."),
            mcq("What is Maria's job?", "شغل ماریا چیست؟",
                ["teacher", "student", "driver", "doctor"], 1,
                "She is a student.", "او دانش‌آموز است."),
            mcq("Where does Maria live?", "ماریا کجا زندگی می‌کند؟",
                ["far from the writer", "near the writer's house",
                 "in a school", "in a shop"], 1,
                "She lives near my house.", "نزدیک خانهٔ من زندگی می‌کند."),
        ],
    ),
    reading_item(
        ("At the shop", "در مغازه"),
        ("Ali: Good morning. I would like bread and cheese, please.\n"
         "Man: Here you are. Anything to drink?\n"
         "Ali: A glass of water, please. Thank you.",
         "علی: صبح بخیر. نان و پنیر می‌خواهم، لطفاً.\n"
         "مرد: بفرمایید. نوشیدنی هم می‌خواهی؟\n"
         "علی: یک لیوان آب، لطفاً. متشکرم."),
        [
            mcq("What does Ali buy to eat?", "علی چه چیزی برای خوردن می‌خرد؟",
                ["rice and fish", "bread and cheese", "an apple", "an egg"],
                1, "Bread and cheese.", "نان و پنیر."),
            mcq("What does he drink?", "چه می‌نوشد؟",
                ["tea", "milk", "water", "coffee"], 2,
                "A glass of water.", "یک لیوان آب."),
            mcq("What time of day is it?", "چه وقتی از روز است؟",
                ["morning", "afternoon", "evening", "night"], 0,
                "He says good morning.", "می‌گوید good morning."),
        ],
    ),
]

LISTENING = [
    listen("Hello. I am Tom. I am from Canada.",
           "Where is Tom from?", "تام اهل کجاست؟",
           ["Iran", "Italy", "Canada", "Turkey"], 2,
           "He says from Canada.", "می‌گوید from Canada."),
    listen("I wake up at seven and eat breakfast at eight.",
           "When does the speaker eat breakfast?",
           "گوینده کِی صبحانه می‌خورد؟",
           ["at six", "at seven", "at eight", "at nine"], 2,
           "Breakfast is at eight.", "صبحانه ساعت هشت است."),
    listen("The bank is on the left. The park is on the right.",
           "Where is the park?", "پارک کجاست؟",
           ["on the left", "on the right", "near the bank", "far away"], 1,
           "The park is on the right.", "پارک سمت راست است."),
    listen("This is my sister. She is twelve. She is a student.",
           "How old is the sister?", "خواهر چند ساله است؟",
           ["two", "ten", "twelve", "twenty"], 2,
           "She is twelve.", "او دوازده ساله است."),
    listen("I don't like coffee. I drink tea.",
           "What does the speaker drink?", "گوینده چه می‌نوشد؟",
           ["coffee", "tea", "milk", "water"], 1,
           "I drink tea.", "چای می‌نوشم."),
    listen("There is a school near my house. There are two shops too.",
           "How many shops are there?", "چند مغازه هست؟",
           ["one", "two", "three", "none"], 1,
           "There are two shops.", "دو مغازه هست."),
]

WRITING = [
    write("Write four sentences about yourself: your name, your country, "
          "your job or school, and one thing you like.",
          "چهار جمله دربارهٔ خودت بنویس: نامت، کشورت، شغلت یا مدرسه‌ات و یک چیز "
          "که دوست داری.",
          30, ["and"], "Four complete short sentences; I am and I like used "
          "correctly; no short forms needed.",
          "چهار جملهٔ کوتاه و کامل؛ I am و I like درست به کار رفته باشد؛ "
          "کوتاه‌سازی لازم نیست."),
    write("Write four sentences about your day. Use at with two clock times.",
          "چهار جمله دربارهٔ روزت بنویس. با دو ساعت at به کار ببر.",
          30, ["and"], "Present simple with I, at + time, one meal and one "
          "daily action.", "حال ساده با I، at + زمان، یک وعده غذا و یک کار "
          "روزانه."),
]

SPEAKING = [
    say("Hello. I am Sara. I am from Iran. I am a student.",
        "سلام. من سارا هستم. اهل ایرانم. دانش‌آموزم."),
    say("I live near the park. There is a shop on my street.",
        "نزدیک پارک زندگی می‌کنم. در خیابان من مغازه‌ای هست."),
    say("Excuse me, where is the bank, please?",
        "ببخشید، بانک کجاست، لطفاً؟"),
]

PAPER = exam(
    60, 0.6, 0.5, BLURB,
    [
        section("grammar", GRAMMAR),
        section("vocabulary", VOCABULARY),
        section("reading", READING),
        section("listening", LISTENING),
        section("writing", WRITING),
        section("speaking", SPEAKING),
    ],
)
