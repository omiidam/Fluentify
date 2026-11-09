#!/usr/bin/env python3
"""A2 · units 1-2: the past simple and the past continuous.

The first half of A2 takes the learner from naming things (A1) to telling what
happened: finished events with a time, then a longer action interrupted by a
shorter one, with the travel vocabulary and the station announcement that make
those forms useful outside the classroom.
"""

from course_kit import T, dialogue, gap, lesson, listen, mcq, passage, say, unit, write

U1 = unit(
    "a2-u1",
    ("What happened", "چه شد"),
    ("Tell a finished story in the past simple, and keep in touch with people.", "داستان تمام‌شده‌ای را با گذشتهٔ ساده تعریف کن و با آدم‌ها در ارتباط بمان."),
    [
        lesson(
            "a2-u1-l1",
            "grammar",
            ("Past simple: regular and irregular verbs", "گذشتهٔ ساده: افعال باقاعده و بی‌قاعده"),
            ("Say what happened at a finished time, and ask about it.", "بگو در زمانی تمام‌شده چه شد و درباره‌اش بپرس."),
            [
                ("The past simple is for something finished: I worked, she called, we went. The form is the same for every person, so nothing changes after he or they.", "گذشتهٔ ساده برای کاری تمام‌شده است: I worked، she called، we went. شکل فعل برای همهٔ شخص‌ها یکی است، پس بعد از he یا they چیزی عوض نمی‌شود."),
                ("Regular verbs add -ed: work → worked, play → played, visit → visited. Verbs ending in a consonant + y change y to i: study → studied, carry → carried.", "افعال باقاعده ـed می‌گیرند: work ← worked، play ← played، visit ← visited. افعالی که به صامت + y ختم می‌شوند y را به i تبدیل می‌کنند: study ← studied."),
                ("Irregular verbs have their own past form, and there is no rule to guess it: go → went, buy → bought, see → saw, have → had, meet → met, take → took. Learn them in a sentence, not in a list.", "افعال بی‌قاعده شکل گذشتهٔ خودشان را دارند و قاعده‌ای برای حدس آن نیست: go ← went، buy ← bought، see ← saw، have ← had. آن‌ها را در جمله یاد بگیر، نه در فهرست."),
                ("Negatives and questions use did, and the main verb goes back to its plain form: I didn't go. Did you see him? Not 'Did you saw'.", "منفی و پرسشی با did ساخته می‌شود و فعل اصلی به شکل ساده برمی‌گردد: I didn't go. Did you see him? نه «Did you saw»."),
            ],
            [
                ("I visited my grandmother on Friday and we talked for two hours.", "جمعه به دیدن مادربزرگم رفتم و دو ساعت با هم حرف زدیم."),
                ("She bought a second-hand bicycle last month.", "ماه گذشته یک دوچرخهٔ دست‌دوم خرید."),
                ("We didn't take the bus because it was late.", "با اتوبوس نرفتیم، چون دیر کرده بود."),
                ("Did you finish the report before the meeting?", "گزارش را قبل از جلسه تمام کردی؟"),
                ("He studied in Shiraz and then moved to Tehran.", "در شیراز درس خواند و بعد به تهران رفت."),
            ],
            [
                mcq("We ___ to the market on Saturday morning.", "شنبه صبح به بازار ___.", ["goed", "go", "went", "gone"], 2,
                    "The time is finished (Saturday), so the past simple is 'went'; 'goed' is not a word.", "زمان تمام شده است (شنبه)، پس گذشتهٔ ساده «went» است؛ «goed» واژه نیست."),
                mcq("___ you finish the report last night?", "دیشب گزارش را ___ کردی؟", ["Did", "Do", "Was", "Have"], 0,
                    "Questions about a finished past event start with Did + plain verb.", "پرسش دربارهٔ رویدادی تمام‌شده با Did + فعل ساده شروع می‌شود."),
            ],
            [
                gap("I ___ (visit) my aunt last night.", ["visited"], "visit + -ed, and the time is finished.", "visit + ـed، و زمان تمام شده است."),
                gap("She ___ (buy) a new phone on Monday.", ["bought"], "buy is irregular: buy → bought.", "buy بی‌قاعده است: buy ← bought."),
                gap("We ___ (not / go) to the party because I had a headache.", ["didn't go", "did not go"], "Negative past simple: didn't + plain verb.", "منفی گذشتهٔ ساده: didn't + فعل ساده."),
                mcq("Which sentence is correct?", "کدام جمله درست است؟", ["He didn't went home.", "He didn't go home.", "He not went home.", "He doesn't went home."], 1,
                    "After didn't the verb has no past ending: didn't go.", "بعد از didn't فعل پایانهٔ گذشته نمی‌گیرد: didn't go."),
            ],
        ),
        lesson(
            "a2-u1-l2",
            "vocabulary",
            ("People and the things that happened to them", "آدم‌ها و چیزهایی که برایشان رخ داد"),
            ("Talk about family, friends and colleagues, and about the events that connect them.", "دربارهٔ خانواده، دوستان و همکاران و رویدادهایی که آن‌ها را به هم وصل می‌کند حرف بزن."),
            [
                ("Family and friends are described by how they are connected to you: a cousin is the child of your aunt or uncle, a colleague works with you, a neighbor lives next door, and your partner is the person you share your life with.", "خویشاوندان با نسبتشان با تو توصیف می‌شوند: cousin فرزند عمه یا عمو است، colleague همکارت است، neighbor همسایهٔ بغلی است و partner کسی است که زندگی‌ات را با او شریک می‌شوی."),
                ("Life events are told with the past simple: I met my wife in college. We moved to Tehran in 2019. I grew up in a small town near Isfahan.", "رویدادهای زندگی با گذشتهٔ ساده گفته می‌شوند: I met my wife in college. We moved to Tehran in 2019. I grew up in a small town."),
                ("Learn the verb that belongs with each noun, not the noun alone: get married, fall in love, keep in touch, lose touch, be close to someone, get to know someone. We keep in touch *with* a friend; we do not 'keep relation'.", "فعلی را یاد بگیر که با هر اسم می‌آید، نه اسم را تنها: get married، fall in love، keep in touch، lose touch، be close to someone، get to know someone. با دوست keep in touch with می‌گوییم."),
            ],
            [
                ("My cousin lives in Tabriz, but we keep in touch every week.", "پسرخاله‌ام در تبریز زندگی می‌کند، اما هر هفته با هم در تماسیم."),
                ("I met my best friend at school and we grew up together.", "بهترین دوستم را در مدرسه دیدم و با هم بزرگ شدیم."),
                ("My colleague helped me a lot when I started this job.", "همکارم وقتی این کار را شروع کردم خیلی کمکم کرد."),
                ("They fell in love in 2018 and got married two years later.", "سال ۲۰۱۸ عاشق هم شدند و دو سال بعد ازدواج کردند."),
            ],
            [
                mcq("Your aunt's son is your ___.", "پسر خاله‌ات ___ تو است.", ["colleague", "neighbor", "cousin", "partner"], 2,
                    "The child of your aunt or uncle is your cousin.", "فرزند عمه، خاله، عمو یا دایی، cousin است."),
                mcq("Which is the natural phrase?", "کدام عبارت طبیعی است؟", ["keep relation with a friend", "keep in touch with a friend", "keep touching a friend", "keep contact of a friend"], 1,
                    "The fixed phrase is keep in touch with someone.", "عبارت ثابت keep in touch with somebody است."),
            ],
            [
                gap("We ___ in touch after college, but only by message.", ["kept"], "keep in touch, past simple kept.", "keep in touch و گذشتهٔ آن kept است."),
                gap("My brother and his wife ___ married last spring.", ["got"], "get married → got married.", "get married و گذشتهٔ آن got married است."),
                mcq("Choose the word for someone you work with.", "واژه‌ای را انتخاب کن که یعنی کسی که با او کار می‌کنی.", ["neighbor", "colleague", "cousin", "partner"], 1,
                    "A colleague is a person you work with.", "colleague کسی است که با او کار می‌کنی."),
                mcq("'I grew up in Rasht' means ___.", "«I grew up in Rasht» یعنی ___.", ["I moved to Rasht", "I spent my childhood in Rasht", "I visited Rasht", "I worked in Rasht"], 1,
                    "Grow up is about childhood, not a single visit.", "grow up دربارهٔ کودکی است، نه یک دیدار کوتاه."),
            ],
        ),
        lesson(
            "a2-u1-l3",
            "reading",
            ("A message from Lisbon", "پیامی از لیسبون"),
            ("Read a short personal message and find what happened, when, and how the writer felt.", "پیام کوتاه شخصی را بخوان و بفهم چه شد، کِی و نویسنده چه حسی داشت."),
            [
                ("A personal message usually moves through time: it says where the writer is now, what happened before, and what comes next. Read once for the story and once for the details.", "پیام شخصی معمولاً در زمان حرکت می‌کند: می‌گوید نویسنده الان کجاست، قبلاً چه شد و بعد چه می‌شود. یک بار برای داستان بخوان و یک بار برای جزئیات."),
                ("Past time words carry the story: on Friday, yesterday, last night. Future words promise what follows: tomorrow, next week, I'll send.", "واژه‌های زمان گذشته داستان را پیش می‌برند: on Friday، yesterday، last night. واژه‌های آینده وعدهٔ ادامه را می‌دهند: tomorrow، next week، I'll send."),
            ],
            [
                ("Message: 'Hi Sara, we arrived on Friday and the apartment is small but lovely.'", "پیام: «سلام سارا، جمعه رسیدیم و آپارتمان کوچک است اما دوست‌داشتنی»."),
                ("'Yesterday it rained, so we stayed in and cooked.'", "«دیروز باران آمد، پس خانه ماندیم و غذا پختیم»."),
                ("'I'll send photos when we're back.'", "«وقتی برگشتیم عکس می‌فرستم»."),
            ],
            [
                mcq("When did they arrive?", "کِی رسیدند؟", ["on Thursday", "on Friday", "on Saturday", "yesterday"], 1,
                    "The message says 'we arrived on Friday'.", "پیام می‌گوید «we arrived on Friday»."),
                mcq("What did they do when it rained?", "وقتی باران آمد چه کردند؟", ["they went to the castle", "they took a train", "they stayed in and cooked", "they went shopping"], 2,
                    "'Yesterday it rained, so we stayed in and cooked.'", "«دیروز باران آمد، پس خانه ماندیم و غذا پختیم»."),
            ],
            [
                mcq("What did they do on Saturday?", "شنبه چه کردند؟", ["they cooked at home", "they walked up to the castle", "they took the train to Sintra", "they stayed in bed"], 1,
                    "'On Saturday we walked up to the castle.'", "«شنبه تا قلعه پیاده رفتیم»."),
                mcq("Why do her legs hurt?", "چرا پاهایش درد می‌کند؟", ["because of the rain", "because of the long walk up to the castle", "because she cooked all day", "because the apartment is small"], 1,
                    "She walked up to the castle and says her legs still hurt.", "تا قلعه پیاده رفت و می‌گوید پاهایش هنوز درد می‌کند."),
                mcq("What is she going to do tomorrow?", "فردا چه کار می‌کند؟", ["cook at home", "take the train to Sintra", "rain", "arrive in Lisbon"], 1,
                    "'Tomorrow we're going to take the train to Sintra.'", "«فردا با قطار به سینترا می‌رویم»."),
                mcq("How does she feel about the apartment?", "دربارهٔ آپارتمان چه حسی دارد؟", ["she hates it", "she thinks it is small but lovely", "she thinks it is too expensive", "she has not seen it"], 1,
                    "'The apartment is small but lovely.'", "«آپارتمان کوچک است اما دوست‌داشتنی»."),
            ],
            passage=passage(("A message from Lisbon", "پیامی از لیسبون"),
                            ("Hi Sara,\n\nWe arrived on Friday and the apartment is small but lovely. On Saturday we walked up to the castle — the view was amazing, but my legs still hurt! Yesterday it rained, so we stayed in and cooked. Tomorrow we're going to take the train to Sintra.\n\nI'll send photos when we're back.\n\nLove,\nMina",
                             "سلام سارا،\n\nجمعه رسیدیم و آپارتمان کوچک است اما دوست‌داشتنی. شنبه تا قلعه پیاده رفتیم؛ منظره فوق‌العاده بود، اما پاهایم هنوز درد می‌کند! دیروز باران آمد، پس خانه ماندیم و غذا پختیم. فردا با قطار به سینترا می‌رویم.\n\nوقتی برگشتیم عکس می‌فرستم.\n\nبا عشق،\nمینا")),
        ),
    ],
)

U2 = unit(
    "a2-u2",
    ("While it was happening", "وقتی داشت اتفاق می‌افتاد"),
    ("Describe an action in progress and the short event that interrupted it.", "کاری را که در جریان بود و رویداد کوتاهی که آن را قطع کرد توصیف کن."),
    [
        lesson(
            "a2-u2-l1",
            "grammar",
            ("Past continuous, and past simple together", "گذشتهٔ استمراری همراه گذشتهٔ ساده"),
            ("Set the scene with was/were + -ing, then say what happened.", "صحنه را با was/were + ing بساز و بعد بگو چه شد."),
            [
                ("The past continuous shows an action in progress at a moment in the past: at eight I was cooking. Form: was/were + verb-ing. Use was with I, he, she, it and were with you, we, they.", "گذشتهٔ استمراری کاری را نشان می‌دهد که در لحظه‌ای در گذشته در جریان بود: at eight I was cooking. ساختار: was/were + فعل ing‌دار. با I/he/she/it از was و با you/we/they از were استفاده کن."),
                ("It is the background of a story. The longer action is continuous and the short event is simple: I was walking home when I saw Reza. She was cooking when the phone rang.", "این زمان پس‌زمینهٔ داستان است. کار طولانی استمراری و رویداد کوتاه ساده است: I was walking home when I saw Reza. She was cooking when the phone rang."),
                ("While is followed by the continuous, when usually by the simple: While I was waiting, the bus came. Two continuous actions can run side by side: I was cooking while she was studying.", "بعد از while معمولاً گذشتهٔ استمراری و بعد از when گذشتهٔ ساده می‌آید: While I was waiting, the bus came. دو کار استمراری هم می‌توانند هم‌زمان باشند: I was cooking while she was studying."),
            ],
            [
                ("At seven o'clock I was still working on the report.", "ساعت هفت هنوز روی گزارش کار می‌کردم."),
                ("We were waiting at the bus stop when it started to rain.", "در ایستگاه اتوبوس منتظر بودیم که باران شروع شد."),
                ("While she was talking, her phone rang twice.", "وقتی داشت حرف می‌زد، تلفنش دو بار زنگ خورد."),
                ("They weren't listening, so they missed the announcement.", "گوش نمی‌دادند، پس اطلاعیه را از دست دادند."),
                ("What were you doing at ten last night?", "دیشب ساعت ده چه کار می‌کردی؟"),
            ],
            [
                mcq("I ___ dinner when the lights went out.", "داشتم شام می‌پختم که برق رفت.", ["cooked", "was cooking", "were cooking", "cook"], 1,
                    "The long background action takes the past continuous: I was cooking.", "کار طولانی پس‌زمینه گذشتهٔ استمراری می‌گیرد: I was cooking."),
                mcq("___ you waiting outside when I called?", "وقتی زنگ زدم بیرون منتظر ___ بودی؟", ["Was", "Were", "Did", "Do"], 1,
                    "With you the past continuous uses were.", "با you گذشتهٔ استمراری از were استفاده می‌کند."),
            ],
            [
                gap("While I ___ (wait) for the bus, I saw my old teacher.", ["was waiting"], "Long background action: was + waiting.", "کار طولانی پس‌زمینه: was + waiting."),
                gap("They ___ (not / listen) when the guide explained the route.", ["weren't listening", "were not listening"], "Plural subject, negative: weren't + -ing.", "فاعل جمع، منفی: weren't + ing."),
                mcq("Which sentence sounds natural?", "کدام جمله طبیعی است؟", ["While I was walking, I was seeing a friend.", "While I was walking home, I saw a friend.", "While I walked home, I was seeing a friend.", "While I walking home, I saw a friend."], 1,
                    "Background continuous + short event in the past simple.", "پس‌زمینهٔ استمراری + رویداد کوتاه با گذشتهٔ ساده."),
                listen("I was making tea when you called, so I didn't hear the phone at first.", "Why didn't she hear the phone?", "چرا صدای تلفن را نشنید؟", ["she was out", "she was making tea", "the phone was broken", "she was asleep"], 1,
                       "She was making tea when the call came.", "وقتی تماس رسید داشت چای درست می‌کرد."),
            ],
        ),
        lesson(
            "a2-u2-l2",
            "vocabulary",
            ("Traveling: from the ticket to the platform", "سفر: از بلیت تا سکو"),
            ("Use the phrasal verbs and fixed phrases of a journey, and follow directions.", "فعل‌های عبارتی و عبارت‌های ثابت سفر را به کار ببر و مسیر را دنبال کن."),
            [
                ("A journey is a chain of small actions, and each one has its own verb: set off (leave), get on / get off a bus or train, check in at a hotel or airport, book a ticket, miss a connection.", "سفر زنجیره‌ای از کارهای کوچک است و هر کدام فعل خودش را دارد: set off (راه افتادن)، get on / get off (سوار/پیاده شدن)، check in (پذیرش)، book a ticket (بلیت گرفتن)، miss a connection (از دست دادن پرواز یا قطار بعدی)."),
                ("Problems travel with you: the car broke down, we ran out of gas, the flight was delayed, I left my bag on the train. Notice that broke down and ran out of keep their particle.", "مشکل‌ها هم همراهت سفر می‌کنند: the car broke down، we ran out of gas، the flight was delayed، I left my bag on the train. توجه کن که broke down و ran out of ذرهٔ خود را نگه می‌دارند."),
                ("Directions: go straight on, turn left at the lights, take the second turning, it's opposite the bank, it's next to the station. Opposite means facing it; next to means beside it.", "مسیر: go straight on، turn left at the lights، take the second turning، it's opposite the bank، it's next to the station. opposite یعنی روبه‌روی آن و next to یعنی کنار آن."),
            ],
            [
                ("We set off at six to avoid the traffic.", "برای فرار از ترافیک ساعت شش راه افتادیم."),
                ("You need to check in two hours before the flight.", "باید دو ساعت قبل از پرواز پذیرش کنی."),
                ("The car broke down halfway, so we took a taxi.", "ماشین وسط راه خراب شد، پس تاکسی گرفتیم."),
                ("Go straight on and take the second turning on your left; the hotel is opposite the post office.", "مستقیم برو و دومین کوچهٔ دست چپ را بگیر؛ هتل روبه‌روی ادارهٔ پست است."),
            ],
            [
                mcq("'We set off at six' means we ___.", "«We set off at six» یعنی ___ .", ["arrived at six", "left at six", "slept at six", "booked at six", ], 1,
                    "Set off means to start a journey.", "set off یعنی سفر را آغاز کردن."),
                mcq("The opposite of 'get on the train' is ___.", "متضاد «get on the train» ___ است.", ["get in the train", "get off the train", "get out the train", "go on the train"], 1,
                    "You get on and get off a train.", "با قطار get on و get off می‌گوییم."),
            ],
            [
                gap("We ___ out of gas outside Yazd and had to walk.", ["ran"], "run out of → ran out of.", "run out of و گذشتهٔ آن ran out of است."),
                gap("Please ___ in at the desk before you go to the gate.", ["check"], "check in at the desk.", "در پذیرش هتل یا فرودگاه check in می‌گوییم."),
                mcq("The bank is ___ the supermarket — they face each other across the road.", "بانک ___ سوپرمارکت است؛ روبه‌روی هم در دو طرف خیابان.", ["next to", "opposite", "behind", "inside"], 1,
                    "Opposite means facing something across a street or space.", "opposite یعنی روبه‌رو در آن سوی خیابان یا فضا."),
                listen("Your train leaves from platform four at ten fifteen, and please keep your bags with you.", "Which platform does the train leave from?", "قطار از کدام سکو حرکت می‌کند؟", ["one", "two", "four", "fourteen"], 2,
                       "The announcement says platform four.", "اطلاعیه می‌گوید platform four."),
            ],
        ),
        lesson(
            "a2-u2-l3",
            "listening",
            ("At the station", "در ایستگاه"),
            ("Follow announcements and a short platform conversation, and pick out times, platforms and changes.", "اطلاعیه‌ها و گفت‌وگوی کوتاه سکو را دنبال کن و ساعت، سکو و تغییرها را پیدا کن."),
            [
                ("Station announcements are formula: which train, from where, at what time, and what has changed. The change is the part you need: delayed, canceled, platform three instead of five.", "اطلاعیه‌های ایستگاه قالبی‌اند: کدام قطار، از کجا، چه ساعتی و چه چیزی عوض شده است. همان تغییر، بخشی است که لازم داری: delayed، canceled، platform three instead of five."),
                ("Numbers are the hard part: half past, quarter to, ten fifteen, twenty past six. Listen for the hour first, then the minutes, and check the platform against the one on your ticket.", "سخت‌ترین بخش عددها هستند: half past، quarter to، ten fifteen، twenty past six. اول ساعت را بشنو، بعد دقیقه‌ها را و سکو را با سکوی بلیتت مقایسه کن."),
            ],
            [
                ("'The 9:40 to Kashan is delayed by twenty minutes.'", "«قطار ۹:۴۰ به کاشان بیست دقیقه تأخیر دارد»."),
                ("'Passengers for Qom should go to platform two.'", "«مسافران قم به سکوی دو بروند»."),
                ("'This train is canceled. Please take the next service.'", "«این قطار لغو شده است. لطفاً با قطار بعدی بروید»."),
            ],
            [
                listen("The nine forty to Kashan is delayed by twenty minutes. It will now leave at ten o'clock from platform two.", "When does the train leave now?", "قطار حالا چه ساعتی حرکت می‌کند؟", ["9:40", "9:55", "10:00", "10:20"], 2,
                       "Twenty minutes after 9:40 is 10:00.", "بیست دقیقه بعد از ۹:۴۰ ساعت ۱۰:۰۰ است."),
                listen("The nine forty to Kashan is delayed by twenty minutes. It will now leave at ten o'clock from platform two.", "Which platform should passengers use?", "مسافران از کدام سکو استفاده کنند؟", ["one", "two", "four", "nine"], 1,
                       "The announcement says platform two.", "اطلاعیه می‌گوید platform two."),
            ],
            [
                listen("Excuse me, is this the train to Qom? — No, this one goes to Qom only on Fridays. Today you need platform five.", "What does the traveler learn?", "مسافر چه چیزی می‌فهمد؟", ["the train is canceled", "this train does not go to Qom today", "the station is closed", "the train is late"], 1,
                       "This train goes to Qom only on Fridays, so today he needs another platform.", "این قطار فقط جمعه‌ها به قم می‌رود، پس امروز سکوی دیگری لازم است."),
                listen("Your ticket is for the 6:15, but the 6:15 is full. You can take the 6:45 instead at no extra cost.", "What can the passenger do?", "مسافر چه کاری می‌تواند بکند؟", ["buy a new ticket", "take the 6:45 for the same price", "get a refund only", "wait until tomorrow"], 1,
                       "The 6:45 is offered at no extra cost.", "قطار ۶:۴۵ بدون هزینهٔ اضافه پیشنهاد می‌شود."),
                listen("We are now arriving at Isfahan. Please take all your bags with you and mind the step.", "What should passengers do?", "مسافران چه کار باید بکنند؟", ["change trains", "take their bags and mind the step", "buy tickets", "wait on the platform"], 1,
                       "The announcement asks them to take their bags and mind the step.", "اطلاعیه می‌خواهد چمدان‌ها را بردارند و مراقب پله باشند."),
                mcq("A 'connection' is ___.", "«connection» یعنی ___.", ["the ticket office", "the next train you change to", "the platform", "a delay"], 1,
                    "A connection is the train, bus or flight you change to on the way.", "connection قطار، اتوبوس یا پروازی است که در راه عوض می‌کنی."),
            ],
        ),
    ],
)
