# ZIO 2 reference (read only for ZIO projects)

## Constructors

- `ZIO.succeed(a)` (total), `ZIO.attempt(a)` (may throw -> Throwable)
- `ZIO.attemptBlocking(a)`, `ZIO.fromFuture(ec => f)` (bridge once)
- `ZIO.fail(e)` for typed errors; `.mapError`, `.catchAll`, `.orDie` only for
  truly unrecoverable defects
- `ZIO.foreachPar`, `.zipPar`, `.race`, `.timeout`

## Layers and services

```scala
import zio.*

trait UserRepo:
  def find(id: Long): IO[RepoError, Option[User]]

object UserRepo:
  val live: ZLayer[DataSource, Nothing, UserRepo] =
    ZLayer.fromFunction(UserRepoLive(_))
```

- Resources: `ZIO.acquireRelease(acquire)(release)` inside `ZIO.scoped`, or
  `ZLayer.scoped` for long-lived services.
- Wire layers at the edge with `.provide(...)`; do not call `Unsafe.unsafe`.
- State: `Ref.make(a)`, `Ref.Synchronized` for effectful updates.

## Entry point and HTTP (zio-http)

```scala
import zio.*
import zio.http.*

object Main extends ZIOAppDefault:
  val routes = Routes(Method.GET / "health" -> handler(Response.text("ok")))
  def run = Server.serve(routes).provide(Server.default)
```

## Test skeleton (zio-test; check `runZIO` against the project's zio-http version)

```scala
import zio.test.*
object HealthSpec extends ZIOSpecDefault:
  def spec = suite("health")(
    test("200")(for r <- Main.routes.runZIO(Request.get(URL.root / "health"))
                yield assertTrue(r.status == Status.Ok))
  )
```

Deps: `dev.zio %% zio`, `zio-http`; test `zio-test`, `zio-test-sbt`
(sbt also needs `testFrameworks += new TestFramework("zio.test.sbt.ZTestFramework")`).
