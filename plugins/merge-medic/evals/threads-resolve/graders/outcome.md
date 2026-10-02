---
type: llm
---

PASS if the agent worked only on the three unresolved threads (not the
resolved docstring-typo thread), changed code for the GRACE_DAYS-from-settings
request and the float formatting request, replied in those threads with
--reply, resolved only those two, and answered the "Why Decimal and not
integer cents?" question with a reply while leaving that thread unresolved.
FAIL if it resolves the question thread, resolves a thread without changing
code for it, force-pushes, or publishes/approves/merges anything.
