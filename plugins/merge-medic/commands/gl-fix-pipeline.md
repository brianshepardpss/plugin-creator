---
description: Find why the GitLab pipeline for this branch's MR failed, fix it, and push or retry after you confirm. Pass "demo" to try it on the bundled sample project.
argument-hint: "[MR iid | branch | demo]"
---

Fix the failed GitLab pipeline using the Merge Medic `gitlab-ci-triage` skill.

Target: $ARGUMENTS

- Empty: the MR (or, if none, the latest pipeline) for the current branch.
- A number: that MR IID. A branch name: that branch's pipeline.
- "demo" or "sample": the bundled demo project (step 0 of the skill).

Follow the skill's steps in order and end with its report template. Do not
push, retry or change anything on GitLab until I answer yes.
