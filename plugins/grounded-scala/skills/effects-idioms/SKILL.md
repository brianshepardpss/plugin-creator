---
name: effects-idioms
description: Use whenever Scala code involves cats-effect IO, ZIO, fs2, http4s or Ox - writing it, reviewing it, or answering a question about it - including "wrap this blocking/JDBC call", "IO.fromFuture", "IO vs Future", "is this idiomatic", "what is wrong with this IO code", "add an endpoint", "use Resource", "make this async". Load it before answering, even for a quick question. Detects the effect system and enforces one consistent style (no Future/Await/global ExecutionContext mixing, scoped resources, typed errors).
---

# Effect-system style for Scala

Pick the project's effect system, then write code the way that ecosystem
does. Mixing styles is the most common agent mistake in Scala.

## 1. Detect (read the build file, do not guess)

| Dependency seen | Stack | Read |
|---|---|---|
| `cats-effect`, `fs2`, `http4s`, `doobie`, `skunk` | cats-effect 3 | `cats-effect.md` |
| `dev.zio::zio` (2.x), `zio-http` | ZIO 2 | `zio.md` |
| `com.softwaremill.ox::core` | Ox (direct style, JDK 21+) | `ox.md` |
| none of these | plain Scala / Future | follow the existing code |

If two stacks appear (for example ZIO with a `zio-interop-cats` bridge), use
the one the surrounding module already uses, and state which. Read only the
reference file for the detected stack.

## 2. Rules for every stack

1. One effect type per module. Do not introduce `Future` into IO/ZIO code or
   `IO` into ZIO code. At a boundary with a Future-returning library, convert
   once (`IO.fromFuture(IO(f))`, `ZIO.fromFuture(_ => f)`) and keep the rest
   in the effect type.
2. Never `Await.result`, `unsafeRunSync()`, `Unsafe.unsafe`,
   `unsafeToFuture()` or `unsafeRunAndForget()` inside application logic.
   Only the entry point (`IOApp`, `ZIOAppDefault`, `OxApp`) runs effects.
3. Never import `ExecutionContext.Implicits.global` in effect code, even
   when a compiler error suggests it.
4. Blocking calls (JDBC, file IO, legacy SDKs) go through the blocking
   constructor (`IO.blocking`, `ZIO.attemptBlocking`; Ox runs on virtual
   threads, so plain calls are fine).
5. Anything with a close/release (HTTP server, client, pool, file) is acquired
   as a scoped resource (`Resource`, `ZIO.scoped`/`ZLayer.scoped`, Ox
   `useInScope`/`supervised`), never with try/finally around an effect.
6. Shared mutable state uses the stack's `Ref`, never `var` or
   `AtomicReference` captured by effects.
7. Errors: model expected failures as types (`EitherT`/`IO[Either[E, A]]` or
   ADT + `raiseError` in CE; the `E` channel in ZIO; `Either` + `either:` in Ox).
   Do not throw from pure code.
8. New code uses Scala 3 syntax when the project is on Scala 3 (`given`,
   `using`, `extension`, braceless only if the file already is).

## 3. When adding a feature (endpoint, job, consumer)

1. Detect stack (step 1), read its reference file.
2. Add dependencies with the scala-build skill (correct `%%`/`::`, version
   looked up, same version line as sibling modules).
3. Write the code following the reference file's skeleton.
4. Write one test with the stack's test library (munit-cats-effect /
   zio-test / munit), run only that suite (see scala-build for the command).
5. Report: files changed, how resources are acquired/released, test result.

## 4. When reviewing

List each violation of section 2 as `file:line - rule n - fix`, most severe
first (unsafe runs and Await, then Future mixing, then leaks, then style).
