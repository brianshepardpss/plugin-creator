#!/usr/bin/env python3
"""Count Dart analyzer issues and compare two runs. Standard library only.

Usage:
  python3 analyze_report.py <project-dir> [--save FILE] [--compare FILE] [--from-json FILE]

  <project-dir>     Dart or Flutter package root (has pubspec.yaml).
  --save FILE       Write this run's snapshot (issues + guardrail fingerprints) to FILE.
  --compare FILE    Compare this run against a snapshot saved earlier with --save.
  --from-json FILE  Use saved `dart analyze --format=json` output instead of running dart.

How the numbers are produced:
  * Runs `dart analyze --format=json <project-dir>` (same analyzer as the LSP server).
  * total = number of diagnostics; by severity = count per ERROR / WARNING / INFO;
    by code = count per diagnostic code; by file = count per file.
  * "fatal-infos clean" means total == 0, which is what `dart analyze --fatal-infos` exits 0 on.
  * Guardrail fingerprints, recomputed on every run:
      ignores   = number of `// ignore:` and `// ignore_for_file:` comments in *.dart files
                  (excluding .dart_tool/ and build/)
      options   = sha256 of analysis_options.yaml (or "absent")
    --compare reports FAIL if ignores went up or analysis_options.yaml changed, because
    silencing the analyzer is not fixing it.
Exit code: 0 when total == 0 and no guardrail failed, 1 otherwise, 2 on usage errors.
"""
import hashlib
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

IGNORE_RE = re.compile(r"//\s*ignore(?:_for_file)?\s*:")
SKIP_DIRS = {".dart_tool", "build", ".git", ".fvm"}


def run_dart(project):
    dart = shutil.which("dart")
    if not dart:
        sys.exit("dart not found on PATH. Install the Flutter or Dart SDK, or pass --from-json.")
    r = subprocess.run([dart, "analyze", "--format=json", str(project)],
                       capture_output=True, text=True, timeout=900)
    out = r.stdout.strip()
    start = out.find("{")
    if start == -1:
        if "No issues found" in r.stdout + r.stderr or (r.returncode == 0 and not out):
            return {"diagnostics": []}
        sys.exit("Could not parse dart analyze output:\n" + (r.stdout + r.stderr)[-2000:])
    return json.loads(out[start:])


def fingerprints(project):
    ignores = 0
    where = []
    for p in project.rglob("*.dart"):
        if SKIP_DIRS.intersection(p.relative_to(project).parts):
            continue
        for i, line in enumerate(p.read_text(errors="replace").splitlines(), 1):
            if IGNORE_RE.search(line):
                ignores += 1
                where.append(f"{p.relative_to(project)}:{i}")
    ao = project / "analysis_options.yaml"
    opts = hashlib.sha256(ao.read_bytes()).hexdigest()[:16] if ao.exists() else "absent"
    return {"ignores": ignores, "ignore_sites": where, "options_sha": opts}


def snapshot(project, data):
    issues = []
    for d in data.get("diagnostics", []):
        loc = d.get("location", {})
        f = loc.get("file", "")
        try:
            f = str(Path(f).resolve().relative_to(project.resolve()))
        except ValueError:
            pass
        start = loc.get("range", {}).get("start", {})
        issues.append({"severity": d.get("severity", "?"), "code": d.get("code", "?"),
                       "file": f, "line": start.get("line", 0),
                       "message": d.get("problemMessage", "")})
    return {"issues": issues, **fingerprints(project)}


def summarize(s, title):
    iss = s["issues"]
    sev = Counter(i["severity"] for i in iss)
    print(f"{title}: {len(iss)} issues  (errors {sev.get('ERROR', 0)}, warnings {sev.get('WARNING', 0)}, infos {sev.get('INFO', 0)})")
    if iss:
        print("  by code:")
        for code, n in Counter(i["code"] for i in iss).most_common():
            print(f"    {n:>3}  {code}")
        print("  by file:")
        for f, n in Counter(i["file"] for i in iss).most_common():
            print(f"    {n:>3}  {f}")
    print(f"  ignore comments: {s['ignores']}   analysis_options.yaml: {s['options_sha']}")


def compare(before, after):
    b, a = len(before["issues"]), len(after["issues"])
    print(f"\nBefore -> after: {b} -> {a} issues ({b - a} fixed)")
    bs, as_ = Counter(i["severity"] for i in before["issues"]), Counter(i["severity"] for i in after["issues"])
    for sev in ("ERROR", "WARNING", "INFO"):
        print(f"  {sev.lower() + 's':<9} {bs.get(sev, 0):>3} -> {as_.get(sev, 0):>3}")
    key = lambda i: (i["code"], i["file"])  # noqa: E731
    new = Counter(map(key, after["issues"])) - Counter(map(key, before["issues"]))
    if new:
        print("  new since before (introduced by edits?):")
        for (code, f), n in sorted(new.items()):
            print(f"    {n:>3}  {code}  {f}")
    fails = []
    if after["ignores"] > before["ignores"]:
        added = sorted(set(after["ignore_sites"]) - set(before["ignore_sites"]))
        fails.append(f"ignore comments went {before['ignores']} -> {after['ignores']}: " + ", ".join(added))
    if after["options_sha"] != before["options_sha"]:
        fails.append(f"analysis_options.yaml changed ({before['options_sha']} -> {after['options_sha']})")
    for f in fails:
        print(f"  [FAIL guardrail] {f}")
    if not fails:
        print("  [OK guardrail] no new ignore comments; analysis_options.yaml unchanged")
    return fails


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 2

    def opt(name):
        if name in args:
            i = args.index(name)
            val = args[i + 1]
            del args[i:i + 2]
            return val
        return None

    save, comp, fromj = opt("--save"), opt("--compare"), opt("--from-json")
    project = Path(args[0])
    if not (project / "pubspec.yaml").exists():
        print(f"{project} has no pubspec.yaml", file=sys.stderr)
        return 2
    if fromj:
        t = Path(fromj).read_text()
        data = json.loads(t[t.find("{"):]) if "{" in t else {"diagnostics": []}
    else:
        data = run_dart(project)
    snap = snapshot(project, data)
    summarize(snap, "Analyzer")
    fails = []
    if comp:
        fails = compare(json.loads(Path(comp).read_text()), snap)
    if save:
        Path(save).write_text(json.dumps(snap, indent=1))
        print(f"  snapshot saved to {save}")
    return 0 if not snap["issues"] and not fails else 1


if __name__ == "__main__":
    sys.exit(main())
