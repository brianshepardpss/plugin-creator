---
name: golden-tests
description: Use when Flutter golden (screenshot) tests fail, are flaky across machines, or need to be added, or when the user says "golden test fails on CI but passes on my Mac", "Pixel test failed, 0.02%, 1px diff detected", "update the goldens", "matchesGoldenFile", "add a golden test for this widget", "golden_toolkit is discontinued" or "set up alchemist". Measures the diff with a bundled script, separates rendering drift from real regressions, and fixes the setup instead of blindly regenerating images.
argument-hint: "[failures dir | sample]"
---

# Golden tests that mean something

Paths: `golden_diff.py` and `recipes.md` are in this skill's base directory.
The plugin root is two directories above it; the demo is
`<plugin root>/samples/golden_drift` (a 1-pixel drift, with the CI failure
images already in `ci_artifacts/failures/` and the log in `ci_failure.log`).

## Hard rule

Never run `flutter test --update-goldens` (or set `autoUpdateGoldenFiles`,
or Alchemist `forceUpdateGoldenFiles`) unless the user explicitly asks in
this conversation to regenerate goldens. Regenerating hides regressions. When
asked, regenerate only the named tests, on the platform that CI compares
against, and list every PNG that changed.

## 1. Measure the failure

1. Argument `sample` (or the user points at the golden_drift sample): run
   `cp -r "<plugin root>/samples/golden_drift" ./golden_drift` and work in the
   copy; its failures are in `./golden_drift/ci_artifacts/failures` and the
   log is `./golden_drift/ci_failure.log`. Never edit files inside the plugin
   directory.
2. Otherwise find the failure images: `test/failures/` next to the failing
   test (`<name>_masterImage.png`, `_testImage.png`, `_isolatedDiff.png`,
   `_maskedDiff.png`), or the CI artifact the user downloaded. If there are
   none, run only the failing test: `flutter test <file> --reporter expanded`.
3. Run:
   ```
   python3 "<skill dir>/golden_diff.py" <failures dir> [name]
   ```
   Quote its numbers (differing pixels, percent, max channel delta, bbox,
   minimum tolerance). Do not estimate them yourself.
4. Look at `_isolatedDiff.png` / `_maskedDiff.png` with the Read tool when the
   verdict is "likely real change" or a size mismatch.

## 2. Diagnose

- **Rendering drift** (script verdict, typically a few anti-aliased pixels,
  fonts or shadows): the golden was made on one OS and compared on another
  (macOS laptop vs Linux CI is the classic case), or a Flutter/Skia/Impeller
  upgrade changed rasterisation. This is the setup's fault, not the widget's.
- **Size mismatch**: surface size, device pixel ratio or text scale differs;
  check `tester.view.physicalSize`, `setSurfaceSize`, `devicePixelRatio`.
- **Likely real change**: a theme, padding or widget change. Show the bbox
  and the diff images and ask whether the change is intended.

## 3. Fix the setup (pick one and explain why)

Read `recipes.md` for the code. In order of preference:

1. **One source of truth platform**: generate and compare goldens only on
   Linux (CI or the documented Docker command), tag golden tests `golden`,
   and skip them locally on other OSes. Best for teams.
2. **Alchemist** (`alchemist` on pub.dev, maintained): CI goldens render text
   as blocks (Ahem) and shadows as solid colours, so they match across OSes;
   platform goldens stay human-readable and are not compared on CI. Prefer it
   for new suites. `golden_toolkit` is discontinued on pub.dev; migrate away
   rather than adding it.
3. **Tolerant comparator**: a `LocalFileComparator` subclass that accepts a
   small `diffPercent`. Use the script's minimum tolerance as the floor and
   round up modestly (never above 0.01 = 1% without the user's explicit OK),
   because a big tolerance lets real regressions through.

Also check: fonts loaded for readable goldens (`loadAppFonts` equivalent in
recipes.md), animations settled (`pumpAndSettle` or a fixed `pump(duration)`),
network images replaced with fakes, and `debugDisableShadows` consistent.

## 4. Adding a new golden test

Use the template in `recipes.md`: fixed surface size, `RepaintBoundary`,
deterministic data, theme passed explicitly, file under `test/goldens/`.
Generate the PNG only for the new test (`flutter test <file> --update-goldens`
is acceptable here because the image does not exist yet; say so).

## Report in exactly this shape

```
Golden: <name>  (<test file>)
Diff: <px> px of <total> = <pct>% (flutter: <flutter pct>), max channel delta <d>, bbox <bbox>   [golden_diff.py]
Verdict: <rendering drift | size mismatch | likely real change> because <reason>
Fix: <option chosen> -> <files changed or to change>
Goldens regenerated: <none | list, only if the user asked>
```
