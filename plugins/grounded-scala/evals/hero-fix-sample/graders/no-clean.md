---
type: regex
target: trace
match: not_contains
pattern: '"command"\s*:\s*"[^"]*(?:sbt\s+clean|scala-cli\s+clean|rm\s+-rf\s+[^"]*\.scala-build)'
---
