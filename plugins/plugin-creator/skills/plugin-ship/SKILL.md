---
name: plugin-ship
description: Use when a Claude plugin is built and the user wants to release it, or says "publish my plugin", "ship it", "make a marketplace", "submit to the plugin directory", "write launch posts", or "how do I get people to use my plugin". Runs preflight checks, packages a .plugin file, sets up a marketplace, prepares directory submissions and launch posts, and sets up traction tracking.
---

# Ship a plugin and measure whether anyone wants it

Publishing is public and hard to undo. Prepare everything, show the user the
exact list of outward actions, and do each one only after they say yes.

## 1. Preflight

```
python3 <this skill dir>/preflight.py <plugin-dir> --package
```

Fix every ERROR. Warnings block directory review, so fix those too unless
the user decides otherwise. `--package` writes `dist/<name>-<version>.plugin`,
a zip that Cowork and claude.ai users can install directly; attach it to the
GitHub release.

Then give it an icon BEFORE any directory submission. The directory takes
`.claude-plugin/icon.png` only the first time the plugin is saved or
submitted in the developer portal, and never updates it after that:

```
python3 <this skill dir>/make_icon.py <plugin-dir> --text "AB" --color "#0f766e" --accent "#5eead4"
```

(Needs Pillow. Any square PNG of 512-2048 px under 2 MB works if you have a
designed one.)

## 2. One repo per plugin

Give each plugin its own public GitHub repository. GitHub reports views,
unique cloners, stars and issues per repo, so this is what makes per-plugin
traction measurable. Add topics `claude-code-plugin`, `claude-plugin`,
`claude-skills`, and a `request` label for feedback issues.

## 3. A marketplace

A marketplace is a repo with `.claude-plugin/marketplace.json`:

```json
{
  "name": "<marketplace-name>",
  "owner": {"name": "<you>", "email": "<email>"},
  "plugins": [
    {"name": "<plugin>", "description": "<one line>", "version": "0.1.0",
     "source": {"source": "github", "repo": "<owner>/<plugin-repo>"}}
  ]
}
```

Users then run `/plugin marketplace add <owner>/<marketplace-repo>` and
`/plugin install <plugin>@<marketplace-name>`. Validate it with
`claude plugin validate <marketplace-dir>`.

## 4. Directories

Prepare, and submit only with the user's go-ahead:

- Anthropic plugin directory, through the developer portal at
  https://claude.ai/directory/manage (Pro, Max, Team or Enterprise; GitHub
  connected on claude.ai with push access to the repo). One submission per
  plugin folder, at most 10 per organization per 24 hours. The portal's
  Validate step blocks on: no README of 40+ words, no license, files outside
  the plugin folder, unpinned npx/uvx launchers, credentials in files. It
  holds for a human reviewer: any non-image binary (PDF, zip), any file over
  256 KiB, more than 512 files, generic or brand-like names. Keep samples as
  text to avoid a hold on every version. A listing reaches claude.ai, Cowork,
  the mobile apps and Claude Code, and its Usage tab shows installs and how
  often each skill runs -- the best traction data you can get.
- Community directories: claudemarketplaces.com, claude-plugins.dev,
  claudepluginhub.com, buildwithclaude.com.
- If the plugin includes its own MCP server: the official MCP registry and
  Smithery.

For each, draft the listing text: name, one-line pitch, three bullet
outcomes, install command, screenshot or GIF description.

## 5. Launch posts

Use LAUNCH.md. Write one post per community, in that community's norms:
lead with the problem in their words, show the hero workflow output, link
once, disclose that you made it. Many practitioner subreddits ban
self-promotion; read the rules first and prefer answering an existing
"is there a tool for X" thread. For a plugin that answers a GitHub feature
request, leave one comment on that issue with the install command; do not
spam related issues.

Tag every link with `?utm_source=<channel>&utm_campaign=<plugin>` so the
channel that worked is visible.

## 6. Tracking

From day one, record daily (GitHub keeps traffic for only 14 days):

```
gh api repos/<owner>/<repo>/traffic/views
gh api repos/<owner>/<repo>/traffic/clones
gh api repos/<owner>/<repo>  --jq '{stars: .stargazers_count, forks: .forks_count, issues: .open_issues_count}'
```

The plugin-studio plugin automates this across a portfolio. Write the day-30
threshold from the brief into the release notes so the decision is made
against a number chosen in advance.
