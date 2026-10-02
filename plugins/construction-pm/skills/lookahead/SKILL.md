---
name: lookahead
description: Use when the user wants a 3-week look-ahead, short-interval schedule or weekly look-ahead from a schedule export, or says "make my three week look ahead", "what's coming up the next few weeks", "what activities are blocked by submittals or RFIs", or "look-ahead for the foremen meeting". Takes a P6, MS Project or spreadsheet schedule CSV plus the submittal register and RFI log; produces a week-by-week table with constraints and a procurement watch list.
---

# Three-week look-ahead with constraints

`<skill dir>` below means this skill's base directory (shown when the skill
loads). Write output files to the user's working folder, not the skill dir.

Script: `scripts/lookahead.py` beside this file. Samples:
`<skill dir>/../../samples/schedule.csv`, plus the register and RFI log the other
skills produce (`<skill dir>/../../samples/expected/submittals.csv`,
`<skill dir>/../../samples/expected/rfis_after_add.csv`).

## Steps

1. Get the schedule export (CSV). If the user has an .xlsx or .mpp, ask them
   to export CSV with columns Activity ID, Activity Name, Start, Finish,
   Spec Section (if they track it) and Responsible. Get the as-of date
   (default: next Monday, ask if unclear) and number of weeks (default 3).
2. Run:
   ```
   python3 <skill dir>/scripts/lookahead.py <schedule.csv> --as-of <YYYY-MM-DD> [--weeks 3] \
     [--submittals <submittals.csv>] [--rfis <rfis.csv>] [--csv lookahead.csv]
   ```
3. Present the script's table unchanged, then:
   - Constraints: for each constrained activity, the submittal or RFI
     holding it and who has the ball.
   - Procurement watch: the script's list of submittals due by the window
     end, in Submit By order; call out LONG-LEAD rows first in your summary.
   - Activities with no Spec Section cannot be checked against the logs;
     say how many.
4. Offer: follow-up emails for constraints, or a printable version for the
   foremen meeting.

## Guardrails

- The look-ahead reflects the schedule file as given. Do not re-sequence,
  change durations or claim float; if the user asks "can we make this
  date", list what the logs say is blocking it and stop there.
- Do not describe a slipping activity as an owner-caused delay. If the user
  says it is, offer the delay-notice skill.
