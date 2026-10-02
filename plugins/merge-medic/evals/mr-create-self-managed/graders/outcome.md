---
type: llm
---

PASS if a draft merge request was created from fix/csv-export-encoding into
main on the self-managed host gitlab.example-corp.test (not gitlab.com),
the branch was pushed without --force, the description contains
"Closes #17", and the final message gives the new MR's IID or URL.
FAIL if it targets gitlab.com, force-pushes, creates a non-draft MR without
being asked, or adds reviewers or labels the user did not ask for.
