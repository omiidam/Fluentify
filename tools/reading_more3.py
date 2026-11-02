"""Two further practices for reference words and for inference."""
from reading_src import bi

MORE = {
    "reference": [
        {
            "title": bi("The mask goes home", "ماسک به خانه برمی‌گردد"),
            "level": "B2",
            "genre": bi("News report", "گزارش خبری"),
            "paragraphs": [
                "In 1897 a British officer took a carved mask from a village "
                "in what is now Nigeria and gave it to a museum in Bristol. "
                "For more than a century it sat in a glass case, labelled only "
                "with a number.",
                "Last year the museum agreed to return it. The decision was not "
                "easy: some trustees argued that the mask was safer in "
                "Bristol, where the building is dry and the insurance is paid. "
                "Others said that argument proved the point - the mask had "
                "never been theirs to protect.",
                "The village sent three elders to collect it. They arrived in "
                "April, were shown the case, and asked for the label to be "
                "removed before the mask was packed. The museum kept the label; "
                "it is now displayed beside an empty case, with a note "
                "explaining where the mask went.",
                "Since the return, two other museums have begun similar talks. "
                "Their directors say the precedent matters more than the "
                "object: once one return is possible, the question stops being "
                "whether and becomes how.",
            ],
            "summary": bi(
                "A museum returns a mask taken in 1897, keeps its label, and "
                "starts a conversation other museums now have to answer.",
                "موزه‌ای ماسکی را که در ۱۸۹۷ برده شده بود برمی‌گرداند، برچسبش را "
                "نگه می‌دارد و گفت‌وگویی می‌سازد که موزه‌های دیگر حالا باید "
                "جوابش را بدهند."),
            "questions": {
                "blanks": [
                    {"sentence": "The mask was taken from the village in ___.",
                     "answer": "1897", "also": [],
                     "hint": bi("A year, at the very start.",
                                "یک سال، در همان آغاز."),
                     "para": 1},
                    {"sentence": "The village sent ___ elders to collect it.",
                     "answer": "three", "also": ["3"],
                     "hint": bi("A number, in the third paragraph.",
                                "یک عدد، در پاراگراف سوم."),
                     "para": 3},
                    {"sentence": "The museum kept the ___, now shown beside an "
                                 "empty case.",
                     "answer": "label", "also": [],
                     "hint": bi("What the elders wanted removed.",
                                "چیزی که بزرگان می‌خواستند برداشته شود."),
                     "para": 3},
                ],
                "mcq": [
                    {"q": "In 'for more than a century it sat in a glass case', "
                           "what does 'it' refer to?",
                     "options": ["The museum", "The village", "The mask",
                                 "The number"],
                     "answer": 2,
                     "why": bi("The subject of the paragraph is the mask, and "
                               "the case is where a mask would sit. 'The "
                               "number' is the label on it.",
                               "موضوع پاراگراف ماسک است و ویترین جایی است که ماسک "
                               "می‌نشیند. «شماره» برچسب روی آن است."),
                     "para": 1},
                    {"q": "What does 'that argument proved the point' mean?",
                     "options": ["The mask was safer in Bristol",
                                 "The trustees' reason for keeping it actually "
                                 "supported returning it",
                                 "The museum should buy better insurance",
                                 "The village could not protect the mask"],
                     "answer": 1,
                     "why": bi("The next clause explains it: 'the mask had "
                               "never been theirs to protect' - so safety was "
                               "not a reason to keep it.",
                               "بند بعد توضیح می‌دهد: «ماسک هرگز مال آن‌ها نبود که "
                               "از آن محافظت کنند»؛ پس امنیت دلیل نگه داشتن نبود."),
                     "para": 2},
                    {"q": "Who are 'their' directors in the last paragraph?",
                     "options": ["The village elders'",
                                 "The two other museums'", "The trustees'",
                                 "The Bristol museum's"],
                     "answer": 1,
                     "why": bi("'Their' points back to 'two other museums', the "
                               "only plural in the sentence before.",
                               "«their» به «دو موزهٔ دیگر» برمی‌گردد، تنها جمع "
                               "جملهٔ قبل."),
                     "para": 4},
                ],
                "truefalse": [
                    {"statement": "The mask was displayed with its name on it.",
                     "answer": False,
                     "why": bi("It was 'labelled only with a number'.",
                               "«فقط با یک شماره برچسب خورده بود»."),
                     "para": 1},
                    {"statement": "The mask is now back in the village.",
                     "answer": True,
                     "why": bi("The village collected it in April; the case in "
                               "Bristol is empty.",
                               "روستا در آوریل آن را تحویل گرفت؛ ویترین بریستول "
                               "خالی است."),
                     "para": 3},
                    {"statement": "The empty case carries a note explaining "
                                  "where the mask went.",
                     "answer": True,
                     "why": bi("'A note explaining where the mask went.'",
                               "«یادداشتی که توضیح می‌دهد ماسک کجا رفت.»"),
                     "para": 3},
                ],
                "essay": [
                    {"prompt": bi("Why keep the label and show an empty case "
                                  "instead of filling the space? Answer in "
                                  "three or four sentences.",
                                  "چرا برچسب را نگه دارند و ویترین خالی را نشان "
                                  "دهند به‌جای پر کردن فضا؟ در سه یا چهار جمله "
                                  "جواب بده."),
                     "min_words": 45,
                     "tips": [
                         bi("Say what an empty case makes a visitor do.",
                            "بگو ویترین خالی بازدیدکننده را به چه کاری وامی‌دارد."),
                         bi("Connect it to the label, which names a number, not "
                            "a person.",
                            "به برچسب وصلش کن، برچسبی که شماره می‌گوید، نه نام "
                            "آدم."),
                         bi("Use the last paragraph's word: precedent.",
                            "واژهٔ پاراگراف آخر را به کار ببر: رویه.")],
                     "model": bi("An empty case is more honest than a "
                                 "replacement object, because it shows a gap "
                                 "rather than filling it. The label beside it "
                                 "tells a visitor that what was here had a "
                                 "number instead of a name, which is how the "
                                 "mask was treated for a century. Leaving the "
                                 "space empty also makes the return visible, and "
                                 "that is what the passage calls the precedent: "
                                 "the question for other museums becomes how to "
                                 "return, not whether.",
                                 "ویترین خالی از یک شیء جانشین صادقانه‌تر است، چون "
                                 "جای خالی را نشان می‌دهد نه پر کردنش. برچسب کنارش "
                                 "به بازدیدکننده می‌گوید چیزی که اینجا بود شماره "
                                 "داشت نه نام؛ همین‌طور یک قرن با ماسک رفتار شد. "
                                 "خالی گذاشتن فضا بازگشت را هم دیدنی می‌کند و "
                                 "همین چیزی است که متن «رویه» می‌نامدش: سؤال موزه‌های "
                                 "دیگر از «آیا» به «چگونه» تغییر می‌کند.")},
                ],
            },
        },
        {
            "title": bi("A vote about the pool", "رأیی دربارهٔ استخر"),
            "level": "B1",
            "genre": bi("Local news", "خبر محلی"),
            "paragraphs": [
                "The council has voted to close the swimming pool on Tuesdays. "
                "This surprised the staff, who had been told the change would "
                "affect only the car park, but it delighted the residents who "
                "had complained about the noise of the pumps.",
                "The pool's manager, Dario Rossi, says the decision was made "
                "without a proper survey. He has asked for the figures the "
                "council used; they have not been published, and the council "
                "says it will release them in June.",
                "The residents' group, however, says its members were never "
                "against the pool itself, only the pumps, which run all night. "
                "They have offered to pay for a quieter pump if the Tuesday "
                "closure is dropped.",
                "The council's cabinet meets on 4 May. Its chair, Councillor "
                "Rehana Ali, told this newspaper that she would listen, but "
                "that the budget for the year had already been set.",
            ],
            "summary": bi(
                "A Tuesday closure pleases the neighbours, shocks the staff and "
                "leaves the manager asking for figures nobody has published.",
                "بستن سه‌شنبه‌ها همسایه‌ها را خوشحال می‌کند، کارکنان را شوکه و "
                "مدیر را در پی ارقامی می‌گذارد که کسی منتشر نکرده است."),
            "questions": {
                "blanks": [
                    {"sentence": "The pool will close on ___.",
                     "answer": "Tuesdays", "also": ["tuesday"],
                     "hint": bi("A day, in the first sentence.",
                                "یک روز، در جملهٔ اول."),
                     "para": 1},
                    {"sentence": "The council says it will release the figures "
                                 "in ___.",
                     "answer": "June", "also": [],
                     "hint": bi("A month, in the second paragraph.",
                                "یک ماه، در پاراگراف دوم."),
                     "para": 2},
                    {"sentence": "The cabinet meets on 4 ___.",
                     "answer": "May", "also": [],
                     "hint": bi("A month, in the last paragraph.",
                                "یک ماه، در پاراگراف آخر."),
                     "para": 4},
                ],
                "mcq": [
                    {"q": "In 'This surprised the staff', what does 'This' "
                           "refer to?",
                     "options": ["The noise of the pumps",
                                 "The vote to close the pool on Tuesdays",
                                 "The car park change",
                                 "The survey"],
                     "answer": 1,
                     "why": bi("'This' points at the whole first sentence - the "
                               "decision - not at the last noun.",
                               "«This» به کل جملهٔ اول اشاره دارد، یعنی تصمیم، نه "
                               "به آخرین اسم."),
                     "para": 1},
                    {"q": "In 'they have not been published', who or what are "
                           "'they'?",
                     "options": ["The staff", "The figures", "The residents",
                                 "The pumps"],
                     "answer": 1,
                     "why": bi("The sentence before asks for 'the figures the "
                               "council used'; the pronoun carries that noun "
                               "forward.",
                               "جملهٔ قبل «ارقامی که شورا استفاده کرد» را می‌خواهد؛ "
                               "ضمیر همان اسم را جلو می‌برد."),
                     "para": 2},
                    {"q": "Whose chair is Councillor Ali?",
                     "options": ["The residents' group", "The pool's",
                                 "The cabinet's", "The newspaper's"],
                     "answer": 2,
                     "why": bi("'The council's cabinet meets on 4 May. Its "
                               "chair...' - 'its' belongs to the cabinet.",
                               "«کابینهٔ شورا ۴ مه جلسه دارد. رئیس آن...»؛ «its» "
                               "مال کابینه است."),
                     "para": 4},
                ],
                "truefalse": [
                    {"statement": "The staff expected only the car park to "
                                  "change.",
                     "answer": True,
                     "why": bi("'Who had been told the change would affect only "
                               "the car park'.",
                               "«که به آن‌ها گفته شده بود تغییر فقط پارکینگ را "
                               "تحت تأثیر می‌گذارد»."),
                     "para": 1},
                    {"statement": "The residents want the pool closed for "
                                  "good.",
                     "answer": False,
                     "why": bi("They were 'never against the pool itself, only "
                               "the pumps'.",
                               "آن‌ها «هرگز مخالف خود استخر نبودند، فقط پمپ‌ها»."),
                     "para": 3},
                    {"statement": "The budget for the year is already fixed.",
                     "answer": True,
                     "why": bi("The councillor says 'the budget for the year "
                               "had already been set'.",
                               "عضو شورا می‌گوید «بودجهٔ سال از قبل تعیین شده "
                               "بود»."),
                     "para": 4},
                ],
                "essay": [
                    {"prompt": bi("The passage uses 'this', 'they' and 'its' to "
                                  "hold it together. Pick two of them, say what "
                                  "each refers to, and explain how you decided.",
                                  "متن از «this»، «they» و «its» برای پیوند استفاده "
                                  "می‌کند. دو تا را انتخاب کن، بگو هر کدام به چه "
                                  "چیزی اشاره دارد و توضیح بده چطور تصمیم گرفتی."),
                     "min_words": 50,
                     "tips": [
                         bi("Quote the sentence each pronoun sits in.",
                            "جمله‌ای را که هر ضمیر در آن است نقل کن."),
                         bi("Say which noun or whole clause it replaces.",
                            "بگو کدام اسم یا کدام بند را جانشین می‌شود."),
                         bi("Mention that the nearest noun is not always the "
                            "answer.",
                            "بگو نزدیک‌ترین اسم همیشه جواب نیست.")],
                     "model": bi("'This surprised the staff' refers to the "
                                 "decision in the sentence before - closing the "
                                 "pool on Tuesdays - not to the word Tuesdays. "
                                 "I decided that because a day cannot surprise "
                                 "anyone; a decision can. 'They have not been "
                                 "published' refers to the figures, which is the "
                                 "last plural noun the manager asked for. In both "
                                 "cases the nearest noun gives the wrong answer, "
                                 "and the verb decides.",
                                 "«This surprised the staff» به تصمیم جملهٔ قبل "
                                 "برمی‌گردد، یعنی بستن استخر در سه‌شنبه‌ها، نه به "
                                 "واژهٔ سه‌شنبه؛ چون یک روز کسی را شوکه نمی‌کند، "
                                 "ولی یک تصمیم می‌کند. «They have not been "
                                 "published» به ارقام برمی‌گردد که آخرین اسم جمعی "
                                 "است که مدیر خواسته بود. در هر دو مورد نزدیک‌ترین "
                                 "اسم جواب غلط می‌دهد و فعل تصمیم می‌گیرد.")},
                ],
            },
        },
    ],
    "inference": [
        {
            "title": bi("The house on the hill", "خانهٔ روی تپه"),
            "level": "B2",
            "genre": bi("Short story", "داستان کوتاه"),
            "paragraphs": [
                "My sister arrived on Friday with a folder of papers and a "
                "bottle of wine, which she put on the table without opening. "
                "She asked how the roof was. I said it was the same as last "
                "year, and she looked at the ceiling as though it had answered "
                "her.",
                "We walked the boundaries after lunch. At the old gate she "
                "stopped and said the estate agent had valued the whole plot at "
                "less than I had hoped. She said it quickly, the way people say "
                "a thing they have rehearsed in the car.",
                "I asked whether she wanted to sell. She said she wanted us "
                "both to be able to sleep, which was not an answer, and we "
                "walked back without talking. The bottle stayed on the table.",
                "On Sunday she made tea and put two cups down, then took one "
                "away again. 'I'll write to you,' she said at the door. The "
                "letter came on Thursday, four pages, and the first line was an "
                "apology.",
            ],
            "summary": bi(
                "Two siblings walk a boundary they may be about to sell; "
                "neither says what they mean, and the letter afterwards says it "
                "for them.",
                "دو خواهر و برادر مرزی را که شاید بفروشند قدم می‌زنند؛ هیچ‌کدام "
                "منظورش را نمی‌گوید و نامهٔ بعداز آن به‌جایشان می‌گوید."),
            "questions": {
                "blanks": [
                    {"sentence": "The sister arrived on ___.", "answer": "Friday",
                     "also": [], "hint": bi("The first word of the story.",
                                             "اولین کلمهٔ داستان."), "para": 1},
                    {"sentence": "The valuation was less than the narrator had "
                                 "___.",
                     "answer": "hoped", "also": [],
                     "hint": bi("A verb, in the second paragraph.",
                                "یک فعل، در پاراگراف دوم."),
                     "para": 2},
                    {"sentence": "The letter came on ___.", "answer": "Thursday",
                     "also": [], "hint": bi("After the weekend visit.",
                                             "بعد از دیدار آخر هفته."),
                     "para": 4},
                ],
                "mcq": [
                    {"q": "How does the sister probably feel about selling?",
                     "options": ["Eager to sell quickly",
                                 "Uncomfortable, and unable to say so directly",
                                 "Certain the narrator will refuse",
                                 "Angry about the roof"],
                     "answer": 1,
                     "why": bi("She rehearses bad news, avoids the question, "
                               "takes a cup away and apologises by letter - "
                               "every sign points to reluctance, not eagerness.",
                               "خبر بد را از پیش تمرین می‌کند، از سؤال می‌گریزد، "
                               "یکی از فنجان‌ها را برمی‌دارد و در نامه عذرخواهی "
                               "می‌کند؛ همهٔ نشانه‌ها به اکراه اشاره دارد، نه "
                               "اشتیاق."),
                     "para": 3},
                    {"q": "What does the unopened bottle suggest?",
                     "options": ["The sister does not drink wine",
                                 "The visit was business, not a celebration",
                                 "The bottle was a present for later",
                                 "The narrator is not allowed alcohol"],
                     "answer": 1,
                     "why": bi("A bottle brought but never opened, left on the "
                               "table, frames a conversation about valuations "
                               "and signatures.",
                               "بطری‌ای آورده و هرگز باز نشده، روی میز مانده، "
                               "گفت‌وگویی دربارهٔ ارزش‌گذاری و امضا را قاب "
                               "می‌گیرد."),
                     "para": 1},
                    {"q": "What do the four pages and the apology suggest?",
                     "options": ["She has changed her mind about the sale",
                                 "She regrets how she handled the weekend",
                                 "She wants a larger share of the money",
                                 "She is asking the narrator to move out"],
                     "answer": 1,
                     "why": bi("An apology on the first line, after a silent "
                               "walk and a withdrawn cup, is about how the "
                               "visit went, and the passage never says she "
                               "changed her mind.",
                               "عذرخواهی در خط اول، پس از قدم زدن بی‌حرف و "
                               "برداشتن فنجان، دربارهٔ نحوهٔ دیدار است؛ متن "
                               "هیچ‌جا نمی‌گوید نظرش عوض شده."),
                     "para": 4},
                ],
                "truefalse": [
                    {"statement": "The roof had been repaired since last year.",
                     "answer": False,
                     "why": bi("'I said it was the same as last year.'",
                               "«گفتم مثل سال قبل است.»"),
                     "para": 1},
                    {"statement": "The sister answered the question about "
                                  "selling directly.",
                     "answer": False,
                     "why": bi("She says she wants them both to be able to "
                               "sleep, 'which was not an answer'.",
                               "می‌گوید می‌خواهد هر دو بتوانند بخوابند، «که جواب "
                               "نبود»."),
                     "para": 3},
                    {"statement": "The narrator had expected a higher "
                                  "valuation.",
                     "answer": True,
                     "why": bi("The figure was 'less than I had hoped'.",
                               "رقم «کمتر از آن بود که امید داشتم»."),
                     "para": 2},
                ],
                "essay": [
                    {"prompt": bi("What can you infer about the relationship "
                                  "between the two? Support each point with one "
                                  "detail, and say what you cannot know.",
                                  "دربارهٔ رابطهٔ این دو چه می‌توانی استنتاج کنی؟ هر "
                                  "نکته را با یک جزئیات پشتیبانی کن و بگو چه چیزی "
                                  "را نمی‌توانی بدانی."),
                     "min_words": 60,
                     "tips": [
                         bi("Two claims is enough; each needs a detail.",
                            "دو ادعا کافی است؛ هر کدام یک جزئیات می‌خواهد."),
                         bi("Do not invent a cause such as an illness or a "
                            "debt.",
                            "علتی مثل بیماری یا بدهی از خودت نساز."),
                         bi("End with the limit of what a short story shows.",
                            "با محدودیت آنچه یک داستان کوتاه نشان می‌دهد تمام کن.")],
                     "model": bi("They are careful with each other but not "
                                 "close, or not close any more: the sister "
                                 "rehearses her news in the car, and the "
                                 "narrator answers a question about the roof "
                                 "with one sentence. The withdrawn cup suggests "
                                 "she intended to stay and then decided not to. "
                                 "The letter is an attempt to repair something, "
                                 "which is why it begins with an apology. What I "
                                 "cannot know is what either of them wants the "
                                 "money for, and whether the narrator agrees to "
                                 "sell.",
                                 "با هم مهربان‌اند ولی نزدیک نیستند، یا دیگر نزدیک "
                                 "نیستند: خواهر خبرش را در ماشین از پیش تمرین "
                                 "می‌کند و راوی با یک جمله به سؤال سقف جواب "
                                 "می‌دهد. برداشتن فنجان نشان می‌دهد قصد داشت بماند "
                                 "و بعد منصرف شد. نامه تلاشی برای ترمیم چیزی است، "
                                 "و همین است که با عذرخواهی شروع می‌شود. چیزی که "
                                 "نمی‌توانم بدانم این است که هر کدام پول را برای چه "
                                 "می‌خواهند و آیا راوی با فروش موافقت می‌کند.")},
                ],
            },
        },
        {
            "title": bi("The fourth floor", "طبقهٔ چهارم"),
            "level": "B2",
            "genre": bi("Personal narrative", "روایت شخصی"),
            "paragraphs": [
                "The office was on the fourth floor and the lift was out of "
                "order. By the time I reached the desk I had rehearsed my "
                "opening line four times and could no longer hear it.",
                "The interviewer did not look up from my CV for the first "
                "minute. Then she asked why I had left my last job, and I heard "
                "myself give the answer I had promised not to give: the honest "
                "one.",
                "She wrote something. 'We have three other people at this "
                "stage,' she said, and then, unexpectedly, 'What would you "
                "change about this office?' I looked at the empty desk by the "
                "window and said the truth again.",
                "On the bus home I decided I had not got it. The email came "
                "that evening, and I read it twice before I understood that the "
                "sentence beginning 'We are pleased' was addressed to me.",
            ],
            "summary": bi(
                "A nervous interview in which the candidate answers honestly "
                "against their own plan - and cannot believe the result.",
                "مصاحبه‌ای پرتنش که در آن داوطلب برخلاف نقشهٔ خودش صادقانه جواب "
                "می‌دهد - و نتیجه را باور نمی‌کند."),
            "questions": {
                "blanks": [
                    {"sentence": "The office was on the ___ floor.",
                     "answer": "fourth", "also": ["4th"],
                     "hint": bi("The first sentence.",
                                "جملهٔ اول."),
                     "para": 1},
                    {"sentence": "The interviewer says three other people are "
                                 "at this ___.",
                     "answer": "stage", "also": [],
                     "hint": bi("After the word 'this'.",
                                "بعد از واژهٔ this."),
                     "para": 3},
                    {"sentence": "The email came that ___.",
                     "answer": "evening", "also": [],
                     "hint": bi("After the bus ride.",
                                "بعد از سوار شدن به اتوبوس."),
                     "para": 4},
                ],
                "mcq": [
                    {"q": "How did the candidate feel when they reached the "
                           "desk?",
                     "options": ["Confident and prepared",
                                 "Nervous, with a prepared line they had lost "
                                 "confidence in",
                                 "Angry about the lift",
                                 "Certain they would be rejected"],
                     "answer": 1,
                     "why": bi("Four floors of stairs and a line rehearsed four "
                               "times until it 'could no longer hear it' is "
                               "nerves, not confidence.",
                               "چهار طبقه پله و جمله‌ای که چهار بار تکرار شده تا "
                               "«دیگر شنیده نمی‌شد»، تنش است نه اعتماد."),
                     "para": 1},
                    {"q": "Why does the empty desk matter?",
                     "options": ["It shows the office is closing",
                                 "It is what the candidate would change, so an "
                                 "honest answer had somewhere to point",
                                 "It belonged to the interviewer",
                                 "It proves the company is growing"],
                     "answer": 1,
                     "why": bi("The question is what they would change; the "
                               "desk is the thing in front of them, so the "
                               "honest answer is also a specific one.",
                               "سؤال این است چه چیزی را عوض می‌کردند؛ میز همان "
                               "چیزی است که جلوی چشمشان است، پس جواب صادقانه "
                               "مشخص هم هست."),
                     "para": 3},
                    {"q": "What does reading the email twice suggest?",
                     "options": ["The email was badly written",
                                 "The candidate could not believe the result",
                                 "The candidate was checking the salary",
                                 "The email was in another language"],
                     "answer": 1,
                     "why": bi("They had already 'decided I had not got it', so "
                               "the offer needed a second reading to be "
                               "believed.",
                               "او از قبل «تصمیم گرفته بود که قبول نشده»، پس پیشنهاد "
                               "برای باور شدن خواندن دوم لازم داشت."),
                     "para": 4},
                ],
                "truefalse": [
                    {"statement": "The lift was working.",
                     "answer": False,
                     "why": bi("'The lift was out of order.'",
                               "«آسانسور خراب بود.»"),
                     "para": 1},
                    {"statement": "The candidate gave the answers they had "
                                  "planned.",
                     "answer": False,
                     "why": bi("They gave 'the answer I had promised not to "
                               "give: the honest one'.",
                               "«جوابی را دادم که قول داده بودم ندهم: جواب "
                               "صادقانه.»"),
                     "para": 2},
                    {"statement": "The candidate was offered the job.",
                     "answer": True,
                     "why": bi("'The sentence beginning We are pleased was "
                               "addressed to me.'",
                               "«جمله‌ای که با We are pleased شروع می‌شد به من "
                               "بود.»"),
                     "para": 4},
                ],
                "essay": [
                    {"prompt": bi("The narrator says they 'heard myself' give "
                                  "the honest answer. What does that phrase "
                                  "reveal about their state of mind, and what "
                                  "does the ending suggest about the "
                                  "interviewer?",
                                  "راوی می‌گوید «خودم را شنیدم» که جواب صادقانه "
                                  "می‌دهم. این عبارت چه چیزی دربارهٔ حال او نشان "
                                  "می‌دهد و پایان دربارهٔ مصاحبه‌کننده چه می‌گوید؟"),
                     "min_words": 55,
                     "tips": [
                         bi("'Heard myself' means it happened without a "
                            "decision - say so.",
                            "«خودم را شنیدم» یعنی بدون تصمیم اتفاق افتاد؛ همین را "
                            "بگو."),
                         bi("Use one detail about the interviewer's behaviour.",
                            "یک جزئیات از رفتار مصاحبه‌کننده بیاور."),
                         bi("Avoid claiming to know what the interviewer "
                            "thought.",
                            "ادعا نکن که فکر مصاحبه‌کننده را می‌دانی.")],
                     "model": bi("'I heard myself' suggests the answer came out "
                                 "before the narrator could stop it, as if they "
                                 "were listening to someone else - which is what "
                                 "happens under stress, when the prepared "
                                 "sentence will not stay in place. The ending "
                                 "suggests the interviewer valued what the "
                                 "candidate calls honesty, since the offer "
                                 "follows the two answers they had not planned. "
                                 "What it does not suggest is that the "
                                 "interviewer was easy to read: she wrote "
                                 "something and said nothing encouraging.",
                                 "«خودم را شنیدم» نشان می‌دهد جواب پیش از آن‌که راوی "
                                 "بتواند جلویش را بگیرد بیرون آمد، مثل اینکه به "
                                 "کسی دیگر گوش می‌داد؛ همان چیزی که زیر فشار "
                                 "اتفاق می‌افتد، وقتی جملهٔ تمرین‌شده سر جایش "
                                 "نمی‌ماند. پایان نشان می‌دهد مصاحبه‌کننده همان "
                                 "چیزی را که داوطلب «صداقت» می‌نامد ارزش دانسته، "
                                 "چون پیشنهاد بعد از دو جوابِ بی‌نقشه می‌آید. چیزی "
                                 "که نشان نمی‌دهد این است که خواندنِ او آسان بود: "
                                 "چیزی نوشت و هیچ تشویقی نکرد.")},
                ],
            },
        },
    ],
}
