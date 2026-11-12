#!/usr/bin/env python3
"""Write chapter twenty of the grammar book into books.json.

    python3 tools/chapter20.py

Chapter twenty of *Understanding and Using English Grammar* is Conditional
Sentences and Wishes. The book shipped with one placeholder section for it; this
replaces it with the chapter's ten charts, written out like chapters three to
nineteen: the rule, the form, examples in both languages, three guided exercises
and a three-question check for each.

The sentences and explanations are written for this app. The book is the
reference text, and nothing in this file is transcribed from it.

It is idempotent: chapter twenty is always rebuilt from this script.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "books.json"

CHAPTER = "Chapter 20"


def ex(prompt, answer, why_en, why_fa):
    return {"prompt": prompt, "answer": answer, "why_en": why_en, "why_fa": why_fa}


def q(text, options, answer, why_en, why_fa):
    assert answer in options and len(options) == 3, text
    return {"q": text, "options": options, "answer": answer,
            "why_en": why_en, "why_fa": why_fa}


LESSONS = [
    {
        "section": "20-1",
        "title": "The forms used in conditional sentences: an overview",
        "title_fa": "شکل‌های به‌کاررفته در جمله‌های شرطی: نگاه کلی",
        "use_en": "A conditional sentence has two parts: the condition after if and the result in the main clause. The present tense is used for a real condition, the past for an unreal one, and the past perfect for something that cannot change. The result takes will, would or would have to match. In none of the three does the if-clause take will, would or would have.",
        "use_fa": "جملهٔ شرطی دو بخش دارد: شرط پس از if و نتیجه در جملهٔ اصلی. زمان حال برای شرط واقعی، گذشته برای شرط غیرواقعی و گذشتهٔ کامل برای چیزی که تغییرپذیر نیست به کار می‌رود. نتیجه با will، would یا would have هماهنگ می‌شود. در هیچ‌یک از این سه، جملهٔ if فعل will، would یا would have نمی‌گیرد.",
        "form_en": "if + present, will · if + past, would · if + had + pp, would have + pp",
        "examples": [
            {"en": "If it rains, we will stay home.",
             "fa": "اگر باران ببارد خانه می‌مانیم."},
            {"en": "If it rained, we would stay home.",
             "fa": "اگر باران می‌بارید خانه می‌ماندیم."},
            {"en": "If it had rained, we would have stayed home.",
             "fa": "اگر باران باریده بود خانه مانده بودیم."},
        ],
        "exercises": [
            ex("If I had more time, I ___ travel more. (unreal present)", "would",
               "An unreal present condition takes would in the result.",
               "شرط غیرواقعی حال در نتیجه would می‌گیرد."),
            ex("If she ___ harder, she would pass. (unreal present)", "studied",
               "The if-clause of an unreal present takes the past.",
               "جملهٔ if در شرط غیرواقعی حال گذشته می‌گیرد."),
            ex("If we had left earlier, we ___ have caught the train. (unreal past)", "would",
               "An unreal past result is would have plus the participle.",
               "نتیجهٔ غیرواقعی گذشته would have و اسم مفعول است."),
        ],
        "exam": [
            q("Which form appears in an if-clause?",
              ["The present", "Will", "Would have"], "The present",
              "The if-clause never takes will or would.",
              "جملهٔ if هرگز will یا would نمی‌گیرد."),
            q("If he ___ the answer, he would tell us.",
              ["knew", "knows", "had known"], "knew",
              "The unreal present condition takes the past form.",
              "شرط غیرواقعی حال شکل گذشته می‌گیرد."),
            q("If they had called, we ___ have waited.",
              ["would", "will", "did"], "would",
              "The unreal past result is would have waited.",
              "نتیجهٔ غیرواقعی گذشته would have waited است."),
        ],
    },
    {
        "section": "20-2",
        "title": "Real conditions in the present or future",
        "title_fa": "شرط‌های واقعی در حال یا آینده",
        "use_en": "A real condition describes something possible, and the speaker does not know yet whether it will happen: if you finish early, we will go out. The if-clause takes the present tense and the result takes will, can or an imperative. The same clause also works for a general truth, where both parts stay in the present: if you heat water, it boils.",
        "use_fa": "شرط واقعی چیزی ممکن را می‌گوید و گوینده هنوز نمی‌داند رخ می‌دهد یا نه: if you finish early, we will go out. جملهٔ if فعل حال می‌گیرد و نتیجه will، can یا جملهٔ امری. همین جمله برای حقیقت کلی هم کار می‌کند، جایی که هر دو بخش در حال می‌مانند: if you heat water, it boils.",
        "form_en": "if + present, + will / can / imperative  ·  if + present, + present (general truth)",
        "examples": [
            {"en": "If you finish early, we will go out.",
             "fa": "اگر زود تمام کنی بیرون می‌رویم."},
            {"en": "If you heat water, it boils.",
             "fa": "اگر آب را گرم کنی می‌جوشد."},
            {"en": "If you see her, tell her I called.",
             "fa": "اگر او را دیدی بگو زنگ زدم."},
        ],
        "exercises": [
            ex("If I ___ time, I will visit you. (real condition)", "have",
               "A real condition takes the present tense.",
               "شرط واقعی فعل حال می‌گیرد."),
            ex("If it ___ tomorrow, the match will be cancelled. (real condition)", "snows",
               "The present carries the future meaning in the if-clause.",
               "فعل حال در جملهٔ if معنای آینده را می‌رساند."),
            ex("If you press this button, the machine ___ . (general truth)", "starts",
               "A general truth keeps both parts in the present.",
               "حقیقت کلی هر دو بخش را در حال نگه می‌دارد."),
        ],
        "exam": [
            q("If she ___ , we will start without her.",
              ["does not come", "will not come", "did not come"], "does not come",
              "A real condition stays in the present.",
              "شرط واقعی در حال می‌ماند."),
            q("If you ___ the ice, it melts.",
              ["heat", "will heat", "heated"], "heat",
              "A general truth takes the present in both clauses.",
              "حقیقت کلی در هر دو جمله حال می‌گیرد."),
            q("Which sentence is correct?",
              ["If they arrive late, we will wait.", "If they will arrive late, we will wait.",
               "If they arriving late, we will wait."], "If they arrive late, we will wait.",
              "No will in the condition.",
              "در شرط هیچ will نمی‌آید."),
        ],
    },
    {
        "section": "20-3",
        "title": "Unreal conditions in the present or future",
        "title_fa": "شرط‌های غیرواقعی در حال یا آینده",
        "use_en": "An unreal condition describes something that is not true now, or is imagined: if I had a car, I would drive to work. The past form in the if-clause signals the unreality, and the result takes would, could or might. With be, the careful form is were for every subject: if I were you. The speaker is not stating a fact but imagining a different one.",
        "use_fa": "شرط غیرواقعی چیزی را می‌گوید که اکنون درست نیست یا تصور می‌شود: if I had a car, I would drive to work. شکل گذشته در جملهٔ if ناواقعی بودن را نشان می‌دهد و نتیجه would، could یا might می‌گیرد. با فعل be شکل دقیق برای همهٔ فاعل‌ها were است: if I were you. گوینده واقعیتی نمی‌گوید بلکه واقعیتی دیگر را تصور می‌کند.",
        "form_en": "if + past, + would / could / might + base verb  ·  if I were you",
        "examples": [
            {"en": "If I had a car, I would drive to work.",
             "fa": "اگر ماشین داشتم با آن سر کار می‌رفتم."},
            {"en": "If I were you, I would apologize.",
             "fa": "جای تو بودم عذرخواهی می‌کردم."},
            {"en": "If she knew the truth, she might be angry.",
             "fa": "اگر حقیقت را می‌دانست شاید عصبانی می‌شد."},
        ],
        "exercises": [
            ex("If I ___ you, I would take the job. (be, careful form)", "were",
               "Were is the unreal form of be for every subject.",
               "were شکل غیرواقعی be برای همهٔ فاعل‌ها است."),
            ex("If we ___ closer, we could walk to work. (live)", "lived",
               "The unreal present takes the past form.",
               "حال غیرواقعی شکل گذشته می‌گیرد."),
            ex("If he ___ more, he would finish on time. (practise)", "practised",
               "The past form marks the unreality.",
               "شکل گذشته ناواقعی بودن را نشان می‌دهد."),
        ],
        "exam": [
            q("If I ___ rich, I would travel the world.",
              ["were", "am", "will be"], "were",
              "The unreal present of be is were.",
              "شکل غیرواقعی be همان were است."),
            q("If she had more time, she ___ learn the piano.",
              ["would", "will", "has"], "would",
              "The result of an unreal condition takes would.",
              "نتیجهٔ شرط غیرواقعی would می‌گیرد."),
            q("Which sentence is unreal?",
              ["If I knew her number, I would call.", "If I know her number, I will call.",
               "If I have her number, I call."], "If I knew her number, I would call.",
              "The past in the if-clause marks an imagined present.",
              "گذشته در جملهٔ if حال تصوری را نشان می‌دهد."),
        ],
    },
    {
        "section": "20-4",
        "title": "Unreal conditions in the past",
        "title_fa": "شرط‌های غیرواقعی در گذشته",
        "use_en": "An unreal past condition describes something that did not happen, and the speaker imagines the different result: if I had studied, I would have passed. The if-clause takes had plus the past participle and the result takes would have plus the past participle. The regret is in the sentence, so these forms appear whenever someone looks back at a missed chance.",
        "use_fa": "شرط غیرواقعی گذشته چیزی را می‌گوید که رخ نداد و گوینده نتیجهٔ دیگر را تصور می‌کند: if I had studied, I would have passed. جملهٔ if فعل had و اسم مفعول می‌گیرد و نتیجه would have و اسم مفعول. پشیمانی در خود جمله است، پس این شکل‌ها هرگاه کسی به فرصت ازدست‌رفته نگاه کند ظاهر می‌شوند.",
        "form_en": "if + had + past participle, + would have + past participle",
        "examples": [
            {"en": "If I had studied, I would have passed.",
             "fa": "اگر درس خوانده بودم قبول شده بودم."},
            {"en": "If they had left earlier, they would not have missed the flight.",
             "fa": "اگر زودتر راه افتاده بودند پرواز را از دست نمی‌دادند."},
            {"en": "She would have called if she had known.",
             "fa": "اگر می‌دانست زنگ می‌زد."},
        ],
        "exercises": [
            ex("If we had taken a taxi, we ___ have arrived on time. (result)", "would",
               "The unreal past result is would have arrived.",
               "نتیجهٔ غیرواقعی گذشته would have arrived است."),
            ex("If he ___ told me, I would have helped. (if-clause)", "had",
               "The if-clause of an unreal past takes had.",
               "جملهٔ if در گذشتهٔ غیرواقعی had می‌گیرد."),
            ex("If she had seen the sign, she would have ___ . (stop)", "stopped",
               "The result keeps the past participle.",
               "نتیجه اسم مفعول را نگه می‌دارد."),
        ],
        "exam": [
            q("If I ___ the answer, I would have said something.",
              ["had known", "knew", "have known"], "had known",
              "The unreal past condition takes had known.",
              "شرط غیرواقعی گذشته had known می‌گیرد."),
            q("They would have won if they ___ harder.",
              ["had trained", "trained", "train"], "had trained",
              "The if-clause keeps the past perfect.",
              "جملهٔ if گذشتهٔ کامل را نگه می‌دارد."),
            q("Which sentence is about the past?",
              ["If he had called, I would have answered.", "If he called, I would answer.",
               "If he calls, I will answer."], "If he had called, I would have answered.",
              "Had plus the participle places the condition in the past.",
              "had و اسم مفعول شرط را به گذشته می‌برد."),
        ],
    },
    {
        "section": "20-5",
        "title": "Progressive forms in conditional sentences",
        "title_fa": "شکل‌های استمراری در جمله‌های شرطی",
        "use_en": "A progressive form puts the emphasis on an action in progress: if it is raining, we will stay in; if she were living here, we would meet often; if he had been driving, he would have seen the sign. The conditional keeps the same pattern and simply uses the progressive inside it. The be verb is the part that carries the tense, and the -ing form stays.",
        "use_fa": "شکل استمراری تأکید را بر کار در جریان می‌گذارد: if it is raining, we will stay in؛ if she were living here, we would meet often؛ if he had been driving, he would have seen the sign. جملهٔ شرطی همان الگو را نگه می‌دارد و فقط استمراری را درون آن می‌آورد. فعل be زمان را حمل می‌کند و شکل ing- می‌ماند.",
        "form_en": "if + is / was / were / had been + -ing, + result clause",
        "examples": [
            {"en": "If it is raining, we will stay inside.",
             "fa": "اگر باران می‌بارد داخل می‌مانیم."},
            {"en": "If she were living here, we would meet often.",
             "fa": "اگر اینجا زندگی می‌کرد بیشتر همدیگر را می‌دیدیم."},
            {"en": "If he had been driving, he would have seen the sign.",
             "fa": "اگر رانندگی می‌کرد تابلو را دیده بود."},
        ],
        "exercises": [
            ex("If they ___ working, we will not disturb them. (present progressive)", "are",
               "The present progressive takes are plus the -ing form.",
               "حال استمراری are و شکل ing- می‌گیرد."),
            ex("If I ___ working there, I would know the manager. (unreal present)", "were",
               "The unreal progressive takes were plus -ing.",
               "استمراری غیرواقعی were و ing- می‌گیرد."),
            ex("If she had ___ waiting, she would have seen him. (past progressive)", "been",
               "The past progressive takes had been plus -ing.",
               "گذشتهٔ استمراری had been و ing- می‌گیرد."),
        ],
        "exam": [
            q("If it ___ raining, the match will be delayed.",
              ["is", "will be", "were"], "is",
              "A real progressive condition takes is raining.",
              "شرط استمراری واقعی is raining می‌گیرد."),
            q("If he were ___ here, he would help us.",
              ["living", "lived", "live"], "living",
              "The unreal progressive keeps the -ing form.",
              "استمراری غیرواقعی شکل ing- را نگه می‌دارد."),
            q("If I had been ___ more carefully, I would not have crashed.",
              ["driving", "drive", "driven"], "driving",
              "The past progressive takes had been driving.",
              "گذشتهٔ استمراری had been driving است."),
        ],
    },
    {
        "section": "20-6",
        "title": "Mixed time in conditional sentences",
        "title_fa": "زمان مختلط در جمله‌های شرطی",
        "use_en": "The two halves of a conditional can sit in different times when the meaning needs it: if I had taken the job, I would be in Dubai now. The condition is in the past and the result in the present, so the if-clause takes had plus the participle and the result takes would plus the base verb. The other direction also occurs: if she were more careful, she would not have broken it.",
        "use_fa": "دو نیمهٔ جملهٔ شرطی می‌توانند در زمان‌های متفاوت بنشینند وقتی معنا چنین می‌خواهد: if I had taken the job, I would be in Dubai now. شرط در گذشته و نتیجه در حال است، پس جملهٔ if فعل had و اسم مفعول می‌گیرد و نتیجه would و فعل ساده. جهت دیگر هم رخ می‌دهد: if she were more careful, she would not have broken it.",
        "form_en": "if + had + pp, + would + base verb (past condition, present result)",
        "examples": [
            {"en": "If I had taken the job, I would be in Dubai now.",
             "fa": "اگر آن کار را پذیرفته بودم اکنون در دبی بودم."},
            {"en": "If she were more careful, she would not have broken it.",
             "fa": "اگر دقیق‌تر بود آن را نمی‌شکست."},
            {"en": "If he had studied medicine, he would be a doctor today.",
             "fa": "اگر پزشکی خوانده بود امروز پزشک بود."},
        ],
        "exercises": [
            ex("If I had saved more, I ___ be on holiday now. (present result)", "would",
               "A present result after a past condition takes would.",
               "نتیجهٔ حال پس از شرط گذشته would می‌گیرد."),
            ex("If he were taller, he would have ___ the team. (past result)", "joined",
               "A past result keeps would have plus the participle.",
               "نتیجهٔ گذشته would have و اسم مفعول را نگه می‌دارد."),
            ex("If they had booked earlier, they ___ be here now. (present result)", "would",
               "The mixed condition joins a past cause to a present result.",
               "شرط مختلط علت گذشته را به نتیجهٔ حال می‌پیوندد."),
        ],
        "exam": [
            q("If I had known you were coming, I ___ have cooked.",
              ["would", "will", "would be"], "would",
              "Both parts are in the past, so would have cooked.",
              "هر دو بخش گذشته‌اند، پس would have cooked."),
            q("If she had left earlier, she ___ be at the airport now.",
              ["would", "will", "had"], "would",
              "The result is in the present, so would be.",
              "نتیجه در حال است، پس would be."),
            q("Which sentence mixes the times?",
              ["If I had studied, I would be an engineer now.",
               "If I studied, I would be an engineer.", "If I study, I will be an engineer."],
              "If I had studied, I would be an engineer now.",
              "A past condition with a present result is the mixed form.",
              "شرط گذشته با نتیجهٔ حال شکل مختلط است."),
        ],
    },
    {
        "section": "20-7",
        "title": "Omitting if: were I you, had I known",
        "title_fa": "حذف if: were I you، had I known",
        "use_en": "In formal writing the if can disappear and the auxiliary moves in front of the subject: were I you, had I known, should you need help. The meaning does not change and the sentence becomes more formal. The pattern only works when the if-clause contains were, had or should; it cannot be done with an ordinary verb, so if I knew cannot become knew I.",
        "use_fa": "در نوشتار رسمی if می‌تواند حذف شود و فعل کمکی به پیش از فاعل برود: were I you، had I known، should you need help. معنا عوض نمی‌شود و جمله رسمی‌تر می‌شود. این الگو تنها وقتی ممکن است که جملهٔ if فعل were، had یا should داشته باشد و با فعل معمولی ممکن نیست، پس if I knew به knew I تبدیل نمی‌شود.",
        "form_en": "were + subject · had + subject + past participle · should + subject + verb",
        "examples": [
            {"en": "Were I you, I would accept the offer.",
             "fa": "جای تو بودم پیشنهاد را می‌پذیرفتم."},
            {"en": "Had I known, I would have called.",
             "fa": "اگر می‌دانستم زنگ می‌زدم."},
            {"en": "Should you need help, call this number.",
             "fa": "اگر کمک لازم داشتی با این شماره تماس بگیر."},
        ],
        "exercises": [
            ex("___ I known the answer, I would have said it. (omitted if)", "Had",
               "Had plus the participle replaces if I had.",
               "had و اسم مفعول جای if I had را می‌گیرد."),
            ex("___ I you, I would wait. (omitted if)", "Were",
               "Were plus the subject replaces if I were.",
               "were و فاعل جای if I were را می‌گیرد."),
            ex("___ you need anything, let me know. (formal omitted if)", "Should",
               "Should plus the subject replaces if you should.",
               "should و فاعل جای if you should را می‌گیرد."),
        ],
        "exam": [
            q("___ he studied more, he would pass.",
              ["If", "Were", "Had"], "If",
              "An ordinary verb cannot lose if.",
              "فعل معمولی نمی‌تواند if را از دست بدهد."),
            q("___ I been there, I would have helped.",
              ["Had", "Have", "Were"], "Had",
              "Had I been replaces if I had been.",
              "had I been جای if I had been را می‌گیرد."),
            q("Which sentence omits if correctly?",
              ["Were I rich, I would travel.", "Was I rich, I would travel.",
               "Am I rich, I would travel."], "Were I rich, I would travel.",
              "Only were inverts for an unreal present.",
              "تنها were برای حال غیرواقعی جابه‌جا می‌شود."),
        ],
    },
    {
        "section": "20-8",
        "title": "Implied conditions",
        "title_fa": "شرط‌های تلویحی",
        "use_en": "Not every condition needs an if-clause. A phrase with with, without, in case of, but for or otherwise can carry it: without your help, we would have failed means if you had not helped, we would have failed. The result clause keeps its would form, which is the signal that a condition is understood rather than stated.",
        "use_fa": "هر شرطی جملهٔ if لازم ندارد. عبارت‌هایی با with، without، in case of، but for یا otherwise می‌توانند آن را حمل کنند: without your help, we would have failed یعنی if you had not helped, we would have failed. جملهٔ نتیجه شکل would خود را نگه می‌دارد و همین نشانهٔ آن است که شرط فهمیده می‌شود نه گفته.",
        "form_en": "without / but for / with + noun, + would clause  ·  the condition is implied",
        "examples": [
            {"en": "Without your help, we would have failed.",
             "fa": "بدون کمک تو شکست خورده بودیم."},
            {"en": "But for the traffic, we would be there by now.",
             "fa": "اگر ترافیک نبود تا حالا آنجا بودیم."},
            {"en": "With a little more practice, you could win.",
             "fa": "با کمی تمرین بیشتر می‌توانستی ببری."},
        ],
        "exercises": [
            ex("___ your advice, I would have made a mistake. (implied condition)", "Without",
               "Without plus a noun replaces if you had not.",
               "without و اسم جای if you had not را می‌گیرد."),
            ex("___ for the rain, the match would have continued. (implied condition)", "But",
               "But for introduces the imagined exception.",
               "but for استثنای تصوری را می‌آورد."),
            ex("With more time, we ___ finish the project. (result)", "could",
               "An implied condition keeps a modal result.",
               "شرط تلویحی نتیجهٔ وجهی را نگه می‌دارد."),
        ],
        "exam": [
            q("___ your help, we would not have finished.",
              ["Without", "Although", "So that"], "Without",
              "The implied condition is a phrase, not a clause.",
              "شرط تلویحی عبارت است نه جمله."),
            q("But for the delay, we ___ be home now.",
              ["would", "will", "are"], "would",
              "The result of an implied condition takes would.",
              "نتیجهٔ شرط تلویحی would می‌گیرد."),
            q("Which sentence has an implied condition?",
              ["With more money, we could move.", "We have more money, so we moved.",
               "We moved because we had money."], "With more money, we could move.",
              "The with-phrase states the condition without if.",
              "عبارت with شرط را بی if می‌گوید."),
        ],
    },
    {
        "section": "20-9",
        "title": "Wishes about the present and the past",
        "title_fa": "آرزو دربارهٔ حال و گذشته",
        "use_en": "Wish plus the past describes a present situation the speaker would like to change: I wish I had more time. Wish plus the past perfect looks back at something that cannot now be changed: I wish I had studied harder. The pattern mirrors the unreal condition: the past form signals that the wish is not a fact, and no will or would appears in the wish clause itself.",
        "use_fa": "wish با گذشته وضعیت حال را توصیف می‌کند که گوینده می‌خواهد عوض شود: I wish I had more time. wish با گذشتهٔ کامل به چیزی نگاه می‌کند که دیگر تغییرپذیر نیست: I wish I had studied harder. الگو آینهٔ شرط غیرواقعی است: شکل گذشته نشان می‌دهد آرزو واقعیت نیست و در خود جملهٔ آرزو will یا would نمی‌آید.",
        "form_en": "wish + past (present wish)  ·  wish + had + past participle (past regret)",
        "examples": [
            {"en": "I wish I had more time.",
             "fa": "ای کاش وقت بیشتری داشتم."},
            {"en": "I wish I had studied harder.",
             "fa": "ای کاش بیشتر درس خوانده بودم."},
            {"en": "She wishes she lived closer to work.",
             "fa": "آرزو می‌کند نزدیک‌تر به محل کارش زندگی می‌کرد."},
        ],
        "exercises": [
            ex("I wish I ___ taller. (present wish)", "were",
               "A present wish about be takes were.",
               "آرزوی حال دربارهٔ be شکل were می‌گیرد."),
            ex("He wishes he ___ the job. (past regret)", "had taken",
               "A past regret takes had plus the participle.",
               "پشیمانی گذشته had و اسم مفعول می‌گیرد."),
            ex("They wish they ___ more money. (present wish)", "had",
               "The present wish uses the past form of have.",
               "آرزوی حال شکل گذشتهٔ have را می‌گیرد."),
        ],
        "exam": [
            q("I wish I ___ how to swim.",
              ["knew", "know", "will know"], "knew",
              "A present wish takes the past form.",
              "آرزوی حال شکل گذشته می‌گیرد."),
            q("She wishes she ___ to the party last night.",
              ["had gone", "went", "has gone"], "had gone",
              "A wish about the past takes the past perfect.",
              "آرزو دربارهٔ گذشته گذشتهٔ کامل می‌گیرد."),
            q("Which sentence is a past regret?",
              ["I wish I had called her.", "I wish I could call her.",
               "I hope I call her."], "I wish I had called her.",
              "Had called looks back at a missed action.",
              "had called به کاری نکرده در گذشته نگاه می‌کند."),
        ],
    },
    {
        "section": "20-10",
        "title": "Wishes about the future and wish + would",
        "title_fa": "آرزو دربارهٔ آینده و wish + would",
        "use_en": "When the wish is about someone else's behaviour and the speaker wants it to change, the pattern is wish plus would: I wish he would call. When the wish is about the speaker's own future ability, could is used: I wish I could help. Wish plus would expresses impatience as often as hope, so it is not a polite way to ask someone for something.",
        "use_fa": "وقتی آرزو دربارهٔ رفتار شخص دیگری است و گوینده می‌خواهد عوض شود، الگو wish و would است: I wish he would call. وقتی آرزو دربارهٔ توانایی آیندهٔ خودِ گوینده است could به کار می‌رود: I wish I could help. wish و would به همان اندازه که امید، بی‌تابی را هم بیان می‌کند، پس راه مؤدبانه‌ای برای درخواست از کسی نیست.",
        "form_en": "wish + person + would + base verb  ·  wish + could + base verb",
        "examples": [
            {"en": "I wish he would call me.",
             "fa": "ای کاش به من زنگ می‌زد."},
            {"en": "I wish I could help you.",
             "fa": "ای کاش می‌توانستم کمکت کنم."},
            {"en": "She wishes it would stop raining.",
             "fa": "آرزو می‌کند باران بند بیاید."},
        ],
        "exercises": [
            ex("I wish you ___ listen to me. (someone else's habit)", "would",
               "A wish about another person's behaviour takes would.",
               "آرزو دربارهٔ رفتار دیگری would می‌گیرد."),
            ex("I wish I ___ speak French. (own ability)", "could",
               "A wish about ability takes could.",
               "آرزو دربارهٔ توانایی could می‌گیرد."),
            ex("They wish the noise ___ stop. (future wish)", "would",
               "A wish for a change in a situation takes would.",
               "آرزوی تغییر وضعیت would می‌گیرد."),
        ],
        "exam": [
            q("I wish it ___ warmer tomorrow.",
              ["would be", "will be", "is"], "would be",
              "A wish about the future takes would.",
              "آرزوی آینده would می‌گیرد."),
            q("She wishes she ___ come to the party.",
              ["could", "can", "will"], "could",
              "A wish about ability takes could.",
              "آرزوی توانایی could می‌گیرد."),
            q("Which wish is about someone else's behaviour?",
              ["I wish he would be quieter.", "I wish I were quieter.",
               "I wish I had been quieter."], "I wish he would be quieter.",
              "Would signals a wish about another person.",
              "would آرزو دربارهٔ شخص دیگر را نشان می‌دهد."),
        ],
    },
]


def main() -> int:
    data = json.loads(BOOKS.read_text(encoding="utf-8"))
    book = next(b for b in data["books"] if b.get("kind") == "grammar")

    old = [l for l in book["lessons"] if l.get("chapter") == CHAPTER]
    assert old, "chapter twenty is not in the book"

    lessons = []
    for lesson in book["lessons"]:
        if lesson.get("chapter") == CHAPTER:
            if lesson is old[0]:
                for item in LESSONS:
                    lessons.append({
                        "n": 0, "title": item["title"], "title_fa": item["title_fa"],
                        "chapter": CHAPTER, "section": item["section"],
                        "use_en": item["use_en"], "use_fa": item["use_fa"],
                        "form_en": item["form_en"], "examples": item["examples"],
                        "exercises": item["exercises"], "exam": item["exam"],
                    })
            continue
        lessons.append(lesson)

    for i, lesson in enumerate(lessons, 1):
        lesson["n"] = i
    book["lessons"] = lessons

    size = len(lessons)

    BOOKS.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")
    print(f"chapter twenty: {len(LESSONS)} charts, {size} structures in the book")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
