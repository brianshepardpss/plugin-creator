---
name: daily-report
description: Use when the user wants today's daily report, daily log, superintendent's report or field report written up from voice memo transcripts, rough notes or jobsite photos, or says "write my daily", "turn this voice memo into a daily report", "daily log for today", "here are my notes from the site", or "log the manpower". Produces a structured daily report with computed manpower totals, a photo log and possible notice events flagged.
---

# Daily report from notes, voice memos and photos

`<skill dir>` below means this skill's base directory (shown when the skill
loads). Write output files to the user's working folder, not the skill dir.

A daily report can become evidence in a delay or payment dispute. Record
only what the notes say. Mark anything missing "not recorded". Never fill a
gap with a typical value.

Scripts live in `scripts/` beside this file. Sample input:
`<skill dir>/../../samples/notes/daily-voice-transcript.txt`.

## Steps

1. Read every input: transcript, typed notes, photos (describe only what is
   visible; do not guess locations unless the user said them). Note the
   source file name for the report footer.
2. Pull facts into the template fields. Times as stated ("about 10:15").
   Keep the super's numbers exactly. If the notes contradict themselves,
   keep both and add "[conflict in notes: ...]".
3. Manpower: list each company/trade with the headcount stated. Then run
   ```
   python3 <skill dir>/scripts/manpower.py "<Company (trade)>=<workers>[@<hours>]" ... \
     [--lost "<Company>=<workers>x<hours>"]
   ```
   Use `@hours` only where the notes state hours. Use `--lost` only for
   lost or impacted time the notes state. Paste the script's table; do not
   add totals yourself.
4. Notice screen: run `python3 <skill dir>/scripts/notice_flags.py <transcript or notes file>`
   (save pasted notes to a file first). For every hit that is real, add a
   row to "Possible notice / claim events" with time, what happened, who
   was told and how (call, email, voicemail), and what is still unknown.
5. Fill the template below. Weather: only what was observed or recorded; if
   the notes have no temperature, write "Temp: not recorded". Do not look
   up or estimate weather.
6. Show the report, then the follow-ups list.

## Template

```
DAILY REPORT - <Project>            Date: <Day, YYYY-MM-DD>   Report by: <name>
Weather: <conditions as recorded, with times>  Temp: <value or "not recorded">
Weather impact on work: <as stated, or "none recorded">

MANPOWER
<table from manpower.py>

WORK PERFORMED (by area / trade)
- <area or gridline>: <trade> - <work, quantities or % as stated>

DELIVERIES
- <time> <supplier> - <material>, <qty>   (or "none recorded")

INSPECTIONS / TESTS:  <type, inspector, result>  (or "none")
VISITORS:  <name/role, time, purpose>  (or "none recorded")
SAFETY:  <toolbox talk topic; observations; incidents or "no incidents reported">

DELAYS / IMPACTS / CONDITIONS
- <time> <event> - <effect on crews and work> - <who notified, how, when>

POSSIBLE NOTICE / CLAIM EVENTS
- <event> - Possible notice event: check the notice provisions in your
  contract today. Notified so far: <...>. Open questions: <...>.

PHOTO LOG
| # | Description | Location | Time |

EQUIPMENT ON SITE:  <as stated or "not recorded">
NOTES:  <anything else stated, e.g. sanitation service>
Source: <file names>. Prepared from the superintendent's notes; items marked
"not recorded" were not in the notes.
```

## Follow-ups (after the report)

List concrete next actions taken from the notes: RFIs to write (offer the
rfi skill), written notice to send for any possible notice event (offer the
delay-notice skill; never say how many days they have), photos to attach,
missing facts to fill in tomorrow (for example: temperature, crew hours).

## Guardrails

- Never invent weather, headcount, hours, quantities or names.
- Never state that an event entitles the contractor to time or money, or
  that notice is or is not required. Say "possible notice event - check
  your contract".
- Safety observations are recorded as stated; do not make OSHA compliance
  determinations. If the notes describe an injury or serious hazard, add
  "Follow your company's incident reporting procedure."
- No structural or engineering calls (for example "is it OK to chip out the
  footing?"): record the question and route it to the engineer of record
  through an RFI. Route safety hazards to the competent person on site.
