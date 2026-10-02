---
name: android-build-doctor
description: Use when a Flutter app's Android (or iOS) build fails after a Flutter, Android Studio or JDK upgrade, or when the user pastes Gradle errors such as "Unsupported class file major version 65", "Minimum supported Gradle version is", "Your project's Android Gradle Plugin version is lower than Flutter's minimum supported version", "incompatible version of Kotlin", "Namespace not specified", or says "flutter run fails on Android", "fix my gradle versions", "AGP / Kotlin / Gradle mismatch", "pod install fails". Reads the build files, checks Gradle, AGP, Kotlin and JDK against each other and Flutter's support policy with a bundled script, and edits only the Android build files to a compatible set.
argument-hint: "[project dir | sample] [build log]"
---

# Android build doctor (Gradle, AGP, Kotlin, JDK)

Paths: `android_versions.py` and `ios.md` are in this skill's base directory.
The plugin root is two directories above it; the demo is
`<plugin root>/samples/android_mismatch` (with `build_failure.log`).

## 1. Collect facts (no edits yet)

1. Argument `sample`: `python3 "<plugin root>/samples/copy_sample.py" android_mismatch`
   and work in `./android_mismatch`. Never edit files inside the plugin directory.
2. Get the failing log: the user's paste, a log file, or run
   `flutter build apk --debug 2>&1 | tail -80` once if they agree (a cold
   Gradle build can take 5+ minutes; ask first). Save a pasted log to
   `.dart_tool/analyzer-loop-build.log` so the script can read it.
3. Find the JDK Flutter uses: `flutter doctor -v` (the "Java version" line
   under Android toolchain). If unavailable, ask the user or take it from the
   log (class file 61 = JDK 17, 65 = 21, 68 = 24, 69 = 25).
4. Run the checker:
   ```
   python3 "<skill dir>/android_versions.py" <project> --java <N> --log <log file>
   ```
   It reads the user's Flutter SDK for the current floors when `flutter` is on
   PATH, otherwise its bundled Flutter 3.47.6 table. If `flutter analyze
   --suggestions` is available, run it too; it reports the same pairwise checks
   from Flutter's own tooling.

## 2. Decide the target set

Use only the two sets the script prints; both are checked against the same
tables. Never pick versions from memory.

- **Recommended (Flutter template)**: what `flutter create` generates today.
  Moving from AGP 8 to AGP 9 also needs the template's gradle.properties
  flags and build-script shape, so diff against a fresh template (step 3).
- **Stopgap**: clears every Flutter error floor without the AGP 9 migration,
  but still prints "support will soon be dropped" warnings. Offer it when a
  plugin dependency is known to break on AGP 9, or the user wants the
  smallest change today.

Explain the choice in two sentences and wait for the user's yes before editing.

## 3. Edit only Android build files

Allowed files: `android/gradle/wrapper/gradle-wrapper.properties`,
`android/settings.gradle(.kts)`, `android/build.gradle(.kts)`,
`android/app/build.gradle(.kts)`, `android/gradle.properties`. Never touch
`lib/`, `pubspec.yaml`, `ios/` or signing config in this step.

1. Generate a reference: `flutter create --no-pub --platforms=android --project-name ref_app <tmp dir>/ref_app`
   (needs the Flutter SDK, no network) and diff its `android/` against the
   user's. Copy structure, not app ids or signing.
2. `gradle-wrapper.properties`: set `distributionUrl` to the target Gradle
   (`...gradle-<ver>-all.zip`, keep `\:` escaping).
3. `settings.gradle(.kts)` plugins block: `com.android.application` to the
   target AGP, `org.jetbrains.kotlin.android` to the target Kotlin. Older
   projects with `buildscript { classpath ... }` / `ext.kotlin_version` in
   `android/build.gradle`: change those lines, then recommend (do not force)
   migrating to the plugins block shown in the reference.
4. `app/build.gradle(.kts)`: `compileOptions` source/target and Kotlin
   `jvmTarget` both to 17 (they must match); `minSdk = flutter.minSdkVersion`
   unless the app needs a higher number; keep `namespace`.
5. For AGP 9: copy the reference's `gradle.properties` flags
   (`android.newDsl`, `android.builtInKotlin`) and its `kotlin { compilerOptions }` block.
6. Re-run `android_versions.py` with the same arguments. Every line must be
   OK (WARN is acceptable only for the stopgap set). Show the before/after
   tables.

## 4. Verify

If the user agrees to a build, run `flutter build apk --debug`. If not, say
the files are consistent per the script and what to run. Classify any new
failure with the log signatures again; a dependency (plugin) that needs a
newer AGP or compileSdk is a pub-upgrade job, not a build-file edit.

## iOS

For CocoaPods / Xcode failures (`pod install` errors, "requires a higher
minimum iOS deployment version", "CocoaPods could not find compatible
versions"), read `ios.md` in this skill directory and follow it.

## Report in exactly this shape

```
Android build doctor: <project>
JDK used by Flutter: <N> (<where it came from>)
| item | before | after | file:line |
|---|---|---|---|
| Gradle | ... |
| AGP | ... |
| Kotlin | ... |
| Java/Kotlin target | ... |
| minSdk | ... |
Checks after: <n> OK, <n> WARN, <n> FAIL  (android_versions.py)
Root cause: <one sentence tied to the log line>
Next: <build command to run, or what is left for the user>
```
