"""A1-A2 pages, part one: simple_present ... word_order."""

P = {
    "simple_present": dict(
        scene=(
            "Every morning Sara leaves the flat at seven. She takes the same bus, "
            "greets the same driver, and buys a coffee on the corner.",
            "هر روز صبح سارا ساعت هفت از خانه بیرون می‌رود. با همان اتوبوس می‌رود، "
            "به همان راننده سلام می‌کند و از سر خیابان قهوهٔ همیشگی را می‌خرد.",
        ),
        pairs=[
            ("هر روز با اتوبوس می‌روم سر کار.",
             "Every day I am going to work by bus.",
             "I go to work by bus every day.",
             "A routine is stated, not watched: the -ing form would say you are "
             "on the bus right now.",
             "عادت را با حال ساده می‌گوییم؛ ing یعنی همین حالا در راهی."),
            ("او انگلیسی بلد است.",
             "She know English.",
             "She knows English.",
             "he, she and it take -s; Persian adds nothing to the verb, so the "
             "ending has to be remembered rather than heard.",
             "فارسی به فعل پایانی اضافه نمی‌کند؛ پس این s را باید به یاد سپرد."),
        ],
        mistakes=[
            ("She have a car.",
             "She has a car.",
             "have is the one irregular verb here: he, she and it take has, and "
             "no amount of logic makes it haves.",
             "have فعل بی‌قاعده است: سوم‌شخص has می‌گیرد، نه haves.",
             "agreement"),
            ("Does she works here?",
             "Does she work here?",
             "the -s has already moved onto does; the main verb goes back to its "
             "base form and cannot carry a second one.",
             "s روی does نشسته؛ فعل اصلی به شکل پایه برمی‌گردد و دو s نمی‌گیرد.",
             "agreement"),
        ],
    ),
    "subject_verb_agreement": dict(
        scene=(
            "The list of names is on the desk. Nobody in the office knows where it "
            "came from, and the manager, together with two assistants, is still "
            "looking for the file.",
            "فهرست اسم‌ها روی میز است. هیچ‌کس در دفتر نمی‌داند از کجا آمده، و مدیر "
            "همراه با دو دستیار هنوز دنبال پرونده می‌گردد.",
        ),
        pairs=[
            ("یکی از دانشجوها اینجا کار می‌کند.",
             "One of the students work here.",
             "One of the students works here.",
             "the subject is one; of the students only describes it, and a phrase "
             "beginning with of never changes the number of the verb.",
             "فاعل «one» است؛ عبارتِ of the students فقط توضیح است و فعل را جمع نمی‌کند."),
            ("خانواده‌ام در تهران زندگی می‌کنند.",
             "My family live in Tehran.",
             "My family lives in Tehran.",
             "American English treats a family as one group. British English "
             "allows either, so pick one and stay with it.",
             "انگلیسی آمریکایی خانواده را یک گروه می‌بیند؛ بریتانیایی هر دو را می‌پذیرد."),
        ],
        mistakes=[
            ("The news are bad.",
             "The news is bad.",
             "news ends in -s but is one uncountable idea, like information and "
             "advice.",
             "news با s تمام می‌شود ولی یک مفهوم غیرقابل‌شمارش است، مثل information.",
             "agreement"),
            ("Everybody are ready.",
             "Everybody is ready.",
             "everybody, everyone and nobody are singular in English, however "
             "many people are standing behind them.",
             "everybody و everybody همیشه مفردند، هر چند نفر هم که پشتشان باشند.",
             "agreement"),
        ],
    ),
    "to_be": dict(
        scene=(
            "It is nine o'clock and the shop is still closed. Sara is outside, "
            "cold, and not very patient.",
            "ساعت نه است و مغازه هنوز بسته است. سارا بیرون است، سردش است و زیاد "
            "صبور نیست.",
        ),
        pairs=[
            ("من بیست‌وپنج ساله‌ام.",
             "I have twenty-five years.",
             "I am twenty-five.",
             "English is its age; it does not have it. The same goes for hungry, "
             "cold, right and wrong.",
             "انگلیسی سن را «است»؛ برای گرسنه و سرد و درست هم همین‌طور."),
            ("او خسته است.",
             "She tired.",
             "She is tired.",
             "Persian's «است» shrinks to a suffix and often disappears in speech; "
             "English never drops the verb.",
             "«است» در فارسی به پسوند تبدیل می‌شود و در گفتار می‌افتد؛ انگلیسی فعل را حذف نمی‌کند."),
        ],
        mistakes=[
            ("I am agree with you.",
             "I agree with you.",
             "agree is already a verb, so adding be makes two verbs and only one "
             "of them can be finite.",
             "agree خودش فعل است؛ آوردن am دو فعل می‌سازد.",
             "double verb"),
            ("My father is work in a bank.",
             "My father works in a bank.",
             "a verb that is not be never takes be in front of it; the tense sits "
             "on works.",
             "فعل غیر از be با am/is/are نمی‌آید؛ زمان روی خودِ فعل است.",
             "double verb"),
        ],
    ),
    "there_is_there_are": dict(
        scene=(
            "There is a small kitchen at the back of the flat. There are two chairs "
            "by the window and no table yet.",
            "یک آشپزخانهٔ کوچک در انتهای خانه هست. دو صندلی کنار پنجره هست و هنوز "
            "میزی نیست.",
        ),
        pairs=[
            ("در خانه‌ام یک گربه هست.",
             "In my house there have a cat.",
             "There is a cat in my house.",
             "existence is said with there is / there are. have belongs to whoever "
             "owns the thing, not to the place it sits in.",
             "وجود را با there is می‌گوییم؛ have مال صاحب چیزی است، نه مکان."),
            ("چند کتاب روی میز است.",
             "There is some books on the table.",
             "There are some books on the table.",
             "the noun after the verb picks the form: books is plural, so are.",
             "اسم بعد از فعل شکل را تعیین می‌کند: books جمع است، پس are."),
        ],
        mistakes=[
            ("There is many people here.",
             "There are many people here.",
             "many is followed by a plural noun, and a plural noun needs are.",
             "بعد از many اسم جمع می‌آید و اسم جمع are می‌گیرد.",
             "agreement"),
            ("It has a cat under the table.",
             "There is a cat under the table.",
             "it has answers who owns it; there is answers whether it exists.",
             "it has مالکیت را می‌گوید؛ there is وجود را.",
             "there is"),
        ],
    ),
    "articles": dict(
        scene=(
            "I saw a cat outside the bakery. The cat was black, and it slept on the "
            "step as if the step belonged to it.",
            "بیرون نانوایی یک گربه دیدم. گربه سیاه بود و طوری روی پله خوابیده بود که "
            "انگار پله مال خودش است.",
        ),
        pairs=[
            ("من معلم هستم.",
             "I am teacher.",
             "I am a teacher.",
             "a job in the singular needs a; Persian simply has no word there, so "
             "the article is the part that gets dropped.",
             "شغل مفرد a می‌خواهد؛ فارسی واژه‌ای در آن جا ندارد، پس حذف می‌شود."),
            ("موسیقی را دوست دارم.",
             "I like the music.",
             "I like music.",
             "a whole category takes no article. the would point at one piece you "
             "and I both have in mind.",
             "کل یک مقوله بی‌حرف است؛ the یعنی همان موسیقیِ مشخص."),
        ],
        mistakes=[
            ("She is an university student.",
             "She is a university student.",
             "the choice follows the sound, not the letter: university opens with "
             "/juː/, a consonant sound.",
             "انتخاب با صدا است نه حرف: university با صامت شروع می‌شود.",
             "a/an sound"),
            ("I go to the school every day.",
             "I go to school every day.",
             "school, work, home and bed drop the when they name the activity "
             "rather than a building.",
             "school و work و home وقتی فعالیت باشند the نمی‌گیرند.",
             "article use"),
        ],
    ),
    "pronouns": dict(
        scene=(
            "Ali and I met at the station. He was late, I was tired, and neither of "
            "us wanted to carry the bags, so we left them in a locker.",
            "من و علی در ایستگاه همدیگر را دیدیم. او دیر رسیده بود، من خسته بودم و "
            "هیچ‌کداممان نمی‌خواستیم ساک‌ها را حمل کنیم، پس آن‌ها را در کمد گذاشتیم.",
        ),
        pairs=[
            ("من و او رفتیم.",
             "Me and him went.",
             "He and I went.",
             "before the verb the subject forms are used; the other person comes "
             "first as a matter of politeness.",
             "قبل از فعل ضمیر فاعلی می‌آید و اول از دیگری نام می‌بریم."),
            ("به من گفت.",
             "He said to I.",
             "He said to me.",
             "after a preposition English always uses the object form.",
             "بعد از حرف اضافه همیشه ضمیر مفعولی می‌آید."),
        ],
        mistakes=[
            ("My brother and me went to the shop.",
             "My brother and I went to the shop.",
             "the pair is the subject, so both halves are in the subject case; "
             "drop the brother and you would never say me went.",
             "ترکیب، فاعل جمله است؛ اگر برادر را حذف کنی هرگز نمی‌گویی me went.",
             "case"),
            ("I like she very much.",
             "I like her very much.",
             "after a verb the object form is used, and Persian's یکسان forms hide "
             "the difference.",
             "بعد از فعل ضمیر مفعولی می‌آید؛ در فارسی شکل‌ها یکسان‌اند."),
        ],
    ),
    "nouns_number": dict(
        scene=(
            "The flat had three pieces of furniture and a lot of advice from the "
            "landlord. By Friday there were two new chairs and no more suggestions.",
            "خانه سه تکه اثاثیه داشت و کلی توصیه از صاحب‌خانه. تا جمعه دو صندلی "
            "تازه داشتیم و دیگر هیچ پیشنهادی نبود.",
        ),
        pairs=[
            ("یک خبر خوب دارم.",
             "I have a good news.",
             "I have good news.",
             "news is one uncountable idea, so it takes no a; when you count it, "
             "it is a piece of news.",
             "news غیرقابل‌شمارش است و a نمی‌گیرد؛ شمارشش با a piece of news است."),
            ("دو تا نان خریدم.",
             "I bought two breads.",
             "I bought two loaves of bread.",
             "bread is measured rather than counted, so the plural goes on the "
             "container word.",
             "نان شمرده نمی‌شود؛ جمع روی واژهٔ واحد می‌نشیند: two loaves."),
        ],
        mistakes=[
            ("She gave me two advices.",
             "She gave me two pieces of advice.",
             "advice has no plural; count it in pieces, bits or words of advice.",
             "advice جمع نمی‌بندد؛ با pieces of advice شمرده می‌شود.",
             "countability"),
            ("The informations are wrong.",
             "The information is wrong.",
             "information is uncountable and singular, so it takes no -s and a "
             "singular verb.",
             "information غیرقابل‌شمارش و مفرد است: نه s، نه are.",
             "countability"),
        ],
    ),
    "word_order": dict(
        scene=(
            "She reads the newspaper on the train and never speaks to anyone. "
            "Yesterday she read it standing up, because the carriage was full.",
            "او در قطار روزنامه می‌خواند و هرگز با کسی حرف نمی‌زند. دیروز ایستاده "
            "خواندش، چون واگن پر بود.",
        ),
        pairs=[
            ("او خیلی خوب انگلیسی صحبت می‌کند.",
             "She very well English speaks.",
             "She speaks English very well.",
             "English fixes subject, verb, object, and the how comes last.",
             "ترتیب انگلیسی ثابت است و قید حالت آخر می‌آید."),
            ("من چای دوست دارم.",
             "I tea like.",
             "I like tea.",
             "the verb cannot wait at the end of the sentence the way Persian's "
             "does; put it second.",
             "فعل مثل فارسی آخر جمله نمی‌ماند؛ جای دومش است."),
        ],
        mistakes=[
            ("She speaks very well English.",
             "She speaks English very well.",
             "the object sits next to its verb and the manner phrase follows it.",
             "مفعول کنار فعل می‌نشیند و عبارت حالت بعد از آن می‌آید.",
             "word order"),
            ("Always he comes late.",
             "He always comes late.",
             "an adverb of frequency sits between the subject and the main verb, "
             "not in front of the subject.",
             "قید تکرار بین فاعل و فعل می‌آید، نه قبل از فاعل.",
             "word order"),
        ],
    ),
}
