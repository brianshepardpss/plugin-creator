# Launch plan: Merge Medic for GitLab

Nothing here is posted without the owner's explicit yes, each time.

## Positioning

One line: **Fix red GitLab pipelines and review MRs from Claude Code. Works
on self-managed, needs no admin toggle and no MCP.**

Wedge: the official `gitlab` plugin is a bare `.mcp.json` that points at
gitlab.com, needs an admin opt-in, and has OAuth and job-log bugs
(#54660, #17209, #95179). Merge Medic runs on the `glab` CLI that GitLab
users already trust, with workflows rather than raw tools: log triage with
a trimming script, a one-subagent draft-only review (vs. the reported
72.5M-token /code-review blowup), MR creation and thread resolution.

What we say up front: much of the demand in #12346 is about cloud surfaces
(web, Slack, Tag, routines). A local plugin cannot fix those, and we say so
in every post.

## Audience and where they are

- anthropics/claude-code issues: #12346 (150 reactions), #26932 / PR #34951,
  #54660, #17209, #95179
- forum.gitlab.com (AI / Duo and CI/CD categories)
- gitlab-org/cli issues about agents and skills
- Reddit: r/gitlab, r/ClaudeAI, r/ClaudeCode, r/devops, r/selfhosted
- Hacker News (Show HN)
- Newsletters: DevOps Weekly, TLDR DevOps, Console.dev (check each
  submission policy before sending)

## Directory listing text

> **Merge Medic for GitLab** - Fix red GitLab pipelines and review merge
> requests from Claude Code through the glab CLI. Finds failed jobs, trims
> 10k-line logs to the lines that matter (secrets masked), classifies the
> failure, fixes it and pushes after you confirm. MR review posts draft
> comments only; MR creation links issues; review threads get fixed,
> answered and resolved. Works on gitlab.com and self-managed GitLab with no
> MCP server or admin toggle. Try it with no account: `/gl-fix-pipeline demo`.
> This plugin is not affiliated, endorsed, sponsored, or approved with or by
> GitLab Inc.

Targets: own marketplace (brianshepardpss/plugin-creator), Anthropic plugin
directory, claudepluginhub.com, claudedirectory.org, awesome-claude-code
lists. Keywords: gitlab, glab, ci, pipeline, merge-request, code-review,
self-managed, devops.

## Post drafts

### 1. GitHub comment on anthropics/claude-code#12346 (one comment, once)

Norms: issue threads are for the feature request. Post once. Be useful
without the link, disclose authorship, and do not +1-bump.

> For anyone stuck on the local side of this (not web/Slack/routines, which a
> plugin can't touch): I built a Claude Code plugin on top of `glab` that
> covers the daily loop on GitLab, including self-managed hosts. It doesn't
> hardcode gitlab.com, needs no MCP or admin toggle, and uses your existing
> `glab auth login --hostname <host>`.
>
> - `/gl-fix-pipeline`: finds failed jobs, pulls the finished log with
>   `glab api .../trace` (not the blocking `glab ci trace`), trims it with a
>   script (masks glpat/AWS keys), classifies test vs. flaky infra, fixes, and
>   asks before pushing or retrying
> - `/gl-review`: one `glab mr diff`, one subagent, draft inline comments only
> - `/gl-mr`, `/gl-threads`: draft MR with `Closes #N`; fix and resolve threads
>
> `/gl-fix-pipeline demo` runs on bundled fixtures with no account.
> Install: `/plugin marketplace add brianshepardpss/plugin-creator` then
> `/plugin install merge-medic@plugin-creator`. Disclosure: I made it. It is
> not affiliated with GitLab Inc. Issues welcome, especially from
> self-managed instances.

Shorter variants for #26932/#34951 (review cost angle), #54660
(self-managed angle) and #17209/#95179 (MCP reconnect and job-log bugs):
one paragraph each, same disclosure, and only where the plugin answers that
issue's problem.

### 2. r/gitlab (text post)

Norms: read the sidebar rules first. Disclose authorship, keep it a text
post with substance, reply to comments, and post once.

> **Title:** Claude Code + self-managed GitLab: a glab-based plugin for red
> pipelines and MR reviews (no MCP, no admin toggle)
>
> Claude Code's built-in flows are GitHub-first, and the official GitLab
> plugin needs the MCP endpoint enabled by an admin and points at
> gitlab.com. I wanted the daily loop on our self-managed instance, so I
> built it on `glab`:
>
> - red pipeline: failed jobs -> finished trace via the API -> a script cuts
>   the log to the failing block plus tail (a 6k-line OOM log becomes about 5
>   lines) and masks tokens -> classify -> fix -> push only after you say yes.
>   Flaky infra such as Docker Hub 429s gets `glab ci retry <job-id>`, not
>   code edits.
> - MR review: one diff fetch, one reviewer, comments posted as drafts that
>   only you see until you publish
> - draft MR creation with `Closes #N`, and fixing and resolving review threads
>
> `/gl-fix-pipeline demo` runs on recorded fixtures, so you can see it
> without pointing it at your instance. Source and install:
> github.com/brianshepardpss/merge-medic. Disclosure: I made it. It is not
> affiliated with GitLab Inc. I'd especially like to hear from people on
> older self-managed versions where things break.

### 3. Show HN

Norms: "Show HN" only for something people can try. Write plain text, skip
the marketing adjectives, and stay to answer questions.

> **Title:** Show HN: Merge Medic - fix red GitLab pipelines from Claude
> Code (works on self-managed)
>
> Claude Code works well with GitHub through gh. GitLab users mostly get
> an MCP endpoint that needs an admin opt-in and assumes gitlab.com. Merge
> Medic is a plugin built on glab instead. It finds failed jobs, fetches
> finished logs, trims them with a small stdlib script (ANSI/section markers
> stripped, secrets masked, polling spam collapsed), classifies the failure,
> and fixes code failures or proposes a retry for infra ones. It never pushes,
> retries, merges or publishes without asking. A PreToolUse hook also asks
> before destructive glab commands.
>
> Token cost was a design goal. One reported attempt to point /code-review at
> a self-managed MR burned 72.5M cache-read tokens. Here a review is one diff
> fetch and one subagent, and comments are posted as drafts.
>
> You can try it without a GitLab account: `/gl-fix-pipeline demo` runs
> against a fake glab that replays recorded responses. MIT. Not affiliated
> with GitLab Inc.

### 4. r/selfhosted (only if its self-promotion rules allow it that week)

> **Title:** For self-hosted GitLab users on Claude Code: pipeline-fix and
> MR-review plugin that talks to your instance via glab
>
> Short version of the r/gitlab post, with the angle on what runs locally.
> Nothing goes anywhere except your own GitLab via your own token. There is
> no MCP endpoint to enable and no telemetry. A private CA works with
> `glab config set ca_cert`.

### 5. forum.gitlab.com (CI/CD category)

> **Title:** Using Claude Code with self-managed GitLab CI: a glab-based
> workflow for failed jobs
>
> A how-to framed post: the glab commands that work well for agents
> (`glab ci get --merge-request N --status failed -F json`,
> `glab api projects/:id/jobs/<id>/trace`, and why to avoid `glab ci trace`
> in agents), then a link to the plugin as one packaged version of the
> workflow. Disclose authorship and the not-affiliated line.

## Day-30 signal (thresholds fixed in lab/plugins.json, never lowered)

| Metric | Threshold at day 30 | Source |
|---|---|---|
| Unique cloners of brianshepardpss/merge-medic | 150 | GitHub traffic |
| GitHub stars | 40 | GitHub |
| Feature requests or issues via /request | 5 | GitHub issues with the `request` label |

Wedge check (from the brief): at least 5 issues or requests that mention
self-managed use. That shows the plugin serves users the official plugin
cannot. Secondary signal: reactions and replies to the #12346 comment.

Kill or rethink: under 10 installs reported, or all usage on gitlab.com only
(then the official plugin plus `glab skills` cover the need). Watch for
platform risk: if PR #34951 merges or GitLab ships workflow skills in
`glab skills`, narrow to CI triage depth and self-managed.
