#!/usr/bin/env python3
"""C2, units 1 and 2: information order, and how certain a claim can be."""

from course_kit import dialogue, gap, lesson, listen, mcq, passage, say, unit, write

U1 = unit(
    "c2-u1",
    ("The weight of the end", "وزنِ پایان"),
    ("Put new and heavy information where the reader can hold it, and let the "
     "opening carry what is already known.",
     "اطلاعات تازه و سنگین را جایی بگذار که خواننده بتواند نگهش دارد و آغاز را "
     "به آنچه از پیش معلوم است بسپار."),
    [
        lesson(
            "c2-u1-l1", "grammar",
            ("End weight: why the long part goes last",
             "وزن پایان: چرا بخش بلند آخر می‌آید"),
            ("Move a heavy subject or object to the end so the sentence opens "
             "lightly and closes on the news.",
             "نهاد یا مفعول سنگین را به پایان ببر تا جمله سبک آغاز شود و با "
             "خبر بسته شود."),
            [
                ("English puts the longest, newest, most complicated part of a "
                 "sentence at the end. The reason is mechanical: a reader "
                 "holding an unfinished clause has to keep it in mind, and the "
                 "heavier the clause, the more it costs. 'That the plan had "
                 "been rejected by every department surprised nobody' makes the "
                 "reader carry ten words before the verb arrives.",
                 "انگلیسی بلندترین و تازه‌ترین و پیچیده‌ترین بخش جمله را در پایان "
                 "می‌گذارد. دلیلش مکانیکی است: خواننده‌ای که بندی ناتمام را در "
                 "دست دارد باید آن را در ذهن نگه دارد و هرچه بند سنگین‌تر باشد "
                 "هزینه بیشتر است. «That the plan had been rejected by every "
                 "department surprised nobody» خواننده را وادار می‌کند ده واژه "
                 "را پیش از رسیدن فعل حمل کند."),
                ("The cure is the it-cleft or the extraposed subject: 'It "
                 "surprised nobody that the plan had been rejected by every "
                 "department.' It is not a decoration. The same information, "
                 "the same truth value, and one of them is readable aloud.",
                 "درمانش cleft با it یا نهادِ جابه‌جاشده است: «It surprised "
                 "nobody that the plan had been rejected by every department.» "
                 "این آرایش تزیین نیست؛ همان اطلاعات و همان ارزش صدق است و یکی "
                 "از آن دو بلندخواندنی است."),
                ("The rule has a second half. What the reader already knows "
                 "belongs at the front, because old information is cheap to "
                 "hold. 'The plan had been rejected by every department. That "
                 "it surprised nobody says more about the departments than "
                 "about the plan' — the second sentence opens on the known and "
                 "ends on the judgement.",
                 "قاعده نیمهٔ دومی هم دارد. آنچه خواننده از پیش می‌داند به آغاز "
                 "تعلق دارد، چون اطلاعات کهنه ارزان نگه داشته می‌شود. «The "
                 "plan had been rejected by every department. That it "
                 "surprised nobody says more about the departments than about "
                 "the plan» — جملهٔ دوم با معلوم آغاز و با داوری تمام می‌شود."),
            ],
            [
                ("It became clear only later that the figures had been "
                 "estimated, not counted.", "تنها بعدها روشن شد که ارقام تخمین "
                 "زده شده بودند، نه شمرده."),
                ("The committee rejected the proposal for reasons it never "
                 "published.", "کمیته پیشنهاد را به دلایلی رد کرد که هرگز "
                 "منتشر نکرد."),
                ("What the report does not say is more interesting than what "
                 "it does.", "آنچه گزارش نمی‌گوید از آنچه می‌گوید جالب‌تر است."),
                ("There is a version of this argument that survives the data, "
                 "and a version that does not.", "از این استدلال نسخه‌ای هست "
                 "که از داده جان سالم به در می‌برد و نسخه‌ای که نه."),
            ],
            [
                mcq("Which sentence opens most lightly?", "کدام جمله سبک‌تر آغاز "
                    "می‌شود؟",
                    ["That the minister had known for months angered the "
                     "committee.",
                     "It angered the committee that the minister had known for "
                     "months.",
                     "The committee angered that the minister had known for "
                     "months.",
                     "The minister, for months, the committee angered."],
                    1,
                    "The extraposed 'it' holds the place while the heavy "
                    "clause waits at the end.",
                    "«it» جابه‌جاشده جا را نگه می‌دارد تا بند سنگین در پایان "
                    "بماند."),
                mcq("A paragraph's first sentence normally carries ___.",
                    "جملهٔ اول یک بند معمولاً ___ را حمل می‌کند.",
                    ["the newest information", "what the reader already knows",
                     "the writer's conclusion", "the longest clause"],
                    1,
                    "Given-new ordering: known material opens, new material "
                    "closes.",
                    "ترتیب معلوم‌تازه: مطالب معلوم آغاز و مطالب تازه پایان."),
            ],
            [
                mcq("Choose the ordering that keeps the news for the end.",
                    "ترتیبی را انتخاب کن که خبر را برای پایان نگه دارد.",
                    ["That nobody had checked the figures emerged at the "
                     "hearing.",
                     "It emerged at the hearing that nobody had checked the "
                     "figures.",
                     "The hearing emerged that nobody had checked the figures.",
                     "Nobody, at the hearing, the figures had not checked."],
                    1,
                    "The heavy clause sits at the end where it can be read.",
                    "بند سنگین در پایان می‌نشیند تا خوانده شود."),
                gap("It was only after the second review ___ anyone asked what "
                    "the trial had cost.",
                    ["that"], "A cleft with 'it was ... that' puts the "
                    "circumstance first and the news last.",
                    "cleft با «it was ... that» وضعیت را اول و خبر را آخر "
                    "می‌آورد.", "one word"),
                mcq("Which sentence buries its subject and reads worst?",
                    "کدام جمله نهادش را دفن می‌کند و بدترین خوانش را دارد؟",
                    ["The fact that the accounts had been signed off by "
                     "someone who had left the company troubled the auditors.",
                     "It troubled the auditors that someone who had left the "
                     "company had signed off the accounts.",
                     "The auditors were troubled by who had signed off the "
                     "accounts.",
                     "Someone had signed off the accounts after leaving the "
                     "company."],
                    0,
                    "Twenty words before the verb 'troubled' is the cost the "
                    "rule exists to avoid.",
                    "بیست واژه پیش از فعل «troubled» همان هزینه‌ای است که قاعده "
                    "برای پرهیز از آن هست."),
                gap("The proposal was rejected. ___ it was rejected for "
                    "reasons nobody published is the part that matters.",
                    ["That"], "Old information first, then the new judgement.",
                    "معلوم در آغاز و داوری تازه پس از آن.", "one word"),
            ],
        ),
        lesson(
            "c2-u1-l2", "vocabulary",
            ("Precision: estimate, assess, evaluate, appraise",
             "دقت: estimate، assess، evaluate، appraise"),
            ("Choose between near-synonyms by what they claim about the "
             "speaker's knowledge, not by their dictionary gloss.",
             "میان هم‌معناهای نزدیک بر پایهٔ آنچه دربارهٔ دانش گوینده ادعا "
             "می‌کنند انتخاب کن، نه بر پایهٔ ترجمهٔ فرهنگ‌نامه."),
            [
                ("These four verbs all touch 'judging worth or size', and they "
                 "are not interchangeable. To estimate is to put a number on "
                 "something without counting it: we estimate the cost at two "
                 "million. To assess is to judge against a standard: the "
                 "damage was assessed by an engineer. To evaluate is to judge "
                 "a process or a proposal, usually to decide what to do next. "
                 "To appraise is the formal, often financial, member of the "
                 "family: the painting was appraised at a higher figure than "
                 "anyone expected.",
                 "این چهار فعل همه به «سنجش ارزش یا اندازه» مربوط‌اند و "
                 "جای‌گزین‌پذیر نیستند. estimate یعنی بی‌شمردن عدد گذاشتن: we "
                 "estimate the cost at two million. assess یعنی سنجش با یک "
                 "معیار: the damage was assessed by an engineer. evaluate یعنی "
                 "سنجش یک فرایند یا پیشنهاد، معمولاً برای تصمیم بعدی. appraise "
                 "عضو رسمی و اغلب مالی این خانواده است: the painting was "
                 "appraised at a higher figure than anyone expected."),
                ("The choice carries an epistemic claim. 'We estimate' says "
                 "the number is a guess with a method behind it. 'We assess' "
                 "says somebody qualified looked. 'We have evaluated' says "
                 "there was a process and a decision at the end of it. A "
                 "writer who uses the wrong one either oversells a guess or "
                 "undersells a finding.",
                 "انتخاب، ادعایی شناختی حمل می‌کند. «We estimate» می‌گوید عدد "
                 "حدسی است که روشی پشتش دارد. «We assess» می‌گوید فرد "
                 "صلاحیت‌دار نگاه کرده. «We have evaluated» می‌گوید فرایندی بود "
                 "و تصمیمی در پایانش. نویسنده‌ای که واژهٔ نادرست را به کار ببرد "
                 "یا حدسی را بیش از اندازه می‌فروشد یا یافته‌ای را کم."),
                ("The same discipline applies across the abstract nouns: an "
                 "estimate is a figure, an assessment is a judgement, an "
                 "evaluation is a judgement with a purpose, an appraisal is a "
                 "valuation. Collocations keep them apart: a rough estimate, a "
                 "risk assessment, a performance evaluation, an insurance "
                 "appraisal.",
                 "همین انضباط در اسم‌های انتزاعی هم هست: estimate رقم است، "
                 "assessment داوری، evaluation داوری با هدف، appraisal "
                 "ارزش‌گذاری. همنشینی‌ها آن‌ها را جدا نگه می‌دارند: a rough "
                 "estimate، a risk assessment، a performance evaluation، an "
                 "insurance appraisal."),
            ],
            [
                ("Engineers assessed the bridge as safe for another decade.",
                 "مهندسان پل را برای یک دههٔ دیگر ایمن سنجیدند."),
                ("We estimate that a third of the letters were never opened.",
                 "تخمین می‌زنیم یک‌سوم نامه‌ها هرگز باز نشده باشند."),
                ("The board will evaluate the scheme in the spring.",
                 "هیئت‌مدیره طرح را در بهار ارزیابی خواهد کرد."),
                ("The house was appraised at well below its asking price.",
                 "خانه بسیار پایین‌تر از قیمت پیشنهادی‌اش ارزش‌گذاری شد."),
            ],
            [
                mcq("A number produced without counting the items is ___.",
                    "عددی که بدون شمردن اقلام به دست آمده ___ است.",
                    ["an assessment", "an estimate", "an appraisal",
                     "an evaluation"], 1,
                    "Estimate is the guess-with-a-method member of the set.",
                    "estimate عضو حدس‌با‌روش این مجموعه است."),
                mcq("An insurer deciding what a damaged car is worth is ___ it.",
                    "بیمه‌گری که تعیین می‌کند خودروی آسیب‌دیده چقدر می‌ارزد "
                    "در حال ___ آن است.",
                    ["assessing", "appraising", "estimating", "auditing"], 1,
                    "Valuation for money is appraisal.",
                    "ارزش‌گذاری مالی appraisal است."),
            ],
            [
                mcq("The panel spent three days ___ whether the policy had "
                    "worked.", "هیئت سه روز صرف ___ کرد که آیا سیاست کار کرده "
                    "است.",
                    ["appraising", "evaluating", "estimating", "pricing"], 1,
                    "Judging a policy's effect, with a decision to follow, is "
                    "evaluation.", "سنجش اثر یک سیاست با تصمیمی در پی آن، "
                    "evaluation است."),
                gap("We cannot count the crowd, so any figure here is an "
                     "___.",
                     ["estimate"], "The absence of a count is what makes it an "
                     "estimate.", "نبودِ شمارش همان چیزی است که آن را estimate "
                     "می‌کند.", "one word"),
                mcq("Which pairing is wrong?", "کدام جفت نادرست است؟",
                    ["risk assessment", "rough estimate",
                     "insurance appraisal", "performance estimate"], 3,
                    "The fixed phrase is 'performance evaluation'.",
                    "عبارت ثابت «performance evaluation» است."),
                gap("Before the sale, an independent surveyor ___ the property.",
                     ["appraised"], "A professional valuation before sale.",
                     "ارزش‌گذاری حرفه‌ای پیش از فروش.", "one word, past tense"),
            ],
        ),
        lesson(
            "c2-u1-l3", "reading",
            ("The house that kept its own hours",
             "خانه‌ای که ساعت خودش را داشت"),
            ("Read for what the narrator refuses to say, and for the detail "
             "that contradicts the surface.",
             "برای آنچه راوی از گفتنش سر باز می‌زند بخوان و برای جزئیاتی که "
             "ظاهر را نقض می‌کند."),
            [
                ("A literary passage rarely states its judgement. It arranges "
                 "detail so that the reader arrives at the judgement alone, and "
                 "the questions that follow usually ask about that arrangement "
                 "rather than about the plot.",
                 "متن ادبی به‌ندرت داوری‌اش را بیان می‌کند. جزئیات را چنان "
                 "می‌چیند که خواننده خودش به داوری برسد و پرسش‌های پس از آن "
                 "معمولاً دربارهٔ همین چیدمان است، نه دربارهٔ خط داستان."),
                ("Watch for the detail that will not fit. A narrator who says "
                 "the house was happy and then mentions the stopped clocks is "
                 "telling you two things at once, and only one of them is "
                 "spoken.",
                 "مراقب جزئیاتی باش که جا نمی‌شود. راویی که می‌گوید خانه خوش بود "
                 "و بعد از ساعت‌های ایستاده حرف می‌زند دو چیز را هم‌زمان می‌گوید "
                 "و تنها یکی از آن‌ها گفته شده است."),
            ],
            [
                ("Read the passage once for the story, then again for what "
                 "the narrator notices.", "متن را یک بار برای داستان بخوان و "
                 "بار دوم برای آنچه راوی متوجهش می‌شود."),
                ("When a question asks about tone, the answer is usually a "
                 "verb of attitude, not an adjective of mood.",
                 "وقتی پرسشی دربارهٔ لحن است، پاسخ معمولاً فعلی از نگرش است، نه "
                 "صفتی از حال‌وهوا."),
                ("An answer that is true but irrelevant is still wrong: the "
                 "passage must support it.", "پاسخی که درست اما بی‌ربط است باز "
                 "هم نادرست است: متن باید پشتیبانش باشد."),
            ],
            [
                mcq("Why does the narrator mention the stopped clocks?",
                    "چرا راوی ساعت‌های ایستاده را ذکر می‌کند؟",
                    ["to date the story", "to contradict the claim that the "
                     "house was happy", "to explain the silence",
                     "to introduce a character"], 1,
                    "A detail that clashes with the stated mood is the "
                    "passage's argument made silently.",
                    "جزئیاتی که با حال‌وهوای گفته‌شده ناسازگار است، استدلال متن "
                    "است که بی‌صدا بیان می‌شود."),
                mcq("The narrator's tone is best called ___.", "لحن راوی بهتر "
                    "است ___ خوانده شود.",
                    ["nostalgic", "guarded", "cheerful", "angry"], 1,
                    "Praise followed by contradiction is guarded, not "
                    "nostalgic.", "تعریف و سپس تناقض، محتاطانه است نه نوستالژیک."),
            ],
            [
                mcq("What does the last sentence suggest?", "جملهٔ آخر چه را "
                    "می‌رساند؟",
                    ["the family will return", "the house outlasted its "
                     "purpose", "the clocks were repaired",
                     "the narrator was a child"], 1,
                    "The house is intact and nothing is left for it to do.",
                    "خانه دست‌نخورده است و کاری نمانده که انجام دهد."),
                mcq("Which claim about the visitors is supported?",
                    "کدام ادعا دربارهٔ بازدیدکنندگان پشتیبانی می‌شود؟",
                    ["they admired the furniture", "they asked about the "
                     "garden", "they left quickly", "they took photographs"],
                    1,
                    "Only the garden question is stated; the others are "
                    "plausible inventions.", "تنها پرسش باغ گفته شده است و "
                    "بقیه اختراع‌های باورپذیرند."),
                mcq("Why does the surveyor's report matter to the narrator?",
                    "چرا گزارش ارزیاب برای راوی مهم است؟",
                    ["it values the house highly", "it records only what can "
                     "be repaired", "it proves the house is unsafe",
                     "it mentions the clocks"], 1,
                    "The surveyor's silence about the clocks is what tells the "
                    "narrator they belong to the past.",
                    "سکوت ارزیاب دربارهٔ ساعت‌هاست که به راوی می‌گوید آن‌ها به "
                    "گذشته تعلق دارند."),
            ],
            passage=passage(
                ("The house that kept its own hours",
                 "خانه‌ای که ساعت خودش را داشت"),
                ("The house was happy, my mother said, and she said it the way "
                 "people say a thing they have decided to keep saying. The "
                 "clocks in the hall had stopped in the spring, all four of "
                 "them, and nobody wound them again. We ate at the hours the "
                 "light allowed.\n\n"
                 "Visitors came that summer and asked about the garden, which "
                 "had been let go, and about the well, which had been covered "
                 "in 1974. They did not ask about the clocks. My father would "
                 "stand in the doorway while they talked, as if the doorway "
                 "were a job he had been given.\n\n"
                 "In October the surveyor came with a folder and walked the "
                 "rooms twice. He said the walls were sound. He said the roof "
                 "would need doing. He wrote nothing about the clocks, and I "
                 "understood that they were not the kind of thing a surveyor "
                 "records. The house was sound and the roof would need doing "
                 "and there was nothing left in it that anybody wanted. My "
                 "mother still called it happy. The clocks were right twice a "
                 "day, which is more than most of us manage.",
                 "خانه خوش بود، مادرم می‌گفت، و آن را طوری می‌گفت که آدم‌ها "
                 "چیزی را می‌گویند که تصمیم گرفته‌اند همچنان بگویند. ساعت‌های "
                 "راهرو در بهار ایستاده بودند، هر چهارتا، و کسی دیگر کوکشان "
                 "نکرد. ما به ساعت‌هایی می‌خوردیم که نور اجازه می‌داد.\n\n"
                 "آن تابستان مهمان‌ها آمدند و از باغ پرسیدند که رها شده بود و "
                 "از چاه که در ۱۹۷۴ پوشانده شده بود. از ساعت‌ها نپرسیدند. "
                 "پدرم وقتی حرف می‌زدند در چارچوب در می‌ایستاد، انگار چارچوب "
                 "در کاری باشد که به او سپرده شده.\n\n"
                 "در اکتبر ارزیاب با پوشه‌ای آمد و اتاق‌ها را دو بار گشت. "
                 "گفت دیوارها سالم‌اند. گفت سقف کار می‌خواهد. دربارهٔ ساعت‌ها "
                 "چیزی ننوشت و من فهمیدم آن‌ها از چیزهایی نیستند که ارزیاب "
                 "ثبت می‌کند. خانه سالم بود و سقف کار می‌خواست و چیزی در آن "
                 "نمانده بود که کسی بخواهد. مادرم هنوز خوشش می‌نامید. "
                 "ساعت‌ها روزی دو بار درست بودند، که بیشتر از کار بیشتر ماست."),
            ),
        ),
        lesson(
            "c2-u1-l4", "writing",
            ("The analysis that quotes and then argues",
             "تحلیلی که نقل می‌کند و سپس استدلال"),
            ("Write a critical analysis of a short passage: name the "
             "technique, quote it, and say what it does to the reader.",
             "تحلیل انتقادی یک متن کوتاه بنویس: شگرد را نام ببر، نقلش کن و "
             "بگو با خواننده چه می‌کند."),
            [
                ("A critical analysis is not a summary with opinions attached. "
                 "It makes a claim about how the text works, and every "
                 "paragraph offers a piece of the text as evidence for that "
                 "claim. The pattern is: technique, quotation, effect.",
                 "تحلیل انتقادی خلاصه‌ای با نظرهای چسبیده نیست. ادعایی دربارهٔ "
                 "نحوهٔ کار متن می‌سازد و هر بند بخشی از متن را شاهد آن ادعا "
                 "می‌آورد. الگو این است: شگرد، نقل، اثر."),
                ("The effect is where most analyses go vague. 'This creates a "
                 "melancholy tone' is not an effect; 'this makes the reader "
                 "notice the stopped clocks before the narrator does' is. Say "
                 "what the reader is made to do, not what mood they are "
                 "supposed to feel.",
                 "اثر جایی است که بیشتر تحلیل‌ها مبهم می‌شوند. «این لحنی غمگین "
                 "می‌سازد» اثر نیست؛ «این باعث می‌شود خواننده ساعت‌های ایستاده "
                 "را پیش از راوی ببیند» اثر است. بگو خواننده وادار به چه کاری "
                 "می‌شود، نه به چه حسی."),
            ],
            [
                ("Technique, quotation, effect — in that order, in every "
                 "paragraph.", "شگرد، نقل، اثر — با همین ترتیب در هر بند."),
                ("Quote the shortest phrase that carries the point, not the "
                 "longest.", "کوتاه‌ترین عبارتی را نقل کن که نکته را حمل می‌کند، "
                 "نه بلندترین."),
                ("One paragraph of counter-reading makes an analysis credible; "
                 "three make it indecisive.", "یک بند خوانش مخالف تحلیل را "
                 "باورپذیر می‌کند و سه بند آن را بی‌تصمیم."),
            ],
            [
                mcq("Which is an effect rather than a mood?", "کدام اثر است و "
                    "نه حال‌وهوا؟",
                    ["a sad atmosphere", "the reader suspects the mother "
                     "before the narrator does", "beautiful language",
                     "a nostalgic feeling"], 1,
                    "An effect names what the reader is led to do or notice.",
                    "اثر نام می‌برد که خواننده به چه کاری یا دیدن چه چیزی "
                    "راهنمایی می‌شود."),
                mcq("The quotation in a body paragraph should be ___.",
                    "نقل‌قول در بند بدنه باید ___ باشد.",
                    ["the longest available", "the shortest phrase carrying "
                     "the point", "the first sentence of the text",
                     "paraphrased, never quoted"], 1,
                    "Short quotations keep the argument in view.",
                    "نقل‌های کوتاه استدلال را در دید نگه می‌دارند."),
            ],
            [
                mcq("Which sentence makes a claim rather than a summary?",
                    "کدام جمله ادعا می‌کند و نه خلاصه؟",
                    ["The narrator describes a house and some visitors.",
                     "The stopped clocks do the work the narrator's words "
                     "refuse to do.",
                     "The passage is about a family in a house.",
                     "There are three paragraphs in the passage."], 1,
                    "Only one of them says how the text works.",
                    "تنها یکی از آن‌ها می‌گوید متن چگونه کار می‌کند."),
                gap("A body paragraph needs a technique, a quotation and an "
                     "___.",
                    ["effect"], "The third element is what the technique does "
                    "to the reader.", "عنصر سوم آن است که شگرد با خواننده چه "
                    "می‌کند.", "one word"),
                write("Write about 140 words analysing how a writer makes a "
                      "reader distrust a narrator. Name two techniques, quote "
                      "a short phrase for each, and say what each makes the "
                      "reader do.",
                      "حدود ۱۴۰ واژه تحلیل کن که نویسنده چگونه باعث می‌شود "
                      "خواننده به راوی بی‌اعتماد شود. دو شگرد را نام ببر، برای "
                      "هرکدام عبارتی کوتاه نقل کن و بگو هر یک خواننده را به چه "
                      "کاری وامی‌دارد.",
                      140, ["although", "whereas"],
                      "Technique, quotation, effect in each paragraph; no "
                      "summary of the plot; one counter-reading at the end.",
                      "در هر بند شگرد، نقل و اثر؛ بدون خلاصهٔ داستان؛ یک خوانش "
                      "مخالف در پایان."),
            ],
        ),
    ],
)

U2 = unit(
    "c2-u2",
    ("How certain can you be", "چقدر می‌توانی مطمئن باشی"),
    ("Calibrate a claim to the evidence behind it, and hear the difference "
     "between a finding and a guess.",
     "ادعا را با شاهدِ پشتش هم‌تراز کن و تفاوت یافته و حدس را بشنو."),
    [
        lesson(
            "c2-u2-l1", "grammar",
            ("Hedging: saying exactly how sure you are",
             "احتیاط: دقیقاً گفتنِ میزان اطمینان"),
            ("Use modals, adverbs and impersonal frames to place a claim "
             "somewhere between certain and possible.",
             "با وجه‌ها، قیدها و ساخت‌های بی‌شخص، ادعا را جایی میان قطعی و "
             "ممکن بنشان."),
            [
                ("Academic and professional English hedges because an "
                 "unhedged claim is a claim about everything. 'This causes "
                 "delay' says the effect is universal; 'this tends to cause "
                 "delay' says it happens often enough to plan for. The second "
                 "is not weaker writing. It is a more accurate description of "
                 "what was observed.",
                 "انگلیسی دانشگاهی و حرفه‌ای احتیاط می‌کند چون ادعای "
                 "بی‌احتیاط ادعایی دربارهٔ همه‌چیز است. «This causes delay» "
                 "می‌گوید اثر جهان‌شمول است؛ «this tends to cause delay» "
                 "می‌گوید آن‌قدر رخ می‌دهد که برایش برنامه ریخت. دومی نوشتهٔ "
                 "ضعیف‌تر نیست، توصیف دقیق‌تری از مشاهده است."),
                ("The scale runs from strong to weak: will, is certain to; "
                 "is likely to, should; may well, could; might, is possible "
                 "that; is unlikely to; is not expected to. Placement "
                 "matters as much as choice: 'This may well be the cause' "
                 "puts the doubt on 'may', where the reader expects it, while "
                 "'This is possibly the cause' quietly overstates by putting "
                 "the hedge in a noun.",
                 "طیف از قوی به ضعیف می‌رود: will، is certain to؛ is likely "
                 "to، should؛ may well، could؛ might، is possible that؛ is "
                 "unlikely to؛ is not expected to. جایگاه به‌اندازهٔ انتخاب "
                 "مهم است: «This may well be the cause» تردید را روی «may» "
                 "می‌گذارد، جایی که خواننده انتظارش را دارد، در حالی که "
                 "«This is possibly the cause» بی‌صدا اغراق می‌کند."),
                ("Impersonal frames move the doubt off the writer and onto the "
                 "evidence: the data suggest, the results would appear to "
                 "indicate, it is not clear that, there is little to support "
                 "the view that. Used once, they are precision. Used in every "
                 "sentence, they are evasion, and a reader notices which.",
                 "ساخت‌های بی‌شخص تردید را از نویسنده به شاهد منتقل می‌کنند: "
                 "the data suggest، the results would appear to indicate، it "
                 "is not clear that، there is little to support the view "
                 "that. یک بار که به کار روند دقت‌اند؛ در هر جمله که تکرار "
                 "شوند فرار از پاسخ‌اند و خواننده تفاوت را می‌بیند."),
            ],
            [
                ("The programme is likely to cost more than the estimate.",
                 "احتمالاً برنامه بیش از برآورد هزینه خواهد برداشت."),
                ("The results would appear to support the earlier study.",
                 "به نظر می‌رسد نتایج مطالعهٔ پیشین را تأیید می‌کنند."),
                ("There is little to suggest that the delay was deliberate.",
                 "شواهد کمی هست که تأخیر عمدی بوده باشد."),
                ("Fuel prices may well fall before the winter.",
                 "به‌احتمال زیاد قیمت سوخت پیش از زمستان پایین می‌آید."),
            ],
            [
                mcq("Which sentence claims the most?", "کدام جمله بیشترین ادعا "
                    "را دارد؟",
                    ["The policy reduced waiting times.",
                     "The policy may have reduced waiting times.",
                     "The policy appears to have reduced waiting times.",
                     "The policy is likely to reduce waiting times."], 0,
                    "No hedge at all: a flat claim of cause and effect.",
                    "بی‌هیچ احتیاطی: ادعای صریح علت و اثر."),
                mcq("'The data suggest' differs from 'the data show' because "
                    "___.", "«the data suggest» با «the data show» تفاوت دارد "
                    "چون ___.",
                    ["it is more formal", "it leaves the conclusion open",
                     "it is weaker grammar", "it means the data are wrong"], 1,
                    "Suggest points at a conclusion without asserting it.",
                    "suggest به نتیجه اشاره می‌کند بی‌آنکه آن را اثبات کند."),
            ],
            [
                mcq("A finding you would defend in a meeting is reported with "
                    "___.", "یافته‌ای که در جلسه از آن دفاع می‌کنی با ___ "
                    "گزارش می‌شود.",
                    ["might indicate", "is consistent with", "could possibly "
                     "show", "may perhaps suggest"], 1,
                    "'Is consistent with' is a strong evidential claim, not a "
                    "timid one.", "«is consistent with» ادعایی شاهدپایه و قوی "
                    "است، نه محتاط."),
                gap("The second trial is ___ to finish before December.",
                    ["unlikely", "expected"],
                    "Both fit the frame; 'unlikely' hedges towards no, "
                    "'expected' hedges towards yes.",
                    "هر دو در این ساخت جا می‌شوند: unlikely به سمت نه و "
                    "expected به سمت بله.", "one word"),
                mcq("Which hedge is placed where it does least work?",
                    "کدام احتیاط کم‌اثرترین جایگاه را دارد؟",
                    ["This may well explain the gap.",
                     "This possibly explains the gap.",
                     "This is likely to explain the gap.",
                     "This would appear to explain the gap."], 1,
                    "An adverb bolted on before the verb hedges the least.",
                    "قیدِ چسبانده پیش از فعل کمترین احتیاط را می‌رساند."),
                gap("There is little ___ that the change was deliberate.",
                    ["evidence", "to suggest"],
                    "The frame takes a noun or an infinitive, and neither "
                    "asserts.", "این ساخت اسم یا مصدر می‌گیرد و هیچ‌کدام ادعا "
                    "نمی‌کند.", "one or two words"),
            ],
        ),
        lesson(
            "c2-u2-l2", "vocabulary",
            ("Concede, refute, rebut, qualify",
             "Concede، refute، rebut، qualify"),
            ("Name what an argument does to the other side, precisely.",
             "دقیق نام بگذار که یک استدلال با طرف مقابل چه می‌کند."),
            [
                ("A debate has verbs of its own, and they are not synonyms. To "
                 "concede is to admit a point against yourself, usually to "
                 "keep the larger argument. To acknowledge is the milder "
                 "cousin: you notice the point without giving ground. To "
                 "refute is to prove false; to rebut is to answer an argument "
                 "without necessarily disproving it. To qualify is to accept "
                 "part of a claim while narrowing it.",
                 "مناظره فعل‌های خودش را دارد و این‌ها هم‌معنا نیستند. concede "
                 "یعنی پذیرفتن نکته‌ای علیه خود، معمولاً برای حفظ استدلال "
                 "بزرگ‌تر. acknowledge پسرعموی ملایم‌ترش است: نکته را می‌بینی "
                 "بی‌آنکه زمین بدهی. refute یعنی اثبات نادرستی؛ rebut یعنی "
                 "پاسخ دادن به استدلال بی‌آنکه حتماً ردش کنی. qualify یعنی "
                 "بخشی از ادعا را می‌پذیری و آن را محدود می‌کنی."),
                ("The misuse is common and easy to hear. 'The minister refuted "
                 "the report' claims proof, and a reader who checks will find "
                 "only disagreement. 'The minister rejected the report' is "
                 "what actually happened. In academic writing, refute is a "
                 "strong word: it means the argument is dead, not merely "
                 "unpopular.",
                 "کاربرد نادرستش رایج و شنیدنی است. «The minister refuted the "
                 "report» ادعای اثبات می‌کند و خواننده‌ای که بررسی کند تنها "
                 "مخالفت می‌یابد. «The minister rejected the report» همان است "
                 "که رخ داده. در نوشتار دانشگاهی refute واژهٔ قوی است: یعنی "
                 "استدلال مرده است، نه فقط محبوب نبودنش."),
                ("The nouns behave the same way: a concession, a rebuttal, a "
                 "refutation, a qualification, an acknowledgement. 'A "
                 "qualified acceptance' is acceptance with conditions, which "
                 "is exactly what a careful committee writes.",
                 "اسم‌ها هم همین‌طورند: a concession، a rebuttal، a "
                 "refutation، a qualification، an acknowledgement. «A "
                 "qualified acceptance» پذیرشی است با شرط، که دقیقاً همان "
                 "چیزی است که کمیتهٔ محتاط می‌نویسد."),
            ],
            [
                ("She conceded that the trial had been too short.",
                 "پذیرفت که آزمایش بیش از حد کوتاه بوده است."),
                ("The paper does not refute the theory; it narrows it.",
                 "مقاله نظریه را رد نمی‌کند؛ محدودش می‌کند."),
                ("He rebutted each objection in a single paragraph.",
                 "به هر اعتراضی در یک بند پاسخ داد."),
                ("The board gave qualified support to the plan.",
                 "هیئت‌مدیره حمایتی مشروط از طرح کرد."),
            ],
            [
                mcq("A writer who proves a claim false has ___ it.",
                    "نویسنده‌ای که نادرستی ادعایی را اثبات کند آن را ___ "
                    "کرده است.",
                    ["rebutted", "refuted", "conceded", "qualified"], 1,
                    "Proof of falsity is refutation.",
                    "اثبات نادرستی، refutation است."),
                mcq("'A qualified yes' means ___.", "«a qualified yes» یعنی "
                    "___.",
                    ["a reluctant no", "a yes with conditions",
                     "an unclear answer", "a yes from an expert"], 1,
                    "Qualified narrows rather than weakens.",
                    "qualified محدود می‌کند، نه ضعیف."),
            ],
            [
                mcq("Which sentence overclaims?", "کدام جمله بیش از اندازه "
                    "ادعا می‌کند؟",
                    ["The review challenges the book's central claim.",
                     "The review refutes the book's central claim.",
                     "The review questions the book's central claim.",
                     "The review disputes the book's central claim."], 1,
                    "Challenging is not proving false.",
                    "به‌چالش‌کشیدن اثبات نادرستی نیست."),
                gap("The government ___ that unemployment had risen, but "
                     "disputed the cause.",
                    ["conceded", "acknowledged"],
                    "Both admit the fact; concede admits it against interest.",
                    "هر دو واقعیت را می‌پذیرند؛ concede آن را علیه خود می‌پذیرد.",
                    "one word, past tense"),
                mcq("A rebuttal is ___ a refutation.", "rebuttal ___ refutation "
                    "است.",
                    ["always", "not necessarily", "the opposite of",
                     "a formal"], 1,
                    "A rebuttal answers; it need not disprove.",
                    "rebuttal پاسخ می‌دهد و لازم نیست رد کند."),
                gap("Her support was ___ : she backed the plan only if the "
                     "budget held.",
                    ["qualified", "conditional"],
                    "Support with conditions is qualified support.",
                    "حمایت با شرط، حمایت مشروط است.", "one word"),
            ],
        ),
        lesson(
            "c2-u2-l3", "listening",
            ("The lecture that admits its limits",
             "سخنرانی‌ای که محدودیت‌هایش را می‌پذیرد"),
            ("Follow a lecture where the speaker grades their own claims, and "
             "tell a finding from a suggestion.",
             "سخنرانی‌ای را دنبال کن که گوینده ادعاهایش را درجه‌بندی می‌کند و "
             "یافته را از پیشنهاد جدا کن."),
            [
                ("In a good lecture the hedges are the argument. A speaker who "
                 "says 'this is consistent with' is making a different claim "
                 "from one who says 'this proves', and the difference is often "
                 "the difference between a defensible paper and a retracted "
                 "one.",
                 "در سخنرانی خوب، احتیاط‌ها خودِ استدلال‌اند. گوینده‌ای که "
                 "می‌گوید «this is consistent with» ادعایی متفاوت از کسی "
                 "می‌کند که می‌گوید «this proves» و این تفاوت اغلب تفاوت "
                 "مقالهٔ قابل‌دفاع و مقالهٔ پس‌گرفته‌شده است."),
                ("Listen for the words that limit scope: in this sample, under "
                 "these conditions, over eight weeks, among younger "
                 "participants. A result without its scope is a slogan.",
                 "به واژه‌هایی گوش کن که دامنه را محدود می‌کنند: in this sample، "
                 "under these conditions، over eight weeks، among younger "
                 "participants. نتیجهٔ بی‌دامنه شعار است."),
            ],
            [
                ("Listen once for the claim, then again for the words that "
                 "limit it.", "یک بار برای ادعا گوش کن و بار دوم برای واژه‌هایی "
                 "که آن را محدود می‌کنند."),
                ("A cautious speaker often states the limitation before the "
                 "finding; that order is itself a signal.",
                 "گویندهٔ محتاط اغلب محدودیت را پیش از یافته می‌گوید؛ همین "
                 "ترتیب خودش نشانه است."),
                ("'We cannot yet say' is not 'we found nothing'.",
                 "«هنوز نمی‌توانیم بگوییم» با «چیزی نیافتیم» یکی نیست."),
            ],
            [
                mcq("A lecturer gives a number and then says what it does not "
                    "cover. Why?", "سخنرانی عددی می‌دهد و بعد می‌گوید چه "
                    "چیزی را پوشش نمی‌دهد. چرا؟",
                    ["to fill time", "to keep the claim inside its evidence",
                     "to avoid giving the number", "to criticise funders"], 1,
                    "The scope is part of the claim, not an apology for it.",
                    "دامنه بخشی از ادعاست، نه عذرخواهی برای آن."),
                mcq("A cautious speaker's limits usually come ___.",
                    "محدودیت‌های گویندهٔ محتاط معمولاً ___ می‌آیند.",
                    ["after the conclusion", "before or with the finding",
                     "in a handout only", "at the very end"], 1,
                    "Stating the limit early is the signal of a careful "
                    "claim.", "گفتن محدودیت در آغاز نشانهٔ ادعای محتاط است."),
            ],
            [
                listen("In our sample of two hundred, the effect was "
                       "consistent. I want to be careful: two hundred "
                       "students in one city is not the country, and we have "
                       "not yet run it for a full year.",
                       "What is the speaker's main point?",
                       "نکتهٔ اصلی گوینده چیست؟",
                       ["the effect is proven nationally",
                        "the effect held in the sample but the scope is "
                        "limited",
                        "the study failed", "the year was too short to "
                        "measure anything"], 1,
                       "The finding is stated and then bounded by sample, "
                       "place and duration.",
                       "یافته گفته و سپس با نمونه، مکان و مدت محدود می‌شود."),
                listen("The two studies are consistent with each other, which "
                       "is not the same as saying either one is right. Both "
                       "could be wrong in the same direction.",
                       "What is the speaker warning against?",
                       "گوینده از چه چیزی هشدار می‌دهد؟",
                       ["repeating a study", "treating agreement as proof",
                        "publishing too early", "using two samples"], 1,
                       "Agreement between studies is not proof of either.",
                       "هم‌خوانی دو مطالعه اثبات هیچ‌کدام نیست."),
                listen("We had expected the app to help most with grammar. "
                       "What we found, and this surprised us, is that it "
                       "mattered most for the students who were already "
                       "confident.",
                       "What surprised the speaker?", "چه چیزی گوینده را "
                       "شگفت‌زده کرد؟",
                       ["the app did not work", "confident students gained "
                        "the most", "grammar improved least",
                        "students ignored the app"], 1,
                       "The gain concentrated among the already confident.",
                       "بهره بیشتر در گروه از پیش مطمئن متمرکز بود."),
                mcq("A lecturer who says 'we cannot yet say' is ___.",
                    "سخنرانی که می‌گوید «we cannot yet say» ___.",
                    ["refusing to answer", "reporting the limit of the "
                     "evidence", "contradicting herself",
                     "ending the lecture"], 1,
                    "It states what the evidence supports, which is the "
                    "professional move.", "می‌گوید شاهد از چه پشتیبانی می‌کند و "
                    "این کار حرفه‌ای است."),
            ],
        ),
        lesson(
            "c2-u2-l4", "speaking",
            ("Defending a position under questioning",
             "دفاع از موضع زیر پرسش"),
            ("Hold a position while conceding what is true, and reformulate "
             "when a question lands.",
             "موضع را نگه دار، آنچه درست است بپذیر و وقتی پرسشی می‌نشیند "
             "بازصورت‌بندی کن."),
            [
                ("A defended position is not a repeated one. The move that "
                 "wins a room is: accept the part of the challenge that is "
                 "true, restate the claim more narrowly, and say what would "
                 "change your mind. It signals that the position was reached "
                 "by thinking rather than by owning.",
                 "موضعِ دفاع‌شده، موضعِ تکرارشده نیست. حرکتی که اتاق را "
                 "می‌برد این است: بخش درستِ چالش را بپذیر، ادعا را محدودتر "
                 "بازگو و بگو چه چیزی نظرت را عوض می‌کند. این نشان می‌دهد "
                 "موضع با فکر کردن به دست آمده، نه با مالکیت."),
                ("Reformulation is a skill in itself: 'Let me put that more "
                 "precisely' or 'The way I would frame it is' buys a second "
                 "and shows control. Filler does the opposite.",
                 "بازصورت‌بندی خودش مهارت است: «Let me put that more "
                 "precisely» یا «The way I would frame it is» ثانیه‌ای می‌خرد "
                 "و تسلط نشان می‌دهد. پرکردن فضا اثر معکوس دارد."),
            ],
            [
                ("That is a fair challenge, and I would narrow my claim: the "
                 "effect is clear in the first year, not afterwards.",
                 "این چالش منصفانه است و ادعایم را محدود می‌کنم: اثر در سال "
                 "اول روشن است، نه پس از آن."),
                ("I would not defend the number; I would defend the direction.",
                 "از عدد دفاع نمی‌کنم؛ از جهت دفاع می‌کنم."),
                ("Let me put that more precisely, because the wording matters "
                 "here.", "بگذار دقیق‌تر بگویم، چون واژه‌بندی اینجا مهم است."),
                ("If the second trial fails to replicate this, I would change "
                 "my position.", "اگر آزمایش دوم این را تکرار نکند، موضعم را "
                 "عوض می‌کنم."),
            ],
            [
                mcq("The strongest response to a fair objection is to ___.",
                    "قوی‌ترین پاسخ به اعتراض منصفانه ___ است.",
                    ["repeat the claim louder", "accept the true part and "
                     "narrow the claim", "change the subject",
                     "question the questioner"], 1,
                    "Conceding precisely is what makes the rest credible.",
                    "پذیرش دقیق همان چیزی است که بقیه را باورپذیر می‌کند."),
                mcq("'Let me put that more precisely' is ___.",
                    "عبارت «Let me put that more precisely» ___ است.",
                    ["an apology", "a reformulation move",
                     "a way of avoiding the question", "a conclusion"], 1,
                    "It buys time and raises the precision of the answer.",
                    "زمان می‌خرد و دقت پاسخ را بالا می‌برد."),
                mcq("Which reply keeps your position open without agreeing?",
                    "کدام پاسخ موضع را باز نگه می‌دارد بی‌آنکه موافقت کند؟",
                    ["Yes, you are right.", "That is not something I can "
                     "agree to at this stage.", "No comment.",
                     "I don't know anything."], 1,
                    "A time limit refuses this round, not the question.",
                    "محدودیت زمانی این دور را رد می‌کند، نه پرسش را."),
            ],
            [
                say("That is a fair objection, and I would accept it in part: "
                    "the sample was small, though the direction of the effect "
                    "was the same in every site.",
                    "این اعتراض منصفانه است و بخشی از آن را می‌پذیرم: نمونه "
                    "کوچک بود، هرچند جهت اثر در همهٔ سایت‌ها یکسان بود."),
                say("I would rather defend the argument than the figure, "
                    "because the figure is the part most likely to be wrong.",
                    "ترجیح می‌دهم از استدلال دفاع کنم تا از رقم، چون رقم "
                    "محتمل‌ترین بخش برای خطاست."),
                say("Let me restate that more carefully: what I am claiming "
                    "is not that the policy worked everywhere, but that it "
                    "worked where it was tried.",
                    "بگذار محتاط‌تر بازگو کنم: ادعایم این نیست که سیاست همه‌جا "
                    "کار کرد، بلکه این است که هرجا آزموده شد کار کرد."),
                say("If a second trial replicates this, I would be more "
                    "confident; if it does not, I would want to know why "
                    "before defending the finding again.",
                    "اگر آزمایش دومی این را تکرار کند مطمئن‌تر می‌شوم و اگر "
                    "نکند، پیش از دفاع دوباره از یافته می‌خواهم بدانم چرا."),
            ],
            dialogue=dialogue([
                ("Chair", "You have five minutes. Make the case, and expect "
                 "questions.",
                 "پنج دقیقه وقت دارید. استدلال را بگویید و منتظر پرسش "
                 "باشید."),
                ("You", "The pilot reduced waiting times by a third in the "
                 "two branches that ran it. I would not claim that for the "
                 "whole network.",
                 "آزمایش زمان انتظار را در دو شعبه‌ای که اجرا شد یک‌سوم کم "
                 "کرد. این را برای کل شبکه ادعا نمی‌کنم."),
                ("Chair", "A third is a large number for a small trial.",
                 "یک‌سوم برای آزمایشی کوچک رقم بزرگی است."),
                ("You", "It is, which is why I would run it for a year "
                 "before extending it.",
                 "درست است و به همین دلیل پیش از گسترش، یک سال اجرایش "
                 "می‌کنم."),
            ]),
        ),
    ],
)
