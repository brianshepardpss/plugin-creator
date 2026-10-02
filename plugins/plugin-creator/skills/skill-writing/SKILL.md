---
name: skill-writing
description: Use when writing or improving a SKILL.md, agent, or slash command for a Claude plugin, or when a skill does not trigger, triggers at the wrong time, or gives inconsistent results. Covers trigger descriptions, procedure bodies, supporting files, bundled scripts for exact math, and guardrails.
---

# Write skills that trigger reliably and work the same way every time

## The description is the trigger

Claude decides whether to load a skill from its `description` alone. Write it
as: "Use when <situation>, or when the user says <3-6 phrases real users
type>. <What it produces>." Use the user's vocabulary ("plate cost", "punch
list", "MR"), not yours. Name the inputs it expects (a CSV export, a PDF).
Two skills whose descriptions overlap will fight; make each one own a
distinct job.

## The body is a procedure

- Numbered steps, imperative voice, under ~150 lines. Say what to read, what
  to compute, what to output and in what shape.
- Put the output format in the skill as a literal template. Consistent
  output is what makes a plugin feel like a product.
- Long reference material (field mappings, rubrics, legal rules, style
  guides) goes in files beside SKILL.md. Tell Claude when to read each one:
  "Read `fields.md` only if the CSV headers don't match."
- Refer to bundled files by path relative to the skill directory. Claude
  sees the skill's base directory when it loads.

## Never let the model do arithmetic in prose

Any number a user might act on (cost, percentage, date, deadline, total)
comes from a bundled script. Standard-library Python only, so it runs in
Claude Code, Cowork and claude.ai. The skill says: run the script, show its
output, explain it. Put the formula in the script's docstring so users can
audit it.

## Guardrails are steps, not disclaimers

Write each rule where it applies, as an action: "Before showing listing
copy, run `fair_housing.py` on it and fix every flagged phrase." Rules
that only appear in a README are ignored. Cover:

- What the plugin must never do (score candidates, assert an allergen is
  safe, state a contract deadline as fact, write to a system without
  confirmation).
- Personal data: minimize it, don't repeat it back unnecessarily, never put
  it in feedback or logs.
- Writes to external systems: always show the exact change and wait for a
  yes.

## Sample data makes the first five minutes work

Bundle realistic, clearly fake data in `samples/` with the messiness real
exports have (odd column names, blank rows, a duplicate). The hero command
should accept `sample` as its input, so a new user sees value before
connecting anything.

## Agents and commands

- A subagent (`agents/<name>.md`) is for a self-contained job whose
  intermediate work would clutter the main conversation: long research, a
  review pass, scanning many files. Give it only the tools it needs.
- A slash command (`commands/<name>.md`) is a named entry point for the hero
  workflow. Commands should be thin: they call skills.

## Test every skill

For each skill, write at least one eval case that would fail if the skill
did not load (see the plugin-evals skill). Run with ablation on: if the
score without the plugin is the same as with it, the skill adds nothing.
