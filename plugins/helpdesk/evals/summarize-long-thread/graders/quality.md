---
type: llm
focus: last_message
---

Ground truth for ticket 1030 (25 messages): the customer's latest ask is (a) confirm
the fix will also clean up existing duplicate bookings and (b) whether billing has
decided on a credit for INV-20931. Steps already tried: reconnecting Google
Calendar, clearing cache, checking two-way sync, one-way sync, re-authorizing,
checking time zones, sending the sync log. Engineering bug ENG-4471; the agent
committed to an update by Tuesday 2026-10-06. The only identifiers in the thread are
BK-55102, BK-55117, ENG-4471 and INV-20931.

PASS only if ALL hold:
1. The summary itself is 150 words or fewer (ignore any short offer line after it).
2. It states the current ask (fix cleanup of duplicates and/or the credit question).
3. It lists steps already tried (at least three of those above).
4. It states the open commitment with its date (update by 2026-10-06).
5. It mentions no order, invoice, booking or bug number other than those four identifiers, and does not promise a credit amount.
FAIL otherwise.
