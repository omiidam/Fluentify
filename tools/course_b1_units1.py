#!/usr/bin/env python3
"""B1 · units 1-2: experience with a timeline, and conditions that are not real.

B1 starts where A2 stopped. The present perfect is no longer only 'ever' — it is
the tense of everything still open — and the second conditional lets a learner
talk about what is not true.
"""

from course_kit import gap, lesson, listen, mcq, passage, unit

U1 = unit(
    "b1-u1",
    ("Since then", "از آن زمان"),
    ("Tell the difference between an experience and a finished event, and describe how a life has changed.", "تفاوت تجربه و رویداد تمام‌شده را بگو و بگو زندگی‌ات چطور عوض شده است."),
    [
        lesson(
            "b1-u1-l1",
            "grammar",
            ("Present perfect and past simple: the timeline decides", "حال کامل و گذشتهٔ ساده: زمان‌خط تصمیم می‌گیرد"),
            ("Choose between the two tenses by whether the time is still open.", "بین این دو زمان بر اساس باز یا بسته بودن زمان انتخاب کن."),
            [
                ("The present perfect (have/has + participle) describes something inside a period that is still open. I've lived here for six years — I still live here. The past simple describes a closed period: I lived there for six years — and then I left.", "حال کامل (have/has + اسم مفعول) چیزی را در دوره‌ای باز توصیف می‌کند. I've lived here for six years یعنی هنوز اینجا زندگی می‌کنم. گذشتهٔ ساده دوره‌ای بسته را می‌گوید: I lived there for six years و بعد رفتم."),
                ("For measures a length, since a starting point: for three months, since March, since I was a child. 'Since three months' is wrong; 'for March' is wrong.", "for طول مدت و since نقطهٔ شروع را می‌گوید: for three months، since March، since I was a child. «since three months» و «for March» غلط‌اند."),
                ("Just (a moment ago), already (sooner than expected), yet (up to now, negative and questions), ever and never sit with the perfect. Yesterday, last week, in 2019 and ago belong to the past simple.", "just، already، yet، ever و never با حال کامل می‌آیند. yesterday، last week، in 2019 و ago به گذشتهٔ ساده تعلق دارند."),
                ("A conversation often shifts from the open to the closed tense: Have you finished the report? — Yes, I finished it at six. The experience is perfect; the detail is simple.", "گفت‌وگو اغلب از زمان باز به بسته می‌رود: Have you finished the report? — Yes, I finished it at six. تجربه با حال کامل و جزئیات با گذشتهٔ ساده."),
            ],
            [
                ("I've worked at this school since 2021, and I've taught about six hundred students.", "از ۲۰۲۱ در این مدرسه کار می‌کنم و حدود ششصد دانش‌آموز داشته‌ام."),
                ("She has just sent the report, so it's in your inbox.", "همین حالا گزارش را فرستاده، پس در صندوق ورودی توست."),
                ("We've already eaten, but we'd love a coffee.", "قبلاً غذا خورده‌ایم، اما قهوه را دوست داریم."),
                ("He worked in Dubai for two years and then came back.", "دو سال در دبی کار کرد و بعد برگشت."),
                ("Have you ever written a complaint? — Yes, I wrote one last year, and they answered in two days.", "تا حالا شکایت نوشته‌ای؟ — بله، سال گذشته نوشتم و دو روزه جواب دادند."),
            ],
            [
                mcq("I ___ here since 2018, and I don't plan to leave.", "از ۲۰۱۸ اینجا ___ و قصد ندارم بروم.", ["worked", "have worked", "work", "was working"], 1,
                    "The situation is still open, so the present perfect.", "وضعیت هنوز باز است، پس حال کامل."),
                mcq("She ___ the report yesterday afternoon.", "او گزارش را دیروز بعدازظهر ___ .", ["has finished", "finished", "finishes", "was finishing"], 1,
                    "Yesterday is closed, so the past simple.", "دیروز بسته است، پس گذشتهٔ ساده."),
            ],
            [
                gap("We've known each other ___ more than ten years.", ["for"], "for + a length of time.", "for + طول مدت."),
                gap("I haven't seen him ___ he moved to Berlin.", ["since"], "since + a point in time or a past action.", "since + نقطهٔ زمانی یا رویداد گذشته."),
                mcq("Which sentence is correct?", "کدام جمله درست است؟", ["I have seen her last Tuesday.", "I've seen her three times this month.", "I saw her three times this month, and I've seen her again tomorrow.", "I have saw her."], 1,
                    "This month is still open, so the perfect is right.", "این ماه هنوز باز است، پس حال کامل درست است."),
                gap("They ___ (just / arrive), so give them a minute.", ["have just arrived"], "Just with the present perfect.", "just با حال کامل."),
            ],
        ),
        lesson(
            "b1-u1-l2",
            "vocabulary",
            ("Personal development and the turning points", "رشد شخصی و نقطه‌های چرخش"),
            ("Describe how people change, what they achieve and what they overcome.", "بگو آدم‌ها چطور عوض می‌شوند، چه به دست می‌آورند و از چه چیزی عبور می‌کنند."),
            [
                ("A turning point is the moment after which things are different: moving to a new city, losing a job, having a child, failing an exam and trying again. We say something changed my life, I made a decision, I gave something up.", "نقطهٔ چرخش لحظه‌ای است که بعد از آن همه‌چیز عوض می‌شود. می‌گوییم something changed my life، I made a decision، I gave something up."),
                ("Achievement has its own verbs: achieve a goal, make progress, overcome a difficulty, take a risk, deal with a problem, get through a hard time. Notice that progress is uncountable — you make progress, you don't 'do a progress'.", "دستاورد فعل‌های خودش را دارد: achieve a goal، make progress، overcome a difficulty، take a risk، deal with a problem، get through a hard time. توجه کن progress نشماردنی است؛ make progress می‌گوییم."),
                ("Character words are graded, not absolute: confident, determined, independent, patient, reliable, ambitious. Be careful with the difference between shy (uncomfortable with people) and quiet (not talkative), or between stubborn and determined.", "واژه‌های شخصیت درجه‌بندی دارند، نه مطلق: confident، determined، independent، patient، reliable، ambitious. تفاوت shy (معذب در جمع) و quiet (کم‌حرف) و نیز stubborn و determined را در نظر بگیر."),
            ],
            [
                ("Moving abroad was a turning point for me; I became much more independent.", "رفتن به خارج برای من نقطهٔ چرخش بود؛ بسیار مستقل‌تر شدم."),
                ("She overcame her fear of speaking in public and now runs a team.", "بر ترس از سخنرانی در جمع غلبه کرد و حالا سرپرست یک تیم است."),
                ("I've made a lot of progress since I started practicing every day.", "از وقتی هر روز تمرین می‌کنم پیشرفت زیادی کرده‌ام."),
                ("He gave up his second job to spend more time with his children.", "کار دومش را رها کرد تا وقت بیشتری با بچه‌هایش بگذراند."),
            ],
            [
                mcq("To successfully deal with a difficulty is to ___ it.", "گذر موفق از یک سختی یعنی ___ آن.", ["overcome", "achieve", "make", "take"], 0,
                    "You overcome a difficulty or a fear.", "overcome با difficulty یا fear می‌آید."),
                mcq("Which is uncountable?", "کدام نشماردنی است؟", ["decision", "progress", "goal", "risk"], 1,
                    "Progress is uncountable: make progress.", "progress نشماردنی است: make progress."),
            ],
            [
                gap("She ___ a big risk when she left a secure job for a company of three people.", ["took"], "Take a risk, past simple took.", "take a risk و گذشتهٔ آن took است."),
                gap("I've ___ a lot of progress with my pronunciation this year.", ["made"], "Make progress, present perfect made.", "make progress و حال کامل made."),
                mcq("'He is determined' is closest to ___.", "«He is determined» نزدیک‌ترین معنا به ___ است.", ["he gives up easily", "he will not let difficulties stop him", "he is unsure", "he is lazy"], 1,
                    "Determination is the refusal to be stopped.", "determination یعنی تن ندادن به توقف."),
                listen("Two years ago I couldn't speak in meetings at all. I joined a club and practiced every week, and last month I gave a presentation to forty people.", "What has the speaker achieved?", "گوینده به چه چیزی رسیده است؟", ["a new job", "confidence in speaking in public", "a bigger team", "a degree"], 1,
                       "She went from silence to presenting to forty people.", "از سکوت به ارائه برای چهل نفر رسیده است."),
            ],
        ),
        lesson(
            "b1-u1-l3",
            "reading",
            ("A second chance at school", "فرصت دوم در مدرسه"),
            ("Read a personal story about returning to education and follow its argument.", "داستان شخصی بازگشت به تحصیل را بخوان و استدلالش را دنبال کن."),
            [
                ("A personal narrative at B1 has a shape: a situation, a problem, a decision, and a result the writer now interprets. The last paragraph usually tells you what the story is for — its point, not just its ending.", "روایت شخصی در B1 شکلی دارد: موقعیت، مشکل، تصمیم و نتیجه‌ای که نویسنده الان تفسیرش می‌کند. پاراگراف آخر معمولاً می‌گوید داستان برای چه گفته شده؛ یعنی نقطهٔ آن، نه فقط پایانش."),
                ("Pronouns do heavy work: 'it' may refer to a whole idea from the previous sentence. When a sentence is unclear, look back one sentence for the noun that fits, not forward.", "ضمیرها کار سنگینی می‌کنند: «it» ممکن است به کل ایدهٔ جملهٔ قبل اشاره کند. اگر جمله مبهم بود، برای اسم مناسب یک جمله عقب‌تر نگاه کن، نه جلوتر."),
            ],
            [
                ("Situation: 'I left school at fifteen and worked in a shop for eleven years.'", "موقعیت: «پانزده‌سالگی مدرسه را رها کردم و یازده سال در مغازه کار کردم»."),
                ("Decision: 'When the shop closed, I decided to finish the education I had missed.'", "تصمیم: «وقتی مغازه بسته شد، تصمیم گرفتم تحصیلی را که از دست داده بودم تمام کنم»."),
                ("Interpretation: 'I was not behind; I had simply taken a longer road.'", "تفسیر: «عقب نبودم؛ فقط راه طولانی‌تری رفته بودم»."),
            ],
            [
                mcq("Why did the writer return to education?", "چرا نویسنده به تحصیل برگشت؟", ["she wanted a better salary immediately", "the shop where she worked closed", "her children asked her to", "she failed an exam"], 1,
                    "The shop closed, and that made the decision possible.", "مغازه بسته شد و همین تصمیم را ممکن کرد."),
                mcq("How long had she worked in the shop?", "چند سال در مغازه کار کرده بود؟", ["two years", "eleven years", "fifteen years", "twenty years"], 1,
                    "'I worked in a shop for eleven years.'", "«یازده سال در مغازه کار کردم»."),
            ],
            [
                mcq("What was hardest at the beginning?", "در آغاز چه چیزی سخت‌تر بود؟", ["the teachers", "feeling younger students knew more than she did", "the journey to school", "the cost of books"], 1,
                    "She says she felt the younger students were far ahead of her.", "می‌گوید حس می‌کرد دانش‌آموزان جوان‌تر خیلی از او جلوترند."),
                mcq("What does 'I was not behind; I had simply taken a longer road' mean?", "«I was not behind; I had simply taken a longer road» یعنی چه؟", ["She was slower than everyone.", "Her experience was different, not worse.", "She had taken the wrong road.", "She wanted to stop studying."], 1,
                    "She reframes her late start as a different route, not a deficit.", "شروع دیرهنگام را مسیری متفاوت می‌بیند، نه کمبود."),
                mcq("What is the writer's purpose?", "هدف نویسنده چیست؟", ["to advertise a school", "to encourage people who think it is too late", "to criticize teachers", "to describe a shop"], 1,
                    "The story is offered as encouragement to late returners.", "داستان تشویقی است برای کسانی که دیر شروع می‌کنند."),
                mcq("Which sentence shows the writer's attitude most clearly?", "کدام جمله نگرش نویسنده را روشن‌تر نشان می‌دهد؟", ["I left school at fifteen.", "I worked in a shop.", "I had simply taken a longer road.", "The shop closed in 2019."], 2,
                    "The metaphor is her judgment about her own path.", "این استعاره داوری او دربارهٔ مسیر خودش است."),
            ],
            passage=passage(("A second chance at school", "فرصت دوم در مدرسه"),
                            ("I left school at fifteen and worked in a shop for eleven years. I was good at the job, but I never stopped thinking about the classrooms I had walked out of.\n\nWhen the shop closed in 2019, I decided to finish the education I had missed. I was thirty-one and the youngest student in my class was sixteen. For the first month I was sure everyone knew more than I did. I nearly stopped twice.\n\nWhat helped was arithmetic. In the shop I had calculated prices, discounts and change for eleven years without a calculator, and suddenly the numbers on the board made sense in a way they never had at school.\n\nI finished the course last summer with the second highest mark in the class. I don't think I was behind all those years. I had simply taken a longer road, and I arrived with something my classmates did not have yet.",
                             "پانزده‌سالگی مدرسه را رها کردم و یازده سال در مغازه کار کردم. در کارم خوب بودم، اما هرگز از فکر کلاس‌هایی که ترک کرده بودم بیرون نیامدم.\n\nوقتی مغازه در ۲۰۱۹ بسته شد، تصمیم گرفتم تحصیلی را که از دست داده بودم تمام کنم. سی‌ویک ساله بودم و جوان‌ترین دانش‌آموز کلاس شانزده سال داشت. ماه اول مطمئن بودم همه بیشتر از من می‌دانند. دو بار نزدیک بود رها کنم.\n\nچیزی که کمک کرد حساب بود. یازده سال در مغازه بدون ماشین‌حساب قیمت، تخفیف و پول خرد را حساب کرده بودم و ناگهان عددهای روی تخته معنایی پیدا کردند که در مدرسه هرگز نداشتند.\n\nتابستان گذشته دوره را با دومین نمرهٔ کلاس تمام کردم. فکر نمی‌کنم آن سال‌ها عقب بوده باشم. فقط راه طولانی‌تری رفته بودم و با چیزی رسیدم که هم‌کلاسی‌هایم هنوز نداشتند.")),
        ),
    ],
)

U2 = unit(
    "b1-u2",
    ("If it were up to me", "اگر دست من بود"),
    ("Talk about real possibilities and about situations that are not true, and use both in a job interview.", "دربارهٔ امکان‌های واقعی و موقعیت‌های غیرواقعی حرف بزن و هر دو را در مصاحبهٔ کاری به کار ببر."),
    [
        lesson(
            "b1-u2-l1",
            "grammar",
            ("First and second conditionals", "شرطی نوع اول و دوم"),
            ("Choose the first conditional for what may happen and the second for what does not happen now.", "شرطی اول را برای آنچه ممکن است بشود و شرطی دوم را برای آنچه الان نمی‌شود انتخاب کن."),
            [
                ("First conditional: if + present simple, will + verb. It is a real possibility: If I get the job, I'll move to Tabriz. The condition is open — it may or may not happen.", "شرطی اول: if + حال ساده، will + فعل. امکانی واقعی است: If I get the job, I'll move to Tabriz. شرط باز است؛ ممکن است بشود یا نشود."),
                ("Second conditional: if + past simple, would + verb. It describes an imagined present, not a future: If I had more time, I would learn the guitar. I don't have the time — that is the point.", "شرطی دوم: if + گذشتهٔ ساده، would + فعل. حالِ خیالی را توصیف می‌کند، نه آینده: If I had more time, I would learn the guitar. وقت ندارم و همین نکتهٔ اصلی است."),
                ("With be, the second conditional prefers were for every person: If I were you, I'd apply. In speech 'If I was you' is common, but were is the careful form.", "با be، شرطی دوم برای همهٔ شخص‌ها were را ترجیح می‌دهد: If I were you, I'd apply. در گفتار «If I was you» رایج است، اما were شکل دقیق‌تر است."),
                ("Related patterns: I wish + past simple for a present regret (I wish I spoke French), and would rather for preference. Unless replaces if not in either conditional.", "الگوهای مرتبط: I wish + گذشتهٔ ساده برای حسرت حال (I wish I spoke French) و would rather برای ترجیح. unless در هر دو شرطی جای if not می‌آید."),
            ],
            [
                ("If the train is on time, we'll be there by six.", "اگر قطار سر وقت باشد، تا شش آنجا هستیم."),
                ("If I had a car, I would drive to work instead of taking two buses.", "اگر ماشین داشتم، به‌جای دو اتوبوس با ماشین به کار می‌رفتم."),
                ("If I were you, I'd ask for the salary in writing.", "جای تو بودم، حقوق را کتبی می‌خواستم."),
                ("Unless we leave now, we'll miss the beginning of the movie.", "اگر الان راه نیفتیم، ابتدای فیلم را از دست می‌دهیم."),
                ("I wish I had more patience with my students.", "ای کاش با دانش‌آموزانم صبورتر بودم."),
            ],
            [
                mcq("If I ___ more confident, I would speak in the meeting.", "اگر ___ اعتماد بیشتری داشتم، در جلسه حرف می‌زدم.", ["am", "was being", "were", "will be"], 2,
                    "The second conditional takes the past; with be, were.", "شرطی دوم گذشته می‌گیرد و با be شکل were."),
                mcq("If you ___ the form today, you'll get an answer this week.", "اگر امروز فرم را ___، همین هفته پاسخ می‌گیری.", ["send", "sent", "will send", "would send"], 0,
                    "First conditional: present simple after if.", "شرطی اول: حال ساده بعد از if."),
            ],
            [
                gap("If I ___ (know) the answer, I would tell you.", ["knew"], "Second conditional: past simple after if.", "شرطی دوم: گذشتهٔ ساده بعد از if."),
                gap("We would have more space if we ___ (move) the desk.", ["moved"], "An imagined present, so the past simple.", "حالِ خیالی، پس گذشتهٔ ساده."),
                mcq("Which sentence is a second conditional?", "کدام جمله شرطی دوم است؟", ["If it rains, we'll stay in.", "If it rained, we would stay in.", "If it rains, we stay in.", "When it rains, we stay in."], 1,
                    "Past + would marks the imagined present.", "گذشته + would نشانهٔ حالِ خیالی است."),
                listen("If I got the job in Isfahan, I would take the train home every weekend — it's only four hours.", "Is the speaker doing the job now?", "آیا گوینده الان آن کار را دارد؟", ["yes, and he travels by train", "no, it is imagined", "yes, but he flies", "no, and he would not travel"], 1,
                       "Would take marks an imagined situation, not a current one.", "would take موقعیت خیالی را نشان می‌دهد، نه وضعیت فعلی."),
            ],
        ),
        lesson(
            "b1-u2-l2",
            "vocabulary",
            ("Careers: applying, interviewing, being hired", "شغل: درخواست، مصاحبه، استخدام"),
            ("Use the vocabulary of a job search from advertisement to contract.", "واژگان جست‌وجوی کار را از آگهی تا قرارداد به کار ببر."),
            [
                ("The process has named stages: a vacancy is advertised, you apply for the post, send a CV and a covering letter, and are shortlisted for an interview. The employer checks your references and makes an offer; you accept or turn it down.", "فرایند مرحله‌های نام‌دار دارد: vacancy آگهی می‌شود، برای post درخواست می‌دهی، CV و نامهٔ همراه می‌فرستی و برای مصاحبه shortlist می‌شوی. کارفرما references را بررسی می‌کند و offer می‌دهد؛ تو قبول می‌کنی یا رد می‌کنی."),
                ("Say what you bring: I have five years' experience in sales. I'm good at working under pressure. I'm responsible for a team of four. Strengths and weaknesses are the interview words; a probation period is the first three months.", "بگو چه چیزی می‌آوری: I have five years' experience in sales. I'm good at working under pressure. I'm responsible for a team of four. strengths و weaknesses واژه‌های مصاحبه‌اند و probation period سه ماه اول است."),
                ("Money and conditions: salary (monthly or yearly), a raise, benefits (health insurance, paid vacation), a permanent or temporary contract, flexible hours, to be promoted, to resign. 'I'm between jobs' is the neutral way to say you are unemployed.", "پول و شرایط: salary (ماهانه یا سالانه)، raise، benefits (بیمه، مرخصی)، قرارداد permanent یا temporary، ساعت منعطف، promote شدن و resign کردن. «I'm between jobs» راه خنثی برای گفتن بیکاری است."),
            ],
            [
                ("I applied for the post of assistant manager and was shortlisted.", "برای سمت کمک‌مدیر درخواست دادم و به مرحلهٔ مصاحبه رسیدم."),
                ("She turned down the offer because the salary was lower than her current one.", "پیشنهاد را رد کرد، چون حقوقش از حقوق فعلی‌اش کمتر بود."),
                ("My main strength is that I stay calm when a customer is angry.", "قوت اصلی‌ام این است که وقتی مشتری عصبانی است آرام می‌مانم."),
                ("He was promoted after two years and now manages the branch.", "بعد از دو سال ارتقا گرفت و حالا شعبه را مدیریت می‌کند."),
            ],
            [
                mcq("A job that is available is a ___.", "کاری که موجود است ___ است.", ["CV", "vacancy", "reference", "probation"], 1,
                    "A vacancy is an open position.", "vacancy یک موقعیت باز است."),
                mcq("To refuse an offer is to ___ it.", "رد کردن پیشنهاد یعنی ___ آن.", ["accept", "turn down", "apply for", "take on"], 1,
                    "Turn down means to decline.", "turn down یعنی رد کردن."),
            ],
            [
                gap("Please send your CV and a covering ___ to the address below.", ["letter"], "A covering letter accompanies a CV.", "covering letter همراه CV فرستاده می‌شود."),
                gap("After six months he was ___ to team leader.", ["promoted"], "Be promoted to a position.", "be promoted to یک سمت."),
                mcq("'A permanent contract' is the opposite of ___.", "«A permanent contract» متضاد ___ است.", ["a full-time job", "a temporary contract", "a probation period", "a salary"], 1,
                    "Permanent and temporary are opposites.", "permanent و temporary متضادند."),
                mcq("'References' are ___.", "«References» ___ هستند.", ["people who recommend you", "the money you earn", "the hours you work", "the questions in an interview"], 0,
                    "A reference is a statement from a previous employer.", "reference اظهارنظر کارفرمای قبلی است."),
            ],
        ),
        lesson(
            "b1-u2-l3",
            "listening",
            ("A job interview", "مصاحبهٔ کاری"),
            ("Follow a short interview and hear the difference between what is asked and what is meant.", "مصاحبهٔ کوتاهی را دنبال کن و تفاوت پرسش و منظورش را بشنو."),
            [
                ("Interview questions are indirect requests. 'Tell me about a difficult customer' asks for a story with a result. 'Why are you leaving your current job?' asks you to be positive about the future, not negative about the past.", "پرسش‌های مصاحبه درخواست‌های غیرمستقیم‌اند. «Tell me about a difficult customer» داستانی با نتیجه می‌خواهد. «Why are you leaving your current job?» می‌خواهد دربارهٔ آینده مثبت باشی، نه دربارهٔ گذشته منفی."),
                ("Listen for the conditions attached to the offer: salary, start date, probation, hours. Those details decide whether 'we'd like to offer you the position' is good news.", "به شرط‌های پیوستِ پیشنهاد گوش کن: حقوق، تاریخ شروع، دورهٔ آزمایشی، ساعت کار. همین جزئیات تعیین می‌کند که «we'd like to offer you the position» خبر خوبی هست یا نه."),
            ],
            [
                ("'Tell me about yourself.' — 'I've worked in customer service for six years, and I'm looking for a role with more responsibility.'", "«از خودت بگو.» — «شش سال در خدمات مشتری کار کرده‌ام و دنبال نقشی با مسئولیت بیشتر هستم»."),
                ("'Why do you want this job?' — 'Because your team works with schools, and that is the part of my last job I enjoyed most.'", "«چرا این کار را می‌خواهی؟» — «چون تیم شما با مدرسه‌ها کار می‌کند و همین بخش، محبوب‌ترین بخش کار قبلی‌ام بود»."),
                ("'We'd like to offer you the position, starting on the first of next month.'", "«می‌خواهیم این سمت را به تو پیشنهاد دهیم، از اول ماه آینده»."),
            ],
            [
                listen("So, tell me about your last job. — I worked in a hotel for four years, and for the last two I was responsible for the night team of six people.", "What was the candidate responsible for?", "متقاضی مسئول چه چیزی بود؟", ["the whole hotel", "the night team of six", "the restaurant", "the accounts"], 1,
                       "He was responsible for the night team of six.", "او مسئول تیم شب شش‌نفره بود."),
                listen("So, tell me about your last job. — I worked in a hotel for four years, and for the last two I was responsible for the night team of six people.", "How long did he work at the hotel?", "چند سال در هتل کار کرد؟", ["two years", "four years", "six years", "ten years"], 1,
                       "'I worked in a hotel for four years.'", "«چهار سال در هتل کار کردم»."),
            ],
            [
                listen("Why do you want to leave your current job? — I've learned a lot there, but there is no chance of promotion, and I'd like to work on bigger projects.", "What is his reason for leaving?", "دلیل رفتنش چیست؟", ["the salary is too low", "no chance of promotion", "he dislikes his manager", "the office is far"], 1,
                       "He names the lack of promotion, not a complaint about people.", "او نبود امکان ارتقا را می‌گوید، نه شکایت از آدم‌ها."),
                listen("We'd like to offer you the position. The salary is what we discussed, there is a three-month probation period, and the hours are nine to five, Monday to Friday.", "What is the probation period?", "دورهٔ آزمایشی چقدر است؟", ["one month", "three months", "six months", "one year"], 1,
                       "'A three-month probation period.'", "«دورهٔ آزمایشی سه‌ماهه»."),
                mcq("'We'd like to offer you the position' means ___.", "«We'd like to offer you the position» یعنی ___.", ["you are invited to a second interview", "you are being hired", "the position is closed", "they will call you next year"], 1,
                    "The offer is the decision to hire.", "offer همان تصمیم به استخدام است."),
                mcq("Which answer is best for 'What is your greatest weakness?'", "بهترین پاسخ برای «What is your greatest weakness?» کدام است؟", ["I have no weaknesses.", "I sometimes take on too much, so I'm learning to say no.", "My boss is terrible.", "I don't like working."], 1,
                    "A real weakness plus what you are doing about it.", "یک ضعف واقعی همراه با کاری که برایش می‌کنی."),
            ],
        ),
    ],
)
