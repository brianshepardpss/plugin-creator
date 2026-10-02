---
type: llm
focus: last_message
---

PASS if the answer says the project was compiled on Scala 3 (with scala-cli,
since sbt is unavailable) and it succeeded, and it lists the changes by
stage: compiler rewrites (procedure syntax, symbol literal), implicit vals
-> given, implicit parameters -> using, implicit class -> extension, the
implicit conversion handled (Conversion given or made explicit), and `: _*`
-> `*`. It must state that scalaVersion in build.sbt is now 3.x.
FAIL if it only bumps the version, claims success without compiling, or
removes functionality (deletes the conversion's call site behaviour without
saying so, comments code out).
