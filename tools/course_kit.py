#!/usr/bin/env python3
"""The shape every level's course is written in.

A course in path.json is data, and the page draws any course the same way, so
the only thing that has to be right here is the shape: a unit is a title, a goal
and its lessons; a lesson is an explanation, examples, two guided questions and
four exercises; an exam is six sections. These helpers exist so a course of
twenty-four lessons is readable as content instead of as JSON punctuation, and
so the same dict is what build_path.py writes and check_path.py reads back.

Nothing here is A1, A2 or B1: `build_path.py` merges whatever courses it finds.
"""

from __future__ import annotations


def T(en: str, fa: str) -> dict:
    """A pair of languages. Every string a learner reads is one of these."""
    return {"en": en, "fa": fa}


def mcq(prompt_en, prompt_fa, options, answer, why_en, why_fa) -> dict:
    return {
        "kind": "mcq",
        "prompt": T(prompt_en, prompt_fa),
        "options": list(options),
        "answer": answer,
        "why": T(why_en, why_fa),
    }


def gap(text, answers, why_en, why_fa, hint="") -> dict:
    return {
        "kind": "gap",
        "text": text,
        "answer": list(answers),
        "why": T(why_en, why_fa),
        "hint": hint,
    }


def listen(say, prompt_en, prompt_fa, options, answer, why_en, why_fa) -> dict:
    return {
        "kind": "listen",
        "say": say,
        "prompt": T(prompt_en, prompt_fa),
        "options": list(options),
        "answer": answer,
        "why": T(why_en, why_fa),
    }


def say(text, fa) -> dict:
    return {"kind": "say", "say": text, "fa": fa}


def write(task_en, task_fa, words, needs, tips_en, tips_fa) -> dict:
    return {
        "kind": "write",
        "task": T(task_en, task_fa),
        "words": words,
        "needs": list(needs),
        "tips": T(tips_en, tips_fa),
    }


def lesson(lid, skill, title, goal, explain, examples, guided, exercises, **extra) -> dict:
    """One lesson. `explain` and `examples` are (en, fa) tuples."""
    out = {
        "id": lid,
        "skill": skill,
        "title": T(*title),
        "goal": T(*goal),
        "explain": [T(*p) for p in explain],
        "examples": [T(*e) for e in examples],
        "guided": list(guided),
        "exercises": list(exercises),
    }
    out.update(extra)
    return out


def unit(uid, title, goal, lessons) -> dict:
    return {"id": uid, "title": T(*title), "goal": T(*goal), "lessons": list(lessons)}


def add_lessons(units, extras) -> list:
    """Append extra lessons to units that already exist.

    `extras` maps a unit id to the lessons added to the end of that unit, so a
    level can be deepened without rewriting the units it already has: the
    lesson order inside a unit stays grammar, vocabulary, then the skill the
    extra covers.
    """
    by_id = {u["id"]: u for u in units}
    for uid, rows in extras.items():
        if uid not in by_id:
            raise KeyError(f"no unit {uid} to add lessons to")
        known = {l["id"] for l in by_id[uid]["lessons"]}
        for row in rows:
            if row["id"] in known:
                raise KeyError(f"lesson {row['id']} is already in {uid}")
            by_id[uid]["lessons"].append(row)
    return units


def passage(title, text) -> dict:
    return {"title": T(*title), "text": T(*text)}


def dialogue(lines) -> list:
    """Role-play lines: (who, en, fa)."""
    return [{"who": who, "en": en, "fa": fa} for who, en, fa in lines]


def reading_item(title, text, questions) -> dict:
    """A reading passage on an exam paper: its text and three marked questions."""
    return {"passage": T(*title), "text": T(*text), "questions": list(questions)}


def section(skill, items) -> dict:
    return {"skill": skill, "items": list(items)}


def exam(minutes, pass_mark, min_skill, blurb, sections) -> dict:
    return {
        "minutes": minutes,
        "pass": pass_mark,
        "minSkill": min_skill,
        "blurb": T(*blurb),
        "sections": list(sections),
    }


def course(title, blurb, units, paper) -> dict:
    return {"title": T(*title), "blurb": T(*blurb), "units": list(units), "exam": paper}
