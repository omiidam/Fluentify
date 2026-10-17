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
    # Centred, so it sits in the quiet middle of the frame rather than in a
    # corner where it used to hide behind the composer.
    check("the watermark bird is centred in the frame",
          re.search(r"left:\s*50%.*?top:\s*50%", wb, re.S) is not None
          and "translate: -50% -50%" in wb,
          "an off-centre watermark ends up behind the composer or the header")
    # The mask is what makes it a watermark rather than a picture. A solid
    # silhouette, however faint, still has an edge for the eye to catch on.
    check("the watermark bird fades out instead of ending at an edge",
          re.search(r"-webkit-mask-image:\s*radial-gradient", src) is not None
          and re.search(r"mask-image:\s*radial-gradient", src) is not None,
          "without the radial mask it is a pale sticker on the conversation")
    size = re.search(r"width:\s*min\(\s*([\d.]+)%", wb)
    opac = re.search(r"opacity:\s*([\d.]+)", wb)
    check("the watermark bird is small and faint enough to read through",
          size is not None and float(size.group(1)) <= 32
          and opac is not None and float(opac.group(1)) <= 0.08,
          "the ask was a watermark: small, and under 8% opaque")

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

    for name in ("user1", "user2", "user3"):
        m = re.search(r"--" + name + r":\s*(#[0-9a-fA-F]{3,6})", src)
        if m:
            check(f"--{name} clears AA against the white bubble text",
                  ratio(m.group(1), "#ffffff") >= 4.5,
                  f"{m.group(1)} is {ratio(m.group(1), '#ffffff'):.2f}:1 on white, "
                  "under the 4.5 that 15px body text needs")

    # The section accents are text-coloured on the navy base, so they owe it
    # the same 4.5. One is open at a time, but each is still read as text.
    for name in ("teal", "cyan", "violet", "emerald", "amber", "rose"):
        m = re.search(r"--" + name + r":\s*(#[0-9a-fA-F]{3,6})", src)
        if m:
            check(f"--{name} clears AA on the base colour",
                  ratio(m.group(1), "#0b102e") >= 4.5,
                  f"{m.group(1)} is {ratio(m.group(1), '#0b102e'):.2f}:1 on "
                  "#0b102e")

    # The learner must not drift back to the chrome's own hue, which is what
    # made both sides of the conversation look alike.
    hues = {}
    for name in ("user1", "user2", "accent"):
        m = re.search(r"--" + name + r":\s*(#[0-9a-fA-F]{6})", src)
        if m:
            c = m.group(1).lstrip("#")
            r, g, b = (int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))
            mx, mn = max(r, g, b), min(r, g, b)
            d = mx - mn
            if d:
                hues[name] = (60 * ((g - b) / d % 6) if mx == r else
                              60 * ((b - r) / d + 2) if mx == g else
                              60 * ((r - g) / d + 4))
    if "user1" in hues and "accent" in hues:
        sep = abs(hues["user1"] - hues["accent"]) % 360
        sep = min(sep, 360 - sep)
        check("the learner's colour is a different hue from the chrome",
              sep >= 30,
              f"{sep:.0f}deg from --accent: too close to read as a different "
              "speaker at a glance")

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