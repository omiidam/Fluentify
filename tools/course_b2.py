#!/usr/bin/env python3
"""The B2 course, assembled from its eight units and its examination."""

from course_kit import course
from course_b2_exam import PAPER
from course_b2_units1 import U1, U2
from course_b2_units2 import U3, U4
from course_b2_units3 import U5, U6
from course_b2_units4 import U7, U8

COURSE = course(
    ("B2 · Upper-Intermediate", "B2 · فراتر از متوسط"),
    (
        "Eight units for a learner who can explain and now has to argue: the perfect and perfect continuous in narrative, the third and mixed conditionals, causatives, reduced relatives, inversion, wish and participles. Twenty-four lessons across all six skills, a final examination of 33 marks, and B1 is assumed.",
        "هشت درس‌نامه برای زبانی که توضیح می‌دهد و حالا باید استدلال کند: حال کامل و کامل استمراری در روایت، شرطی سوم و مختلط، سببی، موصولی کوتاه‌شده، جابه‌جایی، wish و وجه وصفی. بیست‌وچهار درس در هر شش مهارت، آزمون پایانی ۳۳ نمره‌ای، با فرض دانستن B1.",
    ),
    [U1, U2, U3, U4, U5, U6, U7, U8],
    PAPER,
)
