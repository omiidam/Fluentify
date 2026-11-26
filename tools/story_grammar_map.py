#!/usr/bin/env python3
"""Which Grammar lesson answers each grammar point a story teaches.

A story's grammar notes are written for the story ("Past simple of lie and
break", "had made, past perfect"), not for the shelf ("Simple Past", "Past
Perfect"), so the note cannot find its own lesson by name. This is that
translation, written once, so the story can offer a way into the lesson.

Two lists, and build_stories refuses a note that is in neither:

  TOPIC_OF  the note is a form of a lesson the shelf already teaches.
  NO_LESSON the note is about the story's own words - "at last", "this time",
            "list of three verbs" - and no lesson claims it. Those points get
            no button rather than a button that lands on the wrong lesson.

Every id here is checked against grammar.json when the stories are built.
"""
from __future__ import annotations

# note name -> lesson id
TOPIC_OF = {
    "Comparative with -er": "comparatives",
    "as ... as": "comparatives",
    "as tall as, comparison": "comparatives",
    "grew + comparative": "comparatives",
    "taller than a house": "comparatives",

    "Dialogue without quotation marks": "reported_speech",
    "Direct speech": "reported_speech",
    "said + direct speech": "reported_speech",
    "said + that clause": "reported_speech",
    "told her to + verb": "reported_speech",
    "told somebody to + verb": "reported_speech",

    "Embedded question": "wh_questions",
    "Who will ...?": "wh_questions",

    "Past habit with every": "used_to_would",

    "Past perfect for the earlier past": "past_perfect",
    "by the time + past": "past_perfect",
    "had + past participle": "past_perfect",
    "had been dead seven years": "past_perfect",
    "had killed, past perfect": "past_perfect",
    "had made, past perfect": "past_perfect",
    "had never seen": "past_perfect",
    "had traveled, past perfect": "past_perfect",
    "past perfect had + done": "past_perfect",
    "past perfect had lost": "past_perfect",
    "past perfect had sailed": "past_perfect",
    "thought + past perfect": "past_perfect",
    "thought they had won": "past_perfect",

    "Past simple": "simple_past",
    "Past simple irregulars": "simple_past",
    "Past simple of lie and break": "simple_past",
    "Past simple story verbs": "simple_past",
    "Past simple with irregular verbs": "simple_past",
    "Past simple, irregular verbs": "simple_past",
    "Past simple, regular": "simple_past",
    "Past simple, regular and irregular": "simple_past",
    "past simple chain": "simple_past",
    "past simple in order": "simple_past",
    "did not believe he was alive": "simple_past",
    "was angry and threw": "simple_past",
    "when + past simple": "simple_past",
    "when + past, past": "simple_past",

    "past continuous + when": "past_progressive",
    "past continuous with while": "past_progressive",

    "passive: was taken for": "passive_voice",
    "past passive": "passive_voice",
    "past passive was tied": "passive_voice",
    "past passive with 'was'": "passive_voice",
    "ready to be + past participle": "passive_voice",
    "was saved by": "passive_voice",
    "was sent to": "passive_voice",

    "if + past, could": "conditionals",
    "if + present, can": "conditionals",
    "if + present, will promise": "conditionals",
    "unless + clause": "conditionals",

    "could + verb after 'and'": "modals",
    "could not + verb": "modals",
    "had to": "modals",
    "had to + verb": "modals",
    "must for a rule": "modals",
    "must for obligation": "modals",

    "will be, a promise": "simple_future",
    "will for a decision": "simple_future",
    "will for the future": "simple_future",
    "won't = will not": "simple_future",

    "would + verb, a promise in the past": "future_in_past",
    "would marry (future in the past)": "future_in_past",
    "would not + verb": "future_in_past",
    "would not leave": "future_in_past",

    "wished he could": "wish_subjunctive",
    "only + noun + could": "inversion",

    "who / that relative clauses": "relative_clauses",
    "who / which relative clauses": "relative_clauses",
    "who had lost money": "relative_clauses",
    "whose + noun": "relative_clauses",
    "that + clause after a noun": "relative_clauses",

    "because + clause": "purpose_reason",
    "to + purpose": "purpose_reason",
    "to + verb for purpose": "purpose_reason",

    "but for contrast": "linking_words",
    "neither ... nor": "linking_words",
    "not ... or ...": "linking_words",
    "or for a threat": "linking_words",
    "rather than + verb": "linking_words",
    "though + clause": "linking_words",
    "so + clause, result": "linking_words",
    "so + result": "linking_words",
    "So + result": "linking_words",
    "so for a result": "linking_words",
    "so for result": "linking_words",
    "each time": "linking_words",

    "so + adjective, result": "so_such_too_enough",
    "so ... that, result": "so_such_too_enough",
    "too + adjective": "so_such_too_enough",
    "too + adjective (+ to)": "so_such_too_enough",
    "too + adjective + for": "so_such_too_enough",
    "too + adjective + to": "so_such_too_enough",
    "too ... to": "so_such_too_enough",

    "too for addition": "adverbs",
    "too, at the end": "adverbs",
    "never + present simple": "simple_present",

    "each + singular noun": "determiners_some_any",
    "every + singular noun": "determiners_some_any",

    "before + clause": "prepositions_time_place",
    "until + clause": "prepositions_time_place",
    "further into": "prepositions_time_place",
    "with + noun, accompaniment": "prepositions_time_place",

    "Possessive my in dialogue": "pronouns",
    "showed him + noun": "word_order",

    "ask somebody to do": "gerunds_infinitives",
    "let somebody do": "gerunds_infinitives",
    "make somebody + verb": "gerunds_infinitives",
    "make somebody do": "gerunds_infinitives",
    "refuse somebody": "gerunds_infinitives",
    "swear + to": "gerunds_infinitives",
    "tell somebody to do": "gerunds_infinitives",
    "want to / long for": "gerunds_infinitives",
    "wanted to be": "gerunds_infinitives",
    "warn somebody against": "gerunds_infinitives",
    "warn somebody to + verb": "gerunds_infinitives",

    "turn somebody into": "phrasal_verbs",
}

# Notes about this story's own words: a lesson would teach the wrong thing.
NO_LESSON = {
    "Imperatives",
    "Let's + verb",
    "Negative command",
    "What + adjective + noun!",
    "at last",
    "found that he was",
    "had no defense against",
    "imperative as a password",
    "learned that",
    "list of three verbs",
    "made him invisible",
    "made him richer",
    "make ... from",
    "make somebody + adjective",
    "never + verb, an order",
    "not the merry one",
    "seem + adjective",
    "this time",
}


def topic_for(name: str) -> str | None:
    """The lesson that teaches this note, or None when no lesson does."""
    return TOPIC_OF.get(name)


def unmapped(names) -> list[str]:
    """Names the build has no answer for: a new note nobody has placed yet."""
    return sorted(n for n in names if n not in TOPIC_OF and n not in NO_LESSON)
