---
name: state-management
description: Use when writing, refactoring or testing Flutter app state with Riverpod or Bloc, or when the user says "add a provider for", "convert this StateNotifier to a Notifier", "make a cubit for", "write a bloc for login", "use riverpod_generator", "AsyncNotifier", "blocTest", or "how should this state be managed". Detects which library and version the project already uses and writes current idioms (Riverpod 3 with or without riverpod_generator 4, bloc 9 / flutter_bloc 9) plus a test.
argument-hint: "[what state to add or change]"
---

# State in the project's own idiom (Riverpod 3 / Bloc 9)

References in this skill's base directory: `references/riverpod3.md`,
`references/bloc9.md`. Every snippet there was compiled and tested against the
versions they name.

## 1. Detect, do not choose

1. Read `pubspec.yaml` and the versions in `pubspec.lock` for
   flutter_riverpod / hooks_riverpod / riverpod, riverpod_annotation,
   riverpod_generator, bloc, flutter_bloc, bloc_test, provider, get, mobx.
2. Grep `lib/` for `@riverpod`, `extends Notifier`, `extends AsyncNotifier`,
   `StateNotifier`, `extends Bloc<`, `extends Cubit<`.
3. Decide:
   - One library in use: use it. Never add a second state library.
   - riverpod_generator present and `@riverpod` used: write generated
     providers; otherwise plain `NotifierProvider`.
   - Riverpod 2.x locked: write `Notifier` / `AsyncNotifier` (they exist in
     2.x and survive the 3.0 upgrade); never new `StateNotifier` or
     `StateProvider`. Mention that the pub-upgrade skill can move them to 3.
   - None in use: ask the user which one they want. Do not pick for them.
4. Say what you detected in one line before writing code.

## 2. Write the state

1. Read the matching reference file now (riverpod3.md or bloc9.md) and follow
   its shapes exactly. If the locked version is newer than the reference,
   check the package CHANGELOG in the pub cache for anything renamed.
2. Keep business logic in the notifier / bloc, not in widgets. Widgets
   `watch` or `BlocBuilder` for display and call methods or `add(event)` in
   callbacks. Side effects (navigation, snackbars) go in `ref.listen` or
   `BlocListener`.
3. Immutable state: new lists/objects on every change (`[...state, x]`),
   never mutate in place; Riverpod 3 filters updates with `==` and Bloc skips
   equal states.
4. When converting an existing `StateNotifier`, keep the provider name and the
   public method names so call sites do not change; use LSP findReferences to
   confirm every call site still compiles.
5. Codegen: run `dart run build_runner build --delete-conflicting-outputs`
   after editing annotated files. Never hand-edit `*.g.dart`.

## 3. Test it

Add or update one unit test per notifier/bloc using the reference's testing
section (`ProviderContainer.test()` for Riverpod 3, `blocTest` for Bloc).
Fake repositories with overrides or constructor injection; no network in tests.

## 4. Verify

`dart analyze --fatal-infos` (0 issues, no new `// ignore`) and
`flutter test <the test file>`.

## Report in exactly this shape

```
State: <library> <locked version> (<codegen or plain>)
Added/changed: <file>: <class> -> <provider or bloc name>
Call sites updated: <n> (<files>)
Test: <test file> <passed>/<total>
Analyzer: <n> issues
```
