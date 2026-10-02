#!/usr/bin/env python3
"""Look up nonprofits and foundations in the ProPublica Nonprofit Explorer API.

Standard library only. No API key. Every result prints its source URLs.

Usage:
  python3 propublica.py search "literacy" [--state TX] [--ntee 2] [--page 0]
  python3 propublica.py org 74-2479712 [--years 5] [--json]

Data modes (all subcommands):
  --mode auto     live request, fall back to samples/cache if offline (default)
  --mode live     live only
  --mode offline  samples/cache only (the bundled demo works with no network)
  --save-cache    also write the live response into samples/cache (maintainers)

Formulas (org):
  grants paid           = contrpdpbks (990-PF "contributions, gifts, grants paid", books)
  payout % of assets    = grants paid / fair market value of assets at year end * 100
  year-over-year change = (grants paid this year - prior year) / prior year * 100

Data is what the IRS released from e-filed returns. It lags 1-2 years; the
tax year is printed on every row. Source: ProPublica Nonprofit Explorer
(attribution required by its terms of use). Not affiliated with ProPublica.
"""
import argparse
import datetime as dt
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://projects.propublica.org/nonprofits/api/v2"
PAGE = "https://projects.propublica.org/nonprofits/organizations/{ein}"
CACHE = Path(__file__).resolve().parent.parent / "samples" / "cache"
UA = "grant-desk/0.1 (+https://github.com/brianshepardpss/grant-desk)"

FORMTYPE = {0: "990", 1: "990-EZ", 2: "990-PF"}
FOUNDATION_CODE = {
    2: "private operating foundation (excise tax)",
    3: "private operating foundation (other)",
    4: "private non-operating foundation (typical grantmaker)",
    10: "church", 11: "school", 12: "hospital or medical research",
    13: "university or government unit support",
    14: "federal/state/local government unit", 15: "publicly supported (gifts/grants)",
    16: "publicly supported (gross receipts)", 17: "supporting organization",
    21: "supporting organization (Type I)", 22: "supporting organization (Type II)",
    23: "supporting organization (Type III functionally integrated)",
    24: "supporting organization (Type III other)",
}


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
    """Return (bytes, provenance string)."""
    cached = CACHE / cache_name
    if mode != "offline":
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read()
            if save:
                CACHE.mkdir(parents=True, exist_ok=True)
                cached.write_bytes(body.lstrip(b"\xef\xbb\xbf"))
                cache_note(cache_name, url)
            return body, "live, fetched " + dt.datetime.now().strftime("%Y-%m-%d %H:%M")
        except Exception as e:  # network blocked, 404, timeout
            if mode == "live" or not cached.exists():
                sys.exit(f"ERROR fetching {url}: {e}\n"
                         "If you are offline, try --mode offline (bundled samples only), "
                         "or paste the funder's 990 PDF instead.")
            print(f"NOTE: live request failed ({e}); using cached sample.", file=sys.stderr)
    if not cached.exists():
        sys.exit(f"ERROR: no cached sample for this request ({cache_name}). "
                 "Offline mode only covers the bundled demo EINs and searches.")
    when = cache_note(cache_name)
    return cached.read_bytes(), f"CACHED SAMPLE (saved {when}; may be out of date)"


def norm_ein(s):
    d = "".join(c for c in s if c.isdigit())
    if len(d) != 9:
        sys.exit(f"ERROR: EIN must have 9 digits, got {s!r}")
    return d


def money(v):
    return "n/a" if v is None else f"${v:,.0f}"


def cmd_search(a):
    params = {"q": a.query, "page": a.page}
    if a.state:
        params["state[id]"] = a.state.upper()
    if a.ntee:
        params["ntee[id]"] = a.ntee
    url = f"{API}/search.json?" + urllib.parse.urlencode(params)
    key = "propublica_search_" + "_".join(
        "".join(c if c.isalnum() else "-" for c in str(v).lower()) for v in params.values()) + ".json"
    body, prov = fetch(url, key, a.mode, a.save_cache)
    d = json.loads(body)
    if a.json:
        print(json.dumps(d, indent=2))
        return
    print(f"# ProPublica search: {a.query!r}  ({d.get('total_results', 0)} results, "
          f"page {d.get('cur_page', 0) + 1} of {d.get('num_pages', 1)})")
    print(f"Source: {url}\nData: {prov}\n")
    print("| EIN | Name | City | State | NTEE | Profile |")
    print("|-----|------|------|-------|------|---------|")
    for o in d.get("organizations", []):
        print(f"| {o.get('strein')} | {o.get('name')} | {o.get('city')} | {o.get('state')} | "
              f"{o.get('ntee_code') or ''} | {PAGE.format(ein=o.get('ein'))} |")
    print("\nNext: `propublica.py org <EIN>` for financials, `grantees.py <EIN>` for who it funds.")


def cmd_org(a):
    ein = norm_ein(a.ein)
    url = f"{API}/organizations/{ein}.json"
    body, prov = fetch(url, f"propublica_org_{ein}.json", a.mode, a.save_cache)
    d = json.loads(body)
    o = d["organization"]
    filings = sorted(d.get("filings_with_data", []), key=lambda f: f.get("tax_prd", 0), reverse=True)
    rows = []
    for f in filings[: a.years]:
        pf = f.get("formtype") == 2
        assets = f.get("fairmrktvaleoy") if pf and f.get("fairmrktvaleoy") else f.get("totassetsend")
        grants = f.get("contrpdpbks") if pf else None
        rows.append({
            "tax_year": f.get("tax_prd_yr") or str(f.get("tax_prd"))[:4],
            "tax_period": f.get("tax_prd"),
            "form": FORMTYPE.get(f.get("formtype"), str(f.get("formtype"))),
            "revenue": f.get("totrevenue"),
            "assets_eoy": assets,
            "grants_paid": grants,
            "total_expenses": f.get("totfuncexpns") or f.get("totexpnspbks"),
            "officer_comp": f.get("compnsatncurrofcr") or f.get("compofficers"),
            "payout_pct_of_assets": round(grants / assets * 100, 2) if grants and assets else None,
            "pdf_url": f.get("pdf_url"),
        })
    for i, r in enumerate(rows[:-1]):
        prev = rows[i + 1]["grants_paid"]
        r["grants_yoy_pct"] = (round((r["grants_paid"] - prev) / prev * 100, 1)
                               if r["grants_paid"] is not None and prev else None)
    oid = o.get("latest_object_id")
    out = {
        "ein": ein, "name": o.get("name"), "city": o.get("city"), "state": o.get("state"),
        "ntee_code": o.get("ntee_code"), "ruling_date": o.get("ruling_date"),
        "foundation_code": o.get("foundation_code"),
        "foundation_type": FOUNDATION_CODE.get(o.get("foundation_code"), "unknown"),
        "is_private_grantmaker": o.get("foundation_code") == 4,
        "latest_object_id": oid,
        "latest_xml_url": (f"https://gt990datalake-rawdata.s3.amazonaws.com/EfileData/XmlFiles/{oid}_public.xml"
                           if oid else None),
        "filings": rows,
        "sources": [PAGE.format(ein=ein), url],
        "data": prov,
    }
    if a.json:
        print(json.dumps(out, indent=2))
        return
    print(f"# {out['name']} (EIN {ein[:2]}-{ein[2:]})")
    print(f"{out['city']}, {out['state']} | NTEE {out['ntee_code'] or 'n/a'} | "
          f"ruling {out['ruling_date']} | {out['foundation_type']}")
    print(f"Sources: {out['sources'][0]} ; {out['sources'][1]}\nData: {prov}\n")
    print("| Tax year | Form | Revenue | Assets (EOY) | Grants paid | YoY grants | Payout % of assets | Filing PDF |")
    print("|----------|------|---------|--------------|-------------|------------|--------------------|------------|")
    for r in rows:
        yoy = r.get("grants_yoy_pct")
        print(f"| {r['tax_year']} | {r['form']} | {money(r['revenue'])} | {money(r['assets_eoy'])} | "
              f"{money(r['grants_paid'])} | {'' if yoy is None else f'{yoy:+.1f}%'} | "
              f"{'' if r['payout_pct_of_assets'] is None else str(r['payout_pct_of_assets']) + '%'} | "
              f"{r['pdf_url'] or 'n/a'} |")
    if not rows:
        print("(no extracted filings; small 990-N filers are not covered)")
    if oid:
        print(f"\nLatest e-filed return XML (may be newer than the table): {out['latest_xml_url']}")
        print("Run `grantees.py " + ein + "` to list who it funded in that return.")
    print("\nIRS data lags 1-2 years. Source: ProPublica Nonprofit Explorer.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mode", choices=["auto", "live", "offline"], default="auto")
    ap.add_argument("--save-cache", action="store_true")
    ap.add_argument("--json", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("--state")
    s.add_argument("--ntee", help="NTEE major group 1-10 (2 = education, 5 = human services)")
    s.add_argument("--page", type=int, default=0)
    o = sub.add_parser("org")
    o.add_argument("ein")
    o.add_argument("--years", type=int, default=5)
    for p in (s, o):
        p.add_argument("--mode", choices=["auto", "live", "offline"], default=argparse.SUPPRESS)
        p.add_argument("--save-cache", action="store_true", default=argparse.SUPPRESS)
        p.add_argument("--json", action="store_true", default=argparse.SUPPRESS)
    a = ap.parse_args()
    {"search": cmd_search, "org": cmd_org}[a.cmd](a)


if __name__ == "__main__":
    main()
