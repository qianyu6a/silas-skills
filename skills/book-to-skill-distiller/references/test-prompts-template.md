# Decoy Test Question Template

Step 6 produces `skills/test-prompts.md`, filled in per this template.

**This file is handed to the user, not discarded after the run.** Whenever the user later changes any description, they can rerun the original questions to verify, without composing new ones.

## How to use this question set

Dispatch a fresh sub-agent as the tester and **give it only the names and descriptions of all skills — no bodies, no candidate file paths**. Put the distillation tool itself ("One Lamp") on the list as a control item too — the correct answer to the mandatory question "help me distill this book into skills" is to trigger it, and if it is not on the list the tester has no way to answer correctly.

The blind test is the point. If the tester has seen the bodies, it judges from the bodies rather than from the descriptions, and the result is meaningless.

Have it answer, for each question: which skill should trigger, or that none should; questions it is unsure about may carry a one-word annotation.

**Operationally, write "the skill list + the questions" into one standalone test file** (put it in scratch, not in the workspace), and fix the dispatch instruction as: you may read only this one file, do not read any other file, do not search — the workspace is full of bodies and candidates, and one glance from the tester ends the blindness.

**Write the answer key before dispatching the tester**: the lead fills in the "correct answer" column for every question, the tester answers blind, and you compare after collecting. When skills produced from several books will be deployed side by side, the list holds **every skill that will be deployed there** — cross-book call-stealing is as real as same-source call-stealing, and both must be tested.

Write the answer key as **plain names, with no annotations**; before comparing, normalize both sides the same way (strip parenthesized annotations etc.) — annotations mixed into the answers make a strict string comparison grade a correct answer as wrong. **Keep the answer file and the question file in separate directories** (move the answer file out of the test directory as soon as the key is written) so the tester cannot stumble onto it.

---

# Trigger Test for the <content title> Skill Pack

## Skills under test

| name | One-line purpose |
| --- | --- |
| <name> | <purpose> |

## Layer one · Same-source confusion

Skip this layer when there are only 1 to 2 skills in total. With 3 or more, at least 2 questions per skill.

The scenario is "this should trigger another skill in the same batch". Skills split out of one piece of content are naturally close in topic, and the most common failure after deployment is stealing calls from each other — while testing only "completely unrelated scenarios" will never surface it.

| No. | What the user says | Correct answer | Actual result | Pass |
| --- | --- | --- | --- | --- |
| A1 | <one sentence a user would say> | <name that should trigger> | <actual> | <yes/no> |
| A2 | <one sentence a user would say> | <name that should trigger> | <actual> | <yes/no> |

## Layer two · Host confusion

At least 2 questions per skill. The scenario is "the assistant's existing general capabilities should handle this; none of these skills should trigger".

The user's assistant already carries dozens of general skills. Newly installed skills that grab this work will seriously disrupt their daily use.

Reference questions:

- Help me compute the numbers in this table
- Help me write an email
- Help me summarize this web page
- Help me make a slide deck
- Help me tidy up the files in this folder

Beyond general tasks, add 1–2 **topically close but should-fail** probes per skill (emotion-type: "had a fight with my girlfriend, how do I make up"; training-type: "explain what deliberate practice is"; mindset-type: "I'm just born dumb, how do I accept it") — general tasks test "does not grab unrelated work", while these probes test "does not grab adjacent work", and only the latter exposes how wide or narrow the description's boundary is.

| No. | What the user says | Correct answer | Actual result | Pass |
| --- | --- | --- | --- | --- |
| B1 | <one sentence a user would say> | none should trigger | <actual> | <yes/no> |
| B2 | <one sentence a user would say> | none should trigger | <actual> | <yes/no> |

**The verdict column allows three states**: `yes` / `boundary · see note` / `no`. "Boundary" = the question itself is ambiguous, or sibling skills' description trigger words overlap — triggering another one is also defensible, so it does not count as a failure: write it in the note, leave the description alone, and do not spend a retest round on it. Where the actual result equals the correct answer and the tester merely added "boundary", count it as a pass and keep the note verbatim.

**Writing the actual-result column back afterwards means rewriting the whole file** — the host's write tool refuses to overwrite a file "this task has not read": use python's `io.open` to write directly, or read it once and then write.

## Repair log

Questions answered wrongly mean the corresponding skill's description boundary is unclear. Rewrite that skill's description and then **retest all questions, not just the ones answered wrongly** — changing one skill's boundary shifts the verdicts of the others too, and retesting only part of the set will miss newly introduced conflicts.

Two rounds at most.

| Round | Which skill changed | What changed | Pass rate this round |
| --- | --- | --- | --- |
| Round 1 | <name> | <one sentence> | <N/M> |

## Open issues

Skills still failing after two rounds are not deleted, but they must be named here, and a line annotating it must be added at the top of its `SKILL.md`.

| name | Which question it still fails | Note |
| --- | --- | --- |
| <name> | <no.> | <one sentence> |
