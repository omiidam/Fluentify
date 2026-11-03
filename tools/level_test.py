#!/usr/bin/env python3
"""The monthly level check: an item bank, not a story.

Five sections, one per skill area, and 42 questions in total:

    Use of English   15   grammar and vocabulary, three per CEFR band
    Reading          10   three passages, questions banded with them
    Listening         9   short spoken texts, played by the device's own voice
    Writing           4   prompts, each rated against a four-point rubric
    Speaking          4   prompts, each rated against the same kind of rubric

The design follows what placement tests actually do rather than what looks
impressive. Items are banded (A1 to C1) instead of shuffled, because the
score has to say *where* the learner stopped, not just how many they got
right. A band counts as passed at two thirds of its items, a skill's level is
the highest band passed after every lower band, and the overall level is the
median of the five skills - which is why one weak skill cannot drag a strong
reader down and one lucky section cannot lift them up.

Writing and speaking cannot be marked without a human or a model, so they are
marked by the learner against a rubric that names what each score looks like.
Every result screen says so. What the app must not do is pretend a typed
paragraph was graded.

The English is written for this project, as are the Persian lines, the
explanations and the rubric. The band descriptions paraphrase the CEFR's own
can-do statements in plain English.
"""


def L(en, fa):
    return {"en": en, "fa": fa}


def Q(band, stem_en, stem_fa, options, answer, why_en, why_fa):
    return {
        "band": band,
        "stem": L(stem_en, stem_fa),
        "options": options,
        "answer": answer,
        "why": L(why_en, why_fa),
    }


def RQ(passage, band, stem_en, stem_fa, options, answer, why_en, why_fa):
    """A reading question, tied to the passage it belongs to."""
    item = Q(band, stem_en, stem_fa, options, answer, why_en, why_fa)
    item["passage"] = passage
    return item


BANDS = [
    {"id": "A1", "name": L("Beginner", "مبتدی"),
     "can": L("You handle greetings, numbers, prices and very short sentences "
              "about yourself.",
              "سلام و احوال‌پرسی، عدد، قیمت و جمله‌های خیلی کوتاه دربارهٔ خودت "
              "را می‌فهمی و می‌گویی.")},
    {"id": "A2", "name": L("Elementary", "پایه"),
     "can": L("You manage shopping, travel and simple messages about everyday "
              "things.",
              "خرید، سفر و پیام‌های سادهٔ کارهای روزمره را از عهده برمی‌آیی.")},
    {"id": "B1", "name": L("Intermediate", "میانی"),
     "can": L("You follow the main point of a news story and hold a conversation "
              "about plans and opinions.",
              "نکتهٔ اصلی یک خبر را می‌گیری و دربارهٔ برنامه‌ها و نظرها گفت‌وگو "
              "می‌کنی.")},
    {"id": "B2", "name": L("Upper intermediate", "میانی بالا"),
     "can": L("You read an article quickly, argue a position and understand most "
              "films without subtitles.",
              "مقاله را سریع می‌خوانی، از موضعت دفاع می‌کنی و بیشتر فیلم‌ها را "
              "بی‌زیرنویس می‌فهمی.")},
    {"id": "C1", "name": L("Advanced", "پیشرفته"),
     "can": L("You use English flexibly at work and in study, and you notice "
              "register and nuance.",
              "انگلیسی را در کار و تحصیل منعطف به کار می‌بری و تفاوت لحن و "
              "ظرافت‌ها را می‌بینی.")},
]

SECTIONS = [
    {
        "id": "use",
        "kind": "mcq",
        "title": L("Use of English", "کاربرد زبان"),
        "instructions": L("Choose the one word or phrase that completes the sentence.",
                          "واژه یا عبارتی را انتخاب کن که جمله را کامل می‌کند."),
        "items": [
            Q("A1", "My sister ___ in a small apartment near the station.",
              "خواهرم در آپارتمانی کوچک نزدیک ایستگاه ___ می‌کند.",
              ["lives", "live", "living", "is live"], 0,
              "Third person singular takes -s: my sister lives.",
              "سوم‌شخص مفرد s می‌گیرد: my sister lives."),
            Q("A1", "There ___ two apples on the table.",
              "روی میز دو سیب ___.",
              ["is", "are", "be", "been"], 1,
              "'Two apples' is plural, so the verb is are.",
              "«two apples» جمع است، پس فعل are می‌شود."),
            Q("A1", "I go to work ___ bus every morning.",
              "هر صبح با اتوبوس به سر کار می‌روم.",
              ["in", "on", "by", "with"], 2,
              "By + transport, with no article: by bus, by train.",
              "برای وسیلهٔ نقلیه by می‌آید و حرف تعریف ندارد: by bus."),
            Q("A2", "We ___ to the cinema last night.",
              "دیشب به سینما ___.",
              ["go", "went", "gone", "going"], 1,
              "'Last night' needs the past simple: went.",
              "«last night» گذشتهٔ ساده می‌خواهد: went."),
            Q("A2", "This bag is ___ than that one.",
              "این کیف از آن یکی ___ است.",
              ["heavy", "more heavy", "heaviest", "heavier"], 3,
              "Short adjectives take -er before than: heavier.",
              "صفت کوتاه پیش از than پسوند er می‌گیرد: heavier."),
            Q("A2", "Have you ___ your homework yet?",
              "هنوز تکلیفت را ___‌ای؟",
              ["finished", "finish", "finishing", "to finish"], 0,
              "Present perfect is have + past participle: have finished.",
              "حال کامل یعنی have + اسم مفعول: have finished."),
            Q("B1", "She ___ in this city since 2015.",
              "او از ۲۰۱۵ در این شهر ___.",
              ["lives", "lived", "has lived", "is living"], 2,
              "Since marks a period that continues, so present perfect.",
              "since دوره‌ای را نشان می‌دهد که ادامه دارد، پس حال کامل."),
            Q("B1", "If it rains tomorrow, we ___ at home.",
              "اگر فردا باران ببارد، در خانه ___.",
              ["stay", "stayed", "will stay", "would stay"], 2,
              "First conditional: if + present, will + verb.",
              "شرطی نوع اول: if + حال، will + فعل."),
            Q("B1", "He asked me where I ___ from.",
              "از من پرسید اهل ___ هستم.",
              ["come", "came", "am coming", "have come"], 1,
              "Reported speech moves the question back one tense.",
              "در نقل قول، زمان جمله یک پله به عقب می‌رود."),
            Q("B2", "The manager insisted that the meeting ___ postponed.",
              "مدیر اصرار کرد که جلسه ___.",
              ["is", "be", "was", "will be"], 1,
              "Insist that takes the subjunctive: insisted that it be.",
              "insist that حالت التزامی می‌خواهد: insisted that it be."),
            Q("B2", "Hardly had we sat down ___ the phone rang.",
              "به‌سختی نشسته بودیم که تلفن زنگ زد.",
              ["than", "then", "when", "that"], 2,
              "Hardly ... when is a fixed pair, with inversion after hardly.",
              "hardly با when جفت ثابت است و پس از hardly جای فعل و فاعل "
              "عوض می‌شود."),
            Q("B2", "She is used to ___ up at six.",
              "او به بیدار شدن ساعت شش عادت کرده است.",
              ["get", "getting", "got", "gets"], 1,
              "Be used to takes an -ing form; used to + verb is a past habit.",
              "be used to با فعل ing می‌آید؛ used to + فعل عادت گذشته است."),
            Q("C1", "Rarely ___ such confidence in a newcomer.",
              "به‌ندرت در تازه‌واردی چنین اعتمادبه‌نفسی ___.",
              ["we have seen", "have we seen", "we saw", "saw we"], 1,
              "A fronted negative adverb forces inversion: rarely have we seen.",
              "قید منفی در آغاز جمله جای فعل و فاعل را عوض می‌کند: "
              "rarely have we seen."),
            Q("C1", "Had we known about the closure, we ___ another route.",
              "اگر از بسته بودن جاده خبر داشتیم، راه دیگری ___.",
              ["would take", "would have taken", "had taken", "took"], 1,
              "Third conditional: had + past participle, would have + participle.",
              "شرطی نوع سوم: had + اسم مفعول، would have + اسم مفعول."),
            Q("C1", "The scheme drew ___ criticism from local residents.",
              "این طرح خرده‌گیری ___ از سوی ساکنان محلی برانگیخت.",
              ["broad", "wide", "widespread", "spread"], 2,
              "Widespread is the collocation for criticism over an area or group.",
              "برای خرده‌گیری گسترده در میان گروهی، widespread ترکیب درست است."),
        ],
    },
    {
        "id": "reading",
        "kind": "reading",
        "title": L("Reading", "خواندن"),
        "instructions": L("Read each text and answer the questions on it. You can "
                          "go back to the text at any time.",
                          "هر متن را بخوان و به پرسش‌هایش پاسخ بده. هر وقت "
                          "خواستی می‌توانی به متن برگردی."),
        "passages": [
            {
                "id": "sara",
                "band": "A1",
                "title": L("Sara's Friday", "جمعه‌های سارا"),
                "text": L("My name is Sara. I live in a small town. I have one "
                          "brother. He is ten. On Fridays we go to my "
                          "grandmother's house. She makes bread for us.",
                          "نام من سارا است. در شهر کوچکی زندگی می‌کنم. یک برادر "
                          "دارم. او ده سال دارد. جمعه‌ها به خانهٔ مادربزرگم "
                          "می‌رویم. او برای ما نان می‌پزد."),
            },
            {
                "id": "garden",
                "band": "A2",
                "title": L("The garden on Mill Street", "باغ خیابان میل"),
                "text": L("Mill Street had no garden until last spring. A group of "
                          "neighbours asked the city for the empty land behind the "
                          "old school, and the city said yes. On the first Saturday "
                          "in April, twenty people came with spades and seeds. "
                          "By July there were tomatoes, beans and a lot of "
                          "sunflowers. The garden is open every day from eight in "
                          "the morning until sunset, and nobody has to pay. "
                          "There is only one rule: if you pick something, you must "
                          "water something.",
                          "خیابان میل تا بهار گذشته باغی نداشت. گروهی از همسایه‌ها "
                          "از شهرداری زمین خالی پشت مدرسهٔ قدیمی را خواستند و "
                          "شهرداری موافقت کرد. نخستین شنبهٔ آوریل، بیست نفر با "
                          "بیل و دانه آمدند. تا جولای گوجه، لوبیا و کلی گل "
                          "آفتابگردان بود. باغ هر روز از ساعت هشت صبح تا غروب "
                          "آفتاب باز است و کسی لازم نیست پول بدهد. فقط یک قانون "
                          "دارد: اگر چیزی می‌چینی، باید چیزی را آب بدهی."),
            },
            {
                "id": "course",
                "band": "B1",
                "title": L("A letter about a course", "نامه‌ای دربارهٔ یک دوره"),
                "text": L("Dear Ms Farhadi, thank you for your interest in our "
                          "evening course in bookkeeping. The course runs for ten "
                          "weeks, on Tuesdays and Thursdays, from 6.30 to 8.30. "
                          "Because we have had more applications than places, we "
                          "ask everyone to take a short test in the first week; "
                          "this is only to make sure the group starts at the same "
                          "level, and it does not affect the fee. The fee is 240 "
                          "pounds, which covers the workbook but not the exam. "
                          "If you decide not to continue after the first two "
                          "sessions, we will return all but 40 pounds. Please "
                          "confirm your place by Friday, 12 September, as we "
                          "cannot hold it after that date.",
                          "خانم فرهادی عزیز، از علاقهٔ شما به دورهٔ عصرِ حسابداری "
                          "سپاسگزاریم. دوره ده هفته است، سه‌شنبه‌ها و "
                          "پنجشنبه‌ها، از ۶:۳۰ تا ۸:۳۰. چون متقاضی بیش از ظرفیت "
                          "بوده، از همه می‌خواهیم هفتهٔ اول آزمون کوتاهی بدهند؛ "
                          "این آزمون فقط برای هم‌سطح شدن گروه است و بر شهریه "
                          "اثری ندارد. شهریه ۲۴۰ پوند است که کتاب کار را شامل "
                          "می‌شود اما آزمون را نه. اگر پس از دو جلسهٔ اول "
                          "بخواهید ادامه ندهید، همهٔ پول جز ۴۰ پوند بازگردانده "
                          "می‌شود. لطفاً تا جمعه ۱۲ سپتامبر جای خود را تأیید "
                          "کنید، چون بعد از آن تاریخ نمی‌توانیم نگه داریم."),
            },
            {
                "id": "names",
                "band": "B2",
                "title": L("Why we forget names", "چرا نام‌ها را فراموش می‌کنیم"),
                "text": L("Forgetting a name two seconds after hearing it is not a "
                          "failure of memory so much as a failure of attention. "
                          "When we meet someone, most of us are busy deciding what "
                          "to say next, and a name is the least interesting thing "
                          "in the exchange; the brain, which is economical to a "
                          "fault, simply does not file it. The fix is not to try "
                          "harder but to do something with the name within a few "
                          "seconds: repeat it aloud, connect it to someone you "
                          "already know, or write it down. Experiments on name "
                          "learning suggest that the act of producing the word "
                          "matters far more than hearing it again, which is why "
                          "silently repeating a name to yourself is close to "
                          "useless. Curiously, the same pattern holds for "
                          "vocabulary in a second language: recognition feels "
                          "like knowledge and is not.",
                          "فراموش کردن نامی دو ثانیه پس از شنیدنش، بیشتر از آنکه "
                          "نقص حافظه باشد، نقص توجه است. وقتی کسی را می‌بینیم، "
                          "بیشترمان مشغول تصمیم‌گیری دربارهٔ حرف بعدی‌مان "
                          "هستیم و نام کم‌جالب‌ترین چیز آن گفت‌وگوست؛ مغز هم که "
                          "به‌شدت صرفه‌جو است، اصلاً آن را بایگانی نمی‌کند. راه "
                          "حل، تلاش بیشتر نیست، بلکه انجام کاری با نام در همان "
                          "چند ثانیه است: بلند تکرارش کن، به کسی که می‌شناسی "
                          "وصلش کن، یا بنویسش. آزمایش‌ها نشان می‌دهد نفسِ "
                          "برزبان‌آوردن واژه بسیار مهم‌تر از شنیدن دوبارهٔ آن "
                          "است، و همین است که تکرار بی‌صدا در ذهن تقریباً "
                          "بی‌فایده است. جالب اینکه در واژگان زبان دوم هم همین "
                          "الگو برقرار است: آشنا به نظر رسیدن، شبیه دانستن است "
                          "و دانستن نیست."),
            },
        ],
        "items": [
            RQ("sara", "A1", "Where does Sara live?",
              "سارا کجا زندگی می‌کند؟",
              ["In a big city", "In a small town", "Near her school", "With her grandmother"],
              1, "She says she lives in a small town.",
              "می‌گوید در شهر کوچکی زندگی می‌کند."),
            RQ("sara", "A1", "When do they visit their grandmother?",
              "چه زمانی به دیدن مادربزرگ می‌روند؟",
              ["On Mondays", "Every day", "On Fridays", "In summer"],
              2, "Fridays is the day named for the visit.",
              "جمعه‌ها روزی است که برای این دیدار گفته شده."),
            RQ("sara", "A1", "Who makes the bread?",
              "چه کسی نان می‌پزد؟",
              ["Sara", "Her brother", "Her mother", "Her grandmother"],
              3, "The last sentence says her grandmother makes it.",
              "جملهٔ آخر می‌گوید مادربزرگش نان می‌پزد."),
            RQ("garden", "A2", "Who asked the city for the land?",
              "چه کسی زمین را از شهرداری خواست؟",
              ["The old school", "A group of neighbours", "The city", "A shop"],
              1, "The neighbours asked, and the city agreed.",
              "همسایه‌ها خواستند و شهرداری موافقت کرد."),
            RQ("garden", "A2", "When is the garden open?",
              "باغ چه زمانی باز است؟",
              ["Only on Saturdays", "Every day until sunset",
               "From eight until noon", "Only in spring"],
              0, "It opens at eight and closes at sunset, every day.",
              "هر روز از هشت باز می‌شود و هنگام غروب بسته می‌شود."),
            RQ("garden", "A2", "What must you do if you pick something?",
              "اگر چیزی بچینی چه باید بکنی؟",
              ["Pay at the gate", "Tell the city", "Water something", "Leave a seed"],
              2, "One rule: pick something, water something.",
              "یک قانون: چیزی بچین، چیزی را آب بده."),
            RQ("course", "B1", "How often does the course meet?",
              "دوره چند بار در هفته برگزار می‌شود؟",
              ["Once a week", "Twice a week", "Every evening", "Ten times in total"],
              1, "Tuesdays and Thursdays, for ten weeks.",
              "سه‌شنبه‌ها و پنجشنبه‌ها، به مدت ده هفته."),
            RQ("course", "B1", "Why is there a test in the first week?",
              "چرا هفتهٔ اول آزمون گرفته می‌شود؟",
              ["To choose the best students", "To set the price",
               "To start the group at one level", "To replace the exam"],
              2, "The letter says it is only to level the group.",
              "نامه می‌گوید فقط برای هم‌سطح کردن گروه است."),
            RQ("course", "B1", "What does the fee not include?",
              "شهریه شامل چه چیزی نیست؟",
              ["The workbook", "The exam", "The first two sessions", "The test"],
              1, "It covers the workbook but not the exam.",
              "کتاب کار را شامل می‌شود اما آزمون را نه."),
            RQ("names", "B2", "What is the writer's main claim about forgetting names?",
              "ادعای اصلی نویسنده دربارهٔ فراموش کردن نام‌ها چیست؟",
              ["It shows a weak memory", "It comes from not paying attention",
               "It happens more with age", "It cannot be improved"],
              1, "The first sentence calls it a failure of attention.",
              "جملهٔ اول آن را نقص توجه می‌نامد."),
            RQ("names", "B2", "According to the text, what helps most?",
              "به گفتهٔ متن، چه چیزی بیشترین کمک را می‌کند؟",
              ["Hearing the name again", "Repeating it silently",
               "Saying it and using it", "Writing it hours later"],
              2, "Producing the word matters more than hearing it.",
              "برزبان آوردن واژه مهم‌تر از شنیدن دوبارهٔ آن است."),
            RQ("names", "B2", "Why does the writer mention second-language vocabulary?",
              "چرا نویسنده واژگان زبان دوم را مثال می‌آورد؟",
              ["To show the same pattern elsewhere", "To recommend a course",
               "To disagree with the experiments", "To explain memory loss"],
              0, "The same gap between recognition and knowledge.",
              "همان فاصله میان آشنا بودن و دانستن."),
            RQ("names", "B2", "The word 'economical' in the text is closest in meaning to",
              "واژهٔ «economical» در متن نزدیک‌ترین معنا به کدام است؟",
              ["careful with effort", "cheap to run", "well organised", "short of space"],
              0, "It saves effort, which is why the name is not stored.",
              "در تلاش صرفه‌جویی می‌کند و به همین دلیل نام بایگانی نمی‌شود."),
            RQ("names", "C1", "The writer's tone in the last clause is best described as",
              "لحن نویسنده در بند آخر را چگونه می‌توان توصیف کرد؟",
              ["wry", "indignant", "purely technical", "enthusiastic"], 0,
              "The dry aside 'and is not' is a wry observation, not anger.",
              "کنایهٔ خشک «and is not» لحنی طنزآمیز است، نه خشم."),
            RQ("names", "C1", "Which sentence best summarises the passage?",
              "کدام جمله بهترین خلاصهٔ متن است؟",
              ["Memory is weaker than we think.", "Attention, not storage, is the problem.",
               "Names matter less than faces.", "Experiments disagree with each other."],
              1, "The passage argues the name was never attended to, not that memory failed.",
              "متن می‌گوید نام هرگز مورد توجه قرار نگرفته، نه اینکه حافظه ضعیف بوده."),
        ],
    },
    {
        "id": "listening",
        "kind": "listening",
        "title": L("Listening", "شنیدن"),
        "instructions": L("Press play, listen once, and answer. You may play it a "
                          "second time. The transcript is there if you need it, "
                          "but try without it first.",
                          "دکمهٔ پخش را بزن، یک بار گوش کن و پاسخ بده. می‌توانی "
                          "بار دوم هم بشنوی. اگر لازم شد متن گفتار هم هست، اما "
                          "اول بی آن امتحان کن."),
        "items": [
            {"band": "A1",
             "say": "The shop opens at nine and closes at six.",
             "stem": L("What time does the shop open?", "مغازه چه ساعتی باز می‌شود؟"),
             "options": ["Six", "Seven", "Nine", "Ten"],
             "answer": 2,
             "why": L("'Opens at nine' - six is when it closes.",
                      "«opens at nine»؛ شش ساعت بسته شدن است.")},
            {"band": "A1",
             "say": "My brother has two cats and a dog.",
             "stem": L("How many cats does the brother have?",
                       "برادرش چند گربه دارد؟"),
             "options": ["One", "Two", "Three", "Four"],
             "answer": 1,
             "why": L("Two cats; the dog is a third animal, not a third cat.",
                      "دو گربه؛ سگ حیوان سوم است، نه گربهٔ سوم.")},
            {"band": "A1",
             "say": "Please close the window. It's very cold in here.",
             "stem": L("What should be closed?", "چه چیزی باید بسته شود؟"),
             "options": ["The door", "The window", "The shop", "The box"],
             "answer": 1,
             "why": L("The speaker asks for the window to be closed.",
                      "گوینده می‌خواهد پنجره بسته شود.")},
            {"band": "A2",
             "say": "The train to Bristol leaves from platform four at ten past six.",
             "stem": L("Which platform does the Bristol train leave from?",
                       "قطار بریستول از کدام سکو حرکت می‌کند؟"),
             "options": ["Platform one", "Platform four", "Platform six", "Platform ten"],
             "answer": 1,
             "why": L("'From platform four' is the answer; the times are a distraction.",
                      "«from platform four» پاسخ است؛ ساعت‌ها حواس‌پرتی‌اند.")},
            {"band": "A2",
             "say": "Could I have a coffee and a cheese sandwich, please?",
             "stem": L("What did the speaker order?",
                       "گوینده چه سفارش داد؟"),
             "options": ["Tea and a sandwich", "Coffee and a sandwich",
                         "Coffee and a cake", "A sandwich only"],
             "answer": 1,
             "why": L("Both items are named: coffee and a cheese sandwich.",
                      "هر دو چیز نام برده می‌شود: قهوه و ساندویچ پنیر.")},
            {"band": "A2",
             "say": "The museum is closed on Mondays, but it opens at nine every other day.",
             "stem": L("When is the museum shut?", "موزه چه زمانی بسته است؟"),
             "options": ["Every morning", "On Mondays", "At nine", "On Sundays"],
             "answer": 1,
             "why": L("'Closed on Mondays' is the only closing time given.",
                      "«closed on Mondays» تنها زمان بسته بودن است.")},
            {"band": "B1",
             "say": "I was going to drive, but the traffic was so bad that I took the train instead.",
             "stem": L("How did the speaker travel?", "گوینده چگونه سفر کرد؟"),
             "options": ["By car", "By train", "By bus", "On foot"],
             "answer": 1,
             "why": L("The plan was the car; what happened was the train.",
                      "قصدش ماشین بود؛ اما با قطار رفت.")},
            {"band": "B1",
             "say": "We've put the meeting back to Thursday because the client is away until Wednesday.",
             "stem": L("Why was the meeting moved?", "چرا جلسه جابه‌جا شد؟"),
             "options": ["The room was busy", "The client was away",
                         "Thursday suited everyone", "The report was late"],
             "answer": 1,
             "why": L("The because-clause gives the reason: the client is away.",
                      "جملهٔ because دلیل را می‌گوید: مشتری در سفر است.")},
            {"band": "B1",
             "say": "The course starts on the fifth, but you need to register by the first.",
             "stem": L("When must you register?", "تا چه زمانی باید ثبت‌نام کنی؟"),
             "options": ["By the first", "On the fifth", "After the fifth", "By the tenth"],
             "answer": 0,
             "why": L("Register by the first, start on the fifth.",
                      "ثبت‌نام تا اول، شروع در پنجم.")},
            {"band": "B2",
             "say": "Had it not been for the delay, we would have missed the announcement entirely.",
             "stem": L("What does the speaker mean?", "منظور گوینده چیست؟"),
             "options": ["The delay caused a problem", "The delay helped them",
                         "They missed the announcement", "There was no delay"],
             "answer": 1,
             "why": L("Without the delay they would have missed it, so it saved them.",
                      "بی تأخیر آن را از دست می‌دادند، پس تأخیر نجاتشان داد.")},
            {"band": "B2",
             "say": "The figures look encouraging, though the board remains cautious about the second quarter.",
             "stem": L("What is the board's attitude?", "نگرش هیئت‌مدیره چیست؟"),
             "options": ["Completely confident", "Quietly doubtful",
                         "Angry about the figures", "Ready to invest more"],
             "answer": 1,
             "why": L("'Encouraging, though ... cautious' is reserved optimism.",
                      "«امیدبخش، اما ... محتاط» خوش‌بینی محتاطانه است.")},
            {"band": "B2",
             "say": "Not until the report was published did anyone realise how serious the problem was.",
             "stem": L("When did people understand the problem?",
                       "مردم چه زمانی مشکل را فهمیدند؟"),
             "options": ["Before the report", "While writing the report",
                         "After the report came out", "When the problem started"],
             "answer": 2,
             "why": L("'Not until ... published' means understanding came afterwards.",
                      "«not until ... published» یعنی درک پس از انتشار آمد.")},
            {"band": "C1",
             "say": "What I find most striking is not that the policy failed, but that nobody was surprised when it did.",
             "stem": L("What is the speaker's main point?", "نکتهٔ اصلی گوینده چیست؟"),
             "options": ["The policy failed unexpectedly", "The failure was widely expected",
                         "Nobody noticed the failure", "The policy was never tested"],
             "answer": 1,
             "why": L("The surprise would have been surprise itself: nobody was.",
                      "جای تعجب این بود که کسی تعجب نکرد.")},
            {"band": "C1",
             "say": "She's every bit as capable as her predecessor, if rather less inclined to say so.",
             "stem": L("What is implied about her?", "دربارهٔ او چه چیزی برداشت می‌شود؟"),
             "options": ["She is less capable but louder", "She is equally capable and modest",
                         "She replaced someone modest", "She talks about her work a lot"],
             "answer": 1,
             "why": L("'Every bit as capable' plus 'less inclined to say so' is ability with modesty.",
                      "«every bit as capable» با «less inclined to say so» یعنی توانایی همراه با فروتنی.")},
            {"band": "C1",
             "say": "You'd have thought a company of that size could afford to answer an email within a week.",
             "stem": L("How does the speaker sound?", "لحن گوینده چگونه است؟"),
             "options": ["Genuinely puzzled", "Mildly sarcastic", "Openly furious", "Completely neutral"],
             "answer": 1,
             "why": L("'You'd have thought' signals a reproach delivered with irony.",
                      "«You'd have thought» سرزنشی است که با طعنه گفته می‌شود.")},
        ],
    },
    {
        "id": "writing",
        "kind": "writing",
        "title": L("Writing", "نوشتن"),
        "instructions": L("Write your answer, then read the four descriptions and "
                          "choose the one that honestly matches what you wrote. "
                          "This section is rated by you, not by the app.",
                          "پاسخ را بنویس، بعد چهار توصیف را بخوان و صادقانه آن "
                          "یکی را انتخاب کن که با نوشته‌ات می‌خواند. این بخش را "
                          "خودت ارزیابی می‌کنی، نه برنامه."),
        "items": [
            {"band": "A2",
             "prompt": L("Write three or four sentences about your usual morning.",
                         "سه یا چهار جمله دربارهٔ صبح‌های معمولت بنویس."),
             "hint": L("Use times, verbs and one thing you always do.",
                       "از ساعت، فعل و یک کار همیشگی استفاده کن."),
             "rubric": [
                 {"points": 1, "text": L("A few words, or one short sentence.",
                                         "چند واژه، یا یک جملهٔ کوتاه.")},
                 {"points": 2, "text": L("Simple sentences, some mistakes, the meaning is clear.",
                                         "جمله‌های ساده با چند اشتباه؛ معنا روشن است.")},
                 {"points": 3, "text": L("Connected sentences with times and details, mostly accurate.",
                                         "جمله‌های پیوسته با ساعت و جزئیات، بیشترشان درست.")},
                 {"points": 4, "text": L("A short paragraph that flows, with varied sentences.",
                                         "بند کوتاهی که روان است و جمله‌های متنوع دارد.")},
             ]},
            {"band": "B1",
             "prompt": L("A friend is coming to your city for two days. Write five or "
                         "six sentences telling them what to see and why.",
                         "دوستی دو روز به شهرت می‌آید. پنج یا شش جمله بنویس که چه "
                         "ببیند و چرا."),
             "hint": L("Give reasons with because, so or which.",
                       "با because، so یا which دلیل بیاور."),
             "rubric": [
                 {"points": 1, "text": L("Short notes rather than sentences.",
                                         "یادداشت‌های کوتاه، نه جمله.")},
                 {"points": 2, "text": L("Simple sentences, reasons are missing or thin.",
                                         "جمله‌های ساده؛ دلیل‌ها نیست یا سطحی است.")},
                 {"points": 3, "text": L("Clear sentences with reasons and some linking words.",
                                         "جمله‌های روشن با دلیل و چند واژهٔ ربط.")},
                 {"points": 4, "text": L("Well organised, natural, with a range of structures.",
                                         "سازمان‌یافته و طبیعی، با تنوع ساختار.")},
             ]},
            {"band": "B2",
             "prompt": L("Some people think phones should be banned in classrooms. "
                         "Write a short paragraph giving your view and one "
                         "counter-argument.",
                         "بعضی می‌گویند گوشی در کلاس باید ممنوع شود. بندی کوتاه "
                         "بنویس با نظر خودت و یک استدلال مخالف."),
             "hint": L("Concede one point, then answer it.",
                       "یک نکته را بپذیر، بعد پاسخش را بده."),
             "rubric": [
                 {"points": 1, "text": L("An opinion without support.",
                                         "نظری بی پشتوانه.")},
                 {"points": 2, "text": L("An opinion with one simple reason.",
                                         "نظر با یک دلیل ساده.")},
                 {"points": 3, "text": L("A position, a counter-argument and a reply.",
                                         "موضع، استدلال مخالف و پاسخ به آن.")},
                 {"points": 4, "text": L("A balanced argument, precise vocabulary, controlled grammar.",
                                         "استدلال متوازن، واژگان دقیق و گرامر کنترل‌شده.")},
             ]},
            {"band": "C1",
             "prompt": L("Describe a decision you made that changed something at "
                         "work or at home, and what you would do differently now.",
                         "تصمیمی را توصیف کن که چیزی را در کار یا خانه عوض کرد و "
                         "حالا چه کار دیگری می‌کردی."),
             "hint": L("Past perfect and would have let you show range.",
                       "گذشتهٔ کامل و would have دامنهٔ زبانی را نشان می‌دهد."),
             "rubric": [
                 {"points": 1, "text": L("The event is hard to follow.",
                                         "دنبال کردن رویداد سخت است.")},
                 {"points": 2, "text": L("The event is clear; the reflection is one short line.",
                                         "رویداد روشن است؛ بازنگری یک جملهٔ کوتاه.")},
                 {"points": 3, "text": L("A clear account and a real reflection, with some complex forms.",
                                         "روایت روشن و بازنگری واقعی، با چند ساختار پیچیده.")},
                 {"points": 4, "text": L("Fluent, precise, well structured, with natural hedging.",
                                         "روان، دقیق و ساختارمند، با احتیاط‌های زبانی طبیعی.")},
             ]},
        ],
    },
    {
        "id": "speaking",
        "kind": "speaking",
        "title": L("Speaking", "گفتن"),
        "instructions": L("Speak each answer aloud for about thirty seconds, then "
                          "rate yourself honestly. Record it on your phone first "
                          "if you want to hear it back.",
                          "هر پاسخ را حدود سی ثانیه بلند بگو، بعد صادقانه خودت را "
                          "ارزیابی کن. اگر خواستی اول با گوشی ضبطش کن و "
                          "گوش بده."),
        "items": [
            {"band": "A2",
             "prompt": L("Introduce yourself: your name, your work or study, and "
                         "one thing you like doing.",
                         "خودت را معرفی کن: نام، کار یا تحصیل، و یک کاری که "
                         "دوست داری."),
             "hint": L("Three short sentences is enough.",
                       "سه جملهٔ کوتاه کافی است."),
             "rubric": [
                 {"points": 1, "text": L("Single words or a broken phrase.",
                                         "واژه‌های تنها یا عبارتی بریده.")},
                 {"points": 2, "text": L("Short sentences with long pauses.",
                                         "جمله‌های کوتاه با مکث‌های طولانی.")},
                 {"points": 3, "text": L("Three clear sentences, understandable throughout.",
                                         "سه جملهٔ روشن و تا آخر قابل فهم.")},
                 {"points": 4, "text": L("Fluent and natural, with a little extra detail.",
                                         "روان و طبیعی، با کمی جزئیات بیشتر.")},
             ]},
            {"band": "B1",
             "prompt": L("Tell me about a trip you enjoyed and why it was good.",
                         "از سفری بگو که خوش گذشت و چرا خوب بود."),
             "hint": L("Past tenses, then a reason.",
                       "زمان گذشته، بعد یک دلیل."),
             "rubric": [
                 {"points": 1, "text": L("A word or two about a trip.",
                                         "یکی دو واژه دربارهٔ سفر.")},
                 {"points": 2, "text": L("The trip is named; details are missing.",
                                         "سفر گفته می‌شود؛ جزئیات نیست.")},
                 {"points": 3, "text": L("A clear story with past tenses and a reason.",
                                         "روایت روشن با گذشته و یک دلیل.")},
                 {"points": 4, "text": L("A developed story that holds attention.",
                                         "روایتی پرورده که توجه را نگه می‌دارد.")},
             ]},
            {"band": "B2",
             "prompt": L("Do you think working from home is better than working in "
                         "an office? Give both sides.",
                         "فکر می‌کنی کار از خانه بهتر از کار در دفتر است؟ هر دو "
                         "طرف را بگو."),
             "hint": L("Signpost both sides before you decide.",
                       "پیش از نتیجه‌گیری، هر دو طرف را نشان بده."),
             "rubric": [
                 {"points": 1, "text": L("One opinion, no development.",
                                         "یک نظر، بی بسط.")},
                 {"points": 2, "text": L("One side only, with a simple reason.",
                                         "فقط یک طرف، با یک دلیل ساده.")},
                 {"points": 3, "text": L("Both sides, then a clear position.",
                                         "هر دو طرف، بعد موضعی روشن.")},
                 {"points": 4, "text": L("Both sides weighed, precise language, natural pace.",
                                         "سنجش هر دو طرف، زبان دقیق و سرعت طبیعی.")},
             ]},
            {"band": "C1",
             "prompt": L("Explain a change in your field or your neighbourhood and "
                         "what it means for ordinary people.",
                         "تغییری در حوزهٔ کاری یا محله‌ات را توضیح بده و بگو برای "
                         "مردم معمولی چه معنایی دارد."),
             "hint": L("Cause, effect and a qualification.",
                       "علت، اثر و یک استثنا."),
             "rubric": [
                 {"points": 1, "text": L("The topic is named but not explained.",
                                         "موضوع گفته می‌شود اما توضیح نه.")},
                 {"points": 2, "text": L("A simple description of the change.",
                                         "توصیفی ساده از تغییر.")},
                 {"points": 3, "text": L("Cause and effect, with an example.",
                                         "علت و اثر، با یک مثال.")},
                 {"points": 4, "text": L("Nuanced, well organised, with qualifying language.",
                                         "ظرافت، سازمان‌یافتگی و زبان احتیاطی.")},
             ]},
        ],
    },
]

LEVEL = {
    "version": 1,
    "title": L("Level check", "سنجش سطح"),
    "blurb": L("Fifty-three questions across grammar, vocabulary, reading, "
               "listening, writing and speaking. About twenty minutes, once a "
               "month.",
               "چهل‌و‌دو پرسش در گرامر، واژگان، خواندن، شنیدن، نوشتن و گفتن. "
               "حدود بیست دقیقه، ماهی یک بار."),
    "minutes": 26,
    "bands": BANDS,
    "sections": SECTIONS,
    "method": L("Each band counts as passed at two thirds of its questions. A "
                "skill is the highest band you passed after every band below "
                "it, and your overall level is the median of the five skills. "
                "Writing and speaking are rated by you against the rubric, and "
                "the result says so.",
                "هر سطح با دو‌سوم پرسش‌هایش قبول می‌شود. سطح هر مهارت، "
                "بالاترین سطحی است که پس از گذراندن همهٔ سطح‌های پایین‌تر "
                "قبول شده باشد، و سطح کلی میانهٔ پنج مهارت است. نوشتن و "
                "گفتن را خودت بر پایهٔ معیارها می‌سنجی و نتیجه همین را "
                "می‌گوید."),
    "retakeDays": 30,
}
