#!/usr/bin/env python3
"""B1 · units 3-4: what is done to things, and which thing we mean.

The passive puts the action first; relative clauses put the description inside
the sentence. Between them they turn three short A2 sentences into one B1 one.
"""

from course_kit import gap, lesson, listen, mcq, passage, unit

U3 = unit(
    "b1-u3",
    ("It was built in 1928", "در سال ۱۹۲۸ ساخته شد"),
    ("Describe processes and events when the doer is unknown, obvious or unimportant.", "فرایندها و رویدادها را وقتی کننده معلوم، بدیهی یا بی‌اهمیت است توصیف کن."),
    [
        lesson(
            "b1-u3-l1",
            "grammar",
            ("The passive voice", "مجهول"),
            ("Move the object to the front with be + past participle, and add by only when it matters.", "مفعول را با be + اسم مفعول به ابتدا بیاور و by را فقط وقتی مهم است اضافه کن."),
            [
                ("Active: the doer is the subject. Passive: the thing affected is the subject, and the form is be + past participle. They built the bridge in 1928 → The bridge was built in 1928.", "معلوم: کننده فاعل است. مجهول: چیزِ متأثر فاعل می‌شود و ساختار be + اسم مفعول است. They built the bridge in 1928 ← The bridge was built in 1928."),
                ("The tense lives in be: it is cleaned (present), it was cleaned (past), it has been cleaned (perfect), it will be cleaned (future), it is being cleaned (continuous). The participle never changes.", "زمان در be زندگی می‌کند: it is cleaned، it was cleaned، it has been cleaned، it will be cleaned، it is being cleaned. اسم مفعول هرگز عوض نمی‌شود."),
                ("Use the passive when the doer is unknown (my bike was stolen), obvious (he was arrested), unimportant (the forms are checked online), or when the process itself is the subject (the beans are roasted, then ground).", "مجهول را وقتی به کار ببر که کننده ناشناس (my bike was stolen)، بدیهی (he was arrested)، بی‌اهمیت (the forms are checked online) یا خود فرایند موضوع (the beans are roasted, then ground) باشد."),
                ("By introduces the doer only when it adds information: The novel was written by a fourteen-year-old. With verbs like give, send, offer, two passives exist: I was given the form / The form was given to me. Prefer the first.", "by فقط وقتی کننده را می‌آورد که اطلاعات اضافه کند: The novel was written by a fourteen-year-old. با فعل‌هایی مثل give، send، offer دو مجهول هست: I was given the form / The form was given to me. اولی را ترجیح بده."),
            ],
            [
                ("This mosque was built four hundred years ago.", "این مسجد چهارصد سال پیش ساخته شد."),
                ("The results will be announced on Friday.", "نتایج جمعه اعلام می‌شود."),
                ("My phone has been repaired, so I can call you tonight.", "گوشی‌ام تعمیر شده، پس امشب می‌توانم زنگ بزنم."),
                ("English is spoken in more than fifty countries.", "انگلیسی در بیش از پنجاه کشور صحبت می‌شود."),
                ("The letter was sent to the wrong address by mistake.", "نامه به‌اشتباه به نشانی اشتباه فرستاده شد."),
            ],
            [
                mcq("The bridge ___ in 1928.", "پل در ۱۹۲۸ ___ .", ["built", "was built", "is building", "has building"], 1,
                    "Past passive: was + past participle.", "مجهول گذشته: was + اسم مفعول."),
                mcq("Which sentence is passive?", "کدام جمله مجهول است؟", ["They repaired the road.", "The road was repaired.", "The road is long.", "We are repairing."], 1,
                    "Be + past participle with the object as subject.", "be + اسم مفعول با مفعول در جای فاعل."),
            ],
            [
                gap("The forms must ___ (send) before Friday.", ["be sent"], "Modal passive: modal + be + participle.", "مجهول با فعل وجهی: وجهی + be + اسم مفعول."),
                gap("This cake ___ (make) by my grandmother every year.", ["is made"], "Present passive, singular subject.", "مجهول حال، فاعل مفرد."),
                mcq("Why is the passive better here: 'My wallet was stolen on the bus'?", "چرا مجهول در «My wallet was stolen on the bus» بهتر است؟", ["because it is shorter", "because we do not know who stole it", "because it is formal", "because the wallet is important"], 1,
                    "The doer is unknown, so the passive is natural.", "کننده ناشناس است، پس مجهول طبیعی است."),
                listen("The old cinema was closed in 2015 and it has been turned into a library. The seats were removed, but the screen is still there.", "What is the building now?", "ساختمان حالا چیست؟", ["a cinema", "a library", "a shop", "a station"], 1,
                       "'It has been turned into a library.'", "«به کتابخانه تبدیل شده است»."),
            ],
        ),
        lesson(
            "b1-u3-l2",
            "vocabulary",
            ("Technology, data and the words of a process", "فناوری، داده و واژه‌های یک فرایند"),
            ("Describe how something works and what is done to data, files and devices.", "بگو چیزی چطور کار می‌کند و با داده، فایل و دستگاه چه کاری انجام می‌شود."),
            [
                ("Process verbs go in order: collect, store, process, transfer, share, delete. Data is uncountable and usually passive in technical writing: the data is stored on a server and processed automatically.", "فعل‌های فرایند ترتیب دارند: collect، store، process، transfer، share، delete. data نشماردنی است و در نوشتار فنی معمولاً مجهول می‌آید: the data is stored on a server and processed automatically."),
                ("Security words: password, log in, verify your identity, two-step verification, permission, access, back up (make a copy), a breach. 'Back up' is the verb and 'a backup' the noun — the same pattern as 'set up' / 'a setup'.", "واژه‌های امنیت: password، log in، verify your identity، two-step verification، permission، access، back up (نسخهٔ پشتیبان گرفتن)، breach. «back up» فعل و «a backup» اسم است، مثل «set up» و «a setup»."),
                ("Word formation: secure → security, private → privacy, rely → reliable, install → installation. The suffix usually decides the part of speech, so a noun after an article and an adjective before one: a reliable connection, the installation was quick.", "ساخت واژه: secure ← security، private ← privacy، rely ← reliable، install ← installation. پسوند نقش دستوری را تعیین می‌کند: a reliable connection، the installation was quick."),
            ],
            [
                ("All messages are stored for thirty days and then deleted automatically.", "همهٔ پیام‌ها سی روز ذخیره و بعد خودکار حذف می‌شوند."),
                ("You'll need to verify your identity before you can change the password.", "برای تغییر گذرواژه باید هویتت را تأیید کنی."),
                ("Back up your files before the update — the installation can fail.", "قبل از به‌روزرسانی از فایل‌ها پشتیبان بگیر؛ نصب ممکن است شکست بخورد."),
                ("The app asks for permission to use your location.", "اپ اجازهٔ استفاده از موقعیت مکانی را می‌خواهد."),
            ],
            [
                mcq("To make a copy of your files in case of a problem is to ___ them ___.", "کپی گرفتن از فایل‌ها برای روز مبادا ___ است.", ["back / up", "turn / up", "set / off", "log / out"], 0,
                    "Back up is the phrasal verb; a backup is the copy.", "back up فعل عبارتی و backup نسخهٔ کپی است."),
                mcq("A program that does not fail is ___.", "برنامه‌ای که خراب نمی‌شود ___ است.", ["reliable", "private", "automatic", "secure"], 0,
                    "Reliable means you can depend on it.", "reliable یعنی می‌توانی رویش حساب کنی."),
            ],
            [
                gap("The site asks for ___ to use your camera.", ["permission"], "You give or ask for permission.", "permission را می‌دهی یا می‌خواهی."),
                gap("The data ___ (store) on two servers for safety.", ["is stored"], "Passive present: is + participle.", "مجهول حال: is + اسم مفعول."),
                mcq("Which is the noun?", "کدام اسم است؟", ["install", "installation", "installed", "installing"], 1,
                    "The -tion form is the noun.", "شکل tion اسم است."),
                mcq("'Two-step verification' means ___.", "«Two-step verification» یعنی ___.", ["two passwords", "a second check of your identity", "two people must agree", "verifying twice a week"], 1,
                    "A second check, usually a code, confirms identity.", "بررسی دوم، معمولاً با کد، هویت را تأیید می‌کند."),
            ],
        ),
        lesson(
            "b1-u3-l3",
            "reading",
            ("How a bicycle is made", "دوچرخه چطور ساخته می‌شود"),
            ("Read a process description and put its stages in order.", "توصیف یک فرایند را بخوان و مرحله‌هایش را مرتب کن."),
            [
                ("A process text is held together by sequence markers (first, then, after that, finally) and by the passive, because the process, not the workers, is the subject. Follow the markers and you have the order.", "متن فرایند با نشانگرهای ترتیب (first، then، after that، finally) و مجهول به هم چسبیده است، چون موضوع خود فرایند است نه کارگران. نشانگرها را دنبال کن تا ترتیب را داشته باشی."),
                ("Numbers are usually given per unit or per hour, and 'about' signals that the figure is approximate. Reading 'about 300 frames a day' as exactly 300 is a misreading.", "عددها معمولاً برای هر واحد یا هر ساعت‌اند و «about» نشان می‌دهد عدد تقریبی است. خواندن «about 300 frames a day» به‌عنوان دقیقاً ۳۰۰ خطاست."),
            ],
            [
                ("First the tubes are cut and welded into a frame.", "اول لوله‌ها بریده و به هم جوش داده می‌شوند تا بدنه ساخته شود."),
                ("Then the frame is painted and left to dry for a day.", "بعد بدنه رنگ می‌شود و یک روز می‌ماند تا خشک شود."),
                ("After that the wheels are fitted and the brakes are adjusted by hand.", "پس از آن چرخ‌ها نصب و ترمزها دستی تنظیم می‌شوند."),
            ],
            [
                mcq("What happens to the frame after it is welded?", "بدنه بعد از جوش خوردن چه می‌شود؟", ["it is painted and dried", "it is sold", "the wheels are fitted", "it is cut"], 0,
                    "Then the frame is painted and left to dry.", "بعد بدنه رنگ می‌شود و خشک می‌ماند."),
                mcq("Why is the passive used in this text?", "چرا در این متن مجهول به کار رفته است؟", ["because the writer is formal", "because the process matters more than the workers", "because it is shorter", "because there are no workers"], 1,
                    "Process descriptions focus on what is done, not who does it.", "توصیف فرایند روی کاری است که انجام می‌شود، نه روی کننده."),
            ],
            [
                mcq("Which stage comes last?", "کدام مرحله آخر است؟", ["painting the frame", "cutting the tubes", "checking the finished bicycle", "fitting the wheels"], 2,
                    "The final check comes after wheels and brakes.", "بررسی نهایی بعد از چرخ‌ها و ترمزها می‌آید."),
                mcq("'About 300 frames a day' means ___.", "«About 300 frames a day» یعنی ___.", ["exactly 300", "roughly 300", "fewer than 200", "300 a week"], 1,
                    "'About' marks an approximate number.", "«about» عدد را تقریبی می‌کند."),
                mcq("What is done by hand?", "چه کاری با دست انجام می‌شود؟", ["the welding", "the painting", "adjusting the brakes", "cutting the tubes"], 2,
                    "'The brakes are adjusted by hand.'", "«ترمزها دستی تنظیم می‌شوند»."),
                mcq("Which detail is NOT in the text?", "کدام جزئیات در متن نیست؟", ["the frame is welded", "the frame is painted", "the bicycle is packed in cardboard", "the brakes are adjusted"], 2,
                    "Packing is not described.", "بسته‌بندی توصیف نشده است."),
            ],
            passage=passage(("How a bicycle is made", "دوچرخه چطور ساخته می‌شود"),
                            ("A bicycle begins as steel tubes. First the tubes are cut to length and welded into a frame. Each frame is checked by eye before it goes any further, because a weak joint will fail later.\n\nThen the frame is painted and left to dry for a day. After that the wheels are fitted, the gears are connected and the brakes are adjusted by hand — a machine cannot feel the tension that a good brake needs.\n\nFinally every bicycle is ridden twenty metres by a worker before it is packed. The factory makes about three hundred bicycles a day, and roughly one in fifty is sent back at this last check.",
                             "دوچرخه با لوله‌های فولادی شروع می‌شود. اول لوله‌ها به اندازه بریده و به هم جوش داده می‌شوند تا بدنه ساخته شود. هر بدنه پیش از رفتن به مرحلهٔ بعد با چشم بررسی می‌شود، چون جوش ضعیف بعداً می‌شکند.\n\nبعد بدنه رنگ می‌شود و یک روز می‌ماند تا خشک شود. پس از آن چرخ‌ها نصب، دنده‌ها وصل و ترمزها دستی تنظیم می‌شوند؛ ماشین نمی‌تواند کششی را که ترمز خوب لازم دارد حس کند.\n\nدر پایان هر دوچرخه پیش از بسته‌بندی بیست متر توسط یک کارگر سوار می‌شود. کارخانه حدود سیصد دوچرخه در روز می‌سازد و تقریباً یکی از هر پنجاه در همین بررسی آخر برگشت داده می‌شود.")),
        ),
    ],
)

U4 = unit(
    "b1-u4",
    ("The man who sold the shop", "مردی که مغازه را فروخت"),
    ("Identify people and things inside a sentence, and review what you watch.", "آدم‌ها و چیزها را داخل جمله مشخص کن و آنچه می‌بینی را نقد کن."),
    [
        lesson(
            "b1-u4-l1",
            "grammar",
            ("Relative clauses: who, which, that, whose, where", "بندهای موصولی: who، which، that، whose، where"),
            ("Add information about a noun without starting a new sentence.", "بدون شروع جملهٔ تازه اطلاعاتی دربارهٔ یک اسم اضافه کن."),
            [
                ("Who is for people, which for things, that for both in defining clauses: the teacher who taught me, the book which changed my mind, the film that everyone talks about. Where replaces a place: the town where I grew up.", "who برای آدم‌ها، which برای چیزها و that برای هر دو در بندهای تعیین‌کننده است: the teacher who taught me، the book which changed my mind، the film that everyone talks about. where جای مکان می‌آید: the town where I grew up."),
                ("Whose replaces a possessive: the writer whose book I read. It joins two nouns without 'his' or 'her'.", "whose جای possessive می‌آید: the writer whose book I read. دو اسم را بدون his یا her وصل می‌کند."),
                ("Defining clauses are essential and take no commas: The students who failed the test must retake it. Non-defining clauses add extra information and take commas: My brother, who lives in Berlin, is visiting. Removing a non-defining clause leaves a complete sentence; removing a defining one does not.", "بند تعیین‌کننده ضروری است و ویرگول ندارد: The students who failed the test must retake it. بند توصیفی اطلاعات اضافه می‌دهد و ویرگول دارد: My brother, who lives in Berlin, is visiting. حذف بند توصیفی جمله را کامل می‌گذارد؛ حذف تعیین‌کننده نه."),
                ("The pronoun can be dropped when it is the object: the film (that) I watched. It cannot be dropped when it is the subject: the man who called me — not 'the man called me' if you mean a specific man.", "وقتی ضمیر مفعول است می‌توان حذفش کرد: the film (that) I watched. وقتی فاعل است نمی‌شود: the man who called me."),
            ],
            [
                ("The woman who runs the bakery is my neighbour.", "زنی که نانوایی را می‌گرداند همسایهٔ من است."),
                ("This is the app that helped me learn vocabulary.", "این همان اپی است که در یادگیری واژگان کمکم کرد."),
                ("We stayed in a village where there was no internet.", "در روستایی ماندیم که اینترنت نداشت."),
                ("My teacher, who retired last year, still writes to us.", "معلمم، که پارسال بازنشسته شد، هنوز برای ما نامه می‌نویسد."),
                ("That's the writer whose novels my mother loves.", "این همان نویسنده‌ای است که مادرم رمان‌هایش را دوست دارد."),
            ],
            [
                mcq("The film ___ we watched last night was better than the book.", "فیلمی که دیشب دیدیم از کتاب بهتر بود.", ["who", "whose", "which", "where"], 2,
                    "Things take which or that.", "چیزها which یا that می‌گیرند."),
                mcq("She's the colleague ___ helped me with the report.", "او همکاری است که در گزارش کمکم کرد.", ["which", "who", "whose", "where"], 1,
                    "People take who (or that).", "آدم‌ها who (یا that) می‌گیرند."),
            ],
            [
                gap("That's the café ___ we first met.", ["where"], "Where replaces the place.", "where جای مکان می‌آید."),
                gap("I met a man ___ brother works with you.", ["whose"], "Possessive: whose brother.", "مالکیت: whose brother."),
                mcq("Which sentence needs commas?", "کدام جمله ویرگول لازم دارد؟", ["The students who failed must retake the test.", "My brother who lives in Berlin is visiting.", "The book that I bought was expensive.", "The town where I grew up is small."], 1,
                    "The clause about the brother only adds information.", "بند مربوط به برادر فقط اطلاعات اضافه می‌کند."),
                mcq("Where can the relative pronoun be left out?", "کجا می‌توان ضمیر موصولی را حذف کرد؟", ["The man who called me.", "The film that I watched.", "The woman who runs the shop.", "The village where I live."], 1,
                    "An object pronoun can be omitted: the film I watched.", "ضمیر مفعولی قابل حذف است: the film I watched."),
            ],
        ),
        lesson(
            "b1-u4-l2",
            "vocabulary",
            ("Media, entertainment and what you thought of it", "رسانه، سرگرمی و نظرت دربارهٔ آن"),
            ("Recommend, criticise and summarise a series, a film or a book.", "سریال، فیلم یا کتاب را توصیه، نقد یا خلاصه کن."),
            [
                ("A review needs its own nouns: plot (the story), character (the people), setting (where and when), pace (fast or slow), soundtrack, cast (the actors), episode, season, ending. A spoiler reveals the plot.", "نقد واژه‌های خودش را دارد: plot (داستان)، character (آدم‌ها)، setting (زمان و مکان)، pace (تند یا کند)، soundtrack، cast (بازیگران)، episode، season، ending. spoiler داستان را لو می‌دهد."),
                ("Opinion adjectives are graded: brilliant, gripping, moving, entertaining, predictable, slow, disappointing, overrated. 'It was fine' is the weakest positive; 'it didn't work for me' criticises without insulting.", "صفت‌های نظر درجه‌بندی دارند: brilliant، gripping، moving، entertaining، predictable، slow، disappointing، overrated. «It was fine» ضعیف‌ترین مثبت است و «it didn't work for me» بدون توهین نقد می‌کند."),
                ("Recommendation patterns: I'd recommend it to anyone who likes…, it's worth watching, it's not worth the time, it reminded me of…, it's based on a true story. Notice worth + -ing.", "الگوهای توصیه: I'd recommend it to anyone who likes…، it's worth watching، it's not worth the time، it reminded me of…، it's based on a true story. توجه کن به worth + ing."),
            ],
            [
                ("The plot is simple, but the characters are believable and the acting is excellent.", "داستان ساده است، اما شخصیت‌ها باورپذیرند و بازی عالی است."),
                ("It's gripping for two seasons, then the pace slows and it becomes predictable.", "دو فصل گیراست، بعد ریتم کند می‌شود و قابل پیش‌بینی."),
                ("It's worth watching for the soundtrack alone.", "فقط برای موسیقی متنش ارزش دیدن دارد."),
                ("I wouldn't recommend it to anyone who has read the book.", "به کسی که کتاب را خوانده توصیه نمی‌کنم."),
            ],
            [
                mcq("The story of a film is its ___.", "داستان یک فیلم ___ آن است.", ["cast", "plot", "setting", "pace"], 1,
                    "The plot is the sequence of events.", "plot زنجیرهٔ رویدادها است."),
                mcq("If a film is easy to guess, it is ___.", "اگر فیلمی راحت حدس زده شود، ___ است.", ["gripping", "predictable", "moving", "overrated"], 1,
                    "Predictable means you see what is coming.", "predictable یعنی ادامه‌اش را می‌بینی."),
            ],
            [
                gap("The film is ___ on a true story from the 1970s.", ["based"], "Be based on a true story.", "عبارت be based on یعنی برگرفته از چیزی بودن."),
                gap("It's ___ watching, even if the ending is weak.", ["worth"], "Worth + -ing.", "بعد از worth فعل با ing می‌آید."),
                mcq("'Overrated' means ___.", "«Overrated» یعنی ___.", ["better than people say", "not as good as people say", "very old", "too long"], 1,
                    "Overrated: praised more than it deserves.", "overrated یعنی بیشتر از ارزشش تحسین شده."),
                mcq("Which is the weakest opinion?", "کدام نظر ضعیف‌ترین است؟", ["It was brilliant.", "It was fine.", "It was gripping.", "It was moving."], 1,
                    "'Fine' is polite but unenthusiastic.", "«fine» مؤدبانه اما بی‌اشتیاق است."),
            ],
        ),
        lesson(
            "b1-u4-l3",
            "listening",
            ("A review of a series", "نقد یک سریال"),
            ("Hear a recommendation and separate the praise from the criticism.", "توصیه‌ای را بشنو و تعریف را از نقد جدا کن."),
            [
                ("A spoken review alternates: what it is, what is good, what is not, who it suits. Signposts do the work — 'the best thing about it', 'the problem is', 'having said that', 'if you like…'. The recommendation usually comes last.", "نقد گفتاری تناوب دارد: چیست، چه چیز خوبش است، چه چیز نه، به چه کسی می‌خورد. نشانه‌ها کار را می‌کنند: «the best thing about it»، «the problem is»، «having said that»، «if you like…». توصیه معمولاً آخر می‌آید."),
                ("'Having said that' takes back part of what came before without cancelling it. It is the phrase that separates a reviewer who is fair from one who is only enthusiastic.", "«Having said that» بخشی از گفتهٔ قبل را محدود می‌کند بی‌آنکه لغو کند. همین عبارت نقد منصف را از نقد فقط مشتاق جدا می‌کند."),
            ],
            [
                ("'The best thing about it is the acting — the two leads are wonderful.'", "«بهترین بخشش بازی است؛ دو نقش اصلی عالی‌اند»."),
                ("'The problem is the third season, which repeats itself.'", "«مشکل فصل سوم است که خودش را تکرار می‌کند»."),
                ("'Having said that, the ending is worth the wait.'", "«با این حال، پایانش ارزش صبر کردن را دارد»."),
            ],
            [
                listen("I've just finished the series. The best thing about it is the acting — the two leads are wonderful. The problem is the third season, which repeats itself. Having said that, the ending is worth the wait.", "What is the main criticism?", "نقد اصلی چیست؟", ["the acting", "the third season repeats itself", "the ending", "the soundtrack"], 1,
                       "The third season repeats itself.", "فصل سوم خودش را تکرار می‌کند."),
                listen("I've just finished the series. The best thing about it is the acting — the two leads are wonderful. The problem is the third season, which repeats itself. Having said that, the ending is worth the wait.", "How does she feel about the ending?", "دربارهٔ پایان چه حسی دارد؟", ["it ruins the series", "it is worth the wait", "it is too short", "she has not seen it"], 1,
                       "'The ending is worth the wait.'", "«پایانش ارزش صبر کردن را دارد»."),
            ],
            [
                listen("Would I recommend it? Yes, if you like slow stories about families. If you want action, this isn't for you.", "Who is the series for?", "سریال برای چه کسی است؟", ["people who like action", "people who like slow family stories", "children", "people who dislike acting"], 1,
                       "She recommends it to lovers of slow family stories.", "آن را به دوستداران داستان‌های آرام خانوادگی توصیه می‌کند."),
                listen("The film is beautifully shot and the music is memorable, but the plot is predictable and the ending feels rushed.", "Which two things are praised?", "کدام دو چیز تحسین می‌شود؟", ["plot and ending", "photography and music", "acting and plot", "music and ending"], 1,
                       "The photography and the music are the positives.", "فیلم‌برداری و موسیقی نکات مثبت‌اند."),
                mcq("'Having said that' introduces ___.", "«Having said that» ___ را معرفی می‌کند.", ["a repetition", "a limitation of the previous point", "a new topic", "a conclusion"], 1,
                    "It qualifies what was just said.", "گفتهٔ قبلی را محدود می‌کند."),
                mcq("'It didn't work for me' means ___.", "«It didn't work for me» یعنی ___.", ["it was broken", "I did not enjoy it", "I did not understand it", "it was too short"], 1,
                    "A polite way to say it was not to your taste.", "راهی مؤدبانه برای گفتن اینکه به سلیقه‌ات نخورد."),
            ],
        ),
    ],
)
