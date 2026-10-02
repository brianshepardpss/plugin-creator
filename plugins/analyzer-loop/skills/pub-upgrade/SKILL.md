---
name: pub-upgrade
description: Use when the user wants to move Dart or Flutter dependencies to new major versions, or says "upgrade riverpod to 3", "bump go_router to latest", "pub outdated shows a wall of red", "upgrade all my packages", "version solving failed", or "migrate to the new bloc". Upgrades one package family at a time, reads each CHANGELOG slice from the pub cache with a bundled script, applies the migrations, and drives the analyzer and tests back to green after each step.
argument-hint: "[package ... | all | sample]"
---

# Major package upgrades, one family at a time

Paths: `changelog_slice.py` is in this skill's base directory. The plugin root
is two directories above it; the upgrade demo is
`<plugin root>/samples/upgrade_app` (flutter_riverpod 2.6.1, go_router 6.5.9).
The migration table is `<plugin root>/skills/fix-analyzer/references/migrations.md`.

## 1. Set up

1. Argument `sample`: `cp -r "<plugin root>/samples/upgrade_app" ./upgrade_app`
   and work there. Never edit files inside the plugin directory.
2. If the project is a git repo, run `git status --short`. If there are
   uncommitted changes, tell the user and suggest committing or stashing first
   so each upgrade step is reviewable. Do not commit for them unless asked.
3. Copy `pubspec.lock` to `.dart_tool/analyzer-loop-old.lock` (you need the old
   versions later). Run `flutter pub get` if `.dart_tool/` is missing.
4. `flutter pub outdated` (use `dart pub outdated` for pure Dart). Show the
   table.

## 2. Plan before touching pubspec.yaml

Group packages into families that must move together:

- Riverpod: flutter_riverpod / hooks_riverpod / riverpod, riverpod_annotation,
  riverpod_generator, riverpod_lint
- Bloc: bloc, flutter_bloc, bloc_test, hydrated_bloc, bloc_concurrency
- Routing: go_router, go_router_builder
- Codegen: build_runner, freezed, freezed_annotation, json_serializable, json_annotation
- Firebase: every `firebase_*` package plus `cloud_firestore` together

Show the plan as a list: family, current -> target, majors crossed. Upgrade
only the families the user asked for. If they said "all", do the leaf
families first (routing, codegen) and Firebase last. Wait for a yes before
step 3 if more than one family is involved.

## 3. For each family

1. `flutter pub upgrade --major-versions <pkg> <pkg> ...` (only that family).
   If version solving fails, read the solver output, name the blocking
   constraint (often the SDK lower bound or another package), and ask. Never
   add `dependency_overrides`, never downgrade, and never raise
   `environment: sdk:` without asking.
2. For every package in the family whose major changed, and its core package
   (`riverpod` for flutter_riverpod, `bloc` for flutter_bloc):
   ```
   python3 "<skill dir>/changelog_slice.py" <project> <package> --from <old version from analyzer-loop-old.lock>
   ```
   Show the flagged lines. Open any migration guide it lists only if the
   flagged lines are not enough to fix the code.
3. If the family uses code generation, run
   `dart run build_runner build --delete-conflicting-outputs`.
4. Fix the code with the fix-analyzer skill's procedure (dart fix first, then
   targeted edits, LSP diagnostics after each edit, same guardrails: no
   `// ignore`, no analysis_options edits). Use migrations.md and the
   changelog lines; do not invent APIs.
5. `dart analyze --fatal-infos` must reach 0, then `flutter test`. Only then
   move to the next family.

## 4. Report in exactly this shape

```
Upgrade: <project>
| family | package | from | to | majors crossed | changelog lines flagged |
|---|---|---|---|---|---|
...
Code changes per family:
- <family>: <file>: <old API> -> <new API>
Analyzer: <before> -> 0 issues   Tests: <passed>/<total>
Not done / needs you: <SDK bumps, overrides, packages left behind, or "nothing">
```

Numbers in the table come from `pub outdated`, the lock files and
`changelog_slice.py`, not from memory.
