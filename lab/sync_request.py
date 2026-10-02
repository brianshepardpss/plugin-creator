#!/usr/bin/env python3
"""Copy shared/request/SKILL.md into every plugin, substituting repo and name."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = json.loads((ROOT / "lab" / "plugins.json").read_text())
src = (ROOT / "shared" / "request" / "SKILL.md").read_text()

for e in REGISTRY["plugins"]:
    d = ROOT / "plugins" / e["slug"]
    mf = d / ".claude-plugin" / "plugin.json"
    if not mf.exists():
        continue
    name = json.loads(mf.read_text()).get("displayName", e["slug"])
    out = d / "skills" / "request" / "SKILL.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(src.replace("{{REPO}}", e["repo"]).replace("{{PLUGIN}}", name))
    print("synced", e["slug"])
