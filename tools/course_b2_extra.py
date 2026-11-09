#!/usr/bin/env python3
"""Eight lessons that deepen B2: one per unit, using the unit's grammar in a
text, a recording or a performance rather than another rule."""

from course_kit import gap, lesson, listen, mcq, passage, say, write

EXTRA = {
    "b2-u1": [
        lesson(
            "b2-u1-l4", "speaking",
            ("What you had been doing",
             "چه کار داشتی می‌کردی"),
            ("Explain a decision by describing the situation that produced it.",
             "تصمیمی را با توصیف موقعیتی که آن را ساخت توضیح بده."),
            [
                ("To explain a decision, the past perfect continuous gives the "
                 "background that was already running: I had been waiting for "
                 "three weeks, so when the offer came I took it without asking "
                 "many questions.",
                 "برای توضیح یک تصمیم، گذشتهٔ کامل استمراری پس‌زمینه‌ای را می‌آورد "
                 "که در جریان بود: I had been waiting for three weeks, so when "
                 "the offer came I took it without asking many questions."),
                ("The structure of the answer is: what had been happening, the "
                 "moment, the decision, and one honest doubt. The doubt is "
                 "what makes it credible; a decision with no doubt sounds like "
                 "a poster.",
                 "ساختار پاسخ این است: چه در جریان بود، لحظه، تصمیم و یک تردید "
                 "صادقانه. تردید آن را باورپذیر می‌کند؛ تصمیمی بی‌تردید مثل "
                 "پوستر است."),
            ],
            [
                ("I had been saving for two years before I left.",
                 "دو سال پس‌انداز کرده بودم پیش از آنکه بروم."),
                ("The doubt I still have is whether I left too early.",
                 "تردیدی که هنوز دارم این است که آیا زود رفتم."),
            ],
            [
                mcq("The background before the decision takes ___.",
                    "پس‌زمینه پیش از تصمیم ___ می‌گیرد.",
                    ["past simple", "past perfect continuous", "will",
                     "present perfect"], 1,
                    "The action was already running.", "کنش از پیش در جریان "
                    "بود."),
                mcq("A credible account includes ___.", "روایت باورپذیر ___ را "
                    "در بر دارد.",
                    ["only success", "one honest doubt", "three excuses",
                     "no details"], 1,
                    "The doubt is what a listener trusts.",
                    "تردید همان چیزی است که شنونده باورش می‌کند."),
            ],
            [
                say("I had been working nights for a year when the manager "
                    "asked me to stay on permanently.",
                    "یک سال شب‌ها کار کرده بودم که مدیر خواست دائمی بمانم."),
                say("I took it, mostly because I had been sleeping badly and "
                    "the day shift was the offer.",
                    "پذیرفتم، بیشتر چون بد می‌خوابیدم و پیشنهاد همان شیفت روز "
                    "بود."),
                say("The doubt I still have is whether I decided for the "
                    "schedule or for the work.",
                    "تردیدی که هنوز دارم این است که برای برنامه تصمیم گرفتم یا "
                    "برای خودِ کار."),
            ],
        ),
    ],
    "b2-u2": [
        lesson(
            "b2-u2-l4", "reading",
            ("The office that measured itself",
             "دفتری که خودش را سنجید"),
            ("Read about a workplace experiment and find what the measures "
             "changed.",
             "دربارهٔ آزمایشی در محیط کار بخوان و ببین سنجه‌ها چه را عوض "
             "کردند."),
            [
                ("Workplace texts describe intentions and then effects, and "
                 "the gap between them is the argument. Read for the moment "
                 "the measure started to be treated as the goal.",
                 "متن‌های محیط کار نیت‌ها و بعد اثرها را می‌گویند و شکاف میان "
                 "آن‌ها همان استدلال است. لحظه‌ای را بخوان که سنجه خودش هدف "
                 "دانسته شد."),
                ("The future perfect is common in these texts because the "
                 "effects arrive later: by the end of the year the team will "
                 "have held fewer meetings and written more.",
                 "آیندهٔ کامل در این متن‌ها رایج است چون اثرها دیرتر می‌آیند: by "
                 "the end of the year the team will have held fewer meetings "
                 "and written more."),
            ],
            [
                ("By June the team will have held half as many meetings.",
                 "تا ژوئن تیم نصف جلسه‌ها را داشته است."),
                ("The number of decisions did not change.",
                 "تعداد تصمیم‌ها عوض نشد."),
            ],
            [
                mcq("What did the experiment intend to reduce?",
                    "آزمایش قصد داشت چه را کم کند؟",
                    ["decisions", "meetings", "staff", "offices"], 1,
                    "Fewer meetings was the stated aim.",
                    "کم کردن جلسه‌ها هدف اعلام‌شده بود."),
                mcq("What actually changed?", "واقعاً چه عوض شد؟",
                    ["fewer decisions were made", "the meetings moved into "
                     "messages", "the team shrank", "nothing"], 1,
                    "The count fell because the meeting moved, not because "
                    "the work did.", "شمار کم شد چون جلسه جابه‌جا شد، نه کار."),
            ],
            [
                mcq("The gap between intention and effect is ___.", "شکاف نیت "
                    "و اثر ___ است.",
                    ["the argument of the text", "an accident", "the "
                     "conclusion", "a mistake in the data"], 0,
                    "That gap is what the text is about.",
                    "همان شکاف موضوع متن است."),
                mcq("'By June the team will have held fewer meetings' is ___.",
                    "«By June the team will have held fewer meetings» ___ است.",
                    ["future simple", "future perfect", "past perfect",
                     "present perfect"], 1,
                    "Will have + participle looks back from a future point.",
                    "will have + اسم مفعول از آینده به عقب نگاه می‌کند."),
            ],
            passage=passage(
                ("The office that measured itself",
                 "دفتری که خودش را سنجید"),
                ("The pilot was simple: a team of nine would stop holding "
                 "weekly meetings and write a short note instead. The aim was "
                 "to free two hours a week and to make decisions visible. By "
                 "March the team will have held half as many meetings as "
                 "before, and the dashboard will show exactly that, which is "
                 "why the dashboard is not the interesting part.\n\n"
                "What the numbers do not show is where the meeting went. The "
                "note became a thread, the thread became a channel, and by "
                "April the team had been writing to each other for most of "
                "the morning. The meeting had not disappeared; it had been "
                "distributed, in writing, across the week, and nobody could "
                "see it in a room any more. Decisions were still made, at "
                "roughly the same speed, by roughly the same three people.\n\n"
                "The lesson is not that the pilot failed. It is that a measure "
                "which is easy to count — meetings held — will be met in the "
                "way that is easiest to count, and the work will move "
                "somewhere the measure cannot see. The team now has a second "
                "number, minutes spent writing, and the two together tell a "
"truer story than either alone.",
                "آزمایش ساده بود: تیمی نُه‌نفره جلسه‌های هفتگی را کنار می‌گذاشت و به‌جایش "
                "یادداشت کوتاهی می‌نوشت. هدف آزاد کردن دو ساعت در هفته و آشکار کردن "
                "تصمیم‌ها بود. تا مارس تیم نصف جلسه‌های پیشین را داشته است و داشبورد "
                "دقیقاً همین را نشان می‌دهد و به همین دلیل داشبورد بخش جالب ماجرا نیست.\n\n "
                "آنچه اعداد نشان نمی‌دهند این است که جلسه کجا رفت. یادداشت رشته شد، "
                "رشته کانال شد و تا آوریل تیم بیشتر صبح را به هم نوشته بود. جلسه ناپدید "
                "نشده بود؛ توزیع شده بود، در نوشتار، در طول هفته، و کسی دیگر آن را در "
                "اتاقی نمی‌دید. تصمیم‌ها هنوز گرفته می‌شدند، تقریباً با همان سرعت، توسط "
                "تقریباً همان سه نفر.\n\n "
                "درس این نیست که آزمایش شکست خورد. درس این است که سنجه‌ای که شمردنش "
                "آسان است — جلسه‌های برگزارشده — به آسان‌ترین شکل شمردنی برآورده می‌شود و "
                "کار به جایی می‌رود که سنجه نمی‌بیند. تیم حالا عدد دومی دارد، دقایق "
                "نوشتن، و این دو با هم روایتی درست‌تر از هر یک تنها می‌گویند."),
            ),
        ),
    ],
    "b2-u3": [
        lesson(
            "b2-u3-l4", "listening",
            ("The scientist who will not say yes",
             "دانشمندی که بله نمی‌گوید"),
            ("Follow an interview where the expert refuses the conclusion the "
             "interviewer wants.",
             "مصاحبه‌ای را دنبال کن که کارشناس نتیجه‌ای را که مصاحبه‌گر "
             "می‌خواهد نمی‌پذیرد."),
            [
                ("An expert under pressure uses three moves: restate the "
                 "finding, name the limit, and refuse the inference. Listen "
                 "for the third, because that is where the disagreement is.",
                 "کارشناس زیر فشار سه حرکت دارد: بازگویی یافته، نام‌بردن از "
                 "محدودیت و رد استنتاج. به سومی گوش کن، چون اختلاف همان‌جاست."),
                ("Conditional sentences carry the refusal: if we had measured "
                 "the second year, we might be able to say that. The modal "
                 "plus the perfect infinitive is the grammar of a road not "
                 "taken.",
                 "جمله‌های شرطی رد کردن را حمل می‌کنند: if we had measured the "
                 "second year, we might be able to say that. وجه با مصدر کامل، "
                 "گرامر راهی است که نرفته‌اند."),
            ],
            [
                ("If we had followed the group for a second year, we might "
                 "know.", "اگر گروه را سال دوم دنبال کرده بودیم، شاید "
                 "می‌دانستیم."),
                ("That is a reasonable inference, and it is not one the data "
                 "support.", "استنتاج معقولی است، ولی داده پشتیبانی‌اش "
                 "نمی‌کند."),
            ],
            [
                mcq("What does the scientist refuse to do?",
                    "دانشمند از چه کاری خودداری می‌کند؟",
                    ["explain the finding", "extend the finding to a general "
                     "rule", "discuss the method", "admit a limit"], 1,
                    "The finding is local and stays local.",
                    "یافته محلی است و محلی می‌ماند."),
                mcq("'If we had measured the second year' is ___.", "«If we "
                    "had measured the second year» ___ است.",
                    ["a real condition", "an unreal past condition",
                     "a wish about the future", "a reported question"], 1,
                    "The measurement did not happen.", "سنجش رخ نداد."),
            ],
            [
                listen("The effect was clear in the first year. Whether it "
                       "lasts, we cannot say, because we stopped measuring.",
                       "What can the speaker not say?",
                       "گوینده چه را نمی‌تواند بگوید؟",
                       ["the size of the effect", "whether the effect lasts",
                        "when the study began", "who funded it"], 1,
                       "Durability was not measured.", "دوام سنجیده نشد."),
                listen("You are asking me to say the policy works. I can say "
                       "the pilot worked. Those are different sentences.",
                       "What is the speaker correcting?",
                       "گوینده چه را تصحیح می‌کند؟",
                       ["the figures", "the leap from pilot to policy",
                        "the date", "the method"], 1,
                       "A pilot is not a policy.", "آزمایش همان سیاست نیست."),
                listen("Had we known the second site would close, we would "
                       "have chosen another one.",
                       "What happened to the second site?",
                       "سایت دوم چه شد؟",
                       ["it opened", "it closed", "it moved", "it grew"], 1,
                       "The third conditional marks it as a fact known later.",
                       "شرطی سوم آن را واقعیتی می‌داند که بعد معلوم شد."),
            ],
        ),
    ],
    "b2-u4": [
        lesson(
            "b2-u4-l4", "reading",
            ("Two newspapers, one morning",
             "دو روزنامه، یک صبح"),
            ("Compare how two reports of the same event construct their "
             "accounts.",
             "مقایسه کن دو گزارش از یک رویداد چگونه روایت‌هایشان را می‌سازند."),
            [
                ("Reporting passives hide the agent, and that hiding is a "
                 "choice: mistakes were made is a sentence about grammar, not "
                 "about people. Comparing two reports means asking, for every "
                 "passive, who is missing.",
                 "مجهولِ نقل کنشگر را پنهان می‌کند و این پنهان‌سازی انتخابی است: "
                 "mistakes were made جمله‌ای دربارهٔ دستور است، نه دربارهٔ آدم‌ها. "
                 "مقایسهٔ دو گزارش یعنی پرسیدن اینکه در هر مجهول چه کسی غایب "
                 "است."),
                ("Headlines carry the framing before the reader reaches a "
                 "sentence: a 'row' invites conflict, a 'review' invites "
                 "process. The same facts can be filed under either.",
                 "تیترها چارچوب را پیش از رسیدن خواننده به جمله حمل می‌کنند: "
                 "«row» کشمکش می‌طلبد و «review» فرایند. یک واقعیت را می‌توان "
                 "زیر هر دو گذاشت."),
            ],
            [
                ("Mistakes were made, and a review has been commissioned.",
                 "خطاهایی رخ داد و بازبینی‌ای سفارش داده شد."),
                ("The minister rejected calls for resignation.",
                 "وزیر درخواست‌های استعفا را رد کرد."),
            ],
            [
                mcq("'Mistakes were made' omits ___.", "«Mistakes were made» "
                    "چه را حذف می‌کند؟",
                    ["the mistake", "the person who made it", "the date",
                     "the consequence"], 1,
                    "The agentless passive hides who acted.",
                    "مجهول بی‌کنشگر پنهان می‌کند چه کسی کرد."),
                mcq("The two reports differ mainly in ___.", "دو گزارش عمدتاً "
                    "در ___ تفاوت دارند.",
                    ["facts", "who is named and who is omitted",
                     "the date", "the length"], 1,
                    "Same facts, different agents.", "واقعیت یکی، کنشگرها "
                    "متفاوت."),
            ],
            [
                mcq("A headline with 'row' frames the event as ___.",
                    "تیتری با «row» رویداد را ___ چارچوب می‌دهد.",
                    ["a process", "a conflict", "an accident", "a review"],
                    1, "Row is a quarrel.", "row یعنی نزاع."),
                mcq("Which sentence names the agent?", "کدام جمله کنشگر را "
                    "نام می‌برد؟",
                    ["The report was delayed.", "Officials delayed the "
                     "report.", "The report has been delayed.", "Delays "
                     "occurred."], 1,
                    "Officials is the subject of an active verb.",
                    "officials نهاد فعل معلوم است."),
            ],
            passage=passage(
                ("Two newspapers, one morning",
                 "دو روزنامه، یک صبح"),
                ("**The Daily Review.** A report on waiting times was "
                 "delayed for a second time last night, and opposition "
                 "politicians said the delay raised questions about the "
                 "department's competence. Mistakes were made in the earlier "
                 "draft, according to two officials who spoke on condition of "
                 "anonymity, and a review has been commissioned. The minister "
                 "rejected calls for resignation.\n\n"
                "**The Morning Post.** The minister last night rejected calls "
                 "for her resignation, saying the delay was caused by a "
                 "verification problem in the department's own figures. Two "
                 "officials confirmed that the first draft contained errors "
                 "which the department found itself, and that the review she "
                 "announced will report in March. The opposition called the "
                 "delay 'a row of her own making'.\n\n"
                 "The facts are almost identical. The first report puts the "
                 "department in the passive and the politicians in the active; "
                 "the second does the reverse. A reader of either will come "
"away with the same events and a different culprit.",
                 "روزنامهٔ دیلی ریویو. گزارشی دربارهٔ زمان‌های انتظار دیشب برای بار دوم به "
                 "تأخیر افتاد و سیاستمداران مخالف گفتند این تأخیر پرسش‌هایی دربارهٔ شایستگی "
                 "اداره پیش می‌آورد. به گفتهٔ دو مقامی که به شرط ناشناس ماندن سخن گفتند، در "
                 "پیش‌نویس پیشین خطاهایی رخ داده و بازبینی‌ای سفارش داده شده است. وزیر "
                 "درخواست‌های استعفا را رد کرد.\n\n "
                 "مورنینگ پست. وزیر دیشب درخواست‌های استعفا را رد کرد و گفت تأخیر از "
                 "مشکلی در صحت ارقام خود اداره ناشی شده است. دو مقام تأیید کردند که "
                 "پیش‌نویس اول خطاهایی داشت که خود اداره یافت و بازبینی‌ای که او اعلام کرد "
                 "در مارس گزارش می‌دهد. مخالفان تأخیر را «نزاعی که خودش ساخته» خواندند.\n\n "
                 "واقعیت‌ها تقریباً یکسان‌اند. گزارش اول اداره را در مجهول و سیاستمداران را "
                 "در معلوم می‌گذارد و گزارش دوم برعکس. خوانندهٔ هر یک با همان رویدادها و "
                 "مقصر متفاوتی بیرون می‌آید."),
            ),
        ),
    ],
    "b2-u5": [
        lesson(
            "b2-u5-l4", "listening",
            ("The handover call", "تماس تحویل کار"),
            ("Follow a work call where arrangements are being made and "
             "responsibility is assigned.",
             "تماس کاری را دنبال کن که در آن هماهنگی انجام و مسئولیت تقسیم "
             "می‌شود."),
            [
                ("In a handover call the useful information is not what "
                 "happened but who will do what by when: it needs to be "
                 "checked by Friday, I am having it translated, she is getting "
                 "the figures verified.",
                 "در تماس تحویل کار، اطلاعات سودمند این نیست که چه شد، بلکه این "
                 "است که چه کسی تا کِی چه می‌کند: it needs to be checked by "
                 "Friday، I am having it translated، she is getting the figures "
                 "verified."),
                ("Causatives show who arranged an action without doing it: I "
                 "am having it checked means someone else checks and I am "
                 "responsible for the arrangement.",
                 "سببی نشان می‌دهد چه کسی کاری را ترتیب داده بی‌آنکه خودش انجام "
                 "دهد: I am having it checked یعنی کسی دیگر بررسی می‌کند و من "
                 "مسئول هماهنگی‌ام."),
            ],
            [
                ("I am having the figures checked before Friday.",
                 "پیش از جمعه ارقام را بررسی می‌کنم (توسط دیگری)."),
                ("She is getting the contract translated.",
                 "او قرارداد را ترجمه می‌کند (توسط دیگری)."),
            ],
            [
                mcq("Who checks the figures?", "چه کسی ارقام را بررسی می‌کند؟",
                    ["the speaker", "someone else, arranged by the speaker",
                     "nobody", "the client"], 1,
                    "Have something done arranges it.",
                    "have something done آن را ترتیب می‌دهد."),
                mcq("The call is mainly about ___.", "تماس عمدتاً دربارهٔ ___ "
                    "است.",
                    ["what went wrong", "who does what by when",
                     "the cost", "the holiday"], 1,
                    "Responsibility and dates.", "مسئولیت و تاریخ‌ها."),
            ],
            [
                listen("I am having the draft checked by Friday, and I will "
                       "send you the result on Monday.",
                       "When will the result arrive?", "نتیجه کِی می‌رسد؟",
                       ["Friday", "Monday", "today", "next month"], 1,
                       "The check is Friday; the result Monday.",
                       "بررسی جمعه است و نتیجه دوشنبه."),
                listen("She is getting the contract translated, so we need "
                       "the final wording today.",
                       "What do they need today?", "امروز چه لازم دارند؟",
                       ["the translation", "the final wording", "a lawyer",
                        "a signature"], 1,
                       "The wording must be final first.",
                       "اول باید واژه‌بندی نهایی شود."),
                listen("We had the software tested last week and it failed on "
                       "two machines.",
                       "What happened last week?", "هفتهٔ پیش چه شد؟",
                       ["the software was bought", "the software was tested",
                        "the machines were replaced", "the project closed"],
                       1, "Had it tested: someone tested it.",
                       "had it tested: کسی آزمودش."),
            ],
        ),
    ],
    "b2-u6": [
        lesson(
            "b2-u6-l4", "reading",
            ("The village that shares its land",
             "روستایی که زمینش را شریک می‌شود"),
            ("Read an account of a collective arrangement and find the "
             "condition that keeps it working.",
             "روایتی از یک ترتیب جمعی بخوان و شرطی را بیاب که آن را سرپا "
             "نگه می‌دارد."),
            [
                ("Texts about collective arrangements usually name the rule "
                 "that makes them work, and the rule is often a relative "
                 "clause: the families who joined first, the plot that nobody "
                 "wanted. Reduced relatives make the description compact: the "
                 "families joining first.",
                 "متن‌های ترتیب‌های جمعی معمولاً قاعده‌ای را نام می‌برند که آن را "
                 "سرپا نگه می‌دارد و قاعده اغلب بند موصولی است: the families "
                 "who joined first، the plot that nobody wanted. موصولی "
                 "کوتاه‌شده توصیف را جمع‌وجور می‌کند: the families joining "
                 "first."),
                ("The condition is what the reader must extract: it works as "
                 "long as everyone contributes, and it stops the moment one "
                 "family sells.",
                 "شرط همان چیزی است که خواننده باید بیرون بکشد: تا وقتی همه سهم "
                 "بدهند کار می‌کند و لحظه‌ای که یک خانواده بفروشد می‌ایستد."),
            ],
            [
                ("The families joining first had the smallest plots.",
                 "خانواده‌هایی که اول آمدند کوچک‌ترین زمین‌ها را داشتند."),
                ("It works as long as nobody sells.",
                 "تا وقتی کسی نفروشد کار می‌کند."),
            ],
            [
                mcq("What keeps the arrangement working?",
                    "چه چیزی این ترتیب را سرپا نگه می‌دارد؟",
                    ["the size of the plots", "the rule against selling",
                     "the council", "the weather"], 1,
                    "Nobody may sell.", "هیچ‌کس نباید بفروشد."),
                mcq("'The families joining first' is ___.", "«The families "
                    "joining first» ___ است.",
                    ["a full relative clause", "a reduced relative",
                     "a conditional", "a passive"], 1,
                    "The relative pronoun and verb are dropped.",
                    "ضمیر موصولی و فعل حذف شده‌اند."),
            ],
            [
                mcq("Who has the smallest plots?", "کوچک‌ترین زمین‌ها از "
                    "کیست؟",
                    ["the newest families", "the families who joined first",
                     "the council", "nobody"], 1,
                    "Joined first, smallest plots.", "اول آمدند، زمین کوچک‌تر."),
                mcq("What would end the arrangement?", "چه چیزی ترتیب را "
                    "پایان می‌دهد؟",
                    ["a bad harvest", "one family selling its share",
                     "a new council", "a dry year"], 1,
                    "The rule is about selling.", "قاعده دربارهٔ فروش است."),
            ],
            passage=passage(
                ("The village that shares its land",
                 "روستایی که زمینش را شریک می‌شود"),
                ("The arrangement began with eleven families and a field that "
                 "nobody wanted. The families joining first took the smallest "
                 "plots, which sounds unfair until you notice that they also "
                 "took the plots nearest the water. What they agreed was "
                 "simple and, for thirty years, sufficient: the field is "
                 "worked together, the harvest is divided by household, and no "
                 "share may be sold to anyone outside the village.\n\n"
                "The rule that keeps it working is not the sharing. It is the "
                "prohibition, and everybody knows it. Two families have asked "
                "to leave over the years, and both were bought out by the "
                "others at a price agreed in a meeting that lasted three "
                "evenings. The village is not a commune and does not describe "
                "itself as one; it is a group of people who found that the "
                "cheapest way to keep a field is to make it impossible to sell "
"half of it.",
                "این ترتیب با یازده خانواده و زمینی که کسی نمی‌خواست آغاز شد. "
                "خانواده‌هایی که اول آمدند کوچک‌ترین قطعه‌ها را گرفتند که ناعادلانه به گوش "
                "می‌رسد تا وقتی ببینی نزدیک‌ترین قطعه‌ها به آب را هم گرفتند. آنچه توافق "
                "کردند ساده بود و سی سال کافی: زمین با هم کشت می‌شود، محصول به تناسب "
                "خانوار تقسیم می‌شود و هیچ سهمی به کسی بیرون از روستا فروخته نمی‌شود.\n\n "
                "قاعده‌ای که آن را سرپا نگه می‌دارد تقسیم نیست، ممنوعیت است و همه "
                "می‌دانندش. دو خانواده در این سال‌ها خواستند بروند و هر دو را دیگران با "
                "قیمتی خریدند که در جلسه‌ای سه‌شبه توافق شد. روستا کمون نیست و خودش را "
                "چنین نمی‌نامد؛ گروهی است که فهمیدند ارزان‌ترین راه نگه‌داشتن یک زمین این "
                "است که فروش نصفش را ناممکن کنند."),
            ),
        ),
    ],
    "b2-u7": [
        lesson(
            "b2-u7-l4", "writing",
            ("The letter to the council",
             "نامه به شورای شهر"),
            ("Write a formal letter that argues for a decision and answers the "
             "obvious objection.",
             "نامهٔ رسمی بنویس که از تصمیمی دفاع کند و به اعتراض آشکار پاسخ "
             "دهد."),
            [
                ("A letter to a council is read by someone who has forty of "
                 "them. Put your ask in the first two lines, and use the "
                 "inversion you have learned for the one sentence that must "
                 "not be skimmed: Not only would the scheme pay for itself, it "
                 "would do so within four years.",
                 "نامه به شورا را کسی می‌خواند که چهل نامهٔ دیگر هم دارد. "
                 "درخواستت را در دو سطر اول بگذار و برای تنها جمله‌ای که نباید "
                 "سرسری خوانده شود از جابه‌جایی استفاده کن: Not only would the "
                 "scheme pay for itself, it would do so within four years."),
                ("The objection you answer should be the one your reader will "
                 "actually raise — cost, disruption, or precedent — and the "
                 "answer should be a fact, not a hope.",
                 "اعتراضی که پاسخ می‌دهی باید همانی باشد که خواننده واقعاً مطرح "
                 "می‌کند — هزینه، اختلال یا پیشینه — و پاسخ باید واقعیت باشد نه "
                 "امید."),
            ],
            [
                ("Not only would the scheme pay for itself, it would do so "
                 "within four years.", "این طرح نه‌تنها هزینه‌اش را برمی‌گرداند، "
                 "بلکه در چهار سال چنین می‌کند."),
                ("The objection is cost, and the answer is the repair budget.",
                 "اعتراض هزینه است و پاسخش بودجهٔ تعمیرات."),
            ],
            [
                mcq("The ask belongs ___.", "درخواست جا دارد ___.",
                    ["in the last paragraph", "in the first two lines",
                     "in the subject line only", "nowhere"], 1,
                    "Readers skim; the ask must survive skimming.",
                    "خواننده سرسری می‌خواند و درخواست باید از آن جان به‌در ببرد."),
                mcq("Inversion is used here to ___.", "جابه‌جایی اینجا برای "
                    "___ به کار رفته است.",
                    ["sound formal", "make one sentence impossible to skim",
                     "shorten the letter", "avoid the passive"], 1,
                    "The marked order slows the reader down.",
                    "ترتیب نشان‌دار خواننده را کند می‌کند."),
            ],
            [
                write("Write a letter of about 150 words to a council asking "
                      "it to publish the waiting times of every service. Put "
                      "the ask first, use one inversion, answer the cost "
                      "objection with a fact.",
                      "نامه‌ای حدود ۱۵۰ واژه به شورای شهر بنویس و بخواه زمان "
                      "انتظار هر خدمت را منتشر کند. درخواست را اول بگذار، یک "
                      "جابه‌جایی به کار ببر و به اعتراض هزینه با یک واقعیت پاسخ "
                      "بده.",
                      150, ["although", "whereas"],
                      "Ask in two lines, one negative inversion, the strongest "
                      "objection answered with a fact, and a closing request "
                      "with a date.", "درخواست در دو سطر، یک جابه‌جایی منفی، "
                      "قوی‌ترین اعتراض با واقعیت پاسخ داده شود و درخواست پایانی "
                      "با تاریخ."),
                mcq("Which sentence uses negative inversion?", "کدام جمله "
                    "جابه‌جایی منفی دارد؟",
                    ["Not only does it cost less, it works better.",
                     "It does not only cost less.", "Not only it costs less.",
                     "It costs less, not more."], 0,
                    "Not only + auxiliary + subject.", "not only + کمکی + نهاد."),
                gap("Rarely ___ a council changed its mind so quickly.",
                    ["has"], "Fronted rarely inverts.", "rarely در آغاز "
                    "جابه‌جایی می‌خواهد.", "one word"),
            ],
        ),
    ],
    "b2-u8": [
        lesson(
            "b2-u8-l4", "speaking",
            ("The question you did not want",
             "پرسشی که نمی‌خواستی"),
            ("Answer a hostile question in a presentation without losing the "
             "argument.",
             "در ارائه به پرسشی خصمانه پاسخ بده بی‌آنکه استدلال را از دست بدهی."),
            [
                ("A hostile question has a hidden premise, and the answer "
                 "begins by naming it: you are asking why we did not consult, "
                 "and the premise is that consultation was possible in March.",
                 "پرسش خصمانه پیش‌فرضی پنهان دارد و پاسخ با نام‌بردن از آن آغاز "
                 "می‌شود: you are asking why we did not consult, and the "
                 "premise is that consultation was possible in March."),
                ("Participle clauses make the answer short and calm: having "
                 "spoken to both sites, I can say the delay was agreed. They "
                 "compress the evidence into a phrase and leave your sentence "
                 "for the claim.",
                 "بندهای وجه وصفی پاسخ را کوتاه و آرام می‌کنند: having spoken "
                 "to both sites, I can say the delay was agreed. شاهد را در "
                 "عبارتی فشرده می‌کنند و جمله را برای ادعا می‌گذارند."),
            ],
            [
                ("Having spoken to both sites, I can say the delay was agreed.",
                 "با هر دو سایت صحبت کرده‌ام و می‌توانم بگویم تأخیر توافقی بود."),
                ("The premise of that question is that we had a choice.",
                 "پیش‌فرض آن پرسش این است که ما انتخاب داشتیم."),
            ],
            [
                mcq("The first move in answering a hostile question is ___.",
                    "نخستین حرکت در پاسخ به پرسش خصمانه ___ است.",
                    ["apologising", "naming its premise", "changing the "
                     "subject", "repeating your point"], 1,
                    "The premise is where the disagreement lives.",
                    "پیش‌فرض جای اختلاف است."),
                mcq("'Having spoken to both sites' is a ___.", "«Having spoken "
                    "to both sites» یک ___ است.",
                    ["gerund", "participle clause", "relative clause",
                     "conditional"], 1,
                    "It compresses prior evidence.", "شاهد پیشین را فشرده "
                    "می‌کند."),
            ],
            [
                say("If I understand the question, you are asking why we did "
                    "not consult, and the premise is that consultation was "
                    "possible in March.", "اگر درست فهمیده باشم می‌پرسید چرا "
                    "مشورت نکردیم و پیش‌فرض این است که در مارس مشورت ممکن بود."),
                say("Having spoken to both sites, I can say the delay was "
                    "agreed, not imposed.", "با هر دو سایت صحبت کرده‌ام و "
                    "می‌توانم بگویم تأخیر توافقی بود، نه تحمیلی."),
                say("I would rather be judged on the condition we attached "
                    "than on the date we missed.",
                    "ترجیح می‌دهم دربارهٔ شرطی که گذاشتیم قضاوت شوم تا تاریخی که "
                    "از دست دادیم."),
            ],
        ),
    ],
}
