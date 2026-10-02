---
name: gitlab-mr-threads
description: Use when the user wants to deal with review feedback on a GitLab merge request, or says "address the review comments", "fix what the reviewer asked", "resolve the threads", "reply to the MR comments", "what's left on my MR", "handle the unresolved discussions". Lists only unresolved threads, fixes the code where a change was asked for, replies in each thread, and resolves only threads it changed code for, after the user confirms. Works on self-managed GitLab.
---

# Work through unresolved MR threads

`<skill>` is this skill's base directory. Demo mode (user said "demo" or
"sample", or there is no GitLab repo): create the demo with step 0 of the
gitlab-ci-triage skill and work on MR `42` with the fake glab.

## 1. Load the threads

1. Host from the remote; `glab auth status --hostname <host>` must pass.
2. MR: the IID the user gave, else `glab mr view -F json` for this branch.
   The local branch must be the MR's `source_branch`; if not, stop and say so.
3. Fetch and compact (one call):
   ```
   mkdir -p "${TMPDIR:-/tmp}/merge-medic"
   glab mr note list <iid> --state unresolved -F json > "${TMPDIR:-/tmp}/merge-medic/threads.json"
   python3 <skill>/scripts/threads.py "${TMPDIR:-/tmp}/merge-medic/threads.json"
   ```
   Older glab without `mr note list`: use
   `glab api projects/:id/merge_requests/<iid>/discussions` and the same script.

## 2. Plan

Put each thread in one bucket:

- **change**: the reviewer asked for a code change you can make.
- **answer**: a question; reply, do not resolve (the reviewer decides).
- **needs you**: disagreement, product decision, or unclear ask. Draft a
  reply for the user; do not post it.

Show the plan before editing:

```
| Thread | Where | Ask (short) | Plan |
|--------|-------|-------------|------|
| 3f9a1c2e | late_fees.py:4 | grace days from settings | change + reply + resolve |
```

## 3. Change the code (local only)

Make each change, keep it minimal, and run the tests that cover it. One
commit for all thread fixes: `Address review feedback on !<iid>`.

## 4. Confirm, then write to GitLab

Writing to GitLab needs a yes. If the user already said to reply and resolve
in this conversation, that is the yes; otherwise show the exact replies and
the threads to resolve and ask once for the whole batch.

In this order, after the yes:

1. `git push` (never `--force`), so the reviewer can see the commit.
2. Reply in each thread you acted on (use the 8-character ID from the
   script):
   ```
   glab mr note create <iid> --reply <id8> -m "Done in <short-sha>: <what changed>."
   glab mr note create <iid> --reply <id8> -m "<answer to the question>"
   ```
3. Resolve only **change** threads whose fix is in the pushed commit:
   `glab mr note resolve <iid> <id8>`. Never resolve **answer** or
   **needs you** threads, and never resolve a thread you did not change code
   for.

Never publish draft notes, approve or merge from this skill.

## 5. Report

```
!<iid>: <n> unresolved threads -> <c> fixed and resolved, <a> answered (left open), <h> need you

| Thread | Where | Action | Reply posted |
|--------|-------|--------|--------------|

Commit <short-sha> pushed to <branch> on <host>.
Needs you: <thread id8>: <suggested reply text>
```
