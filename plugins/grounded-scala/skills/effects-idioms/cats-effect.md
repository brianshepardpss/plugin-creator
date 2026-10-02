# cats-effect 3 reference (read only for CE projects)

Libraries usually seen together: fs2 (streams), http4s 0.23 (HTTP, Ember
server/client), circe (JSON), doobie or skunk (DB), munit-cats-effect (tests).

## Constructors

- `IO(a)` / `IO.delay(a)`: suspend a side effect
- `IO.blocking(a)`: blocking IO on the blocking pool
- `IO.interruptible(a)`: blocking and cancelable (Thread.interrupt)
- `IO.fromFuture(IO(future))`: one-time bridge from a Future API
- `IO.raiseError(e)`, `.handleErrorWith`, `.attempt`
- `IO.sleep`, `IO.race`, `parTupled`, `parTraverse` (from cats.syntax.all.*)

## Skeleton: http4s Ember server with a health route

```scala
import cats.effect.*
import com.comcast.ip4s.*
import org.http4s.*
import org.http4s.dsl.io.*
import org.http4s.ember.server.EmberServerBuilder

object Server extends IOApp.Simple:
  val routes: HttpRoutes[IO] = HttpRoutes.of[IO] {
    case GET -> Root / "health" => Ok("ok")
  }

  def run: IO[Unit] =
    EmberServerBuilder.default[IO]
      .withHost(ipv4"0.0.0.0").withPort(port"8080")
      .withHttpApp(routes.orNotFound)
      .build          // Resource[IO, Server]
      .useForever
```

Deps (look up versions): `org.http4s %% http4s-ember-server`, `http4s-dsl`;
test `org.typelevel %% munit-cats-effect`.

## Test skeleton

```scala
import cats.effect.IO
import munit.CatsEffectSuite
import org.http4s.*
import org.http4s.implicits.*

class HealthSuite extends CatsEffectSuite:
  test("GET /health is 200") {
    Server.routes.orNotFound.run(Request[IO](Method.GET, uri"/health"))
      .map(r => assertEquals(r.status, Status.Ok))
  }
```

## Resources and state

- `Resource.make(acquire)(release)`, `Resource.fromAutoCloseable(IO(...))`
- Compose resources in a for-comprehension; call `.use` once at the edge.
- `Ref.of[IO, A](a)`, `Deferred[IO, A]`, `Queue.bounded[IO, A](n)`.
- Tagless final (`F[_]: Async`) only if the codebase already uses it.
