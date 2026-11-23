"""B1-B2 pages, part four: passive_voice ... future_perfect."""

P = {
    "passive_voice": dict(
        scene=(
            "The bridge was built in 1932 and is repaired every ten years. Last "
            "winter it was closed for a month, and a new rail was put in.",
            "پل در ۱۹۳۲ ساخته شد و هر ده سال تعمیر می‌شود. زمستان پیش یک ماه بسته "
            "بود و نردهٔ تازه‌ای نصب شد.",
        ),
        pairs=[
            ("این کتاب را سال ۱۹۹۰ نوشتند.",
             "This book wrote in 1990.",
             "This book was written in 1990.",
             "when the doer is unknown or unimportant, English turns the object "
             "into the subject and keeps be + V3.",
             "وقتی کننده معلوم نیست، مفعول فاعل می‌شود و be + قسمت سوم فعل می‌ماند."),
            ("به من گفتند صبر کنم.",
             "They said me to wait.",
             "I was told to wait.",
             "English has no subjectless «گفتند»: you either name them or use the "
             "passive, which is what a report usually does.",
             "انگلیسی فعل بی‌فاعل ندارد؛ یا فاعل را می‌گویی یا مجهول می‌سازی."),
        ],
        mistakes=[
            ("The letter was wrote yesterday.",
             "The letter was written yesterday.",
             "the passive takes the third form: write, wrote, written.",
             "مجهول قسمت سوم فعل می‌خواهد: write, wrote, written.",
             "participle form"),
            ("The house was build in 1990.",
             "The house was built in 1990.",
             "built is the third form of build; build is the base and cannot "
             "follow was.",
             "سومِ build می‌شود built؛ build بعد از was نمی‌آید.",
             "participle form"),
        ],
    ),
    "gerunds_infinitives": dict(
        scene=(
            "I enjoy reading at night, but I decided to stop buying books this "
            "year. Avoiding the shop is easier than avoiding the website.",
            "شب‌ها از خواندن لذت می‌برم، ولی تصمیم گرفتم امسال کتاب نخرم. دوری از "
            "مغازه از دوری از سایت آسان‌تر است.",
        ),
        pairs=[
            ("تصمیم گرفتم بروم.",
             "I decided going.",
             "I decided to go.",
             "decide takes to + verb; the -ing after it is the Persian structure "
             "written in English words.",
             "decide با to می‌آید؛ ing اینجا ترجمهٔ ساختار فارسی است."),
            ("خوب آشپزی کردن سخت است.",
             "Be good at cooking is hard.",
             "Being good at cooking is hard.",
             "a verb in the subject position takes -ing; the bare verb cannot "
             "open an English sentence.",
             "فعل در جای فاعل ing می‌گیرد؛ مصدرِ بی‌to آغاز جمله نمی‌آید."),
        ],
        mistakes=[
            ("I enjoy to read books.",
             "I enjoy reading books.",
             "enjoy is one of the verbs that only takes -ing: enjoy, avoid, finish, "
             "mind, suggest.",
             "enjoy فقط ing می‌گیرد: enjoy, avoid, finish, mind.",
             "gerund form"),
            ("She is good at cook.",
             "She is good at cooking.",
             "after a preposition the verb always takes -ing.",
             "بعد از حرف اضافه فعل همیشه ing می‌گیرد.",
             "gerund form"),
        ],
    ),
    "relative_clauses": dict(
        scene=(
            "The man who called you is my uncle. The office where he works is the "
            "building whose windows are always open.",
            "مردی که به تو زنگ زد عموی من است. دفتری که در آن کار می‌کند همان "
            "ساختمانی است که پنجره‌هایش همیشه باز است.",
        ),
        pairs=[
            ("کتابی که خریدم خوب بود.",
             "The book that I bought it was good.",
             "The book that I bought was good.",
             "the relative pronoun replaces the object, so the it cannot stay — "
             "Persian keeps its «آن» and English does not.",
             "ضمیر موصول جای مفعول می‌نشیند؛ «آن» فارسی در انگلیسی نمی‌ماند."),
            ("مردی که دیدمش.",
             "The man who I saw him.",
             "The man who I saw.",
             "who already stands for him; keeping both doubles the object.",
             "who خودش جای him را می‌گیرد؛ هر دو با هم نمی‌آیند."),
        ],
        mistakes=[
            ("The woman which lives next door is a doctor.",
             "The woman who lives next door is a doctor.",
             "who is for people, which for things.",
             "who برای انسان است و which برای چیز.",
             "relative pronoun"),
            ("The city where I was born in is small.",
             "The city where I was born is small.",
             "where already means in which, so the in has no work left.",
             "where خودش یعنی in which؛ in دوباره لازم نیست.",
             "relative pronoun"),
        ],
    ),
    "purpose_reason": dict(
        scene=(
            "I study English to get a better job. I started because a friend "
            "recommended the course, and I keep going so that my children see me "
            "trying.",
            "انگلیسی می‌خوانم تا کار بهتری پیدا کنم. شروع کردم چون دوستی دوره را "
            "پیشنهاد داد، و ادامه می‌دهم تا بچه‌هایم تلاشم را ببینند.",
        ),
        pairs=[
            ("آمدم اینجا که تو را ببینم.",
             "I came here for to see you.",
             "I came here to see you.",
             "purpose takes to + verb, not for to; for is only used before a noun.",
             "هدف با to + فعل گفته می‌شود؛ for فقط قبل از اسم می‌آید."),
            ("چون باران می‌بارید، نرفتیم.",
             "For it was raining, we didn't go.",
             "Because it was raining, we didn't go.",
             "«چون» at the start of a sentence is because or since; for is "
             "literary and almost never opens a spoken sentence.",
             "«چون» در آغاز جمله because یا since است؛ for تقریباً فقط در نوشتار ادبی."),
        ],
        mistakes=[
            ("I went to the shop for buying milk.",
             "I went to the shop to buy milk.",
             "for is followed by a noun; purpose with a verb needs the infinitive.",
             "for قبل از اسم است؛ هدف با فعل مصدر می‌خواهد.",
             "purpose form"),
            ("She studies hard for to pass the exam.",
             "She studies hard to pass the exam.",
             "for to is not English in any register.",
             "«for to» در هیچ سطحی انگلیسی نیست.",
             "purpose form"),
        ],
    ),
    "reported_speech": dict(
        scene=(
            "«I am tired,» he said. He said he was tired, and that he would call "
            "me later. I told him I had already gone to bed.",
            "«خسته‌ام»، گفت. گفت خسته است و بعداً زنگ می‌زند. من هم گفتم که "
            "خوابیده بودم.",
        ),
        pairs=[
            ("گفت فردا می‌آید.",
             "He said he will come tomorrow.",
             "He said he would come the next day.",
             "everything shifts back one step: will becomes would, and tomorrow "
             "becomes the next day.",
             "همه چیز یک پله عقب می‌رود: will به would و tomorrow به the next day."),
            ("به من گفت بیا.",
             "He said me to come.",
             "He told me to come.",
             "said needs no person after it; told takes the person directly.",
             "said کسی را بعد خودش نمی‌گیرد؛ told شخص را می‌گیرد."),
        ],
        mistakes=[
            ("He said me that he was busy.",
             "He told me that he was busy.",
             "said does not take a person as object; told does.",
             "said شخص را مفعول نمی‌گیرد؛ told می‌گیرد.",
             "reported verb"),
            ("She said she is ill yesterday.",
             "She said she was ill yesterday.",
             "the reporting verb is past, so the reported verb moves back too.",
             "فعل گزارش در گذشته است، پس فعل نقل هم عقب می‌رود.",
             "reported tense"),
        ],
    ),
    "linking_words": dict(
        scene=(
            "It was raining; however, we went out. We were late, so we missed the "
            "first song. Although the hall was full, nobody complained.",
            "باران می‌بارید؛ با این حال بیرون رفتیم. دیر رسیدیم، پس اولین آهنگ را "
            "از دست دادیم. هرچند سالن پر بود، کسی شکایت نکرد.",
        ),
        pairs=[
            ("هرچند خسته بود، آمد.",
             "Although he was tired, but he came.",
             "Although he was tired, he came.",
             "although already carries the contrast; English does not pair it with "
             "but the way Persian pairs «هرچند... ولی».",
             "although خودش تضاد را می‌رساند؛ با but جمع نمی‌شود."),
            ("باران می‌بارید، با این حال رفتیم.",
             "It was raining, however we went.",
             "It was raining; however, we went.",
             "however is an adverb, so it needs a full stop or semicolon before "
             "it, not a comma.",
             "however قید است و قبلش نقطه یا نقطه‌ویرگول لازم دارد، نه ویرگول."),
        ],
        mistakes=[
            ("Because it was late, so we went home.",
             "Because it was late, we went home.",
             "because and so both mark the same relation; one of them has to go.",
             "because و so هر دو یک رابطه را نشان می‌دهند؛ یکی کافی است.",
             "linking pair"),
            ("Although it was expensive, but I bought it.",
             "Although it was expensive, I bought it.",
             "although and but cannot share a sentence.",
             "although و but در یک جمله نمی‌آیند.",
             "linking pair"),
        ],
    ),
    "past_perfect": dict(
        scene=(
            "When I arrived, the class had already started. The teacher had written "
            "three words on the board, and nobody had told me about the test.",
            "وقتی رسیدم، کلاس شروع شده بود. معلم سه کلمه روی تخته نوشته بود و "
            "هیچ‌کس دربارهٔ امتحان به من نگفته بود.",
        ),
        pairs=[
            ("وقتی رسیدم، رفته بود.",
             "When I arrived, he went.",
             "When I arrived, he had gone.",
             "the earlier of two past events takes had + V3, or the order of the "
             "story disappears.",
             "کارِ زودتر با had + قسمت سوم می‌آید، وگرنه ترتیب ماجرا گم می‌شود."),
            ("قبل از اینکه بیایم، خورده بودم.",
             "Before I came, I have eaten.",
             "Before I came, I had eaten.",
             "have is anchored to now; had is anchored to another past moment.",
             "have به «حالا» بسته است و had به یک لحظهٔ گذشته."),
        ],
        mistakes=[
            ("When I arrived, the film already started.",
             "When I arrived, the film had already started.",
             "the film started before I arrived, and that order needs had.",
             "فیلم قبل از رسیدن من شروع شده بود و این ترتیب had می‌خواهد.",
             "past perfect use"),
            ("She had went home before I called.",
             "She had gone home before I called.",
             "the perfect takes the third form: go, went, gone.",
             "حال کامل قسمت سوم فعل می‌خواهد: gone.",
             "participle form"),
        ],
    ),
    "future_perfect": dict(
        scene=(
            "By June, I will have finished the course. By then the children will "
            "have grown another year, and the flat will have been painted twice.",
            "تا خرداد دوره را تمام کرده‌ام. تا آن موقع بچه‌ها یک سال بزرگ‌تر شده‌اند "
            "و خانه دو بار رنگ شده است.",
        ),
        pairs=[
            ("تا فردا کارم را تمام می‌کنم.",
             "By tomorrow I will finish my work.",
             "By tomorrow I will have finished my work.",
             "by names a deadline, and a deadline looks back at the work already "
             "done before it.",
             "by یک مهلت است و از آن مهلت به کارِ تمام‌شده نگاه می‌کنیم."),
            ("تا سال آینده اینجا ده سال کار کرده‌ام.",
             "By next year I will work here for ten years.",
             "By next year I will have been working here for ten years.",
             "a length of time up to a future point takes will have been + -ing.",
             "مدت زمان تا یک نقطهٔ آینده will have been + ing می‌گیرد."),
        ],
        mistakes=[
            ("By 2030, I will finish my studies.",
             "By 2030, I will have finished my studies.",
             "by marks a point the action is complete before; will finish leaves "
             "it open.",
             "by نقطه‌ای است که کار قبلش تمام شده؛ will finish آن را باز می‌گذارد.",
             "future perfect use"),
            ("She will have went by then.",
             "She will have gone by then.",
             "will have takes the third form, so go becomes gone.",
             "will have قسمت سوم فعل می‌خواهد: gone.",
             "participle form"),
        ],
    ),
}
