---
name: log-touch
description: Use when the user pastes or attaches call notes, meeting notes, a voice-memo transcript or an email thread and wants it recorded against a deal, or says "log this call", "add this to Pipedrive", "update the deal from these notes", "record this meeting", "note this on the Acme deal", or "what should I update after this call". Finds the right person and deal, then proposes a note, a next activity and any stage, value or close-date changes for approval. Never creates deals.
---

# Log a touch (call, meeting or email) to the right deal

`<plugin>` is two directories up from this skill's directory. Data source as
in `<plugin>/reference/data-sources.md`.

## 1. Extract from the notes

If the user asks for the sample call or email, read it from
`<plugin>/samples/calls/` or `<plugin>/samples/emails/` and use `sample` as
the deals source.

List, quoting the notes: who (names, emails, company), when, what was
agreed, next step and its timing, and any explicit stage, value or date
signal ("budget closer to 40k", "sign by end of October"). Do not infer a
value or date that is not said.

## 2. Resolve person and deal

```
python3 <plugin>/scripts/dealtender.py match <deals|sample> --person "<name>" --org "<company>" [--email <addr>] --keywords "<3-6 topic words from the notes>"
```

Live mode: `searchPersons` / `getPersons`, then that person's or org's open
deals with `getDeals`; still run `match` on `deals_live.csv` if you built it.

- One open deal: use it.
- AMBIGUOUS (several open deals): pick one only if exactly one title matches
  the topic of the notes, and say why in one line ("the notes discuss the
  pilot; deal 101 is the pilot, 112 is the support renewal"). If the notes
  touch both, split the note per deal or ask. Otherwise ask.
- No person or no open deal: say so. Never create a deal, person or org as a
  side effect. Offer: the user adds them in Pipedrive, or you draft the
  details for them to add.

## 3. Propose the update

Dates: run `dealtender.py date --today <as-of or today> --weekday friday`
(or `--add-days N`, `--add-business-days N`) for "by Friday", "next week",
"in 3 days". Write the result as YYYY-MM-DD.

Per deal, propose only what the notes support:
- Note: 3-6 bullet summary, dated, factual, no adjectives about the person.
  Leave out phone numbers, personal details and anything sensitive that is
  not needed for the deal.
- Next activity: type, subject, due date for the stated next step.
- Stage / value / expected close date: only if the notes state it. If the
  notes give a range or a hint ("closer to 40k"), propose it as optional and
  say it is the customer's words, not a commitment.

Build `changes.json` and run `diff` exactly as in
`<plugin>/reference/approval.md`.

## 4. Output

```
Logging to: deal <id> <title> (<contact>)  - why: <one line>

<diff output>

Apply these changes? (yes / yes to 1,3 / edit)
```

Stop and wait. On an explicit yes, apply per `approval.md` step 4 or 5 and
report what Pipedrive now shows.
