#!/usr/bin/env python3
"""Grounded Scala doctor: why is Scala code intelligence (Metals) not working?

Usage: python3 doctor.py [project_dir]          (default: current directory)

Read-only. Checks, in order:
  1. java on PATH and its major version (Metals needs a JDK; 17+ recommended)
  2. metals on PATH (the plugin's .lsp.json launches the command `metals`)
     - also looks in the default Coursier install dirs, to catch
       "installed but not on PATH", the most common setup failure
  3. cs (Coursier), used to install and update Metals
  4. the project's build tool (sbt, Mill, scala-cli) and its launcher
  5. .gitignore covers Metals/Bloop/BSP output dirs
  6. recent ERROR lines in .metals/metals.log and the global Metals log
Prints one line per check (OK / MISSING / WARN / INFO) and the exact fix
commands. Exits 1 if anything blocks the language server from starting.
Changes nothing on disk.
"""
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
COURSIER_DIRS = [
    HOME / ".local/share/coursier/bin",                    # Linux default
    HOME / "Library/Application Support/Coursier/bin",     # macOS default
    HOME / "AppData/Local/Coursier/data/bin",              # Windows default
]
IS_MAC = platform.system() == "Darwin"
IS_WIN = platform.system() == "Windows"
results = []   # (status, label, detail, fix)


def add(status, label, detail="", fix=""):
    results.append((status, label, detail, fix))


def run(cmd, timeout=20):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (r.stdout + r.stderr).strip()
    except Exception as e:  # noqa: BLE001 - report, never crash
        return f"<failed: {e}>"


def find_off_path(name):
    for d in COURSIER_DIRS:
        for cand in (d / name, d / (name + ".bat")):
            if cand.exists():
                return cand
    return None


def path_fix(found):
    d = found.parent
    if IS_WIN:
        return f'Add "{d}" to PATH (or run: cs setup), then restart Claude Code.'
    return (f'echo \'export PATH="$PATH:{d}"\' >> ~/.bashrc   (or ~/.zshrc), '
            "then open a new shell and restart Claude Code.")


def install_cs_fix():
    if IS_MAC:
        return "brew install coursier && cs setup"
    if IS_WIN:
        return "Download cs-x86_64-pc-win32.zip from https://get-coursier.io/docs/cli-installation, then: cs setup"
    return ("curl -fL https://github.com/coursier/coursier/releases/latest/download/"
            "cs-x86_64-pc-linux.gz | gzip -d > cs && chmod +x cs && ./cs setup")


def check_java():
    java = shutil.which("java")
    if not java:
        add("MISSING", "java", "no JDK on PATH; Metals cannot start",
            "cs java --jvm 17 --setup   (or install any JDK 17+ and put it on PATH)")
        return
    out = run([java, "-version"])
    m = re.search(r'version "(\d+)(?:\.(\d+))?', out)
    major = 0
    if m:
        major = int(m.group(1))
        if major == 1 and m.group(2):
            major = int(m.group(2))
    if major and major < 17:
        add("WARN", "java", f"JDK {major} at {java}; Metals and Scala 3 tooling expect 17+",
            "cs java --jvm 17 --setup")
    else:
        add("OK", "java", f"JDK {major or '?'} at {java}")


def check_tool(name, required, purpose, fix):
    p = shutil.which(name)
    if p:
        ver = ""
        if name == "cs":
            vs = [l for l in run([p, "version"]).splitlines() if re.match(r"^\d+\.\d+", l.strip())]
            ver = vs[-1].strip() if vs else ""
        add("OK", name, f"{p} {ver}".strip())
        return True
    off = find_off_path(name)
    if off:
        add("MISSING" if required else "WARN", name,
            f"installed at {off} but that directory is not on PATH ({purpose})", path_fix(off))
    else:
        add("MISSING" if required else "WARN", name, f"not found ({purpose})", fix)
    return False


def detect_build(root):
    tools = []
    if (root / "build.sbt").exists() or (root / "project" / "build.properties").exists():
        tools.append("sbt")
    if any((root / f).exists() for f in ("build.mill", "build.mill.scala", "build.sc")):
        tools.append("mill")
    using = False
    for f in list(root.glob("*.scala")) + list(root.glob("*.sc")):
        try:
            if "//> using" in f.read_text(errors="replace")[:4000]:
                using = True
                break
        except OSError:
            pass
    if using or (root / ".scala-build").exists() or (root / "project.scala").exists():
        tools.append("scala-cli")
    return tools


def check_build(root):
    tools = detect_build(root)
    if not tools:
        add("WARN", "build tool", f"no build.sbt, build.mill or scala-cli `//> using` file in {root}",
            "Run Claude Code from the project root (the folder with build.sbt / build.mill / project.scala).")
        return
    add("INFO", "build tool", "detected: " + ", ".join(tools))
    if "sbt" in tools:
        if shutil.which("sbt"):
            add("OK", "sbt", shutil.which("sbt"))
        else:
            check_tool("sbt", False, "needed for `sbt --client` builds from the terminal; Metals has its own launcher",
                       "cs install sbt   (or: brew install sbt)")
        bp = root / "project" / "build.properties"
        if bp.exists():
            m = re.search(r"sbt\.version\s*=\s*(\S+)", bp.read_text())
            add("INFO", "sbt.version", m.group(1) if m else "not set in project/build.properties")
    if "mill" in tools:
        if (root / "mill").exists() or (root / "millw").exists():
            add("OK", "mill", "repo-local launcher ./mill")
        elif shutil.which("mill"):
            add("OK", "mill", shutil.which("mill"))
        else:
            add("WARN", "mill", "no ./mill launcher and no mill on PATH",
                "cs install mill   (or add the ./mill bootstrap script from mill-build.org)")
    if "scala-cli" in tools:
        check_tool("scala-cli", False, "needed to compile this scala-cli project",
                   "cs install scala-cli   (or: brew install Virtuslab/scala-cli/scala-cli)")


def check_gitignore(root):
    gi = root / ".gitignore"
    want = [".metals/", ".bloop/", ".bsp/"]
    if (root / ".scala-build").exists() or "scala-cli" in detect_build(root):
        want.append(".scala-build/")
    if not gi.exists():
        add("WARN", ".gitignore", "missing; Metals writes .metals/ .bloop/ .bsp/ here",
            "Add these lines to .gitignore: " + " ".join(want))
        return
    text = gi.read_text(errors="replace")
    missing = [w for w in want if w.rstrip("/") not in text]
    if missing:
        add("WARN", ".gitignore", "does not ignore " + " ".join(missing),
            "Append to .gitignore: " + " ".join(missing))
    else:
        add("OK", ".gitignore", "ignores " + " ".join(want))


def tail_errors(log, n=5):
    try:
        lines = log.read_text(errors="replace").splitlines()[-4000:]
    except OSError:
        return []
    errs = [l.strip() for l in lines if re.search(r"\bERROR\b|Exception|failed to", l)]
    return errs[-n:]


def check_logs(root):
    logs = [root / ".metals" / "metals.log"]
    gdirs = [HOME / ".cache/org.scalameta.metals", HOME / "Library/Caches/org.scalameta.metals",
             HOME / "AppData/Local/scalameta/metals/cache"]
    logs += [g / "global.log" for g in gdirs]
    seen = False
    for log in logs:
        if not log.exists():
            continue
        seen = True
        errs = tail_errors(log)
        if errs:
            add("WARN", f"log {log}", "recent errors:\n      " + "\n      ".join(e[:200] for e in errs),
                "Read the full log around these lines; common causes: build import failed, wrong JDK, sbt not found.")
        else:
            add("OK", f"log {log}", "no recent ERROR lines")
    if not seen:
        add("INFO", "metals logs", "none yet (.metals/metals.log appears after Metals first starts in this project)")


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    print(f"Grounded Scala doctor - project: {root}")
    print(f"platform: {platform.system()} {platform.machine()}, python {platform.python_version()}\n")
    check_java()
    have_metals = check_tool("metals", True, "the language server this plugin launches",
                             "cs install metals   (install Coursier first if `cs` is missing)")
    check_tool("cs", not have_metals and not find_off_path("metals"), "Coursier, used to install and update Metals", install_cs_fix())
    check_build(root)
    check_gitignore(root)
    check_logs(root)

    width = max(len(r[1]) for r in results)
    for status, label, detail, _ in results:
        print(f"[{status:<7}] {label:<{width}}  {detail}")
    fixes, seen = [], {}
    for s, l, _, f in results:
        if f and s in ("MISSING", "WARN"):
            if f in seen:
                fixes[seen[f]] = (fixes[seen[f]][0] + ", " + l, f)
            else:
                seen[f] = len(fixes)
                fixes.append((l, f))
    if fixes:
        print("\nFixes (run these yourself; this script changed nothing):")
        for i, (label, fix) in enumerate(fixes, 1):
            print(f"  {i}. {label}: {fix}")
    blocking = [r for r in results if r[0] == "MISSING"]
    print("\nVerdict: " + ("BLOCKED - Metals cannot start until the MISSING items are fixed. "
                           "Restart Claude Code after fixing."
                           if blocking else "READY - Metals can start. First import of a build "
                           "can take 1-5 minutes."))
    sys.exit(1 if blocking else 0)


if __name__ == "__main__":
    main()
