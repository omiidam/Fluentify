#!/usr/bin/env python3
"""B2 · units 3-4: what would have been, and what is done to us.

Unit 3 adds the third and mixed conditionals, the forms for regret about a past
that cannot change; unit 4 turns to the passive across tenses and the reporting
passives that newspapers live on.
"""

from course_kit import gap, lesson, listen, mcq, passage, unit

U3 = unit(
    "b2-u3",
    ("Had I known", "اگر می‌دانستم"),
    ("Regret, imagine and criticize with the third and mixed conditionals.", "با شرطی سوم و مختلط حسرت بخور، خیال کن و نقد کن."),
    [
        lesson(
            "b2-u3-l1",
            "grammar",
            ("Third and mixed conditionals, wish and if only", "شرطی سوم و مختلط، wish و if only"),
            ("Talk about an unreal past, its unreal present result — and the regret it leaves.", "دربارهٔ گذشته‌ای غیرواقعی، نتیجهٔ غیرواقعی‌اش در حال و افسوسش حرف بزن."),
            [
                ("Third conditional: if + had + participle, would have + participle. Both halves are past and both are unreal — the condition did not happen: if I had left earlier, I would have caught the train. Nothing here is possible now; the sentence is an autopsy.", "شرطی سوم: if + had + اسم مفعول، would have + اسم مفعول. هر دو نیمه گذشته و غیرواقعی‌اند؛ شرط رخ نداده است: if I had left earlier, I would have caught the train. هیچ چیز اینجا دیگر ممکن نیست؛ جمله کالبدشکافی است."),
                ("Mixed conditional, past condition and present result: if I had studied medicine, I would be a doctor now. The if-clause is past perfect, the result is would + plain verb, and 'now' marks the shift.", "شرطی مختلط با شرط گذشته و نتیجهٔ حال: if I had studied medicine, I would be a doctor now. بند if گذشتهٔ کامل و نتیجه would + فعل ساده است و «now» تغییر را نشان می‌دهد."),
                ("The other mix, present condition and past result, is used for a permanent trait explaining an event: if he weren't so impatient, he wouldn't have resigned. The trait is true now; the resignation is over.", "مختلط دیگر با شرط حال و نتیجهٔ گذشته، برای ویژگی دائمی که رویدادی را توضیح می‌دهد: if he weren't so impatient, he wouldn't have resigned. ویژگی الان درست است و استعفا گذشته."),
                ("Could have and might have soften the result: if we had booked earlier, we might have paid less. Should have + participle is regret with a criticism built in: you should have told me — I would have helped.", "could have و might have نتیجه را نرم می‌کنند: if we had booked earlier, we might have paid less. should have + اسم مفعول حسرتی است که نقد در آن هست: you should have told me — I would have helped."),
                ("Formal inversion drops if and inverts had: Had I known, I would have come. It is the same sentence with the same meaning, and it belongs in writing, not in speech.", "وارونگی رسمی if را حذف و had را جابه‌جا می‌کند: Had I known, I would have come. همان جمله با همان معنا و جای آن در نوشتار است، نه گفتار."),
                ("Wish and if only use the same unreal past: I wish I had taken the job; if only we had left earlier. The past perfect marks a regret that cannot now be changed, while wish + past simple marks a present state the speaker wants different (I wish I had more time), and wish + would marks someone else's behavior with irritation (I wish he would stop calling).", "wish و if only همان گذشتهٔ غیرواقعی را می‌گیرند: I wish I had taken the job؛ if only we had left earlier. ماضی بعید افسوسی را نشان می‌دهد که دیگر تغییرپذیر نیست، wish + گذشتهٔ ساده وضعیتی در حال را که گوینده دیگر می‌خواهد (I wish I had more time) و wish + would رفتار دیگری را با آزردگی (I wish he would stop calling)."),
            ],
            [
                ("If we had left ten minutes earlier, we would have missed the traffic.", "اگر ده دقیقه زودتر راه افتاده بودیم، به ترافیک نمی‌خوردیم."),
                ("If she had taken the job, she would be living in Berlin now.", "اگر آن کار را گرفته بود، الان در برلین زندگی می‌کرد."),
                ("If I were more organized, I wouldn't have forgotten the deadline.", "اگر منظم‌تر بودم، مهلت را فراموش نمی‌کردم."),
                ("Had I known you were coming, I would have cooked something.", "اگر می‌دانستم می‌آیی، چیزی می‌پختم."),
                ("You should have asked; we could have shared a taxi.", "باید می‌پرسیدی؛ می‌توانستیم تاکسی را شریک شویم."),
                ("I wish I had kept the receipt.", "ای کاش رسید را نگه داشته بودم."),
                ("If only the train were less crowded.", "ای کاش قطار کم‌جمعیت‌تر بود."),
            ],
            [
                mcq("If I had seen the email, I ___ immediately.", "اگر ایمیل را دیده بودم، فوراً ___ .", ["would reply", "would have replied", "replied", "will reply"], 1,
                    "Both halves are unreal past: would have + participle.", "هر دو نیمه گذشتهٔ غیرواقعی است: would have + اسم مفعول."),
                mcq("If he had saved more, he ___ an apartment now.", "اگر بیشتر پس‌انداز کرده بود، الان ___ آپارتمان.", ["would buy", "would own", "would have bought", "bought"], 1,
                    "A present result after a past condition takes would + plain verb.", "نتیجهٔ حال پس از شرط گذشته با would + فعل ساده می‌آید."),
            ],
            [
                gap("If we ___ (not / miss) the turning, we would have arrived on time.", ["hadn't missed", "had not missed"], "Third conditional: had not + participle.", "شرطی سوم: had not + اسم مفعول."),
                gap("___ I known about the strike, I would have stayed home.", ["Had"], "Inverted third conditional.", "شرطی سوم وارونه."),
                gap("If she ___ (be) taller, she would have passed the medical.", ["had been"], "Third conditional with be.", "شرطی سوم با be."),
                mcq("Which sentence is a mixed conditional?", "کدام جمله شرطی مختلط است؟", ["If it rains, we'll stay in.", "If I had known, I would have called.", "If I had trained as a teacher, I would be working in a school now.", "If I were you, I'd apply."], 2,
                    "Past condition, present result.", "شرط گذشته و نتیجهٔ حال."),
                gap("If only I ___ (know) how expensive it would be.", ["had known"], "A past regret takes if only + past perfect.", "افسوس گذشته if only + ماضی بعید می‌گیرد."),
            ],
        ),
        lesson(
            "b2-u3-l2",
            "vocabulary",
            ("Science, innovation and the words of evidence", "علم، نوآوری و واژه‌های شواهد"),
            ("Discuss a study, a discovery and a claim that overreaches.", "دربارهٔ یک پژوهش، یک کشف و ادعایی که از شواهد جلو می‌زند بحث کن."),
            [
                ("Research verbs are precise: conduct or carry out a study, test a hypothesis, gather data, analyze results, replicate a finding, publish in a journal, peer-review it. A sample is the group studied; a sample size decides how much a result can carry.", "فعل‌های پژوهش دقیق‌اند: conduct/carry out a study، test a hypothesis، gather data، analyze results، replicate a finding، publish in a journal، peer-review. sample گروه بررسی‌شده است و حجم نمونه تعیین می‌کند نتیجه چقدر می‌تواند حمل شود."),
                ("Evidence has degrees, and the verbs mark them: suggests, indicates, shows, proves. 'Suggests' is the weakest and the most common in careful writing; 'proves' is rare outside mathematics. Correlation is not causation is the sentence to keep.", "شواهد درجه دارد و فعل‌ها آن را نشان می‌دهند: suggests، indicates، shows، proves. «suggests» ضعیف‌ترین و در نوشتار دقیق رایج‌ترین است؛ «proves» بیرون از ریاضیات کم است. «همبستگی علیت نیست» جمله‌ای است که باید یادت بماند."),
                ("Innovation vocabulary: a breakthrough, a prototype, a patent, a trial, to scale up, to roll out, to be commercially viable. 'Cutting-edge' describes the frontier; 'state-of-the-art' describes the best available; 'emerging' describes what is not settled yet.", "واژگان نوآوری: breakthrough، prototype، patent، trial، scale up، roll out، commercially viable. «cutting-edge» مرز دانش را می‌گوید، «state-of-the-art» بهترین موجود و «emerging» چیزی که هنوز تثبیت نشده."),
                ("Hedging is a skill, not weakness: the findings suggest, it appears that, this may be explained by, further research is needed. A claim without a hedge in a popular article is usually a claim the researchers did not make.", "محتاط بودن مهارت است، نه ضعف: the findings suggest، it appears that، this may be explained by، further research is needed. ادعای بی‌احتیاط در مقالهٔ عمومی معمولاً ادعایی است که پژوهشگران نکرده‌اند."),
            ],
            [
                ("The team carried out a trial with six hundred participants.", "تیم آزمایشی با ششصد شرکت‌کننده انجام داد."),
                ("The results suggest a link, but they do not prove one.", "نتایج به ارتباطی اشاره می‌کند، اما آن را اثبات نمی‌کند."),
                ("The prototype worked in the lab; scaling it up is the hard part.", "نمونهٔ اولیه در آزمایشگاه کار کرد؛ بزرگ‌کردن مقیاس بخش سخت است."),
                ("Further research is needed before any recommendation is made.", "پیش از هر توصیه‌ای پژوهش بیشتری لازم است."),
            ],
            [
                mcq("Which verb is the weakest claim?", "کدام فعل ضعیف‌ترین ادعاست؟", ["proves", "shows", "suggests", "demonstrates"], 2,
                    "'Suggests' leaves the most room.", "«suggests» بیشترین جای تردید را می‌گذارد."),
                mcq("A first working model is a ___.", "نخستین نمونهٔ کارکننده ___ است.", ["patent", "prototype", "sample", "journal"], 1,
                    "The prototype is the first build.", "prototype نخستین ساخت است."),
            ],
            [
                gap("The study ___ out over three years in four hospitals.", ["was carried", "carried"], "Carry out a study; passive is common.", "carry out a study و مجهول آن رایج است."),
                gap("The results ___ that the drug reduces pain, but more work is needed.", ["suggest", "indicate"], "A careful claim takes suggest or indicate.", "ادعای محتاط suggest یا indicate می‌گیرد."),
                mcq("'Correlation is not causation' means ___.", "«Correlation is not causation» یعنی ___.", ["two things happening together does not mean one causes the other", "statistics are unreliable", "causation cannot be studied", "correlation is always wrong"], 0,
                    "The pair of words is the whole point.", "همان دو واژه تمام نکته است."),
                mcq("'To roll out' a product means ___.", "«To roll out» یک محصول یعنی ___.", ["to design it", "to launch it gradually to users", "to withdraw it", "to patent it"], 1,
                    "Rollout is a staged launch.", "rollout عرضهٔ مرحله‌ای است."),
            ],
        ),
        lesson(
            "b2-u3-l3",
            "reading",
            ("Should cities ban cars from the center?", "آیا شهرها باید ماشین را از مرکز منع کنند؟"),
            ("Read a for-and-against essay and identify the position the writer finally takes.", "مقالهٔ موافق و مخالف را بخوان و موضع نهایی نویسنده را پیدا کن."),
            [
                ("A for-and-against essay is not neutral by accident: it usually presents both sides fairly, then commits in the last paragraph. The commitment is often marked by 'on balance', 'the stronger case', 'what matters most' — read for that phrase.", "مقالهٔ موافق و مخالف تصادفی بی‌طرف نیست: دو طرف را منصفانه می‌آورد و در پاراگراف آخر موضع می‌گیرد. موضع اغلب با «on balance»، «the stronger case»، «what matters most» نشان داده می‌شود؛ دنبال همان عبارت باش."),
                ("Weigh the two sides by their reasons, not by their length. If one side gets three paragraphs of evidence and the other gets one rhetorical question, the writer has already chosen, whatever the introduction promised.", "دو طرف را با دلیل‌هایشان بسنج، نه با طولشان. اگر یک طرف سه پاراگراف شواهد و طرف دیگر یک پرسش بلاغی دارد، نویسنده هرچه در مقدمه گفته باشد انتخاب کرده است."),
            ],
            [
                ("For: 'traffic is the single largest source of nitrogen dioxide in the centre'.", "موافق: «ترافیک بزرگ‌ترین منبع دی‌اکسید نیتروژن در مرکز است»."),
                ("Against: 'shops on the edge of the zone reported a fall in takings'.", "مخالف: «مغازه‌های حاشیهٔ محدوده از کاهش فروش گفتند»."),
                ("Commitment: 'on balance, the health of residents outweighs a two-year adjustment for business'.", "موضع: «در مجموع، سلامت ساکنان از دو سال سازگاری کسب‌وکارها سنگین‌تر است»."),
            ],
            [
                mcq("What is the writer's final position?", "موضع نهایی نویسنده چیست؟", ["cars should be allowed everywhere", "the ban is justified despite the cost to business", "the evidence is equal", "the ban should be postponed indefinitely"], 1,
                    "'The health of residents outweighs…' is the commitment.", "«سلامت ساکنان سنگین‌تر است» همان موضع است."),
                mcq("Which argument does the writer treat most seriously?", "نویسنده کدام استدلال را جدی‌تر می‌گیرد؟", ["the health of residents", "the freedom of drivers", "the cost to shops", "the noise of buses"], 1,
                    "The health evidence gets the data and the closing weight.", "شواهد سلامت داده و وزن پایانی را می‌گیرد."),
            ],
            [
                mcq("How is the counter-argument introduced?", "استدلال مخالف چطور معرفی می‌شود؟", ["with a rhetorical question and a shop owner's figures", "with a scientific study", "with a personal story", "with no evidence"], 0,
                    "A question plus reported takings is the counter's support.", "یک پرسش و آمار فروش، پشتیبانی مخالف است."),
                mcq("Which phrase marks the conclusion?", "کدام عبارت نتیجه را نشان می‌دهد؟", ["To begin with", "On the other hand", "On balance", "For instance"], 2,
                    "'On balance' announces the verdict.", "«On balance» حکم را اعلام می‌کند."),
                mcq("What does the writer concede?", "نویسنده چه چیزی را می‌پذیرد؟", ["that the ban has no effect", "that some businesses lost money", "that buses are worse", "that residents disagree"], 1,
                    "The fall in takings is conceded, then weighed.", "کاهش فروش پذیرفته و بعد سنجیده می‌شود."),
                mcq("The essay's tone is ___.", "لحن مقاله ___ است.", ["angry and personal", "measured and argumentative", "humorous", "purely descriptive"], 1,
                    "Both sides are stated in the same register.", "هر دو طرف با یک لحن گفته می‌شوند."),
            ],
            passage=passage(("Should cities ban cars from the center?", "آیا شهرها باید ماشین را از مرکز منع کنند؟"),
                            ("Few urban policies divide a city as quickly as a car ban. Supporters point to the air, opponents to the tills, and both are describing the same street.\n\nThe case for a ban rests on a measurement. Traffic is the single largest source of nitrogen dioxide in most city centers, and the health effects fall hardest on the people who live there rather than the people who drive through. Where a zone has been introduced, NO₂ has fallen by between a quarter and a third within two years, and cycling has risen more than the forecasts predicted.\n\nThe case against is not only about convenience. Shops on the edge of one zone reported a fall in takings of about 8% in the first year, and delivery firms passed their extra costs to customers. A ban also assumes that the people who lose most — small traders, drivers on low incomes — can absorb the change.\n\nOn balance, the health of residents outweighs a two-year adjustment for business, largely because the alternative is not a return to the old street but a slower version of the same decline. The stronger case is not that cars are evil; it is that a street is a place, and a place cannot be a road first.", 
                             "کم پیش می‌آید سیاستی شهری به‌سرعت ممنوعیت خودرو شهر را دو نیم کند. موافقان به هوا اشاره می‌کنند و مخالفان به صندوق فروش، و هر دو یک خیابان را توصیف می‌کنند.\n\nدلیل موافقان بر یک اندازه‌گیری استوار است. ترافیک بزرگ‌ترین منبع دی‌اکسید نیتروژن در بیشتر مرکزهای شهری است و اثرهای سلامت بیشتر بر کسانی می‌افتد که آنجا زندگی می‌کنند، نه کسانی که از آن می‌گذرند. در جاهایی که محدوده ایجاد شده، NO₂ بین یک‌چهارم تا یک‌سوم در دو سال کم شده و دوچرخه‌سواری بیش از پیش‌بینی‌ها بالا رفته است.\n\nدلیل مخالفان فقط راحتی نیست. مغازه‌های حاشیهٔ یک محدوده از کاهش حدود ۸ درصدی فروش در سال اول گفتند و شرکت‌های تحویل هزینهٔ اضافه را به مشتری دادند. ممنوعیت فرض می‌کند کسانی که بیشتر ضرر می‌کنند — خرده‌فروشان و رانندگان کم‌درآمد — می‌توانند این تغییر را جذب کنند.\n\nدر مجموع، سلامت ساکنان از دو سال سازگاری کسب‌وکارها سنگین‌تر است، عمدتاً چون گزینهٔ جایگزین بازگشت به خیابان قدیم نیست، نسخهٔ کندتری از همان افت است. استدلال قوی‌تر این نیست که خودرو بد است؛ این است که خیابان یک مکان است و یک مکان نمی‌تواند اول از همه جاده باشد.")),
        ),
    ],
)

U4 = unit(
    "b2-u4",
    ("It is said that", "می‌گویند"),
    ("Report events without a named doer, and report claims without owning them.", "رویدادها را بی‌کنندهٔ نام‌دار بازگو کن و ادعاها را بی‌آنکه از آن خودت کنی نقل کن."),
    [
        lesson(
            "b2-u4-l1",
            "grammar",
            ("The passive across tenses, and reporting passives", "مجهول در همهٔ زمان‌ها و مجهول نقل‌قولی"),
            ("Move between be-forms and use it is said / he is believed to.", "میان شکل‌های be جابه‌جا شو و it is said / he is believed to را به کار ببر."),
            [
                ("The passive is be + past participle in every tense: it is checked, it was checked, it has been checked, it is being checked, it will be checked, it had been checked. Choose the tense for the meaning, then keep the participle fixed.", "مجهول در هر زمان be + اسم مفعول است: it is checked، it was checked، it has been checked، it is being checked، it will be checked، it had been checked. زمان را بر اساس معنا انتخاب کن و اسم مفعول را ثابت نگه دار."),
                ("Modals and infinitives put be after the modal: it must be checked, it should have been checked, it needs to be checked. A common B2 error is 'must checked'.", "افعال وجهی و مصدر be را بعد از خود می‌آورند: it must be checked، it should have been checked، it needs to be checked. خطای رایج B2 «must checked» است."),
                ("Reporting passives turn a rumor into a structure: people say he is rich → it is said that he is rich / he is said to be rich. The choice of verb matters: said and believed are neutral, alleged and claimed distance the writer from the fact.", "مجهول نقل‌قولی شایعه را به ساختار تبدیل می‌کند: people say he is rich ← it is said that he is rich / he is said to be rich. انتخاب فعل مهم است: said و believed خنثی‌اند و alleged و claimed نویسنده را از واقعیت دور می‌کنند."),
                ("With a past infinitive, the reporting passive moves the event back in time: he is believed to have left the country. This is the form news writing uses instead of naming a source.", "با مصدر گذشته، مجهول نقل‌قولی رویداد را به گذشته می‌برد: he is believed to have left the country. همین شکل، فرم خبرنویسی به‌جای نام بردن از منبع است."),
                ("Keep the by-phrase only when the doer is news: the law was passed by a single vote. 'The window was broken by someone' adds nothing — the passive exists to leave that out.", "عبارت with by را فقط وقتی نگه دار که کننده خبر باشد: the law was passed by a single vote. «The window was broken by someone» چیزی اضافه نمی‌کند؛ مجهول برای حذف همان است."),
            ],
            [
                ("The road is being repaired, so take the other exit.", "جاده در حال تعمیر است، از خروجی دیگر برو."),
                ("All applications must be submitted by Friday.", "همهٔ درخواست‌ها باید تا جمعه ارسال شوند."),
                ("The minister is said to have known about the report for a month.", "می‌گویند وزیر یک ماه از گزارش خبر داشته است."),
                ("It is widely believed that the market will recover.", "به‌طور گسترده باور دارند که بازار بازمی‌گردد."),
                ("The building should have been inspected last year.", "ساختمان باید سال گذشته بازرسی می‌شد."),
            ],
            [
                mcq("The bridge ___ at the moment, so the road is closed.", "پل در این لحظه ___ و جاده بسته است.", ["repairs", "is repairing", "is being repaired", "has repaired"], 2,
                    "Present continuous passive: is being + participle.", "مجهول حال استمراری: is being + اسم مفعول."),
                mcq("He ___ to have left the country last week.", "___ او هفتهٔ گذشته کشور را ترک کرده است.", ["believes", "is believed", "believed", "is believing"], 1,
                    "Reporting passive with a past infinitive.", "مجهول نقل‌قولی با مصدر گذشته."),
            ],
            [
                gap("The results ___ (publish) next month.", ["will be published"], "Future passive: will be + participle.", "مجهول آینده: will be + اسم مفعول."),
                gap("Nothing ___ (can / do) until the report arrives.", ["can be done"], "Modal passive: modal + be + participle.", "مجهول وجهی: وجهی + be + اسم مفعول."),
                mcq("Which sentence uses the passive best?", "کدام جمله مجهول را بهتر به کار برده است؟", ["The letter was written by me.", "The letter was written by someone.", "The letter was written yesterday and sent today.", "The letter writes easily."], 2,
                    "No empty by-phrase; the passive carries the time.", "بی‌عبارت by بی‌محتوا؛ مجهول زمان را حمل می‌کند."),
                mcq("'It is alleged that…' is ___.", "«It is alleged that…» ___ است.", ["a proven fact", "a claim the writer does not vouch for", "a law", "an opinion of the writer"], 1,
                    "Alleged marks an unproven claim.", "alleged ادعای اثبات‌نشده را نشان می‌دهد."),
            ],
        ),
        lesson(
            "b2-u4-l2",
            "vocabulary",
            ("Media, sources and the language of doubt", "رسانه، منابع و زبان تردید"),
            ("Read and discuss a news story with attention to what is asserted and what is attributed.", "خبری را با توجه به آنچه ادعا و آنچه نسبت داده می‌شود بخوان و بحث کن."),
            [
                ("News vocabulary: a source, a statement, a briefing, an exclusive, an embargo, a correction, a retraction, a headline, an editorial, a column. To break a story is to publish it first; to run a story is to publish it at all.", "واژگان خبر: source، statement، briefing، exclusive، embargo، correction، retraction، headline، editorial، column. «break a story» یعنی اول منتشر کردن و «run a story» یعنی منتشر کردن."),
                ("Attribution verbs carry reliability: confirm and verify are strong, claim and allege are weak, deny is not the same as refute (refute implies you have the evidence). 'Declined to comment' is neutral; 'refused to comment' is a judgment.", "فعل‌های انتساب میزان اعتبار را می‌گویند: confirm و verify قوی‌اند، claim و allege ضعیف، deny با refute یکی نیست (refute شواهد می‌خواهد). «declined to comment» خنثی است و «refused to comment» داوری."),
                ("Media effects vocabulary: bias, framing, agenda, misinformation (false by mistake), disinformation (false on purpose), sensationalism, scrutiny, transparency, accountability. The distinction between the two 'mis-' words is a favorite exam question and a real one.", "واژگان اثر رسانه: bias، framing، agenda، misinformation (نادرست از اشتباه)، disinformation (نادرست از عمد)، sensationalism، scrutiny، transparency، accountability. تفاوت دو واژهٔ «mis-» پرسش محبوب امتحان و مسئلهٔ واقعی است."),
            ],
            [
                ("The paper ran the story without verifying the source.", "روزنامه خبر را بدون راستی‌آزمایی منبع منتشر کرد."),
                ("The company denied the claim but did not refute it.", "شرکت ادعا را رد کرد اما آن را باطل نکرد."),
                ("The correction appeared on page two, three days later.", "اصلاحیه سه روز بعد در صفحهٔ دو آمد."),
                ("Framing decides which facts look like the story.", "قاب‌بندی تعیین می‌کند کدام واقعیت‌ها داستان به نظر برسند."),
            ],
            [
                mcq("False information spread by mistake is ___.", "اطلاعات نادرست که از اشتباه پخش شود ___ است.", ["disinformation", "misinformation", "a retraction", "an embargo"], 1,
                    "Misinformation is unintentional; disinformation is deliberate.", "misinformation ناخواسته و disinformation عمدی است."),
                mcq("To 'refute' a claim is to ___.", "«refute» یک ادعا یعنی ___.", ["deny it", "prove it false", "ignore it", "repeat it"], 1,
                    "Refute needs evidence that the claim is false.", "refute شواهد نادرستی ادعا را می‌خواهد."),
            ],
            [
                gap("The minister's office issued a short ___ denying the report.", ["statement"], "An official statement.", "statement بیانیهٔ رسمی است."),
                gap("The magazine published a ___ after the story proved false.", ["retraction", "correction"], "Withdrawing a story is a retraction.", "پس گرفتن خبر retraction است."),
                mcq("'Declined to comment' suggests ___.", "«Declined to comment» نشان می‌دهد ___.", ["the person is guilty", "the person chose not to speak", "the journalist did not ask", "the story is false"], 1,
                    "It reports the choice without judging it.", "انتخاب را بی‌داوری نقل می‌کند."),
                mcq("Which pair are near-synonyms?", "کدام جفت نزدیک به هم‌معناست؟", ["bias / framing", "deny / refute", "source / statement", "embargo / headline"], 0,
                    "Both describe how a story is shaped.", "هر دو شکل‌گیری خبر را توصیف می‌کنند."),
            ],
        ),
        lesson(
            "b2-u4-l3",
            "listening",
            ("An interview with a fact-checker", "مصاحبه با یک راستی‌آزما"),
            ("Follow an interview and hear how a claim is checked rather than judged.", "مصاحبه را دنبال کن و بشنو ادعا چطور بررسی می‌شود، نه قضاوت."),
            [
                ("Interview answers are structured by the question's type. 'How do you…' asks for a process, 'What made you…' for a motive, 'Isn't it true that…' is a challenge and usually gets a concession first. The concession is the honest part; the turn after 'but' is the position.", "پاسخ‌های مصاحبه با نوع پرسش ساختار می‌گیرند. «How do you…» فرایند می‌خواهد، «What made you…» انگیزه و «Isn't it true that…» چالش است و معمولاً اول امتیاز می‌گیرد. امتیاز بخش صادق است و بعد از «but» موضع می‌آید."),
                ("Listen for the order of a process: first, then, after that, finally. Numbers of steps are usually stated ('there are three stages'), which lets you check you have them all.", "ترتیب فرایند را بشنو: first، then، after that، finally. تعداد مرحله‌ها معمولاً گفته می‌شود («there are three stages») و همین به تو اجازه می‌دهد همه را داشتی بررسی کنی."),
            ],
            [
                ("'We don't start with the claim. We start with the smallest version of it.'", "«از ادعا شروع نمی‌کنیم. از کوچک‌ترین نسخهٔ آن شروع می‌کنیم»."),
                ("'Then we look for the primary source, not the article about the source.'", "«بعد سراغ منبع اصلی می‌رویم، نه مقاله‌ای دربارهٔ منبع»."),
                ("'Sometimes the answer is 'we don't know yet', and that is a result.'", "«گاهی پاسخ این است که هنوز نمی‌دانیم، و همین یک نتیجه است»."),
            ],
            [
                listen("There are three stages. First we reduce the claim to something measurable. Then we look for the primary source — the study, not the article about the study. Finally we ask whether the source supports the size of the claim, because most false stories are true in the small and false in the large.", "How many stages does the process have?", "فرایند چند مرحله دارد؟", ["two", "three", "four", "five"], 1,
                       "'There are three stages.'", "«سه مرحله است»."),
                listen("There are three stages. First we reduce the claim to something measurable. Then we look for the primary source — the study, not the article about the study. Finally we ask whether the source supports the size of the claim, because most false stories are true in the small and false in the large.", "What is the second stage?", "مرحلهٔ دوم چیست؟", ["measure the claim", "find the primary source", "contact the journalist", "publish a correction"], 1,
                       "Then we look for the primary source.", "بعد سراغ منبع اصلی می‌رویم."),
            ],
            [
                listen("Isn't it true that fact-checking is just opinion? — Partly. We have opinions about what matters. But a check ends with a document: the original study, the exact sentence, the number. Readers can disagree with our conclusion and still use our evidence.", "How does the fact-checker answer the challenge?", "راستی‌آزما به چالش چه پاسخ می‌دهد؟", ["by denying it fully", "by conceding partly, then pointing to evidence", "by refusing to answer", "by changing the subject"], 1,
                       "'Partly' is the concession; the document is the answer.", "«Partly» امتیاز است و سند پاسخ."),
                listen("Isn't it true that fact-checking is just opinion? — Partly. We have opinions about what matters. But a check ends with a document: the original study, the exact sentence, the number. Readers can disagree with our conclusion and still use our evidence.", "What does a check end with?", "بررسی با چه چیزی تمام می‌شود؟", ["an opinion piece", "a document with the original evidence", "an apology", "a headline"], 1,
                       "It ends with the study, the sentence and the number.", "با مطالعه، جمله و عدد تمام می‌شود."),
                mcq("'True in the small and false in the large' means ___.", "«True in the small and false in the large» یعنی ___.", ["the detail is right, the conclusion is exaggerated", "the story is entirely false", "the numbers are missing", "the source is anonymous"], 0,
                    "The small fact survives; the big claim does not.", "واقعیت کوچک می‌ماند و ادعای بزرگ نه."),
                mcq("Which response is a concession?", "کدام پاسخ امتیاز دادن است؟", ["No, that's wrong.", "Partly.", "I refuse to answer.", "Everyone knows that."], 1,
                    "'Partly' accepts part of the challenge.", "«Partly» بخشی از چالش را می‌پذیرد."),
            ],
        ),
    ],
)
