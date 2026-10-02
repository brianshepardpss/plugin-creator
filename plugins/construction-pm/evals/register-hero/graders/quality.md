---
type: llm
focus: last_message
---

The golden list for the three sample sections is 23 items:
08 71 00: 1.3.A-E (product data, hardware schedule, wiring diagrams, keying schedule, samples), 1.4.A-B, 1.5.A-C, 3.3.A (hardware consultant inspection report).
09 91 23: 1.03.B-F (product data, samples, product list, VOC certification, maintenance material) and 1.04.A mockups.
23 05 93: 1.4.A-E and 3.3.A final TAB report.

PASS if all of these hold:
- The reply (or the register it describes) accounts for at least 22 of the 23 items, each identified by section and article.
- The door hardware (electrified locks / 08 71 00 action items) is flagged long-lead.
- The reply identifies the earliest due items (door hardware around 2026-10-05 and/or TAB qualification data 2026-10-08) and does not invent submittal items that are not in the spec.
- The output is described as a draft to verify against the spec (or equivalent wording).
FAIL if items are invented, the long-lead flag on hardware is missing, or fewer than 22 items are present.
