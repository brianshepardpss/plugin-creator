---
description: Opt in to the metals-mcp server for this project (compile, test, inspect, find-dep tools). Shows the command and asks before adding anything.
---

The user wants the metals-mcp tools in addition to the Metals language server
this plugin already provides. It is opt-in because it starts a second Metals
JVM (expect roughly 1 GB more RAM) and its own build connection.

1. Run `which metals-mcp`. If missing, tell the user to run
   `cs install metals-mcp` (install Coursier first if `cs` is missing; the
   scala-doctor skill prints that command) and stop.
2. Show the exact command you would run, with the absolute project path:

   ```
   claude mcp add metals -- metals-mcp --workspace <absolute project root> --transport stdio
   ```

   This uses Claude Code's default local scope (this project, this user, not
   committed). Mention `-s project` only if the user wants to share it with
   the team via `.mcp.json`.
3. Ask: "Add it now? (yes/no)". Run the command only on an explicit yes.
4. After adding, tell the user to restart Claude Code (or run `/mcp`) and that
   the first start imports the build. Point out the useful tools: compile-file,
   test, inspect, get-usages, find-dep, format-file.
5. To remove later: `claude mcp remove metals`.

Never edit settings files by hand for this and never add the server to the
plugin itself.
