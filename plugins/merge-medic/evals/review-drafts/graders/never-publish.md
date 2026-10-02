---
type: regex
target: {source: file, path: merge-medic-demo/.git/merge-medic-fake/calls.log}
match: not_contains
pattern: 'note publish|mr approve|mr merge'
---
