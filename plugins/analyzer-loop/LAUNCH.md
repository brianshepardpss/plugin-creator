# Launch plan: Analyzer Loop

Nothing here is posted without the owner's explicit go-ahead for each channel.

## Positioning (one line)

The Dart language server for Claude Code, plus the upgrade, Android-build and
golden-test fixes the official Flutter plugin does not cover. Install both.

## Audience and where they are

| Channel | Why | Self-promo rule to respect |
|---|---|---|
| anthropics/claude-code#16849 "Add Dart/Flutter LSP support" (137 reactions, closed with "write your own .lsp.json") | Warmest list: people who asked for exactly this | One comment, answer the question asked, no follow-up bumps |
| r/FlutterDev | Largest Flutter forum | Show the thing, disclose you made it, answer comments; no repeat posts |
| Flutter forum (forum.itsallwidgets.com), Gradle/AGP upgrade threads | People mid-pain on the Android version matrix | Reply only where the plugin answers the thread's question; disclose authorship |
| flutter/agent-plugins#162 (Bloc/Cubit skill request) and #233 (awesome lists) | Google plugin users asking for what we ship | Not accepting PRs there; comment with a pointer only where relevant |
| Newsletters: Flutter Tap, Flutter Weekly, Code With Andrea | Curated reach | Submit via their link forms; one submission each |
| claude-plugins-official submission | No Dart LSP there; acceptance enables the LSP recommendation dialog for anyone with `dart` on PATH | Follow the submission template; strict validate clean |

## Directory listing text

Analyzer Loop: Dart language server (LSP) for Claude Code plus Flutter
workflow skills: drive `dart analyze` to zero without `// ignore`, upgrade
packages one major at a time using their changelogs, fix Android Gradle / AGP /
Kotlin / JDK mismatches with a checker that uses Flutter's own support rules,
diagnose flaky golden tests, and write Riverpod 3 / Bloc 9 state. Complements
Google's dart-flutter plugin; does not bundle a second Dart MCP server. Not
affiliated with Google LLC. Dart and Flutter are trademarks of Google LLC.

## Post drafts

### 1. Comment on anthropics/claude-code#16849

> For anyone still looking for Dart LSP in Claude Code: I packaged the
> `.lsp.json` from this thread as a plugin, with `onlyAnalyzeProjectsWithOpenFiles`
> on to keep the analysis server's memory down, plus a SessionStart check
> that warns when `dart` on PATH is older than your pubspec `sdk:` or differs
> from your `.fvmrc`.
>
> ```
> /plugin marketplace add brianshepardpss/plugin-creator
> /plugin install analyzer-loop@plugin-creator
> ```
>
> It also has a few Flutter skills (analyzer-to-zero loop, major upgrades,
> Android Gradle/AGP/Kotlin fixer, golden tests). Disclosure: I made it. MIT,
> no telemetry. Works next to Google's dart-flutter plugin.

### 2. r/FlutterDev (text post)

Title: I made a Claude Code plugin that gives Claude the Dart analyzer and fixes Gradle/AGP/Kotlin mismatches

> Disclosure: I built this; it is free and MIT.
>
> Two things kept burning time when I used Claude Code on Flutter apps:
> Claude edited Dart without seeing analyzer errors, and every Flutter upgrade
> broke the Android build on the Gradle / AGP / Kotlin / JDK matrix.
>
> Analyzer Loop adds the Dart language server to Claude Code (diagnostics
> after each edit, find references) and five skills:
> - fix the analyzer to zero: `dart fix` first, then targeted edits, never `// ignore`
> - major package upgrades one family at a time, reading the CHANGELOG slice you cross
> - Android build doctor: a script that checks your versions against the same
>   tables flutter_tools uses and proposes a compatible set
> - golden tests: measures the diff, tells OS drift from real regressions,
>   never regenerates goldens unless you ask
> - Riverpod 3 / Bloc 9 code in whatever your project already uses
>
> Demo on a bundled sample app: `/analyzer-loop:fix-analyzer sample` goes from
> 27 analyzer issues to 0. It is meant to sit next to Google's official
> dart-flutter plugin, not replace it.
>
> Install: `/plugin marketplace add brianshepardpss/plugin-creator` then
> `/plugin install analyzer-loop@plugin-creator`.
>
> I would love real Gradle error logs that it gets wrong; there is an issue template.

### 3. Flutter forum reply (in an "upgrade AGP / Gradle" help thread)

> The error you have (`Unsupported class file major version 65`) means the
> JDK running Gradle is 21 but the wrapper's Gradle is older than 8.4. Flutter
> 3.47 also needs Gradle >= 8.14, AGP >= 8.11.1 and Kotlin >= 2.2.20, and
> Kotlin and AGP have to agree with each other, which is why bumping one at a
> time keeps failing. The set `flutter create` generates today is Gradle 9.3.1,
> AGP 9.1.0, Kotlin 2.4.0 with Java/Kotlin targets 17.
>
> If you use Claude Code, I made a free plugin (Analyzer Loop) whose
> android-build-doctor skill reads your gradle files and checks all of this
> with Flutter's own tables; disclosure, it is mine. The versions above work
> without it too.

### 4. Newsletter submission blurb (Flutter Tap / Flutter Weekly / Code With Andrea)

> Analyzer Loop (MIT): Dart LSP for Claude Code plus skills for analyzer
> cleanup, major package upgrades, Android Gradle/AGP/Kotlin fixes and golden
> tests. Complements Google's dart-flutter agent plugin.
> https://github.com/brianshepardpss/analyzer-loop

## Day-30 signal and thresholds

Thresholds (lab/plugins.json, set before launch, never lowered):
cloners >= 150, stars >= 40, requests (issues from strangers) >= 10.

What to read beyond the numbers:
1. Reactions/replies on #16849 after the comment, and installs that cite it.
2. Issues from strangers pasting real Android/Gradle or upgrade error logs
   (target >= 5). This proves the upgrade-pain wedge, not just the LSP.
3. Whether the plugin is accepted into claude-plugins-official.

Decision rule: if (2) is about 0 while LSP praise is high, cut the skills and
contribute the LSP config upstream instead. If thresholds are missed and (2)
is low, archive.
