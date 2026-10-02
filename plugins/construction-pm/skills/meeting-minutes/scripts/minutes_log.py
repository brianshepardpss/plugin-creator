#!/usr/bin/env python3
"""Carry-forward action item log for recurring meetings. Standard library only.

Item numbers are MEETING.SEQ (7.01 = meeting 7, item 1). Old business keeps
its original number until closed; new items get the current meeting number.

Usage:
  python3 minutes_log.py carry --log actions.csv --as-of YYYY-MM-DD
      Lists open items (old business) with days overdue as of the meeting date.
  python3 minutes_log.py apply --log actions.csv --meeting 7 --date YYYY-MM-DD --ops ops.json
      Applies changes decided in the meeting, writes the log, prints the
      minutes tables. ops.json is a list of objects:
        {"op": "close",  "item": "6.02", "note": "Keying conference set Oct 14"}
        {"op": "update", "item": "5.03", "due": "2026-10-09", "note": "..."}
        {"op": "add", "desc": "...", "owner": "Architect", "due": "2026-10-09", "note": ""}
      A closed item's Closed Date is the meeting date.

Days overdue = as-of (meeting) date - due date, calendar days, open items only.
"""
import argparse
import csv
import datetime as dt
import json
import re
import sys
from pathlib import Path

COLS = ["Item", "Opened Meeting", "Opened Date", "Description", "Owner", "Due", "Status", "Closed Date", "Notes"]


def parse_date(s):
    s = (s or "").strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def safe(v):
    v = "" if v is None else str(v)
    return "'" + v if v[:1] in ("=", "+", "@") else v


def load(path):
    if not Path(path).exists():
        return []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return [r for r in csv.DictReader(fh) if any((v or "").strip() for v in r.values())]


def save(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: safe(r.get(k, "")) for k in COLS})


def is_open(r):
    return not (r.get("Status") or "").lower().startswith("closed")


def overdue(r, as_of):
    d = parse_date(r.get("Due"))
    if is_open(r) and d and as_of > d:
        return f"{(as_of - d).days}d overdue"
    return ""


def table(rows, as_of, title):
    print(f"\n{title}\n")
    print("| Item | Description | Owner | Due | Status | Notes |")
    print("|---|---|---|---|---|---|")
    for r in rows:
        st = r.get("Status", "")
        od = overdue(r, as_of)
        print(f"| {r['Item']} | {r['Description']} | {r['Owner']} | {r.get('Due') or '-'} | "
              f"{st}{' (' + od + ')' if od else ''} | {r.get('Notes', '')} |")
    if not rows:
        print("| - | none | | | | |")


def carry(a):
    rows = load(a.log)
    as_of = parse_date(a.as_of)
    table([r for r in rows if is_open(r)], as_of, f"Open items carried forward as of {as_of}")


def apply(a):
    rows = load(a.log)
    date = parse_date(a.date)
    if not date:
        sys.exit("--date must be YYYY-MM-DD")
    ops = json.load(open(a.ops))
    by = {r["Item"]: r for r in rows}
    touched, prior_open = [], [r["Item"] for r in rows if is_open(r)]
    seq = max([int(r["Item"].split(".")[1]) for r in rows
               if r["Item"].split(".")[0] == str(a.meeting) and re.match(r"^\d+\.\d+$", r["Item"])] + [0])
    for op in ops:
        kind = op.get("op")
        if kind in ("close", "update"):
            r = by.get(op["item"])
            if not r:
                sys.exit(f"item {op['item']} not in log")
            if kind == "close":
                r["Status"], r["Closed Date"] = "Closed", date.isoformat()
            if op.get("due") and op["due"] != r.get("Due") and r.get("Due"):
                op["note"] = (op.get("note", "") + f" (due moved from {r['Due']})").strip()
            for k in ("due", "owner", "desc"):
                if op.get(k):
                    r[{"due": "Due", "owner": "Owner", "desc": "Description"}[k]] = op[k]
            if op.get("note"):
                r["Notes"] = (r.get("Notes", "") + "; " if r.get("Notes") else "") + f"M{a.meeting}: {op['note']}"
            touched.append(r["Item"])
        elif kind == "add":
            seq += 1
            r = {"Item": f"{a.meeting}.{seq:02d}", "Opened Meeting": str(a.meeting), "Opened Date": date.isoformat(),
                 "Description": op["desc"], "Owner": op.get("owner", "TBD"), "Due": op.get("due", ""),
                 "Status": "Open", "Closed Date": "", "Notes": op.get("note", "")}
            rows.append(r)
            by[r["Item"]] = r
        else:
            sys.exit(f"unknown op {kind!r}")
    save(a.log, rows)
    old = [by[i] for i in prior_open]
    new = [r for r in rows if r.get("Opened Meeting") == str(a.meeting)]
    table(old, date, "OLD BUSINESS (items keep their original numbers)")
    table(new, date, "NEW BUSINESS")
    silent = [i for i in prior_open if i not in touched]
    if silent:
        print(f"\nNot discussed, carried unchanged: {', '.join(silent)}")
    print(f"\nLog written to {a.log}: {sum(is_open(r) for r in rows)} open, "
          f"{sum(not is_open(r) for r in rows)} closed.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    c = sp.add_parser("carry")
    c.add_argument("--log", required=True)
    c.add_argument("--as-of", required=True)
    p = sp.add_parser("apply")
    p.add_argument("--log", required=True)
    p.add_argument("--meeting", type=int, required=True)
    p.add_argument("--date", required=True)
    p.add_argument("--ops", required=True)
    a = ap.parse_args()
    (carry if a.cmd == "carry" else apply)(a)


if __name__ == "__main__":
    main()
