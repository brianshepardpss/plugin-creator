---
type: regex
target: {source: file, path: android_mismatch/android/settings.gradle}
pattern: 'com\.android\.application"\s+version\s+"(9\.1\.0|8\.11\.1)".*org\.jetbrains\.kotlin\.android"\s+version\s+"(2\.4\.0|2\.2\.20)"'
flags: s
---
