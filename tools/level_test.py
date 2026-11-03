#!/usr/bin/env python3
"""The Fluentify level assessment: a blueprint and a reviewed item bank.

The design follows the four things a placement test needs and a quiz does not:

  1. Every item is described, not just written. Band, skill, subskill,
     difficulty, format, the ability it tests, an explanation, a weight, a
     source and a review status. Without that, a bank cannot be audited.
  2. Six skills are measured separately, and two of them are not measured at
     all. Grammar, vocabulary, reading and listening are marked from answers.
     Writing and speaking are offered as practice with a rubric and reported
     as "not assessed" - a self-rating is not a proficiency score, and the
     report says so instead of averaging one in.
  3. Format varies with the ability: multiple choice, cloze, error
     correction, sentence transformation, word ordering, comprehension and
     listening. Four of those need the learner to produce language, not
     recognise it.
  4. Difficulty is chosen, not fixed. Each skill is asked three questions at a
     time; the band moves only after a whole block, so one lucky or unlucky
     answer cannot move the estimate.

The bank is 60 objective items - three per band per assessed skill - plus four
productive tasks. That is exactly enough for a nine-item adaptive path in each
skill without repeating an item, which is what the blueprint check enforces.
"""


def L(en, fa):
    return {"en": en, "fa": fa}


SKILLS = [
    {"id": "grammar", "assessed": True,
     "title": L("Grammar", "گرامر"),
     "blurb": L("Tenses, conditionals, the passive and sentence structure.",
                "زمان‌ها، شرطی‌ها، مجهول و ساختار جمله.")},
    {"id": "vocabulary", "assessed": True,
     "title": L("Vocabulary", "واژگان"),
     "blurb": L("Word meaning, collocation, phrasal verbs and idioms.",
                "معنای واژه، هم‌نشینی، افعال عبارتی و اصطلاح‌ها.")},
    {"id": "reading", "assessed": True,
     "title": L("Reading", "خواندن"),
     "blurb": L("Main idea, detail, inference and the writer's attitude.",
                "ایدهٔ اصلی، جزئیات، استنباط و نگرش نویسنده.")},
    {"id": "listening", "assessed": True,
     "title": L("Listening", "شنیدن"),
     "blurb": L("Announcements, short exchanges and what the speaker means.",
                "اعلامیه‌ها، گفت‌وگوهای کوتاه و منظور گوینده.")},
    {"id": "writing", "assessed": False,
     "title": L("Writing", "نوشتن"),
     "blurb": L("Practice tasks with a rubric. Not scored into the level.",
                "تمرین با معیار. در سطح محاسبه نمی‌شود.")},
    {"id": "speaking", "assessed": False,
     "title": L("Speaking", "گفتن"),
     "blurb": L("Practice tasks with a rubric. Not scored into the level.",
                "تمرین با معیار. در سطح محاسبه نمی‌شود.")},
]

BANDS = [
    {"id": "PRE", "label": "Pre-A1", "name": L("Starting out", "شروع"),
     "can": L("You recognise greetings, numbers and a few everyday words.",
              "سلام و احوال‌پرسی، عدد و چند واژهٔ روزمره را می‌شناسی.")},
    {"id": "A1", "label": "A1", "name": L("Beginner", "مبتدی"),
     "can": L("You handle greetings, prices and very short sentences about "
              "yourself.",
              "سلام و احوال‌پرسی، قیمت و جمله‌های خیلی کوتاه دربارهٔ خودت را "
              "می‌فهمی و می‌گویی.")},
    {"id": "A2", "label": "A2", "name": L("Elementary", "پایه"),
     "can": L("You manage shopping, travel and simple messages about everyday "
              "things.",
              "خرید، سفر و پیام‌های سادهٔ کارهای روزمره را از عهده برمی‌آیی.")},
    {"id": "B1", "label": "B1", "name": L("Intermediate", "میانی"),
     "can": L("You follow the point of a news story and discuss plans and "
              "opinions.",
              "نکتهٔ اصلی یک خبر را می‌گیری و دربارهٔ برنامه‌ها و نظرها گفت‌وگو "
              "می‌کنی.")},
    {"id": "B2", "label": "B2", "name": L("Upper intermediate", "میانی بالا"),
     "can": L("You read an article quickly, argue a position and follow most "
              "films without subtitles.",
              "مقاله را سریع می‌خوانی، از موضعت دفاع می‌کنی و بیشتر فیلم‌ها را "
              "بی‌زیرنویس می‌فهمی.")},
    {"id": "C1", "label": "C1", "name": L("Advanced", "پیشرفته"),
     "can": L("You use English flexibly at work and in study, and you hear "
              "register and nuance.",
              "انگلیسی را در کار و تحصیل منعطف به کار می‌بری و تفاوت لحن و "
              "ظرافت‌ها را می‌شنوی.")},
    {"id": "C2", "label": "C2", "name": L("Proficient", "تسلط"),
     "can": L("You read and hear almost everything effortlessly and summarise "
              "it precisely.",
              "تقریباً هر چیزی را بی‌زحمت می‌خوانی و می‌شنوی و دقیق خلاصه "
              "می‌کنی.")},
]

# A1..C1 carry items. C2 is described but not tested: three items per band
# cannot separate C1 from C2 honestly, and the report says so rather than
# handing a C1 learner a C2 label on six correct answers.
TESTED = ["A1", "A2", "B1", "B2", "C1"]


def q(qid, skill, band, subskill, kind, ability_en, ability_fa,
      prompt_en, prompt_fa, why_en, why_fa, *, options=None, answer=None,
      accept=None, difficulty="medium", passage=None, say=None, tokens=None,
      weight=1):
    item = {
        "id": qid,
        "skill": skill,
        "band": band,
        "subskill": L(subskill[0], subskill[1]),
        "kind": kind,
        "difficulty": difficulty,
        "ability": L(ability_en, ability_fa),
        "prompt": L(prompt_en, prompt_fa),
        "why": L(why_en, why_fa),
        "weight": weight,
        "source": "Fluentify original",
        "review": "reviewed",
    }
    if options is not None:
        item["options"] = options
        item["answer"] = answer
    if accept is not None:
        item["accept"] = accept
    if passage is not None:
        item["passage"] = passage
    if say is not None:
        item["say"] = say
    if tokens is not None:
        item["tokens"] = tokens
    return item


# ------------------------------------------------------------------ grammar
GRAMMAR = [
    q("g-a1-1", "grammar", "A1", ("Present simple", "حال ساده"), "mcq",
      "Third-person singular agreement", "تطابق سوم‌شخص مفرد",
      "My sister ___ in a small apartment near the station.",
      "خواهرم در آپارتمانی کوچک نزدیک ایستگاه ___ می‌کند.",
      "Third person singular takes -s: my sister lives.",
      "سوم‌شخص مفرد s می‌گیرد: my sister lives.",
      options=["live", "lives", "living", "is live"], answer=1, difficulty="easy"),
    q("g-a1-2", "grammar", "A1", ("There is / are", "ساختار there is / are"), "cloze",
      "Plural agreement with there", "تطابق جمع با there",
      "There ___ two apples on the table.", "روی میز دو سیب ___.",
      "Two apples is plural, so the verb is are.",
      "«two apples» جمع است، پس فعل are می‌شود.",
      accept=["are"], difficulty="easy"),
    q("g-a1-3", "grammar", "A1", ("Word order", "ترتیب واژه"), "order",
      "Building a simple statement", "ساختن جملهٔ ساده",
      "Put the words in order.", "واژه‌ها را مرتب کن.",
      "Subject, verb, then by + transport.",
      "فاعل، فعل، بعد by + وسیلهٔ نقلیه.",
      accept=["i go to work by bus", "i go to work by bus."],
      tokens=["by bus", "go", "I", "to work", "."],
      difficulty="easy"),
    q("g-a2-1", "grammar", "A2", ("Past simple", "گذشتهٔ ساده"), "cloze",
      "Producing a finished past verb", "ساختن فعل گذشتهٔ ساده",
      "We ___ to the cinema last night.", "دیشب به سینما ___.",
      "Last night needs the past simple: went.",
      "«last night» گذشتهٔ ساده می‌خواهد: went.",
      accept=["went"], difficulty="easy"),
    q("g-a2-2", "grammar", "A2", ("Negatives", "منفی‌سازی"), "error",
      "Choosing the correctly formed negative", "انتخاب جملهٔ منفی درست",
      "Which sentence is correct?", "کدام جمله درست است؟",
      "The auxiliary carries the tense, so the main verb stays in the base form.",
      "زمان روی فعل کمکی می‌آید، پس فعل اصلی ساده می‌ماند.",
      options=["She don't like coffee.", "She doesn't likes coffee.",
               "She doesn't like coffee.", "She not like coffee."],
      answer=2),
    q("g-a2-3", "grammar", "A2", ("Comparatives", "صفت تفضیلی"), "cloze",
      "Comparing two things", "مقایسهٔ دو چیز",
      "This bag is ___ than that one. (heavy)", "این کیف از آن یکی ___ است. (heavy)",
      "Short adjectives add -er before than: heavier.",
      "صفت کوتاه پیش از than پسوند er می‌گیرد: heavier.",
      accept=["heavier"]),
    q("g-b1-1", "grammar", "B1", ("Present perfect", "حال کامل"), "order",
      "Building a present perfect statement", "ساختن جملهٔ حال کامل",
      "Put the words in order.", "واژه‌ها را مرتب کن.",
      "Since marks a period that continues, so the present perfect.",
      "since دوره‌ای را نشان می‌دهد که ادامه دارد، پس حال کامل.",
      accept=["she has lived in this city since 2015",
              "she has lived in this city since 2015."],
      tokens=["since 2015", "lived", "She", "in this city", "has"]),
    q("g-b1-2", "grammar", "B1", ("Conditionals", "شرطی‌ها"), "transform",
      "Expressing a condition with unless", "بیان شرط با unless",
      "Rewrite the sentence with unless: If you don't hurry, we will miss the train.",
      "جمله را با unless بازنویسی کن: If you don't hurry, we will miss the train.",
      "Unless already contains the negative, so don't stays out of the clause.",
      "unless خودش منفی را در خود دارد، پس don't در جمله نمی‌آید.",
      accept=["unless you hurry, we will miss the train",
              "unless you hurry we will miss the train",
              "we will miss the train unless you hurry"]),
    q("g-b1-3", "grammar", "B1", ("First conditional", "شرطی نوع اول"), "cloze",
      "A real future condition", "شرط واقعی در آینده",
      "If it rains tomorrow, we ___ at home.", "اگر فردا باران ببارد، در خانه ___.",
      "First conditional: if + present, will + base verb.",
      "شرطی نوع اول: if + حال، will + فعل ساده.",
      accept=["will stay", "'ll stay", "will stay."]),
    q("g-b2-1", "grammar", "B2", ("Subjunctive", "التزامی"), "mcq",
      "Formal demands after insist", "درخواست رسمی پس از insist",
      "The manager insisted that the meeting ___ postponed.",
      "مدیر اصرار کرد که جلسه ___.",
      "Insist that takes the subjunctive: insisted that it be.",
      "insist that حالت التزامی می‌خواهد: insisted that it be.",
      options=["is", "be", "was", "will be"], answer=1, difficulty="hard"),
    q("g-b2-2", "grammar", "B2", ("Relative clauses", "جمله‌های موصولی"), "error",
      "Spotting a doubled object in a relative clause", "یافتن مفعول تکراری در جملهٔ موصولی",
      "Which part of the sentence is wrong? The report which I wrote it last week was accepted.",
      "کدام بخش جمله اشتباه است؟ The report which I wrote it last week was accepted.",
      "The relative pronoun already replaces the object, so it cannot appear twice.",
      "ضمیر موصولی خودش جانشین مفعول است، پس دوباره نمی‌آید.",
      options=["which", "it", "was accepted", "no error"], answer=1, difficulty="hard"),
    q("g-b2-3", "grammar", "B2", ("The passive", "مجهول"), "transform",
      "Turning an active statement into the passive", "تبدیل جملهٔ معلوم به مجهول",
      "Rewrite in the passive: They will finish the report by Friday.",
      "به مجهول بازنویسی کن: They will finish the report by Friday.",
      "The object becomes the subject and the tense moves to be + participle: will be finished.",
      "مفعول به جای فاعل می‌نشیند و زمان روی be + اسم مفعول می‌آید: will be finished.",
      accept=["the report will be finished by friday",
              "the report will be finished by friday."]),
    q("g-c1-1", "grammar", "C1", ("Inversion", "جابه‌جایی"), "mcq",
      "Inversion after a fronted negative adverb", "جابه‌جایی پس از قید منفی در آغاز",
      "Rarely ___ such confidence in a newcomer.", "به‌ندرت در تازه‌واردی چنین اعتمادبه‌نفسی ___.",
      "A fronted negative adverb forces inversion: rarely have we seen.",
      "قید منفی در آغاز جمله جای فعل و فاعل را عوض می‌کند: rarely have we seen.",
      options=["we have seen", "have we seen", "we saw", "saw we"], answer=1,
      difficulty="hard"),
    q("g-c1-2", "grammar", "C1", ("Third conditional", "شرطی نوع سوم"), "transform",
      "An unreal past condition with inversion", "شرط غیرواقعی گذشته با جابه‌جایی",
      "Rewrite beginning with Had: If we had known about the closure, we would have taken another route.",
      "با Had آغاز کن: If we had known about the closure, we would have taken another route.",
      "Had + subject + participle replaces if: had we known ...",
      "had + فاعل + اسم مفعول جانشین if می‌شود: had we known ...",
      accept=["had we known about the closure, we would have taken another route",
              "had we known about the closure we would have taken another route"],
      difficulty="hard"),
    q("g-c1-3", "grammar", "C1", ("Colligation", "هم‌آیی دستوری"), "cloze",
      "Adjective choice with an abstract noun", "انتخاب صفت با اسم انتزاعی",
      "The scheme drew ___ criticism from local residents.",
      "این طرح خرده‌گیری ___ از سوی ساکنان محلی برانگیخت.",
      "Widespread is the collocation for criticism across a group or area.",
      "برای خرده‌گیری گسترده در میان گروهی، widespread ترکیب درست است.",
      accept=["widespread", "broad", "widespread."], difficulty="hard"),
]

# --------------------------------------------------------------- vocabulary
VOCABULARY = [
    q("v-a1-1", "vocabulary", "A1", ("Everyday nouns", "اسم‌های روزمره"), "cloze",
      "Producing the everyday noun", "آوردن اسم روزمره",
      "We sleep in a ___.", "ما در ___ می‌خوابیم.",
      "A bed is what you sleep in.",
      "در تخت می‌خوابیم.",
      accept=["bed"], difficulty="easy"),
    q("v-a1-2", "vocabulary", "A1", ("Opposites", "متضاد"), "cloze",
      "Basic antonym", "متضاد پایه",
      "The opposite of hot is ___.", "متضاد hot ___ است.",
      "Cold is the antonym of hot.",
      "cold متضاد hot است.",
      accept=["cold"], difficulty="easy"),
    q("v-a1-3", "vocabulary", "A1", ("Places", "جاها"), "mcq",
      "Where a thing is bought", "خرید از کجا",
      "You buy bread at a ___.", "نان را از ___ می‌خری.",
      "A bakery sells bread; a library, a hospital and a garage do not.",
      "نانوایی نان می‌فروشد؛ کتابخانه، بیمارستان و تعمیرگاه نه.",
      options=["bakery", "library", "hospital", "garage"], answer=0, difficulty="easy"),
    q("v-a2-1", "vocabulary", "A2", ("Collocation", "هم‌نشینی"), "mcq",
      "Verb-noun collocation", "هم‌نشینی فعل و اسم",
      "Please ___ a photo of us.", "لطفاً از ما ___ بگیر.",
      "English takes a photo; do, make and put do not collocate with it.",
      "در انگلیسی take a photo می‌گوییم؛ do، make و put با آن نمی‌آیند.",
      options=["take", "do", "make", "put"], answer=0, difficulty="easy"),
    q("v-a2-2", "vocabulary", "A2", ("Collocation", "هم‌نشینی"), "cloze",
      "The verb that goes with decision", "فعلی که با decision می‌آید",
      "We need to ___ a decision before Friday.", "باید تا جمعه ___ تصمیم بگیریم.",
      "English makes a decision.",
      "در انگلیسی make a decision می‌گوییم.",
      accept=["make"]),
    q("v-a2-3", "vocabulary", "A2", ("Everyday objects", "اشیای روزمره"), "cloze",
      "Producing the object that fits the situation", "آوردن شیء مناسب موقعیت",
      "It's raining, so take an ___.", "باران می‌بارد، پس ___ بردار.",
      "An umbrella is for rain.",
      "چتر برای باران است.",
      accept=["umbrella"]),
    q("v-b1-1", "vocabulary", "B1", ("Phrasal verbs", "افعال عبارتی"), "mcq",
      "Beginning a new activity", "آغاز کردن کاری تازه",
      "I want to ___ up a new hobby this year.", "امسال می‌خواهم سرگرمی تازه‌ای ___ کنم.",
      "Take up a hobby means to start it.",
      "take up a hobby یعنی آن را آغاز کردن.",
      options=["take", "turn", "put", "set"], answer=0),
    q("v-b1-2", "vocabulary", "B1", ("Business collocation", "هم‌نشینی کاری"), "cloze",
      "Introducing a product to the market", "عرضهٔ محصول به بازار",
      "The company will ___ a new product in May.", "شرکت در ماه مِی محصول تازه‌ای ___ می‌کند.",
      "Launch a product is the usual pairing; start and begin are too general.",
      "launch a product ترکیب رایج است؛ start و begin بیش از حد کلی‌اند.",
      accept=["launch", "release", "introduce"]),
    q("v-b1-3", "vocabulary", "B1", ("Adjectives", "صفت‌ها"), "error",
      "Telling the -ing and -ed adjectives apart", "تفکیک صفت‌های ing و ed",
      "Which sentence uses the adjective correctly?",
      "کدام جمله صفت را درست به کار برده است؟",
      "A boring film bores people; bored describes the person.",
      "فیلم boring است و آدم bored می‌شود.",
      options=["I was boring during the film.", "The film was boring, so I slept.",
               "The film was bored.", "I was so boring that I slept."],
      answer=1),
    q("v-b2-1", "vocabulary", "B2", ("Idioms", "اصطلاح‌ها"), "mcq",
      "Understanding a common idiom", "فهم یک اصطلاح رایج",
      "She let the cat out of the bag. What happened?",
      "اصطلاح She let the cat out of the bag یعنی چه؟",
      "The idiom means a secret was revealed by accident.",
      "این اصطلاح یعنی رازی ناخواسته فاش شد.",
      options=["She told everyone the secret.", "She lost her pet.",
               "She refused to speak.", "She bought a bag."], answer=0,
      difficulty="hard"),
    q("v-b2-2", "vocabulary", "B2", ("Register", "لحن"), "cloze",
      "A formal verb for disagreeing", "فعل رسمی برای ناسازگاری",
      "The two reports ___ each other, so we could not decide.",
      "دو گزارش یکدیگر را ___، بنابراین نتوانستیم تصمیم بگیریم.",
      "Contradict means to state the opposite of something.",
      "contradict یعنی خلاف چیزی را گفتن.",
      accept=["contradict", "contradicted"]),
    q("v-b2-3", "vocabulary", "B2", ("Prepositional verbs", "افعال حرف اضافه‌دار"), "mcq",
      "The verb that takes for", "فعل‌ای که با for می‌آید",
      "He was ___ for the delay.", "او را برای تأخیر ___ .",
      "Blame someone for something; accuse takes of and charge takes with.",
      "blame somebody for something؛ accuse با of و charge با with می‌آید.",
      options=["blamed", "accused", "charged", "arrested"], answer=0),
    q("v-c1-1", "vocabulary", "C1", ("Academic verbs", "فعل‌های دانشگاهی"), "mcq",
      "A verb of evidential support", "فعل پشتیبانی شواهد",
      "The findings ___ the earlier study's conclusions.",
      "یافته‌ها نتیجه‌گیری‌های پژوهش پیشین را ___ .",
      "Corroborate means to support with evidence; collaborate is to work together.",
      "corroborate یعنی با شواهد تأیید کردن؛ collaborate یعنی همکاری کردن.",
      options=["corroborate", "collaborate", "corrupt", "congratulate"], answer=0,
      difficulty="hard"),
    q("v-c1-2", "vocabulary", "C1", ("Argument", "استدلال"), "cloze",
      "An adjective for a convincing argument", "صفت استدلال متقاعدکننده",
      "Her argument was so ___ that nobody could refute it.",
      "استدلالش چنان ___ بود که کسی نتوانست ردش کند.",
      "Cogent, compelling and convincing all describe an argument that holds.",
      "cogent، compelling و convincing هر سه استدلال محکم را توصیف می‌کنند.",
      accept=["cogent", "compelling", "convincing"], difficulty="hard"),
    q("v-c1-3", "vocabulary", "C1", ("Fixed expressions", "عبارت‌های ثابت"), "mcq",
      "Meaning of a formal fixed phrase", "معنی یک عبارت رسمی",
      "The date is still a moot point. This means it is ___.",
      "عبارت a moot point یعنی موضوع ___ است.",
      "A moot point is open to debate, not settled.",
      "a moot point یعنی موضوعی قابل بحث و حل‌نشده.",
      options=["open to debate", "already agreed", "completely irrelevant",
               "legally binding"], answer=0, difficulty="hard"),
]

# ------------------------------------------------------------------ reading
READING_PASSAGES = [
    {"id": "p-a1", "band": "A1",
     "title": L("Sara's Friday", "جمعه‌های سارا"),
     "text": L("My name is Sara. I live in a small town. I have one brother. "
               "He is ten. On Fridays we go to my grandmother's house. She "
               "makes bread for us.",
               "نام من سارا است. در شهر کوچکی زندگی می‌کنم. یک برادر دارم. او "
               "ده سال دارد. جمعه‌ها به خانهٔ مادربزرگم می‌رویم. او برای ما "
               "نان می‌پزد.")},
    {"id": "p-a2", "band": "A2",
     "title": L("The garden on Mill Street", "باغ خیابان میل"),
     "text": L("Mill Street had no garden until last spring. A group of "
               "neighbours asked the city for the empty land behind the old "
               "school, and the city said yes. On the first Saturday in April, "
               "twenty people came with spades and seeds. By July there were "
               "tomatoes, beans and a lot of sunflowers. The garden is open "
               "every day from eight in the morning until sunset, and nobody "
               "has to pay. There is only one rule: if you pick something, you "
               "must water something.",
               "خیابان میل تا بهار گذشته باغی نداشت. گروهی از همسایه‌ها از "
               "شهرداری زمین خالی پشت مدرسهٔ قدیمی را خواستند و شهرداری "
               "موافقت کرد. نخستین شنبهٔ آوریل، بیست نفر با بیل و دانه آمدند. "
               "تا جولای گوجه، لوبیا و کلی گل آفتابگردان بود. باغ هر روز از "
               "ساعت هشت صبح تا غروب آفتاب باز است و کسی لازم نیست پول بدهد. "
               "فقط یک قانون دارد: اگر چیزی می‌چینی، باید چیزی را آب بدهی.")},
    {"id": "p-b1", "band": "B1",
     "title": L("A letter about a course", "نامه‌ای دربارهٔ یک دوره"),
     "text": L("Dear Ms Farhadi, thank you for your interest in our evening "
               "course in bookkeeping. The course runs for ten weeks, on "
               "Tuesdays and Thursdays, from 6.30 to 8.30. Because we have had "
               "more applications than places, we ask everyone to take a short "
               "test in the first week; this is only to make sure the group "
               "starts at the same level, and it does not affect the fee. The "
               "fee is 240 pounds, which covers the workbook but not the exam. "
               "If you decide not to continue after the first two sessions, we "
               "will return all but 40 pounds. Please confirm your place by "
               "Friday, 12 September, as we cannot hold it after that date.",
               "خانم فرهادی عزیز، از علاقهٔ شما به دورهٔ عصرِ حسابداری "
               "سپاسگزاریم. دوره ده هفته است، سه‌شنبه‌ها و پنجشنبه‌ها، از ۶:۳۰ "
               "تا ۸:۳۰. چون متقاضی بیش از ظرفیت بوده، از همه می‌خواهیم هفتهٔ "
               "اول آزمون کوتاهی بدهند؛ این آزمون فقط برای هم‌سطح شدن گروه است "
               "و بر شهریه اثری ندارد. شهریه ۲۴۰ پوند است که کتاب کار را شامل "
               "می‌شود اما آزمون را نه. اگر پس از دو جلسهٔ اول بخواهید ادامه "
               "ندهید، همهٔ پول جز ۴۰ پوند بازگردانده می‌شود. لطفاً تا جمعه ۱۲ "
               "سپتامبر جای خود را تأیید کنید، چون بعد از آن تاریخ نمی‌توانیم "
               "نگه داریم.")},
    {"id": "p-b2", "band": "B2",
     "title": L("Why we forget names", "چرا نام‌ها را فراموش می‌کنیم"),
     "text": L("Forgetting a name two seconds after hearing it is not a failure "
               "of memory so much as a failure of attention. When we meet "
               "someone, most of us are busy deciding what to say next, and a "
               "name is the least interesting thing in the exchange; the brain, "
               "which is economical to a fault, simply does not file it. The fix "
               "is not to try harder but to do something with the name within a "
               "few seconds: repeat it aloud, connect it to someone you already "
               "know, or write it down. Experiments on name learning suggest "
               "that the act of producing the word matters far more than hearing "
               "it again, which is why silently repeating a name to yourself is "
               "close to useless. Curiously, the same pattern holds for "
               "vocabulary in a second language: recognition feels like "
               "knowledge and is not.",
               "فراموش کردن نامی دو ثانیه پس از شنیدنش، بیشتر از آنکه نقص حافظه "
               "باشد، نقص توجه است. وقتی کسی را می‌بینیم، بیشترمان مشغول "
               "تصمیم‌گیری دربارهٔ حرف بعدی‌مان هستیم و نام کم‌جالب‌ترین چیز آن "
               "گفت‌وگوست؛ مغز هم که به‌شدت صرفه‌جو است، اصلاً آن را بایگانی "
               "نمی‌کند. راه حل، تلاش بیشتر نیست، بلکه انجام کاری با نام در همان "
               "چند ثانیه است: بلند تکرارش کن، به کسی که می‌شناسی وصلش کن، یا "
               "بنویسش. آزمایش‌ها نشان می‌دهد نفسِ برزبان‌آوردن واژه بسیار "
               "مهم‌تر از شنیدن دوبارهٔ آن است، و همین است که تکرار بی‌صدا در "
               "ذهن تقریباً بی‌فایده است. جالب اینکه در واژگان زبان دوم هم همین "
               "الگو برقرار است: آشنا به نظر رسیدن، شبیه دانستن است و دانستن "
               "نیست.")},
    {"id": "p-c1", "band": "C1",
     "title": L("The open-plan trade-off", "معاملهٔ دفتر باز"),
     "text": L("Open-plan offices were sold to a generation of employers as a "
               "means of dissolving hierarchy, and to a generation of employees "
               "as a way of making friends at work. Neither promise survived "
               "contact with measurement. Studies that track conversation find "
               "that removing walls does not increase the number of exchanges "
               "between colleagues; it reduces them, because every exchange "
               "becomes public property, and the people who most need to "
               "concentrate learn to route around the room with headphones and "
               "a fixed gaze. What the layout does produce reliably is a keener "
               "awareness of status: who is on the phone with whom, who leaves "
               "early, whose desk sits nearest the window. The lesson is not "
               "that openness is worthless. It is that a space optimised for "
               "visibility will be optimised for visibility, and concentration "
               "is the price, paid quietly by the people whose work is hardest "
               "to watch.",
               "دفترهای باز به نسل مدیران به‌عنوان راهی برای از میان برداشتن "
               "سلسله‌مراتب فروخته شد و به نسل کارمندان به‌عنوان راهی برای "
               "دوست‌یابی در محل کار. هیچ‌یک از این دو وعده با اندازه‌گیری دوام "
               "نیاورد. پژوهش‌هایی که گفت‌وگوها را رصد می‌کنند می‌بینند برداشتن "
               "دیوارها شمار تبادل‌ها میان همکاران را بالا نمی‌برد، بلکه کم "
               "می‌کند، چون هر تبادلی عمومی می‌شود و کسانی که بیش از همه به "
               "تمرکز نیاز دارند یاد می‌گیرند با هدفون و نگاه ثابت دور اتاق را "
               "بزنند. آنچه این چیدمان به‌طور قابل‌اعتماد تولید می‌کند حس "
               "تیزتری از جایگاه است: چه کسی با چه کسی تلفنی حرف می‌زند، چه "
               "کسی زودتر می‌رود، میز چه کسی نزدیک پنجره است. درس ماجرا این "
               "نیست که باز بودن بی‌ارزش است. این است که فضایی که برای دیده‌شدن "
               "بهینه شود، برای دیده‌شدن بهینه می‌شود و تمرکز بهای آن است، بهایی "
               "که بی‌صدا را کسانی می‌پردازند که کارشان سخت‌ترین کار برای "
               "تماشا کردن است.")},
]

READING = [
    q("r-a1-1", "reading", "A1", ("Detail", "جزئیات"), "mcq",
      "Locating one stated fact", "یافتن یک واقعیت گفته‌شده",
      "Where does Sara live?", "سارا کجا زندگی می‌کند؟",
      "She says she lives in a small town.",
      "می‌گوید در شهر کوچکی زندگی می‌کند.",
      options=["In a big city", "In a small town", "Near her school",
               "With her grandmother"], answer=1, passage="p-a1", difficulty="easy"),
    q("r-a1-2", "reading", "A1", ("Detail", "جزئیات"), "mcq",
      "Locating a day", "یافتن یک روز",
      "When do they visit their grandmother?", "چه زمانی به دیدن مادربزرگ می‌روند؟",
      "Fridays is the day named for the visit.",
      "جمعه‌ها روزی است که برای این دیدار گفته شده.",
      options=["On Mondays", "Every day", "On Fridays", "In summer"],
      answer=2, passage="p-a1", difficulty="easy"),
    q("r-a2-1", "reading", "A2", ("Detail", "جزئیات"), "mcq",
      "Who did something", "چه کسی کاری کرد",
      "Who asked the city for the land?", "چه کسی زمین را از شهرداری خواست؟",
      "The neighbours asked, and the city agreed.",
      "همسایه‌ها خواستند و شهرداری موافقت کرد.",
      options=["The old school", "A group of neighbours", "The city", "A shop"],
      answer=1, passage="p-a2", difficulty="easy"),
    q("r-a2-2", "reading", "A2", ("Detail", "جزئیات"), "mcq",
      "Opening hours", "ساعت کار",
      "When is the garden open?", "باغ چه زمانی باز است؟",
      "It opens at eight and closes at sunset, every day.",
      "هر روز از هشت باز می‌شود و هنگام غروب بسته می‌شود.",
      options=["Only on Saturdays", "Every day until sunset",
               "From eight until noon", "Only in spring"], answer=1, passage="p-a2"),
    q("r-b1-1", "reading", "B1", ("Detail", "جزئیات"), "mcq",
      "Reading a schedule", "خواندن یک برنامه",
      "How often does the course meet?", "دوره چند بار در هفته برگزار می‌شود؟",
      "Tuesdays and Thursdays, for ten weeks.",
      "سه‌شنبه‌ها و پنجشنبه‌ها، به مدت ده هفته.",
      options=["Once a week", "Twice a week", "Every evening",
               "Ten times in total"], answer=1, passage="p-b1"),
    q("r-b1-2", "reading", "B1", ("Inference", "استنباط"), "mcq",
      "Why something is done", "چرا کاری انجام می‌شود",
      "Why is there a test in the first week?", "چرا هفتهٔ اول آزمون گرفته می‌شود؟",
      "The letter says it is only to level the group.",
      "نامه می‌گوید فقط برای هم‌سطح کردن گروه است.",
      options=["To choose the best students", "To set the price",
               "To start the group at one level", "To replace the exam"],
      answer=2, passage="p-b1"),
    q("r-b2-1", "reading", "B2", ("Main idea", "ایدهٔ اصلی"), "mcq",
      "The writer's central claim", "ادعای اصلی نویسنده",
      "What is the writer's main claim about forgetting names?",
      "ادعای اصلی نویسنده دربارهٔ فراموش کردن نام‌ها چیست؟",
      "The first sentence calls it a failure of attention.",
      "جملهٔ اول آن را نقص توجه می‌نامد.",
      options=["It shows a weak memory", "It comes from not paying attention",
               "It happens more with age", "It cannot be improved"],
      answer=1, passage="p-b2"),
    q("r-b2-2", "reading", "B2", ("Inference", "استنباط"), "mcq",
      "What the evidence supports", "شواهد چه چیزی را تأیید می‌کند",
      "According to the text, what helps most?",
      "به گفتهٔ متن، چه چیزی بیشترین کمک را می‌کند؟",
      "Producing the word matters more than hearing it.",
      "برزبان آوردن واژه مهم‌تر از شنیدن دوبارهٔ آن است.",
      options=["Hearing the name again", "Repeating it silently",
               "Saying it and using it", "Writing it hours later"],
      answer=2, passage="p-b2"),
    q("r-c1-1", "reading", "C1", ("Inference", "استنباط"), "mcq",
      "What the findings actually show", "یافته‌ها واقعاً چه نشان می‌دهند",
      "What did the studies find about removing walls?",
      "پژوهش‌ها دربارهٔ برداشتن دیوارها چه یافتند؟",
      "Exchange falls, because every conversation becomes public.",
      "تبادل‌ها کم می‌شود، چون هر گفت‌وگو عمومی می‌شود.",
      options=["Conversation rose sharply", "Conversation fell",
               "Nothing changed at all", "Only managers talked more"],
      answer=1, passage="p-c1", difficulty="hard"),
    q("r-c1-2", "reading", "C1", ("Attitude", "نگرش"), "mcq",
      "Reading the writer's stance", "خواندن موضع نویسنده",
      "What is the writer's view of open-plan offices?",
      "نویسنده چه دیدی به دفترهای باز دارد؟",
      "The last lines weigh the trade-off rather than dismissing the idea.",
      "سطرهای آخر این معامله را می‌سنجند، نه اینکه ایده را رد کنند.",
      options=["They are worthless", "They are a reasonable idea with a real cost",
               "They always improve friendship", "They are too expensive to build"],
      answer=1, passage="p-c1", difficulty="hard"),
]

LISTENING = [
    q("l-a1-1", "listening", "A1", ("Numbers and times", "عدد و ساعت"), "mcq",
      "Catching a time in a short announcement", "گرفتن ساعت در اعلامیه‌ای کوتاه",
      "What time does the shop open?", "مغازه چه ساعتی باز می‌شود؟",
      "Opens at nine; six is when it closes.",
      "ساعت نه باز می‌شود؛ شش ساعت بسته شدن است.",
      options=["Six", "Seven", "Nine", "Ten"], answer=2, difficulty="easy",
      say="The shop opens at nine and closes at six."),
    q("l-a1-2", "listening", "A1", ("Quantity", "تعداد"), "mcq",
      "Counting what is mentioned", "شمردن آنچه گفته می‌شود",
      "How many cats does the brother have?", "برادرش چند گربه دارد؟",
      "Two cats; the dog is a different animal.",
      "دو گربه؛ سگ حیوان دیگری است.",
      options=["One", "Two", "Three", "Four"], answer=1, difficulty="easy",
      say="My brother has two cats and a dog."),
    q("l-a2-1", "listening", "A2", ("Details", "جزئیات"), "mcq",
      "Platform and destination", "سکو و مقصد",
      "Which platform does the Bristol train leave from?",
      "قطار بریستول از کدام سکو حرکت می‌کند؟",
      "From platform four; the times are a distraction.",
      "از سکوی چهار؛ ساعت‌ها حواس‌پرتی‌اند.",
      options=["Platform one", "Platform four", "Platform six", "Platform ten"],
      answer=1,
      say="The train to Bristol leaves from platform four at ten past six."),
    q("l-a2-2", "listening", "A2", ("Orders", "سفارش"), "mcq",
      "What was ordered", "چه چیزی سفارش داده شد",
      "What did the speaker order?", "گوینده چه سفارش داد؟",
      "Both items are named: coffee and a cheese sandwich.",
      "هر دو چیز نام برده می‌شود: قهوه و ساندویچ پنیر.",
      options=["Tea and a sandwich", "Coffee and a sandwich",
               "Coffee and a cake", "A sandwich only"], answer=1,
      say="Could I have a coffee and a cheese sandwich, please?"),
    q("l-b1-1", "listening", "B1", ("Narrative", "روایت"), "mcq",
      "What actually happened", "واقعاً چه اتفاقی افتاد",
      "How did the speaker travel?", "گوینده چگونه سفر کرد؟",
      "The plan was the car; what happened was the train.",
      "قصدش ماشین بود؛ اما با قطار رفت.",
      options=["By car", "By train", "By bus", "On foot"], answer=1,
      say="I was going to drive, but the traffic was so bad that I took the train instead."),
    q("l-b1-2", "listening", "B1", ("Reasons", "دلیل"), "mcq",
      "Why a plan changed", "چرا برنامه عوض شد",
      "Why was the meeting moved?", "چرا جلسه جابه‌جا شد؟",
      "The because-clause gives the reason: the client is away.",
      "جملهٔ because دلیل را می‌گوید: مشتری در سفر است.",
      options=["The room was busy", "The client was away",
               "Thursday suited everyone", "The report was late"], answer=1,
      say="We've put the meeting back to Thursday because the client is away until Wednesday."),
    q("l-b2-1", "listening", "B2", ("Hypotheticals", "فرض"), "mcq",
      "A counterfactual the speaker did not experience", "فرضی که رخ نداد",
      "What does the speaker mean?", "منظور گوینده چیست؟",
      "Without the delay they would have missed it, so it saved them.",
      "بی تأخیر آن را از دست می‌دادند، پس تأخیر نجاتشان داد.",
      options=["The delay caused a problem", "The delay helped them",
               "They missed the announcement", "There was no delay"], answer=1,
      difficulty="hard",
      say="Had it not been for the delay, we would have missed the announcement entirely."),
    q("l-b2-2", "listening", "B2", ("Attitude", "نگرش"), "mcq",
      "Reading reservation in a positive statement", "خواندن تردید در جملهٔ مثبت",
      "What is the board's attitude?", "نگرش هیئت‌مدیره چیست؟",
      "Encouraging, though cautious is reserved optimism.",
      "«امیدبخش، اما محتاط» خوش‌بینی محتاطانه است.",
      options=["Completely confident", "Quietly doubtful",
               "Angry about the figures", "Ready to invest more"], answer=1,
      difficulty="hard",
      say="The figures look encouraging, though the board remains cautious about the second quarter."),
    q("l-c1-1", "listening", "C1", ("Emphasis", "تأکید"), "mcq",
      "Where the speaker puts the emphasis", "گوینده کجا تأکید می‌کند",
      "What is the speaker's main point?", "نکتهٔ اصلی گوینده چیست؟",
      "The surprise would have been surprise itself: nobody was.",
      "جای تعجب این بود که کسی تعجب نکرد.",
      options=["The policy failed unexpectedly", "The failure was widely expected",
               "Nobody noticed the failure", "The policy was never tested"],
      answer=1, difficulty="hard",
      say="What I find most striking is not that the policy failed, but that nobody was surprised when it did."),
    q("l-c1-2", "listening", "C1", ("Implication", "برداشت"), "mcq",
      "What is implied but not said", "آنچه گفته نمی‌شود اما برداشت می‌شود",
      "What is implied about her?", "دربارهٔ او چه چیزی برداشت می‌شود؟",
      "Every bit as capable plus less inclined to say so is ability with modesty.",
      "«every bit as capable» با «less inclined to say so» یعنی توانایی همراه با فروتنی.",
      options=["She is less capable but louder", "She is equally capable and modest",
               "She replaced someone modest", "She talks about her work a lot"],
      answer=1, difficulty="hard",
      say="She's every bit as capable as her predecessor, if rather less inclined to say so."),
]

RUBRIC = [
    {"points": 1, "text": L("A few words, or one short sentence.",
                            "چند واژه، یا یک جملهٔ کوتاه.")},
    {"points": 2, "text": L("Simple sentences, some mistakes, the meaning is clear.",
                            "جمله‌های ساده با چند اشتباه؛ معنا روشن است.")},
    {"points": 3, "text": L("Connected sentences with reasons or details, mostly accurate.",
                            "جمله‌های پیوسته با دلیل و جزئیات، بیشترشان درست.")},
    {"points": 4, "text": L("Well organised, natural, with a range of structures.",
                            "سازمان‌یافته و طبیعی، با تنوع ساختار.")},
]

WRITING = [
    q("w-b1-1", "writing", "B1", ("Short message", "پیام کوتاه"), "shortwriting",
      "Writing a connected message with a reason", "نوشتن پیامی پیوسته با دلیل",
      "A friend is coming to your city for two days. Write five or six sentences "
      "telling them what to see and why.",
      "دوستی دو روز به شهرت می‌آید. پنج یا شش جمله بنویس که چه ببیند و چرا.",
      "Compare your answer with the rubric, not with a key: this task is not marked.",
      "پاسخ خود را با معیار بسنج، نه با کلید: این تمرین نمره نمی‌گیرد.",
      difficulty="medium"),
    q("w-b2-1", "writing", "B2", ("Opinion paragraph", "بند نظر"), "shortwriting",
      "Balancing a claim and a counter-argument", "سنجش یک ادعا و استدلال مخالف",
      "Some people think phones should be banned in classrooms. Write a short "
      "paragraph giving your view and one counter-argument.",
      "بعضی می‌گویند گوشی در کلاس باید ممنوع شود. بندی کوتاه بنویس با نظر خودت "
      "و یک استدلال مخالف.",
      "Concede one point, then answer it. This task is not marked.",
      "یک نکته را بپذیر، بعد پاسخش را بده. این تمرین نمره نمی‌گیرد.",
      difficulty="hard"),
]

SPEAKING = [
    q("s-b1-1", "speaking", "B1", ("Narrative", "روایت"), "speaking",
      "Sustaining a short spoken account", "گفتن روایتی کوتاه و پیوسته",
      "Tell me about a trip you enjoyed and why it was good.",
      "از سفری بگو که خوش گذشت و چرا خوب بود.",
      "Thirty seconds, past tenses, then a reason. Not marked.",
      "سی ثانیه، زمان گذشته، بعد یک دلیل. نمره نمی‌گیرد.",
      difficulty="medium"),
    q("s-b2-1", "speaking", "B2", ("Discussion", "بحث"), "speaking",
      "Presenting both sides before a position", "گفتن هر دو طرف پیش از نتیجه",
      "Do you think working from home is better than working in an office? "
      "Give both sides.",
      "فکر می‌کنی کار از خانه بهتر از کار در دفتر است؟ هر دو طرف را بگو.",
      "Signpost both sides before you decide. Not marked.",
      "پیش از نتیجه‌گیری، هر دو طرف را نشان بده. نمره نمی‌گیرد.",
      difficulty="hard"),
]

ITEMS = GRAMMAR + VOCABULARY + READING + LISTENING + WRITING + SPEAKING

LEVEL = {
    "version": 2,
    "title": L("Level assessment", "سنجش سطح"),
    "blurb": L("Six skills measured separately. Grammar, vocabulary, reading "
               "and listening are marked from your answers; writing and "
               "speaking are practice and are reported as not assessed.",
               "شش مهارت جدا سنجیده می‌شود. گرامر، واژگان، خواندن و شنیدن از "
               "پاسخ‌هایت نمره می‌گیرند؛ نوشتن و گفتن تمرین‌اند و «سنجیده "
               "نشده» گزارش می‌شوند."),
    "minutes": 30,
    "retakeDays": 30,
    "skills": SKILLS,
    "bands": BANDS,
    "testedBands": TESTED,
    # One paper for everyone, ten questions per band, so a count means the
    # same thing for every learner. The level comes from that count.
    "blueprint": {
        "bands": TESTED,
        "perBand": {"grammar": 3, "vocabulary": 3, "reading": 2, "listening": 2},
        "perBandTotal": 10,
        "questions": 50,
        "assessed": ["grammar", "vocabulary", "reading", "listening"],
        "practice": ["writing", "speaking"],
        # Share of the paper that must be right to claim each band, in order:
        # 8, 17, 26, 35 and 44 of 50. The same fractions apply to a skill with
        # its own item count, so a score of 11 of 15 in grammar and 8 of 10 in
        # reading are read against the same ruler.
        "cutoffs": [0.16, 0.34, 0.52, 0.70, 0.88],
    },
    "passages": READING_PASSAGES,
    "items": ITEMS,
    "rubric": RUBRIC,
    "method": L("Everyone answers the same fifty questions: ten from each band, "
                "A1 to C1, spread across grammar, vocabulary, reading and "
                "listening. Your level comes from how many you get right - 8 of "
                "50 is A1, 17 is A2, 26 is B1, 35 is B2, 44 is C1 - and each "
                "skill is read against the same fractions of its own total. "
                "Writing and speaking are not scored.",
                "همه همان پنجاه پرسش را پاسخ می‌دهند: از هر سطح، از A1 تا C1، ده "
                "پرسش در گرامر، واژگان، خواندن و شنیدن. سطح از تعداد پاسخ‌های "
                "درست می‌آید: ۸ از ۵۰ یعنی A1، ۱۷ یعنی A2، ۲۶ یعنی B1، ۳۵ یعنی "
                "B2 و ۴۴ یعنی C1. هر مهارت هم با همان نسبت‌ها از مجموع خودش "
                "خوانده می‌شود. نوشتن و گفتن نمره نمی‌گیرند."),
    "caveat": L("This is a self-assessment built on a reviewed item bank, not a "
                "validated certification. Item difficulty is tracked from your "
                "own attempts, and the level is an estimate with a margin - "
                "not a certificate.",
                "این یک خودسنجی بر پایهٔ بانک پرسش بازبینی‌شده است، نه گواهی "
                "اعتبارسنجی‌شده. سختی پرسش‌ها از تلاش‌های خودت ثبت می‌شود و "
                "سطح تخمینی با حاشیهٔ خطاست، نه گواهی."),
}
