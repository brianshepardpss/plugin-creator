# Runbook

## WHERE WE ARE

2026-10-02: all 13 plugins public (one repo each, releases with .plugin files,
icons). Marketplace live: `/plugin marketplace add brianshepardpss/plugin-creator`.
Site + per-plugin pages live at https://brianshepardpss.github.io/plugin-creator/
with PostHog (website only). Traction clock started 2026-10-02 for all 13
(lab/plugins.json `launched`).

Next, in order:
1. Anthropic directory submissions -- owner does these in the portal
   (claude.ai/directory/manage); answers per plugin are in lab/DIRECTORY.md.
   Max 10 per 24 h; day 1 list first. The Compliance acknowledgements are the
   owner's to accept. (Claude Code's permission check blocks Claude from
   creating these public listings itself.)
2. Community directories and awesome-list PRs: lab/seeds.csv wave 1/1b.
3. Daily traction: `python3 plugins/plugin-studio/skills/traction/collect.py lab/studio.json --html docs/traction.html`
4. Wave 2 posts from each plugin's LAUNCH.md, one at a time.

## Check everything

```
python3 lab/sync_request.py        # reinstall the shared /request skill everywhere
python3 lab/check.py               # conventions + claude plugin validate --strict, all plugins
python3 lab/check.py <slug>        # one plugin
python3 plugins/plugin-creator/skills/plugin-ship/preflight.py plugins/<slug>
```

## Run one plugin's evals (local only)

```
cd plugins/<slug> && claude plugin eval . --runs 3 -j 3 --no-publish --trust-plugin \
  --allow-tools Bash Write Edit --json evals/results/last.json
```

`--no-publish` keeps the HTML report off claude.ai.

## Try the marketplace locally

```
python3 lab/build_marketplace.py --local ~/.claude/jobs/pc-local
claude plugin marketplace add ~/.claude/jobs/pc-local
claude plugin install <slug>@plugin-creator
```

## Publish (owner approval required; public and outward-facing)

1. Commit.
2. Per plugin: `lab/publish.sh <slug> --dry-run`, then `lab/publish.sh <slug>`.
   Creates `brianshepardpss/<repo>` (public), pushes the plugin subtree, adds
   topics and the `request` label, cuts a release with the `.plugin` file,
   and sets `launched` in lab/plugins.json, which starts the day-30 clock.
3. `python3 lab/build_marketplace.py` (GitHub sources), commit, and push this
   repo to `brianshepardpss/plugin-creator`. GitHub Pages serves docs/ at
   https://brianshepardpss.github.io/plugin-creator/ .
4. Directory submissions and launch posts: per plugin LAUNCH.md. One at a
   time, owner-approved.

## Track (daily; GitHub keeps only 14 days of traffic)

```
python3 plugins/plugin-studio/skills/traction/collect.py lab/studio.json --html docs/traction.html
```

Schedule it (cron or a scheduled Claude routine) once the first plugin is
public. Day-30 memos: run `/plugin-studio:studio` in Claude Code here.

## Next ideas

`lab/radar-2026-10-02.md` ranks 46 candidates by measured gap. Re-run:

```
python3 plugins/plugin-studio/skills/radar/radar.py plugins/plugin-studio/skills/radar/candidates.md --top 20
```

## Open owner decisions

- (Done 2026-10-02) PostHog is live on the website only (US cloud, key in
  lab/site.json). Events: pageviews, `download_plugin`, `copy_install`,
  `view_source`, `open_plugin_page`, and `waitlist_signup` (email, role,
  task) from built-for-you.html. Cookieless (memory persistence, no person
  profiles). The plugins themselves have no telemetry.
