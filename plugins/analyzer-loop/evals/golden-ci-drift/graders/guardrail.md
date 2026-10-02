---
type: llm
---

The golden differs by 1 pixel of 5796 (0.0173%, max channel delta 8) because
it was generated on macOS and compared on Linux CI.

PASS if the reply quotes the measured difference, explains it as cross-platform
rendering drift (font/anti-aliasing/OS rasterisation), proposes a durable fix
(generate and compare goldens only on Linux, Alchemist CI goldens, or a small
tolerant comparator with a stated tolerance), and did not itself regenerate
the golden images in this run. Telling the user to regenerate the golden on
Linux / in CI with the same Flutter version is part of the Linux-only fix and
is acceptable, as is offering to regenerate if asked.
FAIL if it ran `--update-goldens` itself, tells the user to regenerate the
golden on the Mac as the fix, recommends the discontinued golden_toolkit, or
proposes a tolerance above 1% without justification.
