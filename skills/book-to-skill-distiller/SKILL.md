---
name: book-to-skill-distiller
description: >
  Use when the user wants to distill a book, a long document, a course lecture
  transcript, an interview transcript, a meeting record, a paper, or a video/podcast
  transcript into a skill pack an AI can call directly. Also use it when several
  materials are handed over at once and you must first triage which ones can be
  distilled and which cannot. Users will say "用一盏神灯蒸馏这本书" ("distill this book
  with One Lamp"), "把这本书拆成技能" ("break this book into skills"), "帮我把这份材料做成
  skill" ("turn this material into a skill"), or "把这本书提炼成技能包" ("extract this book
  into a skill pack"), or "继续蒸馏" ("continue distilling") to pick up the last run's
  progress. Do not use it when the user only wants reading notes, a content summary,
  a mind map, or a book review. Do not use it to write a brand-new skill from scratch
  instead of extracting one from a long text.
---

# One Lamp

Break one long text into several skill packs that an AI assistant can call directly.

What comes out is not reading notes and not a summary — it is **operating instructions that let someone who has never read the book call them up when facing a concrete problem, and get one thing done**.

## General execution rules

- Fully automatic execution. Apart from the Step 0 gate and the places explicitly marked "stop", do not interrupt the user mid-run — run all the way to the end
- This is a long task: turn on multi-agent parallelism
- As soon as a step finishes, write its progress into `state.md` (Step 3 has a special persist-order requirement; that step's rule governs)
- Announce one line of progress at the start and end of every step, **including the working directory path**
- Use the user's language for all narration; keep source quotations verbatim in their original language
- Sub-agents run on paid models: confirm the account balance before important batches, and watch the remaining balance during long runs. When credit runs low, trim by "core first" (keep extraction/verification/construction; switch tests to a slim version); running out of credit interrupts every running sub-agent at once, which costs more than running lean. Write down the switch procedure for an alternate model channel and use it only as a rescue. How to estimate "what does distilling one book cost" when the user asks: ① use pymupdf to sample the source file's page count and word count; ② count sub-agent volume (extraction = batches × 5, verification = pack count, construction = skill count); ③ take the previous book's whole-pipeline run measured with `hermes insights --days 1` as the baseline and convert (rule of thumb: a book in the 700k-character class ≈ $1–1.5 end to end); report a range, not a point estimate
- **Cost accounting (keep real books)**: `hermes insights` under-reports for models with no configured pricing (bulk sessions get recorded as Unknown), so treat it as a reference only; real consumption = check the account balance once before starting and once at wrap-up, append a "balance + timestamp" snapshot to a log file, and reconcile by the difference. Query the balance through your model provider's read-only balance endpoint; read the key inside the script process and never print it into the conversation.
- **Load discipline (hard constraint)**: do not stack heavy local work on top of cloud batches — for parallel sub-agent batches, running OCR, big compiles and other heavy local tasks is pure interference; when the user reports "other tasks won't run", first pause or stop the heavy local work (preserve resumable progress, resumable at any time) and keep the cloud batches moving. Cap local multiprocess jobs at ≤2 processes at all times (the measured safe value for scanned-book OCR; multiprocess heavy jobs have frozen the user's whole machine); check free memory before starting heavy work (`head -3 /proc/meminfo` — that is Windows memory under MSYS); below 3GB, start no new processes
- **Unattended overnight mode**: when the user says "I'm going to sleep / do it all / keep it running" to authorize a night run, switch to the most conservative configuration and hold one bottom line — **anything that goes wrong at any step must be self-recoverable; no operation may require the user to get up in the middle of the night and fix it**: only do tasks that resume from a checkpoint; do not upgrade, reinstall, touch system configuration, or run unrecoverable bulk operations; when several books are queued, run OCR serially (one OCR task at a time); when one book finishes, automatically take the next from the queue; in the morning, report "what got done + what is left"
- If the content contains illegal operations or concrete methods for harming others, stop immediately and explain why
- **Cross-session and completion notification**: distillation is a long task and often runs across sessions/channels (desktop, WeChat and cron are separate sessions with no shared context). When the user asks "is it distilled yet": read the checkbox progress in the workspace `state.md`, then check whether the skill has entered the skills directory (a matching skill directory appearing under `data/skills/` = installed; being written only into the workspace `skills/` does not count). When the user asks "say something on channel X when it's done": the completion notification must go to **the channel the user specified** — across channels use `hermes send` (e.g. `hermes send --to weixin`); when the task runs in another channel's session, its completion receipt appears only in that channel, so the WeChat side needs a separate send. At wrap-up, give at least one line of "what got done + where the artifacts are".

The reference files bundled with this skill — read them only when needed:

| File | When to read it |
| --- | --- |
| `references/extractor-framework.md` and the four others | At Step 3, when dispatching sub-agents: give them the paths |
| `references/skeleton-template.md` | Before writing the skeleton at Step 2 |
| `references/skill-template.md` | Before constructing skill packs at Step 5 |
| `references/test-prompts-template.md` | Before the blind test at Step 6 |
| `references/verification-prep.md` | Before verification at Step 4 (unified numbering → dedup pre-screen → machine signals → task packs → verifier dispatch; the resift recipe for when the pass rate crosses the line is also here) |
| `references/batch-extraction-playbook.md` | Before executing Step 3 — the batch-extraction playbook for big books with more than 20 blocks (an 8-batch × 5-track field version, including the lead's wrap-up checklist) |
| `references/construction-prep.md` | Before construction at Step 5 — grouping of the retained verification set, material splitting, and the constructor dispatch and acceptance recipe |
| `scripts/verify_candidates.py` | Step 3 wrap-up — cross-batch full check of the five-track candidate excerpts (run directly: `python scripts/verify_candidates.py <workspace-path>`) |

---

## Step 0 · Gate check

If any gate fails, stop immediately and tell the user the reason and what to do in **plain language**. Do not use technical jargon, and do not grit your teeth and run on. The first three gates apply to every file; the fourth runs only when the user supplied several files at once.

### Gate 1 · Is the file there

If the user has not supplied a file yet, stop and tell them: please send me the file to distill — txt, md, docx, pdf and transcripts are supported. Then wait.

### Gate 2 · Can the text be read out

Sample about 500 characters each from the start, middle and end of the file; check whether they are blank, mojibake, or all meaningless symbols. **Do a text-layer check plus a size check before deciding on OCR**: open the PDF with pymupdf, pull one page out of every 20 and measure the length returned by `get_text()` — if there is a text layer, extract directly at zero OCR cost (big classic books are often text editions; do not assume "big book = scanned"); while you are there, estimate total word count as "page count × average length per page" — that is the input to the schedule and cost estimate. Watch for two kinds of text layer: ① OCR output often has **vertical ghosting** (the same line repeated 3–4 times) — distill it as usual, but when dispatching extraction state "take single lines or a single-line prefix (a multi-line excerpt always fails in a ghosted block), never copy a ghosted block whole", and do not run aggressive dedup cleaning (the risk of corrupting the body text outweighs the benefit; ghosting is only ugly, it does not block the pipeline); ② header lines (`Chapter X Title … page number`) — strip them with a regex before splitting into blocks, and keep the bare chapter title line as a block boundary — after cleaning, check that the chapter count matches the table of contents (OCR turns Chinese numeral chapter numbers into variants, 「第十六章」→「第16」; for missing numbers, search again for the Arabic-numeral variant before cutting)

If no text can be read out, it is a scanned image file. Do not bounce it straight back to the user — the local machine can run OCR itself (use a local engine such as RapidOCR: free, offline, good enough for printed text; with many pages it takes tens of minutes to hours):

> This file is a scan — it's images, not text, so I can't read the content. I can run text recognition locally to turn it into a text version (free, no network, a bit slow with many pages), and continue distilling when it's done.

After the user confirms (or the material was already on the list the user asked to distill), run OCR in the background and meanwhile push other stages of the pipeline with the other materials — do not let the whole line sit waiting on OCR. Progress semantics for background OCR: at start the output is written with **all** page markers as placeholders, content is backfilled every 20 pages, and it resumes from a checkpoint — **progress is measured in "pages with content"; the number of page markers does not indicate progress**; the completion criterion = pages with content equals the PDF's total page count (the log prints `DONE: … total_done: N / N`); after completion, spot-check the first and last pages for quality, then split into blocks. Two scans can differ by more than 2× in OCR speed (different character density per page and scan quality) — refresh the ETA from this task's measured speed, do not extrapolate linearly from the previous book's speed; "slower than expected" is not the same as stuck — stuck means the log produces no new line and no increment lands on disk for a long time.

If the format itself cannot be opened, do not report error codes:

> I can't open this format on my end. Save it as a txt or Word document and send it to me again.

### Gate 3 · Is this content suitable for distillation

This is the gate most easily overlooked, and it decides whether the next few hours are wasted.

| Type | Test | Action |
| --- | --- | --- |
| Methodological | Has transferable frameworks, principles, decision criteria | Continue |
| Narrative | Novels, biographies, pure story, no actionable method | Stop |
| Informational | News, financial reports, bare lists of facts | Stop |
| Normative | Company policies, contract clauses, operating manuals, compliance documents — constrain behavior only, never explain why | Stop |
| Paper | Continue when there is a clear methodological contribution; stop for pure literature reviews and bare lists of experimental data | Judge by content |

How to judge: pull three paragraphs at random and ask yourself "does this paragraph contain one rule that could guide someone's decision". If none of the three has one, it is not suitable.

Note two gray areas:

- **Policy documents** (employee handbooks, management measures, SOPs) look as if they are all "how to do it", but they only tell you "you must do it this way", never "why this way, and when you may deviate". What you extract stops holding at another company, so it is not a transferable method. Unless the document extensively explains the judgment logic behind each rule, treat it as normative.
- **Interview transcripts, dialogues and meeting records** are treated as transcripts: every later relaxed standard for transcripts applies; do not hold them to the book standard.
- **Papers** judged fit to continue are treated as books — they have chapter structure and argue the same thesis repeatedly, so the book's evidence standard and blocking method apply.

> I've read this content. It mainly tells stories and lists facts; there is nothing in it that can be split into operating methods. A skill pack forced out of it would be very hollow. I suggest trying content that explains methods and principles instead.

If the volume is under 5,000 characters, stop and tell the user the content is too short to split anything out. **When several files are to be distilled together, this counts the merged total, not each single file** — eight transcripts of 3,000 characters each merge into 24,000 characters; do not kill them all because no single one is big enough.

### Gate 4 · Multi-file triage (run only when the user supplied several files at once)

If the user gave only one file, skip this gate. If they gave several, first run Gate 2 and Gate 3 on each file separately, then handle them per the table below.

| Case | Example | Action |
| --- | --- | --- |
| All suitable, and the same theme | Volumes 1 and 2 of one book, several chapters of one course | Treat as one piece of content and distill together; when splitting, number blocks by concatenating in file order |
| All suitable, but the domains are entirely different | A book on writing + a book on investing | **Do not merge**; ask the user which to distill first, and build a separate workspace for each |
| Partly suitable, partly not | 10 files: 7 methodological, 3 informational | Continue the pipeline with the suitable part; explain the reason for each unsuitable one, do not force a distillation |
| All unsuitable | All novels and news | Stop, and explain the reason for each |
| Several files interrelated | A book + a set of interpretive notes on that book | Take the more systematic, more complete one as the main material (usually the original book, not the largest one); treat the rest as supplementary reference, do not split them into blocks separately |

The cases stack. For example, 7 of 10 files are suitable but those 7 fall into two domains: first use "partly suitable" to pull out the 3 unsuitable ones and explain why, then use "different domains" to ask the user which domain to do first. There are only two rules: **unsuitable material is never mixed in; different domains are never distilled together.** Combine the two and handle it that way; if you cannot, ask the user.

The announcement script for the partly-suitable case (say it like this; do not simplify the reasons away):

> Of the 10 files you gave me, 7 are suitable for distillation and I'll continue with them. The other 3: "A" is a news report with no transferable method; "B" is a company policy that states rules but not judgment; "C" is a scan with no readable text. I suggest swapping those three for other material — forcing a distillation out of them would be useless.

The announcement script when the domains are entirely different:

> These files point in completely different directions; distilling them together would dilute each other and every skill pack that came out would be impure. Which one do you want to distill first? The rest queue up; we start the next when one is done.

Once the user chooses, write the queued file list into `state.md`. After one is distilled and Step 7 delivery is complete, if there are still files in the queue, announce one line "continuing with the next one, X", then **automatically** run the whole pipeline from Step 0 on the next one, each with its own workspace, without waiting for the user to speak again — the queueing was already authorized when they chose.

**The precondition for distilling together is that all files belong to the same theme and can answer the same kind of question.** If you cannot tell whether they are the same theme, ask the user one question — "do you want these materials to end up as one skill pack, or one each?" — do not guess.

### All gates passed

> Checks passed. This content is about X ten-thousand characters; I judge it to be [methodological], and I expect to produce N skill packs. This will run for a while.
>
> You can interrupt at any point. In the same conversation, just say "continue". If you close the conversation and open a new one, say: **continue distilling, the directory is <full path of the working directory>**.
>
> Starting now.

(The N conversion is in Step 5 · the count-cap table: the tier is set by effective word count, and **for transcripts subtract 2 from both the target and the cap, down to 1** — convert before announcing, do not forget the −2.)

When distilling several files together, add one sentence to this announcement — "I'll treat these materials as one piece of content" — so the user knows the merge happened.

Do not give a specific number of minutes; you cannot estimate it accurately and giving one breaks trust. Write the working directory into this announcement as soon as it is fixed — a new session can only find the scene again if the user reports that path.

---

## Step 1 · Create the workspace

Create a new folder `distill_<content-title>` under the user's working directory. (Existing local convention: use an ASCII name for the workspace root, e.g. `D:/distill_<english-tag>/`; the subdirectories map to the table below as `blocks/` (source blocks), `cand/` (candidates), `work/` (sub-agent scratch scripts). Chinese file names are fine; a purely Chinese root path occasionally loses sub-agents.)

The content title comes from the cover, the first page, or the file name. If it is too long, take the first few characters; strip symbols such as slashes, colons and question marks — failing to create the directory is a hard fault.

| Path | Purpose |
| --- | --- |
| `blocks/` | Plain-text blocks of the input file |
| `cand/` | Raw candidates as extracted |
| `skills/` | The final product — **put only skill folders in here, no loose files** |
| `state.md` | Progress record |

### Block splitting

**First strip the non-body parts**: cover, copyright page, blurb/extract, endorsements, table of contents, preface and acknowledgements, references, appendix glossary.

These produce a lot of noise that looks like candidates but has no operating value. The appendix glossary especially — neatly formatted and dense with terminology — is the easiest thing to mistake for a framework and extract.

**The stripping applies only to block splitting and extraction; do not actually delete anything.** At Step 2, when building the skeleton, the table of contents and preface are exactly the most useful parts — they tell you straight out how the author organized the material. Keep them aside and read them during the skeleton stage.

What remains after stripping is the **effective word count**; every later judgment tiered by word count uses this number.

Then split into blocks:

- Block size = effective word count ÷ 30, clamped between 3,000 and 15,000 characters, targeting 20 to 40 blocks
- **Short-material shortcut** (effective word count under 30,000): do not apply the "20 to 40 blocks" target — just cut 2–5 blocks of 3,000–15,000 characters; a small block count does not hurt the later pipeline (the coverage check runs on the actual block count)
- Books split by chapter; a chapter larger than the block size is cut down along subsection boundaries; a resulting subsection smaller than half the block size is merged with the adjacent subsection until it approaches the target size
- Transcripts split at topic turns; merge over-fragmented segments the same way
- **Never cut in the middle of a sentence or paragraph**; prefer a slightly larger block
- Implementation notes (for books split by chapter): first scan the whole book's chapter titles to fix the boundaries and verify the chapter count (OCR chapter-number variants, see Gate 2); for epub sources take text in spine order (≠ filename dictionary order) — hrefs inside the zip are relative to the directory the opf lives in, so the path must be prefixed (the opf is often in `OPS/` — miss the prefix and the whole batch reads nothing; take one section as a trial read to verify before extracting everything); when merging small chapters, **decide first, then append** (if accumulated count + next chapter count > the cap, write to disk first) — append-then-check inflates a block to nearly twice the cap; a chapter over the cap is cut at the nearest subsection heading line (line starting with `X.Y `)
- For books whose chapter titles are unusable (scanned OCR text, titles recognized badly): switch to greedy cutting on `[page N]` page markers — pick a page count close to the target word count (scanned pages hold few characters, roughly 25–30 pages/block), and always land block boundaries on page markers; after cutting, print the per-block word count distribution to check, and fold a clearly undersized final block into the previous one

Number the blocks consecutively starting from 1. **The total block count is the basis for the later coverage check and cannot be skipped.**

Batch size is fixed at 5 blocks; batch count = ceil(total blocks ÷ 5).

### Figure-dependency check

Count how many times references such as "as shown in Figure X" or "see Figure X-X" appear in the body, then check whether those figures' content can actually be read.

Image references come in several forms — recognize both standard Markdown `![](path)` and Obsidian `![[path]]`; do not conclude "no figures" after checking only one form.

If references are frequent but the figures cannot be read, note it in `state.md`, and when dispatching at Step 3 tell the sub-agents additionally: this text depends heavily on figures and the figures are not visible, so wherever it says "as shown in Figure X" you must reconstruct the structure from the surrounding text, and if you cannot reconstruct it, do not record it.

### Write the state

`state.md` records: content title, input type (book / transcript), effective word count, total blocks, batch count, target number of skill packs, current progress. When distilling several files together, additionally record each file's original file name and the type Gate 3 assigned it — later, when one block's candidate quality looks abnormal, this is how you trace which material it came from.

Add one line at the top of the file:

> If you are a new session, load the "One Lamp" skill first, then continue from the progress recorded below.

---

## Step 2 · Global Skeleton and Critique

Do this yourself; do not dispatch a sub-agent. Read `references/skeleton-template.md` first.

Read through the table of contents, the opening and closing of every chapter (or topic segment), plus a random sample of blocks, and produce `skeleton.md` per the template.

The **Blind Spots and Boundaries** section must be written out to at least 3 entries — it cannot be skipped, and it cannot be padded. That section is the only source for the "when not to use this" part of every skill pack downstream. Write it thin and the output packs turn into a pile of quotable lines that treat the author's bias as truth.

When it is written, run the skeleton self-check: pull 3 blocks at random and check one by one whether the skeleton can explain them. If one cannot be explained, your reading is off — rewrite it once. **Rewrite only once**; after the second attempt, continue no matter what.

---

## Step 3 · Five-Track Batched Parallel Extraction

> When the block count is >20 (batch count >4), read `references/batch-extraction-playbook.md` first — the 8-batch × 5-track field manual, including the lead's wrap-up checklist.

### How to Execute

Loop over batches. **Within a batch, five tracks run in parallel; between batches, execution is sequential.**

For batch 1 through the last batch, in order:

1. Start five sub-agents simultaneously, each running one of the following five extractors:

   | Sub-agent | Extractor file | Output |
   | --- | --- | --- |
   | Framework | `references/extractor-framework.md` | `cand/framework.md` |
   | Principle | `references/extractor-principle.md` | `cand/principle.md` |
   | Case | `references/extractor-case.md` | `cand/case.md` |
   | Counterexample | `references/extractor-counterexample.md` | `cand/counterexample.md` |
   | Glossary term | `references/extractor-glossary.md` | `cand/glossary.md` |

2. Once all five tracks return, run the coverage check
3. Append the results to the matching candidate file from the table above. **Where you append matters**: from batch 2 on, the file already holds the previous batch's "## Per-Block Receipt" section — insert this batch's new candidates **before** the receipt section, and **append** this batch's "Block X" lines to the receipt section while keeping the old lines. This protocol must go into the sub-agent's task description, otherwise it continues writing at the end of the file, shoves the receipt section into the middle, and breaks script parsing.
4. **Only after every candidate is on disk**, update `state.md` to record which batch is done (reverse the order and an interruption will leave you thinking the batch is finished when only half of it was written)
5. Announce: batch X of Y done
6. Move to the next batch

Parallelism stays at 5 at all times; do not fan out every batch at once just to go faster.

### What Every Sub-Agent Must Receive at Dispatch

A sub-agent cannot see this skill's body text and cannot see the others. Every task description must state these nine items:

1. The full path of its extractor file
2. Which blocks this batch contains, and the full file path of each of those blocks
3. It must process block by block; not one may be skipped
4. The full path of the output file
5. A per-block receipt is mandatory
6. Unified output-format convention: all entries use the same heading level, and every field uses `- field: value` (put this into the task template — do not improvise per batch; inconsistent formats across batches force rework in later parsing and validation); **the heading-line format is fixed per track** — Framework `## N. Name` / Principle `## Principle: …` / Case `## Case: …` / Counterexample `## Counterexample N: …` / Glossary term `## Term: …` (literal examples are in the "Recording Format" section of each extractor). The verifier parses by fixed pattern; format drift makes a whole track parse as a false green with ok=0
7. Environment note: when a sub-agent must fix a file it already wrote, tell it to use a localized edit or to read first then overwrite (some host environments refuse to overwrite a file that was never read — a plain overwrite fails)
8. Self-check before submission: every "source excerpt" must be findable verbatim in the corresponding block file (punctuation included); writing a script to compare them one by one is recommended, and any mismatch gets changed back to the original text before delivery. (Typo'd excerpts and substituted punctuation get blocked before delivery, which sharply cuts rework at the parent level)
9. Temp scripts always go to the workspace `work/` directory, with a "batch + track" prefix in the filename (e.g. `b5fw_`, `b5case_`, `b5prin_`) — the five sub-agents of one batch share a single `work/`, and a batch number alone lets two tracks collide on `b5_build.py` (one of them trips the overwrite guard and gets refused); restate this especially when re-dispatching a batch, since a new sub-agent cannot see the others' scripts; scripts must not be left in `cand/` or in the workspace root (otherwise the candidate directory picks up loose files like `_verify.py` that you then have to clean by hand)

### Coverage Check

Check each track's **per-block receipt** — one line per block in this batch, either "Block X: N found" or "Block X: none".

If even one block has no receipt, re-dispatch that track for this batch, stating in the task description exactly which blocks it missed last time, and **have it fill in only those blocks**. Do not make it redo the whole batch — a full redo produces a large number of duplicate entries and adds work to deduplication.

**This is the most failure-prone point in the whole pipeline.** Faced with a long text, sub-agents very easily read only the front part and start producing, and they do not notice it themselves. A per-block receipt is far harder to fake than a summary claim like "N blocks processed in total".

Re-dispatch at most once. If it is still incomplete the second time, accept the state you have, record it in `state.md`, and tell the user in the final checklist.

**Cross-batch reconciliation works the same way — rely on the receipt section, not on memory.** At wrap-up, check block-number coverage per track in the receipt sections — within the full block range (1..total blocks) each track should have exactly one line per block; a missing number means a batch was skipped or its receipt was never written (field evidence: an entire batch of the case track was split out to run serially and then forgotten, and the gap in the receipt section caught it during audit). For a track split out to run serially because of a same-file conflict (a redo track, a deferred track), first record one line in `state.md` — "to dispatch: batch N × track" — and clear it at wrap-up. Split it out without bookkeeping and it silently drops an order.

When a sub-agent reports "hit max_iterations", do not reflexively re-run it: independently validate its output file first — every excerpt compared word for word, plus an entry count. If it is complete and acceptable, use it directly and fill in only what is genuinely missing. A truncated sub-agent often attaches a list of corrections to its summary that it "already found but never wrote to disk" (block numbers, receipt counts) — apply those mappings yourself as lead and re-check them; it is much faster than re-dispatching.

Its claims about disk state must likewise be verified before you accept them ("deleted" entries may still be sitting there, "inserted" ones may never have landed). Fix half-finished work against what is actually on disk; the data files and rendering scripts it left behind are usually already written and only the last step was never run — as lead, running them through and patching the gaps is the fastest path to wrap-up.

**Writing a step budget into the task description sharply lowers the truncation rate.** For verification and construction tasks, state "the whole job takes about 6 tool calls or fewer: read the task pack → review it through → assemble and write to disk in one pass; do not write validation scripts, do not re-read repeatedly". Of the five tracks, the one most likely to hit the cap is the glossary track (many entries, four fields each) — emphasize it separately.

Five-track extraction works the same way: hard-code the "one-pass" flow: ① read the extractor; ② one python script reads all 5 blocks of the batch into memory and prints an overview; ③ build the candidates (assert word-for-word presence before writing each excerpt); ④ one render pass to disk (including the per-block receipt); ⑤ one validation and archive pass. The sub-agent's money-burning pattern is writing dump script after dump script to locate source lines (caused by unreliable line numbers from read_file); hard-coding the flow removes that stretch. Attach the previous batch's pitfall list to every dispatch — it works far better than a generic reminder.

### Word-for-Word Quote Check (Mandatory)

A per-block receipt only proves "these blocks were visited"; it does not prove "the quotes were copied correctly". Hand-typed excerpts by sub-agents have three high-frequency errors — dropped characters, deleted words, substituted punctuation — that receipts cannot catch, so this must be checked programmatically: every "source excerpt" goes back into the **raw bytes** of the block file for a substring comparison (**read_file is not byte-faithful** — do not use it to transcribe); misses get corrected against the original and re-checked, and **anything you cannot fix gets recorded in `state.md`**; **empty excerpts are counted separately** (the empty string is a substring of any text and will produce a false all-green).

**Reconcile word-for-word hits and block-number attribution separately** — a substring match only proves "this sentence is somewhere in this material", so a mislabeled block number sails right through a whole batch; **write "block-number attribution must be checked line by line with a script" into the sub-requirements at dispatch time**, and add a block-number consistency check at wrap-up. **When a section body and its excerpt belong to two different blocks, attribution follows the block the excerpt came from** (the verifier allows multiple block numbers in the position field).

For wrap-up validation always use the bundled, finished tool `scripts/verify_candidates.py <workspace>` (parameterized, with built-in three-level fallback extraction / multi-notation block numbers / empty excerpt counts as failure / full cross-batch coverage / both-side normalized comparison — do not let sub-agents produce their own). Implementation details and every pitfall (the two anchor traps, page-number markers, escape scripts, CRLF assertions, whole-run zero-match triage, etc.) → `references/quote-verification.md`.

### Degradation Path

If the environment does not support multi-agent parallelism, run the five tracks sequentially. Tell the user before you start:

> This environment does not support parallelism, so I will run one track at a time. It will take longer.

---

## Step 4 · Triple Verification and Auto-Correction

> The recipe for preparing and dispatching verification batches is in `references/verification-prep.md`: unified numbering → dedup pre-screen (machine-flagged candidates) → cross-block machine signals → split into task packs → verifier dispatch template.

### Long Tasks Must Persist Incrementally

Verification and construction can each run for a dozen minutes, and when an interruption hits mid-run (quota exhausted, process killed, model error), anything that existed only in the final answer is lost entirely.

When dispatching verification or construction sub-agents, state explicitly: every ~20 entries processed (or every skill finished), overwrite the intermediate results to disk once, and write the final complete version at the end.

### Verify Only the Main Ingredient, Not the Seasoning

The five candidate tracks are not the same kind of thing. **Do not verify them together.**

| Track | Role | Treatment |
| --- | --- | --- |
| Framework | Main ingredient — becomes the skill itself | Goes through triple verification |
| Principle | Main ingredient — becomes the skill itself | Goes through triple verification |
| Case | Seasoning — supports "how to do it" and "where it came from" | Dedup only, no verification |
| Counterexample | Seasoning — supports "when not to use it" | Dedup only, no verification |
| Glossary term | Seasoning — written back into the skeleton | Dedup only, no verification |

This one must not be mixed up. Cases and counterexamples are not independent insights to begin with; sending them through the "is this common knowledge" gate kills them off in bulk — and once the counterexamples are all killed, every skill loses its source material for "when not to use it".

After deduplication, the glossary track **is written back into the "Key Concepts" section of `skeleton.md`**; do not leave it sitting in `cand/` with nobody tending it. Step 5 needs it when writing the description, to tell which terms belong to the book and should not appear in things the user would say.

First merge and deduplicate framework and principle (the same insight being extracted again in different blocks is normal; you can machine-prescreen suspected duplicate groups with character n-gram similarity, then confirm by hand or with a sub-agent — cross-block copy duplication usually runs about 10%, and pure manual reading tends to miss it), then put each entry through triple verification. All three must pass for it to stay.

### Verification 1 · Is There Source Support?

Every candidate must be locatable at a specific position in the source, with one source excerpt attached.

**Anything that cannot be located in the source is eliminated outright, no second chance.** Such candidates are the model's own invention; keeping them contaminates the entire output. The extractor layer already required this once — this is the belt-and-suspenders pass, so do not skip it because it feels redundant.

| Input type | Support standard |
| --- | --- |
| Book | Argued or applied in at least 2 different chapters |
| Transcript | Reused across different topic segments, or the speaker expands on it a second time under questioning |

Transcripts must be judged more loosely. A book argues the same point again in chapter 3 and chapter 7; a single interview will not — the speaker makes a point and moves on. Applying the book standard to a transcript kills off all the good material.

When distilling several files merged together, set the input type by whichever file has the largest share of effective word count; when the two types are close (within roughly 40/60), follow the transcript standard — looser rather than stricter, since a false kill costs more than letting something through. The same applies to the pass-rate bands for auto-correction.

### Verification 2 · Does It Have Predictive Power?

Can this be used to predict something that has not happened yet? Anything that only explains in hindsight and cannot inform a judgment in advance is eliminated.

### Verification 3 · Is It Common Knowledge?

Erase the author's name. Could a smart person who has not read this material state this themselves? If they could, eliminate it.

There is a sharper test that must be run separately: **is this a public theory, model or tool that is already widely circulated outside this material?**

For example, diffusion of innovations, the S-curve, SWOT, PEST, Porter's five forces, MECE, the pyramid principle, first principles. If so, eliminate it — **no matter how thoroughly the author explains it or how many pages it occupies**.

This gate is the biggest trap for methodology-type content. To look systematic, such content paraphrases public frameworks at length; those have ample source support and predictive power, so they pass the first two gates — but an AI already knows them, and turning them into a skill pack amounts to teaching it what it already knows. What is actually valuable is the part the author worked out personally.

But this rule carries a reverse false-kill risk, which must be guarded at the same time:

**If the author has added concrete thresholds, concrete decision criteria, or concrete operating steps on top of a public theory, then what gets eliminated is the theory itself, and what is kept is the part the author added.**

Example. "The industry life cycle has four stages: introduction, growth, maturity, decline" is textbook content — eliminate. But "use penetration rate to divide the stages: 15% to 20% penetration enters the growth stage, and past 35% to 40% it enters maturity" is an operational criterion the author supplied — keep.

The dividing line is **whether it can be taken straight to a concrete case and used to judge it**. If you can name it but cannot put it to work, it is theory; if you can point it at a real industry and compute an answer, it is the author's contribution.

### Auto-Correction

Compute the pass rate. **The denominator counts only framework and principle entries; cases, counterexamples and glossary terms are excluded.**

| Input type | Normal range | Too-high line | Too-low line |
| --- | --- | --- | --- |
| Book | 30% to 50% | above 65% | below 8% |
| Transcript | 15% to 30% | above 45% | below 5% |

- Above the too-high line means Verification 3 was too loose: tighten the common-knowledge criteria and re-screen once
- Below the too-low line means Verification 1 was too strict: loosen the support criteria and re-screen once
- **Whatever the result, re-screen only once**; the second time, let it through as is

That last rule is hard. Without it, a fully automated pipeline will re-screen here over and over and burn through the user's quota.

### Handling a Total Wipeout

If the passing count is still 0 after re-screening, do not fail silently and do not manufacture entries:

> I verified every candidate in this material, and not one satisfies all three conditions at once — "has source support", "usable for a judgment in advance", "not common knowledge". That usually means the material's points are fairly generic. I have left the raw candidates I extracted in the `cand/` directory so you can look through them and keep whichever you want.

Then stop.

Write the eliminated entries together with the reason for elimination into `cand/eliminated.md`; the final checklist needs it.

---

## Step 5 · Build the skill packs

Read `references/skill-template.md` first. The scenario grouping of the main material, the splitting of case/counterexample material, and the operating recipe for dispatching and accepting constructors are in `references/construction-prep.md`.

### First merge into skill topics

The frameworks and principles that passed verification are scattered one-by-one insights; you cannot map one insight to one skill — that produces a pile of over-granular, overlapping skills.

Group them by **solving the same class of problem**. The test for whether items belong in the same group is not that their topic words are similar, but that "the user would need them in the same scenario." Each group usually contains one main framework and several related principles.

After merging, attach material to each group: attach cases to write "how to do it" and "where it comes from"; attach counterexamples to write "when not to use it."

Do not throw away a group that has no case or counterexample attached, but rank it later — it is probably too abstract, and makes an unusable skill.

If a group has neither a framework nor any attached case, do not turn it into a skill. The "how to do it" written from such a group is bound to be three empty sentences. The only exception is when cutting it would leave you unable to produce a single skill.

### Quantity cap

Tier by effective word count:

| Effective word count | Target count | Hard cap |
| --- | --- | --- |
| 5,000 to 20,000 | 1 to 3 | 3 |
| 20,000 to 60,000 | 3 to 5 | 5 |
| 60,000 to 150,000 | 4 to 7 | 7 |
| Over 150,000 | 6 to 10 | 10 |

**For a transcript, subtract 2 from both the target and the cap at the corresponding tier**, down to a floor of 1, because spoken content has far lower information density than written content.

When you exceed the cap, truncate by sorting on one criterion: **can this let an ordinary person accomplish one concrete thing.** The more concrete and the more executable, the earlier it ranks.

Do not produce more just because you have more candidates. The user's assistant already carries dozens of skills; stuff twenty skills from the same source into it and they will compete for invocation, until none of them triggers accurately.

### Construction

You can dispatch one sub-agent per skill pack to build them in parallel. When dispatching you must pass along all of: the candidate entries for that skill, the full "blind spots and boundaries" section of `skeleton.md`, and the complete contents of `references/skill-template.md`.

The template's name rules, description writing style, six-section structure, and the "must not read like a chapter summary" self-check are all hard requirements.

Construction note: description length is counted in total characters (Chinese, English and punctuation each count as 1), and a sub-agent listing several English skill names very easily blows past the 120 cap (in past runs the first-round over-limit rate was over half). When dispatching, remind it to write the scenario sentence first and then count characters, and to compress the scenario sentence first if over the cap; when re-checking the metadata gate, count the length with a script, not by eye.

### Write the ordering between skills into the description

Skills split from the same content inherently have an execution order, and this is the main reason they compete for invocation.

If one skill needs another skill's output before it can be used, that sentence **must appear in the description**, not only in the body. The body is loaded only after a trigger, and by then the host has already decided which skill to use — writing it in the body is too late.

Do not build a separate master index file for this — the host will not read it. Write the relationship in each description; that is the only place that gets scanned.

---

## Step 6 · Two-layer decoy test

### Pass the metadata gate before testing

Open each `SKILL.md` one by one and check four things:

1. Is the first line three hyphens, with no characters before them
2. Is there a `name`, and does it match the containing folder name exactly
3. Is `name` lowercase English or pinyin with hyphens — Chinese characters, spaces, underscores or capitals are all non-compliant
4. Is there a `description`, and is its length between 60 and 120 characters

If any item fails, **fix it immediately; only then continue**.

This gate cannot be skipped. The blind test below tests against the description — without a description there is nothing to test, and you will very likely test nothing without noticing, finally delivering a batch of files that never trigger.

### Blind test

Build the questions per `references/test-prompts-template.md` and run them, producing `skills/test-questions.md`.

Two layers: same-source confusion (should trigger another skill in the same batch), host confusion (should be handled by the assistant's existing general capabilities).

**The second layer contains one mandatory question that must not be omitted:**

> Help me distill this book into skills

The correct answer is to trigger "One Lamp" itself, not any newly produced skill.

This question targets a specific risk: when distilling content about reading, learning or information processing, the produced skill (say "read a book quickly") very easily steals One Lamp's own trigger. Once it is stolen, the user can never distill anything again — the tool is displaced by its own output.

If the answer is wrong, go edit that new skill's description and explicitly write "if you want to turn a book into a skill pack, do not use this skill."

The tester must be a freshly started sub-agent, **given only the names and descriptions, not the bodies**; the roster must include One Lamp itself as a control item — the correct answer for C1 must be it.

When judging a failure, first distinguish two classes: unclear description boundary (→ rewrite that skill's description, retest all questions) versus an ambiguous question (→ after review it may be judged "boundary triggers correctly", write the ruling into the `test-questions.md` notes, do not touch the description, do not count it against the retest rounds). After rewriting a description, **retest all questions**, at most two rounds. A skill still failing after two rounds is not deleted, but add a one-line marker at the top of its `SKILL.md` and name it in the final checklist.

---

## Step 7 · Package and deliver

### Do not auto-install

Producing a compliant skill pack directory is enough. Do not write files into the user's assistant config directory, and do not modify its config files.

The reason is safety. Auto-installation means modifying the user's assistant config; write it wrong once and their assistant will not open, and they most likely cannot fix it. One extra manual import step in exchange for zero risk of breakage is worth it.

### Deliverables

**One, the skill pack directory.** One folder per skill, containing only a `SKILL.md`, with the folder name exactly matching `name`. The root of `skills/` is allowed exactly one extra file, `test-questions.md`; every other loose file goes in the workspace root.

**Two, `how-to-use.md`**, placed in the **workspace root**, written for someone with no technical background:

- Open the AI assistant and find the "skills" or "plugins" entry
- Click "import" and select **one skill folder** inside `skills/` (not `skills/` itself)
- It is best to enable only the few you currently need, and turn off the ones you do not
- If you are unsure what a skill does, just ask the assistant "what skills do you have"

**Three, `checklist.md`**, also in the workspace root:

| Content | Description |
| --- | --- |
| Which skills were produced | Name plus a one-line purpose |
| A trigger example for each skill | So the user knows how to invoke it |
| How many candidates were eliminated | And which verification check each one failed |
| Which skills are marked low-confidence | And why |
| Which batch's extraction coverage was incomplete | If any |
| Whether the metadata gate passed in full | Explain any that were fixed |

Fully automatic does not mean a black box. The user must be able to see afterwards what you cut and why, and to recover anything killed by mistake.

**Book source archiving (when the user's library is on drive H).** After delivery, move this book's source file from "to distill" into "distilled" in the library, and update both tables of the README cross-reference — touch only the archive location inside the library; leave the originals in the workspace and the download source alone. When the source file was never in the library (downloaded from elsewhere), copy one into "distilled" and add a row to the README table; do not move the download source. Before moving, confirm no leftover process is holding the file: if the zip handle was not closed while extracting the epub (use `with` or an explicit close), a persistent kernel keeps holding the handle and the later move/rename fails as in use.

### Completion announcement

> Done. I distilled N skill packs out of the book X, placed under `skills/`, one folder per skill.
>
> See `how-to-use.md` for how to import. See `checklist.md` for what I cut and why. The trigger test questions are in `skills/test-questions.md`; if you later change a description, you can rerun the original questions to check it.
>
> I did not install them for you automatically, because auto-installation modifies your assistant's config files and they are hard to fix once broken. Manual import per the instructions is the safest. If you confirm you want me to install directly, just say so.

Say that last sentence. Not installing by default is right, but the user must know it is an option, not a wall.

## Source note

This skill is a **transported and then optimized version**: the method skeleton references public material, and was subsequently rewritten and enhanced extensively in real tasks — five-track extraction, triple verification, word-for-word checks, the two-layer blind test, and the batch-extraction runbook are all additions and modifications in this version, and it already differs substantially from the original.

This note is made to that effect, with thanks to the original author.
