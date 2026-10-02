#!/usr/bin/env python3
"""Generate .claude-plugin/marketplace.json from lab/plugins.json.

Default: GitHub sources (each plugin in its own repo, for per-plugin traffic).
--local DIR: write a marketplace into DIR whose sources point at plugins/ on
disk, for testing with `claude plugin marketplace add DIR`.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REG = json.loads((ROOT / "lab" / "plugins.json").read_text())


def build(local):
    plugins = []
    for e in REG["plugins"]:
        mf = ROOT / "plugins" / e["slug"] / ".claude-plugin" / "plugin.json"
        if not mf.exists():
            continue
        m = json.loads(mf.read_text())
        src = (f"./plugins/{e['slug']}" if local
               else {"source": "github", "repo": f"{REG['owner']}/{e['repo']}"})
        plugins.append({
            "name": m["name"],
            "displayName": m.get("displayName", m["name"]),
            "description": m["description"],
            "version": m["version"],
            "source": src,
            "category": "development" if e["surface"] == "code" else "productivity",
            "keywords": m.get("keywords", []),
        })
    return {
        "name": REG["marketplace"],
        "owner": {"name": "Press Start Studios", "email": "brian@press-start-studios.com"},
        "metadata": {"description": "Plugins made with Plugin Creator: focused Claude plugins for industries and tools the official directory does not cover yet."},
        "plugins": plugins,
    }


if __name__ == "__main__":
    if "--local" in sys.argv:
        base = Path(sys.argv[sys.argv.index("--local") + 1]).resolve()
        base.mkdir(parents=True, exist_ok=True)
        link = base / "plugins"
        if not link.exists():
            link.symlink_to(ROOT / "plugins")
        out = base / ".claude-plugin"
        data = build(True)
    else:
        out = ROOT / ".claude-plugin"
        data = build(False)
    out.mkdir(parents=True, exist_ok=True)
    (out / "marketplace.json").write_text(json.dumps(data, indent=2) + "\n")
    print(f"wrote {out / 'marketplace.json'} with {len(data['plugins'])} plugins")
