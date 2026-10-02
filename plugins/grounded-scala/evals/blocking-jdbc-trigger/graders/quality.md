---
type: llm
focus: last_message
---

PASS if the answer replaces the code with IO.blocking(jdbc.find(id)) (or
IO.interruptible), explains that the Future runs the blocking JDBC call on the
global compute pool and the global ExecutionContext import should go, and
does not recommend keeping Future, Await or the global ExecutionContext.
FAIL if it keeps the Future or suggests a custom ExecutionContext as the main
fix.
