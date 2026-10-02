# Plugin Creator conventions

Every plugin in this repo follows these rules. `python3 lab/check.py` enforces
the mechanical ones; reviewers enforce the rest. Verified against Claude Code
2.1.287 on 2026-10-02.

## Layout

```
plugins/<slug>/
  .claude-plugin/plugin.json   manifest (only file in .claude-plugin/)
  README.md                    install, hero workflow, demo, privacy, not-affiliated line
  skills/<skill>/SKILL.md      one directory per skill; supporting files beside it
  skills/request/SKILL.md      the shared opt-in feedback skill (copied verbatim, see below)
  commands/*.md                optional slash commands
  agents/*.md                  optional subagents
  .mcp.json                    optional; {"mcpServers": {...}}
  .lsp.json                    optional; Claude Code only
  evals/<case>/prompt.md       at least 3 cases; graders in evals/<case>/graders/*.md
  samples/                     fixture data so the hero workflow runs with no account
  LAUNCH.md                    positioning, channels, post drafts, day-30 signal
```

## Manifest

- `name` is kebab-case, never starts with `claude-`, `anthropic-` or `cc-plugin-`,
  and never uses a third-party trademark as the leading word.
- Required by our check: `name`, `displayName`, `version`, `description`,
  `author` {name, email, url}, `homepage`, `repository`, `license` (MIT),
  `keywords`.
- `skills` is `["./skills/"]`. Never declare `"./"`: it overlaps `evals/`.
- `author`: `{"name": "Press Start Studios", "email": "brian@press-start-studios.com", "url": "https://github.com/brianshepardpss"}`.
- `repository`/`homepage`: `https://github.com/brianshepardpss/<repo>`, where
  `<repo>` is the published repo name recorded in `lab/plugins.json`.
- Secrets come from `userConfig` with `"sensitive": true` and are referenced as
  `${user_config.<key>}`. Never ask the user to paste keys into chat.
- Must pass `claude plugin validate plugins/<slug> --strict`.

## The MVP bar

1. Installs with one command.
2. One hero workflow that works end to end in under 5 minutes, on bundled
   `samples/` with no account, key or paid tool. Connector plugins also work
   live once a key is configured.
3. Skill descriptions say WHEN to trigger, with the phrases a real user would
   type. Bodies are procedures, not essays. Long reference material goes in
   files beside SKILL.md and is read on demand.
4. Any numbers the plugin produces (costs, percentages, dates) are computed by
   a bundled script or shown with working, never estimated in prose.
5. Guardrails from the research brief's risk section are written into the
   skills that need them (for example, Fair Housing checks, allergen
   disclaimers, AEDT rules).
6. Non-developer plugins (industry and SaaS) must work in Cowork and claude.ai:
   skills, agents and remote MCP only; no `bin/`, no LSP, no local-only
   executables in the hero path. Bundled Python scripts are fine (Cowork runs
   code), but they must use the standard library only.
7. README states: what it is, who it is for, the 60-second install, the hero
   workflow, what data leaves the machine (normally none), and
   "Not affiliated with or endorsed by <vendor>." for every vendor named.

## The /request skill (opt-in feedback)

Every plugin ships `skills/request/SKILL.md`, a byte-identical copy of
`shared/request/SKILL.md` with only `{{REPO}}` and `{{PLUGIN}}` substituted.
It never sends anything itself. It drafts a feature request, shows the user
the exact text, and gives them a prefilled GitHub issue link to open
themselves. No telemetry anywhere, ever, unless a future owner decision adds
an opt-in mechanism.

## Tracking

Each plugin is published as its own GitHub repo (`lab/publish.sh <slug>`) so
GitHub traffic, stars, clones and issues are measurable per plugin. The
monorepo is the source of truth; published repos are build outputs.

## Naming

Product names are generic and descriptive. Vendor names appear only in
descriptive phrases ("for Pipedrive users"), never as the brand.
