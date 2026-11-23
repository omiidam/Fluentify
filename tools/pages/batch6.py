"""C1-C2 pages, part six: complex_modals ... participle_clauses."""

P = {
    "complex_modals": dict(
        scene=(
            "She must have left already, because her coat is gone. He might have "
            "taken the wrong bus, and I should have checked the timetable.",
            "حتماً رفته است، چون کتش نیست. شاید اتوبوس اشتباهی سوار شده و بهتر بود "
            "برنامهٔ حرکت را نگاه می‌کردم.",
        ),
        pairs=[
            ("حتماً فراموش کرده است.",
             "He must forgot.",
             "He must have forgotten.",
             "certainty about the past is must have + V3, not must + past.",
             "حدس قطعی دربارهٔ گذشته must have + قسمت سوم است."),
            ("نمی‌بایست این را می‌گفتم.",
             "I must not have said this.",
             "I shouldn't have said this.",
             "mustn't have means «it is impossible that…»; regret uses shouldn't "
             "have.",
             "mustn't have یعنی «محال است که…»؛ حسرت با shouldn't have گفته می‌شود."),
        ],
        mistakes=[
            ("She might have went out.",
             "She might have gone out.",
             "modal + have takes the third form: go, went, gone.",
             "بعد از might have قسمت سوم فعل می‌آید: gone.",
             "participle form"),
            ("You could have told to me.",
             "You could have told me.",
             "tell takes a direct object, with no to before it.",
             "tell مفعول بی‌واسطه می‌گیرد، بی to.",
             "verb pattern"),
        ],
    ),
    "ellipsis": dict(
        scene=(
            "«I love Italian food.» «So do I.» «I can't come on Friday.» «Nor can "
            "I.» Nobody repeats the whole sentence when a short one will do.",
            "«من عاشق غذای ایتالیایی‌ام.» «من هم.» «جمعه نمی‌توانم بیایم.» «من هم "
            "نمی‌توانم.» کسی جملهٔ کامل را تکرار نمی‌کند وقتی کوتاه‌ترش کار می‌کند.",
        ),
        pairs=[
            ("من هم دوستش دارم.",
             "Me too like it.",
             "So do I.",
             "agreement with a present-tense verb is so + auxiliary + subject: so "
             "do I, so does she.",
             "موافقت با فعل حال: so + فعل کمکی + فاعل."),
            ("من هم نمی‌توانم.",
             "I can't too.",
             "Neither can I. (or: Nor can I.)",
             "a negative agreement inverts after neither or nor; too is only for "
             "positive sentences.",
             "موافقت منفی با neither/nor و وارونگی می‌آید؛ too فقط برای مثبت است."),
        ],
        mistakes=[
            ("So I do.",
             "So do I.",
             "the auxiliary comes before the subject in this agreement.",
             "در این ساختار فعل کمکی قبل از فاعل می‌آید.",
             "ellipsis form"),
            ("I don't like it. — Me too.",
             "I don't like it. — Me neither.",
             "me too agrees with a positive statement; a negative one takes me "
             "neither.",
             "me too با جملهٔ مثبت می‌آید؛ برای منفی me neither.",
             "ellipsis form"),
        ],
    ),
    "nominalization": dict(
        scene=(
            "The implementation of the policy took six months. Its success depended "
            "on the cooperation of three departments, and the delay caused a "
            "revision of the plan.",
            "اجرای این سیاست شش ماه طول کشید. موفقیتش به همکاری سه بخش بستگی داشت و "
            "تأخیر باعث بازنگری نقشه شد.",
        ),
        pairs=[
            ("ما تصمیم گرفتیم که پروژه را متوقف کنیم.",
             "We made a decision of stopping the project.",
             "We decided to stop the project.",
             "a verb is shorter and clearer than a noun made from it; keep the "
             "decision as decided unless the writing is formal.",
             "فعل کوتاه‌تر و روشن‌تر از اسم ساخته‌شده از آن است."),
            ("بررسی این موضوع ضروری است.",
             "Review of this matter is necessary.",
             "A review of this matter is necessary.",
             "the nominalisation needs its article; without one the phrase reads "
             "like a telegram.",
             "اسم‌سازی حرف تعریف خودش را می‌خواهد."),
        ],
        mistakes=[
            ("The discuss of the problem took hours.",
             "The discussion of the problem took hours.",
             "the noun from discuss is discussion; discuss is only a verb.",
             "اسمِ discuss می‌شود discussion؛ خودش فعل است.",
             "nominal form"),
            ("We made an improvement of the system by to update it.",
             "We improved the system by updating it.",
             "one nominalisation per sentence is plenty; here the verb is both "
             "shorter and more accurate.",
             "یک اسم‌سازی در جمله کافی است؛ فعل هم کوتاه‌تر است هم دقیق‌تر.",
             "nominalization use"),
        ],
    ),
    "used_to_would": dict(
        scene=(
            "I used to live in Shiraz. We would walk to the bazaar every Friday, and "
            "my grandmother would make tea before we left.",
            "قبلاً در شیراز زندگی می‌کردم. هر جمعه پیاده تا بازار می‌رفتیم و "
            "مادربزرگم قبل از رفتن چای می‌گذاشت.",
        ),
        pairs=[
            ("قبلاً در شیراز زندگی می‌کردم.",
             "I would live in Shiraz.",
             "I used to live in Shiraz.",
             "would only repeats actions; living somewhere is a state, and states "
             "take used to.",
             "would فقط کارهای تکرارشده را می‌گوید؛ زندگی کردن حالت است و used to می‌گیرد."),
            ("او قبلاً سیگار می‌کشید.",
             "He used to smoked.",
             "He used to smoke.",
             "used to is followed by the base verb: the past is already in used.",
             "بعد از used to فعل پایه می‌آید؛ گذشته در خود used هست."),
        ],
        mistakes=[
            ("I am used to live in Tehran.",
             "I used to live in Tehran.",
             "used to + verb is the past habit; be used to + -ing means it feels "
             "normal now.",
             "used to + فعل گذشتهٔ عادت است؛ be used to + ing یعنی الان عادی است."),
            ("She didn't used to like coffee.",
             "She didn't use to like coffee.",
             "after didn't the verb is the base: use to, not used to.",
             "بعد از didn't فعل پایه می‌آید: use to.",
             "used to form"),
        ],
    ),
    "future_continuous": dict(
        scene=(
            "At eight tomorrow I will be sitting in the same exam hall. We will be "
            "travelling most of Friday, so call in the evening.",
            "فردا ساعت هشت در همان سالن امتحان نشسته‌ام. بیشتر جمعه در راهیم، پس "
            "شب زنگ بزن.",
        ),
        pairs=[
            ("فردا ساعت هشت در راهم.",
             "Tomorrow at eight I will travel.",
             "Tomorrow at eight I will be travelling.",
             "an action in progress at a future moment takes will be + -ing.",
             "کاری که در لحظه‌ای از آینده در جریان است will be + ing می‌گیرد."),
            ("هنوز نمی‌دانم چه کار می‌کنم.",
             "I don't know yet what I will do at that time.",
             "I don't know yet what I will be doing at that time.",
             "the continuous is what makes the future moment feel occupied.",
             "وجه استمراری است که آن لحظهٔ آینده را «مشغول» نشان می‌دهد."),
        ],
        mistakes=[
            ("At 8 I will studying.",
             "At 8 I will be studying.",
             "will be + -ing needs both words; will studying has no verb.",
             "will be + ing هر دو واژه را می‌خواهد؛ will studying فعل ندارد.",
             "progressive form"),
            ("This time tomorrow I am flying is sure.",
             "This time tomorrow I will be flying.",
             "a fixed arrangement can use the present continuous, but a statement "
             "about a moment needs will be + -ing.",
             "برای لحظهٔ آینده will be + ing روشن‌تر است.",
             "future form"),
        ],
    ),
    "future_perfect_continuous": dict(
        scene=(
            "By June, I will have been working here for five years. By the time the "
            "guests arrive, we will have been cooking for six hours.",
            "تا خرداد پنج سال است که اینجا کار می‌کنم. تا وقتی مهمان‌ها برسند، شش "
            "ساعت است که آشپزی می‌کنیم.",
        ),
        pairs=[
            ("تا سال آینده ده سال است که اینجا کار می‌کنم.",
             "By next year I will work here for ten years.",
             "By next year I will have been working here for ten years.",
             "a length of time measured up to a future point takes will have been "
             "+ -ing.",
             "مدت زمان تا نقطه‌ای در آینده will have been + ing می‌گیرد."),
            ("تا فردا سه ساعت است که درس می‌خوانم.",
             "By tomorrow I will study for three hours.",
             "By tomorrow I will have been studying for three hours.",
             "without the perfect continuous the sentence says only that the study "
             "will happen, not how long it will have lasted.",
             "بی این ساختار جمله فقط می‌گوید درس خواندن اتفاق می‌افتد، نه چقدر طول کشیده."),
        ],
        mistakes=[
            ("By June I will have been work here for a year.",
             "By June I will have been working here for a year.",
             "have been takes the -ing form; been work is two verbs with no link.",
             "بعد از have been فعل ing می‌گیرد.",
             "progressive form"),
            ("In June I will have been working here since five years.",
             "In June I will have been working here for five years.",
             "a length of time takes for; since takes a starting point.",
             "مدت زمان for می‌گیرد و نقطهٔ شروع since.",
             "preposition choice"),
        ],
    ),
    "so_such_too_enough": dict(
        scene=(
            "The coffee is too hot to drink. It was such a good film that we "
            "watched it twice, and the seats were not comfortable enough.",
            "قهوه آن‌قدر داغ است که نمی‌شود خورد. فیلم چنان خوبی بود که دو بار "
            "دیدیمش و صندلی‌ها به‌قدر کافی راحت نبودند.",
        ),
        pairs=[
            ("او آن‌قدر خسته بود که خوابش برد.",
             "He was so tired that he slept.",
             "He was so tired that he fell asleep.",
             "so goes before an adjective, and «خوابش برد» is fall asleep, not "
             "sleep.",
             "so قبل از صفت و such قبل از صفت + اسم می‌آید؛ «خوابش برد» یعنی fall asleep."),
            ("برای من به‌قدر کافی بزرگ است.",
             "It is enough big for me.",
             "It is big enough for me.",
             "enough comes after the adjective, not before it.",
             "enough بعد از صفت می‌آید، نه قبلش."),
        ],
        mistakes=[
            ("It was so beautiful weather that we stayed.",
             "It was such beautiful weather that we stayed.",
             "before an adjective plus a noun the word is such, not so.",
             "قبل از صفت + اسم such می‌آید، نه so.",
             "so/such form"),
            ("He is enough old to drive.",
             "He is old enough to drive.",
             "enough follows the adjective.",
             "enough بعد از صفت می‌آید.",
             "enough position"),
        ],
    ),
    "participle_clauses": dict(
        scene=(
            "Walking home, I saw an old friend. Built in 1900, the bridge still "
            "carries traffic, and having finished the report, she went to bed.",
            "وقتی پیاده به خانه می‌رفتم، دوست قدیمی‌ای دیدم. پل که در ۱۹۰۰ ساخته شد "
            "هنوز ترافیک را حمل می‌کند و سارا بعد از تمام کردن گزارش خوابید.",
        ),
        pairs=[
            ("وقتی داشتم پیاده می‌رفتم، باران گرفت.",
             "Walking home, it started to rain.",
             "Walking home, I got caught in the rain.",
             "the participle's subject must be the subject of the main clause; it "
             "cannot be walking while the rain starts.",
             "فاعل عبارت وصفی باید همان فاعل جملهٔ اصلی باشد."),
            ("با تمام کردن گزارش، خوابید.",
             "Finishing the report, she went to bed.",
             "Having finished the report, she went to bed.",
             "finishing says both things happen at once; having + V3 puts the "
             "report first, which is what the Persian means.",
             "having + قسمت سوم ترتیب دو کار را روشن می‌کند."),
        ],
        mistakes=[
            ("Walking home, the rain started.",
             "Walking home, I got caught in the rain.",
             "the rain cannot walk; the participle has to share the subject of the "
             "main clause.",
             "باران نمی‌تواند راه برود؛ فاعل هر دو باید یکی باشد.",
             "dangling participle"),
            ("Having finished the report, the bed looked good.",
             "Having finished the report, she went to bed.",
             "the bed did not finish the report — the same subject rule again.",
             "تخت گزارش را تمام نکرده؛ همان قاعدهٔ فاعل مشترک.",
             "dangling participle"),
        ],
    ),
}
