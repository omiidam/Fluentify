#!/usr/bin/env python3
"""C1 · units 7-8: compression with participles, and the emphatic close.

Unit 7 compresses clauses and then puts the whole level under pressure in a
seminar, where the grammar has to survive being interrupted. Unit 8 is emphasis
at its most deliberate — inversion, comparatives that argue — and a critical
review that has to notice what a work is doing as well as what it says.
"""

from course_kit import dialogue, gap, lesson, mcq, passage, say, unit

U7 = unit(
    "c1-u7",
    ("Having said that", "با این اوصاف"),
    ("Compress clauses with participles, add relative nuance, and hold a seminar turn.", "بندها را با وجه وصفی فشرده کن، ظرافت موصولی بیفزا و نوبت سمینار را نگه دار."),
    [
        lesson(
            "c1-u7-l1",
            "grammar",
            ("Participle clauses and advanced relatives", "بندهای وجه وصفی و موصولی پیشرفته"),
            ("Carry cause, result and concession in a phrase, and qualify a noun with precision.", "علت، نتیجه و امتیاز را در یک عبارت حمل کن و اسم را با دقت مقید کن."),
            [
                ("A participle clause can carry a relationship that a conjunction would have to name: Having read the file, she changed her mind (time/cause). Faced with a choice, they deferred (circumstance). The reader infers the link, and the inference is usually unambiguous — but only when the participle's subject matches the main clause's.", "بند وجه وصفی می‌تواند رابطه‌ای را حمل کند که حرف ربط باید نامش می‌برد: Having read the file, she changed her mind (زمان/علت). Faced with a choice, they deferred (شرایط). خواننده پیوند را استنباط می‌کند و استنباط معمولاً بی‌ابهام است — اما فقط وقتی نهاد وجه وصفی با بند اصلی بخواند."),
                ("Perfect participles fix the order (Having finished, he left); present participles suggest simultaneity (Finishing the report, he noticed the error); past participles are passive (Written in haste, the note was unclear). Choosing the wrong one changes the timeline, which is the commonest error at this level.", "وجه وصفی کامل ترتیب را ثابت می‌کند (Having finished, he left)؛ وجه وصفی حال هم‌زمانی را می‌رساند (Finishing the report, he noticed the error)؛ وجه وصفی گذشته مجهول است (Written in haste, the note was unclear). انتخاب نادرست خط زمان را عوض می‌کند و این رایج‌ترین خطای این سطح است."),
                ("Advanced relatives add qualification without a new sentence: the report, the conclusions of which were disputed; a claim whose evidence has never been published; the period during which the policy was suspended. Preposition + which, of which/whose, and when/where after a time or place noun are the four forms worth automating.", "موصولی پیشرفته تقیید را بی جملهٔ تازه می‌افزاید: the report, the conclusions of which were disputed؛ a claim whose evidence has never been published؛ the period during which the policy was suspended. حرف اضافه + which، of which/whose و when/where پس از اسم زمان یا مکان چهار شکلی هستند که باید خودکار شوند."),
                ("Register note: stacked participles are the signature of academic prose ('Having established the criterion, and having applied it to both cases, the study concludes…'). One is elegant; three in a paragraph is a tic. C1 style means knowing the compression is available, not using it everywhere it fits.", "نکتهٔ لحن: وجه وصفی‌های پشت‌سرهم امضای نوشتار دانشگاهی‌اند («Having established the criterion, and having applied it to both cases, the study concludes…»). یکی ظریف است و سه تا در یک پاراگراف عادت. سبک C1 یعنی بدانی فشرده‌سازی هست، نه اینکه هر جا جا شد به کارش ببری."),
            ],
            [
                ("Having weighed both options, the committee chose the cheaper one.", "کمیته پس از سنجش هر دو گزینه ارزان‌تر را برگزید."),
                ("The study, the methods of which were criticized, has never been replicated.", "مطالعه‌ای که روش‌هایش نقد شد هرگز تکرار نشده است."),
                ("Faced with a deadline, teams reach for the first adequate answer.", "تیم‌ها در برابر مهلت به نخستین پاسخ قابل‌قبول می‌رسند."),
                ("The year during which the policy was suspended saw no improvement.", "سالی که سیاست معلق بود بهبودی ندید."),
            ],
            [
                mcq("Which participle shows the action happened first?", "کدام وجه وصفی نشان می‌دهد عمل اول رخ داد؟", ["Finishing the report", "Having finished the report", "Finished the report", "To finish the report"], 1,
                    "Perfect participle marks completion before the main clause.", "وجه وصفی کامل انجام پیش از بند اصلی را نشان می‌دهد."),
                mcq("'The report, the conclusions of which were disputed' is ___.", "«The report, the conclusions of which were disputed» ___ است.", ["a non-defining relative", "a defining relative", "a participle clause", "a cleft"], 0,
                    "Commas and added information make it non-defining.", "ویرگول و اطلاعات افزوده آن را توصیفی می‌کند."),
            ],
            [
                gap("___ (write) in 1890, the novel still reads as modern.", ["Written"], "Passive past participle.", "وجه وصفی گذشتهٔ مجهول."),
                gap("The period ___ which the funding was frozen lasted two years. (formal)", ["during"], "Preposition + which.", "حرف اضافه + which."),
                mcq("Which sentence has a dangling participle?", "کدام جمله وجه وصفی آویزان دارد؟", ["Having read the file, she changed her mind.", "Having read the file, the decision changed.", "Reading the file, she noticed an error.", "Written quickly, the note was unclear."], 1,
                    "The decision did not read the file.", "تصمیم پرونده را نخواند."),
                mcq("Too many participle clauses in one paragraph ___.", "وجه وصفی‌های زیاد در یک پاراگراف ___.", ["improve clarity", "read as a stylistic tic", "are ungrammatical", "shorten the text"], 1,
                    "Compression becomes mannerism.", "فشردگی به عادت تبدیل می‌شود."),
            ],
        ),
        lesson(
            "c1-u7-l2",
            "vocabulary",
            ("Psychology, relationships and motive", "روان‌شناسی، روابط و انگیزه"),
            ("Name a motive precisely, and describe behavior without diagnosing the person.", "انگیزه را دقیق نام ببر و رفتار را بی‌تشخیص دادن به شخص توصیف کن."),
            [
                ("Psychology vocabulary: a motive, an incentive, a bias, a heuristic, cognitive load, confirmation bias, loss aversion, a defense mechanism, an attachment, a trigger, resilience, burnout. These are technical terms with published meanings; using 'bias' for 'opinion' loses the precision that makes them useful.", "واژگان روان‌شناسی: motive، incentive، bias، heuristic، cognitive load، confirmation bias، loss aversion، defense mechanism، attachment، trigger، resilience، burnout. این‌ها اصطلاحات فنی با معانی منتشرشده‌اند؛ استفاده از «bias» به‌جای «opinion» همان دقتی را از دست می‌دهد که سودمندشان می‌کند."),
                ("Relationship vocabulary: mutual, reciprocal, one-sided, to confide in, to drift apart, to reconcile, to set a boundary, to take something personally, an unspoken expectation. 'Reciprocal' is the precise word for what 'mutual' often means loosely — mutual respect is shared, reciprocal effort is returned.", "واژگان روابط: mutual، reciprocal، one-sided، confide in، drift apart، reconcile، set a boundary، take something personally، unspoken expectation. «reciprocal» واژهٔ دقیق برای چیزی است که «mutual» اغلب سست می‌گوید — احترام متقابل مشترک است و تلاش دوسویه پاسخ‌داده."),
                ("Describing behavior without diagnosis: 'she withdrew from the discussion' rather than 'she was being passive-aggressive'; 'he avoided the question' rather than 'he is in denial'. The first kind of sentence can be checked against evidence; the second requires a clinical claim the speaker cannot support.", "توصیف رفتار بی تشخیص: «she withdrew from the discussion» به‌جای «she was being passive-aggressive»؛ «he avoided the question» به‌جای «he is in denial». جملهٔ نوع اول را می‌توان با شواهد سنجید و دومی ادعای بالینی می‌خواهد که گوینده از عهده‌اش برنمی‌آید."),
                ("Word formation and confusables: empathize / sympathy / empathy, insecure / unsure, anxious / eager, sensible / sensitive, to motivate / motivation / a motive. 'Anxious' is worry; 'eager' is enthusiasm — a distinction that changes the meaning of a whole sentence.", "ساخت واژه و اشتباه‌ها: empathize / sympathy / empathy، insecure / unsure، anxious / eager، sensible / sensitive، motivate / motivation / motive. «anxious» نگرانی است و «eager» شوق — تفاوتی که معنای کل جمله را عوض می‌کند."),
            ],
            [
                ("The resistance was less about the plan than about being consulted too late.", "مقاومت کمتر دربارهٔ طرح بود و بیشتر دربارهٔ دیر مشورت شدن."),
                ("Confirmation bias makes the first explanation the most attractive one.", "سوگیری تأییدی نخستین توضیح را جذاب‌ترین می‌کند."),
                ("They drifted apart without ever having an argument.", "بی آنکه هرگز بحثی کنند از هم دور شدند."),
                ("She set a boundary, and the team adjusted without drama.", "او مرزی گذاشت و تیم بی‌هیاهو خودش را تنظیم کرد."),
            ],
            [
                mcq("'Reciprocal' effort is effort that is ___.", "تلاش «reciprocal» تلاشی است که ___.", ["shared equally at once", "returned by the other side", "one-sided", "unspoken"], 1,
                    "It is given back, not merely shared.", "پاسخ داده می‌شود، نه فقط مشترک."),
                mcq("Which sentence avoids diagnosing?", "کدام جمله از تشخیص پرهیز می‌کند؟", ["He is in denial.", "He avoided the question twice.", "She is passive-aggressive.", "They have attachment issues."], 1,
                    "It reports observable behavior.", "رفتار قابل مشاهده را گزارش می‌کند."),
            ],
            [
                gap("Loss ___ explains why people keep a failing project alive.", ["aversion"], "The preference for avoiding loss.", "ترجیح پرهیز از زیان."),
                gap("I didn't mean to ___ it personally.", ["take"], "Take something personally.", "به خود گرفتن."),
                mcq("Which pair is not a synonym pair?", "کدام جفت هم‌معنا نیست؟", ["anxious / worried", "eager / keen", "sensible / reasonable", "sensitive / sensible"], 3,
                    "Sensitive means easily affected; sensible means reasonable.", "sensitive یعنی زوداثرپذیر و sensible یعنی معقول."),
                mcq("'Cognitive load' refers to ___.", "«Cognitive load» اشاره دارد به ___.", ["the amount of mental work a task requires", "a person's intelligence", "emotional strain", "physical tiredness"], 0,
                    "It is about the demand on working memory.", "دربارهٔ فشار بر حافظهٔ کاری است."),
            ],
        ),
        lesson(
            "c1-u7-l3",
            "speaking",
            ("The seminar: think aloud, then hand over", "سمینار: بلند فکر کن، بعد نوبت را بده"),
            ("Take a position in a discussion, build on another speaker, and manage the turn.", "در بحث موضع بگیر، بر گفتهٔ دیگری بساز و نوبت را مدیریت کن."),
            [
                ("A seminar turn has three jobs: take a position, connect it to what was just said, and leave an opening for the next speaker. The connection is what distinguishes a discussion from a series of monologues — 'building on what Sara said' is not politeness, it is the argument's structure.", "نوبت سمینار سه کار دارد: موضع گرفتن، وصل کردنش به آنچه همین حالا گفته شد، و باز گذاشتن دری برای گویندهٔ بعد. همین وصل کردن بحث را از زنجیرهٔ تک‌گویی جدا می‌کند — «building on what Sara said» تعارف نیست، ساختار استدلال است."),
                ("Thinking aloud is allowed and marks a strong speaker: 'I'm not sure I can defend that yet, but it seems to me…', 'let me test that against the second case'. The alternative — silence until certainty — reads as absence of thought rather than rigor.", "بلند فکر کردن مجاز است و گویندهٔ قوی را نشان می‌دهد: «I'm not sure I can defend that yet, but it seems to me…»، «let me test that against the second case». جایگزینش — سکوت تا قطعیت — غیبت اندیشه خوانده می‌شود، نه دقت."),
                ("Disagreeing with the idea while keeping the person intact: 'I'd put it differently', 'I think that understates the cost', 'the part I'd question is the second step'. Note that each names what is questioned; 'I disagree' names nothing and stops the exchange.", "مخالفت با ایده و سالم نگه داشتن شخص: «I'd put it differently»، «I think that understates the cost»، «the part I'd question is the second step». هر کدام چیزی را که زیر سؤال است نام می‌برند؛ «I disagree» چیزی را نام نمی‌برد و بحث را می‌بندد."),
                ("Handing over and reformulating: 'does that answer your question, or have I moved off it?', 'to put it more carefully', 'what I meant was narrower than that'. Reformulation is a C1 skill, not an admission of failure — it shows the speaker can hear their own sentence as the listener did.", "نوبت دادن و بازسازی: «does that answer your question, or have I moved off it?»، «to put it more carefully»، «what I meant was narrower than that». بازسازی مهارت C1 است، نه اعتراف به شکست — نشان می‌دهد گوینده می‌تواند جملهٔ خودش را آن‌طور که شنونده شنید بشنود."),
            ],
            [
                ("Building on what Sara said, I'd add that the timing matters as much as the design.", "بر پایهٔ گفتهٔ سارا اضافه می‌کنم که زمان‌بندی به‌اندازهٔ طراحی مهم است."),
                ("The part I'd question is the second step, not the aim.", "بخشی که زیر سؤال می‌برم مرحلهٔ دوم است، نه هدف."),
                ("Let me put that more carefully: I mean the pilot, not the policy.", "بگذار دقیق‌تر بگویم: منظورم آزمایش است، نه سیاست."),
                ("Does that answer your question, or have I moved off it?", "پاسخ پرسشت بود یا از آن دور شدم؟"),
            ],
            [
                mcq("What makes a seminar turn part of a discussion rather than a monologue?", "چه چیزی نوبت سمینار را از تک‌گویی جدا می‌کند؟", ["length", "connecting to the previous speaker", "using formal vocabulary", "agreeing"], 1,
                    "The connection is the structure.", "همان پیوند، ساختار است."),
                mcq("Which phrase disagrees precisely?", "کدام عبارت دقیق مخالفت می‌کند؟", ["I disagree.", "That's wrong.", "I think that understates the cost.", "No."], 2,
                    "It names what is understated.", "نام می‌برد چه چیزی کم‌گفته شده."),
            ],
            [
                say("I'd take a slightly different view: the evidence points to timing rather than design.", "من کمی متفاوت می‌بینم: شواهد به زمان‌بندی اشاره می‌کند، نه طراحی."),
                say("Building on that, I'd want to distinguish between the pilot and the policy.", "بر همان پایه، می‌خواهم بین آزمایش و سیاست تفکیک کنم."),
                say("I'm not sure I can defend that yet, but it seems to me the sample was too narrow.", "مطمئن نیستم بتوانم از آن دفاع کنم، اما به نظرم نمونه بیش از حد باریک بود."),
                say("Let me reformulate — I meant the second phase, not the whole program.", "بگذار بازسازی کنم — منظورم مرحلهٔ دوم بود، نه کل برنامه."),
            ],
            dialogue=dialogue([
                ("A", "I'd argue the reform failed because it was designed too quickly.", "استدلال می‌کنم اصلاح شکست خورد چون با شتاب طراحی شد."),
                ("B", "Building on that — though I'd put it differently. The design was fine; the consultation was too late.", "بر همان پایه — هرچند جور دیگری می‌گویم. طراحی خوب بود؛ مشورت دیر شد."),
                ("A", "The part I'd question is whether consultation would have changed the design.", "بخشی که زیر سؤال می‌برم این است که آیا مشورت طراحی را عوض می‌کرد."),
                ("B", "That's fair. Let me test it against the second branch, where consultation did happen.", "درست است. بگذار با شعبهٔ دوم بسنجمش که مشورت واقعاً انجام شد."),
            ]),
        ),
    ],
)

U8 = unit(
    "c1-u8",
    ("Never has it mattered more", "هرگز این‌قدر مهم نبوده"),
    ("Emphasize with inversion and comparatives that argue, then review a work critically.", "با جابه‌جایی و مقایسه‌های استدلالی تأکید کن و بعد اثری را نقد کن."),
    [
        lesson(
            "c1-u8-l1",
            "grammar",
            ("Inversion and emphatic comparison", "جابه‌جایی و مقایسهٔ تأکیدی"),
            ("Build the formal emphatic sentence, and compare in a way that carries an argument.", "جملهٔ تأکیدی رسمی بساز و طوری مقایسه کن که استدلال حمل کند."),
            [
                ("Fronted negatives invert as they do at B2, but C1 adds the concessive and conditional inversions: Had I known, I would have acted (if I had known); Should the committee disagree, the decision stands (if the committee disagrees); Were it not for the funding, the trial would have continued. These are formal, and they are common in correspondence and reports.", "منفی‌های مقدماتی همچنان که در B2 جابه‌جا می‌شدند جابه‌جا می‌شوند، اما C1 جابه‌جایی امتیازی و شرطی را می‌افزاید: Had I known, I would have acted (اگر می‌دانستم)؛ Should the committee disagree, the decision stands (اگر کمیته مخالف باشد)؛ Were it not for the funding, the trial would have continued. این‌ها رسمی‌اند و در مکاتبات و گزارش‌ها رایج."),
                ("Emphatic comparison is a rhetorical instrument, not decoration: far from settling the question, the report widens it; no less important is the effect on staff; the more precisely the target is defined, the easier it is to miss. The last is a double comparative and it argues by proportion rather than by assertion.", "مقایسهٔ تأکیدی ابزار بلاغی است، نه تزئین: far from settling the question, the report widens it؛ no less important is the effect on staff؛ the more precisely the target is defined, the easier it is to miss. آخری مقایسهٔ دوگانه است و به‌جای ادعا با تناسب استدلال می‌کند."),
                ("'Far from' + -ing reverses an expectation in one move: far from reducing costs, the merger increased them. 'Nothing less than', 'no more than', 'little short of' are graded intensifiers; each carries an evaluation, so none of them is neutral reporting.", "«far from» + ing انتظار را در یک حرکت وارونه می‌کند: far from reducing costs, the merger increased them. «nothing less than»، «no more than»، «little short of» تشدیدکننده‌های درجه‌بندی‌شده‌اند؛ هر کدام ارزش‌گذاری دارند، پس هیچ‌کدام گزارش خنثی نیستند."),
                ("Register caution: inversion is a formal resource, and in speech it sounds literary or ironic. The same emphasis in conversation is carried by stress and by 'what… is'. A C1 speaker knows both forms and chooses by setting, which is the whole point of having them.", "احتیاط لحن: جابه‌جایی منبعی رسمی است و در گفتار ادبی یا طنزآمیز به گوش می‌رسد. همان تأکید در گفت‌وگو با تکیه و «what… is» حمل می‌شود. گویندهٔ C1 هر دو شکل را می‌داند و بر پایهٔ موقعیت انتخاب می‌کند و همین کل نکتهٔ داشتنشان است."),
            ],
            [
                ("Had the funding arrived in March, the study would have finished.", "اگر بودجه در مارس رسیده بود، مطالعه تمام می‌شد."),
                ("Should you need an extension, apply in writing.", "اگر به تمدید نیاز داشتید، کتبی درخواست دهید."),
                ("Far from resolving the dispute, the ruling deepened it.", "حکم به‌جای حل اختلاف آن را عمیق‌تر کرد."),
                ("The closer the deadline came, the less anyone was willing to decide.", "هر چه مهلت نزدیک‌تر می‌شد، کمتر کسی حاضر به تصمیم بود."),
            ],
            [
                mcq("'Should the committee disagree' means ___.", "«Should the committee disagree» یعنی ___.", ["the committee disagreed", "if the committee disagrees", "the committee must disagree", "the committee should have disagreed"], 1,
                    "Fronted should replaces if in formal conditionals.", "should در آغاز در شرطی رسمی جای if می‌آید."),
                mcq("'Far from' typically introduces ___.", "«Far from» معمولاً ___ را معرفی می‌کند.", ["supporting evidence", "a reversed expectation", "a definition", "a conclusion"], 1,
                    "It says the opposite of what was expected.", "خلاف انتظار را می‌گوید."),
            ],
            [
                gap("___ it not for the volunteers, the archive would have closed.", ["Were"], "Were it not for = if it were not for.", "Were it not for یعنی اگر ... نبود."),
                gap("The more data we collected, the ___ confident we became about the trend.", ["less", "more"], "Double comparative: the more… the less…", "مقایسهٔ دوگانه: the more… the less…"),
                mcq("Which sentence uses inversion correctly?", "کدام جمله جابه‌جایی را درست به کار برده است؟", ["Had I knew, I would have acted.", "Had I known, I would have acted.", "I had known, would I have acted.", "Had known I, I would act."], 1,
                    "Had + past participle, then the result clause.", "had + اسم مفعول و بعد بند نتیجه."),
                mcq("Where does inversion sound out of place?", "جابه‌جایی کجا نامناسب به گوش می‌رسد؟", ["a formal letter", "a legal notice", "a chat with a friend", "a report"], 2,
                    "In speech it reads as literary or ironic.", "در گفتار ادبی یا طنزآمیز خوانده می‌شود."),
            ],
        ),
        lesson(
            "c1-u8-l2",
            "vocabulary",
            ("Arts, literature and critical vocabulary", "هنر، ادبیات و واژگان نقد"),
            ("Evaluate a work with terms that describe technique rather than taste.", "اثری را با واژه‌هایی بسنج که فن را توصیف کنند، نه سلیقه را."),
            [
                ("Critical vocabulary: a motif, a trope, an idiom, a register, a narrator, a persona, a subtext, an allusion, a juxtaposition, an arc, pacing, a conceit. These let a review say how a work is built; 'beautiful' and 'boring' say only how the reviewer felt.", "واژگان نقد: motif، trope، idiom، register، narrator، persona، subtext، allusion، juxtaposition، arc، pacing، conceit. این‌ها می‌گویند اثر چگونه ساخته شده؛ «beautiful» و «boring» فقط حس منتقد را می‌گویند."),
                ("Evaluation with reasons attached: the prose is restrained to the point of withholding; the structure promises a resolution it declines to deliver; the humor depends on a register the translation cannot carry. Each is a judgment with its mechanism visible, which is what makes it arguable.", "ارزش‌گذاری با دلیل پیوسته: the prose is restrained to the point of withholding؛ the structure promises a resolution it declines to deliver؛ the humor depends on a register the translation cannot carry. هر کدام داوری‌ای است با سازوکار آشکار و همین قابل بحثش می‌کند."),
                ("Distinguishing the work from its reception: 'the novel was read as a political allegory' is not 'the novel is an allegory'. Reviews that blur the two end up arguing with readers instead of with the book. 'Read as', 'taken as', 'received as' keep the distinction available.", "تفکیک اثر از دریافتش: «the novel was read as a political allegory» همان «the novel is an allegory» نیست. نقدهایی که این دو را یکی می‌کنند در نهایت با خوانندگان بحث می‌کنند، نه با کتاب. «read as»، «taken as»، «received as» این تفکیک را نگه می‌دارند."),
                ("Word formation and confusables: irony / sarcasm (irony need not wound), a critic / critical / criticism / critique (a critique is a systematic analysis), literal / literary, artistic / artful (artful can mean cunning), pretentious / ambitious. The last pair is where reviews do the most damage.", "ساخت واژه و اشتباه‌ها: irony / sarcasm (طعنه لازم نیست زخم بزند)، critic / critical / criticism / critique (critique تحلیلی نظام‌مند است)، literal / literary، artistic / artful (artful می‌تواند به معنای مکار باشد)، pretentious / ambitious. جفت آخر جایی است که نقدها بیشترین آسیب را می‌زنند."),
            ],
            [
                ("The novel's central motif is a door that is never opened.", "بن‌مایهٔ اصلی رمان دری است که هرگز باز نمی‌شود."),
                ("The pacing is deliberate: the first hundred pages refuse to advance.", "ضرب‌آهنگ آگاهانه است: صد صفحهٔ نخست پیش نمی‌رود."),
                ("The movie was received as a comedy, which its director disputes.", "فیلم به‌عنوان کمدی دریافت شد و کارگردانش این را رد می‌کند."),
                ("The critique is of the adaptation, not of the novel.", "نقد بر اقتباس است، نه بر رمان."),
            ],
            [
                mcq("Which word describes how a work is built rather than how it felt?", "کدام واژه ساخت اثر را توصیف می‌کند، نه حس را؟", ["boring", "pacing", "beautiful", "disappointing"], 1,
                    "Pacing is a structural property.", "ضرب‌آهنگ ویژگی ساختاری است."),
                mcq("A 'critique' is ___.", "«critique» ___ است.", ["a complaint", "a systematic analysis", "a summary", "a review of a review"], 1,
                    "It analyses rather than complains.", "تحلیل می‌کند، نه شکایت."),
            ],
            [
                gap("The humor depends on a ___ that the translation cannot carry.", ["register"], "A level of formality or tone.", "سطح رسمیت یا لحن."),
                gap("The poem is usually read ___ an elegy.", ["as"], "Read something as something.", "چیزی را چیزی خواندن."),
                mcq("'Artful' can carry the sense of ___.", "«Artful» می‌تواند معنای ___ را داشته باشد.", ["cunning", "beautiful", "expensive", "simple"], 0,
                    "It can mean skillfully deceptive.", "می‌تواند به معنای فریب ماهرانه باشد."),
                mcq("Which distinction does 'the novel was read as an allegory' protect?", "«The novel was read as an allegory» کدام تفکیک را حفظ می‌کند؟", ["author and narrator", "work and reception", "irony and sarcasm", "literal and literary"], 1,
                    "It reports an interpretation, not a property.", "تفسیر را گزارش می‌کند، نه ویژگی را."),
            ],
        ),
        lesson(
            "c1-u8-l3",
            "reading",
            ("The review that argues with the work", "نقدی که با اثر بحث می‌کند"),
            ("Read a critical review for its criteria, and separate judgment from evidence.", "نقدی را برای معیارهایش بخوان و داوری را از شواهد جدا کن."),
            [
                ("A review argues two things at once: what the work is doing (description) and whether it succeeds (evaluation). Confusing the two is the standard weakness — a reviewer who disliked the aim will report it as a failure of execution.", "نقد هم‌زمان دو چیز را استدلال می‌کند: اثر چه می‌کند (توصیف) و آیا موفق است (ارزش‌گذاری). یکی گرفتن این دو ضعف استاندارد است — منتقدی که هدف را نپسندیده آن را شکست اجرا گزارش می‌کند."),
                ("Every evaluation implies a criterion; a strong review states it. 'The book is too long' is taste until the reviewer adds 'for a argument that could be made in a third of the pages'. After that sentence the judgment can be tested, and a reader who disagrees knows exactly what they are disagreeing with.", "هر ارزش‌گذاری معیاری را مفروض می‌گیرد و نقد قوی آن را می‌گوید. «The book is too long» سلیقه است تا وقتی منتقد بیفزاید «for an argument that could be made in a third of the pages». پس از آن جمله داوری آزمون‌پذیر می‌شود و خواننده‌ای که مخالف است دقیقاً می‌داند با چه مخالف است."),
                ("Quote sparingly and quote exactly. One short quotation that carries the claim does more than four that establish the reviewer read the book. Paraphrase is where interpretation shows; quotation is where it gets checked.", "کم نقل کن و دقیق نقل کن. یک نقل کوتاه که ادعا را حمل کند بیشتر از چهار نقلی است که نشان دهد منتقد کتاب را خوانده. بازگویی جایی است که تفسیر خودش را نشان می‌دهد و نقل جایی که بررسی می‌شود."),
                ("A review needs a reader in mind: 'for anyone who has read the earlier books' is not a marketing line, it is a criterion of relevance. The same novel can be ambitious and unnecessary depending on who is being addressed, and saying so is more honest than a verdict without a reader.", "نقد خواننده‌ای در ذهن دارد: «for anyone who has read the earlier books» جملهٔ تبلیغاتی نیست، معیاری از مربوط بودن است. همان رمان بسته به مخاطب می‌تواند جسورانه یا بی‌لزوم باشد و گفتنش از حکمی بی‌مخاطب صادقانه‌تر است."),
            ],
            [
                ("The aim is modest and the execution is exact.", "هدف کوچک است و اجرا دقیق."),
                ("It is too long for an argument that could be made in a third of the pages.", "برای استدلالی که در یک‌سوم صفحه‌ها هم گفته می‌شد، بلند است."),
                ("Read as a sequel, it is generous; read alone, it assumes too much.", "اگر دنباله خوانده شود سخاوتمند است و اگر تنها خوانده شود بیش از حد فرض می‌گیرد."),
            ],
            [
                mcq("What does a strong review state that a weak one leaves implicit?", "نقد قوی چه چیزی را می‌گوید که نقد ضعیف مبهم می‌گذارد؟", ["its criterion", "the price", "the author's biography", "the publisher"], 0,
                    "Without a criterion the judgment is taste.", "بی معیار، داوری سلیقه است."),
                mcq("Why quote sparingly?", "چرا کم نقل کنیم؟", ["space is limited", "one exact quotation is checkable and sufficient", "quotations are unreliable", "readers skip them"], 1,
                    "Interpretation shows in paraphrase, precision in quotation.", "تفسیر در بازگویی و دقت در نقل دیده می‌شود."),
            ],
            [
                mcq("What does the review praise most?", "نقد بیش از همه چه را می‌ستاید؟", ["the plot", "the handling of time across decades", "the characters", "the ending"], 1,
                    "The transitions between decades are the strength.", "گذارهای میان دهه‌ها قوت کار است."),
                mcq("What is the stated weakness?", "ضعف گفته‌شده چیست؟", ["the narrator is unreliable", "the delay outweighs what is revealed", "the ending is missing", "the language is simple"], 1,
                    "'It is smaller than the delay.'", "«کوچک‌تر از تأخیر است»."),
                mcq("What criterion does the review use for length?", "نقد برای طول چه معیاری به کار می‌برد؟", ["page count alone", "whether the withholding earns its space", "the publisher's limit", "the trilogy's length"], 1,
                    "Technique versus mannerism is the test.", "فن در برابر عادت، همان آزمون است."),
            ],
            passage=passage(("A generous book with a narrow door", "کتابی سخاوتمند با دری باریک"),
                                    ("There is a kind of novel that treats the reader as a guest who has been in the house before. It does not explain the family, the town or the feud; it assumes you remember, and it begins in the middle of an argument that started two books ago. Nader's new novel is that kind, and whether you find it masterly or exasperating will be decided in the first twenty pages, before you have any evidence.\n\nWhat the book does superbly is time. Its four sections cover a single afternoon, and within that afternoon it moves between 1979, 1994 and a future that the characters discuss but do not reach. The transitions are managed without a single scene break: a sentence about a kettle becomes a sentence about a curfew, and the reader is in another decade before noticing. This is difficult to do once; Nader does it forty times, and only twice does the machinery show.\n\nThe weakness is the same as the strength, taken too far. Because nothing is explained, the middle section depends entirely on the reader's patience with a narrator who is withholding something we are told, in the first paragraph, that he will eventually say. He does say it, on page two hundred and eleven, and it is smaller than the delay. A shorter book would have made the withholding a technique rather than a mannerism — a hundred pages less, and the silence would have had weight.\n\nNone of this will trouble the readers this book was written for, and it is not a small audience: anyone who has followed the trilogy will find the last section a genuine gift, and the final page does something the earlier books only promised. For a new reader, though, the door is narrow and the book does not hold it open. That is a decision, not an accident, and it should be described as one: this is a generous book with a narrow door, and it has chosen whom to be generous to.",
                                    "نوعی رمان هست که با خواننده مانند مهمانی رفتار می‌کند که پیش‌تر در این خانه بوده. خانواده، شهر یا کینه را توضیح نمی‌دهد؛ فرض می‌کند یادت هست و در میانهٔ بحثی شروع می‌کند که دو کتاب پیش آغاز شده. رمان تازهٔ نادر از این نوع است و اینکه آن را استادانه یا آزاردهنده بیابی در بیست صفحهٔ اول روشن می‌شود، پیش از آنکه شواهدی داشته باشی.\n\nچیزی که کتاب در آن عالی است زمان است. چهار بخشش یک بعدازظهر را در بر می‌گیرد و در همان بعدازظهر میان ۱۹۷۹، ۱۹۹۴ و آینده‌ای که شخصیت‌ها درباره‌اش حرف می‌زنند اما به آن نمی‌رسند حرکت می‌کند. گذارها بی یک شکست صحنه انجام می‌شود: جمله‌ای دربارهٔ کتری به جمله‌ای دربارهٔ منع رفت‌وآمد تبدیل می‌شود و خواننده پیش از آنکه متوجه شود در دههٔ دیگری است. این کار یک بار سخت است؛ نادر چهل بار انجامش می‌دهد و فقط دو بار ماشین کار پیداست.\n\nضعف همان قوت است که بیش از حد رفته. چون هیچ چیز توضیح داده نمی‌شود، بخش میانی کاملاً به صبر خواننده با راوی‌ای وابسته است که چیزی را پنهان می‌کند که در پاراگراف اول به ما گفته می‌شود سرانجام خواهد گفت. می‌گوید، در صفحهٔ دویست‌ویازده، و کوچک‌تر از تأخیر است. کتابی کوتاه‌تر پنهان‌کاری را از عادت به فن تبدیل می‌کرد — صد صفحه کمتر و سکوت وزن می‌داشت.\n\nهیچ‌کدام از این‌ها خوانندگانی را که کتاب برایشان نوشته نشد آزار نمی‌دهد و مخاطبش کوچک نیست: هر کس سه‌گانه را دنبال کرده باشد بخش آخر را هدیه‌ای واقعی می‌یابد و صفحهٔ آخر کاری می‌کند که کتاب‌های پیشین فقط وعده‌اش را داده بودند. اما برای خوانندهٔ تازه در باریک است و کتاب بازش نگه نمی‌دارد. این تصمیم است، نه تصادف، و باید همین‌طور توصیف شود: کتابی سخاوتمند با دری باریک که خودش انتخاب کرده به چه کسی سخاوت کند.")),
        ),
    ],
)
