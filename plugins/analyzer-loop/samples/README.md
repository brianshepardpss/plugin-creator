# Analyzer Loop samples

All apps, names and data here are fake ("Pebble and Pine Goods"). Skills copy a
sample into your working directory before editing, so these files stay pristine.

| Folder | What is wrong | Used by |
|---|---|---|
| `stale_app/` | pubspec.lock is on current majors (flutter_riverpod 3.4.3, go_router 18.0.2, Flutter 3.47) but the code still uses old APIs: StateNotifier, FutureProviderRef, valueOrNull, state.params / queryParams / location, withOpacity, WillPopScope, MaterialStateProperty, textScaleFactor, ButtonBar, ColorScheme.background, Color.value. `dart analyze` reports 27 issues (17 errors, 10 infos). 2 tests (cart unit test, home widget test) pass once it compiles. | fix-analyzer (hero) |
| `upgrade_app/` | The same code, still on flutter_riverpod 2.6.1 and go_router 6.5.9, where it compiles with 11 deprecation infos and tests pass. Upgrading both majors produces the 27 issues above. | pub-upgrade |
| `android_mismatch/` | Android build pinned to Gradle 7.5, AGP 7.3.0, Kotlin 1.7.10, Java/Kotlin target 1.8, minSdk 21; `build_failure.log` is the failure under JDK 21 ("Unsupported class file major version 65"). | android-build-doctor |
| `golden_drift/` | `test/goldens/price_badge.png` differs from what Linux renders by 1 pixel (8/255 on one channel), mimicking a golden generated on macOS. `ci_failure.log` and `ci_artifacts/failures/` hold the CI failure output. | golden-tests |
| `outputs/` | The bundled scripts' output on these samples, kept so evals and docs quote real numbers. | evals, README |

Setup: the Flutter SDK on PATH, then `flutter pub get` inside a copied sample
(first run downloads packages from pub.dev; later runs work offline from the pub cache).

Reproduce the outputs (from the plugin root, after `flutter pub get` in each sample):

```
python3 skills/fix-analyzer/analyze_report.py samples/stale_app
python3 skills/android-build-doctor/android_versions.py samples/android_mismatch --java 21 --log samples/android_mismatch/build_failure.log
python3 skills/golden-tests/golden_diff.py samples/golden_drift/ci_artifacts/failures
python3 skills/pub-upgrade/changelog_slice.py <upgraded copy of upgrade_app> go_router --from 6.5.9
```
