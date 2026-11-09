#!/usr/bin/env python3
"""C2, units 7 and 8: style as choice, and making an argument land."""

from course_kit import (dialogue, gap, lesson, listen, mcq, passage, say,
                       unit, write)

U7 = unit(
    "c2-u7",
    ("Style is a choice", "سبک یک انتخاب است"),
    ("Control emphasis through word order, use idiom without leaning on it, "
     "and present under questioning.",
     "تأکید را با ترتیب واژه‌ها کنترل کن، از اصطلاح تکیه‌گاه نساز و زیر "
     "پرسش ارائه بده."),
    [
        lesson(
            "c2-u7-l1", "grammar",
            ("Fronting, clefts and negative inversion",
             "جابه‌جایی به آغاز، جمله‌های شکافته و وارونگی منفی"),
            ("Move the part of the sentence you want remembered, and know what "
             "each move costs.",
             "بخشی از جمله را که می‌خواهی به یاد بماند جابه‌جا کن و بدان هر "
             "جابه‌جایی چه هزینه‌ای دارد."),
            [
                ("English puts new and important information late. Fronting "
                 "breaks that contract deliberately: 'That argument I have "
                 "heard before' is more dismissive than 'I have heard that "
                 "argument before', because the reader meets the dismissed "
                 "thing first.",
                 "انگلیسی اطلاعات تازه و مهم را در پایان می‌گذارد. جابه‌جایی "
                 "به آغاز این قرارداد را آگاهانه می‌شکند: «That argument I "
                 "have heard before» تحقیرآمیزتر از «I have heard that "
                 "argument before» است، چون خواننده اول با چیزِ رد‌شده روبه‌رو "
                 "می‌شود."),
                ("Clefts split one idea into two clauses to give it weight: "
                 "'What matters is the timing' and 'It was the timing that "
                 "decided it'. The first is a definition, the second a "
                 "correction. Negative inversion does the same work in formal "
                 "prose: 'Not only did the trial fail, it was never "
                 "completed.' The inversion is the emphasis; there is no need "
                 "to add an adverb as well.",
                 "جمله‌های شکافته یک ایده را به دو بند می‌شکنند تا وزن بگیرد: "
                 "«What matters is the timing» و «It was the timing that "
                 "decided it». اولی تعریف است و دومی تصحیح. وارونگی منفی همین "
                 "کار را در نثر رسمی می‌کند: «Not only did the trial fail, it "
                 "was never completed.» وارونگی خودش تأکید است و نیازی به قید "
                 "افزوده نیست."),
                ("The cost is naturalness. One marked structure per paragraph "
                 "reads as control; three read as a speech. And fronting an "
                 "object in speech usually sounds defensive, which is why it "
                 "belongs to argument rather than description.",
                 "هزینه‌اش طبیعی بودن است. یک ساخت نشان‌دار در هر بند مثل تسلط "
                 "خوانده می‌شود و سه تا مثل سخنرانی. جابه‌جایی مفعول در گفتار "
                 "معمولاً دفاعی به گوش می‌رسد و به همین دلیل به استدلال تعلق "
                 "دارد نه به توصیف."),
            ],
            [
                ("What the report does not say is more telling than what it "
                 "does.", "آنچه گزارش نمی‌گوید گویاتر از آن است که می‌گوید."),
                ("It was the second reviewer who caught the error.",
                 "بازبین دوم بود که خطا را گرفت."),
                ("Rarely has a committee reached a decision so quickly.",
                 "به‌ندرت کمیته‌ای این‌قدر سریع به تصمیم رسیده است."),
                ("Such delays we can no longer afford.",
                 "چنین تأخیرهایی را دیگر نمی‌توانیم تحمل کنیم."),
            ],
            [
                mcq("A cleft sentence is used to ___.", "جملهٔ شکافته برای ___ "
                    "به کار می‌رود.",
                    ["shorten the sentence", "give one element weight",
                     "avoid the passive", "add a question"], 1,
                    "It splits one idea so one part carries the stress.",
                    "یک ایده را می‌شکند تا یک بخش تنش را حمل کند."),
                mcq("'Not only did the trial fail' is emphatic because ___.",
                    "«Not only did the trial fail» تأکیدی است چون ___.",
                    ["it is passive", "the auxiliary is inverted",
                     "it is short", "it uses a modal"], 1,
                    "Negative fronting forces inversion of auxiliary and "
                    "subject.", "آغازِ منفی وارونگی کمکی و نهاد را الزام "
                    "می‌کند."),
            ],
            [
                mcq("Which sentence corrects rather than defines?",
                    "کدام جمله تصحیح می‌کند و نه تعریف؟",
                    ["What matters is the timing.", "It was the timing that "
                     "decided it.", "The timing matters.", "Timing is "
                     "important."], 1,
                    "'It was X that' presupposes a wrong alternative.",
                    "«It was X that» وجود گزینهٔ نادرست را پیش‌فرض می‌گیرد."),
                gap("Rarely ___ a review been so blunt.", ["has"],
                    "Negative fronting inverts auxiliary and subject.",
                    "آغازِ منفی کمکی و نهاد را وارون می‌کند.", "one word"),
                mcq("Fronting an object in conversation usually sounds ___.",
                    "جابه‌جایی مفعول به آغاز در گفت‌وگو معمولاً ___ به گوش "
                    "می‌رسد.", ["neutral", "defensive", "poetic", "formal"], 1,
                    "It answers an accusation the other person has not made.",
                    "به اتهامی پاسخ می‌دهد که طرف مقابل نگفته است."),
                gap("Three marked structures in one paragraph read like a "
                     "___.", ["speech"], "One reads as control; three as "
                    "performance.", "یکی تسلط است و سه تا اجرا.", "one word"),
            ],
        ),
        lesson(
            "c2-u7-l2", "vocabulary",
            ("Idioms that survive a second look",
             "اصطلاحاتی که بازبینی را تحمل می‌کنند"),
            ("Use spoken idioms where they fit and replace them where they "
             "would mislead.",
             "اصطلاحات گفتاری را جایی که می‌نشینند به کار ببر و جایی که گمراه "
             "می‌کنند جای‌گزین کن."),
            [
                ("An idiom is a fixed phrase whose meaning is not built from "
                 "its parts: to move the goalposts, to be on the back foot, to "
                 "read the room, to call it a day, to hedge your bets. Used "
                 "once, they signal fluency and shared ground. Used three "
                 "times, they signal that the speaker has no exact word.",
                 "اصطلاح عبارتی ثابت است که معنایش از اجزایش ساخته نمی‌شود: to "
                 "move the goalposts، to be on the back foot، to read the "
                 "room، to call it a day، to hedge your bets. یک بار که به "
                 "کار روند نشانهٔ تسلط و زمینهٔ مشترک‌اند و سه بار که بشوند "
                 "نشانهٔ نبودِ واژهٔ دقیق."),
                ("Many idioms carry a register and a politics. 'Moved the "
                 "goalposts' accuses; 'revised the criteria' describes. In a "
                 "report, the second is safer and the first is an argument "
                 "wearing the clothes of description — which is fine if you "
                 "mean to argue.",
                 "بسیاری از اصطلاحات ثبت و سیاستی با خود دارند. «moved the "
                 "goalposts» متهم می‌کند و «revised the criteria» توصیف. در "
                 "گزارش دومی امن‌تر است و اولی استدلالی است در لباس توصیف — که "
                 "اگر قصد استدلال داری اشکالی ندارد."),
                ("The test for an idiom is whether you could defend it under "
                 "questioning. If someone asked 'what exactly do you mean by "
                 "reading the room?', could you answer in plain words? If not, "
                 "you are using the idiom to avoid the claim.",
                 "آزمون اصطلاح این است که آیا زیر پرسش می‌توانی از آن دفاع "
                 "کنی. اگر کسی بپرسد «reading the room یعنی دقیقاً چه؟» می‌توانی "
                 "با واژه‌های ساده پاسخ دهی؟ اگر نه، اصطلاح را برای پرهیز از "
                 "ادعا به کار می‌بری."),
            ],
            [
                ("They moved the goalposts twice before the deadline.",
                 "دو بار پیش از مهلت شرایط را عوض کردند."),
                ("After the review we were on the back foot for a month.",
                 "بعد از بازبینی یک ماه در موضع دفاعی بودیم."),
                ("She read the room and dropped the proposal.",
                 "فضا را خواند و پیشنهاد را پس گرفت."),
                ("Let us call it a day and start fresh on Monday.",
                 "بگذاریم برای امروز تمام شود و دوشنبه از نو شروع کنیم."),
            ],
            [
                mcq("'Moved the goalposts' differs from 'revised the "
                    "criteria' in that it ___.", "«moved the goalposts» با "
                    "«revised the criteria» تفاوت دارد چون ___.",
                    ["is more formal", "carries an accusation", "is longer",
                     "is about sport"], 1,
                    "The idiom judges; the plain phrase describes.",
                    "اصطلاح داوری می‌کند و عبارت ساده توصیف."),
                mcq("'Read the room' means ___.", "«read the room» یعنی ___.",
                    ["read aloud", "judge the mood of those present",
                     "leave the meeting", "check the seating"], 1,
                    "It is about sensing the audience, not the venue.",
                    "دربارهٔ حس کردن مخاطب است، نه مکان."),
            ],
            [
                mcq("Which idiom would be risky in a formal report?",
                    "کدام اصطلاح در گزارش رسمی پرخطر است؟",
                    ["on the back foot", "a revised timetable",
                     "an interim finding", "a provisional figure"], 0,
                    "It describes a defensive position informally and "
                    "judgementally.", "موضع دفاعی را غیررسمی و داوری‌گرانه "
                    "توصیف می‌کند."),
                gap("To avoid committing, the board decided to ___ its bets.",
                    ["hedge"], "The fixed phrase takes 'hedge'.",
                    "این عبارت ثابت «hedge» می‌گیرد.", "one word"),
                mcq("The test of an idiom under questioning is whether ___.",
                    "آزمون اصطلاح زیر پرسش این است که ___.",
                    ["it is short", "you can restate it in plain words",
                     "it is recent", "it sounds native"], 1,
                    "If it cannot be unpacked, it is hiding a claim.",
                    "اگر بازش کرد، ادعایی را پنهان می‌کند."),
                gap("Three idioms in one paragraph make a speaker sound "
                     "___ rather than fluent.", ["vague"],
                    "Density turns fluency into imprecision.",
                    "تراکم، تسلط را به ابهام بدل می‌کند.", "one word"),
            ],
        ),
        lesson(
            "c2-u7-l3", "reading",
            ("The essay that argues with its own title",
             "مقالاتی که با عنوان خودش بحث می‌کند"),
            ("Read a cultural essay for its thesis, and separate the thesis "
             "from the examples that decorate it.",
             "مقاله‌ای فرهنگی را برای تز آن بخوان و تز را از مثال‌های تزیینی "
             "جدا کن."),
            [
                ("In a cultural essay the thesis often arrives late and "
                 "sideways, inside an anecdote. The first paragraph sets a "
                 "scene, not a claim, and the claim appears where the writer "
                 "stops describing and starts generalising — usually with "
                 "'what this suggests is'.",
                 "در مقالهٔ فرهنگی تز اغلب دیر و کج می‌آید، درون حکایتی. بند "
                 "اول صحنه می‌سازد نه ادعا، و ادعا جایی پیدا می‌شود که نویسنده "
                 "توصیف را رها و تعمیم را آغاز می‌کند — معمولاً با «what this "
                 "suggests is»."),
                ("Distinguish the examples that carry the argument from the "
                 "ones that set the mood. A test: remove the paragraph. If the "
                 "thesis survives, it was decoration; if it collapses, it was "
                 "evidence.",
                 "مثال‌هایی را که استدلال را حمل می‌کنند از آن‌ها که فضا "
                 "می‌سازند جدا کن. آزمونش: بند را بردار. اگر تز بماند تزیین "
                 "بود و اگر فرو بریزد شاهد."),
            ],
            [
                ("Find the sentence that generalises; that is usually the "
                 "thesis.", "جمله‌ای را بیاب که تعمیم می‌دهد؛ آن معمولاً تز "
                 "است."),
                ("An essay can argue against its own title — check whether the "
                 "title is a question the text answers differently.",
                 "مقاله می‌تواند بر ضد عنوان خودش استدلال کند — بررسی کن آیا "
                 "عنوان پرسشی است که متن جور دیگری پاسخ می‌دهد."),
                ("Note who is quoted and what they are used for.",
                 "یادداشت کن از چه کسی نقل شده و برای چه کاری."),
            ],
            [
                mcq("The essay's thesis is that ___.", "تز مقاله این است که "
                    "___.",
                    ["translation is impossible", "a shared language is "
                     "built from shared mistakes", "English is declining",
                     "dictionaries are unreliable"], 1,
                    "The claim emerges from the mistranslation anecdote.",
                    "ادعا از حکایت ترجمهٔ نادرست بیرون می‌آید."),
                mcq("The anecdote about the menu functions as ___.",
                    "حکایت منو ___ عمل می‌کند.",
                    ["decoration", "evidence for the thesis", "a counter-"
                     "argument", "an aside"], 1,
                    "Remove it and the thesis has nothing to stand on.",
                    "آن را بردار و تز چیزی برای ایستادن ندارد."),
            ],
            [
                mcq("Which sentence is the generalising move?",
                    "کدام جمله حرکت تعمیم‌دهنده است؟",
                    ["The menu was printed in three languages.",
                     "What this suggests is that understanding is a "
                     "negotiation, not a transfer.",
                     "I ordered the soup.", "The waiter laughed."], 1,
                    "'What this suggests is' marks the claim.",
                    "«What this suggests is» ادعا را نشانه‌گذاری می‌کند."),
                mcq("The title's question is answered ___.", "به پرسش عنوان "
                    "___ پاسخ داده می‌شود.",
                    ["with a plain yes", "by redefining the terms of the "
                     "question", "by ignoring it", "with statistics"], 1,
                    "The essay rejects the question's assumption.",
                    "مقاله پیش‌فرض پرسش را رد می‌کند."),
                mcq("The quoted translator is used to ___.", "مترجم نقل‌شده "
                    "برای ___ به کار می‌رود.",
                    ["add authority to a claim the writer already made",
                     "introduce a new topic", "contradict the writer",
                     "provide statistics"], 0,
                    "Quotation here decorates a settled argument.",
                    "نقل اینجا استدلالی تثبیت‌شده را تزیین می‌کند."),
            ],
            passage=passage(
                ("A language we can only half share",
                 "زبانی که فقط نیمه شریکش هستیم"),
                ("The menu in the restaurant where I learned most of my "
                 "Italian offered 'mixed grilled fish' in three languages, and "
                 "in none of them did it mean quite the same thing. The English "
                 "suggested a platter. The Italian suggested whatever the boat "
                 "had brought. The third, which I could not identify, "
                 "suggested nothing at all and was probably the most accurate. "
                 "I ordered it, and the waiter laughed — not at my accent, "
                 "which is genuinely funny, but at the menu, which he had been "
                 "meaning to fix for years.\n\n"
                 "For a long time I thought of that afternoon as an anecdote "
                 "about translation: the impossibility of carrying a meaning "
                 "whole from one language into another. What this suggests, "
                 "though, is something less tidy. He and I did not share a "
                 "language. We shared a menu, a joke about the menu, and a "
                 "willingness to be wrong in public. Understanding arrived "
                 "before accuracy did, and it arrived because both of us "
                 "treated the gap as something to work on rather than "
                 "something to be embarrassed by.\n\n"
                 "This is why I distrust the phrase 'a shared language', which "
                 "appears in every policy document I read about integration. "
                 "There is no such thing, if by shared we mean identical. "
                 "There is only the ongoing, slightly ridiculous work of "
                 "repairing misunderstandings — pointing at the fish, laughing "
                 "at the menu, agreeing to order it anyway. The work is not a "
                 "stage on the way to fluency. It is what fluency is.",
                 "منو در رستورانی که بیشتر ایتالیایی‌ام را آنجا یاد گرفتم «ماهی "
                 "کبابی مخلوط» را به سه زبان پیشنهاد می‌کرد و در هیچ‌کدام "
                 "دقیقاً یک معنا نداشت. انگلیسی بشقابی ترکیبی را به ذهن "
                 "می‌آورد. ایتالیایی هرچه قایق آورده بود. سومی، که نشناختمش، "
                 "هیچ چیزی را به ذهن نمی‌آورد و احتمالاً دقیق‌ترین بود. سفارشش "
                 "دادم و پیشخدمت خندید — نه به لهجه‌ام که واقعاً خنده‌دار است، "
                 "بلکه به منو که سال‌ها بود می‌خواست درستش کند.\n\n"
                 "زمانی درازی آن بعدازظهر را حکایتی دربارهٔ ترجمه می‌دانستم: "
                 "ناممکن بودن انتقال کامل معنا از زبانی به زبان دیگر. اما "
                 "آنچه این حکایت پیشنهاد می‌کند مرتب‌تر از این نیست. او و من "
                 "زبان مشترکی نداشتیم. منو، شوخی‌ای دربارهٔ منو و آمادگی برای "
                 "اینکه در جمع اشتباه کنیم را شریک بودیم. فهم پیش از دقت "
                 "رسید و رسید چون هر دو شکاف را چیزی برای کار کردن می‌دانستیم، "
                 "نه چیزی برای خجالت کشیدن.\n\n"
                 "به همین دلیل به عبارت «زبان مشترک» که در هر سند سیاستی "
                 "دربارهٔ ادغام می‌خوانم بی‌اعتمادم. چنین چیزی وجود ندارد، اگر "
                 "از مشترک معنای یکسان را بخواهیم. تنها کار مداوم و کمی "
                 "مسخرهٔ ترمیم سوءتفاهم‌ها هست — اشاره به ماهی، خندیدن به منو "
                 "و توافق بر اینکه به‌هرحال سفارشش دهیم. این کار مرحله‌ای در راه "
                 "روانی نیست؛ خودِ روانی است."),
            ),
        ),
        lesson(
            "c2-u7-l4", "speaking",
            ("Presenting, then surviving the questions",
             "ارائه دادن و بعد از پرسش‌ها جان به‌در بردن"),
            ("Signpost a short presentation and handle a question you did not "
             "expect.",
             "ارائه‌ای کوتاه را نشانه‌گذاری کن و به پرسشی که انتظارش را نداشتی "
             "پاسخ بده."),
            [
                ("A presentation is heard once. Signposting is not decoration "
                 "but navigation: 'three points', 'the part that matters', "
                 "'to come back to your question'. A listener who knows where "
                 "they are can disagree with you precisely, which is the point "
                 "of presenting at all.",
                 "ارائه یک بار شنیده می‌شود. نشانه‌گذاری تزیین نیست، ناوبری "
                 "است: «three points»، «the part that matters»، «to come back "
                 "to your question». شنونده‌ای که بداند کجاست می‌تواند دقیق "
                 "مخالفت کند و هدف ارائه همین است."),
                ("Unexpected questions are handled in three moves: buy time "
                 "honestly ('that is not something I have looked at'), "
                 "restate the question in your own words to check it, and "
                 "commit to a next step. Never invent a number; an audience "
                 "forgives ignorance and does not forgive invention.",
                 "پرسش‌های غافلگیرکننده با سه حرکت اداره می‌شوند: صادقانه زمان "
                 "خریدن («that is not something I have looked at»)، بازگویی "
                 "پرسش با واژه‌های خودت برای بررسی، و تعهد به گام بعدی. هرگز "
                 "عدد نساز؛ مخاطب ناآگاهی را می‌بخشد و ساختن را نه."),
            ],
            [
                ("I will make three points, and the third is the one I would "
                 "like to argue about.", "سه نکته می‌گویم و سومی همان است که "
                 "دوست دارم دربارهٔ آن بحث کنیم."),
                ("That is not something I have looked at, and I will find out "
                 "and send it to you.", "این را بررسی نکرده‌ام و پیدایش "
                 "می‌کنم و برایتان می‌فرستم."),
                ("If I understand you, you are asking whether the effect "
                 "survives a second year.", "اگر درست فهمیده باشم، می‌پرسید "
                 "آیا اثر سال دوم هم می‌ماند."),
                ("Let me come back to that at the end, because it changes my "
                 "second point.", "بگذار در پایان به آن برگردم، چون نکتهٔ دومم "
                 "را عوض می‌کند."),
            ],
            [
                mcq("Signposting helps an audience to ___.", "نشانه‌گذاری به "
                    "مخاطب کمک می‌کند ___.",
                    ["remember your name", "locate themselves in the argument",
                     "agree with you", "take notes faster"], 1,
                    "Orientation is what allows precise disagreement.",
                    "جهت‌یابی همان چیزی است که مخالفت دقیق را ممکن می‌کند."),
                mcq("The worst response to an unexpected question is to ___.",
                    "بدترین پاسخ به پرسش غافلگیرکننده ___ است.",
                    ["admit you do not know", "invent a figure",
                     "restate the question", "promise a follow-up"], 1,
                    "Invention is the one error an audience does not forgive.",
                    "ساختن تنها خطایی است که مخاطب نمی‌بخشد."),
            ],
            [
                say("I will keep this to ten minutes and three points, and I "
                    "will leave time for the questions I cannot answer.",
                    "این را در ده دقیقه و سه نکته نگه می‌دارم و برای پرسش‌هایی "
                    "که نمی‌توانم پاسخ دهم وقت می‌گذارم."),
                say("If I understand you, the question is whether the pilot "
                    "would survive a second year. I do not know, and here is "
                    "how we would find out.", "اگر درست فهمیده باشم، پرسش این "
                    "است که آیا آزمایش سال دوم را دوام می‌آورد. نمی‌دانم و "
                    "این‌گونه می‌فهمیم."),
                say("That is a fair challenge to my second point, and it is "
                    "the reason I put a condition on the recommendation.",
                    "این چالش منصفانه‌ای با نکتهٔ دوم من است و همان دلیلی است که "
                    "بر توصیه شرط گذاشتم."),
                say("I would rather say I do not have that figure than give "
                    "you one I cannot defend.", "ترجیح می‌دهم بگویم آن عدد را "
                    "ندارم تا عددی بدهم که از آن دفاع نمی‌توانم."),
            ],
            dialogue=dialogue([
                ("Chair", "Two minutes left. What do you want us to do?",
                 "دو دقیقه مانده. چه می‌خواهید ما بکنیم؟"),
                ("You", "Publish the pilot figures, including the longest "
                 "wait, and let the second site run for a year.",
                 "ارقام آزمایش را منتشر کنید، از جمله طولانی‌ترین انتظار، و "
                 "بگذارید سایت دوم یک سال اجرا شود."),
                ("Chair", "And if the second site fails?", "و اگر سایت دوم "
                 "شکست بخورد؟"),
                ("You", "Then we will have learned that the effect depends on "
                 "the site, which is worth knowing before a national roll-out.",
                 "آن وقت می‌فهمیم که اثر به سایت وابسته است، و این پیش از اجرای "
                 "سراسری ارزش دانستن دارد."),
            ]),
        ),
    ],
)

U8 = unit(
    "c2-u8",
    ("Making it land", "کاری که بنشیند"),
    ("Use parallelism and antithesis with restraint, keep confusables apart, "
     "and review an argument rather than a book.",
     "توازی و تقابل را با خویشتن‌داری به کار ببر، واژه‌های اشتباه‌گرفته‌شدنی "
     "را جدا نگه دار و به‌جای کتاب، استدلال را نقد کن."),
    [
        lesson(
            "c2-u8-l1", "grammar",
            ("Parallelism, antithesis and the cost of ornament",
             "توازی، تقابل و هزینهٔ آرایه"),
            ("Balance two clauses so that the balance means something, and "
             "know when to stop.",
             "دو بند را چنان متوازن کن که توازن معنایی داشته باشد و بدان کجا "
             "باید ایستاد."),
            [
                ("Parallelism is grammatical symmetry: 'to publish the "
                 "figures, to name the sites, to accept the criticism'. It "
                 "signals that the items belong to one list and one standard. "
                 "Break the symmetry and the reader assumes a difference in "
                 "kind: 'to publish the figures, to name the sites, and "
                 "accepting criticism' makes the third item feel like an "
                 "afterthought.",
                 "توازی تقارن دستوری است: «to publish the figures, to name the "
                 "sites, to accept the criticism». نشان می‌دهد که اقلام به یک "
                 "فهرست و یک معیار تعلق دارند. تقارن را بشکن و خواننده تفاوت "
                 "در نوع را فرض می‌کند: «to publish the figures, to name the "
                 "sites, and accepting criticism» سومین قلم را پس‌اندیشه "
                 "می‌سازد."),
                ("Antithesis sets two halves against each other with matching "
                 "shape: 'not because it was easy, but because it was "
                 "necessary'. The shape does the persuading; the content only "
                 "has to be plausible. That is also its danger — a balanced "
                 "sentence can make a false choice sound inevitable.",
                 "تقابل دو نیمه را با شکل هم‌خوان به هم می‌بندد: «not because "
                 "it was easy, but because it was necessary». شکل، اقناع را "
                 "انجام می‌دهد و محتوا فقط باید باورپذیر باشد. خطرش هم همان "
                 "است — جملهٔ متوازن می‌تواند انتخاب نادرست را ناگزیر جلوه "
                 "دهد."),
                ("The discipline is frequency. One balanced sentence closes a "
                 "paragraph; three close a manifesto. In academic prose, "
                 "parallelism should be structural, not decorative: headings "
                 "that match, list items in the same form, findings stated in "
                 "the same order as the questions.",
                 "انضباط در بسامد است. یک جملهٔ متوازن یک بند را می‌بندد و سه "
                 "تا یک بیانیه. در نثر دانشگاهی توازی باید ساختاری باشد نه "
                 "تزیینی: عنوان‌های هم‌شکل، اقلام فهرست در یک صورت و یافته‌ها "
                 "به همان ترتیب پرسش‌ها."),
            ],
            [
                ("We asked for the figures, the sites and the dates.",
                 "ما ارقام، سایت‌ها و تاریخ‌ها را خواستیم."),
                ("Not because the risk was small, but because it was "
                 "unmeasured.", "نه چون خطر کوچک بود، بلکه چون سنجیده نشده "
                 "بود."),
                ("The report is precise, the summary is honest, and the "
                 "recommendation is late.", "گزارش دقیق است، خلاصه صادق است و "
                 "توصیه دیر رسیده."),
                ("Either publish the method or withdraw the claim.",
                 "یا روش را منتشر کن یا ادعا را پس بگیر."),
            ],
            [
                mcq("Parallelism signals that items ___.", "توازی نشان می‌دهد "
                    "که اقلام ___.",
                    ["are important", "belong to one list and standard",
                     "are new", "are optional"], 1,
                    "Symmetry claims equal treatment.",
                    "تقارن برخورد یکسان را ادعا می‌کند."),
                mcq("Breaking parallelism makes an item feel ___.",
                    "شکستن توازی یک قلم را ___ می‌سازد.",
                    ["stronger", "like an afterthought", "longer",
                     "more formal"], 1,
                    "The reader infers a difference in kind.",
                    "خواننده تفاوت در نوع را استنتاج می‌کند."),
            ],
            [
                mcq("Which list is parallel?", "کدام فهرست متوازن است؟",
                    ["to publish, to name, and accepting",
                     "publishing, naming, and accepting",
                     "to publish, naming, acceptance",
                     "publish, to name, accepting"], 1,
                    "All three are gerunds.",
                    "هر سه اسم فعل‌اند."),
                gap("The construction 'not because X, ___ because Y' is "
                     "antithesis.", ["but"], "The pair is fixed.",
                    "این جفت ثابت است.", "one word"),
                mcq("The danger of antithesis is that it can ___ .",
                    "خطر تقابل این است که می‌تواند ___.",
                    ["shorten a text", "make a false choice sound "
                     "inevitable", "add statistics", "soften a claim"], 1,
                    "Form persuades before content is examined.",
                    "شکل پیش از بررسی محتوا اقناع می‌کند."),
                gap("One balanced sentence closes a paragraph; three close a "
                     "___.", ["manifesto"],
                    "Frequency turns rhetoric into performance.",
                    "بسامد بلاغت را به اجرا بدل می‌کند.", "one word"),
            ],
        ),
        lesson(
            "c2-u8-l2", "vocabulary",
            ("Confusables that survive spellcheck",
             "واژه‌های اشتباه‌گرفته‌شدنی که از غلط‌یاب رد می‌شوند"),
            ("Separate the pairs that no spellchecker can catch.",
             "جفت‌هایی را جدا کن که هیچ غلط‌یابی نمی‌گیرد."),
            [
                ("Affect is usually a verb, effect usually a noun: the delay "
                 "affected the result; the effect was small. To effect a "
                 "change is to bring it about, which is rare and formal. "
                 "Imply is what a speaker does; infer is what a listener "
                 "does. A writer implies, a reader infers, and neither "
                 "'infers a point' in public without being corrected.",
                 "affect معمولاً فعل است و effect معمولاً اسم: the delay "
                 "affected the result؛ the effect was small. «to effect a "
                 "change» یعنی آن را به وجود آوردن که کم‌یاب و رسمی است. "
                 "imply کار گوینده است و infer کار شنونده. نویسنده تلویح "
                 "می‌کند و خواننده استنباط، و هیچ‌کدام در جمع «infers a "
                 "point» نمی‌گویند بی‌آنکه تصحیح شوند."),
                ("Comprise means consist of, so 'is comprised of' is "
                 "redundant, and the whole comprises the parts while the "
                 "parts compose the whole. Disinterested means impartial; "
                 "uninterested means bored. Principal is first or main; "
                 "principle is a rule. Continuous means without a break; "
                 "continual means repeatedly.",
                 "comprise یعنی تشکیل شده از، پس «is comprised of» زائد است؛ "
                 "کل comprises اجزا را و اجزا compose کل را. disinterested "
                 "یعنی بی‌طرف و uninterested یعنی بی‌حوصله. principal یعنی "
                 "نخست یا اصلی و principle یعنی قاعده. continuous یعنی "
                 "بی‌وقفه و continual یعنی مکرر."),
                ("These pairs matter because the wrong one is invisible to a "
                 "checker and audible to a careful reader. In an exam, the "
                 "distinction is usually the whole question.",
                 "این جفت‌ها مهم‌اند چون واژهٔ نادرست از چشم غلط‌یاب پنهان و "
                 "برای خوانندهٔ دقیق شنیدنی است. در آزمون، معمولاً همین تفاوت "
                 "کل پرسش است."),
            ],
            [
                ("The strike affected three ports and had no effect on "
                 "prices.", "اعتصاب سه بندر را تحت تأثیر گذاشت و اثری بر "
                 "قیمت‌ها نداشت."),
                ("The minister implied that the review was over; the press "
                 "inferred that it had been buried.", "وزیر تلویحاً گفت "
                 "بازبینی تمام شده و مطبوعات استنباط کردند دفن شده است."),
                ("The committee comprises nine members, three of whom are "
                 "external.", "کمیته از نُه عضو تشکیل شده که سه نفرشان "
                 "بیرونی‌اند."),
                ("A disinterested chair is not the same as an uninterested "
                 "one.", "رئیس بی‌طرف با رئیس بی‌حوصله یکی نیست."),
            ],
            [
                mcq("Choose the correct form: the decision ___ the outcome.",
                    "صورت درست را انتخاب کن: the decision ___ the outcome.",
                    ["effected", "affected", "effect", "affect"], 1,
                    "Affect is the verb of influence.",
                    "affect فعل تأثیرگذاشتن است."),
                mcq("'Comprised of' is best replaced by ___.",
                    "«comprised of» بهتر است با ___ عوض شود.",
                    ["composed of", "consisting", "comprised", "made"], 0,
                    "Parts compose; the whole comprises.",
                    "اجزا compose و کل comprises."),
            ],
            [
                mcq("A reader ___ a point; a writer ___ one.",
                    "خواننده نکته‌ای را ___ و نویسنده ___ می‌کند.",
                    ["implies / infers", "infers / implies",
                     "affects / effects", "effects / affects"], 1,
                    "The listener draws the conclusion.",
                    "شنونده نتیجه را می‌گیرد."),
                gap("A ___ decision is one made without personal interest.",
                    ["disinterested"], "Not the same as bored.",
                    "با بی‌حوصله یکی نیست.", "one word"),
                mcq("Rain fell ___ for three days without stopping.",
                    "باران سه روز ___ بدون توقف بارید.",
                    ["continually", "continuously", "principally",
                     "compositely"], 1,
                    "Without a break is continuous.",
                    "بدون وقفه یعنی continuous."),
                gap("The ___ finding was that the sample was too small.",
                    ["principal"], "Main, not a rule.",
                    "اصلی، نه قاعده.", "one word"),
            ],
        ),
        lesson(
            "c2-u8-l3", "writing",
            ("The review that reviews the argument",
             "نقدی که استدلال را نقد می‌کند"),
            ("Review a claim and its evidence, not the author's style or "
             "their reputation.",
             "ادعا و شاهدش را نقد کن، نه سبک نویسنده یا شهرتش را."),
            [
                ("A review has three obligations: to state the claim fairly, "
                 "to test the evidence rather than the conclusion, and to say "
                 "what would change the reviewer's mind. The middle one is "
                 "where most reviews fail: they attack a conclusion they "
                 "dislike with an argument the author never made.",
                 "نقد سه تعهد دارد: ادعا را منصفانه بگوید، شاهد را بیازماید نه "
                 "نتیجه را، و بگوید چه چیزی نظر منتقد را عوض می‌کند. وسطی "
                 "جایی است که بیشتر نقدها شکست می‌خورند: به نتیجه‌ای که "
                 "نمی‌پسندند با استدلالی حمله می‌کنند که نویسنده هرگز نگفته."),
                ("Fairness is a technique, not a mood: quote the strongest "
                 "sentence, give its scope, then say where it strains. 'The "
                 "claim holds for the two sites studied and is silent about "
                 "the rest' is a review. 'The author is biased' is a mood.",
                 "انصاف یک تکنیک است، نه حال‌وهوا: قوی‌ترین جمله را نقل کن، "
                 "دامنه‌اش را بگو و بعد بگو کجا کش می‌آید. «The claim holds "
                 "for the two sites studied and is silent about the rest» "
                 "نقد است. «The author is biased» حال‌وهواست."),
            ],
            [
                ("The argument is sound where it is tested and silent where "
                 "it is not.", "استدلال جایی که آزموده شده محکم است و جایی که "
                 "نشده ساکت."),
                ("The evidence supports a local effect, not a general one.",
                 "شاهد از اثری محلی پشتیبانی می‌کند، نه عمومی."),
                ("I would be persuaded by a second site and a full year.",
                 "با سایت دومی و یک سال کامل قانع می‌شوم."),
            ],
            [
                mcq("A review tests ___.", "نقد ___ را می‌آزماید.",
                    ["the author's motives", "the evidence behind the claim",
                     "the publisher", "the title"], 1,
                    "Evidence, not intention, is reviewable.",
                    "شاهد قابل نقد است، نه نیت."),
                mcq("'What would change my mind' makes a review ___.",
                    "«چه چیزی نظرم را عوض می‌کند» نقد را ___ می‌کند.",
                    ["longer", "falsifiable", "polite", "informal"], 1,
                    "It states the conditions under which the judgement "
                    "fails.", "شرایط شکست داوری را می‌گوید."),
            ],
            [
                write("Write a review of about 160 words of a report claiming "
                      "that a pilot cut waiting times by a third. State the "
                      "claim fairly, test the evidence, name one thing the "
                      "report cannot support, and say what would change your "
                      "mind.",
                      "نقدی حدود ۱۶۰ واژه بنویس دربارهٔ گزارشی که ادعا می‌کند "
                      "آزمایشی زمان انتظار را یک‌سوم کم کرده است. ادعا را "
                      "منصفانه بگو، شاهد را بیازما، یک چیز را که گزارش نمی‌تواند "
                      "پشتیبانی کند نام ببر و بگو چه چیزی نظرت را عوض می‌کند.",
                      160, ["although", "whereas"],
                      "Fair statement, evidence tested, one unsupported "
                      "inference, and a falsifiable condition.",
                      "بیان منصفانه، آزمون شاهد، یک استنتاج ناپشتیبان و یک شرط "
                      "ابطال‌پذیر."),
                mcq("Which sentence reviews rather than judges the author?",
                    "کدام جمله نقد می‌کند و نه داوری دربارهٔ نویسنده؟",
                    ["The author clearly has a agenda.",
                     "The sample covers two sites, so the national claim is "
                     "unsupported.",
                     "This report is not worth reading.",
                     "The writing is dull."], 1,
                    "It names the evidential gap.",
                    "شکاف شاهدی را نام می‌برد."),
                gap("A review should say what would ___ its own judgement.",
                    ["change", "falsify"], "Falsifiability is the mark of a "
                    "serious review.", "ابطال‌پذیری نشانهٔ نقد جدی است.",
                    "one word"),
            ],
        ),
        lesson(
            "c2-u8-l4", "speaking",
            ("Holding three positions at once",
             "نگه‌داشتن سه موضع هم‌زمان"),
            ("Synthesise several perspectives aloud without flattening them "
             "into agreement.",
             "چند دیدگاه را با صدای بلند ترکیب کن بی‌آنکه به توافق تختشان "
             "کنی."),
            [
                ("Advanced speaking often means holding three positions at "
                 "once: the one you find strongest, the one you can defend, "
                 "and the one you cannot dismiss. Saying so explicitly is not "
                 "evasion; it is the most precise account of your state of "
                 "mind, and it gives the listener something to argue with.",
                 "گفتار پیشرفته اغلب یعنی نگه‌داشتن سه موضع هم‌زمان: آن که "
                 "قوی‌ترین می‌دانی، آن که می‌توانی از آن دفاع کنی و آن که "
                 "نمی‌توانی ردش کنی. صریح گفتنش فرار نیست؛ دقیق‌ترین توصیف "
                 "حال ذهنی توست و به شنونده چیزی برای بحث می‌دهد."),
                ("The language of synthesis is comparative and attributed: "
                 "'the report's case is stronger on cost, the interviews' case "
                 "on experience'. Notice that no adverb of opinion is needed; "
                 "the comparison does the work, and the listener can disagree "
                 "with a comparison much more easily than with an adjective.",
                 "زبان ترکیب مقایسه‌ای و منتسب است: «the report's case is "
                 "stronger on cost, the interviews' case on experience». ببین "
                 "که هیچ قید نظری لازم نیست؛ مقایسه کار را می‌کند و شنونده "
                 "می‌تواند با مقایسه بسیار آسان‌تر از یک صفت مخالفت کند."),
            ],
            [
                ("On cost the report is stronger; on experience the "
                 "interviews are.", "در هزینه گزارش قوی‌تر است و در تجربه "
                 "مصاحبه‌ها."),
                ("I can defend the first position and I cannot dismiss the "
                 "third.", "می‌توانم از موضع اول دفاع کنم و نمی‌توانم سومی را "
                 "رد کنم."),
                ("Both are right about different things, and only one of them "
                 "is measurable.", "هر دو دربارهٔ چیزهای متفاوت درست می‌گویند و "
                 "تنها یکی سنجیدنی است."),
            ],
            [
                mcq("Synthesis in speech is clearest when it uses ___ .",
                    "ترکیب در گفتار وقتی روشن‌تر است که ___ به کار برد.",
                    ["strong adjectives", "comparisons with attribution",
                     "long pauses", "quotations"], 1,
                    "Comparisons can be contested precisely.",
                    "می‌توان دقیق با مقایسه مخالفت کرد."),
                mcq("Saying 'I cannot dismiss that' is ___.",
                    "گفتن «I cannot dismiss that» ___.",
                    ["evasion", "a precise account of your position",
                     "a change of subject", "a concession of defeat"], 1,
                    "It states the limit of your own argument.",
                    "مرز استدلال خودت را می‌گوید."),
            ],
            [
                say("The report is stronger on cost and the interviews are "
                    "stronger on experience, and I do not think one cancels "
                    "the other.", "گزارش در هزینه قوی‌تر است و مصاحبه‌ها در "
                    "تجربه، و فکر نمی‌کنم یکی دیگری را باطل کند."),
                say("I can defend the first position in detail. The third I "
                    "cannot dismiss, which is why I put a condition on my "
                    "recommendation.", "می‌توانم از موضع اول با جزئیات دفاع "
                    "کنم. سومی را نمی‌توانم رد کنم و به همین دلیل بر توصیه‌ام "
                    "شرط گذاشتم."),
                say("If I had to choose, I would take the measurable claim, "
                    "and I would say plainly what it leaves out.",
                    "اگر مجبور به انتخاب باشم ادعای سنجیدنی را می‌گیرم و صریح "
                    "می‌گویم چه چیزی را بیرون می‌گذارد."),
                say("What would settle this is not another argument but a "
                    "second year of data.", "آنچه این را فیصله می‌دهد "
                    "استدلالی دیگر نیست، بلکه سال دومی از داده است."),
            ],
            dialogue=dialogue([
                ("Chair", "You have heard both sides. Where do you stand?",
                 "هر دو طرف را شنیدید. کجا می‌ایستید؟"),
                ("You", "On cost, with the report: the figures are "
                 "auditable. On experience, with the interviews: forty "
                 "minutes is what people remember.",
                 "در هزینه با گزارش: ارقام قابل حسابرسی‌اند. در تجربه با "
                 "مصاحبه‌ها: چهل دقیقه همان چیزی است که مردم به یاد "
                 "می‌آورند."),
                ("Chair", "That is two answers, not one.", "این دو پاسخ است، "
                 "نه یکی."),
                ("You", "It is one answer with two parts, and I would rather "
                 "give it than pretend the second part is not there.",
                 "یک پاسخ است با دو بخش، و ترجیح می‌دهم همین را بدهم تا "
                 "ادا درآورم بخش دوم وجود ندارد."),
            ]),
        ),
    ],
)
