#!/usr/bin/env python3
"""The A2 course, assembled from its eight units and its examination."""

from course_kit import add_lessons, course
from course_a2_exam import PAPER
from course_a2_extra import EXTRA
from course_a2_units1 import U1, U2
from course_a2_units2 import U3, U4
from course_a2_units3 import U5, U6
from course_a2_units4 import U7, U8

UNITS = [U1, U2, U3, U4, U5, U6, U7, U8]
add_lessons(UNITS, EXTRA)

COURSE = course(
    ("A2 · Elementary", "A2 · پایه"),
    (
        "Eight units that take the past, the present perfect, the future and "
        "the conditional in turn, with the vocabulary and the skills that "
        "make each one usable. Thirty-two lessons: every unit ends with a "
        "message, a conversation, a label or a plan that uses the grammar it "
        "has just taught. A final examination of 33 marks, and no lesson that "
        "repeats A1.",
        "هشت درس‌نامه که یکی‌یکی گذشته، حال کامل، آینده و شرطی را می‌آورد، "
        "همراه واژگان و مهارت‌هایی که هر کدام را قابل استفاده می‌کند. سی‌ودو "
        "درس: هر درس‌نامه با پیام، گفت‌وگو، برچسب یا طرحی تمام می‌شود که همان "
        "گرامر تازه را به کار می‌برد. آزمون پایانی ۳۳ نمره‌ای و هیچ درسی که "
        "A1 را تکرار کند.",
    ),
    UNITS,
    PAPER,
)
