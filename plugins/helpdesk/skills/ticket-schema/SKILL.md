---
name: ticket-schema
description: Use when reading a Zendesk or Freshdesk ticket export (CSV, JSON or NDJSON) or connector payload, or when the user says "load my ticket export", "what does Freshdesk status 4 mean", "my CSV columns don't match", "convert this export", or "which fields do you need". Normalizes both helpdesks into one ticket schema and owns the bundled helpdesk.py script the other Helpdesk Triage skills call.
---

# Ticket schema: one shape for Zendesk and Freshdesk

All Helpdesk Triage skills work on one normalized ticket. This skill loads
exports into it and explains the mapping. The script is
`scripts/helpdesk.py` in this skill's directory (standard library only).
Other skills call it as `<this skill dir>/scripts/helpdesk.py`.

## Procedure

1. Find the input, in this order:
   - a file the user attached or named (Zendesk JSON/NDJSON/CSV, Freshdesk CSV or API JSON);
   - tickets fetched through a connected helpdesk connector (see step 3);
   - the bundled samples: the word `sample` (Zendesk JSON, 40 tickets) or
     `sample-freshdesk` (same tickets as a Freshdesk CSV). Say clearly that
     you are using fake sample data.
2. Normalize and check it:
   ```
   python3 <this skill dir>/scripts/helpdesk.py normalize <file|sample|sample-freshdesk|-> [--tz +HH:MM]
   ```
   Report: source detected, ticket count, blank rows skipped. If the script
   says no ticket id column was found, read `schema.md` (header aliases)
   and tell the user which column to rename. Freshdesk CSV timestamps are in
   the account's time zone with no offset; ask for it once and pass `--tz`.
3. Connector mode (only if a helpdesk connector is connected and the user
   wants live data): fetch tickets with the connector's READ tools only
   (search/list tickets, get ticket, get comments/conversations). Assemble
   them as Zendesk-shaped (`{"tickets": [...], "users": [...]}`) or
   Freshdesk-shaped JSON and pipe them on stdin with `-` as the export, so
   ticket content is never written to disk. Batch reads (100 per page) and
   stop on a 429; both vendors count failed calls against rate limits.
4. Never print raw ticket content you did not pass through the script. All
   script output is already redacted (card numbers, SSNs, CVV, expiry).
   Show requester first names and org names only; do not repeat emails,
   phone numbers, addresses or health details unless the user asks for that
   one ticket.

## The schema (summary; full mapping in `schema.md`)

`id, source, subject, status (new|open|pending|hold|solved|closed),
priority (low|normal|high|urgent), requester{name,email}, org, org_tags,
tags, created_at, updated_at, solved_at, sla_due, sla_paused, assignee,
group, csat{score good|neutral|bad, comment}, messages[{author, role
customer|agent, public, created_at, body}]`

Freshdesk codes: status 2 open, 3 pending, 4 solved (Resolved), 5 closed,
6 pending (Waiting on Customer), 7 hold (Waiting on Third Party); priority 1
low, 2 normal (Medium), 3 high, 4 urgent.

## Limits to state when relevant

- Freshdesk CSV exports contain the first message (Description) only, no
  replies. For thread summaries, use Zendesk JSON, a Freshdesk API export
  (`include=conversations`) or the connector.
- "As of" defaults to the export's `exported_at`, a fixed 2026-10-02 09:00
  UTC for the bundled samples, else the current clock. Pass `--now <ISO>`
  for the export time, or `--now latest` for the latest timestamp in the file.
- Slash dates (03/04/2026) are ambiguous; the script ignores them with a
  warning until you pass `--datefmt '%m/%d/%Y %H:%M'` (or `%d/%m/...`).
- `--tz` takes an IANA zone (America/Chicago), which handles daylight saving.
- Custom statuses (e.g. "In Progress") are treated as open and listed in a
  warning; rows without a ticket id are skipped and counted.
