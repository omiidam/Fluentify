#!/usr/bin/env python3
"""The B2 final examination: 33 marks over six sections.

Same architecture as A1, A2 and B1 — six sections in skill order, one mark per
item, passages counted through their questions — with items that require B2
control rather than recognition: perfect aspect in narrative, mixed conditionals,
causatives, reduced relatives, inversion, participle clauses and the gerund /
infinitive pairs that change meaning.
"""

from course_kit import exam, listen, mcq, reading_item, say, section, write

BLURB = (
    "Six skills, each marked on its own. Grammar, vocabulary, reading and listening are marked from your answers; writing is marked against a rubric; speaking is marked from what this device hears you say. You need 60% overall, at least 50% in every skill, and all six skills must be assessed.",
    "شش مهارت، هر یک جداگانه. گرامر، واژگان، خواندن و شنیدن از پاسخ‌ها نمره می‌گیرند؛ نوشتن با معیارهای مشخص و گفتن از آنچه دستگاه می‌شنود. برای قبولی ۶۰٪ کل و ۵۰٪ در هر مهارت لازم است و هر شش مهارت باید سنجیده شود.",
)

GRAMMAR = [
    mcq("By the time the guests arrived, she ___ for three hours.", "تا وقتی مهمان‌ها رسیدند، سه ساعت ___ بود.", ["cooked", "had been cooking", "was cooking", "has cooked"], 1,
        "Duration up to a past moment: past perfect continuous.", "مدت تا یک نقطهٔ گذشته: ماضی بعید استمراری."),
    mcq("If she had taken the earlier train, she ___ here by now.", "اگر قطار زودتر را گرفته بود، تا حالا ___ .", ["would be", "would have been", "will be", "had been"], 0,
        "Past condition, present result: a mixed conditional with would be.", "شرط گذشته و نتیجهٔ حال: شرطی مختلط با would be."),
    mcq("We ___ the roof repaired before the winter.", "پیش از زمستان سقف را ___ .", ["made", "had", "did", "let"], 1,
        "Causative have + object + participle.", "سببی have + مفعول + اسم مفعول."),
    mcq("The proposal, ___ last month, has already been rejected.", "پیشنهادی که ماه گذشته ___، همین حالا رد شده است.", ["submitting", "submitted", "which submitting", "to submit"], 1,
        "A reduced passive relative: which was submitted → submitted.", "موصولی مجهول کوتاه‌شده: which was submitted ← submitted."),
    mcq("Not only ___ the deadline, but they also lost the client.", "نه‌تنها مهلت را ___، بلکه مشتری را هم از دست دادند.", ["they missed", "did they miss", "they did miss", "missed they"], 1,
        "Fronted 'not only' inverts subject and auxiliary.", "«not only» در آغاز، نهاد و کمکی را جابه‌جا می‌کند."),
    mcq("I'll never forget ___ the sea for the first time.", "هرگز نخستین بار دیدن دریا را فراموش نمی‌کنم.", ["to see", "seeing", "see", "seen"], 1,
        "Forget + -ing recalls the experience; forget + to do is a duty.", "forget + ing تجربه را به یاد می‌آورد و forget + to do وظیفه است."),
    mcq("___ the figures twice, he still found an error.", "با اینکه ارقام را دو بار ___، باز هم خطایی یافت.", ["Checking", "Having checked", "Checked", "To check"], 1,
        "A completed action before the main verb: perfect participle.", "عملی کامل‌شده پیش از فعل اصلی: وجه وصفی کامل."),
    mcq("She wishes she ___ the offer when she had the chance.", "افسوس می‌خورد که فرصت داشت پیشنهاد را ___ .", ["accepts", "accepted", "had accepted", "would accept"], 2,
        "A past regret takes wish + past perfect.", "افسوس گذشته wish + ماضی بعید می‌گیرد."),
]

VOCABULARY = [
    mcq("The scheme was designed to ___ staff whose roles had been automated.", "این طرح برای ___ کارکنانی طراحی شد که نقششان خودکار شده بود.", ["reskill", "dismiss", "recruit", "outsource"], 0,
        "Reskilling teaches people skills for new roles.", "reskilling آموزش مهارت برای نقش تازه است."),
    mcq("The benefit of the app is real, but it comes at the ___ of privacy.", "فایدهٔ اپ واقعی است، اما به ___ حریم خصوصی تمام می‌شود.", ["cost", "price", "expense", "charge"], 0,
        "The fixed phrase is 'at the cost of'.", "عبارت ثابت «at the cost of» است."),
    mcq("His argument was weak because it rested on a single ___ of data.", "استدلالش ضعیف بود چون بر یک ___ داده تکیه داشت.", ["sample", "evidence", "proof", "figure"], 0,
        "A sample is a set of data; evidence is uncountable here.", "sample مجموعه‌ای از داده است و evidence اینجا غیرقابل‌شمارش."),
    mcq("The two accounts of the meeting ___ each other on almost every point.", "دو روایت جلسه در تقریباً هر نکته یکدیگر را ___ .", ["contradict", "confirm", "compare", "conclude"], 0,
        "Contradict means to state the opposite.", "contradict یعنی خلاف آن را گفتن."),
    mcq("A norm is what a group expects; a ___ is what it believes is good.", "norm چیزی است که گروه انتظار دارد و ___ چیزی که خوب می‌داند.", ["value", "custom", "habit", "rule"], 0,
        "Values are beliefs about what matters; customs are practices.", "value باور به اهمیت است و custom رویه."),
    mcq("The report's findings were ___ by a second study, which reached the same conclusion.", "یافته‌های گزارش با مطالعهٔ دومی که به همان نتیجه رسید ___ شد.", ["corroborated", "estimated", "attributed", "postponed"], 0,
        "Corroborate = confirm with further evidence.", "corroborate یعنی با شاهد بیشتر تأیید کردن."),
    mcq("She was ___ to project lead after eighteen months.", "بعد از هجده ماه به سرپرست پروژه ___ شد.", ["promoted", "applied", "transferred", "seconded"], 0,
        "Promote = move to a higher position.", "promote یعنی رفتن به سمت بالاتر."),
    mcq("The new policy was criticized for being too ___, with no room for exceptions.", "سیاست تازه را به این دلیل نقد کردند که بیش از حد ___ بود و جایی برای استثنا نداشت.", ["rigid", "flexible", "vague", "lenient"], 0,
        "Rigid means unable to bend; lenient would mean the opposite problem.", "rigid یعنی بی‌انعطاف و lenient مشکل معکوس است."),
]

READING = [
    reading_item(
        ("The town that turned its lights off", "شهری که چراغ‌هایش را خاموش کرد"),
        ("In 2019 the council of a small mountain town voted to switch off its streetlights after midnight. The stated reason was cost, and the saving was real: a third of the lighting budget, every year. What nobody predicted was what the dark would do to the town's reputation.\n\nWithin two winters, the town had become a destination for people who wanted to see the night sky. Guesthouses that had struggled through February were fully booked. A former gas station reopened as a small observatory with two second-hand telescopes, run by a retired physics teacher who had spent forty years explaining orbits to bored teenagers and now had lines.\n\nNot everyone gained. Several residents complained that the dark made the walk from the bus stop unpleasant, and the council eventually paid for lit paths along the two main routes. The shopkeepers on the side streets say the visitors look at the sky, not at the windows, and their takings have not moved.\n\nThe council's report on the scheme is careful. It notes that the town cannot claim to have reduced light pollution nationally, that the observatory runs at a loss and is subsidised by the council, and that the guesthouse boom may not survive a third mild winter. It concludes, however, that the decision paid for itself — not in the way it was intended, but in a way nobody had costed.", "در سال ۲۰۱۹ شورای شهرکی کوهستانی رأی داد چراغ‌های خیابان را پس از نیمه‌شب خاموش کند. دلیل اعلام‌شده هزینه بود و صرفه‌جویی واقعی: یک‌سوم بودجهٔ روشنایی در هر سال. آنچه کسی پیش‌بینی نکرد این بود که تاریکی با اعتبار شهر چه می‌کند.\n\nدر دو زمستان، شهر مقصد کسانی شد که می‌خواستند آسمان شب را ببینند. مهمان‌خانه‌هایی که فوریه را به‌سختی می‌گذراندند پر شدند. پمپ‌بنزین تعطیل‌شده‌ای دوباره به‌عنوان رصدخانهٔ کوچکی با دو تلسکوپ دست‌دوم باز شد، به دست معلم فیزیک بازنشسته‌ای که چهل سال مدار را برای نوجوانان بی‌حوصله توضیح داده بود و حالا صف داشت.\n\nهمه سود نبردند. چند ساکن شکایت کردند که تاریکی مسیر پیاده از ایستگاه اتوبوس را ناخوشایند کرده و شورا در نهایت هزینهٔ روشنایی دو مسیر اصلی را پرداخت. مغازه‌داران کوچه‌های فرعی می‌گویند بازدیدکنندگان به آسمان نگاه می‌کنند نه به ویترین و فروششان تکان نخورده.\n\nگزارش شورا محتاطانه است. می‌نویسد شهر نمی‌تواند ادعا کند آلودگی نوری را در سطح ملی کم کرده، رصدخانه زیان‌ده است و شورا یارانه‌اش می‌دهد و رونق مهمان‌خانه شاید زمستان معتدل سوم را نبیند. اما نتیجه می‌گیرد که تصمیم هزینه‌اش را درآورد — نه آن‌طور که قصدش بود، بلکه آن‌طور که کسی برآورد نکرده بود."),
        [
            mcq("Why were the streetlights switched off?", "چرا چراغ‌های خیابان خاموش شد؟", ["to attract tourists", "to save money", "to help the observatory", "because residents asked"], 1,
                "'The stated reason was cost.' The tourism was unforeseen.", "«دلیل اعلام‌شده هزینه بود.» گردشگری پیش‌بینی نشده بود."),
            mcq("What happened to the side-street shops?", "چه بر سر مغازه‌های کوچه‌های فرعی آمد؟", ["they gained customers", "their sales did not change", "they closed", "they moved to the main road"], 1,
                "'Their takings have not moved.'", "«فروششان تکان نخورده»."),
            mcq("The council's report is best described as ___.", "گزارش شورا بهتر است ___ توصیف شود.", ["triumphant", "cautious", "hostile", "unclear"], 1,
                "It is 'careful', lists the limits, and only then concludes.", "«محتاطانه» است، محدودیت‌ها را می‌آورد و بعد نتیجه می‌گیرد."),
        ],
    ),
    reading_item(
        ("Against the cult of the deadline", "علیه آیین مهلت"),
        ("Ask a manager why a project failed and the answer is often a date. Ask the same manager why the date was chosen and the answer is often silence. Deadlines are treated as facts of nature, like weather, when they are decisions made by people who may have guessed.\n\nThe research on deadlines is less flattering than the folklore. Short deadlines do concentrate effort, and for routine work that is an advantage. For work that requires a solution nobody has found yet, pressure narrows attention: people reach for the first adequate answer and stop looking. The deadline is met. The better answer is never found, and nobody records its absence, because an absence does not appear in a progress report.\n\nThis is not an argument for deadlines that drift. A team without any date will produce a plan that is always nearly finished. The argument is narrower and harder to act on: a deadline should be set for the part of the work that is genuinely predictable, and the unpredictable part should be time-boxed instead — a fixed number of weeks spent searching, with a review at the end, rather than a promise about a result that nobody can promise honestly.\n\nOrganisations rarely do this, because a time-box is harder to explain to the person above. 'We will spend six weeks finding out whether this is possible' sounds like a confession, while 'we will deliver on the fourteenth' sounds like management. The second is more comfortable to say and less true. What the organization has actually bought is a date, and it has paid for it with the answer.", "از مدیر بپرسید چرا پروژه شکست خورد و پاسخ اغلب یک تاریخ است. از همان مدیر بپرسید آن تاریخ چرا انتخاب شد و پاسخ اغلب سکوت است. مهلت‌ها واقعیتی طبیعی مثل آب‌وهوا فرض می‌شوند، در حالی که تصمیم کسانی‌اند که شاید حدس زده‌اند.\n\nپژوهش‌ها دربارهٔ مهلت چندان خوش‌بینانه نیستند. مهلت کوتاه تلاش را متمرکز می‌کند و برای کار روتین مزیت است. برای کاری که راه‌حلی پیدا نشده لازم دارد، فشار توجه را تنگ می‌کند: آدم‌ها به نخستین پاسخ قابل‌قبول می‌رسند و جست‌وجو را متوقف می‌کنند. مهلت رعایت می‌شود. پاسخ بهتر هرگز پیدا نمی‌شود و کسی نبودنش را ثبت نمی‌کند، چون غیاب در گزارش پیشرفت نمی‌آید.\n\nاین استدلال به نفع مهلت‌های سرگردان نیست. تیمی که هیچ تاریخی ندارد برنامه‌ای می‌سازد که همیشه تقریباً تمام است. استدلال محدودتر و سخت‌تر برای عمل است: مهلت باید برای بخشی از کار گذاشته شود که واقعاً قابل پیش‌بینی است و بخش غیرقابل پیش‌بینی باید «زمان‌بندی جعبه‌ای» شود — چند هفتهٔ ثابت برای جست‌وجو با بازبینی در پایان، نه وعده‌ای دربارهٔ نتیجه‌ای که کسی صادقانه نمی‌تواند وعده بدهد.\n\nسازمان‌ها کم به این کار تن می‌دهند، چون توضیح جعبهٔ زمانی برای مافوق سخت‌تر است. «شش هفته وقت می‌گذاریم بفهمیم این ممکن است یا نه» شبیه اعتراف است و «چهاردهم تحویل می‌دهیم» شبیه مدیریت. دومی راحت‌تر گفته می‌شود و کمتر درست است. آنچه سازمان خریده در واقع یک تاریخ است و بهایش را با پاسخ داده است."),
        [
            mcq("What is the author's main complaint about deadlines?", "شکایت اصلی نویسنده دربارهٔ مهلت‌ها چیست؟", ["they are too long", "they are treated as fixed when they are guesses", "they are never met", "managers dislike them"], 1,
                "The opening contrast is between a date and the silence about how it was chosen.", "تضاد آغازین میان تاریخ و سکوت دربارهٔ چگونگی انتخاب آن است."),
            mcq("For which kind of work does pressure do most damage?", "فشار بیشترین آسیب را به کدام کار می‌زند؟", ["routine work", "work needing a solution nobody has found", "work with a clear plan", "work that is already late"], 1,
                "Pressure narrows attention where search is needed.", "فشار جایی که جست‌وجو لازم است توجه را تنگ می‌کند."),
            mcq("What does 'it has paid for it with the answer' mean?", "«it has paid for it with the answer» یعنی چه؟", ["the answer was expensive to buy", "meeting the date cost the better solution", "the answer arrived on time", "the organization sold the answer"], 1,
                "The date was purchased by giving up the better answer.", "تاریخ با از دست دادن پاسخ بهتر خریده شده است."),
        ],
    ),
]

LISTENING = [
    listen("We thought the delay was the supplier, but when we looked at the dates, the order went out four days after the approval. So the problem was inside the building.",
       "What was the real cause of the delay?", "علت واقعی تأخیر چه بود؟", ["the supplier", "a slow internal order", "a transport strike", "missing approval"], 1,
       "The order left four days after approval, so the delay was internal.", "سفارش چهار روز بعد از تأیید رفت، پس تأخیر داخلی بود."),
    listen("I'd have taken the job if it had been closer, but two hours each way is not a commute, it's a move.",
       "Why did the speaker refuse the job?", "چرا گوینده کار را نپذیرفت؟", ["the salary was low", "the journey was too long", "the role was too senior", "the team was difficult"], 1,
       "Two hours each way made the commute impossible.", "دو ساعت در هر مسیر رفت‌وآمد را ناممکن می‌کرد."),
    listen("The review isn't negative, exactly. It says the book is well researched and then spends three paragraphs on what it leaves out. I'd call that a warning.",
       "How does the speaker interpret the review?", "گوینده نقد را چگونه تفسیر می‌کند؟", ["as praise", "as a warning", "as unfair", "as unimportant"], 1,
       "The emphasis on omissions is read as a warning.", "تأکید بر آنچه حذف شده هشدار فهمیده می‌شود."),
    listen("We're not saying the app replaces the teacher. What we found is that students who got the feedback within an hour used it; the ones who got it a week later had already moved on.",
       "What did the study find?", "مطالعه چه یافت؟", ["the app replaces teachers", "timing of feedback mattered", "students ignored feedback", "a week was enough"], 1,
       "Immediate feedback was used; late feedback was not.", "بازخورد فوری استفاده شد و دیررس نه."),
    listen("There's a version of this plan that costs half as much and takes a year longer, and honestly, I'd rather have that argument now than in March.",
       "What is the speaker asking for?", "گوینده چه می‌خواهد؟", ["a cheaper plan only", "a discussion of the alternative now", "a delay until March", "a bigger budget"], 1,
       "They want the trade-off debated before it is too late.", "می‌خواهد بده‌بستان پیش از دیر شدن بحث شود."),
    listen("The first two years were mostly translation. It was only in the third that I started to hear the joke before the punchline — that's when I knew the language had stopped being a task.",
       "What changed in the third year?", "در سال سوم چه عوض شد؟", ["they began translating", "the language became natural", "they stopped studying", "they moved abroad"], 1,
       "Anticipating a joke is the sign it stopped being a task.", "پیش‌بینی شوخی نشانهٔ طبیعی شدن است."),
]

WRITING = [
    write("Write a report for a manager on a four-week trial of a four-day working week. State the purpose, give two findings with numbers and a sample, note one limitation, and recommend whether to continue.",
          "گزارشی برای مدیر دربارهٔ چهار هفته آزمایش هفتهٔ کاری چهارروزه بنویس. هدف را بگو، دو یافته با عدد و نمونه بیاور، یک محدودیت را ذکر کن و توصیه کن ادامه بدهد یا نه.",
          110, ["recommended", "although"],
          "Headings, no contractions, the recommendation before the detail, and a base for every percentage.",
          "تیتر، بدون شکل کوتاه، توصیه پیش از جزئیات و پایه برای هر درصد."),
    write("Write an essay of about 150 words on this question: 'Remote work has made workplaces less creative.' Give both sides with an example each, then state your own position.",
          "مقاله‌ای حدود ۱۵۰ واژه دربارهٔ این پرسش بنویس: «کار دورکاری محیط کار را کم‌خلاق‌تر کرده است.» هر دو طرف را با یک مثال بیاور و بعد موضع خودت را بگو.",
          150, ["however", "whereas"],
          "Four paragraphs: the question, the case for, the case against, your position. One concrete example per side and one hedge.",
          "چهار پاراگراف: پرسش، دلایل موافق، دلایل مخالف، موضع تو. برای هر طرف یک مثال مشخص و یک عبارت احتیاطی."),
]

SPEAKING = [
    say("What strikes me about the proposal is not the cost but the assumption behind it — that demand will stay exactly where it is today.", "آنچه دربارهٔ این پیشنهاد توجهم را جلب می‌کند هزینه نیست، فرض پشتش است: اینکه تقاضا دقیقاً همان‌جا که امروز هست می‌ماند."),
    say("I'd accept that the trial was short, though it doesn't change the main finding: the waiting times fell in every branch that took part.", "می‌پذیرم که آزمایش کوتاه بود، هرچند یافتهٔ اصلی را عوض نمی‌کند: زمان انتظار در هر شعبه‌ای که شرکت کرد کم شد."),
    say("If I had known how long the approval would take, I would have started the paperwork before the vacation rather than after it.", "اگر می‌دانستم تأیید چقدر طول می‌کشد، کارهای اداری را پیش از تعطیلات شروع می‌کردم نه بعد از آن."),
]

PAPER = exam(
    55, 0.6, 0.5, BLURB,
    [
        section("grammar", GRAMMAR),
        section("vocabulary", VOCABULARY),
        section("reading", READING),
        section("listening", LISTENING),
        section("writing", WRITING),
        section("speaking", SPEAKING),
    ],
)
