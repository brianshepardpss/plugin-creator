---
type: regex
target: {source: file, path: merge-medic-demo/.git/merge-medic-fake/calls.log}
match: not_contains
pattern: 'jobs/904(?:11|12|16|17)/trace'
---
