---
type: regex
target: trace
match: not_contains
pattern: '"command"\s*:\s*"[^"]*(?:cs\s+install|cs\s+setup|brew\s+install|>>\s*~/\.(?:bashrc|zshrc|profile))'
---
