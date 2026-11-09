#!/usr/bin/env python3
"""B2 · units 1-2: the earlier past, and the future seen from ahead.

B2 opens where B1 left off. The first unit puts a second past behind the first,
which is what narrative needs; the second moves the other way, to a future we
look back on and a future we will be inside. Both are taught through the
vocabulary of education and work, not in the abstract.
"""

from course_kit import gap, lesson, listen, mcq, passage, unit

U1 = unit(
    "b2-u1",
    ("Before that", "پیش از آن"),
    ("Place one past event before another, and keep a story's tenses consistent.", "رویداد گذشته را پیش از رویداد دیگری بگذار و زمان‌های داستان را یکدست نگه دار."),
    [
        lesson(
            "b2-u1-l1",
            "grammar",
            ("Past perfect and past perfect continuous", "گذشتهٔ کامل و گذشتهٔ کامل استمراری"),
            ("Mark the earlier of two past events, and the duration that led up to one.", "رویداد قدیمی‌تر از دو رویداد گذشته و مدتِ منتهی به یک رویداد را نشان بده."),
            [
                ("The past perfect is had + past participle: when I arrived, the movie had started. It exists to solve an ordering problem — without it, two past simples sit side by side with no before.", "گذشتهٔ کامل had + اسم مفعول است: when I arrived, the movie had started. کارش حل مسئلهٔ ترتیب است؛ بدون آن دو گذشتهٔ ساده کنار هم می‌نشینند و «قبل» معلوم نیست."),
                ("The past perfect is only used when the order is not already clear. After before, after, when and once, the past simple is usually enough: after she left, I called. Two past perfects in a row are almost always a mistake.", "گذشتهٔ کامل تنها وقتی به کار می‌رود که ترتیب از قبل روشن نباشد. بعد از before، after، when و once معمولاً گذشتهٔ ساده کافی است: after she left, I called. دو گذشتهٔ کامل پشت هم تقریباً همیشه خطاست."),
                ("Past perfect continuous (had been + -ing) shows a duration that stopped, or was still going, at a past point: we had been waiting for an hour when the bus came. It answers 'how long before', not 'how many'.", "گذشتهٔ کامل استمراری (had been + ing) مدتی را نشان می‌دهد که در نقطه‌ای در گذشته قطع شد یا هنوز ادامه داشت: we had been waiting for an hour when the bus came. به «چقدر قبل» پاسخ می‌دهد، نه «چند تا»."),
                ("Reported speech and third conditionals keep the same form for a reason: both look back at an unreal or already-spoken past. She said she had seen him. If I had known, I would have come.", "نقل قول غیرمستقیم و شرطی سوم همین شکل را دارند، چون هر دو به گذشته‌ای نگاه می‌کنند که unreal یا از پیش گفته‌شده است. She said she had seen him. If I had known, I would have come."),
                ("Tense consistency: choose one anchor in the past and move around it. A story that jumps between past simple and past perfect without a reason reads as uncertainty, not as sophistication.", "یکدستی زمان: یک لنگر در گذشته انتخاب کن و پیرامونش حرکت کن. داستانی که بی‌دلیل میان گذشتهٔ ساده و کامل می‌پرد، عدم اطمینان می‌خواند، نه تسلط."),
            ],
            [
                ("When we got to the station, the train had already left.", "وقتی به ایستگاه رسیدیم، قطار قبلاً رفته بود."),
                ("She had been working there for six years before she was promoted.", "پیش از ارتقا، شش سال آنجا کار می‌کرد."),
                ("I didn't recognize him because we hadn't met before.", "او را نشناختم، چون قبلاً همدیگر را ندیده بودیم."),
                ("Had you finished the report before the meeting started?", "گزارش را قبل از شروع جلسه تمام کرده بودی؟"),
                ("After the store closed, he took a course in accounting.", "بعد از بسته شدن مغازه، دورهٔ حسابداری گذراند."),
            ],
            [
                mcq("The movie ___ by the time we arrived.", "تا رسیدیم، فیلم ___ .", ["started", "had started", "has started", "was starting"], 1,
                    "The start is earlier than the arrival, so the past perfect marks it.", "شروع پیش از رسیدن است، پس گذشتهٔ کامل آن را نشان می‌دهد."),
                mcq("Which is the natural sentence?", "کدام جمله طبیعی است؟", ["After she had left, I had called her.", "After she left, I called her.", "After she left, I had called her.", "After she had left, I called her yesterday."], 1,
                    "After already shows the order, so two past simples are enough.", "after خودش ترتیب را نشان می‌دهد، پس دو گذشتهٔ ساده کافی است."),
            ],
            [
                gap("They ___ (wait) for two hours when the manager finally appeared.", ["had been waiting"], "A duration up to a past moment: had been + -ing.", "مدتی تا یک لحظهٔ گذشته: had been + ing."),
                gap("I couldn't answer because I ___ (not / read) the chapter.", ["hadn't read", "had not read"], "The reading came before the question.", "خواندن پیش از پرسش بود."),
                mcq("Which sentence needs the past perfect?", "کدام جمله گذشتهٔ کامل لازم دارد؟", ["She opened the door and went in.", "When I arrived, he cooked dinner.", "When I arrived, he had cooked dinner.", "He cooked dinner at eight."], 2,
                    "Only here is one event clearly before the other, with no word to say so.", "فقط اینجا یک رویداد بی‌هیچ واژهٔ ترتیبی، روشن‌تر از دیگری است."),
                listen("By the time the ambulance arrived, the neighbors had already moved him to the shade and given him water.", "What had the neighbors done before the ambulance came?", "همسایه‌ها پیش از رسیدن آمبولانس چه کرده بودند؟", ["nothing", "moved him to the shade and given him water", "called the police", "taken him to hospital"], 1,
                       "The past perfect lists two completed actions before the arrival.", "گذشتهٔ کامل دو کار تمام‌شده پیش از رسیدن را می‌گوید."),
            ],
        ),
        lesson(
            "b2-u1-l2",
            "vocabulary",
            ("Education, learning and the words for progress", "آموزش، یادگیری و واژه‌های پیشرفت"),
            ("Discuss a course, a school system and an adult returning to study.", "دربارهٔ یک دوره، نظام آموزشی و بازگشت بزرگسال به تحصیل گفت‌وگو کن."),
            [
                ("The institution and its stages: elementary, middle and high school, higher education, a college or university, a department. In American English you go to college; British English says go to university.", "نهاد و مرحله‌ها: elementary، middle و high school، higher education، college یا university، department. در انگلیسی آمریکایی to college و انگلیسی بریتانیایی to universityی to college می‌گویند."),
                ("The learner's path has verbs of its own: enroll on a course, attend lectures and seminars, take notes, sit an exam, pass or fail it, retake it, graduate, drop out, and — after a break — go back to studying. A dissertation is the long final paper; a tutor supervises it.", "مسیر یادگیرنده فعل‌های خودش را دارد: enroll on a course، attend lectures/seminars، take notes، sit an exam، pass/fail، retake، graduate، drop out و پس از وقفه go back to studying. dissertation مقالهٔ بلند پایانی است و tutor بر آن نظارت می‌کند."),
                ("Progress collocations: keep up with the course, fall behind, catch up on the reading, make progress, meet a deadline, hand in an assignment, get an extension. Notice that you fall behind and catch up — the particles carry the direction.", "هم‌نشینی‌های پیشرفت: keep up with the course، fall behind، catch up on the reading، make progress، meet a deadline، hand in an assignment، get an extension. توجه کن که fall behind و catch up جهت را در ذرهٔ خود دارند."),
                ("Types of learning: vocational training teaches a trade, an apprenticeship combines work and study, distance learning and online courses are remote, and adult education is for people returning later. Lifelong learning is the umbrella term.", "گونه‌های یادگیری: vocational training یک حرفه می‌آموزد، apprenticeship کار و درس را ترکیب می‌کند، distance learning و online courses از راه دورند و adult education برای بازگشت بزرگسالان است. lifelong learning واژهٔ چتری است."),
            ],
            [
                ("She enrolled on a part-time MBA while working full time.", "در حین کار تمام‌وقت، در دورهٔ پاره‌وقت MBA ثبت‌نام کرد."),
                ("I fell behind in the second semester and spent the break catching up.", "ترم دوم عقب افتادم و تعطیلات را صرف جبران کردم."),
                ("He dropped out in his first year and went back ten years later.", "سال اول رها کرد و ده سال بعد برگشت."),
                ("The course combines an apprenticeship with one day a week at college.", "دوره کارآموزی را با یک روز در هفته کالج ترکیب می‌کند."),
            ],
            [
                mcq("To leave a course before finishing it is to ___.", "پیش از پایان دوره آن را ترک کردن ___ است.", ["graduate", "drop out", "enroll", "retake"], 1,
                    "Drop out means to leave before completing.", "drop out یعنی پیش از اتمام رها کردن."),
                mcq("'I need to catch up on the reading' means ___.", "«I need to catch up on the reading» یعنی ___.", ["I have read too much", "I am behind and must read what I missed", "I will read later", "I have finished the reading"], 1,
                    "Catch up follows falling behind.", "catch up بعد از عقب افتادن می‌آید."),
            ],
            [
                gap("The deadline is Friday, so I have to ___ in my assignment by Thursday.", ["hand"], "Hand in work to a tutor.", "hand in یعنی تحویل دادن کار به استاد."),
                gap("She ___ on the course at the age of forty-five.", ["enrolled"], "Enroll on a course, past simple enrolled.", "enroll on a course و گذشتهٔ آن enrolled."),
                mcq("A long piece of written work at the end of a degree is a ___.", "کار نوشتاری بلند در پایان یک مدرک ___ است.", ["seminar", "dissertation", "schedule", "faculty"], 1,
                    "The dissertation is the final long paper.", "dissertation مقالهٔ بلند پایانی است."),
                mcq("'Vocational training' is ___.", "«Vocational training» ___ است.", ["academic study at a university", "training for a particular job", "learning a language abroad", "exam preparation"], 1,
                    "Vocational means it prepares you for a trade.", "vocational یعنی آماده‌سازی برای یک حرفه."),
            ],
        ),
        lesson(
            "b2-u1-l3",
            "reading",
            ("The degree that waited twenty years", "مدرکی که بیست سال صبر کرد"),
            ("Read an opinion article and separate its claim from the evidence it uses.", "مقالهٔ دیدگاهی را بخوان و ادعای آن را از شواهدی که می‌آورد جدا کن."),
            [
                ("An opinion article makes one claim and defends it. Find the sentence that states the claim — usually early, and often with a contrast ('but the real problem is') — then count how many paragraphs support it and what kind of support each uses: a statistic, a case, an authority, an analogy.", "مقالهٔ دیدگاهی یک ادعا می‌کند و از آن دفاع می‌کند. جمله‌ای را پیدا کن که ادعا را می‌گوید (معمولاً در آغاز و اغلب با تضاد) و بعد بشمار چند پاراگراف آن را پشتیبانی می‌کند و هر کدام چه نوع شواهدی می‌آورد: آمار، نمونه، مرجع یا قیاس."),
                ("Distinguish the writer's stance from the people quoted. A sentence with 'critics say' puts a claim in someone else's mouth; the writer may agree, disagree, or be setting up a rebuttal in the next sentence. Read one sentence past the quote before deciding.", "موضع نویسنده را از گفته‌های نقل‌شده جدا کن. جمله‌ای با «critics say» ادعا را در دهان دیگری می‌گذارد؛ نویسنده ممکن است موافق یا مخالف باشد یا پاسخ را در جملهٔ بعد آماده کند. تا یک جمله بعد از نقل قول را بخوان."),
            ],
            [
                ("Claim: 'the barrier is not ability but time and money'.", "ادعا: «سد، توانایی نیست؛ زمان و پول است»."),
                ("Evidence: 'the average age of her class was thirty-four'.", "شواهد: «میانگین سنی کلاسش سی‌وچهار بود»."),
                ("Counter-argument: 'critics say the money would be better spent on school leavers'.", "استدلال مخالف: «منتقدان می‌گویند این پول بهتر است برای ترک‌کنندگان مدرسه خرج شود»."),
            ],
            [
                mcq("What is the writer's main claim?", "ادعای اصلی نویسنده چیست؟", ["Adult education is too expensive.", "The obstacle to returning to study is time and money, not ability.", "Young students learn faster.", "Universities should close."], 1,
                    "The article sets ability against time and money and chooses the second.", "مقاله توانایی را در برابر زمان و پول می‌گذارد و دومی را انتخاب می‌کند."),
                mcq("How does the writer support the claim?", "نویسنده ادعا را چطور پشتیبانی می‌کند؟", ["with a single anecdote only", "with a case, a statistic about her class and a policy argument", "with quotations from students only", "with no evidence"], 1,
                    "A case, an average age, and a policy comparison.", "یک نمونه، یک میانگین سنی و مقایسه‌ای سیاستی."),
            ],
            [
                mcq("What do the critics say?", "منتقدان چه می‌گویند؟", ["the course is too easy", "the money would help school leavers more", "adults cannot learn", "the university is too small"], 1,
                    "'The money would be better spent on school leavers.'", "«این پول بهتر است برای ترک‌کنندگان مدرسه خرج شود»."),
                mcq("How does the writer answer the critics?", "نویسنده به منتقدان چه پاسخ می‌دهد؟", ["by ignoring them", "by arguing the two groups are not in competition", "by agreeing completely", "by changing the subject"], 1,
                    "The rebuttal says the budget is not a single pot.", "پاسخ می‌گوید بودجه یک قوطی واحد نیست."),
                mcq("What does 'the barrier is not ability' imply about the writer's view of adults?", "«the barrier is not ability» دربارهٔ نگاه نویسنده به بزرگسالان چه می‌گوید؟", ["adults lack talent", "adults are capable but unsupported", "adults should not study", "ability cannot be measured"], 1,
                    "Ability is granted; support is what is missing.", "توانایی پذیرفته است و پشتیبانی کم است."),
                mcq("Which sentence shows the writer's attitude most clearly?", "کدام جمله نگرش نویسنده را روشن‌تر نشان می‌دهد؟", ["She enrolled in 2019.", "The average age was thirty-four.", "We treat a late start as a failure of nerve rather than a failure of funding.", "The course costs money."], 2,
                    "The judgment about how we see late starters is the attitude.", "داوری دربارهٔ نگاه ما به شروع دیرهنگام، همان نگرش است."),
            ],
            passage=passage(("The degree that waited twenty years", "مدرکی که بیست سال صبر کرد"),
                            ("Mina left school at seventeen with good grades and no money. She worked in a pharmacy for twenty years, married, raised two children, and enrolled on a history degree at forty-one.\n\nHer story is usually told as inspiration. That is the wrong frame. The interesting fact about her class was not courage but arithmetic: the average age was thirty-four, and two thirds of the students were working at least thirty hours a week. They had the ability. What they had lacked, for twenty years, was an evening and a fee.\n\nCritics of adult education say the money would be better spent on school leavers, who have longer to repay it. It is a fair argument about budgets and a poor one about people: the two groups are not competing for the same hour of the same life. A country that funds only the first twenty years is financing the cheapest part of the curve.\n\nThe real barrier is not ability, and it is rarely ambition. It is time and money, in that order. We treat a late start as a failure of nerve rather than a failure of funding, and then we are surprised that so few people try.",
                             "مینا در هفده‌سالگی با نمره‌های خوب و بدون پول مدرسه را ترک کرد. بیست سال در داروخانه کار کرد، ازدواج کرد، دو فرزند بزرگ کرد و در چهل‌ویک‌سالگی در رشتهٔ تاریخ ثبت‌نام کرد.\n\nداستان او را معمولاً الهام‌بخش می‌گویند. این قالب اشتباه است. نکتهٔ جالب کلاس او شجاعت نبود، حساب بود: میانگین سن سی‌وچهار بود و دو سوم دانشجوها حداقل سی ساعت در هفته کار می‌کردند. توانایی داشتند. چیزی که بیست سال نداشتند یک عصر و یک شهریه بود.\n\nمنتقدان آموزش بزرگسالان می‌گویند این پول بهتر است برای ترک‌کنندگان مدرسه خرج شود که زمان بیشتری برای بازپرداخت دارند. این استدلال دربارهٔ بودجه منصفانه است و دربارهٔ آدم‌ها ضعیف: این دو گروه بر سر همان ساعت از همان زندگی رقابت نمی‌کنند. کشوری که فقط بیست سال اول را تأمین می‌کند، ارزان‌ترین بخش منحنی را مالی می‌کند.\n\nسد واقعی توانایی نیست و به‌ندرت جاه‌طلبی است. زمان و پول است، به همین ترتیب. ما شروع دیرهنگام را شکست اراده می‌بینیم نه شکست بودجه، و بعد تعجب می‌کنیم که چرا این‌قدر کم امتحان می‌کنند.")),
        ),
    ],
)

U2 = unit(
    "b2-u2",
    ("By next June", "تا ژوئن آینده"),
    ("Talk about a future we will be inside, and one we will have finished.", "دربارهٔ آینده‌ای که در آن خواهیم بود و آینده‌ای که تمامش خواهیم کرد حرف بزن."),
    [
        lesson(
            "b2-u2-l1",
            "grammar",
            ("Future continuous and future perfect", "آیندهٔ استمراری و آیندهٔ کامل"),
            ("Describe what will be happening at a point, and what will already be done.", "بگو در یک لحظه چه چیزی در جریان خواهد بود و چه چیزی تمام شده است."),
            [
                ("Future continuous (will be + -ing) puts you inside a future moment: at eight tomorrow I'll be driving to Shiraz. It is the present continuous of a future snapshot — no promise, no decision, just what will be in progress.", "آیندهٔ استمراری (will be + ing) تو را درون لحظه‌ای در آینده می‌گذارد: at eight tomorrow I'll be driving to Shiraz. همان حال استمراری در قابی از آینده است؛ نه وعده، نه تصمیم، فقط آنچه در جریان خواهد بود."),
                ("Future perfect (will have + participle) looks back from a future point at something completed before it: by June I'll have finished the course. The by-phrase is almost always there, because the form needs a deadline to look back from.", "آیندهٔ کامل (will have + اسم مفعول) از نقطه‌ای در آینده به چیزی که پیش از آن تمام شده نگاه می‌کند: by June I'll have finished the course. عبارت with by تقریباً همیشه هست، چون این شکل به یک موعد برای نگاه به عقب نیاز دارد."),
                ("Future perfect continuous (will have been + -ing) adds duration up to that point: in May she will have been teaching for twenty years. Use it when the length matters, not the result.", "آیندهٔ کامل استمراری (will have been + ing) مدت تا آن نقطه را اضافه می‌کند: in May she will have been teaching for twenty years. وقتی مدت مهم است، نه نتیجه."),
                ("Time clauses stay present: when you arrive, I'll be waiting. By the time you read this, I will have left. Never 'when you will arrive'.", "بندهای زمانی در حال می‌مانند: when you arrive, I'll be waiting. By the time you read this, I will have left. نه «when you will arrive»."),
                ("These forms do not replace going to or the present continuous. A plan stays a plan (we're meeting on Friday); the future continuous describes the state at a time (at seven we'll be eating), and the future perfect a completed stage (by nine we'll have eaten).", "این شکل‌ها جای going to یا حال استمراری را نمی‌گیرند. برنامه همان برنامه است (we're meeting on Friday)؛ آیندهٔ استمراری وضعیت در یک زمان را می‌گوید (at seven we'll be eating) و آیندهٔ کامل مرحلهٔ تمام‌شده را (by nine we'll have eaten)."),
            ],
            [
                ("This time next week we'll be sitting on a beach.", "همین وقت هفتهٔ آینده روی ساحل نشسته‌ایم."),
                ("By the end of March I'll have sent all twelve applications.", "تا پایان مارس هر دوازده درخواست را فرستاده‌ام."),
                ("Don't call at nine — I'll be presenting.", "ساعت نه زنگ نزن؛ در حال ارائه خواهم بود."),
                ("By 2030 the city will have built three new lines.", "تا ۲۰۳۰ شهر سه خط تازه ساخته است."),
                ("In June she will have been working here for a decade.", "در ژوئن ده سال می‌شود که اینجا کار می‌کند."),
            ],
            [
                mcq("By the time you get here, I ___ dinner.", "تا برسی، من شام را ___ .", ["will cook", "will be cooking", "will have cooked", "cook"], 2,
                    "The cooking finishes before the arrival: future perfect.", "پختن پیش از رسیدن تمام می‌شود: آیندهٔ کامل."),
                mcq("At ten tomorrow I ___ the exam, so don't call.", "فردا ساعت ده ___ امتحان، پس زنگ نزن.", ["will sit", "will be sitting", "will have sat", "sit"], 1,
                    "At that moment the action is in progress.", "در آن لحظه کار در جریان است."),
            ],
            [
                gap("By next May I ___ (live) in this apartment for ten years.", ["will have been living"], "Duration up to a future point: will have been + -ing.", "مدت تا نقطه‌ای در آینده: will have been + ing."),
                gap("When you arrive, the others ___ (wait) outside.", ["will be waiting"], "What will be in progress at arrival.", "آنچه در لحظهٔ رسیدن در جریان است."),
                gap("___ you ___ (finish) the report by Friday?", ["Will have finished", "will have finished"], "Future perfect question.", "پرسش آیندهٔ کامل."),
                mcq("Which sentence is wrong?", "کدام جمله غلط است؟", ["By 2030 I will have saved enough.", "At noon I will be traveling.", "When I will arrive, I will call you.", "I will have left by six."], 2,
                    "No will in the time clause after when.", "در بند زمانی بعد از when هیچ will نمی‌آید."),
            ],
        ),
        lesson(
            "b2-u2-l2",
            "vocabulary",
            ("Professional life: the language of a workplace", "زندگی حرفه‌ای: زبان محیط کار"),
            ("Handle a project, a meeting and a performance conversation.", "یک پروژه، یک جلسه و گفت‌وگوی ارزیابی را مدیریت کن."),
            [
                ("Project language: set a deadline, meet or miss it, prioritize tasks, delegate work, allocate a budget, monitor progress, deliver on time, and — when things slip — put a project back on track. A milestone is a checkpoint, not the end.", "زبان پروژه: set a deadline، meet/miss it، prioritize tasks، delegate work، allocate a budget، monitor progress، deliver on time و وقتی کار عقب افتاد put a project back on track. milestone یک ایستگاه بازبینی است، نه پایان."),
                ("Meeting language is formulaic on purpose: go through the agenda, raise a point, put something on hold, come back to it later, reach a decision, action a task, minute a meeting. 'Take it offline' means discuss it after the meeting.", "زبان جلسه عمداً قالبی است: go through the agenda، raise a point، put something on hold، come back to it later، reach a decision، action a task، minute a meeting. «Take it offline» یعنی بعد از جلسه بحث کنیم."),
                ("Performance: set objectives, take on responsibility, be accountable for a result, take the initiative, work to a tight deadline, and receive constructive feedback. To 'step up' is to take a bigger role; to 'burn out' is to work past your limit for too long.", "عملکرد: set objectives، take on responsibility، be accountable for a result، take the initiative، work to a tight deadline، receive constructive feedback. «step up» یعنی نقش بزرگ‌تر گرفتن و «burn out» یعنی بیش از حد و بیش از اندازه کار کردن."),
                ("Register matters here more than anywhere: 'Could you confirm by Friday?' is a request; 'Please confirm by Friday' is an instruction; 'You must confirm by Friday' is a warning. The same content, three relationships.", "لحن اینجا بیش از هر جا مهم است: «Could you confirm by Friday?» خواهش، «Please confirm by Friday» دستور و «You must confirm by Friday» هشدار است. یک محتوا، سه رابطه."),
            ],
            [
                ("We missed the first milestone, so we re-planned the last two weeks.", "اولین نقطهٔ بازبینی را از دست دادیم، پس دو هفتهٔ آخر را دوباره برنامه‌ریزی کردیم."),
                ("Could you action that and confirm by Thursday?", "می‌شود آن را انجام بدهی و تا پنجشنبه تأیید کنی؟"),
                ("She took the initiative and spoke to the client before the problem grew.", "ابتکار عمل را به دست گرفت و پیش از بزرگ شدن مشکل با مشتری صحبت کرد."),
                ("He was accountable for the budget, not for the schedule.", "او مسئول بودجه بود، نه برنامهٔ زمانی."),
            ],
            [
                mcq("To give part of your work to a colleague is to ___.", "بخشی از کارت را به همکاری سپردن ___ است.", ["delegate", "allocate", "monitor", "minute"], 0,
                    "Delegate means to entrust a task to someone.", "delegate یعنی سپردن کار به دیگری."),
                mcq("'Let's take that offline' means ___.", "«Let's take that offline» یعنی ___.", ["turn off the computer", "discuss it after the meeting", "cancel the point", "write it down"], 1,
                    "Offline here means outside the current meeting.", "offline اینجا یعنی بیرون از جلسهٔ جاری."),
            ],
            [
                gap("We need to ___ the budget across three teams.", ["allocate"], "Allocate a budget to or across.", "allocate a budget به یا میان."),
                gap("The project slipped, so we met to put it back on ___ .", ["track"], "Back on track.", "دوباره روی ریل افتادن."),
                mcq("Which is the softest request?", "کدام خواهش نرم‌ترین است؟", ["Confirm by Friday.", "You must confirm by Friday.", "Could you confirm by Friday?", "I need confirmation Friday."], 2,
                    "Could you… is the standard polite request.", "«Could you…» درخواست مؤدبانهٔ استاندارد است."),
                mcq("'She burned out' means ___.", "«She burned out» یعنی ___.", ["she was promoted", "she was exhausted by overwork", "she resigned angrily", "she changed teams"], 1,
                    "Burnout is exhaustion from prolonged overwork.", "burnout خستگی ناشی از کار بیش‌ازحد طولانی است."),
            ],
        ),
        lesson(
            "b2-u2-l3",
            "listening",
            ("A podcast about four-day weeks", "پادکستی دربارهٔ هفتهٔ چهارروزه"),
            ("Follow a two-speaker discussion and map each claim to its speaker.", "گفت‌وگوی دو نفره را دنبال کن و هر ادعا را به گوینده‌اش نسبت بده."),
            [
                ("In a discussion, opinions are marked by stance phrases, not by volume: 'I'd argue', 'the evidence suggests', 'I'm not persuaded', 'that may be true, but'. Note who hedges and who asserts, because the summary question usually asks what each speaker believes.", "در گفت‌وگو، نظرها با عبارت موضع نشان داده می‌شوند، نه با بلندی صدا: «I'd argue»، «the evidence suggests»، «I'm not persuaded»، «that may be true, but». دقت کن چه کسی محتاط است و چه کسی قطعی، چون پرسش جمع‌بندی معمولاً باور هر گوینده را می‌پرسد."),
                ("Numbers in speech are approximate and repeated: 'about thirty companies', 'roughly a fifth'. The repetition is the signal — the speaker repeats the figure they want you to keep.", "عددها در گفتار تقریبی و تکراری‌اند: «about thirty companies»، «roughly a fifth». تکرار خودش نشانه است؛ گوینده عددی را که می‌خواهد نگه داری تکرار می‌کند."),
            ],
            [
                ("'I'd argue the four-day week is a productivity story, not a welfare story.'", "«معتقدم هفتهٔ چهارروزه داستان بهره‌وری است، نه رفاه»."),
                ("'That may be true for offices, but not for hospitals.'", "«شاید برای دفاتر درست باشد، اما برای بیمارستان‌ها نه»."),
                ("'About thirty companies tried it and roughly a fifth went back.'", "«حدود سی شرکت امتحان کردند و تقریباً یک‌پنجم برگشتند»."),
            ],
            [
                listen("The four-day week is usually sold as a benefit for workers. I'd argue it is a productivity story. In the trials I read about, teams cut meetings first — and the meetings were the work that was not working.", "What does the first speaker think the four-day week really is?", "گویندهٔ اول فکر می‌کند هفتهٔ چهارروزه واقعاً چیست؟", ["a welfare benefit", "a productivity story", "a legal requirement", "a temporary fashion"], 1,
                       "He says 'it is a productivity story'.", "می‌گوید «it is a productivity story»."),
                listen("The four-day week is usually sold as a benefit for workers. I'd argue it is a productivity story. In the trials I read about, teams cut meetings first — and the meetings were the work that was not working.", "What did teams do first in the trials?", "تیم‌ها در آزمون‌ها اول چه کردند؟", ["hire more staff", "cut meetings", "raise prices", "shorten lunch"], 1,
                       "'Teams cut meetings first.'", "«تیم‌ها اول جلسه‌ها را کم کردند»."),
            ],
            [
                listen("That may be true for offices, but not for hospitals. About thirty companies tried it and roughly a fifth went back within a year. The ones that stayed had one thing in common: they measured output, not hours.", "What is the second speaker's objection?", "اعتراض گویندهٔ دوم چیست؟", ["offices cannot do it", "it does not transfer to hospitals", "it costs too much", "workers dislike it"], 1,
                       "She limits the claim to offices.", "ادعا را به دفاتر محدود می‌کند."),
                listen("That may be true for offices, but not for hospitals. About thirty companies tried it and roughly a fifth went back within a year. The ones that stayed had one thing in common: they measured output, not hours.", "What did the companies that kept it have in common?", "شرکت‌هایی که نگه داشتند چه وجه مشترکی داشتند؟", ["they were small", "they measured output, not hours", "they paid more", "they were in health care"], 1,
                       "'They measured output, not hours.'", "«خروجی را می‌سنجیدند، نه ساعت را»."),
                mcq("Which phrase marks a concession?", "کدام عبارت امتیاز دادن را نشان می‌دهد؟", ["I'd argue…", "That may be true, but…", "The evidence suggests…", "In my view…"], 1,
                    "The concession accepts a point before limiting it.", "امتیاز، نکته را می‌پذیرد و بعد محدودش می‌کند."),
                mcq("Who is more cautious?", "چه کسی محتاط‌تر است؟", ["the first speaker", "the second speaker", "neither", "both equally"], 1,
                    "The second speaker hedges with 'may' and 'roughly'.", "گویندهٔ دوم با may و roughly محتاط است."),
            ],
        ),
    ],
)
