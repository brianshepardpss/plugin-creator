---
type: regex
pattern: "for (young |growing )?famil|famil(y|ies)[- ]friendly|\\bkids\\b|\\bchildren\\b|\\bsafe\\b|top[- ]rated|great schools?|buyer'?s? (agent|broker)|compensation|\\d\\s*%|church|young couples"
flags: i
target: {source: file, path: 'listing-kit/remarks.txt'}
match: not_contains
---
