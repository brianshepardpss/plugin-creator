#!/usr/bin/env python3
"""Reconcile a program budget CSV and check a budget narrative against it.

Usage:
  python3 budget_check.py budget.csv [--cap 25000] [--narrative draft.md]

Reads messy exports: "$60,000" style money, blank rows, subtotal/TOTAL rows,
quantity x unit cost rows with no line total. Column names are matched
loosely (line item/description, category, qty/quantity, unit cost/rate,
line total/amount/cost, request/requested/grant).

Formulas:
  line total      = given line total, else qty x unit cost
                    (if both are given and differ by more than $1: FAIL)
  category total  = sum of line totals in that category
  category share  = category total / program total x 100 (1 decimal)
  indirect rate   = Indirect category total / all other categories x 100
  request share   = total request / program total x 100
  Subtotal and TOTAL rows are not added; their stated values are checked
  against the computed sums (mismatch = FAIL).
Narrative check: every $ amount and % in --narrative must equal a computed
figure (line total, line request, category total, program total, request
total, share, or rate); anything else is listed as UNMATCHED. Sentences
whose only tags cite non-budget sources (profile#..., URLs) are skipped;
untagged sentences and sentences citing a budget/.csv source are checked.
Exit code 1 on any FAIL or UNMATCHED.
"""
import argparse
import csv
import re
import sys
from collections import OrderedDict
from pathlib import Path


def money(s):
    s = (s or "").strip().replace("$", "").replace(",", "")
    if s in ("", "-"):
        return None
    neg = s.startswith("(") and s.endswith(")")
    try:
        v = float(s.strip("()"))
    except ValueError:
        return None
    return -v if neg else v


def find(headers, *names, skip=()):
    for n in names:  # names in priority order
        for h in headers:
            if h not in skip and n in h.lower():
                return h
    return None


def fmt(v):
    return f"${v:,.0f}" if abs(v - round(v)) < 0.005 else f"${v:,.2f}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("budget")
    ap.add_argument("--cap", type=float, help="funder's maximum request")
    ap.add_argument("--narrative", help="markdown file whose $ and % figures must match")
    a = ap.parse_args()

    with open(a.budget, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit("ERROR: empty CSV")
    H = list(rows[0].keys())
    c_item = find(H, "line item", "item", "description", "expense", "line", "name") or H[0]
    c_cat = find(H, "category", "type", "class")
    c_qty = find(H, "qty", "quantity", "units", "fte")
    c_rate = find(H, "unit cost", "rate", "unit price", "salary")
    c_req = find(H, "request", "grant", "funder", skip=(c_item, c_rate, c_qty))
    c_tot = find(H, "line total", "total", "amount", "cost", "budget", skip=(c_item, c_rate, c_qty, c_req))
    if not c_item:
        sys.exit(f"ERROR: no line-item column among {H}")

    fails, lines, checks = [], [], []
    for i, r in enumerate(rows, start=2):
        label = (r.get(c_item) or "").strip()
        vals = [v for v in r.values() if (v or "").strip()]
        if not vals:
            continue
        qty = money(r.get(c_qty)) if c_qty else None
        rate = money(r.get(c_rate)) if c_rate else None
        tot = money(r.get(c_tot)) if c_tot else None
        req = money(r.get(c_req)) if c_req else None
        if re.search(r"(sub)?total", label, re.I):
            checks.append((i, label, tot, req))
            continue
        computed = qty * rate if qty is not None and rate is not None else None
        if tot is None and computed is None:
            fails.append(f"row {i} '{label}': no line total and no qty x unit cost")
            continue
        if tot is not None and computed is not None and abs(tot - computed) > 1:
            fails.append(f"row {i} '{label}': stated {fmt(tot)} but qty x unit cost = {fmt(computed)}")
        line = tot if tot is not None else computed
        if req is not None and req > line + 0.5:
            fails.append(f"row {i} '{label}': request {fmt(req)} exceeds line total {fmt(line)}")
        lines.append({"row": i, "item": label, "cat": (r.get(c_cat) or "").strip() or "Uncategorized",
                      "qty": qty, "rate": rate, "total": line, "request": req or 0.0,
                      "notes": " ".join(v for k, v in r.items() if k not in (c_item, c_cat, c_qty, c_rate, c_tot, c_req) and v)})

    total = sum(l["total"] for l in lines)
    reqtot = sum(l["request"] for l in lines)
    cats = OrderedDict()
    for l in lines:
        c = cats.setdefault(l["cat"], {"total": 0.0, "request": 0.0})
        c["total"] += l["total"]
        c["request"] += l["request"]
    for i, label, tot, req in checks:
        named = next((c for c in cats if c.lower() in label.lower()), None)
        if named is None and not re.search(r"\bsub", label, re.I):
            if tot is not None and abs(tot - total) > 1:
                fails.append(f"row {i} '{label}': stated {fmt(tot)} but lines sum to {fmt(total)}")
            if req is not None and abs(req - reqtot) > 1:
                fails.append(f"row {i} '{label}': stated request {fmt(req)} but lines sum to {fmt(reqtot)}")
        else:
            cat = named
            if cat and tot is not None and abs(tot - cats[cat]["total"]) > 1:
                fails.append(f"row {i} '{label}': stated {fmt(tot)} but {cat} lines sum to {fmt(cats[cat]['total'])}")
            elif cat is None:
                fails.append(f"row {i} '{label}': subtotal does not name a category; not checked")

    print(f"# Budget check: {a.budget}\n")
    print("| Row | Line item | Category | Qty | Unit cost | Line total | Request |")
    print("|---|---|---|---|---|---|---|")
    for l in lines:
        q = "" if l["qty"] is None else f"{l['qty']:g}"
        rt = "" if l["rate"] is None else fmt(l["rate"])
        print(f"| {l['row']} | {l['item']} | {l['cat']} | {q} | {rt} | {fmt(l['total'])} | "
              f"{fmt(l['request']) if l['request'] else ''} |")
    print("\n| Category | Total | Share of program | Request |\n|---|---|---|---|")
    figures = {round(total, 2), round(reqtot, 2)}
    pcts = set()
    for c, v in cats.items():
        share = round(v["total"] / total * 100, 1) if total else 0
        pcts.add(share)
        figures |= {round(v["total"], 2), round(v["request"], 2)}
        print(f"| {c} | {fmt(v['total'])} | {share}% | {fmt(v['request']) if v['request'] else ''} |")
    print(f"| **Program total** | **{fmt(total)}** | 100% | **{fmt(reqtot)}** |\n")
    for l in lines:
        for pm in re.findall(r"(\d+(?:\.\d+)?)\s?%", l["item"] + " " + l["notes"]):
            pcts.add(float(pm))
        figures |= {round(l["total"], 2), round(l["request"], 2)}
        if l["rate"] is not None:
            figures.add(round(l["rate"], 2))
    req_share = round(reqtot / total * 100, 1) if total else 0
    pcts.add(req_share)
    print(f"- Request: {fmt(reqtot)} = {req_share}% of the {fmt(total)} program budget")
    ind = sum(v["total"] for c, v in cats.items() if c.lower().startswith("indirect"))
    if ind:
        direct = total - ind
        rate = round(ind / direct * 100, 1)
        pcts.add(rate)
        figures.add(round(direct, 2))
        print(f"- Indirect: {fmt(ind)} = {rate}% of {fmt(direct)} direct costs")
    if a.cap is not None:
        if reqtot > a.cap:
            fails.append(f"request {fmt(reqtot)} is over the {fmt(a.cap)} cap by {fmt(reqtot - a.cap)}")
        else:
            print(f"- Cap: request is within the {fmt(a.cap)} cap ({fmt(a.cap - reqtot)} headroom)")
    print(f"- Other funding needed for this program: {fmt(total - reqtot)}")
    figures.add(round(total - reqtot, 2))

    unmatched = []
    if a.narrative:
        text = Path(a.narrative).read_text()
        kept = []
        for sent in re.split(r"(?<=[.!?])\s+|\n+", text):
            tags = re.findall(r"\[(?:source|src)\s*:([^\]]*)\]", sent, re.I)
            # sentences citing only non-budget sources (profile facts, URLs) are checked by draft_check.py
            if tags and not any(re.search(r"budget|\.csv", t, re.I) for t in tags):
                continue
            kept.append(re.sub(r"\[(?:source|src)\s*:[^\]]*\]", "", sent, flags=re.I))
        text = " ".join(kept)
        for m in re.finditer(r"\$\s?\d[\d,]*(?:\.\d+)?|\d+(?:\.\d+)?\s?%", text):
            raw = m.group(0)
            v = float(re.sub(r"[^\d.]", "", raw))
            pool = pcts if raw.endswith("%") else figures
            if not any(abs(v - p) < 0.051 for p in pool):
                unmatched.append(raw)
        print(f"\n## Narrative check: {a.narrative}")
        if unmatched:
            for u in dict.fromkeys(unmatched):
                print(f"- UNMATCHED {u}: not a figure in the budget; fix the narrative or the CSV")
        else:
            print("- every $ amount and % in the narrative matches the budget")
    if fails:
        print("\n## Must fix")
        for f in fails:
            print(f"- FAIL {f}")
    ok = not fails and not unmatched
    print("\nResult: " + ("PASS" if ok else "FAIL"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
