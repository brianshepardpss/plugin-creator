---
type: regex
target: {source: file, path: lib/favorites.dart}
pattern: 'extends StateNotifier|StateNotifierProvider|legacy\.dart'
match: not_contains
---
