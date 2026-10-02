#!/usr/bin/env python3
"""Enforce CONVENTIONS.md across every plugin in plugins/.

Usage: python3 lab/check.py [slug ...] [--no-validate]
Exits 1 if any plugin fails. --no-validate skips `claude plugin validate`.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = json.loads((ROOT / "lab" / "plugins.json").read_text())
OWNER = REGISTRY["owner"]
SHARED_REQUEST = (ROOT / "shared" / "request" / "SKILL.md").read_text()
REQUIRED = ["name", "displayName", "version", "description", "author",
            "homepage", "repository", "license", "keywords"]
AUTHOR = {"name": "Press Start Studios", "email": "brian@press-start-studios.com",
          "url": f"https://github.com/{OWNER}"}
STDLIB = set(sys.stdlib_module_names)


def check(entry, validate):
    slug, repo = entry["slug"], entry["repo"]
    d = ROOT / "plugins" / slug
    errs = []
    if not d.is_dir():
        return [f"missing directory plugins/{slug}"]
    mpath = d / ".claude-plugin" / "plugin.json"
    try:
        m = json.loads(mpath.read_text())
    except Exception as e:
        return [f"plugin.json unreadable: {e}"]

    for k in REQUIRED:
        if not m.get(k):
            errs.append(f"manifest missing {k}")
    if m.get("name") != slug:
        errs.append(f"manifest name {m.get('name')!r} != slug {slug!r}")
    if m.get("author") != AUTHOR:
        errs.append("author must equal the CONVENTIONS author block")
    url = f"https://github.com/{OWNER}/{repo}"
    for k in ("homepage", "repository"):
        if m.get(k) != url:
            errs.append(f"{k} must be {url}")
    if m.get("license") != "MIT":
        errs.append("license must be MIT")
    if m.get("skills") != ["./skills/"]:
        errs.append('skills must be ["./skills/"]')
    if re.match(r"^(claude|anthropic|cc-plugin)-", slug):
        errs.append("reserved name prefix")

    req = d / "skills" / "request" / "SKILL.md"
    want = SHARED_REQUEST.replace("{{REPO}}", repo).replace("{{PLUGIN}}", m.get("displayName", slug))
    if not req.exists():
        errs.append("missing skills/request/SKILL.md")
    elif req.read_text() != want:
        errs.append("skills/request/SKILL.md drifted from shared/request (run lab/sync_request.py)")

    skills = [p for p in (d / "skills").glob("*/SKILL.md") if p.parent.name != "request"]
    if len(skills) < 2:
        errs.append("needs at least 2 skills besides request")
    for s in skills:
        head = s.read_text().split("---")
        if len(head) < 3 or "description:" not in head[1]:
            errs.append(f"{s.relative_to(d)} lacks frontmatter description")

    cases = [p for p in (d / "evals").glob("*/prompt.md")] if (d / "evals").is_dir() else []
    if len(cases) < 3:
        errs.append(f"needs >= 3 eval cases, has {len(cases)}")
    for c in cases:
        if not list((c.parent / "graders").glob("*.md")):
            errs.append(f"{c.parent.name} has no graders")

    for f in ("README.md", "LAUNCH.md"):
        if not (d / f).exists():
            errs.append(f"missing {f}")
    readme = (d / "README.md").read_text() if (d / "README.md").exists() else ""
    if entry["level"] == 1 and "Not affiliated" not in readme:
        errs.append("README lacks the 'Not affiliated' line")
    if entry["level"] == 1 and not (d / "samples").is_dir():
        errs.append("missing samples/ (hero workflow must run without an account)")

    if entry["surface"] == "cowork":
        if (d / ".lsp.json").exists() or (d / "bin").exists():
            errs.append("cowork plugin may not ship .lsp.json or bin/")
        for py in d.rglob("*.py"):
            for mod in re.findall(r"^\s*(?:from|import)\s+([A-Za-z_]\w*)", py.read_text(), re.M):
                if mod not in STDLIB:
                    errs.append(f"{py.relative_to(d)} imports non-stdlib {mod}")

    for p in d.rglob("*"):
        if p.is_file() and p.suffix in {".md", ".json", ".py", ".csv", ".txt", ".yaml", ".sh"}:
            t = p.read_text(errors="replace")
            if re.search(r"(sk-ant-[A-Za-z0-9-]{20,}|gh[po]_[A-Za-z0-9]{20,}|xox[bp]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)", t):
                errs.append(f"possible secret in {p.relative_to(d)}")

    if validate:
        r = subprocess.run(["claude", "plugin", "validate", str(d), "--strict"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            errs.append("claude plugin validate --strict failed:\n      "
                        + "\n      ".join((r.stdout + r.stderr).strip().splitlines()[-8:]))
    return errs


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    validate = "--no-validate" not in sys.argv
    entries = [e for e in REGISTRY["plugins"] if not args or e["slug"] in args]
    bad = 0
    for e in entries:
        errs = check(e, validate)
        print(f"{'FAIL' if errs else 'ok  '} {e['slug']}")
        for x in errs:
            print(f"     - {x}")
        bad += bool(errs)
    a = ROOT / "plugins/plugin-creator/skills/plugin-brief/demand.py"
    b = ROOT / "plugins/plugin-studio/skills/radar/demand.py"
    if a.exists() and b.exists() and a.read_bytes() != b.read_bytes():
        print("FAIL shared: plugin-studio radar/demand.py differs from plugin-creator plugin-brief/demand.py")
        bad += 1
    print(f"\n{len(entries) - bad}/{len(entries)} plugins pass")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
