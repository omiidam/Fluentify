"""A2-B1 pages, part three: adverbs ... conditionals."""

P = {
    "adverbs": dict(
        scene=(
            "She sings beautifully and drives badly. She works carefully when "
            "someone is watching, and answers questions honestly when nobody is.",
            "او زیبا می‌خواند و بد رانندگی می‌کند. وقتی کسی نگاهش می‌کند با دقت کار "
            "می‌کند و وقتی کسی نیست صادقانه جواب می‌دهد.",
        ),
        pairs=[
            ("او سریع می‌دود.",
             "She runs fastly.",
             "She runs fast.",
             "fast is both adjective and adverb; -ly would turn it into a word "
             "nobody says.",
             "fast هم صفت است هم قید؛ fastly ساختهٔ ذهن ماست، نه انگلیسی."),
            ("او همیشه دیر می‌آید.",
             "She comes always late.",
             "She always comes late.",
             "frequency adverbs sit before the main verb and after be.",
             "قید تکرار قبل از فعل اصلی و بعد از be می‌آید."),
        ],
        mistakes=[
            ("He drives very carefully and slow.",
             "He drives very carefully and slowly.",
             "an adverb modifying a verb needs its own -ly form; slow is the "
             "adjective.",
             "قید برای فعل باید پسوند ly بگیرد؛ slow صفت است.",
             "adverb form"),
            ("I studied very hardly for the exam.",
             "I studied very hard for the exam.",
             "hard is its own adverb; hardly means almost not at all, which is "
             "the opposite of what the sentence is trying to say.",
             "hard خودش قید است؛ hardly یعنی «تقریباً هرگز» و معنای جمله را برعکس می‌کند.",
             "adverb meaning"),
        ],
    ),
    "prepositions_time_place": dict(
        scene=(
            "The train leaves on Friday at 6:15 in the morning. The ticket is in my "
            "coat pocket, and the coat is on the chair by the door.",
            "قطار جمعه ساعت ۶:۱۵ صبح حرکت می‌کند. بلیت در جیب کتم است و کت روی "
            "صندلی کنار در.",
        ),
        pairs=[
            ("جمعه می‌بینمت.",
             "I will see you in Friday.",
             "I will see you on Friday.",
             "days and dates take on; in is for months, years and longer stretches.",
             "روزها و تاریخ‌ها on می‌گیرند؛ in برای ماه و سال است."),
            ("شب می‌رسیم.",
             "We arrive in the night.",
             "We arrive at night.",
             "at night, at noon and at midnight are fixed phrases; in the night "
             "means during one particular night.",
             "at night عبارت ثابت است؛ in the night یعنی در همان شبِ خاص."),
        ],
        mistakes=[
            ("I will call you in Monday.",
             "I will call you on Monday.",
             "a day is a point on the calendar, and points take on.",
             "روز یک نقطه در تقویم است و نقطه on می‌گیرد.",
             "preposition choice"),
            ("We arrived to the airport at 6.",
             "We arrived at the airport at 6.",
             "arrive takes at for a building and in for a city or country, never "
             "to.",
             "arrive با at (مکان) و in (شهر و کشور) می‌آید، هرگز to.",
             "preposition choice"),
        ],
    ),
    "countable_uncountable": dict(
        scene=(
            "There is not much milk left and only a few eggs. There is plenty of "
            "rice, though, and a little cheese for the morning.",
            "شیر زیادی نمانده و فقط چند تخم‌مرغ هست. ولی برنج فراوان است و کمی پنیر "
            "هم برای صبح.",
        ),
        pairs=[
            ("چند تا کتاب داری؟",
             "How much books do you have?",
             "How many books do you have?",
             "much is for what cannot be counted; books is counted, so it takes "
             "many.",
             "much برای غیرقابل‌شمارش است؛ کتاب شمردنی است و many می‌گیرد."),
            ("اطلاعات زیادی دارد.",
             "It has many informations.",
             "It has a lot of information.",
             "information has no plural and no many; a lot of works for both kinds.",
             "information جمع ندارد؛ a lot of برای هر دو نوع می‌آید."),
        ],
        mistakes=[
            ("I need some advices about this.",
             "I need some advice about this.",
             "advice is uncountable, so it stays singular even after some.",
             "advice غیرقابل‌شمارش است و بعد از some هم مفرد می‌ماند.",
             "countability"),
            ("There are much people in the street.",
             "There are a lot of people in the street.",
             "people is countable and plural, so much cannot describe it.",
             "people شمردنی و جمع است؛ much نمی‌گیرد.",
             "countability"),
        ],
    ),
    "determiners_some_any": dict(
        scene=(
            "«Would you like some tea?» «No thanks, I don't want any.» There is no "
            "sugar left anyway, and every cup in the house is dirty.",
            "«چای میل داری؟» «نه ممنون، هیچ نمی‌خواهم.» هر حالا شکر هم نمانده و هر "
            "فنجانی در خانه کثیف است.",
        ),
        pairs=[
            ("چیزی برای خوردن هست؟",
             "Is there something to eat?",
             "Is there anything to eat?",
             "a question normally takes any; something is kept for offers and for "
             "questions you expect a yes to.",
             "در سؤال معمولاً any می‌آید؛ something برای تعارف است."),
            ("هیچ‌کس خانه نیست.",
             "Anybody isn't at home.",
             "Nobody is at home.",
             "English does not put not before any-words; it makes the subject "
             "nobody and keeps the verb positive.",
             "انگلیسی not را با any نمی‌آورد؛ فاعل nobody می‌شود و فعل مثبت می‌ماند."),
        ],
        mistakes=[
            ("I don't have no money.",
             "I don't have any money.",
             "two negatives cancel in English; the second one has to become any.",
             "در انگلیسی دو منفی همدیگر را خنثی می‌کنند؛ دومی any می‌شود.",
             "double negative"),
            ("Every students passed the exam.",
             "Every student passed the exam.",
             "every is followed by a singular noun, whatever the size of the group.",
             "بعد از every اسم مفرد می‌آید.",
             "determiner form"),
        ],
    ),
    "question_tags": dict(
        scene=(
            "«You're coming with us, aren't you?» «I told you about it, didn't I?» "
            "He asks twice, and she answers both times without looking up.",
            "«تو هم با ما می‌آیی، نه؟» «درباره‌اش بهت گفتم، نه؟» دو بار می‌پرسد و "
            "سارا هر دو بار بی‌آنکه سر بلند کند جواب می‌دهد.",
        ),
        pairs=[
            ("تو دانشجویی، نه؟",
             "You are a student, no?",
             "You are a student, aren't you?",
             "English repeats the auxiliary in the tag and flips its sign; «نه» has "
             "no single-word equivalent here.",
             "انگلیسی کمکی را در تگ تکرار می‌کند و علامتش را برمی‌گرداند؛ «نه» معادل تک‌واژه ندارد."),
            ("بریم، نه؟",
             "Let's go, no?",
             "Let's go, shall we?",
             "let's is fixed: its tag is shall we, never don't we.",
             "تگ let's همیشه shall we است، نه don't we."),
        ],
        mistakes=[
            ("She doesn't like coffee, doesn't she?",
             "She doesn't like coffee, does she?",
             "a negative sentence takes a positive tag; the tag reverses the sign.",
             "جملهٔ منفی تگ مثبت می‌گیرد.",
             "tag form"),
            ("You are Iranian, isn't it?",
             "You are Iranian, aren't you?",
             "the tag copies the subject and the auxiliary of the sentence, not a "
             "neutral it.",
             "تگ فاعل و فعل کمکی همان جمله را تکرار می‌کند، نه it."),
        ],
    ),
    "present_perfect": dict(
        scene=(
            "I have finished my homework, but I haven't started the essay. I have "
            "been to Tehran three times, and I have never seen the tower.",
            "تکالیفم را تمام کرده‌ام، ولی انشا را شروع نکرده‌ام. سه بار تهران "
            "بوده‌ام و هرگز برج را ندیده‌ام.",
        ),
        pairs=[
            ("دیروز کارم را تمام کردم.",
             "I have finished my work yesterday.",
             "I finished my work yesterday.",
             "a named past time closes the door on the present perfect; yesterday "
             "belongs to the simple past.",
             "زمان گذشتهٔ مشخص با حال کامل نمی‌آید؛ yesterday مال گذشتهٔ ساده است."),
            ("سه سال است اینجا کار می‌کنم.",
             "I am working here since three years.",
             "I have worked here for three years.",
             "a situation that began in the past and continues takes the present "
             "perfect, with for for a length and since for a point.",
             "وضعیتی که از گذشته شروع شده و ادامه دارد حال کامل می‌گیرد."),
        ],
        mistakes=[
            ("I have seen him last week.",
             "I saw him last week.",
             "last week names the time, so the tense has to be the simple past.",
             "last week زمان را نام می‌برد، پس گذشتهٔ ساده لازم است.",
             "present perfect time"),
            ("She has went to the market.",
             "She has gone to the market.",
             "the perfect takes the past participle: go, went, gone.",
             "حال کامل اسم مفعول می‌خواهد: go, went, gone.",
             "participle form"),
        ],
    ),
    "present_perfect_continuous": dict(
        scene=(
            "I have been studying since eight this morning. The pages have been "
            "piling up for a week, and my eyes have been aching since noon.",
            "از ساعت هشت صبح درس می‌خوانم. یک هفته است کاغذها روی هم تلنبار می‌شوند "
            "و از ظهر چشمم درد می‌کند.",
        ),
        pairs=[
            ("دو ساعت است منتظرت هستم.",
             "I am waiting for you since two hours.",
             "I have been waiting for you for two hours.",
             "an activity still running from a past start takes have been + -ing.",
             "کاری که از گذشته شروع شده و هنوز ادامه دارد have been + ing می‌گیرد."),
            ("سه بار این فیلم را دیده‌ام.",
             "I have been seeing this film three times.",
             "I have seen this film three times.",
             "a finished count of events takes the present perfect, not the "
             "continuous, which would say the activity is still going on.",
             "شمارش کاملِ تکرارها حال کامل می‌گیرد، نه استمراری."),
        ],
        mistakes=[
            ("I have been knowing her for years.",
             "I have known her for years.",
             "know is a state, so it takes the perfect and never the continuous.",
             "know حالت است و استمراری نمی‌شود.",
             "stative verb"),
            ("She has been work here since March.",
             "She has been working here since March.",
             "after been the verb needs -ing; been work is two verbs with no link.",
             "بعد از been فعل ing می‌گیرد.",
             "progressive form"),
        ],
    ),
    "conditionals": dict(
        scene=(
            "If you heat ice, it melts. If it rains tomorrow, we will stay in. If I "
            "had more time, I would learn the guitar.",
            "اگر یخ را گرم کنی، آب می‌شود. اگر فردا باران بیاید، خانه می‌مانیم. اگر "
            "وقت بیشتری داشتم، گیتار یاد می‌گرفتم.",
        ),
        pairs=[
            ("اگر فردا باران بیاید، نمی‌روم.",
             "If it will rain tomorrow, I don't go.",
             "If it rains tomorrow, I won't go.",
             "the if-clause takes the present even when it points at tomorrow, and "
             "the result carries the future.",
             "شرطِ if حتی برای فردا حال می‌گیرد؛ آینده در جملهٔ اصلی می‌نشیند."),
            ("اگر جای تو بودم، قبول می‌کردم.",
             "If I was you, I will accept.",
             "If I were you, I would accept.",
             "an unreal present takes were and would, and never will.",
             "شرط خلاف واقع were و would می‌گیرد، هرگز will."),
        ],
        mistakes=[
            ("If I would have money, I would travel.",
             "If I had money, I would travel.",
             "would never appears in the if-clause; the past form does the "
             "unreality.",
             "would در جملهٔ if نمی‌آید؛ شکل گذشته کار را می‌کند.",
             "conditional form"),
            ("If he studied, he will pass.",
             "If he studied, he would pass.",
             "the two halves of a conditional belong to the same type: past with "
             "would, present with will.",
             "دو نیمهٔ جملهٔ شرطی باید از یک نوع باشند.",
             "conditional form"),
        ],
    ),
}
