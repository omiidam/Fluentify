#!/usr/bin/env python3
"""Write chapter six of the grammar book into books.json.

    python3 tools/chapter6.py

Chapter six of *Understanding and Using English Grammar* is Nouns. The book
shipped with two sections for it (6-1 plural and possessive nouns, 6-9 a few
and a little); this replaces them with the chapter's ten charts, written out
like chapters one to five: the rule, the form, examples in both languages,
three guided exercises and a three-question check for each.

It is idempotent: chapter six is always rebuilt from this script.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "books.json"


def ex(prompt, answer, why_en, why_fa):
    return {"prompt": prompt, "answer": answer, "why_en": why_en, "why_fa": why_fa}


def q(text, options, answer, why_en, why_fa):
    assert answer in options and len(options) == 3, text
    return {"q": text, "options": options, "answer": answer,
            "why_en": why_en, "why_fa": why_fa}


LESSONS = [
    {
        "section": "6-1",
        "title": "Plural forms of nouns: regular and irregular",
        "title_fa": "شکل‌های جمع اسم: باقاعده و بی‌قاعده",
        "use_en": "Most nouns add -s. Nouns ending in -ch, -sh, -ss, -x, -s or -o add -es, a consonant plus y changes to -ies, and some nouns ending in -f or -fe change to -ves. A short list is irregular and has to be learned: man, child, foot, tooth, woman, mouse and person. A few nouns do not change at all, such as sheep, fish and deer.",
        "use_fa": "بیشتر اسم‌ها s می‌گیرند. اسم‌های پایانه‌یافته به ch، sh، ss، x، s یا o پسوند es می‌گیرند، حرف بی‌صدا + y به ies تبدیل می‌شود و برخی اسم‌های پایانه‌یافته به f یا fe به ves تغییر می‌کنند. فهرست کوتاهی بی‌قاعده است و باید حفظ شود: man، child، foot، tooth، woman، mouse و person. چند اسم هیچ تغییری نمی‌کنند، مانند sheep، fish و deer.",
        "form_en": "noun + -s / -es / -ies / -ves  ·  child → children, man → men, tooth → teeth",
        "examples": [
            {"en": "Three children are waiting for the bus.",
             "fa": "سه کودک منتظر اتوبوس‌اند."},
            {"en": "The women in this office are engineers.",
             "fa": "زن‌های این دفتر مهندس‌اند."},
            {"en": "Two sheep are standing near the wall.",
             "fa": "دو گوسفند نزدیک دیوار ایستاده‌اند."},
        ],
        "exercises": [
            ex("There are three ___ (child) in the yard.", "children",
               "Child has the irregular plural children.",
               "child جمع بی‌قاعدهٔ children دارد."),
            ex("Put the two ___ (knife) on the table.", "knives",
               "A noun ending in -fe changes to -ves.",
               "اسم پایانه‌یافته به fe به ves تبدیل می‌شود."),
            ex("The ___ (city) in the north are cold in winter.", "cities",
               "A consonant plus y becomes -ies, and the verb is plural.",
               "حرف بی‌صدا + y به ies تبدیل می‌شود و فعل جمع است."),
        ],
        "exam": [
            q("My two ___ are at school.",
              ["children", "childs", "childes"], "children",
              "Child is one of the irregular plurals.",
              "child از جمع‌های بی‌قاعده است."),
            q("She bought three ___ of bread.",
              ["loaves", "loafs", "loafes"], "loaves",
              "Loaf ends in -f and changes to -ves.",
              "loaf به f ختم می‌شود و به ves تبدیل می‌شود."),
            q("The ___ are playing in the garden.",
              ["mice", "mouses", "mices"], "mice",
              "Mouse has the irregular plural mice.",
              "mouse جمع بی‌قاعدهٔ mice دارد."),
        ],
    },
    {
        "section": "6-2",
        "title": "Possessive nouns: 's, s' and of",
        "title_fa": "اسم‌های ملکی: 's، s' و of",
        "use_en": "Add 's to a singular noun and to an irregular plural: Ali's book, the children's toys. A regular plural ending in -s takes only an apostrophe: the students' books. Two people who own something together take one 's on the last name: Ali and Reza's room. For things rather than people, English usually prefers of: the color of the sky.",
        "use_fa": "به اسم مفرد و جمع بی‌قاعده s' می‌افزاییم: Ali's book، the children's toys. جمع باقاعدهٔ پایانه‌یافته به s تنها آپاستروف می‌گیرد: the students' books. دو نفری که چیزی را با هم دارند، یک s' روی نام آخر می‌گیرند: Ali and Reza's room. برای «چیزها» و نه «انسان‌ها»، انگلیسی معمولاً of را ترجیح می‌دهد: the color of the sky.",
        "form_en": "singular / irregular plural + 's  ·  plural in -s + '  ·  the … of the …",
        "examples": [
            {"en": "This is Sara's notebook.",
             "fa": "این دفتر ساراست."},
            {"en": "The students' papers are on the desk.",
             "fa": "مقاله‌های دانشجویان روی میز است."},
            {"en": "The door of the car is open.",
             "fa": "درِ ماشین باز است."},
        ],
        "exercises": [
            ex("That is Ali___ bicycle.", "Ali's",
               "One owner takes 's on the name.",
               "یک مالک، s' روی نام می‌گیرد."),
            ex("The ___ (teachers) room is upstairs.", "teachers'",
               "A regular plural ending in -s takes only an apostrophe.",
               "جمع باقاعدهٔ پایانه‌یافته به s تنها آپاستروف می‌گیرد."),
            ex("The ___ (children) books are colorful.", "children's",
               "An irregular plural takes 's, not an apostrophe alone.",
               "جمع بی‌قاعده s' می‌گیرد، نه تنها آپاستروف."),
        ],
        "exam": [
            q("This is my ___ car.",
              ["father's", "fathers", "fathers'"], "father's",
              "One father takes 's.",
              "یک پدر s' می‌گیرد."),
            q("The ___ coats are in the hall.",
              ["men's", "mens'", "mens"], "men's",
              "Men is an irregular plural, so it takes 's.",
              "men جمع بی‌قاعده است، پس s' می‌گیرد."),
            q("I like the smell ___ fresh bread.",
              ["of", "of the", "'s"], "of",
              "A thing, not a person, takes of; bread here is noncount.",
              "برای چیز و نه انسان از of استفاده می‌شود؛ bread غیرقابل‌شمارش است."),
        ],
    },
    {
        "section": "6-3",
        "title": "Count and noncount nouns: the difference",
        "title_fa": "اسم‌های قابل‌شمارش و غیرقابل‌شمارش: تفاوت",
        "use_en": "A count noun names something you can count one by one: a book, two books. It has a singular and a plural, takes a or an, and its verb agrees with its number. A noncount noun names something you cannot count that way: water, rice, advice, furniture. It has no plural, never takes a or an, and takes a singular verb.",
        "use_fa": "اسم قابل‌شمارش چیزی را نام می‌برد که می‌توان یکی‌یکی شمرد: a book، two books. مفرد و جمع دارد، a یا an می‌گیرد و فعلش با شمار آن هم‌خوان است. اسم غیرقابل‌شمارش چیزی را نام می‌برد که این‌گونه شمرده نمی‌شود: water، rice، advice، furniture. جمع ندارد، هرگز a یا an نمی‌گیرد و فعل مفرد می‌گیرد.",
        "form_en": "count: a chair / two chairs  ·  noncount: water, rice, advice (no plural, singular verb)",
        "examples": [
            {"en": "I need a chair, and my friend needs two chairs.",
             "fa": "من یک صندلی لازم دارم و دوستم دو صندلی."},
            {"en": "The furniture in this room is new.",
             "fa": "مبلمان این اتاق نو است."},
            {"en": "She gave me good advice.",
             "fa": "او به من مشاورهٔ خوبی داد."},
        ],
        "exercises": [
            ex("There are two ___ (chair) in the kitchen.", "chairs",
               "Chair is a count noun and two makes it plural.",
               "chair قابل‌شمارش است و two آن را جمع می‌کند."),
            ex("The furniture in my room ___ (be) old.", "is",
               "Furniture is noncount, so it takes a singular verb.",
               "furniture غیرقابل‌شمارش است، پس فعل مفرد می‌گیرد."),
            ex("I do not have much ___ (homework) tonight.", "homework",
               "Homework is noncount and has no plural form.",
               "homework غیرقابل‌شمارش است و شکل جمع ندارد."),
        ],
        "exam": [
            q("She has three ___ .",
              ["notebooks", "notebook", "a notebook"], "notebooks",
              "Three makes a count noun plural.",
              "سه، اسم قابل‌شمارش را جمع می‌کند."),
            q("The information ___ correct.",
              ["is", "are", "were"], "is",
              "Information is noncount and takes a singular verb.",
              "information غیرقابل‌شمارش است و فعل مفرد می‌گیرد."),
            q("We need ___ rice for dinner.",
              ["some", "a", "many"], "some",
              "A noncount noun takes some, never a or many.",
              "اسم غیرقابل‌شمارش some می‌گیرد، نه a یا many."),
        ],
    },
    {
        "section": "6-4",
        "title": "Noncount nouns: the categories and the surprises",
        "title_fa": "اسم‌های غیرقابل‌شمارش: دسته‌ها و شگفتی‌ها",
        "use_en": "Noncount nouns fall into groups: liquids and foods (water, bread, rice, cheese), materials (wood, glass, paper), abstractions (love, anger, knowledge, advice, information), school subjects and games (math, tennis, chess), weather (rain, snow), and whole collections (furniture, luggage, jewelry, equipment, money). Each of these is singular and has no plural.",
        "use_fa": "اسم‌های غیرقابل‌شمارش در دسته‌هایی جای می‌گیرند: مایعات و خوراکی‌ها (water، bread، rice، cheese)، مواد (wood، glass، paper)، مفاهیم انتزاعی (love، anger، knowledge، advice، information)، درس‌ها و بازی‌ها (math، tennis، chess)، هوا (rain، snow) و مجموعه‌های کامل (furniture، luggage، jewelry، equipment، money). هر یک مفرد است و جمع ندارد.",
        "form_en": "food · material · abstract · subject or game · weather · collection  → singular verb, no plural",
        "examples": [
            {"en": "The luggage is in the car.",
             "fa": "چمدان‌ها در ماشین‌اند."},
            {"en": "We play tennis on Fridays.",
             "fa": "جمعه‌ها تنیس بازی می‌کنیم."},
            {"en": "His knowledge of history is impressive.",
             "fa": "دانش او از تاریخ چشمگیر است."},
        ],
        "exercises": [
            ex("The equipment in the lab ___ (be) expensive.", "is",
               "Equipment is a collection noun, singular and noncount.",
               "equipment اسم مجموعه است، مفرد و غیرقابل‌شمارش."),
            ex("My luggage ___ (be) still at the airport.", "is",
               "Luggage is noncount, so the verb is singular.",
               "luggage غیرقابل‌شمارش است، پس فعل مفرد است."),
            ex("She studies ___ (math) every evening.", "math",
               "A school subject is noncount and takes no article.",
               "نام درس غیرقابل‌شمارش است و حرف تعریف نمی‌گیرد."),
        ],
        "exam": [
            q("The jewelry in that shop ___ very old.",
              ["is", "are", "were"], "is",
              "Jewelry is a collection noun and takes a singular verb.",
              "jewelry اسم مجموعه است و فعل مفرد می‌گیرد."),
            q("We need ___ for the trip.",
              ["information", "informations", "an information"], "information",
              "Information is noncount and has no plural.",
              "information غیرقابل‌شمارش است و جمع ندارد."),
            q("He plays ___ every weekend.",
              ["chess", "a chess", "chesses"], "chess",
              "A game is noncount and takes no article.",
              "نام بازی غیرقابل‌شمارش است و حرف تعریف نمی‌گیرد."),
        ],
    },
    {
        "section": "6-5",
        "title": "Units of measure with noncount nouns",
        "title_fa": "واحدهای اندازه‌گیری با اسم‌های غیرقابل‌شمارش",
        "use_en": "A noncount noun cannot take a number, but it can be counted through a unit: a piece of information, a glass of water, a loaf of bread, a bar of chocolate, a pair of shoes, two kilos of rice. The unit carries the plural, and the noncount noun stays singular: three pieces of advice.",
        "use_fa": "اسم غیرقابل‌شمارش عدد نمی‌گیرد، اما با یک واحد شمرده می‌شود: a piece of information، a glass of water، a loaf of bread، a bar of chocolate، a pair of shoes، two kilos of rice. واحد جمع می‌بندد و اسم غیرقابل‌شمارش مفرد می‌ماند: three pieces of advice.",
        "form_en": "a piece / glass / loaf / bar / pair / kilo / sheet of + noncount noun",
        "examples": [
            {"en": "He gave me two pieces of advice.",
             "fa": "او دو نصیحت به من کرد."},
            {"en": "I bought a loaf of bread and a bar of chocolate.",
             "fa": "یک نان و یک تخته شکلات خریدم."},
            {"en": "There are three sheets of paper on the desk.",
             "fa": "سه برگ کاغذ روی میز است."},
        ],
        "exercises": [
            ex("She gave me three ___ of advice.", "pieces",
               "The unit carries the plural, so piece becomes pieces.",
               "واحد جمع می‌بندد، پس piece به pieces تبدیل می‌شود."),
            ex("I would like a ___ of water.", "glass",
               "Water is noncount and is counted through a unit.",
               "water غیرقابل‌شمارش است و با واحد شمرده می‌شود."),
            ex("We need two ___ of bread.", "loaves",
               "The unit loaf takes the plural loaves.",
               "واحد loaf جمعش loaves است."),
        ],
        "exam": [
            q("There are two ___ of paper on the table.",
              ["sheets", "sheet", "sheetes"], "sheets",
              "Two makes the unit plural, and the noncount noun stays singular.",
              "دو، واحد را جمع می‌کند و اسم غیرقابل‌شمارش مفرد می‌ماند."),
            q("He drank a ___ of milk.",
              ["glass", "glasses", "piece"], "glass",
              "Milk is a liquid and is counted in glasses.",
              "شیر مایع است و با glass شمرده می‌شود."),
            q("I bought two ___ of chocolate.",
              ["bars", "bar", "barres"], "bars",
              "The unit takes the plural after two.",
              "واحد پس از two جمع می‌شود."),
        ],
    },
    {
        "section": "6-6",
        "title": "A few and a little",
        "title_fa": "a few و a little",
        "use_en": "A few goes with a plural count noun and a little goes with a noncount noun; both mean a small amount, and both sound positive. Without a, few and little mean not enough, and the sentence turns negative: he has few friends, so he is lonely.",
        "use_fa": "a few با اسم قابل‌شمارش جمع و a little با اسم غیرقابل‌شمارش می‌آید؛ هر دو مقدار کم را می‌رسانند و هر دو مثبت به گوش می‌رسند. بدون a، few و little یعنی «به اندازهٔ کافی نیست» و جمله منفی می‌شود: he has few friends, so he is lonely.",
        "form_en": "a few + plural count noun  ·  a little + noncount noun  ·  few / little = not enough",
        "examples": [
            {"en": "There are a few apples in the bowl.",
             "fa": "چند سیب در کاسه است."},
            {"en": "We have a little milk left.",
             "fa": "کمی شیر برایمان مانده است."},
            {"en": "He has few friends, so he feels lonely.",
             "fa": "دوستان کمی دارد، پس احساس تنهایی می‌کند."},
        ],
        "exercises": [
            ex("I need a ___ salt for the soup.", "little",
               "Salt is noncount, so the small amount is a little.",
               "نمک غیرقابل‌شمارش است، پس مقدار کم a little است."),
            ex("There are a ___ chairs in the garden.", "few",
               "Chairs is a plural count noun, so a few.",
               "chairs اسم قابل‌شمارش جمع است، پس a few."),
            ex("She has ___ time, so she cannot help us.", "little",
               "Without a, little means not enough time.",
               "بدون a، little یعنی زمان کافی نیست."),
        ],
        "exam": [
            q("There is a ___ water in the bottle.",
              ["little", "few", "many"], "little",
              "Water is noncount, so a little.",
              "water غیرقابل‌شمارش است، پس a little."),
            q("A ___ students were absent today.",
              ["few", "little", "much"], "few",
              "Students is a plural count noun, so a few.",
              "students اسم قابل‌شمارش جمع است، پس a few."),
            q("We have ___ money, so we cannot take a taxi.",
              ["little", "a little", "few"], "little",
              "Without a, little means not enough.",
              "بدون a، little یعنی به اندازهٔ کافی نیست."),
        ],
    },
    {
        "section": "6-7",
        "title": "Many and much",
        "title_fa": "many و much",
        "use_en": "Many goes with a plural count noun and much goes with a noncount noun. Both are used most naturally in questions and negatives: How many books? How much sugar? There isn't much time. In affirmative sentences, English usually prefers a lot of.",
        "use_fa": "many با اسم قابل‌شمارش جمع و much با اسم غیرقابل‌شمارش می‌آید. هر دو بیشتر در پرسش و منفی طبیعی‌اند: How many books? How much sugar? There isn't much time. در جملهٔ مثبت، انگلیسی معمولاً a lot of را ترجیح می‌دهد.",
        "form_en": "many + plural count noun  ·  much + noncount noun  ·  mostly in questions and negatives",
        "examples": [
            {"en": "How many students are in the class?",
             "fa": "چند دانش‌آموز در کلاس است؟"},
            {"en": "How much sugar do you take in your tea?",
             "fa": "چقدر شکر در چای می‌ریزی؟"},
            {"en": "There isn't much time before the train leaves.",
             "fa": "پیش از حرکت قطار زمان زیادی نیست."},
        ],
        "exercises": [
            ex("How ___ books did you buy?", "many",
               "Books is a plural count noun, so many.",
               "books اسم قابل‌شمارش جمع است، پس many."),
            ex("How ___ water should I add?", "much",
               "Water is noncount, so much.",
               "water غیرقابل‌شمارش است، پس much."),
            ex("There aren't ___ chairs in this room.", "many",
               "A negative with a plural count noun takes many.",
               "منفی با اسم قابل‌شمارش جمع many می‌گیرد."),
        ],
        "exam": [
            q("How ___ people came to the party?",
              ["many", "much", "a lot"], "many",
              "People is plural, so many.",
              "people جمع است، پس many."),
            q("I don't have ___ homework tonight.",
              ["much", "many", "a few"], "much",
              "Homework is noncount, so much.",
              "homework غیرقابل‌شمارش است، پس much."),
            q("She doesn't drink ___ coffee.",
              ["much", "many", "few"], "much",
              "Coffee is noncount, so much in a negative.",
              "coffee غیرقابل‌شمارش است، پس در منفی much."),
        ],
    },
    {
        "section": "6-8",
        "title": "A lot of, lots of and plenty of",
        "title_fa": "a lot of، lots of و plenty of",
        "use_en": "A lot of and lots of mean a large quantity and go with both count and noncount nouns: a lot of books, a lot of water. They are the natural choice in affirmative sentences. Plenty of means more than enough, and also goes with both kinds of noun.",
        "use_fa": "a lot of و lots of مقدار زیاد را می‌رسانند و با اسم‌های قابل‌شمارش و غیرقابل‌شمارش هر دو می‌آیند: a lot of books، a lot of water. در جملهٔ مثبت انتخاب طبیعی همین‌اند. plenty of یعنی بیش از اندازهٔ لازم و با هر دو نوع اسم می‌آید.",
        "form_en": "a lot of / lots of / plenty of + count or noncount noun",
        "examples": [
            {"en": "She has a lot of friends in Shiraz.",
             "fa": "او در شیراز دوستان زیادی دارد."},
            {"en": "There is a lot of water in the pool.",
             "fa": "آب زیادی در استخر است."},
            {"en": "Don't hurry; we have plenty of time.",
             "fa": "عجله نکن؛ وقت به اندازهٔ کافی داریم."},
        ],
        "exercises": [
            ex("There are ___ of people in the street.", "a lot",
               "A lot of goes with a plural count noun in an affirmative sentence.",
               "a lot of با اسم قابل‌شمارش جمع در جملهٔ مثبت می‌آید."),
            ex("We have ___ of time before the movie.", "plenty",
               "Plenty of means more than enough and fits here.",
               "plenty of یعنی بیش از اندازهٔ لازم و اینجا مناسب است."),
            ex("He spends ___ of money on books.", "a lot",
               "A lot of works with the noncount noun money.",
               "a lot of با اسم غیرقابل‌شمارش money به کار می‌رود."),
        ],
        "exam": [
            q("There is ___ of milk in the fridge.",
              ["a lot", "many", "a few"], "a lot",
              "Milk is noncount, so a lot of, not many or a few.",
              "milk غیرقابل‌شمارش است، پس a lot of، نه many یا a few."),
            q("She has ___ of homework this weekend.",
              ["lots", "many", "few"], "lots",
              "Lots of goes with a noncount noun.",
              "lots of با اسم غیرقابل‌شمارش می‌آید."),
            q("We have ___ of chairs for everyone.",
              ["plenty", "much", "a little"], "plenty",
              "Chairs is plural and plenty of means enough.",
              "chairs جمع است و plenty of یعنی به اندازهٔ کافی."),
        ],
    },
    {
        "section": "6-9",
        "title": "Nouns that look plural and are not",
        "title_fa": "اسم‌هایی که جمع به نظر می‌رسند و نیستند",
        "use_en": "News, advice, information, homework, research, furniture and money end in -s or name many things, but they are noncount and take a singular verb: the news is good, this information is useful. They never take a plural verb, and they have no plural form.",
        "use_fa": "news، advice، information، homework، research، furniture و money با s تمام می‌شوند یا چیزهای زیادی را نام می‌برند، اما غیرقابل‌شمارش‌اند و فعل مفرد می‌گیرند: the news is good، this information is useful. هرگز فعل جمع نمی‌گیرند و شکل جمع ندارند.",
        "form_en": "news / information / advice / homework / research / money + singular verb",
        "examples": [
            {"en": "The news is good today.",
             "fa": "امروز خبرها خوب است."},
            {"en": "This information is very useful.",
             "fa": "این اطلاعات بسیار سودمند است."},
            {"en": "Her homework is already finished.",
             "fa": "تکلیف او پیش‌تر تمام شده است."},
        ],
        "exercises": [
            ex("The news ___ (be) surprising.", "is",
               "News ends in -s but is noncount and singular.",
               "news با s تمام می‌شود اما غیرقابل‌شمارش و مفرد است."),
            ex("The money on the table ___ (be) mine.", "is",
               "Money is noncount and takes a singular verb.",
               "money غیرقابل‌شمارش است و فعل مفرد می‌گیرد."),
            ex("His research on the topic ___ (be) excellent.", "is",
               "Research is noncount and never takes a plural verb.",
               "research غیرقابل‌شمارش است و هرگز فعل جمع نمی‌گیرد."),
        ],
        "exam": [
            q("The news ___ very good this morning.",
              ["is", "are", "were"], "is",
              "News is singular despite its -s.",
              "news با وجود s مفرد است."),
            q("This advice ___ helpful.",
              ["is", "are", "have"], "is",
              "Advice is noncount and singular.",
              "advice غیرقابل‌شمارش و مفرد است."),
            q("The homework ___ too long.",
              ["is", "are", "were"], "is",
              "Homework is noncount, so the verb is singular.",
              "homework غیرقابل‌شمارش است، پس فعل مفرد است."),
        ],
    },
    {
        "section": "6-10",
        "title": "Nouns always plural, and nouns with two meanings",
        "title_fa": "اسم‌های همیشه جمع و اسم‌های دو معنایی",
        "use_en": "Some nouns name a pair and are always plural: scissors, glasses, pants, jeans, shoes, clothes. They take a plural verb, and one of them is a pair of. Other nouns change meaning with a or a plural: paper is the material but a paper is a newspaper or an essay, glass is the material but a glass is a cup, chicken is the meat but a chicken is the bird.",
        "use_fa": "برخی اسم‌ها یک جفت را نام می‌برند و همیشه جمع‌اند: scissors، glasses، pants، jeans، shoes، clothes. فعل جمع می‌گیرند و یکی از آن‌ها a pair of است. اسم‌های دیگری با a یا جمع تغییر معنا می‌دهند: paper ماده است اما a paper روزنامه یا مقاله، glass ماده است اما a glass لیوان، chicken گوشت است اما a chicken مرغ.",
        "form_en": "pair nouns + plural verb  ·  a pair of scissors  ·  paper / a paper, glass / a glass",
        "examples": [
            {"en": "My scissors are on the desk.",
             "fa": "قیچی من روی میز است."},
            {"en": "I need a pair of shoes for the trip.",
             "fa": "برای سفر به یک جفت کفش نیاز دارم."},
            {"en": "The window is made of glass, and I drank a glass of water.",
             "fa": "پنجره از شیشه است و من یک لیوان آب خوردم."},
        ],
        "exercises": [
            ex("My jeans ___ (be) still wet.", "are",
               "Jeans names a pair and takes a plural verb.",
               "jeans یک جفت را نام می‌برد و فعل جمع می‌گیرد."),
            ex("She bought a ___ of glasses.", "pair",
               "One of a pair noun is a pair of.",
               "برای یکی از اسم‌های جفتی a pair of می‌گوییم."),
            ex("I read an interesting ___ about the city.", "paper",
               "A paper is an essay or a newspaper, a count noun.",
               "a paper یعنی مقاله یا روزنامه و قابل‌شمارش است."),
        ],
        "exam": [
            q("These pants ___ too long for me.",
              ["are", "is", "was"], "are",
              "Pants is always plural.",
              "pants همیشه جمع است."),
            q("The table is made of ___ .",
              ["wood", "a wood", "woods"], "wood",
              "The material is noncount and takes no article.",
              "ماده غیرقابل‌شمارش است و حرف تعریف نمی‌گیرد."),
            q("Would you like ___ glass of water?",
              ["a", "some", "many"], "a",
              "A glass is one cup, a count noun, so it takes a.",
              "a glass یعنی یک لیوان، قابل‌شمارش است، پس a می‌گیرد."),
        ],
    },
]

ABOUT_EN = ("The grammar of the whole course, chapter by chapter and chart by chart: "
            "sixty-seven structures from the book's twenty chapters, each with the "
            "rule, a pattern, examples of it, exercises and a short exam. Chapters one "
            "to six are complete, chart 1-1 to 6-10. The explanations and sentences are "
            "written for this app; the book is the reference text.")
ABOUT_FA = ("دستور زبان تمام دوره، فصل به فصل و نمودار به نمودار: شصت‌وهفت ساختار از "
            "بیست فصل کتاب، هر یک با قاعده، الگو، مثال، تمرین و یک آزمون کوتاه. "
            "فصل‌های یک تا شش کامل‌اند، از نمودار ۱-۱ تا ۶-۱۰. توضیح‌ها و جمله‌ها برای "
            "همین برنامه نوشته شده‌اند و کتاب متن مرجع است.")


def main() -> int:
    data = json.loads(BOOKS.read_text(encoding="utf-8"))
    book = next(b for b in data["books"] if b.get("kind") == "grammar")

    old = [l for l in book["lessons"] if l.get("chapter") == "Chapter 6"]
    assert old, "chapter six is not in the book"
    first = book["lessons"].index(old[0])
    rest = [l for l in book["lessons"] if l.get("chapter") != "Chapter 6"]

    chapter6 = []
    for lesson in LESSONS:
        chapter6.append({
            "n": 0, "title": lesson["title"], "title_fa": lesson["title_fa"],
            "chapter": "Chapter 6", "section": lesson["section"],
            "use_en": lesson["use_en"], "use_fa": lesson["use_fa"],
            "form_en": lesson["form_en"], "examples": lesson["examples"],
            "exercises": lesson["exercises"], "exam": lesson["exam"],
        })

    lessons = rest[:first] + chapter6 + rest[first:]
    for i, lesson in enumerate(lessons, 1):
        lesson["n"] = i
    book["lessons"] = lessons
    book["about_en"] = ABOUT_EN
    book["about_fa"] = ABOUT_FA

    BOOKS.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")
    print(f"chapter six: {len(chapter6)} charts, {len(lessons)} structures in the book")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
