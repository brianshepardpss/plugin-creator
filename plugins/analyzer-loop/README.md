# Analyzer Loop

The Dart language server for Claude Code, plus Flutter workflow skills for the
jobs that eat whole afternoons: driving the analyzer to zero, major package
upgrades, Android Gradle / AGP / Kotlin / JDK version mismatches, flaky golden
tests, and Riverpod 3 / Bloc 9 state code.

It is built to sit next to Google's official `dart-flutter` plugin, not
replace it. That plugin covers widgets, layout, architecture, l10n, http, json
and ships the Dart MCP server. Analyzer Loop adds the pieces it does not have:
an LSP so Claude sees analyzer diagnostics after every edit and can find
references, and the upgrade / build / golden / state skills. Install both.

Works in: Claude Code (terminal, IDE, desktop). Not in claude.ai or Cowork
(LSP servers and local SDKs only run in Claude Code on your machine).

Who it is for: Flutter developers who already use Claude Code and are tired
of Claude editing Dart blind or of losing a day to a Gradle upgrade.

## Install

Requirements: Flutter (or the Dart SDK) with `dart` on your PATH. The bundled
samples are locked to current packages and need Flutter 3.47 or newer; your own
projects can use any Flutter version.

```
/plugin marketplace add brianshepardpss/plugin-creator
/plugin install analyzer-loop@plugin-creator
```

Restart Claude Code so the language server starts, then run
`/analyzer-loop:doctor` in a Flutter project. Recommended alongside it:

```
claude plugin marketplace add flutter/agent-plugins
claude plugin install dart-flutter@dart-flutter
```

## Try it (under 5 minutes after `flutter pub get`)

```
/analyzer-loop:fix-analyzer sample
```

Claude copies `samples/stale_app` (current Riverpod 3 / go_router 18 lock,
stale code) into your folder, runs `flutter pub get`, records the baseline,
runs `dart fix`, fixes the rest file by file with LSP diagnostics after each
edit, and checks tests. Expected result, from the bundled script:

```
Before -> after: 27 -> 0 issues (27 fixed)
  errors     17 ->   0
  infos      10 ->   0
  [OK guardrail] no new ignore comments; analysis_options.yaml unchanged
```

More demos: `/analyzer-loop:android-build-doctor sample`,
`/analyzer-loop:golden-tests sample`, `/analyzer-loop:pub-upgrade sample`.

## What it does

- `.lsp.json`: runs `dart language-server --protocol=lsp` for `.dart` files
  (diagnostics after edits, go to definition, find references, hover). Uses
  `onlyAnalyzeProjectsWithOpenFiles` to keep memory down in monorepos.
- fix-analyzer: `dart fix`, then targeted edits until `dart analyze --fatal-infos`
  is 0; before/after counts and a no-`// ignore` guardrail from `analyze_report.py`.
- pub-upgrade: one package family at a time; reads the CHANGELOG slice you
  cross from the pub cache (`changelog_slice.py`), migrates, re-greens.
- android-build-doctor: reads gradle-wrapper, settings.gradle, app/build.gradle;
  `android_versions.py` checks Gradle/AGP/Kotlin/JDK pairwise and against
  Flutter's own floors (re-read from your Flutter SDK), proposes a compatible
  set, edits only Android build files. iOS / CocoaPods notes included.
- golden-tests: `golden_diff.py` measures the failing golden exactly like
  flutter_test; separates OS rendering drift from real regressions; recipes
  for Linux-only goldens, Alchemist, or a tolerant comparator. Never runs
  `--update-goldens` unless you ask.
- state-management: detects Riverpod or Bloc and its version, writes Riverpod 3
  (plain or riverpod_generator 4) or bloc 9 code plus a test.
- `/analyzer-loop:doctor` and a SessionStart check: warns when `dart` is
  missing, older than your pubspec `sdk:` constraint, or not the SDK your
  `.fvmrc` pins.
- request: say "I wish this could..." to draft a feature request.

## Dart MCP server

Not bundled, on purpose. Google's plugin already starts it, and every copy
runs its own analysis server (several GB each on large projects). If its
`mcp__*dart*` tools are present the skills may use them; otherwise they use
the `dart` / `flutter` CLI.

## Known limits

- `dart` on PATH must be the SDK your project uses. With FVM or puro, point
  PATH at the pinned SDK (the LSP command cannot be per project).
- The analysis server can use several GB on big monorepos. Close unrelated
  packages, or disable this plugin's LSP in large workspaces.
- Android builds are slow; the doctor checks files with its script and only
  runs a Gradle build when you agree.

## Privacy

Nothing is sent anywhere by this plugin. The scripts read local files and run
local `dart` / `flutter` commands. `flutter pub get` and `pub upgrade` contact
pub.dev as they always do. No telemetry.

## Feedback

Say "I wish this could..." and the request skill drafts an issue for you to
file. Nothing is sent automatically.

Not affiliated with or endorsed by Google LLC. Dart and Flutter are trademarks of Google LLC.
Not affiliated with or endorsed by Anthropic, the Riverpod or Bloc maintainers, or Gradle Inc.
