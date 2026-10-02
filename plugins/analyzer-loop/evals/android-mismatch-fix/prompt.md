---
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

My Android build broke right after I upgraded Flutter to 3.47.6 and Android Studio (its JDK is 21 now). The project is analyzer loop's android_mismatch sample, and build_failure.log in it is exactly what I get. Please copy the sample here and fix the Android build files to a set of versions that work together. I approve the edits, but don't touch my Dart code, and don't run a Gradle build.
