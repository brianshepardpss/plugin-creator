# Migration table

Verified 2026-10-02 against Flutter 3.47.6 / Dart 3.13.5, flutter_riverpod 3.4.3,
riverpod_generator 4.0.9, go_router 18.0.2, bloc 9.2.1 / flutter_bloc 9.1.1.
"dart fix" = `dart fix --apply` migrates it for you. Anything else is a manual edit.
If the user's versions are newer, check the package CHANGELOG in the pub cache first.

## Flutter framework deprecations (diagnostic `deprecated_member_use`)

| Old | New | dart fix |
|---|---|---|
| `color.withOpacity(x)` | `color.withValues(alpha: x)` | yes |
| `color.value` | `color.toARGB32()` | yes |
| `color.opacity` | `color.a` (0.0-1.0) | yes |
| `color.red` / `.green` / `.blue` / `.alpha` (0-255 ints) | `(color.r * 255.0).round().clamp(0, 255)` (same for g, b, a) | no |
| `MaterialStateProperty`, `MaterialState`, `MaterialStatePropertyAll` | `WidgetStateProperty`, `WidgetState`, `WidgetStatePropertyAll` | yes |
| `WillPopScope(onWillPop: () async => false, child: c)` | `PopScope(canPop: false, child: c)` | no |
| `WillPopScope(onWillPop: () async { await save(); return true; })` | `PopScope(canPop: true, onPopInvokedWithResult: (didPop, result) { if (didPop) save(); })` or `canPop: false` + `Navigator.pop` after the async work | no |
| `PopScope(onPopInvoked: (didPop) {...})` | `PopScope(onPopInvokedWithResult: (didPop, result) {...})` | no |
| `MediaQuery.of(context).textScaleFactor` | `MediaQuery.textScalerOf(context)` (a `TextScaler`) | no |
| `Text(..., textScaleFactor: f)` | `Text(..., textScaler: TextScaler.linear(f))`, or pass the `TextScaler` you already have | no |
| `ButtonBar(children: ...)` | `OverflowBar(children: ...)` (add `spacing:` / `alignment:` to match) | yes |
| `ColorScheme(... background: x)` / `.background` | `surface: x` / `.surface` | no |
| `onBackground` | `onSurface` | yes |
| `surfaceVariant` | `surfaceContainerHighest` | yes |
| `RawKeyboardListener` | `KeyboardListener` (events become `KeyEvent`, not `RawKeyEvent`) | no |
| `DropdownButtonFormField(value: v)` | `DropdownButtonFormField(initialValue: v)` | yes |
| `Radio(groupValue: g, onChanged: f)` | wrap radios in `RadioGroup(groupValue: g, onChanged: f, child: ...)`; `Radio(value: v)` only | no |
| `Switch(activeColor: c)` | `Switch(activeThumbColor: c)`; check the track colour visually | yes |

## Riverpod 2 -> 3 (flutter_riverpod / hooks_riverpod 3.x)

| Symptom | Fix |
|---|---|
| `StateNotifier`, `StateNotifierProvider`, `StateProvider`, `ChangeNotifierProvider` undefined | Quick: add `import 'package:flutter_riverpod/legacy.dart';` (hooks: `package:hooks_riverpod/legacy.dart`). Preferred: migrate to `Notifier` (below). Ask which the user wants if the diff would be large. |
| `class X extends StateNotifier<S> { X() : super(init); }` | `class X extends Notifier<S> { @override S build() => init; }` and `NotifierProvider<X, S>(X.new)`; call sites (`ref.read(p.notifier).foo()`, `ref.watch(p)`) do not change |
| `StateNotifierProvider.family` / `FamilyNotifier` | `NotifierProvider.family<X, S, Arg>(X.new)` with `class X extends Notifier<S> { X(this.arg); final Arg arg; ... }` |
| `AutoDisposeNotifier`, `AutoDisposeAsyncNotifier` | plain `Notifier` / `AsyncNotifier`; use `NotifierProvider.autoDispose(...)` or `isAutoDispose: true` |
| `FutureProviderRef<T>`, `AutoDisposeRef`, `XxxRef` types | `Ref` |
| `asyncValue.valueOrNull` | `asyncValue.value` (now null on error as well as loading) |
| `ProviderObserver.didUpdateProvider(provider, prev, next, container)` | `didUpdateProvider(ProviderObserverContext context, Object? prev, Object? next)` |
| errors from `ref.watch` / `ref.read` now arrive wrapped | catch `ProviderException` (import `package:flutter_riverpod/misc.dart`) and read `.exception` |
| `family.overrideWith(...)` deprecated (3.2) | `family.overrideWith2(...)`; for a Notifier family the callback is `(arg) => MyNotifier(arg)` |

riverpod_generator 4: `@riverpod class CartNotifier extends _$CartNotifier` generates
`cartProvider` (the `Notifier` suffix is stripped); functional providers take `Ref ref`.
Regenerate with `dart run build_runner build --delete-conflicting-outputs`.

## go_router (most removals happened in 7-10; 18.0 only raised the SDK floor)

| Old | New | dart fix |
|---|---|---|
| `state.params['id']` | `state.pathParameters['id']` | yes |
| `state.queryParams['q']` | `state.uri.queryParameters['q']` | yes |
| `state.location` | `state.uri.toString()` (or `state.matchedLocation` for the matched path) | yes |
| `state.subloc` / `state.fullpath` | `state.matchedLocation` / `state.fullPath` | yes |
| `GoRouter.of(context).location` | `GoRouterState.of(context).uri.toString()` | no |
| `context.replace` / `replaceNamed` (v6 meaning) | `context.pushReplacement` / `pushReplacementNamed` | no |
| `GoRouteData.onExit(context)` | `onExit(context, state)` | no |
| URL matching changed case | routes are case sensitive since 15.0; `GoRouter(caseSensitive: false)` restores old behaviour |

go_router 18.0.0 requires Flutter 3.44 / Dart 3.12 or newer.

## bloc 8 -> 9 (bloc 9.x, flutter_bloc 9.x, bloc_test 10.x)

| Old | New |
|---|---|
| `BlocOverrides.runZoned(() => ..., blocObserver: o)` | `Bloc.observer = o;` then run the code (removed in 9.0) |
| custom classes implementing `StateStreamableSource` that call `emit` | implement `EmittableStateStreamableSource<State>` |
| `bloc_test` 9.x with bloc 9 | `bloc_test: ^10.0.0` |
| several observers | `MultiBlocObserver(observers: [...])` (9.2) |

## When the analyzer is wrong rather than the code

- Hundreds of `uri_does_not_exist` / `undefined_class` for packages: run `pub get`.
- Errors only in `*.g.dart` / `*.freezed.dart`: rerun build_runner, do not hand-edit generated files.
- `dart` on PATH older than pubspec `sdk:`: fix PATH (or use `fvm dart`), do not edit code.
