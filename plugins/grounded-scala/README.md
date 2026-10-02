# Grounded Scala

Scala language server (Metals) and workflow skills for Claude Code.

Claude Code sees Scala the way Metals does: type errors after every edit,
symbol-true navigation (givens, extension methods and aliases included), and
a compile-fix loop that keeps the build warm instead of restarting sbt.

For backend Scala engineers on Scala 3 or 2.13 (sbt, Mill or scala-cli,
cats-effect, ZIO or Ox) who use Claude Code daily.

Works in: Claude Code CLI and IDE extensions. Not in cloud/web sessions or
Cowork (language servers do not run there).

## Install (60 seconds)

1. Install Metals once (needs a JDK 17+):

   ```
   cs install metals          # Coursier; get cs at https://get-coursier.io
   ```

   Make sure `which metals` works in the shell you start Claude Code from.
   `cs install` puts it in `~/.local/share/coursier/bin` (Linux) or
   `~/Library/Application Support/Coursier/bin` (macOS); run `cs setup` if
   that is not on your PATH.

2. Install the plugin:

   ```
   /plugin marketplace add brianshepardpss/plugin-creator
   /plugin install grounded-scala@plugin-creator
   ```

3. Restart Claude Code in your project root.

Not working? Ask "why isn't Metals working?" and the scala-doctor skill runs a
read-only check and prints the exact fix.

## Try it in 5 minutes

Needs `scala-cli` (`cs install scala-cli`). In an empty folder:

```
/grounded-scala:fix sample
```

Claude copies `samples/ce-broken` (a cats-effect app with three seeded
errors), compiles it once, fixes the errors root-cause first using Metals
diagnostics, recompiles to green and reports each fix. One of the errors is a
trap: the compiler suggests importing the global ExecutionContext; the plugin
fixes it with `IO` instead. The first compile downloads cats-effect and
the Scala compiler; later compiles take seconds.

## What it does

| Piece | What it gives you |
|---|---|
| `.lsp.json` (Metals) | Diagnostics after each edit and LSP navigation for `.scala .sc .sbt .mill`. Auto-imports the build headlessly (no "Import build?" prompt). |
| skill `fix-compile` | Warm compile (`sbt --client`, `scala-cli`, `./mill`), grouped root-cause fixes, never `clean`, never silences errors. Command: `/grounded-scala:fix`. |
| skill `scala-doctor` | Read-only setup check (java, metals, cs, build tool, .gitignore, Metals logs) with exact install commands. |
| skill `scala-build` | Dependencies with the right `%%` / `::` per tool, version lookup via `cs complete-dep`, targeted test runs, cross-building, sbt 1 -> 2 checklist. |
| skill `scala3-migrate` | Staged 2.13 -> 3 migration: scala3-migrate or `-source:3.0-migration -rewrite`, then implicits -> given/using/extension. Sample: `samples/sbt-213`. |
| skill `effects-idioms` | Detects cats-effect / ZIO / Ox and keeps one style: no Future/Await mixing, scoped resources, typed errors. |
| agent `scala-navigator` | Read-only "who calls X / where is this given defined" through Metals, returned as a short file:line list. |
| command `/grounded-scala:metals-mcp` | Opt-in: adds the official `metals-mcp` server (compile, test, inspect, find-dep tools) to this project after asking. Not bundled, since it starts a second JVM. |

## Configuration notes

The language server runs `metals` with `-J-Dmetals.auto-import-builds=all`
(plus the matching `autoImportBuilds` setting),
`isExitOnShutdown`, and a 180 s startup timeout for first imports. If you
already use another Scala LSP plugin, disable one of them in `/plugin`.
Running your IDE's Metals on the same project at the same time is fine.

Requires Claude Code 2.1.287 or later (the `.lsp.json` uses
`shutdownTimeout`, `restartOnCrash` and `maxRestarts`). Tested 2026-10-02 with Claude Code 2.1.287, Metals 1.6.9, scala-cli 1.17.1 on
Linux: diagnostics and find-references work on the bundled samples. sbt and
Mill paths follow the tools' documentation but were not run in that test.

## Privacy

Nothing leaves your machine beyond your normal Claude conversation. Metals,
sbt, Mill and scala-cli download libraries from Maven repositories when they
build. The plugin has no telemetry and no keys.

## Feedback

Say "I wish this could..." and the request skill drafts an issue for you to
file. Nothing is sent automatically.

## License

MIT. Metals is Apache-2.0 and is installed by you; this plugin only launches it.

Not affiliated with or endorsed by the Scala Center or EPFL.
Not affiliated with or endorsed by Scalameta (Metals).
Not affiliated with or endorsed by VirtusLab, Typelevel, the ZIO project, SoftwareMill or com-lihaoyi (Mill).
