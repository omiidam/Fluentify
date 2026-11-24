#!/usr/bin/env python3
"""Compile the boot screen from TypeScript into the file the page inlines.

web/boot/boot.ts is the source of the loader; web/boot/boot.js is the build
output, and it is committed because the web page and the offline APK both
inline it as it is shipped - neither the browser nor the Gradle build has a
TypeScript compiler, and neither should grow one to render a loading screen.

Run this after editing the TypeScript. tools/check_boot.py fails when the two
drift apart, so a forgotten build is a red check rather than a page quietly
running last week's loader.

    python3 tools/build_boot.py
"""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "web" / "boot" / "boot.ts"
OUT = ROOT / "web" / "boot" / "boot.js"


def bun() -> str:
    """The bun on PATH, or the one the desktop app ships."""
    found = shutil.which("bun")
    if found:
        return found
    fallback = os.environ.get("FREEBUFF_BUN")
    if fallback and Path(fallback).exists():
        return fallback
    sys.exit("build_boot: bun is not installed - it is the TypeScript compiler here")


def main() -> int:
    if not SRC.exists():
        sys.exit(f"build_boot: {SRC.relative_to(ROOT)} is missing")

    proc = subprocess.run(
        [bun(), "build", str(SRC), "--outfile", str(OUT), "--target=browser"],
        cwd=str(ROOT), capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit("build_boot: the TypeScript did not compile\n" +
                 (proc.stderr or proc.stdout).strip()[:800])

    js = OUT.read_text(encoding="utf-8")
    # bun stamps the source path it read as a leading comment. The path is this
    # machine's, so dropping it keeps the committed file identical everywhere.
    js = re.sub(r"\A//[^\n]*\.ts\n", "", js).lstrip("\n")
    if "Boot = (() =>" not in js:
        sys.exit("build_boot: the output does not define Boot - check the entry point")
    OUT.write_text(js, encoding="utf-8")

    check = subprocess.run(["node", "--check", str(OUT)], capture_output=True, text=True) \
        if shutil.which("node") else None
    if check is not None and check.returncode != 0:
        sys.exit("build_boot: the compiled loader is not valid JavaScript\n" +
                 (check.stderr or "").strip()[:600])

    print(f"built {OUT.relative_to(ROOT)} ({len(js.splitlines())} lines, "
          f"{len(js.encode('utf-8'))} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
