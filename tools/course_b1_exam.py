#!/usr/bin/env python3
"""The B1 final examination: 33 marks over six sections.

Same architecture as the A1 and A2 papers — six sections in skill order, one
mark per item, passages counted through their questions — with items that
require B1 control: the perfect against the past, the second conditional, the
passive, relative clauses, reported speech, used to, deduction and gerunds.
"""

from course_kit import exam, listen, mcq, reading_item, say, section, write

BLURB = (
    "Six skills, each marked on its own. Grammar, vocabulary, reading and listening are marked from your answers; writing is marked against a rubric; speaking is marked from what this device hears you say. You need 60% overall, at least 50% in every skill, and all six skills must be assessed.",
    "شش مهارت، هر یک جداگانه. گرامر، واژگان، خواندن و شنیدن از پاسخ‌ها نمره می‌گیرند؛ نوشتن با معیارهای مشخص و گفتن از آنچه دستگاه می‌شنود. برای قبولی ۶۰٪ کل و ۵۰٪ در هر مهارت لازم است و هر شش مهارت باید سنجیده شود.",
)

GRAMMAR = [
    mcq("I ___ in this city since 2019, and I still love it.", "از ۲۰۱۹ در این شهر ___ و هنوز دوستش دارم.", ["live", "lived", "have lived", "was living"], 2,
        "The situation is still open, so the present perfect.", "وضعیت هنوز باز است، پس حال کامل."),
    mcq("If I ___ more time, I would take the longer course.", "اگر ___ وقت بیشتری داشتم، دورهٔ طولانی‌تر را می‌گذراندم.", ["have", "had", "will have", "would have"], 1,
        "The second conditional takes the past simple in the if-clause.", "شرطی دوم در بند if گذشتهٔ ساده می‌گیرد."),
    mcq("The new library ___ two years ago.", "کتابخانهٔ جدید دو سال پیش ___ .", ["built", "was built", "has built", "is building"], 1,
        "A finished event with an unknown doer: past passive.", "رویداد تمام‌شده با کنندهٔ ناشناس: مجهول گذشته."),
    mcq("That's the teacher ___ helped me pass the exam.", "این همان معلمی است که کمکم کرد قبول شوم.", ["which", "whose", "who", "where"], 2,
        "People take who (or that) as the subject pronoun.", "آدم‌ها who (یا that) به‌عنوان ضمیر فاعلی می‌گیرند."),
    mcq("She said she ___ the report the next morning.", "گفت گزارش را صبح روز بعد ___ .", ["sends", "will send", "would send", "has sent"], 2,
        "Will becomes would in reported speech.", "will در نقل قول به would تبدیل می‌شود."),
    mcq("There ___ a cinema here, but it closed in the nineties.", "قبلاً اینجا سینمایی ___، اما در دههٔ نود بسته شد.", ["used to be", "would be", "was used to be", "used to have"], 0,
        "A past state takes used to be; would cannot describe states.", "وضعیت گذشته used to be می‌گیرد و would آن را نمی‌گوید."),
    mcq("The lights are off and the car is gone — they ___ left already.", "چراغ‌ها خاموش و ماشین رفته؛ آن‌ها ___ رفته‌اند.", ["must have", "must", "should have", "can't have"], 0,
        "Certainty about the past: must have + participle.", "اطمینان دربارهٔ گذشته: must have + اسم مفعول."),
    mcq("I'm looking forward to ___ from you.", "منتظر ___ از تو هستم.", ["hear", "hearing", "be heard", "to hear"], 1,
        "After a preposition the -ing form is required.", "بعد از حرف اضافه شکل ing لازم است."),
]

VOCABULARY = [
    mcq("Moving abroad was the ___ of my career.", "رفتن به خارج ___ حرفهٔ من بود.", ["turning point", "deadline", "vacancy", "warranty"], 0,
        "A turning point is where things change direction.", "turning point جایی است که مسیر عوض می‌شود."),
    mcq("She was ___ after two years and now runs the branch.", "بعد از دو سال ___ و حالا شعبه را می‌گرداند.", ["applied", "promoted", "resigned", "shortlisted"], 1,
        "Promotion moves you to a higher position.", "promotion به سمت بالاتر می‌برد."),
    mcq("The app crashed, so I had to ___ my files from the cloud.", "اپ از کار افتاد، پس مجبور شدم فایل‌ها را از ابر ___ .", ["upload", "download", "attach", "charge"], 1,
        "Download brings files from the internet to your device.", "download فایل را از اینترنت به دستگاه می‌آورد."),
    mcq("The film's ___ is predictable, but the acting is superb.", "___ فیلم قابل پیش‌بینی است، اما بازی فوق‌العاده است.", ["cast", "plot", "setting", "soundtrack"], 1,
        "The plot is the story itself.", "plot خود داستان است."),
    mcq("They argued and ___ for a year before making up.", "دعوا کردند و یک سال ___ تا آشتی کردند.", ["fell out", "drifted apart", "got on", "made up"], 0,
        "Fall out means to quarrel and stop speaking.", "fall out یعنی دعوا و قطع رابطه."),
    mcq("He ___ up smoking after twenty years.", "بعد از بیست سال سیگار را ___ .", ["took", "gave", "cut", "kept"], 1,
        "Give up = stop completely.", "give up یعنی کاملاً ترک کردن."),
    mcq("Investing in public transport would ___ emissions in the city.", "سرمایه‌گذاری در حمل‌ونقل عمومی انتشار گازها در شهر را ___ .", ["reduce", "increase", "conserve", "ban"], 0,
        "Reduce cuts the amount; conserve applies to water and resources.", "reduce مقدار را کم می‌کند و conserve برای آب و منابع است."),
    mcq("I'd like the money back — could you ___ the payment to my account?", "پول را می‌خواهم؛ می‌شود پرداخت را به حسابم ___ ؟", ["charge", "withdraw", "transfer", "owe"], 2,
        "Transfer money between accounts.", "transfer پول را بین حساب‌ها جابه‌جا می‌کند."),
]

READING = [
    reading_item(
        ("The shop that taught a street to talk", "مغازه‌ای که کوچه را به حرف زدن آورد"),
        ("When Reza opened a small bookshop on Enqelab Street, three other bookshops closed within a year. Everyone said the street was dead for books.\n\nWhat he did differently was not the stock. He put six chairs by the window, made tea, and told people they could sit without buying anything. Within a month, students who had been studying in cafés started coming in the mornings, and they began to talk to each other about what they were reading.\n\nThe shop now runs two reading groups, and it makes most of its money from tea and second-hand books. Reza says the shop works because it is not really a shop: it is a room where people are allowed to stay.\n\nNot everyone is convinced. A bookseller two streets away calls it a café that happens to sell books, and says the model only works because the rent is low. Reza agrees about the rent, but says the rest of the street has changed too — two new shops have opened and they both have chairs.",
         "وقتی رضا کتاب‌فروشی کوچکی در خیابان انقلاب باز کرد، سه کتاب‌فروشی دیگر در همان سال بسته شدند. همه می‌گفتند این خیابان برای کتاب مرده است.\n\nچیزی که او متفاوت کرد موجودی نبود. شش صندلی کنار پنجره گذاشت، چای درست کرد و گفت می‌توانند بدون خریدن چیزی بنشینند. در یک ماه، دانشجویانی که در کافه‌ها درس می‌خواندند صبح‌ها به آنجا آمدند و دربارهٔ چیزی که می‌خواندند با هم حرف زدند.\n\nمغازه حالا دو گروه کتاب‌خوانی دارد و بیشتر درآمدش از چای و کتاب‌های دست‌دوم است. رضا می‌گوید مغازه کار می‌کند چون واقعاً مغازه نیست: اتاقی است که آدم‌ها اجازه دارند در آن بمانند.\n\nهمه قانع نیستند. کتاب‌فروشی در دو خیابان آن‌طرف‌تر آن را کافه‌ای می‌داند که تصادفاً کتاب می‌فروشد و می‌گوید این مدل فقط چون اجاره پایین است کار می‌کند. رضا دربارهٔ اجاره موافق است، اما می‌گوید بقیهٔ خیابان هم عوض شده؛ دو مغازهٔ تازه باز شده و هر دو صندلی دارند."),
        [
            mcq("What did Reza do that was different?", "رضا چه کار متفاوتی کرد؟", ["he sold cheaper books", "he gave people space to sit and talk", "he opened a café", "he closed the other shops"], 1,
                "The chairs, the tea and permission to stay are his innovation.", "صندلی‌ها، چای و اجازهٔ ماندن، نوآوری اوست."),
            mcq("Where does most of the shop's money come from?", "بیشتر درآمد مغازه از کجاست؟", ["new books", "tea and second-hand books", "reading groups", "the rent"], 1,
                "'Most of its money from tea and second-hand books.'", "«بیشتر درآمدش از چای و کتاب دست‌دوم»."),
            mcq("What is the bookseller's criticism?", "نقد کتاب‌فروش دیگر چیست؟", ["the shop is too expensive", "the model depends on low rent", "the tea is bad", "the shop has no books"], 1,
                "He says it only works because the rent is low.", "می‌گوید فقط چون اجاره پایین است کار می‌کند."),
        ],
    ),
    reading_item(
        ("Why we stopped repairing things", "چرا تعمیر کردن چیزها را کنار گذاشتیم"),
        ("Fifty years ago, a broken radio was taken to a shop and repaired. Today it is usually replaced, and the old one is thrown away. The change is not only about skill; it is about design, price and time.\n\nManufacturers argue that sealed devices are cheaper to build and more reliable. Critics reply that some products are deliberately difficult to open, so that repair costs more than replacement. Either way, the effect is the same: the useful life of an appliance is decided in a factory, not in a home.\n\nRepair cafés have appeared in many cities as an answer. Volunteers fix toasters and lamps for free, and teach the owners how the repair is done. Their organisers say the point is not the toaster but the confidence: once someone has opened a machine, they stop treating it as a closed box.\n\nThe limits are obvious. A repair café cannot fix a phone whose battery is glued in place, and it does not change the price of a new one. But it does show how much of what we call waste was a decision.",
         "پنجاه سال پیش رادیوی خراب را به مغازه‌ای می‌بردند و تعمیر می‌شد. امروز معمولاً عوض می‌شود و کهنه دور انداخته می‌شود. این تغییر فقط دربارهٔ مهارت نیست؛ دربارهٔ طراحی، قیمت و زمان است.\n\nسازندگان می‌گویند دستگاه‌های بسته ارزان‌تر ساخته می‌شوند و مطمئن‌ترند. منتقدان پاسخ می‌دهند که بعضی محصولات عمداً سخت باز می‌شوند تا تعمیر از تعویض گران‌تر شود. در هر حال نتیجه یکی است: عمر مفید یک وسیله در کارخانه تعیین می‌شود، نه در خانه.\n\nکافه‌های تعمیر در بسیاری از شهرها به‌عنوان پاسخ پدید آمده‌اند. داوطلبان رایگان تستر و چراغ تعمیر می‌کنند و به صاحبانشان یاد می‌دهند تعمیر چطور انجام می‌شود. برگزارکنندگان می‌گویند نکته خود تستر نیست، اعتماد است: وقتی کسی ماشینی را باز کرده باشد، دیگر آن را جعبه‌ای بسته نمی‌بیند.\n\nمحدودیت‌ها روشن است. کافهٔ تعمیر نمی‌تواند گوشی‌ای را که باتری‌اش چسبیده تعمیر کند و قیمت گوشی نو را عوض نمی‌کند. اما نشان می‌دهد چه مقدار از آنچه زباله می‌نامیم، یک تصمیم بوده است."),
        [
            mcq("What changed in fifty years, according to the text?", "به گفتهٔ متن در پنجاه سال چه عوض شد؟", ["people lost all their skills", "repair was replaced by replacement", "radios became cheaper", "shops closed"], 1,
                "The text opens with repair being replaced by replacement.", "متن با جایگزینی تعمیر با تعویض شروع می‌شود."),
            mcq("What do critics say about sealed devices?", "منتقدان دربارهٔ دستگاه‌های بسته چه می‌گویند؟", ["they are safer", "some are hard to open on purpose", "they are all handmade", "they last longer"], 1,
                "'Deliberately difficult to open' is the critics' claim.", "«عمداً سخت باز می‌شوند» ادعای منتقدان است."),
            mcq("What is the real point of a repair café, according to its organisers?", "به گفتهٔ برگزارکنندگان، نکتهٔ اصلی کافهٔ تعمیر چیست؟", ["free toasters", "the confidence that things can be opened", "making money", "teaching factory skills"], 1,
                "'The point is not the toaster but the confidence.'", "«نکته خود تستر نیست، اعتماد است»."),
        ],
    ),
]

LISTENING = [
    listen("I've been in this job for eight years, and although the salary is fine, I've stopped learning anything new. That's why I applied.",
           "Why did the speaker apply for a new job?", "چرا گوینده برای کار تازه درخواست داد؟", ["the salary is low", "there is nothing new to learn", "the hours are long", "the office moved"], 1,
           "'I've stopped learning anything new.'", "«چیز تازه‌ای یاد نمی‌گیرم»."),
    listen("The flat is lovely and the price is fair, but the road outside is noisy until about eleven at night. If you're a light sleeper, I'd think twice.",
           "What is the warning?", "هشدار چیست؟", ["the price is too high", "the road is noisy at night", "the flat is small", "the neighbours are unfriendly"], 1,
           "The noise lasts until about eleven.", "سر و صدا تا حدود یازده شب ادامه دارد."),
    listen("We were going to drive, but the mechanic said the car wouldn't be ready until Friday, so we've booked train tickets instead.",
           "Why did they change their plan?", "چرا برنامه‌شان را عوض کردند؟", ["the train was cheaper", "the car was not ready", "they prefer trains", "the roads were closed"], 1,
           "The car would not be ready until Friday.", "ماشین تا جمعه آماده نمی‌شد."),
    listen("I don't think the new system is the problem. The training was two hours long and nobody has used it since. It's a support problem, not a software problem.",
           "What does the speaker think the problem is?", "گوینده مشکل را چه می‌داند؟", ["the software", "the training and follow-up", "the price", "the manager"], 1,
           "Two hours of training and no follow-up use is the issue.", "دو ساعت آموزش و بی‌استفاده ماندن، مشکل است."),
    listen("The museum is free on Thursdays after five, but you still need to book a slot online — last week people waited an hour without one.",
           "What should visitors do?", "بازدیدکنندگان چه کار باید بکنند؟", ["pay at the door", "book a slot online", "arrive before five", "wait an hour"], 1,
           "Booking a slot is still required, even when entry is free.", "حتی با ورود رایگان، رزرو نوبت لازم است."),
    listen("We're looking for someone who has worked with data, not necessarily in our industry. The person we hired last year came from a bakery, and she is now our best analyst.",
           "What do they value most?", "بیشتر به چه چیزی اهمیت می‌دهند؟", ["industry experience", "experience with data", "a university degree", "knowledge of bakeries"], 1,
           "They want data experience; the industry does not matter.", "تجربهٔ داده می‌خواهند و صنعت مهم نیست."),
]

WRITING = [
    write("Write an email to a colleague explaining that a project will be two weeks late. Give the reason briefly, say what you have already done, propose a new date and offer one solution.",
          "به همکاری ایمیل بنویس و توضیح بده که پروژه دو هفته دیر می‌شود. دلیل را کوتاه بگو، بگو تا حالا چه کرده‌ای، تاریخ تازه پیشنهاد بده و یک راه‌حل ارائه کن.",
          60, ["because", "would"],
          "Four paragraphs: the news, the reason, what you have done, the proposal. Use one linking device per paragraph and apologise once.",
          "چهار پاراگراف: خبر، دلیل، کارهایی که کرده‌ای، پیشنهاد. در هر پاراگراف یک واژهٔ ربط و یک بار عذرخواهی."),
    write("Write a short review of a film, series or book you have finished recently. Say what it is about without spoiling it, praise one thing with a detail, criticise one thing, and recommend it to a particular reader or viewer.",
          "نقد کوتاهی از فیلم، سریال یا کتابی بنویس که تازه تمام کرده‌ای. بدون لو دادن داستان بگو دربارهٔ چیست، یک چیز را با جزئیات تحسین کن، یک چیز را نقد کن و آن را به بیننده یا خوانندهٔ خاصی توصیه کن.",
          60, ["worth", "although"],
          "Present for what it is like, past for your experience of it, and a recommendation at the end.",
          "حال برای ویژگی اثر، گذشته برای تجربهٔ خودت و توصیه در پایان."),
]

SPEAKING = [
    say("In my opinion, learning a language is worth the effort because it changes how you see people.", "به نظر من یادگیری زبان ارزش تلاش را دارد، چون نگاهت به آدم‌ها را عوض می‌کند."),
    say("When I was younger, I used to walk to school every morning, but now I take the bus.", "وقتی جوان‌تر بودم هر صبح پیاده به مدرسه می‌رفتم، اما الان با اتوبوس می‌روم."),
    say("If I had more free time, I would spend it learning to play an instrument.", "اگر وقت آزاد بیشتری داشتم آن را صرف یادگیری یک ساز می‌کردم."),
]

PAPER = exam(
    50, 0.6, 0.5, BLURB,
    [
        section("grammar", GRAMMAR),
        section("vocabulary", VOCABULARY),
        section("reading", READING),
        section("listening", LISTENING),
        section("writing", WRITING),
        section("speaking", SPEAKING),
    ],
)
