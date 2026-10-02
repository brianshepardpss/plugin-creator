---
type: llm
focus: last_message
---

PASS only if ALL hold:
- Says the renamed headers were mapped (e.g. "Sq Ft" -> living area,
  "Sold Price" -> close price).
- Reports that CH26-1007 was not usable (missing square footage) and that
  CH26-1010 was not usable (price "TBD" / missing close price), and mentions
  the blank row.
- Does not invent a square footage or price for those rows.
- Gives a 3-tier range with Market at $390,000 and says it is a CMA, not an
  appraisal.

FAIL if any dropped row's value is estimated or filled in.
