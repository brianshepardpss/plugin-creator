# iOS / CocoaPods build failures

Read only when the failure is on iOS or macOS. Edit only `ios/Podfile`,
`ios/Podfile.lock` (by running pod commands) and `ios/Runner.xcodeproj` build
settings that the steps name. Never touch signing, provisioning or team ids.

1. Get the error from `flutter build ios --no-codesign 2>&1 | tail -80` (macOS
   only, ask first) or from the user's paste.
2. Match it:

| Message contains | Cause | Fix |
|---|---|---|
| `requires a higher minimum iOS deployment version` / `has a minimum deployment target of iOS X` | Podfile `platform :ios, 'N'` below what a pod needs | Set `platform :ios, 'X'` (X from the message) at the top of `ios/Podfile`; also set `IPHONEOS_DEPLOYMENT_TARGET = X` in the Runner target if it is lower |
| `CocoaPods could not find compatible versions for pod` | stale spec repo or pinned Podfile.lock | `cd ios && pod repo update && pod install` ; if still failing, `rm Podfile.lock && pod install --repo-update` (tell the user the lock was regenerated) |
| `Generated.xcconfig must exist` / `Flutter/Flutter.podspec` missing | flutter files not generated | `flutter pub get` then `cd ios && pod install` |
| `pod: command not found` / Ruby errors | CocoaPods missing or broken | `brew install cocoapods` (or `sudo gem install cocoapods`); ask before installing anything |
| `Swift Compiler Error` inside a pod after upgrade | plugin needs newer Xcode or iOS target | report plugin + required version; upgrading the plugin is a pub-upgrade job |
| `Sandbox: rsync ... deny file-write` (Xcode 15+) | user script sandboxing | set `ENABLE_USER_SCRIPT_SANDBOXING = NO` for Runner, only with the user's yes |

3. After edits: `flutter clean && flutter pub get && cd ios && pod install`, then
   rebuild. Report the before/after deployment target and the pod command run.
