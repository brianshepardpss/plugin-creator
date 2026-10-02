# Launch plan: Structured Hiring Kit

## Positioning

"Structured hiring in Claude: interview kits and debrief packets from your
Greenhouse or Ashby, or a paste. It never scores candidates."

Proof point for every post: `/debrief-prep --sample` in under a minute, and
the sample output in `samples/expected/debrief-priya.md`.

Who: (a) founders and hiring managers at companies under 200 people with no
recruiting ops; (b) recruiters carrying 10-25 reqs; (c) RecOps/TA leads.

## Channels (in order) and their rules

| Channel | Audience | Self-promo rule we follow |
|---|---|---|
| r/recruiting | in-house and agency recruiters | Read the sidebar the day of posting. Lead with the practice (structured debriefs), disclose authorship, no link in the title, answer every comment; if the rules restrict tools, post only in the designated promo thread. |
| RecOps Collective Slack | RecOps and TA leads | Post only in the tools/show-and-tell channel, once, as a member asking for feedback. No DMs. |
| Recruiting Brainfood (Hung Lee) | TA leaders | Editorial pitch by email; no ask for a paid placement. |
| YC Bookface / founder communities | founders hiring first 20 | Only if posted by a YC founder member; otherwise use Show HN below. |
| Show HN | founders and engineers | "Show HN" format, the maker posts, plain description, stays to answer. |
| awesome-claude-plugins lists | Claude users | One PR per list following its CONTRIBUTING format. |
| Greenhouse Community, Ashby customer Slack | ATS admins | Only after 3 users confirm the MCP path works; frame as "how to run structured debriefs with the new MCP". |

## Post drafts

### r/recruiting

Title: How we stopped debriefs from turning into gut-feel contests (free Claude plugin, I made it)

Body:
Most debriefs I've sat in go like this: two scorecards are missing, one
"Strong Yes" says "solid, would be great", and someone mentions culture fit.
Then the loudest person wins.

I built a free, open-source plugin for Claude that preps the debrief from the
scorecards you already have (paste them, a CSV export, or Greenhouse/Ashby if
you've connected their official MCP). It gives you one page:
- a competency x interviewer evidence table with quotes
- where the panel actually disagrees, with each side's evidence
- missing scorecards and competencies nobody covered
- ratings with no evidence behind them
- flags for non-job-related remarks (culture fit, age, family, accent)

What it deliberately does not do: score, rank, or say hire/no-hire. That's
your call, and tools that make it fall under NYC's AEDT law and the EU AI Act.

There's a built-in fake candidate so you can try it without real data:
`/debrief-prep --sample`. Also does interview kits with anchored rubrics and
JDs with a pay-range check for CO/CA/NY/WA/IL and others.

Disclosure: I made it. MIT licensed, no telemetry. I'd love to hear what your
debrief process is missing. Link in the first comment.

### RecOps Collective Slack (tools channel)

Hi all, I'd like feedback from people who own the hiring process. I made a
free Claude plugin called Structured Hiring Kit for small teams that don't
have RecOps:
- `/debrief-prep` turns scorecards into an evidence packet (matrix,
  disagreements, gaps, overdue scorecards, fairness flags)
- interview kits with 1-4 anchored rubrics, laid out to paste into
  Greenhouse/Ashby scorecards
- JD pay-transparency check, pipeline summary, outreach drafts only
Guardrails: no scores, rankings or recommendations; no sentiment inference;
it confirms every ATS write separately. It reads Greenhouse and Ashby through
their official MCP servers (OAuth, your own permissions).
Question for this group: what would stop you from putting this in front of
your hiring managers? Repo: https://github.com/brianshepardpss/structured-hiring

### Recruiting Brainfood pitch (email to Hung Lee)

Subject: Free open-source "debrief prep" for Claude that refuses to score candidates

Hi Hung, a short one for the tools section if it fits. Structured Hiring Kit
is a free, MIT-licensed Claude plugin that builds a debrief packet from
interviewer scorecards: evidence by competency, disagreements, missing
scorecards, thin-evidence ratings, and flags for remarks like "culture fit"
or "young energy". It is built to stay out of AEDT territory: no scores,
rankings or hire/no-hire, and no emotion inference. It works from a paste or
CSV, or reads Greenhouse/Ashby via their official MCP servers. There's a
synthetic demo candidate so anyone can try it in a minute. Repo:
https://github.com/brianshepardpss/structured-hiring. Thanks for the newsletter.

### Show HN

Title: Show HN: Structured Hiring Kit - debrief packets from scorecards, no candidate scoring

Body: I built a Claude plugin for founders who hire without a recruiting team.
Paste your interviewers' scorecards (or connect Greenhouse/Ashby via their
official MCP servers) and `/debrief-prep` produces a one-page packet. It has
an evidence matrix, the disagreements, missing scorecards, ratings without
evidence, and fairness flags. The numbers come from small stdlib Python
scripts, not the model. It refuses on purpose to score, rank or recommend
(NYC LL144, EU AI Act), and every ATS write needs a separate confirmation via a
PreToolUse hook. It also does interview kits, JDs with a pay-transparency
check, and pipeline summaries. MIT, no telemetry. Try it with `/debrief-prep
--sample`. Feedback welcome, especially from people who run debriefs weekly.

## Directory listing text

Name: Structured Hiring Kit
Short: Interview kits, debrief packets and pay-transparent JDs from a paste or
your Greenhouse/Ashby. Never scores or ranks candidates.
Long: Structured Hiring Kit brings structured interviewing into Claude for
founders, hiring managers and recruiters. `/debrief-prep` turns interviewer
scorecards into an evidence packet that shows competency evidence, where the
panel disagrees, missing scorecards, ratings with no evidence, and flags for
non-job-related remarks. Other skills build interview kits with anchored
rubrics, write job descriptions with pay-transparency and inclusive-language
checks, summarize pipelines, and draft outreach (drafts only). It works with
sample data, a paste, a CSV export, or the official Greenhouse and Ashby MCP
servers. Built-in guardrails: no scoring, ranking or hire recommendations; no
emotion inference; contact details stripped; every ATS write confirmed.
Category: productivity / HR. Works in Cowork, claude.ai, Claude Code.

## Day-30 signal and thresholds

- Primary (continue): at least 150 installs (marketplace plus repo clones),
  AND at least 10 unsolicited reports of running `/debrief-prep` on a real req
  (GitHub issues, Reddit or Slack replies).
- Secondary: at least 3 users report a working Greenhouse or Ashby MCP
  connection; at least 1 RecOps lead asks for a team rollout or a
  Lever/Workable connector.
- Kill or pivot: under 30 installs at day 30, or feedback that is mostly
  "my ATS notetaker already does this". Pivot candidate: fairness-lint plus
  interview-kit as a standalone "structured interview starter" for founders.
- Measure from GitHub traffic (views, clones), stars, issues and the
  request-skill issues. No telemetry.
