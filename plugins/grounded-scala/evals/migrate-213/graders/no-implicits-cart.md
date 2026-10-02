---
type: regex
target: {source: file, path: src/main/scala/shop/Cart.scala}
match: not_contains
pattern: '\bimplicit\s+(?:val|def|class|object)|\(implicit\b|:\s*_\*'
---
