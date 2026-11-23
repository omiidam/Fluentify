"""B2-C1 pages, part five: modals_past ... causative_have_done."""

P = {
    "modals_past": dict(
        scene=(
            "You should have told me earlier. She must have missed the bus, because "
            "she is never late, and the light might have been off all morning.",
            "بهتر بود زودتر به من می‌گفتی. حتماً اتوبوس را از دست داده، چون هرگز دیر "
            "نمی‌رسد، و شاید چراغ تمام صبح خاموش بوده.",
        ),
        pairs=[
            ("بهتر بود بهم می‌گفتی.",
             "You had better told me.",
             "You should have told me.",
             "regret about the past is should have + V3; there is no past form of "
             "should on its own.",
             "پشیمانی از گذشته should have + قسمت سوم است."),
            ("حتماً خوابش برده بود.",
             "He must slept.",
             "He must have slept.",
             "a deduction about the past needs have between the modal and the "
             "third form.",
             "حدس دربارهٔ گذشته بین فعل کمکی و قسمت سوم have می‌آید."),
        ],
        mistakes=[
            ("She must have went home.",
             "She must have gone home.",
             "modal + have takes the third form: go, went, gone.",
             "بعد از must have قسمت سوم فعل می‌آید: gone.",
             "participle form"),
            ("You should have came earlier.",
             "You should have come earlier.",
             "come is irregular and its third form is come, not came.",
             "سومِ come همان come است، نه came.",
             "participle form"),
        ],
    ),
    "future_in_past": dict(
        scene=(
            "He said he would call me. He was going to study medicine, but the "
            "money ran out, and the plan quietly became something else.",
            "گفت زنگ می‌زند. می‌خواست پزشکی بخواند، ولی پول تمام شد و نقشه بی‌صدا "
            "چیز دیگری شد.",
        ),
        pairs=[
            ("گفت می‌آید.",
             "He said he will come.",
             "He said he would come.",
             "a future seen from a past moment is would, not will.",
             "آینده از دید یک لحظهٔ گذشته would می‌شود، نه will."),
            ("می‌خواستم زنگ بزنم ولی نشد.",
             "I would call you but I couldn't.",
             "I was going to call you but I couldn't.",
             "a real plan that was interrupted takes was going to; would call "
             "would promise it again.",
             "نقشه‌ای که نیمه‌کاره ماند was going to می‌گیرد."),
        ],
        mistakes=[
            ("He told me he will arrive at six.",
             "He told me he would arrive at six.",
             "the reporting verb is past, so the future inside moves to would.",
             "فعل گزارش گذشته است، پس آیندهٔ داخل آن would می‌شود.",
             "reported tense"),
            ("I was going to called you.",
             "I was going to call you.",
             "going to takes the base verb, never the past form.",
             "بعد از going to فعل پایه می‌آید.",
             "infinitive form"),
        ],
    ),
    "phrasal_verbs": dict(
        scene=(
            "Please turn off the lights before you go. I will look after the cat, "
            "and you can pick the keys up from the neighbour.",
            "لطفاً قبل از رفتن چراغ‌ها را خاموش کن. من مراقب گربه هستم و تو "
            "می‌توانی کلیدها را از همسایه بگیری.",
        ),
        pairs=[
            ("دنبال کلمه‌ای می‌گردم.",
             "I am looking the word for.",
             "I am looking for the word.",
             "the particle belongs to the verb and cannot be moved to the end "
             "when it is inseparable.",
             "در فعل‌های جدانشدنی حرف اضافه جای خودش می‌ماند."),
            ("چراغ را خاموش کن.",
             "Turn off it.",
             "Turn it off.",
             "when the object is a pronoun it must sit between the verb and a "
             "separable particle.",
             "اگر مفعول ضمیر باشد، بین فعل و حرف اضافه می‌نشیند."),
        ],
        mistakes=[
            ("I will look after it the cat.",
             "I will look after the cat.",
             "one object is enough, and after a pronoun no second object follows.",
             "یک مفعول کافی است؛ بعد از ضمیر مفعول دوم نمی‌آید.",
             "phrasal order"),
            ("She gave up it last year.",
             "She gave it up last year.",
             "with a pronoun the particle goes after it: give it up.",
             "با ضمیر، حرف اضافه بعد از آن می‌آید: give it up.",
             "phrasal order"),
        ],
    ),
    "wish_subjunctive": dict(
        scene=(
            "I wish I were taller. I wish I had taken that job, and if only the "
            "train had not been late.",
            "ای کاش قدبلندتر بودم. ای کاش آن کار را قبول کرده بودم و ای کاش قطار "
            "دیر نمی‌کرد.",
        ),
        pairs=[
            ("ای کاش پول بیشتری داشتم.",
             "I wish I have more money.",
             "I wish I had more money.",
             "a wish about now is written in the past: the past is how English "
             "says unreal.",
             "آرزوی حالا با گذشته نوشته می‌شود؛ گذشته نشانهٔ خلاف واقع بودن است."),
            ("ای کاش زودتر آمده بودم.",
             "I wish I came earlier.",
             "I wish I had come earlier.",
             "a regret about the past needs had + V3, not the simple past.",
             "حسرت گذشته had + قسمت سوم می‌خواهد، نه گذشتهٔ ساده."),
        ],
        mistakes=[
            ("I wish I was you.",
             "I wish I were you.",
             "after wish the verb be is were for every person.",
             "بعد از wish فعل be برای همهٔ شخص‌ها were است.",
             "subjunctive form"),
            ("I wish I would know the answer.",
             "I wish I knew the answer.",
             "would does not follow wish about yourself; the past form does.",
             "بعد از wish دربارهٔ خودت would نمی‌آید؛ شکل گذشته می‌آید.",
             "wish form"),
        ],
    ),
    "inversion": dict(
        scene=(
            "Never have I seen such a mess. Rarely does she complain, and not once "
            "did he apologise.",
            "هرگز چنین آشفتگی‌ای ندیده‌ام. به‌ندرت شکایت می‌کند و یک بار هم عذرخواهی "
            "نکرد.",
        ),
        pairs=[
            ("هرگز چنین چیزی ندیده‌ام.",
             "Never I have seen such a thing.",
             "Never have I seen such a thing.",
             "when never or rarely opens the sentence the auxiliary moves in front "
             "of the subject.",
             "وقتی never یا rarely آغاز جمله باشد، فعل کمکی قبل از فاعل می‌آید."),
            ("نه فقط دیر آمد، بلکه فراموش هم کرد.",
             "Not only he came late, but he also forgot.",
             "Not only did he come late, but he also forgot.",
             "not only in first position takes the inverted auxiliary as well.",
             "not only در آغاز جمله هم وارونگی می‌طلبد."),
        ],
        mistakes=[
            ("Rarely she goes out at night.",
             "Rarely does she go out at night.",
             "a negative adverb at the front forces do + subject + base verb.",
             "قید منفی در آغاز جمله do + فاعل + فعل پایه می‌خواهد.",
             "inversion form"),
            ("Never I will forget this.",
             "Never will I forget this.",
             "will moves in front of the subject, not stay behind it.",
             "will قبل از فاعل می‌آید.",
             "inversion form"),
        ],
    ),
    "cleft_sentences": dict(
        scene=(
            "What happened is that the file got corrupted. It was Sara who noticed, "
            "and it was the backup that saved the day.",
            "چیزی که اتفاق افتاد این بود که فایل خراب شد. سارا بود که متوجه شد و "
            "پشتیبان بود که روز را نجات داد.",
        ),
        pairs=[
            ("سارا بود که فایل را پیدا کرد.",
             "It was Sara who found the file.",
             "It was Sara who found the file.",
             "the cleft is built as it was + the person + who + the rest: the "
             "emphasis lands on Sara, and the fact stays in found.",
             "ساختار شکافته: it was + شخص + who + بقیهٔ جمله."),
            ("چیزی که مهم است زمان است.",
             "What is important it is time.",
             "What is important is time.",
             "what ... is takes one is, not two; the Persian «این است که» has no "
             "second pronoun.",
             "در ساختار what ... is فقط یک is می‌آید."),
        ],
        mistakes=[
            ("It was Sara which found the file.",
             "It was Sara who found the file.",
             "a person in a cleft takes who, not which.",
             "برای شخص در جملهٔ شکافته who می‌آید.",
             "cleft pronoun"),
            ("What I need is a coffee is.",
             "What I need is a coffee.",
             "the second half is a plain noun phrase; nothing else comes after it.",
             "نیمهٔ دوم جملهٔ شکافته عبارت اسمی ساده است.",
             "cleft form"),
        ],
    ),
    "mixed_conditionals": dict(
        scene=(
            "If I had taken that job, I would be living in Berlin now. If she were "
            "more patient, she would not have left the course in March.",
            "اگر آن کار را قبول کرده بودم، الان در برلین زندگی می‌کردم. اگر صبورتر "
            "بود، در اسفند دوره را رها نمی‌کرد.",
        ),
        pairs=[
            ("اگر آن کار را گرفته بودم، الان اینجا نبودم.",
             "If I took that job, I am not here now.",
             "If I had taken that job, I wouldn't be here now.",
             "a past cause with a present result mixes had + V3 with would + base: "
             "each half keeps its own time.",
             "علت در گذشته و نتیجه در حال: هر نیمه زمان خودش را دارد."),
            ("اگر مریض نبودم، دیروز می‌آمدم.",
             "If I am not sick, I came yesterday.",
             "If I weren't sick, I would have come yesterday.",
             "a present condition with a past result takes were + would have + V3.",
             "شرط در حال و نتیجه در گذشته: were + would have + قسمت سوم."),
        ],
        mistakes=[
            ("If I would have studied, I would pass now.",
             "If I had studied, I would pass now.",
             "the if-clause never takes would; had + V3 is what marks the "
             "unreal past.",
             "جملهٔ if هرگز would نمی‌گیرد؛ had + قسمت سوم گذشتهٔ خلاف واقع را می‌سازد.",
             "conditional form"),
            ("If he were taller, he would have join the team.",
             "If he were taller, he would have joined the team.",
             "would have takes the third form, not the base verb.",
             "بعد از would have قسمت سوم فعل می‌آید.",
             "participle form"),
        ],
    ),
    "causative_have_done": dict(
        scene=(
            "I need to have the car serviced before the trip. She had her hair cut "
            "on Thursday, and we are having the kitchen painted next month.",
            "قبل از سفر باید ماشین را سرویس کنم. پنجشنبه موهایش را کوتاه کرد و "
            "ماه بعد آشپزخانه را رنگ می‌کنیم.",
        ),
        pairs=[
            ("موهایم را کوتاه کردم.",
             "I cut my hair.",
             "I had my hair cut.",
             "the Persian sentence does not say who held the scissors; if it "
             "was the barber, English says have + object + V3.",
             "جملهٔ فارسی نمی‌گوید قیچی دست کی بوده؛ اگر آرایشگر بوده: have + مفعول + قسمت سوم."),
            ("ماشینم را تعمیر کردم.",
             "I repaired my car had.",
             "I had my car repaired.",
             "the object comes straight after have and the third form closes the "
             "phrase.",
             "مفعول بعد از have و قسمت سوم در پایان می‌آید."),
        ],
        mistakes=[
            ("I had cut my hair yesterday at the salon.",
             "I had my hair cut yesterday at the salon.",
             "without the object between have and the participle it says you cut "
             "it yourself.",
             "بی مفعول بین have و قسمت سوم، جمله می‌گوید خودت کوتاه کردی.",
             "causative form"),
            ("She had repaired her car by the mechanic.",
             "She had her car repaired by the mechanic.",
             "the thing being worked on goes between have and the participle, and "
             "by names the doer.",
             "چیزی که رویش کار می‌شود بین have و قسمت سوم می‌آید.",
             "causative form"),
        ],
    ),
}
