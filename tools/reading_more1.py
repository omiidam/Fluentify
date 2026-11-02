"""Two further practices for skimming and scanning.

Written as a separate module so each batch of passages can be read on its own;
reading_src merges all of these into MORE at the bottom, after bi() exists.
"""
from reading_src import bi

MORE = {
    "skim": [
        {
            "title": bi("Forty minutes without cars", "چهل دقیقه بدون ماشین"),
            "level": "B1",
            "genre": bi("News feature", "گزارش خبری"),
            "paragraphs": [
                "At eight o'clock on a Tuesday, the road outside Hilltown's "
                "largest primary school has no cars on it. Since 2019 the "
                "street has been closed to traffic for forty minutes at the "
                "start and end of the school day. Parents walk, children "
                "cycle, and the crossing guard has much less to do.",
                "The first closures were small and unpopular with some "
                "shopkeepers, who feared losing deliveries and customers. That "
                "fear turned out to be mostly unfounded: a survey of sixty "
                "streets found that takings changed little, while the number "
                "of children walking to school rose by a third.",
                "The clearest gain is air. Monitoring on four streets "
                "recorded nitrogen dioxide falling by up to 24 per cent during "
                "the closure, and the improvement lasted into the afternoon. "
                "Noise fell too, although the council never measured it.",
                "School streets are not free. Each one needs signs, a camera "
                "or a volunteer at the barrier, and a council willing to "
                "enforce the rule. Hilltown now runs eleven, and its transport "
                "officer says the limit is staff time, not money.",
            ],
            "summary": bi(
                "A small daily road closure improves the school run and the "
                "air around it, at a cost measured in staff hours rather than "
                "cash.",
                "بستن روزانهٔ کوتاه یک خیابان، مسیر مدرسه و هوای اطرافش را بهتر "
                "می‌کند و هزینه‌اش با ساعت کارکنان سنجیده می‌شود، نه پول."),
            "questions": {
                "blanks": [
                    {"sentence": "The street is closed for ___ minutes at each "
                                 "end of the school day.",
                     "answer": "forty", "also": ["40"],
                     "hint": bi("A word in the first paragraph.",
                                "یک کلمه در پاراگراف اول."),
                     "para": 1},
                    {"sentence": "The number of children walking to school "
                                 "rose by a ___.",
                     "answer": "third", "also": [],
                     "hint": bi("A fraction, not a percentage.",
                                "یک کسر، نه درصد."),
                     "para": 2},
                    {"sentence": "Nitrogen dioxide fell by up to ___ per cent.",
                     "answer": "24", "also": [],
                     "hint": bi("A figure from the monitoring.",
                                "عددی از اندازه‌گیری‌ها."),
                     "para": 3},
                ],
                "mcq": [
                    {"q": "What is the passage mainly about?",
                     "options": ["How to drive safely near a school",
                                 "A daily road closure that works, and what it "
                                 "costs",
                                 "Why shopkeepers oppose the council",
                                 "The health effects of nitrogen dioxide"],
                     "answer": 1,
                     "why": bi("Each paragraph adds one thing: the scheme, the "
                               "shopkeepers, the gain, the cost. The last is "
                               "the limit, not the subject.",
                               "هر پاراگراف یک چیز اضافه می‌کند: طرح، مغازه‌داران، "
                               "سود، هزینه. پاراگراف آخر محدودیت است، نه "
                               "موضوع."),
                     "para": 1},
                    {"q": "What does the second paragraph do?",
                     "options": ["It describes the crossing guard's job",
                                 "It answers the objection the scheme first "
                                 "faced",
                                 "It gives the exact traffic figures",
                                 "It explains how to apply for a closure"],
                     "answer": 1,
                     "why": bi("It names the fear ('losing deliveries') and "
                               "then gives the survey that answers it.",
                               "اول ترس را نام می‌برد («از دست دادن تحویل») و بعد "
                               "نظرسنجی‌ای را می‌آورد که جوابش است."),
                     "para": 2},
                    {"q": "According to the last paragraph, what limits more "
                           "school streets?",
                     "options": ["The cost of signs", "Staff time",
                                 "The number of children", "Air quality"],
                     "answer": 1,
                     "why": bi("'The limit is staff time, not money' - the "
                               "writer rules out cost explicitly.",
                               "«محدودیت ساعت کارکنان است، نه پول»؛ نویسنده هزینه "
                               "را صریحاً رد می‌کند."),
                     "para": 4},
                ],
                "truefalse": [
                    {"statement": "Shopkeepers lost most of their takings.",
                     "answer": False,
                     "why": bi("'Takings changed little' across sixty streets.",
                               "«درآمد کم تغییر کرد» در شصت خیابان."),
                     "para": 2},
                    {"statement": "The council measured the change in noise.",
                     "answer": False,
                     "why": bi("Noise fell but 'the council never measured it'.",
                               "سر و صدا کم شد ولی «شورا هیچ‌وقت اندازه‌اش "
                               "نگرفت»."),
                     "para": 3},
                    {"statement": "Hilltown now has eleven school streets.",
                     "answer": True,
                     "why": bi("'Hilltown now runs eleven.'", "«هیل‌تاون حالا "
                               "یازده‌تا را اداره می‌کند.»"),
                     "para": 4},
                ],
                "essay": [
                    {"prompt": bi("Skim the passage again, then write two "
                                  "sentences: the first says what the scheme "
                                  "achieves, the second what it costs.",
                                  "دوباره متن را سریع بخوان و دو جمله بنویس: جملهٔ "
                                  "اول بگوید طرح چه به دست می‌آورد، جملهٔ دوم "
                                  "بگوید چه هزینه‌ای دارد."),
                     "min_words": 40,
                     "tips": [
                         bi("One gain, one cost - do not list three of each.",
                            "یک سود، یک هزینه؛ سه‌تا از هر کدام را فهرست نکن."),
                         bi("Keep both sentences in your own words.",
                            "هر دو جمله را با واژه‌های خودت بنویس."),
                         bi("A reader should be able to disagree with each "
                            "sentence.",
                            "خواننده باید بتواند با هر جمله مخالفت کند.")],
                     "model": bi("Closing a street to cars for forty minutes "
                                 "at each end of the school day cuts traffic "
                                 "and nitrogen dioxide on the school run, and "
                                 "does not damage nearby shops. The price is "
                                 "not money but the staff time needed to run "
                                 "and enforce each closure.",
                                 "بستن خیابان برای چهل دقیقه در ابتدا و انتهای "
                                 "روز مدرسه، ترافیک و دی‌اکسید نیتروژن مسیر "
                                 "مدرسه را کم می‌کند و به مغازه‌های اطراف ضرر "
                                 "نمی‌زند. هزینه‌اش پول نیست، بلکه ساعت کارکنانی "
                                 "است که باید هر بستن را اداره و اجرا کنند.")},
                ],
            },
        },
        {
            "title": bi("Why the record came back", "چرا صفحهٔ گرام برگشت"),
            "level": "B1",
            "genre": bi("Explainer", "مقالهٔ توضیحی"),
            "paragraphs": [
                "In 2022, for the first time since 1987, more vinyl records "
                "were sold in the United States than CDs: 41 million against "
                "33 million. Revenue from records reached 1.2 billion dollars. "
                "The format the industry declared dead in the 1990s is now its "
                "most valuable physical product.",
                "The buyers are not only collectors. Record shops report that "
                "most customers are under thirty-five and do not own a player "
                "when they buy their first disc. They buy the object, the "
                "artwork and the ritual, and many buy a cheap player in the "
                "same year.",
                "Streaming is not the enemy here. Subscriptions dominate "
                "listening, and records are bought in addition, not instead. A "
                "listener may stream an album fifty times and then buy it to "
                "own, which is closer to buying a poster than to buying music.",
                "The revival has a practical limit. Records are heavy, "
                "pressing plants are few, and a new album on vinyl can take "
                "nine months to arrive. That delay is why the format will stay "
                "a luxury rather than a replacement.",
            ],
            "summary": bi(
                "Vinyl outsells CDs again and earns more, but most buyers are "
                "young streamers buying an object, not a format taking over.",
                "صفحهٔ گرام دوباره از سی‌دی جلو می‌زند و درآمد بیشتری دارد، ولی "
                "بیشتر خریداران جوانانی هستند که استریم می‌کنند و یک شیء "
                "می‌خرند، نه قالبی که جای بقیه را بگیرد."),
            "questions": {
                "blanks": [
                    {"sentence": "In 2022, 41 million records were sold against "
                                 "___ million CDs.",
                     "answer": "33", "also": [],
                     "hint": bi("The second figure in the first paragraph.",
                                "عدد دوم پاراگراف اول."),
                     "para": 1},
                    {"sentence": "Most record buyers are under ___.",
                     "answer": "thirty-five", "also": ["35"],
                     "hint": bi("An age, written in words in the passage.",
                                "یک سن، در متن با حروف نوشته شده."),
                     "para": 2},
                    {"sentence": "A new album on vinyl can take ___ months to "
                                 "arrive.",
                     "answer": "nine", "also": ["9"],
                     "hint": bi("In the last paragraph, about delay.",
                                "در پاراگراف آخر، دربارهٔ تأخیر."),
                     "para": 4},
                ],
                "mcq": [
                    {"q": "What is the passage mainly about?",
                     "options": ["How records are manufactured",
                                 "A revival that is real but limited",
                                 "Why streaming is losing listeners",
                                 "The history of the record industry"],
                     "answer": 1,
                     "why": bi("Three paragraphs explain the revival and the "
                               "last names its limit; the writer never says "
                               "streaming is in decline.",
                               "سه پاراگراف بازگشت را توضیح می‌دهند و پاراگراف آخر "
                               "محدودیتش را می‌گوید؛ نویسنده هیچ‌جا نمی‌گوید "
                               "استریم در حال افت است."),
                     "para": 4},
                    {"q": "What does the second paragraph say about buyers?",
                     "options": ["They are mostly older collectors",
                                 "They already own a record player",
                                 "Most are young and buy before owning a "
                                 "player",
                                 "They buy records instead of streaming"],
                     "answer": 2,
                     "why": bi("'Most customers are under thirty-five and do "
                               "not own a player when they buy their first "
                               "disc.'",
                               "«بیشتر مشتریان زیر سی‌وپنج سال‌اند و موقع خرید "
                               "اولین صفحه، دستگاه پخش ندارند.»"),
                     "para": 2},
                    {"q": "What is the relationship between streaming and "
                           "records, according to the writer?",
                     "options": ["Records are replacing streaming",
                                 "Streaming is replacing records",
                                 "Records are bought in addition to streaming",
                                 "Neither is growing"],
                     "answer": 2,
                     "why": bi("'Records are bought in addition, not instead.'",
                               "«صفحه‌ها علاوه بر استریم خریداری می‌شوند، نه "
                               "به‌جای آن.»"),
                     "para": 3},
                ],
                "truefalse": [
                    {"statement": "Vinyl last outsold CDs before 2022 in 1987.",
                     "answer": True,
                     "why": bi("'For the first time since 1987'.",
                               "«برای اولین بار از ۱۹۸۷»."),
                     "para": 1},
                    {"statement": "Most first-time buyers already own a record "
                                  "player.",
                     "answer": False,
                     "why": bi("They 'do not own a player when they buy their "
                               "first disc'.",
                               "«موقع خرید اولین صفحه دستگاه پخش ندارند»."),
                     "para": 2},
                    {"statement": "New records can take a long time to be "
                                  "pressed.",
                     "answer": True,
                     "why": bi("'A new album on vinyl can take nine months to "
                               "arrive.'",
                               "«یک آلبوم جدید روی صفحه ممکن است نه ماه طول بکشد "
                               "تا برسد.»"),
                     "para": 4},
                ],
                "essay": [
                    {"prompt": bi("Why does the writer call vinyl 'a luxury "
                                  "rather than a replacement'? Answer in three "
                                  "or four sentences, using two facts.",
                                  "چرا نویسنده صفحهٔ گرام را «کالای لوکس، نه "
                                  "جانشین» می‌نامد؟ در سه یا چهار جمله با دو "
                                  "واقعیت از متن جواب بده."),
                     "min_words": 45,
                     "tips": [
                         bi("Start from the writer's own words, then explain.",
                            "از واژه‌های خود نویسنده شروع کن و بعد توضیح بده."),
                         bi("Use the numbers: nine months, one pressing plant "
                            "shortage.",
                            "از عددها استفاده کن: نه ماه، کمبود کارخانهٔ پرس."),
                         bi("Say what a luxury is not: not a substitute.",
                            "بگو لوکس چه نیست: جانشین نیست.")],
                     "model": bi("A luxury is something you buy in addition, "
                                 "and that is how records behave here. "
                                 "Streaming is how people listen, while a "
                                 "record is bought afterwards to own. The "
                                 "practical side also keeps it a luxury: "
                                 "records are heavy, pressing plants are few, "
                                 "and an album can take nine months to arrive, "
                                 "so it cannot replace a format that arrives "
                                 "instantly.",
                                 "کالای لوکس چیزی است که علاوه بر چیز دیگر "
                                 "می‌خری، و صفحه‌ها همین‌طورند. مردم با استریم "
                                 "گوش می‌دهند و صفحه را بعد برای داشتن "
                                 "می‌خرند. جنبهٔ عملی هم آن را لوکس نگه می‌دارد: "
                                 "صفحه سنگین است، کارخانهٔ پرس کم است و رسیدن "
                                 "آلبوم نه ماه طول می‌کشد، پس نمی‌تواند جای "
                                 "قالبی را بگیرد که فوری می‌رسد.")},
                ],
            },
        },
    ],
    "scan": [
        {
            "title": bi("Harvest Festival: the details", "جشنوارهٔ برداشت: جزئیات"),
            "level": "A2",
            "genre": bi("Event information", "اطلاعات رویداد"),
            "paragraphs": [
                "Harvest Festival, Saturday 14 September, Mill Field. Gates "
                "open at 10 am and the last entry is at 8 pm. Tickets cost £12 "
                "for adults, £7 for students, and children under twelve go "
                "free; buy them at the gate or in advance at the library.",
                "On stage: the Bracken Band at 1 pm, Salma Roy at 4 pm, and "
                "the Hilltown Youth Orchestra closing the day at 7 pm. The "
                "stage is covered, and the field is lit after dark.",
                "Workshops: bread making at 11 am, with twelve places, booked "
                "at the information tent on the day; cider pressing at 2 pm "
                "and again at 5 pm; beekeeping at 3 pm, no booking needed.",
                "Getting there: the number 14 bus stops on Mill Lane every "
                "twenty minutes. Parking costs £3 and must be booked online "
                "before Friday. Dogs are welcome on leads. No glass on the "
                "field.",
            ],
            "summary": bi(
                "One day, one field: prices, stage times, three workshops and "
                "the rules for arriving.",
                "یک روز، یک زمین: قیمت‌ها، ساعت‌های صحنه، سه کارگاه و قواعد "
                "رسیدن."),
            "questions": {
                "blanks": [
                    {"sentence": "The gates open at ___ am.",
                     "answer": "10", "also": ["ten"],
                     "hint": bi("The first line gives it.",
                                "خط اول می‌گوید."),
                     "para": 1},
                    {"sentence": "A student ticket costs £___.",
                     "answer": "7", "also": ["seven"],
                     "hint": bi("Between the adult and child prices.",
                                "بین قیمت بزرگسال و کودک."),
                     "para": 1},
                    {"sentence": "Parking costs £___.",
                     "answer": "3", "also": ["three"],
                     "hint": bi("In the last paragraph, with the bus.",
                                "در پاراگراف آخر، کنار اتوبوس."),
                     "para": 4},
                ],
                "mcq": [
                    {"q": "How do you get a place at the bread workshop?",
                     "options": ["Book online before Friday",
                                 "Book at the information tent on the day",
                                 "Pay £12 at the gate",
                                 "Write to the library"],
                     "answer": 1,
                     "why": bi("'Twelve places, booked at the information tent "
                               "on the day.' Online booking is for parking.",
                               "«دوازده جا، که همان روز در چادر اطلاعات رزرو "
                               "می‌شود.» رزرو آنلاین برای پارکینگ است."),
                     "para": 3},
                    {"q": "Which act closes the festival?",
                     "options": ["The Bracken Band", "Salma Roy",
                                 "The Hilltown Youth Orchestra",
                                 "The beekeeping workshop"],
                     "answer": 2,
                     "why": bi("'The Hilltown Youth Orchestra closing the day "
                               "at 7 pm.'",
                               "«ارکستر جوانان هیل‌تاون روز را ساعت ۷ می‌بندد.»"),
                     "para": 2},
                    {"q": "Where can you buy a ticket in advance?",
                     "options": ["At the library", "At the information tent",
                                 "Online only", "On Mill Lane"],
                     "answer": 0,
                     "why": bi("'Buy them at the gate or in advance at the "
                               "library.'",
                               "«از گیت یا از قبل در کتابخانه بخرید.»"),
                     "para": 1},
                ],
                "truefalse": [
                    {"statement": "Children under twelve pay nothing.",
                     "answer": True,
                     "why": bi("'Children under twelve go free.'",
                               "«کودکان زیر دوازده سال مجانی‌اند.»"),
                     "para": 1},
                    {"statement": "Parking is free if you arrive early.",
                     "answer": False,
                     "why": bi("Parking costs £3 whatever the time, and must "
                               "be booked online.",
                               "پارکینگ هر ساعتی که برسی ۳ پوند است و باید آنلاین "
                               "رزرو شود."),
                     "para": 4},
                    {"statement": "Beekeeping is at 3 pm and needs no booking.",
                     "answer": True,
                     "why": bi("'Beekeeping at 3 pm, no booking needed.'",
                               "«زنبورداری ساعت ۳، رزرو لازم نیست.»"),
                     "para": 3},
                ],
                "essay": [
                    {"prompt": bi("You arrive at 11:20 am with two children "
                                  "under twelve and no car. What can you do "
                                  "before 5 pm, and what must you arrange when "
                                  "you arrive?",
                                  "ساعت ۱۱:۲۰ با دو کودک زیر دوازده سال و بدون "
                                  "ماشین می‌رسی. تا ۵ بعدازظهر چه می‌توانی بکنی "
                                  "و موقع رسیدن باید چه ترتیبی بدهی؟"),
                     "min_words": 45,
                     "tips": [
                         bi("Use the times in the programme, in order.",
                            "از ساعت‌های برنامه به ترتیب استفاده کن."),
                         bi("The bread workshop needs action on arrival - say "
                            "so first.",
                            "کارگاه نان به اقدام هنگام رسیدن نیاز دارد؛ اول "
                            "همین را بگو."),
                         bi("Mention how you get there without a car.",
                            "بگو بدون ماشین چطور می‌رسی.")],
                     "model": bi("We would take the number 14 bus to Mill Lane "
                                 "and go first to the information tent, "
                                 "because the bread workshop at 11 am has only "
                                 "twelve places and is booked on the day. "
                                 "After that we could see the Bracken Band at "
                                 "1 pm, press cider at 2 pm and go to "
                                 "beekeeping at 3 pm. The children are under "
                                 "twelve, so they enter free, and we would "
                                 "leave before Salma Roy at 4 pm if they are "
                                 "tired.",
                                 "با اتوبوس شمارهٔ ۱۴ به خیابان میل می‌رفتیم و اول "
                                 "سراغ چادر اطلاعات می‌رفتیم، چون کارگاه نان "
                                 "ساعت ۱۱ فقط دوازده جا دارد و همان روز رزرو "
                                 "می‌شود. بعد می‌توانستیم ساعت ۱ گروه براکن را "
                                 "ببینیم، ساعت ۲ سیب بفشاریم و ساعت ۳ به "
                                 "زنبورداری برویم. بچه‌ها زیر دوازده سال‌اند و "
                                 "مجانی وارد می‌شوند؛ اگر خسته بودند پیش از "
                                 "سلماروی ساعت ۴ برمی‌گشتیم.")},
                ],
            },
        },
        {
            "title": bi("The Coast Line timetable", "جدول زمانی خط ساحلی"),
            "level": "B1",
            "genre": bi("Timetable / travel information", "جدول زمانی / اطلاعات سفر"),
            "paragraphs": [
                "Weekday trains from Hilltown to Seahaven leave at 06:45, "
                "07:30, 09:10, 12:05, 15:40 and 18:25. The 07:30 is the only "
                "direct service; the others require a change at Marston, where "
                "the connection usually waits four minutes.",
                "Journey time is 58 minutes on the direct train and 1 hour 24 "
                "minutes with the change. A return ticket costs £14.60, or "
                "£9.20 with a railcard. Single tickets are not sold after 6 "
                "pm on Sundays.",
                "Bicycles travel free, but only two are allowed on each train "
                "and none on the 07:30, which is the busiest service. Folding "
                "bicycles count as luggage and are always allowed.",
                "The ticket office opens at 06:15 and closes at 19:00. The "
                "machine on platform 2 takes cards only, and there is no "
                "machine on platform 1. Seat reservations are free but "
                "recommended for the 18:25, and a ticket bought on the train "
                "costs £2 more than one bought at the office.",
            ],
            "summary": bi(
                "A timetable: six trains, one of them direct, with fares, a "
                "bicycle rule that excludes the busiest train, and where to "
                "buy a ticket.",
                "یک جدول زمانی: شش قطار که یکی مستقیم است، با قیمت‌ها، قانون "
                "دوچرخه که پرترددترین قطار را کنار می‌گذارد، و محل خرید "
                "بلیت."),
            "questions": {
                "blanks": [
                    {"sentence": "The ___ train is the only direct service.",
                     "answer": "07:30", "also": ["7:30", "7.30"],
                     "hint": bi("A time, in the first sentence.",
                                "یک ساعت، در جملهٔ اول."),
                     "para": 1},
                    {"sentence": "A return ticket costs £___.",
                     "answer": "14.60", "also": ["14,60"],
                     "hint": bi("The full fare, before the railcard.",
                                "قیمت کامل، پیش از کارت تخفیف."),
                     "para": 2},
                    {"sentence": "The ticket office opens at ___.",
                     "answer": "06:15", "also": ["6:15", "6.15"],
                     "hint": bi("Earlier than the first train.",
                                "پیش از اولین قطار."),
                     "para": 4},
                ],
                "mcq": [
                    {"q": "Where do most trains require a change?",
                     "options": ["Seahaven", "Marston", "Hilltown",
                                 "Platform 2"],
                     "answer": 1,
                     "why": bi("'The others require a change at Marston.'",
                               "«بقیه در مارستون نیاز به تعویض دارند.»"),
                     "para": 1},
                    {"q": "How many bicycles are allowed on each train?",
                     "options": ["None", "Two", "Four", "As many as fit"],
                     "answer": 1,
                     "why": bi("'Only two are allowed on each train'.",
                               "«فقط دو دوچرخه در هر قطار مجاز است.»"),
                     "para": 3},
                    {"q": "What can you do at the platform 2 machine?",
                     "options": ["Pay with cash or card",
                                 "Pay with a card only",
                                 "Reserve a seat",
                                 "Buy a bicycle ticket"],
                     "answer": 1,
                     "why": bi("'The machine on platform 2 takes cards only.'",
                               "«دستگاه سکو ۲ فقط کارت می‌پذیرد.»"),
                     "para": 4},
                ],
                "truefalse": [
                    {"statement": "You can take a bicycle on the 07:30.",
                     "answer": False,
                     "why": bi("'None on the 07:30, which is the busiest "
                               "service.'",
                               "«هیچ‌کدام در قطار ۰۷:۳۰ که پرترددترین است.»"),
                     "para": 3},
                    {"statement": "The direct journey takes under an hour.",
                     "answer": True,
                     "why": bi("'58 minutes on the direct train.'",
                               "«۵۸ دقیقه با قطار مستقیم.»"),
                     "para": 2},
                    {"statement": "Seat reservations cost extra.",
                     "answer": False,
                     "why": bi("'Seat reservations are free but recommended'.",
                               "«رزرو صندلی مجانی است ولی توصیه می‌شود»."),
                     "para": 4},
                ],
                "essay": [
                    {"prompt": bi("You want to spend a day in Seahaven and "
                                  "take a bicycle. Which train would you take "
                                  "out, which back, and what would you check "
                                  "before leaving?",
                                  "می‌خواهی یک روز در سی‌هیون بگذرانی و دوچرخه هم "
                                  "ببری. با کدام قطار می‌روی، با کدام برمی‌گردی "
                                  "و پیش از راه افتادن چه چیزی را بررسی می‌کنی؟"),
                     "min_words": 45,
                     "tips": [
                         bi("The direct train and a bicycle cannot go together "
                            "- say what you do about that.",
                            "قطار مستقیم و دوچرخه با هم نمی‌شوند؛ بگو چه "
                            "می‌کنی."),
                         bi("Give a departure and a return time from the "
                            "timetable.",
                            "یک ساعت رفت و یک ساعت برگشت از جدول بده."),
                         bi("Mention the ticket office closing time.",
                            "ساعت بسته شدن بلیت‌فروشی را بیاور.")],
                     "model": bi("Because bicycles are not allowed on the "
                                 "07:30, I would take the 09:10 and change at "
                                 "Marston, which takes about an hour and "
                                 "twenty-four minutes. I would come back on "
                                 "the 15:40 so that I could buy the return "
                                 "ticket at the office, which closes at 19:00, "
                                 "and I would check the connection time at "
                                 "Marston before leaving, since four minutes "
                                 "is short with a bicycle.",
                                 "چون دوچرخه در قطار ۰۷:۳۰ مجاز نیست، با قطار "
                                 "۰۹:۱۰ می‌رفتم و در مارستون تعویض می‌کردم که "
                                 "حدود یک ساعت و بیست‌وچهار دقیقه طول می‌کشد. با "
                                 "قطار ۱۵:۴۰ برمی‌گشتم تا بلیت برگشت را از "
                                 "بلیت‌فروشی که ساعت ۱۹ می‌بندد بخرم، و پیش از "
                                 "راه افتادن زمان تعویض در مارستون را بررسی "
                                 "می‌کردم، چون چهار دقیقه با دوچرخه کم است.")},
                ],
            },
        },
    ],
}
