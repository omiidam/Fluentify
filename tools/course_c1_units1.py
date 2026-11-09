#!/usr/bin/env python3
"""C1 · units 1-2: what the sentence puts first, and how sure it sounds.

Unit 1 is information structure — cleft sentences, fronting, and the analytical
reading that notices where an argument has been placed. Unit 2 is epistemic
control: modal perfects and the hedging that separates a careful claim from a
weak one.
"""

from course_kit import gap, lesson, listen, mcq, passage, unit, write

U1 = unit(
    "c1-u1",
    ("What the sentence puts first", "آنچه جمله اول می‌گذارد"),
    ("Move emphasis with clefts and fronting, and read an argument for where it places its claims.", "تأکید را با cleft و تقدیم جابه‌جا کن و استدلال را برای جای ادعاهایش بخوان."),
    [
        lesson(
            "c1-u1-l1",
            "grammar",
            ("Cleft sentences: it-clefts and wh-clefts", "جمله‌های cleft: it-cleft و wh-cleft"),
            ("Put one piece of information in focus and relegate the rest to the background.", "یک اطلاعات را در کانون بگذار و بقیه را به پس‌زمینه ببر."),
            [
                ("An it-cleft splits a single clause in two so that one element carries the new information: The committee rejected the proposal on Tuesday → It was the committee that rejected the proposal / It was the proposal that the committee rejected / It was on Tuesday that the committee rejected the proposal. The clause after that is presupposed; only the focused element is asserted.", "it-cleft یک بند را دو نیم می‌کند تا یک جزء اطلاعات تازه را حمل کند: The committee rejected the proposal on Tuesday ← It was the committee that rejected the proposal / It was the proposal that the committee rejected / It was on Tuesday that the committee rejected the proposal. بند پس از that مفروض است و فقط جزء کانونی ادعا می‌شود."),
                ("A wh-cleft (or pseudo-cleft) puts the focus at the end, which is where English naturally puts new information: What the committee rejected was the proposal. What we need is a decision. The wh-clause is old information; the part after be is the news.", "wh-cleft (یا pseudo-cleft) کانون را در پایان می‌گذارد، همان‌جا که انگلیسی طبیعتاً اطلاعات تازه را می‌نهد: What the committee rejected was the proposal. What we need is a decision. بند wh اطلاعات کهنه است و بخش پس از be خبر."),
                ("The choice is rhetorical, not grammatical. 'It was the committee that rejected it' answers 'who rejected it?'. 'What the committee rejected was the proposal' answers 'what did they reject?'. A writer picks the cleft that matches the question the paragraph has been building.", "انتخاب بلاغی است، نه دستوری. «It was the committee that rejected it» به «چه کسی رد کرد؟» پاسخ می‌دهد. «What the committee rejected was the proposal» به «چه چیزی را رد کردند؟». نویسنده clefی را برمی‌گزیند که با پرسش پاراگراف بخواند."),
                ("Two related forms are worth recognising: the all-cleft (All I want is a straight answer) which narrows to a single thing, and the there-cleft (There's one thing I still don't understand), which introduces rather than emphasises. Both are common in speech and both are regular, not idiomatic exceptions.", "دو شکل مرتبط را باید شناخت: all-cleft (All I want is a straight answer) که به یک چیز محدود می‌کند و there-cleft (There's one thing I still don't understand) که معرفی می‌کند نه تأکید. هر دو در گفتار رایج و هر دو قاعده‌مندند، نه استثنای اصطلاحی."),
            ],
            [
                ("It was the timing, not the cost, that the board objected to.", "هیئت‌مدیره به زمان‌بندی اعتراض داشت، نه به هزینه."),
                ("What the report actually shows is a slow decline, not a collapse.", "آنچه گزارش واقعاً نشان می‌دهد کاهشی تدریجی است، نه فروپاشی."),
                ("It is not the technology that worries me; it is who controls the data.", "چیزی که نگرانم می‌کند فناوری نیست؛ کنترل داده است."),
                ("All the study establishes is a correlation.", "تنها چیزی که مطالعه اثبات می‌کند همبستگی است."),
            ],
            [
                mcq("Which question does 'It was the funding that delayed the trial' answer?", "«It was the funding that delayed the trial» به کدام پرسش پاسخ می‌دهد؟", ["What delayed the trial?", "What did the funding delay?", "When was the trial delayed?", "Who funded the trial?"], 0,
                    "The focused element is the funding.", "جزء کانونی «funding» است."),
                mcq("What does a wh-cleft place at the end of the sentence?", "wh-cleft چه چیزی را در پایان جمله می‌گذارد؟", ["the presupposition", "the new information", "the subject", "the time reference"], 1,
                    "The end position carries the news.", "جای پایان خبر را حمل می‌کند."),
            ],
            [
                gap("___ surprised the reviewers was the absence of any control group.", ["What"], "Wh-cleft: what + clause + be.", "wh-cleft: what + بند + be."),
                gap("It was not until the third interview ___ we understood the problem.", ["that"], "It-cleft with a negative time phrase.", "it-cleft با عبارت زمانی منفی."),
                mcq("Which cleft best answers 'who signed the letter?'", "کدام cleft بهتر به «who signed the letter?» پاسخ می‌دهد؟", ["What was signed was the letter.", "It was the director who signed the letter.", "All that was signed was a letter.", "There was a letter signed."], 1,
                    "The person is the focus, so it-cleft on the person.", "شخص کانون است، پس it-cleft روی شخص."),
                mcq("'All I'm asking for is a fair hearing' functions to ___.", "«All I'm asking for is a fair hearing» کارش ___ است.", ["introduce a new topic", "narrow the request to one thing", "soften a criticism", "change the subject"], 1,
                    "The all-cleft excludes everything else.", "all-cleft هر چیز دیگر را بیرون می‌گذارد."),
            ],
        ),
        lesson(
            "c1-u1-l2",
            "vocabulary",
            ("Academic and professional lexis", "واژگان دانشگاهی و حرفه‌ای"),
            ("Use the verbs of argument precisely — establish, suggest, undermine, qualify — instead of 'say' and 'show'.", "فعل‌های استدلال را دقیق به کار ببر — establish، suggest، undermine، qualify — نه «say» و «show»."),
            [
                ("Reporting verbs carry an epistemic judgement and cannot be swapped freely. Establish and demonstrate claim proof. Suggest, indicate and point to claim support. Argue and contend claim a position. Assert claims without support. Allege and purport carry doubt; refute and disprove mean the claim has fallen.", "فعل‌های نقل قول داوری معرفتی دارند و آزادانه جابه‌جا نمی‌شوند. establish و demonstrate ادعای اثبات دارند. suggest، indicate و point to ادعای پشتوانه. argue و contend ادعای موضع. assert ادعا بدون پشتوانه. allege و purport شک دارند؛ refute و disprove یعنی ادعا فروافتاده است."),
                ("Hedging vocabulary: to qualify a claim, to temper a conclusion, to acknowledge a limitation, to caveat, a tentative finding, a provisional estimate. To 'qualify' does not mean to weaken carelessly; it means to state the conditions under which the claim holds.", "واژگان احتیاط: qualify a claim، temper a conclusion، acknowledge a limitation، caveat، tentative finding، provisional estimate. «qualify» یعنی گفتن شرایطی که ادعا در آن برقرار است، نه سست کردن بی‌دقت."),
                ("Critique vocabulary: to undermine an argument, to challenge an assumption, to expose a flaw, to be at odds with the evidence, to overstate the case, a circular argument, a false dichotomy, an unstated premise. These let you disagree in one precise move rather than three vague ones.", "واژگان نقد: undermine an argument، challenge an assumption، expose a flaw، be at odds with the evidence، overstate the case، circular argument، false dichotomy، unstated premise. این‌ها امکان می‌دهند در یک حرکت دقیق مخالفت کنی، نه سه حرکت مبهم."),
                ("Register pairs where the Latinate form is the written one: ask/request, show/demonstrate, use/employ, need/require, wrong/erroneous, but/below/under. The Latinate form is not automatically better; it is appropriate where the reader expects distance and precision, and pompous in a message to a colleague.", "جفت‌های لحن که شکل لاتین نوشتاری است: ask/request، show/demonstrate، use/employ، need/require، wrong/erroneous. شکل لاتین خودکار بهتر نیست؛ جایی مناسب است که خواننده فاصله و دقت می‌خواهد و در پیام به همکار متکبرانه است."),
            ],
            [
                ("The study establishes a link but does not demonstrate causation.", "مطالعه پیوندی را اثبات می‌کند اما علیت را نشان نمی‌دهد."),
                ("The minister's figures were later refuted by the statistical office.", "ارقام وزیر بعداً از سوی دفتر آمار رد شد."),
                ("Her critique undermines the premise rather than the conclusion.", "نقد او فرض را تضعیف می‌کند، نه نتیجه را."),
                ("These are provisional findings and should be read as such.", "این‌ها یافته‌های موقتی‌اند و باید همین‌طور خوانده شوند."),
            ],
            [
                mcq("Which verb claims proof?", "کدام فعل ادعای اثبات دارد؟", ["suggest", "demonstrate", "allege", "argue"], 1,
                    "Demonstrate claims a demonstration; suggest only support.", "demonstrate اثبات می‌خواهد و suggest فقط پشتوانه."),
                mcq("To 'qualify' a claim is to ___.", "«qualify» یک ادعا یعنی ___.", ["withdraw it", "state the conditions under which it holds", "repeat it more loudly", "prove it"], 1,
                    "Qualification states the limits of validity.", "qualification حدود اعتبار را می‌گوید."),
            ],
            [
                gap("The argument rests on an ___ premise that is never stated.", ["unstated"], "A premise the reader must supply.", "فرضی که خواننده باید بیاورد."),
                gap("The evidence is ___ odds with the conclusion drawn from it.", ["at"], "Fixed phrase: at odds with.", "عبارت ثابت: at odds with."),
                mcq("Which is a false dichotomy?", "کدام دوگانهٔ کاذب است؟", ["Either we cut spending or we raise taxes.", "We could cut spending, raise taxes, or do neither.", "Both options have costs.", "Neither option is popular."], 0,
                    "It presents two options as the only ones.", "دو گزینه را تنها گزینه‌ها نشان می‌دهد."),
                mcq("In a note to a close colleague, which is most appropriate?", "در یادداشت به همکاری نزدیک کدام مناسب‌تر است؟", ["We require your input.", "Can you look at this?", "Your assistance is hereby requested.", "Kindly furnish your response."], 1,
                    "Plain register suits a familiar reader.", "لحن ساده با خوانندهٔ آشنا می‌خواند."),
            ],
        ),
        lesson(
            "c1-u1-l3",
            "reading",
            ("Reading an argument's architecture", "خواندن معماری یک استدلال"),
            ("Find the thesis, the premises and the point where the evidence stops supporting the claim.", "تز، مقدمات و جایی که شواهد از ادعا بازمی‌مانند را پیدا کن."),
            [
                ("An argument has three layers: the thesis (what is claimed), the premises (what is assumed), and the evidence (what is offered). A C1 reader separates them before judging. Most disagreements about a text are really disagreements about which layer a sentence belongs to.", "استدلال سه لایه دارد: تز (آنچه ادعا می‌شود)، مقدمات (آنچه فرض می‌شود) و شواهد (آنچه ارائه می‌شود). خوانندهٔ C1 پیش از داوری این‌ها را جدا می‌کند. بیشتر اختلاف‌ها دربارهٔ یک متن در واقع اختلاف دربارهٔ تعلق یک جمله به یکی از این لایه‌هاست."),
                ("Hedged evidence and strong conclusions are the commonest mismatch: 'the data suggest' in paragraph two becomes 'proves' in paragraph five. When a text upgrades its own claim, that is the place to slow down. Mark the verbs as you read — establish, indicate, imply — and watch whether they strengthen.", "شواهد محتاط و نتیجهٔ قوی رایج‌ترین ناهم‌خوانی است: «the data suggest» در پاراگراف دوم در پاراگراف پنجم «proves» می‌شود. جایی که متن ادعای خود را ارتقا می‌دهد، همان‌جا باید کند شد. هنگام خواندن فعل‌ها را علامت بزن — establish، indicate، imply — و ببین آیا قوی‌تر می‌شوند."),
                ("Concession is a structural signal. A writer who grants a point ('critics are right that…') is usually about to limit it; a writer who never concedes is usually selling something. The concession is where the honest limitation of the argument is stated, and skipping it is how readers end up quoting a claim the author had already qualified.", "امتیاز دادن نشانهٔ ساختاری است. نویسنده‌ای که نکته‌ای را می‌پذیرد («critics are right that…») معمولاً می‌خواهد محدودش کند؛ نویسنده‌ای که هرگز نمی‌پذیرد معمولاً چیزی می‌فروشد. امتیاز جایی است که محدودیت صادقانهٔ استدلال گفته می‌شود و نادیده گرفتنش باعث می‌شود خواننده ادعایی را نقل کند که نویسنده محدودش کرده بود."),
                ("Tone is carried by adverbs and by what is placed in subordinate clauses: 'the admittedly modest gains' concedes before it asserts; 'the so-called reform' marks distance without arguing. Irony rarely announces itself; it usually appears as a mismatch between an evaluative word and a flat fact.", "لحن با قیدها و با آنچه در بند پیرو گذاشته می‌شود حمل می‌شود: «the admittedly modest gains» پیش از ادعا امتیاز می‌دهد و «the so-called reform» فاصله را بی‌استدلال نشان می‌دهد. طعنه کم خود را اعلام می‌کند؛ معمولاً به‌صورت ناهم‌خوانی واژهٔ ارزشی با واقعیتی خنثی ظاهر می‌شود."),
            ],
            [
                ("Thesis: cities should be judged by access, not by growth.", "تز: شهرها را باید با دسترسی سنجید، نه با رشد."),
                ("Premise: growth without access produces congestion and exclusion.", "مقدمه: رشد بدون دسترسی ازدحام و طرد تولید می‌کند."),
                ("Evidence: in three of the four cities studied, journey times rose as output grew.", "شواهد: در سه شهر از چهار شهر مطالعه‌شده، با رشد تولید زمان سفر بالا رفت."),
                ("Concession: the sample is small and the period short.", "امتیاز: نمونه کوچک و دوره کوتاه است."),
            ],
            [
                mcq("A text that moves from 'suggests' to 'proves' has ___.", "متنی که از «suggests» به «proves» می‌رود ___ .", ["become more honest", "upgraded its claim without new evidence", "repeated itself", "conceded a point"], 1,
                    "The strength of the verb rose while the evidence did not.", "قوت فعل بالا رفت و شواهد نه."),
                mcq("Why does a concession matter to a reader?", "چرا امتیاز برای خواننده مهم است؟", ["it weakens the text", "it states the limits the author accepts", "it ends the argument", "it introduces evidence"], 1,
                    "It is where the argument admits its boundary.", "همان‌جا استدلال مرزش را می‌پذیرد."),
            ],
            [
                mcq("Why is the case study persuasive, according to the text?", "به گفتهٔ متن چرا مطالعهٔ موردی متقاعدکننده است؟", ["because it is statistically representative", "because it is concrete and sequential", "because it is peer-reviewed", "because it is short"], 1,
                    "'It persuades because it is concrete.'", "«متقاعد می‌کند چون مشخص است»."),
                mcq("What is the author's proposed remedy?", "درمان پیشنهادی نویسنده چیست؟", ["abandon case studies", "label what a case can support", "use larger samples", "add a control group"], 1,
                    "'The remedy is a sentence, not a redesign.'", "«درمان یک جمله است، نه بازطراحی»."),
                mcq("The word 'so-called' in a text usually signals ___.", "واژهٔ «so-called» در متن معمولاً نشانهٔ ___ است.", ["agreement", "distance or scepticism", "a definition", "a citation"], 1,
                    "It marks evaluation without argument.", "ارزیابی را بی‌استدلال نشان می‌دهد."),
            ],
            passage=passage(("The case against the case study", "استدلال علیه مطالعهٔ موردی"),
                        ("The case study is the most persuasive form in social science and the least reliable. It persuades because it is concrete: one factory, one village, one reform, told in sequence with named people and specific numbers. A reader who has followed a single case to its conclusion feels they have understood something, and they have — but what they have understood is that case.\n\nThe methodological objection is old and never quite answered. A case cannot tell you how often its outcome occurs, because it has no comparison. The factory that introduced a four-day week and reported higher output may have been unusual in forty ways that the study did not measure, and the reform may have contributed nothing at all. Researchers know this; the genre's conventions quietly absorb it. 'Illustrative' appears in the introduction, 'suggestive' in the conclusion, and the body of the text proceeds as though the mechanism had been demonstrated.\n\nDefenders make a fair point: some questions are only answerable this way. If you want to know how a reform was experienced — what changed in the meetings, who resisted, where the plan nearly failed — a survey will not tell you, and a randomised trial cannot be run. The case study is not a poor substitute for an experiment; it is the only instrument for a different question.\n\nWhat follows is not that case studies should be abandoned but that they should be labelled. The problem is not the method but the borrowing of its prestige: a finding about one factory cited in a policy debate as though it were a finding about factories. The remedy is a sentence, not a redesign — say what the case can support, and let the reader see the boundary. Writers resist this because the boundary makes the story smaller. It also makes it true.",
                         "مطالعهٔ موردی متقاعدکننده‌ترین شکل در علوم اجتماعی و کم‌اعتبارترین آن است. متقاعد می‌کند چون مشخص است: یک کارخانه، یک روستا، یک اصلاح، به‌ترتیب با آدم‌های نام‌دار و عددهای دقیق. خواننده‌ای که یک مورد را تا نتیجه دنبال کرده حس می‌کند چیزی فهمیده، و فهمیده — اما آنچه فهمیده همان مورد است.\n\nاعتراض روش‌شناختی قدیمی است و هرگز کامل پاسخ نگرفته. یک مورد نمی‌تواند بگوید نتیجه‌اش چند بار رخ می‌دهد، چون مقایسه‌ای ندارد. کارخانه‌ای که هفتهٔ چهارروزه را آزمود و بهرهٔ بالاتر گزارش کرد شاید از چهل جهت نامعمول بوده باشد که مطالعه نسنجیده و اصلاح شاید هیچ سهمی نداشته است. پژوهشگران این را می‌دانند؛ قراردادهای این ژانر آن را بی‌صدا جذب می‌کنند. «illustrative» در مقدمه می‌آید، «suggestive» در نتیجه، و بدنهٔ متن طوری پیش می‌رود که گویی سازوکار اثبات شده است.\n\nمدافعان نکتهٔ درستی می‌گویند: بعضی پرسش‌ها فقط این‌طور پاسخ‌گرفتنی‌اند. اگر بخواهی بدانی اصلاح چگونه تجربه شد — در جلسه‌ها چه عوض شد، چه کسی مقاومت کرد، طرح کجا نزدیک بود شکست بخورد — پیمایش نمی‌گوید و آزمون تصادفی اجرا نمی‌شود. مطالعهٔ موردی جانشین ضعیف آزمایش نیست؛ تنها ابزار برای پرسشی دیگر است.\n\nنتیجه این نیست که مطالعات موردی را رها کنیم، بلکه باید برچسب بخورند. مشکل روش نیست، قرض گرفتن اعتبار آن است: یافته‌ای دربارهٔ یک کارخانه که در بحث سیاست‌گذاری چنان نقل می‌شود که گویی یافته‌ای دربارهٔ کارخانه‌هاست. درمان یک جمله است، نه بازطراحی — بگو این مورد از چه پشتیبانی می‌کند و بگذار خواننده مرز را ببیند. نویسندگان در برابر این مقاومت می‌کنند چون مرز داستان را کوچک‌تر می‌کند. همچنین آن را درست می‌کند.")),
        ),
    ],
)

U2 = unit(
    "c1-u2",
    ("How sure it sounds", "چقدر مطمئن به گوش می‌رسد"),
    ("Grade certainty with modal perfects and hedges, and take a position on an ethical question.", "قطعیت را با وجهی کامل و احتیاط درجه‌بندی کن و دربارهٔ پرسشی اخلاقی موضع بگیر."),
    [
        lesson(
            "c1-u2-l1",
            "grammar",
            ("Modal perfects and the grammar of certainty", "وجهی کامل و دستور قطعیت"),
            ("Say how certain a past event is, and how much of that certainty is evidence.", "بگو یک رویداد گذشته چقدر قطعی است و چه مقدار از آن قطعیت از شواهد می‌آید."),
            [
                ("Modal + have + participle places a judgement on a past event, and the modal carries the strength: must have (near-certain from evidence), can't have / couldn't have (near-certain negative), may/might/could have (possible), should have / ought to have (expected but not done), needn't have (did it unnecessarily).", "وجهی + have + اسم مفعول داوری‌ای بر رویداد گذشته می‌گذارد و وجهی قدرت را حمل می‌کند: must have (تقریباً قطعی از شواهد)، can't have / couldn't have (قطعی منفی)، may/might/could have (محتمل)، should have / ought to have (انتظار بود ولی نشد)، needn't have (بی‌لزوم انجام شد)."),
                ("Must have and can't have are inferences, not permissions. 'She must have left' means the evidence forces the conclusion; 'she had to leave' means obligation. Mixing them is one of the clearest signs of a B2 writer in C1 clothing.", "must have و can't have استنباط‌اند، نه اجازه. «She must have left» یعنی شواهد نتیجه را تحمیل می‌کند و «she had to leave» یعنی اجبار. اشتباه گرفتنشان یکی از روشن‌ترین نشانه‌های نویسندهٔ B2 در لباس C1 است."),
                ("Should have + participle is retrospective criticism or regret, and it is inherently evaluative: 'you should have told me' says both that you did not and that you ought to have. In formal writing, 'it would have been preferable to' performs the same move with the criticism distributed away from the person.", "should have + اسم مفعول نقد یا افسوس پس‌نگر است و ذاتاً ارزشی است: «you should have told me» هم می‌گوید نگفتی و هم باید می‌گفتی. در نوشتار رسمی «it would have been preferable to» همان کار را می‌کند و نقد را از شخص دور می‌کند."),
                ("Certainty is a scale, and C1 control means placing a claim on it deliberately rather than choosing between 'is' and 'might be': it is certain that, the evidence indicates, it is likely that, it is conceivable that, there is little to suggest that, it cannot be ruled out that. The last two are the hedges of institutional writing, and they are not vagueness — they are precision about the limits of knowledge.", "قطعیت یک طیف است و کنترل C1 یعنی قرار دادن آگاهانهٔ ادعا روی آن، نه انتخاب بین «is» و «might be»: it is certain that، the evidence indicates، it is likely that، it is conceivable that، there is little to suggest that، it cannot be ruled out that. دو مورد آخر احتیاط نوشتار نهادی‌اند و مبهم‌گویی نیستند — دقت دربارهٔ حدود دانش‌اند."),
            ],
            [
                ("The lights were on, so someone must have been there.", "چراغ‌ها روشن بود، پس کسی آنجا بوده است."),
                ("They can't have received the letter; it was sent yesterday.", "نمی‌شود نامه را گرفته باشند؛ دیروز فرستاده شد."),
                ("The delay might have been avoided.", "شاید می‌شد از تأخیر پرهیز کرد."),
                ("You needn't have booked; the hall was empty.", "لازم نبود رزرو کنی؛ سالن خالی بود."),
                ("It cannot be ruled out that the effect was seasonal.", "نمی‌توان رد کرد که اثر فصلی بوده باشد."),
            ],
            [
                mcq("The file is missing. Someone ___ it by mistake.", "پرونده گم شده است. کسی ___ آن را اشتباهی.", ["must delete", "must have deleted", "should delete", "had to delete"], 1,
                    "An inference about the past: must have + participle.", "استنباط دربارهٔ گذشته: must have + اسم مفعول."),
                mcq("'You needn't have waited' means ___.", "«You needn't have waited» یعنی ___.", ["you did not wait", "you waited, unnecessarily", "you should wait", "you must wait"], 1,
                    "The waiting happened and was unnecessary.", "انتظار رخ داد و لازم نبود."),
            ],
            [
                gap("They ___ have arrived already; the flight was delayed two hours.", ["can't", "couldn't"], "A near-certain negative inference.", "استنباط منفی تقریباً قطعی."),
                gap("It would have been ___ to consult the department first.", ["preferable"], "The impersonal form of retrospective criticism.", "شکل بی‌شخصِ نقد پس‌نگر."),
                mcq("Which is the strongest claim?", "کدام ادعا قوی‌ترین است؟", ["It is conceivable that the policy worked.", "There is little to suggest that the policy worked.", "The evidence indicates that the policy worked.", "It cannot be ruled out that the policy worked."], 2,
                    "Indicates is a positive evidential claim; the others are weaker or negative.", "indicates ادعای شاهدمحور مثبت است و بقیه ضعیف‌تر یا منفی‌اند."),
                mcq("'She must have left' differs from 'she had to leave' because ___.", "«She must have left» با «she had to leave» فرق دارد چون ___.", ["one is past and one is present", "one is inference and one is obligation", "one is formal", "there is no difference"], 1,
                    "Must have = inference; had to = obligation.", "must have استنباط و had to اجبار است."),
            ],
        ),
        lesson(
            "c1-u2-l2",
            "vocabulary",
            ("Ethics, judgement and the words of disagreement", "اخلاق، داوری و واژه‌های اختلاف"),
            ("Disagree precisely, name the principle at stake, and avoid both moralism and vagueness.", "دقیق مخالفت کن، اصلی را که در خطر است نام ببر و از اخلاق‌گرایی و ابهام هر دو بپرهیز."),
            [
                ("Ethics vocabulary: a principle, a duty, a right, an obligation, a consequence, an intention, a motive, consent, autonomy, fairness, harm, accountability, a conflict of interest, a moral hazard. Arguments usually turn on which of these is treated as prior — duty or consequence.", "واژگان اخلاق: principle، duty، right، obligation، consequence، intention، motive، consent، autonomy، fairness، harm، accountability، conflict of interest، moral hazard. بحث‌ها معمولاً بر سر این می‌گردند که کدام مقدم است — وظیفه یا پیامد."),
                ("Judgement words with different force: acceptable, defensible, justifiable, permissible, questionable, indefensible, reprehensible. 'Defensible' is a low bar and an honest one; 'permissible' appeals to a rule; 'questionable' marks doubt without accusation. Choosing among them is the whole art of measured disagreement.", "واژه‌های داوری با نیروی متفاوت: acceptable، defensible، justifiable، permissible، questionable، indefensible، reprehensible. «defensible» آستانهٔ پایین و صادقانه است؛ «permissible» به قاعده ارجاع می‌دهد؛ «questionable» شک را بی‌اتهام نشان می‌دهد. انتخاب میانشان کل هنر مخالفت سنجیده است."),
                ("Disagreement without aggression: I'd take issue with, that rests on an assumption I don't share, I'm not persuaded that, the difficulty with that position is, I'd want to distinguish between. Each names the disagreement and leaves the person intact — which is what makes it usable in a room.", "مخالفت بدون پرخاش: I'd take issue with، that rests on an assumption I don't share، I'm not persuaded that، the difficulty with that position is، I'd want to distinguish between. هر کدام اختلاف را نام می‌برند و شخص را سالم می‌گذارند — و همین آن را در جلسه قابل استفاده می‌کند."),
                ("Word formation and precision: moral / morale (unrelated meanings), ethical / ethics, legal / lawful / legitimate, responsible / responsive, credible / credulous. Note that 'legitimate' often means 'recognised as valid', not 'legal', and 'credulous' means too willing to believe.", "ساخت واژه و دقت: moral / morale (بی‌ربط)، ethical / ethics، legal / lawful / legitimate، responsible / responsive، credible / credulous. «legitimate» اغلب یعنی «معتبر شناخته‌شده»، نه «قانونی»، و «credulous» یعنی بیش از حد زودباور."),
            ],
            [
                ("The objection is to the method, not to the motive.", "اعتراض به روش است، نه به انگیزه."),
                ("That position is defensible, but it is not the only defensible one.", "آن موضع قابل دفاع است، اما تنها موضع قابل دفاع نیست."),
                ("I'd want to distinguish between withholding information and misrepresenting it.", "می‌خواهم بین پنهان کردن اطلاعات و وارونه نشان دادن آن تفکیک کنم."),
                ("The arrangement creates a conflict of interest, whatever the intention.", "این ترتیب، هر چه نیت باشد، تعارض منافع می‌سازد."),
            ],
            [
                mcq("Which word is the most cautious criticism?", "کدام واژه محتاطانه‌ترین نقد است؟", ["reprehensible", "questionable", "indefensible", "unacceptable"], 1,
                    "It marks doubt without passing sentence.", "شک را بی‌صدور حکم نشان می‌دهد."),
                mcq("'Legitimate' most often means ___.", "«legitimate» بیشتر یعنی ___.", ["legal", "recognised as valid", "profitable", "popular"], 1,
                    "Validity, not legality, is the usual sense.", "معمولاً اعتبار است، نه قانونی بودن."),
            ],
            [
                gap("The decision raises a genuine conflict of ___.", ["interest"], "A situation where duties collide.", "موقعیتی که دو وظیفه با هم برخورد می‌کنند."),
                gap("I'd ___ issue with the second premise.", ["take"], "Fixed phrase: take issue with.", "عبارت ثابت: take issue with."),
                mcq("Which pair is not related in meaning?", "کدام جفت از نظر معنا بی‌ربط است؟", ["ethical / ethics", "credible / credulous", "responsible / responsive", "legal / lawful"], 1,
                    "Credible means believable; credulous means gullible.", "credible یعنی باورپذیر و credulous یعنی زودباور."),
                mcq("An argument from consequences asks ___.", "استدلال از پیامد می‌پرسد ___.", ["what rule was broken", "what will happen if we act", "what the agent intended", "who has authority"], 1,
                    "It judges by outcomes, not rules or intentions.", "با نتیجه داوری می‌کند، نه قاعده یا نیت."),
            ],
        ),
        lesson(
            "c1-u2-l3",
            "listening",
            ("The lecture: following a line of reasoning", "سخنرانی: دنبال کردن خط استدلال"),
            ("Track a speaker's structure through signposting, and hear where certainty is lowered.", "ساختار گوینده را با نشانه‌گذاری دنبال کن و بشنو کجا قطعیت پایین می‌آید."),
            [
                ("A lecture announces its structure before it uses it: 'I want to make three points, and the third is the contentious one'. Catch that sentence and the rest is map-reading. Miss it and you are transcribing.", "سخنرانی ساختارش را پیش از استفاده اعلام می‌کند: «I want to make three points, and the third is the contentious one». همان جمله را بگیر و بقیه نقشه‌خوانی است. از دستش بدهی، در حال پیاده‌سازی متن هستی."),
                ("Listen for the epistemic drop. A careful speaker moves from 'we know' to 'we think' to 'it is possible that' as the claim gets harder. The drop is the most informative moment in a talk, because it tells you where the evidence ends — and examiners ask about exactly those places.", "به افت معرفتی گوش کن. گویندهٔ دقیق وقتی ادعا سخت‌تر می‌شود از «we know» به «we think» و بعد «it is possible that» می‌رود. این افت آگاهی‌بخش‌ترین لحظهٔ سخنرانی است، چون می‌گوید شواهد کجا تمام می‌شود — و آزمون‌ها دقیقاً همان جاها را می‌پرسند."),
                ("Discourse markers in speech are not the written ones: 'that said', 'having said that', 'now, the interesting part', 'which brings me to', 'if you take one thing away'. They are longer, and they are said more slowly, because they are doing structural work the layout does in writing.", "نشانه‌های گفتمانی در گفتار همان‌های نوشتار نیستند: «that said»، «having said that»، «now, the interesting part»، «which brings me to»، «if you take one thing away». بلندترند و کندتر گفته می‌شوند، چون کاری را می‌کنند که چیدمان صفحه در نوشتار می‌کند."),
                ("Spoken irony is carried by pitch and by a slight delay: 'and that, apparently, solved everything'. A transcript loses it entirely, which is why listening to the tone is not optional for C1 — the words alone can reverse the meaning.", "طعنهٔ گفتاری با ارتفاع صدا و تأخیری کوتاه حمل می‌شود: «and that, apparently, solved everything». رونوشت آن را کامل از دست می‌دهد و همین است که برای C1 گوش دادن به لحن اختیاری نیست — واژه‌ها به‌تنهایی می‌توانند معنا را وارونه کنند."),
            ],
            [
                ("I'll make three points; the third is the one I'd argue hardest for.", "سه نکته می‌گویم؛ سومی آن است که بیشتر از همه دفاع می‌کنم."),
                ("That said, the sample was small.", "با این حال، نمونه کوچک بود."),
                ("Which brings me to the question nobody wants to ask.", "که مرا به پرسشی می‌رساند که کسی نمی‌خواهد بپرسد."),
                ("And that, apparently, solved everything.", "و ظاهراً همان همه‌چیز را حل کرد."),
            ],
            [
                mcq("What does an 'epistemic drop' mark?", "«افت معرفتی» چه را نشان می‌دهد؟", ["a change of topic", "the point where evidence weakens", "the end of the lecture", "a joke"], 1,
                    "The speaker's certainty falls as the claim gets harder.", "با سخت‌تر شدن ادعا قطعیت گوینده کم می‌شود."),
                mcq("Why is 'apparently' a warning in speech?", "چرا «apparently» در گفتار هشدار است؟", ["it means certainly", "it often carries irony", "it ends the sentence", "it is formal"], 1,
                    "Spoken with pitch, it marks distance.", "با ارتفاع صدا، فاصله را نشان می‌دهد."),
            ],
            [
                gap("Having ___ that, the conclusion still holds.", ["said"], "A spoken concessive marker.", "نشانهٔ امتیاز در گفتار."),
                mcq("Which is a structural signpost?", "کدام نشانهٔ ساختاری است؟", ["however", "which brings me to my second point", "in addition", "therefore"], 1,
                    "It names the position in the argument.", "جای خود را در استدلال نام می‌برد."),
                listen("We know the programme reached forty schools. We think it changed teaching in about half of them. Whether it improved results is, honestly, still open.",
                       "Which claim is the least certain?", "کدام ادعا کم‌ترین قطعیت را دارد؟", ["it reached forty schools", "it changed teaching in half", "it improved results", "none of them"], 2,
                       "'Still open' withholds the conclusion.", "«still open» نتیجه را معلق نگه می‌دارد."),
                write("Write five sentences that summarise a talk you have heard recently: two things the speaker knew, two they only suspected, and one structural marker they used.",
                      "پنج جمله بنویس که سخنرانی‌ای را که تازگی شنیده‌ای خلاصه کند: دو چیز که گوینده می‌دانست، دو چیز که فقط حدس می‌زد و یک نشانهٔ ساختاری که به کار برد.",
                      70, ["that said"],
                      "Keep the certainty of each claim visible in the verb.",
                      "قطعیت هر ادعا را در فعل آشکار نگه دار."),
            ],
        ),
    ],
)
