#!/usr/bin/env python3
"""B2 · units 7-8: emphasis, the environment, and the argument out loud.

Unit 7 turns a claim around for emphasis, then gives the vocabulary of the
environment the debate that follows needs. Unit 8 closes the level's grammar
with the non-finite verb forms — gerund, infinitive and participle, where the
choice changes the meaning — and pairs it with the language of psychology and
the arts before the final presentation.
"""

from course_kit import gap, lesson, mcq, unit, write

U7 = unit(
    "b2-u7",
    ("Never have I seen", "هرگز ندیده‌ام"),
    ("Emphasise with inversion, argue about the environment, and hold the floor in a debate.", "با جابه‌جایی تأکید کن، دربارهٔ محیط بحث کن و در مناظره نوبت را نگه دار."),
    [
        lesson(
            "b2-u7-l1",
            "grammar",
            ("Inversion after negative and limiting adverbials", "جابه‌جایی پس از قیدهای منفی و محدودکننده"),
            ("Front a limiting adverbial and invert the subject and auxiliary.", "قید محدودکننده را جلو بیاور و نهاد و فعل کمکی را جابه‌جا کن."),
            [
                ("When a negative or limiting adverbial starts the sentence, the auxiliary moves before the subject: Never have I seen such a thing. Rarely does she complain. Not only did he arrive late, but he also forgot the file.", "وقتی قید منفی یا محدودکننده آغاز جمله باشد، فعل کمکی پیش از نهاد می‌آید: Never have I seen such a thing. Rarely does she complain. Not only did he arrive late, but he also forgot the file."),
                ("The set is small and worth learning as a set: never, rarely, seldom, hardly, scarcely, barely, little, no sooner, not only, not until, at no time, under no circumstances, on no account, only then, only later, only when.", "مجموعه کوچک است و بهتر است به‌صورت مجموعه حفظ شود: never، rarely، seldom، hardly، scarcely، barely، little، no sooner، not only، not until، at no time، under no circumstances، on no account، only then، only later، only when."),
                ("If there is no auxiliary in the original, do-support supplies one: Rarely does she complain (not 'Rarely she complains'). With 'no sooner … than' and 'hardly … when', the first clause inverts and the second does not: No sooner had we sat down than the phone rang.", "اگر جمله فعل کمکی ندارد، do جای آن را می‌گیرد: Rarely does she complain (نه «Rarely she complains»). در «no sooner … than» و «hardly … when» بند اول جابه‌جا می‌شود و دوم نه: No sooner had we sat down than the phone rang."),
                ("Register matters: inversion belongs to formal writing, speeches and emphasis in narrative. In conversation the same meaning is carried by stress alone — 'I've never seen anything like it'. Using inversion in a chat message reads as ironic.", "لحن مهم است: جابه‌جایی به نوشتار رسمی، سخنرانی و تأکید روایی تعلق دارد. در گفت‌وگو همان معنا با تکیهٔ صدا حمل می‌شود — «I've never seen anything like it». استفاده از آن در پیام روزمره طنزآمیز خوانده می‌شود."),
            ],
            [
                ("Never have I read a clearer explanation.", "هرگز توضیحی روشن‌تر نخوانده‌ام."),
                ("Not only did they finish early, they also checked the figures.", "نه‌تنها زود تمام کردند، بلکه ارقام را هم بررسی کردند."),
                ("Hardly had the meeting started when the power failed.", "تازه جلسه شروع شده بود که برق رفت."),
                ("Under no circumstances should this file leave the office.", "تحت هیچ شرایطی این پرونده نباید از دفتر بیرون برود."),
                ("Only later did we understand what she had meant.", "فقط بعدتر فهمیدیم منظورش چه بود."),
            ],
            [
                mcq("Rarely ___ such a generous offer.", "به‌ندرت ___ چنین پیشنهاد سخاوتمندانه‌ای.", ["we receive", "do we receive", "we do receive", "receive we"], 1,
                    "Fronted limiting adverb → auxiliary before subject.", "قید محدودکننده در آغاز ← کمکی پیش از نهاد."),
                mcq("No sooner ___ than it began to rain.", "تازه ___ که باران گرفت.", ["we had left", "had we left", "we left", "did we leave"], 1,
                    "No sooner + inverted past perfect + than.", "no sooner + ماضی بعید جابه‌جاشده + than."),
            ],
            [
                gap("Not only ___ she apologise, but she also paid for the damage.", ["did"], "Do-support for a fronted 'not only'.", "do برای «not only» در آغاز."),
                gap("Under no circumstances ___ you share this password.", ["should", "must"], "Modal before the subject.", "فعل وجهی پیش از نهاد."),
                mcq("Which is wrong?", "کدام نادرست است؟", ["Little did he know.", "Seldom have I seen it.", "Never I have been there.", "Only then did she speak."], 2,
                    "Inversion is obligatory after a fronted 'never'.", "پس از «never» در آغاز، جابه‌جایی اجباری است."),
                mcq("Which register does inversion suit least?", "جابه‌جایی با کدام لحن کمترین سازگاری را دارد؟", ["a formal report", "a speech", "a text message to a friend", "a literary narrative"], 2,
                    "It reads as ironic in casual messaging.", "در پیام روزمره طنزآمیز خوانده می‌شود."),
            ],
        ),
        lesson(
            "b2-u7-l2",
            "vocabulary",
            ("Environment, climate and sustainability", "محیط زیست، اقلیم و پایداری"),
            ("Argue about emissions, targets and trade-offs without borrowing someone else's slogans.", "دربارهٔ انتشار، هدف‌ها و بده‌بستان‌ها بی‌قرض گرفتن شعار دیگران بحث کن."),
            [
                ("The words of the problem: emissions, carbon footprint, greenhouse gas, fossil fuel, deforestation, pollution, waste, biodiversity, depletion, contamination. These are countable and uncountable in specific ways — emissions are plural, pollution is not — and getting that wrong is the first sign of a borrowed argument.", "واژه‌های مسئله: emissions، carbon footprint، greenhouse gas، fossil fuel، deforestation، pollution، waste، biodiversity، depletion، contamination. شمارش‌پذیری‌شان معین است — emissions جمع است و pollution غیرقابل‌شمارش — و اشتباه در آن نخستین نشانهٔ استدلال قرضی است."),
                ("The words of the response: mitigation (cutting the cause) and adaptation (living with the effect), renewable, sustainable, recyclable, biodegradable, energy-efficient, a levy, a subsidy, a target, a ban, a phase-out. Mitigation and adaptation are not synonyms; a policy is usually one or the other, and saying which one is the substance of a B2 argument.", "واژه‌های پاسخ: mitigation (کاهش علت) و adaptation (زندگی با اثر)، renewable، sustainable، recyclable، biodegradable، energy-efficient، levy، subsidy، target، ban، phase-out. mitigation و adaptation هم‌معنا نیستند؛ یک سیاست معمولاً یکی از این دو است و گفتن اینکه کدام، جان استدلال B2 است."),
                ("Collocations that carry the debate: to meet a target, to fall short of a commitment, to cut emissions by a third, to phase out coal, to invest in renewables, to offset the cost, to hold a company to account, to make a difference at the margins. 'Reduce' takes an amount; 'offset' means compensating for what remains.", "هم‌نشینی‌هایی که بحث را حمل می‌کنند: meet a target، fall short of a commitment، cut emissions by a third، phase out coal، invest in renewables، offset the cost، hold a company to account، make a difference at the margins. «reduce» مقدار می‌گیرد و «offset» یعنی جبران آنچه مانده."),
                ("The evaluative pair that keeps an argument honest: effective vs affordable, ambitious vs realistic, immediate vs gradual. Most environmental disagreement is not about facts but about which of these pairs takes priority — and a writer who names the trade-off is harder to argue with than one who does not.", "جفت ارزشی که استدلال را صادق نگه می‌دارد: effective در برابر affordable، ambitious در برابر realistic، immediate در برابر gradual. بیشتر اختلاف محیطی بر سر واقعیت‌ها نیست، بر سر این است که کدام جفت اولویت دارد — و نویسنده‌ای که بده‌بستان را نام می‌برد سخت‌تر رد می‌شود."),
            ],
            [
                ("The city cut its emissions by a fifth by phasing out diesel buses.", "شهر با کنار گذاشتن اتوبوس‌های دیزلی انتشارش را یک‌پنجم کم کرد."),
                ("Adaptation funding has lagged behind mitigation for a decade.", "بودجهٔ سازگاری یک دهه از بودجهٔ کاهش عقب مانده است."),
                ("The target is ambitious; whether it is affordable is another question.", "هدف جسورانه است؛ اینکه از عهدهٔ هزینه‌اش بربیاییم پرسش دیگری است."),
                ("Offsetting does not remove the emissions, it pays for them elsewhere.", "جبران انتشار را حذف نمی‌کند، بهایش را جای دیگری می‌پردازد."),
            ],
            [
                mcq("Which cuts the cause rather than coping with the effect?", "کدام علت را کم می‌کند، نه کنار آمدن با اثر؟", ["adaptation", "mitigation", "resilience", "recovery"], 1,
                    "Mitigation reduces emissions.", "mitigation انتشار را کم می‌کند."),
                mcq("To 'phase out' a fuel is to ___.", "«phase out» یک سوخت یعنی ___.", ["ban it immediately", "withdraw it gradually", "make it cheaper", "import more of it"], 1,
                    "A phase-out is a staged withdrawal.", "phase-out خروج مرحله‌ای است."),
            ],
            [
                gap("The country fell short ___ its own commitment.", ["of"], "The fixed form is 'fall short of'.", "شکل ثابت «fall short of» است."),
                gap("Cutting emissions is cheaper than ___ for them later.", ["offsetting", "paying"], "Offset emissions you cannot remove.", "offset برای انتشار غیرقابل‌حذف."),
                mcq("Which word is uncountable?", "کدام واژه غیرقابل‌شمارش است؟", ["emissions", "targets", "pollution", "subsidies"], 2,
                    "Pollution has no plural in this sense.", "pollution در این معنا جمع ندارد."),
                mcq("Which pair names the real trade-off?", "کدام جفت بده‌بستان واقعی را نام می‌برد؟", ["ambitious / unrealistic", "renewable / sustainable", "effective / affordable", "green / clean"], 2,
                    "What works against what can be paid for.", "آنچه کار می‌کند در برابر آنچه توان پرداختش هست."),
            ],
        ),
        lesson(
            "b2-u7-l3",
            "speaking",
            ("The debate: hold a position under pressure", "مناظره: موضع را زیر فشار نگه دار"),
            ("Argue a motion, concede one point, and respond to a challenge without repeating yourself.", "دربارهٔ یک موضوع استدلال کن، یک نکته را بپذیر و بی‌تکرار به چالش پاسخ بده."),
            [
                ("A debate turn has four moves and about ninety seconds: state the claim, give the mechanism (why it is true), give one piece of evidence, then pre-empt the obvious objection. Ninety seconds is short; one claim done well beats four done vaguely.", "نوبت مناظره چهار حرکت و حدود نود ثانیه دارد: ادعا را بگو، سازوکار (چرا درست است) را بگو، یک شاهد بیاور و بعد اعتراض آشکار را پیش‌دستی کن. نود ثانیه کوتاه است؛ یک ادعای خوب از چهار ادعای مبهم بهتر است."),
                ("Language for holding a position: the point I'm making is, that's precisely why, I'd go further, the evidence points the other way. Language for conceding without collapsing: that's a fair point, though it doesn't change the main issue; I'd accept the cost, but not the conclusion.", "زبان حفظ موضع: the point I'm making is، that's precisely why، I'd go further، the evidence points the other way. زبان پذیرش بدون فروپاشی: that's a fair point, though it doesn't change the main issue؛ I'd accept the cost, but not the conclusion."),
                ("Buying time is a skill, not a failure: let me put that another way, that deserves a proper answer, before I answer that, could I finish the point. What sounds fluent is not speed but the absence of panic.", "وقت خریدن یک مهارت است، نه شکست: let me put that another way، that deserves a proper answer، before I answer that، could I finish the point. آنچه روان به گوش می‌رسد سرعت نیست، نبودِ دستپاچگی است."),
                ("Interaction: signpost when you hand over ('I'll leave the numbers to Sara'), when you interrupt ('sorry to jump in, but that's the crux'), and when you close ('so, to sum up, the motion stands'). A speaker who never marks the turn leaves the listener guessing.", "تعامل: نشانه بده وقتی نوبت را می‌دهی («I'll leave the numbers to Sara»)، وقتی میان حرف می‌آیی («sorry to jump in, but that's the crux») و وقتی جمع می‌کنی («so, to sum up, the motion stands»). گوینده‌ای که نوبت را نشانه‌گذاری نکند، شنونده را سرگردان می‌گذارد."),
            ],
            [
                ("The point I'm making is that the ban moves the problem, not the traffic.", "نکتهٔ من این است که ممنوعیت مشکل را جابه‌جا می‌کند، نه ترافیک را."),
                ("That's a fair point, though it doesn't change the main issue.", "نکتهٔ درستی است، هرچند مسئلهٔ اصلی را عوض نمی‌کند."),
                ("Let me put that another way.", "بگذار جور دیگری بگویم."),
                ("So, to sum up, the motion stands.", "پس در جمع‌بندی، طرح پابرجاست."),
            ],
            [
                mcq("Which move should come second in a debate turn?", "کدام حرکت در نوبت مناظره دوم می‌آید؟", ["the evidence", "the mechanism", "the objection", "the conclusion"], 1,
                    "Claim, then why it is true, then evidence.", "ادعا، بعد چرایی، بعد شاهد."),
                mcq("Which phrase concedes without collapsing?", "کدام عبارت می‌پذیرد بی‌آنکه فروبپاشد؟", ["You're completely right, I was wrong.", "That's fair, but it doesn't change the main issue.", "I don't accept any of that.", "Let's agree to disagree."], 1,
                    "It grants the detail and keeps the claim.", "جزئیات را می‌پذیرد و ادعا را نگه می‌دارد."),
            ],
            [
                gap("Sorry to ___ in, but that's the crux of it.", ["jump"], "Jump in = interrupt.", "jump in یعنی میان حرف آمدن."),
                mcq("What marks the end of a turn?", "چه چیزی پایان نوبت را نشان می‌دهد؟", ["a new argument", "a summary sentence", "a question to yourself", "silence"], 1,
                    "Close explicitly so the listener knows.", "صریح ببند تا شنونده بداند."),
                write("Write the ninety-second turn you would deliver for the motion 'Cities should phase out private cars from the centre.' Claim, mechanism, one piece of evidence, one pre-empted objection.",
                      "نوبت نودثانیه‌ای خود را برای موضوع «شهرها باید خودروهای شخصی را از مرکز کنار بگذارند» بنویس. ادعا، سازوکار، یک شاهد و یک اعتراض پیش‌دستی‌شده.",
                      90, ["although"],
                      "Spoken register: contractions are fine, but keep the four moves visible.",
                      "لحن گفتاری: شکل کوتاه اشکالی ندارد، اما چهار حرکت را آشکار نگه دار."),
            ],
        ),
    ],
)

U8 = unit(
    "b2-u8",
    ("Remember doing, remember to do", "به یاد آوردن انجام، به یاد داشتن برای انجام"),
    ("Choose the non-finite form by meaning, compress with participles, and present a case.", "شکل غیرصرفی را بر پایهٔ معنا انتخاب کن، با وجه وصفی فشرده کن و موضوعی را ارائه بده."),
    [
        lesson(
            "b2-u8-l1",
            "grammar",
            ("Gerunds, infinitives and participle clauses", "gerund، infinitive و بندهای وجه وصفی"),
            ("Use the pairs that change meaning, and compress a clause into a phrase without losing its subject.", "جفت‌هایی را که معنا را عوض می‌کنند به کار ببر و بند را بی از دست دادن نهادش به عبارت فشرده کن."),
            [
                ("After remember, forget, stop, try, go on and regret, the choice is meaning, not grammar. Remember posting it = you recall the act. Remember to post it = you did not forget the duty. Stop smoking = quit. Stop to smoke = pause in order to smoke.", "پس از remember، forget، stop، try، go on و regret، انتخاب بر پایهٔ معناست نه دستور. remember posting it یعنی آن عمل را به یاد داری. remember to post it یعنی وظیفه را فراموش نکردی. stop smoking یعنی ترک کردن. stop to smoke یعنی برای سیگار کشیدن توقف کردن."),
                ("Try + -ing means experiment with a method; try + to do means attempt something difficult: try restarting it (test a solution) / try to lift it (attempt and maybe fail). Go on + -ing continues the same activity; go on + to do moves to the next one.", "try + ing یعنی روشی را آزمودن؛ try + to do یعنی تلاش برای کار سخت: try restarting it (راه‌حلی را آزمودن) / try to lift it (تلاش و شاید شکست). go on + ing همان فعالیت را ادامه می‌دهد و go on + to do به مورد بعدی می‌رود."),
                ("Some verbs take only the gerund: enjoy, avoid, mind, suggest, admit, deny, consider, involve, look forward to, be used to. Some take only the infinitive: decide, promise, refuse, manage, afford, fail, seem, tend. A handful take both with no change: begin, start, continue, prefer. After a preposition it is always the gerund.", "برخی فعل‌ها فقط gerund می‌گیرند: enjoy، avoid، mind، suggest، admit، deny، consider، involve، look forward to، be used to. برخی فقط infinitive: decide، promise، refuse، manage، afford، fail، seem، tend. چندتا هر دو را بی تغییر می‌گیرند: begin، start، continue، prefer. پس از حرف اضافه همیشه gerund."),
                ("A participle clause compresses a whole clause into a phrase: Having finished the report, she left; Written in 1520, the letter still reads clearly; Arriving early, he waited outside. The participle carries time, reason or result without naming it, and the reader infers the link from the content.", "بند وجه وصفی کل بند را به عبارت فشرده می‌کند: Having finished the report, she left؛ Written in 1520, the letter still reads clearly؛ Arriving early, he waited outside. وجه وصفی زمان، علت یا نتیجه را بی نام بردن حمل می‌کند و خواننده پیوند را از محتوا می‌فهمد."),
                ("The one rule that cannot be broken: the participle's subject must be the subject of the main clause. 'Walking home, the notice caught my eye' makes the notice walk. If the subjects differ, keep the full clause — a dangling participle is the error examiners recognise fastest at this level.", "تنها قاعدهٔ نشکستنی: نهاد وجه وصفی باید نهاد بند اصلی باشد. «Walking home, the notice caught my eye» باعث می‌شود تابلو راه برود. اگر نهادها متفاوت‌اند، بند کامل را نگه دار — وجه وصفی آویزان خطایی است که داور در این سطح زودتر از همه می‌شناسد."),
            ],
            [
                ("I'll never forget arriving in Tehran at dawn.", "هرگز رسیدن به تهران در سپیده‌دم را فراموش نمی‌کنم."),
                ("Don't forget to bring the receipt.", "فراموش نکن رسید را بیاوری."),
                ("She stopped to answer the phone, then went on explaining.", "برای پاسخ به تلفن ایستاد، بعد توضیح دادن را ادامه داد."),
                ("I'm not used to working with a team this large.", "به کار با تیمی این‌قدر بزرگ عادت ندارم."),
                ("Having read the file, she changed her mind.", "پس از خواندن پرونده، نظرش عوض شد."),
                ("Written in haste, the note was unclear.", "نامه که با شتاب نوشته شده بود، روشن نبود."),
            ],
            [
                mcq("Remember ___ the lights before you leave.", "یادت باشد پیش از رفتن چراغ‌ها را ___ .", ["turning off", "to turn off", "turn off", "turned off"], 1,
                    "A duty you must not forget: remember + to do.", "وظیفه‌ای که نباید فراموش شود: remember + to do."),
                mcq("Which sentence has a dangling participle?", "کدام جمله وجه وصفی آویزان دارد؟", ["Walking home, I lost my keys.", "Walking home, the keys were lost.", "Having walked home, I slept.", "Written quickly, the note was unclear."], 1,
                    "The keys did not walk home.", "کلیدها راهی خانه نشدند."),
            ],
            [
                gap("I'm looking forward to ___ (hear) from you.", ["hearing"], "Preposition + gerund.", "حرف اضافه + gerund."),
                gap("We managed ___ (finish) before the deadline.", ["to finish"], "Manage takes the infinitive.", "manage infinitive می‌گیرد."),
                gap("___ (finish) the exam, she checked every answer twice.", ["Having finished"], "Perfect participle for an earlier action.", "وجه وصفی کامل برای عمل پیشین."),
                mcq("'Try restarting the router' means ___.", "«Try restarting the router» یعنی ___.", ["attempt the impossible", "test this as a solution", "stop using the router", "remember to restart"], 1,
                    "Try + -ing tests a method.", "try + ing روشی را می‌آزماید."),
                mcq("Which verb cannot take the infinitive?", "کدام فعل infinitive نمی‌گیرد؟", ["decide", "avoid", "promise", "refuse"], 1,
                    "Avoid takes the gerund only.", "avoid فقط gerund می‌گیرد."),
            ],
        ),
        lesson(
            "b2-u8-l2",
            "vocabulary",
            ("Psychology, the arts and the words of evaluation", "روان‌شناسی، هنر و واژه‌های ارزش‌گذاری"),
            ("Describe a mind and judge a work with terms that can be checked.", "ذهن را توصیف کن و اثری را با واژه‌هایی بسنج که قابل بررسی‌اند."),
            [
                ("Psychology vocabulary: behaviour, a habit, a motive, an emotion, stress, anxiety, confidence, resilience, burnout, a bias, a coping strategy, a trigger. A motive is why someone acted; an emotion is what they felt; a bias is a systematic tilt in judgement, not an opinion.", "واژگان روان‌شناسی: behaviour، habit، motive، emotion، stress، anxiety، confidence، resilience، burnout، bias، coping strategy، trigger. motive دلیل عمل است، emotion احساس و bias کج‌شدگی نظام‌مند در داوری، نه نظر."),
                ("Describing people precisely: to be prone to, to be aware of, to cope with, to open up, to bottle something up, to take something to heart, to come to terms with. The phrasal verbs here carry most of the emotional meaning, and each has a register — 'bottle up' is conversational, 'come to terms with' is neutral.", "توصیف دقیق آدم‌ها: be prone to، be aware of، cope with، open up، bottle something up، take something to heart، come to terms with. فعل‌های عبارتی اینجا بیشتر معنای عاطفی را حمل می‌کنند و هر کدام لحنی دارند — «bottle up» گفتاری و «come to terms with» خنثی است."),
                ("Arts vocabulary: a novel, a plot, a character, a setting, a theme, a style, a genre, a performance, an exhibition, a review, a masterpiece, an adaptation. A theme is what the work is about; a plot is what happens; a setting is where and when. Reviews that confuse the three are summaries with adjectives.", "واژگان هنر: novel، plot، character، setting، theme، style، genre، performance، exhibition، review، masterpiece، adaptation. theme موضوع اثر است، plot آنچه رخ می‌دهد و setting کجا و کِی. نقدی که این سه را یکی کند خلاصه‌ای است با صفت."),
                ("Evaluative adjectives with reasons attached: moving, gripping, predictable, contrived, uneven, subtle, heavy-handed, overlong. Each is a judgement about craft, and each can be supported by a detail — 'the ending is contrived' is arguable in a way that 'the ending is bad' is not.", "صفت‌های ارزشی با دلیل پیوسته: moving، gripping، predictable، contrived، uneven، subtle، heavy-handed، overlong. هر کدام داوری دربارهٔ فن است و با جزئیات پشتیبانی می‌شود — «the ending is contrived» قابل بحث است، برخلاف «the ending is bad»."),
            ],
            [
                ("He is prone to taking criticism personally.", "او مستعد است نقد را به خود بگیرد."),
                ("She coped with the move by keeping a routine.", "او با حفظ روال روزانه با جابه‌جایی کنار آمد."),
                ("The novel's theme is memory; its setting is a town that is being rebuilt.", "موضوع رمان حافظه است و مکانش شهرکی که بازسازی می‌شود."),
                ("The performance was subtle, but the second act was overlong.", "اجرا ظریف بود، اما پردهٔ دوم بیش از حد طولانی."),
            ],
            [
                mcq("A 'bias' in psychology is ___.", "«bias» در روان‌شناسی ___ است.", ["an opinion", "a systematic tilt in judgement", "a strong emotion", "a habit"], 1,
                    "It is a pattern, not a preference.", "الگوست، نه ترجیح."),
                mcq("Which word describes where a story happens?", "کدام واژه جای رخداد داستان را می‌گوید؟", ["theme", "plot", "setting", "genre"], 2,
                    "Setting is time and place.", "setting زمان و مکان است."),
            ],
            [
                gap("She found it hard to ___ up about the loss.", ["open"], "Open up = speak about feelings.", "open up یعنی از احساسات گفتن."),
                gap("The film is an ___ of a novel published in 1998.", ["adaptation"], "A work made from another work.", "اثری ساخته‌شده از اثری دیگر."),
                mcq("Which judgement can be supported by a detail?", "کدام داوری را می‌توان با جزئیات پشتیبانی کرد؟", ["The book is boring.", "The middle section repeats the opening chapter.", "The author is untalented.", "Nobody likes it."], 1,
                    "It names something checkable in the text.", "چیزی قابل بررسی در متن را نام می‌برد."),
                mcq("'Burnout' is best described as ___.", "«Burnout» بهتر است ___ توصیف شود.", ["a single bad day", "exhaustion from prolonged stress", "a lack of skill", "a conflict with a manager"], 1,
                    "It is cumulative, not episodic.", "انباشته است، نه رویدادی."),
            ],
        ),
        lesson(
            "b2-u8-l3",
            "speaking",
            ("The presentation: structure an argument aloud", "ارائه: استدلال را بلند سازمان بده"),
            ("Deliver a three-minute case with a signposted structure and a clear ask.", "استدلال سه‌دقیقه‌ای با ساختار نشانه‌گذاری‌شده و درخواست روشن ارائه بده."),
            [
                ("A three-minute presentation has room for one idea. Structure: the hook (a number or a short story), the claim, three supports, the objection you answer yourself, then the ask — what you want the listener to do or believe. Without the ask, the audience leaves with information and no decision.", "ارائهٔ سه‌دقیقه‌ای جای یک ایده را دارد. ساختار: قلاب (یک عدد یا داستان کوتاه)، ادعا، سه پشتوانه، اعتراضی که خودت پاسخ می‌دهی، و بعد درخواست — کاری که می‌خواهی شنونده بکند یا باور کند. بدون درخواست، مخاطب با اطلاعات می‌رود و بدون تصمیم."),
                ("Signposting is what makes structure audible: I'll make three points; the first is…; that brings me to…; before I finish, the objection you're probably thinking of; so here's what I'm asking. These phrases are not filler; they are the map.", "نشانه‌گذاری چیزی است که ساختار را شنیدنی می‌کند: I'll make three points؛ the first is…؛ that brings me to…؛ before I finish, the objection you're probably thinking of؛ so here's what I'm asking. این عبارت‌ها پرکننده نیستند؛ نقشه‌اند."),
                ("Delivery: slow down at the claim and the ask, and let the supports run faster. Pause after the number instead of explaining it immediately — the pause is what makes the number land. Fillers (um, like, you know) cluster where the speaker has not decided what comes next, so the fix is planning, not willpower.", "ارائه: در ادعا و در درخواست کند شو و پشتوانه‌ها را تندتر بران. بعد از عدد درنگ کن و فوراً توضیحش نده — همان درنگ عدد را می‌نشاند. پرکننده‌ها (um، like، you know) جایی جمع می‌شوند که گوینده تصمیم نگرفته بعد چه بگوید؛ پس درمانش برنامه‌ریزی است، نه اراده."),
                ("Handling questions: repeat the question in your own words (it buys time and checks you heard it), answer in one sentence, then add the detail. If you do not know, say what you would need to know — that is an answer, and it is more credible than invention.", "پاسخ به پرسش‌ها: پرسش را با واژه‌های خودت تکرار کن (وقت می‌خرد و بررسی می‌کند شنیده‌ای)، در یک جمله پاسخ بده و بعد جزئیات را اضافه کن. اگر نمی‌دانی، بگو چه چیزی را باید بدانی — این هم پاسخ است و از ساختن باورپذیرتر است."),
            ],
            [
                ("I'll make three points, and the third is the one that matters.", "سه نکته می‌گویم و سومی مهم‌ترین است."),
                ("Before I finish, let me take the objection you're probably thinking of.", "پیش از پایان، بگذار اعتراضی را که احتمالاً در ذهن دارید مطرح کنم."),
                ("So here's what I'm asking: a two-week trial, not a permanent change.", "پس درخواستم این است: یک آزمایش دو هفته‌ای، نه تغییری همیشگی."),
                ("If I don't know, I'll tell you what I'd need to find out.", "اگر ندانم، می‌گویم چه چیزی را باید پیدا کنم."),
            ],
            [
                mcq("What should come last in a three-minute presentation?", "در ارائهٔ سه‌دقیقه‌ای چه چیزی آخر می‌آید؟", ["a new argument", "the ask", "the hook", "another example"], 1,
                    "The audience needs a decision to carry away.", "مخاطب باید تصمیمی با خود ببرد."),
                mcq("Why pause after a number?", "چرا بعد از عدد درنگ کنیم؟", ["to remember the next line", "to let it land", "to check the slide", "to slow the clock"], 1,
                    "The pause gives the figure weight.", "درنگ به عدد وزن می‌دهد."),
            ],
            [
                gap("That ___ me to my second point.", ["brings", "leads"], "Signposting move.", "حرکت نشانه‌گذاری."),
                write("Write the opening sixty seconds of a presentation arguing that your workplace should trial a four-day week. Include the hook, the claim and the first support.",
                      "شصت ثانیهٔ آغازین ارائه‌ای را بنویس که استدلال می‌کند محیط کارت باید چهار روز کاری را آزمایش کند. قلاب، ادعا و نخستین پشتوانه را بیاور.",
                      100, ["because"],
                      "Use at least three signposting phrases so the structure is audible.",
                      "دست‌کم سه عبارت نشانه‌گذاری به کار ببر تا ساختار شنیدنی شود."),
                mcq("Which is the best way to handle a question you cannot answer?", "بهترین راه پاسخ به پرسشی که نمی‌توانی پاسخ دهی کدام است؟", ["change the subject", "invent a plausible figure", "say what you would need to find out", "repeat the question and stop"], 2,
                    "Naming the missing information is an answer.", "نام بردن اطلاعات نبوده، خودش پاسخ است."),
            ],
        ),
    ],
)
