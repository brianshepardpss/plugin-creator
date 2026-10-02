# Launch plan: DealTender

Nothing here is posted without explicit owner approval each time.

## Positioning

"The Pipedrive connector gives Claude access. DealTender gives it a sales
ops routine: triage, log, forecast, prep. Try it on a CSV in 2 minutes, no
login."

Audience: SMB founders and 1-10 rep teams on Pipedrive Lite/Growth
(agencies, B2B services, SaaS, trades) who hate CRM data entry.

## Channels (in order)

1. r/ClaudeAI - project showcase posts allowed with the right flair; lead
   with the demo, not the pitch.
2. Pipedrive Community (community.pipedrive.com), integrations/apps
   discussion - check current posting guidelines first; frame as a free,
   open-source workflow on top of Pipedrive's own MCP, answer questions in
   thread.
3. r/sales - no self-promotion outside allowed threads; post only as a
   how-to with the repo link at the end, or skip if the mods' rules forbid
   it that week.
4. r/smallbusiness - promotion only in the weekly promo thread.
5. LinkedIn - owner's own feed, tag nobody without permission.
6. Indie Hackers - build log.

## Post drafts

### r/ClaudeAI (flair: Built with Claude / Showcase)

Title: I built a free Claude plugin that triages a Pipedrive pipeline and drafts the follow-ups (works on a CSV, no login)

Pipedrive's official MCP connector lets Claude read and update your CRM,
but it is plumbing. I wanted the routine on top: every Monday, which deals
are rotting, what to send each one, and what to fix in the CRM.

DealTender does four things:
- triage: ranks stale and past-close deals with the reason, drafts a
  follow-up per deal, proposes CRM updates as a diff you approve
- log-touch: paste call notes or an email, it finds the right deal (asks if
  ambiguous), proposes note + next activity, never creates deals
- forecast-brief: weighted / best case / commit per currency, what moved
  this week, slipped deals
- meeting-prep: one-page brief from deal + contacts + last 5 activities

All math is a stdlib Python script, so the numbers are reproducible. Try it
with `/deal-tender:triage sample` on a fictional 40-deal pipeline.

MIT, no telemetry: <repo link>. Feedback very welcome, especially from live
Pipedrive accounts.

### Pipedrive Community

Title: Free open-source Claude workflow on top of Pipedrive's MCP: stale-deal triage, call logging, forecast brief

Hi all - if you connected the Pipedrive MCP to Claude and wondered "now
what?", I put together a free plugin that gives it a routine:

1. Which deals are going stale (uses your stages' rotting days), with a
   drafted follow-up for each.
2. Paste call notes or an email and it proposes the note, next activity and
   any stage/close-date change on the right deal. Nothing is written until
   you approve the list.
3. A Monday forecast brief per currency, including what moved since last
   week.
4. Meeting prep from the deal history.

It also works on a plain CSV export if you would rather not connect
anything. It is not affiliated with Pipedrive; it uses the official MCP
server and your own permissions. Repo and install: <repo link>. I'd love to
hear where it gets your pipeline wrong.

### r/sales (how-to framing; only if rules allow a link)

Title: The 15-minute Monday pipeline routine I automated (stale deals, follow-ups, forecast)

What I do every Monday, and what I now let Claude do from a CRM export:
1. Flag deals with no activity past the stage's rotting days and nothing
   scheduled. Those are the ones that die quietly.
2. Flag deals whose expected close date already passed; ask the customer for
   the new timeline instead of guessing one.
3. Weighted pipeline = value x stage probability; "commit" = deals at 80%+.
   Separate per currency. Note what moved since last week.
4. One short follow-up per stale deal with a single concrete ask.

If you are on Pipedrive and use Claude, I packaged this as a free plugin
(works on a CSV export, no login): <repo link>. Happy to share the scoring
rules if you want to do it by hand.

### LinkedIn

Most small sales teams don't need a better CRM. They need someone to tell
them on Monday which five deals are going cold and what to say to each.

I built DealTender, a free Claude plugin for Pipedrive users: stale-deal
triage with drafted follow-ups, call logging from notes, a per-currency
forecast brief and meeting prep. Every CRM change waits for your approval,
and the numbers come from a script you can audit. Try it on a sample
pipeline in two minutes: <repo link>

Not affiliated with Pipedrive.

## Directory listing text

DealTender - Pipeline triage, call logging, forecast briefs and meeting prep
for Pipedrive users. Ranks stale and past-close deals, drafts follow-ups,
and proposes CRM updates you approve before anything is written. Works live
through Pipedrive's official MCP connector or on a CSV export with no login;
includes a 40-deal fictional sample. All math by a bundled stdlib script.
Not affiliated with or endorsed by Pipedrive.

Listings: own marketplace (brianshepardpss/plugin-creator), Anthropic plugin
directory (claude-plugins-official submission), community plugin
directories.

## Day-30 signal (set before launch, never lowered)

- Go: >= 150 installs (marketplace + repo clones), >= 40 GitHub stars,
  >= 10 unsolicited reports or issues from real Pipedrive accounts, and
  >= 3 people asking for a second CRM or a scheduled mode.
- Kill or pivot: < 30 installs and no live-account usage reports.
- In between: keep, fix the top reported gap, re-post once in the best
  performing channel.
