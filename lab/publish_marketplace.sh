#!/usr/bin/env bash
# Publish this repo as the marketplace (brianshepardpss/plugin-creator) with
# GitHub Pages on /docs. OWNER APPROVAL REQUIRED (public).
set -euo pipefail
cd "$(dirname "$0")/.."
owner=$(python3 -c 'import json;print(json.load(open("lab/plugins.json"))["owner"])')
python3 lab/build_marketplace.py
python3 lab/build_site.py
claude plugin validate . >/dev/null
git add -A && git commit -q -m "Update marketplace and site" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || true
if ! gh repo view "$owner/plugin-creator" >/dev/null 2>&1; then
  gh repo create "$owner/plugin-creator" --public \
    --description "Claude plugins for the gaps in the official directory, plus the plugin that builds them. Marketplace: /plugin marketplace add $owner/plugin-creator" \
    --homepage "https://$owner.github.io/plugin-creator/"
  gh api -X PUT "repos/$owner/plugin-creator/topics" -f "names[]=claude-code-plugin" -f "names[]=claude-plugin-marketplace" -f "names[]=claude-skills" -f "names[]=claude-plugin" >/dev/null
fi
git push "https://github.com/$owner/plugin-creator.git" main
gh api "repos/$owner/plugin-creator/pages" >/dev/null 2>&1 || \
  gh api -X POST "repos/$owner/plugin-creator/pages" -f "source[branch]=main" -f "source[path]=/docs" >/dev/null
echo "marketplace: https://github.com/$owner/plugin-creator  site: https://$owner.github.io/plugin-creator/"
