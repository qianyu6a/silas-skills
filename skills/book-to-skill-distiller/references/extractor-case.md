# Case Extractor

Your task is to extract [**transferable cases**] from the text blocks assigned to you.

**Definition of a case**: a specific thing that actually happened, which shows why some method works.

## What to look for

- Examples with specific people, specific actions, specific results
- Instances the author uses to support a claim
- Especially those whose result is unexpected

## What to leave out

- Examples that give only the conclusion and no process
- Stories where you cannot tell what they are proving
- One-off cases that collapse completely in another situation

## Processing requirements

Process every block assigned to you, one by one; not a single block may be skipped.

When you hit "as shown in Figure X" and cannot see the figure, reconstruct the content from the surrounding text; if you cannot reconstruct it, do not record it. **Do not treat "as shown in Figure X" as a source excerpt** — that sentence carries no information.

## Record format

## Case: one-sentence summary (**heading line format is fixed**: starts with `## Case: `, e.g. `## Case: Master Chen demonstrates non-resistance`)

- Situation: what the situation was at the time
- Action: what was actually done
- Result: what happened
- What it proves: which method this case supports
- Where it transfers: what other situation it still holds in
- Source location: which block / which chapter / timestamp
- Source excerpt: one sentence from the source

Do not record anything without a source excerpt.

## Per-block receipt

When done, write one line per block at the end of the file — as many lines as blocks were assigned to you, no merging, no omitting:

    Block 1: found 2
    Block 2: none
    Block 3: found 1
