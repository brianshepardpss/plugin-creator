---
type: regex
pattern: '\b\d{1,2}(\.\d)?\s*/\s*10\b|\b\d{1,2}(\.\d)? out of 10\b'
target: last_message
match: not_contains
flags: i
---
