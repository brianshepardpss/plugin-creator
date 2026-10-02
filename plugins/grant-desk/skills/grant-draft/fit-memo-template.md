# Fit memo: <Funder> for <Org>  (<date>)

Data: <live or CACHED SAMPLE, from script output>. IRS data lags 1-2 years.
<If demo: "Demo stand-in: the sample RFP's funder is fictional; this memo
uses <real foundation>'s public 990-PF to show the method.">

## Verdict
<Apply / Apply with changes / Do not apply> - <one sentence why, citing the
figures below>.

## Funder at a glance
| Item | Value | Source |
|---|---|---|
| Type | <foundation_type> | ProPublica |
| Latest return | <form>, tax period ending <date> | <XML URL> |
| Grants paid that year | <$> across <n> grants | grantees.py |
| Grant size | 25th pct <$>, median <$>, 75th pct <$> | grantees.py |
| Assets (latest extracted year) | <$> (<tax year>) | propublica.py |
| Giving trend | <grants paid by year, YoY %> | propublica.py |
| Accepts unsolicited requests | <yes / NO - preselected only> | 990-PF Part XV |
| How to apply (as filed) | <deadlines / restrictions text> | 990-PF Part XV |

## Who they fund near us
<n> grants to <city>, total <$>. Examples (as filed):
| Recipient | Amount | Purpose |
|---|---|---|

## Mission match
Keyword matches for <keywords>: <n>. <One honest sentence: strong / partial /
weak match, based only on the purposes listed.>

## Ask
Suggested <$> (range <$> to <$>), basis: <basis from script, n=...>.
<If the RFP cap differs, say which governs.>

## Risks and unknowns
- <e.g. one year of data; no literacy grants listed; preselected-only flag>
- Program officer names in the return are filing contacts, not confirmed
  program staff; verify on the funder's site before contacting.

Sources: <every URL printed by the scripts>
Data from ProPublica Nonprofit Explorer and the GivingTuesday 990 Data Lake (IRS e-file).
