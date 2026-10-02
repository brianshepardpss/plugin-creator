---
description: Fix Scala compile errors in this project (or `sample` for the bundled broken cats-effect project) with a warm compile-fix loop.
argument-hint: "[sample | path]"
---

Use the grounded-scala fix-compile skill on: $ARGUMENTS

If the argument is empty, use the current project. If it is `sample`, copy the
bundled `samples/ce-broken` project into the working directory first and fix
the copy. Finish with the skill's report template.
