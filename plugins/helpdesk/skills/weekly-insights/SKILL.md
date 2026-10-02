---
name: weekly-insights
description: Use when a support lead wants a weekly or periodic report, or says "weekly support report", "what drove tickets this week", "top contact reasons", "SLA misses this week", "CSAT detractors", "which macros should we write", or "where are our KB gaps". Computes volume delta, top drivers, SLA misses, CSAT and macro/KB-gap candidates from a Zendesk or Freshdesk export with a bundled script, then writes a short lead-ready report.
---

# Weekly insights

Script: `../ticket-schema/scripts/helpdesk.py` (SCRIPT). Every number in
the report comes from the script output. Do not compute or round anything
yourself.

## Procedure

1. Input and KB folder as in the queue-triage skill (`sample` or
   `sample-freshdesk` for the bundled data; KB is needed for macro/KB-gap
   candidates). Run:
   ```
   python3 SCRIPT weekly <input> [--kb <dir>] [--days 7] [--min 3] [--tz +HH:MM]
   ```
   Use `--days 30` for a monthly view. `--min` is the ticket count that
   makes a category a macro or KB-gap candidate.
2. Write the report in this shape (markdown; if the user is in Cowork or
   claude.ai and wants something to share, render the same content as an
   artifact or document):

   ```
   # Support week <start> to <end>
   **Headline:** <one sentence: the biggest change, using script numbers>

   | Metric | This window | Prior window |
   |---|---|---|
   | Tickets created | <n> | <n> |
   | SLA misses | <n> (<ids>) | <n> |
   | CSAT good share | <x%> (<good>/<rated>) | - |

   ## Top 3 drivers
   1. <category> - <n> tickets (prior <n>): <one line on what customers ask, from subjects>
   ...

   ## Detractors
   - <id> (<category>): "<comment>" -> <suggested follow-up>

   ## Macros to write
   - <category> (<n> tickets: <ids>): <proposed macro title + 2-line outline grounded in existing KB if any>

   ## KB articles to write
   - <category> (<n> tickets): <proposed article title + 3 bullet outline>

   ## Watch next week
   - <1-3 bullets: open escalations, known issues, repeat contacts>
   ```
3. For macro and KB outlines, read the tickets in that category (subjects
   and first messages from `python3 SCRIPT ticket <input> <id>`) so the
   outline answers what customers actually asked. Mark any product fact you
   could not find in the KB as [ASSUMED - check with product].
4. State the as-of time and data source from the script header. If the
   export is a CSV without comments, note that CSAT comments may be missing.
5. Do not name individual agents in a negative light; report by category
   and ticket, not by person.
