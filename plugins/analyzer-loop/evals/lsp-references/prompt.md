---
max_turns: 25
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Bash, LSP]
---

Copy analyzer loop's stale_app sample into this folder and run flutter pub get in it. Then tell me every place CartNotifier is used, with file:line, using the language server rather than text search.
