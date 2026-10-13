#!/usr/bin/env python3
"""Round 1 harness fixes: the advanced words a learner actually asks about.

Harness round 1 showed `translate <word>` failing for exactly the kind of
word that shows up in B2–C2 reading — resilient, ubiquitous, ephemeral,
pragmatic… The vocabulary had the everyday nouns but not the words that make
you read a newspaper. This adds them, plus the small-talk phrasings the
learner actually types.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- vocabulary
NEW_WORDS = {
    "advanced_adjectives": (
        "C1", "Advanced adjectives", "صفت‌های پیشرفته",
        "Advanced adjectives", "صفت‌های سطح بالا",
        ["advanced adjectives", "describing qualities", "fine distinctions",
         "high level adjectives"],
        ["صفت پیشرفته", "توصیف صفات", "صفات سطح بالا"],
        [("resilient", "تاب‌آور"), ("ubiquitous", "همه‌جا حاضر"), ("ephemeral", "کوتاه‌عمر"),
         ("candid", "رک‌گو / صادقانه"), ("meticulous", "سخت‌گیر در جزئیات"),
         ("pragmatic", "عمل‌گرا"), ("tenacious", "سرسخت"), ("magnitude", "بزرگی و اهمیت"),
         ("nuance", "ظرافت معنا"), ("sceptical", "شکاک"), ("compelling", "قانع‌کننده"),
         ("discreet", "محتاط در رازداری"), ("lavish", "سخاوتمندانه / تجملی"),
         ("mundane", "روزمره و بی‌هیجان"), ("obscure", "مبهم و ناشناخته"),
         ("profound", "عمیق و تأثیرگذار"), ("redundant", "زائد و تکراری"),
         ("subtle", "ظریف"), ("tedious", "خسته‌کننده"), ("vivid", "زنده و پررنگ"),
         ("austere", "ساده و درون‌گرا"), ("benevolent", "نوع‌دوستانه"),
         ("candidly", "صریحانه"), ("cynical", "بدبین درباره همه"), ("diligent", "مجتهد"),
         ("eloquent", "خوش‌بیان"), ("frugal", "کم‌خرج"), ("gregarious", "جمع‌گرا"),
         ("impartial", "بی‌طرف"), ("indifferent", "بی‌تفاوت"), ("intrepid", "بی‌باک"),
         ("lucid", "روشن و گویا"), ("naive", "ساده‌لوح"), ("obstinate", "سرکش"),
         ("perpetual", "همیشگی"), ("quaint", "قدیمی و دلپذیر")],
    ),
    "academic_vocab": (
        "C1", "Academic & research words", "واژه‌های دانشگاهی",
        "Academic research vocabulary", "واژه‌های پژوهش دانشگاهی",
        ["academic vocabulary", "research words", "study words", "thesis vocabulary"],
        ["واژه های پژوهش", "واژه های مقاله", "کلمات دانشگاهی"],
        [("hypothesis", "فرضیه"), ("methodology", "روش‌شناسی"), ("empirical", "تجربی"),
         ("quantify", "کمی‌سازی کردن"), ("correlation", "همبستگی"), ("anomaly", "ناهنجاری"),
         ("paradigm", "الگوی فکری"), ("proliferation", "تکثیر و گسترش"),
         ("discrepancy", "ناهمخوانی"), ("coherence", "انسجام"), ("validity", "روایی"),
         ("replicate", "بازتولید پژوهش"), ("conflate", "یکی گرفتن"),
         ("juxtapose", "کنار هم گذاشتن"), ("delineate", "ترسیم کردن مرزها"),
         ("exacerbate", "بدتر کردن"), ("mitigate", "کاهش دادن"), ("substantiate", "اثبات کردن"),
         ("contradict", "تناقض داشتن با"), ("incorporate", "ادغام کردن"),
         ("allocate", "تخصیص دادن"), ("derive from", "مشتق شدن از"),
         ("attribute to", "نسبت دادن به"), ("underpin", "پایه‌گذار بودن"),
         ("articulate", "بیان روشن"), ("elucidate", "روشن کردن"),
         ("scrutinise", "به دقت بررسی کردن"), ("synthesise", "ترکیب و یکپارچه کردن")],
    ),
    "business_vocab": (
        "B2", "Work & business words", "واژه‌های کار و تجارت",
        "Office and business vocabulary", "واژه‌های محیط کار",
        ["business words", "office vocabulary", "work vocabulary", "meeting words"],
        ["واژه های کار", "واژه های اداری", "کلمات محیط کار"],
        [("agenda", "دستور جلسه"), ("minutes", "صورت‌جلسه"), ("deliverable", "خروجی قابل تحویل"),
         ("milestone", "نقطه عطف"), ("stakeholder", "ذی‌نفع"), ("deadline", "مهلت نهایی"),
         ("bandwidth", "ظرفیت کاری"), ("procurement", "تأمین"), ("forecast", "پیش‌بینی"),
         ("turnover", "گردش مالی"), ("margin", "حاشیه سود"), ("invoice", "صورتحساب"),
         ("reimburse", "بازپرداخت کردن"), ("escalate", "ارجاع به بالاتر"),
         ("sign off", "تأیید نهایی"), ("streamline", "ساده‌سازی فرایند"),
         ("prioritise", "اولویت‌بندی کردن"), ("delegate", "واگذار کردن"),
         ("negotiate", "مذاکره کردن"), ("leverage", "بهره‌برداری از"),
         ("onboarding", "ورود کارمند جدید"), ("workload", "حجم کار"),
         ("appraisal", "ارزیابی عملکرد"), ("probation", "دوره آزمایشی"),
         ("overtime", "اضافه‌کاری"), ("payroll", "حقوق و دستمزد"),
         ("contract", "قرارداد"), ("compliance", "رعایت مقررات")],
    ),
}

# ---------------------------------------------------------------- small talk
SMALL_TALK_KEYWORDS = {
    "how_are_you": ["how r u", "how're you", "how you doing", "how is it going",
                    "hows it going", "how are u", "چطوری", "چطوری؟", "حالت چطوره"],
    "user_stressed": ["im stressed", "i'm stressed", "i am stressed", "stressed",
                      "under pressure", "anxious", "i feel anxious", "استرس دارم",
                      "اضطراب دارم", "under stress"],
    "user_sick": ["i feel sick", "im sick", "feel ill", "i'm ill", "not feeling well",
                  "i feel unwell", "sick", "ill", "حالم خوب نیست", "بیمارم",
                  "م feel sick"],
    "weather": ["what is the weather", "whats the weather", "weather like",
                "how is the weather", "is it going to rain", "will it rain",
                "هوا چطوره", "هوا چطور است", "باران میباره"],
    "meaning": ["what does this word mean", "what does that mean", "what does it mean",
                "what does this mean", "whats the meaning", "یعنی چی",
                "معنی این چیه", "این یعنی چی"],
    "help": ["how does this work", "what can i do", "commands", "what are the sections",
             "چیکار کنم", "چه کارهایی میتونم بکنم", "چطور کار میکنه"],
}


def main() -> None:
    g_path = ROOT / "glossary.json"
    glossary = json.loads(g_path.read_text(encoding="utf-8"))["domains"]

    added = 0
    for key, spec in NEW_WORDS.items():
        level, label_en, label_fa, list_en, list_fa, kw_en, kw_fa, words = spec
        if key in glossary:
            print(f"  skip {key}")
            continue
        glossary[key] = {
            "label": {"en": label_en, "fa": label_fa},
            "list_label": {"en": list_en, "fa": list_fa},
            "level": level,
            "keywords": {"en": kw_en, "fa": kw_fa},
            "words": [list(w) for w in words],
        }
        added += len(words)
        print(f"  + {level} {key:22} {len(words)} words")

    # the new banks must appear in a panel group
    groups = glossary.setdefault("_groups", [])
    covered = {d for g in groups for d in g["domains"]}
    missing = [k for k in NEW_WORDS if k not in covered]
    if missing:
        groups.append({
            "id": "academic_pro",
            "en": "Academic & professional — B2 → C2",
            "fa": "دانشگاهی و حرفه‌ای — B2 تا C2",
            "domains": missing,
        })
        print(f"  + UI group with {len(missing)} domains")

    g_path.write_text(
        json.dumps({"domains": glossary}, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(len(d["words"]) for k, d in glossary.items() if k != "_groups")
    print(f"\nvocabulary now {len(glossary) - 1} domains / {total} words (+{added})")

    # ---------------------------------------------------------------- intents
    m_path = ROOT / "memory.json"
    memory = json.loads(m_path.read_text(encoding="utf-8"))
    for intent in memory["intents"]:
        extra = SMALL_TALK_KEYWORDS.get(intent["name"])
        if not extra:
            continue
        for lang, words in (("en", extra), ("fa", extra)):
            have = intent["keywords"].setdefault(lang, [])
            for w in words:
                if w not in have:
                    have.append(w)
        print(f"  ~ {intent['name']}: +{len(extra)} keywords")
    m_path.write_text(json.dumps(memory, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()