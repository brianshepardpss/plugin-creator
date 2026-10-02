---
name: change-order-narrative
description: Use when the user needs to price or write up added, deleted or changed scope, or says "price this as a change order", "write up a CO request", "change order backup", "PCO for the extra work", "T&M ticket to CO", "how much do we ask for this added scope", or gives crew sizes, days, materials and markup percentages. Produces a change order request narrative in our own template with cost backup computed by a script, working shown.
---

# Change order request narrative and cost backup

`<skill dir>` below means this skill's base directory (shown when the skill
loads). Write output files to the user's working folder, not the skill dir.

This produces a Change Order Request (COR) for the user's review. It is
not an AIA document and must not copy any AIA form's text, layout or
numbering. If the user asks for "a G701" or another AIA form, say that
those forms are copyrighted and must come from a licensed AIA source; offer
this COR as the backup that goes with it.

Script: `scripts/co_calc.py` beside this file. Sample rates:
`<skill dir>/../../samples/rates.csv`.

## Steps

1. Collect: description of the change, what triggered it (RFI answer,
   owner request, directive, field condition), reference documents (RFI
   no., ASI, sketch, meeting item), labor (trade, workers, hours/day, days),
   rates (the user's rates file, or ask), materials, equipment, subcontract
   quotes, the markup percentages the user says apply, and any time
   requested. If a number is missing, ask for it; never assume a rate or
   markup.
2. Compute the cost, every time, with the script:
   ```
   python3 <skill dir>/scripts/co_calc.py --labor "Painter/Journeyman:3:8:2" --rates <rates.csv> \
     --material "<item>=<amount>" [--equipment ...] [--sub ...] \
     --oh <pct> --fee <pct> [--fee-base cost+oh|cost] [--tax <pct>] [--bond <pct>]
   ```
   Paste its tables unchanged. Do not do any arithmetic in prose. If the
   user's contract sets fee on cost only, use `--fee-base cost`.
3. Time: only if the user asks for days and gives the basis (which
   activities, how many days). Write "Time requested: <N> calendar days,
   basis: <...>" or "Time: to be determined. Contractor reserves the right
   to request an extension of time." Never state that time is owed.
4. Run `python3 <skill dir>/../daily-report/scripts/notice_flags.py <notes file>` on the
   notes behind the change, if any. If the change came from a field
   condition, delay or directive, add the notice line in the template.
5. Write the COR with this template:

```
CHANGE ORDER REQUEST <COR no. or [COR-__]>
Project: <...>                 Date: <YYYY-MM-DD>
To: <Owner / Architect>        From: <Contractor>
Reference: <RFI / ASI / directive / meeting item / field condition, with dates>

1. Description of change
<What is added, deleted or changed, where, and in what quantity. Plain
facts, no adjectives.>

2. Reason for change
<What happened and what document directed it, quoted where possible.
Neutral: "The Owner requested..." / "RFI-006 response revised...". No
statements of fault or entitlement.>

3. Cost
<tables from co_calc.py>
Exclusions: <...>   Assumptions: <...>   Quote valid for <N> days.

4. Time
<from step 3>

5. Notice
<If applicable:> This request is submitted as notice of a possible change
to the Contract Sum and/or Contract Time. [Check the notice and claim
provisions of your contract for required timing, recipient and format
before sending.]

6. Reservation of rights
[RESERVATION OF RIGHTS - have your PM or counsel insert your company's
approved language here. Do not send without it reviewed.]

Attachments: <quotes, T&M tickets, photos, sketches>
Draft for professional review. Not legal advice.
```

## Guardrails

- Never write that the contractor "is entitled to", "is owed" or "must be
  paid"; describe facts and the request.
- Never state a contract deadline or notice period as fact. If the user
  asks how long they have, say notice periods vary by contract and can be
  short, point them to the notice and claims articles of their own
  contract, and offer the delay-notice skill.
- No pay applications or schedule-of-values forms (out of scope).
