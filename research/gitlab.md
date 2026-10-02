# Research brief: `gitlab` plugin (working name "Merge Medic for GitLab")

Date: 2026-10-02. Verified via gh CLI / docs fetch unless marked [UNVERIFIED].

## 1. Target user and jobs-to-be-done

User: developer at a GitLab shop (often self-managed, often enterprise) using Claude Code locally, who sees GitHub users get `gh`-native flows (/code-review, PR status, Slack, web) and GitLab users get "it looks like it works but doesn't".

Demand evidence:
- anthropics/claude-code#12346 "Add GitLab Integration": 150 reactions (140 +1, 10 rocket), 54 comments, open since 2025-11-25, still getting +1s on 2026-09-30. Quote: "media organization running 60+ AWS accounts with GitLab as our core SCM ... the GitHub-only integration is the single biggest gap."
- #21527 GitLab for Slack integration: 44 reactions. #70565 Claude Tag self-managed GitLab: 12. #44544 ultraplan GitLab: 11. NOTE: much of the 150 is about cloud surfaces (web, Slack, routines, Tag) a local plugin cannot fix. Say so honestly in positioning.
- #26932 + open PR #34951: GitLab support for /code-review (unmerged). Comment on #12346 (2026-08-10): pointing /code-review at a self-managed MR URL "doesn't error out", spawned "20 subagents, 786 API calls, 72.5M cache-read tokens ... exhausted the full 5-hour usage window" because there is no `glab mr diff` path.
- #54660: official plugin "hardcodes https://gitlab.com/api/v4/mcp ... self-hosted cannot use the plugin without manually patching the plugin cache" (auto-closed, unresolved).
- #17209 (12 reactions, 11 comments): official plugin "Failed to reconnect to plugin:gitlab:gitlab"; commenter: "claude-code is great at using the glab cli tool. Just give it a token."
- #95179 (2026-09-17): official MCP job-log tool "returns {}" on self-managed CE while other tools work. #59187/#55954: OAuth "scope is invalid" with GitLab MCP.

Ranked JTBD (pain x frequency):
1. Red pipeline on my MR -> find the failing job, read the right 50 lines of a 20k-line log, fix, push. (Daily; log-reading is the pain; official MCP job-log is flaky per #95179.)
2. Review an MR (mine or a teammate's) cheaply and post inline comments as draft notes. (Daily; #34951/#26932, cost blowup above.)
3. Create/update an MR from the current branch with a good description, linked issue, labels, reviewers. (Daily, low pain once glab is set up.)
4. Address unresolved MR discussions: fetch threads, fix, reply, resolve. (Several times a week.)
5. Issue -> branch -> MR. (Weekly.)
6. Work on self-managed instances behind SSO/VPN. (Cross-cutting; this is the main blocker for the official plugin.)

## 2. Competition

| Option | What it is | Gap |
|---|---|---|
| `gitlab@claude-plugins-official` (authored "GitLab") | Only `.mcp.json` -> `https://gitlab.com/api/v4/mcp`; no skills/commands/hooks | gitlab.com only (#54660); requires group/instance admin to enable MCP; OAuth reconnect bugs; no workflows |
| GitLab MCP server (official, Beta) | ~45 tools incl. get_merge_request, save_merge_request_review, get_job (trace), get_pipeline | Admin opt-in, Free tier 60 req/min on MCP endpoint, self-managed needs 18.3+ (Free tier since 19.2), raw tools not workflows |
| `glab skills install` (glab v1.120.0, EXPERIMENTAL, since ~2026-05) | Bundled 320-line `glab` SKILL.md + `glab-stack` into `.agents/skills/` | Reference card, not workflows; no log triage, no review flow; not a Claude plugin |
| `glab mcp serve` | stdio MCP in glab, EXPERIMENTAL | "not ready for production use" |
| zereight/gitlab-mcp | Community MCP, 2,020 stars, 266 tools, PAT/OAuth/self-hosted, read-only mode | Tool sprawl (context cost), no opinionated workflows, npx supply chain |
| jmrplens/gitlab-mcp-server (42), yoda-digital (64), ttpears (11) | Community MCPs | Same |
| fprochazka/claude-code-plugins `glab` (15 stars) | Real Claude plugin: glab skill, mr-status, mr-watch agent | Requires 3 marketplaces + 2 extra uv tools; MR-status focused |
| henricook/claude-glab-skill (74 stars, last push 2025-11) | Single skill | Stale, no CI triage |
| GitKraken plugin (official marketplace) | Multi-forge git context | Generic, account-gated |
| Claude Code native (v2.1.232-233, Aug 2026) | `--worktree <MR URL>`, `!N` labels, glpat redaction, glab config protection, GitLab marketplaces | No /code-review, no CI, no MR create |
| Claude Code GitLab CI/CD (Beta, maintained by GitLab) | @claude in MRs via CI job | Server-side, needs runner + API key; not local |
| GitLab Duo Agent Platform | Native agents/flows, Credits $1 each; Premium $29/user incl. 12 credits | Paid, not Claude Code, users already chose Claude |

Gap to own: a self-managed-first, glab-backed, workflow plugin for CI triage + MR review with low token cost.

## 3. Technical integration facts

glab (gitlab.com/gitlab-org/cli, mirror gitlabhq/cli; latest tag v1.120.0):
- Install: `brew install glab` (official); others community-supported.
- Auth: `glab auth login` (interactive), `--web` OAuth, `--device` (GitLab 17.9+), `--stdin` or `--token` PAT, `--hostname gitlab.example.com` for self-managed, `--job-token $CI_JOB_TOKEN` in CI. Env: `GITLAB_TOKEN`/`GITLAB_ACCESS_TOKEN`/`OAUTH_TOKEN`, `GITLAB_HOST`. Host auto-resolved from git remotes. Multiple instances supported.
- PAT scopes per glab docs: `api`, `write_repository`. (OAuth: openid, profile, read_user, write_repository, api.) Read-only mode possible with `read_api` [UNVERIFIED for all commands].
- Key commands: `glab ci get --merge-request <iid> --with-job-details -F json`, `glab ci get -p <id> -s failed`, `glab api projects/:id/jobs/<job-id>/trace` (finished log; `glab ci trace` STREAMS and blocks - avoid in agents), `glab ci retry <job-id>` (job ID, not pipeline), `glab ci lint`, `glab mr create --push --title --description`, `glab mr view <iid> --unresolved -F json`, `glab mr diff <iid>`, `glab mr note create <iid> --file <path> --line <n> --draft --unique`, `glab mr note publish`, `glab mr note resolve`, `glab mr note create --reply <discussion-id>`.

Official MCP server: `https://<host>/api/v4/mcp`, HTTP transport, OAuth 2.0 DCR (or pre-registered app with `mcp` scope, non-confidential); Beta; Free/Premium/Ultimate; .com/self-managed/Dedicated; must be enabled per top-level group (.com) or instance. Claude Code: `claude mcp add -s user --transport http GitLab https://<host>/api/v4/mcp`. Limits on .com: MCP endpoint 60/min Free, 600/min Premium+; DCR 10 registrations/hour/IP.

GitLab.com REST limits: authenticated 2,000 req/min/user (tier-aware limits proposed, not enforced); note creation 60/min; pipeline creation 25/min per project/user/commit. Self-managed: admin-defined.

Build vs reuse: REUSE glab as the transport (no own MCP server). Do not bundle the official MCP by default; document it as optional for teams that already enabled it.

## 4. Recommended MVP

Hero workflow (<5 min): on a branch with a red MR pipeline, user types `/gl-fix-pipeline`. Plugin resolves MR from current branch, lists failed jobs (JSON), fetches each trace, runs a local extractor script that strips ANSI/section markers and keeps the first error block + last 80 lines (traces are often 10k+ lines), classifies (test failure / lint / dependency / infra-flaky / config), proposes and applies a fix, runs the job's script locally where possible, and offers `git push` (or `glab ci retry <job-id>` for flaky/infra). Output: one-paragraph root cause per job with the log excerpt cited.

Components:
1. `skills/gitlab-ci-triage` (+ `scripts/trace-excerpt.py`): failed-job discovery, trace fetch, excerpting, classification. Hero.
2. `commands/gl-fix-pipeline`: entry point for the hero.
3. `skills/gitlab-mr-review` + `agents/mr-reviewer`: fetch `glab mr diff` once, review in one subagent (cost guard vs. the 72M-token failure), post findings as `--draft --unique` inline notes, never auto-publish; user runs publish.
4. `commands/gl-mr`: create/update MR from branch: push, title from commits, description template, `Closes #N`, draft by default.
5. `skills/gitlab-mr-threads`: list `--unresolved` discussions, fix, reply, resolve with confirmation.
6. Hook SessionStart: if `origin` is non-GitHub and `glab` missing/unauthed, print one-line setup hint (host-aware command). No network calls beyond `glab auth status`.
7. Hook PreToolUse (Bash): require confirmation for `glab mr merge`, `glab mr approve`, `glab ci delete`, `glab api -X DELETE|PUT`, `glab mr note publish`.

MCP decision: none bundled. Reasons: admin opt-in, OAuth bugs, .com-hardcoding precedent, Free-tier 60/min, job-log bug #95179. glab inherits Claude Code's native glpat redaction and config protection.

Fixtures: recorded `glab ci get -F json` payloads and traces (pytest assertion, eslint, npm ERESOLVE, Docker Hub 429 pull limit, OOM-killed runner, job timeout, YAML `ci lint` error); MR diff + discussions JSON; a fake `glab` shim on PATH replaying fixtures for deterministic evals; plus a live public test project on gitlab.com with a deliberately failing pipeline.

Deliberate omissions: cloud surfaces (web, Slack, Tag, routines - not pluggable); Duo integration; issues/epics/wikis beyond `Closes #N`; security dashboards; merge/approve automation; running a webhook bot; own MCP server.

## 5. Eval scenarios

1. "My pipeline on this MR is red, fix it." (fixture: pytest failure in job 3 of 7) Pass: calls `ci get` with failed filter, fetches only failed job traces, never runs `glab ci trace` (blocking), names the failing test + file:line, edits that file, local test passes.
2. "Why did build-image fail?" (fixture: Docker Hub 429) Pass: classifies infra/flaky, makes no code edits, suggests `glab ci retry <job-id>` with job ID (not pipeline ID) and a mirror/registry fix.
3. "Review !42 and leave comments." Pass: exactly one `glab mr diff` fetch, at most 1 subagent, comments created with `--draft`, no `note publish` without confirmation, total tokens under a set budget (e.g. 300k).
4. "Open an MR for this branch against main, it fixes issue 17." (self-managed host fixture) Pass: uses remote-resolved host (not gitlab.com), pushes, description contains `Closes #17`, MR created as draft.
5. "Address the unresolved review threads." Pass: lists only unresolved discussions, replies with `--reply <id>`, resolves only threads it changed code for, PreToolUse hook fires before any publish.

## 6. Distribution

- Comment (once, helpful, with install line) on #12346, #26932/#34951, #54660, #17209, #95179; GitLab forum (forum.gitlab.com, AI/Duo and CI categories); gitlab-org/cli issues about agents/skills.
- Reddit: r/gitlab, r/ClaudeAI, r/ClaudeCode, r/devops, r/selfhosted (self-managed angle).
- HN Show HN (self-managed + token-cost angle); newsletters: DevOps Weekly, TLDR DevOps, Console.dev [submission policies UNVERIFIED]; community directories: claudepluginhub.com, claudedirectory.org, awesome-claude-code lists.
- Positioning: "Fix red GitLab pipelines and review MRs from Claude Code - works on self-managed, no admin toggle, no MCP."
- Name: trademark rules (GitLab handbook trademark guidelines) forbid "GitLab" as first word in plugin names; only "... for GitLab" or "GitLab Compatible"; listing must state "This plugin is not affiliated, endorsed, sponsored, or approved with or by GitLab Inc." So slug `gitlab` is out (also collides with official `gitlab`). Proposed: "Merge Medic for GitLab", slug `merge-medic` (npm free; tiny unrelated GH repos). Alt: "Pipefix for GitLab" / `pipefix`. Avoid "Tanuki" (GitLab mascot/logo) and the logo.

## 7. Risks

- Trademark: see naming rules + disclaimer; no logo, no orange tanuki palette.
- Platform risk: Anthropic merges #34951 or ships native GitLab /code-review; GitLab promotes `glab skills` to GA with workflow skills. Mitigation: CI triage depth + self-managed is the moat; keep review skill thin.
- glab flag drift (fast release cadence, v1.120); `glab mr note --draft/--file/--line` relatively new - pin minimum glab version and check in SessionStart [minimum version UNVERIFIED].
- Old self-managed instances (<16.x) lack some endpoints/draft-notes behaviour [UNVERIFIED].
- Secrets in job traces: excerpt script must mask tokens (glpat-, glrt-, AWS keys) before printing; Claude Code redacts glpat/glrt natively but not all.
- Rate limits: 60 notes/min on .com - batch review comments, cap per run.
- Destructive ops on shared MRs: PreToolUse guard; drafts only.
- Windows: glab via winget/scoop community; Python excerpt script dependency (keep stdlib-only or do it in bash/awk).

## 8. Day-30 traction signal

Primary: count of distinct self-managed hosts in opt-in `/request` feedback or issue reports (target: 5+ different non-gitlab.com hosts) - proves the wedge the official plugin cannot serve. Secondary: thumbs/replies on our comment in #12346 and GitHub stars >= 50 (henricook's stale skill reached 74). Kill signal: under 10 installs-reported or all usage on gitlab.com only (then the official plugin + glab skill already suffice).

Sources: github.com/anthropics/claude-code/issues/12346, /21527, /26932, /pull/34951, /54660, /17209, /95179; github.com/anthropics/claude-plugins-official external_plugins/gitlab; docs.gitlab.com/user/model_context_protocol/mcp_server/ and mcp_server_tools/; docs.gitlab.com/user/gitlab_com/rate_limits/; gitlabhq/cli docs (auth/login, authentication.md, ci/trace, mcp/serve, skills/install, mr/note/create); code.claude.com/docs/en/gitlab-ci-cd and /whats-new/2026-w33; about.gitlab.com/blog/claude-code-and-gitlab/; handbook.gitlab.com trademark guidelines (via search summary); fprochazka/claude-code-plugins; zereight/gitlab-mcp.
