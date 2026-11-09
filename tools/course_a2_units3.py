#!/usr/bin/env python3
"""A2 · units 5-6: comparing, counting, and what the body needs.

Unit 5 compares places and prices and ends in a short article about a market;
unit 6 divides the world into countable and uncountable, and uses that grammar
in the pharmacy, where amounts and instructions matter.
"""

from course_kit import dialogue, gap, lesson, listen, mcq, passage, unit

U5 = unit(
    "a2-u5",
    ("Bigger and better", "بزرگ‌تر و بهتر"),
    ("Compare two things, say how much difference there is, and shop without being cheated.", "دو چیز را مقایسه کن، اندازهٔ تفاوت را بگو و بدون فریب خرید کن."),
    [
        lesson(
            "a2-u5-l1",
            "grammar",
            ("Comparatives and superlatives", "صفت‌های برتر و برترین"),
            ("Compare two things with -er/more, and one against all with -est/most.", "دو چیز را با er/more و یکی را با همه با est/most مقایسه کن."),
            [
                ("Short adjectives add -er and -est: cheap → cheaper → the cheapest; big → bigger → the biggest (double the consonant after one vowel + one consonant); easy → easier → the easiest (y → i).", "صفت‌های کوتاه er و est می‌گیرند: cheap ← cheaper ← the cheapest؛ big ← bigger ← the biggest (بعد از یک مصوت + یک صامت، صامت تکرار می‌شود)؛ easy ← easier ← the easiest (y به i تبدیل می‌شود)."),
                ("Longer adjectives take more and most: expensive → more expensive → the most expensive. Never 'more cheaper'.", "صفت‌های بلندتر more و most می‌گیرند: expensive ← more expensive ← the most expensive. هرگز «more cheaper»."),
                ("Irregular: good → better → the best; bad → worse → the worst; far → further → the furthest. Than introduces the second thing: Tehran is bigger than Karaj.", "بی‌قاعده: good ← better ← best؛ bad ← worse ← worst؛ far ← further ← furthest. than چیز دوم را معرفی می‌کند: Tehran is bigger than Karaj."),
                ("Say how big the difference is: much, far and a lot go before the comparative, a bit and slightly too, and (not) as … as says two things are equal: this one isn't as good as that one.", "اندازهٔ تفاوت را بگو: much، far و a lot قبل از صفت برتر می‌آیند، a bit و slightly هم همین‌طور، و (not) as … as برابری دو چیز را می‌گوید: this one isn't as good as that one."),
            ],
            [
                ("This apartment is cheaper than the one near the park.", "این آپارتمان از آن یکی نزدیک پارک ارزان‌تر است."),
                ("Today is much colder than yesterday.", "امروز از دیروز خیلی سردتر است."),
                ("It's the best restaurant in the city, but it's also the most expensive.", "بهترین رستوران شهر است، اما گران‌ترین هم هست."),
                ("My new phone is slightly bigger but not as fast as the old one.", "گوشی جدیدم کمی بزرگ‌تر است اما به سرعت قبلی نیست."),
            ],
            [
                mcq("This bag is ___ than that one.", "این کیف از آن یکی ___ است.", ["cheapper", "more cheap", "cheaper", "cheapest"], 2,
                    "One-syllable adjectives add -er, with no doubling here: cheaper.", "صفت‌های یک‌هجایی er می‌گیرند، بدون تکرار حرف: cheaper."),
                mcq("What is the superlative of 'bad'?", "برترین شکل «bad» چیست؟", ["baddest", "most bad", "worse", "the worst"], 3,
                    "Bad → worse → the worst.", "صفت برترین bad واژهٔ the worst است."),
            ],
            [
                gap("This road is ___ (narrow) than the main street.", ["narrower"], "Two syllables ending in -ow take -er: narrower.", "two-syllable با پایان ow شکل er می‌گیرد: narrower."),
                gap("It's ___ most beautiful building in the town.", ["the"], "Superlatives take the definite article.", "صفت برترین حرف تعریف می‌گیرد."),
                gap("The new version is ___ better than the old one — a huge difference.", ["much", "far", "a lot"], "much/far/a lot before a comparative show a big difference.", "much/far/a lot قبل از صفت برتر تفاوت بزرگ را نشان می‌دهند."),
                mcq("Which sentence is correct?", "کدام جمله درست است؟", ["She is more taller than me.", "She is taller than me.", "She is tallest than me.", "She is more tall than me."], 1,
                    "Tall takes -er; use one comparative form only.", "tall شکل er می‌گیرد؛ فقط یک شکل برتر به کار ببر."),
            ],
        ),
        lesson(
            "a2-u5-l2",
            "vocabulary",
            ("Shopping, money and getting a refund", "خرید، پول و پس گرفتن وجه"),
            ("Buy, return and complain with the words shops actually use.", "با واژه‌هایی که فروشگاه‌ها واقعاً به کار می‌برند بخر، پس بده و شکایت کن."),
            [
                ("The paper trail of a purchase: you pay by card or in cash, and you keep the receipt. The receipt is your proof, so without it a return is difficult.", "ردّ کاغذی خرید: با کارت یا نقد پول می‌دهی و رسید را نگه می‌داری. رسید مدرک توست، پس بدون آن پس دادن سخت است."),
                ("Problems: it doesn't fit, it's the wrong size, it's faulty, it's broken. You ask for a refund (money back), an exchange (another one), or a repair. A warranty covers faults for a period.", "مشکل‌ها: اندازه نیست، سایز اشتباه است، معیوب است، شکسته است. refund (پس دادن پول)، exchange (تعویض) یا repair (تعمیر) می‌خواهی. warranty خرابی را برای مدتی پوشش می‌دهد."),
                ("Prices and value: a discount is a reduction, a bargain is something cheap for its value, and 'on sale' means the shop has reduced it. A line is what you wait in; a fitting room is where you try clothes.", "قیمت و ارزش: discount تخفیف، bargain چیزی ارزان نسبت به ارزشش و on sale یعنی فروشگاه قیمت را کم کرده است. line صفی است که در آن می‌ایستی و fitting room اتاق پرو است."),
            ],
            [
                ("Can I pay by card, or is it cash only?", "می‌توانم با کارت پرداخت کنم یا فقط نقدی است؟"),
                ("I'd like a refund, please. Here's the receipt.", "می‌خواهم پولم را پس بگیرم. این هم رسید."),
                ("These shoes were faulty, so they exchanged them without a problem.", "این کفش‌ها معیوب بودند، پس بدون مشکل عوضش کردند."),
                ("It was half price, so it was a real bargain.", "نصف قیمت بود، پس واقعاً ارزان و به‌صرفه بود."),
            ],
            [
                mcq("You want your money back. You ask for a ___.", "پولت را می‌خواهی. ___ می‌خواهی.", ["receipt", "refund", "discount", "line"], 1,
                    "A refund returns the money you paid.", "refund پولی را که داده‌ای برمی‌گرداند."),
                mcq("A product with a problem is ___.", "محصولی که مشکل دارد ___ است.", ["faulty", "bargain", "receipt", "warranty"], 0,
                    "Faulty means it has a fault.", "faulty یعنی عیب دارد."),
            ],
            [
                gap("Keep the ___ , or you can't return the item.", ["receipt"], "The receipt is the proof of purchase.", "رسید مدرک خرید است."),
                gap("There's a 20% ___ on everything this week.", ["discount"], "A reduction in price is a discount.", "کاهش قیمت discount است."),
                mcq("'It's faulty' means ___.", "«It's faulty» یعنی ___.", ["it is expensive", "it does not work properly", "it is the wrong color", "it is on sale"], 1,
                    "Faulty: it does not work as it should.", "faulty: آن‌طور که باید کار نمی‌کند."),
                listen("I bought this kettle last week and it stopped working yesterday. — Do you have the receipt? — Yes, here it is. — Then I can give you a refund or an exchange.", "What does the shop offer?", "فروشگاه چه پیشنهاد می‌دهد؟", ["only a repair", "a refund or an exchange", "nothing without a warranty", "a discount"], 1,
                       "With the receipt, the shop offers a refund or an exchange.", "با رسید، فروشگاه بازپرداخت یا تعویض پیشنهاد می‌دهد."),
            ],
        ),
        lesson(
            "a2-u5-l3",
            "reading",
            ("The Thursday market", "بازار پنجشنبه"),
            ("Read a short article about a market and separate the writer's facts from her opinion.", "مقالهٔ کوتاهی دربارهٔ یک بازار بخوان و واقعیت‌ها را از نظر نویسنده جدا کن."),
            [
                ("A short article gives facts (where, when, what is sold, how much) and opinions (better, best, I love). Facts can be checked; opinions carry the writer's view.", "مقالهٔ کوتاه واقعیت‌ها (کجا، کِی، چه چیزی، چند) و نظرها (better، best، I love) را با هم می‌آورد. واقعیت‌ها را می‌توان بررسی کرد؛ نظرها دید نویسنده را دارند."),
                ("Comparatives are the writer's tool for recommending: cheaper than the supermarket, the freshest vegetables, busier in the morning. Read them as judgment, not measurement.", "صفت‌های برتر ابزار توصیهٔ نویسنده‌اند: cheaper than the supermarket، the freshest vegetables، busier in the morning. آن‌ها را داوری بخوان، نه اندازه‌گیری."),
            ],
            [
                ("Facts: it opens at seven on Thursday mornings, behind the old movie theater.", "واقعیت: پنجشنبه‌ها ساعت هفت صبح، پشت سینمای قدیمی باز می‌شود."),
                ("Opinion: it is the friendliest market in the city.", "نظر: صمیمی‌ترین بازار شهر است."),
                ("Recommendation: arrive before nine, because the best bread goes first.", "توصیه: قبل از نه برس، چون بهترین نان اول تمام می‌شود."),
            ],
            [
                mcq("When is the market open?", "بازار کِی باز است؟", ["every morning", "on Thursday mornings", "on Thursday evenings", "on Fridays"], 1,
                    "It opens at seven on Thursday mornings.", "پنجشنبه‌ها ساعت هفت صبح باز می‌شود."),
                mcq("Which sentence is an opinion, not a fact?", "کدام جمله نظر است، نه واقعیت؟", ["It opens at seven.", "It is behind the old movie theater.", "It is the friendliest market in the city.", "It sells vegetables."], 2,
                    "'Friendly' is a judgment the writer makes.", "«صمیمی» داوری نویسنده است."),
            ],
            [
                mcq("Why should you arrive before nine?", "چرا باید قبل از نه برسی؟", ["the market closes at nine", "the best bread sells quickly", "prices rise at nine", "the movie theater opens"], 1,
                    "'The best bread goes first' — it sells out early.", "«بهترین نان اول می‌رود» یعنی زود تمام می‌شود."),
                mcq("What does the writer compare the market with?", "نویسنده بازار را با چه چیزی مقایسه می‌کند؟", ["the movie theater", "a supermarket", "a restaurant", "another city"], 1,
                    "She says the vegetables are cheaper than at the supermarket.", "می‌گوید سبزی‌ها از سوپرمارکت ارزان‌ترند."),
                mcq("How does the writer feel about the market?", "نویسنده دربارهٔ بازار چه حسی دارد؟", ["She dislikes the crowds.", "She thinks it is the best place to shop.", "She thinks it is too expensive.", "She has never been there."], 1,
                    "She calls it the friendliest and recommends it.", "آن را صمیمی‌ترین می‌خواند و توصیه می‌کند."),
                mcq("'The best bread goes first' means ___.", "«The best bread goes first» یعنی ___.", ["the bread is free", "the good bread sells out early", "they bake at nine", "the bread is the cheapest thing"], 1,
                    "Goes first here means it is sold earliest.", "goes first اینجا یعنی زودتر فروخته می‌شود."),
            ],
            passage=passage(("The Thursday market", "بازار پنجشنبه"),
                            ("Every Thursday morning, behind the old movie theater, the market opens at seven. There are about forty stalls: vegetables, bread, cheese, second-hand books and one very good coffee cart.\n\nThe vegetables are cheaper than at the supermarket and much fresher, because most of them come from farms outside the city. The cheese stall is the most popular, and the line is longest at about eight.\n\nIt is the friendliest market in the city. Come before nine if you want the best bread — it always goes first.",
                             "هر پنجشنبه صبح، پشت سینمای قدیمی، بازار ساعت هفت باز می‌شود. حدود چهل غرفه هست: سبزی، نان، پنیر، کتاب دست‌دوم و یک چرخ قهوهٔ خیلی خوب.\n\nسبزی‌ها از سوپرمارکت ارزان‌تر و بسیار تازه‌ترند، چون بیشترشان از مزرعه‌های بیرون شهر می‌آیند. غرفهٔ پنیر محبوب‌ترین است و صف حدود ساعت هشت بلندترین است.\n\nصمیمی‌ترین بازار شهر است. اگر بهترین نان را می‌خواهی قبل از نه بیا؛ همیشه اول تمام می‌شود.")),
        ),
    ],
)

U6 = unit(
    "a2-u6",
    ("How much, how many", "چقدر، چندتا"),
    ("Count what can be counted, measure what cannot, and follow instructions at the pharmacy.", "آنچه شمرده می‌شود را بشمار، آنچه نمی‌شود را اندازه بگیر و دستورهای داروخانه را دنبال کن."),
    [
        lesson(
            "a2-u6-l1",
            "grammar",
            ("Countable, uncountable, and the quantifiers", "شماردنی، نشماردنی و کمیت‌سنج‌ها"),
            ("Use much/many, some/any, a few/a little and enough correctly.", "much/many، some/any، a few/a little و enough را درست به کار ببر."),
            [
                ("Countable nouns have a plural and take a number: one apple, two apples. Uncountable nouns have no plural and take a singular verb: water, rice, money, advice, information, news. 'Two informations' is impossible.", "اسم‌های شماردنی جمع می‌بندند و عدد می‌گیرند: one apple، two apples. اسم‌های نشماردنی جمع ندارند و فعل مفرد می‌گیرند: water، rice، money، advice، information، news. «Two informations» ممکن نیست."),
                ("Many goes with plurals, much with uncountables, and both are usual in negatives and questions: How many tickets? How much time? In positive sentences, a lot of is more natural.", "many با جمع و much با نشماردنی می‌آید و هر دو در منفی و پرسشی طبیعی‌اند: How many tickets? How much time? در جملهٔ مثبت a lot of طبیعی‌تر است."),
                ("Some in positives, any in negatives and questions: I need some milk. We don't have any bread. Do you have any questions? Some also appears in offers: Would you like some tea?", "some در مثبت و any در منفی و پرسشی: I need some milk. We don't have any bread. Do you have any questions? some در پیشنهاد هم می‌آید: Would you like some tea?"),
                ("A few counts (a few friends), a little measures (a little sugar). Enough means as much as needed and comes after the adjective but before the noun: it's warm enough, enough time.", "a few می‌شمارد (a few friends) و a little اندازه می‌گیرد (a little sugar). enough یعنی به‌اندازهٔ لازم و بعد از صفت اما قبل از اسم می‌آید: it's warm enough، enough time."),
            ],
            [
                ("How much rice do we need for six people?", "برای شش نفر چقدر برنج لازم داریم؟"),
                ("There aren't many seats left.", "صندلی زیادی باقی نمانده است."),
                ("Could I have a little more water, please?", "می‌شود کمی آب بیشتر بدهم؟"),
                ("We don't have enough time to finish today.", "وقت کافی نداریم امروز تمام کنیم."),
                ("Only a few people came, but they had a lot of questions.", "آدم‌های کمی آمدند، اما پرسش‌های زیادی داشتند."),
            ],
            [
                mcq("How ___ money do you need?", "چقدر پول لازم داری؟", ["many", "much", "few", "some"], 1,
                    "Money is uncountable, so how much.", "money نشماردنی است، پس how much."),
                mcq("There aren't ___ chairs in the room.", "در اتاق صندلی ___ نیست.", ["much", "a little", "many", "enough of"], 2,
                    "Chairs are countable, so many in a negative.", "chair شماردنی است، پس در منفی many."),
            ],
            [
                gap("We have ___ milk, but we need more for the cake.", ["a little"], "A small amount of an uncountable noun.", "مقدار کم از اسم نشماردنی."),
                gap("Do you have ___ information about the course?", ["any"], "any in a question.", "any در پرسش."),
                mcq("Which sentence is correct?", "کدام جمله درست است؟", ["I have many informations.", "I have a lot of information.", "I have much information.", "I have a lot of informations."], 1,
                    "Information is uncountable: a lot of information.", "information نشماردنی است: a lot of information."),
                listen("Take this medicine twice a day, and drink a little water with it. Don't take more than four in twenty-four hours.", "How often should you take the medicine?", "هر چند وقت یک بار باید دارو را بخوری؟", ["once a day", "twice a day", "four times a day", "every hour"], 1,
                       "Twice a day, and no more than four in twenty-four hours.", "دو بار در روز و بیشتر از چهار تا در بیست‌وچهار ساعت نه."),
            ],
        ),
        lesson(
            "a2-u6-l2",
            "vocabulary",
            ("Health: symptoms, the pharmacy and advice", "سلامت: نشانه‌ها، داروخانه و توصیه"),
            ("Describe how you feel, buy the right medicine and understand the instructions.", "بگو چه حسی داری، داروی درست را بخر و دستورها را بفهم."),
            [
                ("Say what hurts with have: I have a headache, a sore throat, a cough, a temperature. A pain is in a place: a pain in my back. Dizzy and sick describe how you feel.", "درد را با have بگو: I have a headache، a sore throat، a cough، a temperature. pain در یک نقطه است: a pain in my back. dizzy و sick حال تو را توصیف می‌کنند."),
                ("The pharmacy, also called a drugstore, sells medicine; in British English it is the chemist's. A prescription is the doctor's paper you need for stronger medicine. Tablets, capsules, syrup; a dose is how much you take at one time.", "داروخانه (در انگلیسی بریتانیایی chemist's) دارو می‌فروشد؛ prescription کاغذ پزشک برای داروهای قوی‌تر است. tablet، capsule، syrup؛ dose مقدار مصرف در هر نوبت است."),
                ("Instructions are fixed phrases: take one tablet twice a day, after food, with water, do not exceed the dose, keep out of reach of children. Miss a dose? Take it when you remember, unless it is nearly time for the next one.", "دستورها عبارت‌های ثابت دارند: take one tablet twice a day، after food، with water، do not exceed the dose، keep out of reach of children. اگر یک نوبت را فراموش کردی، وقتی یادت آمد بخور، مگر اینکه نوبت بعدی نزدیک باشد."),
            ],
            [
                ("I've got a sore throat and a slight temperature.", "گلویم درد می‌کند و کمی تب دارم."),
                ("Take one tablet after food, twice a day.", "روزی دو بار، هر بار یک قرص بعد از غذا."),
                ("You don't need a prescription for these; they're over the counter.", "این‌ها نسخه لازم ندارند؛ بدون نسخه فروخته می‌شوند."),
                ("If the pain continues for more than three days, see a doctor.", "اگر درد بیش از سه روز ادامه داشت، به پزشک مراجعه کن."),
            ],
            [
                mcq("A paper from the doctor for medicine is a ___.", "کاغذ پزشک برای دارو ___ است.", ["receipt", "prescription", "dose", "tablet"], 1,
                    "The prescription is what the pharmacy dispenses.", "prescription چیزی است که داروخانه تحویل می‌دهد."),
                mcq("'Twice a day' means ___.", "«Twice a day» یعنی ___.", ["once every two days", "two times a day", "two tablets at once", "for two days"], 1,
                    "Twice = two times.", "twice یعنی دو بار."),
            ],
            [
                gap("I've got a ___ throat, so it hurts to talk.", ["sore"], "A sore throat is the fixed phrase.", "sore throat عبارت ثابت است."),
                gap("Take the tablets ___ food, not on an empty stomach.", ["after"], "After food means following a meal.", "after food یعنی بعد از غذا."),
                mcq("'Do not exceed the dose' means ___.", "«Do not exceed the dose» یعنی ___.", ["take less than one", "do not take more than the stated amount", "take it with water", "take it at night"], 1,
                    "Exceed means to go beyond the stated amount.", "exceed یعنی از مقدار گفته‌شده بیشتر رفتن."),
                mcq("You feel hot and your head hurts. You probably have ___.", "بدنت داغ است و سرت درد می‌کند. احتمالاً ___ داری.", ["a cough", "a temperature", "a prescription", "a dose"], 1,
                    "A temperature means your body is hotter than normal.", "temperature یعنی بدنت از حد معمول گرم‌تر است."),
            ],
        ),
        lesson(
            "a2-u6-l3",
            "listening",
            ("At the pharmacy", "در داروخانه"),
            ("Follow a short consultation and take the right medicine at the right time.", "مشاورهٔ کوتاهی را دنبال کن و داروی درست را در زمان درست بخور."),
            [
                ("A pharmacy conversation follows a route: symptoms, how long, what you have tried, what is recommended, how to take it. Listen for the amount and the frequency, because those are the instructions you will follow at home.", "گفت‌وگوی داروخانه مسیر خودش را دارد: نشانه‌ها، مدت، چیزهایی که امتحان کرده‌ای، توصیه و نحوهٔ مصرف. به مقدار و تعداد نوبت‌ها گوش کن، چون همان‌ها دستورهایی است که در خانه انجام می‌دهی."),
                ("Warning phrases matter as much as the medicine: not with milk, on an empty stomach, for children only, if it gets worse. One small word changes the instruction.", "عبارت‌های هشدار به‌اندازهٔ خود دارو مهم‌اند: not with milk، on an empty stomach، for children only، if it gets worse. یک واژهٔ کوچک دستور را عوض می‌کند."),
            ],
            [
                ("'How long have you had the cough?' — 'About a week.'", "«چند وقت است سرفه می‌کنی؟» — «حدود یک هفته»."),
                ("'Take this syrup three times a day, after meals.'", "«این شربت را روزی سه بار بعد از غذا بخور»."),
                ("'If you still have a temperature on Friday, come back.'", "«اگر جمعه هنوز تب داشتی، برگرد»."),
            ],
            [
                listen("Good morning, how can I help? — I've had a headache for three days. — Have you taken anything? — Just tea. — Try these tablets, one every eight hours, after food.", "How often should she take the tablets?", "هر چند وقت یک بار باید قرص‌ها را بخورد؟", ["once a day", "every four hours", "every eight hours", "three at once"], 2,
                       "One tablet every eight hours.", "هر هشت ساعت یک قرص."),
                listen("Good morning, how can I help? — I've had a headache for three days. — Have you taken anything? — Just tea. — Try these tablets, one every eight hours, after food.", "How long has she had the headache?", "چند وقت است سردرد دارد؟", ["three hours", "eight days", "three days", "a week"], 2,
                       "She says 'for three days'.", "می‌گوید «for three days»."),
            ],
            [
                listen("These are for children, so keep them out of reach. — Of course. And can I take them with milk? — No, take them with water.", "What should the customer avoid?", "مشتری از چه چیزی پرهیز کند؟", ["water", "milk with the medicine", "food", "the pharmacy"], 1,
                       "The pharmacist says no milk, take them with water.", "داروساز می‌گوید شیر نه، با آب بخور."),
                listen("It's a sore throat. Use this spray twice a day and drink warm water. If it gets worse after five days, see a doctor. You don't need a prescription for the spray.", "When should the customer see a doctor?", "کِی باید مشتری به پزشک برود؟", ["immediately", "if it is worse after five days", "after ten days", "never"], 1,
                       "Five days without improvement is the trigger.", "پنج روز بدون بهبود، شرط مراجعه است."),
                mcq("The customer asks about a prescription because ___.", "مشتری دربارهٔ نسخه می‌پرسد چون ___.", ["the spray is expensive", "he wants to know if he needs one", "the pharmacy is closed", "he has no money"], 1,
                    "The pharmacist says no prescription is needed.", "داروساز می‌گوید نسخه لازم نیست."),
                mcq("'Keep out of reach of children' means ___.", "«Keep out of reach of children» یعنی ___.", ["children can take it", "store it where children cannot get it", "it is for children", "give it to children twice a day"], 1,
                    "Reach: children must not be able to touch it.", "reach: بچه‌ها نباید به آن دسترسی داشته باشند."),
            ],
        ),
    ],
)
