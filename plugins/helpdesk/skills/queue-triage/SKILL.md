---
name: queue-triage
description: Use when a support lead or agent wants the open ticket queue sorted out, or says "triage my queue", "what should we work on first", "which tickets are about to breach SLA", "morning queue", "prioritize these tickets", "find duplicate tickets", or attaches a Zendesk or Freshdesk export and asks what matters. Produces a ranked queue table with priority, category, SLA time left, escalation flags, suggested owner and duplicate clusters, then ready-to-paste drafts for the top 3 tickets.
---

# Queue triage

Script: `../ticket-schema/scripts/helpdesk.py` (relative to this skill's
directory; call it SCRIPT below). Sample data: `../../samples/`.

## Procedure

1. Pick the input (see the ticket-schema skill for details):
   attached/named export file > connector read (pipe JSON on stdin, `-`) >
   `sample`. If the user said "sample", "demo" or "try it" or gave nothing
   and has no connector, use `sample` and say it is fake data.
2. Pick the team files. KB folder: one the user named, else `./kb` or
   `./helpdesk/kb` if it exists, else (sample input only) the bundled
   `../../samples/kb`. Voice: `./voice.md` or `./helpdesk/voice.md`, else
   `../../samples/voice.md` (say it is the sample voice; offer
   `/helpdesk:setup` to write theirs).
3. Run, and keep the output exactly as printed:
   ```
   python3 SCRIPT triage <input> [--kb <dir>] [--tz +HH:MM] [--now now]
   ```
   "As of" defaults to the export's `exported_at`, a fixed snapshot time for
   the bundled samples, and the current clock for everything else. If the
   user's export is from earlier (say, yesterday's file), pass
   `--now <time it was exported>`. Repeat any `Warning:` lines the script
   prints (skipped rows, custom statuses treated as open, ambiguous dates:
   ask the user for the date order and rerun with `--datefmt`). Never reorder
   rows, change SLA times or recompute scores yourself; the formula is in
   the script docstring if the user asks why.
4. Show the result in this shape:

   ```
   ## Queue as of <as-of from script> (<n> open)
   <one line: SLA breached / due within 4h / escalations / clusters, from the script>

   <the script's table, unchanged>

   ### Act now
   - <ticket>: <why, from flags and SLA, one line each, for every row with
     SLA due within 4h or a legal/security/vip flag>

   ### Duplicates and known issues
   - <cluster>: <ids> -> <known issue id or "no known issue">: suggest one
     parent ticket and one macro/answer for the rest (do not merge).

   ### Drafts for the top 3
   <for ranks 1-3, a draft following the reply-draft skill: get the thread
   with `python3 SCRIPT ticket <input> <id>`, ground it in KB + macros +
   voice, label it "Draft - internal note, not sent">
   ```
5. Escalations: for any legal, security or vip flag, add the line "Escalate
   to <owner from table> before replying". For more than 3 escalations, or
   if the user asks for an escalation pack, hand off to the
   `escalation-scout` agent, passing the absolute path of SCRIPT, the input
   and the KB folder in its prompt.
6. Non-English tickets (`lang:xx` flag): draft in the customer's language
   and note it.
7. Close with: "Nothing was sent or changed in your helpdesk." Offer
   `/helpdesk:draft <id>` for any other ticket and `/helpdesk:weekly`.

## Guardrails

- Read-only. Never set status, priority, assignee, tags, merge, close or
  reply in the helpdesk. Suggested owner is a suggestion.
- Script output is already redacted. If a ticket has the `pii-redacted`
  flag, never quote the original number; tell the lead to redact it in the
  helpdesk (Zendesk: redact comment; Freshdesk: edit/delete the
  conversation).
- Do not paste requester emails, phone numbers, addresses or health details
  into the summary. First name and org are enough.
- For a real (non-sample) export, say once: "Ticket content is processed
  under your Claude plan; use a Team or Enterprise plan with your company's
  approval for customer data."
- If the export has no SLA column (`SLA left` = none), say SLA risk could
  not be computed instead of guessing.
