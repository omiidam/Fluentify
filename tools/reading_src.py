"""The content behind reading.json - six strategies and their practice readings.

Written here rather than in JSON so the passages and their answer keys sit next
to the check that refuses to publish a key that cannot be reached from the text.
tools/build_reading.py turns this into reading.json.
"""


def bi(en: str, fa: str) -> dict:
    return {"en": en, "fa": fa}


STRATEGIES = [
    # ---------------------------------------------------------------- 1 -----
    {
        "id": "skim",
        "icon": "🦅",
        "level": "B1",
        "title": bi("Skim for the main idea", "سریع بخوان و ایدهٔ اصلی را بگیر"),
        "blurb": bi(
            "Read the first and last sentence of every paragraph before you "
            "read any of them slowly.",
            "پیش از خواندنِ آرام، جملهٔ اول و آخر هر پاراگراف را بخوان."),
        "what": bi(
            "Skimming is reading for the shape of a text, not its details. You "
            "look at the title, the first sentence of each paragraph and the "
            "last paragraph, and you deliberately skip everything else, asking "
            "one question: what is this text about, and what does the writer "
            "want me to think about it? You finish in a minute or two, with a "
            "map in your head instead of a pile of sentences.",
            "سُرمه‌کشی (skim) یعنی خواندن برای فهمیدنِ شمای کلی متن، نه جزئیات. "
            "عنوان، جملهٔ اول هر پاراگراف و پاراگراف آخر را می‌خوانی و بقیه را "
            "عمداً رد می‌کنی و فقط یک سؤال داری: این متن دربارهٔ چیست و نویسنده "
            "می‌خواهد من چه فکری بکنم؟ در یکی دو دقیقه تمام می‌شود و به‌جای "
            "تپه‌ای از جمله، یک نقشهٔ کلی از متن در ذهنت داری."),
        "why": bi(
            "Reading word by word in a second language is slow, and slow "
            "reading loses the thread: by the end of a long sentence you have "
            "forgotten how it started. Skimming first gives the details a place "
            "to land, so the second, careful read is faster than reading once, "
            "slowly, would have been.",
            "کلمه‌به‌کلمه خواندن در زبان دوم کند است و در خواندنِ کند رشتهٔ کلام "
            "از دست می‌رود: تا آخر یک جملهٔ بلند، ابتدایش را فراموش کرده‌ای. "
            "اگر اول سُرمه‌کشی کنی، جزئیات جایی برای نشستن پیدا می‌کنند و "
            "خواندنِ دقیقِ بعدی از یک بار خواندنِ آرام هم سریع‌تر می‌شود."),
        "steps": [
            bi("Read the title and the first line. Guess the topic in one word.",
               "عنوان و خط اول را بخوان. موضوع را با یک کلمه حدس بزن."),
            bi("Read only the first sentence of each paragraph and the whole of "
               "the last one.",
               "فقط جملهٔ اول هر پاراگراف و تمام پاراگراف آخر را بخوان."),
            bi("Say the main idea to yourself in one sentence. If you cannot, "
               "you have not found it yet - look again at the last paragraph, "
               "where writers usually say what they actually think.",
               "ایدهٔ اصلی را با یک جمله برای خودت بگو. اگر نمی‌توانی، یعنی هنوز "
               "پیدایش نکرده‌ای؛ دوباره پاراگراف آخر را ببین، چون نویسنده "
               "معمولاً آنجا نظر واقعی‌اش را می‌گوید."),
            bi("Only now read the details, with that sentence as a hook.",
               "حالا و فقط حالا جزئیات را بخوان، با همان جمله به‌عنوان قلاب."),
        ],
        "reading": {
            "title": bi("Night trains are back", "قطارهای شبانه برگشته‌اند"),
            "level": "B1",
            "paragraphs": [
                "Europe's night trains are coming back. A decade ago sleeper "
                "services were closing one by one: they were slow, they lost "
                "money, and budget airlines were cheaper. Today new routes link "
                "Vienna to Paris, Berlin to Stockholm and Amsterdam to Zurich, "
                "and tickets for the best cabins sell out weeks in advance.",
                "The reason is not only the climate. Air travel has become less "
                "pleasant: airports are crowded, security queues are long, and a "
                "short flight often costs a whole day once you count the trip to "
                "the airport. A night train turns that wasted day into sleep. You "
                "leave a city centre after dinner and arrive in another city "
                "centre in time for breakfast, with a bed, a window and no "
                "luggage limit.",
                "Operators still face hard problems. Carriages are old, tracks "
                "are shared with freight, and a train that crosses four countries "
                "needs four sets of paperwork. Two of the new routes have already "
                "been cancelled.",
                "Even so, the direction is clear. When a journey of twelve hours "
                "can be spent asleep instead of in an airport, a growing number "
                "of travellers are choosing the slower way, and arriving more "
                "rested than they left.",
            ],
            "summary": bi(
                "Night trains are returning because a flight wastes a day at the "
                "airport, while a sleeper turns the same hours into sleep. Old "
                "carriages and borders still make the business difficult, but "
                "travellers are choosing the train anyway.",
                "قطارهای شبانه برمی‌گردند چون پرواز یک روز را در فرودگاه تلف "
                "می‌کند، در حالی که قطار همان ساعت‌ها را به خواب تبدیل می‌کند. "
                "واگن‌های قدیمی و مرزها کار را سخت می‌کنند، اما مسافران با این "
                "حال قطار را انتخاب می‌کنند."),
        },
        "questions": {
            "blanks": [
                {"sentence": "A decade ago sleeper services were closing because "
                             "they were slow, they lost money, and ___ were cheaper.",
                 "answer": "budget airlines",
                 "hint": bi("Two words, from paragraph 1.", "دو کلمه، از پاراگراف اول.")},
                {"sentence": "Tickets for the best cabins sell out weeks in ___.",
                 "answer": "advance",
                 "hint": bi("A fixed phrase: in advance = before the date.",
                            "یک عبارت ثابت: in advance یعنی پیش از موعد.")},
                {"sentence": "A night train turns that wasted day into ___.",
                 "answer": "sleep",
                 "hint": bi("One noun, paragraph 2.", "یک اسم، پاراگراف دوم.")},
                {"sentence": "Carriages are old and the tracks are shared with ___.",
                 "answer": "freight",
                 "hint": bi("Goods carried by train - paragraph 3.",
                            "بارهایی که با قطار حمل می‌شوند؛ پاراگراف سوم.")},
            ],
            "mcq": [
                {"q": "What is the passage mainly about?",
                 "options": ["Why airports are crowded",
                             "The return of night trains in Europe",
                             "How to buy cheap tickets",
                             "The history of the railways"],
                 "answer": 1,
                 "why": bi("Every paragraph is about sleepers coming back, and "
                           "the last one states it outright: the direction is clear.",
                           "همهٔ پاراگراف‌ها دربارهٔ بازگشت قطارهای شبانه‌اند و "
                           "پاراگراف آخر هم صریح می‌گوید: مسیر روشن است.")},
                {"q": "According to paragraph 2, one problem with flying is that",
                 "options": ["planes are often late",
                             "a short flight can take a whole day",
                             "you cannot sleep on a plane",
                             "tickets have become expensive"],
                 "answer": 1,
                 "why": bi("'A short flight often costs a whole day once you "
                           "count the trip to the airport.'",
                           "«یک پرواز کوتاه اگر رفتن به فرودگاه را حساب کنی، "
                           "اغلب یک روز کامل هزینه دارد.»")},
                {"q": "How does the writer treat the problems in paragraph 3?",
                 "options": ["As proof that night trains will fail",
                             "By ignoring them",
                             "As real, but not enough to change the trend",
                             "By blaming the passengers"],
                 "answer": 2,
                 "why": bi("The problems come first, then 'Even so, the direction "
                           "is clear' - the concession sets up the conclusion.",
                           "اول مشکلات می‌آید و بعد «با این حال، مسیر روشن است»؛ "
                           "این پذیرشِ ایراد، مقدمهٔ نتیجه‌گیری است.")},
                {"q": "The phrase 'the slower way' refers to",
                 "options": ["driving across Europe",
                             "travelling overnight by train",
                             "taking a long flight with a stop",
                             "walking to the station"],
                 "answer": 1,
                 "why": bi("It contrasts with the flight that 'costs a whole day'.",
                           "در مقابل پروازی است که «یک روز کامل» را می‌گیرد.")},
            ],
            "truefalse": [
                {"statement": "Sleeper services disappeared completely ten years ago.",
                 "answer": False,
                 "why": bi("They were 'closing one by one', not gone.",
                           "«یکی‌یکی بسته می‌شدند»، نه اینکه کاملاً از بین رفته باشند.")},
                {"statement": "The writer says the climate is the only reason for "
                              "the comeback.",
                 "answer": False,
                 "why": bi("'The reason is not only the climate' - comfort and "
                           "time are the others.",
                           "«دلیل فقط اقلیم نیست»؛ راحتی و زمان هم دلیل‌اند.")},
                {"statement": "New routes include Vienna to Paris.",
                 "answer": True,
                 "why": bi("Named in the first paragraph with two more routes.",
                           "در پاراگراف اول همراه دو مسیر دیگر نام برده شده است.")},
                {"statement": "The writer expects train passengers to arrive less "
                              "tired than plane passengers.",
                 "answer": True,
                 "why": bi("'arriving more rested than they left.'",
                           "«با استراحت بیشتر از وقتی که رفتند» می‌رسند.")},
            ],
            "essay": [
                {"prompt": bi("State the main idea of this passage in one or two "
                              "sentences of your own. Do not copy the first sentence.",
                              "ایدهٔ اصلی متن را در یکی دو جملهٔ خودت بنویس؛ "
                              "جملهٔ اول متن را کپی نکن."),
                 "tips": [bi("Name the subject: night trains.",
                             "موضوع را نام ببر: قطارهای شبانه."),
                          bi("Say what changed: they were closing, now they are growing.",
                             "بگو چه چیزی عوض شد: در حال تعطیلی بودند، حالا رشد می‌کنند."),
                          bi("Say why, in four or five words.",
                             "دلیل را در چهار پنج کلمه بگو.")],
                 "model": bi("Night trains, which were closing across Europe ten "
                             "years ago, are opening new routes again. Travellers "
                             "are coming back to them because sleeping through a "
                             "journey is better use of a day than waiting in an "
                             "airport.",
                             "قطارهای شبانه‌ای که ده سال پیش در اروپا یکی‌یکی "
                             "تعطیل می‌شدند، دوباره مسیرهای تازه باز می‌کنند. "
                             "مسافران به این دلیل برمی‌گردند که خوابیدن در سفر "
                             "استفادهٔ بهتری از یک روز است تا انتظار در فرودگاه.")},
                {"prompt": bi("The writer says 'the direction is clear'. Do you "
                              "agree that night trains will keep growing? Use one "
                              "detail from the passage and one idea of your own.",
                              "نویسنده می‌گوید «مسیر روشن است». آیا موافقی که "
                              "قطارهای شبانه به رشد ادامه می‌دهند؟ یک جزئیات از "
                              "متن و یک ایدهٔ خودت را بیاور."),
                 "tips": [bi("Take a side in the first sentence.",
                             "در جملهٔ اول موضع بگیر."),
                          bi("Quote or paraphrase one detail: old carriages, or "
                             "four sets of paperwork.",
                             "یک جزئیات را نقل کن: واگن‌های قدیمی یا چهار دسته "
                             "کاغذبازی."),
                          bi("Add something the passage does not say - price, "
                             "family travel, your own country.",
                             "چیزی اضافه کن که در متن نیست؛ قیمت، سفر خانوادگی یا "
                             "کشور خودت.")],
                 "model": bi("I partly agree. The demand is real: the passage says "
                             "the best cabins sell out weeks in advance, and that "
                             "is a market, not a fashion. But old carriages and "
                             "four sets of paperwork across four borders are not "
                             "small costs. In my country the same route is cheap "
                             "to fly, so until night trains are cheaper than "
                             "planes, they will stay a choice for people with time.",
                             "تا حدی موافقم. تقاضا واقعی است: متن می‌گوید بهترین "
                             "کابین‌ها هفته‌ها قبل تمام می‌شوند و این یک بازار "
                             "است، نه مد. اما واگن‌های قدیمی و کاغذبازی چهار "
                             "کشور هزینهٔ کمی نیست. در کشور من پرواز در همان مسیر "
                             "ارزان است، پس تا وقتی قطار شبانه از هواپیما ارزان‌تر "
                             "نشود، انتخابی برای کسانی می‌ماند که وقت دارند.")},
            ],
        },
    },
    # ---------------------------------------------------------------- 2 -----
    {
        "id": "scan",
        "icon": "🔎",
        "level": "B1",
        "title": bi("Scan for a detail", "جزئیات را پیدا کن"),
        "blurb": bi(
            "Move your eyes over the page looking for one thing: a name, a "
            "number, a date.",
            "چشمت را روی صفحه بگردان و فقط یک چیز را بجوی: یک نام، یک عدد، یک تاریخ."),
        "what": bi(
            "Scanning is the opposite of skimming: you already know what you "
            "need, and you are not reading sentences at all. You hold the target "
            "in your mind - 'the year the first library opened' - and let your "
            "eye jump down the page in a zigzag until it catches it. Numbers, "
            "capital letters and quotation marks are the landmarks that make "
            "this fast.",
            "اسکن کردن نقطهٔ مقابل سُرمه‌کشی است: می‌دانی چه می‌خواهی و اصلاً "
            "جمله نمی‌خوانی. هدف را در ذهن نگه می‌داری — «سال افتتاح اولین "
            "کتابخانه» — و چشم را زیگزاگ روی صفحه پایین می‌بری تا به آن برسد. "
            "عددها، حروف بزرگ و علامت‌های نقل‌قول نشانه‌هایی‌اند که این کار را "
            "سریع می‌کنند."),
        "why": bi(
            "In an exam, or on a website, you rarely need the whole text; you need "
            "one fact in it. Reading everything first is how a two-minute task "
            "turns into ten minutes, and how you answer a question from memory "
            "instead of from the page.",
            "در امتحان یا در یک سایت، به‌ندرت کل متن را لازم داری؛ یک نکته در آن "
            "لازم داری. خواندنِ همه‌چیز از اول، کاری دو دقیقه‌ای را ده دقیقه‌ای "
            "می‌کند و باعث می‌شود جواب را از حافظه بدهی، نه از متن."),
        "steps": [
            bi("Read the question and underline the exact words you are hunting "
               "for: usually a name, a number or a date.",
               "سؤال را بخوان و دقیقاً همان کلمه‌ای را که می‌جویی خط بکش؛ "
               "معمولاً یک نام، یک عدد یا یک تاریخ است."),
            bi("Sweep the page in a zigzag, not line by line, and stop only "
               "when a shape matches: 4 followed by million, a capital letter.",
               "صفحه را زیگزاگ بگرد، نه خط‌به‌خط، و فقط وقتی متوقف شو که شکلی "
               "با آنچه می‌خواهی جور باشد: ۴ و بعد واژهٔ میلیون، یا یک حرف بزرگ."),
            bi("When you land on it, read that whole sentence - the answer "
               "usually needs one word on either side.",
               "وقتی به آن رسیدی، تمام آن جمله را بخوان؛ جواب معمولاً یک کلمه "
               "قبل یا بعد از آن را هم لازم دارد."),
            bi("Check the question again: a wrong year that looks right is the "
               "commonest scanning mistake.",
               "دوباره سؤال را ببین؛ سالی که درست به نظر می‌رسد ولی غلط است، "
               "رایج‌ترین خطای اسکن کردن است."),
        ],
        "reading": {
            "title": bi("The libraries that changed a city",
                         "کتابخانه‌هایی که یک شهر را عوض کردند"),
            "level": "B1",
            "paragraphs": [
                "Forty years ago the central library of Medellín had 12,000 books "
                "and one reading room. Today it holds 620,000 books across nine "
                "buildings, and its evening classes have a waiting list.",
                "The change began in 2004, when the city decided that its five "
                "poorest neighbourhoods would each get a library before they got "
                "a new road. The first one, in Santo Domingo, opened in 2007 on a "
                "hilltop reached by two outdoor escalators. It was designed by the "
                "architect Giancarlo Mazzanti and cost four million dollars, a sum "
                "that critics said should have been spent on housing.",
                "Fifteen years later the numbers are hard to argue with. Visits to "
                "the Santo Domingo library rose from 300 a week to more than 4,000. "
                "In the same period reported thefts in the neighbourhood fell by "
                "half, and the share of teenagers who said they had never read a "
                "book for pleasure dropped from 61 per cent to 22 per cent. The "
                "libraries now run 1,100 free computer courses a year.",
                "Not every promise was kept. Two of the five buildings were "
                "delayed by years and one was never built. But the city's head "
                "librarian, María Restrepo, says the lesson is simple: 'A library "
                "is not a building with books. It is a place where a neighbourhood "
                "decides what it wants to become.'",
            ],
            "summary": bi(
                "Medellín moved its library budget to its poorest neighbourhoods: "
                "five library buildings were promised, three were finished. Visits, "
                "reading and computer courses rose sharply, and crime in the area "
                "halved.",
                "مدیین بودجهٔ کتابخانه‌اش را به فقیرترین محله‌ها برد: پنج ساختمان "
                "وعده داده شد و سه‌تا ساخته شد. رفت‌وآمد، کتاب‌خواندن و دوره‌های "
                "کامپیوتر به‌شدت بالا رفت و جرم در آن محله نصف شد."),
        },
        "questions": {
            "blanks": [
                {"sentence": "Today the central library holds ___ books.",
                 "answer": "620,000",
                 "hint": bi("A number with a comma.", "یک عدد با ویرگول.")},
                {"sentence": "The first new library opened in ___.",
                 "answer": "2007",
                 "hint": bi("Three years after the decision.",
                            "سه سال بعد از آن تصمیم.")},
                {"sentence": "Critics said the four million dollars should have "
                             "been spent on ___.",
                 "answer": "housing",
                 "hint": bi("Homes for people - end of paragraph 2.",
                            "خانه برای مردم؛ آخر پاراگراف دوم.")},
                {"sentence": "The libraries now run 1,100 free ___ a year.",
                 "answer": "computer courses",
                 "hint": bi("Two words, end of paragraph 3.",
                            "دو کلمه، آخر پاراگراف سوم.")},
            ],
            "mcq": [
                {"q": "When did the city decide to build the libraries?",
                 "options": ["1974", "2004", "2007", "2019"],
                 "answer": 1,
                 "why": bi("'The change began in 2004' - 2007 is when the first "
                           "one opened, which is the trap.",
                           "«تغییر در ۲۰۰۴ شروع شد»؛ ۲۰۰۷ سال افتتاح اولین "
                           "کتابخانه است و همان دام سؤال است.")},
                {"q": "How many libraries were planned?",
                 "options": ["Two", "Three", "Five", "Nine"],
                 "answer": 2,
                 "why": bi("Five were planned; two were late and one was never "
                           "built, so three stand.",
                           "پنج‌تا برنامه‌ریزی شد؛ دوتا دیر شد و یکی ساخته نشد، پس "
                           "سه‌تا ساخته شد.")},
                {"q": "Weekly visits to the Santo Domingo library rose to",
                 "options": ["300", "1,100", "more than 4,000", "620,000"],
                 "answer": 2,
                 "why": bi("300 was the figure before; 1,100 is the number of "
                           "courses, not visits.",
                           "۳۰۰ عدد قبلی بود؛ ۱۱۰۰ تعداد دوره‌هاست، نه بازدیدها.")},
                {"q": "According to María Restrepo, a library is",
                 "options": ["a building full of books",
                             "a place where a neighbourhood decides its future",
                             "a cheap alternative to a road",
                             "a centre for computer courses"],
                 "answer": 1,
                 "why": bi("Her quotation is the last sentence of the passage.",
                           "نقل‌قول او جملهٔ آخر متن است.")},
            ],
            "truefalse": [
                {"statement": "All five libraries were built.",
                 "answer": False,
                 "why": bi("One 'was never built' and two were delayed.",
                           "یکی «هرگز ساخته نشد» و دوتا دیر شد.")},
                {"statement": "The Santo Domingo library is reached by outdoor "
                              "escalators.",
                 "answer": True,
                 "why": bi("'on a hilltop reached by two outdoor escalators.'",
                           "«روی تپه‌ای که با دو پله‌برقی روباز به آن می‌رسند.»")},
                {"statement": "Reported thefts in the neighbourhood fell by half.",
                 "answer": True,
                 "why": bi("Stated in paragraph 3.", "در پاراگراف سوم گفته شده است.")},
                {"statement": "The first library was built before 2004.",
                 "answer": False,
                 "why": bi("The decision came in 2004 and the building in 2007.",
                           "تصمیم در ۲۰۰۴ بود و ساختمان در ۲۰۰۷.")},
            ],
            "essay": [
                {"prompt": bi("Scan the passage and list three numbers that show "
                              "the change. Then say in one sentence which number "
                              "you find most convincing, and why.",
                              "متن را اسکن کن و سه عدد را که تغییر را نشان می‌دهند "
                              "بنویس. بعد در یک جمله بگو کدام عدد برایت "
                              "قانع‌کننده‌تر است و چرا."),
                 "tips": [bi("Numbers only at first - no sentences needed.",
                             "اول فقط عددها؛ لازم نیست جمله بنویسی."),
                          bi("Then one sentence with 'because'.",
                             "بعد یک جمله با «because»."),
                          bi("A change in behaviour (visits, reading) usually "
                             "convinces more than money spent.",
                             "تغییر در رفتار (بازدید، کتاب‌خواندن) معمولاً از پولِ "
                             "خرج‌شده قانع‌کننده‌تر است.")],
                 "model": bi("Three numbers: 12,000 books became 620,000; visits "
                             "rose from 300 a week to more than 4,000; and the "
                             "share of teenagers who never read for pleasure fell "
                             "from 61 to 22 per cent. The last one convinces me "
                             "most, because it describes a habit changing, not a "
                             "building opening.",
                             "سه عدد: ۱۲٬۰۰۰ کتاب به ۶۲۰٬۰۰۰ رسید؛ بازدید هفتگی از "
                             "۳۰۰ به بیش از ۴٬۰۰۰ رسید؛ و سهم نوجوانانی که هرگز "
                             "برای لذت نمی‌خواندند از ۶۱ به ۲۲ درصد رسید. عدد آخر "
                             "بیشتر قانعم می‌کند، چون از عوض شدن یک عادت حرف "
                             "می‌زند، نه از باز شدن یک ساختمان.")},
                {"prompt": bi("The city spent four million dollars on a library "
                              "instead of housing. In your view, was that the "
                              "right choice? Write 60-80 words.",
                              "شهر چهار میلیون دلار را به‌جای مسکن به کتابخانه داد. "
                              "به نظر تو این انتخاب درستی بود؟ ۶۰ تا ۸۰ کلمه "
                              "بنویس."),
                 "tips": [bi("Give a clear position in sentence one.",
                             "در جملهٔ اول موضع روشن بده."),
                          bi("Use the passage once and your own experience once.",
                             "یک بار از متن استفاده کن و یک بار از تجربهٔ خودت."),
                          bi("End with a condition: 'if the library is used...'",
                             "با یک شرط تمام کن: «اگر کتابخانه استفاده شود…»")],
                 "model": bi("I think it was the right choice, but only because "
                             "the money bought something people use. The passage "
                             "shows visits rising from 300 a week to over 4,000, "
                             "and crime falling by half in the same streets. "
                             "Housing would have helped too, and four million "
                             "dollars is not a small sum. Still, a library that is "
                             "open every day changes what children in a poor "
                             "neighbourhood can imagine for themselves.",
                             "فکر می‌کنم انتخاب درستی بود، اما فقط چون پول صرف چیزی "
                             "شد که مردم استفاده می‌کنند. متن نشان می‌دهد بازدید "
                             "از ۳۰۰ در هفته به بیش از ۴٬۰۰۰ رسید و جرم در همان "
                             "خیابان‌ها نصف شد. مسکن هم کمک می‌کرد و چهار میلیون "
                             "دلار مبلغ کمی نیست. با این حال، کتابخانه‌ای که هر روز "
                             "باز است، تصویری که بچه‌های یک محلهٔ فقیر از آیندهٔ "
                             "خود دارند را عوض می‌کند.")},
            ],
        },
    },
    # ---------------------------------------------------------------- 3 -----
    {
        "id": "context",
        "icon": "🧩",
        "level": "B2",
        "title": bi("Guess a word from its context",
                    "معنی واژه را از بافت حدس بزن"),
        "blurb": bi(
            "Stop at an unknown word, look at the words around it, and carry "
            "on without a dictionary.",
            "روی واژهٔ ناشناس توقف کن، کلمه‌های اطرافش را ببین و بدون فرهنگ "
            "لغت ادامه بده."),
        "what": bi(
            "Context clues are the words a writer puts next to a hard word so "
            "you can work out what it means: a definition, an example, an "
            "opposite, or a cause and its result. Three of these cover most "
            "cases. You do not need the Persian translation; you need enough "
            "meaning to keep reading, and then a guess you can check when the "
            "word comes back.",
            "نشانه‌های بافت همان کلمه‌هایی هستند که نویسنده کنار واژهٔ دشوار "
            "می‌گذارد تا معنی‌اش را بفهمی: یک تعریف، یک مثال، یک متضاد، یا یک "
            "علت و نتیجه. تقریباً همهٔ موارد با همین سه‌تا حل می‌شود. تو به "
            "ترجمهٔ فارسی نیاز نداری؛ به اندازه‌ای معنی نیاز داری که خواندن را "
            "ادامه بدهی و بعد وقتی واژه دوباره آمد، حدست را بسنجی."),
        "why": bi(
            "Stopping at every unknown word is what makes reading in English "
            "exhausting: ten stops on a page and you have lost the argument and "
            "your patience. A context guess costs ten seconds, keeps the meaning "
            "in motion, and is usually right - and when it is wrong, the text "
            "corrects you a line later.",
            "توقف روی هر واژهٔ ناشناس همان چیزی است که خواندن انگلیسی را "
            "خسته‌کننده می‌کند: ده توقف در یک صفحه و هم رشتهٔ مطلب و هم حوصله‌ات "
            "از دست می‌رود. حدس زدن از بافت ده ثانیه وقت می‌گیرد، معنی را در "
            "جریان نگه می‌دارد و معمولاً هم درست است؛ و اگر غلط باشد، متن یک "
            "خط بعد خودش تصحیحش می‌کند."),
        "steps": [
            bi("Read to the end of the sentence first. Half of all context "
               "clues sit after the word, not before it.",
               "اول تا آخر جمله بخوان. نصف نشانه‌های بافت بعد از واژه می‌آیند، "
               "نه قبل از آن."),
            bi("Look for one of four signals: a definition after a dash or "
               "'that is', an example after 'such as', an opposite after 'but', "
               "or a result after 'so'.",
               "دنبال یکی از چهار نشانه بگرد: تعریف بعد از خط تیره یا «that is»، "
               "مثال بعد از «such as»، متضاد بعد از «but»، یا نتیجه بعد از «so»."),
            bi("Replace the word with your guess and read the sentence again. If "
               "it still makes sense, keep going; do not stop to be sure.",
               "واژه را با حدست عوض کن و جمله را دوباره بخوان. اگر هنوز معنی "
               "می‌دهد، ادامه بده و برای مطمئن شدن توقف نکن."),
            bi("Only look the word up if it comes back a third time or if the "
               "whole paragraph now makes no sense.",
               "فقط اگر واژه برای بار سوم برگشت یا کل پاراگراف بی‌معنی شد، "
               "معنی‌اش را نگاه کن."),
        ],
        "reading": {
            "title": bi("The repair café", "کافهٔ تعمیر"),
            "level": "B2",
            "paragraphs": [
                "The first repair café opened in Amsterdam in 2009. Neighbours "
                "bring broken toasters, lamps, bicycles and radios to a community "
                "hall, where volunteers with toolboxes try to fix them for free. "
                "The idea was a response to a throwaway culture: goods are cheap, "
                "so they are replaced rather than mended, and the skills needed to "
                "mend them are dwindling. In many families nobody under forty has "
                "ever opened the back of a radio.",
                "A repair café works because it is social before it is technical. "
                "You sit next to the person repairing your machine, you watch, and "
                "you learn. Volunteers salvage what they can from devices that "
                "cannot be saved - a switch here, a cable there - and those parts "
                "go into a shared box. Nothing is thrown away while it might still "
                "be useful, which is the whole point.",
                "Critics say the movement is sentimental: a toaster costs less than "
                "the bus fare to the café. That misses the arithmetic. The café "
                "saves the price of the machine, but it also saves the trip to the "
                "shop, the wait for delivery and, above all, the habit of not "
                "bothering. The movement has thrived: there are now more than "
                "2,500 repair cafés worldwide, and some manufacturers send their "
                "own engineers to learn what breaks first.",
            ],
            "summary": bi(
                "Repair cafés are free community workshops where volunteers fix "
                "broken things and teach the owner how. They exist because goods "
                "are thrown away too easily and mending skills are disappearing. "
                "Over 2,500 now operate, and manufacturers are paying attention.",
                "کافه‌های تعمیر کارگاه‌های رایگان محلی‌اند که داوطلبان در آن‌ها "
                "چیزهای خراب را تعمیر می‌کنند و به صاحبشان یاد می‌دهند. دلیلشان "
                "این است که کالاها زیاد دور ریخته می‌شوند و مهارت تعمیر از بین "
                "می‌رود. بیش از ۲٬۵۰۰ کافه فعال است و سازندگان هم توجه "
                "می‌کنند."),
            "note": bi(
                "Four words in this passage are deliberately above B1: "
                "dwindling, salvage, sentimental, thrived.",
                "چهار واژه در این متن عمداً بالاتر از سطح B1 هستند: dwindling، "
                "salvage، sentimental، thrived."),
        },
        "questions": {
            "blanks": [
                {"sentence": "Goods are replaced rather than mended, and the "
                             "skills needed to mend them are ___.",
                 "answer": "dwindling",
                 "hint": bi("The sentence before it says nobody under forty has "
                            "ever opened a radio - the skills are going away.",
                            "جملهٔ قبل می‌گوید هیچ‌کس زیر چهل سال تابه‌حال پشت "
                            "رادیویی را باز نکرده؛ یعنی مهارت‌ها از بین می‌روند.")},
                {"sentence": "Volunteers ___ what they can from devices that "
                             "cannot be saved.",
                 "answer": "salvage",
                 "hint": bi("They keep a switch and a cable out of a broken "
                            "machine.",
                            "از دستگاه خراب یک کلید و یک کابل برمی‌دارند و "
                            "نگه می‌دارند.")},
                {"sentence": "Critics say the movement is ___: a toaster costs "
                             "less than the bus fare.",
                 "answer": "sentimental",
                 "hint": bi("Emotional rather than practical - that is what "
                            "the critics mean.",
                            "احساسی و نه عملی؛ منظور منتقدان همین است.")},
                {"sentence": "The movement has ___: there are now more than "
                             "2,500 repair cafés.",
                 "answer": "thrived",
                 "hint": bi("Followed by a number that keeps growing.",
                            "بعد از آن عددی می‌آید که مدام بزرگ‌تر می‌شود.")},
            ],
            "mcq": [
                {"q": "'Dwindling' most nearly means",
                 "options": ["growing quickly", "becoming fewer",
                             "being taught", "becoming cheaper"],
                 "answer": 1,
                 "why": bi("The next sentence proves it: nobody under forty "
                           "has the skill any more.",
                           "جملهٔ بعد اثباتش می‌کند: هیچ‌کس زیر چهل سال دیگر "
                           "این مهارت را ندارد.")},
                {"q": "'Salvage' most nearly means",
                 "options": ["throw away", "sell", "keep the useful parts",
                             "buy new"],
                 "answer": 2,
                 "why": bi("The dash after it explains: 'a switch here, a cable "
                           "there'.",
                           "خط تیرهٔ بعد از آن توضیح می‌دهد: «یک کلید اینجا، یک "
                           "کابل آنجا».")},
                {"q": "'Thrived' most nearly means",
                 "options": ["grown strong", "closed down", "become expensive",
                             "stayed the same"],
                 "answer": 0,
                 "why": bi("The figure after it - more than 2,500 cafés - is the "
                           "evidence of growth.",
                           "عدد بعد از آن — بیش از ۲٬۵۰۰ کافه — شاهد رشد است.")},
                {"q": "What does 'that misses the arithmetic' mean in paragraph 3?",
                 "options": ["The critics cannot count",
                             "The critics are forgetting some of the costs",
                             "The café charges too much",
                             "Toasters are getting more expensive"],
                 "answer": 1,
                 "why": bi("The writer then lists the costs the critics left "
                           "out: the trip, the wait, the habit.",
                           "نویسنده بعد هزینه‌هایی را می‌آورد که منتقدان حساب "
                           "نکرده‌اند: سفر، انتظار، و عادت.")},
            ],
            "truefalse": [
                {"statement": "Repair cafés charge a small fee for the repair.",
                 "answer": False,
                 "why": bi("'try to fix them for free.'", "«رایگان تعمیر می‌کنند.»")},
                {"statement": "The writer thinks saving money is the least "
                              "important saving.",
                 "answer": True,
                 "why": bi("'above all, the habit of not bothering' puts money "
                           "last in the list.",
                           "عبارت «و مهم‌تر از همه، عادت به زحمت ندادن خود» پول را "
                           "آخر فهرست می‌گذارد.")},
                {"statement": "Some manufacturers now study what breaks first.",
                 "answer": True,
                 "why": bi("The last sentence says so.", "جملهٔ آخر همین را می‌گوید.")},
                {"statement": "The first repair café opened in 2019.",
                 "answer": False,
                 "why": bi("2009, not 2019 - a scanning slip anyone can make.",
                           "۲۰۰۹ است نه ۲۰۱۹؛ اشتباهی که برای هر کسی پیش می‌آید.")},
            ],
            "essay": [
                {"prompt": bi("Explain in your own words what a 'throwaway "
                              "culture' is, using the passage and one example "
                              "from your own life. 60-80 words.",
                              "با کلمات خودت توضیح بده «فرهنگ دورریز» چیست؛ از متن "
                              "و یک مثال از زندگی خودت استفاده کن. ۶۰ تا ۸۰ کلمه."),
                 "tips": [bi("Define it in one sentence, without the word "
                             "'culture' twice.",
                             "در یک جمله تعریفش کن، بدون اینکه دو بار واژهٔ "
                             "«فرهنگ» را بیاوری."),
                          bi("Then give your example - a phone, a charger, a kettle.",
                             "بعد مثال خودت را بده: گوشی، شارژر، کتری."),
                          bi("End with what the repair café changes about it.",
                             "آخرش بگو کافهٔ تعمیر چه چیزی را در آن عوض می‌کند.")],
                 "model": bi("A throwaway culture is one in which things are "
                             "cheap enough to replace and too complicated to "
                             "repair, so nobody tries. My mother's kettle broke "
                             "last year: the shop had a new one for less than the "
                             "fare to a repair shop, so it went in the bin. A "
                             "repair café interrupts that habit twice - it fixes "
                             "the thing, and it teaches you that fixing is "
                             "something people do.",
                             "فرهنگ دورریز فرهنگی است که در آن چیزها آن‌قدر ارزان‌اند "
                             "که عوض شوند و آن‌قدر پیچیده که تعمیر نشوند، پس کسی "
                             "تلاش نمی‌کند. کتری مادرم سال پیش خراب شد: مغازه یکی "
                             "تازه داشت که از کرایهٔ رفتن به تعمیرگاه کمتر بود، پس "
                             "رفت در سطل. کافهٔ تعمیر این عادت را دو بار می‌شکند: "
                             "چیز را درست می‌کند و یادت می‌دهد که تعمیر کردن کاری "
                             "است که آدم‌ها انجام می‌دهند.")},
                {"prompt": bi("The writer says critics 'miss the arithmetic'. "
                              "Write two or three sentences agreeing or "
                              "disagreeing, and use one number from the passage.",
                              "نویسنده می‌گوید منتقدان «حساب را اشتباه می‌کنند». دو "
                              "یا سه جمله بنویس که موافق یا مخالف باشی و یک عدد از "
                              "متن را به کار ببری."),
                 "tips": [bi("Name the number: 2,500 cafés, 2009.",
                             "عدد را نام ببر: ۲٬۵۰۰ کافه، ۲۰۰۹."),
                          bi("Say what the number proves, not just that it exists.",
                             "بگو آن عدد چه چیزی را ثابت می‌کند، نه فقط اینکه وجود دارد."),
                          bi("One concession makes an argument stronger.",
                             "یک پذیرشِ کوچک، استدلال را قوی‌تر می‌کند.")],
                 "model": bi("The critics are counting only money, and the writer "
                             "is right that this is the wrong sum. More than 2,500 "
                             "cafés exist because people keep coming, and nobody "
                             "queues on a Saturday morning for something they "
                             "could buy. That said, the bus fare argument is not "
                             "silly: for a cheap kettle, the café is a hobby, not "
                             "an economy.",
                             "منتقدان فقط پول را می‌شمارند و نویسنده درست می‌گوید که "
                             "این جمعِ اشتباهی است. بیش از ۲٬۵۰۰ کافه وجود دارد چون "
                             "مردم همچنان می‌آیند و کسی صبح شنبه برای چیزی که "
                             "می‌تواند بخرد صف نمی‌بندد. با این حال، حرف کرایهٔ "
                             "اتوبوس بی‌معنی نیست: برای یک کتری ارزان، کافه یک "
                             "سرگرمی است، نه صرفه‌جویی.")},
            ],
        },
    },
    # ---------------------------------------------------------------- 4 -----
    {
        "id": "reference",
        "icon": "🔗",
        "level": "B2",
        "title": bi("Follow the reference words", "واژه‌های ارجاعی را دنبال کن"),
        "blurb": bi(
            "It, this, they, those - every one of them points back at something. "
            "Find it or lose the sentence.",
            "it، this، they، those — هر کدام به چیزی برمی‌گردند. پیدایش کن، "
            "وگرنه جمله را از دست می‌دهی."),
        "what": bi(
            "English hates repeating a noun, so it replaces it: 'the programme' "
            "becomes 'it', 'the cities that copied it' becomes 'those', a whole "
            "clause becomes 'this'. These words are what holds a paragraph "
            "together, and they are where comprehension quietly breaks: you read "
            "a correct sentence and understand the wrong thing, because you "
            "attached 'it' to the nearest noun instead of the right one.",
            "انگلیسی از تکرار اسم خوشش نمی‌آید، پس جایش می‌گذارد: «the programme» "
            "می‌شود it، «شهرهایی که از آن کپی کردند» می‌شود those، و یک بند کامل "
            "می‌شود this. همین واژه‌ها پاراگراف را به هم می‌چسبانند و دقیقاً همان "
            "جایی هستند که فهم بی‌صدا می‌شکند: جملهٔ درست را می‌خوانی و چیز "
            "اشتباهی می‌فهمی، چون it را به نزدیک‌ترین اسم چسبانده‌ای، نه به اسم "
            "درست."),
        "why": bi(
            "A pronoun is a promise that the writer has already told you what it "
            "means. When a paragraph stops making sense, the answer is almost "
            "never vocabulary - it is one 'it' pointing at the wrong thing. "
            "Naming the referent out loud, in your own words, is the fastest "
            "repair there is.",
            "ضمیر یعنی نویسنده قبلاً گفته چه چیزی را می‌گوید. وقتی یک پاراگراف "
            "بی‌معنی می‌شود، جواب تقریباً هیچ‌وقت واژه نیست؛ یک it است که به چیز "
            "اشتباهی اشاره می‌کند. بلند گفتنِ مرجع با کلمات خودت، سریع‌ترین "
            "تعمیر ممکن است."),
        "steps": [
            bi("Circle every pronoun in the paragraph: it, this, they, them, "
               "those, he, she, which.",
               "همهٔ ضمیرهای پاراگراف را دور بزن: it، this، they، them، those، "
               "he، she، which."),
            bi("Say the noun out loud in place of the pronoun. 'It has run for "
               "fifty years' -> 'the Sunday road closure has run for fifty years.'",
               "جای ضمیر، اسم را بلند بگو. «it پنجاه سال ادامه داشته» ← «بستن "
               "خیابان در یکشنبه‌ها پنجاه سال ادامه داشته»."),
            bi("If two nouns could fit, choose by meaning, not by distance: "
               "'this' usually means the whole previous sentence, not its last word.",
               "اگر دو اسم جور درمی‌آید، با معنی انتخاب کن نه با فاصله: this "
               "معمولاً یعنی کل جملهٔ قبل، نه آخرین کلمهٔ آن."),
            bi("Check the sentence with your noun inside. If it now says "
               "something true about the passage, you have the right referent.",
               "جمله را با اسمِ خودت بسنج. اگر حالا چیزی درست دربارهٔ متن می‌گوید، "
               "مرجع را درست پیدا کرده‌ای."),
        ],
        "reading": {
            "title": bi("One day a week without cars",
                         "یک روز در هفته بدون ماشین"),
            "level": "B2",
            "paragraphs": [
                "Bogotá closes 120 kilometres of roads to cars every Sunday. The "
                "programme, called Ciclovía, began in 1974, when a group of "
                "cyclists rode through the city centre to protest about air "
                "pollution. The police tried to stop them; the mayor, instead, "
                "asked whether the roads could be closed once a week. Few people "
                "expected it to last. It has now run for fifty years, and on a "
                "sunny Sunday more than a million people use it - cyclists, "
                "runners, families with prams, and vendors who sell mangoes and "
                "coffee from carts they push along the route.",
                "Cities from Los Angeles to Jakarta have copied the idea. Most "
                "found that the hardest part was not closing the roads but keeping "
                "them closed: a single complaint from a shop owner, or a change of "
                "government, can end a programme that took years to build. Those "
                "that survived share one habit. They measure who uses the space, "
                "they publish the numbers, and they let residents see what a "
                "street looks like when it belongs to people rather than engines.",
            ],
            "summary": bi(
                "Bogotá has closed 120 km of roads to cars every Sunday since "
                "1974. Other cities copied the idea, and most discovered that "
                "keeping the roads closed was harder than closing them; the ones "
                "that lasted measured and published who used the space.",
                "بوگوتا از ۱۹۷۴ هر یکشنبه ۱۲۰ کیلومتر جاده را به روی ماشین‌ها "
                "می‌بندد. شهرهای دیگر از این ایده کپی کردند و بیشترشان فهمیدند "
                "بسته نگه داشتن جاده‌ها از بستنشان سخت‌تر است؛ آن‌هایی که ماندند، "
                "اندازه گرفتند و منتشر کردند که چه کسی از فضا استفاده می‌کند."),
        },
        "questions": {
            "blanks": [
                {"sentence": "Few people expected ___ to last. (the programme)",
                 "answer": "it",
                 "hint": bi("One word - the programme again.",
                            "یک کلمه؛ همان برنامه.")},
                {"sentence": "Cities from Los Angeles to Jakarta have copied ___.",
                 "answer": "the idea",
                 "hint": bi("Two words: what exactly did they copy?",
                            "دو کلمه: دقیقاً چه چیزی را کپی کردند؟")},
                {"sentence": "Most found that the hardest part was ___ the roads.",
                 "answer": "keeping",
                 "hint": bi("Not closing them - ___ them closed.",
                            "نه بستن؛ ___ آن‌ها بسته.")},
                {"sentence": "___ that survived share one habit.",
                 "answer": "Those",
                 "hint": bi("Refers back to the cities; four letters.",
                            "به شهرها برمی‌گردد؛ چهار حرف.")},
            ],
            "mcq": [
                {"q": "In 'Few people expected it to last', 'it' means",
                 "options": ["the city centre", "the protest",
                             "the Sunday road closure", "the traffic"],
                 "answer": 2,
                 "why": bi("The nearest sensible referent is the mayor's idea of "
                           "closing the roads once a week, not the protest.",
                           "مرجع منطقی، ایدهٔ شهردار برای بستن هفتگی جاده‌ها است، "
                           "نه اعتراض.")},
                {"q": "'Those that survived share one habit' - 'those' are",
                 "options": ["the roads", "the cities that copied the idea",
                             "the residents", "the governments"],
                 "answer": 1,
                 "why": bi("'Those' stands for 'cities ... most found'.",
                           "«Those» جانشین «cities» در جملهٔ قبل است.")},
                {"q": "In the last sentence, 'they' is repeated three times. "
                      "Who are 'they'?",
                 "options": ["residents", "the cities that survived",
                             "cyclists", "vendors"],
                 "answer": 1,
                 "why": bi("The sentence continues the subject of the one before "
                           "it: those cities.",
                           "جمله همان فاعل جملهٔ قبل را ادامه می‌دهد: همان شهرها.")},
                {"q": "'what a street looks like when it belongs to people rather "
                      "than engines' - 'them' in 'keeping them closed' refers to",
                 "options": ["the residents", "the roads", "the shops", "people"],
                 "answer": 1,
                 "why": bi("'Closing the roads ... keeping them closed' - the same "
                           "plural noun.",
                           "«بستن جاده‌ها … بسته نگه داشتن آن‌ها»؛ همان اسم جمع.")},
            ],
            "truefalse": [
                {"statement": "Ciclovía began as a protest about air pollution.",
                 "answer": True,
                 "why": bi("The cyclists rode 'to protest about air pollution'.",
                           "دوچرخه‌سواران «برای اعتراض به آلودگی هوا» رکاب زدند.")},
                {"statement": "Most copycat cities found closing the roads harder "
                              "than keeping them closed.",
                 "answer": False,
                 "why": bi("The passage says the opposite order.",
                           "متن ترتیب برعکس را می‌گوید.")},
                {"statement": "The successful cities published data about who uses "
                              "the space.",
                 "answer": True,
                 "why": bi("'they publish the numbers.'", "«عددها را منتشر می‌کنند.»")},
                {"statement": "Vendors sell from shops along the route.",
                 "answer": False,
                 "why": bi("From carts 'they push along the route'.",
                           "از گاری‌هایی که «در مسیر هل می‌دهند».")},
            ],
            "essay": [
                {"prompt": bi("In one paragraph, describe how the second paragraph "
                              "is tied together by reference words. Name at least "
                              "three of them and what each points to.",
                              "در یک پاراگراف توضیح بده پاراگراف دوم با واژه‌های ارجاعی "
                              "چگونه به هم بسته شده است. دست‌کم سه واژه و مرجع هر "
                              "کدام را نام ببر."),
                 "tips": [bi("Start with 'the idea' and work forwards.",
                             "از «the idea» شروع کن و جلو برو."),
                          bi("Quote the pronoun, then write its noun in brackets.",
                             "ضمیر را نقل کن و بعد اسمش را در پرانتز بنویس."),
                          bi("Say what the chain achieves: it avoids repeating "
                             "'cities', and it keeps the subject moving.",
                             "بگو این زنجیره چه می‌کند: از تکرار «شهرها» جلوگیری "
                             "می‌کند و فاعل را به حرکت ادامه می‌دهد.")],
                 "model": bi("The paragraph opens with 'the idea', which points "
                             "back to Ciclovía, the Sunday closure of 120 "
                             "kilometres of road. 'Them' in 'keeping them closed' "
                             "means the roads. 'Those that survived' replaces the "
                             "copying cities, and the three 'they's in the last "
                             "sentence keep the same group as the subject. The "
                             "chain lets the writer move from one city to many "
                             "without ever repeating the noun.",
                             "پاراگراف با «the idea» شروع می‌شود که به Ciclovía "
                             "برمی‌گردد؛ همان بستن ۱۲۰ کیلومتر جاده در "
                             "یکشنبه‌ها. «them» در «keeping them closed» یعنی "
                             "جاده‌ها. «Those that survived» جانشین شهرهایی است که "
                             "کپی کردند، و سه «they» در جملهٔ آخر همان گروه را "
                             "فاعل نگه می‌دارد. این زنجیره اجازه می‌دهد نویسنده "
                             "از یک شهر به شهرهای بسیار برود بدون اینکه اسم را "
                             "تکرار کند.")},
                {"prompt": bi("Would a car-free Sunday work in your city? Answer "
                              "in 60-80 words and refer back to the passage at "
                              "least once using a reference word ('this', 'that "
                              "habit').",
                              "آیا یکشنبهٔ بدون ماشین در شهر تو جواب می‌دهد؟ در ۶۰ تا "
                              "۸۰ کلمه جواب بده و دست‌کم یک بار با یک واژهٔ ارجاعی "
                              "(this یا that habit) به متن برگرد."),
                 "tips": [bi("Use 'this' to point at the whole previous sentence, "
                             "not at one noun.",
                             "از this برای اشاره به کل جملهٔ قبل استفاده کن، نه یک "
                             "اسم."),
                          bi("Give one local detail: a street, a season.",
                             "یک جزئیات محلی بده: یک خیابان، یک فصل."),
                          bi("Say what would have to be measured.",
                             "بگو چه چیزی باید اندازه گرفته شود.")],
                 "model": bi("It could work, but only on a smaller scale. In my "
                             "city the main road is the only way to the hospital, "
                             "so closing it would be dangerous - this is exactly "
                             "the objection that ended several programmes in the "
                             "passage. A better start is one street, on Friday "
                             "mornings in summer. That habit, as the writer says, "
                             "has to be measured and published, or nobody will "
                             "believe it helped.",
                             "می‌تواند جواب بدهد، اما فقط در مقیاس کوچک‌تر. در شهر "
                             "من جادهٔ اصلی تنها راه رسیدن به بیمارستان است، پس "
                             "بستنش خطرناک می‌شود؛ این دقیقاً همان اعتراضی است که "
                             "در متن چند برنامه را تمام کرد. شروع بهتر، یک خیابان "
                             "است، صبح‌های جمعه در تابستان. همان‌طور که نویسنده "
                             "می‌گوید، این عادت باید اندازه‌گیری و منتشر شود، وگرنه "
                             "هیچ‌کس باور نمی‌کند که فایده داشته است.")},
            ],
        },
    },
    # ---------------------------------------------------------------- 5 -----
    {
        "id": "inference",
        "icon": "💭",
        "level": "B2",
        "title": bi("Read between the lines", "بین خطوط را بخوان"),
        "blurb": bi(
            "The writer does not say it. What do the details let you conclude?",
            "نویسنده صریحاً نمی‌گوید. جزئیات به تو اجازه می‌دهند چه نتیجه‌ای بگیری؟"),
        "what": bi(
            "An inference is a conclusion the text supports but does not state. "
            "Nobody writes 'he was poor' if they can write 'he counted the coins "
            "twice'. Exam questions ask for this constantly - 'what can we "
            "conclude', 'how does the narrator feel', 'what does this suggest' - "
            "and the answer is never a quotation. It is a sentence you write "
            "yourself and then defend with two details from the page.",
            "استنتاج نتیجه‌ای است که متن از آن پشتیبانی می‌کند ولی آن را نمی‌گوید. "
            "کسی نمی‌نویسد «فقیر بود» وقتی می‌تواند بنویسد «سکه‌ها را دو بار "
            "شمرد». سؤال‌های امتحانی مدام همین را می‌خواهند — «چه می‌توان نتیجه "
            "گرفت»، «احساس راوی چیست»، «این چه چیزی را نشان می‌دهد» — و جواب "
            "هیچ‌وقت نقل‌قول نیست. جواب جمله‌ای است که خودت می‌نویسی و با دو "
            "جزئیات از متن از آن دفاع می‌کنی."),
        "why": bi(
            "A correct inference is the only proof that you understood rather "
            "than decoded. It also protects you from the commonest exam trap: an "
            "option that repeats the words of the passage and means nothing.",
            "استنتاجِ درست تنها مدرکی است که نشان می‌دهد فهمیده‌ای، نه اینکه فقط "
            "واژه‌ها را خوانده‌ای. همچنین از رایج‌ترین دام امتحان حفظت می‌کند: "
            "گزینه‌ای که کلمه‌های متن را تکرار می‌کند و هیچ معنایی ندارد."),
        "steps": [
            bi("Answer first, then find the evidence. Reading the options before "
               "you have a view is how wrong answers get chosen.",
               "اول جواب بده، بعد شاهد پیدا کن. خواندن گزینه‌ها پیش از داشتن نظر، "
               "همان راهی است که جواب غلط انتخاب می‌شود."),
            bi("Ask 'what would have to be true for the writer to say this?'",
               "بپرس «چه چیزی باید درست باشد که نویسنده این را بگوید؟»"),
            bi("Find two details that point the same way. One is a guess; two is "
               "an inference.",
               "دو جزئیات پیدا کن که به یک جهت اشاره کنند. یکی حدس است؛ دو تا "
               "استنتاج."),
            bi("Reject any option that is quoted word for word from the passage: "
               "an inference is never a quotation.",
               "هر گزینه‌ای را که عیناً از متن نقل شده رد کن؛ استنتاج هیچ‌وقت "
               "نقل‌قول نیست."),
        ],
        "reading": {
            "title": bi("The last bus", "آخرین اتوبوس"),
            "level": "B2",
            "paragraphs": [
                "The last bus left at 11:40, and I was at the stop at 11:20 with "
                "two bags and a paper cup of tea. A man in a grey coat was already "
                "there, reading a newspaper under the light.",
                "At 11:35 a bus came, stopped and opened its doors. The driver "
                "looked at us, then at the empty street, and shut them again. "
                "'Not this one,' the man said, without looking up. 'This one goes "
                "to the depot.' He turned a page.",
                "I had lived in the city for six years and had never once checked "
                "which bus went where. At 11:41 the last bus arrived, and it was "
                "full. The man folded his newspaper, and I understood that he had "
                "been waiting, patiently, for exactly this bus, and that he had "
                "probably been doing so every night for years.",
            ],
            "summary": bi(
                "A narrator waiting for the last bus is quietly corrected by a "
                "stranger who knows the routes. The narrator, six years in the "
                "city, realises how little attention they have paid to it.",
                "راوی که منتظر آخرین اتوبوس است، بی‌صدا از غریبه‌ای که مسیرها را "
                "می‌شناسد درس می‌گیرد. راوی که شش سال در شهر زندگی کرده، می‌فهمد "
                "چقدر کم به شهرش توجه کرده است."),
        },
        "questions": {
            "blanks": [
                {"sentence": "The last bus left at ___.",
                 "answer": "11:40",
                 "hint": bi("A time, first line.", "یک ساعت، خط اول.")},
                {"sentence": "A man in a grey coat was reading a ___.",
                 "answer": "newspaper",
                 "hint": bi("He folds it at the end.", "آخر متن آن را تا می‌زند.")},
                {"sentence": "'This one goes to the ___,' the man said.",
                 "answer": "depot",
                 "hint": bi("Where buses go when they stop working.",
                            "جایی که اتوبوس‌ها وقتی کار نمی‌کنند می‌روند.")},
                {"sentence": "At 11:41 the last bus arrived, and it was ___.",
                 "answer": "full",
                 "hint": bi("Opposite of empty.", "متضاد خالی.")},
            ],
            "mcq": [
                {"q": "Why does the narrator mention six years?",
                 "options": ["To show how long the journey takes",
                             "To show how careless they have been in a city they "
                             "know well",
                             "To explain why they were at the stop late",
                             "To suggest they are about to leave the city"],
                 "answer": 1,
                 "why": bi("Six years and 'never once checked' - the contrast is "
                           "the point, and it is never stated.",
                           "شش سال و «حتی یک بار هم نگاه نکرده بودم»؛ همین تضاد "
                           "مقصود است و هیچ‌جا صریح گفته نمی‌شود.")},
                {"q": "What can we infer about the man in the grey coat?",
                 "options": ["He works for the bus company",
                             "He is waiting for someone",
                             "He takes this bus often and knows the routes well",
                             "He is a stranger to the city"],
                 "answer": 2,
                 "why": bi("He knows which bus goes to the depot and waits "
                           "'night after night for years'.",
                           "می‌داند کدام اتوبوس به دپو می‌رود و «هر شب، سال‌ها» "
                           "منتظر همین اتوبوس است.")},
                {"q": "How does the narrator feel at the end?",
                 "options": ["Angry with the driver",
                             "Amused by the man",
                             "A little ashamed of their own inattention",
                             "Afraid of missing the bus"],
                 "answer": 2,
                 "why": bi("The realisation lands on the narrator, not on the man: "
                           "'I understood that...'. Nothing in the text is angry.",
                           "این فهم به خود راوی می‌رسد، نه به آن مرد: «فهمیدم "
                           "که…». در متن هیچ خشمگی نیست.")},
                {"q": "The man's short answer 'Not this one' suggests he is",
                 "options": ["rude and impatient",
                             "helpful but not interested in a conversation",
                             "unsure about the timetable",
                             "trying to keep a seat for himself"],
                 "answer": 1,
                 "why": bi("He gives the information and adds a reason, then "
                           "turns a page - help without chat.",
                           "اطلاعات را می‌دهد و دلیلش را هم می‌گوید، بعد صفحه را "
                           "برمی‌گرداند؛ کمک بدون گفتگو.")},
            ],
            "truefalse": [
                {"statement": "The narrator checked the timetable before leaving home.",
                 "answer": False,
                 "why": bi("'never once checked which bus went where.'",
                           "«حتی یک بار هم نگاه نکرده بودم کدام اتوبوس کجا "
                           "می‌رود.»")},
                {"statement": "The 11:35 bus was going to the depot.",
                 "answer": True,
                 "why": bi("The man says exactly that.", "آن مرد دقیقاً همین را می‌گوید.")},
                {"statement": "The man offered the narrator a seat.",
                 "answer": False,
                 "why": bi("He only explains which bus to wait for.",
                           "او فقط توضیح می‌دهد که منتظر کدام اتوبوس باشد.")},
                {"statement": "The narrator is a visitor to the city.",
                 "answer": False,
                 "why": bi("'I had lived in the city for six years.'",
                           "«شش سال بود که در این شهر زندگی می‌کردم.»")},
            ],
            "essay": [
                {"prompt": bi("What kind of person is the narrator? Write a short "
                              "paragraph and support it with two details from the "
                              "text.",
                              "راوی چه جور آدمی است؟ یک پاراگراف کوتاه بنویس و با دو "
                              "جزئیات از متن از حرفت دفاع کن."),
                 "tips": [bi("Do not quote the two details; describe them.",
                             "دو جزئیات را نقل نکن؛ توصیفشان کن."),
                          bi("Use 'which suggests', 'this shows' to mark the inference.",
                             "از «which suggests» یا «this shows» استفاده کن تا "
                             "استنتاج معلوم شود."),
                          bi("A character sketch needs a flaw as well as a virtue.",
                             "یک توصیف شخصیت هم عیب می‌خواهد هم حسن.")],
                 "model": bi("The narrator is well-meaning but careless about "
                             "ordinary things. They arrive twenty minutes early and "
                             "hold a cup of tea, which suggests someone organised "
                             "about the journey; but six years in the city and "
                             "never knowing which bus goes where shows a habit of "
                             "letting other people do the noticing. The final "
                             "realisation - understanding the stranger's nightly "
                             "routine only after being helped - suggests a person "
                             "who is honest with themselves once the evidence is "
                             "in front of them.",
                             "راوی خوش‌نیت است ولی به چیزهای معمولی بی‌توجه. بیست "
                             "دقیقه زودتر می‌رسد و چای در دست دارد، که نشان می‌دهد "
                             "در سفر منظم است؛ اما شش سال در شهر زندگی کرده و "
                             "نمی‌داند کدام اتوبوس کجا می‌رود، که نشانهٔ عادت به این "
                             "است که دیگران حواسشان باشد. فهمِ آخر — اینکه تازه "
                             "بعد از کمک، برنامهٔ هرشبِ آن غریبه را می‌فهمد — نشان "
                             "می‌دهد آدمی است که وقتی شاهد جلوی چشمش باشد، با خودش "
                             "صادق است.")},
                {"prompt": bi("The writer never says the man is kind. Write two "
                              "sentences explaining how the reader still knows it.",
                              "نویسنده هیچ‌جا نمی‌گوید آن مرد مهربان است. در دو جمله "
                              "توضیح بده خواننده از کجا این را می‌فهمد."),
                 "tips": [bi("Name the action, not the adjective.",
                             "عمل را نام ببر، نه صفت را."),
                          bi("Explain what the action would mean if it were absent.",
                             "بگو اگر آن عمل نبود چه معنایی داشت.")],
                 "model": bi("The man speaks without being asked, and the "
                             "information saves the narrator an hour in the cold; "
                             "he gives it and then goes back to his newspaper, so "
                             "he is helping without wanting credit. If he had said "
                             "nothing, the narrator would simply have boarded the "
                             "wrong bus, which is why his two words carry the "
                             "kindness of the whole story.",
                             "آن مرد بدون اینکه کسی بپرسد حرف می‌زند و همان اطلاعات "
                             "یک ساعت سرما را از راوی می‌گیرد؛ آن را می‌گوید و "
                             "دوباره به روزنامه‌اش برمی‌گردد، پس کمک می‌کند بدون "
                             "اینکه بخواهد دیده شود. اگر چیزی نمی‌گفت، راوی سوار "
                             "اتوبوس اشتباه می‌شد؛ همین است که آن دو کلمه، مهربانی "
                             "کل داستان را حمل می‌کند.")},
            ],
        },
    },
    # ---------------------------------------------------------------- 6 -----
    {
        "id": "signposts",
        "icon": "🪧",
        "level": "B2",
        "title": bi("Follow the signposts", "نشانه‌های متن را دنبال کن"),
        "blurb": bi(
            "However, yet, for example, consequently - the small words that tell "
            "you what the next sentence is doing.",
            "however، yet، for example، consequently — کلمه‌های کوچکی که می‌گویند "
            "جملهٔ بعد چه کاری می‌کند."),
        "what": bi(
            "Academic and journalistic English is built out of links: a claim, a "
            "contrast, an example, a result, a limitation. The links are short "
            "words and they carry the argument. If you skip them you get a list "
            "of true statements with no idea which one the writer believes, and "
            "you answer 'what is the writer's attitude' wrongly every time.",
            "انگلیسی آکادمیک و روزنامه‌ای از پیوندها ساخته می‌شود: یک ادعا، یک "
            "تضاد، یک مثال، یک نتیجه، یک محدودیت. این پیوندها واژه‌های کوتاهی "
            "هستند و خودِ استدلال را حمل می‌کنند. اگر از آن‌ها بگذری، فهرستی از "
            "جمله‌های درست داری بی‌آنکه بدانی نویسنده کدام را باور دارد، و "
            "سؤال «نگرش نویسنده چیست» را هر بار غلط جواب می‌دهی."),
        "why": bi(
            "These words are the cheapest marks in any reading test. 'However' "
            "tells you the next sentence will disagree with the last one, so you "
            "can predict it before reading it - and prediction is what makes "
            "reading fast enough to finish an exam.",
            "این واژه‌ها ارزان‌ترین امتیازهای هر آزمون خواندن‌اند. «However» "
            "می‌گوید جملهٔ بعد با جملهٔ قبل مخالف است، پس می‌توانی پیش از "
            "خواندنش پیش‌بینی‌اش کنی؛ و پیش‌بینی همان چیزی است که خواندن را "
            "آن‌قدر سریع می‌کند تا امتحان تمام شود."),
        "steps": [
            bi("Underline every linking word in the passage before answering "
               "anything. There are usually five or six.",
               "پیش از پاسخ دادن، همهٔ واژه‌های پیوند را در متن خط بکش. "
               "معمولاً پنج شش‌تا هستند."),
            bi("Write what each one promises: contrast, example, cause, result, "
               "limitation.",
               "کنار هر کدام بنویس چه چیزی وعده می‌دهد: تضاد، مثال، علت، نتیجه، "
               "محدودیت."),
            bi("Before you read the sentence after 'however', predict it. Then "
               "check yourself - being wrong is how the habit forms.",
               "پیش از خواندن جملهٔ بعد از «however» آن را پیش‌بینی کن، بعد "
               "خودت را بسنج؛ اشتباه شدن همان راهی است که این عادت ساخته می‌شود."),
            bi("Use the last paragraph for the writer's own position: it almost "
               "always starts with 'However' or 'Still' or a limitation.",
               "برای فهم موضع خود نویسنده از پاراگراف آخر استفاده کن؛ تقریباً "
               "همیشه با «However» یا «Still» یا یک محدودیت شروع می‌شود."),
        ],
        "reading": {
            "title": bi("What sleep does for memory", "خواب با حافظه چه می‌کند"),
            "level": "B2",
            "paragraphs": [
                "Sleep is not a pause in learning; it is part of it. During deep "
                "sleep the brain replays the day's experiences, running them again "
                "in a compressed form, and it is during that replay that new "
                "connections are strengthened. Students who learn a list of words "
                "in the evening and sleep before testing remember more of it than "
                "students who learn the same list in the morning.",
                "Yet the effect depends on timing. Sleeping immediately after "
                "study helps; sleeping eight hours later, after a day of new "
                "information, helps much less. For example, volunteers who napped "
                "for ninety minutes right after learning a route through a virtual "
                "city could still find their way a week later, while those who "
                "stayed awake lost most of the route within days.",
                "In contrast, sleep cannot rescue material that was never "
                "understood. Rereading a chapter you did not follow and then "
                "sleeping on it produces a confident feeling and very little "
                "recall, a combination that is worse than knowing you do not "
                "know. Consequently, the useful rule is not 'sleep more' but "
                "'understand first, then sleep'.",
                "However, the research has a limit that is rarely mentioned: most "
                "of it was done on young adults in laboratories, with measured "
                "sleep and simple tasks. Whether the same gains appear in a noisy "
                "home, after a night shift, or at sixty is still an open question.",
            ],
            "summary": bi(
                "Sleep strengthens what was learned, but only if the study and "
                "the sleep are close together and the material was understood "
                "first. The evidence, however, comes mostly from young adults in "
                "laboratories.",
                "خواب آموخته‌ها را تقویت می‌کند، اما فقط اگر مطالعه و خواب نزدیک "
                "به هم باشند و مطلب قبلاً فهمیده شده باشد. با این حال، شواهد "
                "بیشتر از جوانان در آزمایشگاه به دست آمده است."),
        },
        "questions": {
            "blanks": [
                {"sentence": "During deep sleep the brain ___ the day's experiences.",
                 "answer": "replays",
                 "hint": bi("Runs them again - paragraph 1.",
                            "دوباره اجرا می‌کند؛ پاراگراف اول.")},
                {"sentence": "___ the effect depends on timing.",
                 "answer": "Yet",
                 "hint": bi("Three letters; it contrasts with the good news "
                            "before it.",
                            "سه حرف؛ با خبر خوب جملهٔ قبل مخالفت می‌کند.")},
                {"sentence": "___ , sleep cannot rescue material that was never "
                             "understood.",
                 "answer": "In contrast",
                 "hint": bi("Two words that announce a different case.",
                            "دو کلمه که یک حالت متفاوت را اعلام می‌کند.")},
                {"sentence": "___ , the useful rule is not 'sleep more' but "
                             "'understand first, then sleep'.",
                 "answer": "Consequently",
                 "hint": bi("It introduces the result of everything above.",
                            "نتیجهٔ همهٔ مطالب بالا را معرفی می‌کند.")},
            ],
            "mcq": [
                {"q": "What does 'Yet' at the start of paragraph 2 do?",
                 "options": ["It adds another benefit",
                             "It limits the claim made in paragraph 1",
                             "It gives an example",
                             "It concludes the passage"],
                 "answer": 1,
                 "why": bi("It signals a condition: the effect is real but depends "
                           "on timing.",
                           "یک شرط را اعلام می‌کند: اثر واقعی است اما به زمان‌بندی "
                           "بستگی دارد.")},
                {"q": "The function of the nap experiment is to",
                 "options": ["prove that naps are better than sleep at night",
                             "give evidence for the timing claim",
                             "show that virtual cities are useful",
                             "introduce a new topic"],
                 "answer": 1,
                 "why": bi("'For example' marks it as support for the sentence "
                           "before it.",
                           "«For example» آن را شاهدی برای جملهٔ قبل معرفی می‌کند.")},
                {"q": "What follows 'Consequently'?",
                 "options": ["A contradiction",
                             "A practical rule drawn from the evidence",
                             "A new experiment",
                             "A definition"],
                 "answer": 1,
                 "why": bi("Consequently introduces the result: understand first, "
                           "then sleep.",
                           "Consequently نتیجه را می‌آورد: اول بفهم، بعد بخواب.")},
                {"q": "The last paragraph exists to",
                 "options": ["repeat the main finding",
                             "admit the limits of the research",
                             "recommend more sleep",
                             "explain laboratory methods in detail"],
                 "answer": 1,
                 "why": bi("'However, the research has a limit' - the writer ends "
                           "on caution, not on the claim.",
                           "«However، این پژوهش محدودیتی دارد»؛ نویسنده با احتیاط "
                           "تمام می‌کند، نه با ادعا.")},
            ],
            "truefalse": [
                {"statement": "The passage says sleep is a pause in learning.",
                 "answer": False,
                 "why": bi("It says the opposite in the first six words.",
                           "پنج کلمهٔ اول دقیقاً برعکس را می‌گوید.")},
                {"statement": "Learning in the evening and sleeping helps more than "
                              "learning in the morning.",
                 "answer": True,
                 "why": bi("The comparison is in paragraph 1.",
                           "این مقایسه در پاراگراف اول است.")},
                {"statement": "According to the passage, any sleep improves any "
                              "memory.",
                 "answer": False,
                 "why": bi("Timing matters, and sleep cannot fix what was never "
                           "understood.",
                           "زمان‌بندی مهم است و خواب چیزی را که فهمیده نشده درست "
                           "نمی‌کند.")},
                {"statement": "The writer mentions a night shift as an example of "
                              "an untested situation.",
                 "answer": True,
                 "why": bi("'after a night shift... is still an open question.'",
                           "«بعد از شیفت شب… هنوز پرسشی بی‌جواب است.»")},
            ],
            "essay": [
                {"prompt": bi("Summarize the passage in 60-80 words. Use at least "
                              "two linking words of your own (however, therefore, "
                              "for instance).",
                              "متن را در ۶۰ تا ۸۰ کلمه خلاصه کن. دست‌کم دو واژهٔ "
                              "پیوند از خودت به کار ببر (however، therefore، "
                              "for instance)."),
                 "tips": [bi("One sentence per paragraph of the original.",
                             "برای هر پاراگراف متن اصلی یک جمله."),
                          bi("Keep the writer's caution - do not turn 'may' into "
                             "'does'.",
                             "احتیاط نویسنده را حفظ کن؛ «ممکن است» را به «هست» "
                             "تبدیل نکن."),
                          bi("Mark your links clearly; they are being tested.",
                             "پیوندهایت را واضح بگذار؛ همین‌ها آزمون می‌شوند.")],
                 "model": bi("Sleep helps memory because the brain replays new "
                             "experience and strengthens it. However, the effect "
                             "depends on timing: a nap straight after learning "
                             "works far better than sleep many hours later, as "
                             "the route experiment showed. Therefore, sleeping "
                             "cannot replace understanding - rereading something "
                             "you did not follow only makes you feel confident. "
                             "For instance, most of the evidence comes from young "
                             "adults in laboratories, so the rule may need "
                             "adjusting for other people.",
                             "خواب به حافظه کمک می‌کند چون مغز تجربهٔ تازه را دوباره "
                             "اجرا و تقویتش می‌کند. با این حال، اثر آن به زمان‌بندی "
                             "بستگی دارد: چرتِ بلافاصله بعد از یادگیری بسیار بهتر "
                             "از خواب چند ساعت بعد کار می‌کند، همان‌طور که آزمایش "
                             "مسیر نشان داد. بنابراین خواب جای فهمیدن را نمی‌گیرد؛ "
                             "خواندن دوبارهٔ چیزی که نفهمیده‌ای فقط به تو احساس "
                             "اطمینان می‌دهد. مثلاً بیشتر شواهد از جوانان در "
                             "آزمایشگاه است، پس قاعده ممکن است برای دیگران نیاز به "
                             "تعدیل داشته باشد.")},
                {"prompt": bi("The writer says the useful rule is 'understand first, "
                              "then sleep'. Describe how you would apply it to one "
                              "real exam you are preparing for.",
                              "نویسنده می‌گوید قاعدهٔ مفید این است: «اول بفهم، بعد "
                              "بخواب». توضیح بده آن را روی یک امتحان واقعی که برایش "
                              "آماده می‌شوی چگونه به کار می‌بری."),
                 "tips": [bi("Name the exam and the topic.",
                             "امتحان و موضوع را نام ببر."),
                          bi("Say what 'understand' means for that topic - a "
                             "worked example, not a reread.",
                             "بگو برای آن موضوع «فهمیدن» یعنی چه: یک مثال حل‌شده، "
                             "نه خواندن دوباره."),
                          bi("Put the study close to sleep and check the next "
                             "morning.",
                             "مطالعه را نزدیک خواب بگذار و صبح فردا بسنج.")],
                 "model": bi("For my statistics exam I would change one habit: "
                             "instead of rereading chapter four, I would solve two "
                             "problems without notes at nine in the evening, then "
                             "go to bed. If I cannot start a problem, that is the "
                             "signal that I do not understand it yet, and rereading "
                             "until midnight would only make me feel prepared. The "
                             "next morning I would redo the same two problems: "
                             "whatever comes back without help is what the sleep "
                             "actually kept.",
                             "برای امتحان آمارم یک عادت را عوض می‌کنم: به‌جای "
                             "خواندن دوبارهٔ فصل چهار، ساعت نُهِ شب دو مسئله را "
                             "بدون نگاه به جزوه حل می‌کنم و بعد می‌خوابم. اگر "
                             "نتوانم مسئله‌ای را شروع کنم، همین نشانهٔ آن است که "
                             "هنوز نفهمیده‌ام، و خواندن تا نیمه‌شب فقط حس آمادگی "
                             "به من می‌دهد. صبح فردا همان دو مسئله را دوباره حل "
                             "می‌کنم: هر چه بدون کمک برگردد، همان چیزی است که خواب "
                             "واقعاً نگه داشته است.")},
            ],
        },
    },
]
