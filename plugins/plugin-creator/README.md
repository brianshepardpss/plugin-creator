# Plugin Creator

Go from a one-sentence idea to a published, tested Claude plugin, and find
out whether anyone wants it.

Most plugin tooling stops at the scaffold. Plugin Creator covers the whole
path: measure demand with live data, write a design brief, scaffold a plugin
that passes strict validation, write skills that actually trigger, prove them
with evals against a no-plugin baseline, package a `.plugin` file for Cowork
and claude.ai, and prepare directory listings, launch posts and traction
tracking.

Works in: Claude Code (the scripts need Python 3; the demand scan uses
`gh` if you are logged in, for higher GitHub rate limits).

## Install

```
/plugin marketplace add brianshepardpss/plugin-creator
/plugin install plugin-creator@plugin-creator
```

## Try it in 60 seconds

```
/plugin-creator:new a plugin that turns restaurant invoices into plate costs
```

Or just ask: "is there demand for a Claude plugin for Bitbucket?"

## What it does

| Piece | Purpose |
|---|---|
| `/plugin-creator:new <idea>` | Runs the whole pipeline with two check-ins: after the brief, and before anything is published |
| plugin-brief skill | Live demand scan (GitHub issue reactions on the Claude repos, Hacker News, official plugins, Smithery, npm) plus user research, written up as BRIEF.md |
| plugin-scaffold skill | Strict-valid skeleton from a script, then samples, scripts, skills, README and launch plan in the right order |
| skill-writing skill | How to write descriptions that trigger, procedures that give consistent output, scripts for any number a user acts on, guardrails as steps |
| plugin-evals skill | Hero, exact-math, guardrail and trigger cases for `claude plugin eval`, with the no-plugin baseline |
| plugin-ship skill | Preflight checks, `.plugin` packaging, marketplace setup, directory listings, launch posts, daily traction tracking |
| plugin-reviewer agent | Adversarial review against the brief before you ship |

## Made with Plugin Creator

Every plugin in the [plugin-creator marketplace](https://github.com/brianshepardpss/plugin-creator)
was built with this pipeline, briefs and evals included. They are the worked
examples.

## Privacy

The demand scan calls public APIs (GitHub, Hacker News, Smithery, npm,
raw.githubusercontent.com) with your search terms. Nothing else leaves your
machine, and nothing is published without your explicit yes.

## Feedback

Say "I wish this could..." and the request skill drafts an issue for you to
file. Nothing is sent automatically.

Not affiliated with or endorsed by Anthropic.
