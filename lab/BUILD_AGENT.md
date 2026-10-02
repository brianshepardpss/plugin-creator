# Instructions for a plugin build agent

You are building ONE Level 1 plugin in the Plugin Creator lab at
/home/admin/code/plugin-creator. Your slug, display name, surface and
research brief are given in your prompt. The goal is the best possible MVP
for real users in that domain, built the way the plugin-creator plugin
teaches.

## Read first (all of it)

1. /home/admin/code/plugin-creator/CONVENTIONS.md (hard rules; lab/check.py enforces them)
2. Your research brief in /home/admin/code/plugin-creator/research/
3. /home/admin/code/plugin-creator/plugins/plugin-creator/skills/plugin-scaffold/SKILL.md
4. /home/admin/code/plugin-creator/plugins/plugin-creator/skills/skill-writing/SKILL.md
5. /home/admin/code/plugin-creator/plugins/plugin-creator/skills/plugin-evals/SKILL.md
6. /home/admin/code/plugin-creator/plugins/plugin-creator/agents/plugin-reviewer.md

The brief is your spec. Where the brief and CONVENTIONS disagree,
CONVENTIONS wins. Where the brief is thin, do more research (web search,
fetch, gh) before guessing. Verify any API detail you rely on.

## Build

1. Scaffold:
   ```
   python3 /home/admin/code/plugin-creator/plugins/plugin-creator/skills/plugin-scaffold/scaffold.py \
     /home/admin/code/plugin-creator/plugins/<slug> --name <slug> --display "<Display>" \
     --description "<one sentence>" --author "Press Start Studios" \
     --email brian@press-start-studios.com --url https://github.com/brianshepardpss \
     --repo https://github.com/brianshepardpss/<slug> --skills <list> --surface <code|cowork> \
     --keywords <a,b,c>
   ```
   Then copy the brief to `plugins/<slug>/BRIEF.md`.
2. Fill, in the scaffold skill's order: samples, scripts (stdlib Python, test
   every one on the samples and keep the outputs), skills, commands, agents,
   optional `.mcp.json` (only to reuse an official vendor server; secrets via
   `userConfig` with `"sensitive": true`), optional `.lsp.json` (code surface
   only), README, LAUNCH.md.
3. LAUNCH.md must contain ready-to-post drafts for at least 3 specific
   channels from the brief (respecting each community's self-promo rules), a
   directory listing text, and the day-30 thresholds.
4. Evals: at least 5 cases from the brief's scenarios, including hero,
   guardrail, trigger (`tool_used` Skill with `arm: with-only`) and, if the
   plugin computes numbers, an exact-math `regex` case using values your
   scripts actually produced.
5. Do NOT write `skills/request/`. Run `python3 lab/sync_request.py` from
   the lab root to install it.
6. Delegate a review to a subagent following plugins/plugin-creator/agents/plugin-reviewer.md
   (or do the review pass yourself rigorously against that checklist) and fix
   every blocker and should-fix.

## Verify

From /home/admin/code/plugin-creator:
```
python3 lab/check.py <slug>
claude plugin validate plugins/<slug> --strict
python3 plugins/plugin-creator/skills/plugin-ship/preflight.py plugins/<slug>
```
All three must pass. Then run the evals once:
```
cd plugins/<slug> && claude plugin eval . --runs 1 -j 3 --no-publish --trust-plugin \
  --allow-tools Bash Write Edit --max-cost-usd 4 --json evals/results/last.json
```
`--no-publish` is mandatory (nothing leaves this machine). If evals cannot
run (early access, auth, missing toolchain such as dart or metals), say so
and continue. Fix failures that are the plugin's fault; report the rest.
Do not leave `evals/results/` content other than last.json.

## Boundaries

- Touch only plugins/<slug>/ (plus running lab/sync_request.py).
- No git commits, no gh repo creation, no pushes, no posts, no submissions.
- No real personal data in samples. Clearly fake names and companies.
- Plain ASCII in all files.

## Report back (under 300 words)

Skills/commands/agents built (one line each), the hero command, check and
validate results, eval scores (with vs without plugin) or why they didn't
run, any brief recommendations you overrode and why, and open risks.
