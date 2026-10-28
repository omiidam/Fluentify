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
# ---------------------------------------------------------------- sections --
    # This used to be deferred on purpose: 450 KB of word chips that nobody
    # sees until the Sentences panel opens, so fetching them at boot looked
    # like waste. With the loading screen held for five seconds, deferring
    # saves nothing the user is waiting on and leaves that panel feeling
    # broken on first open. The word index is read during boot now; the
    # open-panel hook below stays as the fallback for a read that failed.
    #
    # The list inside loadAllSections is the boot's entire value. A section
    # dropped from it goes back to loading on first tap, and nothing else
    # would say so - the app would still open, just slower to be usable.
    boot_sections = re.search(r"async function loadAllSections\(\)\s*\{([\s\S]*?)\n\}", src)
    boot_body = boot_sections.group(1) if boot_sections else ""
    for fn, why in (("loadVocabulary", "Vocabulary"),
                    ("loadGrammar", "Grammar"),
                    ("loadPhrases", "Sentences"),
                    ("loadListening", "Listening"),
                    ("loadPhonetics", "Sounds"),
                    ("loadWordArch", "the word index behind the chips"),
                    ("bbcDoc", "the audio catalogue")):
        check(f"{why} is read during boot",
              boot_sections is not None and fn in boot_body,
              f"{fn} is missing from loadAllSections(), so that section is "
              "back to loading on first tap")
    check("the boot reports progress rather than spinning blindly",
          "Boot.step(" in boot_body and "Boot.step(0," in boot_body,
          "a bar that never moves is worse than the bouncing tile, because "
          "it looks like a stall")
    check("one unreadable section does not abandon the rest of the boot",
          re.search(r"try \{ await run\(\); \} catch", boot_body) is not None,
          "Promise.all rejects on the first failure, so one missing file "
          "leaves every later section unbuilt")

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
          "no playable audio" in bbc,
          "an honest count has to explain the difference")
    # BBC's transcript PDFs are not dependable from the WebView, so the list
    # must not offer a control that opens one. The grade still comes from the
    # transcript; only its dead download link is gone.
    check("the bbc list does not offer transcript downloads",
          "transcript_url" not in bbc and "Transcript" not in bbc,
          "a transcript button that opens a retired PDF reads as a broken app")

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

    # ------------------------------------------------------------ the flock --
    # The backdrop lived behind .app, which is 58-72% opaque and blurs
    # whatever is behind it - so on a phone, where .app is full-bleed, none of
    # it could be seen. The birds have to be a child of .app to show at all.
    check("the bird flock is inside the app frame",
          re.search(r'<div class="app">\s*<div class="flock"', src) is not None,
          "behind .app it is blurred by the glass and hidden on a phone, "
          "which is where it looked like there was nothing to see")
    flock = re.search(r"\n  \.flock \{(.*?)\n  \}", src, re.S)
    fb = re.sub(r"/\*.*?\*/", "", flock.group(1), flags=re.S) if flock else ""
    check("the flock cannot be clicked",
          "pointer-events: none" in fb,
          "a decorative bird that swallows a tap is a bug")
    check("the flock sits behind the conversation",
          re.search(r"z-index:\s*0", fb) is not None,
          "it is a background, not an overlay")
    wm = re.search(r"\.flock i\.wm \{(.*?)\n  \}", src, re.S)
    wb = wm.group(1) if wm else ""
    # The watermark was tuned for navy glass, where 6% white reads as a ghost.
    # The cream theme made it a white bird on white paper: invisible except its
    # dark eye, which sat mid-transcript and looked like a dead pixel. It is off
    # now, and this is what stops a later recovery of the old opacity from
    # bringing the dot back. The geometry checks below still guard the artwork
    # itself, so re-enabling it cannot reintroduce a different bird.
    check("the watermark is switched off on the paper theme",
          re.search(r"display:\s*none", wb) is not None,
          "a white bird on cream shows only its eye, which reads as a dead "
          "pixel in the middle of the conversation")
    check("the watermark still fades out instead of ending at an edge",
          re.search(r"-webkit-mask-image:\s*radial-gradient", src) is not None
          and re.search(r"mask-image:\s*radial-gradient", src) is not None,
          "without the radial mask it is a pale sticker on the conversation")

    # One bird. The six drifting ones read as clutter behind a transcript.
    flock_html = re.search(r'<div class="flock"[^>]*>(.*?)</div>', src, re.S)
    check("there is exactly one background bird",
          flock_html is not None
          and len(re.findall(r"<i\b", flock_html.group(1))) == 1,
          "a flock behind a conversation is clutter, not ambience")

    # The watermark is the icon, so its geometry has to be the icon's. Matching
    # on the crest and tail paths rather than on the whole SVG: those two are
    # what make the shape read as this bird rather than a generic one, and they
    # are the parts a hand-drawn replacement would quietly lose.
    # Every path in the watermark must exist in the mascot. Testing for the
    # crest with a plain substring passed while the watermark was missing it,
    # because the icon itself carries the same string - the two only diverge
    # when compared to each other.
    icon = re.search(r"const BIRD =\s*'(.*?)';", src, re.S)
    mark = re.search(r"\.flock i \{.*?url\(\"data:image/svg\+xml,(.*?)\"\) no-repeat", src, re.S)
    # Geometry only - d, cx, cy, rx, ry, r. Comparing d alone let an ellipse
    # be moved to any centre and still pass, which is most of the shape.
    paths = lambda t: set(re.findall(r"(?:d|cx|cy|rx|ry|r)=['\"]([^'\"]+)['\"]", t)) if t else set()
    icon_paths, mark_paths = paths(icon.group(1) if icon else ""), \
                              paths(mark.group(1).replace("%3C", "<").replace("%3E", ">")
                                    if mark else "")
    check("the watermark invents no geometry of its own",
          bool(mark_paths) and mark_paths <= icon_paths,
          f"not in the icon: {sorted(mark_paths - icon_paths)[:2]} - a "
          "hand-drawn replacement drifts into a different bird, which is what "
          "happened when this was a duck")
    # And the other direction. Subset alone passed with the crest deleted,
    # because a smaller set is still a subset; it takes both halves to say the
    # watermark is the icon rather than some of it.
    OUTLINE = ("M10 27 L3.5 20 L5.5 31 Z",             # tail
               "M21.5 13.5 q1-6.5 4.5-6.5",          # crest
               "M36 22.5 L42.5 25.5 L36 28.5 Z")      # beak
    mark_d = set(re.findall(r"d=['\"]([^'\"]+)['\"]", mark.group(1))) if mark else set()
    missing = [d for d in OUTLINE if not any(p.startswith(d) for p in mark_d)]
    check("the watermark keeps the bird's tail, crest and beak",
          not missing,
          f"dropped: {len(missing)} of tail/crest/beak - without them it stops "
          "being this bird")

    check("the flock collapses under prefers-reduced-motion",
          re.search(r"@media \(prefers-reduced-motion: reduce\) \{\s*\.flock i "
                    r"\{ animation: none", src) is not None,
          "six birds drifting forever is exactly what that setting is for")
    # Ambient motion is transform/opacity only, and slow. Scoped to the
    # decorative keyframes by name: a 180ms button bounce may legitimately
    # touch box-shadow, and a rule that flagged those would be a rule nobody
    # could satisfy. Also ignored where the value is 0 or none - a
    # `padding: 0` keyframe step changes nothing.
    AMBIENT = {"drift", "float1", "float2", "float3", "flyAcross",
               "driftBird", "flap"}
    ANIMATED_BAD = ("width", "height", "top", "left", "right", "bottom",
                    "background", "filter", "box-shadow", "margin", "padding")
    for name, body in re.findall(r"@keyframes\s+([\w-]+)\s*\{([\s\S]*?)\n  \}", src):
        if name not in AMBIENT:
            continue
        steps = re.findall(r"[;{]\s*([a-z-]+)\s*:\s*([^;}]+)", body)
        bad = sorted({prop for prop, val in steps
                      if prop in ANIMATED_BAD and val.strip() not in ("0", "0px", "none")})
        check(f"@keyframes {name} animates transform or opacity only",
              not bad,
              f"{', '.join(bad)} re-runs layout or paint on every frame")

        # The duration is on the rule that uses the animation, not inside the
        # keyframes - reading it from the body found nothing and skipped the
        # check entirely.
        secs = [float(x) for x in re.findall(
            rf"animation:\s*{re.escape(name)}\s+([\d.]+)s", src)]
        if secs:
            # min(), not max(): six birds share this keyframe, and taking the
            # slowest let one of them run at 4s without the check noticing.
            slowest = min(secs)
            check(f"@keyframes {name} stays in the ambient band",
                  slowest >= 18,
                  f"a {slowest}s cycle is below the project's 18-30s ambient "
                  "band; under that it reads as movement rather than drift")

    # Opening a panel leaves .chatwrap 0px tall. #chat cannot shrink below
    # its own padding - 20px plus 10px - so without clipping a 30px band of
    # transcript painted straight over the chips row. min-height:0 on #chat
    # does not fix it: a padding box is the floor a box can shrink to.
    wrap = re.search(r"\.chatwrap \{([^}]*)\}", src)
    wb = re.sub(r"/\*.*?\*/", " ", wrap.group(1), flags=re.S) if wrap else ""
    check("the transcript is clipped when a panel squeezes it to nothing",
          re.search(r"overflow:\s*hidden", wb) is not None,
          "opening a panel otherwise paints 30px of conversation across the "
          "chips row; the box cannot shrink below its padding")

    # ------------------------------------------------------------ density --
    # The ask was to make room for the material, not to make it smaller to
    # read. Padding and chrome were cut; type sizes were not, and these hold
    # that line so a later tidy-up cannot quietly undo it.
    # Every declaration in the cascade, not the first one found. .msg is
    # declared twice - 15px on the desktop and again on a phone - and a check
    # that took the first block passed happily when only the phone one was
    # shrunk to 13px, which is the device that actually shows it.
    def declared(sel: str, prop: str) -> list[float]:
        return [float(x) for x in re.findall(
            re.escape(sel) + r"\s*\{[^}]*?" + prop + r":\s*([\d.]+)px", src)]

    msg_fs = declared(".msg", "font-size")
    check("message text stays at 15px or larger everywhere",
          bool(msg_fs) and min(msg_fs) >= 15,
          f"{msg_fs}px: denser layout is not an excuse for smaller type")

    check("the composer reaches 16px on a phone so iOS does not zoom on focus",
          max(declared("#input", "font-size") or [0]) >= 16,
          f"{declared('#input', 'font-size')}px")

    # WCAG 2.5.8 asks for 24x24. The tiles went 44 to 38, which is well past
    # it and is what lets seven of them fit without a scroll strip.
    for sel, label in ((".hbtn", "panel tiles"), (".mic", "microphone")):
        ws, hs = declared(sel, "width"), declared(sel, "height")
        check(f"{label} stay above the WCAG 2.5.8 target minimum",
              bool(ws) and bool(hs) and min(ws) >= 24 and min(hs) >= 24,
              f"smallest declared {min(ws) if ws else '?'}x{min(hs) if hs else '?'}"
              ": below 24px is not a target, it is a guess")

    # The chrome is what was actually too big: 119px of header and 108px of
    # composer left barely two thirds of a phone for the conversation.
    # The send button is an icon button with an explicit box, so it no longer
    # sets the height of the row by min-height. What it must not do is grow:
    # the composer is one line whatever happens inside it.
    send_w, send_h = declared(".send", "width"), declared(".send", "height")
    check("the send button is a fixed square, not a floor for the row",
          bool(send_w) and bool(send_h)
          and max(send_w) <= 44 and max(send_h) <= 44,
          f"{send_w}x{send_h}: when it was 46px tall by min-height it set the "
          "height of the input and the microphone too")


    # -------------------------------------------------------------- borderless --
    # Seven outlined boxes in a row is a rack of buttons, not a toolbar, and
    # the same outline around the mic and the send button made the composer
    # read as three small boxes sitting inside a fourth. The states that used
    # to live on the outline have to be carried by fill and shadow instead, so
    # these checks test both halves of that: no outline, and a state that is
    # still readable without one.
    def border_px(sel: str) -> list[float]:
        """Declared border widths for a selector's own rules, in px.

        Matches the bare selector only: ".hbtn" followed by whitespace and a
        brace, so it picks up the base rule and the narrow-screen one while
        skipping ".hbtn:hover" and ".hbtn i".
        """
        out: list[float] = []
        for block in re.findall(r"(?<![\w.-])" + re.escape(sel) + r"\s*\{([^}]*)\}", src):
            m = re.search(r"(?<!-)\bborder(?:-width)?\s*:\s*([^;]+)", block)
            if not m:
                continue
            for part in m.group(1).split():
                if part in ("none", "0"):
                    out.append(0.0)
                elif part.endswith("px"):
                    out.append(float(part[:-2]))
        return out

    # The theme change moved the toolbar the other way on purpose. On paper a
    # white tile needs its hairline to sit *on* the cream at all; without it
    # the seven buttons float as pale smudges. The composer's own controls stay
    # borderless, because they live inside a container that already has one -
    # that was the original complaint and it still holds. Each is asserted, so
    # neither decision can quietly spread to the other.
    ws = border_px(".hbtn")
    check("the top-bar tiles sit on one hairline",
          bool(ws) and max(ws) <= 1,
          f"{ws}: a white tile with no edge disappears into cream, and a "
          "heavy one turns the toolbar into a rack of boxes")
    for sel, label in ((".mic", "microphone"), (".send", "send button")):
        ws = border_px(sel)
        check(f"the {label} carries no border of its own",
              bool(ws) and max(ws) == 0,
              f"{ws}: three outlined controls inside an outlined composer "
              "read as a box inside a box")

    on = re.search(r"\.hbtn\.on\s*\{([^}]*)\}", src)
    check("the open section button still reads as open without its outline",
          on is not None and "background" in on.group(1)
          and "box-shadow" in on.group(1),
          "the border was doing that job: with no fill and no glow, the open "
          "panel looks exactly like the seven closed ones")

    # The microphone told four states apart with four border colours. Fill
    # alone has to carry them now, so they must differ by hue rather than by
    # a shade of the same blue - which is invisible to anyone who glances at
    # it, and "is it listening?" is exactly what a glance is asking.
    mic_fills: dict[str, str | None] = {}
    for state, pat in (("idle", r"\.mic\s*\{"),
                       ("listening", r"\.mic\.rec\s*\{"),
                       ("unavailable", r"\.mic\[aria-disabled=.true.\]\s*\{")):
        m = re.search(pat + r"([^}]*)\}", src)
        bg = re.search(r"background:\s*(#[0-9a-f]{3,8})", m.group(1)) if m else None
        mic_fills[state] = bg.group(1).lower() if bg else None
    check("the microphone's states differ by colour, not just by brightness",
          all(mic_fills.values()) and len(set(mic_fills.values())) == 3,
          f"{mic_fills}: these were told apart by border colour, which is gone")    # -------------------------------------------------------------- boot --
    # The loader is in the markup rather than added by script: boot reads about
    # a megabyte of JSON, and a script-added overlay lands after the first long
    # frame - the blank screen it was meant to cover.
    check("the boot overlay is in the markup, not injected by script",
          re.search(r"<body>\s*<div class=\"boot\"", src) is not None,
          "injected by script it appears after the first slow frame, which is "
          "the blank screen it exists to hide")
    # Four independent ways down. Any one of them failing still leaves the app
    # usable; all four failing is a blank screen with an animation on it.
    # "the boot finishing" is Boot.ready(), not Boot.hide(): the ordinary path
    # is the sections landing plus the floor having passed, and the overlay is
    # not allowed to go the moment the last read finishes.
    for label, pat in (
        ("the boot finishing", r"Boot\.ready\(\)"),
        ("an uncaught error", r"window\.addEventListener\('error', hide\)"),
        ("a promise rejection", r"window\.addEventListener\('unhandledrejection', hide\)"),
        ("a deadline", r"setTimeout\(hide, CEILING_MS\)"),
    ):
        check(f"the boot screen always comes down on {label}",
              re.search(pat, src) is not None,
              "a loader that cannot be dismissed is worse than no loader")
    check("the boot overlay is removed from the tree, not just faded",
          re.search(r"classList\.add\('gone'\)[\s\S]{0,300}?removeChild\(el\)", src) is not None,
          "left in the tree it stays a full-screen element a later focus can "
          "land on, over a working page")
    # The floor is the requirement: start-up reads about a megabyte of JSON
    # and the loading screen is what covers it, so it is held for five seconds
    # whether the reads take two or twenty. Without the floor a fast machine
    # flashes the loader and the slow one keeps it, which is the one thing a
    # loading screen must not do.
    floor = re.search(r"FLOOR_MS\s*=\s*(\d+)", src)
    check("the boot screen is held for at least five seconds",
          floor is not None and int(floor.group(1)) >= 5000,
          "a boot that returns in 300ms reads as a flicker, not as a load")
    check("the floor is a timer, not a promise",
          re.search(r"setTimeout\(\(\) => \{ floorUp = true; maybe\(\); \}, FLOOR_MS\)", src)
          is not None,
          "awaited instead, one slow section extends the boot by its own time")
    # Three conditions, and the third is the one the learner can see: the bar
    # has to have actually arrived at 100% before the overlay goes, or the
    # screen leaves mid-fill under a label that already said 100%.
    check("the boot waits for the sections as well as the floor",
          re.search(r"function maybe\(\) \{ if \(floorUp && dataIn && shown >= 1\) hide\(\); \}", src)
          is not None,
          "either condition alone dismisses the screen before the app is usable, "
          "and the bar has to finish before the screen does")
    check("the boot deadline is short enough to be useful",
          (lambda m: m is not None and 8000 <= int(m.group(1)) <= 20000)(
              re.search(r"CEILING_MS\s*=\s*(\d+)", src)),
          "boot reads about a megabyte of JSON; much past twenty seconds and "
          "the user is watching a spinner rather than watching it load")
    # The mascot again: the boot bird is a second copy of the same geometry,
    # and a hand-drawn one drifts from the icon exactly as the watermark did.
    icon = re.search(r"const BIRD =\s*'(.*?)';", src, re.S)
    check("the boot bird is the mascot, not a redrawing of it",
          icon is not None and all(d in src for d in (
              "M10 27 L3.5 20 L5.5 31 Z", "M21.5 13.5 q1-6.5 4.5-6.5",
              "M36 22.5 L42.5 25.5 L36 28.5 Z")),
          "crest, tail and beak are the icon's own paths, copied so the boot "
          "bird cannot drift into a different animal")
    # The loader animates on a 0.5s cycle. That is UI feedback, not ambience,
    # so it is exempt from the 18s band - but it still has to be transform-only
    # or it repaints every frame.
    def keyframes_body(name: str) -> str:
        """The whole block, braces balanced.

        A [^}]* capture stops at the first nested "}", which in a keyframe is
        the end of the first step - so a check written that way never saw the
        50% step, where the property it was looking for actually lived.
        """
        start = src.find("@keyframes " + name)
        if start < 0:
            return ""
        i = src.find("{", start)
        depth, j = 0, i
        while j < len(src):
            if src[j] == "{":
                depth += 1
            elif src[j] == "}":
                depth -= 1
                if depth == 0:
                    return src[i + 1:j]
            j += 1
        return ""

    for name in ("bootJump", "bootShadow", "bootBob"):
        body = keyframes_body(name)
        bad = sorted({prop for prop in re.findall(
            r"[;{]\s*([a-z-]+)\s*:", body)
            if prop in ("width", "height", "top", "left", "bottom", "right",
                        "background", "margin", "padding", "filter")})
        check(f"@{name} animates transform only", bool(body) and not bad,
              f"{', '.join(bad)} re-runs layout or paint on every frame")
    check("the boot animation collapses under prefers-reduced-motion",
          re.search(r"@media \(prefers-reduced-motion: reduce\)[\s\S]{0,600}?"
                    r"\.loader::before, \.loader::after \{ animation: none", src) is not None,
          "an endless bounce is what that setting is for")

    # ----------------------------------------------------------- stickers --
    # Content lives in foxes.json, not in code. That is the rule the whole
    # project follows, and a picker with its artwork hardcoded here would break
    # it while looking like the feature works.
    check("the sticker catalogue is a data file, not code",
          re.search(r"loadJSON\('foxes'\)", src) is not None
          and "😀" not in src,
          "adding a sticker must be an edit to foxes.json, never to webapp.py")
    check("the sticker button is wired to the panel it controls",
          re.search(r'id="stickerbtn"[^>]*aria-controls="stickerpanel"', src) is not None
          and re.search(r"id='stickerpanel'|getElementById\('stickerpanel'\)", src) is not None,
          "aria-controls has to point at something that exists")
    # A sticker is a picture, so it travels as a token and is painted back on
    # render: a picker that inserted a token nothing expanded would look for
    # all the world like it worked, right up to the moment the message sent.
    check("the sticker token is expanded when a message is rendered",
          "function stickerize(" in src and "stickerize(escapeHtml(s))" in src,
          "[fox:id] would sit in the bubble as text")
    check("the sticker catalogue is registered before it is drawn",
          "function registerFoxes(" in src and "registerFoxes(data.stickers)" in src,
          "a sticker already in the transcript would never paint")
    check("the picker inserts a token rather than a single character",
          re.search(r"insert\('\[fox:' \+ t\.dataset\.fox \+ '\]'\)", src) is not None,
          "the tile no longer inserts the sticker it shows")
    check("the picker reports its open state",
          re.search(r"els\.btn\.setAttribute\('aria-expanded'", src) is not None,
          "a button that opens something should say whether it is open")
    # Escape and an outside click both have to close it, or on a phone it is
    # a panel in the way with no obvious way out. Every document keydown
    # handler is examined, not just the first: the search field has its own
    # Escape branch, so searching the source for the key anywhere passed even
    # with the document-level handler deleted.
    handlers = re.findall(
        r"document\.addEventListener\('keydown',[\s\S]{0,400}?\n    \}\)", src)
    outside = "els.panel.contains(ev.target)" in src
    check("the picker closes on Escape and on an outside click",
          any("Escape" in h and "close()" in h for h in handlers) and outside,
          "either route alone leaves the other open, and on a phone that is a "
          "panel sitting over the composer with no way out of it")
    check("the picker returns focus to the composer when it closes",
          re.search(r"function close\(\)[\s\S]{0,400}?els\.input\.focus\(\)", src) is not None,
          "focus left on a hidden button is a keyboard trap")
    # The picker used a \w-ish character class to split the query; \w is
    # ASCII-only, so a Farsi search matched nothing. The sticker search
    # compares lowered substrings instead, which is Unicode-correct without a
    # pattern at all - but that is only true if the words in the haystack
    # include the Persian, so both halves are asserted.
    match_fn = next((l for l in src.splitlines() if "const hay = norm(" in l), "")
    check("the sticker search is fed the Persian name and the keywords",
          "s.fa" in match_fn and "s.kw" in match_fn,
          "the Farsi name of each sticker has to be searchable")
    check("the sticker search compares substrings, not a \\w class",
          ".includes(word)" in src,
          "a search that goes through \\w cannot match Persian at all")
    check("every sticker tile carries an accessible name",
          re.search(r"b\.setAttribute\('aria-label', label\)", src) is not None,
          "a grid of unlabelled pictures is a wall of nothing to a screen reader")

    # The catalogue itself. Its SVGs are inserted with innerHTML, so the file is
    # the thing that has to be well-formed: a stray <script> pasted into one
    # entry would be code execution on every page that draws a fox.
    import json as _json
    try:
        foxes = _json.loads((ROOT / "foxes.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        foxes = None
        check("foxes.json is readable", False, str(exc))
    if foxes:
        rows = foxes.get("stickers") or []
        check("the sticker set has enough faces to be a picker", len(rows) >= 8,
              f"only {len(rows)} stickers")
        ids = [r.get("id") for r in rows]
        check("every sticker id is unique", len(set(ids)) == len(ids),
              f"duplicates in {ids}")
        bad_id = [i for i in ids if not re.fullmatch(r"[a-z0-9-]+", str(i))]
        check("every sticker id survives the [fox:id] token", not bad_id,
              f"{bad_id} would never render: the token is [a-z0-9-] only")
        for r in rows:
            where = r.get("id", "?")
            check(f"sticker {where} is complete",
                  bool(r.get("name") and r.get("fa") and r.get("kw") and r.get("svg")),
                  "a sticker without a name, a Persian name, keywords or artwork")
            art = str(r.get("svg") or "")
            check(f"sticker {where} carries only drawing markup",
                  "<script" not in art and "<foreignObject" not in art
                  and not re.search(r"\son[a-z]+\s*=", art)
                  and "href=" not in art,
                  "it is inserted with innerHTML, so a script or an href in "
                  "it would run")
            check(f"sticker {where} stays inside its own box",
                  'viewBox="0 0 64 64"' not in art,
                  "the 64x64 viewBox belongs on the wrapper the page draws")

    # ------------------------------------------------------------- colour --
    # Contrast has to be computed, not eyeballed. The learner bubble was
    # indigo->violet and two of its three stops sat under 4.5:1 against the
    # white 15px text - 4.28 and 3.96 - and had been shipped that way. A
    # check that only asked "is this a hex colour" would have passed it.
    def lum(c: str) -> float:
        c = c.lstrip("#")
        if len(c) == 3:
            c = "".join(x * 2 for x in c)
        ch = [int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        f = lambda v: v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
        return 0.2126 * f(ch[0]) + 0.7152 * f(ch[1]) + 0.0722 * f(ch[2])

    def ratio(a: str, b: str) -> float:
        la, lb = lum(a), lum(b)
        hi, lo = max(la, lb), min(la, lb)
        return (hi + 0.05) / (lo + 0.05)

    # The learner bubble is navy with cream text on the paper theme.
    bubble_text = "#fdf7ea"
    for name in ("user1", "user2", "user3"):
        m = re.search(r"--" + name + r":\s*(#[0-9a-fA-F]{3,6})", src)
        if m:
            check(f"--{name} clears AA against the bubble text",
                  ratio(m.group(1), bubble_text) >= 4.5,
                  f"{m.group(1)} is {ratio(m.group(1), bubble_text):.2f}:1 on "
                  "the bubble text colour, under the 4.5 that 16px body text "
                  "needs")

    # The section accents are text-coloured on the paper base, so they owe it
    # the same 4.5. One is open at a time, but each is still read as text.
    for name in ("teal", "cyan", "violet", "emerald", "amber", "rose"):
        m = re.search(r"--" + name + r":\s*(#[0-9a-fA-F]{3,6})", src)
        if m:
            check(f"--{name} clears AA on the paper base",
                  ratio(m.group(1), "#faf4e8") >= 4.5,
                  f"{m.group(1)} is {ratio(m.group(1), '#faf4e8'):.2f}:1 on "
                  "#faf4e8")

    # The two speakers have to stay separable at a glance. Navy-on-cream made
    # the hue test wrong - both sides share the theme's ink - so what is
    # checked now is the thing the eye actually uses: one bubble is dark and
    # the other is paper.
    m = re.search(r"--user1:\s*(#[0-9a-fA-F]{6})", src)
    if m:
        check("the learner bubble separates from the tutor's paper card",
              ratio(m.group(1), "#fffcf3") >= 3,
              f"{m.group(1)} is {ratio(m.group(1), '#fffcf3'):.2f}:1 against "
              "the tutor card: the two speakers would read alike")

    # ------------------------------------------------------------- player --
    # One bar under the header for everything that makes a sound. The failure
    # it exists to prevent is a six-minute clip that can only be halted by
    # finding the card it came from, where the only control was "pause" -
    # which is not stop, it leaves the position and the download behind.
    check("there is a player bar under the header",
          re.search(r"</header>\s*<div id=\"player\"", src) is not None,
          "it must sit above the chat and the panels, or a panel opened on "
          "top of it would hide the only way to stop the audio")
    for ident, label in (("pltoggle", "Pause"), ("plstop", "Stop")):
        check(f"the player has a {label.lower()} control with an accessible name",
              re.search(r'id="' + ident + r'"[^>]*aria-label="[^"]+"', src) is not None,
              "an unlabelled icon button is a control nobody can find")
    check("the player is hidden until something is playing",
          re.search(r'id="player"[^>]*\bhidden\b', src) is not None,
          "an empty bar sitting above the conversation is furniture")
    check("the player hides when hidden despite being flex",
          re.search(r"\.player\[hidden\]\s*\{\s*display:\s*none", src) is not None,
          "display:flex beats the hidden attribute, so the bar would never "
          "go away")
    check("the seek track is a labelled slider",
          re.search(r'id="plseek"[^>]*role="slider"', src) is not None
          and re.search(r'id="plseek"[^>]*aria-valuenow', src) is not None,
          "a progress bar you cannot operate by keyboard excludes people")
    # One Audio, reused. Per-card players are how two clips end up talking
    # over each other.
    check("there is exactly one audio element in the page",
          len(re.findall(r"new Audio\(\)", src)) == 1,
          f"{len(re.findall(r'new Audio()', src))} of them: two clips can "
          "then play at once, which is what per-card players always did")
    check("BBC cards delegate to the player",
          re.search(r"play\.onclick = \(\) => \{[\s\S]{0,400}?Player\.clip\(", src) is not None,
          "a card with its own audio has no bar to stop it from")
    check("a card that is already playing toggles rather than stops",
          re.search(r"Player\.currentSrc === ep\.audio\) \{ Player\.toggle\(\);", src) is not None,
          "the button reads Play while pressing it wound the audio up")
    # Both directions, or the card and the bar end up disagreeing.
    # Bounded to the handler itself. A {0,220} window reached past the pause
    # listener and found owner(false) in the ended handler, so deleting the
    # pause notify still passed.
    notify = lambda ev, flag: re.search(
        r"addEventListener\('" + ev + r"',[^{]*\{[^}]*clip\.owner\(" + flag + r"\)", src)
    check("the card is told about both play and pause",
          notify("play", "true") is not None and notify("pause", "false") is not None,
          "notified on play only, the card kept reading Pause while the bar "
          "read Resume - two controls, one truth, disagreeing")
    # Most of the page calls Speech.speak directly; without a hook the bar
    # would only ever know about clips it started itself.
    check("the player watches Speech rather than being called",
          re.search(r"Speech\.onchange = sync;", src) is not None
          and re.search(r"emit\(\) \{ if \(this\.onchange\) this\.onchange", src) is not None,
          "otherwise the bar sits blank while a word is being spoken")
    # The catch has to actually clear things. Only checking that a catch
    # existed passed with a catch that re-armed the broken state.
    caught = re.search(
        r"speechSynthesis\.speak\(u\);\s*\}\s*catch \(err\) \{(.*?)\n    \}", src, re.S)
    body = caught.group(1) if caught else ""
    check("a throwing speech engine cannot wedge the playing state",
          bool(caught) and "this.playing = null;" in body and "this.emit();" in body,
          "speak() throws synchronously on a bad utterance; unless the catch "
          "clears playing and emits, Speech.playing stays set for ever and "
          "every later press reads as a stop instead of a start")
    check("the speech scan collapses under prefers-reduced-motion",
          re.search(r"@media \(prefers-reduced-motion: reduce\)[\s\S]*?"
                    r"\.player\.speech \.pltrack i \{ animation: none", src) is not None,
          "a bar sweeping back and forth forever is what that setting is for")

    # ---------------------------------------------------------- bbc mirror --
    # The catalogue listed 1123 episodes of which 5 could be played, which
    # reads as broken rather than as small. It now lists exactly what exists.
    cat = ROOT / "bbc_6min.json"
    if cat.exists():
        import json as _json
        doc = _json.loads(cat.read_text(encoding="utf-8"))
        eps = doc.get("episodes") or []
        mirrored = [e for e in eps if str(e.get("audio", "")).startswith(
            (doc.get("mirrored") or {}).get("public_base", "\x00"))]
        check("every listed episode is one that can actually be played",
              len(mirrored) == len(eps) and eps,
              f"{len(eps) - len(mirrored)} of {len(eps)} point at the BBC "
              "rather than the mirror; the list is meant to be what exists")
        check("the catalogue count matches the episode list",
              doc.get("count") == len(eps),
              "the header number and the list have to agree")
        levels = {e.get("level") for e in eps if e.get("level")}
        check("a short catalogue still spans more than one CEFR level",
              len(levels) >= 3 or len(eps) < 6,
              f"levels present: {sorted(levels)} - ten clips of one band is a "
              "worse listening course than three")

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

    # The suggestion row is gone. It was a fixed strip of eight canned
    # questions that never changed, it cost a whole band of the screen on a
    # phone, and everything it offered is already reachable from the panels
    # or by typing. The check is here so it cannot quietly come back with its
    # CSS and its click handler still attached to a missing element.
    check("there is no suggestion chip row",
          'id="chips"' not in src and "class=\"chip\"" not in src,
          "the hint row was removed; do not bring it back")
    check("nothing still looks for the removed chip row",
          "getElementById('chips')" not in src,
          "a listener bound to a missing element throws and takes the rest of "
          "the boot script with it")
    # .chip or .chips opening a rule, but not .cchip, which belongs to the
    # word panels and is still in use.
    orphan = re.findall(r"\n\s*\.chips?\s*[,{]", src)
    check("no orphaned .chip styling is left behind", not orphan,
          f"{len(orphan)} selector(s) for a row that no longer exists")

    # ------------------------------------------------------------ panels --
    # Every panel in the markup has to be in the CSS that hides it. #dpanel
    # was added to the markup without being added to the display:none rule, so
    # the Today panel simply sat in the flow: 2400px of cards on an 844px
    # phone, leaving #chat sixteen pixels tall. Nothing caught it, because
    # every check looked at the panels the CSS already mentioned.
    # The panels are the ones with a tile, in the order Panels.TILES lists
    # them: that table is what the top bar toggles, so a panel missing from the
    # CSS is a panel that is always on screen. #phpanel and #rpanel lay
    # themselves out with flex, so either display is accepted for the open
    # state; #emojipanel is a dialog with the hidden attribute and is not one
    # of these at all.
    tiles = re.search(r"const TILES = \{(.*?)\};", src, re.S)
    panels = sorted(set(re.findall(r"(\w+panel):\s*'", tiles.group(1)))) if tiles else []
    check("the panel table is where this check can read it", len(panels) >= 6,
          f"found {panels}")
    for btn in (re.findall(r"\w+panel:\s*'(\w+)'", tiles.group(1)) if tiles else []):
        check(f"the {btn} tile exists for its panel",
              f'id="{btn}"' in src,
              "Panel's TILES points at a tile that is not in the markup")

    # Comments count in a manual read and must not count here: the note above
    # this very rule names the two panels it had to be given, and scanning the
    # raw source found them in the comment and called the rule correct.
    css = re.sub(r"/\*.*?\*/", " ", src, flags=re.S)

    def has_display(panel: str, kind: str) -> bool:
        for m in re.finditer(r"([^{}]*)\{\s*display:\s*(block|flex)", css):
            sel = m.group(1)
            if f"#{panel}.open" in sel and m.group(2) == kind:
                return True
        return False

    hidden = []
    for m in re.finditer(r"([^{}]*)\{\s*display:\s*none", css):
        hidden += re.findall(r"#(\w+panel)", m.group(1))
    missing = [p for p in panels if p not in hidden]
    check("every panel in the tile table is hidden until it is opened",
          not missing,
          f"{missing} would sit in the flow, eating the chat the way the "
          "Today panel did")
    unopenable = [p for p in panels
                  if not (has_display(p, "block") or has_display(p, "flex"))]
    check("every panel has an .open rule that shows it", not unopenable,
          f"{unopenable} could never open")

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

        # Every data file is read behind the loading screen, the two big ones
        # included. They used to be fetched on first use instead, on the
        # reasoning that a panel most people never open should not cost every
        # start-up 1.4 MB - which is true and also irrelevant, because the
        # screen is held for five seconds whatever the machine does. Deferring
        # them only moved the wait from start-up to the first tap, and made
        # the progress bar on the loading screen count three of seven.
        boot_block = built[i:j] if i != -1 else ""
        for name, why in (("bbc_6min", "the Listen tab's catalogue"),
                          ("word_arch", "the Sentences panel's word chips")):
            check(f"{name}.json is loaded during the boot",
                  f"loadJSON('{name}')" in boot_block,
                  f"{why} should be read while the loading screen is up, not "
                  f"on the first tap")
        # ...and because the boot holds the screen, it has to reach the same
        # loadAllSections() the web build does. The offline page used to have
        # its own smaller boot that filled five panels and left two empty
        # until they were opened.
        check("the offline boot fills the panels through loadAllSections",
              re.search(r"return loadAllSections\(\);", built) is not None,
              "one boot, one place to look when a section comes back empty")
        check("the offline boot is dismissed through Boot, not a bare timer",
              "Boot.ready()" in built
              and "Boot.hide()" not in (built[j:] if i != -1 and j != -1 else ""),
              "Boot.hide() straight after the reads throws away the five "
              "second floor and the loading screen is a flicker")

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