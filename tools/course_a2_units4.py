#!/usr/bin/env python3
"""A2 · units 7-8: what you should and must do, and what happens if you do.

The last two A2 units move from permission and obligation to condition, and the
reading text in unit 7 is a small experiment the learner could repeat: two days
without a phone.
"""

from course_kit import gap, lesson, listen, mcq, passage, unit

U7 = unit(
    "a2-u7",
    ("You should rest", "باید استراحت کنی"),
    ("Give advice, say what is allowed, required and possible, and survive offline for a day.", "توصیه بده، بگو چه چیزی مجاز، لازم یا ممکن است و یک روز بدون اینترنت سر کن."),
    [
        lesson(
            "a2-u7-l1",
            "grammar",
            ("Modals: can, could, should, must, have to, might", "افعال کمکی وجهی: can، could، should، must، have to، might"),
            ("Choose a modal by what you mean: ability, advice, obligation or possibility.", "افعال وجهی را بر اساس معنا انتخاب کن: توانایی، توصیه، اجبار یا احتمال."),
            [
                ("Can is ability and permission: I can swim. Can I open the window? Could is the polite version, and also the past of can: Could you help me? I could read at four.", "can توانایی و اجازه است: I can swim. Can I open the window? could شکل مؤدبانه و همچنین گذشتهٔ can است: Could you help me? I could read at four."),
                ("Should gives advice and is not strong: You should see a doctor. Shouldn't means it is a bad idea: You shouldn't drive tonight.", "should توصیه می‌دهد و شدید نیست: You should see a doctor. shouldn't یعنی کار بدی است: You shouldn't drive tonight."),
                ("Must and have to both mean obligation. Must is the speaker's own strong rule, have to is an outside rule: You must wear a seatbelt (the law). I have to work on Saturday (my boss). Mustn't is prohibition; don't have to means it is not necessary — a completely different meaning.", "must و have to هر دو اجبار را می‌گویند. must قانون شدید خود گوینده است و have to قانون بیرونی: You must wear a seatbelt. I have to work on Saturday. mustn't ممنوعیت است و don't have to یعنی لازم نیست — معنایی کاملاً متفاوت."),
                ("Might and may say something is possible: It might rain later. May I come in? is the formal permission question. All modals are followed by the plain verb, with no to and no -s: she must go, not 'she musts to go'.", "might و may احتمال را می‌گویند: It might rain later. May I come in? پرسش رسمی اجازه است. بعد از همهٔ افعال وجهی فعل ساده می‌آید، بدون to و بدون s: she must go، نه «she musts to go»."),
            ],
            [
                ("You should take a break; you've been working for six hours.", "باید استراحت کنی؛ شش ساعت است کار می‌کنی."),
                ("Could you send me the file by email?", "می‌شود فایل را با ایمیل بفرستی؟"),
                ("Passengers must not smoke on board.", "مسافران نباید داخل هواپیما سیگار بکشند."),
                ("I have to wear a uniform at work, but I don't have to wear a tie.", "در کار باید لباس فرم بپوشم، اما لازم نیست کراوات بزنم."),
                ("She might be late — the traffic is terrible.", "ممکن است دیر برسد؛ ترافیک وحشتناک است."),
            ],
            [
                mcq("You look tired. You ___ go to bed early.", "خسته به نظر می‌رسی. ___ زود بخوابی.", ["must", "should", "can", "might"], 1,
                    "Advice takes should; must would be too strong.", "توصیه با should است؛ must بیش از حد شدید است."),
                mcq("It's a rule of the library: you ___ talk loudly.", "قانون کتابخانه است: ___ بلند حرف بزنی.", ["don't have to", "mustn't", "shouldn't have", "couldn't"], 1,
                    "A prohibition is mustn't.", "ممنوعیت با mustn't است."),
            ],
            [
                gap("You ___ (not / have to) pay — it's free for students.", ["don't have to", "do not have to"], "No obligation: don't have to.", "بدون اجبار: don't have to."),
                gap("___ you open the window, please? It's hot in here.", ["Could", "Can"], "A polite request: Could/Can you …", "درخواست مؤدبانه: Could/Can you …"),
                mcq("Which sentence means 'it is not necessary'?", "کدام جمله یعنی «لازم نیست»؟", ["You mustn't go.", "You don't have to go.", "You shouldn't go.", "You can't go."], 1,
                    "Don't have to = no obligation; mustn't = prohibited.", "don't have to یعنی اجباری نیست؛ mustn't یعنی ممنوع است."),
                listen("You mustn't use your phone during the exam, but you can leave your bag at the front of the room.", "What are the rules?", "قانون‌ها چیست؟", ["no phones, bags at the front", "no bags, phones allowed", "phones and bags are both fine", "phones only at the front"], 0,
                       "Phones are prohibited; bags go at the front.", "تلفن ممنوع است و کیف‌ها جلو گذاشته می‌شوند."),
            ],
        ),
        lesson(
            "a2-u7-l2",
            "vocabulary",
            ("Technology and staying in touch", "فناوری و در تماس ماندن"),
            ("Use the verbs and nouns of phones, files and messages without the wrong preposition.", "فعل و اسم تلفن، فایل و پیام را بدون حرف اضافهٔ اشتباه به کار ببر."),
            [
                ("Devices have verbs of care: charge the battery, plug it in, turn it on and off, restart it, update it. A battery runs out; a screen is cracked; the connection is slow.", "دستگاه‌ها فعل‌های نگهداری دارند: charge the battery، plug it in، turn it on/off، restart it، update it. باتری تمام می‌شود، صفحه ترک می‌خورد و اتصال کند است."),
                ("Accounts and files: sign up for an account, log in and log out, download and upload a file, attach a document to an email, save it in the cloud, share a link. Reply to a message; don't 'answer to' it.", "حساب و فایل: sign up for an account، log in و log out، download و upload، attach a document to an email، save it in the cloud، share a link. به پیام reply می‌کنی، نه «answer to»."),
                ("Word families help: connect → connection, inform → information, attach → attachment, secure → security. The noun often ends in -tion or -ment, and the meaning stays close.", "خانواده‌های واژه کمک می‌کنند: connect ← connection، inform ← information، attach ← attachment، secure ← security. اسم اغلب به tion یا ment ختم می‌شود و معنا نزدیک می‌ماند."),
            ],
            [
                ("My phone died in the middle of the call because I forgot to charge it.", "وسط تماس گوشی‌ام خاموش شد، چون یادم رفت شارژش کنم."),
                ("I've attached the report — let me know if you can open it.", "گزارش را پیوست کرده‌ام؛ خبر بده می‌توانی بازش کنی."),
                ("You need to sign up before you can download the app.", "برای دانلود اپ باید اول ثبت‌نام کنی."),
                ("The connection is terrible here, so let's talk later.", "اتصال اینجا افتضاح است، بعداً حرف بزنیم."),
            ],
            [
                mcq("To put a file on the internet is to ___.", "گذاشتن فایل روی اینترنت ___ است.", ["download", "upload", "attach", "charge"], 1,
                    "Upload goes up to the internet; download comes down.", "upload به اینترنت می‌رود و download پایین می‌آید."),
                mcq("The paper in an email that carries a document is an ___.", "کاغذی که فایل را در ایمیل حمل می‌کند ___ است.", ["account", "attachment", "update", "upload"], 1,
                    "An attachment is the file sent with a message.", "attachment فایلی است که با پیام فرستاده می‌شود."),
            ],
            [
                gap("My battery is almost empty, so I need to ___ my phone.", ["charge"], "You charge a battery.", "باتری را charge می‌کنی."),
                gap("Please ___ in with your email and password.", ["log", "sign"], "Log in with your details.", "با اطلاعاتت log in کن."),
                mcq("'The app crashed' means ___.", "«The app crashed» یعنی ___.", ["it closed suddenly and stopped working", "it updated", "it downloaded", "it echoed"], 0,
                    "A crash is a sudden stop, not an update.", "crash توقف ناگهانی است، نه به‌روزرسانی."),
                mcq("Which is the noun of 'attach'?", "اسم «attach» کدام است؟", ["attaching", "attachment", "attached", "attaches"], 1,
                    "The noun is attachment.", "اسم آن attachment است."),
            ],
        ),
        lesson(
            "a2-u7-l3",
            "reading",
            ("Two days without a phone", "دو روز بدون گوشی"),
            ("Read a personal experiment and find the writer's reasons, results and opinion.", "تجربهٔ شخصی کوتاهی را بخوان و دلیل، نتیجه و نظر نویسنده را پیدا کن."),
            [
                ("A personal experiment text answers three questions: why did I do it, what happened, what do I think now. The order is usually chronological, and the opinion is at the end.", "متن تجربهٔ شخصی به سه پرسش پاسخ می‌دهد: چرا این کار را کردم، چه شد، الان چه فکر می‌کنم. ترتیب معمولاً زمانی است و نظر در پایان می‌آید."),
                ("Look for the turning point: 'but on the second day…'. Contrast words (but, however, although) mark where the writer changes direction, and that is where the main idea usually sits.", "نقطهٔ چرخش را پیدا کن: «but on the second day…». واژه‌های تضاد (but، however، although) جایی را نشان می‌دهند که نویسنده مسیر را عوض می‌کند و ایدهٔ اصلی معمولاً همان‌جاست."),
            ],
            [
                ("Reason: 'I realised I checked my phone forty times a day.'", "دلیل: «فهمیدم چهل بار در روز گوشی‌ام را چک می‌کنم»."),
                ("Result: 'The first evening was boring. I kept reaching for a screen that wasn't there.'", "نتیجه: «اولین شب خسته‌کننده بود. مدام دستم به صفحه‌ای می‌رفت که نبود»."),
                ("Opinion: 'I'm not going back to forty times a day, but I don't want to give it up either.'", "نظر: «به چهل بار در روز برنمی‌گردم، اما نمی‌خواهم کاملاً کنارش بگذارم»."),
            ],
            [
                mcq("Why did the writer stop using her phone?", "چرا نویسنده استفاده از گوشی را قطع کرد؟", ["it was broken", "she felt she used it too often", "her teacher asked her to", "she lost it"], 1,
                    "She realised she checked it forty times a day.", "فهمید چهل بار در روز چکش می‌کند."),
                mcq("How did the first evening feel?", "اولین شب چه حسی داشت؟", ["relaxing", "boring", "exciting", "busy"], 1,
                    "'The first evening was boring.'", "«اولین شب خسته‌کننده بود»."),
            ],
            [
                mcq("What changed on the second day?", "روز دوم چه عوض شد؟", ["she bought a new phone", "she began to enjoy the quiet", "she went back to work", "she forgot her phone at home"], 1,
                    "The text says that by the second day she started to like the quiet.", "متن می‌گوید تا روز دوم کمکم سکوت را دوست داشت."),
                mcq("What is her conclusion?", "نتیجه‌گیری او چیست؟", ["She will never use a phone again.", "She will use it less, not give it up.", "She thinks phones are useless.", "She wants a new phone."], 1,
                    "She won't return to forty checks a day, but won't give it up either.", "به چهل بار در روز برنمی‌گردد، اما کاملاً هم کنار نمی‌گذارد."),
                mcq("'I kept reaching for a screen' means she ___.", "«I kept reaching for a screen» یعنی او ___.", ["bought a screen", "repeatedly wanted to pick up her phone", "broke the screen", "cleaned the screen"], 1,
                    "Keep + -ing means to do something repeatedly.", "keep + ing یعنی کاری را مکرر انجام دادن."),
                mcq("What is the main idea?", "ایدهٔ اصلی چیست؟", ["Phones are dangerous.", "A short break from a habit shows you the habit.", "Everyone should delete their apps.", "The writer has no friends."], 1,
                    "The experiment reveals her own habit, not a rule for everyone.", "تجربه عادت خودش را نشان می‌دهد، نه قانونی برای همه."),
            ],
            passage=passage(("Two days without a phone", "دو روز بدون گوشی"),
                            ("Last month I realised I checked my phone about forty times a day. So I decided to switch it off for two days.\n\nThe first evening was boring. I kept reaching for a screen that wasn't there. I read the same page of a book three times.\n\nBut on the second day something changed. I walked to work without music and noticed the shops I pass every morning. I had a long conversation with my sister because neither of us was looking at anything else.\n\nI'm not going back to forty times a day, but I don't want to give up my phone either. I just want to decide when I use it.",
                             "ماه گذشته فهمیدم حدود چهل بار در روز گوشی‌ام را چک می‌کنم. پس تصمیم گرفتم دو روز خاموشش کنم.\n\nاولین شب خسته‌کننده بود. مدام دستم به صفحه‌ای می‌رفت که نبود. یک صفحه از کتاب را سه بار خواندم.\n\nاما روز دوم چیزی عوض شد. بدون موسیقی تا محل کار پیاده رفتم و مغازه‌هایی را دیدم که هر صبح از کنارشان می‌گذرم. با خواهرم گفت‌وگوی طولانی کردم، چون هیچ‌کدام به چیز دیگری نگاه نمی‌کردیم.\n\nبه چهل بار در روز برنمی‌گردم، اما نمی‌خواهم گوشی‌ام را هم کنار بگذارم. فقط می‌خواهم خودم تصمیم بگیرم کِی از آن استفاده کنم.")),
        ),
    ],
)

U8 = unit(
    "a2-u8",
    ("If you come early", "اگر زود بیایی"),
    ("Make a condition and its result, and use it for weather, plans and the town you live in.", "شرط و نتیجه‌اش را بساز و آن را برای هوا، برنامه‌ها و شهرت به کار ببر."),
    [
        lesson(
            "a2-u8-l1",
            "grammar",
            ("The first conditional: if, when, unless", "شرطی نوع اول: if، when، unless"),
            ("Say what will happen if something else happens.", "بگو اگر چیز دیگری اتفاق بیفتد چه می‌شود."),
            [
                ("The first conditional is real and possible: if + present simple, then will + verb. If it rains, we'll stay at home. The condition is in the present, the result in the future.", "شرطی نوع اول واقعی و ممکن است: if + حال ساده، سپس will + فعل. If it rains, we'll stay at home. شرط در حال است و نتیجه در آینده."),
                ("The if-clause can come first or second. When it comes first, a comma separates it: If you leave now, you'll catch the bus. You'll catch the bus if you leave now.", "بند if می‌تواند اول یا دوم بیاید. وقتی اول می‌آید، ویرگول آن را جدا می‌کند: If you leave now, you'll catch the bus. You'll catch the bus if you leave now."),
                ("Will stays in the result, never in the condition: if it rains, not 'if it will rain'. When works like if for something certain: when I get home, I'll call you.", "will فقط در نتیجه می‌آید، هرگز در شرط: if it rains، نه «if it will rain». when مثل if برای امر قطعی به کار می‌رود: when I get home, I'll call you."),
                ("Unless means if not, and it already carries the negative: unless you hurry, we'll be late = if you don't hurry. Use one negative, not two.", "unless یعنی if not و خودش منفی را در خود دارد: unless you hurry, we'll be late = if you don't hurry. یک منفی به کار ببر، نه دو."),
            ],
            [
                ("If you come before nine, the market will still be open.", "اگر قبل از نه بیایی، بازار هنوز باز است."),
                ("We'll go to the park if the weather is good.", "اگر هوا خوب باشد به پارک می‌رویم."),
                ("Unless we leave now, we'll miss the train.", "اگر الان راه نیفتیم، قطار را از دست می‌دهیم."),
                ("If you press this button, the machine stops. (a general truth)", "اگر این دکمه را بزنی، دستگاه می‌ایستد. (حقیقت کلی)"),
            ],
            [
                mcq("If it ___ tomorrow, we'll cancel the picnic.", "اگر فردا ___، پیک‌نیک را لغو می‌کنیم.", ["will rain", "rains", "rained", "is raining"], 1,
                    "The condition takes the present simple, not will.", "شرط حال ساده می‌گیرد، نه will."),
                mcq("___ you finish early, call me.", "اگر زود تمام کردی، به من زنگ بزن.", ["Unless", "If", "Will", "When will"], 1,
                    "If introduces the condition; the result follows in the imperative.", "if شرط را می‌آورد و نتیجه به شکل امری می‌آید."),
            ],
            [
                gap("We ___ (miss) the bus if we don't hurry.", ["will miss", "'ll miss"], "Result clause: will + verb.", "بند نتیجه: will + فعل."),
                gap("___ you water the plants, they will die.", ["Unless"], "Unless = if not, with no extra not.", "unless یعنی if not، بدون not اضافه."),
                mcq("Which sentence is correct?", "کدام جمله درست است؟", ["If he will come, I will tell him.", "If he comes, I'll tell him.", "If he come, I'll tell him.", "If he comes, I tell him."], 1,
                    "Present simple after if, will in the result.", "بعد از if حال ساده و در نتیجه will."),
                listen("If you book online, the tickets are cheaper. But you must print them before you travel.", "How can you pay less?", "چطور می‌توانی کمتر بپردازی؟", ["by booking at the station", "by booking online", "by travelling at night", "by paying in cash"], 1,
                       "Online booking makes the tickets cheaper.", "رزرو اینترنتی بلیت را ارزان‌تر می‌کند."),
            ],
        ),
        lesson(
            "a2-u8-l2",
            "vocabulary",
            ("Your town, its services and its weather", "شهرت، خدماتش و هوایش"),
            ("Find your way around local services and understand a forecast.", "در خدمات محلی راه پیدا کن و پیش‌بینی هوا را بفهم."),
            [
                ("Public places have precise names: the town hall (where you register things), the post office, the library, the recycling centre, the police station, the health centre. A service is what they do for you; a form is what you fill in.", "مکان‌های عمومی نام دقیق دارند: town hall (ثبت امور)، post office، library، recycling centre، police station، health centre. service کاری است که برایت می‌کنند و form فرمی است که پر می‌کنی."),
                ("Directions in town use landmarks, not numbers: opposite the bank, next to the pharmacy, at the end of the street, on the corner, across from the park, just past the lights.", "مسیر در شهر با نشانه‌ها گفته می‌شود، نه شماره: opposite the bank، next to the pharmacy، at the end of the street، on the corner، across from the park، just past the lights."),
                ("Weather words are graded: it's sunny, cloudy, windy, foggy, freezing, mild. A shower is short rain; sunny spells are short sunny periods; a heatwave is a long hot period. The forecast gives the probability: a 40% chance of rain.", "واژه‌های هوا درجه‌بندی دارند: sunny، cloudy، windy، foggy، freezing، mild. shower باران کوتاه، sunny spells دوره‌های کوتاه آفتاب و heatwave دورهٔ طولانی گرماست. پیش‌بینی احتمال را می‌دهد: a 40% chance of rain."),
            ],
            [
                ("You can renew your passport at the town hall, but you need an appointment.", "می‌توانی گذرنامه را در شهرداری تمدید کنی، اما باید وقت بگیری."),
                ("The library is on the corner, opposite the post office.", "کتابخانه سر نبش، روبه‌روی ادارهٔ پست است."),
                ("Take your old batteries to the recycling centre.", "باتری‌های کهنه را به مرکز بازیافت ببر."),
                ("Tomorrow will be cloudy with sunny spells and a light wind.", "فردا ابری با آفتاب پراکنده و باد ملایم خواهد بود."),
            ],
            [
                mcq("Where do you go to report a lost document officially?", "برای اعلام رسمی گم شدن مدرک کجا می‌روی؟", ["the library", "the police station", "the recycling centre", "the post office"], 1,
                    "The police station records lost documents officially.", "پلیس گم شدن مدارک را رسماً ثبت می‌کند."),
                mcq("'Sunny spells' means ___.", "«Sunny spells» یعنی ___.", ["a long hot day", "short periods of sun", "strong wind", "heavy rain"], 1,
                    "A spell is a short period.", "spell دورهٔ کوتاه است."),
            ],
            [
                gap("The bank is ___ the supermarket — they face each other.", ["opposite", "across from"], "Opposite / across from means facing.", "opposite / across from یعنی روبه‌رو."),
                gap("There's a 70% ___ of rain this afternoon.", ["chance"], "A forecast gives a chance of rain.", "پیش‌بینی هوا chance باران می‌دهد."),
                mcq("You ___ a form at the town hall.", "در شهرداری فرم را ___ .", ["fill in", "fill up", "fill on", "fill out of"], 0,
                    "Fill in (BrE) / fill out (AmE) a form.", "fill in (بریتانیایی) / fill out (آمریکایی) a form."),
                mcq("'It's freezing' means ___.", "«It's freezing» یعنی ___.", ["it's very cold", "it's raining", "it's windy", "it's warm"], 0,
                    "Freezing is extremely cold.", "freezing یعنی خیلی سرد."),
            ],
        ),
        lesson(
            "a2-u8-l3",
            "listening",
            ("A forecast and a plan", "پیش‌بینی هوا و یک برنامه"),
            ("Listen to a forecast and a plan, and hear the condition behind the decision.", "پیش‌بینی هوا و یک برنامه را بشنو و شرط پشت تصمیم را دریاب."),
            [
                ("A forecast is a list: today, tonight, tomorrow, with temperature and wind. Listen for the change, not every adjective: 'rain later' and 'clearing by the evening' tell you how to plan the day.", "پیش‌بینی هوا یک فهرست است: امروز، امشب، فردا، با دما و باد. به تغییر گوش کن، نه به همهٔ صفت‌ها: «rain later» و «clearing by the evening» می‌گویند روزت را چطور برنامه‌ریزی کنی."),
                ("Plans made from a forecast use the first conditional in speech: if it clears up, we'll go; otherwise we'll stay in. The words otherwise, in that case and so mark the result.", "برنامه‌هایی که از پیش‌بینی هوا ساخته می‌شوند در گفتار شرطی نوع اول دارند: if it clears up, we'll go; otherwise we'll stay in. واژه‌های otherwise، in that case و so نتیجه را نشان می‌دهند."),
            ],
            [
                ("'Rain until midday, then brighter in the afternoon.'", "«باران تا ظهر، بعدازظهر روشن‌تر می‌شود»."),
                ("'If it clears up after lunch, we'll take the kids to the park.'", "«اگر بعد از ناهار هوا باز شد، بچه‌ها را به پارک می‌بریم»."),
                ("'Otherwise we'll stay in and watch a film.'", "«وگرنه خانه می‌مانیم و فیلم می‌بینیم»."),
            ],
            [
                listen("Good morning. Rain until midday, then brighter in the afternoon, with a high of eighteen degrees. Tonight will be clear and cold.", "What will the afternoon be like?", "بعدازظهر هوا چطور خواهد بود؟", ["rainy all day", "brighter", "snowy", "very windy"], 1,
                       "'Brighter in the afternoon' after rain until midday.", "«Brighter in the afternoon» بعد از باران تا ظهر."),
                listen("Good morning. Rain until midday, then brighter in the afternoon, with a high of eighteen degrees. Tonight will be clear and cold.", "What is the highest temperature?", "بیشترین دما چند است؟", ["eight degrees", "eighteen degrees", "eighty degrees", "twelve degrees"], 1,
                       "The high is eighteen degrees.", "بیشترین دما هجده درجه است."),
            ],
            [
                listen("If it clears up after lunch, we'll take the kids to the park. Otherwise we'll stay in and watch a film. — Sounds good. I'll make lunch either way.", "What will they do if the weather improves?", "اگر هوا بهتر شود چه می‌کنند؟", ["watch a film", "take the kids to the park", "stay in bed", "go shopping"], 1,
                       "The park plan depends on the weather clearing.", "برنامهٔ پارک به باز شدن هوا بسته است."),
                listen("If it clears up after lunch, we'll take the kids to the park. Otherwise we'll stay in and watch a film. — Sounds good. I'll make lunch either way.", "What does the second speaker promise?", "گویندهٔ دوم چه قولی می‌دهد؟", ["to drive to the park", "to make lunch whatever happens", "to watch a film alone", "to check the forecast"], 1,
                       "'I'll make lunch either way' means in both cases.", "«I'll make lunch either way» یعنی در هر دو حالت."),
                mcq("'Otherwise' introduces ___.", "«Otherwise» ___ را معرفی می‌کند.", ["the condition", "the result if the condition is not true", "a new topic", "the time"], 1,
                    "Otherwise = if not, so it marks the alternative result.", "otherwise یعنی if not، پس نتیجهٔ جایگزین را نشان می‌دهد."),
                listen("We're meeting at the station at nine, so if you're late, text me. The train leaves at nine fifteen and it won't wait.", "What happens if the friend is late?", "اگر دوستش دیر کند چه می‌شود؟", ["the train waits", "they meet later", "he should text", "the station closes"], 2,
                       "'If you're late, text me' — the instruction for lateness is a text.", "«If you're late, text me» یعنی در صورت تأخیر پیام بده."),
            ],
        ),
    ],
)
