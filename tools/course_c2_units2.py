#!/usr/bin/env python3
"""C2, units 3 and 4: what is left unsaid, and reasoning about what did not
happen."""

from course_kit import (dialogue, gap, lesson, listen, mcq, passage, say,
                       unit, write)

U3 = unit(
    "c2-u3",
    ("Saying less than you mean", "کمتر از آنچه می‌گویی گفتن"),
    ("Recognise and use understatement, irony and euphemism, and know what "
     "each one asks the reader to do.",
     "کم‌گویی، طعنه و حسن‌تعابیر را بشناس و به کار ببر و بدان هر یک از "
     "خواننده چه می‌خواهد."),
    [
        lesson(
            "c2-u3-l1", "grammar",
            ("Litotes and the negative turn",
             "کم‌گویی با نفی (litotes)"),
            ("Use a negated opposite to make a point more forcefully than the "
             "plain adjective would.",
             "متضادِ منفی‌شده را به کار ببر تا نکته را از صفت ساده قوی‌تر "
             "برسانی."),
            [
                ("Litotes denies the opposite: 'not unattractive', 'not "
                 "without merit', 'no small achievement'. Grammatically it is "
                 "a negated adjective or noun; rhetorically it is a way of "
                 "claiming something while appearing not to claim it. 'The "
                 "result was not insignificant' is stronger than 'the result "
                 "was significant', because the reader has to undo the "
                 "negation and so participates in the claim.",
                 "litotes متضاد را نفی می‌کند: «not unattractive»، «not "
                 "without merit»، «no small achievement». از نظر دستوری صفت "
                 "یا اسمی منفی‌شده است؛ از نظر بلاغی راهی برای ادعا کردن "
                 "بی‌آنکه ادعا به نظر برسی. «The result was not insignificant» "
                 "از «the result was significant» قوی‌تر است، چون خواننده باید "
                 "نفی را برگرداند و در ادعا شریک شود."),
                ("It has a register. In speech it is warm and modest; in "
                 "writing it is formal and often evaluative. It fails when it "
                 "is stacked: 'not unproblematic' makes the reader work twice "
                 "and sound uncertain. One negation is a stance; three are a "
                 "muddle.",
                 "ثبت دارد. در گفتار گرم و فروتن است و در نوشتار رسمی و اغلب "
                 "ارزش‌گذار. وقتی روی هم انباشته شود شکست می‌خورد: «not "
                 "unproblematic» خواننده را دو بار به زحمت می‌اندازد و "
                 "مردد به نظر می‌رسد. یک نفی موضع است و سه نفی گِل‌آلودگی."),
                ("Related moves: 'to say the least', 'if anything', 'rather', "
                 "'something of a'. Each lowers the volume while raising the "
                 "implication. 'The launch was something of a setback' is a "
                 "worse verdict than 'the launch failed', delivered more "
                 "politely.",
                 "حرکت‌های مربوط: «to say the least»، «if anything»، "
                 "«rather»، «something of a». هر یک صدا را پایین می‌آورد و "
                 "تلویح را بالا می‌برد. «The launch was something of a "
                 "setback» داوری بدتری از «the launch failed» است که مؤدبانه‌تر "
                 "بیان شده."),
            ],
            [
                ("The committee's findings are not without interest.",
                 "یافته‌های کمیته بی‌بهره از اهمیت نیستند."),
                ("He is not the easiest person to disagree with.",
                 "او آسان‌ترین کسی نیست که با او مخالفت کنی."),
                ("The timing was unfortunate, to say the least.",
                 "زمان‌بندی، دست‌کم، نامناسب بود."),
                ("Her reply was something of a surprise.",
                 "پاسخش تا حدی غافلگیرکننده بود."),
            ],
            [
                mcq("'Not a bad result' usually means ___.", "«Not a bad "
                    "result» معمولاً یعنی ___.",
                    ["a bad result", "a good result, said modestly",
                     "an unclear result", "no result at all"], 1,
                    "The negated opposite is praise with the volume down.",
                    "متضادِ منفی‌شده تعریفی با صدای پایین است."),
                mcq("Which sentence hedges and evaluates at once?",
                    "کدام جمله هم‌زمان احتیاط و داوری می‌کند؟",
                    ["The plan is bad.", "The plan is not unworkable.",
                     "The plan costs money.", "The plan was discussed."], 1,
                    "A double negative with a judgement inside it.",
                    "نفیِ دوگانه‌ای که داوری در آن هست."),
            ],
            [
                mcq("Stacking negations in one phrase usually makes writing "
                    "___.",
                    "انباشتن نفی‌ها در یک عبارت معمولاً نوشته را ___ می‌کند.",
                    ["clearer", "muddled", "warmer", "shorter"], 1,
                    "The reader has to undo each negation.",
                    "خواننده باید هر نفی را برگرداند."),
                gap("The evidence was ___ without significance.", ["not"],
                    "A single negation carries the claim.",
                    "یک نفی ادعا را حمل می‌کند.", "one word"),
                mcq("'The launch was something of a setback' is ___ than 'the "
                    "launch failed'.", "«The launch was something of a "
                    "setback» از «the launch failed» ___ است.",
                    ["less critical", "more critical", "the same as",
                     "less clear but milder"], 0,
                    "Understatement usually softens; the verdict here is "
                    "milder, not harsher.", "کم‌گویی معمولاً نرم می‌کند و "
                    "داوری اینجا ملایم‌تر است."),
            ],
        ),
        lesson(
            "c2-u3-l2", "vocabulary",
            ("Euphemism, irony, sarcasm, innuendo",
             "حسن‌تعابیر، طعنه، طنز تلخ، کنایه"),
            ("Name the figure a speaker is using, and the social work it does.",
             "نام شگردی را بگو که گوینده به کار می‌برد و کاری که در اجتماع "
             "می‌کند."),
            [
                ("A euphemism replaces a harsh word with a gentler one: "
                 "letting people go for dismissing them, a correction for a "
                 "mistake. It is not always dishonest; sometimes it is how a "
                 "society agrees to speak about pain. It becomes dishonest "
                 "when the gentler word hides who did what to whom.",
                 "حسن‌تعابیر واژه‌ای خشن را با واژه‌ای ملایم‌تر جای‌گزین "
                 "می‌کند: letting people go به‌جای اخراج، a correction به‌جای "
                 "خطا. همیشه ناراست نیست؛ گاه شیوه‌ای است که جامعه بر گفتن "
                 "دربارهٔ درد توافق می‌کند. وقتی ناراست می‌شود که واژهٔ "
                 "ملایم‌تر پنهان کند چه کسی با چه کسی چه کرد."),
                ("Irony says one thing and means the reverse, and it needs a "
                 "reader who can hear the mismatch. Sarcasm is irony with a "
                 "bite, aimed at a person. Innuendo is the unsaid accusation: "
                 "it invites the listener to draw the conclusion so the "
                 "speaker never has to state it. The three share a "
                 "characteristic — deniability.",
                 "طعنه چیزی می‌گوید و ضدش را می‌خواهد و خواننده‌ای لازم دارد "
                 "که ناسازگاری را بشنود. sarcasm طعنه‌ای است با نیش که به "
                 "شخص نشانه می‌رود. innuendo اتهام ناگفته است: شنونده را به "
                 "نتیجه‌گیری دعوت می‌کند تا گوینده هرگز مجبور به گفتنش نشود. "
                 "این سه یک ویژگی مشترک دارند — امکان انکار."),
                ("In writing, irony is carried by register: a formal, "
                 "flattering sentence about something trivial, or a flat, "
                 "neutral sentence about something outrageous. The mismatch "
                 "between tone and topic is the signal. Miss it and you read "
                 "the passage backwards.",
                 "در نوشتار، طعنه با ثبت حمل می‌شود: جمله‌ای رسمی و ستایش‌آمیز "
                 "دربارهٔ چیزی بی‌اهمیت، یا جمله‌ای تخت و بی‌طرف دربارهٔ چیزی "
                 "هولناک. ناسازگاری لحن و موضوع همان نشانه است. اگر آن را "
                 "نبینی متن را وارونه می‌خوانی."),
            ],
            [
                ("The company described the losses as a period of "
                 "repositioning.", "شرکت زیان‌ها را «دورهٔ بازآرایی» نامید."),
                ("'What a magnificent turnout,' she said, counting eleven "
                 "people.", "«چه حضور باشکوهی»، گفت در حالی که یازده نفر را "
                 "می‌شمرد."),
                ("Nobody said the figures had been changed. Nobody had to.",
                 "هیچ‌کس نگفت ارقام عوض شده‌اند. لازم نبود کسی بگوید."),
                ("The report calls the delay 'an extended settling-in "
                 "phase'.", "گزارش تأخیر را «دورهٔ طولانی جاافتادن» می‌نامد."),
            ],
            [
                mcq("'Letting people go' is a euphemism for ___.",
                    "«letting people go» حسن‌تعبیری برای ___ است.",
                    ["hiring", "dismissing", "retiring early", "promoting"], 1,
                    "The gentler phrase hides the decision and who made it.",
                    "عبارت ملایم‌تر تصمیم و تصمیم‌گیرنده را پنهان می‌کند."),
                mcq("Innuendo works by ___.", "innuendo با ___ کار می‌کند.",
                    ["stating the accusation", "letting the listener conclude",
                     "praising the target", "changing the subject"], 1,
                    "The speaker keeps deniability; the listener supplies the "
                    "charge.", "گوینده امکان انکار را نگه می‌دارد و شنونده "
                    "اتهام را می‌سازد."),
            ],
            [
                mcq("Which is sarcasm rather than plain irony?",
                    "کدام sarcasm است و نه طعنهٔ ساده؟",
                    ["The rain ruined the whole afternoon.",
                     "'Excellent work,' he said, looking at the broken window.",
                     "The window was broken by the storm.",
                     "We stayed inside because of the rain."], 1,
                    "It is aimed at a person and has a bite.",
                    "به یک شخص نشانه رفته و نیش دارد."),
                gap("The minister's statement was full of ___ : he never "
                     "accused anyone, and everyone understood the "
                     "accusation.",
                    ["innuendo"], "The charge is implied, never stated.",
                    "اتهام تلویحی است و هرگز گفته نمی‌شود.", "one word"),
                mcq("'A period of repositioning' for job losses is ___.",
                    "«A period of repositioning» برای از دست رفتن شغل‌ها ___ "
                    "است.",
                    ["irony", "a euphemism", "an innuendo", "litotes"], 1,
                    "It softens a harsh fact, which is euphemism.",
                    "واقعیتی خشن را نرم می‌کند و این حسن‌تعابیر است."),
                gap("Read the tone against the topic: when a flat sentence "
                     "describes something outrageous, expect ___.",
                    ["irony", "sarcasm"], "The mismatch of tone and topic is "
                    "the signal.", "ناسازگاری لحن و موضوع نشانه است.",
                    "one word"),
            ],
        ),
        lesson(
            "c2-u3-l3", "reading",
            ("The column that praises what it despises",
             "ستونی که آنچه را خوار می‌دارد می‌ستاید"),
            ("Read a satirical column for what it is doing, not for what its "
             "sentences literally say.",
             "ستون طنزی را برای کاری که می‌کند بخوان، نه برای آنچه جمله‌هایش "
             "به‌ظاهر می‌گویند."),
            [
                ("Satire borrows the voice of its target. The column praises "
                 "efficiency while describing something inhuman, and the "
                 "praise is the attack. The literal reading gives you the "
                 "opposite of the argument.",
                 "طنز صدای هدفش را قرض می‌گیرد. ستون کارایی را می‌ستاید و در "
                 "همان حال چیزی غیرانسانی را توصیف می‌کند و همین ستایش، حمله "
                 "است. خوانش ظاهری عکس استدلال را به تو می‌دهد."),
                ("The signals are cumulative: hyperbole that no serious writer "
                 "would use, a statistic quoted with admiration, a human cost "
                 "mentioned in a subordinate clause. One signal is not enough. "
                 "Three in a paragraph is a decision.",
                 "نشانه‌ها انباشتی‌اند: اغراقی که هیچ نویسندهٔ جدی به کار "
                 "نمی‌برد، آماری که با تحسین نقل می‌شود، هزینهٔ انسانی در بندی "
                 "فرعی. یک نشانه کافی نیست؛ سه نشانه در یک بند تصمیم است."),
            ],
            [
                ("Ask of every sentence: who is supposed to be speaking?",
                 "از هر جمله بپرس: قرار است چه کسی حرف بزند؟"),
                ("A question about the author's attitude is not a question "
                 "about the character's.", "پرسش دربارهٔ نگرش نویسنده با پرسش "
                 "دربارهٔ نگرش شخصیت یکی نیست."),
                ("If an option is the literal meaning, check whether the "
                 "passage is arguing with it.", "اگر گزینه‌ای معنای ظاهری است، "
                 "بررسی کن آیا متن با آن می‌جنگد."),
            ],
            [
                mcq("The column's attitude to the system it describes is ___.",
                    "نگرش ستون به نظامی که توصیف می‌کند ___ است.",
                    ["admiring", "hostile", "neutral", "nostalgic"], 1,
                    "The admiration is the borrowed voice of the target.",
                    "تحسین صدای قرض‌گرفتهٔ هدف است."),
                mcq("'Customer seconds' is used in the column to ___.",
                    "«customer seconds» در ستون برای ___ به کار رفته است.",
                    ["measure service speed", "make waiting sound like a "
                     "product", "praise the staff", "explain the software"],
                    1,
                    "The commercial vocabulary applied to waiting is the "
                    "joke.", "واژگان تجاری بر انتظار، همان طنز است."),
            ],
            [
                mcq("Which detail most clearly carries the criticism?",
                    "کدام جزئیات نقد را روشن‌تر حمل می‌کند؟",
                    ["the length of the queue", "the phrase about the "
                     "assistant's unpaid overtime", "the name of the software",
                     "the time of day"], 1,
                    "It is the human cost mentioned in passing.",
                    "هزینهٔ انسانی است که در گذر گفته می‌شود."),
                mcq("A reader who takes the column literally would conclude "
                    "that ___.", "خواننده‌ای که ستون را ظاهری بگیرد نتیجه "
                    "می‌گیرد که ___.",
                    ["the system is cruel", "the system is efficient and "
                     "admirable", "the software failed", "the staff are "
                     "angry"], 1,
                    "That is exactly the reading the satire is mocking.",
                    "این همان خوانشی است که طنز مسخره‌اش می‌کند."),
            ],
            passage=passage(
                ("The efficiency we deserve",
                 "کارایی‌ای که سزاوارش هستیم"),
                ("Our new queue-management system is a triumph of "
                 "measurement, and I say that as a customer who has now spent "
                 "forty minutes being measured. The screen above the counter "
                 "informs us that the average wait is nine minutes, which is "
                 "excellent news for the average. Those of us above it are, "
                 "presumably, outliers, and outliers are how systems learn.\n\n"
                 "The assistant — 'service partner', in the language the "
                 "company prefers — scans, smiles, and explains that the "
                 "system now allocates staff to the busiest windows. It has "
                 "allocated one. She has been allocated to this window since "
                 "eight, and her break, the screen explains, is scheduled for "
                 "when demand allows.\n\n"
                 "What impresses me most is the vocabulary. We are no longer "
                 "waiting; we are 'in queue', which sounds like a place rather "
                 "than a delay. The minutes we lose are not lost at all — they "
                 "are 'customer seconds', a resource, patiently donated. The "
                 "company has not made the wait shorter. It has made it "
                 "countable, and counting, as every manager knows, is the "
                 "first step towards improving something.\n\n"
                 "I left before my number was called, which the system will "
                 "record as an abandonment. Somewhere a dashboard turned a "
                 "shade more efficient, and a service partner was relieved of "
                 "one customer's unreasonable expectations. Everybody won, "
                 "except the outlier, and the outlier is how systems learn.",
                 "نظام تازهٔ مدیریت صف ما پیروزی سنجش است و این را به عنوان "
                 "مشتری‌ای می‌گویم که حالا چهل دقیقه است سنجیده می‌شود. صفحهٔ "
                 "بالای پیشخوان به ما می‌گوید میانگین انتظار نُه دقیقه است، که "
                 "برای «میانگین» خبر عالی‌ای است. ما که بالاتر از میانگینیم "
                 "احتمالاً داده‌های پرت‌ایم و داده‌های پرت همان چیزی است که "
                 "سامانه‌ها از آن یاد می‌گیرند.\n\n"
                 "فروشنده — «همکار خدمت» به زبان موردپسند شرکت — اسکن "
                 "می‌کند، لبخند می‌زند و توضیح می‌دهد که نظام حالا کارکنان را "
                 "به شلوغ‌ترین باجه‌ها می‌فرستد. یکی را فرستاده. او از ساعت "
                 "هشت به این باجه اختصاص یافته و استراحتش، چنان که صفحه "
                 "می‌گوید، هر وقت تقاضا اجازه دهد برنامه‌ریزی شده است.\n\n"
                 "بیش از همه واژگان تحت تأثیرم می‌کند. ما دیگر منتظر نیستیم؛ "
                 "«در صف» هستیم که مثل مکان به گوش می‌رسد نه تأخیر. دقایقی که "
                 "از دست می‌دهیم اصلاً از دست نمی‌رود — «ثانیه‌های مشتری» است، "
                 "منبعی که با صبر اهدا می‌شود. شرکت انتظار را کوتاه‌تر نکرده؛ "
                 "آن را قابل‌شمردن کرده و شمردن، چنان که هر مدیری می‌داند، "
                 "نخستین گام بهبود چیزی است.\n\n"
                 "پیش از آنکه شماره‌ام خوانده شود رفتم و نظام این را "
                 "«ترک صف» ثبت خواهد کرد. جایی داشبوردی یک پله کاراتر شد و "
                 "همکار خدمتی از انتظارهای نامعقول یک مشتری راحت شد. همه "
                 "بردند، جز دادهٔ پرت، و دادهٔ پرت همان چیزی است که سامانه‌ها "
                 "از آن یاد می‌گیرند."),
            ),
        ),
        lesson(
            "c2-u3-l4", "writing",
            ("The editorial that argues in a voice",
             "سرمقاله‌ای که با صدا استدلال می‌کند"),
            ("Argue a position for a public reader: one claim, three "
             "supports, one acknowledged cost, and a close that lands.",
             "برای خوانندهٔ عمومی از موضعی دفاع کن: یک ادعا، سه پشتوانه، یک "
             "هزینهٔ پذیرفته‌شده و پایانی که بنشیند."),
            [
                ("An editorial is an argument with a voice. The voice is not "
                 "decoration: it is how the reader knows what kind of claim "
                 "this is — a warning, a defence, a demand. The structure "
                 "underneath is plain: the claim in the first two sentences, "
                 "three supports, the strongest objection acknowledged and "
                 "answered, and a last line the reader can repeat.",
                 "سرمقاله استدلالی است با صدا. صدا تزیین نیست: خواننده از آن "
                 "می‌فهمد این چه نوع ادعایی است — هشدار، دفاع یا مطالبه. "
                 "ساختار زیرین ساده است: ادعا در دو جملهٔ اول، سه پشتوانه، "
                 "پذیرش و پاسخ به قوی‌ترین اعتراض و جملهٔ آخری که خواننده "
                 "بتواند تکرارش کند."),
                ("The acknowledged objection is what separates an editorial "
                 "from a rant. Name the best version of the other side, not "
                 "the weakest, and answer it in one sentence. A reader who "
                 "disagrees will at least know they were heard.",
                 "اعتراضِ پذیرفته‌شده همان چیزی است که سرمقاله را از پرخاش جدا "
                 "می‌کند. بهترین نسخهٔ طرف مقابل را نام ببر، نه ضعیف‌ترین را، و "
                 "در یک جمله پاسخش بده. خوانندهٔ مخالف دست‌کم می‌داند که شنیده "
                 "شده است."),
            ],
            [
                ("Claim first, in a sentence short enough to quote.",
                 "ادعا اول، در جمله‌ای به‌قدری کوتاه که نقل شود."),
                ("One number per support, and say what it is a number of.",
                 "برای هر پشتوانه یک عدد، و بگو آن عددِ چیست."),
                ("Do not end on a summary; end on the thing you want done.",
                 "با خلاصه تمام نکن؛ با کاری که می‌خواهی انجام شود تمام کن."),
            ],
            [
                mcq("An editorial's first two sentences should contain ___.",
                    "دو جملهٔ اول سرمقاله باید ___ را در خود داشته باشد.",
                    ["the counter-argument", "the claim", "the statistics",
                     "the writer's name"], 1,
                    "The reader decides in two sentences whether to continue.",
                    "خواننده در دو جمله تصمیم می‌گیرد ادامه بدهد یا نه."),
                mcq("Naming the strongest objection makes the argument ___.",
                    "نام بردن قوی‌ترین اعتراض استدلال را ___ می‌کند.",
                    ["weaker", "more credible", "longer", "less clear"], 1,
                    "It shows the writer has done the work.",
                    "نشان می‌دهد نویسنده کارش را کرده است."),
            ],
            [
                write("Write an editorial of about 150 words arguing that a "
                      "city should publish the waiting times of every public "
                      "service. Take a clear position, give three supports, "
                      "answer the strongest objection, and end with the action "
                      "you want.",
                      "سرمقاله‌ای حدود ۱۵۰ واژه بنویس که استدلال کند شهر باید "
                      "زمان انتظار هر خدمت عمومی را منتشر کند. موضع روشن "
                      "بگیر، سه پشتوانه بیاور، به قوی‌ترین اعتراض پاسخ بده و با "
                      "اقدامی که می‌خواهی تمام کن.",
                      150, ["although", "whereas"],
                      "Claim in two sentences, three numbered supports, the "
                      "best objection and its answer, and a final line that "
                      "asks for something.", "ادعا در دو جمله، سه پشتوانه، "
                      "بهترین اعتراض و پاسخش و جملهٔ آخری که چیزی می‌خواهد."),
                mcq("Which ending is an action rather than a summary?",
                    "کدام پایان اقدام است و نه خلاصه؟",
                    ["In conclusion, waiting times matter.",
                     "The council should publish the figures by March.",
                     "This essay has discussed waiting times.",
                     "Waiting is a problem for everyone."], 1,
                    "It asks for a specific act by a specific date.",
                    "اقدامی مشخص را در زمانی مشخص می‌خواهد."),
                gap("An editorial ends on the thing you want ___, not on a "
                     "summary.", ["done"], "The last line is the ask.",
                    "جملهٔ آخر همان درخواست است.", "one word"),
            ],
        ),
    ],
)

U4 = unit(
    "c2-u4",
    ("What did not happen", "آنچه رخ نداد"),
    ("Reason about unreal pasts with the formal conditionals, and carry a "
     "comparison across two sources.",
     "دربارهٔ گذشته‌های رخ‌نداده با شرطی‌های رسمی استدلال کن و مقایسه‌ای را "
     "در دو منبع پیش ببر."),
    [
        lesson(
            "c2-u4-l1", "grammar",
            ("But for, were it not for, had it not been for",
             "But for، were it not for، had it not been for"),
            ("Replace an if-clause with a formal phrase without losing the "
             "condition.",
             "بندِ if را با عبارتی رسمی جای‌گزین کن بی‌آنکه شرط را از دست "
             "بدهی."),
            [
                ("Three formal substitutes for 'if it were not for' and 'if "
                 "it had not been for'. In the present, use 'were it not for' "
                 "or 'but for': were it not for the funding, the study would "
                 "have stopped in March. In the past, use 'had it not been "
                 "for': had it not been for the funding, the study would have "
                 "stopped.",
                 "سه جانشین رسمی برای «if it were not for» و «if it had not "
                 "been for». در حال، «were it not for» یا «but for» به کار "
                 "می‌رود: were it not for the funding, the study would have "
                 "stopped in March. در گذشته، «had it not been for»: had it "
                 "not been for the funding, the study would have stopped."),
                ("The inversion is the point: the auxiliary moves in front of "
                 "the subject and 'if' disappears. That is why 'had it not "
                 "been for' cannot become 'had not it been for', and why 'but "
                 "for' takes a noun rather than a clause: but for the rain, we "
                 "would have walked — not 'but for it rained'.",
                 "وارونگی همان نکته است: فعل کمکی به پیش از نهاد می‌رود و "
                 "«if» حذف می‌شود. به همین دلیل «had it not been for» به «had "
                 "not it been for» تبدیل نمی‌شود و «but for» اسم می‌گیرد نه "
                 "بند: but for the rain, we would have walked — نه «but for "
                 "it rained»."),
                ("The register is formal and slightly literary. In a report it "
                 "buys precision in one clause; in speech it sounds like a "
                 "speech. Use it when the condition is the headline, not as a "
                 "decoration on every sentence.",
                 "ثبتش رسمی و کمی ادبی است. در گزارش، دقت را در یک بند "
                 "می‌خرد؛ در گفتار مثل سخنرانی به گوش می‌رسد. جایی به کارش ببر "
                 "که شرط تیتر است، نه تزیین هر جمله."),
            ],
            [
                ("Had it not been for the second reviewer, the error would "
                 "have been published.", "اگر بازبین دوم نبود، خطا منتشر "
                 "می‌شد."),
                ("Were it not for the archive, we would know almost nothing "
                 "about the period.", "اگر آرشیو نبود، تقریباً هیچ از آن دوره "
                 "نمی‌دانستیم."),
                ("But for one dissenting vote, the proposal would have "
                 "passed.", "اگر یک رأی مخالف نبود، پیشنهاد تصویب می‌شد."),
                ("Had the data been shared earlier, two teams would not have "
                 "repeated the work.", "اگر داده زودتر به اشتراک گذاشته شده "
                 "بود، دو تیم کار را تکرار نمی‌کردند."),
            ],
            [
                mcq("___ the weather, the launch would have gone ahead.",
                    "___ هوا، پرتاب انجام می‌شد.",
                    ["But for", "Were it not", "Had it not", "If not"], 0,
                    "'But for' takes a noun phrase.",
                    "«but for» عبارت اسمی می‌گیرد."),
                mcq("Which is correctly inverted?", "کدام وارونگی درست است؟",
                    ["Had not it been for the delay, we would have finished.",
                     "Had it not been for the delay, we would have finished.",
                     "Had it been not for the delay, we would have finished.",
                     "It had not been for the delay, we would have "
                     "finished."], 1,
                    "The auxiliary fronts, then the subject, then 'not'.",
                    "کمکی جلو می‌آید، بعد نهاد، بعد «not»."),
            ],
            [
                mcq("The sentence 'Had the review been earlier, the error "
                    "would not have reached print' is ___.",
                    "جملهٔ «Had the review been earlier, the error would not "
                    "have reached print» ___.",
                    ["a present condition", "an inverted past condition",
                     "a wish about the future", "a reported question"], 1,
                    "'Had' fronts the clause and the result is past.",
                    "«had» به آغاز بند می‌آید و نتیجه گذشته است."),
                gap("___ for the funding, the trial would have stopped in "
                     "March.", ["But"], "'But for' + noun.",
                    "«but for» + اسم.", "one word"),
                mcq("Which sentence mixes the pattern wrongly?",
                    "کدام جمله الگو را نادرست درهم می‌کند؟",
                    ["Were it not for the cost, we would extend the trial.",
                     "But for the cost, we would extend the trial.",
                     "Had it not been for the cost, we would have extended "
                     "it.",
                     "But for the cost was high, we would extend it."], 3,
                    "'But for' never takes a clause.",
                    "«but for» هرگز بند نمی‌گیرد."),
                gap("Were it not ___ the second reader, the mistake would "
                     "have gone unnoticed.", ["for"],
                    "The frame is fixed: were it not for.",
                    "ساخت ثابت است: were it not for.", "one word"),
            ],
        ),
        lesson(
            "c2-u4-l2", "vocabulary",
            ("Metaphor: literal, figurative, dead, mixed",
             "استعاره: تحت‌اللفظی، مجازی، مرده، درهم"),
            ("Use figurative language deliberately and know when a metaphor "
             "has stopped working.",
             "زبان مجازی را آگاهانه به کار ببر و بدان کدام استعاره از کار "
             "افتاده است."),
            [
                ("A metaphor carries meaning from one domain to another: the "
                 "market froze, the argument collapsed, the policy is a "
                 "bandage. Most of the metaphors in professional English are "
                 "dead — nobody pictures anything when they say 'cash flow' — "
                 "and dead metaphors are useful: they cost the reader nothing "
                 "and everyone understands them.",
                 "استعاره معنا را از یک حوزه به حوزهٔ دیگر می‌برد: the market "
                 "froze، the argument collapsed، the policy is a bandage. "
                 "بیشتر استعاره‌های انگلیسی حرفه‌ای مرده‌اند — کسی با شنیدن "
                 "«cash flow» چیزی تصور نمی‌کند — و استعارهٔ مرده سودمند است: "
                 "برای خواننده هزینه‌ای ندارد و همه می‌فهمند."),
                ("A mixed metaphor breaks because two domains collide: 'we "
                 "must steer the ship out of this swamp' asks the reader to "
                 "sail and wade at once. The test is whether the image can be "
                 "continued. If you cannot say what the vehicle does next, "
                 "the metaphor is doing no work.",
                 "استعارهٔ درهم می‌شکند چون دو حوزه به هم می‌خورند: «we must "
                 "steer the ship out of this swamp» از خواننده می‌خواهد "
                 "هم‌زمان دریانوردی و راه‌رفتن در باتلاق کند. آزمون این است که "
                 "آیا تصویر ادامه‌پذیر است. اگر نمی‌توانی بگویی تصویر بعد چه "
                 "می‌کند، استعاره کاری نمی‌کند."),
                ("Figurative language in argument is not decoration; it is "
                 "framing. Calling a tax a burden invites the reader to think "
                 "about weight and relief. Calling it a contribution invites "
                 "membership. Both are metaphors, and the choice is an "
                 "argument.",
                 "زبان مجازی در استدلال تزیین نیست؛ چارچوب‌بندی است. نامیدن "
                 "مالیات به «بار» خواننده را به وزن و آسودگی می‌برد. نامیدنش "
                 "به «سهم» به عضویت دعوت می‌کند. هر دو استعاره‌اند و انتخاب، "
                 "خودش استدلال است."),
            ],
            [
                ("The negotiations ran aground on a single clause.",
                 "مذاکرات روی یک بند به گل نشست."),
                ("Her argument does not hold water.",
                 "استدلالش آب‌بند نمی‌شود."),
                ("We are steering the ship out of this swamp.",
                 "ما کشتی را از این باتلاق بیرون می‌بریم."),
                ("The policy is a bandage on a broken arm.",
                 "این سیاست چسب‌زخمی بر بازوی شکسته است."),
            ],
            [
                mcq("'Cash flow' is best described as ___.",
                    "«cash flow» بهتر است ___ توصیف شود.",
                    ["a live metaphor", "a dead metaphor", "a mixed "
                     "metaphor", "literal language"], 1,
                    "Nobody pictures water; the image has worn away.",
                    "کسی آب تصور نمی‌کند؛ تصویر ساییده شده است."),
                mcq("Why does 'steer the ship out of this swamp' fail?",
                    "چرا «steer the ship out of this swamp» شکست می‌خورد؟",
                    ["it is too formal", "two domains collide",
                     "it is too long", "ships cannot move"], 1,
                    "You cannot sail and wade in the same image.",
                    "نمی‌توان در یک تصویر هم دریانوردی کرد هم در گل راه رفت."),
            ],
            [
                mcq("Calling a tax a 'contribution' frames it as ___.",
                    "نامیدن مالیات به «سهم» آن را ___ چارچوب می‌دهد.",
                    ["a weight to be lifted", "membership of a group",
                     "a punishment", "a temporary measure"], 1,
                    "The metaphor invites belonging rather than burden.",
                    "استعاره به تعلق دعوت می‌کند، نه به بار."),
                gap("The two images in 'we must navigate this minefield' "
                     "collide: the metaphor is ___.", ["mixed"],
                    "Sailing and walking through mines are different "
                    "domains.", "دریانوردی و گذر از میدان مین دو حوزهٔ "
                    "متفاوت‌اند.", "one word"),
                mcq("A metaphor is doing work when ___.",
                    "استعاره وقتی کار می‌کند که ___.",
                    ["it is unusual", "its image can be continued",
                     "it contains an adjective", "it is explained in "
                     "brackets"], 1,
                    "Continuability is the test of a live image.",
                    "ادامه‌پذیری آزمون تصویر زنده است."),
            ],
        ),
        lesson(
            "c2-u4-l3", "listening",
            ("Two speakers, one question, no agreement",
             "دو گوینده، یک پرسش، بی‌توافق"),
            ("Follow a debate where the speakers disagree about the evidence "
             "itself, not just the conclusion.",
             "مناظره‌ای را دنبال کن که گویندگان دربارهٔ خودِ شاهد اختلاف دارند، "
             "نه فقط نتیجه."),
            [
                ("In an advanced debate the disagreement often moves down a "
                 "level: first the conclusion, then the interpretation, then "
                 "the quality of the evidence. Listening well means hearing "
                 "which level the speakers are actually on.",
                 "در مناظرهٔ پیشرفته اختلاف اغلب یک پله پایین‌تر می‌رود: اول "
                 "نتیجه، بعد تفسیر و بعد کیفیت شاهد. خوب شنیدن یعنی شنیدن این "
                 "که گویندگان واقعاً روی کدام پله‌اند."),
                ("Watch for the concessive turn — 'I accept that, but' — which "
                 "marks the moment a speaker stops attacking the person and "
                 "starts attacking the method. That turn is usually where the "
                 "real argument is.",
                 "به گردشِ پذیرش توجه کن — «I accept that, but» — که لحظه‌ای "
                 "را نشان می‌دهد که گوینده از حمله به شخص دست می‌کشد و به روش "
                 "حمله می‌کند. همان گردش معمولاً جای استدلال واقعی است."),
            ],
            [
                ("First the claim, then the scope, then the method.",
                 "اول ادعا، بعد دامنه، بعد روش."),
                ("A speaker who repeats a number has not answered a question "
                 "about it.", "گوینده‌ای که عددی را تکرار می‌کند به پرسش "
                 "دربارهٔ آن پاسخ نداده است."),
                ("Note who is asked to prove what; the burden of proof is "
                 "part of the argument.", "یادداشت کن چه کسی باید چه چیزی را "
                 "اثبات کند؛ بار اثبات بخشی از استدلال است."),
            ],
            [
                mcq("Where does the disagreement actually lie?",
                    "اختلاف واقعاً کجاست؟",
                    ["the conclusion only", "the reliability of the survey",
                     "the definition of waiting time", "the cost of the "
                     "system"], 1,
                    "Both accept the figures; they split on the survey's "
                    "design.", "هر دو ارقام را می‌پذیرند و بر سر طراحی نظرسنجی "
                    "اختلاف دارند."),
                mcq("One speaker says 'I accept that, but'. What follows is "
                    "___.", "یک گوینده می‌گوید «I accept that, but». آنچه "
                    "می‌آید ___.",
                    ["a concession", "the real objection", "a summary",
                     "a change of topic"], 1,
                    "The concessive turn introduces the substantive attack.",
                    "گردشِ پذیرش حملهٔ اصلی را معرفی می‌کند."),
            ],
            [
                listen("I am not disputing your figures. Nine minutes is nine "
                       "minutes. What I am disputing is that a survey taken "
                       "outside one office in August tells us anything about "
                       "the network in December.",
                       "What is the speaker's objection?",
                       "اعتراض گوینده چیست؟",
                       ["the numbers are wrong", "the sample does not support "
                        "the generalisation", "the office was closed",
                        "December is busier"], 1,
                       "The figures are granted; their reach is denied.",
                       "ارقام پذیرفته و دامنهٔ آنها رد می‌شود."),
                listen("You keep saying the effect is small. Small compared "
                       "with what? Compared with the cost of doing nothing, "
                       "it is not small at all.",
                       "What move does the second speaker make?",
                       "گویندهٔ دوم چه حرکتی می‌کند؟",
                       ["repeats the figure", "changes the comparison",
                        "accepts the point", "questions the data"], 1,
                       "The baseline is contested, not the size.",
                       "خط پایه به چالش کشیده می‌شود، نه اندازه."),
                listen("So we agree the pilot worked and disagree about "
                       "whether it would survive contact with the rest of the "
                       "network. That is a useful place to stop arguing and "
                       "start testing.",
                       "What does the speaker propose?",
                       "گوینده چه پیشنهادی می‌دهد؟",
                       ["another debate", "a wider test", "abandoning the "
                        "pilot", "a new survey"], 1,
                       "The remaining disagreement is empirical, so test it.",
                       "اختلاف باقی‌مانده تجربی است، پس باید آزمود."),
                mcq("A debate moves 'down a level' when it turns from ___.",
                    "مناظره وقتی «یک پله پایین» می‌رود که از ___ بچرخد.",
                    ["method to conclusion", "conclusion to evidence",
                     "people to policy", "cost to time"], 1,
                    "The disagreement gets more fundamental, not less.",
                    "اختلاف بنیادی‌تر می‌شود، نه سطحی‌تر."),
            ],
        ),
        lesson(
            "c2-u4-l4", "writing",
            ("Synthesis: two sources, one argument",
             "ترکیب: دو منبع، یک استدلال"),
            ("Combine two sources that disagree into a single position of "
             "your own, without flattening either.",
             "دو منبع ناهم‌خوان را در موضعی از خودت ترکیب کن بی‌آنکه هیچ‌کدام "
             "را تخت کنی."),
            [
                ("A synthesis is not a summary of two texts side by side. It "
                 "is a claim that the two texts, taken together, support — "
                 "usually a claim neither makes alone. The structure is: what "
                 "both agree on, where they part, and what the parting tells "
                 "us.",
                 "ترکیب خلاصهٔ دو متن در کنار هم نیست. ادعایی است که دو متن با "
                 "هم از آن پشتیبانی می‌کنند — معمولاً ادعایی که هیچ‌کدام تنها "
                 "نمی‌گوید. ساختارش این است: بر چه هم‌داستان‌اند، کجا جدا "
                 "می‌شوند و این جدایی چه به ما می‌گوید."),
                ("Attribution keeps the sources distinct: 'Whereas the survey "
                 "reports a nine-minute average, the interviews describe waits "
                 "of forty minutes.' The contrast is carried by the joining "
                 "words, not by an adverb of opinion. If a reader cannot tell "
                 "which sentence belongs to which source, the synthesis has "
                 "failed.",
                 "انتساب منابع را جدا نگه می‌دارد: «Whereas the survey reports "
                 "a nine-minute average, the interviews describe waits of "
                 "forty minutes.» تقابل را واژه‌های پیوند حمل می‌کنند، نه قید "
                 "نظر. اگر خواننده نتواند بگوید کدام جمله از کدام منبع است، "
                 "ترکیب شکست خورده است."),
                ("End with the reconciliation you actually believe. 'Both are "
                 "right about different things' is a way of not writing. Say "
                 "what should be measured, by whom, and what would settle it.",
                 "با آشتی‌ای تمام کن که واقعاً باورش داری. «هر دو دربارهٔ چیزهای "
                 "متفاوت درست می‌گویند» راهی برای ننوشتن است. بگو چه چیزی باید "
                 "سنجیده شود، توسط چه کسی و چه چیزی آن را فیصله می‌دهد."),
            ],
            [
                ("Both sources accept that the pilot reduced waiting times.",
                 "هر دو منبع می‌پذیرند که آزمایش زمان انتظار را کم کرد."),
                ("They differ on whether a single site can stand for a "
                 "network.", "بر سر این اختلاف دارند که یک سایت می‌تواند "
                 "نمایندهٔ یک شبکه باشد یا نه."),
                ("The disagreement is empirical, so it can be tested rather "
                 "than argued.", "اختلاف تجربی است، پس می‌توان آزمودش نه که "
                 "بحثش کرد."),
                ("The proposal should specify the measure, the period and the "
                 "sites.", "پیشنهاد باید سنجه، دوره و سایت‌ها را مشخص کند."),
            ],
            [
                mcq("A synthesis should produce ___.", "ترکیب باید ___ را "
                    "تولید کند.",
                    ["two summaries", "a claim neither source makes alone",
                     "a list of quotations", "the stronger source"], 1,
                    "The new claim is the reason to synthesise at all.",
                    "ادعای تازه همان دلیل ترکیب است."),
                mcq("Which sentence keeps attribution clear?",
                    "کدام جمله انتساب را روشن نگه می‌دارد؟",
                    ["Obviously the survey is wrong about August.",
                     "The survey reports nine minutes; the interviews "
                     "describe forty.",
                     "Everyone knows waiting feels longer than it is.",
                     "The data speak for themselves."], 1,
                    "Each clause is assigned to a named source.",
                    "هر بند به منبعی نام‌برده نسبت داده شده است."),
            ],
            [
                write("Two sources disagree: a survey reports an average wait "
                      "of nine minutes, while interviews describe waits of "
                      "about forty. Write about 160 words synthesising them "
                      "into one position. Say what both accept, where they "
                      "part, and what should be measured next.",
                      "دو منبع اختلاف دارند: نظرسنجی میانگین انتظار نُه دقیقه "
                      "را گزارش می‌کند و مصاحبه‌ها انتظار حدود چهل دقیقه را. "
                      "حدود ۱۶۰ واژه بنویس و آن‌ها را در یک موضع ترکیب کن. "
                      "بگو هر دو چه می‌پذیرند، کجا جدا می‌شوند و بعد چه باید "
                      "سنجیده شود.",
                      160, ["whereas", "although"],
                      "Agreement, divergence, then a measurement proposal "
                      "with a measure, a period and a site. No source left "
                      "unattributed.", "توافق، واگرایی و سپس پیشنهاد سنجش با "
                      "سنجه، دوره و سایت. هیچ منبعی بی‌انتساب نماند."),
                mcq("The weakest ending for a synthesis is ___.",
                    "ضعیف‌ترین پایان برای یک ترکیب ___ است.",
                    ["a specific test proposal", "'both are right about "
                     "different things'", "a named measure and period",
                     "a question for the next study"], 1,
                    "It closes the argument without deciding anything.",
                    "استدلال را می‌بندد بی‌آنکه چیزی را فیصله دهد."),
                gap("Join two sources with ___ when you want the contrast "
                     "inside one sentence.", ["whereas"],
                    "'Whereas' holds two clauses in explicit opposition.",
                    "«whereas» دو بند را در تقابل صریح نگه می‌دارد.",
                    "one word"),
            ],
        ),
    ],
)
