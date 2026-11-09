#!/usr/bin/env python3
"""C2, units 5 and 6: whose account it is, and how a text holds together."""

from course_kit import (dialogue, gap, lesson, listen, mcq, passage, say,
                       unit, write)

U5 = unit(
    "c2-u5",
    ("Whose account is this", "این روایت از کیست"),
    ("Attribute claims to their sources, shift register deliberately, and "
     "negotiate without conceding the substance.",
     "ادعاها را به منابعشان نسبت بده، ثبت را آگاهانه عوض کن و بدون واگذاشتن "
     "جانِ مطلب مذاکره کن."),
    [
        lesson(
            "c2-u5-l1", "grammar",
            ("Attribution: who says so, and how sure they are",
             "انتساب: چه کسی می‌گوید و چقدر مطمئن است"),
            ("Report a claim without adopting it, and mark how committed the "
             "original speaker was.",
             "ادعایی را گزارش کن بی‌آنکه بپذیری و نشان بده گویندهٔ اصلی چقدر "
             "به آن متعهد بوده."),
            [
                ("Attribution has two jobs: naming the source and reproducing "
                 "its strength. 'The report claims' and 'the report shows' "
                 "describe the same document with different commitments. "
                 "Choosing the verb is choosing how much of the claim you "
                 "pass on.",
                 "انتساب دو کار دارد: نام‌بردن از منبع و بازتولید قدرت آن. "
                 "«The report claims» و «the report shows» یک سند را با دو "
                 "تعهد متفاوت توصیف می‌کنند. انتخاب فعل، انتخاب میزان انتقال "
                 "ادعاست."),
                ("The frames differ in formality and in distance. 'According "
                 "to X' is neutral and common in journalism. 'X maintains "
                 "that' signals a position the writer may not share. 'It is "
                 "said that' and 'X is reported to have' remove the speaker "
                 "entirely. 'X alleges' warns of an unproven charge, and is "
                 "close to a legal term.",
                 "ساخت‌ها در رسمیت و فاصله فرق دارند. «According to X» بی‌طرف "
                 "و روزنامه‌نگارانه است. «X maintains that» موضعی را نشان "
                 "می‌دهد که نویسنده شاید شریکش نباشد. «It is said that» و «X "
                 "is reported to have» گوینده را کامل حذف می‌کنند. «X "
                 "alleges» هشدار اتهامی اثبات‌نشده است و به اصطلاح حقوقی "
                 "نزدیک."),
                ("Do not stack distance on distance. 'It is believed that the "
                 "report allegedly suggests' tells the reader nothing about "
                 "who believes what. One frame per claim; if two sources "
                 "agree, say so plainly instead of hedging twice.",
                 "فاصله را روی فاصله نگذار. «It is believed that the report "
                 "allegedly suggests» هیچ نمی‌گوید که چه کسی چه را باور دارد. "
                 "برای هر ادعا یک ساخت؛ اگر دو منبع هم‌داستان‌اند صریح بگو، نه "
                 "با دو بار احتیاط."),
            ],
            [
                ("According to the minutes, the decision was unanimous.",
                 "بنا بر صورت‌جلسه، تصمیم unanimous بود."),
                ("The authors maintain that the effect persists after two "
                 "years.", "نویسندگان معتقدند اثر پس از دو سال باقی می‌ماند."),
                ("The company is reported to have known about the fault.",
                 "گفته می‌شود شرکت از نقص خبر داشته است."),
                ("The complaint alleges that the warning was removed.",
                 "شکایت ادعا می‌کند هشدار برداشته شده است."),
            ],
            [
                mcq("Which verb commits the writer least?", "کدام فعل کمترین "
                    "تعهد را برای نویسنده می‌سازد؟",
                    ["shows", "demonstrates", "claims", "proves"], 2,
                    "'Claims' reports without endorsing.", "«claims» گزارش "
                    "می‌کند بی‌آنکه تأیید کند."),
                mcq("'X is reported to have left' differs from 'X left' "
                    "because ___.", "«X is reported to have left» با «X "
                    "left» تفاوت دارد چون ___.",
                    ["it is more polite", "the writer does not vouch for it",
                     "it happened earlier", "it is less formal"], 1,
                    "The passive frame removes the writer's commitment.",
                    "ساخت مجهول تعهد نویسنده را برمی‌دارد."),
            ],
            [
                mcq("'Alleges' is appropriate when the charge is ___.",
                    "«alleges» جایی مناسب است که اتهام ___.",
                    ["proven", "unproven", "minor", "withdrawn"], 1,
                    "It marks an accusation not yet established.",
                    "اتهامی را نشان می‌دهد که هنوز اثبات نشده."),
                gap("___ to the summary, costs rose by a fifth.",
                    ["According"], "The frame takes 'to' + source.",
                    "این ساخت «to» و منبع می‌گیرد.", "one word"),
                mcq("Which sentence hedges twice and says nothing?",
                    "کدام جمله دو بار احتیاط می‌کند و هیچ نمی‌گوید؟",
                    ["The report suggests a link.", "It is believed that the "
                     "report may possibly suggest a link.",
                     "According to the report, a link is possible.",
                     "The report claims a link."], 1,
                    "Stacked distance hides who claims what.",
                    "فاصلهٔ انباشته پنهان می‌کند که چه کسی چه ادعایی دارد."),
                gap("The witness ___ that the light was red, a claim the "
                     "other driver denies.", ["maintains", "alleges"],
                    "Both keep the claim at arm's length; 'alleges' adds the "
                    "sense of a charge.", "هر دو ادعا را دور نگه می‌دارند و "
                    "«alleges» حس اتهام می‌افزاید.", "one word"),
            ],
        ),
        lesson(
            "c2-u5-l2", "vocabulary",
            ("Register shifting: same message, different room",
             "تغییر ثبت: یک پیام، اتاق‌های متفاوت"),
            ("Move a message between formal and informal registers without "
             "changing what it claims.",
             "پیامی را میان ثبت رسمی و غیررسمی جابه‌جا کن بی‌آنکه ادعایش عوض "
             "شود."),
            [
                ("Register is a set of consistent choices: vocabulary, "
                 "contraction, nominalisation, directness. 'We need to talk "
                 "about the budget' and 'a discussion of the budget is "
                 "required' carry the same content into different rooms. "
                 "Mixing the choices is what sounds wrong — a legal noun in a "
                 "friendly email reads as a threat.",
                 "ثبت مجموعه‌ای از انتخاب‌های هم‌خوان است: واژگان، کوتاه‌سازی، "
                 "اسم‌سازی، صراحت. «We need to talk about the budget» و «a "
                 "discussion of the budget is required» یک محتوا را به دو "
                 "اتاق متفاوت می‌برند. درهم‌کردن انتخاب‌هاست که نادرست به گوش "
                 "می‌رسد — اسم حقوقی در ایمیلی دوستانه مثل تهدید خوانده "
                 "می‌شود."),
                ("The usual direction in professional writing is towards "
                 "verbs: 'make a decision' becomes 'decide', 'conduct an "
                 "investigation' becomes 'investigate'. Nominalisation is not "
                 "wrong — it is how you keep a process at a distance, which is "
                 "sometimes exactly what a report needs — but it costs the "
                 "reader energy.",
                 "جهت معمول در نوشتار حرفه‌ای به سوی فعل است: «make a "
                 "decision» می‌شود «decide» و «conduct an investigation» "
                 "می‌شود «investigate». اسم‌سازی نادرست نیست — راهی است برای "
                 "دور نگه‌داشتن یک فرایند که گاه دقیقاً نیاز گزارش است — اما "
                 "از انرژی خواننده می‌کاهد."),
                ("Three pairs worth owning: commence/start, purchase/buy, "
                 "request/ask for. The formal member is not better; it is "
                 "longer-lived in print and colder in feeling. Choose by "
                 "audience, and then stay consistent for the whole text.",
                 "سه جفت ارزش دانستن: commence/start، purchase/buy، "
                 "request/ask for. عضو رسمی بهتر نیست؛ در چاپ ماندگارتر و در "
                 "احساس سردتر است. بر اساس مخاطب انتخاب کن و در تمام متن "
                 "یکدست بمان."),
            ],
            [
                ("We regret to inform you that the deadline has passed.",
                 "با تأسف اطلاع می‌دهیم که مهلت گذشته است."),
                ("Sorry, you missed the deadline.", "ببخشید، مهلت را از دست "
                 "دادی."),
                ("The committee will consider the request at its next "
                 "meeting.", "کمیته در نشست بعدی درخواست را بررسی می‌کند."),
                ("We'll talk about it next time.", "دفعهٔ بعد درباره‌اش حرف "
                 "می‌زنیم."),
            ],
            [
                mcq("Which is the least nominalised version?", "کدام کمترین "
                    "اسم‌سازی را دارد؟",
                    ["We conducted an evaluation of the proposal.",
                     "We evaluated the proposal.",
                     "An evaluation of the proposal was conducted.",
                     "The proposal underwent evaluation."], 1,
                    "A finite verb carries the action directly.",
                    "فعل صرف‌شده کنش را مستقیم حمل می‌کند."),
                mcq("'We regret to inform you' is appropriate for ___.",
                    "«We regret to inform you» برای ___ مناسب است.",
                    ["a friend's birthday", "a formal refusal",
                     "a shopping list", "a chat message"], 1,
                    "The frame belongs to formal correspondence.",
                    "این ساخت به مکاتبهٔ رسمی تعلق دارد."),
            ],
            [
                mcq("Nominalisation is useful when you want to ___.",
                    "اسم‌سازی وقتی سودمند است که بخواهی ___.",
                    ["sound friendly", "keep a process at a distance",
                     "shorten the text", "add examples"], 1,
                    "It creates distance, at a cost in energy.",
                    "فاصله می‌سازد، به قیمت از دست رفتن انرژی."),
                gap("Formal correspondence usually prefers ___ to 'ask for'.",
                    ["request"], "One of the standard formal/informal pairs.",
                    "یکی از جفت‌های استاندارد رسمی/غیررسمی.", "one word"),
                mcq("Which text mixes registers badly?", "کدام متن ثبت‌ها را "
                    "بد درهم می‌کند؟",
                    ["Hi Sam, quick question about the invoice.",
                     "Dear Sir, gonna need that report by Friday.",
                     "We write to confirm the meeting on Monday.",
                     "Thanks — I'll send the file tonight."], 1,
                    "Contraction and slang sit badly inside a formal frame.",
                    "کوتاه‌سازی و زبان عامیانه در چارچوبی رسمی بد می‌نشیند."),
                gap("'Commence' is the formal partner of ___.", ["start"],
                    "Same meaning, different room.", "یک معنا، دو اتاق.",
                    "one word"),
            ],
        ),
        lesson(
            "c2-u5-l3", "reading",
            ("Two accounts of one afternoon",
             "دو روایت از یک بعدازظهر"),
            ("Read two versions of the same event and locate the disagreement "
             "in what was selected, not in what was invented.",
             "دو روایت از یک رویداد را بخوان و اختلاف را در گزینش ببین، نه در "
             "ساختگی بودن."),
            [
                ("Two honest accounts of one event differ because selection "
                 "is unavoidable. Account A includes the crowd and the "
                 "timing; account B includes the message and the silence. "
                 "Neither lies, and neither is complete.",
                 "دو روایت صادق از یک رویداد فرق دارند چون گزینش ناگزیر است. "
                 "روایت الف جمعیت و زمان را می‌آورد؛ روایت ب پیام و سکوت را. "
                 "هیچ‌کدام دروغ نمی‌گوید و هیچ‌کدام کامل نیست."),
                ("When a question asks what one account omits, the answer is "
                 "usually something the other account treats as central. "
                 "Compare the two for emphasis rather than for facts, and "
                 "notice which details are placed in subordinate clauses — "
                 "where a writer puts what they must mention but do not want "
                 "to stress.",
                 "وقتی پرسشی می‌پرسد یک روایت چه را حذف کرده، پاسخ معمولاً "
                 "چیزی است که روایت دیگر مرکزی می‌داند. دو متن را برای تأکید "
                 "مقایسه کن نه برای واقعیت، و ببین کدام جزئیات در بند فرعی "
                 "نشسته‌اند — جایی که نویسنده چیزی را که باید بگوید ولی "
                 "نمی‌خواهد برجسته کند می‌گذارد."),
            ],
            [
                ("Ask which detail each account would have to lose to become "
                 "the other.", "بپرس هر روایت باید کدام جزئیات را از دست بدهد "
                 "تا روایت دیگر شود."),
                ("A detail in both accounts is the safest ground for a "
                 "conclusion.", "جزئیاتی که در هر دو روایت هست امن‌ترین زمین "
                 "برای نتیجه‌گیری است."),
                ("Silence is evidence only when someone had a reason to "
                 "speak.", "سکوت تنها وقتی شاهد است که کسی دلیلی برای گفتن "
                 "داشته باشد."),
            ],
            [
                mcq("What does Account A emphasise?", "روایت الف بر چه تأکید "
                    "می‌کند؟",
                    ["the message on the wall", "the size and timing of the "
                     "gathering", "the police decision", "the rain"],
                    1, "It counts people and notes the hour.",
                    "افراد را می‌شمارد و ساعت را یاد می‌کند."),
                mcq("Account B's central fact is ___.", "واقعیت مرکزی روایت ب "
                    "___ است.",
                    ["the crowd", "a written demand ignored for a year",
                     "the weather", "the number of police"], 1,
                    "The letter and its reception organise the account.",
                    "نامه و نحوهٔ دریافتش روایت را سازمان می‌دهند."),
            ],
            [
                mcq("The two accounts disagree about ___.", "دو روایت بر سر "
                    "___ اختلاف دارند.",
                    ["whether anything happened", "what the event was about",
                     "the date", "the location"], 1,
                    "Each frames the same afternoon differently.",
                    "هر یک همان بعدازظهر را در چارچوبی دیگر می‌بیند."),
                mcq("Which conclusion is supported by both accounts?",
                    "کدام نتیجه از هر دو روایت پشتیبانی می‌شود؟",
                    ["the gathering was small", "a group assembled outside "
                     "the building", "the letter was never sent",
                     "the police made arrests"], 1,
                    "Only the assembly is common ground.",
                    "تنها گردهمایی زمین مشترک است."),
                mcq("Account A's treatment of the letter shows ___.", "نحوهٔ "
                    "پرداخت روایت الف به نامه نشان می‌دهد ___.",
                    ["it was central", "it was mentioned but subordinated",
                     "it did not exist", "it was read aloud"], 1,
                    "It appears inside another clause, not as a topic.",
                    "داخل بندی دیگر می‌آید، نه به‌عنوان موضوع."),
            ],
            passage=passage(
                ("Two accounts of one afternoon",
                 "دو روایت از یک بعدازظهر"),
                ("**Account A.** By three o'clock the pavement outside the "
                 "office held perhaps sixty people, which was more than the "
                 "organisers had expected and fewer than the police had "
                 "prepared for. The banners were hand-painted. A man with a "
                 "megaphone read out four names and the crowd repeated them. "
                 "At ten past three the rain began, and the gathering, having "
                 "achieved nothing it could point to, dispersed in an orderly "
                 "way by half past. A letter that the group had delivered a "
                 "year earlier went unmentioned by everyone, including me.\n\n"
                 "**Account B.** The letter was sent in March and acknowledged "
                 "in April. It asked for one meeting and named three "
                 "questions. The acknowledgement said the questions would be "
                 "considered. Twelve months later, on a wet afternoon, sixty "
                 "people stood outside the building to say the twelve months "
                 "had happened. That was the whole of the event: not the "
                 "banners, not the megaphone, but the distance between April "
                 "and the following March. The rain, which Account A records "
                 "as an inconvenience, is the reason most of them left — and "
                 "the reason the questions are still unanswered.",
                 "روایت الف. ساعت سه بعدازظهر حدود شصت نفر روی پیاده‌رو "
                 "بیرون دفتر بودند؛ بیشتر از آنچه برگزارکنندگان انتظار داشتند "
                 "و کمتر از آنچه پلیس آماده کرده بود. پلاکارد‌ها دست‌نویس "
                 "بودند. مردی با بلندگو چهار نام خواند و جمعیت تکرار کرد. ساعت "
                 "سه و ده دقیقه باران آمد و تجمع، بی‌آنکه چیزی برای نشان دادن "
                 "به دست آورده باشد، تا سه و نیم منظم پراکنده شد. نامه‌ای که "
                 "گروه یک سال پیش داده بود از زبان همه، از جمله من، نیفتاد.\n\n"
                 "روایت ب. نامه در مارس فرستاده شد و در آوریل دریافتش تأیید "
                 "شد. یک نشست می‌خواست و سه پرسش را نام می‌برد. تأییدیه گفت "
                 "پرسش‌ها بررسی خواهند شد. دوازده ماه بعد، در بعدازظهری "
                 "بارانی، شصت نفر بیرون ساختمان ایستادند تا بگویند آن دوازده "
                 "ماه گذشته است. تمام رویداد همین بود: نه پلاکاردها، نه "
                 "بلندگو، بلکه فاصلهٔ میان آوریل و مارس بعد. باران، که روایت "
                 "الف آن را زحمت ثبت می‌کند، دلیل رفتن بیشتر آنها است — و "
                 "دلیل آنکه پرسش‌ها هنوز بی‌پاسخ‌اند."),
            ),
        ),
        lesson(
            "c2-u5-l4", "speaking",
            ("Negotiating without giving away the substance",
             "مذاکره بی‌آنکه جانِ مطلب را واگذار کنی"),
            ("Trade on terms, not on principles: concede sequence, timing or "
             "wording, and hold the requirement.",
             "بر سر شرایط معامله کن، نه بر سر اصول: ترتیب، زمان یا واژه‌بندی "
             "را واگذار و الزام را نگه دار."),
            [
                ("A negotiation fails in two directions: the speaker gives "
                 "away the requirement to keep the mood, or holds everything "
                 "and loses the room. The skill is to separate what you need "
                 "from how it is delivered. 'We can move the date, and the "
                 "figures still have to be published' concedes a term and "
                 "holds a principle in one sentence.",
                 "مذاکره از دو سو شکست می‌خورد: گوینده الزام را برای حفظ فضا "
                 "واگذار می‌کند یا همه‌چیز را نگه می‌دارد و اتاق را از دست "
                 "می‌دهد. مهارت در جدا کردن «چه می‌خواهی» از «چگونه گفته "
                 "می‌شود» است. «We can move the date, and the figures still "
                 "have to be published» در یک جمله یک شرط را واگذار و یک اصل "
                 "را نگه می‌دارد."),
                ("Conditional trades are the workhorse: 'if we can agree the "
                 "wording, we can accept the deadline'. Notice the order — "
                 "the offer first, the condition second, so the other side "
                 "hears a gift before a demand. 'We cannot' is weaker than "
                 "'we are not able to at this stage', which leaves a door "
                 "without promising one.",
                 "معامله‌های شرطی اسب کار است: «if we can agree the wording, "
                 "we can accept the deadline». ترتیب را ببین — پیشنهاد اول و "
                 "شرط دوم تا طرف مقابل پیش از درخواست هدیه را بشنود. «We "
                 "cannot» از «we are not able to at this stage» ضعیف‌تر است؛ "
                 "دومی دری را باز می‌گذارد بی‌آنکه وعده‌ای بدهد."),
            ],
            [
                ("We can move the date; the figures still have to be "
                 "published.", "تاریخ را می‌توانیم جابه‌جا کنیم؛ ارقام هنوز "
                 "باید منتشر شوند."),
                ("If you can accept the wording, we can accept the deadline.",
                 "اگر واژه‌بندی را بپذیرید، مهلت را می‌پذیریم."),
                ("That is not something I can agree to at this stage.",
                 "این چیزی نیست که در این مرحله بتوانم بپذیرم."),
                ("Let me be clear about what is fixed and what is open.",
                 "بگذار روشن بگویم چه چیزی ثابت است و چه چیزی باز."),
            ],
            [
                mcq("The strongest negotiating sentence separates ___.",
                    "قوی‌ترین جملهٔ مذاکره ___ را جدا می‌کند.",
                    ["friend and enemy", "the requirement and the delivery",
                     "cost and time", "past and future"], 1,
                    "Terms are tradable; principles are not.",
                    "شرایط معامله‌پذیرند و اصول نه."),
                mcq("'We are not able to at this stage' is better than 'we "
                    "cannot' because ___.", "«We are not able to at this "
                    "stage» از «we cannot» بهتر است چون ___.",
                    ["it is shorter", "it leaves the position open",
                     "it is more emotional", "it promises agreement"], 1,
                    "A time limit keeps the door ajar without a commitment.",
                    "محدودیت زمانی در را نیمه‌باز نگه می‌دارد بی‌تعهد شدن."),
            ],
            [
                say("We can be flexible on the schedule, and the audit has to "
                    "be independent. Those are two different things.",
                    "در زمان‌بندی می‌توانیم انعطاف داشته باشیم و حسابرسی باید "
                    "مستقل باشد. این‌ها دو چیز متفاوت‌اند."),
                say("If you can move the review to March, we can accept the "
                    "wording as it stands.", "اگر بازبینی را به مارس ببرید، "
                    "واژه‌بندی را همان‌طور می‌پذیریم."),
                say("I am not in a position to agree to that today, and I can "
                    "come back to you on Thursday.", "امروز نمی‌توانم آن را "
                    "بپذیرم و پنجشنبه به شما پاسخ می‌دهم."),
                say("Let me say what is fixed: the number of sites. What is "
                    "open is when they are announced.", "بگذار بگویم چه ثابت "
                    "است: تعداد سایت‌ها. آنچه باز است زمان اعلام آن‌هاست."),
            ],
            dialogue=dialogue([
                ("Buyer", "We need the report by Friday, and we need the "
                 "figures in it.", "گزارش را تا جمعه می‌خواهیم و ارقامش را هم."),
                ("You", "The figures we can do by Friday. The commentary needs "
                 "another week, because two sites have not confirmed.",
                 "ارقام را تا جمعه می‌توانیم. توضیح‌ها یک هفته دیگر لازم "
                 "دارند، چون دو سایت تأیید نکرده‌اند."),
                ("Buyer", "Then send the figures alone.", "پس فقط ارقام را "
                 "بفرستید."),
                ("You", "We can do that if the covering note says they are "
                 "provisional.", "این را می‌کنیم به شرطی که یادداشت همراه "
                 "بگوید ارقام موقتی‌اند."),
            ]),
        ),
    ],
)

U6 = unit(
    "c2-u6",
    ("Holding the thread", "نگه‌داشتن رشتهٔ متن"),
    ("Make a long text cohere without repetition, and describe numbers so "
     "that they mean something.",
     "متنی بلند را بی‌تکرار منسجم کن و اعداد را طوری توصیف کن که معنایی "
     "داشته باشند."),
    [
        lesson(
            "c2-u6-l1", "grammar",
            ("Reference, substitution and ellipsis",
             "ارجاع، جانشینی و حذف"),
            ("Carry meaning across sentences without repeating the words that "
             "carried it the first time.",
             "معنا را در جمله‌ها پیش ببر بی‌آنکه واژه‌هایی را که بار اول حملش "
             "کردند تکرار کنی."),
            [
                ("Cohesion is done by three devices. Reference points back: "
                 "this, that, the former, the latter, such a claim. "
                 "Substitution replaces a whole phrase: 'so do I', 'I think "
                 "not', 'if you can, we will'. Ellipsis leaves the phrase out "
                 "entirely and trusts the reader: 'Some sites agreed and "
                 "others did not.'",
                 "انسجام با سه ابزار ساخته می‌شود. ارجاع به عقب اشاره "
                 "می‌کند: this، that، the former، the latter، such a claim. "
                 "جانشینی تمام عبارت را جای‌گزین می‌کند: «so do I»، «I think "
                 "not»، «if you can, we will». حذف عبارت را کامل بیرون "
                 "می‌گذارد و به خواننده اعتماد می‌کند: «Some sites agreed and "
                 "others did not.»"),
                ("'This' and 'that' are not interchangeable. 'This' points to "
                 "what was just said; 'that' distances it, often to disagree: "
                 "'That is a different question.' Bare 'this' across a "
                 "paragraph boundary is the commonest fault in advanced "
                 "writing, because the reader cannot tell which of three "
                 "ideas it points at. Add the noun: this assumption, this "
                 "finding.",
                 "«this» و «that» جای هم نمی‌نشینند. «this» به چیزی که همین "
                 "الان گفته شد اشاره می‌کند و «that» فاصله می‌اندازد، اغلب "
                 "برای مخالفت: «That is a different question.» «this» بی‌اسم "
                 "در مرز بند شایع‌ترین خطای نوشتار پیشرفته است، چون خواننده "
                 "نمی‌فهمد از میان سه ایده به کدام اشاره می‌شود. اسم را "
                 "بیفزا: this assumption، this finding."),
                ("Ellipsis has a register: it is natural in speech and in "
                 "confident prose, and it fails in legal or instructional "
                 "text where nothing may be left to inference. Know which "
                 "text you are writing before you leave a verb out.",
                 "حذف ثبت دارد: در گفتار و نثر مطمئن طبیعی است و در متن حقوقی "
                 "یا آموزشی که هیچ چیز نباید به استنتاج سپرده شود شکست "
                 "می‌خورد. پیش از حذف فعل بدان چه متنی می‌نویسی."),
            ],
            [
                ("Few sites reported a fall; most did not.",
                 "سایت‌های کمی کاهش گزارش کردند؛ بیشترشان نکردند."),
                ("The former argues for delay, the latter for publication.",
                 "اولی طرفدار تعویق است و دومی طرفدار انتشار."),
                ("Such a claim needs more than one survey behind it.",
                 "چنین ادعایی بیش از یک نظرسنجی پشتش لازم دارد."),
                ("I expected the figures to be revised. I think not.",
                 "انتظار داشتم ارقام بازنگری شوند. فکر نمی‌کنم."),
            ],
            [
                mcq("Bare 'this' at a paragraph boundary is weak because "
                    "___.", "«this» بی‌اسم در مرز بند ضعیف است چون ___.",
                    ["it is informal", "the reader cannot tell what it "
                     "points to", "it is too short", "it repeats a noun"],
                    1, "Reference needs a recoverable antecedent.",
                    "ارجاع به مرجعِ بازیابی‌پذیر نیاز دارد."),
                mcq("'The former' refers to ___.", "«the former» به ___ "
                    "اشاره می‌کند.",
                    ["the second of two", "the first of two",
                     "the most recent noun", "the main subject"], 1,
                    "Former is first, latter is second.",
                    "former اولی است و latter دومی."),
            ],
            [
                mcq("Which sentence uses ellipsis?", "کدام جمله حذف دارد؟",
                    ["Some agreed and others did not agree.",
                     "Some agreed and others did not.",
                     "Some of the sites agreed.",
                     "Others did not agree with the sites."], 1,
                    "The verb is left out and understood.",
                    "فعل حذف شده و فهمیده می‌شود."),
                gap("The first survey was small; the ___ covered four "
                     "regions.", ["latter"], "Latter names the second of "
                    "two.", "latter دومی از دو را نام می‌برد.", "one word"),
                mcq("In legal text, ellipsis is ___.", "در متن حقوقی حذف "
                    "___.",
                    ["preferred", "risky", "compulsory", "neutral"], 1,
                    "Nothing may be left to inference.",
                    "هیچ چیز را نمی‌توان به استنتاج سپرد."),
                gap("Add a noun after 'this': this ___, this finding.",
                    ["assumption", "claim", "result"],
                    "Any noun that names the antecedent works.",
                    "هر اسمی که مرجع را نام ببرد کار می‌کند.", "one word"),
            ],
        ),
        lesson(
            "c2-u6-l2", "vocabulary",
            ("Collocation: the words that insist on each other",
             "هم‌نشینی: واژه‌هایی که همدیگر را می‌طلبند"),
            ("Use high-frequency academic chunks correctly instead of "
             "inventing near-synonyms.",
             "خوشه‌های پرکاربرد دانشگاهی را درست به کار ببر، نه با ساختن "
             "شبه‌مترادف."),
            [
                ("Collocation is habit, not logic. We make a decision and do "
                 "research; we strongly agree and highly effective; a sharp "
                 "rise and a marked increase but not a marked fall in every "
                 "register. None of these is explained by meaning alone, which "
                 "is why they must be learned in chunks.",
                 "هم‌نشینی عادت است نه منطق. make a decision و do research؛ "
                 "strongly agree و highly effective؛ a sharp rise و a marked "
                 "increase، ولی نه در هر ثبتی a marked fall. هیچ‌کدام تنها "
                 "با معنا توضیح داده نمی‌شوند و به همین دلیل باید در خوشه "
                 "یاد گرفته شوند."),
                ("The high-value academic chunks are few and reusable: to a "
                 "large extent, in the light of, with respect to, on the "
                 "grounds that, in so far as, a growing body of evidence. One "
                 "per paragraph is plenty; two in a sentence is padding.",
                 "خوشه‌های دانشگاهی پرکاربرد کم و بازمصرف‌شدنی‌اند: to a large "
                 "extent، in the light of، with respect to، on the grounds "
                 "that، in so far as، a growing body of evidence. یکی در هر "
                 "بند کافی است و دو تا در یک جمله پرکردن فضا."),
                ("Watch the prepositions inside chunks: an increase in "
                 "waiting times, a decrease of ten per cent, a rise from nine "
                 "to fourteen. The preposition carries the direction, and it "
                 "is the part learners most often get wrong.",
                 "حروف اضافهٔ درون خوشه را ببین: an increase in waiting "
                 "times، a decrease of ten per cent، a rise from nine to "
                 "fourteen. حرف اضافه جهت را حمل می‌کند و همان بخشی است که "
                 "زبان‌آموزان بیشتر اشتباه می‌کنند."),
            ],
            [
                ("The committee made a decision it could not explain.",
                 "کمیته تصمیمی گرفت که نمی‌توانست توضیحش دهد."),
                ("There has been a marked increase in complaints.",
                 "افزایش چشمگیری در شکایت‌ها رخ داده است."),
                ("To a large extent, the delay was administrative.",
                 "تا حد زیادی، تأخیر اداری بود."),
                ("The ruling was made on the grounds that the process was "
                 "unfair.", "حکم بر این پایه صادر شد که فرایند ناعادلانه بود."),
            ],
            [
                mcq("Which is the standard collocation?", "کدام هم‌نشینی "
                    "استاندارد است؟",
                    ["do a decision", "make a decision", "take a decision "
                     "off", "perform a decision"], 1,
                    "'Make a decision' is fixed.",
                    "«make a decision» ثابت است."),
                mcq("An increase ___ waiting times is correct.",
                    "«an increase ___ waiting times» درست است.",
                    ["of", "in", "on", "at"], 1,
                    "Increase in + the thing measured.",
                    "increase in + چیزی که سنجیده می‌شود."),
            ],
            [
                mcq("'Highly' collocates with ___.", "«highly» با ___ هم‌نشین "
                    "می‌شود.",
                    ["agree", "effective", "increase", "decide"], 1,
                    "We strongly agree but a highly effective method.",
                    "می‌گوییم strongly agree ولی a highly effective method."),
                gap("A decrease ___ ten per cent is a fall of that size.",
                    ["of"], "Decrease of + amount.",
                    "decrease of + مقدار.", "one word"),
                mcq("Two academic chunks in one sentence usually read as "
                    "___.", "دو خوشهٔ دانشگاهی در یک جمله معمولاً ___",
                    ["precision", "padding", "formality", "humour"], 1,
                    "One does the work; the second fills space.",
                    "یکی کار را می‌کند و دومی فضا را پر می‌کند."),
                gap("The ban was imposed on the ___ that the risk was "
                     "unacceptable.", ["grounds"], "On the grounds that.",
                    "ساخت «on the grounds that» یعنی بر این پایه که.",
                    "one word"),
            ],
        ),
        lesson(
            "c2-u6-l3", "listening",
            ("The podcast that argues with its own chart",
             "پادکستی که با نمودار خودش بحث می‌کند"),
            ("Follow a discussion where the figures and the interpretation "
             "pull in different directions.",
             "گفت‌وگویی را دنبال کن که ارقام و تفسیر در آن دو جهت مخالف "
             "می‌کشند."),
            [
                ("Numbers arrive with a story attached, and the story is often "
                 "in the words around them: 'only', 'already', 'as many as'. "
                 "Listening critically means hearing those words as claims and "
                 "asking what the number would look like without them.",
                 "اعداد با روایتی می‌آیند و روایت اغلب در واژه‌های اطرافشان "
                 "است: «only»، «already»، «as many as». شنیدن نقادانه یعنی "
                 "شنیدن این واژه‌ها به‌عنوان ادعا و پرسیدن اینکه عدد بدون "
                 "آن‌ها چه شکلی می‌شد."),
                ("A base rate changes everything. 'Twice as many complaints' "
                 "is alarming until you hear that the base was four. Listen "
                 "for the denominator, and notice when a speaker supplies it "
                 "and when they do not.",
                 "نرخ پایه همه‌چیز را عوض می‌کند. «Twice as many complaints» "
                 "تا وقتی نشنوی پایه چهار بوده نگران‌کننده است. به مخرج گوش "
                 "کن و ببین گوینده چه وقت آن را می‌دهد و چه وقت نه."),
            ],
            [
                ("The trend is up; the level is still below where it was in "
                 "2019.", "روند صعودی است؛ سطح هنوز پایین‌تر از ۲۰۱۹ است."),
                ("Complaints doubled, from four to eight.",
                 "شکایت‌ها دو برابر شد، از چهار به هشت."),
                ("On average the wait fell, which tells you nothing about the "
                 "longest one.", "میانگین انتظار کم شد و این هیچ از طولانی‌ترین "
                 "انتظار نمی‌گوید."),
            ],
            [
                mcq("The presenter's 'only' before a figure signals ___.",
                    "«only» پیش از یک عدد نشانهٔ ___ است.",
                    ["a measured claim", "an evaluation of the figure",
                     "a correction", "a new topic"], 1,
                    "'Only' judges the number rather than reporting it.",
                    "«only» عدد را داوری می‌کند، نه گزارش."),
                mcq("A claim of doubling is weak without ___.",
                    "ادعای دو برابر شدن بدون ___ ضعیف است.",
                    ["a year", "the base figure", "an average", "a chart"],
                    1, "Doubling from four is not doubling from four "
                    "thousand.", "دو برابر شدن از چهار با دو برابر شدن از چهار "
                    "هزار یکی نیست."),
            ],
            [
                listen("Complaints doubled last year. I want to be honest "
                       "about that: they went from four to eight. Four to "
                       "eight is a doubling, and it is also eight "
                       "complaints.",
                       "What is the speaker doing with the figure?",
                       "گوینده با عدد چه می‌کند؟",
                       ["hiding it", "giving its base", "rejecting it",
                        "comparing years"], 1,
                       "The base turns a headline into a quantity.",
                       "پایه، تیتر را به یک کمیت تبدیل می‌کند."),
                listen("The average wait is nine minutes. The median is "
                       "seven. The longest was fifty-one. All three are "
                       "true, and only one of them is what people "
                       "remember.", "What does the speaker point out?",
                       "گوینده به چه چیزی اشاره می‌کند؟",
                       ["the figures are wrong", "different summaries tell "
                        "different stories", "nobody waits", "averages "
                        "are useless"], 1,
                       "Each summary is accurate and persuasive in a "
                       "different direction.", "هر خلاصه دقیق است و در جهتی "
                       "متفاوت اقناع می‌کند."),
                listen("I would not say the policy failed. I would say it "
                       "worked in the two places it was tried, and we have "
                       "not tried it anywhere else.",
                       "How does the speaker characterise the result?",
                       "گوینده نتیجه را چگونه توصیف می‌کند؟",
                       ["as a failure", "as a local success with unknown "
                        "reach", "as unmeasured", "as a national "
                        "success"], 1,
                       "Both the success and its boundary are stated.",
                       "هم موفقیت و هم مرزش گفته می‌شود."),
                mcq("Which word most clearly carries evaluation rather than "
                    "measurement?", "کدام واژه داوری را حمل می‌کند و نه "
                    "سنجش را؟",
                    ["nine", "median", "merely", "per cent"], 2,
                    "'Merely' tells you what to think about the size.",
                    "«merely» می‌گوید دربارهٔ اندازه چه فکر کن."),
            ],
        ),
        lesson(
            "c2-u6-l4", "writing",
            ("Writing about numbers so that they mean something",
             "نوشتن دربارهٔ اعداد تا معنا پیدا کنند"),
            ("Report a trend with its base, its period and its limit, in prose "
             "a reader can act on.",
             "روندی را با پایه، دوره و محدودیتش چنان گزارش کن که خواننده "
             "بتواند بر اساسش تصمیم بگیرد."),
            [
                ("A number in prose needs four things: what is counted, over "
                 "what period, against what base, and with what caveat. Miss "
                 "the base and you have written an advertisement; miss the "
                 "caveat and you have written a promise.",
                 "عدد در نثر چهار چیز لازم دارد: چه چیزی شمرده شده، در چه "
                 "دوره‌ای، در برابر چه پایه‌ای و با چه هشداری. پایه را که جا "
                 "بگذاری تبلیغ نوشته‌ای و هشدار را که جا بگذاری وعده."),
                ("Choose the summary that fits the claim: average for totals, "
                 "median for typical experience, range for risk. Then say "
                 "which you chose, in a subordinate clause, so the reader is "
                 "not misled by the shape of the sentence.",
                 "خلاصه‌ای را انتخاب کن که با ادعا می‌خواند: میانگین برای مجموع، "
                 "میانه برای تجربهٔ معمول و دامنه برای ریسک. بعد در بندی فرعی "
                 "بگو کدام را انتخاب کردی تا خواننده با شکل جمله گمراه نشود."),
            ],
            [
                ("Waiting times fell by a third, from a median of nine "
                 "minutes to six, over the eight weeks of the pilot.",
                 "زمان انتظار یک‌سوم کم شد، از میانهٔ نُه دقیقه به شش، در هشت "
                 "هفتهٔ آزمایش."),
                ("Complaints doubled, although from a base of four.",
                 "شکایت‌ها دو برابر شد، هرچند از پایه‌ای چهارتایی."),
                ("The average masks a range of four to fifty-one minutes.",
                 "میانگین دامنهٔ چهار تا پنجاه‌ویک دقیقه را پنهان می‌کند."),
            ],
            [
                mcq("A trend sentence without a base is ___.", "جملهٔ روند "
                    "بدون پایه ___ است.",
                    ["precise", "misleading", "informal", "redundant"], 1,
                    "Doubling from four says almost nothing about scale.",
                    "دو برابر شدن از چهار تقریباً هیچ از مقیاس نمی‌گوید."),
                mcq("For the typical experience, report the ___.",
                    "برای تجربهٔ معمول، ___ را گزارش کن.",
                    ["average", "median", "total", "maximum"], 1,
                    "The median is less distorted by extremes.",
                    "میانه از مقادیر حدی کمتر آسیب می‌بیند."),
            ],
            [
                write("Write about 150 words reporting a pilot that cut "
                      "median waiting times from nine minutes to six across "
                      "eight weeks, while the longest wait rose to fifty-one "
                      "minutes and complaints doubled from four. Give the "
                      "trend, the base, the period, the counter-evidence and "
                      "a recommendation.",
                      "حدود ۱۵۰ واژه گزارش بنویس دربارهٔ آزمایشی که میانهٔ زمان "
                      "انتظار را در هشت هفته از نُه به شش دقیقه رساند، در حالی "
                      "که طولانی‌ترین انتظار به پنجاه‌ویک دقیقه رسید و شکایت‌ها "
                      "از چهار دو برابر شد. روند، پایه، دوره، شاهد مخالف و یک "
                      "توصیه را بیاور.",
                      150, ["although", "whereas"],
                      "One sentence per element; no adjective without a "
                      "number behind it; the recommendation must follow from "
                      "the counter-evidence.", "برای هر عنصر یک جمله؛ هیچ "
                      "صفتی بی‌عدد پشتش؛ توصیه باید از شاهد مخالف بیرون بیاید."),
                mcq("Which sentence reports rather than advertises?",
                    "کدام جمله گزارش می‌کند و نه تبلیغ؟",
                    ["Waiting times plummeted.", "Waiting times fell by a "
                     "third, from nine to six minutes.",
                     "Waiting times are now excellent.",
                     "Patients love the new system."], 1,
                    "The change, the base and the unit are all present.",
                    "تغییر، پایه و واحد همه آمده‌اند."),
                gap("A figure needs a base, a period and a ___.",
                    ["caveat", "limit", "source"],
                    "A caveat keeps the claim inside its evidence.",
                    "هشدار ادعا را در محدودهٔ شاهدش نگه می‌دارد.",
                    "one word"),
            ],
        ),
    ],
)
