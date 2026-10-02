#!/usr/bin/env python3
"""Write lab/studio.json (Plugin Studio's input) from lab/plugins.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
reg = json.loads((ROOT / "lab" / "plugins.json").read_text())
studio = {"owner": reg["owner"], "plugins": [
    {"name": e["slug"], "repo": e["repo"], "launched": e.get("launched"), "thresholds": e["thresholds"]}
    for e in reg["plugins"]]}
(ROOT / "lab" / "studio.json").write_text(json.dumps(studio, indent=2) + "\n")
print(f"wrote lab/studio.json ({len(studio['plugins'])} plugins, "
      f"{sum(1 for p in studio['plugins'] if p['launched'])} launched)")
