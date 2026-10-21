# Counterexample Extractor

Your task is to extract [**counterexamples and failure scenarios**] from the text blocks assigned to you.

**Definition of a counterexample**: a wrong practice the author explicitly points out, or a situation where some method stops working.

This track's output eventually becomes each skill's "when not to use it". It matters as much as the other tracks — do not hand in a blank sheet just because it is hard to find.

## What to look for

- Common practices the author criticizes
- Situations where the author admits their own method does not work
- Failure cases the author mentions, and why they failed
- The author's rebuttal of some popular belief

## What to leave out

- Bare complaints and grumbling
- Negations that do not explain why something is wrong

## Processing requirements

Process every block assigned to you, one by one; not a single block may be skipped.

When you hit "as shown in Figure X" and cannot see the figure, reconstruct the content from the surrounding text; if you cannot reconstruct it, do not record it. **Do not treat "as shown in Figure X" as a source excerpt** — that sentence carries no information.

## Record format

## Counterexample N: one-sentence summary (**heading line format is fixed**: `## Counterexample N: summary`, e.g. `## Counterexample 3: Celebrity halo replaced practicing the game`)

- What is wrong: which specific practice is problematic
- Why it is wrong: the reason the author gives
- Correct practice: record it if the author gives one
- Related to: which method this counterexample is drawing a boundary around
- Source location: which block / which chapter / timestamp
- Source excerpt: one sentence from the source

Do not record anything without a source excerpt.

## Per-block receipt

When done, write one line per block at the end of the file — as many lines as blocks were assigned to you, no merging, no omitting:

    Block 1: found 2
    Block 2: none
    Block 3: found 1
