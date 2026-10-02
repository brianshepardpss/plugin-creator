---
name: fix-compile
description: Use when Scala code does not compile or the user says "fix the compile errors", "it doesn't build", "sbt compile fails", "make it green", "fix these type errors", "red squiggles in my Scala", or pastes scalac/Metals errors. Runs a warm compile (sbt --client, scala-cli, ./mill), fixes errors root-cause first using Metals diagnostics, recompiles, and reports each fix. Accepts `sample` to run on the bundled broken cats-effect project.
---

# Compile-fix loop for Scala

Goal: a green compile with idiomatic fixes, in as few build invocations as
possible. Metals diagnostics arrive after every Edit/Write; the build tool is
the final judge.

## Rules (apply to every step)

- Never run `sbt clean`, `./mill clean`, `scala-cli clean`, or delete
  `target/`, `.bloop/`, `.scala-build/` or `out/` unless the user asks. They
  throw away incremental state and cost minutes.
- Never start a fresh sbt JVM per command (`sbt compile`). Use
  `sbt --client <cmd>`, which reuses one warm sbt server.
- Never silence errors to get green: no `asInstanceOf`, no `@nowarn`, no
  removing `-Xfatal-warnings`/`-Werror`, no `???` in place of logic, no
  commenting code out. If a real fix needs a decision, stop and ask.
- Scala 3 code: write `given`/`using`/`extension`, never new `implicit`
  definitions or implicit classes.
- In cats-effect or ZIO code, never fix an effect error by importing
  `ExecutionContext.Implicits.global`, adding `Await.result`, or wrapping in
  `Future`, even when the compiler message suggests it. Use the effect
  system's own constructor (see the effects-idioms skill).
- Keep public signatures unless the error is in the signature itself; list any
  signature change in the report.

## How Metals behaves in Claude Code (tested)

- Metals starts lazily on the first Scala file touched. For the first
  10-60 s (minutes on a cold sbt build) LSP calls can fail with "server is
  starting"; that is normal. The build tool compile in step 3 does not wait
  on Metals.
- Diagnostics are compiled in the background and arrive a few seconds after
  an Edit, usually attached to a later tool result, not the Edit itself.
  Absence of diagnostics right after an Edit is not proof the file is clean.
- While a file has syntax errors, references and hover can be incomplete.
  Fix parse errors first.

## Procedure

1. **Pick the project.** If the user said `sample`, copy the bundled sample
   (never edit the plugin's own files). Metals uses the directory Claude Code
   was started in as its workspace, so:
   - current directory empty (or only hidden files): copy the sample's
     contents into it: `cp -r <skill dir>/../../samples/ce-broken/. .`
   - otherwise: `cp -r <skill dir>/../../samples/ce-broken ./ce-broken` and
     tell the user Metals diagnostics need Claude Code started inside
     `ce-broken`; the build-tool loop still works.
2. **Detect the build tool** from the project root:

   | Marker | Tool | Compile | Test |
   |---|---|---|---|
   | `build.sbt` or `project/build.properties` | sbt | `sbt --client compile` (or `Test/compile`) | `sbt --client "testOnly <Suite>"` |
   | `build.mill`, `build.mill.scala`, `build.sc` | Mill | `./mill __.compile` (or `./mill <module>.compile`) | `./mill <module>.test` |
   | `project.scala` or `//> using` headers | scala-cli | `scala-cli compile .` | `scala-cli test .` |

   If several match, prefer sbt, then Mill. Use `./mill` if the repo has it,
   else `mill`. If the tool is not installed, say so and run the scala-doctor
   skill instead of guessing.
3. **Collect errors once.** Run the compile command a single time and capture
   the output. Strip ANSI colours when reading. If Metals diagnostics are
   already visible for the files, use them too.
4. **Group by root cause**, not by line. Order: syntax/parse errors first
   (they hide type errors), then missing givens/imports, then type
   mismatches, then warnings promoted to errors.
5. **Look up types only where needed.** Use the LSP tool (`hover`,
   `goToDefinition`) for a symbol whose type you cannot read from the file.
   Each LSP call costs a full turn; do at most a handful per iteration and
   prefer reading the definition file once.
6. **Fix** each root cause with the smallest idiomatic change. After each
   Edit, read the new Metals diagnostics for that file before moving on.
7. **Recompile** with the same command. Repeat steps 4-7 at most 5 times. If
   the error count does not drop between two iterations, stop and report
   what is blocking.
8. **Report** using the template below. Leave the sbt server running (it is
   the point); mention `sbt --client shutdown` if the user wants it gone.

## Report template

```
Build: <tool> - <command used>   Result: <GREEN | still N errors>
Iterations: <n>

Fixes
1. <file>:<line> - <error in a few words> -> <what you changed and why>
2. ...

Not changed / needs a decision
- <item, or "none">
```

## Known errors in the bundled sample (for orientation, do not hardcode)

`samples/ce-broken` has three seeded errors: a missing `given Show[Order]`,
Scala 2 procedure syntax, and a `Future` returned where `IO` is promised. The
compiler suggests importing the global ExecutionContext for the third; the
correct fix is `IO(...)`/`IO.blocking(...)`, not the import. The run prints a
total of 27.00 once green (`scala-cli run .`).
