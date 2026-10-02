#!/usr/bin/env python3
"""Annotate an MR diff with the exact line numbers GitLab expects for
inline comments, and size the review before spending tokens on it.

Usage:
  glab mr diff <iid> --raw | python3 diff_lines.py - [--max-lines 1500] [--summary]
  python3 diff_lines.py mr.diff

Output:
  1. A summary: files changed, lines added/removed per file, total changed
     lines, and files skipped as generated/vendored (lockfiles, minified
     bundles, vendor/, snapshots). If total changed lines exceed
     --max-lines, it says so: review per file or ask the user to narrow it.
  2. (unless --summary) every hunk line prefixed with NEW and OLD line
     numbers:
        NEW   OLD  marker text
     For an inline comment on an added (+) or unchanged ( ) line use
     `--file <path> --line <NEW>`; for a removed (-) line use
     `--file <path> --old-line <OLD>`. A line outside every hunk cannot take
     an inline comment (GitLab answers 400 "line_code can't be blank").

Standard library only.
"""
import argparse
import re
import sys

SKIP = re.compile(r"(^|/)(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|poetry\.lock|Pipfile\.lock|"
                  r"Cargo\.lock|go\.sum|composer\.lock|Gemfile\.lock|uv\.lock)$|\.min\.(js|css)$|"
                  r"(^|/)(vendor|node_modules|dist|build)/|\.snap$|\.svg$")
HUNK = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@(.*)")


def parse(text):
    files, cur = [], None
    old = new = 0
    for line in text.splitlines():
        if line.startswith("diff --git "):
            m = re.match(r"diff --git a/(.*) b/(.*)", line)
            cur = {"old": m.group(1) if m else "?", "new": m.group(2) if m else "?", "status": "modified",
                   "add": 0, "del": 0, "rows": [], "binary": False}
            files.append(cur)
        elif cur is None:
            continue
        elif line.startswith("new file mode"):
            cur["status"] = "new file"
        elif line.startswith("deleted file mode"):
            cur["status"] = "deleted"
        elif line.startswith("rename from "):
            cur["status"] = "renamed"
        elif line.startswith("Binary files "):
            cur["binary"] = True
        elif line.startswith("--- ") or line.startswith("+++ ") or line.startswith("index "):
            continue
        elif line.startswith("@@"):
            m = HUNK.match(line)
            old, new = int(m.group(1)), int(m.group(2))
            cur["rows"].append(("@@", None, None, line))
        elif line.startswith("+"):
            cur["rows"].append(("+", new, None, line[1:]))
            cur["add"] += 1
            new += 1
        elif line.startswith("-"):
            cur["rows"].append(("-", None, old, line[1:]))
            cur["del"] += 1
            old += 1
        elif line.startswith(" ") or line == "":
            cur["rows"].append((" ", new, old, line[1:]))
            new += 1
            old += 1
        elif line.startswith("\\"):
            continue
    return files


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file", help="unified diff file, or - for stdin")
    ap.add_argument("--max-lines", type=int, default=1500,
                    help="changed-line budget for a single review pass (default 1500)")
    ap.add_argument("--summary", action="store_true", help="print only the summary")
    a = ap.parse_args()
    text = sys.stdin.read() if a.file == "-" else open(a.file, encoding="utf-8", errors="replace").read()
    files = parse(text)

    review = [f for f in files if not SKIP.search(f["new"]) and not f["binary"]]
    skipped = [f for f in files if f not in review]
    changed = sum(f["add"] + f["del"] for f in review)
    print(f"files changed: {len(files)} (reviewing {len(review)}, skipped {len(skipped)})")
    for f in files:
        tag = " [skipped: generated/vendored/binary]" if f in skipped else ""
        print(f"  {f['new']}  +{f['add']} -{f['del']}  ({f['status']}){tag}")
    print(f"changed lines to review: {changed} (budget {a.max_lines})")
    if changed > a.max_lines:
        print("OVER BUDGET: review file by file (pass one path at a time to the reviewer) "
              "or ask the user which files matter.")
    if a.summary:
        return
    for f in review:
        print(f"\n=== {f['new']} ({f['status']}) ===")
        print(f"{'NEW':>5} {'OLD':>5}  text")
        for kind, n, o, t in f["rows"]:
            if kind == "@@":
                print(t)
                continue
            print(f"{'' if n is None else n:>5} {'' if o is None else o:>5} {kind}{t}")


if __name__ == "__main__":
    main()
