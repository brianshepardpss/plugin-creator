---
name: pipeline-summary
description: Use when the user wants the status of an open role or a weekly hiring update, or says "where are we on the backend req", "pipeline update", "who is stuck", "weekly status for the hiring manager", "which scorecards are overdue", "how many candidates are in each stage". Works from a pipeline CSV export, the bundled sample, or a connected Greenhouse/Ashby MCP. Produces stage counts, days in stage, stuck candidates, overdue scorecards and a hiring-manager update email draft.
---

# Pipeline summary

## 0. Guardrails

Read `../fairness-lint/guardrails.md`. This is an operations view: counts,
dates and next actions. It never scores, ranks or compares candidates, and
the hiring-manager email uses aggregates plus named next actions only.

## 1. Get the data (one req at a time)

- **Sample** ("try it", no data): `../../samples/fernhill-robotics/pipeline.csv`
  with `--scorecards ../../samples/fernhill-robotics/scorecards.json --as-of 2026-10-01`.
- **CSV export** from any ATS: needs candidate, current stage and the date
  the candidate entered that stage. If headers differ, read `fields.md`.
- **Greenhouse or Ashby MCP**: read-only tools for ONE job: the job's
  pipeline / applications with current stage and stage-entry date, and the
  scheduled interviews with scorecard status. (Ashby: `get_job_pipeline`,
  `get_pending_tasks`.) Write them to a temp CSV in the shape of the sample,
  and a temp scorecards JSON if you have interview data. Do not fetch
  resumes, contact details or other reqs.

## 2. Compute

From this skill's directory:

`python3 pipeline.py <pipeline.csv> [--scorecards <scorecards.json>] [--as-of YYYY-MM-DD] [--stuck-days 14]`

All numbers you show come from this output. Do not count or subtract dates
yourself. If this session cannot run Python, say so, compute by hand with
the formulas in the script's docstring, show the working for each number,
and label the result "computed by hand -- check against pipeline.py".

## 3. Present (literal template)

```
## <Role> pipeline -- as of <date>
<script output>

### Next actions
- <stuck candidate>: <the concrete unblocking step, e.g. schedule the technical screen>
- <overdue scorecard>: nudge <interviewer> (draft below)
- Data cleanup: <duplicates / unparsed dates the script reported>

### Draft: update to the hiring manager (not sent)
Subject: <Role> -- pipeline update <date>
Hi <name>,
- <active> active candidates: <n> in <stage>, ... (from the script)
- Stuck: <n> (<name, stage, days>) -- next step: ...
- Waiting on feedback: <interviewer> for <session> (<days> days)
- Upcoming this week: <only if the user gave it>
Asks for you: <decisions the HM owns, e.g. approve the onsite slots>
```

Rules for the email: no ratings, no opinions about candidates, no ordering
by strength; names appear only next to an action. Offer to save it as a Gmail
draft if Gmail is connected (create a draft only; never send).

Close with: "AI-drafted, human decision required."
