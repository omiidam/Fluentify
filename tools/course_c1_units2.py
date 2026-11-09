#!/usr/bin/env python3
"""C1 · units 3-4: packing meaning into nouns, and leaving words out.

Unit 3 is nominalization — the move that makes academic prose sound like itself,
for better and for worse — and the summary that has to compress a source without
distorting it. Unit 4 is ellipsis and substitution, which is what makes a debate
sound like a conversation rather than a series of statements.
"""

from course_kit import dialogue, gap, lesson, listen, mcq, unit, write

U3 = unit(
    "c1-u3",
    ("The packing of meaning", "فشرده‌سازی معنا"),
    ("Turn clauses into noun phrases, then compress a source into a summary that keeps its argument.", "بندها را به گروه اسمی تبدیل کن و بعد منبعی را به خلاصه‌ای فشرده کن که استدلالش را نگه دارد."),
    [
        lesson(
            "c1-u3-l1",
            "grammar",
            ("Nominalization and the complex noun phrase", "اسم‌سازی و گروه اسمی پیچیده"),
            ("Compress a clause into a noun phrase, and recognize when that compression hides the agent.", "بند را به گروه اسمی فشرده کن و ببین این فشردگی کِی عامل را پنهان می‌کند."),
            [
                ("Nominalization turns a verb or adjective into a noun: prices rose because demand increased → the rise in prices was driven by an increase in demand. Two clauses become one, and the sentence gains density and loses directness. That trade is the whole issue.", "اسم‌سازی فعل یا صفت را به اسم تبدیل می‌کند: prices rose because demand increased ← the rise in prices was driven by an increase in demand. دو بند یکی می‌شود و جمله چگالی می‌گیرد و صراحت را از دست می‌دهد. همین بده‌بستان کل مسئله است."),
                ("The cost is agency. 'Mistakes were made' has no subject; 'the implementation of the policy resulted in unintended outcomes' has no actor either. Nominalization is the grammatical form of institutional distance, and a C1 writer uses it when the distance is meant and avoids it when it is a hiding place.", "بهایش از دست رفتن عامل است. «Mistakes were made» نهاد ندارد و «the implementation of the policy resulted in unintended outcomes» هم کنشگر ندارد. اسم‌سازی شکل دستوری فاصلهٔ نهادی است؛ نویسندهٔ C1 وقتی فاصله مقصود است به کارش می‌برد و وقتی پناهگاه است رهایش می‌کند."),
                ("Complex noun phrases build leftwards: the premodifiers stack before the head noun (a long-delayed, under-funded regional transport review) and the postmodifiers follow it (the review of regional transport that was delayed by two years). English tolerates about three premodifiers before the reader slows down.", "گروه‌های اسمی پیچیده به چپ ساخته می‌شوند: پیش‌آیندها پیش از اسم هسته انباشته می‌شوند (a long-delayed, under-funded regional transport review) و پس‌آیندها پس از آن می‌آیند (the review of regional transport that was delayed by two years). انگلیسی تا حدود سه پیش‌آیند را تحمل می‌کند و بعد خواننده کند می‌شود."),
                ("Precision tools in the noun phrase: of-phrases for possession and topic, compound nouns for category (a transport review, a review board), and hyphenated premodifiers where ambiguity would otherwise occur (a two-year delay, a well-run service). Hyphens disappear when the phrase moves after the noun: the delay lasted two years.", "ابزار دقت در گروه اسمی: عبارت‌های of برای مالکیت و موضوع، اسم‌های مرکب برای مقوله (a transport review، a review board) و پیش‌آیندهای خط‌تیره‌دار جایی که ابهام پیش می‌آید (a two-year delay، a well-run service). خط تیره وقتی عبارت پس از اسم می‌آید حذف می‌شود: the delay lasted two years."),
            ],
            [
                ("The sharp rise in applications followed the change in the deadline.", "افزایش شدید درخواست‌ها پس از تغییر مهلت رخ داد."),
                ("A poorly funded, hastily designed scheme was abandoned within a year.", "طرحی کم‌بودجه و شتاب‌زده در یک سال رها شد."),
                ("The refusal of the committee to publish the report damaged trust.", "امتناع کمیته از انتشار گزارش به اعتماد آسیب زد."),
                ("There was a marked decline in the number of applicants.", "کاهش چشمگیری در شمار متقاضیان رخ داد."),
            ],
            [
                mcq("Which sentence has been nominalized?", "کدام جمله اسم‌سازی شده است؟", ["The council decided quickly.", "The council's quick decision surprised nobody.", "The council decided, and it was quick.", "Quickly, the council decided."], 1,
                    "The verb became a noun phrase with a possessive agent.", "فعل به گروه اسمی با عامل ملکی تبدیل شده است."),
                mcq("What does nominalization tend to hide?", "اسم‌سازی معمولاً چه چیزی را پنهان می‌کند؟", ["the time", "the agent", "the object", "the number"], 1,
                    "The actor becomes optional.", "کنشگر اختیاری می‌شود."),
            ],
            [
                gap("The ___ (fail) of the negotiations was never explained.", ["failure"], "Nominalize the verb.", "فعل را اسم کن."),
                gap("It was a well-___ service before the cuts. (hyphenated premodifier)", ["run"], "A compound premodifier keeps its hyphen.", "پیش‌آیند مرکب خط تیره‌اش را نگه می‌دارد."),
                mcq("Which is the most natural complex noun phrase?", "کدام گروه اسمی پیچیده طبیعی‌تر است؟", ["the review of transport regional long-delayed", "the long-delayed review of regional transport", "the regional long transport delayed review", "review the regional transport long-delayed"], 1,
                    "Premodifiers before the head, postmodifiers after it.", "پیش‌آیند پیش از هسته و پس‌آیند پس از آن."),
                mcq("'There was a decline in applications' is more formal but less direct than ___.", "«There was a decline in applications» رسمی‌تر اما کم‌صراحت‌تر از ___ است.", ["applications declined", "applications are declining", "declining applications", "the applications"], 0,
                    "The verbal form names the action and its subject.", "شکل فعلی کنش و نهادش را نام می‌برد."),
            ],
        ),
        lesson(
            "c1-u3-l2",
            "vocabulary",
            ("Global affairs and environmental policy", "امور جهانی و سیاست محیطی"),
            ("Discuss treaties, targets and trade-offs with the precision the subject requires.", "دربارهٔ معاهدات، هدف‌ها و بده‌بستان‌ها با دقت لازم بحث کن."),
            [
                ("Policy vocabulary: a binding target, a voluntary pledge, a commitment, an obligation, a sanction, a subsidy, a levy, a moratorium, ratification, compliance, enforcement. The distinction between binding and voluntary is where most climate arguments actually live.", "واژگان سیاست: binding target، voluntary pledge، commitment، obligation، sanction، subsidy، levy، moratorium، ratification، compliance، enforcement. تفاوت binding و voluntary همان جایی است که بیشتر بحث‌های اقلیمی در آن رخ می‌دهد."),
                ("Environmental vocabulary: emissions, carbon footprint, net zero, mitigation, adaptation, biodiversity, deforestation, depletion, contamination, resilience, a tipping point, a feedback loop. Mitigation reduces the cause; adaptation reduces the damage. Using them interchangeably is the commonest error in the field.", "واژگان محیطی: emissions، carbon footprint، net zero، mitigation، adaptation، biodiversity، deforestation، depletion، contamination، resilience، tipping point، feedback loop. mitigation علت را کم می‌کند و adaptation آسیب را؛ یکی گرفتنشان رایج‌ترین خطای این حوزه است."),
                ("Global-affairs collocations: to ratify a treaty, to meet a target, to fall short of a commitment, to phase out a fuel, to impose a levy, to hold a party to account, to reach a settlement, to escalate a dispute, to broker a deal. Note 'fall short of', not 'fail of'.", "هم‌نشینی‌های امور جهانی: ratify a treaty، meet a target، fall short of a commitment، phase out a fuel، impose a levy، hold a party to account، reach a settlement، escalate a dispute، broker a deal. توجه: «fall short of»، نه «fail of»."),
                ("Evaluative vocabulary that stays honest: modest, marginal, substantial, unprecedented, contested, disputed, unverifiable, well-documented. A C1 writer prefers 'the evidence for the claim is contested' to 'the claim is a lie', because the first can be defended and the second has to be.", "واژگان ارزشی صادق: modest، marginal، substantial، unprecedented، contested، disputed، unverifiable، well-documented. نویسندهٔ C1 «the evidence for the claim is contested» را به «the claim is a lie» ترجیح می‌دهد، چون اولی قابل دفاع است و دومی باید ثابت شود."),
            ],
            [
                ("The target is binding, but the enforcement mechanism is voluntary.", "هدف الزام‌آور است، اما سازوکار اجرا اختیاری."),
                ("Adaptation funding has lagged behind mitigation funding for a decade.", "بودجهٔ سازگاری یک دهه از بودجهٔ کاهش عقب مانده است."),
                ("Three countries have yet to ratify the treaty.", "سه کشور هنوز معاهده را تصویب نکرده‌اند."),
                ("The government fell short of its own commitment by a wide margin.", "دولت به‌فاصلهٔ زیاد از تعهد خود بازماند."),
            ],
            [
                mcq("Which reduces the cause rather than the damage?", "کدام علت را کم می‌کند نه آسیب را؟", ["adaptation", "mitigation", "resilience", "recovery"], 1,
                    "Mitigation cuts emissions; adaptation copes with effects.", "mitigation انتشار را کم می‌کند و adaptation با اثرها کنار می‌آید."),
                mcq("A 'binding' target is one that ___.", "هدف «binding» هدفی است که ___.", ["is recommended", "creates a legal obligation", "is voluntary", "has been achieved"], 1,
                    "Binding means enforceable in law.", "binding یعنی قابل اجرا در قانون."),
            ],
            [
                gap("The country failed to ___ the agreement until 2021.", ["ratify"], "Ratify a treaty.", "معاهده را تصویب کردن."),
                gap("The levy is intended to ___ out the most polluting vehicles.", ["phase"], "Phase out = withdraw gradually.", "phase out یعنی تدریجاً کنار گذاشتن."),
                mcq("Which collocation is correct?", "کدام هم‌نشینی درست است؟", ["fall short of a target", "fall short to a target", "fall short from a target", "fall short in a target"], 0,
                    "The fixed form is 'fall short of'.", "شکل ثابت «fall short of» است."),
                mcq("'The finding is contested' means ___.", "«The finding is contested» یعنی ___.", ["it is proven", "it is disputed", "it is published", "it is irrelevant"], 1,
                    "Contested = others dispute it.", "contested یعنی دیگران بر سرش اختلاف دارند."),
            ],
        ),
        lesson(
            "c1-u3-l3",
            "writing",
            ("The summary that keeps the argument", "خلاصه‌ای که استدلال را نگه می‌دارد"),
            ("Compress a source to 120 words without dropping its position or its caveat.", "منبعی را به ۱۲۰ واژه فشرده کن بی‌آنکه موضع و احتیاطش را از دست بدهی."),
            [
                ("A summary is not a shorter text; it is the same argument at a lower resolution. Test it by asking what the original would deny: if the summary could be written from the title alone, it is a paraphrase of the topic, not of the argument.", "خلاصه متن کوتاه‌تر نیست؛ همان استدلال با تفکیک کمتر است. آن را با این پرسش بیازما که اصل چه چیزی را انکار می‌کرد: اگر خلاصه را می‌شد از تیتر نوشت، بازگویی موضوع است، نه استدلال."),
                ("Keep three things and cut the rest: the claim, the strongest support, and the limitation the author accepts. Cut examples, repetitions, rhetorical questions and the writer's asides. A summary that keeps the examples and drops the limitation has inverted the original's priorities.", "سه چیز را نگه دار و بقیه را ببر: ادعا، قوی‌ترین پشتوانه و محدودیتی که نویسنده می‌پذیرد. مثال‌ها، تکرارها، پرسش‌های بلاغی و حاشیه‌روی‌ها را حذف کن. خلاصه‌ای که مثال‌ها را نگه دارد و محدودیت را بیندازد، اولویت‌های اصل را وارونه کرده است."),
                ("Attribute and hedge in the reporting verb. 'The author argues', 'the report concedes', 'the study suggests' — the verb is where the summary shows it has understood the epistemic status. And never adopt the source's claim as your own without a marker: 'according to', 'the report claims', 'it is argued that'.", "نقل و احتیاط را در فعل نقل بگذار. «The author argues»، «the report concedes»، «the study suggests» — فعل همان‌جایی است که خلاصه درک وضعیت معرفتی را نشان می‌دهد. و هرگز ادعای منبع را بی‌نشانه از خود نکن: «according to»، «the report claims»، «it is argued that»."),
                ("Length discipline: 120 words is about four sentences of C1 density. Plan them before writing — claim, support, limitation, evaluation — because compressing after drafting produces sentences that carry three ideas and communicate none.", "نظم طول: ۱۲۰ واژه حدود چهار جمله با چگالی C1 است. پیش از نوشتن نقشه‌شان را بکش — ادعا، پشتوانه، محدودیت، ارزیابی — چون فشرده‌سازی پس از نوشتن جمله‌هایی می‌سازد که سه ایده حمل می‌کنند و هیچ نمی‌رسانند."),
            ],
            [
                ("The report argues that the scheme paid for itself, though it concedes the sample was one region.", "گزارش استدلال می‌کند طرح هزینه‌اش را درآورد، هرچند می‌پذیرد نمونه یک منطقه بود."),
                ("According to the study, the effect was modest and short-lived.", "به گفتهٔ مطالعه، اثر کوچک و کوتاه‌مدت بود."),
                ("The author's central claim is narrower than the headline suggests.", "ادعای اصلی نویسنده از تیتر باریک‌تر است."),
            ],
            [
                mcq("What must a summary preserve above all?", "خلاصه بیش از همه چه چیزی را باید حفظ کند؟", ["the examples", "the claim and its limitation", "the writer's style", "the length"], 1,
                    "Claim plus caveat is the argument's shape.", "ادعا به‌همراه احتیاط، شکل استدلال است."),
                mcq("Which reporting verb signals the author's own doubt?", "کدام فعل نقل شک خود نویسنده را نشان می‌دهد؟", ["proves", "demonstrates", "concedes", "establishes"], 2,
                    "Concede marks a point granted against interest.", "concede نکته‌ای را می‌پذیرد که به زیان خودش است."),
            ],
            [
                write("Summarize in about 120 words the argument that case studies persuade more than they prove. Keep its claim, its strongest support and the limitation it accepts, and attribute the position to its author.",
                       "استدلالی را که می‌گوید مطالعات موردی بیشتر متقاعد می‌کنند تا اثبات، در حدود ۱۲۰ واژه خلاصه کن. ادعا، قوی‌ترین پشتوانه و محدودیتی که می‌پذیرد را نگه دار و موضع را به نویسنده‌اش نسبت بده.",
                       120, ["argues", "although"],
                       "Four sentences: claim, support, limitation, evaluation. Cut every example.",
                       "چهار جمله: ادعا، پشتوانه، محدودیت، ارزیابی. همهٔ مثال‌ها را حذف کن."),
                gap("___ to the report, the savings were overstated.", ["According"], "Attribution: according to.", "نقل: according to."),
                mcq("A summary that could be written from the title alone is ___.", "خلاصه‌ای که می‌شد از تیتر نوشت ___ است.", ["accurate", "a paraphrase of the topic, not the argument", "too long", "well attributed"], 1,
                    "It has not engaged with the reasoning.", "با استدلال درگیر نشده است."),
            ],
        ),
    ],
)

U4 = unit(
    "c1-u4",
    ("Leaving words out", "حذف واژه‌ها"),
    ("Use ellipsis and substitution so speech stays quick, and follow a debate that changes its ground.", "از حذف و جانشینی استفاده کن تا گفتار سریع بماند و مناظره‌ای را که زمینش را عوض می‌کند دنبال کن."),
    [
        lesson(
            "c1-u4-l1",
            "grammar",
            ("Ellipsis and substitution", "حذف و جانشینی"),
            ("Drop what is recoverable and replace what would repeat, without losing the thread.", "آنچه بازیافتنی است را بینداز و آنچه تکرار می‌شد را جانشین کن، بی‌آنکه رشته از دست برود."),
            [
                ("Ellipsis omits words the listener can reconstruct: 'Would you like to come?' — 'I'd love to' (come). At the end of a clause the auxiliary can stand alone: 'She's applied.' — 'Has she?' — 'She has.' The rule is recoverability, not brevity.", "حذف واژه‌هایی را می‌اندازد که شنونده بازسازی می‌کند: «Would you like to come?» — «I'd love to» (come). در پایان بند فعل کمکی تنها می‌تواند بایستد: «She's applied.» — «Has she?» — «She has.» قاعده بازیافت‌پذیری است، نه کوتاهی."),
                ("Substitution replaces rather than deletes: one/ones for nouns (the red one), do so / do that for predicates (she asked me to wait and I did so), so and not for whole clauses (I think so, I hope not, I'm afraid not). 'So' after think, expect, hope, suppose, believe is the most frequent substitution in English conversation.", "جانشینی جایگزین می‌کند نه حذف: one/ones برای اسم (the red one)، do so / do that برای محمول (she asked me to wait and I did so)، so و not برای کل بند (I think so، I hope not، I'm afraid not). «so» پس از think، expect، hope، suppose، believe رایج‌ترین جانشینی در گفت‌وگوی انگلیسی است."),
                ("Ellipsis in coordinated clauses follows the same subject: 'She wrote the report and sent it' (she sent). When the subject changes, the second verb needs its own subject — dropping it produces the classic 'walking down the road, the church came into view' error in a different guise.", "حذف در بندهای هم‌پایه با نهاد یکسان است: «She wrote the report and sent it» (she sent). وقتی نهاد عوض می‌شود، فعل دوم نهاد خودش را لازم دارد؛ انداختنش همان خطای «walking down the road, the church came into view» را در لباس دیگر می‌سازد."),
                ("Register: ellipsis is normal in speech and informal writing and rare in formal prose, where the full form is preferred for clarity. A report that says 'the figures suggest so' is not wrong, but 'the figures suggest that this is the case' is what the reader expects; the elliptical form sounds like the writer is in a hurry.", "لحن: حذف در گفتار و نوشتار غیررسمی طبیعی است و در نوشتار رسمی کم، چون شکل کامل برای وضوح ترجیح می‌شود. گزارشی که بگوید «the figures suggest so» غلط نیست، اما خواننده «the figures suggest that this is the case» را انتظار دارد؛ شکل محذوف حس شتاب به خواننده می‌دهد."),
            ],
            [
                ("I asked her to check the dates and she did so.", "از او خواستم تاریخ‌ها را بررسی کند و همین کار را کرد."),
                ("'Will they come?' 'I hope so.'", "«می‌آیند؟» «امیدوارم.»"),
                ("'The blue folder or the red one?' 'The red one.'", "«پوشهٔ آبی یا قرمز؟» «قرمزه.»"),
                ("She hasn't finished, and I'm afraid she won't.", "تمام نکرده و می‌ترسم نکند."),
            ],
            [
                mcq("'I think so' substitutes for ___.", "«I think so» جانشین ___ است.", ["a noun", "a whole clause", "an adjective", "a verb phrase only"], 1,
                    "So stands for the proposition, not a word.", "so جانشین گزاره است، نه یک واژه."),
                mcq("Which is ellipsis, not substitution?", "کدام حذف است، نه جانشینی؟", ["the red one", "I hope so", "I'd love to", "she did so"], 2,
                    "The verb is omitted and recovered from context.", "فعل حذف شده و از بافت بازسازی می‌شود."),
            ],
            [
                gap("'Are you coming?' 'I'm afraid ___ .' (negative substitute)", ["not"], "So and not substitute for clauses.", "so و not جانشین بند می‌شوند."),
                gap("He asked me to wait, and I ___ so.", ["did"], "Do so substitutes for the predicate.", "do so جانشین محمول است."),
                mcq("Which sentence is ungrammatical?", "کدام جمله نادرست است؟", ["She applied and was accepted.", "She applied and he was accepted.", "She applied and accepted.", "She applied, and she was accepted."], 2,
                    "'Accepted' has no object and implies she accepted something else.", "«accepted» مفعول ندارد و معنای دیگری می‌سازد."),
                mcq("Where is ellipsis least appropriate?", "حذف کجا کم‌ترین تناسب را دارد؟", ["in a chat message", "in a formal report", "in dialogue", "in a note to a colleague"], 1,
                    "Formal prose prefers the full form.", "نوشتار رسمی شکل کامل را ترجیح می‌دهد."),
            ],
        ),
        lesson(
            "c1-u4-l2",
            "vocabulary",
            ("Media, public discourse and the vocabulary of doubt", "رسانه، گفتمان عمومی و واژگان تردید"),
            ("Describe how a claim travels, and name the techniques that make it travel.", "توصیف کن ادعا چگونه سفر می‌کند و فن‌هایی را که سفرش را آسان می‌کنند نام ببر."),
            [
                ("Media vocabulary: a headline, a soundbite, a framing, an angle, a source, a leak, an embargo, a retraction, a correction, a fact-check, a rebuttal, a talking point, an echo chamber, a narrative. 'Framing' is which facts are foregrounded, not which facts are false.", "واژگان رسانه: headline، soundbite، framing، angle، source، leak، embargo، retraction، correction، fact-check، rebuttal، talking point، echo chamber، narrative. «framing» یعنی کدام واقعیت‌ها پیش‌آورده می‌شوند، نه کدام‌ها دروغ‌اند."),
                ("Rhetoric vocabulary: to appeal to authority, to appeal to emotion, to straw-man an opponent, to beg the question, to move the goalposts, whataboutism, a loaded term, a false equivalence. These name moves rather than people, which is what makes them usable in argument.", "واژگان بلاغت: appeal to authority، appeal to emotion، straw-man an opponent، beg the question، move the goalposts، whataboutism، loaded term، false equivalence. این‌ها حرکت‌ها را نام می‌برند نه آدم‌ها و همین قابل استفاده‌شان می‌کند."),
                ("Doubt vocabulary with graduated force: to question, to cast doubt on, to challenge, to dispute, to contest, to refute, to debunk. 'Debunk' claims the thing was false; 'question' claims only that it is not settled. Using debunk for a claim you merely doubt is the most common overreach in commentary.", "واژگان تردید با نیروی درجه‌بندی‌شده: question، cast doubt on، challenge، dispute، contest، refute، debunk. «debunk» می‌گوید چیز دروغ بود و «question» فقط می‌گوید حل نشده است. استفاده از debunk برای ادعایی که فقط مشکوکی، رایج‌ترین زیاده‌روی در تحلیل است."),
                ("Fixed chunks worth having ready: at face value, on the record, off the record, to bury the lede, to set the record straight, to go viral, to gain traction, to lose credibility, a grain of truth. Each replaces a sentence of explanation.", "ترکیب‌های ثابت آماده: at face value، on the record، off the record، bury the lede، set the record straight، go viral، gain traction، lose credibility، a grain of truth. هر کدام جای یک جمله توضیح را می‌گیرند."),
            ],
            [
                ("The correction ran three weeks after the original claim.", "اصلاحیه سه هفته پس از ادعای اولیه منتشر شد."),
                ("The framing was accurate and the emphasis was not.", "چارچوب‌بندی درست بود و تأکید نه."),
                ("That argument begs the question it claims to answer.", "آن استدلال همان پرسشی را مفروض می‌گیرد که ادعا می‌کند پاسخش می‌دهد."),
                ("The claim gained traction before anyone checked it.", "ادعا پیش از آنکه کسی بررسی‌اش کند، جا افتاد."),
            ],
            [
                mcq("'Framing' concerns ___.", "«Framing» مربوط است به ___.", ["whether facts are true", "which facts are foregrounded", "who wrote the article", "the length of the piece"], 1,
                    "Selection and emphasis, not truth value.", "گزینش و تأکید، نه ارزش صدق."),
                mcq("Which is the strongest verb?", "کدام فعل قوی‌ترین است؟", ["question", "debunk", "challenge", "dispute"], 1,
                    "Debunk asserts the claim was false.", "debunk ادعای دروغ بودن را مطرح می‌کند."),
            ],
            [
                gap("The story first gained ___ on a small forum.", ["traction"], "Gain traction = begin to spread.", "gain traction یعنی شروع به گسترش."),
                gap("To ___ the record straight, the figure was 12%, not 21%.", ["set"], "Fixed phrase.", "عبارت ثابت."),
                mcq("A 'false equivalence' is ___.", "«false equivalence» ___ است.", ["a comparison that hides a relevant difference", "an outright lie", "a correction", "a quotation"], 0,
                    "Two things treated as alike that are not.", "دو چیز که همانند فرض شده‌اند و نیستند."),
                mcq("'Whataboutism' answers a criticism by ___.", "«Whataboutism» به نقد پاسخ می‌دهد با ___.", ["conceding it", "raising another criticism", "providing evidence", "apologizing"], 1,
                    "It deflects rather than replies.", "منحرف می‌کند، پاسخ نمی‌دهد."),
            ],
        ),
        lesson(
            "c1-u4-l3",
            "listening",
            ("The debate: when the ground moves", "مناظره: وقتی زمین عوض می‌شود"),
            ("Follow a two-speaker argument, notice a shift of ground, and hear the concession.", "استدلال دو گوینده را دنبال کن، تغییر زمین را ببین و امتیاز را بشنو."),
            [
                ("In a debate, the most important moment is usually the one where a speaker stops answering the question that was asked. Listen for the pivot: 'the real issue is…', 'that's not what's at stake', 'you're comparing two different things'. A pivot is not automatically a fallacy, but it is always a change of subject that needs checking.", "در مناظره مهم‌ترین لحظه معمولاً همان است که گوینده پاسخ پرسش پرسیده‌شده را رها می‌کند. به محور گوش کن: «the real issue is…»، «that's not what's at stake»، «you're comparing two different things». محور همیشه مغالطه نیست، اما همیشه تغییر موضوع است و باید بررسی شود."),
                ("Concessions are quiet in speech: a short 'fair enough', a 'I'd accept that', a rise in pitch on 'true'. A listener who only tracks the main verbs misses them, and then reports a debate as more hostile than it was.", "امتیازها در گفتار آهسته‌اند: یک «fair enough» کوتاه، یک «I'd accept that»، بالا رفتن لحن روی «true». شنونده‌ای که فقط فعل‌های اصلی را دنبال کند آن‌ها را از دست می‌دهد و بعد مناظره را خصمانه‌تر از آنچه بود گزارش می‌کند."),
                ("Turn-taking signals carry the argument's shape: 'if I could finish', 'let me come back to that', 'go on', 'no, you had your turn'. Interruptions cluster where the disagreement is sharpest, which is a useful map of the actual dispute.", "نشانه‌های نوبت‌گیری شکل استدلال را حمل می‌کنند: «if I could finish»، «let me come back to that»، «go on»، «no, you had your turn». میان‌حرف‌ها جایی جمع می‌شوند که اختلاف تیزتر است و این نقشهٔ خوبی از نزاع واقعی است."),
                ("Numbers in speech are round and repeated: 'about a third', 'roughly forty percent'. When a speaker repeats a figure with more precision the second time, they are usually being challenged; when they round it further, they are usually conceding uncertainty. Both are information.", "عددها در گفتار گرد و تکرارشده‌اند: «about a third»، «roughly forty percent». وقتی گوینده عدد را بار دوم دقیق‌تر تکرار می‌کند، معمولاً به چالش کشیده شده و وقتی بیشتر گردش می‌کند، معمولاً عدم قطعیت را می‌پذیرد. هر دو اطلاعات‌اند."),
            ],
            [
                ("With respect, that's not what's at stake here.", "با احترام، مسئله اینجا آن نیست."),
                ("Fair enough — I'd accept the cost point.", "قبول — نکتهٔ هزینه را می‌پذیرم."),
                ("If I could finish the point before you answer it.", "اگر بگذارید نکته را تمام کنم پیش از پاسخ."),
                ("So we agree on the diagnosis and disagree on the remedy.", "پس در تشخیص موافقیم و در درمان مخالف."),
            ],
            [
                mcq("What does a pivot in a debate indicate?", "محور در مناظره چه را نشان می‌دهد؟", ["agreement", "a change of subject", "the end of the debate", "a new speaker"], 1,
                    "The speaker has moved to a different question.", "گوینده به پرسشی دیگر رفته است."),
                mcq("Why are quiet concessions easy to miss?", "چرا امتیازهای آهسته آسان از دست می‌روند؟", ["they are said quickly and low", "they use rare words", "they come first", "they are written down"], 0,
                    "They are short and unstressed.", "کوتاه و بی‌تکیه‌اند."),
            ],
            [
                listen("Look, I'd accept that the sample was small. But the direction of the effect was the same in all four regions, and that's not something a small sample invents.",
                       "What does the speaker concede, and what do they defend?", "گوینده چه را می‌پذیرد و از چه دفاع می‌کند؟", ["size of the sample; consistency of the effect", "the conclusion; the method", "nothing; everything", "the regions; the sample"], 0,
                       "The sample is granted; the consistency is the defense.", "نمونه پذیرفته می‌شود و سازگاری دفاع است."),
                gap("So we agree on the diagnosis and ___ on the remedy.", ["disagree"], "The pair is agree / disagree.", "جفت agree / disagree است."),
            ],
            dialogue=dialogue([
                    ("Host", "You've argued the scheme failed. But waiting times fell by a third.", "شما گفتید طرح شکست خورد. اما زمان انتظار یک‌سوم کم شد."),
                    ("Guest", "They did, and I'd accept that. My point is that the fall began before the scheme, and the real issue is what happened after month four.", "همین‌طور است و می‌پذیرم. نکتهٔ من این است که کاهش پیش از طرح شروع شد و مسئلهٔ اصلی آن است که بعد از ماه چهارم رخ داد."),
                    ("Host", "So you're saying the timing is the problem, not the policy.", "پس می‌گویید مشکل زمان‌بندی است، نه سیاست."),
                    ("Guest", "Exactly — and that's a different claim from the one I was answering.", "دقیقاً — و این ادعایی متفاوت از آن است که پاسخش را می‌دادم."),
                ]),
        ),
    ],
)
