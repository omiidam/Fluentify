"""Two further practices for reading for detail and for context clues."""
from reading_src import bi

MORE = {
    "detail": [
        {
            "title": bi("The reed bed that cleans a town's water",
                        "بستر نی که آب شهر را پاک می‌کند"),
            "level": "B1",
            "genre": bi("Report", "گزارش"),
            "paragraphs": [
                "Hilltown's sewage has been cleaned by reeds since 2004. "
                "Rather than a concrete tank, the town built three shallow "
                "beds planted with common reed, each about the size of a "
                "football pitch, and let the plants and the gravel do the "
                "work.",
                "Water flows slowly through the beds for nine days. Bacteria "
                "on the gravel break down the waste, the reeds take up "
                "nitrogen and phosphorus through their roots, and the gravel "
                "filters what is left. No chemicals are added at any stage.",
                "The beds cost $1.9 million to build and about $40,000 a year "
                "to run, roughly a third of the running cost of the mechanical "
                "plant they replaced. They use no electricity except for one "
                "pump, which runs for six hours a day.",
                "The limit is land. A reed bed needs about ten times the area "
                "of a mechanical plant for the same population, and it works "
                "poorly in frost. Hilltown can serve 9,000 people this way; "
                "the neighboring town of Ashby, with 60,000, cannot.",
            ],
            "summary": bi(
                "Reed beds clean sewage with plants, gravel and time, run on a "
                "third of the cost - and need ten times the land.",
                "بسترهای نی فاضلاب را با گیاه، شن و زمان پاک می‌کنند، با یک‌سوم "
                "هزینه کار می‌کنند - و ده برابر زمین می‌خواهند."),
            "questions": {
                "blanks": [
                    {"sentence": "Water flows through the beds for ___ days.",
                     "answer": "nine", "also": ["9"],
                     "hint": bi("A word, in the second paragraph.",
                                "یک کلمه، در پاراگراف دوم."),
                     "para": 2},
                    {"sentence": "The beds cost $___ million to build.",
                     "answer": "1.9", "also": ["1,9"],
                     "hint": bi("A decimal, with the building cost.",
                                "یک عدد اعشاری، کنار هزینهٔ ساخت."),
                     "para": 3},
                    {"sentence": "The single pump runs for ___ hours a day.",
                     "answer": "six", "also": ["6"],
                     "hint": bi("In the same sentence as 'no electricity'.",
                                "در همان جملهٔ «بدون برق»."),
                     "para": 3},
                ],
                "mcq": [
                    {"q": "Why does the system use almost no electricity?",
                     "options": ["The town has its own generator",
                                 "Gravity and the plants do the work",
                                 "The pump is solar powered",
                                 "It only runs in summer"],
                     "answer": 1,
                     "why": bi("Water 'flows slowly' by itself and the reeds "
                               "and gravel do the cleaning; one pump is all "
                               "that is needed.",
                               "آب خودش «به‌آرامی جریان دارد» و نی و شن پاک‌سازی را "
                               "انجام می‌دهند؛ فقط یک پمپ لازم است."),
                     "para": 2},
                    {"q": "What is the main reason Ashby cannot copy the "
                           "system?",
                     "options": ["It is too cold in winter",
                                 "It is too large for the land a reed bed "
                                 "needs",
                                 "It has no reeds",
                                 "Its water is too dirty"],
                     "answer": 1,
                     "why": bi("The limit is 'land': ten times the area, and "
                               "60,000 people is beyond what the beds could "
                               "serve.",
                               "محدودیت «زمین» است: ده برابر مساحت، و ۶۰٬۰۰۰ نفر "
                               "بیشتر از توان بسترهاست."),
                     "para": 4},
                    {"q": "How does the running cost compare with the old "
                           "plant?",
                     "options": ["About a third", "About the same",
                                 "Three times higher", "It is not stated"],
                     "answer": 0,
                     "why": bi("'Roughly a third of the running cost of the "
                               "mechanical plant they replaced.'",
                               "«حدود یک‌سوم هزینهٔ جاری کارخانهٔ مکانیکی که جایگزین "
                               "آن شدند.»"),
                     "para": 3},
                ],
                "truefalse": [
                    {"statement": "Chemicals are added to help the reeds.",
                     "answer": False,
                     "why": bi("'No chemicals are added at any stage.'",
                               "«در هیچ مرحله‌ای مادهٔ شیمیایی اضافه نمی‌شود.»"),
                     "para": 2},
                    {"statement": "The beds work badly when it freezes.",
                     "answer": True,
                     "why": bi("'It works poorly in frost.'",
                               "«در یخبندان بد کار می‌کند.»"),
                     "para": 4},
                    {"statement": "Hilltown serves 60,000 people with the "
                                  "beds.",
                     "answer": False,
                     "why": bi("Hilltown serves 9,000; 60,000 is Ashby, which "
                               "cannot use the method.",
                               "هیل‌تاون ۹٬۰۰۰ نفر را پوشش می‌دهد؛ ۶۰٬۰۰۰ مال "
                               "اشبی است که نمی‌تواند از این روش استفاده کند."),
                     "para": 4},
                ],
                "essay": [
                    {"prompt": bi("Explain why reed beds suit a town like "
                                  "Hilltown and not one like Ashby. Use the "
                                  "land figures and one cost figure.",
                                  "توضیح بده چرا بسترهای نی برای شهری مثل هیل‌تاون "
                                  "مناسب است و برای اشبی نه. از ارقام زمین و یک "
                                  "رقم هزینه استفاده کن."),
                     "min_words": 50,
                     "tips": [
                         bi("Give both population figures.",
                            "هر دو رقم جمعیت را بیاور."),
                         bi("Say what 'ten times the area' means in practice.",
                            "بگو «ده برابر مساحت» در عمل چه معنایی دارد."),
                         bi("Mention frost, because it is a second limit.",
                            "یخبندان را هم بیاور، چون محدودیت دوم است.")],
                     "model": bi("Reed beds need about ten times the area of a "
                                 "mechanical plant for the same population, "
                                 "so they only work where land is cheap and "
                                 "plentiful. Hilltown, with 9,000 people, has "
                                 "that space, and its running cost of about "
                                 "$40,000 a year is a third of the old plant's. "
                                 "Ashby has 60,000 people and would need an "
                                 "enormous site, and frost would slow the beds "
                                 "in winter, so the town must keep a mechanical "
                                 "plant.",
                                 "بسترهای نی برای همان جمعیت حدود ده برابر مساحت "
                                 "یک کارخانهٔ مکانیکی می‌خواهند، پس فقط جایی کار "
                                 "می‌کنند که زمین ارزان و فراوان باشد. هیل‌تاون با "
                                 "۹٬۰۰۰ نفر این فضا را دارد و هزینهٔ جاری حدود "
                                 "۴۰٬۰۰۰ پوند در سالش یک‌سوم کارخانهٔ قبلی است. "
                                 "اشبی ۶۰٬۰۰۰ نفر دارد و به زمینی عظیم نیاز "
                                 "داشت، و یخبندان در زمستان بسترها را کند "
                                 "می‌کند، پس باید کارخانهٔ مکانیکی را نگه دارد.")},
                ],
            },
        },
        {
            "title": bi("The tenancy agreement", "قرارداد اجاره"),
            "level": "B2",
            "genre": bi("Contract / terms", "قرارداد / شرایط"),
            "paragraphs": [
                "The tenancy of Flat 4, 12 Mill Lane begins on March 1 and runs "
                "for twelve months. Rent is $780 a month, payable on the first "
                "working day of the month. The deposit is $900 and is held by "
                "a government protection scheme, not by the landlord.",
                "The tenant may keep one cat but no dogs. Visitors may stay "
                "for up to fourteen nights in any three-month period; any "
                "longer stay must be reported to the landlord in writing. The "
                "apartment may not be sublet, and no more than two people may live "
                "in it.",
                "Repairs. The landlord is responsible for the roof, the boiler "
                "and the windows. The tenant must report a fault within 48 "
                "hours and must be at home for the appointment, or pay $25 for "
                "a missed visit.",
                "Ending the tenancy. After six months the tenant may leave by "
                "giving two months' written notice. The landlord may end it "
                "earlier only for rent more than two months overdue or for "
                "serious damage. Notice must be sent by post, not by message.",
            ],
            "summary": bi(
                "A short tenancy: what is paid and when, what is allowed, who "
                "repairs what, and the only two ways either side can end it.",
                "یک اجاره‌نامهٔ کوتاه: چه چیزی و چه وقت پرداخت می‌شود، چه چیزی "
                "مجاز است، تعمیر با کیست، و تنها دو راهی که هر طرف می‌تواند "
                "قرارداد را تمام کند."),
            "questions": {
                "blanks": [
                    {"sentence": "The rent is $___ a month.",
                     "answer": "780", "also": [],
                     "hint": bi("Three digits, in the first paragraph.",
                                "سه رقم، در پاراگراف اول."),
                     "para": 1},
                    {"sentence": "Visitors may stay up to ___ nights in three "
                                 "months.",
                     "answer": "fourteen", "also": ["14"],
                     "hint": bi("A word, about visitors.",
                                "یک کلمه، دربارهٔ مهمان‌ها."),
                     "para": 2},
                    {"sentence": "A fault must be reported within ___ hours.",
                     "answer": "48", "also": ["forty-eight"],
                     "hint": bi("In the repairs paragraph.",
                                "در پاراگراف تعمیرات."),
                     "para": 3},
                ],
                "mcq": [
                    {"q": "Who holds the deposit?",
                     "options": ["The landlord", "The tenant",
                                 "A protection scheme", "The council"],
                     "answer": 2,
                     "why": bi("'Held by a government protection scheme, not by "
                               "the landlord.'",
                               "«نزد یک طرح حمایتی دولتی نگه داشته می‌شود، نه نزد "
                               "صاحب‌خانه.»"),
                     "para": 1},
                    {"q": "How can the tenant leave after six months?",
                     "options": ["Immediately, by message",
                                 "With two months' written notice",
                                 "Only when the year ends",
                                 "By paying the deposit"],
                     "answer": 1,
                     "why": bi("'Leave by giving two months' written notice.' "
                               "Leaving at the end of the year needs no notice "
                               "at all, but the question asks about after six "
                               "months.",
                               "«با دو ماه اطلاع کتبی برود.» ماندن تا پایان سال "
                               "اطلاع لازم ندارد، ولی سؤال دربارهٔ پس از شش ماه "
                               "است."),
                     "para": 4},
                    {"q": "What does a missed repair appointment cost?",
                     "options": ["Nothing", "$25", "$48", "$900"],
                     "answer": 1,
                     "why": bi("'Or pay $25 for a missed visit.'",
                               "«یا ۲۵ پوند برای ویزیت ازدست‌رفته بپردازد.»"),
                     "para": 3},
                ],
                "truefalse": [
                    {"statement": "The tenant may sublet the flat.",
                     "answer": False,
                     "why": bi("'The apartment may not be sublet.'",
                               "«اجارهٔ دوبارهٔ آپارتمان مجاز نیست.»"),
                     "para": 2},
                    {"statement": "One late payment lets the landlord end the "
                                  "tenancy.",
                     "answer": False,
                     "why": bi("Only rent 'more than two months overdue' allows "
                               "it.",
                               "فقط اجارهٔ «بیش از دو ماه عقب‌افتاده» اجازه می‌دهد."),
                     "para": 4},
                    {"statement": "Notice must be in writing and by post.",
                     "answer": True,
                     "why": bi("'Notice must be sent by post, not by message.'",
                               "«اطلاع باید با پست فرستاده شود، نه با پیام.»"),
                     "para": 4},
                ],
                "essay": [
                    {"prompt": bi("A friend is about to sign this agreement and "
                                  "wants to keep a dog, work abroad for two "
                                  "months and rent the apartment to a cousin. Using "
                                  "the text, tell them what is and is not "
                                  "allowed.",
                                  "دوستی می‌خواهد این قرارداد را امضا کند و سگی نگه "
                                  "دارد، دو ماه خارج کار کند و آپارتمان را به "
                                  "پسرخاله‌اش اجاره بدهد. با استفاده از متن بگو چه "
                                  "چیزی مجاز است و چه چیزی نه."),
                     "min_words": 55,
                     "tips": [
                         bi("Answer the three points in the same order.",
                            "به سه نکته به همان ترتیب جواب بده."),
                         bi("Quote the exact limit for each one.",
                            "برای هر کدام محدودیت دقیق را نقل کن."),
                         bi("Say what a written report to the landlord would "
                            "not fix.",
                            "بگو گزارش کتبی به صاحب‌خانه چه چیزی را درست نمی‌کند.")],
                     "model": bi("The dog is not allowed: one cat is permitted "
                                 "and dogs are not. Working abroad for two "
                                 "months is probably fine, because the "
                                 "agreement only restricts how long visitors "
                                 "stay, but the rent must still be paid on the "
                                 "first working day and someone must be at home "
                                 "for repairs within 48 hours of a report. "
                                 "Renting the flat to a cousin is not allowed "
                                 "at all, because the apartment may not be sublet, "
                                 "and telling the landlord in writing would not "
                                 "change that.",
                                 "سگ مجاز نیست: یک گربه اجازه دارد و سگ نه. دو ماه "
                                 "کار در خارج احتمالاً اشکالی ندارد، چون قرارداد "
                                 "فقط مدت اقامت مهمان‌ها را محدود می‌کند، ولی "
                                 "اجاره باید در اولین روز کاری ماه پرداخت شود و "
                                 "کسی باید تا ۴۸ ساعت پس از گزارش برای تعمیرات "
                                 "خانه باشد. اجاره دادن آپارتمان به پسرخاله اصلاً "
                                 "مجاز نیست، چون اجارهٔ دوباره ممنوع است و اطلاع "
                                 "کتبی به صاحب‌خانه هم این را عوض نمی‌کند.")},
                ],
            },
        },
    ],
    "context": [
        {
            "title": bi("Eleven years of the same jar", "یازده سال با همان شیشه"),
            "level": "B1",
            "genre": bi("Profile", "گزارش توصیفی"),
            "paragraphs": [
                "At half past four in the morning the bakery on Rye Lane is "
                "already warm. Ama takes a jar from the shelf - the levain, a "
                "paste of flour and water that has been kept alive for eleven "
                "years - and stirs it into the dough.",
                "Nothing in the shop is bought ready-made. The dough is left to "
                "proof, covered, for six hours; when it has doubled, it is "
                "shaped and left again. The last stage, in the oven, is what "
                "gives the bread its open crumb - the holes that a supermarket "
                "loaf never has.",
                "The levain is the reason the bread tastes slightly sour. Wild "
                "yeasts and bacteria live in it, and they change with the "
                "weather: in July it rises in four hours, in January it may "
                "need eight. Ama feeds it twice a day and has never washed the "
                "jar.",
                "This is why the loaves cost $5.50. Three people work through "
                "the night, and the oven is on for nine hours. 'You cannot "
                "hurry it,' Ama says. 'You can only wait, and then sell it "
                "before it goes stale.'",
            ],
            "summary": bi(
                "A bakery raised by a living paste of flour and water, where "
                "speed is impossible and the price reflects the night's work.",
                "نانوایی‌ای که با خمیرمایهٔ زندهٔ آرد و آب کار می‌کند؛ جایی که "
                "سرعت ممکن نیست و قیمت بازتاب کار شب است."),
            "questions": {
                "blanks": [
                    {"sentence": "The levain has been kept alive for ___ years.",
                     "answer": "eleven", "also": ["11"],
                     "hint": bi("A word, in the first paragraph.",
                                "یک کلمه، در پاراگراف اول."),
                     "para": 1},
                    {"sentence": "The dough is left to proof for ___ hours.",
                     "answer": "six", "also": ["6"],
                     "hint": bi("Before it is shaped.",
                                "پیش از شکل گرفتن."),
                     "para": 2},
                    {"sentence": "A loaf costs $___.",
                     "answer": "5.50", "also": ["5,50"],
                     "hint": bi("A price, in the last paragraph.",
                                "یک قیمت، در پاراگراف آخر."),
                     "para": 4},
                ],
                "mcq": [
                    {"q": "What is the levain?",
                     "options": ["A kind of oven",
                                 "A living mixture of flour and water used to "
                                 "raise dough",
                                 "A shop-bought additive",
                                 "A type of bread"],
                     "answer": 1,
                     "why": bi("The dash defines it: 'a paste of flour and "
                               "water that has been kept alive', and later it "
                               "'rises' - so it is what raises the dough.",
                               "خط تیره تعریفش می‌کند: «خمیری از آرد و آب که زنده "
                               "نگه داشته شده» و بعد «ورمی‌آید»؛ پس همان چیزی است "
                               "که خمیر را می‌ورآورد."),
                     "para": 1},
                    {"q": "What does the passage say about the levain's speed?",
                     "options": ["It is always the same",
                                 "It changes with the weather",
                                 "It stops working in winter",
                                 "It depends on the oven"],
                     "answer": 1,
                     "why": bi("'They change with the weather: in July it rises "
                               "in four hours, in January it may need eight.'",
                               "«با هوا تغییر می‌کنند: در ژوئیه در چهار ساعت "
                               "ورمی‌آید، در ژانویه ممکن است هشت ساعت بخواهد.»"),
                     "para": 3},
                    {"q": "Why does a loaf cost $5.50?",
                     "options": ["The flour is imported",
                                 "The oven is expensive to buy",
                                 "Three people work all night and the oven runs "
                                 "for nine hours",
                                 "The shop is in a rich area"],
                     "answer": 2,
                     "why": bi("The price is explained by the labor and the "
                               "oven time, not by ingredients.",
                               "قیمت با کار و زمان پخت توضیح داده می‌شود، نه با "
                               "مواد اولیه."),
                     "para": 4},
                ],
                "truefalse": [
                    {"statement": "The bakery buys its dough ready-made.",
                     "answer": False,
                     "why": bi("'Nothing in the shop is bought ready-made.'",
                               "«هیچ‌چیز در مغازه آماده خریداری نمی‌شود.»"),
                     "para": 2},
                    {"statement": "Ama washes the jar regularly.",
                     "answer": False,
                     "why": bi("'Ama feeds it twice a day and has never washed "
                               "the jar.'",
                               "«آما دو بار در روز غذا می‌دهد و هیچ‌وقت شیشه را "
                               "نشسته است.»"),
                     "para": 3},
                    {"statement": "The bread tastes slightly sour.",
                     "answer": True,
                     "why": bi("'The levain is the reason the bread tastes "
                               "slightly sour.'",
                               "«خمیرمایه دلیل ترشی خفیف نان است.»"),
                     "para": 3},
                ],
                "essay": [
                    {"prompt": bi("Guess the meaning of 'crumb' from its "
                                  "sentence, and explain the two clues that "
                                  "let you guess. Then guess 'stale'.",
                                  "معنی «crumb» را از جمله‌اش حدس بزن و دو نشانه‌ای "
                                  "را توضیح بده که به حدس رساندت. بعد «stale» را "
                                  "حدس بزن."),
                     "min_words": 50,
                     "tips": [
                         bi("Quote the words that define each term.",
                            "واژه‌هایی را نقل کن که هر اصطلاح را تعریف می‌کنند."),
                         bi("Say what is being contrasted, not just what is "
                            "described.",
                            "بگو چه چیزی با چه چیزی مقایسه می‌شود، نه فقط چه چیزی "
                            "توصیف می‌شود."),
                         bi("Give a one-word synonym for each guess.",
                            "برای هر حدس یک مترادف یک‌کلمه‌ای بده.")],
                     "model": bi("'Crumb' must mean the inside of the loaf, "
                                 "because the passage calls it 'the holes that "
                                 "a supermarket loaf never has' - holes are "
                                 "inside bread, not on it - and it comes right "
                                 "after the oven, which sets the inside. 'Stale' "
                                 "means too old to sell, since the baker says to "
                                 "sell it 'before' that happens. So crumb is the "
                                 "texture, and stale is the age.",
                                 "«crumb» باید معنای داخل نان را بدهد، چون متن آن را "
                                 "«حفره‌هایی که نان سوپرمارکت هرگز ندارد» "
                                 "می‌نامد؛ حفره‌ها داخل نان‌اند، نه روی آن؛ و بلافاصله "
                                 "بعد از تنور می‌آید که داخل را می‌پزد. «stale» "
                                 "یعنی زیادی کهنه برای فروش، چون نانوا می‌گوید "
                                 "«پیش از» آن بفروشش. پس crumb بافت است و stale "
                                 "سن.")},
                ],
            },
        },
        {
            "title": bi("Your first afternoon on the lake",
                        "اولین بعدازظهر تو روی دریاچه"),
            "level": "B1",
            "genre": bi("Course information", "اطلاعات دوره"),
            "paragraphs": [
                "The first lesson is on the water, not in a classroom. You "
                "will learn to read the wind: a dark line moving across the "
                "lake is a gust, a sudden push that can tip the boat if you are "
                "not ready for it.",
                "Sailing upwind means tacking - turning the front of the boat "
                "through the wind again and again, in a zigzag, because a boat "
                "cannot sail straight into the wind. Downwind you simply let "
                "the sail out and the boat runs before the wind.",
                "Beginners capsize, and the course plans for it. The water is "
                "shallow, the boats are unsinkable, and the instructor stands "
                "beside you in a second boat. Bring a change of clothes; you "
                "will need them.",
                "Courses run on Saturdays from April to October, cost $120 for "
                "six sessions, and are limited to eight people. Nobody has ever "
                "been asked to leave for falling in.",
            ],
            "summary": bi(
                "A beginner's course: reading gusts, zigzagging upwind, and "
                "turning over being an expected part of the afternoon.",
                "دورهٔ مقدماتی: خواندن بادهای ناگهانی، زیگزاگ در جهت باد، و "
                "واژگون شدن به‌عنوان بخشی منتظره از بعدازظهر."),
            "questions": {
                "blanks": [
                    {"sentence": "A dark line moving across the lake is a ___.",
                     "answer": "gust", "also": [],
                     "hint": bi("A short word for a sudden push of wind.",
                                "واژه‌ای کوتاه برای فشار ناگهانی باد."),
                     "para": 1},
                    {"sentence": "Turning the boat through the wind is called "
                                 "___.",
                     "answer": "tacking", "also": ["tack"],
                     "hint": bi("The -ing word before the dash.",
                                "واژهٔ ing پیش از خط تیره."),
                     "para": 2},
                    {"sentence": "Six sessions cost $___.",
                     "answer": "120", "also": [],
                     "hint": bi("In the last paragraph.",
                                "در پاراگراف آخر."),
                     "para": 4},
                ],
                "mcq": [
                    {"q": "What does 'capsize' mean here?",
                     "options": ["To sail very fast",
                                 "To turn the boat over in the water",
                                 "To leave the course",
                                 "To change direction"],
                     "answer": 1,
                     "why": bi("The next sentences explain it: the water is "
                               "shallow, the boats cannot sink, and you need "
                               "dry clothes - all consequences of turning over.",
                               "جمله‌های بعد توضیحش می‌دهند: آب کم‌عمق است، قایق‌ها "
                               "غرق نمی‌شوند و لباس خشک لازم داری؛ همه نتیجهٔ "
                               "واژگون شدن."),
                     "para": 3},
                    {"q": "Why does a boat sail in a zigzag?",
                     "options": ["To avoid other boats",
                                 "Because it cannot sail straight into the wind",
                                 "To go faster downwind",
                                 "Because the lake is shallow"],
                     "answer": 1,
                     "why": bi("'Because a boat cannot sail straight into the "
                               "wind.'",
                               "«چون قایق نمی‌تواند مستقیم به سمت باد برود.»"),
                     "para": 2},
                    {"q": "What does 'unsinkable' tell you about the boats?",
                     "options": ["They are very expensive",
                                 "They cannot go under, so falling in is safe",
                                 "They are too small for two people",
                                 "They are new this year"],
                     "answer": 1,
                     "why": bi("It is offered as reassurance next to "
                               "'shallow' and 'the instructor stands beside "
                               "you'.",
                               "کنار «کم‌عمق» و «مربی در قایق دوم کنارت است» "
                               "به‌عنوان دلگرمی آمده."),
                     "para": 3},
                ],
                "truefalse": [
                    {"statement": "The first lesson takes place in a classroom.",
                     "answer": False,
                     "why": bi("'The first lesson is on the water, not in a "
                               "classroom.'",
                               "«درس اول روی آب است، نه در کلاس.»"),
                     "para": 1},
                    {"statement": "The lake is deep.",
                     "answer": False,
                     "why": bi("'The water is shallow.'", "«آب کم‌عمق است.»"),
                     "para": 3},
                    {"statement": "Falling in is treated as normal.",
                     "answer": True,
                     "why": bi("'Nobody has ever been asked to leave for "
                               "falling in.'",
                               "«هیچ‌کس هرگز به‌خاطر افتادن در آب اخراج نشده است.»"),
                     "para": 4},
                ],
                "essay": [
                    {"prompt": bi("Explain 'tacking' to a friend who has never "
                                  "sailed, using the passage only. Then say "
                                  "which word in the text helped you most.",
                                  "«tacking» را برای دوستی که هرگز قایق‌سواری "
                                  "نکرده توضیح بده، فقط با استفاده از متن. بعد بگو "
                                  "کدام کلمهٔ متن بیشتر کمک کرد."),
                     "min_words": 45,
                     "tips": [
                         bi("Give the image first: zigzag.",
                            "اول تصویر را بده: زیگزاگ."),
                         bi("Explain why straight is impossible.",
                            "توضیح بده چرا مستقیم ممکن نیست."),
                         bi("Name the word that carries the meaning.",
                            "واژه‌ای را نام ببر که معنی را حمل می‌کند.")],
                     "model": bi("Tacking is how you get to a place that lies "
                                 "upwind: instead of pointing straight at it, "
                                 "you turn the front of the boat through the "
                                 "wind again and again, so you travel in a "
                                 "zigzag. It works because a boat cannot sail "
                                 "straight into the wind, but it can sail at an "
                                 "angle to it. The word that helped me most was "
                                 "'zigzag', because it is a shape I can picture.",
                                 "تکینگ راهی است برای رسیدن به جایی که در جهت باد "
                                 "است: به‌جای نشانه گرفتن مستقیم، جلوی قایق را "
                                 "بارها از میان باد می‌چرخانی، پس زیگزاگ حرکت "
                                 "می‌کنی. کار می‌کند چون قایق نمی‌تواند مستقیم به "
                                 "سمت باد برود، ولی با زاویه می‌تواند. واژه‌ای که "
                                 "بیشتر کمکم کرد «zigzag» بود، چون شکلی است که "
                                 "می‌توانم تصورش کنم.")},
                ],
            },
        },
    ],
}
