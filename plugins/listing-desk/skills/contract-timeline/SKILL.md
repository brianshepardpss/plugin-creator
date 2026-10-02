---
name: contract-timeline
description: Use when an agent has an executed purchase contract and needs the deadlines, or says "build my contract timeline", "when is the option period up", "inspection deadline", "what are the deadlines on this contract", "calendar the contract dates", "make an .ics", or uploads a purchase agreement PDF (typed or scanned). Extracts key terms, computes every deadline with business-day and weekend/federal-holiday rules shown, and writes a checklist plus an .ics calendar file. Every date is marked verify-against-the-contract.
---

# Contract to timeline

Dates come from `timeline.py` in this skill's directory, never from mental
math. This is a checklist for the agent, broker, TC or attorney to verify;
it is not legal advice and does not interpret the contract.

## 1. Read the contract

- Read the contract the user gives you, usually a PDF (sample: the text
  extract `../../samples/purchase_contract.txt`; the original PDF and a
  scanned variant are at https://github.com/brianshepardpss/plugin-creator/tree/main/lab/sample-pdfs). For a scan, read
  the page images carefully and mark any value you could not read clearly as
  `UNREADABLE` rather than guessing.
- Find: parties, property, sales price, financing, earnest money and option
  fee (amount, holder, due), the Effective Date (date of final acceptance),
  and every deadline: earnest money, inspection/option, seller disclosure,
  HOA documents, title commitment, title objections, survey, appraisal,
  financing, closing, final walk-through, possession.
- Find the contract's own rules: what "days" means (calendar vs business),
  whether the Effective Date is counted, the weekend/holiday rollover clause,
  and the deadline time of day.
- Quote the paragraph number for each item. If the contract leaves a blank
  unfilled, record it as a flag, not a date.

## 2. Write terms.json

Write `contract/terms.json` (schema and rules are in the docstring at the top
of `timeline.py`; read it if unsure):

```
{"property": "<address>", "effective_date": "YYYY-MM-DD", "rollover": true,
 "deadline_time": "5:00 p.m. local time",
 "terms": [["Sales price", "$...", "Para 3"], ...],
 "deadlines": [
  {"id": "effective_date", "name": "Effective Date", "date": "YYYY-MM-DD", "source": "Para 4"},
  {"id": "earnest", "name": "Earnest money delivered", "days": 3, "unit": "business",
   "from": "effective", "source": "Para 5", "owner": "Buyer"},
  {"id": "title_objection", "name": "Buyer title objections", "days": 5, "unit": "business",
   "from": "title", "source": "Para 9", "owner": "Buyer"},
  {"id": "closing", "name": "Closing", "date": "YYYY-MM-DD", "source": "Para 13"},
  {"id": "walkthrough", "name": "Final walk-through", "days": 1, "unit": "calendar",
   "before": "closing", "source": "Para 14", "owner": "Buyer"}]}
```

Set `rollover` from the contract's clause (false if there is none). If the
contract says the Effective Date counts as day 1, add `"count_base_day": true`
to those deadlines. Add state holidays the contract counts with
`"extra_holidays": ["YYYY-MM-DD"]`.

## 3. Run it

```
python3 <base>/timeline.py contract/terms.json --out contract/timeline.md \
  --ics contract/deadlines.ics
```

## 4. Reply

```
## Contract timeline: <address>
**VERIFY every date against the executed contract with your broker/TC/attorney.**

Key terms: <price, financing, earnest money + holder, option fee>
Effective Date: <day date>. Deadlines end <time>. Rollover clause: <yes/no>.

| Due | Deadline | Who | Rule and working |
<one row per deadline, copied from the script, including any rollover or
skipped-holiday note>

Holidays in this window: <from the script>
Flags: <unfilled blanks, unreadable values, VERIFY notes from the script>

Files: contract/timeline.md, contract/deadlines.ics (import into Google
Calendar / Outlook / Apple Calendar)
```

Explain any rollover in one sentence, e.g. "Title commitment: 15 days lands
on Sat 10/24, so the contract's rollover clause moves it to Mon 10/26."

## Guardrails

- Never state a deadline as fact; every date says VERIFY.
- Do not give legal advice, interpret contingency rights, or draft notices,
  amendments or disclosure forms. Refer those to the broker or an attorney.
- Do not fill or draft buyer-agent compensation terms.
- Federal holidays only by default; say so, and ask whether their contract
  counts state holidays.
- Keep party names and contact details out of anything except the files the
  agent asked for.
