---
name: pipeline-triage
description: Use when the user wants to know which deals are going stale, rotting, stuck, slipping or overdue, or asks "which deals should I follow up on", "what am I neglecting", "triage my pipeline", "clean up my pipeline", "show me rotting deals", or "who haven't I talked to in a while". Works on the Pipedrive connector, a Pipedrive deals CSV export, or the bundled sample. Produces a ranked at-risk list with reasons, follow-up email drafts, and proposed CRM updates the user approves.
---

# Pipeline triage

Read-only until the user approves changes. All numbers come from the script.
`<plugin>` below is two directories up from this skill's directory.

## 1. Get the data

Follow `<plugin>/reference/data-sources.md`: the word `sample`, the user's
CSV, or the live connector written to `deals_live.csv`. If unsure which, ask
one question: "Use your Pipedrive connector, a CSV export, or the sample?"

## 2. Rank

```
python3 <plugin>/scripts/dealtender.py triage <deals|sample>
```

Use `--json` if you need fields for drafting. If the output starts with DATA
WARNINGS, tell the user before the table and suggest the csv-mode check. Copy ranks, days idle, dates,
values and scores exactly as printed. Do not add, drop or re-rank deals; if
you disagree with a flag, say so in a note under the table.

## 3. Draft follow-ups (top 5 by rank; offer the rest)

For each deal, one short email to the deal's contact person:
- 50-120 words, plain text, tone from settings (`tone`), signed with
  `sender_name` if set, else "[your name]".
- Reference only facts in the data: deal title, stage, last activity
  subject/note (run `dealtender.py prep <deals> <deal id>` for history if
  needed). Anything else goes in as `[confirm: ...]`.
- One clear ask with a concrete option (a call slot or a yes/no question).
- Never invent deadlines, discounts, pricing or "other customers" claims;
  never guilt-trip ("just bumping this").
- Past-close deals: ask about the new timeline, do not assume it.
- These are drafts. Never send email.

## 4. Propose CRM updates

For the top 10 flagged deals by rank (one approval covers at most 10 deals;
offer the rest as a second batch), at most one or two changes each:
- STALE with nothing scheduled or overdue: add a follow-up activity. Get the
  date with `dealtender.py date --today <as-of date> --add-business-days 2`.
- PAST CLOSE: propose updating the expected close date, but set it to
  `"[you choose]"` unless the data or user gives one; `diff` shows it as a
  QUESTION and it is applied only after the user supplies a date.
- Possible duplicates: flag for the user to merge in Pipedrive (DealTender
  never merges or deletes).

Build `changes.json` and run `diff` as in `<plugin>/reference/approval.md`.

## 5. Output

Write `pipeline-triage-<as-of date>.md` in the working folder and show the
same content in chat:

```
# Pipeline triage - <as of date>
<N> open deals, <X> need attention (stale <a>, past close <b>). Biggest at risk: <deal> (<value>).

## Needs attention
| # | Deal | Stage | Value | Days idle | Close | Why |
|---|------|-------|-------|-----------|-------|-----|
<one row per flagged deal, values from the script>

## Follow-up drafts
### <#>. <deal title> -> <contact>
Subject: <subject>
<body>

## Proposed updates (nothing applied yet)
<diff output>
Reply "apply all", "apply 1,3" or edit a line. Nothing changes in Pipedrive until you do.

## Watch list and hygiene
<watch list and possible duplicates from the script>
```

## 6. On approval

Follow `<plugin>/reference/approval.md` step 4 (live) or 5 (CSV). Never
apply anything the user did not explicitly approve.
