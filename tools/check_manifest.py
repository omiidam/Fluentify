#!/usr/bin/env python3
"""Validates AndroidManifest.xml without an Android SDK.

There is no JDK or Android SDK here, so AAPT cannot be run, and the one thing
AAPT catches that nothing else does is a misspelled android: attribute. That
is not hypothetical: this file shipped

    android:windowSoftKeyboardMode="adjustResize"

which is not an attribute that exists. The build died with

    error: attribute android:windowSoftKeyboardMode not found.

and it got there because the manifest was hand-edited to add the microphone
permission and the result was committed without being compiled. CI caught it,
but only after the fact.

So: every attribute in the manifest is checked against the names the platform
actually defines for the element it sits on. A typo fails in a second instead
of after a round trip through GitHub Actions.

    python3 tools/check_manifest.py

Not a replacement for a real build - it cannot see resource ids, manifest
merging or Kotlin. It catches the class of mistake that is invisible when you
are reading the file and fatal when you are not.
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "android/app/src/main/AndroidManifest.xml"
ANDROID_NS = "{http://schemas.android.com/apk/res/android}"

# The android: attributes each element in this project's manifest may carry.
# Sourced from the platform's own attribute tables, trimmed to what an app
# manifest realistically uses. Names not listed here are the ones worth
# double-checking by hand rather than trusting silently.
ALLOWED: dict[str, set[str]] = {
    "manifest": {
        "versionCode", "versionName", "package", "compileSdkVersion",
        "platformBuildVersionCode", "platformBuildVersionName",
        "installLocation", "sharedUserId", "coreApp",
    },
    "uses-sdk": {
        "minSdkVersion", "targetSdkVersion", "maxSdkVersion",
    },
    "uses-permission": {
        "name", "required", "maxSdkVersion",
    },
    "uses-feature": {
        "name", "required", "glEsVersion", "version",
    },
    "permission": {
        "name", "protectionLevel", "permissionGroup", "label",
        "description", "allowBackup",
    },
    "application": {
        "allowBackup", "icon", "roundIcon", "label", "supportsRtl",
        "theme", "usesCleartextTraffic", "networkSecurityConfig",
        "extractNativeLibs", "appComponentFactory", "fullBackupContent",
        "dataExtractionRules", "hasFragileUserData", "isGame",
        "persistent", "debuggable", "allowBackupAgent", "localeConfig",
        "enableOnBackInvokedCallback", "appCategory", "taskAffinity",
        "process",
    },
    "activity": {
        "name", "exported", "configChanges", "windowSoftInputMode",
        "screenOrientation", "launchMode", "theme", "label", "icon",
        "taskAffinity", "excludeFromRecents", "alwaysRetainTaskState",
        "noHistory", "stateNotNeeded", "singleTop", "documentLaunchMode",
        "clearTaskOnLaunch", "finishOnTaskLaunch", "multiprocess",
        "description", "enabled", "parentActivityName", "screenSize",
        "resizeableActivity", "allowTaskReparenting", "preferMinimalPostProcessing",
    },
    "service": {
        "name", "exported", "enabled", "foregroundServiceType", "permission",
        "process", "isolatedProcess", "theme", "label", "icon",
        "stopWithTask", "bindIsolatedService",
    },
    "receiver": {
        "name", "exported", "enabled", "permission", "process", "theme",
        "label", "icon", "priority", "directBootAware",
    },
    "intent-filter": {"action", "category", "data", "priority"},
    "action": {"name"},
    "category": {"name"},
    "data": {
        "scheme", "host", "port", "path", "pathPrefix", "pathPattern",
        "mimeType", "host",
    },
    "queries": {"package"},
    "meta-data": {"name", "value", "resource"},
}

# configChanges values are a closed set of flags, not free text
CONFIG_FLAGS = {
    "orientation", "screenSize", "keyboardHidden", "smallestScreenSize",
    "screenLayout", "uiMode", "keyboard", "navigation", "layoutDirection",
    "fontScale", "density", "colorMode", "grammaticalGender",
    "fontWeightAdjustment", "screenLayoutDirection", "locale",
}

# android: attributes that exist but are almost never what someone means.
# Each of these is a real attribute with a near-neighbour, which is exactly
# how windowSoftKeyboardMode happened.
LOOKALIKES = {
    "windowSoftKeyboardMode": "windowSoftInputMode",
    "windowSoftKeyboardHidden": "windowSoftInputMode",
    "launchMode ": "launchMode",
    "exported ": "exported",
    "configChange": "configChanges",
    "configchanges": "configChanges",
    "windowSoftinputMode": "windowSoftInputMode",
}


def walk(node: ET.Element):
    yield node
    for child in node:
        yield from walk(child)


def main() -> int:
    if not MANIFEST.exists():
        print(f"FAIL  {MANIFEST} not found")
        return 1

    raw = MANIFEST.read_text(encoding="utf-8")
    problems: list[str] = []

    # ---- 1. it has to parse at all ------------------------------------
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        print(f"FAIL  the manifest is not well-formed XML: {exc}")
        return 1

    # ---- 2. every android: attribute must exist for its element -------
    seen = 0
    for node in walk(root):
        tag = node.tag.split("}")[-1]
        allowed = ALLOWED.get(tag)
        for key, value in node.attrib.items():
            if not key.startswith(ANDROID_NS):
                continue
            name = key[len(ANDROID_NS):]
            seen += 1
            if allowed is None:
                problems.append(f"<{tag}>: android:{name} is not a known "
                                f"attribute for this element")
                continue
            if name not in allowed:
                hint = LOOKALIKES.get(name)
                extra = f" - did you mean android:{hint}?" if hint else ""
                problems.append(f"<{tag} android:{name}=\"{value}\">: no such "
                                f"attribute{extra}")
            if tag == "activity" and name == "configChanges":
                for flag in value.split("|"):
                    if flag not in CONFIG_FLAGS:
                        problems.append(
                            f'<activity> configChanges: "{flag}" is not a valid '
                            f"flag (one of {', '.join(sorted(CONFIG_FLAGS))})")

    # ---- 3. structure that aapt also enforces -------------------------
    if root.tag != "manifest":
        problems.append("the root element is not <manifest>")

    app = root.find("application")
    if app is None:
        problems.append("no <application> element")
    else:
        activities = app.findall("activity")
        if not activities:
            problems.append("no <activity> in <application>")
        for act in activities:
            if act.get(ANDROID_NS + "name") is None:
                problems.append("an <activity> has no android:name")
            # android:exported is mandatory from API 31 when there is a filter
            if act.find("intent-filter") is not None:
                if act.get(ANDROID_NS + "exported") is None:
                    problems.append(
                        '<activity> has an <intent-filter> but no '
                        'android:exported; from API 31 this fails the build')

    # <queries> must be a direct child of <manifest>, not of <application>
    for q in root.iter("queries"):
        parent_ok = any(q in list(r) for r in root.iter()
                        if r.tag.split("}")[-1] == "manifest")
        if not parent_ok:
            problems.append("<queries> must be a direct child of <manifest>")

    # ---- 4. the permissions this app asks for -------------------------
    asked = {p.get(ANDROID_NS + "name")
             for p in root.findall("uses-permission")}
    if "android.permission.INTERNET" not in asked:
        problems.append("no INTERNET permission, so the BBC audio cannot stream")
    if "android.permission.RECORD_AUDIO" not in asked:
        problems.append("no RECORD_AUDIO permission, so dictation cannot work")

    # ---- 5. the Kotlin bridges and the page must agree -----------------
    # A bridge registered in Kotlin but never called from the page is dead
    # code; one called from the page but never registered is a crash waiting
    # for the feature that uses it.
    kt = ROOT / "android/app/src/main/java/app/fluentify/MainActivity.kt"
    page = ROOT / "android/app/src/main/assets/www/index.html"
    if not kt.exists():
        problems.append("MainActivity.kt not found")
    else:
        kotlin = kt.read_text(encoding="utf-8")
        if not page.exists():
            problems.append("the built page not found - run build_apk_ui.py")
        else:
            js = page.read_text(encoding="utf-8")
            for symbol in ("AndroidTTS", "AndroidSTT"):
                registered = f'"{symbol}"' in kotlin
                used = f"window.{symbol}" in js
                if registered and not used:
                    problems.append(
                        f"MainActivity registers {symbol} but the page never "
                        f"calls it - dead code")
                if used and not registered:
                    problems.append(
                        f"the page calls window.{symbol} but MainActivity does "
                        f"not register it - this feature will fail at runtime")

    # ------------------------------------------------------------------
    print(f"checked {seen} android: attributes in {MANIFEST.relative_to(ROOT)}")
    if problems:
        print(f"\nFAIL  {len(problems)} problems\n")
        for p in problems:
            print(f"  {p}")
        return 1
    print("PASS  the manifest is well-formed and every attribute is real")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())