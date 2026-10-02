# Ox reference (direct style; read only for Ox projects)

Ox (SoftwareMill) uses JDK 21+ virtual threads; code is plain Scala with
structured concurrency, no `IO` type. For broader direct-style guidance
(tapir, sttp) see VirtusLab/scala-skill, which complements this plugin.

- Concurrency: `par(a, b)`, `race(a, b)`, `timeout(d)(op)`
- Scopes: `supervised { fork { ... } }`; forks cannot outlive the scope
- Resources: `useInScope(acquire)(release)` inside `supervised`
- Errors: `either { val a = op1.ok(); ... }` with `Either` values; exceptions
  only for defects
- Retries and rate limits: Ox has `retry` and schedules; check the API of
  the Ox version in the build before writing them (it changed before 1.0)
- Entry point: `object Main extends OxApp` with `def run(args: Vector[String])(using Ox): ExitCode`
- Blocking calls are fine (virtual threads); do not wrap them in Future.
