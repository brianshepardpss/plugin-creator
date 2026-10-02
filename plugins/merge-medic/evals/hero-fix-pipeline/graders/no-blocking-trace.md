---
type: regex
target: {source: file, path: merge-medic-demo/.git/merge-medic-fake/calls.log}
match: not_contains
pattern: 'glab ci trace'
---
