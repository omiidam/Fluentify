# Fluentify Adults — level assessment

This is the design and maintenance record for the adult placement assessment
(`level_test.json`, rendered by the `Level` module in `webapp.py`). It applies
to Fluentify Adults only; the kids experience never mounts the panel.

## What was wrong before this version

The audit of the previous assessment (v2, 55 questions) found:

- **One fixed paper for everyone.** Every learner answered A1 through C1, and
  the docstring claimed an adaptive staircase the engine never implemented.
- **Four recognition skills only.** Grammar, vocabulary, reading and listening
  were marked; interaction and mediation — the abilities adults actually need
  at a front desk or in a meeting — were absent.
- **Academic prompts.** Most items were sentence-level grammar, not tasks with
  a purpose. There were no situations, no documents and no visual stimuli.
- **Thin metadata.** Items had a band, skill and explanation, but no domain,
  task type, CEFR descriptor, rights line, version or review date, so the bank
  could not be audited or refreshed on a schedule.
- **A report that stopped at a level.** It listed skill bands but no can-do
  statements, no route explanation and no overall confidence.

## Blueprint

| | |
|---|---|
| Tested bands | A1, A2, B1, B2, C1 (Pre-A1 reported below the first cutoff; C2 described but not tested) |
| Core route (everyone) | A1, A2, B1 |
| Upper route (evidence-gated) | B2 when the core is ≥ 65% correct; C1 when B2 is ≥ 60% |
| Objective items | 60: grammar 15, vocabulary 15, reading 10, listening 10, interaction 5, mediation 5 |
| Writing | 5 tasks, one per band, 4 rubric points each |
| Maximum paper | 65 questions (60 + 5) |
| Typical time | 25–45 minutes, untimed |
| Retake window | 30 days; history keeps the last 12 results |

`tools/level_test.py` is the source of truth. `tools/build_level.py` validates
it and writes `level_test.json`; `tools/check_level.py` audits the result and
runs the engine in node.

## Skills and constructs

| Skill | What it measures | How |
|---|---|---|
| Grammar | control of tense, agreement, conditionals, passive, word order | selected response, cloze, error identification, transformation, ordering |
| Vocabulary | range, collocation, phrasal verbs, idiom, precision | selected response, cloze |
| Reading | detail, main idea, inference, attitude | passages with questions, including notices and schedules |
| Listening | announcements, exchanges, implication, tone | device speech (`say`) with an optional transcript |
| Interaction | taking a turn, register, repairing a problem, negotiating | dialogue-response items set in a real exchange |
| Mediation | relaying meaning between people and documents | notices, timetables, policies, two-source briefings |
| Writing | task achievement, length, cohesion, accuracy | five constructed tasks marked on a visible rubric |
| Speaking | practice only | two prompts with a self-rating rubric; **not** scored into the level |

Interaction and mediation are assessed with selected-response items because
the platform cannot reliably mark free production offline. That limitation is
stated on the report, not hidden.

## Item metadata

Every item in `level_test.json` carries:

`id`, `skill`, `band`, `subskill`, `kind`, `difficulty`, `ability`, `prompt`,
`why`, `weight`, `source`, `review`, `domain`, `taskType`, `descriptor`,
`accessibility`, `rights`, `itemVersion`, `status`, `reviewedOn`,
`nextReview`, and — where the task needs them — `scenario`, `stimulus`,
`passage`, `say`, `accept`, `tokens`, `needs`.

- **Domain** is one of everyday, travel, work, food, shopping, technology,
  health, education, social. The builder fails if one domain holds more than
  40% of the bank.
- **Descriptor** is the CEFR can-do line the item is evidence for, bilingual.
- **Stimulus** is data, not markup: `note`, `table` or `message`. The page draws
  it with escaped values; the builder rejects any `<script`, `javascript:` or
  `on*=` attribute.
- **Accessibility** states how the item can be answered without the picture or
  audio; listening items always carry a transcript alternative.

## Adaptive route

`route(bank, attempt)` is the only adaptive rule. It counts correct answers in
the core bands as they are answered:

```
core ≥ 65%  → B2 is administered
B2   ≥ 60%  → C1 is administered
otherwise   → the paper stops at the band reached
```

The route changes which questions are asked, never what an answer is worth.
Skipped bands contribute nothing to the numerator, and every skill is read
against its **whole-bank** denominator (grammar out of 15, reading out of 10,
and so on), so a short route cannot report a band it never tested. A perfect
A1–B1 core is 36 of 65 — a B1 result, not a B2.

The route is stored on the attempt (`bands`) so a saved paper reopens with the
paper it was actually given, even after a content update.

## Scoring and reporting

- Level cutoffs are shares of the whole 65-question paper: 11 correct = A1,
  23 = A2, 34 = B1, 46 = B2, 58 = C1. Each skill is read on the same fractions
  of its own total.
- Confidence comes from the standard error of the count; a score within one
  standard error of a cutoff is reported as moderate confidence with ±1 band.
- Writing is marked deterministically on four visible points per task — enough
  words, enough sentences, the linking the task asks for, a slips check — and
  each task is worth at most one question.
- The report shows: overall band and confidence, score as a share of the whole
  paper, which bands the route administered, per-skill band and evidence,
  the can-do statement for each skill at the band it reached, strengths and
  growth areas, next steps, and an explicit "speaking is not assessed" line.
- Old reports (before the route) are labelled as such rather than being
  reinterpreted.

## Content refresh pipeline

`level_test.json` carries a `content` block: version (`YYYY.MM`), published
date, owner, review cycle (365 days), next review date and a review log.

Workflow for a change:

1. **Create / edit** the item in `tools/level_test.py` with its full metadata.
2. **Editorial review** — natural English, unambiguous instruction, plausible
   distractors that encode real misunderstandings.
3. **CEFR alignment review** — band, descriptor, and difficulty label agree.
4. **Authenticity review** — a real domain and a real communication goal.
5. **Bias and fairness review** — no unnecessary cultural or socioeconomic
   assumption; no answer that depends on colour alone.
6. **Technical review** — every stimulus is data, every `say` is long enough
   to listen to, every typed item has accepted answers.
7. **Build and audit** — `python3 tools/build_level.py` then
   `python3 tools/check_level.py`; the audit fails on missing metadata,
   repeated prompts, one domain dominating, a duplicate id, an unbalanced
   answer key, an A1 item marked hard or a C1 item marked easy.
8. **Approval** — status `approved`; add the change to `content.reviewLog`.
9. **Publish** — bump `content.version`, `published` and `nextReview`, rebuild
   the page and the APK so web and offline carry the same package.
10. **Monitor** — per-item counts on the device (`fluentify.level.items`) show
    questions missed more than once; they aim the next attempt and never leave
    the device.
11. **Revise or retire** — a retired item keeps its historical results; it is
    removed from `paper()` by its `status`, not by deleting evidence.

The freshness check fails when `content.nextReview` or any item's `nextReview`
is in the past, so the pipeline is enforced rather than aspirational.

Review cadence: stable grammar and vocabulary annually; work, technology and
digital communication every review cycle; time-sensitive scenarios (prices,
policies, timetables) whenever the real-world detail changes.

## Offline and platform parity

The bank is a static file served at `/api/level_test`, bundled into the APK by
`build_apk_ui.py` and read from `data/level_test.json` offline. No network call
is needed to sit the paper, mark it or print the report. Listening uses the
device's speech synthesis, so there are no audio files to download.

## Known limitations

- The bank is reviewed but **not statistically calibrated**. Difficulty labels
  are editorial; item facility and discrimination can only be estimated once
  enough attempts exist. The report says "estimate", not "certificate".
- Selected-response interaction and mediation measure recognition of an
  appropriate move, not the ability to produce it under time pressure.
- Speaking is deliberately unscored: there is no reliable offline pronunciation
  or fluency judgement, and a self-rating is not a proficiency score.
- C2 is described in the band table but not tested: five bands of items cannot
  separate C1 from C2 honestly.
