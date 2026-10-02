# Launch plan: Helpdesk Triage

## Positioning (one line)

Queue triage and on-brand reply drafts for Zendesk and Freshdesk. No per-seat
copilot fee; works from an export file in 5 minutes.

Lead with the two groups the vendors leave out: Freshdesk Growth (Freddy
Copilot is not sold on Growth) and Zendesk Team/Growth (Copilot is $50 per
agent per month on top of the Suite plan). Secondary hook for Zendesk: API tokens
retire on 2027-04-30, and this plugin works from an export with no token at all.

Never say "copilot" or "Freddy" as our name; use Zendesk/Freshdesk only as
"works with".

## Audience and where they are

| Channel | Who | Self-promo norms (check the sidebar/rules again on the day) |
|---|---|---|
| r/Zendesk | admins and agents | Small sub; disclose you made it, post as a question/discussion, answer every comment |
| r/freshdesk | admins on Growth/Pro | Same; lead with the Growth no-copilot pain |
| r/CustomerSuccess, r/CustomerService | team leads | Stricter about promotion; only post a "how I triage my morning queue" write-up with the link at the end, if allowed |
| Support Driven Slack (~10k+ [UNVERIFIED]) | support leads | Promotion only in the designated tools/promo channel; disclose |
| CX Accelerator Slack | CX ops | Tools channel only |
| Zendesk Community, API-token retirement threads | admins hit by token removal | Answer the question asked; mention the export-file route only where relevant |
| Freshworks Community ideas board ("Official MCP server when?") | Freshdesk admins | Reply in thread with the read-only allowlist tip; link last |
| LinkedIn support-ops creators | leads | Personal post with a 30-second screen capture of the triage table |
| Claude plugin directory, awesome-claude-plugins lists | Claude users | Listing text below |

## Post drafts

### 1. r/freshdesk

Title: Freshdesk Growth has no AI copilot, so I built a free Claude plugin that triages the queue from a CSV export

> Disclosure: I made this. It is free and MIT licensed, and there is nothing to buy.
>
> We're on Freshdesk Growth, and Freddy Copilot isn't available on our plan.
> So I built a Claude plugin that works from the normal ticket CSV export:
>
> - It ranks the open queue by SLA time left, priority and risk flags (legal,
>   security, VIP, churn, repeat contact). It also clusters duplicates
>   against your known issues.
> - It drafts replies from your own KB articles, canned responses and a
>   `voice.md` file that the lead edits. Every claim is marked [KB] or
>   [ASSUMED]. It never promises refunds or dates.
> - It writes a weekly report covering top drivers, SLA misses and CSAT
>   detractors, plus which canned responses and articles you're missing.
>
> It maps Freshdesk status codes 2-7 and priority codes 1-4, and it redacts
> card numbers that customers paste. It is read-only. Its only possible
> write is a private note, and that happens only after you confirm.
>
> You can try it on bundled fake data with `/helpdesk:triage sample-freshdesk`.
> Repo: https://github.com/brianshepardpss/helpdesk
>
> I'd love to hear what your morning triage actually looks like, and what
> you would want it to flag.

### 2. Zendesk Community, in an API-token retirement thread (reply, not a new post)

> For anyone whose triage scripts depend on an API token: tokens stop working
> on 2027-04-30, and you can't create new ones after 2026-10-27. The
> long-term fix is an OAuth client, which your admin creates in Admin Center
> > APIs > OAuth Clients with read scopes only.
>
> If you only need queue triage and reply drafting in the meantime, an
> export file works with no token at all. I maintain a free, open-source
> Claude plugin that does this from a Zendesk JSON or CSV export (disclosure:
> I wrote it): https://github.com/brianshepardpss/helpdesk. The setup guide
> includes the OAuth checklist above in more detail.

### 3. Support Driven Slack, tools/promo channel

> Hi all. I built a free Claude plugin for support leads (disclosure: mine,
> MIT licensed, no paid tier). You attach a Zendesk or Freshdesk export and
> get three things:
> 1. The open queue ranked by SLA time left, with legal, VIP and churn
>    flags and duplicate clusters
> 2. Drafts for the top 3 tickets in your brand voice, grounded in your
>    macros and KB
> 3. A weekly drivers, SLA and CSAT report that also lists missing macros
>    and articles
>
> It's read-only and redacts card numbers. You can try it on fake data in 5
> minutes: https://github.com/brianshepardpss/helpdesk
> Looking for 10 teams to run it on a real queue and tell me where it's wrong.

### 4. LinkedIn

> Every support lead I know starts the day the same way. You open the queue,
> sort by "oldest", and hope nothing is about to breach.
>
> I built a free Claude plugin that does that first pass from a Zendesk or
> Freshdesk export:
>
> - What breaches SLA in the next 4 hours
> - Who mentioned a lawyer, a cancellation, or that it's the third time
>   they've asked
> - Which tickets are the same outage
> - Draft replies in your team's voice, citing your own help articles
>
> There's no per-seat fee, and nothing is sent without you.
> Repo + 5-minute demo on fake data: https://github.com/brianshepardpss/helpdesk
> #customersupport #cx #zendesk #freshdesk

## Directory listing text

**Helpdesk Triage**: Queue triage and on-brand reply drafts for Zendesk and
Freshdesk teams. Rank the open queue by SLA risk. Flag legal, VIP and churn
tickets. Cluster duplicates against known issues. Draft replies from your KB,
macros and editable voice.md. Summarize long threads and produce a weekly
report of drivers, SLA misses, CSAT, and missing macros and KB articles.

It works from an export file with no account or key, and live connectors are
optional. It is read-only by design and redacts card numbers. Not affiliated
with Zendesk or Freshworks.

Keywords: helpdesk, support, zendesk, freshdesk, triage, sla, macros,
knowledge base.

## Day-30 signal and thresholds (set before launch; never lowered)

- **Primary:** 15 or more distinct teams report running `/helpdesk:triage`
  or `/helpdesk:draft` on real queues. Count them from /request issues,
  GitHub issues/discussions and forum replies.
- **Secondary:**
  - 100 or more GitHub stars.
  - 3 or more inbound requests for another helpdesk (HelpScout, Gorgias,
    Intercom).
  - At least 1 lead publicly sharing a voice.md or weekly report.
- **Kill or rethink:** fewer than 5 real-queue users by day 30, or most of
  the feedback is "can't connect". In that case, invest in a hosted OAuth
  connector.
