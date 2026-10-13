#!/usr/bin/env python3
"""Harness round 2 — the three things a real learner asks that nothing answered.

Round 2's probes came back with "I'm not sure I understand" on the questions a
tutor is asked most: **what's the difference between X and Y*, **how do you
pronounce that*, **is this sentence correct*, and **what does this idiom mean*.

This writes the data behind them:

  distinctions.json  — classic confusable pairs, graded A1 → C2
  idioms.json        — figurative English with no dictionary gloss
  corrections.json   — the errors Persian speakers actually make, each with
                       the reason, so a fix teaches instead of just scolding

Run after editing; it is idempotent.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- distinctions
# (a, b, level, why they differ, one example each side, keywords)
DISTINCTIONS = [
    ("affect", "effect", "B1",
     "'Affect' is usually the verb (to change something); 'effect' is usually "
     "the noun (the change itself). The only common exception is the phrase "
     "'effect' as in 'to have an effect on'.",
     [("The rain **affected** our plans.", "باران برنامه‌های ما را تحت تأثیر قرار داد."),
      ("The rain had a big **effect** on our plans.", "باران تأثیر زیادی بر برنامه‌های ما داشت.")]),
    ("since", "for", "B1",
     "'Since' marks a point in time (since 2020, since Monday). 'For' marks a "
     "length of time (for three years, for two hours).",
     [("I have lived here **since** May.", "از ماه مه اینجا زندگی می‌کنم."),
      ("I have lived here **for** three years.", "سه سال است که اینجا زندگی می‌کنم.")]),
    ("borrow", "lend", "A2",
     "You **borrow** from someone; someone **lends** to you.",
     [("Can I **borrow** your pen?", "می‌توانی قلمت را به من قرض بدهی؟"),
      ("Can you **lend** me your pen?", "می‌توانی قلمت را به من قرض بدهی؟")]),
    ("in", "on", "B1",
     "'On' touches a surface or a day (on the table, on Monday). 'In' is "
     "inside something or for a period (in the box, in June).",
     [("The book is **on** the table.", "کتاب روی میز است."),
      ("The book is **in** the box.", "کتاب در جعبه است.")]),
    ("between", "among", "B2",
     "'Between' separates two or more individual things. 'Among' places "
     "something inside a group.",
     [("The match is **between** Iran and Japan.", "بازی بین ایران و ژاپن است."),
      ("He is the tallest **among** the players.", "او بلندترین بین بازیکنان است.")]),
    ("speak", "talk", "A2",
     "'Speak' is about the language used (speak English). 'Talk' is about the "
     "act of exchanging words, about anything (talk about money, talk to Ali).",
     [("Can you **speak** English?", "آیا می‌توانی انگلیسی صحبت کنی؟"),
      ("Let's **talk** about the plan.", "بیایید درباره برنامه صحبت کنیم.")]),
    ("say", "tell", "A2",
     "'Say' takes the words directly (say hello). 'Tell' needs a person "
     "after it (tell Ali). Both take a thing directly: 'say the truth', "
     "'tell the truth'.",
     [("He said **hello** to me.", "او به من سلام کرد."),
      ("He told me **hello**.", "او به من سلام کرد."),
      ("**Say** the truth.", "حقیقت را بگو."),
      ("**Tell** the truth.", "حقیقت را بگو.")]),
    ("bring", "take", "A2",
     "Both move things away from the speaker, but 'bring' moves it **toward** "
     "the place you are ('bring it here'), and 'take' moves it **away** "
     "('take it there').",
     [("**Bring** your book to my house.", "کتابت را به خانه من بیاور."),
      ("**Take** your book to school.", "کتابت را به مدرسه ببر.")]),
    ("make", "do", "A2",
     "'Make' builds or creates something; 'do' is an action you perform, "
     "especially work or a task. 'Make a cake', 'do your homework'.",
     [("She can **make** a cake.", "او می‌تواند کیک درست کند."),
      ("I **do** my homework at night.", "من شب‌ها تکلیفم را می‌کنم.")]),
    ("some", "any", "A2",
     "'Some' is used in affirmative and offer sentences (I have some money, "
     "Would you like some tea?). 'Any' is used in negatives and questions "
     "(I don't have any money, Do you have any tea?).",
     [("I have **some** questions.", "چند تا سؤال دارم."),
      ("I don't have **any** questions.", "هیچ سؤالی ندارم.")]),
    ("present perfect", "past simple", "B2",
     "'Present perfect' links the past to now: it says the TIME is not "
     "finished or not named. 'Past simple' puts the action at a stated or "
     "finished past time. Never use the past simple with 'yesterday', "
     "'last year' or 'in 2020'.",
     [("I **have lost** my keys. (I still don't have them.)",
       "کلیدم را گم کرده‌ام. (هنوز پیدایش نکرده‌ام.)"),
      ("I **lost** my keys **yesterday**.",
       "کلیدم را دیروز گم کردم.")]),
    ("because", "since", "B1",
     "'Because' gives a full reason with words. 'Since' is shorter and needs "
     "a point in time. Since is also the present perfect's time word: "
     "'since 2020', never 'since I lost it'.",
     [("I stayed in **because** it was raining.",
       "چون باران می‌بارید داخل ماندم."),
      ("I have stayed in **since** Friday.",
       "از جمعه اینجا مانده‌ام.")]),
    ("a", "an", "A1",
     "'An' before a vowel **sound** (an apple, an hour, an MP3). 'A' before a "
     "consonant sound (a university, a European city).",
     [("I need **an** umbrella.", "به چتر نیاز دارم."),
      ("She goes to **a** university.", "او به یک دانشگاه می‌رود.")]),
    ("by", "until", "B1",
     "'Until' marks the end of a period (wait until tomorrow). 'By' means "
     "no later than, and is common with a deadline (by Friday).",
     [("Wait **until** I come.", "تا وقتی که برمی‌گردم صبر کن."),
      ("Finish the work **by** Friday.", "کار را تا جمعه تمام کن.")]),
    ("each", "every", "B1",
     "'Each' separates two items (each of the students). 'Every' looks at "
     "three or more (every day). Both go before a noun.",
     [("**Each** of them has a book.", "هر کدام از آن‌ها یک کتاب دارند."),
      ("I read **every** day.", "من هر روز مطالعه می‌کنم.")]),
    ("few", "a few", "B1",
     "'A few' = some, a small positive number. 'Few' alone = almost none, "
     "negative.",
     [("I have **a few** questions.", "چند تا سؤال کم دارم."),
      ("I have **few** questions.", "تقریباً هیچ سؤالی ندارم.")]),
    ("although", "though", "B1",
     "Same meaning; different position. 'Although' starts a clause and is "
     "followed by a full clause. 'Though' can also stand alone at the end.",
     [("**Although** it rained, we went out.", "با اینکه باران می‌بارید، بیرون رفتیم."),
      ("We went out, **though** it rained.", "ما بیرون رفتیم، هرچند باران می‌بارید.")]),
    ("interesting", "interested", "A2",
     "'Interesting' describes the thing. 'Interested' describes the person's "
     "feeling. This is the classic Persian-speaker mistake (از کلمه علاقه).",
     [("The film was very **interesting**.  ↳ فیلم خیلی جالب بود.",
      "I'm **interested** in history.  ↳ من به تاریخ علاقه‌مند هستم.")]),
    ("used to", "get used to", "B2",
     "'Used to + verb' is a habit in the past that is gone. 'Get used to + "
     "noun/gerund' is getting comfortable with something.",
     [("I **used to** play chess every day.", "قبلاً هر روز شطرنج بازی می‌کردم."),
      ("I'm getting **used to** waking up early.", "دارم به زود بیدار شدن عادت می‌کنم.")]),
    ("interested in", "interesting", "A2",
     "Keep them in the right order: a person is **interested in** something; "
     "the thing is **interesting**.",
     [("She's **interested in** Persian art.", "او به هنر ایرانی علاقه‌مند است."),
      ("Persian art is very **interesting**.  ↳ هنر ایرانی خیلی جالب است.")]),
    ("by the way", "on the way", "B1",
     "'By the way' is a phrase that introduces a new topic. 'On the way' "
     "describes travel.",
     [("**By the way**, I called Ali yesterday.", "راستی، دیروز به علی زنگ زدم."),
      ("I bought bread **on the way** home.", "در راه خانه نان خریدم.")]),
    ("look for", "look after", "B2",
     "People confuse these constantly: look **for** = search for, look "
     "**after** = take care of. (Look **up** is a third one: search the "
     "meaning.)",
     [("I'm **looking for** my keys.", "دنبال کلیدم می‌گردم."),
      ("She **looks after** her little brother.", "او مراقب برادر کوچکش است.")]),
    ("look up", "find out", "B1",
     "'Look up' means to search for a meaning or a phone number. 'Find out' "
     "means to discover a fact.",
     [("**Look up** this word in a dictionary.", "این کلمه را در فرهنگ لغت پیدا کن."),
      ("**Find out** what happened.", "فهمیدن اتفاقی که افتاد.")]),
    ("borrow from", "lend to", "A2",
     "'Borrow' takes the source (borrow from Ali). 'Lend' takes the receiver "
     "(lend to Ali). 'Keep' means to hold onto something you already have.",
     [("I borrowed it **from** Ali.", "آن را از علی قرض گرفتم."),
      ("Ali lent it **to** me.", "علی آن را به من قرض داد."),
      ("I **kept** the book for a year.", "کتاب را یک سال نگه داشتم.")]),
    ("used", "broken", "A1",
     "Confused spelling: 'used to' (past habit), 'use to' is wrong; "
     "'broke' is the past of break, 'broken' is the adjective.",
     [("I **used to** sing, but now I don't.", "قبلاً آواز می‌خواندم، اما الان نه."),
      ("He **broke** the glass. It is **broken**.", "او لیوان را شکست. لیوان شکسته است.")]),
    ("weather", "whether", "B2",
     "'Weather' is the sky. 'Whether' asks about a choice: I don't know "
     "**whether** he is coming.",
     [("The **weather** is nice today.", "هوا امروز خوب است."),
      ("I don't know **whether** he will come.", "نمی‌دانم آیا او می‌آید یا نه.")]),
    ("lie", "lay", "B1",
     "'Lie' is intransitive (lie down) and 'lay' is transitive (lay the "
     "table). Irregular verbs mixed up constantly.",
     [("I **lay** on the sofa and watched TV.", "روی مبل دراز کشیدم و تلویزیون دیدم."),
      ("**Lay** the books on the desk.", "کتاب‌ها را روی میز بگذار.")]),
    ("beside", "besides", "B1",
     "'Beside' = next to. 'Besides' = in addition to.",
     [("Sit **beside** me.", "کنار من بنشین."),
      ("**Besides** English, I speak Persian.", "علاوه بر انگلیسی، فارسی هم صحبت می‌کنم.")]),
    ("farther", "further", "C1",
     "Both mean 'more distant'. 'Further' is the standard for physical "
     "distance and for extra quantity; 'farther' is physical distance only.",
     [("Go **further** — we are not there yet.", "جلوتر برو، هنوز نرسیده‌ایم."),
      ("Tell me **further** details.", "جزئیات بیشتری بگو.")]),
    ("imply", "infer", "C1",
     "'Imply' = to suggest indirectly. 'Infer' = to conclude from evidence. "
     "The verb and the noun use different words.",
     [("His silence **implied** agreement.", "سکوتش به سکوت رضایت اشاره داشت."),
      ("We can **infer** that he agreed.", "می‌توانیم نتیجه بگیریم که او موافقت کرد.")]),
    ("comprised of", "comprise", "C2",
     "'Comprise' is a verb (the whole comprises the parts). It is not a "
     "passive participle, so 'comprised of' is informal and often criticised.",
     [("The team **comprises** ten members.", "تیم از ده عضو تشکیل شده است."),
      ("The committee **is comprised of** five people.", "کمیته از پنج نفر تشکیل شده است.")]),
    ("due to", "because of", "C1",
     "'Due to' is a preposition (Due to rain, we stayed in). 'Because of' is "
     "also a preposition but joins to a noun. Both are correct for cause.",
     [("**Due to** rain, we stayed inside.", "به دلیل باران، داخل ماندیم."),
      ("We stayed inside **because of** the rain.", "به خاطر باران داخل ماندیم.")]),
    ("regret", "regretful", "C1",
     "'Regret' is a verb or noun. 'Regretful' is the adjective. Mixing them "
     "is a common advanced-learner slip.",
     [("I **regret** saying that.", "از گفتن آن متأسفم."),
      ("I am **regretful** about the decision.", "از آن تصمیم متأسفم.")]),
    ("notwithstanding", "despite", "C2",
     "'Despite' takes a noun; 'notwithstanding' takes a full clause and is "
     "formal. 'Despite of' is wrong.",
     [("**Despite** the rain, we played.", "با وجود باران بازی کردیم."),
      ("**Notwithstanding** the rain, we played.", "باران notwithstanding بازی کردیم.")]),
    ("alike", "likely", "B2",
     "'Alike' = similar (they look alike). 'Likely' = probable (it is likely "
     "to rain). One letter, two meanings.",
     [("The twins look very **alike**.  ↳ دوقلوها خیلی شبیه هم هستند.",
      "It is **likely** to rain today.  ↳ امروز احتمالاً باران می‌بارد.")]),
    ("advice", "advise", "B2",
     "'Advice' is the noun (uncountable). 'Advise' is the verb. No plural, "
     "and it never takes an 's'.",
     [("Let me give you some **advice**.  ↳ بگذار به تو یک مشاوره بدهم.",
      "I **advise** you to rest.  ↳ به تو توصیه می‌کنم استراحت کنی.")]),
    ("practise", "practice", "B2",
     "British English: 'practise' is the verb, 'practice' the noun. American "
     "English uses 'practice' for both.",
     [("She **practises** the piano daily.  ↳ او هر روز پیانو می‌نوازد.",
      "She has a daily piano **practice**.  ↳ او یک تمرین روزانه پیانو دارد.")]),
    ("affect", "effect", "C1",
     "Also as a verb: 'to effect a change' is formal and rarer than 'to "
     "affect a change'.",
     [("The new law **effects** many changes.  ↳ قانون جدید تغییرات زیادی ایجاد می‌کند.",
      "The new law **affects** many people.  ↳ قانون جدید بر مردم زیادی تأثیر می‌گذارد.")]),
    ("at the end", "in the end", "B1",
     "'At the end' = at the final point of something (at the end of the film). "
     "'In the end' = after considering everything (in the end, she said no).",
     [("Turn left **at the end** of the street.", "در انتهای خیابان بپیچ چپ."),
      ("**In the end**, it was not important.", "در نهایت، مهم نبود.")]),
    ("who", "which", "B1",
     "'Who' is for people. 'Which' is for things. In informal English 'who' "
     "is sometimes used for things, but avoid it in exams.",
     [("The man **who** called is my uncle.", "مردی که زنگ زد عموی من است."),
      ("The book **which** I lost was new.", "کتابی که گم کردم نو بود.")]),
    ("quantity of", "number of", "B1",
     "'Number of' for countable things (a number of books). 'Quantity of' for "
     "uncountable (a large quantity of water). This distinction can change "
     "the meaning of 'few' and 'much'.",
     [("a **number of** students", "تعدادی دانشجو"),
      ("a **quantity of** water", "مقداری آب")]),
    ("not ... because", "because ... not", "C2",
     "Word order changes the meaning: 'I didn't leave **because** I was tired' "
     "means he had another reason.",
     [("I didn't leave **because** I was tired.", "به این دلیل نرفتم که خسته بودم."),
      ("I left **because** I wasn't tired.", "رفتم چون خسته نبودم.")]),
]

IDIOMS = [
    ("spill the beans", "لو دادن راز", "informal",
     "to tell a secret by accident", "Did you spill the beans?"),
    ("piece of cake", "کیک اسفنجی", "idiom",
     "something very easy", "The exam was a piece of cake."),
    ("break the ice", "شکستن یخ", "idiom",
     "to start a conversation with strangers", "He told a joke to break the ice."),
    ("under the weather", "زیر سقف", "idiom",
     "feeling slightly ill", "I'm a bit under the weather today."),
    ("once in a blue moon", "یک بار در ماه", "idiom",
     "very rarely", "We meet once in a blue moon."),
    ("hit the books", "کتاب خواندن", "informal",
     "to study hard", "I need to hit the books before the exam."),
    ("cost an arm and a leg", "خیلی گران بود", "idiom",
     "to be very expensive", "That car cost me an arm and a leg."),
    ("get the hang of it", "به آن عادت کردن", "idiom",
     "to become good at something after practice", "You'll get the hang of it."),
    ("out of the blue", "ناگهانی", "idiom",
     "completely unexpected", "He called me out of the blue."),
    ("call it a day", "کار را تمام کردن", "idiom",
     "to stop working for now", "It's five — let's call it a day."),
    ("a blessing in disguise", "نعمت پنهان", "idiom",
     "a bad event that turns out good", "Losing that job was a blessing in disguise."),
    ("bite the bullet", "تحمل کردن", "idiom",
     "to do something unpleasant you cannot avoid", "We'll have to bite the bullet."),
    ("keep an eye on", "زیر نظر داشتن", "idiom",
     "to watch or look after", "Keep an eye on my bag, please."),
    ("from head to toe", "از سر تا نوک پا", "idiom",
     "over the whole body", "He was wet from head to toe."),
    ("no pain, no gain", "بدون رنج، بدون سود", "saying",
     "you must suffer to gain something", "No pain, no gain — keep training."),
    ("the last straw", "آخرین صبر / توان", "idiom",
     "the final problem that causes you to give up", "That was the last straw."),
    ("on the ball", "هوشیار و آماده", "idiom",
     "alert and quick to react", "She is always on the ball."),
    ("get cold feet", "دل سرد شدن / منصرف شدن", "idiom",
     "to become afraid and change your mind", "He got cold feet before signing."),
    ("in the same boat", "در یک کشتی", "idiom",
     "in the same difficult situation", "We're all in the same boat."),
    ("cut corners", "گوشه را گوشه گذاشتن", "idiom",
     "to do something cheaply and badly", "Don't cut corners on safety."),
    ("miss the boat", "از قطار جا ماندن", "idiom",
     "to be too late for an opportunity", "Don't miss the boat — apply today."),
    ("a big deal", "یک اتفاق بزرگ", "informal",
     "an important matter", "It's not a big deal, don't worry."),
    ("a piece of advice", "یک نصیحت", "idiom",
     "some advice", "Can I give you a piece of advice?"),
    ("so far so good", "تا اینجا خوب بوده", "saying",
     "things are going well until now", "So far so good — half way there."),
    ("to be honest", "راستش", "idiom",
     "used to say something true, maybe surprising", "To be honest, I disagree."),
    ("as far as I know", "تا جایی که می‌دانم", "idiom",
     "based on the information I have", "As far as I know, the shop is open."),
    ("the thing is", "نکته این است", "idiom",
     "used to introduce the real point", "The thing is, I have no money."),
    ("let the cat out of the bag", "بستن راز را لو دادن", "idiom",
     "to reveal a secret", "She let the cat out of the bag."),
    ("give it a shot", "یک بار امتحان کردن", "informal",
     "to try something, accepting the risk", "Just give it a shot."),
    ("in hot water", "به دردسر افتاده", "idiom",
     "in trouble", "He's in hot water with his teacher."),
    ("a piece of luck", "شانس", "idiom",
     "something fortunate", "It was a piece of luck that we met."),
    ("under control", "تحت کنترل", "idiom",
     "being managed well", "Everything is under control."),
    ("by heart", "از حفظ", "idiom",
     "memorised", "I know the poem by heart."),
    ("day by day", "روز به روز", "idiom",
     "gradually, a little each day", "He gets better day by day."),
]

# ---------------------------------------------------------------- corrections
# (pattern, message, fix, why)
# Each rule replaces the span it matches. Templates may use:
#   {0}  the first word of the match   {1}  the last word of the match
#   {pp} the past participle of {1}, looked up in PAST_PARTICIPLES
CORRECTIONS = [
    (r"\b(he|she|it)\s+(don['’]?t|do not)\b",
     "Subject-verb agreement", "{0} doesn't",
     "With he / she / it the verb takes -s, even in the negative: "
     "'He doesn't like it'."),
    (r"\b(they|we|you|i)\s+(doesn['’]?t|does not)\b",
     "Subject-verb agreement", "{0} don't",
     "With I / we / you / they the verb has no -s: 'They don't like it'."),
    (r"\bi\s+(is|are|was|were)\b",
     "Subject-verb agreement", "I am / {1} is",
     "'I am' in the present, 'I was' in the past. Never 'I is'."),
    (r"\bhave\s+(went|gone|ate|eaten|saw|seen|made|taken|took|said|come|"
     r"came|did|done|got|found|knew|known|thought|bought|gave|given|"
     r"wrote|written|spoke|spoken|drove|driven|broke|broken|felt|kept|"
     r"left|met|paid|put|set|sat|stood|understood|worn|run|ran)\b",
     "Present perfect needs a participle", "have {pp}",
     "After have / has / been the verb must be the past participle: "
     "'I have gone', not 'I have went'."),
    (r"\b(doesn['’]?t|don['’]?t|didn['’]?t|did not)\s+"
     r"(went|came|saw|ate|made|took|said|got|gave|knew|thought|bought|"
     r"wrote|spoke|drove|broke|felt|kept|left|met|had|did|was|were|"
     r"gone|eaten|seen|taken|given|known|written|spoken|driven|broken)\b",
     "Past tense needs the base verb", "{0} {base}",
     "After don't / doesn't / didn't the verb goes back to its base form: "
     "'I didn't go', not 'I didn't went'."),
    (r"\bmore\s+(better|worse|bigger|smaller|easier|harder|faster|"
     r"slower|cheaper|prettier)\b",
     "Double comparison", "{1}",
     "Do not use 'more' with a word that is already comparative: "
     "'more better' becomes 'better'."),
    (r"\bmost\s+(best|worst|easiest|hardest|tallest|biggest|"
     r"most beautiful)\b",
     "Double superlative", "the {1}",
     "'Most' doubles the superlative: 'most best' becomes 'the best'."),
    (r"\b(can|will|should|must|could|would|may|might)\s+to\b",
     "Modal verb never takes to", "{0} {1}",
     "Modal verbs stand alone: 'can go', 'must go' - never 'can to go'."),
    (r"\b(is|are|was|were|be|been|being)\s+(in\s+)?agree\b",
     "Wrong word", "agree",
     "'Agree' is a verb. Say 'I agree' or 'I am in agreement with you'."),
    (r"\bdiscuss\s+about\b", "Extra preposition", "discuss",
     "'Discuss' is transitive and takes no 'about': 'discuss the plan'."),
    (r"\bexplain\s+me\b", "Explain needs to me", "explain to me",
     "'Explain' takes the thing first, then the person: 'explain it to me'."),
    (r"\badvices\b", "Uncountable noun", "advice",
     "'Advice' has no plural. Say 'a piece of advice'."),
    (r"\b(informations|knowledges|equipments|furnitures|advices|"
     r"softwares|researches|homeworks)\b",
     "Uncountable noun", "{sg}",
     "This noun has no plural in English: 'information', 'advice', "
     "'equipment'."),
    (r"\bregard\s+of\b", "Wrong idiom", "regardless of",
     "The phrase is 'regardless of' or 'in spite of'."),
    (r"\bdespite\s+of\b", "Wrong idiom", "despite",
     "'Despite' takes no 'of': 'despite the rain'."),
    (r"\bsince\s+(\d+)\s+years?\b", "Wrong preposition", "for {0} year(s)",
     "For a duration use 'for': 'for three years'. Use 'since' with a point "
     "in time: 'since 2020'."),
    (r"\binterested\s+(about|on)\b", "Wrong preposition", "interested in",
     "The set phrase is 'interested in something'."),
    (r"\bdepend\s+(of|to)\b", "Wrong preposition", "depend on",
     "Always 'depend on' - never 'depend of'."),
    (r"\bmarry\s+(with|to)\b", "Wrong preposition", "marry",
     "'Marry' takes no preposition: 'I married Ali'."),
    (r"\bwaiting\s+(to|for)\s+(decide|choose|think|see)\b",
     "Wrong preposition", "waiting to {1}",
     "After 'wait' use 'to' + base verb: 'waiting to see'."),
    (r"\b(depend|concentrate)\s+(on|upon)\b", "Correct preposition", "{0} {1}",
     "Good - keep 'depend on' and 'concentrate on'."),
    (r"\bthe\s+same\s+same\b", "Repetition", "the same",
     "One 'same' is enough."),
    (r"\b(is is|the the|of of|in in|and and)\b", "Doubled word", "{0}",
     "The word is repeated - a slip of the keyboard or the tongue."),
    (r"\bi\s+(?:am\s+)?(?:have\s+)?(?:18|19|20)\d{2}\s*years\s+old\s+age\b",
     "Redundant", "I am {1} years old",
     "'Age' is not needed after 'years old'."),
    (r"\bin\s+the\s+conclusion\b", "Fixed expression", "in conclusion",
     "The set phrase is 'in conclusion', no article."),
    (r"\bby\s+the\s+time\s+when\b", "Redundant", "by the time",
     "'By the time' already means 'when'."),
    (r"\bevery\s+each\b", "Double determiner", "every",
     "Choose one: 'every student' or 'each student'."),
    (r"\bboth\s+of\s+the\s+two\b", "Over-specified", "both",
     "'Both' already means two: 'both students'."),
    (r"\beffect\s+of\s+(a|an|the)\b", "Wrong word",
     "affect of {1}",
     "The verb is 'affect', the noun is 'effect': 'the effect of the rain'."),
    (r"\byour\s+(welcome|right|wrong)\b", "Missing apostrophe", "you're {1}",
     "'You're welcome' and 'you're right' use the contraction 'you are'."),
    (r"\bit['’]s\s+own\b", "Possessive vs contraction", "its own",
     "'Its' shows possession; 'it's' means 'it is' or 'it has'."),
    (r"\b(less|more)\s+than\s+(more|less)\b", "Double comparison", "{0} than {2}",
     "Use one comparative only: 'more than', not 'more than more'."),
    (r"\bno\s+(understand|know|like|want|need|have|go|do|speak|eat|read)\b",
     "Missing auxiliary", "don't {1}",
     "The negative needs a helper verb: 'I don't understand', never "
     "'I no understand'."),
    (r"\b(i|we|they)\s+(is|are|was|were)\s+(\w+ing)\b",
     "Wrong word order", "reorder the sentence",
     "With I / we / they the progressive is am / are + V-ing: "
     "'I am learning'."),
    (r"\b(he|she|it)\s+(go|come|eat|like|want|need|play|walk|talk|work|"
     r"live|look|see|know|make|take|give|read|write|drink|buy|sleep|"
     r"help|learn|teach|open|close|start|finish|watch|listen)\b",
     "Third person singular -s", "{0} {th}",
     "With he / she / it the present simple verb takes -s: 'He goes to school'."),
    (r"\b(is|are|am|was|were|be|been|being)\s+agree\b",
     "Wrong word", "agree",
     "'Agree' is a verb: 'I agree with you', not 'I am agree'."),
    (r"\b(have|has|had)\s+(?:\d+|a|an)\s+(year|month|day|week|hour)\b",
     "Duration phrase", "{0} {1} {2} {2}s",
     "'for' goes before the duration: 'for three years'."),
]


def _kw(a: str, b: str, extra=()) -> list[str]:
    out = [f"{a} or {b}", f"difference between {a} and {b}",
           f"{a} vs {b}", f"{a} and {b} difference",
           f"tell me the difference between {a} and {b}"]
    out.extend(extra)
    return out


def main() -> None:
    # ---------------------------------------------------------- distinctions
    topics = []
    for a, b, level, why, pairs in DISTINCTIONS:
        # Normalise every entry to a list of {en, fa} sides. A side may be
        # written as one string carrying its own "\u21b3 ..." translation.
        sides = []
        for item in pairs:
            chunks = list(item) if isinstance(item, (tuple, list)) else [item]
            if len(chunks) == 1 and "\u21b3" in chunks[0]:
                head, _, tail = chunks[0].partition("  \u21b3 ")
                sides.append({"en": head.strip(), "fa": tail.strip()})
            elif len(chunks) == 1:
                sides.append({"en": chunks[0].strip(), "fa": ""})
            else:
                en, fa = chunks[0], chunks[1]
                if "\u21b3" in en:
                    head, _, tail = en.partition("  \u21b3 ")
                    sides.append({"en": head.strip(), "fa": tail.strip()})
                    if fa.strip():
                        sides.append({"en": fa.strip(), "fa": ""})
                else:
                    sides.append({"en": en.strip(),
                                  "fa": fa.replace("\u21b3 ", "").strip()})
        assert sides, a
        topics.append({
            "id": f"{a}_vs_{b}".replace(" ", "_"),
            "level": level,
            "title": {"en": f"{a.capitalize()} / {b}", "fa": f"{a} یا {b}"},
            "keywords": {
                "en": _kw(a, b, [f"{a} and {b}", f"{a} versus {b}",
                                 f"confusion between {a} and {b}"]),
                "fa": [f"\u062a\u0641\u0627\u0648\u062a {a} \u0648 {b}",
                       f"{a} \u06cc\u0627 {b}",
                       f"\u0641\u0631\u0642 {a} \u0648 {b}",
                       f"\u06a9\u062f\u0627\u0645 {a} \u06cc\u0627 {b}"],
            },
            "why": why,
            "sides": sides,
        })

    (ROOT / "distinctions.json").write_text(
        json.dumps({"topics": topics}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  + distinctions.json  {len(topics)} pairs")

    # ---------------------------------------------------------------- idioms
    id_topics = []
    by_kind: dict[str, list] = {}
    for en, fa, kind, meaning, example in IDIOMS:
        by_kind.setdefault(kind, []).append((en, fa, meaning, example))
    for kind, rows in by_kind.items():
        id_topics.append({
            "id": f"idioms_{kind.replace(' ', '_')}",
            "level": "B1" if kind == "informal" else "B2",
            "title": {"en": f"Idioms — {kind}", "fa": f"اصطلاح‌ها — {kind}"},
            "keywords": {
                "en": [f"{kind} idioms", f"english idioms", f"idioms about {kind}",
                       "common idioms", "sayings and idioms"]
                if kind == "idiom" else
                [f"{kind} expressions", "informal english", "common idioms",
                 "sayings and idioms"],
                "fa": ["اصطلاح", "ضرب المثل انگلیسی", "عبارت های انگلیسی",
                       "معنی اصطلاح"],
            },
            "idioms": [{"en": en, "fa": fa, "meaning": meaning, "example": example}
                       for en, fa, meaning, example in rows],
        })
    (ROOT / "idioms.json").write_text(
        json.dumps({"topics": id_topics}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  + idioms.json        {len(IDIOMS)} idioms in {len(id_topics)} banks")

    # ------------------------------------------------------------ corrections
    rows = []
    for pattern, label, fix, why in CORRECTIONS:
        rows.append({"pattern": pattern, "label": label, "fix": fix, "why": why})
    (ROOT / "corrections.json").write_text(
        json.dumps({"rules": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  + corrections.json   {len(rows)} error rules")


if __name__ == "__main__":
    main()