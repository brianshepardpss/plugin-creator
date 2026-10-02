---
name: fix-analyzer
description: Use when a Dart or Flutter project has analyzer errors, warnings or deprecation infos to clear, or when the user says "fix the analyzer errors", "make dart analyze clean", "flutter analyze shows 40 issues", "clean up the deprecations", "fix the red squiggles after the upgrade", "withOpacity is deprecated everywhere" or "try analyzer loop on the sample". Runs dart fix first, then targeted edits checked by the Dart language server, until `dart analyze --fatal-infos` reports zero, and prints before/after counts from a bundled script.
argument-hint: "[project dir | sample]"
---

# Drive the Dart analyzer to zero

Fixes code against the packages that are already locked. It does not upgrade
packages (that is the pub-upgrade skill) and it never silences the analyzer.

Paths: `analyze_report.py` and `references/` are in this skill's base
directory. The plugin root is two directories above it; the demo app is
`<plugin root>/samples/stale_app`.

## 1. Pick the project

- Argument `sample`, or the user asks to try it on the sample: run
  `cp -r "<plugin root>/samples/stale_app" ./stale_app` and work in
  `./stale_app`. Never edit files inside the plugin directory.
- Otherwise use the given directory, or the nearest folder with `pubspec.yaml`.
  In a monorepo (melos, pub workspaces) do one package at a time.

## 2. Preflight

1. `dart --version`. If `dart` is missing, say so and stop; the LSP and every
   step below need the SDK. If an `.fvmrc` exists, prefix commands with `fvm`.
2. If `.dart_tool/package_config.json` is missing, run `flutter pub get`
   (`dart pub get` for a package with no `flutter:` dependency). If version
   solving fails, stop and hand over to the pub-upgrade skill.
3. Tools: if `mcp__*dart*` tools are available (Google's dart-flutter plugin
   or a manual `dart mcp-server`), you may use `analyze_files`, `dart_fix` and
   `read_package_uris`; otherwise use the CLI. Do not install an MCP server.

## 3. Baseline (numbers come from the script, never from counting by eye)

```
python3 "<skill dir>/analyze_report.py" <project> --save <project>/.dart_tool/analyzer-loop-before.json
```

Show its output as the "Before" block.

## 4. Mechanical fixes first

1. `dart fix --dry-run` in the project. Show the summary.
2. `dart fix --apply`. Re-run `analyze_report.py <project>` (no `--save`).

## 5. Targeted fixes, one file at a time

1. Order: errors before infos; within errors, start at definitions other files
   import (models, providers, notifiers), because one root error cascades.
2. For each diagnostic code, look it up in `references/migrations.md` (read
   it once, now). If the API is not listed, inspect the real signature: use
   the LSP tool (hover, goToDefinition) or read the package source under the
   `rootUri` that `.dart_tool/package_config.json` gives for that package.
   Do not guess an API from memory.
3. Edit. After each edit the Dart language server returns fresh diagnostics
   for the file; fix anything new before moving on.
4. Before renaming or changing a signature, run LSP findReferences and update
   every call site in the same pass.
5. Every migration must keep behaviour: `withOpacity(x)` becomes
   `withValues(alpha: x)`, `WillPopScope(onWillPop: () async => false)`
   becomes `PopScope(canPop: false)`, and so on as the reference shows.
6. If two full passes do not reduce the count, stop and report what remains
   with your best explanation instead of looping.

## 6. Guardrails (stop and ask instead of doing any of these)

- Adding `// ignore:` or `// ignore_for_file:` comments.
- Editing `analysis_options.yaml`, removing a lint include, or excluding files.
- Deleting or skipping tests, or deleting code only to silence a diagnostic.
- Changing package versions (`pub upgrade`, `pub downgrade`, editing pubspec
  constraints). That is the pub-upgrade skill's job, with the user's yes.
- Running `flutter test --update-goldens`.

`analyze_report.py --compare` fails if ignore comments were added or
`analysis_options.yaml` changed; treat that as a bug in your work.

## 7. Verify

1. `dart analyze --fatal-infos` must exit 0.
2. `python3 "<skill dir>/analyze_report.py" <project> --compare <project>/.dart_tool/analyzer-loop-before.json`
3. `flutter test --reporter expanded` (or `dart test`). A failing golden test
   goes to the golden-tests skill; do not regenerate goldens.

## 8. Report in exactly this shape

```
Analyzer Loop: <project>
Before:  <N> issues (<e> errors, <w> warnings, <i> infos)      [analyze_report.py]
dart fix: <k> fixes in <f> files
After:   <M> issues                                             [analyze_report.py --compare]
Guardrails: <OK line from the script, or the FAIL lines>
Tests:   <passed>/<total> (<command>)

Manual changes:
- <file>: <old API> -> <new API> (<diagnostic code>)
...
Left for you: <anything not fixed, with the reason, or "nothing">
```
