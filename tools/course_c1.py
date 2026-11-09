#!/usr/bin/env python3
"""The C1 course, assembled from its eight units and its examination."""

from course_kit import course
from course_c1_exam import PAPER
from course_c1_units1 import U1, U2
from course_c1_units2 import U3, U4
from course_c1_units3 import U5, U6
from course_c1_units4 import U7, U8

COURSE = course(
    ("C1 · Advanced", "C1 · پیشرفته"),
    (
        "Eight units for a learner who argues fluently and now has to argue precisely: clefting and information structure, modal perfects and hedging, nominalisation, ellipsis, reporting passives, the formal subjunctive, advanced relatives and emphatic inversion. Twenty-four lessons across all six skills, a final examination of 33 marks, and B2 is assumed.",
        "هشت درس‌نامه برای زبانی که روان استدلال می‌کند و حالا باید دقیق استدلال کند: cleft و ساختار اطلاعات، وجهی کامل و احتیاط، اسم‌سازی، حذف، مجهول نقل، وجه شرطی رسمی، موصولی پیشرفته و جابه‌جایی تأکیدی. بیست‌وچهار درس در هر شش مهارت، آزمون پایانی ۳۳ نمره‌ای، با فرض دانستن B2.",
    ),
    [U1, U2, U3, U4, U5, U6, U7, U8],
    PAPER,
)
