---
name: listing-kit
description: Use when a real estate agent is preparing a listing appointment or launching a new listing, or says "listing kit", "prep my listing appointment", "CMA and listing description", "get this listing ready to go live", "price this house and write the remarks", or "/listing-kit sample". Runs the whole package from an MLS CSV export and the subject property facts - CMA with adjustment table and 3-tier price range, MLS public remarks, 3 social posts, a just-listed email - then a Fair Housing check on every piece of copy.
argument-hint: "sample | <path to MLS CSV export> [subject notes]"
---

# Listing kit: CMA + listing copy + Fair Housing report

This skill orchestrates three other skills in this plugin. Paths below are
relative to this skill's base directory.

- CMA script: `../cma/cma.py` (rates in `../cma/adjustments.json`)
- Copy rules: `../listing-copy/SKILL.md`
- Fair Housing checker: `../fair-housing-check/fair_housing.py`
- Sample data: `../../samples/mls_export.csv`, `../../samples/subject.md`

## 1. Inputs

- If the argument is `sample` (or the user says "try it on the sample"), use
  the two sample files above and say they are fictional.
- Otherwise you need (a) the agent's MLS CSV export of nearby sales and
  listings, and (b) the subject property facts. If facts arrive in chat, write
  them to `listing-kit/subject.md` in the same shape as the sample subject
  file (a "Property facts" list of `- Key: value` lines, including
  `As Of Date`). Ask once for anything missing that the CMA needs: living
  sqft, beds, full/half baths, year built, subdivision or ZIP.
- Never invent a fact, feature, upgrade or sale. If it is not in the export,
  the subject file or the user's words, it does not go in the output.

## 2. CMA

Create the folder `listing-kit/` in the working (outputs) directory, then run:

```
python3 <base>/../cma/cma.py --csv <export.csv> --subject <subject.md> \
  --out listing-kit/cma.md --csv-out listing-kit/cma_adjustments.csv \
  --json-out listing-kit/cma.json
```

- If it exits saying it cannot find ClosePrice or LivingArea, show the column
  list it printed, ask which columns hold sold price and living area, and
  re-run with `--map "<their column>=ClosePrice"`.
- Use the script's numbers exactly. Do not round, re-add or "sanity adjust"
  them in prose. If the agent wants different rates, edit a copy of
  `adjustments.json` and re-run with `--adjustments`.
- Read the dropped-rows table and the widening notes; mention them.

## 3. Listing copy

Read `../listing-copy/SKILL.md` and follow it to write:

- `listing-kit/remarks.txt` -- MLS public remarks only, plain text, at or
  under the cap (default 1,000 characters; ask if their MLS differs).
- `listing-kit/social.md` -- 3 posts (Instagram/Facebook, a short one, and a
  "coming soon / just listed" one).
- `listing-kit/email.md` -- a just-listed email to the agent's sphere
  (subject line + body + unsubscribe line).

Use `[LIST PRICE]` as a placeholder until the agent picks a tier; never pick
the list price for them.

Seller notes often contain things that cannot be used (for example "great
for families", "safe neighborhood", "near the good schools", "offer 3% to the
buyer's agent"). Leave them out and tell the agent which ones and why.

## 4. Fair Housing check (always, on every file)

```
python3 <base>/../fair-housing-check/fair_housing.py \
  --remarks listing-kit/remarks.txt listing-kit/social.md listing-kit/email.md \
  --cap 1000 --out listing-kit/fair_housing_report.md
```

- Any FLAG: rewrite that phrase (describe the property, not the people), save,
  and re-run. Repeat until there are zero FLAGs. Never show copy that still
  has a FLAG.
- REVIEW: fix it, or keep it and say in one line why it is acceptable.
- Then do the context review in `../fair-housing-check/SKILL.md` step 3
  (things a phrase list cannot see) and note anything you changed.

## 5. Reply

Answer in this shape (keep the totals exactly as the scripts printed them):

```
## Listing kit: <address>   (CMA -- not an appraisal)

**Suggested list-price range** (from <n> closed comps, adjusted)
| Tier | Price |
| Low (faster sale) | $... |
| Market | $... |
| High (test the market) | $... |
Median adjusted price $...; data check: <rows dropped and why>.

**Comps used:** <MLS # - address - net price - adjusted price>, one per line.

**MLS public remarks** (<chars>/<cap> characters)
<remarks text>

**Social posts** -- see listing-kit/social.md (first post shown)
**Just-listed email** -- see listing-kit/email.md (subject line shown)

**Fair Housing check:** <PASS / REVIEW> -- <n> FLAG fixed before showing you,
<what was rewritten>. Seller notes left out: <list and why>.

Files: listing-kit/cma.md, cma_adjustments.csv, remarks.txt, social.md,
email.md, fair_housing_report.md

Next: pick a price tier and I will drop it into the copy. Information deemed
reliable but not guaranteed; comps come from your own MLS export and should
not be republished.
```

## Guardrails

- Label every CMA "CMA -- not an appraisal". Do not call it an appraisal,
  valuation report or BPO.
- No buyer-agent compensation anywhere in MLS remarks, ever.
- The export is the agent's licensed MLS data: use it for this client only,
  do not suggest publishing the comp table, and keep it out of feedback.
- Drafts only. Do not post, send or upload anything.
