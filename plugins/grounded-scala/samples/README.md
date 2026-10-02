# Samples

All names, companies and data here are fake. Copy a sample into your working
directory before editing it; the skills do this for you.

| Folder | Build | What it is for |
|---|---|---|
| `ce-broken/` | scala-cli, Scala 3.3.7 LTS, cats-effect 3.7.1 | Hero workflow. Three seeded compile errors: missing `given Show[Order]`, Scala 2 procedure syntax, a `Future` returned where `IO` is promised (the compiler's suggested fix, importing the global ExecutionContext, is the wrong one). Fixed, `scala-cli run .` prints a total of 27.00. |
| `nav-demo/` | scala-cli, Scala 3.3.7, no deps | Navigation. `UserRepo.findById` has 5 true call sites (direct, via a type alias, inside an extension method, inside a given, eta-expanded) and grep decoys (a same-named `OrderRepo.findById`, a comment, a string). Answer key in `EXPECTED.md`. Compiles clean. |
| `sbt-213/` | sbt 1.11.6, Scala 2.13.16 | Migration to Scala 3: implicit vals, implicit class, implicit conversion, context bound, `: _*`, procedure syntax, symbol literal. Runs on 2.13 and prints `total=$11.00 priciest=SKU-PEN`. |

The first compile downloads dependencies; later compiles take seconds.
