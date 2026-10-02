---
name: rfi
description: Use when the user needs to write, log or chase a Request for Information, or says "draft an RFI", "write up an RFI about", "this conflicts with the drawings, need to ask the architect", "add it to the RFI log", "which RFIs are overdue", "how long has RFI 3 been open", or "close out RFI-004". Works from field notes, photos, spec text and the rfis.csv log; produces a cited RFI draft and updates the log with the next number and computed days open.
---

# RFI drafting and RFI log

`<skill dir>` below means this skill's base directory (shown when the skill
loads). Write output files to the user's working folder, not the skill dir.

Scripts live in `scripts/` beside this file. Sample notes and log:
`<skill dir>/../../samples/notes/walk-notes.txt`, `<skill dir>/../../samples/logs/rfis.csv`, spec
text in `<skill dir>/../../samples/spec/`.

## Draft an RFI

1. Find the facts. Read the user's notes or photo and the relevant spec
   section. Identify: the exact conflict or gap, the spec section and
   article (for example `08 71 00 / 3.4.C`), the drawing sheet and detail,
   the location (room, door, gridline), and what work it holds up.
   If the spec text is available, quote the governing sentence. If a cite
   is not in the material you have, write `[confirm: sheet/detail]` instead
   of inventing one.
2. Ask ONE question. If the notes contain two issues, write two RFIs (or
   offer to) rather than one RFI with two questions.
3. Proposed solution: the contractor's suggested resolution from the notes,
   phrased as a proposal for the design team to accept or reject. If none,
   write "Contractor requests direction."
4. Impact: tick Cost and Schedule as Yes / No / Possible / TBD from the
   notes. Never put a dollar or day figure here unless the user gave it.
   If the notes mention extra cost or time, add the line from the template
   below reserving the right to submit a change request. Do not say the
   contractor is entitled to anything.
5. Response needed by: date work is affected (from the notes or schedule),
   else the default 7 calendar days the script applies.
6. Write it with this template, then show it before logging:

```
RFI <number from log> - <short subject>
Project: <project>            Date: <YYYY-MM-DD>
To: <architect/engineer>      From: <name, company>
Spec reference: <NN NN NN / article>     Drawing reference: <sheet/detail>
Location: <room / door / gridline>

Question:
<one question, answerable in a sentence or a sketch>

Background:
<2-5 sentences: what the documents say, quoted where possible, and what
was found. Facts only.>

Proposed solution:
<contractor's proposal, or "Contractor requests direction.">

Impact:  Cost [ ] Yes [ ] No [x] Possible  /  Schedule [ ] Yes [ ] No [x] Possible
Response needed by: <date> to avoid affecting <activity/date>.
<If impact is Yes or Possible:> The Contractor reserves the right to submit
a change request for cost or time if the response changes the Work.

Attachments: <photos, markups>
```

7. Log it (after the user is happy with the draft, or straight away if they
   asked you to log it):

```
python3 <skill dir>/scripts/rfi_log.py add --log <rfis.csv> --subject "<subject>" \
  --spec-ref "<NN NN NN / art>" --drawing-ref "<sheet>" --sent <YYYY-MM-DD> \
  [--response-days 7 | --due YYYY-MM-DD] --ball "<Architect>" \
  --cost-impact <Yes|No|Possible|TBD> --schedule-impact <...>
```

Use the RFI number the script printed in the final draft. If the user has
no log yet, the script creates one; tell them where.

8. Run the notice screen on the notes the RFI came from:
   `python3 <skill dir>/../daily-report/scripts/notice_flags.py <notes file>`. If it
   flags anything, say: "Possible notice event - check the notice
   provisions in your contract today." and offer the delay-notice skill's
   letter. Do not state a deadline.

## Report on the log

```
python3 <skill dir>/scripts/rfi_log.py report --log <rfis.csv> --as-of <YYYY-MM-DD>
```

Show the table as printed (days open and days past due are calendar days,
computed by the script). Then list open RFIs past due with ball in court,
and offer a short follow-up email for each. Close an answered RFI with
`python3 <skill dir>/scripts/rfi_log.py close --log <rfis.csv> --rfi RFI-003 --date <date> --answer "<summary>"`.

## Guardrails

- No engineering judgments: do not tell the user a structural, fire-rating
  or life-safety condition is acceptable. Route it to the engineer of record
  in the RFI question.
- Do not answer the RFI on the architect's behalf.
- Keep personal names to the To/From lines.
