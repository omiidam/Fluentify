"""Two further practices for summarising and paraphrasing."""
from reading_src import bi

MORE = {
    "summarize": [
        {
            "title": bi("Ten minutes later, five years of argument",
                        "ده دقیقه بعد، پنج سال بحث"),
            "level": "B2",
            "genre": bi("Education report", "گزارش آموزشی"),
            "paragraphs": [
                "For twenty years, sleep researchers have argued that secondary "
                "schools start too early. The recommendation most often quoted "
                "is 8.30 am, because at that hour most teenagers can have had "
                "eight hours of sleep.",
                "The evidence is stronger than the argument suggests. In one "
                "district that moved its start time from 7.25 to 8.45, average "
                "sleep rose by about an hour, attendance improved, and car "
                "accidents involving teenage drivers fell by 16 per cent over "
                "the first two years.",
                "The obstacles are practical rather than scientific. Buses run "
                "two or three school routes each morning, sport and after-school "
                "jobs are arranged around the old timetable, and parents on "
                "early shifts depend on schools opening early.",
                "Where change has succeeded, it was made slowly: one district "
                "moved its start time by ten minutes a year for five years, and "
                "nobody noticed until the change was complete. The lesson for a "
                "summariser is the same as for a school board - the smallest "
                "true statement carries furthest.",
            ],
            "summary": bi(
                "Starting school later clearly helps teenagers, the obstacles "
                "are timetables rather than evidence, and slow ten-minute steps "
                "get past them.",
                "دیرتر شروع شدن مدرسه آشکارا به نوجوانان کمک می‌کند، موانع جدول "
                "زمانی است نه شواهد، و قدم‌های آرام ده‌دقیقه‌ای از آن‌ها می‌گذرند."),
            "questions": {
                "blanks": [
                    {"sentence": "The most quoted recommended start time is "
                                 "___ am.",
                     "answer": "8.30", "also": ["8:30", "8.30am"],
                     "hint": bi("A time, in the first paragraph.",
                                "یک ساعت، در پاراگراف اول."),
                     "para": 1},
                    {"sentence": "Car accidents among teenage drivers fell by "
                                 "___ per cent.",
                     "answer": "16", "also": ["sixteen"],
                     "hint": bi("A figure, in the second paragraph.",
                                "عددی در پاراگراف دوم."),
                     "para": 2},
                    {"sentence": "One district moved its start by ___ minutes "
                                 "a year.",
                     "answer": "ten", "also": ["10"],
                     "hint": bi("A word, in the last paragraph.",
                                "یک کلمه، در پاراگراف آخر."),
                     "para": 4},
                ],
                "mcq": [
                    {"q": "What is the passage mainly about?",
                     "options": ["Why teenagers need less sleep",
                                 "Evidence for later starts, the practical "
                                 "obstacles, and a way through them",
                                 "How school buses are organised",
                                 "Why parents disagree with researchers"],
                     "answer": 1,
                     "why": bi("One paragraph of evidence, one of obstacles, one "
                               "of the method that worked - and the last "
                               "sentence generalises it.",
                               "یک پاراگراف شواهد، یکی موانع، یکی روشی که جواب "
                               "داد؛ و جملهٔ آخر آن را کلی می‌کند."),
                     "para": 4},
                    {"q": "What do the obstacles have in common?",
                     "options": ["They are scientific disagreements",
                                 "They are timetables and habits, not evidence",
                                 "They affect only rural districts",
                                 "They were solved by the trial"],
                     "answer": 1,
                     "why": bi("'The obstacles are practical rather than "
                               "scientific', and each example is a schedule: "
                               "buses, sport, shifts.",
                               "«موانع عملی‌اند نه علمی»، و هر مثال یک برنامه است: "
                               "اتوبوس، ورزش، شیفت."),
                     "para": 3},
                    {"q": "What does the five-year example show?",
                     "options": ["That change must be announced loudly",
                                 "That small annual steps can pass unnoticed "
                                 "and still arrive",
                                 "That ten minutes is enough on its own",
                                 "That districts avoid the issue"],
                     "answer": 1,
                     "why": bi("Ten minutes a year for five years produced the "
                               "change, and 'nobody noticed until the change "
                               "was complete'.",
                               "ده دقیقه در سال برای پنج سال تغییر را ساخت و "
                               "«هیچ‌کس تا کامل شدن تغییر متوجه نشد»."),
                     "para": 4},
                ],
                "truefalse": [
                    {"statement": "Attendance improved after the start time "
                                  "moved.",
                     "answer": True,
                     "why": bi("'Average sleep rose by about an hour, "
                               "attendance improved.'",
                               "«میانگین خواب حدود یک ساعت بیشتر شد، حضور بهتر "
                               "شد.»"),
                     "para": 2},
                    {"statement": "Districts resisted change because the "
                                  "evidence was weak.",
                     "answer": False,
                     "why": bi("'The obstacles are practical rather than "
                               "scientific.'",
                               "«موانع عملی‌اند نه علمی.»"),
                     "para": 3},
                    {"statement": "The five-year change was completed without "
                                  "much public attention.",
                     "answer": True,
                     "why": bi("'Nobody noticed until the change was complete.'",
                               "«هیچ‌کس تا کامل شدن تغییر متوجه نشد.»"),
                     "para": 4},
                ],
                "essay": [
                    {"prompt": bi("Summarise the passage in 45-70 words: the "
                                  "evidence, the obstacle, the method. Use no "
                                  "sentence from the original.",
                                  "متن را در ۴۵ تا ۷۰ کلمه خلاصه کن: شواهد، مانع، "
                                  "روش. هیچ جمله‌ای از متن اصلی را به کار نبر."),
                     "min_words": 45,
                     "tips": [
                         bi("Three sentences will do: one each.",
                            "سه جمله کافی است: یکی برای هر کدام."),
                         bi("Round the numbers or drop them; the point is the "
                            "pattern.",
                            "عددها را گرد کن یا حذف؛ نکته الگوست."),
                         bi("Check for any four copied words in a row.",
                            "هر چهار کلمهٔ پشت‌سرهمِ کپی‌شده را بررسی کن.")],
                     "model": bi("Teenagers do better when secondary school "
                                 "starts later: one district that delayed the "
                                 "bell by more than an hour saw more sleep, "
                                 "better attendance and fewer young-driver "
                                 "crashes. Resistance comes from bus routes, "
                                 "sport and parents' shifts rather than from "
                                 "disagreeing evidence. The districts that "
                                 "managed it moved the start a few minutes each "
                                 "year, so the change arrived without a fight.",
                                 "نوجوانان وقتی مدرسه دیرتر شروع شود بهتر عمل "
                                 "می‌کنند: در یکی از مناطق که شروع را بیش از یک "
                                 "ساعت عقب انداخت، خواب بیشتر، حضور بهتر و "
                                 "تصادف کمتری میان رانندگان جوان دیده شد. مقاومت "
                                 "از مسیر اتوبوس‌ها، ورزش و شیفت والدین می‌آید، نه "
                                 "از شواهد مخالف. مناطقی که موفق شدند، هر سال چند "
                                 "دقیقه شروع را عقب انداختند تا تغییر بی‌دعوا "
                                 "برسد.")},
                ],
            },
        },
        {
            "title": bi("The fox that is not lost", "روباهی که گم نشده"),
            "level": "B2",
            "genre": bi("Nature feature", "گزارش طبیعت"),
            "paragraphs": [
                "The fox on the bin at two in the morning is not lost. Urban "
                "foxes have lived in British cities since the 1930s, and studies "
                "suggest densities of up to thirty adults per square kilometre "
                "in some suburbs.",
                "The city suits them. Gardens offer shelter, food waste is "
                "reliable, and there are fewer large predators. A fox's "
                "territory in a town is smaller than in the countryside, and "
                "town foxes are often heavier.",
                "Conflict is real but narrower than the headlines imply. Most "
                "complaints concern noise and fouled gardens; attacks on pets "
                "are rare and mostly involve outdoor rabbits. Council advice is "
                "consistent: do not feed them, secure bins, and block the gaps "
                "under sheds.",
                "Culling has been tried repeatedly and has not worked: numbers "
                "return within two years, because the survivors breed earlier. "
                "The measure that does reduce complaints is the dull one - bins "
                "that close.",
            ],
            "summary": bi(
                "Urban foxes are established, mostly a nuisance rather than a "
                "danger, and closing bins works where culling has not.",
                "روباه‌های شهری جا افتاده‌اند، بیشتر مزاحم‌اند تا خطر، و بستن سطل "
                "ها جایی کار می‌کند که کشتار جمعی نکرده."),
            "questions": {
                "blanks": [
                    {"sentence": "Urban foxes have lived in British cities since "
                                 "the ___.",
                     "answer": "1930s", "also": ["1930's"],
                     "hint": bi("A decade, in the first paragraph.",
                                "یک دهه، در پاراگراف اول."),
                     "para": 1},
                    {"sentence": "Densities can reach ___ adults per square "
                                 "kilometre.",
                     "answer": "thirty", "also": ["30"],
                     "hint": bi("A word, near 'per square kilometre'.",
                                "یک کلمه، کنار «per square kilometre»."),
                     "para": 1},
                    {"sentence": "After culling, numbers return within ___ "
                                 "years.",
                     "answer": "two", "also": ["2"],
                     "hint": bi("In the last paragraph.",
                                "در پاراگراف آخر."),
                     "para": 4},
                ],
                "mcq": [
                    {"q": "What is the passage mainly about?",
                     "options": ["How to remove foxes from a city",
                                 "Foxes are settled in towns, the real problem "
                                 "is small, and bins matter more than culling",
                                 "Why foxes are dangerous to pets",
                                 "The diet of the urban fox"],
                     "answer": 1,
                     "why": bi("The passage establishes the population, limits "
                               "the conflict, and ends on the measure that "
                               "works. Culling is mentioned only to dismiss it.",
                               "متن جمعیت را ثابت می‌کند، دامنهٔ تعارض را محدود "
                               "می‌کند و با اقدامی که کار می‌کند تمام می‌شود. "
                               "کشتار جمعی فقط برای رد شدن آمده."),
                     "para": 4},
                    {"q": "Why do foxes do well in towns?",
                     "options": ["Because people feed them deliberately",
                                 "Because gardens, waste and few predators suit "
                                 "them",
                                 "Because winters are warmer",
                                 "Because they have no territories"],
                     "answer": 1,
                     "why": bi("The second paragraph lists shelter, reliable "
                               "food waste and fewer predators; it also warns "
                               "against feeding them.",
                               "پاراگراف دوم پناه، غذای مطمئن و شکارچیان کمتر را "
                               "فهرست می‌کند؛ همان‌جا هم از غذا دادن منع می‌کند."),
                     "para": 2},
                    {"q": "What actually reduces complaints?",
                     "options": ["Culling", "Moving the foxes", "Bins that "
                                 "close", "Feeding them away from houses"],
                     "answer": 2,
                     "why": bi("'The measure that does reduce complaints is the "
                               "dull one - bins that close.'",
                               "«اقدامی که واقعاً شکایت‌ها را کم می‌کند همان کار "
                               "خسته‌کننده است: سطل‌هایی که بسته می‌شوند.»"),
                     "para": 4},
                ],
                "truefalse": [
                    {"statement": "Culling keeps fox numbers down permanently.",
                     "answer": False,
                     "why": bi("Numbers 'return within two years, because the "
                               "survivors breed earlier'.",
                               "تعدادها «در دو سال برمی‌گردند، چون بازماندگان زودتر "
                               "زادآوری می‌کنند»."),
                     "para": 4},
                    {"statement": "Town foxes are often heavier than rural ones.",
                     "answer": True,
                     "why": bi("'Town foxes are often heavier.'",
                               "«روباه‌های شهری معمولاً سنگین‌ترند.»"),
                     "para": 2},
                    {"statement": "Councils advise residents to leave food out.",
                     "answer": False,
                     "why": bi("The advice is 'do not feed them'.",
                               "توصیه «به آن‌ها غذا ندهید» است."),
                     "para": 3},
                ],
                "essay": [
                    {"prompt": bi("Write a 50-70 word summary for someone who "
                                  "has just moved to a city and is worried "
                                  "about foxes. Keep the reassurance, the real "
                                  "problem and the one measure that works.",
                                  "خلاصه‌ای ۵۰ تا ۷۰ کلمه‌ای برای کسی بنویس که تازه "
                                  "به شهر آمده و نگران روباه‌هاست. دلگرمی، مشکل "
                                  "واقعی و تنها اقدام مؤثر را نگه دار."),
                     "min_words": 50,
                     "tips": [
                         bi("Address the reader's fear directly and briefly.",
                            "مستقیم و کوتاه به ترس خواننده بپرداز."),
                         bi("Say how common attacks on pets are, as the text "
                            "does.",
                            "بگو حمله به حیوان خانگی چقدر شایع است، همان‌طور که "
                            "متن می‌گوید."),
                         bi("End with the action, not with the history.",
                            "با اقدام تمام کن، نه با تاریخ.")],
                     "model": bi("Foxes have lived in British cities since the "
                                 "1930s and are now a normal part of them, "
                                 "reaching up to thirty adults per square "
                                 "kilometre in some suburbs. The usual problem "
                                 "is noise and fouled gardens; attacks on pets "
                                 "are rare and mostly involve outdoor rabbits. "
                                 "Do not feed them and keep bins closed - that "
                                 "reduces complaints, while culling has failed "
                                 "wherever it has been tried.",
                                 "روباه‌ها از دههٔ ۱۹۳۰ در شهرهای بریتانیا زندگی "
                                 "می‌کنند و حالا بخش عادی آن‌اند؛ در برخی حومه‌ها "
                                 "تا سی روباه بالغ در هر کیلومتر مربع. مشکل معمول "
                                 "سر و صدا و آلوده شدن باغ‌هاست؛ حمله به حیوان "
                                 "خانگی نادر است و بیشتر دربارهٔ خرگوش‌های بیرونی. "
                                 "به آن‌ها غذا ندهید و سطل‌ها را بسته نگه دارید؛ "
                                 "همین شکایت‌ها را کم می‌کند، در حالی که کشتار جمعی "
                                 "هر جا امتحان شده شکست خورده است.")},
                ],
            },
        },
    ],
}
