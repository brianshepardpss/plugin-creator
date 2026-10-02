---
name: capture-workflow
description: Use when someone wants Claude to do a task "the way I do it", wants to automate or standardize something they do repeatedly, or says "make me a plugin", "make me a template", "I do this every week", "can you learn how I write these", or "make Claude do this my way". Interviews a non-technical user and writes WORKFLOW.md describing the task precisely enough to build a plugin from.
---

# Capture how this person does the task

The user is an expert in their work, not in software. No jargon: never say
skill, frontmatter, manifest, MCP or JSON. Say "your assistant", "the steps",
"your examples".

## Interview (one question at a time, at most ~8 questions total)

1. "What do you do, and which task eats the most time or happens most
   often?" If they list several, pick the one that is most repetitive and has
   a clear finished product (a document, an email, a table, a checklist).
2. "Walk me through the last time you did it. What did you start with?"
   (Inputs: a form, an email, a spreadsheet, notes, a PDF.)
3. "Can you paste or attach two or three past examples of the finished
   thing?" These are the most valuable input by far. If they have none, ask
   them to describe one in detail and say the result will be less exact.
   Remind them to remove anything private (client names, account numbers)
   or offer to replace those with placeholders for them.
4. "What makes one of these good versus just OK?" (Quality bar.)
5. "Is there anything it must always include, or must never say or do?"
   (Rules, legal lines, tone, things that got them in trouble before.)
6. "Who reads the finished thing?" (Audience and tone.)
7. "Are there numbers or dates in it?" If yes, ask how each is worked out;
   these will be computed by a small script, never guessed.
8. "What would you call this assistant?"

## Write WORKFLOW.md

In the current folder:

```
# <Assistant name>
Owner's role: <role>
Task: <one sentence>
Trigger phrases: <5 ways they'd ask for it, in their words>
Inputs: <what they start with, formats>
Steps: <numbered, as they described, made precise>
Output template: <literal structure distilled from their examples>
Quality bar: <their words>
Always: <rules>
Never: <rules>
Audience and tone: <...>
Calculations: <each number and its exact rule, or "none">
Examples: <file names or pasted blocks, with private details replaced>
```

Read it back as one plain paragraph ("Your assistant will take X, do Y, and
give you Z, always A, never B. Right?") and fix anything they correct.
