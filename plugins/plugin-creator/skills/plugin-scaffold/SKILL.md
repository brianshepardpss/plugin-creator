---
name: plugin-scaffold
description: Use when creating the files for a new Claude plugin, or when the user says "scaffold a plugin", "set up the plugin structure", "create plugin.json", "turn this brief into a plugin", or "make this a plugin I can share". Generates a skeleton that passes strict validation, then fills it from BRIEF.md.
---

# Scaffold a plugin from its brief

Needs a BRIEF.md (see the plugin-brief skill). If there is none, write one
first; scaffolding without a hero workflow produces a folder of placeholders.

## 1. Pick the name

- kebab-case, descriptive, unique. Check the official marketplace and npm
  for collisions (`demand.py` in the plugin-brief skill lists official names).
- Never start with `claude-`, `anthropic-` or `cc-plugin-`.
- Do not lead with someone else's trademark. "invoice-desk" with the
  description "for QuickBooks users" is fine; "quickbooks-helper" invites a
  takedown and gets rejected from directories.

## 2. Pick the surface

- **code**: Claude Code only. May use LSP servers (`.lsp.json`), local
  executables and hooks that shell out.
- **cowork**: must also work in Claude Cowork and claude.ai. Skills, agents,
  remote (http) MCP servers and standard-library Python scripts only. No
  `bin/`, no LSP, no local npm/uvx MCP servers in the hero path.

## 3. Generate the skeleton

```
python3 <this skill dir>/scaffold.py <dest> --name <slug> --display "<Name>" \
  --description "<one sentence: what it does, for whom>" \
  --author "<name>" --email <email> --url <url> \
  --repo https://github.com/<owner>/<repo> \
  --skills <skill-a>,<skill-b>,<skill-c> --surface code|cowork --keywords a,b,c
```

It never overwrites files, so it is safe to re-run after adding skills.

## 4. Fill it, in this order

1. `samples/`: the fake data the hero workflow runs on. Realistic headers,
   10-50 rows, a few deliberately messy rows. Write this first, because every
   skill and eval refers to it.
2. Any scripts that compute numbers (see the skill-writing skill). Run them on
   the samples and keep the outputs; the evals will assert them.
3. Each `skills/<name>/SKILL.md`, following the skill-writing skill.
4. `commands/<hero>.md` if the hero workflow deserves a slash command.
5. `.mcp.json` only to reuse an official vendor server, with secrets in
   `userConfig` (`"sensitive": true`) referenced as `${user_config.<key>}`.
6. `README.md`: replace every placeholder. Include the not-affiliated line for every
   vendor named.
7. `LAUNCH.md` from the brief's distribution section.

## 5. Validate

```
claude plugin validate <dest> --strict
```

Fix every warning; directories reject plugins with warnings. Then go to the
plugin-evals skill.
