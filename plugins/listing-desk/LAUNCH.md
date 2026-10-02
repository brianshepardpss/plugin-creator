# Launch plan: Listing Desk

Nothing here is posted without explicit owner approval, each time.

## Positioning

One line: Your listing appointment prep and listing launch in five minutes,
from the MLS export you already have -- with a Fair Housing check on every
word. No new subscription.

Lead with compliance + CMA math, not "AI writes descriptions" (commodity).
Never use REALTOR(R), NAR, Zillow, Realtor.com or an MLS brand in the name,
headline or hashtags. Every post says it is free, open source (MIT) and
that nothing is sent anywhere.

## Audience and where they are

| Channel | Why | Self-promo norms (re-check the day you post) |
|---|---|---|
| r/realtors | Working agents; frequent "AI for listings" and "is this Fair Housing OK" threads | Self-promotion is restricted; post as a value/discussion post with full disclosure, no affiliate links, answer questions in comments. Read the sidebar rules first. [rules UNVERIFIED -- check before posting] |
| Facebook: Lab Coat Agents (and local association/MLS member groups) | Large practitioner group; tools threads | Most groups ban promo outside designated threads; use the group's promo day/thread or ask an admin. [group size and rules UNVERIFIED] |
| Brokerage trainers and team leads (email/LinkedIn) | One trainer reaches 20-200 agents; compliance angle matters to brokers | Direct, personal, one email; no list blasts. |
| YouTube "AI for agents" creators | They demo tools weekly | One personal pitch with a 2-minute screen recording; no ask for paid placement. |
| r/RealEstate | Mostly consumers | Do not post the tool. Only answer Fair Housing wording questions where relevant, without links unless asked. |

## Post drafts

### r/realtors (value post, disclosed)

Title: I built a free Fair Housing checker + CMA-from-your-MLS-export for Claude. Roast it.

Body:

> Disclosure: I made this. It's free and open source (MIT), no account, no
> API keys, nothing leaves your Claude chat.
>
> Two things kept coming up with AI listing copy: it writes "great for
> families" and "safe neighborhood" by default, and it "can't do comps"
> because it has no data. So:
>
> - You export closed/active/pending from your MLS as CSV (any system --
>   it maps the headers). It picks 4-6 closed comps, shows an adjustment
>   table with every dollar (your rates, editable), and gives a 3-tier
>   range. Labelled "CMA -- not an appraisal."
> - It writes remarks under your character cap, 3 social posts and a
>   just-listed email, then runs a Fair Housing phrase check on all of it
>   (familial status, religion, steering words like "safe area" and "top
>   schools", source of income, buyer-agent comp in remarks) and rewrites
>   anything flagged.
> - Also: contract deadlines with business-day/holiday rollover shown and an
>   .ics file (always "verify against the contract"), and open-house
>   follow-up drafts that respect text consent.
>
> What I want from you: run it on a real export and tell me which headers
> it didn't recognise (which MLS system?), and any Fair Housing false
> positives. Link in comments if mods allow.

### Facebook group (Lab Coat Agents or local association group, promo thread)

> Free tool for listing appointments (I built it, no cost, no signup):
> drop your MLS CSV export into Claude and get a CMA with a full adjustment
> table + 3 price tiers, MLS remarks under your character limit, social
> posts, and a Fair Housing check that runs on every word ("perfect for
> young families", "safe area", "near top-rated schools" all get flagged
> and rewritten). Also turns your purchase contract into a deadline
> calendar. Nothing is sent anywhere; your data stays in your chat.
> Looking for 10 agents on different MLS systems to try it on a real export
> and tell me what broke. Comment "export" and I'll send the link.

### Brokerage trainer / team lead email

Subject: Fair Housing check on every AI-written listing, free for your agents

> Hi <first name>,
>
> Your agents are already using AI for listing descriptions; most of it
> defaults to "great for families", "safe neighborhood" and "near great
> schools". I built a free, open-source Claude plugin that runs a Fair
> Housing phrase check (plus a context review) on every piece of copy it
> writes, keeps buyer-agent compensation out of MLS remarks, and labels
> every CMA "not an appraisal".
>
> It also builds the CMA from the agent's own MLS export with a visible
> adjustment table, and turns an executed contract into a deadline
> checklist + calendar file. No subscription, no data leaves the chat.
>
> Would a 15-minute walkthrough for your next training be useful? Happy to
> adapt the phrase list to your state's protected classes.
>
> <name>, Press Start Studios

### YouTube creator pitch

Subject: 2-minute demo: CMA + Fair Housing check from an MLS export in Claude

> Hi <name> -- I watched your <video> on AI for listings. I built a free,
> open-source Claude plugin that does the part generic chatbots can't:
> comps from the agent's own MLS CSV with a visible adjustment table, and a
> Fair Housing check that runs on every line of copy. 2-minute screen
> recording attached, fictional data. If it's useful for a future video,
> it's yours to show; no payment either way.

## Directory listing text

Listing Desk -- Listing appointment prep and launch for US residential real
estate agents. Builds a CMA (labelled "not an appraisal") from your own MLS
CSV export with a full adjustment table and 3-tier price range, writes MLS
remarks, social posts and a just-listed email, and runs a Fair Housing check
on every word. Also: contract deadline calendar (.ics), open-house
follow-up drafts and a 12-month sphere plan. Works in Cowork, claude.ai and
Claude Code. No API keys, no subscription; runs on bundled sample data in
under five minutes.

Category: productivity. Keywords: real estate, CMA, comps, Fair Housing,
listing description, MLS export, contract deadlines, open house.

## Day-30 signal and thresholds

Set before launch; never lowered afterwards.

| Signal | Healthy at day 30 |
|---|---|
| Installs | >= 150 |
| GitHub stars | >= 25 |
| Unsolicited reports of running it on a REAL export | >= 10, from >= 3 different MLS systems (header mapping working is the PMF proxy) |
| Rollout interest | >= 1 brokerage trainer or team lead asking to roll it out |

Kill or rethink if: installs but no real-export reports (the demo is a
toy), or Fair Housing false-positive complaints dominate feedback.

Before posting: gather 3-5 real r/realtors thread quotes about AI listing
copy and Fair Housing (the research brief could not collect them).
