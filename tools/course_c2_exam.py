#!/usr/bin/env python3
"""The C2 final examination: 33 marks over six sections.

Same architecture as the papers below it — six sections in skill order, one
mark per item, passages counted through their questions — with items that need
C2 control: inverted conditionals, clefts, hedging frames, attribution,
understatement, euphemism and the vocabulary of argument.
"""

from course_kit import exam, listen, mcq, reading_item, say, section, write

BLURB = (
    "Six skills, each marked on its own. Grammar, vocabulary, reading and "
    "listening are marked from your answers; writing is marked against a "
    "rubric; speaking is marked from what this device hears you say. You need "
    "60% overall, at least 50% in every skill, and all six skills must be "
    "assessed.",
    "شش مهارت، هر یک جداگانه. گرامر، واژگان، خواندن و شنیدن از پاسخ‌ها نمره "
    "می‌گیرند؛ نوشتن با معیارهای مشخص و گفتن از آنچه دستگاه می‌شنود. برای "
    "قبولی ۶۰٪ کل و ۵۰٪ در هر مهارت لازم است و هر شش مهارت باید سنجیده شود.",
)

GRAMMAR = [
    mcq("___ the review been published earlier, the error would have been "
        "caught.", "اگر بازبینی زودتر منتشر شده بود، خطا گرفته می‌شد.",
        ["If", "Had", "Should", "Were"], 1,
        "A past unreal condition inverted: had + participle, no if.",
        "شرط غیرواقعی گذشته به‌صورت جابه‌جاشده: had + اسم مفعول، بدون if."),
    mcq("Rarely ___ a committee reversed its own decision within a week.",
        "به‌ندرت پیش آمده کمیته‌ای تصمیم خود را در یک هفته برگرداند.",
        ["a committee has", "has a committee", "a committee had",
         "did a committee has"], 1,
        "Fronted 'rarely' requires inversion of auxiliary and subject.",
        "«rarely» در آغاز، جابه‌جایی کمکی و نهاد را می‌خواهد."),
    mcq("___ matters is not the number but the method behind it.",
        "آنچه مهم است عدد نیست، روشِ پشت آن است.",
        ["That", "What", "Which", "It"], 1,
        "A wh-cleft begins with 'what' and takes a singular verb.",
        "wh-cleft با «what» آغاز می‌شود و فعل مفرد می‌گیرد."),
    mcq("Not until the figures were audited ___ the scale of the error.",
        "تا وقتی ارقام حسابرسی نشدند، کسی اندازهٔ خطا را نفهمید.",
        ["anyone realised", "did anyone realise", "anyone did realise",
         "realised anyone"], 1,
        "Fronted 'not until' forces inversion in the main clause.",
        "«not until» در آغاز، جابه‌جایی در بند اصلی را الزام می‌کند."),
    mcq("The results ___ to support the earlier study, though the sample is "
        "small.", "به نظر می‌رسد نتایج مطالعهٔ پیشین را تأیید می‌کنند، هرچند "
        "نمونه کوچک است.",
        ["would appear", "appear would", "are appeared", "appearing"], 0,
        "A hedged evidential frame: would appear to + infinitive.",
        "ساخت شاهدمحور محتاط: would appear to + مصدر."),
    mcq("'Will the policy be reviewed?' 'I am afraid ___ .'",
        "«سیاست بازبینی می‌شود؟» «متأسفانه ___ .»",
        ["no", "not", "it not", "don't"], 1,
        "Ellipsis after 'I am afraid': not stands for the whole clause.",
        "حذف پس از «I am afraid»: not جانشین کل بند است."),
    mcq("The company ___ to have known about the fault for two years.",
        "گفته می‌شود شرکت دو سال از نقص خبر داشته است.",
        ["reports", "is reported", "reporting", "has reported"], 1,
        "A reporting passive keeps the writer at a distance.",
        "مجهولِ نقل، نویسنده را دور نگه می‌دارد."),
    mcq("Under no circumstances ___ the data be shared before publication.",
        "تحت هیچ شرایطی نباید داده پیش از انتشار به اشتراک گذاشته شود.",
        ["should", "it should", "should it", "it must"], 0,
        "Negative fronting inverts modal and subject: should the data be.",
        "آغاز منفی، وجه و نهاد را جابه‌جا می‌کند: should the data be."),
]

VOCABULARY = [
    mcq("The review does not ___ the theory; it narrows its scope.",
        "نقد نظریه را ___ نمی‌کند؛ دامنه‌اش را محدود می‌کند.",
        ["refute", "rebut", "concede", "qualify"], 0,
        "Refute means prove false, which the sentence denies.",
        "refute یعنی اثبات نادرستی، که جمله آن را رد می‌کند."),
    mcq("Her support for the plan was ___ : she backed it only if the "
        "budget held.", "حمایتش از طرح ___ بود: تنها در صورت ثبات بودجه "
        "پشتیبانی کرد.",
        ["unqualified", "qualified", "reluctant", "implicit"], 1,
        "Support with conditions is qualified support.",
        "حمایت مشروط، حمایت qualified است."),
    mcq("'A period of repositioning' for job losses is a ___.",
        "«دورهٔ بازآرایی» برای از دست رفتن شغل‌ها یک ___ است.",
        ["litotes", "euphemism", "innuendo", "hyperbole"], 1,
        "A gentler word replaces a harsher one.",
        "واژه‌ای ملایم‌تر جای واژه‌ای خشن‌تر می‌نشیند."),
    mcq("He never accused anyone; the ___ was enough.",
        "او هرگز کسی را متهم نکرد؛ همین ___ کافی بود.",
        ["innuendo", "irony", "cliché", "register"], 0,
        "Innuendo invites the conclusion without stating it.",
        "innuendo نتیجه را می‌طلبد بی‌آنکه بگوید."),
    mcq("There has been a marked ___ in complaints since March.",
        "از مارس افزایش چشمگیری در شکایت‌ها بوده است.",
        ["increase", "raise", "growth of", "rise of"], 0,
        "A marked increase in + the thing counted.",
        "a marked increase in + چیزی که شمرده می‌شود."),
    mcq("The measures were introduced to ___ the worst effects of the "
        "shortage.", "این اقدام‌ها برای ___ بدترین اثرهای کمبود معرفی شدند.",
        ["mitigate", "aggravate", "provoke", "forgo"], 0,
        "Mitigate means make less severe.",
        "mitigate یعنی کم‌شدن شدت."),
    mcq("A ___ chair has no personal stake; an uninterested one is bored.",
        "رئیس ___ نفعی ندارد و رئیس بی‌حوصله خسته است.",
        ["disinterested", "uninterested", "dispassionate", "indifferent"],
        0, "Disinterested is impartiality, not indifference.",
        "disinterested بی‌طرفی است نه بی‌اعتنایی."),
    mcq("The report's ___ purpose was transparency; its effect was to bury "
        "the finding.", "هدف ___ گزارش شفافیت بود؛ اثرش دفن یافته بود.",
        ["ostensible", "comprehensive", "provisional", "conclusive"], 0,
        "Ostensible marks a stated purpose the writer doubts.",
        "ostensible هدفی اعلام‌شده را نشان می‌دهد که نویسنده در آن تردید "
        "دارد."),
]

READING = [
    reading_item(
        ("The myth of the finished speaker",
         "افسانهٔ گویندهٔ تمام‌شده"),
        ("Every language classroom contains at least one student who believes "
         "that somewhere there is a person who speaks the language perfectly, "
         "and that this person is the standard against which they will be "
         "measured. The belief is rarely stated and never examined, and it "
         "does a great deal of harm, because the standard does not exist.\n\n"
         "What exists is a range of competences distributed unevenly across "
         "people who use the language daily. A translator may write "
         "exquisitely and hesitate in a noisy restaurant. A comedian may hold "
         "a room for an hour and be unable to draft a formal letter. Native "
         "speakers make errors of agreement, drop syllables, change "
         "constructions mid-sentence and misunderstand each other constantly, "
         "and none of this is treated as evidence that they cannot speak "
         "their own language.\n\n"
         "The myth survives because it is useful to institutions. A standard "
         "that nobody meets is a standard that can always be sold: another "
         "course, another certificate, another level above the one you have "
         "just completed. It survives, too, because it flatters those who "
         "have stopped studying. If perfection is unreachable, then the "
         "person who stopped ten years ago has lost nothing by stopping.\n\n"
         "The alternative is not lower standards but better ones: a standard "
         "defined by what you can do in a situation rather than by how close "
         "you come to an imaginary speaker. Can you apologise in a way that "
         "repairs something? Can you disagree with a senior colleague and "
         "keep the relationship? Can you read a contract and know which "
         "clause to ask about? These are finishable, and finishing them "
         "teaches you what the myth never does: that competence is a set of "
         "specific things, most of which you can acquire, and none of which "
         "requires you to become someone else.",
         "در هر کلاس زبانی حداقل یک زبان‌آموز هست که باور دارد جایی کسی "
         "هست که زبان را کامل حرف می‌زند و همان شخص معیاری است که او با آن "
         "سنجیده می‌شود. این باور به‌ندرت گفته و هرگز بررسی نمی‌شود و زیان "
         "بسیاری می‌زند، چون آن معیار وجود ندارد.\n\n"
         "آنچه وجود دارد طیفی از توانایی‌هاست که میان کسانی که روزانه زبان را "
         "به کار می‌برند نایکنواخت پخش شده. مترجمی ممکن است عالی بنویسد و در "
         "رستورانی پرصدا تعلل کند. کمدینی ممکن است یک ساعت سالن را نگه دارد "
         "و از نوشتن نامهٔ رسمی برنیاید. گویشوران بومی خطای مطابقت می‌کنند، "
         "هجا می‌اندازند، ساخت را وسط جمله عوض می‌کنند و مدام همدیگر را "
         "نمی‌فهمند، و هیچ‌کدام شاهدی بر ناتوانی‌شان در زبان خودشان دانسته "
         "نمی‌شود.\n\n"
         "افسانه می‌ماند چون برای نهادها سودمند است. معیاری که هیچ‌کس به آن "
         "نمی‌رسد معیاری است که همیشه قابل فروش است: دورهٔ دیگر، گواهی دیگر، "
         "سطحی بالاتر از سطحی که همین حالا تمام کردی. همچنین می‌ماند چون "
         "کسانی را که درس را رها کرده‌اند نوازش می‌کند. اگر کمال دست‌نیافتنی "
         "است، کسی که ده سال پیش رها کرده چیزی از دست نداده.\n\n"
         "جای‌گزینش معیارهای پایین‌تر نیست، معیارهای بهتر است: معیاری که با "
         "کاری که در موقعیتی می‌توانی بکنی تعریف شود، نه با نزدیکی‌ات به "
         "گوینده‌ای خیالی. می‌توانی چنان عذرخواهی کنی که چیزی را ترمیم کند؟ "
         "می‌توانی با همکاری ارشد مخالفت کنی و رابطه را نگه داری؟ می‌توانی "
         "قراردادی را بخوانی و بدانی از کدام بند باید بپرسی؟ این‌ها تمام‌شدنی "
         "اند و تمام کردنشان چیزی را یادت می‌دهد که افسانه هرگز نمی‌دهد: "
         "توانایی مجموعه‌ای از چیزهای مشخص است، بیشترشان قابل کسب، و هیچ‌کدام "
         "نمی‌خواهد کس دیگری شوی."),
        [
            mcq("What is the author's attitude to the 'perfect speaker'?",
                "نگرش نویسنده به «گویندهٔ کامل» چیست؟",
                ["it is a useful goal", "it does not exist and causes harm",
                 "it describes native speakers", "it is achievable with "
                 "study"], 1,
                "The standard is called non-existent and harmful in the first "
                "paragraph.", "در بند اول این معیار ناموجود و زیان‌بار خوانده "
                "می‌شود."),
            mcq("Why does the myth survive, according to the text?",
                "به گفتهٔ متن چرا این افسانه می‌ماند؟",
                ["because learners demand it", "because it is useful to "
                 "institutions and flatters those who stopped",
                 "because it is accurate", "because teachers invented it"],
                1, "Both reasons are given in the third paragraph.",
                "هر دو دلیل در بند سوم آمده است."),
            mcq("The proposed alternative standard is based on ___.",
                "معیار جای‌گزین پیشنهادی بر ___ استوار است.",
                ["native-speaker pronunciation", "situations and what you "
                 "can do in them", "certificates", "grammatical accuracy"],
                1, "The final paragraph lists finishable situational "
                "abilities.", "بند آخر توانایی‌های موقعیتی قابل‌اتمام را "
                "فهرست می‌کند."),
        ],
    ),
    reading_item(
        ("The label beside the object",
         "برچسب کنار شیء"),
        ("The museum label is a small literary form with an unusually strict "
         "brief: it must make an object legible to someone who has walked in "
         "from the rain with no preparation, and it must not lie. Between "
         "those two demands there is very little room, and the history of "
         "museum text is largely the history of choosing which demand to "
         "betray.\n\n"
         "The older labels betrayed legibility. They assumed a visitor who "
         "knew the dynasty, the material and the trade route, and they "
         "offered dates and dimensions as if the object explained itself. The "
         "contemporary label betrays something else: it tells a story, "
         "usually of the people who made the object rather than of the person "
         "who acquired it, and in telling that story it often asserts more "
         "than the evidence carries. 'Made by a workshop in the third "
         "century' is a description. 'Made by a community whose skills were "
         "undervalued' is a claim, and a good one, but it is not visible in "
         "the object.\n\n"
         "The honest label does three things, and the third is the one "
         "curators resist. It says what the object is, as far as anyone "
         "knows; it says what is disputed, in words a visitor can follow; and "
         "it says how it came to be here. That last sentence is "
         "uncomfortable because it is often the only part of the label that "
         "is fully documented, and the documentation rarely reflects well on "
         "the institution displaying it.\n\n"
         "None of this is an argument for returning to the label that assumed "
         "a specialist. A museum that requires expertise to be understood has "
         "decided, in advance, who is welcome. The argument is that "
         "legibility and honesty are not in competition as long as the label "
         "is willing to say which is which: this is what we know, this is "
         "what we think, and this is what we would rather not discuss.",
         "برچسب موزه فرم ادبی کوچکی است با وظیفه‌ای به‌طور غیرعادی سخت: باید "
         "شیء را برای کسی که از باران وارد شده و آماده نیست خوانا کند و "
         "نباید دروغ بگوید. میان این دو خواسته جای بسیار کمی هست و تاریخ "
         "متن موزه عمدتاً تاریخ انتخاب این است که کدام خواسته فدا شود.\n\n"
         "برچسب‌های قدیمی‌تر خوانایی را فدا می‌کردند. بازدیدکننده‌ای را فرض "
         "می‌کردند که سلسله، جنس و مسیر تجاری را می‌شناسد و تاریخ و ابعاد را "
         "چنان می‌دادند که گویی شیء خودش را توضیح می‌دهد. برچسب امروزی چیز "
         "دیگری را فدا می‌کند: داستانی می‌گوید، معمولاً از سازندگان شیء نه از "
         "خریدارش، و در گفتن آن داستان اغلب بیش از آنچه شاهد حمل می‌کند ادعا "
         "می‌کند. «ساختهٔ کارگاهی در سدهٔ سوم» توصیف است. «ساختهٔ جامعه‌ای که "
         "مهارت‌هایش کم‌ارزش گرفته می‌شد» ادعاست، و ادعای خوبی است، ولی در "
         "شیء دیده نمی‌شود.\n\n"
         "برچسب صادق سه کار می‌کند و سومی همان است که متصدیان در برابرش "
         "مقاومت می‌کنند. می‌گوید شیء چیست، تا آنجا که کسی می‌داند؛ می‌گوید "
         "چه چیزی محل اختلاف است، با واژه‌هایی که بازدیدکننده بفهمد؛ و می‌گوید "
         "چگونه به اینجا رسیده. جملهٔ آخر ناخوشایند است چون اغلب تنها بخشی "
         "از برچسب است که کامل مستند شده و مستندات به‌ندرت به سود نهادی است "
         "که آن را نمایش می‌دهد.\n\n"
         "هیچ‌کدام از این‌ها استدلال برای بازگشت به برچسبی نیست که متخصص را "
         "فرض می‌کرد. موزه‌ای که برای فهمیده شدن تخصص می‌خواهد از پیش تصمیم "
         "گرفته چه کسی خوش‌آمد است. استدلال این است که خوانایی و صداقت با هم "
         "نمی‌جنگند تا وقتی برچسب بپذیرد بگوید کدام کدام است: این را "
         "می‌دانیم، این را گمان می‌کنیم و این را ترجیح می‌دهیم درباره‌اش حرف "
         "نزنیم."),
        [
            mcq("The central tension in museum labels is between ___.",
                "کشمکش اصلی در برچسب‌های موزه میان ___ است.",
                ["length and cost", "legibility and honesty", "old and new "
                 "objects", "curators and visitors"], 1,
                "The opening paragraph sets up exactly those two demands.",
                "بند آغازین دقیقاً همین دو خواسته را می‌گذارد."),
            mcq("The example of the workshop label shows that contemporary "
                "labels sometimes ___.", "نمونهٔ برچسب کارگاه نشان می‌دهد "
                "برچسب‌های امروزی گاه ___.",
                ["avoid interpretation", "assert more than the object "
                 "supports", "use technical language", "omit the date"], 1,
                "The text contrasts a description with a claim not visible in "
                "the object.", "متن توصیف را از ادعایی که در شیء دیده نمی‌شود "
                "جدا می‌کند."),
            mcq("Why do curators resist the third element?",
                "چرا متصدیان در برابر عنصر سوم مقاومت می‌کنند؟",
                ["it is hard to write", "it is the best documented and least "
                 "flattering part", "visitors ignore it", "it is too short"],
                1, "Provenance is documented and rarely reflects well.",
                "منشأ مستند است و به‌ندرت خوش‌آیند."),
        ],
    ),
]

LISTENING = [
    listen("I am not going to defend the number. I am going to defend the "
           "direction: in every site where it was tried, waiting fell. The "
           "size of the fall is a different question.",
           "What does the speaker refuse to defend?",
           "گوینده از دفاع کردن از چه چیزی خودداری می‌کند؟",
           ["the direction of the effect", "the size of the effect",
            "the number of sites", "the pilot's cost"], 1,
           "The magnitude is explicitly set aside as a separate question.",
           "اندازه صریحاً پرسشی جدا خوانده می‌شود."),
    listen("People hear 'average wait: nine minutes' and think about their "
           "own worst afternoon, which was fifty. The average is true and it "
           "is not what they are asking.",
           "What is the speaker pointing out?",
           "گوینده به چه چیزی اشاره می‌کند؟",
           ["the figure is false", "a true summary can answer the wrong "
            "question", "nobody waits fifty minutes", "averages are useless"],
           1, "Accuracy and relevance are different virtues.",
           "دقت و مربوط بودن دو فضیلت متفاوت‌اند."),
    listen("The minister said the review had 'concluded'. She did not say it "
           "had concluded favourably, and she did not say it had concluded at "
           "all — the review is still open.",
           "What is the speaker suggesting about the minister?",
           "گوینده دربارهٔ وزیر چه القا می‌کند؟",
           ["she was misquoted", "she chose a word that implied more than was "
            "true", "she cancelled the review", "she was not informed"], 1,
           "The word carries an implication the facts do not support.",
           "واژه تلویحی می‌رساند که واقعیت‌ها پشتیبانی نمی‌کنند."),
    listen("Both accounts agree sixty people were there. They disagree about "
           "whether that number was the point. One counts it; the other asks "
           "what it was for.",
           "Where is the disagreement?",
           "اختلاف کجاست؟",
           ["the number of people", "the significance of the number",
            "the date", "the weather"], 1,
           "The count is shared; its meaning is contested.",
           "شمار مشترک است و معنایش محل اختلاف."),
    listen("I would rather say I do not have that figure than give you one I "
           "cannot stand behind in a month. Send me the question and I will "
           "have it by Thursday.",
           "What does the speaker prioritise?",
           "گوینده چه چیزی را در اولویت می‌گذارد؟",
           ["speed", "credibility", "politeness", "completeness"], 1,
           "A number they cannot defend would cost credibility.",
           "عددی که از آن دفاع نتوانند کرد اعتبار می‌سوزاند."),
    listen("The pilot worked. Whether the policy works is an empirical "
           "question, and the difference between those two sentences is the "
           "whole of my objection.",
           "What is the objection?",
           "اعتراض چیست؟",
           ["the pilot failed", "a pilot's success does not settle a "
            "policy's", "the policy is too expensive", "the data are "
            "missing"], 1,
           "Scale changes the question from fact to prediction.",
           "مقیاس پرسش را از واقعیت به پیش‌بینی می‌برد."),
]

WRITING = [
    write("Write about 160 words analysing how an opinion column persuades "
          "without stating its conclusion. Name two techniques, quote a short "
          "phrase for each, and say what each makes the reader do.",
          "حدود ۱۶۰ واژه تحلیل کن که یک ستون نظری چگونه بدون گفتن نتیجه "
          "اقناع می‌کند. دو شگرد را نام ببر، برای هرکدام عبارتی کوتاه نقل کن و "
          "بگو هر یک خواننده را به چه کاری وامی‌دارد.",
          160, ["although", "whereas"],
          "Two techniques, each with a quotation and an effect; no plot "
          "summary; a closing judgement about why the indirection works.",
          "دو شگرد، هرکدام با نقل و اثر؛ بدون خلاصهٔ محتوا؛ داوری پایانی "
          "دربارهٔ اینکه چرا غیرمستقیم گفتن کار می‌کند."),
    write("Write about 150 words of a proposal to a committee: your city "
          "should publish the waiting times of every public service. State the "
          "measure, the period, who publishes, and the strongest objection "
          "with your answer.",
          "حدود ۱۵۰ واژه از پیشنهادی به یک کمیته بنویس: شهر تو باید زمان "
          "انتظار هر خدمت عمومی را منتشر کند. سنجه، دوره، منتشرکننده و "
          "قوی‌ترین اعتراض را با پاسخش بیاور.",
          150, ["whereas", "although"],
          "Measure, period and publisher must be specific; the objection must "
          "be the best version of the other side, not a straw man.",
          "سنجه، دوره و منتشرکننده باید مشخص باشند؛ اعتراض باید بهترین نسخهٔ "
          "طرف مقابل باشد، نه آدم‌کاهی."),
]

SPEAKING = [
    say("What the report establishes is narrower than its title suggests: "
        "the effect is clear in the two sites studied and untested "
        "elsewhere.",
        "آنچه گزارش اثبات می‌کند از عنوانش باریک‌تر است: اثر در دو سایت "
        "مطالعه‌شده روشن است و جای دیگر آزموده نشده."),
    say("I would distinguish between the finding, which I accept, and the "
        "recommendation, which does not follow from it.",
        "بین یافته، که می‌پذیرم، و توصیه، که از آن بیرون نمی‌آید، تفکیک "
        "می‌کنم."),
    say("Had the second site been included, we would be arguing about a "
        "different number — which is precisely why it should be included "
        "next time.",
        "اگر سایت دوم هم بود، دربارهٔ عددی دیگر بحث می‌کردیم — و دقیقاً به همین "
        "دلیل باید بار بعد باشد."),
]

PAPER = exam(
    60, 0.6, 0.5, BLURB,
    [
        section("grammar", GRAMMAR),
        section("vocabulary", VOCABULARY),
        section("reading", READING),
        section("listening", LISTENING),
        section("writing", WRITING),
        section("speaking", SPEAKING),
    ],
)
