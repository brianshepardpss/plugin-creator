---
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

Our cats-effect service has this, and a reviewer said it's wrong but didn't say why. jdbc.find is a plain blocking JDBC call. What should it be?

```scala
import scala.concurrent.Future
import scala.concurrent.ExecutionContext.Implicits.global

def find(id: Long): IO[Option[User]] =
  IO.fromFuture(IO(Future(jdbc.find(id))))
```
