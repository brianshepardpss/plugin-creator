---
name: meeting-prep
description: Use when the user has an upcoming call or meeting with a customer or prospect and says "prep me for my call with Northwind", "brief me on Acme before the meeting", "what do I need to know about Globex", "get me ready for my 2pm", or "what happened last time with Rosa". Builds a one-page brief from the Pipedrive deal, contacts, organization and recent activities and notes (connector, CSV export or sample), with open questions to ask.
---

# Meeting prep

Only facts in the data. If something is not there, write "not in CRM", never
a guess. `<plugin>` is two directories up from this skill's directory.

## 1. Find the account

```
python3 <plugin>/scripts/dealtender.py prep <deals|sample> "<company, person or deal id>"
```

Live mode: `searchOrganization` or `searchPersons`, then `getDeals` for that
org, `getActivities` and `getNotes` for its deals (last 5), `getPersons` for
the org; write them to files and run `prep` on `deals_live.csv` with
`--persons` and `--activities`. If several orgs match, ask which one.

If the user attached emails or notes for this account, read them too and
mark those facts "(from your email of <date>)".

## 2. Write the brief

```
# <Company> - <meeting, if known> - prep

Deal: <title> | <stage> | <value currency> | expected close <date> <(PASSED n days ago) if flagged>
Last touch: <date> (<n> days ago) - <subject>
Next scheduled: <activity or "nothing scheduled">

## Who
- <name>, <title> - <role in the deal from notes, or "role not in CRM">

## History (newest first)
- <date> <type>: <one-line note>   (up to 5)

## Where it stands
<2-3 sentences, facts only: what they want, what is blocking, what was promised>

## Ask in this meeting
1. <question that closes a gap in the data>
2. <question about timeline/decision process if close date passed or unknown>
3. <question about the blocker named in the latest note>

## Watch out
<risks visible in the data: past close date, overdue activity, budget note, open security/legal item>
```

Rules: dates, values and day counts copied from the script output; no
invented attendees, budgets, competitors or personal details; leave out
phone numbers unless the user asks. One page.

## 3. After the meeting

Offer: "Paste your notes after the call and I'll log them" (log-touch skill).
