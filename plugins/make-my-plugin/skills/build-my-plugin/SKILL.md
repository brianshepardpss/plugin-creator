---
name: build-my-plugin
description: Use after WORKFLOW.md exists, or when the user says "build it", "make the plugin", "package it", or "give me the file to install". Builds a private plugin from WORKFLOW.md, tests it on one of the user's examples, and packages a .plugin file they can install with one click.
---

# Build, test and package the user's plugin

Read WORKFLOW.md. If it is missing, run the capture-workflow skill first.

## 1. Build the folder

Pick a short kebab-case name from the assistant's name (never starting with
`claude-` or `anthropic-`). Create `<name>/` with:

- `.claude-plugin/plugin.json`:
  `{"name": "<name>", "displayName": "<Assistant name>", "version": "1.0.0",
  "description": "<task sentence>", "author": {"name": "<user's name or business, if given, else 'Me'>"},
  "skills": ["./skills/"]}`
- `skills/<name>/SKILL.md`:
  - frontmatter `name: <name>` and a `description` that starts "Use when"
    and includes every trigger phrase from WORKFLOW.md.
  - body: the steps, the literal output template, the Always and Never
    rules written as steps ("Before finishing, check that..."), the
    audience and tone, and one short example (anonymized) from their
    examples.
- `skills/<name>/examples/`: their anonymized examples as text files; the
  skill body says to read them for style before writing.
- `skills/<name>/calc.py` ONLY if WORKFLOW.md lists calculations: standard
  library Python, one function per rule from WORKFLOW.md, with a docstring
  stating the rule. The skill says to run it for every number.
- `README.md`: two plain paragraphs: what it does, and how to update it
  ("tell Claude what to change and ask it to rebuild").

## 2. Test on their own example

Take the inputs behind one of their examples, follow the new SKILL.md
exactly as written, and produce the output. Compare it to their real
example and show both side by side. Fix the SKILL.md for every difference
the user cares about, then test once more.

## 3. Package

Run `python3 <this skill dir>/package.py <name>`. It zips the folder into
`<name>.plugin` and prints where it put it. In Cowork, if an outputs folder
exists, copy the file there so it appears in the chat with an install
button. Then tell the user, in plain words:

- Cowork / claude.ai: "Click the file above and choose Install" (or upload it
  in Settings > Plugins if no button appears).
- Claude Code: `/plugin install` from a local folder, or keep the folder and
  add it as a local marketplace.

Their data stays theirs: say that the plugin and examples live only in their
account and nothing was shared.
