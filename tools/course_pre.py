#!/usr/bin/env python3
"""The Pre-A1 course, assembled from its six units and its examination.

This is the level before A1: letters and sounds, the first forty words, the
verb to be, one and many, where things are, what you like, and the shape of a
day. A learner who finishes it can introduce themselves, ask for something in
a shop, and say what they do.
"""

from course_kit import course
from course_pre_exam import PAPER
from course_pre_units1 import U1, U2
from course_pre_units2 import U3, U4
from course_pre_units3 import U5, U6

COURSE = course(
    ("Pre-A1 · First words", "Pre-A1 · نخستین واژه‌ها"),
    (
        "Six units for someone starting from nothing: saying hello, giving a "
        "name and a country, counting and naming the days, pointing at people "
        "and things, ordering food, and describing a day. Twenty-four short "
        "lessons across all six skills, and a final examination of 33 marks "
        "made of the same simple items in a different order.",
        "شش درس‌نامه برای کسی که از صفر شروع می‌کند: سلام کردن، گفتن نام و "
        "کشور، شمردن و نام‌بردن از روزها، اشاره به آدم‌ها و چیزها، سفارش "
        "خوراکی و توصیف یک روز. بیست‌وچهار درس کوتاه در هر شش مهارت و آزمون "
        "پایانی ۳۳ نمره‌ای از همان اقلام ساده با ترتیبی دیگر.",
    ),
    [U1, U2, U3, U4, U5, U6],
    PAPER,
)
