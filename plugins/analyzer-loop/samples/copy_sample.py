#!/usr/bin/env python3
"""Copy one Analyzer Loop sample into a working directory so the plugin's own copy stays pristine.
Standard library only.

Usage: python3 copy_sample.py <sample-name> [dest-dir]
  sample-name  stale_app | upgrade_app | android_mismatch | golden_drift
  dest-dir     default: ./<sample-name>. Refuses to overwrite an existing directory.
Skips .dart_tool/, build/ and test/failures/ so the copy starts clean.
"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAMPLES = sorted(p.name for p in HERE.iterdir() if p.is_dir() and p.name != "outputs")


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help") or a[0] not in SAMPLES:
        print(__doc__)
        print("Available samples:", ", ".join(SAMPLES))
        return 2
    src = HERE / a[0]
    dest = Path(a[1] if len(a) > 1 else a[0]).resolve()
    if dest.exists():
        print(f"{dest} already exists; using it as is (delete it first for a fresh copy).")
        return 0
    def skip(d, names):
        out = {n for n in names if n in (".dart_tool", "build")}
        if Path(d).name == "test" and "failures" in names:
            out.add("failures")
        return out

    shutil.copytree(src, dest, ignore=skip)
    n = sum(1 for p in dest.rglob("*") if p.is_file())
    print(f"Copied sample {a[0]} to {dest} ({n} files).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
