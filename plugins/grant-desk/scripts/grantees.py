#!/usr/bin/env python3
"""Who does this foundation actually fund? Parse the grantee list from its
latest e-filed 990-PF (Part XV) or 990 (Schedule I) XML.

Standard library only. No API key. Sources:
  - ProPublica Nonprofit Explorer API: finds the latest e-file object id
  - GivingTuesday 990 Data Lake (public S3): the IRS e-file XML itself

Usage:
  python3 grantees.py 74-2479712 [--state TX] [--city Waco] \
      [--keyword literacy,reading,library] [--cap 25000] [--top 15] \
      [--object-id 202611359349102136] [--csv grants.csv] [--json]
  Data modes: --mode auto|live|offline, --save-cache (see propublica.py)

Formulas:
  median, p25, p75   = statistics.quantiles(amounts, n=4, method="inclusive")
  comparables        = grants in --state whose city equals --city OR whose
                       purpose/name contains a --keyword; if fewer than 3,
                       widen to all grants in --state; if still fewer than 3,
                       use every grant in the return.
  suggested ask      = median of comparables, rounded to the nearest $1,000
  ask range          = p25 to p75 of comparables, rounded to nearest $1,000
  If --cap is given, the ask and range are clipped to the cap.

The ask is a starting point from one year of public data, not advice; the
funder's guidelines and a conversation with program staff come first.
Not affiliated with ProPublica, GivingTuesday or the IRS.
"""
import argparse
import csv
import datetime as dt
import json
import statistics
import sys
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

API = "https://projects.propublica.org/nonprofits/api/v2/organizations/{ein}.json"
PAGE = "https://projects.propublica.org/nonprofits/organizations/{ein}"
XML = "https://gt990datalake-rawdata.s3.amazonaws.com/EfileData/XmlFiles/{oid}_public.xml"
CACHE = Path(__file__).resolve().parent.parent / "samples" / "cache"
UA = "grant-desk/0.1 (+https://github.com/brianshepardpss/grant-desk)"
NS = "{http://www.irs.gov/efile}"


def cache_note(name, url=None):
    """Read (or with url, record) when a cached sample was fetched, in cache/MANIFEST.json."""
    mf = CACHE / "MANIFEST.json"
    try:
        m = json.loads(mf.read_text())
    except (OSError, ValueError):
        m = {}
    if url:
        m[name] = {"url": url, "fetched": dt.date.today().isoformat()}
        mf.write_text(json.dumps(m, indent=1, sort_keys=True) + "\n")
    return m.get(name, {}).get("fetched", "unknown date")


def fetch(url, cache_name, mode, save):
    cached = CACHE / cache_name
    if mode != "offline":
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read()
            if save:
                CACHE.mkdir(parents=True, exist_ok=True)
                cached.write_bytes(body.lstrip(b"\xef\xbb\xbf"))
                cache_note(cache_name, url)
            return body, "live, fetched " + dt.datetime.now().strftime("%Y-%m-%d %H:%M")
        except Exception as e:
            if mode == "live" or not cached.exists():
                sys.exit(f"ERROR fetching {url}: {e}\n"
                         "Offline? Use --mode offline for the bundled demo EINs, or ask the "
                         "user to upload the funder's 990-PF PDF and read Part XV by hand.")
            print(f"NOTE: live request failed ({e}); using cached sample.", file=sys.stderr)
    if not cached.exists():
        sys.exit(f"ERROR: no cached sample for {cache_name}. Offline mode only covers the demo EINs.")
    when = cache_note(cache_name)
    return cached.read_bytes(), f"CACHED SAMPLE (saved {when}; may be out of date)"


def txt(el, path):
    x = el.find(path)
    return (x.text or "").strip() if x is not None and x.text else ""


def name_of(el):
    for p in (f".//{NS}BusinessNameLine1Txt", f".//{NS}BusinessNameLine1", f"{NS}RecipientPersonNm"):
        v = txt(el, p)
        if v:
            return v
    return "(name not given)"


def parse(xml_bytes):
    root = ET.fromstring(xml_bytes)
    rtype = txt(root, f".//{NS}ReturnTypeCd")
    period = txt(root, f".//{NS}TaxPeriodEndDt")
    filer = txt(root, f".//{NS}Filer/{NS}BusinessName/{NS}BusinessNameLine1Txt")
    grants = []
    # 990-PF Part XV: grants paid during the year
    for g in root.iter(f"{NS}GrantOrContributionPdDurYrGrp"):
        grants.append({
            "recipient": name_of(g),
            "city": txt(g, f".//{NS}CityNm") or txt(g, f".//{NS}CityTxt"),
            "state": txt(g, f".//{NS}StateAbbreviationCd") or txt(g, f".//{NS}CountryCd"),
            "status": txt(g, f"{NS}RecipientFoundationStatusTxt"),
            "purpose": txt(g, f"{NS}GrantOrContributionPurposeTxt"),
            "amount": float(txt(g, f"{NS}Amt") or 0),
        })
    # 990 Schedule I: grants to domestic organizations
    for g in root.iter(f"{NS}RecipientTable"):
        grants.append({
            "recipient": name_of(g),
            "city": txt(g, f".//{NS}CityNm"),
            "state": txt(g, f".//{NS}StateAbbreviationCd"),
            "status": txt(g, f"{NS}IRCSectionDesc"),
            "purpose": txt(g, f"{NS}PurposeOfGrantTxt"),
            "amount": float(txt(g, f"{NS}CashGrantAmt") or 0) + float(txt(g, f"{NS}NonCashAssistanceAmt") or 0),
        })
    info = {
        "return_type": rtype, "tax_period_end": period, "filer": filer,
        "reported_total_paid": txt(root, f".//{NS}TotalGrantOrContriPdDurYrAmt"),
        "approved_future_total": txt(root, f".//{NS}TotalGrantOrContriApprvFutAmt"),
        "preselected_only": txt(root, f".//{NS}OnlyContriToPreselectedInd"),
        "how_to_apply": {},
    }
    app = root.find(f".//{NS}ApplicationSubmissionInfoGrp")
    if app is not None:
        info["how_to_apply"] = {
            "contact": txt(app, f"{NS}RecipientPersonNm"),
            "materials": txt(app, f"{NS}FormAndInfoAndMaterialsTxt"),
            "deadlines": txt(app, f"{NS}SubmissionDeadlinesTxt"),
            "restrictions": txt(app, f"{NS}RestrictionsOnAwardsTxt"),
        }
    return info, grants


def quart(vals):
    if len(vals) == 1:
        return vals[0], vals[0], vals[0]
    q = statistics.quantiles(vals, n=4, method="inclusive")
    return q[0], q[1], q[2]


def r1k(x):
    return int(x / 1000.0 + 0.5) * 1000  # halves round up ($24,500 -> $25,000)


def money(v):
    return f"${v:,.0f}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ein")
    ap.add_argument("--object-id", help="specific e-file object id (default: latest)")
    ap.add_argument("--state", help="your state, e.g. TX")
    ap.add_argument("--city", help="your city, e.g. Waco")
    ap.add_argument("--keyword", default="", help="comma list matched against purpose and recipient name")
    ap.add_argument("--cap", type=float, help="the RFP's maximum request")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--csv", help="write every grant to this CSV")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--mode", choices=["auto", "live", "offline"], default="auto")
    ap.add_argument("--save-cache", action="store_true")
    a = ap.parse_args()

    ein = "".join(c for c in a.ein if c.isdigit())
    if len(ein) != 9:
        sys.exit(f"ERROR: EIN must have 9 digits, got {a.ein!r}")
    org_url = API.format(ein=ein)
    oid = a.object_id
    org_name = None
    if not oid:
        body, _ = fetch(org_url, f"propublica_org_{ein}.json", a.mode, a.save_cache)
        org = json.loads(body)["organization"]
        oid, org_name = org.get("latest_object_id"), org.get("name")
        if not oid:
            sys.exit("ERROR: ProPublica lists no e-filed return for this EIN. Paper filers and "
                     "990-N filers are not covered; read the PDF on the ProPublica page instead: "
                     + PAGE.format(ein=ein))
    xml_url = XML.format(oid=oid)
    body, prov = fetch(xml_url, f"gt990_{oid}.xml", a.mode, a.save_cache)
    info, grants = parse(body)

    kws = [k.strip().lower() for k in a.keyword.split(",") if k.strip()]
    st = (a.state or "").upper()
    city = (a.city or "").lower()
    for g in grants:
        g["in_state"] = bool(st) and g["state"].upper() == st
        g["in_city"] = g["in_state"] and bool(city) and g["city"].lower() == city
        hay = (g["purpose"] + " " + g["recipient"]).lower()
        g["keyword_hit"] = [k for k in kws if k in hay]

    amounts = sorted(g["amount"] for g in grants if g["amount"] > 0)
    out = {
        "funder": info["filer"] or org_name, "ein": ein, "object_id": oid,
        "return_type": info["return_type"], "tax_period_end": info["tax_period_end"],
        "data": prov, "sources": [xml_url, PAGE.format(ein=ein), org_url],
        "grant_count": len(amounts), "total": sum(amounts),
        "reported_total_paid": info["reported_total_paid"],
        "approved_future_total": info["approved_future_total"],
        "accepts_unsolicited": info["preselected_only"].lower() not in ("x", "1", "true"),
        "how_to_apply": info["how_to_apply"],
    }
    if amounts:
        p25, med, p75 = quart(amounts)
        out.update({"min": amounts[0], "p25": p25, "median": med, "p75": p75, "max": amounts[-1]})
    states = Counter(g["state"] or "?" for g in grants)
    cities = Counter(f"{g['city']}, {g['state']}" for g in grants)
    out["by_state"] = states.most_common(10)
    out["by_city"] = cities.most_common(10)

    tiers = [("your city or keyword match in " + st,
              [g for g in grants if g["in_state"] and (g["in_city"] or g["keyword_hit"])]),
             ("all grants in " + st, [g for g in grants if g["in_state"]]),
             ("all grants in this return", grants)]
    if not st:
        tiers = [("keyword match", [g for g in grants if g["keyword_hit"]]), tiers[2]]
    basis, comps = tiers[-1]
    for label, gs in tiers:
        if len([g for g in gs if g["amount"] > 0]) >= 3:
            basis, comps = label, gs
            break
    camts = sorted(g["amount"] for g in comps if g["amount"] > 0)
    if camts:
        c25, cmed, c75 = quart(camts)
        ask, lo, hi = r1k(cmed), r1k(c25), r1k(c75)
        if a.cap:
            ask, lo, hi = min(ask, a.cap), min(lo, a.cap), min(hi, a.cap)
        out["ask"] = {"basis": basis, "n": len(camts), "median": cmed, "p25": c25, "p75": c75,
                      "suggested": ask, "range": [lo, hi], "cap": a.cap}
    near = [g for g in grants if g["in_city"]] if city else []
    kw = [g for g in grants if g["keyword_hit"]]
    out["near_you"] = sorted(near, key=lambda g: -g["amount"])
    out["keyword_matches"] = sorted(kw, key=lambda g: -g["amount"])
    out["top_grants"] = sorted(grants, key=lambda g: -g["amount"])[: a.top]

    if a.csv:
        with open(a.csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["recipient", "city", "state", "status", "purpose", "amount", "tax_period_end", "source"])
            for g in grants:
                w.writerow([g["recipient"], g["city"], g["state"], g["status"], g["purpose"],
                            int(g["amount"]), info["tax_period_end"], xml_url])
    if a.json:
        print(json.dumps(out, indent=2, default=str))
        return

    def row(g):
        tag = (" (keyword: " + ", ".join(g["keyword_hit"]) + ")") if g["keyword_hit"] else ""
        return f"| {g['recipient']} | {g['city']}, {g['state']} | {money(g['amount'])} | {g['purpose'][:90]}{tag} |"

    print(f"# Grantees of {out['funder']} (EIN {ein[:2]}-{ein[2:]})")
    print(f"Return: {info['return_type']} for tax period ending {info['tax_period_end']} "
          f"(e-file object {oid})")
    print(f"Data: {prov}")
    print("Sources: " + " ; ".join(out["sources"]) + "\n")
    if not amounts:
        print("No itemized grants found in this return (some filers attach a PDF statement instead). "
              "Check the filing PDF on the ProPublica page.")
        return
    print("## Giving in this return")
    print(f"- Grants listed: {out['grant_count']}, total {money(out['total'])}"
          + (f" (return reports {money(float(out['reported_total_paid']))} paid)" if out["reported_total_paid"] else ""))
    print(f"- Smallest {money(out['min'])} | 25th pct {money(out['p25'])} | median {money(out['median'])} "
          f"| 75th pct {money(out['p75'])} | largest {money(out['max'])}")
    if out["approved_future_total"]:
        print(f"- Approved for future payment: {money(float(out['approved_future_total']))}")
    print("- Top states: " + ", ".join(f"{s} {n}" for s, n in out["by_state"]))
    print("- Top cities: " + ", ".join(f"{c} ({n})" for c, n in out["by_city"][:6]))
    if not out["accepts_unsolicited"]:
        print("- WARNING: the return checks 'only makes contributions to preselected charitable "
              "organizations and does not accept unsolicited requests'.")
    h = out["how_to_apply"]
    if h and any(h.values()):
        print(f"- How to apply (as filed): contact {h.get('contact') or 'n/a'}; deadlines: "
              f"{h.get('deadlines') or 'n/a'}; restrictions: {h.get('restrictions') or 'n/a'}")
    if city:
        print(f"\n## Grants to organizations in {a.city}, {st}: {len(near)}"
              + (f", total {money(sum(g['amount'] for g in near))}" if near else ""))
        if near:
            print("| Recipient | City | Amount | Purpose (as filed) |\n|---|---|---|---|")
            for g in near:
                print(row(g))
    if kws:
        print(f"\n## Keyword matches ({', '.join(kws)}): {len(kw)}")
        if kw:
            print("| Recipient | City | Amount | Purpose (as filed) |\n|---|---|---|---|")
            for g in kw:
                print(row(g))
    if "ask" in out:
        k = out["ask"]
        print(f"\n## Ask sizing (basis: {k['basis']}, n={k['n']})")
        print(f"- Comparable grants: 25th pct {money(k['p25'])}, median {money(k['median'])}, "
              f"75th pct {money(k['p75'])}")
        print(f"- Suggested ask: {money(k['suggested'])} (range {money(k['range'][0])} to "
              f"{money(k['range'][1])})" + (f", clipped to the {money(a.cap)} cap" if a.cap else ""))
        print("- Formula: median of comparables rounded to $1,000; range = p25..p75. "
              "One year of data; confirm with the funder's guidelines.")
    print(f"\n## Largest {len(out['top_grants'])} grants")
    print("| Recipient | City | Amount | Purpose (as filed) |\n|---|---|---|---|")
    for g in out["top_grants"]:
        print(row(g))
    if a.csv:
        print(f"\nAll {len(grants)} grants written to {a.csv}")
    print("\nSource: IRS e-file data via the GivingTuesday 990 Data Lake and ProPublica Nonprofit Explorer.")


if __name__ == "__main__":
    main()
