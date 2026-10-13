#!/usr/bin/env python3
"""Run every check, in the order that makes a failure easiest to read.

    python3 tools/check_all.py

Four suites, each answering a different question:

  harness        can the bot answer what a learner asks? (capability)
  harness_round5 is the content well-formed and the input handling safe?
  tests_js_vs_python  does the APK engine still agree with the CLI, message
                      for message?
  tests_flow_parity   do they still agree over a *conversation*? Memory only
                      shows up across several messages, so a single-message
                      test cannot see it at all.
  harness_stt   is the CEFR listening grader still calibrated, is stt.json still
                the shape the web app, the CLI and Android all read, and does
                the offline bundle still start?
  check_manifest  is every android: attribute in the manifest one the platform
                actually defines? There is no SDK here, so this is the only
                thing standing between a typo and a CI round trip.
  check_ui      is the page wired up - does every generated panel repaint when
                it opens, does the mic repaint on save, is toast() defined?
                Static, because the only real test is a browser and this
                project has no browser automation. It catches the Review panel
                opening blank, which looked like data loss and was not.

Exit code is non-zero if any suite fails.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SUITES = [
    ("content & input integrity", [sys.executable, "tools/harness_round5.py"]),
    ("capability harness", [sys.executable, "tools/harness.py"]),
    ("python/js message parity", [sys.executable, "tests_js_vs_python.py"]),
    ("python/js conversation parity", [sys.executable, "tests_flow_parity.py"]),
    ("BBC grader & speech-to-text", [sys.executable, "tools/harness_stt.py"]),
    ("android manifest", [sys.executable, "tools/check_manifest.py"]),
    ("page wiring (static)", [sys.executable, "tools/check_ui.py"]),
]


def main() -> int:
    results = []
    for label, cmd in SUITES:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        tail = [line for line in proc.stdout.strip().split("\n") if line.strip()]
        summary = tail[-1] if tail else "(no output)"
        results.append((label, proc.returncode, summary, proc.stderr))

    width = max(len(label) for label, _, _, _ in results)
    print()
    failed = 0
    for label, code, summary, stderr in results:
        mark = "PASS" if code == 0 else "FAIL"
        failed += code != 0
        print(f"  {mark}  {label.ljust(width)}   {summary}")
        if code != 0:
            for line in stderr.strip().split("\n")[-5:]:
                print(f"        {line}")
    print()
    if failed:
        print(f"{failed} of {len(results)} suites failed")
        return 1
    print(f"all {len(results)} suites green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())