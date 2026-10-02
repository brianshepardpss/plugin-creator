#!/usr/bin/env python3
"""Print the CHANGELOG entries a package upgrade crosses, and the breaking lines in them.
Standard library only. Reads the CHANGELOG.md that pub already downloaded; no network.

Usage:
  python3 changelog_slice.py <project-dir> <package> --from <old-version> [--to <new-version>] [--all]

  --from   the version you are upgrading from (from the old pubspec.lock or `pub outdated`)
  --to     defaults to the version currently resolved in .dart_tool/package_config.json
  --all    print every line of the crossed sections, not just the flagged ones

How it works:
  * Finds the package root via .dart_tool/package_config.json (rootUri), so it reads the
    exact version the project now resolves (run `pub get` / `pub upgrade` first).
  * A section starts at a Markdown heading whose first token is a version (e.g. "## 3.0.0",
    "# 9.0.0", "## 3.0.0-dev.12 - 2025-04-30"). Sections with old < version <= new are kept.
    Pre-releases sort before their release (3.0.0-dev.12 < 3.0.0).
  * A line is flagged when it matches BREAKING, removed, renamed, deprecated, "no longer",
    "now requires", "minimum supported SDK", "migrat" (case-insensitive).
Exit code 0 if the slice was printed, 2 on errors (package not found, no CHANGELOG).
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

FLAG = re.compile(r"breaking|removed|renamed|deprecat|no longer|now requires|minimum supported sdk|migrat", re.I)
HEAD = re.compile(r"^#{1,4}\s*\[?v?(\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.\-+]*)?)\]?")


def key(ver):
    core, _, pre = ver.partition("-")
    core = core.split("+")[0]
    nums = [int(x) for x in core.split(".")[:3]]
    if not pre:
        return (nums, 1, [])
    parts = [(0, int(p), "") if p.isdigit() else (1, 0, p) for p in re.split(r"[.\-]", pre.split("+")[0])]
    return (nums, 0, parts)


def package_root(project, name):
    cfg = project / ".dart_tool" / "package_config.json"
    if not cfg.exists():
        sys.exit(f"{cfg} not found; run `flutter pub get` first.")
    for p in json.loads(cfg.read_text())["packages"]:
        if p["name"] == name:
            uri = p["rootUri"]
            if uri.startswith("file:"):
                return Path(unquote(urlparse(uri).path))
            return (cfg.parent / uri).resolve()
    return None


def resolved_version(root):
    ps = root / "pubspec.yaml"
    m = re.search(r"^version:\s*['\"]?([^\s'\"]+)", ps.read_text(), re.M) if ps.exists() else None
    return m.group(1) if m else None


def main():
    a = sys.argv[1:]
    if len(a) < 2 or a[0] in ("-h", "--help"):
        print(__doc__)
        return 2

    def opt(n):
        if n in a:
            i = a.index(n)
            v = a[i + 1]
            del a[i:i + 2]
            return v
        return None

    old, new = opt("--from"), opt("--to")
    show_all = "--all" in a
    a = [x for x in a if x != "--all"]
    project, name = Path(a[0]), a[1]
    if not old:
        print("--from <old-version> is required", file=sys.stderr)
        return 2
    root = package_root(project, name)
    if not root:
        print(f"{name} is not in {project}/.dart_tool/package_config.json", file=sys.stderr)
        return 2
    new = new or resolved_version(root)
    cl = root / "CHANGELOG.md"
    if not cl.exists():
        print(f"No CHANGELOG.md in {root}; read the package page or repository instead.", file=sys.stderr)
        return 2

    sections, cur = [], None
    for line in cl.read_text(errors="replace").splitlines():
        m = HEAD.match(line)
        if m:
            cur = (m.group(1), [])
            sections.append(cur)
        elif cur:
            cur[1].append(line)

    lo, hi = key(old), key(new)
    crossed = [(v, body) for v, body in sections if lo < key(v) <= hi]
    flagged = [(v, ln.strip()) for v, body in crossed for ln in body if FLAG.search(ln)]

    print(f"{name}: {old} -> {new}  ({cl})")
    print(f"Sections crossed: {len(crossed)}   flagged lines: {len(flagged)}")
    majors = sorted({key(v)[0][0] for v, _ in crossed if key(v)[1] == 1})
    if majors:
        print(f"Release majors crossed: {', '.join(str(m) for m in majors)}")
    if show_all:
        for v, body in crossed:
            print(f"\n## {v}")
            print("\n".join(l for l in body if l.strip()))
    else:
        print("\nFlagged (version: line):")
        for v, ln in flagged:
            print(f"  {v}: {ln[:220]}")
        links = sorted({u for _, body in crossed for ln in body for u in re.findall(r"https?://\S*migrat\S*|https?://flutter\.dev/go/\S+", ln, re.I)})
        if links:
            print("\nMigration guides linked from the changelog:")
            for u in links:
                print(f"  {u.rstrip(').,')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
