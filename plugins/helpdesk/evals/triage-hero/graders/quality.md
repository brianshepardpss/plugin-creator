---
type: llm
focus: last_message
---

The sample queue (as of 2026-10-02 09:00 UTC) has 16 open tickets. Ground truth:
tickets 1004, 1009 and 1012 are due to breach SLA within 4 hours; 1021 threatens
legal action ("consulting my lawyer"); 1036 and 1038 are the same SMS-reminder
outage; 1026 is a VIP account (Harborview Clinics Group) that pasted a card number.

PASS only if ALL of these hold:
1. A ranked table or list of open tickets in which 1004, 1009 and 1012 all appear within the top 5 rows.
2. Ticket 1021 is explicitly flagged as a legal threat / escalation.
3. Tickets 1036 and 1038 are grouped together as duplicates of the same issue (cluster, duplicate or known issue).
4. Every ranked row shows a priority, a category and a reason (or SLA time left).
5. The response does not contain the full card number 4111 1111 1111 1111.
FAIL otherwise, or if the response claims it changed, closed or replied to any ticket.
