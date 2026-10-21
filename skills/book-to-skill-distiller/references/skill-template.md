# Skill Pack Template and description Writing Guide

## 1. File structure

One folder per skill, containing only one `SKILL.md`:

    skills/
    ├── <name-1>/
    │   └── SKILL.md
    └── <name-2>/
        └── SKILL.md

The folder name must match the `name` field exactly. No loose files may appear in the `skills/` root.

## 2. SKILL.md skeleton

**The first line of the file must be three hyphens**, with no blank line, heading or any other character before it. The three hyphens on the first line of the code block below are part of the file content and must be written in exactly as they are; they are not a code-block delimiter.

```
---
name: <content-slug>-<skill-topic>
description: <60 to 120 characters, see below>
---

# <skill display name>

## When to use it

<the specific problem situation, described in the words the user would use>
<if another skill has to be used first, say so here, and the same sentence must also appear in description>

## Core judgement

<one to three sentences, an opinionated claim>

## How to do it

1. <executable action>
2. <executable action>
3. <executable action>

## Judgement criteria

Done right you will see: <observable signal>

Done wrong you will see: <observable signal>

## When not to use it

<failure scenarios, from the skeleton's blind spots and boundaries. Cannot say "none".>

## Source

From <content title> <chapter or timestamp>

Original: <one-sentence excerpt>
```

## 3. The name field

- Lowercase English or pinyin, joined only with hyphens
- No Chinese, no spaces, no underscores
- Length no more than 64
- Must carry a content-slug prefix, otherwise distilling a second book will collide
- **Must match the folder it sits in exactly**

The display name goes in the body's level-one heading, not into `name`.

## 4. The description field

This is the only field that decides whether the skill gets triggered correctly, and the only content the host scans residently. The body is loaded only after a trigger, so **anything that affects "should this trigger me" must appear here**.

Rules:

- Keep it between 60 and 120 characters
- Write "when to use it", not "what this skill is"
- Use words the user would actually say out loud, not terms from the book
- **Put the trigger sentence first and close it within the first 57 characters** — the host's skill list truncates for display, and a trigger sentence cut off outside the window might as well not be written. Standard form: "Use when you <situation>."
- Must state when not to use it — best landed as an exclusion sentence at the end: "To <A> or <B>, don't use this." (In blind tests this form triggers most accurately.)
- If there is a prerequisite skill, name it here

Badly written:

> This skill provides a business decision framework grounded in first principles to help users make strategic judgements.

All abstract nouns, no user talks like that, and no exclusion condition, so it triggers at random.

Well written:

> Use when the user is weighing whether to take on a new business, a new project or a new direction — whether to invest, whether it is worth doing. Gives a checklist for deciding whether to do it. If the decision is already made and they are only asking how, don't use this skill.

## 5. Write nothing but these two fields

Do not write `allowed-tools`, version numbers, or an author. These skills are pure method, they need no tool permissions, and leaving the field empty equals least privilege, which makes them easier to clear security review on import.

## 6. One self-check is mandatory when you finish

Cover the "Source" section and reread the skill. What does it read like?

- Like "what chapter X of this book talks about" → **failed, rewrite**
- Like "here is what to do, step by step, when you hit this problem" → passes

This is the easiest failure mode to slide past. The content itself is usually one topic per chapter, so writing it straight through silently turns the output into a chapter summary — looks complete, is unusable. A skill is meant to be used, not read.
