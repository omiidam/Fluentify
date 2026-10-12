#!/usr/bin/env python3
"""Extends listening.json from 8 to 16 sentences per CEFR band.

Level design follows the CEFR listening descriptors: A1 short fixed phrases,
A2 simple questions, B1 longer everyday exchanges, B2 fast connected speech
with contractions and weak forms, C1 abstract and professional content,
C2 dense native-speed material. Every sentence is bilingual.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "listening.json"

ADD = {
"A1": [
 ("Good morning. Did you sleep well?", "صبح بخیر. خوب خوابیدی؟"),
 ("My name is Sara. I am from Tehran.", "اسمم سارا است. اهل تهرانم."),
 ("I would like a glass of water, please.", "یک لیوان آب می‌خواهم، لطفاً."),
 ("What time does the shop open?", " مغازه چه ساعتی باز می‌شود؟"),
 ("It is very cold today.", "امروز خیلی سرد است."),
 ("Can you help me, please?", "می‌توانید کمکم کنید؟"),
 ("I have two brothers and one sister.", "دو برادر و یک خواهر دارم."),
 ("Where is the bus stop?", "ایستگاه اتوبوس کجاست؟"),
 ("Thank you very much.", "خیلی ممنونم."),
 ("I am hungry. What is for dinner?", "گرسنه‌ام. برای شام چه داریم؟"),
 ("She is my teacher. She is very kind.", "او معلم من است. خیلی مهربان است."),
 ("I like tea with sugar.", "چای با قند دوست دارم."),
 ("The door is over there.", "در آنجا است."),
 ("How are you today?", "امروز چطوری؟"),
 ("I go to work by bus.", "با اتوبوس به سر کار می‌روم."),
 ("See you tomorrow.", "فردا می‌بینمت."),
],
"A2": [
 ("Could you tell me where the pharmacy is?", "می‌توانید بگویید داروخانه کجاست؟"),
 ("I usually get up at seven in the morning.", "معمولاً هفت صبح بیدار می‌شوم."),
 ("We are meeting at the restaurant at eight.", "ساعت هشت در رستوران همدیگر را می‌بینیم."),
 ("That jacket is too expensive for me.", "آن ژاکت برای من خیلی گران است."),
 ("I have never been to this city before.", "تا حالا به این شهر نیامده‌ام."),
 ("My brother studies medicine in Isfahan.", "برادرم در اصفهان پزشکی می‌خواند."),
 ("Do you want to watch a film tonight?", "می‌خواهی امشب فیلم ببینیم؟"),
 ("The weather is getting colder every day.", "هوا هر روز سردتر می‌شود."),
 ("I lost my ticket on the train.", "بلیتم را در قطار گم کردم."),
 ("Could you speak more slowly, please?", "می‌توانید لطفاً آهسته‌تر حرف بزنید؟"),
 ("She has lived here for three years.", "او سه سال است اینجا زندگی می‌کند."),
 ("We usually have lunch at one o'clock.", "معمولاً ساعت یک ناهار می‌خوریم."),
 ("How much does it cost altogether?", "در مجموع چند می‌شود؟"),
 ("I need to buy a present for my mother.", "باید برای مادرم یک هدیه بخرم."),
 ("The shop is closed on Thursdays.", "مغازه پنج‌شنبه‌ها تعطیل است."),
 ("He works in a hospital near here.", "او در بیمارستانی نزدیک اینجا کار می‌کند."),
],
"B1": [
 ("I've been working on this project for about six months now.", "حدود شش ماه است روی این پروژه کار می‌کنم."),
 ("If you book before Friday, you'll get a discount.", "اگر قبل از جمعه رزرو کنی، تخفیف می‌گیری."),
 ("Could you let me know as soon as possible?", "می‌توانی هرچه زودتر به من اطلاع بدهی؟"),
 ("I'm afraid the last train has already left.", "متأسفانه آخرین قطار رفته است."),
 ("We've been looking for a new flat for months.", "ماه‌هاست دنبال خانه جدید می‌گردییم."),
 ("It's worth waiting — the queue moves quickly.", "ارزش انتظار دارد — صف سریع جلو می‌رود."),
 ("I'd rather not go out; I'm feeling under the weather.", "ترجیح می‌دهم بیرون نروم؛ حالم خوب نیست."),
 ("She offered to help, which was really kind of her.", "او پیشنهاد کمک داد که خیلی لطف بود."),
 ("The results haven't come through yet.", "نتایج هنوز نرسیده است."),
 ("I turned it down because the hours were terrible.", "رد کردم چون ساعت کاری خیلی بد بود."),
 ("Could we move the meeting to Thursday?", "می‌توانیم جلسه را به پنج‌شنبه منتقل کنیم؟"),
 ("They've been renovating the building since March.", "از مارس دارد ساختمان را بازسازی می‌کنند."),
 ("I was going to call you, but I completely forgot.", "قصد داشتم زنگ بزنم، اما کاملاً فراموش کردم."),
 ("Let me know if you'd rather meet somewhere else.", "بگو اگر جای دیگری را ترجیح می‌دهی."),
 ("It's a bit of a squeeze, but we can make it work.", "کمی فشرده است، اما می‌توانیم جورش کنیم."),
 ("He runs his own business now.", "حالا کسب‌وکار خودش را اداره می‌کند."),
],
"B2": [
 ("I'd have appreciated a bit more notice, to be honest.", "راستش کمی بیشتر اطلاع‌رسانی را ترجیح می‌دادم."),
 ("The deadline's been moved up, so we're going to have to prioritise.", "مهلت جلو آمده، پس باید اولویت‌بندی کنیم."),
 ("You'd be better off getting it checked before you sign.", "بهتر است قبل از امضا بگیری بررسی‌اش کنند."),
 ("It's not exactly what we had in mind, but it might work.", "دقیقاً آنچه در ذهن داشتیم نیست، اما شاید جواب بدهد."),
 ("I've run out of time, so I'll have to leave it for tomorrow.", "وقت‌ام تمام شده، پس باید بگذارمش برای فردا."),
 ("We're still waiting to hear back from the landlord.", "هنوز منتظر پاسخ صاحبخانه هستیم."),
 ("Could you fill me in on what happened?", "می‌توانی ماجرا را برایم توضیح بدهی؟"),
 ("There's no point rearranging it now; the damage is done.", "الان جابه‌جا کردنش فایده‌ای ندارد؛ کار از دست رفته."),
 ("I'd rather not commit to anything until I've seen the figures.", "تا ارقام را نبینم ترجیح می‌دهم به چیزی متعهد نشوم."),
 ("She ended up taking on more work than she could handle.", "در نهایت بیش از توانش کار برداشت."),
 ("Let's play it by ear and decide in the morning.", "بگذاریم ببینیم و صبح تصمیم بگیریم."),
 ("He's always been one to put things off until the last minute.", "او همیشه کارها را تا لحظه آخر به تعویق می‌انداخته."),
 ("It cost us more than we'd budgeted for, but it's done.", "بیشتر از بودجه‌ای که داشتیم برایمان هزینه برد، اما تمام شد."),
 ("I couldn't help overhearing what you said to her.", "ناخواسته حرفی را که به او زدی شنیدم."),
 ("The sooner we agree on the terms, the better for everyone.", "هرچه زودتر بر سر شرایط توافق کنیم، برای همه بهتر است."),
 ("You'll find it hard to get used to the pace here.", "سخت می‌شود به ریتم اینجا عادت کنی."),
 ("Given the circumstances, I think we can live with it.", "با توجه به شرایط، فکر می‌کنم می‌توانیم با آن کنار بیاییم."),
],
"C1": [
 ("The findings broadly support the original hypothesis.", "یافته‌ها از فرضیه اصلی تا حدی پشتیبانی می‌کنند."),
 ("There's a growing consensus that the policy needs revising.", "اجماع روزبه‌روزی وجود دارد که سیاست نیاز به بازنگری دارد."),
 ("I'd rather we reserved judgement until we've seen the full data.", "ترجیح می‌دهم تا دیدن داده‌های کامل قضاوت نکنیم."),
 ("The proposal is, at best, a partial solution to a systemic problem.", "این پیشنهاد حداکثر راه‌حلی جزئی برای مشکلی سیستمی است."),
 ("It stands to reason that the costs will exceed the original estimate.", "بدیهی است که هزینه‌ها از برآورد اولیه بیشتر خواهد شد."),
 ("We'd be well advised to consult the stakeholders before deciding.", "مشورت با ذی‌نفعان پیش از تصمیم‌گیری عاقلانه است."),
 ("The correlation is striking, though causation cannot be inferred.", "همبستگی چشمگیر است، اما نمی‌توان علیت را نتیجه گرفت."),
 ("She's consistently under-delivered against her stated commitments.", "او بارها نتوانسته به تعهدات اعلام‌شده‌اش عمل کند."),
 ("A more nuanced approach would serve everyone better.", "رویکرد دقیق‌تری به همه بهتر خدمت می‌کند."),
 ("The premise, however reasonable, remains empirically untested.", "این مقدمه، هرچقدر هم منطقی، از نظر تجربی آزمون‌نشده است."),
 ("Subject to the usual caveats, the intervention appears effective.", "با ملاحظه همان ملاحظات همیشگی، مداخله مؤثر به نظر می‌رسد."),
 ("We should be candid about what we don't yet understand.", "باید صریح باشیم درباره آنچه هنوز درک نکرده‌ایم."),
],
"C2": [
 ("That, to borrow an expression, is a bridge too far.", "با قرض گرفتن یک تعبیر، این دیگر زیاده‌روی است."),
 ("The ostensibly neutral figures, on closer inspection, tell another story.", "ارقام به‌ظاهر بی‌طرف، با بررسی دقیق‌تر، داستان دیگری می‌گویند."),
 ("He was being scrupulously diplomatic, to the point of evasiveness.", "او با دقت دیپلماتیک رفتار می‌کرد، تا حدی که طفره‌گو می‌شد."),
 ("It is not so much a question of resources as of priorities.", "این بیش از آنکه سؤال منابع باشد، سؤال اولویت‌هاست."),
 ("The rationale, however persuasive, rests on shaky ground.", "منطق آن، هرچقدر هم متقاعدکننده، بر پایه‌ای سست بنا شده."),
 ("She has an unwelcome habit of restating the obvious at length.", "او عادت ناخوشایندی دارد که بدیهیات را با طولانی تکرار کند."),
 ("Taken in isolation, the figures are unremarkable; the trend is not.", "به‌تنهایی ارقام چیز خاصی نیستند؛ روند هست."),
 ("There is a tacit assumption here that few would defend.", "اینجا فرضی ضمنی وجود دارد که کمتر کسی از آن دفاع می‌کند."),
 ("His candour is admirable; his judgement, less so.", "صراحتش ستودنی است؛ قضاوتش کمتر."),
 ("The correlation, though statistically robust, remains merely suggestive.", "همبستگی، هرچند آماری‌محکم، همچنان تنها نشانه‌ای است."),
 ("One might contend that the argument proves rather more than it proves.", "می‌توان استدلال کرد که این بحث بیش از آنچه می‌رساند، ادعا می‌کند."),
 ("Whatever the merits of the case, the timing could hardly be worse.", "هرچه ارزش‌های پرونده باشد، زمان‌بندی نمی‌تواند بدتر باشد."),
],
}

BLOBS = {
 "A1": "Short, fixed phrases — repeat them until they come out automatically. / جمله‌های کوتاه و ثابت — تا خودکار شوند تکرار کن.",
 "A2": "Everyday questions and answers you will use this week. / سؤال‌های روزمره‌ای که همین هفته استفاده می‌کنی.",
 "B1": "Longer, connected everyday speech. Listen for the weak forms. / گفتار روزمره طولانی‌تر؛ به شکل‌های ضعیف گوش کن.",
 "B2": "Natural speed with contractions and linking. / سرعت طبیعی با انقباض‌ها و اتصال کلمات.",
 "C1": "Abstract, professional and academic content. / محتوای انتزاعی، حرفه‌ای و دانشگاهی.",
 "C2": "Dense, native-speed material with irony and subtext. / متراکم و بومی، با کنایه و متن پنهان.",
}


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    levels = data["levels"]
    added = 0
    for lv in levels:
        new = ADD.get(lv["id"], [])
        have = {s["en"] for s in lv["sentences"]}
        added_n = 0
        for en, fa in new:
            if en in have:
                continue
            lv["sentences"].append({"en": en, "fa": fa})
            added_n += 1
        if BLOBS.get(lv["id"]):
            lv["blurb"]["en"] = BLOBS[lv["id"]].split(" / ")[0]
            lv["blurb"]["fa"] = BLOBS[lv["id"]].split(" / ")[1]
        print(f"  + {lv['id']:3} {len(lv['sentences']):2} sentences (+{added_n})")
        added += added_n
    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nadded {added} sentences · listening now "
          f"{sum(len(l['sentences']) for l in levels)} total")


if __name__ == "__main__":
    main()