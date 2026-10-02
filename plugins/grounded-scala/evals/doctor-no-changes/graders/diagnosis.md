---
type: llm
focus: last_message
---

PASS if the answer reports the result of an actual check (java, metals on
PATH, build tool detection), names the concrete cause it found (for example:
no Scala build file in the current directory so Claude Code must be started
from the project root, or metals missing / not on PATH), gives the exact
command or action to fix it, says to restart Claude Code after fixing, and
made no changes (no installs, no edits to shell profiles or settings).
FAIL if it suggests adding an "lsp" key to settings.json, installs or edits
anything, or gives only generic advice without having checked.
