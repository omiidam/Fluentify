"""Top-ups: the lessons the other six batches left one item short.

A pair list replaces what is there, so the two lessons below carry both of
their pairs rather than only the new one.
"""

P = {
    "subject_verb_agreement": dict(
        mistakes=[
            ("The number of students are rising.",
             "The number of students is rising.",
             "the subject is the number; of students only describes it, exactly "
             "as with one of the students.",
             "فاعل number است و of students فقط توضیح آن است.",
             "agreement"),
        ],
    ),
    "there_is_there_are": dict(
        mistakes=[
            ("There are a book on the table.",
             "There is a book on the table.",
             "a book is singular, so the verb is is, however long the rest of "
             "the sentence gets.",
             "book مفرد است، پس is می‌آید.",
             "agreement"),
        ],
    ),
    "wh_questions": dict(
        mistakes=[
            ("How much is it cost?",
             "How much does it cost?",
             "cost is the verb here, so the question needs does; how much is not "
             "the subject of anything.",
             "cost فعل است و does می‌خواهد؛ how much فاعل نیست.",
             "question form"),
        ],
    ),
    "simple_future": dict(
        mistakes=[
            ("I am going to will travel next week.",
             "I am going to travel next week.",
             "going to and will both mark the future; one of them is enough.",
             "going to و will هر دو آینده‌اند؛ یکی کافی است.",
             "future form"),
        ],
    ),
    "present_progressive": dict(
        mistakes=[
            ("I am work in a bank.",
             "I am working in a bank.",
             "be needs the -ing form after it; am work is two verbs with no link.",
             "بعد از be فعل ing می‌گیرد؛ am work دو فعل بی‌ربط است.",
             "progressive form"),
            ("Does he is coming?",
             "Is he coming?",
             "be makes its own question by moving in front of the subject; does "
             "belongs to other verbs.",
             "be با جابه‌جا شدن سؤال می‌سازد؛ does مال فعل‌های دیگر است.",
             "question form"),
        ],
    ),
    "gerunds_infinitives": dict(
        mistakes=[
            ("I look forward to see you.",
             "I look forward to seeing you.",
             "the to here is a preposition, not part of an infinitive, so the "
             "verb after it takes -ing.",
             "اینجا to حرف اضافه است، پس فعل بعدش ing می‌گیرد.",
             "gerund form"),
        ],
    ),
    "purpose_reason": dict(
        mistakes=[
            ("I study English because to work abroad.",
             "I study English because I want to work abroad.",
             "because introduces a clause with its own subject and verb; an "
             "infinitive cannot follow it.",
             "بعد از because جملهٔ کامل با فاعل و فعل می‌آید، نه مصدر.",
             "purpose form"),
        ],
    ),
    "so_such_too_enough": dict(
        mistakes=[
            ("The box is too heavy that I can't lift it.",
             "The box is so heavy that I can't lift it.",
             "too goes with to (too heavy to lift) and so goes with that; the two "
             "patterns do not mix.",
             "too با to می‌آید و so با that؛ این دو ساختار با هم نمی‌آیند.",
             "so/too form"),
        ],
    ),
    "adjective_order": dict(
        pairs=[
            ("یک کیف چرمی قهوه‌ای بزرگ خریدم.",
             "I bought a big brown leather bag.",
             "I bought a big brown leather bag.",
             "size, then colour, then material; the order sounds wrong the moment "
             "two of them swap.",
             "اندازه، رنگ، جنس؛ با جابه‌جایی هر دو، ترتیب غلط می‌شود."),
            ("یک میز چوبی قدیمی خریدیم.",
             "We bought a wooden old table.",
             "We bought an old wooden table.",
             "age comes before material; the wooden old order is the one Persian "
             "speakers produce most often.",
             "سن قبل از جنس می‌آید؛ «چوبی قدیمی» رایج‌ترین ترتیب فارسی است."),
        ],
    ),
    "past_progressive": dict(
        pairs=[
            ("وقتی رسیدم، داشت غذا می‌خورد.",
             "When I arrived, he ate.",
             "When I arrived, he was eating.",
             "the longer action in the background takes was + -ing; the short one "
             "uses the simple past.",
             "کار طولانی‌تر در پس‌زمینه was + ing می‌گیرد و کار کوتاه گذشتهٔ ساده."),
            ("داشتم تلفن می‌زدم که او آمد.",
             "I phoned when he came.",
             "I was phoning when he came.",
             "without the continuous the two events look equally short, and the "
             "call stops being the background.",
             "بی استمراری هر دو کار کوتاه به نظر می‌رسند و تلفن از پس‌زمینه بیرون می‌رود."),
        ],
    ),
}
