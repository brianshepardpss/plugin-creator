# Metals troubleshooting notes (read on demand)

Verified 2026-10-02 with Metals 1.6.9, scala-cli 1.17.1, Claude Code 2.1.287.

## How the plugin starts Metals

`.lsp.json` runs `metals -J-Dmetals.client=claude-code -J-Dmetals.auto-import-builds=all`
(the Coursier launcher forwards `-J` arguments to the JVM as system properties)
over stdio for `.scala .sc .sbt .mill` files, with
`initializationOptions {isExitOnShutdown: true, statusBarProvider: "log-message"}`
and settings `{metals: {autoImportBuilds: "all"}}` so Metals imports the build
without waiting on an "Import build?" prompt that a headless client never
answers. `startupTimeout` is 180 s because the first import downloads
dependencies.

## Prompts Metals may raise that are safe to ignore

- "Http server is required for such features as Metals Doctor..." - the HTML
  doctor is an editor feature; diagnostics and navigation work without it.
- "Metals might not work correctly for N build targets in this workspace due
  to mis-configuration" - usually missing JDK sources or semanticdb on one
  target; read `.metals/metals.log` only if navigation is actually broken.

## Logs

- Per project: `.metals/metals.log`
- Before Metals has a workspace: `~/.cache/org.scalameta.metals/global.log`
  (macOS `~/Library/Caches/org.scalameta.metals/global.log`)

## Common causes, in order of frequency

1. `cs install metals` put the binary in `~/.local/share/coursier/bin`
   (Linux) or `~/Library/Application Support/Coursier/bin` (macOS) and that
   directory is not on PATH. `cs setup` or a PATH line fixes it.
2. No JDK, or Claude Code inherited a different PATH (GUI launch). Start
   Claude Code from a terminal where `java -version` and `which metals` work.
3. sbt project but `sbt` not installed: Metals can still import the build
   (it embeds an sbt launcher), but the fix-compile loop cannot run
   `sbt --client` from Bash. `cs install sbt`.
4. Build import failed (bad sbt plugin resolution, private repo credentials):
   `.metals/metals.log` has the error; reproduce with `sbt compile`.
5. Two LSP plugins for Scala installed: disable one in `/plugin`.
6. Running the user's IDE Metals on the same project at the same time is fine:
   Metals uses an H2 auto-server so both can share `.metals/`.
