"""Curated word-use content for the vocabulary knowledge base.

Everything in `vocab_use.json` that the app cannot derive from the files it
already ships is authored here, once, and validated by build_vocab_use.py and
check_vocab_use.py. The rule the brief sets is the rule this file follows:

  * no invented meanings - the senses and Persian glosses come from
    senses.json and glossary.json, never from this file;
  * no invented pronunciation - IPA comes from senses.json, and the syllable
    count and stress position are read off that IPA;
  * what is added here is what a dictionary does not hold: the family, the
    collocations, the grammatical patterns, the learner mistakes, the
    Persian-transfer traps, and short passages that show the word at work.

Each word entry may carry:

    fam     word family: [{w, pos, fa}]
    colls   collocations: [{en, fa, ex?}]
    pats    grammatical patterns: [{p, ex, fa}]
    reg     neutral | formal | informal, and reg_note when it needs saying
    infl    inflections worth showing for this word's part of speech
    bad     learner mistakes: [{bad, good, why}]
    bridge  the Persian-transfer trap for this word: {bad, good, why}
    use     production prompts: [{task, frame, example}]
    wild    ids of WILD passages that belong to this word (attached by the
            builder, so a passage is written once and shared)

WILD entries are the "word in the wild" material: a short, natural text with
the target expressions in it, one question about the meaning, and the answer.
The builder checks that every listed word really appears in the text.
"""

WORDS = {}

# --------------------------------------------------------------------------
# Character adjectives, B1. The set a learner uses about people they know, so
# the collocations and the patterns matter more here than the definition does.
# --------------------------------------------------------------------------


def _add(word, **fields):
    WORDS[word] = fields


_add(
    "confident",
    fam=[{"w": "confidence", "pos": "noun", "fa": "اعتماد به نفس"},
         {"w": "confidently", "pos": "adverb", "fa": "با اعتماد به نفس"}],
    colls=[{"en": "feel confident", "fa": "احساس اطمینان کردن",
            "ex": "I feel confident about the interview."},
           {"en": "confident about something", "fa": "مطمئن دربارهٔ چیزی"},
           {"en": "confident in your abilities", "fa": "به توانایی‌هایت مطمئن"},
           {"en": "a confident speaker", "fa": "سخنرانِ با اعتماد به نفس"}],
    pats=[{"p": "confident about / of + noun",
           "ex": "She is confident about her decision.", "fa": "مطمئن دربارهٔ ..."},
          {"p": "confident that + clause", "ex": "I am confident that it will work.",
           "fa": "مطمئنم که ..."}],
    bad=[{"bad": "I am confident on my answer.",
          "good": "I am confident about my answer.",
          "why": "The adjective takes about (or of) for the thing you are sure "
                 "of; on belongs to depend on and rely on, not to confident."}],
    bridge={"bad": "I have confident.",
            "good": "I am confident.",
            "why": "Confident is an adjective, not a noun: the noun is "
                   "confidence. Persian «اعتماد به نفس دارم» maps to "
                   "I am confident, not I have confident."},
    use=[{"task": "Describe a decision you feel good about.",
          "frame": "I am confident about … because …",
          "example": "I am confident about my choice because I checked the prices."}],
    wild=["meeting"],
)

_add(
    "honest",
    fam=[{"w": "honesty", "pos": "noun", "fa": "صداقت"},
         {"w": "honestly", "pos": "adverb", "fa": "صادقانه"},
         {"w": "dishonest", "pos": "adjective", "fa": "ناصادق"}],
    colls=[{"en": "an honest answer", "fa": "پاسخ صادقانه"},
           {"en": "be honest about something", "fa": "دربارهٔ چیزی صادق بودن"},
           {"en": "to be honest", "fa": "راستش را بخواهی"}],
    pats=[{"p": "honest with somebody", "ex": "Be honest with me.",
           "fa": "با من صادق باش."},
          {"p": "honest about something", "ex": "He was honest about the mistake.",
           "fa": "دربارهٔ اشتباه صادق بود."}],
    bad=[{"bad": "She is honest to me.", "good": "She is honest with me.",
          "why": "Honest with a person, honest about a thing."}],
    bridge={"bad": "He said me the truth.",
            "good": "He told me the truth.",
            "why": "Persian «به من گفت» takes an object, so say and tell get "
                   "swapped: tell takes the person, say does not."},
    use=[{"task": "Tell someone an honest opinion about a film.",
          "frame": "To be honest, …",
          "example": "To be honest, the ending felt too long."}],
)

_add(
    "polite",
    fam=[{"w": "politely", "pos": "adverb", "fa": "با ادب"},
         {"w": "politeness", "pos": "noun", "fa": "ادب"},
         {"w": "impolite", "pos": "adjective", "fa": "بی‌ادب"}],
    colls=[{"en": "a polite request", "fa": "درخواست مؤدبانه"},
           {"en": "a polite conversation", "fa": "گفت‌وگوی مؤدبانه"},
           {"en": "polite to somebody", "fa": "مؤدب با کسی"}],
    pats=[{"p": "polite to + person", "ex": "She is polite to everyone.",
           "fa": "با همه مؤدب است."},
          {"p": "it is polite to + verb", "ex": "It is polite to say thank you.",
           "fa": "مؤدبانه است که تشکر کنی."}],
    bad=[{"bad": "He is polite with me.", "good": "He is polite to me.",
          "why": "Polite takes to for the person it is shown to."}],
    use=[{"task": "Write a polite request to a neighbour.",
          "frame": "Could you possibly …?",
          "example": "Could you possibly keep the music down after ten?"}],
)

_add(
    "patient",
    fam=[{"w": "patience", "pos": "noun", "fa": "صبر"},
         {"w": "patiently", "pos": "adverb", "fa": "با صبر"},
         {"w": "impatient", "pos": "adjective", "fa": "بی‌حوصله"}],
    colls=[{"en": "be patient with somebody", "fa": "با کسی صبور بودن"},
           {"en": "lose patience", "fa": "صبر از دست دادن"},
           {"en": "a patient teacher", "fa": "معلمی صبور"}],
    pats=[{"p": "patient with + person", "ex": "Please be patient with the new staff.",
           "fa": "با کارکنان تازه صبور باش."},
          {"p": "patient about + thing", "ex": "Try to be patient about the delay.",
           "fa": "دربارهٔ تأخیر صبور باش."}],
    bad=[{"bad": "I have not patient.", "good": "I am not patient.",
          "why": "Patient is an adjective; the noun is patience, and the "
                 "negative of the noun is not patience."}],
    use=[{"task": "Describe a time you had to wait for something.",
          "frame": "It was hard to be patient when …",
          "example": "It was hard to be patient when the bus was late again."}],
)

_add(
    "punctual",
    fam=[{"w": "punctuality", "pos": "noun", "fa": "وقت‌شناسی"},
         {"w": "punctually", "pos": "adverb", "fa": "سر وقت"}],
    colls=[{"en": "be punctual for something", "fa": "برای چیزی سر وقت بودن"},
           {"en": "punctual arrival", "fa": "رسیدن سر وقت"}],
    pats=[{"p": "punctual for + event", "ex": "He is always punctual for meetings.",
           "fa": "او همیشه سر وقت در جلسه‌ها حاضر است."}],
    bad=[{"bad": "I am punctual in the class.", "good": "I am punctual for the class.",
          "why": "Punctual for an event, punctual at work; in is the usual "
                 "translation trap from «در کلاس»."}],
    use=[{"task": "Say why being on time matters where you work or study.",
          "frame": "Being punctual matters because …",
          "example": "Being punctual matters because the whole team waits for you."}],
)

_add(
    "reliable",
    fam=[{"w": "rely", "pos": "verb", "fa": "اتکا کردن"},
         {"w": "reliability", "pos": "noun", "fa": "قابل‌اعتماد بودن"},
         {"w": "unreliable", "pos": "adjective", "fa": "غیرقابل‌اعتماد"}],
    colls=[{"en": "a reliable source", "fa": "منبعی قابل‌اعتماد"},
           {"en": "reliable information", "fa": "اطلاعات قابل‌اعتماد"},
           {"en": "a reliable car", "fa": "خودرویی قابل‌اعتماد"}],
    pats=[{"p": "rely on somebody / something",
           "ex": "You can rely on her to be early.", "fa": "می‌توانی روی او حساب کنی."}],
    bad=[{"bad": "You can rely her.", "good": "You can rely on her.",
          "why": "The verb rely needs on; the adjective reliable does not."}],
    use=[{"task": "Describe someone you can depend on.",
          "frame": "I can rely on … because …",
          "example": "I can rely on my brother because he always keeps his word."}],
)

_add(
    "curious",
    fam=[{"w": "curiosity", "pos": "noun", "fa": "کنجکاوی"},
         {"w": "curiously", "pos": "adverb", "fa": "با کنجکاوی"}],
    colls=[{"en": "curious about something", "fa": "کنجکاو دربارهٔ چیزی"},
           {"en": "curious to know", "fa": "مشتاق دانستن"},
           {"en": "curious eyes", "fa": "چشم‌های کنجکاو"}],
    pats=[{"p": "curious about + noun", "ex": "I am curious about the result.",
           "fa": "دربارهٔ نتیجه کنجکاوم."},
          {"p": "curious to + verb", "ex": "She was curious to see the message.",
           "fa": "مشتاق بود پیام را ببیند."}],
    bad=[{"bad": "I am curious to the history of this city.",
          "good": "I am curious about the history of this city.",
          "why": "Curious about a subject, curious to do something."}],
    use=[{"task": "Ask someone a question you really want answered.",
          "frame": "I'm curious about …",
          "example": "I'm curious about how you learned to cook."}],
)

# --------------------------------------------------------------------------
# Everyday service words: the ones a learner uses in a shop, a restaurant and
# at a bank, where the natural English is a fixed pattern rather than a
# translation of the Persian sentence.
# --------------------------------------------------------------------------

_add(
    "recommend",
    fam=[{"w": "recommendation", "pos": "noun", "fa": "توصیه"}],
    colls=[{"en": "highly recommend", "fa": "قویاً توصیه کردن",
            "ex": "I highly recommend this restaurant."},
           {"en": "recommend something to somebody", "fa": "چیزی را به کسی توصیه کردن"}],
    pats=[{"p": "recommend + noun", "ex": "Can you recommend a good hotel?",
           "fa": "هتلی خوب پیشنهاد می‌کنی؟"},
          {"p": "recommend + -ing", "ex": "I recommend booking early.",
           "fa": "توصیه می‌کنم زود رزرو کنی."},
          {"p": "recommend that + clause", "ex": "She recommends that we wait.",
           "fa": "توصیه می‌کند صبر کنیم."}],
    bad=[{"bad": "Can you recommend me a good restaurant?",
          "good": "Can you recommend a good restaurant to me?",
          "why": "Recommend is not like give: the thing comes first and the "
                 "person takes to, or use recommend somebody something only for "
                 "people (I recommend him for the job)."}],
    bridge={"bad": "I recommend you this book.",
            "good": "I recommend this book to you.",
            "why": "Persian puts the person first («به تو این کتاب را توصیه "
                   "می‌کنم»); English recommends the thing and gives the person "
                   "to."},
    use=[{"task": "Recommend a place in your city to a visitor.",
          "frame": "I'd recommend … because …",
          "example": "I'd recommend the old bazaar because it is quieter in the morning."}],
)

_add(
    "reservation",
    fam=[{"w": "reserve", "pos": "verb", "fa": "رزرو کردن"},
         {"w": "reserved", "pos": "adjective", "fa": "رزرو شده"}],
    colls=[{"en": "make a reservation", "fa": "رزرو کردن",
            "ex": "I'd like to make a reservation for two."},
           {"en": "cancel a reservation", "fa": "رزرو را لغو کردن"},
           {"en": "a reservation for four", "fa": "رزرو برای چهار نفر"}],
    pats=[{"p": "make a reservation for + number / time",
           "ex": "She made a reservation for eight o'clock.",
           "fa": "برای ساعت هشت رزرو کرد."},
          {"p": "reserve a table / a room", "ex": "We reserved a table by the window.",
           "fa": "میزی کنار پنجره رزرو کردیم."}],
    bad=[{"bad": "I want to take a reservation.",
          "good": "I'd like to make a reservation.",
          "why": "A reservation is made, not taken; take is for a seat, a "
                 "break or a photo."}],
    use=[{"task": "Book a table for four at eight o'clock.",
          "frame": "I'd like to make a reservation for …",
          "example": "I'd like to make a reservation for four at eight, please."}],
    wild=["hotel"],
)

_add(
    "borrow",
    fam=[{"w": "borrower", "pos": "noun", "fa": "قرض‌گیرنده"}],
    colls=[{"en": "borrow something from somebody", "fa": "چیزی از کسی قرض گرفتن",
            "ex": "I borrowed a pen from Sara."},
           {"en": "borrow money from a bank", "fa": "از بانک پول قرض گرفتن"}],
    pats=[{"p": "borrow + thing + from + person",
           "ex": "He borrowed the car from his neighbour.",
           "fa": "ماشین را از همسایه‌اش قرض گرفت."}],
    bad=[{"bad": "Can I borrow your pen to me?",
          "good": "Can I borrow your pen?",
          "why": "Borrow already means the thing comes to you, so adding to "
                 "me doubles the direction; the sentence needs from only when "
                 "the owner is named."}],
    bridge={"bad": "Can you borrow me your pen?",
            "good": "Can you lend me your pen?",
            "why": "Persian «قرض دادن» and «قرض گرفتن» share a root, but "
                   "English does not: lend is to give for a time, borrow is "
                   "to take for a time."},
    use=[{"task": "Ask a colleague for something you will return.",
          "frame": "Could I borrow your … until …?",
          "example": "Could I borrow your charger until the end of the meeting?"}],
)

_add(
    "lend",
    fam=[{"w": "lender", "pos": "noun", "fa": "وام‌دهنده"}],
    colls=[{"en": "lend somebody something", "fa": "چیزی به کسی قرض دادن",
            "ex": "She lent me her umbrella."},
           {"en": "lend something to somebody", "fa": "چیزی را به کسی قرض دادن"}],
    pats=[{"p": "lend + person + thing", "ex": "Can you lend me a hand?",
           "fa": "می‌شود کمکم کنی؟"},
          {"p": "lend + thing + to + person", "ex": "He lent his bike to a friend.",
           "fa": "دوچرخه‌اش را به دوستی قرض داد."}],
    bad=[{"bad": "He lended me the book.", "good": "He lent me the book.",
          "why": "The past of lend is lent, not lended; lend / lent / lent."}],
    use=[{"task": "Offer something of yours to somebody who needs it.",
          "frame": "I can lend you …",
          "example": "I can lend you my notes until Friday."}],
)

_add(
    "afford",
    fam=[{"w": "affordable", "pos": "adjective", "fa": "قابل پرداخت"},
         {"w": "affordability", "pos": "noun", "fa": "قابل پرداخت بودن"}],
    colls=[{"en": "can't afford something", "fa": "توان پرداخت چیزی را نداشتن",
            "ex": "We can't afford a bigger flat."},
           {"en": "affordable housing", "fa": "مسکن مقرون‌به‌صرفه"}],
    pats=[{"p": "can / can't afford + noun", "ex": "I can't afford that car.",
           "fa": "توان خرید آن ماشین را ندارم."},
          {"p": "can / can't afford to + verb", "ex": "We can't afford to wait.",
           "fa": "نمی‌توانیم صبر کنیم."}],
    bad=[{"bad": "I can't afford buying a new laptop.",
          "good": "I can't afford to buy a new laptop.",
          "why": "Afford takes to + verb, not -ing: the second verb is a "
                 "to-infinitive."}],
    bridge={"bad": "It is not in my money.",
            "good": "I can't afford it.",
            "why": "Persian «به پول من نمی‌خورد» has no word-for-word English; "
                   "afford is the verb that carries the whole idea."},
    use=[{"task": "Talk about something you would buy if you could.",
          "frame": "I'd love to … but I can't afford …",
          "example": "I'd love to travel in summer, but I can't afford the tickets."}],
)

_add(
    "complain",
    fam=[{"w": "complaint", "pos": "noun", "fa": "شکایت"}],
    colls=[{"en": "complain about something", "fa": "از چیزی شکایت کردن",
            "ex": "They complained about the noise."},
           {"en": "make a complaint", "fa": "شکایت کردن"},
           {"en": "complain to the manager", "fa": "به مدیر شکایت کردن"}],
    pats=[{"p": "complain about + thing", "ex": "She complained about the delay.",
           "fa": "از تأخیر شکایت کرد."},
          {"p": "complain to + person", "ex": "He complained to the receptionist.",
           "fa": "به پذیرش شکایت کرد."}],
    bad=[{"bad": "I complained the manager about the room.",
          "good": "I complained to the manager about the room.",
          "why": "The person takes to, the problem takes about; complain "
                 "never takes a direct object."}],
    bridge={"bad": "I complained from the noise.",
            "good": "I complained about the noise.",
            "why": "Persian «از ... شکایت کردم» uses the same preposition as "
                   "from, but English complains about a thing and to a person."},
    use=[{"task": "Complain politely about a problem in a hotel room.",
          "frame": "I'm afraid I have to complain about …",
          "example": "I'm afraid I have to complain about the air conditioning."}],
    wild=["hotel"],
)

# --------------------------------------------------------------------------
# A1 core: the words a beginner meets first and then needs for years. Their
# value is in the patterns they sit in, not in a longer definition.
# --------------------------------------------------------------------------

_add(
    "take",
    infl=[{"f": "takes"}, {"f": "took"}, {"f": "taken"}, {"f": "taking"}],
    fam=[{"w": "takeaway", "pos": "noun", "fa": "غذای بیرون‌بر"},
         {"w": "mistake", "pos": "noun", "fa": "اشتباه"}],
    colls=[{"en": "take a break", "fa": "استراحت کردن"},
           {"en": "take a photo", "fa": "عکس گرفتن"},
           {"en": "take care of somebody", "fa": "مراقبت کردن از کسی"},
           {"en": "take part in something", "fa": "در چیزی شرکت کردن"},
           {"en": "take your time", "fa": "عجله نکن"}],
    pats=[{"p": "take + noun (a break, a photo, a seat)",
           "ex": "Let's take a break.", "fa": "بیا استراحت کنیم."},
          {"p": "it takes + time + to + verb",
           "ex": "It takes twenty minutes to get there.",
           "fa": "بیست دقیقه طول می‌کشد تا برسیم."}],
    bad=[{"bad": "I take a shower every morning.",
          "good": "I take a shower in the morning.",
          "why": "Take a shower is correct English; the mistake this pair "
                 "catches is time: every morning (habit) versus in the "
                 "morning (part of the day)."}],
    use=[{"task": "Say how long your journey to work or school takes.",
          "frame": "It takes … minutes to …",
          "example": "It takes forty minutes to get to the office by bus."}],
)

_add(
    "make",
    infl=[{"f": "makes"}, {"f": "made"}, {"f": "making"}],
    fam=[{"w": "maker", "pos": "noun", "fa": "سازنده"},
         {"w": "make-up", "pos": "noun", "fa": "آرایش"}],
    colls=[{"en": "make a decision", "fa": "تصمیم گرفتن"},
           {"en": "make a mistake", "fa": "اشتباه کردن"},
           {"en": "make friends", "fa": "دوست پیدا کردن"},
           {"en": "make progress", "fa": "پیشرفت کردن"},
           {"en": "make an effort", "fa": "تلاش کردن"}],
    pats=[{"p": "make + somebody + verb (no to)",
           "ex": "The film made me cry.", "fa": "فیلم باعث شد گریه کنم."},
          {"p": "be made of / from + material",
           "ex": "The table is made of wood.", "fa": "میز از چوب است."}],
    bad=[{"bad": "I did a mistake in the test.",
          "good": "I made a mistake in the test.",
          "why": "English makes a mistake; do belongs to homework, the "
                 "dishes and your best."}],
    bridge={"bad": "I want to do a decision.",
            "good": "I want to make a decision.",
            "why": "Persian uses one verb for both «تصمیم گرفتن» and «انجام "
                   "دادن», and learners carry do into the fixed phrase. "
                   "English decides with make."},
    use=[{"task": "Describe a choice you made recently.",
          "frame": "I made the decision to … because …",
          "example": "I made the decision to study in the morning because I'm too tired at night."}],
)

_add(
    "run",
    infl=[{"f": "runs"}, {"f": "ran"}, {"f": "run"}, {"f": "running"}],
    fam=[{"w": "runner", "pos": "noun", "fa": "دونده"},
         {"w": "running", "pos": "noun", "fa": "دویدن"}],
    colls=[{"en": "run a business", "fa": "کسب‌وکار را اداره کردن"},
           {"en": "run out of something", "fa": "چیزی تمام شدن"},
           {"en": "run late", "fa": "دیر شدن"}],
    pats=[{"p": "run + object (a company, a meeting, a check)",
           "ex": "She runs a small studio.", "fa": "او یک استودیوی کوچک را اداره می‌کند."},
          {"p": "run out of + noun", "ex": "We ran out of milk.",
           "fa": "شیرمان تمام شد."}],
    bad=[{"bad": "He runs a marathon yesterday.",
          "good": "He ran a marathon yesterday.",
          "why": "The past of run is ran, not runs; with yesterday the "
                 "sentence needs the past form."}],
    use=[{"task": "Describe something you have run out of this week.",
          "frame": "I ran out of …",
          "example": "I ran out of coffee on Tuesday morning."}],
)

_add(
    "break",
    infl=[{"f": "breaks"}, {"f": "broke"}, {"f": "broken"}],
    fam=[{"w": "breakable", "pos": "adjective", "fa": "شکستنی"},
         {"w": "outbreak", "pos": "noun", "fa": "شیوع"}],
    colls=[{"en": "take a break", "fa": "استراحت کردن"},
           {"en": "break the rules", "fa": "قوانین را شکستن"},
           {"en": "a coffee break", "fa": "استراحت قهوه"}],
    pats=[{"p": "break + object", "ex": "He broke his phone.",
           "fa": "گوشی‌اش را شکست."},
          {"p": "break down / break up / break into",
           "ex": "The car broke down on the motorway.",
           "fa": "ماشین در بزرگراه خراب شد."}],
    bad=[{"bad": "I broke my leg in the last year.",
          "good": "I broke my leg last year.",
          "why": "last year needs no in; in the last year means the past "
                 "twelve months and needs a perfect tense."}],
    use=[{"task": "Say what you do on a short break at work.",
          "frame": "On my break I usually …",
          "example": "On my break I usually walk around the block."}],
)

_add(
    "rain",
    infl=[{"f": "rains"}, {"f": "rained"}, {"f": "raining"}],
    fam=[{"w": "rainy", "pos": "adjective", "fa": "بارانی"},
         {"w": "rainbow", "pos": "noun", "fa": "رنگین‌کمان"}],
    colls=[{"en": "heavy rain", "fa": "باران شدید"},
           {"en": "light rain", "fa": "باران سبک"},
           {"en": "in the rain", "fa": "زیر باران"}],
    pats=[{"p": "it rains / it is raining",
           "ex": "It was raining when we left.", "fa": "وقتی راه افتادیم باران می‌آمد."},
          {"p": "rain + noun (rain water, rain cloud)",
           "ex": "The rain water filled the bucket.", "fa": "آب باران سطل را پر کرد."}],
    bad=[{"bad": "It rains heavily yesterday.",
          "good": "It rained heavily yesterday.",
          "why": "With a past time the verb is past: rained, not rains."}],
    bridge={"bad": "strong rain", "good": "heavy rain",
            "why": "Persian «باران شدید» maps strong onto rain, but English "
                   "weighs rain: it is heavy or light. Strong belongs to wind, "
                   "coffee and arguments."},
    use=[{"task": "Describe the weather on a day you remember.",
          "frame": "It was raining when …",
          "example": "It was raining when we arrived, so we waited inside."}],
    wild=["weather"],
)

# --------------------------------------------------------------------------
# Work and professional life, B2-C1: the words an adult learner needs in a
# meeting, a proposal or a performance review.
# --------------------------------------------------------------------------

_add(
    "deadline",
    fam=[{"w": "deadline", "pos": "noun", "fa": "مهلت نهایی"}],
    colls=[{"en": "meet a deadline", "fa": "به مهلت رسیدن",
            "ex": "We met the deadline by two days."},
           {"en": "miss a deadline", "fa": "از مهلت گذشتن"},
           {"en": "a tight deadline", "fa": "مهلت فشرده"}],
    pats=[{"p": "the deadline for + noun", "ex": "The deadline for applications is Friday.",
           "fa": "مهلت درخواست‌ها جمعه است."},
          {"p": "work to a deadline", "ex": "She works well to a deadline.",
           "fa": "با مهلت خوب کار می‌کند."}],
    bad=[{"bad": "I finished the report in the deadline.",
          "good": "I finished the report before the deadline.",
          "why": "A deadline is a point in time: you finish before it or by "
                 "it, never in it."}],
    use=[{"task": "Describe the next thing you have to finish and when.",
          "frame": "My deadline for … is …",
          "example": "My deadline for the budget draft is Wednesday afternoon."}],
    wild=["office"],
)

_add(
    "budget",
    fam=[{"w": "budgetary", "pos": "adjective", "fa": "بودجه‌ای"},
         {"w": "budgeting", "pos": "noun", "fa": "بودجه‌بندی"}],
    colls=[{"en": "on a budget", "fa": "با بودجهٔ محدود"},
           {"en": "a tight budget", "fa": "بودجهٔ فشرده"},
           {"en": "stay within budget", "fa": "در محدودهٔ بودجه ماندن"}],
    pats=[{"p": "budget for + noun", "ex": "We budgeted for two new laptops.",
           "fa": "برای دو لپ‌تاپ نو بودجه گذاشتیم."},
          {"p": "a budget of + amount", "ex": "The project has a budget of ten thousand euros.",
           "fa": "پروژه بودجه‌ای ده‌هزار یورویی دارد."}],
    bad=[{"bad": "We must stay in the budget.",
          "good": "We must stay within budget.",
          "why": "Budget in this pattern takes no article: on budget, over "
                 "budget, within budget."}],
    use=[{"task": "Plan a small purchase for your home with a limit.",
          "frame": "I have a budget of … for …",
          "example": "I have a budget of two hundred for a new desk."}],
)

_add(
    "delegate",
    fam=[{"w": "delegation", "pos": "noun", "fa": "واگذاری"}],
    colls=[{"en": "delegate a task to somebody", "fa": "کاری را به کسی واگذار کردن",
            "ex": "She delegated the report to a junior colleague."},
           {"en": "delegate responsibility", "fa": "مسئولیت واگذار کردن"}],
    pats=[{"p": "delegate + task + to + person",
           "ex": "He delegated the calls to his assistant.",
           "fa": "تماس‌ها را به دستیارش واگذار کرد."}],
    bad=[{"bad": "I delegated to him the task of calling clients.",
          "good": "I delegated the task of calling clients to him.",
          "why": "The thing comes after the verb and the person at the end "
                 "with to; putting the person first sounds like Persian word "
                 "order."}],
    use=[{"task": "Name one job you could hand to someone else this week.",
          "frame": "I could delegate … to …",
          "example": "I could delegate the scheduling to the new intern."}],
)

_add(
    "implement",
    fam=[{"w": "implementation", "pos": "noun", "fa": "اجرا"}],
    colls=[{"en": "implement a plan", "fa": "طرحی را اجرا کردن",
            "ex": "We implemented the plan in March."},
           {"en": "implement a policy", "fa": "سیاستی را اجرا کردن"},
           {"en": "fully implement", "fa": "به‌طور کامل اجرا کردن"}],
    pats=[{"p": "implement + plan / policy / change",
           "ex": "The team implemented the change quietly.",
           "fa": "تیم تغییر را بی‌سروصدا اجرا کرد."}],
    bad=[{"bad": "We implemented the new system from last month.",
          "good": "We implemented the new system last month.",
          "why": "A finished action with a past time takes no from; from "
                 "marks a starting point, not a when."}],
    use=[{"task": "Describe a change you would make where you work.",
          "frame": "I would implement … because …",
          "example": "I would implement a shorter Friday meeting because nobody reads the notes."}],
    wild=["office"],
)

_add(
    "compliance",
    fam=[{"w": "comply", "pos": "verb", "fa": "پیروی کردن"},
         {"w": "compliant", "pos": "adjective", "fa": "منطبق"}],
    colls=[{"en": "in compliance with something", "fa": "در انطباق با چیزی",
            "ex": "The building is in compliance with fire safety rules."},
           {"en": "compliance training", "fa": "آموزش انطباق"}],
    pats=[{"p": "comply with + rule", "ex": "All staff must comply with the policy.",
           "fa": "همهٔ کارکنان باید با سیاست پیروی کنند."}],
    bad=[{"bad": "We must comply to the new rules.",
          "good": "We must comply with the new rules.",
          "why": "Comply takes with; compliance likewise is in compliance "
                 "with a rule."}],
    use=[{"task": "Say which rule at work or school you always follow.",
          "frame": "We are required to comply with …",
          "example": "We are required to comply with the data protection policy."}],
)

_add(
    "turnover",
    fam=[{"w": "turnover", "pos": "noun", "fa": "گردش مالی"}],
    colls=[{"en": "annual turnover", "fa": "گردش مالی سالانه"},
           {"en": "high staff turnover", "fa": "ترک خدمت زیاد کارکنان",
            "ex": "High staff turnover usually means low pay."}],
    pats=[{"p": "a turnover of + amount", "ex": "The firm has a turnover of two million.",
           "fa": "شرکت گردش مالی دو میلیونی دارد."}],
    bad=[{"bad": "The company has a turnover of two millions.",
          "good": "The company has a turnover of two million.",
          "why": "Million, thousand and hundred stay singular after a number: "
                 "two million, not two millions."}],
    use=[{"task": "Explain why people leave jobs, in one sentence.",
          "frame": "High turnover is often caused by …",
          "example": "High turnover is often caused by long hours and no training."}],
)

_add(
    "benchmark",
    fam=[{"w": "benchmarking", "pos": "noun", "fa": "مقایسه با معیار"}],
    colls=[{"en": "set a benchmark", "fa": "معیاری تعیین کردن",
            "ex": "Their last release set a benchmark for the industry."},
           {"en": "against a benchmark", "fa": "در مقایسه با معیار"}],
    pats=[{"p": "benchmark against + noun", "ex": "We benchmark our prices against the market.",
           "fa": "قیمت‌هایمان را با بازار مقایسه می‌کنیم."}],
    bad=[{"bad": "We benchmark with our competitors.",
          "good": "We benchmark against our competitors.",
          "why": "Benchmark takes against: the comparison is a measurement "
                 "against a fixed line."}],
    use=[{"task": "Name one thing you measure to see if you are improving.",
          "frame": "I benchmark … against …",
          "example": "I benchmark my reading speed against last month's score."}],
)

_add(
    "forecast",
    fam=[{"w": "forecast", "pos": "noun", "fa": "پیش‌بینی"},
         {"w": "forecasting", "pos": "noun", "fa": "پیش‌بینی کردن"}],
    colls=[{"en": "a sales forecast", "fa": "پیش‌بینی فروش"},
           {"en": "the weather forecast", "fa": "پیش‌بینی هوا",
            "ex": "The forecast says rain by evening."}],
    pats=[{"p": "forecast + noun (growth, sales)",
           "ex": "Analysts forecast slower growth.", "fa": "تحلیل‌گران رشدی کندتر پیش‌بینی می‌کنند."},
          {"p": "forecast that + clause", "ex": "They forecast that prices will fall.",
           "fa": "پیش‌بینی می‌کنند قیمت‌ها پایین بیاید."}],
    bad=[{"bad": "The weather forecast says it will rains.",
          "good": "The weather forecast says it will rain.",
          "why": "After will the verb has no -s: will rain."}],
    use=[{"task": "Make a forecast about your week.",
          "frame": "I forecast that …",
          "example": "I forecast that Thursday will be the busiest day."}],
    wild=["weather"],
)

_add(
    "leverage",
    fam=[{"w": "leverage", "pos": "noun", "fa": "اهرم"}],
    colls=[{"en": "leverage your experience", "fa": "از تجربه‌ات بهره بردن",
            "ex": "She leveraged her experience into a better role."},
           {"en": "financial leverage", "fa": "اهرم مالی"}],
    pats=[{"p": "leverage + noun + to + verb",
           "ex": "We leveraged the data to win the account.",
           "fa": "از داده‌ها برای گرفتن حساب استفاده کردیم."}],
    bad=[{"bad": "We leveraged on our contacts.",
          "good": "We leveraged our contacts.",
          "why": "Leverage is a verb that takes a direct object here; on "
                 "belongs to rely on and depend on."}],
    use=[{"task": "Name a skill you want to turn into an advantage.",
          "frame": "I want to leverage my … to …",
          "example": "I want to leverage my Persian to work with Iranian clients."}],
)

_add(
    "stakeholder",
    fam=[{"w": "stake", "pos": "noun", "fa": "سهم / علاقه"}],
    colls=[{"en": "key stakeholders", "fa": "ذی‌نفعان اصلی"},
           {"en": "involve stakeholders", "fa": "ذی‌نفعان را دخیل کردن",
            "ex": "Involve the stakeholders before the design is fixed."}],
    pats=[{"p": "a stakeholder in + noun", "ex": "She is a stakeholder in the project.",
           "fa": "او در این پروژه ذی‌نفع است."}],
    bad=[{"bad": "The stakeholders of the project agreed.",
          "good": "The stakeholders in the project agreed.",
          "why": "A stakeholder is a person with a stake in something: in, "
                 "not of."}],
    use=[{"task": "Say who would care about a change you want to make.",
          "frame": "The main stakeholders in … are …",
          "example": "The main stakeholders in the new timetable are the parents and the teachers."}],
)

# --------------------------------------------------------------------------
# Persian Bridge: documented transfer traps. These are not "everything Persian
# speakers get wrong"; each one is a pattern that is reliably produced by
# translating a Persian sentence word for word, and each carries the natural
# English that replaces it.
# --------------------------------------------------------------------------

BRIDGE = [
    {"bad": "I did a mistake.", "good": "I made a mistake.",
     "why": "«اشتباه کردم» uses the verb for doing, but English mistakes are "
            "made. The same verb pair covers a decision, a plan, a promise "
            "and an effort."},
    {"bad": "We discussed about the plan.", "good": "We discussed the plan.",
     "why": "Discuss takes its object directly; about belongs to talk about "
            "and argue about. This is the most common -about of all."},
    {"bad": "She is married with a doctor.", "good": "She is married to a doctor.",
     "why": "«ازدواج کرد با» translates with, but English marries to a person. "
            "Married with children is a different, correct phrase."},
    {"bad": "It depends of the weather.", "good": "It depends on the weather.",
     "why": "Depend, rely and concentrate all take on; of belongs to consist of "
            "and be afraid of."},
    {"bad": "I arrived to the airport.", "good": "I arrived at the airport.",
     "why": "Arrive at a place, arrive in a city or country - never to, which "
            "belongs to go to and get to."},
    {"bad": "He explained me the problem.", "good": "He explained the problem to me.",
     "why": "Explain, describe and suggest do not take a person as their first "
            "object; the person comes after to."},
    {"bad": "Can you suggest me a book?", "good": "Can you suggest a book to me?",
     "why": "Suggest takes the thing, then to the person. Recommend works the "
            "same way."},
    {"bad": "I am interested about history.", "good": "I am interested in history.",
     "why": "Interested in, good at, afraid of, proud of: the adjective chooses "
            "the preposition, and Persian «علاقه‌مند به» does not decide it."},
    {"bad": "I prefer tea than coffee.", "good": "I prefer tea to coffee.",
     "why": "Prefer A to B. Than appears only with the comparative: I like tea "
            "more than coffee."},
    {"bad": "I have a rest every afternoon.", "good": "I take a break every afternoon.",
     "why": "«استراحت کردن» is take a break or have a rest, but have a rest is "
            "British and rarer; take a break is the natural phrase in most "
            "contexts."},
    {"bad": "The food was very delicious.", "good": "The food was delicious.",
     "why": "Delicious is already absolute, like perfect and freezing: it does "
            "not take very. Absolutely delicious is the emphatic form."},
    {"bad": "I learned it by heart.", "good": "I memorized it.",
     "why": "Learn by heart exists but is dated in most varieties; memorize or "
            "learn off by heart are clearer. Keeping the phrase is not wrong, "
            "it just dates the sentence."},
    {"bad": "He said me the truth.", "good": "He told me the truth.",
     "why": "Tell takes the person; say takes the words. Say me is never "
            "English, whatever the Persian sentence looks like."},
    {"bad": "She informed me about the delay.", "good": "She informed me of the delay.",
     "why": "Inform takes of, or a that-clause. About belongs to tell and "
            "warn."},
    {"bad": "I am agree with you.", "good": "I agree with you.",
     "why": "Agree is a verb, not an adjective: no am. «موافقم» looks like a "
            "state, but English says I agree."},
    {"bad": "I have 25 years old.", "good": "I am 25 years old.",
     "why": "Age is be, not have: Persian «۲۵ سال دارم» uses having, English "
            "uses being."},
    {"bad": "We went to home.", "good": "We went home.",
     "why": "Home takes no to after a verb of movement: go home, come home, "
            "get home."},
    {"bad": "I am living here since 2019.", "good": "I have lived here since 2019.",
     "why": "Since with a point in the past needs the present perfect; the "
            "continuous sounds like a temporary stay."},
    {"bad": "I will call you when I will arrive.", "good": "I will call you when I arrive.",
     "why": "After when, if, before and after, the future is the present "
            "tense: when I arrive."},
    {"bad": "Everybody are ready.", "good": "Everybody is ready.",
     "why": "Everybody, everyone and each take a singular verb in English, "
            "even though they mean a group."},
]

# --------------------------------------------------------------------------
# Word in the wild: a natural text, one question, one answer. Every word the
# passage is filed under has to appear in it - the builder checks that, so a
# passage cannot drift away from the word it is meant to show.
# --------------------------------------------------------------------------

WILD = [
    {"id": "meeting", "kind": "Workplace dialogue",
     "title": {"en": "Presenting an idea", "fa": "ارائهٔ یک ایده"},
     "text": "Sara presented her ideas confidently during the meeting. She felt "
             "confident about the numbers, and the team trusted her because she "
             "was honest about what she did not know.",
     "words": ["confident", "honest"],
     "question": "What does 'confidently' tell us about Sara?",
     "options": ["She spoke in a self-assured way.", "She spoke very quickly.",
                 "She spoke in a quiet voice."],
     "answer": 0,
     "why": "Confidently describes how sure she sounded, not how fast or how "
            "loudly she spoke."},
    {"id": "hotel", "kind": "Reception dialogue",
     "title": {"en": "Checking in", "fa": "ورود به هتل"},
     "text": "Guest: I made a reservation for two nights under the name Ahmadi. "
             "Receptionist: I can see it here. Guest: I'm afraid I have to "
             "complain about the room - the window does not close.",
     "words": ["reservation", "complain"],
     "question": "What does the guest do after checking the reservation?",
     "options": ["Cancel a reservation.", "Make a complaint about the room.",
                 "Ask for a bigger budget."],
     "answer": 1,
     "why": "To complain about something is to make a complaint; the guest "
            "reports the window, not a bill."},
    {"id": "weather", "kind": "News bulletin",
     "title": {"en": "The forecast", "fa": "پیش‌بینی هوا"},
     "text": "The forecast promises heavy rain across the north by evening, "
             "with strong wind on the coast. Drivers are asked to leave more "
             "time for their journey.",
     "words": ["rain", "forecast"],
     "question": "What kind of rain does the forecast describe?",
     "options": ["Light rain.", "Heavy rain.", "No rain at all."],
     "answer": 1,
     "why": "English weighs rain: heavy or light. The passage says heavy, and "
            "strong belongs to the wind in the next clause."},
    {"id": "office", "kind": "Workplace email",
     "title": {"en": "A short project update", "fa": "گزارش کوتاه پروژه"},
     "text": "Hi all, a quick update before the deadline. We implemented the "
             "new booking form on Monday and the first numbers look good. "
             "Please keep the budget in mind if you order anything else this "
             "week. Thanks, Reza",
     "words": ["deadline", "implement", "budget"],
     "question": "What happened on Monday?",
     "options": ["The budget was cut.", "The new booking form was put into use.",
                 "The deadline moved."],
     "answer": 1,
     "why": "To implement something is to put it into use; the form was not "
            "planned again, it went live."},
]

# --------------------------------------------------------------------------
# Goal collections. They are views over the domains that already exist, not a
# second vocabulary list: the same word can sit in Everyday and in Business.
# --------------------------------------------------------------------------

COLLECTIONS = [
    {"id": "everyday", "en": "Everyday English", "fa": "انگلیسی روزمره",
     "blurb": {"en": "The words of a normal day: home, food, people, places.",
               "fa": "واژه‌های یک روز معمولی: خانه، غذا، آدم‌ها، جاها."},
     "domains": ["basic_words", "daily_routine_words", "food", "house",
                 "family", "emotions", "places", "shopping_clothes"]},
    {"id": "travel", "en": "Travel & hotels", "fa": "سفر و هتل",
     "blurb": {"en": "Airports, rooms, restaurants and asking for help.",
               "fa": "فرودگاه، اتاق، رستوران و کمک خواستن."},
     "domains": ["travel", "hotel_stay", "airport_flight", "restaurant_dining",
                 "directions_words", "emergency_safety"]},
    {"id": "business", "en": "Business & workplace", "fa": "کسب‌وکار و محیط کار",
     "blurb": {"en": "Meetings, money, targets and the language of a team.",
               "fa": "جلسه، پول، هدف و زبان کار تیمی."},
     "domains": ["business_vocab", "workplace", "workplace_c1", "finance_b2",
                 "work_business", "bank_money"]},
    {"id": "academic", "en": "Academic English", "fa": "انگلیسی آکادمیک",
     "blurb": {"en": "The words that make writing and research sound precise.",
               "fa": "واژه‌هایی که نوشتار و پژوهش را دقیق می‌کنند."},
     "domains": ["academic_wordlist", "academic_vocab", "formal_register",
                 "evaluation_language", "science_tech_c1", "education_b1"]},
    {"id": "exams", "en": "IELTS & TOEFL", "fa": "آیلتس و تافل",
     "blurb": {"en": "Evaluation, argument and the register an exam expects.",
               "fa": "ارزیابی، استدلال و لحنی که آزمون انتظار دارد."},
     "domains": ["academic_wordlist", "evaluation_language", "formal_advanced",
                 "nuance_synonyms", "media_news", "environment_b2"]},
    {"id": "tech", "en": "Technology & media", "fa": "فناوری و رسانه",
     "blurb": {"en": "Phones, apps, headlines and the words around them.",
               "fa": "گوشی، برنامه، تیتر خبر و واژه‌های پیرامونشان."},
     "domains": ["technology", "digital_life", "media_news", "science_tech_c1"]},
]
