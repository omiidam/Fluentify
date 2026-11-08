#!/usr/bin/env python3
"""B1 · units 7-8: what must be true, and what is worth doing.

Unit 7 ends in a complaint call, where obligation and probability meet; unit 8
ends in the spoken opinion, where gerunds and infinitives let a learner say
what something is worth.
"""

from course_kit import dialogue, gap, lesson, listen, mcq, passage, say, unit

U7 = unit(
    "b1-u7",
    ("You must be tired", "باید خسته باشی"),
    ("Say what is required, what is likely and what is not possible, and complain until a problem is fixed.", "بگو چه چیزی لازم و چه چیزی محتمل است و چه چیزی ممکن نیست، و شکایت کن تا مشکل حل شود."),
    [
        lesson(
            "b1-u7-l1",
            "grammar",
            ("Modals of obligation, advice and probability", "افعال وجهی اجبار، توصیه و احتمال"),
            ("Use must, have to, should, might and can't for rules, advice and deductions.", "must، have to، should، might و can't را برای قانون، توصیه و استنباط به کار ببر."),
            [
                ("Obligation: must (strong, often the speaker's own view), have to (an outside rule), need to (a practical necessity). No obligation is don't have to; prohibition is mustn't. I must call my mother / I have to wear a uniform / You don't have to come / You mustn't smoke here.", "اجبار: must (شدید، اغلب نظر گوینده)، have to (قانون بیرونی)، need to (ضرورت عملی). نبودِ اجبار don't have to و ممنوعیت mustn't است."),
                ("Advice: should / ought to / had better. Had better carries a warning — something bad follows if you don't: You'd better take an umbrella. Should is neutral advice.", "توصیه: should / ought to / had better. had better هشدار دارد: You'd better take an umbrella. should توصیهٔ خنثی است."),
                ("Deduction about the present: must be (I'm certain it is true), might/may/could be (possible), can't be (I'm certain it is not). 'He must be tired' is a conclusion from evidence, not an obligation — the opposite of 'He must rest'.", "استنباط دربارهٔ حال: must be (مطمئنم درست است)، might/may/could be (ممکن)، can't be (مطمئنم نیست). «He must be tired» نتیجه‌گیری از شاهد است، نه اجبار؛ متضاد «He must rest»."),
                ("Past deduction: must have + participle (it certainly happened), might have (perhaps), can't have (certainly not). She must have missed the train. Permission uses can, may (formal) and be allowed to.", "استنباط گذشته: must have + اسم مفعول، might have، can't have. She must have missed the train. اجازه با can، may (رسمی) و be allowed to گفته می‌شود."),
            ],
            [
                ("You mustn't use your phone while you're driving — it's illegal.", "هنگام رانندگی نباید از گوشی استفاده کنی؛ غیرقانونی است."),
                ("You don't have to book, but it's cheaper if you do.", "لازم نیست رزرو کنی، اما اگر بکنی ارزان‌تر است."),
                ("You'd better leave now if you want to catch the last metro.", "اگر می‌خواهی به آخرین مترو برسی بهتر است الان راه بیفتی."),
                ("The lights are off — they must have gone to bed.", "چراغ‌ها خاموش است؛ حتماً خوابیده‌اند."),
                ("That can't be Sara at the door; she's in Tabriz.", "آن نمی‌تواند سارا باشد؛ او در تبریز است."),
            ],
            [
                mcq("The office is dark and the door is locked. Everyone ___ gone home.", "دفتر تاریک است و در قفل. همه ___ رفته‌اند.", ["must have", "must", "should have", "can't have"], 0,
                    "Certainty about the past: must have + participle.", "اطمینان دربارهٔ گذشته: must have + اسم مفعول."),
                mcq("You ___ bring a towel; the hotel provides them.", "لازم نیست حوله بیاوری؛ هتل حوله می‌دهد.", ["mustn't", "don't have to", "shouldn't", "can't"], 1,
                    "No obligation is don't have to.", "نبودِ اجبار با don't have to است."),
            ],
            [
                gap("She's been working since six. She ___ be exhausted.", ["must"], "A deduction from evidence: must be.", "استنباط از شاهد: must be."),
                gap("You ___ better see a doctor if the pain continues.", ["had", "'d"], "Had better + plain verb, a warning.", "had better + فعل ساده، همراه هشدار."),
                mcq("Which sentence is a prohibition?", "کدام جمله ممنوعیت است؟", ["You don't have to pay.", "You mustn't park here.", "You should rest.", "You might be right."], 1,
                    "Mustn't forbids; don't have to permits.", "mustn't منع می‌کند و don't have to اجازه می‌دهد."),
                listen("The train left at seven and it's only half past six now. — Then we can't have missed it; we're early.", "What do they conclude?", "به چه نتیجه‌ای می‌رسند؟", ["they missed the train", "they are early", "the train is late", "they are on the wrong platform"], 1,
                       "Can't have missed it — the time has not come.", "can't have missed it، چون زمان نرسیده است."),
            ],
        ),
        lesson(
            "b1-u7-l2",
            "vocabulary",
            ("Money, services and complaining effectively", "پول، خدمات و شکایت مؤثر"),
            ("Handle an account, a bill or a broken service with the right verbs and prepositions.", "حساب، صورت‌حساب یا خدمت خراب را با فعل و حرف اضافهٔ درست مدیریت کن."),
            [
                ("Money verbs carry their prepositions: pay for something, pay back a loan, spend money on, save up for, afford (no preposition), owe someone, be worth. 'I can't afford it' needs no 'to'.", "فعل‌های پول حرف اضافهٔ خودشان را دارند: pay for، pay back، spend on، save up for، afford (بدون حرف اضافه)، owe، be worth. «I can't afford it» به to نیاز ندارد."),
                ("Accounts and services: open an account, transfer money, withdraw cash, set up a direct debit, cancel a subscription, be charged for, be refunded. 'They charged me twice' is the complaint pattern.", "حساب و خدمات: open an account، transfer money، withdraw cash، set up a direct debit، cancel a subscription، be charged for، be refunded. «They charged me twice» الگوی شکایت است."),
                ("Complaint language escalates in three steps: state the facts, state the effect, state what you want. I cancelled on the 3rd. I was still charged on the 5th. I'd like the money back and the subscription closed.", "زبان شکایت سه پله دارد: واقعیت را بگو، اثرش را بگو و آنچه می‌خواهی را بگو. I cancelled on the 3rd. I was still charged on the 5th. I'd like the money back."),
            ],
            [
                ("I'm saving up for a course next year.", "برای دوره‌ای در سال آینده پول پس‌انداز می‌کنم."),
                ("They charged me for a service I had already cancelled.", "برای خدمتی که قبلاً لغو کرده بودم از من پول گرفتند."),
                ("Could you transfer the amount back to my account?", "می‌شود مبلغ را به حسابم برگردانید؟"),
                ("It's not worth arguing about five thousand toman.", "ارزش ندارد بر سر پنج هزار تومان بحث کنیم."),
            ],
            [
                mcq("Which is correct?", "کدام درست است؟", ["I can't afford to buy a car.", "I can't afford buying a car.", "I can't afford for a car.", "I can't afford to a car."], 0,
                    "Afford takes a to-infinitive or a direct object: can't afford a car / can't afford to buy.", "afford با to + فعل یا مفعول مستقیم می‌آید."),
                mcq("To take money out of an account is to ___ it.", "برداشتن پول از حساب ___ است.", ["transfer", "withdraw", "charge", "owe"], 1,
                    "Withdraw cash from an account.", "withdraw cash از حساب."),
            ],
            [
                gap("I ___ him fifty pounds until payday.", ["owe"], "Owe someone money.", "owe somebody money یعنی به کسی بدهکار بودن."),
                gap("They ___ me twice for the same order.", ["charged"], "Charge someone for something.", "charge somebody for something یعنی از کسی پول گرفتن."),
                mcq("Which sentence states the effect of a problem?", "کدام جمله اثر مشکل را می‌گوید؟", ["I cancelled on the 3rd.", "I was still charged on the 5th.", "I'd like a refund.", "Hello."], 1,
                    "The effect is what the error did to you.", "اثر همان چیزی است که خطا با تو کرد."),
                mcq("'Set up a direct debit' means ___.", "«Set up a direct debit» یعنی ___.", ["pay in cash", "arrange an automatic payment", "cancel a payment", "borrow money"], 1,
                    "A direct debit pays automatically from your account.", "direct debit به‌طور خودکار از حساب پرداخت می‌کند."),
            ],
        ),
        lesson(
            "b1-u7-l3",
            "listening",
            ("The complaint call", "تماس شکایت"),
            ("Follow a service call and catch the numbers, the dates and the resolution.", "تماس خدماتی را دنبال کن و عددها، تاریخ‌ها و نتیجه را بگیر."),
            [
                ("A service call has a script: identify yourself, state the problem, give the reference, hear the offer, accept or escalate. Numbers and dates are the evidence, so write them as you hear them.", "تماس خدماتی فیلم‌نامه دارد: خودت را معرفی کن، مشکل را بگو، شمارهٔ پیگیری بده، پیشنهاد را بشنو، قبول کن یا بالا ببر. عددها و تاریخ‌ها شاهدند، پس همان‌طور که می‌شنوی بنویس."),
                ("Listen for the modal of the resolution. 'We can refund you' is a decision; 'we should be able to' is not. 'It might take five days' warns you not to expect it tomorrow.", "به فعل وجهیِ نتیجه گوش کن. «We can refund you» تصمیم است و «we should be able to» نه. «It might take five days» هشدار می‌دهد فردا انتظار نداشته باش."),
            ],
            [
                ("'I was charged twice on the fifth of May, twenty-nine ninety-nine each time.'", "«پنجم مه دو بار از من پول گرفته شد، هر بار بیست‌ونه و نودونه»."),
                ("'I can refund the second payment today, but the subscription will close at the end of the month.'", "«پرداخت دوم را امروز برمی‌گردانم، اما اشتراک آخر ماه بسته می‌شود»."),
                ("'It might take five working days to appear in your account.'", "«ممکن است پنج روز کاری طول بکشد تا در حسابت دیده شود»."),
            ],
            [
                listen("I cancelled my subscription on the third of May, but I was charged twice on the fifth. — I can see two payments here. I can refund the second one today.", "What is the problem?", "مشکل چیست؟", ["the subscription never started", "she was charged twice after cancelling", "the app does not work", "she was charged too little"], 1,
                       "Two payments after a cancellation.", "دو پرداخت بعد از لغو."),
                listen("I cancelled my subscription on the third of May, but I was charged twice on the fifth. — I can see two payments here. I can refund the second one today.", "What does the agent offer?", "کارشناس چه پیشنهاد می‌دهد؟", ["to refund both payments", "to refund the second payment", "a free month", "nothing"], 1,
                       "'I can refund the second one today.'", "«پرداخت دوم را امروز برمی‌گردانم»."),
            ],
            [
                listen("I'm afraid the refund might take five working days to appear in your account. — Five days? That's a long time. — I understand, but that is the bank's process.", "How long might the refund take?", "بازپرداخت چقدر طول می‌کشد؟", ["one day", "three days", "five working days", "a month"], 2,
                       "'Five working days' is the stated time.", "«پنج روز کاری» زمان گفته‌شده است."),
                listen("We can send an engineer on Tuesday between eight and twelve, or on Thursday afternoon. — Thursday is better for me. — Then I'll book Thursday between one and five.", "When is the appointment?", "قرار کِی است؟", ["Tuesday morning", "Tuesday afternoon", "Thursday afternoon", "Thursday morning"], 2,
                       "Thursday between one and five is the afternoon.", "پنجشنبه بین یک تا پنج بعدازظهر است."),
                mcq("Which phrase is a firm promise?", "کدام عبارت قول قطعی است؟", ["We should be able to help.", "We can refund you today.", "It might be possible.", "I'll try to ask."], 1,
                    "'We can' states the decision; the others are tentative.", "«We can» تصمیم را می‌گوید و بقیه محتاط‌اند."),
                mcq("'That is the bank's process' means ___.", "«That is the bank's process» یعنی ___.", ["the agent cannot change it", "the bank is closed", "the money is lost", "the agent made a mistake"], 0,
                    "The delay belongs to the bank, not to the agent's choice.", "تأخیر مربوط به بانک است، نه انتخاب کارشناس."),
            ],
        ),
    ],
)

U8 = unit(
    "b1-u8",
    ("Too tired to think", "آن‌قدر خسته که فکر نکنم"),
    ("Say what is worth doing, what is too much and what is enough — then give an opinion out loud.", "بگو چه چیزی ارزش انجام دادن دارد، چه چیزی زیاد و چه چیزی کافی است و بعد نظرت را بلند بگو."),
    [
        lesson(
            "b1-u8-l1",
            "grammar",
            ("Gerunds, infinitives, too, enough, so and such", "اسم مصدر، مصدر، too، enough، so و such"),
            ("Choose -ing or to + verb by the verb before it, and grade with too/enough/so/such.", "بین ing و to + فعل بر اساس فعل قبل انتخاب کن و با too/enough/so/such درجه‌بندی کن."),
            [
                ("Some verbs take -ing: enjoy, avoid, suggest, mind, finish, keep, be worth, look forward to. Some take to + verb: decide, hope, plan, manage, offer, refuse, afford, want. A few take both with a change of meaning: stop smoking / stop to smoke.", "برخی فعل‌ها ing می‌گیرند: enjoy، avoid، suggest، mind، finish، keep، be worth، look forward to. برخی to + فعل: decide، hope، plan، manage، offer، refuse، afford، want. چند تا هر دو را با معنای متفاوت می‌گیرند: stop smoking / stop to smoke."),
                ("After a preposition, always -ing: interested in learning, good at explaining, instead of waiting, before leaving. This is the most common B1 error: 'interested in learn'.", "بعد از حرف اضافه همیشه ing: interested in learning، good at explaining، instead of waiting، before leaving. این رایج‌ترین خطای B1 است: «interested in learn»."),
                ("As a subject, -ing is normal: Learning a language takes time. To + verb as a subject is more formal or abstract: To learn a language is to change how you think.", "به‌عنوان فاعل، ing طبیعی است: Learning a language takes time. مصدر با to رسمی‌تر یا انتزاعی‌تر است: To learn a language is to change how you think."),
                ("Grading: too + adjective + to + verb (too tired to think), adjective + enough + to + verb (old enough to drive), so + adjective + that (so tired that I fell asleep), such + (a) + noun + that (such a long day that…).", "درجه‌بندی: too + صفت + to + فعل (too tired to think)، صفت + enough + to + فعل (old enough to drive)، so + صفت + that (so tired that I fell asleep)، such + اسم + that (such a long day that…)."),
            ],
            [
                ("I'm looking forward to seeing you next week.", "مشتاق دیدن تو در هفتهٔ آینده هستم."),
                ("She suggested taking the earlier train.", "پیشنهاد کرد قطار زودتر را بگیریم."),
                ("It's not worth waiting for a better price.", "ارزش ندارد برای قیمت بهتر صبر کنیم."),
                ("I was too tired to finish the report, so I left it for the morning.", "آن‌قدر خسته بودم که گزارش را تمام نکنم، پس برای صبح گذاشتم."),
                ("It was such a good film that we watched it twice.", "آن‌قدر فیلم خوبی بود که دو بار دیدیمش."),
            ],
            [
                mcq("I'm interested in ___ how languages are learned.", "به ___ اینکه زبان‌ها چطور یاد گرفته می‌شوند علاقه دارم.", ["learn", "learning", "to learn", "learned"], 1,
                    "After a preposition, the -ing form.", "بعد از حرف اضافه شکل ing."),
                mcq("The box was too heavy ___ .", "جعبه آن‌قدر سنگین بود که ___ .", ["to carry", "carrying", "for carry", "carry"], 0,
                    "Too + adjective + to + verb.", "too + صفت + to + فعل."),
            ],
            [
                gap("We decided ___ (take) the night train.", ["to take"], "Decide takes to + verb.", "decide با to + فعل می‌آید."),
                gap("He isn't old ___ to drive yet.", ["enough"], "Adjective + enough + to + verb.", "صفت + enough + to + فعل."),
                mcq("Which is correct?", "کدام درست است؟", ["I enjoy to read.", "I enjoy reading.", "I enjoy read.", "I enjoy for reading."], 1,
                    "Enjoy takes -ing.", "enjoy شکل ing می‌گیرد."),
                listen("I'd love to come, but I'm too tired to drive tonight. Could we meet tomorrow instead?", "Why can't he come?", "چرا نمی‌تواند بیاید؟", ["he is busy", "he is too tired to drive", "he has no car", "he doesn't want to"], 1,
                       "'Too tired to drive tonight.'", "«آن‌قدر خسته که امشب رانندگی نکند»."),
            ],
        ),
        lesson(
            "b1-u8-l2",
            "vocabulary",
            ("Nature, the environment and the choices behind them", "طبیعت، محیط زیست و انتخاب‌های پشت آن"),
            ("Discuss environmental problems and solutions without slogans.", "مشکلات و راه‌حل‌های محیط زیستی را بدون شعار بحث کن."),
            [
                ("The issues: climate change, air and water pollution, waste, deforestation, drought, flooding, energy use, carbon emissions. Countability matters: pollution is uncountable, emissions are plural, a drought is countable.", "مسائل: climate change، pollution، waste، deforestation، drought، flooding، energy use، carbon emissions. شماردنی بودن مهم است: pollution نشماردنی، emissions جمع و a drought شماردنی است."),
                ("Solutions: renewable energy (solar, wind), recycle and reuse, cut emissions, conserve water, plant trees, ban single-use plastic, invest in public transport. The verbs are the argument: cut, conserve, ban, invest.", "راه‌حل‌ها: renewable energy، recycle، reuse، cut emissions، conserve water، plant trees، ban single-use plastic، invest in public transport. فعل‌ها خودشان استدلال‌اند: cut، conserve، ban، invest."),
                ("Cause and consequence: this leads to, it results in, it is caused by, the main reason for. For opinions, hedge: in my view, it seems clear that, I'm not convinced that. Avoid 'everyone knows'.", "علت و پیامد: this leads to، it results in، it is caused by، the main reason for. برای نظر، محتاط باش: in my view، it seems clear that، I'm not convinced that. از «everyone knows» پرهیز کن."),
            ],
            [
                ("Air pollution in the city is caused mainly by old vehicles.", "آلودگی هوای شهر عمدتاً از خودروهای فرسوده می‌آید."),
                ("The council has banned single-use plastic in its buildings.", "شهرداری پلاستیک یک‌بارمصرف را در ساختمان‌هایش ممنوع کرده است."),
                ("Investing in public transport reduces both traffic and emissions.", "سرمایه‌گذاری در حمل‌ونقل عمومی هم ترافیک و هم انتشار را کم می‌کند."),
                ("I'm not convinced that a new road will solve the problem.", "قانع نشده‌ام که یک جادهٔ تازه مشکل را حل کند."),
            ],
            [
                mcq("Energy from the sun and wind is called ___ energy.", "انرژی خورشید و باد ___ نام دارد.", ["renewable", "limited", "heavy", "natural gas"], 0,
                    "Renewable energy replaces itself.", "انرژی تجدیدپذیر خودش را بازمی‌سازد."),
                mcq("'Deforestation' is ___.", "«Deforestation» ___ است.", ["planting trees", "cutting down forests", "burning waste", "cleaning rivers"], 1,
                    "The prefix de- and forest: removing forests.", "پیشوند de و forest: از بین بردن جنگل."),
            ],
            [
                gap("Old cars are the main ___ of air pollution in the city.", ["cause"], "The main cause of a problem.", "the main cause of یک مشکل."),
                gap("We should ___ water in summer, not waste it.", ["conserve", "save"], "Conserve/save water.", "conserve یا save water یعنی در مصرف آب صرفه‌جویی کردن."),
                mcq("Which sentence hedges an opinion?", "کدام جمله نظر را محتاط بیان می‌کند؟", ["Everyone knows recycling is useless.", "It seems clear that recycling alone is not enough.", "Recycling is completely pointless.", "Nobody recycles."], 1,
                    "'It seems clear that' leaves room for discussion.", "«It seems clear that» جا برای بحث می‌گذارد."),
                mcq("Which word is uncountable?", "کدام واژه نشماردنی است؟", ["drought", "emission", "pollution", "flood"], 2,
                    "Pollution has no plural in normal use.", "pollution در کاربرد عادی جمع ندارد."),
            ],
        ),
        lesson(
            "b1-u8-l3",
            "speaking",
            ("Giving an opinion with reasons", "نظر دادن با دلیل"),
            ("State a position, support it, concede a point and answer a follow-up.", "موضعی بگو، پشتیبانی کن، امتیازی بده و به پرسش بعدی پاسخ بده."),
            [
                ("The four moves of a B1 opinion: say what you think (I'd say…), give a reason (because…), give an example (for instance…), concede something (although…). Without the reason and the example, the opinion is only a preference.", "چهار حرکت نظر در B1: بگو چه فکر می‌کنی (I'd say…)، دلیل بده (because…)، مثال بده (for instance…)، امتیازی بده (although…). بدون دلیل و مثال، نظر فقط سلیقه است."),
                ("Hedge and then commit: it depends, but overall… / on the whole… / I'm in two minds, but… Hedging first makes the committed sentence sound considered rather than careless.", "اول محتاط باش و بعد تصمیم بگیر: it depends, but overall… / on the whole… / I'm in two minds, but… محتاط بودن اول باعث می‌شود جملهٔ قطعی سنجیده به نظر برسد."),
                ("Follow-up questions need a real answer, not a repetition: What makes you say that? — I've seen it in my own street. Would you change your mind? — If the numbers showed otherwise, yes.", "پرسش‌های بعدی پاسخ واقعی می‌خواهند، نه تکرار: What makes you say that? — I've seen it in my own street. Would you change your mind? — If the numbers showed otherwise, yes."),
            ],
            [
                ("I'd say cycling is the best way to get around this city, because it's faster than the bus and much cheaper.", "به نظر من دوچرخه بهترین راه رفت‌وآمد در این شهر است، چون از اتوبوس سریع‌تر و بسیار ارزان‌تر است."),
                ("For instance, my trip to work takes twelve minutes by bike and forty by car.", "مثلاً مسیر کار من با دوچرخه دوازده دقیقه و با ماشین چهل دقیقه است."),
                ("Although the air is not clean yet, more people cycle than five years ago.", "هرچند هوا هنوز پاک نیست، بیشتر از پنج سال پیش دوچرخه سوار می‌شوند."),
                ("That's a fair point, but I still think the city needs better bike lanes.", "نکتهٔ درستی است، اما هنوز فکر می‌کنم شهر به مسیر دوچرخهٔ بهتر نیاز دارد."),
            ],
            [
                mcq("Which order makes an opinion convincing?", "کدام ترتیب نظر را قانع‌کننده می‌کند؟", ["opinion, example, reason", "opinion, reason, example", "example only", "reason only"], 1,
                    "Position, then why, then a case in point.", "موضع، بعد دلیل، بعد یک نمونه."),
                mcq("Which reply concedes a point?", "کدام پاسخ امتیازی به طرف مقابل می‌دهد؟", ["You're wrong.", "That's a fair point, but…", "I don't know.", "Everyone agrees with me."], 1,
                    "Conceding before disagreeing keeps the exchange open.", "امتیاز دادن پیش از مخالفت گفت‌وگو را باز نگه می‌دارد."),
            ],
            [
                say("I'm in two minds about it, but on the whole I think it's a good idea.", "دربارهٔ آن دو دلم، اما در کل فکر می‌کنم ایدهٔ خوبی است."),
                say("For example, when the metro opened, my journey became much shorter.", "مثلاً وقتی مترو باز شد، مسیر من بسیار کوتاه‌تر شد."),
                say("What makes you say that?", "چه چیزی باعث می‌شود این را بگویی؟"),
                say("That's a fair point, but I'd still choose the cheaper option.", "نکتهٔ درستی است، اما من باز هم گزینهٔ ارزان‌تر را انتخاب می‌کنم."),
            ],
            dialogue=dialogue([
                ("A", "Do you think the city should ban cars in the centre?", "فکر می‌کنی شهر باید ماشین‌ها را در مرکز ممنوع کند؟"),
                ("B", "On the whole, yes. The air is terrible in summer.", "در کل بله. هوا در تابستان افتضاح است."),
                ("A", "But what about people who work there?", "اما کسانی که آنجا کار می‌کنند چه؟"),
                ("B", "That's a fair point. I'd say deliveries should still be allowed before nine.", "نکتهٔ درستی است. به نظر من تحویل بار تا قبل از نه باید مجاز باشد."),
                ("A", "And would you change your mind if the shops lost customers?", "اگر مغازه‌ها مشتری از دست بدهند نظرت عوض می‌شود؟"),
                ("B", "If the numbers showed that, yes — I'd look at the evidence.", "اگر آمار این را نشان دهد، بله؛ به شواهد نگاه می‌کنم."),
            ]),
        ),
    ],
)
