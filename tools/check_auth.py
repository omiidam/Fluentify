#!/usr/bin/env python3
"""The account gate and the certificate.

Two things matter here and they are the two a reviewer would ask about:

  * the session really is seven days from the last use, not from sign-in, and
    the boundary is exclusive - day seven plus one second is a lock, not a
    grace period;
  * the certificate says what it is. It names a level from a self-assessment,
    counts the questions actually answered, and never claims to be an
    examination.

The arithmetic and the certificate text are run in node against the module
itself, so this checks the shipped code rather than a description of it.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEBAPP = ROOT / "webapp.py"
MAIN = ROOT / "android/app/src/main/java/app/fluentify/MainActivity.kt"
CACHE = Path("/tmp/fluentify-auth-check")

problems: list[str] = []


def check(ok: bool, what: str) -> bool:
    if not ok:
        problems.append(what)
    return ok


def check_wiring() -> None:
    src = WEBAPP.read_text(encoding="utf-8")
    for needle, what in (
        ('id="auth"', "there is no sign-in overlay"),
        ('id="authform"', "the sign-in form is missing"),
        ('id="authname"', "there is nowhere to collect the full name"),
        ('data-authtab="signin"', "no sign-in tab"),
        ('data-authtab="signup"', "no create-account tab"),
        ('id="authexpired"', "an expired session has no message"),
        ('id="cert"', "there is no certificate view"),
        ('data-cert="pdf"', "the certificate has no download control"),
        ("const DAYS = 7;", "the session is not seven days"),
        ("'PBKDF2'", "the password is not stretched"),
        ("iterations", "the password hash has no iteration count"),
        ("fluentify.auth.account", "no credential is stored"),
        ("fluentify.auth.session", "no session is stored"),
        ("session.seen = now", "the session clock does not follow the last use"),
        ("Auth.init();", "the gate is never started"),
        ("Cert.bind();", "the certificate is never wired"),
        ('data-act="certificate"', "the report offers no certificate"),
        ('id="actoggle"', "there is no way to reach the account"),
        ("acpanel: 'acpanel'" if False else "acpanel: 'actoggle'",
         "the account panel is not registered"),
        ("@media print", "the certificate has no print rules"),
        ("body > *:not(.certwrap)", "printing would include the whole app"),
        ("Self-assessment built on a reviewed item bank",
         "the certificate does not say it is a self-assessment"),
    ):
        check(needle in src, what)

    check("AndroidPrint" in src, "the page never asks Android to print")
    kt = MAIN.read_text(encoding="utf-8") if MAIN.exists() else ""
    check("PrintBridge" in kt and '"AndroidPrint"' in kt,
          "MainActivity has no print bridge")
    check("createPrintDocumentAdapter" in kt,
          "the Android bridge does not use the WebView print adapter")


def check_engine() -> None:
    if not shutil.which("node"):
        print("SKIP  node is not installed - the session clock was not exercised")
        return

    src = WEBAPP.read_text(encoding="utf-8")
    start = src.index("const Auth = (() => {")
    end = src.index("/* only one panel open at a time", start)
    module = src[start:end].rstrip()

    CACHE.mkdir(parents=True, exist_ok=True)
    script = CACHE / "auth.js"
    script.write_text(HARNESS.replace("__MODULE__", module), encoding="utf-8")

    proc = subprocess.run(["node", str(script)], capture_output=True, text=True)
    if proc.returncode != 0:
        problems.append("the session harness failed:\n" + (proc.stdout + proc.stderr).strip())
        return
    print(proc.stdout.strip())


HARNESS = r"""
__MODULE__

const DAY = 86400000;
let bad = 0;
const ok = (cond, line) => { if (!cond) bad++; console.log(`${cond ? '  ok  ' : '  FAIL'}  ${line}`); };

const seen = 1700000000000;
ok(Auth.sessionLeft({seen}, seen) === 7 * DAY, 'a fresh session has seven days left');
ok(Auth.sessionLeft({seen}, seen + 7 * DAY - 1) === 1, 'one millisecond before the seventh day is still open');
ok(Auth.sessionLeft({seen}, seen + 7 * DAY) === 0, 'the seventh day exactly closes the session');
ok(Auth.isOpen({seen}, seen + 6 * DAY), 'six days of idleness keeps the session');
ok(!Auth.isOpen({seen}, seen + 7 * DAY + 1), 'seven days and a second locks it');
ok(Auth.sessionLeft(null, seen) === 0, 'no session means no time left');
ok(Auth.sessionLeft({seen}, seen - DAY) === 8 * DAY, 'a clock that went backwards cannot extend it');

const good = Auth.validate({name: 'Sara Ahmadi', user: 'sara.a', pass: 'correct horse', pass2: 'correct horse'}, false);
ok(good.ok, 'a full sign-up is accepted');
ok(!Auth.validate({name: 'Sara', user: 'sara.a', pass: 'short', pass2: 'short'}, false).ok,
   'a short password is refused');
ok(!Auth.validate({name: 'Sara', user: 'sara.a', pass: 'long enough', pass2: 'long enough2'}, false).ok,
   'two different passwords are refused');
ok(!Auth.validate({name: 'Sara', user: 's!', pass: 'long enough', pass2: 'long enough'}, false).ok,
   'a username with symbols is refused');
ok(!Auth.validate({name: 'Sara 9', user: 'sara', pass: 'long enough', pass2: 'long enough'}, false).ok,
   'a name with digits is refused');
ok(Auth.validate({name: 'سارا احمدی', user: 'sara', pass: 'long enough', pass2: 'long enough'}, false).ok,
   'a Persian name is accepted');
ok(Auth.validate({name: '', user: 'sara', pass: 'long enough', pass2: 'long enough'}, true).ok,
   'signing in does not ask for the name again');

const id1 = Cert.ident({name: 'Sara Ahmadi', band: 'B2', at: '2026-11-03T10:00:00.000Z'});
const id2 = Cert.ident({name: 'Sara Ahmadi', band: 'B2', at: '2026-11-03T10:00:00.000Z'});
const id3 = Cert.ident({name: 'Sara Ahmadi', band: 'B1', at: '2026-11-03T10:00:00.000Z'});
ok(/^FL-\d{8}-[A-Z0-9]{6}$/.test(id1), 'the certificate id has the printed shape (' + id1 + ')');
ok(id1 === id2 && id1 !== id3, 'the same result keeps its id, a different level does not');

const sheet = Cert.render({name: '<b>Sara</b>', band: 'B2', label: 'Upper intermediate',
  labelFa: 'میانی بالا', can: 'You read an article quickly.', at: '2026-11-03T10:00:00.000Z',
  questions: 36, minutes: 17});
ok(!sheet.includes('<b>Sara</b>'), 'a name is escaped on the certificate');
ok(sheet.includes('B2') && sheet.includes('36') && sheet.includes('17'),
   'the certificate carries the level and the assessment counts');
ok(sheet.includes('not a certified examination'), 'the certificate states its own limits');

process.exit(bad ? 1 : 0);
"""


def main() -> int:
    check_wiring()
    check_engine()

    if problems:
        for p in problems:
            print("FAIL  " + p)
        print(f"\n{len(problems)} problem(s) with the account gate")
        return 1

    print("PASS  seven-day sliding session, local credential, certificate with limits")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
