#!/usr/bin/env python3
"""Converts British vocabulary and usage in Fluentify's own content.

`americanize.py` handles spelling, where one word has two written forms and the
meaning cannot change. This file handles the other half of the job, where the
word itself is different: petrol/gas, queue/line, flat/apartment, and the
grammar British English prefers in these lessons (have got, shall, mustn't,
needn't, at the weekend).

Every rule here is a content decision, so each one names the sentence it
changes rather than replacing a bare word across the corpus. "Flat" is an
ordinary American adjective, "marks" is usually a verb, and "chips" is a poker
stack in an idiom, so word-level substitution would quietly break meaning.

Skipped, deliberately:
  * bbc_6min.json - BBC transcripts are quotations and keep their wording.
  * distinctions.json - it exists to compare the two standards.
  * lexicon/, nlp/, tools/.cache/ - dictionaries and cached source material,
    not Fluentify's own copy.
  * word_arch.json - a morphological dictionary keyed by headword; renaming a
    key would desynchronise its forms.
  * slang.json - an idiom bank; idioms are lexical items, not usage to convert.
  * this file itself, which contains the British forms as its rule keys.

Run with --write to convert, or --check to fail if a marker survives in the
shipped JSON.
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import americanize

ROOT = Path(__file__).parent.parent
POUND = "\u00a3"

# Sentences rewritten whole, because a word-level swap would leave the grammar
# wrong (a question form, an answer, a negation) or change the meaning.
EXACT = [
    # --- the A1 possession lesson: American "have" is the model form -------
    ('"en": "have got and possessives"', '"en": "have and possessives"'),
    ('"fa": "have got و ملکی‌ها"', '"fa": "have و ملکی‌ها"'),
    ("Say what people own with have got, and whose thing it is with my, your, his, hers.",
     "Say what people own with have and has, and whose thing it is with my, your, his, hers."),
    ("با have got بگویی کسی چه دارد و با my، your، his، hers بگویی چیزی مال کیست.",
     "با have و has بگویی کسی چه دارد و با my، your، his، hers بگویی چیزی مال کیست."),
    ("have got means the same as have: I have got a car = I have a car. The forms are "
     "I / you / we / they have got, he / she / it has got.",
     "Have is the everyday verb of ownership: I have a car. The forms are I / you / we / "
     "they have, he / she / it has. British English often says have got instead: I have got "
     "a car, she has got a dog."),
    ("have got همان have است: I have got a car = I have a car. صورت‌ها: I/you/we/they have got "
     "و he/she/it has got.",
     "have فعل روزمرهٔ دارایی است: I have a car. صورت‌ها: I/you/we/they have و he/she/it has. "
     "انگلیسی بریتانیایی اغلب به جایش have got می‌گوید: I have got a car، she has got a dog."),
    ("Say what hurts with have got: I've got a headache, a sore throat, a cough, a temperature.",
     "Say what hurts with have: I have a headache, a sore throat, a cough, a temperature."),
    ("درد را با have got بگو: I've got a headache، a sore throat، a cough، a temperature.",
     "درد را با have بگو: I have a headache، a sore throat، a cough، a temperature."),
    ("Describe three people with have got and one possession each.",
     "Describe three people with have or has and one possession each."),
    ("سه نفر را با have got و یک دارایی برای هرکدام توصیف کن.",
     "سه نفر را با have یا has و یک دارایی برای هرکدام توصیف کن."),
    ("Have got is the everyday way to say what someone owns or has: she has got two brothers. "
     "In negatives and questions it behaves like have: she hasn't got a car, has he got a phone?",
     "Have is the everyday way to say what someone owns: she has two brothers. In negatives "
     "and questions American English uses do: she doesn't have a car, does he have a phone? "
     "British English often uses have got: she has got two brothers."),
    ("have got راه روزمرهٔ گفتن دارایی است: she has got two brothers. در منفی و پرسش مثل have "
     "رفتار می‌کند: she hasn't got a car، has he got a phone?",
     "have راه روزمرهٔ گفتن دارایی است: she has two brothers. در منفی و پرسش انگلیسی آمریکایی "
     "از do استفاده می‌کند: she doesn't have a car، does he have a phone? انگلیسی بریتانیایی "
     "اغلب have got می‌گوید: she has got two brothers."),
    ("My sister has got a new phone.", "My sister has a new phone."),
    ("My brother has got a bike.", "My brother has a bike."),
    ("My parents have got a small shop.", "My parents have a small shop."),
    ("Use have got for each person, and put the thing they have at the end of the sentence.",
     "Use have or has for each person, and put the thing they have at the end of the sentence."),
    ("برای هر نفر have got به کار ببر و چیزی که دارد را در پایان جمله بگذار.",
     "برای هر نفر have یا has به کار ببر و چیزی که دارد را در پایان جمله بگذار."),
    ("Four sentences, one person each, have got correct, the object last.",
     "Four sentences, one person each, have or has correct, the object last."),
    ("چهار جمله، در هر یک یک نفر، have got درست و شیء در پایان.",
     "چهار جمله، در هر یک یک نفر، have یا has درست و شیء در پایان."),
    ("She takes has got.", "She takes has."),
    ("با she فعل has got می‌آید.", "با she فعل has می‌آید."),
    ("We takes have got.", "We takes have."),
    ("we با have got می‌آید.", "we با have می‌آید."),
    ("Third person singular takes has got.", "Third person singular takes has."),
    ("سوم‌شخص مفرد has got می‌گیرد.", "سوم‌شخص مفرد has می‌گیرد."),
    ("He takes has got.", "He takes has."),
    ("he با has got می‌آید.", "he با has می‌آید."),
    ("Which is a question with have got?", "Which is a question with have?"),
    ("کدام پرسش با have got است؟", "کدام پرسش با have است؟"),
    ("Maryam ___ got a new phone.", "Maryam ___ a new phone."),
    ("We ___ got a big garden.", "We ___ a big garden."),
    ("She ___ got two sisters.", "She ___ two sisters."),
    ("My sister ___ got a new phone.", "My sister ___ a new phone."),
    ("Have you got a smaller ___?", "Do you have a smaller ___?"),
    ("Have you got this jacket in medium?", "Do you have this jacket in medium?"),
    ("Have you got this shirt in ___?", "Do you have this shirt in ___?"),
    ("I have got two ___.", "I have two ___."),
    ("We haven't got any milk.", "We don't have any milk."),
    ("I have got an umbrella.", "I have an umbrella."),
    ("She has got a small dog.", "She has a small dog."),
    ("I have got two sisters.", "I have two sisters."),
    ("We have got a cat", "We have a cat"),
    ('"She have got a brother."', '"She have a brother."'),
    ('"My brother have got a bike."', '"My brother have a bike."'),
    ("Have you got a smaller one?", "Do you have a smaller one?"),
    ("have you got a smaller one?", "do you have a smaller one?"),
    ('"Has he got a car?"', '"Does he have a car?"'),
    ('"He has got a car?"', '"He has a car?"'),
    ('"Does he got a car?"', '"Does he has a car?"'),
    ('"She has got a brother."', '"She has a brother."'),
    ('"My brother has got a bike."', '"My brother has a bike."'),
    ('"Shall we"', '"Should we"'),
    ("Shall we", "Should we"),
    ("shall we", "should we"),
    ("Shall I", "Should I"),

    # --- obligation and absence of obligation ------------------------------
    ("Mustn't is prohibition; don't have to means it is not necessary — a completely "
     "different meaning.",
     "Must not expresses prohibition; don't have to means it is not necessary — a "
     "completely different meaning."),
    ("mustn't ممنوعیت است و don't have to یعنی لازم نیست — معنایی کاملاً متفاوت.",
     "must not ممنوعیت است و don't have to یعنی لازم نیست — معنایی کاملاً متفاوت."),
    ("A prohibition is mustn't.", "A prohibition is must not."),
    ("ممنوعیت با mustn't است.", "ممنوعیت با must not است."),
    ("Don't have to = no obligation; mustn't = prohibited.",
     "Don't have to = no obligation; must not = prohibited."),
    ("don't have to یعنی اجباری نیست؛ mustn't یعنی ممنوع است.",
     "don't have to یعنی اجباری نیست؛ must not یعنی ممنوع است."),
    ("A prohibition is mustn't; don't have to would mean it is allowed.",
     "A prohibition is must not; don't have to would mean it is allowed."),
    ("ممنوعیت با mustn't است؛ don't have to یعنی مجاز است.",
     "ممنوعیت با must not است؛ don't have to یعنی مجاز است."),
    ("prohibition is mustn't", "prohibition is must not"),
    ("needn't have (did it unnecessarily)", "didn't need to (did it unnecessarily)"),
    ("needn't have (بی‌لزوم انجام شد)", "didn't need to (بی‌لزوم انجام شد)"),
    ("You needn't have booked; the hall was empty.",
     "You didn't need to book; the hall was empty."),
    ("'You needn't have waited' means ___.", "'You didn't need to wait' means ___."),
    ("«You needn't have waited» یعنی ___.", "«You didn't need to wait» یعنی ___."),

    # --- school, work, the town -------------------------------------------
    ("The institution and its stages: primary and secondary school, higher education, a "
     "university, a college, a department, a faculty. In British English you go to university; "
     "in American English you go to college.",
     "The institution and its stages: elementary, middle and high school, higher education, a "
     "college or university, a department. In American English you go to college; British "
     "English says go to university."),
    ("نهاد و مرحله‌ها: primary و secondary school، higher education، university، college، "
     "department، faculty. در انگلیسی بریتانیایی to university و در آمریکای",
     "نهاد و مرحله‌ها: elementary، middle و high school، higher education، college یا "
     "university، department. در انگلیسی آمریکایی to college و انگلیسی بریتانیایی to university"),
    ("I met my wife at university.", "I met my wife in college."),
    ("I met my wife at university", "I met my wife in college"),
    ("We ___ in touch after university, but only by message.",
     "We ___ in touch after college, but only by message."),
    ("At university he built a body from dead parts",
     "In college he built a body from dead parts"),
    ("The pharmacy (chemist's in British English) sells medicine; a prescription is the "
     "doctor's paper you need for stronger medicine.",
     "The pharmacy, also called a drugstore, sells medicine; in British English it is the "
     "chemist's. A prescription is the doctor's paper you need for stronger medicine."),
    ("داروخانه (chemist's در انگلیسی بریتانیایی) دارو می‌فروشد؛ prescription کاغذ پزشک برای "
     "داروهای قوی‌تر است.",
     "داروخانه (در انگلیسی بریتانیایی chemist's) دارو می‌فروشد؛ prescription کاغذ پزشک برای "
     "داروهای قوی‌تر است."),
    ("The post of shop assistant", "The position of sales associate"),
    ("the post of shop assistant", "the position of sales associate"),
    ("weekend shop assistant post", "weekend sales associate position"),
    ("mostly at weekends", "mostly on weekends"),
    ("she is on holiday", "she is on vacation"),
    ("I fell behind in the second term and spent the holiday catching up.",
     "I fell behind in the second semester and spent the break catching up."),
    ("benefits (insurance, holidays)", "benefits (health insurance, paid vacation)"),
    ("before the holiday rather than after it", "before the vacation rather than after it"),
    ('"the holiday"', '"the vacation"'),
    ("After the shop closed, he took a course in accounting.",
     "After the store closed, he took a course in accounting."),
    ("She abandoned her plan to study law after one term.",
     "She abandoned her plan to study law after one semester."),
    ("Teachers evaluate progress each term.", "Teachers evaluate progress each semester."),
    ("A benevolent uncle paid for the whole term.",
     "A benevolent uncle paid for the whole semester."),

    # --- the home ---------------------------------------------------------
    ("Our flat is near the park.", "Our apartment is near the park."),
    ("There are three rooms in our flat.", "There are three rooms in our apartment."),
    ("the flat is small but lovely", "the apartment is small but lovely"),
    ("because the flat is small", "because the apartment is small"),
    ("How does she feel about the flat?", "How does she feel about the apartment?"),
    ("'The flat is small but lovely.'", "'The apartment is small but lovely.'"),
    ("This flat is cheaper than the one near the park.",
     "This apartment is cheaper than the one near the park."),
    ("keep some water in your flat for the day",
     "keep some water in your apartment for the day"),
    ("The flat is lovely and the price is fair",
     "The apartment is lovely and the price is fair"),
    ('"the flat is small"', '"the apartment is small"'),
    ("in this flat for ten years", "in this apartment for ten years"),
    ("he ___ a flat now", "he ___ an apartment now"),
    ("the flat decorated before we move in",
     "the apartment decorated before we move in"),
    ("The occupants of the flat were away.", "The occupants of the apartment were away."),
    ("An indigent family took the flat.", "An indigent family took the apartment."),
    ("The flat is the antithesis of the old house.",
     "The apartment is the antithesis of the old house."),
    ("from a flat near the port", "from an apartment near the port"),
    ("A commodious flat with two large rooms.",
     "A commodious apartment with two large rooms."),
    ("They chose the flat for its proximity to the school.",
     "They chose the apartment for its proximity to the school."),
    ("furniture for the flat", "furniture for the apartment"),
    ("The flat is both small ___ comfortable.",
     "The apartment is both small ___ comfortable."),
    ("looking for a new flat for months", "looking for a new apartment for months"),
    ("my flat ____ (paint)", "my apartment ____ (paint)"),
    ("The flat may not be sublet", "The apartment may not be sublet"),
    ("the flat may not be sublet", "the apartment may not be sublet"),
    ("rent the flat to a cousin", "rent the apartment to a cousin"),
    ("an affordable flat near work", "an affordable apartment near work"),
    ("The whole flat for that price?", "The whole apartment for that price?"),
    ("in a shared flat", "in a shared apartment"),
    ('"Renting a flat"', '"Renting an apartment"'),
    ("about a flat he has seen online", "about an apartment he has seen online"),
    ("about the flat on Green Street", "about the apartment on Green Street"),
    ("That's right, flat four.", "That's right, apartment four."),
    ("We shared a flat in our first year", "We shared an apartment in our first year"),
    ("see the flat again", "see the apartment again"),
    ("Is the flat furnished?", "Is the apartment furnished?"),
    ("moving to a bigger flat", "moving to a bigger apartment"),

    # --- the lift ---------------------------------------------------------
    ("There isn't a lift in this building.", "There isn't an elevator in this building."),
    ("The lift will also be off", "The elevator will also be off"),
    ("the lift was out of order", "the elevator was out of order"),
    ("Angry about the lift", "Angry about the elevator"),
    ("The lift was working.", "The elevator was working."),
    ("'The lift was out of order.'", "'The elevator was out of order.'"),
    ("in the lift about the building", "in the elevator about the building"),
    ("The lift is slow though.", "The elevator is slow though."),
    ("The lift isn't working again.", "The elevator isn't working again."),

    # --- the road, the train ----------------------------------------------
    ("While everyone was asking the guard what had happened",
     "While everyone was asking the conductor what had happened"),
    ("**Account A.** By three o'clock the pavement outside the office held perhaps sixty people",
     "**Account A.** By three o'clock the sidewalk outside the office held perhaps sixty people"),
    ("the pavement cools, the street looks different",
     "the sidewalk cools, the street looks different"),
    ("The pavement cools, but nobody claims the town is cool",
     "The sidewalk cools, but nobody claims the town is cool"),
    ("on the pavement at noon", "on the sidewalk at noon"),
    ("You will work one evening a fortnight, from 6 to 9 pm",
     "You will work one evening every two weeks, from 6 to 9 pm"),
    ("It is 'one evening a fortnight', not every evening.",
     "It is 'one evening every two weeks', not every evening."),
    ("the estate agent had valued the whole plot",
     "the real estate agent had valued the whole plot"),
    ("open a current account", "open a checking account"),
    ("this jumper", "this sweater"),
    ("a jumper that is the wrong size", "a sweater that is the wrong size"),
    ("A return ticket costs " + POUND + "14.60, or " + POUND + "9.20 with a railcard. "
     "Single tickets are not sold after 6 pm on Sundays.",
     "A round-trip ticket costs $14.60, or $9.20 with a discount card. One-way tickets are "
     "not sold after 6 pm on Sundays."),
    ("A return ticket costs " + POUND + "___", "A round-trip ticket costs $___"),
    ("buy the return ticket at the office", "buy the round-trip ticket at the office"),
    ("buys a return ticket at the station", "buys a round-trip ticket at the station"),
    ("The full fare, before the railcard.", "The full fare, before the discount card."),
    ("the site of an old railway yard", "the site of an old rail yard"),
    ("The railway yard", "The rail yard"),
    ("the railway came", "the railroad came"),
    ("Carriages are old, tracks are shared with freight",
     "Train cars are old, tracks are shared with freight"),
    ("Old carriages and borders still make the business difficult",
     "Old train cars and borders still make the business difficult"),
    ("Carriages are old and the tracks are shared with ___",
     "Train cars are old and the tracks are shared with ___"),
    ("old carriages, or four sets of paperwork", "old train cars, or four sets of paperwork"),

    # --- food, post, waste ------------------------------------------------
    ("A biscuit runs out of an oven", "A cookie runs out of an oven"),
    ("take the biscuit", "take the cake"),
    ("take out the rubbish", "take out the trash"),
    ("a land of sweets", "a land of candy"),
    ("surfeit of sweets", "surfeit of candy"),
    ("The dog was a menace to the postman.", "The dog was a menace to the mail carrier."),
    ("barked at the postman", "barked at the mail carrier"),

    # --- money and shops --------------------------------------------------
    ("Line is the line you wait in; changing room is where you try clothes.",
     "A line is what you wait in; a fitting room is where you try clothes."),
    ("line صفی است که در آن می‌ایستی و changing room اتاق پرو است.",
     "line صفی است که در آن می‌ایستی و fitting room اتاق پرو است."),
    ("changing room", "fitting room"),
    ("ten pounds from last week", "ten dollars from last week"),
    ("around fifteen pounds", "around fifteen dollars"),
    ("six pounds fifty", "six dollars fifty"),
    ("Nine pounds, or you can move something into your hand luggage.",
     "Nine dollars, or you can move something into your carry-on bag."),

    # --- comparison notes keep both standards, American first -------------
    ("at the weekend (BrE) / on the weekend (AmE)",
     "on the weekend (AmE) / at the weekend (BrE)"),
    ("at the weekend (بریتانیایی) / on the weekend (آمریکایی)",
     "on the weekend (آمریکایی) / at the weekend (بریتانیایی)"),
]

# Word-level rules. Each is safe across a whole sentence: the British form has
# no other common sense in this corpus.
PATTERNS = [
    (r"\bfilm's\b", "movie's", set()),
    (r"\bfilms\b", "movies", set()),
    (r"\bFilm\b", "Movie", set()),
    (r"\bFilms\b", "Movies", set()),
    (r"\bfilm\b", "movie", set()),
    (r"\bcinemas\b", "movie theaters", set()),
    (r"\bcinema\b", "movie theater", set()),
    (r"\bCinema\b", "Movie theater", set()),
    (r"\bpetrol station\b", "gas station", set()),
    (r"\bpetrol\b", "gas", set()),
    (r"\bPetrol\b", "Gas", set()),
    (r"\btimetables\b", "schedules", set()),
    (r"\btimetable\b", "schedule", set()),
    (r"\bTimetable\b", "Schedule", set()),
    (r"\bqueues\b", "lines", set()),
    (r"\bqueue\b", "line", set()),
    (r"\bQueue\b", "Line", set()),
    (r"\bpavements\b", "sidewalks", set()),
    (r"\bpavement\b", "sidewalk", set()),
    (r"\bcar parks\b", "parking lots", set()),
    (r"\bcar park\b", "parking lot", set()),
    (r"\bmotorways\b", "highways", set()),
    (r"\bmotorway\b", "highway", set()),
    (r"\bfortnights\b", "two-week periods", set()),
    (r"\bfortnight\b", "two weeks", set()),
    (r"\bpostmen\b", "mail carriers", set()),
    (r"\bpostman\b", "mail carrier", set()),
    (r"\bat the weekend\b", "on the weekend", {"grammar.json"}),
    (r"\bat weekends\b", "on weekends", set()),
    (r"\bAt weekends\b", "On weekends", set()),
    (r"\bmustn[’']t\b", "must not", set()),
    (r"\bMustn[’']t\b", "Must not", set()),
    (r"\bneedn[’']t\b", "don't need to", set()),
    (r"\bShall\b", "Should", set()),
    (r"\bshall\b", "should", set()),
    (POUND, "$", set()),
]

# Watchlist for --check. These have no second sense in Fluentify's copy, so a
# surviving hit is a hole in the conversion.
WATCH = [
    r"\bmustn[’']t\b", r"\bneedn[’']t\b", r"\bhave got\b",
    r"\bshall\b", r"\bpetrol\b", r"\bqueue\b", r"\btimetable\b",
    r"\bfortnight\b", r"\bpavement\b", r"\bcar park\b", r"\bmotorway\b",
    r"\bpostman\b", r"\brailway yard\b", r"\breturn ticket\b", POUND,
]


def convert(text: str, name: str):
    count = 0
    for old, new in EXACT:
        if old in text:
            count += text.count(old)
            text = text.replace(old, new)
    for pattern, repl, skip in PATTERNS:
        if name in skip:
            continue
        text, n = re.subn(pattern, repl, text)
        count += n
    return text, count


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    me = Path(__file__).name

    total = 0
    for path in americanize.targets():
        if path.name in americanize.QUOTED or path.name == me:
            continue
        # chatbot.py keeps the British forms as data now - BRITISH_TO_AMERICAN
        # maps "petrol" to "gas" - so converting it would rewrite its own keys.
        if path.name == "chatbot.py":
            continue
        text = path.read_text(encoding="utf-8")
        if path.name == "README.md":
            head, block, tail = americanize.readme_parts(text)
            head, n1 = convert(head, path.name)
            tail, n2 = convert(tail, path.name)
            new, n = head + block + tail, n1 + n2
        else:
            new, n = convert(text, path.name)
        if n and args.write:
            path.write_text(new, encoding="utf-8")
        if n:
            print(f"{n:5d}  {path.relative_to(ROOT)}")
            total += n
    print(("converted" if args.write else "would convert") + f" {total} occurrences")
    if args.write:
        return 0

    leftover = []
    for path in americanize.targets():
        if path.suffix != ".json" or path.name in americanize.QUOTED:
            continue
        if path.name == "word_arch.json":
            continue
        text = path.read_text(encoding="utf-8")
        for pat in WATCH:
            for m in re.finditer(pat, text, re.I):
                start = text.rfind("\n", 0, m.start()) + 1
                end = text.find("\n", m.end())
                row = text[start:end if end != -1 else len(text)]
                # A comparison lesson names the British form on purpose.
                if "British English" in row or "بریتانیایی" in row:
                    continue
                line = text.count("\n", 0, m.start()) + 1
                leftover.append((path.name, line, m.group(0)))
    if leftover:
        for name, line, hit in leftover:
            print(f"leftover: {name}:{line}: {hit}")
        return 1
    print("no British usage markers left in the shipped JSON")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
