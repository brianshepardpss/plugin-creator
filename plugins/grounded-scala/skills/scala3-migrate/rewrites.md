# Option and plugin mapping (read on demand)

| Scala 2.13 | Scala 3 |
|---|---|
| `-Xsource:3` | remove |
| `-Xfatal-warnings` | `-Werror` (both accepted in 3.3) |
| `-Ywarn-unused` / `-Wunused:imports` | `-Wunused:all` (3.3+) |
| `-Ymacro-annotations`, macro paradise plugin | remove; macro annotations need a rewrite |
| `-Ypartial-unification` | remove (always on) |
| `-language:higherKinds` | remove |
| `kind-projector` plugin (`*`, `?` lambdas) | `-Ykind-projector` (3.3: `-Ykind-projector:underscores` for `_`) |
| `better-monadic-for` plugin | remove; Scala 3 for-comprehensions behave similarly for `implicit0`, rewrite `implicit0(x)` to a `given` |
| `-Xlint` | remove; use `-Wunused:all -Wvalue-discard` |
| `-Yrangepos` | remove |

Compiler flags for the mechanical pass: `-source:3.0-migration` (accept Scala
2 syntax with warnings) plus `-rewrite` (patch sources). Remove both after.

Things `-rewrite` fixes: procedure syntax, symbol literals, `_*` in some
positions, deprecated wildcard imports. It does not convert implicits; that
is the manual idiomatic pass.
