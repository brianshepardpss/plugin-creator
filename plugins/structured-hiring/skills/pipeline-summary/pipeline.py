#!/usr/bin/env python3
"""Aggregate pipeline status for ONE req from an ATS pipeline export.

Usage:
  python3 pipeline.py <pipeline.csv> [--scorecards scorecards.json]
                      [--as-of YYYY-MM-DD] [--stuck-days 14] [--json]

Input CSV needs a candidate column, a stage column and a stage-entered date
column; common header spellings are recognized (see fields.md). Dates may be
YYYY-MM-DD, MM/DD/YYYY or YYYY-MM-DDTHH:MM. Blank rows are skipped; exact
duplicate (candidate, stage, date) rows are counted once and reported.

Formulas:
  days_in_stage  = as_of - stage_entered            (calendar days)
  stuck          = active stage and days_in_stage > --stuck-days (default 14)
  overdue card   = interview with no submitted scorecard and
                   as_of - interview_date > 1 day   (24h submission norm)
  median days    = statistics.median of days_in_stage over active candidates
Closed stages (Rejected, Withdrawn, Hired, Archived, Declined) are counted but
excluded from days-in-stage, stuck and median.

It reports stage counts and stuck items only. It never scores, ranks or
compares candidates.
"""
import csv
import datetime as dt
import json
import statistics
import sys

CLOSED = {"rejected", "withdrawn", "hired", "archived", "declined", "offer declined"}
HEAD = {
    "candidate": ("candidate", "candidate name", "name", "applicant"),
    "stage": ("current stage", "stage", "status", "current_stage", "pipeline stage"),
    "entered": ("stage entered", "entered stage", "stage_entered", "date entered stage",
                "last stage change", "moved to stage at", "stage changed at"),
}


def pdate(s):
    s = (s or "").strip()[:10]
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d.%m.%Y"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    s = s.split("T")[0]
    try:
        return dt.date.fromisoformat(s)
    except ValueError:
        return None


def find(heads, keys):
    low = {h.strip().lower(): h for h in heads}
    for k in keys:
        if k in low:
            return low[k]
    return None


def summarize(path, as_of, stuck_days=14, scorecards=None):
    rows, dupes, bad = [], 0, []
    with open(path, newline="", encoding="utf-8-sig") as f:
        rd = csv.DictReader(f)
        cols = {k: find(rd.fieldnames or [], v) for k, v in HEAD.items()}
        missing = [k for k, v in cols.items() if not v]
        if missing:
            raise SystemExit(f"Could not find column(s) {missing} in {rd.fieldnames}. Map them using fields.md.")
        seen = set()
        for r in rd:
            if not any((v or "").strip() for v in r.values()):
                continue
            name = r[cols["candidate"]].strip()
            stage = " ".join(w.capitalize() for w in r[cols["stage"]].strip().split())
            d = pdate(r[cols["entered"]])
            key = (name.lower(), stage.lower(), d)
            if key in seen:
                dupes += 1
                continue
            seen.add(key)
            if d is None:
                bad.append(name)
            rows.append({"candidate": name, "stage": stage, "entered": d.isoformat() if d else None,
                         "days_in_stage": (as_of - d).days if d else None,
                         "closed": stage.lower() in CLOSED})
    order = []
    for r in rows:
        if r["stage"] not in order:
            order.append(r["stage"])
    counts = {s: sum(1 for r in rows if r["stage"] == s) for s in order}
    active = [r for r in rows if not r["closed"] and r["days_in_stage"] is not None]
    stuck = sorted([r for r in active if r["days_in_stage"] > stuck_days], key=lambda r: -r["days_in_stage"])
    overdue = []
    if scorecards:
        for i in json.load(open(scorecards, encoding="utf-8")).get("interviews", []):
            d = pdate(i.get("date"))
            if not i.get("submitted_at") and d and (as_of - d).days > 1:
                overdue.append({"candidate": i["candidate"], "interviewer": i["interviewer"],
                                "session": i["session"], "interview_date": d.isoformat(),
                                "days_since_interview": (as_of - d).days})
    return {"as_of": as_of.isoformat(), "stuck_threshold_days": stuck_days,
            "total_candidates": len(rows), "active": sum(1 for r in rows if not r["closed"]),
            "closed": sum(1 for r in rows if r["closed"]), "stage_counts": counts,
            "median_days_in_stage_active": statistics.median([r["days_in_stage"] for r in active]) if active else None,
            "stuck": stuck, "overdue_scorecards": overdue, "duplicates_removed": dupes,
            "unparsed_dates": bad, "candidates": rows}


def render(s):
    L = [f"Pipeline as of {s['as_of']}: {s['total_candidates']} candidates "
         f"({s['active']} active, {s['closed']} closed).", "",
         "| Stage | Candidates |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in s["stage_counts"].items()]
    L += ["", f"Median days in current stage (active): {s['median_days_in_stage_active']}", "",
          f"Stuck (> {s['stuck_threshold_days']} days in stage):"]
    L += [f"- {r['candidate']}: {r['stage']} since {r['entered']} ({r['days_in_stage']} days)" for r in s["stuck"]] or ["- none"]
    L += ["", "Overdue scorecards (no feedback > 1 day after the interview):"]
    L += [f"- {o['interviewer']} for {o['candidate']} ({o['session']}, {o['interview_date']}; "
          f"{o['days_since_interview']} days ago)" for o in s["overdue_scorecards"]] or ["- none (or no scorecard data given)"]
    L += ["", "Days in current stage (active candidates):"]
    L += [f"- {r['candidate']}: {r['stage']}, {r['days_in_stage']} days" for r in s["candidates"]
          if not r["closed"] and r["days_in_stage"] is not None]
    notes = []
    if s["duplicates_removed"]:
        notes.append(f"{s['duplicates_removed']} duplicate row(s) removed")
    if s["unparsed_dates"]:
        notes.append("unparsed dates for: " + ", ".join(s["unparsed_dates"]))
    if notes:
        L += ["", "Data notes: " + "; ".join(notes) + "."]
    return "\n".join(L)


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    def opt(n, d=None):
        return a[a.index(n) + 1] if n in a else d
    as_of = pdate(opt("--as-of")) if opt("--as-of") else dt.date.today()
    s = summarize(a[0], as_of, int(opt("--stuck-days", 14)), opt("--scorecards"))
    print(json.dumps(s, indent=2) if "--json" in a else render(s))


if __name__ == "__main__":
    main()
