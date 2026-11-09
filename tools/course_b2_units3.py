#!/usr/bin/env python3
"""B2 · units 5-6: getting it done, and saying exactly which one.

Unit 5 is the causative — the structure of a service economy — and ends in the
report that a workplace actually asks for. Unit 6 reduces relative clauses and
ends in the essay that weighs two sides.
"""

from course_kit import gap, lesson, listen, mcq, passage, unit, write

U5 = unit(
    "b2-u5",
    ("I had it repaired", "دادم تعمیرش کنند"),
    ("Say that you arranged for something to be done, and write the report that records it.", "بگو کاری را برایت انجام دادند و گزارشی بنویس که همان را ثبت می‌کند."),
    [
        lesson(
            "b2-u5-l1",
            "grammar",
            ("Causatives: have / get something done", "سببی: have / get something done"),
            ("Describe a service, a mishap and a result without naming who did the work.", "خدمت، حادثه و نتیجه را بی‌نام بردن از عامل توصیف کن."),
            [
                ("Have + object + past participle means you arranged for the action: I had my hair cut, we had the roof repaired, she had her car serviced. The grammar says 'someone did this for me' and declines to say who.", "have + مفعول + اسم مفعول یعنی ترتیب دادی کاری انجام شود: I had my hair cut، we had the roof repaired، she had her car serviced. دستور می‌گوید «کسی این را برای من کرد» و از نام بردن او می‌گذرد."),
                ("Get + object + participle is the same meaning in a more conversational register: I got my phone fixed. Get also carries the idea of finishing something difficult, and get + object + participle can describe a mishap you did not arrange: he got his wallet stolen.", "get + مفعول + اسم مفعول همان معنا با لحن گفتاری‌تر است: I got my phone fixed. get همچنین ایدهٔ تمام کردن کار سخت را دارد و در حادثهٔ ناخواسته هم می‌آید: he got his wallet stolen."),
                ("Have someone do something is the active version: I had the plumber check the pipes. Get someone to do something is the same in speech: I got a friend to look at it. The active names the person; the passive causative does not.", "have somebody do something نسخهٔ معلوم است: I had the plumber check the pipes. get somebody to do something در گفتار همان است. معلوم شخص را نام می‌برد و سببی مجهول نام نمی‌برد."),
                ("A few verbs take the same shape with a different meaning: make someone do (force), let someone do (allow), help someone (to) do. Compare 'I had him check it' (I asked and he did) with 'I made him check it' (he had no choice).", "چند فعل همین شکل را با معنای دیگر دارند: make somebody do (اجبار)، let somebody do (اجازه)، help somebody (to) do. «I had him check it» (خواستم و کرد) را با «I made him check it» (انتخابی نداشت) مقایسه کن."),
            ],
            [
                ("We had the kitchen painted last spring.", "بهار گذشته آشپزخانه را رنگ کردیم (کسی برایمان رنگ کرد)."),
                ("I need to get my eyes tested before I renew my licence.", "پیش از تمدید گواهینامه باید چشمانم را معاینه کنم."),
                ("She had the whole team rewrite the section.", "او کل تیم را واداشت بخش را بازنویسی کند."),
                ("He got his bag stolen on the metro.", "در مترو کیفش دزدیده شد."),
                ("Could you get someone to look at the heating?", "می‌شود کسی را بفرستی به شوفاژ نگاه کند؟"),
            ],
            [
                mcq("I ___ my car serviced last week.", "هفتهٔ گذشته ماشینم را سرویس کردم (کسی برایم).", ["serviced", "had", "have", "did"], 1,
                    "Causative: have + object + participle.", "سببی: have + مفعول + اسم مفعول."),
                mcq("Which sentence means someone else did it for you?", "کدام جمله یعنی دیگری آن را برایت انجام داد؟", ["I repaired my bike.", "I had my bike repaired.", "I was repairing my bike.", "My bike repairs."], 1,
                    "Only the causative leaves the doer out.", "فقط سببی کننده را حذف می‌کند."),
            ],
            [
                gap("We're going to ___ the flat decorated before we move in.", ["have", "get"], "Have/get + object + participle.", "have/get + مفعول + اسم مفعول."),
                gap("She got a colleague ___ check the figures. (active, with to)", ["to"], "Get someone to do something.", "get somebody to do something یعنی از کسی بخواهی کاری کند."),
                mcq("'He got his wallet stolen' suggests ___.", "«He got his wallet stolen» نشان می‌دهد ___.", ["he arranged it", "it happened to him", "he stole it", "he found it"], 1,
                    "A mishap, not an arrangement.", "حادثه است، نه ترتیب دادن."),
                mcq("Which is the most formal?", "کدام رسمی‌ترین است؟", ["I got the car fixed.", "I had the car fixed.", "I had them fix the car.", "The car got fixed."], 1,
                    "Have + object + participle is the neutral-formal form.", "have + مفعول + اسم مفعول شکل رسمی و خنثی است."),
            ],
        ),
        lesson(
            "b2-u5-l2",
            "vocabulary",
            ("Technology, data and digital society", "فناوری، داده و جامعهٔ دیجیتال"),
            ("Discuss automation, privacy and the trade-offs a platform makes.", "دربارهٔ خودکارسازی، حریم خصوصی و بده‌بستان‌های یک پلتفرم بحث کن."),
            [
                ("Automation vocabulary: to automate a process, replace a task, augment a job, displace workers, redeploy staff, reskill. Note the difference between a task (automatable) and a job (a bundle of tasks) — most of the argument turns on it.", "واژگان خودکارسازی: automate a process، replace a task، augment a job، displace workers، redeploy staff، reskill. تفاوت task (قابل خودکارسازی) و job (بسته‌ای از کارها) را در نظر بگیر؛ بیشتر بحث بر سر همین است."),
                ("Platform vocabulary: an algorithm, a feed, an engagement metric, targeted advertising, a recommendation engine, a filter bubble, data collection, consent, a privacy policy. 'Personalised' is the marketing word for 'profiled'.", "واژگان پلتفرم: algorithm، feed، engagement metric، targeted advertising، recommendation engine، filter bubble، data collection، consent، privacy policy. «personalised» واژهٔ بازاریابی برای «profiled» است."),
                ("Trade-off language is what B2 needs: in exchange for, at the cost of, the benefit is offset by, there is a tension between, on the one hand. A paragraph that lists only benefits has not made an argument.", "زبان بده‌بستان همان چیزی است که B2 لازم دارد: in exchange for، at the cost of، the benefit is offset by، there is a tension between، on the one hand. پاراگرافی که فقط فایده فهرست کند استدلال نکرده است."),
                ("Word formation: private → privacy, secure → security, automate → automation, regulate → regulation, consume → consumer. The -tion nouns are usually the abstract process; the -er noun is usually the actor, and sometimes the product (a computer).", "ساخت واژه: private ← privacy، secure ← security، automate ← automation، regulate ← regulation، consume ← consumer. اسم‌های tion معمولاً فرایند انتزاعی‌اند و اسم‌های er کنشگر و گاهی محصول (computer)."),
            ],
            [
                ("The warehouse automated its sorting, which displaced twelve jobs and created three.", "انبار مرتب‌سازی را خودکار کرد؛ دوازده شغل حذف و سه شغل ایجاد شد."),
                ("The recommendation engine optimises for time spent, not for satisfaction.", "موتور پیشنهاد برای زمان صرف‌شده بهینه می‌شود، نه برای رضایت."),
                ("Users consent to the policy without reading it, which is the whole business model.", "کاربران بدون خواندن به سیاست رضایت می‌دهند و همین کل مدل کسب‌وکار است."),
                ("In exchange for free storage, we give up the right to be forgotten.", "در برابر فضای رایگان، حق فراموش شدن را از دست می‌دهیم."),
            ],
            [
                mcq("To 'reskill' staff is to ___.", "«reskill» کارکنان یعنی ___.", ["dismiss them", "teach them skills for new roles", "reduce their hours", "hire replacements"], 1,
                    "Reskilling trains people for different work.", "reskilling آموزش برای کار متفاوت است."),
                mcq("A 'filter bubble' is ___.", "«filter bubble» ___ است.", ["a security feature", "an environment where you only meet confirming views", "a type of advertisement", "a data breach"], 1,
                    "The metaphor is confinement by personalisation.", "استعاره، محصور شدن با شخصی‌سازی است."),
            ],
            [
                gap("The benefit is ___ by the loss of privacy.", ["offset"], "Offset by: balanced against.", "offset by یعنی در برابر آن سنجیده می‌شود."),
                gap("Regulators want companies to obtain explicit ___ before collecting data.", ["consent"], "Consent is permission given knowingly.", "consent اجازهٔ آگاهانه است."),
                mcq("'Augment a job' means ___.", "«Augment a job» یعنی ___.", ["replace it completely", "add tools that make the worker more capable", "reduce its pay", "split it in two"], 1,
                    "Augmentation keeps the worker and adds capability.", "augmentation کارگر را نگه می‌دارد و توانایی می‌افزاید."),
                mcq("Which phrase introduces a trade-off?", "کدام عبارت بده‌بستان را معرفی می‌کند؟", ["As a result", "At the cost of", "For example", "In addition"], 1,
                    "A cost is the other side of a benefit.", "هزینه طرف دیگر فایده است."),
            ],
        ),
        lesson(
            "b2-u5-l3",
            "writing",
            ("The report that a workplace asks for", "گزارشی که محیط کار می‌خواهد"),
            ("Write a short report with findings, a recommendation and a reason.", "گزارش کوتاهی با یافته‌ها، توصیه و دلیل بنویس."),
            [
                ("A report is not an essay with headings. It answers a question someone asked, in an order that lets them decide: purpose, what was looked at, what was found, what is recommended. The recommendation comes before the detail it rests on, because readers stop early.", "گزارش مقاله با تیتر نیست. به پرسشی که کسی پرسیده پاسخ می‌دهد، به ترتیبی که تصمیم بگیرد: هدف، آنچه بررسی شد، یافته‌ها، توصیه. توصیه پیش از جزئیات می‌آید، چون خواننده زود دست می‌کشد."),
                ("Register: no contractions, no rhetorical questions, no 'I think'. Use 'the survey indicates', 'three of the four teams reported', 'it is recommended that'. The passive is not decoration here — it keeps the focus on the finding rather than the author.", "لحن: بدون شکل کوتاه، بدون پرسش بلاغی، بدون «I think». از «the survey indicates»، «three of the four teams reported»، «it is recommended that» استفاده کن. مجهول اینجا تزئین نیست؛ تمرکز را روی یافته نگه می‌دارد."),
                ("Numbers need to be attributable and comparable: give the base ('of 42 respondents'), the change ('up from 61% to 74%') and the limit ('the sample was one office'). A report that hides its sample is an opinion with headings.", "عددها باید قابل انتساب و مقایسه باشند: پایه («of 42 respondents»)، تغییر («up from 61% to 74%») و محدودیت («the sample was one office»). گزارشی که نمونه‌اش را پنهان کند، نظری است با تیتر."),
            ],
            [
                ("Purpose: This report examines the effect of the new booking system on waiting times.", "هدف: این گزارش اثر سامانهٔ رزرو تازه را بر زمان انتظار بررسی می‌کند."),
                ("Finding: Waiting times fell by a third in the first month.", "یافته: زمان انتظار در ماه اول یک‌سوم کم شد."),
                ("Recommendation: It is recommended that the system be extended to the second branch.", "توصیه: پیشنهاد می‌شود سامانه به شعبهٔ دوم گسترش یابد."),
                ("Limit: The sample covered one branch over four weeks.", "محدودیت: نمونه یک شعبه در چهار هفته بود."),
            ],
            [
                mcq("Where does the recommendation belong in a short report?", "توصیه در گزارش کوتاه کجا می‌آید؟", ["only at the end", "early, before the detail", "in the title", "nowhere"], 1,
                    "Readers decide early; the detail supports the decision.", "خواننده زود تصمیم می‌گیرد و جزئیات پشتیبانی می‌کند."),
                mcq("Which sentence fits a report's register?", "کدام جمله با لحن گزارش می‌خواند؟", ["I think it's better.", "It is recommended that the trial continue.", "Don't you think we should try?", "Let's give it a go."], 1,
                    "Impersonal and declarative.", "بی‌شخص و خبری."),
            ],
            [
                write("Write a short report for a manager on a four-week trial of a new booking system. State the purpose, two findings with numbers and a sample, one limitation, and a recommendation.",
                       "گزارش کوتاهی برای مدیر دربارهٔ چهار هفته آزمایش یک سامانهٔ رزرو تازه بنویس. هدف، دو یافته با عدد و نمونه، یک محدودیت و یک توصیه را بیاور.",
                       110, ["recommended", "although"],
                       "Use headings, no contractions, and keep the recommendation before the detail. Give the base for every percentage.",
                       "از تیتر استفاده کن، شکل کوتاه ننویس و توصیه را پیش از جزئیات بگذار. برای هر درصد پایه‌اش را بده."),
                gap("Waiting times fell ___ a third in the first month.", ["by"], "Fall by an amount.", "fall by مقدار کاهش."),
                mcq("Which detail makes a finding credible?", "کدام جزئیات یافته را باورپذیر می‌کند؟", ["many people agreed", "of 42 respondents, 31 preferred it", "it was obviously better", "everyone was happy"], 1,
                    "A base and a count, not an impression.", "پایه و شمارش، نه حس."),
            ],
        ),
    ],
)

U6 = unit(
    "b2-u6",
    ("The team that stayed", "تیمی که ماند"),
    ("Identify and describe with full and reduced relative clauses, then argue both sides in writing.", "با بند موصولی کامل و کوتاه‌شده شناسایی و توصیف کن و بعد هر دو طرف را مکتوب استدلال کن."),
    [
        lesson(
            "b2-u6-l1",
            "grammar",
            ("Relative clauses and reduced relatives", "بندهای موصولی و موصولی کوتاه‌شده"),
            ("Cut a relative clause down to a phrase without losing the meaning.", "بند موصولی را بدون از دست دادن معنا به عبارت کوتاه کن."),
            [
                ("Defining clauses identify and take no commas; non-defining clauses add and take commas. The comma is not cosmetic: 'the employees who were made redundant' is a subset, 'the employees, who were made redundant' is all of them.", "بند تعیین‌کننده شناسایی می‌کند و ویرگول ندارد؛ بند توصیفی اضافه می‌کند و ویرگول دارد. ویرگول تزئینی نیست: «the employees who were made redundant» زیرمجموعه است و «the employees, who were made redundant» همهٔ آن‌ها."),
                ("Prepositions can move to the end in speech and stay at the front in formal writing: the person I spoke to / the person to whom I spoke. 'Whom' after a preposition is the only place it is still required.", "حرف اضافه در گفتار آخر می‌آید و در نوشتار رسمی اول می‌ماند: the person I spoke to / the person to whom I spoke. «whom» بعد از حرف اضافه تنها جایی است که هنوز لازم است."),
                ("Reduced relatives drop the pronoun and the be: the man who was standing by the door → the man standing by the door; the report which was written in 2019 → the report written in 2019. Only possible when the relative clause has be + participle or be + -ing.", "موصولی کوتاه‌شده ضمیر و be را حذف می‌کند: the man who was standing by the door ← the man standing by the door؛ the report which was written in 2019 ← the report written in 2019. فقط وقتی ممکن است که بند be + اسم مفعول یا be + ing داشته باشد."),
                ("Which, referring to a whole clause, and whose, for possession, are the two that no reduction covers: she passed the exam, which surprised nobody. The house whose roof leaked. 'What' means 'the thing that' and never takes a noun before it.", "«which» برای کل بند و «whose» برای مالکیت دو موردی هستند که کوتاه‌شدن شاملشان نمی‌شود: she passed the exam, which surprised nobody. The house whose roof leaked. «what» یعنی «the thing that» و هرگز اسم پیش از خود نمی‌گیرد."),
            ],
            [
                ("Anyone wanting to join should sign the list.", "هر کس بخواهد بپیوندد باید فهرست را امضا کند."),
                ("The documents sent last week have not arrived.", "مدارک فرستاده‌شده در هفتهٔ گذشته نرسیده‌اند."),
                ("The team, which had lost three members, still delivered on time.", "تیم، که سه عضو از دست داده بود، باز هم به‌موقع تحویل داد."),
                ("That's the colleague whose advice saved the project.", "این همان همکاری است که مشورتش پروژه را نجات داد."),
                ("What surprised me was the silence of the room.", "آنچه مرا شگفت‌زده کرد سکوت اتاق بود."),
            ],
            [
                mcq("The woman ___ at the desk is the manager.", "زنی که پشت میز ___ مدیر است.", ["stands", "standing", "who standing", "stood"], 1,
                    "A reduced relative: who is standing → standing.", "موصولی کوتاه‌شده: who is standing ← standing."),
                mcq("Which sentence needs commas?", "کدام جمله ویرگول لازم دارد؟", ["The students who failed must retake the test.", "My sister who lives in Berlin is visiting.", "The book that I bought was expensive.", "The team that won celebrated."], 1,
                    "The sister clause adds information, not identity.", "بند خواهر اطلاعات اضافه می‌کند، نه شناسایی."),
            ],
            [
                gap("The car ___ (steal) last night was found in Karaj.", ["stolen"], "Reduced passive relative: which was stolen → stolen.", "موصولی مجهول کوتاه‌شده: which was stolen ← stolen."),
                gap("This is the article ___ which I referred. (formal)", ["to"], "Preposition fronted in formal style.", "حرف اضافه در سبک رسمی جلو می‌آید."),
                mcq("Which cannot be reduced?", "کدام را نمی‌توان کوتاه کرد؟", ["the man who was waiting", "the letter which was sent", "the man who called me", "the road which was repaired"], 2,
                    "No be + participle or -ing, so nothing can be dropped.", "be + اسم مفعول یا ing ندارد، پس چیزی حذف‌شدنی نیست."),
                mcq("'What I need is time' means ___.", "«What I need is time» یعنی ___.", ["I need something called time", "the thing I need is time", "time needs me", "I need what time is"], 1,
                    "What = the thing that.", "what یعنی the thing that."),
            ],
        ),
        lesson(
            "b2-u6-l2",
            "vocabulary",
            ("Society, culture and the words of comparison", "جامعه، فرهنگ و واژه‌های مقایسه"),
            ("Compare societies and describe cultural difference without stereotyping.", "جامعه‌ها را مقایسه کن و تفاوت فرهنگی را بدون کلیشه توصیف کن."),
            [
                ("Society vocabulary: a norm, a value, a custom, a generation, a minority, a majority, social mobility, inequality, cohesion, a stereotype, a prejudice. A norm is what people expect; a value is what they believe is good — the two are often confused in essays.", "واژگان جامعه: norm، value، custom، generation، minority، majority، social mobility، inequality، cohesion، stereotype، prejudice. norm چیزی است که مردم انتظار دارند و value چیزی که خوب می‌دانند؛ این دو در مقاله‌ها اغلب اشتباه می‌شوند."),
                ("Comparison needs hedges or it becomes prejudice: tends to, on average, in general, compared with, whereas, in contrast. 'They are more relaxed' is a stereotype; 'working hours tend to be shorter, on average' is a comparison.", "مقایسه بدون احتیاط به تعصب تبدیل می‌شود: tends to، on average، in general، compared with، whereas، in contrast. «They are more relaxed» کلیشه است و «working hours tend to be shorter, on average» مقایسه."),
                ("Culture words with collocations: cultural differences, a shared identity, a sense of belonging, integration, assimilation, diversity, tolerance, a language barrier. 'Assimilation' means becoming like the majority; 'integration' means joining without disappearing.", "واژه‌های فرهنگ با هم‌نشینی: cultural differences، shared identity، sense of belonging، integration، assimilation، diversity، tolerance، language barrier. assimilation یعنی شبیه اکثریت شدن و integration یعنی پیوستن بی‌آنکه محو شدن."),
                ("Word formation in this field: equal → equality, diverse → diversity, integrate → integration, tolerate → tolerance, prejudge → prejudice. Note that the verb 'prejudge' exists but the noun is far more common.", "ساخت واژه در این حوزه: equal ← equality، diverse ← diversity، integrate ← integration، tolerate ← tolerance، prejudge ← prejudice. فعل prejudge هست اما اسم بسیار رایج‌تر است."),
            ],
            [
                ("Working hours tend to be shorter in the north, on average.", "به‌طور متوسط، ساعت کار در شمال کوتاه‌تر است."),
                ("Integration is slower when there is no shared language.", "وقتی زبان مشترکی نباشد، ادغام کندتر است."),
                ("The survey measured social mobility, not income alone.", "نظرسنجی تحرک اجتماعی را سنجید، نه فقط درآمد را."),
                ("A norm can change in a generation; a value changes more slowly.", "یک هنجار در یک نسل می‌تواند عوض شود؛ ارزش کندتر عوض می‌شود."),
            ],
            [
                mcq("Which is a hedge, not a claim?", "کدام احتیاط است، نه ادعا؟", ["They are lazy.", "They tend to start later.", "Everyone agrees.", "It is obvious that…"], 1,
                    "'Tend to' allows exceptions.", "«tend to» استثنا را می‌پذیرد."),
                mcq("'Assimilation' means ___.", "«Assimilation» یعنی ___.", ["keeping your culture and joining", "becoming like the majority", "refusing to integrate", "living apart"], 1,
                    "Assimilation implies losing distinctiveness.", "assimilation یعنی از دست دادن تمایز."),
            ],
            [
                gap("The study measures social ___ — how far children move from their parents' income group.", ["mobility"], "Social mobility.", "تحرک اجتماعی."),
                gap("___ with the south, the north has shorter working hours.", ["Compared"], "Compared with / to.", "در مقایسه با."),
                mcq("Which sentence avoids stereotyping?", "کدام جمله از کلیشه پرهیز می‌کند؟", ["They are more relaxed about time.", "Arrivals tend to be later, on average.", "They never arrive on time.", "Their culture is disorganised."], 1,
                    "A measurable tendency with a hedge, not a trait.", "گرایش قابل اندازه‌گیری با احتیاط، نه خصلت."),
                mcq("A 'norm' is ___.", "«norm» ___ است.", ["a law", "what people expect of each other", "a personal belief", "a statistic"], 1,
                    "Norms are shared expectations.", "norm انتظارهای مشترک است."),
            ],
        ),
        lesson(
            "b2-u6-l3",
            "writing",
            ("The essay that argues both ways", "مقاله‌ای که هر دو طرف را می‌آورد"),
            ("Write 150 words that give both sides fairly and then commit.", "صدوپنجاه واژه بنویس که هر دو طرف را منصفانه بیاورد و بعد موضع بگیرد."),
            [
                ("Structure: introduce the question and signal that both sides exist, give two reasons for, two against with a concrete example each, then commit in the last two sentences. The commitment is what makes it an essay rather than a list.", "ساختار: پرسش را معرفی کن و بگو هر دو طرف هست، دو دلیل موافق و دو دلیل مخالف با یک مثال مشخص برای هر کدام بیاور و در دو جملهٔ آخر موضع بگیر. همان موضع، آن را از فهرست به مقاله تبدیل می‌کند."),
                ("Cohesion is more than connectors: repeat the key noun, use this/that to point back, and order the paragraphs so each one answers the previous. 'However' at the start of every paragraph is a symptom, not a style.", "انسجام بیش از واژه‌های ربط است: اسم کلیدی را تکرار کن، با this/that به قبل اشاره کن و پاراگراف‌ها را طوری بچین که هر کدام به قبلی پاسخ دهد. «However» در آغاز هر پاراگراف نشانهٔ مشکل است، نه سبک."),
                ("Hedging in an essay protects the argument: tends to, in most cases, the evidence suggests, it would be too simple to say. Absolute claims are easy to refute, and a reader who can refute you has stopped reading.", "احتیاط در مقاله از استدلال محافظت می‌کند: tends to، in most cases، the evidence suggests، it would be too simple to say. ادعای مطلق راحت رد می‌شود و خواننده‌ای که رد کند، خواندن را رها کرده است."),
            ],
            [
                ("Both sides: 'Supporters argue…, while critics point out…'", "هر دو طرف: «supporters argue…, while critics point out…»"),
                ("Evidence: 'in one survey of 300 graduates, a third had changed field within five years'.", "شواهد: «در نظرسنجی از ۳۰۰ دانش‌آموخته، یک‌سوم در پنج سال رشته را عوض کرده بودند»."),
                ("Commitment: 'on balance, the flexibility is worth the loss of certainty'.", "موضع: «در مجموع، انعطاف ارزش از دست دادن قطعیت را دارد»."),
            ],
            [
                mcq("What makes the last paragraph different from the others?", "پاراگراف آخر چه تفاوتی با بقیه دارد؟", ["it adds a new argument", "it states a position", "it repeats the introduction", "it asks a question"], 1,
                    "The essay commits there.", "مقاله همان‌جا موضع می‌گیرد."),
                mcq("Which is the best concession?", "کدام امتیاز دادن بهتر است؟", ["The other side is simply wrong.", "Critics are right that the cost is real, but it is temporary.", "Some people disagree.", "There is no other side."], 1,
                    "It grants the point and limits it.", "نکته را می‌پذیرد و محدودش می‌کند."),
            ],
            [
                write("Write an essay of about 150 words: 'University education should be free for everyone.' Give two reasons for and two against, each with an example, then state your own position.",
                       "مقاله‌ای حدود ۱۵۰ واژه بنویس: «تحصیل دانشگاهی باید برای همه رایگان باشد.» دو دلیل موافق و دو دلیل مخالف با مثال بیاور و بعد موضع خودت را بگو.",
                       150, ["although", "however"],
                       "Four paragraphs: the question, the case for, the case against, your position. One concrete example per side.",
                       "چهار پاراگراف: پرسش، دلایل موافق، دلایل مخالف، موضع تو. برای هر طرف یک مثال مشخص."),
                gap("Supporters argue that access improves, ___ critics point out the cost.", ["while", "whereas"], "Contrast within one sentence.", "تضاد در یک جمله."),
                mcq("Which opening signals a two-sided essay?", "کدام شروع مقالهٔ دوطرفه را نشان می‌دهد؟", ["Everyone knows university is expensive.", "The question divides opinion, and both sides have a case.", "I will now list the arguments.", "In conclusion, university should be free."], 1,
                    "It names the disagreement before arguing.", "پیش از استدلال، اختلاف را نام می‌برد."),
            ],
        ),
    ],
)
