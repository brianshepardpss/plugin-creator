#!/usr/bin/env python3
"""Total jobsite manpower for a daily report. Standard library only.

Usage:
  python3 manpower.py "GC (Halvorsen)=3" "Plumbing (Rio Verde)=4" "Demo=1@2" \
      [--hours 8] [--lost "Plumbing=4x3"]

Each entry is Company/trade=WORKERS[@HOURS_EACH]. Hours are only counted when
given per entry or via --hours (a default for entries without @). If neither
is given, worker-hours for that entry are "not recorded" and are left out of
the total (the total is then marked partial).
--lost Trade=WORKERSxHOURS records lost or impacted time as stated in the
notes: worker-hours = workers x hours.
"""
import argparse
from decimal import Decimal


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entries", nargs="+")
    ap.add_argument("--hours", type=Decimal)
    ap.add_argument("--lost", action="append", default=[])
    a = ap.parse_args()
    print("| Company / trade | Workers | Hours each | Worker-hours |")
    print("|---|---|---|---|")
    heads, wh, partial = 0, Decimal(0), False
    for e in a.entries:
        name, _, spec = e.rpartition("=")
        cnt, _, hrs = spec.partition("@")
        cnt = int(cnt)
        h = Decimal(hrs) if hrs else a.hours
        heads += cnt
        if h is None:
            partial = True
            print(f"| {name} | {cnt} | not recorded | not recorded |")
        else:
            wh += cnt * h
            print(f"| {name} | {cnt} | {h} | {cnt * h} |")
    print(f"| **Total** | **{heads}** | | **{wh}{' (partial: some hours not recorded)' if partial else ''}** |")
    for l in a.lost:
        name, _, spec = l.rpartition("=")
        w, _, h = spec.lower().partition("x")
        print(f"\nLost/impacted time, {name}: {int(w)} workers x {Decimal(h)} h = {int(w) * Decimal(h)} worker-hours "
              "(as stated in the notes; approximate if the notes say so).")


if __name__ == "__main__":
    main()
