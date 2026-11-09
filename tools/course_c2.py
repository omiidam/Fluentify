#!/usr/bin/env python3
"""The C2 course, assembled from its eight units and its examination."""

from course_kit import course
from course_c2_exam import PAPER
from course_c2_units1 import U1, U2
from course_c2_units2 import U3, U4
from course_c2_units3 import U5, U6
from course_c2_units4 import U7, U8

COURSE = course(
    ("C2 · Proficient", "C2 · تبحر"),
    (
        "Eight units for a learner who can already do everything and now has "
        "to do it precisely: end weight and given-new, hedging, understatement "
        "and irony, attribution, cohesion, fronting and clefts, and the "
        "confusables that survive a spellchecker. Thirty-two lessons across "
        "all six skills — literary and satirical reading, lectures and "
        "debates, editorials and reviews, negotiation and presentation — with "
        "a final examination of 33 marks. C2 is the end of the path: passing "
        "it completes the seven levels.",
        "هشت درس‌نامه برای زبانی که از پیش همه‌چیز می‌تواند و حالا باید دقیق "
        "انجامش دهد: وزن پایان و اطلاعات داده-تازه، احتیاط، کم‌گویی و طعنه، "
        "انتساب، انسجام، جابه‌جایی به آغاز و جمله‌های شکافته و واژه‌های "
        "اشتباه‌گرفته‌شدنی که از غلط‌یاب رد می‌شوند. سی‌ودو درس در هر شش "
        "مهارت — خواندن ادبی و طنز، سخنرانی و مناظره، سرمقاله و نقد، مذاکره و "
        "ارائه — با آزمون پایانی ۳۳ نمره‌ای. C2 پایان مسیر است: قبولی در آن "
        "هفت سطح را کامل می‌کند.",
    ),
    [U1, U2, U3, U4, U5, U6, U7, U8],
    PAPER,
)
