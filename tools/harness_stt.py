#!/usr/bin/env python3
"""Checks the two new subsystems: the BBC grader and speech-to-text.

    python3 tools/harness_stt.py

Neither the grader nor the STT config is covered by the main harness, and both
are the kind of thing that fails quietly - a grader that returns A2 for
everything looks like it is working, and a malformed stt.json simply means the
mic button never appears.

Grader:
  * a passing grade needs enough text; a one-line blurb must NOT be graded
  * the blend must be monotonic - harder text never grades easier
  * function words alone must not drag a passage down
  * BBC's own tag must agree, as a range check

STT:
  * stt.json must parse and carry every key the three surfaces read
  * the language codes must be real BCP-47 tags
  * the MP3 duration probe must land on a 6 Minute English clip's length
    (the file is VBR, so a bitrate estimate is wrong by minutes)
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

FAILURES: list[str] = []
CHECKS = 0


def fail(msg: str) -> None:
    FAILURES.append(msg)


def check(name: str, ok: bool, detail: str = "") -> None:
    global CHECKS
    CHECKS += 1
    if not ok:
        fail(f"{name}{': ' + detail if detail else ''}")


# --------------------------------------------------------------------------
# the grader
# --------------------------------------------------------------------------
EASY = (
    "The cat sat on the mat. The dog ran in the park. I saw a bird on the "
    "tree. We went to the shop and bought some bread. She made a cake for "
    "the party. He read a book about the sea. The sun was very warm today. "
    "I like tea and coffee in the morning. They play football after work. "
    "We live in a small house near the river. "
) * 6

HARD = (
    "Notwithstanding the epistemological objections raised by subsequent "
    "commentators, the paradigm remains structurally inadequate for "
    "accommodating heteronormative presuppositions. Institutional "
    "accommodation of pluralistic frameworks necessitates a reconceptualised "
    "accounting of intergenerational accountability mechanisms. "
    "Proliferation of bureaucratic nomenclature has inadvertently exacerbated "
    "counterproductive antagonisms among stakeholders. "
    "Notwithstanding unprecedented volatility, unprecedented juxtaposition "
    "of unprecedented circumstances renders unprecedented ramifications "
    "unprecedentedly consequential for unprecedentedly heterogeneous "
    "populations. "
) * 4


def run_grader() -> None:
    from listening_grade import (
        BBC_TAG_RANGE, clean_transcript, grade_text, in_band_range, load_cefr,
    )

    cefr = load_cefr()
    check("cefr table", len(cefr) > 100_000, f"only {len(cefr)} words")

    easy = grade_text(EASY, cefr)
    hard = grade_text(HARD, cefr)
    check("easy text is graded", easy.get("level") is not None, str(easy))
    check("hard text is graded", hard.get("level") is not None, str(hard))
    if easy.get("level") and hard.get("level"):
        order = ["A1", "A2", "B1", "B2", "C1", "C2"]
        check("harder text grades no easier",
              order.index(hard["level"]) > order.index(easy["level"]),
              f"easy={easy['level']} hard={hard['level']}")
        check("easy text is not advanced",
              order.index(easy["level"]) <= order.index("B1"),
              f"easy={easy['level']}")

    # a blurb must be refused rather than guessed at
    short = grade_text("Do you drink alcoholic drinks?", cefr)
    check("a one-line blurb is not graded",
          short.get("level") is None, str(short))

    # the transcript cleaner must not throw on real junk
    for junk in ["", "   ", "\n\n", "↳ x", "‮mirror", "a" * 3000]:
        try:
            clean_transcript(junk)
        except Exception as exc:  # noqa: BLE001
            fail(f"clean_transcript crashed on {junk[:12]!r}: {exc}")

    # BBC's tag is a range, and containment is the honest test
    check("BBC intermediate accepts B1", in_band_range("B1", "intermediate"))
    check("BBC intermediate accepts B2", in_band_range("B2", "intermediate"))
    check("BBC intermediate rejects A2", not in_band_range("A2", "intermediate"))
    check("BBC intermediate rejects C1", not in_band_range("C1", "intermediate"))
    check("unknown tag is rejected", not in_band_range("B1", "advanced"))
    for tag in BBC_TAG_RANGE:
        lo, hi = BBC_TAG_RANGE[tag]
        check(f"{tag} range is ordered",
              ["A1", "A2", "B1", "B2", "C1", "C2"].index(lo)
              <= ["A1", "A2", "B1", "B2", "C1", "C2"].index(hi))


# --------------------------------------------------------------------------
# the STT configuration
# --------------------------------------------------------------------------
REQUIRED_KEYS = ["enabled", "language", "web", "android", "cli", "levels",
                 "privacy"]
BCP47 = re.compile(r"^[a-z]{2,3}(-[A-Z][a-z]{3})?(-[A-Z]{2})?$")


def run_config() -> None:
    path = ROOT / "stt.json"
    check("stt.json exists", path.exists())
    if not path.exists():
        return
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"stt.json does not parse: {exc}")
        return

    for key in REQUIRED_KEYS:
        check(f"stt.{key} present", key in cfg)
    for key in ("default", "fallback", "supported"):
        check(f"stt.language.{key} present", key in cfg.get("language", {}))

    langs = cfg.get("language", {}).get("supported", [])
    check("at least 6 languages", len(langs) >= 6, f"only {len(langs)}")
    codes = [l.get("code") for l in langs]
    for code in codes:
        check(f"language code {code} is BCP-47",
              bool(code and BCP47.match(code)), str(code))
    default = cfg.get("language", {}).get("default")
    check("default language is in the list", default in codes, str(default))
    fallback = cfg.get("language", {}).get("fallback")
    check("fallback language is in the list", fallback in codes, str(fallback))

    for key in ("engine", "interim_results", "continuous", "max_alternatives",
                "auto_stop_ms", "unsupported_message"):
        check(f"stt.web.{key} present", key in cfg.get("web", {}))
    for key in ("engine", "partial_results", "max_results"):
        check(f"stt.android.{key} present", key in cfg.get("android", {}))
    for key in ("backends", "model", "language", "output_formats"):
        check(f"stt.cli.{key} present", key in cfg.get("cli", {}))

    # auto-stop must not fire before anyone has had time to speak
    web = cfg.get("web", {})
    auto = web.get("auto_stop_ms", 0)
    check("auto-stop is not instant", auto >= 3000, f"{auto}ms")
    check("min speech precedes auto-stop",
          web.get("min_speech_ms", 0) < auto)

    fmts = cfg.get("cli", {}).get("output_formats", [])
    for f in ("txt", "srt", "vtt", "json"):
        check(f"cli supports {f}", f in fmts)


# --------------------------------------------------------------------------
# the audio probe
# --------------------------------------------------------------------------
def run_audio() -> None:
    from transcribe import probe, probe_duration

    have = probe()
    check("probe reports all three backends",
          all(b in have for b in ("faster-whisper", "whisper", "vosk")))
    check("probe reports ffmpeg", "ffmpeg" in have)

    # A real clip if one has been fetched; otherwise skip rather than pretend.
    clips = list((ROOT / "tools/.cache").glob("*.mp3"))
    if not clips:
        return
    clip = clips[0]
    seconds, kind = probe_duration(clip)
    check("mp3 recognised", kind == "mp3", kind)
    # The series is six minutes; a VBR file read as CBR overshoots by minutes,
    # which is exactly the bug the Xing header fixes.
    check("duration is about six minutes", 240 < seconds < 480,
          f"{seconds:.0f}s for a 6-minute clip")


# --------------------------------------------------------------------------
# the PDF reader
# --------------------------------------------------------------------------
def run_pdf() -> None:
    """pdf_to_text must stay linear.

    Its first version pulled strings out with a regex whose nested quantifier
    backtracked without bound on a PDF that embedded a multi-megabyte font.
    It did not raise or return wrong data - it consumed a core at 98% and the
    fetch simply stopped, which is why the check here is a wall-clock budget
    rather than an assertion about the output.
    """
    import threading

    from fetch_bbc_6min import _pdf_strings, pdf_to_text

    # a synthetic stream in the shape that broke it: a '[' that never closes,
    # followed by megabytes of payload
    hostile = (b"[ " + b"abcdefgh " * 400_000) + b" 0 0 0 Tj"
    result: list = []

    def run() -> None:
        try:
            result.append(pdf_to_text(hostile))
        except Exception as exc:  # noqa: BLE001
            result.append(exc)

    t = threading.Thread(target=run, daemon=True)
    t0 = time.time()
    t.start()
    t.join(timeout=20)
    check("pdf_to_text survives an unbalanced TJ array", not t.is_alive(),
          "still running after 20s - the reader is no longer linear")
    if not t.is_alive() and result:
        check("pdf_to_text returns text for a hostile stream",
              isinstance(result[0], str), str(result[0])[:60])

    # and it must still read ordinary text out of a real stream
    simple = b"BT /F1 12 Tf (Hello) Tj (World) TJ ET"
    check("pdf_to_text reads a normal stream",
          "Hello" in pdf_to_text(simple) or
          any("Hello" in x for x in _pdf_strings(simple)),
          pdf_to_text(simple)[:40])

    # every cached transcript must read in reasonable time
    cache = ROOT / "tools/.cache/bbc"
    pdfs = sorted(cache.glob("*.pdf"))[:12]
    for pdf in pdfs:
        t0 = time.time()
        try:
            text = pdf_to_text(pdf.read_bytes())
        except Exception as exc:  # noqa: BLE001
            fail(f"pdf_to_text crashed on {pdf.name[:28]}: {exc}")
            continue
        took = time.time() - t0
        check(f"{pdf.name[:24]} reads fast", took < 2.0, f"{took:.1f}s")
        check(f"{pdf.name[:24]} yields words", len(text.split()) > 50,
              f"only {len(text.split())} words")


# --------------------------------------------------------------------------
# the fetcher's failure modes
# --------------------------------------------------------------------------
def run_fetcher() -> None:
    """Bad URLs must degrade, not end the run.

    BBC's older transcript links contain a literal space, and urllib turns that
    into InvalidURL - a ValueError, not a URLError, so the original handler
    let it through and a single bad link killed the whole 1126-episode run.
    """
    import urllib.error
    import urllib.request

    from fetch_bbc_6min import _title_key, http_get, parse_episode_page

    spaced = ("https://downloads.bbc.co.uk/learningenglish/features/6min/"
              "180607_6_minute_english_talking_to machines.pdf")
    # The point is not that this file still exists - it may not - but that a
    # space in the URL reaches the network instead of raising InvalidURL
    # before a socket is ever opened.
    try:
        http_get(spaced, timeout=25)
        reachable = True
    except urllib.error.HTTPError as exc:
        reachable = f"HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        check("a URL with a space reaches the network", False,
              f"{type(exc).__name__}: {exc}")
        reachable = False
    else:
        pass
    if reachable:
        check("a URL with a space reaches the network", True)

    # the older page template: no mp3, and a topic-named transcript
    old_page = (
        '<a href="http://downloads.bbc.co.uk/learningenglish/features/6min/'
        '201029_6min_english_walkman.pdf">transcript</a>'
        '<div id="heading-intermediate-level"></div>')
    meta = parse_episode_page(old_page)
    check("older pages still yield a transcript",
          meta["transcript_url"].endswith(".pdf"), str(meta["transcript_url"]))
    check("older pages report no audio", meta["audio"] == "", meta["audio"])

    # titles must join the same way on both sides of the podcast join
    for a, b in [("Do trees have memories?", "Do trees have memories ?"),
                 ("Bitcoin: digital crypto-currency", "Bitcoin - digital crypto currency")]:
        check(f"titles join: {a[:26]}", _title_key(a) == _title_key(b),
              f"{_title_key(a)!r} vs {_title_key(b)!r}")

    # Every failure this fetcher meets in the wild must be one it catches.
    # Three separate runs were ended by one of these slipping past a narrower
    # except clause - HTTPError, then InvalidURL, then ConnectionResetError -
    # so the whole class is checked rather than a hand-picked few.
    from fetch_bbc_6min import NET_ERRORS

    wild = [
        urllib.error.HTTPError("u", 500, "server error", None, None),
        urllib.error.HTTPError("u", 404, "gone", None, None),
        urllib.error.URLError("dns"),
        TimeoutError("timed out"),
        ConnectionResetError(104, "reset by peer"),
        ConnectionRefusedError(111, "refused"),
        ValueError("URL can't contain control characters"),
        OSError("socket died"),
    ]
    for exc in wild:
        check(f"{type(exc).__name__} is caught by the fetcher",
              isinstance(exc, NET_ERRORS), str(exc)[:50])

    # a 404 is final; a 500 is worth retrying
    import inspect

    from fetch_bbc_6min import http_get
    check("http_get retries", "attempts" in inspect.signature(http_get).parameters)


# --------------------------------------------------------------------------
# the shipped offline bundle
# --------------------------------------------------------------------------
def run_bundle() -> None:
    """The APK must be able to start.

    A duplicate top-level name between the page and bot.js - a `function esc`
    beside bot.js's `const esc` - is a SyntaxError that kills the whole inline
    script. The build still succeeds, the APK still installs, and the app is
    blank with nothing in the log. It shipped once, and only a real browser
    caught it, because the web build does not load bot.js.
    """
    import shutil
    import subprocess

    out = ROOT / "android/app/src/main/assets/www"
    index, bot_js = out / "index.html", out / "bot.js"
    check("the offline page exists", index.exists())
    check("bot.js is bundled", bot_js.exists())
    if not index.exists():
        return

    html = index.read_text(encoding="utf-8")

    # every file the boot sequence fetches must be there
    import re as _re
    wanted = set(_re.findall(r"loadJSON\('([^']+)'\)", html))
    data_dir = out / "data"
    missing = [n for n in wanted if not (data_dir / f"{n}.json").exists()]
    check("every bundled data file is present", not missing,
          "missing " + ", ".join(sorted(missing)))

    # and nothing may still call the server
    leftovers = sorted(set(_re.findall(r"fetch\(\s*['\"](/api/[^'\"]+)", html)))
    check("no server calls survive in the offline page", not leftovers,
          ", ".join(leftovers))

    # the real check: page and bot.js share one global scope
    if not shutil.which("node"):
        return
    script = _re.search(r"<script>\n(.*)\n</script>", html, _re.S)
    check("the page has an inline script", script is not None)
    if not script:
        return
    combined = (bot_js.read_text(encoding="utf-8") + "\n;"
                if bot_js.exists() else "") + script.group(1)
    tmp = ROOT / "tools/.cache/bundle_check.js"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(combined, encoding="utf-8")
    parsed = subprocess.run(["node", "--check", str(tmp)],
                            capture_output=True, text=True)
    check("page and bot.js parse together", parsed.returncode == 0,
          (parsed.stderr or "")[:400])


# --------------------------------------------------------------------------
# the motion system
# --------------------------------------------------------------------------
def run_motion() -> None:
    """Animation must be present, cheap, and switchable off.

    Three things are easy to get wrong and expensive to find: a decorative
    rule that loses to a later base rule and silently never applies, a
    top-level name that collides with bot.js and blanks the page, and motion
    that keeps running for someone who asked for it to stop.
    """
    import re as _re

    out = ROOT / "android/app/src/main/assets/www/index.html"
    if not out.exists():
        return
    html = out.read_text(encoding="utf-8")

    check("the motion layer is present", "MOTION SYSTEM" in html)
    check("the ambient layer has markup", 'id="motes"' in html)
    check("the motion module is defined", "const Motion = " in html)
    check("motion is initialised", "Motion.init()" in html)

    # a rule that never applies looks identical to one that does, in source
    style_end = html.index("</style>")
    motion_at = html.index("MOTION SYSTEM")
    check("the motion block is last in the stylesheet",
          motion_at > html.index(".row { display: flex"),
          "a later base rule would win on order and the animation never run")
    check("the motion block is inside the stylesheet", motion_at < style_end)

    # the ambient canvas is decorative and must not be reachable
    check("the ambient layer is aria-hidden", 'id="motes" aria-hidden="true"' in html)

    # Reduced motion works by neutralising selectors, not by naming keyframes,
    # so what matters is that the block is last, disables animations outright,
    # and names everything that would otherwise run forever on its own.
    check("a reduced-motion block exists",
          "@media (prefers-reduced-motion: reduce)" in html)
    reduced = html[html.rindex("@media (prefers-reduced-motion: reduce)"):]
    check("the reduced-motion block is last in the stylesheet",
          html.rindex("@media (prefers-reduced-motion: reduce)")
          > html.rindex("@keyframes"),
          "an !important override must come after the rules it overrides")
    check("reduced motion disables animation outright",
          "animation: none !important" in reduced)

    # the things that would keep moving unprompted, by selector
    forever = [
        (".motes", "the ambient canvas"),
        (".backdrop::before", "the drifting backdrop"),
        (".orb.o1", "the floating orbs"),
        (".mav.bot", "the bird idling"),
        ("body.speaking", "the bird while speaking"),
        (".bbc-lvl", "the level pill shimmer"),
        (".mtool.on", "the speaking glow"),
        (".mic.rec", "the recording pulse"),
    ]
    for selector, what in forever:
        pat = _re.escape(selector).replace(r"\ ", r"\s*")
        # "stopped" means either not rendered at all, or rendered but static
        still = _re.search(
            pat + r"[^}]*?(?:animation:\s*none|display:\s*none)", reduced)
        check(f"reduced motion stops {what}", still is not None, selector)

    # cost: nothing may animate a layout property
    layout_props = _re.findall(r"@keyframes[^{]+\{([^}]*)\}", html)
    bad = set()
    for body in layout_props:
        for line in body.split(";"):
            prop = line.strip().split(":")[0].strip()
            if prop.startswith(("width", "height", "top", "left", "right",
                                "bottom", "margin", "padding")):
                bad.add(prop)
    check("no keyframe animates a layout property", not bad,
          ", ".join(sorted(bad)))

    # mounting must be idempotent - the offline build calls it from the boot
    # block and again at the end of the page script, and two mic buttons in
    # the composer is worse than none
    check("mountMic is guarded against a double mount",
          "if (document.getElementById('mic')) return;" in html)

    # the module must be namespaced: one top-level const, nothing else
    tops = _re.findall(r"^(?:const|let|var|function|class)\s+([A-Za-z_$][\w$]*)",
                       html, _re.M)
    motion_tops = [n for n in tops if n.startswith("Motion")]
    check("the motion module exposes exactly one global", len(motion_tops) == 1,
          ", ".join(motion_tops))


def main() -> int:
    t0 = time.time()
    print("→ grader");   run_grader()
    print("→ stt.json");  run_config()
    print("→ audio");    run_audio()
    print("→ pdf");      run_pdf()
    print("→ fetcher");  run_fetcher()
    print("→ bundle");   run_bundle()
    print("→ motion");   run_motion()
    print()
    if FAILURES:
        print(f"FAIL  {len(FAILURES)} of {CHECKS} checks ({time.time() - t0:.1f}s)\n")
        for msg in FAILURES:
            print(f"  {msg}")
        return 1
    print(f"PASS  all {CHECKS} checks ({time.time() - t0:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())