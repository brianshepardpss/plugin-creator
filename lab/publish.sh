#!/usr/bin/env bash
# Publish one plugin from plugins/<slug> to its own public GitHub repo.
# OWNER APPROVAL REQUIRED before running: this creates a public repo.
# Usage: lab/publish.sh <slug> [--dry-run]
set -euo pipefail
cd "$(dirname "$0")/.."
slug="$1"; dry="${2:-}"
owner=$(python3 -c 'import json;print(json.load(open("lab/plugins.json"))["owner"])')
repo=$(python3 -c "import json;print([p['repo'] for p in json.load(open('lab/plugins.json'))['plugins'] if p['slug']=='$slug'][0])")
desc=$(python3 -c "import json;print(json.load(open('plugins/$slug/.claude-plugin/plugin.json'))['description'][:340])")

python3 lab/check.py "$slug"
git diff --quiet HEAD -- "plugins/$slug" || { echo "commit plugins/$slug first"; exit 1; }

branch="pub/$slug"
git branch -D "$branch" >/dev/null 2>&1 || true
git subtree split --prefix "plugins/$slug" -b "$branch" >/dev/null
echo "split plugins/$slug -> $branch ($(git rev-parse --short "$branch"))"

if [[ "$dry" == "--dry-run" ]]; then echo "dry run: would push to $owner/$repo"; exit 0; fi

if ! gh repo view "$owner/$repo" >/dev/null 2>&1; then
  gh repo create "$owner/$repo" --public --description "$desc" --homepage "https://github.com/$owner/plugin-creator"
  gh api -X PUT "repos/$owner/$repo/topics" -f "names[]=claude-code-plugin" -f "names[]=claude-plugin" -f "names[]=claude-skills" >/dev/null
  gh label create request --repo "$owner/$repo" --color 5319e7 --description "Filed via the /request skill" >/dev/null 2>&1 || true
fi
git push "https://github.com/$owner/$repo.git" "$branch:main"

# Release with a .plugin file for Cowork / claude.ai users (counts as downloads in traction).
version=$(python3 -c "import json;print(json.load(open('plugins/$slug/.claude-plugin/plugin.json'))['version'])")
python3 plugins/plugin-creator/skills/plugin-ship/preflight.py "plugins/$slug" --package >/dev/null
asset="plugins/$slug/dist/$slug-$version.plugin"
gh release view "v$version" --repo "$owner/$repo" >/dev/null 2>&1 || \
  gh release create "v$version" "$asset" --repo "$owner/$repo" --title "v$version" \
    --notes "Install in Claude Code: /plugin marketplace add $owner/plugin-creator then /plugin install $slug@plugin-creator. Cowork / claude.ai: download $slug-$version.plugin and install it."

# Start the traction clock on first publish.
python3 - "$slug" <<'PY'
import datetime, json, sys
p = "lab/plugins.json"; r = json.load(open(p))
for e in r["plugins"]:
    if e["slug"] == sys.argv[1] and not e.get("launched"):
        e["launched"] = datetime.date.today().isoformat()
json.dump(r, open(p, "w"), indent=2)
PY
python3 lab/make_studio.py
echo "published https://github.com/$owner/$repo"
