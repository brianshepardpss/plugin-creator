---
name: scala-doctor
description: Use when Scala code intelligence is not working or the user is setting it up, or says "why isn't Metals working", "no LSP server available", "Claude can't see Scala errors", "set up Metals", "is my Scala setup ok", "go to definition doesn't work in Scala". Runs a read-only setup check (java, metals, cs, build tool, .gitignore, Metals logs) and prints exact install commands.
---

# Scala setup check (read-only)

This plugin's `.lsp.json` starts the command `metals` over stdio. If `metals`
is not on the PATH that Claude Code was launched with, Claude silently falls
back to grep. This skill finds out why and tells the user what to run.

## Guardrails

- Read-only. Do not install anything, edit shell profiles, settings.json,
  `.lsp.json` or `.gitignore` yourself. Print the commands; the user runs them.
  Only if the user then explicitly asks you to run a specific command, run that
  one command.
- Never suggest adding an `lsp` key to settings.json (Claude Code ignores it;
  LSP servers come from plugins).

## Procedure

1. Run the bundled checker from the project root (pass the project dir if
   the user named one):

   ```
   python3 <skill dir>/doctor.py [project_dir]
   ```

2. Show its output verbatim in a code block.
3. If the verdict is BLOCKED, list the fixes in order and add: "After fixing,
   restart Claude Code (the language server is started at session start)."
4. If the verdict is READY but the user still sees no diagnostics, check these
   in order and report which applies (read `troubleshooting.md` for details):
   - Claude Code was started before `metals` was on PATH: restart it from a
     shell where `which metals` works.
   - First build import is still running (1-5 min on sbt builds): wait, then
     edit a file again.
   - Another plugin also registers a Scala server (for example a separate
     `metals` LSP plugin): run `/plugin` and disable one of them.
   - Session is a cloud/web session: LSP servers do not run there.
   - `.metals/metals.log` shows a build import error: quote the line and fix
     the build (`sbt compile` from a terminal reproduces it).
5. End with exactly one next action for the user.

## Output shape

```
<doctor output>

Verdict: <BLOCKED|READY>
Do this next: <one command or action>
```
