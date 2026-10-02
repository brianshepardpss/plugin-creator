# Research brief: `scala-metals` plugin (proposed slug `grounded-scala`, see 6)
Date: 2026-10-02. Verified against Claude Code 2.1.287 docs + live GitHub. [U] = unverified.

## 1. Target user and jobs-to-be-done
User: backend Scala engineer or tech lead on a Scala 3 (or 2.13 migrating) codebase, sbt (80% of devs) / scala-cli (~50%) / Mill (20%), cats-effect or ZIO, using Claude Code daily. Scala Survey 2026 (VirtusLab, n=1,056): "tooling in general remains the #1 concern, closely followed by compile / build speed"; 70% use Metals-based editors; 49% plan a 2->3 migration.

Ranked pain x frequency:
1. Claude cannot see Scala type errors until a slow full build (every edit, high). No official Scala LSP plugin; anthropics/claude-code#45132 "Add Scala (Metals) to the native LSP plugin lineup" is OPEN, 97 thumbs-up, 15 comments; dupes #24734, #24735, #48094 closed into it. CTO quote: "Missing this LSP support is heavily hampering our productivity." 68 thumbs-down on the bot's auto-dup-close.
2. Grep is wrong for Scala navigation (daily, high). "Implicits, extension methods, type aliases, and givens mean grep misses call sites and returns false positives constantly" (#45132). Benchmark on 347k LOC: grep found 37 hits with false positives vs 107 true refs from Metals.
3. sbt cold-start per command (every compile/test, high). #16663: each `sbt compile` via Bash "starts new JVM ... (~15-30 seconds)", loses incremental state. Codex-for-Scala guide lists "Runs `sbt clean` repeatedly" as a top agent failure.
4. Agents write Scala 2 / mixed-paradigm code (daily, medium). Same guide: generates `implicit` not `given`; "Mixes `Future` with `IO`"; ignores exhaustivity warnings.
5. Scala 2.13 -> 3 and sbt 1 -> 2 migrations (episodic, high value). sbt 2.0.9 is current stable; Scala 3.9.0 / LTS 3.3.x.
6. DIY setup is fragile (one-time, high friction). #66308 (settings.json `lsp` key never invoked metals), #15168 (+15, "No LSP server available"), Piebald#56 (metals plugin failed on `shutdownTimeout`), #45132 comment: "never bullet proof ... claude would silently fallback to grep."
Reddit/HN Scala-specific threads: none high-signal found [U]; demand lives on GitHub + Scala Discourse.

## 2. Competition
- Official (anthropics/claude-plugins-official): 12 LSP plugins + Shopify liquid; NO Scala. Risk Anthropic adds `metals-lsp` (would take the recommendation dialog: "Official first").
- Piebald-AI/claude-code-lsps (521 stars) `metals` plugin: bare `.lsp.json` (command metals, initializationOptions isExitOnShutdown + statusBarProvider log-message, startupTimeout 90000, maxRestarts 3). Lacks: build auto-import settings, doctor/install, skills, compile loop, Mill ext, docs. boostvolt/claude-code-lsps (183): no Scala.
- metals-mcp (in scalameta/metals, 2,332 stars, Apache-2.0): maintainer tgodzik recommends it for agents. 17 tools (compile-file/module/full, test, glob-search, inspect, get-docs, get-usages, get-source, import-build, find-dep, list-modules, format-file, scalafix tools). Lacks: workflow guidance, latency (see 3), separate JVM.
- oraios/serena (29.9k stars): MCP wrapper supporting Metals; reported "order of magnitude slower than grep".
- NovaMage/agents-metals-direct-lsp (4), magaransoft/claude-lsp-direct (4, MIT): curl-to-metals-mcp-HTTP batching hacks; install.sh edits settings.json.
- VirtusLab/scala-skill (76 stars): direct-style (Ox/tapir) skill pack, Claude + Codex; no LSP, no CE/ZIO, no migration. Complementary, cross-link.
- Generic agents: rohitg00 toolkit scala-developer.md, 0xfurai scala-expert.md, moai-lang-scala: prose personas, no tooling.
- Other AI tools: Cursor/VS Code Copilot get Metals MCP auto-configured via `metals.startMcpServer`; JetBrains AI/Junie ride IntelliJ Scala plugin (80% use IntelliJ); Codex CLI guide (danielvaughan, 2026-05-21) = metals-mcp + AGENTS.md.
Gap: nobody ships a validated one-install Metals LSP + doctor + Scala workflow skills for Claude Code.

## 3. Technical integration facts
- LSP plugin format. Official plugins put config in marketplace.json entry with `"strict": false`, e.g. kotlin: `"lspServers": {"kotlin-lsp": {"command":"kotlin-lsp","args":["--stdio"],"extensionToLanguage":{".kt":"kotlin",".kts":"kotlin"},"startupTimeout":120000}}`; jdtls: `{"command":"jdtls","extensionToLanguage":{".java":"java"},"startupTimeout":120000}`; rust-analyzer: command + extensionToLanguage only. Plugin dirs hold only README+LICENSE. For third-party marketplaces ship `.lsp.json` at plugin root (#53399: marketplace `lspServers` alone was ignored on 2.1.119 [U still true]).
- `.lsp.json` schema (strict; unknown key = load failure): required `command`, `extensionToLanguage`; optional `args, transport (stdio|socket, always stdio), env, initializationOptions, settings (sent via workspace/didChangeConfiguration), workspaceFolder, startupTimeout, shutdownTimeout, restartOnCrash, maxRestarts, diagnostics`. Older CC rejected restartOnCrash/maxRestarts/shutdownTimeout as "not yet implemented" -> omit unless `claude plugin validate --strict` passes and set min version. `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PROJECT_DIR}` resolve in command/args/env.
- LSP tool: diagnostics pushed after each Edit/Write ("Found N new diagnostic issues"); ops: definition, references, hover/type, documentSymbol, workspaceSymbol, implementations, call hierarchy. Read-only. Not started in cloud sessions. Recommendation dialog offers plugins from added marketplaces when binary on PATH.
- Metals: v1.6.9 (2026-09-14), 2.0.0-M19 pre-release. Install `cs install metals` (Coursier) or `brew install metals` (brew lags: 1.6.7, depends openjdk@25). JVM required (JDK 17+ [U exact min]). No auth, no keys, no rate limits; network only for Maven/Coursier downloads.
- Metals headless knobs: user config `auto-import-builds` = off|initial|all (camelCase `autoImportBuilds` also read; also `-Dmetals.auto-import-builds`) avoids the "Import build?" showMessageRequest a headless client may never answer [U how CC answers]. `-Dmetals.h2.auto-server=on` (default) lets plugin Metals coexist with the user's IDE Metals. Logs: `.metals/metals.log`, pre-connect `~/.cache/org.scalameta.metals/global.log`. initializationOptions: isExitOnShutdown, statusBarProvider, isHttpEnabled, compilerOptions.
- metals-mcp: `cs install metals-mcp`; `metals-mcp --workspace <path> [--transport http|stdio] [--port N] [--client claude] [--<config-key> v]`; endpoint `http://localhost:<port>/mcp` (moved from /sse in 1.6.5); in-editor port in `.metals/mcp.json`.
- Latency: #45132 measured get-usages 0.029s direct HTTP vs 6.7s (stdio) / 7.5s (http) through Claude. Timing wraps the whole agent turn, so most is model round-trip, not transport [our reading]; same cost applies to native LSP calls (~8-9s per claude-lsp-direct). Design implication: few, targeted lookups; batch.
- Builds: `sbt --client <cmd>` (thin client, keeps warm server); scala-cli compiles via Bloop server; Mill runs a daemon (`./mill`). Migration: scalacenter/scala3-migrate (sbt plugin), `-source:3.0-migration -rewrite`, Scalafix (875 stars).

## 4. Recommended MVP
Hero workflow (<5 min): `cs install metals` -> `/plugin install grounded-scala@plugin-creator` -> open `samples/ce-broken` (scala-cli project, `project.scala` with `//> using scala 3.3.x` + cats-effect) -> "fix the compile errors". Claude edits, sees Metals diagnostics inline, runs `scala-cli compile .` once to confirm green, reports each fix. Cold import budget is the risk; scala-cli sample keeps it ~1-2 min [U, time it].

Components:
- `.lsp.json`: metals; ext `.scala .sc .sbt .mill` -> scala; initializationOptions {isExitOnShutdown:true, statusBarProvider:"log-message"}; settings {metals:{autoImportBuilds:"all"}} [U payload shape]; startupTimeout 180000.
- skill `scala-doctor`: checks java, cs, metals on PATH, build tool detected, .metals/.bloop in .gitignore, Metals log errors; prints exact install commands (bundled stdlib Python script).
- skill `fix-compile` (hero): detect build tool, compile via fastest warm path (sbt --client / scala-cli / ./mill), group errors, use LSP hover/definition only where types matter, fix, recompile, never `clean`.
- skill `scala-build`: add deps (correct `%%`/`::` per tool, latest via `cs complete-dep`), cross-build, sbt 1->2 notes, test-only runs.
- skill `scala3-migrate`: 2.13->3 procedure (migration plugin, rewrite flags, implicit->given/using, wildcard/varargs syntax, macro blockers).
- skill `effects-idioms`: detect CE3/ZIO2/Ox from deps; rules (one effect system, Resource/ZIO.scoped, Ref, no Await/Future mixing, typed errors); reference files per stack.
- agent `scala-navigator`: read-only subagent for "who calls X / where is this given defined" that uses LSP references and returns a summary, keeping main context clean.
- `/scala-metals:mcp-on` command (opt-in): adds project-scoped metals-mcp (stdio) for test/inspect/find-dep. Not bundled in `.mcp.json`: second JVM, ~1GB+ RAM [U].
Hooks: none in MVP (LSP already pushes diagnostics). Fixtures: `samples/ce-broken` (scala-cli, 3 seeded errors: missing given, Scala-2 implicit class, IO/Future mix), `samples/sbt-213` (tiny 2.13 project for migration), `samples/zio-app`. Leave out: Bazel/Gradle tuning, bundling Metals/JDK, batch HTTP proxy (v2), Scala.js/Native, worksheet support, IntelliJ.

## 5. Eval scenarios
1. "This project doesn't compile, fix it" (ce-broken). Pass: `scala-cli compile .` exits 0; no `sbt clean`; no `implicit` added; summary lists 3 fixes.
2. "Find every caller of `UserRepo.findById`" (sample with extension-method + alias call sites). Pass: uses LSP references or metals-mcp get-usages; returns all N seeded sites, 0 false positives.
3. "Migrate samples/sbt-213 to Scala 3" Pass: scalaVersion 3.x, compiles, implicits converted to given/using, migration steps listed.
4. "Add a /health endpoint with http4s and a test" in CE project. Pass: correct `%%` dep, Resource-based server, no Future, `sbt --client test` green.
5. "Why isn't Scala code intelligence working?" (metals absent from PATH). Pass: doctor names missing binary and gives `cs install metals`; makes no config edits.

## 6. Distribution
- anthropics/claude-code#45132 (97 reactions; comment with install line), #48094/#15168 watchers; Piebald#54 thread.
- Scala Contributors "Rallying native Scala Metals LSP support in Claude Code" (contributors.scala-lang.org/t/7437), users.scala-lang.org, r/scala, r/ClaudeCode, Scala Discord, Typelevel Discord, ZIO Discord, This Week in Scala, Scala Times, @ScalaSpace on X; ask tgodzik (Metals) re: linking from docs/features/mcp.md; cross-link VirtusLab/scala-skill.
- One-liner: "Claude Code that sees Scala like Metals does: type errors after every edit, symbol-true navigation, and a compile-fix loop that never restarts sbt."
- Name: `scala-metals` breaks our convention (third-party mark as leading word: Scala is an EPFL trademark; Metals is a scalameta project). Recommend slug `grounded-scala`, displayName "Grounded Scala (Metals LSP)" [U marketplace collision check]. Piebald already uses `metals`.

## 7. Risks
- Legal: EPFL Scala trademark (permissive, no endorsement implication); Metals Apache-2.0, we only invoke it. README: "Not affiliated with or endorsed by EPFL, Scala Center, Scalameta or VirtusLab."
- Obsolescence: Anthropic may ship an official metals plugin; moat must be skills + doctor + evals, not `.lsp.json`.
- Diagnostics depend on Metals compiling via BSP after didSave; whether CC sends didSave/which diagnostics surface for Scala 2 vs 3 is [U] - must test day 1.
- Cold import 1-5 min on real sbt builds; startupTimeout and first-run messaging matter. Memory: Metals + Bloop + sbt JVMs.
- Per-call LSP latency (~7s turn cost) makes chatty navigation slow; skills must batch/limit.
- Schema drift (restartOnCrash etc. rejected on older CC); pin min CC version. LSP absent in cloud/Cowork: plugin is CLI-only.

## 8. Day-30 signal
Distinct users confirming "diagnostics work" on #45132/our repo across >=3 build tools (sbt, scala-cli, Mill), target >=10, plus one Metals maintainer acknowledgement/link. Secondary: >=40 GitHub stars, and zero open "server never starts" reports older than 7 days.
