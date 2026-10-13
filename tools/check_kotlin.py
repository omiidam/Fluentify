#!/usr/bin/env python3
"""Narrow static checks on the Kotlin sources.

There is no JDK or Android SDK in this repo, so `kotlinc` cannot be run, and
two compile errors have now shipped that only CI could see:

  * `val data = result.data ?: Bundle()` — result.data is Intent? and Bundle
    is Bundle, so the elvis widens to their common supertype and
    getStringArrayListExtra stops resolving
  * `c.toInt()` on a Char — hidden on Kotlin 1.9, replaced by `c.code`

Both are invisible when reading the file. Both are one line to fix and a
round trip through CI to find.

This is NOT a Kotlin compiler and does not try to be. It flags a small, named
set of constructs that have actually caused a build failure here, plus a few
API renames that are removed rather than merely deprecated. It will not catch
a genuine type error - for that, the Gradle build is still the answer, and CI
runs it on every push.

    python3 tools/check_kotlin.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "android/app/src/main/java/app/fluentify"

FAILURES: list[str] = []
CHECKS = 0

# (pattern, why it fails, suggestion or None)
DANGEROUS: list[tuple[str, str, str]] = [
    # --- the two that actually shipped ---
    (
        r"\?\s*Bundle\s*\(",
        "mixing an elvis fallback of Bundle() into an expression that is "
        "otherwise a different type widens it to their common supertype, and "
        "the original type's methods stop resolving",
        "keep the nullable type and use a safe call",
    ),
    (
        r"(\w+)\.toInt\(\)\s*<",
        "Char.toInt() is hidden on Kotlin 1.9 and will not compile",
        "use Char.code",
    ),
    # --- removed or renamed APIs, same failure mode ---
    (
        r"\bAsyncTask\b",
        "AsyncTask was removed in API 30",
        None,
    ),
    (
        r"\bstartActivityForResult\s*\(",
        "removed in favour of the Activity Result API",
        None,
    ),
    (
        r"onActivityResult\s*\(",
        "removed in favour of the Activity Result API",
        None,
    ),
    (
        r"getSerializableExtra\s*\(",
        "getSerializableExtra(String) was removed in API 33; use the typed "
        "overload",
        None,
    ),
    (
        r"Resources\.getColor\s*\(",
        "removed in API 23 in favour of ContextCompat.getColor",
        None,
    ),
    (
        r"\.compileKotlin\w*\(|CompileKotlin\b",
        None,
        None,
    ),
]

# Names the page expects the Activity to register, and the reverse.
REQUIRED_BRIDGES = ["AndroidTTS", "AndroidSTT"]


def check(name: str, ok: bool, detail: str = "") -> None:
    global CHECKS
    CHECKS += 1
    if not ok:
        FAILURES.append(f"{name}{': ' + detail if detail else ''}")


def main() -> int:
    files = sorted(SRC.rglob("*.kt")) if SRC.exists() else []
    if not files:
        print(f"FAIL  no Kotlin sources under {SRC}")
        return 1

    for path in files:
        src = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT)

        for pattern, why, suggestion in DANGEROUS:
            if not why:
                continue
            for m in re.finditer(pattern, src):
                line = src.count("\n", 0, m.start()) + 1
                hint = f" - {suggestion}" if suggestion else ""
                FAILURES.append(
                    f"{rel}:{line}: {why}{hint}  ({m.group(0)[:40]!r})")

        # every override must match a signature the SDK actually declares
        check(f"{rel.name}: WebViewClient overrides take WebResourceRequest",
              not re.search(
                  r"override fun should(?:InterceptRequest|OverrideUrlLoading)"
                  r"\s*\(\s*\w+\s*:\s*WebView\s*,\s*\w+\s*:\s*View\b",
                  src),
              "the View-based overloads are deprecated and gone from API 24+")

    # --- the page and the Activity must agree on the bridge names --------
    page = ROOT / "android/app/src/main/assets/www/index.html"
    all_kt = "\n".join(p.read_text(encoding="utf-8") for p in files)
    if page.exists():
        js = page.read_text(encoding="utf-8")
        for bridge in REQUIRED_BRIDGES:
            check(f"{bridge} is registered in Kotlin", f'"{bridge}"' in all_kt)
            check(f"{bridge} is called from the page", f"window.{bridge}" in js)
    else:
        check("the built page exists", False, "run build_apk_ui.py")

    # --- the Activity Result API, if used, must be registered before onCreate
    for path in files:
        src = path.read_text(encoding="utf-8")
        if "registerForActivityResult" not in src:
            continue
        check(f"{path.name}: Activity result launchers are properties, not locals",
              all(re.search(rf"(private )?val \w+ =\s*\n?\s*registerForActivityResult",
                            src) for _ in [0]),
              "registering in onCreate is too late and throws at runtime")
        check(f"{path.name}: recogniser results are read from a nullable Intent",
              not re.search(r"result\.data\s*\?:", src),
              "an elvis fallback of the wrong type widens the expression")
        check(f"{path.name}: Char.toInt() is not used",
              not re.search(r"\bc\.toInt\(\)", src))

    # ----------------------------------------------------------------------
    if FAILURES:
        print(f"FAIL  {len(FAILURES)} of {CHECKS + len(FAILURES)} Kotlin checks\n")
        for f in FAILURES:
            print(f"  {f}")
        print("\n  These are narrow, known-bad constructs - not a type checker. "
              "The Gradle build remains the real gate.")
        return 1
    print(f"PASS  all {CHECKS} Kotlin checks ({len(files)} file(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())