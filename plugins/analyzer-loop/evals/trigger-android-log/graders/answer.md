---
type: llm
---

PASS if the reply explains that class file major version 65 means Gradle is
being run by JDK 21, that the Gradle wrapper must be raised (at least 8.4 to
run on JDK 21, and current Flutter needs Gradle 8.14 or newer), and that AGP
and Kotlin must be raised together to a compatible set, and asks for or reads
gradle-wrapper.properties and settings.gradle rather than guessing the
current versions.
FAIL if it only suggests downgrading the JDK with no version guidance, or
gives a single version bump without mentioning AGP/Kotlin compatibility.
