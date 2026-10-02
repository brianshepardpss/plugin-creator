# Merge Medic for GitLab

Fix red GitLab pipelines and review merge requests from Claude Code. Works
on self-managed GitLab, needs no admin toggle and no MCP server. Merge Medic
drives the official `glab` CLI you already use.

**Who it is for:** developers at GitLab shops, including self-managed and
enterprise instances behind SSO or VPN. GitHub users get `gh`-native flows in
Claude Code. On GitLab the usual result is "it looks like it works but
doesn't". This plugin fills that gap for the daily loop: red pipeline,
review, MR, review threads.

Works in: Claude Code (terminal, IDE and desktop). Needs `git`, Python 3
(standard library only) and, for live use, `glab` 1.119 or newer.

What it does not do: it can't add GitLab to Claude's cloud features (web,
Slack, routines). A local plugin has no access to those.

## Install

```
/plugin marketplace add brianshepardpss/plugin-creator
/plugin install merge-medic@plugin-creator
```

For live use, install glab (`brew install glab`, or see
https://gitlab.com/gitlab-org/cli#installation) and log in to your own host:

```
glab auth login --hostname gitlab.example.com     # your instance; token scopes: api, write_repository
```

## Try it in 60 seconds (no GitLab account)

```
/gl-fix-pipeline demo
```

This builds a small demo repo whose remote is a fictional self-managed host
(`gitlab.example-corp.test`) and uses a bundled fake `glab` that replays
recorded API responses. Merge Medic finds the 3 failed jobs in pipeline 1873:

- **unit-tests** (test): traces the two failing tests to a `max` that should
  be `min` in `late_fees.py`, fixes it, and reruns the tests locally.
- **build-image** (infra-flaky): a Docker Hub 429 pull limit. It edits no
  code and offers `glab ci retry 90414` plus the Dependency Proxy fix.
- **e2e-smoke**: a job that is allowed to fail and timed out. It is
  reported, but nothing is changed for it.

Then it asks before pushing. Logs are cut by a script before Claude reads
them. The 6,245-line OOM log in `samples/` comes down to 5 lines plus a
header.

## What it does

| Piece | Purpose |
|---|---|
| `/gl-fix-pipeline [iid\|branch\|demo]` | **Hero.** Failed jobs via `glab ci get`, finished logs via `glab api .../trace` (never the blocking `glab ci trace`), excerpted and secret-masked by `trace_excerpt.py`, classified (test, lint, build, dependency, config, infra-flaky, resource, timeout), fixed and verified locally, pushed or retried only after you say yes |
| `/gl-review [iid\|url\|demo]` | One `glab mr diff`, one reviewer subagent, line numbers computed by `diff_lines.py`, findings posted as **draft** inline comments that only you see until you publish |
| `/gl-mr` | Pushes the branch and opens a **draft** MR on your remote's host with a title and description from the commits and `Closes #N` |
| `/gl-threads` | Lists only unresolved threads, fixes what was asked, replies in-thread, and resolves only the threads it changed code for |
| SessionStart check | In a GitLab repo, prints one line if glab is missing, too old, or not logged in to *your* host. Silent otherwise |
| Confirmation guard | Asks before `glab mr merge/approve/close`, `mr note publish/delete`, `ci delete/cancel`, `glab api -X DELETE/PUT/PATCH`, `variable set`, other delete/revoke commands, and force pushes |

Skills trigger on plain requests too: "my pipeline is red", "review !42",
"open an MR for this branch, it fixes 17", "address the review comments".

## Self-managed GitLab

Merge Medic never hardcodes gitlab.com. glab picks the host from your git
remote, and `GITLAB_HOST` overrides it. A private CA works with
`glab config set ca_cert /path/ca.pem --host <host>`. The setup check and
every skill use the host from your remote.

## Privacy

Nothing is sent anywhere by the plugin itself. Commands go from your machine
to your own GitLab instance through glab, with your token. Job logs are
saved to your temp directory. Common secret formats (GitLab, AWS, npm,
GitHub and Slack tokens, auth headers, URL credentials, `*_PASSWORD=` style
variables, JWTs, private keys) are masked before log text reaches Claude;
masking is pattern-based, so treat it as a safety net. Pushes and retries
always wait for your yes. MR creation, thread replies and resolves happen
only when you asked for them in the conversation, or after you confirm.
Review comments are always drafts, and Merge Medic never publishes them,
approves or merges on its own.
There is no telemetry.

## Feedback

Say "I wish Merge Medic could..." and the request skill drafts an issue for
you to file. Nothing is sent automatically. Please mention whether you are
on gitlab.com or self-managed (the host name is not needed).

Not affiliated with or endorsed by GitLab Inc. This plugin is not
affiliated, endorsed, sponsored, or approved with or by GitLab Inc.
GitLab is a trademark of GitLab Inc. Not affiliated with or endorsed by
Docker, Inc. (mentioned for Docker Hub rate limits).
