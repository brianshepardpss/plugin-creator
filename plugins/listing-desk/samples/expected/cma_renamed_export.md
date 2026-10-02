# CMA -- not an appraisal: 26 Larkspur Dr, Cedar Hollow, TX 75999

As-of date: 2026-09-30. Source: MLS export supplied by the agent. Information deemed reliable but not guaranteed.
This comparative market analysis is a broker/agent opinion to help set a list price. It is not an appraisal and must not be used as one for lending purposes.

## Subject

| Beds | Baths | Living sqft | Lot acres | Year built | Garage | Pool | Subdivision |
|---|---|---|---|---|---|---|---|
| 4 | 2.5 | 2,150 | 0.22 | 2008 | 2 | N | Cedar Hollow Estates |

## Data check

Rows read: 11. Closed sales usable: 6. Rows dropped: 3.

| MLS # | CSV line | Reason dropped |
|---|---|---|
| (blank) | 10 | blank row |
| CH26-1007 | 8 | missing LivingArea |
| CH26-1010 | 9 | missing ClosePrice (Sold Price='TBD' not a number) |

Column mapping (your header -> RESO field):

| Your column | RESO field | How |
|---|---|---|
| ML Number | ListingId | alias |
| St | StandardStatus | alias |
| Sold Price | ClosePrice | alias |
| Sold Date | CloseDate | alias |
| Address | UnparsedAddress | alias |
| Zip Code | PostalCode | alias |
| Subdiv | SubdivisionName | alias |
| BR | BedroomsTotal | alias |
| FB | BathroomsFull | alias |
| HB | BathroomsHalf | alias |
| Sq Ft | LivingArea | alias |
| Acres | LotSizeAcres | alias |
| Yr Blt | YearBuilt | alias |
| Gar | GarageSpaces | alias |
| Pool | PoolPrivateYN | alias |
| Concess | ConcessionsAmount | alias |
| Agent Remarks | PrivateRemarks | alias |

## Comp selection

Rules: Closed; closed within 6 months of 2026-09-30; living area 1,720-2,580 sqft (+/-20%); same subdivision. Ranked by relevance score; top 6 kept (minimum 4).

| # | MLS # | Address | Closed | Close price | Concessions | Net price | Sqft | Net $/sqft | Bd | Ba | Yr | Gar | Pool | Score |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | CH26-1005 | 150 Larkspur Dr | 2026-06-18 | $394,000 | $6,000 | $388,000 | 2,190 | $177.17 | 4 | 2.5 | 2008 | 2 | N | 94.6 |
| 2 | CH26-1001 | 118 Bramble Way | 2026-08-14 | $385,000 | $5,000 | $380,000 | 2,080 | $182.69 | 4 | 2.5 | 2007 | 2 | N | 92.2 |
| 3 | CH26-1002 | 204 Bramble Way | 2026-07-02 | $402,500 | $0 | $402,500 | 2,240 | $179.69 | 4 | 2.5 | 2009 | 2 | N | 89.7 |
| 4 | CH26-1006 | 9 Fennel Pl | 2026-04-30 | $379,500 | $0 | $379,500 | 2,050 | $185.12 | 4 | 2 | 2007 | 2 | N | 85.7 |
| 5 | CH26-1003 | 31 Thistle Ct | 2026-05-22 | $371,000 | $3,500 | $367,500 | 1,960 | $187.50 | 3 | 2 | 2006 | 2 | N | 72.2 |
| 6 | CH26-1004 | 77 Larkspur Dr | 2026-09-05 | $429,000 | $0 | $429,000 | 2,380 | $180.25 | 4 | 3 | 2010 | 3 | Y | 67.2 |

## Adjustment table

Each comp is adjusted toward the subject: amount = rate x (subject - comp). Rates come from `adjustments.json`; edit them to match your market.

**Comp 1: CH26-1005 150 Larkspur Dr** -- net price $388,000

| Item | Subject | Comp | Difference | Rate | Adjustment |
|---|---|---|---|---|---|
| Living area | 2150 | 2190 | -40 | $60 per sqft | -2,400 |
| **Net adjustment** | | | | | **-2,400** |
| **Adjusted price** | | | | | **$385,600** |

Gross adjustment: 0.6% of net price.

**Comp 2: CH26-1001 118 Bramble Way** -- net price $380,000

| Item | Subject | Comp | Difference | Rate | Adjustment |
|---|---|---|---|---|---|
| Living area | 2150 | 2080 | +70 | $60 per sqft | +4,200 |
| Year built | 2008 | 2007 | +1 | $1,000 per year | +1,000 |
| Lot size | 0.22 | 0.2 | +0.02 | $20,000 per acre | +400 |
| **Net adjustment** | | | | | **+5,600** |
| **Adjusted price** | | | | | **$385,600** |

Gross adjustment: 1.5% of net price.

**Comp 3: CH26-1002 204 Bramble Way** -- net price $402,500

| Item | Subject | Comp | Difference | Rate | Adjustment |
|---|---|---|---|---|---|
| Living area | 2150 | 2240 | -90 | $60 per sqft | -5,400 |
| Year built | 2008 | 2009 | -1 | $1,000 per year | -1,000 |
| Lot size | 0.22 | 0.24 | -0.02 | $20,000 per acre | -400 |
| **Net adjustment** | | | | | **-6,800** |
| **Adjusted price** | | | | | **$395,700** |

Gross adjustment: 1.7% of net price.

**Comp 4: CH26-1006 9 Fennel Pl** -- net price $379,500

| Item | Subject | Comp | Difference | Rate | Adjustment |
|---|---|---|---|---|---|
| Living area | 2150 | 2050 | +100 | $60 per sqft | +6,000 |
| Half baths | 1 | 0 | +1 | $3,000 per half bath | +3,000 |
| Year built | 2008 | 2007 | +1 | $1,000 per year | +1,000 |
| Lot size | 0.22 | 0.21 | +0.01 | $20,000 per acre | +200 |
| **Net adjustment** | | | | | **+10,200** |
| **Adjusted price** | | | | | **$389,700** |

Gross adjustment: 2.7% of net price.

**Comp 5: CH26-1003 31 Thistle Ct** -- net price $367,500

| Item | Subject | Comp | Difference | Rate | Adjustment |
|---|---|---|---|---|---|
| Living area | 2150 | 1960 | +190 | $60 per sqft | +11,400 |
| Bedrooms | 4 | 3 | +1 | $7,500 per bedroom | +7,500 |
| Half baths | 1 | 0 | +1 | $3,000 per half bath | +3,000 |
| Year built | 2008 | 2006 | +2 | $1,000 per year | +2,000 |
| Lot size | 0.22 | 0.19 | +0.03 | $20,000 per acre | +600 |
| **Net adjustment** | | | | | **+24,500** |
| **Adjusted price** | | | | | **$392,000** |

Gross adjustment: 6.7% of net price.

**Comp 6: CH26-1004 77 Larkspur Dr** -- net price $429,000

| Item | Subject | Comp | Difference | Rate | Adjustment |
|---|---|---|---|---|---|
| Living area | 2150 | 2380 | -230 | $60 per sqft | -13,800 |
| Full baths | 2 | 3 | -1 | $6,000 per full bath | -6,000 |
| Half baths | 1 | 0 | +1 | $3,000 per half bath | +3,000 |
| Garage | 2 | 3 | -1 | $5,000 per space | -5,000 |
| Pool | 0 | 1 | -1 | $15,000 pool vs none | -15,000 |
| Year built | 2008 | 2010 | -2 | $1,000 per year | -2,000 |
| Lot size | 0.22 | 0.26 | -0.04 | $20,000 per acre | -800 |
| **Net adjustment** | | | | | **-39,600** |
| **Adjusted price** | | | | | **$389,400** |

Gross adjustment: 10.6% of net price.

## Summary

| Measure | Value | Working |
|---|---|---|
| Adjusted prices | $385,600, $385,600, $389,400, $389,700, $392,000, $395,700 | 6 comps |
| Median adjusted price | $389,550 | middle of the sorted list |
| Mean adjusted price | $389,667 | sum / 6 |
| Median net $/sqft | $181.47 | x 2,150 sqft = $390,160 (cross-check) |

## Suggested list-price range (3 tiers)

| Tier | Price | Basis |
|---|---|---|
| Low (faster sale) | $387,000 | 25th percentile of adjusted prices ($386,550), nearest $1,000 |
| Market | $390,000 | median adjusted price ($389,550), nearest $1,000 |
| High (test the market) | $391,000 | 75th percentile of adjusted prices ($391,425), nearest $1,000 |

Not adjusted by the script (agent judgment, explain to the seller): condition and updates, floor plan, view and backing, location within the subdivision, and any seller-reported upgrades.

## Current competition (not used in the price math)

| MLS # | Status | Address | List price | Sqft | List $/sqft | DOM |
|---|---|---|---|---|---|---|
| CH26-1404 | Pending | 55 Bramble Way | $0 | 2,140 | $0.00 |  |
| CH26-1401 | Active | 17 Fennel Pl | $0 | 2,170 | $0.00 |  |

---
CMA -- not an appraisal. Prepared from the agent's own MLS export for this client only; do not republish the comp data. Information deemed reliable but not guaranteed. Adjustment rates are editable assumptions, not market facts.
