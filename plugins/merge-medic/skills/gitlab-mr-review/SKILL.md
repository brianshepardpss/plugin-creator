---
name: gitlab-mr-review
description: Use when the user wants a GitLab merge request reviewed, or says "review !42", "review this MR", "look over my merge request", "code review on GitLab", "leave comments on the MR", "review my teammate's MR" or pastes a /-/merge_requests/ URL. Fetches the diff once with glab, reviews it in a single subagent pass with a token budget, and posts findings as draft (pending) inline comments that only the user sees until they publish. Never publishes, approves or merges. Works on self-managed GitLab.
---

# Review a GitLab merge request cheaply, as drafts

`<skill>` means this skill's base directory. Demo mode (user said "demo" or
"sample", or there is no GitLab repo): follow step 0 of the gitlab-ci-triage
skill to create the demo project, then review MR `42` with the fake glab.

## 1. Resolve the MR and check glab

1. Target: an IID (`!42` or `42`), a URL
   (`https://<host>/<group>/<project>/-/merge_requests/<iid>`: pass the
   project URL as `-R` so its host is used), or the current branch.
2. Host comes from the remote or the URL; never default to gitlab.com.
   `glab auth status --hostname <host>` must pass, else give
   `glab auth login --hostname <host>` and stop.
3. `glab --version` must be 1.119.0 or newer for draft comments. If older,
   say so, offer to show the review in chat only, and suggest upgrading.

## 2. Fetch once

```
mkdir -p "${TMPDIR:-/tmp}/merge-medic"
glab mr view <iid> -F json > "${TMPDIR:-/tmp}/merge-medic/mr.json"
glab mr diff <iid> --raw > "${TMPDIR:-/tmp}/merge-medic/mr.diff"
python3 <skill>/scripts/diff_lines.py "${TMPDIR:-/tmp}/merge-medic/mr.diff" --summary
```

Exactly one `glab mr diff` per review. No per-file API calls, no fetching
every commit, no web fetches of the MR page.

If the summary says OVER BUDGET (default 1,500 changed lines), ask the user
which files matter, or review the files in batches with the same single
subagent. Lockfiles, minified and vendored files are skipped automatically.

## 3. Annotate and review in ONE subagent

```
python3 <skill>/scripts/diff_lines.py "${TMPDIR:-/tmp}/merge-medic/mr.diff" > "${TMPDIR:-/tmp}/merge-medic/mr.annotated.txt"
```

Launch exactly one `mr-reviewer` subagent (from this plugin). Give it the
annotated diff path, the mr.json path, and the repo root if the local
checkout is at the MR head (`git rev-parse HEAD` equals
`diff_refs.head_sha` in mr.json); otherwise tell it to review the diff
alone. Never launch one agent per file. If subagents are unavailable,
apply the rubric in `<skill>/../../agents/mr-reviewer.md` yourself.

## 4. Check every finding before posting

- An inline comment needs a NEW line number that the annotated diff shows
  on a `+` or unchanged line of that file (or `--old-line` for a `-` line).
  Anything else becomes a file-level comment (`--file` with no `--line`) or
  goes in the summary. GitLab rejects lines outside the hunks.
- At most 15 comments. Drop nits first. Merge duplicates.
- Re-run safety: list existing drafts with
  `glab api projects/:id/merge_requests/<iid>/draft_notes` and skip any
  finding whose body is already there.

## 5. Post as drafts

Post only if the user asked for comments to be left on the MR (that request
is the go-ahead: drafts are visible only to them and can be edited or
deleted). Otherwise show the findings and ask "Post these N as draft
comments?".

```
glab mr note create <iid> --draft --file <path> --line <NEW> -m "<body>"
glab mr note create <iid> --draft --file <path> --old-line <OLD> -m "<body>"
glab mr note create <iid> --draft -m "<general comment>"
```

- Always `--draft`. Never `--unique` (glab refuses it with `--draft`).
- Body format: `**<blocker|should-fix|nit>:** <problem>. <fix>.` For a
  one-line fix add a GitLab suggestion block:
  ````
  ```suggestion:-0+0
  <replacement line>
  ```
  ````
- Never run `glab mr note publish`, `glab mr approve` or `glab mr merge`.
  If the user later asks to publish, show the count and run
  `glab mr note publish <iid> --yes` only after they confirm (`--yes` is
  required because the shell is not interactive; the plugin's guard asks
  too).

## 6. Report

```
Review of !<iid> "<title>" on <host> (<files> files, +<add> -<del>)

Posted <n> draft comments (only you can see them until you publish):
| # | Severity | File:line | Comment |
|---|----------|-----------|---------|

Not posted: <findings outside the diff, or dropped as duplicates/nits>
Overall: <one or two sentences: merge-ready or not, and the main risk>

Publish when ready: open the MR and submit your review, or run
`glab mr note publish <iid>` yourself.
```
