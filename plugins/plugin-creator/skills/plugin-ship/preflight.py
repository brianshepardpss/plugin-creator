#!/usr/bin/env python3
"""Pre-publish checks for any Claude plugin, plus .plugin packaging.

Usage:
  python3 preflight.py <plugin-dir>              check only
  python3 preflight.py <plugin-dir> --package    check, then write dist/<name>-<version>.plugin

Checks: strict validation, required manifest metadata, leftover TODOs,
README sections, eval count, sample data, secrets, Cowork compatibility.
A .plugin file is a zip of the plugin folder; Cowork and claude.ai users can
install it directly.
"""
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

META = ["name", "displayName", "version", "description", "author", "homepage",
        "repository", "license", "keywords"]
SECRET = re.compile(r"(sk-ant-[A-Za-z0-9-]{10,}|ghp_[A-Za-z0-9]{20,}|gho_[A-Za-z0-9]{20,}|"
                    r"xox[bp]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY)")
TEXT = {".md", ".json", ".py", ".js", ".ts", ".csv", ".txt", ".yaml", ".yml", ".sh"}
SKIP = {".git", "node_modules", "dist", "results", "__pycache__"}


def files(d):
    for p in d.rglob("*"):
        if p.is_file() and not SKIP.intersection(p.relative_to(d).parts):
            yield p


def check(d):
    errs, warns = [], []
    r = subprocess.run(["claude", "plugin", "validate", str(d), "--strict"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        errs.append("strict validation failed:\n    " +
                    "\n    ".join((r.stdout + r.stderr).strip().splitlines()[-8:]))
    m = json.loads((d / ".claude-plugin" / "plugin.json").read_text())
    for k in META:
        if not m.get(k):
            (errs if k in ("name", "version", "description") else warns).append(f"manifest: no {k}")
    if m.get("skills") == ["./"] or m.get("skills") == "./":
        errs.append('manifest skills is "./" -- overlaps evals/; use ["./skills/"]')

    for p in files(d):
        if p.suffix not in TEXT:
            continue
        t = p.read_text(errors="replace")
        rel = p.relative_to(d)
        if SECRET.search(t):
            errs.append(f"possible secret in {rel}")
        if re.search(r"\bTODO\b", t) and "preflight.py" not in str(rel) and "scaffold.py" not in str(rel):
            errs.append(f"leftover TODO in {rel}")

    readme = (d / "README.md").read_text() if (d / "README.md").exists() else ""
    for section in ("## Install", "## Privacy"):
        if section not in readme:
            warns.append(f"README has no '{section}' section")
    cases = list((d / "evals").glob("*/prompt.md")) if (d / "evals").exists() else []
    if len(cases) < 3:
        warns.append(f"only {len(cases)} eval cases (aim for 3+)")
    if not (d / ".claude-plugin" / "icon.png").exists():
        warns.append("no .claude-plugin/icon.png -- the directory captures the icon only on the first "
                     "save or submit; run make_icon.py before submitting")
    if not (d / "samples").exists():
        warns.append("no samples/ -- new users cannot try it without an account")

    cowork_blockers = [x for x in ("bin", ".lsp.json") if (d / x).exists()]
    surface = ("Claude Code only (has " + ", ".join(cowork_blockers) + ")") if cowork_blockers \
        else "Claude Code, Cowork and claude.ai"
    return m, errs, warns, surface


def package(d, m):
    out = d / "dist" / f"{m['name']}-{m['version']}.plugin"
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files(d):
            if p.name != ".DS_Store":
                z.write(p, p.relative_to(d))
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    d = Path(sys.argv[1]).resolve()
    m, errs, warns, surface = check(d)
    print(f"{m.get('displayName', m.get('name'))} {m.get('version')}  ->  runs in: {surface}")
    for e in errs:
        print(f"  ERROR {e}")
    for w in warns:
        print(f"  warn  {w}")
    if errs:
        print("\nNot ready to publish.")
        sys.exit(1)
    print("\nReady to publish." if not warns else "\nPublishable; fix warnings for directory review.")
    if "--package" in sys.argv:
        print(f"Packaged {package(d, m)}")


if __name__ == "__main__":
    main()
