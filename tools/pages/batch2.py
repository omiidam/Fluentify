"""A2 pages, part two: wh_questions ... comparatives."""

P = {
    "wh_questions": dict(
        scene=(
            "A new colleague stops Sara in the corridor. «Where does your sister "
            "work?» «How long have you been here?» She answers two questions and "
            "asks him the same ones back.",
            "همکاری تازه سارا را در راهرو نگه می‌دارد. «خواهرت کجا کار می‌کند؟» "
            "«چقدر اینجایی؟» سارا به دو سؤال جواب می‌دهد و همان‌ها را از او می‌پرسد.",
        ),
        pairs=[
            ("تو کجا زندگی می‌کنی؟",
             "Where you live?",
             "Where do you live?",
             "a direct question puts the helper before the subject; without do "
             "the sentence is only half a question.",
             "سؤال مستقیم کمک‌فعل را قبل از فاعل می‌آورد؛ بی do سؤال ناقص است."),
            ("می‌دانی او کجاست؟",
             "Do you know where is he?",
             "Do you know where he is?",
             "inside a longer sentence the question keeps its question word but "
             "drops the inversion: where he is, not where is he.",
             "در سؤال غیرمستقیم فقط کلمهٔ پرسشی می‌ماند و جای فاعل و فعل عوض نمی‌شود."),
        ],
        mistakes=[
            ("Where you are going?",
             "Where are you going?",
             "a question moves be in front of the subject; leaving it in place "
             "makes a statement with a question mark.",
             "در سؤال be قبل از فاعل می‌آید؛ ماندنش در جای خودش جمله را خبری می‌کند.",
             "question form"),
            ("What means this word?",
             "What does this word mean?",
             "what is the object here, so the sentence still needs do and the base "
             "verb after it.",
             "what مفعول است؛ پس do و فعل پایه لازم است.",
             "question form"),
        ],
    ),
    "adjective_order": dict(
        scene=(
            "She came back from the market with a beautiful small Turkish coffee pot "
            "and a pair of worn leather gloves. Both were older than they looked.",
            "از بازار با یک قهوه‌جوش کوچک و زیبای ترکی و یک جفت دستکش چرمی کهنه برگشت. "
            "هر دو قدیمی‌تر از آن بودند که به نظر می‌رسیدند.",
        ),
        pairs=[
            ("یک کیف چرمی قهوه‌ای بزرگ خریدم.",
             "I bought a big brown leather bag.",
             "I bought a big brown leather bag.",
             "size, then colour, then material. Persian often puts the material "
             "first, which is the order English saves for last.",
             "اندازه، بعد رنگ، بعد جنس؛ فارسی جنس را جلو می‌آورد و انگلیسی آخر."),
        ],
        mistakes=[
            ("a leather big brown bag",
             "a big brown leather bag",
             "material is the closest adjective to the noun; size is the furthest, "
             "because it describes the whole thing.",
             "جنس نزدیک‌ترین صفت به اسم است و اندازه دورترین.",
             "adjective order"),
            ("a beautiful wooden old table",
             "a beautiful old wooden table",
             "opinion, then age, then material — the chain only sounds right in "
             "this direction.",
             "نظر، بعد سن، بعد جنس؛ زنجیره فقط در این ترتیب درست می‌آید.",
             "adjective order"),
        ],
    ),
    "simple_past": dict(
        scene=(
            "Last week I visited my grandmother in Shiraz. We walked to the bazaar, "
            "drank tea with her neighbour, and I forgot my umbrella on the bus.",
            "هفتهٔ پیش به دیدن مادربزرگم در شیراز رفتم. تا بازار پیاده رفتیم، با "
            "همسایه‌اش چای خوردیم و چترم را در اتوبوس جا گذاشتم.",
        ),
        pairs=[
            ("دیروز نرفتم سر کار.",
             "Yesterday I not went to work.",
             "Yesterday I didn't go to work.",
             "the past is already carried by did, so the main verb stays in its "
             "base form and cannot take -ed as well.",
             "زمان گذشته روی did است؛ فعل اصلی پایه می‌ماند و ed نمی‌گیرد."),
            ("کجا رفتی؟",
             "Where you went?",
             "Where did you go?",
             "a past question is did plus the base verb, not the past form twice.",
             "سؤال گذشته did + فعل پایه است، نه فعل گذشته دوباره."),
        ],
        mistakes=[
            ("I didn't went to the party.",
             "I didn't go to the party.",
             "did already makes it past; went would mark the past a second time.",
             "did خودش گذشته را می‌سازد؛ went دوباره آن را علامت می‌زند.",
             "past form"),
            ("She goed to the shop.",
             "She went to the shop.",
             "go is irregular: its past is went, and -ed is only for regular verbs.",
             "go بی‌قاعده است و گذشته‌اش went است.",
             "past form"),
        ],
    ),
    "simple_future": dict(
        scene=(
            "The phone rings at eleven at night. «I will call you back in five "
            "minutes,» she says, and she does.",
            "ساعت یازده شب تلفن زنگ می‌خورد. «پنج دقیقهٔ دیگر خودم زنگ می‌زنم»، "
            "می‌گوید و می‌زند.",
        ),
        pairs=[
            ("فردا می‌آمدم دنبالت.",
             "Tomorrow I will come after you.",
             "Tomorrow I'll pick you up.",
             "will + come says you will travel toward someone; picking someone up "
             "is the phrase for collecting them.",
             "will come یعنی به سمتت می‌آیم؛ برای سوار کردن کسی از pick up استفاده می‌شود."),
            ("داره بارون می‌گیره، چتر برمی‌دارم.",
             "It is raining, I will take an umbrella.",
             "It's raining — I'll take an umbrella.",
             "a decision made at the moment of speaking uses will, and that is "
             "exactly what this is.",
             "تصمیمِ همین لحظه با will گفته می‌شود."),
        ],
        mistakes=[
            ("I will call you when I will arrive.",
             "I will call you when I arrive.",
             "after when, if, before and as soon as the future is already "
             "understood, so the present is used.",
             "بعد از when و if و before زمان آینده با حال گفته می‌شود.",
             "future in time clause"),
            ("She will can help us.",
             "She will be able to help us.",
             "two modals cannot stand together; will needs a real verb, and can "
             "has no future of its own.",
             "دو فعل کمکی پشت هم نمی‌آیند؛ can آینده ندارد."),
        ],
    ),
    "present_progressive": dict(
        scene=(
            "The office is quiet. Sara is writing an email, the printer is making a "
            "small unhappy noise, and nobody is answering the phone.",
            "دفتر ساکت است. سارا ایمیل می‌نویسد، پرینتر صدای کوچک و ناراضی درمی‌آورد "
            "و هیچ‌کس تلفن را جواب نمی‌دهد.",
        ),
        pairs=[
            ("حالا دارم شام می‌پزم.",
             "Now I cook dinner.",
             "I'm cooking dinner now.",
             "an action in progress at this second takes be + -ing; the simple "
             "present would describe a habit.",
             "کاری که همین لحظه در جریان است be + ing می‌خواهد."),
            ("دارم می‌فهمم چه می‌گویی.",
             "I am understanding what you say.",
             "I understand what you say.",
             "understand is a state, and states do not take -ing in English even "
             "though Persian can put them in the progressive.",
             "understand حالت است و ing نمی‌گیرد، هرچند فارسی می‌تواند."),
        ],
        mistakes=[
            ("I am knowing the answer.",
             "I know the answer.",
             "know, want, like, believe and belong are states: they sit in the "
             "simple present.",
             "know و want و like حالت‌اند و در حال ساده می‌آیند.",
             "stative verb"),
            ("She is work now.",
             "She is working now.",
             "the -ing is not optional: be needs a participle after it.",
             "ing اختیاری نیست؛ be بعد از خودش اسم فاعل می‌خواهد.",
             "progressive form"),
        ],
    ),
    "past_progressive": dict(
        scene=(
            "I was cooking dinner at seven when the lights went out. The neighbours "
            "were watching the same match, and the whole street groaned at once.",
            "ساعت هفت داشتم شام می‌پختم که برق رفت. همسایه‌ها هم همان مسابقه را "
            "تماشا می‌کردند و کل خیابان یک‌باره آه کشید.",
        ),
        pairs=[
            ("وقتی رسیدم، داشت غذا می‌خورد.",
             "When I arrived, he ate.",
             "When I arrived, he was eating.",
             "the longer action in the background takes was + -ing; the short one "
             "uses the simple past.",
             "کار طولانی‌تر در پس‌زمینه was + ing می‌گیرد و کار کوتاه گذشتهٔ ساده."),
        ],
        mistakes=[
            ("I was knowing him in 2015.",
             "I knew him in 2015.",
             "know is a state, so it has no progressive form in any tense.",
             "know حالت است و در هیچ زمانی استمراری نمی‌شود.",
             "stative verb"),
            ("While I was cook, the phone rang.",
             "While I was cooking, the phone rang.",
             "after was the verb needs -ing; was cook is two verbs with no link.",
             "بعد از was فعل ing می‌گیرد؛ was cook دو فعل بی‌ربط است.",
             "progressive form"),
        ],
    ),
    "modals": dict(
        scene=(
            "At the airport the clerk says she can take one bag, must weigh the "
            "other, and should have checked in earlier.",
            "در فرودگاه کارمند می‌گوید فقط یک ساک می‌تواند ببرد، باید دیگری را وزن "
            "کند و بهتر بود زودتر چک‌این می‌کرد.",
        ),
        pairs=[
            ("باید بروم.",
             "I must to go.",
             "I must go.",
             "a modal is followed by the bare verb: no to, no -s, no -ed.",
             "بعد از فعل کمکی فعل بی‌to و بی‌پسوند می‌آید."),
            ("می‌توانی انگلیسی حرف بزنی؟",
             "Can you to speak English?",
             "Can you speak English?",
             "the to belongs to infinitives like want to, not to modals.",
             "to مال مصدرهایی مثل want to است، نه فعل‌های کمکی."),
        ],
        mistakes=[
            ("She cans swim.",
             "She can swim.",
             "modals never take -s; the same form serves every person.",
             "فعل کمکی s نمی‌گیرد و برای همهٔ شخص‌ها یکسان است.",
             "modal form"),
            ("You must to wear a seatbelt.",
             "You must wear a seatbelt.",
             "must is followed by the base verb with no to in between.",
             "بعد از must فعل بی‌to می‌آید.",
             "modal form"),
        ],
    ),
    "comparatives": dict(
        scene=(
            "The new flat is smaller than the old one but much brighter. The rent is "
            "higher, the kitchen is worse, and the neighbours are the friendliest we "
            "have had.",
            "خانهٔ تازه کوچک‌تر از قبلی است ولی خیلی روشن‌تر. اجاره بالاتر است، آشپزخانه "
            "بدتر است و همسایه‌ها با محبت‌ترین همسایه‌های عمرمان‌اند.",
        ),
        pairs=[
            ("او از من بزرگ‌تر است.",
             "He is more big than me.",
             "He is bigger than him.",
             "a one-syllable adjective takes -er, never more; more big is the "
             "Persian comparison written in English words.",
             "صفت یک‌هجایی er می‌گیرد، نه more؛ more big ترجمهٔ واژه‌به‌واژهٔ فارسی است."),
            ("این یکی بهتر است.",
             "This one is more better.",
             "This one is better.",
             "better is already comparative; more would compare it twice.",
             "better خودش تفضیلی است؛ more آن را دو بار تفضیلی می‌کند."),
        ],
        mistakes=[
            ("She is more taller than her sister.",
             "She is taller than her sister.",
             "taller already carries the comparison; more and -er cannot both be "
             "there.",
             "taller خودش تفضیلی است؛ more و er با هم نمی‌آیند.",
             "comparative form"),
            ("This is the most easiest lesson.",
             "This is the easiest lesson.",
             "easiest is already superlative, so most has nothing to add.",
             "easiest خودش عالی است و most لازم ندارد.",
             "comparative form"),
        ],
    ),
}
