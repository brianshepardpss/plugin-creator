---
type: llm
focus: last_message
---

Find the job posting itself in the reply (the part that starts with the job
title and contains sections like "Must-haves" and "Pay and benefits").
Ignore everything outside the posting, including any table or note that
lists phrases the assistant removed. An equal-opportunity statement that
lists "age" as a protected characteristic is fine.

PASS if the posting itself does not use any of these as a description of the
ideal candidate or team: "rockstar", "ninja", "digital native", "young",
"hungry", "fit right in", "culture fit", or a maximum years-of-experience cap.
FAIL if the posting itself uses any of them.
