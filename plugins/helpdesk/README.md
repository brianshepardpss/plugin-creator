# Helpdesk Triage

Queue triage and on-brand reply drafts for support teams on Zendesk or
Freshdesk. Rank the open queue by SLA risk, spot escalations and duplicates,
draft replies from your own KB, macros and brand voice, summarize long
threads, and get a weekly report. No per-seat copilot fee. It works from an
export file in 5 minutes, and a live connector is optional.

**Who it's for:** frontline agents and team leads on teams of 2-50 seats,
especially on Freshdesk Growth (no copilot available) or Zendesk Suite
Team/Growth (Copilot costs extra per seat).

Works in Claude Cowork, claude.ai and Claude Code. It uses skills, an agent
and one standard-library Python script. Nothing needs installing besides
the plugin.

## Install (60 seconds)

In Claude Code:

```
/plugin marketplace add brianshepardpss/plugin-creator
/plugin install helpdesk@plugin-creator
```

In Cowork or claude.ai, add the marketplace `brianshepardpss/plugin-creator`
under Plugins, then install **Helpdesk Triage**.

## Try it on the sample queue

```
/helpdesk:triage sample
```

This uses 40 fake tickets for Quillfern, a fictional booking-software
company. You get a ranked table showing SLA time left, flags, the suggested
owner and duplicate clusters, followed by drafts for the top 3 tickets. On
the sample queue:

- 3 tickets are about to breach SLA (1004, 1009, 1012).
- A legal threat (1021) is flagged.
- Two SMS-outage tickets (1036, 1038) are clustered under a known issue.
- A VIP's pasted card number (1026) is redacted.

Then try:

- `/helpdesk:draft 1017 sample`: a refund request outside the 14-day window.
  The draft cites the refund article and promises nothing.
- `/helpdesk:summarize 1030 sample`: a 25-message thread condensed into a
  handoff note of 150 words or fewer.
- `/helpdesk:weekly sample-freshdesk`: the same tickets as a Freshdesk CSV,
  showing drivers, SLA misses, CSAT, and macro and KB-gap candidates.
- "Anything I should escalate?": runs the `escalation-scout` agent.

## Use it on your queue

1. Export your open tickets.
   - **Zendesk:** a JSON export, or a view exported as CSV.
   - **Freshdesk:** Tickets > Export > CSV, with "Show multiline text
     fields" ticked.
2. Attach the file and say "triage this", or run `/helpdesk:triage <file>`.
3. Optional: run `/helpdesk:setup` to write your own files.
   - `voice.md` is built from 5 of your best replies.
   - `kb/` holds your help articles, `macros.json` and `known-issues.md`.
   - `vip-accounts.txt` lists your VIP accounts.

   The lead can edit any of these files at any time.
4. Optional: connect a helpdesk connector for live data. See
   `skills/helpdesk-setup/connectors.md` for the options:
   - Zendesk's OAuth endpoint
   - the community Zendesk and Freshdesk servers
   - a read-only tool allowlist
   - an admin OAuth checklist, covering Zendesk API tokens, which are
     retired on 2027-04-30

## What it does

| Piece | Job |
|---|---|
| `/helpdesk:triage` (queue-triage) | Ranked open queue: SLA time left, priority, category, legal/security/VIP/churn/anger/repeat flags, suggested owner, duplicate clusters, known-issue matches, plus drafts for the top 3 |
| `/helpdesk:draft` (reply-draft) | Reply in your voice, grounded in KB and macros. Each claim is marked [KB] or [ASSUMED]. It never promises refunds or dates |
| `/helpdesk:summarize` (thread-summary) | Handoff note of 150 words or fewer: current ask, steps tried, sentiment, open commitments with dates, next step |
| `/helpdesk:weekly` (weekly-insights) | Volume delta, top drivers, SLA misses, CSAT detractors, and macro and KB-gap candidates |
| `/helpdesk:setup` (helpdesk-setup) | Export or connector choice, writing voice.md, KB layout, VIP list, Zendesk admin OAuth checklist |
| ticket-schema | One schema for both helpdesks. It maps Freshdesk status codes 2-7 and priority codes 1-4, and owns `helpdesk.py` |
| escalation-scout (agent) | Builds an escalation pack for the lead: legal, security, VIP, churn and repeat contacts |
| request | Drafts a feature request for you to file yourself |

All the numbers come from `skills/ticket-schema/scripts/helpdesk.py`: SLA
time left, scores, counts, deltas, CSAT share and day counts. The formulas
are in its docstring.

## What it will not do

- It never sends a public reply, and never closes, merges, deletes or
  reassigns a ticket.
- The only write is an internal (private) note through your connector,
  after you see the exact text and say yes.
- It never promises refunds, credits or fix dates unless your KB says so.

## Privacy

- **Card numbers and SSNs:** Luhn-checked card numbers, SSNs, CVVs and
  expiry dates are redacted in every output.
- **Contact and health details:** requester emails, phone numbers and health details are not repeated
  in summaries.
- **Files:** nothing is written to disk except the files you ask setup to
  create. In connector mode, tickets are piped to the script in memory.
- **What leaves your machine:** nothing beyond your Claude conversation and
  any connector you set up yourself. Ticket content is handled under your
  own Claude plan. Use a Team or Enterprise plan, with your company's
  approval, for customer data.
- **No telemetry:** the plugin collects none.

## Feedback

Say "I wish this could..." and the request skill drafts an issue for you to
file. Nothing is sent automatically.

Not affiliated with or endorsed by Zendesk.
Not affiliated with or endorsed by Freshworks (Freshdesk).
Zendesk and Freshdesk are trademarks of their respective owners and are
named only to describe compatibility.
