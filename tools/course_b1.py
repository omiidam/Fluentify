#!/usr/bin/env python3
"""The B1 course, assembled from its eight units and its examination."""

from course_kit import add_lessons, course
from course_b1_exam import PAPER
from course_b1_extra import EXTRA
from course_b1_units1 import U1, U2
from course_b1_units2 import U3, U4
from course_b1_units3 import U5, U6
from course_b1_units4 import U7, U8

UNITS = [U1, U2, U3, U4, U5, U6, U7, U8]
add_lessons(UNITS, EXTRA)

COURSE = course(
    ("B1 · Intermediate", "B1 · متوسط"),
    (
        "Eight units for a learner who can already describe and now has to "
        "explain: the perfect against the past, two kinds of conditional, the "
        "passive, relative clauses, reported speech, habits that ended and the "
        "modals of deduction. Thirty-two lessons, each unit closing with "
        "something the learner has to perform — a story told aloud, an "
        "application, a process heard, a review read, a complaint written. A "
        "final examination of 33 marks, and A2 is assumed.",
        "هشت درس‌نامه برای زبانی که توصیف می‌کند و حالا باید توضیح بدهد: حال "
        "کامل در برابر گذشته، دو نوع شرطی، مجهول، بندهای موصولی، نقل قول، "
        "عادت‌های تمام‌شده و افعال وجهی استنباط. سی‌ودو درس که هر درس‌نامه با "
        "کاری تمام می‌شود که زبان‌آموز باید انجامش دهد — داستانی با صدای بلند، "
        "درخواست شغلی، فرایندی شنیدنی، نقدی خواندنی، شکایتی نوشتنی. آزمون "
        "پایانی ۳۳ نمره‌ای، با فرض دانستن A2.",
    ),
    UNITS,
    PAPER,
)
