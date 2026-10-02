# Structured Hiring Kit

Structured hiring inside Claude: interview kits, debrief packets from your
scorecards, pay-transparent job descriptions, pipeline updates and outreach
drafts. Works from a paste, a CSV export, or your Greenhouse or Ashby
account. **It never scores, ranks or recommends candidates.**

For founders and hiring managers at small companies without recruiting ops,
recruiters carrying 10-25 reqs, and RecOps/TA leads who own the process.

Works in: Claude Cowork, claude.ai and Claude Code.

## Install

Claude Code or Cowork:

```
/plugin marketplace add brianshepardpss/plugin-creator
/plugin install structured-hiring@plugin-creator
```

Cowork or claude.ai without the marketplace: install the `.plugin` file from
the GitHub releases page (https://github.com/brianshepardpss/structured-hiring/releases).

## Try it in 60 seconds

```
/debrief-prep --sample
```

It runs on bundled synthetic data (Fernhill Robotics, a fictional company)
and produces a one-page packet for candidate Priya N.: the competency x
interviewer evidence matrix with quotes, the 2 vs 2 split on System Design,
the missing Debugging & Operations scorecard, a "Strong Yes" backed by five
words, and the flagged "culture fit / young energy" remark. See
`samples/expected/debrief-priya.md` for the exact output.

## What it does

| Skill / command | You say | You get |
|---|---|---|
| `/debrief-prep` (debrief-prep) | "prep the debrief for Priya", or paste scorecards | Evidence packet, disagreements, gaps, missing scorecards, fairness flags, debrief questions, decision-memo template |
| interview-kit | "build an interview kit for a founding AE" | 4-6 competencies, behavioral + situational questions with probes, anchored 1-4 rubrics, panel split, ready to paste into Greenhouse or Ashby |
| job-description | "write a JD from these intake notes" | Must-haves vs nice-to-haves, pay-range check against posting laws (CO, CA, WA, NY, IL, MD, MN, NJ, MA, VA, CT and more), inclusive-language lint |
| pipeline-summary | "where are we on the backend req?" | Stage counts, days in stage, stuck candidates, overdue scorecards, a hiring-manager update draft |
| `/outreach` (outreach-drafts) | "write the rejection emails" | Sourcing, follow-up, scheduling, status and rejection drafts; never sent |
| ats-update | "move Alex to onsite" | A change plan and a separate yes before every ATS write |
| hiring-decision | "who should we hire? rank them" | A plain explanation of why it will not rank, plus an alphabetical, unrated evidence table and a debrief plan |
| fairness-lint | "is this interview question okay?" | Flags for age, family, origin, disability, religion, culture fit, salary history and more, with fixes |
| request | "I wish this could..." | A feature request draft and a prefilled GitHub issue link for you to open |

Every number (days in stage, overdue days, rating counts) comes from a
bundled standard-library Python script, not from the model.

## Connect your ATS (optional)

The plugin bundles the official remote MCP servers (OAuth, your own
permissions, no keys stored):

- Greenhouse: `https://mcp.us.greenhouse.io/mcp` (open beta; Core, Plus or Pro;
  a Site Admin enables MCP access; default scopes are read-only). In
  claude.ai add the connector `https://mcp.greenhouse.io/mcp`.
- Ashby: `https://mcp.ashbyhq.com/mcp/v1` (open beta, all plans; an org admin
  opts in).
- Lever: no official MCP server yet. Export feedback or the pipeline as CSV.

See `CONNECTORS.md`. Reads fetch one candidate or one req at a time.

## Guardrails (built into the skills, not just this page)

- No scores, averages, rankings, fit percentages or hire/no-hire
  recommendations, ever. Asked to rank, it explains why the call is yours
  (NYC Local Law 144, the EU AI Act's high-risk rules, state AI-in-hiring
  laws) and offers an alphabetical, unrated evidence table instead.
- No emotion, sentiment or personality inference about candidates.
- Non-job-related remarks in feedback ("culture fit", age, family, accent)
  are flagged and set aside, never silently rewritten.
- Contact details are stripped before synthesis; EEO/demographic data is
  ignored and never used.
- Every ATS write is shown first and needs its own yes. In Claude Code and
  Cowork a hook also asks before any non-read Greenhouse/Ashby/Lever tool
  call and logs it (tool, time, ids only). Email is drafts only, and the
  hook asks before any email send/reply/forward tool runs. Check the hook
  logic with `python3 hooks/ats_write_guard.py selftest`.
- Outputs end with "AI-drafted, human decision required."

This plugin does not give legal advice. The pay-transparency table was last
reviewed 2026-10-02; confirm with counsel before posting.

## Privacy

- Nothing is sent anywhere by this plugin. Your data goes only to your
  Claude conversation and to services you connect yourself (your ATS, Gmail).
- The plugin stores no candidate data. The only file it writes on its own is
  the ATS action log (`ats-actions.log` in the plugin's data folder), which
  holds tool names, timestamps and record ids, no names or notes.
- Sample data is synthetic: fictional companies, first-name-plus-initial
  people, example.com emails, 555-01xx phone numbers.
- No telemetry.

## Feedback

Say "I wish this could..." and the request skill drafts an issue for you to
file. Nothing is sent automatically.

## License

MIT. Copyright Press Start Studios.

Not affiliated with or endorsed by Greenhouse Software, Inc.
Not affiliated with or endorsed by Ashby, Inc.
Not affiliated with or endorsed by Lever (Employ Inc.).
Not affiliated with or endorsed by Anthropic beyond use of its plugin format.
