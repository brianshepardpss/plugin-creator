# Launch plan: Grounded Scala

## Positioning

One line: "Claude Code that sees Scala like Metals does: type errors after
every edit, symbol-true navigation, and a compile-fix loop that never
restarts sbt."

Why now: anthropics/claude-code#45132 ("Add Scala (Metals) to the native LSP
plugin lineup") is open with ~97 reactions and several closed duplicates;
there is no official Scala LSP plugin. Existing third-party options are a bare
`.lsp.json` (Piebald `metals`) or MCP wrappers. Our moat is the doctor,
the compile-fix loop, migration/effect skills and shipped evals, not the
`.lsp.json` (Anthropic may ship one; then we document "use theirs plus our
skills").

## Audience and where they are

- GitHub: anthropics/claude-code#45132 watchers (and #48094, #15168),
  Piebald-AI/claude-code-lsps#54.
- Scala Contributors: "Rallying native Scala Metals LSP support in Claude
  Code" (contributors.scala-lang.org/t/7437); users.scala-lang.org.
- r/scala, r/ClaudeCode.
- Discord: Scala, Typelevel, ZIO.
- Newsletters: This Week in Scala, Scala Times. X: @ScalaSpace.
- Metals maintainers (tgodzik): ask, do not pitch, about a link from the
  metals docs page on MCP/agents once users confirm it works.
- Cross-link VirtusLab/scala-skill (direct-style skills; complementary).

## Rules we follow

- One post per community, written for it; no cross-posting the same text.
- Disclose we built it in every post. No vote/star asks.
- GitHub issues: comment only where it answers the thread's ask, once.
- Do not post until the evals pass and one non-author has installed it on a
  real sbt project.

## Post drafts

### 1. GitHub comment on anthropics/claude-code#45132

> For anyone who needs Scala LSP today: we published a third-party plugin,
> Grounded Scala, that registers Metals via `.lsp.json` (strict-schema
> checked on 2.1.287) with headless build auto-import, plus a read-only
> setup doctor and a compile-fix skill that uses `sbt --client`.
>
> ```
> cs install metals
> /plugin marketplace add brianshepardpss/plugin-creator
> /plugin install grounded-scala@plugin-creator
> ```
>
> Tested with scala-cli on Linux: diagnostics arrive a few seconds after an
> edit, find-references resolves aliases/extension/given call sites. sbt and
> Mill reports welcome in the repo issues. Disclosure: I maintain it. Happy to
> drop it once an official Metals plugin lands.

### 2. Scala Contributors thread (t/7437) reply

> Status update from the Claude Code side: until there is an official
> Metals plugin, here is an MIT plugin that wires Metals 1.6.x into Claude
> Code's LSP tool. Two details that mattered for headless use:
> `auto-import-builds=all` (the client never answers "Import build?") and
> the first-call "server is starting" window, which the skills handle by
> compiling via the build tool first. It ships three sample projects
> (scala-cli + cats-effect with seeded errors, a navigation fixture with
> alias/extension/given call sites, a 2.13 sbt project for migration) and
> evals. Feedback from sbt-heavy and Mill builds especially welcome:
> github.com/brianshepardpss/grounded-scala (I'm the author).

### 3. r/scala post

Title: "Metals in Claude Code: a plugin with diagnostics, navigation and a
no-`sbt clean` compile loop (MIT)"

> I got tired of Claude Code grepping for implicits and restarting sbt for
> every compile, so I packaged Metals as a Claude Code plugin with a few
> Scala-specific skills: compile-fix (sbt --client / scala-cli / ./mill,
> never clean, never `import global` into IO code), 2.13 -> 3 migration,
> effect-system style for CE/ZIO/Ox, and a read-only navigator that uses
> find-references instead of grep. There's a broken cats-effect sample you
> can try in an empty folder with `/grounded-scala:fix sample`.
> Known limits: needs `metals` on PATH, cold sbt imports take minutes, not
> available in cloud sessions. I'm the author; issues and "it didn't work on
> my build" reports are the most useful thing you can send.

### 4. This Week in Scala submission (link + one line)

> Grounded Scala - MIT Claude Code plugin that wires Metals diagnostics and
> navigation into Claude Code, with compile-fix, Scala 3 migration and
> effect-style skills. github.com/brianshepardpss/grounded-scala

## Directory listing text

Name: Grounded Scala
Short: Scala language server (Metals) and workflow skills for Claude Code.
Long: Registers Metals as Claude Code's Scala language server (diagnostics
after edits, references, definitions, hover) with headless build import, and
adds skills for a warm compile-fix loop (sbt, Mill, scala-cli), build changes,
Scala 2.13 -> 3 migration and cats-effect/ZIO/Ox style, plus a read-only
navigation agent and a setup doctor. Requires `metals` on PATH (cs install
metals). Claude Code CLI/IDE only. Not affiliated with the Scala Center, EPFL
or Scalameta.
Keywords: scala, metals, lsp, sbt, scala-cli, mill, cats-effect, zio, scala3

## Day-30 signal and thresholds

| Signal | Target by day 30 | Kill/rethink below |
|---|---|---|
| Distinct users confirming "diagnostics work" (repo issues/discussions, #45132) across sbt, scala-cli and Mill | >= 10, all three tools represented | < 3 |
| Metals maintainer acknowledgement or docs link | 1 | 0 is fine; not a kill signal |
| GitHub stars on grounded-scala | >= 40 | < 10 |
| Open "server never starts" reports older than 7 days | 0 | any |

If Anthropic ships an official Metals plugin before day 30: drop our
`.lsp.json` in a minor release, keep the skills, and re-measure on skill use.
