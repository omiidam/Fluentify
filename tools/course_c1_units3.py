#!/usr/bin/env python3
"""C1 · units 5-6: who did it, and what is recommended.

Unit 5 is the passive at its most advanced — reporting passives, the passive of
attribution, and the reading that asks who benefits from an agentless sentence.
Unit 6 is the formal register of recommendation, where the subjunctive survives
and where 'should' would be too blunt.
"""

from course_kit import gap, lesson, mcq, passage, unit, write

U5 = unit(
    "c1-u5",
    ("It is believed that", "گفته می‌شود که"),
    ("Attribute claims without asserting them, and read for the agent an impersonal sentence hides.", "ادعاها را بی‌تصدیق نسبت بده و ببین جملهٔ بی‌شخص کدام عامل را پنهان می‌کند."),
    [
        lesson(
            "c1-u5-l1",
            "grammar",
            ("Reporting passives and the passive of attribution", "مجهول نقل قول و مجهول انتساب"),
            ("Report what is thought, said and believed without committing to it.", "آنچه اندیشیده، گفته و باور می‌شود را بی‌تعهد نقل کن."),
            [
                ("Two shapes do the same work. It is said that the scheme failed / The scheme is said to have failed. The first puts the claim in a that-clause and leaves the source unnamed; the second makes the subject of the rumour the subject of the sentence. Both are agentless by design.", "دو شکل یک کار می‌کنند. It is said that the scheme failed / The scheme is said to have failed. اولی ادعا را در بند that می‌گذارد و منبع را نام نمی‌برد؛ دومی موضوع شایعه را نهاد جمله می‌کند. هر دو به‌عمد بی‌عامل‌اند."),
                ("The verb set is small: say, think, believe, report, claim, allege, understand, consider, expect, estimate, rumour. Each carries a different amount of institutional weight. 'It is understood that' is diplomatic; 'it is alleged that' is legal; 'it is estimated that' is statistical.", "مجموعهٔ فعل کوچک است: say، think، believe، report، claim، allege، understand، consider، expect، estimate، rumour. هر کدام وزن نهادی متفاوتی دارند. «It is understood that» دیپلماتیک است، «it is alleged that» حقوقی و «it is estimated that» آماری."),
                ("Tense shifting matters: The scheme is said to be failing (now) / to have failed (before now) / to be about to fail (immediately after). With the infinitive perfect, the reporting verb stays present and the claim points backwards — which is why this form is so useful in journalism.", "جابه‌جایی زمان مهم است: The scheme is said to be failing (اکنون) / to have failed (پیش از اکنون) / to be about to fail (بی‌درنگ بعد). با مصدر کامل، فعل نقل حال می‌ماند و ادعا به عقب اشاره می‌کند — و همین این شکل را در روزنامه‌نگاری چنان کارآمد می‌کند."),
                ("Do not confuse this with the passive of a specific report: 'the committee reported the failure' → 'the failure was reported by the committee'. That passive keeps the agent available in a by-phrase; the reporting passive removes the agent entirely. The difference is accountability, and it is the reason the construction is worth arguing about.", "این را با مجهول گزارش مشخص اشتباه نگیر: «the committee reported the failure» ← «the failure was reported by the committee». آن مجهول عامل را در عبارت by نگه می‌دارد و مجهول نقل کاملاً حذفش می‌کند. تفاوت، پاسخ‌گویی است و همین دلیل بحث‌برانگیز بودن ساخت است."),
            ],
            [
                ("The bridge is believed to be structurally sound.", "باور بر این است که پل از نظر سازه سالم است."),
                ("It is alleged that the funds were transferred abroad.", "ادعا می‌شود که وجوه به خارج منتقل شده است."),
                ("She is understood to have resigned last week.", "شنیده می‌شود که او هفتهٔ گذشته استعفا داده است."),
                ("It is estimated that a third of the buildings need repair.", "برآورد می‌شود که یک‌سوم ساختمان‌ها نیاز به تعمیر دارند."),
            ],
            [
                mcq("Which sentence reports a past claim without naming the source?", "کدام جمله ادعای گذشته را بی‌نام بردن منبع نقل می‌کند؟", ["The committee reported the failure.", "The failure was reported by the committee.", "The scheme is said to have failed.", "The scheme failed."], 2,
                    "Reporting passive with a perfect infinitive.", "مجهول نقل با مصدر کامل."),
                mcq("'It is understood that…' typically signals ___.", "«It is understood that…» معمولاً نشانهٔ ___ است.", ["a legal allegation", "a diplomatic, unconfirmed position", "a statistical estimate", "a proven fact"], 1,
                    "It is the softest of the reporting formulas.", "نرم‌ترین فرمول نقل است."),
            ],
            [
                gap("The minister is ___ to have known about the payments.", ["believed", "said", "thought"], "Reporting passive + perfect infinitive.", "مجهول نقل + مصدر کامل."),
                gap("It is ___ that the two events are connected, though no evidence is offered.", ["alleged", "claimed"], "A claim without proof.", "ادعایی بی‌شواهد."),
                mcq("Which keeps the agent accountable?", "کدام عامل را پاسخ‌گو نگه می‌دارد؟", ["Mistakes were made.", "The failure was reported by the committee.", "It is said that mistakes were made.", "There were failures."], 1,
                    "The by-phrase names who did the reporting.", "عبارت by گویندهٔ گزارش را نام می‌برد."),
                mcq("'The scheme is said to be failing' locates the failure ___.", "«The scheme is said to be failing» شکست را ___ می‌گذارد.", ["in the past", "now", "in the future", "nowhere"], 1,
                    "The present infinitive points at current time.", "مصدر حال به زمان اکنون اشاره می‌کند."),
            ],
        ),
        lesson(
            "c1-u5-l2",
            "vocabulary",
            ("Science, research and the language of evidence", "علم، پژوهش و زبان شواهد"),
            ("Distinguish a hypothesis from a finding, and correlation from cause, in one precise move.", "فرضیه را از یافته و همبستگی را از علیت در یک حرکت دقیق جدا کن."),
            [
                ("Research vocabulary: a hypothesis, a variable, a control group, a sample, a cohort, a longitudinal study, a randomised trial, a replication, a meta-analysis, a peer review, a preprint, a confidence interval. The words are not decoration; each answers a specific question about how the claim was produced.", "واژگان پژوهش: hypothesis، variable، control group، sample، cohort، longitudinal study، randomised trial، replication، meta-analysis، peer review، preprint، confidence interval. این واژه‌ها تزئین نیستند؛ هر کدام به پرسشی مشخص دربارهٔ چگونگی تولید ادعا پاسخ می‌دهند."),
                ("The correlation–causation distinction has three standard escapes: reverse causation (B causes A), a common cause (C causes both), and selection (the groups differed before the intervention). Naming which escape applies is what turns 'correlation is not causation' from a slogan into an argument.", "تفکیک همبستگی از علیت سه راه فرار استاندارد دارد: علیت معکوس (B باعث A می‌شود)، علت مشترک (C هر دو را می‌سازد) و گزینش (گروه‌ها پیش از مداخله متفاوت بودند). نام بردن اینکه کدام راه فرار مصداق دارد، «همبستگی علیت نیست» را از شعار به استدلال تبدیل می‌کند."),
                ("Hedging that is precise rather than vague: the effect was modest but consistent; the association weakened after adjustment; the finding did not replicate; the sample was not powered to detect an effect that small. Each says what is uncertain and how much, which 'more research is needed' never does.", "احتیاط دقیق، نه مبهم: the effect was modest but consistent؛ the association weakened after adjustment؛ the finding did not replicate؛ the sample was not powered to detect an effect that small. هر کدام می‌گوید چه چیزی و چقدر نامعلوم است، کاری که «more research is needed» هرگز نمی‌کند."),
                ("Word formation and confusables: to replicate / a replication, to validate / validity / valid, to infer / inference, significant (statistical) vs important (practical), systematic vs systemic, principle vs principal, discrete vs discreet. Note that 'significant' in a research context usually means statistically detectable, not large.", "ساخت واژه و واژه‌های اشتباه‌شونده: replicate / replication، validate / validity / valid، infer / inference، significant (آماری) در برابر important (عملی)، systematic در برابر systemic، principle در برابر principal، discrete در برابر discreet. «significant» در بافت پژوهش معمولاً یعنی قابل تشخیص آماری، نه بزرگ."),
            ],
            [
                ("The finding did not replicate in a larger sample.", "یافته در نمونهٔ بزرگ‌تر تکرار نشد."),
                ("The association weakened after adjusting for income.", "پیوند پس از تعدیل برای درآمد ضعیف شد."),
                ("Reverse causation cannot be ruled out here.", "علیت معکوس را اینجا نمی‌توان رد کرد."),
                ("The effect was statistically significant and practically trivial.", "اثر از نظر آماری معنادار و از نظر عملی ناچیز بود."),
            ],
            [
                mcq("Which is a threat to a causal claim?", "کدام تهدید برای ادعای علی است؟", ["a large sample", "reverse causation", "peer review", "a control group"], 1,
                    "The effect may run the other way.", "اثر ممکن است در جهت مخالف باشد."),
                mcq("'The finding did not replicate' means ___.", "«The finding did not replicate» یعنی ___.", ["it was not published", "the repeat study did not reproduce it", "it was too small", "it was reviewed"], 1,
                    "Replication is a repeat that succeeds or fails.", "replication تکرار موفق یا ناموفق است."),
            ],
            [
                gap("The sample was too small to ___ an effect of that size.", ["detect"], "Detect an effect: to be able to measure it.", "detect an effect یعنی توان اندازه‌گیری آن."),
                gap("The study could not rule ___ reverse causation.", ["out"], "Rule out = exclude.", "rule out یعنی کنار گذاشتن."),
                mcq("Which pair is often confused?", "کدام جفت اغلب اشتباه می‌شود؟", ["systematic / systemic", "sample / cohort", "trial / test", "data / finding"], 0,
                    "Systematic = methodical; systemic = across the whole system.", "systematic یعنی روشمند و systemic یعنی در کل سیستم."),
                mcq("In research writing, 'significant' usually means ___.", "در نوشتار پژوهشی «significant» معمولاً یعنی ___.", ["important", "statistically detectable", "large", "surprising"], 1,
                    "It is a technical term about detectability.", "واژه‌ای فنی دربارهٔ قابل تشخیص بودن است."),
            ],
        ),
        lesson(
            "c1-u5-l3",
            "reading",
            ("Reading the agentless sentence", "خواندن جملهٔ بی‌عامل"),
            ("Notice who disappears from a sentence, and what that disappearance does to responsibility.", "ببین چه کسی از جمله ناپدید می‌شود و این ناپدید شدن با مسئولیت چه می‌کند."),
            [
                ("Passives without agents are not automatically evasive. Sometimes the agent is unknown ('the manuscript was written in the twelfth century'), irrelevant ('the forms are processed centrally') or obvious ('the suspect was arrested'). The question to ask is whether the sentence would be more informative with the agent in it.", "مجهول‌های بی‌عامل خودکار پنهان‌کار نیستند. گاهی عامل ناشناخته است («the manuscript was written in the twelfth century»)، بی‌ربط است («the forms are processed centrally») یا آشکار است («the suspect was arrested»). پرسش این است که آیا جمله با آوردن عامل آگاهی‌بخش‌تر می‌شود."),
                ("Nominalisation and agentless passives cluster in institutional writing for a reason: they allow a document to describe a decision without attributing it. 'A decision was taken to close the site' is grammatically complete and answers nothing. The reader who notices this can ask the one question the text was built to avoid.", "اسم‌سازی و مجهول بی‌عامل در نوشتار نهادی دلیلی دارند: سند می‌تواند تصمیمی را توصیف کند بی‌آنکه آن را به کسی نسبت دهد. «A decision was taken to close the site» از نظر دستوری کامل است و به هیچ چیز پاسخ نمی‌دهد. خواننده‌ای که این را ببیند می‌تواند همان پرسشی را بپرسد که متن برای پرهیز از آن ساخته شده."),
                ("Agency also moves through metaphor. A market 'punishes', a policy 'signals', a system 'fails'. When an abstraction becomes the subject of a deliberate verb, responsibility has been transferred to something that cannot be held to account. C1 reading means noticing the transfer, not rejecting it — metaphor is often doing necessary compression.", "عامل از راه استعاره هم جابه‌جا می‌شود. بازار «تنبیه می‌کند»، سیاست «علامت می‌دهد»، سیستم «شکست می‌خورد». وقتی انتزاعی نهادِ فعلی ارادی می‌شود، مسئولیت به چیزی منتقل شده که نمی‌توان بازخواستش کرد. خواندن C1 یعنی دیدن این انتقال، نه رد کردنش — استعاره اغلب فشرده‌سازی لازم را انجام می‌دهد."),
                ("Practical test: rewrite the sentence with a named subject. If the rewrite is easy and the original did not do it, the omission is a choice. If the rewrite is impossible without invention, the agentless form was honest. That test takes ten seconds and separates analysis from suspicion.", "آزمون عملی: جمله را با نهادی نام‌دار بازنویسی کن. اگر بازنویسی آسان است و اصل انجامش نداده، حذف یک انتخاب بوده. اگر بازنویسی بدون ساختن چیزی ممکن نیست، شکل بی‌عامل صادق بوده. این آزمون ده ثانیه می‌برد و تحلیل را از بدگمانی جدا می‌کند."),
            ],
            [
                ("Mistakes were made, and lessons will be learned.", "خطاهایی رخ داد و درس‌هایی گرفته خواهد شد."),
                ("A decision was taken to reduce the workforce.", "تصمیم گرفته شد نیروی کار کاهش یابد."),
                ("The manuscript was copied by three scribes.", "دست‌نوشته را سه کاتب رونویسی کردند."),
                ("The market punished the announcement within an hour.", "بازار اعلامیه را در یک ساعت تنبیه کرد."),
            ],
            [
                mcq("When is an agentless passive honest?", "مجهول بی‌عامل کِی صادق است؟", ["when the agent is powerful", "when the agent is unknown or irrelevant", "when the sentence is short", "when it is in a report"], 1,
                    "The omission then reflects real ignorance.", "حذف در این حالت بازتاب ناآگاهی واقعی است."),
                mcq("'A decision was taken' answers which question?", "«A decision was taken» به کدام پرسش پاسخ می‌دهد؟", ["who decided", "that a decision exists", "why it was taken", "when it was taken"], 1,
                    "It reports the existence of a decision only.", "فقط وجود تصمیم را گزارش می‌کند."),
            ],
            [
                mcq("Why does institutional writing favour the agentless passive?", "چرا نوشتار نهادی مجهول بی‌عامل را ترجیح می‌دهد؟", ["to sound educated", "to record decisions without assigning them", "to save space", "to avoid errors"], 1,
                    "It lets a document record without attributing.", "سند را قادر می‌کند ثبت کند بی‌آنکه نسبت دهد."),
                mcq("What repair does the author propose?", "نویسنده چه ترمیمی پیشنهاد می‌کند؟", ["ban the passive", "name the person or at least the office", "shorten the report", "add an appendix"], 1,
                    "'Naming the office is not the same as blaming a person.'", "«نام بردن اداره با سرزنش شخص یکی نیست»."),
                mcq("The author's attitude to the passive is ___.", "نگرش نویسنده به مجهول ___ است.", ["hostile", "qualified", "indifferent", "celebratory"], 1,
                    "'The passive is not dishonest'; the problem is the cumulative effect.", "«مجهول ناصادق نیست»؛ مشکل اثر انباشته است."),
            ],
            passage=passage(("The passive that built a bridge", "مجهولی که پلی ساخت"),
                                    ("The inquiry into the collapse published four hundred pages and used the passive voice for most of them. 'The design was approved.' 'Concerns were raised.' 'The inspection was deferred.' Each sentence is true, and each one has had its subject surgically removed.\n\nThis is not, as critics often claim, a conspiracy of grammar. Institutional writing drifts towards the agentless passive because it is the only register in which a document can record a decision without assigning it, and most documents are written by people who do not have the authority to assign it. The civil servant who writes 'concerns were raised' may be describing a meeting he attended, in which concerns were indeed raised, by people whose names he is not permitted to publish.\n\nBut the cumulative effect is a text in which nobody did anything. Four hundred pages of deferred inspection, and not one sentence that says who deferred it. The reader is left with a process that failed on its own, like a machine wearing out.\n\nThere is a repair, and it is not a stylistic preference. The inquiry could have written 'the regional engineer deferred the inspection', and where it could not name the person, it could have named the office. Naming the office is not the same as blaming a person; it is the minimum a public document owes a reader who wants to know where to write. The passive is not dishonest. A four-hundred-page passive is a decision about what a document is for.",
                                     "تحقیق دربارهٔ فروریختن پل چهارصد صفحه منتشر کرد و در بیشترشان مجهول به کار برد. «طرح تأیید شد.» «نگرانی‌هایی مطرح شد.» «بازرسی به تعویق افتاد.» هر جمله درست است و هر جمله نهادش را با جراحی برداشته‌اند.\n\nاین، آن‌طور که منتقدان اغلب می‌گویند، توطئهٔ دستور زبان نیست. نوشتار نهادی به مجهول بی‌عامل می‌گراید چون تنها لحنی است که سند می‌تواند در آن تصمیمی را ثبت کند بی‌آنکه به کسی نسبتش دهد، و بیشتر اسناد را کسانی می‌نویسند که اختیار نسبت دادن ندارند. کارمندی که «نگرانی‌هایی مطرح شد» می‌نویسد شاید جلسه‌ای را توصیف می‌کند که در آن واقعاً نگرانی‌هایی مطرح شد، به دست کسانی که اجازهٔ انتشار نامشان را ندارد.\n\nاما اثر انباشته متنی است که در آن هیچ‌کس هیچ کاری نکرد. چهارصد صفحه بازرسی تعویق‌افتاده و یک جمله که بگوید چه کسی تعویقش انداخت. خواننده با فرایندی می‌ماند که خودش شکست خورد، مثل ماشینی که فرسوده شد.\n\nترمیمی هست و ترجیح سبکی نیست. تحقیق می‌توانست بنویسد «مهندس منطقه بازرسی را به تعویق انداخت» و جایی که نمی‌توانست شخص را نام ببرد، می‌توانست اداره را نام ببرد. نام بردن اداره با سرزنش یک شخص یکی نیست؛ کمترین چیزی است که سند عمومی به خواننده‌ای بدهکار است که می‌خواهد بداند کجا بنویسد. مجهول ناصادق نیست. چهارصد صفحه مجهول تصمیمی است دربارهٔ اینکه سند برای چه ساخته شده.")),
        ),
    ],
)

U6 = unit(
    "c1-u6",
    ("It is recommended that", "توصیه می‌شود که"),
    ("Recommend formally, argue from a stated criterion, and write the proposal that gets a decision.", "رسمی توصیه کن، از معیاری اعلام‌شده استدلال کن و پیشنهادی بنویس که تصمیم بگیرد."),
    [
        lesson(
            "c1-u6-l1",
            "grammar",
            ("The subjunctive and the formal recommendation", "وجه شرطی و توصیهٔ رسمی"),
            ("Use the mandative subjunctive and its alternatives without sounding archaic.", "وجه شرطیِ الزامی و جانشین‌هایش را به کار ببر بی‌آنکه کهنه به گوش برسی."),
            [
                ("The mandative subjunctive uses the base form after verbs of demand and recommendation: the board recommended that the policy be reviewed; they insisted that he resign. There is no -s in the third person and no tense marking — 'that the policy be reviewed', never 'is reviewed'.", "وجه شرطی الزامی پس از فعل‌های درخواست و توصیه شکل پایه می‌گیرد: the board recommended that the policy be reviewed؛ they insisted that he resign. در سوم‌شخص s ندارد و زمان نشان نمی‌دهد — «that the policy be reviewed»، هرگز «is reviewed»."),
                ("It survives mainly in formal and institutional English: reports, resolutions, contracts, legal drafting. Three alternatives are equally correct and more common in speech: should (that the policy should be reviewed), the indicative (that the policy is reviewed), and a to-infinitive after the verb (the board recommended the policy to be reviewed — rarer and stiffer).", "این ساخت عمدتاً در انگلیسی رسمی و نهادی زنده مانده: گزارش‌ها، قطعنامه‌ها، قراردادها، متن حقوقی. سه جانشین به‌همان اندازه درست و در گفتار رایج‌ترند: should (that the policy should be reviewed)، اخباری (that the policy is reviewed) و مصدر پس از فعل (the board recommended the policy to be reviewed — کم‌کاربردتر و خشک‌تر)."),
                ("Negative subjunctive: that the policy not be changed. 'Do not' is impossible there — 'that the policy not to be changed' is wrong on two counts. The negative is formed before the base verb, which is one reason the construction is easy to get wrong under pressure.", "وجه شرطی منفی: that the policy not be changed. «do not» آنجا ممکن نیست — «that the policy not to be changed» از دو جهت غلط است. منفی پیش از فعل پایه ساخته می‌شود و همین یکی از دلایل خطای رایج این ساخت زیر فشار است."),
                ("Other formal frames for recommendation, in order of force: it is essential that, it is imperative that, it is recommended that, it would be advisable to, it might be worth considering. The last is the weakest and the most useful in a document that must not commit its author.", "قاب‌های رسمی دیگر برای توصیه، به ترتیب نیرو: it is essential that، it is imperative that، it is recommended that، it would be advisable to، it might be worth considering. آخری ضعیف‌ترین و سودمندترین است در سندی که نباید نویسنده‌اش را متعهد کند."),
            ],
            [
                ("It is recommended that the trial be extended by six months.", "توصیه می‌شود آزمایش شش ماه تمدید شود."),
                ("The committee insisted that the report not be published.", "کمیته اصرار کرد گزارش منتشر نشود."),
                ("It is essential that every claim be attributed.", "ضروری است هر ادعا به منبعش نسبت داده شود."),
                ("It would be advisable to consult the legal team first.", "مصلحت است نخست با تیم حقوقی مشورت شود."),
            ],
            [
                mcq("The board recommended that the policy ___.", "هیئت‌مدیره توصیه کرد سیاست ___ .", ["is reviewed", "be reviewed", "was reviewed", "to be reviewed"], 1,
                    "Mandative subjunctive: base form after recommend that.", "وجه شرطی الزامی: شکل پایه پس از recommend that."),
                mcq("Which is the weakest recommendation?", "کدام توصیه ضعیف‌ترین است؟", ["It is essential that…", "It is imperative that…", "It might be worth considering…", "It is recommended that…"], 2,
                    "It commits the writer to nothing.", "نویسنده را به چیزی متعهد نمی‌کند."),
            ],
            [
                gap("They insisted that he ___ (not / inform) the press.", ["not inform"], "Negative subjunctive: not + base form.", "وجه شرطی منفی: not + شکل پایه."),
                gap("It is ___ that all figures be checked twice. (strongest form)", ["essential", "imperative"], "The strongest of the frames.", "قوی‌ترین قاب."),
                mcq("Which alternative is also correct?", "کدام جانشین هم درست است؟", ["that the policy should be reviewed", "that the policy to be reviewed", "that the policy be review", "that the policy reviews"], 0,
                    "Should + base is a standard alternative.", "should + پایه جانشین استاندارد است."),
                mcq("Where is the subjunctive most at home?", "وجه شرطی بیشتر کجا خانه دارد؟", ["casual conversation", "resolutions and contracts", "text messages", "song lyrics"], 1,
                    "Formal institutional drafting.", "نگارش نهادی رسمی."),
            ],
        ),
        lesson(
            "c1-u6-l2",
            "vocabulary",
            ("Leadership, organisations and decision", "رهبری، سازمان و تصمیم‌گیری"),
            ("Talk about authority, incentives and failure with terms that survive scrutiny.", "دربارهٔ اقتدار، انگیزه و شکست با واژه‌هایی حرف بزن که نقد را تاب بیاورند."),
            [
                ("Organisation vocabulary: authority, accountability, a mandate, a hierarchy, delegation, autonomy, a stakeholder, an incentive, a trade-off, a bottleneck, a silo, attrition, turnover. Accountability is answerability for a decision; responsibility is the duty to carry it out. Organisations collapse the two and then wonder why nobody owns anything.", "واژگان سازمان: authority، accountability، mandate، hierarchy، delegation، autonomy، stakeholder، incentive، trade-off، bottleneck، silo، attrition، turnover. accountability پاسخ‌گویی برای تصمیم است و responsibility وظیفهٔ اجرا. سازمان‌ها این دو را یکی می‌کنند و بعد می‌پرسند چرا هیچ‌کس مالک چیزی نیست."),
                ("Decision vocabulary: to weigh the options, to set a criterion, to defer a decision, to escalate, to sign off, to reverse course, to commit resources, a sunk cost, a pilot, a rollback. 'Sunk cost' is the most useful and the most ignored: the money is gone whether or not the project continues.", "واژگان تصمیم: weigh the options، set a criterion، defer a decision، escalate، sign off، reverse course، commit resources، sunk cost، pilot، rollback. «sunk cost» سودمندترین و نادیده‌گرفته‌شده‌ترین است: پول رفته است، پروژه ادامه یابد یا نه."),
                ("Failure vocabulary that is not euphemism: a near miss, a systemic failure, a single point of failure, an unforced error, a blind spot, a warning sign, a post-mortem. Blameless post-mortems exist because a report that punishes honesty produces a report that contains no honesty.", "واژگان شکست بی‌لفظ‌سازی: near miss، systemic failure، single point of failure، unforced error، blind spot، warning sign، post-mortem. بازبینی بی‌سرزنش وجود دارد چون گزارشی که صداقت را تنبیه کند گزارشی است بدون صداقت."),
                ("Word formation and register: to lead / leadership, to manage / management (managing things vs leading people), to decide / decision / decisive / indecisive. 'Decisive' is praise; 'indecisive' is criticism; neither says anything about whether the decision was right, which is why the words are so popular.", "ساخت واژه و لحن: lead / leadership، manage / management (مدیریت چیزها در برابر رهبری آدم‌ها)، decide / decision / decisive / indecisive. «decisive» تعریف است و «indecisive» نقد؛ هیچ‌کدام نمی‌گویند تصمیم درست بود یا نه و همین محبوبشان کرده."),
            ],
            [
                ("The decision was escalated because nobody had the mandate to make it.", "تصمیم بالا رفت چون هیچ‌کس اختیار گرفتنش را نداشت."),
                ("The pilot ran for six weeks before the rollback.", "آزمایش شش هفته ادامه یافت تا بازگردانی."),
                ("Continuing the project is a sunk-cost decision, not an investment.", "ادامهٔ پروژه تصمیمی بر پایهٔ هزینهٔ رفته است، نه سرمایه‌گذاری."),
                ("The post-mortem was blameless, and it produced three real findings.", "بازبینی بی‌سرزنش بود و سه یافتهٔ واقعی داد."),
            ],
            [
                mcq("'Accountability' means ___.", "«Accountability» یعنی ___.", ["carrying out the task", "being answerable for the decision", "having authority", "sharing the work"], 1,
                    "Answerability, not execution.", "پاسخ‌گویی، نه اجرا."),
                mcq("A 'sunk cost' should ___.", "«Sunk cost» باید ___.", ["drive the decision", "be ignored in the decision", "be recovered first", "be reported"], 1,
                    "It is unrecoverable and irrelevant to the forward choice.", "بازنگشتنی و بی‌ربط به انتخاب پیش‌رو است."),
            ],
            [
                gap("The lack of a clear ___ meant the decision kept moving up the hierarchy.", ["mandate"], "Authority to decide.", "اختیار تصمیم."),
                gap("The team ran a blameless ___ after the outage.", ["post-mortem", "postmortem"], "A review after failure.", "بازبینی پس از شکست."),
                mcq("A 'blind spot' is ___.", "«Blind spot» ___ است.", ["a deliberate error", "something the organisation cannot see about itself", "a legal risk", "a budget gap"], 1,
                    "It is invisible from the inside.", "از درون دیده نمی‌شود."),
                mcq("Which pair is correctly contrasted?", "کدام جفت درست مقابله شده است؟", ["manage things / lead people", "lead things / manage people", "manage money / lead money", "lead budgets / manage budgets"], 0,
                    "Management coordinates; leadership sets direction.", "مدیریت هماهنگ می‌کند و رهبری جهت می‌دهد."),
            ],
        ),
        lesson(
            "c1-u6-l3",
            "writing",
            ("The proposal that survives a committee", "پیشنهادی که از کمیته بیرون می‌آید"),
            ("Write a proposal with an explicit criterion, two options and a defensible recommendation.", "پیشنهادی با معیار صریح، دو گزینه و توصیه‌ای قابل دفاع بنویس."),
            [
                ("A proposal differs from a report in one respect: it asks for a decision, so it must state the criterion by which the options were judged. Without a stated criterion, the recommendation is a preference, and a committee will treat it as one.", "پیشنهاد در یک جهت از گزارش متفاوت است: تصمیم می‌خواهد، پس باید معیاری را که گزینه‌ها با آن سنجیده شد بگوید. بی معیار اعلام‌شده، توصیه یک ترجیح است و کمیته هم همین‌طور با آن رفتار می‌کند."),
                ("Structure: the problem in two sentences, the criterion, the options (at least two, one of which is 'do nothing'), the comparison against the criterion, the recommendation, the cost and the risk. 'Do nothing' is not a rhetorical device; it is often the correct option and always the one the committee will otherwise supply itself.", "ساختار: مسئله در دو جمله، معیار، گزینه‌ها (دست‌کم دو، یکی «هیچ کاری نکردن»)، مقایسه بر پایهٔ معیار، توصیه، هزینه و ریسک. «هیچ کاری نکردن» تمهید بلاغی نیست؛ اغلب گزینهٔ درست است و همیشه گزینه‌ای است که کمیته خودش تأمین می‌کند اگر تو نکنی."),
                ("Register: impersonal, no contractions, subjunctive where a recommendation is stated ('it is recommended that the pilot be extended'), and numbers with their base. Hedging is not weakness here: 'the evidence suggests' protects the proposal when the pilot disappoints, and a proposal that cannot survive its own pilot should not be approved.", "لحن: بی‌شخص، بدون شکل کوتاه، وجه شرطی در بیان توصیه («it is recommended that the pilot be extended») و عددها با پایه‌شان. احتیاط اینجا ضعف نیست: «the evidence suggests» پیشنهاد را وقتی آزمایش ناامید می‌کند حفظ می‌کند و پیشنهادی که آزمایش خودش را تاب نیاورد نباید تأیید شود."),
                ("Length and rhythm: alternate a short sentence with a longer one. A proposal entirely in long nominalised sentences reads as evasion; entirely in short ones reads as a slide deck. The alternation is what makes a document sound as though a person wrote it and meant it.", "طول و آهنگ: جملهٔ کوتاه را با بلندتر یکی در میان کن. پیشنهادی که همه‌اش جمله‌های بلند اسمی است پنهان‌کاری خوانده می‌شود و پیشنهادی که همه‌اش کوتاه است اسلاید. همین یکی‌درمیان بودن باعث می‌شود سند به گوش برسد که آدمی نوشته و باورش داشته."),
            ],
            [
                ("The criterion is cost per pupil, not total cost.", "معیار هزینهٔ هر دانش‌آموز است، نه هزینهٔ کل."),
                ("Option three is to do nothing for a year and re-examine the demand.", "گزینهٔ سوم این است که یک سال هیچ نکنیم و تقاضا را دوباره بسنجیم."),
                ("It is recommended that the pilot be extended to two more branches.", "توصیه می‌شود آزمایش به دو شعبهٔ دیگر گسترش یابد."),
                ("The principal risk is that demand falls before the second phase.", "ریسک اصلی این است که تقاضا پیش از مرحلهٔ دوم بیفتد."),
            ],
            [
                mcq("What must a proposal state that a report need not?", "پیشنهاد چه چیزی را باید بگوید که گزارش لازم ندارد؟", ["the budget", "the criterion for judging options", "the author", "the date"], 1,
                    "The criterion is what makes the choice arguable.", "معیار انتخاب را قابل بحث می‌کند."),
                mcq("Why include a 'do nothing' option?", "چرا گزینهٔ «هیچ کاری نکردن» را بیاوریم؟", ["to fill space", "because it is often correct and always relevant", "to seem cautious", "because committees require it"], 1,
                    "It is a real alternative with real costs.", "گزینه‌ای واقعی با هزینه‌های واقعی است."),
            ],
            [
                write("Write a proposal of about 150 words recommending whether a company should keep its four-day week. State the criterion, compare two options (one of which is returning to five days), recommend one, and name the main risk.",
                       "پیشنهادی حدود ۱۵۰ واژه بنویس و توصیه کن شرکت هفتهٔ چهارروزه را نگه دارد یا نه. معیار را بگو، دو گزینه (یکی بازگشت به پنج روز) را مقایسه کن، یکی را توصیه کن و ریسک اصلی را نام ببر.",
                       150, ["recommended", "whereas"],
                       "Use the subjunctive once, no contractions, and give the base for any percentage.",
                       "یک بار وجه شرطی به کار ببر، شکل کوتاه ننویس و برای هر درصد پایه‌اش را بده."),
                gap("Option two is to ___ to five days and review in six months.", ["return", "revert"], "Return / revert to a previous arrangement.", "return یا revert به وضع پیشین."),
                mcq("Which sentence states a criterion?", "کدام جمله معیار را بیان می‌کند؟", ["Option A is better.", "Options are judged on cost per pupil.", "The committee preferred A.", "A is more popular."], 1,
                    "It names the measure, not the verdict.", "معیار را نام می‌برد، نه حکم را."),
            ],
        ),
    ],
)
