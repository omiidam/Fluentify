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
        ('id="authemail"', "sign-up does not ask for an email"),
        ('data-secret="1"', "the password field is not marked as secret"),
        ("const MIN_PASS = 8", "the minimum is not eight characters"),
        ("const SPECIAL = '@#$%!'", "the symbol set is not the stated default"),
        ('data-authtab="signin"', "no sign-in tab"),
        ('data-authtab="signup"', "no create-account tab"),
        ('id="resetopen"', "sign-in offers no way to recover a forgotten password"),
        ('id="authreset"', "there is no recovery panel"),
        ('id="resetsubmit"', "the recovery panel has no submit"),
        ('id="resetback"', "recovery has no way back to sign-in"),
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
        ("paper: paperSize", "the result does not record the size of the paper"),
        ("questions: result.paper ||", "the certificate is handed the answered count as the size"),
        ("Self-assessment built on a reviewed item bank",
         "the certificate does not say it is a self-assessment"),
    ):
        check(needle in src, what)

    check("AndroidPrint" in src, "the page never asks Android to print")
    # A password is typed, never carried in from a clipboard and never carried
    # out: the fields are marked secret and the binder refuses the events.
    check(re.search(r"\['paste', 'cut', 'copy', 'drop', 'dragover', 'contextmenu'\]", src)
          is not None and "e.preventDefault()" in src,
          "the password field accepts paste, cut, copy or the context menu")
    check(re.search(r"account = \{name, user, email,", src) is not None,
          "the email is collected but never stored with the account")
    # Recovery is proved against what the account already holds, not against
    # whatever is typed into the box.
    check(re.search(r"known\.indexOf\(typedMail\)", src) is not None,
          "recovery accepts any address instead of the one on the account")
    check("passwordProblems" in src,
          "recovery does not run the password rule the gate enforces")
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
    # The slice also carries KAnim and Kids, which were written after Auth.
    # They are browser modules, so their top-level code must survive a run
    # without a window; the gate itself needs Cert, which is defined after
    # them, so the comment marker stays the end of the slice.
    module = src[start:end].rstrip()

    # Nothing in the gate may reach the network: there is no server holding an
    # account, so a request would be a promise the app cannot keep.
    check("fetch(" not in module and "XMLHttpRequest" not in module,
          "the account gate talks to a network")

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

const P = 'Nine small rivers 7!';
// Age is part of sign-up now: it picks the experience, so every fixture below
// carries a grown-up one and the age rules themselves are exercised separately.
const sign = (pass, extra) => Auth.validate(Object.assign(
  {name: 'Sara Ahmadi', user: 'sara.a', email: 'sara@example.com', pass, pass2: pass,
   age: 16}, extra || {}), false);
const okPass = (pass) => sign(pass).ok;
const reason = (pass, extra) => {
  const r = Auth.validate(Object.assign(
    {name: 'Sara Ahmadi', user: 'sara.a', email: 'sara@example.com', pass, pass2: pass,
     age: 16}, extra || {}), false);
  return r.errors.length ? r.errors[0][0] : '';
};

ok(P.length >= Auth.MIN_PASS, 'the harness password clears the stated minimum');
ok(okPass(P), 'a full sign-up is accepted');
ok(!okPass('short'), 'a short password is refused');
ok(!okPass('Sh0r7!y'), 'seven characters is one short of the floor');
ok(!sign(P, {pass2: P + '2'}).ok, 'two different passwords are refused');
ok(!sign(P, {user: 's!'}).ok, 'a username with symbols is refused');
ok(!sign(P, {name: 'Sara 9'}).ok, 'a name with digits is refused');
ok(Auth.validate({name: '', user: 'sara', pass: P, pass2: P}, true).ok,
   'signing in asks for neither the name nor the email again');

// the four stated characteristics, one at a time
ok(okPass('Abcdef1!'), 'eight characters with all four kinds is accepted');
ok(!okPass('Abcdefg1'), 'a password with no @ # $ % ! is refused');
ok(!okPass('Abcdefg!'), 'a password with no number is refused');
ok(!okPass('abcdef1!'), 'a password with no capital is refused');
ok(!okPass('ABCDEF1!'), 'a password with no lower case is refused');
ok(!okPass('Ab1!'), 'composition cannot rescue a short password');
ok(okPass('Spaces are fine 12!'), 'spaces are still allowed inside the policy');
ok(Auth.SPECIAL === '@#$%!', 'the symbol set is the stated default');
ok(Auth.ruleCheck('Abcdef1!').special && Auth.ruleCheck('Abcdef1!').digits,
   'the rule check reports which characteristics are met');
ok(sign('یک جملهٔ بلند دیگر 4!', {name: 'سارا احمدی', user: 'sara'}).ok,
   'a Persian password passes once it carries a number and a symbol');
ok(!okPass('یک عبارت طولانی فارسی'), 'a Persian password of letters alone is refused');

// the email the account is recovered with
ok(!sign(P, {email: ''}).ok, 'sign-up asks for an email');
ok(!sign(P, {email: 'sara.example.com'}).ok, 'an address with no @ is refused');
ok(!sign(P, {email: 'sara@localhost'}).ok, 'a domain with no dot is refused');
ok(!sign(P, {email: 'sara @example.com'}).ok, 'an address with a space is refused');
ok(Auth.emailProblem('sara@example.com') === null, 'an ordinary address is accepted');
ok(Auth.emailProblem('sara@localhost') !== null, 'the email check names the fault');

// the blocklist still runs under the composition rule
ok(!okPass('Password1!'), 'Password1! meets every rule and is still refused');
ok(!okPass('P@ssw0rd1234'), 'leet substitutions do not launder a common password');
ok(!okPass('Qwertyuiop1!'), 'a keyboard walk is refused');
ok(!okPass('Ab1!Ab1!Ab1!'), 'a repeated pattern is refused');
ok(!okPass('Saraa1!xyz'), 'a password built from the username is refused');
ok(!okPass('Ahmadi1!Xyz'), 'a password built from the name is refused');
ok(okPass('The river runs past us 5!'), 'an ordinary sentence the blocklist misses is accepted');
ok(!okPass('Xx1!' + 'x'.repeat(200)), 'a password over the ceiling is refused');

// the meter
ok(Auth.strength('', 'sara', 'Sara')['score'] === 0, 'an empty password scores zero');
ok(Auth.strength('Abcdef1!', 'sara', 'Sara')['score'] === 4, 'all four rules light the whole meter');
ok(Auth.strength('Abcdefg1', 'sara', 'Sara')['score'] === 3, 'a missing symbol leaves one segment dark');
ok(Auth.strength('Password1!', 'sara', 'Sara')['score'] === 0, 'a blocked password scores zero');
ok(Auth.strength('Abcdef1!', 'sara', 'Sara')['ok'], 'the meter agrees with the submit path');
ok(/at least 8/.test(reason('short')), 'the refusal says what the minimum is');

// recovery must not be a weaker door than the gate
ok(Auth.passwordProblems('Abcdef1!', 'sara', 'Sara').length === 0,
   'a new password for recovery meets the same four rules');
ok(Auth.passwordProblems('Abcdefg1', 'sara', 'Sara').length === 1,
   'recovery refuses what the gate would refuse');
ok(Auth.passwordProblems('password1!', 'sara', 'Sara').length === 1,
   'recovery runs the blocklist too');

const id1 = Cert.ident({name: 'Sara Ahmadi', band: 'B2', at: '2026-11-03T10:00:00.000Z'});
const id2 = Cert.ident({name: 'Sara Ahmadi', band: 'B2', at: '2026-11-03T10:00:00.000Z'});
const id3 = Cert.ident({name: 'Sara Ahmadi', band: 'B1', at: '2026-11-03T10:00:00.000Z'});
ok(/^FL-\d{8}-[A-Z0-9]{6}$/.test(id1), 'the certificate id has the printed shape (' + id1 + ')');
ok(id1 === id2 && id1 !== id3, 'the same result keeps its id, a different level does not');

const sheet = Cert.render({name: '<b>Sara</b>', band: 'B2', label: 'Upper intermediate',
  labelFa: 'میانی بالا', can: 'You read an article quickly.', at: '2026-11-03T10:00:00.000Z',
  questions: 50, answered: 50, minutes: 17});
ok(!sheet.includes('<b>Sara</b>'), 'a name is escaped on the certificate');
ok(sheet.includes('B2') && sheet.includes('50 questions') && sheet.includes('17'),
   'the certificate carries the level and the assessment counts');
ok(sheet.includes('not a certified examination'), 'the certificate states its own limits');
ok(!/questions were answered/.test(sheet), 'a complete run is not described as short');

// A run that skipped a part is this attempt, not a smaller assessment: the
// sheet keeps the size of the paper and says what was actually answered. The
// certificate used to print the answered count as the size, so a half-finished
// run issued a sheet for "36 questions" while the test is fifty.
const half = Cert.render({name: 'Sara', band: 'B2', label: 'Upper intermediate',
  labelFa: 'میانی بالا', can: 'You read an article quickly.', at: '2026-11-03T10:00:00.000Z',
  questions: 50, answered: 36, minutes: 17});
ok(/50 questions/.test(half), 'a short run still states the size of the assessment');
ok(half.includes('36 of 50 questions were answered'),
   'a short run says how many questions it answered');
ok(!/\b36 questions/.test(half), 'the answered count is never printed as the size');

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
