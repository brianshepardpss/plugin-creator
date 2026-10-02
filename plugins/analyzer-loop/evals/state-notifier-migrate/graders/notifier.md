---
type: regex
target: {source: file, path: lib/favorites.dart}
pattern: 'extends Notifier<Set<String>>.*NotifierProvider<FavoritesNotifier,\s*Set<String>>\(\s*FavoritesNotifier\.new\s*\)'
flags: s
---
