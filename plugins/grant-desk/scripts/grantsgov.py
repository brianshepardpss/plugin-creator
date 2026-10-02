#!/usr/bin/env python3
"""Search open and forecasted federal grants on Grants.gov (public REST API, no key).

Usage:
  python3 grantsgov.py search "youth mentoring" [--eligibility 12] [--agency HHS] \
      [--category ED] [--status forecasted|posted] [--rows 25] [--today 2026-10-02]
  python3 grantsgov.py opportunity 363911
  Data modes: --mode auto|live|offline, --save-cache (see propublica.py)

Endpoints (verified 2026-10-02):
  POST https://api.grants.gov/v1/api/search2         {"keyword","oppStatuses","rows",...}
  POST https://api.grants.gov/v1/api/fetchOpportunity {"opportunityId": N}

Eligibility code 12 = "Nonprofits having a 501(c)(3) status with the IRS, other
than institutions of higher education". Category ED = Education, HL = Health,
ISS = Income Security and Social Services, CD = Community Development.

Formula: days_left = close date - today (calendar days). Posted opportunities
whose close date is before today are dropped. Forecasted ones have no close
date yet. Each row carries its Grants.gov detail URL.
Not affiliated with Grants.gov or any federal agency.
"""
import argparse
import datetime as dt
import html
import json
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path

BASE = "https://api.grants.gov/v1/api"
DETAIL = "https://www.grants.gov/search-results-detail/{id}"
CACHE = Path(__file__).resolve().parent.parent / "samples" / "cache"
UA = "grant-desk/0.1 (+https://github.com/brianshepardpss/grant-desk)"


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


def post(endpoint, payload, cache_name, mode, save):
    cached = CACHE / cache_name
    url = f"{BASE}/{endpoint}"
    if mode != "offline":
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST",
                                         headers={"Content-Type": "application/json", "User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read()
            if save:
                CACHE.mkdir(parents=True, exist_ok=True)
                cached.write_bytes(body.lstrip(b"\xef\xbb\xbf"))
                cache_note(cache_name, url)
            return json.loads(body), "live, fetched " + dt.datetime.now().strftime("%Y-%m-%d %H:%M")
        except Exception as e:
            if mode == "live" or not cached.exists():
                sys.exit(f"ERROR calling {url}: {e}\nOffline? Use --mode offline for the bundled "
                         "demo searches, or search https://www.grants.gov/search-grants by hand.")
            print(f"NOTE: live request failed ({e}); using cached sample.", file=sys.stderr)
    if not cached.exists():
        sys.exit(f"ERROR: no cached sample for {cache_name}. Offline mode only covers the demo searches.")
    when = cache_note(cache_name)
    return json.loads(cached.read_bytes()), f"CACHED SAMPLE (saved {when}; dates may have passed)"


def slug(*parts):
    s = "_".join(str(p) for p in parts if p)
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


ASCII = str.maketrans({"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
                       "\u2013": "-", "\u2014": "-", "\xa0": " "})


def clean(s):
    s = html.unescape(s or "").translate(ASCII)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip()


def mdy(s):
    try:
        return dt.datetime.strptime(s, "%m/%d/%Y").date()
    except (TypeError, ValueError):
        return None


def cmd_search(a):
    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    payload = {"keyword": a.keyword, "oppStatuses": a.status, "rows": a.rows}
    if a.eligibility:
        payload["eligibilities"] = a.eligibility
    if a.agency:
        payload["agencies"] = a.agency
    if a.category:
        payload["fundingCategories"] = a.category
    key = "grantsgov_search_" + slug(a.keyword, a.status.replace("|", "-"), a.eligibility,
                                     a.agency, a.category, a.rows) + ".json"
    d, prov = post("search2", payload, key, a.mode, a.save_cache)
    if d.get("errorcode"):
        sys.exit(f"Grants.gov error: {d.get('msg')}")
    data = d["data"]
    rows, dropped = [], 0
    for h in data.get("oppHits", []):
        close = mdy(h.get("closeDate"))
        if h.get("oppStatus") == "posted" and close and close < today:
            dropped += 1
            continue
        h = {**h, "title": clean(h.get("title")), "agency": clean(h.get("agency"))}
        rows.append({**h, "days_left": (close - today).days if close else None,
                     "url": DETAIL.format(id=h["id"])})
    rows.sort(key=lambda r: (r["days_left"] is None, r["days_left"] or 0))
    if a.json:
        print(json.dumps({"data": prov, "hitCount": data.get("hitCount"), "today": str(today),
                          "payload": payload, "results": rows}, indent=2))
        return
    print(f"# Grants.gov: {a.keyword!r} ({data.get('hitCount')} matches; showing {len(rows)}, "
          f"status {a.status}" + (f", eligibility {a.eligibility}" if a.eligibility else "") + ")")
    print(f"Source: POST {BASE}/search2 {json.dumps(payload)}\nData: {prov} | today = {today}\n")
    print("| Opportunity # | Title | Agency | Status | Close date | Days left | Link |")
    print("|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['number']} | {r['title']} | {r['agency'].strip()} | {r['oppStatus']} | "
              f"{r.get('closeDate') or 'not set'} | {'' if r['days_left'] is None else r['days_left']} | {r['url']} |")
    if dropped:
        print(f"\n{dropped} posted opportunities already past their close date were dropped.")
    print("\nEligibility and match rules are in each notice; run `grantsgov.py opportunity <id>` "
          "before deciding. Results are keyword matches, not a fit judgment.")


def strip_html(s):
    return clean(re.sub(r"<[^>]+>", " ", s or ""))


def cmd_opp(a):
    d, prov = post("fetchOpportunity", {"opportunityId": int(a.id)},
                   f"grantsgov_opp_{a.id}.json", a.mode, a.save_cache)
    x = d.get("data") or {}
    s = x.get("synopsis") or x.get("forecast") or {}
    out = {
        "id": a.id, "number": x.get("opportunityNumber"), "title": clean(x.get("opportunityTitle")),
        "agency": s.get("agencyName"), "posted": s.get("postingDate"),
        "close": s.get("responseDate") or s.get("estApplicationResponseDate"),
        "award_floor": s.get("awardFloor"), "award_ceiling": s.get("awardCeiling"),
        "estimated_total": s.get("estimatedFunding"), "awards": s.get("numberOfAwards"),
        "cost_sharing": s.get("costSharing"),
        "eligible": [t.get("description") for t in s.get("applicantTypes", [])],
        "eligibility_notes": strip_html(s.get("applicantEligibilityDesc")),
        "notice_url": s.get("fundingDescLinkUrl"), "contact": s.get("agencyContactEmail"),
        "cfda": [c.get("cfdaNumber") for c in x.get("cfdas", [])],
        "summary": strip_html(s.get("synopsisDesc"))[:1200],
        "url": DETAIL.format(id=a.id), "data": prov,
    }
    if a.json:
        print(json.dumps(out, indent=2))
        return
    print(f"# {out['title']}\n{out['number']} | {out['agency']} | ALN/CFDA {', '.join(c for c in out['cfda'] if c)}")
    print(f"Source: {out['url']}\nData: {prov}\n")
    for k in ("posted", "close", "award_floor", "award_ceiling", "estimated_total", "awards",
              "cost_sharing", "notice_url", "contact"):
        print(f"- {k.replace('_', ' ')}: {out[k] if out[k] not in (None, '') else 'not stated'}")
    print("- eligible applicants:")
    for e in out["eligible"]:
        print(f"  - {e}")
    if out["eligibility_notes"]:
        print(f"- eligibility notes: {out['eligibility_notes'][:600]}")
    print(f"\nSummary (first 1,200 chars): {out['summary']}")
    print("\nRead the full notice of funding opportunity before applying.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--mode", choices=["auto", "live", "offline"], default="auto")
    common.add_argument("--save-cache", action="store_true")
    common.add_argument("--json", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", parents=[common])
    s.add_argument("keyword")
    s.add_argument("--eligibility", help="e.g. 12 (501(c)(3) nonprofits); pipe-separate several")
    s.add_argument("--agency")
    s.add_argument("--category")
    s.add_argument("--status", default="forecasted|posted")
    s.add_argument("--rows", type=int, default=25)
    s.add_argument("--today")
    o = sub.add_parser("opportunity", parents=[common])
    o.add_argument("id")
    a = ap.parse_args()
    {"search": cmd_search, "opportunity": cmd_opp}[a.cmd](a)


if __name__ == "__main__":
    main()
