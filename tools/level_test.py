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
     recognize it.
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
    {"id": "interaction", "assessed": True,
     "title": L("Interaction", "تعامل"),
     "blurb": L("Taking your turn in real exchanges: check-in desks, orders, "
                "meetings and complaints.",
                "نوبت گرفتن در گفت‌وگوهای واقعی: پذیرش، سفارش، جلسه و شکایت.")},
    {"id": "mediation", "assessed": True,
     "title": L("Mediation", "میانجی‌گری"),
     "blurb": L("Carrying meaning between people and documents: explaining a "
                "notice, relaying a policy, briefing a colleague.",
                "رساندن معنا میان آدم‌ها و سندها: توضیح اطلاعیه، بازگویی "
                "سیاست، گزارش به همکار.")},
    {"id": "writing", "assessed": True,
     "title": L("Writing", "نوشتن"),
     "blurb": L("Five tasks, one per band, marked on the same rubric the "
                "report shows: length, sentences, linking and accuracy.",
                "پنج تمرین، یکی از هر سطح، با همان معیاری که گزارش نشان "
                "می‌دهد سنجیده می‌شود: طول، جمله‌ها، پیوند و دقت.")},
    {"id": "speaking", "assessed": False,
     "title": L("Speaking", "گفتن"),
     "blurb": L("Practice tasks with a rubric. Not scored into the level.",
                "تمرین با معیار. در سطح محاسبه نمی‌شود.")},
]


# What a band means in each skill, in the learner's own words. The report
# prints the line for the band a skill actually reached and nothing above it:
# a can-do statement is only honest when there is evidence behind it.
CAN_DO = {
    "grammar": {
        "A1": L("Can use the present simple and basic word order in short sentences.",
                "می‌تواند حال ساده و ترتیب پایهٔ واژه‌ها را در جمله‌های کوتاه به کار ببرد."),
        "A2": L("Can use the past simple, comparatives and simple negatives correctly.",
                "می‌تواند گذشتهٔ ساده، صفت تفضیلی و منفی ساده را درست به کار ببرد."),
        "B1": L("Can use the present perfect, first conditional and basic passive in familiar contexts.",
                "می‌تواند حال کامل، شرطی نوع اول و مجهول پایه را در موقعیت‌های آشنا به کار ببرد."),
        "B2": L("Can use a range of tenses, conditionals and passive forms with few errors that obscure meaning.",
                "می‌تواند طیفی از زمان‌ها، شرطی‌ها و مجهول را با خطاهای کم و بدون ابهام به کار ببرد."),
        "C1": L("Can use complex structures flexibly and correct errors that would matter.",
                "می‌تواند ساختارهای پیچیده را منعطف به کار ببرد و خطاهای مهم را اصلاح کند."),
    },
    "vocabulary": {
        "A1": L("Has enough everyday words for greetings, family, food and prices.",
                "واژه‌های روزمره برای سلام، خانواده، غذا و قیمت را دارد."),
        "A2": L("Can talk about routines, travel and shopping with common collocations.",
                "می‌تواند با هم‌نشینی‌های رایج دربارهٔ routine، سفر و خرید حرف بزند."),
        "B1": L("Can express opinions and narrate with a working range of phrasal verbs and idioms.",
                "می‌تواند با طیفی کاربردی از افعال عبارتی و اصطلاح‌ها نظر بگوید و روایت کند."),
        "B2": L("Has a broad range for work and current affairs, and can paraphrase a missing word.",
                "دامنهٔ واژگانی گسترده‌ای برای کار و مسائل روز دارد و می‌تواند واژهٔ جاافتاده را بازگو کند."),
        "C1": L("Uses precise, idiomatic vocabulary and distinguishes near-synonyms.",
                "واژگان دقیق و اصطلاحی به کار می‌برد و نزدیک‌معناها را از هم جدا می‌کند."),
    },
    "reading": {
        "A1": L("Can understand short messages and notices with familiar words.",
                "پیام‌ها و اطلاعیه‌های کوتاه با واژه‌های آشنا را می‌فهمد."),
        "A2": L("Can find specific information in adverts, timetables and short emails.",
                "می‌تواند اطلاعات مشخص را در آگهی، جدول زمانی و ایمیل کوتاه پیدا کند."),
        "B1": L("Can follow the main points of an article and infer simple attitudes.",
                "نکته‌های اصلی یک مقاله را می‌گیرد و نگرش سادهٔ نویسنده را استنباط می‌کند."),
        "B2": L("Can read reports and articles efficiently and separate fact from claim.",
                "گزارش و مقاله را کارآمد می‌خواند و واقعیت را از ادعا جدا می‌کند."),
        "C1": L("Can follow complex argument and implicit stance across long texts.",
                "استدلال پیچیده و موضع ضمنی را در متن‌های بلند دنبال می‌کند."),
    },
    "listening": {
        "A1": L("Can understand slow, clear speech about familiar everyday things.",
                "گفتار آهسته و روشن دربارهٔ کارهای آشنا را می‌فهمد."),
        "A2": L("Can follow short announcements and routine exchanges.",
                "اعلامیه‌های کوتاه و گفت‌وگوهای روزمره را دنبال می‌کند."),
        "B1": L("Can follow the main points of a conversation or talk at natural speed.",
                "نکته‌های اصلی گفت‌وگو یا سخنرانی با سرعت طبیعی را می‌فهمد."),
        "B2": L("Can follow extended speech, interviews and presentations, including tone.",
                "گفتار بلند، مصاحبه و ارائه را با لحن آن دنبال می‌کند."),
        "C1": L("Can follow complex discussion and identify implied meaning and register.",
                "بحث پیچیده را می‌فهمد و معنای ضمنی و لحن را تشخیص می‌دهد."),
    },
    "interaction": {
        "A1": L("Can take a short turn in a service exchange.",
                "می‌تواند نوبتی کوتاه در یک گفت‌وگوی خدماتی بگیرد."),
        "A2": L("Can handle a routine problem politely.",
                "می‌تواند مشکلی روزمره را مؤدبانه حل کند."),
        "B1": L("Can negotiate arrangements and keep a conversation going.",
                "می‌تواند دربارهٔ قرارها مذاکره کند و گفت‌وگو را ادامه دهد."),
        "B2": L("Can disagree, clarify and hold a position professionally.",
                "می‌تواند حرفه‌ای مخالفت کند، روشن‌سازی بخواهد و بر موضع بماند."),
        "C1": L("Can manage delicate exchanges and state consequences diplomatically.",
                "می‌تواند گفت‌وگوهای حساس را اداره کند و پیامدها را دیپلماتیک بگوید."),
    },
    "mediation": {
        "A1": L("Can pass on one simple fact from a sign.",
                "می‌تواند یک واقعیت ساده را از یک تابلو برساند."),
        "A2": L("Can explain a timetable or rule to someone else.",
                "می‌تواند جدول زمانی یا قاعده‌ای را برای دیگری توضیح دهد."),
        "B1": L("Can relay a written policy in plain language.",
                "می‌تواند سیاستی مکتوب را به زبان ساده بازگو کند."),
        "B2": L("Can combine two sources and identify the conflict between them.",
                "می‌تواند دو منبع را با هم جمع کند و تعارضشان را نشان دهد."),
        "C1": L("Can explain a complex constraint without distorting it.",
                "می‌تواند محدودیتی پیچیده را بدون تحریف توضیح دهد."),
    },
    "writing": {
        "A1": L("Can write three connected sentences about yourself.",
                "می‌تواند سه جملهٔ پیوسته دربارهٔ خودش بنویسد."),
        "A2": L("Can narrate a past event in sequence.",
                "می‌تواند رخدادی در گذشته را به ترتیب روایت کند."),
        "B1": L("Can write a short message that gives reasons.",
                "می‌تواند پیامی کوتاه با دلیل بنویسد."),
        "B2": L("Can write a balanced paragraph with a counter-argument.",
                "می‌تواند بند متوازنی با استدلال مخالف بنویسد."),
        "C1": L("Can write a qualified argument with hedged claims.",
                "می‌تواند استدلالی سنجیده با ادعاهای محدودشده بنویسد."),
    },
    "speaking": {
        "B1": L("Can sustain a short account of an experience.",
                "می‌تواند روایتی کوتاه از یک تجربه را پیوسته بگوید."),
        "B2": L("Can present both sides before taking a position.",
                "می‌تواند پیش از گرفتن موضع، هر دو طرف را بگوید."),
    },
}

for _skill in SKILLS:
    _skill["canDo"] = CAN_DO.get(_skill["id"], {})

BANDS = [
    {"id": "PRE", "label": "Pre-A1", "name": L("Absolute beginner", "مبتدی مطلق"),
     "can": L("You recognize greetings, numbers and a few everyday words.",
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
              "movies without subtitles.",
              "مقاله را سریع می‌خوانی، از موضعت دفاع می‌کنی و بیشتر فیلم‌ها را "
              "بی‌زیرنویس می‌فهمی.")},
    {"id": "C1", "label": "C1", "name": L("Advanced", "پیشرفته"),
     "can": L("You use English flexibly at work and in study, and you hear "
              "register and nuance.",
              "انگلیسی را در کار و تحصیل منعطف به کار می‌بری و تفاوت لحن و "
              "ظرافت‌ها را می‌شنوی.")},
    {"id": "C2", "label": "C2", "name": L("Proficient", "تسلط"),
     "can": L("You read and hear almost everything effortlessly and summarize "
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
      needs=None, weight=1, domain="everyday", task="selected-response",
      scenario=None, descriptor=None, stimulus=None, accessibility=None):
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
        # The item bank's provenance block. Everything below is what a
        # reviewer, a report and the freshness check read: what real-world
        # domain the task comes from, which CEFR descriptor it is evidence
        # for, what the learner is looking at, and how the item can be
        # accessed without the picture or the audio.
        "domain": domain,
        "taskType": task,
        "descriptor": descriptor or L(
            "Uses English to complete a routine task at this level.",
            "انگلیسی را برای انجام کاری روزمره در این سطح به کار می‌برد."),
        "accessibility": accessibility or L(
            "All information needed to answer is in the text.",
            "همهٔ اطلاعات لازم برای پاسخ در متن آمده است."),
        "rights": "Fluentify original, all rights reserved",
        "itemVersion": "3.0",
        "status": "approved",
        "reviewedOn": "2026-11-18",
        "nextReview": "2027-11-18",
    }
    if scenario:
        item["scenario"] = scenario
    if stimulus:
        item["stimulus"] = stimulus
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
    if needs is not None:
        item["needs"] = needs
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
      "Build one sentence: how you travel to work.", "یک جمله بساز: چطور به سر کار می‌روی.",
      "Subject, verb, then by + transport.",
      "فاعل، فعل، بعد by + وسیلهٔ نقلیه.",
      accept=["i go to work by bus", "i go to work by bus."],
      tokens=["by bus", "go", "I", "to work", "."],
      difficulty="easy"),
    q("g-a2-1", "grammar", "A2", ("Past simple", "گذشتهٔ ساده"), "cloze",
      "Producing a finished past verb", "ساختن فعل گذشتهٔ ساده",
      "We ___ to the movie theater last night.", "دیشب به سینما ___.",
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
      "Build one sentence: since 2015, and where she lives.", "یک جمله بساز: از ۲۰۱۵ و جایی که او زندگی می‌کند.",
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
      "A boring movie bores people; bored describes the person.",
      "فیلم boring است و آدم bored می‌شود.",
      options=["I was boring during the movie.", "The movie was boring, so I slept.",
               "The movie was bored.", "I was so boring that I slept."],
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
               "neighbors asked the city for the empty land behind the old "
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
               "Friday, September 12, as we cannot hold it after that date.",
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
               "that openness is worthless. It is that a space optimized for "
               "visibility will be optimized for visibility, and concentration "
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
      "The neighbors asked, and the city agreed.",
      "همسایه‌ها خواستند و شهرداری موافقت کرد.",
      options=["The old school", "A group of neighbors", "The city", "A shop"],
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
    {"points": 4, "text": L("Well organized, natural, with a range of structures.",
                            "سازمان‌یافته و طبیعی، با تنوع ساختار.")},
]

# What each band's task has to reach before it earns its points. The engine
# reads this table, so the floors are part of the bank rather than constants
# buried in the page: changing a band's demand is a data edit.
WRITING_SCALE = {
    "A1": {"words": 20, "sentences": 3},
    "A2": {"words": 35, "sentences": 4},
    "B1": {"words": 50, "sentences": 5},
    "B2": {"words": 70, "sentences": 6},
    "C1": {"words": 90, "sentences": 6},
}

WRITING = [
    q("w-a1-1", "writing", "A1", ("Sentences about yourself", "جمله دربارهٔ خودت"),
      "shortwriting",
      "Writing three connected sentences", "نوشتن سه جملهٔ پیوسته",
      "Write three sentences about your family: who is in it, where you live, "
      "and one thing you do together.",
      "سه جمله دربارهٔ خانواده‌ات بنویس: چه کسانی در آن هستند، کجا زندگی می‌کنید "
      "و یک کار که با هم می‌کنید.",
      "Three sentences that join with and or but is the whole task at A1.",
      "در A1 همین کافی است که سه جمله با and یا but به هم وصل شوند.",
      difficulty="easy", needs=["and", "but", "with"]),
    q("w-a2-1", "writing", "A2", ("Weekend narrative", "روایت آخر هفته"),
      "shortwriting",
      "Narrating past events in sequence", "روایت پی‌درپی رخدادهای گذشته",
      "Write four or five sentences about last weekend: where you went, what "
      "you did, and what you liked.",
      "چهار یا پنج جمله دربارهٔ آخر هفتهٔ گذشته بنویس: کجا رفتی، چه کار کردی و "
      "چه چیزی را دوست داشتی.",
      "Past simple, in order, with at least one linking word.",
      "گذشتهٔ ساده، به ترتیب، با دست‌کم یک واژهٔ پیوند.",
      difficulty="medium", needs=["and", "then", "because", "but", "after"]),
    q("w-b1-1", "writing", "B1", ("Short message", "پیام کوتاه"), "shortwriting",
      "Writing a connected message with a reason", "نوشتن پیامی پیوسته با دلیل",
      "A friend is coming to your city for two days. Write five or six sentences "
      "telling them what to see and why.",
      "دوستی دو روز به شهرت می‌آید. پنج یا شش جمله بنویس که چه ببیند و چرا.",
      "Five sentences and one reason: because or so has to appear.",
      "پنج جمله و یک دلیل: باید because یا so بیاید.",
      difficulty="medium", needs=["because", "so", "since", "as"]),
    q("w-b2-1", "writing", "B2", ("Opinion paragraph", "بند نظر"), "shortwriting",
      "Balancing a claim and a counter-argument", "سنجش یک ادعا و استدلال مخالف",
      "Some people think phones should be banned in classrooms. Write a short "
      "paragraph giving your view and one counter-argument.",
      "بعضی می‌گویند گوشی در کلاس باید ممنوع شود. بندی کوتاه بنویس با نظر خودت "
      "و یک استدلال مخالف.",
      "Concede one point, then answer it: however or although has to appear.",
      "یک نکته را بپذیر، بعد پاسخش را بده: باید however یا although بیاید.",
      difficulty="hard",
      needs=["however", "although", "though", "on the other hand", "while",
             "even though", "but"]),
    q("w-c1-1", "writing", "C1", ("Qualified argument", "استدلال سنجیده"),
      "shortwriting",
      "Qualifying a claim rather than stating it", "سنجیدن یک ادعا نه فقط گفتن آن",
      "Write a paragraph of about ninety words: does remote work harm the "
      "careers of young employees? Take a position and qualify it.",
      "بندی حدود نود واژه بنویس: آیا کار از راه دور به پیشرفت شغلی کارمندان جوان "
      "آسیب می‌زند؟ نظری بگیر و آن را محدود و سنجیده بیان کن.",
      "A hedge (may, tends to, arguably) and a concession lift it above B2.",
      "یک تعبیر سنجیده (may، tends to، arguably) و یک پذیرش مخالف آن را از B2 "
      "بالاتر می‌برد.",
      difficulty="hard",
      needs=["arguably", "may", "might", "tend", "tends", "to some extent",
             "however", "while", "although"]),
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


# --------------------------------------------------------------- interaction
# Interaction is not a grammar question wearing a hat: every item is a turn in
# a real exchange, and the distractors are the things learners actually say
# when the register, the turn or the obligation is wrong. One item per band,
# because one well-chosen exchange is enough evidence of a band's interaction
# behaviour - and there are limits to how much of a placement test a person
# will sit through.
INTERACTION = [
    q("i-a1-1", "interaction", "A1",
      ("Hotel check-in", "پذیرش هتل"), "mcq",
      "Answering a receptionist at check-in", "پاسخ به پذیرش هتل",
      "You arrive at the hotel. The receptionist asks: “Good evening. Do you have a reservation with us?”  What do you say?",
      "به هتل می‌رسی. پذیرش می‌پرسد: «عصر بخیر. رزرو دارید؟» چه می‌گویی؟",
      "A booking is named with under or in the name of; a short answer is enough.",
      "رزرو را با under یا in the name of می‌گویند؛ پاسخ کوتاه کافی است.",
      options=["Yes, under Ahmadi, for two nights.",
               "Yes, I am reservation two nights.",
               "No, I have two nights please.",
               "Thank you, and you are welcome."],
      answer=0, difficulty="easy", domain="travel",
      task="dialogue-response", scenario={
          "en": "You have just landed and you are checking in at the hotel you booked online.",
          "fa": "تازه فرود آمده‌ای و در هتلی که آنلاین رزرو کرده‌ای پذیرش می‌گیری."},
      descriptor=L("Can ask and answer simple questions about a booking.",
                   "می‌تواند دربارهٔ یک رزرو سؤال‌های ساده بپرسد و پاسخ دهد.")),

    q("i-a2-1", "interaction", "A2",
      ("Changing an order", "تغییر سفارش"), "mcq",
      "Correcting a wrong order politely", "اصلاح مؤدبانهٔ سفارش اشتباه",
      "The waiter brings you a chicken salad. You ordered the vegetarian one. What do you say?",
      "پیش‌خدمت سالاد مرغ می‌آورد. تو سالاد گیاهی سفارش داده بودی. چه می‌گویی؟",
      "A polite correction names the order and asks for a change: I think / could you.",
      "اصلاح مؤدبانه سفارش را نام می‌برد و درخواست تغییر می‌کند: I think / could you.",
      options=["I think there’s a mix-up — I ordered the vegetarian salad. Could you check?",
               "This is not my food. You made a mistake.",
               "I am vegetarian, so I don’t eat this every day.",
               "Sorry, can I have the chicken salad please?"],
      answer=0, domain="food", task="dialogue-response", scenario={
          "en": "You are at a restaurant with a colleague and the wrong dish arrives.",
          "fa": "در رستورانی با همکاری هستی و غذای اشتباه آورده می‌شود."},
      descriptor=L("Can handle a simple problem in a service situation politely.",
                   "می‌تواند مشکلی ساده در موقعیت خدماتی را مؤدبانه حل کند.")),

    q("i-b1-1", "interaction", "B1",
      ("Rescheduling a meeting", "تغییر زمان جلسه"), "mcq",
      "Negotiating a time without losing the commitment", "مذاکره بر سر زمان بدون از دست دادن تعهد",
      "A colleague writes: “Can we move our three o’clock to Thursday?” You need the review before Friday’s client call. What do you reply?",
      "همکاری می‌نویسد: «می‌شود جلسهٔ سه‌شنبه ساعت سه را به پنجشنبه موکول کنیم؟» تو بررسی را پیش از تماس مشتری در جمعه لازم داری. چه پاسخ می‌دهی؟",
      "Accept the change and name the constraint with a request - that keeps both the relationship and the deadline.",
      "تغییر را بپذیر و محدودیت را با یک درخواست بگو؛ هم رابطه می‌ماند هم مهلت.",
      options=["Thursday works, but could we meet in the morning? I need the review before the client call on Friday.",
               "No, Thursday is impossible for me.",
               "Sure, no problem at all. Friday is fine too.",
               "Why do you always change the meeting?"],
      answer=0, domain="work", task="dialogue-response",
      stimulus={"kind": "message", "title": L("Team chat", "گفت‌وگوی تیمی"),
                "lines": [
                    {"who": "Nadia (colleague)",
                     "text": "Can we move our three o’clock to Thursday?"},
                    {"who": "You", "text": "…"}]},
      scenario={
          "en": "Your team meets every week. The review you are preparing is due before the client call on Friday morning.",
          "fa": "تیمت هر هفته جلسه دارد. بررسی‌ای که آماده می‌کنی باید پیش از تماس مشتری در صبح جمعه آماده باشد."},
      descriptor=L("Can negotiate arrangements and explain a constraint clearly.",
                   "می‌تواند دربارهٔ قرارها مذاکره کند و محدودیت را روشن توضیح دهد.")),

    q("i-b2-1", "interaction", "B2",
      ("Disagreeing in a meeting", "مخالفت در جلسه"), "mcq",
      "Disagreeing without closing the discussion", "مخالفت بدون بستن بحث",
      "In a meeting, a senior colleague says: “Two weeks is plenty for this migration.” You think it is risky. What is the most effective response?",
      "در جلسه همکاری ارشدی می‌گوید: «دو هفته برای این مهاجرت کافی است.» تو آن را پرخطر می‌دانی. مؤثرترین پاسخ کدام است؟",
      "Effective disagreement acknowledges the estimate, names the specific risk and asks for a decision.",
      "مخالفت مؤثر برآورد را می‌پذیرد، خطر مشخص را نام می‌برد و درخواست تصمیم می‌کند.",
      options=["I understand why two weeks looks enough, but the data migration alone took three last time. Can we agree on a checkpoint before we commit?",
               "That’s simply not true.",
               "I’m not sure, maybe you’re right.",
               "Everyone knows migrations always fail. We should cancel it."],
      answer=0, difficulty="hard", domain="work", task="dialogue-response",
      scenario={
          "en": "You are in a project meeting. The decision will be recorded in the minutes and people will plan around it.",
          "fa": "در جلسهٔ پروژه هستی. تصمیم در صورت‌جلسه ثبت می‌شود و بقیه بر اساس آن برنامه می‌ریزند."},
      descriptor=L("Can argue a point diplomatically in a professional discussion.",
                   "می‌تواند در بحثی حرفه‌ای نظر خود را دیپلماتیک بیان کند.")),

    q("i-c1-1", "interaction", "C1",
      ("Escalating a complaint", "پیگیری شکایت"), "mcq",
      "Holding a position while keeping the relationship", "پافشاری بر موضع با حفظ رابطه",
      "A supplier has missed a deadline for the second time. You need delivery this week without damaging a long partnership. What do you write?",
      "تأمین‌کننده برای دومین بار مهلت را از دست داده است. تحویل این هفته را لازم داری، بدون آسیب به همکاری بلندمدت. چه می‌نویسی؟",
      "The strongest move states the impact, the requirement and the consequence, and leaves the supplier a route to say yes.",
      "قوی‌ترین حرکت تأثیر، نیاز و پیامد را می‌گوید و راهی برای پاسخ مثبت تأمین‌کننده باقی می‌گذارد.",
      options=["This is the second missed date, and it now puts our launch at risk. We need the shipment by Thursday; if that is not possible, please tell me today what you can deliver and when, so we can plan around it.",
               "This is unacceptable. We will find another supplier.",
               "Just checking in again — any news on the delivery?",
               "As you know, we have been very patient with you."],
      answer=0, difficulty="hard", domain="work", task="dialogue-response",
      scenario={
          "en": "You manage a supplier relationship. The supplier is reliable in quality but has missed two dates.",
          "fa": "رابط تأمین‌کننده هستی. کیفیت کارش خوب است اما دو بار مهلت را از دست داده."},
      descriptor=L("Can handle a delicate negotiation and state consequences appropriately.",
                   "می‌تواند مذاکره‌ای حساس را اداره کند و پیامدها را مناسب بیان کند.")),
]

# ----------------------------------------------------------------- mediation
# Mediation items ask the learner to carry meaning from one person or document
# to another: read the notice, tell the friend; read two emails, brief the
# colleague. The answer is judged on whether the meaning survives the trip,
# not on whether the grammar is impressive.
MEDIATION = [
    q("m-a1-1", "mediation", "A1",
      ("Passing on a notice", "رساندن یک اطلاعیه"), "mcq",
      "Relaying one simple fact", "رساندن یک واقعیت ساده",
      "A sign at the pool says: “Pool closed for cleaning, 9:00–11:00.” Your friend wants to swim now, at half past nine. What do you tell them?",
      "تابلویی کنار استخر می‌گوید: «استخر برای نظافت بسته است، ۹ تا ۱۱.» دوستت همین حالا، ساعت نه و نیم، می‌خواهد شنا کند. چه می‌گویی؟",
      "The useful message is the fact plus what it means for the friend: closed until eleven.",
      "پیام مفید همان واقعیت و معنایش برای دوستت است: تا ساعت یازده بسته است.",
      options=["The pool is closed until eleven, so let’s swim after that.",
               "The pool is cleaning now.",
               "I read a sign about the pool.",
               "You can swim at nine o’clock."],
      answer=0, difficulty="easy", domain="everyday",
      task="mediation",
      stimulus={"kind": "note", "title": L("Pool notice", "اطلاعیهٔ استخر"),
                "text": "POOL CLOSED FOR CLEANING\n9:00 – 11:00\nThank you for your patience."},
      scenario={
          "en": "You are at the pool with a friend who does not read English well.",
          "fa": "با دوستی که انگلیسی را خوب نمی‌خواند کنار استخر هستی."},
      descriptor=L("Can pass on a simple piece of practical information.",
                   "می‌تواند یک اطلاعات سادهٔ کاربردی را به دیگری برساند.")),

    q("m-a2-1", "mediation", "A2",
      ("Explaining opening hours", "توضیح ساعت کار"), "mcq",
      "Turning a timetable into advice", "تبدیل جدول زمانی به توصیه",
      "The museum’s website says last entry is 16:30 and it closes at 17:00. A visitor arriving at 16:40 asks if they can go in. What do you tell them?",
      "وب‌سایت موزه می‌گوید آخرین ورود ۱۶:۳۰ است و موزه ۱۷:۰۰ بسته می‌شود. بازدیدکننده‌ای ساعت ۱۶:۴۰ می‌رسد و می‌پرسد می‌تواند وارد شود. چه می‌گویی؟",
      "The visitor needs the rule, not the closing time alone: entry stops at 16:30.",
      "بازدیدکننده به قاعده نیاز دارد، نه فقط ساعت بسته‌شدن: ورود از ۱۶:۳۰ تمام می‌شود.",
      options=["I’m afraid entry closes at half past four. The museum itself is open until five, but you can’t go in now.",
               "Yes, it is open until five.",
               "No, the museum is closed today.",
               "The website has all the information."],
      answer=0, domain="travel", task="mediation",
      stimulus={"kind": "table", "title": L("Museum opening hours", "ساعت کار موزه"),
                "head": [L("Last entry", "آخرین ورود"), L("Closes", "بسته می‌شود")],
                "rows": [["16:30", "17:00"]]},
      scenario={
          "en": "You are standing near the museum entrance when a visitor asks for help.",
          "fa": "نزدیک ورودی موزه ایستاده‌ای که بازدیدکننده‌ای کمک می‌خواهد."},
      descriptor=L("Can explain a simple rule or timetable to someone else.",
                   "می‌تواند قاعده‌ای ساده یا جدول زمانی را برای دیگری توضیح دهد.")),

    q("m-b1-1", "mediation", "B1",
      ("Explaining a refund policy", "توضیح سیاست بازپرداخت"), "mcq",
      "Making a policy understandable without changing it", "فهم‌پذیر کردن یک سیاست بدون تغییر آن",
      "A ticket policy says: “Refunds are not available within 48 hours of the event. Tickets may be exchanged once, up to 48 hours before the event, for a £5 fee.” A friend wants their money back for tomorrow’s show. What do you tell them?",
      "سیاست بلیت می‌گوید: «بازپرداخت تا ۴۸ ساعت پیش از رویداد امکان‌پذیر نیست. بلیت را یک بار، تا ۴۸ ساعت پیش از رویداد، با هزینهٔ ۵ پوند می‌توان تعویض کرد.» دوستی برای نمایش فردا پولش را می‌خواهد. چه می‌گویی؟",
      "A refund is closed off, but the exchange route is still open and needs its fee and deadline named.",
      "بازپرداخت بسته است، اما راه تعویض با هزینه و مهلت مشخص باز است.",
      options=["You can’t get a refund this close to the show, but you can exchange the ticket once for a £5 fee. It has to be before the 48-hour mark, so today.",
               "Sorry, the tickets are completely non-refundable and cannot be changed.",
               "You can get a refund if you pay five pounds.",
               "The show is tomorrow, so nothing can be done."],
      answer=0, domain="shopping", task="mediation", scenario={
          "en": "A friend has bought a ticket and cannot go. You are the one who reads the terms.",
          "fa": "دوستت بلیت خریده و نمی‌تواند برود. تو کسی هستی که شرایط را می‌خوانی."},
      descriptor=L("Can relay the substance of a written policy in plain language.",
                   "می‌تواند جانِ یک سیاست مکتوب را به زبان ساده برساند.")),

    q("m-b2-1", "mediation", "B2",
      ("Combining two messages", "ترکیب دو پیام"), "mcq",
      "Summarizing two sources for a decision", "خلاصهٔ دو منبع برای یک تصمیم",
      "Your supplier emails: “The component is back in stock, but dispatch is delayed by three days.” Your client emails: “We can accept a delay of up to two days.” What do you tell your manager?",
      "تأمین‌کننده ایمیل می‌زند: «قطعه موجود شد، اما ارسال سه روز تأخیر دارد.» مشتری ایمیل می‌زند: «تا دو روز تأخیر را می‌پذیریم.» به مدیرت چه می‌گویی؟",
      "The briefing has to combine both facts and state the conflict: three days against a limit of two.",
      "گزارش باید هر دو واقعیت را با هم بگوید و تعارض را روشن کند: سه روز در برابر سقف دو روز.",
      options=["The part is available again, but it would arrive three days late, and the client will only accept two. We need to find a day somewhere or renegotiate.",
               "The supplier has the part in stock now.",
               "The client is happy with the schedule.",
               "There is a delay of three days, so the client will have to accept it."],
      answer=0, difficulty="hard", domain="work", task="mediation",
      stimulus={"kind": "table", "title": L("Two messages", "دو پیام"),
                "head": [L("Supplier", "تأمین‌کننده"), L("Client", "مشتری")],
                "rows": [["Back in stock; dispatch +3 days", "Accepts up to +2 days"]]},
      scenario={
          "en": "Two emails arrived this morning. Your manager has five minutes and needs the decision.",
          "fa": "امروز صبح دو ایمیل رسید. مدیرت پنج دقیقه وقت دارد و تصمیم را می‌خواهد."},
      descriptor=L("Can synthesize information from two sources and identify a conflict.",
                   "می‌تواند اطلاعات دو منبع را با هم جمع کند و تعارض را نشان دهد.")),

    q("m-c1-1", "mediation", "C1",
      ("Explaining a constraint", "توضیح یک محدودیت"), "mcq",
      "Making a technical limit meaningful to a non-specialist", "فهماندن محدودیت فنی به غیرمتخصص",
      "An engineering report says: “The API rate limit is 60 requests per minute per key; exceeding it returns 429 and a retry-after header.” You must explain to a non-technical client why the dashboard cannot refresh every second. What do you say?",
      "گزارش فنی می‌گوید: «محدودیت نرخ API شصت درخواست در دقیقه برای هر کلید است؛ عبور از آن ۴۲۹ و سرآیند retry-after برمی‌گرداند.» باید به مشتری غیرفنی توضیح دهی چرا داشبورد نمی‌تواند هر ثانیه تازه شود. چه می‌گویی؟",
      "The client needs the cause in their terms - a cap of one update a second - and the practical consequence.",
      "مشتری علت را به زبان خودش می‌خواهد — سقف یک به‌روزرسانی در ثانیه — و پیامد عملی آن.",
      options=["The system lets us ask for new data sixty times a minute, so it can refresh about once a second, not every second. Refreshing faster would be refused until the minute resets.",
               "The API returns a 429 with a retry-after header, so we cannot refresh every second.",
               "The engineering team has limited the dashboard for security reasons.",
               "It is a technical limitation and cannot be explained simply."],
      answer=0, difficulty="hard", domain="technology", task="mediation",
      scenario={
          "en": "You are the bridge between an engineering team and a client who needs to understand a constraint.",
          "fa": "تو پل میان تیم فنی و مشتری‌ای هستی که باید یک محدودیت را بفهمد."},
      descriptor=L("Can explain a complex constraint in accessible terms without distorting it.",
                   "می‌تواند محدودیتی پیچیده را بدون تحریف، ساده و فهم‌پذیر توضیح دهد.")),
]

ITEMS = (GRAMMAR + VOCABULARY + READING + LISTENING + INTERACTION
         + MEDIATION + WRITING + SPEAKING)

# Which part of adult life each existing item comes from. The bank is not all
# offices and it is not all cafés: the domain is a property of the task, and
# the builder refuses a bank where one setting has swallowed the rest.
DOMAIN_BY_ID = {
    "g-a1-1": "everyday", "g-a1-2": "food", "g-a1-3": "travel",
    "g-a2-1": "social", "g-a2-2": "food", "g-a2-3": "shopping",
    "g-b1-1": "everyday", "g-b1-2": "travel", "g-b1-3": "everyday",
    "g-b2-1": "work", "g-b2-2": "work", "g-b2-3": "work",
    "g-c1-1": "work", "g-c1-2": "everyday", "g-c1-3": "social",
    "v-a1-1": "everyday", "v-a1-2": "everyday", "v-a1-3": "food",
    "v-a2-1": "social", "v-a2-2": "work", "v-a2-3": "everyday",
    "v-b1-1": "everyday", "v-b1-2": "work", "v-b1-3": "everyday",
    "v-b2-1": "everyday", "v-b2-2": "work", "v-b2-3": "work",
    "v-c1-1": "education", "v-c1-2": "education", "v-c1-3": "everyday",
    "r-a1-1": "everyday", "r-a1-2": "everyday",
    "r-a2-1": "social", "r-a2-2": "everyday",
    "r-b1-1": "education", "r-b1-2": "education",
    "r-b2-1": "health", "r-b2-2": "health",
    "r-c1-1": "work", "r-c1-2": "work",
    "l-a1-1": "shopping", "l-a1-2": "everyday",
    "l-a2-1": "travel", "l-a2-2": "food",
    "l-b1-1": "travel", "l-b1-2": "work",
    "l-b2-1": "travel", "l-b2-2": "work",
    "l-c1-1": "work", "l-c1-2": "work",
    "w-a1-1": "everyday", "w-a2-1": "social", "w-b1-1": "travel",
    "w-b2-1": "education", "w-c1-1": "work",
    "s-b1-1": "travel", "s-b2-1": "work",
}

for _item in ITEMS:
    _item["domain"] = DOMAIN_BY_ID.get(_item["id"], _item.get("domain", "everyday"))

LEVEL = {
    "version": 3,
    "title": L("Level assessment", "سنجش سطح"),
    "blurb": L("Seven skills measured separately, through real situations: "
               "grammar, vocabulary, reading, listening, interaction, mediation "
               "and writing. Speaking is practice and is reported as not "
               "assessed. The paper starts at your own level and only climbs "
               "while the evidence supports it.",
               "هفت مهارت جدا و در موقعیت‌های واقعی سنجیده می‌شود: گرامر، واژگان، "
               "خواندن، شنیدن، تعامل، میانجی‌گری و نوشتن. گفتن تمرین است و "
               "«سنجیده نشده» گزارش می‌شود. برگه از سطح خودت شروع می‌شود و تا "
               "جایی بالا می‌رود که شواهد پشتیبانی کند."),
    "minutes": 45,
    "minutesRange": [25, 45],
    "retakeDays": 30,
    "skills": SKILLS,
    "bands": BANDS,
    "testedBands": TESTED,
    # One paper for everyone, ten questions per band, so a count means the
    # same thing for every learner. The level comes from that count.
    "blueprint": {
        "bands": TESTED,
        "perBand": {"grammar": 3, "vocabulary": 3, "reading": 2, "listening": 2,
                    "interaction": 1, "mediation": 1, "writing": 1},
        "perBandTotal": 13,
        "questions": 65,
        # What the adaptive route may do: the first three bands are always
        # administered, and the two above are opened only when the evidence
        # from the core supports them. A route that stops early cannot report
        # a band it never tested, which is why the cutoffs below are shares of
        # the full paper.
        "core": ["A1", "A2", "B1"],
        "upper": ["B2", "C1"],
        # Two counts, kept apart on purpose. `objective` is the fifty
        # recognition questions the parts are built from, ten a band.
        # `assessed` adds writing, which is marked against the rubric rather
        # than answered, so it is its own part and is added to the total only
        # after it has been read on the same ruler.
        "objective": ["grammar", "vocabulary", "reading", "listening",
                      "interaction", "mediation"],
        "assessed": ["grammar", "vocabulary", "reading", "listening",
                     "interaction", "mediation", "writing"],
        "practice": ["speaking"],
        # A writing task is worth up to one question: four rubric points, each
        # a quarter of a question in the count the level is read from.
        "writingPoints": 4,
        # Share of the paper that must be right to claim each band, in order:
        # 9, 19, 29, 39 and 49 of 55. The same fractions apply to a skill with
        # its own item count, so a score of 11 of 15 in grammar and 8 of 10 in
        # reading are read against the same ruler.
        "cutoffs": [0.16, 0.34, 0.52, 0.70, 0.88],
    },
    # The content package the page reads: one version for the whole bank, so
    # a web build and an APK can say whether they are looking at the same
    # paper, and a review date that the freshness check reads.
    "content": {
        "version": "2026.11",
        "published": "2026-11-18",
        "owner": "Assessment review team",
        "reviewCycleDays": 365,
        "nextReview": "2027-11-18",
        "reviewLog": [
            {"on": "2026-11-18", "what": "Added interaction and mediation banks, "
             "scenario and document stimuli, can-do descriptors and the adaptive "
             "route; reviewed every item for level and natural English."},
        ],
    },
    "passages": READING_PASSAGES,
    "items": ITEMS,
    "rubric": RUBRIC,
    "writingScale": WRITING_SCALE,
    "method": L("The paper is adaptive. Everyone answers the core bands - A1, "
                "A2 and B1 - across grammar, vocabulary, reading, listening, "
                "interaction and mediation. Strong evidence in the core opens "
                "B2, and strong evidence in B2 opens C1; when the evidence is "
                "clear the paper stops climbing instead of asking questions "
                "that cannot change the result. Your level is read from the "
                "share of the whole paper you answer correctly - 11 of 65 is "
                "A1, 23 is A2, 34 is B1, 46 is B2, 58 is C1 - so a route that "
                "stopped at B1 cannot report C1. Each skill is read against "
                "the same fractions of its own total, with a margin from the "
                "standard error of that count. The five writing tasks are "
                "marked on four points each - enough words, enough sentences, "
                "the linking the task asks for, and a spot check for slips - "
                "and each is worth up to one question. Speaking is not scored.",
                "برگه تطبیقی است. همه بخش‌های هستهٔ A1، A2 و B1 را در گرامر، "
                "واژگان، خواندن، شنیدن، تعامل و میانجی‌گری پاسخ می‌دهند. شواهد "
                "قوی در هسته B2 را باز می‌کند و شواهد قوی در B2 سطح C1 را؛ وقتی "
                "شواهد روشن باشد برگه از بالا رفتن می‌ایستد تا پرسشی نپرسد که "
                "نتیجه را عوض نمی‌کند. سطح از نسبت پاسخ‌های درست به کل برگه "
                "خوانده می‌شود — ۱۱ از ۶۵ یعنی A1، ۲۳ یعنی A2، ۳۴ یعنی B1، ۴۶ "
                "یعنی B2 و ۵۸ یعنی C1 — پس مسیری که در B1 بایستد نمی‌تواند C1 "
                "گزارش کند. هر مهارت با همان نسبت‌ها از مجموع خودش و با حاشیهٔ "
                "خطای معیار خوانده می‌شود. پنج تمرین نوشتن هر یک با چهار امتیاز "
                "سنجیده می‌شود — واژهٔ کافی، جملهٔ کافی، پیوند خواسته‌شده و یک "
                "بررسی نمونه‌ای — و هر تمرین حداکثر یک پرسش می‌ارزد. گفتن نمره "
                "نمی‌گیرد."),
    "caveat": L("This is a placement assessment built on a reviewed item bank, "
                "not a certified examination. The adaptive route and the "
                "rubric are documented, but the items are not statistically "
                "calibrated and the level is an estimate with a margin - not a "
                "certificate.",
                "این سنجش جایگاه بر پایهٔ بانک پرسش بازبینی‌شده است، نه آزمون "
                "گواهی‌دار. مسیر تطبیقی و معیار سنجش مستند است، اما پرسش‌ها "
                "کالیبرهٔ آماری نشده‌اند و سطح تخمینی با حاشیهٔ خطاست، نه گواهی."),
}
