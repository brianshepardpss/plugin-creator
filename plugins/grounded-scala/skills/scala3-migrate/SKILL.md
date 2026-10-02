---
name: scala3-migrate
description: Use when moving Scala 2.13 code to Scala 3, or when the user says "migrate to Scala 3", "upgrade scalaVersion to 3", "port this from Scala 2", "convert implicits to given", "get rid of implicit classes", "cross-build for Scala 3". Runs a staged migration (dependencies, scalacOptions, compiler rewrites, then idiomatic given/using/extension) and verifies each stage compiles. Try it on the bundled samples/sbt-213 project.
---

# Scala 2.13 -> Scala 3 migration

Staged, each stage compiles before the next. Never mix the migration with
feature work or reformatting.

## Guardrails

- Start from a green 2.13 build. If it is red, run the fix-compile skill first.
- Macro-based code (Scala 2 `def macro`, `scala.reflect.macros`, libraries that
  only ship 2.13 macros such as old shapeless 2 derivation) cannot be migrated
  mechanically. List every such file and library as a blocker and stop on
  that module; do not stub it out.
- Library upgrades: change versions only to ones that exist with a `_3`
  artifact (check with `cs complete-dep org:name_3:`). Report each change.
- Keep behaviour: implicit -> given conversions must not change which instance
  is selected. If two candidates would become ambiguous, keep an explicit
  import and say so.
- Never drop `-Xfatal-warnings`/`-Werror` to finish.

## Procedure

1. **Inventory.** Read the build file(s). Record: Scala version, build tool,
   sbt version, `scalacOptions`, every dependency, and any compiler plugins
   (`kind-projector`, `better-monadic-for`, `paradise`). Grep for
   `macro`, `scala.reflect`, `implicit class`, `implicit def`, `: _*`, `'sym`.
2. **Mechanical rewrite with the compiler.** Choose one path:
   - sbt with scala3-migrate (sbt 1.5+, Scala 2.13.x): add
     `addSbtPlugin("ch.epfl.scala" % "sbt-scala3-migrate" % "0.7.5")` to
     `project/plugins.sbt` (check for a newer version first), then in order:
     `migrateDependencies <project>`, `migrateScalacOptions <project>`,
     `migrateSyntax <project>`, `migrateTypes <project>`. Apply what each
     reports before the next.
   - Any tool, compiler only: set `scalaVersion` to the target (3.3.x LTS
     unless the user wants latest) and compile once with
     `-source:3.0-migration -rewrite`. For scala-cli:
     `scala-cli compile . --scala 3.3.7 -O -source:3.0-migration -O -rewrite`.
     Then remove those two flags.
   Read `rewrites.md` for the compiler-plugin and option mapping.
3. **Compile on Scala 3** with the warm command (see fix-compile). Fix the
   remaining errors with the fix-compile loop.
4. **Idiomatic pass** (only after green), file by file, recompiling after each
   file:
   - `implicit val/object x: T` -> `given x: T = ...` / `given T with`
   - `(implicit p: T)` parameters -> `(using p: T)`; call sites passing
     explicitly need `(using ...)`
   - `implicit class Ops(x: A)` -> `extension (x: A) def ...`
   - `implicit def f(a: A): B` -> `given Conversion[A, B] = ...` and say the
     call sites now need `import scala.language.implicitConversions`, or
     better, make them explicit
   - `xs: _*` -> `xs*`; `import a._` -> `import a.*`; `'sym` -> `Symbol("sym")`
   - Importers of givens need `import X.given` (or `import X.{given, *}`).
5. **Verify**: compile and run the tests on Scala 3. If the project
   cross-builds, also run the 2.13 build.
6. **Report** with the template.

## Report template

```
Migrated: <project/modules>  Scala <from> -> <to>  Build: <tool>
Result: <GREEN on Scala 3 | blocked>

Stages
1. Dependencies: <changes or "none">
2. scalacOptions / compiler plugins: <changes>
3. Compiler rewrites: <what -rewrite / migrateSyntax changed>
4. Manual fixes: <file:line - change>
5. Idiomatic pass: <n> implicits -> given/using, <n> implicit classes -> extension, ...

Blockers / follow-ups
- <macro library, ambiguous given, or "none">
```

## Sample

`samples/sbt-213` (sbt, Scala 2.13.16) has implicit vals, an implicit class,
an implicit conversion, `: _*`, procedure syntax and a symbol literal. Copy
its contents into the current directory if it is empty
(`cp -r <skill dir>/../../samples/sbt-213/. .`), else into `./sbt-213`. If `sbt` is not installed, use
the compiler-only path with scala-cli on `src/main/scala`.
