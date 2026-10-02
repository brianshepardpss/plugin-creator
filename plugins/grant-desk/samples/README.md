# Grant Desk samples

Everything here lets the hero workflow run with no account, key or network.
Organizations, people and donors in these files are fictional, except the
cached public records in `cache/`.

| File | What it is |
|---|---|
| `sample-org/profile.md` | Org profile for "Riverbend Youth Literacy" (fictional, Waco, TX): mission, programs, staff, a 17-row Facts table with sources and dates, known gaps. One fact (F17) is deliberately stale. |
| `sample-rfp.md` | Fictional family-foundation literacy RFP: 4 questions with word limits, $25,000 cap, LOI/proposal/report dates, an AI-use policy. Names a real stand-in EIN for the fit-memo demo. |
| `sample-budget.csv` | Program budget export with the usual mess: "$60,000" strings, a blank row, a subtotal row, a TOTAL row, qty x unit cost lines with no total. |
| `sample-donors.csv` | 38 gift rows for 24 fictional donors (example.org emails), one exact duplicate, one blank row, mixed date formats and recurring flags. |
| `award-letter.md` | Fictional award letter with relative report deadlines ("6 months after the start"). |
| `cache/` | Raw public API responses saved 2026-10-02 (see `cache/MANIFEST.json`): ProPublica Nonprofit Explorer org records for EINs 74-2479712 and 75-6015322 and a "literacy" TX search; IRS e-file 990-PF XML for both from the GivingTuesday 990 Data Lake; Grants.gov search2 results for "youth mentoring" and "literacy" (eligibility 12) and one opportunity record. Scripts use these automatically when offline or with `--mode offline`. |
| `expected/` | Script outputs on these samples (budget check, draft check, donor segments, grantee list, tracker) and a hand-written reference draft, used by the evals. |

The real foundations in `cache/` are used only as public-data examples. They
did not write the sample RFP and have no connection to Grant Desk.
