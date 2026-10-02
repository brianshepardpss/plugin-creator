#!/usr/bin/env python3
"""Segment a donor/gift CSV export and mail-merge thank-you letters, locally.

Privacy design: this script reads names and emails so Claude does not have
to. `segment` prints only counts and totals (no names, no emails). `merge`
fills letter templates on disk and prints only counts. Nothing is sent
anywhere; there is no network code in this file.

Usage:
  python3 donors.py segment donors.csv [--as-of 2026-12-31] [--major 1000] [--out grants/donors]
  python3 donors.py merge grants/donors/segments.csv --templates <dir> [--out grants/donors/letters]

Input: one row per gift (CRM export). Columns matched loosely: donor id,
first name, last name, email, gift date, gift amount, recurring, fund.
Blank rows and exact duplicate rows are dropped and counted.

Segments (first match wins), using gifts on or before --as-of:
  monthly      recurring flag is Y/yes/true/monthly on any gift this year
  major        total given this calendar year >= --major (default $1,000)
  first_time   gave this year and never before
  repeat       gave this year and in an earlier year
  lapsed       no gift this year; last gift in the previous calendar year
  lapsed_long  no gift this year or last year
"This year" = the calendar year of --as-of (default: today).

Merge placeholders: {first_name} {last_name} {year} {total_this_year}
{gift_count} {last_gift_amount} {last_gift_date} {fund} {receipt_line}
{receipt_line} holds the IRS written-acknowledgment sentence when any single
gift this year was $250 or more (IRS Publication 1771), otherwise it is empty.
"""
import argparse
import csv
import datetime as dt
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path

RECEIPT = ("No goods or services were provided in exchange for your contribution(s). "
           "Please keep this letter for your tax records.")
SEGMENTS = ["monthly", "major", "first_time", "repeat", "lapsed", "lapsed_long"]


def col(headers, *names, avoid=("gift", "date", "amount")):
    for n in names:
        for h in headers:
            hl = h.lower()
            if n in hl and not (n in ("first", "last") and any(x in hl for x in avoid)):
                return h
    return None


def money(s):
    s = (s or "").strip()
    neg = s.startswith("(") and s.endswith(")") or s.startswith("-")
    s = re.sub(r"[^\d.]", "", s)
    try:
        v = float(s)
    except ValueError:
        return None
    return -v if neg else v


def date(s):
    s = (s or "").strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d-%b-%Y", "%b %d, %Y"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def segment(a):
    as_of = dt.date.fromisoformat(a.as_of) if a.as_of else dt.date.today()
    year = as_of.year
    with open(a.csv, newline="", encoding="utf-8-sig") as f:
        raw = list(csv.reader(f))
    if not raw:
        sys.exit("ERROR: empty CSV")
    H = [h.strip() for h in raw[0]]
    c = {
        "id": col(H, "donor id", "constituent id", "account id", "id"),
        "first": col(H, "first name", "firstname", "first"),
        "last": col(H, "last name", "lastname", "surname", "last"), "email": col(H, "email"),
        "date": col(H, "gift date", "date"), "amt": col(H, "gift amount", "amount"),
        "rec": col(H, "recurring", "monthly", "sustainer"), "fund": col(H, "fund", "designation"),
    }
    missing = [k for k in ("date", "amt") if not c[k]]
    if missing or not (c["id"] or c["email"]):
        sys.exit(f"ERROR: need a donor id or email, a gift date and an amount column; found {H}")
    seen, blanks, dups, bad, future, refunds = set(), 0, 0, 0, 0, 0
    donors = OrderedDict()
    for row in raw[1:]:
        if not any(x.strip() for x in row):
            blanks += 1
            continue
        key = tuple(x.strip() for x in row)
        if key in seen:
            dups += 1
            continue
        seen.add(key)
        r = dict(zip(H, row))
        d, amt = date(r.get(c["date"])), money(r.get(c["amt"]))
        if d is None or amt is None:
            bad += 1
            continue
        if amt < 0:
            refunds += 1
        if d > as_of:
            future += 1
            continue
        did = (r.get(c["id"]) or "").strip() or (r.get(c["email"]) or "").strip().lower()
        p = donors.setdefault(did, {"donor_id": did, "first_name": "", "last_name": "", "email": "",
                                    "gifts": [], "recurring": False, "fund": ""})
        for k, ck in (("first_name", "first"), ("last_name", "last"), ("email", "email")):
            if c[ck] and r.get(c[ck], "").strip():
                p[k] = r[c[ck]].strip()
        rec = (r.get(c["rec"]) or "").strip().lower() if c["rec"] else ""
        if rec in ("y", "yes", "true", "1", "monthly", "recurring") and d.year == year:
            p["recurring"] = True
        p["gifts"].append((d, amt, (r.get(c["fund"]) or "").strip() if c["fund"] else ""))

    out_rows = []
    for p in donors.values():
        g = sorted(p["gifts"])
        this = [x for x in g if x[0].year == year]
        earlier = [x for x in g if x[0].year < year]
        tot = sum(x[1] for x in this)
        if this and p["recurring"]:
            seg = "monthly"
        elif tot >= a.major:
            seg = "major"
        elif this and not earlier:
            seg = "first_time"
        elif this:
            seg = "repeat"
        elif g[-1][0].year == year - 1:
            seg = "lapsed"
        else:
            seg = "lapsed_long"
        last = g[-1]
        funds = Counter(x[2] for x in this if x[2]) or Counter(x[2] for x in g if x[2])
        out_rows.append({
            "donor_id": p["donor_id"], "first_name": p["first_name"], "last_name": p["last_name"],
            "email": p["email"], "segment": seg, "year": year,
            "gift_count": len(this), "total_this_year": f"{tot:.2f}",
            "last_gift_amount": f"{last[1]:.2f}", "last_gift_date": last[0].isoformat(),
            "first_gift_date": g[0][0].isoformat(), "lifetime_total": f"{sum(x[1] for x in g):.2f}",
            "max_single_gift_this_year": f"{max([x[1] for x in this] or [0]):.2f}",
            "fund": funds.most_common(1)[0][0] if funds else "",
        })
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    seg_path = out / "segments.csv"
    with seg_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)

    print(f"# Donor segments as of {as_of} (calendar year {year}; major = ${a.major:,.0f}+ this year)")
    print(f"Input rows: {len(raw) - 1} | blank dropped: {blanks} | exact duplicates dropped: {dups} | "
          f"unreadable date/amount: {bad} | after as-of date: {future}")
    print(f"Donors: {len(out_rows)}\n")
    earliest = min((r["first_gift_date"] for r in out_rows), default="")
    if earliest and earliest[:4] == str(year):
        print(f"WARNING: the export starts in {year}, so everyone looks first_time or monthly. "
              "Export at least two years of gifts for repeat/lapsed segments.\n")
    if refunds:
        print(f"Note: {refunds} negative amounts (refunds/reversals) were netted into totals.\n")
    print("| Segment | Donors | Given this year | Letter |\n|---|---|---|---|")
    letter = {"monthly": "thank-you", "major": "thank-you", "first_time": "thank-you + welcome",
              "repeat": "thank-you", "lapsed": "we miss you (no thank-you)", "lapsed_long": "skip by default"}
    for s in SEGMENTS:
        rs = [r for r in out_rows if r["segment"] == s]
        tot = sum(float(r["total_this_year"]) for r in rs)
        print(f"| {s} | {len(rs)} | ${tot:,.2f} | {letter[s]} |")
    alltot = sum(float(r["total_this_year"]) for r in out_rows)
    receipts = sum(1 for r in out_rows if float(r["max_single_gift_this_year"]) >= 250)
    lapsed_big = sum(1 for r in out_rows if r["segment"].startswith("lapsed") and float(r["lifetime_total"]) >= a.major)
    print(f"| total | {len(out_rows)} | ${alltot:,.2f} | |")
    print(f"\n- Donors needing the IRS written acknowledgment (a single gift of $250+ this year): {receipts}")
    if lapsed_big:
        print(f"- Lapsed donors with lifetime giving >= ${a.major:,.0f}: {lapsed_big} (consider a personal call)")
    print(f"- Per-donor detail (names, emails) written locally to {seg_path}; not printed here.")


def merge(a):
    with open(a.segments, newline="") as f:
        rows = list(csv.DictReader(f))
    tdir = Path(a.templates)
    templates = {}
    for s in SEGMENTS:
        for ext in (".md", ".txt"):
            p = tdir / f"{s}{ext}"
            if p.exists():
                templates[s] = p.read_text()
    if not templates:
        sys.exit(f"ERROR: no templates in {tdir} (expected files like monthly.md, first_time.md)")
    allowed = {"first_name", "last_name", "year", "total_this_year", "gift_count",
               "last_gift_amount", "last_gift_date", "fund", "receipt_line"}
    for s, t in templates.items():
        todo = re.findall(r"<[A-Z][A-Z0-9 ,.'()/:-]{3,}>", t)
        if todo:
            sys.exit(f"ERROR: template {s} still has fill-in markers {todo[:3]}; adapt it to the org first")
        unknown = set(re.findall(r"\{(\w+)\}", t)) - allowed
        if unknown:
            sys.exit(f"ERROR: template {s} uses unknown placeholder(s) {sorted(unknown)}; allowed {sorted(allowed)}")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    counts, skipped, combined = Counter(), Counter(), []
    for r in rows:
        t = templates.get(r["segment"])
        if not t:
            skipped[r["segment"]] += 1
            continue
        vals = {
            "first_name": r["first_name"] or "Friend", "last_name": r["last_name"], "year": r["year"],
            "total_this_year": f"${float(r['total_this_year']):,.2f}", "gift_count": r["gift_count"],
            "last_gift_amount": f"${float(r['last_gift_amount']):,.2f}",
            "last_gift_date": dt.date.fromisoformat(r["last_gift_date"]).strftime("%B %d, %Y").replace(" 0", " "),
            "fund": r["fund"] or "our programs",
            "receipt_line": RECEIPT if float(r["max_single_gift_this_year"]) >= 250 else "",
        }
        text = t.format(**vals).rstrip() + "\n"
        (out / f"{r['donor_id']}-{r['segment']}.txt").write_text(text)
        combined.append(f"---\n<!-- {r['donor_id']} ({r['segment']}) -->\n{text}")
        counts[r["segment"]] += 1
    (out / "all-letters.md").write_text("\n".join(combined))
    print(f"# Letters written to {out}/ (one file per donor, plus all-letters.md)")
    for s in SEGMENTS:
        if counts[s] or skipped[s]:
            print(f"- {s}: {counts[s]} written" + (f", {skipped[s]} skipped (no template)" if skipped[s] else ""))
    print("Names and amounts were merged on this machine; review a few letters before sending.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("segment")
    s.add_argument("csv")
    s.add_argument("--as-of")
    s.add_argument("--major", type=float, default=1000)
    s.add_argument("--out", default="grants/donors")
    m = sub.add_parser("merge")
    m.add_argument("segments")
    m.add_argument("--templates", required=True)
    m.add_argument("--out", default="grants/donors/letters")
    a = ap.parse_args()
    segment(a) if a.cmd == "segment" else merge(a)


if __name__ == "__main__":
    main()
