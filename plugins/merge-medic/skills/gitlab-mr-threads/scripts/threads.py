#!/usr/bin/env python3
"""Compact view of the unresolved discussions on a GitLab merge request.

Usage:
  glab mr note list <iid> --state unresolved -F json | python3 threads.py -
  python3 threads.py discussions.json [--all] [--json]

Input: the JSON array printed by `glab mr note list -F json` or by
`glab api projects/:id/merge_requests/<iid>/discussions`.

Keeps only resolvable, unresolved, non-system discussions (use --all to
keep resolved ones too). For each it prints the 8-character ID prefix that
`glab mr note create --reply` and `glab mr note resolve` accept, the full
discussion ID, file:line for diff threads, who opened it, how many replies
it has, who spoke last, and the full text of the first and last notes.
Standard library only.
"""
import argparse
import json
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file", help="JSON file, or - for stdin")
    ap.add_argument("--all", action="store_true", help="include resolved threads")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    discs = json.load(sys.stdin if a.file == "-" else open(a.file))

    rows = []
    for d in discs:
        notes = [n for n in d.get("notes", []) if not n.get("system")]
        if not notes or not any(n.get("resolvable") for n in notes):
            continue
        resolved = all(n.get("resolved") for n in notes if n.get("resolvable"))
        if resolved and not a.all:
            continue
        first, last = notes[0], notes[-1]
        pos = first.get("position") or {}
        where = "general"
        if pos.get("new_path"):
            line = pos.get("new_line") or pos.get("old_line")
            side = "" if pos.get("new_line") else " (old side)"
            where = f"{pos['new_path']}:{line}{side}"
        rows.append({
            "id": d["id"], "short_id": d["id"][:8], "where": where,
            "author": (first.get("author") or {}).get("username", "?"),
            "replies": len(notes) - 1,
            "last_author": (last.get("author") or {}).get("username", "?"),
            "resolved": resolved, "first_note": first.get("body", ""),
            "last_note": last.get("body", "") if len(notes) > 1 else None,
        })
    if a.json:
        print(json.dumps(rows, indent=2))
        return
    label = "threads" if a.all else "unresolved threads"
    print(f"{label}: {len(rows)}")
    for r in rows:
        state = " [resolved]" if r["resolved"] else ""
        print(f"\n[{r['short_id']}] {r['where']} by @{r['author']}, {r['replies']} repl"
              f"{'y' if r['replies'] == 1 else 'ies'}, last: @{r['last_author']}{state}")
        print(f"  full id: {r['id']}")
        print("  first: " + r["first_note"].replace("\n", "\n         "))
        if r["last_note"]:
            print("  last:  " + r["last_note"].replace("\n", "\n         "))


if __name__ == "__main__":
    main()
