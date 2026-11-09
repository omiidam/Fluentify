#!/usr/bin/env python3
"""The C1 final examination: 33 marks over six sections.

Same architecture as the four papers below it — six sections in skill order, one
mark per item, passages counted through their questions — with items that need
C1 control rather than recognition: clefting and inversion, modal perfects,
nominalisation, ellipsis, reporting passives, the mandative subjunctive and
comparatives that carry an argument.
"""

from course_kit import exam, listen, mcq, reading_item, say, section, write

BLURB = (
    "Six skills, each marked on its own. Grammar, vocabulary, reading and listening are marked from your answers; writing is marked against a rubric; speaking is marked from what this device hears you say. You need 60% overall, at least 50% in every skill, and all six skills must be assessed.",
    "شش مهارت، هر یک جداگانه. گرامر، واژگان، خواندن و شنیدن از پاسخ‌ها نمره می‌گیرند؛ نوشتن با معیارهای مشخص و گفتن از آنچه دستگاه می‌شنود. برای قبولی ۶۰٪ کل و ۵۰٪ در هر مهارت لازم است و هر شش مهارت باید سنجیده شود.",
)

GRAMMAR = [
    mcq("___ the funding had arrived earlier, the trial would have finished.", "اگر بودجه زودتر رسیده بود، آزمایش تمام می‌شد.", ["If", "Had", "Should", "Were"], 1,
        "A past unreal condition inverted: had + participle, no if.", "شرط غیرواقعی گذشته به‌صورت جابه‌جاشده: had + اسم مفعول، بدون if."),
    mcq("What surprised the reviewers ___ the absence of any control group.", "آنچه داوران را شگفت‌زده کرد ___ نبود هیچ گروه گواه بود.", ["is", "was", "were", "has been"], 1,
        "A wh-cleft takes a singular verb with a singular complement.", "wh-cleft با مکمل مفرد فعل مفرد می‌گیرد."),
    mcq("The committee recommended that the policy ___ before the next quarter.", "کمیته توصیه کرد سیاست پیش از سه‌ماههٔ بعد ___ .", ["is reviewed", "be reviewed", "was reviewed", "reviews"], 1,
        "Mandative subjunctive after recommend that.", "وجه شرطی الزامی پس از recommend that."),
    mcq("The scheme is said ___ two years ago.", "گفته می‌شود طرح دو سال پیش ___ .", ["to launch", "to have launched", "to be launched", "launching"], 1,
        "Reporting passive with a perfect infinitive for a past event.", "مجهول نقل با مصدر کامل برای رویداد گذشته."),
    mcq("'Will they extend the deadline?' 'I hope ___ .'", "«مهلت را تمدید می‌کنند؟» «امیدوارم ___ .»", ["it", "so", "that", "yes"], 1,
        "So substitutes for the whole clause.", "so جانشین کل بند است."),
    mcq("___ the figures twice, the auditor still missed the discrepancy.", "با اینکه ارقام را دو بار ___، حسابرس باز هم اختلاف را ندید.", ["Checking", "Having checked", "Checked", "To check"], 1,
        "A completed action before the main clause: perfect participle.", "عملی کامل‌شده پیش از بند اصلی: وجه وصفی کامل."),
    mcq("Never ___ a clearer case for reform.", "هرگز ___ روشن‌تر برای اصلاح.", ["I have heard", "have I heard", "I heard", "did I heard"], 1,
        "Fronted 'never' requires inversion.", "«never» در آغاز جابه‌جایی می‌خواهد."),
    mcq("Far from ___ the dispute, the ruling deepened it.", "حکم به‌جای ___ اختلاف، آن را عمیق‌تر کرد.", ["resolve", "resolving", "resolved", "resolves"], 1,
        "Far from + -ing reverses an expectation.", "far from + ing انتظار را وارونه می‌کند."),
]

VOCABULARY = [
    mcq("The two accounts ___ each other on every material point.", "دو روایت در هر نکتهٔ مهم یکدیگر را ___ .", ["corroborate", "contradict", "confirm", "compare"], 1,
        "Contradict states the opposite.", "contradict خلاف را می‌گوید."),
    mcq("The effect was statistically significant and practically ___.", "اثر از نظر آماری معنادار و از نظر عملی ___ بود.", ["trivial", "robust", "coherent", "rigorous"], 0,
        "Detectable is not the same as important.", "قابل تشخیص با مهم یکی نیست."),
    mcq("The report's findings were ___ by an independent replication.", "یافته‌های گزارش با تکرار مستقل ___ شد.", ["undermined", "corroborated", "disputed", "postponed"], 1,
        "A successful replication confirms them.", "تکرار موفق آن‌ها را تأیید می‌کند."),
    mcq("A ___ is a situation in which two duties cannot both be met.", "___ موقعیتی است که دو وظیفه با هم برآورده نمی‌شوند.", ["conflict of interest", "false equivalence", "moral hazard", "trade-off"], 0,
        "A conflict of interest sets duties against each other.", "تعارض منافع دو وظیفه را رودررو می‌کند."),
    mcq("The claim gained ___ before anyone had checked it.", "ادعا پیش از آنکه کسی بررسی‌اش کند ___ .", ["traction", "consent", "sanction", "momentum"], 0,
        "Gain traction is the fixed collocation for spreading.", "gain traction هم‌نشینی ثابت برای گسترش است."),
    mcq("The decision was ___ to the board because no one had the mandate.", "تصمیم به هیئت ___ شد چون هیچ‌کس اختیار نداشت.", ["delegated", "escalated", "deferred", "reversed"], 1,
        "Escalate moves a decision upwards.", "escalate تصمیم را به بالا می‌برد."),
    mcq("Her objection was not to the aim but to the ___ of the plan.", "اعتراض او به هدف نبود، به ___ طرح بود.", ["implementation", "implication", "innovation", "intention"], 0,
        "Implementation is how it is carried out.", "implementation یعنی چگونه اجرا می‌شود."),
    mcq("The novel's central ___ is a door that never opens.", "___ اصلی رمان دری است که هرگز باز نمی‌شود.", ["motif", "register", "pacing", "persona"], 0,
        "A motif is a recurring image or idea.", "motif تصویر یا ایدهٔ تکرارشونده است."),
]

READING = [
    reading_item(
        ("The cost of being measurable", "هزینهٔ قابل اندازه‌گیری بودن"),
        ("Every organisation measures something, and what it measures slowly becomes what it values. This is not a scandal; it is arithmetic. A manager who is judged on a number will attend to the number, and the parts of the work that have no number will be attended to by whoever has time, which is nobody.\n\nThe result is well documented and rarely discussed in the same document as the metrics themselves. Response times fall while the quality of the response falls with them. Attendance improves while the teaching does not. A hospital meets its waiting-time target by reclassifying patients at the door — the target was met, and the waiting did not move.\n\nThe usual remedy is more measurement: add a quality indicator, audit the reclassification, publish the exceptions. This works in the way that adding a second ruler works on a table that has been cut too short. The new measure is now the thing being gamed, and the work has one more meeting.\n\nThere is a harder answer, and it is unpopular because it cannot be delegated to a dashboard: some things are known by people rather than by systems, and the only way to know them is to ask the people and believe the answer. That is slower, it does not scale, and it makes the manager responsible for a judgement instead of a figure. Organisations choose metrics not because they are accurate but because they are defensible — a number can be shown to a committee, and a judgement has to be defended by the person who made it.\n\nNone of this argues for abolishing measurement. A target that nobody can check is a rumour with authority. The argument is that measurement should be treated as a claim rather than a fact: what does this number leave out, who decided it mattered, and what would we see if it were wrong? Those three questions cost nothing and are almost never asked.",
         "هر سازمان چیزی را اندازه می‌گیرد و آنچه اندازه می‌گیرد آرام‌آرام همان می‌شود که برایش ارزش قائل است. این رسوایی نیست؛ حساب است. مدیری که با یک عدد سنجیده می‌شود به همان عدد می‌پردازد و بخش‌های کار که عددی ندارند را هر کس وقت داشته باشد انجام می‌دهد، که هیچ‌کس نیست.\n\nنتیجه به‌خوبی مستند شده و به‌ندرت در همان سندی بحث می‌شود که معیارها در آن‌اند. زمان پاسخ کوتاه می‌شود و کیفیت پاسخ با آن کوتاه می‌شود. حضور بهتر می‌شود و آموزش نه. بیمارستانی هدف زمان انتظار را با بازطبقه‌بندی بیماران دم در برمی‌آورد — هدف محقق شد و انتظار تکان نخورد.\n\nدرمان معمول اندازه‌گیری بیشتر است: یک شاخص کیفیت اضافه کن، بازطبقه‌بندی را بازرسی کن، استثناها را منتشر کن. این مثل گذاشتن خط‌کش دومی است روی میزی که کوتاه بریده شده. معیار تازه حالا خودش بازی‌خوردنی است و کار یک جلسهٔ دیگر پیدا کرده.\n\nپاسخ سخت‌تری هست و محبوب نیست چون نمی‌شود به یک داشبورد سپردش: بعضی چیزها را آدم‌ها می‌دانند نه سامانه‌ها و تنها راه دانستنشان پرسیدن از آدم‌ها و باور کردن پاسخ است. این کندتر است، مقیاس‌پذیر نیست و مدیر را مسئول یک داوری می‌کند نه یک رقم. سازمان‌ها معیار عددی را برمی‌گزینند نه چون دقیق است، بلکه چون قابل دفاع است — عدد را می‌توان به کمیته نشان داد و داوری را باید کسی که کرده دفاع کند.\n\nهیچ‌کدام از این‌ها استدلال برای حذف اندازه‌گیری نیست. هدفی که کسی نمی‌تواند بررسی‌اش کند شایعه‌ای است با اقتدار. استدلال این است که اندازه‌گیری را باید ادعا دانست نه واقعیت: این عدد چه چیزی را جا می‌گذارد، چه کسی تصمیم گرفت مهم است و اگر غلط بود چه می‌دیدیم؟ این سه پرسش هیچ هزینه‌ای ندارند و تقریباً هرگز پرسیده نمی‌شوند."),
        [
            mcq("What is the author's central claim?", "ادعای اصلی نویسنده چیست؟", ["measurement should be abolished", "what is measured becomes what is valued, with costs", "managers dislike numbers", "targets are always met"], 1,
                "The opening sentence states the mechanism and the text then shows its costs.", "جملهٔ آغازین سازوکار را می‌گوید و متن هزینه‌هایش را نشان می‌دهد."),
            mcq("Why is 'more measurement' an inadequate remedy?", "چرا «اندازه‌گیری بیشتر» درمان ناکافی است؟", ["it is expensive", "the new measure is gamed in turn", "it needs new staff", "it is unpopular"], 1,
                "'The new measure is now the thing being gamed.'", "«معیار تازه خودش بازی‌خوردنی می‌شود»."),
            mcq("Why do organisations prefer metrics, according to the text?", "به گفتهٔ متن چرا سازمان‌ها معیار عددی را ترجیح می‌دهند؟", ["they are more accurate", "they are defensible to a committee", "they are cheaper", "staff prefer them"], 1,
                "A number can be shown; a judgement must be defended.", "عدد را می‌توان نشان داد و داوری را باید دفاع کرد."),
        ],
    ),
    reading_item(
        ("Two ways to be misunderstood", "دو راه برای بد فهمیده شدن"),
        ("A translation can fail in two directions, and reviewers usually notice only one. The first failure is foreignisation: the text keeps its idioms, its chronology, its untranslatable jokes, and the reader is left outside a room where something is clearly happening. The second is domestication: everything is smoothed into the target language, the jokes are replaced with local ones, and the reader is comfortable inside a book that has quietly stopped being the book.\n\nCritics tend to punish the first and forgive the second, which is odd, because the second is the one that leaves no trace. A foreignised translation announces its difficulty on every page; you can argue with it. A domesticated one reads beautifully and gives you no way to know what was changed, since the evidence has been removed along with the difficulty.\n\nThe defence of domestication is that a translation is written for readers, not for scholars, and a reader who cannot follow a paragraph is not being served by fidelity. This is true, and it is also the argument that produces books in which everyone speaks like the reviewer. Fidelity and readability are not a binary; the interesting question is which specific losses a translator has decided to accept, and whether the decision is consistent.\n\nA translation worth arguing about usually shows its decisions. It keeps the joke that does not work and adds a note; it leaves a term untranslated after the first use, trusting the reader to build the meaning from context. These are not compromises between two poles but choices about where the difficulty should sit. The reviewer's job is not to award points for difficulty or for fluency. It is to say what was lost, what was gained, and whether the exchange was worth making.",
         "ترجمه می‌تواند در دو جهت شکست بخورد و منتقدان معمولاً فقط یکی را می‌بینند. شکست اول غریبه‌سازی است: متن اصطلاح‌ها، ترتیب زمانی و لطیفه‌های ترجمه‌نشدنی‌اش را نگه می‌دارد و خواننده بیرون اتاقی می‌ماند که آشکارا چیزی در آن رخ می‌دهد. شکست دوم بومی‌سازی است: همه‌چیز در زبان مقصد هموار می‌شود، لطیفه‌ها با لطیفه‌های محلی عوض می‌شوند و خواننده در کتابی راحت است که بی‌صدا از بودن آن کتاب دست کشیده.\n\nمنتقدان معمولاً اولی را تنبیه و دومی را می‌بخشند و این عجیب است، چون دومی همان است که اثری باقی نمی‌گذارد. ترجمهٔ غریبه‌ساز دشواری‌اش را در هر صفحه اعلام می‌کند و می‌توان با آن بحث کرد. ترجمهٔ بومی‌ساز زیبا خوانده می‌شود و هیچ راهی نمی‌دهد که بدانی چه عوض شد، چون شواهد همراه با دشواری برداشته شده‌اند.\n\nدفاع از بومی‌سازی این است که ترجمه برای خواننده نوشته می‌شود نه برای پژوهشگر و خواننده‌ای که از یک پاراگراف نمی‌گذرد با وفاداری خدمت نمی‌گیرد. این درست است و همان استدلالی است که کتاب‌هایی می‌سازد که در آن‌ها همه مثل خود منتقد حرف می‌زنند. وفاداری و روانی دوقطبی نیستند؛ پرسش جالب این است که مترجم کدام زیان‌های مشخص را پذیرفته و آیا تصمیمش یکدست است.\n\nترجمه‌ای که ارزش بحث دارد معمولاً تصمیم‌هایش را نشان می‌دهد. لطیفه‌ای را که کار نمی‌کند نگه می‌دارد و پانویس می‌گذارد؛ واژه‌ای را پس از نخستین کاربرد ترجمه‌نشده می‌گذارد و به خواننده اعتماد می‌کند که معنا را از بافت بسازد. این‌ها سازش میان دو قطب نیستند، انتخاب‌هایی دربارهٔ اینکه دشواری کجا بنشیند. کار منتقد دادن امتیاز برای دشواری یا روانی نیست. کارش این است که بگوید چه از دست رفت، چه به دست آمد و آیا این معاوضه می‌ارزید."),
        [
            mcq("Which failure leaves no trace, according to the text?", "به گفتهٔ متن کدام شکست اثری باقی نمی‌گذارد؟", ["foreignisation", "domestication", "both equally", "neither"], 1,
                "Smoothing removes the evidence along with the difficulty.", "هموارسازی شواهد را با دشواری برمی‌دارد."),
            mcq("What is the author's view of the fidelity/readability pair?", "نظر نویسنده دربارهٔ جفت وفاداری/روانی چیست؟", ["it is a strict binary", "it is not a binary; specific losses matter", "readability always wins", "fidelity always wins"], 1,
                "'Fidelity and readability are not a binary.'", "«وفاداری و روانی دوقطبی نیستند»."),
            mcq("What is the reviewer's task?", "کار منتقد چیست؟", ["to reward difficulty", "to state losses, gains and whether the exchange was worth it", "to prefer fluency", "to check the translator's notes"], 1,
                "The final sentence defines the task.", "جملهٔ آخر وظیفه را تعریف می‌کند."),
        ],
    ),
]

LISTENING = [
    listen("The figures are right; it's the question that's wrong. We measured how long people waited, not how long they thought they waited, and those are different numbers.",
       "What is the speaker's objection?", "اعتراض گوینده چیست؟", ["the figures are wrong", "the measure does not capture the experience", "the sample was small", "the question was unclear"], 1,
       "The measurement answers a different question from the one that matters.", "اندازه‌گیری به پرسشی دیگر پاسخ می‌دهد."),
    listen("I'd accept that the pilot was short. But the effect was in the same direction in all four sites, and a short pilot doesn't produce that by accident.",
       "How does the speaker handle the criticism?", "گوینده با نقد چگونه روبه‌رو می‌شود؟", ["rejects it entirely", "concedes it and counters with consistency", "changes the subject", "asks for more time"], 1,
       "The concession is followed by a counter-argument.", "امتیاز با استدلال متقابل دنبال می‌شود."),
    listen("Honestly, the reading of the data changed my mind. I came in expecting to argue for the delay and I can't defend it now.",
       "What has happened to the speaker's position?", "موضع گوینده چه شد؟", ["it hardened", "it changed because of the evidence", "it stayed the same", "it became unclear"], 1,
       "The evidence moved the position, and the speaker says so.", "شواهد موضع را جابه‌جا کرد و گوینده می‌گوید."),
    listen("There's a version of this that costs half as much and takes twice as long, and I'd rather have that argument in this room than in a year.",
       "What is the speaker asking for?", "گوینده چه می‌خواهد؟", ["a cheaper plan", "the trade-off debated now", "a one-year delay", "a larger budget"], 1,
       "They want the alternative argued before it is too late.", "می‌خواهد بدیل پیش از دیر شدن بحث شود."),
    listen("The problem with the report isn't that it's wrong. It's that four hundred pages of passive voice leave you unable to write to anyone about it.",
       "What is the criticism?", "نقد چیست؟", ["the report is inaccurate", "the report names nobody, so nobody can be asked", "the report is too short", "the report is unreadable"], 1,
       "Agency is missing, so accountability is missing.", "عامل غایب است، پس پاسخ‌گویی غایب است."),
    listen("We stopped calling it a consultation when we realised we had already decided. That's the finding I'd put first, and it isn't in the summary.",
       "What does the speaker say about the summary?", "گوینده دربارهٔ خلاصه چه می‌گوید؟", ["it is too long", "it omits the most important finding", "it is accurate", "it was never written"], 1,
       "The key finding is absent from the summary.", "یافتهٔ کلیدی از خلاصه غایب است."),
]

WRITING = [
    write("Write a proposal of about 150 words recommending whether a school should keep a four-day teaching week. State the criterion you judge by, compare two options (one is returning to five days), recommend one, and name the main risk.",
          "پیشنهادی حدود ۱۵۰ واژه بنویس و توصیه کن مدرسه هفتهٔ چهارروزهٔ آموزشی را نگه دارد یا نه. معیاری که با آن می‌سنجی را بگو، دو گزینه (یکی بازگشت به پنج روز) را مقایسه کن، یکی را توصیه کن و ریسک اصلی را نام ببر.",
          150, ["recommended", "whereas"],
          "Impersonal register, the subjunctive once, the recommendation before the detail, and a base for every figure.",
          "لحن بی‌شخص، یک بار وجه شرطی، توصیه پیش از جزئیات و پایه برای هر عدد."),
    write("Summarise in about 120 words an argument you have read recently. Keep its claim, its strongest support and the limitation it accepts, and attribute the position to its author rather than adopting it.",
          "استدلالی را که تازگی خوانده‌ای در حدود ۱۲۰ واژه خلاصه کن. ادعا، قوی‌ترین پشتوانه و محدودیتی که می‌پذیرد را نگه دار و موضع را به نویسنده‌اش نسبت بده، نه به خودت.",
          120, ["argues", "although"],
          "Four sentences: claim, support, limitation, evaluation. Attribute with a reporting verb.",
          "چهار جمله: ادعا، پشتوانه، محدودیت، ارزیابی. با فعل نقل نسبت بده."),
]

SPEAKING = [
    say("What strikes me about the proposal is not the cost but the assumption behind it: that demand will stay exactly where it is today.", "آنچه دربارهٔ پیشنهاد توجهم را جلب می‌کند هزینه نیست، فرض پشت آن است: اینکه تقاضا دقیقاً همان‌جا که امروز هست می‌ماند."),
    say("Building on that, I'd want to distinguish between the pilot and the policy that follows it.", "بر همان پایه، می‌خواهم بین آزمایش و سیاستی که پس از آن می‌آید تفکیک کنم."),
    say("Had the consultation happened six months earlier, we would be having a different conversation about the design.", "اگر مشورت شش ماه زودتر انجام شده بود، الان دربارهٔ طراحی گفت‌وگوی دیگری داشتیم."),
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
