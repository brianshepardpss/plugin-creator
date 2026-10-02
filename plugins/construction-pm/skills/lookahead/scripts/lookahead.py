#!/usr/bin/env python3
"""Three-week look-ahead from a schedule CSV export. Standard library only.

Usage:
  python3 lookahead.py schedule.csv --as-of YYYY-MM-DD [--weeks 3] \
      [--submittals submittals.csv] [--rfis rfis.csv] [--csv lookahead.csv]

Reads P6 / MS Project / spreadsheet exports with columns like Activity ID,
Activity Name, Start, Finish, Spec Section, Responsible. Dates such as
05-Oct-26, 10/5/2026 or 2026-10-05; a trailing " A" marks an actual date.

Window: week 1 starts on the Monday on or before --as-of; the window runs
weeks x 7 days. An activity is shown if its start-finish range overlaps the
window and its finish is not an actual (completed) date.
Constraints for each activity, by Spec Section match:
  * submittals in the register for that section whose Status does not
    contain "approved" (closeout items are ignored)
  * open RFIs whose Spec Ref mentions that section number
Also lists register rows whose Submit By falls on or before the window end
and whose Status is not yet submitted (procurement watch).
"""
import argparse
import csv
import datetime as dt
import re


def parse_date(s):
    s = (s or "").strip().rstrip("*").strip()
    actual = bool(re.search(r"\sA$", s))
    s = re.sub(r"\s+A$", "", s)
    s = re.sub(r"^[A-Za-z]{3}\s+(?=\d)", "", s)
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d-%b-%y", "%d-%b-%Y"):
        try:
            return dt.datetime.strptime(s, fmt).date(), actual
        except ValueError:
            pass
    return None, actual


def norm(s):
    d = re.sub(r"\D", "", s or "")
    return f"{d[0:2]} {d[2:4]} {d[4:6]}" if len(d) >= 6 else ""


def lower_keys(r):
    return {(k or "").strip().lower(): (v or "").strip() for k, v in r.items()}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("schedule")
    ap.add_argument("--as-of", required=True)
    ap.add_argument("--weeks", type=int, default=3)
    ap.add_argument("--submittals")
    ap.add_argument("--rfis")
    ap.add_argument("--csv")
    a = ap.parse_args()
    as_of, _ = parse_date(a.as_of)
    w0 = as_of - dt.timedelta(days=as_of.weekday())
    w_end = w0 + dt.timedelta(days=7 * a.weeks - 1)
    weeks = [(w0 + dt.timedelta(days=7 * i), w0 + dt.timedelta(days=7 * i + 6)) for i in range(a.weeks)]

    subs, due_soon = {}, []
    if a.submittals:
        with open(a.submittals, newline="", encoding="utf-8-sig") as fh:
            for r in csv.DictReader(fh):
                r = lower_keys(r)
                if "approved" in r.get("status", "").lower() or r.get("category", "").lower() == "closeout":
                    continue
                subs.setdefault(norm(r.get("spec section")), []).append(r)
                sb, _ = parse_date(r.get("submit by"))
                if sb and sb <= w_end and "submitted" not in r.get("status", "").lower().replace("not submitted", ""):
                    due_soon.append((sb, r))
    rfis = []
    if a.rfis:
        with open(a.rfis, newline="", encoding="utf-8-sig") as fh:
            for r in csv.DictReader(fh):
                r = lower_keys(r)
                if r.get("rfi no") and not r.get("status", "").lower().startswith(("closed", "answered")):
                    secs = {norm(m) for m in re.findall(r"\d{2}\s?\d{2}\s?\d{2}", r.get("spec ref", ""))}
                    rfis.append((r, secs))

    rows = []
    with open(a.schedule, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            r = lower_keys(r)
            if not any(r.values()):
                continue
            st, _ = parse_date(r.get("start"))
            fi, fin_actual = parse_date(r.get("finish"))
            fi = fi or st
            if not st or fin_actual or st > w_end or fi < w0:
                continue
            sec = norm(r.get("spec section"))
            cons = []
            for s in subs.get(sec, []):
                cons.append(f"Submittal {s.get('submittal no')} {s.get('item')} - {s.get('status') or 'not submitted'}"
                            + (f", submit by {s.get('submit by')}" if s.get("submit by") else ""))
            for rf, secs in rfis:
                if sec and sec in secs:
                    cons.append(f"{rf.get('rfi no')} open ({rf.get('subject')})")
            marks = ["X" if st <= we and fi >= ws else "" for ws, we in weeks]
            rows.append({"id": r.get("activity id", ""), "name": r.get("activity name", ""), "start": st,
                         "finish": fi, "resp": r.get("responsible", ""), "sec": sec, "marks": marks, "cons": cons})
    rows.sort(key=lambda x: (x["start"], x["id"]))

    hdr = " | ".join(f"Wk {i + 1} {ws.strftime('%m/%d')}" for i, (ws, _) in enumerate(weeks))
    print(f"{a.weeks}-week look-ahead {w0} to {w_end} (as of {as_of})\n")
    print(f"| ID | Activity | Start | Finish | Responsible | {hdr} | Constraints |")
    print("|---|---|---|---|---|" + "---|" * a.weeks + "---|")
    for x in rows:
        print(f"| {x['id']} | {x['name']} | {x['start']} | {x['finish']} | {x['resp']} | "
              + " | ".join(x["marks"]) + f" | {'; '.join(x['cons']) or '-'} |")
    if due_soon:
        print(f"\nSubmittals due to be submitted by {w_end} (or overdue), not yet submitted:\n")
        print("| Submittal | Item | Submit by | Flags |\n|---|---|---|---|")
        for sb, r in sorted(due_soon, key=lambda t: (t[0], t[1].get("submittal no", ""))):
            late = " (OVERDUE)" if sb < as_of else ""
            print(f"| {r.get('submittal no')} | {r.get('item')} | {sb}{late} | {re.sub(r"(DUE IN \d+d|OVERDUE by \d+d)(; )?", "", r.get('flags', ''))} |")
    n_c = sum(1 for x in rows if x["cons"])
    print(f"\n{len(rows)} activities in window, {n_c} with open submittal/RFI constraints.")
    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["Activity ID", "Activity Name", "Start", "Finish", "Responsible", "Spec Section"]
                       + [f"Wk {i + 1} {ws}" for i, (ws, _) in enumerate(weeks)] + ["Constraints"])
            for x in rows:
                w.writerow([x["id"], x["name"], x["start"], x["finish"], x["resp"], x["sec"]] + x["marks"]
                           + ["; ".join(x["cons"])])
        print(f"Wrote {a.csv}")


if __name__ == "__main__":
    main()
