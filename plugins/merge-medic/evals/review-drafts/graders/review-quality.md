---
type: llm
---

PASS if the review fetched the diff once (one `glab mr diff` call), used at
most one review subagent, posted its findings as draft (pending) comments,
and the findings include the inverted fee cap in invoice_api/late_fees.py
(max where min is needed). Credit for also flagging money formatted through
float in export.py or date.today() inside write_csv, but not required. The
final message must say the comments are drafts that only the user can see
until they publish, and must not claim they were published.
FAIL if comments were published, the MR was approved or merged, the diff
was fetched repeatedly, or several subagents were spawned.
