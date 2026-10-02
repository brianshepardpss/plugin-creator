#!/usr/bin/env python3
"""Fair Housing phrase check for real estate marketing text. Standard library only.

Usage:
  python3 fair_housing.py FILE [FILE ...]            check marketing text files
  python3 fair_housing.py --remarks remarks.txt      also apply MLS remark rules
                                                     (no compensation, no contact
                                                     info, character cap)
  python3 fair_housing.py --text "Perfect for young families"
  python3 fair_housing.py --cap 1000 --remarks r.txt social.md email.md --out report.md
  add --json for machine-readable output.

How it decides (deterministic, auditable):
  - Every entry in phrases.json is a regular expression with a level
    (FLAG = must fix, REVIEW = check context, NOTE = style only), a category
    (protected class, steering proxy or MLS rule), a reason and a rewrite.
  - Matching is case-insensitive unless the entry says case_sensitive.
  - When two matches overlap, the higher level wins (FLAG > REVIEW > NOTE).
  - Entries with scope "remarks" run only on --remarks files. Entries with
    level_outside_remarks use that lower level outside MLS remarks.
  - Length = len(text.strip()) characters (and words) for every input;
    for remarks it is compared with --cap.
  - Overall status: FLAG if any FLAG, else REVIEW if any REVIEW, else PASS.

This is a phrase list, not legal advice. It cannot see context ("walk-in
closet" is fine; "perfect for a young couple" is not), so the skill that
calls it also reviews the text in context.
"""
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RANK = {"FLAG": 3, "REVIEW": 2, "NOTE": 1}


def load():
    data = json.loads((HERE / "phrases.json").read_text())
    out = []
    for e in data["entries"]:
        flags = 0 if e.get("case_sensitive") else re.I
        out.append((e, re.compile(e["pattern"], flags)))
    return out


def check_text(text, label, is_remarks, entries):
    hits = []
    for e, rx in entries:
        if e.get("scope") == "remarks" and not is_remarks:
            continue
        level = e["level"] if is_remarks or "level_outside_remarks" not in e else e["level_outside_remarks"]
        for m in rx.finditer(text):
            hits.append({"start": m.start(), "end": m.end(), "phrase": m.group(0), "level": level,
                         "category": e["category"], "why": e["why"], "rewrite": e["rewrite"], "id": e["id"]})
    hits.sort(key=lambda h: (-RANK[h["level"]], h["start"]))
    kept = []
    for h in hits:
        if any(h["start"] < k["end"] and k["start"] < h["end"] for k in kept):
            continue
        kept.append(h)
    kept.sort(key=lambda h: h["start"])
    for h in kept:
        line = text.count("\n", 0, h["start"]) + 1
        h["where"] = f"{label}:{line}"
        del h["start"], h["end"]
    return kept


def status(hits):
    levels = {h["level"] for h in hits}
    return "FLAG" if "FLAG" in levels else "REVIEW" if "REVIEW" in levels else "PASS"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--remarks", action="append", default=[], help="MLS public remarks file(s)")
    ap.add_argument("--text", action="append", default=[], help="inline text to check")
    ap.add_argument("--cap", type=int, default=1000, help="MLS public remarks character limit")
    ap.add_argument("--out")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if not (a.files or a.remarks or a.text):
        if sys.stdin.isatty():
            sys.exit("give files, --remarks FILE or --text TEXT (or pipe text on stdin)")
        a.text.append(sys.stdin.read())

    entries = load()
    docs = [(f, Path(f).read_text(), True) for f in a.remarks]
    docs += [(f, Path(f).read_text(), False) for f in a.files]
    docs += [(f"text{i + 1}", t, False) for i, t in enumerate(a.text)]

    results = []
    for label, text, is_remarks in docs:
        hits = check_text(text, Path(label).name, is_remarks, entries)
        n = len(text.strip())
        r = {"file": label, "mls_remarks": is_remarks, "status": status(hits), "hits": hits,
             "chars": n, "words": len(text.split())}
        if is_remarks:
            r["cap"] = a.cap
            if n > a.cap:
                r["status"] = "FLAG"
                r["hits"].append({"phrase": f"{n} characters", "level": "FLAG", "category": "MLS rule: length",
                                  "why": f"Public remarks are {n} characters; the cap is {a.cap}.",
                                  "rewrite": f"Cut {n - a.cap} or more characters.", "id": "mls-cap",
                                  "where": Path(label).name})
        results.append(r)
    overall = max((r["status"] for r in results), key=lambda s: {"PASS": 0, "REVIEW": 1, "FLAG": 2}[s])

    if a.json:
        out = json.dumps({"overall": overall, "results": results}, indent=2)
    else:
        L = ["# Fair Housing check", "",
             f"Overall: **{overall}** (FLAG = must fix, REVIEW = check context, NOTE = style only)", "",
             "| Text | Status | FLAG | REVIEW | NOTE | Length |", "|---|---|---|---|---|---|"]
        for r in results:
            c = {k: sum(1 for h in r["hits"] if h["level"] == k) for k in RANK}
            ln = f"{r['chars']}/{r['cap']} chars" if r["mls_remarks"] else f"{r['chars']} chars, {r['words']} words"
            L.append(f"| {Path(r['file']).name}{' (MLS remarks)' if r['mls_remarks'] else ''} | {r['status']} | "
                     f"{c['FLAG']} | {c['REVIEW']} | {c['NOTE']} | {ln} |")
        L.append("")
        any_hits = [h for r in results for h in r["hits"]]
        if any_hits:
            L += ["| Level | Phrase | Where | Category | Why | Suggested rewrite |", "|---|---|---|---|---|---|"]
            for h in any_hits:
                L.append(f"| {h['level']} | \"{h['phrase']}\" | {h['where']} | {h['category']} | {h['why']} | {h['rewrite']} |")
            L.append("")
        else:
            L += ["No listed phrases found.", ""]
        L.append("Phrase-list check only; not legal advice. Describe the property, not the people. "
                 "Context review still required.")
        out = "\n".join(L) + "\n"
    if a.out:
        Path(a.out).write_text(out)
    print(out)


if __name__ == "__main__":
    main()
