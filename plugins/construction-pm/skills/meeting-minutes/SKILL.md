---
name: meeting-minutes
description: Use when the user wants minutes written from an OAC meeting, owner-architect-contractor meeting, sub coordination meeting, foremen meeting or preconstruction meeting, or says "write up the meeting minutes", "turn this transcript into minutes", "what action items came out of the OAC", "update the action item log", or "carry forward the open items". Produces minutes in item-number carry-forward format (old business keeps its numbers) and updates actions.csv with owners and due dates.
---

# Meeting minutes with carried-forward action items

`<skill dir>` below means this skill's base directory (shown when the skill
loads). Write output files to the user's working folder, not the skill dir.

Item numbers are MEETING.SEQ (7.03 = meeting 7, item 3). Old business keeps
its original number until closed. This is the format most GCs use so an
item can be traced across meetings.

Script: `scripts/minutes_log.py` beside this file. Samples:
`<skill dir>/../../samples/notes/oac-meeting-transcript.txt`, `<skill dir>/../../samples/logs/actions.csv`.

## Steps

1. Get the meeting number and date from the transcript or the user. If the
   user has an action log CSV, show open items first:
   `python3 <skill dir>/scripts/minutes_log.py carry --log <actions.csv> --as-of <meeting date>`
2. Read the transcript. For each open item, decide from what was SAID:
   close (with what resolved it), update (new due date, owner or note), or
   not discussed. For each new commitment, capture: description (verb
   first), owner (company or role, not just a first name), due date if one
   was stated. If no date was stated, leave due blank and list it under
   "Needs a date". Transcripts self-correct ("no, that was today, sorry");
   use the corrected statement.
3. Write the changes as `ops.json` (see the script docstring: close /
   update / add) and apply them:
   `python3 <skill dir>/scripts/minutes_log.py apply --log <actions.csv> --meeting <N> --date <YYYY-MM-DD> --ops ops.json`
   Use the script's OLD BUSINESS and NEW BUSINESS tables in the minutes.
   Never number items yourself.
4. Run the notice screen on the transcript:
   `python3 <skill dir>/../daily-report/scripts/notice_flags.py <transcript file>`.
   Review each hit. Directives to add or change scope, and statements like
   "we'd want that in writing", go under "Items with possible cost/time or
   notice implications" with the neutral wording below.
5. Write the minutes with this template.

```
MEETING MINUTES - <Project>
Meeting: <type> No. <N>    Date/time: <...>    Location: <...>
Attendees: <name - company (role)>, ...    Absent/late: <...>
Prepared by: <...>   Next meeting: <date/time>

OLD BUSINESS
<table from the script>

NEW BUSINESS
<table from the script>

DISCUSSION NOTES (by topic, facts and decisions only)
- Schedule: ...
- Submittals / RFIs: ...
- Owner items: ...

ITEMS WITH POSSIBLE COST/TIME OR NOTICE IMPLICATIONS
- <item no> <what was said, by whom>. This may be a change or notice event;
  confirm in writing and check the notice provisions in your contract.

NEEDS A DATE: <items with no due date>

These minutes are the preparer's record. Attendees should report
corrections in writing within <N> days (use the period your contract or
meeting procedures set; if unknown, leave as "[per project procedures]").
```

## Guardrails

- Minutes record what was said; do not add commitments nobody made, and do
  not soften or strengthen what someone said.
- An architect's or owner's verbal direction in a meeting is recorded as
  stated with "confirm in writing"; never describe it as an approved change.
- Do not state whether anyone is entitled to cost or time.
- Use roles and companies in the action table; keep personal contact
  details out of the log.
