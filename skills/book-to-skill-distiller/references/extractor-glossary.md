# Glossary Term Extractor

Your task is to extract [**the author's own terminology**] from the text blocks assigned to you.

**Definition of a glossary term**: a word the author coined, or a common word the author has given a special meaning.

The test is hard: **the meaning of this word in this content differs from its meaning in everyday usage.** If it is the same, do not record it.

## What to look for

- New words the author invented
- Concepts the author uses repeatedly and has explicitly defined
- Common words whose meaning the author narrowed or widened

## What to leave out

- Industry-standard terms the author is merely using normally
- Words that appear only once and were never defined
- Words where the dictionary meaning is enough

## Processing requirements

Process every block assigned to you, one by one; not a single block may be skipped.

When you hit "as shown in Figure X" and cannot see the figure, reconstruct the content from the surrounding text; if you cannot reconstruct it, do not record it. **Do not treat "as shown in Figure X" as a source excerpt** — that sentence carries no information.

## Record format

## Glossary term: term name (**heading line format is fixed**: starts with `## Glossary term: `, e.g. `## Glossary term: soft zone`)

- The author's definition: in the author's own words
- Difference from everyday usage: where it differs
- Source location: which block / which chapter / timestamp
- Source excerpt: one sentence from the source that shows the author's usage

Do not record anything without a source excerpt.

## Per-block receipt

When done, write one line per block at the end of the file — as many lines as blocks were assigned to you, no merging, no omitting:

    Block 1: found 2
    Block 2: none
    Block 3: found 1
