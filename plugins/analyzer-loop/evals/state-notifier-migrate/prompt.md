---
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write, Edit]
---

We just bumped to flutter_riverpod 3.4.3 (no riverpod_generator in the project). Rewrite this the way it should be written now, keep the provider name and methods so the screens don't change, and give me a unit test for it. Write them to lib/favorites.dart and test/favorites_test.dart.

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

class FavoritesNotifier extends StateNotifier<Set<String>> {
  FavoritesNotifier() : super(<String>{});

  void toggle(String sku) {
    if (state.contains(sku)) {
      state = {...state}..remove(sku);
    } else {
      state = {...state, sku};
    }
  }
}

final favoritesProvider =
    StateNotifierProvider<FavoritesNotifier, Set<String>>((ref) => FavoritesNotifier());
```
