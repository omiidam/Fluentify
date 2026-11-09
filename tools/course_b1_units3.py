#!/usr/bin/env python3
"""B1 · units 5-6: reporting what was said, and the habits that made us.

Both units end in writing, because both grammar points exist to carry someone
else's words and someone else's past into a text.
"""

from course_kit import gap, lesson, listen, mcq, passage, unit, write

U5 = unit(
    "b1-u5",
    ("She said she would", "گفت که می‌آید"),
    ("Pass on what someone said, and write the email that changes a plan politely.", "حرف کسی را بازگو کن و ایمیلی بنویس که با احترام برنامه را عوض می‌کند."),
    [
        lesson(
            "b1-u5-l1",
            "grammar",
            ("Reported speech and indirect questions", "نقل قول غیرمستقیم و پرسش‌های غیرمستقیم"),
            ("Report a statement or a question without quoting it word for word.", "گزاره یا پرسشی را بدون نقل کلمه‌به‌کلمه بازگو کن."),
            [
                ("When the reporting verb is past (said, told me), the tense usually moves back one step: 'I'm tired' → She said she was tired. 'I'll call you' → She said she would call me. 'I saw him' → She said she had seen him.", "وقتی فعل نقل گذشته است (said، told me)، زمان معمولاً یک پله عقب می‌رود: «I'm tired» ← She said she was tired. «I'll call you» ← She said she would call me. «I saw him» ← She said she had seen him."),
                ("Pronouns and time words move too: I → she/he, my → her/his, today → that day, tomorrow → the next day, here → there, this → that. The meaning must survive the move, so adjust what needs adjusting: 'Come here tomorrow' → She told me to go there the next day.", "ضمیرها و واژه‌های زمان هم جابه‌جا می‌شوند: I ← she، today ← that day، tomorrow ← the next day، here ← there. معنا باید سالم بماند، پس هر چه لازم است تغییر بده: «Come here tomorrow» ← She told me to go there the next day."),
                ("Say and tell differ: say + clause (she said she was late), tell + person (she told me she was late). Commands become tell + object + to + verb: He told me to wait. Requests are reported with ask: She asked me to send the file.", "say و tell تفاوت دارند: say + جمله (she said she was late) و tell + شخص (she told me she was late). امر به tell + مفعول + to + فعل تبدیل می‌شود: He told me to wait. خواهش با ask نقل می‌شود: She asked me to send the file."),
                ("Indirect questions lose the inversion and the auxiliary: 'Where do you live?' → She asked where I lived. 'Have you finished?' → She asked if I had finished. Yes/no questions take if or whether.", "پرسش غیرمستقیم وارونگی و فعل کمکی را از دست می‌دهد: «Where do you live?» ← She asked where I lived. «Have you finished?» ← She asked if I had finished. پرسش بله/خیر با if یا whether می‌آید."),
            ],
            [
                ("She said she had already sent the report.", "گفت گزارش را قبلاً فرستاده است."),
                ("He told me he would be late because of the traffic.", "به من گفت به‌خاطر ترافیک دیر می‌رسد."),
                ("They asked whether the office was open on Saturday.", "پرسیدند دفتر شنبه باز است یا نه."),
                ("My manager asked me to prepare the figures for Monday.", "مدیرم از من خواست figures را برای دوشنبه آماده کنم."),
                ("She said she was moving to Shiraz the next month.", "گفت ماه بعد به شیراز می‌رود."),
            ],
            [
                mcq("'I'll call you.' → She said she ___ call me.", "جملهٔ «I'll call you» را در نقل قول غیرمستقیم کامل کن: She said she ___ call me.", ["will", "would", "calls", "has"], 1,
                    "Will moves back to would in reported speech.", "will در نقل قول به would تبدیل می‌شود."),
                mcq("'Where do you work?' → He asked me where I ___.", "پرسش «Where do you work?» را غیرمستقیم کن: He asked me where I ___.", ["do work", "work", "worked", "will work"], 2,
                    "Indirect questions drop do and move the tense back: worked.", "پرسش غیرمستقیم do را حذف و زمان را عقب می‌برد: worked."),
            ],
            [
                gap("'I'm waiting for the bus.' → She said she ___ waiting for the bus.", ["was"], "Present continuous becomes past continuous.", "حال استمراری به گذشتهٔ استمراری تبدیل می‌شود."),
                gap("He ___ me to close the window. (tell)", ["told"], "Tell + person + to + verb.", "tell + شخص + to + فعل."),
                mcq("Which is correct?", "کدام درست است؟", ["She asked me where was the station.", "She asked me where the station was.", "She asked me where is the station.", "She asked where was the station to me."], 1,
                    "No inversion in an indirect question.", "پرسش غیرمستقیم وارونگی ندارد."),
                listen("Sara called. She said the meeting has moved to Thursday at ten, and she asked you to bring the sales figures.", "What does Sara want?", "سارا چه می‌خواهد؟", ["a new meeting room", "the sales figures on Thursday", "to cancel the meeting", "a report by Friday"], 1,
                       "She asked for the sales figures at the Thursday meeting.", "او figures را برای جلسهٔ پنجشنبه خواسته است."),
            ],
        ),
        lesson(
            "b1-u5-l2",
            "vocabulary",
            ("Relationships, society and the problems between them", "روابط، جامعه و مشکلات میانشان"),
            ("Discuss people's relationships and social problems with precise, neutral language.", "روابط آدم‌ها و مشکلات اجتماعی را با زبان دقیق و بی‌طرف بحث کن."),
            [
                ("Relationships progress through verbs: get to know, become close, fall out (argue and stop being friendly), make up, drift apart, break up, get back together. 'We fell out over money' names the cause; 'we drifted apart' means no single cause.", "روابط با فعل‌ها پیش می‌روند: get to know، become close، fall out (قهر کردن)، make up، drift apart، break up، get back together. «We fell out over money» علت را می‌گوید؛ «we drifted apart» یعنی علت مشخصی نبود."),
                ("Social issues are named in noun phrases: poverty, inequality, unemployment, discrimination, loneliness, housing costs, an aging population. Discuss them with 'the' for the general problem: the rise in housing costs, not 'a rise of housing costs'.", "مسائل اجتماعی در عبارت‌های اسمی نام می‌گیرند: poverty، inequality، unemployment، discrimination، loneliness، housing costs، an aging population. برای مشکل کلی از the استفاده کن: the rise in housing costs."),
                ("Opinion language stays tentative: it seems to me that, I'd say, there's a tendency to, one reason may be, this is partly because. Strong claims need evidence: research suggests, according to a recent survey.", "زبان نظر محتاط می‌ماند: it seems to me that، I'd say، there's a tendency to، one reason may be، this is partly because. ادعای قوی شواهد می‌خواهد: research suggests، according to a recent survey."),
            ],
            [
                ("They fell out over a small thing and didn't speak for a year.", "بر سر چیز کوچکی قهر کردند و یک سال حرف نزدند."),
                ("Loneliness among older people has become a serious problem in big cities.", "تنهایی سالمندان در شهرهای بزرگ مشکل جدی شده است."),
                ("It seems to me that housing costs are the main reason young people leave.", "به نظر من هزینهٔ مسکن دلیل اصلی رفتن جوانان است."),
                ("According to a recent survey, half of the workers feel undervalued.", "بر اساس یک نظرسنجی تازه، نیمی از کارکنان احساس می‌کنند ارزششان دیده نمی‌شود."),
            ],
            [
                mcq("To argue and stop speaking is to ___.", "دعوا کردن و قطع رابطه ___ است.", ["make up", "fall out", "drift apart", "get on"], 1,
                    "Fall out means to quarrel and stop being friendly.", "fall out یعنی دعوا و قهر."),
                mcq("Which is the neutral, careful phrase?", "کدام عبارت خنثی و محتاط است؟", ["Everyone knows that…", "It seems to me that…", "It is obvious that…", "Nobody can deny that…"], 1,
                    "Tentative phrasing leaves room for other views.", "عبارت محتاط جا برای نظر دیگر باز می‌گذارد."),
            ],
            [
                gap("After ten years they simply ___ apart and stopped calling.", ["drifted"], "Drift apart: grow distant slowly.", "drift apart: آهسته دور شدن."),
                gap("The report looks at ___ among young people in the city. (the problem of being alone)", ["loneliness"], "Loneliness is the noun of lonely.", "loneliness اسم lonely است."),
                mcq("'They made up' means ___.", "«They made up» یعنی ___.", ["they invented a story", "they became friendly again", "they broke up", "they moved away"], 1,
                    "Make up after a quarrel means to reconcile.", "make up بعد از قهر یعنی آشتی کردن."),
                mcq("Which collocation is correct?", "کدام هم‌نشینی درست است؟", ["make a survey", "carry out a survey", "do a survey research", "take a survey out"], 1,
                    "You carry out or conduct a survey.", "survey را carry out یا conduct می‌کنند."),
            ],
        ),
        lesson(
            "b1-u5-l3",
            "writing",
            ("The email that changes a plan", "ایمیل تغییر برنامه"),
            ("Postpone, decline and renegotiate in writing without sounding rude.", "به تعویق انداختن، رد کردن و دوباره توافق کردن را مکتوب و بی‌بی‌ادبی انجام بده."),
            [
                ("Bad news needs four moves: acknowledge the arrangement, give the reason briefly, apologize once, offer an alternative. An apology repeated three times weakens the email; a solution strengthens it.", "خبر بد چهار حرکت دارد: قرار را یادآوری کن، دلیل را کوتاه بگو، یک بار عذرخواهی کن و جایگزین پیشنهاد بده. عذرخواهی سه‌باره ایمیل را ضعیف و راه‌حل آن را قوی می‌کند."),
                ("Formal register: I'm afraid, unfortunately, due to, I would like to, would it be possible to, I appreciate. Informal: sorry, I can't make it, can we move it? Use I'm afraid to soften, not to hide: I'm afraid I can't make Friday.", "لحن رسمی: I'm afraid، unfortunately، due to، I would like to، would it be possible to، I appreciate. غیررسمی: sorry، I can't make it، can we move it? از I'm afraid برای نرم کردن استفاده کن، نه پنهان کردن: I'm afraid I can't make Friday."),
                ("Linking devices give the email its logic: however, therefore, as a result, in addition, on the other hand. One per paragraph is enough; three in a sentence is a style problem.", "واژه‌های ربط منطق ایمیل را می‌سازند: however، therefore، as a result، in addition، on the other hand. در هر پاراگراف یکی کافی است؛ سه تا در یک جمله مشکل سبکی است."),
            ],
            [
                ("I'm afraid I can't make Friday at three — could we move it to Monday morning?", "متأسفانه جمعه ساعت سه نمی‌توانم؛ می‌شود به دوشنبه صبح موکول کنیم؟"),
                ("Due to a family matter, I will not be able to attend the training on Tuesday.", "به دلیل مسئلهٔ خانوادگی، سه‌شنبه نمی‌توانم در آموزش شرکت کنم."),
                ("Thank you for your patience; I appreciate you changing the date at short notice.", "ممنون از صبرت؛ ممنون که با اطلاع کوتاه تاریخ را عوض کردی."),
                ("Unfortunately the figures are not ready. However, I can send a summary today.", "متأسفانه figures آماده نیست. با این حال می‌توانم امروز خلاصه‌ای بفرستم."),
            ],
            [
                mcq("Which opening is appropriately soft in a formal email?", "کدام شروع در ایمیل رسمی به‌درستی نرم است؟", ["I can't come.", "I'm afraid I won't be able to attend.", "I will not come.", "No."], 1,
                    "I'm afraid + won't be able to is the standard softening.", "I'm afraid + won't be able to شکل استاندارد نرم‌سازی است."),
                mcq("What should follow the apology?", "بعد از عذرخواهی چه باید بیاید؟", ["another apology", "an explanation of the whole week", "an alternative", "nothing"], 2,
                    "An alternative turns an apology into a solution.", "جایگزین عذرخواهی را به راه‌حل تبدیل می‌کند."),
            ],
            [
                write("Write an email to a colleague. You cannot attend a meeting on Wednesday because of a family matter. Apologize once, explain briefly, propose another time and ask them to send the notes.",
                       "به همکاری ایمیل بنویس. به‌دلیل مسئلهٔ خانوادگی نمی‌توانی چهارشنبه در جلسه شرکت کنی. یک بار عذرخواهی کن، کوتاه توضیح بده، زمان دیگری پیشنهاد بده و بخواه صورت‌جلسه را بفرستد.",
                       60, ["afraid", "could"],
                       "Four short paragraphs: the problem, the reason, the alternative, the request. One linking word per paragraph.",
                       "چهار پاراگراف کوتاه: مشکل، دلیل، جایگزین، درخواست. در هر پاراگراف یک واژهٔ ربط."),
                gap("___ to the weather, the flight was canceled.", ["Due"], "Due to + noun introduces a reason.", "due to + اسم دلیل را می‌آورد."),
                mcq("Which sentence is too direct for a formal email?", "کدام جمله برای ایمیل رسمی زیادی مستقیم است؟", ["I'm afraid I can't attend.", "Unfortunately I won't be able to come.", "I can't come.", "Would it be possible to meet on Monday?"], 2,
                    "Bare 'I can't come' has no softening.", "«I can't come» هیچ نرم‌کننده‌ای ندارد."),
            ],
        ),
    ],
)

U6 = unit(
    "b1-u6",
    ("We used to walk", "قبلاً پیاده می‌رفتیم"),
    ("Talk about habits that have ended, and write a review of a place you know well.", "دربارهٔ عادت‌هایی که تمام شده‌اند حرف بزن و نقد جایی را که خوب می‌شناسی بنویس."),
    [
        lesson(
            "b1-u6-l1",
            "grammar",
            ("Used to, would and the habits that stopped", "used to، would و عادت‌هایی که تمام شدند"),
            ("Separate a past habit, a past state and a single past event.", "عادت گذشته، وضعیت گذشته و رویداد تکی گذشته را از هم جدا کن."),
            [
                ("Used to + plain verb describes a habit or a state in the past that is no longer true: I used to walk to school. There used to be a bakery here. The negative is didn't use to (no -d) and the question Did you use to…?", "used to + فعل ساده عادت یا وضعیتی در گذشته را می‌گوید که دیگر نیست: I used to walk to school. There used to be a bakery here. منفی آن didn't use to (بدون d) و پرسش Did you use to…? است."),
                ("Would + verb can also describe a repeated past action, but only actions, never states: every summer we would swim in the river (habit) — but not 'there would be a bakery here' for a state. When in doubt, used to works for both.", "would + فعل هم می‌تواند عمل تکراری گذشته را بگوید، اما فقط عمل، نه وضعیت: every summer we would swim in the river، اما برای وضعیت نه. در شک، used to برای هر دو کار می‌کند."),
                ("For a single finished event, neither is possible: I went to Isfahan last year, not 'I used to go to Isfahan last year' (which means repeatedly).", "برای رویداد تکی تمام‌شده هیچ‌کدام به کار نمی‌رود: I went to Isfahan last year، نه «I used to go…» که یعنی مکرر."),
                ("Be used to + -ing is a different structure: it means accustomed to. I'm used to getting up early. Don't confuse it with I used to get up early (I did, and now I don't).", "be used to + ing ساختاری متفاوت است: یعنی عادت داشتن به. I'm used to getting up early. آن را با I used to get up early (قبلاً میکردم و الان نه) اشتباه نگیر."),
            ],
            [
                ("We used to spend every summer at my grandmother's house.", "هر تابستان را در خانهٔ مادربزرگم می‌گذراندیم."),
                ("There used to be a movie theater on this street, but it closed years ago.", "قبلاً در این خیابان سینمایی بود، اما سال‌ها پیش بسته شد."),
                ("Did you use to play football when you were a child?", "وقتی بچه بودی فوتبال بازی می‌کردی؟"),
                ("She would read to us every night before we slept.", "هر شب قبل از خواب برایمان کتاب می‌خواند."),
                ("I'm used to working in a noisy office now.", "الان به کار در دفتر شلوغ عادت کرده‌ام."),
            ],
            [
                mcq("There ___ a bakery on this corner when I was a child.", "وقتی بچه بودم در این نبش ___ نانوایی بود.", ["used to be", "used to have", "would be", "was used to be"], 0,
                    "A past state takes used to be; would cannot describe a state.", "وضعیت گذشته used to be می‌گیرد؛ would وضعیت را نمی‌گوید."),
                mcq("I ___ get up at five, but now I start work at ten.", "قبلاً ساعت پنج بیدار می‌شدم، اما الان کارم ده شروع می‌شود.", ["am used to", "used to", "use to", "would used to"], 1,
                    "A finished habit: used to + plain verb.", "عادت تمام‌شده: used to + فعل ساده."),
            ],
            [
                gap("He ___ (not / use) to like coffee, but now he drinks three cups a day.", ["didn't use", "did not use"], "Negative: didn't use to, without -d.", "منفی: didn't use to، بدون d."),
                gap("I'm used to ___ (work) with children, so the noise doesn't bother me.", ["working"], "Be used to + -ing.", "ساختار be used to یعنی به چیزی عادت داشتن و با ing می‌آید."),
                mcq("Which sentence is wrong?", "کدام جمله غلط است؟", ["I used to live in Rasht.", "There used to be a shop here.", "I would live in Rasht.", "We would go to the sea every July."], 2,
                    "Would cannot describe a past state like living somewhere.", "would وضعیت گذشته مثل زندگی کردن در جایی را نمی‌گوید."),
                listen("Before the metro opened, I used to leave home at six and get to work at eight. Now it takes twenty-five minutes.", "How did the journey change?", "مسیر چطور عوض شد؟", ["it is longer now", "it is much shorter now", "it is the same", "he stopped working"], 1,
                       "Two hours before, twenty-five minutes now.", "قبلاً دو ساعت و الان بیست‌وپنج دقیقه."),
            ],
        ),
        lesson(
            "b1-u6-l2",
            "vocabulary",
            ("Health, lifestyle and the habits that help", "سلامت، سبک زندگی و عادت‌های کمک‌کننده"),
            ("Discuss wellbeing with the collocations doctors and articles actually use.", "سلامت را با هم‌نشینی‌هایی بحث کن که پزشکان و مقاله‌ها واقعاً به کار می‌برند."),
            [
                ("Habits take specific verbs: take up a sport, give up smoking, cut down on sugar, stick to a routine, keep fit, get enough sleep. 'Cut down on' is reduction, not stopping.", "عادت‌ها فعل مشخص می‌گیرند: take up a sport، give up smoking، cut down on sugar، stick to a routine، keep fit، get enough sleep. «cut down on» کاهش است، نه توقف."),
                ("Health nouns: a condition (a long-term problem), symptoms, treatment, a check-up, a balanced diet, mental health, stress levels, life expectancy. 'I'm on medication' means you take it regularly.", "اسم‌های سلامت: condition (مشکل بلندمدت)، symptoms، treatment، check-up، balanced diet، mental health، stress levels، life expectancy. «I'm on medication» یعنی مرتب دارو مصرف می‌کنی."),
                ("Cause and effect in health writing: this can lead to, it increases the risk of, it contributes to, it helps prevent. Avoid 'it makes healthy' — the verb needs its object: it helps you stay healthy.", "علت و اثر در نوشتار سلامت: this can lead to، it increases the risk of، it contributes to، it helps prevent. از «it makes healthy» پرهیز کن؛ فعل مفعول می‌خواهد: it helps you stay healthy."),
            ],
            [
                ("I've cut down on coffee and I sleep much better.", "مصرف قهوه را کم کرده‌ام و خیلی بهتر می‌خوابم."),
                ("Walking to work every day helps me keep fit without a gym.", "هر روز پیاده رفتن به کار کمک می‌کند بدون باشگاه تناسب اندام داشته باشم."),
                ("Long working hours can lead to serious stress.", "ساعت‌های طولانی کار می‌تواند به استرس جدی بینجامد."),
                ("She's on medication for her blood pressure and has a check-up every year.", "برای فشار خونش دارو مصرف می‌کند و هر سال آزمایش می‌دهد."),
            ],
            [
                mcq("To stop a habit completely is to ___ it ___.", "کاملاً کنار گذاشتن یک عادت ___ است.", ["cut / down", "give / up", "take / up", "keep / on"], 1,
                    "Give up = stop completely; cut down = reduce.", "give up یعنی کاملاً ترک کردن و cut down یعنی کم کردن."),
                mcq("A regular medical examination is a ___.", "معاینهٔ پزشکی منظم ___ است.", ["treatment", "check-up", "condition", "symptom"], 1,
                    "A check-up checks your health.", "check-up سلامتت را بررسی می‌کند."),
            ],
            [
                gap("He ___ up smoking two years ago and hasn't touched a cigarette since.", ["gave"], "Give up, past simple gave.", "give up و گذشتهٔ آن gave."),
                gap("Sugar can ___ to weight problems if you eat too much.", ["lead", "contribute"], "Lead/contribute to + noun.", "lead/contribute to + اسم."),
                mcq("'A balanced diet' means ___.", "«A balanced diet» یعنی ___.", ["eating only vegetables", "eating the right amounts of different foods", "eating twice a day", "a diet to lose weight fast"], 1,
                    "Balance is about proportion, not restriction.", "تعادل دربارهٔ تناسب است، نه محدودیت."),
                mcq("Which collocation is correct?", "کدام هم‌نشینی درست است؟", ["do exercise regularly", "take exercise regularly", "get exercise regularly", "make exercise regularly"], 0,
                    "In British English you do exercise; both do and get are used, but 'do exercise' is standard.", "در انگلیسی بریتانیایی do exercise استاندارد است."),
            ],
        ),
        lesson(
            "b1-u6-l3",
            "writing",
            ("A review of a place", "نقد یک مکان"),
            ("Recommend a place with a clear structure: what it is, what is good, what is not, who it suits.", "جایی را با ساختاری روشن توصیه کن: چیست، چه خوب است، چه نه، به چه کسی می‌خورد."),
            [
                ("A review is an opinion with evidence. Name the place and the occasion, give two concrete details (a price, a dish, a wait), one honest criticism, and a recommendation for a specific kind of visitor.", "نقد نظری است با شاهد. مکان و موقعیت را نام ببر، دو جزئیات مشخص بده (قیمت، غذا، مدت انتظار)، یک نقد صادقانه و توصیه‌ای برای نوع خاصی از بازدیدکننده."),
                ("Keep the tenses consistent: present for what the place is like (the staff are friendly), past for your visit (we waited twenty minutes).", "زمان‌ها را یکدست نگه دار: حال برای ویژگی مکان (the staff are friendly) و گذشته برای بازدیدت (we waited twenty minutes)."),
                ("Use the vocabulary of unit 4: worth a visit, overpriced, generous portions, a bit noisy, I'd go back. One superlative and one comparative are enough — more turns a review into advertising.", "واژگان درس ۴ را به کار ببر: worth a visit، overpriced، generous portions، a bit noisy، I'd go back. یک صفت برترین و یک برتر کافی است؛ بیشتر از آن نقد را تبلیغ می‌کند."),
            ],
            [
                ("We went on a Friday evening and waited twenty minutes for a table.", "جمعه شب رفتیم و بیست دقیقه برای میز صبر کردیم."),
                ("The portions are generous and the bread is worth the trip alone.", "پرس‌ها پرحجم‌اند و نانش به‌تنهایی ارزش سفر دارد."),
                ("It's a bit noisy, so it's better for friends than for a quiet dinner.", "کمی شلوغ است، پس برای دوستان بهتر از شام آرام است."),
                ("I'd go back, but I'd book first.", "دوباره می‌روم، اما اول رزرو می‌کنم."),
            ],
            [
                mcq("Which detail makes a review convincing?", "کدام جزئیات نقد را قانع‌کننده می‌کند؟", ["it was nice", "we waited twenty minutes for a table", "everyone should go", "it is a restaurant"], 1,
                    "A concrete detail is evidence; 'nice' is only a verdict.", "جزئیات مشخص شاهد است؛ «nice» فقط داوری است."),
                mcq("Which tense describes the place in general?", "کدام زمان مکان را به‌طور کلی توصیف می‌کند؟", ["past simple", "present simple", "present perfect", "future"], 1,
                    "General descriptions sit in the present.", "توصیف کلی در حال است."),
            ],
            [
                write("Write a review of a café, restaurant or park you know well. Say where it is, describe two things you liked with concrete details, name one problem, and recommend it to a particular kind of visitor.",
                       "نقد کافه، رستوران یا پارکی را که خوب می‌شناسی بنویس. بگو کجاست، دو چیز را که دوست داشتی با جزئیات مشخص توصیف کن، یک مشکل را بگو و آن را به نوع خاصی از بازدیدکننده توصیه کن.",
                       60, ["worth", "although"],
                       "Four short paragraphs; present for description, past for your visit; finish with a clear recommendation.",
                       "چهار پاراگراف کوتاه؛ حال برای توصیف و گذشته برای بازدیدت؛ با یک توصیهٔ روشن تمام کن."),
                gap("The museum is ___ a visit, even if you only have an hour.", ["worth"], "Worth + noun or -ing.", "worth + اسم یا ing."),
                mcq("Which sentence is a fair criticism?", "کدام جمله نقد منصفانه است؟", ["The food was terrible and the staff were awful.", "The food was good, although the music was too loud.", "Everything was perfect.", "I don't like restaurants."], 1,
                    "Balanced praise and one specific limitation.", "تعریف متعادل با یک محدودیت مشخص."),
            ],
        ),
    ],
)
