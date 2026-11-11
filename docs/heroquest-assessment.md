# Hero Quest: child-testing and learning protocol

This is the protocol the game is measured with. **No child has been tested yet**;
nothing below is a result.

## Consent and safety

- A parent or guardian signs a one-page consent; the child gives spoken assent
  and may stop at any time without a reason.
- No names, faces, audio or video are recorded. The session notes hold an age
  band, the device, task times and what the child did, nothing identifying.
- Sessions run in a familiar room, last at most 20 minutes, and end early if the
  child loses interest. Nobody is asked to continue after they want to stop.

## Groups

Age decides presentation, never English level. The level comes from the existing
Fluentify placement:

| band | ages | what changes |
|------|------|--------------|
| young | 5-7 | an adult reads the prompt aloud; tapping only |
| middle | 8-10 | child reads alone; tapping or dragging |
| older | 11-14 | child reads alone; all interactions |

Each band should include at least one A1 and one A2-romB1 child, so the same age
is not mistaken for the same proficiency.

## Tasks (observed, not assisted)

1. Open the app and find the game.
2. Say what the open mission is asking for, in their own words.
3. Find and start a mission.
4. Finish the vocabulary challenge.
5. Finish the grammar challenge.
6. Finish the sentence-building or bridge challenge.
7. Get one answer wrong on purpose and say what the screen told them.
8. Find how many stars they have and what opens next.
9. Leave the game and come back; confirm the stars and the mission are still
   there.

Record: time to start, wrong taps, requests for help, whether they re-read the
prompt, whether they retried after a mistake, and one sentence on mood. Silence
is not understanding - ask the child to explain, never assume.

## Assessment forms

Four short forms, sat on the device, each 8-10 items drawn from the mission's own
vocabulary and grammar but **never the same sentences**:

- **baseline** before the first mission,
- **immediate** within ten minutes of the last mission,
- **delayed7** seven days later (same objectives, new sentences),
- **transfer** a new situation: the target word or structure used in a sentence
  the game never showed.

A comparison group plays an unrelated activity for the same time. Record every
answer as `{"phase": "...", "item": "w:bridge", "ok": true, "at": <ms>}` in the
export, then run:

    python3 tools/quest_learning.py export.json

## Report

Report baseline, immediate, delayed and transfer separately. A gain that is gone
at `delayed7` is not a learning outcome. With fewer than 20 children per band,
call the numbers formative and say so in the same sentence as the number.
