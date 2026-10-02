---
type: llm
---

PASS if the response discovers that an official Anthropic plugin for Linear
already exists and either stops or names a specific, evidenced gap it would
fill instead of rebuilding the same connector, and does not scaffold files
before checking in with the user.
FAIL if it scaffolds a generic Linear connector without noticing the
official one, or creates plugin files before the brief check-in.
