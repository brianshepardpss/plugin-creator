---
type: regex
target: {source: file, path: src/Pricing.scala}
match: not_contains
pattern: 'ExecutionContext|Await|Future\s*\{'
---
