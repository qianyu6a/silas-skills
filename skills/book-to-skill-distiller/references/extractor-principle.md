# Principle Extractor

Your task is to extract [**decision principles**] from the text blocks assigned to you.

**Definition of a principle**: a rule that can guide someone to make a trade-off in a concrete situation.

## What to look for

- Standards the author uses to make trade-offs, especially counter-intuitive ones
- The author's "rather A than B" style statements
- The criteria the author uses to judge good or bad, right or wrong, worth it or not worth it

## What to leave out

- Pep talk, slogans, correct platitudes
- Abstract advocacy that means nothing until it is turned into an action
- Things a clever person could say without reading this content

## Processing requirements

Process every block assigned to you, one by one; not a single block may be skipped.

When you hit "as shown in Figure X" and cannot see the figure, reconstruct the content from the surrounding text; if you cannot reconstruct it, do not record it. **Do not treat "as shown in Figure X" as a source excerpt** — that sentence carries no information.

## Record format

## Principle: one-sentence statement (**heading line format is fixed**: starts with `## Principle: `, e.g. `## Principle: Better to lose often than to stay in a small circle where you can win`)

- Applies when: under what conditions this holds
- What it argues against: which common practice this principle is pushing back on
- Source location: which block / which chapter / timestamp
- Source excerpt: one sentence from the source that proves this principle

Do not record anything without a source excerpt.

## Per-block receipt

When done, write one line per block at the end of the file — as many lines as blocks were assigned to you, no merging, no omitting:

    Block 1: found 2
    Block 2: none
    Block 3: found 1
