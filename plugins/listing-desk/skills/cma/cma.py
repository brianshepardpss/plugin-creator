#!/usr/bin/env python3
"""Comparative market analysis (CMA) from an MLS CSV export. Standard library only.

Usage:
  python3 cma.py --csv EXPORT.csv --subject SUBJECT.md [--adjustments adjustments.json]
                 [--map "Sq Ft=LivingArea"] [--as-of YYYY-MM-DD] [--months 6]
                 [--sqft-band 0.20] [--min-comps 4] [--max-comps 6]
                 [--out cma.md] [--csv-out adjustments.csv] [--json-out cma.json]

What it does, in order (every step is printed in the report):
  1. Header mapping: each CSV column is matched to a RESO Data Dictionary field
     name (ListingId, ClosePrice, LivingArea, ...) using reso_fields.json
     aliases (exact match after normalising case/punctuation, then a close
     match at >= 0.88 similarity). --map overrides any column.
  2. Cleaning: "$1,234" -> 1234, dates in MM/DD/YYYY or YYYY-MM-DD, Y/N/Yes/No.
     Rows dropped (and listed by MLS #): blank, exact duplicate MLS #, Closed
     without a usable close price, close date or living area.
  3. Comp selection: StandardStatus Closed, CloseDate within --months of the
     as-of date, LivingArea within +/- --sqft-band of the subject, same
     subdivision. Fewer than --min-comps: widen to same ZIP, then to 12 months.
     Each widening is reported.
  4. Relevance score (higher is closer), per candidate:
       100 - 2 x |sqft diff %| - 5 x |bed diff| - 4 x |bath diff|
           - 0.5 x months since close - 0.5 x |year built diff|
           - 3 x |garage diff| - 5 x (pool mismatch)
     where bath = full + 0.5 x half. Top --max-comps are kept.
  5. Adjustments (rates from adjustments.json, editable): every comp is
     adjusted TOWARD the subject:
       net price      = ClosePrice - ConcessionsAmount
       line item      = rate x (subject value - comp value)
       adjusted price = net price + sum(line items)
     Gross adjustment % = sum(|line items|) / net price; over 25% is flagged.
  6. Price range (3 tiers) from the adjusted prices of the selected comps:
       Low    = 25th percentile   (statistics.quantiles, method="inclusive")
       Market = median
       High   = 75th percentile
     each rounded to the nearest $1,000. The range always brackets the median.
     Also shown: mean adjusted price and median net $/sqft x subject sqft.

Output is labelled "CMA -- not an appraisal". Nothing is sent anywhere; the
export is read locally and not stored.
"""
import argparse
import csv
import difflib
import json
import re
import statistics
import sys
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
NUMERIC = {"ListPrice", "OriginalListPrice", "ClosePrice", "DaysOnMarket",
           "CumulativeDaysOnMarket", "BedroomsTotal", "BathroomsFull",
           "BathroomsHalf", "BathroomsTotalInteger", "LivingArea", "LotSizeAcres",
           "LotSizeSquareFeet", "YearBuilt", "GarageSpaces", "StoriesTotal",
           "AssociationFee", "ConcessionsAmount"}
DATES = {"CloseDate", "ListingContractDate"}
BOOLS = {"PoolPrivateYN"}
STATUS = {"closed": "Closed", "sold": "Closed", "sld": "Closed", "s": "Closed", "closed sale": "Closed",
          "cls": "Closed", "clsd": "Closed", "sold/closed": "Closed", "settled": "Closed",
          "active": "Active", "a": "Active", "act": "Active",
          "pending": "Pending", "p": "Pending", "pnd": "Pending",
          "under contract": "Pending", "active under contract": "ActiveUnderContract",
          "option pending": "Pending", "contingent": "Pending",
          "expired": "Expired", "exp": "Expired", "x": "Expired",
          "withdrawn": "Withdrawn", "wd": "Withdrawn", "canceled": "Canceled",
          "cancelled": "Canceled", "terminated": "Canceled", "temp off market": "Hold"}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def load_aliases():
    data = json.loads((HERE / "reso_fields.json").read_text())
    table = {}
    for field, aliases in data["fields"].items():
        table[norm(field)] = field
        for a in aliases:
            table[norm(a)] = field
    return table


def map_headers(headers, overrides):
    table = load_aliases()
    mapping, how, used = {}, {}, set()
    for h in headers:
        if h in overrides:
            mapping[h], how[h] = overrides[h], "override"
        elif norm(h) in table:
            mapping[h], how[h] = table[norm(h)], "alias"
        else:
            close = difflib.get_close_matches(norm(h), list(table), n=1, cutoff=0.88)
            if close:
                mapping[h], how[h] = table[close[0]], "close match"
    final = {}
    for h in headers:  # first column wins if two map to the same field
        f = mapping.get(h)
        if f and f not in used:
            final[h] = f
            used.add(f)
    return final, how


def money(v):
    if v is None:
        return None
    s = str(v).strip().replace("$", "").replace(",", "")
    if s == "" or s.lower() in {"na", "n/a", "-", "none"}:
        return None
    try:
        return float(s)
    except ValueError:
        return "BAD"


def parse_date(v):
    s = (v or "").strip()
    if not s:
        return None
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y", "%m-%d-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return "BAD"


def yn(v):
    """Y/N/descriptive pool text -> True/False; blank -> None (unknown)."""
    s = (v or "").strip().lower()
    if s == "":
        return None
    if s in {"y", "yes", "true", "1", "private", "in ground", "inground"}:
        return True
    if s in {"n", "no", "false", "0", "none", "n/a", "na"}:
        return False
    if re.search(r"\bno\b|none|n/a|community|neighbou?rhood|association|hoa|shared", s):
        return False  # "No Pool", "Community Pool" are not a private pool
    return True  # descriptive private-pool text ("Heated, In Ground") means yes


def clean_row(raw, mapping):
    rec, problems = {}, []
    for col, field in mapping.items():
        v = raw.get(col, "")
        if field in NUMERIC:
            x = money(v)
            if x == "BAD":
                problems.append(f"{col}={v!r} not a number")
                x = None
            rec[field] = x
        elif field in DATES:
            x = parse_date(v)
            if x == "BAD":
                problems.append(f"{col}={v!r} not a date")
                x = None
            rec[field] = x
        elif field in BOOLS:
            rec[field] = yn(v)
        elif field == "StandardStatus":
            raw_status = (v or "").strip()
            rec[field] = STATUS.get(raw_status.lower(), raw_status)
            if raw_status and raw_status.lower() not in STATUS:
                problems.append(f"status {raw_status!r} not recognised (row not treated as Closed)")
        else:
            rec[field] = (v or "").strip()
    return rec, problems


def baths(r):
    if r.get("BathroomsFull") is not None:
        return (r.get("BathroomsFull") or 0) + 0.5 * (r.get("BathroomsHalf") or 0)
    return r.get("BathroomsTotalInteger") or 0


def parse_subject(path):
    text = Path(path).read_text()
    pairs = {}
    for line in text.splitlines():
        m = re.match(r"^\s*[-*]?\s*([A-Za-z][A-Za-z0-9 /#()._-]*?)\s*:\s*(.+?)\s*$", line)
        if m:
            pairs.setdefault(m.group(1).strip(), m.group(2).strip())
    mapping, _ = map_headers(list(pairs), {})
    subj, _ = clean_row(pairs, mapping)
    asof = pairs.get("As Of Date") or pairs.get("As-of Date") or pairs.get("As Of")
    return subj, (parse_date(asof) if asof else None)


def months_between(a, b):
    return (b.year - a.year) * 12 + (b.month - a.month) + (b.day - a.day) / 30.0


def score(s, c, asof):
    sq = abs(c["LivingArea"] - s["LivingArea"]) / s["LivingArea"] * 100
    pts = 100 - 2 * sq
    if c.get("BedroomsTotal") is not None and s.get("BedroomsTotal") is not None:
        pts -= 5 * abs(c["BedroomsTotal"] - s["BedroomsTotal"])
    pts -= 4 * abs(baths(c) - baths(s))
    pts -= 0.5 * months_between(c["CloseDate"], asof)
    if c.get("YearBuilt") and s.get("YearBuilt"):
        pts -= 0.5 * abs(c["YearBuilt"] - s["YearBuilt"])
    if c.get("GarageSpaces") is not None and s.get("GarageSpaces") is not None:
        pts -= 3 * abs(c["GarageSpaces"] - s["GarageSpaces"])
    if c.get("PoolPrivateYN") is not None and s.get("PoolPrivateYN") is not None:
        pts -= 5 * (c["PoolPrivateYN"] != s["PoolPrivateYN"])
    return round(pts, 1)


def adjust(s, c, rates):
    items = []
    def add(label, rate, sv, cv, unit):
        if sv is None or cv is None:
            return
        diff = sv - cv
        amt = round(rate * diff)
        if amt:
            items.append({"item": label, "subject": sv, "comp": cv, "diff": round(diff, 2),
                          "rate": f"${rate:,.0f} {unit}", "amount": amt})
    add("Living area", rates["living_area_per_sqft"], s.get("LivingArea"), c.get("LivingArea"), "per sqft")
    add("Bedrooms", rates["bedroom"], s.get("BedroomsTotal"), c.get("BedroomsTotal"), "per bedroom")
    add("Full baths", rates["full_bath"], s.get("BathroomsFull"), c.get("BathroomsFull"), "per full bath")
    add("Half baths", rates["half_bath"], s.get("BathroomsHalf"), c.get("BathroomsHalf"), "per half bath")
    add("Garage", rates["garage_space"], s.get("GarageSpaces"), c.get("GarageSpaces"), "per space")
    sp, cp = s.get("PoolPrivateYN"), c.get("PoolPrivateYN")
    add("Pool", rates["pool"], None if sp is None else int(sp), None if cp is None else int(cp), "pool vs none")
    add("Year built", rates["year_built_per_year"], s.get("YearBuilt"), c.get("YearBuilt"), "per year")
    add("Lot size", rates["lot_per_acre"], s.get("LotSizeAcres"), c.get("LotSizeAcres"), "per acre")
    if rates.get("market_time_pct_per_month"):
        net = c["ClosePrice"] - (c.get("ConcessionsAmount") or 0)
        m = round(months_between(c["CloseDate"], ASOF), 1)
        amt = round(net * rates["market_time_pct_per_month"] / 100 * m)
        if amt:
            items.append({"item": "Market time", "subject": "as-of", "comp": str(c["CloseDate"]),
                          "diff": m, "rate": f"{rates['market_time_pct_per_month']}% per month", "amount": amt})
    return items


def r1000(x):
    return int(round(x / 1000.0)) * 1000


def fmt(x):
    return f"${x:,.0f}"


def pool_txt(v):
    return "?" if v is None else ("Y" if v else "N")


def g(x):
    """Plain number for tables: 4.0 -> 4, 0.22 -> 0.22, None -> blank."""
    if x is None:
        return ""
    if isinstance(x, float):
        return f"{x:g}"
    return str(x)


ASOF = None


def main():
    global ASOF
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--subject", required=True)
    ap.add_argument("--adjustments", default=str(HERE / "adjustments.json"))
    ap.add_argument("--map", action="append", default=[], help='"CSV column=ResoField"')
    ap.add_argument("--as-of")
    ap.add_argument("--months", type=int, default=6)
    ap.add_argument("--sqft-band", type=float, default=0.20)
    ap.add_argument("--min-comps", type=int, default=4)
    ap.add_argument("--max-comps", type=int, default=6)
    ap.add_argument("--source", default="MLS export supplied by the agent")
    ap.add_argument("--out")
    ap.add_argument("--csv-out")
    ap.add_argument("--json-out")
    a = ap.parse_args()

    overrides = dict(m.split("=", 1) for m in a.map)
    subj, subj_asof = parse_subject(a.subject)
    ASOF = parse_date(a.as_of) if a.as_of else (subj_asof or date.today())
    for need in ("LivingArea",):
        if not subj.get(need):
            sys.exit(f"subject is missing {need}; add it to the subject file")
    rates = json.loads(Path(a.adjustments).read_text())["rates"]

    with open(a.csv, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        raws = list(reader)
    mapping, how = map_headers(headers, overrides)
    unmapped = [h for h in headers if h not in mapping]
    if "ClosePrice" not in mapping.values() or "LivingArea" not in mapping.values():
        print("Could not find ClosePrice and LivingArea columns. Mapping found:", file=sys.stderr)
        for h in headers:
            print(f"  {h} -> {mapping.get(h, '(unmapped)')}", file=sys.stderr)
        sys.exit("Re-run with --map \"<your column>=ClosePrice\" (and/or LivingArea).")

    rows, dropped, seen = [], [], {}
    for i, raw in enumerate(raws, start=2):
        if not any((v or "").strip() for v in raw.values()):
            dropped.append(("(blank)", i, "blank row"))
            continue
        rec, probs = clean_row(raw, mapping)
        rec["_line"] = i
        lid = rec.get("ListingId") or f"line {i}"
        if lid in seen:
            dropped.append((lid, i, f"duplicate of line {seen[lid]}"))
            continue
        seen[lid] = i
        rec["_problems"] = probs
        rows.append(rec)

    closed = [r for r in rows if r.get("StandardStatus") == "Closed"]
    usable = []
    for r in closed:
        miss = [f for f in ("ClosePrice", "CloseDate", "LivingArea") if not r.get(f)]
        if miss:
            why = "missing " + ", ".join(miss)
            if r["_problems"]:
                why += " (" + "; ".join(r["_problems"]) + ")"
            dropped.append((r.get("ListingId"), r["_line"], why))
        else:
            usable.append(r)

    lo, hi = subj["LivingArea"] * (1 - a.sqft_band), subj["LivingArea"] * (1 + a.sqft_band)
    widen = []

    def candidates(months, scope):
        out = []
        for r in usable:
            age = months_between(r["CloseDate"], ASOF)
            if age < 0 or age > months:
                continue
            if not lo <= r["LivingArea"] <= hi:
                continue
            if scope == "subdivision" and subj.get("SubdivisionName"):
                if norm(r.get("SubdivisionName", "")) != norm(subj["SubdivisionName"]):
                    continue
            if scope in ("subdivision", "zip") and subj.get("PostalCode"):
                if str(r.get("PostalCode", ""))[:5] != str(subj["PostalCode"])[:5]:
                    continue
            out.append(r)
        return out

    if not subj.get("PostalCode"):
        m = re.search(r"\b(\d{5})\b", subj.get("UnparsedAddress", ""))
        if m:
            subj["PostalCode"] = m.group(1)
    plan = [(a.months, "subdivision"), (a.months, "zip"), (12, "zip")]
    scope_used = None
    for months, scope in plan:
        cands = candidates(months, scope)
        scope_used = (months, scope)
        if len(cands) >= a.min_comps:
            break
        widen.append(f"only {len(cands)} closed sales within {months} months in same {scope}; widening")
    for c in cands:
        c["_score"] = score(subj, c, ASOF)
    cands.sort(key=lambda c: (-c["_score"], c.get("ListingId", "")))
    comps = cands[: a.max_comps]
    not_used = cands[a.max_comps:]

    results = []
    for c in comps:
        net = c["ClosePrice"] - (c.get("ConcessionsAmount") or 0)
        items = adjust(subj, c, rates)
        total = sum(i["amount"] for i in items)
        gross = sum(abs(i["amount"]) for i in items)
        results.append({"ListingId": c.get("ListingId"), "Address": c.get("UnparsedAddress"),
                        "CloseDate": str(c["CloseDate"]), "ClosePrice": c["ClosePrice"],
                        "Concessions": c.get("ConcessionsAmount") or 0, "NetPrice": net,
                        "LivingArea": c["LivingArea"], "NetPerSqft": round(net / c["LivingArea"], 2),
                        "Beds": c.get("BedroomsTotal"), "Baths": baths(c),
                        "YearBuilt": c.get("YearBuilt"), "Garage": c.get("GarageSpaces"),
                        "Pool": c.get("PoolPrivateYN"), "Score": c["_score"],
                        "Adjustments": items, "NetAdjustment": total,
                        "GrossPct": round(gross / net * 100, 1), "AdjustedPrice": net + total})

    report = []
    P = report.append
    P(f"# CMA -- not an appraisal: {subj.get('UnparsedAddress', 'subject property')}")
    P("")
    P(f"As-of date: {ASOF}. Source: {a.source}. Information deemed reliable but not guaranteed.")
    P("This comparative market analysis is a broker/agent opinion to help set a list price. "
      "It is not an appraisal and must not be used as one for lending purposes.")
    P("")
    P("## Subject")
    P("")
    P(f"| Beds | Baths | Living sqft | Lot acres | Year built | Garage | Pool | Subdivision |")
    P("|---|---|---|---|---|---|---|---|")
    P(f"| {g(subj.get('BedroomsTotal'))} | {g(baths(subj))} | {subj['LivingArea']:,.0f} | "
      f"{g(subj.get('LotSizeAcres'))} | {g(subj.get('YearBuilt'))} | {g(subj.get('GarageSpaces'))} | "
      f"{pool_txt(subj.get('PoolPrivateYN'))} | {subj.get('SubdivisionName', '')} |")
    P("")
    P("## Data check")
    P("")
    P(f"Rows read: {len(raws)}. Closed sales usable: {len(usable)}. Rows dropped: {len(dropped)}.")
    P("")
    P("| MLS # | CSV line | Reason dropped |")
    P("|---|---|---|")
    for lid, line, why in dropped:
        P(f"| {lid} | {line} | {why} |")
    P("")
    dropped_lines = {line for _, line, _ in dropped}
    kept_probs = [r for r in rows if r["_problems"] and r["_line"] not in dropped_lines]
    if kept_probs:
        P("Values that could not be read (row kept, value ignored -- not guessed):")
        P("")
        P("| MLS # | CSV line | Problem |")
        P("|---|---|---|")
        for r in kept_probs:
            P(f"| {r.get('ListingId')} | {r['_line']} | {'; '.join(r['_problems'])} |")
        P("")
    gaps = [(r["ListingId"], f) for r in results for f, k in (("Beds", "BedroomsTotal"), ("YearBuilt", "YearBuilt"),
            ("Garage", "GarageSpaces"), ("Pool", "PoolPrivateYN")) if r[f] is None]
    if gaps:
        P("Missing facts on comps used (that adjustment skipped, not guessed): "
          + ", ".join(f"{lid} {f}" for lid, f in gaps) + ".")
        P("")
    P("Column mapping (your header -> RESO field):")
    P("")
    P("| Your column | RESO field | How |")
    P("|---|---|---|")
    for h in headers:
        if h in mapping:
            P(f"| {h} | {mapping[h]} | {how.get(h, '')} |")
    if unmapped:
        P(f"| {', '.join(unmapped)} | (not used) | |")
    P("")
    P("## Comp selection")
    P("")
    months, scope = scope_used
    P(f"Rules: Closed; closed within {months} months of {ASOF}; living area "
      f"{lo:,.0f}-{hi:,.0f} sqft (+/-{a.sqft_band:.0%}); same {scope}. "
      f"Ranked by relevance score; top {a.max_comps} kept (minimum {a.min_comps}).")
    for w in widen:
        P(f"- Widened: {w}.")
    if len(comps) < a.min_comps:
        P(f"- WARNING: only {len(comps)} comps found even after widening. Treat the range as weak.")
    if not_used:
        P("- Qualified but not used (lower score): " + ", ".join(
            f"{c.get('ListingId')} (score {c['_score']})" for c in not_used))
    P("")
    P("| # | MLS # | Address | Closed | Close price | Concessions | Net price | Sqft | Net $/sqft | Bd | Ba | Yr | Gar | Pool | Score |")
    P("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for n, r in enumerate(results, 1):
        P(f"| {n} | {r['ListingId']} | {r['Address']} | {r['CloseDate']} | {fmt(r['ClosePrice'])} | "
          f"{fmt(r['Concessions'])} | {fmt(r['NetPrice'])} | {r['LivingArea']:,.0f} | ${r['NetPerSqft']:,.2f} | "
          f"{g(r['Beds'])} | {g(r['Baths'])} | {g(r['YearBuilt'])} | {g(r['Garage'])} | {pool_txt(r['Pool'])} | {r['Score']} |")
    P("")
    P("## Adjustment table")
    P("")
    P("Each comp is adjusted toward the subject: amount = rate x (subject - comp). "
      f"Rates come from `{Path(a.adjustments).name}`; edit them to match your market.")
    P("")
    for n, r in enumerate(results, 1):
        P(f"**Comp {n}: {r['ListingId']} {r['Address']}** -- net price {fmt(r['NetPrice'])}")
        P("")
        P("| Item | Subject | Comp | Difference | Rate | Adjustment |")
        P("|---|---|---|---|---|---|")
        for i in r["Adjustments"]:
            P(f"| {i['item']} | {g(i['subject'])} | {g(i['comp'])} | {i['diff']:+g} | {i['rate']} | {i['amount']:+,} |")
        if not r["Adjustments"]:
            P("| (none) | | | | | 0 |")
        flag = "  (over 25%: weak comp)" if r["GrossPct"] > 25 else ""
        P(f"| **Net adjustment** | | | | | **{r['NetAdjustment']:+,}** |")
        P(f"| **Adjusted price** | | | | | **{fmt(r['AdjustedPrice'])}** |")
        P("")
        P(f"Gross adjustment: {r['GrossPct']}% of net price{flag}.")
        P("")
    adj = [r["AdjustedPrice"] for r in results]
    summary = {}
    if len(adj) < 2:
        P("## Summary")
        P("")
        P("Fewer than 2 usable comps: no price range computed. Widen the export (more months, nearby "
          "subdivisions) or pass --months / --sqft-band, and say so to the seller.")
        P("")
    if len(adj) >= 2:
        q1, med, q3 = statistics.quantiles(adj, n=4, method="inclusive")
        mean = statistics.mean(adj)
        ppsf = statistics.median([r["NetPerSqft"] for r in results])
        summary = {"low": r1000(q1), "market": r1000(med), "high": r1000(q3),
                   "low_raw": round(q1, 2), "median_raw": round(med, 2), "high_raw": round(q3, 2),
                   "mean": round(mean, 2), "median_net_ppsf": ppsf,
                   "ppsf_value": round(ppsf * subj["LivingArea"], 2),
                   "min": min(adj), "max": max(adj), "comps": len(adj)}
        P("## Summary")
        P("")
        P("| Measure | Value | Working |")
        P("|---|---|---|")
        P(f"| Adjusted prices | {', '.join(fmt(x) for x in sorted(adj))} | {len(adj)} comps |")
        P(f"| Median adjusted price | {fmt(med)} | middle of the sorted list |")
        P(f"| Mean adjusted price | {fmt(mean)} | sum / {len(adj)} |")
        P(f"| Median net $/sqft | ${ppsf:,.2f} | x {subj['LivingArea']:,.0f} sqft = {fmt(ppsf * subj['LivingArea'])} (cross-check) |")
        P("")
        P("## Suggested list-price range (3 tiers)")
        P("")
        P("| Tier | Price | Basis |")
        P("|---|---|---|")
        P(f"| Low (faster sale) | {fmt(summary['low'])} | 25th percentile of adjusted prices ({fmt(q1)}), nearest $1,000 |")
        P(f"| Market | {fmt(summary['market'])} | median adjusted price ({fmt(med)}), nearest $1,000 |")
        P(f"| High (test the market) | {fmt(summary['high'])} | 75th percentile of adjusted prices ({fmt(q3)}), nearest $1,000 |")
        P("")
        P("Not adjusted by the script (agent judgment, explain to the seller): condition and updates, "
          "floor plan, view and backing, location within the subdivision, and any seller-reported upgrades.")
        P("")
    competition = [r for r in rows if r.get("StandardStatus") in ("Active", "Pending", "ActiveUnderContract")
                   and r.get("LivingArea") and lo <= r["LivingArea"] <= hi
                   and norm(r.get("SubdivisionName", "")) == norm(subj.get("SubdivisionName", ""))]
    if competition:
        P("## Current competition (not used in the price math)")
        P("")
        P("| MLS # | Status | Address | List price | Sqft | List $/sqft | DOM |")
        P("|---|---|---|---|---|---|---|")
        for r in competition:
            lp = r.get("ListPrice") or 0
            P(f"| {r.get('ListingId')} | {r.get('StandardStatus')} | {r.get('UnparsedAddress')} | {fmt(lp)} | "
              f"{r['LivingArea']:,.0f} | ${lp / r['LivingArea']:,.2f} | {g(r.get('DaysOnMarket'))} |")
        P("")
    P("---")
    P("CMA -- not an appraisal. Prepared from the agent's own MLS export for this client only; "
      "do not republish the comp data. Information deemed reliable but not guaranteed. "
      "Adjustment rates are editable assumptions, not market facts.")
    text = "\n".join(report) + "\n"
    if a.out:
        Path(a.out).write_text(text)
    print(text)
    if a.csv_out:
        with open(a.csv_out, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["Comp", "ListingId", "Address", "Item", "Subject", "Comp value", "Difference", "Rate", "Amount"])
            for n, r in enumerate(results, 1):
                w.writerow([n, r["ListingId"], r["Address"], "Net price", "", "", "", "", r["NetPrice"]])
                for i in r["Adjustments"]:
                    w.writerow([n, r["ListingId"], r["Address"], i["item"], i["subject"], i["comp"], i["diff"], i["rate"], i["amount"]])
                w.writerow([n, r["ListingId"], r["Address"], "Adjusted price", "", "", "", "", r["AdjustedPrice"]])
    if a.json_out:
        Path(a.json_out).write_text(json.dumps({"as_of": str(ASOF), "subject": {k: (str(v) if isinstance(v, date) else v) for k, v in subj.items()},
                                                "comps": results, "summary": summary,
                                                "dropped": [{"ListingId": d[0], "line": d[1], "reason": d[2]} for d in dropped],
                                                "mapping": mapping}, indent=2, default=str))


if __name__ == "__main__":
    main()
