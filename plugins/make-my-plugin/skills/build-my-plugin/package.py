#!/usr/bin/env python3
"""Zip a plugin folder into <name>.plugin (the format Cowork installs).

Usage: python3 package.py <plugin-folder> [output-dir]
Checks the manifest exists and has a valid name before packaging.
"""
import json
import re
import sys
import zipfile
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1]).resolve()
    out_dir = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else src.parent
    manifest = src / ".claude-plugin" / "plugin.json"
    if not manifest.exists():
        sys.exit(f"no manifest at {manifest}")
    m = json.loads(manifest.read_text())
    name = m.get("name", "")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or re.match(r"(claude|anthropic)-", name):
        sys.exit(f"invalid plugin name: {name!r}")
    skills = list((src / "skills").glob("*/SKILL.md"))
    if not skills:
        sys.exit("no skills/<name>/SKILL.md found")
    out = out_dir / f"{name}.plugin"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(src.rglob("*")):
            if p.is_file() and p.name != ".DS_Store" and "__pycache__" not in p.parts:
                z.write(p, p.relative_to(src))
    print(f"packaged {len(skills)} skill(s) into {out}")


if __name__ == "__main__":
    main()
