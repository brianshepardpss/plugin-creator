---
name: scala-build
description: Use when changing a Scala build or running part of it, or when the user says "add a dependency", "add http4s/circe/zio to the build", "which version of X", "run just this test", "cross-build for 2.13 and 3", "upgrade to sbt 2", "set up Mill", "convert to scala-cli". Covers sbt, Mill and scala-cli with the right dependency syntax per tool and warm, targeted commands.
---

# Build changes for sbt, Mill and scala-cli

## Rules

- Detect the tool first (`build.sbt` -> sbt; `build.mill`/`build.sc` -> Mill;
  `project.scala` or `//> using` -> scala-cli). Change only that tool's files.
- Never invent a version number. Look it up (step 2) and show the command
  output that gave it.
- Run commands warm and targeted: `sbt --client`, one module, one suite.
  Never `clean`.
- Show the exact diff of a build file before writing it when the change adds
  a resolver, a plugin, or a credential. Never write credentials into a build
  file; point at env vars or `~/.sbt/` / `~/.mill/` config instead.

## 1. Dependency syntax (Scala libraries use the cross-version separator)

| Tool | Scala library | Java library | Test only |
|---|---|---|---|
| sbt | `"org.http4s" %% "http4s-ember-server" % "<v>"` | `"org.postgresql" % "postgresql" % "<v>"` | append `% Test` |
| Mill | `mvn"org.http4s::http4s-ember-server:<v>"` in `mvnDeps` | `mvn"org.postgresql:postgresql:<v>"` | in `object test extends ScalaTests` `mvnDeps` |
| scala-cli | `//> using dep org.http4s::http4s-ember-server:<v>` | `//> using dep org.postgresql:postgresql:<v>` | `//> using test.dep ...` |

`%%` / `::` appends `_3` or `_2.13`. Using `%` / `:` for a Scala library is
the most common build bug: it fails resolution or pulls the wrong binary.
Mill before 1.0 used `ivy"..."` and `ivyDeps`; keep whatever the file already
uses.

## 2. Find the latest version

```
cs complete-dep org.http4s:http4s-ember-server_3:      # all versions, oldest first
cs complete-dep org.http4s:http4s-ember-server_3:0.23   # narrow to a line
```

Prefer the newest non-RC/-M version whose binary suffix matches the
project's Scala version. Libraries in one family (http4s-*, circe-*, zio-*)
must share one version; set it once in a `val`/`def`.

## 3. Run part of the build

| Job | sbt | Mill | scala-cli |
|---|---|---|---|
| compile one module | `sbt --client core/compile` | `./mill core.compile` | `scala-cli compile <dir>` |
| one test suite | `sbt --client "core/testOnly *UserRepoSuite"` | `./mill core.test.testOnly core.UserRepoSuite` | `scala-cli test . --test-only '*UserRepoSuite'` |
| list modules | `sbt --client projects` | `./mill resolve _` | n/a |
| dependency tree | `sbt --client core/dependencyTree` | `./mill core.showMvnDepsTree` | `scala-cli dependency-update .` (lists updates) |

In sbt 2, `test` is incremental and cached; `testFull` reruns everything.

## 4. Cross-building

- sbt: `crossScalaVersions := Seq("3.3.7", "2.13.16")`, run `sbt --client +test`.
  Version-specific code goes in `src/main/scala-2` / `src/main/scala-3`.
- Mill: `object core extends Cross[CoreModule]("3.3.7", "2.13.16")` with
  `trait CoreModule extends CrossScalaModule`.
- scala-cli: one version per run: `scala-cli test . --scala 2.13`.
- Scala 3 can use most 2.13 libraries via
  `("org" %% "lib" % "v").cross(CrossVersion.for3Use2_13)`; macros from 2.13
  libraries do not work in Scala 3.

## 5. sbt 1 -> sbt 2

Read `sbt2.md` beside this file before touching `project/build.properties`.
Do it as its own change, after the build is green on sbt 1.

## Output

End every build change with: the files changed, the command you ran to
verify, and its result (green or the first error).
