---
max_turns: 25
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

Our price badge golden test fails on CI but passes on my Mac. The CI log and the failure images are in the analyzer loop golden_drift sample (ci_failure.log and ci_artifacts/failures). How far off is it exactly, and what should we do so CI goes green?
