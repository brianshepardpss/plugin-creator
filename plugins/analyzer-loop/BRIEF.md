# Research brief: `flutter-dart` plugin (rename recommended: `analyzer-loop`, "Analyzer Loop - Dart LSP and upgrade fixes for Flutter")
Date: 2026-10-02. [U] = unverified. Current stable: Flutter 3.47.6 / Dart 3.13.5 (2026-10-01).

## 1. Target user and jobs-to-be-done
User: Flutter app dev (solo/agency/startup) already using Claude Code. Claude Code is the #1 AI agent among Flutter devs: 32% vs Antigravity 23%, Copilot 19%, Cursor 18% (Flutter Q2 2026 survey, 3,500+ responses, flutter.dev/blog/flutter-q2-2026-survey). 79% of Flutter devs use AI; 46% do not trust it for debugging -> "verification tax" (flutter.dev/blog/how-dart-and-flutter-are-thinking-about-ai-in-2026).

Ranked pain x frequency:
1. Claude edits Dart blind: no analyzer feedback after edits, no symbol navigation (every session, high). anthropics/claude-code#16849 "Add Dart/Flutter LSP support": 109 thumbs-up + 28 hearts, closed with "write your own .lsp.json". No Dart entry in the official code-intelligence table (13 languages, Dart absent).
2. Upgrade breakage, esp. Android Gradle/AGP/Kotlin/JDK version matching (monthly-ish, very high). Top survey pain theme: 44% "platform/ecosystem maturity", "primarily upgrade complexity, particularly Android's version-matching across Flutter, Dart, Gradle, Kotlin, and JVM". flutter/flutter#153668 (36 comments), #124838 (31), #148668 (29).
3. Analyzer error/deprecation cleanup after `pub upgrade --major-versions` or SDK bump (each upgrade, high): e.g. Color.withOpacity deprecation fight flutter/flutter#162069 (31 comments); Riverpod 3.x (3.4.3) moved StateNotifier to legacy [U exact path]; go_router now 18.0.2.
4. Golden tests: brittle cross-OS pixel diffs, font loading, `--update-goldens` misuse (weekly for teams with goldens, med). golden_toolkit is discontinued on pub.dev (isDiscontinued=true, replacedBy=null); alchemist 0.14.0 is the live alternative.
5. State management in current idioms (Riverpod 3 + riverpod_generator 4, bloc 9) (daily, med). Open request flutter/agent-plugins#162 (Bloc/Cubit skill).

## 2. Competition
- Google official `dart-flutter` plugin, github.com/flutter/agent-plugins (3,019 stars, BSD-3, created 2026-02-25, v1.0.6). Install: `claude plugin marketplace add flutter/agent-plugins` then `claude plugin install dart-flutter@dart-flutter`. Ships: 25 skills (flutter-add-widget-test, -integration-test, -widget-preview, fix-layout-issues, responsive-layout, architecture, json, go_router, l10n, http; dart-run-static-analysis, -resolve-package-conflicts, -fix-runtime-errors, mocks, coverage, ffi...) + inline `mcpServers.dart-mcp-server` (`dart mcp-server`, env AGENT_PLUGIN=claude-code). LACKS: LSP, Claude hooks (its .agents/hooks.json is not the Claude format), golden tests, Android/iOS build doctor, Riverpod/Bloc, major-upgrade migration. Not accepting PRs. Own bug: l10n skill emits rejected `synthetic-package: true` (#239).
- Very Good Ventures vgv-ai-flutter-plugin (166 stars, MIT, v0.0.5): 15 skills (bloc, testing incl. goldens, dart-flutter-sdk-upgrade = pubspec/CI SDK constraints only, 0 mentions of Gradle/Kotlin/AGP, green-gate loop, a11y...), flutter-reviewer agent, format/analyze hooks, .mcp.json with `dart mcp-server --enable dart_format` + `very_good mcp`. LACKS: LSP, Riverpod, native build doctor; opinionated to VGV stack.
- Piebald-AI/claude-code-lsps (521 stars, multi-language): `dart` plugin v0.1.0, LSP only, no skills. michelsciortino/dart-lsp (1 star). Both LSP-only.
- Rules/skills: evanca/flutter-ai-rules (645), dart-lang/skills (509, synced into agent-plugins). Small Claude Flutter skill repos (0-3 stars each).
- MCP: leancodepl/marionette_mcp (472, runtime tap/scroll/screenshot), mhmzdev/figma-flutter-mcp (244), adamsmaka/flutter-mcp (74).
- Gap: nobody combines Dart LSP + skills, and nobody covers native build/upgrade breakage (the #1 survey pain). Our plugin should COMPLEMENT the Google plugin, not clone it.

## 3. Technical integration facts
LSP config format (verified from source). Anthropic's official LSP plugins have no files beyond README/LICENSE; config is inline in claude-plugins-official/.claude-plugin/marketplace.json with `"strict": false`, e.g.
`"lspServers": {"rust-analyzer": {"command": "rust-analyzer", "extensionToLanguage": {".rs": "rust"}}}`;
pyright: `"command": "pyright-langserver", "args": ["--stdio"]`; kotlin adds `"startupTimeout": 120000`. Third-party pattern (Shopify liquid-lsp): `.lsp.json` at plugin root = map of name -> config. Strict fields (unknown key = load failure): command, extensionToLanguage (req), args, transport, env, initializationOptions, settings, workspaceFolder, startupTimeout, shutdownTimeout, restartOnCrash, maxRestarts, diagnostics (code.claude.com/docs/en/plugins-reference).

Recommended `.lsp.json`:
```
{"dart": {"command": "dart",
  "args": ["language-server", "--protocol=lsp", "--client-id=analyzer-loop", "--client-version=0.1.0"],
  "extensionToLanguage": {".dart": "dart"},
  "initializationOptions": {"onlyAnalyzeProjectsWithOpenFiles": true},
  "startupTimeout": 60000, "shutdownTimeout": 5000, "maxRestarts": 3}}
```
`onlyAnalyzeProjectsWithOpenFiles` is documented in dart-lang/sdk pkg/analysis_server/tool/lsp_spec/README.md (avoids whole-monorepo analysis). --client-id/--client-version flags [U, not run locally; no Dart SDK on this box]. LSP does not run in Claude Code cloud sessions.

Dart MCP server: package dart_mcp_server 1.1.2 (dart-lang/ai). Since 1.0.0 it "is now shipped on pub instead of through the SDK. The `dart mcp-server` command will continue to work as an alias for `dart run dart_mcp_server@`" (first run may need pub.dev network [U]). Flags: `--dart-sdk`, `--flutter-sdk`, `--log-file`, `--enable/--disable <tool|category>` (alias `--exclude-tool`, `-x`), deprecated `--tools`. Default-on tools: analyze_files, dtd, hot_reload, hot_restart, widget_inspector, get_runtime_errors, lsp (hover/signatureHelp/workspace symbols), pub, pub_dev_search, read_package_uris, rip_grep_packages, vm_service, flutter_driver_command, roots. Default-off: run_tests, dart_fix, dart_format, create_project, launch_app/list_devices/stop_app (category flutter_app_lifecycle). Language server started lazily with 10-min idle timeout (0.1.3). No auth, no rate limits; pub_dev_search hits pub.dev. Claude Code manual add: `claude mcp add --transport stdio dart -- dart mcp-server`.

Key CLIs: `dart analyze --fatal-infos`, `dart fix --dry-run|--apply`, `dart format .`, `flutter pub outdated`, `flutter pub upgrade --major-versions`, `flutter analyze --suggestions` (checks Java/Gradle/AGP compatibility), `./gradlew wrapper --gradle-version=X`, `flutter doctor -v`, `flutter test --update-goldens`, `dart run build_runner build --delete-conflicting-outputs`.

Decision: REUSE, do not build, MCP. Do not bundle it by default: Google's plugin already bundles it as `dart-mcp-server`, VGV as `dart`; each copy can spawn its own analysis server (~2.8-2.9 GB each with 5 sessions, dart-lang/ai#399; OOM crash report misfiled as claude-plugins-official#2771). Skills detect `mcp__*dart*` tools and fall back to CLI.

## 4. Recommended MVP
Hero workflow (<5 min, offline after `pub get`): `samples/stale_app/` = 6-file Flutter app whose pubspec.lock is already on current majors (Riverpod 3, go_router 18) but code still uses old APIs (withOpacity, WillPopScope, MaterialStateProperty, StateNotifierProvider, removed go_router params) -> ~25 analyzer issues + 1 failing golden. User runs `/analyzer-loop:fix-analyzer`. Claude runs `dart fix --apply`, then fixes remaining issues file-by-file with LSP diagnostics after each edit, reruns `dart analyze --fatal-infos` to 0, `flutter test` green. Before/after counts printed by a bundled script.

Components:
1. `.lsp.json` - Dart analysis server (the thing #16849 asked for).
2. skill `fix-analyzer` - drive analyzer to zero: dart fix first, then targeted edits; never add `// ignore:` or loosen analysis_options without asking.
3. skill `pub-upgrade` - `pub outdated` -> major upgrade one package family at a time, read CHANGELOG from pub cache (or MCP read_package_uris), apply migrations, verify; references/migrations.md for Flutter deprecations, Riverpod 3, go_router.
4. skill `android-build-doctor` - parse build error, run `flutter analyze --suggestions`, align gradle-wrapper.properties / settings.gradle(.kts) AGP + Kotlin / JDK using a bundled compatibility table; iOS section for Podfile platform + `pod repo update`. Uncovered by Google and VGV.
5. skill `golden-tests` - add/update goldens with fonts loaded, per-platform tolerance, `--update-goldens` only on explicit request, CI (Linux docker) guidance; recommend alchemist, not discontinued golden_toolkit.
6. skill `state-management` - detect riverpod vs bloc from pubspec, emit current idioms (Riverpod 3 + generator 4, bloc 9).
7. hook SessionStart - warn if `dart` missing or `dart --version` below pubspec `environment.sdk`; mention FVM (`.fvmrc`) mismatch.
Fixtures: stale_app (above), samples/android_mismatch/ (android/ dir only: AGP 7.x + Gradle 7.5 + Kotlin 1.7, with the real error log text), golden fixture with a deliberate 1-px diff.
Leave out: bundled MCP, format-on-save hook (VGV/Google territory, fight risk), widget-building/architecture/l10n/http skills (Google covers them), runtime app driving (marionette), iOS signing, Firebase.

## 5. Eval scenarios
1. "Fix all the analyzer errors in this project" (stale_app). Pass: `dart analyze --fatal-infos` exit 0; zero new `// ignore`; analysis_options.yaml unchanged; dart fix ran before manual edits.
2. "My Android build broke after upgrading Flutter: <log>" (android_mismatch). Pass: runs `flutter analyze --suggestions` or reads gradle files; gradle-wrapper Gradle, AGP, Kotlin versions all edited to a mutually compatible set from the bundled table; no edits under lib/.
3. "Upgrade go_router and riverpod to latest majors". Pass: pubspec majors bumped; CHANGELOG read (tool call visible); analyzer 0; tests pass.
4. "The home screen golden test fails on CI but passes on my Mac". Pass: explains platform font/rendering diff; proposes Linux-generated goldens or tolerance comparator; does NOT run `--update-goldens` unprompted.
5. "Where is CartNotifier used?" Pass: uses LSP tool (findReferences/workspaceSymbol) not grep; lists all 3 call sites with file:line.

## 6. Distribution
Channels: anthropics/claude-code#16849 (comment with install line; 137 reactions = warm list); r/FlutterDev [U size]; Flutter forum forum.itsallwidgets.com (Gradle-upgrade threads exist, e.g. "Help to upgrade AGP"); Flutter Discord / Flutter Community Slack [U]; Flutter Tap / Flutter Weekly / Code With Andrea newsletters [U]; flutter/agent-plugins#162 and #233 (awesome lists); submit to claude-plugins-official (no Dart LSP there; the LSP recommendation dialog then auto-offers it to anyone with `dart` on PATH - biggest lever); dart-lang/sdk#63298 (LSP RAM).
Positioning: "The Dart language server for Claude Code, plus the upgrade and Android-build fixes the official Flutter plugin does not cover. Install both."
Name check: `flutter-dart` collides with Google's `dart-flutter` (same words, swapped) AND breaks our CONVENTIONS (no trademark as leading word). `analyzer-loop`: no GitHub/pub collision found. Alt `pubwright` (pub.dev 404, no GitHub repo).

## 7. Risks
- Trademark: Flutter/Dart are Google marks. Flutter guidelines: "Don't incorporate the Flutter trademarks into your own product names" and nothing implying Google built/endorses it. Use only "for Flutter" descriptively, no logo; README: "Not affiliated with or endorsed by Google LLC. Flutter and Dart are trademarks of Google LLC." [exact disclaimer text U].
- Being obsoleted: Google or Anthropic could ship a Dart LSP entry any week (it is a 10-line config). Value must sit in the upgrade/build/golden skills.
- Memory: analysis server can hit 20 GB (dart-lang/sdk#63298); LSP + up to two MCP copies triple it. Mitigate with onlyAnalyzeProjectsWithOpenFiles, shutdownTimeout, no bundled MCP, README note.
- `dart` on PATH may be the wrong SDK (FVM/puro); LSP command cannot be per-project. Document `dart` shim or absolute path.
- Hero needs Flutter SDK (~1-2 GB) and a one-time `pub get`; Claude Code web has no Dart SDK (#45524 closed) and no plugin LSP.
- Gradle builds take >5 min cold; evals for android-build-doctor must grade the file edits, not a full build.
- Fast churn (go_router 18, Riverpod 3.x): migration tables need dated sources and a refresh cadence.

## 8. Day-30 signal
Not stars alone. Watch: (a) reactions/replies on #16849 after our comment and installs referencing it; (b) number of GitHub issues from strangers pasting real Android/Gradle or upgrade error logs (target >= 5) - proves the upgrade-pain wedge, not just LSP; (c) whether the plugin is accepted into claude-plugins-official (unlocks the auto-recommendation dialog). If (b) is ~0 while LSP praise is high, cut skills and contribute the LSP upstream instead.
