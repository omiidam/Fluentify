"""Two further practices for main ideas and for signposts."""
from reading_src import bi

MORE = {
    "mainidea": [
        {
            "title": bi("Painting the street white", "رنگ کردن خیابان به سفید"),
            "level": "B1",
            "genre": bi("Explainer", "مقالهٔ توضیحی"),
            "paragraphs": [
                "A white roof is not a new idea, but the measurements are. In "
                "Los Angeles, streets coated with a pale reflective surface "
                "measured up to 2.1 degrees Fahrenheit cooler in the air above "
                "them on sunny days, and about half a degree cooler at night.",
                "The mechanism is simple. Dark surfaces absorb sunlight and "
                "release it as heat; pale ones reflect part of it away. In "
                "Phoenix, coated asphalt has measured up to twelve degrees "
                "Fahrenheit cooler at the surface at noon, which matters to "
                "anyone who has to touch it.",
                "The limits are equally simple. A reflective street is bright, "
                "and drivers have complained about glare. Coatings wear away "
                "and must be reapplied every few years, and the effect on air "
                "temperature, though real, is small next to planting trees, "
                "which also provide shade.",
                "So painting is best understood as one measure among several. "
                "Cities that have done it report the same thing: the sidewalk "
                "cools, the street looks different, and nobody claims the town "
                "is cool. For that you need shade, water and fewer cars.",
            ],
            "summary": bi(
                "Pale coatings measurably cool a road surface and slightly "
                "cool the air, but they are one small measure among several.",
                "پوشش‌های روشن دمای سطح خیابان را محسوس و دمای هوا را کمی کم "
                "می‌کنند، ولی یکی از چند اقدام کوچک‌اند."),
            "questions": {
                "blanks": [
                    {"sentence": "In Los Angeles the air above coated streets "
                                 "measured up to ___ degrees cooler.",
                     "answer": "2.1", "also": ["2,1"],
                     "hint": bi("A decimal, in the first paragraph.",
                                "یک عدد اعشاری، در پاراگراف اول."),
                     "para": 1},
                    {"sentence": "In Phoenix the surface measured up to ___ "
                                 "degrees cooler at noon.",
                     "answer": "twelve", "also": ["12"],
                     "hint": bi("A word, in the second paragraph.",
                                "یک کلمه، در پاراگراف دوم."),
                     "para": 2},
                    {"sentence": "Coatings must be reapplied every few ___.",
                     "answer": "years", "also": [],
                     "hint": bi("How long a coating lasts.",
                                "مدت دوام پوشش."),
                     "para": 3},
                ],
                "mcq": [
                    {"q": "What is the passage mainly about?",
                     "options": ["Why cities should paint every road white",
                                 "A cooling measure that works but is limited",
                                 "The cost of reflective paint",
                                 "How asphalt is made"],
                     "answer": 1,
                     "why": bi("Two paragraphs give the effect, one gives the "
                               "limits, and the last says it is 'one measure "
                               "among several'.",
                               "دو پاراگراف اثر را می‌دهند، یکی محدودیت‌ها، و "
                               "پاراگراف آخر می‌گوید «یکی از چند اقدام» است."),
                     "para": 4},
                    {"q": "Why do pale surfaces stay cooler?",
                     "options": ["They are made of different stone",
                                 "They reflect part of the sunlight instead of "
                                 "absorbing it",
                                 "They hold more water",
                                 "They are always in the shade"],
                     "answer": 1,
                     "why": bi("'Dark surfaces absorb sunlight and release it "
                               "as heat; pale ones reflect part of it away.'",
                               "«سطوح تیره نور خورشید را جذب و به گرما تبدیل "
                               "می‌کنند؛ سطوح روشن بخشی را بازمی‌تابانند.»"),
                     "para": 2},
                    {"q": "What do the cities that have done it report?",
                     "options": ["The whole town is cooler",
                                 "The sidewalk cools, but nobody claims the town "
                                 "is cool",
                                 "Drivers prefer the brighter streets",
                                 "The paint never needs replacing"],
                     "answer": 1,
                     "why": bi("The last paragraph reports exactly that pair, "
                               "and warns that shade, water and fewer cars are "
                               "needed for the town.",
                               "پاراگراف آخر دقیقاً همین دو را می‌گوید و هشدار "
                               "می‌دهد که برای شهر سایه، آب و ماشین کمتر لازم "
                               "است."),
                     "para": 4},
                ],
                "truefalse": [
                    {"statement": "Drivers have complained about glare from "
                                  "reflective streets.",
                     "answer": True,
                     "why": bi("'Drivers have complained about glare.'",
                               "«رانندگان از خیرگی شکایت کرده‌اند.»"),
                     "para": 3},
                    {"statement": "The passage says planting trees cools the "
                                  "air more than coating does.",
                     "answer": True,
                     "why": bi("The effect on air temperature is 'small next "
                               "to planting trees, which also provide shade'.",
                               "اثر روی دمای هوا «در مقایسه با کاشتن درخت، که "
                               "سایه هم می‌دهد، کوچک» است."),
                     "para": 3},
                    {"statement": "Coatings last for decades.",
                     "answer": False,
                     "why": bi("They 'wear away and must be reapplied every few "
                               "years'.",
                               "«ساییده می‌شوند و باید هر چند سال دوباره زده "
                               "شوند»."),
                     "para": 3},
                ],
                "essay": [
                    {"prompt": bi("Write the main idea of the whole passage in "
                                  "one sentence, then explain in two more why "
                                  "the last paragraph is necessary.",
                                  "ایدهٔ اصلی کل متن را در یک جمله بنویس، بعد در دو "
                                  "جملهٔ دیگر توضیح بده چرا پاراگراف آخر لازم است."),
                     "min_words": 50,
                     "tips": [
                         bi("The sentence must be something a reader could "
                            "argue with.",
                            "جمله باید چیزی باشد که خواننده بتواند با آن مخالفت "
                            "کند."),
                         bi("Say what the last paragraph stops a reader "
                            "believing.",
                            "بگو پاراگراف آخر جلوی چه باوری را می‌گیرد."),
                         bi("Keep the numbers out of the main idea.",
                            "عددها را از ایدهٔ اصلی بیرون بگذار.")],
                     "model": bi("Pale reflective coatings cool a street "
                                 "surface a lot and the air above it a little, "
                                 "and they are worth doing as one small part of "
                                 "a wider plan. The last paragraph is necessary "
                                 "because the first three could leave a reader "
                                 "thinking the problem is solved by paint, and "
                                 "it says plainly that shade, water and fewer "
                                 "cars are what a cool town needs.",
                                 "پوشش‌های روشن و بازتابنده سطح خیابان را زیاد و "
                                 "هوای بالای آن را کم خنک می‌کنند و ارزش دارند "
                                 "به‌عنوان بخش کوچکی از یک برنامهٔ بزرگ‌تر. پاراگراف "
                                 "آخر لازم است چون سه پاراگراف اول می‌توانست "
                                 "خواننده را به این باور برساند که مشکل با رنگ حل "
                                 "می‌شود؛ و آن پاراگراف صریح می‌گوید شهر خنک به "
                                 "سایه، آب و ماشین کمتر نیاز دارد.")},
                ],
            },
        },
        {
            "title": bi("The second-hand shirt", "پیراهن دست‌دوم"),
            "level": "B2",
            "genre": bi("Opinion / analysis", "یادداشت تحلیلی"),
            "paragraphs": [
                "Ten years ago buying used clothes was a way of saving money. "
                "Today it is also a way of being seen: resale platforms "
                "advertise vintage labels, and a jacket that someone else has "
                "worn can cost more than a new one.",
                "The environmental argument is the one most often made. A new "
                "cotton shirt uses thousands of liters of water before it "
                "reaches a shop; a second-hand shirt uses almost none. On that "
                "measure, buying used is clearly better.",
                "The catch is that the argument only holds while people buy "
                "fewer new clothes. If a shopper buys second-hand in addition "
                "to everything they bought before, the water saved by the used "
                "shirt is spent on the new one in the same bag.",
                "Resale has therefore changed the second-hand shop more than it "
                "has changed consumption. The shops now compete for the best "
                "donations, prices have risen, and the cheapest clothes - the "
                "ones that used to clothe people who needed them - are the "
                "hardest to find.",
            ],
            "summary": bi(
                "Second-hand fashion saves water per garment, but only if it "
                "replaces a purchase; mostly it has raised prices instead.",
                "مد دست‌دوم برای هر لباس آب صرفه‌جویی می‌کند، ولی فقط اگر جای "
                "خرید تازه را بگیرد؛ در عمل بیشتر قیمت‌ها را بالا برده است."),
            "questions": {
                "blanks": [
                    {"sentence": "A new cotton shirt uses thousands of liters "
                                 "of ___.",
                     "answer": "water", "also": [],
                     "hint": bi("The resource named in paragraph two.",
                                "منبعی که در پاراگراف دوم نام برده شده."),
                     "para": 2},
                    {"sentence": "Nothing is saved if used clothes are bought "
                                 "in ___ to new ones.",
                     "answer": "addition", "also": [],
                     "hint": bi("The writer's phrase for buying more, not "
                                "instead.",
                                "عبارت نویسنده برای بیشتر خریدن، نه به‌جای آن."),
                     "para": 3},
                    {"sentence": "The cheapest clothes are now the hardest to "
                                 "___.",
                     "answer": "find", "also": [],
                     "hint": bi("The last word of the passage.",
                                "آخرین کلمهٔ متن."),
                     "para": 4},
                ],
                "mcq": [
                    {"q": "What is the passage mainly about?",
                     "options": ["How to save money on clothes",
                                 "Why resale helps the environment",
                                 "A saving that depends on buying less, and what "
                                 "resale has actually changed",
                                 "The history of vintage fashion"],
                     "answer": 2,
                     "why": bi("The paragraph three qualification is the point; "
                               "the last paragraph says what really changed.",
                               "قیدِ پاراگراف سوم همان نکتهٔ اصلی است و پاراگراف آخر "
                               "می‌گوید واقعاً چه چیزی تغییر کرد."),
                     "para": 3},
                    {"q": "What is 'the catch'?",
                     "options": ["Second-hand clothes are dirty",
                                 "The saving disappears if the shopper also "
                                 "buys new clothes",
                                 "Cotton is becoming rarer",
                                 "Resale platforms charge too much"],
                     "answer": 1,
                     "why": bi("If used clothes are bought 'in addition to "
                               "everything they bought before', nothing is "
                               "saved.",
                               "اگر لباس دست‌دوم «علاوه بر هر چیزی که قبلاً خریده» "
                               "خریداری شود، چیزی صرفه‌جویی نمی‌شود."),
                     "para": 3},
                    {"q": "What has resale changed most?",
                     "options": ["How much clothing is produced",
                                 "The second-hand shop itself",
                                 "The price of cotton",
                                 "How people wash clothes"],
                     "answer": 1,
                     "why": bi("'Resale has therefore changed the second-hand "
                               "shop more than it has changed consumption.'",
                               "«پس فروش دوباره بیشتر مغازهٔ دست‌دوم را عوض کرده تا "
                               "مصرف را.»"),
                     "para": 4},
                ],
                "truefalse": [
                    {"statement": "Some used jackets now cost more than new "
                                  "ones.",
                     "answer": True,
                     "why": bi("'A jacket that someone else has worn can cost "
                               "more than a new one.'",
                               "«کاپشنی که کس دیگری پوشیده می‌تواند از نو گران‌تر "
                               "باشد.»"),
                     "para": 1},
                    {"statement": "Buying used always reduces total "
                                  "consumption.",
                     "answer": False,
                     "why": bi("Only if it replaces a purchase rather than "
                               "adding to it.",
                               "فقط اگر جای یک خرید را بگیرد، نه اینکه به آن اضافه "
                               "شود."),
                     "para": 3},
                    {"statement": "Prices in second-hand shops have risen.",
                     "answer": True,
                     "why": bi("'Prices have risen', and the cheapest clothes "
                               "are hardest to find.",
                               "«قیمت‌ها بالا رفته‌اند» و ارزان‌ترین لباس‌ها سخت‌تر "
                               "پیدا می‌شوند."),
                     "para": 4},
                ],
                "essay": [
                    {"prompt": bi("A friend says buying second-hand is always "
                                  "greener. Using the passage, explain what is "
                                  "right and what is missing in that claim.",
                                  "دوستی می‌گوید خرید دست‌دوم همیشه سبزتر است. با "
                                  "استفاده از متن توضیح بده چه چیزی درست است و چه "
                                  "چیزی جا افتاده."),
                     "min_words": 60,
                     "tips": [
                         bi("Grant the part that is true before you qualify it.",
                            "اول بخش درست را بپذیر، بعد قید بزن."),
                         bi("Use the water comparison and the word 'addition'.",
                            "از مقایسهٔ آب و واژهٔ «علاوه بر» استفاده کن."),
                         bi("End with what happened to prices, which the friend "
                            "probably has not noticed.",
                            "با سرنوشت قیمت‌ها تمام کن، چیزی که دوستت احتمالاً "
                            "متوجهش نشده.")],
                     "model": bi("My friend is right about the shirt: a new "
                                 "cotton one uses thousands of liters of water "
                                 "and a second-hand one uses almost none, so "
                                 "per garment the used shirt is better. What the "
                                 "claim misses is addition. If the same shopper "
                                 "also buys everything they bought before, the "
                                 "water saved on the shirt is spent on the new "
                                 "clothes in the same bag. The passage also "
                                 "shows a side effect nobody advertised: resale "
                                 "has pushed prices up, so the cheapest clothes "
                                 "are now the hardest to find.",
                                 "دستم دربارهٔ پیراهن درست است: پیراهن نوی پنبه‌ای "
                                 "هزاران لیتر آب می‌خواهد و دست‌دوم تقریباً هیچ، "
                                 "پس به‌ازای هر لباس دست‌دوم بهتر است. چیزی که این "
                                 "ادعا جا می‌اندازد «اضافه شدن» است. اگر همان "
                                 "خریدار همهٔ چیزهایی را که قبلاً می‌خرید هم "
                                 "بخرد، آبی که در پیراهن صرفه‌جویی شد صرف لباس‌های "
                                 "نو در همان سبد می‌شود. متن یک عارضهٔ تبلیغ‌نشده "
                                 "هم نشان می‌دهد: فروش دوباره قیمت‌ها را بالا برده، "
                                 "پس ارزان‌ترین لباس‌ها حالا سخت‌ترین برای پیدا "
                                 "کردن‌اند.")},
                ],
            },
        },
    ],
    "signposts": [
        {
            "title": bi("Remote work: what the studies can support",
                        "کار از راه دور: پژوهش‌ها از چه چیزی پشتیبانی می‌کنند"),
            "level": "B2",
            "genre": bi("Analysis", "تحلیل"),
            "paragraphs": [
                "Remote work raises productivity. However, the studies showing "
                "this were mostly done with experienced staff doing tasks that "
                "need concentration rather than coordination.",
                "For example, one trial of data-entry staff found a 13 percent "
                "gain when they worked from home four days a week; a second "
                "study of software teams found no measurable change in output "
                "but slower decisions.",
                "Therefore the useful question is not whether remote work is "
                "productive but for whom. Consequently, a manager who reads "
                "only the first result will expect gains that a mixed team may "
                "never see.",
                "Nevertheless, the pattern is not random. Tasks that are "
                "individual, measurable and already well defined travel well; "
                "work that depends on quick, unplanned conversation does not. "
                "Unless a team's tasks are sorted into those two groups, any "
                "general claim will be wrong for half of it.",
            ],
            "summary": bi(
                "The evidence supports remote work for concentrated, "
                "measurable tasks, and not for work that runs on quick "
                "conversation.",
                "شواهد از کار از راه دور برای کارهای متمرکز و قابل‌اندازه‌گیری "
                "پشتیبانی می‌کند، نه برای کاری که با گفت‌وگوی سریع پیش می‌رود."),
            "questions": {
                "blanks": [
                    {"sentence": "The data-entry trial found a ___ percent "
                                 "gain.",
                     "answer": "13", "also": ["thirteen"],
                     "hint": bi("A number in the second paragraph.",
                                "عددی در پاراگراف دوم."),
                     "para": 2},
                    {"sentence": "The software study found slower ___.",
                     "answer": "decisions", "also": [],
                     "hint": bi("Output did not change, but this did.",
                                "بازده عوض نشد، ولی این عوض شد."),
                     "para": 2},
                    {"sentence": "Tasks that are individual and measurable "
                                 "travel ___.",
                     "answer": "well", "also": [],
                     "hint": bi("A short adverb, twice in the last paragraph.",
                                "یک قید کوتاه، دو بار در پاراگراف آخر."),
                     "para": 4},
                ],
                "mcq": [
                    {"q": "What does 'However' do at the start of the second "
                           "sentence?",
                     "options": ["It gives an example",
                                 "It limits the claim just made",
                                 "It adds a second reason",
                                 "It concludes the paragraph"],
                     "answer": 1,
                     "why": bi("The first sentence is the claim; 'However' "
                               "immediately says the studies behind it were "
                               "narrow - a limit, not a new reason.",
                               "جملهٔ اول ادعاست؛ «However» فوراً می‌گوید پژوهش‌های "
                               "پشتش محدود بوده‌اند؛ این محدودیت است، نه دلیل "
                               "تازه."),
                     "para": 1},
                    {"q": "What does 'Therefore' introduce?",
                     "options": ["A correction of the first paragraph",
                                 "A better question to ask",
                                 "A second example",
                                 "A definition"],
                     "answer": 1,
                     "why": bi("It follows from the two studies that the "
                               "question should change from 'whether' to 'for "
                               "whom'.",
                               "از دو پژوهش نتیجه می‌گیرد که سؤال باید از «آیا» به "
                               "«برای چه کسی» تغییر کند."),
                     "para": 3},
                    {"q": "What is the writer's final position?",
                     "options": ["Remote work never works",
                                 "Remote work always works",
                                 "Any general claim fails unless tasks are split "
                                 "by type",
                                 "Managers should ignore the studies"],
                     "answer": 2,
                     "why": bi("'Unless a team's tasks are sorted into those two "
                               "groups, any general claim will be wrong for half "
                               "of it' - a condition, not a rejection.",
                               "«مگر اینکه کارهای تیم به آن دو گروه تقسیم شود، هر "
                               "ادعای کلی برای نیمی از آن غلط است»؛ این یک شرط "
                               "است، نه رد کردن."),
                     "para": 4},
                ],
                "truefalse": [
                    {"statement": "The software study found that decisions were "
                                  "made more slowly.",
                     "answer": True,
                     "why": bi("'No measurable change in output but slower "
                               "decisions'.",
                               "«تغییر قابل‌اندازه‌گیری در بازده نبود، ولی تصمیم‌ها "
                               "کندتر شد»."),
                     "para": 2},
                    {"statement": "The writer says remote work never raises "
                                  "productivity.",
                     "answer": False,
                     "why": bi("The trial did raise it by 13 percent; the "
                               "writer limits the claim, not denies it.",
                               "آزمون ۱۳ درصد افزایش داد؛ نویسنده ادعا را محدود "
                               "می‌کند، انکار نمی‌کند."),
                     "para": 2},
                    {"statement": "'Unless' introduces a condition.",
                     "answer": True,
                     "why": bi("It says what must happen for general claims to "
                               "hold.",
                               "می‌گوید برای درست بودن ادعاهای کلی چه چیزی باید "
                               "اتفاق بیفتد."),
                     "para": 4},
                ],
                "essay": [
                    {"prompt": bi("Write the argument as a map: claim, limit, "
                                  "evidence, conclusion, condition. One line "
                                  "each, using the signposts.",
                                  "استدلال را مثل یک نقشه بنویس: ادعا، محدودیت، "
                                  "شاهد، نتیجه، شرط. هر کدام یک خط، با استفاده از "
                                  "نشانه‌ها."),
                     "min_words": 50,
                     "tips": [
                         bi("Start each line with the signpost the writer used.",
                            "هر خط را با نشانه‌ای شروع کن که نویسنده به کار برده."),
                         bi("Keep the order of the passage.",
                            "ترتیب متن را نگه دار."),
                         bi("Do not add an opinion of your own.",
                            "نظر خودت را اضافه نکن.")],
                     "model": bi("Claim: remote work raises productivity. "
                                 "However - the studies used experienced staff "
                                 "on concentrated tasks. For example - data "
                                 "entry gained 13 percent, while software "
                                 "teams saw slower decisions. Therefore - the "
                                 "question is not whether but for whom. "
                                 "Consequently - managers expecting the same "
                                 "gain will be disappointed. Nevertheless - the "
                                 "pattern is regular, and unless tasks are "
                                 "sorted, general claims fail.",
                                 "ادعا: کار از راه دور بهره‌وری را بالا می‌برد. "
                                 "However - پژوهش‌ها با کارکنان باتجربه روی کارهای "
                                 "متمرکز انجام شده بود. For example - ورود داده "
                                 "۱۳ درصد سود داشت، در حالی که تیم‌های نرم‌افزار "
                                 "تصمیم‌های کندتر داشتند. Therefore - سؤال «آیا» "
                                 "نیست، «برای چه کسی» است. Consequently - مدیری که "
                                 "همان سود را انتظار دارد ناامید می‌شود. "
                                 "Nevertheless - الگو منظم است و تا کارها دسته‌بندی "
                                 "نشوند، ادعاهای کلی شکست می‌خورند.")},
                ],
            },
        },
        {
            "title": bi("A diet study, and the sentence the headlines missed",
                        "یک پژوهش رژیم، و جمله‌ای که تیترها جا انداختند"),
            "level": "B2",
            "genre": bi("Science commentary", "یادداشت علمی"),
            "paragraphs": [
                "A trial published this spring found that people who ate "
                "breakfast before ten in the morning lost more weight than "
                "those who ate later. Newspapers reported it as proof that "
                "timing matters more than quantity.",
                "Yet the trial had 90 participants, all of them already "
                "overweight, and it ran for twelve weeks. A result of that size, "
                "over that period, cannot tell you what happens across five "
                "years.",
                "Moreover, the two groups differed in something the headlines "
                "ignored: the early group also ate fewer snacks in the evening. "
                "As a result, the study cannot separate the effect of timing "
                "from the effect of simply eating less.",
                "In short, the finding is interesting and the conclusion is not "
                "yet available. Until a trial controls for what people eat as "
                "well as when, the practical advice stays the boring one: eat "
                "less, move more, and sleep.",
            ],
            "summary": bi(
                "A small, short trial was reported as proof of timing; it "
                "cannot separate timing from eating less, so the advice does "
                "not change.",
                "آزمونی کوچک و کوتاه به‌عنوان اثبات اهمیت زمان گزارش شد؛ نمی‌تواند "
                "زمان را از کمتر خوردن جدا کند، پس توصیه عوض نمی‌شود."),
            "questions": {
                "blanks": [
                    {"sentence": "The trial had ___ participants.",
                     "answer": "90", "also": ["ninety"],
                     "hint": bi("A number in the second paragraph.",
                                "عددی در پاراگراف دوم."),
                     "para": 2},
                    {"sentence": "The trial ran for ___ weeks.",
                     "answer": "twelve", "also": ["12"],
                     "hint": bi("A word, about the length of the trial.",
                                "یک کلمه، دربارهٔ مدت آزمون."),
                     "para": 2},
                    {"sentence": "The early group also ate fewer ___ in the "
                                 "evening.",
                     "answer": "snacks", "also": [],
                     "hint": bi("What people eat between meals.",
                                "چیزی که بین وعده‌ها خورده می‌شود."),
                     "para": 3},
                ],
                "mcq": [
                    {"q": "What does 'Yet' introduce in paragraph two?",
                     "options": ["A second result",
                                 "A reason to doubt the conclusion drawn from "
                                 "the trial",
                                 "A definition of weight loss",
                                 "The writer's own diet advice"],
                     "answer": 1,
                     "why": bi("The size and the twelve weeks are given as "
                               "reasons the result cannot support a long-term "
                               "claim.",
                               "اندازهٔ نمونه و دوازده هفته به‌عنوان دلایلی آمده‌اند که "
                               "نتیجه نمی‌تواند ادعای بلندمدت را پشتیبانی کند."),
                     "para": 2},
                    {"q": "What does 'Moreover' add?",
                     "options": ["A repeat of the first problem",
                                 "A different, independent problem",
                                 "A defense of the study",
                                 "The newspaper's reaction"],
                     "answer": 1,
                     "why": bi("'Moreover' marks a second point of a different "
                               "kind: the groups differed in what they ate.",
                               "«Moreover» نکتهٔ دومی از نوعی دیگر را نشان می‌دهد: "
                               "گروه‌ها در آنچه می‌خوردند هم تفاوت داشتند."),
                     "para": 3},
                    {"q": "What is the writer's conclusion?",
                     "options": ["Timing is proven to matter",
                                 "The study should not have been published",
                                 "The practical advice does not change yet",
                                 "Breakfast should be banned after ten"],
                     "answer": 2,
                     "why": bi("'The practical advice stays the boring one', "
                               "because the trial cannot separate the two "
                               "causes.",
                               "«توصیهٔ عملی همان توصیهٔ خسته‌کننده می‌ماند»، چون "
                               "آزمون نمی‌تواند دو علت را جدا کند."),
                     "para": 4},
                ],
                "truefalse": [
                    {"statement": "The trial lasted a full year.",
                     "answer": False,
                     "why": bi("It ran for 'twelve weeks'.",
                               "«دوازده هفته» طول کشید."),
                     "para": 2},
                    {"statement": "The early group ate fewer evening snacks.",
                     "answer": True,
                     "why": bi("'The early group also ate fewer snacks in the "
                               "evening.'",
                               "«گروه صبح‌زودتر شب‌ها تنقلات کمتری هم می‌خورد.»"),
                     "para": 3},
                    {"statement": "The writer thinks the finding is worthless.",
                     "answer": False,
                     "why": bi("'The finding is interesting and the conclusion "
                               "is not yet available' - interesting, not "
                               "worthless.",
                               "«یافته جالب است و نتیجه هنوز در دسترس نیست»؛ جالب، "
                               "نه بی‌ارزش."),
                     "para": 4},
                ],
                "essay": [
                    {"prompt": bi("Summarize the passage's argument in three "
                                  "sentences, one for the finding, one for the "
                                  "two problems, one for the conclusion.",
                                  "استدلال متن را در سه جمله خلاصه کن: یکی برای "
                                  "یافته، یکی برای دو مشکل، یکی برای نتیجه."),
                     "min_words": 50,
                     "tips": [
                         bi("Keep the numbers that carry the argument.",
                            "عددهایی را که استدلال را حمل می‌کنند نگه دار."),
                         bi("Use 'because' or 'so' once, not in every sentence.",
                            "یک بار از because یا so استفاده کن، نه در هر جمله."),
                         bi("No new opinion of your own.",
                            "هیچ نظر تازهٔ خودت اضافه نکن.")],
                     "model": bi("A trial found that people who ate breakfast "
                                 "before ten lost more weight, and papers "
                                 "reported that timing matters more than "
                                 "quantity. The trial had only 90 participants "
                                 "over twelve weeks, and its early group also "
                                 "ate fewer evening snacks, so it cannot "
                                 "separate timing from eating less. The writer "
                                 "therefore keeps the old advice: eat less, move "
                                 "more and sleep.",
                                 "آزمونی یافت افرادی که پیش از ده صبح صبحانه "
                                 "می‌خورند وزن بیشتری کم می‌کنند و روزنامه‌ها "
                                 "گزارش کردند که زمان مهم‌تر از مقدار است. آزمون "
                                 "فقط ۹۰ شرکت‌کننده در دوازده هفته داشت و گروه "
                                 "صبح‌زودتر شب‌ها تنقلات کمتری هم می‌خورد، پس "
                                 "نمی‌تواند زمان را از کمتر خوردن جدا کند. نویسنده "
                                 "پس همان توصیهٔ قدیمی را نگه می‌دارد: کمتر بخور، "
                                 "بیشتر حرکت کن و بخواب.")},
                ],
            },
        },
    ],
}
