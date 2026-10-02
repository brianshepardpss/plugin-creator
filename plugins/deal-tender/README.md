# DealTender

A sales ops routine for Pipedrive users, inside Claude: triage stale deals,
log calls to the right deal, write the Monday forecast, and prep for
meetings. Every CRM change is shown as a diff and waits for your yes.

For SMB founders and small sales teams (1-10 reps) who sell through a
Pipedrive deal pipeline and would rather not do data entry.

Works in: Claude Cowork, claude.ai and Claude Code.

## Install (60 seconds)

```
/plugin marketplace add brianshepardpss/plugin-creator
/plugin install deal-tender@plugin-creator
```

In Cowork or claude.ai, add the plugin from the same marketplace in
Settings > Plugins.

## Try it in 60 seconds, no account

```
/deal-tender:triage sample
```

You get a ranked list of the 11 deals that need attention in a fictional
40-deal pipeline (8 stale, 3 past their close date), each with the reason,
a follow-up email draft for the top five, and a proposed change list
(next activities, close dates) that is not applied until you say so.

Then try:
- "Give me my forecast for this quarter, and what moved since last week" (sample)
- "Log the sample Acme call" (DealTender reads its bundled call notes)
- "Prep me for my 2pm with Northwind" (sample)

## Use it on your pipeline

Two ways, same results:

1. **CSV export (no login).** In Pipedrive, open the Deals list view,
   choose ... > Export filter results > CSV, then "here's my Pipedrive
   export, triage it". Run `/deal-tender:setup` once to record stage
   probabilities, your stale threshold, currencies and tone.
2. **Live, through Pipedrive's official connector.** DealTender reuses
   Pipedrive's own remote MCP server (`https://mcp.pipedrive.ai/mcp`, OAuth,
   currently BETA). In Claude Code the plugin declares it: run `/mcp` and
   sign in. In Cowork and claude.ai, add the Pipedrive connector under
   Settings > Connectors. You never paste an API key.

## What it does

| Skill / command | What you say | What you get |
|---|---|---|
| `/deal-tender:triage` (pipeline-triage) | "which deals are going stale?" | ranked at-risk deals with reasons, follow-up drafts, proposed updates |
| log-touch | "log this call" + notes or an email | the right person and deal, a note, a next activity, stage/value/date changes for approval; never auto-creates deals |
| forecast-brief | "forecast for this quarter" | weighted, best case and commit per currency, slipped deals, what moved, a paste-ready brief |
| meeting-prep | "prep me for my call with Acme" | one-page brief from deal, contacts and last 5 activities, with questions to ask |
| csv-mode | "here's my Pipedrive export" | header mapping, custom-field check, duplicates and missing close dates |
| `/deal-tender:setup` | | connector check, stage probabilities, thresholds, fx rates you choose, tone |
| request | "I wish this could..." | a feature request draft you can file yourself |

All numbers (days idle, scores, weighted totals, dates) come from a bundled
standard-library Python script, `scripts/dealtender.py`, whose docstring
states every formula. Expected outputs for the sample are in
`samples/expected/`.

## Guardrails

- Read-only by default. Writes happen only after you approve the exact
  change list, one `updateDeal` per deal, then a read-back of the result.
- Never deletes or merges deals and never creates one as a side effect of
  logging; it creates a deal only if you ask, as its own change with its own
  yes. Never marks deals won/lost on its own, never sends email (drafts
  only).
- Drafts and briefs cite only what is in your CRM data; gaps are marked
  `[confirm]` or "not in CRM".
- Stops on Pipedrive rate-limit errors (429) instead of retrying, and
  explains the daily API budget.

## Privacy

DealTender has no server and no telemetry. Your CSV stays in your working
folder. In live mode, data flows only between Pipedrive's connector and your
Claude conversation, under the permissions of your own Pipedrive user. The
feedback skill only drafts text for you to file.

## Feedback

Say "I wish this could..." and the request skill drafts an issue for you to
file. Nothing is sent automatically.

Not affiliated with or endorsed by Pipedrive. Pipedrive is a trademark of
Pipedrive OU. All sample companies and people are fictional.
