---
name: funder-research
description: Use when the user asks whether a foundation or funder is a good fit, who a foundation funds, how big its grants are, how much to ask for, or wants prospects or federal grants, e.g. "is this foundation a fit for us", "who does the X Foundation fund", "look up this EIN", "what's their average grant", "find foundations that fund literacy in Texas", "find open federal grants for youth mentoring". Uses free public 990/990-PF data (ProPublica, IRS e-file XML grantee lists) and Grants.gov; every figure carries its source URL.
---

# Funder research from public data

Scripts are in `../../scripts/` relative to this skill's base directory. All
are standard-library Python with no API key. Each prints its source URLs and
whether data is live or a cached sample; keep both in your answer.

Never invent a program officer, priority, deadline or grant. If the data
does not show it, say "not in the public filing".

## A. "Is <foundation / EIN> a fit for us?"

1. Get the org's state, city and 3-5 mission keywords from its profile
   (`grants/profile.md`, or ask). Demo: `../../samples/sample-org/profile.md`.
2. If you only have a name: `python3 ../../scripts/propublica.py search "<name>" --state <XX>`.
   Confirm the EIN with the user if several match.
3. `python3 ../../scripts/propublica.py org <EIN>` -> type (foundation_code
   4 = private grantmaking foundation), assets, grants paid by year, trend.
   A public charity (990 filer) may still give grants; grantees.py reads
   Schedule I for those.
4. `python3 ../../scripts/grantees.py <EIN> --state <XX> --city <city> --keyword <k1,k2,k3> [--cap <RFP cap>] [--csv grants/<slug>-grants.csv]`
   -> grantee list from the latest e-filed return, grants near the user,
   keyword matches, ask range with its formula.
5. Write `grants/fit-memo-<slug>.md` using
   `../grant-draft/fit-memo-template.md`. Copy numbers from script output
   only; keep the tax year next to every figure.
6. Reply with the verdict, 3-5 key figures with tax year, 3 example
   grantees near the user with amounts, the suggested ask and range, risks
   (stale data, preselected-only, no mission matches), and the source URLs.
   End with a human review checklist: read the funder's current guidelines
   on its website; confirm the EIN match; check whether this is a
   preselected-only funder; talk to program staff before choosing the ask.

Warnings to surface whenever the script prints them:
- "only makes contributions to preselected charitable organizations" -> the
  funder does not accept unsolicited proposals; say so first.
- CACHED SAMPLE -> data may be old; offer a live rerun.
- No itemized grants -> point to the filing PDF link instead.

## B. Prospect list ("foundations that fund X near us")

ProPublica search is by name and keyword, not by what a foundation funds.
1. Run `propublica.py search "<keyword> foundation" --state <XX>` and
   `propublica.py search "family foundation" --state <XX>`, and add any
   funders the user already knows (for example, funders thanked in peer
   organizations' annual reports). Say plainly that a reverse lookup
   ("who funds organization Y") is not available from these public APIs.
2. For each candidate EIN (max 5 per turn), run steps A3-A4 with
   `--keyword` and rank by: in-state grants count, keyword matches, median
   grant vs the user's ask. Show the ranking table with the numbers.

## C. Federal grants

1. `python3 ../../scripts/grantsgov.py search "<keywords>" --eligibility 12`
   (12 = 501(c)(3) nonprofits other than universities). Add
   `--category ED|HL|ISS|CD` or `--agency HHS` to narrow.
2. Grants.gov has no state filter: tell the user that, and check each
   promising notice with `grantsgov.py opportunity <id>` for eligibility,
   floor/ceiling, cost sharing and close date.
3. Show only opportunities still open (the script drops past close dates)
   with number, title, agency, close date, days left and link. Say plainly
   that research (NIH R/P/U, NSF) listings that match by keyword are usually
   not a fit for a community nonprofit, and flag NIH's AI rule
   (NOT-OD-25-132) if the user wants help writing one.
4. Offer to add chosen close dates to the tracker (grant-tracker skill).

## Offline

If the user asks for the cached, sample or offline data, add
`--mode offline` to every call (and `--today 2026-10-02` to grantsgov.py
search, the date the cache was saved) and say the data is a saved sample.

If a live call fails, scripts fall back to `../../samples/cache/` when that
exact request is cached (demo EINs 74-2479712 and 75-6015322; searches
"literacy" TX, "youth mentoring" and "literacy" with eligibility 12).
Otherwise ask the user to upload the funder's 990-PF PDF and read Part XV
(grants paid) yourself, labeling every figure with the PDF page.

Attribution line for every memo: "Data from ProPublica Nonprofit Explorer,
the GivingTuesday 990 Data Lake (IRS e-file) and Grants.gov."
