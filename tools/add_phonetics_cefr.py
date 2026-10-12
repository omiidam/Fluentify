#!/usr/bin/env python3
"""Adds B2-C2 phonetics sections: rhythm, professional prosody, fast reduction.

A1-B2 teaches the sounds; these teach the *music* — thought groups, stress
position, and the reductions that only appear at full speed.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "phonetics.json"

NEW = [
{
 "id": "rhythm",
 "icon": "🎼",
 "level": "B2",
 "title": {"en": "Rhythm & thought groups", "fa": "ریتم و گروه‌های فکری"},
 "blurb": {
   "en": "English is a stress-timed language: the important words land on the beat and everything else gets crushed between them. Get this right and people will call you 'natural' before you finish the sentence.",
   "fa": "انگلیسی زبانی ضربه‌ای است: کلمات مهم روی ضربه می‌نشینند و بقیه بین آن‌ها فشرده می‌شوند. این را درست بگیری و قبل از تمام شدن جمله به تو می‌گویند بومی حرف می‌زنی."},
 "tip": {
   "en": "One main stress per information group. Say the group, pause, say the next one. Never put equal weight on every word.",
   "fa": "در هر گروه اطلاعات فقط یک تکیه اصلی بگذار. یک گروه را بگو، مکث کن، گروه بعدی. هرگز به همه کلمات وزن یکسان نده."},
 "groups": [
  {"name": {"en": "Where the beat lands", "fa": "ضربه کجا می‌نشیند"},
   "rows": [
    {"ip": "content words", "sub": "noun · verb · adjective · adverb", "say": "I bought a new car last week.", "fa": "ماشین نو خریدم — روی «خریدم» و «نو» ضربه بزن.", "note": "function words ride in between, unstressed"},
    {"ip": "stress shift", "sub": "when a word becomes the verb", "say": "I can run ten kilometres.", "fa": "می‌توانم ده کیلومتر بدوم — «run» برجسته می‌شود.", "words": "light·to light · second·a second · present·to present"},
    {"ip": "unstressed words", "sub": "they vanish", "say": "Would you like to come?", "fa": "می‌آیی؟ — of, to, would تقریباً حذف می‌شوند."},
    {"ip": "chunking", "sub": "phrase > word > sound", "say": "I'd like to book a table for two.", "fa": "می‌خواهم میز دو نفره رزرو کنم — چهار گروه."},
    {"ip": "weak + strong", "sub": "the rhythm pattern", "say": "Can you see the sea?", "fa": "می‌بینی دریا را؟ — CAN you SEE the SEA."},
    {"ip": "overlong groups", "sub": "split them", "say": "When I arrived, the meeting had already started.", "fa": "وقتی رسیدم | جلسه شروع شده بود — دو گروه."}]},
  {"name": {"en": "Practice it", "fa": "تمرین کنید"},
   "rows": [
    {"ip": "clap it", "sub": "clap on stressed words only", "say": "I would really like to help you.", "fa": "واقعاً دوست دارم کمکت کنم — سه ضربه."},
    {"ip": "record yourself", "sub": "compare with the original", "say": "Reading fluently is a matter of practice.", "fa": "روان خواندن نتیجه تمرین است."},
    {"ip": "don't over-pause", "sub": "short pauses, not silences", "say": "Well, I mean, it depends, doesn't it?", "fa": "خب، یعنی، بستگی دارد، نه؟"},
    {"ip": "sentence stress", "sub": "one new idea = one beat", "say": "That's a good idea. But it needs work.", "fa": "ایده خوبی است. | اما کار می‌برد."}]},
 ]},
{
 "id": "prosody_pro",
 "icon": "🎤",
 "level": "C1",
 "title": {"en": "Professional prosody", "fa": "لحن حرفه‌ای"},
 "blurb": {
   "en": "Presenting, selling, persuading — the melody does as much work as the words. These patterns make you sound prepared rather than merely correct.",
   "fa": "ارائه، متقاعد کردن، مذاکره — آهنگ به اندازه کلمات کار می‌کند. این الگوها تو را آماده نشان می‌دهند، نه فقط درست."},
 "tip": {
   "en": "Slow down and drop your pitch on the words that matter. Speed and rising pitch signal nervousness, not confidence.",
   "fa": "روی کلمات مهم کند شو و زیر بمان. سرعت بالا و لحن صعودی نشانه اضطراب است، نه اعتماد به نفس."},
 "groups": [
  {"name": {"en": "Presenting", "fa": "ارائه"},
   "rows": [
    {"ip": "signpost", "sub": "pause, then drop", "say": "Three things happened last quarter.", "fa": "سه اتفاق افتاد — مکث، سپس افت."},
    {"ip": "the number", "sub": "isolated and loud", "say": "Revenue rose by forty per cent.", "fa": "درآمد چهل درصد رشد کرد — روی عدد تأکید کن."},
    {"ip": "contrast", "sub": "the other half falls", "say": "Costs rose. Profits fell.", "fa": "هزینه‌ها بالا رفت. | سود پایین آمد."},
    {"ip": "closing", "sub": "fall, then hold", "say": "That is where we are today.", "fa": "اینجاییم که امروز هستیم — پایین و ثابت."}]},
  {"name": {"en": "Persuading & managing", "fa": "متقاعد کردن و مدیریت"},
   "rows": [
    {"ip": "hedged decline", "sub": "rise, then firm drop", "say": "I see your point, though…", "fa": "نکته‌تان را می‌بینم، اما…"},
    {"ip": "confident", "sub": "low and level", "say": "We can deliver this by Friday.", "fa": "می‌توانیم تا جمعه تحویل دهیم — یکنواخت و پایین."},
    {"ip": "excuse", "sub": "flat and slightly rising", "say": "That won't work for the team.", "fa": "برای تیم مناسب نیست — بدون تنش."},
    {"ip": "good news", "sub": "rise, level, hold", "say": "We have a new offer on the table.", "fa": "پیشنهاد جدیدی داریم — بالا، سپس ثابت."},
    {"ip": "bad news", "sub": "small sigh, then level", "say": "The supplier has withdrawn.", "fa": "تأمین‌کننده انصراف داده است."},
    {"ip": "disagreement", "sub": "never end on a rise", "say": "I understand, but I see it differently.", "fa": "درک می‌کنم، اما نظرم فرق دارد — آخرش پایین."}]},
 ]},
{
 "id": "fast_reduction",
 "icon": "💨",
 "level": "C2",
 "title": {"en": "Full-speed reduction", "fa": "کاهش صدا در سرعت کامل"},
 "blurb": {
   "en": "At native speed, unstressed syllables lose their vowels entirely. If you pronounce every syllable you will sound slow — and slightly foreign, however good your accent is.",
   "fa": "در سرعت بومی، هجاهای بی‌فشار واکشان را کامل از دست می‌دهند. اگر همه هجاها را تلفظ کنی، کند به‌نظر می‌رسی — و هرچقدر لهجه‌ات خوب باشد، کمی بیگانه."},
 "tip": {
   "en": "Syllables you never stress never keep a full vowel. \"Every\" is two beats, but \"everywhere\" is closer to two and a half.",
   "fa": "هجایی که هرگز رویش تکیه نمی‌کنی، واک کاملش را نگه نمی‌دارد. «هر» دو ضربه است، اما «همه‌جا» نزدیک دو‌ونیم است."},
 "groups": [
  {"name": {"en": "Common reductions", "fa": "کاهش‌های پرتکرار"},
   "rows": [
    {"ip": "of /əv/ → (v)", "sub": "often just a breath", "say": "a couple of hours", "fa": "چند ساعت — و در عمل تقریباً حذف می‌شود."},
    {"ip": "to /tə/ → (t)", "sub": "used to → 'juːstə'", "say": "I used to live there.", "fa": "آنجا زندگی می‌کردم — فشرده می‌شود."},
    {"ip": "and → n", "sub": "just a nasal", "say": "bread and butter", "fa": "نان و کره — «and» فقط یک ن می‌شود."},
    {"ip": "for → fə", "sub": "one syllable", "say": "what are you waiting for?", "fa": "منتظر چی هستی؟ — همه در هم ادغام می‌شوند."},
    {"ip": "-ing → ŋ", "sub": "no vowel at all", "say": "I'm not going.", "fa": "نمی‌روم — «ing» فقط یک ن است."},
    {"ip": "-ed → d / t", "sub": "gone entirely", "say": "we walked", "fa": "راه رفتیم — پسوند حذف می‌شود."},
    {"ip": "final stops", "sub": "just a glottal click", "say": "that right?", "fa": "درسته؟ — تلفظ انفجاری کوتاه."},
    {"ip": "the → ðə", "sub": "or just /ə/", "say": "the other one", "fa": "آن یکی دیگر — «the» تقریباً حذف می‌شود."}]},
  {"name": {"en": "Where to stop reducing", "fa": "کجا دیگر کم نکن"},
   "rows": [
    {"ip": "content words", "sub": "keep every sound", "say": "Reorganisation is unavoidable.", "fa": "بازسازی سازمان اجتناب‌ناپذیر است — محتوا کامل."},
    {"ip": "numbers & names", "sub": "always clear", "say": "Room seven, please.", "fa": "اتاق هفت، لطفاً."},
    {"ip": "negatives", "sub": "don't lose the contrast", "say": "I said no, not maybe.", "fa": "گفتم نه، نه شاید — تفاوت حیاتی است."},
    {"ip": "instructions", "sub": "clarity beats speed", "say": "Turn left after the bridge.", "fa": "بعد از پل بپیچ چپ — دستور باید واضح بماند."},
    {"ip": "first time", "sub": "say it fully", "say": "Could you say that again?", "fa": "می‌توانید دوباره بگویید؟ — آهسته و کامل."}]},
 ]},
]


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    secs = data["sections"]
    have = {s["id"] for s in secs}
    for s in NEW:
        if s["id"] in have:
            print(f"  skip {s['id']}")
            continue
        secs.append(s)
        rows = sum(len(g["rows"]) for g in s["groups"])
        print(f"  + {s['level']:3} {s['id']:18} {len(s['groups'])} groups / {rows} rows")
    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(len(g.get("rows", [])) for s in secs for g in s["groups"])
    print(f"\nphonetics now {len(secs)} sections / {total} rows")


if __name__ == "__main__":
    main()