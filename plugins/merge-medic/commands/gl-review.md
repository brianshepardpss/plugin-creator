---
description: Review a GitLab merge request and leave the findings as draft inline comments that only you can see until you publish. Pass an MR IID, URL, or "demo".
argument-hint: "[MR iid | MR URL | demo]"
---

Review the merge request using the Merge Medic `gitlab-mr-review` skill and
leave the findings as draft comments.

Target: $ARGUMENTS (empty means the MR for the current branch; "demo" or
"sample" means MR 42 in the bundled demo project).

One diff fetch, one reviewer subagent, drafts only. Never publish, approve
or merge.
