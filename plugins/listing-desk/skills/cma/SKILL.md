---
name: cma
description: Use when an agent wants comps or a price opinion from their own MLS export, or says "run a CMA", "pull comps from this CSV", "what should we list it at", "adjust these comps", "price range for the seller", or uploads a Matrix/Flexmls/Paragon CSV export of sold listings. Maps the export's columns to RESO field names, reports dirty and dropped rows by MLS number, selects 4-6 closed comps, builds an adjustment table and a 3-tier list-price range with every number computed by a bundled script. Labelled "CMA -- not an appraisal".
---

# CMA from an MLS CSV export

All math comes from `cma.py` in this skill's directory. You explain it; you
never compute or adjust prices in prose.

## 1. Gather inputs

- The MLS CSV export (any MLS; headers vary). Sample: `../../samples/mls_export.csv`
  or the messier `../../samples/mls_export_renamed.csv`.
- Subject facts in a markdown file with `- Key: value` lines (see
  `../../samples/subject.md`). If the user gives facts in chat, write
  `cma/subject.md` in that shape. Required: living sqft. Strongly wanted:
  beds, full and half baths, year built, garage spaces, pool Y/N, lot acres,
  subdivision, ZIP, and the as-of date (default today).
- Never fill a missing fact with a guess. Ask once, or run without it and say
  which adjustment was skipped.

## 2. Run the script

```
python3 <base>/cma.py --csv <export.csv> --subject <subject.md> \
  --out cma/cma.md --csv-out cma/cma_adjustments.csv --json-out cma/cma.json
```

Options the agent may ask for:

| Need | Flag |
|---|---|
| A column was not recognised | `--map "Their Header=ResoField"` (fields in `reso_fields.json`) |
| Different look-back | `--months 3` |
| Wider/narrower size band | `--sqft-band 0.15` |
| More or fewer comps | `--min-comps 3 --max-comps 5` |
| Their own adjustment rates | copy `adjustments.json`, edit, `--adjustments mine.json` |
| Fixed as-of date | `--as-of 2026-09-30` |
| Cite the source MLS | `--source "<MLS name> export, pulled <date>"` |

If the script stops because ClosePrice or LivingArea is unmapped, show its
column list, ask which column is which, and re-run with `--map`.

## 3. Check the output before showing it

- Every comp is Closed and inside the date and size rules printed under
  "Comp selection". If the script widened the search, say so plainly.
- Read the "Data check" table aloud in one line: which MLS numbers were
  dropped and why (duplicate, missing sqft, unreadable price). Never patch a
  dropped row with an estimate.
- Gross adjustments over 25% are marked weak; mention them.
- The price range is the script's 25th percentile / median / 75th percentile,
  rounded to $1,000. Do not widen or move it to please the seller. If the
  agent wants a different list price, that is their call; say what the comps
  support.

## 4. Reply

```
## CMA -- not an appraisal: <address>  (as of <date>)

| Tier | Price | Basis |
| Low (faster sale) | $... | 25th percentile of adjusted comps |
| Market | $... | median adjusted ($...) |
| High (test the market) | $... | 75th percentile |

Comps (<n>): <MLS # | address | closed | net price | adjusted price>
Biggest adjustments: <comp: item +/-$...>
Data check: <dropped rows and why; header mapping notes>
Not adjusted (your judgment): condition/updates, layout, backing, location in subdivision.
Competition now: <active/pending count and list-price range from the report>

Files: cma/cma.md (full table, seller-ready), cma/cma_adjustments.csv
Source: your MLS export. Information deemed reliable but not guaranteed.
```

For a seller-facing one-pager, rewrite `cma.md` in plain language with the
same numbers, keep the "CMA -- not an appraisal" label and the source line,
and drop the private columns (concessions detail stays if the agent wants it).

## Guardrails

- Always "CMA -- not an appraisal". Never call it an appraisal, a valuation
  for lending, or a BPO; some states restrict BPOs by licensees.
- The export is licensed MLS data for this client's use. Do not suggest
  publishing the comp table on a website or social post, do not store it,
  and warn if the user asks to share it publicly.
- Do not add demographic, school-quality or crime commentary to a CMA, even
  as "market context".
