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
    # ---------------------------------------------------------------- 7 -----
    {
        "id": "survey",
        "icon": "🧭",
        "level": "A2",
        "minutes": 6,
        "title": bi("Survey the text before you read it",
                    "پیش از خواندن، متن را بررسی کن"),
        "blurb": bi(
            "Two minutes on the title, the headings and the shape, and you know "
            "what kind of text you are holding.",
            "دو دقیقه روی عنوان، تیترها و شکل متن، و می‌دانی چه نوع متنی در دست "
            "داری."),
        "what": bi(
            "Surveying is looking at a text as an object before you read a "
            "single full sentence. You read the title, the subtitle, the "
            "headings, any picture or caption, the first and last line, and you "
            "decide three things: what kind of text this is (a guide, a report, "
            "a story, a notice), who wrote it for whom, and what it is probably "
            "going to tell you. Then you predict. Those predictions are what "
            "make the real reading fast, because you are checking guesses "
            "instead of discovering everything from zero.",
            "بررسی اولیه (survey) یعنی پیش از خواندن حتی یک جملهٔ کامل، به متن "
            "مثل یک شیء نگاه کنی: عنوان، زیرعنوان، تیترها، تصویر و زیرنویس، خط "
            "اول و آخر را بخوانی و سه چیز را تعیین کنی: این چه نوع متنی است "
            "(راهنما، گزارش، داستان، اطلاعیه)، چه کسی برای چه کسی نوشته، و "
            "احتمالاً چه چیزی به تو می‌گوید. بعد پیش‌بینی می‌کنی. همین پیش‌بینی‌ها "
            "خواندن واقعی را سریع می‌کنند، چون دیگر از صفر کشف نمی‌کنی؛ حدس‌هایت "
            "را می‌سنجی."),
        "why": bi(
            "A reader who knows what a text is for reads it differently. A "
            "guide is scanned for the section you need; a report is read for its "
            "conclusion; a story is read in order. Two minutes of surveying "
            "tells you which of those you are doing, and stops the commonest "
            "waste in reading: treating a list of rules as if it were an "
            "argument and looking for a point it never makes.",
            "خواننده‌ای که می‌داند متن برای چه نوشته شده، جور دیگری می‌خواند. "
            "راهنما را برای پیدا کردن بخش لازم اسکن می‌کنی؛ گزارش را برای نتیجه‌اش "
            "می‌خوانی؛ داستان را به ترتیب. دو دقیقه بررسی می‌گوید کدام‌یک را "
            "انجام می‌دهی و جلوی رایج‌ترین هدررفت خواندن را می‌گیرد: برخورد با "
            "فهرست قوانین مثل یک استدلال و گشتن دنبال نتیجه‌ای که هرگز نمی‌آید."),
        "when": bi(
            "At the start of any text you did not choose yourself: an exam "
            "passage, a letter from an office, a page of instructions, a "
            "website you have just landed on.",
            "در شروع هر متنی که خودت انتخابش نکرده‌ای: متن امتحان، نامهٔ اداری، "
            "صفحهٔ دستورالعمل، یا سایتی که تازه بازش کرده‌ای."),
        "steps": [
            bi("Read the title and subtitle and say the genre out loud: notice, "
               "guide, report, review, story.",
               "عنوان و زیرعنوان را بخوان و نوع متن را بلند بگو: اطلاعیه، راهنما، "
               "گزارش، نقد، داستان."),
            bi("List the headings in order. They are the author's own plan of "
               "the text, printed for you.",
               "تیترها را به ترتیب بنویس. آن‌ها نقشهٔ خود نویسنده از متن‌اند که "
               "برای تو چاپ شده است."),
            bi("Look for the small print: a date, a price, a name, a phone "
               "number. They tell you who the text is for and how official it "
               "is.",
               "نوشته‌های ریز را ببین: تاریخ، قیمت، نام، شمارهٔ تلفن. همین‌ها "
               "می‌گویند متن برای چه کسی و چقدر رسمی است."),
            bi("Predict in one sentence what you expect to learn, then read to "
               "check that sentence.",
               "در یک جمله پیش‌بینی کن چه چیزی یاد می‌گیری، بعد بخوان تا همان "
               "جمله را بسنجی."),
        ],
        "example": {
            "text": "HILLTOWN SWIMMING POOL — winter timetable. From 1 October "
                    "the pool opens at 7 am on weekdays and 8 am at weekends. "
                    "Lanes 1-3 are reserved for clubs before 9 am. The learner "
                    "pool is closed for repairs until 12 November; lessons move "
                    "to the main pool. Prices: adult £5.20, under-16 £2.60, "
                    "family £12.",
            "steps": [
                bi("Title first: 'winter timetable' plus a place name. This is a "
                   "notice, not an article - so the useful reading is scanning "
                   "for a day and a time, not looking for an argument.",
                   "اول عنوان: «winter timetable» و نام یک مکان. این یک اطلاعیه "
                   "است، نه مقاله؛ پس خواندن مفیدش اسکن کردن برای یک روز و ساعت "
                   "است، نه گشتن دنبال استدلال."),
                bi("The colon after 'Prices' tells you the last line is a list. "
                   "In a notice, a colon almost always introduces the exact "
                   "facts you came for.",
                   "دونقطه بعد از «Prices» می‌گوید خط آخر یک فهرست است. در "
                   "اطلاعیه‌ها دونقطه تقریباً همیشه همان واقعیت‌هایی را معرفی "
                   "می‌کند که به‌خاطرش آمده‌ای."),
                bi("Prediction: 'I will find out when it opens and what it "
                   "costs, and something is closed.' Reading then confirms it "
                   "in fifteen seconds.",
                   "پیش‌بینی: «می‌فهمم کی باز است، چقدر هزینه دارد، و چیزی تعطیل "
                   "است.» بعد خواندن در پانزده ثانیه تأییدش می‌کند."),
            ],
        },
        "mistakes": [
            bi("Reading the body first and the title afterwards. Titles and "
               "headings are the cheapest information in the text.",
               "اول متن را خواندن و بعد عنوان را. عنوان و تیترها ارزان‌ترین "
               "اطلاعات متن‌اند."),
            bi("Assuming every text has a main argument. A timetable, a recipe "
               "and a set of rules do not; hunting for one wastes the reading.",
               "فرض کردن اینکه هر متنی استدلال اصلی دارد. جدول زمانی، دستور "
               "پخت و فهرست قوانین ندارند؛ گشتن دنبال آن، خواندن را هدر می‌دهد."),
        ],
        "tips": [
            bi("Say the genre out loud before you read. Naming it changes how "
               "you read the first paragraph.",
               "نوع متن را پیش از خواندن بلند بگو. نام‌گذاری‌اش، خواندن پاراگراف "
               "اول را عوض می‌کند."),
            bi("Count the headings. Three headings mean three things to find; "
               "that is your reading plan, given away for free.",
               "تیترها را بشمار. سه تیتر یعنی سه چیز برای پیدا کردن؛ همین نقشهٔ "
               "خواندن تو است که مجانی لو رفته."),
        ],
        "checklist": [
            bi("Genre named before the first paragraph.",
               "نام‌گذاری نوع متن پیش از پاراگراف اول."),
            bi("Headings listed as a plan.",
               "نوشتن تیترها به‌عنوان نقشه."),
            bi("One prediction written down.",
               "نوشتن یک پیش‌بینی."),
            bi("Small print checked for date, price and audience.",
               "بررسی نوشته‌های ریز برای تاریخ، قیمت و مخاطب."),
        ],
        "reading": {
            "title": bi("Hilltown Community Garden: a guide for new members",
                         "باغ محلی هیل‌تاون: راهنمای اعضای تازه"),
            "level": "A2",
            "genre": bi("Guide / notice", "راهنما / اطلاعیه"),
            "paragraphs": [
                "Hilltown Community Garden — a guide for new members. The "
                "garden has forty plots on the site of an old railway yard, "
                "behind the swimming pool on Mill Road. Membership costs £18 a "
                "year and includes a key to the gate.",
                "Opening times. The gate opens at 8 am and closes at dusk. It "
                "is closed all day on Mondays for maintenance, and the water "
                "taps are switched off in December and January.",
                "Getting a plot. There is a waiting list of about two years. "
                "New members are asked to work four hours a month on the shared "
                "paths and hedges while they wait, which also earns them a "
                "small raised bed in the meantime.",
                "Rules. No bonfires between May and September. Tools must be "
                "returned to the shed by 7 pm. Dogs are welcome on leads. "
                "Contact the secretary, Mrs Okafor, at the shed on Sunday "
                "mornings.",
            ],
            "summary": bi(
                "A members' guide: where the garden is, when it is open, how to "
                "get a plot, and the rules. It contains times, a price and a "
                "contact name, but no argument.",
                "راهنمای اعضا: باغ کجاست، چه وقت باز است، چطور زمین بگیری و "
                "قوانین چیست. شامل ساعت‌ها، یک قیمت و نام یک نفر برای تماس "
                "است، ولی استدلالی ندارد."),
        },
        "questions": {
            "blanks": [
                {"sentence": "Membership costs ___ pounds a year.",
                 "answer": "18", "also": ["£18", "eighteen"],
                 "hint": bi("A number in the first section.",
                            "عددی در بخش اول."),
                 "para": 1},
                {"sentence": "The gate is closed all day on ___.",
                 "answer": "Mondays", "also": ["monday"],
                 "hint": bi("Look under 'Opening times'.",
                            "زیر «Opening times» را ببین."),
                 "para": 2},
                {"sentence": "The waiting list is about ___ years long.",
                 "answer": "two", "also": ["2"],
                 "hint": bi("A word, not a digit.", "یک کلمه، نه رقم."),
                 "para": 3},
                {"sentence": "Tools must be back in the shed by ___.",
                 "answer": "7 pm", "also": ["7pm", "seven pm"],
                 "hint": bi("A time, in the rules.", "یک ساعت، در قوانین."),
                 "para": 4},
            ],
            "mcq": [
                {"q": "What kind of text is this?",
                 "options": ["A news report about a garden",
                             "A guide for people joining a garden",
                             "A letter of complaint about a garden",
                             "A job advertisement for a gardener"],
                 "answer": 1,
                 "why": bi("The title says 'a guide for new members', and every "
                           "section gives instructions rather than news.",
                           "عنوان می‌گوید «راهنمای اعضای تازه» و هر بخش دستورالعمل "
                           "می‌دهد، نه خبر."),
                 "para": 1},
                {"q": "Which section tells you when you may visit?",
                 "options": ["Getting a plot", "Rules", "Opening times",
                             "The first section"],
                 "answer": 2,
                 "why": bi("'Opening times' is the heading that answers a "
                           "question about time.",
                           "تیتر «Opening times» همان تیتری است که به سؤال زمانی "
                           "جواب می‌دهد."),
                 "para": 2},
                {"q": "While you are on the waiting list, what can you do?",
                 "options": ["Pay an extra fee for a plot",
                             "Work four hours a month and get a raised bed",
                             "Use the shed but not the beds",
                             "Nothing at all"],
                 "answer": 1,
                 "why": bi("The third section says the four hours 'also earns "
                           "them a small raised bed in the meantime'.",
                           "بخش سوم می‌گوید چهار ساعت کار «در این فاصله یک بستر "
                           "کوچک» برایشان به دست می‌آورد."),
                 "para": 3},
                {"q": "Who should a member contact about a problem?",
                 "options": ["The council on Mill Road", "Mrs Okafor",
                             "The swimming pool", "The railway yard"],
                 "answer": 1,
                 "why": bi("The last line names the secretary and where to find "
                           "her.",
                           "خط آخر نام منشی و محل پیدا کردنش را می‌گوید."),
                 "para": 4},
            ],
            "truefalse": [
                {"statement": "The garden is on the site of an old railway yard.",
                 "answer": True,
                 "why": bi("'forty plots on the site of an old railway yard'.",
                           "«چهل قطعه روی محل یک حیاط راه‌آهن قدیمی»."),
                 "para": 1},
                {"statement": "You can start digging as soon as you pay.",
                 "answer": False,
                 "why": bi("There is a waiting list of about two years.",
                           "یک لیست انتظار حدوداً دوساله وجود دارد."),
                 "para": 3},
                {"statement": "Bonfires are allowed in July.",
                 "answer": False,
                 "why": bi("No bonfires between May and September.",
                           "بین مه و سپتامبر آتش روشن نمی‌شود."),
                 "para": 4},
                {"statement": "Dogs must be kept on a lead.",
                 "answer": True,
                 "why": bi("'Dogs are welcome on leads.'", "«سگ‌ها با قلاده مجازند.»"),
                 "para": 4},
            ],
            "essay": [
                {"prompt": bi("You have just moved to Hilltown and want a plot. "
                              "Using only the guide, describe what you would do "
                              "in your first month and what you would expect.",
                              "تازه به هیل‌تاون نقل مکان کرده‌ای و یک زمین می‌خواهی. "
                              "فقط با استفاده از راهنما بگو در ماه اول چه می‌کنی و "
                              "چه انتظاری داری."),
                 "tips": [
                     bi("Name the two things a new member must do: pay, and join "
                        "the list.",
                        "دو کاری را که عضو تازه باید بکند نام ببر: پرداخت و نوشتن "
                        "در لیست."),
                     bi("Use the guide's own times and price.",
                        "از ساعت‌ها و قیمت خود راهنما استفاده کن."),
                     bi("End with what you would ask that the guide does not "
                        "answer.",
                        "آخرش بگو چه چیزی می‌پرسی که راهنما جوابش را ندارد.")],
                 "model": bi("First I would go to the shed on a Sunday morning "
                             "and speak to Mrs Okafor, because that is where new "
                             "members are told to go. I would pay the £18 and "
                             "join the waiting list, which the guide says is about "
                             "two years. While I waited I would work my four "
                             "hours a month on the paths and use the raised bed "
                             "that comes with it. What I would still want to know "
                             "is whether the hours can be done at weekends only, "
                             "and whether the raised bed has water in winter.",
                             "اول صبح یکشنبه به انبار می‌رفتم و با خانم اوکافور حرف "
                             "می‌زدم، چون راهنما می‌گوید اعضای تازه باید آنجا بروند. "
                             "۱۸ پوند را می‌پرداختم و در لیست انتظار که راهنما "
                             "حدوداً دوساله می‌گوید ثبت‌نام می‌کردم. تا آن موقع ماهی "
                             "چهار ساعت روی مسیرها کار می‌کردم و از بستر بلندی که "
                             "همراهش می‌آید استفاده می‌کردم. چیزی که هنوز می‌خواستم "
                             "بدانم این بود که آیا ساعت‌ها فقط آخر هفته هم انجام "
                             "می‌شود و آیا بستر در زمستان آب دارد.")},
                {"prompt": bi("The guide gives times and prices but says nothing "
                              "about seeds or tools. Write three questions you "
                              "would ask the secretary, and say why the guide "
                              "does not answer them.",
                              "راهنما ساعت‌ها و قیمت‌ها را می‌گوید ولی از بذر و ابزار "
                              "حرفی نمی‌زند. سه سؤال بنویس که از منشی می‌پرسی و "
                              "بگو چرا راهنما جوابشان را ندارد."),
                 "tips": [
                     bi("Surveying is also noticing what a text leaves out.",
                        "بررسی اولیه یعنی دیدن چیزهایی که متن جا انداخته است."),
                     bi("Write real questions, with a question mark.",
                        "سؤال واقعی بنویس، با علامت سؤال."),
                     bi("Explain the gap: a guide is short on purpose.",
                        "خلأ را توضیح بده: راهنما عمداً کوتاه است.")],
                 "model": bi("Who supplies the seeds, and are they included in "
                             "the £18? Are there tools in the shed for members "
                             "who do not own any, and can they be borrowed "
                             "overnight? Is there a tap that works in January? "
                             "The guide does not answer these because it is "
                             "written for someone who has already decided to "
                             "join: it tells you how to get in, not how to "
                             "garden once you are in.",
                             "بذر را چه کسی می‌دهد و در همان ۱۸ پوند حساب شده است؟ "
                             "در انبار برای اعضایی که ابزار ندارند ابزاری هست و "
                             "می‌شود شبانه امانت گرفت؟ شیر آبی هست که در ژانویه کار "
                             "کند؟ راهنما به این‌ها جواب نمی‌دهد چون برای کسی نوشته "
                             "شده که تصمیمش را گرفته است: می‌گوید چطور وارد شوی، نه "
                             "اینکه بعدش چطور باغبانی کنی.")},
            ],
        },
    },
    {
        "id": "detail",
        "icon": "🖐️",
        "level": "B1",
        "minutes": 8,
        "title": bi("Read for detail and connect the sentences",
                    "خواندن برای جزئیات و پیوند دادن جمله‌ها"),
        "blurb": bi(
            "Careful reading is not slow reading. It is reading with a question "
            "in mind and a check after every fact.",
            "خواندن دقیق یعنی خواندن کند نیست؛ یعنی خواندن با یک سؤال در ذهن و "
            "بررسی بعد از هر واقعیت."),
        "what": bi(
            "Reading for detail means tracking individual facts and the links "
            "between them. Most wrong answers in detailed reading come from "
            "sentences that are true on their own but have been separated from "
            "the one that controls them: a number without its unit, a cause "
            "without its condition, a rule without its exception. Careful "
            "reading, then, has two moves. First you fix each fact exactly - "
            "what, how much, compared with what. Then you read the connecting "
            "words that say how the facts relate: because, although, unless, "
            "only, still. The second move is what turns a list of facts into "
            "comprehension.",
            "خواندن برای جزئیات یعنی دنبال کردن واقعیت‌های جداگانه و پیوندهای میان "
            "آن‌ها. بیشتر جواب‌های غلط در این نوع خواندن از جمله‌هایی می‌آید که "
            "تنهایی درست‌اند ولی از جمله‌ای که آن‌ها را کنترل می‌کند جدا شده‌اند: "
            "عددی بدون واحدش، علتی بدون شرطش، قانونی بدون استثنایش. پس خواندن "
            "دقیق دو حرکت دارد. اول هر واقعیت را مو‌به‌مو تثبیت می‌کنی: چه، چه "
            "مقداری، در مقایسه با چه. بعد واژه‌های پیوند را می‌خوانی که می‌گویند "
            "این واقعیت‌ها چه نسبتی دارند: because، although، unless، only، "
            "still. حرکت دوم همان چیزی است که فهرست واقعیت‌ها را به فهم تبدیل "
            "می‌کند."),
        "why": bi(
            "Exams and real documents both hide their answer in a relationship. "
            "'The equipment cost 1.4 million euros' is easy; 'the equipment "
            "cost 1.4 million and pays for itself in nine years, but only if the "
            "neighbour keeps producing heat' is the sentence you actually have "
            "to understand. Detailed reading is the habit of not stopping at "
            "the first half.",
            "هم امتحان و هم اسناد واقعی جواب را در یک رابطه پنهان می‌کنند. «تجهیزات "
            "۱٫۴ میلیون یورو هزینه داشت» ساده است؛ «تجهیزات ۱٫۴ میلیون هزینه داشت و "
            "در نه سال جبران می‌شود، ولی فقط اگر همسایه تولید گرما را ادامه دهد» "
            "همان جمله‌ای است که واقعاً باید بفهمی. خواندن دقیق، عادت نایستادن در "
            "نیمهٔ اول است."),
        "when": bi(
            "When the question asks for a number, a condition, a reason or a "
            "comparison - and when the text is a report, a contract, a set of "
            "instructions or an exam passage with several facts close together.",
            "وقتی سؤال یک عدد، یک شرط، یک دلیل یا یک مقایسه می‌خواهد؛ و وقتی متن "
            "گزارش، قرارداد، دستورالعمل یا متن امتحانی با چند واقعیت نزدیک به "
            "هم است."),
        "steps": [
            bi("Turn the question into the shape of its answer: a temperature, "
               "a percentage, a length of time.",
               "سؤال را به شکل جوابش برگردان: یک دما، یک درصد، یک مدت زمان."),
            bi("Find the sentence, then read the one before and the one after "
               "it. Detail questions are usually answered across two sentences.",
               "جمله را پیدا کن، بعد جملهٔ قبل و بعدش را بخوان. سؤال‌های جزئیات "
               "معمولاً در دو جمله جواب داده می‌شوند."),
            bi("Circle the qualifier: only, unless, at least, up to, compared "
               "with. Most traps live in that word.",
               "دور قید شرط خط بکش: only، unless، at least، up to، compared with. "
               "بیشتر تله‌ها در همان کلمه‌اند."),
            bi("Say the fact back in a full sentence with its condition "
               "attached before you choose.",
               "پیش از انتخاب، واقعیت را در یک جملهٔ کامل و همراه با شرطش بازگو "
               "کن."),
        ],
        "example": {
            "text": "The library closes at six on weekdays, except during exam "
                    "weeks, when it stays open until ten. Students may borrow "
                    "eight books at a time; staff may borrow twelve. Renewals "
                    "are free twice, after which a fee of 40 pence a day applies.",
            "steps": [
                bi("Question: 'Until what time is the library open in exam "
                   "weeks?' The first clause answers a different question - six "
                   "on ordinary weekdays - and 'except' is the hinge.",
                   "سؤال: «کتابخانه در هفته‌های امتحان تا چه ساعتی باز است؟» بند اول "
                   "به سؤال دیگری جواب می‌دهد (شش در روزهای عادی) و except لولای "
                   "مطلب است."),
                bi("Question: 'How many books may a student borrow?' Eight, not "
                   "twelve: the semicolon separates two groups, and the second "
                   "number belongs to staff.",
                   "سؤال: «دانشجو چند کتاب می‌تواند امانت بگیرد؟» هشت، نه دوازده: "
                   "نقطه‌ویرگول دو گروه را جدا می‌کند و عدد دوم مال کارکنان است."),
                bi("Question: 'Is the third renewal free?' No. Two renewals are "
                   "free; from the third, 40 pence a day. 'After which' counts "
                   "forwards.",
                   "سؤال: «تمدید سوم مجانی است؟» نه. دو تمدید مجانی است؛ از سومی "
                   "روزی ۴۰ پنس. عبارت after which رو به جلو می‌شمارد."),
            ],
        },
        "mistakes": [
            bi("Answering from the first sentence that contains the key word, "
               "without reading its condition.",
               "جواب دادن از اولین جمله‌ای که کلمهٔ کلیدی را دارد، بدون خواندن "
               "شرطش."),
            bi("Ignoring punctuation. A semicolon, a dash or a bracket usually "
               "marks a change of subject or an exception.",
               "نادیده گرفتن نقطه‌گذاری. نقطه‌ویرگول، خط تیره یا پرانتز معمولاً "
               "تغییر موضوع یا استثنا را نشان می‌دهد."),
            bi("Rushing because the topic is familiar. Familiarity is exactly "
               "when you stop checking the numbers.",
               "شتاب کردن چون موضوع آشناست. آشنایی دقیقاً همان وقتی است که بررسی "
               "عددها را رها می‌کنی."),
        ],
        "tips": [
            bi("Read numbers with their units out loud: 'twenty-seven degrees', "
               "not 'twenty-seven'.",
               "عددها را با واحدشان بلند بخوان: «بیست‌وهفت درجه»، نه «بیست‌وهفت»."),
            bi("Mark every contrast in the margin with a single symbol. Six "
               "marks on a page show you where the text is doing work.",
               "هر تضاد را در حاشیه با یک نماد علامت بزن. شش علامت در صفحه نشان "
               "می‌دهد متن کجا کار می‌کند."),
        ],
        "checklist": [
            bi("Answer shape named before searching.",
               "تعیین شکل جواب پیش از جست‌وجو."),
            bi("Sentence plus its neighbour read together.",
               "خواندن جمله همراه با جملهٔ کنارش."),
            bi("Qualifier identified and included in the answer.",
               "شناسایی قید شرط و آوردنش در جواب."),
            bi("Fact restated as a full sentence before choosing.",
               "بازگویی واقعیت در جملهٔ کامل پیش از انتخاب."),
        ],
        "reading": {
            "title": bi("The swimming pool that heats itself",
                         "استخری که خودش را گرم می‌کند"),
            "level": "B1",
            "genre": bi("Popular science report", "گزارش علمی عمومی"),
            "paragraphs": [
                "The swimming pool in the French town of Vitry replaced its gas "
                "boiler in 2021 with a system that recovers heat from the "
                "building next door. The neighbour is a data centre: a hall of "
                "servers that runs all day and must be cooled. Its waste heat, "
                "once released into the air, now passes through a heat "
                "exchanger and warms the pool's water to 27 °C.",
                "The engineering is less simple than the idea. The data "
                "centre's cooling circuit uses a fluid at about 45 °C, while "
                "the pool needs water at 27 °C, so a second circuit and a pump "
                "station were needed to step the temperature down without "
                "losing the difference. That equipment cost €1.4 million and "
                "took eleven months to install.",
                "The saving is measured in gas: the pool burned 420,000 cubic "
                "metres a year before the change and 60,000 after, a fall of 86 "
                "per cent. The remaining gas is used only in the coldest weeks, "
                "when the data centre alone cannot meet demand.",
                "Not every town can copy this. A pool needs a neighbour that "
                "produces heat all year, within about 300 metres, and a council "
                "willing to sign a fifteen-year contract. Vitry had all three. "
                "The mayor's office says the payback period is nine years.",
            ],
            "summary": bi(
                "A pool is warmed by the waste heat of a neighbouring data "
                "centre. The idea is simple, the plumbing is not, and the "
                "saving depends on conditions most towns do not have.",
                "استخر با گرمای هدررفتهٔ یک مرکز دادهٔ همسایه گرم می‌شود. ایده "
                "ساده است، لوله‌کشی نه، و صرفه‌جویی به شرایطی بند است که بیشتر "
                "شهرها ندارند."),
        },
        "questions": {
            "blanks": [
                {"sentence": "The pool's water is warmed to ___ °C.",
                 "answer": "27", "also": [],
                 "hint": bi("The first paragraph gives the figure.",
                            "پاراگراف اول عدد را می‌دهد."),
                 "para": 1},
                {"sentence": "The data centre's cooling fluid is at about ___ °C.",
                 "answer": "45", "also": [],
                 "hint": bi("Compare the two temperatures.",
                            "دو دما را با هم مقایسه کن."),
                 "para": 2},
                {"sentence": "The new equipment cost €___ million.",
                 "answer": "1.4", "also": ["1,4"],
                 "hint": bi("A price, with a decimal point.",
                            "یک قیمت، با ممیز."),
                 "para": 2},
                {"sentence": "Gas use fell by ___ per cent.",
                 "answer": "86", "also": [],
                 "hint": bi("The third paragraph does the arithmetic for you.",
                            "پاراگراف سوم حساب را برایت انجام داده."),
                 "para": 3},
            ],
            "mcq": [
                {"q": "Why was a second circuit and pump station needed?",
                 "options": ["Because the data centre is 300 metres away",
                             "Because the two sides run at different "
                             "temperatures",
                             "Because the pool is open all year",
                             "Because gas boilers cannot work with a heat "
                             "exchanger"],
                 "answer": 1,
                 "why": bi("'45 °C ... while the pool needs water at 27 °C, so a "
                           "second circuit ... was needed to step the temperature "
                           "down'. The reason is the gap, not the distance.",
                           "«۴۵ درجه... در حالی که استخر آب ۲۷ درجه می‌خواهد، پس "
                           "مدار دومی لازم شد تا دما را پایین بیاورد». دلیل، فاصلهٔ "
                           "دماست، نه مسافت."),
                 "para": 2},
                {"q": "When is the remaining gas used?",
                 "options": ["Every night", "In the coldest weeks only",
                             "All year, at a low rate", "During repairs"],
                 "answer": 1,
                 "why": bi("The passage says 'only in the coldest weeks, when the "
                           "data centre alone cannot meet demand'. The word "
                           "'only' is the whole answer.",
                           "متن می‌گوید «فقط در سردترین هفته‌ها، وقتی مرکز داده "
                           "تنها نمی‌تواند تقاضا را پوشش دهد». کلمهٔ only تمام "
                           "جواب است."),
                 "para": 3},
                {"q": "Which of these is NOT given as a condition for copying "
                       "the system?",
                 "options": ["A neighbour that produces heat all year",
                             "A distance of about 300 metres or less",
                             "A national subsidy for green heating",
                             "A fifteen-year contract"],
                 "answer": 2,
                 "why": bi("The last paragraph lists three conditions: heat all "
                           "year, within 300 metres, a fifteen-year contract. No "
                           "subsidy is mentioned anywhere.",
                           "پاراگراف آخر سه شرط را می‌شمارد: گرمای تمام سال، فاصلهٔ "
                           "حدود ۳۰۰ متر، قرارداد پانزده‌ساله. هیچ یارانه‌ای در متن "
                           "نیست."),
                 "para": 4},
                {"q": "What does 'the payback period is nine years' mean?",
                 "options": ["The contract lasts nine years",
                             "The equipment will need replacing in nine years",
                             "The money saved takes nine years to equal the money "
                             "spent",
                             "The pool was built nine years ago"],
                 "answer": 2,
                 "why": bi("Payback is the time for savings to repay the €1.4 "
                           "million cost. The contract is fifteen years, which is "
                           "a different number in the same paragraph.",
                           "بازگشت سرمایه زمانی است که صرفه‌جویی هزینهٔ ۱٫۴ میلیون را "
                           "بپوشاند. قرارداد پانزده‌ساله است و عدد دیگری در همان "
                           "پاراگراف."),
                 "para": 4},
            ],
            "truefalse": [
                {"statement": "Before 2021 the data centre's waste heat went "
                              "into the air.",
                 "answer": True,
                 "why": bi("'Its waste heat, once released into the air, now "
                           "passes through a heat exchanger'.",
                           "«گرمای هدررفته‌اش، که قبلاً در هوا رها می‌شد، حالا از "
                           "مبدل گرما می‌گذرد»."),
                 "para": 1},
                {"statement": "Installing the new equipment took longer than a "
                              "year.",
                 "answer": False,
                 "why": bi("It 'took eleven months', which is less than a year. A "
                           "careless reader sees a big number and assumes 'over a "
                           "year'.",
                           "«یازده ماه» طول کشید که کمتر از یک سال است. خوانندهٔ "
                           "بی‌دقت عدد بزرگ را می‌بیند و «بیش از یک سال» فرض "
                           "می‌کند."),
                 "para": 2},
                {"statement": "The pool still burns some gas.",
                 "answer": True,
                 "why": bi("60,000 cubic metres remain, used in the coldest "
                           "weeks. The saving is 86 per cent, not 100.",
                           "۶۰٬۰۰۰ متر مکعب باقی مانده که در سردترین هفته‌ها مصرف "
                           "می‌شود. صرفه‌جویی ۸۶ درصد است، نه ۱۰۰."),
                 "para": 3},
                {"statement": "Any town with a data centre can copy the system.",
                 "answer": False,
                 "why": bi("The passage says the opposite: 'Not every town can "
                           "copy this', and requires three conditions at once.",
                           "متن خلافش را می‌گوید: «هر شهری نمی‌تواند این را کپی کند» "
                           "و سه شرط همزمان می‌خواهد."),
                 "para": 4},
            ],
            "essay": [
                {"prompt": bi("Explain, in your own words, why the temperature "
                              "difference made the project harder. Use both "
                              "temperatures in your answer.",
                              "با کلمات خودت توضیح بده چرا اختلاف دما کار را سخت‌تر "
                              "کرد. هر دو دما را در جواب بیاور."),
                 "tips": [
                     bi("State the two temperatures first, then the problem "
                        "they create.",
                        "اول دو دما را بگو، بعد مشکلی که می‌سازند."),
                     bi("Use 'because' and 'so that' to show the link.",
                        "برای نشان دادن پیوند از because و so that استفاده کن."),
                     bi("Mention what would be wasted without the second "
                        "circuit.",
                        "بگو بدون مدار دوم چه چیزی هدر می‌رفت.")],
                 "model": bi("The data centre's cooling fluid leaves at about 45 "
                             "°C, but the pool only needs water at 27 °C. If the "
                             "hot fluid went straight into the pool, the water "
                             "would be too hot, and if it were simply left to "
                             "cool, the extra heat would be wasted. So a second "
                             "circuit and a pump station were added to bring the "
                             "temperature down by about 18 degrees while keeping "
                             "as much of the heat as possible. That is why the "
                             "system cost more than a direct connection would "
                             "have.",
                             "سیال خنک‌کنندهٔ مرکز داده با حدود ۴۵ درجه بیرون می‌آید، "
                             "ولی استخر فقط آب ۲۷ درجه می‌خواهد. اگر سیال داغ مستقیم "
                             "به استخر می‌رفت، آب بیش از حد گرم می‌شد، و اگر فقط "
                             "رها می‌شد تا سرد شود، گرمای اضافی هدر می‌رفت. پس یک "
                             "مدار دوم و ایستگاه پمپ اضافه شد تا دما را حدود ۱۸ "
                             "درجه پایین بیاورد و در همان حال بیشترین گرما را نگه "
                             "دارد. همین باعث شد سیستم از یک اتصال مستقیم گران‌تر "
                             "تمام شود.")},
                {"prompt": bi("The passage says 'Vitry had all three'. List the "
                              "three conditions and say which one you think is "
                              "hardest for a small town to meet, and why.",
                              "متن می‌گوید «ویتری هر سه را داشت». سه شرط را فهرست کن "
                              "و بگو کدام‌یک برای یک شهر کوچک سخت‌ترین است و چرا."),
                 "tips": [
                     bi("Number the conditions exactly as the passage gives "
                        "them.",
                        "شرط‌ها را دقیقاً همان‌طور که متن می‌دهد شماره‌گذاری کن."),
                     bi("Choose one and give a reason from the text, not from "
                        "general opinion.",
                        "یکی را انتخاب کن و دلیلت را از متن بیاور، نه از نظر "
                        "عمومی."),
                     bi("Keep it to five or six sentences.",
                        "در پنج یا شش جمله نگهش دار.")],
                 "model": bi("The three conditions are: a neighbour that produces "
                             "heat all year, that neighbour within about 300 "
                             "metres, and a council willing to sign a fifteen-year "
                             "contract. I think the contract is hardest for a "
                             "small town, because it commits the council to one "
                             "supplier for longer than most councils plan ahead, "
                             "and the passage shows the payback takes nine years, "
                             "so the decision has to survive at least two "
                             "elections.",
                             "سه شرط این‌ها هستند: همسایه‌ای که تمام سال گرما تولید "
                             "کند، فاصلهٔ حدود ۳۰۰ متر، و شورایی که حاضر باشد قرارداد "
                             "پانزده‌ساله امضا کند. فکر می‌کنم قرارداد برای یک شهر "
                             "کوچک سخت‌ترین است، چون شورا را بیشتر از افق برنامه‌ریزی "
                             "معمولش به یک تأمین‌کننده گره می‌زند، و متن نشان می‌دهد "
                             "بازگشت سرمایه نه سال طول می‌کشد؛ پس تصمیم باید حداقل "
                             "دو دورهٔ انتخاباتی را دوام بیاورد.")},
            ],
        },
    },
    {
        "id": "mainidea",
        "icon": "🎯",
        "level": "B1",
        "minutes": 7,
        "title": bi("Find the main idea and leave the details where they are",
                    "ایدهٔ اصلی را پیدا کن و جزئیات را سر جایشان بگذار"),
        "blurb": bi(
            "A paragraph says one thing and proves it. Learning to hear the "
            "difference is the whole skill.",
            "هر پاراگراف یک چیز می‌گوید و آن را اثبات می‌کند. یاد گرفتن شنیدن "
            "این تفاوت، تمام مهارت است."),
        "what": bi(
            "The topic of a paragraph is what it is about: pocket forests. The "
            "main idea is what the paragraph says about that topic: cities "
            "plant them mainly because they cool the air. Everything else - a "
            "temperature in degrees, a date, a named botanist - is a supporting "
            "detail, and its job is to make the main idea believable. A topic "
            "is a noun or a phrase; a main idea is a full sentence that "
            "somebody could disagree with. That test is the fastest one there "
            "is: if nobody could argue with your sentence, it is a topic, not "
            "an idea.",
            "موضوع یک پاراگراف چیزی است که دربارهٔ آن حرف می‌زند: جنگل‌های جیبی. "
            "ایدهٔ اصلی چیزی است که پاراگراف دربارهٔ آن موضوع می‌گوید: شهرها "
            "اصولاً آن‌ها را می‌کارند چون هوا را خنک می‌کنند. بقیهٔ چیزها - دمایی "
            "بر حسب درجه، یک تاریخ، نام یک گیاه‌شناس - جزئیات پشتیبان‌اند و کارشان "
            "باورپذیر کردن ایدهٔ اصلی است. موضوع یک اسم یا عبارت است؛ ایدهٔ اصلی "
            "یک جملهٔ کامل که کسی می‌تواند با آن مخالفت کند. همین آزمون سریع‌ترین "
            "است: اگر هیچ‌کس نتواند با جملهٔ تو مخالفت کند، آن جمله موضوع است، "
            "نه ایده."),
        "why": bi(
            "Almost every summary question, title question and 'what is the "
            "passage mainly about' question is testing this one distinction. "
            "Readers who cannot separate the two pick the answer that repeats "
            "the most words from the text, which is usually a detail, and "
            "usually correct in itself - which is what makes it a good trap.",
            "تقریباً هر سؤال خلاصه، سؤال عنوان و سؤال «متن اصلاً دربارهٔ چیست» همین "
            "یک تفکیک را می‌سنجد. خواننده‌ای که نمی‌تواند این دو را جدا کند، "
            "گزینه‌ای را انتخاب می‌کند که بیشترین کلمه‌های متن را تکرار می‌کند؛ "
            "که معمولاً یک جزئیات است و خودش هم درست است - و همین آن را به تلهٔ "
            "خوبی تبدیل می‌کند."),
        "when": bi(
            "Whenever a question asks for the main idea, the best title, the "
            "writer's purpose or a summary - and whenever you are taking notes "
            "and need one line per paragraph instead of ten.",
            "هر وقت سؤالی ایدهٔ اصلی، بهترین عنوان، هدف نویسنده یا خلاصه را "
            "می‌پرسد؛ و هر وقت یادداشت برمی‌داری و به‌جای ده خط، یک خط برای هر "
            "پاراگراف می‌خواهی."),
        "steps": [
            bi("Name the topic in one or two words. Wrong answers often share "
               "the topic, so the topic alone decides nothing.",
               "موضوع را در یک یا دو کلمه نام ببر. جواب‌های غلط هم معمولاً همان "
               "موضوع را دارند، پس موضوع تنها چیزی را تعیین نمی‌کند."),
            bi("Find the topic sentence - usually first, sometimes last - and "
               "check that the other sentences support it rather than continue "
               "it.",
               "جملهٔ موضوع را پیدا کن - معمولاً اول، گاهی آخر - و بسنج که جمله‌های "
               "دیگر پشتیبانی‌اش می‌کنند یا ادامه‌اش می‌دهند."),
            bi("Write the idea as a sentence somebody could disagree with. "
               "'Pocket forests are small' fails; 'cities plant them for heat' "
               "passes.",
               "ایده را به‌صورت جمله‌ای بنویس که کسی بتواند مخالفت کند. «جنگل‌های "
               "جیبی کوچک‌اند» رد می‌شود؛ «شهرها آن‌ها را برای گرما می‌کارند» قبول "
               "می‌شود."),
            bi("Cover the details and check the idea still stands. If it needs "
               "the numbers to make sense, it was a detail.",
               "جزئیات را بپوشان و ببین ایده هنوز سرپاست. اگر برای معنی داشتن به "
               "عددها نیاز دارد، جزئیات بوده."),
        ],
        "example": {
            "text": "Many hospitals now clean their corridors at night. The "
                    "change began in 2018, when a study found that daytime "
                    "cleaning disturbed patients' sleep and slowed recovery. "
                    "Night shifts cost eleven per cent more in wages, but the "
                    "same study estimated that faster recovery saved more than "
                    "that difference.",
            "steps": [
                bi("Topic: hospital cleaning times. That is not yet an idea - "
                   "nobody would argue with a topic.",
                   "موضوع: ساعت نظافت بیمارستان. این هنوز ایده نیست؛ هیچ‌کس با یک "
                   "موضوع مخالفت نمی‌کند."),
                bi("The first sentence is the claim: cleaning moved to night. "
                   "The next two give the reason (sleep) and the price (wages), "
                   "both supporting it.",
                   "جملهٔ اول ادعاست: نظافت به شب منتقل شد. دو جملهٔ بعد دلیل "
                   "(خواب) و قیمت (دستمزد) را می‌دهند و هر دو پشتیبان آن‌اند."),
                bi("So the main idea is a trade: hospitals accept higher wages "
                   "to protect sleep and shorten stays. 'A study in 2018' is a "
                   "detail, however true.",
                   "پس ایدهٔ اصلی یک معامله است: بیمارستان‌ها دستمزد بیشتر را "
                   "می‌پذیرند تا خواب را حفظ کنند و مدت بستری را کوتاه کنند. "
                   "«یک مطالعه در ۲۰۱۸» هرچقدر هم درست، جزئیات است."),
            ],
        },
        "mistakes": [
            bi("Choosing the longest, most complete-looking option. Length is "
               "not importance.",
               "انتخاب بلندترین و کامل‌ترین گزینه. بلندی نشانهٔ اهمیت نیست."),
            bi("Choosing an option that is true but narrow - one paragraph's "
               "detail offered as the whole passage's point.",
               "انتخاب گزینه‌ای که درست ولی محدود است: جزئیات یک پاراگراف به‌جای "
               "نکتهٔ کل متن."),
            bi("Confusing the writer's topic with the writer's attitude. "
               "'Pocket forests have limits' is an attitude about the topic.",
               "اشتباه گرفتن موضوع با موضع نویسنده. «جنگل‌های جیبی محدودیت دارند» "
               "موضعی دربارهٔ موضوع است."),
        ],
        "tips": [
            bi("Write the main idea of each paragraph in the margin as you "
               "read. Four lines at the end give you the whole passage.",
               "موقع خواندن، ایدهٔ اصلی هر پاراگراف را در حاشیه بنویس. چهار خط در "
               "پایان، تمام متن را به تو می‌دهد."),
            bi("Ask 'so what?' after each paragraph. The answer is the idea; "
               "the sentence you just read was probably the evidence.",
               "بعد از هر پاراگراف بپرس «خب که چه؟». جواب همان ایده است؛ جمله‌ای "
               "که خواندی احتمالاً شاهد بود."),
        ],
        "checklist": [
            bi("Topic written as a word, idea written as a sentence.",
               "نوشتن موضوع به‌صورت یک کلمه و ایده به‌صورت یک جمله."),
            bi("The idea is something a reader could disagree with.",
               "ایده چیزی است که خواننده می‌تواند با آن مخالفت کند."),
            bi("Details covered and the idea still standing.",
               "پوشاندن جزئیات و سرپا ماندن ایده."),
        ],
        "reading": {
            "title": bi("A forest the size of a tennis court",
                         "جنگلی به اندازهٔ یک زمین تنیس"),
            "level": "B1",
            "genre": bi("Feature article", "مقالهٔ گزارش‌گونه"),
            "paragraphs": [
                "A pocket forest is a patch of woodland the size of a tennis "
                "court or two, planted densely in a school yard, beside a road "
                "or on the corner of a car park. The method comes from the "
                "Japanese botanist Akira Miyawaki, who argued in the 1970s that "
                "a forest could be rebuilt from native species in decades "
                "rather than centuries. The first European versions were "
                "planted in the Netherlands in 2015.",
                "The clearest reason to plant one is heat. A dense stand of "
                "trees cools the air beneath it by shading the ground and by "
                "releasing water through its leaves, and measurements in Dutch "
                "and Belgian towns record differences of two to four degrees "
                "on summer afternoons. In streets where most residents have no "
                "garden, that difference is felt in the bedroom at night as "
                "much as on the pavement at noon.",
                "The second reason is rain. Concrete sends a storm straight "
                "into the drains, while the roots and loose soil of a small "
                "wood hold part of it back, so a single forest can keep "
                "hundreds of litres out of an overloaded sewer in one "
                "downpour.",
                "Pocket forests are not a solution on their own. They need "
                "about three years of watering before they survive without "
                "help, they struggle on badly polluted ground, and a tennis "
                "court of trees takes away parking that somebody was using. "
                "The method's defenders answer that a forest is one of the few "
                "pieces of city infrastructure that gets cheaper to keep every "
                "year.",
            ],
            "summary": bi(
                "Small dense woods cool streets, hold back rain and cost less "
                "to keep as they age - but they need years of care and take up "
                "space people were already using.",
                "جنگل‌های کوچک و انبوه خیابان‌ها را خنک می‌کنند، آب باران را نگه "
                "می‌دارند و هرچه پیرتر می‌شوند نگهداری‌شان ارزان‌تر می‌شود - ولی "
                "سال‌ها مراقبت می‌خواهند و فضایی را می‌گیرند که مردم از قبل "
                "استفاده می‌کردند."),
        },
        "questions": {
            "blanks": [
                {"sentence": "A pocket forest is about the size of a ___ court.",
                 "answer": "tennis", "also": [],
                 "hint": bi("The first line names the comparison.",
                            "خط اول مقایسه را نام می‌برد."),
                 "para": 1},
                {"sentence": "The method comes from the botanist Akira ___.",
                 "answer": "Miyawaki", "also": [],
                 "hint": bi("A Japanese name, spelled in English letters.",
                            "یک نام ژاپنی، با حروف انگلیسی."),
                 "para": 1},
                {"sentence": "Trees cool the air by ___ and by releasing water "
                             "through their leaves.",
                 "answer": "shading the ground", "also": ["shading", "shade"],
                 "hint": bi("The verb is a form of 'shade'.",
                            "فعل از ریشهٔ shade است."),
                 "para": 2},
                {"sentence": "New forests need about ___ years of watering.",
                 "answer": "three", "also": ["3"],
                 "hint": bi("A word, in the last paragraph.",
                            "یک کلمه، در پاراگراف آخر."),
                 "para": 4},
            ],
            "mcq": [
                {"q": "Which sentence states the main idea of the second "
                       "paragraph?",
                 "options": ["Measurements in Dutch and Belgian towns record "
                             "differences of two to four degrees",
                             "The clearest reason to plant one is heat",
                             "Most residents in these streets have no garden",
                             "Trees release water through their leaves"],
                 "answer": 1,
                 "why": bi("The first sentence is the claim the rest of the "
                           "paragraph supports. The measurements are the "
                           "evidence; the garden detail explains who benefits.",
                           "جملهٔ اول ادعایی است که بقیهٔ پاراگراف پشتیبانی‌اش می‌کند. "
                           "اندازه‌گیری‌ها شاهدند و جزئیات باغ توضیح می‌دهد چه کسی "
                           "سود می‌برد."),
                 "para": 2},
                {"q": "What is the passage mainly about?",
                 "options": ["The life of the botanist Akira Miyawaki",
                             "Why cities plant pocket forests, and what limits "
                             "them",
                             "How to plant a tree correctly",
                             "Why concrete causes flooding in cities"],
                 "answer": 1,
                 "why": bi("Three paragraphs give reasons (heat, rain, low "
                           "upkeep) and the last gives the limits. Each wrong "
                           "option is one detail inflated into the whole.",
                           "سه پاراگراف دلیل می‌دهند (گرما، باران، نگهداری ارزان) و "
                           "پاراگراف آخر محدودیت‌ها را. هر گزینهٔ غلط یک جزئیات است "
                           "که به کل متن باد شده."),
                 "para": 4},
                {"q": "Which of these is a supporting detail rather than a main "
                       "idea?",
                 "options": ["Small woods are worth planting in cities",
                             "Pocket forests have real limits",
                             "A stand of trees can keep hundreds of litres out of "
                             "a sewer",
                             "Trees get cheaper to keep as they age"],
                 "answer": 2,
                 "why": bi("The litres are a measurement inside the rain "
                           "argument. The other three are claims a reader could "
                           "disagree with.",
                           "لیترها اندازه‌گیری‌ای درون استدلال باران‌اند. سه گزینهٔ "
                           "دیگر ادعاهایی‌اند که خواننده می‌تواند با آن‌ها مخالفت "
                           "کند."),
                 "para": 3},
                {"q": "What does the last sentence of the passage suggest?",
                 "options": ["Forests are expensive to maintain",
                             "The cost of looking after a forest falls as it "
                             "matures",
                             "Cities should not plant forests near car parks",
                             "Infrastructure always gets more expensive"],
                 "answer": 1,
                 "why": bi("'Gets cheaper to keep every year' is the defenders' "
                           "answer to the cost objection - the opposite of the "
                           "first option.",
                           "«هر سال نگهداری‌اش ارزان‌تر می‌شود» جواب مدافعان به اعتراض "
                           "هزینه است - برعکس گزینهٔ اول."),
                 "para": 4},
            ],
            "truefalse": [
                {"statement": "The method uses trees native to the area.",
                 "answer": True,
                 "why": bi("The forest is 'rebuilt from native species'.",
                           "جنگل «از گونه‌های بومی» بازسازی می‌شود."),
                 "para": 1},
                {"statement": "Once planted, a pocket forest needs no care.",
                 "answer": False,
                 "why": bi("It needs 'about three years of watering before they "
                           "survive without help'.",
                           "«حدود سه سال آبیاری» لازم است تا بدون کمک دوام بیاورد."),
                 "para": 4},
                {"statement": "The passage says such woods can lower summer "
                              "temperatures by a few degrees.",
                 "answer": True,
                 "why": bi("'Differences of two to four degrees on summer "
                           "afternoons'.",
                           "«اختلاف دو تا چهار درجه در بعدازظهرهای تابستان»."),
                 "para": 2},
                {"statement": "The writer believes pocket forests can solve "
                              "every city problem.",
                 "answer": False,
                 "why": bi("The fourth paragraph opens with the opposite claim: "
                           "'not a solution on their own'.",
                           "پاراگراف چهارم با ادعای مخالف شروع می‌شود: «به‌تنهایی راه‌حل "
                           "نیستند»."),
                 "para": 4},
            ],
            "essay": [
                {"prompt": bi("Write one sentence for the main idea of each of "
                              "the four paragraphs. Do not copy the topic "
                              "sentences.",
                              "برای ایدهٔ اصلی هر یک از چهار پاراگراف یک جمله "
                              "بنویس. جمله‌های موضوع را کپی نکن."),
                 "min_words": 55,
                 "tips": [
                     bi("One sentence per paragraph, four lines in total.",
                        "یک جمله برای هر پاراگراف، در کل چهار خط."),
                     bi("Paraphrase: change the verb and the order, not just "
                        "one word.",
                        "بازنویسی کن: فعل و ترتیب را عوض کن، نه فقط یک کلمه."),
                     bi("Each sentence should be something a reader could "
                        "disagree with.",
                        "هر جمله باید چیزی باشد که خواننده بتواند با آن مخالفت "
                        "کند.")],
                 "model": bi("First, a very small wood can be built from local "
                             "trees in a few decades rather than centuries. "
                             "Second, the strongest argument for them is that "
                             "they noticeably cool the streets around them. "
                             "Third, they also protect drains by soaking up storm "
                             "water. Fourth, they work only when someone pays "
                             "for their first years, and their upkeep becomes "
                             "easier as they grow.",
                             "اول، یک جنگل بسیار کوچک را می‌توان در چند دهه، نه چند "
                             "قرن، از درختان محلی ساخت. دوم، قوی‌ترین دلیل برای آن‌ها "
                             "این است که خیابان‌های اطراف را به‌طور محسوس خنک "
                             "می‌کنند. سوم، با جذب آب طوفان از فاضلاب هم محافظت "
                             "می‌کنند. چهارم، فقط وقتی کار می‌کنند که کسی هزینهٔ "
                             "سال‌های اول را بدهد، و با رشدشان نگهداری آسان‌تر "
                             "می‌شود.")},
                {"prompt": bi("The passage's title is a size, not an idea. "
                              "Suggest a better title of no more than six words "
                              "and explain in two sentences why it is more "
                              "accurate.",
                              "عنوان متن یک اندازه است، نه یک ایده. عنوان بهتری در "
                              "حداکثر شش کلمه پیشنهاد بده و در دو جمله توضیح بده چرا "
                              "دقیق‌تر است."),
                 "min_words": 45,
                 "tips": [
                     bi("A title should carry the main idea, not the "
                        "measurement.",
                        "عنوان باید ایدهٔ اصلی را حمل کند، نه اندازه را."),
                     bi("Keep it under six words - that is part of the task.",
                        "زیر شش کلمه نگهش دار؛ این بخشی از تمرین است."),
                     bi("Say what your title adds that the old one leaves out.",
                        "بگو عنوان تو چه چیزی را اضافه می‌کند که عنوان قبلی جا "
                        "انداخته.")],
                 "model": bi("'Small Woods That Cool Whole Streets'. The "
                             "original title gives the size of the forest, "
                             "which is a detail, and says nothing about why "
                             "anyone would plant one. A title that names the "
                             "effect points the reader at the argument the "
                             "passage actually makes, and the last paragraph's "
                             "limits then read as a qualification of that "
                             "claim.",
                             "«جنگل‌های کوچکی که کل خیابان را خنک می‌کنند». عنوان "
                             "اصلی اندازهٔ جنگل را می‌دهد که جزئیات است و نمی‌گوید "
                             "چرا کسی باید یکی بکارد. عنوانی که نتیجه را نام می‌برد، "
                             "خواننده را به همان استدلالی می‌برد که متن واقعاً می‌سازد، "
                             "و آن‌وقت محدودیت‌های پاراگراف آخر به‌عنوان قید همان "
                             "ادعا خوانده می‌شوند.")},
            ],
        },
    },
    {
        "id": "summarize",
        "icon": "📝",
        "level": "B2",
        "minutes": 9,
        "title": bi("Summarise and paraphrase without copying",
                    "خلاصه کردن و بازنویسی بدون کپی کردن"),
        "blurb": bi(
            "If your summary could have been written without the text, you "
            "have not read it yet.",
            "اگر خلاصه‌ات را می‌شد بدون خواندن متن نوشت، هنوز نخوانده‌ای."),
        "what": bi(
            "A paraphrase restates one sentence at roughly the same length, "
            "with new words: same meaning, different surface. A summary "
            "compresses a whole text and keeps only what a reader who has not "
            "seen it needs: the central claim, the two or three supports that "
            "carry it, and the limit the writer admits. The two skills "
            "combine. You paraphrase sentence by sentence, then throw away "
            "every sentence that only supports another one, which is how a "
            "four-hundred-word article becomes sixty words that still say "
            "something a reader could argue with.",
            "بازنویسی (paraphrase) یک جمله را با همان طول تقریبی و واژه‌های تازه "
            "بیان می‌کند: همان معنی، سطحی متفاوت. خلاصه (summary) کل متن را "
            "فشرده می‌کند و فقط چیزی را نگه می‌دارد که خوانندهٔ ناآشنا لازم دارد: "
            "ادعای مرکزی، دو یا سه پشتوانه‌ای که آن را حمل می‌کنند، و محدودیتی "
            "که نویسنده می‌پذیرد. این دو مهارت با هم کار می‌کنند. جمله‌به‌جمله "
            "بازنویسی می‌کنی، بعد هر جمله‌ای را که فقط پشتیبان جملهٔ دیگری است "
            "دور می‌ریزی؛ این‌طور یک مقالهٔ چهارصد کلمه‌ای شصت کلمه می‌شود که هنوز "
            "چیزی می‌گوید که کسی می‌تواند با آن مخالفت کند."),
        "why": bi(
            "Summarising is how you find out whether you understood. A reader "
            "who can only repeat the sentences has stored the words, not the "
            "argument. It is also the skill most examined: summary questions, "
            "note-completion, 'which sentence best expresses...' and every "
            "academic task you will meet later are the same operation in "
            "different clothes.",
            "خلاصه کردن راهی است که می‌فهمی آیا فهمیدی یا نه. خواننده‌ای که فقط "
            "می‌تواند جمله‌ها را تکرار کند، واژه‌ها را ذخیره کرده، نه استدلال را. "
            "همچنین این مهارت بیشترین کاربرد امتحانی را دارد: سؤال خلاصه، تکمیل "
            "یادداشت، «کدام جمله بهتر بیان می‌کند...» و هر تکلیف دانشگاهی بعدی، "
            "همان عملیات با لباس دیگری است."),
        "when": bi(
            "After a careful read, not during it - and whenever you need notes "
            "you can actually revise from, or have to use a source without "
            "copying its words.",
            "بعد از خواندن دقیق، نه در حین آن؛ و هر وقت یادداشتی می‌خواهی که واقعاً "
            "بشود از آن مرور کرد، یا باید از منبعی استفاده کنی بدون کپی کردن "
            "واژه‌هایش."),
        "steps": [
            bi("Write the main idea of the text in one sentence, closed book. "
               "That sentence is the spine of the summary.",
               "با کتاب بسته، ایدهٔ اصلی متن را در یک جمله بنویس. همان جمله ستون "
               "فقرات خلاصه است."),
            bi("List the two or three points that would be lost without the "
               "text. Two is usually enough; five is a rewrite.",
               "دو یا سه نکته‌ای را که بدون متن از دست می‌رفت فهرست کن. دو تا "
               "معمولاً کافی است؛ پنج تا یعنی بازنویسی."),
            bi("Change the grammar, not just the vocabulary: a noun becomes a "
               "verb, active becomes passive, two short sentences become one.",
               "گرامر را عوض کن، نه فقط واژه‌ها را: اسم فعل شود، معلوم مجهول، دو "
               "جملهٔ کوتاه یکی."),
            bi("Compare with the original for copied phrases of four words or "
               "more, and rewrite any you find.",
               "با متن اصلی مقایسه کن و هر عبارت چهارکلمه‌ای یا بیشترِ کپی‌شده را "
               "بازنویسی کن."),
            bi("Check the length and the meaning: shorter than the original, "
               "and no fact added that the writer did not say.",
               "طول و معنی را بسنج: کوتاه‌تر از متن اصلی، و بدون هیچ واقعیتی که "
               "نویسنده نگفته."),
        ],
        "example": {
            "text": "The city's bike scheme lost money for six years. Last "
                    "spring the council stopped replacing stolen bikes and "
                    "began charging visitors a small daily fee instead. Use "
                    "doubled within a season, and for the first time the "
                    "scheme covered its own repairs.",
            "steps": [
                bi("Spine: a failing bike scheme became self-funding after two "
                   "changes.",
                   "ستون فقرات: یک طرح دوچرخهٔ زیان‌ده بعد از دو تغییر خودکفا شد."),
                bi("Keep the two changes, drop the six years of losses - that "
                   "is background, not information.",
                   "دو تغییر را نگه دار و شش سال ضرر را بریز - آن زمینه است، نه "
                   "اطلاع."),
                bi("Summary: 'A city bike scheme that had lost money for years "
                   "became self-funding within one season after the council "
                   "stopped replacing stolen bikes and started charging "
                   "visitors a daily fee.' Two sentences became one; nothing "
                   "was added.",
                   "خلاصه: «طرح دوچرخهٔ شهری که سال‌ها ضرر می‌داد، پس از اینکه "
                   "شورا جایگزینی دوچرخه‌های دزدی را متوقف کرد و از گردشگران "
                   "هزینهٔ روزانه گرفت، در یک فصل خودکفا شد.» دو جمله یکی شد و "
                   "چیزی اضافه نشد."),
            ],
        },
        "mistakes": [
            bi("Copying the topic sentences in order and calling it a summary. "
               "That is a quotation with the details removed.",
               "کپی کردن جمله‌های موضوع به ترتیب و اسمش را خلاصه گذاشتن. این یک "
               "نقل‌قول است که جزئیاتش حذف شده."),
            bi("Swapping synonyms one at a time ('big' → 'large') and thinking "
               "the sentence is now your own.",
               "عوض کردن مترادف‌ها یکی‌یکی (بزرگ → وسیع) و فکر کردن اینکه جمله "
               "حالا مال خودت است."),
            bi("Adding your opinion. A summary reports the writer's claim, "
               "including the limits the writer admits.",
               "افزودن نظر خودت. خلاصه ادعای نویسنده را گزارش می‌کند، همراه با "
               "محدودیت‌هایی که خودش می‌پذیرد."),
        ],
        "tips": [
            bi("Aim for a quarter of the original for an exam summary, or one "
               "sentence for a paragraph.",
               "برای خلاصهٔ امتحانی یک‌چهارم متن اصلی را هدف بگیر، یا یک جمله برای "
               "هر پاراگراف."),
            bi("If a phrase feels easy to write, it is probably the original's. "
               "The awkward version is usually yours.",
               "اگر عبارتی راحت نوشته می‌شود، احتمالاً از خود متن است. نسخهٔ "
               "ناهموار معمولاً مال خودت است."),
        ],
        "checklist": [
            bi("Spine sentence written with the text closed.",
               "نوشتن جملهٔ ستون فقرات با متن بسته."),
            bi("Two or three supports kept, rest dropped.",
               "نگه داشتن دو یا سه پشتوانه و حذف بقیه."),
            bi("Grammar changed, not only vocabulary.",
               "تغییر گرامر، نه فقط واژگان."),
            bi("No copied run of four words.",
               "هیچ رشتهٔ چهارکلمه‌ای کپی‌شده نداشتن."),
            bi("Nothing added that the writer did not claim.",
               "چیزی اضافه نشده که نویسنده نگفته باشد."),
        ],
        "reading": {
            "title": bi("The four-day week: what the trial showed and what it "
                         "did not",
                         "هفتهٔ چهارروزه: آزمون چه نشان داد و چه نشان نداد"),
            "level": "B2",
            "genre": bi("Analysis / report", "تحلیل / گزارش"),
            "paragraphs": [
                "In 2022, 61 British companies took part in a trial of a "
                "four-day week that lasted six months. Staff worked four days "
                "instead of five "
                "and kept their full pay. The trial was organised by a "
                "research group and a campaign organisation, and the companies "
                "chose to join - a fact worth remembering when you read the "
                "results.",
                "For most firms the results were better than expected. Revenue "
                "stayed flat or rose in almost all of them, the number of "
                "resignations fell sharply, and sick days dropped. Managers "
                "reported that the hardest part was not the missing day but "
                "the meetings they had to cancel to pay for it.",
                "The caveats matter as much as the numbers. Sixty-one "
                "companies is a small sample, and volunteers are never a random "
                "sample: firms that expect a four-day week to fail do not "
                "apply. Most were office employers with control over their own "
                "hours, and the trial did not include hospitals, schools or "
                "shops, where cover has to be arranged hour by hour.",
                "How the participating firms paid for the fifth day is the most "
                "transferable finding. They shortened meetings, replaced many "
                "of them with written updates, and cut the time staff spent "
                "waiting for approvals. None of these changes requires a "
                "four-day week; any employer could try them tomorrow.",
            ],
            "summary": bi(
                "A voluntary six-month trial found stable revenue, fewer "
                "resignations and less sickness; its sample was small and "
                "office-based, and its most reusable lesson is that meetings "
                "and waiting time can be cut without changing the week at all.",
                "یک آزمون داوطلبانهٔ شش‌ماهه درآمد پایدار، استعفای کمتر و بیماری "
                "کمتر یافت؛ نمونه‌اش کوچک و اداری بود و قابل‌استفاده‌ترین درسش "
                "این است که می‌توان جلسه‌ها و زمان انتظار را بدون هیچ تغییری در "
                "هفته کم کرد."),
        },
        "questions": {
            "blanks": [
                {"sentence": "___ British companies joined the trial.",
                 "answer": "61", "also": ["sixty-one", "sixty one"],
                 "hint": bi("A number in the first line.",
                            "عددی در خط اول."),
                 "para": 1},
                {"sentence": "The trial lasted six ___.",
                 "answer": "months", "also": [],
                 "hint": bi("A unit of time.", "یک واحد زمان."),
                 "para": 1},
                {"sentence": "Revenue stayed flat or ___ in almost all of the "
                             "companies.",
                 "answer": "rose", "also": [],
                 "hint": bi("The opposite of 'fell'.", "متضاد fell."),
                 "para": 2},
                {"sentence": "Firms paid for the fifth day partly by shortening "
                             "___.",
                 "answer": "meetings", "also": [],
                 "hint": bi("What managers had to cancel.",
                            "چیزی که مدیران مجبور شدند لغو کنند."),
                 "para": 4},
            ],
            "mcq": [
                {"q": "What is the passage mainly about?",
                 "options": ["Why the four-day week is better for everyone",
                             "A trial's results, its limits, and what other "
                             "employers can copy",
                             "How to organise a meeting in less time",
                             "Why British companies are short of staff"],
                 "answer": 1,
                 "why": bi("The passage gives results, then caveats, then the "
                           "one transferable finding - and it never claims the "
                           "week works everywhere.",
                           "متن نتایج را می‌دهد، بعد قیدها، بعد تنها یافتهٔ قابل‌انتقال "
                           "- و هیچ‌جا ادعا نمی‌کند هفته همه‌جا کار می‌کند."),
                 "para": 4},
                {"q": "Which of these is given as a limitation of the trial?",
                 "options": ["Staff were paid less during the trial",
                             "The companies volunteered rather than being "
                             "chosen at random",
                             "The trial lasted only three months",
                             "Revenue fell in most firms"],
                 "answer": 1,
                 "why": bi("'Volunteers are never a random sample: firms that "
                           "expect a four-day week to fail do not apply.' Pay "
                           "was full and the term was six months, both stated as "
                           "facts.",
                           "«داوطلبان هرگز نمونهٔ تصادفی نیستند: شرکت‌هایی که انتظار "
                           "شکست دارند درخواست نمی‌دهند.» دستمزد کامل بود و مدت شش "
                           "ماه، که هر دو واقعیت‌اند."),
                 "para": 3},
                {"q": "According to the second paragraph, what was hardest for "
                       "managers?",
                 "options": ["Filling the fifth day with work",
                             "Cancelling the meetings that paid for the missing "
                             "day",
                             "Recruiting new staff",
                             "Measuring revenue"],
                 "answer": 1,
                 "why": bi("'The hardest part was not the missing day but the "
                           "meetings they had to cancel to pay for it.' The "
                           "sentence is built on a contrast, so the first half "
                           "is the trap.",
                           "«سخت‌ترین بخش روز غایب نبود، بلکه جلسه‌هایی بود که باید "
                           "لغو می‌کردند تا هزینه‌اش را بدهند.» جمله بر یک تضاد "
                           "ساخته شده، پس نیمهٔ اول تله است."),
                 "para": 2},
                {"q": "Which finding does the writer call most transferable?",
                 "options": ["Full pay can be kept on four days",
                             "Sick days fall when the week is shorter",
                             "Cutting meetings and waiting time works without "
                             "a four-day week",
                             "Small samples are unreliable"],
                 "answer": 2,
                 "why": bi("The last paragraph says exactly that, and ends with "
                           "'any employer could try them tomorrow'.",
                           "پاراگراف آخر دقیقاً همین را می‌گوید و با «هر کارفرمایی "
                           "می‌تواند فردا امتحانشان کند» تمام می‌شود."),
                 "para": 4},
            ],
            "truefalse": [
                {"statement": "Staff kept their full pay during the trial.",
                 "answer": True,
                 "why": bi("'Staff worked four days instead of five and kept "
                           "their full pay.'",
                           "«کارکنان چهار روز کار کردند و دستمزد کامل گرفتند.»"),
                 "para": 1},
                {"statement": "Sick days rose during the trial.",
                 "answer": False,
                 "why": bi("They 'dropped', and the number of resignations fell "
                           "as well.",
                           "«کم شد»، و تعداد استعفاها هم پایین آمد."),
                 "para": 2},
                {"statement": "Hospitals and schools took part in the trial.",
                 "answer": False,
                 "why": bi("'The trial did not include hospitals, schools or "
                           "shops'.",
                           "«آزمون شامل بیمارستان‌ها، مدرسه‌ها یا مغازه‌ها نبود»."),
                 "para": 3},
                {"statement": "Some of the changes could be tried without "
                              "shortening the week.",
                 "answer": True,
                 "why": bi("'None of these changes requires a four-day week; "
                           "any employer could try them tomorrow.'",
                           "«هیچ‌کدام از این تغییرها به هفتهٔ چهارروزه نیاز ندارد؛ هر "
                           "کارفرمایی می‌تواند فردا امتحانشان کند.»"),
                 "para": 4},
            ],
            "essay": [
                {"prompt": bi("Write a summary of the passage in 45-70 words. "
                              "Keep the result, the main limitation and the "
                              "transferable finding, and use your own words.",
                              "خلاصه‌ای از متن در ۴۵ تا ۷۰ کلمه بنویس. نتیجه، "
                              "محدودیت اصلی و یافتهٔ قابل‌انتقال را نگه دار و از "
                              "واژه‌های خودت استفاده کن."),
                 "min_words": 45,
                 "tips": [
                     bi("One sentence for the result, one for the caveat, "
                        "one for the finding.",
                        "یک جمله برای نتیجه، یکی برای قید، و یکی برای یافته."),
                     bi("Say 'about 60 firms', not the exact figure - a "
                        "summary rounds.",
                        "بگو «حدود ۶۰ شرکت»، نه رقم دقیق؛ خلاصه گرد می‌کند."),
                     bi("Do not evaluate. Save your opinion for another "
                        "paragraph.",
                        "ارزیابی نکن. نظرت را برای پاراگراف دیگری نگه دار.")],
                 "model": bi("A six-month British trial of a four-day week, "
                             "involving about sixty companies, found stable or "
                             "rising revenue, fewer resignations and less "
                             "sickness while pay stayed the same. The sample was "
                             "small and entirely voluntary, and it covered office "
                             "work rather than hospitals or shops. The most "
                             "portable lesson is that shorter meetings and less "
                             "waiting for approvals help any employer, with or "
                             "without a shorter week. (70 words)",
                             "یک آزمون شش‌ماههٔ بریتانیایی برای هفتهٔ چهارروزه با حدود "
                             "شصت شرکت، درآمد پایدار یا رو‌به‌رشد، استعفای کمتر و "
                             "بیماری کمتر یافت، در حالی که دستمزد ثابت بود. نمونه "
                             "کوچک و کاملاً داوطلبانه بود و کار اداری را پوشش می‌داد، "
                             "نه بیمارستان و مغازه. قابل‌انتقال‌ترین درس این است که "
                             "جلسه‌های کوتاه‌تر و انتظار کمتر برای تأییدها به هر "
                             "کارفرمایی کمک می‌کند، با هفتهٔ کوتاه‌تر یا بدون آن. "
                             "(۷۰ کلمه)")},
                {"prompt": bi("Paraphrase this sentence in one sentence of your "
                              "own: 'Firms that expect a four-day week to fail "
                              "do not apply.' Then explain in two sentences why a "
                              "paraphrase is not a summary.",
                              "این جمله را در یک جملهٔ خودت بازنویسی کن: «شرکت‌هایی "
                              "که انتظار شکست هفتهٔ چهارروزه را دارند درخواست "
                              "نمی‌دهند.» بعد در دو جمله توضیح بده چرا بازنویسی با "
                              "خلاصه یکی نیست."),
                 "min_words": 55,
                 "tips": [
                     bi("Keep the logic (only firms that expect success join) "
                        "and change the structure.",
                        "منطق را نگه دار (فقط شرکت‌هایی که انتظار موفقیت دارند "
                        "می‌پیوندند) و ساختار را عوض کن."),
                     bi("No run of four copied words.",
                        "هیچ رشتهٔ چهارکلمه‌ای کپی نشود."),
                     bi("Then state the difference in length and scope, not in "
                        "quality.",
                        "بعد تفاوت را در طول و گستره بگو، نه در کیفیت.")],
                 "model": bi("Only employers who already believe the shorter "
                             "week will work choose to enter such a trial, so "
                             "the group is not representative. A paraphrase "
                             "keeps the length and the single idea of one "
                             "sentence, reworded. A summary covers a whole text "
                             "and is deliberately much shorter, keeping only the "
                             "points a new reader needs.",
                             "فقط کارفرمایانی که از پیش باور دارند هفتهٔ کوتاه‌تر کار "
                             "می‌کند در چنین آزمونی شرکت می‌کنند، پس این گروه "
                             "نماینده نیست. بازنویسی طول و ایدهٔ یک جمله را نگه "
                             "می‌دارد و واژه‌ها را عوض می‌کند. خلاصه کل یک متن را "
                             "پوشش می‌دهد و عمداً بسیار کوتاه‌تر است و فقط نکته‌هایی "
                             "را نگه می‌دارد که خوانندهٔ تازه لازم دارد.")},
            ],
        },
    },
]


# The order a learner should meet the strategies in: survey before reading at
# all, summary last because it needs everything above it.
ORDER = [
    "survey", "skim", "scan", "detail", "context",
    "reference", "inference", "mainidea", "signposts", "summarize",
]


# The rest of each lesson for the strategies written before the lesson had
# these sections. Keyed by strategy id and merged by tools/build_reading.py.
EXTRAS = {
    "skim": {
        "minutes": 7,
        "when": bi(
            "You have two minutes to decide whether a text is worth reading: an "
            "exam passage, a news article, an email thread with forty replies.",
            "دو دقیقه وقت داری تصمیم بگیری آیا یک متن ارزش خواندن دارد یا نه: "
            "متن امتحان، یک خبر، یا زنجیرهٔ ایمیلی با چهل جواب."),
        "example": {
            "text": "Pontevedra banned cars from its centre in 1999. Shop "
                    "owners expected to lose customers. Instead, sales rose, "
                    "because people who walk stop and look in windows. Twenty "
                    "years later the centre has no traffic and no empty shops. "
                    "Other cities have come to copy the model, but few have "
                    "banned cars outright: the political cost is too high. The "
                    "mayor says the trick was never calling it a ban on cars.",
            "steps": [
                bi("Read only the first sentence of each paragraph. Banned in "
                   "1999 · shops expected losses · sales rose · other cities "
                   "hesitate · what did the mayor call it.",
                   "فقط جملهٔ اول هر پاراگراف را بخوان: ممنوعیت در ۱۹۹۹ · انتظار "
                   "ضرر · افزایش فروش · تردید شهرهای دیگر · شهردار چه نامی "
                   "گذاشت."),
                bi("The last sentence gives the writer's point: the policy "
                   "worked because it was framed as something else.",
                   "جملهٔ آخر نظر نویسنده را می‌دهد: سیاست موفق شد چون جور دیگری "
                   "معرفی شد."),
                bi("Say it in one line - 'how a small city took cars out of the "
                   "centre and made its shops busier' - and only then read it "
                   "properly.",
                   "در یک خط بگو: «چگونه یک شهر کوچک ماشین‌ها را از مرکز بیرون "
                   "کرد و مغازه‌ها را پرتر کرد»؛ و تنها بعد از آن کامل بخوان."),
            ],
        },
        "mistakes": [
            bi("Skimming the first sentences and then reading every word "
               "anyway. That is reading slowly with extra steps.",
               "جمله‌های اول را سریع خواندن و بعد با این حال کلمه‌به‌کلمه خواندن. "
               "این همان خواندن کند است با چند قدم اضافه."),
            bi("Skipping the last paragraph. It is where the writer usually "
               "says what they actually think.",
               "رد کردن پاراگراف آخر؛ همان‌جایی که نویسنده معمولاً نظر واقعی‌اش "
               "را می‌گوید."),
            bi("Answering with the topic instead of the idea: 'cars' is the "
               "topic, 'a city that removed them and improved' is the idea.",
               "جواب دادن با موضوع به‌جای ایده: «ماشین» موضوع است؛ «شهری که "
               "ماشین‌ها را برد و بهتر شد» ایده است."),
        ],
        "tips": [
            bi("Time it. Sixty seconds, then say the idea out loud before you "
               "look at anything else.",
               "زمان بگیر. شصت ثانیه، بعد پیش از هر چیز دیگری ایده را بلند بگو."),
            bi("Trust the first sentence less than the last one when the two "
               "disagree.",
               "وقتی جملهٔ اول و آخر با هم نمی‌سازند، به جملهٔ آخر بیشتر اعتماد "
               "کن."),
        ],
        "checklist": [
            bi("Title, first line, first sentence of each paragraph, last "
               "paragraph.",
               "عنوان، خط اول، جملهٔ اول هر پاراگراف، پاراگراف آخر."),
            bi("One sentence in your own words before the careful read.",
               "یک جمله با کلمات خودت پیش از خواندن دقیق."),
            bi("Topic named separately from the main idea.",
               "تفکیک موضوع از ایدهٔ اصلی."),
        ],
    },
    "scan": {
        "minutes": 6,
        "when": bi(
            "A question names a year, a price or a person, and the answer is "
            "somewhere on the page but you have no time to read all of it.",
            "سؤالی یک سال، یک قیمت یا یک نام را می‌آورد و جواب جایی در صفحه "
            "است، ولی وقت نداری همه‌اش را بخوانی."),
        "example": {
            "text": "The bridge opened in March 2018 after four years of work "
                    "and cost 61 million euros. Its designer, Elena Ferraro, "
                    "had proposed a cheaper wooden version in 2011, which the "
                    "council rejected twice. The current span is 240 metres, "
                    "the longest in the region, and carries 19,000 vehicles a "
                    "day. Repairs in 2023 closed it for eleven weeks.",
            "steps": [
                bi("Underline the target first: 'eleven weeks' means you are "
                   "hunting a duration, and durations sit next to 'for', "
                   "'since' or a number plus a unit.",
                   "اول هدف را خط بکش: «یازده هفته» یعنی دنبال یک مدت زمانی؛ و "
                   "مدت‌ها کنار for، since یا یک عدد و واحد می‌آیند."),
                bi("Sweep down the numbers column instead of reading: 2018, 61, "
                   "2011, 240, 19,000, 2023 - the last one is followed by "
                   "'closed it for eleven weeks'.",
                   "به‌جای خواندن، ستون عددها را پایین برو: ۲۰۱۸، ۶۱، ۲۰۱۱، ۲۴۰، "
                   "۱۹٬۰۰۰، ۲۰۲۳؛ عدد آخر با «closed it for eleven weeks» "
                   "می‌آید."),
                bi("Read that sentence in full before answering: the question "
                   "was about repairs, and the number alone does not say what "
                   "was closed.",
                   "پیش از جواب دادن، آن جمله را کامل بخوان: سؤال دربارهٔ تعمیرات "
                   "بود و عدد تنها نمی‌گوید چه چیزی بسته شد."),
            ],
        },
        "mistakes": [
            bi("Scanning for the exact words of the question. A text says "
               "'eleven weeks'; the question says 'how long'.",
               "جست‌وجوی عین کلمه‌های سؤال. متن می‌گوید eleven weeks و سؤال "
               "می‌پرسد how long."),
            bi("Stopping at the first number that fits. Bridges cost money and "
               "open in years, and both look alike at speed.",
               "توقف روی اولین عددی که جور درمی‌آید. پول و سال هر دو شبیه هم‌اند "
               "وقتی سریع نگاه می‌کنی."),
        ],
        "tips": [
            bi("Say what shape the answer has before you look: a date, a "
               "number with a unit, a name in capitals.",
               "پیش از نگاه کردن بگو جواب چه شکلی است: تاریخ، عدد با واحد، یا "
               "نامی با حرف بزرگ."),
            bi("Scan a narrow column, not the whole width - the eye finds "
               "digits faster in a strip.",
               "یک ستون باریک را بگرد، نه تمام عرض را؛ چشم در یک نوار باریک "
               "رقم‌ها را سریع‌تر پیدا می‌کند."),
        ],
        "checklist": [
            bi("Target named as a shape, not a paraphrase.",
               "هدف را به شکل یک قالب نام ببر، نه با بازنویسی."),
            bi("Zigzag sweep, digits and capitals as landmarks.",
               "جاروب زیگزاگ، با رقم‌ها و حروف بزرگ به‌عنوان نشانه."),
            bi("The whole sentence read before the answer is written.",
               "خواندن کل جمله پیش از نوشتن جواب."),
        ],
    },
    "context": {
        "minutes": 8,
        "when": bi(
            "You meet an unfamiliar word in a text you otherwise follow, and "
            "stopping now would cost you the paragraph.",
            "به واژه‌ای ناشناس می‌رسی در متنی که بقیه‌اش را می‌فهمی، و توقف در "
            "همین نقطه پاراگراف را از دستت می‌برد."),
        "example": {
            "text": "The village shop was failing. Then the owner began to "
                    "stock small, cheap things people forget at the "
                    "supermarket - a single battery, one candle, half a loaf - "
                    "and trade began to burgeon. Within a year she had hired "
                    "two assistants and opened a second till.",
            "steps": [
                bi("'Burgeon' is unknown, but the sentence after it is the "
                   "proof: two assistants and a second till mean the trade "
                   "grew.",
                   "«burgeon» را نمی‌دانی، ولی جملهٔ بعد شاهدش است: دو کارمند و "
                   "صندوق دوم یعنی فروش رشد کرد."),
                bi("Test the guess by substitution: 'trade began to grow' fits "
                   "the cause (small things people forget) and the result "
                   "(hiring).",
                   "حدس را با جای‌گذاری بسنج: «فروش شروع کرد به رشد» هم با علت "
                   "جور است هم با نتیجه (استخدام)."),
                bi("Note the shape: burgeon is a verb of growth, so it can be "
                   "reused for cities, costs and interest rates.",
                   "شکل واژه را یادداشت کن: burgeon فعل رشد است و برای شهر، هزینه "
                   "و نرخ بهره هم به کار می‌رود."),
            ],
        },
        "mistakes": [
            bi("Using only the word's shape: 'burgeon' looks like 'burger', "
               "and guessing from sound is how false friends are born.",
               "فقط از شکل واژه حدس زدن: burgeon شبیه burger است، و حدس از روی "
               "صدا همان جایی است که دوستان نادرست به دنیا می‌آیند."),
            bi("Deciding that a guess is wrong because the dictionary gives a "
               "different word. 'Grow' is not the translation; it is enough.",
               "غلط دانستن حدس چون فرهنگ لغت واژهٔ دیگری می‌دهد. «رشد کردن» "
               "ترجمهٔ دقیق نیست، اما کافی است."),
        ],
        "tips": [
            bi("Guess a part of speech first - noun, verb, adjective - because "
               "that alone fixes half the meaning.",
               "اول نقش دستوری را حدس بزن: اسم، فعل، صفت؛ همین نصف معنی را "
               "مشخص می‌کند."),
            bi("Write the word on a card with the sentence, not the "
               "translation. The sentence is what will bring it back.",
               "واژه را با همان جمله روی کارت بنویس، نه با ترجمه؛ همان جمله "
               "است که آن را برمی‌گرداند."),
        ],
        "checklist": [
            bi("Word class guessed before meaning.",
               "حدس نقش دستوری پیش از معنی."),
            bi("One of the four signals found: definition, example, "
               "opposite, result.",
               "پیدا کردن یکی از چهار نشانه: تعریف، مثال، متضاد، نتیجه."),
            bi("Guess substituted into the sentence and checked.",
               "جای‌گذاری حدس در جمله و سنجیدنش."),
            bi("Dictionary opened only after the third meeting.",
               "باز کردن فرهنگ لغت فقط بعد از سومین برخورد."),
        ],
    },
    "reference": {
        "minutes": 6,
        "when": bi(
            "A paragraph stops making sense although you know every word in "
            "it. Nine times out of ten a pronoun is pointing at the wrong "
            "noun.",
            "پاراگرافی بی‌معنی می‌شود هرچند همهٔ کلمه‌هایش را می‌دانی. نه بار از "
            "ده بار یک ضمیر به اسم اشتباهی اشاره می‌کند."),
        "example": {
            "text": "The council voted to close the market on Sundays. This "
                    "surprised nobody who had seen the empty stalls, but it "
                    "angered the traders, who had asked for a later opening "
                    "instead. They collected 4,000 signatures in a week.",
            "steps": [
                bi("'This' is not 'Sundays' and not 'the market': it stands for "
                   "the whole decision in the first sentence.",
                   "«This» نه «یکشنبه‌ها» است و نه «بازار»: به کل تصمیم جملهٔ "
                   "اول برمی‌گردد."),
                bi("'They' comes after 'the traders', and the verb 'collected "
                   "signatures' only makes sense for the people who object.",
                   "«They» بعد از «the traders» می‌آید و فعل «امضا جمع کردند» فقط "
                   "برای معترضان معنی می‌دهد."),
                bi("Replace each pronoun with its noun and read again: the "
                   "sentence now says who was surprised and who was angry, "
                   "which the pronouns were hiding.",
                   "هر ضمیر را با اسمش عوض کن و دوباره بخوان: حالا جمله می‌گوید "
                   "چه کسی تعجب کرد و چه کسی عصبانی شد؛ همان چیزی که ضمیرها "
                   "پنهانش کرده بودند."),
            ],
        },
        "mistakes": [
            bi("Attaching a pronoun to the nearest noun. Distance is not "
               "grammar; meaning is.",
               "چسباندن ضمیر به نزدیک‌ترین اسم. فاصله گرامر نیست؛ معنی است."),
            bi("Reading 'this' as one word instead of one sentence, which "
               "turns a comment on a policy into a comment on a weekday.",
               "خواندن this به‌عنوان یک کلمه و نه یک جمله؛ همین نظر دربارهٔ یک "
               "سیاست را به نظر دربارهٔ یک روز هفته تبدیل می‌کند."),
        ],
        "tips": [
            bi("Say the paragraph out loud with the nouns in place. Your ear "
               "catches the wrong referent faster than your eye.",
               "پاراگراف را با اسم‌ها بلند بخوان. گوش زودتر از چشم مرجع اشتباه "
               "را می‌گیرد."),
            bi("'Which' usually points at the whole clause before it, not at "
               "the last noun.",
               "«which» معمولاً به کل بند قبل برمی‌گردد، نه به آخرین اسم."),
        ],
        "checklist": [
            bi("Every pronoun circled before complaining that the text is "
               "unclear.",
               "دور زدن همهٔ ضمیرها پیش از شکایت از مبهم بودن متن."),
            bi("Noun substituted and the sentence re-read.",
               "جای‌گذاری اسم و خواندن دوبارهٔ جمله."),
            bi("'This' / 'that' read as a whole sentence, not a word.",
               "خواندن this و that به‌عنوان کل جمله، نه یک کلمه."),
        ],
    },
    "inference": {
        "minutes": 8,
        "when": bi(
            "The question asks how someone felt, what they intended, or what "
            "can be concluded - and the answer is nowhere in the words.",
            "سؤال می‌پرسد کسی چه حسی داشت، چه قصدی داشت، یا چه می‌توان نتیجه "
            "گرفت؛ و جواب در هیچ کلمه‌ای نیست."),
        "example": {
            "text": "My father read the letter twice, folded it along the "
                    "same crease, and put it back in the envelope. 'Good "
                    "news?' my mother asked. 'They want an answer by Friday,' "
                    "he said, and went to make tea.",
            "steps": [
                bi("Notice what is missing: he never answers the question, "
                   "and the deadline is the only fact he offers.",
                   "به آنچه نیست توجه کن: او به سؤال جواب نمی‌دهد و تنها واقعیتی "
                   "که می‌گوید مهلت است."),
                bi("Two details point the same way - reading it twice, and "
                   "folding it along the same crease - which suggests the "
                   "news is not simple.",
                   "دو جزئیات به یک جهت اشاره می‌کنند: دو بار خواندن و تا کردن "
                   "روی همان خط قبلی؛ یعنی خبر ساده نیست."),
                bi("Make the smallest claim the evidence supports: he is "
                   "worried. Not 'he lost his job' - the passage does not say "
                   "that, and an inference is not a guess.",
                   "کوچک‌ترین ادعایی را بکن که شواهد پشتیبانی می‌کند: نگران است. "
                   "نه «کارش را از دست داد»؛ متن این را نمی‌گوید و استنتاج حدس "
                   "نیست."),
            ],
        },
        "mistakes": [
            bi("Choosing the option that repeats the passage's words. An "
               "inference question almost never has a quoted answer.",
               "انتخاب گزینه‌ای که کلمه‌های متن را تکرار می‌کند. سؤال استنتاج "
               "تقریباً هیچ‌وقت جواب نقل‌قولی ندارد."),
            bi("Going one step further than the text allows - inventing a "
               "cause (a lost job, an illness) instead of describing the "
               "feeling.",
               "یک قدم جلوتر از متن رفتن: ساختن علت (اخراج، بیماری) به‌جای "
               "توصیف احساس."),
        ],
        "tips": [
            bi("Answer first, then find two details that support it. Reading "
               "the options first is how the plausible wrong one gets chosen.",
               "اول جواب بده، بعد دو جزئیات برای پشتیبانی‌اش پیدا کن. خواندن "
               "گزینه‌ها از اول، همان راهی است که گزینهٔ غلطِ قابل‌قبول انتخاب "
               "می‌شود."),
            bi("Keep the claim small. 'He is worried' is defensible; 'he is "
               "angry with his wife' needs evidence the passage does not "
               "give.",
               "ادعا را کوچک نگه دار. «نگران است» قابل دفاع است؛ «از همسرش "
               "عصبانی است» شواهدی می‌خواهد که متن نمی‌دهد."),
        ],
        "checklist": [
            bi("Own answer written before the options are read.",
               "نوشتن جواب خودت پیش از خواندن گزینه‌ها."),
            bi("Two details found that point the same way.",
               "پیدا کردن دو جزئیات که به یک جهت اشاره می‌کنند."),
            bi("The claim is the smallest one the evidence allows.",
               "کوچک‌ترین ادعایی که شواهد اجازه می‌دهد."),
        ],
    },
    "signposts": {
        "minutes": 7,
        "when": bi(
            "You are reading an article, a report or an exam text and you can "
            "follow every sentence but not the argument.",
            "مقاله، گزارش یا متن امتحانی می‌خوانی و هر جمله را می‌فهمی ولی "
            "استدلال را نه."),
        "example": {
            "text": "Remote work raises productivity. However, the studies "
                    "that show this were mostly done with experienced staff. "
                    "For example, one trial found a 13 per cent gain among "
                    "engineers with five years' experience. Consequently, the "
                    "result may not travel to a first job.",
            "steps": [
                bi("Three signposts, three jobs: however limits the first "
                   "claim, for example supports the limit, consequently draws "
                   "the conclusion.",
                   "سه نشانه، سه کار: however ادعای اول را محدود می‌کند، for "
                   "example آن محدودیت را پشتیبانی می‌کند، consequently نتیجه "
                   "را می‌گیرد."),
                bi("Predict before reading: after 'however' the writer must "
                   "qualify the good news, so the next sentence should say "
                   "under what conditions it holds.",
                   "پیش از خواندن پیش‌بینی کن: بعد از however نویسنده باید خبر خوب "
                   "را مشروط کند، پس جملهٔ بعد باید بگوید تحت چه شرطی درست است."),
                bi("Read only the signposts in order and you already have the "
                   "argument: claim, limit, evidence, conclusion.",
                   "فقط نشانه‌ها را به ترتیب بخوان و استدلال را داری: ادعا، "
                   "محدودیت، شاهد، نتیجه."),
            ],
        },
        "mistakes": [
            bi("Treating 'however' as decoration. It usually marks the "
               "sentence the writer actually believes.",
               "تزئینی دانستن however. این واژه معمولاً جمله‌ای را نشان می‌دهد "
               "که نویسنده واقعاً باورش دارد."),
            bi("Reading 'for example' as new information. It is evidence for "
               "the sentence before it.",
               "خواندن for example به‌عنوان اطلاعات تازه. این عبارت شاهد جملهٔ "
               "قبل است."),
        ],
        "tips": [
            bi("Learn them in families: contrast (however, yet, although), "
               "cause (because, therefore), example (for instance, such as), "
               "limit (unless, except).",
               "آن‌ها را خانوادگی یاد بگیر: تضاد (however، yet، although)، علت "
               "(because، therefore)، مثال (for instance، such as)، محدودیت "
               "(unless، except)."),
            bi("A paragraph that opens with a signpost is telling you how to "
               "read it. Use the first word before the first sentence.",
               "پاراگرافی که با یک نشانه شروع می‌شود، می‌گوید چطور بخوانش. پیش از "
               "جملهٔ اول، کلمهٔ اول را ببین."),
        ],
        "checklist": [
            bi("Signposts underlined before answering anything.",
               "خط کشیدن زیر نشانه‌ها پیش از پاسخ دادن."),
            bi("Each one labelled: contrast, example, cause, result, limit.",
               "برچسب زدن به هر کدام: تضاد، مثال، علت، نتیجه، محدودیت."),
            bi("The last paragraph read for the writer's own position.",
               "خواندن پاراگراف آخر برای فهم موضع خود نویسنده."),
        ],
    },
}


# Which paragraph answers each of the questions whose explanation quotes the
# text loosely enough that the builder cannot find it on its own. Keys are the
# question's position in its group; a missing entry falls back to the builder's
# search, and to no reference at all rather than a wrong one.
EVIDENCE = {
    "skim": {
        "blanks": {2: 2},
        "mcq": {0: 4},
        "truefalse": {2: 1},
    },
    "scan": {
        "mcq": {1: 2, 2: 3, 3: 4},
        "truefalse": {2: 3, 3: 2},
    },
    "context": {
        "mcq": {0: 1, 2: 3, 3: 3},
        "truefalse": {2: 3, 3: 1},
    },
    "reference": {
        "blanks": {0: 1},
        "mcq": {0: 1, 1: 2, 2: 2, 3: 2},
        "truefalse": {1: 2, 3: 1},
    },
    "inference": {
        "blanks": {1: 1},
        "mcq": {1: 3, 3: 2},
        "truefalse": {1: 2, 2: 2},
    },
    "signposts": {
        "mcq": {0: 2, 2: 3},
        "truefalse": {0: 1, 1: 1, 2: 3, 3: 4},
    },
}
