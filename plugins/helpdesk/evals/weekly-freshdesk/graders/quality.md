---
type: llm
focus: last_message
---

Ground truth from the bundled script for the window 2026-09-25 to 2026-10-02:
30 tickets created (prior window 10, +200.0%); top drivers billing 5, access 4,
booking-form 4 (then several categories at 3); SLA misses 2 (tickets 1018 and 1024),
prior window 2; CSAT 11 rated, 9 good, 2 bad (81.8% good; detractors 1018 and 1031);
macro candidates booking-form, data-export, timezone; KB-gap candidates booking-form
and timezone. The CSV mixes status names with Freshdesk numeric codes (2 open,
3 pending, 4 resolved, 5 closed; priority 1-4).

PASS only if ALL hold:
1. Top drivers name billing with 5 tickets, and access and booking-form with 4 each (order between the two 4s does not matter).
2. SLA misses are reported as 2 (1018 and 1024).
3. At least one macro candidate and at least one KB-gap candidate are named, from the lists above.
4. Ticket volume is 30 this window vs 10 prior, and no count or percentage in the report contradicts the ground truth.
FAIL otherwise.
