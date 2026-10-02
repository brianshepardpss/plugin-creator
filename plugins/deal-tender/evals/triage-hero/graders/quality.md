---
type: llm
focus: last_message
---

PASS if all of the following hold:
- The reply flags 8 stale deals (Acme Anvil Warehouse Robotics Pilot, Globex Fleet Telematics, Initech Payroll Integration, Bluebird Bakery, Copperline Dental, Harborview Hotels, Pinecrest Schools, Vantage Freight) and 3 past-close deals (Northwind Traders, Summit Outdoor, Riverside Clinic), each with a reason (days idle or close date passed).
- It does NOT flag as stale "Lumen Labs", "Initech - Analytics Add-on" or "Acme Anvil - Support Renewal 2027" (they have upcoming activities).
- The list is ranked, and at least one follow-up email draft is included.
- Any CRM changes are presented as proposals awaiting approval, not as already applied.
FAIL otherwise.
