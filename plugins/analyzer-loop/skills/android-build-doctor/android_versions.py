#!/usr/bin/env python3
"""Read a Flutter app's Android build versions and check them against each other
and against Flutter's support policy. Standard library only.

Usage:
  python3 android_versions.py <project-or-android-dir> [--java 21] [--log build.log]
                              [--flutter-root PATH] [--json]

What it reads (first match wins):
  Gradle  android/gradle/wrapper/gradle-wrapper.properties  distributionUrl=...gradle-X-all.zip
  AGP     android/settings.gradle(.kts) plugins { id "com.android.application" version "X" }
          or android/build.gradle(.kts) classpath 'com.android.tools.build:gradle:X'
  Kotlin  android/settings.gradle(.kts) id "org.jetbrains.kotlin.android" version "X"
          or android/build.gradle(.kts) ext.kotlin_version = 'X'
  JDK     --java, else org.gradle.java.home in gradle.properties is reported, else `java -version`
  minSdk  android/app/build.gradle(.kts) minSdk / minSdkVersion

Rules (all from flutter_tools 3.47.6, packages/flutter_tools/lib/src/android/gradle_utils.dart
and packages/flutter_tools/gradle/src/main/kotlin/DependencyVersionChecker.kt, read 2026-10-02):
  * Flutter floor: a version below "error" fails the build; below "warn" prints
    "support ... will soon be dropped". If --flutter-root (or `flutter` on PATH) is found,
    the error/warn/template values are re-read from that SDK so they match the user's Flutter.
  * AGP -> minimum Gradle            (GRADLE_FOR_AGP)
  * Kotlin Gradle plugin -> Gradle    (KGP_GRADLE), Kotlin -> AGP (KGP_AGP)
  * JDK -> minimum Gradle             (JAVA_GRADLE: JDK N needs Gradle >= min to run)
  * AGP -> minimum JDK                (AGP 8.x/9.x need JDK 17, AGP 7.x needs JDK 11)
Version comparison is numeric per dot-separated part; missing parts count as 0.
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

TABLE_SOURCE = "flutter_tools 3.47.6 (bundled table, read 2026-10-02)"

POLICY = {  # DependencyVersionChecker.kt
    "gradle": {"error": "8.14.0", "warn": "9.1.0"},
    "agp": {"error": "8.11.1", "warn": "9.0.1"},
    "kotlin": {"error": "2.2.20", "warn": "2.3.20"},
    "java": {"error": "17", "warn": "17"},
    "minsdk": {"error": "23", "warn": "24"},  # non inclusive: minSdk must be >= value
}
TEMPLATE = {"gradle": "9.3.1", "agp": "9.1.0", "kotlin": "2.4.0", "java": "17"}  # gradle_utils.dart

# (agp_min, agp_max_inclusive, min_gradle)  getGradleVersionFor()
GRADLE_FOR_AGP = [
    ("7.0.0", "7.5", "7.5"), ("8.0.0", "8.1.99", "8.0"), ("8.2.0", "8.2.99", "8.2"),
    ("8.3.0", "8.3.99", "8.4"), ("8.4.0", "8.4.99", "8.6"), ("8.5.0", "8.6.99", "8.7"),
    ("8.7.0", "8.7.99", "8.9"), ("8.8.0", "8.8.99", "8.10.2"), ("8.9.0", "8.9.99", "8.11.1"),
    ("8.10.0", "8.10.99", "8.11.1"), ("8.11.0", "8.11.99", "8.14"), ("8.12.0", "8.12.99", "8.14"),
    ("8.13.0", "8.13.99", "8.14"), ("9.0", "9.0.99", "9.1.0"), ("9.1.0", "9.1.99", "9.3.1"),
    ("9.2", "9.2.99", "9.3.1"),
]
# (kgp_min, kgp_max, max_inclusive, gradle_min, gradle_max, gradle_max_inclusive)  validateGradleAndKGP()
KGP_GRADLE = [
    ("2.4.0", "2.4.29", True, "8.5", "9.5.99", False),
    ("2.3.0", "2.3.29", True, "7.6.3", "9.5.99", False),
    ("2.2.20", "2.3.0", True, "7.6.3", "8.14.99", False),
    ("2.2.0", "2.2.10", True, "7.6.3", "8.14.99", False),
    ("2.1.20", "2.1.21", True, "7.6.3", "8.12.99", False),
    ("2.1.0", "2.1.10", True, "7.6.3", "8.11", False),
    ("2.0.20", "2.1", False, "6.8.3", "8.9", False),
    ("2.0", "2.0.20", False, "6.8.3", "8.6", False),
    ("1.9.20", "2.0", False, "6.8.3", "8.1.1", True),
    ("1.8.20", "1.9.20", False, "6.8.3", "7.6.0", True),
    ("1.8.0", "1.8.20", False, "6.8.3", "7.3.3", True),
    ("1.7.20", "1.8.0", False, "6.7.1", "7.1.1", True),
    ("1.7.0", "1.7.20", False, "6.7.1", "7.0.2", True),
    ("1.6.20", "1.7.0", False, "6.1.1", "7.0.2", True),
]
# (kgp_min, kgp_max, max_inclusive, agp_min, agp_max, agp_max_inclusive)  validateAgpAndKgp()
KGP_AGP = [
    ("2.4.0", "2.4.29", True, "8.2.2", "9.2.99", False),
    ("2.3.10", "2.3.29", True, "8.2.2", "9.2.99", False),
    ("2.3.0", "2.3.10", False, "8.2.2", "8.14", False),
    ("2.2.20", "2.3.0", False, "7.3.1", "8.12", False),
    ("2.2.0", "2.2.19", True, "7.3.1", "8.11", False),
    ("2.1.0", "2.1.21", True, "7.3.1", "8.7.2", True),
    ("2.0.20", "2.1.0", False, "7.1.3", "8.6", False),
    ("2.0.0", "2.0.20", False, "7.1.3", "8.3.1", True),
    ("1.9.20", "2.0.0", False, "4.2.2", "8.1.0", True),
    ("1.9.0", "1.9.20", False, "4.2.2", "7.4.0", True),
    ("1.8.20", "1.9", False, "4.1.3", "7.4.0", True),
    ("1.8.0", "1.8.20", False, "4.1.3", "7.2.1", True),
    ("1.7.20", "1.8.0", False, "3.6.4", "7.0.4", True),
    ("1.6.20", "1.7.20", False, "3.4.3", "7.0.2", True),
]
# (java_major, min_gradle)  _javaGradleCompatList: running Gradle on JDK N needs Gradle >= min
JAVA_GRADLE = [
    ("25", "9.1.0"), ("24", "8.14"), ("23", "8.10"), ("22", "8.7"), ("21", "8.4"),
    ("20", "8.1"), ("19", "7.6"), ("18", "7.5"), ("17", "7.3"), ("16", "7.0"), ("11", "5.0"),
]
GRADLE_MAX_FOR_JAVA_PRE17 = "8.14.100"
# (agp_min, agp_max_inclusive, min_java)  _javaAgpCompatList
JAVA_AGP = [("8.0", "100", "17"), ("7.0", "7.4.99", "11"), ("4.2", "4.2.99", "1.8")]
# A fallback set that clears every Flutter 3.47.6 error floor without the AGP 9 migration.
# It still triggers the "will soon be dropped" warnings, so it is a stopgap.
MIN_JUMP = {"gradle": "8.14.3", "agp": "8.11.1", "kotlin": "2.2.20", "java": "17"}

# Log signatures: (regex, explanation). Class file majors: 61=17, 65=21, 68=24, 69=25.
LOG_SIGNATURES = [
    (r"Unsupported class file major version\s+(\d+)",
     "The JDK running Gradle (class file {0} = JDK {jdk}) is newer than this Gradle supports."),
    (r"Minimum supported Gradle version is ([\d.]+)",
     "AGP demands Gradle >= {0}; bump distributionUrl in gradle-wrapper.properties."),
    (r"Your project's (\w[\w ]*?) version \(([\d.]+)\) is lower than Flutter's minimum supported version of ([\d.]+)",
     "Flutter's floor: {0} {1} < required {2}."),
    (r"Flutter support for your project's (\w[\w ]*?) version \(([\d.]+)\) will soon be dropped",
     "Flutter warning: {0} {1} is below the warn floor."),
    (r"compiled with an incompatible version of Kotlin\. The binary version of its metadata is ([\d.]+), expected version is ([\d.]+)",
     "A dependency was built with Kotlin {0} but the project's Kotlin Gradle plugin is {1}: raise KGP."),
    (r"requires Android Gradle plugin ([\d.]+) or higher",
     "A dependency needs AGP >= {0}."),
    (r"Dependency '([^']+)' requires (?:libraries and applications that depend on it to compile against version|compileSdk) (\d+)",
     "Dependency {0} needs compileSdk {1}."),
    (r"Namespace not specified",
     "AGP 8+ needs `namespace` in the module's android block (often a stale plugin; upgrade the plugin)."),
    (r"Inconsistent JVM-target compatibility detected for tasks '(\w+)' \((\d+)\) and '(\w+)' \((\d+)\)",
     "Java and Kotlin targets differ ({1} vs {3}); set both compileOptions and jvmTarget to the same value."),
]
JDK_FOR_CLASS = {"52": "8", "55": "11", "61": "17", "65": "21", "66": "22", "67": "23", "68": "24", "69": "25", "70": "26"}


def v(s):
    return tuple(int(p) for p in re.findall(r"\d+", s or "")[:4]) or (0,)


def cmp(a, b):
    a, b = list(v(a)), list(v(b))
    n = max(len(a), len(b))
    a += [0] * (n - len(a))
    b += [0] * (n - len(b))
    return (a > b) - (a < b)


def within(x, lo, hi, hi_incl=True):
    return cmp(x, lo) >= 0 and (cmp(x, hi) <= 0 if hi_incl else cmp(x, hi) < 0)


def java_major(s):
    s = s.strip().strip('"')
    if s.startswith("1."):
        return s.split(".")[1] if s != "1.8" else "1.8"
    m = re.match(r"(\d+)", s)
    return m.group(1) if m else s


def find(text, pats):
    for p in pats:
        m = re.search(p, text, re.M)
        if m:
            return m
    return None


def line_of(text, m):
    return text[: m.start()].count("\n") + 1


def read_versions(android, java_arg):
    out = {}

    def rd(rel):
        p = android / rel
        return (p.read_text(errors="replace"), rel) if p.exists() else ("", rel)

    t, rel = rd("gradle/wrapper/gradle-wrapper.properties")
    m = find(t, [r"gradle-([\d.]+)-(?:all|bin)\.zip"])
    if m:
        out["gradle"] = (m.group(1), f"{rel}:{line_of(t, m)}")

    for rel in ("settings.gradle", "settings.gradle.kts", "build.gradle", "build.gradle.kts"):
        t, _ = rd(rel)
        if not t:
            continue
        if "agp" not in out:
            m = find(t, [r"""id\s*\(?\s*["']com\.android\.application["']\s*\)?\s*version\s*["']([\d.]+)""",
                         r"""com\.android\.tools\.build:gradle:([\d.]+)"""])
            if m:
                out["agp"] = (m.group(1), f"{rel}:{line_of(t, m)}")
        if "kotlin" not in out:
            m = find(t, [r"""id\s*\(?\s*["']org\.jetbrains\.kotlin\.android["']\s*\)?\s*version\s*["']([\d.]+)""",
                         r"""kotlin_version\s*=\s*["']([\d.]+)""",
                         r"""kotlin-gradle-plugin:([\d.]+)"""])
            if m:
                out["kotlin"] = (m.group(1), f"{rel}:{line_of(t, m)}")

    for rel in ("app/build.gradle", "app/build.gradle.kts"):
        t, _ = rd(rel)
        if not t:
            continue
        m = find(t, [r"minSdk(?:Version)?\s*=?\s*(\d+|flutter\.minSdkVersion)"])
        if m and "minsdk" not in out:
            out["minsdk"] = (m.group(1), f"{rel}:{line_of(t, m)}")
        m = find(t, [r"JavaVersion\.VERSION_(\w+)"])
        if m and "java_target" not in out:
            out["java_target"] = (m.group(1).replace("_", "."), f"{rel}:{line_of(t, m)}")
        m = find(t, [r"""jvmTarget\s*=\s*["']?([\w.]+)""", r"JvmTarget\.JVM_(\w+)"])
        if m and "kotlin_target" not in out:
            out["kotlin_target"] = (m.group(1).replace("_", "."), f"{rel}:{line_of(t, m)}")

    if java_arg:
        out["java"] = (java_major(java_arg), "--java")
    else:
        t, rel = rd("gradle.properties")
        m = find(t, [r"org\.gradle\.java\.home\s*=\s*(.+)"])
        if m:
            out["java_home"] = (m.group(1).strip(), f"{rel}:{line_of(t, m)}")
        j = shutil.which("java")
        if j:
            try:
                r = subprocess.run([j, "-version"], capture_output=True, text=True, timeout=20)
                m = re.search(r'version "([^"]+)"', r.stderr + r.stdout)
                if m:
                    out["java"] = (java_major(m.group(1)), "java -version on PATH (Flutter may use another JDK; check `flutter doctor -v`)")
            except Exception:
                pass
    return out


def load_policy(flutter_root):
    """Re-read floors and template versions from the user's Flutter SDK when available."""
    src = TABLE_SOURCE
    root = flutter_root
    if not root:
        f = shutil.which("flutter")
        if f:
            root = str(Path(os.path.realpath(f)).parent.parent)
    if not root:
        return src
    dvc = Path(root) / "packages/flutter_tools/gradle/src/main/kotlin/DependencyVersionChecker.kt"
    gu = Path(root) / "packages/flutter_tools/lib/src/android/gradle_utils.dart"
    try:
        t = dvc.read_text()
        for key, name in (("gradle", "Gradle"), ("agp", "AGP"), ("kotlin", "KGP")):
            for lvl in ("warn", "error"):
                m = re.search(rf"val {lvl}{name}Version: \w+ = \w+\((\d+), (\d+), (\d+)\)", t)
                if m:
                    POLICY[key][lvl] = ".".join(m.groups())
        for lvl in ("warn", "error"):
            m = re.search(rf"val {lvl}JavaVersion: JavaVersion = JavaVersion\.VERSION_(\d+)", t)
            if m:
                POLICY["java"][lvl] = m.group(1)
            m = re.search(rf"val {lvl}MinSdkVersion: Int = (\d+)", t)
            if m:
                POLICY["minsdk"][lvl] = m.group(1)
        g = gu.read_text()
        for key, const in (("gradle", "templateDefaultGradleVersion"), ("agp", "templateAndroidGradlePluginVersion"),
                           ("kotlin", "templateKotlinGradlePluginVersion")):
            m = re.search(rf"const {const} = '([\d.]+)'", g)
            if m:
                TEMPLATE[key] = m.group(1)
        ver = (Path(root) / "version").read_text().strip() if (Path(root) / "version").exists() else ""
        if not ver:
            vj = Path(root) / "bin/cache/flutter.version.json"
            if vj.exists():
                ver = json.loads(vj.read_text()).get("frameworkVersion", "")
        src = f"flutter_tools {ver or '(unknown version)'} at {root} (live)"
    except Exception:
        pass
    return src


def min_gradle_for_agp(agp):
    for lo, hi, g in GRADLE_FOR_AGP:
        if within(agp, lo, hi):
            return g
    if cmp(agp, GRADLE_FOR_AGP[-1][0]) > 0:
        return GRADLE_FOR_AGP[-1][2]
    return None


def checks(found):
    res = []
    g = found.get("gradle", (None,))[0]
    a = found.get("agp", (None,))[0]
    k = found.get("kotlin", (None,))[0]
    j = found.get("java", (None,))[0]

    for key, label in (("gradle", "Gradle"), ("agp", "AGP"), ("kotlin", "Kotlin"), ("java", "JDK")):
        x = found.get(key, (None,))[0]
        if not x or x == "1.8" and key != "java":
            continue
        xv = "8" if x == "1.8" else x
        if cmp(xv, POLICY[key]["error"]) < 0:
            res.append(("FAIL", f"{label} {x} is below Flutter's minimum {POLICY[key]['error']} (build error)"))
        elif cmp(xv, POLICY[key]["warn"]) < 0:
            res.append(("WARN", f"{label} {x} is below Flutter's warn floor {POLICY[key]['warn']} (support ending soon)"))
        else:
            res.append(("OK", f"{label} {x} meets Flutter's floor {POLICY[key]['warn']}"))

    ms = found.get("minsdk", (None,))[0]
    if ms and ms.isdigit():
        if int(ms) < int(POLICY["minsdk"]["error"]):
            res.append(("FAIL", f"minSdk {ms} is below Flutter's minimum {POLICY['minsdk']['error']}"))
        elif int(ms) < int(POLICY["minsdk"]["warn"]):
            res.append(("WARN", f"minSdk {ms} is below Flutter's warn floor {POLICY['minsdk']['warn']}"))

    if a and g:
        need = min_gradle_for_agp(a)
        if need:
            ok = cmp(g, need) >= 0
            res.append(("OK" if ok else "FAIL", f"AGP {a} needs Gradle >= {need}; found {g}"))
    if k and g:
        for lo, hi, hin, glo, ghi, ghin in KGP_GRADLE:
            if within(k, lo, hi, hin):
                ok = within(g, glo, ghi, ghin)
                res.append(("OK" if ok else "FAIL", f"Kotlin {k} supports Gradle {glo} to {ghi}{'' if ghin else ' (exclusive)'}; found {g}"))
                break
    if k and a:
        for lo, hi, hin, alo, ahi, ahin in KGP_AGP:
            if within(k, lo, hi, hin):
                ok = within(a, alo, ahi, ahin)
                res.append(("OK" if ok else "FAIL", f"Kotlin {k} supports AGP {alo} to {ahi}{'' if ahin else ' (exclusive)'}; found {a}"))
                break
    if j and g:
        jj = "8" if j == "1.8" else j
        for jv, gmin in JAVA_GRADLE:
            if cmp(jj, jv) >= 0:
                ok = cmp(g, gmin) >= 0
                res.append(("OK" if ok else "FAIL", f"JDK {j} needs Gradle >= {gmin} to run; found {g}"))
                if cmp(jj, "17") < 0 and cmp(g, GRADLE_MAX_FOR_JAVA_PRE17) >= 0:
                    res.append(("FAIL", f"Gradle {g} needs JDK 17+ to run; found JDK {j}"))
                break
    if j and a:
        jj = "8" if j == "1.8" else j
        for lo, hi, jmin in JAVA_AGP:
            if within(a, lo, hi):
                jm = "8" if jmin == "1.8" else jmin
                res.append(("OK" if cmp(jj, jm) >= 0 else "FAIL", f"AGP {a} needs JDK >= {jmin}; found {j}"))
                break
    jt = found.get("java_target", (None,))[0]
    kt = found.get("kotlin_target", (None,))[0]
    if jt and kt and java_major(jt) != java_major(kt):
        res.append(("FAIL", f"Java target {jt} and Kotlin jvmTarget {kt} differ"))
    if jt and java_major(jt) in ("1.8", "11") and a and cmp(a, "8.0") >= 0:
        res.append(("WARN", f"Java/Kotlin target {jt} is older than the Flutter template's 17"))
    return res


def set_check(s, java):
    """Return list of failures for a proposed set using the same tables."""
    found = {k: (s[k], "proposed") for k in ("gradle", "agp", "kotlin")}
    found["java"] = (java, "proposed")
    return [m for st, m in checks(found) if st == "FAIL"]


def scan_log(path):
    hits = []
    t = Path(path).read_text(errors="replace")
    for pat, msg in LOG_SIGNATURES:
        for m in re.finditer(pat, t):
            g = m.groups()
            extra = {"jdk": JDK_FOR_CLASS.get(g[0], "?")} if "jdk" in msg else {}
            hits.append((line_of(t, m), msg.format(*g, **extra)))
            break
    return sorted(hits)


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    def opt(name):
        if name in args:
            i = args.index(name)
            val = args[i + 1]
            del args[i:i + 2]
            return val
        return None

    java_arg, log, froot = opt("--java"), opt("--log"), opt("--flutter-root")
    as_json = "--json" in args
    args = [a for a in args if a != "--json"]
    base = Path(args[0])
    android = base / "android" if (base / "android").is_dir() else base
    if not (android / "settings.gradle").exists() and not (android / "settings.gradle.kts").exists() \
            and not (android / "build.gradle").exists() and not (android / "build.gradle.kts").exists():
        print(f"No Android Gradle files under {android}", file=sys.stderr)
        return 2

    src = load_policy(froot)
    found = read_versions(android, java_arg)
    results = checks(found)
    hits = scan_log(log) if log else []
    jprop = found.get("java", ("17",))[0]
    jprop = jprop if cmp("8" if jprop == "1.8" else jprop, "17") >= 0 else "17"
    tmpl_fail = set_check(TEMPLATE, jprop)
    min_fail = set_check(MIN_JUMP, jprop)

    if as_json:
        print(json.dumps({"source": src, "android_dir": str(android), "found": found,
                          "checks": results, "log": hits, "policy": POLICY,
                          "recommended": TEMPLATE, "recommended_failures": tmpl_fail,
                          "stopgap": MIN_JUMP, "stopgap_failures": min_fail}, indent=2))
        return 1 if any(s == "FAIL" for s, _ in results) else 0

    print(f"Android build versions: {android}")
    print(f"Rules: {src}\n")
    print(f"{'item':<20}{'found':<22} where")
    labels = [("gradle", "Gradle"), ("agp", "AGP"), ("kotlin", "Kotlin (KGP)"), ("java", "JDK"),
              ("java_home", "org.gradle.java.home"), ("minsdk", "minSdk"), ("java_target", "Java target"),
              ("kotlin_target", "Kotlin jvmTarget")]
    for key, label in labels:
        if key in found:
            print(f"{label:<20}{found[key][0]:<22} {found[key][1]}")
        elif key in ("gradle", "agp", "kotlin", "java"):
            print(f"{label:<20}{'not found':<22} -")
    print("\nChecks:")
    for st, msg in results:
        print(f"  [{st}] {msg}")
    if log:
        print(f"\nBuild log signatures ({log}):")
        for ln, msg in hits or [(0, "none recognised; read the first 'What went wrong' block")]:
            print(f"  line {ln}: {msg}")
    print(f"\nRecommended set (Flutter template): Gradle {TEMPLATE['gradle']}, AGP {TEMPLATE['agp']}, "
          f"Kotlin {TEMPLATE['kotlin']}, with JDK {jprop}  -> "
          + ("all pairwise checks pass" if not tmpl_fail else "FAILS: " + "; ".join(tmpl_fail)))
    print(f"Stopgap set (no AGP 9 migration, still warns): Gradle {MIN_JUMP['gradle']}, AGP {MIN_JUMP['agp']}, "
          f"Kotlin {MIN_JUMP['kotlin']}, with JDK {jprop}  -> "
          + ("all pairwise checks pass" if not min_fail else "FAILS: " + "; ".join(min_fail)))
    fails = sum(1 for s, _ in results if s == "FAIL")
    warns = sum(1 for s, _ in results if s == "WARN")
    print(f"\nSummary: {fails} FAIL, {warns} WARN")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
