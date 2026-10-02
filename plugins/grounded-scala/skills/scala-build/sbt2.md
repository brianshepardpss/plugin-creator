# sbt 1.x -> 2.x checklist (read on demand)

Source: sbt 2.0 change summary, scala-sbt.org/2.x/docs (checked 2026-10-02).

1. Confirm the build is green on sbt 1 first: `sbt --client compile test`.
2. Check every plugin in `project/plugins.sbt` has an sbt 2 release (sbt 2
   plugins are published with the `_sbt2_3` suffix). Any plugin without one
   blocks the upgrade: report it and stop.
3. Set `sbt.version=2.x.y` in `project/build.properties` (look up the latest
   2.x release; do not guess).
4. The build definition (build.sbt, project/*.scala) is now Scala 3:
   - `implicit` conversions in build code may need `given`/`Conversion`.
   - Wildcard imports `_` still work; `*` is preferred.
5. Bare settings in build.sbt now apply to every subproject. Remove duplicated
   `ThisBuild /` boilerplate only if behaviour stays the same.
6. `%%%` (Scala.js/Native) can become `%%`.
7. `IntegrationTest` configuration is gone: move it to a separate subproject.
8. Keys of type `URL` became `URI`; `licenses` is `Seq[License]`.
9. Coursier is always on; remove `useCoursier`.
10. `sbt` starts the thin client by default; `sbt --client` still works.
11. `test` is incremental; use `testFull` in CI to run all tests.
12. Verify: `sbt compile test` green, then report each change made.
