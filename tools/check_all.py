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
  check_kotlin   does the Kotlin avoid the constructs that have actually
                failed a build here? Narrow and named, not a type checker -
                Gradle in CI is still the real gate.
  check_ui      is the page wired up - does every generated panel repaint when
                it opens, does the mic repaint on save, is toast() defined?
                Static, because the only real test is a browser and this
                project has no browser automation. It catches the Review panel
                opening blank, which looked like data loss and was not.
  check_boot    do the loading screen's bar and its percentage agree? The
                label is the readout people actually read, and it used to run
                ahead of the bar it was reporting. Runs the shipped Boot code
                against a two-element stub, and refuses a CSS transition on
                the bar, because that is what put the two on separate clocks.
  check_seed_clock  is the fifty-message gate's clock right? It runs the
                shipped Seed code against a pinned clock at every hour of a
                day and both sides of 03:30 GMT, and refuses a countdown that
                is written once and then freezes, or a session that needs a
                reload to unlock.
  check_daily   is the Daily English catalogue sound, and do the CLI, the APK
                engine and the page pick the same three items for the same
                local date? The rotation exists in three places, one per
                runtime, and this compares all three over a year of dates and
                five timezones - including both 2026 daylight-saving nights,
                where the wait to midnight is not 24 hours.
  check_lexicon   is the dictionary sound, does it answer through the chat, and
                is it still invisible? No route, no panel, no tab: it is
                knowledge behind the existing conversation, and this refuses
                both a malformed shard and a new dictionary surface.
  check_analyser  is the bundled grammar engine accurate and honest? It runs
                the shipped 3.5 MB bundle over the sentences the feature was
                specified against plus contractions, unpunctuated input,
                unknown names, a garden-path sentence and mixed script, and
                refuses any dependency label, any invented offset, and any
                lesson chip whose topic the Knowledge Base cannot answer.

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
    ("boot loading meter", [sys.executable, "tools/check_boot.py"]),
    ("daily seed clock", [sys.executable, "tools/check_seed_clock.py"]),
    ("daily english rotation", [sys.executable, "tools/check_daily.py"]),
    ("offline grammar analyser", [sys.executable, "tools/check_analyser.py"]),
    ("dictionary knowledge", [sys.executable, "tools/check_lexicon.py"]),
    ("android kotlin (static)", [sys.executable, "tools/check_kotlin.py"]),
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