#!/usr/bin/env python3
"""The A2 final examination: 33 marks over six sections.

Eight grammar, eight vocabulary, two passages with three questions each, six
listening items, two writing tasks and three speaking tasks. The pass rule is
the one the level check already uses: 60% overall, 50% in every skill, and every
skill actually assessed.
"""

from course_kit import exam, listen, mcq, reading_item, say, section, write

BLURB = (
    "Six skills, each marked on its own. Grammar, vocabulary, reading and listening are marked from your answers; writing is marked against a rubric; speaking is marked from what this device hears you say. You need 60% overall, at least 50% in every skill, and all six skills must be assessed.",
    "شش مهارت، هر یک جداگانه. گرامر، واژگان، خواندن و شنیدن از پاسخ‌ها نمره می‌گیرند؛ نوشتن با معیارهای مشخص و گفتن از آنچه دستگاه می‌شنود. برای قبولی ۶۰٪ کل و ۵۰٪ در هر مهارت لازم است و هر شش مهارت باید سنجیده شود.",
)

GRAMMAR = [
    mcq("We ___ to the beach last Friday.", "جمعهٔ گذشته به ساحل ___.", ["go", "went", "have gone", "were going"], 1,
        "Last Friday is a finished time, so the past simple: went.", "جمعهٔ گذشته زمان تمام‌شده است، پس گذشتهٔ ساده: went."),
    mcq("While I ___ the dishes, the phone rang.", "وقتی ___ ظرف‌ها بودم، تلفن زنگ زد.", ["washed", "was washing", "wash", "have washed"], 1,
        "The background action interrupted by a short event takes the past continuous.", "کار پس‌زمینه‌ای که رویداد کوتاهی آن را قطع کرده، گذشتهٔ استمراری می‌گیرد."),
    mcq("___ you ever ___ to a concert?", "تا حالا به کنسرت ___ ای؟", ["Did / go", "Have / been", "Have / go", "Do / go"], 1,
        "Experience questions use have + past participle: have you ever been.", "پرسش تجربه با have + اسم مفعول: have you ever been."),
    mcq("Don't worry, I ___ you with the boxes.", "نگران نباش، در جابه‌جایی جعبه‌ها ___ .", ["am helping", "help", "will help", "helped"], 2,
        "A promise made at the moment of speaking takes will.", "قولی که در لحظهٔ صحبت داده می‌شود با will می‌آید."),
    mcq("This hotel is ___ than the one we booked last year.", "این هتل از هتلی که پارسال رزرو کردیم ___ است.", ["expensiver", "more expensive", "most expensive", "expensive"], 1,
        "Long adjectives take more + adjective.", "صفت‌های بلند more + صفت می‌گیرند."),
    mcq("How ___ sugar do you take in your tea?", "چقدر شکر در چایت می‌ریزی؟", ["many", "much", "few", "a few"], 1,
        "Sugar is uncountable, so how much.", "شکر نشماردنی است، پس how much."),
    mcq("You ___ park here — it's a bus stop.", "اینجا ___ پارک کنی؛ ایستگاه اتوبوس است.", ["don't have to", "must not", "shouldn't", "couldn't"], 1,
        "A prohibition is must not; don't have to would mean it is allowed.", "ممنوعیت با must not است؛ don't have to یعنی مجاز است."),
    mcq("If the weather ___ good, we'll have lunch outside.", "اگر هوا ___، بیرون ناهار می‌خوریم.", ["will be", "is", "was", "were"], 1,
        "The if-clause takes the present simple.", "بند if حال ساده می‌گیرد."),
]

VOCABULARY = [
    mcq("The child of your aunt is your ___.", "فرزند خاله‌ات ___ تو است.", ["cousin", "colleague", "neighbor", "partner"], 0,
        "A cousin is the child of an aunt or uncle.", "cousin فرزند خاله یا عمه است."),
    mcq("We ___ in touch by message since we left school.", "از وقتی مدرسه را ترک کردیم با پیام ___ مانده‌ایم.", ["kept", "keep", "have kept", "are keeping"], 2,
        "The phrase is keep in touch; with 'since' it takes the present perfect.", "عبارت keep in touch است و با since حال کامل می‌گیرد."),
    mcq("We ___ at six to avoid the traffic.", "ساعت شش ___ تا در ترافیک نمانیم.", ["set off", "checked in", "got off", "ran out"], 0,
        "Set off means to start a journey.", "set off یعنی راه افتادن."),
    mcq("There wasn't any bread, so we bought a ___ .", "نان نبود، پس یک ___ خریدیم.", ["receipt", "loaf", "bill", "tip"], 1,
        "A loaf is a whole bread.", "loaf یعنی یک نان کامل."),
    mcq("The last day to hand in the project is the ___.", "آخرین روز تحویل پروژه ___ است.", ["shift", "deadline", "warranty", "receipt"], 1,
        "The deadline is the final date.", "deadline تاریخ نهایی است."),
    mcq("They gave me a ___ because the shoes were faulty.", "چون کفش‌ها معیوب بودند، ___ دادند.", ["discount", "refund", "line", "receipt"], 1,
        "A refund returns your money.", "refund پولت را برمی‌گرداند."),
    mcq("Take one tablet twice a day — that is the ___.", "روزی دو بار یک قرص؛ این ___ است.", ["prescription", "dose", "medicine", "syrup"], 1,
        "The dose is the amount you take at one time.", "dose مقدار مصرف در یک نوبت است."),
    mcq("My phone has no battery left, so I need to ___ it.", "گوشی‌ام باتری ندارد، باید ___ .", ["charge", "upload", "attach", "update"], 0,
        "You charge a battery.", "باتری را charge می‌کنی."),
]

READING = [
    reading_item(
        ("A weekend in Yazd", "آخر هفته در یزد"),
        ("Last month my wife and I took the night train to Yazd. We arrived at six in the morning and walked to our hotel through the old streets while the city was still waking up. The hotel was an old house with a small courtyard, and the owner made us tea with dates.\n\nOn Saturday we visited the wind towers and the water museum, then ate lunch near the Friday mosque. The food was simple and very good, and it was much cheaper than in Tehran. In the evening we sat on the roof and watched the sun go down over the domes.\n\nWe only had two days, so we didn't see the desert, but we're going to go back next spring and stay longer.",
         "ماه گذشته من و همسرم با قطار شبانه به یزد رفتیم. ساعت شش صبح رسیدیم و وقتی شهر هنوز بیدار نشده بود، از کوچه‌های قدیمی تا هتل پیاده رفتیم. هتل خانه‌ای قدیمی با حیاط کوچک بود و صاحبش برایمان چای با خرما آورد.\n\nشنبه از بادگیرها و موزهٔ آب دیدن کردیم و بعد نزدیک مسجد جامع ناهار خوردیم. غذا ساده و خیلی خوب بود و از تهران بسیار ارزان‌تر. عصر روی پشت‌بام نشستیم و غروب آفتاب را روی گنبدها تماشا کردیم.\n\nفقط دو روز داشتیم، پس کویر را ندیدیم، اما بهار آینده برمی‌گردیم و بیشتر می‌مانیم."),
        [
            mcq("How did they travel to Yazd?", "چطور به یزد رفتند؟", ["by plane", "by night train", "by car", "by bus"], 1,
                "'We took the night train to Yazd.'", "«با قطار شبانه به یزد رفتیم»."),
            mcq("Why was the food a good experience?", "چرا غذا تجربهٔ خوبی بود؟", ["it was expensive but famous", "it was simple, good and cheaper than in Tehran", "it was spicy", "the hotel cooked it"], 1,
                "The writer calls it simple and very good, and much cheaper.", "نویسنده آن را ساده و خیلی خوب و بسیار ارزان‌تر می‌خواند."),
            mcq("What do they plan to do next spring?", "بهار آینده چه برنامه‌ای دارند؟", ["visit the desert in one day", "return and stay longer", "move to Yazd", "take the day train"], 1,
                "They are going back next spring and staying longer.", "بهار آینده برمی‌گردند و بیشتر می‌مانند."),
        ],
    ),
    reading_item(
        ("A note from the building", "اطلاعیهٔ ساختمان"),
        ("Dear residents,\n\nThe water will be off on Tuesday from nine in the morning until about four in the afternoon. Workers will repair the pipes on the ground floor. Please keep some water in your apartment for the day, and do not use the washing machines during this time.\n\nThe elevator will also be off between ten and eleven while the workers move their equipment. If you need help with shopping or with the stairs, please call the building office before Monday evening and we will arrange it.\n\nThank you for your patience,\nThe building office",
         "ساکنان محترم،\n\nروز سه‌شنبه از ساعت نه صبح تا حدود چهار بعدازظهر آب قطع خواهد بود. کارگران لوله‌های طبقهٔ همکف را تعمیر می‌کنند. لطفاً برای آن روز در آپارتمان خود آب نگه دارید و در این مدت از ماشین لباسشویی استفاده نکنید.\n\nآسانسور هم بین ده تا یازده قطع می‌شود، چون کارگران وسایلشان را جابه‌جا می‌کنند. اگر برای خرید یا پله‌ها کمک لازم دارید، تا دوشنبه عصر با دفتر ساختمان تماس بگیرید تا هماهنگ کنیم.\n\nاز صبر شما سپاسگزاریم،\nدفتر ساختمان"),
        [
            mcq("Why will the water be off?", "چرا آب قطع می‌شود؟", ["the building is empty", "workers are repairing pipes", "there is no water in the city", "the office is closed"], 1,
                "The note says workers will repair the pipes.", "اطلاعیه می‌گوید کارگران لوله‌ها را تعمیر می‌کنند."),
            mcq("What should residents do before Tuesday?", "ساکنان قبل از سه‌شنبه چه کار باید بکنند؟", ["buy washing machines", "keep some water", "move their cars", "pay the bill"], 1,
                "'Please keep some water in your apartment for the day.'", "«برای آن روز در آپارتمان خود آب نگه دارید»."),
            mcq("When should someone ask for help with the stairs?", "کِی باید برای پله‌ها کمک بخواهد؟", ["after Tuesday", "before Monday evening", "at ten on Tuesday", "any time"], 1,
                "Call the office before Monday evening so they can arrange it.", "تا دوشنبه عصر با دفتر تماس بگیر تا هماهنگ کنند."),
        ],
    ),
]

LISTENING = [
    listen("I've just come back from the dentist. It wasn't as bad as I expected, but I can't eat anything hot today.",
           "What is the speaker's problem now?", "مشکل گوینده الان چیست؟", ["her tooth hurts a lot", "she can't eat hot food today", "she has to go back tomorrow", "she lost her appointment"], 1,
           "'I can't eat anything hot today.'", "«امروز چیزی گرم نمی‌توانم بخورم»."),
    listen("The train to Qom leaves from platform three at ten past seven, and there is a small café on platform one if you need coffee.",
           "Where can passengers get coffee?", "مسافران از کجا قهوه بگیرند؟", ["platform one", "platform three", "the ticket office", "the train"], 0,
           "The café is on platform one.", "کافه در سکوی یک است."),
    listen("I booked a table for seven, but the kitchen closes at nine, so we'll have to order by half past eight.",
           "When is the last order?", "آخرین سفارش کِی است؟", ["seven", "eight thirty", "nine", "nine thirty"], 1,
           "'We'll have to order by half past eight.'", "«باید تا هشت‌ونیم سفارش بدهیم»."),
    listen("Take one tablet every eight hours, after food. Don't take it with milk, and if you still have a temperature after three days, see a doctor.",
           "What should you avoid?", "از چه چیزی پرهیز کن؟", ["food", "milk with the tablet", "water", "sleep"], 1,
           "'Don't take it with milk.'", "«با شیر نخور»."),
    listen("We're meeting at the library at five, not at the café. If you arrive early, wait outside — the library closes at half past four and opens again at five.",
           "Where are they meeting?", "کجا همدیگر را می‌بینند؟", ["the café", "the library", "the park", "the station"], 1,
           "'We're meeting at the library at five.'", "«ساعت پنج در کتابخانه همدیگر را می‌بینیم»."),
    listen("I wanted to buy the jacket, but they only had it in small and extra large, so I asked them to order my size and I'll collect it on Thursday.",
           "Why didn't she buy the jacket?", "چرا ژاکت را نخرید؟", ["it was too expensive", "they didn't have her size", "it was faulty", "she changed her mind"], 1,
           "Only small and extra large were in stock.", "فقط سایز کوچک و خیلی بزرگ موجود بود."),
]

WRITING = [
    write("Write an email to a friend about a trip you took last month. Say where you went, how you traveled, what you did there and one thing you would do differently.",
          "ایمیلی برای دوستت دربارهٔ سفر ماه گذشته بنویس. بگو کجا رفتی، چطور سفر کردی، آنجا چه کردی و یک چیز که دفعهٔ بعد جور دیگری انجام می‌دهی.",
          50, ["went", "because"],
          "Past simple for the trip; three or four short paragraphs; finish with a question for your friend.",
          "برای سفر از گذشتهٔ ساده استفاده کن؛ سه یا چهار پاراگراف کوتاه؛ با یک پرسش از دوستت تمام کن."),
    write("Write a short message to your neighbor. You are going to be away for three days. Ask them to water your plants and explain what to do.",
          "پیام کوتاهی برای همسایه‌ات بنویس. سه روز خانه نیستی. از او بخواه گلدان‌ها را آب بدهد و توضیح بده چه کار کند.",
          40, ["could", "if"],
          "Make the request polite with could, and give one condition with if.",
          "درخواست را با could مؤدبانه کن و یک شرط با if بیاور."),
]

SPEAKING = [
    say("Last weekend I visited my cousin and we cooked dinner together.", "آخر هفتهٔ گذشته به دیدن پسرم رفتن و با هم شام پختیم."),
    say("I have never been to a foreign country, but I would like to travel next year.", "تا حالا به کشور خارجی نرفته‌ام، اما دوست دارم سال آینده سفر کنم."),
    say("If the weather is good tomorrow, I will go to the park with my friends.", "اگر فردا هوا خوب باشد، با دوستانم به پارک می‌روم."),
]

PAPER = exam(
    45, 0.6, 0.5, BLURB,
    [
        section("grammar", GRAMMAR),
        section("vocabulary", VOCABULARY),
        section("reading", READING),
        section("listening", LISTENING),
        section("writing", WRITING),
        section("speaking", SPEAKING),
    ],
)
