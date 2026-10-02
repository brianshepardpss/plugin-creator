---
name: grant-tracker
description: Use when the user wants to track grant deadlines, LOI and application due dates, or interim and final report due dates from an RFP, award letter or grant agreement, or says "add these deadlines", "when are my reports due", "what's due this month", "put this in my calendar", "track this award". Keeps grants/tracker.csv and a calendar file (deadlines.ics) with reminders 14 and 3 days before each date.
---

# Grant deadline and reporting tracker

Script: `../../scripts/tracker.py` relative to this skill's base directory.
Tracker file: `grants/tracker.csv` in the user's folder (created on first
add); calendar: `grants/deadlines.ics` (rewritten on every change).
Demo award letter: `../../samples/award-letter.md`.

## Add from a document

1. Read the RFP, award letter or agreement. List every obligation with a
   date: LOI, application, signed agreement, payment request, interim and
   final reports, site visits.
2. For each, record the date exactly as written. Relative dates ("6 months
   after the start of the grant period", "30 days after the period ends")
   become expressions the script computes; never compute them yourself:
   - start + 6 months: `"2026-10-01 +6 months"`
   - end of a 12-month period: `"2026-10-01 +12 months -1 day"`
   - 30 days after that end: `"2026-10-01 +12 months -1 day +30 days"`
   - 30 days from the letter date: `"2026-09-18 +30 days"`
3. If a date is ambiguous (no year, "early spring", business vs calendar
   days, missing time zone), ask the user instead of guessing, and add only
   the clear ones.
4. Write a JSON list (`funder`, `item`, `type` = loi|application|report|agreement|payment|other,
   `due`, `time`, `amount`, `source` = file name and section, `notes`)
   to `grants/new-deadlines.json` and run:
   `python3 ../../scripts/tracker.py add-json --tracker grants/tracker.csv grants/new-deadlines.json`
5. Show the script's table. In `notes`, record what each report must
   contain if the document says (e.g. "narrative + financial").

## Other requests

- "What's due soon?": `tracker.py list --tracker grants/tracker.csv --within 60`
- Mark submitted: `tracker.py done --tracker grants/tracker.csv --id <n>`
- Calendar: tell the user to import `grants/deadlines.ics` into Google
  Calendar (Settings > Import), Outlook or Apple Calendar. Grant Desk does
  not write to any calendar itself.

## Reply

```
Added <n> deadlines from <document>:
<script table>
Computed dates: <item>: <expression> = <date> (shown so you can check)
Questions: <ambiguous dates, if any>
Files: grants/tracker.csv, grants/deadlines.ics
```

Always end with this human review checklist: "Confirm dates against the
signed agreement; the funder's document governs. Check time zones and
whether 'days' means business days. Import deadlines.ics and check one
event."
