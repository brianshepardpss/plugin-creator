# Grant Desk

A grant-writing desk for small nonprofits. It looks up who a foundation
actually funds, using free public 990-PF grantee lists, and searches open
federal grants on Grants.gov. It drafts proposal sections from your own org
profile and tags every claim to its source, or marks it [NEEDS DATA] if
there is no source. It checks word limits and budget math with scripts and
puts every deadline into a tracker and calendar file. It never invents a
number.

For: executive directors, one- or two-person development teams and
contract grant writers at US 501(c)(3)s with budgets of roughly $250K-$5M.

Works in: Claude Cowork, claude.ai and Claude Code. You don't need an
account, API key or paid database. The scripts are standard-library Python.

## Install (60 seconds)

Claude Code:

```
/plugin marketplace add brianshepardpss/plugin-creator
/plugin install grant-desk@plugin-creator
```

Cowork / claude.ai: add the marketplace `brianshepardpss/plugin-creator` in
plugin settings, then install "Grant Desk".

## Try it on the sample (about 5 minutes)

```
/grant-draft sample
```

Or, in Cowork or claude.ai, just say: "Try Grant Desk on the sample RFP."

This runs on a fictional organization (Riverbend Youth Literacy, Waco, TX)
and a fictional family-foundation RFP (4 questions, word limits, $25,000
cap). The output:

1. **AI-policy gate.** It reads the RFP's AI-use section first. This one
   permits AI with disclosure, so it runs in DRAFT mode.
2. **Fit memo from real public data.** The sample funder is fictional, so
   the demo looks up a real Waco foundation as a stand-in (Bernard & Audre
   Rapoport Foundation, EIN 74-2479712). Its 2025 990-PF lists 41 grants
   totaling $2,020,399. 16 of them, $480,777 in total, went to Waco
   organizations, and the median comparable grant was $25,000. So the
   $25,000 cap is a realistic ask there. Every figure comes with the
   tax year and source URL.
3. **Section draft** in `grants/draft-<funder>.md`. Every number is tagged,
   for example `[source: profile#F05]`. Gaps such as the demographics of
   students served are marked `[NEEDS DATA: ...]`, not filled with a
   made-up statistic.
4. **Draft check.** A script counts words against each limit, finds
   numbers with no source tag and numbers that don't match the fact they
   cite, and warns about stale facts. Sample output is in
   `samples/expected/draft-check.md`.
5. **Deadlines** go to `grants/tracker.csv` and `grants/deadlines.ics`
   (LOI, proposal and both report dates, with reminders 14 and 3 days
   before each).

The demo uses cached copies of the public data in `samples/cache/`, so it
works offline. On your own funders, the same scripts fetch live data.

## What it does

| Skill | You say | You get |
|---|---|---|
| grant-draft | "draft this grant", "answer these RFP questions" | AI-policy gate, question map, fit memo, tagged draft, word-limit and number check, deadlines tracked |
| funder-research | "is this foundation a fit?", "who does EIN 75-6015322 fund?", "open federal grants for youth mentoring" | 990/990-PF financials and trend, the grantee list near you, keyword matches, an ask range with its formula, Grants.gov opportunities still open |
| org-profile | "build our org profile", "pull the facts out of our old proposals" | `grants/profile.md`: mission, programs and a Facts table where every number has a source and an as-of date |
| logic-model-budget | "build the logic model", "write the budget narrative" | a logic model table and a budget narrative that a script checks against your budget CSV |
| grant-tracker | "add the report deadlines from this award letter" | `tracker.csv` plus a `.ics` calendar file; relative dates ("6 months after start") computed by script |
| donor-thanks | "year-end thank-you letters from this donor export" | donor segments (monthly, major, first-time, repeat, lapsed) and mail-merged letters, with the IRS $250+ acknowledgment sentence |
| request | "I wish this could..." | a feature request you can file yourself |

Command: `/grant-draft [sample | RFP path] [profile path]`.

## Guardrails built in

- **Funder AI policies.** Before drafting, it checks the RFP or asks you
  for the funder's policy. For restricted funders it switches to ASSIST
  mode: outline, critique and edits of text you write, but no finished
  prose. This applies to NIH under NOT-OD-25-132, which won't consider
  applications "substantially developed by AI", and to the Spencer
  Foundation, which bars verbatim AI drafts.
- **No invented facts.** Numbers come only from your profile, your files
  or a script output with a URL. `draft_check.py` fails the draft if any
  number has no source tag.
- **Exact math.** Word counts, budget totals and shares, ask ranges, dates
  and donor counts all come from bundled scripts that show their formulas.
- **Donor privacy.** `donors.py` reads names and emails on your machine
  and prints only counts. Claude writes templates with placeholders, and
  the script merges them locally.
- Every output ends with a human review checklist.

## Privacy: what leaves your machine

- Funder research sends only EINs, keywords and state codes to the public
  ProPublica Nonprofit Explorer API, the GivingTuesday 990 Data Lake (AWS
  S3) and the Grants.gov API. Nothing about your organization is sent.
- Your profile, drafts, budgets, tracker and donor files stay in your
  working folder and your Claude conversation. Donor data is never sent to
  any of the services above.
- No telemetry. The request skill only drafts an issue for you to file.

## Data notes

- IRS data lags 1-2 years, and every figure shows its tax year.
  ProPublica's extracted financials can be a year behind the newest e-filed
  XML. Grant Desk reads both and labels each.
- Grantee lists come from e-filed returns only. For paper filers, upload
  the 990-PF PDF and Grant Desk reads Part XV with you.
- Grants.gov search has no state filter. Check eligibility in each notice.

Data from ProPublica Nonprofit Explorer, the GivingTuesday 990 Data Lake
(IRS e-file) and Grants.gov.

Not affiliated with or endorsed by ProPublica.
Not affiliated with or endorsed by Candid.
Not affiliated with or endorsed by GivingTuesday.
Not affiliated with or endorsed by Grants.gov or any federal agency.
Not affiliated with or endorsed by Amazon Web Services.
Not affiliated with or endorsed by the Bernard & Audre Rapoport Foundation, the Meadows Foundation, the Spencer Foundation or NIH.
