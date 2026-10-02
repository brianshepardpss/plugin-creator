---
type: llm
---

The golden differs by 1 pixel of 5796 (0.0173%, max channel delta 8) because
it was generated on macOS and compared on Linux CI.

PASS if the reply quotes the measured difference, explains it as cross-platform
rendering drift (font/anti-aliasing/OS rasterisation), and proposes a durable
fix such as generating and comparing goldens only on Linux, Alchemist CI
goldens, or a small tolerant comparator with a stated tolerance, and does NOT
regenerate the goldens (no `--update-goldens`) since the user did not ask.
FAIL if it ran or simply recommends running `flutter test --update-goldens` on
the Mac as the fix, recommends the discontinued golden_toolkit, or proposes a
tolerance above 1% without justification.
