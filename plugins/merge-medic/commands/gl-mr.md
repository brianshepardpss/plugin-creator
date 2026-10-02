---
description: Open a draft GitLab merge request for the current branch (push, title and description from the commits, "Closes #N"), or update the existing one.
argument-hint: "[target branch] [issue number] | demo"
---

Open or update the merge request for the current branch using the Merge
Medic `gitlab-mr-create` skill.

Details from me (may be empty): $ARGUMENTS

A bare number is an issue to close; a branch name is the target branch;
"demo" or "sample" uses the bundled demo project. Create it as a draft on
this repo's own GitLab host.
