#!/usr/bin/env python3
"""Eight lessons that deepen C1: one per unit, each turning the unit's grammar
into a text to read, a recording to follow or a performance to give."""

from course_kit import gap, lesson, listen, mcq, passage, say, write

EXTRA = {
    "c1-u1": [
        lesson(
            "c1-u1-l4", "speaking",
            ("The viva: defending a reading",
             "دفاع: از یک خوانش دفاع کن"),
            ("Defend an interpretation of a text and concede what the text "
             "will not support.",
             "از تفسیری از یک متن دفاع کن و بپذیر متن چه را پشتیبانی نمی‌کند."),
            [
                ("A defended reading has three parts: what the text does, "
                 "what that does to a reader, and what it does not settle. The "
                 "cleft is useful for the middle one: what the last paragraph "
                 "does is withdraw the promise the first one made.",
                 "خوانش مدافع سه بخش دارد: متن چه می‌کند، این با خواننده چه "
                 "می‌کند و چه را فیصله نمی‌دهد. جملهٔ شکافته برای بخش میانی "
                 "سودمند است: what the last paragraph does is withdraw the "
                 "promise the first one made."),
                ("Conceding is a move, not a retreat: the text does not tell "
                 "us why she leaves, and I would not want it to. Naming the "
                 "silence as a choice shows you have read the whole thing.",
                 "واگذاری یک حرکت است نه عقب‌نشینی: the text does not tell us "
                 "why she leaves, and I would not want it to. نام‌بردن از سکوت "
                 "به‌عنوان انتخاب نشان می‌دهد تمام متن را خوانده‌ای."),
            ],
            [
                ("What the ending does is refuse the explanation.",
                 "آنچه پایان می‌کند رد کردن توضیح است."),
                ("The text does not tell us why she leaves, and that is the "
                 "point.", "متن نمی‌گوید چرا می‌رود و همین نکته است."),
            ],
            [
                mcq("A cleft is used here to ___.", "جملهٔ شکافته اینجا برای "
                    "___ به کار رفته است.",
                    ["shorten the answer", "separate what the text does from "
                     "what it says", "sound formal", "avoid an opinion"], 1,
                    "It splits the doing from the saying.",
                    "کردن را از گفتن جدا می‌کند."),
                mcq("Naming the silence as a choice shows ___.",
                    "نام‌بردن از سکوت به‌عنوان انتخاب نشان می‌دهد ___.",
                    ["you disagree", "you have read the whole text",
                     "you are unsure", "the text is weak"], 1,
                    "It is evidence of a reading, not a mood.",
                    "شاهدی بر خواندن است، نه حال‌وهوا."),
            ],
            [
                say("What the last paragraph does is withdraw the promise the "
                    "first one made.",
                    "آنچه بند آخر می‌کند پس گرفتن وعده‌ای است که بند اول داد."),
                say("It is the silence, not the sentence, that carries the "
                    "judgment.", "این سکوت است، نه جمله، که داوری را حمل "
                    "می‌کند."),
                say("The text does not tell us why she leaves, and I would not "
                    "want it to; a reason would make it a different book.",
                    "متن نمی‌گوید چرا می‌رود و من هم نمی‌خواهم بگوید؛ دلیل آن را "
                    "کتاب دیگری می‌کرد."),
            ],
        ),
    ],
    "c1-u2": [
        lesson(
            "c1-u2-l4", "reading",
            ("The editorial that admits doubt",
             "سرمقاله‌ای که تردید را می‌پذیرد"),
            ("Read an argument that marks its own uncertainty and find where "
             "the doubt is doing work.",
             "استدلالی بخوان که تردید خودش را نشانه‌گذاری می‌کند و ببین تردید "
             "کجا کار می‌کند."),
            [
                ("Modal perfects let a writer say what probably happened "
                 "without claiming it: the warning may have been lost in the "
                 "handover. In an editorial this is not weakness but "
                 "protection — the claim survives if the fact does not.",
                 "وجهی کامل به نویسنده اجازه می‌دهد بگوید چه احتمالاً رخ داده "
                 "بی‌آنکه ادعایش کند: the warning may have been lost in the "
                 "handover. در سرمقاله این ضعف نیست، محافظت است — ادعا می‌ماند "
                 "حتی اگر واقعیت نماند."),
                ("Find where the doubt is placed. If it is on the evidence, "
                 "the argument is careful; if it is on the conclusion, the "
                 "argument is retreating. The position of the modal tells you "
                 "which.",
                 "ببین تردید کجا نشسته. اگر روی شاهد باشد، استدلال محتاط است؛ اگر "
                 "روی نتیجه باشد، استدلال عقب می‌نشیند. جای وجهی همین را "
                 "می‌گوید."),
            ],
            [
                ("The warning may have been lost in the handover.",
                 "ممکن است هشدار در تحویل کار گم شده باشد."),
                ("The figures should have been published in March.",
                 "ارقام باید در مارس منتشر می‌شد."),
            ],
            [
                mcq("'May have been lost' claims ___.", "«may have been lost» "
                    "ادعا می‌کند ___.",
                    ["it was lost", "it possibly was lost", "it was not lost",
                     "nobody knows anything"], 1,
                    "Possibility, not fact.", "امکان، نه واقعیت."),
                mcq("Doubt placed on the evidence makes the argument ___.",
                    "تردید روی شاهد استدلال را ___ می‌کند.",
                    ["careful", "weak", "personal", "emotional"], 0,
                    "It stays inside what is known.", "داخل دانسته‌ها می‌ماند."),
            ],
            [
                mcq("'Should have been published' means ___.", "«should have "
                    "been published» یعنی ___.",
                    ["it was published", "it was not, and that was wrong",
                     "it may be published", "it will be published"], 1,
                    "Should have + participle criticizes a past omission.",
                    "should have + اسم مفعول یک کوتاهی گذشته را نقد می‌کند."),
                mcq("Which sentence retreats from its own conclusion?",
                    "کدام جمله از نتیجهٔ خودش عقب می‌نشیند؟",
                    ["The delay was caused by the handover.",
                     "The delay may have been caused by the handover, or by "
                     "something we cannot see.",
                     "The handover caused the delay.",
                     "The evidence points to the handover."], 1,
                    "The doubt is on the conclusion, not the detail.",
                    "تردید روی نتیجه است، نه جزئیات."),
            ],
            passage=passage(
                ("The warning nobody received",
                 "هشداری که به کسی نرسید"),
                ("The warning may have been lost in the handover, and the "
                 "handover, by all accounts, was rushed. Two officials say the "
                 "email was sent on the Friday; a third says it was drafted "
                 "and never sent. The figures should have been published in "
                 "March and were not, which is not in dispute. What is in "
                 "dispute is whether anyone read the warning before the "
                 "decision, and on that question the record is silent rather "
                 "than clear.\n\n"
                "It would be satisfying to say that the department ignored a "
                "warning. The evidence does not support that sentence and "
                "supports a duller one: nobody can now show that the warning "
                "reached the person who decided. A department that cannot show "
                "this has a record-keeping problem, and a record-keeping "
                "problem is not a scandal, which is precisely why it is "
                "allowed to continue.\n\n"
                "The recommendation, then, is not a resignation. It is that "
                "every decision of this kind should be able to name the "
                "documents in front of the person who took it. That would have "
                "settled this argument in an afternoon, and it would settle "
"the next one too.",
                "هشدار ممکن است در تحویل کار گم شده باشد و تحویل کار، به گفتهٔ همه، با عجله "
                "انجام شده. دو مقام می‌گویند ایمیل جمعه فرستاده شد و سومی می‌گوید نوشته شد "
                "و هرگز فرستاده نشد. ارقام باید در مارس منتشر می‌شدند و نشدند و این محل "
                "اختلاف نیست. محل اختلاف این است که آیا کسی هشدار را پیش از تصمیم خوانده "
                "است یا نه و در این باره سند ساکت است، نه روشن.\n\n "
                "خوشایند بود اگر می‌گفتیم اداره هشداری را نادیده گرفته است. شاهد از آن جمله "
                "پشتیبانی نمی‌کند و از جملهٔ کسل‌کننده‌تری پشتیبانی می‌کند: هیچ‌کس حالا "
                "نمی‌تواند نشان دهد هشدار به کسی رسیده که تصمیم گرفته است. اداره‌ای که "
                "نمی‌تواند این را نشان دهد مشکل بایگانی دارد و مشکل بایگانی رسوایی نیست و "
                "دقیقاً به همین دلیل اجازه دارد ادامه یابد.\n\n "
                "پس توصیه استعفا نیست. توصیه این است که هر تصمیم از این نوع باید بتواند "
                "سندهایی را که پیش روی تصمیم‌گیرنده بوده نام ببرد. این کار آن بحث را در یک "
                "بعدازظهر فیصله می‌داد و بحث بعدی را هم فیصله می‌دهد."),
            ),
        ),
    ],
    "c1-u3": [
        lesson(
            "c1-u3-l4", "listening",
            ("The policy briefing",
             "جلسهٔ توجیهی سیاست"),
            ("Follow a briefing where every claim is attached to a document.",
             "جلسهٔ توجیهی‌ای را دنبال کن که هر ادعا به سندی بسته است."),
            [
                ("In a briefing, attribution is the information. The same "
                 "sentence means different things depending on whether it "
                 "follows 'the review found' or 'the department believes'.",
                 "در جلسهٔ توجیهی، انتساب خودِ اطلاعات است. یک جمله بسته به "
                 "اینکه پس از «the review found» بیاید یا «the department "
                 "believes» معنایی دیگر دارد."),
                ("Nominalizations are the warning signs: an 'assessment of "
                 "options' usually means nobody has chosen. Listen for the "
                 "abstract noun and ask what concrete decision it replaces.",
                 "اسم‌سازی‌ها نشانهٔ هشدارند: «an assessment of options» معمولاً "
                 "یعنی هیچ‌کس انتخاب نکرده. به اسم انتزاعی گوش کن و بپرس چه "
                 "تصمیم مشخصی را جای‌گزین می‌کند."),
            ],
            [
                ("The review found that the process was sound.",
                 "بازبینی یافت که فرایند سالم بود."),
                ("The department believes the delay was unavoidable.",
                 "اداره باور دارد تأخیر ناگزیر بود."),
            ],
            [
                mcq("Which phrase marks a belief rather than a finding?",
                    "کدام عبارت باور را نشان می‌دهد نه یافته را؟",
                    ["the review found", "the data show", "the department "
                     "believes", "the audit confirmed"], 2,
                    "Belief is not evidence.", "باور شاهد نیست."),
                mcq("'An assessment of options' usually means ___.",
                    "«an assessment of options» معمولاً یعنی ___.",
                    ["a decision was made", "no decision was made",
                     "the options are equal", "the cost is known"], 1,
                    "The noun hides the absence of a choice.",
                    "اسم، نبودِ انتخاب را پنهان می‌کند."),
            ],
            [
                listen("The review found the process sound. It did not examine "
                       "the outcome, which is a separate question.",
                       "What did the review not examine?",
                       "بازبینی چه را بررسی نکرد؟",
                       ["the process", "the outcome", "the cost", "the "
                        "staff"], 1,
                       "The outcome was out of scope.", "نتیجه بیرون از دامنه "
                       "بود."),
                listen("We are doing an assessment of options, so I cannot give "
                       "you a date.",
                       "Why can the speaker not give a date?",
                       "چرا گوینده تاریخ نمی‌دهد؟",
                       ["the date is secret", "no decision has been made",
                        "the date is unknown", "the review is late"], 1,
                       "Assessing options means not yet choosing.",
                       "سنجش گزینه‌ها یعنی هنوز انتخاب نشده."),
                listen("According to the minutes, the decision was taken in "
                       "March. The minutes do not say by whom.",
                       "What do the minutes omit?", "صورت‌جلسه چه را حذف "
                       "می‌کند؟",
                       ["the date", "who decided", "the decision", "the "
                        "meeting"], 1,
                       "The agent is missing.", "کنشگر غایب است."),
            ],
        ),
    ],
    "c1-u4": [
        lesson(
            "c1-u4-l4", "speaking",
            ("The panel: answering with less",
             "پنل: با کمتر گفتن پاسخ دادن"),
            ("Answer short questions precisely, using substitution instead of "
             "repetition.",
             "به پرسش‌های کوتاه دقیق پاسخ بده و به‌جای تکرار از جانشینی "
             "استفاده کن."),
            [
                ("In a panel, the shortest accurate answer wins. Substitution "
                 "does the work: I think so, I am afraid not, most of them have "
                 "and the rest have not. Repetition makes you sound unsure; "
                 "substitution makes you sound in control.",
                 "در پنل، کوتاه‌ترین پاسخ دقیق برنده است. جانشینی کار را می‌کند: "
                 "I think so، I am afraid not، most of them have and the rest "
                 "have not. تکرار مردد به گوش می‌رسد و جانشینی مسلط."),
                ("Ellipsis after auxiliaries is the mark of a confident "
                 "speaker: some sites did, and some did not. The verb is left "
                 "out because the listener already has it.",
                 "حذف پس از افعال کمکی نشانهٔ گویندهٔ مطمئن است: some sites "
                 "did, and some did not. فعل حذف می‌شود چون شنونده آن را دارد."),
            ],
            [
                ("Has the report been published? — Not yet, I am afraid.",
                 "گزارش منتشر شده؟ — متأسفانه هنوز نه."),
                ("Did all the sites agree? — Most did, and two did not.",
                 "همهٔ سایت‌ها موافقت کردند؟ — بیشترشان بله و دو تا نه."),
            ],
            [
                mcq("Substitution is preferred because it ___.", "جانشینی ترجیح "
                    "دارد چون ___.",
                    ["is shorter and shows control", "is more polite",
                     "hides the answer", "sounds formal"], 0,
                    "It answers without repeating.", "بی‌تکرار پاسخ می‌دهد."),
                mcq("'Most did, and two did not' uses ___.", "«Most did, and "
                    "two did not» از ___ استفاده می‌کند.",
                    ["repetition", "ellipsis", "inversion", "a cleft"], 1,
                    "The verb is understood, not repeated.",
                    "فعل فهمیده می‌شود و تکرار نمی‌شود."),
            ],
            [
                say("Has it been published? Not yet, I am afraid, and I can "
                    "give you the date on Thursday.",
                    "منتشر شده؟ متأسفانه هنوز نه، و پنجشنبه تاریخ را می‌دهم."),
                say("Did every site agree? Most did, and the two newest did "
                    "not.", "همهٔ سایت‌ها موافقت کردند؟ بیشترشان بله و دو "
                    "تازه‌وارد نه."),
                say("I think so, though I would want to check the second year "
                    "before saying it plainly.",
                    "فکر می‌کنم بله، هرچند پیش از صریح گفتن می‌خواهم سال دوم را "
                    "بررسی کنم."),
            ],
        ),
    ],
    "c1-u5": [
        lesson(
            "c1-u5-l4", "writing",
            ("The literature note",
             "یادداشت مروری"),
            ("Summarize three sources in one paragraph that keeps their "
             "disagreement visible.",
             "سه منبع را در یک بند خلاصه کن که اختلافشان دیده شود."),
            [
                ("A literature note is not three summaries in a row. It is one "
                 "paragraph organized by the question, with each source "
                 "attached to what it contributes and where it parts from the "
                 "others: two studies find a local effect; a third, using a "
                 "larger sample, finds none.",
                 "یادداشت مروری سه خلاصهٔ پشت‌سرهم نیست. یک بند است که با پرسش "
                 "سازمان می‌یابد و هر منبع به آنچه می‌افزاید و جایی که جدا "
                 "می‌شود بسته است: two studies find a local effect; a third, "
                 "using a larger sample, finds none."),
                ("Reporting passives keep the note about the evidence rather "
                 "than the authors: the effect has been reported in two "
                 "trials. Use the active only when the author matters.",
                 "مجهولِ نقل یادداشت را دربارهٔ شاهد نگه می‌دارد نه نویسندگان: the "
                 "effect has been reported in two trials. معلوم را تنها وقتی به "
                 "کار ببر که نویسنده مهم باشد."),
            ],
            [
                ("The effect has been reported in two trials and not in a "
                 "third.", "اثر در دو آزمایش گزارش شده و در سومی نه."),
                ("The larger study has been read as a refutation.",
                 "مطالعهٔ بزرگ‌تر ردِ نظریه خوانده شده است."),
            ],
            [
                mcq("A literature note is organized by ___.", "یادداشت مروری "
                    "با ___ سازمان می‌یابد.",
                    ["author", "date", "question", "length"], 2,
                    "The question holds the sources together.",
                    "پرسش منابع را کنار هم نگه می‌دارد."),
                mcq("A reporting passive keeps the focus on ___.", "مجهولِ نقل "
                    "تمرکز را روی ___ نگه می‌دارد.",
                    ["the authors", "the evidence", "the journal", "the "
                     "reader"], 1,
                    "Who did it matters less than what was found.",
                    "چه کسی کرد از چه یافت شد کم‌اهمیت‌تر است."),
            ],
            [
                write("Write a note of about 150 words summarizing three "
                      "studies of one question: two that agree and one that "
                      "does not. Keep the disagreement visible and use at "
                      "least two reporting passives.",
                      "یادداشتی حدود ۱۵۰ واژه بنویس که سه مطالعه دربارهٔ یک پرسش "
                      "را خلاصه کند: دو هم‌خوان و یکی ناهم‌خوان. اختلاف را دیده "
                      "کن و دست‌کم دو مجهولِ نقل به کار ببر.",
                      150, ["although", "whereas"],
                      "One paragraph by question, three sources, two "
                      "reporting passives, a closing sentence about what "
                      "would settle it.", "یک بند بر پایهٔ پرسش، سه منبع، دو "
                      "مجهول نقل و جملهٔ پایانی دربارهٔ اینکه چه چیزی آن را "
                      "فیصله می‌دهد."),
                gap("The effect ___ been reported in two trials.",
                    ["has"], "Present perfect passive.", "مجهول حال کامل.",
                    "one word"),
                mcq("Which sentence keeps the agent out?", "کدام جمله کنشگر را "
                    "بیرون می‌گذارد؟",
                    ["Two trials reported the effect.",
                     "The effect has been reported in two trials.",
                     "The authors reported the effect.",
                     "We found the effect in two trials."], 1,
                    "The passive omits who reported.", "مجهول چه کسی را حذف "
                    "می‌کند."),
            ],
        ),
    ],
    "c1-u6": [
        lesson(
            "c1-u6-l4", "reading",
            ("The minutes that record a disagreement",
             "صورت‌جلسه‌ای که اختلاف را ثبت می‌کند"),
            ("Read minutes and separate what was decided from what was only "
             "discussed.",
             "صورت‌جلسه را بخوان و تصمیم را از آنچه فقط بحث شد جدا کن."),
            [
                ("Minutes have a grammar of their own. 'It was agreed that' "
                 "marks a decision; 'the committee considered' marks a "
                 "discussion; 'it was recommended that' marks advice that still "
                 "needs a decision. Reading minutes means sorting those three.",
                 "صورت‌جلسه گرامر خودش را دارد. «It was agreed that» تصمیم را "
                 "نشان می‌دهد؛ «the committee considered» بحث را؛ «it was "
                 "recommended that» توصیه‌ای را که هنوز تصمیم می‌خواهد. خواندن "
                 "صورت‌جلسه یعنی جدا کردن این سه."),
                ("The subjunctive after recommend is the formal marker: it was "
                 "recommended that the policy be reviewed. That is not a "
                 "decision, however much it sounds like one.",
                 "وجه شرطی پس از recommend نشانهٔ رسمی است: it was recommended "
                 "that the policy be reviewed. این تصمیم نیست، هرقدر هم که "
                 "تصمیم به گوش برسد."),
            ],
            [
                ("It was agreed that the trial would continue.",
                 "توافق شد که آزمایش ادامه یابد."),
                ("It was recommended that the figures be published.",
                 "توصیه شد ارقام منتشر شوند."),
            ],
            [
                mcq("'It was agreed that' marks ___.", "«It was agreed that» "
                    "نشانهٔ ___ است.",
                    ["a discussion", "a decision", "advice", "a doubt"], 1,
                    "Agreement is the decision.", "توافق همان تصمیم است."),
                mcq("'The committee considered' means ___.", "«The committee "
                    "considered» یعنی ___.",
                    ["it decided", "it discussed without deciding",
                     "it refused", "it postponed"], 1,
                    "Consideration is not a decision.",
                    "بررسی تصمیم نیست."),
            ],
            [
                mcq("'It was recommended that the policy be reviewed' is ___.",
                    "«It was recommended that the policy be reviewed» ___ است.",
                    ["a decision", "advice awaiting a decision", "a refusal",
                     "a legal order"], 1,
                    "Recommendation needs a later decision.",
                    "توصیه تصمیم بعدی می‌خواهد."),
                mcq("Which sentence reports a decision?", "کدام جمله تصمیم را "
                    "گزارش می‌کند؟",
                    ["The committee considered the report.",
                     "It was agreed to extend the pilot.",
                     "It was suggested that costs might rise.",
                     "Officers were asked to look into it."], 1,
                    "Agreed marks the decision.", "agreed تصمیم را نشان "
                    "می‌دهد."),
            ],
            passage=passage(
                ("Minutes: waiting times review",
                 "صورت‌جلسه: بازبینی زمان‌های انتظار"),
                ("Present: the chair, four members, two officers.\n\n"
                 "1. The committee considered the review of waiting times. "
                 "Officers reported that the median wait had fallen and that "
                 "the longest wait had risen. It was noted that the two "
                 "figures had not previously been published together.\n\n"
                 "2. It was agreed that the pilot would continue for a second "
                 "year at the same two sites.\n\n"
                 "3. It was recommended that the full figures, including the "
                 "longest wait, be published quarterly. Two members asked "
                 "whether the publication should wait for the second year. It "
                 "was suggested that delaying publication would itself be a "
                 "finding.\n\n"
                 "4. It was agreed that officers would prepare a note on the "
                 "cost of quarterly publication, and that the recommendation "
                 "at 3 would return to the next meeting.\n\n"
"5. The meeting closed at 16:40.",
                 "حاضران: رئیس، چهار عضو، دو کارشناس.\n\n "
                 "۱. کمیته بازبینی زمان‌های انتظار را بررسی کرد. کارشناسان گزارش دادند که "
                 "میانهٔ انتظار کاهش یافته و طولانی‌ترین انتظار افزایش یافته است. یادآوری شد "
                 "که این دو رقم پیش‌تر با هم منتشر نشده بودند.\n\n "
                 "۲. توافق شد که آزمایش برای سال دومی در همان دو سایت ادامه یابد.\n\n "
                 "۳. توصیه شد ارقام کامل، از جمله طولانی‌ترین انتظار، هر سه ماه منتشر شوند. "
                 "دو عضو پرسیدند آیا انتشار باید تا سال دوم صبر کند. پیشنهاد شد که تعویق "
                 "انتشار خودش یافته‌ای باشد.\n\n "
                 "۴. توافق شد که کارشناسان یادداشتی دربارهٔ هزینهٔ انتشار سه‌ماهه آماده کنند و "
                 "توصیهٔ بند ۳ به نشست بعد بازگردد.\n\n "
                 "۵. جلسه در ساعت ۱۶:۴۰ بسته شد."),
            ),
        ),
    ],
    "c1-u7": [
        lesson(
            "c1-u7-l4", "listening",
            ("The interview that changes its mind",
             "مصاحبه‌ای که نظرش عوض می‌شود"),
            ("Follow an interview where the speaker revises a position mid-"
             "conversation.",
             "مصاحبه‌ای را دنبال کن که گوینده در میانهٔ گفت‌وگو موضعش را "
             "بازنگری می‌کند."),
            [
                ("A revision is announced by a small set of phrases: having "
                 "said that, I would qualify that, let me put it differently. "
                 "The phrase is the signpost; the revision follows.",
                 "بازنگری با مجموعهٔ کوچکی از عبارات اعلام می‌شود: having said "
                 "that، I would qualify that، let me put it differently. عبارت "
                 "نشانه است و بازنگری پس از آن می‌آید."),
                ("Participle clauses make the revision graceful: having "
                 "argued for a year, I now think six months would have shown "
                 "the same. The clause carries the old position so the new one "
                 "does not have to apologize.",
                 "بندهای وجه وصفی بازنگری را نرم می‌کنند: having argued for a "
                 "year, I now think six months would have shown the same. بند، "
                 "موضع قدیم را حمل می‌کند تا موضع تازه مجبور به عذرخواهی نباشد."),
            ],
            [
                ("Having said that, I would qualify the second point.",
                 "با این حال، نکتهٔ دوم را محدود می‌کنم."),
                ("Let me put it differently: the delay was a choice.",
                 "بگذار طور دیگری بگویم: تأخیر یک انتخاب بود."),
            ],
            [
                mcq("Which phrase announces a revision?", "کدام عبارت بازنگری "
                    "را اعلام می‌کند؟",
                    ["In addition", "Having said that", "As I said before",
                     "Furthermore"], 1,
                    "It signals the turn.", "گردش را نشان می‌دهد."),
                mcq("'Having argued for a year' is a ___.", "«Having argued for "
                    "a year» یک ___ است.",
                    ["gerund", "participle clause", "conditional",
                     "relative clause"], 1,
                    "It carries the previous position.", "موضع پیشین را حمل "
                    "می‌کند."),
            ],
            [
                listen("I spent two years saying the pilot was too small. "
                       "Having seen the second site, I would say it was small "
                       "and enough.",
                       "What has the speaker changed?", "گوینده چه را عوض "
                       "کرده است؟",
                       ["the size of the pilot", "the judgment of the pilot",
                        "the sites", "the year"], 1,
                       "Small and enough replaces too small.",
                       "«small and enough» جای «too small» را می‌گیرد."),
                listen("Let me put it differently. It is not that the data are "
                       "weak; it is that they answer a different question.",
                       "What is the speaker correcting?",
                       "گوینده چه را تصحیح می‌کند؟",
                       ["the data quality", "the framing of the objection",
                        "the question", "the answer"], 1,
                       "The objection is reframed, not withdrawn.",
                       "اعتراض بازچهارچوب می‌شود، پس گرفته نمی‌شود."),
                listen("Having recommended publication, I now think the "
                       "quarterly note should include the longest wait.",
                       "What does the speaker now recommend?",
                       "گوینده حالا چه توصیه می‌کند؟",
                       ["no publication", "a quarterly note with the longest "
                        "wait", "a yearly report", "a new review"], 1,
                       "The recommendation is extended, not dropped.",
                       "توصیه گسترده می‌شود، حذف نمی‌شود."),
            ],
        ),
    ],
    "c1-u8": [
        lesson(
            "c1-u8-l4", "speaking",
            ("The closing statement",
             "بیانیهٔ پایانی"),
            ("Close a discussion with a summary that keeps what is unresolved "
             "in view.",
             "بحثی را با خلاصه‌ای ببند که ناحل‌شده را دیده نگه دارد."),
            [
                ("A closing statement does three things in ninety seconds: "
                 "what was agreed, what was not, and what happens next. The "
                 "inversion earns its place here: rarely has a decision been "
                 "so well prepared and so little understood.",
                 "بیانیهٔ پایانی در نود ثانیه سه کار می‌کند: چه توافق شد، چه نشد و "
                 "بعد چه می‌شود. جابه‌جایی اینجا جای خودش را می‌گیرد: rarely has "
                 "a decision been so well prepared and so little understood."),
                ("Do not summarize the discussion; summarize the state. A "
                 "listener who missed the meeting needs to know what is now "
                 "true, not who said what.",
                 "بحث را خلاصه نکن؛ وضع را خلاصه کن. شنونده‌ای که جلسه را ندیده "
                 "باید بداند حالا چه درست است، نه اینکه چه کسی چه گفت."),
            ],
            [
                ("What we agreed is the second year at the same sites.",
                 "آنچه توافق کردیم سال دوم در همان سایت‌هاست."),
                ("Rarely has a decision been so well prepared and so little "
                 "understood.", "به‌ندرت تصمیمی این‌قدر خوب آماده و این‌قدر کم "
                 "فهمیده شده است."),
            ],
            [
                mcq("A closing statement summarizes ___.", "بیانیهٔ پایانی ___ "
                    "را خلاصه می‌کند.",
                    ["who spoke", "the state of the question", "the agenda",
                     "the minutes"], 1,
                    "The state, not the conversation.",
                    "وضع، نه گفت‌وگو."),
                mcq("The inversion in the example emphasizes ___.",
                    "جابه‌جایی در مثال ___ را تأکید می‌کند.",
                    ["the preparation", "the contrast between preparation and "
                     "understanding", "the decision", "the speaker"], 1,
                    "Two halves set against each other.", "دو نیمه در برابر "
                    "هم."),
            ],
            [
                say("What we agreed is a second year at the same two sites.",
                    "آنچه توافق کردیم سال دومی در همان دو سایت است."),
                say("What we did not settle is whether to publish quarterly, "
                    "and that returns next month.",
                    "آنچه فیصله ندادیم انتشار سه‌ماهه است و ماه بعد برمی‌گردد."),
                say("Rarely has a decision been so carefully prepared, and "
                    "rarely has so little of it been understood outside this "
                    "room.", "به‌ندرت تصمیمی این‌قدر با دقت آماده شده و به‌ندرت "
                    "این‌قدر کم از آن بیرون این اتاق فهمیده شده است."),
            ],
        ),
    ],
}
