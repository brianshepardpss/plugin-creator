---
name: gitlab-mr-create
description: Use when the user wants to open or update a GitLab merge request from the current branch, or says "open an MR", "create a merge request", "put this up for review", "make an MR for this branch against main", "this fixes issue 17, open the MR", "update the MR description". Pushes the branch, writes the title and description from the commits, links issues with "Closes #N", and creates the MR as a draft on the repo's own GitLab host (self-managed included).
---

# Open (or update) a merge request from this branch

Demo mode (user said "demo"/"sample", or no GitLab repo): run
`python3 <skill>/../../samples/setup_demo.py ./merge-medic-mr --branch fix/csv-export-encoding`,
`cd` into it, and use the fake glab path it prints in place of `glab`.
`<skill>` is this skill's base directory.

## 1. Preflight

1. Host from `git remote get-url origin`. Never default to gitlab.com.
   `glab auth status --hostname <host>` must pass, else give
   `glab auth login --hostname <host>` and stop.
2. Branch: `git rev-parse --abbrev-ref HEAD`. Refuse to open an MR from the
   default branch; offer to create a branch instead.
3. `git status --short`: if there are uncommitted changes, ask whether to
   commit them first. Never commit them silently.
4. Existing MR: `glab mr view -F json`. If one exists, switch to update mode
   (step 5b) and tell the user its IID and URL.

## 2. Gather

- Target branch: what the user said, else `default_branch` from
  `glab repo view -F json`.
- Commits: `git log --format='%h %s%n%b' origin/<target>..HEAD` (fall back to
  `<target>..HEAD` if the remote ref is missing). Diff size:
  `git diff --stat origin/<target>...HEAD`.
- Issue: from the user's words ("fixes 17", "#17"), the branch name
  (`17-some-title`), or commit messages. Confirm it with
  `glab issue view <N> -F json`. If that fails, still link it but say the
  issue could not be read. Other project: `Closes group/project#N`.
- Template: if `.gitlab/merge_request_templates/Default.md` exists, fill its
  sections instead of the one below.

## 3. Write

Title: imperative, under 72 characters, from the commits (not the branch
name). Description, written to `${TMPDIR:-/tmp}/merge-medic/mr-description.md`:

```
## What
<one to three sentences>

## Why
<the problem>. Closes #<N>

## How to test
- <commands or steps, taken from the repo's test setup>

## Notes for reviewers
- <risks, migrations, follow-ups; "None" if none>
```

Use `Closes #N` exactly (GitLab's closing pattern); never invent an issue
number. No reviewers, assignees or labels unless the user named them
(reviewers get notified).

## 4. Confirm

If the user explicitly asked you to open the MR, that is the go-ahead for a
draft MR: create it, then show what you created. Ask first when the request
was indirect, when they want it non-draft (ready), or when reviewers would
be notified. Always show the title, target, draft flag and description.

## 5a. Create

```
git push -u origin <branch>              # never --force
glab mr create --source-branch <branch> --target-branch <target> --title "<title>" --description-file "${TMPDIR:-/tmp}/merge-medic/mr-description.md" --draft --yes
```

Add `--label`, `--reviewer` or `--remove-source-branch` only when the user
asked for them (the project defaults apply otherwise).

Draft by default; drop `--draft` only if the user asked for a ready MR.
glab uses the remote's host, so the same command works on self-managed.

## 5b. Update

`glab mr update <iid> --description-file <file>` (and `--title` if needed).
Show the old and new description first and wait for a yes; this edits a
page other people read.

## 6. Report

```
Opened draft !<iid> "<title>" -> <target> on <host>
<url>
Links: Closes #<N> (<issue title>)
Next: push more commits to update it; mark ready with `glab mr update <iid> --ready`
when the pipeline is green (run /gl-fix-pipeline if it goes red).
```
