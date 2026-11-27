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
    {"id": "everyday-life", "en": "Everyday Life", "fa": "زندگی روزمره",
     "blurb": {"en": "The words of an ordinary day: home, people, places, time, "
                     "numbers and the small verbs that hold a sentence together.",
               "fa": "واژه‌های یک روز معمولی: خانه، آدم‌ها، جاها، زمان، عدد و "
                     "فعل‌های کوچکی که جمله را سر پا نگه می‌دارند."},
     "domains": ["basic_words", "daily_routine_words", "house", "household_actions",
                 "family", "places", "city", "time_words", "numbers", "colors",
                 "adjectives", "verbs", "quantities", "communication",
                 "directions_words"]},
    {"id": "travel-adventure", "en": "Travel & Adventure", "fa": "سفر و ماجراجویی",
     "blurb": {"en": "Airports, rooms, roads and the weather that changes the plan.",
               "fa": "فرودگاه، اتاق، جاده و هوایی که برنامه را عوض می‌کند."},
     "domains": ["travel", "airport_flight", "hotel_stay", "transport",
                 "emergency_safety", "weather_seasons", "directions_words"]},
    {"id": "health-lifestyle", "en": "Health & Lifestyle", "fa": "سلامت و سبک زندگی",
     "blurb": {"en": "The body, the doctor, sleep, sport, feelings and the "
                     "relationships that keep a person well.",
               "fa": "بدن، دکتر، خواب، ورزش، احساس‌ها و رابطه‌هایی که آدم را "
                     "سالم نگه می‌دارند."},
     "domains": ["health_visits", "body_health", "sleep_wellbeing", "body",
                 "sports", "emotions", "psychology_feelings", "relationships",
                 "environment_b2", "nature", "animals"]},
    {"id": "beauty-personal-care", "en": "Beauty & Personal Care",
     "fa": "زیبایی و مراقبت شخصی",
     "blurb": {"en": "Clothes, sizes, the shop and the language of how "
                     "something looks and fits.",
               "fa": "لباس، سایز، مغازه و زبانِ این‌که چیزی چه‌طور دیده می‌شود "
                     "و چه‌طور می‌نشیند."},
     "domains": ["clothing", "shopping_clothes", "body", "art_design"]},
    {"id": "food-hospitality", "en": "Food & Hospitality", "fa": "غذا و مهمان‌نوازی",
     "blurb": {"en": "Shopping for food, cooking it, ordering it and staying "
                     "somewhere it is served.",
               "fa": "خرید غذا، پختنش، سفارش دادنش و اقامت جایی که سرو می‌شود."},
     "domains": ["food", "fruits", "vegetables", "cooking_basics",
                 "restaurant_dining", "quantities", "hotel_stay"]},
    {"id": "technology-innovation", "en": "Technology & Innovation",
     "fa": "فناوری و نوآوری",
     "blurb": {"en": "Phones, apps, online life and the words of the things "
                     "that keep getting faster.",
               "fa": "گوشی، برنامه، زندگی آنلاین و واژه‌های چیزهایی که مدام "
                     "تندتر می‌شوند."},
     "domains": ["technology", "digital_life", "science_tech_c1", "art_design"]},
    {"id": "professional-english", "en": "Professional English",
     "fa": "انگلیسی حرفه‌ای",
     "blurb": {"en": "Meetings, money, contracts and the language of a working "
                     "day, from the office to the bank.",
               "fa": "جلسه، پول، قرارداد و زبان یک روز کاری، از دفتر تا بانک."},
     "domains": ["work_business", "workplace", "workplace_c1", "business_vocab",
                 "finance_b2", "bank_money", "law_rights", "jobs",
                 "collocations_b2"]},
    {"id": "education-academic", "en": "Education & Academic Life",
     "fa": "آموزش و زندگی آکادمیک",
     "blurb": {"en": "School, university, essays and the register an assignment "
                     "expects.",
               "fa": "مدرسه، دانشگاه، مقاله و لحنی که یک تکلیف انتظار دارد."},
     "domains": ["school", "education_b1", "academic_wordlist", "academic_vocab",
                 "formal_register", "evaluation_language", "formal_advanced"]},
    {"id": "entertainment-culture", "en": "Entertainment & Culture",
     "fa": "سرگرمی و فرهنگ",
     "blurb": {"en": "Music, the news, the way people describe each other, and "
                     "the idioms that make a sentence sound lived-in.",
               "fa": "موسیقی، خبر، این‌که آدم‌ها همدیگر را چه‌طور توصیف می‌کنند "
                     "و اصطلاح‌هایی که جمله را طبیعی می‌کنند."},
     "domains": ["music", "media_news", "idioms_b2", "idioms_c2",
                 "idiomatic_collocations_c2", "nuance_synonyms",
                 "advanced_adjectives", "describing_people", "phrasal_verbs"]},
    {"id": "shopping-consumer", "en": "Shopping & Consumer Life",
     "fa": "خرید و زندگی مصرفی",
     "blurb": {"en": "Buying, returning, paying, and dealing with the offices "
                     "and services around a purchase.",
               "fa": "خریدن، پس دادن، پرداختن و سر و کله زدن با اداره‌ها و "
                     "خدماتِ یک خرید."},
     "domains": ["shopping_clothes", "clothing", "bank_money", "public_services",
                 "tools_diy", "jobs", "food", "transport"]},
]

# ==========================================================================
# DOMAIN DIALOGUES
# One conversation per vocabulary domain, written for that domain: its words,
# its situation, its communicative purpose. The builder derives each
# dialogue's target vocabulary by finding the domain's own words in the lines,
# so a dialogue cannot claim to teach words it never uses, and a domain word
# list cannot drift away from the conversation that is meant to teach it.
#
# Shape: (scenario_en, scenario_fa, [roles], [(speaker, line), ...])
# ==========================================================================

DIALOGUES = {}


def _dlg(domain, scenario_en, scenario_fa, roles, lines, note=""):
    DIALOGUES[domain] = {
        "scenario": (scenario_en, scenario_fa),
        "roles": list(roles),
        "lines": [tuple(line) for line in lines],
        "note": note,
    }


_dlg(
    "travel", "A connection that did not wait", "اتصالی که نماند",
    ["Passenger", "Desk agent"], [
        ("Passenger", "I missed my connecting flight because the first one was late. "
                      "My luggage is still tagged to Shiraz."),
        ("Desk agent", "I can see the delay on your ticket. There is another departure "
                       "at six; I can move your reservation to it at no charge."),
        ("Passenger", "That saves the trip. Do I need a new boarding pass?"),
        ("Desk agent", "You do, and it will print at the gate. Your suitcase stays "
                       "checked through, so you only carry the carry-on."),
        ("Passenger", "Is there time for sightseeing near the terminal?"),
        ("Desk agent", "Two hours is enough for the old quarter, but keep your passport "
                       "with you and be back before boarding."),
    ],
    "The scenario is a missed connection: the vocabulary is travel, flight and "
    "reservation, not office English.",
)

_dlg(
    "airport_flight", "The bag that went to the wrong city", "چمدانی که به شهر اشتباه رفت",
    ["Traveller", "Baggage service"], [
        ("Traveller", "My checked baggage did not arrive. I waited at baggage claim "
                      "until the belt stopped."),
        ("Baggage service", "What was your connecting flight, and was the layover short?"),
        ("Traveller", "Fifty minutes. The gate was at the far end of the terminal."),
        ("Baggage service", "That is usually enough. I can see the suitcase was sent to "
                            "the wrong city - it arrives on the nine o'clock flight."),
        ("Traveller", "Can it be delivered to my hotel, or must I come back for it?"),
        ("Baggage service", "We deliver it tonight. Keep this reference, and put the "
                            "essentials in your carry-on baggage next time."),
    ],
)

_dlg(
    "hotel_stay", "The room above the kitchen", "اتاق بالای آشپزخانه",
    ["Guest", "Receptionist"], [
        ("Guest", "I booked a double room for three nights, but the noise from the "
                  "kitchen keeps waking me up."),
        ("Receptionist", "I am sorry about that. The air conditioning unit is above "
                         "that room and it runs all night."),
        ("Guest", "Could I move to a quieter room? I do not mind the stairs."),
        ("Receptionist", "There is a twin room on the top floor, with a pillow and a "
                         "spare blanket already there. Breakfast is included."),
        ("Guest", "That works. What time is check-out on Sunday?"),
        ("Receptionist", "Eleven, but you can leave your luggage at reception after that."),
    ],
)

_dlg(
    "transport", "The bus that does not take the bridge", "اتوبوسی که از پل نمی‌گذرد",
    ["Visitor", "Local"], [
        ("Visitor", "Does this bus go to the harbour, or do I need the metro?"),
        ("Local", "It goes there, but not today - the bridge is closed for repairs."),
        ("Visitor", "So what is the quickest way? I have a ferry at four."),
        ("Local", "Take the tram to the last stop, then a taxi for the final kilometre. "
                  "A bicycle would be faster than the bus right now."),
        ("Visitor", "And the ticket - do I pay on the tram?"),
        ("Local", "There is a machine at the stop. Keep the ticket; inspectors check."),
    ],
)

_dlg(
    "emergency_safety", "Smoke in the stairwell", "دود در راه‌پله",
    ["Resident", "Fire officer"], [
        ("Resident", "The smoke alarm went off and there is smoke in the stairwell. "
                     "Should we evacuate?"),
        ("Fire officer", "Leave by the emergency exit on the left, not the lift. Is "
                         "anyone injured or unable to walk?"),
        ("Resident", "My neighbour has a burn on her hand from the kitchen; she needs "
                     "first aid."),
        ("Fire officer", "The ambulance is outside. Take the bandage from the kit by "
                         "the door and keep her warm."),
        ("Resident", "The fire extinguisher cabinet is locked."),
        ("Fire officer", "I have the key. Stay outside and do not go back in for anything."),
    ],
)

_dlg(
    "weather_seasons", "The forecast changes the walk", "پیش‌بینی هوا برنامهٔ پیاده‌روی را عوض می‌کند",
    ["Guide", "Walker"], [
        ("Walker", "Is the ridge walk still on? The forecast mentioned a storm."),
        ("Guide", "It did, and there is fog on the summit already. We move the walk to "
                  "the valley, where it is mild and dry."),
        ("Walker", "Will it rain? I only brought a light jacket."),
        ("Guide", "Drizzle until noon, then sunny. The wind is the real problem today, "
                  "not the temperature."),
        ("Walker", "And tomorrow? I would rather see the autumn colours in clear weather."),
        ("Guide", "Tomorrow is cold but clear - good light, no humidity, and no thunder."),
    ],
)

_dlg(
    "directions_words", "Finding the entrance on the wrong side", "پیدا کردن ورودی از سمت اشتباه",
    ["Shopper", "Security guard"], [
        ("Shopper", "I am looking for the main entrance, but every door on this side is "
                    "locked."),
        ("Security guard", "You are on the back of the building. Go straight to the "
                           "corner, turn left at the roundabout, and the entrance is "
                           "opposite the signpost."),
        ("Shopper", "Is it far? I am parked behind the bank."),
        ("Security guard", "Two minutes. The lift inside is next to the stairs; the "
                           "office is on the third floor."),
        ("Shopper", "And the exit for the car park?"),
        ("Security guard", "Same door, then across the road - the one beside the kiosk."),
    ],
)

_dlg(
    "sports", "Joining a class that is already full", "ثبت‌نام در کلاسی که پر شده",
    ["Member", "Coach"], [
        ("Member", "I want to join the evening swimming class, but the app says it is "
                   "full."),
        ("Coach", "It is, for now. Most people come for the gym and leave the pool at "
                  "seven, so there is space then."),
        ("Member", "I also do running twice a week. Would cycling help my knees?"),
        ("Coach", "It would - low impact, and you can keep the running for the weekend. "
                  "Do you play any ball sport?"),
        ("Member", "Table tennis, badly. Is there a group here?"),
        ("Coach", "Thursday nights. Bring your own bat; we have the table and the balls."),
    ],
)

_dlg(
    "cooking_basics", "The sauce that caught on the pan", "سسی که ته قابلمه گرفت",
    ["Cook", "Friend"], [
        ("Friend", "That smells good. What is in the sauce?"),
        ("Cook", "Tomato, garlic and a little honey - I tasted it twice before it was "
                 "sweet enough."),
        ("Friend", "Did you roast the garlic first? It gets sweeter in the oven."),
        ("Cook", "I fried it, and the pan was too hot, so it caught. I had to start "
                 "again and stir the whole time."),
        ("Friend", "Use a heavier pot next time and keep the heat low. Is the fish ready?"),
        ("Cook", "Two more minutes. Could you slice the lemon and put it on the plate?"),
    ],
)

_dlg(
    "restaurant_dining", "A table, an allergy and a bill", "میز، حساسیت و صورتحساب",
    ["Guest", "Waiter"], [
        ("Guest", "We booked a table for two at eight. Could we sit away from the door?"),
        ("Waiter", "Of course. Before you order - is there an allergy in the party?"),
        ("Guest", "Yes, nuts. What would you recommend from the main course?"),
        ("Waiter", "The grilled fish is mild and has no nuts. The starter of the day is "
                   "spicy, so I would avoid it."),
        ("Guest", "We will take the fish and a still water. Can we split the bill?"),
        ("Waiter", "Yes, two receipts. The tip is not included, so it is up to you."),
    ],
)

_dlg(
    "basic_words", "The first week somewhere new", "هفتهٔ اول در جای تازه",
    ["Newcomer", "Colleague"], [
        ("Newcomer", "Sorry - where is the kitchen, and when does everyone have lunch?"),
        ("Colleague", "There, behind the stairs. We eat at one, because the afternoon "
                      "meeting starts at two."),
        ("Newcomer", "Who do I ask about a key, and why is this door always locked?"),
        ("Colleague", "Ask Sam; she has a key for everyone. It is locked because the "
                      "printer is inside."),
        ("Newcomer", "Thanks. Something else - how do I get to the station from here?"),
        ("Colleague", "You go left at the corner, and if you see the park you have gone "
                      "too far."),
    ],
)

_dlg(
    "daily_routine_words", "Two mornings that do not match", "دو صبحی که به هم نمی‌خورند",
    ["Roya", "Ben"], [
        ("Roya", "I wake up at six and get up straight away, so I can have breakfast "
                 "before the traffic."),
        ("Ben", "I set an alarm for seven and still do not get up. I skip breakfast and "
                "take a shower instead."),
        ("Roya", "Who makes breakfast in your house?"),
        ("Ben", "Nobody. I buy something on the way. In the evening I cook, and my "
                "brother does the dishes."),
        ("Roya", "Do you go to bed early?"),
        ("Ben", "Never. I read a book until midnight, so I am tired all week."),
    ],
)

_dlg(
    "house", "A flat with one problem after another", "آپارتمانی با یک مشکل پس از دیگری",
    ["Tenant", "Landlord"], [
        ("Tenant", "The window in the bedroom does not close, and the radiator under it "
                   "stays cold."),
        ("Landlord", "The window needs a new handle. I will bring one and check the "
                     "balcony door too."),
        ("Tenant", "Also, the lamp in the living room flickers, and the wardrobe door "
                   "came off its rail."),
        ("Landlord", "Send me a photo of the wardrobe. Is the fridge working, at least?"),
        ("Tenant", "The fridge is fine. The shower is not - the water stays cold for a "
                   "long time."),
        ("Landlord", "Then it is the boiler. I will book someone for Thursday; keep the "
                     "key with you."),
    ],
)

_dlg(
    "household_actions", "Cleaning before the guests arrive", "تمیزکاری پیش از رسیدن مهمان‌ها",
    ["Sara", "Ali"], [
        ("Sara", "You tidy up the living room and I will mop the floor, but please do "
                 "not forget to dust the shelf."),
        ("Ali", "I already loaded the dishwasher, but there is a spill under the sink "
                "that needs a cloth."),
        ("Sara", "Use the one in the drawer. After that, fold the laundry and put it in "
                 "the wardrobe."),
        ("Ali", "Should I preheat the oven now, or wait until they arrive?"),
        ("Sara", "Now. The chicken takes an hour, and I still have to chop the vegetables."),
        ("Ali", "Fine. I will take out the trash before they ring the bell."),
    ],
)

_dlg(
    "family", "Introducing everybody at a wedding", "معرفی همه در یک عروسی",
    ["Neda", "Hassan"], [
        ("Neda", "That is my mother next to the door, and my father is the one with the "
                 "camera."),
        ("Hassan", "And the little boy who keeps running between the tables?"),
        ("Neda", "My nephew. His sister, my niece, is the one in blue - she is a twin, "
                 "actually."),
        ("Hassan", "So your brother is the tall man talking to my wife?"),
        ("Neda", "Yes, and the woman beside him is my sister-in-law. My grandmother is "
                 "the one everyone is queuing to greet."),
        ("Hassan", "Your family is much bigger than mine. I have one cousin and no "
                   "siblings at all."),
    ],
)

_dlg(
    "places", "Where to find everything in a new town", "چیزها را در شهر تازه کجا پیدا کنیم",
    ["Mina", "Reza"], [
        ("Mina", "Is there a pharmacy near the market? My son has a fever."),
        ("Reza", "There is one on the corner, next to the bakery. The supermarket is "
                 "opposite the bank."),
        ("Mina", "And a park? He needs some air."),
        ("Reza", "The garden behind the mosque is quieter, and there is a cafe by the "
                 "gate."),
        ("Mina", "What about a hospital, just in case?"),
        ("Reza", "The hospital is on the main street, past the post office - ten minutes "
                 "by taxi from the village road."),
    ],
)

_dlg(
    "city", "The library card and the bus stop", "کارت کتابخانه و ایستگاه اتوبوس",
    ["Visitor", "Librarian"], [
        ("Visitor", "I want a library card. Which documents do I need?"),
        ("Librarian", "A ticket with your address - a utility bill is enough - and your "
                      "passport."),
        ("Visitor", "Is the museum on this street free on Fridays?"),
        ("Librarian", "It is, and the square in front of it has a market at the weekend. "
                      "The bus stop is by the traffic light."),
        ("Visitor", "How do I cross? There is no crosswalk near the corner."),
        ("Librarian", "Use the pedestrian bridge past the post office; the sidewalk on "
                      "this side is closed for works."),
    ],
)

_dlg(
    "time_words", "A deadline, a weekend and a late train", "مهلت، آخر هفته و قطار دیرکرده",
    ["Client", "Freelancer"], [
        ("Client", "The deadline is Friday at noon. Is that still possible?"),
        ("Freelancer", "Friday is tight, but I can send the draft tomorrow afternoon and "
                       "the final version a day later."),
        ("Client", "Tomorrow is a holiday. What about the weekend?"),
        ("Freelancer", "I work Saturday morning, so the weekend is not lost. The last "
                       "hour is always the quiet one."),
        ("Client", "Good. How many weeks until the second phase starts?"),
        ("Freelancer", "Two weeks from now, in the new month - I will send the calendar."),
    ],
)

_dlg(
    "adjectives", "Choosing between two flats", "انتخاب بین دو آپارتمان",
    ["Leila", "Agent"], [
        ("Leila", "The first flat is cheaper, but the rooms are small and the street is "
                  "loud."),
        ("Agent", "The second is more expensive, yet it is quiet, clean and close to the "
                  "park."),
        ("Leila", "Is the kitchen modern? I cook a lot, so a good stove is important."),
        ("Agent", "It is new. The bathroom is old, but the water is hot and the heating "
                  "is strong."),
        ("Leila", "And the balcony - big or small?"),
        ("Agent", "Small but sunny. For a young couple it is the easier flat to love."),
    ],
)

_dlg(
    "verbs", "A week of small decisions", "یک هفته پر از تصمیم‌های کوچک",
    ["Omid", "Sahar"], [
        ("Omid", "I want to learn to cook, but I never find the time."),
        ("Sahar", "Start with one dish. Buy the ingredients, read the recipe twice, and "
                  "give yourself an hour."),
        ("Omid", "And if it goes wrong? I hate wasting food."),
        ("Sahar", "Then write down what you did, and change one thing next time. Do you "
                  "remember the soup you made?"),
        ("Omid", "I try to forget it. My brother still talks about it."),
        ("Sahar", "Ask him to help. Two people in a kitchen finish twice as fast."),
    ],
)

_dlg(
    "numbers", "Splitting a bill three ways", "تقسیم صورتحساب بین سه نفر",
    ["Cashier", "Customer"], [
        ("Customer", "What is the total? We are three people and I want to split it."),
        ("Cashier", "One hundred and twenty thousand. That is forty each, exactly."),
        ("Customer", "I only have a fifty. Can you give me ten back?"),
        ("Cashier", "Of course. Two of you pay by card and the third in cash, if that is "
                    "easier."),
        ("Customer", "It is. And the first item on the receipt - was that the soup?"),
        ("Cashier", "It was the second. The first was the salad, at half the price."),
    ],
)

_dlg(
    "colors", "Painting a room in daylight", "رنگ کردن اتاق در نور روز",
    ["Painter", "Client"], [
        ("Client", "I want the living room light gray, not white - white looks cold here."),
        ("Painter", "Then we keep the ceiling white and the wall light gray. Do you want "
                    "the door dark blue or the same gray?"),
        ("Client", "Dark blue would be too much with the brown sofa."),
        ("Painter", "Agreed. A beige curtain and a green plant will warm it up without "
                    "another colour on the wall."),
        ("Client", "What about the small room? It is always dark."),
        ("Painter", "Then cream, or a pale yellow - both hold the light better than gray."),
    ],
)

_dlg(
    "quantities", "Enough for eight people", "به‌اندازهٔ هشت نفر",
    ["Host", "Helper"], [
        ("Host", "We are eight for dinner. Is one chicken enough?"),
        ("Helper", "Barely. I would cook two, and a dozen eggs for the salad."),
        ("Host", "How much rice? I never judge it right."),
        ("Helper", "A handful per person, so roughly two cups. Add a few extra for the "
                   "children."),
        ("Host", "And the cake? The recipe says a spoonful of cinnamon."),
        ("Helper", "A spoonful is plenty. Double the recipe if you want leftovers for "
                   "tomorrow."),
    ],
)

_dlg(
    "communication", "A call that keeps dropping", "تماسی که مدام قطع می‌شود",
    ["Nima", "Support"], [
        ("Nima", "My calls keep dropping. The signal shows two bars and then the line "
                 "goes dead."),
        ("Support", "Is it everywhere, or only at home? Check whether the network is "
                    "weak indoors."),
        ("Nima", "At home, mostly. I also get no notification when a message arrives."),
        ("Support", "Open the settings and look at the account - the notification sound "
                    "may be off, and voicemail is full."),
        ("Nima", "If I send you an attachment, can you check the line from your side?"),
        ("Support", "Send a screenshot to this inbox and I will call you back on a "
                    "different number."),
    ],
)

_dlg(
    "emotions", "The week nobody enjoyed", "هفته‌ای که هیچ‌کس از آن لذت نبرد",
    ["Marta", "Kian"], [
        ("Marta", "You look tired and a little sad. Is everything all right?"),
        ("Kian", "I am exhausted, and honestly a bit disappointed. The project was "
                 "cancelled on Friday."),
        ("Marta", "That is frustrating. Were you angry with the decision?"),
        ("Kian", "Not angry - more confused. I felt proud of the work, and then it was "
                 "gone."),
        ("Marta", "It is normal to feel hopeless for a day. Are you nervous about the "
                  "next one?"),
        ("Kian", "A little. But I am grateful the team said so early."),
    ],
)

_dlg(
    "body", "Where it hurts", "کجا درد می‌کند",
    ["Patient", "Nurse"], [
        ("Nurse", "Where does it hurt - the chest, the back, or the shoulder?"),
        ("Patient", "My back, low down, and sometimes my left leg."),
        ("Nurse", "Does the pain reach the knee or the ankle?"),
        ("Patient", "To the knee. And my neck is stiff when I turn my head."),
        ("Nurse", "Any numbness in the fingers or the toes?"),
        ("Patient", "No, but my right shoulder aches when I lift my arm above my head."),
    ],
)

_dlg(
    "body_health", "A cold that will not go", "سرماخوردگی‌ای که خوب نمی‌شود",
    ["Patient", "Pharmacist"], [
        ("Patient", "I have had a cough and a fever for five days, and the medicine I "
                    "bought is finished."),
        ("Pharmacist", "Do you have a headache or a stomach ache as well?"),
        ("Patient", "A headache in the evening. No stomach ache."),
        ("Pharmacist", "This looks like flu, not a simple cold. Take the syrup at night "
                       "and rest; if the fever stays, see a doctor."),
        ("Patient", "Do I need a prescription for the pills?"),
        ("Pharmacist", "Not for these, but the pharmacy cannot sell the stronger ones "
                       "without one."),
    ],
)

_dlg(
    "health_visits", "A check-up that finds something", "معایناتی که چیزی پیدا می‌کند",
    ["Patient", "Doctor"], [
        ("Doctor", "Your blood pressure is high again. Any headache, or swelling in the "
                   "ankles?"),
        ("Patient", "Some swelling, and I tire quickly. The prescription ran out last "
                    "week."),
        ("Doctor", "I will refill it at a lower dose and book a check-up in a month. Is "
                   "the pharmacy still the one on the corner?"),
        ("Patient", "Yes. Is this chronic, or will it get better?"),
        ("Doctor", "It is manageable, not curable - and the side effect you mentioned "
                   "should fade with the lower dose."),
        ("Patient", "Should I take the medicine with food?"),
        ("Doctor", "With breakfast, and keep the insurance card with the referral."),
    ],
)

_dlg(
    "sleep_wellbeing", "Three nights of bad sleep", "سه شب بی‌خوابی",
    ["Client", "Coach"], [
        ("Client", "I have insomnia again. I go to bed late, wake up at three and cannot "
                   "get back to sleep."),
        ("Coach", "What is the last thing you do before bedtime - screen time, or work?"),
        ("Client", "Email, usually. I am exhausted by Friday and I nap at my desk."),
        ("Coach", "Set an alarm for the same wake up time, and give yourself an hour to "
                  "unwind with no screen."),
        ("Client", "Will exercise help? I have no energy for the gym."),
        ("Coach", "A short walk is enough. Sleep, food and hydration do more for a mood "
                  "than one hard workout."),
    ],
)

_dlg(
    "psychology_feelings", "The colleague who went quiet", "همکاری که ساکت شد",
    ["Manager", "Colleague"], [
        ("Manager", "You seem withdrawn this week. Are you overwhelmed by the new "
                    "deadline?"),
        ("Colleague", "A bit anxious, and reluctant to say so. I am self-conscious about "
                      "asking for help twice."),
        ("Manager", "That is understandable. What would make the week feel manageable?"),
        ("Colleague", "Fewer meetings, and someone to share the reporting. My motivation "
                      "is fine; the volume is not."),
        ("Manager", "I can move two meetings. How is your mood outside work?"),
        ("Colleague", "Better. I have empathy for the team, but I need to protect my own "
                      "focus too."),
    ],
)

_dlg(
    "clothing", "Dressing for a cold wedding", "لباس پوشیدن برای عروسی در سرما",
    ["Sara", "Dressmaker"], [
        ("Sara", "I need something for a winter wedding. The dress I have is too light "
                 "for the season."),
        ("Dressmaker", "A coat over it, or a heavier dress with long sleeves. Do you "
                       "prefer a skirt or trousers?"),
        ("Sara", "Trousers, and comfortable shoes - the ceremony is outdoors."),
        ("Dressmaker", "Then boots, a scarf and gloves, and no sandals whatever the "
                       "forecast says."),
        ("Sara", "The jacket I own has a broken zipper and a missing button."),
        ("Dressmaker", "Bring it in; I can replace both before Thursday. Wear the belt "
                       "you like and we will match the colour."),
    ],
)

_dlg(
    "shopping_clothes", "The jacket that is the wrong size", "ژاکتی با سایز اشتباه",
    ["Customer", "Shop assistant"], [
        ("Customer", "I bought this jacket in medium, but it is tight across the "
                     "shoulders. Do you have a large?"),
        ("Shop assistant", "Let me check the shelf. If not, the fitting room has two "
                           "similar ones on sale."),
        ("Customer", "I would rather exchange it than take a refund. I like the quality."),
        ("Shop assistant", "An exchange is fine with the receipt. The price tag is still "
                           "on, so there is no problem."),
        ("Customer", "Is there a discount on the second one?"),
        ("Shop assistant", "Twenty percent, but it is a different brand and it runs small."),
    ],
)

_dlg(
    "food", "What is left in the kitchen", "چیزی که در آشپزخانه مانده",
    ["Roommate", "Cook"], [
        ("Roommate", "There is bread, cheese and one egg. Should we order pizza instead?"),
        ("Cook", "No need. I can make an omelette and a salad, and there is soup in the "
                 "freezer."),
        ("Roommate", "Do we have rice? I could cook kebab if there is meat."),
        ("Cook", "The meat is finished, but there is chicken. Buy some yogurt and a "
                 "lemon on the way home."),
        ("Roommate", "And coffee - we are out of it."),
        ("Cook", "Get tea too. We drink more tea than coffee in this house."),
    ],
)

_dlg(
    "fruits", "The stall at the end of the street", "دکهٔ آخر خیابان",
    ["Customer", "Seller"], [
        ("Customer", "Are the peaches ripe? Last week they were hard."),
        ("Seller", "These are from yesterday, and the watermelon is sweet. Try a slice."),
        ("Customer", "I will take a kilo of peaches and one pomegranate."),
        ("Seller", "The pomegranates are small but full of juice. The figs are better value."),
        ("Customer", "Then a box of figs as well, and two lemons for the tea."),
        ("Seller", "The strawberries are finished, but the cherries arrive tomorrow."),
    ],
)

_dlg(
    "vegetables", "A stew with what the garden gives", "خورشتی با محصول باغچه",
    ["Cook", "Gardener"], [
        ("Gardener", "The tomatoes are ready, and there is more spinach than we can eat."),
        ("Cook", "Perfect for a stew. I need onion, garlic and two carrots as well."),
        ("Gardener", "Take the eggplant too - it is small this year but sweet."),
        ("Cook", "Should I add potato, or is it heavy enough?"),
        ("Gardener", "A sweet potato would be lighter. There is chili if you want heat."),
        ("Cook", "Just one, and some lettuce for the side. The peas are still frozen, so "
                 "they can wait."),
    ],
)

_dlg(
    "work_business", "A project that needs one more week", "پروژه‌ای که یک هفته بیشتر می‌خواهد",
    ["Manager", "Employee"], [
        ("Manager", "The client wants the report on Monday. Can the team meet that "
                    "deadline?"),
        ("Employee", "The research is done, but the budget section needs the finance "
                     "figures. One extra week would make it solid."),
        ("Manager", "Then I will ask for a week and offer a shorter summary on Monday."),
        ("Employee", "That works. I will schedule a meeting with the client and update "
                     "the task list today."),
        ("Manager", "Who is leading the presentation?"),
        ("Employee", "The new colleague, with my support. It is good for his career, and "
                     "he knows the product."),
    ],
)

_dlg(
    "workplace", "Minutes, a grievance and a promotion", "صورت‌جلسه، شکایت و ارتقا",
    ["Line manager", "Team member"], [
        ("Line manager", "Before the meeting, I need the agenda circulated and the "
                         "minutes from last week."),
        ("Team member", "They are ready. I flagged two deliverables that will miss the "
                        "milestone unless we delegate part of the workflow."),
        ("Line manager", "I will tackle that with the stakeholder and escalate the budget "
                         "line if needed. Anything else?"),
        ("Team member", "One personal item: I submitted a grievance about the overtime "
                        "on my payroll."),
        ("Line manager", "I saw it, and we will follow up this week. On a better note, "
                         "your appraisal is positive - promotion is on the table."),
        ("Team member", "That is good to hear. I will sign off the brief this afternoon."),
    ],
)

_dlg(
    "jobs", "Two people describing their work", "دو نفر از کارشان می‌گویند",
    ["Parisa", "Tom"], [
        ("Parisa", "I am a pharmacist, so I spend the day explaining medicine to people."),
        ("Tom", "My sister is a nurse and my father was a farmer. Different worlds."),
        ("Parisa", "What do you do? You said something about design."),
        ("Tom", "I am a designer, but I trained as an architect. The pay is better in "
                "design."),
        ("Parisa", "Do you work with a programmer or an engineer?"),
        ("Tom", "Both, and a photographer. A small team, so everyone does two jobs."),
    ],
)

_dlg(
    "bank_money", "A card that will not work abroad", "کارتی که در خارج کار نمی‌کند",
    ["Customer", "Bank clerk"], [
        ("Customer", "My card was refused in Turkey. The balance is fine, so I do not "
                     "understand it."),
        ("Bank clerk", "The account is blocked for foreign payments. Did you travel "
                       "without telling us?"),
        ("Customer", "I did. I need to withdraw cash and pay a hotel bill tomorrow."),
        ("Bank clerk", "I can lift the block now. Carry some cash as well, and keep the "
                       "receipt for the exchange rate."),
        ("Customer", "Is there a fee for the transfer?"),
        ("Bank clerk", "A small one, shown on your statement. The discount applies only "
                       "to payments in the local currency."),
    ],
)

_dlg(
    "finance_b2", "The mortgage the bank would not agree to", "وام مسکنی که بانک نپذیرفت",
    ["Advisor", "Client"], [
        ("Client", "The bank refused the mortgage. They said my income is fine but my "
                   "expenditure is too high."),
        ("Advisor", "Do you have other debt - a loan, or an installment plan on a car?"),
        ("Client", "One loan, and a credit card balance I have been paying off slowly."),
        ("Advisor", "Clear the card first. It affects your credit score more than the "
                    "loan does."),
        ("Client", "And the deposit? They asked for a bigger one because of inflation."),
        ("Advisor", "Twenty percent is the realistic figure. I will build a budget that "
                    "shows your cash flow over six months."),
    ],
)

_dlg(
    "school", "The exam the whole class worried about", "امتحانی که کل کلاس نگرانش بود",
    ["Pupil", "Teacher"], [
        ("Pupil", "I left my notebook at home, so I have no notes for the lesson."),
        ("Teacher", "You can share with the student next to you, and write on paper for "
                    "today."),
        ("Pupil", "Will the exam cover the whole semester or only the last subject?"),
        ("Teacher", "The last two terms. Bring a pencil, a ruler and your schoolbag with "
                    "the book, nothing else."),
        ("Pupil", "And the project? Is the grade separate from the exam?"),
        ("Teacher", "Yes. The library has the books you need, and the schedule is on the "
                    "board."),
    ],
)

_dlg(
    "education_b1", "An essay, a deadline and a citation", "مقاله، مهلت و ارجاع",
    ["Student", "Tutor"], [
        ("Student", "I want to extend the deadline for my essay by three days. The "
                    "literature review took longer than I planned."),
        ("Tutor", "That is possible. Submit what you have on Friday and the full "
                  "assignment a week later."),
        ("Student", "Do I need the abstract before the introduction?"),
        ("Tutor", "No. Write the introduction, then the methodology, and revise the "
                  "abstract last."),
        ("Student", "The citation format is confusing me. Which reference style does the "
                    "department use?"),
        ("Tutor", "The one in the syllabus. And please check the plagiarism rules before "
                  "you paraphrase."),
    ],
)

_dlg(
    "academic_wordlist", "Reading a paper that contradicts itself", "خواندن مقاله‌ای که با خودش تناقض دارد",
    ["Supervisor", "Researcher"], [
        ("Researcher", "The study claims to demonstrate a correlation, but the data do "
                       "not indicate any significant change."),
        ("Supervisor", "Does it establish causation, or merely rely on previous findings?"),
        ("Researcher", "It relies on previous work and fails to distinguish the two "
                       "variables. The conclusion is not coherent."),
        ("Supervisor", "Then your critique should emphasize that, and justify why the "
                       "method is inadequate."),
        ("Researcher", "I can illustrate it with their own table, and predict what a "
                       "larger sample would show."),
        ("Supervisor", "Do that, but keep the tone appropriate - the authors are prominent "
                       "in the field."),
    ],
)

_dlg(
    "academic_vocab", "A result nobody can replicate", "نتیجه‌ای که کسی نمی‌تواند تکرار کند",
    ["Reviewer", "Author"], [
        ("Reviewer", "Your hypothesis is clear, but the methodology does not let anyone "
                     "replicate the experiment."),
        ("Author", "We acknowledge that. The anomaly came from one instrument, and we "
                   "tried to substantiate it with a second sample."),
        ("Reviewer", "That discrepancy needs to be delineated, not explained away. Can "
                     "you quantify the error?"),
        ("Author", "We can allocate two more weeks and incorporate the raw data in an "
                   "appendix."),
        ("Reviewer", "Good. Be careful not to conflate correlation with causation - your "
                     "conclusion currently does."),
        ("Author", "I will articulate that more carefully in the revision."),
    ],
)

_dlg(
    "formal_register", "A letter that must sound like a letter", "نامه‌ای که باید لحن نامه داشته باشد",
    ["Assistant", "Manager"], [
        ("Assistant", "Here is the draft. I wrote 'ask for' and 'get', which sounds too "
                       "informal for a client."),
        ("Manager", "Change them to 'request' and 'obtain', and use 'regarding' instead "
                    "of 'about'."),
        ("Assistant", "Should I write 'prior to' or 'before' in the second paragraph?"),
        ("Manager", "Either is correct, but 'prior to' is more formal. Keep 'sufficient' "
                    "for 'enough' and 'additional' for 'extra'."),
        ("Assistant", "And the closing - 'yours sincerely' or 'dear Sir or Madam'?"),
        ("Manager", "Use 'dear Sir or Madam' only if you do not know the name; otherwise "
                    "'yours sincerely'. Please submit it before noon."),
    ],
)

_dlg(
    "evaluation_language", "How sure can a report sound", "یک گزارش تا چه حد می‌تواند مطمئن باشد",
    ["Editor", "Writer"], [
        ("Writer", "The draft says the policy will definitely work. Is that too strong?"),
        ("Editor", "It is. 'Arguably' or 'presumably' is fairer, and 'on the whole' "
                   "softens the summary."),
        ("Writer", "The data are mixed, so I could say the result is 'a mixed blessing'."),
        ("Editor", "To some extent, yes. Admittedly the sample is small; that should "
                   "appear before the conclusion."),
        ("Writer", "Should I keep 'undoubtedly' anywhere?"),
        ("Editor", "Only for the figure itself. Everything else is 'largely' or "
                   "'comparatively' - and 'all things considered' closes it well."),
    ],
)

_dlg(
    "formal_advanced", "A contract clause read aloud", "خواندن یک بند قرارداد با صدای بلند",
    ["Solicitor", "Client"], [
        ("Solicitor", "The clause states that the tenant is liable for repairs, albeit "
                       "only for damage caused by negligence."),
        ("Client", "Notwithstanding that, the landlord must still maintain the roof - "
                   "insofar as the statute applies."),
        ("Solicitor", "Precisely. Furthermore, the deposit is refundable thereafter, "
                       "whereby the balance is returned within thirty days."),
        ("Client", "And pending the inspection? Can they withhold the whole amount?"),
        ("Solicitor", "No. Save for documented costs, the remainder is due; barring a "
                       "dispute, the matter ends there."),
        ("Client", "Then I will sign, subject to the aforementioned changes."),
    ],
)

_dlg(
    "law_rights", "Arrested, charged, and out on bail", "بازداشت، اتهام و آزادی با قید وثیقه",
    ["Client", "Lawyer"], [
        ("Client", "My brother was arrested last night. They say he was involved in an "
                   "offense near the station."),
        ("Lawyer", "Has he been charged, and is he in custody or out on bail?"),
        ("Client", "In custody. There is a witness, but no evidence that I know of."),
        ("Lawyer", "Then we ask for bail tomorrow. The judge will look at the verdict "
                   "history and whether he is liable to flee."),
        ("Client", "He has a residency permit and a job. Does that help?"),
        ("Lawyer", "It does. If the court imposes a fine, we can settle out of court on "
                   "the civil claim."),
    ],
)

_dlg(
    "public_services", "Renewing a licence before the deadline", "تمدید گواهینامه پیش از مهلت",
    ["Citizen", "Clerk"], [
        ("Citizen", "I need to renew my licence. Which form do I fill in at this counter?"),
        ("Clerk", "This one, with your identification and a photocopy of the certificate."),
        ("Citizen", "Do I need an appointment, or can I submit it today?"),
        ("Clerk", "Today is fine. There is a fee, and the signature must match the "
                  "passport."),
        ("Citizen", "My address changed last month. Does that affect the application?"),
        ("Clerk", "It does - bring proof of the new address, or the office will reject it "
                  "and you will have to complain in writing."),
    ],
)

_dlg(
    "science_tech_c1", "A result that will not replicate", "نتیجه‌ای که تکرار نمی‌شود",
    ["Researcher", "Reviewer"], [
        ("Researcher", "We ran the experiment three times and could not replicate the "
                       "original correlation."),
        ("Reviewer", "Was the control group the same size, and did the sample change "
                     "between runs?"),
        ("Researcher", "Same protocol, different sample. The statistics suggest the "
                       "effect is small, not absent."),
        ("Reviewer", "Then say so plainly. A robust finding survives peer review; a "
                     "fragile one needs replication."),
        ("Researcher", "The method is accurate but slow. We are prototyping an algorithm "
                       "to shorten it."),
        ("Reviewer", "Keep the evidence separate from the tool. Causation is not the same "
                     "as a faster pipeline."),
    ],
)

_dlg(
    "advanced_adjectives", "A review of a very quiet film", "نقدی بر فیلمی بسیار آرام",
    ["Critic", "Editor"], [
        ("Critic", "The film is subtle rather than vivid, and the dialogue is candid "
                   "about a mundane marriage."),
        ("Editor", "Is that compelling enough for a Saturday page? Readers want a "
                   "reason to go."),
        ("Critic", "The reason is the nuance. Nothing is lavish or profound; it is "
                   "honest, and quietly resilient."),
        ("Editor", "Your last review was skeptical about films like this."),
        ("Critic", "I was, and I still am about the ending, which is obscure on purpose. "
                   "But the acting is meticulous."),
        ("Editor", "Keep that ambivalence - it is fairer than praise, and less tedious "
                   "than a summary."),
    ],
)

_dlg(
    "animals", "The farm that lost a chicken", "مزرعه‌ای که یک مرغ گم کرد",
    ["Farmer", "Neighbour"], [
        ("Farmer", "One chicken is missing, and the dog will not stop barking at the "
                   "hedge."),
        ("Neighbour", "A fox, most likely. Did you see tracks near the sheep?"),
        ("Farmer", "No, but the goat is nervous and the horse was restless all night."),
        ("Neighbour", "Put the ducks and the turkey inside, and keep the rabbit hutch "
                      "shut."),
        ("Farmer", "The cat is useless. It slept through the whole thing."),
        ("Neighbour", "Cats are like that. The geese are better guards than any dog."),
    ],
)

_dlg(
    "art_design", "A portrait that is too realistic", "پرتره‌ای که زیادی واقعی است",
    ["Curator", "Artist"], [
        ("Curator", "The exhibition opens in three weeks. Is the portrait finished?"),
        ("Artist", "Almost. The composition works, but the texture of the canvas is too "
                   "smooth for the style."),
        ("Curator", "The gallery wall is bright; a darker shade behind it would help the "
                    "contrast."),
        ("Artist", "I was thinking abstract shapes in the background, and a sketch of "
                   "the hands in the corner."),
        ("Curator", "That could be a masterpiece, or a distraction. What is the "
                    "inspiration?"),
        ("Artist", "A painting I saw as a child. I want the design to feel drawn, not "
                   "photographed."),
    ],
)

_dlg(
    "business_vocab", "A quarterly report nobody read", "گزارشی فصلی که کسی نخواند",
    ["Director", "Analyst"], [
        ("Director", "The turnover is up, but the margin is down. What does the forecast "
                      "say for next quarter?"),
        ("Analyst", "Flat, unless we streamline procurement. The workload is already "
                    "high, and overtime is on the payroll."),
        ("Director", "Then delegate the reporting and escalate the invoice problem to "
                     "compliance."),
        ("Analyst", "I can prioritize two deliverables, but the milestone needs a "
                    "stakeholder decision."),
        ("Director", "Set up a meeting, sign off the agenda, and take minutes. I want the "
                     "quarterly report short enough to read."),
        ("Analyst", "One page. I will forecast the conservative number."),
    ],
)

_dlg(
    "collocations_b2", "The meeting where nobody decided", "جلسه‌ای که در آن کسی تصمیم نگرفت",
    ["Chair", "Member"], [
        ("Chair", "We need to reach an agreement today and make a decision on the budget."),
        ("Member", "I want to raise an issue first: we cannot meet a deadline we never "
                   "agreed to."),
        ("Chair", "Fair. Let us draw a distinction between the report and the launch, and "
                  "set a goal for each."),
        ("Member", "I will take responsibility for the report if someone else does the "
                   "research."),
        ("Chair", "I can carry out the research and keep track of the figures. We should "
                  "also hold a meeting with the client."),
        ("Member", "Then I will place the order for the equipment, and pay the bill this "
                   "week."),
    ],
)

_dlg(
    "describing_people", "The new neighbour everybody likes", "همسایهٔ جدیدی که همه دوستش دارند",
    ["Lena", "Marco"], [
        ("Lena", "The new neighbour is friendly and remarkably patient with the children."),
        ("Marco", "He is also punctual, which is rare in this building. Is he reliable?"),
        ("Lena", "Very. He is honest about what he can and cannot fix, and never careless "
                 "with tools."),
        ("Marco", "Some people find him a bit serious. I would say confident, not arrogant."),
        ("Lena", "He is shy until you talk about football, then he is talkative and "
                 "genuinely humorous."),
        ("Marco", "A good neighbour. His wife is the ambitious one - she runs two shops."),
    ],
)

_dlg(
    "digital_life", "The phone that forgot its password", "گوشی‌ای که رمزش را فراموش کرد",
    ["User", "Friend"], [
        ("User", "I cannot log in. The screen asks for a password I do not remember, and "
                 "the battery is nearly dead."),
        ("Friend", "Plug in the charger first. Then tap 'forgot password' and check your "
                   "username."),
        ("User", "Will that delete my backup? I have photos I never uploaded."),
        ("Friend", "No, but sync them when you are back online. Turn on Wi-Fi before you "
                   "download the update."),
        ("User", "The app also asks for a permission it does not need. Should I allow it?"),
        ("Friend", "Check the privacy settings and refuse. A screenshot app wants your "
                   "whole profile, which is suspicious."),
    ],
)

_dlg(
    "environment_b2", "A town arguing about its river", "شهری که بر سر رودخانه‌اش بحث می‌کند",
    ["Reporter", "Campaigner"], [
        ("Reporter", "The council approved the landfill beside the river. Is that "
                     "sustainable?"),
        ("Campaigner", "No. Waste disposal there would contaminate the water and destroy "
                       "the habitat of an endangered species."),
        ("Reporter", "They argue it reduces emissions from transport."),
        ("Campaigner", "Marginally, while the carbon footprint of the site grows. "
                       "Renewable energy and conservation would do more."),
        ("Reporter", "What about the drought last summer? Does it change the plan?"),
        ("Campaigner", "It should. Flooding and drought in one year is exactly what "
                       "climate change looks like here."),
    ],
)

_dlg(
    "idiomatic_collocations_c2", "A deal that was a blessing in disguise", "معامله‌ای که باطنش خیر بود",
    ["Investor", "Partner"], [
        ("Investor", "Losing that contract was a blessing in disguise - we were at the "
                     "mercy of one client."),
        ("Partner", "A far cry from where we started. Still, the terms left much to be "
                    "desired."),
        ("Investor", "By no means a disaster. We took it with a grain of salt and kept "
                     "abreast of the market."),
        ("Partner", "Now we are at the helm, and the new team will stand the test of time "
                    "if we do not sit on our hands."),
        ("Investor", "Agreed. Let us set the record straight with the bank and meet "
                     "halfway on the repayment."),
        ("Partner", "Then I will take a back seat on hiring and focus on the product."),
    ],
)

_dlg(
    "idioms_b2", "The pitch that broke the ice", "ارائه‌ای که یخ را شکست",
    ["Presenter", "Client"], [
        ("Presenter", "I will break the ice with a question: how many of you have "
                      "missed a deadline this month?"),
        ("Client", "All of us. So far so good, then - but the software looked "
                   "complicated."),
        ("Presenter", "It is a piece of cake once you set it up. The training is free, "
                      "and support answers out of the blue, even on Sundays."),
        ("Client", "Our manager wants to see eye to eye with the IT team before signing."),
        ("Presenter", "Then the ball is in your court. I can join that meeting and hit "
                      "the nail on the head about costs."),
        ("Client", "Let us call it a day. I will make up my mind by Thursday."),
    ],
)

_dlg(
    "idioms_c2", "A meeting that needed brass tacks", "جلسه‌ای که به اصل مطلب نیاز داشت",
    ["Chair", "Director"], [
        ("Chair", "Let us cut to the chase: the launch is up in the air and the board "
                  "wants a date."),
        ("Director", "To make matters worse, two suppliers are on thin ice and the "
                     "contract is a storm in a teacup for legal."),
        ("Chair", "Then get down to brass tacks. Read between the lines of their email "
                  "and tell me what they really want."),
        ("Director", "Money, by the book. They will not throw caution to the wind, and "
                     "they will not go the extra mile for free."),
        ("Chair", "Pull no punches with them. If they swallow their pride, we have a "
                  "golden opportunity."),
        ("Director", "I will leave no stone unturned and report on Friday. No picnic, "
                     "but doable."),
    ],
)

_dlg(
    "media_news", "A headline nobody can stand behind", "تیتری که کسی پشتش نمی‌ایستد",
    ["Editor", "Correspondent"], [
        ("Editor", "The headline says the minister was allegedly involved. Where is the "
                   "evidence?"),
        ("Correspondent", "Two sources, one document, and a witness who will not go on "
                          "the record."),
        ("Editor", "Then it is an allegation, not a fact. Cite the document and "
                   "fact-check the statistics before we publish."),
        ("Correspondent", "The investigation is solid, but the leak came from inside the "
                          "ministry."),
        ("Editor", "That is the story. Write a feature story, keep the poll out of the "
                   "lead, and let the editorial take the position."),
        ("Correspondent", "Understood. The broadcast version will be shorter, and the "
                          "podcast can carry the testimony."),
    ],
)

_dlg(
    "music", "A song that needs one more verse", "ترانه‌ای که یک بند دیگر می‌خواهد",
    ["Singer", "Guitarist"], [
        ("Singer", "The melody is good, but the chorus arrives too early and the lyrics "
                   "repeat themselves."),
        ("Guitarist", "Then we slow the tempo for one verse. The drum comes in after the "
                      "second line."),
        ("Singer", "I want the guitar quieter there so the voice carries. Is the piano "
                   "in the same key?"),
        ("Guitarist", "It is. We can add a violin on the last note, and keep the harmony "
                      "simple."),
        ("Singer", "The band plays it better live than on the album - the rhythm is "
                   "looser."),
        ("Guitarist", "Then record the concert. A microphone in the hall beats a studio "
                      "take with no audience."),
    ],
)

_dlg(
    "nature", "A walk before the rain", "پیاده‌روی پیش از باران",
    ["Hiker", "Guide"], [
        ("Hiker", "Is the path to the lake open? The map shows a river crossing."),
        ("Guide", "It is, but the bridge is old. Follow the branch of the trail along the "
                  "valley, under the cliff."),
        ("Hiker", "And the forest on the other side - is there a cave?"),
        ("Guide", "A small one, near the desert edge. Do not go in if it rains; the soil "
                  "above it moves."),
        ("Hiker", "The sky looks heavy. How long until the storm?"),
        ("Guide", "An hour. Take the stone path back, and watch for lightning on the "
                  "mountain."),
    ],
)

_dlg(
    "nuance_synonyms", "Choosing the exact word", "انتخاب واژهٔ دقیق",
    ["Translator", "Author"], [
        ("Author", "You translated 'angry' as 'irritated'. He was furious, not mildly "
                   "annoyed."),
        ("Translator", "I chose the softer word because the sentence says he spoke "
                       "calmly. Should I use 'furious' and keep the contrast?"),
        ("Author", "Yes. And here - 'he looked at her' became 'he stared at her'. That "
                   "changes the meaning."),
        ("Translator", "'Glance' would be closer. One quick look, no threat."),
        ("Author", "Exactly. The scene is ordinary, not strange - it should read "
                   "typical, almost boring."),
        ("Translator", "Then I will replace 'peculiar' with 'ordinary' and reduce the "
                       "adjectives by half."),
    ],
)

_dlg(
    "phrasal_verbs", "The flat that needs sorting out", "آپارتمانی که باید سر و سامان بگیرد",
    ["Tenant", "Friend"], [
        ("Tenant", "I am looking for a flat, and I have run out of time before the "
                   "contract ends."),
        ("Friend", "I can look into two agencies. Do you want me to come across on "
                   "Saturday?"),
        ("Tenant", "Please. I need to sort out the deposit first, and figure out how much "
                   "the move costs."),
        ("Friend", "Put off the furniture until you see the place. You can pick up a "
                   "cheap table later."),
        ("Tenant", "The landlord turned down my offer, so I may have to give in on the "
                   "price."),
        ("Friend", "Do not give up yet. We will go over the contract and rule out the "
                   "hidden fees."),
    ],
)

_dlg(
    "relationships", "Two friends who drifted apart", "دو دوست که از هم دور شدند",
    ["Nadia", "Reza"], [
        ("Nadia", "We used to keep in touch every week, and then we drifted apart. I "
                  "miss the friendship."),
        ("Reza", "There was a misunderstanding about the wedding, and neither of us "
                 "apologised."),
        ("Nadia", "I was jealous, honestly. You had a partner and a new flat, and I felt "
                  "left behind."),
        ("Reza", "I should have been more supportive. Trust works both ways, and I "
                 "assumed you did not care."),
        ("Nadia", "Can we make up? Not with a big gesture - just coffee on Fridays."),
        ("Reza", "Deal. Commitment to a small thing is easier than a promise to change "
                 "everything."),
    ],
)

_dlg(
    "technology", "The laptop that will not start", "لپ‌تاپی که روشن نمی‌شود",
    ["Owner", "Technician"], [
        ("Owner", "My laptop will not start. The charger works, but the screen stays "
                  "black."),
        ("Technician", "Does the battery light come on? Try a different socket and hold "
                       "the power button for ten seconds."),
        ("Owner", "Nothing. I have the files backed up on a hard drive, luckily."),
        ("Technician", "Then we test the memory first, and the router is not involved. "
                       "Is the software under warranty?"),
        ("Owner", "The hardware is, for one more month. There is also a virus warning "
                  "every time I open the browser."),
        ("Technician", "Leave it with me. I will update the program, check the database "
                       "of errors, and call you."),
    ],
)

_dlg(
    "tools_diy", "A shelf that will not stay level", "قفسه‌ای که تراز نمی‌شود",
    ["Helper", "Homeowner"], [
        ("Homeowner", "The shelf is not level and the bracket is loose. I think the wall "
                      "is broken behind it."),
        ("Helper", "Measure twice first. Hand me the tape measure and the drill."),
        ("Homeowner", "Do we need a screwdriver or a wrench for the bracket?"),
        ("Helper", "A screwdriver, and longer screws. The plug in the wall is too small, "
                   "so it pulls out."),
        ("Homeowner", "There is a leak under the sink too. Can we fix that today?"),
        ("Helper", "We can tighten the pipe and tape it, but the proper repair needs a "
                   "plumber. Assemble the shelf first."),
    ],
)

_dlg(
    "workplace_c1", "A restructuring nobody expected", "بازساختاری که کسی انتظارش را نداشت",
    ["Board member", "Director"], [
        ("Board member", "The projection shows a deficit next quarter. Which initiative "
                         "can we cut without hurting productivity?"),
        ("Director", "None of them cheaply. The restructuring is already in the roadmap, "
                     "and the merger needs due diligence."),
        ("Board member", "Then look at overhead and procurement. Our market share is "
                         "stable, but the churn worries shareholders."),
        ("Director", "We can outsource support and optimize the process, with clear "
                     "accountability and a benchmark for each KPI."),
        ("Board member", "Do it without burning the team. Retention is cheaper than "
                         "hiring, and the outlook depends on it."),
        ("Director", "Agreed. I will iterate on the plan and bring the escalation path to "
                     "the board on Monday."),
    ],
)

# ==========================================================================
# DIALOGUE QUESTIONS
# One question per dialogue, answerable from the script itself. The answer
# index points into the options; the builder checks it, and the page shows
# the explanation only after the learner has chosen.
# ==========================================================================

QUESTIONS = {
    "travel": ("Why did the passenger miss the connecting flight?",
               ["The gate closed early", "The first flight was late", "The passport was missing"],
               1, "The connection was missed because the first flight was delayed."),
    "airport_flight": ("Where did the suitcase go?",
                       ["To the wrong city", "Back home", "Nowhere - it was never checked"],
                       0, "Baggage service says it was sent to the wrong city and arrives tonight."),
    "hotel_stay": ("Why is the guest's room noisy?",
                   ["A party next door", "Street works outside", "The air conditioning unit above it"],
                   2, "The unit above the room runs all night, which is what wakes the guest."),
    "transport": ("Why can't the bus take the bridge today?",
                  ["It is closed for repairs", "The bus is too heavy", "There is no driver"],
                  0, "The bridge is closed, so the tram and a taxi are the quickest way."),
    "emergency_safety": ("How should the resident leave the building?",
                         ["By the lift", "By the emergency exit", "Through the window"],
                         1, "The fire officer says to use the emergency exit, never the lift."),
    "weather_seasons": ("Why is the ridge walk moved to the valley?",
                        ["Too many people booked", "The path is private", "There is fog and wind on the summit"],
                        2, "Fog on the summit and strong wind are why the walk changes."),
    "directions_words": ("Where is the main entrance?",
                         ["Opposite the signpost, after the roundabout", "Behind the bank", "On the third floor"],
                         0, "Go straight, turn left at the roundabout; the entrance is opposite the signpost."),
    "sports": ("Why can't the member join the evening swimming class?",
               ["It is full", "It is too expensive", "It is the wrong level"],
               0, "The class is full until the gym crowd leaves at seven."),
    "cooking_basics": ("What went wrong with the sauce?",
                       ["Too much salt", "The pan was too hot and it caught", "There was no garlic"],
                       1, "The pan was too hot, so the garlic caught and the sauce had to start again."),
    "restaurant_dining": ("What must the kitchen avoid for this guest?",
                          ["Fish", "Salt", "Nuts"],
                          2, "There is a nut allergy in the party, so the waiter recommends the fish."),
    "numbers": ("How much does each of the three people pay?",
                ["Forty", "Fifty", "Thirty"],
                0, "One hundred and twenty split three ways is forty each."),
    "colors": ("Which colour is the living room wall?",
               ["White", "Light gray", "Dark blue"],
               1, "The wall is light gray; the ceiling stays white and the door is not dark blue."),
    "quantities": ("How much rice does the helper suggest?",
                   ["About two cups", "One cup", "A kilogram"],
                   0, "A handful per person is roughly two cups for eight people."),
    "communication": ("What else is wrong besides the dropped calls?",
                      ["The battery dies", "Notifications and voicemail are off", "The screen is broken"],
                      1, "The notification sound may be off and the voicemail is full."),
    "emotions": ("Why is Kian disappointed?",
                 ["He lost his job", "The project was cancelled", "He missed a train"],
                 1, "The project was cancelled on Friday, after he had been proud of the work."),
    "body": ("Where does the patient feel the pain most?",
             ["The lower back", "The chest", "The head"],
             0, "The pain is low in the back and reaches the left knee."),
    "body_health": ("What does the pharmacist think it is?",
                    ["A simple cold", "Flu", "An allergy"],
                    1, "Five days of fever and cough looks like flu, not a cold."),
    "health_visits": ("What will the doctor do with the prescription?",
                      ["Stop it", "Double the dose", "Refill it at a lower dose"],
                      2, "The doctor refills it at a lower dose and books a check-up."),
    "sleep_wellbeing": ("What is the coach's first advice?",
                        ["Sleep earlier every night", "Take a pill", "Keep one wake-up time and no screen before bed"],
                        2, "The routine is the fix: one wake-up time and an hour to unwind."),
    "psychology_feelings": ("What does the colleague ask for?",
                            ["A new job", "Fewer meetings and shared reporting", "More pay"],
                            1, "The volume, not the motivation, is the problem."),
    "basic_words": ("Where is the kitchen?",
                    ["Behind the stairs", "Upstairs", "Outside the building"],
                    0, "The colleague points behind the stairs, and lunch is at one."),
    "daily_routine_words": ("What does Ben skip in the morning?",
                            ["The shower", "Breakfast", "Work"],
                            1, "Ben sets an alarm, does not get up, and skips breakfast."),
    "house": ("What is wrong with the shower?",
              ["It leaks", "The water stays cold", "There is no pressure"],
              1, "The water stays cold, so the landlord suspects the boiler."),
    "household_actions": ("What will Ali do before the guests arrive?",
                          ["Cook the chicken", "Wash the car", "Take out the trash"],
                          2, "Ali takes out the trash before the bell rings."),
    "family": ("Who is the little boy running between the tables?",
               ["Neda's nephew", "Neda's son", "Neda's cousin"],
               0, "The boy is her nephew; his twin sister is the girl in blue."),
    "places": ("Where is the pharmacy?",
               ["Opposite the bank", "On the corner next to the bakery", "Behind the mosque"],
               1, "The pharmacy is on the corner, next to the bakery."),
    "city": ("What does the visitor need for a library card?",
             ["A photo", "A bank card", "A ticket with the address and a passport"],
             2, "A utility bill with the address and a passport are enough."),
    "time_words": ("When is the deadline?",
                   ["Monday morning", "Friday at noon", "Saturday night"],
                   1, "The deadline is Friday at noon, and the draft comes tomorrow afternoon."),
    "adjectives": ("Which flat is quieter?",
                   ["The second one", "The first one", "Neither of them"],
                   0, "The second is more expensive but quiet, clean and close to the park."),
    "verbs": ("What does Sahar suggest first?",
              ["Take a class", "Buy a book", "Start with one dish"],
              2, "One dish, the ingredients, the recipe twice, and an hour."),
    "clothing": ("What does Sara need for the winter wedding?",
                 ["A light dress", "Warmer clothes and comfortable shoes", "A uniform"],
                 1, "The ceremony is outdoors, so boots, a scarf and gloves."),
    "shopping_clothes": ("Why does the customer want an exchange?",
                         ["The jacket is too tight across the shoulders", "The colour is wrong", "A button is missing"],
                         0, "The medium is tight, so a large or an exchange is needed."),
    "food": ("What can they cook without going shopping?",
             ["Pizza", "An omelette and a salad", "Kebab"],
             1, "There is bread, cheese, one egg and soup in the freezer."),
    "fruits": ("What arrives at the stall tomorrow?",
               ["Peaches", "Figs", "Cherries"],
               2, "The strawberries are finished, but the cherries arrive tomorrow."),
    "vegetables": ("What is ready in the garden?",
                   ["Potatoes", "Tomatoes and spinach", "Corn"],
                   1, "The tomatoes are ready and there is more spinach than they can eat."),
    "work_business": ("Why does the report need one more week?",
                      ["The client left", "The budget section needs the finance figures", "The team is on holiday"],
                      1, "The research is done; the budget figures are what is missing."),
    "workplace": ("What did the team member submit?",
                  ["A resignation", "A promotion request", "A grievance about overtime"],
                  2, "The grievance is about the overtime on the payroll."),
    "jobs": ("What does Tom do now?",
             ["Design", "Architecture", "Photography"],
             0, "He trained as an architect but works as a designer."),
    "bank_money": ("Why was the card refused?",
                   ["Foreign payments were blocked", "The balance was empty", "The card had expired"],
                   0, "The account is blocked for foreign payments and the clerk lifts the block."),
    "finance_b2": ("Why did the bank refuse the mortgage?",
                   ["There is no income", "Expenditure is too high", "There is no deposit at all"],
                   1, "The income is fine; the expenditure, the loan and the card balance are the problem."),
    "school": ("What will the exam cover?",
               ["The last two terms", "The whole year", "One subject only"],
               0, "The exam covers the last two terms."),
    "education_b1": ("What does the student want?",
                     ["A new topic", "A lower grade", "Three more days for the essay"],
                     2, "The essay needs three more days because the literature review took longer."),
    "academic_wordlist": ("What is wrong with the paper?",
                          ["It claims a correlation the data do not show", "It is too long", "It has no abstract"],
                          0, "The data indicate no significant change, so the claim does not hold."),
    "academic_vocab": ("What can the authors do about the anomaly?",
                       ["Change the hypothesis", "Quantify the error and add the raw data", "Withdraw the paper"],
                       1, "They can allocate two weeks and put the raw data in an appendix."),
    "formal_register": ("Which word is more formal than 'ask for'?",
                        ["Request", "Want", "Say"],
                        0, "The manager replaces 'ask for' with 'request' and 'get' with 'obtain'."),
    "evaluation_language": ("Which word is too strong for the draft?",
                            ["Arguably", "Definitely", "Presumably"],
                            1, "'Definitely' is too strong; 'arguably' and 'presumably' are fairer."),
    "formal_advanced": ("What must the landlord still do?",
                        ["Pay the deposit", "Maintain the roof", "Leave the flat"],
                        1, "The tenant is liable for negligence, but the landlord maintains the roof."),
    "law_rights": ("What will the lawyer ask for tomorrow?",
                   ["A fine", "Bail", "A new trial"],
                   1, "They ask for bail, since there is a witness but no evidence yet."),
    "public_services": ("What happens if the address proof is missing?",
                        ["The office will reject the application", "A bigger fee is charged", "Nothing at all"],
                        0, "Without proof of the new address the office rejects it."),
    "science_tech_c1": ("What could the team not do?",
                        ["Replicate the original correlation", "Collect data", "Write the paper"],
                        0, "Three runs could not replicate the original correlation."),
    "advanced_adjectives": ("How does the critic describe the film?",
                            ["Loud and shallow", "Subtle rather than vivid", "Long and tedious"],
                            1, "It is subtle, candid about a mundane marriage, and meticulously acted."),
    "animals": ("What probably took the chicken?",
                ["The dog", "A fox", "A cat"],
                1, "A fox is most likely, and the geese guard better than the dog."),
    "art_design": ("What is wrong with the portrait?",
                   ["The colours are too dark", "It is unfinished", "The canvas texture is too smooth"],
                   2, "The texture is too smooth for the style the artist wants."),
    "business_vocab": ("What is down while turnover is up?",
                       ["The margin", "The workload", "The forecast"],
                       0, "Turnover is up but the margin is down, and the forecast is flat."),
    "collocations_b2": ("What must they do today?",
                        ["Find a new client", "Reach an agreement", "Take a holiday"],
                        1, "They need to reach an agreement and make a decision on the budget."),
    "describing_people": ("How is the new neighbour described?",
                          ["Shy and careless", "Friendly and punctual", "Lazy and strict"],
                          1, "He is friendly, patient, punctual and reliable."),
    "digital_life": ("What is the first step?",
                     ["Buy a new phone", "Delete the account", "Charge the phone and reset the password"],
                     2, "Charge it, tap 'forgot password', and check the username."),
    "environment_b2": ("Why is the landfill a bad idea?",
                       ["It costs too much", "It would contaminate the water and harm a habitat", "It is too far from town"],
                       1, "Waste disposal there would contaminate the river and destroy an endangered habitat."),
    "idiomatic_collocations_c2": ("How does the investor see losing the contract?",
                                  ["A blessing in disguise", "A disaster", "A mistake"],
                                  0, "Losing it ended their dependence on one client."),
    "idioms_b2": ("How does the presenter begin?",
                  ["With the price", "With a question to break the ice", "With a video"],
                  1, "The presenter breaks the ice with a question about missed deadlines."),
    "idioms_c2": ("What does the board want?",
                  ["A date for the launch", "More suppliers", "A new chair"],
                  0, "The launch is up in the air and the board wants a date."),
    "media_news": ("What does the editor demand before publishing?",
                   ["A longer headline", "Evidence and a fact-check", "A photograph"],
                   1, "An allegation needs evidence, and the statistics must be fact-checked."),
    "music": ("What arrives too early in the song?",
              ["The chorus", "The drum", "The violin"],
              0, "The chorus arrives too early and the lyrics repeat themselves."),
    "nature": ("Why should the hiker stay out of the cave in the rain?",
               ["It is closed", "It is too dark", "The soil above it moves"],
               2, "The guide says the soil above the cave moves when it rains."),
    "nuance_synonyms": ("Which word fits 'he was very angry'?",
                        ["Irritated", "Furious", "Calm"],
                        1, "'Furious' is the strong word; 'irritated' is too soft for the scene."),
    "phrasal_verbs": ("What has the tenant run out of?",
                      ["Time before the contract ends", "Money for the deposit", "Furniture"],
                      0, "The contract is ending and there is no time left to look."),
    "relationships": ("What caused the distance between them?",
                      ["A new job", "A misunderstanding about the wedding", "Money"],
                      1, "A misunderstanding about the wedding, and neither of them apologised."),
    "technology": ("What is wrong with the laptop?",
                   ["The screen is cracked", "It will not start", "It has no internet"],
                   1, "The screen stays black even with a working charger."),
    "tools_diy": ("Why does the bracket pull out of the wall?",
                  ["The shelf is too heavy", "The plug in the wall is too small", "The drill is broken"],
                  1, "The plug is too small, so longer screws are needed."),
    "workplace_c1": ("What worries the shareholders?",
                     ["Churn", "The market share", "The roadmap"],
                     0, "Market share is stable, but the churn worries shareholders."),
}
