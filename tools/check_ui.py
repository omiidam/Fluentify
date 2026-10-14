#!/usr/bin/env python3
"""Source-level checks for the parts of the UI that only exist in the page.

The other suites cover Python: content, the bot engine, the BBC grader, the
manifest. None of them can see a panel that opens empty, because that is a
rendering bug and nothing in Python renders.

The bug this file exists for: the Review panel opened completely blank. The
words were saved, the badge counted them, localStorage had them - and
togglePanel only flipped a CSS class, so nothing on that path ever called
Review.paint(). It is invisible when you read the code, because every piece of
it is correct in isolation.

These are static checks, not a DOM test. Running the real page needs a
browser, and this project deliberately has no browser-automation dependency;
the interactive equivalent is done in the browser during development. What is
asserted here is that the wiring exists at all, which is what regressed.

    python3 tools/check_ui.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "webapp.py"
BUILT = ROOT / "android/app/src/main/assets/www/index.html"

FAILURES: list[str] = []
CHECKS = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global CHECKS
    CHECKS += 1
    if not ok:
        FAILURES.append(f"{name}{': ' + detail if detail else ''}")


def fn_body(src: str, name: str) -> str:
    """The body of `name(...)` up to its closing brace at the same indent."""
    m = re.search(rf"(?:function\s+)?\b{re.escape(name)}\s*\([^)]*\)\s*\{{", src)
    if not m:
        return ""
    start = m.end()
    depth, i = 1, start
    while i < len(src) and depth:
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
        i += 1
    return src[start:i - 1]


def obj_method(src: str, obj: str, method: str) -> str:
    m = re.search(rf"\b{re.escape(obj)}\s*=\s*\{{", src)
    if not m:
        return ""
    # methods live inside the object literal; scan forward for the name
    start = m.end()
    depth, i = 1, start
    while i < len(src) and depth:
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
        i += 1
    block = src[start:i - 1]
    m2 = re.search(rf"(?:^|\n)\s*{re.escape(method)}\s*\([^)]*\)\s*\{{", block)
    if not m2:
        return ""
    d, j = 1, m2.end()
    while j < len(block) and d:
        if block[j] == "{":
            d += 1
        elif block[j] == "}":
            d -= 1
        j += 1
    return block[m2.end():j - 1]


def main() -> int:
    if not SRC.exists():
        print(f"FAIL  {SRC} missing")
        return 1
    src = SRC.read_text(encoding="utf-8")

    # ------------------------------------------------- WCAG 2.5.3 label in name --
    # Lighthouse caught three tiles whose visible text was not inside the
    # accessible name - "Sounds" on screen, "Phonetics" to a screen reader.
    # A voice-control user says what they can see, so those tiles could not be
    # activated by their own label. The score was still 1.0, which is exactly
    # why it needed a check rather than a number to watch.
    for m in re.finditer(
        r'<button[^>]*class="hbtn[^"]*"[^>]*aria-label="([^"]+)"[^>]*>\s*'
        r'<i>[^<]*</i>\s*<span>([^<]+)</span>', src,
    ):
        name, visible = m.group(1), m.group(2).strip()
        check(f"the {visible!r} tile is named after what it says",
              visible.lower() in name.lower(),
              f'aria-label={name!r} does not contain the visible text; '
              f"a voice-control user cannot say {visible!r} to open it")

    # ---------------------------------------------------- lazy word archive --
    # word_arch.json is 302 KB of boot payload and only fills the Sentences
    # panel's word chips, so it is fetched on first use.
    # The boot statements are the top-level calls after PANEL_ON_OPEN is
    # declared; the hook that does fetch word_arch lives above them, so the
    # window has to start after it or this check just finds its own fix.
    boot = src[src.rindex("PANEL_ON_OPEN"):]
    boot = boot[boot.index("};") + 2:]
    # Anchored to column zero, so it finds the top-level boot call and not the
    # `await loadWordArch()` inside the save command, which is deliberate.
    check("word_arch is not fetched at boot",
          not re.search(r"^loadWordArch\(\)", boot, re.M),
          "302 KB of word chips should wait for the panel that shows them")
    hooks = re.search(r"PANEL_ON_OPEN\s*=\s*\{(.*?)\n\};", src, re.S)
    hook_body = hooks.group(1) if hooks else ""
    check("opening the Sentences panel is what fetches word_arch",
          "loadWordArch" in hook_body,
          "otherwise the word chips are a placeholder that never fills")
    # "save apple to review" looks a word up in the archive, so that path has
    # to wait for it rather than report the word as unknown.
    review = fn_body(src, "matchReviewCommand")
    check("saving a word waits for word_arch if it is not loaded",
          "await loadWordArch()" in review,
          "otherwise saving before the Sentences panel was ever opened fails")

    # Fetch and paint are separate because either can run first: offline the
    # archive is in memory and resolves before the topic buttons exist.
    # loadWordArch() alone paints whichever ran, leaving the placeholders.
    check("painting the word chips is separate from fetching them",
          "function paintWordArch(" in src,
          "one function cannot win both orderings")
    phrases = fn_body(src, "loadPhrases")
    check("the Sentences panel repaints the chips into its fresh slots",
          "await loadWordArch()" in phrases and "paintWordArch()" in phrases,
          "the topic buttons are rebuilt on every open, so the chips go with them")

    # ------------------------------------------------------- failed sends --
    # Two bugs shared by both builds: a message that produced no reply still
    # cost one of the fifty daily ones, and the composer was already cleared so
    # the words were gone unless they were put back.
    send = fn_body(src, "send")
    check("a failed send refunds the daily message",
          "Seed.add(-1)" in send,
          "nothing was taught, so nothing should have been charged")
    check("a failed send puts the words back in the composer",
          "input.value = text" in send,
          "losing a typed Persian sentence to a dropped connection is not acceptable")

    # The offline build is a separate copy of this path, produced by
    # build_apk_ui.py. It regressed silently once because the two were matched
    # as exact strings and any edit to one broke the other's pattern.
    builder = (ROOT / "build_apk_ui.py").read_text(encoding="utf-8")
    check("the offline build gets the same failure handling",
          builder.count("Seed.add(-1)") >= 1 and builder.count("input.value = text") >= 1,
          "build_apk_ui.py rewrites send(); it must keep both repairs")

    # ---------------------------------------------------------- bbc list --
    # The header used to quote doc.count while the list showed a filtered
    # subset, so it claimed 1126 episodes while the All tab held 1123 and no
    # level tab ever added up to the number printed above them.
    bbc = fn_body(src, "loadBBC")
    check("loadBBC exists", bool(bbc))
    check("the bbc header counts the episodes it lists",
          "episodes.length} BBC episodes" in bbc or
          "BBC episodes" in bbc and "doc.count" not in bbc.split("note.textContent")[1][:400],
          "a filtered list must not be captioned with the unfiltered total")
    check("bbc says how many were dropped",
          "neither audio nor transcript" in bbc,
          "an honest count has to explain the difference")

    # ---------------------------------------------------- review count badge --
    # It was at top:-3px / inset-inline-end:-3px, which is outside a 46px
    # button - and being a <span> it inherited .hbtn span's overflow:hidden,
    # so the tile clipped it in half and it read as a sliver on the edge.
    rbadge = re.search(r"\n  \.rbadge \{(.*?)\n  \}", src, re.S)
    rb = re.sub(r"/\*.*?\*/", "", rbadge.group(1), flags=re.S) if rbadge else ""
    check("the review badge sits inside its tile",
          not re.search(r"(top|inset-inline-end|right|left)\s*:\s*-\d", rb),
          "a negative offset puts it outside the button, where it is clipped "
          "into a sliver by the label's overflow:hidden")
    check("the review badge overrides the label's ellipsis",
          "text-overflow: clip" in rb,
          ".hbtn span sets ellipsis and nowrap, which is for labels not counts")

    # ---------------------------------------------------------- the backdrop --
    # The drifting background layer had `filter: blur(40px) saturate(140%)` on
    # it. A filter on an animated element is re-rasterised every frame on a
    # full-viewport element, which on a phone is the most expensive thing the
    # page can do - and the gradients were already soft, so it bought nothing.
    # Put one back and the cost returns silently.
    css_blocks = re.findall(r"<style>(.*?)</style>", src, re.S)
    for block in css_blocks:
        for rule in re.findall(r"([^{}]+)\{([^{}]*)\}", block):
            selector, body = rule[0].strip(), rule[1]
            # the shorthand, not animation-name: the stylesheet only ever
            # uses the shorthand, and requiring both meant the check silently
            # skipped everything - verified by putting the blur back and
            # watching it pass
            if not re.search(r"(^|[;\s])animation(-name)?\s*:", body):
                continue
            if not re.search(r"(^|[;\s])filter\s*:", body):
                continue
            check(f"nothing both animates and filters: {selector[:40]}",
                  False,
                  "a filter on an animated element is re-rasterised every "
                  "frame; gradients fading to transparent need no blur")

    # the ambient motion rules the project holds itself to
    check("the backdrop respects prefers-reduced-motion",
          re.search(r"@media \(prefers-reduced-motion: reduce\)\s*\{[^}]*"
                    r"\.backdrop::before[^}]*animation: none", src, re.S)
          is not None,
          "decorative motion has to collapse for anyone who asked for it")

    # --------------------------------------------------------------- the mic --
    # It was a click handler and nothing else. On Android a long press raises
    # the text-selection callout and the browser suppresses the second click,
    # so dictation started and nothing ever stopped it.
    mic = fn_body(src, "mountMic")
    check("the mic is driven by pointer events, not click alone",
          "pointerdown" in mic and "pointerup" in mic,
          "a click is suppressed by the long-press callout on Android")
    check("a cancelled press stops dictation",
          "pointercancel" in mic,
          "a gesture the system takes over ends the press without a click")
    check("the pointer is captured so a slide off the button still releases",
          "setPointerCapture" in mic,
          "people slide off a button without looking, and then it sticks")
    check("losing the capture is treated as the end of the press",
          "lostpointercapture" in mic,
          "otherwise a gesture taken over by the system leaves it listening")
    for cause, why in (("visibilitychange", "the page being hidden"),
                       ("pagehide", "the page being closed"),
                       ("blur", "the window losing focus")):
        check(f"dictation stops on {cause}",
              cause in mic,
              f"{why} leaves no way to stop it from the page")
    check("a stuck session is capped in length",
          "MAX_MS" in mic and "setTimeout(stop" in mic,
          "every escape route can still be missed by one path")
    check("the mic is told not to trigger the long-press callout",
          re.search(r"\.mic \{[^}]*touch-action:\s*none", src) is not None,
          "without touch-action the browser can steal the gesture")
    check("a recogniser that refuses to start is reported to the user",
          re.search(r"if \(!STT\.begin\(\)\)", mic) is not None,
          "begin() returns false on a denied permission; swallowing it leaves "
          "a button that does nothing")

    # ------------------------------------------------------- daily limit --
    # The moon rides a rail left to right as the counter goes 0 -> 50. It was
    # text that appeared only once the limit had already been hit.
    lockui = fn_body(src, "lockUI")
    check("the moon's position comes from the message counter",
          "--p" in lockui and "used / SEED_GOAL" in lockui,
          "the rail has to be driven by the count, not by the full/empty flag")
    check("the limit note is always present, not hidden until the limit",
          re.search(r'<div class="limitenote"[^>]*id="limitenote"(?![^>]*hidden)', src)
          is not None,
          "a progress indicator that only appears at 100% shows no progress")
    lockic = re.search(r"\n  \.limitenote \.lockic \{(.*?)\n  \}", src, re.S)
    # Comments out, or this check matches the comment that explains why the
    # transform was removed - which mentions translateX by name.
    lb = re.sub(r"/\*.*?\*/", "", lockic.group(1), flags=re.S) if lockic else ""
    # A % inside transform() resolves against the element's own box, so the
    # moon moved by a fraction of its own width and never left the start.
    check("the moon is positioned with left, not a percentage transform",
          "left: calc(var(--p" in lb and "translateX" not in lb,
          "a % in a transform resolves against the element, so it never travels")
    check("the rail keeps the moon inside it at both ends",
          "100% - 20px" in lb,
          "otherwise the moon hangs off the end of the track when full")

    # ------------------------------------------------- scroll-to-latest --
    # It was at bottom:78px, which is inside the composer, so it floated over
    # the message input. Now anchored to the transcript, whose height is not a
    # constant to drift against.
    check("the transcript is wrapped so the jump button can anchor to it",
          '<div class="chatwrap">' in src and "</div>\n  <button id=\"jump\"" not in src,
          "positioning the button against the window is what put it on the composer")
    check("the jump button lives inside that wrapper",
          re.search(r'<div class="chatwrap">.*?<button id="jump".*?</div>', src, re.S)
          is not None)
    jumpcss = re.search(r"\n  \.jump \{(.*?)\n  \}", src, re.S)
    jb = jumpcss.group(1) if jumpcss else ""
    # The offset is only safe because the wrapper is the containing block:
    # 14px then means 14px above the last message whatever the chrome's
    # height, instead of 14px up from the app and on top of the composer.
    wrap = re.search(r"\n  \.chatwrap \{(.*?)\n  \}", src, re.S)
    check("the jump button is offset from the transcript, not from the window",
          wrap is not None and "position: relative" in wrap.group(1)
          and "position: absolute" in jb,
          "without a positioned wrapper, bottom: is measured from the app and "
          "lands on the composer again the moment the chrome changes height")
    check("the jump button is centred on the transcript",
          "left: 50%" in jb and "translateX(-50%)" in jb,
          "the reading column is centred here, so the button belongs there too")
    check("the press state keeps the centring",
          ".jump:active" in src and "translateX(-50%) scale(.93)" in src,
          "a bare scale() drops translateX(-50%) and the button lurches sideways")
    check("the jump button meets the touch target minimum",
          re.search(r"width: 44px", jb) is not None)
    check("the jump button says how much is waiting below",
          "unread" in src and 'id="jumpn"' in src,
          "a scroll button that cannot say what you are missing is pressed speculatively")
    check("reaching the bottom clears the unread count",
          re.search(r"if \(pinned\) unread = 0", src) is not None)

    # The suggestion row was left to shrink and got squeezed to 19px against
    # 38px chips, showing every suggestion as its bottom half.
    chips = re.search(r"\n  \.chips \{(.*?)\n  \}", src, re.S)
    check("the suggestion row keeps its natural height",
          chips is not None and "flex: none" in chips.group(1),
          "it was being squeezed and clipped; the transcript should shrink instead")

    # ------------------------------------------------------- review list --
    # The regression: opening the panel painted nothing.
    toggle = fn_body(src, "togglePanel")
    check("togglePanel exists", bool(toggle))
    check("togglePanel routes through the panel shell",
           "Panels.toggle" in toggle,
           "focus and aria-expanded must not diverge from the open class")
    # The hook used to run in togglePanel. It now lives in Panels.set(), which
    # is the only thing that opens a panel. Checking the old location would let
    # the exact regression this file was written for come back unnoticed.
    openbody = fn_body(src, "set")
    check("opening a panel runs its per-panel hook",
           "if (hook) hook();" in openbody,
           "generated panels must repaint on open")
    check("togglePanel passes the per-panel hook down",
           "PANEL_ON_OPEN" in toggle)

    hooks = re.search(r"PANEL_ON_OPEN\s*=\s*\{(.*?)\n\};", src, re.S)
    check("PANEL_ON_OPEN is declared", bool(hooks))
    hook_body = hooks.group(1) if hooks else ""
    check("the review panel is wired to repaint on open",
           "rpanel" in hook_body and "Review.paint()" in hook_body,
           hook_body.strip()[:70])

    add = obj_method(src, "Review", "add")
    check("Review.add exists", bool(add))
    check("Review.add repaints after saving",
           "this.refresh()" in add,
           "saving a word with the panel open must update it immediately")
    check("Review.refresh only paints when the panel is open",
           "classList.contains('open')" in obj_method(src, "Review", "refresh"),
           "painting a hidden panel on every add() is wasted work")

    paint = obj_method(src, "Review", "paint")
    check("Review.paint has an empty state",
           "No words saved yet" in paint,
           "an empty list must say what to do, not show nothing")

    badge = obj_method(src, "Review", "paintBadge")
    check("the badge reflects the saved count",
           "this.items.length" in badge)

    # ---------------------------------------------------------- mic button --
    check("the mic icon is an SVG, not an emoji",
           "btn.innerHTML = MIC_ICON" in src)
    check("mountMic is guarded against a double mount",
           "if (document.getElementById('mic')) return;" in src)
    check("the mic is never given the disabled attribute",
           re.search(r"(?<![A-Za-z_$])btn\.disabled", src) is None,
           "a disabled button does not fire click, so tapping it would be dead")

    # ------------------------------------------------------------- toasts --
    check("toast() is defined", "function toast(" in src)
    check("toast() has a host element", 'id="toasthost"' in src)

    # ------------------------------------------------------------- motion --
    check("the motion module is a single IIFE",
           src.count("const Motion = (() =>") == 1)
    check("motion is initialised on boot", "Motion.init();" in src)

    # ------------------------------------------------------- speech to text
    stt = fn_body(src, "STT") or src[src.index("const STT = {"):][:6000]
    check("STT picks an engine at runtime", "engine()" in src)
    check("STT falls back to the Android bridge",
           "window.AndroidSTT" in src)
    check("a recogniser that refuses to start is reported",
           "if (!STT.begin())" in src,
           "otherwise a denied permission is a button that does nothing")

    # --------------------------------------------------- the built bundle --
    if BUILT.exists():
        built = BUILT.read_text(encoding="utf-8")
        check("the built page carries the review on-open hook",
              "PANEL_ON_OPEN" in built)
        check("the built page carries the mic SVG", "MIC_ICON" in built)
        check("the built page carries toast()", "function toast(" in built)
        loaded = re.findall(r"loadJSON\('([^']+)'", built)
        check("the built page still loads every data file",
              len(loaded) >= 13, f"only {len(loaded)}: {loaded}")
        # The offline boot hands its data to the engine through a positional
        # destructure. Leaving one name in after its loadJSON() came out of
        # the Promise.all shifts every name after it by one - the engine then
        # builds with the wrong file and no suite notices, because bot.js is
        # only ever constructed correctly on the web side.
        i = built.find("Promise.all([")
        if i != -1:
            j = built.find(".then(([", i)
            k = built.find("]) => {", j)
            if j != -1 and k != -1:
                promises = re.findall(r"loadJSON\('([^']+)'\)",
                                      built[i:j])
                picked = [x.strip() for x in
                          built[j + len(".then((["):k].split(",") if x.strip()]
                check("the offline destructure matches its promise list, in order",
                      promises == picked,
                      f"{len(promises)} loads but {len(picked)} names; "
                      f"anything after the first divergence is off by one")

        # the two big files are fetched on demand, not at boot: 1.4 MB and
        # about 420ms of startup on the build that ships to a phone
        boot_block = built[i:j] if i != -1 else ""
        check("bbc_6min.json is not loaded at boot",
              "bbc_6min" not in boot_block,
              "~1 MB for a panel most users never open")
        check("word_arch.json is not loaded at boot",
              "word_arch" not in boot_block,
              "~450 KB, only needed by the Sentences panel's word chips")

        leftovers = sorted(set(re.findall(r"fetch\(\s*['\"]/api/[^'\"]+", built)))
        check("no server calls survive in the offline page", not leftovers,
              ", ".join(leftovers))
    else:
        check("the built page exists", False, "run build_apk_ui.py")

    # ----------------------------------------------------------------------
    if FAILURES:
        print(f"FAIL  {len(FAILURES)} of {CHECKS} UI checks\n")
        for f in FAILURES:
            print(f"  {f}")
        return 1
    print(f"PASS  all {CHECKS} UI checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())