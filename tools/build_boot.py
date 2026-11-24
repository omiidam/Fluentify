#!/usr/bin/env python3
"""Compile the loading page from TypeScript into the three files it ships as.

The loading page is one thing made of three: its markup, its stylesheet and the
module that drives them. All three are authored in web/boot/:

    boot.ts     the module: the bar, the percentage, the floor, the ways down
    shell.ts    the card's markup and the two loading stylesheets, as strings

and this build writes the three files the page inlines as it ships:

    boot.js     the module, compiled
    boot.html   the markup, for the <body>
    boot.css    the stylesheet, for the <style> block

They are committed because neither the browser nor the Gradle build has a
TypeScript compiler, and neither should grow one to draw a loading screen. The
page inlines them at their markers, so the overlay is in the first frame rather
than injected after it. tools/check_boot.py fails when the built files drift
from the source, so a forgotten build is a red check and not a page quietly
running last week's loader.

Run this after editing anything in web/boot/.

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
DIR = ROOT / "web" / "boot"
SRC = DIR / "boot.ts"
SHELL = DIR / "shell.ts"
OUT = DIR / "boot.js"
CSS = DIR / "boot.css"
HTML = DIR / "boot.html"
CACHE = ROOT / "tools" / ".cache"

BANNER = "/* ---- the boot screen ----"
CARD = '<div class="boot" id="boot"'


def bun() -> str:
    """The bun on PATH, or the one the desktop app ships."""
    found = shutil.which("bun")
    if found:
        return found
    fallback = os.environ.get("FREEBUFF_BUN")
    if fallback and Path(fallback).exists():
        return fallback
    sys.exit("build_boot: bun is not installed - it is the TypeScript compiler here")


def compile_module(bun_bin: str) -> None:
    proc = subprocess.run(
        [bun_bin, "build", str(SRC), "--outfile", str(OUT), "--target=browser"],
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


def compile_shell(bun_bin: str) -> None:
    """Evaluate shell.ts with bun and write its two strings out."""
    CACHE.mkdir(parents=True, exist_ok=True)
    driver = CACHE / "shell_dump.mjs"
    driver.write_text(
        "import {BOOT_CSS, BOOT_MARKUP} from " +
        json.dumps(SHELL.as_uri()) + ";\n"
        "process.stdout.write(JSON.stringify({css: BOOT_CSS, markup: BOOT_MARKUP}));\n",
        encoding="utf-8")
    proc = subprocess.run([bun_bin, str(driver)], cwd=str(ROOT),
                          capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit("build_boot: the markup and stylesheet did not compile\n" +
                 (proc.stderr or proc.stdout).strip()[:800])
    try:
        shell = json.loads(proc.stdout)
    except json.JSONDecodeError:
        sys.exit("build_boot: shell.ts did not export BOOT_CSS / BOOT_MARKUP")

    css = shell["css"]
    markup = shell["markup"]
    if BANNER not in css or CARD not in markup:
        sys.exit("build_boot: the loading page's markup or stylesheet is empty")
    CSS.write_text(css, encoding="utf-8")
    HTML.write_text(markup, encoding="utf-8")


def main() -> int:
    for path in (SRC, SHELL):
        if not path.exists():
            sys.exit(f"build_boot: {path.relative_to(ROOT)} is missing")
    bun_bin = bun()
    compile_module(bun_bin)
    compile_shell(bun_bin)

    if shutil.which("node"):
        for path in (OUT,):
            check = subprocess.run(["node", "--check", str(path)],
                                   capture_output=True, text=True)
            if check.returncode != 0:
                sys.exit("build_boot: the compiled loader is not valid JavaScript\n" +
                         (check.stderr or "").strip()[:600])

    print(f"built {OUT.relative_to(ROOT)} "
          f"({len(OUT.read_text(encoding='utf-8').splitlines())} lines), "
          f"{CSS.relative_to(ROOT)} "
          f"({len(CSS.read_text(encoding='utf-8').splitlines())} lines), "
          f"{HTML.relative_to(ROOT)} "
          f"({len(HTML.read_text(encoding='utf-8').splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
