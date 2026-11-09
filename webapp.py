#!/usr/bin/env python3
"""Web preview for the bilingual chatbot — stdlib only, no dependencies.

Run:  python3 webapp.py   →  http://localhost:8765
"""

import json
import os
import re
import select
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from chatbot import ChatBot

PORT = int(os.environ.get("FLUENTIFY_PORT", "8765"))
# Loopback by default, because this is also the developer's preview. A deployed
# backend sets FLUENTIFY_HOST=0.0.0.0 (behind TLS) so the phone can reach it.
HOST = os.environ.get("FLUENTIFY_HOST", "127.0.0.1")
ROOT = Path(__file__).resolve().parent
STT_FILE = ROOT / "stt.json"
BBC_FILE = ROOT / "bbc_6min.json"


def stt_config() -> dict:
    """Speech-to-text settings, with a usable default if the file is missing.

    Kept as a function rather than a constant so editing stt.json takes effect
    without a restart during development.
    """
    if not STT_FILE.exists():
        return {"enabled": False, "language": {"default": "en-GB"},
                "web": {}, "cli": {}}
    try:
        return json.loads(STT_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"enabled": False, "language": {"default": "en-GB"},
                "web": {}, "cli": {}}


def render_page() -> str:
    """Fill the page template.

    The speech-to-text configuration is inlined rather than fetched: the page
    already has the server-rendered HTML, this costs no round trip, and the
    offline APK build gets the exact same block with no special case.
    """
    cfg = json.dumps(stt_config(), ensure_ascii=False)
    return HTML_TEMPLATE.replace(
        "/*__STT_CONFIG__*/",
        f"window.STT_CONFIG = {cfg};")


def bbc_catalogue() -> dict:
    """The graded BBC catalogue. Links only - the audio stays on BBC's CDN."""
    if not BBC_FILE.exists():
        return {"episodes": [], "count": 0,
                "_readme": "run tools/fetch_bbc_6min.py to build this"}
    try:
        doc = json.loads(BBC_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"episodes": [], "count": 0}
    # Never serve transcript text: it is BBC's copyright, and the page has no
    # transcript download control - the audio and episode links are the offer.
    for ep in doc.get("episodes", []):
        ep.pop("transcript", None)
    doc["count"] = len(doc.get("episodes", []))
    return doc
bot = ChatBot()  # shared session memory for the preview

# ------------------------------------------------------------ local corrector
# GEC-BART Base (gotutiyan/gec-bart-base) runs on the server and nowhere else:
# the weights are a 558 MB BART, the interpreter is .venv/gec, and
# tools/gec_worker.py keeps the model loaded between sentences. Only a Python
# process can host it - the browser and the APK ship JavaScript, and a BART is
# not a JavaScript dependency - so the correction is an endpoint of its own.
# That is also why chat replies are untouched: the model answers a question
# about a sentence, it does not edit the conversation, and the APK keeps the
# rule-based checker it ships with.
sys.path.insert(0, str(ROOT / "tools"))
try:
    import gec as gec_model
except Exception:                    # a partial checkout must not stop the app
    gec_model = None


class LocalGec:
    """One long-lived model process, and the fetch that puts it on disk.

    A server is expected to boot with storage keys and an empty disk: the
    checkpoint lives in ArvanCloud, so the first start pulls it with the key
    this process already holds and never asks a browser or a phone for
    anything. The pull runs in the background so a request that arrives during
    it gets a sentence rather than a timeout; loading the model happens once,
    and every correction after that costs one generation.
    """

    def __init__(self):
        self.proc = None
        self.lock = threading.Lock()
        self.state = "idle"          # idle | installing | ready | failed
        self.error = ""

    def status(self) -> str:
        """A sentence the page can show, not a stack trace."""
        if self.state == "installing":
            return ("The correction model is being installed from storage "
                    "(561 MB) — try again in a minute.")
        return self.error

    def prefetch(self) -> None:
        """Install from object storage at boot when the disk is empty.

        This is what makes a fresh server work with nothing but credentials:
        the weights are not in the repository, not in the APK, and not on the
        machine until this runs. Failure is reported, never raised - a missing
        key must not take the chat down with it.
        """
        if self.state in ("installing", "ready"):
            return
        if gec_model is None:
            self.state = "failed"
            self.error = "The correction model module is missing."
            return
        try:
            cfg = gec_model.load_config()
        except Exception as exc:
            self.state, self.error = "failed", f"The corrector is misconfigured: {exc}"
            return
        if gec_model.weights_present(cfg):
            self.state = "ready"
            return
        self.state = "installing"
        threading.Thread(target=self._install, args=(cfg,), daemon=True).start()

    def _install(self, cfg) -> None:
        try:
            code = gec_model.install(cfg)
            ok = code == 0 and gec_model.weights_present(cfg)
        except Exception as exc:
            ok, self.error = False, f"The correction model could not be installed: {exc}"
        if ok:
            self.state = "ready"
        else:
            self.state = "failed"
            self.error = self.error or (
                "The correction model could not be installed from storage — check "
                "the ARVAN_S3_* keys in .arvan-storage.env on this server.")

    def _start(self):
        if self.proc is not None and self.proc.poll() is None:
            return self.proc
        if gec_model is None:
            raise RuntimeError("The correction model is not installed.")
        cfg = gec_model.load_config()
        python = gec_model.venv_python(cfg)
        if not gec_model.weights_present(cfg):
            if self.state == "idle":
                self.prefetch()         # a request before boot: fetch, then say so
            raise RuntimeError(self.status() or
                               "The correction model is not installed yet — see "
                               "gec.json / tools/gec.py.")
        self.proc = subprocess.Popen(
            [str(python), str(ROOT / "tools" / "gec_worker.py")],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, bufsize=1,
            env={**os.environ, "HF_HUB_OFFLINE": "1"},
        )
        ready, _, _ = select.select([self.proc.stdout], [], [], 180)
        line = self.proc.stdout.readline() if ready else ""
        if '"ready": true' not in line.replace("'", '"'):
            self.proc.kill()
            self.proc = None
            raise RuntimeError("The local correction model did not start.")
        return self.proc

    def correct(self, sentence: str) -> dict:
        text = " ".join((sentence or "").split())
        if not text:
            return {"available": True, "input": "", "output": "", "changed": False,
                    "refused": "Nothing to correct — the sentence is empty."}
        with self.lock:
            try:
                proc = self._start()
            except RuntimeError as exc:
                return {"available": False, "input": text, "output": "",
                        "changed": False, "refused": str(exc)}
            try:
                proc.stdin.write(json.dumps({"sentence": text}) + "\n")
                proc.stdin.flush()
                ready, _, _ = select.select([proc.stdout], [], [], 120)
                line = proc.stdout.readline() if ready else ""
                row = json.loads(line) if line.strip() else {}
            except (OSError, ValueError, subprocess.SubprocessError):
                row = {}
            if not row:
                self.proc = None
                return {"available": False, "input": text, "output": "",
                        "changed": False,
                        "refused": "The local correction model stopped answering."}
        row["available"] = True
        return row


gec = LocalGec()

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fluentify — English &amp; Persian</title>
<meta name="description" content="A bilingual English and Persian tutor: graded vocabulary, grammar, sentence patterns, pronunciation and 1126 BBC listening episodes, with speech-to-text and an offline Android app.">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<!-- The tab icon is the mascot too, from the same brand picture as the header
     and the launcher - so the browser tab does not keep a different animal. -->
<link rel="icon" type="image/png" href="brand/fox-face.png">
<link rel="apple-touch-icon" href="brand/fox-mark.png">
<meta name="theme-color" content="#f7f1e0">
<!-- The theme is decided before the first paint, in the document head, from
     the same key the Account panel writes. Reading it inside the app instead
     meant the boot screen painted light and then flipped: a white flash on a
     dark theme, which is exactly the thing a dark theme exists to avoid. -->
<script>
  (function () {
    var dark = false;
    try {
      var saved = localStorage.getItem('fluentify.theme');
      if (saved === 'dark' || saved === 'light') dark = saved === 'dark';
      else if (window.matchMedia) dark = matchMedia('(prefers-color-scheme: dark)').matches;
    } catch (e) {}
    document.documentElement.dataset.theme = dark ? 'dark' : 'light';
  })();
</script>
<style>
  /* The two faces, vendored next to this file so the offline APK keeps them.
     Latin uses the rounded display face and the handwritten text face; the
     Persian copy falls through to the system Arabic face, because neither
     font has Arabic glyphs and a handwriting face would fight the script. */
  @font-face {
    font-family: 'Baloo2';
    src: url('fonts/baloo2-latin.woff2') format('woff2');
    font-weight: 400 800; font-style: normal; font-display: swap;
    unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6,
      U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC,
      U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
  }
  @font-face {
    font-family: 'Kalam';
    src: url('fonts/kalam-latin.woff2') format('woff2');
    font-weight: 400; font-style: normal; font-display: swap;
    unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6,
      U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC,
      U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
  }
  /* Vazirmatn (rastikerdar/vazirmatn, OFL) is the Persian face of the whole
     app: a modern naskh drawn for screens, with the weights a UI needs and none
     of Nastaliq's depth, which had the Persian lines sitting lower than their
     Latin neighbours and reading as calligraphy where the app wanted plain
     text. One variable file covers 100-900, so bold Persian is bold rather
     than a synthesised smear. The unicode-range keeps it to the Arabic script,
     so Latin stays in Baloo2/Kalam and a mixed line keeps two voices on
     purpose. */
  @font-face {
    font-family: 'Vazirmatn';
    font-style: normal;
    font-weight: 100 900;
    font-display: swap;
    src: url('fonts/vazirmatn.woff2') format('woff2-variations'),
         url('fonts/vazirmatn.woff2') format('woff2');
    unicode-range: U+0600-06FF, U+0750-077F, U+08A0-08FF, U+FB50-FDFF,
      U+FE70-FEFF, U+200C-200D, U+0640;
  }

  :root {
    /* Four colours, taken from the poster this theme is set in: its sand band
       (#EBE2B7), its slate band (#3C405B), the gold of its linework (#E8BF5F)
       and the steel blue of its water (#33526E, #E4ECF3). Everything below is
       one of those four, used in the ratios the poster uses them: slate only
       where something must read as the dark side (the learner's own bubbles,
       the mic, the seed ring), sand for surfaces that should look printed
       rather than white, steel blue where the palette used to have a violet
       chip, gold as ornament - rules, rails, the day's card. */
    --base: #f7f1e0;
    --bg1: #f7f1e0; --bg2: #f2ead6; --bg3: #efe5cd;
    --panel: rgba(20, 26, 50, .9); --panel2: #fffcef;
    --accent: #3c405b; --accent2: #4a4fa0; --accent3: #3f6a8a;
    /* Both greys are darker than the paper first suggests: --muted lands at
       5.3:1 on the blue chips (not just on white) and --dim at 5.0:1 there,
       so the 9-11px counters and timestamps clear AA wherever they sit. */
    --text: #2b3049; --muted: #55607a; --dim: #5b6478;
    --bot: #fffcef;
    --paper: #f7f1e0; --paper2: #efe5cd; --card: #fffcef;
    /* The dark side of the theme is navy now, not the poster's slate:
       deeper and bluer, which is what lets a toolbar icon, a panel rule
       and an open tile all be navy without reading as four greys. */
    --ink: #2b3049; --navy: #22375e; --navy2: #182a4a;
    --gold: #e8bf5f; --gold2: #cf9f3c; --gold-soft: #f7e6bd;
    /* the poster's first band, as a surface rather than an accent */
    --sand: #ebe2b7; --sand2: #ddd2a2;
    /* the poster's water: the cool note the lavender chip used to carry */
    --ice: #e4ecf3; --ice2: #d4e1ed; --ice-ink: #33526e;
    --success: #4a4fa0; --red: #a8493a;
    /* Two scripts, two faces, one stack each: Kalam is the handwritten Latin
       body of the reference, Baloo 2 the rounded Latin display face, and
       Vazirmatn carries every Persian glyph in both, because its unicode-range
       claims the Arabic script and nothing else. Tahoma stays behind it for a
       device that cannot load the file. */
    --font-body: 'Kalam', 'Vazirmatn', 'Segoe Print', 'Comic Sans MS', Tahoma,
      'IranSans', sans-serif;
    --font-fa: 'Vazirmatn', Tahoma, 'IranSans', sans-serif;
    --font-display: 'Baloo2', 'Vazirmatn', 'Trebuchet MS', Tahoma, 'IranSans',
      sans-serif;
    /* The learner's own side, in the poster's slate. One bubble is dark and
       the other is paper, which is the contrast the eye actually uses to tell
       the two speakers apart - and every stop is at least 7.9:1 against the
       15px cream text, well clear of AA. */
    --user1: #3c405b; --user2: #262b44; --user3: #464b69;
    /* accents, one per section. All clear 4.5:1 on --base, and only one
       section is ever open at a time, so they read as a wayfinding key
       rather than a spectrum. */
    --teal: #2a5a7a; --cyan: #14607e; --violet: #4a5580;
    --indigo: #4a4fa0; --amber: #8a5a00; --rose: #a03a63;
    /* the Reading panel's own accent: green, because every other section is
       already using one and a shared colour reads as a shared section */
    --leaf: #2f6b4f; --leaf-soft: #eaf3ec;
    --line: rgba(43,48,73,0.136);
    --line2: rgba(43,48,73,0.238);
    --shadow: 0 40px 100px rgba(74,58,30, .7);

    /* ---- the theme ladder ------------------------------------------------
       Everything above names a colour. Everything from here names a *job*, and
       every job is answered twice: once by this block and once by the dark
       block below it. A surface is a step on a ladder rather than a hex value,
       so "the frame, one step darker than the card" survives a palette change
       - which is the whole reason the dark theme took an afternoon instead of
           a rewrite.

       The steps, lightest first:
         --surf-1  raised cards, bubbles, panels      --surf-4  page tints
         --surf-2  a card's second stop               --surf-5  deep paper
         --surf-3  the page itself                    --surf-6  deepest wash
       In the dark block the same ladder runs the other way: --surf-1 is the
       *highest* surface and therefore the lightest, because elevation in a
       dark theme is shown by lifting a surface towards the light, not by a
       shadow nobody can see. */
    --surf-1: #fffcef; --surf-2: #fdf8ea; --surf-3: #f7f1e0;
    --surf-4: #f5eedb; --surf-5: #efe5cd; --surf-6: #eadfc7;
    --chat-bg: #f8f1de;
    --raise: #ffffff;
    --raise-2: #fffdf8;
    --line-soft: #f0e9d8;
    --line-strong: #cfc1a4;
    --edge-light: rgba(255,255,255,.75);
    /* Translucent white is a surface, so it is a token: 78% white over cream
       reads as a raised card, and the same 78% over #232833 reads as paper
       glued to a dark page - which is exactly what the grammar lesson looked
       like. The dark values are a few percent, which is all a lift needs once
       the surface behind it is already lifted. */
    --lift: rgba(255,255,255,.78);
    --lift-soft: rgba(255,255,255,.55);
    --lift-warm: rgba(255,252,239,.34);
    /* A sheen is a highlight, not a surface, and a highlight only reads in
       proportion to how dark the thing under it is. The same 55% white that
       reads as glass over cream reads as a grey bar slid across graphite. */
    --glint: rgba(255,255,255,.55);
    --glint-soft: rgba(255,255,255,.38);
    /* The tutor's portrait is a cut-out on a transparent file, so the tile
       behind it is the backdrop the picture was drawn against: cream paper.
       The same cream on graphite is a white disc with a fox dropped on it,
       which is the square this token removes - in dark the tile becomes the
       warm graphite the gold accents are already built on. */
    --tile-bot: linear-gradient(150deg, rgba(235,226,183,.95), rgba(221,210,162,.9));
    --tile-bot-edge: rgba(205,159,60,.38);
    /* ink, darkest first. --ink-1 is body copy, --ink-5 is a hint. */
    --ink-1: #2b3049; --ink-2: #3f4a6b; --ink-3: #55607e;
    --ink-4: #7b829c; --ink-5: #666d84;
    --on-fill: #fffcef;
    /* accents, separated into the two jobs a colour can do: --x-ink is text
       and must clear 4.5:1 on its surface, --x-fill is a filled surface and
       must clear it against the text that sits on it. */
    --gold-ink: #8a5a00; --green-ink: #2f6b4f; --red-ink: #a8493a;
    --pink-ink: #a8456a; --purple-ink: #6b6386; --blue-ink: #235c76;
    --navy-ink: #22375e; --indigo-ink: #4a4fa0; --rose-ink: #a03a63;
    --violet-ink: #6b5bd2;
    /* the CEFR bands, as ink and as wash. A band is an identity, so each one
       keeps its own pair instead of borrowing a section accent. */
    --band-a1: #2f8f7a; --band-a2: #2f7d9e; --band-b1: #2f6b4f;
    --band-b2: #9b6a12; --band-c1: #6b5bd2; --band-pre: #a8456a;
    --band-a1-soft: #e6f5ef; --band-a2-soft: #e6f2f7; --band-b1-soft: #e8f3ec;
    --band-b2-soft: #fbf1dc; --band-c1-soft: #eeebfd; --band-pre-soft: #fbe9ef;
    /* The ghost in the composer. Three tokens, because she is white on cream
       here and white on graphite there: the body, the one line drawn round
       her, and the mint she glows in. */
    --ghost-body: #ffffff; --ghost-line: #58c39a; --ghost-ink: #1f7455;
    --ghost-halo: rgba(111, 208, 166, .5);
    --fill-navy: #22375e; --fill-navy2: #182a4a; --fill-navy3: #2f4a78;
    --fill-slate: #3c405b; --fill-slate2: #262b44;
    --fill-red: #a8493a;
    --send-1: #464b69; --send-2: #3c405b;
    --wash-amber: #fbf3e4; --wash-rose: #fbeef2; --wash-ice: #e6f0f7;
    --wash-leaf: #e8f5ea; --wash-violet: #e4e6f8; --wash-slate: #f5eedb;
    --gold-line: #e8bf5f;
    --focus: #3c405b;
    /* masks read alpha, not colour, so this stays black in both themes */
    --mask: #000000;
    /* The primary button's fill. It shares --ink's value in light and must not
       share its *token*: --ink becomes pale text in the dark theme, and a
       button filled with pale text is a button with no label. */
    --btn-fill: #2b3049;
    /* The certificate is a document. It keeps its paper in both themes,
       because it is the one surface whose job is to be printed, and a navy
       sheet with pale type is not a certificate anybody can hand to a school.
       These values are therefore repeated in the dark block on purpose: a
       token that changes with the theme is the wrong tool for a sheet of paper. */
    --doc-paper: #fffdf6; --doc-paper2: #fdf8ea;
    --doc-ink: #2b3049; --doc-ink2: #3f4a6b; --doc-ink3: #55607e;
    --doc-ink4: #7b829c; --doc-gold: #8a5a00; --doc-navy: #22375e;
    color-scheme: light;
  }

  /* ---- the dark block ----------------------------------------------------
     Not an inversion. Three things are deliberately *not* mirrored:

       1. Surfaces are near-black, never black. #000 with cream type is the
          halation complaint - the letters bleed into the field - and a theme
          chosen for tired eyes at 1am should not be the one that glares.
       2. Accents are lifted and desaturated rather than darkened. A navy that
          reads as text on cream is invisible on graphite, so --navy-ink
          becomes a pale blue while --fill-navy stays a filled navy: the same
          family doing two different jobs still does two different jobs.
       3. Shadows are dropped and edges are drawn instead. A 30px black shadow
          on a #12141a field is nothing; a 1px lighter edge is everything, so
          --line and --edge-light do the work the drop shadows do in light. */
  [data-theme="dark"] {
    --base: #12141a;
    --bg1: #12141a; --bg2: #171a21; --bg3: #1b1f27;
    --panel: rgba(10, 12, 18, .92); --panel2: #20242e;
    --text: #e6ebf4; --muted: #a9b2c5; --dim: #8d96a9;
    --bot: #232833;
    --paper: #12141a; --paper2: #1b1f27; --card: #232833;
    --ink: #e9eefa; --navy: #a9c3ec; --navy2: #c3d6f4;
    --gold: #d9b46c; --gold2: #c2a05c; --gold-soft: #3a3221;
    --sand: #2f2c22; --sand2: #3a362a;
    --ice: #22303c; --ice2: #2a3a48; --ice-ink: #9fc7de;
    --success: #a9aef2; --red: #e69a8f;
    --teal: #78b8d8; --cyan: #6ec0dd; --violet: #aab3e2;
    --indigo: #a9aef5; --amber: #e0b56b; --rose: #ee9db6;
    --leaf: #8ed3ab; --leaf-soft: #1b2a20;
    --user1: #334a75; --user2: #2a3c61; --user3: #3a527f;
    --line: rgba(255,255,255,0.10);
    --line2: rgba(255,255,255,0.16);
    /* a shadow in dark mode is a depth cue that costs nothing and shows
       nothing: it is kept only where a floating element needs to sit off the
       page, and tuned to near-black rather than warm brown */
    --shadow: 0 40px 100px rgba(0, 0, 0, .55);

    --surf-1: #252a35; --surf-2: #20242e; --surf-3: #1a1d25;
    --surf-4: #171a21; --surf-5: #14171d; --surf-6: #121419;
    --chat-bg: #0f1116;
    --raise: #2b303c;
    --raise-2: #313744;
    --line-soft: #242a34;
    --line-strong: #3d4451;
    --edge-light: rgba(255,255,255,.07);
    --lift: rgba(255,255,255,.05);
    --lift-soft: rgba(255,255,255,.035);
    --lift-warm: rgba(255,255,255,.025);
    --glint: rgba(255,255,255,.07);
    --glint-soft: rgba(255,255,255,.05);
    --tile-bot: linear-gradient(150deg, var(--gold-soft), var(--sand));
    --tile-bot-edge: rgba(217,180,108,.42);
    --ink-1: #eef2f9; --ink-2: #d6dded; --ink-3: #b3bccf;
    --ink-4: #98a1b5; --ink-5: #8a94a8;
    --on-fill: #fffcef;
    --gold-ink: #e7bd78; --green-ink: #86cfa8; --red-ink: #f1968b;
    --pink-ink: #f2a3c0; --purple-ink: #bdb6da; --blue-ink: #8ecbe4;
    --navy-ink: #a9c3ec; --indigo-ink: #a9aef5; --rose-ink: #ee9db6;
    --violet-ink: #b3a9f0;
    --band-a1: #6fc3a8; --band-a2: #6fb6d4; --band-b1: #86cfa8;
    --band-b2: #dfb268; --band-c1: #b3a9f0; --band-pre: #f2a3c0;
    --band-a1-soft: #17251f; --band-a2-soft: #17242c; --band-b1-soft: #18251d;
    --band-b2-soft: #2a2519; --band-c1-soft: #202338; --band-pre-soft: #2b1e26;
    /* The same ghost, read against graphite: the white is barely off-white so
       it does not glare, and the mint carries the glow on its own. */
    --ghost-body: #f4fffa; --ghost-line: #7ef0c1; --ghost-ink: #3fa882;
    --ghost-halo: rgba(126, 240, 193, .5);
    --fill-navy: #26395c; --fill-navy2: #1e2d4b; --fill-navy3: #30466e;
    --fill-slate: #3b4256; --fill-slate2: #2b3140;
    --fill-red: #8a3f34;
    --send-1: #4a5470; --send-2: #3d4560;
    --wash-amber: #2a2519; --wash-rose: #2b1e26; --wash-ice: #1a2530;
    --wash-leaf: #18251d; --wash-violet: #202338; --wash-slate: #1f232c;
    --gold-line: #d9b46c;
    --focus: #a9c3ec;
    --mask: #000000;
    --btn-fill: #3a4562;
    --doc-paper: #fffdf6; --doc-paper2: #fdf8ea;
    --doc-ink: #2b3049; --doc-ink2: #3f4a6b; --doc-ink3: #55607e;
    --doc-ink4: #7b829c; --doc-gold: #8a5a00; --doc-navy: #22375e;
    color-scheme: dark;
  }
  /* Chrome speaks in the rounded display face; the transcript keeps the
     handwritten one. Mixing the two everywhere made the buttons look like
     notes and the lessons look like buttons. */
  h1, h2, h3, h4, .phead h3, .hbtn span, .gmain, .vbtn, .ftopic, .ltab,
  .vtab, .go, .pclose, .send, .status, .meta, .boot-tag, .boot-meta,
  .pcount, .wd-lab, .wd-pos, .ltext .fa, .gmain .fa {
    font-family: var(--font-display);
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { height: 100%; }
  body {
    font-family: var(--font-body);
    background: var(--bg1);
    color: var(--text);
    display: flex; align-items: center; justify-content: center;
    padding: 18px;
    overflow: hidden;
  }
  /* Layered gradient field — the glass needs colour behind it to refract. */
  /* ---- the backdrop ----------------------------------------------------
     Everything here is a gradient fading to transparent, moving only with
     `transform`. Nothing carries a filter.

     The previous version put `filter: blur(40px) saturate(140%)` on the
     drifting layer. A filter on an animated element is re-rasterised every
     frame, on a full-viewport element - the most expensive thing this page
     could do - and it bought nothing, because radial-gradient stops fading
     to transparent are already soft. Dropping it is the performance fix and
     the reason the colours below can be richer. */
  .backdrop { position: fixed; inset: 0; z-index: 0; overflow: hidden; }

  .backdrop::before {
    content: ''; position: absolute; inset: -18%;
    background: radial-gradient(58% 52% at 12% 4%, rgba(232,191,95,.20), transparent 72%),
      radial-gradient(52% 48% at 90% 2%, rgba(150,175,200,.38), transparent 72%),
      radial-gradient(56% 50% at 84% 96%, rgba(235,226,183,.9), transparent 74%),
      linear-gradient(165deg, var(--surf-2) 0%, var(--surf-3) 55%, var(--surf-3) 100%);
    will-change: transform;
    animation: drift 30s cubic-bezier(.22,1,.36,1) infinite alternate;
  }
  /* translate only: scaling a layer this large makes the compositor
     re-rasterise it too, which is what the filter was concealing. */
  @keyframes drift {
    from { transform: translate3d(-2.5%, -1.5%, 0); }
    to   { transform: translate3d(3%, 2%, 0); }
  }

  /* Light from above the header, so it reads as lit rather than pasted on.
     Static, so it costs nothing. */
  .backdrop::after {
    content: ''; position: absolute; inset: 0 0 auto; height: 46%;
    background: radial-gradient(70% 100% at 50% 0%,
                rgba(232,191,95,.16), transparent 68%);
    pointer-events: none;
  }

  /* Grounds the composer instead of letting the gradient run flat to the edge. */
  .vignette {
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background: radial-gradient(120% 90% at 50% 42%,
                transparent 55%, rgba(120,96,48,.07) 100%);
  }

  /* Grain. Large gradients band visibly on an OLED phone, and the banding is
     what makes a background look cheap. One static tiled SVG turbulence
     costs a small texture and nothing per frame. */
  .grain {
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    opacity: .05; mix-blend-mode: multiply;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3'/%3E%3C/filter%3E%3Crect width='140' height='140' filter='url(%23n)'/%3E%3C/svg%3E");
    background-size: 140px 140px;
  }


  /* ---- the boot screen ----
     Shown on every cold start, before anything else paints. It is in the
     markup rather than added by script on purpose: the boot reads about a
     megabyte of JSON, and a script-added overlay arrives after the first
     long frame - which is the blank screen it was meant to cover.

     The composition is a lit glass card floating over a slow aurora, rather
     than a logo on an empty field. Everything that moves is transform- or
     opacity-only, so the five seconds this is on screen do not compete with
     the JSON reads behind it for the phone's main thread.

     It always goes away. Three ways out, because a loader that cannot be
     dismissed is the one bug worse than no loader at all: the boot finishing,
     a window error, and a deadline that fires whatever happened in between.
  */
  .boot {
    position: fixed; inset: 0; z-index: 9998;
    display: grid; place-items: center;
    overflow: hidden; isolation: isolate;
    padding: max(24px, env(safe-area-inset-top)) 24px
             max(24px, env(safe-area-inset-bottom));
    background: radial-gradient(95% 70% at 50% -10%, var(--surf-1) 0%, transparent 62%),
      radial-gradient(80% 60% at 108% 108%, var(--surf-3) 0%, transparent 58%),
      linear-gradient(158deg, var(--surf-2) 0%, var(--surf-3) 52%, var(--surf-3) 100%);
    transition: opacity .4s cubic-bezier(.22,1,.36,1), visibility .4s;
  }
  .boot.gone { opacity: 0; visibility: hidden; pointer-events: none; }

  /* Static colour, moving light. No filter on an animated layer: a blur here
     is re-rasterised every frame on the one screen that must stay smooth. */
  .boot-aurora { position: absolute; inset: 0; z-index: -1; pointer-events: none; }
  .boot-aurora i {
    position: absolute; display: block;
    width: 62vmax; height: 62vmax; border-radius: 50%;
    background: radial-gradient(circle, rgba(160,58,99,.22) 0%, rgba(160,58,99,0) 68%);
    animation: bootDrift 19s ease-in-out infinite alternate;
  }
  .boot-aurora i:nth-child(1) { top: -34vmax; left: -26vmax; }
  .boot-aurora i:nth-child(2) {
    top: 18vmax; right: -34vmax;
    background: radial-gradient(circle, rgba(110,90,168,.26) 0%, rgba(110,90,168,0) 68%);
    animation-duration: 24s; animation-delay: -7s;
  }
  .boot-aurora i:nth-child(3) {
    bottom: -38vmax; left: 8vmax;
    background: radial-gradient(circle, rgba(79,70,160,.14) 0%, rgba(79,70,160,0) 70%);
    animation-duration: 29s; animation-delay: -13s;
  }
  @keyframes bootDrift {
    0%   { transform: translate3d(-2%, -1%, 0) scale(1); }
    50%  { transform: translate3d(4%, 3%, 0) scale(1.08); }
    100% { transform: translate3d(-1%, 5%, 0) scale(1.03); }
  }

  /* The card is most of the screen on purpose. A loader that is a small badge
     in the middle of a large field reads as a stalled page; one that fills the
     frame, names the section it is on and shows how much is left reads as
     work in progress. 62vh, not 100: the aurora still has edges to show. */
  .boot-in {
    position: relative; width: min(100%, 460px);
    min-height: min(66vh, 620px);
    display: grid; grid-template-rows: auto auto 1fr auto;
    justify-items: center; align-items: center; gap: 14px;
    padding: 30px 26px 20px;
    border-radius: 32px;
    background: linear-gradient(168deg, var(--surf-1), var(--surf-2) 58%, var(--surf-3));
    border: 1px solid rgba(205,159,60,.30);
    box-shadow: 0 40px 90px -28px rgba(74,58,30,.42),
      0 2px 0 var(--edge-light) inset;
    overflow: hidden;
    animation: bootCardIn .72s cubic-bezier(.22,1,.36,1) both;
  }
  /* One slow band of light crosses the card, so the surface is never still
     even while the bar is waiting. Transform only, and behind the content. */
  .boot-in::after {
    content: ""; position: absolute; inset: -40% -10%;
    background: linear-gradient(104deg, transparent 38%,
      var(--glint) 50%, transparent 62%);
    transform: translateX(-70%) rotate(0.001deg);
    animation: bootSweep 6.5s ease-in-out infinite;
    pointer-events: none;
  }
  @keyframes bootSweep {
    0%, 55% { transform: translateX(-70%); opacity: 0; }
    70%     { opacity: .9; }
    100%    { transform: translateX(70%); opacity: 0; }
  }
  .boot-in > * { position: relative; z-index: 1; }
  @keyframes bootCardIn {
    from { opacity: 0; transform: translateY(14px) scale(.975); }
    to   { opacity: 1; transform: none; }
  }

  /* The mark: the mascot inside a slowly turning gradient ring, with a soft
     inner well so the bird reads against the card rather than floating. */
  .boot-mark {
    position: relative; width: 126px; height: 126px;
    display: grid; place-items: center;
  }
  .boot-halo {
    position: absolute; inset: 0; border-radius: 50%;
    background: conic-gradient(from 0deg,
      var(--fill-slate), var(--gold-line), var(--surf-3), var(--fill-slate), var(--gold-ink), var(--fill-slate));
    opacity: .95;
    box-shadow: 0 0 42px rgba(232,191,95,.38), 0 0 80px rgba(60,64,91,.12);
    animation: bootSpin 7s linear infinite;
  }
  .boot-halo::after {
    content: ''; position: absolute; inset: 4px; border-radius: 50%;
    background: radial-gradient(circle at 32% 24%, var(--surf-1), var(--surf-3) 72%);
    box-shadow: 0 1px 0 var(--edge-light) inset;
  }
  @keyframes bootSpin {
    to { transform: rotate(1turn); }
  }
  /* The mascot itself, not a redrawn copy of it: the same cut-out the header
     and the launcher show, standing in the well behind it. The picture brings
     its own transparent background, so it needs no disc and no border - a
     rounded frame around a figure that is already ragged would show as a
     square behind it. The shadow is a drop-shadow for the same reason: it
     follows the silhouette instead of the box the PNG is drawn in. */
  .boot-fox-bob {
    position: relative; z-index: 1; display: grid; place-items: center;
    animation: bootBob 2.8s cubic-bezier(.45,0,.55,1) infinite;
    transform-origin: 50% 62%;
  }
  /* The bob is on the wrapper and the shadow on the picture: a filter on an
     animated element is re-rasterised every frame (see the backdrop's own
     note), and this shadow is a per-pixel blur of a 100px cut-out. 86px of
     picture is 79px of figure inside the well's 100px - the first cut at
     100px put the beret and the tail through the ring. */
  .boot-fox {
    width: 100px; height: 100px; display: block;
    filter: drop-shadow(0 8px 14px rgba(74,58,30,.32));
  }
  @keyframes bootBob {
    0%, 100% { transform: translateY(0) rotate(-1.5deg); }
    50%      { transform: translateY(-6px) rotate(1.5deg); }
  }

  .boot-brand { display: grid; justify-items: center; gap: 5px; text-align: center; }
  .boot-name {
    font-size: 33px; font-weight: 700; letter-spacing: -.7px;
    line-height: 1.05;
    /* The wordmark is a gradient clipped to the letters. It has to be built
       from inks, not from fills: a fill is chosen to sit behind text, so in
       the dark theme the first two stops were a near-black gradient with the
       letters cut out of it - a title made of background. */
    background: linear-gradient(102deg, var(--navy-ink) 8%, var(--purple-ink) 58%, var(--gold2) 96%);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent; color: transparent;
  }
  .boot-tag {
    font-size: 12.5px; letter-spacing: .2px; color: var(--muted);
    line-height: 1.5;
  }
  /* The second line is the meaning of the first, not a second slogan, so it is
     set as one block under it and isolated as Persian: its own punctuation has
     to read right to left even though the line above it is English. */
  .boot-tag em {
    display: block; margin-top: 2px; color: var(--gold-ink); font-style: normal;
    font-family: var(--font-fa); direction: rtl; unicode-bidi: isolate;
    font-size: 12px; line-height: 1.95;
  }

  /* A bouncing tile with its shadow on the floor. The shape is borrowed from
     a well-known loading animation; the colour is the tutor's. Transform
     only, so it stays on the compositor. */
  /* The three things the app does every day, as a preview of the product
     rather than as decoration: a loading screen is the one place a first-time
     reader sees the shape of the app before anything has loaded. */
  .boot-trio {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;
    width: 100%;
  }
  .boot-tile {
    display: grid; justify-items: center; gap: 3px; text-align: center;
    padding: 10px 4px 9px; border-radius: 14px;
    background: var(--surf-1);
    border: 1px solid var(--line);
    box-shadow: 0 1px 0 var(--edge-light) inset;
  }
  .boot-tile svg { width: 17px; height: 17px; color: var(--gold-ink); opacity: .85; }
  .boot-tile b {
    font-size: 10.5px; font-weight: 700; color: var(--navy2);
    letter-spacing: .2px;
  }
  .boot-tile small {
    font-family: var(--font-fa); font-size: 10px; color: var(--muted);
    direction: rtl; line-height: 1.85;
  }
  /* One thing the app actually does, said while the day is being read. The
     section name that used to sit here ("Sentences") repeated the three tiles
     above it and told the reader nothing they could use; a fact about the app
     earns the line instead. */
  .boot-wait { width: 100%; display: grid; gap: 7px; }
  .boot-facts { display: grid; justify-items: center; gap: 1px; min-height: 34px; }
  .boot-fact, .boot-factfa { transition: opacity .45s ease; }
  .boot-fact {
    font-size: 11px; font-weight: 600; color: var(--gold-ink); letter-spacing: .1px;
    text-align: center; line-height: 1.5;
  }
  .boot-factfa {
    font-family: var(--font-fa); font-size: 10.5px; color: var(--muted);
    direction: rtl; line-height: 1.9; text-align: center;
  }
  .boot-facts.swap .boot-fact, .boot-facts.swap .boot-factfa { opacity: 0; }
  .boot-foot {
    width: 100%; display: grid; justify-items: center; gap: 2px;
    padding-top: 6px; border-top: 1px solid rgba(205,159,60,.20);
    font-size: 10.5px; color: var(--muted); text-align: center;
  }
  .boot-foot span {
    font-family: var(--font-fa); font-size: 10.5px; direction: rtl;
    line-height: 1.9; color: var(--gold-ink);
  }
  .boot-loading {
    width: 100%; display: flex; align-items: center; gap: 15px;
    margin-top: 2px;
  }
  .loader {
    width: 26px; height: 26px; position: relative; flex: 0 0 26px;
  }
  .loader::before {
    content: ''; width: 26px; height: 3px;
    background: rgba(60,64,91,.22);
    position: absolute; top: 33px; left: 0;
    border-radius: 50%;
    animation: bootShadow .5s linear infinite;
  }
  .loader::after {
    content: ''; width: 100%; height: 100%;
    background: linear-gradient(140deg, var(--gold-line), var(--gold2));
    position: absolute; top: 0; left: 0;
    border-radius: 4px;
    box-shadow: 0 4px 14px rgba(207,159,60,.35);
    animation: bootJump .5s linear infinite;
  }
  @keyframes bootJump {
    15%  { border-bottom-right-radius: 3px; }
    25%  { transform: translateY(6px) rotate(22.5deg); }
    50%  { transform: translateY(11px) scale(1, .9) rotate(45deg); border-bottom-right-radius: 18px; }
    75%  { transform: translateY(6px) rotate(67.5deg); }
    100% { transform: translateY(0) rotate(90deg); }
  }
  @keyframes bootShadow {
    0%, 100% { transform: scale(1, 1); }
    50%      { transform: scale(1.18, 1); }
  }

  /* The bar counts sections that have actually landed, so it has to be a
     real width rather than an animation on a fixed timeline. Transform
     only, so filling it costs no layout on a phone. */
  .boot-track {
    position: relative; flex: 1 1 auto;
    height: 8px; border-radius: 999px;
    background: var(--line2); overflow: hidden;
    box-shadow: 0 1px 0 var(--line) inset;
  }
  /* A stripe moving inside the filled part, so a bar that is waiting on a slow
     read still looks alive. Kept to the bar's own painted width. */
  .boot-track i::after {
    content: ""; position: absolute; inset: 0;
    background: repeating-linear-gradient(115deg,
      var(--glint-soft) 0 6px, transparent 6px 14px);
    animation: bootStripe 1.1s linear infinite;
  }
  @keyframes bootStripe {
    from { transform: translateX(-14px); }
    to   { transform: translateX(0); }
  }
  /* No transition here: the bar is repainted from the one eased ratio every
     frame (see Boot), and a transition on top of that would put the bar and
     the percentage back on two different clocks. */
  .boot-track i {
    position: relative;
    display: block; width: 100%; height: 100%; border-radius: inherit;
    background: linear-gradient(90deg, var(--fill-slate), var(--gold-ink) 55%, var(--gold-line) 100%);
    box-shadow: 0 0 12px rgba(232,191,95,.55);
    transform: scaleX(0); transform-origin: 0 50%;
  }
  .boot-meta {
    width: 100%; display: flex; justify-content: space-between;
    align-items: baseline; gap: 8px;
    margin-top: -3px;
    font-size: 11.5px; color: var(--muted);
  }
  .boot-meta .boot-left { font-size: 10.5px; color: var(--gold-ink); }
  .boot-meta #bootpct {
    flex: none; color: var(--gold-ink); font-weight: 700;
    font-variant-numeric: tabular-nums;
  }

  @media (prefers-reduced-motion: reduce) {
    .boot { transition: none; }
    .boot-in { animation: none; }
    .boot-in::after { animation: none; opacity: 0; }
    .boot-track i::after { animation: none; }
    .boot-aurora i, .boot-halo { animation: none; }
    .boot-fox-bob { animation: none; }
    .loader::before, .loader::after { animation: none; }
    .boot-track i { transition: none; }
  }

  /* ---- the emoji picker ---- */
  .emoji-panel {
    margin: 0 0 6px;
    border-radius: 16px; overflow: hidden;
    background: var(--surf-1);
    border: 1px solid var(--line);
    box-shadow: 0 18px 44px rgba(74,58,30,.16);
    animation: emojiIn .2s cubic-bezier(.22,1,.36,1);
  }
  .emoji-panel[hidden] { display: none; }
  @keyframes emojiIn {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: none; }
  }
  .esearch {
    width: 100%; border: 0; border-bottom: 1px solid var(--line);
    background: var(--line); color: var(--text);
    padding: 11px 14px; font-size: 14px; font-family: inherit;
    outline: none;
  }
  .esearch::placeholder { color: var(--ink-4); }
  .esearch::-webkit-search-cancel-button { filter: invert(.7); }
  .ebody {
    max-height: 46vh; overflow-y: auto;
    padding: 8px 10px 10px;
    overscroll-behavior: contain;
  }
  .ebody::-webkit-scrollbar { width: 7px; }
  .ebody::-webkit-scrollbar-thumb { background: var(--surf-5); border-radius: 6px; }
  .ehead {
    font-size: 10px; letter-spacing: .09em; text-transform: uppercase;
    color: var(--dim); font-weight: 700;
    padding: 9px 2px 5px; position: sticky; top: -8px;
    background: linear-gradient(180deg, var(--surf-1), var(--surf-2));
  }
  /* Stickers are drawn, not typed, so a tile is a 46px square with the fox at
     34px inside it and room for the tile itself to lift on hover. */
  .stile {
    width: 46px; height: 46px; padding: 0; margin: 2px;
    display: inline-grid; place-items: center; vertical-align: top;
    border: 0; border-radius: 12px; background: transparent; cursor: pointer;
    transition: background .13s, transform .13s cubic-bezier(.22,1,.36,1);
  }
  .stileart { width: 34px; height: 34px; display: block; pointer-events: none; }
  .stile:hover { background: var(--line); transform: scale(1.1); }
  .stile:active { transform: scale(.92); }
  .stile:focus-visible { outline: 2px solid var(--focus); outline-offset: 1px; }
  .eempty { padding: 22px 8px; text-align: center; color: var(--dim); font-size: 13px; }
  /* Touch has no hover, and a tap that only shows a tooltip teaches nothing:
     the tile presses, the sticker goes in. */
  @media (hover: none) {
    .stile:hover { background: transparent; transform: none; }
  }

  /* ---- the watermark ------------------------------------------------------
     The backdrop lived behind .app, which is 58-72% opaque and blurs whatever
     is behind it - so on a phone, where .app is full-bleed, none of it was
     visible at all. Whatever draws here has to be a child of .app to be seen,
     and a child is painted after the backdrop-filter, so it stays crisp.

     One mark, dead centre, and it is the brand picture itself rather than a
     redrawn silhouette of it: two drawings of one mascot drift apart, and did
     when this was a hand-cut copy of the header's bird.

     Three things keep it from interrupting anything. It is small, it is faint,
     and it is masked: the radial gradient dissolves the outline to nothing
     before the edge, so the mark has no hard boundary to catch the eye. A
     solid silhouette, however faint, still has an edge; this one has a falloff.

     The six drifting marks that were here before are gone. Moving shapes at
     13-20% read as clutter behind a transcript, not as ambience.
  */
  .flock {
    position: absolute; inset: 0; z-index: 0; overflow: hidden;
    pointer-events: none; border-radius: inherit;
  }
  .flock i {
    position: absolute; display: block;
    background: url("brand/fox-mark.png") no-repeat center / contain;
    -webkit-mask-image: radial-gradient(closest-side, var(--ink-1) 0%, var(--ink-1) 34%, rgba(74,58,30,.45) 58%, transparent 80%);
    mask-image: radial-gradient(closest-side, var(--ink-1) 0%, var(--ink-1) 34%, rgba(74,58,30,.45) 58%, transparent 80%);
  }
  /* The watermark was a white bird drawn for the navy glass, where 6% white
     read as a ghost. On cream it is invisible except its dark eye, which sat
     in the middle of the transcript looking like a dead pixel. */
  .flock i.wm { display: none; }
  /* The only motion left: a slow swell, so the mark breathes rather than sits.
     transform and opacity only, and slow enough to go unnoticed if you are
     reading. */
  @keyframes breathe {
    from { scale: 1;    rotate: -1.5deg; }
    to   { scale: 1.04; rotate: 1.5deg; }
  }
  @media (prefers-reduced-motion: reduce) {
    .flock i { animation: none; }
  }

  /* ---- the player ------------------------------------------------------
     One bar under the header for everything that makes a sound. It is a
     sibling of the chat, not of any panel, so a clip keeps playing - and
     stays stoppable - when you open a list on top of it.
  */
  .player {
    display: flex; align-items: center; gap: 10px;
    margin: 10px 16px 0; padding: 7px 14px 7px 7px;
    border-radius: 16px;
    background: linear-gradient(180deg, var(--line), var(--line));
    border: 1px solid var(--line);
    box-shadow: inset 0 1px 0 var(--line), 0 10px 28px rgba(74,58,30,.34);
    backdrop-filter: blur(14px) saturate(1.3);
    -webkit-backdrop-filter: blur(14px) saturate(1.3);
    animation: plIn .28s cubic-bezier(.22,1,.36,1);
  }
  /* display:flex would otherwise beat the hidden attribute */
  .player[hidden] { display: none; }
  @keyframes plIn {
    from { opacity: 0; transform: translateY(-8px); }
    to   { opacity: 1; transform: none; }
  }
  .plbtn {
    flex: 0 0 auto; width: 38px; height: 38px; display: grid; place-items: center;
    border-radius: 50%; border: 1px solid var(--line);
    background: linear-gradient(180deg, var(--line2), var(--line));
    color: var(--ink); cursor: pointer; padding: 0;
    transition: transform .16s cubic-bezier(.22,1,.36,1), background .16s;
  }
  .plbtn:hover { background: linear-gradient(180deg, var(--line2), var(--line)); }
  .plbtn:active { transform: scale(.93); }
  .plbtn svg { width: 18px; height: 18px; fill: currentColor; }
  .plbtn:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
  .plbtn.ghost { width: 32px; height: 32px; color: var(--muted); }
  .plbtn.ghost svg { width: 14px; height: 14px; }
  .plbody { flex: 1 1 auto; min-width: 0; }
  .plhead { display: flex; align-items: baseline; gap: 8px; min-width: 0; }
  .plkind {
    flex: 0 0 auto; font-size: 10px; letter-spacing: .09em; text-transform: uppercase;
    color: var(--gold-ink); font-weight: 700;
  }
  .pltitle {
    font-size: 13px; color: var(--ink); white-space: nowrap;
    overflow: hidden; text-overflow: ellipsis; min-width: 0;
  }
  .pltrack {
    position: relative; height: 6px; margin-top: 6px; border-radius: 99px;
    background: var(--line); cursor: pointer;
    touch-action: none; overflow: hidden;
  }
  .pltrack:focus-visible { outline: 2px solid var(--focus); outline-offset: 3px; }
  .pltrack i {
    position: absolute; inset: 0 auto 0 0; width: 0%; border-radius: 99px;
    background: linear-gradient(90deg, var(--fill-slate), var(--fill-slate2));
  }
  /* Speech has no duration to scrub, so the bar breathes instead of lying
     about a position. */
  .player.speech .pltrack i {
    width: 100% !important;
    background: linear-gradient(90deg, transparent, var(--gold2) 40%, var(--gold2) 60%, transparent);
    animation: plScan 2.4s cubic-bezier(.45,0,.55,1) infinite;
  }
  @keyframes plScan {
    0%   { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
  }
  .player.speech .pltrack { cursor: default; }
  .pltime {
    /* was #a9adcf, the old theme's periwinkle: 2.0:1 on the paper bar the
       player now sits on, i.e. the elapsed time was effectively invisible. */
    flex: 0 0 auto; font-size: 12px; color: var(--muted);
    font-variant-numeric: tabular-nums; min-width: 38px; text-align: right;
  }
  @media (max-width: 560px) {
    .player { margin: 8px 10px 0; gap: 8px; padding: 6px 10px 6px 6px; }
    .plbtn { width: 34px; height: 34px; }
    .plbtn.ghost { width: 30px; height: 30px; }
    .pltitle { font-size: 12px; }
  }
  @media (prefers-reduced-motion: reduce) {
    .player { animation: none; }
    .emoji-panel { animation: none; }
    .stile { transition: none; }
    .player.speech .pltrack i { animation: none; opacity: .7; }
    .plbtn { transition: none; }
  }

  .orb {
    position: fixed; border-radius: 50%; pointer-events: none; z-index: 0;
    opacity: .40; will-change: transform;
  }
  /* Paper takes light, not ink: the orbs are the palette's own gold and
     lavender thinned right down, so the page stays warm cream instead of
     blooming violet behind the header the way the old navy-glass orbs did. */
  .orb.o1 { width: 460px; height: 460px; top: -140px; left: -110px;
            background: radial-gradient(circle, rgba(232,191,95,.55) 0%,
                        rgba(232,191,95,.16) 42%, transparent 72%);
            opacity: .30;
            animation: float1 18s cubic-bezier(.22,1,.36,1) infinite alternate; }
  .orb.o2 { width: 380px; height: 380px; bottom: -110px; right: -90px;
            background: radial-gradient(circle, rgba(150,175,200,.75) 0%,
                        rgba(150,175,200,.22) 42%, transparent 72%);
            opacity: .34;
            animation: float2 22s cubic-bezier(.22,1,.36,1) infinite alternate; }
  .orb.o3 { width: 260px; height: 260px; top: 46%; right: 16%;
            background: radial-gradient(circle, rgba(207,159,60,.42) 0%,
                        rgba(207,159,60,.12) 44%, transparent 72%);
            opacity: .22;
            animation: float3 28s cubic-bezier(.22,1,.36,1) infinite alternate-reverse; }
  @keyframes float1 { to { transform: translate(60px, 40px); } }
  @keyframes float2 { to { transform: translate(-50px, -40px); } }
  @keyframes float3 { to { transform: translate(-40px, 30px); } }

  @media (prefers-reduced-motion: reduce) {
    .backdrop::before, .orb.o1, .orb.o2, .orb.o3 { animation: none; }
  }

  /* ---------------------------------------------------- panel shell -------
     One header for every panel: a title, an optional search and a close
     button. Before this each panel had its own h3 and its own idea of how to
     be dismissed. */
  .phead {
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 14px; flex: none;
    /* A section page scrolls; its title and its way out must not scroll with
       the content, or the close button is only reachable by remembering where
       the top was. The band behind it is the panel's own first gradient stop,
       so at rest it is invisible and while scrolled it covers what passes
       under it - no second colour, no hairline drawn when nothing is behind. */
    position: sticky; top: 0; z-index: 5;
    padding-block: 12px;
  }
  .phead::before {
    content: ''; position: absolute; z-index: -1;
    top: -14px; bottom: -14px;
    inset-inline: calc(-1 * var(--secpad, 20px));
    background: var(--surf-1);
  }
  /* The titles are bilingual and can be long. Without min-width: 0 the h3
     refuses to shrink below its content and pushes the close button past the
     edge of the panel on a narrow phone. */
  .phead h3 { min-width: 0; overflow-wrap: anywhere; }
  .phead h3 { flex: 1 1 auto; margin: 0; min-width: 0; }
  .pclose {
    /* The button the thumb gets is 40px. The chip the eye sees is 28px: it is
       the ::before, inset inside it. A panel header is a title and one button,
       and at 40 visible the button read louder than the title and took a sixth
       of a phone's width. Shrinking the box instead shrank the target, so the
       box stays and the paint got smaller. */
    position: relative; flex: 0 0 40px; width: 40px; height: 40px;
    border-radius: 12px; display: grid; place-items: center;
    background: none; border: 0; padding: 0; cursor: pointer;
    color: var(--ice-ink); font-size: 15px; line-height: 1;
  }
  .pclose::before {
    content: ''; position: absolute; inset: 6px; border-radius: 9px;
    background: var(--ice); border: 1px solid rgba(51,82,110,.22);
    transition: background .16s, border-color .16s;
  }
  .pclose:hover { color: var(--on-fill); }
  .pclose:hover::before { background: var(--fill-navy); border-color: var(--navy); }
  .pclose:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
  .pclose:active { transform: scale(.93); }
  .pclose svg { width: 11px; height: 11px; display: block; position: relative; }

  /* the search box every panel now shares */
  .psearch { margin-bottom: 10px; flex: none; }
  .psearch input {
    width: 100%; padding: 8px 13px; border-radius: 12px;
    background: var(--surf-1); border: 1px solid var(--line); color: var(--text);
    font-size: 14px; font-family: inherit; outline: none;
  }
  .psearch input::placeholder { color: var(--ink-4); }
  .psearch input:focus {
    border-color: var(--focus);
    box-shadow: 0 0 0 3px rgba(60,64,91, .18);
  }

  /* the one empty state, used by every panel */
  .pempty {
    padding: 26px 18px; text-align: center; line-height: 1.7;
    color: var(--muted); font-size: 13.5px;
    background: var(--surf-2); border: 1px dashed var(--line2); border-radius: 14px;
  }
  .pempty b { color: var(--ink-1); }

  .pcount {
    flex: none; margin: -2px 2px 10px; font-size: 11.5px; color: var(--muted);
    letter-spacing: .01em;
  }

  /* Grouped runs: the avatar collapses to a thin stem and the speaker name is
     dropped, so a multi-part answer reads as one turn. */
  /* Hide only the portrait, not the avatar box. Hiding the box with visibility
     would hide the stem drawn on it as well, since a pseudo-element cannot be
     more visible than its parent - so the picture fades and the stem stays. */
  .row.grouped .mav { position: relative; }
  .row.grouped .mav > svg, .row.grouped .mav > img { opacity: 0; }
  .row.grouped .mav::before {
    content: ''; position: absolute; left: 50%; top: 15px; bottom: -15px;
    width: 2px; transform: translateX(-50%); border-radius: 1px;
    background: linear-gradient(rgba(207,159,60,.55), rgba(207,159,60,.08));
  }
  .row + .row.grouped { margin-top: -6px; }
  .row.grouped .meta > span:first-child,
  .row.grouped .meta > i { display: none; }
  .row.grouped .meta { justify-content: flex-end; }

  /* A cue that the panels scroll, or they just stop mid-button and read as a
     rendering fault. Painted on the clipping box rather than on :last-child,
     which PanelSearch appends to and so is not stable. */
  #vpanel, #gpanel, #fpanel, #lpanel, #phpanel, #rpanel, #dpanel, #npanel,
  #bpanel, #rdpanel, #stpanel, #lvlpanel, #wqpanel, #prpanel, #acpanel,
  #pathpanel {
    box-shadow: inset 0 -16px 16px -16px rgba(74,58,30,.62);
  }

  /* "Show more" for the 1126-episode BBC list */
  .bbc-more {
    display: block; width: 100%; margin-top: 10px; padding: 11px 14px;
    border-radius: 12px; cursor: pointer; font-family: inherit;
    font-size: 12.5px; color: var(--navy-ink);
    background: rgba(60,64,91,.13); border: 1px solid rgba(60,64,91,.3);
    transition: background .16s, border-color .16s;
  }
  .bbc-more:hover { background: rgba(60,64,91,.22); border-color: var(--focus); }
  .bbc-more:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }

  /* ---- the app is a pane of frosted glass ---- */
  .app {
    position: relative; z-index: 1;
    width: min(1180px, 100%); height: min(94vh, 980px);
    display: flex; flex-direction: column; overflow: hidden;
    border-radius: 26px;
    /* Three stops, and none of them white. A near-white top edge above a warm
       foot is what made the frame glare at the top of every screen; the sheet
       now darkens as it falls, which is how paper actually behaves under a
       lamp and what the eye reads as depth without a single hard line. */
    background: linear-gradient(152deg, var(--surf-1) 0%, var(--surf-2) 42%, var(--surf-3) 100%);
    border: 1px solid rgba(205,159,60,.30);
    box-shadow: 0 30px 70px rgba(74,58,30,.16),
      0 1px 0 var(--raise) inset;
  }
  /* thicker, brighter edge at the bottom = sense of glass depth */
  .app::after {
    content: ''; position: absolute; left: 12%; right: 12%; bottom: 0; height: 3px;
    background: linear-gradient(90deg, transparent, var(--line), transparent);
    pointer-events: none; z-index: 5;
  }

  /* ---------- header ---------- */
  /* frosted header — the .hb layer is oversized + masked so the blur also
   picks up pixels *near* the bar, which is what real frosted glass does */
  header {
    position: relative;
    display: flex; align-items: center; gap: 12px;
    padding: 15px 20px;
    /* The poster's top band, at the scale a header can carry it: the sand is
       the surface, the gold hairline its printed edge. */
    background: linear-gradient(180deg, var(--surf-2) 0%, var(--surf-3) 100%);
    border-bottom: 1px solid rgba(205,159,60,.32);
    box-shadow: 0 1px 0 var(--edge-light) inset,
                0 10px 24px -22px rgba(74,58,30,.9);
    flex: none;
  }
  /* the frosted layer belonged to the glass theme; paper needs no refraction */
  .hb { display: none; }
  /* The portrait sits on the header's own sand rather than in a badge. A ring
     plus a border plus a drop shadow made it look pasted on: three edges for
     one circular picture. What is left is the paper it is printed on. */
  .avatar {
    width: 46px; height: 46px; border-radius: 15px; flex: none;
    background: var(--surf-3);
    border: 0;
    display: grid; place-items: center;
    box-shadow: none;
  }
  .avatar img {
    width: 40px; height: 40px; display: block;
  }
  /* the mascot reacts to the daily seed */
  @keyframes bob { 0%,100% { transform: translateY(0) rotate(0deg); }
                   50% { transform: translateY(-4px) rotate(-4deg); } }
  @keyframes bloom { 0% { transform: scale(1); }
                      35% { transform: scale(1.18) rotate(6deg); }
                      60% { transform: scale(1.06) rotate(-4deg); }
                      100% { transform: scale(1); } }
  .avatar img { animation: bob 1.7s ease-in-out infinite; }
  .avatar.full img { animation: bob .9s ease-in-out infinite; }
  .avatar.bloom { animation: bloom 1.6s ease; }
  .avatar.full {
    background: linear-gradient(150deg, var(--surf-4), var(--surf-6));
    box-shadow: 0 0 0 2px rgba(207,159,60,.5);
  }

  /* daily seed meter */
  #seedmeter {
    position: relative; flex: none; width: 66px; height: 20px; border-radius: 999px;
    background: var(--line); border: 1px solid var(--line);
    overflow: hidden; display: flex; align-items: center; justify-content: flex-end;
  }
  #seedmeter i {
    position: absolute; inset: 0 auto 0 0; border-radius: 999px;
    background: linear-gradient(90deg, var(--gold2), var(--gold-line) 70%, var(--surf-4));
    transition: width .45s cubic-bezier(.34,1.3,.64,1);
  }
  #seedmeter span {
    position: relative; font-size: 10.5px; font-weight: 700; padding: 0 7px;
    color: var(--ink); white-space: nowrap;
  }
  header h1 { font-family: var(--font-display); font-size: 19px;
              letter-spacing: -.2px; font-weight: 700; color: var(--ink); }
  header p { font-size: 11.5px; color: var(--muted); margin-top: 3px;
              white-space: nowrap; letter-spacing: .01em; }
  .spacer { flex: 1; }
  /* A dot and a word. The filled pill competed with the toolbar for
     attention while carrying the least information on the bar. */
  .status {
    display: flex; align-items: center; gap: 6px;
    font-size: 11.5px; color: var(--indigo-ink);
    padding: 4px 2px; font-weight: 600;
  }
  .status i { width: 8px; height: 8px; border-radius: 50%; background: var(--indigo-ink);
              box-shadow: 0 0 8px var(--indigo-ink); animation: pulse 1.6s infinite; display: inline-block; }
  @keyframes pulse { 50% { opacity: .35; } }
  /* Section tiles: icon over a tiny caption. Seven of these fit across a
     phone without scrolling, where the old full-width pills overflowed. */
  /* Borderless on purpose. Seven outlined boxes in a row is a rack of
     buttons, not a toolbar; what separates them is the fill and the space
     between, which is what a toolbar actually is. The states carry
     themselves on background and shadow instead of on a coloured outline. */
  /* A card, not a pill: white paper on cream, one hairline, one soft shadow.
     The emoji these replaced were seven different icons from seven different
     fonts and read as clip art next to the navy wordmark; these are one
     stroke weight drawn in currentColor, so the toolbar looks like one set.
     The states carry themselves on fill and elevation, never on an outline. */
  .hbtn {
    position: relative;
    background: var(--surf-1);
    color: var(--ink);
    border: 1px solid var(--line); border-radius: 13px;
    box-shadow: 0 1px 2px rgba(74,58,30,.07);
    width: 46px; height: 46px; padding: 4px 2px;
    display: inline-flex; flex-direction: column;
    align-items: center; justify-content: center; gap: 3px;
    cursor: pointer; flex: none;
    transition: background .15s, border-color .15s, box-shadow .18s,
                transform .18s cubic-bezier(.22,1,.36,1);
    font-family: inherit;
  }
  .hbtn i {
    font-style: normal; line-height: 0;
    width: 18px; height: 18px; display: grid; place-items: center;
  }
  .hbtn i svg { width: 18px; height: 18px; display: block; }
  /* One hue per section, the same hue that section's panel header carries, so
     the toolbar works as a colour key: thirteen grey glyphs said nothing about
     where you were going, and the paper theme had almost no colour above the
     fold. The label stays muted; only the icon speaks. */
  .hbtn.tint-teal   i { color: var(--teal); }
  .hbtn.tint-cyan   i { color: var(--cyan); }
  .hbtn.tint-violet i { color: var(--violet); }
  .hbtn.tint-indigo i { color: var(--indigo); }
  .hbtn.tint-amber  i { color: var(--amber); }
  .hbtn.tint-rose   i { color: var(--rose); }
  .hbtn.tint-leaf   i { color: var(--leaf); }
  .hbtn.tint-navy   i { color: var(--navy); }
  /* The theme tile is about the app rather than the lesson, so its icon is the
     one that stays muted: it is a utility sitting at the end of the strip. */
  .hbtn.tint-slate  i { color: var(--muted); }
  .hbtn span {
    font-size: 8.5px; font-weight: 700; letter-spacing: -.05px;
    line-height: 1; color: var(--muted); max-width: 100%;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }
  .hbtn:hover {
    background: var(--surf-2); border-color: rgba(205,159,60,.42);
    transform: translateY(-1px);
    box-shadow: 0 6px 14px rgba(74,58,30,.12);
  }
  .hbtn.on {
    background: linear-gradient(150deg, var(--fill-navy3), var(--fill-navy) 60%, var(--fill-navy2));
    border-color: transparent;
    box-shadow: 0 6px 16px rgba(34,55,94,.30), inset 0 1px 0 var(--edge-light);
  }
  .hbtn.on i, .hbtn.on span { color: var(--on-fill); }
  .hbtn.on i svg { stroke-width: 1.85; }
  .hbtn:focus-visible {
    outline: 2px solid var(--navy);
    outline-offset: 2px;
    box-shadow: 0 0 0 4px rgba(232,191,95,.45);
  }
  .hbtn.danger { color: var(--red); }
  .hbtn.danger:hover {
    border-color: rgba(168,73,58,.45);
    background: var(--surf-2);
  }

  /* ---------- vocabulary / grammar / phrases panels ----------
     Every panel is here, and every panel must be: #dpanel and #npanel were
     added to the markup without being added to this rule, so they had no
     display:none at all and simply sat in the flow. The Today panel is 2400px
     of cards on an 844px phone, which left #chat sixteen pixels tall - the
     daily feature did not sit beside the conversation, it was the page.
     tools/check_ui.py now derives the list from the markup and fails on any
     panel that is missing here. */
  /* A section is a page, not a band above the chat. These used to be flex
     children capped at 52% of the window and parked above the transcript -
     which is why every section looked confined to the top half of the screen
     with a strip of conversation under it. Now an open panel takes the whole
     column between the header and the bottom of the shell, and the transcript
     and the composer step aside (see `.app.section` below). One rule here, so
     no panel can drift back to a half-screen height of its own. */
  #vpanel, #gpanel, #fpanel, #lpanel, #phpanel, #rpanel, #dpanel, #npanel,
  #bpanel, #rdpanel, #stpanel, #lvlpanel, #wqpanel, #prpanel, #acpanel,
  #pathpanel {
    display: none; padding: 14px var(--secpad) 30px;
    /* The page gutter, named once: the header band has to reach exactly the
       panel's edges, and a second copy of this number was two pixels wider on
       a phone - enough to make the whole page scroll sideways. */
    --secpad: clamp(16px, 3.2vw, 34px);
    background: linear-gradient(180deg, var(--surf-1) 0%, var(--surf-2) 55%, var(--surf-2) 100%);
    box-shadow: inset 0 1px 0 var(--raise);
    border-bottom: 1px solid var(--line);
    flex: 1 1 auto; min-height: 0; animation: fade .18s ease;
    max-height: none; overflow-y: auto; overscroll-behavior: contain;
    -webkit-overflow-scrolling: touch;
    /* No bottom mask: it existed to say "this band scrolls", and on a page
       that is the whole column the fade would shade the last row of real
       content instead of a sliver of it. */
    -webkit-mask-image: none; mask-image: none;
  }
  #vpanel.open, #gpanel.open, #fpanel.open, #lpanel.open,
  #dpanel.open, #npanel.open, #bpanel.open, #stpanel.open,
  #lvlpanel.open, #wqpanel.open, #prpanel.open, #pathpanel.open { display: block; }
  #rdpanel.open { display: block; max-height: none; overflow-y: auto; }
  /* The transcript and the composer belong to the conversation, not to a
     section page. Opening a section is a change of destination, so they are
     not squeezed to nothing beside it - they leave the room. Closing the
     section brings both back exactly as they were. */
  .app.section .chatwrap,
  .app.section .stt-panel,
  .app.section #composer { display: none; }
  /* #phpanel gets its own flex layout below, so it is not listed here */
  @keyframes fade { from { opacity: 0; transform: translateY(-4px); } }
  /* A section's title is the page's title now, not a label on a band: at
     13px it named a strip of the screen, and on a full page that reads as a
     caption someone forgot to finish. */
  #vpanel h3, #gpanel h3, #fpanel h3, #lpanel h3, #phpanel h3, #rpanel h3,
  #bpanel h3, #rdpanel h3, #stpanel h3, #lvlpanel h3, #wqpanel h3,
  #prpanel h3, #acpanel h3, #dpanel h3, #npanel h3, #pathpanel h3 {
    font-size: 19px; color: var(--ink); margin-bottom: 4px; font-weight: 700;
    font-family: var(--font-display); letter-spacing: -.2px; line-height: 1.28;
  }
  /* A coloured rule per section. Only one panel is ever open, so this is a
     wayfinding cue rather than a palette to look at - it tells you where you
     are before you have read a word. */
  #dpanel h3  { border-inline-start: 3px solid var(--amber);   padding-inline-start: 9px; }
  #npanel h3  { border-inline-start: 3px solid var(--violet);  padding-inline-start: 9px; }
  #vpanel h3  { border-inline-start: 3px solid var(--teal);    padding-inline-start: 9px; }
  #gpanel h3  { border-inline-start: 3px solid var(--violet);  padding-inline-start: 9px; }
  #fpanel h3  { border-inline-start: 3px solid var(--rose);    padding-inline-start: 9px; }
  #lpanel h3  { border-inline-start: 3px solid var(--cyan);    padding-inline-start: 9px; }
  #phpanel h3 { border-inline-start: 3px solid var(--indigo); padding-inline-start: 9px; }
  #bpanel h3 { border-inline-start: 3px solid var(--navy);   padding-inline-start: 9px; }
  #rpanel h3  { border-inline-start: 3px solid var(--amber);   padding-inline-start: 9px; }
  #rdpanel h3 { border-inline-start: 3px solid var(--leaf);    padding-inline-start: 9px; }
  #stpanel h3 { border-inline-start: 3px solid var(--violet);  padding-inline-start: 9px; }
  #lvlpanel h3 { border-inline-start: 3px solid var(--indigo); padding-inline-start: 9px; }
  #acpanel h3 { border-inline-start: 3px solid var(--amber);  padding-inline-start: 9px; }
  #pathpanel h3 { border-inline-start: 3px solid var(--leaf); padding-inline-start: 9px; }
  /* Account is the tallest panel: a name, three rows, the password-named
     certificate field, two settings and three actions. At 70% the actions fell
     below the box and were clipped, not merely scrolled - the one thing on the
     panel you cannot use if you do not know it is there. 88% plus a bottom pad
     clears the mask fade, and the actions now sit above the two blocks that
     can scroll. */
  #acpanel.open {
    display: block; overflow-y: auto; padding-bottom: 30px;
    /* The offsets that used to keep a share of the chat and the composer
       visible are gone with the chat: the account page owns the column now. */
    max-height: none;
  }

  /* ---------- sign in: the first thing after the loading screen -----------
     It sits under the boot overlay (9998) and over everything else, so the
     loader finishes in front of it and the page is ready behind it: the first
     thing a returning reader does is not watching a spinner. */
  .auth {
    position: fixed; inset: 0; z-index: 9990;
    /* Flex with margin:auto on the card, not grid centring: a centred grid
       item taller than the viewport is clipped at the top and its first field
       cannot be scrolled to. Auto margins collapse to zero instead, so the
       card starts at the top edge and scrolls on a short phone. */
    display: flex; flex-direction: column; padding: 18px;
    overflow-y: auto;
    /* Two washes and a base, the same construction as the app behind it, so
       the gate looks like the room it opens into rather than a modal pasted
       over it. */
    background: radial-gradient(70% 50% at 18% 0%, rgba(34,55,94,.10) 0%, transparent 62%),
      radial-gradient(60% 45% at 100% 100%, rgba(232,191,95,.30) 0%, transparent 60%),
      linear-gradient(158deg, var(--surf-2) 0%, var(--surf-3) 55%, var(--surf-4) 100%);
  }
  .auth[hidden] { display: none; }
  .authcard {
    /* flex: none, or the column flex parent shrinks the card below its own
       content and `overflow: hidden` then clips the submit button off the
       bottom of the gate on a short viewport. The gate scrolls instead. */
    flex: none;
    width: min(100%, 432px); margin: auto;
    background: linear-gradient(180deg, var(--surf-1) 0%, var(--surf-2) 62%, var(--surf-2) 100%);
    border: 1px solid var(--line); border-radius: 22px;
    box-shadow: 0 30px 70px -38px var(--line), 0 1px 0 var(--edge-light) inset;
    overflow: hidden;
    backdrop-filter: blur(8px);
  }
  /* The hero is the card's one dark surface. Navy at the top and cream below
     gives the gate a header instead of a wall of fields, and it is the same
     navy the open section tile and every panel heading already use. */
  .authhero {
    position: relative; display: flex; align-items: center; gap: 12px;
    padding: 16px 18px 15px;
    background: radial-gradient(120% 130% at 88% -30%, rgba(232,191,95,.34) 0%, transparent 58%),
      linear-gradient(150deg, var(--fill-navy3) 0%, var(--fill-navy) 55%, var(--fill-navy2) 100%);
    color: var(--on-fill);
  }
  .authhero::after {
    content: ''; position: absolute; inset: auto 0 0 0; height: 3px;
    background: linear-gradient(90deg, var(--gold-line), rgba(232,191,95,0), var(--gold2));
  }
  .authbadge {
    width: 50px; height: 50px; flex: none; border-radius: 16px;
    display: grid; place-items: center;
    background: linear-gradient(160deg, var(--surf-1), var(--surf-3));
    box-shadow: 0 6px 16px -8px rgba(0,0,0,.6), inset 0 0 0 1px var(--edge-light);
  }
  .authbadge img { width: 42px; height: 42px; display: block; }
  .authhero-t b {
    display: block; font-family: var(--font-display); font-size: 19px;
    letter-spacing: .2px; line-height: 1.15;
  }
  .authhero-t span {
    display: block; font-size: 10.5px; line-height: 1.55; margin-top: 3px;
    color: rgba(255,253,245,.82);
  }
  .authbody { padding: 16px 18px 14px; }
  .authh {
    font-family: var(--font-display); font-size: 20px; color: var(--ink);
    margin: 0 0 3px; letter-spacing: -.1px;
  }
  .authsub { font-size: 12px; line-height: 1.55; color: var(--ink-3); margin: 0 0 12px; }
  .authtabs {
    display: grid; grid-template-columns: 1fr 1fr; gap: 4px; padding: 3px;
    background: var(--line); border-radius: 12px; margin-bottom: 13px;
  }
  .authtab {
    font: inherit; font-size: 12px; font-weight: 700; cursor: pointer;
    border: 0; border-radius: 9px; padding: 8px 6px; color: var(--navy-ink);
    background: transparent; transition: background .15s, color .15s, box-shadow .15s;
  }
  .authtab:hover { color: var(--ink); }
  .authtab.on {
    background: linear-gradient(180deg, var(--surf-1), var(--surf-2)); color: var(--navy);
    box-shadow: 0 2px 8px -4px var(--line), inset 0 0 0 1px var(--line);
  }
  .authtab[disabled] { opacity: .45; cursor: not-allowed; }
  .authfield { display: block; margin-bottom: 8px; }
  /* The display rule above beats the browser's [hidden] default, so the
     sign-in card was still as tall as the sign-up card: two fields were
     invisible but still taking up their space. */
  .authfield[hidden], .authmeter[hidden] { display: none; }
  .authfield > span:first-child {
    display: block; font-size: 10.5px; font-weight: 700; color: var(--navy-ink);
    margin-bottom: 4px; letter-spacing: .02em;
  }
  .authfield input {
    width: 100%; font: inherit; font-size: 13.5px; padding: 10px 12px;
    border-radius: 12px; border: 1px solid var(--line2);
    background: linear-gradient(180deg, var(--raise), var(--surf-1));
    color: var(--ink); box-shadow: inset 0 1px 2px var(--line);
  }
  .authfield input::placeholder { color: var(--ink-5); }
  .authfield input:focus-visible {
    outline: 2px solid rgba(34,55,94,.55); outline-offset: 1px;
    border-color: rgba(34,55,94,.45);
  }
  .authfield .hint { display: block; font-size: 10px; color: var(--ink-5); margin-top: 3px; }
  /* The reveal button sits inside the field's own box, so the field is still
     one control rather than an input plus a stranger beside it. */
  .authwrap { position: relative; display: block; }
  .authwrap input { padding-inline-end: 62px; }
  .authreveal {
    position: absolute; inset-inline-end: 6px; top: 50%; transform: translateY(-50%);
    font: inherit; font-size: 10.5px; font-weight: 700; cursor: pointer;
    padding: 5px 8px; border-radius: 8px; border: 1px solid var(--line);
    background: var(--raise); color: var(--ice-ink);
  }
  .authreveal:hover { background: var(--ice); }
  .authreveal[aria-pressed="true"] { background: var(--ice); border-color: rgba(51,82,110,.35); }
  /* Strength: four segments rather than a percentage bar, because the score is
     a band, not a measurement, and a bar that fills to 87% pretends otherwise. */
  .authmeter { margin: 2px 0 9px; }
  .authtrack { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; }
  .authtrack i {
    height: 4px; border-radius: 999px; background: var(--line2);
    transition: background .2s;
  }
  .authmeter[data-score="1"] .authtrack i:nth-child(-n+1) { background: var(--fill-red); }
  .authmeter[data-score="2"] .authtrack i:nth-child(-n+2) { background: var(--gold2); }
  .authmeter[data-score="3"] .authtrack i:nth-child(-n+3) { background: var(--fill-navy3); }
  .authmeter[data-score="4"] .authtrack i { background: linear-gradient(90deg, var(--green-ink), var(--fill-navy)); }
  .authlabel {
    display: block; margin-top: 5px; font-size: 10px; line-height: 1.6; color: var(--ink-4);
  }
  .authlabel b { color: var(--ink-3); }
  .authlabel .fa { display: block; }
  /* The rule, spelled out. A meter that says "weak" without naming what is
     missing makes the learner guess at four constraints; four lines that tick
     as they are met do not. */
  .authrules { list-style: none; margin: 6px 0 0; padding: 0; }
  .authrule {
    display: flex; align-items: flex-start; gap: 6px;
    font-size: 10px; line-height: 1.5; color: var(--ink-4);
    transition: color .15s;
  }
  .authrule i {
    flex: none; width: 11px; height: 11px; margin-top: 1px; border-radius: 50%;
    border: 1px solid var(--line-strong); font-style: normal; font-size: 8px;
    line-height: 10px; text-align: center; color: transparent;
    transition: background .15s, border-color .15s;
  }
  .authrule.on { color: var(--ink-2); }
  .authrule.on i {
    background: var(--green-ink); border-color: var(--green-ink); color: var(--surf-1);
  }
  .authrule-fa {
    margin: 5px 0 0; font-size: 10px; line-height: 1.6; color: var(--ink-5);
    direction: rtl; text-align: right;
  }
  /* A password has to be typed. Selection is off in the field so the text
     cannot be swept and copied, and the event blockers in Auth.bind() stop
     paste, cut, drag and the context menu. */
  .authfield input[data-secret] {
    -webkit-user-select: none; user-select: none;
    -webkit-touch-callout: none;
  }
  .autherr {
    font-size: 11.5px; line-height: 1.5; color: var(--pink-ink); min-height: 16px;
    margin: 2px 0 6px;
  }
  .autherr.ok { color: var(--green-ink); }
  /* Recovery, kept to the card the learner is already looking at: no second
     modal, no back button into a different screen. The link sits under the
     button where "I cannot get in" is the thought that is forming. */
  .authlink {
    display: block; width: 100%; margin: 9px 0 0; padding: 4px;
    font: inherit; font-size: 11px; font-weight: 600; cursor: pointer;
    background: none; border: 0; color: var(--ice-ink); text-decoration: underline;
    text-underline-offset: 3px; text-decoration-thickness: 1px;
    text-decoration-color: var(--line2);
  }
  .authlink:hover { color: var(--navy-ink); text-decoration-color: var(--ink-4); }
  .authback {
    display: block; width: 100%; margin: 8px 0 0; padding: 9px 12px;
    font: inherit; font-size: 11.5px; font-weight: 600; cursor: pointer;
    border-radius: 11px; border: 1px solid var(--line2);
    background: var(--raise); color: var(--ink-2);
  }
  .authback:hover { background: var(--surf-3); }
  .authreset[hidden] { display: none; }
  .authreset .authh { margin-bottom: 4px; }
  .authsubmit {
    width: 100%; font: inherit; font-size: 13.5px; font-weight: 700; cursor: pointer;
    padding: 12px 14px; border-radius: 13px; border: 1px solid rgba(24,42,74,.5);
    background: radial-gradient(120% 130% at 12% -20%, rgba(232,191,95,.35) 0%, transparent 55%),
      linear-gradient(150deg, var(--fill-navy3), var(--fill-navy) 60%, var(--fill-navy2));
    color: var(--on-fill); display: flex; align-items: center; justify-content: center; gap: 8px;
    box-shadow: 0 10px 22px -14px rgba(24,42,74,.9), inset 0 1px 0 var(--edge-light);
    transition: transform .14s, box-shadow .18s, filter .18s;
  }
  .authsubmit:hover { transform: translateY(-1px); filter: brightness(1.06); }
  .authsubmit:active { transform: translateY(0); }
  .authsubmit[disabled] { opacity: .6; cursor: wait; transform: none; }
  .authfoot {
    margin: 11px 0 0; text-align: center; font-size: 10px; color: var(--ink-5);
  }
  .authfoot .fa { unicode-bidi: plaintext; }
  .authlink {
    font: inherit; font-size: 10.5px; background: none; border: 0; padding: 0;
    color: var(--violet-ink); cursor: pointer; text-decoration: underline;
    text-underline-offset: 2px;
  }
  .authexpired {
    display: flex; gap: 8px; align-items: flex-start; margin-bottom: 11px;
    padding: 9px 11px; border-radius: 11px; font-size: 11.5px; line-height: 1.5;
    background: var(--surf-2); border: 1px solid rgba(155,106,18,.24); color: var(--gold-ink);
  }
  .authexpired[hidden] { display: none; }

  /* The account panel keeps the small grey note the gate used to carry. */
  .authnote {
    margin-top: 11px; padding-top: 10px; border-top: 1px solid var(--line);
    font-size: 10.5px; line-height: 1.55; color: var(--ink-4);
  }
  .authnote b { color: var(--ink-3); }

  /* ---------- the account panel ----------------------------------------- */
  .ac-name {
    font-family: var(--font-display); font-size: 16px; color: var(--ink);
    margin: 0 0 2px; line-height: 1.3;
  }
  .ac-user { font-size: 11.5px; color: var(--purple-ink); margin: 0 0 10px; }
  .ac-rows { display: grid; gap: 6px; margin-bottom: 12px; }
  .ac-row {
    display: flex; justify-content: space-between; gap: 10px; font-size: 11.5px;
    padding: 7px 10px; border-radius: 10px; background: var(--surf-1);
    border: 1px solid var(--line); color: var(--ink-3);
  }
  .ac-row b { color: var(--ink); font-weight: 600; }
  .ac-actions { display: flex; flex-wrap: wrap; gap: 7px; }
  .ac-danger {
    font: inherit; font-size: 11.5px; cursor: pointer; padding: 8px 12px;
    border-radius: 10px; border: 1px solid rgba(168,69,106,.35);
    background: var(--surf-1); color: var(--pink-ink);
  }

  /* The panel is a profile now, and a profile is read before it is edited:
     who you are and what you have done at the top, then the things that change
     something - face, password, appearance - then the two doors out. */
  .ac-hero {
    display: flex; align-items: center; gap: 11px; padding: 11px 12px;
    border-radius: 14px; margin-bottom: 9px;
    background: linear-gradient(150deg, var(--surf-1), var(--surf-3));
    border: 1px solid var(--line);
  }
  .ac-face {
    width: 54px; height: 54px; border-radius: 17px; flex: none;
    display: grid; place-items: center; cursor: pointer;
    background: radial-gradient(circle at 32% 24%, var(--surf-1) 0%,
                var(--season-wash, rgba(232,191,95,.22)) 62%, var(--surf-3) 100%);
    border: 1px solid var(--season-ring, var(--gold-line));
    box-shadow: inset 0 1px 0 var(--raise), 0 6px 16px -12px rgba(0,0,0,.6);
  }
  .ac-face svg { width: 42px; height: 42px; display: block; }
  .ac-heroid { min-width: 0; }
  .ac-heroid .ac-name { margin-bottom: 1px; }
  .ac-heroid .ac-user { margin: 0 0 2px; }
  .ac-mail {
    display: block; font-size: 10.5px; color: var(--ink-4);
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }
  /* Four numbers, one hairline grid: time studied, today, the run of days, and
     the level the last assessment reported. */
  .ac-stats {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px;
    background: var(--line); border: 1px solid var(--line);
    border-radius: 12px; overflow: hidden;
  }
  .ac-stat { background: var(--surf-1); padding: 8px 3px 7px; text-align: center; }
  .ac-stat b {
    display: block; font-family: var(--font-display); font-size: 13.5px;
    line-height: 1.15; color: var(--ink);
  }
  .ac-stat span { display: block; font-size: 8.5px; color: var(--ink-4); line-height: 1.3; }
  .ac-stat span .fa { display: block; }
  /* The last seven days as bars: the numbers above say how much, this says how
     regularly - which is the part a streak is trying to teach. */
  .ac-week {
    display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; align-items: end;
    height: 46px; padding: 8px 10px 5px; margin: 7px 0 10px;
    border-radius: 12px; background: var(--surf-1); border: 1px solid var(--line);
  }
  .ac-bar {
    display: flex; flex-direction: column; justify-content: flex-end;
    align-items: center; gap: 3px; height: 100%;
  }
  .ac-bar i {
    display: block; width: 100%; max-width: 18px; min-height: 3px;
    border-radius: 3px 3px 2px 2px; background: var(--line2);
  }
  .ac-bar.on i { background: linear-gradient(180deg, var(--gold), var(--gold2)); }
  .ac-bar span {
    font-size: 7px; letter-spacing: .04em; text-transform: uppercase;
    color: var(--ink-5);
  }
  .ac-bar.on span { color: var(--ink-3); }
  .ac-block { margin: 0 0 11px; }
  .ac-blockh {
    display: flex; justify-content: space-between; align-items: baseline;
    gap: 8px; margin-bottom: 6px;
  }
  .ac-blockh b {
    font-family: var(--font-display); font-size: 11.5px; font-weight: 700;
    color: var(--ink-2);
  }
  .ac-blockh small { font-size: 9.5px; color: var(--ink-4); }
  .ac-avatars { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }
  .ac-av {
    font: inherit; cursor: pointer; display: grid; justify-items: center;
    gap: 2px; padding: 7px 4px 6px; border-radius: 12px;
    background: var(--surf-1); border: 1px solid var(--line);
    color: var(--ink-4); transition: border-color .15s, background .15s;
  }
  .ac-av svg { width: 34px; height: 34px; display: block; }
  .ac-av b { font-size: 9.5px; font-weight: 600; color: var(--ink-3); }
  .ac-av i { font-style: normal; font-size: 9px; }
  .ac-av:hover { border-color: var(--line2); }
  .ac-av.on {
    background: var(--raise); border-color: var(--focus);
    box-shadow: 0 5px 14px -10px rgba(0,0,0,.6);
  }
  .ac-av.on b { color: var(--ink); }
  .ac-badges { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
  .ac-badge {
    display: grid; grid-template-columns: 22px 1fr; gap: 7px; align-items: start;
    padding: 8px 9px; border-radius: 12px;
    background: var(--surf-1); border: 1px solid var(--line);
  }
  .ac-badge svg {
    width: 20px; height: 20px; margin-top: 1px; fill: none; stroke: currentColor;
    stroke-width: 1.55; stroke-linecap: round; stroke-linejoin: round;
    color: var(--ink-4);
  }
  .ac-badge b {
    display: block; font-size: 9.5px; font-weight: 600; color: var(--ink-3);
    line-height: 1.3;
  }
  .ac-badge i { display: block; font-style: normal; font-size: 8.5px; color: var(--ink-4); line-height: 1.4; }
  .ac-badge .ac-prog {
    display: block; height: 3px; margin-top: 5px; border-radius: 2px;
    background: var(--line); overflow: hidden;
  }
  .ac-badge .ac-prog i { display: block; height: 100%; background: var(--focus); }
  .ac-badge .ac-pct { display: block; margin-top: 3px; font-size: 8px; color: var(--ink-4); }
  .ac-badge .ac-earned {
    display: inline-block; margin-top: 5px; font-size: 7.5px; letter-spacing: .08em;
    text-transform: uppercase; color: var(--gold);
  }
  .ac-badge.on { background: var(--raise); border-color: var(--focus); }
  .ac-badge.on svg { color: var(--gold); }
  .ac-badge.on b { color: var(--ink); }
  .ac-pass {
    display: grid; gap: 7px; padding: 10px; border-radius: 12px;
    background: var(--surf-2); border: 1px solid var(--line);
  }
  .ac-pass .authfield { margin: 0; }
  .ac-pass .authrules { margin: 0; }
  .ac-passerr { margin: 0; font-size: 10px; line-height: 1.5; color: var(--pink-ink); }
  .ac-passerr[hidden] { display: none; }
  .ac-passerr > div[dir="rtl"] { direction: rtl; }
  .ac-ok { margin: 0; font-size: 10px; line-height: 1.5; color: var(--ink-2); font-weight: 600; }

  /* ---------- the certificate ------------------------------------------- */
  .certwrap {
    position: fixed; inset: 0; z-index: 9995; display: grid;
    grid-template-rows: 1fr auto; gap: 10px; padding: 14px;
    background: rgba(24, 26, 40, .58); backdrop-filter: blur(5px);
    overflow: auto;
  }
  .certwrap[hidden] { display: none; }
  .certsheet {
    width: min(100%, 780px); aspect-ratio: 1.414 / 1; margin: auto;
    background: radial-gradient(120% 90% at 50% -20%, var(--doc-paper) 0%, var(--doc-paper) 55%, var(--doc-paper2) 100%);
    border-radius: 8px; padding: 6px; position: relative;
    box-shadow: 0 30px 70px -38px rgba(0,0,0,.8);
  }
  /* A phone cannot show a landscape sheet at a readable size: at 390px wide the
     ratio leaves 276px of height, and the name, the level, the facts and the
     two signatures need more than that - so the bottom of the page, where the
     signature is, would be the part that fell off. Below this width the sheet
     keeps its margins and grows downwards instead, the way a PDF viewer shows
     a wide page on a narrow screen. The ratio is kept wherever there is room. */
  @media (max-width: 700px) {
    .certsheet { aspect-ratio: auto; }
    .certinner { height: auto; }
  }
  .certinner {
    position: relative; height: 100%; border-radius: 5px;
    border: 1.5px solid rgba(155,106,18,.55);
    padding: 4.2% 5.2%; display: flex; flex-direction: column;
    color: var(--doc-ink); overflow: hidden;
  }
  .certinner::before {
    content: ''; position: absolute; inset: 8px; border: 1px solid rgba(155,106,18,.28);
    border-radius: 3px; pointer-events: none;
  }
  /* The head is a letterhead: the mark and the wordmark at the start of the
     line, the stamp that says what this sheet is at the end of it. The stamp
     used to float in the middle of the page, where it sat on the recipient's
     name and read as a watermark; a seal belongs in the corner of a letter. */
  .certhead { display: flex; align-items: center; gap: 9px; }
  .certhead img { width: 30px; height: 30px; border-radius: 8px; }
  .certword { display: flex; flex-direction: column; gap: 2px; line-height: 1.1; }
  .certword b {
    font-family: var(--font-display); font-size: 14px; letter-spacing: .2px;
    color: var(--doc-gold);
  }
  .certword span {
    font-size: 7px; letter-spacing: .16em; text-transform: uppercase;
    color: var(--doc-ink4);
  }
  .certseal {
    margin-inline-start: auto; width: clamp(34px, 6.4vw, 48px); aspect-ratio: 1;
    border-radius: 50%; border: 1px solid rgba(155,106,18,.45);
    box-shadow: inset 0 0 0 3px var(--doc-paper), inset 0 0 0 4px rgba(155,106,18,.24);
    display: grid; place-content: center; justify-items: center; gap: 1px;
    transform: rotate(-7deg); text-align: center;
  }
  .certseal b {
    font-family: var(--font-display); font-size: clamp(7px, 1.25vw, 9px);
    letter-spacing: .1em; color: var(--doc-gold); line-height: 1;
  }
  .certseal span {
    font-size: clamp(3.6px, .66vw, 5px); letter-spacing: .07em;
    text-transform: uppercase; color: var(--doc-ink4); line-height: 1.25;
  }
  /* The middle is the claim: who, what, and how well. It is centred because
     that is the one line of the page a reader looks for first. */
  .certbody {
    flex: 1; display: flex; flex-direction: column; align-items: center;
    justify-content: center; text-align: center; gap: 4px; padding: 1.2% 0;
  }
  .certkick {
    display: flex; align-items: center; gap: 9px; margin: 0;
    font-size: 8px; letter-spacing: .3em; text-transform: uppercase;
    color: var(--doc-gold);
  }
  .certkick::before, .certkick::after {
    content: ''; width: clamp(12px, 3vw, 24px); height: 1px;
    background: rgba(155,106,18,.45);
  }
  .certname {
    font-family: var(--font-display); font-size: clamp(19px, 4.6vw, 33px);
    line-height: 1.1; color: var(--doc-navy); margin: 0;
    unicode-bidi: plaintext; letter-spacing: -.2px;
  }
  .certlead { font-size: clamp(8.5px, 1.4vw, 11.5px); color: var(--doc-ink3); margin: 0; }
  .certband {
    display: inline-flex; align-items: baseline; gap: 8px; margin: .8% 0;
    padding: .9% 3.2%; border-radius: 999px;
    background: linear-gradient(180deg, rgba(155,106,18,.13), rgba(155,106,18,.06));
    border: 1px solid rgba(155,106,18,.34); color: var(--doc-gold);
  }
  .certband b { font-family: var(--font-display); font-size: clamp(20px, 4.3vw, 31px); line-height: 1; }
  .certband span { font-size: clamp(8px, 1.4vw, 11px); font-weight: 600; }
  .certline {
    font-size: clamp(8.5px, 1.4vw, 11.5px); line-height: 1.5;
    color: var(--doc-ink3); margin: 0; max-width: 88%;
  }
  .certfa {
    font-family: var(--font-fa); direction: rtl; font-size: clamp(9px, 1.55vw, 12px);
    line-height: 1.8; color: var(--doc-ink3); margin: 0;
  }
  /* The facts are a ruled row rather than a sentence: three items, each with
     its label above the value, divided by hairlines. */
  .certfacts {
    display: grid; grid-template-columns: 1fr 1.15fr 1.3fr;
    border-top: 1px solid rgba(155,106,18,.22); padding-top: 1.5%;
    margin: 1.5% 0 1.3%;
  }
  .certfacts > div {
    padding-inline: 3%; min-width: 0;
    border-inline-start: 1px solid rgba(155,106,18,.14);
  }
  .certfacts > div:first-child { padding-inline-start: 0; border-inline-start: 0; }
  .certfacts > div:last-child { padding-inline-end: 0; }
  .certfacts dt {
    font-size: 6.2px; letter-spacing: .14em; text-transform: uppercase;
    color: var(--doc-ink4); margin: 0 0 2px;
  }
  .certfacts dd {
    margin: 0; font-size: clamp(7.5px, 1.28vw, 10px); font-weight: 600;
    color: var(--doc-ink2); white-space: nowrap; overflow: hidden;
    text-overflow: ellipsis;
  }
  /* The foot is what makes the sheet a certificate: a hand at the start of the
     line and the name and office at the end of it, with the rule between them
     running under each. */
  .certfoot {
    display: flex; align-items: flex-end; justify-content: space-between;
    gap: 14px; margin-top: auto;
  }
  .certsign {
    display: flex; flex-direction: column; align-items: flex-start; gap: 2px;
    min-width: 0;
  }
  .certwho {
    display: flex; flex-direction: column; align-items: flex-end; gap: 2px;
    min-width: 0; text-align: end;
  }
  /* Kalam is the handwriting face the app already ships, so the signature is
     drawn with a font and not an image: it stays crisp at print size and adds
     nothing to the bundle. */
  .certink {
    font-family: 'Kalam', 'Segoe Script', cursive;
    font-size: clamp(14px, 2.7vw, 21px); line-height: 1;
    color: var(--doc-navy); opacity: .9; white-space: nowrap;
    transform: rotate(-2.2deg); transform-origin: left bottom;
    padding: 0 3px 1px;
  }
  .certsignrule {
    display: block; height: 1px; width: clamp(88px, 20vw, 138px); margin-bottom: 3px;
    background: linear-gradient(90deg, rgba(43,48,73,.42), rgba(43,48,73,.14));
  }
  .certwho .certsignrule {
    background: linear-gradient(270deg, rgba(43,48,73,.42), rgba(43,48,73,.14));
  }
  .certwho b {
    font-family: var(--font-display); font-size: clamp(9px, 1.6vw, 12px);
    color: var(--doc-navy); letter-spacing: .2px; line-height: 1.2;
  }
  .certlab {
    font-size: 6.2px; letter-spacing: .11em; text-transform: uppercase;
    color: var(--doc-ink4); line-height: 1.45;
  }
  .certlab .fa { text-transform: none; letter-spacing: 0; }
  .certbar {
    display: flex; gap: 8px; justify-content: center; align-items: center;
    padding-bottom: max(6px, env(safe-area-inset-bottom));
  }
  .certbar .lv-btn { font-size: 12.5px; }
  .certnote {
    font-size: 7px; line-height: 1.55; color: var(--doc-ink4);
    margin: 1.8% 0 0; text-align: center; align-self: center; max-width: 96%;
  }

  /* Printing the certificate alone: the screen behind it is a page of panels,
     and a PDF of that is not a certificate. */
  @media print {
    @page { size: A4 landscape; margin: 6mm; }
    body > *:not(.certwrap) { display: none !important; }
    .certwrap {
      position: static; display: block; background: var(--doc-paper); padding: 0;
      backdrop-filter: none;
    }
    .certwrap[hidden] { display: none !important; }
    .certsheet {
      width: 100%; height: auto; aspect-ratio: auto; box-shadow: none; margin: 0;
      background: var(--doc-paper);
    }
    .certinner { border-color: var(--gold-line); }
    .certbar { display: none !important; }
    .certwrap, .certsheet, .certinner { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }

  /* ---------- level assessment: rounds, the report, and the practice ------
     The six skills are rows in one profile, so their bands line up and a weak
     one is obvious without reading a number. */
  .lv-sectiontitle {
    font-size: 10.5px; letter-spacing: .12em; text-transform: uppercase;
    font-weight: 700; color: var(--purple-ink); margin: 4px 0 -2px;
  }
  .lv-insight {
    display: grid; gap: 3px; margin-top: 12px; font-size: 11px;
    line-height: 1.55; color: var(--ink-2);
  }
  .lv-insight b { color: var(--ink); font-weight: 700; }
  .lv-skillblock { margin-top: 14px; }
  .lv-caption {
    display: flex; align-items: baseline; justify-content: space-between;
    gap: 10px; padding: 0 2px 2px; font-family: var(--font-display);
    font-size: 13px; font-weight: 700; color: var(--ink);
    border-bottom: 1px solid var(--line); margin-bottom: 2px;
  }
  .lv-caption .lv-fa { margin: 0; font-size: 11.5px; }
  .lv-subskill { font-size: 10px; color: var(--ink-4); margin-inline-start: 2px; }
  .lv-skband { display: flex; justify-content: flex-end; }
  .lv-skev { grid-column: 1 / -1; font-size: 10.5px; color: var(--purple-ink); line-height: 1.5; }
  .lv-evidence { grid-column: 1 / -1; font-size: 10.5px; color: var(--purple-ink); }
  .lv-conf {
    display: inline-block; font-size: 9px; font-weight: 700; letter-spacing: .05em;
    text-transform: uppercase; padding: 2px 6px; border-radius: 999px;
    background: var(--line); color: var(--purple-ink); margin-top: 2px;
  }
  .lv-conf.c-high { background: var(--surf-2); color: var(--green-ink); }
  .lv-conf.c-medium { background: var(--surf-2); color: var(--gold-ink); }
  .lv-conf.c-low { background: var(--surf-2); color: var(--pink-ink); }
  .lv-unassessed { opacity: .78; }
  .lv-input {
    width: 100%; font: inherit; font-size: 13.5px; padding: 9px 11px;
    border-radius: 11px; border: 1px solid var(--line2); background: var(--raise);
    color: var(--ink); margin-top: 9px;
  }
  .lv-input:focus-visible { outline: 2px solid rgba(107,91,210,.45); outline-offset: 1px; }
  .lv-compose { margin-top: 9px; display: grid; gap: 7px; }
  .lv-built {
    min-height: 42px; display: flex; flex-wrap: wrap; gap: 5px; align-items: center;
    padding: 8px; border-radius: 11px; border: 1px dashed var(--line2);
    background: var(--raise);
  }
  .lv-pool { display: flex; flex-wrap: wrap; gap: 5px; }
  .lv-token {
    font: inherit; font-size: 12.5px; cursor: pointer; padding: 5px 10px;
    border-radius: 9px; border: 1px solid var(--line2); background: var(--surf-1);
    color: var(--navy-ink);
  }
  .lv-token:hover { border-color: rgba(107,91,210,.5); }
  .lv-token.on { background: var(--surf-1); border-color: var(--violet); color: var(--navy-ink); }
  .lv-hintline { font-size: 11.5px; color: var(--ink-5); }
  .lv-callout {
    margin-top: 6px; padding: 11px 13px; border-radius: 13px;
    background: var(--surf-2); border: 1px solid rgba(155,106,18,.22);
  }
  .lv-callout b { display: block; font-size: 12.5px; color: var(--gold-ink); margin-bottom: 4px; }
  .lv-callout p { margin: 0; font-size: 11.5px; line-height: 1.6; color: var(--gold-ink); }
  .lv-reliability {
    margin-top: 10px; padding: 10px 12px; border-radius: 12px;
    background: var(--surf-1); border: 1px solid var(--line); font-size: 11px;
    color: var(--ink-3);
  }
  .lv-reliability b { display: block; font-size: 11px; color: var(--ink); margin-bottom: 4px; }
  .lv-reliability ul { margin: 0 0 5px; padding-inline-start: 16px; }
  .lv-reliability li { margin-bottom: 3px; }
  .lv-reliability p { margin: 0; line-height: 1.55; }

  /* ---------- level check: the monthly CEFR assessment ---------------------
     One panel with three faces: the invitation, the paper, and the report.
     The colours are the app's own; the only new decision is that a band is
     always the same colour wherever it appears, so the badge in the header,
     the row in the result and the tag on a question agree at a glance. */
  #lvlpanel.open { display: block; max-height: none; overflow-y: auto; }
  /* The level check, the weekly quiz and the practice sheet used to lift out
     of the column and hang over the conversation as bottom sheets. A sheet is
     a drawer, and a drawer is not a destination: they now take the same page
     as every other section, with the shell's own edges rather than a floating
     card of their own. */
  #lvlpanel.open, #wqpanel.open, #prpanel.open {
    position: relative; inset: auto; height: auto; max-height: none;
    z-index: auto; border-start-start-radius: 0; border-start-end-radius: 0;
    box-shadow: inset 0 1px 0 var(--raise);
  }
  /* A mask over a scroller this tall becomes one composited layer the height
     of the whole paper - four thousand pixels on a phone - and the raster
     budget runs out before the questions are drawn. In logcat that is "tile
     memory limits exceeded, some content may not draw", and on the phone it
     is a blank sheet in the middle of the check. The fade is only the cue that
     there is more to scroll, so the tall panels keep the inset shadow cue and
     spend nothing on a mask. */
  #lvlpanel.open, #rdpanel.open, #wqpanel.open, #prpanel.open {
    -webkit-mask-image: none; mask-image: none;
    scroll-padding-top: 96px; scroll-padding-bottom: 40px;
    /* The panel is a child of the app's column, and the column is not a
       scroller: a sheet taller than the space left above the composer does not
       stop at the top of the window, it grows past it, and the question under
       the status bar is the part that is cut off. Given a share of the column
       and its own scroll box, the sheet stops at the window edge and the
       sticky header stays whole. */
    flex: 1 1 auto; min-height: 0;
  }
  #lvlpanel h3 { border-inline-start: 3px solid var(--indigo); padding-inline-start: 9px; }
  #lvlbody { max-width: 660px; margin: 0 auto; padding-bottom: 8px; }

  .lv-wrap { display: flex; flex-direction: column; gap: 11px; }
  .lv-hero {
    position: relative; overflow: hidden; border-radius: 18px;
    padding: 16px 16px 15px;
    background: radial-gradient(120% 90% at 100% 0%, rgba(107,91,210,.10), transparent 58%),
      radial-gradient(90% 80% at 0% 100%, rgba(47,107,79,.10), transparent 55%),
      linear-gradient(160deg, var(--surf-1), var(--surf-1) 70%, var(--surf-1));
    border: 1px solid var(--line);
    box-shadow: 0 10px 26px -20px var(--line2);
  }
  .lv-eyebrow {
    font-size: 10px; letter-spacing: .15em; text-transform: uppercase;
    color: var(--purple-ink); font-weight: 700; margin-bottom: 7px;
  }
  .lv-h {
    font-family: var(--font-display); font-size: 20px; line-height: 1.22;
    color: var(--ink); margin: 0 0 6px; letter-spacing: -.01em;
  }
  .lv-sub { font-size: 12.5px; line-height: 1.62; color: var(--ink-2); margin: 0; }
  .lv-fa {
    direction: rtl; text-align: right; unicode-bidi: plaintext;
    font-family: var(--font-fa); font-size: 13px; line-height: 2.15;
    color: var(--ink-2); margin: 4px 0 0;
  }

  .lv-meta { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }
  .lv-chip {
    font-size: 10.5px; padding: 4px 9px; border-radius: 999px;
    background: var(--lift); border: 1px solid var(--line);
    color: var(--ink-2); white-space: nowrap;
  }
  .lv-chip b { color: var(--ink); font-weight: 700; }

  /* --- a band, in one place, with one colour ------------------------------ */
  [data-band="A1"] { --lvc: var(--band-a1); --lvcs: var(--band-a1-soft); }
  [data-band="A2"] { --lvc: var(--band-a2); --lvcs: var(--band-a2-soft); }
  [data-band="B1"] { --lvc: var(--band-b1); --lvcs: var(--band-b1-soft); }
  [data-band="B2"] { --lvc: var(--band-b2); --lvcs: var(--band-b2-soft); }
  [data-band="C1"] { --lvc: var(--band-c1); --lvcs: var(--band-c1-soft); }
  [data-band="PRE"], [data-band="none"] { --lvc: var(--band-pre); --lvcs: var(--band-pre-soft); }

  .lv-band {
    display: inline-flex; align-items: baseline; gap: 5px;
    padding: 3px 9px; border-radius: 999px; font-size: 11.5px; font-weight: 700;
    color: var(--lvc); background: var(--lvcs); border: 1px solid color-mix(in srgb, var(--lvc) 30%, transparent);
  }
  .lv-band small { font-size: 9.5px; font-weight: 600; opacity: .8; }

  .lv-bigband {
    display: flex; align-items: center; gap: 13px; margin-top: 14px;
    padding: 11px; border-radius: 15px;
    background: var(--lift); border: 1px solid var(--line);
  }
  .lv-disc {
    width: 62px; height: 62px; flex: none; border-radius: 50%;
    display: grid; place-items: center; color: var(--on-fill); position: relative;
    background: var(--lvc); font-family: var(--font-display); font-weight: 700;
    font-size: 21px; letter-spacing: -.02em;
    box-shadow: 0 8px 18px -12px var(--lvc), inset 0 -2px 6px rgba(0,0,0,.14);
  }
  .lv-disc::after {
    content: ''; position: absolute; inset: -5px; border-radius: 50%;
    border: 1.5px solid color-mix(in srgb, var(--lvc) 32%, transparent);
  }
  .lv-bigband p { margin: 0; font-size: 12px; line-height: 1.55; color: var(--navy-ink); }
  .lv-bigband b { display: block; font-family: var(--font-display); font-size: 14px; color: var(--ink); margin-bottom: 2px; }

  /* --- actions ------------------------------------------------------------ */
  .lv-actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
  .lv-btn {
    font: inherit; font-size: 12.5px; font-weight: 700; cursor: pointer;
    border-radius: 12px; padding: 10px 16px; border: 1px solid transparent;
    background: var(--btn-fill); color: var(--on-fill); display: inline-flex; gap: 7px;
    align-items: center; transition: transform .14s ease, box-shadow .14s ease;
    box-shadow: 0 8px 18px -12px var(--line2);
  }
  .lv-btn:hover { transform: translateY(-1px); }
  .lv-btn:active { transform: translateY(0); }
  .lv-btn.ghost {
    background: var(--surf-1); color: var(--ink); border-color: var(--line2);
    box-shadow: none;
  }
  .lv-btn.ghost:hover { border-color: var(--line2); }
  .lv-btn[disabled] { opacity: .52; cursor: not-allowed; transform: none; }
  .lv-btn.wide { flex: 1 1 100%; justify-content: center; }

  /* --- the paper: sticky header, questions, sticky footer ------------------ */
  .lv-top {
    position: sticky; top: 0; z-index: 3; margin: 0;
    padding: 9px 0 10px; background: var(--surf-1);
    border-bottom: 1px solid var(--line);
  }
  .lv-toprow { display: flex; align-items: baseline; flex-wrap: wrap; gap: 4px 8px; margin-bottom: 6px; }
  .lv-step { font-size: 10.5px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--purple-ink); }
  .lv-secttl { font-family: var(--font-display); font-size: 13.5px; color: var(--ink); font-weight: 700; }
  .lv-count { margin-inline-start: auto; font-size: 11px; color: var(--ink-3); font-variant-numeric: tabular-nums; }
  .lv-toptrack { height: 5px; border-radius: 999px; background: var(--line); overflow: hidden; }
  .lv-toptrack i {
    display: block; height: 100%; width: 0; border-radius: 999px;
    background: linear-gradient(90deg, var(--violet), var(--leaf));
    transition: width .22s ease;
  }
  .lv-exit {
    font: inherit; font-size: 11px; background: none; border: 0; cursor: pointer;
    color: var(--purple-ink); padding: 2px 0 0; text-decoration: underline; text-underline-offset: 2px;
  }

  .lv-secnote { font-size: 12px; line-height: 1.6; color: var(--ink-2); margin: 10px 0 4px; }
  .lv-secnote .lv-fa { font-size: 12.5px; }

  .lv-q {
    background: var(--surf-1); border: 1px solid var(--line);
    border-radius: 14px; padding: 12px 12px 10px; margin-top: 10px;
    scroll-margin-top: 96px;
  }
  .lv-qh { display: flex; align-items: center; gap: 7px; margin-bottom: 6px; }
  .lv-qn {
    font-size: 10.5px; font-weight: 700; color: var(--purple-ink);
    background: var(--line); border-radius: 7px; padding: 2px 7px;
    font-variant-numeric: tabular-nums;
  }
  .lv-stem { font-size: 13.5px; line-height: 1.55; color: var(--ink); margin: 0 0 2px; }
  .lv-stem .gap { color: var(--ink-5); }
  .lv-opts { display: flex; flex-direction: column; gap: 6px; margin-top: 9px; }
  .lv-opt {
    display: flex; align-items: flex-start; gap: 9px; cursor: pointer;
    padding: 9px 11px; border-radius: 11px; font-size: 13px; line-height: 1.45;
    background: var(--raise); border: 1px solid var(--line); color: var(--navy-ink);
    transition: border-color .12s ease, background .12s ease;
  }
  .lv-opt:hover { border-color: rgba(107,91,210,.55); }
  .lv-opt input { position: absolute; opacity: 0; width: 1px; height: 1px; }
  .lv-opt .lv-od {
    flex: none; width: 19px; height: 19px; border-radius: 50%;
    display: grid; place-items: center; font-size: 10.5px; font-weight: 700;
    border: 1px solid var(--line2); color: var(--ink-3); margin-top: 1px;
  }
  .lv-opt.on { background: var(--surf-1); border-color: var(--violet); }
  .lv-opt.on .lv-od { background: var(--violet); border-color: var(--violet); color: var(--on-fill); }
  .lv-opt:focus-within { outline: 2px solid rgba(107,91,210,.45); outline-offset: 1px; }

  .lv-passage {
    margin-top: 12px; padding: 12px 13px; border-radius: 14px;
    background: linear-gradient(180deg, var(--surf-1), var(--surf-1));
    border: 1px dashed var(--line2);
  }
  .lv-passage h4 { margin: 0 0 6px; font-family: var(--font-display); font-size: 13.5px; color: var(--ink); }
  .lv-passage p { margin: 0; font-size: 13px; line-height: 1.72; color: var(--navy-ink); }
  .lv-passage details { margin-top: 8px; }
  .lv-passage summary { font-size: 11.5px; color: var(--navy-ink); cursor: pointer; }
  .lv-passage .lv-fa { font-size: 12.5px; }

  .lv-play {
    font: inherit; font-size: 12px; cursor: pointer; border-radius: 999px;
    padding: 7px 13px; border: 1px solid rgba(47,125,158,.45);
    background: var(--surf-2); color: var(--blue-ink); font-weight: 700;
    display: inline-flex; align-items: center; gap: 7px; margin-top: 9px;
  }
  .lv-play:hover { background: var(--surf-3); }
  .lv-play.on { background: var(--fill-navy3); color: var(--on-fill); border-color: var(--fill-navy3); }
  .lv-transcript { margin-top: 8px; font-size: 12px; color: var(--ink-3); }
  .lv-transcript summary { cursor: pointer; font-size: 11px; }
  .lv-transcript p { margin: 6px 0 0; font-size: 12.5px; line-height: 1.55; color: var(--navy-ink); }

  .lv-textarea {
    width: 100%; min-height: 104px; resize: vertical; font: inherit;
    font-size: 13px; line-height: 1.6; padding: 10px 11px; border-radius: 12px;
    border: 1px solid var(--line2); background: var(--raise); color: var(--ink);
    margin-top: 9px;
  }
  .lv-textarea:focus-visible { outline: 2px solid rgba(107,91,210,.45); outline-offset: 1px; }
  /* The four rubric points, shown while the answer is being written. A point
     that is not earned yet is not an error: it says what the next sentence
     could add. */
  .lv-wmark {
    margin-top: 9px; padding: 9px 10px; border-radius: 12px;
    background: var(--surf-2); border: 1px solid var(--line);
    display: flex; flex-direction: column; gap: 6px;
  }
  .lv-wmh { display: flex; flex-wrap: wrap; gap: 6px; align-items: baseline;
    font-size: 11.5px; color: var(--ink-2); }
  .lv-wmh b { color: var(--navy-ink); font-variant-numeric: tabular-nums; }
  .lv-wmh i { font-style: normal; font-size: 10.5px; color: var(--ink-3); }
  .lv-wms { display: flex; flex-wrap: wrap; gap: 5px; }
  .lv-wmk {
    display: inline-flex; align-items: baseline; gap: 4px; font-size: 11px;
    padding: 3px 7px; border-radius: 999px; border: 1px solid var(--line2);
    color: var(--ink-3); background: var(--raise);
  }
  .lv-wmk.on { color: var(--navy-ink); border-color: var(--line2); background: var(--surf-3); }
  .lv-wmk svg { width: 10px; height: 10px; flex: none; }
  .lv-wmk i { font-style: normal; color: var(--ink-3); }
  .lv-rublabel { font-size: 11px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--purple-ink); margin: 12px 0 6px; }
  .lv-rubric { display: flex; flex-direction: column; gap: 6px; }
  .lv-rubric .lv-opt { font-size: 12.5px; }
  .lv-rubric .lv-od { border-radius: 6px; }
  .lv-timer {
    display: inline-flex; align-items: center; gap: 7px; margin-top: 9px;
    font-size: 11.5px; color: var(--ink-3); font-variant-numeric: tabular-nums;
  }
  .lv-timer b { font-size: 13px; color: var(--ink); }

  .lv-foot {
    position: sticky; bottom: 0; z-index: 3; margin-top: 12px;
    display: flex; gap: 8px; align-items: center;
    padding: 10px 0 12px; background: linear-gradient(180deg, var(--lift-warm), var(--surf-1) 42%);
    border-top: 1px solid var(--line);
  }
  .lv-foot .lv-menu { margin-inline-start: auto; font-size: 11px; color: var(--purple-ink); }

  .lv-warn { color: var(--pink-ink); font-size: 11.5px; }

  /* --- the report --------------------------------------------------------- */
  .lv-game { display: flex; flex-direction: column; gap: 7px; margin-top: 12px; }
  .lv-skillrow {
    display: grid; grid-template-columns: minmax(0,1fr) auto; gap: 4px 10px;
    align-items: center; padding: 9px 11px; border-radius: 12px;
    background: var(--lift); border: 1px solid var(--line);
  }
  .lv-skname { font-size: 12.5px; color: var(--ink); font-weight: 600; }
  .lv-skname small { display: block; font-weight: 400; font-size: 11px; color: var(--purple-ink); font-family: var(--font-fa); direction: rtl; text-align: right; }
  .lv-skself { font-size: 9.5px; letter-spacing: .06em; text-transform: uppercase; color: var(--ink-5); }
  .lv-scale { grid-column: 1 / -1; display: flex; gap: 3px; margin-top: 3px; }
  .lv-scale i {
    flex: 1; height: 5px; border-radius: 999px; background: var(--line);
  }
  .lv-scale i.on { background: var(--lvc); }
  .lv-next {
    margin-top: 12px; padding: 12px; border-radius: 14px;
    background: linear-gradient(180deg, var(--surf-1), var(--surf-1));
    border: 1px solid rgba(107,91,210,.22);
  }
  .lv-next h4 { margin: 0 0 4px; font-size: 12.5px; font-family: var(--font-display); color: var(--ink); }
  .lv-next p { margin: 0; font-size: 12px; line-height: 1.6; color: var(--ink-2); }
  .lv-note { font-size: 11px; line-height: 1.6; color: var(--purple-ink); margin: 10px 0 0; }
  .lv-note b { color: var(--ink-2); }

  .lv-method { margin-top: 4px; font-size: 11.5px; color: var(--ink-3); }
  .lv-method summary { cursor: pointer; font-weight: 600; color: var(--ink-2); }
  .lv-method p { margin: 6px 0 0; line-height: 1.6; }
  .lv-method .lv-fa { font-size: 12px; }

  .lv-hist { margin-top: 6px; }
  .lv-hist h4 { margin: 0 0 5px; font-size: 11px; letter-spacing: .08em; text-transform: uppercase; color: var(--purple-ink); }
  .lv-histrow {
    display: flex; align-items: center; gap: 8px; padding: 6px 2px;
    border-bottom: 1px solid var(--line); font-size: 11.5px; color: var(--ink-2);
  }
  .lv-histrow:last-child { border-bottom: 0; }
  .lv-histrow span:last-child { margin-inline-start: auto; }
  .lv-dots { display: flex; gap: 3px; }
  .lv-dots i { width: 6px; height: 6px; border-radius: 50%; background: var(--lvc); }

  .lv-lock {
    display: flex; align-items: center; gap: 9px; margin-top: 11px;
    padding: 10px 12px; border-radius: 12px; font-size: 12px; color: var(--ink-2);
    background: var(--surf-2); border: 1px solid rgba(155,106,18,.22);
  }
  .lv-lock b { color: var(--gold-ink); }
  .lv-lock .lv-fa { margin: 0; font-size: 12px; }

  /* --- the ladder: one strip that says where you are, A1 to C1 ---------- */
  .lv-ladder { display: flex; gap: 3px; margin-top: 12px; }
  .lv-rung {
    flex: 1; height: 25px; display: grid; place-items: center; border-radius: 8px;
    background: var(--line); color: var(--ink-5); font-size: 10.5px;
    font-weight: 700; letter-spacing: .02em;
  }
  .lv-rung.on { background: var(--lvc); color: var(--on-fill); box-shadow: 0 6px 14px -10px var(--lvc); }

  /* --- the month, as a ring -------------------------------------------- */
  .lv-wait {
    display: flex; align-items: center; gap: 12px; margin-top: 12px;
    padding: 10px 13px; border-radius: 14px;
    background: var(--lift); border: 1px solid rgba(155,106,18,.22);
  }
  .lv-wait b { display: block; font-size: 12.5px; color: var(--gold-ink); }
  .lv-wait .lv-fa { margin: 2px 0 0; font-size: 11.5px; color: var(--gold-ink); }
  .lv-ringwrap { position: relative; width: 60px; height: 60px; flex: none; display: grid; place-items: center; }
  .lv-ring { position: absolute; inset: 0; width: 60px; height: 60px; transform: rotate(-90deg); }
  .lv-ringbg { fill: none; stroke: rgba(155,106,18,.16); stroke-width: 6; }
  .lv-ringfg {
    fill: none; stroke: var(--gold-line); stroke-width: 6; stroke-linecap: round;
    transition: stroke-dashoffset .5s ease;
  }
  .lv-ringwrap b {
    position: relative; font-family: var(--font-display); font-size: 17px;
    color: var(--gold-ink); line-height: 1; text-align: center;
  }
  .lv-ringwrap small { display: block; font-size: 8.5px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; margin-top: 2px; }

  /* --- what you get, in three tiles ------------------------------------ */
  .lv-perks { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 7px; }
  .lv-perk {
    background: var(--surf-1); border: 1px solid var(--line); border-radius: 13px;
    padding: 10px 7px 9px; text-align: center;
  }
  .lv-perk svg { width: 17px; height: 17px; color: var(--violet-ink); }
  .lv-perk b { display: block; font-size: 10.5px; line-height: 1.35; color: var(--ink); margin-top: 5px; }
  .lv-perk small {
    display: block; font-family: var(--font-fa); font-size: 10px; color: var(--purple-ink);
    direction: rtl; line-height: 1.7; margin-top: 3px;
  }

  /* --- the one button that matters -------------------------------------- */
  .lv-cta {
    flex: 1 1 100%; justify-content: space-between; gap: 10px;
    padding: 12px 16px; border-radius: 14px; font-size: 13.5px; text-align: start;
  }
  .lv-cta span { display: block; }
  .lv-cta small { display: block; font-weight: 500; font-size: 10.5px; opacity: .78; margin-top: 2px; }
  .lv-cta svg { width: 17px; height: 17px; flex: none; opacity: .85; }

  /* --- a question answers itself back ----------------------------------- */
  .lv-q { transition: border-color .15s ease, box-shadow .15s ease, background .15s ease; }
  .lv-q:hover { box-shadow: 0 10px 22px -20px var(--line2); }
  .lv-q.answered { border-color: rgba(47,107,79,.34); background: linear-gradient(180deg, var(--surf-1), var(--surf-1)); }
  .lv-q.answered .lv-qn { background: rgba(47,107,79,.15); color: var(--green-ink); }
  .lv-tick { margin-inline-start: auto; color: var(--green-ink); display: inline-flex; }
  .lv-tick svg { width: 13px; height: 13px; }
  .lv-keys { font-size: 10px; color: var(--ink-5); margin-top: 2px; }
  .lv-keys kbd {
    font: inherit; font-size: 9.5px; padding: 1px 4px; border-radius: 4px;
    border: 1px solid var(--line2); background: var(--raise); color: var(--ink-3);
  }

  @media (prefers-reduced-motion: reduce) {
    .lv-btn, .lv-toptrack i, .lv-q, .lv-ringfg { transition: none; }
  }
  @media (max-width: 420px) {
    .lv-h { font-size: 18px; }
    .lv-disc { width: 54px; height: 54px; font-size: 19px; }
  }
  .lv-crumbs { display: flex; gap: 4px; margin-top: 7px; flex-wrap: wrap; }
  .lv-crumb {
    font: inherit; font-size: 10.5px; cursor: pointer; border-radius: 999px;
    padding: 3px 8px; border: 1px solid var(--line);
    background: var(--surf-1); color: var(--ink-3);
  }
  .lv-crumb.on { background: var(--btn-fill); color: var(--on-fill); border-color: var(--btn-fill); font-weight: 700; }
  .lv-crumb.done { border-color: rgba(47,107,79,.5); color: var(--green-ink); }

  /* ---------- mini stories: a reader, then the drills that go with it ------ */
  #stpanel.open { display: block; max-height: none; overflow-y: auto; }
  .stlevels { display: flex; gap: 5px; flex-wrap: wrap; margin-bottom: 10px; }
  .stlv {
    font-family: inherit; font-size: 11px; cursor: pointer; border-radius: 999px;
    padding: 4px 10px; border: 1px solid var(--line);
    background: var(--surf-1); color: var(--ink-2);
  }
  .stlv:hover { border-color: rgba(47,107,79,.5); }
  .stlv.on { background: var(--leaf-soft); border-color: var(--leaf); color: var(--leaf); font-weight: 700; }
  .stcards { display: grid; gap: 8px; }
  .stcard {
    display: flex; gap: 9px; width: 100%; text-align: start; font-family: inherit;
    cursor: pointer; background: var(--surf-1); border: 1px solid var(--line);
    border-radius: 12px; padding: 9px 11px; color: var(--ink);
  }
  .stcard:hover { border-color: rgba(47,107,79,.5); background: var(--surf-1); }
  .stcard:focus-visible { outline: 2px solid var(--leaf); outline-offset: 2px; }
  .stnum {
    flex: none; width: 24px; height: 24px; border-radius: 50%;
    display: grid; place-items: center; background: rgba(47,107,79,.12);
    color: var(--leaf); font-size: 11px; font-weight: 700;
  }
  .stmain { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
  .stname { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; font-size: 13px; font-weight: 700; }
  .stblurb { font-size: 11.5px; color: var(--ink-5); line-height: 1.5; }
  .stmeta { font-size: 10.5px; color: var(--muted); }
  .stbadge {
    font-size: 9.5px; font-weight: 700; padding: 3px 7px; border-radius: 999px;
    background: rgba(47,107,79,.12); color: var(--leaf);
    line-height: 1.5;
  }
  .stbar { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; flex-wrap: wrap; }
  /* text size and the Persian switch, on their own quiet row under the bar */
  .sttools {
    display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
    margin-bottom: 10px;
  }
  .stsizegrp {
    display: inline-flex; align-items: stretch; border: 1px solid var(--line);
    border-radius: 9px; overflow: hidden; background: var(--surf-1);
  }
  .stsize {
    font-family: inherit; font-size: 11px; font-weight: 700; cursor: pointer;
    border: 0; background: none; color: var(--ink-2); padding: 4px 9px; line-height: 1.4;
  }
  .stsize + .stsize { border-inline-start: 1px solid var(--line); }
  .stsize:hover:not(:disabled) { background: var(--leaf-soft); color: var(--leaf); }
  .stsize:disabled { color: rgba(43,48,73,.25); cursor: default; }
  .sttoggle {
    margin-inline-start: auto; font-family: inherit; font-size: 11px; cursor: pointer;
    background: none; border: 1px dashed rgba(47,107,79,.45); border-radius: 9px;
    padding: 4px 9px; color: var(--leaf);
  }
  .sttoggle:hover { background: var(--leaf-soft); }
  .stch {
    margin: 12px 0 5px; font-family: var(--font-display); font-size: 12.5px;
    font-weight: 700; color: var(--ink); display: flex; gap: 6px; align-items: baseline;
  }
  .sts { display: flex; gap: 7px; margin: 0 0 4px; }
  .sts .n { flex: none; width: 18px; text-align: end; font-size: 10px; color: var(--muted); padding-top: 2px; }
  .sts .tx { min-width: 0; }
  .sts .en { font-size: calc(13px * var(--stzoom, 1)); line-height: 1.55; color: var(--ink); }
  .sts .fa {
    display: block; font-size: calc(11.5px * var(--stzoom, 1)); line-height: 2.15;
    color: var(--ink-5); margin-top: 0;
  }
  .stbody.hidefa .sts .fa, .stbody.hidefa .stch .fa { display: none; }
  .stv { padding: 7px 0; border-bottom: 1px solid var(--line); }
  .stv .w { font-size: 12.5px; font-weight: 700; color: var(--ink); }
  .stv .w i { font-style: normal; font-weight: 400; color: var(--muted); font-size: 10.5px; }
  .stv .m { font-size: 11.5px; color: var(--navy-ink); }
  .stv .ex { font-size: 11.5px; color: var(--ink-1); margin-top: 2px; }
  /* ---------- shelf: how far in, and the way to a single story ------------ */
  .stprog { margin: 2px 0 10px; }
  .stprogbar {
    height: 5px; border-radius: 999px; background: rgba(47,107,79,.13);
    overflow: hidden;
  }
  .stprogbar i {
    display: block; height: 100%; border-radius: 999px;
    background: linear-gradient(90deg, var(--leaf), var(--surf-6));
    transition: width .3s ease;
  }
  .stprogline {
    display: flex; justify-content: space-between; gap: 8px; margin-top: 4px;
    font-size: 10.5px; color: var(--muted);
  }
  .stprogline b { color: var(--leaf); }
  .stsearchrow { margin-bottom: 8px; }
  .stsearch {
    width: 100%; font-family: inherit; font-size: 12px; color: var(--ink);
    background: var(--surf-1); border: 1px solid var(--line);
    border-radius: 10px; padding: 7px 11px;
  }
  .stsearch:focus { outline: 2px solid rgba(47,107,79,.35); outline-offset: 1px; border-color: var(--leaf); }
  .stcount { font-size: 10.5px; color: var(--muted); margin: 0 0 6px; }
  .stdots { display: inline-flex; gap: 3px; vertical-align: middle; margin-inline-start: 2px; }
  .stdots i {
    width: 5px; height: 5px; border-radius: 50%; background: var(--line2);
  }
  .stdots i.on { background: var(--leaf); }
  .stcard.lv-VE { border-inline-start: 3px solid var(--line-strong); }
  .stcard.lv-E  { border-inline-start: 3px solid var(--fill-navy3); }
  .stcard.lv-M  { border-inline-start: 3px solid var(--fill-navy3); }
  .stcard.lv-H  { border-inline-start: 3px solid var(--red-ink); }
  .stempty {
    text-align: center; color: var(--muted); font-size: 12px;
    padding: 18px 8px; border: 1px dashed var(--line2); border-radius: 12px;
  }
  .stempty p { margin: 0 0 4px; }
  .stnext { display: flex; gap: 8px; margin-top: 14px; }
  .stnext > span { flex: 1; }
  .stjump {
    flex: 1; min-width: 0; text-align: start; font-family: inherit; cursor: pointer;
    background: var(--surf-1); border: 1px solid var(--line); border-radius: 11px;
    padding: 8px 10px; color: var(--ink); display: flex; flex-direction: column; gap: 2px;
  }
  .stjump.next { text-align: end; align-items: flex-end; margin-inline-start: auto; }
  .stjump:hover { border-color: rgba(47,107,79,.5); background: var(--surf-1); }
  .stjump .k { font-size: 10px; color: var(--leaf); font-weight: 700; }
  .stjump b {
    font-size: 11.5px; font-weight: 600; color: var(--ink-2);
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 100%;
  }
  .stcu { font-size: 10.5px; color: var(--muted); margin-top: 12px; line-height: 1.6; }
  .stcu a { color: var(--leaf); }

  /* ---------- listening: level tabs + playable sentences ---------- */
  .ltabs { display: flex; gap: 5px; margin-bottom: 10px; flex-wrap: wrap; }
  .ltab {
    background: var(--ice);
    color: var(--ice-ink); border: 1px solid rgba(51,82,110,.2);
    border-radius: 999px; padding: 4px 12px; font-size: 12px; font-weight: 700;
    cursor: pointer; transition: .12s; font-family: inherit;
  }
  .ltab:hover { background: var(--ice2); transform: translateY(-1px); }
  .ltab.on {
    background: var(--fill-navy); color: var(--on-fill);
    border-color: transparent; box-shadow: 0 3px 10px var(--line2);
  }
  .llist { display: flex; flex-direction: column; gap: 4px; }
  .lrow {
    display: flex; align-items: center; gap: 10px;
    background: var(--surf-2); border: 1px solid var(--line);
    border-radius: 10px; padding: 7px 11px; transition: .12s;
  }
  .lrow:hover { background: var(--surf-2); border-color: var(--line2); }
  .lrow.playing {
    background: var(--ice); border-color: rgba(51,82,110,.4);
  }
  .lplay {
    width: 28px; height: 28px; flex: none; border-radius: 50%;
    background: var(--fill-navy); border: none;
    color: var(--on-fill); font-size: 12px; cursor: pointer;
    display: grid; place-items: center; transition: .12s;
  }
  .lplay:hover { filter: brightness(1.12); transform: scale(1.08); }
  .ltext { flex: 1; min-width: 0; }
  .ltext .en { font-size: 13.5px; line-height: 1.45; }
  .ltext .fa { font-size: 11.5px; color: var(--muted); margin-top: 1px; }
  .lblurb { font-size: 11.5px; color: var(--muted); margin-bottom: 8px; }
  .domains { display: block; max-height: 230px; overflow-y: auto; padding-right: 4px; }

  /* vocabulary: grouped, compact — one pill per domain (alt-click = فارسی) */
  .vgroup { margin-bottom: 8px; }
  .vgroup:last-child { margin-bottom: 0; }
  .vgroup-head {
    display: flex; align-items: baseline; gap: 6px;
    font-size: 10.5px; letter-spacing: .06em; text-transform: uppercase;
    color: var(--ink-3); margin-bottom: 5px; font-weight: 600;
  }
  .vgroup-head .fa { color: var(--dim); text-transform: none; letter-spacing: 0; font-weight: 400; }
  .vgroup-head .count {
    background: var(--line); border-radius: 999px;
    padding: 0 6px; font-size: 10px; margin-inline-start: auto;
  }
  .vrow { display: flex; flex-wrap: wrap; gap: 3px; }
  .vbtn {
    display: inline-flex; align-items: center; gap: 5px;
    background: var(--ice); color: var(--ice-ink);
    border: 1px solid rgba(51,82,110,.18);
    border-radius: 7px; padding: 2px 7px; font-size: 10.5px; line-height: 1.25;
    cursor: pointer; transition: .12s; font-family: inherit;
  }
  .vbtn:hover {
    background: rgba(60,64,91,.26); border-color: rgba(60,64,91,.5);
    transform: translateY(-1px); color: var(--navy);
  }
  .vbtn .n {
    background: var(--line); border-radius: 4px;
    padding: 0 4px; font-size: 9px; color: var(--muted);
    font-variant-numeric: tabular-nums;
  }
  /* A lesson is six things - structure, tip, explanation, function, examples,
     exercises - and they used to arrive as one pre-wrap wall of text. Each is
     its own bordered card now, with a rail whose colour says which part of the
     lesson you are in. The engine's text is untouched: this is the page's
     parsing of the same words the CLI and the APK print. */
  .glesson { white-space: normal; }
  .glesson-head {
    font-family: var(--font-display); font-size: 14.5px; font-weight: 700;
    color: var(--navy); line-height: 1.4; margin-bottom: 2px;
    unicode-bidi: plaintext; text-align: start;
  }
  /* One frame around the whole lesson, and hairline borders *inside* it
     between the parts: the sections read as chapters of one page rather than
     six loose cards, and the frame is what separates the lesson from the rest
     of the conversation. */
  .glesson-head .bl, .gsec-h .bl { display: inline; }
  .glbody {
    margin-top: 10px; border: 1px solid var(--line2);
    border-radius: 14px; overflow: hidden;
    background: linear-gradient(180deg, var(--lift-soft), var(--lift-warm));
    box-shadow: 0 1px 2px var(--line);
  }
  .gsec {
    margin: 0; border: 0; border-radius: 0;
    background: transparent; box-shadow: none;
  }
  .gsec + .gsec {
    border-top: 1px solid var(--line);
  }
  .gsec-h {
    display: flex; align-items: center; gap: 7px;
    padding: 6px 11px 6px 10px;
    font-family: var(--font-display); font-size: 12.5px; font-weight: 700;
    letter-spacing: .015em; color: var(--navy);
    background: var(--line);
    border-bottom: 1px solid var(--line);
    border-inline-start: 3px solid var(--violet);
    unicode-bidi: plaintext; text-align: start;
  }
  .gsec-b {
    white-space: pre-wrap; padding: 9px 12px 10px 13px;
    font-size: 13.5px; line-height: 1.66; color: var(--text);
    unicode-bidi: plaintext; text-align: start;
  }
  /* A Persian run inside an English line is its own island, so a bracket
     around it belongs to the English sentence it was written in rather than
     being pulled into the right-to-left text and mirrored. */
  .msg bdi, .gsec-b bdi, .glesson-head bdi, .gsec-h bdi { unicode-bidi: isolate; }
  /* Every line of a bilingual message is its own block carrying an explicit
     dir. unicode-bidi: plaintext only picks the *paragraph* direction; the
     alignment still came from the inherited left-to-right `direction`, which is
     why Persian lines stayed on the left. With dir on the line, text-align:
     start is right for Persian and left for English, by construction. */
  .bl { display: block; white-space: pre-wrap; text-align: start; }
  /* A line that carries both scripts: the Persian is set in the theme's
     declared Persian face (the handwriting font also claims Arabic glyphs and
     reads as a wobble at this size), it gets the taller line height Persian
     wants, and the Latin inside it is marked as its own run with a hair of
     space around it so a borrowed term does not collide with the Persian
     around it. */
  /* Vazirmatn is the Persian face wherever Persian appears: the language the
     renderer writes on a line, the islands it emits inside an English one, the
     translation lines, and any element the app marks as Persian. A font stack
     is easy to override by accident; naming the surfaces it applies to is not. */
  /* A Persian element is a Persian element anywhere in the app, not only in
     the conversation. The panels used to give every one of these spans the
     Persian face and nothing else, so a Persian word sat in a left-to-right
     box: left-aligned, with its own punctuation opening on the wrong side.
     Direction belongs to the element, so it is declared once here for every
     class the panels use. */
  [lang="fa"], .fa, .dfa, .pfa, .bfa, .bl[dir="rtl"], .dline.fa, .msg.rtl,
  .gsec-b bdi.fa {
    font-family: var(--font-fa);
    direction: rtl;
    unicode-bidi: isolate;
  }
  /* A Persian sentence on its own line starts at the right edge, the way the
     reader's eye enters it; inline Persian keeps its place inside the
     English line and only its own text is right-to-left. */
  div.fa, p.fa, .dline.fa, .dfa, .pfa, .bfa.block { text-align: right; }
  .bl .fa { font-family: var(--font-fa); font-size: .97em; line-height: 2; }
  .bl[dir="rtl"] { line-height: 2.05; }
  .bl[dir="rtl"] .lat {
    padding-inline: 2px; font-size: .96em; letter-spacing: .005em;
    font-family: var(--font-body);
  }
  /* A Persian value inside an English label - a dictionary meaning, a word's
     Persian name - is an island for the same reason a Persian parenthetical
     is: otherwise its full stop resolves against the English line. */
  .wd-mean { text-align: start; }
  .wd-mean .fa { unicode-bidi: isolate; direction: rtl; }
  /* the quiet marker that opens a translation line */
  .trm { color: var(--muted); margin-inline-end: 5px; font-size: .92em; }
  .gsec-b b { color: var(--navy); }
  /* one rail colour per part, drawn from the theme's own accents */
  .gsec[data-kind="structure"]   .gsec-h { border-inline-start-color: var(--violet); }
  .gsec[data-kind="tip"]         .gsec-h { border-inline-start-color: var(--amber); }
  .gsec[data-kind="explanation"] .gsec-h { border-inline-start-color: var(--indigo); }
  .gsec[data-kind="function"]    .gsec-h { border-inline-start-color: var(--cyan); }
  .gsec[data-kind="examples"]    .gsec-h { border-inline-start-color: var(--teal); }
  .gsec[data-kind="exercises"]   .gsec-h { border-inline-start-color: var(--slate-rail, var(--focus)); }
  @media (max-width: 560px) {
    .gsec-b { font-size: 13px; padding: 8px 10px 9px 11px; }
  }
  /* grammar panel: compact, grouped by CEFR level */
  .glevel { margin-bottom: 5px; }
  .glevel:last-child { margin-bottom: 0; }
  .glevel-head {
    display: flex; align-items: center; gap: 5px;
    font-size: 10px; color: var(--muted); letter-spacing: .05em;
    text-transform: uppercase; margin-bottom: 4px;
  }
  /* CEFR level chip in the group header */
  .vgroup-head .lv {
    font-size: 9.5px; font-weight: 800; letter-spacing: .05em;
    padding: 2px 6px; border-radius: 5px;
    background: var(--ice);
    color: var(--ice-ink); border: 1px solid rgba(51,82,110,.22);
  }
  /* in-panel search (the domain panel needs one) */
  .psearch { margin-bottom: 9px; }
  .psearch input {
    /* The box was taller than the rows it filters. A search field is a
       shortcut, not a form: the type stays at 15px and only the line box and
       the padding shrink, which is where the height was going. */
    width: 100%; padding: 6px 12px; font-size: 15px; line-height: 1.2;
    font-family: inherit;
    color: var(--text); outline: none; border-radius: 10px;
    background: var(--line); border: 1px solid var(--line);
  }
  .psearch input:focus {
    border-color: rgba(60,64,91,.7); background: var(--line);
    box-shadow: 0 0 0 3px rgba(60,64,91,.16);
  }
  .psearch input::placeholder { color: var(--ink-4); }
  .pempty { font-size: 12.5px; color: var(--muted); padding: 10px 2px; }
  .ftopic .n {
    background: var(--line); border-radius: 5px;
    padding: 0 5px; font-size: 10px; color: var(--muted);
  }
  .glevel-head b { color: var(--ink); font-weight: 700; }
  .glevel-head .count {
    background: var(--line); border-radius: 999px;
    padding: 1px 7px; font-size: 10.5px;
  }
  .gtopic {
    display: flex; flex-wrap: wrap; gap: 3px;
  }
  .gbtn {
    display: inline-flex; align-items: stretch;
    background: var(--ice);
    border: 1px solid rgba(51,82,110,.18);
    border-radius: 999px; overflow: hidden;
    transition: .15s; white-space: nowrap;
  }
  .gbtn:hover { background: var(--ice2); transform: translateY(-1px); }
  .gmain {
    background: none; border: none; cursor: pointer;
    display: inline-flex; align-items: baseline; gap: 4px;
    color: var(--ice-ink); padding: 2px 3px 2px 7px; font-size: 11px;
    line-height: 1.25; font-family: inherit;
  }
  .gmain .fa { color: var(--ice-ink); font-size: 9.5px; }
  .go {
    background: rgba(232,191,95,.34); color: var(--gold-ink);
    border: none; border-left: 1px solid rgba(207,159,60,.45);
    padding: 0 5px; font-size: 9.5px; cursor: pointer; line-height: 1.2;
  }
  .go:hover { background: rgba(232,191,95,.62); }
  .gsep { color: var(--muted); font-size: 10px; width: 100%; }

  /* ---------- the library: books → lessons → words ----------
     One panel, three depths. A book opens its lessons, a lesson opens its
     words, and every depth carries a way back: a list you cannot leave reads
     as the end of the app, not as a page of it.

     Direction is declared per element rather than left to the browser. An
     English definition is ltr and a Persian meaning is rtl, so the pair can
     never reorder each other the way the dictionary senses did. */
  .bbooks { display: flex; flex-direction: column; gap: 7px; }
  /* Lessons are a grid, not a column: a book of forty lessons was forty rows
     of scroll before the first word, and the number is what a learner looks
     for, so the tile leads with it. */
  .bgrid {
    display: grid; gap: 7px;
    grid-template-columns: repeat(auto-fill, minmax(144px, 1fr));
  }
  .bgrid .blesson {
    flex-direction: column; align-items: flex-start; gap: 0;
    padding: 7px 10px 8px;
  }
  .bgrid .blesson .n { margin-inline-start: 0; margin-top: 3px; }
  /* The breadcrumb stays put: twelve word cards is more than a phone screen,
     and once you have scrolled past them you should still know which book and
     lesson you are reading. */
  .bstick {
    position: sticky; top: 0; z-index: 3; display: flex; align-items: center;
    gap: 8px; padding: 1px 0 7px; margin-top: -2px;
    background: linear-gradient(var(--surf-1) 76%, rgba(255,252,239,0));
  }
  .bstick .bback { padding: 0; }
  .bstick .bcrumb {
    font-size: 10.5px; color: var(--muted); overflow: hidden;
    text-overflow: ellipsis; white-space: nowrap; direction: ltr;
  }
  /* The number is a fixed column, not a chip that changes width with its
     digits: entry 9 and entry 100 have to start their word at the same x,
     otherwise the list marches sideways down the page. */
  .bnum {
    flex: 0 0 20px; box-sizing: border-box; text-align: center;
    font-size: 9.5px; color: var(--muted); background: var(--line);
    border-radius: 5px; padding: 1px 2px; font-variant-numeric: tabular-nums;
  }
  .bday {
    font-size: 9.5px; color: var(--gold-ink); background: rgba(138,90,0,.10);
    border-radius: 5px; padding: 1px 6px;
  }
  .bbook {
    display: grid; gap: 2px; width: 100%; text-align: start; cursor: pointer;
    font-family: inherit; color: var(--ink);
    background: var(--surf-1); border: 1px solid var(--line);
    border-radius: 12px; padding: 9px 11px 10px;
    border-inline-start: 3px solid var(--navy); transition: .15s;
  }
  .bbook:hover { transform: translateY(-1px); border-color: rgba(60,64,91,.42); }
  .bbook b { font-size: 13.5px; font-weight: 700; }
  .bbook .bfa { font-size: 12px; color: var(--ink-2); line-height: 1.9; }
  .bbook .bmeta { font-size: 10.5px; color: var(--muted); }
  .bback {
    display: inline-flex; align-items: center; gap: 5px;
    background: none; border: none; cursor: pointer; font-family: inherit;
    color: var(--indigo-ink); font-size: 11.5px; font-weight: 700; padding: 0 0 7px;
  }
  .bback:hover { text-decoration: underline; }
  .bhead2 { font-size: 12px; font-weight: 700; color: var(--ink); padding-bottom: 6px; }
  .blesson {
    display: flex; align-items: center; gap: 8px; width: 100%;
    font-family: inherit; cursor: pointer; text-align: start;
    background: var(--surf-1); border: 1px solid var(--line);
    border-radius: 10px; padding: 8px 11px; color: var(--ink);
  }
  .blesson:hover { border-color: rgba(60,64,91,.42); }
  .blesson .bn { font-size: 12.5px; font-weight: 700; }
  .blesson .bfa { font-size: 11.5px; color: var(--muted); }
  .blesson .n {
    margin-inline-start: auto; font-size: 10px; color: var(--muted);
    background: var(--line); border-radius: 5px; padding: 0 5px;
  }
  .bwords { display: flex; flex-direction: column; gap: 8px; }
  .bword {
    background: var(--surf-1); border: 1px solid var(--line);
    border-radius: 12px; padding: 9px 11px 10px;
    border-inline-start: 3px solid var(--teal);
  }
  /* A book entry is laid out on one gutter. The number sits in it, so the
     word, the Persian meaning, the definition and the examples all start at
     the same left edge; before this the head was indented by its number while
     the definition started at the card edge, and the Persian meaning floated
     at the far right of a third, different line - three alignments in one
     entry, which is what made the list look scattered. English stays left to
     right, Persian right to left on its own line under the word. */
  /* 20px number column + the head's 6px gap: the definition and the examples
     begin exactly under the word itself. */
  .bword .bfa, .bword .bdef, .bex { margin-inline-start: 26px; }
  .bword .bfa {
    /* in an RTL element the inline start is the right edge, so this insets
       the Persian from the right by the same width as the number gutter:
       two lanes, each with its own margin, neither touching the card edge */
    direction: rtl; text-align: right; unicode-bidi: plaintext;
    line-height: 2.2; margin-top: 0;
  }
  .bwh { display: flex; align-items: baseline; gap: 6px; flex-wrap: wrap; }
  .bwh b { font-size: 15px; }
  .bwh .ipa { font-size: 11px; color: var(--muted); }
  .bwh .pos {
    font-size: 9.5px; font-style: normal; color: var(--indigo-ink);
    background: rgba(79,70,160,.10); border-radius: 5px; padding: 1px 6px;
  }
  .bwh .bsay {
    margin-inline-start: auto; background: none; cursor: pointer;
    border: 1px solid var(--line); border-radius: 8px;
    font-size: 11px; line-height: 1; padding: 4px 6px; color: var(--ink);
  }
  .bwh .bsay:hover { background: var(--line); }
  .bword .bfa { font-size: 12.5px; color: var(--ink-2); }
  .bword .bdef { font-size: 12px; color: var(--ink); margin-top: 4px; }
  .bex { margin: 5px 0 0; margin-inline-start: 26px; padding: 0; list-style: none; }
  .bex li {
    display: flex; gap: 6px; align-items: baseline;
    font-size: 11.5px; color: var(--ink-2);
    padding: 2px 0 2px 9px; border-inline-start: 2px solid var(--line-strong);
  }
  .bex li button {
    flex: none; background: none; border: none; cursor: pointer;
    color: var(--indigo-ink); font-size: 10px; padding: 0; font-family: inherit;
  }
  /* ---- a book of structures --------------------------------------------
     The grammar book is a different animal from the word books: a lesson is a
     rule with examples of it and then something to do. Same card, same gutter,
     one more layer for the exercises - the pattern line sits in a monospace
     strip because a form is not a sentence, and an answer stays folded until
     the learner asks for it. */
  .bform {
    margin-top: 6px; padding: 6px 9px; border-radius: 8px;
    background: var(--surf-2); border: 1px dashed var(--line-strong);
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 11.5px; line-height: 1.7; color: var(--ink-2);
    direction: ltr; text-align: left; overflow-wrap: anywhere;
  }
  /* the rule, the labels and the pattern line start where the body of a word
     entry starts, under the title and not at the card edge */
  .bstruct .bform, .bstruct .blabel { margin-inline-start: 26px; }
  .bstruct .bchap {
    font-size: 9.5px; color: var(--muted); letter-spacing: .02em;
    border: 1px solid var(--line); border-radius: 5px; padding: 1px 6px;
  }
  .blabel {
    display: flex; align-items: baseline; gap: 6px; flex-wrap: wrap;
    margin: 11px 0 5px; font-family: var(--font-display);
    font-size: 11px; font-weight: 700; letter-spacing: .04em;
    text-transform: uppercase; color: var(--ink-3);
  }
  .blabel .bfa { font-size: 10.5px; font-weight: 500; text-transform: none;
    letter-spacing: 0; color: var(--muted); }
  .bexg { display: flex; flex-direction: column; gap: 6px; margin-inline-start: 26px; }
  .bexrow { padding: 4px 0 4px 9px; border-inline-start: 2px solid var(--line-strong); }
  .bexrow .en {
    display: flex; gap: 6px; align-items: baseline;
    font-size: 12px; color: var(--ink); direction: ltr; text-align: left;
  }
  .bexrow .en button {
    flex: none; background: none; border: none; cursor: pointer;
    color: var(--indigo-ink); font-size: 10px; padding: 0; font-family: inherit;
  }
  .bexrow .fa {
    direction: rtl; text-align: right; unicode-bidi: plaintext;
    font-size: 11.5px; line-height: 1.95; color: var(--ink-2);
  }
  /* exercise and exam cards: the prompt, then the answer behind a button */
  .bexr {
    margin-inline-start: 26px; margin-bottom: 6px; padding: 8px 10px;
    border-radius: 10px; background: var(--surf-2); border: 1px solid var(--line);
  }
  .bexr .q {
    font-size: 12px; line-height: 1.6; color: var(--ink);
    direction: ltr; text-align: left;
  }
  .bexr .q .num {
    display: inline-block; min-width: 15px; color: var(--muted);
    font-variant-numeric: tabular-nums;
  }
  .bexr .opts {
    display: flex; flex-wrap: wrap; gap: 5px; margin-top: 5px;
    direction: ltr; text-align: left;
  }
  .bexr .opt {
    font-size: 11px; padding: 2px 7px; border-radius: 999px;
    border: 1px solid var(--line); background: var(--surf-1); color: var(--ink-2);
  }
  .bexr .peek {
    font: inherit; font-size: 10.5px; cursor: pointer; margin-top: 6px;
    padding: 3px 9px; border-radius: 999px;
    border: 1px solid var(--line); background: var(--surf-1); color: var(--ink-3);
  }
  .bexr .peek:hover { border-color: var(--line2); color: var(--ink); }
  .bexr .ans {
    margin-top: 6px; padding-top: 6px; border-top: 1px dashed var(--line);
    font-size: 11.5px; line-height: 1.75; color: var(--ink);
    direction: ltr; text-align: left;
  }
  .bexr .ans[hidden] { display: none; }
  .bexr .ans b { color: var(--teal); }
  .bexr .ans .why-fa {
    display: block; direction: rtl; text-align: right; unicode-bidi: plaintext;
    color: var(--ink-2); font-size: 11.5px;
  }

  /* ---------- reading: strategies, a passage, four kinds of question ----
     One panel with two views. The list is a table of contents; the detail is
     a lesson: explanation first, then the passage, then the questions. Both
     are drawn into #rdbody by the Reading module, so every class here is used
     by generated markup and none of it can be styled by a document selector
     that does not exist yet. Green is this section's colour and appears in
     exactly three places: the heading rule, the strategy numbers and the
     "right answer" state. */
  /* A lesson is read, not scanned, so the column has a measure: 640px on a
     1178px panel keeps the questions together, and the passage is narrower
     still. Full width on a desktop put 168 characters on a line, which is
     three times the length an eye can track back from. */
  .rdbody {
    display: flex; flex-direction: column; gap: 10px;
    width: 100%; max-width: 640px; margin-inline: auto;
  }
  .rdintro {
    font-size: 11.5px; color: var(--muted); line-height: 1.6;
    padding: 2px 0 2px 9px; border-inline-start: 2px solid rgba(47,107,79,.35);
  }
  .rdintro .fa { display: block; margin-top: 2px; }

  .rdlist { display: flex; flex-direction: column; gap: 7px; }
  .rdcard {
    display: flex; align-items: center; gap: 11px; width: 100%;
    text-align: start; font-family: inherit; cursor: pointer;
    background: var(--surf-1); border: 1px solid var(--line);
    border-radius: 12px; padding: 9px 12px 9px 10px; color: var(--ink);
    transition: border-color .14s, transform .14s, background .14s;
  }
  .rdcard:hover { border-color: rgba(47,107,79,.55); transform: translateY(-1px); }
  .rdcard:focus-visible { outline: 2px solid var(--leaf); outline-offset: 2px; }
  .rdnum {
    flex: 0 0 26px; height: 26px; border-radius: 8px;
    display: grid; place-items: center; font-size: 13px;
    background: var(--leaf-soft); color: var(--leaf);
    border: 1px solid rgba(47,107,79,.22);
  }
  .rdmain { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
  .rdname { display: flex; align-items: center; gap: 7px; flex-wrap: wrap; }
  .rdname b { font-size: 13.5px; font-weight: 700; }
  .rdname .lvl {
    font-size: 9.5px; font-weight: 700; letter-spacing: .04em;
    color: var(--leaf); background: var(--leaf-soft);
    border-radius: 5px; padding: 1px 5px;
  }
  .rdblurb { font-size: 11.5px; color: var(--ink-2); line-height: 1.5; }
  .rdmeta { font-size: 10.5px; color: var(--muted); }
  .rdchev { flex: none; color: var(--leaf); font-size: 13px; opacity: .75; }
  .rdcard.done { border-color: rgba(47,107,79,.42); background: var(--surf-1); }
  .rdcard.done .rdnum { background: var(--leaf); color: var(--on-fill); border-color: var(--leaf); }

  /* --- progress, above the cards --- */
  .rdprog {
    display: flex; flex-direction: column; gap: 6px;
    background: var(--surf-1); border: 1px solid rgba(47,107,79,.25);
    border-radius: 12px; padding: 9px 12px 10px;
  }
  .rdprogtop {
    display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap;
    font-size: 11px; color: var(--ink-2);
  }
  .rdprogtop b { font-size: 12px; color: var(--ink); }
  .rdprogtop .pct { margin-inline-start: auto; font-weight: 700; color: var(--leaf); }
  .rdtrack { height: 7px; border-radius: 999px; background: var(--line); overflow: hidden; }
  .rdfill {
    height: 100%; border-radius: 999px;
    background: linear-gradient(90deg, var(--leaf), var(--surf-6));
    transition: width .3s;
  }
  .rdstats { display: flex; gap: 10px; flex-wrap: wrap; font-size: 10.5px; color: var(--muted); }
  .rdstats b { color: var(--ink); font-weight: 700; }

  /* --- the detail view --- */
  .rdbar {
    display: flex; align-items: center; gap: 8px;
    padding-bottom: 2px;
  }
  .rdback {
    display: inline-flex; align-items: center; gap: 5px;
    font-family: inherit; font-size: 11.5px; cursor: pointer;
    background: none; border: 1px solid var(--line2);
    border-radius: 999px; padding: 4px 11px 4px 9px; color: var(--ink);
  }
  .rdback:hover { background: var(--line); }
  .rdscore {
    margin-inline-start: auto; font-size: 10.5px; color: var(--muted);
    background: rgba(47,107,79,.09); border-radius: 999px; padding: 3px 9px;
    border: 1px solid rgba(47,107,79,.2);
  }
  .rdhero h4 {
    margin: 2px 0 0; font-size: 15px; font-family: var(--font-display);
    color: var(--ink); display: flex; align-items: center; gap: 7px; flex-wrap: wrap;
  }
  .rdhero .rdhero-fa { font-size: 12.5px; color: var(--leaf); margin-top: 3px; }
  .rdherometa { font-size: 10.5px; color: var(--muted); margin-top: 3px; }

  /* --- worked example, mistakes, tips, checklist --- */
  .rdexample {
    background: var(--surf-1); border: 1px solid var(--line);
    border-inline-start: 3px solid var(--leaf);
    border-radius: 11px; padding: 9px 12px;
  }
  .rdexample p { margin: 0; font-size: 12.5px; line-height: 1.72; color: var(--ink-1); }
  .rdlist2 {
    list-style: none; margin: 0; padding: 0;
    display: flex; flex-direction: column; gap: 6px;
  }
  .rdlist2 li {
    display: grid; grid-template-columns: 13px 1fr; gap: 6px;
    font-size: 11.8px; line-height: 1.55; color: var(--ink-1);
  }
  .rdlist2 li::before { font-weight: 700; line-height: 1.5; }
  .rdlist2.mistakes li::before { content: '✗'; color: var(--rose-ink); }
  .rdlist2.checklist li::before { content: '✓'; color: var(--leaf); }
  .rdlist2.tips li::before { content: '→'; color: var(--leaf); }
  .rdlist2 li .fa {
    display: block; direction: rtl; text-align: right;
    color: var(--ink-5); font-size: 11.2px; line-height: 1.85;
  }
  .rdpara { transition: background .2s; }
  .rdpara.flash { background: var(--surf-2); box-shadow: 0 0 0 6px var(--surf-2); border-radius: 3px; }
  .rdev {
    margin-top: 4px; padding: 0; background: none; border: none;
    font-family: inherit; font-size: 10.5px; color: var(--leaf);
    text-decoration: underline; cursor: pointer;
  }
  .rdev:hover { color: var(--ink); }
  .rdresult {
    display: flex; flex-direction: column; gap: 6px;
    background: var(--leaf-soft); border: 1px solid rgba(47,107,79,.3);
    border-radius: 12px; padding: 10px 12px;
  }
  .rdresult b { font-size: 13px; color: var(--ink); }
  .rdresult .rdrows { display: flex; gap: 8px; flex-wrap: wrap; font-size: 10.8px; color: var(--ink-2); }
  .rdresult .rdrows span {
    background: var(--surf-1); border-radius: 999px; padding: 1px 8px;
    border: 1px solid rgba(47,107,79,.16);
  }
  .rdresult .rdp { font-size: 11.5px; }
  .rdresult .rdp.fa { margin-top: 2px; }

  .rdsec { border-top: 1px dashed var(--line); padding-top: 9px; }
  .rdsec:first-of-type { border-top: none; padding-top: 0; }
  .rdlabel {
    display: flex; align-items: baseline; gap: 6px;
    font-size: 10px; letter-spacing: .09em; text-transform: uppercase;
    color: var(--ink-3); font-weight: 700; margin-bottom: 5px;
  }
  .rdlabel .fa { text-transform: none; letter-spacing: 0; font-weight: 400; color: var(--muted); }
  .rdp { font-size: 12.5px; line-height: 1.65; color: var(--ink-1); margin: 0; }
  .rdp + .rdp { margin-top: 4px; }
  .rdp.fa {
    direction: rtl; text-align: right; margin-top: 2px; color: var(--ink-2);
    line-height: 2.15;
  }

  .rdsteps { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }
  .rdsteps li { display: flex; gap: 8px; align-items: flex-start; }
  .rdsteps .sn {
    flex: 0 0 18px; height: 18px; border-radius: 50%; margin-top: 1px;
    display: grid; place-items: center; font-size: 10px; font-weight: 700;
    background: var(--leaf-soft); color: var(--leaf);
    border: 1px solid rgba(47,107,79,.25);
  }
  .rdsteps .stx { flex: 1; min-width: 0; }
  .rdsteps .sen { font-size: 12.5px; line-height: 1.55; color: var(--ink-1); }
  .rdsteps .sfa { font-size: 11.5px; line-height: 1.8; color: var(--muted); }

  /* --- the three practices, as a row of chips --- */
  .rdprac {
    display: flex; gap: 6px; margin-bottom: 9px;
    overflow-x: auto; padding-bottom: 2px; scrollbar-width: thin;
  }
  .rdpracbtn {
    display: flex; align-items: center; gap: 6px; flex: 0 0 auto;
    max-width: 46%; font-family: inherit; font-size: 11px; cursor: pointer;
    background: var(--surf-1); border: 1px solid var(--line);
    border-radius: 999px; padding: 4px 10px 4px 4px; color: var(--ink);
  }
  .rdpracbtn:hover { border-color: rgba(47,107,79,.5); }
  .rdpracbtn:focus-visible { outline: 2px solid var(--leaf); outline-offset: 2px; }
  .rdpracbtn.on { border-color: var(--leaf); background: var(--leaf-soft); }
  .rdpracbtn .pn {
    flex: none; width: 17px; height: 17px; border-radius: 50%;
    display: grid; place-items: center; font-size: 10px; font-weight: 700;
    background: rgba(47,107,79,.12); color: var(--leaf);
  }
  .rdpracbtn .pt {
    max-width: 150px; overflow: hidden; text-overflow: ellipsis;
    white-space: nowrap; color: var(--ink-2);
  }
  .rdpracbtn .ps { flex: none; font-size: 10px; color: var(--muted); }
  .rdpracbtn.done .ps { color: var(--leaf); font-weight: 700; }

  /* --- the passage --- */
  .rdpassage {
    background: var(--surf-1); border: 1px solid rgba(47,107,79,.25);
    border-radius: 13px; padding: 12px 14px 13px;
    box-shadow: 0 2px 10px rgba(74,58,30,.05);
  }
  .rdph {
    display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap;
    margin-bottom: 8px; padding-bottom: 7px;
    border-bottom: 1px solid var(--line);
  }
  .rdph b { font-size: 13.5px; font-family: var(--font-display); }
  .rdph .rdph-fa { font-size: 11.5px; color: var(--leaf); }
  .rdph .pill {
    font-size: 9.5px; color: var(--muted); margin-inline-start: auto;
    background: var(--line); border-radius: 999px; padding: 2px 8px;
  }
  .rdnote {
    font-size: 11px; color: var(--muted); font-style: italic;
    margin: 0 0 8px; line-height: 1.55;
  }
  .rdnote .fa { display: block; font-style: normal; text-align: right; margin-top: 2px; }
  .rdpara {
    font-size: 13px; line-height: 1.75; color: var(--ink-1);
    margin: 0 0 9px; direction: ltr; text-align: left;
    max-width: 36em;
  }
  .rdpara:last-of-type { margin-bottom: 0; }
  .rdsum {
    margin-top: 10px; padding-top: 9px; border-top: 1px dashed var(--line);
  }
  .rdsum .fa { display: block; margin-top: 2px; direction: rtl; text-align: right; line-height: 2.15; }
  .rdsumbtn {
    font-family: inherit; font-size: 11.5px; cursor: pointer;
    background: none; border: 1px dashed rgba(47,107,79,.45);
    border-radius: 9px; padding: 5px 10px; color: var(--leaf);
  }
  .rdsumbtn:hover { background: var(--leaf-soft); }

  /* --- questions --- */
  .rdqhead { display: flex; align-items: center; gap: 8px; margin: 2px 0 7px; }
  .rdqhead b { font-size: 12.5px; }
  .rdqhead .n {
    font-size: 10px; color: var(--muted); background: var(--line);
    border-radius: 999px; padding: 1px 7px;
  }
  .rdqhead .fa { font-size: 11.5px; color: var(--muted); }
  .rdq { display: flex; flex-direction: column; gap: 7px; }
  .rditem {
    background: var(--surf-1); border: 1px solid var(--line);
    border-radius: 12px; padding: 10px 12px;
  }
  .rditem.right { border-color: rgba(47,107,79,.55); background: var(--surf-1); }
  .rditem.wrong { border-color: rgba(160,58,99,.5); background: var(--surf-1); }
  .rdstem { font-size: 12.5px; line-height: 1.7; color: var(--ink-1); }
  .rdnum2 {
    display: inline-grid; place-items: center; width: 17px; height: 17px;
    border-radius: 50%; font-size: 10px; font-weight: 700; margin-inline-end: 5px;
    background: rgba(47,107,79,.1); color: var(--leaf);
  }
  .rdopt {
    display: flex; align-items: flex-start; gap: 8px; width: 100%;
    text-align: start; font-family: inherit; font-size: 12px; line-height: 1.5;
    cursor: pointer; color: var(--ink);
    background: var(--surf-1); border: 1px solid var(--line);
    border-radius: 9px; padding: 6px 9px;
    transition: background .12s, border-color .12s;
  }
  .rdopt + .rdopt { margin-top: 5px; }
  .rdopt:hover { border-color: rgba(47,107,79,.5); background: var(--surf-1); }
  .rdopt .k {
    flex: 0 0 16px; font-weight: 700; color: var(--muted);
    font-size: 10.5px; text-align: center;
  }
  .rdopt.on { border-color: var(--leaf); background: var(--leaf-soft); }
  .rdopt.right { border-color: var(--leaf); background: var(--surf-2); }
  .rdopt.wrong { border-color: rgba(160,58,99,.55); background: var(--surf-2); }
  .rdopt:disabled { cursor: default; }
  .rdtf { display: flex; gap: 6px; }
  .rdtf button {
    flex: 1; font-family: inherit; font-size: 12px; cursor: pointer;
    padding: 6px 0; border-radius: 9px; color: var(--ink);
    background: var(--surf-1); border: 1px solid var(--line);
  }
  .rdtf button:hover { border-color: rgba(47,107,79,.5); }
  .rdtf button.on { background: var(--leaf-soft); border-color: var(--leaf); }
  .rdtf button.right { background: var(--surf-2); border-color: var(--leaf); }
  .rdtf button.wrong { background: var(--surf-2); border-color: rgba(160,58,99,.55); }

  .rdblank {
    font-family: inherit; font-size: 12.5px; color: var(--ink);
    background: var(--surf-1); border: none; border-bottom: 1.5px solid rgba(47,107,79,.45);
    border-radius: 3px 3px 0 0; padding: 1px 6px; min-width: 96px;
    direction: ltr; text-align: center;
  }
  .rdblank:focus { outline: none; background: var(--leaf-soft); }
  .rdblank.right { border-bottom-color: var(--leaf); background: var(--surf-2); }
  .rdblank.wrong { border-bottom-color: rgba(160,58,99,.7); background: var(--surf-2); }
  .rdhint { font-size: 10.5px; color: var(--muted); margin-top: 5px; line-height: 1.6; }
  .rdhint .fa { display: block; text-align: right; margin-top: 2px; }

  .rdfb { margin-top: 7px; font-size: 11.5px; line-height: 1.6; }
  .rdfb .ok { color: var(--leaf); font-weight: 700; }
  .rdfb .no { color: var(--rose-ink); font-weight: 700; }
  .rdfb p { margin: 2px 0 0; color: var(--ink-2); }
  .rdfb .fa { display: block; direction: rtl; text-align: right; margin-top: 2px; line-height: 2.15; }

  .rdessay { display: flex; flex-direction: column; gap: 6px; }
  .rdarea {
    font-family: inherit; font-size: 12.5px; line-height: 1.6; color: var(--ink);
    background: var(--surf-1); border: 1px solid var(--line);
    border-radius: 10px; padding: 8px 10px; resize: vertical; min-height: 74px;
    direction: ltr; text-align: left;
  }
  .rdarea:focus { outline: none; border-color: var(--leaf); background: var(--surf-1); }
  .rdessaybar { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
  .rdcount { font-size: 10.5px; color: var(--muted); }
  .rdcount.ok { color: var(--leaf); }
  .rdsmall {
    margin-inline-start: auto; font-family: inherit; font-size: 11px;
    cursor: pointer; background: none; border: 1px solid var(--line2);
    border-radius: 999px; padding: 3px 9px; color: var(--ink);
  }
  .rdsmall:hover { background: var(--line); }
  .rdtips { margin: 4px 0 0; padding: 0 0 0 2px; list-style: none; }
  /* English on the first line, Persian under it: a tip that runs
     'Name the subject: night trains. موضوع را نام ببر' turns the reader's
     eye around mid-line, which is the one thing this page refuses to do. */
  .rdtips li {
    display: flex; gap: 6px; font-size: 11px; color: var(--muted);
    line-height: 1.65; margin-bottom: 3px;
  }
  .rdtips li::before { content: '•'; color: var(--leaf); flex: none; }
  .rdtips .ten { display: block; }
  .rdtips .tfa {
    display: block; color: var(--ink-2);
    direction: rtl; text-align: right;
  }
  .rdmodel {
    margin-top: 7px; padding: 9px 11px; border-radius: 10px;
    background: var(--leaf-soft); border: 1px solid rgba(47,107,79,.22);
  }
  .rdmodel .lbl {
    font-size: 10px; letter-spacing: .08em; text-transform: uppercase;
    color: var(--leaf); font-weight: 700; margin-bottom: 4px;
  }
  .rdmodel p { margin: 0; font-size: 12px; line-height: 1.7; color: var(--ink-1); }
  .rdmodel p.fa { direction: rtl; text-align: right; margin-top: 3px; color: var(--ink-2); line-height: 2.15; }

  .rdfoot {
    display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
    padding-top: 10px; margin-top: 4px; border-top: 1px solid var(--line);
  }
  .rdgo {
    font-family: inherit; font-size: 11.5px; font-weight: 700; cursor: pointer;
    background: var(--leaf); color: var(--on-fill); border: none;
    border-radius: 999px; padding: 7px 14px;
  }
  .rdgo:hover { filter: brightness(1.1); }
  .rdgo.ghost { background: none; color: var(--leaf); border: 1px solid rgba(47,107,79,.4); }
  .rdgo.ghost:hover { background: var(--leaf-soft); }
  .rderr { font-size: 12px; color: var(--rose-ink); padding: 8px 0; }

  /* ---------- chat area ---------- */
  #chat {
    flex: 1; overflow-y: auto; padding: 22px 22px 10px;
    display: flex; flex-direction: column; gap: 16px;
    /* The transcript is its own sheet, a shade deeper than the card it sits
       in: without it the header, the conversation and the composer were one
       unbroken field of cream with three horizontal rules in it. */
    /* Shaded, not painted: a flat fill this close to the frame made the
       boundary read as a seam. The gradient goes slightly deeper downwards, so
       the conversation settles against the composer instead of floating. */
    background: linear-gradient(180deg, var(--chat-bg) 0%, var(--surf-2) 46%, var(--surf-3) 100%);
    scroll-behavior: smooth;
    /* Android's WebView keeps momentum scrolling only when asked, and the
       daily card is taller than a phone screen once its rows are open: the
       transcript has to scroll like a list, not stick under the finger. */
    -webkit-overflow-scrolling: touch;
    /* Firefox: backdrop-filter can flicker inside overflow+border-radius parents */
    overscroll-behavior: none;
  }
  #chat::-webkit-scrollbar, .domains::-webkit-scrollbar { width: 9px; }
  #chat::-webkit-scrollbar-thumb, .domains::-webkit-scrollbar-thumb {
    background: var(--surf-5); border-radius: 8px;
  }
  #chat::-webkit-scrollbar-track { background: transparent; }
  .row { display: flex; gap: 10px; align-items: flex-end; animation: pop .2s ease; }
  @keyframes pop { from { opacity: 0; transform: translateY(8px); } }
  .row.user { flex-direction: row-reverse; }
  .mav {
    width: 32px; height: 32px; border-radius: 11px; flex: none;
    display: grid; place-items: center; font-size: 16px;
    background: var(--line); border: 1px solid var(--line);
  }
  .mav svg, .mav img { width: 26px; height: 26px; display: block; }
  /* the tutor's face is a round portrait, so the tile reads as a frame */
  .mav img { border-radius: 50%; }
  .mav.bot {
    background: var(--tile-bot);
    border-color: var(--tile-bot-edge);
    /* The tutor's portrait is round, so its tile is too: a circle sitting in a
       rounded square reads as a picture that missed its frame. The picture
       fills the tile, so the gold edge is the only frame it gets. */
    border-radius: 50%;
  }
  .mav.bot img { width: 100%; height: 100%; }
  .mav.me {
    background: linear-gradient(150deg, rgba(233,229,248,.9), var(--line));
    border-color: rgba(51,82,110,.28);
  }
  /* One rule, not three. The two lavender ones above were dead - a later rule
     with the same selector always won - and the shadow that survived was the
     old indigo rgba(79,110,247): a blue glow on the calmer, warmer page. */
  /* The learner's tile is the bird's own season: paper washed in the season's
     tint, ringed in the season's edge colour. It used to be a navy block, which
     swallowed the one coloured thing drawn for the learner - at 26px the bird
     was a yellow shape on a dark square, and the colour carried no meaning. */
  .row.user .mav {
    background: radial-gradient(circle at 32% 24%, var(--surf-1) 0%,
                var(--season-wash, rgba(232,191,95,.22)) 62%, var(--surf-3) 100%);
    border: 1px solid var(--season-ring, var(--gold-line));
    box-shadow: 0 3px 10px rgba(74,58,30,.14), inset 0 1px 0 var(--raise);
  }
  .bubble-wrap { max-width: min(78%, 760px); display: flex; flex-direction: column; gap: 5px; }
  .row.user .bubble-wrap { align-items: flex-end; }
  .msg {
    position: relative;
    padding: 12px 16px; border-radius: 17px;
    /* Kalam runs narrow; 16px here reads like the 15px it replaced */
    font-size: 16px; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word;
    border: 1px solid var(--line);
  }
  /* The tutor's own bubbles carry the bird's colour. Neutral white glass made
     every reply look like a system message; the tutor is the one voice in the
     conversation and should be the one that looks like a voice. Anthropomorphic
     styling measurably raises perceived empathy and trust, and trust is what
     drives whether people stay in a tutor (Frontiers 2025, n=160). */
  .msg.bot {
    /* A gradient of two creams rather than one: a 1.5px step over a bubble's
       height is enough to round it, and it stops the wall of identical white
       cards that made a long conversation tiring to scan. The border carries
       the edge so the gradient never has to. */
    background: linear-gradient(180deg, var(--surf-1) 0%, var(--surf-2) 100%);
    color: var(--ink);
    border: 1px solid var(--line);
    border-bottom-left-radius: 6px;
    box-shadow: 0 4px 16px rgba(74,58,30,.09), inset 0 1px 0 var(--raise);
  }
  /* The gold hairline down the leading edge is gone: on a white card it read
     as a stray bookmark rather than an accent, and the corner radius already
     says which side of the conversation a bubble belongs to. */
  .msg.bot::before { display: none; }
  /* The learner's bubble carries no accent line: gold on navy reads as a
     rendering artefact, and the filled navy card already says "you". */
  .msg.user::before { display: none; }

  /* Terms the tutor is pointing at. Yellow on pink glass was the weakest
     pairing on the page; this reads at a glance and stays legible on the
     user's violet bubble too. */
  .msg b, .msg strong {
    color: var(--gold-ink); font-weight: 700;
    background: rgba(232,191,95,.34);
    border-radius: 5px; padding: 0 4px; margin: 0 -1px;
    box-shadow: inset 0 0 0 1px rgba(207,159,60,.45);
  }
  .msg.user b, .msg.user strong {
    color: var(--on-fill); background: rgba(255,255,255,.16);
    box-shadow: inset 0 0 0 1px var(--edge-light);
  }
  .msg.user {
    background: linear-gradient(135deg, var(--user1) 0%, var(--user2) 55%,
                                        var(--user3) 100%);
    color: var(--on-fill); border: none; border-bottom-right-radius: 6px;
    box-shadow: 0 6px 18px var(--line), inset 0 1px 0 var(--edge-light);
  }
  .msg.rtl { direction: rtl; text-align: right; }
  /* mixed bilingual text: each line picks its own direction */
  .msg { unicode-bidi: plaintext; text-align: start; }
  .msg b, .msg strong { color: var(--gold-ink); font-weight: 700; }
  .msg.long { max-height: 420px; overflow-y: auto; }
  /* A fox inside a bubble. 46px reads as a sticker without turning a
     one-word message into a billboard, and the negative margin keeps the
     bubble from growing a blank line above and below it. */
  .msg .stk {
    width: 46px; height: 46px; display: inline-block;
    vertical-align: -12px; margin: -2px 1px;
  }
  .meta { font-size: 10.5px; color: var(--dim); padding: 0 5px; font-weight: 500;
          display: flex; align-items: center; gap: 7px; }
  .meta i { font-style: normal; opacity: .75; }
  /* per-message tools: listen / copy */
  .tools-row { display: inline-flex; gap: 3px; margin-inline-start: auto; }
  .row.user .tools-row { display: none; }
  .mtool {
    background: none; border: 1px solid transparent; color: var(--dim);
    font-size: 12px; line-height: 1; cursor: pointer; border-radius: 6px;
    padding: 3px 5px; font-family: inherit; transition: .12s;
  }
  .mtool:hover { color: var(--text); background: var(--line);
                 border-color: var(--line); }
  @media (hover: none) {
    .mtool:hover { background: none; color: var(--dim); border-color: transparent; }
  }
  .msg.err { border-color: var(--line-strong); color: var(--red-ink); background: var(--surf-3); }

  /* ---------- the opening prompt ----------
     A greeting and an empty box is the weakest first screen a tutor can
     show: the learner has to invent a sentence before anything happens.
     Four pills name the four things this bot is actually good at, so the
     first tap is a choice rather than a guess. They live in the transcript
     and go away the moment the conversation starts. */
  .starters {
    display: flex; flex-direction: column; gap: 9px;
    padding: 2px 2px 4px 38px; animation: fade .22s ease both;
  }
  .schips { display: flex; flex-wrap: wrap; gap: 7px; }
  /* Steel blue, not paper: these are the first thing a learner can touch, and
     the one cool colour in the palette belongs on them - it is the poster's
     water against its sand. */
  .schip {
    background: var(--ice); color: var(--ice-ink);
    border: 1px solid rgba(51,82,110,.24); border-radius: 999px;
    padding: 7px 14px; font-family: var(--font-body); font-size: 14.5px;
    line-height: 1.2; cursor: pointer;
    box-shadow: 0 1px 2px rgba(74,58,30,.06);
    transition: background .15s, border-color .15s, transform .16s,
                box-shadow .18s, color .15s;
  }
  .schip:hover {
    background: var(--ice2); border-color: rgba(51,82,110,.42); color: var(--ice-ink);
    transform: translateY(-1px); box-shadow: 0 6px 14px rgba(74,58,30,.12);
  }
  .schip:active { transform: translateY(0) scale(.985); }
  .schip:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
  @media (hover: none) { .schip:hover { background: var(--ice); color: var(--ice-ink);
                                        border-color: rgba(51,82,110,.24);
                                        transform: none; box-shadow: none; } }
  @media (prefers-reduced-motion: reduce) { .starters { animation: none; } }

  /* Wrapping the transcript lets the jump button anchor to it rather than to
     the window: a bottom offset measured from the window lands on the
     composer, which is taller than any constant worth writing down. */
  .chatwrap {
    flex: 1 1 auto; position: relative; min-height: 0;
    display: flex; flex-direction: column;
    /* Opening a panel leaves this 0px tall, and #chat cannot shrink below
       its own padding - 20px top plus 10px bottom - so a 30px band of
       transcript used to paint straight over the controls beneath it.
       min-height:0 on #chat does not help: a padding box is the floor a box
       can shrink to, not a minimum-height. Clipping is the fix. The jump
       button lives in here too, and is only meaningful while the transcript
       is on screen; clipped content takes no pointer events either, so it
       cannot become an invisible target. */
    overflow: hidden;
  }

  /* scroll-to-latest — bottom centre of the transcript. Centred rather than
     over the right-hand edge, which is the usual convention: the transcript
     is a single centred reading column here, and a button on one side pulls
     the eye away from it. Carries a count of what has arrived below. */
  .jump {
    position: absolute; left: 50%; bottom: 14px; z-index: 6;
    /* -50% of its own width is exactly what centring wants. (The moon on the
       daily-limit rail is the opposite case: there a % has to resolve against
       the rail, and transform cannot do that.) */
    transform: translateX(-50%) translateY(10px) scale(.9);
    width: 44px; height: 44px;                  /* a real touch target */
    border-radius: 50%; cursor: pointer; font-size: 17px;
    display: grid; place-items: center;
    color: var(--on-fill); font-family: inherit; line-height: 1;
    background: linear-gradient(135deg, var(--fill-slate), var(--fill-navy3));
    border: 1px solid var(--line2);
    box-shadow: 0 6px 18px rgba(74,58,30,.45);
    opacity: 0; pointer-events: none;
    transition: opacity .18s, transform .18s cubic-bezier(.22,1,.36,1);
  }
  .jump.show {
    opacity: 1; pointer-events: auto;
    transform: translateX(-50%);
  }
  .jump:hover { filter: brightness(1.12); }
  /* keeps translateX(-50%) - without it the button lurches to the right
     on press, since that is the only thing centring it */
  .jump:active { transform: translateX(-50%) scale(.93); }
  .jump:focus-visible { outline: 2px solid var(--focus); outline-offset: 3px; }
  .jump svg { width: 17px; height: 17px; display: block; }

  /* ---------- practice drawer: the one way into the drills ---------------
     A circular control in the corner of the transcript that unfolds the
     activities. It is the navigation, not a second sheet: picking an item
     opens that drill as a page of its own, and closing the page folds this
     back open on the list. It is a child of .chatwrap, so it is clipped with
     the transcript when a section is open and it cannot cover the composer,
     which is a sibling below it. The jump button owns the bottom centre; this
     owns the right. */
  .prfab {
    position: absolute; right: 14px; bottom: 14px; z-index: 8;
    width: 48px; height: 48px; border-radius: 50%; cursor: pointer;
    display: grid; place-items: center; font-family: inherit; line-height: 1;
    color: var(--on-fill); border: 1px solid var(--line2);
    background: linear-gradient(135deg, var(--gold-ink), var(--fill-navy3));
    box-shadow: 0 8px 20px rgba(74,58,30,.34);
    transition: transform .18s cubic-bezier(.22,1,.36,1), filter .15s,
                box-shadow .18s;
  }
  .prfab:hover { filter: brightness(1.1); }
  .prfab:active { transform: scale(.94); }
  .prfab:focus-visible { outline: 2px solid var(--focus); outline-offset: 3px; }
  .prfab svg { width: 21px; height: 21px; display: block; }
  .prfab[aria-expanded="true"] {
    transform: rotate(90deg);
    background: linear-gradient(135deg, var(--fill-navy3), var(--fill-slate));
  }
  .prdrawer {
    position: absolute; right: 12px; bottom: 72px; z-index: 9;
    width: min(346px, calc(100% - 24px));
    max-height: calc(100% - 86px);
    display: flex; flex-direction: column;
    border: 1px solid var(--line2); border-radius: 16px;
    background: var(--surf-2);
    box-shadow: 0 18px 44px rgba(34,32,28,.30);
    transform-origin: bottom right;
    opacity: 0; visibility: hidden; pointer-events: none;
    transform: translateY(10px) scale(.97);
    transition: opacity .18s, transform .22s cubic-bezier(.22,1,.36,1),
                visibility 0s .22s;
  }
  .prdrawer.on {
    opacity: 1; visibility: visible; pointer-events: auto; transform: none;
    transition: opacity .18s, transform .22s cubic-bezier(.22,1,.36,1);
  }
  .prdhead {
    flex: none; display: flex; align-items: center; gap: 9px;
    padding: 11px 10px 11px 13px; border-bottom: 1px solid var(--line);
  }
  .prdmark {
    width: 26px; height: 26px; border-radius: 50%; flex: none;
    display: grid; place-items: center; color: var(--on-fill);
    background: linear-gradient(135deg, var(--gold-ink), var(--fill-navy3));
  }
  .prdmark svg { width: 15px; height: 15px; display: block; }
  .prdtitle {
    display: flex; align-items: baseline; gap: 6px;
    font-size: 13px; font-weight: 800; color: var(--navy2); letter-spacing: .01em;
  }
  .prdtitle .fa { font-family: var(--font-fa); font-weight: 600; color: var(--muted); }
  .prdclose {
    margin-inline-start: auto; width: 30px; height: 30px; border-radius: 50%;
    display: grid; place-items: center; cursor: pointer; font-family: inherit;
    color: var(--ink-2); background: var(--surf-1); border: 1px solid var(--line2);
    transition: background .15s, transform .15s;
  }
  .prdclose:hover { background: var(--surf-3); }
  .prdclose:active { transform: scale(.94); }
  .prdclose:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
  .prdclose svg { width: 13px; height: 13px; display: block; }

  /* One row per activity: a mark, the name in both languages, and what the
     drill actually asks. The row is the target, so it is 46px tall with the
     whole width live, not a 30px word. */
  .prdnav {
    padding: 6px; overflow: auto; overscroll-behavior: contain;
    scrollbar-width: thin; scrollbar-color: var(--surf-5) transparent;
  }
  .prdnav::-webkit-scrollbar { width: 6px; }
  .prdnav::-webkit-scrollbar-thumb { background: var(--surf-5); border-radius: 6px; }
  .prdnav::-webkit-scrollbar-track { background: transparent; }
  .prditem {
    width: 100%; display: grid; grid-template-columns: 34px 1fr 12px;
    align-items: center; gap: 10px; padding: 7px 9px; min-height: 46px;
    border: 0; border-radius: 12px; background: transparent;
    font: inherit; text-align: start; cursor: pointer; color: var(--ink);
    transition: background .14s, transform .14s;
  }
  .prditem:hover { background: var(--surf-3); }
  .prditem:active { transform: scale(.99); }
  .prditem:focus-visible { outline: 2px solid var(--focus); outline-offset: -2px; }
  .prdico {
    width: 34px; height: 34px; border-radius: 10px; flex: none;
    display: grid; place-items: center; color: var(--gold-ink);
    background: var(--gold-soft); border: 1px solid rgba(138,90,0,.14);
  }
  .prdico svg { width: 17px; height: 17px; display: block; }
  .prdtxt { display: flex; flex-direction: column; gap: 1px; min-width: 0; }
  .prden {
    display: flex; align-items: baseline; gap: 6px; min-width: 0;
    font-size: 12.5px; font-weight: 750; color: var(--navy2); line-height: 1.3;
  }
  .prden .fa {
    font-family: var(--font-fa); font-weight: 500; font-size: 11px;
    color: var(--muted); white-space: nowrap;
  }
  .prdsub {
    font-size: 11px; line-height: 1.45; color: var(--dim);
    /* one line, clipped rather than wrapped: a row that grows to three lines
       makes the list a paragraph */
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }
  .prdchev { width: 12px; height: 12px; color: var(--ink-4); }
  .prdfoot {
    flex: none; margin: 0; padding: 8px 13px 10px; border-top: 1px solid var(--line);
    font-size: 10.5px; line-height: 1.5; color: var(--dim);
  }
  .prdfoot .fa { font-family: var(--font-fa); display: block; }
  /* The list arrives in order, a few milliseconds apart, so the eye is led down
     it instead of being handed six rows at once. */
  .prdrawer.on .prditem {
    animation: prdIn .2s cubic-bezier(.22,1,.36,1) both;
    animation-delay: calc(var(--i, 0) * 18ms);
  }
  @keyframes prdIn {
    from { opacity: 0; transform: translateY(4px); }
    to { opacity: 1; transform: none; }
  }
  @media (prefers-reduced-motion: reduce) {
    .prfab, .prdrawer, .prdrawer.on, .prditem, .prdclose { transition: none; }
    .prdrawer.on .prditem { animation: none; }
  }

  /* typing indicator */
  .typing { display: inline-flex; gap: 5px; padding: 13px 16px !important; }
  .typing span {
    width: 7px; height: 7px; border-radius: 50%; background: var(--muted);
    animation: bounce 1.2s infinite;
  }
  .typing span:nth-child(2) { animation-delay: .15s; }
  .typing span:nth-child(3) { animation-delay: .3s; }
  @keyframes bounce { 30% { transform: translateY(-6px); opacity: 1; } }

  /* ---------- input ---------- */
  form {
    /* --fgap is the same number as the gap, named because the fox's band sits
       on the box's lip: it has to cancel the space between them exactly, and
       there is no other way to reach a gap from an item. */
    --fgap: 10px;
    display: flex; gap: var(--fgap); padding: 14px 20px 18px;
    /* the sand rises from the floor of the app, the way the poster's band
       closes its card at the bottom */
    background: linear-gradient(0deg, rgba(235,226,183,.6), rgba(235,226,183,0));
    flex: none;
  }
  /* The box is the field now. The input used to carry its own border, focus
     ring and background, which drew a second outline inside the first. It is
     bare now and .messageBox:focus-within does the talking. */
  #input {
    flex: 1; background: transparent; border: 0;
    padding: 0 2px; color: var(--text);
    font-size: 16px; outline: none; transition: .15s;
    font-family: inherit;
  }
  #input::placeholder { color: var(--ink-4); }
  /* ---------- the message box ----------
     The shape is borrowed from a plain chat composer: one rounded container
     with the controls inside it rather than a row of separate pills. The
     greys are the app's own - the shell is the same paper as the panels, and
     the focus ring is the theme's gold, so typing into it reads the same way
     as the rest of the page lighting up.
  */
  .messageBox {
    display: flex; align-items: center; gap: 4px;
    padding: 3px 4px 3px 6px; border-radius: 999px;
    background: linear-gradient(180deg, var(--surf-1) 0%, var(--surf-2) 100%);
    border: 1px solid rgba(205,159,60,.34);
    box-shadow: 0 2px 8px rgba(74,58,30,.08), inset 0 1px 0 var(--raise),
                0 8px 20px -18px var(--line);
    transition: border-color .18s, box-shadow .18s;
  }
  .messageBox:focus-within {
    border-color: rgba(60,64,91,.45);
    box-shadow: 0 0 0 4px rgba(232,191,95,.30), 0 2px 10px rgba(74,58,30,.10);
  }
  /* ---------- the fox in the send box -----------------------------------
     She is not beside the composer, she is inside it: the band above the pill
     is the hole she climbs out of, its bottom edge is the pill's top edge,
     and the band clips. Whatever is still in the box is simply not drawn, so
     the head that shows is the part that has risen - no floating portrait,
     no second avatar.

     The band is a fixed height, so the climb is a transform: no layout shift,
     nothing pushed, and it cannot cover the input, the buttons or a message -
     the transcript ends above it. It hangs on the form rather than on the
     window, so it leaves with the composer when a section is open. */
  .foxslot {
    position: relative; flex: none;
    /* Its bottom edge must be the box's top edge, and the form's own gap sits
       between the two: the negative margin is that gap, cancelled, so the clip
       line is the lip of the box and not a band above it. */
    height: 46px; margin: 0 0 calc(-1 * var(--fgap, 10px));
    overflow: hidden; pointer-events: none;
  }
  .foxpeek {
    position: absolute; inset: 0;
    transform: translateY(100%);
    transition: transform .62s cubic-bezier(.22,.9,.3,1);
  }
  /* Risen. Everything else - the bob, the look around, the blink - is an
     animation inside it, so none of them fights the climb for `transform`. */
  .foxpeek.on { transform: none; }
  .foxshade {
    position: absolute; left: 26px; bottom: -4px; width: 64px; height: 12px;
    border-radius: 50%;
    background: radial-gradient(50% 50% at 50% 50%,
                var(--ghost-halo), rgba(255,255,255,0) 74%);
  }
  /* Left 30px, not 12: the pill's corner is a 26px radius, so anything nearer
     the end would end above the curve rather than above the box, and the cut
     at her chin would show daylight instead of the lip she is climbing out
     of. Past the curve the top edge is flat, and the cut reads as the box. */
  .foxhead {
    position: absolute; left: 30px; bottom: -14px;
    width: 58px; height: 58px; transform-origin: 50% 100%;
    animation: foxBob 6.5s ease-in-out infinite;
  }
  /* No drop-shadow: a filter on an animated element is re-rasterised every
     frame, which is the note the boot card's cut-out already carries. Her
     glow is therefore painted rather than filtered - a radial gradient behind
     the body, and a mint line round it - so the whole drawing is one cheap
     SVG that the bob can move without repainting. */
  .foxpic {
    width: 100%; height: 100%; display: block;
    transform-origin: 50% 92%;
    animation: foxLook 11.3s ease-in-out infinite;
  }
  /* A ghost, in three strokes: white body, one green line, and a face made of
     two eyes, a nose and a smile - no fur, no hat, no colour but these. */
  .foxghost {
    fill: var(--ghost-body); stroke: var(--ghost-line); stroke-width: 1.6;
    stroke-linejoin: round; stroke-linecap: round;
  }
  .foxglow .g1 { stop-color: var(--ghost-body); stop-opacity: .9; }
  .foxglow .g2 { stop-color: var(--ghost-line); stop-opacity: .34; }
  .foxglow .g3 { stop-color: var(--ghost-line); stop-opacity: 0; }
  .foxeyes { fill: var(--ghost-ink); transform-box: view-box;
             transform-origin: 30px 32.4px;
             animation: foxBlink 6.8s ease-in-out infinite; }
  .foxnose { fill: var(--ghost-line); }
  .foxsmile { fill: none; stroke: var(--ghost-line); stroke-width: 1.4;
              stroke-linecap: round; opacity: .85; }
  @keyframes foxBob {
    0%, 100% { transform: translateY(0) rotate(0); }
    50%      { transform: translateY(-1.6px) rotate(0); }
    /* Once a cycle, a flick of a degree and a half. Her ears are part of the
       picture, so the whole head twitches - at this size that is read as the
       ears, and it is the only motion here that is over in a fifth of a
       second. */
    62%      { transform: translateY(-1.6px) rotate(-1.5deg); }
    66%      { transform: translateY(-1.5px) rotate(1.1deg); }
    70%      { transform: translateY(-1.4px) rotate(0); }
  }
  /* Slow, and mostly still: a companion that looks around on a loop is a gif,
     one that glances every eleven seconds is alive. */
  @keyframes foxLook {
    0%, 38%, 64%, 100% { transform: rotate(0); }
    45%  { transform: rotate(-3deg); }
    52%  { transform: rotate(0); }
    55%  { transform: rotate(2.4deg); }
    60%  { transform: rotate(0); }
  }
  /* The eyes are hers now, so the blink is the eyes closing: two small ovals
     squashed to a line and opened again, on the same slow cycle as the look
     around. */
  @keyframes foxBlink {
    0%, 86%, 100% { transform: scaleY(1); }
    89%, 93%      { transform: scaleY(.12); }
  }
  /* A message goes out: she nods, once, and settles back to the bob. */
  .foxhead.nod { animation: foxNod .52s cubic-bezier(.3,1.6,.5,1); }
  @keyframes foxNod {
    0%   { transform: translateY(0) rotate(0); }
    32%  { transform: translateY(4px) rotate(2.5deg); }
    70%  { transform: translateY(-2px) rotate(-1.6deg); }
    100% { transform: translateY(0) rotate(0); }
  }
  /* Dictation opens its own box directly above this one, and she would sit on
     the words: she ducks until it is gone. */
  body.stt-open .foxpeek { transform: translateY(100%); }
  @media (max-width: 560px) {
    .foxslot { height: 42px; }
    .foxhead { left: 28px; width: 54px; height: 54px; bottom: -14px; }
    .foxshade { left: 22px; width: 60px; }
  }
  /* The animation block below switches the app's motion off wholesale; these
     are listed there too. She stays - a still fox in the corner of the box is
     the point of the design - she just does not move. */
  @media (prefers-reduced-motion: reduce) {
    .foxpeek { transition: none; }
    .foxhead, .foxpic, .foxeyes, .foxhead.nod { animation: none; }
  }
  .ico {
    flex: 0 0 auto; width: 36px; height: 36px; padding: 0;
    display: grid; place-items: center; border: 0; border-radius: 10px;
    background: transparent; color: var(--muted); cursor: pointer;
    transition: background .16s, color .16s, transform .16s cubic-bezier(.22,1,.36,1);
  }
  .ico svg { width: 19px; height: 19px; }
  .ico:hover { background: var(--line); color: var(--ink); }
  .ico:active { transform: scale(.9); }
  .ico:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
  #stickerbtn[aria-expanded="true"] { background: var(--ice); color: var(--ice-ink); }
  /* Round, because it sits inside a pill. A 12px rectangle in a 999px
     capsule looked like a button that had been dropped in. */
  .send {
    flex: 0 0 auto; width: 38px; height: 38px; padding: 0;
    display: grid; place-items: center;
    background: linear-gradient(150deg, var(--send-1) 0%, var(--fill-slate) 100%);
    border: 0; border-radius: 50%; color: var(--on-fill); cursor: pointer;
    transition: filter .15s, transform .16s cubic-bezier(.22,1,.36,1),
                box-shadow .18s;
    box-shadow: 0 2px 8px rgba(60,64,91,.28), inset 0 1px 0 var(--edge-light);
    font-family: inherit;
  }
  .send svg { width: 18px; height: 18px; }
  .send:hover { filter: brightness(1.1); transform: translateY(-1px);
                box-shadow: 0 5px 14px rgba(60,64,91,.32), inset 0 1px 0 var(--edge-light); }
  .send:disabled { opacity: .55; cursor: not-allowed; transform: none; }

  /* ---------- phrases panel pills ---------- */
  .ftopic {
    background: var(--ice); color: var(--ice-ink);
    border: 1px solid rgba(51,82,110,.22);
    border-radius: 999px; padding: 6px 13px; font-size: 12.5px; font-weight: 500;
    cursor: pointer; transition: .15s; white-space: nowrap;
    display: inline-flex; align-items: baseline; gap: 6px;
  }
  .ftopic:hover { background: var(--ice2); transform: translateY(-1px); }
  .ftopic .fa { color: var(--muted); font-size: 11.5px; }

  /* ---------- word architecture: clickable chips + detail card ---------- */
  .wd-slot { margin-top: 9px; padding-top: 9px;
             border-top: 1px dashed var(--line); }
  .wd-lab {
    font-size: 10.5px; letter-spacing: .04em; color: var(--ink-3);
    font-weight: 600; margin-bottom: 6px;
  }
  .wd-lab b { color: var(--muted); font-weight: 400; }
  .wd-chips { display: flex; flex-wrap: wrap; gap: 4px; }
  .wchip {
    background: rgba(79,70,160,.10); color: var(--navy-ink);
    border: 1px solid rgba(79,70,160,.28); border-radius: 7px;
    padding: 4px 9px; font-size: 11.5px; cursor: pointer;
    transition: .12s; font-family: inherit;
  }
  .wchip:hover { background: rgba(79,70,160,.18); color: var(--navy-ink);
                 border-color: rgba(79,70,160,.55); }
  .wchip.on { background: linear-gradient(135deg, var(--indigo-ink), var(--fill-slate));
              color: var(--on-fill); border-color: transparent; }
  .wd-more { font-size: 10.5px; color: var(--dim); margin-top: 5px; }
  .wd-more.btn {
    background: var(--line); border: 1px solid var(--line);
    border-radius: 8px; padding: 5px 10px; cursor: pointer;
    font-family: inherit; color: var(--muted);
  }
  .wd-more.btn:hover { background: var(--line); color: var(--text); }

  .wdetail {
    display: none; margin-bottom: 11px; padding: 12px;
    border-radius: 13px; position: relative;
    background: linear-gradient(150deg, rgba(79,70,160,.14), rgba(60,64,91,.10));
    border: 1px solid rgba(79,70,160,.34);
    box-shadow: 0 6px 20px rgba(74,58,30,.28), inset 0 1px 0 var(--line);
    animation: pop .18s ease;
  }
  .wdetail.open { display: block; }
  .wd-head { display: flex; align-items: center; gap: 9px; }
  .wd-word {
    flex: 1; min-width: 0; font-size: 19px; font-weight: 700;
    letter-spacing: .2px; display: flex; align-items: baseline;
    gap: 7px; flex-wrap: wrap; line-height: 1.25;
  }
  .wd-pos {
    font-size: 9.5px; font-weight: 700; padding: 2px 6px; border-radius: 5px;
    background: var(--line2); color: var(--ink-2);
  }
  .wd-close {
    background: none; border: none; color: var(--dim); cursor: pointer;
    font-size: 12px; padding: 2px 5px; border-radius: 6px; line-height: 1;
    font-family: inherit;
  }
  .wd-close:hover { color: var(--text); background: var(--line); }
  .wd-mean {
    font-size: 14px; line-height: 1.6; margin: 7px 0 4px; color: var(--text);
  }
  .wd-mean b { color: var(--indigo-ink); }
  .wd-forms {
    display: grid; grid-template-columns: 1fr; gap: 4px; margin-top: 5px;
  }
  .wd-form {
    display: flex; align-items: baseline; gap: 8px;
    padding: 6px 9px; border-radius: 8px;
    background: var(--line); border: 1px solid var(--line);
  }
  .wd-form b {
    font-family: "SF Mono", Consolas, "DejaVu Sans Mono", monospace;
    font-size: 13px; color: var(--gold-ink); font-weight: 700; flex: none;
    min-width: 104px;
  }
  .wd-form i { font-style: normal; font-size: 11px; color: var(--muted); }
  .wd-meta { font-size: 10.5px; color: var(--dim); margin-top: 8px; }
  @media (min-width: 600px) {
    .wd-forms { grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); }
    .wd-word { font-size: 21px; }
  }
  @media (max-width: 420px) {
    .wd-form b { min-width: 92px; font-size: 12.5px; }
  }

  /* ---------- weekly quiz: the week's card, and the paper behind it ------
     The daily card is the day; this is the week, and it is deliberately the
     same object one size up: a card in the transcript, an indigo rule instead
     of a gold one so the two are told apart at a glance, and a sheet that
     opens over the page for the questions themselves. */
  .wqcard {
    position: relative; overflow: hidden; flex: 0 0 auto;
    max-width: 980px; width: 100%; margin: 2px auto 10px;
    border-radius: 18px; border: 1px solid rgba(79,70,160,.26);
    background: var(--card);
    box-shadow:
      0 1px 0 var(--edge-light) inset,
      0 2px 5px rgba(74,58,30,.055),
      0 20px 38px -26px rgba(74,58,30,.75);
    font-family: var(--font-body);
  }
  .wqcard::before {
    content: ""; position: absolute; inset: 0 0 auto; height: 3px; z-index: 1;
    background: linear-gradient(90deg, var(--indigo), var(--violet) 46%, var(--surf-4));
  }
  .wqhead {
    display: flex; align-items: flex-start; gap: 9px;
    padding: 13px 12px 9px 14px;
    background: radial-gradient(130% 160% at 0% 0%, rgba(107,91,210,.20), transparent 64%),
      linear-gradient(180deg, var(--surf-2), var(--surf-3));
  }
  .wqico {
    width: 28px; height: 28px; border-radius: 9px; flex: none;
    display: grid; place-items: center;
    background: linear-gradient(180deg, var(--surf-3), var(--ice));
    border: 1px solid rgba(79,70,160,.26); color: var(--indigo);
    box-shadow: 0 1px 2px rgba(79,70,160,.14);
  }
  .wqico svg { width: 16px; height: 16px; }
  .wqtitle {
    font-family: var(--font-display); font-size: 14px; font-weight: 700;
    color: var(--navy2); line-height: 1.25; letter-spacing: .1px;
  }
  .wqtitle small {
    display: block; font-family: var(--font-body); font-size: 10px;
    font-weight: 400; color: var(--muted); margin-top: 2px;
  }
  .wqhead .spacer { flex: 1 1 auto; }
  .wqscore {
    font-family: var(--font-display); font-size: 12px; font-weight: 700;
    color: var(--indigo); background: rgba(74,79,160,.12);
    border: 1px solid rgba(74,79,160,.24); border-radius: 999px;
    padding: 3px 9px; white-space: nowrap; font-variant-numeric: tabular-nums;
  }
  .wqline {
    margin: 11px 14px 0; font-size: 12.5px; line-height: 1.5; color: var(--ink-2);
  }
  .wqline b { color: var(--navy2); }
  .wqfa {
    margin: 4px 14px 0; font-family: var(--font-fa); font-size: 12px;
    line-height: 1.65; color: var(--muted);
  }
  .wqmeta {
    margin: 9px 14px 0; font-size: 10.5px; font-weight: 700; letter-spacing: .2px;
    color: var(--indigo); font-variant-numeric: tabular-nums;
  }
  .wqnote {
    margin: 8px 14px 0; font-size: 12px; line-height: 1.55; color: var(--ink-2);
  }
  .wqnote.fa { font-family: var(--font-fa); font-size: 11.5px; color: var(--muted); }
  .wqacts { display: flex; flex-wrap: wrap; gap: 8px; padding: 11px 14px 13px; }
  .wqbtn {
    font: inherit; font-size: 12.5px; font-weight: 700; cursor: pointer;
    display: inline-flex; align-items: center; gap: 7px;
    border-radius: 12px; padding: 9px 14px; border: 1px solid transparent;
    background: var(--indigo); color: var(--on-fill);
    box-shadow: 0 8px 18px -12px rgba(74,79,160,.9);
  }
  .wqbtn.ghost {
    background: transparent; color: var(--ink-2);
    border-color: var(--line2); box-shadow: none;
  }
  .wqbtn bdi { font-family: var(--font-fa); font-size: 11px; font-weight: 400; opacity: .85; }
  .wqbtn:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
  @media (max-width: 520px) {
    .wqacts .wqbtn { flex: 1 1 auto; justify-content: center; }
  }

  /* ---- the paper: the same sheet the level check uses ------------------ */
  .wq-wrap { display: flex; flex-direction: column; gap: 11px; max-width: 660px; margin: 0 auto; }
  .wq-top {
    position: sticky; top: 0; z-index: 3; margin: 0;
    padding: 8px 0 9px; background: var(--surf-1);
    border-bottom: 1px solid var(--line);
  }
  .wq-toprow {
    display: flex; align-items: baseline; flex-wrap: wrap; gap: 4px 8px;
    margin-bottom: 6px;
  }
  .wq-toprow .spacer { flex: 1 1 auto; }
  .wq-chip {
    font-size: 10.5px; font-weight: 800; letter-spacing: .5px;
    text-transform: uppercase; color: var(--indigo);
    background: rgba(74,79,160,.12); border-radius: 999px; padding: 3px 9px;
  }
  .wq-chip.ghost { color: var(--muted); background: rgba(43,48,73,.07); }
  .wq-x {
    font: inherit; font-size: 13px; line-height: 1; cursor: pointer;
    width: 26px; height: 26px; border-radius: 8px; border: 1px solid var(--line);
    background: var(--surf-2); color: var(--muted); align-self: center;
  }
  .wq-bar {
    height: 4px; border-radius: 999px; overflow: hidden;
    background: var(--line); box-shadow: inset 0 1px 2px var(--line);
  }
  .wq-bar i {
    display: block; height: 100%; border-radius: 999px;
    background: linear-gradient(90deg, var(--indigo), var(--violet));
    transition: width .3s cubic-bezier(.22,1,.36,1);
  }
  .wq-q {
    background: var(--card); border: 1px solid var(--line);
    border-radius: 16px; padding: 14px 14px 12px;
    box-shadow: 0 1px 0 var(--edge-light) inset, 0 2px 5px rgba(74,58,30,.05);
  }
  .wq-prompt {
    margin: 0 0 4px; font-size: 14.5px; line-height: 1.55; color: var(--navy2);
    font-family: var(--font-display); font-weight: 600;
  }
  .wq-prompt.fa {
    font-family: var(--font-fa); font-weight: 400; font-size: 12.5px;
    color: var(--muted); line-height: 1.7;
  }
  .wq-opts { display: flex; flex-direction: column; gap: 7px; margin-top: 11px; }
  .wq-opt {
    display: flex; align-items: flex-start; gap: 9px; text-align: left;
    font: inherit; font-size: 13px; line-height: 1.45; cursor: pointer;
    padding: 9px 11px; border-radius: 12px;
    border: 1px solid var(--line2); background: var(--surf-1); color: var(--ink);
    transition: border-color .14s ease, background .14s ease;
  }
  .wq-opt:hover { background: var(--surf-2); }
  .wq-opt.on {
    border-color: var(--indigo); background: rgba(74,79,160,.10); color: var(--navy2);
    box-shadow: 0 0 0 1px rgba(74,79,160,.35) inset;
  }
  .wq-opt:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
  .wq-letter {
    flex: none; width: 20px; height: 20px; border-radius: 7px;
    display: grid; place-items: center; font-size: 10.5px; font-weight: 800;
    background: var(--line); color: var(--ink-2);
  }
  .wq-opt.on .wq-letter { background: var(--indigo); color: var(--on-fill); }
  /* a drill is marked straight away: the right option and the one that was
     chosen, so a miss teaches the answer without a second screen */
  .wq-opt.right {
    border-color: var(--success); background: rgba(45,122,79,.10); color: var(--navy2);
  }
  .wq-opt.wrong {
    border-color: var(--red); background: rgba(178,60,48,.09); color: var(--navy2);
  }
  .wq-text { flex: 1 1 auto; }
  .wq-foot {
    position: sticky; bottom: 0; z-index: 3; margin-top: 12px;
    display: flex; align-items: center; gap: 8px;
    padding: 9px 0 10px; background: var(--surf-1);
    border-top: 1px solid var(--line); flex-wrap: wrap;
  }
  .wq-foot .wq-note { flex: 1 1 auto; font-size: 10.5px; color: var(--muted); }
  .wq-foot .lv-btn[disabled] { opacity: .45; cursor: default; }
  .wq-hero {
    border-radius: 16px; padding: 16px 15px;
    border: 1px solid var(--line);
    background: radial-gradient(120% 90% at 100% 0%, rgba(107,91,210,.12), transparent 58%),
      linear-gradient(160deg, var(--surf-1), var(--surf-1) 70%, var(--surf-2));
    box-shadow: 0 10px 26px -20px var(--line2);
  }
  .wq-eyebrow {
    font-size: 10px; letter-spacing: .15em; text-transform: uppercase;
    color: var(--indigo); font-weight: 700; margin-bottom: 7px;
  }
  .wq-h {
    font-family: var(--font-display); font-size: 18px; font-weight: 700;
    color: var(--navy2); margin: 0 0 6px; line-height: 1.3;
  }
  .wq-sub { margin: 0 0 5px; font-size: 12.5px; line-height: 1.6; color: var(--ink-2); }
  .wq-fa {
    margin: 0 0 6px; font-family: var(--font-fa); font-size: 12px;
    line-height: 1.75; color: var(--muted);
  }
  .wq-score {
    display: flex; align-items: baseline; gap: 8px; margin: 2px 0 8px;
  }
  .wq-score b {
    font-family: var(--font-display); font-size: 34px; line-height: 1;
    color: var(--indigo);
  }
  .wq-score span { font-size: 12px; color: var(--muted); }
  .wq-score em {
    font-style: normal; font-size: 11px; font-weight: 800;
    color: var(--indigo); background: rgba(74,79,160,.12);
    border-radius: 999px; padding: 3px 9px; margin-inline-start: auto;
  }
  .wq-actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
  .wq-h4 {
    font-family: var(--font-display); font-size: 12px; font-weight: 700;
    letter-spacing: .1em; text-transform: uppercase; color: var(--muted);
    margin: 4px 0 0;
  }
  .wq-miss {
    border: 1px solid var(--line); border-inline-start: 3px solid var(--red);
    border-radius: 12px; background: var(--surf-1); padding: 10px 12px;
  }
  .wq-missq { margin: 0 0 5px; font-size: 12.5px; line-height: 1.5; color: var(--navy2); font-weight: 600; }
  .wq-said { margin: 0 0 2px; font-size: 12px; color: var(--red); }
  .wq-right { margin: 0 0 4px; font-size: 12.5px; color: var(--success); font-weight: 700; }
  .wq-detail { margin: 0; font-size: 11.5px; line-height: 1.55; color: var(--muted); }
  .wq-detail.fa { font-family: var(--font-fa); line-height: 1.75; }

  /* ---------- practice: the drills that share one sheet ----------------
     Same card and same question parts as the weekly quiz, because a second
     visual language for "answer this" would be a second thing to learn. The
     practice card is told apart by its gold rule, and by nothing else. */
  .prcard::before {
    background: linear-gradient(90deg, var(--gold), var(--gold2) 46%, var(--surf-4));
  }
  /* The drills are a page now, so they take a reading column wide enough for a
     sentence and its options without the eye travelling the whole window. */
  .prwrap { display: flex; flex-direction: column; gap: 10px; max-width: 760px; margin: 0 auto; }
  .prtabs { display: flex; flex-wrap: wrap; gap: 6px; }
  /* The way back to the drawer, at the top of every drill page. */
  .prback {
    align-self: flex-start; display: inline-flex; align-items: center; gap: 6px;
    font: inherit; font-size: 12px; font-weight: 700; cursor: pointer;
    padding: 6px 12px 6px 9px; border-radius: 999px;
    border: 1px solid var(--line2); background: var(--surf-1); color: var(--ink-2);
    transition: background .15s, border-color .15s;
  }
  .prback:hover { background: var(--surf-3); border-color: rgba(138,90,0,.34); }
  .prback:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
  .prback svg { width: 13px; height: 13px; display: block; }
  .prback .fa { font-family: var(--font-fa); font-weight: 600; color: var(--muted); }
  .prtab {
    font: inherit; font-size: 11.5px; font-weight: 700; cursor: pointer;
    padding: 6px 11px; border-radius: 999px;
    border: 1px solid var(--line2); background: var(--surf-1); color: var(--ink-2);
  }
  .prtab.on {
    background: var(--gold-soft); border-color: rgba(138,90,0,.38); color: var(--gold-ink);
  }
  .prtab:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
  .prtype {
    width: 100%; min-height: 68px; resize: vertical; margin-top: 10px;
    font: inherit; font-size: 13.5px; line-height: 1.55; padding: 10px 11px;
    border-radius: 12px; border: 1px solid var(--line2);
    background: var(--surf-1); color: var(--ink);
  }
  .prtype:focus-visible { outline: 2px solid var(--focus); outline-offset: 1px; }
  .prdiff {
    display: flex; flex-wrap: wrap; gap: 4px 7px; margin-top: 10px;
    font-size: 13px; line-height: 1.9;
  }
  .prdiff .w { padding: 1px 5px; border-radius: 6px; background: rgba(45,122,79,.13); }
  .prdiff .w.miss { background: rgba(178,60,48,.14); text-decoration: underline wavy rgba(178,60,48,.55); }
  .prmic {
    font: inherit; font-size: 12.5px; font-weight: 700; cursor: pointer;
    display: inline-flex; align-items: center; gap: 7px;
    padding: 8px 13px; border-radius: 12px; border: 1px solid var(--line2);
    background: var(--surf-2); color: var(--navy2);
  }
  .prmic.rec { background: rgba(178,60,48,.12); border-color: rgba(178,48,.4); }
  .prnote { margin: 0; font-size: 11.5px; line-height: 1.6; color: var(--muted); }
  .prnote.fa { font-family: var(--font-fa); line-height: 1.8; }

  /* the four verdicts in the review queue: equal buttons, no "right" one */
  .rgrade { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; }
  .rgrade .rbtn { font-size: 12px; }
  .rprog-line {
    margin: 8px 0 0; font-size: 11.5px; line-height: 1.6; color: var(--muted);
    font-variant-numeric: tabular-nums;
  }

  /* what keeps slipping, in the account panel */
  .ac-slip { display: flex; flex-direction: column; gap: 6px; }
  .ac-sliprow {
    display: flex; align-items: center; gap: 9px; flex-wrap: wrap;
    padding: 8px 10px; border-radius: 11px;
    border: 1px solid var(--line); background: var(--surf-1);
  }
  .ac-sliprow .n {
    font-family: var(--font-display); font-size: 12px; font-weight: 700;
    color: var(--navy2); flex: 1 1 120px; min-width: 0;
  }
  .ac-sliprow .n i {
    display: block; font-style: normal; font-family: var(--font-fa);
    font-size: 10.5px; color: var(--muted);
  }
  .ac-sliprow .c {
    font-size: 11px; font-weight: 800; color: var(--red);
    background: rgba(178,60,48,.10); border-radius: 999px; padding: 2px 8px;
    font-variant-numeric: tabular-nums;
  }
  .ac-sliprow button {
    font: inherit; font-size: 11.5px; font-weight: 700; cursor: pointer;
    padding: 6px 10px; border-radius: 9px; border: 1px solid var(--line2);
    background: var(--surf-2); color: var(--ink-2);
  }
  .ac-slip .empty { font-size: 12px; color: var(--muted); }

  /* ---------- daily english: word, expression, conversation ----------
     Three cards, one per daily item. Everything is built from the page's own
     tokens, so the panel follows the theme rather than inventing a second
     one, and the grid collapses to a single column on a phone, which is where
     most of these are read. */
  .dhead {
    display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
    margin: 0 0 10px;
  }
  .ddate {
    font-family: var(--font-display); font-size: 12px; font-weight: 700;
    color: var(--gold-ink); padding: 3px 9px; border-radius: 999px;
    background: var(--gold-soft); border: 1px solid rgba(138,90,0,.2);
    letter-spacing: .2px;
  }
  .dtrack {
    flex: 1 1 80px; height: 7px; border-radius: 999px; overflow: hidden;
    background: var(--line); border: 1px solid var(--line);
  }
  .dtrack i {
    display: block; height: 100%; width: 0; border-radius: 999px;
    background: linear-gradient(90deg, var(--gold), var(--gold2));
    transition: width .35s cubic-bezier(.22,1,.36,1);
  }
  .dcount {
    font-size: 10.5px; font-weight: 800; color: var(--muted);
    white-space: nowrap;
  }
  .dcards { display: grid; grid-template-columns: 1fr; gap: 10px; }
  .dcard {
    background: var(--card); border: 1px solid var(--line);
    border-radius: 14px; padding: 11px 12px 10px;
    box-shadow: 0 1px 2px rgba(74,58,30,.06);
  }
  .dcard.done { border-color: rgba(79,70,160,.4); }
  .dtop { display: flex; align-items: center; gap: 7px; margin-bottom: 7px; }
  .dico {
    width: 22px; height: 22px; border-radius: 7px; flex: none;
    display: grid; place-items: center; font-size: 12px;
    background: var(--ice); color: var(--ice-ink);
  }
  .dkind {
    font-family: var(--font-display); font-size: 12.5px; font-weight: 700;
    color: var(--navy2); line-height: 1.2;
  }
  .dkind small {
    font-family: var(--font-body); font-size: 10px; font-weight: 400;
    color: var(--muted); display: block;
  }
  .dtop .spacer { flex: 1 1 auto; }
  .dlvl, .dreg {
    font-size: 9.5px; font-weight: 800; padding: 2px 6px; border-radius: 5px;
    letter-spacing: .3px; white-space: nowrap;
  }
  .dlvl { background: var(--line2); color: var(--ink-2); }
  .dreg { background: rgba(110,90,168,.14); color: var(--blue-ink); }
  .dword {
    font-family: var(--font-display); font-size: 21px; font-weight: 700;
    color: var(--navy2); line-height: 1.15; word-break: break-word;
  }
  .dipa {
    font-family: "SF Mono", Consolas, "DejaVu Sans Mono", monospace;
    font-size: 12px; color: var(--amber); margin-inline-start: 6px;
  }
  .dpos { font-size: 10px; color: var(--dim); font-style: italic; }
  /* Persian inside an English page: the browser needs to be told twice -
     once for the paragraph direction and once so a line that starts with a
     Latin word still ends where it should. */
  .dfa, .dline.fa, .dbubble .dfa {
    direction: rtl; text-align: right; unicode-bidi: plaintext;
    /* Tahoma is the theme's declared Persian face; the body's handwriting
       font also claims Arabic glyphs, and at 12px they read as a wobble. */
    font-family: var(--font-fa);
  }
  .dfa { font-size: 13px; color: var(--text); line-height: 2.2; margin-top: 0; }
  .dline { font-size: 13px; color: var(--text); line-height: 1.5; }
  .dline.fa { font-size: 12.5px; color: var(--muted); line-height: 2.15; }
  .dlabel {
    font-size: 9.5px; font-weight: 800; letter-spacing: .5px;
    text-transform: uppercase; color: var(--dim); margin-top: 9px;
  }
  .drow { display: flex; align-items: flex-start; gap: 7px; margin-top: 6px; }
  .drow .grow { flex: 1 1 auto; min-width: 0; }
  .dquote {
    font-family: var(--font-display); font-size: 15.5px; font-weight: 600;
    color: var(--navy2); line-height: 1.3;
  }
  .dex { display: grid; gap: 5px; margin-top: 5px; }
  .dex .exrow {
    display: flex; align-items: flex-start; gap: 7px;
    padding: 6px 8px; border-radius: 9px;
    background: var(--line); border: 1px solid var(--line);
  }
  .dex .n {
    flex: none; font-size: 10px; font-weight: 800; color: var(--dim);
    padding-top: 3px;
  }
  .dchips { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 6px; }
  .dchip {
    font-size: 10.5px; padding: 3px 8px; border-radius: 999px;
    background: var(--ice); color: var(--ice-ink);
  }
  .dchip b { font-weight: 700; }
  .dturns { display: grid; gap: 6px; margin-top: 7px; }
  .dturn { display: grid; grid-template-columns: auto 1fr; gap: 8px; }
  .dwho {
    font-size: 10.5px; font-weight: 800; color: var(--navy);
    min-width: 56px; padding-top: 5px; word-break: break-word;
  }
  .dbubble {
    padding: 6px 9px; border-radius: 3px 11px 11px 11px; min-width: 0;
    background: var(--line); border: 1px solid var(--line);
  }
  .dturn.alt .dbubble { background: var(--ice); border-color: rgba(51,82,110,.18); }
  .dbubble .dfa { font-size: 12px; color: var(--muted); margin-top: 2px; }
  /* Every Persian line on a card is .dfa, so that one selector is the whole
     toggle. It used to say .fa, which matched nothing the renderer emits -
     the button flipped its label and hid nothing at all. */
  .dcard.persian-off .dfa { display: none; }

  /* ---------- Today's English inside the conversation ----------
     The daily set is a container in the transcript rather than a panel: one
     small card a day, three rows, skip it or switch it off, and the whole
     thing stays somewhere between the chat and the top bar instead of being
     a page of its own. */
  /* The container itself. It had no rule at all when the card first shipped:
     every row was styled and the box around them was not, so the card
     inherited the transcript's handwriting face with no padding, border or
     background and read as loose text wedged into the conversation. */
  .dinline {
    position: relative; overflow: hidden;
    /* The transcript's own width, centred: the day's material is not a side
       note, and at 760px it read as a narrow insert beside full-width
       bubbles. Capped so a wide monitor does not stretch three short rows
       into one long line, and auto margins do the centring. */
    max-width: 980px; width: 100%;
    /* #chat is a flex column, and this card clips its own content for the
       gold top rule. A clipped flex item has an automatic minimum size of
       zero, so on a short screen flexbox squashed the whole card to 2px and
       the transcript never scrolled: on a phone the day could not be read at
       all, and no amount of scrolling brought it back. It keeps its height
       now, and the transcript scrolls instead. */
    flex: 0 0 auto;
    margin: 2px auto 10px;
    border-radius: 18px; border: 1px solid rgba(138,90,0,.26);
    background: var(--card);
    /* Three light sources: a hairline of daylight on the top edge, a contact
       shadow so it sits on the page, and one wide soft one so it does not read
       as a flat rectangle pasted into the transcript. */
    box-shadow:
      0 1px 0 var(--edge-light) inset,
      0 2px 5px rgba(74,58,30,.055),
      0 20px 38px -26px rgba(74,58,30,.75);
    font-family: var(--font-body);
  }
  /* A gold rule across the top edge rather than a bar down the side: the card
     is something you read, and the rule marks where the day starts without
     turning its left edge into a permanent stripe. */
  .dinline::before {
    content: ""; position: absolute; inset: 0 0 auto; height: 3px; z-index: 1;
    background: linear-gradient(90deg, var(--gold2), var(--gold) 42%, var(--surf-4));
  }
  .dinline.complete { border-color: rgba(79,70,160,.32); }
  .dinline.complete::before {
    background: linear-gradient(90deg, var(--success), var(--surf-6) 55%, var(--surf-4));
  }
  /* Finished: the third tick turns the rule violet, then the card folds away
     rather than vanishing between two frames. Opacity and transform only, so
     the close stays on the compositor like every other animation here. */
  .dinline.closing {
    opacity: 0; transform: translateY(-8px) scale(.99);
    transition: opacity .55s ease .25s, transform .55s ease .25s;
  }
  @media (prefers-reduced-motion: reduce) {
    .dinline.closing { transition: none; }
  }
  /* The header is its own band: a warm wash that separates "what this is"
     from the three things it holds, and a hairline to close it. */
  .dihead {
    display: flex; align-items: flex-start; gap: 9px;
    padding: 13px 12px 10px 14px;
    background: radial-gradient(130% 160% at 0% 0%, rgba(232,191,95,.26), transparent 64%),
      linear-gradient(180deg, var(--surf-2), var(--surf-3));
  }
  .diico {
    width: 28px; height: 28px; border-radius: 9px; flex: none;
    display: grid; place-items: center;
    background: linear-gradient(180deg, var(--surf-3), var(--gold-soft));
    border: 1px solid rgba(138,90,0,.26); color: var(--gold-ink);
    box-shadow: 0 1px 2px rgba(138,90,0,.14);
  }
  .diico svg { width: 16px; height: 16px; }
  .dico svg { width: 13px; height: 13px; }
  .dititle {
    font-family: var(--font-display); font-size: 14px; font-weight: 700;
    color: var(--navy2); line-height: 1.25; letter-spacing: .1px;
  }
  .dititle small {
    display: block; font-family: var(--font-body); font-size: 10px;
    font-weight: 400; color: var(--muted); margin-top: 2px;
    font-variant-numeric: tabular-nums;
  }
  .dihead .spacer { flex: 1 1 auto; }
  /* The bar runs under the whole heading instead of being squeezed between
     the title and the counter, where it had 92px to report three steps. */
  /* Full-bleed under the header band, so it doubles as the rule that closes
     the band off from the three rows below it. */
  .dump {
    height: 4px; margin: 0; border-radius: 0;
    border-top: 1px solid rgba(138,90,0,.16);
    overflow: hidden; background: var(--line);
    box-shadow: inset 0 1px 2px var(--line);
  }
  .dump i {
    display: block; height: 100%; width: 0; border-radius: 0;
    background: linear-gradient(90deg, var(--gold2), var(--gold));
    transition: width .35s cubic-bezier(.22,1,.36,1);
  }
  .diprog {
    font-family: var(--font-display); font-size: 11.5px; font-weight: 700;
    color: var(--muted); white-space: nowrap; padding-top: 4px;
    font-variant-numeric: tabular-nums; letter-spacing: .2px;
  }
  .dinline.complete .diprog { color: var(--success); }
  .dix {
    flex: none; width: 28px; height: 28px; border-radius: 8px; cursor: pointer;
    display: grid; place-items: center; padding: 0; font-family: inherit;
    font-size: 15px; line-height: 1; color: var(--ink-4);
    border: 1px solid transparent; background: transparent;
    transition: background .15s, color .15s;
  }
  /* The header band is warm, so the ✕ darkens toward the navy on hover rather
     than sitting in the flat grey the rows below use. */
  .dix:hover { background: rgba(138,90,0,.12); color: var(--navy); }
  .dirow {
    display: flex; align-items: flex-start; gap: 8px;
    padding: 8px 13px 7px 14px;
    border-top: 1px solid var(--line);
    transition: background .15s;
  }
  /* The meter already draws the line above the first row. */
  .dump + .dirow { border-top: 0; }
  @media (hover: hover) { .dirow:hover { background: var(--line); } }
  .dirow .grow { flex: 1 1 auto; min-width: 0; cursor: pointer; }
  /* A tinted chip per kind, so the three rows are told apart at a glance
     without a label repeating what the row already says. */
  .dikind {
    flex: none; width: 24px; height: 24px; border-radius: 7px; margin-top: 1px;
    display: grid; place-items: center;
  }
  .dikind svg { width: 13px; height: 13px; }
  .dirow[data-kind="words"] .dikind { background: var(--gold-soft); color: var(--gold-ink); }
  .dirow[data-kind="expressions"] .dikind { background: var(--ice); color: var(--ice-ink); }
  .dirow[data-kind="conversations"] .dikind {
    background: rgba(42,90,122,.13); color: var(--blue-ink);
  }
  .dimain {
    font-family: var(--font-display); font-size: 14.5px; font-weight: 700;
    color: var(--navy2); line-height: 1.3; word-break: break-word;
  }
  .dirow.done .dimain { color: var(--indigo-ink); }
  /* Persian gets more leading than Latin here, and it keeps it: the Nastaliq
     this face replaced needed ~2em of it to stop its tallest initials being
     clipped by an ellipsis, and Vazirmatn - a naskh - reads comfortably at the
     same setting rather than tightly. The row wraps instead of truncating, so
     the leading is never the thing that decides whether a word fits. */
  .disub {
    direction: rtl; text-align: right; unicode-bidi: plaintext;
    font-family: var(--font-fa);
    font-size: 12px; color: var(--muted); margin-top: 2px;
    line-height: 2.2;
    overflow-wrap: anywhere;
  }
  /* The opened body is an inset of the card, not a second card: warm paper,
     a hairline, and slightly looser leading than the rows above it. */
  .dibody { margin-top: 7px; padding: 9px 11px; border-radius: 12px;
            background: linear-gradient(180deg, var(--surf-1), var(--surf-2));
            border: 1px solid rgba(138,90,0,.15);
            line-height: 1.55; }
  /* Three one-line rows until a row is opened: the card is a container in the
     conversation, so it must not be a screenful of material the learner has
     not asked to read yet. */
  .dirow .dibody { display: none; }
  .dirow.open .dibody { display: block; }
  .ditools { display: flex; align-items: center; gap: 5px; flex: none; padding-top: 2px; }
  .ditick, .dimore {
    flex: none; width: 26px; height: 26px; border-radius: 8px; cursor: pointer;
    display: grid; place-items: center; padding: 0; font-family: inherit;
    font-size: 12px; color: var(--dim);
    border: 1px solid var(--line); background: var(--surf-1);
    transition: background .15s, border-color .15s, color .15s;
  }
  /* A done item is a filled disc, not a lightly tinted outline: at a glance
     the day is either three unfilled boxes or three filled ones. */
  .ditick.on, .dtick.on {
    background: var(--success); border-color: var(--success); color: var(--on-fill);
  }
  .ditick:hover, .dimore:hover { border-color: var(--line2); }
  .dimore svg { width: 11px; height: 11px; transition: transform .18s; }
  .dirow.open .dimore svg { transform: rotate(180deg); }
  .difoot {
    display: flex; align-items: center; gap: 4px; flex-wrap: wrap;
    margin: 0; padding: 8px 12px 9px 14px;
    border-top: 1px solid var(--line);
    background: var(--line);
  }
  .dibtn {
    font-family: var(--font-body); font-size: 11px; padding: 5px 9px;
    border-radius: 999px; cursor: pointer; color: var(--navy2);
    border: 1px solid var(--line); background: var(--surf-1);
  }
  .dibtn:hover { background: var(--gold-soft); }
  .dibtn.ghost {
    border-color: transparent; background: transparent; color: var(--dim);
    padding-inline: 6px;
  }
  .dibtn.ghost:hover { background: var(--line); color: var(--navy); }
  .difoot .spacer { flex: 1 1 auto; }

  /* ---------- the Today panel, scannable rather than scrollable ---------- */
  .dlead { margin-top: 2px; }
  .dmore {
    flex: none; width: 26px; height: 26px; border-radius: 8px; cursor: pointer;
    display: grid; place-items: center; padding: 0; font-family: inherit;
    color: var(--dim); border: 1px solid var(--line); background: var(--surf-1);
  }
  .dmore svg { width: 11px; height: 11px; transition: transform .18s; }
  .dcard.open .dmore svg { transform: rotate(180deg); }
  .dcard .dbody { display: none; }
  .dcard.open .dbody { display: block; }
  .dtick {
    flex: none; width: 26px; height: 26px; border-radius: 8px; cursor: pointer;
    display: grid; place-items: center; padding: 0; font-family: inherit;
    font-size: 12px; color: var(--dim);
    border: 1px solid var(--line); background: var(--surf-1);
  }
  .dtick.on { background: rgba(79,70,160,.14); border-color: rgba(79,70,160,.4); color: var(--indigo-ink); }
  .dpanelbar {
    display: flex; align-items: center; gap: 7px; flex-wrap: wrap; margin-bottom: 9px;
  }

  /* ---------- offline sentence analyser ---------- */
  .nbar { display: flex; gap: 8px; margin-bottom: 10px; }
  #ninput {
    flex: 1 1 auto; min-width: 0; font-family: var(--font-body); font-size: 14px;
    padding: 9px 12px; border-radius: 11px; color: var(--navy);
    border: 1px solid var(--line); background: var(--card);
  }
  #ninput:focus { outline: 2px solid var(--gold); outline-offset: 1px; }
  .nbtn {
    flex: none; font-family: var(--font-display); font-weight: 700; font-size: 12.5px;
    padding: 9px 14px; border-radius: 11px; cursor: pointer; color: var(--ice-ink);
    border: 1px solid rgba(51,82,110,.35); background: var(--ice);
  }
  .nbtn:hover { filter: brightness(.97); }
  .nexamples { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 4px; }
  .nex {
    font-family: var(--font-body); font-size: 11.5px; padding: 5px 9px;
    border-radius: 999px; cursor: pointer; color: var(--navy2);
    border: 1px dashed var(--line); background: transparent;
  }
  .nex:hover { border-style: solid; background: var(--card); }
  .nresult { padding-top: 4px; }
  .nbusy, .nfail { font-size: 13px; color: var(--muted); padding: 10px 2px; }
  .nfail { color: var(--gold-ink); }
  .nhead b { font-family: var(--font-display); font-size: 15px; color: var(--navy2); }
  .nhead { margin-bottom: 2px; }
  /* The grammar readout: the one thing a learner asked for, before the
     evidence. A gold rule on the leading edge ties it to the theme's own
     accent, and the pattern line is set in the display face because it is the
     line people copy. */
  .ngram {
    border: 1px solid rgba(205,159,60,.38); border-inline-start: 3px solid var(--gold);
    border-radius: 12px; background: linear-gradient(150deg, var(--surf-1), var(--surf-2));
    padding: 9px 12px; margin: 8px 0 4px;
  }
  .ngram-kind {
    font-family: var(--font-display); font-size: 14px; font-weight: 700;
    color: var(--navy2); line-height: 1.3;
  }
  .ngram-kind small {
    display: block; direction: rtl; text-align: right; unicode-bidi: plaintext;
    font-family: var(--font-fa); font-size: 11px; font-weight: 400;
    color: var(--muted); line-height: 1.9;
  }
  .ngram-form {
    font-family: var(--font-display); font-size: 12.5px; font-weight: 700;
    color: var(--gold-ink); margin-top: 4px; word-break: break-word;
  }
  .ngram-note { font-size: 12.5px; color: var(--text); margin-top: 4px; line-height: 1.5; }
  .ngram-note.fa {
    direction: rtl; text-align: right; font-family: var(--font-fa);
    font-size: 11.5px; color: var(--muted); line-height: 1.9;
  }
  .ngram-type {
    display: inline-block; margin-top: 6px; font-size: 10px; font-weight: 800;
    letter-spacing: .4px; text-transform: uppercase; color: var(--ice-ink);
    background: var(--ice); border: 1px solid rgba(51,82,110,.22);
    border-radius: 999px; padding: 2px 8px;
  }
  .msg .ngram { background: transparent; }
  .nlabel {
    font-size: 9.5px; font-weight: 800; letter-spacing: .5px; text-transform: uppercase;
    color: var(--dim); margin: 13px 0 6px;
  }
  .ntable {
    border: 1px solid var(--line); border-radius: 12px; overflow: hidden;
    background: var(--card);
  }
  .nrow {
    display: grid; grid-template-columns: 1.1fr 1.5fr 1fr 1.3fr;
    gap: 6px; align-items: center; padding: 6px 10px; font-size: 12.5px;
    border-top: 1px solid var(--line);
  }
  .nrow:first-child { border-top: 0; }
  .nw { font-weight: 700; color: var(--navy2); word-break: break-word; }
  .npos, .nrole { color: var(--text); }
  .npos small, .nrole small {
    display: block; direction: rtl; text-align: right; unicode-bidi: plaintext;
    font-size: 10.5px; color: var(--muted); font-weight: 400;
    line-height: 1.9; overflow-wrap: anywhere;
  }
  .nlemma { font-size: 11.5px; color: var(--dim); }
  .nunknown { font-size: 10.5px; color: var(--dim); font-style: italic; }
  .ncard {
    border: 1px solid var(--line); border-radius: 12px; padding: 9px 11px;
    background: var(--card); margin-bottom: 8px;
  }
  .ntitle { font-family: var(--font-display); font-size: 13.5px; font-weight: 700; color: var(--navy2); }
  .ntitle small {
    display: block; direction: rtl; text-align: right; unicode-bidi: plaintext;
    font-family: var(--font-fa); font-size: 11px; font-weight: 400; color: var(--muted);
    line-height: 1.9;
  }
  .nev {
    font-size: 11.5px; color: var(--gold-ink, var(--gold-ink)); margin-top: 4px;
    font-style: italic; word-break: break-word;
  }
  .nnote2 { font-size: 12.5px; color: var(--text); margin-top: 5px; line-height: 1.5; }
  .nchip {
    margin-top: 8px; font-family: var(--font-body); font-size: 11.5px;
    padding: 5px 10px; border-radius: 999px; cursor: pointer;
    border: 1px solid rgba(79,70,160,.35); background: rgba(79,70,160,.08);
    color: var(--indigo-ink);
  }
  .nchip:hover { background: rgba(79,70,160,.16); }
  .nlim { margin: 0; padding-left: 16px; }
  .nlim li { font-size: 11.5px; color: var(--muted); line-height: 1.5; margin-bottom: 4px; }
  /* inside a chat bubble the analysis is the same thing, a little tighter */
  .msg .ntable { background: transparent; }
  .msg .ncard { background: transparent; }
  .msg .nrow { font-size: 12px; padding: 5px 8px; }
  @media (max-width: 640px) {
    .nrow { grid-template-columns: 1fr 1.2fr; row-gap: 2px; }
    .nlemma, .nrole { grid-column: 2; }
  }
  .dtools {
    display: flex; align-items: center; gap: 6px; flex-wrap: wrap;
    margin-top: 10px; padding-top: 8px; border-top: 1px dashed var(--line);
  }
  .dbtn {
    font-family: inherit; font-size: 11px; font-weight: 700; cursor: pointer;
    padding: 5px 10px; border-radius: 9px; color: var(--navy);
    background: var(--surf-1); border: 1px solid var(--line);
    transition: background .15s, border-color .15s;
  }
  .dbtn:hover { background: var(--gold-soft); }
  .dbtn.on, .dbtn[aria-pressed="true"] {
    background: rgba(79,70,160,.12); border-color: rgba(79,70,160,.35);
    color: var(--navy-ink);
  }
  .dfoot { font-size: 10px; color: var(--dim); margin-inline-start: auto; }
  .dnote { font-size: 12px; color: var(--muted); line-height: 1.5; margin-top: 6px; }
  .dnone { font-size: 13px; color: var(--muted); line-height: 1.6; }
  @media (min-width: 620px) {
    .dcards { gap: 12px; }
    .dword { font-size: 23px; }
    .dwho { min-width: 74px; }
  }
  /* The Today page is the width of the shell now, and a word card stretched
     to eleven hundred pixels is a one-line card with a horizon in it. Three
     columns where there is room, one where there is not. */
  @media (min-width: 900px) {
    .dcards { grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); align-items: start; }
  }
  @media (max-width: 420px) {
    .dwho { min-width: 46px; font-size: 10px; }
    .dturn { gap: 6px; }
  }

  /* ---------- review: saved words + flashcards ---------- */
  /* Inside the tile. A negative offset puts it outside a 46px button, and
     being a span it then inherits .hbtn span's overflow:hidden and is clipped
     in half - a sliver on the edge rather than a badge. Today's outstanding
     items and the month's level are the two that earn one: a count of saved
     words said nothing the Review panel did not already say. */
  .rbadge {
    position: absolute; top: 3px; inset-inline-end: 3px; z-index: 1;
    display: inline-flex; align-items: center; justify-content: center;
    min-width: 15px; height: 15px; padding: 0 3px; border-radius: 999px;
    font-size: 9px; font-weight: 800; line-height: 1; color: var(--gold-ink);
    background: var(--gold-line); border: 1px solid rgba(250,244,232,.55);
    box-shadow: 0 1px 3px rgba(74,58,30,.35);
    /* .hbtn span sets ellipsis and a nowrap overflow; a number needs neither */
    text-overflow: clip; max-width: none;
  }
  /* .hbtn span (0,1,1) outranked .rbadge (0,1,0), so the count inherited the
     label's grey on a gold pill - 3.8:1 at 9px. The badge needs its own ink. */
  .hbtn span.rbadge { color: var(--gold-ink); }
  .rbadge[hidden] { display: none; }
  .rtop { display: flex; align-items: center; gap: 7px; flex-wrap: wrap; margin-bottom: 10px; }
  .rprog {
    flex: 1 1 120px; height: 7px; border-radius: 999px; overflow: hidden;
    background: var(--line); border: 1px solid var(--line);
  }
  .rprog i {
    display: block; height: 100%; border-radius: 999px;
    background: linear-gradient(90deg, var(--indigo-ink), var(--fill-slate));
    transition: width .35s cubic-bezier(.34,1.3,.64,1);
  }
  .rcount { font-size: 11.5px; color: var(--muted); white-space: nowrap; }
  .rtab {
    background: var(--line); color: var(--muted);
    border: 1px solid var(--line); border-radius: 8px;
    padding: 5px 11px; font-size: 11.5px; cursor: pointer;
    font-family: inherit; transition: .12s;
  }
  .rtab.on { background: linear-gradient(135deg, var(--indigo-ink), var(--fill-slate)); color: var(--on-fill); border-color: transparent; }
  .rtab:hover { color: var(--text); }
  .rtab.on:hover { color: var(--on-fill); }
  .rdanger:hover { background: rgba(168,73,58,.25); border-color: rgba(168,73,58,.5); }

  /* flashcard */
  .rcard {
    padding: 18px 14px 14px; border-radius: 15px; text-align: center;
    background: linear-gradient(155deg, var(--line), var(--line));
    border: 1px solid var(--line);
    box-shadow: inset 0 1px 0 var(--line), 0 8px 24px rgba(74,58,30,.28);
    min-height: 176px; display: flex; flex-direction: column;
    justify-content: center; gap: 8px;
  }
  .rcard .rword { font-size: 26px; font-weight: 700; letter-spacing: .2px; line-height: 1.2; }
  .rcard .rpos {
    align-self: center; font-size: 10px; font-weight: 700; padding: 2px 8px;
    border-radius: 999px; background: var(--line2); color: var(--ink-2);
  }
  .rcard .rfa { font-size: 15px; color: var(--text); line-height: 1.6; }
  .rcard .rlvl { font-size: 10px; color: var(--dim); letter-spacing: .05em; }
  .rcard .rforms {
    font-size: 11.5px; color: var(--muted);
    font-family: "SF Mono", Consolas, monospace;
    line-height: 1.7; word-spacing: .2em;
  }
  .rhidden { filter: blur(7px); opacity: .55; user-select: none; }
  .rflip {
    margin-top: 4px; background: none; border: 1px dashed var(--line2);
    color: var(--muted); border-radius: 9px; padding: 7px 12px; font-size: 12px;
    cursor: pointer; font-family: inherit;
  }
  .rflip:hover { background: var(--line); color: var(--text); }
  .racts { display: flex; gap: 8px; margin-top: 11px; }
  .rbtn {
    flex: 1; min-height: 44px; border-radius: 11px; cursor: pointer;
    font-family: inherit; font-size: 13px; font-weight: 700;
    border: 1px solid var(--line); color: var(--on-fill);
  }
  .rbtn.know { background: linear-gradient(135deg, var(--indigo-ink), var(--surf-6)); }
  .rbtn.again { background: linear-gradient(135deg, var(--red-ink), var(--fill-red)); }
  .rbtn.play { background: var(--line); flex: 0 0 52px; font-size: 16px;
               line-height: 1; padding: 0; }
  .rbtn:hover { filter: brightness(1.1); }
  .rdots { display: flex; gap: 3px; justify-content: center; margin-top: 10px; flex-wrap: wrap; }
  .rdot { width: 6px; height: 6px; border-radius: 50%; background: var(--line2); }
  .rdot.on { background: var(--indigo-ink); }
  .rdot.now { background: var(--gold-line); transform: scale(1.5); }

  /* list mode */
  .rlist { display: flex; flex-direction: column; gap: 6px; }
  .rrow {
    display: grid; grid-template-columns: 1fr auto auto; gap: 9px; align-items: center;
    padding: 8px 10px; border-radius: 10px;
    background: linear-gradient(150deg, var(--line), var(--line));
    border: 1px solid var(--line);
  }
  .rrow .rmain { min-width: 0; }
  .rrow .ren { font-size: 13.5px; font-weight: 600; }
  .rrow .rfa2 { font-size: 11.5px; color: var(--muted); margin-top: 1px; }
  .rrow.ok { border-color: rgba(79,70,160,.4); }
  .rrow.ok .ren::after { content: ' \2713'; color: var(--indigo-ink); }
  .ricon {
    width: 30px; height: 30px; border-radius: 8px; border: 1px solid var(--line);
    background: var(--line); color: var(--text); font-size: 13px;
    cursor: pointer; display: grid; place-items: center; font-family: inherit;
  }
  .ricon:hover { background: var(--line2); }
  .ricon.del:hover { background: rgba(168,73,58,.25); border-color: rgba(168,73,58,.5); }
  .rempty { text-align: center; padding: 26px 10px; color: var(--muted); font-size: 13px; line-height: 1.7; }
  .rempty .big { font-size: 30px; display: block; margin-bottom: 8px; }

  /* the "save to review" toggle inside the word card */
  .rstar {
    background: rgba(201,138,22,.14); border: 1px solid rgba(201,138,22,.34);
    color: var(--gold-ink); border-radius: 9px; padding: 6px 11px; font-size: 12px;
    cursor: pointer; font-family: inherit; font-weight: 600;
  }
  .rstar:hover { background: rgba(201,138,22,.26); }
  .rstar.on { background: linear-gradient(135deg, var(--gold-line), var(--red-ink)); color: var(--gold-ink); border-color: transparent; }
  .wd-star { margin-top: 10px; display: flex; gap: 7px; align-items: center; flex-wrap: wrap; }
  .wd-star .why { font-size: 11px; color: var(--dim); }

  /* ---------- phonetics: topic rail + dense symbol cards ----------
     Designed so a whole lesson fits on one phone screen: the rail is one
     scroll line, rows are a single column, and every ▶ speaks the example. */
  .phrail {
    display: flex; gap: 6px; overflow-x: auto; padding: 2px 0 9px;
    margin-bottom: 4px; border-bottom: 1px solid var(--line);
    -webkit-overflow-scrolling: touch; overscroll-behavior-x: contain;
    scrollbar-width: none;
  }
  .phrail::-webkit-scrollbar { display: none; }
  .phtab {
    flex: none; display: inline-flex; align-items: center; gap: 6px;
    background: var(--line); color: var(--muted);
    border: 1px solid var(--line); border-radius: 999px;
    padding: 6px 12px; font-size: 12px; font-weight: 600;
    cursor: pointer; transition: .14s; font-family: inherit; white-space: nowrap;
  }
  .phtab i {
    font-style: normal; font-size: 9px; font-weight: 800; letter-spacing: .04em;
    padding: 2px 5px; border-radius: 5px;
    background: var(--line); color: var(--ink-3);
  }
  .phtab:hover { background: var(--line); color: var(--text); }
  .phtab.on {
    background: var(--fill-navy);
    color: var(--on-fill); border-color: transparent;
    box-shadow: 0 4px 12px var(--line2);
  }
  .phtab.on i { background: rgba(255,255,255,.18); color: var(--on-fill); }

  /* the view scrolls inside the panel; the rail stays pinned so you never
     lose your place when drilling through a list */
  .phview { padding-top: 12px; overflow-y: auto; flex: 1; min-height: 0;
            overscroll-behavior: contain; -webkit-overflow-scrolling: touch; }
  #phpanel, #rpanel { display: none; flex-direction: column; }
  #phpanel.open, #rpanel.open { display: flex; }
  .phead { margin-bottom: 14px; }
  .phead .ptitle {
    display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
    font-size: 16px; font-weight: 700; letter-spacing: .2px;
  }
  .phead .ptitle .lvl {
    font-size: 9.5px; font-weight: 800; letter-spacing: .06em;
    padding: 2px 7px; border-radius: 999px;
    background: var(--ice);
    color: var(--ink-1); border: 1px solid rgba(60,64,91,.4);
  }
  .phead .ptitle .pfa { font-size: 13px; color: var(--muted); font-weight: 500; }
  .pblurb {
    font-size: 12.5px; line-height: 1.65; color: var(--muted); margin-top: 6px;
  }

  .ptip {
    display: flex; gap: 9px; align-items: flex-start;
    padding: 10px 12px; margin-bottom: 14px; border-radius: 12px;
    background: linear-gradient(135deg, rgba(201,138,22,.14), rgba(160,58,99,.08));
    border: 1px solid rgba(201,138,22,.28);
  }
  .ptip .pk { font-size: 14px; line-height: 1.3; flex: none; }
  .ptip .pt { font-size: 12.5px; line-height: 1.6; color: var(--muted); }
  .ptip .pt b { color: var(--ink); }

  .pgroup { margin-bottom: 14px; }
  .pgroup:last-child { margin-bottom: 0; }
  .pgroup > .ghead {
    font-size: 10.5px; letter-spacing: .06em; text-transform: uppercase;
    color: var(--ink-3); font-weight: 700; margin-bottom: 7px;
  }
  .pgroup > .ghead .fa {
    color: var(--dim); text-transform: none; letter-spacing: 0; font-weight: 400;
  }
  .prows {
    display: grid; grid-template-columns: 1fr; gap: 7px;
  }
  .prow {
    display: grid; grid-template-columns: 1fr auto; gap: 10px; align-items: center;
    padding: 9px 11px; border-radius: 11px;
    background: linear-gradient(150deg, var(--line), var(--line));
    border: 1px solid var(--line);
    box-shadow: inset 0 1px 0 var(--line);
  }
  .prow:hover { background: var(--line); border-color: rgba(60,64,91,.3)); }
  .pmain { min-width: 0; }
  .pip {
    font-family: "SF Mono", "Cascadia Mono", Consolas, "DejaVu Sans Mono", monospace;
    font-size: 13.5px; font-weight: 700; color: var(--gold-ink);
    word-break: break-word; line-height: 1.35;
  }
  .psub { font-size: 11px; color: var(--ink-3); margin-top: 1px; line-height: 1.4; }
  .psay { font-size: 13px; color: var(--text); margin-top: 3px; line-height: 1.45; }
  .pfa { font-size: 12px; color: var(--muted); margin-top: 2px; line-height: 1.55; }
  .pwords {
    font-size: 11px; color: var(--dim); margin-top: 3px; line-height: 1.5;
    font-family: "SF Mono", Consolas, "DejaVu Sans Mono", monospace;
  }
  .pnote {
    font-size: 11px; color: var(--muted); margin-top: 4px; line-height: 1.5;
    padding-inline-start: 13px; position: relative;
  }
  .pnote::before { content: '💡'; position: absolute; inset-inline-start: 0; font-size: 10px; }
  .pplay {
    width: 34px; height: 34px; flex: none; border-radius: 50%;
    background: var(--fill-navy); border: none;
    color: var(--on-fill); font-size: 12px; cursor: pointer;
    display: grid; place-items: center; transition: .12s;
    box-shadow: 0 3px 10px var(--line2);
  }
  .pplay:hover { filter: brightness(1.12); transform: scale(1.06); }
  .pplay.playing { background: linear-gradient(135deg, var(--indigo-ink), var(--fill-slate)); }

  @media (min-width: 600px) {
    .prows { grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 8px; }
    .phead .ptitle { font-size: 17.5px; }
    .pblurb, .ptip .pt { font-size: 13px; }
    .phtab { padding: 7px 14px; font-size: 12.5px; }
    .pplay { width: 36px; height: 36px; }
  }

  /* ---------- everyday-sentence cards ----------
     A phrase bank used to arrive as one run-on pre-wrap block, so the
     translations collided. Each "• en / ↲ fa" pair is its own card now. */
  .msg.plist { white-space: normal; padding: 8px 10px; }
  .msg.plist .plist-head {
    font-size: 13px; font-weight: 700; color: var(--gold-ink);
    padding: 1px 3px 6px; margin-bottom: 6px;
    border-bottom: 1px solid var(--line);
  }
  .pcard {
    display: flex; flex-direction: column; gap: 2px;
    padding: 8px 10px; margin-bottom: 5px;
    border-radius: 10px;
    background: linear-gradient(150deg, var(--line), var(--line));
    border: 1px solid var(--line);
    box-shadow: inset 0 1px 0 var(--line);
  }
  .pcard:last-child { margin-bottom: 0; }
  .pcard .pen { font-size: 13px; line-height: 1.45; color: var(--text); }
  .pcard .pen::before {
    content: '▸'; color: var(--gold-ink); font-size: 10px; margin-inline-end: 6px;
    vertical-align: 1px;
  }
  .pcard .pfa { font-size: 12px; line-height: 1.5; color: var(--muted); }
  .pcard .pfa::before {
    content: '↲'; color: var(--dim); font-size: 10px; margin-inline-end: 6px;
  }
  @media (min-width: 600px) {
    .msg.plist { padding: 9px 12px; }
    .pcard { padding: 8px 11px; margin-bottom: 6px; }
    .pcard .pen { font-size: 13.5px; }
    .pcard .pfa { font-size: 12.5px; }
  }

  /* ---------- graceful fallback where backdrop-filter is unsupported ---------- */
  @supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
    .app { background: var(--surf-1); }
    header { background: var(--surf-1); }
    #vpanel, #gpanel, #fpanel, #phpanel, #rpanel, #dpanel, #npanel, #bpanel { background: var(--surf-1); }
    .msg.bot { background: var(--surf-1); }
    #input { background: var(--surf-1); }
    .hb { display: none; }
  }

  /* =================================================================
     MOBILE FIRST
     The rules above are the phone layout: full-bleed, one column,
     44px touch targets, safe-area aware. Larger screens only ever
     *add* room — nothing below is required for the app to be usable.
     ================================================================= */
  :root {
    /* phones don't have a pointer: no hover lift, and 44px min targets */
    --tap: 44px;
    --gap: 8px;
    --pad: 14px;
    --sat: env(safe-area-inset-top, 0px);
    --sab: env(safe-area-inset-bottom, 0px);
    --sal: env(safe-area-inset-left, 0px);
    --sar: env(safe-area-inset-right, 0px);
    --vh: 100dvh; /* falls back to 100vh where dvh is unsupported */
  }
  @supports not (height: 100dvh) { :root { --vh: 100vh; } }

  html { -webkit-text-size-adjust: 100%; }
  body {
    padding: 0;
    /* the phone owns the whole screen; the desktop frame is opt-in below */
    align-items: stretch; justify-content: stretch;
  }
  .app {
    width: 100%; height: var(--vh);
    border-radius: 0; border-inline: none; border-block: none;
  }
  .app::after { left: 6%; right: 6%; }

  /* ---- header: title row, then a scrollable strip of panel toggles ---- */
  header {
    flex-wrap: wrap; gap: 8px;
    /* The chrome was a quarter of the screen: 119px of header plus 108px of
       composer on an 791px viewport left barely two thirds for the thing the
       app is for. Padding is cut rather than type - the reading size stays. */
    padding: calc(7px + var(--sat)) calc(var(--pad) + var(--sar)) 7px
             calc(var(--pad) + var(--sal));
  }
  header h1 { font-size: 17px; }
  .avatar { width: 42px; height: 42px; border-radius: 14px; }
  .avatar img { width: 34px; height: 34px; }
  .status { display: none; }      /* the pill is desktop-only decoration */
  /* the daily counter belongs on the phone too — just more compact */
  #seedmeter { width: 62px; height: 18px; }
  #seedmeter span { font-size: 9.5px; padding: 0 6px; letter-spacing: -.2px; }

  /* seven compact tiles share the title row — no scrolling needed */
  .tools {
    order: 10; width: 100%;
    display: flex; gap: 4px; justify-content: space-between;
    /* Seven 38px tiles, six 4px gaps and 14px of padding each side is 306px
       exactly - so any phone narrower than that clips the last tile. The row
       scrolls instead. Desktop overrides this back to visible above 600px. */
    overflow-x: auto;
    scrollbar-width: none; padding-bottom: 0;
    /* let the row bleed into the side padding so tiles can use the full width */
    margin-inline: calc(var(--pad) * -1); padding-inline: var(--pad);
  }
  .tools::-webkit-scrollbar { display: none; }
  /* the tagline is a desktop nicety; on a phone the row needs the width */
  header p { display: none; }
  @media (min-width: 600px) { header p { display: block; } }
  /* 38x40, not 44x46: still well past the 24px WCAG 2.5.8 minimum, and
     seven of them plus gaps now fit without a scroll on a 360dp phone. */
  .hbtn { width: 38px; height: 40px; border-radius: 11px; padding: 3px 0; gap: 2px; }
  .hbtn i, .hbtn i svg { width: 16px; height: 16px; }
  .hbtn span { font-size: 8px; }
  /* no hover affordances on touch — they'd stick after a tap */
  @media (hover: none) {
    .hbtn:hover, .ftopic:hover, .vbtn:hover,
    .gbtn:hover, .go:hover, .ltab:hover, .lrow:hover, .lplay:hover,
    .send:hover { transform: none; filter: none; }
    .hbtn:active, .ftopic:active, .vbtn:active,
    .gbtn:active, .go:active, .ltab:active, .lrow:active, .send:active {
      transform: scale(.96);
    }
  }

  /* ---- panels: edge-to-edge, own scroll area, the height of the column ---- */
  #vpanel, #gpanel, #fpanel, #lpanel, #phpanel, #rpanel, #dpanel, #npanel, #bpanel {
    padding: 10px calc(var(--pad) + var(--sar)) 24px calc(var(--pad) + var(--sal));
    --secpad: calc(var(--pad) + var(--sar));
    max-height: none;
    overscroll-behavior: contain;
    -webkit-overflow-scrolling: touch;
  }
  #vpanel h3, #gpanel h3, #fpanel h3, #lpanel h3, #phpanel h3, #rpanel h3,
  #bpanel h3, #rdpanel h3, #stpanel h3, #lvlpanel h3, #wqpanel h3,
  #prpanel h3, #acpanel h3, #dpanel h3, #npanel h3 {
    margin-bottom: 4px; line-height: 1.28;
  }
  /* The chip cloud is the panel's own content now: the page scroller does the
     scrolling, and a second scroll box inside it trapped the last row. */
  .domains { max-height: none; }

  /* every tappable pill in a panel gets a real touch target */
  .vbtn, .gbtn, .ftopic, .ltab {
    min-height: 32px; padding: 6px 11px; font-size: 12px;
  }
  /* 28px, not 32: still past the 24px WCAG 2.5.8 minimum, and 48 lessons
     grouped by level now fit a phone screen without hunting. */
  .gbtn { padding: 0; min-height: 28px; }
  .gmain { padding: 4px 3px 4px 9px; font-size: 11.5px; min-height: 28px; }
  .go { padding: 0 9px; font-size: 11.5px; }
  .go.exam {
    background: rgba(201,138,22,.14); color: var(--gold-ink);
    border-left-color: rgba(201,138,22,.34);
  }
  .go.exam:not(.locked):hover { background: rgba(201,138,22,.34); }
  .go.exam.locked {
    /* --muted, not --dim: the locked chip sits on the lavender bar, where the
       lighter grey measured 4.1:1 at 11.5px. */
    background: rgba(43,48,73,0.102); color: var(--muted);
    border-left-color: var(--line2);
  }
  .lrow { padding: 7px 10px; gap: 10px; }
  .lplay { width: 36px; height: 36px; font-size: 14px; }
  .ltext .en { font-size: 14px; }
  .ltext .fa { font-size: 12px; margin-top: 2px; }
  .ltabs { gap: 6px; }

  /* ---- chat ---- */
  #chat { padding: 10px calc(var(--pad) + var(--sar)) 6px calc(var(--pad) + var(--sal));
          gap: 10px; }
  .bubble-wrap { max-width: 94%; }
  .mav { width: 24px; height: 24px; border-radius: 9px; }
  .mav svg, .mav img { width: 20px; height: 20px; }
  /* font-size deliberately unchanged: denser, not smaller to read */
  .msg { padding: 10px 13px; font-size: 16px; border-radius: 14px; }
  .msg.long { max-height: 52vh; }
  .row { gap: 6px; }

  /* ---- input: 16px stops iOS zooming on focus, safe area clears the bar ---- */
  form {
    padding: 8px calc(var(--pad) + var(--sar))
             calc(8px + var(--sab)) calc(var(--pad) + var(--sal));
    --fgap: 8px; gap: var(--fgap); flex-direction: column;
  }
  /* The composer holds three things: the input, the mic and Send. The input is
     the only one allowed to shrink, so the mic can never be squeezed off a
     narrow screen - min-width:0 states that explicitly rather than relying on
     the input's intrinsic width being small. */
  #input { min-width: 0; }
  @media (max-width: 420px) {
    .messageBox { gap: 2px; padding: 3px 4px 3px 3px; }
    /* A page title at 19px on a 360px phone is three lines of Persian before
       the first row of content. It steps down rather than the whole panel
       stepping back to the old 13px caption size. */
    #vpanel h3, #gpanel h3, #fpanel h3, #lpanel h3, #phpanel h3, #rpanel h3,
    #bpanel h3, #rdpanel h3, #stpanel h3, #lvlpanel h3, #wqpanel h3,
    #prpanel h3, #acpanel h3, #dpanel h3, #npanel h3 { font-size: 16.5px; }
  }

  /* ---- daily limit reached: the composer goes quiet ---- */
  /* The daily allowance: a rail under the composer with the moon riding it
     left to right. It was text that appeared only at the limit, which is the
     one moment advice is too late to be useful. */
  .limitenote {
    padding: 0; margin: 5px 2px 0; min-height: 20px;
  }

  .limitrail {
    position: relative; height: 15px;
  }
  /* the track */
  .limitrail::before {
    content: ''; position: absolute; left: 0; right: 0; top: 8px;
    height: 3px; border-radius: 2px; background: var(--line);
  }
  /* how much of the day is spent */
  .limitfill {
    position: absolute; left: 0; top: 8px; height: 3px; border-radius: 2px;
    width: calc(var(--p, 0) * (100% - 20px) + 10px);
    background: linear-gradient(90deg, rgba(60,64,91,.85), rgba(207,159,60,.85));
    transition: width .45s cubic-bezier(.22,1,.36,1), background .3s;
  }

  .limitenote .lockic {
    position: absolute; top: -2px; font-size: 15px; line-height: 1;
    /* left, not transform: a % inside transform() resolves against the
       element's own box, so the moon moves by a fraction of its own width and
       never leaves the start of the rail. */
    left: calc(var(--p, 0) * (100% - 20px));
    transition: left .45s cubic-bezier(.22,1,.36,1);
    filter: grayscale(.35) brightness(.95);
  }

  /* the text is quiet until it has something worth saying */
  .limitxt {
    display: block; margin-top: 3px; font-size: 11.5px; line-height: 1.5;
    color: var(--muted);
  }
  .limitxt:empty { display: none; }

  .limitenote.warn .limitfill {
    background: linear-gradient(90deg, rgba(201,138,22,.9), rgba(168,73,58,.9));
  }
  .limitenote.warn .lockic { filter: none; }
  .limitenote.warn .limitxt { color: var(--gold-ink); }

  .limitenote.full .limitfill {
    background: linear-gradient(90deg, rgba(168,73,58,.95), rgba(168,73,58,.95));
  }
  .limitenote.full .lockic { filter: none; }
  .limitenote.full {
    padding: 9px 12px; border-radius: 11px;
    background: var(--surf-2);
    border: 1px solid rgba(168,73,58,.28);
    animation: fade .2s ease;
  }
  .limitenote.full .limitrail { height: 14px; }
  .limitenote.full .limitfill { top: 6px; height: 3px; }
  .limitenote.full .lockic { top: -4px; }
  .limitenote b { color: var(--ink); }
  form.locked #input {
    opacity: .45; cursor: not-allowed; background: var(--line);
  }
  form.locked .send {
    opacity: .4; cursor: not-allowed; filter: grayscale(.5); transform: none;
    box-shadow: none;
  }
  /* every control that would send a message is visibly retired */
  .ftopic.locked, .vbtn.locked, .gmain.locked, .go.locked {
    opacity: .35; cursor: not-allowed; pointer-events: none;
    filter: grayscale(.6);
  }
  #input { padding: 10px 13px; font-size: 16px; border-radius: 13px; }

  /* ------------------------------------------------------------ speech ---- */
  /* The mic used to be an emoji on a #f5eedb disc with a #cfc1a4 ring -
     dark on dark, next to a bright indigo Send button. It read as missing,
     and where the platform has no emoji font the glyph rendered as nothing
     at all. So: an inline SVG for the icon (never depends on a font) and a
     fill light enough to be seen without competing with Send. */
  .mic {
    /* none, so a hold is never stolen for scrolling or swallowed by the
       long-press callout - which is what left the button stuck on Android */
    touch-action: none;
    -webkit-touch-callout: none;
    user-select: none; -webkit-user-select: none;
    width: 36px; height: 36px; flex: 0 0 36px; border-radius: 50%;
    display: grid; place-items: center; cursor: pointer;
    color: var(--on-fill); background: var(--fill-slate);
    border: 0;
    box-shadow: 0 2px 8px var(--line), inset 0 1px 0 var(--edge-light);
    transition: background .18s, color .18s, transform .1s, box-shadow .18s;
  }
  .mic svg { width: 19px; height: 19px; display: block; }
  .mic svg * { stroke: currentColor; }
  /* The outline used to carry every state - default, hover, listening,
     unavailable - so removing it is not just deleting a line: each of those
     states now has to be legible from the fill alone. They are, because the
     fills differ in hue, not just in brightness. */
  .mic:hover {
    /* #3a4b93 was the indigo highlight of the old palette */
    background: var(--fill-slate2); color: var(--on-fill);
    box-shadow: 0 4px 16px rgba(74,58,30, .6), inset 0 1px 0 var(--line);
  }
  .mic:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
  .mic:active { transform: scale(.94); }
  /* Teal, not pink. Pink is the tutor; when the mic pulses in the tutor's
     own colour it reads as though the app is talking at you. */
  .mic.rec {
    background: var(--fill-red); color: var(--on-fill);
    box-shadow: 0 2px 10px rgba(168,73,58,.3), 0 0 0 1px rgba(168,73,58,.35);
    animation: micPulse 1.4s ease-out infinite;
  }
  .mic.rec svg { transform: scale(1.06); }
  /* aria-disabled, not disabled: a disabled button swallows its own click
     events, so on touch the control would sit there doing nothing and the
     explanation in its title would be unreachable. aria-disabled announces
     the state to a screen reader while leaving the tap working. */
  .mic[aria-disabled="true"] {
    background: var(--surf-4); color: var(--dim);
    box-shadow: inset 0 1px 0 var(--edge-light);
  }
  .mic[aria-disabled="true"]:hover {
    background: var(--surf-4); color: var(--ink-3);
  }
  /* a hint, once, so the button is noticed rather than rediscovered */
  @keyframes micHint {
    0%, 100% { box-shadow: 0 2px 8px var(--line2), 0 0 0 0 rgba(232,191,95,.6); }
    60%      { box-shadow: 0 2px 8px var(--line2), 0 0 0 9px rgba(232,191,95,0); }
  }
  .mic.hint { animation: micHint 2.6s ease-out 3; }
  /* the pulse ring follows the button's own red, not the tutor's pink */
  @keyframes micPulse {
    0%   { box-shadow: 0 0 0 0 rgba(168,73,58,.5); }
    100% { box-shadow: 0 0 0 16px rgba(168,73,58,0); }
  }
  @media (prefers-reduced-motion: reduce) {
    .mic.rec, .mic.hint { animation: none; }
    /* The moon still lands in the right place - it just arrives there
       rather than sliding across. Its position is information; the travel is
       decoration. */
    .limitenote .lockic, .limitfill { transition: none; }
  }
  .stt-panel {
    display: flex; gap: 8px; align-items: center; flex-wrap: wrap;
    padding: 9px 14px; margin: 0 10px 6px; font-size: 13.5px; line-height: 1.45;
    background: var(--surf-1); border: 1px solid var(--line);
    border-radius: 14px; color: var(--ice-ink);
  }
  .stt-panel[hidden] { display: none; }
  .stt-dot {
    width: 9px; height: 9px; border-radius: 50%; background: var(--fill-red);
    flex: 0 0 9px; animation: micBlink 1.1s ease-in-out infinite;
  }
  @keyframes micBlink { 0%, 100% { opacity: 1; } 50% { opacity: .25; } }
  .stt-label { color: var(--ink-3); font-size: 12.5px; }
  .stt-interim { color: var(--navy-ink); font-style: italic; }
  /* white on the cream speech card: the transcript arrived invisible */
  .stt-final { color: var(--ink); }

  /* ------------------------------------------------ BBC listening ------- */
  .bbc-open {
    display: block; width: 100%; margin-bottom: 10px; padding: 11px 14px;
    border-radius: 13px; border: 1px solid var(--line-strong); background: var(--surf-3);
    color: var(--ink-2); font-size: 13.5px; text-align: left; cursor: pointer;
  }
  .bbc-open:hover { border-color: var(--focus); }
  .bbc-head { display: flex; flex-direction: column; gap: 7px; margin-bottom: 10px; }
  .bbc-back {
    align-self: flex-start; min-height: 40px; padding: 8px 13px; border-radius: 11px;
    border: 1px solid var(--line-strong); background: var(--surf-3); color: var(--ink-2);
    font-size: 12.5px; cursor: pointer;
  }
  .bbc-note { font-size: 12px; color: var(--ink-3); line-height: 1.5; }
  .bbc-tabs { display: flex; gap: 6px; overflow-x: auto; padding-bottom: 9px; }
  .bbc-tab {
    flex: 0 0 auto; padding: 6px 12px; border-radius: 999px; font-size: 12.5px;
    border: 1px solid var(--line-strong); background: transparent; color: var(--navy-ink); cursor: pointer;
  }
  .bbc-tab.on { background: var(--fill-navy); border-color: var(--navy); color: var(--on-fill); }
  .bbc-list { display: flex; flex-direction: column; gap: 9px; }
  .bbc-row {
    padding: 12px 14px; border-radius: 14px; background: var(--surf-3);
    /* a hairline, not the #2b3768 outline the dark list used */
    border: 1px solid var(--line);
    box-shadow: 0 2px 8px rgba(74,58,30,.07);
  }
  .bbc-row-head { display: flex; gap: 9px; align-items: baseline; }
  .bbc-lvl {
    flex: 0 0 auto; font-size: 11px; font-weight: 700; padding: 2px 8px;
    border-radius: 999px; background: var(--surf-4); color: var(--ink-2);
  }
  .bbc-lvl.lvl-A2 { background: var(--surf-2); color: var(--navy-ink); }
  .bbc-lvl.lvl-B1 { background: var(--surf-3); color: var(--blue-ink); }
  .bbc-lvl.lvl-B2 { background: var(--surf-2); color: var(--blue-ink); }
  .bbc-lvl.lvl-C1 { background: var(--surf-3); color: var(--rose-ink); }
  /* the unrated chip belongs to the same family as the others; it was a navy
     pill left over from the dark list, sitting on a cream card */
  .bbc-lvl.lvl-none { background: var(--surf-4); color: var(--ink-2); }
  .bbc-title { font-size: 14.5px; color: var(--ink); font-weight: 600; }
  .bbc-blurb { margin-top: 5px; font-size: 12.5px; color: var(--navy-ink); line-height: 1.5; }
  .bbc-meta { margin-top: 6px; font-size: 11.5px; color: var(--ink-3); }
  .bbc-actions { display: flex; gap: 7px; margin-top: 9px; flex-wrap: wrap; align-items: center; }
  .bbc-play {
    padding: 8px 14px; min-height: 40px; border-radius: 11px; font-size: 13px;
    border: 1px solid var(--navy); background: var(--fill-navy); color: var(--on-fill);
    cursor: pointer; font-family: var(--font-display);
  }
  .bbc-play.on { background: var(--gold-ink); border-color: var(--gold-line); }
  .bbc-play.nofile { background: var(--surf-3); border-color: var(--line2); color: var(--muted); }
  .bbc-play.nofile:hover { border-color: var(--line2); color: var(--ink); }
  .bbc-link { font-size: 12px; color: var(--ice-ink); text-decoration: none; padding: 6px 4px; }
  .bbc-link:hover { color: var(--navy); text-decoration: underline; }
  .bbc-empty { font-size: 12px; color: var(--ink-3); padding: 4px 2px; }
  /* 40, not 46: this min-height was the floor for the whole composer row,
     input and mic included, so the button set the height of the form. */
  .send { width: 36px; height: 36px; border-radius: 50%; }

  /* ---------- tablets: two comfortable columns ---------- */
  @media (min-width: 600px) {
    :root { --pad: 18px; }
    .app { border-radius: 22px; border: 1px solid var(--line); }
    body { padding: 16px; align-items: center; justify-content: center; }
    .app { height: min(94vh, 980px); width: min(1180px, 100%); }
    .app::after { left: 12%; right: 12%; }
    header { padding: 14px 20px; flex-wrap: wrap; }
    header h1 { font-size: 19px; }
    .avatar { width: 46px; height: 46px; border-radius: 15px; }
    .avatar img { width: 38px; height: 38px; }
    /* The toolbar leaves the phone strip but stays on its own row. Inlining
       it here was a clipped row: at 600-880px the title, the meter and seven
       48px tiles measure ~830px, so the last two tiles - Review and Clear -
       ran under the app's overflow:hidden and could not be tapped at all.
       One row measures the whole header; it only fits from 900px up. */
    .tools { order: 10; width: 100%; margin: 0; padding: 0;
             overflow: visible; gap: 6px; justify-content: flex-start; }
    .hbtn { width: 48px; height: 48px; }
    .hbtn i, .hbtn i svg { width: 19px; height: 19px; }
    .hbtn span { font-size: 8.5px; }
    #chat { padding: 20px 22px 10px; gap: 16px; }
    .bubble-wrap { max-width: 80%; }
    .mav { width: 32px; height: 32px; border-radius: 11px; }
    .mav svg, .mav img { width: 26px; height: 26px; }
    .msg { padding: 12px 16px; font-size: 16px; }
    #vpanel, #gpanel, #fpanel, #lpanel, #phpanel, #rpanel, #dpanel, #npanel, #bpanel { padding: 12px 18px 24px; --secpad: 18px; max-height: none; }
    .domains { max-height: none; }
    form { padding: 14px 20px 18px; --fgap: 8px; gap: var(--fgap); }
    #input { padding: 10px 14px; font-size: 15.5px; }
    .send { width: 36px; height: 36px; padding: 0; }
  }

  /* ---------- desktop: full-size meter + the status pill ---------- */
  @media (min-width: 900px) {
    .status { display: flex; }
    #seedmeter { width: 66px; height: 20px; }
    #seedmeter span { font-size: 10.5px; padding: 0 7px; }
    /* now the header really is one row: brand, meter, tool rail */
    header { flex-wrap: nowrap; }
    .tools { order: 0; width: auto; justify-content: flex-end; }
  }

  /* ==================================================================
     MOTION SYSTEM
     Two speeds, one curve, transform/opacity only. Every rule below is
     neutralised at the end of this block under prefers-reduced-motion.
     ================================================================== */

  /* ---------- 1. the mote field -------------------------------------
     A thin layer of drifting points behind the glass. They sit under the
     app's backdrop-filter, so they read as depth in the pane rather than
     as objects floating over the text. */
  .motes { position: fixed; inset: 0; z-index: 0; pointer-events: none; }
  .motes canvas { width: 100%; height: 100%; display: block; }

  /* ---------- 2. message entrance ------------------------------------
     The avatar leads and the bubble follows, a few frames apart. That is
     what makes a message feel like it was *placed* rather than appearing. */
  @keyframes msgIn {
    from { opacity: 0; transform: translate3d(0, 14px, 0) scale(.965); }
    60%  { opacity: 1; }
    to   { opacity: 1; transform: none; }
  }
  @keyframes avatarIn {
    from { opacity: 0; transform: translate3d(-10px, 10px, 0) rotate(-14deg) scale(.7); }
    to   { opacity: 1; transform: none; }
  }
  @keyframes avatarInMe {
    from { opacity: 0; transform: translate3d(10px, 10px, 0) rotate(14deg) scale(.7); }
    to   { opacity: 1; transform: none; }
  }
  .row { animation: msgIn .34s cubic-bezier(.22,1,.36,1) both; }
  .row .mav { animation: avatarIn .42s cubic-bezier(.22,1,.36,1) both; }
  .row.user .mav { animation-name: avatarInMe; }

  /* a sheen crosses the bubble as it lands - only on new bot messages */
  @keyframes sheen {
    from { transform: translate3d(-120%, 0, 0); }
    to   { transform: translate3d(320%, 0, 0); }
  }
  .bubble-wrap { position: relative; overflow: hidden; border-radius: 16px; }
  .msg.bot::after {
    content: ''; position: absolute; inset: 0; pointer-events: none;
    background: linear-gradient(105deg, transparent 30%,
      var(--line2) 50%, transparent 70%);
    transform: translate3d(-120%, 0, 0);
  }
  .row.bot .msg.bot::after { animation: sheen .85s .16s ease-out; }

  /* ---------- 3. the bird -------------------------------------------
     Idle: a slow breath. Speaking: the whole portrait pulses on the beat of
     whatever is being read aloud. The blink is gone with the drawn eye - a
     picture cannot squint, and faking it would mean two mascots again. */
  @keyframes breathe {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    50%      { transform: translateY(-2px) rotate(-1.2deg); }
  }
  @keyframes talkPulse {
    0%, 100% { transform: scale(1); }
    50%      { transform: scale(1.09); }
  }
  .mav.bot { animation: breathe 4.2s ease-in-out infinite; }
  body.speaking .mav.bot { animation: talkPulse .62s ease-in-out infinite; }

  /* ---------- 4. typing indicator ------------------------------------
     Three dots with a light travelling through them, plus a small lift so
     the row breathes while the bot composes. */
  @keyframes typingLift { 0%,100% { opacity:.85; } 50% { opacity:1; } }
  @keyframes typingWave {
    0%, 60%, 100% { transform: translateY(0) scale(1); opacity: .45; }
    30%           { transform: translateY(-4px) scale(1.25); opacity: 1; }
  }
  @keyframes typingSheen { to { background-position: 200% 0; } }
  #typing .msg.typing {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 13px 16px; overflow: hidden;
  }
  #typing .msg.typing span {
    width: 7px; height: 7px; border-radius: 50%;
    background: linear-gradient(90deg, var(--fill-slate), var(--gold2), var(--fill-slate));
    background-size: 200% 100%;
    animation: typingWave 1.15s ease-in-out infinite, typingSheen 1.8s linear infinite;
  }
  #typing .msg.typing span:nth-child(2) { animation-delay: .16s, .16s; }
  #typing .msg.typing span:nth-child(3) { animation-delay: .32s, .32s; }
  #typing .mav { animation: typingLift 1.6s ease-in-out infinite; }

  /* ---------- 5. ripple ---------------------------------------------
     One delegated listener for the whole app: a ring expands from the
     point of contact and fades. Cheaper and steadier than a ripple per
     element, and it inherits the element's own border radius. */
  @keyframes rippleOut {
    from { transform: scale(.15); opacity: .55; }
    to   { transform: scale(2.6); opacity: 0; }
  }
  .ripple {
    position: absolute; border-radius: 50%; pointer-events: none;
    background: radial-gradient(circle, var(--line2), rgba(43,48,73,0) 70%);
    transform: scale(.15); opacity: .55;
    animation: rippleOut .58s cubic-bezier(.22,1,.36,1) forwards;
    z-index: 2;
  }
  button, .ltab, .bbc-tab, .lrow, .tile, .cchip { position: relative; overflow: hidden; }
  button:active, .ltab:active { transform: scale(.965); }
  button, .ltab, .bbc-tab, .lrow { transition: transform .14s cubic-bezier(.22,1,.36,1); }

  /* ---------- 6. panels ---------------------------------------------
     Content staggers in. The nth-child delays are in CSS rather than JS so
     that lists built by six different loaders all stagger the same way
     without any of them having to know this exists. */
  @keyframes itemIn {
    from { opacity: 0; transform: translate3d(0, 10px, 0); }
    to   { opacity: 1; transform: none; }
  }
  .domains > *, .lrows > *, .bbc-list > *, .gitems > * {
    animation: itemIn .3s cubic-bezier(.22,1,.36,1) both;
  }
  .domains > *:nth-child(1),  .lrows > *:nth-child(1),  .bbc-list > *:nth-child(1) { animation-delay: .02s; }
  .domains > *:nth-child(2),  .lrows > *:nth-child(2),  .bbc-list > *:nth-child(2) { animation-delay: .05s; }
  .domains > *:nth-child(3),  .lrows > *:nth-child(3),  .bbc-list > *:nth-child(3) { animation-delay: .08s; }
  .domains > *:nth-child(4),  .lrows > *:nth-child(4),  .bbc-list > *:nth-child(4) { animation-delay: .11s; }
  .domains > *:nth-child(5),  .lrows > *:nth-child(5),  .bbc-list > *:nth-child(5) { animation-delay: .14s; }
  .domains > *:nth-child(n+6), .lrows > *:nth-child(n+6), .bbc-list > *:nth-child(n+6) { animation-delay: .17s; }

  /* ---------- 7. active level pill ---------------------------------- */
  @keyframes pillShimmer {
    from { background-position: -160% 0; }
    to   { background-position: 260% 0; }
  }
  .ltab.on, .bbc-tab.on, .lvl.on {
    background-image: linear-gradient(100deg, var(--surf-4) 20%, var(--fill-navy3) 45%, var(--surf-4) 70%);
    background-size: 220% 100%;
    animation: pillShimmer 4.6s ease-in-out infinite;
  }
  .bbc-lvl.lvl-A1 { background-image: linear-gradient(100deg,var(--surf-2),var(--surf-6),var(--surf-2)); background-size:220% 100%; }
  .bbc-lvl.lvl-A2 { background-image: linear-gradient(100deg,var(--surf-3),var(--surf-6),var(--surf-3)); background-size:220% 100%; }
  .bbc-lvl.lvl-B1 { background-image: linear-gradient(100deg,var(--surf-3),var(--surf-6),var(--surf-3)); background-size:220% 100%; }
  .bbc-lvl.lvl-B2 { background-image: linear-gradient(100deg,var(--surf-3),var(--surf-6),var(--surf-3)); background-size:220% 100%; }
  .bbc-lvl.lvl-C1 { background-image: linear-gradient(100deg,var(--surf-3),var(--red-ink),var(--surf-3)); background-size:220% 100%; }
  .bbc-lvl { animation: pillShimmer 7s ease-in-out infinite; }

  /* ---------- 8. audio ----------------------------------------------
     While something is playing: bars in the play button, and a conic ring on
     the track button for real progress. */
  @keyframes eq { 0%,100% { transform: scaleY(.3); } 50% { transform: scaleY(1); } }

  .playing, .bbc-play.on {
    position: relative;
  }
  .playing::before, .bbc-play.on::before {
    content: ''; position: absolute; inset: -1px; border-radius: inherit;
    background: conic-gradient(from -90deg, var(--gold-ink) var(--p, 0turn), transparent 0);
    -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 2px), var(--ink-1) calc(100% - 1px));
    mask: radial-gradient(farthest-side, transparent calc(100% - 2px), var(--ink-1) calc(100% - 1px));
    pointer-events: none;
  }
  .eqbar {
    display: inline-flex; align-items: flex-end; gap: 2px; height: 13px;
    margin-left: 7px; vertical-align: -2px;
  }
  .eqbar i {
    width: 2.5px; height: 100%; border-radius: 2px; background: currentColor;
    transform-origin: bottom; animation: eq .9s ease-in-out infinite;
  }
  .eqbar i:nth-child(2) { animation-delay: .16s; }
  .eqbar i:nth-child(3) { animation-delay: .32s; }
  .eqbar i:nth-child(4) { animation-delay: .48s; }

  /* ---------- 9. header + counter ---------------------------------- */
  @counter { }
  @keyframes countPop { from { transform: scale(1.28); filter: brightness(1.6); } to { transform: none; } }
  .count.pop { animation: countPop .5s cubic-bezier(.22,1,.36,1); }
  @keyframes tileIn {
    from { opacity: 0; transform: translate3d(0, -6px, 0) scale(.9); }
    to   { opacity: 1; transform: none; }
  }
  .hbtn, .tile { animation: tileIn .3s cubic-bezier(.22,1,.36,1) both; }
  .hbtn:nth-child(2) { animation-delay: .03s; }
  .hbtn:nth-child(3) { animation-delay: .06s; }
  .hbtn:nth-child(4) { animation-delay: .09s; }
  .hbtn:nth-child(5) { animation-delay: .12s; }
  .hbtn:nth-child(6) { animation-delay: .15s; }
  .hbtn:nth-child(7) { animation-delay: .18s; }

  /* ---------- 10. toasts ----------------------------------------------
     Short messages that must not be part of the conversation: a microphone
     that was denied, a clip that needs a network. They land above the
     composer, speak politely to a screen reader, and leave on their own. */
  @keyframes toastIn {
    from { opacity: 0; transform: translate3d(0, 16px, 0) scale(.94); }
    to   { opacity: 1; transform: none; }
  }
  @keyframes toastOut {
    from { opacity: 1; transform: none; }
    to   { opacity: 0; transform: translate3d(0, 8px, 0) scale(.97); }
  }
  .toast-host {
    position: fixed; left: 50%; transform: translateX(-50%);
    bottom: calc(88px + env(safe-area-inset-bottom, 0px));
    z-index: 40; display: flex; flex-direction: column; gap: 8px;
    align-items: center; pointer-events: none;
    width: min(560px, calc(100vw - 28px));
  }
  .toast {
    pointer-events: auto; max-width: 100%;
    padding: 11px 15px; border-radius: 13px;
    background: var(--fill-navy);
    border: 1px solid var(--navy); color: var(--on-fill);
    font-size: 13px; line-height: 1.5; text-align: center;
    box-shadow: 0 14px 40px rgba(74,58,30, .6);
    animation: toastIn .32s cubic-bezier(.22,1,.36,1) both;
  }
  .toast.out { animation: toastOut .26s ease-in forwards; }
  @media (min-width: 900px) {
    .toast-host { bottom: 96px; }
  }

  /* ---------- 12. the learning path ------------------------------------
     A page of seven level spaces, one written course, and its examination.
     Everything here is keyed on the page's own grid, so a level with a course
     and a level without look like the same kind of thing - which is the point:
     the difference is the button, not the card. */
  /* The header tiles are flex boxes, and a class rule beats the browser's
     [hidden] default - so the path tile, which only appears after a level
     check, needs saying twice. */
  .hbtn[hidden] { display: none; }
  .path-wrap { width: 100%; max-width: 1060px; margin: 0 auto; }
  .path-head { margin-bottom: 18px; }
  .path-kicker {
    font-size: 11px; letter-spacing: .09em; text-transform: uppercase;
    font-weight: 800; color: var(--muted); margin: 0 0 6px;
  }
  .path-h {
    font-size: clamp(21px, 2.4vw, 27px); line-height: 1.25; margin: 0 0 8px;
    font-family: var(--font-display); color: var(--ink); letter-spacing: -.3px;
  }
  .path-h-fa { font-size: 15px; color: var(--muted); font-weight: 600; margin: -4px 0 8px; }
  .path-sub {
    font-size: 13.5px; line-height: 1.75; color: var(--muted);
    margin: 0 0 6px; max-width: 74ch;
  }
  .path-sub b { color: var(--ink); }
  .path-meta { font-size: 12px; color: var(--dim); margin: 6px 0 0; }
  .path-foot { font-size: 12px; line-height: 1.7; color: var(--dim); margin-top: 18px; max-width: 74ch; }
  .path-empty { font-size: 13.5px; color: var(--muted); padding: 18px 0; }
  .path-back {
    background: none; border: 0; padding: 0 0 12px; cursor: pointer;
    font-family: inherit; font-size: 12.5px; font-weight: 700; color: var(--navy-ink);
  }
  .path-back:hover { color: var(--focus); }
  .path-back:focus-visible { outline: 2px solid var(--focus); outline-offset: 3px; }

  .path-btn {
    font-family: inherit; font-size: 12.5px; font-weight: 700; cursor: pointer;
    padding: 9px 15px; border-radius: 11px; border: 1px solid transparent;
    background: var(--fill-navy); color: var(--on-fill);
    transition: background .16s, border-color .16s, transform .12s;
  }
  .path-btn:hover { background: var(--navy); }
  .path-btn:active { transform: scale(.97); }
  .path-btn:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
  .path-btn.ghost { background: rgba(60,64,91,.10); color: var(--navy-ink); border-color: rgba(60,64,91,.28); }
  .path-btn.ghost:hover { background: rgba(60,64,91,.18); }
  .path-btn[disabled] { opacity: .5; cursor: not-allowed; background: rgba(60,64,91,.10); color: var(--muted); }
  .path-link {
    background: none; border: 0; padding: 0; cursor: pointer; font-family: inherit;
    font-size: 13px; font-weight: 700; color: var(--navy-ink); text-align: start;
  }
  .path-link:hover { color: var(--focus); text-decoration: underline; }

  .path-bar {
    display: block; height: 8px; border-radius: 99px; overflow: hidden;
    background: rgba(60,64,91,.16);
  }
  .path-bar.big { height: 12px; }
  .path-bar i {
    display: block; height: 100%; border-radius: inherit;
    background: linear-gradient(90deg, var(--gold), var(--gold2));
    transition: width .3s cubic-bezier(.22,1,.36,1);
  }

  /* ---- the seven level cards ---- */
  .plv-grid {
    display: grid; gap: 14px;
    grid-template-columns: repeat(auto-fit, minmax(238px, 1fr));
  }
  .plv {
    display: flex; flex-direction: column; gap: 7px;
    border: 1px solid var(--line); border-radius: 16px; padding: 15px 16px 14px;
    background: var(--card); box-shadow: 0 1px 2px rgba(74,58,30,.05);
  }
  .plv-current { border-color: rgba(232,191,95,.85); box-shadow: 0 0 0 3px rgba(232,191,95,.22); }
  .plv-done { border-color: rgba(88,140,84,.55); }
  .plv-locked, .plv-awaiting, .plv-past { background: rgba(60,64,91,.04); }
  .plv-locked .plv-name, .plv-awaiting .plv-name, .plv-past .plv-name { color: var(--muted); }
  .plv-top { display: flex; align-items: center; gap: 8px; }
  .plv-badge {
    font-size: 12.5px; font-weight: 800; letter-spacing: .02em;
    padding: 3px 9px; border-radius: 999px; color: var(--navy-ink);
    background: rgba(60,64,91,.12); border: 1px solid rgba(60,64,91,.24);
  }
  .plv-current .plv-badge { background: rgba(232,191,95,.32); border-color: rgba(201,138,22,.5); }
  .plv-done .plv-badge { background: rgba(88,140,84,.20); border-color: rgba(88,140,84,.5); }
  .plv-state { margin-inline-start: auto; font-size: 10.5px; font-weight: 700; color: var(--muted); text-align: end; }
  .plv-state .fa { display: block; font-size: 10px; font-weight: 500; opacity: .85; }
  .plv-name { font-size: 16.5px; margin: 2px 0 0; font-family: var(--font-display); color: var(--ink); }
  .plv-fa { display: block; font-size: 12.5px; font-weight: 500; color: var(--muted); }
  .plv-can { font-size: 12px; line-height: 1.65; color: var(--muted); margin: 0; }
  .plv-note { font-size: 11.5px; line-height: 1.6; color: var(--dim); margin: 2px 0 0; }
  .plv-prog { margin-top: 4px; }
  .plv-foot { font-size: 11px; color: var(--dim); margin: 2px 0 0; }
  .plv-actions { margin-top: auto; padding-top: 8px; }
  .plv-actions .path-btn { width: 100%; }
  .plv-unit-meta { font-size: 11px; font-weight: 600; color: var(--dim); }

  /* ---- where you are, and what to open next ----
     One band above the seven cards: the assessed level on the left, the
     progress through its course in the middle, and the one button a learner
     should press on the right. The band is the answer to "what now?"; the
     grid below is the map. */
  .path-band {
    display: flex; flex-wrap: wrap; align-items: center; gap: 14px 22px;
    border: 1px solid var(--line); border-radius: 18px; padding: 15px 18px;
    margin: 0 0 16px; background: var(--card);
    box-shadow: 0 1px 2px rgba(74,58,30,.05);
  }
  .path-band-l { min-width: 0; flex: 1 1 220px; }
  .path-band-k {
    font-size: 10px; letter-spacing: .09em; text-transform: uppercase;
    font-weight: 800; color: var(--muted); margin: 0 0 4px;
  }
  .path-band-v {
    font-size: 17px; font-weight: 700; color: var(--ink); margin: 0;
    font-family: var(--font-display); letter-spacing: -.2px;
  }
  .path-band-s { font-size: 11.5px; color: var(--muted); margin: 3px 0 0; line-height: 1.55; }
  .path-band-m { flex: 1 1 240px; min-width: 0; }
  .path-band-p { font-size: 11px; color: var(--dim); margin: 5px 0 0; }
  .path-band-r { flex: 0 0 auto; }

  /* ---- the level dashboard ----
     Units in the reading column, the state of the level beside them. On a
     phone the aside stacks under the units; on a laptop it stays in view while
     the units scroll, because the examination and the next lesson are the two
     things a learner looks for between lessons. */
  .pldash { display: grid; gap: 18px; align-items: start; }
  .pldash-main { display: flex; flex-direction: column; gap: 14px; min-width: 0; }
  .pldash-side { display: flex; flex-direction: column; gap: 12px; min-width: 0; }
  @media (min-width: 980px) {
    .pldash { grid-template-columns: minmax(0, 1fr) 300px; }
    .pldash-side { position: sticky; top: 14px; }
  }
  .pcard {
    border: 1px solid var(--line); border-radius: 16px; padding: 14px 15px 15px;
    background: var(--card); box-shadow: 0 1px 2px rgba(74,58,30,.05);
  }
  .pcard-h {
    font-size: 10px; letter-spacing: .09em; text-transform: uppercase;
    font-weight: 800; color: var(--muted); margin: 0 0 10px;
  }
  .pcard .psk + .psk { margin-top: 9px; }
  .pnext-t { font-size: 13.5px; font-weight: 700; color: var(--ink); margin: 0; line-height: 1.45; }
  .pnext-u { font-size: 10.5px; font-weight: 800; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); margin: 0 0 4px; }
  .pnext-s { font-size: 11.5px; line-height: 1.65; color: var(--muted); margin: 6px 0 10px; }
  .pcard .path-btn { width: 100%; }

  /* ---- a unit, with its number and its own count ---- */
  .punit-head { display: flex; align-items: flex-start; gap: 11px; }
  .punit-badge {
    flex: 0 0 auto; width: 30px; height: 30px; border-radius: 10px;
    display: grid; place-items: center; font-size: 12px; font-weight: 800;
    color: var(--gold-ink); background: rgba(232,191,95,.22);
    border: 1px solid rgba(201,138,22,.32);
  }
  .punit-head-t { min-width: 0; flex: 1 1 auto; }
  .punit-head .punit-n { display: block; margin: 0 0 3px; }
  .punit-count {
    flex: 0 0 auto; font-size: 10.5px; font-weight: 700; color: var(--dim);
    padding: 3px 8px; border-radius: 999px; background: rgba(60,64,91,.07);
    white-space: nowrap;
  }

  /* ---- the examination card, inside the aside ---- */
  .pldash-side .pexam { margin-top: 0; flex-wrap: wrap; }
  .pldash-side .pexam .path-btn { width: 100%; }

  /* ---- a lesson page reads across the panel, not down a column ----
     Prose keeps a readable measure; the rail beside it carries the things a
     learner looks for between exercises - where they are, what is in the
     lesson, and what comes next - so the page fills the panel instead of
     leaving half of it empty. */
  .path-wrap.pwide { max-width: 1180px; }
  .pwide .plx-en, .pwide .plx-fa,
  .pwide .ppass-en, .pwide .ppass-fa { max-width: 82ch; }
  .pwide .punit-goal, .pwide .path-sub { max-width: 84ch; }
  .plesson-cols { display: grid; gap: 18px; align-items: start; }
  .plesson-main { min-width: 0; }
  .plesson-rail { display: flex; flex-direction: column; gap: 12px; min-width: 0; }
  @media (min-width: 1040px) {
    .plesson-cols { grid-template-columns: minmax(0, 1fr) 262px; }
    .plesson-rail { position: sticky; top: 14px; }
  }
  .plesson-rail .path-btn { width: 100%; }

  /* ---- the course page ---- */
  .path-total { margin: 14px 0 4px; max-width: 520px; }
  .path-total-top {
    display: flex; justify-content: space-between; align-items: baseline;
    font-size: 12px; color: var(--muted); margin-bottom: 6px;
  }
  .path-total-top b { font-size: 13px; color: var(--ink); }
  .pskills {
    display: grid; gap: 11px 18px; margin: 18px 0 22px;
    grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  }
  .psk { display: flex; flex-direction: column; gap: 5px; }
  .psk-top { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; }
  .psk-name { font-size: 12px; font-weight: 700; color: var(--ink); }
  .psk-num { font-size: 10.5px; color: var(--dim); }
  .punits { display: flex; flex-direction: column; gap: 14px; }
  .punit {
    border: 1px solid var(--line); border-radius: 16px; padding: 15px 17px 12px;
    background: var(--card);
  }
  .punit-head { display: flex; align-items: baseline; gap: 10px; }
  .punit-n {
    font-size: 10px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase;
    color: var(--muted);
  }
  .punit-title { font-size: 16px; margin: 0; font-family: var(--font-display); color: var(--ink); }
  .punit-fa { font-size: 12px; font-weight: 500; color: var(--muted); margin-inline-start: 8px; }
  .punit-goal { font-size: 12px; line-height: 1.65; color: var(--muted); margin: 5px 0 0; }
  .plessons { list-style: none; margin: 11px 0 0; padding: 0; }
  .plesson {
    display: grid; grid-template-columns: 26px minmax(0, 1fr) auto 42px;
    align-items: center; gap: 10px; padding: 7px 0;
    border-top: 1px solid var(--line2);
  }
  .plesson:first-child { border-top: 0; }
  .pdot {
    width: 24px; height: 24px; border-radius: 50%; display: grid; place-items: center;
    font-size: 10.5px; font-weight: 800; color: var(--muted);
    background: rgba(60,64,91,.10); border: 1px solid rgba(60,64,91,.18);
  }
  .plesson.done .pdot { color: var(--on-fill); background: var(--fill-navy); border-color: transparent; }
  .plesson-main {
    display: flex; flex-direction: column; gap: 1px; min-width: 0;
    background: none; border: 0; padding: 2px 0; cursor: pointer; text-align: start;
    font-family: inherit;
  }
  .plesson-title { font-size: 13.5px; font-weight: 600; color: var(--ink); }
  .plesson-main:hover .plesson-title { color: var(--focus); }
  .plesson-main:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; border-radius: 6px; }
  .plesson-fa { font-size: 11.5px; color: var(--muted); }
  .pskill {
    font-size: 10px; font-weight: 800; letter-spacing: .04em; text-transform: uppercase;
    padding: 3px 8px; border-radius: 999px; color: var(--navy-ink);
    background: rgba(60,64,91,.10); white-space: nowrap;
  }
  .pskill-grammar { background: rgba(168,122,30,.16); color: var(--gold-ink); }
  .pskill-vocabulary { background: rgba(96,88,160,.16); color: var(--violet-ink, var(--navy-ink)); }
  .pskill-reading { background: rgba(70,120,84,.16); color: var(--leaf-ink, var(--navy-ink)); }
  .pskill-listening { background: rgba(44,112,132,.16); color: var(--cyan-ink, var(--navy-ink)); }
  .pskill-writing { background: rgba(150,70,96,.16); color: var(--rose-ink, var(--navy-ink)); }
  .pskill-speaking { background: rgba(70,86,150,.16); color: var(--indigo-ink, var(--navy-ink)); }
  .pskill-review { background: rgba(60,64,91,.12); color: var(--muted); }
  .plesson-score { font-size: 11px; color: var(--dim); text-align: end; }

  .pexam {
    display: flex; align-items: center; justify-content: space-between; gap: 14px;
    margin-top: 18px; padding: 15px 17px; border-radius: 16px;
    border: 1px solid var(--line); background: var(--card);
  }
  .pexam-ready { border-color: rgba(232,191,95,.7); }
  .pexam-done { border-color: rgba(88,140,84,.55); }
  .pexam-k { font-size: 10.5px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); margin: 0; }
  .pexam-t { font-size: 14px; margin: 4px 0 0; color: var(--ink); }
  .pexam-lock { font-size: 18px; opacity: .6; }

  /* ---- a lesson ---- */
  .pblock { margin: 0 0 18px; }
  .pblock-h {
    font-size: 11px; font-weight: 800; letter-spacing: .09em; text-transform: uppercase;
    color: var(--muted); margin: 0 0 10px;
  }
  .pblock-sub { font-size: 12px; color: var(--dim); margin: -4px 0 10px; }
  .plx-en { font-size: 13.5px; line-height: 1.8; color: var(--ink); margin: 0 0 4px; max-width: 74ch; }
  .plx-fa { font-size: 12.5px; line-height: 1.9; color: var(--muted); margin: 0 0 14px; max-width: 74ch; }
  .plexs { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }
  .plex {
    display: grid; grid-template-columns: minmax(0,1fr) auto; gap: 4px 10px;
    align-items: center; padding: 9px 12px; border-radius: 12px;
    background: rgba(60,64,91,.05); border: 1px solid var(--line2);
  }
  .plex-en { font-size: 13.5px; color: var(--ink); grid-column: 1; }
  .plex-fa { font-size: 12px; color: var(--muted); grid-column: 1; }
  .path-play {
    grid-column: 2; grid-row: 1 / span 2; justify-self: end;
    border: 1px solid rgba(60,64,91,.24); background: rgba(60,64,91,.07);
    border-radius: 10px; width: 34px; height: 34px; cursor: pointer;
    font-size: 13px; color: var(--navy-ink);
  }
  .path-play:hover { background: rgba(60,64,91,.16); }
  .path-play.big { width: auto; height: 36px; padding: 0 14px; font-size: 12.5px; font-weight: 700; margin-bottom: 10px; }
  .path-play:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }

  .ppass {
    border: 1px solid var(--line); border-radius: 14px; padding: 14px 16px;
    background: rgba(60,64,91,.045); margin: 0 0 18px;
  }
  .pexam-pass { border: 1px solid var(--line); border-radius: 14px; padding: 14px 16px; margin-bottom: 14px; background: var(--card); }
  .ppass-t { font-size: 12px; font-weight: 800; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); margin: 0 0 8px; }
  .ppass-en { font-size: 14px; line-height: 1.85; color: var(--ink); margin: 0 0 8px; max-width: 74ch; }
  .ppass-fa { font-size: 12.5px; line-height: 1.95; color: var(--muted); margin: 0; max-width: 74ch; }

  .pdia { border: 1px solid var(--line); border-radius: 14px; padding: 13px 15px; margin: 0 0 18px; background: var(--card); }
  .pdia-k { font-size: 11px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); margin: 0 0 8px; }
  .pdia-row {
    display: grid; grid-template-columns: 18px minmax(0,1fr) 34px; gap: 2px 8px;
    padding: 5px 0; border-top: 1px solid var(--line2); align-items: center;
  }
  .pdia-row:first-of-type { border-top: 0; }
  .pdia-who { font-size: 11px; font-weight: 800; color: var(--muted); }
  .pdia-en { font-size: 13px; color: var(--ink); }
  .pdia-fa { grid-column: 2; font-size: 11.5px; color: var(--muted); }
  .pdia-row .path-play { width: 28px; height: 28px; font-size: 11px; }

  .pguide, .pex {
    border: 1px solid var(--line); border-radius: 14px; padding: 13px 15px;
    background: var(--card); margin-bottom: 11px;
  }
  .pex.ok { border-color: rgba(88,140,84,.6); }
  .pex.bad { border-color: rgba(182,72,72,.6); }
  .pex-top { display: flex; align-items: center; gap: 8px; margin-bottom: 7px; }
  .pex-n {
    width: 22px; height: 22px; border-radius: 50%; display: grid; place-items: center;
    font-size: 11px; font-weight: 800; color: var(--muted);
    background: rgba(60,64,91,.10);
  }
  .pex-kind { font-size: 10px; font-weight: 800; letter-spacing: .07em; text-transform: uppercase; color: var(--dim); }
  .pq { font-size: 14px; line-height: 1.6; color: var(--ink); margin: 0 0 4px; }
  .pq-fa { font-size: 12px; line-height: 1.7; color: var(--muted); margin: 0 0 10px; }
  .pops { display: flex; flex-direction: column; gap: 6px; }
  .popt {
    display: flex; align-items: center; gap: 9px; text-align: start;
    font-family: inherit; font-size: 13px; color: var(--ink); cursor: pointer;
    padding: 9px 12px; border-radius: 11px; border: 1px solid rgba(60,64,91,.22);
    background: rgba(60,64,91,.04);
  }
  .popt:hover { background: rgba(60,64,91,.10); }
  .popt.on { border-color: var(--focus); background: rgba(232,191,95,.18); }
  .popt.right { border-color: rgba(88,140,84,.75); background: rgba(88,140,84,.14); }
  .popt.wrong { border-color: rgba(182,72,72,.7); background: rgba(182,72,72,.12); }
  .popt[disabled] { cursor: default; }
  .popt-k { font-size: 10.5px; font-weight: 800; color: var(--muted); width: 12px; }
  .pwhy { font-size: 12px; line-height: 1.7; color: var(--muted); margin: 9px 0 0; }
  .pgap {
    font-family: inherit; font-size: 14px; width: 8.5em; padding: 4px 8px;
    border-radius: 8px; border: 1px dashed rgba(60,64,91,.4);
    background: rgba(60,64,91,.06); color: var(--ink); margin: 0 4px;
  }
  .pgap:focus { outline: 2px solid var(--focus); outline-offset: 1px; }
  .phint { font-size: 11.5px; color: var(--dim); margin: 8px 0 0; }
  .pwrite {
    font-family: inherit; font-size: 13.5px; line-height: 1.7; width: 100%;
    padding: 10px 12px; border-radius: 11px; resize: vertical;
    border: 1px solid rgba(60,64,91,.28); background: rgba(60,64,91,.06); color: var(--ink);
  }
  .pwrite:focus { outline: 2px solid var(--focus); outline-offset: 1px; }
  .pcount { font-size: 11px; color: var(--dim); margin: 5px 0 0; text-align: end; }
  .psay { font-size: 16px; color: var(--ink); margin: 0 0 3px; font-family: var(--font-display); }
  .psay-fa { font-size: 12px; color: var(--muted); margin: 0 0 10px; }
  .prow { display: flex; gap: 8px; flex-wrap: wrap; }
  .pheard { font-size: 12px; color: var(--muted); margin: 8px 0 0; min-height: 16px; }
  .pfoot { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin-top: 18px; }
  .pok-line { font-size: 12px; color: var(--muted); margin: 0; }
  .presult { margin-top: 12px; padding: 12px 14px; border-radius: 12px; background: rgba(60,64,91,.06); }
  .pres-h { font-size: 14px; font-weight: 700; color: var(--ink); margin: 0 0 4px; }
  .pres-s { font-size: 12px; line-height: 1.65; color: var(--muted); margin: 0; }
  .pnote { font-size: 12px; line-height: 1.7; color: var(--muted); margin: 0 0 12px; }
  .plexs .prec { padding: 7px 0; border-top: 1px solid var(--line2); }
  .plexs .prec:first-child { border-top: 0; }
  .prec-fa { display: block; font-size: 11.5px; color: var(--muted); margin-top: 1px; }

  /* ---- the exam and its report ---- */
  .pexam-paper { display: flex; flex-direction: column; gap: 12px; }
  .prep {
    border: 1px solid var(--line); border-radius: 16px; padding: 18px 20px 16px;
    margin-bottom: 16px; background: var(--card);
  }
  .prep-pass { border-color: rgba(88,140,84,.6); background: rgba(88,140,84,.06); }
  .prep-fail { border-color: rgba(201,138,22,.5); }
  .prep-k { font-size: 11px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); margin: 0; }
  .prep-score { font-size: 42px; font-weight: 800; color: var(--ink); margin: 4px 0 0; line-height: 1; }
  .prep-verdict { font-size: 14px; font-weight: 700; color: var(--ink); margin: 6px 0 6px; }
  .prep-line { font-size: 12.5px; line-height: 1.7; color: var(--muted); margin: 0; max-width: 74ch; }
  .preps { display: flex; flex-direction: column; gap: 10px; margin-bottom: 18px; }
  .prep-row {
    display: grid; grid-template-columns: minmax(0,1fr) 42px;
    grid-template-areas: 'name num' 'bar bar'; gap: 5px 10px; align-items: center;
  }
  .prep-name { grid-area: name; font-size: 12.5px; font-weight: 600; color: var(--ink); }
  .prep-num { grid-area: num; font-size: 12px; color: var(--muted); text-align: end; }
  .prep-row .path-bar { grid-area: bar; }
  .prep-weak .prep-num { color: rgba(182,72,72,.95); font-weight: 700; }
  .prep-ok .prep-num { color: rgba(88,140,84,.95); font-weight: 700; }
  .prep-not .path-bar i { background: repeating-linear-gradient(45deg, var(--line), var(--line) 4px, transparent 4px, transparent 8px); }

  @media (max-width: 560px) {
    .path-wrap { max-width: none; }
    .plv-grid { grid-template-columns: 1fr; }
    .pskills { grid-template-columns: 1fr; gap: 10px; }
    .plesson { grid-template-columns: 24px minmax(0,1fr) auto; }
    .plesson-score { display: none; }
    .pexam { flex-direction: column; align-items: flex-start; }
    .prep-score { font-size: 34px; }
    .pgap { width: 6.5em; }
  }

  /* ---------- 11. the lot, off -------------------------------------
     One block turns the whole system off. Anything added above that is
     not an entrance or a tap response should be listed here too. */
  @media (prefers-reduced-motion: reduce) {
    .motes { display: none; }
    .backdrop::before, .orb.o1, .orb.o2, .orb.o3 { animation: none !important; }
    .row, .row .mav, .row.bot .msg.bot::after,
    .domains > *, .lrows > *, .bbc-list > *, .gitems > *,
    .mav.bot, #typing .msg.typing span, #typing .mav,
    .ltab.on, .bbc-tab.on, .bbc-lvl, .hbtn, .tile,
    .count.pop, .toast, .ripple,
    .mic.rec, .stt-dot, .bbc-play.on::before { animation: none !important; }
    body.speaking .mav.bot { animation: none !important; }
    .eqbar i { animation: none !important; }
    button, .ltab, .bbc-tab, .lrow { transition: none !important; }
    * { scroll-behavior: auto !important; }
  }
</style>
</head>
<body>
<div class="boot" id="boot" role="status" aria-live="polite"
     aria-label="Loading Fluentify / در حال بارگذاری">
    <div class="boot-aurora" aria-hidden="true"><i></i><i></i><i></i></div>
    <div class="boot-in">
      <div class="boot-mark" aria-hidden="true">
        <span class="boot-halo"></span>
        <span class="boot-fox-bob">
          <img class="boot-fox" src="brand/fox-mark.png" alt="" width="100"
               height="100" decoding="async">
        </span>
      </div>
      <div class="boot-brand">
        <div class="boot-name">Fluentify</div>
        <div class="boot-tag">A step a day, a win a day
          <em dir="rtl" lang="fa">هر روز یک قدم، هر روز یک برد</em></div>
      </div>
      <div class="boot-trio" aria-hidden="true">
        <span class="boot-tile">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
               stroke-linecap="round" stroke-linejoin="round">
            <path d="M4.5 5.5A1.5 1.5 0 0 1 6 4h5v15H6a1.5 1.5 0 0 1-1.5-1.5Z"/>
            <path d="M19.5 5.5A1.5 1.5 0 0 0 18 4h-5v15h5a1.5 1.5 0 0 0 1.5-1.5Z"/>
          </svg>
          <b>A word</b><small>یک واژه</small>
        </span>
        <span class="boot-tile">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
               stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 7H6.5A1.5 1.5 0 0 0 5 8.5v0A1.5 1.5 0 0 0 6.5 10H9V6.5A1.5 1.5 0 0 0 7.5 5"/>
            <path d="M15 17h2.5a1.5 1.5 0 0 0 1.5-1.5v0a1.5 1.5 0 0 0-1.5-1.5H15v3.5a1.5 1.5 0 0 0 1.5 1.5"/>
            <path d="M9 17H6.5A1.5 1.5 0 0 1 5 15.5v0A1.5 1.5 0 0 1 6.5 14H9v3.5A1.5 1.5 0 0 1 7.5 19"/>
            <path d="M15 7h2.5A1.5 1.5 0 0 1 19 8.5v0A1.5 1.5 0 0 1 17.5 10H15V6.5A1.5 1.5 0 0 1 16.5 5"/>
          </svg>
          <b>An expression</b><small>یک عبارت</small>
        </span>
        <span class="boot-tile">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
               stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 6.5A2.5 2.5 0 0 1 6.5 4h11A2.5 2.5 0 0 1 20 6.5v7A2.5 2.5 0 0 1 17.5 16H9l-4 4v-4.2A2.5 2.5 0 0 1 4 13.5Z"/>
          </svg>
          <b>A conversation</b><small>یک گفت‌وگو</small>
        </span>
      </div>
      <div class="boot-wait">
        <div class="boot-facts" id="bootfacts">
          <span class="boot-fact" id="bootfact">50 graded stories, A1 to C1</span>
          <span class="boot-factfa" id="bootfactfa" dir="rtl" lang="fa">۵۰ داستان سطح‌بندی‌شده، از A1 تا C1</span>
        </div>
        <div class="boot-loading" aria-hidden="true">
          <div class="loader"></div>
          <div class="boot-track"><i id="bootfill"></i></div>
        </div>
        <div class="boot-meta">
          <span class="boot-left">Getting your day ready</span>
          <span id="bootpct">0%</span>
        </div>
      </div>
      <div class="boot-foot">
        Reading, listening and stories at your level
        <span dir="rtl" lang="fa">خواندن، شنیدن و داستان، در سطح خودت</span>
      </div>
    </div>
  </div>

<div id="auth" class="auth" hidden>
  <div class="authcard" role="dialog" aria-modal="true" aria-labelledby="authh">
    <div class="authhero">
      <span class="authbadge"><img src="brand/fox-mark.png" alt="" width="46" height="46" decoding="async"></span>
      <div class="authhero-t">
        <b>Fluentify</b>
        <span>A step a day, a win a day<br><bdi dir="rtl" lang="fa">هر روز یک قدم، هر روز یک برد</bdi></span>
      </div>
    </div>
    <div class="authbody">
      <h2 class="authh" id="authh">Welcome back</h2>
      <p class="authsub" id="authsub">Sign in to keep your level, your certificate and your place in the stories.</p>
      <div class="authexpired" id="authexpired" hidden>
        <span>Your session ended after seven days without use. Sign in again to continue —
          <bdi dir="rtl" lang="fa">نشست پس از هفت روز بی‌استفاده بسته شد؛ دوباره وارد شو.</bdi></span>
      </div>
      <div class="authtabs" role="tablist" aria-label="Sign in or create an account">
        <button class="authtab on" type="button" role="tab" aria-selected="true" data-authtab="signin">Sign in</button>
        <button class="authtab" type="button" role="tab" aria-selected="false" data-authtab="signup">Create account</button>
      </div>
      <form id="authform" novalidate>
        <label class="authfield" data-only="signup">
          <span>Full name — نام و نام خانوادگی</span>
          <input id="authname" type="text" autocomplete="name" placeholder="Sara Ahmadi" maxlength="60">
          <small class="hint">Printed on your certificate. — روی گواهی چاپ می‌شود.</small>
        </label>
        <label class="authfield">
          <span>Username — نام کاربری</span>
          <input id="authuser" type="text" autocomplete="username" placeholder="sara" maxlength="32"
                 autocapitalize="none" spellcheck="false">
        </label>
        <label class="authfield" data-only="signup">
          <span>Email — ایمیل</span>
          <input id="authemail" type="email" autocomplete="email" placeholder="sara@example.com"
                 maxlength="254" inputmode="email" autocapitalize="none" spellcheck="false"
                 dir="ltr">
          <small class="hint">Recovers this account. — برای بازیابی حساب.</small>
        </label>
        <label class="authfield">
          <span>Password — گذرواژه</span>
          <span class="authwrap">
            <input id="authpass" type="password" autocomplete="current-password" maxlength="128"
                   data-secret="1">
            <button class="authreveal" id="authreveal" type="button" aria-label="Show password"
                    aria-pressed="false" title="Show password — نمایش گذرواژه">Show</button>
          </span>
          <small class="hint">Typed only, never pasted. — فقط تایپ؛ چسباندن ممکن نیست.</small>
        </label>
        <div class="authmeter" id="authmeter" hidden>
          <div class="authtrack" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
          <span class="authlabel" id="authlabel"><b>Choose a password</b></span>
          <ul class="authrules" id="authrules"></ul>
          <p class="authrule-fa" id="authrulesfa" lang="fa">
            دست‌کم ۸ نویسه؛ حرف بزرگ و کوچک؛ حرف و رقم؛ یکی از @#$%!</p>
        </div>
        <label class="authfield" data-only="signup">
          <span>Repeat password — تکرار گذرواژه</span>
          <input id="authpass2" type="password" autocomplete="new-password" maxlength="128"
                 data-secret="1">
        </label>
        <p class="autherr" id="autherr" role="alert"></p>
        <button class="authsubmit" id="authsubmit" type="submit">Sign in</button>
        <button class="authlink" id="resetopen" type="button" data-only="signin">
          Forgot password? — گذرواژه را فراموش کرده‌ای؟
        </button>
      </form>
      <section class="authreset" id="authreset" hidden aria-labelledby="reseth">
        <h3 class="authh" id="reseth">Reset your password</h3>
        <p class="authsub" id="resetsubtext">Confirm what this device already knows about the
          account, then choose a new password. Nothing is sent anywhere — there is nowhere to send it.</p>
        <div class="authfield">
          <span>Username — نام کاربری</span>
          <input id="resetuser" type="text" maxlength="32" autocapitalize="none" spellcheck="false">
        </div>
        <div class="authfield">
          <span>Email — ایمیل</span>
          <input id="resetmail" type="text" maxlength="254" autocapitalize="none" spellcheck="false">
          <small class="hint">The address on this account. — نشانی ثبت‌شده روی این حساب.</small>
        </div>
        <div class="authfield" id="resetnew" hidden>
          <span>New password — گذرواژهٔ تازه</span>
          <span class="authwrap">
            <input id="resetpass" type="password" autocomplete="new-password" maxlength="128"
                   data-secret="1">
            <button class="authreveal" id="resetreveal" type="button" aria-label="Show password"
                    aria-pressed="false" title="Show password — نمایش گذرواژه">Show</button>
          </span>
        </div>
        <div class="authfield" id="resetnew2" hidden>
          <span>Repeat the new password — تکرار گذرواژهٔ تازه</span>
          <input id="resetpass2" type="password" autocomplete="new-password" maxlength="128"
                 data-secret="1">
        </div>
        <div class="authmeter" id="resetmeter" hidden>
          <div class="authtrack" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
          <ul class="authrules" id="resetrules"></ul>
          <p class="authrule-fa" lang="fa">دست‌کم ۸ نویسه؛ حرف بزرگ و کوچک؛ حرف و رقم؛ یکی از @#$%!</p>
        </div>
        <p class="autherr" id="reseterr" role="alert"></p>
        <button class="authsubmit" id="resetsubmit" type="button">Continue</button>
        <button class="authback" id="resetback" type="button">
          Back to sign in — بازگشت به ورود</button>
      </section>
      <p class="authfoot">Stored on this device only · <bdi dir="rtl" lang="fa">فقط روی همین دستگاه</bdi></p>
    </div>
  </div>
</div>

<div id="cert" class="certwrap" hidden>
  <div class="certsheet" id="certsheet" role="dialog" aria-label="Certificate"></div>
  <div class="certbar">
    <button class="lv-btn" id="certpdf" type="button" data-cert="pdf">Download PDF</button>
    <button class="lv-btn ghost" type="button" data-cert="close">Close</button>
    <p class="certnote">In the print dialog choose “Save as PDF”.</p>
  </div>
</div>
  <div class="motes" id="motes" aria-hidden="true"></div>
  <div class="toast-host" id="toasthost" aria-live="polite"></div>
<div class="backdrop"></div>
<div class="vignette"></div>
<div class="grain"></div>
<div class="orb o1"></div>
<div class="orb o2"></div>
<div class="orb o3"></div>

<div class="app">
  <div class="flock" aria-hidden="true">
    <i class="wm"></i>
  </div>
  <header>
    <div class="hb"></div>
    <div class="avatar" aria-hidden="true">
      <img src="brand/fox-face.png" alt="" width="38" height="38" decoding="async">
    </div>
    <div>
      <h1>Fluentify</h1>
      <p>English &amp; Persian, one chat at a time</p>
    </div>
    <div class="spacer"></div>
    <div id="seedmeter" title="Daily seed"></div>
    <div class="status"><i></i> online</div>
    <nav class="tools" aria-label="Study panels">
            <button class="hbtn tint-amber" id="rtoggle" aria-expanded="false" title="Review saved words — واژه‌های مرور" >
        <i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m12 3.4 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17.4l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9L12 3.4Z"/></svg></i><span>Review</span></button>
      <button class="hbtn tint-amber" id="dtoggle" aria-expanded="false" title="Today's English — انگلیسی امروز" aria-label="Today — word, expression and conversation of the day">
        <i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3.4" y="4.8" width="17.2" height="16" rx="2.4"/><path d="M3.4 9.6h17.2M8.2 3.2v3.2M15.8 3.2v3.2"/><path d="M7.6 13.4h3.2v3.2H7.6z"/></svg></i><span>Today</span><span class="rbadge" id="dbadge" hidden>0</span></button>
      <button class="hbtn tint-teal" id="vtoggle" aria-expanded="false" title="Vocabulary — واژگان" aria-label="Vocabulary">
        <i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="8" y="3.2" width="12.4" height="13.6" rx="2.2"/><path d="M15.4 19.4h.6a2 2 0 0 0 2-2V8"/><path d="M16 20.8H5.6a2 2 0 0 1-2-2V8.4"/></svg></i><span>Vocab</span></button>
      <button class="hbtn tint-violet" id="gtoggle" aria-expanded="false" title="Grammar — گرامر" aria-label="Grammar">
        <i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4.2 19.4V5.6a1.8 1.8 0 0 1 1.8-1.8h8.6l4.6 4.6v11a1.8 1.8 0 0 1-1.8 1.8H6a1.8 1.8 0 0 1-1.8-1.8Z"/><path d="M14.2 3.8v4.8h4.6"/><path d="M8 12.4h7M8 16.2h4.6"/></svg></i><span>Grammar</span></button>
      <button class="hbtn tint-cyan" id="ltoggle" aria-expanded="false" title="Listening A1–C2 — شنیدن" aria-label="Listening">
        <i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4.4 15.2v-3.4a7.6 7.6 0 0 1 15.2 0v3.4"/><rect x="2.6" y="13.8" width="4.4" height="6.6" rx="2.2"/><rect x="17" y="13.8" width="4.4" height="6.6" rx="2.2"/></svg></i><span>Listen</span></button>
      <button class="hbtn tint-rose" id="ftoggle" aria-expanded="false" title="Sentences — جملات کاربردی" aria-label="Say — everyday sentences / جملات کاربردی">
        <i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.6 11.6a8.2 8.2 0 0 1-8.4 8.2 8.6 8.6 0 0 1-3.2-.6l-4.6 1.4 1.4-4.2a8.2 8.2 0 1 1 14.8-4.8Z"/><path d="M8.8 11.6h.01M12.2 11.6h.01M15.6 11.6h.01"/></svg></i><span>Say</span></button>
      <button class="hbtn tint-indigo" id="phtoggle" aria-expanded="false" title="Phonetics — تلفظ و آهنگ" aria-label="Sounds — pronunciation and rhythm / تلفظ و آهنگ">
        <i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2.8 12h1.4M7.2 7.6v8.8M11.4 4.6v14.8M15.6 8.6v6.8M19.8 10.6v2.8"/></svg></i><span>Sounds</span></button>
      <button class="hbtn tint-leaf" id="rdtoggle" aria-expanded="false" title="Reading strategies — راهبردهای خواندن" aria-label="Reading — strategies, a passage and questions">
        <i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 6.6C10.4 5.2 8.2 4.6 5 4.8v13.4c3.2-.2 5.4.4 7 1.6 1.6-1.2 3.8-1.8 7-1.6V4.8c-3.2-.2-5.4.4-7 1.8Z"/><path d="M12 6.6v13.2"/><path d="M8 8.6h1.6M8 11.6h1.6M14.4 8.6H16M14.4 11.6H16"/></svg></i><span>Reading</span></button>
      <button class="hbtn tint-violet" id="stoggle" aria-expanded="false" title="Mini stories — داستان‌های کوتاه" aria-label="Mini stories — an English story, its Persian, and questions">
        <i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4.6 5.4a1.6 1.6 0 0 1 1.6-1.6h5.2v16.4H6.2a1.6 1.6 0 0 1-1.6-1.6Z"/><path d="M19.4 5.4a1.6 1.6 0 0 0-1.6-1.6h-5.2v16.4h5.2a1.6 1.6 0 0 0 1.6-1.6Z"/><path d="M14.8 7.4h2M14.8 10.4h2"/><path d="m8.6 7.6.7 1.5 1.6.2-1.2 1.1.3 1.6-1.4-.8-1.4.8.3-1.6L6.3 9.3l1.6-.2Z"/></svg></i><span>Stories</span></button>
      <button class="hbtn tint-navy" id="btoggle" aria-expanded="false" title="Books — کتاب‌ها" aria-label="Books — lesson words from the course books">
        <i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4.4 5.2a1.8 1.8 0 0 1 1.8-1.8h3.2A1.8 1.8 0 0 1 11.2 5.2v13.4H6.2a1.8 1.8 0 0 0-1.8 1.8Z"/><path d="M19.6 5.2a1.8 1.8 0 0 0-1.8-1.8h-3.2a1.8 1.8 0 0 0-1.8 1.8v13.4h5a1.8 1.8 0 0 1 1.8 1.8Z"/></svg></i><span>Books</span></button>
      <button class="hbtn tint-violet" id="ntoggle" aria-expanded="false" title="Analyze a sentence — تحلیل گرامری جمله" aria-label="Analyze a sentence">
        <i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="10.8" cy="10.6" r="5.8"/><path d="M15.2 15.2 20 20"/><path d="M8 12.4V9.2M10.8 12.4V7.4M13.6 12.4v-3"/></svg></i><span>Analyze</span></button>
      <button class="hbtn tint-indigo" id="lvltoggle" aria-expanded="false" title="Level check — سنجش سطح" aria-label="Level check — a monthly assessment across grammar, vocabulary, reading, listening, writing and speaking"><i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4.4 19.4h15.2"/><path d="M6.4 15.6v-4.2"/><path d="M11 15.6V7.6"/><path d="M15.6 15.6v-3"/><path d="M20.2 15.6V4.6"/></svg></i><span>Level</span><span class="rbadge" id="lvlbadge" hidden>B1</span></button>
      <button class="hbtn tint-leaf" id="pathtoggle" aria-expanded="false" hidden
              title="Learning path — مسیر یادگیری" aria-label="Learning path — seven CEFR levels, from Pre-A1 to C2">
        <i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4.8 18.4c0-3.2 2.6-4.4 5-4.4h4.4c2.4 0 5-1.2 5-4.4"/><circle cx="4.8" cy="18.4" r="1.9"/><circle cx="19.2" cy="5.6" r="1.9"/></svg></i><span>Path</span><span class="rbadge" id="pathbadge" hidden></span></button>
      <button class="hbtn tint-amber" id="actoggle" aria-expanded="false" title="Account — حساب" aria-label="Account — your name, session and sign out">
        <i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="8.4" r="3.6"/><path d="M4.8 20.2a7.2 7.2 0 0 1 14.4 0"/></svg></i><span>Account</span></button>
      <button class="hbtn tint-slate" id="themetoggle" aria-pressed="false" title="Theme — پوسته" aria-label="Theme — light or dark / پوسته">
        <i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.8v2.2M12 19v2.2M2.8 12h2.2M19 12h2.2M5.5 5.5l1.6 1.6M16.9 16.9l1.6 1.6M18.5 5.5l-1.6 1.6M7.1 16.9l-1.6 1.6"/></svg></i><span>Theme</span></button>
      <button class="hbtn danger" id="clear" title="Clear conversation — پاک کردن گفتگو" aria-label="Clear conversation">
        <i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3.8 6.8h16.4M9.4 6.8V4.4h5.2v2.4"/><path d="M6.2 6.8l.9 12.4a2 2 0 0 0 2 1.9h5.8a2 2 0 0 0 2-1.9l.9-12.4"/><path d="M10.4 10.8v6M13.6 10.8v6"/></svg></i><span>Clear</span></button>
    </nav>
  </header>

  <div id="player" class="player" hidden role="region" aria-label="Listening player">
    <button id="pltoggle" class="plbtn" aria-label="Pause" title="Pause">
      <svg viewBox="0 0 20 20" aria-hidden="true"><rect x="5" y="4" width="3.6" height="12" rx="1.2"/><rect x="11.4" y="4" width="3.6" height="12" rx="1.2"/></svg>
    </button>
    <button id="plstop" class="plbtn ghost" aria-label="Stop" title="Stop">
      <svg viewBox="0 0 20 20" aria-hidden="true"><rect x="5" y="5" width="10" height="10" rx="2"/></svg>
    </button>
    <div class="plbody">
      <div class="plhead">
        <span class="plkind" id="plkind">Listening</span>
        <span class="pltitle" id="pltitle"></span>
      </div>
      <div class="pltrack" id="plseek" role="slider" tabindex="0"
           aria-label="Seek within the clip" aria-valuemin="0" aria-valuemax="100"
           aria-valuenow="0" aria-valuetext="Not started"></div>
    </div>
    <span class="pltime" id="pltime">0:00</span>
  </div>

  <div id="npanel">
    <h3>Sentence analyzer</h3>
    <div class="nbar">
      <input id="ninput" type="text" dir="ltr" autocomplete="off" spellcheck="false"
             placeholder="One English sentence… / یک جملهٔ انگلیسی…"
             aria-label="Sentence to analyze">
      <button type="button" id="ngo" class="nbtn">Analyze</button>
    </div>
    <div class="nexamples" id="nexamples"></div>
    <div class="nresult" id="nresult" aria-live="polite"></div>
  </div>

  <div id="dpanel">
    <h3>Today's English: one word, one expression, one conversation —
      <bdi class="fa" lang="fa" dir="rtl">انگلیسی امروز</bdi></h3>
    <div class="dpanelbar">
      <span class="ddate" id="ddate"></span>
      <div class="dtrack" role="progressbar" aria-label="Today's progress"
           aria-valuemin="0" aria-valuemax="3" aria-valuenow="0" id="dtrack"><i id="dfill"></i></div>
      <span class="dcount" id="dcount">0 / 3</span>
    </div>
    <div class="dcards" id="dcards"></div>
    <div class="disk">
      <button type="button" class="dibtn" id="dcardtoggle" aria-pressed="true">Keep
      today&rsquo;s English out of the chat — <bdi class="fa" lang="fa" dir="rtl">پنهان کردن کارت روزانه</bdi></button>
    </div>
  </div>

  <div id="vpanel">
    <h3>Vocabulary A1 → C2</h3>
    <div class="psearch">
      <input id="vsearch" type="search" placeholder="Search 70 domains… / جست‌وجوی دسته‌ها…"
             autocomplete="off" aria-label="Search vocabulary domains">
    </div>
    <div class="domains" id="domains"></div>
    <div class="pempty" id="vempty" hidden>No domain matches that search. / <bdi class="fa" lang="fa" dir="rtl">دسته‌ای با این جست‌وجو پیدا نشد.</bdi></div>
  </div>

  <div id="bpanel">
    <h3>Books — <bdi class="fa" lang="fa" dir="rtl">کتاب‌ها</bdi></h3>
    <div class="bbooks" id="bbooks" aria-live="polite"></div>
  </div>

  <div id="rdpanel">
    <h3>Reading strategies — <bdi class="fa" lang="fa" dir="rtl">راهبردهای خواندن</bdi></h3>
    <div class="rdbody" id="rdbody" aria-live="polite"></div>
  </div>

  <div id="stpanel">
    <h3>Mini stories — <bdi class="fa" lang="fa" dir="rtl">داستان‌های کوتاه</bdi></h3>
    <div class="stbody" id="stbody" aria-live="polite"></div>
  </div>
  <div id="lvlpanel">
    <h3>Level check — <bdi class="fa" lang="fa" dir="rtl">سنجش سطح</bdi></h3>
    <div id="lvlbody" aria-live="polite"></div>
  </div>
  <div id="wqpanel">
    <h3>Weekly quiz — <bdi class="fa" lang="fa" dir="rtl">آزمون هفتگی</bdi></h3>
    <div id="wqbody" aria-live="polite"></div>
  </div>
  <div id="prpanel">
    <h3>Practice — <bdi class="fa" lang="fa" dir="rtl">تمرین</bdi></h3>
    <div id="prbody" aria-live="polite"></div>
  </div>
  <div id="acpanel">
    <h3>Account — <bdi class="fa" lang="fa" dir="rtl">حساب</bdi></h3>
    <div id="acbody" aria-live="polite"></div>
  </div>

    <div id="pathpanel">
    <h3>Learning path — <bdi class="fa" lang="fa" dir="rtl">مسیر یادگیری</bdi></h3>
    <div id="pathbody"></div>
  </div>

<div id="gpanel">
    <h3>English grammar lessons &amp; practice (click = lesson · ✏️ = practice)</h3>
    <div class="domains" id="gtopics"></div>
  </div>

  <div id="fpanel">
    <h3>Everyday sentences A1 → C2</h3>
    <div class="wdetail" id="wdetail" aria-live="polite"></div>
    <div class="domains" id="ftopics"></div>
  </div>

  <div id="lpanel">
    <h3>Listening practice A1 → C2</h3>
    <div id="llevels"></div>
  </div>

  <div id="phpanel">
    <h3>The sounds that make English fluent</h3>
    <div class="phrail" id="phrail" role="tablist" aria-label="Pronunciation topics"></div>
    <div class="phview" id="phview"></div>
  </div>

  <div id="rpanel">
    <h3>Your review list</h3>
    <div class="rtop" id="rtop"></div>
    <div class="rbody" id="rbody"></div>
  </div>

  <div class="chatwrap">
    <div id="chat" role="log" aria-live="polite"
         aria-relevant="additions" aria-label="Conversation"></div>
    <button id="jump" class="jump" aria-label="Scroll to the latest message"
            title="Latest ↓"><svg viewBox="0 0 16 16" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round"
            stroke-linejoin="round" aria-hidden="true"><path d="M8 3v10M3.5 8.5L8 13l4.5-4.5"/></svg></button>
    <!-- The one way into Practice: a circular control that unfolds the six
         activities, each a full page of its own. -->
    <section id="prdrawer" class="prdrawer" role="dialog" aria-modal="false"
             aria-label="Practice — تمرین" aria-hidden="true">
      <div class="prdhead">
        <span class="prdmark" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
               stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="7.6"/><circle cx="12" cy="12" r="3.1"/>
            <path d="M12 1.9v2.6M12 19.5v2.6M1.9 12h2.6M19.5 12h2.6"/></svg>
        </span>
        <span class="prdtitle">Practice
          <small class="fa" dir="rtl" lang="fa">تمرین</small></span>
        <button type="button" class="prdclose" data-pr-drawer="close"
                aria-label="Close practice / بستن تمرین" title="Close / بستن">
          <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2"
               stroke-linecap="round" aria-hidden="true"><path d="M4 4l8 8M12 4l-8 8"/></svg>
        </button>
      </div>
      <nav class="prdnav" id="prdnav" aria-label="Practice activities — تمرین"></nav>
      <p class="prdfoot">Each drill opens as a full page.
        <span class="fa" dir="rtl" lang="fa">هر تمرین در برگهٔ کامل باز می‌شود.</span></p>
    </section>
    <button type="button" id="prfab" class="prfab" aria-expanded="false"
            aria-controls="prdrawer" aria-label="Practice — تمرین"
            title="Practice — تمرین">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
           stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <circle cx="12" cy="12" r="7.6"/><circle cx="12" cy="12" r="3.1"/>
        <path d="M12 1.9v2.6M12 19.5v2.6M1.9 12h2.6M19.5 12h2.6"/>
      </svg>
    </button>
  </div>

  <div class="stt-panel" id="stt" hidden></div>
  <form id="composer">
    <!-- The band the little fox climbs into. Its bottom edge is the top edge
         of the send box, and it clips: everything below that line is inside
         the box and stays out of sight, so she is only ever drawn in the part
         that has risen out of it. -->
    <div class="foxslot" aria-hidden="true">
      <div class="foxpeek" id="chatfox">
        <span class="foxshade"></span>
        <div class="foxhead">
          <!-- Drawn rather than photographed: she is a white ghost with one
               mint line, and the glow is her own gradient. The mascot's ears,
               cheeks and muzzle are kept, and nothing else is. -->
          <svg class="foxpic" viewBox="0 0 60 60" aria-hidden="true" focusable="false">
            <defs>
              <radialGradient class="foxglow" id="foxglow" cx="50%" cy="52%" r="52%">
                <stop class="g1" offset="0"/>
                <stop class="g2" offset=".58"/>
                <stop class="g3" offset="1"/>
              </radialGradient>
            </defs>
            <ellipse cx="30" cy="33" rx="29" ry="28" fill="url(#foxglow)"/>
            <path class="foxghost"
                  d="M10.6 4.6 L19.4 13.4 C22.5 12.3 26.2 11.9 30 11.9 C33.8 11.9 37.5 12.3 40.6 13.4 L49.4 4.6 L50 26 C50.6 38 41 49 30 49 C19 49 10.4 38 10 26 Z"/>
            <g class="foxeyes">
              <ellipse cx="23.4" cy="32.4" rx="2.7" ry="3.5"/>
              <ellipse cx="36.6" cy="32.4" rx="2.7" ry="3.5"/>
            </g>
            <path class="foxnose" d="M30 36.8 l-2.1 2 h4.2 Z"/>
            <path class="foxsmile" d="M26.8 40.8 c1.5 1.9 5.4 1.9 6.9 0"/>
          </svg>
        </div>
      </div>
    </div>
    <div class="messageBox" id="messageBox">
      <button type="button" class="ico" id="gecbtn"
              aria-label="Check my English / گرامر جمله را چک کن"
              title="Check my English — گرامر جمله را چک کن">
        <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor"
             stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
          <path d="M4.5 19.5l1-4.2L15.8 5a1.8 1.8 0 0 1 2.5 0l.7.7a1.8 1.8 0 0 1 0 2.5L8.7 18.5l-4.2 1Z"/>
          <path d="M14.6 6.2l3.2 3.2"/>
        </svg>
      </button>
      <button type="button" class="ico" id="stickerbtn"
              aria-label="Fox stickers / استیکرهای روباه"
              title="Fox stickers / استیکرهای روباه"
              aria-haspopup="dialog" aria-expanded="false" aria-controls="stickerpanel">
        <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor"
             stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
          <path d="M4.4 10.4 6 3.2 10.6 5.8"/>
          <path d="M19.6 10.4 18 3.2 13.4 5.8"/>
          <path d="M4.4 10.4c0 5.4 3.4 9.8 7.6 9.8s7.6-4.4 7.6-9.8"/>
          <circle cx="9.5" cy="11.6" r="1.05" fill="currentColor" stroke="none"/>
          <circle cx="14.5" cy="11.6" r="1.05" fill="currentColor" stroke="none"/>
          <path d="M10.8 15.4h2.4l-1.2 1.7z" fill="currentColor" stroke="none"/>
        </svg>
      </button>
      <input id="input" autocomplete="off" placeholder="Type a message… / پیام بنویسید…"
             aria-label="Message / پیام">
      <button class="send" id="sendbtn" type="submit"
              aria-label="Send / ارسال" title="Send / ارسال">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M20.9 3.1 2.9 10.2l7.2 2.9 2.9 7.2 7.9-17.2Z"
                fill="none" stroke="currentColor" stroke-width="1.9"
                stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M20.9 3.1 10.1 13.1" fill="none" stroke="currentColor"
                stroke-width="1.9" stroke-linecap="round"/>
        </svg>
      </button>
    </div>
    <div id="stickerpanel" class="emoji-panel" role="dialog"
         aria-label="Fox stickers / استیکرهای روباه" hidden></div>
    <div class="limitenote" id="limitenote" role="status" aria-live="polite">
      <div class="limitrail">
        <span class="limitfill"></span>
        <span class="lockic" aria-hidden="true">🌙</span>
      </div>
      <span class="limitxt"></span>
    </div>
  </form>
</div>

<script>
/* Fluentify's mascot — the fox, cut from the one brand picture
   (brand/fox-source.png, via tools/build_brand.py). The header, the boot
   screen, the launcher icon and every message row show this same animal, and
   all of them keep the picture's transparent background: the face here
   because a full-length portrait at 26px is an orange smudge. */
const MASCOT =
  '<img class="mface" src="brand/fox-face.png" alt="" width="26" ' +
  'height="26" decoding="async">';

/* Reading a data file by name. The offline bundle defines this against its own
   data/*.json; the web build reads every section over /api instead, and the
   emoji picker is the one place that asks for a file by name. Without it here
   the picker never opened at all: the call threw, the module caught the throw,
   and the composer's emoji button hid itself rather than sit there dead. */
const _json = {};
const loadJSON = (name) => (_json[name] ||= fetch('/api/' + name).then((r) => {
  if (!r.ok) throw new Error(name + ' could not be read (HTTP ' + r.status + ')');
  return r.json();
}));

const chat = document.getElementById('chat');
const input = document.getElementById('input');
const jump = document.getElementById('jump');
let pinned = true;   // false once the reader scrolls up
function paintJump() {
  jump.classList.toggle('show', !pinned && chat.scrollHeight > chat.clientHeight + 40);
}
jump.onclick = () => {
  chat.scrollTo({top: chat.scrollHeight, behavior: 'smooth'});
  pinned = true;
  paintJump();
};
const sendbtn = document.getElementById('sendbtn');
const isFa = s => /[\u0600-\u06FF]/.test(s);
/* The learner's own marker: a sunny bird, so the two sides of the conversation
   never look alike. This is not the brand mark - the fox is. */
/* The learner's own avatar is this bird, and it wears the season the device's
   calendar is in: pink in spring, yellow in summer, orange in fall, ice blue in
   winter. The season is read from the local clock rather than a server, the
   same reason the daily rotation is - there is no server to ask, and a bird
   that is always yellow says "summer" in November.

   One palette drives both halves: the SVG's own gradients and the tile it sits
   on, so the ring around the bird is never a colour the bird isn't. */
const SEASONS = {
  spring: { season: 'spring', fa: 'بهار',
            body: ['#ffe6f1', '#ffb0d0', '#c26088'], wing: '#ff9dc3',
            belly: '#fff7fb', beak: '#a84f74', crest: '#ffc9e0', eye: '#3d1d2c',
            ring: '#eda6c4', wash: 'rgba(255,176,208,.22)' },
  summer: { season: 'summer', fa: 'تابستان',
            body: ['#ffe9a8', '#ffd257', '#b8872a'], wing: '#ffbe3d',
            belly: '#fffdf2', beak: '#b8872a', crest: '#ffd979', eye: '#4a2b00',
            ring: '#dfb457', wash: 'rgba(255,210,87,.24)' },
  fall:   { season: 'fall', fa: 'پاییز',
            body: ['#ffd9ab', '#f0913c', '#a3541a'], wing: '#e8812c',
            belly: '#fff2e2', beak: '#8e4512', crest: '#f6a95c', eye: '#3d1f06',
            ring: '#e08f45', wash: 'rgba(240,145,60,.22)' },
  winter: { season: 'winter', fa: 'زمستان',
            body: ['#eef8ff', '#c3e2f7', '#6f9dc2'], wing: '#b7dcf4',
            belly: '#ffffff', beak: '#5b829e', crest: '#d9eefc', eye: '#17324a',
            ring: '#9ac4e0', wash: 'rgba(158,201,230,.24)' },
};

/* Months are 0-based; the seasons turn on the first of March, June, September
   and December, which is the meteorological year and the one a learner's own
   calendar shows. */
function seasonOf(when) {
  const m = (when || new Date()).getMonth();
  if (m === 11 || m < 2) return 'winter';   // Dec, Jan, Feb
  if (m < 5) return 'spring';               // Mar, Apr, May
  if (m < 8) return 'summer';               // Jun, Jul, Aug
  return 'fall';                            // Sep, Oct, Nov
}

const SEASON = seasonOf();
const BIRD_PAL = SEASONS[SEASON];
/* Handed to CSS so the tile behind the bird is the same season as the bird. */
try {
  document.documentElement.dataset.season = SEASON;
  document.documentElement.style.setProperty('--season-ring', BIRD_PAL.ring);
  document.documentElement.style.setProperty('--season-wash', BIRD_PAL.wash);
} catch (e) { /* a browser without dataset is not worth failing the page for */ }

/* The bird itself. One silhouette, drawn in five pieces - tail, body, wing,
   breast, head - so the gradient has something to fall across and the 20px
   phone version still reads as a bird rather than a blob: bold shapes, no
   hairline detail that disappears below 24px, and a single highlight in the
   eye where the light comes from. */
let birdSeq = 0;
function birdSVG(p) {
  /* Every bird carries its own gradient id, and its own means *every copy*: a
     name taken from the palette was still a shared id, so the hero and the
     button that picked it - same palette, two elements - claimed one id, and a
     third copy elsewhere replaced the gradients the first two were pointing
     at. A page that draws the learner's face in the chat, in the picker and on
     the hero repaints all of them, and a gradient id that is reused across
     repaints is how a bird comes back bald. A counter cannot collide. */
  const ns = 'bird' + (++birdSeq);
  return '<svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">' +
    '<defs>' +
      '<linearGradient id="' + ns + 'Body" x1="0" y1="0" x2="1" y2="1">' +
        '<stop offset="0" stop-color="' + p.body[0] + '"/>' +
        '<stop offset="55%" stop-color="' + p.body[1] + '"/>' +
        '<stop offset="100%" stop-color="' + p.body[2] + '"/>' +
      '</linearGradient>' +
      '<radialGradient id="' + ns + 'Belly" cx="42%" cy="30%" r="72%">' +
        '<stop offset="0" stop-color="#ffffff"/>' +
        '<stop offset="100%" stop-color="' + p.belly + '"/>' +
      '</radialGradient>' +
    '</defs>' +
    /* tail, kept to one wedge so it does not read as a second bird */
    '<path d="M11.2 28.4 L4.2 20.6 L6.2 31.8 Z" fill="' + p.body[2] + '"/>' +
    /* body */
    '<ellipse cx="24" cy="27" rx="15.2" ry="12.9" fill="url(#' + ns + 'Body)"/>' +
    /* breast: the light side, which is what makes it look round rather than flat */
    '<ellipse cx="24" cy="30.4" rx="9.3" ry="7.3" fill="url(#' + ns + 'Belly)" opacity=".95"/>' +
    /* folded wing */
    '<path d="M13.4 23.5 q8.7 2.7 8.5 10.8 q-8.7-2.6-8.5-10.8Z" fill="' + p.wing + '"/>' +
    /* crest, two feathers and a gap between them */
    '<path d="M22.4 14 q.5-7.1 4.6-7.3 q-.6 4.2-1.8 6.6 q2.8-3.4 6-2.1 q-2.4 3-5 4.1Z" fill="' + p.crest + '"/>' +
    /* beak, upper and lower halves split by the seam */
    '<path d="M37 22.7 L44.2 26 L37 29.1 Z" fill="' + p.beak + '"/>' +
    '<path d="M37.2 25.9 h6.4" stroke="' + p.body[2] + '" stroke-width=".7" opacity=".55"/>' +
    /* eye, with the catch-light up and left of centre */
    '<circle cx="31.3" cy="21" r="3.4" fill="' + p.eye + '"/>' +
    '<circle cx="32.7" cy="19.7" r="1.15" fill="#fff"/>' +
    /* cheek, at 22% so it is a warmth rather than a spot */
    '<ellipse cx="34.5" cy="27.7" rx="2.9" ry="1.8" fill="' + p.body[2] + '" opacity=".22"/>' +
    /* feet, two strokes: the phone size cannot hold toes */
    '<path d="M20.8 39.3 v2.3 M27.2 39.3 v2.3" stroke="' + p.beak + '" stroke-width="1.5" stroke-linecap="round"/>' +
  '</svg>';
}

/* ---- the learner's face -------------------------------------------------
   The tile beside the learner's messages is a bird, and a bird is a palette:
   body gradient, wing, breast, beak, crest, eye, ring, wash. Six are offered -
   the four seasons the app already dresses itself in, plus a dawn and a dusk
   drawn for the pick - so the face is chosen rather than assigned. The choice
   is stored once and read wherever a message is drawn. */
const AVATARS = {
  spring: {en: 'Spring', fa: 'بهار', pal: SEASONS.spring},
  summer: {en: 'Summer', fa: 'تابستان', pal: SEASONS.summer},
  fall:   {en: 'Autumn', fa: 'پاییز', pal: SEASONS.fall},
  winter: {en: 'Winter', fa: 'زمستان', pal: SEASONS.winter},
  dawn:   {en: 'Dawn', fa: 'سپیده', pal: {
    body: ['#ffe9c7', '#f5b978', '#c9743a'], wing: '#efc08a', belly: '#fff6ea',
    beak: '#b8622f', crest: '#ffe0b0', eye: '#3a2415', ring: '#e6a866',
    wash: 'rgba(240,180,120,.22)'}},
  dusk:   {en: 'Dusk', fa: 'غروب', pal: {
    body: ['#e6e1ff', '#b3a8e8', '#6b5fa8'], wing: '#c6bdf0', belly: '#fbf9ff',
    beak: '#5c4f8c', crest: '#ded7ff', eye: '#241d43', ring: '#a99cdb',
    wash: 'rgba(160,144,220,.22)'}},
};
const AVATAR_KEY = 'fluentify.avatar';

function avatarId() {
  try {
    const saved = localStorage.getItem(AVATAR_KEY);
    if (saved && AVATARS[saved]) return saved;
  } catch (e) { /* private mode: the season is a fine default */ }
  return SEASON;
}

function avatarSVG(id) {
  const key = AVATARS[id] ? id : SEASON;
  return birdSVG(AVATARS[key].pal);
}

/* A face belongs to the learner, not to the message it was drawn beside. The
   bubbles written before a change kept the old bird, so the chat showed two
   different people - the new face on the next line, the old one above it. */
function repaintAvatarTiles() {
  document.querySelectorAll('#chat .row.user .mav').forEach((tile) => {
    if (tile.querySelector('svg')) tile.innerHTML = avatarSVG(avatarId());
  });
}

/* The tile behind the bird is ringed in the bird's own ring colour, so a
   chosen face changes the frame too and not just the animal inside it. */
function applyAvatarSkin(id) {
  const key = AVATARS[id] ? id : SEASON;
  try {
    document.documentElement.dataset.avatar = key;
    document.documentElement.style.setProperty('--season-ring', AVATARS[key].pal.ring);
    document.documentElement.style.setProperty('--season-wash', AVATARS[key].pal.wash);
  } catch (e) { /* no dataset, no ring: the bird is still drawn */ }
}
applyAvatarSkin(avatarId());

const WELCOME = "Hey! Fluentify here. Let's learn English together.";

/* The four things this tutor does well, offered as the first move. Each one
   is a sentence the engine already recognises, so a tap gets a real answer
   rather than a polite "I don't know that one". */
const STARTERS = [
  ['colors', 'Colors', 'واژگان رنگ‌ها'],
  // The query is what the user bubble will show, so it has to read the way the
  // chip does. It used to send 'present simple', which the lesson accepted as
  // a keyword but echoed back reversed, under a chip that said "Simple present".
  ['simple present', 'Simple present', 'درس حال ساده'],
  ['listen a1', 'Listen A1', 'شنیدن سطح A1'],
  ['idioms and sayings', 'Idioms', 'اصطلاح‌ها و ضرب‌المثل‌ها'],
];

function renderStarters() {
  const old = document.getElementById('starters');
  if (old) old.remove();
  const wrap = document.createElement('div');
  wrap.className = 'starters';
  wrap.id = 'starters';

  const row = document.createElement('div');
  row.className = 'schips';
  STARTERS.forEach(([query, label, fa]) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'schip';
    b.textContent = label;
    b.title = fa;
    b.onclick = () => send(query);
    row.appendChild(b);
  });

  wrap.append(row);
  chat.appendChild(wrap);
}

function now() {
  return new Date().toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
}

function escapeHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
/* ---------------------------------------------------------------- stickers
   A fox travels through a message as [fox:cute]: the composer holds the
   token, and the bubble holds the drawing. The catalogue registers itself
   when it loads, and the swap happens after the text has been escaped, so the
   picture always comes from our own data and never from what someone typed. */
const FOX_STICKERS = Object.create(null);

function registerFoxes(list) {
  (list || []).forEach((s) => { FOX_STICKERS[s.id] = s; });
}

function foxSvg(id, cls) {
  const s = FOX_STICKERS[id];
  if (!s) return '';
  return '<svg class="' + (cls || 'stk') + '" viewBox="0 0 64 64" role="img" ' +
    'aria-label="' + escapeHtml(s.name) + ' fox sticker">' + s.svg + '</svg>';
}

function stickerize(html) {
  return html.replace(/\[fox:([a-z0-9-]+)\]/g, (m, id) => foxSvg(id) || m);
}

/* A run of Persian inside an English line is wrapped in <bdi>: an isolated
   island that keeps its own right-to-left order. The spaces join it only when
   another Persian word follows, so English spacing is untouched. This is what
   puts "(فعل حال ساده)" back the right way round in an English sentence - the
   brackets stay with the English, the Persian stays right-to-left. */
/* Which way a line reads: the first *letter* decides, skipping the neutral mark
   a line usually opens with (↲, •, a bullet, a number, an emoji). Counting the
   letters instead would flip a Persian sentence to left-to-right as soon as the
   English term it quotes was longer than the Persian around it. */
function lineDir(raw) {
  /* A digit is not a script. "۳. a number of sheets" used to open on a Persian
     numeral, which is inside the Arabic block, so the whole line was laid out
     right to left and reversed the English after it. Only a letter decides,
     and the Arabic-Indic digits (\u0660-\u0669, \u06F0-\u06F9) are excluded. */
  const first = raw.match(/[\u0621-\u064A\u066E-\u06D3\u06FA-\u06FF]|[A-Za-z]/);
  return first && /[\u0621-\u064A\u066E-\u06D3\u06FA-\u06FF]/.test(first[0])
    ? 'rtl' : 'ltr';
}

/* A mixed line is tokenised once and rebuilt as three kinds of run: Persian,
   Latin, and everything neutral (spaces, punctuation, emoji). Building runs
   first, instead of wrapping the already-escaped HTML, is what keeps the
   brackets and the markup out of the pattern's way - an earlier version
   matched the letters of its own <bdi> tag.
 *
 * Persian words are joined into one run across the spaces between them, so a
 * phrase flows as one right-to-left island instead of a row of separate
 * fragments. A single space between two Latin words stays neutral, which is
 * what an inline English term inside a Persian sentence needs. */
const FA_TOKEN = /^[\u0600-\u06FF][\u0600-\u06FF\u200c\u200d\u060c\u061b\u061f\u066b\u066c]*$/;
const EN_TOKEN = /^[A-Za-z][A-Za-z0-9'\u2019._\-\/]*$/;

/* A parenthetical is lifted out before the line is split, and put back as one
   isolated unit of the line's own direction. Left in the stream, a bracket
   holding a Latin term inside a Persian sentence is three neutrals around an
   island, and the bidi algorithm is free to park the whole group at the end of
   the line - which is what it did to "(he/she/it)".
 *
 * The markers are private-use characters, not NUL: a NUL cannot travel through
 * HTML at all, and a backslash-u escape typed into a string stays six readable
 * characters instead of becoming a sentinel.
 */
const PAREN_OPEN = '\ue000';
const PAREN_CLOSE = '\ue001';
const TOKEN_RE = /[\u0600-\u06FF][\u0600-\u06FF\u200c\u200d\u060c\u061b\u061f\u066b\u066c]*|[A-Za-z][A-Za-z0-9'\u2019\/_-]*(?:\.[A-Za-z0-9][A-Za-z0-9'\u2019\/_-]*)*|[\ue000]\d+[\ue001]|\s+|[\s\S]/g;

function inlineHtml(raw, lineDirection) {
  const groups = [];
  raw = raw.replace(/\(([^()]*)\)/g, (m, inner) => {
    groups.push(inner);
    return PAREN_OPEN + (groups.length - 1) + PAREN_CLOSE;
  });
  const runs = [];
  for (const tk of raw.match(TOKEN_RE) || []) {
    const kind = FA_TOKEN.test(tk) ? 'fa' : EN_TOKEN.test(tk) ? 'en'
      : tk[0] === PAREN_OPEN ? 'paren' : 'n';
    const prev = runs[runs.length - 1];
    if (prev && prev.kind === kind && kind !== 'paren') prev.text += tk;
    else runs.push({kind, text: tk});
  }
  // fold the spaces between Persian words into the Persian run
  for (let i = 1; i < runs.length - 1; i++) {
    const space = runs[i], before = runs[i - 1], after = runs[i + 1];
    if (space.kind === 'n' && !space.text.trim() && before.kind === 'fa' &&
        after.kind === 'fa') {
      before.text += space.text + after.text;
      runs.splice(i, 2);
      i -= 2;
    }
  }
  return runs.map((run) => {
    if (run.kind === 'paren') {
      const inner = groups[Number(run.text.slice(1, -1))];
      return `<bdi class="paren" dir="${lineDirection}">(${
        inlineHtml(inner, lineDirection)})</bdi>`;
    }
    const esc = escapeHtml(run.text);
    if (run.kind === 'fa') {
      return `<bdi class="fa" lang="fa" dir="rtl">${esc}</bdi>`;
    }
    if (run.kind === 'en' && lineDirection === 'rtl') {
      return `<bdi class="lat" lang="en" dir="ltr">${esc}</bdi>`;
    }
    return esc;
  }).join('');
}

function renderText(s) {
  // one block per line, each with its own direction, its own runs and its own
  // language. A blank line keeps its height rather than collapsing.
  return s.split('\n').map((raw) => {
    if (!raw.trim()) return '<div class="bl">&nbsp;</div>';
    const dir = lineDir(raw);
    let html = stickerize(inlineHtml(raw, dir))
      .replace(/\*\*(.+?)\*\*/g, '<b>$1</b>');
    html = html.replace(/^(\s*)↲/, (m, space) => `${space}<span class="trm">↲</span>`);
    return `<div class="bl" dir="${dir}" lang="${dir === 'rtl' ? 'fa' : 'en'}">${html}</div>`;
  }).join('');
}

/* A lesson arrives as five numbered parts plus a tip, separated only by blank
   lines. Splitting on those markers is what lets each part have its own card;
   everything else about the text - the words, the order, the bilingual ↲ lines
   - is left exactly as the engine wrote it. Returns null for anything that is
   not a lesson, so every other message keeps the plain bubble. */
const GLESSON_PARTS = {'1️⃣': 'structure', '💡': 'tip', '2️⃣': 'explanation',
                       '3️⃣': 'function', '4️⃣': 'examples', '5️⃣': 'exercises'};

function parseGrammarSections(text) {
  if (!text.trimStart().startsWith('📘 English Grammar')) return null;
  const head = [];
  const sections = [];
  let cur = null;
  for (const raw of text.split('\n')) {
    const line = raw.replace(/\s+$/, '');
    const m = line.match(/^(?:([1-5]️⃣)\s*(.+)|(💡)\s*(Tip:.*))$/);
    if (m) {
      cur = { title: m[1] ? m[1] + ' ' + m[2].trim() : '💡 ' + m[4].trim(),
              body: [] };
      sections.push(cur);
      continue;
    }
    if (cur) cur.body.push(line); else head.push(line);
  }
  // A real lesson has the numbered parts; a menu or a stray mention does not.
  if (sections.length < 3) return null;
  return {
    head: head.join('\n').trim(),
    sections: sections.map((s) => ({title: s.title, body: s.body.join('\n').trim()}))
      .filter((s) => s.body),
  };
}

function renderGrammarLesson(bubble, parsed) {
  bubble.classList.add('glesson');
  bubble.textContent = '';
  if (parsed.head) {
    const h = document.createElement('div');
    h.className = 'glesson-head';
    h.innerHTML = renderText(parsed.head);
    bubble.appendChild(h);
  }
  const body = document.createElement('div');
  body.className = 'glbody';
  parsed.sections.forEach((sec) => {
    const card = document.createElement('section');
    card.className = 'gsec';
    card.dataset.kind = GLESSON_PARTS[sec.title.slice(0, sec.title.indexOf(' '))]
                        || 'structure';
    const h = document.createElement('div');
    h.className = 'gsec-h';
    h.innerHTML = renderText(sec.title);
    const b = document.createElement('div');
    b.className = 'gsec-b';
    b.innerHTML = renderText(sec.body);
    card.append(h, b);
    body.appendChild(card);
  });
  bubble.appendChild(body);
}

/* A phrase bank arrives as "💬 Title\n• english\n  ↲ فارسی" pairs.
   Render it as separate cards instead of one run-on pre-wrap block.
   Only the 💬 banner marks a phrase bank — grammar lessons also use • and ↲,
   and must stay as plain text or the parser tears them apart. */
function parsePhraseList(text) {
  if (!text.trimStart().startsWith('💬')) return null;
  const head = [];
  const pairs = [];
  let cur = null;
  for (const raw of text.split('\n')) {
    const line = raw.replace(/\s+$/, '');
    const bullet = line.match(/^\s*[•·]\s+(.*)$/);
    const arrow = line.match(/^\s*↲\s*(.*)$/);
    if (bullet) {
      cur = { en: bullet[1].trim(), fa: '' };
      pairs.push(cur);
    } else if (arrow) {
      // only a translation *directly under* a bullet belongs to it
      if (cur) cur.fa = arrow[1].trim();
    } else if (line.trim()) {
      head.push(line.trim());   // a heading ends the current pair
      cur = null;
    }
  }
  // a real bank has a translation for nearly every line
  const translated = pairs.filter((p) => p.fa).length;
  if (!pairs.length || translated < pairs.length / 2) return null;
  return { head: head.join('\n'), pairs };
}

function renderPhraseList(bubble, parsed) {
  bubble.classList.add('plist');
  bubble.textContent = '';
  if (parsed.head) {
    const h = document.createElement('div');
    h.className = 'plist-head';
    h.innerHTML = renderText(parsed.head);
    bubble.appendChild(h);
  }
  for (const p of parsed.pairs) {
    const card = document.createElement('div');
    card.className = 'pcard';
    const en = document.createElement('div');
    en.className = 'pen';
    en.innerHTML = renderText(p.en);
    card.appendChild(en);
    if (p.fa) {
      const fa = document.createElement('div');
      fa.className = 'pfa';
      fa.innerHTML = renderText(p.fa);
      card.appendChild(fa);
    }
    bubble.appendChild(card);
  }
}

// The text the user last actually sent, so a bot message can offer to try the
// question again. Commands never reach here - they are intercepted above and
// never become chat messages - so this cannot replay "open grammar section".
let lastUserText = '';

function add(text, who, opts = {}) {
  const row = document.createElement('div');
  row.className = 'row ' + who;

  // Grouping. The tutor answers in several bubbles - the reply, then a tip,
  // then a correction - and repeating the full avatar and speaker name on
  // each one reads as four separate people talking. Consecutive messages from
  // the same speaker share one.
  const prev = chat.lastElementChild;
  if (!opts.err && !opts.typing && prev &&
      prev.classList.contains('row') &&
      prev.classList.contains(who) &&
      !prev.classList.contains('typing-row')) {
    row.classList.add('grouped');
    prev.classList.add('grouped');
  }

  const av = document.createElement('div');
  av.className = 'mav' + (who === 'bot' ? ' bot' : ' me');
  av.innerHTML = who === 'bot' ? MASCOT : avatarSVG(avatarId());

  const wrap = document.createElement('div');
  wrap.className = 'bubble-wrap';

  const bubble = document.createElement('div');
  bubble.className = 'msg ' + who;
  if (opts.err) bubble.classList.add('err');
  if (isFa(text) && !/[A-Za-z]/.test(text.slice(0, 40))) bubble.classList.add('rtl');
  if (text.split('\n').length > 10) bubble.classList.add('long');
  const phrases = who === 'bot' && !opts.err && !opts.html ? parsePhraseList(text) : null;
  const lesson = who === 'bot' && !opts.err && !opts.html ? parseGrammarSections(text) : null;
  if (lesson) renderGrammarLesson(bubble, lesson);
  else if (phrases) renderPhraseList(bubble, phrases);
  // opts.html is renderAnalysis() output: already escaped field by field, and
  // escaping it a second time would print the markup instead of the analysis.
  else if (opts.html) bubble.innerHTML = text;
  else bubble.innerHTML = renderText(text);

  const meta = document.createElement('div');
  meta.className = 'meta';
  // The speaker name goes in an element rather than a bare text node so that
  // grouping can hide it - CSS cannot select a text node.
  meta.append(
    Object.assign(document.createElement('span'), {className: 'who',
      textContent: who === 'bot' ? 'Fluentify' : 'You'}),
    Object.assign(document.createElement('i'), {textContent: now()}),
  );

  // A failed message gets one tool and it is not a copy button: there is
  // nothing useful to copy, and the only thing to do about it is try again.
  if (who === 'bot' && opts.err) {
    const retry = document.createElement('button');
    retry.className = 'mtool';
    retry.textContent = '↻';
    retry.title = 'Try again — دوباره';
    retry.setAttribute('aria-label', 'Try that again');
    retry.onclick = () => {
      const again = input.value.trim();
      if (!again || busy) return;
      send(again);
    };
    const box = document.createElement('div');
    box.className = 'tools-row';
    box.appendChild(retry);
    meta.appendChild(box);
  }

  // Every bot message gets its tools: hear it, copy it, ask again.
  if (who === 'bot' && !opts.err) {
    const tools = document.createElement('div');
    tools.className = 'tools-row';

    // No speaker on a message: the per-answer speaker is gone everywhere it
    // appeared - it turned every answer into a player, and the app already
    // has a Listening section for listening. Copy and ask-again stay.
    const copyBtn = document.createElement('button');
    copyBtn.className = 'mtool';
    copyBtn.textContent = '⧉';
    copyBtn.title = 'Copy — کپی';
    copyBtn.setAttribute('aria-label', 'Copy message');
    copyBtn.onclick = async () => {
      try {
        await navigator.clipboard.writeText(text);
        copyBtn.textContent = '✓';
        setTimeout(() => (copyBtn.textContent = '⧉'), 1400);
      } catch (e) {
        copyBtn.textContent = '!';
        setTimeout(() => (copyBtn.textContent = '⧉'), 1400);
      }
    };

    // "Try that again" re-sends what the user actually asked, rather than
    // asking the bot to repeat itself - a learner who did not understand the
    // answer wants a different one, not the same words louder.
    const againBtn = document.createElement('button');
    againBtn.className = 'mtool';
    againBtn.textContent = '↻';
    againBtn.title = 'Ask again — یک بار دیگر';
    againBtn.setAttribute('aria-label', 'Ask that again');
    againBtn.hidden = !lastUserText;
    againBtn.onclick = () => {
      if (busy || !lastUserText) return;
      const again = lastUserText;
      // drop the question and the answer being retried, so the thread reads
      // as one attempt rather than three
      const rows = [...chat.querySelectorAll('.row.user, .row.bot')];
      const ui = rows.map((r) => r).filter((r) => r.classList.contains('user'));
      const lastUi = ui[ui.length - 1];
      if (lastUi) {
        let n = lastUi;
        while (n && n.nextElementSibling &&
               !n.nextElementSibling.classList.contains('user')) {
          n = n.nextElementSibling;
          n.remove();
        }
        lastUi.remove();
      }
      send(again);
    };

    tools.append(copyBtn, againBtn);
    meta.appendChild(tools);
  }

  wrap.appendChild(bubble);
  wrap.appendChild(meta);
  row.appendChild(av);
  row.appendChild(wrap);
  chat.appendChild(row);
  if (pinned) chat.scrollTop = chat.scrollHeight;
  else paintJump();
  return bubble;
}

function showTyping() {
  const row = document.createElement('div');
  row.className = 'row bot';
  row.id = 'typing';
  row.innerHTML =
    '<div class="mav bot">' + MASCOT + '</div>' +
    '<div class="bubble-wrap"><div class="msg bot typing">' +
    '<span></span><span></span><span></span></div></div>';
  chat.appendChild(row);
  if (pinned) chat.scrollTop = chat.scrollHeight;
}
function hideTyping() { document.getElementById('typing')?.remove(); }

let busy = false;
const history = [];      // ↑/↓ recall, like every real messenger
let historyAt = -1;

/* The fox in the send box.
 *
 * She is the app's own mascot - the same cut-out the launcher, the header and
 * the boot card use - put where a companion belongs: inside the composer,
 * with only her head above its lip. The climb, the bob, the glance and the
 * blink are all CSS; this only decides when they start and adds the nod when a
 * message goes out. Nothing here is announced: she is aria-hidden decoration,
 * she takes no pointer events, and she never covers the field she lives in. */
const ChatFox = (() => {
  let timer = 0;
  const el = () => document.getElementById('chatfox');
  /* Reduced motion is read live: the pref can be switched while the page is
     open, and an OS-level switch should not need a reload. */
  const still = () => !!(window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches);

  /* The nod is a class, so it can be replayed on the next message - but it
     has to come off again or it would hold the head still: while it is on it
     replaces the bob. */
  function bindHead(head) {
    if (!head || head.dataset.foxBound) return;
    head.dataset.foxBound = '1';
    head.addEventListener('animationend', (e) => {
      if (e.animationName === 'foxNod') head.classList.remove('nod');
    });
  }

  function mount() {
    const f = el();
    if (!f) return;
    bindHead(f.querySelector('.foxhead'));
    clearTimeout(timer);
    if (still()) { f.classList.add('on'); return; }  // present, never moving
    /* After the boot card, not during it: she should be found, not waiting. */
    timer = setTimeout(() => f.classList.add('on'), 900);
  }

  function nod() {
    const f = el();
    if (!f || still()) return;
    f.classList.add('on');
    const head = f.querySelector('.foxhead');
    if (!head) return;
    bindHead(head);
    head.classList.remove('nod');
    void head.offsetWidth;          // two messages in a row nod twice
    head.classList.add('nod');
  }

  return {mount, nod};
})();

async function send(text) {
  // the opening prompt has done its job once the learner says anything
  const starters = document.getElementById('starters');
  if (starters) starters.remove();
  text = (text || '').trim();
  if (!text) return;
  // Commands run before the `busy` guard: typing a section name while a
  // reply is still loading must still work, not be silently dropped.
  // Every command clears the composer — the typed word was a command, not a
  // message waiting to be sent.
  if (isClearCommand(text)) {
    input.value = '';
    add(text, 'user');
    clearChat();
    return;
  }
  // "analyse this sentence …" / «نقش دستوری کلمات چیه؟» — the bundled tagger
  // answers it on the device. Runs before the section commands, because both
  // match words like "grammar".
  if (await matchAnalyseCommand(text)) { input.value = ''; return; }
  // A request that asked for a sentence without giving one ("check my
  // grammar") gets the next sentence typed, before the sections and the tutor
  // can claim it. This is the context half of the analyser.
  if (await takePendingSentence(text)) { input.value = ''; return; }
  // "listening", "open grammar section", "بخش واژگان" → open the topbar panel
  const section = matchSectionCommand(text);
  if (section) {
    input.value = '';
    openSection(section[0], section[1], text);
    return;
  }
  // "save apple to review" / "open my review list" — also not chat messages.
  // matchReviewCommand does the work itself and returns true when it handled it.
  if (await matchReviewCommand(text)) { input.value = ''; return; }
  // Remember a plain sentence, so "check the sentence I just sent" has a
  // referent at the moment it is asked.
  if (looksLikeSentence(text)) lastTyped = text;
  if (busy) return;                      // real message, but one is in flight
  // daily limit reached — refuse the message, don't queue it
  if (Seed.spent()) { Seed.block(); return; }
  busy = true;
  sendbtn.disabled = true;
  lastUserText = text;
  add(text, 'user');
  ChatFox.nod();
  input.value = '';
  history.push(text);
  historyAt = history.length;
  Seed.add(1);                 // daily seed grows with usage
  showTyping();
  try {
    const r = await fetch('/api/chat?message=' + encodeURIComponent(text));
    const data = await r.json();
    hideTyping();
    add(data.reply, 'bot');
    // finishing a practice unlocks that topic's exam — refresh the panel so
    // the 🎓 button stops showing the lock
    if (/exam is now open|آزمون باز شد/i.test(data.reply) &&
        document.getElementById('gpanel').classList.contains('open')) {
      loadGrammar();
    }
  } catch (e) {
    hideTyping();
    // Nothing was taught, so nothing should have been charged. The seed is
    // added before the request to keep the meter moving while it is in flight;
    // a message that never arrived must not cost one of the fifty.
    Seed.add(-1);

    // The composer was already cleared, so the words are gone from the screen
    // unless we put them back. Someone who typed a full Persian sentence and
    // lost the connection should not have to write it twice.
    input.value = text;
    add('⚠️ No reply came back — is the server running?\n' +
        `Your message is back in the box, and none of your ${SEED_GOAL} ` +
        'daily messages was used.\n' +
        'پاسخی نرسید. پیام شما به کادر برگشت و از سهم امروز کم نشد.',
        'bot', {err: true});
  }
  busy = false;
  sendbtn.disabled = false;
  input.focus();
}

/* The local corrector: the sentence goes to the model, which answers
   from the weights on this machine, and the page only draws the result. It is a
   button rather than a step of send(), so a correction costs nothing from the
   daily seed and never rewords the conversation the bot is having. */
async function checkEnglish(text) {
  text = (text || '').trim();
  if (!text || busy) return;
  const starters = document.getElementById('starters');
  if (starters) starters.remove();
  busy = true;
  add(text, 'user');
  input.value = '';
  showTyping();
  let data = null;
  try {
    // The model is server-side, so the page asks the endpoint and draws the
    // answer. No weights are loaded into the browser any more.
    const r = await fetch('/api/correct?message=' + encodeURIComponent(text));
    data = await r.json();
  } catch (e) {
    data = null;
  }
  hideTyping();
  busy = false;
  if (!data || data.available === false) {
    add('⚠️ ' + ((data && data.refused) || 'The correction model did not answer.') +
        '\n  ↲ مدل اصلاحِ گرامر پاسخ نداد.', 'bot', {err: true});
    return;
  }
  if (data.refused) {
    add('✍️ ' + data.refused, 'bot');
    return;
  }
  if (!data.changed) {
    add('✅ That sentence is already correct English.\n' +
        '  ↲ این جمله از نظر گرامری درست است.', 'bot');
    return;
  }
  add('✍️ Grammar correction / اصلاح گرامر\n' +
      '• You wrote / نوشتی: ' + text + '\n' +
      '• Correct / درست: **' + data.output + '**\n' +
      '  ↲ ' + data.output, 'bot');
}

document.getElementById('gecbtn').addEventListener('click', () => checkEnglish(input.value));

document.getElementById('composer').addEventListener('submit', e => {
  e.preventDefault();
  send(input.value);
});
/* ---------- motion seed: the bird fills up with daily usage ---------- */
const SEED_GOAL = 50;                     // messages allowed per session
/* The day is Iran's day, not UTC's: GMT+3:30, so the session rolls over at
   00:00 Tehran, which is 20:30 UTC. A learner in Tehran at 23:59 local (20:29
   UTC) is still in the session they started that morning, and one minute later
   they get a fresh fifty - whatever the UTC date says. Iran has had no daylight
   saving since 2022, so the offset is a constant rather than a rule set. */
const SEED_TZ_MIN = 210;                  // +03:30
const Seed = {
  state: { day: '', count: 0, streak: 0, best: 0 },
  warned: false,                 // only explain the limit once per session
  /* The session day is the calendar date in Tehran, so the roll is midnight
     there - the same instant msLeft() counts down to. */
  key(d = new Date()) {
    const local = new Date(d.getTime() + SEED_TZ_MIN * 60 * 1000);
    return local.getUTCFullYear() + '-' +
           String(local.getUTCMonth() + 1).padStart(2, '0') + '-' +
           String(local.getUTCDate()).padStart(2, '0');
  },
  /* when the current session ends: the next midnight in Tehran */
  msLeft() {
    const local = new Date(Date.now() + SEED_TZ_MIN * 60 * 1000);
    return Date.UTC(local.getUTCFullYear(), local.getUTCMonth(),
                    local.getUTCDate() + 1, 0, 0, 0, 0) - local.getTime();
  },
  /* Minutes left, and never "0h 00m" while the reset is still ahead: flooring
     to zero for the last minute reads as "this should be open already". */
  msText() {
    const ms = this.msLeft();
    if (ms < 60000) return 'under a minute';
    const mins = Math.floor(ms / 60000);
    const h = Math.floor(mins / 60), m = mins % 60;
    return h ? `${h}h ${String(m).padStart(2, '0')}m` : `${m}m`;
  },
  /* The countdown is a clock, not a snapshot. It used to be written only when
     a message was sent, so a screen read on the next morning still counted the
     hours from when the note first appeared - and, worse, the only thing that
     ever re-read the day was a send, which a locked composer cannot do, so the
     app never unlocked itself at midnight. This is that tick. */
  tick() {
    if (this.rollDay()) { this.paint(); return; }
    this.noteText();
  },
  load() {
    try {
      const raw = localStorage.getItem('fluentify.seed');
      if (raw) this.state = Object.assign(this.state, JSON.parse(raw));
    } catch (e) { /* private mode: keep in memory only */ }
    this.rollDay();
    this.paint();
    // Every half minute, and again the moment a sleeping tab comes back: a
    // phone that was asleep at midnight must not wake up to yesterday's lock.
    clearInterval(Seed.timer);
    Seed.timer = setInterval(() => Seed.tick(), 30000);
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) Seed.tick();
    });
  },
  save() {
    try { localStorage.setItem('fluentify.seed', JSON.stringify(this.state)); } catch (e) {}
  },
  rollDay() {
    const today = this.key();
    if (this.state.day === today) return false;
    if (this.state.day) {
      // yesterday completed the goal → the streak continues
      if (this.state.count >= SEED_GOAL) this.state.streak += 1;
      else this.state.streak = 0;
      this.state.best = Math.max(this.state.best, this.state.streak);
    }
    this.state.day = today;
    this.state.count = 0;
    this.warned = false;
    this.save();
    return true;
  },
  /* Checked on every send, so a tab left open past midnight unlocks itself. */
  spent() {
    if (this.rollDay()) this.paint();
    return this.state.count >= SEED_GOAL;
  },
  left() { return Math.max(0, SEED_GOAL - this.state.count); },
  add(n = 1) {
    const before = this.state.count;
    this.state.count += n;
    if (before < SEED_GOAL && this.state.count >= SEED_GOAL) {
      this.streak = Math.max(this.streak, 0);
      this.celebrate();
    }
    this.save();
    this.paint();
  },
  /* Once the daily limit is reached, sending is refused — here and in the
     offline app this is the whole gate, so it has to be the single check. */
  block() {
    if (this.warned) return;
    this.warned = true;
    add(`🌙 You've used all ${SEED_GOAL} messages for today — the seed is full.\n` +
        `Your next ${SEED_GOAL} messages arrive in ${this.msText()} (00:00 GMT+3:30).`,
        'bot');
    this.paint();
  },
  celebrate() {
    const av = document.querySelector('.avatar');
    if (av) { av.classList.add('bloom'); setTimeout(() => av.classList.remove('bloom'), 1600); }
    add(`🌱 Today's seed is full — ${SEED_GOAL} messages done! You have finished ` +
        `for today; the next session starts in ${this.msText()} (00:00 GMT+3:30).`, 'bot');
  },
  paint() {
    const pct = Math.min(100, Math.round((this.state.count / SEED_GOAL) * 100));
    const full = pct >= 100;
    const av = document.querySelector('.avatar');
    const mark = av && av.querySelector('img');
    if (mark) {
      // the seed ring around the bird grows through the day
      mark.style.setProperty('--seed', pct + '%');
      av.classList.toggle('full', full);
    }
    const meter = document.getElementById('seedmeter');
    if (meter) {
      meter.innerHTML = '';
      const bar = document.createElement('i');
      bar.style.width = pct + '%';
      const t = document.createElement('span');
      t.textContent = full ? '🌸 ' + this.state.streak + 'd' : this.state.count + '/' + SEED_GOAL;
      meter.append(bar, t);
      // the tooltip is written by noteText, with the countdown it reports
    }
    this.lockUI(full);
  },
  /* The sentence under the rail. Split out of lockUI so the half-minute tick
     can refresh the countdown without rebuilding the meter - rewriting that
     would restart the bar's width transition twice a minute. English only:
     this is chrome about the app's own clock, not something being taught. */
  noteText() {
    const note = document.getElementById('limitenote');
    const txt = note && note.querySelector('.limitxt');
    if (!txt) return;
    const used = Math.min(this.state.count, SEED_GOAL);
    const left = SEED_GOAL - used;
    const at = this.msText();
    // Warn over the last fifth, where a learner can still do something about
    // it, and say nothing at all before that. A bar that announces itself on
    // every message is a bar people stop reading.
    // "1 messages left" is the sort of thing that makes a learner stop
    // trusting the rest of the copy.
    txt.innerHTML = used >= SEED_GOAL
      ? `Daily limit reached — <b>${SEED_GOAL}/${SEED_GOAL}</b> messages used. ` +
        `The next ${SEED_GOAL} arrive in <b>${at}</b> (00:00 GMT+3:30).`
      : left <= SEED_GOAL * 0.2
        ? `<b>${left}</b> ${left === 1 ? 'message' : 'messages'} left today — ` +
          `the next ${SEED_GOAL} arrive in <b>${at}</b> (00:00 GMT+3:30).`
        : '';
    // The tooltip carries the same clock, so it is refreshed with it.
    const meter = document.getElementById('seedmeter');
    if (meter) {
      meter.title = `Seed ${Math.round((used / SEED_GOAL) * 100)}% · streak ` +
        `${this.state.streak} session(s) · ${this.state.count}/${SEED_GOAL} ` +
        `messages · resets in ${at} (00:00 GMT+3:30)`;
    }
  },
  /* Grey out the composer so the block is visible, not just enforced */
  lockUI(full) {
    const box = document.getElementById('composer');
    if (!box) return;
    box.classList.toggle('locked', full);
    const note = document.getElementById('limitenote');
    if (note) {
      const used = Math.min(this.state.count, SEED_GOAL);
      // The moon's position is the whole point of the row: one property,
      // and the track does the rest. 0 is the left end, 1 the right.
      note.style.setProperty('--p', (used / SEED_GOAL).toFixed(4));
      note.classList.toggle('warn', used / SEED_GOAL >= 0.8 && !full);
      note.classList.toggle('full', !!full);
      this.noteText();
    }
    if (full) {
      input.disabled = true;
      sendbtn.disabled = true;
      document.querySelectorAll('.ftopic, .vbtn, .gmain, .go').forEach((n) => {
        n.classList.add('locked');
      });
    } else {
      input.disabled = false;
      sendbtn.disabled = false;
      document.querySelectorAll('.ftopic.locked, .vbtn.locked, .gmain.locked, .go.locked')
        .forEach((n) => n.classList.remove('locked'));
    }
  },
};

/* ---------- listening: CEFR A1-C2, spoken aloud ---------- */

/* Speech: on Android use the app's native engine (offline, natural voice);
   everywhere else fall back to the Web Speech API. */
const Speech = {
  playing: null,
  voice: null,
  /* Prefer the most natural-sounding voice the device actually has, instead of
     taking whatever the engine happens to default to (often the worst one). */
  pickVoice() {
    if (!('speechSynthesis' in window)) return null;
    const list = speechSynthesis.getVoices();
    if (!list.length) return null;
    const score = (v) => {
      let s = 0;
      const n = (v.name || '').toLowerCase();
      if (/natural|neural|premium|enhanced/.test(n)) s += 100;
      if (/google/.test(n)) s += 60;
      if (/(samantha|karen|daniel|serena|moira|tessa|zira|aria|jenny|libby|sonia)/.test(n)) s += 45;
      if (v.localService) s += 25;           // offline = instant, no network
      if (/^en[-_]GB/i.test(v.lang)) s += 22;
      else if (/^en[-_]AU|^en[-_]IE/i.test(v.lang)) s += 14;
      else if (/^en[-_]US/i.test(v.lang)) s += 12;
      if (/female|woman|woman/.test(n)) s += 8;
      if (/(compact|eloquence|espeak)/.test(n)) s -= 50;   // robotic engines
      return s;
    };
    const en = list.filter((v) => /^en/i.test(v.lang));
    const pool = en.length ? en : list;
    return pool.slice().sort((a, b) => score(b) - score(a))[0] || null;
  },
  speak(text, onEnd) {
    this.stop();
    // Android: the native engine (high-quality offline voices)
    if (window.AndroidTTS && window.AndroidTTS.speak) {
      window.AndroidTTS.speak(text);
      this.playing = { text };
      setTimeout(() => { this.playing = null; if (onEnd) onEnd(); this.emit(); },
                 Math.max(2200, text.length * 62));
      this.emit();
      return true;
    }
    if (!('speechSynthesis' in window)) return false;
    const u = new SpeechSynthesisUtterance(text);
    if (!this.voice) this.voice = this.pickVoice();
    if (this.voice) u.voice = this.voice;
    u.lang = this.voice ? this.voice.lang : 'en-GB';
    u.rate = 0.95;      // a touch slower than default = clearer
    u.pitch = 1.0;      // neutral, avoids the chipmunk effect
    u.volume = 1;
    u.onend = () => { this.playing = null; if (onEnd) onEnd(); this.emit(); };
    u.onerror = () => { this.playing = null; if (onEnd) onEnd(); this.emit(); };
    this.playing = { text, utter: u };
    speechSynthesis.cancel();
    try {
      speechSynthesis.speak(u);
    } catch (err) {
      /* speak() throws synchronously on a bad utterance, and on some engines
         when it is already mid-sentence. Unhandled, this.playing stayed set
         for ever: the bar never appeared, the page believed it was still
         talking, and the next press of any say-button read as a stop rather
         than a start. */
      this.playing = null;
      this.emit();
      return false;
    }
    this.emit();
    return true;
  },
  stop() {
    if (this.playing && this.playing.utter) speechSynthesis.cancel();
    if (window.AndroidTTS && window.AndroidTTS.stop) window.AndroidTTS.stop();
    this.playing = null;
    this.emit();
  },
  isPlaying(text) { return !!this.playing && this.playing.text === text; },

  /* Player watches this. Most of the page calls Speech.speak directly, so
     without a signal the bar would only ever know about the clips it started
     itself and would sit there blank while a word was being spoken. */
  onchange: null,
  emit() { if (this.onchange) this.onchange(this.playing); },
};
/*__STT_CONFIG__*/


/* ================================================================== PLAYER
 * One bar under the header for everything that makes a sound: the BBC clips
 * and the spoken words. Before this every card carried its own Audio object
 * and its own button, so a six-minute episode could only be halted by finding
 * the card it came from and pressing pause - and pause is not stop, it leaves
 * the position behind and the download half done.
 *
 * One Audio element, reused, is what makes "one thing at a time" true rather
 * than aspirational: two clips playing over each other is the failure mode
 * every per-card player has.
 */
const Player = (() => {
  const ICON_PAUSE =
    '<svg viewBox="0 0 20 20" aria-hidden="true"><rect x="5" y="4" width="3.6" ' +
    'height="12" rx="1.2"/><rect x="11.4" y="4" width="3.6" height="12" rx="1.2"/></svg>';
  const ICON_PLAY =
    '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M6 4.2v11.6a1 1 0 ' +
    '0 0 1.5.87l9.2-5.8a1 1 0 0 0 0-1.74l-9.2-5.8A1 1 0 0 0 6 4.2Z"/></svg>';

  let el, toggle, stopBtn, titleEl, kindEl, track, fill, timeEl;
  let audio = null;            // created once, reused for every clip
  let clip = null;             // {src, title, owner}
  let mode = null;             // null | 'clip' | 'speech'
  let paused = false;
  let seeking = false;

  const mmss = (v) => {
    if (!isFinite(v) || v < 0) v = 0;
    return Math.floor(v / 60) + ':' + String(Math.floor(v % 60)).padStart(2, '0');
  };

  function mount() {
    el = document.getElementById('player');
    if (!el) return false;
    toggle = document.getElementById('pltoggle');
    stopBtn = document.getElementById('plstop');
    titleEl = document.getElementById('pltitle');
    kindEl = document.getElementById('plkind');
    track = document.getElementById('plseek');
    timeEl = document.getElementById('pltime');
    if (!toggle || !stopBtn || !track || !titleEl || !kindEl || !timeEl) return false;
    if (!fill) { fill = document.createElement('i'); track.appendChild(fill); }
    toggle.onclick = () => togglePlay();
    stopBtn.onclick = () => stopAll();
    wireSeek();
    return true;
  }

  /* ---- seeking -------------------------------------------------------- */
  const fracAt = (ev) => {
    const r = track.getBoundingClientRect();
    if (!r.width) return 0;
    return Math.min(1, Math.max(0, (ev.clientX - r.left) / r.width));
  };
  function applySeek(f) {
    if (!audio || mode !== 'clip' || paused) return;
    const d = audio.duration;
    if (isFinite(d) && d > 0) { audio.currentTime = f * d; paint(); }
  }
  function wireSeek() {
    track.addEventListener('pointerdown', (ev) => {
      if (mode !== 'clip' || paused) return;
      seeking = true;
      try { track.setPointerCapture(ev.pointerId); } catch (e) { /* not fatal */ }
      applySeek(fracAt(ev));
    });
    track.addEventListener('pointermove', (ev) => {
      if (seeking) applySeek(fracAt(ev));
    });
    const done = (ev) => {
      if (!seeking) return;
      seeking = false;
      try { track.releasePointerCapture(ev.pointerId); } catch (e) { /* already gone */ }
    };
    track.addEventListener('pointerup', done);
    track.addEventListener('pointercancel', done);
    track.addEventListener('keydown', (ev) => {
      if (mode !== 'clip' || paused) return;
      const d = audio && isFinite(audio.duration) ? audio.duration : 0;
      if (!d) return;
      const step = ev.shiftKey ? 0.1 : 0.02;
      let f = (audio.currentTime || 0) / d;
      if (ev.key === 'ArrowRight') f += step;
      else if (ev.key === 'ArrowLeft') f -= step;
      else if (ev.key === 'Home') f = 0;
      else if (ev.key === 'End') f = 1;
      else if (ev.key === ' ' || ev.key === 'Enter') {
        togglePlay(); ev.preventDefault(); return;
      } else return;
      ev.preventDefault();
      applySeek(Math.min(1, Math.max(0, f)));
    });
  }

  /* ---- painting -------------------------------------------------------- */
  function paint() {
    if (!el || !fill) return;
    if (mode === 'speech') {
      el.classList.add('speech');
      kindEl.textContent = 'Speaking';
      toggle.innerHTML = paused ? ICON_PLAY : ICON_PAUSE;
      toggle.setAttribute('aria-label', paused ? 'Resume speaking' : 'Stop speaking');
      toggle.title = paused ? 'Resume' : 'Stop';
      timeEl.textContent = paused ? 'paused' : '…';
      track.setAttribute('aria-valuenow', '0');
      track.setAttribute('aria-valuetext',
                         titleEl.textContent
                           ? 'Speaking: ' + titleEl.textContent : 'Speaking');
      fill.style.width = '100%';
      return;
    }
    el.classList.remove('speech');
    const dur = audio && isFinite(audio.duration) ? audio.duration : 0;
    const cur = audio ? (audio.currentTime || 0) : 0;
    const pct = dur > 0 ? (cur / dur) * 100 : 0;
    fill.style.width = pct.toFixed(2) + '%';
    toggle.innerHTML = paused ? ICON_PLAY : ICON_PAUSE;
    toggle.setAttribute('aria-label', paused ? 'Resume' : 'Pause');
    toggle.title = paused ? 'Resume' : 'Pause';
    timeEl.textContent = dur > 0 ? mmss(cur) + ' / ' + mmss(dur) : mmss(cur);
    track.setAttribute('aria-valuenow', String(Math.round(pct)));
    track.setAttribute('aria-valuetext',
                       dur > 0 ? mmss(cur) + ' of ' + mmss(dur) : 'Not started');
  }

  /* ---- speech, wherever it was started from ----------------------------
     Most of the page calls Speech.speak directly, so Player watches Speech
     rather than asking to be called. Without that the bar would only ever
     know about clips it started itself and would sit blank while a word was
     being spoken.
  */
  function sync() {
    if (!el) return;
    const sp = Speech.playing;
    if (sp) {
      if (mode !== 'clip') mode = 'speech';
      if (mode === 'speech') {
        if (titleEl.textContent !== sp.text) titleEl.textContent = sp.text;
        el.hidden = false;
        paused = false;
        paint();
      }
      return;
    }
    if (mode === 'speech') {
      // finished on its own, or Speech.stop() was called
      if (audio && clip && !audio.paused) return;   // a clip took over
      mode = null;
      paused = false;
      titleEl.textContent = '';
      el.hidden = true;
      paint();
      return;
    }
    paint();
  }

  /* ---- clips ----------------------------------------------------------- */
  function ensureAudio() {
    if (audio) return audio;
    audio = new Audio();
    audio.preload = 'none';
    audio.crossOrigin = 'anonymous';
    audio.addEventListener('timeupdate', paint);
    audio.addEventListener('loadedmetadata', paint);
    // Both directions. Only notifying on play left the card reading
    // "Pause" while the bar read "Resume" - two controls, one truth, and
    // they disagreed about it.
    audio.addEventListener('play', () => {
      paused = false;
      if (clip && clip.owner) clip.owner(true);
      paint();
    });
    audio.addEventListener('pause', () => {
      paused = true;
      if (clip && clip.owner) clip.owner(false);
      paint();
    });
    audio.addEventListener('ended', () => {
      paused = false;
      if (clip && clip.owner) clip.owner(false);
      clip = null;
      audio.removeAttribute('src');
      mode = null;
      el.hidden = true;
      paint();
    });
    audio.addEventListener('error', () => {
      if (!clip) return;
      const code = audio.error ? audio.error.code : 0;
      if (clip.owner) clip.owner(false);
      clip = null;
      mode = null;
      el.hidden = true;
      paint();
      // "Needs a network connection" was the one diagnosis that could not be
      // right - it was reported when the device was online and the stream was
      // simply refused. MediaError distinguishes a network failure (2) from a
      // decode or format problem (3) and from a blocked source (4), which is
      // what cleartext HTTP on Android produced.
      toast(code === 4 || !navigator.onLine
        ? '🔇 That clip is blocked on this device — open it on the web ' +
          'version. / این کلیپ روی این دستگاه مسدود است.'
        : code === 3
          ? '🔇 This clip could not be decoded — این کلیپ پخش نشد.'
          : '🔇 Could not reach the audio, check your connection — ' +
            'اتصال را بررسی کن.', 4200);
    });
    return audio;
  }

  /* owner(on) is how the originating card's button keeps its label honest,
     so the card and the bar can never disagree about what is playing. */
  function playClip(src, title, owner) {
    if (window.AndroidTTS && window.AndroidTTS.stop) window.AndroidTTS.stop();
    Speech.stop();
    if (clip && clip.src !== src && clip.owner) clip.owner(false);
    const resuming = !!(clip && clip.src === src && audio && !audio.paused);
    clip = { src, title, owner: owner || null };
    mode = 'clip';
    paused = false;
    titleEl.textContent = title || '';
    kindEl.textContent = 'Listening';
    el.hidden = false;
    paint();
    const a = ensureAudio();
    if (!resuming) a.src = src;
    a.play().then(() => { if (clip && clip.owner) clip.owner(true); paint(); })
     .catch(() => { /* the error handler above says why */ paint(); });
  }

  function togglePlay() {
    if (mode === 'speech') {
      // Android's TextToSpeech has no pause, so stopping is the honest answer
      // there; resume speaks it again rather than pretending to continue.
      if (paused) { const t = titleEl.textContent; paused = false; Speech.speak(t); return; }
      Speech.stop();
      return;
    }
    if (!audio || !clip) return;
    if (audio.paused) { paused = false; audio.play().catch(() => { /* handled above */ }); }
    else audio.pause();
    paint();
  }

  function stopAll() {
    if (mode === 'speech') { Speech.stop(); return; }
    if (audio) {
      try { audio.pause(); } catch (e) { /* nothing playing */ }
      try { audio.currentTime = 0; } catch (e) { /* no metadata yet */ }
      audio.removeAttribute('src');
    }
    if (clip && clip.owner) clip.owner(false);
    clip = null;
    mode = null;
    paused = false;
    if (el) { el.hidden = true; paint(); }
  }

  Speech.onchange = sync;
  return {
    mount,
    clip: playClip,
    stop: stopAll,
    toggle: togglePlay,
    get playing() { return mode !== null; },
    get paused() { return paused; },
    get mode() { return mode; },
    get currentSrc() { return clip ? clip.src : null; },
  };
})();

/* ================================================================= STICKERS
 * The picker offers the fox stickers, and their artwork lives in foxes.json -
 * same rule as every other piece of content here: adding a sticker is an edit
 * to a data file, never to this page.
 *
 * A sticker is a picture, not a character, so it travels through a message as
 * [fox:cute] and is painted back into the bubble afterwards by stickerize().
 * The composer shows the token while it is being written; the bubble shows the
 * fox.
 *
 * Search matches the sticker's id, its English name, its Persian name and its
 * keywords, so "happy", "sleep" and «خوشحال» all find something. That matters
 * more here than in a phone keyboard: the people using this are learners, and
 * looking for a word they already know is faster than hunting a grid.
 */
const Stickers = (() => {
  let data = null;
  let open = false;
  let lastFocus = null;
  let els = {};

  const norm = (s) => String(s || '').toLowerCase().trim();

  /* A sticker carries no text of its own, so each one gets its name as an
     accessible label. A grid of unlabelled pictures is a wall of nothing to a
     screen reader. */
  function tile(s) {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'stile';
    b.innerHTML = foxSvg(s.id, 'stileart');
    b.dataset.fox = s.id;
    const label = s.name + ' — ' + s.fa;
    b.title = label;
    b.setAttribute('aria-label', label);
    return b;
  }

  function matches(s, q) {
    if (!q) return true;
    const hay = norm(s.id + ' ' + s.name + ' ' + s.fa + ' ' + (s.kw || ''));
    return q.split(/\s+/).every((word) => hay.includes(word));
  }

  function renderGrid(host, list) {
    const frag = document.createDocumentFragment();
    list.forEach((s) => frag.appendChild(tile(s)));
    host.appendChild(frag);
  }

  function build() {
    els.panel = document.getElementById('stickerpanel');
    els.btn = document.getElementById('stickerbtn');
    els.input = document.getElementById('input');
    if (!els.panel || !els.btn) return false;

    els.search = document.createElement('input');
    els.search.type = 'search';
    els.search.className = 'esearch';
    els.search.placeholder = 'Search stickers… / جست‌وجوی استیکر…';
    els.search.setAttribute('aria-label', 'Search stickers / جست‌وجوی استیکر');
    els.panel.appendChild(els.search);

    els.body = document.createElement('div');
    els.body.className = 'ebody';
    els.panel.appendChild(els.body);

    els.search.addEventListener('input', () => paint());
    els.search.addEventListener('keydown', (ev) => {
      if (ev.key === 'Escape') { ev.stopPropagation(); close(); }
    });

    els.btn.addEventListener('click', () => (open ? close() : show()));

    /* Delegated: the grid is rebuilt on every keystroke, so a listener on each
       tile would go with the tile and leak a closure per emoji. */
    els.panel.addEventListener('click', (ev) => {
      const t = ev.target.closest('.stile');
      if (!t) return;
      insert('[fox:' + t.dataset.fox + ']');
    });

    // A click anywhere else closes it. Capture, so it still works when the
    // click lands on something that stops propagation.
    document.addEventListener('pointerdown', (ev) => {
      if (!open) return;
      if (els.panel.contains(ev.target) || els.btn.contains(ev.target)) return;
      close();
    }, true);

    document.addEventListener('keydown', (ev) => {
      if (!open) return;
      if (ev.key === 'Escape') { ev.preventDefault(); close(); }
    });

    load();
    return true;
  }

  /* Insert at the caret, not at the end. Someone writing "good mo" then
     picking an emoji should not have their emoji land after the sentence. */
  function insert(ch) {
    const box = els.input;
    if (!box) return;
    const at = typeof box.selectionStart === 'number' ? box.selectionStart : box.value.length;
    const before = box.value.slice(0, at);
    const after = box.value.slice(typeof box.selectionEnd === 'number' ? box.selectionEnd : at);
    box.value = before + ch + after;
    const caret = at + ch.length;
    box.setSelectionRange(caret, caret);
    box.dispatchEvent(new Event('input'));
    box.focus();
  }

  /* One grid. The set is twelve pictures, not three hundred glyphs, so the
     categories and the recents row the emoji palette needed would be two
     headings and a strip of duplicates above a single row of foxes. */
  function paint() {
    const q = norm(els.search.value);
    els.body.textContent = '';
    const hits = data.stickers.filter((s) => matches(s, q));

    /* No heading: the panel holds one set and its button already says what it
       is, so a name above the grid only repeats it. While a search is live the
       count is the one thing the grid cannot show by itself. */
    if (q && hits.length) {
      const head = document.createElement('div');
      head.className = 'ehead';
      head.textContent = hits.length + (hits.length === 1 ? ' match' : ' matches');
      els.body.appendChild(head);
    }

    if (!hits.length) {
      const none = document.createElement('div');
      none.className = 'eempty';
      none.textContent = 'No sticker matches “' + els.search.value.trim() + '”';
      els.body.appendChild(none);
      return;
    }
    renderGrid(els.body, hits);
  }

  function show() {
    if (!data) return;
    open = true;
    lastFocus = document.activeElement;
    els.panel.hidden = false;
    els.btn.setAttribute('aria-expanded', 'true');
    els.search.value = '';
    paint();
    els.search.focus();
  }

  function close() {
    if (!open) return;
    open = false;
    els.panel.hidden = true;
    els.btn.setAttribute('aria-expanded', 'false');
    // Focus goes back to the field, not to the button: the user's next move
    // is to carry on typing.
    if (els.input) els.input.focus();
    else if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  async function load() {
    if (data) return true;
    try {
      data = await loadJSON('foxes');
    } catch (e) {
      // No picker is a smaller problem than a composer that cannot send.
      if (els.btn) els.btn.hidden = true;
      data = null;
      return false;
    }
    /* The same catalogue feeds the bubbles, so a sticker already in the
       transcript still paints when the picker is never opened. */
    registerFoxes(data.stickers);
    return true;
  }

  return { mount: build, open: show, close, load,
           get open() { return open; }, get catalogue() { return data; } };
})();
/* ==================================================================== MOTION
 * One IIFE, no top-level names, so it cannot collide with bot.js - which is
 * the failure that blanked the offline app once already.
 */
const Motion = (() => {
  const calm = window.matchMedia('(prefers-reduced-motion: reduce)');
  const fine = window.matchMedia('(pointer: fine)');

  /* ------------------------------------------------------------------ motes
   * A thin scatter of points drifting behind the glass. The count scales
   * with the viewport so a phone is not asked to run a desktop's worth, the
   * loop stops when the tab is hidden, and it never starts at all if the
   * user asked for reduced motion.
   */
  let motes = null;
  function startMotes() {
    if (calm.matches || motes) return;
    const layer = document.getElementById('motes');
    if (!layer) return;
    const canvas = document.createElement('canvas');
    layer.appendChild(canvas);
    const ctx = canvas.getContext('2d', {alpha: true});
    let w = 0, h = 0, dots = [], raf = 0, running = false;

    const resize = () => {
      // 1x, not 2x. Everything this canvas draws is a soft blob of 1-3px with
      // no edge to resolve, so the second set of pixels is invisible and costs
      // four times the fill. On a 3x phone that is the difference between
      // clearing 1.3 megapixels a frame and clearing 320 thousand, for no
      // visible change.
      const dpr = Math.min(1.25, window.devicePixelRatio || 1);
      w = layer.clientWidth; h = layer.clientHeight;
      canvas.width = Math.max(1, Math.round(w * dpr));
      canvas.height = Math.max(1, Math.round(h * dpr));
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const want = Math.round(Math.min(48, Math.max(14, (w * h) / 26000)));
      dots = Array.from({length: want}, () => spawn(true));
    };

    const COLORS = ['167,139,250', '109,140,255', '255,141,196', '52,211,153'];
    function spawn(anywhere) {
      const depth = 0.35 + Math.random() * 0.65;   // parallax: near ones brighter
      return {
        x: Math.random() * w,
        y: anywhere ? Math.random() * h : h + 12,
        r: 0.6 + depth * 1.9,
        vx: (Math.random() - 0.5) * 0.13 * depth,
        vy: -(0.05 + Math.random() * 0.16) * depth,
        a: 0.05 + depth * 0.16,
        tw: Math.random() * Math.PI * 2,
        tws: 0.008 + Math.random() * 0.016,
        c: COLORS[(Math.random() * COLORS.length) | 0],
      };
    }

    let t = 0;
    function frame() {
      if (!running) return;
      t += 1;
      ctx.clearRect(0, 0, w, h);
      for (const d of dots) {
        d.x += d.vx; d.y += d.vy; d.tw += d.tws;
        if (d.y < -14 || d.x < -20 || d.x > w + 20) Object.assign(d, spawn(false));
        // twinkle, gently: a sine rather than a random blink
        const alpha = d.a * (0.62 + 0.38 * Math.sin(d.tw));
        ctx.beginPath();
        ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${d.c},${alpha.toFixed(3)})`;
        ctx.fill();
      }
      raf = requestAnimationFrame(frame);
    }

    const start = () => { if (running || calm.matches) return; running = true; frame(); };
    const stop = () => { running = false; cancelAnimationFrame(raf); };

    resize();
    let rt = 0;
    window.addEventListener('resize', () => {
      clearTimeout(rt);
      rt = setTimeout(resize, 180);
    });
    document.addEventListener('visibilitychange', () =>
      document.hidden ? stop() : start());
    calm.addEventListener?.('change', () => (calm.matches ? stop() : start()));
    start();
    motes = {stop};
  }

  /* ----------------------------------------------------------------- ripple
   * One delegated listener for the entire app. A ring is positioned from the
   * pointer event, sized to cover the element, and cleaned up on animationend
   * so a long session does not accumulate dead nodes.
   */
  function startRipple() {
    if (calm.matches) return;
    const SEL = 'button, .ltab, .bbc-tab, .lrow, .tile, .cchip';
    document.addEventListener('pointerdown', (ev) => {
      const host = ev.target.closest?.(SEL);
      if (!host || !host.getBoundingClientRect) return;
      const r = host.getBoundingClientRect();
      const size = Math.max(r.width, r.height);
      const ink = document.createElement('span');
      ink.className = 'ripple';
      ink.style.width = ink.style.height = size + 'px';
      ink.style.left = (ev.clientX - r.left - size / 2) + 'px';
      ink.style.top = (ev.clientY - r.top - size / 2) + 'px';
      host.appendChild(ink);
      ink.addEventListener('animationend', () => ink.remove(), {once: true});
      // a tap on a non-pointer device has no coordinates worth using
      if (ev.pointerType === 'touch') {
        ink.style.left = (r.width - size) / 2 + 'px';
        ink.style.top = (r.height - size) / 2 + 'px';
      }
    }, {passive: true});
  }

  /* ------------------------------------------------------- speaking state
   * The bird breathes idly and pulses while a message is being read. The
   * page marks an active player with .on - the Listening section's play
   * button - so this only has to watch for that rather than know anything
   * about audio. The per-answer speaker no longer exists, so .mtool.on has
   * nothing to observe: one observer on the document covers the transcript
   * and the panels alike.
   */
  function watchSpeaking() {
    const set = () => {
      document.body.classList.toggle('speaking',
        !!document.querySelector('.bbc-play.on'));
    };
    new MutationObserver(set).observe(document.body,
      {subtree: true, attributes: true, attributeFilter: ['class']});
    set();
  }

  /* ------------------------------------------------------------------ init
   * Idempotent, because the page calls it once on boot and the panel loaders
   * do not need to know about any of this.
   */
  function init() {
    startMotes();
    startRipple();
    watchSpeaking();
  }

  return {init, calm, fine};
})();

/* ============================================================================
 * PANEL SHELL
 * Close button, Esc, focus in on open and back to the tile on close, and
 * aria-expanded - for all six panels, which had otherwise drifted into six
 * behaviours. togglePanel routes through here so they cannot diverge again.
 * ==========================================================================*/
const Panels = (() => {
  const TILES = {
    dpanel: 'dtoggle', npanel: 'ntoggle', vpanel: 'vtoggle', gpanel: 'gtoggle',
    fpanel: 'ftoggle', lpanel: 'ltoggle', phpanel: 'phtoggle',
    bpanel: 'btoggle', rpanel: 'rtoggle', rdpanel: 'rdtoggle',
    stpanel: 'stoggle',
    lvlpanel: 'lvltoggle',
    // the weekly quiz has no tile: the landing-page card is its way in
    wqpanel: null,
    // practice has no tile either: the transcript card is its way in, and the
    // account panel routes into one of its tabs
    prpanel: null,
    acpanel: 'actoggle',
    // the learning path has a tile, but it stays hidden until the level check
    // has produced a placement
    pathpanel: 'pathtoggle',
  };
  let openId = null;
  /* Panels that lead somewhere when they close, rather than back to the
     transcript: the practice page returns to the list it was chosen from. */
  const ON_CLOSE = {};

  const CLOSE_ICON =
    '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" ' +
    'stroke-width="2" stroke-linecap="round" aria-hidden="true">' +
    '<path d="M3 3l10 10M13 3L3 13"/></svg>';

  /* Build the header once. Existing bare <h3> elements are adopted in place
     so the panels keep their own wording without being rewritten. */
  function ensureShell(panelId) {
    const panel = document.getElementById(panelId);
    if (!panel || panel.querySelector('.phead')) return;
    const h3 = panel.querySelector('h3');
    if (!h3) return;

    const head = document.createElement('div');
    head.className = 'phead';
    panel.insertBefore(head, h3);
    head.appendChild(h3);

    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'pclose';
    close.innerHTML = CLOSE_ICON;
    close.title = 'Close — بستن';
    close.setAttribute('aria-label', 'Close this section');
    close.addEventListener('click', () => toggle(panelId));
    head.appendChild(close);

    const tile = document.getElementById(TILES[panelId]);
    if (tile) tile.setAttribute('aria-controls', panelId);
  }

  /* A search box for any panel that can usefully be filtered. `count` reports
     how many items are currently visible so the label can be honest. */
  function addSearch(panelId, placeholder, onInput) {
    const panel = document.getElementById(panelId);
    if (!panel || panel.querySelector('.psearch')) return;
    const box = document.createElement('div');
    box.className = 'psearch';
    const input = document.createElement('input');
    input.type = 'search';
    input.placeholder = placeholder;
    input.autocomplete = 'off';
    input.setAttribute('aria-label', placeholder);
    input.addEventListener('input', () => onInput(input.value));
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') { input.value = ''; onInput(''); }
    });
    box.appendChild(input);
    const head = panel.querySelector('.phead');
    if (head) head.after(box);
    else panel.prepend(box);
    panel._search = input;
  }

  function focusables(panel) {
    return [...panel.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )].filter((el) => el.offsetParent !== null || el === document.activeElement);
  }

  /* The one place panel visibility changes. togglePanel() routes through here
     so the class, the tile state, aria-expanded and focus cannot disagree. */
  function set(panelId, wantOpen, hook) {
    ensureShell(panelId);
    const panel = document.getElementById(panelId);
    if (!panel) return;
    const tile = document.getElementById(TILES[panelId]);

    if (!wantOpen) {
      panel.classList.remove('open');
      tile?.classList.remove('on');
      tile?.setAttribute('aria-expanded', 'false');
      if (openId === panelId) openId = null;
      paintShell();
      // Only pull focus back if it is still inside the panel being closed -
      // otherwise Escape from the composer would steal it. The destination is
      // the panel's own tile rather than whatever was focused on open, because
      // a mouse click does not reliably focus the button it lands on and the
      // remembered element would sometimes be <body>.
      if (panel.contains(document.activeElement)) {
        document.getElementById(TILES[panelId])?.focus();
      }
      // ...and then whatever this panel returns to, if it is not the column
      if (ON_CLOSE[panelId]) ON_CLOSE[panelId]();
      return;
    }

    // one panel at a time, the way it has always worked
    if (openId && openId !== panelId) set(openId, false);

    panel.classList.add('open');
    tile?.classList.add('on');
    tile?.setAttribute('aria-expanded', 'true');
    openId = panelId;
    paintShell();

    // A panel whose content is generated rather than static has to be told to
    // redraw when it opens. Without this the Review panel opened blank.
    if (hook) hook();

    // focus the close button, not the first field: opening a panel should not
    // drop a keyboard user into a search box they did not ask for
    (panel.querySelector('.pclose') || panel).focus?.();
  }

  /* One flag on the shell, not a class per panel: whether a section owns the
     column is a fact about the app, and the transcript and composer hide from
     it rather than from a list of fifteen panel ids that must stay in step. */
  function paintShell() {
    const app = document.querySelector('.app');
    if (app) app.classList.toggle('section', !!openId);
  }

  function toggle(panelId, hook) {
    const panel = document.getElementById(panelId);
    if (!panel) return;
    set(panelId, !panel.classList.contains('open'), hook);
  }

  /* Escape closes the topmost thing: an open panel, else the audio. */
  function init() {
    Object.keys(TILES).forEach(ensureShell);

    document.addEventListener('keydown', (e) => {
      if (e.key !== 'Escape') return;
      if (openId) { e.preventDefault(); set(openId, false); }
      else if (typeof Speech !== 'undefined' && Speech.playing) Speech.stop();
    }, true);

    // keep Tab inside an open panel
    document.addEventListener('keydown', (e) => {
      if (e.key !== 'Tab' || !openId) return;
      const panel = document.getElementById(openId);
      const items = focusables(panel);
      if (!items.length) return;
      const first = items[0], last = items[items.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault(); last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault(); first.focus();
      }
    });
  }

  function onClose(panelId, fn) {
    if (fn) ON_CLOSE[panelId] = fn;
    else delete ON_CLOSE[panelId];
  }

  return {init, set, toggle, ensureShell, addSearch, onClose,
          isOpen: () => openId,
          closeAll: () => { if (openId) set(openId, false); }};
})();

/* ============================================================================
 * PANEL SEARCH
 * Only Vocabulary had a search box; 48 grammar lessons and 39 sentence banks
 * could only be found by scrolling. Generic on purpose - hide what does not
 * match, report what is left, say so when nothing does.
 * ==========================================================================*/
const PanelSearch = (() => {
  const attached = new Map();

  function emptyFor(panelId) {
    const panel = document.getElementById(panelId);
    let box = panel.querySelector('.pempty[data-search]');
    if (!box) {
      box = document.createElement('div');
      box.className = 'pempty';
      box.dataset.search = '1';
      box.hidden = true;
      panel.appendChild(box);
    }
    return box;
  }

  function apply(panelId, needle) {
    const panel = document.getElementById(panelId);
    const state = attached.get(panelId);
    if (!panel || !state) return;
    const q = needle.trim().toLowerCase();

    let shown = 0;
    for (const el of state.items) {
      // re-read the text each time: the cards re-render on their own
      const hit = !q || el.textContent.toLowerCase().includes(q);
      el.hidden = !hit;
      if (hit) shown++;
    }
    pruneEmptyGroups(state.selector.split(',').map((s) => s.trim()),
                     state.group || []);

    if (state.tabs) state.tabs(q, shown);
    if (state.after) state.after(shown, q);

    const box = emptyFor(panelId);

    if (q && shown === 0) {
      box.innerHTML = 'Nothing matches <b>' + (needle.length > 28
        ? needle.slice(0, 28) + '…' : needle) + '</b>.<br>' +
        'چیزی پیدا نشد — املای دیگری را امتحان کن.';
      box.hidden = false;
    } else {
      box.hidden = true;
    }

    const node = document.getElementById(panelId + 'count');
    if (node) {
      // Count in English, then the Persian label as its own island: appending
      // «نمایش همه» to an English count made one left-to-right run out of both
      // scripts, so the Persian sat in the middle of the line reading left to
      // right.
      node.innerHTML = q
        ? `${shown} of ${state.items.length} · <bdi class="fa" lang="fa" dir="rtl">${escapeHtml(needle)}</bdi>`
        : `${state.items.length} · <bdi class="fa" lang="fa" dir="rtl">نمایش همه</bdi>`;
    }
  }

  /* A group is the heading a set of items sits under - A2 under Vocabulary,
     a band under Sounds. Hiding every item in it without hiding the heading
     itself leaves the panel looking broken, so empty groups go too. */
  function pruneEmptyGroups(items, groups) {
    for (const g of groups) {
      const kids = [...g.querySelectorAll(items.join(','))];
      g.hidden = kids.length > 0 && kids.every((k) => k.hidden);
    }
  }

  /* items:   what the panel repeats and what a search matches against
     group:   the heading that wraps them, hidden when they all filter out
     shadow:  items re-render, so the handler is on the panel, not the item  */
  function attach(panelId, selector, placeholder, opts = {}) {
    const panel = document.getElementById(panelId);
    if (!panel) return;
    const items = [...panel.querySelectorAll(selector)];
    if (!items.length) return;      // content not loaded yet; boot calls again

    // Re-attach is a refresh, not a skip. loadListening empties its list and
    // rebuilds it on every level change, so holding the original nodes would
    // leave the search filtering elements that are no longer in the document.
    const known = attached.get(panelId);
    if (known && known.selector === selector) {
      known.items = items;
      known.group = opts.group ? [...panel.querySelectorAll(opts.group)] : [];
    } else {
      attached.set(panelId, {
        items,
        group: opts.group ? [...panel.querySelectorAll(opts.group)] : [],
        selector,
        tabs: opts.tabs,
        after: opts.after,
      });
    }

    Panels.addSearch(panelId, placeholder, (v) => apply(panelId, v));

    let status = document.getElementById(panelId + 'count');
    if (!status) {
      status = document.createElement('div');
      status.className = 'pcount';
      status.id = panelId + 'count';
    }
    // under the search box, not at the top of the panel: prepending put the
    // count above the panel's own title, which read as a heading
    const searchBox = panel.querySelector('.psearch');
    if (searchBox) searchBox.after(status);
    else panel.prepend(status);

    const live = document.getElementById(panelId + 'count');
    const q = panel._search ? panel._search.value : '';
    live.innerHTML = q
      ? `… · <bdi class="fa" lang="fa" dir="rtl">${escapeHtml(q)}</bdi>`
      : `${items.length} · <bdi class="fa" lang="fa" dir="rtl">نمایش همه</bdi>`;
    // keep whatever is already typed rather than dropping it on a refresh
    if (q) apply(panelId, q);
  }

  function attachAll() {
    // selectors are the classes the loaders actually emit, not the ones they
    // look like they should
    // Vocabulary is deliberately absent. It shipped with a search box of its
    // own that filters the 56 domain names; attaching a second one here would
    // put two identical-looking inputs in one panel.
    attach('gpanel', '.gbtn',
      'Search 48 lessons… / جست‌وجوی درس‌ها…', {group: '.glevel'});
    attach('fpanel', '.ftopic',
      'Search the sentence banks… / جست‌وجوی موضوع‌ها…');
    // Sounds shows one topic at a time in .phview, so .pgroup is empty until
    // something is clicked and searching it would match nothing. The topic
    // rail is the panel's index and is always there, so that is what is
    // searched - it filters what you can reach, not just what is on screen.
    attach('phpanel', '.phtab',
      'Search the topics… / جست‌وجوی موضوع صداها…');
    attach('phpanel', '.phtab',
      'Search the topics… / جست‌وجوی موضوع صداها…',
      {after: (shown) => {
        // if the topic on screen was filtered out, move to the first that was
        // not, so the panel is never showing an invisible selection
        const rail = document.querySelector('#phpanel .prail');
        const cur = rail?.querySelector('.phtab.on, .phtab[aria-selected="true"]');
        if (cur && cur.hidden) {
          const next = [...rail.querySelectorAll('.phtab')].find((t) => !t.hidden);
          next?.click();
        }
      }});
    attach('lpanel', '.lrow',
      'Search the sentences… / جست‌وجوی جمله‌ها…',
      {tabs: (q) => { document.querySelectorAll('#lpanel .ltab').forEach((t) => {
        t.hidden = !!q && !t.textContent.toLowerCase().includes(q);
      }); }});
  }

  return {attachAll, apply};
})();

/* ------------------------------------------------------------------ STT ---
 * Speech to text, configured entirely by stt.json so the web app, the CLI and
 * the Android app cannot drift apart. Two engines, chosen at runtime:
 *
 *   Android    window.AndroidSTT  — the on-device RecognizerIntent that ships
 *                                 with Android. No model to download, no key.
 *   Web        window.SpeechRecognition / webkitSpeechRecognition — the
 *                                 browser's own. Chrome, Edge and Safari have
 *                                 it; Firefox does not, and the UI says so
 *                                 instead of failing silently.
 *
 * None of this uploads anything from this project: recognition is done by the
 * browser or the OS, and the transcript lands in the composer like typed text.
 */
const STT = {
  cfg: window.STT_CONFIG || {},
  rec: null,
  listening: false,
  interim: '',
  final: '',
  startedAt: 0,
  language: null,

  /* Which engine is actually usable here, or null. */
  /* A dictation that ends in a text field is one use of this; a sentence the
     learner was asked to say aloud is another, and it must not land in the
     composer. `sink` is that second destination: set, it receives the words and
     the field is left alone. */
  sink: null,

  engine() {
    if (window.AndroidSTT && window.AndroidSTT.available) return 'android';
    const R = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (R) return 'web';
    return null;
  },
  supported() { return this.engine() !== null; },

  lang() {
    if (this.language) return this.language;
    const l = this.cfg.language || {};
    return l.default || l.fallback || 'en-GB';
  },

  setLanguage(code) { this.language = code; },

  /* What this utterance has already put in the composer, so a late final
     result cannot repeat it. Reset per utterance, not per page. */
  _written: '',


  begin() {
    if (this.listening) return true;
    const engine = this.engine();
    if (!engine) return false;

    if (engine === 'android') {
      this.listening = true;
      this.interim = '';
      this._written = '';
      this.render();
      window.AndroidSTT.start(this.lang(), (partial) => {
        this.interim = partial || '';
        if (this.cfg.show_interim !== false) this.render();
      }, (final) => {
        this.listening = false;
        this.interim = '';
        this.final = final || '';
        this.render();
        /* Always commit, and commit here rather than in the button's stop().
           Two things made dictation record but never write, on a phone:
           stopListening() is asynchronous, so pressing the button committed
           an empty final and threw away what was said a moment later; and
           this was gated on submit_on_final, which is about sending a
           message, not about filling the composer. Gating the two together
           is why every word went missing. */
        this.commit();
      }, (err) => {
        this.listening = false;
        this.interim = '';
        this.final = '';
        this._written = '';
        this.render();
        if (err) this.onError(err);
      });
      return true;
    }

    const R = window.SpeechRecognition || window.webkitSpeechRecognition;
    const rec = new R();
    this.cfg.web = this.cfg.web || {};
    rec.lang = this.lang();
    rec.continuous = !!this.cfg.web.continuous;
    rec.interimResults = this.cfg.web.interim_results !== false;
    rec.maxAlternatives = this.cfg.web.max_alternatives || 1;

    // On-device recognition is deliberately NOT touched.
    //
    // It is supposed to stop the Web Speech API streaming audio to a Google
    // service, which is worth having. But on Android WebView the on-device
    // speech interfaces are exposed with no binder behind them, and merely
    // asking about them is fatal: Chromium logs
    //
    //   Terminating render process for bad Mojo message: No binder found
    //   for interface media.mojom.OnDeviceSpeechRecognition
    //
    // and kills the renderer. Observed on the device as a crash loop, because
    // the renderer-death handler reloads the page, the page asks again, and
    // the renderer dies again - a black screen that never settles.
    //
    // So neither SpeechRecognition.available() nor processLocally is touched
    // here. Dictation uses the cloud engine on Android and on the web; the
    // native SpeechRecognizer bridge is what the APK uses, and it is already
    // on-device. Revisit only with a WebView that implements the interface.
    this.rec = rec;
    this.listening = true;
    this.startedAt = Date.now();
    this.interim = '';
    this.final = '';
    this._written = '';

    rec.onresult = (e) => {
      let interim = '';
      let final = '';
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const r = e.results[i];
        if (r.isFinal) final += r[0].transcript;
        else interim += r[0].transcript;
      }
      if (final) this.final = (this.final + ' ' + final).trim();
      this.interim = interim.trim();
      this.render();
    };
    rec.onerror = (e) => {
      this.listening = false;
      this.rec = null;
      this.render();
      this.onError(e.error);
    };
    rec.onend = () => {
      this.listening = false;
      this.rec = null;
      this.render();
      /* Same reasoning as the auto-stop: the engine can end a session on its
         own, and by then the ledger in commit() makes a repeat harmless. */
      this.commit();
    };
    try {
      rec.start();
    } catch (err) {
      this.listening = false;
      this.rec = null;
      this.render();
      return false;
    }
    this.render();
    /* The browser has no "user stopped talking" event, so auto-stop after a
       pause in results. Silence that long is not someone thinking about a word. */
    if (this.cfg.web.auto_stop_ms) {
      clearTimeout(this._idle);
      const watch = () => {
        if (!this.listening) return;
        const gap = Date.now() - this.startedAt;
        if (gap > (this.cfg.web.min_speech_ms || 900)) {
          this._stopped = true;
          this.stop();
          /* Write it. The browser ending a session is not a reason to throw
             away what was said: this fires after the engine has already
             delivered its result, and nothing else would ever commit it. A
             tap that started dictation then goes quiet had the same effect -
             the words were recognised, held in final, and dropped. */
          this.commit();
        } else {
          this._idle = setTimeout(watch, 500);
        }
      };
      this._idle = setTimeout(watch, this.cfg.web.auto_stop_ms);
    }
    return true;
  },

  stop() {
    if (!this.listening) return;
    clearTimeout(this._idle);
    if (this.rec) { try { this.rec.stop(); } catch (e) { /* already stopped */ } }
    if (window.AndroidSTT && window.AndroidSTT.stop) window.AndroidSTT.stop();
    this.listening = false;
    this.render();
  },

  commit() {
    let text = (this.final + ' ' + this.interim).trim();
    this.final = '';
    this.interim = '';
    if (!text) return false;
    /* Only what has not been written yet. Android streams partials and then
       answers with the whole utterance again, so a stop that committed the
       interim was followed a moment later by the same words being appended:
       "what is a verb what is a verb". The web engine never does this, which
       is why it only showed up on a phone. */
    if (this._written && text.startsWith(this._written))
      text = text.slice(this._written.length).trim();
    if (!text) { this.render(); return false; }
    this._written = this._written ? this._written + ' ' + text : text;
    if (this.sink) {
      const sink = this.sink;
      this.sink = null;
      this.render();
      try { sink(text); } catch (e) { /* a paused drill must not break the mic */ }
      return true;
    }
    const box = document.getElementById('input');
    if (box) {
      /* Append, never replace. Assigning box.value meant that typing half a
         sentence and then dictating the other half deleted the half. */
      box.value = box.value.trim() ? box.value.trim() + ' ' + text : text;
      box.dispatchEvent(new Event('input'));
      box.focus();
    }
    this.render();
    return true;
  },

  onError(code) {
    const messages = {
      /* A toast is one left-to-right paragraph, so the English comes first
         and the Persian follows it; the reverse put a right-to-left run at
         the start of the line, hanging off the left edge. */
      'not-allowed': 'Microphone permission was denied — دسترسی به میکروفون داده نشد.',
      'service-not-allowed': 'The speech service is unavailable — سرویس گفتار در دسترس نیست.',
      'no-speech': 'Nothing heard, try again — چیزی نشنیدم، دوباره بگو.',
      'audio-capture': 'No microphone found — میکروفون پیدا نشد.',
      'network': 'This browser needs a network connection — شبکه لازم است برای این مرورگر.',
      'aborted': '',
    };
    const msg = messages[code];
    if (msg) toast(msg);
  },

  /* Interim text shown live above the composer while recording. */
  render() {
    const mic = document.getElementById('mic');
    if (mic) mic.classList.toggle('rec', this.listening);
    const panel = document.getElementById('stt');
    if (!panel) return;
    /* The fox lives in the band directly under this box, so she ducks while
       there are words in it rather than sitting on them. */
    document.body.classList.toggle('stt-open',
      !!(this.listening || this.interim || this.final));
    if (!this.listening && !this.interim && !this.final) {
      panel.hidden = true;
      panel.innerHTML = '';
      return;
    }
    panel.hidden = false;
    const bits = [];
    if (this.listening) {
      bits.push('<span class="stt-dot"></span><span class="stt-label">listening… · ' +
        '<bdi class="fa" lang="fa" dir="rtl">در حال شنیدن…</bdi></span>');
    }
    if (this.interim)
      bits.push('<span class="stt-interim">' + escapeHtml(this.interim) + '</span>');
    if (this.final)
      bits.push('<span class="stt-final">' + escapeHtml(this.final) + '</span>');
    panel.innerHTML = bits.join(' ');
  },
};
/* A transient message. The STT error path and the media player both want to
 * say something without putting it in the conversation, where it would read
 * as the tutor talking. */
let toastSeq = 0;
function toast(text, ms = 2600) {
  if (!text) return;
  const host = document.getElementById('toasthost');
  if (!host) return;
  const el = document.createElement('div');
  el.className = 'toast';
  el.textContent = text;
  host.appendChild(el);
  // cap the stack: three notices is a message, five is noise
  while (host.children.length > 3) host.firstElementChild.remove();
  const id = ++toastSeq;
  setTimeout(() => {
    if (!el.isConnected) return;
    el.classList.add('out');
    el.addEventListener('animationend', () => el.remove(), {once: true});
    setTimeout(() => el.remove(), 400);
  }, Math.max(900, ms));
  return id;
}

/* A single mic button in the composer: tap to talk, tap to stop.
 *
 * The icon is an inline SVG rather than the 🎙 emoji. The emoji depends on the
 * platform having a colour-emoji font, and where it does not the button renders
 * as an empty circle - which reads as a broken control, or as no control.
 */
const MIC_ICON =
  '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.9" ' +
  'stroke-linecap="round" aria-hidden="true">' +
  '<rect x="9" y="2.5" width="6" height="11" rx="3"/>' +
  '<path d="M5.5 11a6.5 6.5 0 0 0 13 0"/>' +
  '<path d="M12 17.5V21"/><path d="M8.5 21h7"/>' +
  '</svg>';

function mountMic() {
  const box = document.getElementById('input');
  if (!box) return;
  // Idempotent: anything that boots the page early mounts it too, and two mic
  // buttons is worse than none.
  if (document.getElementById('mic')) return;

  const btn = document.createElement('button');
  btn.id = 'mic';
  btn.className = 'mic';
  btn.type = 'button';
  const LABEL = 'Dictate with the microphone — با میکروفون تایپ کن';
  btn.title = LABEL;
  btn.setAttribute('aria-label', LABEL);
  btn.innerHTML = MIC_ICON;

  const usable = STT.supported();
  if (!usable) {
    // Firefox and a few other browsers have no speech engine. Rather than
    // hide the control - which is what made it look missing - show it in a
    // muted state and explain itself on tap.
    btn.setAttribute('aria-disabled', 'true');
    btn.title = STT.cfg?.web?.unsupported_message
      || 'This browser has no speech recognition — type instead. / این مرورگر گفتار را تشخیص نمی‌دهد — تایپ کن.';
    btn.setAttribute('aria-label', btn.title);
    btn.addEventListener('click', () => toast(btn.title, 4200));
  } else {
    /* Hold to talk. A short tap is still a tap, so it falls through to
       toggle-on and the next tap turns it off - which is what the button did
       before and what people reach for first.
     *
     * This used to be a click handler and nothing else, which is why holding
     * the button left it stuck: on Android a long press raises the text
     * selection callout and the browser suppresses the second click, so the
     * recogniser started and no second tap ever arrived. Pointer events fix
     * that, and setPointerCapture means the release is delivered even if the
     * finger slides off the button - which is what people do, especially
     * without looking.
     *
     * Every way out is covered: release, cancel, lost capture, the window
     * losing focus, the page being hidden, and a hard cap. Anything less and
     * there is a way to leave the microphone open with nothing showing it. */
    const HOLD_MS = 250;          // shorter than this is a tap, not a hold
    const MAX_MS = 60000;         // no dictation session runs forever
    let pressAt = 0;
    let wasListening = false;     // was it already running when this began?
    let capped = 0;

    const stop = () => {
      if (!STT.listening) return;
      STT.stop();
      STT.commit();
    };

    btn.addEventListener('pointerdown', (ev) => {
      ev.preventDefault();                    // no callout, no text selection
      pressAt = Date.now();
      // A press that begins while dictation is already running is a request
      // to stop, however brief. The previous version tracked a `held` flag
      // that only a long press ever set, so tapping a second time fell
      // through as "too short, keep listening" and the button could not be
      // turned off at all - you had to hold it.
      wasListening = STT.listening;
      if (!STT.listening) {
        // begin() returns false when the recogniser refuses to start - a denied
        // OS permission, or a microphone already in use. Swallowing that leaves
        // a button that does nothing, which is the same invisible control
        // problem in a different costume.
        if (!STT.begin()) {
          toast('🎙 Could not start dictation — check the microphone ' +
                'permission. / دسترسی به میکروفون را بررسی کن.', 3800);
          pressAt = 0;
          return;
        }
        clearTimeout(capped);
        capped = setTimeout(stop, MAX_MS);
      }
      try { btn.setPointerCapture(ev.pointerId); } catch (e) { /* not fatal */ }
    });

    const release = (ev) => {
      try { btn.releasePointerCapture(ev.pointerId); } catch (e) { /* fine */ }
      if (!STT.listening) { pressAt = 0; return; }
      const held_ms = Date.now() - pressAt;
      pressAt = 0;
      // Stop if it was already running, or if this was a hold. A short press
      // that started it deliberately leaves it running for the next tap.
      if (wasListening || held_ms >= HOLD_MS) stop();
      wasListening = false;
    };

    btn.addEventListener('pointerup', release);
    // The two ways a press ends without a click reaching the button.
    btn.addEventListener('pointercancel', release);
    btn.addEventListener('lostpointercapture', () => {
      // Only if the pointer genuinely went away - releasePointerCapture in
      // release() also fires this, and stopping there would cut every hold
      // short the moment it started.
      if (pressAt && Date.now() - pressAt >= HOLD_MS) stop();
    });

    // Backgrounded, switched away, or the screen locked: stop rather than hold
    // the microphone open behind a UI nobody can see.
    const bail = () => { if (STT.listening) stop(); };
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) bail();
    });
    window.addEventListener('pagehide', bail);
    window.addEventListener('blur', bail);
  }

  box.parentNode.insertBefore(btn, box.nextSibling);
  STT.render();

  // one short hint the first time, so the control is found rather than
  // rediscovered. Shown at most once per browser.
  if (usable) {
    const KEY = 'fluentify.mic.hinted';
    try {
      if (!localStorage.getItem(KEY)) {
        btn.classList.add('hint');
        localStorage.setItem(KEY, '1');
        btn.addEventListener('animationend', () => btn.classList.remove('hint'),
                             {once: true});
      }
    } catch (e) { /* private mode: the hint is a nicety, so ignore */ }
  }
}

if ('speechSynthesis' in window) {
  speechSynthesis.onvoiceschanged = () => { Speech.voice = Speech.pickVoice(); };
}

async function loadPhonetics() {
  const rail = document.getElementById('phrail');
  const view = document.getElementById('phview');
  if (!rail || !view || rail.childElementCount) return;   // already built
  let sections;
  try {
    const r = await fetch('/api/phonetics');
    sections = await r.json();
  } catch (e) {
    view.innerHTML = '<div class="pblurb">Phonetics unavailable offline. / <bdi class="fa" lang="fa" dir="rtl">آموزش تلفظ در دسترس نیست.</bdi></div>';
    return;
  }
  if (!sections.length) return;

  const stop = (b) => {
    Speech.stop();
    [...view.querySelectorAll('.pplay')].forEach((n) => {
      n.classList.remove('playing');
      n.textContent = '▶';
    });
    b.textContent = '▶';
  };

  const render = (sec, idx) => {
    [...rail.children].forEach((b, i) => b.classList.toggle('on', i === idx));
    view.innerHTML = '';

    const head = document.createElement('div');
    head.className = 'phead';
    const h = document.createElement('div');
    h.className = 'ptitle';
    h.textContent = sec.icon + ' ' + sec.title_en;
    const lvl = document.createElement('span');
    lvl.className = 'lvl';
    lvl.textContent = 'CEFR ' + sec.level;
    const fa = document.createElement('span');
    fa.className = 'pfa';
    fa.textContent = sec.title_fa;
    h.append(lvl, fa);
    const blurb = document.createElement('div');
    blurb.className = 'pblurb';
    blurb.textContent = sec.blurb_en;
    head.append(h, blurb);
    view.appendChild(head);

    if (sec.tip_en) {
      const tip = document.createElement('div');
      tip.className = 'ptip';
      const k = document.createElement('span');
      k.className = 'pk';
      k.textContent = '🔑';
      const t = document.createElement('span');
      t.className = 'pt';
      t.textContent = sec.tip_en;
      tip.append(k, t);
      view.appendChild(tip);
    }

    (sec.groups || []).forEach((g) => {
      const wrap = document.createElement('div');
      wrap.className = 'pgroup';
      const gh = document.createElement('div');
      gh.className = 'ghead';
      gh.textContent = g.name_en;
      wrap.appendChild(gh);

      const grid = document.createElement('div');
      grid.className = 'prows';
      (g.rows || []).forEach((r) => {
        const row = document.createElement('div');
        row.className = 'prow';

        const main = document.createElement('div');
        main.className = 'pmain';
        const add = (cls, txt) => {
          if (!txt) return;
          const d = document.createElement('div');
          d.className = cls;
          d.textContent = txt;
          main.appendChild(d);
        };
        add('pip', r.ip);
        add('psub', r.sub);
        // skip the spoken-example line when it would just repeat the symbol
        if (r.say && r.say !== r.ip && !r.sub.includes(r.say)) add('psay', r.say);
        add('pwords', r.words);
        add('pnote', r.note);

        const btn = document.createElement('button');
        btn.className = 'pplay';
        btn.textContent = '▶';
        btn.title = 'Hear it — گوش بده';

        const speak = (ev) => {
          if (ev) ev.stopPropagation();
          if (Speech.isPlaying(r.say)) { stop(btn); return; }
          [...view.querySelectorAll('.pplay')].forEach((n) => {
            n.classList.remove('playing');
            n.textContent = '▶';
          });
          btn.classList.add('playing');
          btn.textContent = '❚❚';
          if (!Speech.speak(r.say, () => stop(btn))) {
            stop(btn);
            add0('🔇 No speech engine on this device — / روی این دستگاه موتور گفتار نیست.');
          }
        };
        const add0 = (msg) => add('pnote', msg);
        btn.onclick = speak;
        row.onclick = speak;          // the row is a bigger tap target
        row.append(main, btn);
        grid.appendChild(row);
      });
      wrap.appendChild(grid);
      view.appendChild(wrap);
    });
  };

  rail.innerHTML = '';
  sections.forEach((sec, idx) => {
    const b = document.createElement('button');
    b.className = 'phtab';
    b.setAttribute('role', 'tab');
    b.textContent = sec.icon + ' ' + sec.title_en.split(' — ')[0].split(' &')[0];
    b.title = sec.title_en + ' — ' + sec.title_fa;
    const lvl = document.createElement('i');
    lvl.textContent = sec.level;
    b.appendChild(lvl);
    b.onclick = () => {
      render(sec, idx);
      b.scrollIntoView({block: 'nearest', inline: 'nearest',
                        behavior: 'smooth'});
    };
    rail.appendChild(b);
  });
  render(sections[0], 0);
}

async function loadListening() {
  const box = document.getElementById('llevels');
  try {
    const r = await fetch('/api/listening');
    const levels = await r.json();
    if (!levels.length) return;

    const tabs = document.createElement('div');
    tabs.className = 'ltabs';
    const list = document.createElement('div');
    list.className = 'llist';

    const render = (lv, idx) => {
      [...tabs.children].forEach((b, i) => b.classList.toggle('on', i === idx));
      list.innerHTML = '';
      const blurb = document.createElement('div');
      blurb.className = 'lblurb';
      blurb.innerHTML = renderText(lv.blurb_en + ' — ' + lv.blurb_fa);
      list.appendChild(blurb);
      lv.sentences.forEach((s) => {
        const row = document.createElement('div');
        row.className = 'lrow';
        const btn = document.createElement('button');
        btn.className = 'lplay';
        btn.textContent = '▶';
        btn.title = 'Play — تلفظ کن';
        const text = document.createElement('div');
        text.className = 'ltext';
        const en = document.createElement('div');
        en.className = 'en';
        en.textContent = s.en;
        const fa = document.createElement('div');
        fa.className = 'fa';
        fa.textContent = s.fa;
        text.append(en, fa);
        row.append(btn, text);

        btn.onclick = (ev) => {
          ev.stopPropagation();
          if (Speech.isPlaying(s.en)) {
            Speech.stop();
            row.classList.remove('playing');
            btn.textContent = '▶';
            return;
          }
          [...list.querySelectorAll('.lrow')].forEach((n) => {
            n.classList.remove('playing');
            n.firstChild.textContent = '▶';
          });
          row.classList.add('playing');
          btn.textContent = '❚❚';
          const spoken = Speech.speak(s.en, () => {
            row.classList.remove('playing');
            btn.textContent = '▶';
          });
          if (!spoken) {
            row.classList.remove('playing');
            btn.textContent = '▶';
            // a system notice, not the tutor speaking
            toast('🔇 No speech engine on this device — the sentence is still ' +
                  'here to practise. / روی این دستگاه صدایی در دسترس نیست.', 4000);
          }
        };
        row.onclick = (ev) => btn.onclick(ev);   // the row is just a bigger play target
        list.appendChild(row);
      });
    };

    levels.forEach((lv, idx) => {
      const b = document.createElement('button');
      b.className = 'ltab';
      b.textContent = lv.id;
      b.title = lv.title_en;
      b.onclick = () => render(lv, idx);
      tabs.appendChild(b);
    });

    const toBbc = document.createElement('button');
    toBbc.className = 'bbc-open';
    toBbc.textContent = '📻  BBC 6 Minute English — graded A2 → C1';
    toBbc.title = 'Real BBC episodes, graded by listening difficulty';
    toBbc.onclick = () => loadBBC();

    box.innerHTML = '';
    box.append(toBbc, tabs, list);
    render(levels[0], 0);
    PanelSearch.attachAll();
  } catch (e) { /* panel stays empty offline */ }
}


/* ---------- BBC 6 Minute English ----------
   An audio catalogue: the mirrored clips and the episode links are what this
   section offers. The transcript PDFs are not shown at all - BBC's download
   links are unreliable from a WebView and several have been retired, so a
   "Transcript" control that opens a dead PDF is worse than no control.

   Each episode is graded A2→C1 by tools/fetch_bbc_6min.py, which reads the
   official transcript and blends vocabulary stretch, the share of B2+ words,
   sentence length, clause density and speaking rate. The grade still comes
   from the transcript, so the band is what you actually hear, not the topic;
   the transcript is simply not surfaced as a download. */
let bbcDocCache = null;
/* The graded catalogue, cached. It is about a megabyte, and the boot warms it
   so the first tap on the Listen tab is not the thing that discovers it. */
async function bbcDoc() {
  bbcDocCache ||= fetch('/api/bbc').then((r) => r.json());
  return bbcDocCache;
}

async function loadBBC() {
  const box = document.getElementById('llevels');
  if (!box) return;
  try {
    const doc = await bbcDoc();
    // Audio first, and only audio. An episode with no stream has nothing this
    // section can play, and its transcript link is exactly the dead PDF the
    // section no longer offers - so it is not listed at all.
    const all = doc.episodes || [];
    const episodes = all.filter((e) => e.audio);
    if (!episodes.length) return;

    const wrap = document.createElement('div');
    wrap.className = 'bbc';

    const head = document.createElement('div');
    head.className = 'bbc-head';
    const badge = document.createElement('button');
    badge.className = 'bbc-back';
    badge.textContent = '🎧  CEFR sentences';
    badge.title = 'Back to the built-in listening levels';
    badge.onclick = () => loadListening();
    head.appendChild(badge);

    const note = document.createElement('div');
    note.className = 'bbc-note';
    const dist = doc.distribution || {};
    // '?' means "ungraded", not a level - it must not be listed as one
    const spread = Object.keys(dist).filter((k) => k && k !== '?').sort().join(' · ');
    const ungradedN = episodes.filter((e) => !e.level).length;
    const tail = ungradedN ? ` ${ungradedN} are still ungraded.` : '';
    // Count what is actually listed, not doc.count. Episodes with no playable
    // stream are filtered out above, so quoting the catalogue total would
    // claim more episodes are on screen than any level tab can add up to.
    const hidden = (doc.count || 0) - episodes.length;
    const dropped = hidden > 0
      ? ` ${hidden} have no playable audio and are not listed.`
      : '';
    note.textContent = spread
      ? `${episodes.length} BBC episodes — ${episodes.length - ungradedN} graded ` +
        `${spread}. Each grade is set from the episode's transcript: vocabulary, ` +
        `sentence length and speaking pace.${tail}${dropped} ` +
        'Audio plays from the offline mirror. / <bdi class="fa" lang="fa" dir="rtl">صدا از نسخه آفلاین پخش می‌شود.</bdi>'
      : `${episodes.length} episodes from BBC Learning English. ` +
        'Audio plays from the offline mirror.';
    head.appendChild(note);
    wrap.appendChild(head);

    // Level filter. Episodes without a grade get their own tab rather than
    // being silently lumped into "All" as if they were A2.
    const levels = [...new Set(episodes.map((e) => e.level).filter(Boolean))].sort();
    const ungraded = episodes.filter((e) => !e.level).length;
    const bar = document.createElement('div');
    bar.className = 'bbc-tabs';
    let current = 'all';
    const list = document.createElement('div');
    list.className = 'bbc-list';

    /* 1126 episodes is too many to render at once, and a hard cap with no
       way past it is worse than a slow one: "Showing 80 of 1126" with no
       button just tells the user the rest is unreachable. So it pages - 80 at
       a time, more on request, and the count stays honest throughout. */
    const PAGE = 80;
    let shown = PAGE;
    const matching = () => episodes
      // an ungraded episode has level === null, not '?', so normalise
      // before comparing or the "Not graded" tab comes back empty
      .filter((e) => current === 'all' || (e.level || '?') === current);

    const paint = () => {
      list.innerHTML = '';
      const all = matching();
      const rows = all.slice(0, shown);
      if (!rows.length) {
        const empty = document.createElement('div');
        empty.className = 'bbc-empty';
        empty.textContent = 'Nothing at this level yet.';
        list.appendChild(empty);
        return;
      }
      for (const ep of rows) {
        const card = document.createElement('div');
        card.className = 'bbc-row';

        const head2 = document.createElement('div');
        head2.className = 'bbc-row-head';
        const lvl = document.createElement('span');
        lvl.className = 'bbc-lvl lvl-' + (ep.level || 'none');
        lvl.textContent = ep.level || '–';
        if (!ep.level) lvl.title = 'Not graded yet';
        const title = document.createElement('span');
        title.className = 'bbc-title';
        title.textContent = ep.title;
        head2.append(lvl, title);
        card.appendChild(head2);

        if (ep.blurb) {
          const blurb = document.createElement('div');
          blurb.className = 'bbc-blurb';
          blurb.textContent = ep.blurb;
          card.appendChild(blurb);
        }

        const meta = document.createElement('div');
        meta.className = 'bbc-meta';
        const bits = [];
        if (ep.year) bits.push(ep.year);
        if (ep.duration) bits.push(Math.round(ep.duration / 60) + ' min');
        const st = ep.stats || {};
        if (!ep.level) bits.push('not graded yet');
        if (st.avg_sentence) bits.push('sentences ~' + st.avg_sentence + ' words');
        if (st.challenge_pct != null) bits.push(st.challenge_pct + '% B2+');
        if (st.c1c2_pct) bits.push(st.c1c2_pct + '% C1');
        meta.textContent = bits.join(' · ');
        card.appendChild(meta);

        const bar2 = document.createElement('div');
        bar2.className = 'bbc-actions';

        const play = document.createElement('button');
        play.className = 'bbc-play';
        play.textContent = '▶  Play';
        const label = (on) => {
          play.textContent = on ? '❚❚  Pause' : '▶  Play';
          play.classList.toggle('on', !!on);
        };
        // The bar under the header owns the audio; the card only says where
        // to start it and mirrors what came back, so a six-minute episode can
        // be paused or stopped from anywhere without hunting for its card.
        play.onclick = () => {
          // Pressing the card that is already playing pauses or resumes it,
          // exactly as the bar does. Treating any playing clip as "stop"
          // meant the button said Play while pressing it wound up the audio.
          if (Player.currentSrc === ep.audio) { Player.toggle(); return; }
          Player.clip(ep.audio, ep.title || ep.url, label);
        };
        bar2.appendChild(play);

        const page = document.createElement('a');
        page.className = 'bbc-link';
        page.href = ep.url;
        page.target = '_blank';
        page.rel = 'noopener noreferrer';
        page.textContent = 'Episode';
        bar2.appendChild(page);

        if (ep.worksheet_url) {
          const ws = document.createElement('a');
          ws.className = 'bbc-link';
          ws.href = ep.worksheet_url;
          ws.target = '_blank';
          ws.rel = 'noopener noreferrer';
          ws.textContent = 'Worksheet';
          bar2.appendChild(ws);
        }
        card.appendChild(bar2);
        list.appendChild(card);
      }
      if (all.length > rows.length) {
        const more = document.createElement('button');
        more.className = 'bbc-more';
        const left = all.length - rows.length;
        more.textContent = `Show ${Math.min(PAGE, left)} more · ` +
                           `${rows.length} of ${all.length} shown`;
        more.onclick = () => { shown += PAGE; paint(); };
        list.appendChild(more);
      }
    };

    const addTab = (id, label) => {
      const b = document.createElement('button');
      b.className = 'bbc-tab';
      b.textContent = label;
      b.dataset.level = id;
      b.onclick = () => {
        current = id;
        shown = PAGE;              // a new level starts at one page again
        [...bar.children].forEach((c) => c.classList.toggle('on', c === b));
        paint();
      };
      bar.appendChild(b);
    };
    addTab('all', `All (${episodes.length})`);
    levels.forEach((lv) => {
      const n = episodes.filter((e) => e.level === lv).length;
      addTab(lv, `${lv} (${n})`);
    });
    if (ungraded) addTab('?', `Not graded (${ungraded})`);
    bar.firstChild.classList.add('on');

    wrap.append(bar, list);
    box.innerHTML = '';
    box.appendChild(wrap);
    paint();
  } catch (e) { /* panel stays empty offline */ }
}

/* phrases panel (fetched from phrases.json via the server) */
/* ---------- word architecture ----------
   Every vocabulary word carries its form family (decide → decides · decided ·
   deciding). The chips live inside each CEFR level of the Sentences panel;
   tapping one opens its detail card. */
const POS_FA = {noun: 'اسم', verb: 'فعل', adj: 'صفت', adv: 'قید', prep: 'حرف اضافه'};
const wordArch = {};          // level -> array of entries
let wordArchLoaded = false;

function showWord(entry) {
  const card = document.getElementById('wdetail');
  card.innerHTML = '';

  const head = document.createElement('div');
  head.className = 'wd-head';

  const title = document.createElement('div');
  title.className = 'wd-word';
  title.textContent = entry.en;

  const pos = document.createElement('span');
  pos.className = 'wd-pos';
  pos.textContent = (POS_FA[entry.pos] || entry.pos);
  title.appendChild(pos);

  const say = document.createElement('button');
  say.className = 'pplay';
  say.textContent = '▶';
  say.title = 'Listen — گوش بده';
  say.onclick = () => {
    if (Speech.isPlaying(entry.en)) { Speech.stop(); say.textContent = '▶'; return; }
    say.textContent = '❚❚';
    Speech.speak(entry.en, () => (say.textContent = '▶'));
  };
  say.onkeydown = (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); say.click(); } };

  const close = document.createElement('button');
  close.className = 'wd-close';
  close.textContent = '✕';
  close.setAttribute('aria-label', 'Close');
  close.onclick = () => card.classList.remove('open');

  head.append(title, say, close);

  const mean = document.createElement('div');
  mean.className = 'wd-mean';
  // One line, two scripts: the word is English, the meaning is Persian. The
  // meaning is its own island, so its letters read right to left and its full
  // stop stays at its end instead of jumping to the line's start.
  mean.setAttribute('dir', 'ltr');
  mean.innerHTML = '<b>' + escapeHtml(entry.en) + '</b> — ' +
    '<bdi class="fa" lang="fa" dir="rtl">' + escapeHtml(entry.fa) + '</bdi>';

  card.append(head, mean);

  if (entry.forms && entry.forms.length) {
    const lab = document.createElement('div');
    lab.className = 'wd-lab';
    lab.innerHTML = 'Word architecture / <bdi class="fa" lang="fa" dir="rtl">ساختار واژه</bdi>';
    const grid = document.createElement('div');
    grid.className = 'wd-forms';
    entry.forms.forEach((f) => {
      const chip = document.createElement('span');
      chip.className = 'wd-form';
      chip.innerHTML = '<b>' + escapeHtml(f.f) + '</b><i>' + escapeHtml(f.n) + '</i>';
      grid.appendChild(chip);
    });
    card.append(lab, grid);
  }

  const meta = document.createElement('div');
  meta.className = 'wd-meta';
  meta.textContent = 'CEFR ' + entry.level + ' · ' + (entry.domains || []).length +
    ' domain' + ((entry.domains || []).length === 1 ? '' : 's');
  card.appendChild(meta);

  // save it for the review section
  const starWrap = document.createElement('div');
  starWrap.className = 'wd-star';
  const star = document.createElement('button');
  const paintStar = () => {
    const on = Review.has(entry.en);
    star.classList.toggle('on', on);
    star.textContent = on ? '⭐ In review' : '☆ Save to review';
  };
  star.className = 'rstar';
  star.onclick = () => {
    Review.toggle(entry);
    paintStar();
    add(Review.has(entry.en)
      ? `⭐ Added **${entry.en}** to your review list — ${Review.items.length} word(s) saved.`
      : `Removed **${entry.en}** from your review list.`, 'bot');
  };
  paintStar();
  const hint = document.createElement('span');
  hint.className = 'why';
  hint.textContent = 'then open ⭐ Review in the top bar';
  starWrap.append(star, hint);
  card.appendChild(starWrap);

  card.classList.add('open');
  card.scrollIntoView({block: 'nearest', behavior: 'smooth'});
}

/* word_arch.json is 302 KB of boot payload and only fills the word chips in
   the Sentences panel, so it is fetched on first use. The promise is kept so
   two callers cannot start two downloads. */
let wordArchPromise = null;
async function loadWordArch() {
  if (wordArchLoaded) return;
  if (wordArchPromise) return wordArchPromise;
  wordArchPromise = (async () => {
    try {
    const r = await fetch('/api/wordarch');
    const bands = await r.json();
    Object.assign(wordArch, bands);
    wordArchLoaded = true;
    paintWordArch();
    } catch (e) {
      const slots = document.querySelectorAll('#ftopics [data-words]');
      slots.forEach((slot) => {
        slot.innerHTML = '<div class="wd-more">Word forms unavailable offline.</div>';
      });
    }
  })().finally(() => {
    wordArchPromise = null;
  });
  return wordArchPromise;
}

/* Fetching the archive and painting the chips are separate because either can
   happen first: the fetch waits for the panel to open, the paint has to
   follow the topic buttons being rebuilt. Folded together, offline wins the
   race and finds no slots to fill. */
function paintWordArch() {
  if (!wordArchLoaded) return;
  // drop the placeholder text and insert the real chips into each level
  document.querySelectorAll('#ftopics [data-words]').forEach((slot) => {
      const items = wordArch[slot.dataset.words] || [];
      slot.innerHTML = '';
      const lab = document.createElement('div');
      lab.className = 'wd-lab';
      lab.innerHTML = '🧩 New words of this level — tap one to see its architecture' +
        ' / <bdi class="fa" lang="fa" dir="rtl">واژه‌های این سطح</bdi>';
      slot.appendChild(lab);

      // A1 has ~800 words; rendering them all at once is slow on a phone, so
      // show a page at a time and let the learner open the rest.
      const PAGE = 48;
      let shown = Math.min(PAGE, items.length);
      const grid = document.createElement('div');
      grid.className = 'wd-chips';

      const paint = () => {
        grid.innerHTML = '';
        items.slice(0, shown).forEach((entry) => {
          const b = document.createElement('button');
          b.className = 'wchip';
          b.textContent = entry.en;
          b.title = entry.fa;
          b.onclick = () => {
            [...slot.querySelectorAll('.wchip.on')].forEach((n) => n.classList.remove('on'));
            b.classList.add('on');
            showWord(entry);
          };
          grid.appendChild(b);
        });
      };
      paint();
      slot.appendChild(grid);

      const more = document.createElement('button');
      more.className = 'wd-more btn';
      more.onclick = () => {
        const open = more.dataset.open === '1';
        shown = open ? PAGE : items.length;
        more.dataset.open = open ? '0' : '1';
        more.textContent = open
          ? items.length + ' words at ' + slot.dataset.words + ' — show more'
          : 'showing all ' + items.length + ' · show fewer';
        paint();
      };
      more.dataset.open = '0';
      more.textContent = items.length + ' words at ' + slot.dataset.words +
        (items.length > PAGE ? ' — show all' : '');
      slot.appendChild(more);
    });
}

async function loadPhrases() {
  const box = document.getElementById('ftopics');
  try {
    const r = await fetch('/api/phrases');
    const topics = await r.json();
    box.innerHTML = '';
    byLevel(topics).forEach(([level, items]) => {
      const sec = document.createElement('div');
      sec.className = 'vgroup';
      sec.appendChild(levelHead(level, items.length, ' topics', 'موضوع'));
      const row = document.createElement('div');
      row.className = 'vrow';
      items.forEach((t) => {
        const b = document.createElement('button');
        b.className = 'ftopic';
        b.title = t.count + ' sentences — ' + t.title_fa;
        const en = document.createElement('span');
        en.textContent = t.title_en;
        const fa = document.createElement('span');
        fa.className = 'fa';
        fa.textContent = t.title_fa;
        const n = document.createElement('span');
        n.className = 'n';
        n.textContent = t.count;
        b.append(en, fa, n);
        b.onclick = () => send(t.query);
        row.appendChild(b);
      });
      sec.appendChild(row);

      const slot = document.createElement('div');
      slot.className = 'wd-slot';
      slot.dataset.words = level;
      slot.innerHTML = '<div class="wd-more">Loading word forms…</div>';
      sec.appendChild(slot);

      box.appendChild(sec);
    });
    // Fetch if it is not in hand, then paint into the slots just created.
    // The two are separate calls because either can be the first: on the web
    // the 302 KB archive arrives after this panel has rendered, and offline it
    // is already in memory and resolves before the slots exist at all. Calling
    // loadWordArch() on its own would return early the second time and leave
    // five empty "Loading word forms…" placeholders on screen.
    await loadWordArch();
    paintWordArch();
  } catch (e) {
    box.innerHTML = '<div class="pblurb">Sentences unavailable offline. / <bdi class="fa" lang="fa" dir="rtl">جملات در دسترس نیست.</bdi></div>';
  }
}

/* vocabulary panel — grouped, one compact pill per domain */
/* The CEFR ladder, shared by the vocabulary and sentence panels so a learner
   can always see which band they are looking at. */
const LEVELS = [
  ['A1', 'Beginner', 'مبتدی'],
  ['A2', 'Elementary', 'پایه'],
  ['B1', 'Intermediate', 'متوسط'],
  ['B2', 'Upper-interm.', 'پیشرفته'],
  ['C1', 'Advanced', 'پیشرفتهٔ بالا'],
  ['C2', 'Mastery', 'تسلط'],
];
const LEVEL_NAME = Object.fromEntries(LEVELS.map(([id, en, fa]) => [id, {en, fa}]));

/* Flat list → sections grouped by level, biggest bands first. */
function byLevel(items) {
  const order = LEVELS.map(([id]) => id);
  const buckets = new Map(order.map((id) => [id, []]));
  items.forEach((it) => buckets.get(it.level || 'A1').push(it));
  return order
    .map((id) => [id, buckets.get(id)])
    .filter(([, list]) => list.length);
}

function levelHead(level, count, noun, nounFa) {
  const head = document.createElement('div');
  head.className = 'vgroup-head';
  const name = LEVEL_NAME[level] || {en: level, fa: level};
  const b = document.createElement('b');
  b.className = 'lv';
  b.textContent = level;
  // The band, then the count in English. The Persian name is its own island
  // and the Persian noun sits with it, so no line here mixes the two scripts
  // into one text run: "27 domains · دسته" was a single left-to-right string
  // with a Persian word dropped in the middle of it.
  const count_ = document.createElement('span');
  count_.className = 'count';
  count_.textContent = count + (noun || '');
  head.append(
    b,
    document.createTextNode(name.en),
    Object.assign(document.createElement('span'), {className: 'fa', textContent: name.fa}),
    count_,
  );
  if (nounFa) {
    // the noun only: the count is already on the line in English, and
    // "27 domains · دسته 27" said the number twice
    const faCount = document.createElement('span');
    faCount.className = 'count fa';
    faCount.textContent = nounFa;
    head.append(faCount);
  }
  return head;
}

async function loadVocabulary() {
  const box = document.getElementById('domains');
  try {
    const r = await fetch('/api/vocabulary');
    const groups = await r.json();
    // the API returns themed groups; flatten so the panel can regroup by level
    const all = groups.flatMap((g) => g.items.map((d) => ({...d, group_fa: g.fa})));
    const search = document.getElementById('vsearch');
    if (search) {
      search.placeholder = `Search ${all.length} domains… / جست‌وجوی دسته‌ها…`;
    }
    const filter = (window.__vFilter != null ? window.__vFilter
      : (search?.value || '')).trim().toLowerCase();

    box.innerHTML = '';
    byLevel(all).forEach(([level, items]) => {
      const shown = filter
        ? items.filter((d) => (d.title_en + ' ' + d.title_fa).toLowerCase().includes(filter))
        : items;
      if (filter && !shown.length) return;
      const sec = document.createElement('div');
      sec.className = 'vgroup';
      sec.appendChild(levelHead(level, shown.length, ' domains', 'دسته'));
      const row = document.createElement('div');
      row.className = 'vrow';
      shown.forEach((d) => {
        const b = document.createElement('button');
        b.className = 'vbtn';
        // English first, Persian at the end: a tooltip that opens with Persian
        // then says "words" reads backwards for the learner it is aimed at.
        b.title = d.title_en + ' — ' + d.title_fa + ' · ' + d.count + ' words';
        b.append(
          Object.assign(document.createElement('span'), {textContent: d.title_en}),
          Object.assign(document.createElement('span'), {className: 'n', textContent: d.count}),
        );
        // alt-click → ask in Persian instead
        b.onclick = (ev) => send(ev.altKey ? d.query_fa : d.query_en);
        row.appendChild(b);
      });
      sec.appendChild(row);
      box.appendChild(sec);
    });

    const empty = document.getElementById('vempty');
    if (empty) empty.hidden = !(filter && !box.children.length);
  } catch (e) {
    box.innerHTML = '<div class="pblurb">Vocabulary unavailable offline. / <bdi class="fa" lang="fa" dir="rtl">واژگان در دسترس نیست.</bdi></div>';
  }
}
/* ============================================================================
 * READING
 * Six reading strategies. Each one is a short lesson - what the strategy is,
 * why it earns its place, the moves that make it work - and then a passage
 * that needs exactly that strategy, with four kinds of question on it.
 *
 * Two views, one container: the list is a table of contents and the lesson is
 * what a tap on a row produces. Answers live in localStorage per strategy, so
 * closing the panel to answer a message does not throw the work away - the
 * page is a chat app, and every panel is closed the moment you type.
 *
 * Nothing here is generated at boot: reading.json is 83 KB and no other
 * section needs it, so it is read the first time the panel opens.
 * ==========================================================================*/
const Reading = (() => {
  const KEY = 'fluentify.reading.v1';
  const body = () => document.getElementById('rdbody');
  let doc = null;          // reading.json, once
  let pending = null;      // the in-flight fetch
  let view = 'list';       // 'list' | a strategy id
  let pi = 1;              // which of the strategy's three passages is open

  /* --- state, one entry per (strategy, practice). Practice 1 keeps the plain
     strategy id, so every answer a learner gave before the section grew a
     second and third passage is still where it was.
     {id: {picks:{qid:value}, checked:{group:true}, essays:{qid:text}, models:{qid:true}}} */
  const skey = (id, p) => p === 1 ? id : id + '#' + p;
  function read() {
    try { return JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { return {}; }
  }
  function write(all) {
    try { localStorage.setItem(KEY, JSON.stringify(all)); } catch (e) { /* private mode */ }
  }
  function state(id, p) {
    const all = read();
    const k = skey(id, p || 1);
    all[k] = all[k] || {picks: {}, checked: {}, essays: {}, models: {}};
    return all[k];
  }
  function patch(id, p, fn) {
    const all = read();
    const k = skey(id, p || 1);
    all[k] = all[k] || {picks: {}, checked: {}, essays: {}, models: {}};
    fn(all[k]);
    write(all);
  }
  const patchCur = (fn) => patch(_current, pi, fn);
  const stateCur = () => state(_current, pi);

  /* --- tiny DOM helper: h('div', {class: 'x'}, child, 'text') ------------ */
  function h(tag, props, ...kids) {
    const node = document.createElement(tag);
    Object.entries(props || {}).forEach(([k, v]) => {
      if (v === null || v === undefined || v === false) return;
      if (k === 'class') node.className = v;
      else if (k === 'html') node.innerHTML = v;
      else if (k.startsWith('on')) node.addEventListener(k.slice(2), v);
      else node.setAttribute(k, v === true ? '' : v);
    });
    kids.flat().forEach((kid) => {
      if (kid === null || kid === undefined || kid === false) return;
      node.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
    });
    return node;
  }
  /* Persian always in its own isolated run, never bare inside an English line */
  const fa = (text, cls) => h('span', {class: (cls || '') + ' fa', dir: 'rtl', lang: 'fa'}, text);
  const faP = (text, cls) => h('p', {class: (cls || '') + ' fa', dir: 'rtl', lang: 'fa'}, text);

  const opening = (r) => r.counts.blanks + r.counts.mcq + r.counts.truefalse;
  const total = (s) => s.counts.blanks + s.counts.mcq + s.counts.truefalse;
  const label = (n) => n === 1 ? 'question' : 'questions';

  /* The three groups that can be marked. An essay is read against a model,
     so it never counts as checked - pretending otherwise would be a lie. */
  const GROUPS = ['blanks', 'mcq', 'truefalse'];

  /* How far through one passage a learner is: 0-3 groups marked. */
  function marked(id, p) {
    const st = read()[skey(id, p)] || {};
    return GROUPS.filter((g) => st.checked && st.checked[g]).length;
  }
  function passageCounts(s) {
    let full = 0, markedGroups = 0;
    s.readings.forEach((r, k) => {
      const got = marked(s.id, k + 1);
      if (got === GROUPS.length) full += 1;
      markedGroups += got;
    });
    return {full, markedGroups};
  }

  /* Repaint the passage chips in place. Checking a group must not redraw the
     page, or the feedback that was just appended would go with it. */
  function refreshTabs() {
    const s = doc.strategies.find((x) => x.id === _current);
    if (!s) return;
    body().querySelectorAll('.rdpracbtn').forEach((btn, k) => {
      if (!s.readings[k]) return;
      const c = marked(_current, k + 1);
      const fin = c === GROUPS.length;
      const ps = btn.querySelector('.ps');
      if (ps) ps.textContent = fin ? '\u2713' : c + '/3';
      btn.classList.toggle('done', fin);
      btn.setAttribute('aria-label', 'Passage ' + (k + 1) + ': ' +
        s.readings[k].title.en + ' - ' +
        (fin ? 'finished' : c + ' of 3 parts checked'));
    });
  }

  function progress() {
    let strategies = 0, passages = 0, sets = 0;
    doc.strategies.forEach((s) => {
      const c = passageCounts(s);
      passages += c.full;
      sets += c.markedGroups;
      if (c.full === s.readings.length) strategies += 1;
    });
    const allPassages = doc.totals.practices;
    const totalSets = allPassages * GROUPS.length;
    return {
      strategies, passages, allPassages, sets, totalSets,
      pct: totalSets ? Math.round(sets * 100 / totalSets) : 0,
    };
  }

  /* Marking a blank: case, full stops and stray spaces are not the skill
     being tested, so they are folded away before the comparison. */
  const tidy = (x) => String(x).toLowerCase()
    .replace(/[.,!?;:'"«»()\u00a3\u20ac$]/g, ' ')
    .replace(/\s+/g, ' ').trim();
  const accepts = (item, given) =>
    [item.answer].concat(item.also || []).some((a) => tidy(a) === tidy(given));

  /* Feedback says which paragraph answers the question, and the button takes
     the reader there instead of asking them to count paragraphs. */
  function showPara(n) {
    const ps = body().querySelectorAll('.rdpassage .rdpara');
    const p = ps[n - 1];
    if (!p) return;
    p.scrollIntoView({block: 'center', behavior: 'smooth'});
    p.classList.add('flash');
    setTimeout(() => p.classList.remove('flash'), 1400);
  }
  function evidence(n) {
    if (!n) return null;
    return h('button', {type: 'button', class: 'rdev', onclick: () => showPara(n)},
      'See paragraph ' + n + ' in the passage');
  }

  /* ---------------------------------------------------------------- list -- */
  function renderList() {
    const wrap = body();
    wrap.replaceChildren();
    wrap.append(h('div', {class: 'rdintro'},
      doc.intro.en, faP(doc.intro.fa)));

    const pr = progress();
    const bar = h('div', {class: 'rdfill', style: 'width:' + pr.pct + '%'});
    wrap.append(h('div', {class: 'rdprog'},
      h('div', {class: 'rdprogtop'},
        h('b', {}, 'Your progress'),
        h('span', {}, pr.passages + ' of ' + pr.allPassages +
          ' passages finished'),
        h('span', {class: 'pct'}, pr.pct + '%')),
      h('div', {class: 'rdtrack', role: 'progressbar', 'aria-valuemin': '0',
        'aria-valuemax': '100', 'aria-valuenow': String(pr.pct),
        'aria-label': 'Reading progress'}, bar),
      h('div', {class: 'rdstats'},
        h('span', {}, h('b', {}, String(pr.sets)), ' of ' + pr.totalSets +
          ' practice sets checked'),
        h('span', {}, h('b', {}, String(pr.strategies)), ' of ' +
          doc.strategies.length + ' strategies finished'),
        h('span', {}, h('b', {}, String(doc.totals.questions)),
          ' questions'),
        h('span', {}, h('b', {}, String(doc.totals.words)),
          ' words of reading'))));

    const list = h('div', {class: 'rdlist'});
    doc.strategies.forEach((s, i) => {
      const pc = passageCounts(s);
      const done = pc.full === s.readings.length;
      list.append(h('button', {
        type: 'button', class: 'rdcard' + (done ? ' done' : ''),
        'aria-label': s.title.en + ' - ' + s.title.fa +
          (done ? ' - finished' : ''),
        onclick: () => open(s.id, 1),
      },
        h('span', {class: 'rdnum', 'aria-hidden': 'true'},
          done ? '✓' : String(i + 1)),
        h('span', {class: 'rdmain'},
          h('span', {class: 'rdname'},
            h('b', {}, s.title.en),
            h('span', {class: 'lvl'}, s.level)),
          h('span', {class: 'rdblurb'}, s.blurb.en),
          fa(s.blurb.fa, 'rdblurb'),
          h('span', {class: 'rdmeta'},
            s.minutes + ' min lesson · ' + s.readings.length + ' passages · ' +
            total(s) + ' ' + label(total(s)) + ' · ' +
            (done ? 'finished'
                  : pc.full ? pc.full + ' of ' + s.readings.length +
                              ' passages finished'
                            : pc.markedGroups ? 'in progress' : 'not started'))),
        h('span', {class: 'rdchev', 'aria-hidden': 'true'}, '›')));
    });
    wrap.append(list);
  }

  /* ------------------------------------------------------------ question -- */
  /* One blank: the sentence is split on ___ so the input sits inside it. */
  function blankItem(s, q, i, st, repaint) {
    const id = 'b' + i;
    const card = h('div', {class: 'rditem'}, h('div', {class: 'rdstem'}));
    const stem = card.firstChild;
    stem.append(h('span', {class: 'rdnum2'}, String(i + 1)));
    q.sentence.split('___').forEach((part, k) => {
      if (k) {
        // a narrow field: the gap is one word or a short phrase, and a
        // 180px box breaks the sentence into two unreadable halves
        const input = h('input', {
          type: 'text', class: 'rdblank', inputmode: 'text', size: '10',
          autocomplete: 'off', spellcheck: 'false', 'aria-label': 'Answer ' + (i + 1),
        });
        input.value = st.picks[id] || '';
        input.addEventListener('input', () => {
          st.picks[id] = input.value;
          patchCur((s) => { s.picks[id] = input.value; });
          card.classList.remove('right', 'wrong');
          input.classList.remove('right', 'wrong');
          const fb = card.querySelector('.rdfb');
          if (fb) fb.remove();
        });
        input.addEventListener('keydown', (e) => {
          if (e.key === 'Enter') { e.preventDefault(); check('blanks'); }
        });
        stem.append(input);
      }
      stem.append(document.createTextNode(part));
    });
    card.append(h('div', {class: 'rdhint'}, q.hint.en, fa(q.hint.fa)));
    return card;
  }

  function mcqItem(q, i, st) {
    const id = 'm' + i;
    const card = h('div', {class: 'rditem'});
    const stem = h('div', {class: 'rdstem'}, h('span', {class: 'rdnum2'}, String(i + 1)));
    stem.append(document.createTextNode(q.q));
    card.append(stem);
    q.options.forEach((opt, k) => {
      const btn = h('button', {
        type: 'button', class: 'rdopt' + (st.picks[id] === k ? ' on' : ''),
        'aria-pressed': st.picks[id] === k ? 'true' : 'false',
      }, h('span', {class: 'k'}, 'ABCD'[k]), h('span', {}, opt));
      btn.addEventListener('click', () => {
        patchCur((s) => { s.picks[id] = k; delete s.checked.mcq; });
        card.querySelectorAll('.rdopt').forEach((b) => {
          b.classList.remove('on', 'right', 'wrong');
          b.setAttribute('aria-pressed', 'false');
        });
        btn.classList.add('on');
        btn.setAttribute('aria-pressed', 'true');
        card.classList.remove('right', 'wrong');
        const fb = card.querySelector('.rdfb');
        if (fb) fb.remove();
        refreshScore();
      });
      card.append(btn);
    });
    card.dataset.key = id;
    return card;
  }

  function tfItem(q, i, st) {
    const id = 't' + i;
    const card = h('div', {class: 'rditem'});
    const stem = h('div', {class: 'rdstem'}, h('span', {class: 'rdnum2'}, String(i + 1)));
    stem.append(document.createTextNode(q.statement));
    const row = h('div', {class: 'rdtf', style: 'margin-top:7px'});
    [['True', true], ['False', false]].forEach(([txt, val]) => {
      const b = h('button', {
        type: 'button', class: st.picks[id] === val ? 'on' : '',
        'aria-pressed': st.picks[id] === val ? 'true' : 'false',
      }, txt);
      b.addEventListener('click', () => {
        patchCur((s) => { s.picks[id] = val; delete s.checked.truefalse; });
        row.querySelectorAll('button').forEach((x) => {
          x.classList.remove('on', 'right', 'wrong');
          x.setAttribute('aria-pressed', 'false');
        });
        b.classList.add('on');
        b.setAttribute('aria-pressed', 'true');
        card.classList.remove('right', 'wrong');
        const fb = card.querySelector('.rdfb');
        if (fb) fb.remove();
        refreshScore();
      });
      row.append(b);
    });
    card.append(stem, row);
    card.dataset.key = id;
    return card;
  }

  function essayItem(s, q, i, st) {
    const id = 'e' + i;
    const card = h('div', {class: 'rditem'});
    const stem = h('div', {class: 'rdstem'}, h('span', {class: 'rdnum2'}, String(i + 1)));
    stem.append(document.createTextNode(q.prompt.en));
    card.append(stem, h('div', {class: 'rdhint'}, fa(q.prompt.fa)));

    const area = h('textarea', {
      class: 'rdarea', rows: '4', spellcheck: 'true',
      'aria-label': 'Your answer to question ' + (i + 1),
      placeholder: 'Write here…',
    });
    area.value = st.essays[id] || '';
    const count = h('span', {class: 'rdcount'});
    const aim = q.min_words || 50;
    const tick = () => {
      const n = (area.value.trim().match(/\S+/g) || []).length;
      count.textContent = n + ' words' +
        (n >= aim ? ' ✓' : ' · aim for ' + aim + '-' + (aim + 30));
      count.classList.toggle('ok', n >= aim);
    };
    area.addEventListener('input', () => {
      patchCur((x) => { x.essays[id] = area.value; });
      tick();
    });
    tick();

    const showBtn = h('button', {type: 'button', class: 'rdsmall'}, 'Show a model answer');
    const bar = h('div', {class: 'rdessaybar'}, count, showBtn);
    const tips = h('div', {},
      h('div', {class: 'rdlabel', style: 'margin:4px 0 2px'},
        'What a good answer does', fa('جواب خوب چه می‌کند')),
      h('ul', {class: 'rdtips'}));
    q.tips.forEach((t) => {
      tips.lastChild.append(h('li', {},
        h('span', {class: 'ten'}, t.en),
        fa(t.fa, 'tfa')));
    });

    const model = h('div', {class: 'rdmodel', hidden: true},
      h('div', {class: 'lbl'}, 'Model answer'),
      h('p', {}, q.model.en), faP(q.model.fa));

    showBtn.addEventListener('click', () => {
      const open = model.hidden;
      model.hidden = !open;
      showBtn.textContent = open ? 'Hide the model answer' : 'Show a model answer';
      patchCur((x) => { x.models[id] = open; });
    });
    if (st.models[id]) {
      model.hidden = false;
      showBtn.textContent = 'Hide the model answer';
    }

    card.append(h('div', {class: 'rdessay', style: 'margin-top:8px'},
      area, bar, tips, model));
    return card;
  }

  /* -------------------------------------------------------------- checking - */
  let _current = null;
  const currentId = () => _current;

  function check(group) {
    const s = doc.strategies.find((x) => x.id === _current);
    if (!s) return;
    const q = s.readings[pi - 1].questions[group];
    const st = stateCur();
    let right = 0;

    const items = [...body().querySelectorAll('[data-group="' + group + '"] .rditem')];
    items.forEach((card, i) => {
      const item = q[i];
      card.classList.remove('right', 'wrong');
      card.querySelectorAll('.right, .wrong').forEach((x) => x.classList.remove('right', 'wrong'));
      const old = card.querySelector('.rdfb');
      if (old) old.remove();

      let ok = false;
      let fb;
      if (group === 'blanks') {
        const input = card.querySelector('.rdblank');
        const given = (st.picks['b' + i] || '').trim();
        ok = accepts(item, given);
        input.classList.add(ok ? 'right' : 'wrong');
        if (!ok) input.value = given;   // keep what they wrote; the answer is below
        fb = h('div', {class: 'rdfb'},
          h('span', {class: ok ? 'ok' : 'no'},
            ok ? '✓ Correct' : '✗ The word in the passage is "' +
                               item.answer + '"'),
          ok ? null : h('p', {}, item.hint.en), ok ? null : fa(item.hint.fa));
        const ev = evidence(item.para);
        if (ev) fb.append(ev);
      } else if (group === 'mcq') {
        const given = st.picks['m' + i];
        ok = given === item.answer;
        card.querySelectorAll('.rdopt').forEach((b, k) => {
          if (k === item.answer) b.classList.add('right');
          else if (k === given) b.classList.add('wrong');
        });
        fb = h('div', {class: 'rdfb'},
          h('span', {class: ok ? 'ok' : 'no'},
            ok ? '✓ Correct' : '✗ The answer is ' + 'ABCD'[item.answer] +
                               (given === undefined ? '' : ' — you chose ' +
                                'ABCD'[given])),
          h('p', {}, item.why.en), faP(item.why.fa));
        const ev = evidence(item.para);
        if (ev) fb.append(ev);
      } else {
        const given = st.picks['t' + i];
        ok = given === item.answer;
        card.querySelectorAll('.rdtf button').forEach((b, k) => {
          const val = k === 0;
          if (val === item.answer) b.classList.add('right');
          else if (val === given) b.classList.add('wrong');
        });
        fb = h('div', {class: 'rdfb'},
          h('span', {class: ok ? 'ok' : 'no'},
            ok ? '✓ Correct' : '✗ ' + (item.answer ? 'True' : 'False')),
          h('p', {}, item.why.en), faP(item.why.fa));
        const ev = evidence(item.para);
        if (ev) fb.append(ev);
      }
      card.classList.add(ok ? 'right' : 'wrong');
      card.append(fb);
      if (ok) right++;
    });

    patchCur((x) => { x.checked[group] = true; x.score = x.score || {}; x.score[group] = right; });

    const btn = body().querySelector('[data-check="' + group + '"]');
    if (btn) {
      btn.textContent = right + ' of ' + q.length + ' correct';
      btn.classList.remove('ghost');
    }
    refreshTabs();
    refreshScore();
  }

  function refreshScore() {
    const badge = body().querySelector('.rdscore');
    const s = doc.strategies.find((x) => x.id === _current);
    if (!badge || !s) return;
    const st = read()[skey(_current, pi)] || {};
    const sc = st.score || {};
    const done = Object.keys(sc).length;
    const right = Object.values(sc).reduce((a, b) => a + b, 0);
    const r = s.readings[pi - 1];
    const all = opening(r);
    badge.textContent = done
      ? right + ' of ' + all + ' right · ' + done + ' of 3 checked'
      : all + ' answerable questions';

    /* Once all three groups have been marked there is a result to show, and
       a next step. Until then the box stays away rather than showing zeros. */
    const box = body().querySelector('.rdresult');
    if (!box) return;
    if (done < GROUPS.length) { box.hidden = true; return; }
    const pct = Math.round(right * 100 / all);
    box.hidden = false;
    const head = pct >= 80
      ? ['Strong reading. ' + right + ' of ' + all + ' right (' + pct + '%)',
         'خواندن قوی. ' + right + ' از ' + all + ' درست (' + pct + '٪)',
         'Look at the two or three you missed, then move on to the next '
           + 'passage - this one is doing its job.',
         'به دو یا سه موردی که اشتباه شد نگاه کن و بعد سراغ متن بعدی '
           + 'برو؛ این یکی کارش را کرده.']
      : pct >= 50
      ? ['Getting there. ' + right + ' of ' + all + ' right (' + pct + '%)',
         'نزدیک شدی. ' + right + ' از ' + all + ' درست (' + pct + '٪)',
         'Re-read the paragraphs behind the questions you missed - they are '
           + 'named under each answer - then check those two groups again.',
         'پاراگراف‌های پشت سؤال‌های اشتباه را دوباره بخوان - زیر هر جواب '
           + 'نامشان آمده - بعد آن دو بخش را دوباره بررسی کن.']
      : ['Worth a second pass. ' + right + ' of ' + all + ' right (' +
         pct + '%)',
         'یک دور دیگر لازم است. ' + right + ' از ' + all + ' درست (' +
         pct + '٪)',
         'The passage is short: read it once with the strategy in mind, then '
           + 'answer again. Every wrong answer here points at a paragraph you '
           + 'can reread in thirty seconds.',
         'متن کوتاه است: یک بار با راهبرد در ذهن بخوانش و بعد دوباره جواب '
           + 'بده. هر جواب غلط به پاراگرافی اشاره می‌کند که در سی ثانیه '
           + 'می‌توانی دوباره بخوانی.'];
    box.replaceChildren(
      h('b', {}, head[0]),
      h('div', {class: 'rdrows'},
        h('span', {}, 'Fill in the blanks ' + (sc.blanks ?? 0) + '/' +
          r.counts.blanks),
        h('span', {}, 'Multiple choice ' + (sc.mcq ?? 0) + '/' +
          r.counts.mcq),
        h('span', {}, 'True or false ' + (sc.truefalse ?? 0) + '/' +
          r.counts.truefalse)),
      h('p', {class: 'rdp'}, head[2]),
      faP(head[3], 'rdp'));
  }

  /* ------------------------------------------------------------- detail -- */
  function renderStrategy(id, p) {
    const s = doc.strategies.find((x) => x.id === id);
    const wrap = body();
    wrap.replaceChildren();
    if (!s) { renderList(); return; }
    _current = id;
    pi = Math.min(Math.max(1, p || pi || 1), s.readings.length);
    const r = s.readings[pi - 1];
    const st = stateCur();
    const n = doc.strategies.indexOf(s);

    wrap.append(h('div', {class: 'rdbar'},
      h('button', {type: 'button', class: 'rdback', onclick: () => { view = 'list'; renderList(); }},
        '\u2039 All strategies'),
      h('span', {class: 'rdscore'})));

    wrap.append(h('div', {class: 'rdhero'},
      h('h4', {}, h('span', {'aria-hidden': 'true'}, s.icon), s.title.en,
        h('span', {class: 'lvl'}, s.level)),
      faP(s.title.fa, 'rdhero-fa'),
      h('div', {class: 'rdherometa'},
        s.minutes + ' min lesson \u00b7 ' + s.readings.length + ' passages \u00b7 ' +
        total(s) + ' questions')));

    /* what / why / steps */
    const sec1 = h('div', {class: 'rdsec'},
      h('div', {class: 'rdlabel'}, 'What it is', fa('چیست')),
      h('p', {class: 'rdp'}, s.what.en), faP(s.what.fa, 'rdp'));
    const sec2 = h('div', {class: 'rdsec'},
      h('div', {class: 'rdlabel'}, 'Why it works', fa('چرا جواب می‌دهد')),
      h('p', {class: 'rdp'}, s.why.en), faP(s.why.fa, 'rdp'));
    const steps = h('ol', {class: 'rdsteps'});
    s.steps.forEach((step, i) => {
      steps.append(h('li', {},
        h('span', {class: 'sn', 'aria-hidden': 'true'}, String(i + 1)),
        h('span', {class: 'stx'},
          h('span', {class: 'sen'}, step.en),
          h('span', {class: 'sfa fa', dir: 'rtl', lang: 'fa'}, step.fa))));
    });
    const sec3 = h('div', {class: 'rdsec'},
      h('div', {class: 'rdlabel'}, 'How it works', fa('چطور کار می‌کند')), steps);
    const secWhen = h('div', {class: 'rdsec'},
      h('div', {class: 'rdlabel'}, 'When to use it', fa('کجا به کار می‌آید')),
      h('p', {class: 'rdp'}, s.when.en), faP(s.when.fa, 'rdp'));

    /* worked example: the text, then the same text read by someone who
       knows the strategy - the second half is what teaches. */
    const analysis = h('ol', {class: 'rdsteps'});
    s.example.steps.forEach((line, i) => {
      analysis.append(h('li', {},
        h('span', {class: 'sn', 'aria-hidden': 'true'}, String(i + 1)),
        h('span', {class: 'stx'},
          h('span', {class: 'sen'}, line.en),
          h('span', {class: 'sfa fa', dir: 'rtl', lang: 'fa'}, line.fa))));
    });
    const secEx = h('div', {class: 'rdsec'},
      h('div', {class: 'rdlabel'}, 'Worked example', fa('نمونهٔ حل‌شده')),
      h('div', {class: 'rdexample'}, h('p', {}, s.example.text)),
      h('div', {class: 'rdlabel', style: 'margin:9px 0 5px'},
        'Step-by-step analysis', fa('تحلیل گام‌به‌گام')), analysis);

    /* one builder for the three short lists, so their bilingual rhythm is
       identical: English line, Persian line under it, never side by side. */
    const rows = (field, cls) => {
      const ul = h('ul', {class: 'rdlist2 ' + cls});
      s[field].forEach((row) => {
        ul.append(h('li', {}, h('div', {},
          h('span', {}, row.en), fa(row.fa))));
      });
      return ul;
    };
    const secMis = h('div', {class: 'rdsec'},
      h('div', {class: 'rdlabel'}, 'Common mistakes', fa('اشتباه‌های رایج')),
      rows('mistakes', 'mistakes'));
    const secTips = h('div', {class: 'rdsec'},
      h('div', {class: 'rdlabel'}, 'Practical tips', fa('نکته‌های عملی')),
      rows('tips', 'tips'));
    const secCheck = h('div', {class: 'rdsec'},
      h('div', {class: 'rdlabel'}, 'Checklist', fa('چک‌لیست')),
      rows('checklist', 'checklist'));

    wrap.append(sec1, sec2, secWhen, sec3, secEx, secMis, secTips, secCheck);

    /* the three passages. Each keeps its own answers, so switching practice
       is not the same as losing work. */
    const tabs = h('div', {class: 'rdprac', role: 'tablist',
      'aria-label': 'Practice passages'});
    s.readings.forEach((rd, k) => {
      const c = marked(id, k + 1);
      const on = k + 1 === pi;
      tabs.append(h('button', {
        type: 'button', role: 'tab',
        class: 'rdpracbtn' + (on ? ' on' : '') + (c === GROUPS.length ? ' done' : ''),
        'aria-selected': on ? 'true' : 'false',
        title: rd.title.en,
        'aria-label': 'Passage ' + (k + 1) + ': ' + rd.title.en + ' - ' +
          (c === GROUPS.length ? 'finished' : c + ' of 3 parts checked'),
        onclick: () => open(id, k + 1),
      },
        h('span', {class: 'pn'}, String(k + 1)),
        h('span', {class: 'pt'}, rd.title.en),
        h('span', {class: 'ps'}, c === GROUPS.length ? '\u2713' : c + '/3')));
    });

    const psg = h('div', {class: 'rdpassage'},
      h('div', {class: 'rdph'},
        h('b', {}, r.title.en),
        fa(r.title.fa, 'rdph-fa'),
        h('span', {class: 'pill'}, r.level + ' \u00b7 ' + r.words +
          ' words \u00b7 ' + r.minutes + ' min read')));
    if (r.note && r.note.en) {
      psg.append(h('p', {class: 'rdnote'}, r.note.en, ' ', fa(r.note.fa)));
    }
    r.paragraphs.forEach((p, i) => {
      psg.append(h('p', {class: 'rdpara', dir: 'ltr', lang: 'en',
        'data-para': String(i + 1)}, p));
    });
    const sumBtn = h('button', {type: 'button', class: 'rdsumbtn'}, 'Show the Persian summary');
    const sumBox = h('div', {class: 'rdsum', hidden: true},
      h('div', {class: 'rdlabel'}, 'In short', fa('خلاصهٔ فارسی')),
      h('p', {class: 'rdp'}, r.summary.en),
      faP(r.summary.fa, 'rdp'));
    sumBtn.addEventListener('click', () => {
      sumBox.hidden = !sumBox.hidden;
      sumBtn.textContent = sumBox.hidden ? 'Show the Persian summary' : 'Hide the summary';
    });
    psg.append(sumBtn, sumBox);
    wrap.append(h('div', {class: 'rdsec'},
      h('div', {class: 'rdlabel'}, 'Practice reading', fa('متن تمرین')),
      tabs, psg));

    /* questions: blank, choice, true/false, writing */
    const order = [
      ['blanks', 'Fill in the blank', 'جای خالی', 'a word or phrase from the text'],
      ['mcq', 'Multiple choice', 'چندگزینه‌ای', 'one right answer each'],
      ['truefalse', 'True or false', 'درست یا غلط', 'say if it follows from the text'],
      ['essay', 'Write about it', 'نوشتن', 'checked by you, against a model'],
    ];
    order.forEach(([group, title, titleFa, sub]) => {
      const sec = h('div', {class: 'rdsec', 'data-group': group});
      const head = h('div', {class: 'rdqhead'},
        h('b', {}, title), fa(titleFa),
        h('span', {class: 'n'}, r.questions[group].length + ' \u00b7 ' + sub));
      sec.append(head);
      const list = h('div', {class: 'rdq'});
      r.questions[group].forEach((item, i) => {
        let card;
        if (group === 'blanks') card = blankItem(r, item, i, st);
        else if (group === 'mcq') card = mcqItem(item, i, st);
        else if (group === 'truefalse') card = tfItem(item, i, st);
        else card = essayItem(r, item, i, st);
        list.append(card);
      });
      sec.append(list);

      if (group !== 'essay') {
        const btn = h('button', {
          type: 'button', class: 'rdgo ghost', 'data-check': group,
          onclick: () => check(group),
        }, 'Check these answers');
        sec.append(h('div', {style: 'margin-top:9px'}, btn));
        if (st.checked && st.checked[group]) {
          /* repaint in the checked state without re-running the marking twice */
          setTimeout(() => check(group), 0);
        }
      }
      wrap.append(sec);
    });

    const lastPractice = pi === s.readings.length;
    wrap.append(h('div', {class: 'rdresult', hidden: true}));
    wrap.append(h('div', {class: 'rdfoot'},
      h('button', {type: 'button', class: 'rdgo ghost', onclick: () => {
        patch(id, pi, (x) => { x.picks = {}; x.checked = {}; x.essays = {}; x.models = {}; x.score = {}; });
        renderStrategy(id, pi);
      }}, 'Reset this passage'),
      !lastPractice
        ? h('button', {type: 'button', class: 'rdgo', onclick: () => open(id, pi + 1)},
            'Next passage \u203a')
        : n < doc.strategies.length - 1
          ? h('button', {type: 'button', class: 'rdgo', onclick: () => open(doc.strategies[n + 1].id, 1)},
              'Next strategy: ' + doc.strategies[n + 1].title.en + ' \u203a')
          : h('button', {type: 'button', class: 'rdgo', onclick: () => { view = 'list'; renderList(); }},
              'Back to the list')));

    refreshScore();
  }

  function open(id, p) {
    view = id;
    pi = p || 1;
    renderStrategy(id, pi);
    const panel = document.getElementById('rdpanel');
    if (panel) panel.scrollTop = 0;
  }

  /* --------------------------------------------------------------- public -- */
  async function load() {
    if (doc) return doc;
    if (!pending) {
      pending = loadJSON('reading').then((d) => {
        doc = d;
        return d;
      });
    }
    return pending;
  }

  async function mount() {
    const wrap = body();
    if (!wrap || wrap.dataset.ready) { if (doc) view === 'list' ? renderList() : renderStrategy(view); return; }
    wrap.replaceChildren(h('div', {class: 'rdintro'}, 'Loading the strategies…'));
    try {
      await load();
      wrap.dataset.ready = '1';
      view === 'list' ? renderList() : renderStrategy(view);
    } catch (e) {
      console.error('reading:', e);
      wrap.replaceChildren(h('div', {class: 'rderr'},
        'The reading strategies could not be read. ',
        fa('راهبردهای خواندن خوانده نشد.')));
    }
  }

  return {mount, load, open, renderList};
})();

/* ==========================================================================
   Mini stories: one graded English story at a time, the Persian under every
   sentence it belongs to, the words and structures worth keeping, and the
   questions. The panel is content plus marking; nothing here talks to the bot.
   ==========================================================================*/
const Stories = (() => {
  const body = () => document.getElementById('stbody');
  const KEY = 'fluentify.stories.v1';
  const GROUPS = ['mcq', 'truefalse', 'blanks'];
  const LETTERS = ['A', 'B', 'C', 'D'];

  const h = (tag, attrs, ...kids) => {
    const node = document.createElement(tag);
    Object.entries(attrs || {}).forEach(([k, v]) => {
      if (v === null || v === undefined || v === false) return;
      if (k === 'class') node.className = v;
      else if (k === 'html') node.innerHTML = v;
      else if (k.startsWith('on')) node.addEventListener(k.slice(2), v);
      else node.setAttribute(k, v === true ? '' : v);
    });
    kids.flat().forEach((kid) => {
      if (kid === null || kid === undefined || kid === false) return;
      node.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
    });
    return node;
  };
  const fa = (text, cls) =>
    h('span', {class: (cls || '') + ' fa', dir: 'rtl', lang: 'fa'}, text);
  const faP = (text, cls) =>
    h('p', {class: (cls || '') + ' fa', dir: 'rtl', lang: 'fa'}, text);

  let doc = null, pending = null, view = 'list', filter = 'all', openId = null;
  let showFa = true, query = '';

  /* Reading preferences outlive the panel, and the story: someone who turns
     the Persian off to test themselves wants it off in the next story too. */
  const PREFS = 'fluentify.story.prefs';
  const readPrefs = () => {
    try { return JSON.parse(localStorage.getItem(PREFS) || '{}'); }
    catch (e) { return {}; }
  };
  const savePrefs = () => {
    try { localStorage.setItem(PREFS, JSON.stringify({fa: showFa, zoom})); }
    catch (e) { /* full or private */ }
  };
  const firstPrefs = readPrefs();
  showFa = firstPrefs.fa !== false;
  let zoom = [0.9, 1, 1.15, 1.3].includes(firstPrefs.zoom) ? firstPrefs.zoom : 1;
  const ZOOMS = [0.9, 1, 1.15, 1.3];

  const read = () => {
    try { return JSON.parse(localStorage.getItem(KEY) || '{}'); }
    catch (e) { return {}; }
  };
  const write = (all) => {
    try { localStorage.setItem(KEY, JSON.stringify(all)); } catch (e) { /* full or private */ }
  };
  const st = (id) => read()[id] || {};
  const patch = (id, fn) => {
    const all = read();
    const one = all[id] || (all[id] = {});
    fn(one);
    write(all);
  };

  /* How many of the three markable sets have been checked for a story. */
  const marked = (id) => {
    const one = st(id);
    return GROUPS.filter((g) => one.checked && one.checked[g]).length;
  };
  const rightOf = (id) =>
    Object.values(st(id).score || {}).reduce((a, b) => a + b, 0);

  const tidy = (x) => String(x).toLowerCase()
    .replace(/[.,!?;:'"\u00ab\u00bb()\u2019]/g, ' ')
    .replace(/\s+/g, ' ').trim();

  function levelOf(id) {
    const lv = (doc.levels || []).find((l) => l.id === id);
    return lv ? lv.name : {en: id, fa: id};
  }

  /* --------------------------------------------------------------- the list - */
  function renderList() {
    const wrap = body();
    wrap.replaceChildren();
    wrap.classList.remove('hidefa');
    wrap.style.removeProperty('--stzoom');
    view = 'list';

    const total = doc.stories.length;
    const finished = doc.stories.filter((s) => marked(s.id) === GROUPS.length).length;
    const started = doc.stories.filter((s) => marked(s.id) > 0).length;

    wrap.append(h('div', {class: 'rdintro'},
      h('p', {}, 'An English story at your level, the Persian beside every '
        + 'sentence, then the words, the grammar and the questions that make '
        + 'it stick.'),
      faP('یک داستان انگلیسی در سطح خودت، فارسی زیر هر جمله، و بعد واژه‌ها، '
        + 'گرامر و پرسش‌ها.')));

    /* how far the shelf has got - finished is the number that matters */
    wrap.append(h('div', {class: 'stprog'},
      h('div', {class: 'stprogbar'},
        h('i', {style: 'width:' + Math.round(finished * 100 / total) + '%'})),
      h('div', {class: 'stprogline'},
        h('b', {}, finished + ' of ' + total + ' finished'),
        h('span', {}, finished === total ? 'the whole shelf'
          : started > finished ? started - finished + ' started'
          : started ? started + ' started' : 'nothing started yet'))));

    const search = h('input', {
      type: 'search', class: 'stsearch', value: query,
      placeholder: 'Search a title or a subject',
      'aria-label': 'Search the stories',
    });
    search.addEventListener('input', () => { query = search.value.trim(); paint(); });
    wrap.append(h('div', {class: 'stsearchrow'}, search));

    const levels = h('div', {class: 'stlevels', role: 'tablist',
      'aria-label': 'Story level'});
    const rows = [['all', 'All ' + total]];
    doc.levels.forEach((lv) => {
      const n = doc.stories.filter((s) => s.level === lv.id).length;
      if (n) rows.push([lv.id, lv.name.en + ' · ' + n]);
    });
    rows.forEach(([id, label]) => {
      const b = h('button', {
        type: 'button', role: 'tab', class: 'stlv' + (filter === id ? ' on' : ''),
        'aria-selected': filter === id ? 'true' : 'false',
        onclick: () => {
          filter = id;
          [...levels.children].forEach((x) => {
            x.classList.toggle('on', x === b);
            x.setAttribute('aria-selected', x === b ? 'true' : 'false');
          });
          paint();
        },
      }, label);
      levels.append(b);
    });
    wrap.append(levels);

    const note = h('p', {class: 'stcount'});
    const cards = h('div', {class: 'stcards'});
    wrap.append(note, cards);

    const needle = () => tidy(query);
    const matches = (s) => {
      if (filter !== 'all' && s.level !== filter) return false;
      const q = needle();
      if (!q) return true;
      return tidy([s.title.en, s.title.fa, s.blurb.en, s.blurb.fa, s.id].join(' '))
        .includes(q);
    };

    function paint() {
      const shown = doc.stories.filter(matches);
      cards.replaceChildren();
      shown.forEach((s, i) => {
        const c = marked(s.id);
        const done = c === GROUPS.length;
        const checked = st(s.id).checked || {};
        const dots = h('span', {class: 'stdots', 'aria-hidden': 'true'});
        GROUPS.forEach((g) => dots.append(h('i', {class: checked[g] ? 'on' : ''})));
        cards.append(h('button', {
          type: 'button', class: 'stcard lv-' + s.level, onclick: () => open(s.id),
        },
          h('span', {class: 'stnum', 'aria-hidden': 'true'},
            done ? '✓' : String(i + 1)),
          h('span', {class: 'stmain'},
            h('span', {class: 'stname'}, s.title.en,
              h('span', {class: 'lvl'}, levelOf(s.level).en),
              fa(s.title.fa, 'stbadge')),
            h('span', {class: 'stblurb'}, s.blurb.en),
            h('span', {class: 'stmeta'},
              s.words + ' words · ' + s.minutes + ' min · ' +
              s.sentences + ' sentences · ', dots,
              done ? ' finished' : c ? ' ' + c + ' of 3 sets checked'
                                     : ' not started')),
          h('span', {class: 'rdchev', 'aria-hidden': 'true'}, '›')));
      });
      if (!shown.length) {
        cards.append(h('div', {class: 'stempty'},
          h('p', {}, 'No story has that word.'),
          faP('داستانی با این واژه پیدا نشد.')));
      }
      note.textContent = shown.length === total ? ''
        : shown.length + (shown.length === 1 ? ' story' : ' stories') +
          ' of ' + total;
      note.hidden = !note.textContent;
    }
    paint();

    const credit = h('p', {class: 'stcu'}, doc.credit.en + ' ');
    credit.append(h('a', {href: doc.credit.url, target: '_blank',
      rel: 'noopener'}, 'Source'));
    wrap.append(credit);
  }

  /* ------------------------------------------------------------- one story -- */
  function renderStory(id) {
    const s = doc.stories.find((x) => x.id === id);
    const wrap = body();
    wrap.replaceChildren();
    if (!s) { renderList(); return; }
    view = id;
    openId = id;
    wrap.classList.toggle('hidefa', !showFa);
    const one = st(id);

    const back = h('button', {type: 'button', class: 'rdback',
      onclick: () => { view = 'list'; renderList(); }}, '‹ All stories');

    const applyZoom = () => wrap.style.setProperty('--stzoom', String(zoom));

    /* text size: four steps, kept between stories and across visits */
    const sizeStep = (label, delta, title) => h('button', {
      type: 'button', class: 'stsize', title, 'aria-label': title,
      onclick: () => {
        const at = ZOOMS.indexOf(zoom);
        const to = Math.min(ZOOMS.length - 1, Math.max(0, at + delta));
        if (to === at) return;
        zoom = ZOOMS[to];
        applyZoom();
        savePrefs();
        sizeA.disabled = to === 0;
        sizeB.disabled = to === ZOOMS.length - 1;
      },
    }, label);
    const sizeA = sizeStep('A−', -1, 'Smaller text');
    const sizeB = sizeStep('A+', 1, 'Larger text');
    sizeA.disabled = zoom === ZOOMS[0];
    sizeB.disabled = zoom === ZOOMS[ZOOMS.length - 1];

    const toggle = h('button', {
      type: 'button', class: 'sttoggle',
      onclick: () => {
        showFa = !showFa;
        wrap.classList.toggle('hidefa', !showFa);
        toggle.textContent = showFa ? 'Hide the Persian' : 'Show the Persian';
        savePrefs();
      },
    }, showFa ? 'Hide the Persian' : 'Show the Persian');

    wrap.append(h('div', {class: 'stbar'}, back, h('span', {class: 'rdscore'})));
    wrap.append(h('div', {class: 'sttools'},
      h('span', {class: 'stsizegrp', role: 'group', 'aria-label': 'Text size'},
        sizeA, sizeB),
      toggle));

    wrap.append(h('div', {class: 'rdhero'},
      h('h4', {}, s.title.en, h('span', {class: 'lvl'}, levelOf(s.level).en)),
      faP(s.title.fa, 'rdhero-fa'),
      h('div', {class: 'rdherometa'},
        s.words + ' words · ' + s.minutes + ' min read · ' +
        s.chapters.length + ' chapter' + (s.chapters.length === 1 ? '' : 's') +
        ' · ' + s.counts.all + ' questions')));

    /* the story itself, sentence by sentence, with its Persian underneath */
    const story = h('div', {});
    s.chapters.forEach((ch) => {
      story.append(h('div', {class: 'stch'},
        h('span', {}, ch.title.en), fa(ch.title.fa)));
      ch.pairs.forEach((p, i) => {
        story.append(h('div', {class: 'sts'},
          h('span', {class: 'n', 'aria-hidden': 'true'}, String(i + 1)),
          h('span', {class: 'tx'},
            h('span', {class: 'en', dir: 'ltr', lang: 'en'}, p.en),
            fa(p.fa))));
      });
    });
    wrap.append(h('div', {class: 'rdsec'},
      h('div', {class: 'rdlabel'}, 'The story', fa('داستان')),
      story));
    applyZoom();

    /* vocabulary: the word, what it means, and the line it came from */
    const vocab = h('div', {});
    s.vocab.forEach((v) => {
      vocab.append(h('div', {class: 'stv'},
        h('div', {class: 'w'}, v.word, ' ', h('i', {}, v.pos)),
        h('div', {class: 'm'}, v.meaning.en, ' \u00b7 ', fa(v.meaning.fa)),
        h('div', {class: 'ex'}, v.example),
        h('div', {class: 'ex fa', dir: 'rtl', lang: 'fa'}, v.exampleFa)));
    });
    wrap.append(h('div', {class: 'rdsec'},
      h('div', {class: 'rdlabel'}, 'Important words',
        fa('\u0648\u0627\u0698\u06af\u0627\u0646 \u0645\u0647\u0645')), vocab));

    const exprs = h('div', {});
    s.expressions.forEach((e) => {
      exprs.append(h('div', {class: 'stv'},
        h('div', {class: 'w'}, e.phrase),
        h('div', {class: 'm'}, e.meaning.en, ' \u00b7 ', fa(e.meaning.fa)),
        h('div', {class: 'ex'}, e.example),
        h('div', {class: 'ex fa', dir: 'rtl', lang: 'fa'}, e.exampleFa)));
    });
    wrap.append(h('div', {class: 'rdsec'},
      h('div', {class: 'rdlabel'}, 'Useful expressions',
        fa('\u0639\u0628\u0627\u0631\u062a\u200c\u0647\u0627\u06cc \u06a9\u0627\u0631\u0628\u0631\u062f\u06cc')), exprs));

    const gram = h('div', {});
    s.grammar.forEach((g) => {
      gram.append(h('div', {class: 'stv'},
        h('div', {class: 'w'}, g.name.en, ' ', fa(g.name.fa)),
        h('div', {class: 'ex'}, g.example),
        h('div', {class: 'm'}, g.note.en),
        h('div', {class: 'm fa', dir: 'rtl', lang: 'fa'}, g.note.fa)));
    });
    wrap.append(h('div', {class: 'rdsec'},
      h('div', {class: 'rdlabel'}, 'Grammar in the story',
        fa('\u06af\u0631\u0627\u0645\u0631 \u062f\u0627\u0633\u062a\u0627\u0646')), gram));

    /* the questions, in the order a class would ask them */
    const order = [
      ['mcq', 'Multiple choice', '\u0686\u0646\u062f\u06af\u0632\u06cc\u0646\u0647\u200c\u0627\u06cc',
       'one right answer each'],
      ['truefalse', 'True or false', '\u062f\u0631\u0633\u062a \u06cc\u0627 \u063a\u0644\u0637',
       'does the story say so?'],
      ['blanks', 'Fill in the blank', '\u062c\u0627\u06cc \u062e\u0627\u0644\u06cc',
       'a word from the story'],
      ['open', 'Think and write', '\u0641\u06a9\u0631 \u06a9\u0646 \u0648 \u0628\u0646\u0648\u06cc\u0633',
       'compare with a model answer'],
    ];

    order.forEach(([group, title, titleFa, sub]) => {
      const sec = h('div', {class: 'rdsec', 'data-g': group});
      sec.append(h('div', {class: 'rdqhead'},
        h('b', {}, title), fa(titleFa),
        h('span', {class: 'n'}, (group === 'open' ? 2 : s.questions[group].length) +
          ' \u00b7 ' + sub)));
      const list = h('div', {class: 'rdq'});
      s.questions[group].forEach((item, i) => {
        list.append(itemCard(s, item, group, i, one));
      });
      sec.append(list);
      if (GROUP_SCORE.includes(group)) {
        const btn = h('button', {type: 'button', class: 'rdgo ghost',
          'data-check': group, onclick: () => check(group)},
          'Check these answers');
        sec.append(h('div', {style: 'margin-top:9px'}, btn));
      }
      wrap.append(sec);
    });

    wrap.append(h('div', {class: 'rdresult', hidden: true}));
    const at = doc.stories.indexOf(s);
    const prev = doc.stories[at - 1];
    const next = doc.stories[at + 1];
    const jump = (other) => {
      view = other.id;
      renderStory(other.id);
      const panel = document.getElementById('stpanel');
      if (panel) panel.scrollTop = 0;
    };

    wrap.append(h('div', {class: 'rdfoot'},
      h('button', {type: 'button', class: 'rdgo ghost', onclick: () => {
        patch(id, (x) => {
          x.picks = {}; x.checked = {}; x.score = {}; x.open = {};
        });
        renderStory(id);
      }}, 'Reset this story'),
      h('button', {type: 'button', class: 'rdgo', onclick: () => { view = 'list'; renderList(); }},
        'All stories ›')));

    wrap.append(h('div', {class: 'stnext'},
      prev ? h('button', {type: 'button', class: 'stjump',
        onclick: () => jump(prev)},
        h('span', {class: 'k'}, '‹ Previous'), h('b', {}, prev.title.en))
        : h('span', {}),
      next ? h('button', {type: 'button', class: 'stjump next',
        onclick: () => jump(next)},
        h('span', {class: 'k'}, 'Next ›'), h('b', {}, next.title.en))
        : h('span', {})));

    refreshHead();
    if (one.checked) {
      GROUPS.forEach((g) => { if (one.checked[g]) setTimeout(() => check(g), 0); });
    }
  }

  const GROUP_SCORE = ['mcq', 'truefalse', 'blanks'];

  /* One question card. Choices and true/false mark themselves as you go; the
     blank waits for the check button; the open question keeps what you wrote. */
  function itemCard(s, item, group, i, one) {
    const picks = one.picks || {};
    if (group === 'mcq') {
      const opts = h('div', {style: 'margin-top:6px'});
      item.options.forEach((opt, k) => {
        const b = h('button', {
          type: 'button',
          class: 'rdopt' + (picks['m' + i] === k ? ' on' : ''),
          onclick: () => {
            opts.querySelectorAll('.rdopt').forEach((x) => x.classList.remove('on'));
            b.classList.add('on');
            patch(s.id, (y) => {
              y.picks = y.picks || {};
              y.picks['m' + i] = k;
              if (y.checked) delete y.checked.mcq;
            });
            refreshHead();
          },
        }, h('span', {class: 'k'}, LETTERS[k]), ' ' + opt);
        opts.append(b);
      });
      return h('div', {class: 'rditem'},
        h('div', {class: 'rdstem'}, item.q.en),
        faP(item.q.fa, 'rdstem fa'), opts);
    }

    if (group === 'truefalse') {
      const row = h('div', {class: 'rdtf', style: 'margin-top:6px'});
      [['True', true], ['False', false]].forEach(([label, val]) => {
        const b = h('button', {
          type: 'button',
          class: 'rdopt' + (picks['t' + i] === val ? ' on' : ''),
          onclick: () => {
            row.querySelectorAll('button').forEach((x) => x.classList.remove('on'));
            b.classList.add('on');
            patch(s.id, (y) => {
              y.picks = y.picks || {};
              y.picks['t' + i] = val;
              if (y.checked) delete y.checked.truefalse;
            });
            refreshHead();
          },
        }, label);
        row.append(b);
      });
      return h('div', {class: 'rditem'},
        h('div', {class: 'rdstem'}, item.q.en),
        faP(item.q.fa, 'rdstem fa'), row);
    }

    if (group === 'blanks') {
      const input = h('input', {
        type: 'text', class: 'rdblank', autocomplete: 'off',
        'aria-label': 'Missing word', value: picks['b' + i] || '',
      });
      input.addEventListener('input', () => {
        patch(s.id, (y) => {
          y.picks = y.picks || {};
          y.picks['b' + i] = input.value;
          if (y.checked) delete y.checked.blanks;
        });
        refreshHead();
      });
      return h('div', {class: 'rditem'},
        h('div', {class: 'rdstem'}, item.sentence.split('___')[0], input,
          item.sentence.split('___')[1] || ''),
        h('p', {class: 'rdnote'}, item.hint.en, ' ', fa(item.hint.fa)));
    }

    /* open-ended: a paragraph of your own, then the model to compare with */
    const area = h('textarea', {class: 'rdarea', rows: '4',
      placeholder: 'Write two or three sentences.',
      'aria-label': 'Your answer'});
    area.value = (one.open || {})['o' + i] || '';
    area.addEventListener('input', () => {
      patch(s.id, (y) => {
        y.open = y.open || {};
        y.open['o' + i] = area.value;
      });
    });
    const model = h('div', {class: 'rdmodel', hidden: true},
      h('div', {class: 'rdlabel'}, 'A model answer',
        fa('\u067e\u0627\u0633\u062e \u0646\u0645\u0648\u0646\u0647')),
      h('p', {}, item.model.en), faP(item.model.fa));
    const btn = h('button', {type: 'button', class: 'rdsumbtn',
      style: 'margin-top:6px',
      onclick: () => {
        model.hidden = !model.hidden;
        btn.textContent = model.hidden ? 'Show a model answer' : 'Hide the model answer';
      }}, 'Show a model answer');
    return h('div', {class: 'rditem'},
      h('div', {class: 'rdstem'}, item.q.en),
      faP(item.q.fa, 'rdstem fa'), area, btn, model,
      h('p', {class: 'rdnote'}, item.tip.en, ' ', fa(item.tip.fa)));
  }

  /* ---------------------------------------------------------------- marking - */
  function check(group) {
    const s = doc.stories.find((x) => x.id === openId);
    if (!s) return;
    const sec = body().querySelector('[data-g="' + group + '"]');
    if (!sec) return;
    const items = [...sec.querySelectorAll('.rditem')];
    const picks = st(s.id).picks || {};
    let right = 0;

    items.forEach((card, i) => {
      const item = s.questions[group][i];
      card.classList.remove('right', 'wrong');
      card.querySelectorAll('.right, .wrong').forEach((x) =>
        x.classList.remove('right', 'wrong'));
      const old = card.querySelector('.rdfb');
      if (old) old.remove();
      let ok = false;
      let fb;

      if (group === 'mcq') {
        const given = picks['m' + i];
        ok = given === item.answer;
        card.querySelectorAll('.rdopt').forEach((b, k) => {
          if (k === item.answer) b.classList.add('right');
          else if (k === given) b.classList.add('wrong');
        });
        fb = h('div', {class: 'rdfb'},
          h('span', {class: ok ? 'ok' : 'no'},
            ok ? '\u2713 Correct' : '\u2717 The answer is ' + LETTERS[item.answer] +
              (given === undefined ? '' : ' \u2014 you chose ' + LETTERS[given])),
          h('p', {}, item.why.en), faP(item.why.fa));
      } else if (group === 'truefalse') {
        const given = picks['t' + i];
        ok = given === item.answer;
        card.querySelectorAll('.rdtf button').forEach((b, k) => {
          const val = k === 0;
          if (val === item.answer) b.classList.add('right');
          else if (val === given) b.classList.add('wrong');
        });
        fb = h('div', {class: 'rdfb'},
          h('span', {class: ok ? 'ok' : 'no'},
            ok ? '\u2713 Correct' : '\u2717 ' + (item.answer ? 'True' : 'False')),
          h('p', {}, item.why.en), faP(item.why.fa));
      } else {
        const input = card.querySelector('.rdblank');
        const given = (picks['b' + i] || '').trim();
        ok = tidy(given) === tidy(item.answer);
        input.classList.add(ok ? 'right' : 'wrong');
        fb = h('div', {class: 'rdfb'},
          h('span', {class: ok ? 'ok' : 'no'},
            ok ? '\u2713 Correct' : '\u2717 The word in the story is "' +
              item.answer + '"'),
          h('p', {}, item.hint.en), faP(item.hint.fa));
      }

      card.classList.add(ok ? 'right' : 'wrong');
      card.append(fb);
      if (ok) right++;
    });

    patch(s.id, (y) => {
      y.checked = y.checked || {};
      y.checked[group] = true;
      y.score = y.score || {};
      y.score[group] = right;
    });

    const btn = sec.querySelector('[data-check="' + group + '"]');
    if (btn) {
      btn.textContent = right + ' of ' + items.length + ' correct';
      btn.classList.remove('ghost');
    }
    refreshHead();
  }

  /* Badge and result box, recomputed from storage so they never disagree with
     what is marked on the page. */
  function refreshHead() {
    const s = doc.stories.find((x) => x.id === openId);
    const badge = body() && body().querySelector('.rdscore');
    if (!s || !badge) return;
    const one = st(s.id);
    const sets = GROUPS.filter((g) => one.checked && one.checked[g]).length;
    const total = s.counts.mcq + s.counts.truefalse + s.counts.blanks;
    const right = rightOf(s.id);
    badge.textContent = sets
      ? right + ' of ' + total + ' right \u00b7 ' + sets + ' of 3 checked'
      : total + ' markable questions';

    const box = body().querySelector('.rdresult');
    if (!box) return;
    if (sets < GROUPS.length) { box.hidden = true; return; }
    box.hidden = false;
    const pct = Math.round(right * 100 / total);
    const head = pct >= 80
      ? ['Strong reading. ' + right + ' of ' + total + ' right (' + pct + '%)',
         '\u062e\u0648\u0627\u0646\u062f\u0646 \u0642\u0648\u06cc. ' + right +
         ' \u0627\u0632 ' + total + ' \u062f\u0631\u0633\u062a (' + pct + '\u066a)',
         'Reread only the sentences behind the ones you missed, then take the '
           + 'next story. You are reading, not guessing.',
         '\u0641\u0642\u0637 \u062c\u0645\u0644\u0647\u200c\u0647\u0627\u06cc\u06cc \u0631\u0627 '
           + '\u06a9\u0647 \u062c\u0648\u0627\u0628\u0634\u0627\u0646 \u0631\u0627 '
           + '\u0627\u0634\u062a\u0628\u0627\u0647 \u0632\u062f\u06cc '
           + '\u062f\u0648\u0628\u0627\u0631\u0647 \u0628\u062e\u0648\u0627\u0646\u060c '
           + '\u0628\u0639\u062f \u062f\u0627\u0633\u062a\u0627\u0646 \u0628\u0639\u062f\u06cc.']
      : pct >= 50
      ? ['Getting there. ' + right + ' of ' + total + ' right (' + pct + '%)',
         '\u0646\u0632\u062f\u06cc\u06a9 \u0634\u062f\u06cc. ' + right + ' \u0627\u0632 ' +
         total + ' \u062f\u0631\u0633\u062a (' + pct + '\u066a)',
         'Read the story once more with the Persian hidden. The lines you '
           + 'missed are the ones your eye skipped.',
         '\u062f\u0627\u0633\u062a\u0627\u0646 \u0631\u0627 \u06cc\u06a9 '
           + '\u0628\u0627\u0631 \u062f\u06cc\u06af\u0631 \u0628\u0627 '
           + '\u0641\u0627\u0631\u0633\u06cc \u067e\u0646\u0647\u0627\u0646 '
           + '\u0628\u062e\u0648\u0627\u0646\u061b \u062c\u0645\u0644\u0647\u200c\u0647\u0627\u06cc\u06cc '
           + '\u06a9\u0647 \u0627\u0634\u062a\u0628\u0627\u0647 \u0634\u062f\u06cc '
           + '\u0647\u0645\u0627\u0646\u200c\u0647\u0627\u06cc\u06cc \u0647\u0633\u062a\u0646\u062f '
           + '\u06a9\u0647 \u0686\u0634\u0645\u062a \u0627\u0632 \u0622\u0646\u200c\u0647\u0627 '
           + '\u067e\u0631\u06cc\u062f.']
      : ['A second pass will pay. ' + right + ' of ' + total + ' right (' +
         pct + '%)', '\u06cc\u06a9 \u062f\u0648\u0631 \u062f\u06cc\u06af\u0631 '
         + '\u0644\u0627\u0632\u0645 \u0627\u0633\u062a. ' + right + ' \u0627\u0632 ' +
         total + ' \u062f\u0631\u0633\u062a (' + pct + '\u066a)',
         'Show the Persian, read the English sentence by sentence until each '
           + 'one makes you nod, then answer again. The story is short.',
         '\u0641\u0627\u0631\u0633\u06cc \u0631\u0627 \u0646\u0634\u0627\u0646 '
           + '\u0628\u062f\u0647 \u0648 \u062c\u0645\u0644\u0647 \u0628\u0647 '
           + '\u062c\u0645\u0644\u0647 \u0628\u062e\u0648\u0627\u0646 \u062a\u0627 '
           + '\u0647\u0631 \u062c\u0645\u0644\u0647 \u0631\u0627 \u0628\u0641\u0647\u0645\u06cc\u060c '
           + '\u0628\u0639\u062f \u062f\u0648\u0628\u0627\u0631\u0647 '
           + '\u062c\u0648\u0627\u0628 \u0628\u062f\u0647.'];
    box.replaceChildren(
      h('b', {}, head[0]),
      h('div', {class: 'rdrows'},
        h('span', {}, 'Multiple choice ' + (one.score.mcq ?? 0) + '/' + s.counts.mcq),
        h('span', {}, 'True or false ' + (one.score.truefalse ?? 0) + '/' + s.counts.truefalse),
        h('span', {}, 'Fill in the blanks ' + (one.score.blanks ?? 0) + '/' + s.counts.blanks)),
      h('p', {class: 'rdp'}, head[2]),
      faP(head[3], 'rdp'));
  }

  function open(id) {
    renderStory(id);
    const panel = document.getElementById('stpanel');
    if (panel) panel.scrollTop = 0;
  }

  async function load() {
    if (doc) return doc;
    if (!pending) {
      pending = loadJSON('stories').then((d) => {
        doc = d;
        return d;
      });
    }
    return pending;
  }

  async function mount() {
    const wrap = body();
    if (!wrap) return;
    if (wrap.dataset.ready) {
      if (doc) { view === 'list' ? renderList() : renderStory(view); }
      return;
    }
    wrap.replaceChildren(h('div', {class: 'rdintro'}, 'Loading the stories\u2026'));
    try {
      await load();
      wrap.dataset.ready = '1';
      view === 'list' ? renderList() : renderStory(view);
    } catch (e) {
      console.error('stories:', e);
      wrap.replaceChildren(h('div', {class: 'rderr'},
        'The stories could not be read. ',
        fa('\u062f\u0627\u0633\u062a\u0627\u0646\u200c\u0647\u0627 \u062e\u0648\u0627\u0646\u062f\u0647 \u0646\u0634\u062f.')));
    }
  }

  /* Escape is the one key a panel reader expects to work. */
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape' || view === 'list') return;
    const panel = document.getElementById('stpanel');
    if (!panel || !panel.classList.contains('open')) return;
    view = 'list';
    renderList();
  });

  /* The level check sends a reader to the shelf at their band. This sets the
     same filter the chips set, then lets mount() draw the list, so the chips
     and the list cannot disagree about what is being shown. */
  function openLevel(level) {
    filter = level || 'all';
    view = 'list';
    openId = null;
    if (doc) renderList();
  }

  return {mount, load, openLevel};
})();

/* ==========================================================================
   Level check: a CEFR placement test that runs in the page.

   The bank (level_test.json) is banded A1..C1. A band is *passed* at two
   thirds of its items; a skill's level is the highest band passed after every
   band below it, and the overall level is the median of the five skills. That
   is why one bad section cannot sink a strong reader, and one lucky section
   cannot lift a weak one.

   Writing and speaking cannot be marked offline, so they are rated by the
   learner against a rubric - and every screen that shows a level says which
   skills were machine-marked and which were not. A result is kept for
   retakeDays and then the check opens again; the last twelve results stay in
   the history so the trend is visible.
   ==========================================================================*/
/* ==========================================================================
   Level assessment: six skills, five of them measured, none of them guessed
   from a percentage.

   The attempt is a staircase, not a quiz. Each skill is asked three questions
   at a time; after a block the band moves up when two of three are right and
   down when they are not. Three blocks, so a skill is answered nine times at
   most and never two questions in a row at a band that has already been
   judged. One bad answer cannot move the estimate: the block decides.

   A skill's level is the highest band cleared after every band below it, with
   a margin that comes from the actual variance of the answers, not from a
   label. Writing and speaking are practice - offered, read against a rubric,
   reported as "not assessed" - because a self-rating is not a proficiency
   score and averaging one in would be a lie with a number attached.
   ==========================================================================*/
const Level = (() => {
  const body = () => document.getElementById('lvlbody');
  const KEY = {
    result: 'fluentify.level.v2.result',
    history: 'fluentify.level.v2.history',
    attempt: 'fluentify.level.v2.attempt',
    items: 'fluentify.level.items',
  };
  const BANDS = ['A1', 'A2', 'B1', 'B2', 'C1'];
  /* Below the first tested band is a level of its own, not an absence. The
     paper cannot measure under A1 - its first part is A1 - so a finished paper
     that stays under the A1 cutoff is reported as Pre-A1, and the learning path
     opens on Pre-A1's own card rather than on A1. */
  const PRE = 'Pre-A1';
  const DAY = 86400000;
  const LETTERS = ['A', 'B', 'C', 'D'];

  let doc = null, pending = null, state = null;
  let view = 'intro', warned = false, ticker = null, tickLeft = 0;
  let saveTimer = null, healed = false;

  const esc = (s) => String(s).replace(/[&<>"]/g,
    (c) => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));

  /* A count in running copy is a word, not a digit: "five skills measured"
     reads as a sentence. The number itself always comes from the blueprint, so
     the button, the chip and the report can never disagree about how many
     skills this paper marks. */
  const NUM_WORDS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six',
    'seven', 'eight', 'nine', 'ten'];
  const numWord = (n) => NUM_WORDS[n] || String(n);
  const read = (k, d) => {
    try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; }
    catch (e) { return d; }
  };
  const write = (k, v) => {
    try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* full */ }
  };
  const faLine = (text, cls) =>
    `<p class="lv-fa${cls ? ' ' + cls : ''}" dir="rtl" lang="fa">${esc(text)}</p>`;

  const isPre = (band) => !band || band === PRE || band === 'PRE';
  const bandLabel = (band) => (isPre(band) ? PRE : band);
  const bandIndex = (band) => (isPre(band) ? -1 : BANDS.indexOf(band));
  const bandKey = (band) => (isPre(band) ? 'PRE' : band);
  const bandName = (band) => {
    const b = doc.bands.find((x) => x.id === bandKey(band));
    return b ? b.name.en : '';
  };
  const bandCan = (band) => {
    const b = doc.bands.find((x) => x.id === bandKey(band));
    return b ? b.can.en : '';
  };
  const skillTitle = (id) => {
    const s = doc.skills.find((x) => x.id === id);
    return s ? s.title : {en: id, fa: id};
  };
  const fmtDate = (iso) => new Date(iso).toLocaleDateString(undefined,
    {day: 'numeric', month: 'short', year: 'numeric'});

  const ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
    '<path d="M5 12h13m-5.5-5.5L18 12l-5.5 5.5"/></svg>';
  const TICK = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2.2" ' +
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m3 8.5 3.2 3.2L13 4.8"/></svg>';

  /* ---------------------------------------------------------------- engine */

  /* Same word, however it was typed: case, curly apostrophes, spacing and a
     final full stop are not what a cloze is testing. */
  const normalise = (value) => String(value == null ? '' : value)
    .replace(/[’`]/g, "'")
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase()
    .replace(/[.!?]+$/, '');

  const typedKinds = new Set(['cloze', 'transform', 'order']);

  function isCorrect(item, value) {
    if (item.kind === 'mcq' || item.kind === 'error') {
      return typeof value === 'number' && value === item.answer;
    }
    if (!typedKinds.has(item.kind)) return false;
    if (value == null || value === '') return false;
    const given = Array.isArray(value) ? value.join(' ') : value;
    const wanted = (item.accept || []).map(normalise);
    return wanted.includes(normalise(given));
  }

  /* One paper for everyone: ten questions from each band, climbing A1 to C1.
     Nothing is chosen from the learner's answers, which is exactly what makes
     a raw count comparable between two people. */
  let paperIds = null;
  function paper(bank) {
    if (paperIds) return paperIds;
    /* The recognition questions only. Writing is assessed, but it is marked
       against a rubric rather than answered, so it is not one of a band's ten:
       it has its own part, and joins the total there. */
    const skills = bank.blueprint.objective ||
      bank.blueprint.assessed.filter((s) => s !== 'writing');
    const ids = [];
    bank.blueprint.bands.forEach((band) => {
      skills.forEach((skill) => {
        bank.items.forEach((it) => {
          if (it.skill === skill && it.band === band) ids.push(it.id);
        });
      });
    });
    paperIds = ids;
    return ids;
  }
  const partSize = (bank) => bank.blueprint.perBandTotal -
    ((bank.blueprint.perBand || {}).writing || 0);
  const partCount = (bank) => bank.blueprint.bands.length;
  const partBand = (bank, n) => bank.blueprint.bands[n] || null;
  function partIds(bank, n) {
    const size = partSize(bank);
    return paper(bank).slice(n * size, (n + 1) * size);
  }
  /* One marked task per band, in band order, so a weak writer is met where
     they are rather than at the top of the ladder. */
  const writingIds = (bank) => bank.blueprint.bands
    .map((band) => (bank.items.find((it) => it.skill === 'writing' && it.band === band) || {}).id)
    .filter(Boolean);

  function blankAttempt() {
    return {
      startedAt: Date.now(),
      part: 0,
      answers: {},
      practice: {writing: {}, speaking: {}},
      finishedAt: 0,
    };
  }

  const hasAnswer = (attempt, id) => {
    const v = attempt.answers[id];
    return v !== undefined && v !== '' && (!Array.isArray(v) || v.length > 0);
  };

  /* The level is the count, read against the cutoffs in the bank: eight right
     out of fifty is A1, seventeen A2, twenty-six B1, thirty-five B2, forty-four
     C1. The same fractions are applied to a skill's own total, so grammar out
     of fifteen and reading out of ten are read on one ruler. */
  function levelFromCorrect(right, total, cutoffs) {
    if (!total) return null;
    const share = right / total;
    let level = null;
    BANDS.forEach((band, k) => { if (share >= cutoffs[k]) level = band; });
    return level;
  }

  /* ------------------------------------------------------------ writing mark

     A written answer cannot be marked by a key, so it is marked by the four
     things the rubric on screen already names: enough words, enough sentences,
     the linking the task asked for, and a spot check for slips. Everything
     here is deterministic and visible to the learner - the same text always
     earns the same points, and the card says which point failed and why.

     What this is not: a judge of style. It cannot hear whether a sentence is
     natural, so it never claims to. The report calls the result "rubric
     points", which is what it is. */

  const SLIPS = [
    [/\b(he|she|it)\s+don'?t\b/i, "he/she/it with don't"],
    [/\b(i|you|we|they)\s+doesn'?t\b/i, "doesn't after a plural subject"],
    [/\b(i|you|we|they)\s+(is|was)\b/i, 'is/was after a plural subject'],
    [/\b(he|she|it)\s+(are|were)\b/i, 'are/were after a singular subject'],
    [/\ba\s+(?!(user|university|useful|usual|one|euro))[aeiou]\w*/i, 'a before a vowel'],
    [/\ban\s+(?!(hour|honest|honour|heir))[^aeiou\s]\w*/i, 'an before a consonant'],
    [/\bmore\s+\w+er\b/i, 'double comparative'],
    [/\bmost\s+\w+est\b/i, 'double superlative'],
  ];

  function writingSlips(text) {
    const t = String(text || '').trim();
    if (!t) return ['nothing written yet'];
    const slips = [];
    if (/^[a-z]/.test(t)) slips.push('the first word is not capitalised');
    if (!/[.!?]\s*$/.test(t)) slips.push('no full stop at the end');
    if (/(^|\s)i(\s|$|[,.])/.test(t)) slips.push('"i" in lower case');
    if (/ {2,}/.test(t)) slips.push('double spaces');
    if (/\s+[,.!?;:]/.test(t)) slips.push('a space before punctuation');
    SLIPS.forEach(([re, label]) => { if (re.test(t)) slips.push(label); });
    return slips;
  }

  function markWriting(bank, item, text) {
    const scale = (bank.writingScale || {})[item.band] || {words: 30, sentences: 3};
    const body = String(text || '');
    const words = (body.match(/[A-Za-z][A-Za-z'’-]*/g) || []).length;
    const sentences = body.split(/[.!?]+/).filter((s) => s.trim().length > 1).length;
    const lower = ' ' + body.toLowerCase().replace(/[’]/g, "'") + ' ';
    const needs = item.needs || [];
    const linked = needs.filter((n) => lower.includes(n));
    const slips = writingSlips(text);
    const parts = [
      {id: 'length', ok: words >= scale.words, note: `${words}/${scale.words} words`},
      {id: 'sentences', ok: sentences >= scale.sentences,
       note: `${sentences}/${scale.sentences} sentences`},
      {id: 'link', ok: linked.length > 0,
       note: linked.length ? `found "${linked[0]}"` : `wanted ${needs.slice(0, 2).join(' / ') || 'a link'}`},
      /* Nothing written is not "clean": it is empty, and an empty task has
         to count as wrong or a skipped paper would score. */
      {id: 'accuracy', ok: words > 0 && slips.length <= 1,
       note: words ? (slips.length ? slips[0] : 'no slips found') : 'nothing to check'},
    ];
    return {points: parts.filter((p) => p.ok).length, total: parts.length,
            parts, words, sentences, slips};
  }

  function writingResult(bank, attempt) {
    const picks = (attempt.practice && attempt.practice.writing) || {};
    const marks = writingIds(bank).map((id) => {
      const item = bank.items.find((it) => it.id === id);
      const text = ((picks[id] || {}).text) || '';
      return {id, band: item.band, text, mark: markWriting(bank, item, text)};
    });
    const points = marks.reduce((n, m) => n + m.mark.points, 0);
    const total = marks.reduce((n, m) => n + m.mark.total, 0);
    const cutoffs = bank.blueprint.cutoffs;
    return Object.assign({
      scored: 'rubric',
      band: levelFromCorrect(points, total, cutoffs),
      right: points,
      total,
      share: total ? Math.round((points / total) * 100) : 0,
      marks,
    }, confidenceFor(points, total, cutoffs));
  }

  /* How much a count lets us claim: a score that sits within one standard
     error of a cutoff could be a band either way. */
  function confidenceFor(right, total, cutoffs) {
    const p = total ? right / total : 0;
    const se = total ? Math.sqrt((p * (1 - p)) / total) : 0.5;
    const near = cutoffs.some((c) => Math.abs(p - c) <= se);
    return {
      se: Math.round(se * 100) / 100,
      confidence: near ? 'medium' : 'high',
      margin: near ? 1 : 0,
    };
  }

  function skillResult(bank, attempt, skill) {
    const rows = {};
    let right = 0;
    let total = 0;
    paper(bank).forEach((id) => {
      const item = bank.items.find((it) => it.id === id);
      if (!item || item.skill !== skill) return;
      rows[item.band] = rows[item.band] || {band: item.band, total: 0, right: 0};
      rows[item.band].total++;
      total++;
      if (isCorrect(item, attempt.answers[id])) {
        rows[item.band].right++;
        right++;
      }
    });
    const cutoffs = bank.blueprint.cutoffs;
    return Object.assign({
      band: levelFromCorrect(right, total, cutoffs),
      bands: BANDS.filter((b) => rows[b]).map((b) => rows[b]),
      right,
      total,
      share: total ? Math.round((right / total) * 100) : 0,
    }, confidenceFor(right, total, cutoffs));
  }

  function compute(bank, attempt) {
    const objective = bank.blueprint.objective ||
      bank.blueprint.assessed.filter((s) => s !== 'writing');
    const skills = {};
    objective.forEach((skill) => {
      skills[skill] = skillResult(bank, attempt, skill);
    });
    const writing = writingResult(bank, attempt);
    skills.writing = writing;
    const cutoffs = bank.blueprint.cutoffs;
    const right = objective.reduce((n, s) => n + skills[s].right, 0);
    const total = objective.reduce((n, s) => n + skills[s].total, 0);
    /* One ruler for both: a task is worth up to one question, marked in
       quarters, so fifty recognition questions and five tasks make 55. */
    const perTask = bank.blueprint.writingPoints || 4;
    const earned = right + (perTask ? writing.right / perTask : 0);
    const outOf = total + writing.marks.length;
    /* Two numbers, kept apart because they mean different things. `questions`
       is how many this attempt answered - a run that skipped a part has fewer,
       and the report has to say so. `paper` is how many the assessment asks,
       which is the bank's own blueprint and never a property of one attempt:
       the certificate printed the answered count as if it were the size of the
       test, so a half-finished run issued a sheet for "36 questions". */
    const questions = paper(bank).filter((id) => hasAnswer(attempt, id)).length +
      writing.marks.filter((m) => m.text.trim()).length;
    const paperSize = paper(bank).length + writing.marks.length;
    const practice = {};
    bank.blueprint.practice.forEach((skill) => {
      const picks = (attempt.practice && attempt.practice[skill]) || {};
      const tasks = bank.items.filter((it) => it.skill === skill);
      practice[skill] = {
        rated: Object.keys(picks).filter((k) => picks[k] && picks[k].rating).length,
        total: tasks.length,
        picks,
      };
    });
    return {
      at: new Date().toISOString(),
      overall: levelFromCorrect(earned, outOf, cutoffs) || PRE,
      right,
      total,
      earned: Math.round(earned * 100) / 100,
      outOf,
      share: outOf ? Math.round((earned / outOf) * 100) : 0,
      skills,
      practice,
      questions,
      paper: paperSize,
      minutes: attempt.finishedAt && attempt.startedAt
        ? Math.max(1, Math.round((attempt.finishedAt - attempt.startedAt) / 60000)) : 0,
      completion: questions >= total ? 'complete' : 'partial',
    };
  }

  /* --------------------------------------------------------------- storage */

  function attemptState() {
    if (state) return state;
    state = read(KEY.attempt, null) || blankAttempt();
    /* A half-finished paper is read back after an update, and the paper it was
       written on may not have had the shape it has now: no writing box, no
       speaking box, no part number. Reading those as if they were this
       build's is how a saved attempt came back as a blank sheet - the first
       tap on a question threw on `undefined`, and on the phone a throw inside
       a paint is an empty panel with nothing to scroll. */
    state.answers = state.answers || {};
    state.practice = state.practice || {};
    ['writing', 'speaking'].forEach((k) => { state.practice[k] = state.practice[k] || {}; });
    const rooms = doc ? partCount(doc) : 0;
    if (typeof state.part !== 'number' || state.part < 0 || (rooms && state.part >= rooms)) {
      state.part = 0;
    }
    return state;
  }
  function saveAttempt(now) {
    clearTimeout(saveTimer);
    if (now) { if (state) write(KEY.attempt, state); return; }
    saveTimer = setTimeout(() => { if (state) write(KEY.attempt, state); }, 350);
  }

  /* Every missed item is a diagnosis the app already made and used to throw
     away: the item knows its skill and its subskill, and the item itself has
     the prompt, the options and the explanation. Writing those into the error
     log is what turns one paper into a profile, and the drill can then ask the
     same questions again without a second copy of the bank. */
  function recordMisses(attempt) {
    if (!doc || typeof ErrorLog === 'undefined') return;
    let log = ErrorLog.read();
    const today = Mastery.keyOf(new Date());
    paper(doc).forEach((id) => {
      if (!hasAnswer(attempt, id)) return;
      const item = doc.items.find((it) => it.id === id);
      if (!item || isCorrect(item, attempt.answers[id])) return;
      if (!Array.isArray(item.options) || typeof item.answer !== 'number') return;
      const sub = item.subskill || {};
      const key = 'level:' + String(sub.en || item.skill || 'other')
        .toLowerCase().replace(/[^a-z0-9]+/g, '-');
      log = ErrorLog.note(log,
        {key: key, en: sub.en || item.skill || 'Other', fa: sub.fa || ''},
        {id: item.id, kind: 'choice', prompt: item.prompt, options: item.options,
         answer: item.answer, why: item.why || {en: '', fa: ''},
         detail: item.ability || {en: '', fa: ''}}, today);
    });
    ErrorLog.write(log);
    if (typeof Slip !== 'undefined') Slip.refresh();
  }

  function recordItems(result, attempt) {
    const stats = read(KEY.items, {});
    paper(doc).filter((id) => hasAnswer(attempt, id)).forEach((id) => {
      const item = doc.items.find((it) => it.id === id);
      if (!item) return;
      const row = stats[id] || {a: 0, c: 0};
      row.a++;
      if (isCorrect(item, attempt.answers[id])) row.c++;
      stats[id] = row;
    });
    write(KEY.items, stats);
  }

  /* ------------------------------------------------------------------ hero */

  const ladder = (active) => '<div class="lv-ladder" aria-hidden="true">' +
    BANDS.map((b) => `<span class="lv-rung${active && bandIndex(active) >= bandIndex(b) ? ' on' : ''}" data-band="${b}">${b}</span>`).join('') +
    '</div>';

  const ring = (daysLeft) => {
    const c = 2 * Math.PI * 26;
    const gone = Math.max(0, Math.min(1, 1 - daysLeft / doc.retakeDays));
    return `<div class="lv-ringwrap" aria-hidden="true">
      <svg class="lv-ring" viewBox="0 0 64 64">
        <circle class="lv-ringbg" cx="32" cy="32" r="26"/>
        <circle class="lv-ringfg" cx="32" cy="32" r="26"
          stroke-dasharray="${c.toFixed(1)}" stroke-dashoffset="${(c * (1 - gone)).toFixed(1)}"/>
      </svg>
      <b>${daysLeft}<small>${daysLeft === 1 ? 'day' : 'days'}</small></b>
    </div>`;
  };

  function chips() {
    const assessed = doc.blueprint.assessed.length;
    return `<div class="lv-meta">
      <span class="lv-chip"><b>${numWord(assessed)}</b> skills measured</span>
      <span class="lv-chip"><b>${doc.blueprint.questions}</b> questions</span>
      <span class="lv-chip">about <b>${doc.minutes}</b> min</span>
      <span class="lv-chip">same paper for everyone</span>
    </div>`;
  }

  function renderIntro() {
    const result = read(KEY.result, null);
    const history = read(KEY.history, []);
    const until = result ? Date.parse(result.at) + doc.retakeDays * DAY : 0;
    const locked = !!result && Date.now() < until;
    const days = Math.max(1, Math.ceil((until - Date.now()) / DAY));
    const resumed = read(KEY.attempt, null);
    const touched = resumed && Object.keys(resumed.answers || {}).length > 0;

    const hero = result
      ? `<div class="lv-bigband" data-band="${bandKey(result.overall)}">
           <div class="lv-disc" aria-hidden="true">${bandLabel(result.overall)}</div>
           <div>
             <b>${esc(bandName(result.overall))}</b>
             <p>${esc(bandCan(result.overall))}</p>
           </div>
         </div>
         ${ladder(result.overall)}
         ${locked ? `<div class="lv-wait">
             ${ring(days)}
             <div>
               <b>Next check opens in ${days} ${days === 1 ? 'day' : 'days'}.</b>
               <p class="lv-fa" dir="rtl" lang="fa">سنجش بعدی ${days} روز دیگر باز می‌شود.</p>
             </div>
           </div>` : ''}`
      : `${ladder(null)}${chips()}`;

    const actions = locked
      ? `<button class="lv-btn lv-cta" data-act="result">
           <span>See the full report
             <small>${fmtDate(result.at)} · ${bandLabel(result.overall)} · ${result.right}/${result.total} correct · ${result.minutes} min</small>
           </span>${ARROW}</button>`
      : `<button class="lv-btn lv-cta" data-act="start">
           <span>${touched ? 'Continue the assessment' : result ? "Take this month's assessment" : 'Start the assessment'}              <small>${touched ? 'Your place is saved' : doc.blueprint.questions + ' questions · about ' + doc.minutes + ' minutes · ' + numWord(doc.blueprint.assessed.length) + ' skills measured'}</small>
           </span>${ARROW}</button>
         ${touched ? `<button class="lv-btn ghost" data-act="restart">Start over</button>` : ''}
         ${result ? `<button class="lv-btn ghost" data-act="result">Last report</button>` : ''}`;

    const skills = doc.skills.map((s) => `<div class="lv-skillrow" data-band="${result && s.assessed && result.skills[s.id] ? bandKey(result.skills[s.id].band) : 'none'}">
        <span class="lv-skname">${esc(s.title.en)}
          <small dir="rtl" lang="fa">${esc(s.title.fa)}</small></span>
        <span class="lv-skself">${s.assessed ? 'measured' : 'practice only'}</span>
        <span class="lv-skev">${esc(s.blurb.en)}</span>
      </div>`).join('');

    const hist = history.length > 1
      ? `<div class="lv-hist"><h4>Earlier assessments</h4>${history.slice(1, 7).map((h) => `
          <div class="lv-histrow" data-band="${bandKey(h.overall)}">
            <span>${fmtDate(h.at)}</span>
            <span class="lv-dots">${BANDS.map((b) =>
              `<i style="opacity:${h.overall && bandIndex(h.overall) >= bandIndex(b) ? 1 : .18}"></i>`).join('')}</span>
            <span>${bandLabel(h.overall)}</span>
          </div>`).join('')}</div>`
      : '';

    body().innerHTML = `<div class="lv-wrap">
      <section class="lv-hero">
        <div class="lv-eyebrow">${locked ? 'This month' : 'Level assessment'} · ${doc.retakeDays} days apart</div>
        <h2 class="lv-h">${locked ? 'Your level this month' : 'Where does your English actually sit?'}</h2>
        <p class="lv-sub">${esc(doc.blurb.en)}</p>
        ${faLine(doc.blurb.fa)}
        ${hero}
        <div class="lv-actions">${actions}</div>
      </section>
      <div class="lv-sectiontitle">What gets measured</div>
      <div class="lv-game">${skills}</div>
      <details class="lv-method">
        <summary>How the level is worked out</summary>
        <p>${esc(doc.method.en)}</p>
        ${faLine(doc.method.fa)}
        <p class="lv-note">${esc(doc.caveat.en)}</p>
      </details>
      ${hist}
    </div>`;
  }

  /* ------------------------------------------------------------------ test */

  function groupBySkill(ids) {
    const groups = [];
    ids.forEach((id) => {
      const item = doc.items.find((it) => it.id === id);
      if (!item) return;
      let g = groups.find((x) => x.skill === item.skill);
      if (!g) { g = {skill: item.skill, ids: []}; groups.push(g); }
      g.ids.push(id);
    });
    return groups;
  }

  function passageBlock(item) {
    const p = doc.passages.find((x) => x.id === item.passage);
    if (!p) return '';
    return `<div class="lv-passage">
      <h4>${esc(p.title.en)}</h4>
      <p>${esc(p.text.en)}</p>
      <details><summary>Persian — ترجمهٔ فارسی</summary>${faLine(p.text.fa)}</details>
    </div>`;
  }

  function answerOf(id) {
    return attemptState().answers[id];
  }

  function questionCard(item, number) {
    const value = answerOf(item.id);
    const done = value !== undefined && value !== '';
    const read = item.kind === 'reading' || item.passage;
    const head = `<div class="lv-qh">
        <span class="lv-qn">${number}</span>
        ${bandPill(item.band)}
        <span class="lv-subskill">${esc(item.subskill.en)}</span>
        ${done ? `<span class="lv-tick" role="img" aria-label="answered">${TICK}</span>` : ''}
      </div>`;

    const audio = item.say
      ? `<button class="lv-play" type="button" data-rec="${item.id}">
           <svg viewBox="0 0 24 24" width="13" height="13" fill="currentColor" aria-hidden="true"><path d="M8 5.4v13.2L19 12Z"/></svg>
           Play the recording
         </button>
         <details class="lv-transcript"><summary>Transcript (try without it)</summary>
           <p>${esc(item.say)}</p></details>`
      : '';

    let answerUi = '';
    if (item.kind === 'mcq' || item.kind === 'error') {
      answerUi = `<div class="lv-opts">${item.options.map((opt, k) => `
        <label class="lv-opt${value === k ? ' on' : ''}">
          <input type="radio" name="lv-${item.id}" value="${k}" data-answer="${item.id}"
            ${value === k ? 'checked' : ''}>
          <span class="lv-od" aria-hidden="true">${LETTERS[k]}</span>
          <span class="lv-ot">${esc(opt)}</span>
        </label>`).join('')}</div>`;
    } else if (item.kind === 'cloze') {
      answerUi = `<input class="lv-input" type="text" data-typed="${item.id}"
        value="${esc(value || '')}" autocomplete="off" spellcheck="false"
        placeholder="Type the missing word — واژهٔ جاافتاده" aria-label="Your answer">`;
    } else if (item.kind === 'transform') {
      answerUi = `<textarea class="lv-textarea" data-typed="${item.id}" dir="auto"
        placeholder="Write the full sentence — جملهٔ کامل را بنویس"
        aria-label="Your answer">${esc(value || '')}</textarea>`;
    } else if (item.kind === 'order') {
      const picked = Array.isArray(value) ? value : [];
      const rest = item.tokens.filter((t) => !picked.includes(t));
      answerUi = `<div class="lv-compose" data-compose="${item.id}">
          <div class="lv-built">${picked.length
            ? picked.map((t, k) => `<button type="button" class="lv-token on" data-pick="${item.id}" data-k="${k}">${esc(t)}</button>`).join('')
            : '<span class="lv-hintline">Tap the words in order</span>'}</div>
          <div class="lv-pool">${rest.map((t) => `<button type="button" class="lv-token" data-add="${item.id}" data-token="${esc(t)}">${esc(t)}</button>`).join('')}</div>
        </div>`;
    }

    return `${read ? '' : ''}<div class="lv-q${done ? ' answered' : ''}" id="lvq-${item.id}">
      ${head}
      <p class="lv-stem">${esc(item.prompt.en)}</p>
      ${faLine(item.prompt.fa)}
      ${audio}
      ${answerUi}
    </div>`;
  }

  function bandPill(band) {
    return `<span class="lv-band" data-band="${bandKey(band)}">${bandLabel(band)}</span>`;
  }

  function renderTest() {
    const a = attemptState();
    const band = partBand(doc, a.part);
    const ids = partIds(doc, a.part);
    const parts = partCount(doc);
    const paperTotal = paper(doc).length;
    const answered = ids.filter((id) => hasAnswer(a, id)).length;
    const answeredAll = paper(doc).filter((id) => hasAnswer(a, id)).length;
    const groups = groupBySkill(ids);
    let n = a.part * partSize(doc);

    const blocks = groups.map((g) => {
      /* One passage, not one per question: the questions that share a text sit
         right under it. */
      const shown = new Set();
      return `<div class="lv-skillblock">
        <div class="lv-caption">
          <span>${esc(skillTitle(g.skill).en)}</span>
          <span class="lv-fa" dir="rtl" lang="fa">${esc(skillTitle(g.skill).fa)}</span>
        </div>
        ${g.ids.map((id) => {
          const item = doc.items.find((it) => it.id === id);
          n++;
          let text = '';
          if (item.passage && !shown.has(item.passage)) {
            shown.add(item.passage);
            text = passageBlock(item);
          }
          return text + questionCard(item, n);
        }).join('')}
      </div>`;
    }).join('');

    body().innerHTML = `<div class="lv-wrap">
      <div class="lv-top">
        <div class="lv-toprow">
          <span class="lv-step">Part ${a.part + 1} of ${parts} · ${band}</span>
          <span class="lv-secttl">${groups.map((g) => skillTitle(g.skill).en).join(' · ')}</span>
          <span class="lv-count" data-count>${answered} of ${ids.length} answered</span>
        </div>
        <div class="lv-toptrack"><i data-track style="width:${ids.length ? Math.round(answered / ids.length * 100) : 0}%"></i></div>
        <button class="lv-exit" type="button" data-act="pause">Pause and keep my place</button>
      </div>
      <p class="lv-secnote">${answeredAll} of ${paperTotal} answered so far. This part is the ${band} band:
        the paper starts at A1 and climbs to C1, so later parts are meant to feel hard.</p>
      ${faLine(`تا اینجا ${answeredAll} پرسش از ${paperTotal} پاسخ داده شده. این بخش سطح ${band} است: ` +
        'برگه از A1 شروع می‌شود و تا C1 بالا می‌رود، پس بخش‌های بعدی باید سخت به نظر برسند.')}
      ${blocks}
      <div class="lv-foot">
        <button class="lv-btn" data-act="part" type="button">
          ${a.part + 1 >= parts ? 'Writing tasks' : 'Next part'}
        </button>
        <span class="lv-menu" data-hint>${answered} of ${ids.length} in this part</span>
        <span class="lv-keys"><kbd>1</kbd>–<kbd>4</kbd> answer</span>
      </div>
    </div>`;
    warned = false;
  }

  /* --------------------------------------------------------------- writing */

  const MARK_LABEL = {length: 'enough words', sentences: 'enough sentences',
                      link: 'links its ideas', accuracy: 'no slips'};

  function markChips(mark, scale) {
    return `<span class="lv-wmh">Marked on the rubric — <b>${mark.points}/4</b>` +
      `<i>${scale.words}+ words, ${scale.sentences}+ sentences</i></span>` +
      `<span class="lv-wms">${mark.parts.map((p) =>
        `<span class="lv-wmk${p.ok ? ' on' : ''}">${p.ok ? TICK : ''}` +
        `${MARK_LABEL[p.id]} <i>${esc(p.note)}</i></span>`).join('')}</span>`;
  }

  function renderWriting() {
    const a = attemptState();
    const picks = a.practice.writing || (a.practice.writing = {});
    const tasks = writingIds(doc).map((id) => doc.items.find((it) => it.id === id));
    const written = tasks.filter((it) => String((picks[it.id] || {}).text || '').trim()).length;
    const cards = tasks.map((item, k) => {
      const pick = picks[item.id] || {};
      const text = pick.text || '';
      const scale = (doc.writingScale || {})[item.band] || {words: 30, sentences: 3};
      const mark = markWriting(doc, item, text);
      const done = String(text).trim().length > 0;
      return `<div class="lv-q${done ? ' answered' : ''}" id="lvq-${item.id}">
        <div class="lv-qh">
          <span class="lv-qn">${k + 1}</span>
          ${bandPill(item.band)}
          <span class="lv-subskill">${esc(item.subskill.en)}</span>
          ${done ? `<span class="lv-tick" role="img" aria-label="answered">${TICK}</span>` : ''}
        </div>
        <p class="lv-stem">${esc(item.prompt.en)}</p>
        ${faLine(item.prompt.fa)}
        <textarea class="lv-textarea" data-practice="${item.id}" dir="auto"
          placeholder="Write your answer here — بنویس">${esc(text)}</textarea>
        <div class="lv-wmark" data-mark="${item.id}">${markChips(mark, scale)}</div>
      </div>`;
    }).join('');

    body().innerHTML = `<div class="lv-wrap">
      <div class="lv-top">
        <div class="lv-toprow">
          <span class="lv-step">Writing</span>
          <span class="lv-secttl">One task per band</span>
          <span class="lv-count" data-wcount>${written} of ${tasks.length} written</span>
        </div>
        <div class="lv-toptrack"><i data-wtrack style="width:${tasks.length ? Math.round(written / tasks.length * 100) : 0}%"></i></div>
        <button class="lv-exit" type="button" data-act="pause">Pause and keep my place</button>
      </div>
      <div class="lv-callout">
        <b>Writing is scored, and you can see the marks as you type.</b>
        <p>Each task is worth four points: enough words for the band, enough sentences, the linking
          the task asks for, and a spot check for slips. One task is worth one question in the total,
          so a strong paragraph cannot outweigh fifty answers — and a blank one counts as wrong.</p>
        ${faLine('نوشتن نمره می‌گیرد و نمره را همان‌طور که می‌نویسی می‌بینی. هر تمرین چهار امتیاز دارد: ' +
          'واژهٔ کافی برای سطح، جملهٔ کافی، پیوندی که تمرین می‌خواهد و یک بررسی نمونه‌ای. هر تمرین ' +
          'به اندازهٔ یک پرسش در مجموع می‌ارزد و تمرین خالی اشتباه حساب می‌شود.')}
      </div>
      ${cards}
      <div class="lv-foot">
        <button class="lv-btn" data-act="finish" type="button">See my level</button>
        <span class="lv-menu">${tasks.length - written} still empty</span>
      </div>
    </div>`;
    warned = false;
  }

  /* -------------------------------------------------------------- practice */

  function renderPractice() {
    const a = attemptState();
    const tasks = doc.items.filter((it) => it.skill === 'speaking');
    const cards = tasks.map((item, k) => {
      const pick = (a.practice[item.skill] || {})[item.id] || {};
      const speaking = item.kind === 'speaking';
      return `<div class="lv-q${pick.rating ? ' answered' : ''}" id="lvq-${item.id}">
        <div class="lv-qh">
          <span class="lv-qn">${k + 1}</span>
          ${bandPill(item.band)}
          <span class="lv-skself">${speaking ? 'speaking' : 'writing'} · not assessed</span>
        </div>
        <p class="lv-stem">${esc(item.prompt.en)}</p>
        ${faLine(item.prompt.fa)}
        <p class="lv-note">${esc(item.why.en)}</p>
        ${speaking
          ? `<button class="lv-btn ghost" type="button" data-timer="${item.id}">
               <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></svg>
               30-second timer
             </button>
             <span class="lv-timer" hidden>speaking… <b>30s</b></span>`
          : `<textarea class="lv-textarea" data-practice="${item.id}" dir="auto"
               placeholder="Write your answer here — بنویس">${esc(pick.text || '')}</textarea>`}
        <div class="lv-rublabel">Optional: which describes your answer?</div>
        <div class="lv-rubric">${doc.rubric.map((r) => `
          <label class="lv-opt${pick.rating === r.points ? ' on' : ''}">
            <input type="radio" name="pr-${item.id}" value="${r.points}" data-rating="${item.id}"
              ${pick.rating === r.points ? 'checked' : ''}>
            <span class="lv-od" aria-hidden="true">${r.points}</span>
            <span class="lv-ot">${esc(r.text.en)}<br><span class="fa" dir="rtl" lang="fa">${esc(r.text.fa)}</span></span>
          </label>`).join('')}
        </div>
      </div>`;
    }).join('');

    body().innerHTML = `<div class="lv-wrap">
      <div class="lv-top">
        <div class="lv-toprow">
          <span class="lv-step">Practice</span>
          <span class="lv-secttl">Speaking</span>
          <span class="lv-count">not part of the level</span>
        </div>
      </div>
      <div class="lv-callout">
        <b>Speaking is reported as not assessed.</b>
        <p>These tasks are here to practise, and to rate yourself against a rubric. They are never
          averaged into your level, because a self-rating is not a proficiency score. Writing is
          scored, on the page before this one.</p>
        ${faLine('گفتن «سنجیده‌نشده» گزارش می‌شود. این تمرین‌ها برای تمرین و سنجش خودت با معیار است و هرگز در سطح کلی میانگین نمی‌شود، چون خودسنجی نمرهٔ مهارت نیست. نوشتن در صفحهٔ پیش نمره می‌گیرد.')}
      </div>
      ${cards}
      <div class="lv-foot">
        <button class="lv-btn" data-act="finish" type="button">See my level</button>
        <span class="lv-menu">you can skip this part</span>
      </div>
    </div>`;
  }

  /* ---------------------------------------------------------------- report */

  function confidenceChip(skill) {
    const words = {high: 'high confidence', medium: 'moderate confidence', low: 'low confidence'};
    return `<span class="lv-conf c-${skill.confidence}">${words[skill.confidence]}` +
      (skill.margin ? ' · ±1 band' : '') + `</span>`;
  }

  function renderResult() {
    const result = read(KEY.result, null);
    if (!result) { view = 'intro'; renderIntro(); return; }
    const until = Date.parse(result.at) + doc.retakeDays * DAY;
    const days = Math.max(0, Math.ceil((until - Date.now()) / DAY));
    const history = read(KEY.history, []);
    const prev = history[1] || null;

    const rows = doc.skills.map((s) => {
      const r = result.skills[s.id];
      if (!s.assessed || !r) {
        return `<div class="lv-skillrow lv-unassessed" data-band="none">
          <span class="lv-skname">${esc(s.title.en)}
            <small dir="rtl" lang="fa">${esc(s.title.fa)}</small></span>
          <span class="lv-skband"><span class="lv-band" data-band="none">not assessed</span></span>
          <span class="lv-skev">${esc(s.blurb.en)}</span>
        </div>`;
      }
      /* Writing is counted, not answered, so its evidence is rubric points -
         saying "9 of 20 correct" there would describe the wrong thing. */
      const evidence = r.scored === 'rubric'
        ? `${r.right} of ${r.total} rubric points (${r.share}%)`
        : `${r.right} of ${r.total} correct (${r.share}%)`;
      return `<div class="lv-skillrow" data-band="${bandKey(r.band)}">
        <span class="lv-skname">${esc(s.title.en)}
          <small dir="rtl" lang="fa">${esc(s.title.fa)}</small></span>
        <span class="lv-skband">${bandPill(r.band)}</span>
        <span class="lv-evidence">${evidence}</span>
        ${confidenceChip(r)}
        <span class="lv-scale">${BANDS.map((b, k) =>
          `<i class="${k <= bandIndex(r.band) ? 'on' : ''}"></i>`).join('')}</span>
      </div>`;
    }).join('');

    const measured = doc.blueprint.assessed
      .map((id) => ({id, ...result.skills[id]}))
      .filter((x) => x.total);
    const strongest = measured.slice().sort((a, b) => bandIndex(b.band) - bandIndex(a.band))[0];
    const weakest = measured.slice().sort((a, b) => bandIndex(a.band) - bandIndex(b.band))[0];
    const tied = strongest && weakest &&
      bandIndex(strongest.band) === bandIndex(weakest.band);
    const      advice = tied
      ? ['Stories at my level', 'stories']
      : {
        grammar: ['Open grammar', 'grammar'],
        vocabulary: ['Open vocabulary', 'vocab'],
        reading: ['Read a story', 'stories'],
        listening: ['Open listening', 'listen'],
        writing: ['Practice writing', 'writing'],
      }[weakest ? weakest.id : 'reading'];
    const speakingTasks = doc.items.filter((it) => it.skill === 'speaking').length;

    const delta = prev && prev.overall && result.overall
      ? bandIndex(result.overall) - bandIndex(prev.overall) : 0;
    const stats = read(KEY.items, {});
    const weakItems = Object.entries(stats)
      .filter(([, r]) => r.a >= 2 && r.c / r.a <= 0.5)
      .map(([id]) => doc.items.find((it) => it.id === id))
      .filter(Boolean).slice(0, 3);

    body().innerHTML = `<div class="lv-wrap">
      <section class="lv-hero" data-band="${bandKey(result.overall)}">
        <div class="lv-eyebrow">Report · ${fmtDate(result.at)} · ${result.right} of ${result.total} correct · ${result.minutes} min</div>
        <div class="lv-bigband" style="margin-top:4px">
          <div class="lv-disc" aria-hidden="true">${bandLabel(result.overall)}</div>
          <div>
            <b>${esc(bandName(result.overall))}</b>
            <p>${esc(bandCan(result.overall))}</p>
            ${faLine(bandCan(result.overall) ? '' : '')}
          </div>
        </div>
        ${ladder(result.overall)}
        <div class="lv-insight">
          <span><b>Score</b> ${result.right} of ${result.total} correct (${result.share}%)</span>
          <span><b>Based on</b> ${measured.length} of 6 skills. Speaking is not assessed.</span>
          ${prev ? `<span><b>Last time</b> ${fmtDate(prev.at)} · ${bandLabel(prev.overall)}${delta
            ? ` (${delta > 0 ? '+' : ''}${delta} band${Math.abs(delta) === 1 ? '' : 's'})` : ' (no change)'}</span>` : ''}
          <span><b>Completed</b> ${result.completion === 'complete' ? `all ${result.questions} questions` : `${result.questions} of ${result.paper} questions`}${result.completion !== 'complete' ? ' — unanswered questions count as wrong, so the level is provisional' : ''}</span>
        </div>
      </section>

      <div class="lv-sectiontitle">Skill profile</div>
      <div class="lv-game">${rows}</div>

      <div class="lv-next" data-band="${bandKey(result.overall)}">
        <h4>Next</h4>
        <p>${tied
          ? `An even profile: all ${numWord(measured.length)} measured skills sit at <b>${bandLabel(result.overall)}</b>.
             The next step is material at that level rather than repair of one skill.`
          : `${strongest ? `Strongest: <b>${esc(skillTitle(strongest.id).en)}</b> (${bandLabel(strongest.band)}). ` : ''}${
            weakest ? `Work next on <b>${esc(skillTitle(weakest.id).en)}</b> (${bandLabel(weakest.band)}).` : ''}`}</p>
        ${faLine('قوی‌ترین مهارت و مهارتی که باید رویش کار کنی در بالا آمده است.')}
        <div class="lv-actions">
          <button class="lv-btn ghost" data-act="open" data-panel="${advice[1]}" data-band="${bandKey(result.overall)}">${advice[0]}</button>
          ${speakingTasks ? '<button class="lv-btn ghost" data-act="practice">Speaking practice</button>' : ''}
          <button class="lv-btn" data-act="certificate">Get certificate</button>
          <button class="lv-btn ghost" data-act="intro">Done</button>
        </div>
      </div>

      ${weakItems.length ? `<div class="lv-reliability">
        <b>Questions you have missed more than once</b>
        <ul>${weakItems.map((it) => `<li>${esc(it.subskill.en)} <span class="lv-band" data-band="${it.band}">${it.band}</span></li>`).join('')}</ul>
        <p>Kept on this device only, to aim the next attempt. Item difficulty is tracked from your own
          answers; it is not a calibrated item bank.</p>
      </div>` : ''}

      <p class="lv-note">${esc(doc.caveat.en)}</p>
      <p class="lv-note">${days > 0
        ? `The next assessment opens in <b>${days} ${days === 1 ? 'day' : 'days'}</b>, on ${fmtDate(new Date(until).toISOString())}.`
        : 'This assessment is a month old — you can take it again.'}</p>
      ${days > 0 ? '' : '<div class="lv-actions"><button class="lv-btn" data-act="restart">Take this month\'s assessment</button></div>'}
    </div>`;
  }

  /* ----------------------------------------------------------------- flow */

  function render() {
    if (ticker) { clearInterval(ticker); ticker = null; }
    try {
      if (view === 'test') renderTest();
      else if (view === 'writing') renderWriting();
      else if (view === 'practice') renderPractice();
      else if (view === 'result') renderResult();
      else renderIntro();
    } catch (e) {
      /* A paint that throws used to leave the panel half-built, which on a
         phone is a white sheet with nothing on it and no way forward. The
         answers are already written down, so say that and offer the door back
         rather than a dead panel. */
      console.error('level:', e);
      fallbackSheet();
    }
    /* A paint that draws nothing at all leaves the panel as it found it, which
       on the phone is the same empty sheet as a throw. If the paper was meant
       to have questions and the body has none, say so instead of showing a
       blank panel. */
    if (view !== 'practice') {
      const host = body();
      if (host && !host.childElementCount) {
        console.error('level: the panel came out empty (' + view + ')');
        fallbackSheet();
      }
    }
  }

  /* The one door out of a paper that cannot be drawn: the answers are already
     written down, so the learner is told that and offered a way back. */
  function fallbackSheet() {
    const host = body();
    if (!host) return;
    host.innerHTML = `<div class="lv-wrap"><section class="lv-hero">
      <div class="lv-eyebrow">Level assessment</div>
      <h2 class="lv-h">This part could not be drawn</h2>
      <p class="lv-sub">Your answers are saved. Open the level check again to carry on where you were.</p>
      ${faLine('پاسخ‌هایت ذخیره شده‌اند. بخش سنجش سطح را دوباره باز کن تا از همان‌جا ادامه دهی.')}
      <div class="lv-actions"><button class="lv-btn" data-act="intro">Back to the start</button></div>
    </section></div>`;
  }

  function start(fresh) {
    if (fresh || !read(KEY.attempt, null)) {
      state = blankAttempt();
      write(KEY.attempt, state);
    } else {
      state = read(KEY.attempt, null);
    }
    view = 'test';
    render();
    body().scrollIntoView({block: 'start'});
  }

  function nextPart() {
    const a = attemptState();
    const ids = partIds(doc, a.part);
    const answered = ids.filter((id) => hasAnswer(a, id)).length;
    if (answered < ids.length && !warned) {
      warned = true;
      const hint = body().querySelector('[data-hint]');
      if (hint) hint.innerHTML = `<span class="lv-warn">${ids.length - answered} unanswered — press again</span>`;
      return;
    }
    a.part++;
    warned = false;

    if (a.part >= partCount(doc)) {
      view = 'writing';
      saveAttempt(true);
      render();
      body().scrollIntoView({block: 'start'});
      return;
    }
    saveAttempt(true);
    render();
    body().scrollIntoView({block: 'start'});
  }

  function finish() {
    const a = attemptState();
    a.finishedAt = Date.now();
    const result = compute(doc, a);
    write(KEY.result, result);
    recordItems(result, a);
    recordMisses(a);
    const history = read(KEY.history, []);
    history.unshift({at: result.at, overall: result.overall,
                     skills: Object.fromEntries(Object.entries(result.skills).map(([k, v]) => [k, v.band]))});
    write(KEY.history, history.slice(0, 12));
    try { localStorage.removeItem(KEY.attempt); } catch (e) { /* private */ }
    state = null;
    view = 'result';
    paintBadge();
    // a placement is what puts the learning path in the header
    if (typeof Path !== 'undefined') Path.sync();
    render();
    body().scrollIntoView({block: 'start'});
  }

  function paintBadge() {
    const badge = document.getElementById('lvlbadge');
    const result = read(KEY.result, null);
    if (!badge) return;
    if (result && result.overall) {
      badge.textContent = bandKey(result.overall);
      badge.hidden = false;
    } else if (result) {
      badge.textContent = 'PRE';
      badge.hidden = false;
    } else {
      badge.hidden = true;
    }
  }

  /* ---------------------------------------------------------------- input */

  function markCard(id) {
    const card = document.getElementById('lvq-' + id);
    if (!card) return;
    card.classList.add('answered');
    if (card.querySelector('.lv-tick')) return;
    const head = card.querySelector('.lv-qh');
    if (!head) return;
    const tick = document.createElement('span');
    tick.className = 'lv-tick';
    tick.setAttribute('role', 'img');
    tick.setAttribute('aria-label', 'answered');
    tick.innerHTML = TICK;
    head.append(tick);
  }

  /* A word-ordering answer repaints only its own block: rerendering the round
     would throw the reader back to the top of it. */
  function paintCompose(id) {
    const host = body().querySelector('[data-compose="' + id + '"]');
    if (!host) return;
    const item = doc.items.find((it) => it.id === id);
    const a = attemptState();
    const picked = Array.isArray(a.answers[id]) ? a.answers[id] : [];
    const rest = item.tokens.filter((t) => !picked.includes(t));
    host.innerHTML = `
      <div class="lv-built">${picked.length
        ? picked.map((t, k) => `<button type="button" class="lv-token on" data-pick="${id}" data-k="${k}">${esc(t)}</button>`).join('')
        : '<span class="lv-hintline">Tap the words in order</span>'}</div>
      <div class="lv-pool">${rest.map((t) => `<button type="button" class="lv-token" data-add="${id}" data-token="${esc(t)}">${esc(t)}</button>`).join('')}</div>`;
    const card = host.closest('.lv-q');
    if (picked.length) {
      if (card && !card.classList.contains('answered')) {
        card.classList.add('answered');
        const head = card.querySelector('.lv-qh');
        if (head && !head.querySelector('.lv-tick')) {
          const tick = document.createElement('span');
          tick.className = 'lv-tick';
          tick.setAttribute('role', 'img');
          tick.setAttribute('aria-label', 'answered');
          tick.innerHTML = TICK;
          head.append(tick);
        }
      }
    }
    refreshProgress();
  }

  function refreshProgress() {
    if (view !== 'test') return;
    const a = attemptState();
    const ids = partIds(doc, a.part);
    const total = ids.length;
    const answered = ids.filter((id) => hasAnswer(a, id)).length;
    const track = body().querySelector('[data-track]');
    const count = body().querySelector('[data-count]');
    const hint = body().querySelector('[data-hint]');
    if (track) track.style.width = (total ? Math.round(answered / total * 100) : 0) + '%';
    if (count) count.textContent = `${answered} of ${total} answered`;
    if (hint && !warned) hint.textContent = `${answered} of ${total} in this part`;
  }

  function startTicker(btn) {
    const wrap = btn.parentElement;
    const out = wrap.querySelector('.lv-timer');
    const num = out.querySelector('b');
    if (ticker) clearInterval(ticker);
    tickLeft = 30;
    out.hidden = false;
    btn.classList.add('on');
    const tick = () => {
      num.textContent = tickLeft + 's';
      if (tickLeft-- <= 0) {
        clearInterval(ticker); ticker = null;
        btn.classList.remove('on');
        btn.textContent = 'Run it again';
        num.textContent = 'done';
      }
    };
    tick();
    ticker = setInterval(tick, 1000);
  }

  function bind() {
    const wrap = body();
    if (wrap.dataset.ready) return;
    wrap.dataset.ready = '1';

    wrap.addEventListener('change', (e) => {
      const input = e.target;
      const a = attemptState();
      if (input.matches('input[data-answer]')) {
        a.answers[input.dataset.answer] = Number(input.value);
        const card = input.closest('.lv-q');
        card.querySelectorAll('.lv-opt').forEach((label) => {
          label.classList.toggle('on', label.contains(input));
        });
        markCard(input.dataset.answer);
        saveAttempt();
        refreshProgress();
      } else if (input.matches('input[data-rating]')) {
        const id = input.dataset.rating;
        const item = doc.items.find((it) => it.id === id);
        a.practice[item.skill] = a.practice[item.skill] || {};
        a.practice[item.skill][id] = Object.assign({}, a.practice[item.skill][id],
          {rating: Number(input.value)});
        const card = input.closest('.lv-q');
        card.querySelectorAll('.lv-opt').forEach((label) => {
          label.classList.toggle('on', label.contains(input));
        });
        markCard(id);
        saveAttempt();
      }
    });

    wrap.addEventListener('input', (e) => {
      const a = attemptState();
      if (e.target.matches('[data-typed]')) {
        a.answers[e.target.dataset.typed] = e.target.value;
        const card = e.target.closest('.lv-q');
        if (e.target.value.trim()) markCard(e.target.closest('.lv-q').id.replace('lvq-', ''));
        else {
          card.classList.remove('answered');
          const tick = card.querySelector('.lv-tick');
          if (tick) tick.remove();
        }
        saveAttempt();
        refreshProgress();
      } else if (e.target.matches('[data-practice]')) {
        const id = e.target.dataset.practice;
        const item = doc.items.find((it) => it.id === id);
        a.practice[item.skill][id] = a.practice[item.skill][id] || {};
        a.practice[item.skill][id].text = e.target.value;
        saveAttempt();
        /* A marked answer shows its marks while it is written, not after the
           paper is handed in: the point of a rubric is that the learner can
           act on it in the next sentence. */
        if (item.skill === 'writing') {
          const host = wrap.querySelector('[data-mark="' + id + '"]');
          if (host) {
            host.innerHTML = markChips(markWriting(doc, item, e.target.value),
                                       (doc.writingScale || {})[item.band] || {words: 30, sentences: 3});
          }
          const written = writingIds(doc).filter((tid) => {
            const pick = (a.practice.writing || {})[tid] || {};
            return String(pick.text || '').trim().length > 0;
          }).length;
          const count = wrap.querySelector('[data-wcount]');
          if (count) count.textContent = `${written} of ${writingIds(doc).length} written`;
          const track = wrap.querySelector('[data-wtrack]');
          if (track) {
            track.style.width = Math.round(written / writingIds(doc).length * 100) + '%';
          }
        }
      }
    });

    wrap.addEventListener('click', (e) => {
      const rec = e.target.closest('[data-rec]');
      if (rec) {
        const item = doc.items.find((it) => it.id === rec.dataset.rec);
        if (item && item.say) {
          rec.classList.add('on');
          Speech.speak(item.say, () => rec.classList.remove('on'));
        }
        return;
      }

      const timerBtn = e.target.closest('[data-timer]');
      if (timerBtn) { startTicker(timerBtn); return; }

      const add = e.target.closest('[data-add]');
      if (add) {
        const a = attemptState();
        const id = add.dataset.add;
        const cur = Array.isArray(a.answers[id]) ? a.answers[id] : [];
        a.answers[id] = cur.concat(add.dataset.token);
        saveAttempt();
        paintCompose(id);
        return;
      }

      const pick = e.target.closest('[data-pick]');
      if (pick) {
        const a = attemptState();
        const id = pick.dataset.pick;
        const cur = Array.isArray(a.answers[id]) ? a.answers[id] : [];
        a.answers[id] = cur.filter((_, k) => k !== Number(pick.dataset.k));
        saveAttempt();
        paintCompose(id);
        return;
      }

      const act = e.target.closest('[data-act]');
      if (!act) return;
      const kind = act.dataset.act;
      if (kind === 'start') start(false);
      else if (kind === 'restart') start(true);
      else if (kind === 'pause') { saveAttempt(true); view = 'intro'; render(); }
      else if (kind === 'part') nextPart();
      else if (kind === 'finish') finish();
      else if (kind === 'result') { view = 'result'; render(); }
      else if (kind === 'certificate') {
        const result = read(KEY.result, null);
        if (!result) return;
        const band = doc.bands.find((b) => b.id === bandKey(result.overall)) || doc.bands[0];
        Cert.open({
          name: (Auth.profile() || {}).name || 'Fluentify learner',
          band: result.overall,
          label: band.name.en,
          labelFa: band.name.fa,
          can: band.can.en,
          at: result.at,
          /* The size of the assessment, not the number this run answered: a
             certificate that says "36 questions" because a part was skipped
             describes the attempt, not the test. */
          questions: result.paper || doc.blueprint.questions || result.total || result.questions,
          answered: result.questions,
          minutes: result.minutes,
          completion: result.completion,
        });
      }
      else if (kind === 'intro') { view = 'intro'; render(); }
      /* The speaking tasks are practice, so they are opened from the report
         rather than forced into the paper. */
      else if (kind === 'practice') {
        view = 'practice'; render(); body().scrollIntoView({block: 'start'});
      }
      else if (kind === 'open') {
        const target = act.dataset.panel;
        /* Writing lives inside this panel, so it is a view change rather than
           a panel switch - toggling here would close the panel the learner is
           standing in. */
        if (target === 'writing') {
          view = 'writing'; render(); body().scrollIntoView({block: 'start'});
          return;
        }
        togglePanel('lvlpanel', 'lvltoggle');
        if (target === 'stories') {
          togglePanel('stpanel', 'stoggle');
          Stories.openLevel({A1: 'VE', A2: 'E', B1: 'M', B2: 'H', C1: 'VH'}[act.dataset.band] || 'all');
        } else {
          const map = {grammar: ['gpanel', 'gtoggle'], vocab: ['vpanel', 'vtoggle'],
                       listen: ['lpanel', 'ltoggle'], say: ['fpanel', 'ftoggle']};
          const pair = map[target];
          if (pair) togglePanel(pair[0], pair[1]);
        }
      }
    });

    /* Keys for a paper of this length: 1-4 answers the question in focus, or
       the next unanswered one. Ignored while typing. */
    document.addEventListener('keydown', (e) => {
      const panel = document.getElementById('lvlpanel');
      if (view !== 'test' || !panel || !panel.classList.contains('open')) return;
      if (e.target.matches('textarea, input')) return;
      if (!/^[1-4]$/.test(e.key)) return;
      const card = (document.activeElement && document.activeElement.closest('.lv-q')) ||
        wrap.querySelector('.lv-q:not(.answered)');
      if (!card) return;
      const box = card.querySelectorAll('input[data-answer]')[Number(e.key) - 1];
      if (!box) return;
      e.preventDefault();
      box.checked = true;
      box.dispatchEvent(new Event('change', {bubbles: true}));
      card.scrollIntoView({block: 'nearest'});
    });

    /* The soft keyboard takes half the screen, and the box the learner is
       typing in was left under it: the paper looked empty with only the
       keyboard in view. A box that takes focus brings its own question back
       to the top of the panel, above the keyboard rather than behind it. */
    document.addEventListener('focusin', (e) => {
      const card = e.target.closest && e.target.closest('.lv-q');
      if (!card) return;
      setTimeout(() => {
        try { card.scrollIntoView({block: 'start', behavior: 'smooth'}); } catch (err) { /* old WebView */ }
      }, 260);
    });

    /* A throw inside a handler - a tap on an option, a keystroke in a box, a
       tap on the footer - never reaches the paint guard. If it leaves the
       panel with nothing in it, draw the paper again rather than showing a
       blank sheet. Once, so a repeat failure cannot spin. */
    if (!healed) {
      healed = true;
      const heal = () => {
        const panel = document.getElementById('lvlpanel');
        const host = body();
        if (!panel || !panel.classList.contains('open') || !host) return;
        if (host.childElementCount) return;
        console.error('level: the panel was emptied outside a paint');
        try { render(); } catch (err) { fallbackSheet(); }
      };
      window.addEventListener('error', heal);
      window.addEventListener('unhandledrejection', heal);
    }
  }

  async function mount() {
    bind();
    if (!doc) {
      pending ||= loadJSON('level_test').then((d) => { doc = d; return d; });
      body().innerHTML = `<div class="lv-wrap"><section class="lv-hero">
        <div class="lv-eyebrow">Level assessment</div>
        <h2 class="lv-h">Loading the questions…</h2>
        ${faLine('پرسش‌ها در حال بارگذاری‌اند…')}
      </section></div>`;
      try {
        await pending;
      } catch (e) {
        console.error('level:', e);
        body().innerHTML = `<div class="lv-wrap"><section class="lv-hero">
          <h2 class="lv-h">The assessment could not be loaded</h2>
          <p class="lv-sub">The question bank is missing from this build.</p>
          ${faLine('بانک پرسش‌ها در این نسخه نیست.')}
        </section></div>`;
        pending = null;
        return;
      }
    }
    attemptState();
    if (state && state.part >= partCount(doc)) view = 'writing';
    render();
  }

  return {
    mount, paintBadge, compute, blankAttempt, paper, partIds, partCount,
    writingIds, markWriting, writingResult,
    levelFromCorrect, isCorrect, normalise,
    reset() {
      try {
        localStorage.removeItem(KEY.result);
        localStorage.removeItem(KEY.attempt);
        localStorage.removeItem(KEY.history);
        localStorage.removeItem(KEY.items);
      } catch (e) { /* private */ }
      state = null; view = 'intro'; paintBadge();
      if (doc && document.getElementById('lvlbody').dataset.ready) render();
    },
  };
})();

/* ==========================================================================
   Account, session and certificate.

   Fluentify runs offline, so there is no server to hold a password. What it
   can do honestly is keep the credential on the device: a random salt and a
   PBKDF2-SHA256 hash of the password (150,000 iterations), never the password
   itself, and a session that stays open for seven days after the last time
   the app was used. The overlay sits under the boot screen, so signing in is
   the first thing after loading and never in front of a spinner.

   What this is not: an account that follows you to another device, or one
   that can be recovered by email. Both limits are written on the card, because
   a learner who thinks this is a server login will one day lose a password and
   blame the app.
   ==========================================================================*/
/* ---- appearance ---------------------------------------------------------
   Two themes, one switch, and the switch lives where the learner's settings
   already live. The mechanism is deliberately small: the whole palette is
   custom properties, so a theme is one attribute on <html>, and every rule
   downstream of it - including the ones written months ago - follows without
   knowing a theme exists.

   What is stored is the *choice*, not the resolved colour: "dark" stays dark
   after the device switches to light at sunrise, which is what someone who
   picked a theme is asking for. A learner who has never chosen gets whatever
   the device is set to, and gets it without a flash (the head script). */
const Theme = (() => {
  const KEY = 'fluentify.theme';
  const META = {light: '#f7f1e0', dark: '#12141a'};

  function current() {
    return document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light';
  }

  function paint() {
    const now = current();
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', META[now]);
    /* The header tile is a switch, not a panel button: it says which theme is
       on, and it works whether or not there is an account to open. */
    const tile = document.getElementById('themetoggle');
    if (tile) {
      const dark = now === 'dark';
      tile.setAttribute('aria-pressed', dark ? 'true' : 'false');
      tile.title = dark ? 'Theme: dark — tap for light / پوستهٔ تیره' :
        'Theme: light — tap for dark / پوستهٔ روشن';
    }
  }

  /* `remember` is false for the first paint, which is applying a decision that
     was already made - writing it back would turn "follow the device" into "this
     device chose light" on the very first visit. */
  function apply(name, remember) {
    const next = name === 'dark' ? 'dark' : 'light';
    document.documentElement.dataset.theme = next;
    if (remember) {
      try { localStorage.setItem(KEY, next); } catch (e) {}
    }
    paint();
    document.dispatchEvent(new CustomEvent('fluentify:theme', {detail: {theme: next}}));
    return next;
  }

  function init() {
    paint();
    /* The head script already set the attribute; this keeps the control honest
       if the page was cached with a different attribute. */
    return apply(current(), false);
  }

  return {KEY, current, apply, init, paint};
})();

/* ==========================================================================
   How long the learner has studied.

   "Studied" here means the app was open and being used: a heartbeat adds
   fifteen seconds while the page is visible and something was touched in the
   last three minutes. A tab left open overnight therefore adds nothing after
   the first three minutes, and a phone in a pocket adds nothing at all - a
   timer that runs while nobody is looking would report a number that is not
   about learning.

   Kept per day, because the streak and the week's bars are the same data read
   two ways, and a day counts toward a streak once it holds a full minute.
   ==========================================================================*/
const Study = (() => {
  const KEY = 'fluentify.time.v1';
  const TICK = 15;          // seconds added per heartbeat
  const IDLE = 180;         // no input for three minutes = not studying
  const MIN_DAY = 60;       // a minute is what makes a day count
  let state = null, timer = null, last = Date.now();

  const dayKey = (when) => {
    const d = new Date(when);
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') +
      '-' + String(d.getDate()).padStart(2, '0');
  };

  function read() {
    try {
      const raw = localStorage.getItem(KEY);
      const s = raw ? JSON.parse(raw) : null;
      if (s && typeof s.total === 'number' && s.days && typeof s.days === 'object') {
        return {total: s.total, days: s.days};
      }
    } catch (e) { /* a corrupt record is simply a new one */ }
    return {total: 0, days: {}};
  }

  function save() {
    try {
      localStorage.setItem(KEY, JSON.stringify(
        {total: Math.round(state.total), days: state.days}));
    } catch (e) { /* private mode: the minutes just do not persist */ }
  }

  function add(sec) {
    if (!state) state = read();
    state.total += sec;
    const k = dayKey(Date.now());
    state.days[k] = Math.round((state.days[k] || 0) + sec);
    save();
  }

  function mount() {
    if (timer) return;
    state = read();
    ['pointerdown', 'keydown', 'wheel', 'touchstart'].forEach((evt) =>
      document.addEventListener(evt, () => { last = Date.now(); }, {passive: true}));
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) last = Date.now();
    });
    timer = setInterval(() => {
      if (document.hidden) return;
      if (Date.now() - last > IDLE * 1000) return;
      add(TICK);
    }, TICK * 1000);
  }

  function stats(now) {
    const s = state || (state = read());
    const t = now || Date.now();
    let streak = 0;
    for (let i = 0; i < 500; i++) {
      const d = new Date(t);
      d.setDate(d.getDate() - i);
      const sec = s.days[dayKey(d)] || 0;
      if (sec >= MIN_DAY) { streak++; continue; }
      if (i === 0) continue;      // today can still be earned before midnight
      break;
    }
    const week = [];
    for (let i = 6; i >= 0; i--) {
      const d = new Date(t);
      d.setDate(d.getDate() - i);
      week.push({sec: s.days[dayKey(d)] || 0, day: d.getDay()});
    }
    return {
      total: s.total,
      today: s.days[dayKey(t)] || 0,
      streak,
      week,
      activeDays: Object.keys(s.days).filter((k) => (s.days[k] || 0) >= MIN_DAY).length,
    };
  }

  function clear() {
    state = {total: 0, days: {}};
    save();
  }

  return {mount, stats, add, clear, KEY, dayKey};
})();

const Auth = (() => {
  const ACCOUNT = 'fluentify.auth.account';
  const SESSION = 'fluentify.auth.session';
  const DAYS = 7;
  const DAY = 86400000;
  const ITER = 150000;

  let account = null, session = null, tab = 'signin';
  let lastTouch = 0, confirmReset = false;

  const $ = (id) => document.getElementById(id);
  const read = (k, d) => {
    try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; }
    catch (e) { return d; }
  };
  const write = (k, v) => {
    try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* private */ }
  };
  const drop = (k) => { try { localStorage.removeItem(k); } catch (e) { /* private */ } };
  const esc = (s) => String(s == null ? '' : s)
    .replace(/[&<>"]/g, (c) => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));

  const b64 = (bytes) => btoa(String.fromCharCode.apply(null, Array.from(bytes)));
  const unb64 = (s) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0));

  const canHash = () => !!(window.crypto && crypto.subtle && crypto.getRandomValues);

  async function derive(password, salt, iterations) {
    const key = await crypto.subtle.importKey(
      'raw', new TextEncoder().encode(password), 'PBKDF2', false, ['deriveBits']);
    const bits = await crypto.subtle.deriveBits(
      {name: 'PBKDF2', salt: unb64(salt), iterations, hash: 'SHA-256'}, key, 256);
    return b64(new Uint8Array(bits));
  }

  const newSalt = () => {
    const a = new Uint8Array(16);
    crypto.getRandomValues(a);
    return b64(a);
  };

  /* ---- pure arithmetic, tested by tools/check_auth.py ------------------- */
  function sessionLeft(st, now) {
    return st && typeof st.seen === 'number' ? Math.max(0, st.seen + DAYS * DAY - now) : 0;
  }
  const isOpen = (st, now) => sessionLeft(st, now) > 0;

  /* ---- the password rule ------------------------------------------------
     Four requirements, and they are requirements rather than hints: eight
     characters at least, both cases, letters with digits, and one symbol from
     @#$%!. The blocklist below still runs on top, because a policy that only
     counts character classes is satisfied by "Password1!" - the first line of
     every cracking dictionary. The ceiling exists so a novel cannot stall the
     KDF; 128 is double the 64 a verifier is required to accept.

     One concession to the Persian half of the app: a password with no Latin
     letters cannot be mixed-case, because the script has no case at all. The
     case rule counts as met when there is no Latin to case, and every other
     rule still applies, so a Persian password is asked for a number and a
     symbol exactly like an English one. */
  const MIN_PASS = 8, MAX_PASS = 128;
  const SPECIAL = '@#$%!';
  const SPECIAL_RE = /[@#$%!]/;

  /* The rules in the order the card draws them: one segment of the meter and
     one line of the list each, so the bar and the ticks cannot disagree. */
  const RULES = [
    ['length', 'At least 8 characters'],
    ['case', 'Upper and lower case'],
    ['digits', 'Letters and numbers'],
    ['special', 'One of @ # $ % !'],
  ];

  function ruleCheck(pass) {
    const p = String(pass || '');
    const latin = /[A-Za-z]/.test(p);
    return {
      length: p.length >= MIN_PASS && p.length <= MAX_PASS,
      case: latin ? /[A-Z]/.test(p) && /[a-z]/.test(p) : p.length > 0,
      digits: /[A-Za-z\u0600-\u06FF]/.test(p) && /[0-9]/.test(p),
      special: SPECIAL_RE.test(p),
    };
  }

  /* An address, checked as far as it can be without a mail server: one @, a
     dotted domain, no spaces. Anything stricter rejects addresses that are
     legal, and anything looser accepts typos that make recovery impossible. */
  const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[A-Za-z]{2,}$/;
  function emailProblem(email) {
    const e = String(email || '').trim();
    if (!e) return ['Enter your email, so this account can be recovered.',
                    'ایمیلت را وارد کن تا این حساب قابل بازیابی باشد.'];
    if (e.length > 254) return ['That email is longer than any address can be.',
                                'این ایمیل از بلندترین نشانی ممکن هم بلندتر است.'];
    if (!EMAIL_RE.test(e)) return ['That does not look like an email address.',
                                   'این شکل یک نشانی ایمیل نیست.'];
    return null;
  }

  /* The passwords a cracker tries first. Short on purpose - a real blocklist
     is megabytes and this file ships offline - but it covers the shapes people
     reach for: the classics, their keyboard-walk cousins, and the padded ones
     ("password123456") that a length rule alone would wave through. Compared
     after folding: case, separators and the usual leet substitutions. */
  const WEAK_PASSWORDS = [
    'password', 'passw0rd', 'passwordpassword', 'qwerty', 'qwertyuiop',
    'letmein', 'welcome', 'iloveyou', 'admin', 'administrator', 'monkey',
    'dragon', 'sunshine', 'princess', 'football', 'baseball', 'superman',
    'trustnoone', 'abc123', 'abcdefghijk', '123456789012', '1234567890123',
    'qwertyuiopas', 'asdfghjklzxc', 'zxcvbnmasdf', 'correcthorsebattery',
    'changeme', 'secretpassword', 'mypassword', 'thisismypassword',
    'fluentify', 'iraniraniran', 'iran123456789', 'tehran1234567',
  ];

  /* One normal form for both jobs: lower-case, fold the substitutions that turn
     a blocked word into a "new" one, then drop everything that is not a letter
     or a digit. "@" becomes "a" before it can be stripped, which is the whole
     point - P@ssw0rd is a password, not a consonant cluster.
     A second form drops trailing digits, so "password1234" and
     "qwertyuiop2024" stop being different passwords. */
  function leetFold(pass) {
    let raw = String(pass).toLowerCase();
    /* A trailing run of digits is padding, not spelling - but only when a word
       is left behind it, so "123456789012" is still its own password. */
    const tail = raw.match(/\d{2,}$/);
    if (tail && raw.length - tail[0].length >= 3) raw = raw.slice(0, -tail[0].length);
    return raw
      .replace(/[0]/g, 'o').replace(/[1!|]/g, 'l').replace(/[3]/g, 'e')
      .replace(/[4@]/g, 'a').replace(/[5$]/g, 's').replace(/[7]/g, 't')
      .replace(/[^a-z0-9\u0600-\u06FF]/g, '');
  }
  function passForms(pass) {
    /* Three readings, because all three are real: the password as typed, the
       same with the padded digits off ("password123456"), and the folded one
       ("P@ssw0rd1234"). A blocked word is blocked in any of them. */
    const raw = String(pass).toLowerCase();
    const plain = raw.replace(/[^a-z0-9\u0600-\u06FF]/g, '');
    return [plain, plain.replace(/\d+$/, ''), leetFold(pass)];
  }

  function weakReason(pass, user, name) {
    const forms = passForms(pass);
    if (!forms[0]) return ['Choose a password, not punctuation.', 'یک گذرواژه انتخاب کن، نه فقط نشانه.'];
    for (const form of forms) {
      if (form && WEAK_PASSWORDS.indexOf(form) !== -1) {
        return ['That password is on every list a cracker tries first. Pick another.',
                'این گذرواژه در اولین فهرستی است که هر نفوذگر امتحان می‌کند؛ یکی دیگر انتخاب کن.'];
      }
    }
    if (/^(.)\1+$/.test(pass)) {
      return ['One repeated character is not a password.', 'یک نویسهٔ تکراری گذرواژه نیست.'];
    }
    const u = leetFold(user || '');
    if (u.length >= 3 && forms[0].indexOf(u) !== -1) {
      return ['Do not build the password out of your username.',
              'گذرواژه را از نام کاربری نساز.'];
    }
    const parts = String(name || '').toLowerCase().split(/\s+/)
      .map((w) => leetFold(w)).filter((w) => w.length >= 3);
    for (const part of parts) {
      if (forms[0].indexOf(part) !== -1) {
        return ['Do not build the password out of your name.',
                'گذرواژه را از نام خودت نساز.'];
      }
    }
    /* A run of one key is the other thing a length rule waves through:
       "aaaaaaaaaaaa" is caught above, "abcdabcdabcd" and "qwertyqwerty" here. */
    if (/^(.{2,6})\1+$/.test(pass)) {
      return ['A repeated pattern is easy to guess. Use a phrase instead.',
              'الگوی تکراری حدس‌زدنی است؛ یک عبارت به کار ببر.'];
    }
    return null;
  }

  /* 0-4 for the meter: one segment per requirement met, so the bar says the
     same thing as the tick list. Nothing here is a promise about entropy,
     which is why the top label says "strong", not "unbreakable". */
  function strength(pass, user, name) {
    const p = String(pass || '');
    const rules = ruleCheck(p);
    if (!p) {
      return {score: 0, label: 'Empty', labelFa: 'خالی', ok: false,
              weak: false, rules};
    }
    let score = RULES.filter(([key]) => rules[key]).length;
    const weak = weakReason(p, user, name);
    if (weak) score = 0;
    score = Math.max(0, Math.min(4, score));
    const labels = [['Too weak', 'بسیار ضعیف'], ['Weak', 'ضعیف'],
                    ['Fair', 'قابل قبول'], ['Good', 'خوب'], ['Strong', 'قوی']];
    /* A blocked password is not "too weak" - it can meet all four rules and
       still be the first thing a cracker tries - so the word has to say why. */
    if (weak) labels[0] = ['Too common', 'رایج'];
    return {score, label: labels[score][0], labelFa: labels[score][1],
            ok: !weak && score === 4, weak: !!weak, rules};
  }

  /* Everything the password has to satisfy, in one list of complaints, so the
     gate and the recovery screen cannot drift apart: resetting a forgotten
     password is no more allowed to be weaker than choosing one. */
  function passwordProblems(pass, user, name) {
    const errors = [];
    if (pass.length < MIN_PASS) {
      errors.push(['Password: at least ' + MIN_PASS + ' characters.',
                   'گذرواژه: دست‌کم ۸ نویسه.']);
      return errors;
    }
    if (pass.length > MAX_PASS) {
      errors.push(['Password: ' + MAX_PASS + ' characters at most.',
                   'گذرواژه: حداکثر ۱۲۸ نویسه.']);
      return errors;
    }
    const weak = weakReason(pass, user, name);
    if (weak) { errors.push(weak); return errors; }
    /* The message names the rule that is actually missing, because "use a
       stronger password" tells the learner nothing about which of the four
       bars is not met. */
    const rules = ruleCheck(pass);
    const missing = RULES.filter(([key]) => !rules[key]).map(([, text]) => text.toLowerCase());
    if (missing.length) {
      errors.push(['Password: also needs ' + missing.join(', ') + '.',
                   'گذرواژه باید حرف بزرگ و کوچک، حرف و رقم، و یکی از @#$%! را داشته باشد.']);
    }
    return errors;
  }

  function validate(fields, hasAccount) {
    const name = String(fields.name || '').trim().replace(/\s+/g, ' ');
    const user = String(fields.user || '').trim();
    const pass = String(fields.pass || '');
    const pass2 = String(fields.pass2 || '');
    const email = String(fields.email || '').trim();
    const errors = [];
    if (!hasAccount) {
      if (name.length < 2) errors.push(['Enter your full name.', 'نام و نام خانوادگی را وارد کن.']);
      /* No \p{L}: unicode property escapes throw at parse time on older
         WebViews, which would take the whole gate down. Digits are the only
         thing a name must not carry, and a name in any script must pass. */
      if (/[\d<>]/.test(name)) {
        errors.push(['The name cannot contain digits.', 'نام نمی‌تواند رقم داشته باشد.']);
      }
      const mail = emailProblem(email);
      if (mail) errors.push(mail);
    }
    if (!/^[a-zA-Z0-9._-]{3,32}$/.test(user)) {
      errors.push(['Username: 3–32 letters, digits, dot, dash or underscore.',
                   'نام کاربری: ۳ تا ۳۲ حرف یا رقم، نقطه، خط تیره یا زیرخط.']);
    }
    errors.push(...passwordProblems(pass, user, name));
    if (!hasAccount && pass !== pass2) {
      errors.push(['The two passwords do not match.', 'دو گذرواژه یکسان نیستند.']);
    }
    return {ok: errors.length === 0, errors, name, user, email, pass};
  }

  /* ---- the overlay ------------------------------------------------------ */
  function setTab(next) {
    tab = next;
    document.querySelectorAll('[data-authtab]').forEach((b) => {
      const on = b.dataset.authtab === tab;
      b.classList.toggle('on', on);
      b.setAttribute('aria-selected', on ? 'true' : 'false');
      if (b.dataset.authtab === 'signup') b.disabled = !!account;
    });
    /* One rule for every element that belongs to a single tab, so a new
       sign-in-only control cannot silently show up while signing up. */
    document.querySelectorAll('[data-only]').forEach((n) => {
      n.hidden = n.dataset.only !== tab;
    });
    $('authh').textContent = tab === 'signup' ? 'Create your account' : 'Welcome back';
    $('authsub').textContent = tab === 'signup'
      ? 'One account on this device, so your level and certificate have a name on them.'
      : 'Sign in to keep your level, your certificate and your place in the stories.';
    $('authsubmit').textContent = tab === 'signup' ? 'Create account' : 'Sign in';
    $('authpass').setAttribute('autocomplete', tab === 'signup' ? 'new-password' : 'current-password');
    const meter = $('authmeter');
    if (meter) meter.hidden = tab !== 'signup';
    paintStrength();
    error('');
  }

  /* The meter is the rule, drawn: same function the submit path calls, so the
     bar cannot say "strong" about something the button will refuse. */
  function paintRulesInto(id, res) {
    const list = $(id);
    if (!list) return;
    list.innerHTML = RULES.map(([key, text]) =>
      '<li class="authrule' + (res.rules[key] ? ' on' : '') + '">' +
      '<i aria-hidden="true">✓</i>' + text + '</li>').join('');
  }

  function paintStrength() {
    const meter = $('authmeter');
    if (!meter) return;
    const label = $('authlabel');
    const pass = $('authpass') ? $('authpass').value : '';
    const res = strength(pass, $('authuser') ? $('authuser').value : '',
                        $('authname') ? $('authname').value : '');
    meter.dataset.score = String(pass ? res.score : 0);
    paintRulesInto('authrules', res);
    if (!label) return;
    if (!pass) {
      label.innerHTML = '<b>Choose a password</b> — all four rules below have to tick.';
      return;
    }
    label.innerHTML = '<b>' + res.label + ' · ' + res.labelFa + '</b>' +
      '<bdi class="fa" dir="rtl" lang="fa">' +
      (res.ok ? 'خوب است؛ همین را نگه دار.'
              : res.weak ? 'این یکی در فهرست گذرواژه‌های رایج است؛ یکی دیگر بساز.'
              : 'قاعده‌ای که تیک نخورده باقی مانده است.') +
      '</bdi>';
  }

  function error(pair, ok) {
    const box = $('autherr');
    if (!box) return;
    if (!pair) { box.textContent = ''; box.classList.remove('ok'); return; }
    box.classList.toggle('ok', !!ok);
    box.innerHTML = `<div>${pair[0]}</div><div dir="rtl" lang="fa">${pair[1]}</div>`;
  }

  function show(nextTab, expired) {
    account = read(ACCOUNT, null) || account;
    $('auth').hidden = false;
    $('authexpired').hidden = !expired;
    setTab(account ? (nextTab || 'signin') : 'signup');
    $('authname').value = account ? account.name : '';
    $('authuser').value = account ? account.user : '';
    if ($('authemail')) $('authemail').value = account && account.email ? account.email : '';
    setTimeout(() => {
      const target = tab === 'signup' ? $('authname') : $('authuser');
      if (target) target.focus({preventScroll: true});
    }, 60);
  }

  function hide() {
    $('auth').hidden = true;
    $('authpass').value = '';
    if ($('authpass2')) $('authpass2').value = '';
    if ($('authpass')) $('authpass').type = 'password';
    const reveal = $('authreveal');
    if (reveal) { reveal.textContent = 'Show'; reveal.setAttribute('aria-pressed', 'false'); }
    paintStrength();
    error('');
    showReset(false);
  }

  function touch(force) {
    if (!session || !isOpen(session, Date.now())) return;
    const now = Date.now();
    if (!force && now - lastTouch < 60000) return;
    lastTouch = now;
    session.seen = now;
    write(SESSION, session);
  }

  /* ---- recovery ---------------------------------------------------------
     A forgotten password on a device-local account has one honest shape: the
     device already holds the account, so ownership is proved by knowing what
     the account is - its username and the address on it - and not by a link.
     The two steps are separated so the new password fields only appear once
     the first answer was right. */
  let resetStep = 0, resetWho = null;

  function resetError(pair) {
    const box = $('reseterr');
    if (!box) return;
    box.innerHTML = pair
      ? `<div>${pair[0]}</div><div dir="rtl" lang="fa">${pair[1]}</div>` : '';
  }

  function paintReset() {
    const meter = $('resetmeter');
    if (!meter) return;
    const pass = $('resetpass') ? $('resetpass').value : '';
    const res = strength(pass, resetWho ? resetWho.user : '', resetWho ? resetWho.name : '');
    meter.dataset.score = String(pass ? res.score : 0);
    paintRulesInto('resetrules', res);
  }

  function paintResetStep() {
    const second = resetStep === 1;
    ['resetnew', 'resetnew2'].forEach((id) => {
      const el = $(id);
      if (el) el.hidden = !second;
    });
    const meter = $('resetmeter');
    if (meter) meter.hidden = !second;
    ['resetuser', 'resetmail'].forEach((id) => {
      const el = $(id);
      if (el) el.disabled = second;
    });
    const btn = $('resetsubmit');
    if (btn) btn.textContent = second ? 'Set the new password' : 'Continue';
    const head = $('reseth');
    if (head) head.textContent = second ? 'Choose a new password' : 'Reset your password';
    const sub = $('resetsubtext');
    if (sub) {
      sub.textContent = second
        ? 'The four rules are the ones sign-up asks for; the salt is new, so the old hash is gone.'
        : 'Confirm what this device already knows about the account, then choose a new password. ' +
          'Nothing is sent anywhere — there is nowhere to send it.';
    }
    paintReset();
  }

  function showReset(on) {
    const box = $('authreset');
    if (!box) return;
    box.hidden = !on;
    $('authform').hidden = !!on;
    const tabs = document.querySelector('.authtabs');
    if (tabs) tabs.hidden = !!on;
    resetStep = 0;
    resetWho = null;
    ['resetuser', 'resetmail', 'resetpass', 'resetpass2'].forEach((id) => {
      const el = $(id);
      if (el) el.value = '';
    });
    resetError(null);
    paintResetStep();
    if (on) {
      const first = $('resetuser');
      if (first) setTimeout(() => first.focus({preventScroll: true}), 40);
    }
  }

  async function resetSubmit() {
    resetError(null);
    if (resetStep === 0) {
      const stored = read(ACCOUNT, null);
      if (!stored) {
        resetError(['There is no account on this device to recover.',
                    'روی این دستگاه حسابی برای بازیابی نیست.']);
        return;
      }
      const typedUser = String(($('resetuser') || {}).value || '').trim().toLowerCase();
      if (typedUser !== String(stored.user).toLowerCase()) {
        resetError(['That username is not the one saved here.',
                    'این نام کاربری با نام ذخیره‌شده یکی نیست.']);
        return;
      }
      /* The address, or the name for an account made before an email was
         asked for. Both are things only the owner of the account knows, and
         there is no server here that could verify anything stronger. */
      const typedMail = String(($('resetmail') || {}).value || '').trim().toLowerCase();
      const known = [stored.email, stored.name]
        .map((v) => String(v || '').trim().toLowerCase()).filter(Boolean);
      if (!typedMail || known.indexOf(typedMail) === -1) {
        resetError(['That is not the email on this account.',
                    'این نشانی، ایمیل این حساب نیست.']);
        return;
      }
      resetWho = stored;
      resetStep = 1;
      paintResetStep();
      const next = $('resetpass');
      if (next) setTimeout(() => next.focus({preventScroll: true}), 40);
      return;
    }

    const pass = $('resetpass').value;
    const pass2 = $('resetpass2').value;
    const problems = passwordProblems(pass, resetWho.user, resetWho.name);
    if (problems.length) { resetError(problems[0]); return; }
    if (pass !== pass2) {
      resetError(['The two passwords do not match.', 'دو گذرواژه یکسان نیستند.']);
      return;
    }
    if (!canHash()) {
      resetError(['This browser cannot store a password securely.',
                  'این مرورگر نمی‌تواند گذرواژه را امن نگه دارد.']);
      return;
    }
    const go = $('resetsubmit');
    const label = go ? go.textContent : '';
    if (go) { go.disabled = true; go.textContent = 'Working…'; }
    try {
      /* A new salt as well as a new hash: the old salt is what made the old
         hash checkable, so it does not survive the reset. */
      const salt = newSalt();
      const hash = await derive(pass, salt, ITER);
      const next = Object.assign({}, resetWho, {salt, hash, iter: ITER});
      write(ACCOUNT, next);
      account = next;
      session = {at: Date.now(), seen: Date.now(), user: next.user};
      write(SESSION, session);
      lastTouch = Date.now();
      showReset(false);
      hide();
      document.dispatchEvent(new CustomEvent('fluentify:signed-in', {detail: {name: next.name}}));
      if (document.getElementById('acbody')) paintAccount();
    } catch (err) {
      console.error('reset:', err);
      resetError(['Could not save the new password.',
                  'ذخیرهٔ گذرواژهٔ تازه انجام نشد.']);
    } finally {
      if (go) { go.disabled = false; go.textContent = label; }
    }
  }

  async function submit(e) {
    e.preventDefault();
    const submitBtn = $('authsubmit');
    const has = tab === 'signin';
    const fields = {
      name: $('authname').value,
      user: $('authuser').value,
      email: $('authemail') ? $('authemail').value : '',
      pass: $('authpass').value,
      pass2: $('authpass2').value,
    };
    const {ok, errors, name, user, email, pass} = validate(
      {name: fields.name, user: fields.user, email: fields.email,
       pass: fields.pass, pass2: fields.pass2}, has);
    if (!ok) { error(errors[0]); return; }

    if (!canHash()) {
      error(['This browser cannot store a password securely. Open Fluentify over https or localhost.',
             'این مرورگر نمی‌تواند گذرواژه را امن نگه دارد. برنامه را روی https یا localhost باز کن.']);
      return;
    }

    submitBtn.disabled = true;
    const label = submitBtn.textContent;
    submitBtn.textContent = 'Working…';
    try {
      if (has) {
        const stored = read(ACCOUNT, null);
        if (!stored) { error(['No account on this device yet. Create one.', 'هنوز حسابی روی این دستگاه نیست. یکی بساز.']); return; }
        if (stored.user.toLowerCase() !== user.toLowerCase()) {
          error(['That username is not the one saved here.', 'این نام کاربری با نام ذخیره‌شده یکی نیست.']);
          return;
        }
        const digest = await derive(pass, stored.salt, stored.iter || ITER);
        if (digest !== stored.hash) {
          error(['Wrong password. Passwords are case-sensitive.', 'گذرواژه نادرست است. گذرواژه به بزرگی و کوچکی حرف حساس است.']);
          return;
        }
        account = stored;
      } else {
        if (read(ACCOUNT, null)) {
          error(['An account already exists on this device. Sign in instead.',
                 'روی این دستگاه حسابی هست. به جای ساختن، وارد شو.']);
          return;
        }
        const salt = newSalt();
        const hash = await derive(pass, salt, ITER);
        account = {name, user, email, salt, hash, iter: ITER, at: new Date().toISOString()};
        write(ACCOUNT, account);
      }
      session = {at: Date.now(), seen: Date.now(), user: account.user};
      write(SESSION, session);
      lastTouch = Date.now();
      hide();
      document.dispatchEvent(new CustomEvent('fluentify:signed-in', {detail: {name: account.name}}));
      if (document.getElementById('acbody')) paintAccount();
    } catch (err) {
      console.error('auth:', err);
      error(['Could not save the account: ' + (err && err.message ? err.message : 'unknown error'),
             'ذخیرهٔ حساب انجام نشد.']);
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = label;
    }
  }

  function signOut() {
    drop(SESSION);
    session = null;
    show('signin', false);
  }

  function resetDevice() {
    if (!confirmReset) {
      confirmReset = true;
      const btn = $('acreset');
      if (btn) btn.textContent = 'Press again to erase this device';
      setTimeout(() => {
        confirmReset = false;
        if (btn) btn.textContent = 'Reset this device';
      }, 5000);
      return;
    }
    ['fluentify.auth.account', 'fluentify.auth.session',
     'fluentify.level.v2.result', 'fluentify.level.v2.history',
     'fluentify.level.v2.attempt', 'fluentify.level.items',
     AVATAR_KEY, Study.KEY].forEach(drop);
    Study.clear();
    account = null; session = null; confirmReset = false;
    hide();
    show('signup', false);
    applyAvatarSkin(avatarId());
    repaintAvatarTiles();
    if (document.getElementById('lvlbody')) Level.mount();
  }

  /* ---- the account panel ------------------------------------------------
     A profile is read before it is edited, so the panel opens on who the
     learner is and what the time in the app has bought, and everything that
     changes something sits below it: the face, the badges, the password, the
     appearance, then the session facts and the two doors out. */

  const ICONS = {
    seed: '<path d="M12 20.4V10"/><path d="M12 10C9.2 10 7 8.2 6.4 5.4 9.2 5 11.4 6.8 12 10Z"/><path d="M12 12.6c2.8 0 5-1.8 5.6-4.6-2.8.4-5 2.2-5.6 4.6Z"/>',
    clock: '<circle cx="12" cy="12" r="8.4"/><path d="M12 7.6V12l3 1.9"/>',
    moon: '<path d="M20 14.2A8.2 8.2 0 0 1 9.8 4a8.4 8.4 0 1 0 10.2 10.2Z"/>',
    flame: '<path d="M12 3.6c3.2 2.9 4.9 5.4 4.9 8.1a4.9 4.9 0 0 1-9.8 0c0-1.6.6-3.1 1.9-4.6.3 1.2.8 2 1.6 2.4.5-1.9.9-3.8 1.4-5.9Z"/>',
    flag: '<path d="M6.6 20V4.6"/><path d="M6.6 5.4c3.9-1.9 7 1.9 10.8 0v6.9c-3.8 1.9-6.9-1.9-10.8 0Z"/>',
    book: '<path d="M4.6 5.8c2.7-.8 5-.3 7.4 1.1 2.4-1.4 4.7-1.9 7.4-1.1v12c-2.7-.8-5-.3-7.4 1.1-2.4-1.4-4.7-1.9-7.4-1.1Z"/><path d="M12 6.9v12"/>',
    star: '<path d="M12 3.9l2.4 5 5.5.8-4 3.9 1 5.5-4.9-2.6-4.9 2.6 1-5.5-4-3.9 5.5-.8Z"/>',
    medal: '<circle cx="12" cy="14.4" r="4.5"/><path d="M8.7 3.8l1.9 4.8M15.3 3.8l-1.9 4.8"/>',
  };

  /* Says so once, right after the change lands; cleared by the next paint. */
  let passNotice = '';

  function fmtDur(sec) {
    const m = Math.round((sec || 0) / 60);
    if (m < 60) return m + 'm';
    const h = Math.floor(m / 60), r = m % 60;
    return r ? h + 'h ' + r + 'm' : h + 'h';
  }

  function savedWords() {
    try {
      const raw = localStorage.getItem('fluentify.review');
      const list = raw ? JSON.parse(raw) : [];
      return Array.isArray(list) ? list.length : 0;
    } catch (e) { return 0; }
  }

  function levelBand() {
    try {
      const raw = localStorage.getItem('fluentify.level.v2.result');
      const r = raw ? JSON.parse(raw) : null;
      return r && r.overall ? String(r.overall) : '';
    } catch (e) { return ''; }
  }

  /* Every badge is a number this device already keeps, never a reward for
     pressing a button: minutes studied, days in a row, words saved, and the
     band the assessment last reported. A badge that cannot be reached by
     learning would be decoration. */
  function achievements(study) {
    const words = savedWords();
    const band = levelBand();
    const rank = {'Pre-A1': 0, A1: 1, A2: 2, B1: 3, B2: 4, C1: 5};
    return [
      {icon: 'seed',  en: 'First five minutes', fa: 'نخستین پنج دقیقه', got: study.total, goal: 300, time: true},
      {icon: 'clock', en: 'One hour studied', fa: 'یک ساعت مطالعه', got: study.total, goal: 3600, time: true},
      {icon: 'moon',  en: 'Five hours studied', fa: 'پنج ساعت مطالعه', got: study.total, goal: 18000, time: true},
      {icon: 'flame', en: 'Three days running', fa: 'سه روز پیاپی', got: study.streak, goal: 3},
      {icon: 'flag',  en: 'A week of habit', fa: 'یک هفته پیوستگی', got: study.streak, goal: 7},
      {icon: 'book',  en: '25 words saved', fa: '۲۵ واژهٔ ذخیره‌شده', got: words, goal: 25},
      {icon: 'star',  en: 'Level checked', fa: 'سنجش سطح', got: band ? 1 : 0, goal: 1},
      {icon: 'medal', en: 'Reached B1', fa: 'رسیدن به B1', got: rank[band] || 0, goal: 3},
    ];
  }

  function badgeHTML(a) {
    const done = a.got >= a.goal;
    const got = Math.min(a.got, a.goal);
    const pct = Math.max(0, Math.min(100, Math.round((got / a.goal) * 100)));
    const now = a.time ? fmtDur(got) : String(got);
    const goal = a.time ? fmtDur(a.goal) : String(a.goal);
    const foot = done
      ? '<span class="ac-earned">Earned</span>'
      : `<span class="ac-prog"><i style="width:${pct}%"></i></span><span class="ac-pct">${now} / ${goal}</span>`;
    return `<div class="ac-badge${done ? ' on' : ''}">
      <svg viewBox="0 0 24 24" aria-hidden="true">${ICONS[a.icon] || ''}</svg>
      <div><b>${a.en}</b><i lang="fa" dir="rtl">${a.fa}</i>${foot}</div></div>`;
  }

  function paintAccount() {
    const body = $('acbody');
    if (!body) return;
    /* Repainting replaces every node in the panel, and a replaced panel starts
       at its top: picking a face three rows down threw the learner back to the
       name they had already read. Where the panel was standing is part of what
       the panel showed. */
    const panel = document.getElementById('acpanel');
    const keep = panel ? panel.scrollTop : 0;
    account = read(ACCOUNT, null) || account;
    session = read(SESSION, null) || session;
    if (!account) {
      body.innerHTML = `<p class="lv-sub">No account on this device.</p>
        <div class="ac-actions"><button class="lv-btn" data-ac="open">Create one</button></div>`;
      return;
    }
    const study = Study.stats();
    const band = levelBand();
    const face = avatarId();
    const left = sessionLeft(session, Date.now());
    const days = Math.ceil(left / DAY);
    const signed = session ? new Date(session.seen) : null;
    const peak = Math.max(60, ...study.week.map((d) => d.sec));
    const LETTERS = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
    const week = study.week.map((d) => {
      const h = Math.max(4, Math.round((d.sec / peak) * 100));
      return `<div class="ac-bar${d.sec >= 60 ? ' on' : ''}" title="${fmtDur(d.sec)}">` +
        `<i style="height:${h}%"></i><span>${LETTERS[d.day]}</span></div>`;
    }).join('');
    const badges = achievements(study);
    const earned = badges.filter((a) => a.got >= a.goal).length;
    const faces = Object.keys(AVATARS).map((id) =>
      `<button class="ac-av${id === face ? ' on' : ''}" type="button" data-avatar="${id}" ` +
      `aria-pressed="${id === face}">${avatarSVG(id)}<b>${AVATARS[id].en}</b>` +
      `<i lang="fa" dir="rtl">${AVATARS[id].fa}</i></button>`).join('');

    body.innerHTML = `
      <section class="ac-hero">
        <div class="ac-face" data-ac="avatar-focus" role="img" aria-label="${AVATARS[face].en}">
          ${avatarSVG(face)}</div>
        <div class="ac-heroid">
          <p class="ac-name">${esc(account.name)}</p>
          <p class="ac-user">@${esc(account.user)} · joined ${new Date(account.at).toLocaleDateString(undefined, {day: 'numeric', month: 'short', year: 'numeric'})}</p>
          <span class="ac-mail">${esc(account.email || 'no email on this account')}</span>
        </div>
      </section>

      <div class="ac-stats">
        <div class="ac-stat"><b>${fmtDur(study.total)}</b><span>Studied<span class="fa" dir="rtl" lang="fa">مطالعه</span></span></div>
        <div class="ac-stat"><b>${fmtDur(study.today)}</b><span>Today<span class="fa" dir="rtl" lang="fa">امروز</span></span></div>
        <div class="ac-stat"><b>${study.streak}</b><span>Day streak<span class="fa" dir="rtl" lang="fa">روز پیاپی</span></span></div>
        <div class="ac-stat"><b>${esc(band || '—')}</b><span>Level<span class="fa" dir="rtl" lang="fa">سطح</span></span></div>
      </div>
      <div class="ac-week" aria-label="The last seven days">${week}</div>

      <div class="ac-block">
        <div class="ac-blockh"><b>Avatar — نمایه</b><small>${AVATARS[face].en}</small></div>
        <div class="ac-avatars">${faces}</div>
      </div>

      <div class="ac-block">
        <div class="ac-blockh"><b>Achievements — دستاوردها</b><small>${earned} of ${badges.length}</small></div>
        <div class="ac-badges">${badges.map(badgeHTML).join('')}</div>
      </div>

      <div class="ac-block">
        <div class="ac-blockh"><b>What keeps slipping — اشتباه‌های تکرارشده</b>
          <small>${ErrorLog.total(ErrorLog.read())} misses</small></div>
        <div id="acslip">${Slip.html()}</div>
      </div>

      <label class="authfield"><span>Name on the certificate — نام روی گواهی</span>
        <input id="acname" type="text" maxlength="60" value="${esc(account.name)}"></label>
      <div class="ac-actions" style="margin:0 0 10px">
        <button class="lv-btn" data-ac="save">Save name</button>
      </div>

      <div class="ac-block">
        <div class="ac-blockh"><b>Password — گذرواژه</b><small>the same four rules as sign-up</small></div>
        <form class="ac-pass" id="acpass" autocomplete="off">
          <label class="authfield"><span>Current password — گذرواژهٔ کنونی</span>
            <input id="acpass0" type="password" data-secret autocomplete="current-password"></label>
          <label class="authfield"><span>New password — گذرواژهٔ تازه</span>
            <input id="acpass1" type="password" data-secret autocomplete="new-password"></label>
          <div class="authrules" id="acpassrules" aria-live="polite"></div>
          <label class="authfield"><span>Repeat the new password — تکرار گذرواژهٔ تازه</span>
            <input id="acpass2" type="password" data-secret autocomplete="new-password"></label>
          <div class="ac-actions"><button class="lv-btn" type="submit">Change password</button></div>
          <p class="ac-passerr" id="acpasserr" role="alert" hidden></p>
          ${passNotice ? `<p class="ac-ok">${passNotice}</p>` : ''}
        </form>
      </div>

      <div class="ac-rows" style="margin-top:10px">
        <div class="ac-row"><span>Email</span><b>${esc(account.email || '—')}</b></div>
        <div class="ac-row"><span>Session</span><b>${left > 0 ? `open · ${days} day${days === 1 ? '' : 's'} left` : 'expired'}</b></div>
        <div class="ac-row"><span>Last used</span><b>${signed ? signed.toLocaleString(undefined, {day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit'}) : '—'}</b></div>
        <div class="ac-row"><span>Studied on</span><b>${study.activeDays} day${study.activeDays === 1 ? '' : 's'}</b></div>
        <div class="ac-row"><span>Stored</span><b>on this device only</b></div>
      </div>
      <div class="ac-actions" style="margin-top:10px">
        <button class="lv-btn ghost" data-ac="signout">Sign out</button>
        <button class="ac-danger" data-ac="reset">Reset this device</button>
      </div>
      <p class="authnote">Signing out keeps the account; resetting erases it, the level results, the
        certificate history, the study time and the chosen avatar from this device.</p>`;
    Theme.paint();
    if (panel && keep) panel.scrollTop = keep;
  }

  /* ---- changing the password from inside the panel -----------------------
     The same rule set as the gate, a fresh salt, and the current password
     asked for first: an unlocked phone should not be enough to lock its owner
     out of their own account. */
  function passError(pair) {
    const box = $('acpasserr');
    if (!box) return;
    box.hidden = !pair;
    box.innerHTML = pair
      ? `<div>${pair[0]}</div><div dir="rtl" lang="fa">${pair[1]}</div>` : '';
  }

  async function changePassword() {
    const cur = $('acpass0') ? $('acpass0').value : '';
    const next = $('acpass1') ? $('acpass1').value : '';
    const again = $('acpass2') ? $('acpass2').value : '';
    const stored = read(ACCOUNT, null);
    if (!stored) return;
    passError(null);
    if (!canHash()) {
      passError(['This browser cannot hash a password, so nothing was changed.',
                 'این مرورگر نمی‌تواند گذرواژه را ذخیره کند؛ چیزی تغییر نکرد.']);
      return;
    }
    if (!cur) {
      passError(['Type the password you are using now.', 'گذرواژهٔ کنونی را بنویسید.']);
      return;
    }
    const digest = await derive(cur, stored.salt, stored.iter || ITER);
    if (digest !== stored.hash) {
      passError(['That is not the current password.', 'این گذرواژهٔ کنونی نیست.']);
      return;
    }
    const problems = passwordProblems(next, stored.user, stored.name);
    if (problems.length) { passError(problems[0]); return; }
    if (next !== again) {
      passError(['The two new passwords do not match.', 'دو گذرواژهٔ تازه یکی نیستند.']);
      return;
    }
    const salt = newSalt();
    const hash = await derive(next, salt, ITER);
    write(ACCOUNT, Object.assign({}, stored, {salt, hash, iter: ITER}));
    account = read(ACCOUNT, null);
    passNotice = 'Password changed — گذرواژه عوض شد.';
    paintAccount();
    passNotice = '';
  }

  function bind() {
    const overlay = $('auth');
    if (!overlay || overlay.dataset.ready) return;
    overlay.dataset.ready = '1';
    $('authform').addEventListener('submit', submit);
    ['authpass', 'authpass2', 'authuser', 'authname', 'authemail'].forEach((id) => {
      const el = $(id);
      if (el) el.addEventListener('input', paintStrength);
    });
    /* A password is typed, never carried in from a clipboard and never carried
       out: paste, cut, copy, drop and the context menu are all refused on the
       secret fields, and the CSS keeps the text from being swept as well.
       preventDefault() rather than return false, so the listener stays passive
       where the browser allows it. */
    /* Delegated to the document and listened for on the way down, because the
       password fields in the account panel are painted long after this runs: a
       per-field binding made at boot would have left those three fields happy
       to accept a paste. */
    ['paste', 'cut', 'copy', 'drop', 'dragover', 'contextmenu'].forEach((evt) =>
      document.addEventListener(evt, (e) => {
        const field = e.target && e.target.closest ? e.target.closest('[data-secret]') : null;
        if (field) e.preventDefault();
      }, true));
    const reveal = $('authreveal');
    if (reveal) {
      reveal.addEventListener('click', () => {
        const box = $('authpass');
        const showing = box.type === 'text';
        box.type = showing ? 'password' : 'text';
        reveal.textContent = showing ? 'Show' : 'Hide';
        reveal.setAttribute('aria-pressed', showing ? 'false' : 'true');
        reveal.setAttribute('aria-label', showing ? 'Show password' : 'Hide password');
      });
    }
    /* Recovery is a second face of the same card, so it is bound here rather
       than as a modal of its own. */
    const resetOpen = $('resetopen');
    if (resetOpen) resetOpen.addEventListener('click', () => showReset(true));
    const resetBack = $('resetback');
    if (resetBack) resetBack.addEventListener('click', () => { showReset(false); setTab('signin'); });
    const resetGo = $('resetsubmit');
    if (resetGo) resetGo.addEventListener('click', resetSubmit);
    ['resetpass', 'resetpass2'].forEach((id) => {
      const el = $(id);
      if (el) el.addEventListener('input', paintReset);
    });
    const resetReveal = $('resetreveal');
    if (resetReveal) {
      resetReveal.addEventListener('click', () => {
        const box = $('resetpass');
        const showing = box.type === 'text';
        box.type = showing ? 'password' : 'text';
        resetReveal.textContent = showing ? 'Show' : 'Hide';
        resetReveal.setAttribute('aria-pressed', showing ? 'false' : 'true');
        resetReveal.setAttribute('aria-label', showing ? 'Show password' : 'Hide password');
      });
    }
    document.querySelectorAll('[data-authtab]').forEach((b) => {
      b.addEventListener('click', () => { if (!b.disabled) setTab(b.dataset.authtab); });
    });
    /* Delegated, because paintAccount() replaces the panel's markup: binding
       the buttons once at boot bound the ones that were about to be thrown
       away, and every action in the account panel was silently dead. */
    const accountBody = $('acbody');
    if (accountBody) {
      accountBody.addEventListener('click', (e) => {
        const face = e.target.closest('[data-avatar]');
        if (face) {
          const id = face.dataset.avatar;
          if (AVATARS[id]) {
            try { localStorage.setItem(AVATAR_KEY, id); } catch (err) { /* private */ }
            applyAvatarSkin(id);
            repaintAvatarTiles();
            paintAccount();
          }
          return;
        }
        const b = e.target.closest('[data-ac]');
        if (!b) return;
        const act = b.dataset.ac;
        if (act === 'avatar-focus') {
          const pick = accountBody.querySelector('.ac-av.on') || accountBody.querySelector('.ac-av');
          if (pick) {
            pick.scrollIntoView({block: 'nearest'});
            pick.focus({preventScroll: true});
          }
        }
        else if (act === 'signout') signOut();
        else if (act === 'reset') resetDevice();
        else if (act === 'open') show('signup', false);
        else if (act === 'save') {
          const input = $('acname');
          const name = input.value.trim().replace(/\s+/g, ' ');
          if (name.length < 2) { input.focus(); return; }
          account = read(ACCOUNT, null);
          account.name = name;
          write(ACCOUNT, account);
          paintAccount();
        }
      });
      /* The password form is replaced on every paint, so its input and submit
         are delegated to the panel rather than bound to the fields. */
      accountBody.addEventListener('input', (e) => {
        if (!e.target || e.target.id !== 'acpass1') return;
        const acc = read(ACCOUNT, null);
        const res = strength(e.target.value, acc ? acc.user : '', acc ? acc.name : '');
        paintRulesInto('acpassrules', res);
        passError(null);
      });
      accountBody.addEventListener('submit', (e) => {
        if (!e.target || e.target.id !== 'acpass') return;
        e.preventDefault();
        changePassword();
      });
    }
    /* The session clock is "seven days since you last used it", so use counts:
       a tap, a key, a panel opened, the tab coming back into view. */
    ['pointerdown', 'keydown'].forEach((evt) =>
      document.addEventListener(evt, () => touch(false), {passive: true}));
    document.addEventListener('visibilitychange', () => { if (!document.hidden) touch(true); });
    window.addEventListener('pagehide', () => touch(true));
    setInterval(() => {
      if (!session) return;
      if (!isOpen(session, Date.now())) {
        session = null;
        drop(SESSION);
        if ($('auth').hidden) show('signin', true);
      }
    }, 30000);
  }

  function init() {
    bind();
    account = read(ACCOUNT, null);
    session = read(SESSION, null);
    if (!account) { show('signup', false); return; }
    if (!isOpen(session, Date.now())) { show('signin', !!session); return; }
    hide();
    touch(true);
  }

  return {
    init, touch, paintAccount, signOut, resetDevice,
    sessionLeft, isOpen, validate, strength, MIN_PASS,
    emailProblem, ruleCheck, RULES, SPECIAL,
    passwordProblems,
    profile: () => read(ACCOUNT, null),
    signedIn: () => isOpen(read(SESSION, null), Date.now()),
  };
})();

/* ==========================================================================
   The certificate. Rendered on the page, printed by the platform's own print
   path: window.print() on the web, PrintManager in the APK. No PDF library
   and no canvas screenshot, so the text stays text and the layout stays the
   one on screen.
   ==========================================================================*/
const Cert = (() => {
  let current = null;

  const esc = (s) => String(s == null ? '' : s)
    .replace(/[&<>"]/g, (c) => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));

  function code(text) {
    let h = 2166136261;
    for (let i = 0; i < text.length; i++) {
      h ^= text.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return (h >>> 0).toString(36).toUpperCase().padStart(6, '0').slice(0, 6);
  }

  function ident(data) {
    const d = new Date(data.at);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    return `FL-${d.getFullYear()}${month}${day}-${code(data.name + '|' + data.band + '|' + data.at)}`;
  }

  /* Who signs the sheet, and the office the signature stands for. One
     constant, so the hand at the start of the line and the printed name at the
     end of it can never drift apart. */
  const HEAD = {
    name: 'Ghazal Poortaghi',
    title: 'Head of Fluentify',
    titleFa: 'سرپرست فلوئنتیفای',
  };

  function render(data) {
    const id = ident(data);
    const date = new Date(data.at).toLocaleDateString(undefined,
      {day: 'numeric', month: 'long', year: 'numeric'});
    /* A run that skipped a part is not a smaller assessment; it is this
       attempt. The size comes from the bank, and the shortfall is stated rather
       than quietly printed as the size. */
    const asked = Number(data.questions) || 0;
    const answered = Number(data.answered) || 0;
    const short = asked && answered && answered < asked
      ? ` ${answered} of ${asked} questions were answered; the rest counted as wrong.` : '';
    return `
      <div class="certinner">
        <header class="certhead">
          <img src="brand/fox-mark.png" alt="" width="30" height="30">
          <div class="certword">
            <b>Fluentify</b>
            <span>Level assessment · سنجش سطح</span>
          </div>
          <div class="certseal" aria-hidden="true"><b>CEFR</b><span>self<br>assessed</span></div>
        </header>
        <div class="certbody">
          <p class="certkick">Certificate of level</p>
          <h2 class="certname" dir="auto">${esc(data.name)}</h2>
          <p class="certlead">has completed the Fluentify level assessment and reached</p>
          <div class="certband">
            <b>${esc(data.band || 'Pre-A1')}</b>
            <span>${esc(data.label)} · CEFR</span>
          </div>
          <p class="certline">${esc(data.can)}</p>
          <p class="certfa" dir="rtl" lang="fa">سطح ${esc(data.band || 'Pre-A1')} در چارچوب مرجع اروپایی (CEFR) — ${esc(data.labelFa || '')}</p>
        </div>
        <dl class="certfacts">
          <div><dt>Issued</dt><dd>${esc(date)}</dd></div>
          <div><dt>Assessment</dt><dd>${asked || '—'} questions · ${data.minutes} min</dd></div>
          <div><dt>Certificate ID</dt><dd>${esc(id)}</dd></div>
        </dl>
        <footer class="certfoot">
          <div class="certsign">
            <span class="certink" aria-hidden="true">${HEAD.name}</span>
            <span class="certsignrule"></span>
            <span class="certlab">Signature · <span class="fa" dir="rtl" lang="fa">امضا</span></span>
          </div>
          <div class="certwho">
            <span class="certsignrule"></span>
            <b>${HEAD.name}</b>
            <span class="certlab">${HEAD.title} · <span class="fa" dir="rtl" lang="fa">${HEAD.titleFa}</span></span>
          </div>
        </footer>
        <p class="certnote">Based on grammar, vocabulary, reading, listening and a marked writing task. Speaking was not assessed.${short}
          Self-assessment built on a reviewed item bank — not a certified examination.</p>
      </div>`;
  }

  function open(data) {
    current = data;
    const sheet = document.getElementById('certsheet');
    const wrap = document.getElementById('cert');
    if (!sheet || !wrap) return;
    sheet.innerHTML = render(data);
    wrap.hidden = false;
    document.getElementById('certpdf').focus({preventScroll: true});
  }

  function close() {
    const wrap = document.getElementById('cert');
    if (wrap) wrap.hidden = true;
  }

  function pdf() {
    /* Android has no window.print(); the WebView's print adapter does the
       same job and the same print stylesheet applies inside it. */
    if (window.AndroidPrint && typeof window.AndroidPrint.print === 'function') {
      try { window.AndroidPrint.print(); return; } catch (e) { /* fall through */ }
    }
    window.print();
  }

  function bind() {
    const wrap = document.getElementById('cert');
    if (!wrap || wrap.dataset.ready) return;
    wrap.dataset.ready = '1';
    wrap.addEventListener('click', (e) => {
      if (e.target === wrap) { close(); return; }
      const btn = e.target.closest('[data-cert]');
      if (!btn) return;
      if (btn.dataset.cert === 'close') close();
      if (btn.dataset.cert === 'pdf') pdf();
    });
  }

  return {open, close, pdf, bind, render, ident};
})();

/* only one panel open at a time; the active header button is highlighted */
function togglePanel(panelId, btnId) {
  // All of the book-keeping - the open class, the tile, aria-expanded, focus -
  // lives in Panels. This stays the entry point every caller already uses.
  Panels.toggle(panelId, PANEL_ON_OPEN[panelId]);
}

/* Panels that must rebuild their contents each time they are opened.
   Declared before togglePanel so the lookup is never undefined; the functions
   themselves are only called on click, long after they are defined. */
const PANEL_ON_OPEN = {
  // the day's three items: repaint on every open, because the date may have
  // moved on since the panel was last looked at (an overnight session)
  dpanel: () => Daily.refresh(true),
  // the analyser mounts its input handler and examples on first open, and
  // keeps whatever analysis is already on screen
  npanel: () => Analyser.mount(),
  rpanel: () => { Review.load(); Review.paint(); },
  // seven level spaces, one course and its examination: read path.json on the
  // first open, then paint the level list
  pathpanel: () => Path.open(),
  // search is attached on first open rather than at boot, because the panels
  // are filled asynchronously and a search with nothing to filter is useless
  gpanel: () => PanelSearch.attachAll(),
  // The word chips are the only consumer, and they are 302 KB. Fetch when the
  // panel is actually opened, then attach the search once there is something
  // to filter.
  fpanel: () => {
    loadPhrases().then(() => PanelSearch.attachAll());
    loadWordArch();
  },
  lpanel: () => PanelSearch.attachAll(),
  phpanel: () => PanelSearch.attachAll(),
  // the library loads its catalogue on first open, then remembers where the
  // reader was, so reopening the panel does not walk them back to the shelf
  bpanel: () => Books.load(),
  // six strategies and their questions, 83 KB, read on the first open
  rdpanel: () => Reading.mount(),
  // the story library is fetched the first time the panel opens
  stpanel: () => Stories.mount(),
  // the monthly level check: a banded item bank, read the first time it opens
  lvlpanel: () => Level.mount(),
  // the account panel is local: a name, a session clock, and the exit
  acpanel: () => Auth.paintAccount(),
  // the drills read their data on first open and then keep it
  prpanel: () => Practice.open(),
};
document.getElementById('dtoggle').onclick = () => togglePanel('dpanel', 'dtoggle');
document.getElementById('ntoggle').onclick = () => togglePanel('npanel', 'ntoggle');
document.getElementById('vtoggle').onclick = () => togglePanel('vpanel', 'vtoggle');
document.getElementById('gtoggle').onclick = () => togglePanel('gpanel', 'gtoggle');
document.getElementById('ftoggle').onclick = () => togglePanel('fpanel', 'ftoggle');
document.getElementById('ltoggle').onclick = () => togglePanel('lpanel', 'ltoggle');
document.getElementById('phtoggle').onclick = () => togglePanel('phpanel', 'phtoggle');
document.getElementById('btoggle').onclick = () => togglePanel('bpanel', 'btoggle');
document.getElementById('rdtoggle').onclick = () => togglePanel('rdpanel', 'rdtoggle');
document.getElementById('stoggle').onclick = () => togglePanel('stpanel', 'stoggle');
document.getElementById('lvltoggle').onclick = () => togglePanel('lvlpanel', 'lvltoggle');
document.getElementById('actoggle').onclick = () => togglePanel('acpanel', 'actoggle');
/* The learning path: hidden until a level check has placed the learner, and
   the panel reads path.json on its first open. */
document.getElementById('pathtoggle').onclick = () => togglePanel('pathpanel', 'pathtoggle');
/* Theme is a preference, not a section, so its switch sits in the header too:
   a learner should not have to open Account - or be signed in at all - to
   change how the app looks, and the choice is remembered the moment it is
   made. */
document.getElementById('themetoggle').onclick = () => {
  Theme.apply(Theme.current() === 'dark' ? 'light' : 'dark', true);
};
/* The tile carries the level from the last check, which is only a localStorage
   read, so it can be painted before the bank is ever fetched. */
Level.paintBadge();
/* The gate: a stored credential and a session younger than seven days go
   straight through; anything else meets the sign-in card when the loader
   lifts, because the overlay sits under the boot screen. */
Study.mount();
Auth.init();
Cert.bind();
document.getElementById('rtoggle').onclick = () => togglePanel('rpanel', 'rtoggle');

/* ============================================================================
 * DAILY ENGLISH
 * One word, one expression and one conversation, changing at local midnight.
 *
 * The selection is a pure function of the local calendar date, so this page,
 * the CLI and the offline APK all show the same three items on the same day
 * and none of them has to ask a server for the day's choice. The rotation
 * below is deliberately a second copy of daily_index() in chatbot.py and
 * dailyIndex() in bot.js; tools/check_daily.py runs all three copies over a
 * year of dates and fails on any disagreement, which is what keeps three
 * copies honest instead of three drifting apart.
 * ==========================================================================*/

/* --- daily rotation: pure, executed by tools/check_daily.py ------------- */
const DAY_EPOCH = Date.UTC(2024, 0, 1);
const DAY_SALTS = {words: 3, expressions: 11, conversations: 5};

/* The device's own local calendar date as YYYY-MM-DD. Not toISOString(), which
   converts to UTC first - east of Greenwich that answers with yesterday's date
   every morning until the offset catches up. */
function dayKey(d) {
  const p = (n) => String(n).padStart(2, '0');
  return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate());
}

/* The card's date line. The ISO key was shown raw next to a Persian phrase,
   and the bidi run flipped the two around - the day read as
   "28-10-2026 · انگلیسی امروز". Plain English and a written-out month, so there
   is nothing for the direction algorithm to reorder. */
const dayLabel = (key) => {
  const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                  'August', 'September', 'October', 'November', 'December'];
  const DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                'Saturday'];
  const [y, m, d] = String(key).split('-').map(Number);
  const at = new Date(y, m - 1, d);
  return DAYS[at.getDay()] + ', ' + d + ' ' + MONTHS[m - 1] + ' ' + y;
};

/* Whole calendar days since the epoch, counted in UTC arithmetic so a 23- or
   25-hour day across a daylight-saving change still counts as one day. */
function dayNumber(key) {
  const parts = String(key).split('-').map(Number);
  return Math.round((Date.UTC(parts[0], parts[1] - 1, parts[2]) - DAY_EPOCH) / 86400000);
}

function dayGcd(a, b) {
  while (b) { const t = a % b; a = b; b = t; }
  return Math.abs(a);
}

/* A step coprime with the catalogue size, so `day * step % size` walks every
   entry before it repeats one, whatever the size happens to be. */
function dayStep(size, salt) {
  if (size <= 1) return 1;
  let step = 1 + (salt % 9);
  while (dayGcd(step, size) !== 1) {
    step += 1;
    if (step > size + 1) return 1;
  }
  return step;
}

const dayIndex = (day, size, salt) =>
  (size <= 0 ? 0 : (day * dayStep(size, salt) + salt) % size);

/* Milliseconds until the next local midnight, plus a second of slack. Asked of
   the Date object rather than by adding 24 hours, so the night the clocks
   change is not an hour early or an hour late. */
function untilLocalMidnight(now) {
  const next = new Date(now.getTime());
  next.setHours(24, 0, 1, 0);
  return Math.max(1000, next.getTime() - now.getTime());
}
/* --- end daily rotation ------------------------------------------------- */

/* --- daily store: pure, executed by tools/check_daily.py ----------------
   Completion lives beside the date it belongs to and is never cleared, so
   yesterday's record survives and "today" simply has no entries yet. Keyed on
   the content id rather than the position, so extending the catalogue cannot
   move a tick onto a different word. */
const DailyStore = {
  KEY: 'fluentify.daily.v1',
  read() {
    try {
      const raw = localStorage.getItem(this.KEY);
      const state = raw ? JSON.parse(raw) : null;
      const days = state && state.days && typeof state.days === 'object'
        ? state.days : {};
      const clean = {};
      Object.keys(days).forEach((k) => {
        if (Array.isArray(days[k])) clean[k] = days[k].filter((x) => typeof x === 'string');
      });
      return {days: clean};
    } catch (e) {
      return {days: {}};   // a corrupt record must not take the panel down
    }
  },
  write(state) {
    try { localStorage.setItem(this.KEY, JSON.stringify({days: state.days})); }
    catch (e) { /* private mode, full disk: the tick just does not persist */ }
  },
  isDone(state, date, id) {
    return !!(state.days[date] || []).includes(id);
  },
  setDone(state, date, id, done) {
    const list = (state.days[date] = state.days[date] || []);
    const at = list.indexOf(id);
    if (done && at === -1) list.push(id);
    if (!done && at !== -1) list.splice(at, 1);
    if (!list.length) delete state.days[date];
    return state;
  },
  /* Counted against the ids on screen, so an id left over from an older
     catalogue can never make a card look finished or the day look complete. */
  count(state, date, ids) {
    return ids.filter((id) => this.isDone(state, date, id)).length;
  },

  /* Whether the daily set is offered at all, and whether today's offer was
     turned down. Learning a language is not a streak to be defended: the
     feature is a suggestion, so "not today" and "not ever, in the chat" are
     both one tap away and neither is punished with a nagging badge. */
  CARD_KEY: 'fluentify.daily.card.v1',
  readCard() {
    try {
      const raw = localStorage.getItem(this.CARD_KEY);
      const s = raw ? JSON.parse(raw) : null;
      const sk = s && s.skipped && typeof s.skipped === 'object' ? s.skipped : {};
      const fin = s && s.finished && typeof s.finished === 'object' ? s.finished : {};
      const skipped = {}, finished = {};
      Object.keys(sk).forEach((k) => { if (sk[k]) skipped[k] = true; });
      Object.keys(fin).forEach((k) => { if (fin[k]) finished[k] = true; });
      return {hidden: !!(s && s.hidden), skipped: skipped, finished: finished};
    } catch (e) {
      return {hidden: false, skipped: {}, finished: {}};
    }
  },
  writeCard(prefs) {
    // Both maps are per day, so they would grow forever. The newest sixty are
    // kept: more than enough to remember the recent past, and bounded.
    const prune = (map) => {
      const kept = {};
      Object.keys(map || {}).sort().reverse().slice(0, 60)
        .forEach((k) => { kept[k] = true; });
      return kept;
    };
    const skipped = prune(prefs.skipped);
    const finished = prune(prefs.finished);
    try {
      localStorage.setItem(this.CARD_KEY,
        JSON.stringify({hidden: !!prefs.hidden, skipped: skipped,
                        finished: finished}));
    } catch (e) { /* private mode: the choice just does not persist */ }
    return {hidden: !!prefs.hidden, skipped: skipped, finished: finished};
  },
  isSkipped(prefs, date) { return !!prefs.skipped[date]; },
  /* A day whose three items are all ticked is over too: the card closes and
     stays closed, so the next repaint cannot reopen a finished day. */
  isFinished(prefs, date) { return !!prefs.finished[date]; },
  setFinished(prefs, date) {
    prefs.finished = prefs.finished || {};
    prefs.finished[date] = true;
    return prefs;
  },
  /* One way only. There is no "un-skip" parameter, because there is no
     un-skip: a day the learner turned down stays turned down, so the store
     cannot be talked into reopening it by a later repaint or a stale
     handler. */
  setSkipped(prefs, date) {
    prefs.skipped = prefs.skipped || {};
    prefs.skipped[date] = true;
    return prefs;
  },
};
/* --- end daily store ---------------------------------------------------- */

/* --- weekly quiz: pure, executed by tools/check_weekly.py ---------------
   The quiz reviews what the learner actually ticked off in the last seven
   days, so its only content source is the daily store. Everything in here is
   arithmetic over that record and the daily catalogue: no clock of its own, no
   network, no randomness that is not seeded by the period - the same week and
   the same ticks must always give the same paper, or a refresh would rewrite
   the questions under the reader.

   The week here is the Iranian one, Friday to Thursday, and the clock is
   Tehran's rather than the device's: this is an app for Iranian learners, and
   a quiz that opens at a different hour in Dubai than in Tehran is a quiz two
   people cannot talk about. Iran has had no daylight saving since 2022, so
   the offset is a constant 3:30, not a table.

   The paper is offered on Friday from 09:00 Tehran (05:30 UTC) until midnight
   (20:30 UTC): the Friday morning after the week's learning, which is the
   weekend morning people actually have. What it asks is the seven days that
   ended on Thursday - the Friday-to-Thursday week that just closed - so a
   word met on Friday is not asked on that same Friday but on the next one.
   One paper per Friday, frozen when built, so reopening cannot redraw it. */
/* A word from the catalogue is put into a regular expression to find the
   sentence it belongs in, so its own punctuation must not become a pattern. */
const weeklyEscapeRe = (s) => String(s).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

const WeeklyQuiz = {
  KEY: 'fluentify.weekly.quiz.v1',
  MIN_ITEMS: 5,
  MAX_QUESTIONS: 10,
  WINDOW: 7,
  KEEP: 12,
  /* Tehran is UTC+3:30 all year. Written as hours so the shift is one number:
     9:00 in Tehran is 5:30 UTC and midnight is 20:30 UTC. */
  TZ_HOURS: 3.5,
  OPEN_HOUR: 9,
  FRIDAY: 5,
  /* A word can be asked three ways; an expression is a whole sentence, so it
     is asked what it means and when it fits rather than with a blank in it. */
  TYPES: {
    word: ['meaning', 'reverse', 'cloze'],
    expression: ['situation', 'meaning'],
  },

  pad(n) { return String(n).padStart(2, '0'); },

  /* The device's local calendar date as YYYY-MM-DD, the same shape the daily
     store is keyed on. Not toISOString(), which answers with yesterday's date
     all morning east of Greenwich. */
  keyOf(date) {
    return date.getFullYear() + '-' + this.pad(date.getMonth() + 1) + '-' +
      this.pad(date.getDate());
  },

  /* A date key back to the local midnight it names. */
  dateOf(key) {
    const p = String(key).split('-').map(Number);
    return new Date(p[0], p[1] - 1, p[2]);
  },

  addDays(key, n) {
    const d = this.dateOf(key);
    return this.keyOf(new Date(d.getFullYear(), d.getMonth(), d.getDate() + n));
  },

  /* The device's clock, moved to Tehran. Every getter below reads this the way
     it would read a local date, so the calendar arithmetic never has to know
     which zone the phone is in. */
  tehran(now) { return new Date(now.getTime() + this.TZ_HOURS * 3600000); },

  /* Today's date in Tehran, which is the date the week and the quiz key on.
     Read through the UTC fields of the shifted date: the shift already put the
     wall clock in the hours, so reading the *local* hours as well would add the
     device's offset a second time - which on a Tehran phone is a quiz that
     opens three and a half hours early. */
  tehranKey(now) {
    const t = this.tehran(now);
    return t.getUTCFullYear() + '-' + this.pad(t.getUTCMonth() + 1) + '-' +
      this.pad(t.getUTCDate());
  },

  weekday(key) {
    const p = String(key).split('-').map(Number);
    return new Date(Date.UTC(p[0], p[1] - 1, p[2])).getUTCDay();
  },

  /* The most recent Friday, today included: the identity of one quiz. It stays
     the same all week, so a paper opened on Friday evening and looked at again
     on Monday is still the same paper - the card is simply not offered after
     the Friday. */
  periodStart(now) {
    const key = this.tehranKey(now);
    return this.addDays(key, -(((this.weekday(key) - this.FRIDAY) + 7) % 7));
  },

  /* The seven dates the paper is drawn from: the week that ended on the
     Thursday before this Friday. That is the Friday-to-Thursday week Iranian
     learners just finished, and it is why a word met on the quiz Friday waits
     for the next quiz instead of being asked the same morning. */
  contentWindow(period) {
    const out = [];
    for (let i = this.WINDOW; i >= 1; i -= 1) out.push(this.addDays(period, -i));
    return out;
  },

  /* Offered on Friday only, from 09:00 Tehran until midnight. Before nine the
     week is not over for anyone who is still asleep; after midnight the day
     has turned and the next paper is the one that matters. */
  isOpen(now) {
    const t = this.tehran(now);
    return t.getUTCDay() === this.FRIDAY && t.getUTCHours() >= this.OPEN_HOUR;
  },

  /* When the card next becomes available, as a Date in the device's clock. The
     page uses it to set one timer instead of polling, so the card appears in
     the window it belongs to without a reload. */
  opensAt(now) {
    const t = this.tehran(now);
    const key = this.tehranKey(now);
    let at;
    if (t.getUTCDay() === this.FRIDAY && t.getUTCHours() < this.OPEN_HOUR) {
      at = key;
    } else {
      at = this.addDays(key, (this.FRIDAY - this.weekday(key) + 7) % 7 || 7);
    }
    const p = at.split('-').map(Number);
    const wall = Date.UTC(p[0], p[1] - 1, p[2], this.OPEN_HOUR, 0, 0);
    return new Date(wall - this.TZ_HOURS * 3600000);
  },

  /* The kind of a daily-store id: w001 is a word, e001 an expression, c001 a
     conversation. A conversation is not quizzed, so it drops out here. */
  kindOf(id) {
    const s = String(id || '');
    if (/^w\d+$/.test(s)) return 'word';
    if (/^e\d+$/.test(s)) return 'expression';
    return null;
  },

  /* Every distinct item ticked off inside the week, oldest first. The daily
     store is keyed by date, so this is also the only place the days are read:
     a tick outside the week is a tick from last month and is not reviewed. */
  eligible(days, now) {
    const out = [];
    const seen = new Set();
    const store = days && typeof days === 'object' ? days : {};
    this.contentWindow(this.periodStart(now)).forEach((day) => {
      const list = Array.isArray(store[day]) ? store[day] : [];
      list.forEach((id) => {
        const kind = this.kindOf(id);
        if (!kind || seen.has(id)) return;
        seen.add(id);
        out.push({id: id, kind: kind, day: day});
      });
    });
    return out;
  },

  /* FNV-1a: the seed for one period, so the paper is a function of the week
     and its items and of nothing else. */
  hash(text) {
    let h = 2166136261;
    const s = String(text);
    for (let i = 0; i < s.length; i += 1) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return h >>> 0;
  },

  /* mulberry32, seeded: small, deterministic, and good enough to shuffle ten
     options without looking like a pattern. */
  rand(seed) {
    let a = seed >>> 0;
    return () => {
      a = (a + 0x6D2B79F5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  },

  shuffle(list, rand) {
    const out = list.slice();
    for (let i = out.length - 1; i > 0; i -= 1) {
      const j = Math.floor(rand() * (i + 1));
      const t = out[i];
      out[i] = out[j];
      out[j] = t;
    }
    return out;
  },

  rows(cat, kind) {
    const rows = (cat || {})[kind === 'word' ? 'words' : 'expressions'];
    return Array.isArray(rows) ? rows : [];
  },

  find(cat, kind, id) {
    return this.rows(cat, kind).find((r) => r && r.id === id) || null;
  },

  /* The answer plus up to three wrong ones drawn from the same kind, all
     distinct: two options that both read as right would make the question
     unanswerable, and the key is the item's own translation, never invented. */
  options(answer, others, rand) {
    if (!answer) return null;
    const texts = [answer];
    const seen = new Set(texts);
    this.shuffle(others, rand).forEach((t) => {
      if (texts.length >= 4) return;
      if (typeof t !== 'string' || !t.trim() || seen.has(t)) return;
      seen.add(t);
      texts.push(t);
    });
    if (texts.length < 3) return null;
    const order = this.shuffle(texts, rand);
    return {options: order, answer: order.indexOf(answer)};
  },

  /* One question, or null when the entry cannot carry this format - a word
     with no example sentence cannot be asked with a blank in it. */
  make(cat, item, type, rand) {
    const row = this.find(cat, item.kind, item.id);
    if (!row) return null;
    const others = this.rows(cat, item.kind).filter((r) => r && r.id !== row.id);
    const word = item.kind === 'word';
    const fa = (t) => String(t || '');

    if (type === 'meaning') {
      const answer = row.fa;
      if (!answer) return null;
      const set = this.options(answer, others.map((r) => r.fa), rand);
      if (!set) return null;
      return {
        id: row.id + ':meaning',
        item: row.id,
        kind: item.kind,
        type: 'meaning',
        prompt: {
          en: 'What does \u201c' + row.en + '\u201d mean?',
          fa: '\u00ab' + row.en + '\u00bb چه معنایی دارد؟',
        },
        options: set.options,
        answer: set.answer,
        detail: {
          en: row.en + ' \u2014 ' + fa(row.fa) +
            (row.def && row.def.en ? '. ' + row.def.en : ''),
          fa: fa(row.fa) + (row.def && row.def.fa ? ' \u2014 ' + row.def.fa : ''),
        },
      };
    }

    if (type === 'reverse') {
      if (!row.en || !row.fa) return null;
      const set = this.options(row.en, others.map((r) => r.en), rand);
      if (!set) return null;
      return {
        id: row.id + ':reverse',
        item: row.id,
        kind: item.kind,
        type: 'reverse',
        prompt: {
          en: 'Which word means \u201c' + row.fa + '\u201d?',
          fa: '\u00ab' + row.fa + '\u00bb کدام واژه است؟',
        },
        options: set.options,
        answer: set.answer,
        detail: {
          en: row.en + ' \u2014 ' + row.fa,
          fa: row.fa + ' \u2014 ' + row.en,
        },
      };
    }

    if (type === 'cloze') {
      const examples = word ? (row.examples || []) : [];
      const example = examples.find((ex) => ex && typeof ex.en === 'string' &&
        new RegExp('(^|[^A-Za-z])' + weeklyEscapeRe(row.en) + '([^A-Za-z]|$)', 'i')
          .test(ex.en));
      if (!example) return null;
      const re = new RegExp('(^|[^A-Za-z])(' + weeklyEscapeRe(row.en) + ')([^A-Za-z]|$)', 'i');
      const blank = example.en.replace(re, (m, a, b, c) => a + '____' + c);
      const set = this.options(row.en, others.map((r) => r.en), rand);
      if (!set) return null;
      return {
        id: row.id + ':cloze',
        item: row.id,
        kind: item.kind,
        type: 'cloze',
        prompt: {
          en: 'Choose the word that fills the gap: ' + blank,
          fa: 'واژه‌ای که جای خالی را پر می‌کند انتخاب کن: ' + blank,
        },
        options: set.options,
        answer: set.answer,
        detail: {
          en: example.en + ' (' + row.en + ' \u2014 ' + row.fa + ')',
          fa: (example.fa || '') + ' (' + row.en + ' \u2014 ' + row.fa + ')',
        },
      };
    }

    if (type === 'situation') {
      const when = row.when && row.when.en ? row.when.en : '';
      if (!when || !row.en) return null;
      const set = this.options(row.en, others.map((r) => r.en), rand);
      if (!set) return null;
      return {
        id: row.id + ':situation',
        item: row.id,
        kind: item.kind,
        type: 'situation',
        prompt: {
          en: 'Which expression fits? ' + when,
          fa: 'کدام عبارت مناسب است؟ ' + ((row.when && row.when.fa) || ''),
        },
        options: set.options,
        answer: set.answer,
        detail: {
          en: row.en + ' \u2014 ' + fa(row.fa),
          fa: fa(row.fa),
        },
      };
    }

    return null;
  },

  /* The paper for one period: at most ten items, words and expressions taken
     in turn so one kind cannot crowd the other out, each item asked once, and
     the format rotated so ten questions are not ten of the same shape. */
  build(cat, items, period, todayKey) {
    /* Sorted before anything else: the paper is a function of the set of
       items, not of the order the store happened to hand them over, so a
       record rewritten from a different path cannot reword the week. */
    const list = Array.isArray(items)
      ? items.slice().sort((a, b) => (a.id < b.id ? -1 : a.id > b.id ? 1 : 0))
      : [];
    if (list.length < this.MIN_ITEMS) return null;

    const seed = this.hash(period + '|' +
      list.map((i) => i.id).sort().join(','));
    const rand = this.rand(seed);

    let words = this.shuffle(list.filter((i) => i.kind === 'word'), rand);
    let exprs = this.shuffle(list.filter((i) => i.kind === 'expression'), rand);
    const order = [];
    while (words.length || exprs.length) {
      const tail = order.slice(-2);
      let pick;
      if (words.length && exprs.length) {
        const stuck = tail.length === 2 && tail[0].kind === tail[1].kind;
        if (stuck && tail[0].kind === 'word') pick = exprs.shift();
        else if (stuck) pick = words.shift();
        else pick = words.length >= exprs.length ? words.shift() : exprs.shift();
      } else {
        pick = words.length ? words.shift() : exprs.shift();
      }
      order.push(pick);
    }

    const chosen = order.slice(0, this.MAX_QUESTIONS);
    const questions = [];
    chosen.forEach((item, n) => {
      const types = this.TYPES[item.kind] || [];
      for (let k = 0; k < types.length; k += 1) {
        const type = types[(n + k) % types.length];
        const q = this.make(cat, item, type, rand);
        if (q) { questions.push(q); break; }
      }
    });
    if (questions.length < this.MIN_ITEMS) return null;

    return {
      period: period,
      made: todayKey,
      items: chosen.map((i) => ({id: i.id, kind: i.kind, day: i.day})),
      questions: questions,
    };
  },

  /* Every answer checked against the key, never against the reader's own
     memory of what they chose. */
  grade(quiz, answers) {
    const qs = (quiz && quiz.questions) || [];
    const picked = answers && typeof answers === 'object' ? answers : {};
    const missed = [];
    let right = 0;
    qs.forEach((q, i) => {
      const pick = picked[i] != null ? Number(picked[i]) : null;
      if (pick != null && pick === q.answer) right += 1;
      else missed.push(i);
    });
    return {total: qs.length, right: right, missed: missed,
            percent: qs.length ? Math.round((right / qs.length) * 100) : 0};
  },

  /* ---- the record of the periods ------------------------------------- */

  read() {
    try {
      const raw = localStorage.getItem(this.KEY);
      const state = raw ? JSON.parse(raw) : null;
      const periods = state && state.periods && typeof state.periods === 'object'
        ? state.periods : {};
      const clean = {};
      Object.keys(periods).forEach((k) => {
        const p = periods[k];
        if (!p || typeof p !== 'object') return;
        const status = ['available', 'started', 'completed', 'skipped'].includes(p.status)
          ? p.status : 'available';
        clean[k] = {
          status: status,
          quiz: p.quiz && Array.isArray(p.quiz.questions) ? p.quiz : null,
          answers: p.answers && typeof p.answers === 'object' ? p.answers : {},
          result: p.result && typeof p.result === 'object' ? p.result : null,
          cursor: typeof p.cursor === 'number' && p.cursor >= 0 ? p.cursor : 0,
          at: typeof p.at === 'string' ? p.at : '',
        };
      });
      return {periods: clean};
    } catch (e) {
      return {periods: {}};      // a corrupt record must not take the page down
    }
  },

  write(state) {
    const periods = (state && state.periods) || {};
    const kept = {};
    Object.keys(periods).sort().reverse().slice(0, this.KEEP)
      .forEach((k) => { kept[k] = periods[k]; });
    try {
      localStorage.setItem(this.KEY, JSON.stringify({periods: kept}));
    } catch (e) { /* private mode or a full disk: the paper still plays */ }
    return {periods: kept};
  },

  record(state, period) {
    return (state.periods && state.periods[period]) || null;
  },

  /* One way, like the daily skip: there is no argument that takes a learner
     back out of a finished week, because the paper is over and its score is
     history. */
  setSkipped(state, period) {
    state.periods = state.periods || {};
    state.periods[period] = {
      status: 'skipped', quiz: null, answers: {}, result: null,
      at: this.keyOf(new Date()),
    };
    return state;
  },

  setStarted(state, period, quiz) {
    state.periods = state.periods || {};
    const prev = state.periods[period] || {};
    state.periods[period] = {
      status: 'started', quiz: quiz || prev.quiz || null,
      answers: prev.answers || {}, result: prev.result || null,
      at: prev.at || this.keyOf(new Date()),
    };
    return state;
  },

  setCompleted(state, period, quiz, answers, result) {
    state.periods = state.periods || {};
    state.periods[period] = {
      status: 'completed', quiz: quiz, answers: answers || {},
      result: result, at: this.keyOf(new Date()),
    };
    return state;
  },
};
/* --- end weekly quiz ---------------------------------------------------- */

/* --- mastery: pure, executed by tools/check_mastery.py -----------------
   One record per thing the learner has met, and one date on which it should
   come back. Before this the Review panel had `ok` and `streak` and no dates
   at all: a saved word was either due on every visit or, if the reader never
   reached it, due on none. "Mastered" was a tick, and nothing ever measured
   whether the word was still there a week later.

   The schedule is the well-known SM-2 shape (interval, ease, lapses), kept
   deliberately small: four verdicts, an interval in whole days, and a hard cap
   of 180 days so a single confident answer cannot bury an item for a year.

   Retention is not a promise, it is a measurement: every review that comes
   after a gap of six to ten days (or twenty-five to thirty-five) is counted
   in r7 / r30 together with whether it was recalled. Those two counters are
   the only claim this feature makes about memory, and they are earned by
   answers, never by opening the app. */
const Mastery = {
  KEY: 'fluentify.mastery.v1',
  KEEP: 600,
  MAX_DAYS: 180,
  DUE_NOW: 0,
  VERDICTS: ['again', 'hard', 'good', 'easy'],

  pad(n) { return String(n).padStart(2, '0'); },

  keyOf(date) {
    return date.getFullYear() + '-' + this.pad(date.getMonth() + 1) + '-' +
      this.pad(date.getDate());
  },

  /* Days as integers on the UTC grid: date keys are calendar labels, so adding
     a day must not depend on the device's zone or on a daylight-saving night. */
  dayOf(key) {
    const p = String(key).split('-').map(Number);
    return Math.round(Date.UTC(p[0], p[1] - 1, p[2]) / 86400000);
  },

  keyOfDay(n) {
    const d = new Date(n * 86400000);
    return d.getUTCFullYear() + '-' + this.pad(d.getUTCMonth() + 1) + '-' +
      this.pad(d.getUTCDate());
  },

  addDays(key, n) { return this.keyOfDay(this.dayOf(key) + n); },

  itemKey(kind, id) { return String(kind || 'word') + ':' + String(id); },

  read() {
    try {
      const raw = localStorage.getItem(this.KEY);
      const state = raw ? JSON.parse(raw) : null;
      const src = state && state.items && typeof state.items === 'object'
        ? state.items : {};
      const items = {};
      Object.keys(src).forEach((k) => {
        const it = src[k];
        if (!it || typeof it !== 'object') return;
        items[k] = {
          k: k,
          kind: typeof it.kind === 'string' ? it.kind : 'word',
          en: typeof it.en === 'string' ? it.en : '',
          fa: typeof it.fa === 'string' ? it.fa : '',
          level: typeof it.level === 'string' ? it.level : '',
          first: typeof it.first === 'string' ? it.first : '',
          due: typeof it.due === 'string' ? it.due : '',
          iv: Number(it.iv) >= 0 ? Number(it.iv) : 0,
          ease: Number(it.ease) >= 1.3 ? Number(it.ease) : 2.5,
          reps: Number(it.reps) >= 0 ? Number(it.reps) : 0,
          lapses: Number(it.lapses) >= 0 ? Number(it.lapses) : 0,
          last: typeof it.last === 'string' ? it.last : '',
          r7: Array.isArray(it.r7) ? [Number(it.r7[0]) || 0, Number(it.r7[1]) || 0] : [0, 0],
          r30: Array.isArray(it.r30) ? [Number(it.r30[0]) || 0, Number(it.r30[1]) || 0] : [0, 0],
        };
      });
      return {items: items};
    } catch (e) {
      return {items: {}};   // a corrupt record must not take the panel down
    }
  },

  write(state) {
    const items = (state && state.items) || {};
    /* Bounded: the newest six hundred by the day they were first met. An
       unbounded ledger is a record that eventually cannot be written. */
    const keys = Object.keys(items).sort((a, b) => {
      const x = items[a].first || '', y = items[b].first || '';
      return x < y ? 1 : x > y ? -1 : (a < b ? -1 : 1);
    }).slice(0, this.KEEP);
    const kept = {};
    keys.forEach((k) => { kept[k] = items[k]; });
    try {
      localStorage.setItem(this.KEY, JSON.stringify({items: kept}));
    } catch (e) { /* private mode or a full disk: the queue still plays */ }
    return {items: kept};
  },

  /* A new item is due immediately: it was just met in the daily set and has
     never been recalled once, so the first thing the queue should ask is
     whether any of it stuck. `seed` never overwrites a record that already
     exists, so a saved word and a daily word cannot reset each other's dates. */
  seed(state, seeds, today) {
    const items = (state && state.items) || {};
    const day = today || '';
    (Array.isArray(seeds) ? seeds : []).forEach((s) => {
      if (!s || !s.key || items[s.key]) return;
      items[s.key] = {
        k: s.key,
        kind: s.kind || 'word',
        en: s.en || '',
        fa: s.fa || '',
        level: s.level || '',
        first: s.day || day,
        due: day || s.day || '',
        iv: 0, ease: 2.5, reps: 0, lapses: 0, last: '',
        r7: [0, 0], r30: [0, 0],
      };
    });
    return state;
  },

  /* Everything the daily store has ticked, as seeds. A tick is the only proof
     the app has that the item was met, so it is the only thing that can put an
     item in the queue. */
  seedDaily(state, cat, days, today) {
    const seeds = [];
    const store = days && typeof days === 'object' ? days : {};
    const rows = (kind) => (cat && Array.isArray(cat[kind]) ? cat[kind] : []);
    Object.keys(store).sort().forEach((day) => {
      (Array.isArray(store[day]) ? store[day] : []).forEach((id) => {
        const kind = /^w\d+$/.test(id) ? 'word' : /^e\d+$/.test(id) ? 'expression' : null;
        if (!kind) return;
        const row = rows(kind === 'word' ? 'words' : 'expressions')
          .find((r) => r && r.id === id);
        if (!row || !row.en) return;
        seeds.push({key: this.itemKey(kind, id), kind: kind, en: row.en,
                    fa: row.fa || '', level: row.level || '', day: day});
      });
    });
    return this.seed(state, seeds, today);
  },

  /* One answer, one new date. `gap` is how long the item actually survived
     since it was last asked, which is what the retention counters record - not
     how the learner feels about the word. */
  grade(state, key, verdict, today) {
    const items = (state && state.items) || {};
    const v = Math.max(0, Math.min(3, Number(verdict) || 0));
    let it = items[key];
    if (!it) {
      it = items[key] = {k: key, kind: 'word', en: '', fa: '', level: '',
        first: today, due: today, iv: 0, ease: 2.5, reps: 0, lapses: 0,
        last: '', r7: [0, 0], r30: [0, 0]};
    }
    const todayN = this.dayOf(today);
    if (it.last) {
      const gap = todayN - this.dayOf(it.last);
      const recall = v >= 2 ? 1 : 0;
      if (gap >= 6 && gap <= 10) { it.r7[0] += 1; it.r7[1] += recall; }
      if (gap >= 25 && gap <= 35) { it.r30[0] += 1; it.r30[1] += recall; }
    }

    let iv = Number(it.iv) || 0;
    let ease = Number(it.ease) || 2.5;
    if (v === 0) {
      iv = this.DUE_NOW; ease = Math.max(1.3, ease - 0.2);
      it.lapses = (it.lapses || 0) + 1;
    } else if (v === 1) {
      iv = Math.max(1, Math.round((iv || 1) * 1.2));
      ease = Math.max(1.3, ease - 0.15);
    } else if (v === 2) {
      iv = iv ? Math.max(iv + 1, Math.round(iv * ease)) : 1;
    } else {
      iv = Math.max(2, Math.round((iv || 1) * ease * 1.3));
      ease = Math.min(3.2, ease + 0.1);
    }
    it.iv = Math.min(this.MAX_DAYS, iv);
    it.ease = Math.round(ease * 100) / 100;
    it.reps = (it.reps || 0) + 1;
    it.last = today;
    it.due = this.addDays(today, it.iv);
    items[key] = it;
    return state;
  },

  /* Everything whose date has arrived, oldest first. An item with no date is
     due: it has never been scheduled, so it is not something to skip. */
  due(state, today) {
    const items = (state && state.items) || {};
    const out = [];
    Object.keys(items).forEach((k) => {
      const it = items[k];
      if (!it) return;
      /* An item with no date has never been scheduled, so it is not something
         to skip: it is the oldest thing in the queue. */
      if (it.due && it.due > today) return;
      out.push(it);
    });
    out.sort((a, b) => (a.due < b.due ? -1 : a.due > b.due ? 1 :
      (a.k < b.k ? -1 : 1)));
    return out;
  },

  /* When the queue next has something in it, or null when it is empty. */
  next(state) {
    const items = (state && state.items) || {};
    const keys = Object.keys(items).filter((k) => items[k] && items[k].due);
    if (!keys.length) return null;
    keys.sort((a, b) => (items[a].due < items[b].due ? -1 : 1));
    return items[keys[0]].due;
  },

  /* The measured claim: of the reviews that happened after a real gap, how
     many were recalled. n is the count, good the ones answered good or easy. */
  retention(state) {
    const items = (state && state.items) || {};
    const at7 = {n: 0, good: 0}, at30 = {n: 0, good: 0};
    Object.keys(items).forEach((k) => {
      const it = items[k];
      if (!it) return;
      at7.n += it.r7[0]; at7.good += it.r7[1];
      at30.n += it.r30[0]; at30.good += it.r30[1];
    });
    const pct = (x) => (x.n ? Math.round((x.good / x.n) * 100) : null);
    return {at7: at7, at30: at30, pct7: pct(at7), pct30: pct(at30)};
  },

  stats(state, today) {
    const items = (state && state.items) || {};
    const keys = Object.keys(items);
    return {
      total: keys.length,
      due: this.due(state, today).length,
      learning: keys.filter((k) => (items[k].iv || 0) < 21).length,
      mature: keys.filter((k) => (items[k].iv || 0) >= 21).length,
    };
  },
};
/* --- end mastery -------------------------------------------------------- */

/* --- error log: pure, executed by tools/check_errors.py -----------------
   The app already diagnoses mistakes and then throws the diagnosis away: a
   level-check item knows its subskill, the weekly quiz knows which word it
   asked, a drill knows which partner it wanted - and each one shows a line and
   forgets it. This is the smallest structure that lets those diagnoses add up:
   an event per miss (class, item, day) and the card itself so the drill can ask
   it again without a second copy of the content.

   Nothing here scores the learner. It counts what the app has already been
   told, ranks it, and hands the same questions back. */
const ErrorLog = {
  KEY: 'fluentify.errors.v1',
  EVENTS: 400,
  CARDS: 80,

  read() {
    try {
      const raw = localStorage.getItem(this.KEY);
      const s = raw ? JSON.parse(raw) : null;
      const events = Array.isArray(s && s.events) ? s.events : [];
      const cardsIn = s && s.cards && typeof s.cards === 'object' ? s.cards : {};
      const events_ = [], cards = {};
      events.forEach((e) => {
        if (!e || typeof e !== 'object' || typeof e.c !== 'string') return;
        events_.push({c: e.c, e: typeof e.e === 'string' ? e.e : '',
                      f: typeof e.f === 'string' ? e.f : '',
                      d: typeof e.d === 'string' ? e.d : ''});
      });
      Object.keys(cardsIn).forEach((k) => {
        const c = cardsIn[k];
        if (!c || typeof c !== 'object' || !c.prompt) return;
        cards[k] = {
          id: typeof c.id === 'string' ? c.id : k,
          c: typeof c.c === 'string' ? c.c : '',
          kind: c.kind === 'type' ? 'type' : 'choice',
          prompt: {en: String((c.prompt || {}).en || ''),
                   fa: String((c.prompt || {}).fa || '')},
          options: Array.isArray(c.options) ? c.options.filter((o) => typeof o === 'string') : [],
          answer: typeof c.answer === 'string' || typeof c.answer === 'number'
            ? c.answer : 0,
          why: {en: String((c.why || {}).en || ''), fa: String((c.why || {}).fa || '')},
          detail: {en: String((c.detail || {}).en || ''),
                   fa: String((c.detail || {}).fa || '')},
          d: typeof c.d === 'string' ? c.d : '',
          seq: Number(c.seq) || 0,
        };
      });
      return {events: events_.slice(-this.EVENTS), cards: cards,
              seq: Number(s && s.seq) || 0};
    } catch (e) {
      return {events: [], cards: {}, seq: 0};
    }
  },

  write(state) {
    const events = (state.events || []).slice(-this.EVENTS);
    const all = Object.keys(state.cards || {}).map((k) => state.cards[k]);
    /* Newest cards kept: an item answered correctly later is not deleted, it
       just stops being the newest, and the cap keeps the record writable. */
    all.sort((a, b) => (b.seq || 0) - (a.seq || 0));
    const keep = all.slice(0, this.CARDS);
    const cards = {};
    keep.forEach((c) => { cards[c.c + '|' + c.id] = c; });
    const out = {events: events, cards: cards, seq: Number(state.seq) || 0};
    try {
      localStorage.setItem(this.KEY, JSON.stringify(out));
    } catch (e) { /* private mode: the profile just does not grow */ }
    return out;
  },

  /* One miss. A card with the same class and id replaces the older copy, so
     the drill always shows the most recent wording of the same question. */
  note(state, cls, card, today) {
    const key = String((cls && cls.key) || 'other');
    const st = state || {events: [], cards: {}, seq: 0};
    st.events = Array.isArray(st.events) ? st.events : [];
    st.cards = st.cards && typeof st.cards === 'object' ? st.cards : {};
    st.seq = Number(st.seq) || 0;
    st.events.push({c: key, e: (cls && cls.en) || key, f: (cls && cls.fa) || '',
                    d: today || ''});
    if (st.events.length > this.EVENTS) st.events = st.events.slice(-this.EVENTS);
    if (card && card.id) {
      st.seq += 1;
      st.cards[key + '|' + card.id] = {
        id: String(card.id), c: key,
        kind: card.kind === 'type' ? 'type' : 'choice',
        prompt: card.prompt || {en: '', fa: ''},
        options: Array.isArray(card.options) ? card.options : [],
        answer: card.answer, why: card.why || {en: '', fa: ''},
        detail: card.detail || {en: '', fa: ''},
        d: today || '', seq: st.seq,
      };
    }
    return st;
  },

  /* Classes, most frequent first, then most recent. This is the whole profile:
     a count the learner can check against their own memory of the month. */
  rank(state) {
    const events = (state && state.events) || [];
    const seen = {};
    const order = [];
    events.forEach((e) => {
      if (!e || !e.c) return;
      if (!seen[e.c]) {
        seen[e.c] = {key: e.c, en: e.e || e.c, fa: e.f || '', count: 0, last: ''};
        order.push(e.c);
      }
      seen[e.c].count += 1;
      if (!seen[e.c].last || e.d > seen[e.c].last) seen[e.c].last = e.d;
    });
    return order.map((k) => seen[k]).sort((a, b) =>
      b.count - a.count || (a.last < b.last ? 1 : -1));
  },

  /* The questions behind one class, newest first, so "practise this" asks the
     exact items that were missed rather than an invented set. */
  drill(state, key, limit) {
    const cards = (state && state.cards) || {};
    const out = Object.keys(cards)
      .map((k) => cards[k])
      .filter((c) => c && c.c === key && c.prompt && c.prompt.en)
      .sort((a, b) => (b.seq || 0) - (a.seq || 0));
    return out.slice(0, Math.max(1, Number(limit) || 5));
  },

  total(state) { return ((state && state.events) || []).length; },

  clear() {
    try { localStorage.removeItem(this.KEY); } catch (e) { /* private */ }
    return {events: [], cards: {}, seq: 0};
  },
};
/* --- end error log ------------------------------------------------------ */

/* --- say match: pure, executed by tools/check_speech.py -----------------
   Comparing what the app asked the learner to say with what the recogniser
   heard. This is not a phoneme score and must never be shown as one: it is a
   word-level report of which words came back, and a missing word is a real
   signal about intelligibility rather than a grade.

   Order matters, so the alignment is longest-common-subsequence rather than a
   position-by-position zip: a recogniser that drops one word would otherwise
   mark every word after it wrong. */
/* Written out, not compared as strings: "don't" and "do not" are the same
   words, and calling one of them missing would be the app's mistake rather
   than the speaker's. */
const SAY_CONTRACTIONS = {
  "don't": 'do not', "doesn't": 'does not', "didn't": 'did not',
  "can't": 'cannot', "won't": 'will not', "isn't": 'is not',
  "aren't": 'are not', "wasn't": 'was not', "weren't": 'were not',
  "haven't": 'have not', "hasn't": 'has not', "hadn't": 'had not',
  "i'm": 'i am', "i've": 'i have', "i'll": 'i will', "i'd": 'i would',
  "you're": 'you are', "we're": 'we are', "they're": 'they are',
  "it's": 'it is', "that's": 'that is', "there's": 'there is',
  "he's": 'he is', "she's": 'she is', "let's": 'let us',
  "you'll": 'you will', "we'll": 'we will', "they'll": 'they will',
  "you've": 'you have', "we've": 'we have', "they've": 'they have',
};

const SayMatch = {
  clean(s) {
    return String(s == null ? '' : s)
      .toLowerCase()
      .replace(/[\u2018\u2019]/g, "'")
      .replace(/[^a-z0-9'\s]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()
      .split(' ')
      .filter((w) => w)
      .map((w) => SAY_CONTRACTIONS[w] || w)
      .join(' ');
  },

  words(s) { const c = this.clean(s); return c ? c.split(' ') : []; },

  /* The same tolerance the chat drill uses for contractions, applied here so
     "do not" and "don't" are not called a missed word. */
  same(a, b) {
    if (a === b) return true;
    const flat = (w) => w.replace(/'/g, '');
    if (flat(a) === flat(b)) return true;
    return false;
  },

  compare(target, said) {
    const t = this.words(target);
    const s = this.words(said);
    const n = t.length, m = s.length;
    const lcs = [];
    for (let i = 0; i <= n; i += 1) lcs.push(new Array(m + 1).fill(0));
    for (let i = 1; i <= n; i += 1) {
      for (let j = 1; j <= m; j += 1) {
        lcs[i][j] = this.same(t[i - 1], s[j - 1])
          ? lcs[i - 1][j - 1] + 1
          : Math.max(lcs[i - 1][j], lcs[i][j - 1]);
      }
    }
    const hit = new Array(n).fill(false);
    let i = n, j = m;
    while (i > 0 && j > 0) {
      if (this.same(t[i - 1], s[j - 1])) { hit[i - 1] = true; i -= 1; j -= 1; }
      else if (lcs[i - 1][j] >= lcs[i][j - 1]) i -= 1;
      else j -= 1;
    }
    const words = t.map((w, k) => ({w: w, ok: hit[k]}));
    const right = words.filter((x) => x.ok).length;
    const matched = new Set(t.map((w, k) => (hit[k] ? w : null)).filter(Boolean));
    const extra = s.filter((w) => !matched.has(w));
    return {
      total: n, right: right,
      percent: n ? Math.round((right / n) * 100) : 0,
      words: words, missing: words.filter((x) => !x.ok).map((x) => x.w),
      extra: extra, empty: s.length === 0,
    };
  },
};
/* --- end say match ------------------------------------------------------ */

/* --- drills: pure, executed by tools/check_speech.py --------------------
   Three mini-drills over data the app already ships: word partners from
   collocations.json, register from register.json, and the minimal pairs the
   phonetics reference has always listed but never tested. Seeded, so the same
   day asks the same question and a test can check the answer key. */
const Drills = {
  rand(seed) {
    let a = seed >>> 0;
    return () => {
      a = (a + 0x6D2B79F5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  },

  hash(text) {
    let h = 2166136261;
    const s = String(text);
    for (let i = 0; i < s.length; i += 1) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return h >>> 0;
  },

  shuffle(list, rand) {
    const out = list.slice();
    for (let i = out.length - 1; i > 0; i -= 1) {
      const j = Math.floor(rand() * (i + 1));
      const t = out[i]; out[i] = out[j]; out[j] = t;
    }
    return out;
  },

  pick(list, seed) {
    if (!Array.isArray(list) || !list.length) return null;
    return list[Math.abs(seed) % list.length];
  },

  /* The listening bank is one object - {levels: [...]} - and every reader of
     it has to unwrap the same way. The chat engine writes that unwrap inline
     ((data.listening && data.listening.levels) || data.listening); the practice
     sheet read the file as though it were already the array, so both dictation
     and say-it found no sentences and told the learner the bank was missing.
     One unwrapper, and the tests feed it the real file. */
  levels(raw) {
    if (Array.isArray(raw)) return raw;
    if (raw && Array.isArray(raw.levels)) return raw.levels;
    return [];
  },

  /* A word partner. The blank is authored, the alternatives are authored -
     grammatical but not English - so the question teaches the difference and
     not merely which string is in a file. */
  collocation(cat, seed) {
    const entries = (cat && Array.isArray(cat.entries) ? cat.entries : [])
      .filter((e) => e && e.blank && e.answer && Array.isArray(e.wrong) && e.wrong.length);
    const e = this.pick(entries, seed);
    if (!e) return null;
    const rand = this.rand(seed + 1);
    const opts = this.shuffle([e.answer].concat(e.wrong.slice(0, 2)), rand);
    return {
      id: 'coll:' + e.id,
      cls: {key: 'collocation', en: 'Word partners', fa: 'هم‌نشینی واژه‌ها'},
      kind: 'choice',
      prompt: {
        en: 'Which word completes it? ' + e.blank,
        fa: 'کدام واژه کامل می‌کند؟ ' + e.blank,
      },
      options: opts,
      answer: opts.indexOf(e.answer),
      why: {
        en: "'" + e.phrase + "' is the pairing English uses.",
        fa: 'در انگلیسی همین ترکیب به کار می‌رود: «' + e.phrase + '».',
      },
      detail: {
        en: e.phrase + ' — ' + (e.fa || '') + (e.example && e.example.en
          ? ' · ' + e.example.en : ''),
        fa: (e.example && e.example.fa) || e.fa || '',
      },
    };
  },

  /* Register: one meaning, three ways to say it. Asking which one is formal is
     the only question here that has one right answer, so it is the one asked. */
  register(cat, seed) {
    const pairs = (cat && Array.isArray(cat.pairs) ? cat.pairs : [])
      .filter((p) => p && p.formal && p.formal.en && p.casual && p.consultative);
    const p = this.pick(pairs, seed);
    if (!p) return null;
    const rand = this.rand(seed + 7);
    const want = p.formal.en;
    const asc = Math.abs(seed) % 2 === 1;
    if (asc) {
      const opts = this.shuffle([p.formal.en, p.consultative.en, p.casual.en], rand);
      return {
        id: 'reg:' + p.id,
        cls: {key: 'register', en: 'Register', fa: 'لحن و رسمیت'},
        kind: 'choice',
        prompt: {
          en: 'Which one would you put in a formal email? ' +
            ((p.meaning || {}).en || ''),
          fa: 'کدام را در یک ایمیل رسمی می‌نویسی؟ ' +
            ((p.meaning || {}).fa || ''),
        },
        options: opts, answer: opts.indexOf(want),
        why: {
          en: 'That is the formal register. The other two are consultative and ' +
            'casual - both correct, both wrong for an email you sign.',
          fa: 'این لحن رسمی است. دو گزینهٔ دیگر نیمه‌رسمی و محاوره‌ای‌اند: هر دو درست‌اند، ' +
            'ولی برای ایمیل رسمی نه.',
        },
        detail: {
          en: p.formal.en + ' · ' + p.consultative.en + ' · ' + p.casual.en,
          fa: ((p.note || {}).fa || p.formal.fa || ''),
        },
      };
    }
    const opts = ['Formal', 'Consultative', 'Casual'];
    return {
      id: 'reg:' + p.id + ':casual',
      cls: {key: 'register', en: 'Register', fa: 'لحن و رسمیت'},
      kind: 'choice',
      prompt: {
        en: 'Which register is this? “' + p.casual.en + '”',
        fa: 'این جمله در چه لحنی است؟ «' + p.casual.en + '»',
      },
      options: opts, answer: 2,
      why: {
        en: 'It is the casual form of: ' + ((p.meaning || {}).en || ''),
        fa: 'این شکل محاوره‌ای «' + ((p.meaning || {}).fa || '') + '» است.',
      },
      detail: {
        en: p.formal.en + ' (formal) · ' + p.consultative.en + ' (consultative) · ' +
          p.casual.en + ' (casual)',
        fa: ((p.note || {}).fa || ''),
      },
    };
  },

  /* The phonetics reference has always carried the pairs - "eat·it · seat·sit" -
     and never asked anyone to tell them apart. This turns those strings into a
     listening test that needs no microphone, so it works on every device. */
  pairs(phonetics) {
    const out = [];
    const seen = {};
    /* Two shapes reach this: the file (sections) and the page's own route,
       which serves the bare list. Accepting both is what keeps the drill alive
       on the web build and in the APK, where the same call reads a file. */
    const sections = Array.isArray(phonetics) ? phonetics
      : (phonetics && Array.isArray(phonetics.sections) ? phonetics.sections : []);
    sections.forEach((s) => {
      (s.groups || []).forEach((g) => {
        (g.rows || []).forEach((r) => {
          /* Only the rows that set one sound against another. A row headed
             /ɑː/ lists words that all share the sound - park and star are not a
             pair to tell apart, and asking which was played would teach the
             learner nothing about a contrast they cannot hear. */
          if (!/\bvs\b/i.test(String(r.ip || ''))) return;
          const words = String(r.words || '').split(/[\u00b7\u2022|]/)
            .map((w) => w.trim())
            .filter((w) => w && /^[a-z']+$/i.test(w) && w.length <= 14)
            .map((w) => w.toLowerCase());
          for (let i = 0; i + 1 < words.length; i += 2) {
            const a = words[i].toLowerCase(), b = words[i + 1].toLowerCase();
            if (!a || !b || a === b) continue;
            const k = a + '|' + b;
            if (seen[k]) continue;
            seen[k] = true;
            out.push({a: a, b: b, ip: r.ip || '', sub: r.sub || ''});
          }
        });
      });
    });
    return out;
  },

  /* Play one of the two and ask which. `say` is the word that is played, so the
     caller must play question.say, not question.options[question.answer]. */
  pairQuestion(bank, seed) {
    const list = Array.isArray(bank) ? bank : [];
    const p = this.pick(list, seed);
    if (!p) return null;
    const which = Math.abs(seed >> 1) % 2 === 0;
    const say = which ? p.b : p.a;
    const opts = this.shuffle([p.a, p.b], this.rand(seed + 3));
    return {
      id: 'pair:' + p.a + ':' + p.b,
      cls: {key: 'listening', en: 'Sound contrasts', fa: 'تقابل صداها'},
      kind: 'choice',
      say: say,
      prompt: {en: 'Which word did you hear?', fa: 'کدام واژه را شنیدی؟'},
      options: opts, answer: opts.indexOf(say),
      why: {en: p.ip + (p.sub ? ' — ' + p.sub : ''), fa: ''},
      detail: {
        en: 'Played: ' + say + ' · ' + p.a + ' / ' + p.b +
          (p.ip ? ' (' + p.ip + ')' : ''),
        fa: 'پخش شد: ' + say,
      },
    };
  },
};
/* --- end drills --------------------------------------------------------- */

/* ============================================================================
 * WEEKLY QUIZ
 * The daily set is what you meet today; this is what you met this week. It
 * draws on nothing but the ticks the daily store already keeps, so there is no
 * second vocabulary list, no second progress record and no network: the paper
 * is frozen into the same record the moment it is built, which is what stops a
 * refresh from drawing a new one and what makes it survive a restart.
 * ==========================================================================*/
const Weekly = (() => {
  const PANEL = 'wqpanel';
  let cat = null;
  let picks = {};
  let view = 'quiz';
  let warned = false;

  const body = () => document.getElementById('wqbody');
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"]/g,
    (c) => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));

  /* The week as the page sees it right now: the period, the record already
     kept for it, and the items learned inside the trailing seven days. */
  function snapshot() {
    const now = new Date();
    const state = WeeklyQuiz.read();
    const period = WeeklyQuiz.periodStart(now);
    const days = DailyStore.read().days;
    const items = WeeklyQuiz.eligible(days, now);
    return {now: now, state: state, period: period, items: items,
            rec: WeeklyQuiz.record(state, period)};
  }

  function counts(items) {
    const words = items.filter((i) => i.kind === 'word').length;
    return {words: words, expressions: items.length - words};
  }

  /* ---- the card in the landing page ----------------------------------- */

  function cardHtml(snap) {
    const c = counts(snap.items);
    const rec = snap.rec;
    const status = rec ? rec.status : 'available';
    const enough = snap.items.length >= WeeklyQuiz.MIN_ITEMS;
    const lead = rec && rec.result
      ? 'You scored <b>' + rec.result.right + ' of ' + rec.result.total + '</b> (' +
        rec.result.percent + '%) on this week&rsquo;s review.'
      : 'Ten questions at most on the words and expressions you learned in the '
        + 'week that ended on Thursday. It is offered on Friday and it is '
        + 'optional: skip it and nothing changes.';
    const meta = enough
      ? c.words + ' word' + (c.words === 1 ? '' : 's') + ' · ' +
        c.expressions + ' expression' + (c.expressions === 1 ? '' : 's') +
        ' · up to ' + WeeklyQuiz.MAX_QUESTIONS + ' questions'
      : snap.items.length + ' of ' + WeeklyQuiz.MIN_ITEMS + ' learned this week';
    const actions = !enough
      ? ''
      : status === 'completed'
        ? '<button type="button" class="wqbtn" data-wq="review">See the review' +
          '<bdi class="fa" lang="fa" dir="rtl">مرور پاسخ‌ها</bdi></button>'
        : '<button type="button" class="wqbtn" data-wq="start">' +
          (status === 'started' ? 'Resume the quiz' : 'Start quiz') +
          '<bdi class="fa" lang="fa" dir="rtl">' +
          (status === 'started' ? 'ادامهٔ آزمون' : 'شروع آزمون') + '</bdi></button>' +
          '<button type="button" class="wqbtn ghost" data-wq="skip">Skip' +
          '<bdi class="fa" lang="fa" dir="rtl">رد کردن</bdi></button>';
    const note = !enough
      ? '<p class="wqnote" dir="ltr">Keep learning! Your weekly quiz will be ready ' +
        'once you&rsquo;ve learned enough new words and expressions.</p>' +
        '<p class="wqnote fa" dir="rtl" lang="fa">به یادگیری ادامه بده! آزمون هفتگی ' +
        'وقتی به اندازهٔ کافی واژه و عبارت تازه یاد بگیری آماده می‌شود.</p>'
      : '';
    return '<div class="wqhead">' +
        '<span class="wqico" aria-hidden="true">' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" ' +
        'stroke-linecap="round" stroke-linejoin="round">' +
        '<path d="M4.6 5.6h14.8v12.8H4.6z"/><path d="M8 3.4v4.4M16 3.4v4.4"/>' +
        '<path d="m8.6 13.4 2 2 4.4-4.4"/></svg></span>' +
        '<span class="wqtitle">Weekly quiz<small dir="rtl" lang="fa">آزمون هفتگی</small></span>' +
        '<span class="spacer"></span>' +
        (status === 'completed'
          ? '<span class="wqscore">' + rec.result.right + '/' + rec.result.total + '</span>'
          : '') +
        '</div>' +
      '<p class="wqline" dir="ltr">' + lead + '</p>' +
      '<p class="wqfa" dir="rtl" lang="fa">' +
        (rec && rec.result
          ? 'در مرور این هفته ' + rec.result.right + ' از ' + rec.result.total +
            ' پاسخ درست بود.'
          : 'حداکثر ده پرسش از واژه‌ها و عبارت‌هایی که تا پنجشنبهٔ همین هفته یاد گرفته‌ای. ' +
            'اختیاری است: اگر رد کنی هیچ چیز تغییر نمی‌کند.') + '</p>' +
      '<div class="wqmeta" dir="ltr">' + meta + '</div>' + note +
      (actions ? '<div class="wqacts">' + actions + '</div>' : '');
  }

  function mountWeek() {
    const chatEl = document.getElementById('chat');
    const old = document.getElementById('weeklyquiz');
    if (old && old.parentNode) old.parentNode.removeChild(old);
    if (!chatEl || !cat) return;
    /* Friday only, from nine in the morning Tehran time. Outside that window
       the card does not exist at all - not greyed out, not counting down: the
       week's review is a Friday morning, and a disabled card sitting in the
       transcript all week is a nag. */
    if (!WeeklyQuiz.isOpen(new Date())) return;
    const snap = snapshot();
    /* A week turned down stays turned down: the card is gone until the next
       period, exactly as the daily card behaves, and no repaint brings it
       back. */
    if (snap.rec && snap.rec.status === 'skipped') return;
    const node = document.createElement('div');
    node.className = 'wqcard';
    node.id = 'weeklyquiz';
    node.setAttribute('role', 'region');
    node.setAttribute('aria-label', 'Weekly quiz — آزمون هفتگی');
    node.innerHTML = cardHtml(snap);
    const daily = document.getElementById('dailyset');
    if (daily && daily.parentNode === chatEl) chatEl.insertBefore(node, daily.nextSibling);
    else chatEl.appendChild(node);
    bindCard(node);
  }

  function bindCard(root) {
    root.querySelectorAll('[data-wq]').forEach((b) => {
      b.addEventListener('click', () => {
        const act = b.dataset.wq;
        if (act === 'skip') skip();
        else if (act === 'review') open('result');
        else open('quiz');
      });
    });
  }

  function skip() {
    const snap = snapshot();
    WeeklyQuiz.write(WeeklyQuiz.setSkipped(snap.state, snap.period));
    mountWeek();
  }

  /* ---- opening the paper ---------------------------------------------- */

  function start() {
    const snap = snapshot();
    if (snap.items.length < WeeklyQuiz.MIN_ITEMS) return null;
    const existing = snap.rec && snap.rec.quiz;
    const quiz = existing || WeeklyQuiz.build(cat, snap.items, snap.period,
      WeeklyQuiz.keyOf(snap.now));
    if (!quiz) return null;
    const state = WeeklyQuiz.setStarted(snap.state, snap.period, quiz);
    WeeklyQuiz.write(state);
    return quiz;
  }

  function open(which) {
    const snap = snapshot();
    const quiz = (snap.rec && snap.rec.quiz) || start();
    if (!quiz) { Panels.set(PANEL, true); renderInsufficient(snap); return; }
    picks = Object.assign({}, (snap.rec && snap.rec.answers) || {});
    view = which === 'result' || (snap.rec && snap.rec.status === 'completed')
      ? 'result' : 'quiz';
    warned = false;
    Panels.set(PANEL, true, render);
  }

  function renderInsufficient(snap) {
    const c = counts(snap.items);
    body().innerHTML = '<div class="wq-wrap"><section class="wq-hero">' +
      '<div class="wq-eyebrow">Weekly quiz · <bdi class="fa" lang="fa" dir="rtl">آزمون هفتگی</bdi></div>' +
      '<h2 class="wq-h">Not enough learned yet</h2>' +
      '<p class="wq-sub" dir="ltr">You have learned ' + snap.items.length + ' of the ' +
      WeeklyQuiz.MIN_ITEMS + ' items a review needs (' + c.words + ' words, ' +
      c.expressions + ' expressions).</p>' +
      '<p class="wq-fa" dir="rtl" lang="fa">از ' + WeeklyQuiz.MIN_ITEMS +
      ' مورد لازم، ' + snap.items.length + ' مورد را یاد گرفته‌ای. به یادگیری ادامه بده؛ ' +
      'آزمون هفتگی وقتی آماده می‌شود که به اندازهٔ کافی یاد گرفته باشی.</p>' +
      '<div class="wq-actions"><button type="button" class="lv-btn ghost" data-wq-close="1">' +
      'Close</button></div></section></div>';
    bindPanel();
  }

  /* ---- the questions --------------------------------------------------- */

  function render() {
    const snap = snapshot();
    const rec = snap.rec;
    if (!rec || !rec.quiz) { renderInsufficient(snap); return; }
    if (view === 'result') renderResult(rec);
    else renderQuiz(rec);
    bindPanel();
  }

  function renderQuiz(rec) {
    const quiz = rec.quiz;
    const i = Math.min(Math.max(0, Number(rec.cursor || 0)), quiz.questions.length - 1);
    const q = quiz.questions[i];
    const last = i === quiz.questions.length - 1;
    body().innerHTML = '<div class="wq-wrap">' +
      '<div class="wq-top">' +
        '<div class="wq-toprow"><span class="wq-chip">Question ' + (i + 1) + ' of ' +
          quiz.questions.length + '</span><span class="wq-chip ghost">' +
          (q.kind === 'word' ? 'Word' : 'Expression') + '</span>' +
        '</div>' +
        '<div class="wq-bar" role="progressbar" aria-valuemin="0" aria-valuemax="' +
          quiz.questions.length + '" aria-valuenow="' + (i + 1) + '">' +
          '<i style="width:' + Math.round(((i + 1) / quiz.questions.length) * 100) + '%"></i></div>' +
      '</div>' +
      '<div class="wq-q" dir="ltr"><p class="wq-prompt">' + esc(q.prompt.en) + '</p>' +
        '<p class="wq-prompt fa" dir="rtl" lang="fa">' + esc(q.prompt.fa) + '</p>' +
        '<div class="wq-opts" role="radiogroup" aria-label="Answer options">' +
        q.options.map((t, n) =>
          '<button type="button" class="wq-opt' + (picks[i] === n ? ' on' : '') +
          '" data-wq-pick="' + n + '" role="radio" aria-checked="' +
          (picks[i] === n ? 'true' : 'false') + '">' +
          '<span class="wq-letter">' + 'ABCD'[n] + '</span>' +
          '<span class="wq-text"' + (/[\u0600-\u06FF]/.test(t) ? ' dir="rtl" lang="fa"' : '') +
          '>' + esc(t) + '</span></button>').join('') +
        '</div></div>' +
      '<div class="wq-foot">' +
        '<button type="button" class="lv-btn ghost" data-wq-go="-1"' +
          (i === 0 ? ' disabled' : '') + '>Back</button>' +
        '<span class="wq-note">' + Object.keys(picks).length + ' of ' +
          quiz.questions.length + ' answered</span>' +
        '<button type="button" class="lv-btn" data-wq-go="1">' +
          (last ? 'See my score' : 'Next') + '</button>' +
      '</div></div>';
  }

  function renderResult(rec) {
    const quiz = rec.quiz;
    const result = rec.result || WeeklyQuiz.grade(quiz, rec.answers);
    const missed = result.missed || [];
    const rows = missed.map((i) => {
      const q = quiz.questions[i];
      const said = q.options[rec.answers[i]] || 'no answer';
      return '<div class="wq-miss"><p class="wq-missq" dir="ltr">' + esc(q.prompt.en) + '</p>' +
        '<p class="wq-said" dir="ltr">You chose: ' + esc(said) + '</p>' +
        '<p class="wq-right" dir="ltr">Answer: ' + esc(q.options[q.answer]) + '</p>' +
        '<p class="wq-detail" dir="ltr">' + esc(q.detail.en) + '</p>' +
        (q.detail.fa ? '<p class="wq-detail fa" dir="rtl" lang="fa">' +
          esc(q.detail.fa) + '</p>' : '') + '</div>';
    }).join('');
    const line = result.percent >= 80
      ? 'Strong week. These are staying with you.'
      : result.percent >= 50
        ? 'A good week. The ones that slipped are below, with their meanings.'
        : 'A hard week, and that is all right: every miss below is a word you have already met.';
    body().innerHTML = '<div class="wq-wrap">' +
      '<section class="wq-hero">' +
        '<div class="wq-eyebrow">This week&rsquo;s review</div>' +
        '<div class="wq-score"><b>' + result.right + '</b><span>of ' + result.total + '</span>' +
          '<em>' + result.percent + '%</em></div>' +
        '<p class="wq-sub" dir="ltr">' + esc(line) + '</p>' +
        '<p class="wq-fa" dir="rtl" lang="fa">' +
          (result.percent >= 80 ? 'هفتهٔ خوبی بود؛ این‌ها در ذهنت می‌مانند.'
            : result.percent >= 50 ? 'هفتهٔ خوبی بود؛ مواردی که از دست رفت پایین‌تر آمده‌اند.'
            : 'هفتهٔ سختی بود و اشکالی ندارد؛ هر پاسخ نادرست واژه‌ای است که قبلاً دیده‌ای.') +
        '</p>' +
        '<p class="wq-sub" dir="ltr">' + result.right + ' correct · ' +
          (result.total - result.right) + ' to review</p>' +
      '</section>' +
      (rows ? '<h4 class="wq-h4" dir="ltr">Words to look at again</h4>' + rows : '') +
      '<div class="wq-actions"><button type="button" class="lv-btn ghost" data-wq-exit="1">' +
        'Back to the chat</button></div></div>';
  }

  function bindPanel() {
    const box = body();
    if (!box) return;
    box.querySelectorAll('[data-wq-close]').forEach((b) => {
      b.addEventListener('click', () => Panels.set(PANEL, false));
    });
    box.querySelectorAll('[data-wq-exit]').forEach((b) => {
      b.addEventListener('click', () => Panels.set(PANEL, false));
    });
    box.querySelectorAll('[data-wq-pick]').forEach((b) => {
      b.addEventListener('click', () => {
        const snap = snapshot();
        if (!snap.rec || !snap.rec.quiz) return;
        const cursor = Number(snap.rec.cursor || 0);
        picks[cursor] = Number(b.dataset.wqPick);
        warned = false;
        const state = snap.state;
        state.periods[snap.period].answers = picks;
        WeeklyQuiz.write(state);
        render();
      });
    });
    box.querySelectorAll('[data-wq-go]').forEach((b) => {
      b.addEventListener('click', () => {
        const snap = snapshot();
        if (!snap.rec || !snap.rec.quiz) return;
        const quiz = snap.rec.quiz;
        const step = Number(b.dataset.wqGo);
        const cursor = Number(snap.rec.cursor || 0);
        if (step > 0 && cursor === quiz.questions.length - 1) { submit(snap, quiz); return; }
        const next = Math.min(Math.max(0, cursor + step), quiz.questions.length - 1);
        snap.state.periods[snap.period].cursor = next;
        WeeklyQuiz.write(snap.state);
        render();
        body().scrollTop = 0;
      });
    });
  }

  /* The week's answers are also the best evidence the app will ever have about
     what is still in memory: a right answer is a recall after at least a day,
     a wrong one is a lapse. So the paper feeds the mastery ledger, and each
     miss is handed to the error log as a recall question the drill can ask
     again. Nothing here is scored twice - Mastery reads the verdict, ErrorLog
     reads the card. */
  function recordWeek(quiz, answers) {
    const today = WeeklyQuiz.tehranKey(new Date());
    let state = Mastery.seedDaily(Mastery.read(), cat, DailyStore.read().days, today);
    let log = ErrorLog.read();
    quiz.questions.forEach((q, i) => {
      const key = Mastery.itemKey(q.kind, q.item);
      if (!state.items[key]) return;
      const right = answers[i] != null && Number(answers[i]) === q.answer;
      state = Mastery.grade(state, key, right ? 2 : 0, today);
      if (!right) {
        log = ErrorLog.note(log,
          {key: 'recall', en: 'Vocabulary recall', fa: 'یادآوری واژه'},
          {id: q.id, kind: 'choice', prompt: q.prompt, options: q.options,
           answer: q.answer, why: q.detail, detail: q.detail}, today);
      }
    });
    Mastery.write(state);
    ErrorLog.write(log);
    if (typeof Slip !== 'undefined') Slip.refresh();
  }

  /* One submission per week. The record holds the status, so a double tap, a
     reload or a second tab lands on the same result rather than two. */
  function submit(snap, quiz) {
    if (snap.rec && snap.rec.status === 'completed') { view = 'result'; render(); return; }
    const answered = quiz.questions.filter((q, i) => picks[i] != null).length;
    if (answered < quiz.questions.length && !warned) {
      warned = true;
      const foot = body().querySelector('.wq-note');
      if (foot) foot.textContent = (quiz.questions.length - answered) +
        ' still unanswered — tap again to finish anyway';
      return;
    }
    const result = WeeklyQuiz.grade(quiz, picks);
    result.at = WeeklyQuiz.keyOf(new Date());
    WeeklyQuiz.write(WeeklyQuiz.setCompleted(snap.state, snap.period, quiz, picks, result));
    recordWeek(quiz, picks);
    view = 'result';
    render();
    body().scrollTop = 0;
  }

  /* Today's card is mounted by Daily; the week's card goes right after it, and
     is rebuilt with it when the day turns over. One timer is set for the next
     Friday 09:00, so the card appears in the window it belongs to without the
     learner reloading the page. */
  async function init() {
    try {
      cat = await loadJSON('daily');
    } catch (e) {
      cat = null;
    }
    mountWeek();
    arm();
  }

  let timer = 0;
  function arm() {
    clearTimeout(timer);
    const wait = WeeklyQuiz.opensAt(new Date()).getTime() - Date.now();
    // a long wait is left to the next launch: setTimeout is signed 32-bit and
    // overflows at about 24 days, and a week-long timer adds nothing here
    if (!(wait > 0) || wait > 6 * 86400000) return;
    timer = setTimeout(() => { mountWeek(); arm(); }, wait + 1000);
  }

  return {init, mountCard: mountWeek, start, open, skip, refresh: mountWeek,
          PANEL: PANEL};
})();
/* ============================================================================
 * PRACTICE
 * Five drills that use content the app already ships, in one sheet, reached
 * from one card in the transcript. Each of them tests something the app could
 * not test before:
 *
 *   Word partners  collocations.json - "heavy rain", not "strong rain"
 *   Register       register.json - one meaning, three levels of formality
 *   Ear test       the minimal pairs the phonetics panel only ever listed
 *   Dictation      hearing a sentence and writing it, word by word
 *   Say it         reading a sentence aloud and seeing which words the
 *                  recogniser did not hear
 *
 * None of it is generated and none of it needs the network: the questions are
 * drawn from the files, seeded by the local date so a day asks the same five
 * questions twice, and every miss is handed to the error log so the account
 * panel can show what keeps slipping.
 * ==========================================================================*/
const Practice = (() => {
  const PANEL = 'prpanel';
  /* key, English, Persian, and one line saying what the drill asks - the last
     of which is what the drawer's rows are built from. */
  const TABS = [
    ['coll', 'Word partners', 'هم‌نشینی',
      'Which word goes with which — heavy rain, not strong rain.'],
    ['reg', 'Register', 'لحن',
      'One meaning at three levels of formality.'],
    ['ear', 'Ear test', 'جفت‌های صوتی',
      'Hear a word, pick it from a pair that sounds alike.'],
    ['dict', 'Dictation', 'دیکته',
      'Hear a sentence, type it, marked word by word.'],
    ['say', 'Say it', 'بگو',
      'Read aloud; see which words were heard.'],
    ['slip', 'What slips', 'اشتباه‌ها',
      'The questions you missed, asked again.'],
  ];
  const cls = (key, en, fa) => ({key: key, en: en, fa: fa});

  let loaded = false;
  let data = {coll: null, reg: null, pairs: null, listen: null};
  let tab = 'coll';
  let idx = 0;
  let picked = null;
  let typed = '';
  let checked = null;
  let said = '';
  let level = 0;
  let slipKey = null;
  let slipAt = 0;

  const body = () => document.getElementById('prbody');
  const today = () => Mastery.keyOf(new Date());
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"]/g,
    (c) => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
  const seed = (salt) => Mastery.dayOf(today()) + idx * 13 + salt;

  async function load() {
    if (loaded) return;
    loaded = true;
    try { data.coll = await loadJSON('collocations'); } catch (e) { data.coll = {entries: []}; }
    try { data.reg = await loadJSON('register'); } catch (e) { data.reg = {pairs: []}; }
    try { data.pairs = Drills.pairs(await loadJSON('phonetics')); } catch (e) { data.pairs = []; }
    try { data.listen = Drills.levels(await loadJSON('listening')); } catch (e) { data.listen = []; }
  }

  /* ---- the sheet ------------------------------------------------------- */

  function setTab(which) {
    if (!TABS.some((t) => t[0] === which)) return;
    tab = which;
    idx = 0; picked = null; typed = ''; checked = null; said = '';
  }

  async function open(which, key) {
    await load();
    /* coming back to the drill that is already selected keeps what was typed,
       answered or heard; choosing a different one starts it clean */
    if (which && which !== tab) setTab(which);
    if (key) {
      slipKey = key;
      slipAt = 0;
      tab = 'slip';
      // the class changed, so an answer given to the last one is not this one's
      picked = null; checked = null; typed = '';
    }
    Panels.set(PANEL, true, render);
  }

  function listeningSet() {
    const levels = Drills.levels(data.listen);
    if (!levels.length) return [];
    /* the chosen level first, then the nearest one that actually has lines, so
       a level that was emptied cannot take dictation down with it */
    const at = Math.min(level, levels.length - 1);
    const order = [at].concat(levels.map((_, n) => n).filter((n) => n !== at));
    for (const n of order) {
      const lv = levels[n];
      if (lv && Array.isArray(lv.sentences) && lv.sentences.length) return lv.sentences;
    }
    return [];
  }

  function sentenceFor(salt) {
    const list = listeningSet();
    if (!list.length) return null;
    return list[Mastery.dayOf(today()) * 7 % list.length + (idx * 3 + salt) % list.length];
  }

  /* The drill is the page now, and the list of drills is the drawer - so the
     page carries the way back rather than a second row of tabs. */
  function backRow() {
    return '<button type="button" class="prback" data-pr-back="1" ' +
      'aria-label="Back to the practice list — بازگشت به فهرست تمرین">' +
      '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" ' +
      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      '<path d="M9.5 3.5 5 8l4.5 4.5"/></svg>' +
      'All drills<span class="fa" dir="rtl" lang="fa">همهٔ تمرین‌ها</span></button>';
  }

  const optionsHtml = (q, choice) =>
    '<div class="wq-opts" role="radiogroup">' + q.options.map((t, n) => {
      let state = '';
      if (choice != null) {
        if (n === q.answer) state = ' right';
        else if (n === choice) state = ' wrong';
      }
      return '<button type="button" class="wq-opt' + (choice === n ? ' on' : '') +
        state + '" data-pr-opt="' + n + '" role="radio">' +
        '<span class="wq-letter">' + 'ABCD'[n] + '</span>' +
        '<span class="wq-text"' + (/[\u0600-\u06FF]/.test(t) ? ' dir="rtl" lang="fa"' : '') +
        '>' + esc(t) + '</span></button>';
    }).join('') + '</div>';

  function feedbackHtml(q, choice) {
    if (choice == null) return '';
    const ok = choice === q.answer;
    return '<div class="wq-miss" style="margin-top:10px">' +
      '<p class="wq-said" dir="ltr">' + (ok ? '✓ Correct' : '✗ The answer is ' +
        esc(q.options[q.answer])) + '</p>' +
      '<p class="wq-detail" dir="ltr">' + esc(q.why && q.why.en ? q.why.en : '') + '</p>' +
      (q.detail && q.detail.en ? '<p class="wq-detail" dir="ltr">' + esc(q.detail.en) + '</p>' : '') +
      (q.detail && q.detail.fa ? '<p class="wq-detail fa" dir="rtl" lang="fa">' +
        esc(q.detail.fa) + '</p>' : '') + '</div>';
  }

  function questionHtml(q, choice, playLabel) {
    return '<div class="wq-q">' +
      '<p class="wq-prompt" dir="ltr">' + esc(q.prompt.en) + '</p>' +
      '<p class="wq-prompt fa" dir="rtl" lang="fa">' + esc(q.prompt.fa) + '</p>' +
      (playLabel ? '<div class="wq-foot" style="border:0;padding:8px 0 0">' +
        '<button type="button" class="prmic" data-pr-play="1">🔊 ' + playLabel +
        '</button></div>' : '') +
      optionsHtml(q, choice) + feedbackHtml(q, choice) + '</div>';
  }

  function dictationHtml() {
    const s = sentenceFor(1);
    if (!s) return '<p class="prnote">The listening bank is not on this device.</p>';
    return '<div class="wq-q">' +
      '<p class="wq-prompt" dir="ltr">Type the sentence you hear.</p>' +
      '<p class="wq-prompt fa" dir="rtl" lang="fa">جمله‌ای را که می‌شنوی بنویس.</p>' +
      '<button type="button" class="prmic" data-pr-play="1">🔊 Play again · دوباره</button>' +
      '<textarea class="prtype" data-pr-type="1" dir="ltr" spellcheck="false" ' +
        'placeholder="Type what you heard…">' + esc(typed) + '</textarea>' +
      (checked ? '<div class="prdiff">' + checked.words.map((w) =>
        '<span class="w' + (w.ok ? '' : ' miss') + '">' +
        esc(w.w) + '</span>').join('') + '</div>' +
        '<p class="wq-detail" dir="ltr">' + checked.right + ' of ' + checked.total +
        ' words (' + checked.percent + '%)</p>' +
        '<p class="wq-detail" dir="ltr">' + esc(s.en) + '</p>' +
        '<p class="wq-detail fa" dir="rtl" lang="fa">' + esc(s.fa || '') + '</p>' : '') +
      '<div class="wq-actions">' +
        (checked ? '<button type="button" class="lv-btn" data-pr-next="1">Next</button>'
          : '<button type="button" class="lv-btn" data-pr-check="1">Check</button>') +
      '</div></div>';
  }

  function sayHtml() {
    const s = sentenceFor(2);
    if (!s) return '<p class="prnote">The listening bank is not on this device.</p>';
    const diff = said ? SayMatch.compare(s.en, said) : null;
    return '<div class="wq-q">' +
      '<p class="wq-prompt" dir="ltr">' + esc(s.en) + '</p>' +
      '<p class="wq-prompt fa" dir="rtl" lang="fa">' + esc(s.fa || '') + '</p>' +
      '<p class="prnote" dir="ltr">Read it aloud. The app compares the words it '
      + 'heard with the words on screen - it is not a phoneme score.</p>' +
      '<p class="prnote fa" dir="rtl" lang="fa">بلند بخوان. برنامه واژه‌هایی را که '
      + 'شنیده با واژه‌های روی صفحه مقایسه می‌کند، نه امتیاز تک‌تک صداها را.</p>' +
      '<div class="wq-actions" style="margin-top:8px">' +
        '<button type="button" class="prmic" data-pr-play="1">🔊 Listen · گوش بده</button>' +
        '<button type="button" class="prmic' + (STT.listening ? ' rec' : '') +
        '" data-pr-mic="1">🎙 ' + (STT.listening ? 'Listening…' : 'Say it') + '</button>' +
      '</div>' +
      (diff ? '<div class="prdiff">' + diff.words.map((w) =>
        '<span class="w' + (w.ok ? '' : ' miss') + '">' + esc(w.w) + '</span>').join('') +
        '</div>' +
        '<p class="wq-detail" dir="ltr">' + diff.right + ' of ' + diff.total +
        ' words heard (' + diff.percent + '%)' +
        (diff.missing.length ? ' · not heard: ' + esc(diff.missing.join(', ')) : '') +
        '</p>' : '') +
      '<div class="wq-actions">' +
        '<button type="button" class="lv-btn" data-pr-next="1">Next sentence</button>' +
      '</div></div>';
  }

  function slipHtml() {
    const log = ErrorLog.read();
    const ranked = ErrorLog.rank(log);
    if (!ranked.length) {
      return '<p class="prnote" dir="ltr">Nothing has been missed yet. The level '
        + 'check, the weekly quiz and these drills all feed this list.</p>' +
        '<p class="prnote fa" dir="rtl" lang="fa">هنوز چیزی از دست نرفته است. سنجش سطح، '
        + 'آزمون هفتگی و همین تمرین‌ها این فهرست را می‌سازند.</p>';
    }
    const key = slipKey && ranked.some((r) => r.key === slipKey) ? slipKey : ranked[0].key;
    const cardsNow = ErrorLog.drill(log, key, 6);
    const head = ranked.map((r) =>
      '<button type="button" class="prtab' + (r.key === key ? ' on' : '') +
      '" data-pr-class="' + esc(r.key) + '">' + esc(r.en) + ' · ' + r.count + '</button>').join('');
    const card = cardsNow[Math.min(slipAt, cardsNow.length - 1)];
    if (!card) {
      return '<div class="prtabs">' + head + '</div>' +
        '<p class="prnote">No question was kept for this class.</p>';
    }
    const isType = card.kind === 'type';
    const diff = checked && isType ? checked : null;
    return '<div class="prtabs">' + head + '</div>' +
      '<div class="wq-q" style="margin-top:10px">' +
        '<p class="wq-prompt" dir="ltr">' + esc(card.prompt.en) + '</p>' +
        (card.prompt.fa ? '<p class="wq-prompt fa" dir="rtl" lang="fa">' +
          esc(card.prompt.fa) + '</p>' : '') +
        (isType
          ? '<textarea class="prtype" data-pr-type="1" dir="ltr" spellcheck="false">' +
            esc(typed) + '</textarea>' +
            (diff ? '<div class="prdiff">' + diff.words.map((w) =>
              '<span class="w' + (w.ok ? '' : ' miss') + '">' + esc(w.w) +
              '</span>').join('') + '</div>' +
              '<p class="wq-detail" dir="ltr">' + esc(String(card.answer)) + '</p>' : '')
          : (picked == null ? '' : optionsHtml({
              options: card.options, answer: Number(card.answer)}, picked))) +
        (picked != null && !isType
          ? '<div class="wq-miss" style="margin-top:10px"><p class="wq-said" dir="ltr">' +
            (picked === Number(card.answer) ? '✓ Correct' : '✗ The answer is ' +
              esc(String(card.options[Number(card.answer)] || ''))) + '</p>' +
            '<p class="wq-detail" dir="ltr">' + esc(card.why.en || '') + '</p>' +
            (card.detail.en ? '<p class="wq-detail" dir="ltr">' + esc(card.detail.en) +
              '</p>' : '') + '</div>'
          : '') +
        (picked == null && !isType ? optionsHtml({
            options: card.options, answer: Number(card.answer)}, null) : '') +
        '<div class="wq-actions">' +
          ((isType && !diff)
            ? '<button type="button" class="lv-btn" data-pr-check="1">Check</button>'
            : '<button type="button" class="lv-btn" data-pr-next="1">Next</button>') +
        '</div></div>';
  }

  function levelRow() {
    const levels = Array.isArray(data.listen) ? data.listen : [];
    if (!levels.length || (tab !== 'dict' && tab !== 'say')) return '';
    return '<div class="prtabs">' + levels.map((lv, n) =>
      '<button type="button" class="prtab' + (n === level ? ' on' : '') +
      '" data-pr-level="' + n + '">' + esc(lv.id) + '</button>').join('') + '</div>';
  }

  /* The sheet, as markup - the page's own body. The drawer only lists the
     drills, so this string is drawn in exactly one place: #prbody. */
  function sheetHtml() {
    let inner = '';
    if (tab === 'coll') {
      const q = Drills.collocation(data.coll, seed(1));
      inner = q ? questionHtml(q, picked) : '<p class="prnote">No word partners are on this device.</p>';
    } else if (tab === 'reg') {
      const q = Drills.register(data.reg, seed(2));
      inner = q ? questionHtml(q, picked) : '<p class="prnote">Register data is not on this device.</p>';
    } else if (tab === 'ear') {
      const q = Drills.pairQuestion(data.pairs, seed(3));
      inner = q ? questionHtml(q, picked, 'Play · پخش') :
        '<p class="prnote">No sound pairs were found in the phonetics bank.</p>';
    } else if (tab === 'dict') {
      inner = dictationHtml();
    } else if (tab === 'say') {
      inner = sayHtml();
    } else {
      inner = slipHtml();
    }
    return '<div class="prwrap">' + backRow() + levelRow() + inner + '</div>';
  }

  function render() {
    const box = body();
    if (box) box.innerHTML = sheetHtml();
    /* the drawer is navigation only: nothing of the drill is drawn there */
  }

  /* ---- answers --------------------------------------------------------- */

  function currentQuestion() {
    if (tab === 'coll') return Drills.collocation(data.coll, seed(1));
    if (tab === 'reg') return Drills.register(data.reg, seed(2));
    if (tab === 'ear') return Drills.pairQuestion(data.pairs, seed(3));
    return null;
  }

  function note(clsObj, card) {
    ErrorLog.write(ErrorLog.note(ErrorLog.read(), clsObj, card, today()));
    if (typeof Slip !== 'undefined') Slip.refresh();
  }

  function choose(n) {
    if (tab === 'slip') {
      const log = ErrorLog.read();
      const ranked = ErrorLog.rank(log);
      const key = slipKey && ranked.some((r) => r.key === slipKey) ? slipKey : (ranked[0] || {}).key;
      const cards = ErrorLog.drill(log, key, 6);
      const card = cards[Math.min(slipAt, cards.length - 1)];
      if (!card) return;
      picked = n;
      render();
      return;
    }
    const q = currentQuestion();
    if (!q) return;
    picked = n;
    if (n !== q.answer) {
      note(q.cls, {id: q.id, kind: 'choice', prompt: q.prompt, options: q.options,
                   answer: q.answer, why: q.why, detail: q.detail});
    }
    render();
  }

  function check() {
    if (tab === 'slip') {
      const log = ErrorLog.read();
      const ranked = ErrorLog.rank(log);
      const key = slipKey && ranked.some((r) => r.key === slipKey) ? slipKey : (ranked[0] || {}).key;
      const cards = ErrorLog.drill(log, key, 6);
      const card = cards[Math.min(slipAt, cards.length - 1)];
      if (!card || card.kind !== 'type') return;
      checked = SayMatch.compare(String(card.answer), typed);
      if (checked.percent < 80) {
        note(cls(card.c || 'recall', 'Recall', 'یادآوری'),
          {id: card.id, kind: 'type', prompt: card.prompt, answer: String(card.answer),
           why: card.why, detail: card.detail});
      }
      render();
      return;
    }
    const s = sentenceFor(tab === 'dict' ? 1 : 2);
    if (!s) return;
    const heard = tab === 'dict' ? typed : said;
    checked = SayMatch.compare(s.en, heard);
    if (checked.percent < 80) {
      note(tab === 'dict' ? cls('dictation', 'Dictation', 'دیکته')
                          : cls('speaking', 'Speaking', 'گفتار'),
        {id: (tab === 'dict' ? 'dict:' : 'say:') + Drills.hash(s.en),
         kind: 'type', prompt: {en: s.en, fa: s.fa || ''}, answer: s.en,
         why: {en: 'Hear it again and say it in one breath.', fa: ''},
         detail: {en: s.en, fa: s.fa || ''}});
    }
    render();
  }

  function next() {
    idx += 1;
    picked = null; typed = ''; checked = null; said = '';
    if (tab === 'slip') slipAt += 1;
    render();
  }

  function play() {
    if (tab === 'ear') {
      const q = Drills.pairQuestion(data.pairs, seed(3));
      if (q) Speech.speak(q.say);
      return;
    }
    if (tab === 'dict') { const s = sentenceFor(1); if (s) Speech.speak(s.en); return; }
    if (tab === 'say') { const s = sentenceFor(2); if (s) Speech.speak(s.en); }
  }

  function mic() {
    if (STT.listening) { STT.stop(); render(); return; }
    if (!STT.supported()) {
      toast('This device has no speech recognition — the ear test and dictation ' +
        'work without a microphone. / این دستگاه تشخیص گفتار ندارد.', 4200);
      return;
    }
    STT.sink = (text) => {
      said = text || '';
      STT.sink = null;
      if (tab === 'say' && said) check();
      else render();
    };
    if (!STT.begin()) {
      STT.sink = null;
      toast('Could not start the microphone — check the permission.', 3600);
    }
    render();
  }

  /* One set of handlers, bound to whichever box is showing the sheet: the
     section's body, the drawer's, or both. */
  function bindTo(el) {
    const box = el;
    if (!box || box.dataset.prBound) return;
    box.dataset.prBound = '1';
    box.addEventListener('click', (e) => {
      const t = e.target.closest('[data-pr-back],[data-pr-tab],[data-pr-opt],[data-pr-next],[data-pr-play],' +
        '[data-pr-check],[data-pr-level],[data-pr-mic],[data-pr-class]');
      if (!t) return;
      if (t.dataset.prBack != null) { Panels.set(PANEL, false); return; }
      if (t.dataset.prTab != null) { setTab(t.dataset.prTab); render(); return; }
      if (t.dataset.prOpt != null) { choose(Number(t.dataset.prOpt)); return; }
      if (t.dataset.prNext != null) { next(); return; }
      if (t.dataset.prPlay != null) { play(); return; }
      if (t.dataset.prCheck != null) { check(); return; }
      if (t.dataset.prLevel != null) { level = Number(t.dataset.prLevel); idx = 0; typed = ''; said = ''; checked = null; render(); return; }
      if (t.dataset.prMic != null) { mic(); return; }
      if (t.dataset.prClass != null) { slipKey = t.dataset.prClass; slipAt = 0; picked = null; checked = null; typed = ''; render(); }
    });
    box.addEventListener('input', (e) => {
      if (!e.target || e.target.dataset.prType == null) return;
      typed = e.target.value;
    });
  }

  function bind() { bindTo(body()); }

  async function init() {
    bind();
    await load();
  }

  return {init, open, setTab, bindTo, sheetHtml, ensure: load, PANEL: PANEL, TABS: TABS};
})();

/* ============================================================================
 * PRACTICE DRAWER
 *
 * The only way into Practice: a circular control in the corner of the
 * transcript that unfolds the list of activities. It is navigation, not a
 * second sheet - choosing an item opens that drill as a full page, the same
 * #prpanel every other section uses, and closing the page folds the list back
 * open. The rows are built from Practice.TABS, so the navigation and the sheet
 * cannot drift into two different sets of drills.
 *
 * Closed, the drawer is visibility:hidden and takes no pointer events, so it
 * is neither a tab stop nor an invisible target over the transcript.
 * ==========================================================================*/
const PracticeDrawer = (() => {
  let open = false;
  let bound = false;
  /* true while the panel on screen was opened from this list, which is what
     makes closing it come back here rather than drop to the transcript */
  let fromList = false;

  const root = () => document.getElementById('prdrawer');
  const fab = () => document.getElementById('prfab');
  const nav = () => document.getElementById('prdnav');

  const ICONS = {
    coll: '<circle cx="9.2" cy="12" r="5.2"/><circle cx="14.8" cy="12" r="5.2"/>',
    reg: '<path d="M5 19V9.5M12 19V5M19 19v-6.5"/><path d="M3 19h18"/>',
    ear: '<path d="M3.4 10.6v2.8M7.6 7.4v9.2M12 4.2v15.6M16.4 7.4v9.2M20.6 10.6v2.8"/>',
    dict: '<path d="M3.8 20.2h16.4"/><path d="M6.4 16.4l9-9a1.9 1.9 0 0 1 2.7 2.7l-9 9-3.6.9z"/>',
    say: '<rect x="9" y="3" width="6" height="10.5" rx="3"/><path d="M5.6 11.4a6.4 6.4 0 0 0 12.8 0"/><path d="M12 17.8V21"/>',
    slip: '<path d="M5.4 21V3.4"/><path d="M5.4 4.4h11.2l-2.4 4 2.4 4H5.4z"/>',
  };

  /* Built once, from the sheet's own list: an activity added to Practice.TABS
     appears here without a second edit. */
  function rowsHtml() {
    return Practice.TABS.map(([k, en, fa, sub], i) =>
      '<button type="button" class="prditem" data-pr-open="' + k + '" ' +
      'style="--i:' + i + '" title="' + escAttr(en + ' — ' + fa) + '">' +
        '<span class="prdico" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" ' +
          'stroke="currentColor" stroke-width="1.7" stroke-linecap="round" ' +
          'stroke-linejoin="round">' + (ICONS[k] || '') + '</svg></span>' +
        '<span class="prdtxt">' +
          '<span class="prden">' + en +
            '<span class="fa" dir="rtl" lang="fa">' + fa + '</span></span>' +
          '<span class="prdsub">' + (sub || '') + '</span>' +
        '</span>' +
        '<svg class="prdchev" viewBox="0 0 16 16" fill="none" stroke="currentColor" ' +
          'stroke-width="2" stroke-linecap="round" aria-hidden="true">' +
          '<path d="M6 3.5 10.5 8 6 12.5"/></svg>' +
      '</button>').join('');
  }

  const escAttr = (s) => String(s == null ? '' : s)
    .replace(/[&<>"]/g, (c) => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));

  function setOpen(on, refocus) {
    const r = root(), f = fab();
    if (!r || !f) return;
    open = !!on;
    r.classList.toggle('on', open);
    r.setAttribute('aria-hidden', open ? 'false' : 'true');
    f.setAttribute('aria-expanded', open ? 'true' : 'false');
    f.setAttribute('aria-label', open ? 'Close practice — بستن تمرین'
                                       : 'Practice — تمرین');
    f.title = f.getAttribute('aria-label');
    if (open) {
      const first = nav() && nav().querySelector('.prditem');
      if (first) first.focus({preventScroll: true});
    } else if (refocus) {
      f.focus({preventScroll: true});
    }
  }

  function toggle() { setOpen(!open, true); }

  /* Choosing an item: the list folds away and the drill takes the page. */
  async function choose(which) {
    await Practice.ensure();
    fromList = true;
    setOpen(false);
    Practice.open(which);
  }

  function bind() {
    if (bound) return;
    const r = root(), f = fab(), n = nav();
    if (!r || !f || !n) return;
    bound = true;
    n.innerHTML = rowsHtml();
    f.addEventListener('click', toggle);
    r.addEventListener('click', (e) => {
      if (e.target.closest('[data-pr-drawer="close"]')) { setOpen(false, true); return; }
      const item = e.target.closest('[data-pr-open]');
      if (item) choose(item.dataset.prOpen);
    });
    /* Captured, and before the panel shell's own Escape: closing a drill
       reopens this list, and an Escape that then reached the shell would be
       the second handler to act on one keypress. */
    document.addEventListener('keydown', (e) => {
      if (e.key !== 'Escape' || !open) return;
      e.preventDefault();
      e.stopPropagation();
      setOpen(false, true);
    }, true);
    document.addEventListener('click', (e) => {
      if (!open) return;
      const path = typeof e.composedPath === 'function' ? e.composedPath() : [];
      /* the drawer, the control - and the page itself, because closing a drill
         reopens this list from inside the panel's own close button, and that
         same click must not then read as a click outside */
      if (path.includes(r) || path.includes(f)) return;
      if (path.some((el) => el && el.id === Practice.PANEL)) return;
      if (e.target && e.target.closest &&
          (e.target.closest('#prdrawer') || e.target.closest('#prfab'))) return;
      setOpen(false);
    });
    /* Closing a drill returns to the list it was chosen from. */
    Panels.onClose(Practice.PANEL, () => {
      if (!fromList) return;
      fromList = false;
      setOpen(true);
    });
  }

  async function init() {
    bind();
    await Practice.ensure();
  }

  /* Bound at definition, not at boot: the control is on screen the moment the
     transcript is, and waiting for the banks to load before it answers a tap
     made the first tap of a cold start do nothing. */
  bind();

  return {init, toggle, setOpen, choose, isOpen: () => open};
})();

/* The account panel's "what keeps slipping" list. It is a view of one file,
   the error log, and it routes straight into the drill for a class. */
const Slip = (() => {
  function ranked() { return ErrorLog.rank(ErrorLog.read()); }

  function html() {
    const rows = ranked().slice(0, 4);
    if (!rows.length) {
      return '<div class="ac-slip"><p class="empty" dir="ltr">Nothing recorded yet. ' +
        'The level check, the weekly quiz and the practice drills feed this list.' +
        '</p><p class="empty fa" dir="rtl" lang="fa">هنوز چیزی ثبت نشده؛ سنجش سطح، ' +
        'آزمون هفتگی و تمرین‌ها این فهرست را می‌سازند.</p></div>';
    }
    return '<div class="ac-slip">' + rows.map((r) =>
      '<div class="ac-sliprow"><span class="n">' + escapeHtml(r.en) +
      '<i lang="fa" dir="rtl">' + escapeHtml(r.fa || '') + '</i></span>' +
      '<span class="c">' + r.count + '×</span>' +
      '<button type="button" data-slip="' + escapeHtml(r.key) + '">Practise</button></div>')
      .join('') + '</div>';
  }

  /* Only the panel that is on screen needs repainting; this is called from a
     drill on a tab the account panel cannot see. */
  function refresh() {
    const host = document.getElementById('acslip');
    if (host) host.innerHTML = html();
  }

  /* The rows are inside the account panel, which repaints itself on every
     change, so the routing is delegated from the document rather than bound to
     the buttons that are about to be replaced. */
  function init() {
    document.addEventListener('click', (e) => {
      if (!e.target || !e.target.closest) return;
      const btn = e.target.closest('[data-slip]');
      if (!btn) return;
      Practice.open('slip', btn.dataset.slip);
    });
  }

  return {html, refresh, ranked, init};
})();

/* --- learning path: pure, executed by tools/check_path.py ---------------
   One structure for every CEFR level, filled in for one of them. A level is a
   course, a course is units, a unit is lessons, a lesson is explanation,
   examples, guided practice and exercises. Nothing here knows the letter A1:
   the page reads path.json, and the next level is a second entry in
   `courses` with the same shape.

   What the model does and the view does not:
     - where the learner starts, read from the level check's own result
     - what a level's status is (current, done, locked, awaiting)
     - lesson and skill progress over a course
     - the exam paper: the same questions the same way for every skill
     - marking: objective answers, the writing rubric the level check already
       uses, and the recogniser's word match for speaking
   ==========================================================================*/
const PathModel = {
  ORDER: ['PRE', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2'],
  SKILLS: ['grammar', 'vocabulary', 'reading', 'listening', 'writing', 'speaking'],
  PASS: 0.6,
  FLOOR: 0.5,

  /* The starting level is the level check's own overall band, never a guess and
     never a default of A1. A paper that scored below the first band is
     reported as 'Pre-A1' and opens on the PRE card - the name and the id are
     both accepted, because the assessment writes one and path.json the other. */
  startLevel(result) {
    const raw = result && (result.overall || result.band);
    const id = raw == null ? '' : String(raw).trim().toUpperCase();
    if (id === 'PRE' || id === 'PRE-A1' || id === 'PRE A1') return 'PRE';
    return this.ORDER.indexOf(id) >= 0 ? id : 'PRE';
  },

  /* done     - its final exam has been passed
     current  - the learner's assessed level, and there is a course for it
     awaiting - a level whose curriculum is not written: the assessed level
                itself, or the level that follows one the learner has passed
     available- a lower level with a course, open to revisit
     past     - a lower level with no course: behind them, nothing to open
     locked   - above the learner, and nothing has been passed to reach it

     `nearest` is the level a learner who has nothing to start should be
     offered: when the assessed level's own course is not written yet (Pre-A1
     today) the nearest written level above it is open, under its own name and
     with its own button - an offer, not a redirect. Everything else above the
     learner stays locked. */
  status(id, start, hasCourse, passed, belowPassed, nearest = null) {
    if (passed) return 'done';
    const at = this.ORDER.indexOf(id);
    const from = this.ORDER.indexOf(start);
    if (at < 0 || from < 0) return 'locked';
    if (id === start) return hasCourse ? 'current' : 'awaiting';
    if (at < from) return hasCourse ? 'available' : 'past';
    /* Passing the level directly below opens this one: with a course it is
       open to start, and without one it is the next space, waiting for its
       curriculum. Only the level immediately below counts, so a pass at A1
       never opens B1. */
    if (belowPassed && hasCourse) return 'available';
    if (!hasCourse && belowPassed) return 'awaiting';
    if (hasCourse && nearest && id === nearest) return 'available';
    return 'locked';
  },

  /* Flat lesson list with its unit attached, in curriculum order. */
  lessons(course) {
    const out = [];
    (course && course.units ? course.units : []).forEach((u) => {
      (u.lessons || []).forEach((l) => out.push({unit: u, lesson: l}));
    });
    return out;
  },

  /* A lesson counts as done when its record says so; the record is written by
     the lesson page only after its exercises are checked and passed. */
  done(prog, lessonId) {
    const lv = prog && prog.lessons ? prog.lessons[lessonId] : null;
    return !!(lv && lv.done);
  },

  stats(course, prog) {
    const rows = this.lessons(course);
    const bySkill = {};
    this.SKILLS.forEach((s) => { bySkill[s] = {done: 0, total: 0}; });
    let done = 0;
    rows.forEach((row) => {
      const s = row.lesson.skill === 'review' ? null : row.lesson.skill;
      if (s && bySkill[s]) bySkill[s].total += 1;
      if (this.done(prog, row.lesson.id)) {
        done += 1;
        if (s && bySkill[s]) bySkill[s].done += 1;
      }
    });
    return {
      total: rows.length, done: done,
      share: rows.length ? done / rows.length : 0,
      bySkill: bySkill,
      complete: rows.length > 0 && done === rows.length,
    };
  },

  /* Every exam question, flattened, with a stable id and the skill it belongs
     to. Reading questions live inside a passage group; listening items carry
     their own sentence to speak. */
  paper(exam) {
    const out = [];
    ((exam && exam.sections) || []).forEach((section) => {
      (section.items || []).forEach((item, i) => {
        if (section.skill === 'reading') {
          (item.questions || []).forEach((q, k) => out.push({
            id: 'reading.' + i + '.' + k, skill: 'reading', kind: 'mcq',
            item: q, passage: item,
          }));
        } else {
          out.push({id: section.skill + '.' + i, skill: section.skill,
                    kind: item.kind, item: item});
        }
      });
    });
    return out;
  },

  answerRight(item, value) {
    if (!item) return false;
    if (item.kind === 'gap') {
      const norm = (x) => SayMatch.clean(String(x == null ? '' : x));
      const wanted = (item.answer || []).map(norm);
      return wanted.indexOf(norm(value)) >= 0;
    }
    return Number(value) === Number(item.answer);
  },

  /* The writing rubric is the level check's own: length, sentences, one
     required link, and fewer than two slips. Reusing it keeps one standard for
     writing in the whole app instead of two. The sentence count rises with the
     level, so a B1 task is not marked as if it were A1. */
  SENTENCES: {PRE: 3, A1: 3, A2: 4, B1: 5, B2: 6, C1: 6, C2: 6},

  writingScore(item, text, level) {
    const band = item.band || level || 'A1';
    const sentences = this.SENTENCES[band] || 3;
    const bank = {writingScale: {[band]: {words: item.words || 30, sentences: sentences}}};
    return Level.markWriting(bank, {band: band, needs: item.needs || []}, text || '');
  },

  /* Speaking is marked only from words the device actually heard. An empty
     transcript is not a zero - it is no evidence at all. */
  speakingScore(items, heard) {
    const marks = items.map((item, i) => {
      const said = (heard || {})[i] || '';
      const cmp = SayMatch.compare(item.say, said);
      return {id: 'speaking.' + i, said: said, percent: cmp.percent,
              right: cmp.right, total: cmp.total, missing: cmp.missing,
              empty: cmp.empty};
    });
    const assessed = marks.length > 0 && marks.every((m) => !m.empty);
    const share = marks.length
      ? marks.reduce((n, m) => n + m.percent, 0) / (marks.length * 100) : 0;
    return {assessed: assessed, share: share, marks: marks};
  },

  /* One number per skill, then the paper's own rule: 60% overall, 50% in every
     skill, and speaking actually measured. */
  grade(exam, answers, texts, heard, level) {
    const out = {skills: {}, missing: []};
    const paper = this.paper(exam);
    const objective = (skill) => {
      const rows = paper.filter((q) => q.skill === skill);
      const right = rows.filter((q) => this.answerRight(q.item, (answers || {})[q.id])).length;
      return {right: right, total: rows.length,
              share: rows.length ? right / rows.length : 0, assessed: true};
    };
    ['grammar', 'vocabulary', 'reading', 'listening'].forEach((s) => {
      out.skills[s] = objective(s);
    });
    const writing = (exam.sections.find((x) => x.skill === 'writing') || {}).items || [];
    const wMarks = writing.map((item, i) => this.writingScore(item, (texts || {})[i], level));
    const wRight = wMarks.reduce((n, m) => n + m.points, 0);
    const wTotal = wMarks.reduce((n, m) => n + m.total, 0);
    out.skills.writing = {right: wRight, total: wTotal,
                          share: wTotal ? wRight / wTotal : 0, assessed: true,
                          marks: wMarks};
    const sayItems = (exam.sections.find((x) => x.skill === 'speaking') || {}).items || [];
    const sp = this.speakingScore(sayItems, heard);
    out.skills.speaking = {right: 0, total: sayItems.length,
                           share: sp.share, assessed: sp.assessed, marks: sp.marks};
    const shares = this.SKILLS.map((s) => out.skills[s].share);
    out.overall = shares.reduce((n, x) => n + x, 0) / shares.length;
    this.SKILLS.forEach((s) => {
      const r = out.skills[s];
      r.passed = r.assessed && r.share >= this.FLOOR;
      if (!r.assessed) out.missing.push(s);
    });
    out.pass = out.overall >= this.PASS && out.missing.length === 0 &&
      this.SKILLS.every((s) => out.skills[s].passed);
    return out;
  },

  /* Which lessons to send someone back to, given the skills they missed. */
  recommend(course, prog, weak) {
    const wants = weak && weak.length ? weak : [];
    if (!wants.length) return [];
    const rows = this.lessons(course).filter((r) => wants.indexOf(r.lesson.skill) >= 0);
    /* Lessons not done yet first. When the weak skill's lessons are all done,
       the advice is still the right one - go back to them - so an empty list
       is only for a skill the course does not teach. */
    const open = rows.filter((r) => !this.done(prog, r.lesson.id));
    return (open.length ? open : rows).slice(0, 4).map((r) => r.lesson);
  },
};

/* The Learning Path page: seven level spaces, one written course, and the
   final examination that closes it. The markup it draws is generated from
   path.json, so the page has no A1 in it - adding A2 is adding a course. */
const Path = (() => {
  const PANEL = 'pathpanel';
  const KEY = 'fluentify.path.v1';
  const LEVEL_KEY = 'fluentify.level.v2.result';
  const SKILL = {
    grammar: ['Grammar', 'گرامر'], vocabulary: ['Vocabulary', 'واژگان'],
    reading: ['Reading', 'خواندن'], listening: ['Listening', 'شنیدن'],
    writing: ['Writing', 'نوشتن'], speaking: ['Speaking', 'گفتن'],
    review: ['Review', 'مرور'],
  };
  const STATE = {
    done: ['Passed', 'قبول‌شده'], current: ['Your level', 'سطح تو'],
    awaiting: ['Curriculum not written yet', 'برنامهٔ درسی هنوز نوشته نشده'],
    available: ['Open to revisit', 'برای مرور باز است'],
    past: ['Below your level', 'پایین‌تر از سطح تو'],
    locked: ['Opens later', 'بعداً باز می‌شود'],
  };

  let bank = null, loading = null, failed = '';
  let screen = 'levels', levelId = null, unitId = null, lessonId = null;
  let draft = null, examDraft = null, report = null, checked = false;

  const body = () => document.getElementById('pathbody');
  const esc = (s) => String(s == null ? '' : s)
    .replace(/[&<>"]/g, (c) => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
  const fa = (s) => '<span class="fa" dir="rtl" lang="fa">' + esc(s) + '</span>';
  const read = (k, d) => {
    try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; }
    catch (e) { return d; }
  };
  const save = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* private */ } };
  const pct = (x) => Math.round((x || 0) * 100) + '%';
  const bar = (share, extra) => '<span class="path-bar' + (extra ? ' ' + extra : '') +
    '" role="presentation"><i style="width:' + pct(share) + '"></i></span>';

  /* ------------------------------------------------------------ progress */

  function all() {
    const raw = read(KEY, null);
    const out = raw && typeof raw === 'object' ? raw : {};
    out.v = 1;
    out.levels = out.levels && typeof out.levels === 'object' ? out.levels : {};
    out.exams = Array.isArray(out.exams) ? out.exams : [];
    return out;
  }

  function prog(id) {
    const a = all();
    const p = a.levels[id] || (a.levels[id] = {lessons: {}, passed: false, at: 0});
    p.lessons = p.lessons && typeof p.lessons === 'object' ? p.lessons : {};
    return p;
  }

  function patch(id, fn) {
    const a = all();
    const p = a.levels[id] || (a.levels[id] = {lessons: {}, passed: false});
    fn(p, a);
    a.levels[id] = p;
    save(KEY, a);
  }

  function placement() { return read(LEVEL_KEY, null); }
  function start() { return PathModel.startLevel(placement()); }

  /* --------------------------------------------------------------- data */

  function load() {
    if (bank) return Promise.resolve(bank);
    if (loading) return loading;
    /* Through loadJSON, because that is the one call the offline build
       rewrites: on the web it is a request for /api/path, in the APK it is the
       same file out of data/. */
    loading = loadJSON('path').then((data) => {
      if (!data || !(data.levels || []).length) throw new Error('path.json is empty');
      bank = data;
      failed = '';
      return data;
    }).catch((e) => {
      failed = String((e && e.message) || e);
      loading = null;
      return null;
    });
    return loading;
  }

  const course = (id) => (bank && bank.courses ? bank.courses[id] : null) || null;
  const levelRow = (id) => ((bank && bank.levels) || []).find((l) => l.id === id) || null;

  /* A learner placed on a level whose course is not written yet (Pre-A1 today)
     has nothing to open there. The nearest written level above is offered, by
     name and with its own button - the assessed card is not replaced, and the
     learner is not moved without being told. */
  const nearestOffer = (here) => {
    const from = PathModel.ORDER.indexOf(here);
    if (!here || from < 0 || course(here)) return null;
    const above = ((bank && bank.levels) || [])
      .filter((l) => PathModel.ORDER.indexOf(l.id) > from && course(l.id));
    above.sort((a, b) => PathModel.ORDER.indexOf(a.id) - PathModel.ORDER.indexOf(b.id));
    return above.length ? above[0].id : null;
  };

  /* ------------------------------------------------------------- chrome */

  /* The tile exists only after the level check has been taken: a learning path
     with no placement would be a path from nowhere. */
  function sync() {
    const tile = document.getElementById('pathtoggle');
    if (!tile) return;
    const result = placement();
    tile.hidden = !(result && result.overall !== undefined);
    const badge = document.getElementById('pathbadge');
    if (badge && result) {
      badge.textContent = PathModel.startLevel(result);
      badge.hidden = false;
    }
  }

  function open() {
    load().then(() => {
      if (failed) return paintFailed();
      screen = 'levels';
      render();
    });
  }

  /* -------------------------------------------------------------- pages */

  function render() {
    const host = body();
    if (!host) return;
    if (failed) { paintFailed(); return; }
    if (screen === 'lesson') return paintLesson();
    if (screen === 'exam') return paintExam();
    if (screen === 'report') return paintReport();
    if (screen === 'level') return paintLevel();
    return paintLevels();
  }

  function paintFailed() {
    const host = body();
    if (host) {
      host.innerHTML = '<div class="path-wrap"><p class="path-empty">' +
        'The learning path could not be read: ' + esc(failed) + '</p></div>';
    }
  }

  function paintLevels() {
    const host = body();
    const here = start();
    const asked = placement();
    const under = (asked && asked.overall) || 'PRE';
    const offer = nearestOffer(here);
    const cards = ((bank && bank.levels) || []).map((lv) => {
      const c = course(lv.id);
      const p = prog(lv.id);
      const below = PathModel.ORDER[PathModel.ORDER.indexOf(lv.id) - 1];
      const state = PathModel.status(lv.id, here, !!c, !!p.passed,
        !!(below && prog(below).passed), offer);
      const st = PathModel.stats(c, p);
      /* A course below the learner is open to revisit; one above the learner
         was opened by passing the level below it, so it is next in the path
         rather than something being revisited. */
      const ahead = PathModel.ORDER.indexOf(lv.id) > PathModel.ORDER.indexOf(here);
      const stateText = state === 'available' && ahead
        ? ['Next in the path', 'قدم بعدی مسیر'] : STATE[state];
      const action = state === 'current' || state === 'available'
        ? '<button type="button" class="path-btn" data-path="level" data-id="' + lv.id + '">' +
          (state === 'current' ? 'Start learning'
            : ahead ? 'Start this level' : 'Open this level') + '</button>'
        : state === 'done'
          ? '<button type="button" class="path-btn ghost" data-path="level" data-id="' +
            lv.id + '">Review the course</button>'
          : '<button type="button" class="path-btn" disabled>' +
            (state === 'awaiting' ? 'Coming soon'
              : state === 'past' ? 'Not available' : 'Locked') + '</button>';
      const note = state === 'awaiting'
        ? (lv.id === here
          ? '<p class="plv-note">Your assessed level. Its curriculum has not been written yet — ' +
            'the courses below are the ones that exist today.</p>'
          : '<p class="plv-note">Next level: the one below is passed. Its curriculum is not ' +
            'written yet.</p>')
        : state === 'locked'
          ? '<p class="plv-note">Opens after the level below is passed.</p>'
          : state === 'past'
            ? '<p class="plv-note">Below the level this assessment placed you at.</p>'
            : state === 'available' && lv.id === offer
              ? '<p class="plv-note">The written course to start with; your own '
                + 'level\u2019s curriculum is still being written.</p>'
              : '';
      return '<article class="plv plv-' + state + '">' +
          '<div class="plv-top"><span class="plv-badge">' + esc(lv.label) + '</span>' +
            '<span class="plv-state">' + esc(stateText[0]) + ' ' + fa(stateText[1]) + '</span>' +
          '</div>' +
          '<h4 class="plv-name" dir="ltr">' + esc(lv.name.en) +
            '<span class="plv-fa">' + esc(lv.name.fa) + '</span></h4>' +
          '<p class="plv-can" dir="ltr">' + esc(lv.can.en) + '</p>' +
          '<p class="plv-can fa" dir="rtl" lang="fa">' + esc(lv.can.fa) + '</p>' +
          note +
          (c ? '<div class="plv-prog">' + bar(st.share) + '</div>' +
            '<p class="plv-foot" dir="ltr">' + (c.units || []).length + ' units · ' +
            st.total + ' lessons · six skills</p>' +
            '<p class="plv-foot" dir="ltr">' + st.done + ' done' +
            (p.passed ? ' · passed' : '') + '</p>' : '') +
          '<div class="plv-actions">' + action + '</div>' +
        '</article>';
    }).join('');

    /* Which courses actually exist today, so the page never advertises a level
       whose curriculum is not written. */
    const written = ((bank && bank.levels) || []).filter((lv) => course(lv.id)).map((lv) => lv.label);
    const named = written.length > 1
      ? written.slice(0, -1).join(', ') + ' and ' + written[written.length - 1]
      : String(written[0] || '');
    /* The same names, joined the way Persian joins a list. */
    const namedFa = written.length > 1
      ? written.slice(0, -1).join('، ') + ' و ' + written[written.length - 1]
      : String(written[0] || '');

    /* The band answers the one question the grid cannot: what should I open
       now? It names the level the learner is on - or, when that curriculum is
       not written, the written level offered instead - and gives the single
       next action. */
    const target = course(here) ? here : offer;
    const tRow = target ? levelRow(target) : null;
    const tC = target ? course(target) : null;
    const tP = target ? prog(target) : null;
    const tSt = PathModel.stats(tC, tP);
    const band = (tRow && tC)
      ? '<div class="path-band">' +
          '<div class="path-band-l">' +
            '<p class="path-band-k">Your level · ' +
              '<span class="fa" dir="rtl" lang="fa">سطح تو</span></p>' +
            '<p class="path-band-v" dir="ltr">' + esc(tRow.label) + ' · ' +
              esc(tRow.name.en) + '</p>' +
            '<p class="path-band-s" dir="ltr">' + tSt.done + ' of ' + tSt.total +
              ' lessons · ' + (tP.passed ? 'examination passed' : 'examination not yet passed') +
            '</p>' +
          '</div>' +
          '<div class="path-band-m">' + bar(tSt.share, 'big') +
            '<p class="path-band-p" dir="ltr">' + pct(tSt.share) + ' of the course complete</p>' +
          '</div>' +
          '<div class="path-band-r"><button type="button" class="path-btn" ' +
            'data-path="level" data-id="' + tRow.id + '">' +
            (tP.passed ? 'Review the course' : tSt.done ? 'Continue' : 'Start learning') +
          '</button></div>' +
        '</div>'
      : '';

    host.innerHTML = '<div class="path-wrap">' +
      '<div class="path-head">' +
        '<p class="path-kicker">Learning path · <bdi class="fa" dir="rtl" lang="fa">مسیر یادگیری</bdi></p>' +
        '<h2 class="path-h">Seven levels, one step at a time</h2>' +
        '<p class="path-sub" dir="ltr">Your level check placed you at <b>' + esc(under) +
          '</b>. The path runs from Pre-A1 to C2; the courses for ' + esc(named) +
          ' and their examinations are written and ready, and the other levels have their place here.</p>' +
        '<p class="path-sub fa" dir="rtl" lang="fa">سنجش سطح تو را در <b>' + esc(under) +
          '</b> قرار داد. مسیر از Pre-A1 تا C2 ادامه دارد؛ دوره‌های ' + esc(namedFa) +
          ' و آزمون‌هایشان آماده‌اند و بقیهٔ سطح‌ها جای خود را در همین صفحه دارند.</p>' +
      '</div>' +
      band +
      '<div class="plv-grid">' + cards + '</div>' +
      '<p class="path-foot" dir="ltr">Every level keeps the same shape: units, lessons ' +
        'and a final examination over the six skills. A level with no course yet is a ' +
        'place in the path, not a course.</p>' +
    '</div>';
  }

  function paintLevel() {
    const host = body();
    const lv = levelRow(levelId);
    const c = course(levelId);
    if (!lv || !c) { screen = 'levels'; return paintLevels(); }
    const p = prog(levelId);
    const st = PathModel.stats(c, p);
    const passed = !!p.passed;
    const last = (p.exams || []).slice(-1)[0];

    const skills = PathModel.SKILLS.map((s) => {
      const row = st.bySkill[s];
      const share = row.total ? row.done / row.total : 0;
      return '<div class="psk"><div class="psk-top"><span class="psk-name">' +
          esc(SKILL[s][0]) + ' · ' + esc(SKILL[s][1]) + '</span>' +
        '<span class="psk-num" dir="ltr">' + row.done + '/' + row.total + ' lessons</span></div>' +
        bar(share) + '</div>';
    }).join('');

    const units = (c.units || []).map((u, ui) => {
      const rows = (u.lessons || []).map((l, li) => {
        const done = PathModel.done(p, l.id);
        const rec = p.lessons[l.id];
        return '<li class="plesson' + (done ? ' done' : '') + '">' +
          '<span class="pdot" aria-hidden="true">' + (done ? '✓' : (ui * 3 + li + 1)) + '</span>' +
          '<button type="button" class="plesson-main" data-path="lesson" data-id="' + l.id + '">' +
            '<span class="plesson-title" dir="ltr">' + esc(l.title.en) + '</span>' +
            '<span class="plesson-fa">' + esc(l.title.fa) + '</span>' +
          '</button>' +
          '<span class="pskill pskill-' + l.skill + '">' + esc(SKILL[l.skill][0]) + '</span>' +
          '<span class="plesson-score" dir="ltr">' +
            (rec && rec.done ? Math.round((rec.right / Math.max(1, rec.total)) * 100) + '%' : '') +
          '</span>' +
        '</li>';
      }).join('');
      const unitDone = (u.lessons || []).filter((l) => PathModel.done(p, l.id)).length;
      const unitAll = (u.lessons || []).length;
      return '<section class="punit">' +
        '<header class="punit-head">' +
          '<span class="punit-badge" aria-hidden="true">' + (ui + 1) + '</span>' +
          '<div class="punit-head-t">' +
            '<span class="punit-n">Unit ' + (ui + 1) + '</span>' +
            '<h4 class="punit-title" dir="ltr">' + esc(u.title.en) +
            '<span class="punit-fa">' + esc(u.title.fa) + '</span></h4>' +
            '<p class="punit-goal" dir="ltr">' + esc(u.goal.en) + '</p>' +
            '<p class="punit-goal fa" dir="rtl" lang="fa">' + esc(u.goal.fa) + '</p>' +
          '</div>' +
          '<span class="punit-count" dir="ltr">' + unitDone + '/' + unitAll + ' done</span>' +
        '</header>' +
        '<ol class="plessons">' + rows + '</ol></section>';
    }).join('');

    const exam = c.exam || {};
    const left = st.total - st.done;
    const examCard = passed
      ? '<div class="pexam pexam-done">' +
          '<div><p class="pexam-k">Final examination</p>' +
          '<p class="pexam-t" dir="ltr">Passed' + (last ? ' at ' + pct(last.overall) : '') + '</p></div>' +
          '<button type="button" class="path-btn ghost" data-path="exam" data-id="' + levelId + '">Retake</button>' +
        '</div>'
      : left > 0
        ? '<div class="pexam">' +
            '<div><p class="pexam-k">Final examination</p>' +
            '<p class="pexam-t" dir="ltr">' + left + ' lesson' + (left === 1 ? '' : 's') +
              ' left before the examination opens</p></div>' +
            '<span class="pexam-lock" aria-hidden="true">🔒</span>' +
          '</div>'
        : '<div class="pexam pexam-ready">' +
            '<div><p class="pexam-k">Final examination</p>' +
            '<p class="pexam-t" dir="ltr">All lessons done. Six skills, one paper.</p></div>' +
            '<button type="button" class="path-btn" data-path="exam" data-id="' + levelId + '">Open the exam</button>' +
          '</div>';

    /* The one thing to do next: the first lesson not yet marked, and the
       examination once every lesson is. A dashboard that lists twenty-four
       lessons without saying which one to open is a table of contents, not a
       dashboard. */
    const rows = PathModel.lessons(c);
    const nextRow = rows.find((r) => !PathModel.done(p, r.lesson.id)) || null;
    const nextUnit = nextRow
      ? (c.units || []).indexOf(nextRow.unit) + 1 : 0;
    const nextCard = '<div class="pcard">' +
      '<p class="pcard-h">Recommended next · <span class="fa" dir="rtl" lang="fa">' +
        'قدم بعدی</span></p>' +
      (nextRow
        ? '<p class="pnext-u">Unit ' + nextUnit + ' · ' + esc(SKILL[nextRow.lesson.skill][0]) + '</p>' +
          '<p class="pnext-t" dir="ltr">' + esc(nextRow.lesson.title.en) + '</p>' +
          '<p class="pnext-s" dir="ltr">' + esc(nextRow.lesson.goal.en) + '</p>' +
          '<button type="button" class="path-btn" data-path="lesson" data-id="' +
            nextRow.lesson.id + '">Open the lesson</button>'
        : '<p class="pnext-t" dir="ltr">' +
            (passed ? 'Every lesson is done and the examination is passed.'
              : 'Every lesson is done. The paper is waiting.') + '</p>' +
          '<p class="pnext-s" dir="ltr">' +
            (passed ? 'You can retake it whenever you want a higher mark.'
              : 'The final examination covers all six skills at this level.') + '</p>' +
          '<button type="button" class="path-btn" data-path="exam" data-id="' + levelId + '">' +
            (passed ? 'Retake the exam' : 'Open the exam') + '</button>') +
      '</div>';

    host.innerHTML = '<div class="path-wrap">' +
      '<button type="button" class="path-back" data-path="home">← All levels</button>' +
      '<div class="path-head">' +
        '<p class="path-kicker">' + esc(lv.label) + ' · ' + esc(lv.name.en) + '</p>' +
        '<h2 class="path-h">' + esc(c.title.en) + ' <span class="path-h-fa">' + esc(c.title.fa) + '</span></h2>' +
        '<p class="path-sub" dir="ltr">' + esc(c.blurb.en) + '</p>' +
        '<p class="path-sub fa" dir="rtl" lang="fa">' + esc(c.blurb.fa) + '</p>' +
        '<div class="path-total"><div class="path-total-top"><span dir="ltr">Course progress</span>' +
          '<b dir="ltr">' + st.done + '/' + st.total + ' lessons · ' + pct(st.share) + '</b></div>' +
          bar(st.share, 'big') + '</div>' +
      '</div>' +
      '<div class="pldash">' +
        '<div class="pldash-main">' + units + '</div>' +
        '<aside class="pldash-side">' +
          '<div class="pcard"><p class="pcard-h">Six skills · ' +
            '<span class="fa" dir="rtl" lang="fa">شش مهارت</span></p>' + skills + '</div>' +
          examCard +
          nextCard +
        '</aside>' +
      '</div>' +
    '</div>';
  }

  /* -------------------------------------------------------------- lesson */

  function begin(lid) {
    lessonId = lid;
    checked = false;
    draft = {answers: {}, texts: {}, heard: {}, say: {}};
    screen = 'lesson';
    render();
  }

  function currentLesson() {
    if (!levelId) return null;
    return PathModel.lessons(course(levelId)).find((r) => r.lesson.id === lessonId) || null;
  }

  function paintLesson() {
    const host = body();
    const row = currentLesson();
    if (!row) { screen = 'level'; return paintLevel(); }
    const l = row.lesson;
    const c = course(levelId);
    const idx = PathModel.lessons(c).findIndex((r) => r.lesson.id === lessonId);
    const rec = prog(levelId).lessons[lessonId];

    const explain = (l.explain || []).map((p) =>
      '<p class="plx-en" dir="ltr">' + esc(p.en) + '</p>' +
      '<p class="plx-fa fa" dir="rtl" lang="fa">' + esc(p.fa) + '</p>').join('');

    const examples = (l.examples || []).map((e, i) =>
      '<li class="plex"><span class="plex-en" dir="ltr">' + esc(e.en) + '</span>' +
      '<span class="plex-fa">' + esc(e.fa) + '</span>' +
      '<button type="button" class="path-play" data-path="play" data-id="' + i +
        '" aria-label="Play this example">🔊</button></li>').join('');

    const passage = l.passage
      ? '<div class="ppass"><p class="ppass-t" dir="ltr">' + esc(l.passage.title.en) +
        '</p><p class="ppass-en" dir="ltr">' + esc(l.passage.text.en) + '</p>' +
        '<p class="ppass-fa fa" dir="rtl" lang="fa">' + esc(l.passage.text.fa) + '</p></div>'
      : '';

    const dialogue = l.dialogue
      ? '<div class="pdia"><p class="pdia-k" dir="ltr">Role-play · نقش‌بازی</p>' +
        l.dialogue.map((d) => '<div class="pdia-row"><span class="pdia-who">' + esc(d.who) +
          '</span><span class="pdia-en" dir="ltr">' + esc(d.en) + '</span>' +
          '<button type="button" class="path-play" data-path="dialogue" data-id="' +
          esc(d.en) + '" aria-label="Play this line">🔊</button>' +
          '<span class="pdia-fa">' + esc(d.fa) + '</span></div>').join('') + '</div>'
      : '';

    const guided = (l.guided || []).map((q, i) =>
      '<div class="pguide" data-guide="' + i + '"><p class="pq" dir="ltr">' +
      esc(q.prompt.en) + '</p><p class="pq-fa fa" dir="rtl" lang="fa">' + esc(q.prompt.fa) +
      '</p><div class="pops">' + q.options.map((o, k) =>
        '<button type="button" class="popt" data-guide-opt="' + i + '" data-k="' + k + '">' +
        '<span class="popt-k">' + 'ABCD'[k] + '</span>' + esc(o) + '</button>').join('') +
      '</div><p class="pwhy" hidden dir="ltr">' + esc(q.why.en) + ' <span class="fa" dir="rtl" ' +
      'lang="fa">' + esc(q.why.fa) + '</span></p></div>').join('');

    const exercises = (l.exercises || []).map((e, i) => exerciseHtml(e, i)).join('');

    const done = rec && rec.done;
    const flat = PathModel.lessons(c);
    const after = flat[idx + 1] || null;
    const unitNo = (c.units || []).indexOf(row.unit) + 1;
    const rail = '<aside class="plesson-rail">' +
      '<div class="pcard">' +
        '<p class="pcard-h">This lesson · <span class="fa" dir="rtl" lang="fa">این درس</span></p>' +
        '<p class="pnext-u">Unit ' + unitNo + ' · ' + esc(SKILL[l.skill][0]) + '</p>' +
        '<p class="pnext-t" dir="ltr">' + (idx + 1) + ' of ' + flat.length + ' in this level</p>' +
        '<p class="pnext-s" dir="ltr">' + (l.exercises || []).length + ' exercises · ' +
          (done ? 'marked done' : 'not yet done') + '</p>' +
      '</div>' +
      (after
        ? '<div class="pcard">' +
            '<p class="pcard-h">Next lesson · <span class="fa" dir="rtl" lang="fa">درس بعد</span></p>' +
            '<p class="pnext-t" dir="ltr">' + esc(after.lesson.title.en) + '</p>' +
            '<p class="pnext-s" dir="ltr">' + esc(SKILL[after.lesson.skill][0]) + ' · ' +
              esc(after.unit.title.en) + '</p>' +
            '<button type="button" class="path-btn ghost" data-path="lesson" data-id="' +
              after.lesson.id + '">Go to it</button>' +
          '</div>'
        : '<div class="pcard">' +
            '<p class="pcard-h">After this · <span class="fa" dir="rtl" lang="fa">بعد از این</span></p>' +
            '<p class="pnext-t" dir="ltr">The final examination</p>' +
            '<p class="pnext-s" dir="ltr">Six skills, thirty-three marks, one pass rule.</p>' +
            '<button type="button" class="path-btn ghost" data-path="exam" data-id="' +
              levelId + '">See the paper</button>' +
          '</div>') +
    '</aside>';

    host.innerHTML = '<div class="path-wrap pwide">' +
      '<button type="button" class="path-back" data-path="level" data-id="' + levelId +
        '">← ' + esc((levelRow(levelId) || {label: levelId}).label) + ' course</button>' +
      '<div class="path-head">' +
        '<p class="path-kicker">Lesson ' + (idx + 1) + ' of ' + flat.length +
          ' · ' + esc(SKILL[l.skill][0]) + '</p>' +
        '<h2 class="path-h" dir="ltr">' + esc(l.title.en) + '</h2>' +
        '<p class="path-h-fa">' + esc(l.title.fa) + '</p>' +
        '<p class="path-sub" dir="ltr"><b>Goal:</b> ' + esc(l.goal.en) + '</p>' +
        '<p class="path-sub fa" dir="rtl" lang="fa">' + esc(l.goal.fa) + '</p>' +
      '</div>' +
      '<div class="plesson-cols">' +
        '<div class="plesson-main">' +
          passage +
          '<section class="pblock"><h3 class="pblock-h" dir="ltr">Explanation</h3>' + explain + '</section>' +
          '<section class="pblock"><h3 class="pblock-h" dir="ltr">Examples</h3>' +
            '<ul class="plexs">' + examples + '</ul></section>' +
          dialogue +
          '<section class="pblock"><h3 class="pblock-h" dir="ltr">Guided practice</h3>' + guided + '</section>' +
          '<section class="pblock"><h3 class="pblock-h" dir="ltr">Exercises</h3>' +
            '<p class="pblock-sub" dir="ltr">Answer all of them, then check. 60% or more and ' +
            'the lesson is done.</p>' + exercises + '</section>' +
          '<div class="pfoot" id="pfoot">' +
            (done ? '<p class="pok-line">Done · ' + Math.round((rec.right / Math.max(1, rec.total)) * 100) +
              '% on the exercises</p>' : '') +
            '<button type="button" class="path-btn" data-path="check">Check my answers</button>' +
            (done ? '' : '<button type="button" class="path-btn ghost" data-path="finish" hidden>' +
              'Finish the lesson</button><button type="button" class="path-btn ghost" data-path="retry" ' +
              'hidden>Try again</button>') +
          '</div>' +
          '<div class="presult" id="presult" hidden></div>' +
        '</div>' +
        rail +
      '</div>' +
    '</div>';
    if (checked) checkLesson(false);
  }

  function exerciseHtml(e, i) {
    const head = '<div class="pex" data-ex="' + i + '"><div class="pex-top">' +
      '<span class="pex-n">' + (i + 1) + '</span>' +
      '<span class="pex-kind">' + esc({mcq: 'Choose', gap: 'Fill the gap', listen: 'Listen',
        write: 'Write', say: 'Say it'}[e.kind] || 'Exercise') + '</span></div>';
    if (e.kind === 'mcq') {
      return head + '<p class="pq" dir="ltr">' + esc(e.prompt.en) + '</p>' +
        '<p class="pq-fa fa" dir="rtl" lang="fa">' + esc(e.prompt.fa) + '</p><div class="pops">' +
        e.options.map((o, k) => '<button type="button" class="popt" data-ex-opt="' + i +
          '" data-k="' + k + '"><span class="popt-k">' + 'ABCD'[k] + '</span>' + esc(o) +
          '</button>').join('') + '</div><p class="pwhy" hidden dir="ltr">' + esc(e.why.en) +
        ' <span class="fa" dir="rtl" lang="fa">' + esc(e.why.fa) + '</span></p></div>';
    }
    if (e.kind === 'listen') {
      return head + '<button type="button" class="path-play big" data-path="playsay" data-id="' +
        i + '">🔊 Play</button><p class="pq" dir="ltr">' + esc(e.prompt.en) + '</p>' +
        '<p class="pq-fa fa" dir="rtl" lang="fa">' + esc(e.prompt.fa) + '</p><div class="pops">' +
        e.options.map((o, k) => '<button type="button" class="popt" data-ex-opt="' + i +
          '" data-k="' + k + '"><span class="popt-k">' + 'ABCD'[k] + '</span>' + esc(o) +
          '</button>').join('') + '</div><p class="pwhy" hidden dir="ltr">' + esc(e.why.en) +
        ' <span class="fa" dir="rtl" lang="fa">' + esc(e.why.fa) + '</span></p></div>';
    }
    if (e.kind === 'gap') {
      const parts = String(e.text).split('___');
      return head + '<p class="pq gapq" dir="ltr">' +
        esc(parts[0]) + '<input type="text" class="pgap" data-ex-gap="' + i +
        '" autocomplete="off" spellcheck="false" aria-label="Missing word">' +
        esc(parts.slice(1).join('___')) + '</p>' +
        (e.hint ? '<p class="phint" dir="ltr">' + esc(e.hint) + '</p>' : '') +
        '<p class="pwhy" hidden dir="ltr">' + esc(e.why.en) + ' <span class="fa" dir="rtl" ' +
        'lang="fa">' + esc(e.why.fa) + '</span></p></div>';
    }
    if (e.kind === 'write') {
      return head + '<p class="pq" dir="ltr">' + esc(e.task.en) + '</p>' +
        '<p class="pq-fa fa" dir="rtl" lang="fa">' + esc(e.task.fa) + '</p>' +
        '<p class="phint" dir="ltr">' + esc(e.tips.en) + ' · at least ' + e.words + ' words' +
        '</p><textarea class="pwrite" data-ex-write="' + i + '" rows="5" dir="ltr" ' +
        'aria-label="Your answer"></textarea>' +
        '<p class="pcount" data-count="' + i + '">0 words</p>' +
        '<p class="pwhy" hidden dir="ltr"></p></div>';
    }
    /* say */
    return head + '<p class="pq" dir="ltr">Say this aloud:</p>' +
      '<p class="psay" dir="ltr">' + esc(e.say) + '</p>' +
      '<p class="psay-fa fa" dir="rtl" lang="fa">' + esc(e.fa) + '</p>' +
      '<div class="prow"><button type="button" class="path-btn ghost" data-path="playsay" ' +
      'data-id="' + i + '">🔊 Hear it</button>' +
      '<button type="button" class="path-btn" data-path="say" data-id="' + i + '">🎤 Say it</button></div>' +
      '<p class="pheard" data-heard="' + i + '" dir="ltr"></p><p class="pwhy" hidden></p></div>';
  }

  /* ----------------------------------------------------------- checking */

  function exValue(i) {
    const e = currentLesson().lesson.exercises[i];
    if (e.kind === 'write') return draft.texts[i] || '';
    if (e.kind === 'say') return draft.heard[i] || '';
    return draft.answers[i];
  }

  function exScore(e, i) {
    if (e.kind === 'write') {
      const m = PathModel.writingScore(e, draft.texts[i] || '', levelId);
      return m.total ? m.points / m.total : 0;
    }
    if (e.kind === 'say') {
      const c = SayMatch.compare(e.say, draft.heard[i] || '');
      return c.empty ? 0 : c.percent / 100;
    }
    return PathModel.answerRight(e, draft.answers[i]) ? 1 : 0;
  }

  function checkLesson(record) {
    const row = currentLesson();
    if (!row) return;
    const ex = row.lesson.exercises || [];
    /* A speaking exercise on a device with no recogniser is not a failed
       exercise - there is no way to hear the answer. It comes out of the
       denominator rather than out of the score, and the paper says so. The
       exam still requires the skill: this is only a lesson. */
    const canSay = typeof STT !== 'undefined' && STT.supported();
    const counted = ex.filter((e) => !(e.kind === 'say' && !canSay));
    let sum = 0, answered = 0;
    ex.forEach((e, i) => {
      const sc = exScore(e, i);
      if (counted.indexOf(e) >= 0) sum += sc;
      if (e.kind === 'write' || e.kind === 'say' ? !!(draft.texts[i] || draft.heard[i]) : draft.answers[i] != null) answered += 1;
      const node = document.querySelector('[data-ex="' + i + '"]');
      if (!node) return;
      node.classList.toggle('ok', sc >= 0.6);
      node.classList.toggle('bad', sc < 0.6);
      const why = node.querySelector('.pwhy');
      if (why) {
        why.hidden = false;
        if (e.kind === 'write') {
          const m = PathModel.writingScore(e, draft.texts[i] || '', levelId);
          why.innerHTML = m.parts.map((p) => (p.ok ? '✓ ' : '✗ ') + esc(p.note)).join(' · ');
        } else if (e.kind === 'say') {
          const c = SayMatch.compare(e.say, draft.heard[i] || '');
          why.textContent = c.empty ? 'Nothing was heard — try again or move on.'
            : c.right + ' of ' + c.total + ' words heard' +
              (c.missing.length ? ' · missing: ' + c.missing.join(', ') : '');
        }
      }
      const gaps = node.querySelector('.pgap');
      if (gaps && e.kind === 'gap') gaps.disabled = true;
      if (e.kind === 'mcq' || e.kind === 'listen') {
        [...node.querySelectorAll('[data-ex-opt]')].forEach((b) => {
          b.disabled = true;
          const k = Number(b.dataset.k);
          if (k === Number(e.answer)) b.classList.add('right');
          else if (Number(draft.answers[i]) === k) b.classList.add('wrong');
        });
      }
    });
    const total = counted.length || 1;
    const share = sum / total;
    const out = document.getElementById('presult');
    if (out) {
      out.hidden = false;
      out.innerHTML = '<p class="pres-h" dir="ltr">' + Math.round(share * 100) + '% · ' +
        answered + ' of ' + counted.length + ' answered</p>' +
        (counted.length < ex.length
          ? '<p class="pres-s" dir="ltr">The speaking exercise is not counted on this ' +
            'device: there is no speech recogniser to hear it.</p>' : '') +
        '<p class="pres-s" dir="ltr">' + (share >= 0.6
          ? 'That is enough to finish the lesson. The ones marked in red come back in the review queue.'
          : 'Not yet: 60% finishes a lesson. Read the explanation again and try the red ones.') + '</p>';
    }
    const fin = document.querySelector('[data-path="finish"]');
    if (fin) fin.hidden = share < 0.6;
    const again = document.querySelector('[data-path="retry"]');
    if (again) again.hidden = false;
    checked = true;

    if (record && share >= 0.6) {
      const right = ex.reduce((n, e, i) =>
        n + (counted.indexOf(e) >= 0 && exScore(e, i) >= 0.6 ? 1 : 0), 0);
      patch(levelId, (p) => {
        p.lessons[lessonId] = {done: true, at: new Date().toISOString(),
                               right: right, total: counted.length};
      });
      screen = 'level';
      render();
      toast('Lesson complete · درس کامل شد', 2600);
    }
  }

  /* ----------------------------------------------------------- exam page */

  function startExam() {
    examDraft = {answers: {}, texts: {}, heard: {}};
    report = null;
    screen = 'exam';
    render();
  }

  function paintExam() {
    const host = body();
    const c = course(levelId) || {};
    const lv = levelRow(levelId) || {};
    const label = lv.label || levelId || '';
    const exam = c.exam || {};
    const paper = PathModel.paper(exam);
    const objective = paper.filter((q) => q.kind !== 'write' && q.kind !== 'say');
    const count = (skill) => (((exam.sections || []).find((s) => s.skill === skill) || {}).items || []).length;
    const tasks = count('writing') + ' writing ' + (count('writing') === 1 ? 'task · ' : 'tasks · ');
    const sections = (exam.sections || []).map((section) => {
      if (section.skill === 'reading') {
        return section.items.map((g, gi) =>
          '<div class="pexam-pass"><p class="ppass-t" dir="ltr">' + esc(g.passage.en) + '</p>' +
          '<p class="ppass-en" dir="ltr">' + esc(g.text.en) + '</p>' +
          '<p class="ppass-fa fa" dir="rtl" lang="fa">' + esc(g.text.fa) + '</p>' +
          (g.questions || []).map((q, k) => examQuestion(q, 'reading.' + gi + '.' + k, 'r' + gi + k)).join('') +
          '</div>').join('');
      }
      return (section.items || []).map((item, i) =>
        examQuestion(item, section.skill + '.' + i, section.skill + i, section.skill)).join('');
    }).join('');

    host.innerHTML = '<div class="path-wrap pwide">' +
      '<button type="button" class="path-back" data-path="level" data-id="' + levelId +
        '">← Back to the course</button>' +
      '<div class="path-head">' +
        '<p class="path-kicker">' + esc(label) + ' final examination · آزمون پایانی ' +
          esc(label) + '</p>' +
        '<h2 class="path-h">Six skills, one paper</h2>' +
        '<p class="path-sub" dir="ltr">' + esc(exam.blurb.en) + '</p>' +
        '<p class="path-sub fa" dir="rtl" lang="fa">' + esc(exam.blurb.fa) + '</p>' +
        '<p class="path-meta" dir="ltr">' + objective.length + ' marked questions · ' + tasks +
          count('speaking') + ' speaking ' + (count('speaking') === 1 ? 'task' : 'tasks') +
          ' · about ' + (exam.minutes || 35) + ' minutes</p>' +
      '</div>' +
      '<div class="pexam-paper">' + sections + '</div>' +
      '<div class="pfoot"><button type="button" class="path-btn" data-path="exam-submit">' +
        'Submit the paper</button></div>' +
    '</div>';
  }

  function examQuestion(item, id, key, skill) {
    const label = skill === 'listening'
      ? '<button type="button" class="path-play" data-path="playsay" data-id="' + id +
        '">🔊 Play</button>' : '';
    const kind = item.kind;
    if (kind === 'write') {
      return '<div class="pex" data-exam="' + id + '"><div class="pex-top"><span class="pex-n">' +
        '✎</span><span class="pex-kind">Write</span></div><p class="pq" dir="ltr">' +
        esc(item.task.en) + '</p><p class="pq-fa fa" dir="rtl" lang="fa">' + esc(item.task.fa) +
        '</p><p class="phint" dir="ltr">' + esc(item.tips.en) + ' · at least ' + item.words +
        ' words</p><textarea class="pwrite" data-exam-write="' + id + '" rows="5" dir="ltr" ' +
        'aria-label="Your answer"></textarea><p class="pcount" data-count="' + id + '">0 words</p></div>';
    }
    if (kind === 'say') {
      return '<div class="pex" data-exam="' + id + '"><div class="pex-top"><span class="pex-n">' +
        '🎤</span><span class="pex-kind">Speak</span></div><p class="pq" dir="ltr">' +
        esc(item.say) + '</p><p class="pq-fa fa" dir="rtl" lang="fa">' + esc(item.fa) + '</p>' +
        '<div class="prow"><button type="button" class="path-btn ghost" data-path="playsay" ' +
        'data-id="say:' + id + '">🔊 Hear it</button>' +
        '<button type="button" class="path-btn" data-path="exam-say" data-id="' + id +
        '">🎤 Say it</button></div><p class="pheard" data-exam-heard="' + id + '" dir="ltr"></p></div>';
    }
    const prompt = kind === 'listen' ? item.prompt : item.prompt;
    return '<div class="pex" data-exam="' + id + '"><div class="pex-top"><span class="pex-n">' +
      '?</span><span class="pex-kind">' + esc(SKILL[skill] ? SKILL[skill][0] : 'Question') +
      '</span></div>' + label + '<p class="pq" dir="ltr">' + esc(prompt.en) + '</p>' +
      '<p class="pq-fa fa" dir="rtl" lang="fa">' + esc(prompt.fa) + '</p><div class="pops">' +
      item.options.map((o, k) => '<button type="button" class="popt" data-exam-opt="' + id +
        '" data-k="' + k + '"><span class="popt-k">' + 'ABCD'[k] + '</span>' + esc(o) +
        '</button>').join('') + '</div></div>';
  }

  function submitExam() {
    const c = course(levelId) || {};
    const exam = c.exam || {};
    const result = PathModel.grade(exam, examDraft.answers, examDraft.texts,
      examDraft.heard, levelId);
    const weak = PathModel.SKILLS.filter((s) => !result.skills[s].passed);
    const advice = PathModel.recommend(c, prog(levelId), weak);
    const record = {
      at: new Date().toISOString(), overall: result.overall, pass: result.pass,
      missing: result.missing,
      skills: Object.fromEntries(PathModel.SKILLS.map((s) => [s, {
        share: result.skills[s].share, assessed: result.skills[s].assessed,
        right: result.skills[s].right, total: result.skills[s].total,
      }])),
      advice: advice.map((l) => l.id),
    };
    patch(levelId, (p) => {
      p.exams = (p.exams || []).concat([record]).slice(-8);
      if (result.pass) { p.passed = true; p.passedAt = record.at; }
    });
    report = {result: result, advice: advice, record: record};
    screen = 'report';
    render();
  }

  function paintReport() {
    const host = body();
    if (!report) { screen = 'level'; return paintLevel(); }
    const r = report.result;
    const passed = r.pass;
    const lv = levelRow(levelId) || {};
    const label = lv.label || levelId || '';
    /* What passing this paper opens next, named from the path itself. */
    const up = PathModel.ORDER[PathModel.ORDER.indexOf(levelId) + 1];
    const upLv = up ? levelRow(up) : null;
    const above = upLv && upLv.label ? upLv.label : up;
    const next = !up
      ? 'That is the end of the path.'
      : upLv && course(up)
        ? label + ' is complete; ' + above + ' is the next level.'
        : label + ' is complete. The next level, ' + above + ', has no course yet.';
    const rows = PathModel.SKILLS.map((s) => {
      const row = r.skills[s];
      const share = row.share;
      const state = !row.assessed ? 'not assessed' : (share >= 0.5 ? 'ok' : 'weak');
      return '<div class="prep-row prep-' + state + '"><span class="prep-name">' +
        esc(SKILL[s][0]) + ' · ' + esc(SKILL[s][1]) + '</span>' +
        bar(share) +
        '<span class="prep-num" dir="ltr">' + (row.assessed ? pct(share) : '—') + '</span></div>';
    }).join('');
    const advice = report.advice.length
      ? '<div class="pblock"><h3 class="pblock-h" dir="ltr">Lessons to go back to</h3><ul class="plexs">' +
        report.advice.map((l) => '<li class="prec"><button type="button" class="path-link" ' +
          'data-path="lesson" data-id="' + l.id + '">' + esc(l.title.en) + '</button>' +
          '<span class="prec-fa">' + esc(l.title.fa) + '</span></li>').join('') + '</ul></div>'
      : '';
    const missing = r.missing.length
      ? '<p class="pnote" dir="ltr">Not assessed: ' + r.missing.map((s) => esc(SKILL[s][0])).join(', ') +
        '. Speaking needs the device\'s speech recogniser — without it the paper cannot claim ' +
        'the skill, and it is not reported as passed.</p>'
      : '';
    host.innerHTML = '<div class="path-wrap pwide">' +
      '<button type="button" class="path-back" data-path="level" data-id="' + levelId +
        '">← Back to the course</button>' +
      '<div class="prep ' + (passed ? 'prep-pass' : 'prep-fail') + '">' +
        '<p class="prep-k">' + esc(label) + ' final examination</p>' +
        '<p class="prep-score" dir="ltr">' + pct(r.overall) + '</p>' +
        '<p class="prep-verdict">' + (passed ? 'Passed · قبول شدی' : 'Not passed yet · هنوز قبول نشدی') + '</p>' +
        '<p class="prep-line" dir="ltr">' + (passed
          ? 'Every skill is at or above 50% and the paper is above 60%. ' + next
          : 'A pass needs 60% overall, 50% in every skill, and every skill assessed.') + '</p>' +
      '</div>' + missing +
      '<div class="preps">' + rows + '</div>' + advice +
      '<div class="pfoot">' +
        '<button type="button" class="path-btn ghost" data-path="exam-retake">Retake the exam</button>' +
        '<button type="button" class="path-btn" data-path="level" data-id="' + levelId +
          '">Back to the course</button>' +
      '</div>' +
    '</div>';
  }

  /* -------------------------------------------------------------- events */

  function bind() {
    const host = body();
    if (!host || host._bound) return;
    host._bound = true;

    host.addEventListener('click', (ev) => {
      const g = ev.target.closest('[data-guide-opt]');
      if (g) return guide(g);
      const o = ev.target.closest('[data-ex-opt]');
      if (o) return pickExercise(o);
      const eo = ev.target.closest('[data-exam-opt]');
      if (eo) return pickExamOption(eo);
      const act = ev.target.closest('[data-path]');
      if (!act) return;
      const id = act.dataset.id;
      switch (act.dataset.path) {
        case 'home': screen = 'levels'; return render();
        case 'level': levelId = act.dataset.id || levelId; screen = 'level'; return render();
        case 'lesson': screen = 'lesson'; begin(act.dataset.id); return;
        case 'check': return checkLesson(false);
        case 'finish': return checkLesson(true);
        // checking locks the answers, so a lesson under 60% needs a way back
        // into its own exercises that is not reopening it from the course
        case 'retry': return begin(lessonId);
        case 'exam': levelId = act.dataset.id || levelId; startExam(); return;
        case 'exam-retake': startExam(); return;
        case 'exam-submit': return submitExam();
        case 'play': return playExample(id);
        case 'dialogue': return Speech.speak(String(id));
        case 'playsay': return playSay(id);
        case 'say': return captureSay(id, false);
        case 'exam-say': return captureSay(id, true);
        default: return;
      }
    });

    host.addEventListener('input', (ev) => {
      const gapIn = ev.target.closest('[data-ex-gap]');
      if (gapIn) { draft.answers[Number(gapIn.dataset.exGap)] = gapIn.value; return; }
      const wr = ev.target.closest('[data-ex-write]');
      if (wr) {
        const i = Number(wr.dataset.exWrite);
        draft.texts[i] = wr.value;
        const c = host.querySelector('[data-count="' + i + '"]');
        if (c) c.textContent = countWords(wr.value) + ' words';
        return;
      }
      const ew = ev.target.closest('[data-exam-write]');
      if (ew) {
        const id2 = ew.dataset.examWrite;
        examDraft.texts[Number(String(id2).split('.').pop())] = ew.value;
        const c2 = host.querySelector('[data-count="' + id2 + '"]');
        if (c2) c2.textContent = countWords(ew.value) + ' words';
      }
    });
  }

  function countWords(s) {
    return (String(s || '').match(/[A-Za-z][A-Za-z'’-]*/g) || []).length;
  }

  function guide(btn) {
    const i = Number(btn.dataset.guideOpt);
    const block = btn.closest('[data-guide]');
    const row = currentLesson();
    const q = row && row.lesson.guided[i];
    if (!q || !block) return;
    [...block.querySelectorAll('[data-guide-opt]')].forEach((b) => {
      b.disabled = true;
      const k = Number(b.dataset.k);
      if (k === Number(q.answer)) b.classList.add('right');
      else if (b === btn) b.classList.add('wrong');
    });
    const why = block.querySelector('.pwhy');
    if (why) why.hidden = false;
  }

  function pickExercise(btn) {
    const i = Number(btn.dataset.exOpt);
    draft.answers[i] = Number(btn.dataset.k);
    [...document.querySelectorAll('[data-ex-opt="' + i + '"]')].forEach((b) => {
      b.classList.toggle('on', b === btn);
    });
  }

  function pickExamOption(btn) {
    const id = btn.dataset.examOpt;
    examDraft.answers[id] = Number(btn.dataset.k);
    document.querySelectorAll('[data-exam-opt="' + id + '"]').forEach((b) => {
      b.classList.toggle('on', b === btn);
    });
  }

  function playExample(i) {
    const row = currentLesson();
    const ex = row && row.lesson.examples && row.lesson.examples[Number(i)];
    if (ex && typeof Speech !== 'undefined') Speech.speak(ex.en);
  }

  function examItem(id) {
    const c = course(levelId) || {};
    const row = PathModel.paper(c.exam || {}).find((q) => q.id === String(id));
    return row ? (row.skill === 'reading' ? row.passage : row.item) : null;
  }

  function playSay(id) {
    if (typeof Speech === 'undefined') return;
    const want = String(id).indexOf('say:') === 0 ? String(id).slice(4) : String(id);
    if (screen === 'exam') {
      const item = examItem(want);
      if (item && item.say) Speech.speak(item.say);
      return;
    }
    const row = currentLesson();
    const e = row && row.lesson.exercises[Number(want)];
    if (e && e.say) Speech.speak(e.say);
  }

  function captureSay(id, isExam) {
    if (typeof STT === 'undefined' || !STT.supported()) {
      toast('This device has no speech recognition — the paper cannot assess speaking here. ' +
        'Try Chrome or the Android app. / این دستگاه تشخیص گفتار ندارد.', 4800);
      return;
    }
    STT.sink = (text) => {
      STT.sink = null;
      if (isExam) {
        examDraft.heard[Number(String(id).split('.').pop())] = text || '';
        const out = document.querySelector('[data-exam-heard="' + id + '"]');
        const item = examItem(id);
        if (out && item) {
          const cmp = SayMatch.compare(item.say, text || '');
          out.textContent = cmp.empty ? 'Nothing was heard. Try again.'
            : cmp.right + ' of ' + cmp.total + ' words heard';
        }
      } else {
        const i = Number(id);
        draft.heard[i] = text || '';
        const row = currentLesson();
        const item = row && row.lesson.exercises[i];
        const out = document.querySelector('[data-heard="' + i + '"]');
        if (out && item && item.say) {
          const cmp = SayMatch.compare(item.say, text || '');
          out.textContent = cmp.empty ? 'Nothing was heard. Try again.'
            : cmp.right + ' of ' + cmp.total + ' words heard' +
              (cmp.missing.length ? ' · missing: ' + cmp.missing.join(', ') : '');
        }
      }
    };
    if (!STT.begin()) {
      STT.sink = null;
      toast('The microphone did not start. / میکروفون شروع نشد.', 3200);
    }
  }

  /* --------------------------------------------------------------- boot */

  function init() {
    bind();
    sync();
  }

  return {init, open, sync, render, PANEL: PANEL, begin: begin};
})();


const Daily = (() => {
  /* Line icons in the toolbar's own family, drawn in currentColor. The three
     emoji these replace rendered differently on every platform and read as
     decoration beside the theme's drawn set. */
  const svgIcon = (paths) => '<svg viewBox="0 0 24 24" fill="none" ' +
    'stroke="currentColor" stroke-width="1.7" stroke-linecap="round" ' +
    'stroke-linejoin="round" aria-hidden="true">' + paths + '</svg>';
  const CARD_ICON = {
    today: svgIcon('<rect x="3.4" y="4.8" width="17.2" height="16" rx="2.4"/>' +
      '<path d="M3.4 9.6h17.2M8.2 3.2v3.2M15.8 3.2v3.2"/>'),
    words: svgIcon('<path d="M12 7.6C10.5 6.4 8.5 5.8 6 5.8H4.2v12.4H6c2.5 0 4.5.6 6 1.8"/>' +
      '<path d="M12 7.6c1.5-1.2 3.5-1.8 6-1.8h1.8v12.4H18c-2.5 0-4.5.6-6 1.8"/>' +
      '<path d="M12 7.6v12.4"/>'),
    /* Solid blocks, not strokes: two outline quotes at 13px read as the
       numerals "55" in the chip. */
    expressions: svgIcon('<path fill="currentColor" stroke="none" d="M6.4 9.6h4.4v3.9c0 2.4-1.6 4.3-4.4 5.1l-.7-1.6c1.5-.5 2.4-1.4 2.6-2.6H6.4z"/>' +
      '<path fill="currentColor" stroke="none" d="M14.8 9.6h4.4v3.9c0 2.4-1.6 4.3-4.4 5.1l-.7-1.6c1.5-.5 2.4-1.4 2.6-2.6h-1.9z"/>'),
    conversations: svgIcon('<path d="M20.4 12.4c0 3.5-3.5 6.3-7.8 6.3-1 0-2-.1-2.9-.4l-4.1 1.5 1.2-3.4a5.8 5.8 0 0 1-1.9-4c0-3.5 3.5-6.3 7.7-6.3s7.8 2.8 7.8 6.3z"/>'),
  };
  const KIND_EN = {words: 'Word of the Day', expressions: 'Expression of the Day',
                   conversations: 'Conversation of the Day'};
  const KIND_FA = {words: 'لغت امروز', expressions: 'عبارت امروز',
                   conversations: 'مکالمه امروز'};
  const ORDER = ['words', 'expressions', 'conversations'];

  let cat = null;          // the catalogue, read once
  let failed = false;
  let shown = null;        // the date currently painted
  let picked = null;       // the three items currently painted
  let timer = 0;

  const els = () => ({
    cards: document.getElementById('dcards'),
    date: document.getElementById('ddate'),
    count: document.getElementById('dcount'),
    fill: document.getElementById('dfill'),
    track: document.getElementById('dtrack'),
    badge: document.getElementById('dbadge'),
  });

  const esc = (s) => escapeHtml(String(s == null ? '' : s));

  function faLine(text, cls) {
    return '<div class="' + (cls || 'dfa') + '">' + esc(text) + '</div>';
  }

  function examples(entry) {
    const rows = (entry.examples || []).map((ex, i) =>
      '<div class="exrow"><span class="n">' + (i + 1) + '</span>' +
      '<div class="grow"><div class="dline">' + esc(ex.en) + '</div>' +
      faLine(ex.fa, 'dline fa') + '</div></div>').join('');
    return rows ? '<div class="dlabel">Examples — <bdi class="fa" lang="fa" dir="rtl">مثال‌ها</bdi></div><div class="dex">' +
      rows + '</div>' : '';
  }

  function cardShell(kind, level, extraHead, body) {
    return '<div class="dtop"><span class="dico">' + CARD_ICON[kind] + '</span>' +
      '<span class="dkind">' + KIND_EN[kind] +
      '<small dir="rtl" lang="fa">' + KIND_FA[kind] +
      '</small></span><span class="spacer"></span>' + (extraHead || '') +
      (level ? '<span class="dlvl">' + esc(level) + '</span>' : '') +
      '</div>' + body;
  }

  function wordBody(entry) {
    let html = '';
    const def = entry.def || {};
    if (def.en || def.fa) {
      html += '<div class="dlabel">Meaning — <bdi class="fa" lang="fa" dir="rtl">معنی</bdi></div>' +
        '<div class="dline">' + esc(def.en) + '</div>' + faLine(def.fa, 'dline fa');
    }
    html += examples(entry);
    const chips = [];
    if ((entry.syn || []).length) {
      chips.push('<span class="dchip"><b>Syn</b> ' + esc(entry.syn.join(' · ')) + '</span>');
    }
    if ((entry.ant || []).length) {
      chips.push('<span class="dchip"><b>Ant</b> ' + esc(entry.ant.join(' · ')) + '</span>');
    }
    if (chips.length) html += '<div class="dchips">' + chips.join('') + '</div>';
    return html;
  }

  function expressionBody(entry) {
    let html = '';
    [['use', 'Means — <bdi class="fa" lang="fa" dir="rtl">یعنی</bdi>'],
      ['when', 'When — <bdi class="fa" lang="fa" dir="rtl">کجا به کار می‌رود</bdi>']].forEach(([f, label]) => {
      const body = entry[f] || {};
      if (!body.en && !body.fa) return;
      html += '<div class="dlabel">' + label + '</div><div class="dline">' +
        esc(body.en) + '</div>' + faLine(body.fa, 'dline fa');
    });
    html += examples(entry);
    const alt = entry.alt || {};
    if (alt.en) {
      html += '<div class="dlabel">Also say — <bdi class="fa" lang="fa" dir="rtl">این هم می‌شود</bdi></div><div class="drow">' +
        '<div class="grow"><div class="dline">“' + esc(alt.en) + '”</div>' +
        faLine(alt.fa, 'dline fa') + '</div></div>';
    }
    return html;
  }

  /* leadOf() already prints the item's headline — the word, the quote, the
     topic — so the open body starts at what is new. Repeating the headline
     here showed every card's first two lines twice on opening. */
  function conversationBody(entry) {
    const setting = entry.setting || {};
    let html = '';
    if (setting.en) {
      html += '<div class="dline">' + esc(setting.en) + '</div>' + faLine(setting.fa, 'dline fa');
    }
    html += '<div class="dturns">' + (entry.turns || []).map((t, i) =>
      '<div class="dturn' + (i % 2 ? ' alt' : '') + '">' +
      '<div class="dwho">' + esc(t.who) + '</div>' +
      '<div class="dbubble"><div class="dline">' + esc(t.en) + '</div>' +
      faLine(t.fa) + '</div></div>').join('') + '</div>';
    if ((entry.key || []).length) {
      html += '<div class="dchips">' + entry.key.map((k) =>
        '<span class="dchip">' + esc(k.en) + ' — ' +
          '<bdi class="fa" lang="fa" dir="rtl">' + esc(k.fa) + '</bdi></span>').join('') + '</div>';
    }
    (entry.notes || []).forEach((n) => {
      if (n.en) html += '<div class="dnote">' + esc(n.en) + '</div>';
      if (n.fa) html += faLine(n.fa, 'dnote dfa');
    });
    return html;
  }

  const CHEVRON = '<svg viewBox="0 0 12 12" fill="none" stroke="currentColor" ' +
    'stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" ' +
    'aria-hidden="true"><path d="M2.4 4.4 6 8l3.6-3.6"/></svg>';

  function doneTick(id, done) {
    return '<button type="button" class="dtick' + (done ? ' on' : '') + '" data-done="' +
      esc(id) + '" aria-pressed="' + (done ? 'true' : 'false') + '" title="Mark as done — ' +
      'انجام دادم" aria-label="Mark as done">✓</button>';
  }

  /* The panel keeps the full detail, but one line of it per item is enough to
     decide whether to open it: a wall of three expanded cards is what made
     this panel two screens tall before anyone had chosen anything. */
  function leadOf(kind, entry) {
    if (kind === 'words') {
      return '<div class="dlead"><div class="dword">' + esc(entry.en) +
        (entry.ipa ? '<span class="dipa">' + esc(entry.ipa) + '</span>' : '') +
        '</div>' + (entry.pos ? '<div class="dpos">' + esc(entry.pos) + '</div>' : '') +
        faLine(entry.fa) + '</div>';
    }
    if (kind === 'expressions') {
      return '<div class="dlead"><div class="dquote">“' + esc(entry.en) + '”</div>' +
        faLine(entry.fa) + '</div>';
    }
    const topic = entry.topic || {};
    return '<div class="dlead"><div class="dquote">' + esc(topic.en) + '</div>' +
      faLine(topic.fa) + '</div>';
  }

  /* The dialogue keeps its Persian toggle and nothing else. This is reading
     material; the Listening panel is where the app does audio, and a play row
     under every daily card was asking the learner to switch modes to use it. */
  function tools(kind) {
    return kind === 'conversations'
      ? '<div class="dtools"><button type="button" class="dbtn" data-persian="1" ' +
        'aria-pressed="true">Persian: on · <bdi class="fa" lang="fa" dir="rtl">فارسی: روشن</bdi></button></div>'
      : '';
  }

  function paintCard(kind, entry, done) {
    if (!entry) {
      return '<div class="dcard" data-kind="' + kind + '">' +
        cardShell(kind, '', '', '<div class="dnone">This item is missing from the ' +
          'catalogue. / این مورد در کاتالوگ نیست.</div>') + '</div>';
    }
    const extraHead = kind === 'expressions' && entry.register
      ? '<span class="dreg">' + esc(entry.register) + '</span>' : '';
    const body = kind === 'words' ? wordBody(entry)
      : kind === 'expressions' ? expressionBody(entry)
      : conversationBody(entry);
    const head = '<div class="dtop"><span class="dico">' + CARD_ICON[kind] + '</span>' +
      '<span class="dkind">' + KIND_EN[kind] +
      '<small dir="rtl" lang="fa">' + KIND_FA[kind] +
      '</small></span><span class="spacer"></span>' + extraHead +
      (entry.level ? '<span class="dlvl">' + esc(entry.level) + '</span>' : '') +
      doneTick(entry.id, done) +
      '<button type="button" class="dmore" data-more="1" aria-expanded="false" ' +
      'title="More — بیشتر" aria-label="Show more">' + CHEVRON + '</button></div>';
    return '<div class="dcard' + (done ? ' done' : '') + '" data-kind="' + kind +
      '">' + head + leadOf(kind, entry) +
      '<div class="dbody">' + body + tools(kind) + '</div></div>';
  }

  /* The three items for a date. Shared by the panel and by the card in the
     conversation, so the two can never show different content on one day. */
  function ensurePicked(key) {
    if (picked && picked.date === key && cat) return picked;
    picked = {date: key};
    ORDER.forEach((kind) => {
      const rows = (cat && cat[kind]) || [];
      picked[kind] = rows.length
        ? rows[dayIndex(dayNumber(key), rows.length, DAY_SALTS[kind])] : null;
    });
    return picked;
  }

  function progress(key) {
    const ids = ORDER.map((k) => picked && picked[k] && picked[k].id).filter(Boolean);
    return DailyStore.count(DailyStore.read(), key, ids);
  }

  /* Paint the three cards for the current local date, and the progress that
     goes with them. Called on open, on the date changing, and on resume. */
  function paint() {
    const el = els();
    const key = dayKey(new Date());
    shown = key;
    if (el.date) el.date.textContent = key;
    if (!cat) {
      if (el.cards) {
        el.cards.innerHTML = '<div class="dcard"><div class="dnone">' +
          'Today&rsquo;s English could not be loaded. Check the connection and open ' +
          'this panel again.<br><bdi class="fa" lang="fa" dir="rtl">درس امروز بارگذاری نشد — یک بار دیگر این بخش را باز کن.</bdi>' +
          '</div></div>';
      }
      return;
    }
    ensurePicked(key);
    const state = DailyStore.read();
    const done = progress(key);
    if (el.cards) {
      el.cards.innerHTML = ORDER.map((kind) =>
        paintCard(kind, picked[kind], picked[kind] && DailyStore.isDone(state, key, picked[kind].id))
      ).join('');
      bind(el.cards);
    }
    paintProgress(done);
    paintCardToggle();
    mountCard();
  }

  function paintProgress(done) {
    const el = els();
    const pct = Math.round((done / 3) * 100);
    if (el.count) el.count.textContent = done + ' / 3';
    if (el.fill) el.fill.style.width = pct + '%';
    if (el.track) el.track.setAttribute('aria-valuenow', String(done));
    if (el.badge) { el.badge.textContent = String(done); el.badge.hidden = done === 0; }
    const card = document.getElementById('dailyset');
    if (!card) return;
    const fill = card.querySelector('.dump i');
    const label = card.querySelector('.diprog');
    const bar = card.querySelector('.dump');
    if (fill) fill.style.width = pct + '%';
    if (label) label.textContent = done + ' / 3';
    if (bar) bar.setAttribute('aria-valuenow', String(done));
    card.classList.toggle('complete', done === 3);
  }

  function repaintProgress() {
    if (!picked) return;
    paintProgress(progress(dayKey(new Date())));
  }

  /* ---------------------------------------------------------------- the
     card in the conversation.
     The daily set is offered *inside* the chat: one small container in the
     transcript, not a panel that takes the screen. It arrives once a day,
     every row can be opened or ticked without leaving the conversation, and
     the footer can turn today's offer down or the whole thing off. */

  function previewOf(kind, entry) {
    if (kind === 'words') {
      const def = entry.def || {};
      let html = def.en ? '<div class="dline">' + esc(def.en) + '</div>' : '';
      if (def.fa) html += faLine(def.fa, 'dline fa');
      const ex = (entry.examples || [])[0];
      if (ex) {
        html += '<div class="dlabel">Example — <bdi class="fa" lang="fa" dir="rtl">مثال</bdi></div><div class="dline">' +
          esc(ex.en) + '</div>' + faLine(ex.fa, 'dline fa');
      }
      return html;
    }
    if (kind === 'expressions') {
      const use = entry.use || {};
      let html = use.en ? '<div class="dline">' + esc(use.en) + '</div>' : '';
      if (use.fa) html += faLine(use.fa, 'dline fa');
      const ex = (entry.examples || [])[0];
      if (ex) {
        html += '<div class="dlabel">Example — <bdi class="fa" lang="fa" dir="rtl">مثال</bdi></div><div class="dline">' +
          esc(ex.en) + '</div>' + faLine(ex.fa, 'dline fa');
      }
      return html;
    }
    const setting = entry.setting || {};
    let html = setting.en ? '<div class="dline">' + esc(setting.en) + '</div>' : '';
    if (setting.fa) html += faLine(setting.fa, 'dline fa');
    const turns = entry.turns || [];
    html += '<div class="dturns">' + turns.slice(0, 2).map((t, i) =>
      '<div class="dturn' + (i % 2 ? ' alt' : '') + '"><div class="dwho">' +
      esc(t.who) + '</div><div class="dbubble"><div class="dline">' + esc(t.en) +
      '</div>' + faLine(t.fa) + '</div></div>').join('') + '</div>';
    if (turns.length > 2) {
      html += '<div class="dnote">' + (turns.length - 2) +
        ' more lines in the panel. / <bdi class="fa" lang="fa" dir="rtl">ادامهٔ مکالمه در بخش امروز.</bdi>' + '</div>';
    }
    return html;
  }

  function mainOf(kind, entry) {
    if (kind === 'words') return esc(entry.en);
    if (kind === 'expressions') return '“' + esc(entry.en) + '”';
    const topic = entry.topic || {};
    return esc(topic.en || 'Conversation');
  }

  function subOf(kind, entry) {
    if (kind === 'conversations') return esc((entry.topic || {}).fa || '');
    return esc(entry.fa || '');
  }

  function rowHtml(kind, entry, done) {
    if (!entry) return '';
    return '<div class="dirow' + (done ? ' done' : '') + '" data-kind="' + kind + '">' +
      '<span class="dikind">' + CARD_ICON[kind] + '</span>' +
      '<div class="grow"><div class="dimain">' + mainOf(kind, entry) +
      (entry.level ? ' <span class="dlvl">' + esc(entry.level) + '</span>' : '') +
      '</div><div class="disub">' + subOf(kind, entry) + '</div>' +
      '<div class="dibody">' + previewOf(kind, entry) + '</div></div>' +
      '<div class="ditools">' +
      '<button type="button" class="ditick' + (done ? ' on' : '') + '" data-done="' +
      esc(entry.id) + '" aria-pressed="' + (done ? 'true' : 'false') +
      '" title="Done — انجام دادم" aria-label="Mark as done">✓</button>' +
      '<button type="button" class="dimore" data-more="1" aria-expanded="false" ' +
      'title="Open — بیشتر" aria-label="Show details">' + CHEVRON + '</button>' +
      '</div></div>';
  }

  function cardHtml(key) {
    const state = DailyStore.read();
    const done = progress(key);
    const rows = ORDER.map((kind) =>
      rowHtml(kind, picked[kind], picked[kind] && DailyStore.isDone(state, key, picked[kind].id))
    ).join('');
    /* One control per action: the ✕ turns today's offer down for good (the
       card is removed, not folded into a restore line), "Read all three"
       opens every row in place, and the permanent switch sits quiet on the
       right. It used to carry four buttons, two of which skipped the same
       day. */
    return '<div class="dihead"><span class="diico">' + CARD_ICON.today + '</span>' +
      '<span class="dititle">Today&rsquo;s English<small>' + dayLabel(key) +
      '</small></span><span class="spacer"></span>' +
      '<span class="diprog">' + done + ' / 3</span>' +
      '<button type="button" class="dix" data-skip="1" ' +
      'title="Skip today — رد کردن (برنمی‌گردد)" ' +
      'aria-label="Skip today — the card will not come back today">✕</button></div>' +
      '<div class="dump" role="progressbar" aria-label="Today&rsquo;s progress" ' +
      'aria-valuemin="0" aria-valuemax="3" aria-valuenow="' + done + '">' +
      '<i style="width:' + Math.round((done / 3) * 100) + '%"></i></div>' + rows +
      '<div class="difoot">' +
      '<button type="button" class="dibtn ghost" data-learn="1">Read all three — ' +
      '<bdi class="fa" lang="fa" dir="rtl">هر سه</bdi></button>' +
      '<span class="spacer"></span>' +
      '<button type="button" class="dibtn ghost" data-hide="1" ' +
      'title="Don&rsquo;t show again — دیگر نشان نده" ' +
      'aria-label="Don&rsquo;t show again — دیگر نشان نده">Don&rsquo;t show again</button>' +
      '</div>';
  }

  /* Mounted into the transcript, so the daily set is part of the conversation
     rather than a panel over it. Nothing is drawn when the feature has been
     switched off, and the panel's own button is the way back. */
  function mountCard() {
    const chatEl = document.getElementById('chat');
    const existing = document.getElementById('dailyset');
    if (existing && existing.parentNode) existing.parentNode.removeChild(existing);
    if (!chatEl || !cat) return;
    const prefs = DailyStore.readCard();
    const key = dayKey(new Date());
    /* Turning today's offer down is a decision, not a toggle: the card goes,
       and nothing on the page brings it back - not a repaint, not the next
       launch, not a resume. The day is over until tomorrow's card. */
    if (prefs.hidden || DailyStore.isSkipped(prefs, key) ||
        DailyStore.isFinished(prefs, key)) {
      paintCardToggle();
      return;
    }
    ensurePicked(key);
    const node = document.createElement('div');
    node.className = 'dinline' + (progress(key) === 3 ? ' complete' : '');
    node.id = 'dailyset';
    node.setAttribute('role', 'region');
    node.setAttribute('aria-label', "Today's English — انگلیسی امروز");
    node.innerHTML = cardHtml(key);
    chatEl.appendChild(node);
    bindCard(node);
    /* The card is the last thing in the transcript, so on a short screen its
       footer starts below the fold. Nudge it into view only while the reader
       is still at the bottom: scrolling a transcript someone has scrolled up
       in is the one thing a chat must never do. */
    if (pinned) node.scrollIntoView({block: 'nearest'});
    /* the week's card sits under the day's, and moves with it */
    Weekly.refresh();
  }

  function removeCard() {
    const el = document.getElementById('dailyset');
    if (el && el.parentNode) el.parentNode.removeChild(el);
  }

  function bindCard(root) {
    root.querySelectorAll('[data-more]').forEach((b) => {
      b.addEventListener('click', () => {
        const row = b.closest('.dirow');
        const open = row.classList.toggle('open');
        b.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
    });
    /* Tapping a row opens it. The chevron stays the labelled control for
       keyboards and screen readers; this is the same toggle for a thumb, and
       it ignores clicks inside the opened body so selecting a line does not
       fold the row shut under the reader. */
    root.querySelectorAll('.dirow .grow').forEach((g) => {
      g.addEventListener('click', (ev) => {
        if (ev.target.closest('.dibody') || ev.target.closest('button')) return;
        const more = g.parentNode.querySelector('[data-more]');
        if (more) more.click();
      });
    });
    root.querySelectorAll('[data-done]').forEach((b) => {
      b.addEventListener('click', () => {
        const next = toggleDone(b.getAttribute('data-done'));
        b.classList.toggle('on', next);
        b.setAttribute('aria-pressed', next ? 'true' : 'false');
        const row = b.closest('.dirow');
        if (row) row.classList.toggle('done', next);
      });
    });
    root.querySelectorAll('[data-skip]').forEach((b) => {
      b.addEventListener('click', () => skipToday());
    });
    root.querySelectorAll('[data-hide]').forEach((b) => {
      b.addEventListener('click', () => setHidden(true));
    });
    /* "Read all three" opens the rows here instead of throwing the learner
       into the panel: the whole point of the card is that the day is
       readable without leaving the conversation. */
    root.querySelectorAll('[data-learn]').forEach((b) => {
      b.addEventListener('click', () => {
        const list = [...root.querySelectorAll('.dirow')];
        const open = !list.every((r) => r.classList.contains('open'));
        list.forEach((r) => {
          r.classList.toggle('open', open);
          const more = r.querySelector('[data-more]');
          if (more) more.setAttribute('aria-expanded', open ? 'true' : 'false');
        });
        b.innerHTML = open
          ? 'Close all — <bdi class="fa" lang="fa" dir="rtl">بستن همه</bdi>'
          : 'Read all three — <bdi class="fa" lang="fa" dir="rtl">هر سه</bdi>';
        b.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
    });
  }

  /* One place that marks an item done, for the tick in the card and the tick in
     the panel: the badge, both progress bars and the day's count follow, and
     the third tick ends the day - the card closes itself once it is finished
     instead of sitting in the transcript as a spent progress bar. */
  function toggleDone(id) {
    if (!id) return false;
    const key = dayKey(new Date());
    const state = DailyStore.read();
    const next = !DailyStore.isDone(state, key, id);
    DailyStore.setDone(state, key, id, next);
    DailyStore.write(state);
    /* A tick is the app's only proof that the item was met, so the mastery
       ledger is updated here rather than on a schedule: today's word enters the
       review queue the moment it is ticked, due today. */
    try {
      const today = Mastery.keyOf(new Date());
      Mastery.write(Mastery.seedDaily(Mastery.read(), cat, DailyStore.read().days, today));
    } catch (e) { /* the tick is worth more than the schedule */ }
    document.querySelectorAll('[data-done="' + id + '"]').forEach((b) => {
      b.classList.toggle('on', next);
      b.setAttribute('aria-pressed', next ? 'true' : 'false');
      const card = b.closest('.dcard');
      if (card) card.classList.toggle('done', next);
    });
    repaintProgress();
    if (next && progress(key) === 3) closeWhenDone();
    return next;
  }

  /* All three ticked: let the third tick land, then take the card out. The
     day is recorded as finished before the timer runs, so a repaint in the
     half second before it closes cannot re-mount the card behind our back.
     One way only, like a skipped day: unticking in the panel later does not
     reopen the conversation's card - the day has been read. */
  let closing = 0;
  function closeWhenDone() {
    const key = dayKey(new Date());
    DailyStore.writeCard(DailyStore.setFinished(DailyStore.readCard(), key));
    const card = document.getElementById('dailyset');
    if (card) card.classList.add('complete', 'closing');
    if (closing) return;
    closing = setTimeout(() => {
      closing = 0;
      removeCard();
      if (typeof toast === 'function') {
        toast('Today\u2019s English is done \u2014 \u0627\u0645\u0631\u0648\u0632 \u06a9\u0627\u0645\u0644 \u0634\u062f');
      }
    }, 900);
  }

  /* Skipping removes the card outright. There is deliberately no un-skip
     control anywhere: a day the learner turned down must stay turned down,
     so the flag is written and the card is taken out of the transcript. */
  function skipToday() {
    const prefs = DailyStore.readCard();
    DailyStore.writeCard(DailyStore.setSkipped(prefs, dayKey(new Date())));
    removeCard();
    if (typeof toast === 'function') {
      toast("Today's English is skipped. / امروز رد شد");
    }
  }

  function setHidden(on) {
    const prefs = DailyStore.readCard();
    prefs.hidden = on;
    DailyStore.writeCard(prefs);
    if (on) removeCard(); else mountCard();
    paintCardToggle();
    /* The card is gone the moment this runs, so say where it went: the switch
       that brings it back lives in the Today panel. */
    if (on && typeof toast === 'function') {
      toast('Daily card hidden — از بخش Today برگردان');
    }
  }

  /* The panel's own switch, labelled with what it will do next rather than
     with the current state - a button that says "hidden" and does nothing is
     the usual way this goes wrong. */
  function paintCardToggle() {
    const b = document.getElementById('dcardtoggle');
    if (!b) return;
    const hidden = DailyStore.readCard().hidden;
    // English instruction, then the Persian on its own island: the two used to
    // be one string, so the Persian half was laid out left to right.
    b.innerHTML = hidden
      ? 'Show today\u2019s English in the chat — <bdi class="fa" lang="fa" dir="rtl">نمایش کارت روزانه</bdi>'
      : 'Keep today\u2019s English out of the chat — <bdi class="fa" lang="fa" dir="rtl">پنهان کردن کارت روزانه</bdi>';
    b.setAttribute('aria-pressed', hidden ? 'false' : 'true');
  }

  /* One delegated listener for the panel card's buttons, so a repaint never
     leaves a stale handler behind. The ticks live in the card header, so the
     state is visible without opening the card - which is what the panel is
     for now: three collapsed lines you can scan. */
  function bind(root) {
    root.querySelectorAll('[data-more]').forEach((b) => {
      b.addEventListener('click', () => {
        const card = b.closest('.dcard');
        const open = card.classList.toggle('open');
        b.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
    });
    root.querySelectorAll('[data-done]').forEach((b) => {
      b.addEventListener('click', () => toggleDone(b.getAttribute('data-done')));
    });
    root.querySelectorAll('[data-persian]').forEach((b) => {
      b.addEventListener('click', () => {
        const card = b.closest('.dcard');
        const off = card.classList.toggle('persian-off');
        // English first, the Persian toggle word after it as its own island:
        // "فارسی: روشن / Persian: on" opened with a right-to-left run inside
        // a left-to-right button, so the Persian hung off the left edge.
        b.innerHTML = off
          ? 'Persian: off · <bdi class="fa" lang="fa" dir="rtl">فارسی: خاموش</bdi>'
          : 'Persian: on · <bdi class="fa" lang="fa" dir="rtl">فارسی: روشن</bdi>';
        b.setAttribute('aria-pressed', off ? 'false' : 'true');
      });
    });
  }

  /* Everything about the day is already in the catalogue, so "loading" is one
     file read that happens behind the boot screen. */
  async function load() {
    if (cat || failed) return cat;
    try {
      cat = await loadJSON('daily');
    } catch (e) {
      failed = true;
      cat = null;
    }
    return cat;
  }

  /* Repaint when the local date has moved on: on open, on resume, and once at
     the next midnight while the app is left running. No polling - one timer
     that is re-armed for the following midnight each time it fires. */
  function refresh(force) {
    const key = dayKey(new Date());
    if (!force && key === shown) return;
    paint();
  }

  function schedule() {
    clearTimeout(timer);
    timer = setTimeout(() => {
      refresh(true);
      schedule();
    }, untilLocalMidnight(new Date()));
  }

  function init() {
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) return;
      refresh(false);   // resumed: only repaints if the date moved
      mountCard();      // and the day's card is the day's card
      schedule();       // timers do not run while backgrounded
    });
    window.addEventListener('focus', () => refresh(false));
    const toggle = document.getElementById('dcardtoggle');
    if (toggle) {
      toggle.addEventListener('click', () => setHidden(!DailyStore.readCard().hidden));
    }
    schedule();
  }

  return {load, paint, refresh, init, mountCard, removeCard,
          paintCardToggle, skipToday, setHidden};
})();

async function loadDaily() {
  await Daily.load();
  Daily.paint();
  // the daily set is offered in the conversation itself, and skipped or
  // switched off entirely by the learner
  Daily.mountCard();
  // the week's review sits under the day's card, and reads the same catalogue
  await Weekly.init();
  // the drills are a card of their own, under both of those
  await Practice.init();
  // and the circular control in the transcript folds the same sheet out
  await PracticeDrawer.init();
  Slip.init();
}

/* grammar lessons panel (fetched from grammar.json via the server) */
/* English name first, Persian second, each in its own script run: these were
   one string that opened Persian and closed English, on a line the reader
   enters from the left. */
const LEVEL_NAMES = {
  A1: ['Beginner', 'مبانی'],
  A2: ['Elementary', 'پایه'],
  B1: ['Intermediate', 'متوسط'],
  B2: ['Upper-Int.', 'پیشرفته'],
  C1: ['Advanced', 'پیشرفته'],
  C2: ['Proficiency', 'تسلط'],
};
/* Online the server reports the unlock state; offline (APK) the flag lives on
   the local bot engine, so ask whichever one is present. */
function isExamUnlocked(t) {
  if (typeof bot !== 'undefined' && bot && bot.practiceDone && t.id) {
    return bot.practiceDone.has(t.id);
  }
  return !!t.unlocked;
}

async function loadGrammar() {
  try {
    const r = await fetch('/api/grammar');
    const topics = await r.json();
    const box = document.getElementById('gtopics');
    box.innerHTML = '';
    // group by CEFR level so 30+ topics stay compact
    const groups = {};
    topics.forEach(t => {
      const lv = t.level || 'other';
      (groups[lv] = groups[lv] || []).push(t);
    });
    Object.keys(groups).sort().forEach(lv => {
      const wrap = document.createElement('div');
      wrap.className = 'glevel';
      const head = document.createElement('div');
      head.className = 'glevel-head';
      const band = LEVEL_NAMES[lv];
      head.append(
        document.createTextNode(lv + ' · '),
        Object.assign(document.createElement('b'), {textContent: band ? band[0] : lv}),
        Object.assign(document.createElement('span'), {
          className: 'fa', textContent: band ? band[1] : '',
        }),
        Object.assign(document.createElement('span'), {
          className: 'count', textContent: groups[lv].length,
        }),
      );
      wrap.appendChild(head);

      const row = document.createElement('div');
      row.className = 'gtopic';
      groups[lv].forEach(t => {
        // compact pill = one lesson button + one small practice button
        const pill = document.createElement('span');
        pill.className = 'gbtn';

        const b = document.createElement('button');
        b.className = 'gmain';
        b.title = t.title_en + ' — ' + t.title_fa;
        const en = document.createElement('span');
        en.textContent = t.title_en;
        const fa = document.createElement('span');
        fa.className = 'fa';
        fa.textContent = t.title_fa;
        b.append(en, fa);
        b.onclick = () => send(t.query_en);

        const go = document.createElement('button');
        go.className = 'go';
        go.textContent = '✏️';
        go.title = (t.practice_n || 0) + ' practice questions — ' + t.title_en;
        go.setAttribute('aria-label', 'Practice ' + t.title_en);
        go.onclick = () => send(t.practice_en);

        // the 20-question exam — locked until the practice is finished
        const ex = document.createElement('button');
        const open = isExamUnlocked(t);
        ex.className = 'go exam' + (open ? '' : ' locked');
        ex.textContent = '🎓';
        ex.title = open
          ? (t.exam_n || 0) + ' exam questions — ' + t.title_en
          : (t.exam_n || 0) + ' exam questions (locked — finish the practice first)';
        ex.setAttribute('aria-label', 'Exam ' + t.title_en);
        ex.onclick = () => {
          if (ex.classList.contains('locked')) {
            send(t.practice_en);
          } else {
            send(t.exam_en);
          }
        };

        pill.append(b, go, ex);
        row.appendChild(pill);
      });
      wrap.appendChild(row);
      box.appendChild(wrap);
    });
  } catch (e) { /* panel stays empty offline */ }
}
/* ---- the boot screen ----
 * Held for a set spell rather than for as long as the reads happen to take.
 * A boot that returns in three hundred milliseconds reads as a flicker, and
 * this is the one moment every section is being read off disk anyway - so the
 * overlay stays up for a floor of about five seconds while they load behind
 * it, and counts them as they land.
 *
 * It always comes down. Four ways out, and the point of listing them is that
 * any one of them failing still leaves the app usable. A loader that cannot
 * be dismissed is worse than no loader: it is a blank screen with an
 * animation on it, and there is no way to tell that from a crash.
 *
 *   1. the sections finishing, once the floor has also passed
 *   2. an uncaught error, which otherwise leaves the overlay over a page that
 *      is mostly working and so looks broken
 *   3. a rejected promise, which would otherwise be silent
 *   4. a deadline, for the case where a fetch simply never settles
 */
const Boot = (() => {
  const el = document.getElementById('boot');
  if (!el) return { say() {}, step() {}, ready() {}, hide() {} };

  const FLOOR_MS = 5000;     // what start-up should feel like, not how long it takes
  const CEILING_MS = 20000;  // past this the user is watching a spinner, not a load

  const fill = document.getElementById('bootfill');
  const pct = document.getElementById('bootpct');
  const factBox = document.getElementById('bootfacts');
  const fact = document.getElementById('bootfact');
  const factFa = document.getElementById('bootfactfa');
  /* What the app is, not which file is being read: the three tiles above say
     what the day holds, and this line says what the rest of the shelf does.
     Both languages are written here so they cannot drift apart. */
  const FACTS = [
    ['50 graded stories, A1 to C1', '۵۰ داستان سطح‌بندی‌شده، از A1 تا C1'],
    ['A word, an expression, a conversation — every day',
     'هر روز یک واژه، یک عبارت، یک گفت‌وگو'],
    ['A level check across five skills, once a month',
     'سنجش سطح در پنج مهارت، ماهی یک بار'],
    ['Listening from A1 to C2, read aloud on your device',
     'شنیدن از A1 تا C2، با صدای دستگاه'],
    ['48 grammar lessons and an analyser that runs offline',
     '۴۸ درس گرامر و تحلیل‌گری که آفلاین کار می‌کند'],
  ];
  const calm = window.matchMedia('(prefers-reduced-motion: reduce)');
  let factAt = 0;
  let factTimer = 0;
  function showFact(k) {
    const pair = FACTS[k % FACTS.length];
    factBox.classList.add('swap');
    setTimeout(() => {
      fact.textContent = pair[0];
      factFa.textContent = pair[1];
      factBox.classList.remove('swap');
    }, 320);
  }
  if (!calm.matches && FACTS.length > 1) {
    factTimer = setInterval(() => showFact(++factAt), 2100);
  }
  let gone = false;
  let floorUp = false;
  let dataIn = false;
  let deadline = 0;

  /* One number, two readouts.
     The bar and the label were already painted from the same ratio, but not
     on the same clock: the bar eased to it over a .5s CSS transition while the
     label was set at once, so the percentage ran ahead of the bar that was
     reporting it - worst at the end, where the label read 100% while the bar
     still had a tenth of itself to fill. The ratio is eased here instead, once
     per frame, and both readouts are painted from that single value, so they
     cannot disagree: 0 is an empty bar and 0%, 1 is a full bar and 100%, and
     every frame between is the same number in both places. */
  let target = 0;      // what the sections that have landed have earned
  let shown = 0;       // what the screen is showing
  let timer = 0;       // the tick that closes the gap between the two
  let last = 0;        // when that tick last ran, for the time-based ease

  function paint() {
    if (fill) fill.style.transform = 'scaleX(' + shown + ')';
    if (pct) pct.textContent = Math.round(shown * 100) + '%';
  }

  /* Timed, not frame-based. A rAF loop stops dead whenever the page is hidden —
     and this overlay covers the very moment a phone is still locked or the tab
     is still in the background — so a frame-counter would leave the bar parked
     at whatever it had reached and never arrive. Elapsed time is used instead,
     with a 90ms half-life, so a tick that arrives late (a throttled timer, a
     janky frame) closes the same share of the gap a smooth one would. */
  function tick() {
    timer = 0;
    const now = performance.now();
    const dt = last ? Math.min(400, now - last) : 16;
    last = now;
    const gap = target - shown;
    if (gap < 0.0006) {          // close enough to land exactly on it
      shown = target;
      paint();
      maybe();                   // 100% is one of the ways the screen comes down
      return;
    }
    shown += gap * (1 - Math.pow(0.5, dt / 90));
    paint();
    timer = setTimeout(tick, 16);
  }

  function aim(next) {
    target = Math.max(target, Math.min(1, next));   // never goes backwards
    if (gone) return;                               // nothing left to paint on
    if (calm.matches) { shown = target; paint(); maybe(); return; }
    if (!timer && shown !== target) { last = 0; timer = setTimeout(tick, 0); }
  }

  paint();   // 0% over an empty bar, before the first section lands

  function hide() {
    if (gone) return;
    gone = true;
    clearTimeout(timer);
    timer = 0;
    clearTimeout(deadline);
    clearInterval(factTimer);
    el.classList.add('gone');
    // Removed as well as faded: left in the tree it stays a full-screen
    // element that a later focus can land on.
    setTimeout(() => { if (el.parentNode) el.parentNode.removeChild(el); }, 400);
    /* The page is hers now: she climbs out of the composer once the boot card
       is off the screen, so the first thing seen after loading is not a
       static corner. */
    try { ChatFox.mount(); } catch (e) { /* a boot without a composer */ }
    try { input.focus(); } catch (e) { /* the field may not exist yet */ }
  }

  /* Three conditions now, in whichever order they arrive: the floor the design
     asks for, the sections being in, and the bar having actually arrived at
     100%. The third is what makes the number honest at the end - the bar used
     to be able to show 96% and then be whisked away under a label that had
     already said 100%, because the dismissal and the paint were on separate
     clocks. The floor is on a timer rather than on a promise so that a slow
     section cannot extend it, and the ceiling still gets the screen down if
     the data never lands (the bar then says so, by stopping short). */
  function maybe() { if (floorUp && dataIn && shown >= 1) hide(); }
  setTimeout(() => { floorUp = true; maybe(); }, FLOOR_MS);

  deadline = setTimeout(hide, CEILING_MS);
  window.addEventListener('error', hide);
  window.addEventListener('unhandledrejection', hide);

  return {
    /* Kept for callers that want to explain the wait; the card itself now
       shows only the bar and its percentage. */
    say() {},
    step(done, total) {
      aim(total ? done / total : 0);
    },
    /* Every section is in. The overlay still holds until the floor passes. */
    ready() { dataIn = true; maybe(); },
    hide,
  };
})();

/* ---- the sections ----
 * Every one is read here rather than on first open. The loader is on screen
 * anyway, so the reads are close to free where the user can see them, and a
 * panel that opens instantly is worth more than a boot that returns a few
 * hundred milliseconds sooner. Each step reports itself, so the bar counts
 * real work instead of animating a fixed fiction.
 *
 * The last two are the heavy ones and the ones that used to be deferred: the
 * word index is about 450 KB and feeds the chips in Sentences, the catalogue
 * is about a megabyte and feeds the Listen tab. Deferring them saved time
 * nobody was waiting on and made those two sections feel broken.
 */
async function loadAllSections() {
  /* An ordered list of readers, counted so the bar reflects work done. The
     names used to be here as well, for a line that told the reader which file
     was open; that line now carries a fact about the app instead, so the
     labels would only be a second copy of the order below. */
  const steps = [
    loadDaily,
    () => Stickers.load(),
    loadVocabulary,
    loadGrammar,
    loadPhrases,
    loadListening,
    loadPhonetics,
    loadWordArch,
    bbcDoc,
  ];
  let done = 0;
  Boot.step(0, steps.length);
  await Promise.all(steps.map(async (run) => {
    try { await run(); } catch (e) { /* one thin section beats no app */ }
    Boot.step(++done, steps.length);
  }));
}

/* The offline build replaces this line with its bundled boot block, which
   reads the same sections out of the APK's assets and calls
   loadAllSections() itself once the engine is built. */
loadAllSections().finally(() => Boot.ready());

/* live-filter the vocabulary panel as you type */
document.getElementById('vsearch').addEventListener('input', (ev) => {
  window.__vFilter = ev.target.value;
  loadVocabulary();
});
mountMic();
Stickers.mount();
Player.mount();
Motion.init();
Panels.init();
PanelSearch.attachAll();
Path.init();
Daily.init();

/* clear conversation */
/* ---------- clear: button or typed ---------- */
function clearChat() {
  chat.innerHTML = '';
  history.length = 0;
  historyAt = -1;
  add(WELCOME, 'bot');
  Daily.mountCard();     // today's set belongs where the conversation starts
  renderStarters();
  input.focus();
}

/* Typing "clear" (or the Persian equivalents) does exactly what the 🗑 button
   does. Without this the message was treated as a vocabulary lookup. */
const CLEAR_RE = new RegExp(
  '^\\s*(?:please\\s+|لطفا\\s*)?' +
  '(?:' +
    '(?:clear|reset|wipe|delete|erase)' +
    '(?:\\s+(?:the\\s+)?(?:chat|conversation|messages?|history|everything))?' +
    '|پاک\\s*کن(?:\\s*چت|\\s*گفتگو)?' +
    '|پاک\\s*کردن(?:\\s*چت|\\s*گفتگو)?' +
    '|حذف\\s*(?:پیام|چت|گفتگو)[\\u200c\\s\\S]*' +
    '|از\\s*اول\\s*بریم' +
    '|شروع\\s*مجدد' +
  ')' +
  '\\s*(?:please|لطفا|من\\s*فضلك)?\\s*[!.؟]*\\s*$', 'i');

function isClearCommand(text) {
  return CLEAR_RE.test((text || '').trim());
}

document.getElementById('clear').onclick = clearChat;

/* ---------- review list: save words, then drill them ----------
   Words are saved from the word cards in the Sentences panel (⭐) or by
   typing "save apple to review". Progress lives in localStorage so it
   survives a reload, exactly like the daily seed. */
const Review = {
  KEY: 'fluentify.review',
  items: [],            // [{en, fa, pos, forms, level, ok, streak}]
  mode: 'cards',       // 'cards' | 'list'
  at: 0,
  flipped: false,

  load() {
    try {
      const raw = localStorage.getItem(this.KEY);
      if (raw) this.items = JSON.parse(raw) || [];
    } catch (e) { this.items = []; }
    /* A word saved here is a word the learner chose to keep, so it belongs in
       the mastery queue as well. Seeded once; a record that already exists
       keeps its schedule. */
    if (this.items.length) {
      const today = Mastery.keyOf(new Date());
      const seeds = this.items.filter((i) => i && i.en).map((i) => ({
        key: Mastery.itemKey('saved', String(i.en).toLowerCase()),
        kind: 'saved', en: i.en, fa: i.fa || '', level: i.level || '',
      }));
      Mastery.write(Mastery.seed(Mastery.read(), seeds, today));
    }
  },
  save() {
    try { localStorage.setItem(this.KEY, JSON.stringify(this.items)); } catch (e) {}
  },
  has(word) {
    const w = (word || '').toLowerCase();
    return this.items.some((i) => i.en.toLowerCase() === w);
  },
  /* Repaint only when the panel is actually on screen. Painting a hidden
     panel is wasted work on the hot path - every word card's ☆ calls add(). */
  refresh() {
    const panel = document.getElementById('rpanel');
    if (panel && panel.classList.contains('open')) this.paint();
  },
  add(entry) {
    if (!entry || !entry.en) return false;
    if (this.has(entry.en)) return false;
    this.items.push({
      en: entry.en, fa: entry.fa || '', pos: entry.pos || '',
      forms: (entry.forms || []).map((f) => f.f),
      level: entry.level || 'A1', ok: false, streak: 0,
    });
    this.save();
    this.refresh();
    return true;
  },
  remove(word) {
    const w = (word || '').toLowerCase();
    this.items = this.items.filter((i) => i.en.toLowerCase() !== w);
    this.save();
    this.refresh();
  },
  toggle(entry) { return this.has(entry.en) ? (this.remove(entry.en), false) : (this.add(entry), true); },
  reset() { this.items.forEach((i) => { i.ok = false; i.streak = 0; }); this.at = 0; this.flipped = false; this.save(); this.paint(); },
  clear() { this.items = []; this.at = 0; this.flipped = false; this.save(); this.paint(); },
  get mastered() { return this.items.filter((i) => i.ok).length; },
  current() { return this.items[this.at] || null; },
  /* ---------- rendering ---------- */
  paint() {
    const top = document.getElementById('rtop');
    const body = document.getElementById('rbody');
    if (!top || !body) return;
    top.innerHTML = '';
    body.innerHTML = '';

    if (!this.items.length) {
      top.style.display = 'none';
      body.innerHTML =
        '<div class="rempty"><span class="big">⭐</span>' +
        'No words saved yet.<br>Open any word card and tap <b>☆ Save</b> — or type ' +
        '<b>"save apple to review"</b>.<br>' +
        '<bdi class="fa" lang="fa" dir="rtl">هنوز واژه‌ای ذخیره نشده. هر کارت واژه را باز ' +
        'کنید و ☆ را بزنید.</bdi></div>';
      return;
    }
    top.style.display = '';

    const pct = this.items.length ? Math.round(this.mastered / this.items.length * 100) : 0;
    const mk = (tag, cls, txt) => {
      const n = document.createElement(tag);
      if (cls) n.className = cls;
      if (txt != null) n.textContent = txt;
      return n;
    };
    const today = Mastery.keyOf(new Date());
    const mastery = Mastery.read();
    const dueNow = Mastery.due(mastery, today).length;
    const cardsTab = mk('button', 'rtab' + (this.mode === 'cards' ? ' on' : ''), '🃏 Cards');
    cardsTab.onclick = () => { this.mode = 'cards'; this.at = 0; this.flipped = false; this.paint(); };
    const dueTab = mk('button', 'rtab' + (this.mode === 'due' ? ' on' : ''),
      '⏰ Due' + (dueNow ? ' · ' + dueNow : ''));
    dueTab.onclick = () => { this.mode = 'due'; this.dueAt = 0; this.flipped = false; this.paint(); };
    const listTab = mk('button', 'rtab' + (this.mode === 'list' ? ' on' : ''), '📋 List');
    listTab.onclick = () => { this.mode = 'list'; this.paint(); };
    const restart = mk('button', 'rtab rdanger', '↻ Restart');
    restart.onclick = () => this.reset();
    const wipe = mk('button', 'rtab rdanger', '🗑 Empty');
    wipe.onclick = () => this.clear();

    const prog = mk('div', 'rprog');
    const fill = mk('i');
    fill.style.width = pct + '%';
    prog.appendChild(fill);
    const count = mk('div', 'rcount',
      `${this.mastered}/${this.items.length} mastered · ${pct}%`);

    top.append(cardsTab, dueTab, listTab, prog, count, restart, wipe);
    if (this.mode === 'due') this.paintDue(body);
    else (this.mode === 'cards' ? this.paintCard : this.paintList).call(this, body);
  },

  /* ---- the queue the schedule asks for, not the one the list happens to be
     in. Four verdicts rather than the old known/not-known pair, because the
     difference between "hard" and "again" is exactly what decides the next
     interval. */
  paintDue(body) {
    const today = Mastery.keyOf(new Date());
    const state = Mastery.read();
    const due = Mastery.due(state, today);
    const stat = Mastery.stats(state, today);
    const ret = Mastery.retention(state);

    const head = document.createElement('div');
    head.className = 'rprog-line';
    head.textContent = stat.due + ' due today · ' + stat.learning + ' learning · ' +
      stat.mature + ' at three weeks or more';
    body.appendChild(head);
    if (ret.pct7 != null) {
      const retLine = document.createElement('div');
      retLine.className = 'rprog-line';
      retLine.textContent = 'Recall after a week: ' + ret.pct7 + '% of ' +
        ret.at7.n + ' reviews (' + ret.at7.good + ' right).';
      body.appendChild(retLine);
    }

    if (!due.length) {
      const next = Mastery.next(state);
      const empty = document.createElement('div');
      empty.className = 'rempty';
      empty.innerHTML = '<span class="big">🌤</span>' +
        'Nothing is due today.' +
        (next ? '<br>Next: ' + escapeHtml(next) : '') +
        '<br><bdi class="fa" lang="fa" dir="rtl">امروز چیزی برای مرور نیست — ' +
        'بر اساس تاریخ‌های خودت زمان‌بندی شده است، نه برای پر کردن وقت تو.</bdi>';
      body.appendChild(empty);
      return;
    }

    if (this.dueAt >= due.length) this.dueAt = 0;
    const item = due[this.dueAt] || due[0];
    const card = document.createElement('div');
    card.className = 'rcard';
    const word = document.createElement('div');
    word.className = 'rword';
    word.textContent = item.en || item.k;
    card.appendChild(word);
    const kind = document.createElement('span');
    kind.className = 'rpos';
    kind.textContent = item.kind === 'expression' ? 'عبارت' :
      item.kind === 'saved' ? 'ذخیره‌شده' : 'واژه';
    card.appendChild(kind);
    const fa = document.createElement('div');
    fa.className = 'rfa' + (this.flipped ? '' : ' rhidden');
    fa.textContent = item.fa || '—';
    card.appendChild(fa);
    const meta = document.createElement('div');
    meta.className = 'rlvl';
    meta.textContent = 'interval ' + (item.iv || 0) + 'd · seen ' + (item.reps || 0) +
      '×' + (item.lapses ? ' · lapsed ' + item.lapses + '×' : '');
    card.appendChild(meta);
    body.appendChild(card);

    const acts = document.createElement('div');
    acts.className = 'racts';
    const play = document.createElement('button');
    play.className = 'rbtn play';
    play.textContent = '🔊';
    play.title = 'Listen — گوش بده';
    play.onclick = () => Speech.speak(item.en || item.k);
    const flip = document.createElement('button');
    flip.className = 'rbtn';
    flip.style.background = 'rgba(43,48,73,0.085)';
    flip.textContent = this.flipped ? '🙈 Hide' : '👁 Show meaning';
    flip.onclick = () => { this.flipped = !this.flipped; this.paint(); };
    acts.append(play, flip);
    body.appendChild(acts);

    if (this.flipped) {
      const grade = document.createElement('div');
      grade.className = 'racts rgrade';
      [['Again', 0], ['Hard', 1], ['Good', 2], ['Easy', 3]].forEach(([label, v]) => {
        const b = document.createElement('button');
        b.className = 'rbtn';
        b.textContent = label;
        b.dataset.verdict = String(v);
        b.onclick = () => this.gradeDue(item.k, v);
        grade.appendChild(b);
      });
      body.appendChild(grade);
    }
  },

  gradeDue(key, verdict) {
    const today = Mastery.keyOf(new Date());
    Mastery.write(Mastery.grade(Mastery.read(), key, verdict, today));
    this.dueAt += 1;
    this.flipped = false;
    this.paint();
  },

  paintCard(body) {
    if (this.at >= this.items.length) this.at = 0;
    const item = this.current();
    if (!item) { this.paint(); return; }

    const card = document.createElement('div');
    card.className = 'rcard';
    const word = document.createElement('div');
    word.className = 'rword';
    word.textContent = item.en;
    card.appendChild(word);
    if (item.pos) {
      const pos = document.createElement('span');
      pos.className = 'rpos';
      pos.textContent = POS_FA[item.pos] || item.pos;
      card.appendChild(pos);
    }

    const fa = document.createElement('div');
    fa.className = 'rfa' + (this.flipped ? '' : ' rhidden');
    fa.textContent = item.fa || '—';
    card.appendChild(fa);

    if (item.forms && item.forms.length) {
      const forms = document.createElement('div');
      forms.className = 'rforms' + (this.flipped ? '' : ' rhidden');
      forms.textContent = item.forms.join(' · ');
      card.appendChild(forms);
    }
    const lvl = document.createElement('div');
    lvl.className = 'rlvl';
    lvl.textContent = 'CEFR ' + (item.level || 'A1');
    card.appendChild(lvl);

    const acts = document.createElement('div');
    acts.className = 'racts';
    const play = document.createElement('button');
    play.className = 'rbtn play';
    play.textContent = '🔊';
    play.title = 'Listen — گوش بده';
    play.onclick = () => Speech.speak(item.en);
    const flip = document.createElement('button');
    flip.className = 'rbtn';
    flip.style.background = 'rgba(43,48,73,0.085)';
    flip.textContent = this.flipped ? '🙈 Hide' : '👁 Show meaning';
    flip.onclick = () => { this.flipped = !this.flipped; this.paint(); };
    acts.append(play, flip);
    body.append(card, acts);

    if (this.flipped) {
      const grade = document.createElement('div');
      grade.className = 'racts';
      const again = document.createElement('button');
      again.className = 'rbtn again';
      again.textContent = '🔁 Again';
      again.onclick = () => this.grade(false);
      const know = document.createElement('button');
      know.className = 'rbtn know';
      know.textContent = '✅ Know it';
      know.onclick = () => this.grade(true);
      grade.append(again, know);
      body.appendChild(grade);
    }

    const dots = document.createElement('div');
    dots.className = 'rdots';
    this.items.slice(0, 60).forEach((it, i) => {
      const d = document.createElement('span');
      d.className = 'rdot' + (it.ok ? ' on' : '') + (i === this.at ? ' now' : '');
      dots.appendChild(d);
    });
    body.appendChild(dots);
  },

  paintList(body) {
    const list = document.createElement('div');
    list.className = 'rlist';
    this.items.forEach((item) => {
      const row = document.createElement('div');
      row.className = 'rrow' + (item.ok ? ' ok' : '');
      const main = document.createElement('div');
      main.className = 'rmain';
      const en = document.createElement('div');
      en.className = 'ren';
      en.textContent = item.en;
      const fa = document.createElement('div');
      fa.className = 'rfa2';
      fa.textContent = (item.fa || '—') + (item.forms && item.forms.length
        ? '   ·   ' + item.forms.join(' · ') : '');
      main.append(en, fa);
      const play = document.createElement('button');
      play.className = 'ricon';
      play.textContent = '🔊';
      play.title = 'Listen';
      play.onclick = () => Speech.speak(item.en);
      const del = document.createElement('button');
      del.className = 'ricon del';
      del.textContent = '✕';
      del.title = 'Remove — حذف';
      del.onclick = () => this.remove(item.en);
      row.append(main, play, del);
      list.appendChild(row);
    });
    body.appendChild(list);
  },

  /* Grade the current card. The word stays in the list — it is marked known
     or not — and the cursor moves on. Grading used to splice the word out,
     which silently emptied the list. */
  grade(known) {
    const item = this.current();
    if (!item) return;
    if (known) {
      item.ok = true;
      item.streak = (item.streak || 0) + 1;
    } else {
      item.ok = false;
      item.streak = 0;
    }
    this.at += 1;
    if (this.at >= this.items.length) this.at = 0;   // loop round the deck
    this.flipped = false;
    this.save();
    this.paint();
  },
};

/* ============================================================================
 * THE LIBRARY
 * Books → lessons → words. The catalogue is books.json: one entry per book,
 * its lessons, and each lesson's words with a Persian meaning, an English
 * definition and sentences that use them. Nothing here is generated - what is
 * on screen is what the file says - so a definition can be corrected in one
 * place and the web page and the APK both follow.
 *
 * Every line declares its own direction, the way the chat does it: an English
 * definition in an ltr block, a Persian meaning in an rtl one. A single mixed
 * line would be laid out by its first strong character and turn the other
 * language around; that is exactly how the dictionary senses went wrong.
 * ==========================================================================*/
const Books = {
  data: null,
  bookId: null,
  lesson: null,

  box() { return document.getElementById('bbooks'); },

  async load() {
    const box = this.box();
    if (!box) return;
    if (!this.data) {
      box.innerHTML = '<div class="pblurb">Reading the library… / <bdi class="fa" lang="fa" dir="rtl">در حال خواندن کتاب‌ها…</bdi></div>';
      try {
        this.data = await loadJSON('books');
      } catch (e) {
        box.innerHTML = '<div class="pblurb">The books could not be read. / <bdi class="fa" lang="fa" dir="rtl">کتاب‌ها خوانده نشدند.</bdi></div>';
        return;
      }
    }
    this.paint();
  },

  paint() {
    const box = this.box();
    if (!box) return;
    box.innerHTML = '';
    if (!this.data) return;
    const books = this.data.books || [];
    const book = books.find((b) => b.id === this.bookId);
    if (!book) {
      this.bookId = null;
      this.lesson = null;
      this.paintBooks(box, books);
      return;
    }
    if (this.lesson == null) this.paintLessons(box, book);
    else if (book.kind === 'grammar') this.paintStructure(box, book);
    else this.paintWords(box, book);
  },

  /* the word count of a book, computed once so all three depths agree */
  wordsOf(book) {
    return (book.lessons || []).reduce((n, l) => n + (l.words || []).length, 0);
  },

  /* A grammar book teaches structures, not words, so the shelf cannot call
     both kinds "lessons" and both contents "words". */
  isGrammar(book) { return (book || {}).kind === 'grammar'; },

  examplesOf(book) {
    return (book.lessons || []).reduce((n, l) => n + (l.examples || []).length, 0);
  },

  /* what a grammar lesson holds, for its tile and its heading */
  counts(lesson) {
    const ex = (lesson.examples || []).length;
    const pr = (lesson.exercises || []).length;
    const qs = (lesson.exam || []).length;
    const one = (n, s) => n + ' ' + s + (n === 1 ? '' : 's');
    return one(ex, 'example') + ' · ' + one(pr, 'exercise') +
      (qs ? ' · ' + one(qs, 'exam question') : '');
  },

  /* Back one level. The English word for where you are going, then the
     Persian, isolated: "← Lessons · درس‌ها" was one text node, so the
     Persian half of it ran left to right. */
  back(en, fa, fn) {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'bback';
    b.innerHTML = '← ' + escapeHtml(en) +
      (fa ? ' · <bdi class="fa" lang="fa" dir="rtl">' + escapeHtml(fa) + '</bdi>' : '');
    b.onclick = fn;
    return b;
  },

  /* shelf: one card per book */
  paintBooks(box, books) {
    if (!books.length) {
      box.innerHTML = '<div class="pblurb">No book is in the library yet. / <bdi class="fa" lang="fa" dir="rtl">هنوز کتابی در کتابخانه نیست.</bdi></div>';
      return;
    }
    books.forEach((book) => {
      const card = document.createElement('button');
      card.type = 'button';
      card.className = 'bbook';
      card.setAttribute('aria-label', book.title);
      const title = document.createElement('b');
      title.dir = 'ltr';
      title.textContent = book.title;
      card.appendChild(title);
      if (book.title_fa) {
        const fa = document.createElement('span');
        fa.className = 'bfa';
        fa.dir = 'rtl';
        fa.lang = 'fa';
        fa.textContent = book.title_fa;
        card.appendChild(fa);
      }
      const lessons = (book.lessons || []).length;
      const meta = document.createElement('span');
      meta.className = 'bmeta';
      meta.dir = 'ltr';
      meta.textContent = (book.author ? book.author + ' · ' : '') +
        (this.isGrammar(book)
          ? lessons + (lessons === 1 ? ' structure' : ' structures') +
            ' · ' + this.examplesOf(book) + ' examples'
          : lessons + (lessons === 1 ? ' lesson' : ' lessons') +
            ' · ' + this.wordsOf(book) + ' words');
      card.appendChild(meta);
      card.onclick = () => {
        this.bookId = book.id;
        this.lesson = null;
        this.paint();
      };
      box.appendChild(card);
    });
  },

  /* one book: its lessons */
  paintLessons(box, book) {
    box.appendChild(this.back('Books', 'کتاب‌ها', () => {
      this.bookId = null;
      this.lesson = null;
      this.paint();
    }));
    const head = document.createElement('div');
    head.className = 'bhead2';
    head.dir = 'ltr';
    head.textContent = book.title;
    box.appendChild(head);
    // the blurb in both languages: the English one first, on its own line,
    // then the Persian, because a mixed line is laid out by its first strong
    // character and would drag the Persian half left to right
    if (book.author) {
      const by = document.createElement('div');
      by.className = 'bmeta';
      by.dir = 'ltr';
      by.textContent = book.author + (book.edition ? ' · ' + book.edition : '');
      box.appendChild(by);
    }
    if (book.about_en) {
      const about = document.createElement('div');
      about.className = 'pblurb';
      about.dir = 'ltr';
      about.textContent = book.about_en;
      box.appendChild(about);
    }
    if (book.about_fa) {
      const about = document.createElement('div');
      about.className = 'pblurb';
      about.dir = 'rtl';
      about.lang = 'fa';
      about.textContent = book.about_fa;
      box.appendChild(about);
    }
    const list = document.createElement('div');
    list.className = 'bgrid';
    (book.lessons || []).forEach((lesson) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'blesson';
      const name = document.createElement('span');
      name.className = 'bn';
      name.dir = 'ltr';
      // a book that numbers its charts is read chart first, like its contents
      // page: "1-2" then the heading it belongs to
      name.textContent = (lesson.section ? lesson.section + '  ' : '') +
        (lesson.title || ('Lesson ' + lesson.n));
      b.appendChild(name);
      if (lesson.title_fa) {
        const fa = document.createElement('span');
        fa.className = 'bfa';
        fa.dir = 'rtl';
        fa.lang = 'fa';
        fa.textContent = lesson.title_fa;
        b.setAttribute('aria-label', name.textContent + ' — ' + lesson.title_fa);
        b.appendChild(fa);
      }
      const n = document.createElement('span');
      n.className = 'n';
      n.textContent = this.isGrammar(book)
        ? this.counts(lesson)
        : (lesson.words || []).length + ' words';
      b.appendChild(n);
      b.onclick = () => {
        this.lesson = lesson.n;
        this.paint();
        const p = this.box();
        if (p) p.scrollTop = 0;
      };
      list.appendChild(b);
    });
    box.appendChild(list);
  },

  /* one lesson: the words, each with meaning, definition and examples */
  paintWords(box, book) {
    const lesson = (book.lessons || []).find((l) => l.n === this.lesson);
    if (!lesson) {
      this.lesson = null;
      this.paintLessons(box, book);
      return;
    }
    // one sticky row instead of a back button and then a heading that scrolls
    // away: the lesson is twelve cards long on a phone
    const bar = document.createElement('div');
    bar.className = 'bstick';
    bar.appendChild(this.back('Lessons', 'درس‌ها', () => {
      this.lesson = null;
      this.paint();
    }));
    const crumb = document.createElement('span');
    crumb.className = 'bcrumb';
    crumb.textContent = book.title + ' · ' +
      (lesson.title || ('Lesson ' + lesson.n));
    bar.appendChild(crumb);
    const count = document.createElement('span');
    count.className = 'bnum';
    count.textContent = (lesson.words || []).length + ' words';
    bar.appendChild(count);
    box.appendChild(bar);

    const list = document.createElement('div');
    list.className = 'bwords';
    (lesson.words || []).forEach((w, index) => {
      const card = document.createElement('div');
      card.className = 'bword';

      const h = document.createElement('div');
      h.className = 'bwh';
      h.dir = 'ltr';
      const num = document.createElement('span');
      num.className = 'bnum';
      num.textContent = String(index + 1);
      num.setAttribute('aria-hidden', 'true');
      h.appendChild(num);
      const word = document.createElement('b');
      word.textContent = w.word;
      h.appendChild(word);
      if (w.ipa) {
        const ipa = document.createElement('span');
        ipa.className = 'ipa';
        ipa.textContent = w.ipa;
        h.appendChild(ipa);
      }
      if (w.pos) {
        const pos = document.createElement('i');
        pos.className = 'pos';
        pos.textContent = w.pos;
        h.appendChild(pos);
      }
      // a book that teaches in days says which day the word belongs to
      if (w.day) {
        const day = document.createElement('span');
        day.className = 'bday';
        day.textContent = 'Day ' + w.day;
        h.appendChild(day);
      }
      const say = document.createElement('button');
      say.type = 'button';
      say.className = 'bsay';
      say.title = 'Say it — بشنو';
      say.setAttribute('aria-label', 'Say ' + w.word);
      say.textContent = '🔊';
      say.onclick = () => Speech.speak(w.word);
      h.appendChild(say);
      card.appendChild(h);

      if (w.fa) {
        const fa = document.createElement('div');
        fa.className = 'bfa';
        fa.dir = 'rtl';
        fa.lang = 'fa';
        fa.textContent = w.fa;
        card.appendChild(fa);
      }
      if (w.def_en) {
        const def = document.createElement('div');
        def.className = 'bdef';
        def.dir = 'ltr';
        def.textContent = w.def_en;
        card.appendChild(def);
      }
      const examples = w.examples || [];
      if (examples.length) {
        const ul = document.createElement('ul');
        ul.className = 'bex';
        examples.forEach((sentence) => {
          const li = document.createElement('li');
          li.dir = 'ltr';
          const play = document.createElement('button');
          play.type = 'button';
          play.textContent = '▶';
          play.title = 'Hear the sentence — شنیدن جمله';
          play.setAttribute('aria-label', 'Hear: ' + sentence);
          play.onclick = () => Speech.speak(sentence);
          const line = document.createElement('span');
          line.textContent = sentence;
          li.append(play, line);
          ul.appendChild(li);
        });
        card.appendChild(ul);
      }
      list.appendChild(card);
    });
    box.appendChild(list);
  },

  /* one structure: the rule and its form, examples of it in both languages,
     then something to do. A grammar book has no third depth below this, so
     this is the leaf the whole panel ends on. Answers stay folded behind a
     button: a learner who wants to try a gap-fill first should not read the
     answer on the way past. */
  paintStructure(box, book) {
    const lesson = (book.lessons || []).find((l) => l.n === this.lesson);
    if (!lesson) {
      this.lesson = null;
      this.paintLessons(box, book);
      return;
    }
    const bar = document.createElement('div');
    bar.className = 'bstick';
    bar.appendChild(this.back('Structures', 'ساختارها', () => {
      this.lesson = null;
      this.paint();
    }));
    const crumb = document.createElement('span');
    crumb.className = 'bcrumb';
    crumb.textContent = book.title + ' · ' + (lesson.title || ('Structure ' + lesson.n));
    bar.appendChild(crumb);
    const count = document.createElement('span');
    count.className = 'bnum';
    count.textContent = (lesson.examples || []).length + ' examples';
    bar.appendChild(count);
    box.appendChild(bar);

    const card = document.createElement('div');
    card.className = 'bword bstruct';

    const h = document.createElement('div');
    h.className = 'bwh';
    h.dir = 'ltr';
    const num = document.createElement('span');
    num.className = 'bnum';
    num.textContent = String(lesson.n);
    num.setAttribute('aria-hidden', 'true');
    h.appendChild(num);
    const title = document.createElement('b');
    title.textContent = lesson.title || ('Structure ' + lesson.n);
    h.appendChild(title);
    if (lesson.chapter) {
      const ch = document.createElement('span');
      ch.className = 'bchap';
      // the book calls its numbered sections charts, and that is the name a
      // learner will look for when they go back to the printed page
      ch.textContent = /\d-\d/.test(lesson.section || '')
        ? 'Chart ' + lesson.section
        : lesson.chapter;
      h.appendChild(ch);
    }
    card.appendChild(h);

    const faLine = (text, cls) => {
      const el = document.createElement('div');
      el.className = cls;
      el.dir = 'rtl';
      el.lang = 'fa';
      el.textContent = text;
      return el;
    };
    if (lesson.title_fa) card.appendChild(faLine(lesson.title_fa, 'bfa'));
    if (lesson.use_en) {
      const use = document.createElement('div');
      use.className = 'bdef';
      use.dir = 'ltr';
      use.textContent = lesson.use_en;
      card.appendChild(use);
    }
    if (lesson.use_fa) card.appendChild(faLine(lesson.use_fa, 'bfa'));
    if (lesson.form_en) {
      const form = document.createElement('div');
      form.className = 'bform';
      form.dir = 'ltr';
      form.textContent = lesson.form_en;
      card.appendChild(form);
    }

    const label = (en, fa) => {
      const el = document.createElement('div');
      el.className = 'blabel';
      el.innerHTML = escapeHtml(en) +
        (fa ? ' <bdi class="fa" lang="fa" dir="rtl">' + escapeHtml(fa) + '</bdi>' : '');
      return el;
    };

    const examples = lesson.examples || [];
    if (examples.length) {
      card.appendChild(label('Examples', 'مثال‌ها'));
      const group = document.createElement('div');
      group.className = 'bexg';
      examples.forEach((ex) => {
        const row = document.createElement('div');
        row.className = 'bexrow';
        const en = document.createElement('div');
        en.className = 'en';
        en.dir = 'ltr';
        const play = document.createElement('button');
        play.type = 'button';
        play.textContent = '▶';
        play.title = 'Hear the sentence — شنیدن جمله';
        play.setAttribute('aria-label', 'Hear: ' + ex.en);
        play.onclick = () => Speech.speak(ex.en);
        const line = document.createElement('span');
        line.textContent = ex.en;
        en.append(play, line);
        row.appendChild(en);
        if (ex.fa) row.appendChild(faLine(ex.fa, 'fa'));
        group.appendChild(row);
      });
      card.appendChild(group);
    }

    const exercises = lesson.exercises || [];
    if (exercises.length) {
      card.appendChild(label('Exercises', 'تمرین‌ها'));
      exercises.forEach((item, index) => {
        const r = document.createElement('div');
        r.className = 'bexr';
        const q = document.createElement('div');
        q.className = 'q';
        q.dir = 'ltr';
        const n = document.createElement('span');
        n.className = 'num';
        n.textContent = (index + 1) + '.';
        q.append(n, document.createTextNode(' ' + item.prompt));
        r.appendChild(q);
        r.appendChild(this.answer(item.answer, item.why_en, item.why_fa));
        card.appendChild(r);
      });
    }

    const exam = lesson.exam || [];
    if (exam.length) {
      card.appendChild(label('Exam', 'آزمون'));
      exam.forEach((item, index) => {
        const r = document.createElement('div');
        r.className = 'bexr';
        const q = document.createElement('div');
        q.className = 'q';
        q.dir = 'ltr';
        const n = document.createElement('span');
        n.className = 'num';
        n.textContent = (index + 1) + '.';
        q.append(n, document.createTextNode(' ' + item.q));
        r.appendChild(q);
        const opts = document.createElement('div');
        opts.className = 'opts';
        opts.dir = 'ltr';
        (item.options || []).forEach((option) => {
          const o = document.createElement('span');
          o.className = 'opt';
          o.textContent = option;
          opts.appendChild(o);
        });
        r.appendChild(opts);
        r.appendChild(this.answer(item.answer, item.why_en, item.why_fa));
        card.appendChild(r);
      });
    }
    box.appendChild(card);
  },

  /* the folded answer of one exercise or exam question */
  answer(text, whyEn, whyFa) {
    const wrap = document.createElement('div');
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'peek';
    btn.setAttribute('aria-expanded', 'false');
    const ans = document.createElement('div');
    ans.className = 'ans';
    ans.dir = 'ltr';
    ans.setAttribute('hidden', '');
    const key = document.createElement('b');
    key.textContent = text || '—';
    ans.appendChild(key);
    if (whyEn) {
      const why = document.createElement('div');
      why.textContent = whyEn;
      ans.appendChild(why);
    }
    if (whyFa) {
      const why = document.createElement('div');
      why.className = 'why-fa';
      why.dir = 'rtl';
      why.lang = 'fa';
      why.textContent = whyFa;
      ans.appendChild(why);
    }
    const paint = (open) => {
      btn.innerHTML = escapeHtml(open ? 'Hide the answer' : 'Show the answer') +
        ' · <bdi class="fa" lang="fa" dir="rtl">' +
        escapeHtml(open ? 'پنهان کن' : 'پاسخ') + '</bdi>';
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    };
    paint(false);
    btn.onclick = () => {
      const open = ans.hasAttribute('hidden');
      if (open) ans.removeAttribute('hidden');
      else ans.setAttribute('hidden', '');
      paint(open);
    };
    wrap.append(btn, ans);
    return wrap;
  },
};

/* ---------- open a panel by typing its name ----------
   "open grammar section", "بخش شنیدن را باز کن" → the topbar panel slides
   open, exactly as if the button had been tapped. Navigation is not practice,
   so it costs no daily token. */
const SECTIONS = {
  vocabulary: {
    panel: 'vpanel', btn: 'vtoggle', en: 'Vocabulary', fa: 'واژگان', icon: '📚',
    kw: ['vocabulary', 'vocabularies', 'vocab', 'dictionary', 'glossary',
         'word bank', 'words bank', 'واژگان', 'واژه', 'کلمات', 'فرهنگ لغت', 'لغت'],
  },
  grammar: {
    panel: 'gpanel', btn: 'gtoggle', en: 'Grammar', fa: 'گرامر', icon: '📘',
    kw: ['grammar', 'grammer', 'دستور زبان', 'گرامر'],
  },
  analyser: {
    panel: 'npanel', btn: 'ntoggle', en: 'Sentence analyzer', fa: 'تحلیل جمله',
    icon: '🔬',
    kw: ['analyser', 'analyzer', 'analyse', 'sentence analyser', 'sentence analyzer',
         'parts of speech', 'تجزیه جمله', 'تحلیل جمله', 'تحلیل گرامری'],
  },
  sentences: {
    panel: 'fpanel', btn: 'ftoggle', en: 'Sentences', fa: 'جملات', icon: '💬',
    kw: ['sentences', 'sentence', 'phrases', 'phrase bank', 'useful sentences',
         'everyday sentences', 'جملات', 'جمله', 'عبارت', 'عبارات'],
  },
  listening: {
    panel: 'lpanel', btn: 'ltoggle', en: 'Listening', fa: 'گوش دادن', icon: '🎧',
    kw: ['listening', 'audio', 'voice', 'sound', 'pronunciation practice',
         'گوش دادن', 'شنیدن', 'صدا', 'آواز', 'ضبط'],
  },
  books: {
    panel: 'bpanel', btn: 'btoggle', en: 'Books', fa: 'کتاب‌ها', icon: '📚',
    kw: ['books', 'book', 'library', '504', 'essential words', 'lesson', 'lessons',
         'کتاب', 'کتاب‌ها', 'کتابخانه', 'درس', 'دروس', '۵۰۴'],
  },
  reading: {
    panel: 'rdpanel', btn: 'rdtoggle', en: 'Reading', fa: 'خواندن', icon: '📖',
    // "reading strategy", "skim", "scan" and "inference" are what a learner
    // actually types, so the panel opens on the strategy rather than on an
    // empty list. The Persian words are the ones the lessons use.
    kw: ['reading', 'read', 'reading strategies', 'reading strategy',
         'comprehension', 'skim', 'skimming', 'scan', 'scanning', 'inference',
         'خواندن', 'مهارت خواندن', 'راهبرد خواندن',
         'درک مطلب', 'سرمه‌کشی', 'اسکن', 'استنتاج'],
  },
  stories: {
    panel: 'stpanel', btn: 'stoggle', en: 'Mini stories', fa: 'داستان‌ها', icon: '📚',
    // "story", "short story" and "داستان" are what a learner types; the panel
    // opens on the library rather than on the chat.
    kw: ['story', 'stories', 'short story', 'mini story', 'mini stories',
         'graded reader', 'graded readers', 'reading practice', 'fairy tale',
         'داستان', 'داستان کوتاه', 'داستان‌ها', 'قصه'],
  },
  phonetics: {
    panel: 'phpanel', btn: 'phtoggle', en: 'Phonetics', fa: 'تلفظ', icon: '🗣',
    kw: ['phonetics', 'phonetic', 'pronunciation', 'تلفظ', 'فونتیک', 'تلفظ انگلیسی'],
  },
  review: {
    panel: 'rpanel', btn: 'rtoggle', en: 'Review', fa: 'مرور', icon: '⭐',
    kw: ['review', 'reviews', 'flashcards', 'flash cards', 'starred words',
         'saved words', 'my words', 'مرور', 'مرور کلمات', 'کارت های مرور',
         'واژه های ذخیره شده'],
  },
  /* The two panels about the learner were the only two a name could not open.
     Same contract as the rest: a bare "level" or "account" opens it, "open my
     account" opens it, and a question that merely mentions either goes to the
     tutor as before - the bare-word test below is what decides. */
  level: {
    panel: 'lvlpanel', btn: 'lvltoggle', en: 'Level check', fa: 'سنجش سطح', icon: '📊',
    kw: ['level', 'levels', 'level check', 'level test', 'cefr', 'my level',
         'سنجش سطح', 'آزمون سطح', 'تست سطح', 'سطح'],
  },
  account: {
    panel: 'acpanel', btn: 'actoggle', en: 'Account', fa: 'حساب', icon: '👤',
    kw: ['account', 'my account', 'sign in', 'signin', 'log in', 'login',
         'profile', 'حساب', 'حساب کاربری', 'پروفایل', 'ورود'],
  },
};

/* an explicit "do something" verb — anything else is treated as a question
   about the topic, which the bot should answer normally */
/* ============================================================================
 * OFFLINE GRAMMAR ANALYSER
 * A real tagger — winkNLP plus the English web model, 3.5 MB of JavaScript
 * bundled with the page and with the APK — runs the analysis here, on the
 * device. No server, no Python, no network, and no model download: the file
 * is served from /nlp/ on the web and sits next to index.html inside the
 * APK. It is fetched on the first request only, and the model itself is built
 * when it is first asked a question (~80 ms, once), so the sentence is handed
 * over after the browser has painted the "analysing" bubble.
 * ==========================================================================*/
const NLP = (() => {
  /* Relative on purpose. On the web this is /nlp/fluentify-nlp.js; inside the
     APK the page is served from the appassets origin by the WebView asset
     loader, so the same relative path resolves to assets/www/nlp/ with no
     change to the WebView, no file access and no new permission. */
  const SRC = 'nlp/fluentify-nlp.js';
  let loading = null;

  function load() {
    if (window.FluentifyNLP) return Promise.resolve(window.FluentifyNLP);
    if (loading) return loading;
    loading = new Promise((resolve, reject) => {
      const tag = document.createElement('script');
      tag.src = SRC;
      tag.async = true;
      tag.onload = () => (window.FluentifyNLP
        ? resolve(window.FluentifyNLP)
        : reject(new Error('the analyser file loaded but started nothing')));
      tag.onerror = () => reject(new Error('the analyser file is missing (' + SRC + ')'));
      document.head.appendChild(tag);
    });
    return loading;
  }

  async function analyze(sentence) {
    const api = await load();
    /* The first call builds the model. One yield, so the bubble that says the
       sentence is being analysed is on screen before the main thread goes
       busy; after that the model is cached and a bounded sentence costs about
       a millisecond. */
    await new Promise((r) => setTimeout(r, 0));
    return api.analyze(sentence);
  }

  /* Which existing grammar lesson covers a structure the tagger found. These
     are the Knowledge Base's own phrases, so the chip lands on the lesson the
     learner already has; tools/check_analyser.py fails if one stops being a
     keyword in grammar.json. */
  const TOPIC = {
    simple_present: 'simple present', third_person_s: 'subject verb agreement',
    simple_past: 'simple past', past_simple: 'simple past',
    future_simple: 'simple future', present_continuous: 'present continuous',
    past_continuous: 'past continuous', future_continuous: 'future continuous',
    present_perfect: 'present perfect',
    present_perfect_continuous: 'present perfect continuous',
    past_perfect: 'past perfect',
    past_perfect_continuous: 'perfect continuous',
    future_perfect: 'future perfect',
    future_perfect_continuous: 'future perfect progressive',
    modal_verb: 'modal verbs', modal_verbs: 'modal verbs', modal_perfect: 'must have',
    passive_voice: 'passive voice',
    zero_conditional: 'conditionals', first_conditional: 'conditionals',
    second_conditional: 'conditionals', third_conditional: 'conditionals',
    gerund: 'gerunds and infinitives', infinitive: 'gerunds and infinitives',
    verb_infinitive: 'gerunds and infinitives', past_participle: 'be verb past participle',
    articles: 'articles', pronouns: 'pronouns', adjectives: 'adjective order',
    comparison: 'comparatives', adverbs: 'adverbs',
    prepositional_phrase: 'prepositions of time', conjunction: 'conjunctions',
    negation: 'word order', declarative: 'word order', imperative: 'word order',
    exclamative: 'word order', yes_no_question: 'how to ask a question',
    wh_question: 'question words', copular: 'to be',
  };

  return {load, analyze, TOPIC, ready: () => !!window.FluentifyNLP};
})();

/* Does this message ask for a sentence to be taken apart? Kept to explicit
   request wording in both languages, because a message that merely mentions
   grammar is a question for the tutor, not a parse. */
const ANALYSE_INTENT = new RegExp(
  // "analyse [this / the sentence / it]" — the request words are consumed with
  // the verb, so the sentence that follows is left whole
  '(?:analyse|analyze|analysis|parse)\\s*' +
  '(?:this|that|it|these|those|the\\s+sentences?|my\\s+sentences?|' +
  'the\\s+following|below)?|' +
  'break\\s+(?:this|that|it|the)\\s+(?:sentence\\s+)?down|' +
  'break\\s+down\\s+th(?:is|e)\\s+sentence|parts?\\s+of\\s+speech|' +
  'part\\s+of\\s+speech|grammatical\\s+roles?|(?:explain|show)\\s+the\\s+grammar|' +
  '(?:explain|show)\\s+the\\s+structure|grammar\\s+of\\s+th(?:is|e)\\s+sentence|' +
  'sentence\\s+structure|structure\\s+of\\s+th(?:is|e)\\s+sentence|' +
  '(?:find|list)\\s+the\\s+(?:verbs?|nouns?)|nouns?\\s+and\\s+verbs?|' +
  'verbs?\\s+and\\s+nouns?|grammar\\s+(?:analyse|analyze|analysis)|' +
  // "check my grammar", "fix this sentence", "is this sentence right?" - the
  // same request in the words people actually use, which is why they are here
  // and not left to the tutor's general grammar topic, which would answer with
  // a lesson instead of taking the sentence apart
  '\\b(?:check|fix|correct|proofread|review)\\s+(?:the\\s+|my\\s+|this\\s+|that\\s+)?' +
  '(?:grammar|sentences?|english|writing|text)|' +
  '\\bgrammar\\s*(?:check|correction|mistakes?)|' +
  '\\b(?:is|are|was|were)\\s+(?:(?:this|that|it|these|those|the)\\s+)?sentences?\\s+' +
  '(?:grammatically\\s+)?(?:correct|right|wrong|ok|okay|fine)|' +
  '\\bproofread\\s+(?:this|that|it|below)|' +
  '\\bgrammatically\\s+(?:correct|right|wrong)|' +
  "\\b(?:what(?:'s|\\s+is)|anything)\\s+(?:wrong|the\\s+problem|the\\s+mistake)\\s+" +
  'with\\s+(?:this|that|my|the)\\s+(?:sentences?|writing|text)|' +
  '\\bhow\\s+(?:is|was)\\s+(?:this|that|the)\\s+sentence\\s+' +
  '(?:built|formed|structured|made)|' +
  '\\bexplain\\s+(?:this|that|my|the)\\s+sentence|' +
  'گرامر\\s*(?:این|اون|آن|جمله|من|مو)|گرامر\\s*(?:رو|را)|' +
  'این\\s*جمله\\s*(?:رو|را)?\\s*(?:از\\s*نظر\\s*گرامری\\s*)?' +
  '(?:درست|غلط|صحیح)|' +
  '(?:غلط|اشکال|مشکل|خطای)\\s*گرامری|اصلاح\\s*گرامری|' +
  'بررسی\\s*(?:کن|کنید)?\\s*گرامر|تحلیل\\s*گرامری|آنالیز\\s*گرامری|گرامر\\s*این\\s*جمله|' +
  'تجزیه\\s*(?:کن|گرامری)?|نقش\\s*دستوری\\s*کلمات?|نقش\\s*کلمه\\w*|' +
  'از\\s*نظر\\s*گرامری|ساختار\\s*این\\s*جمله|اجزای\\s*جمله|' +
  'فاعل\\s*و\\s*فعل|تحلیل\\s*(?:کن|کنید|این\\s*جمله)?', 'i');

/* The words that ask for the analysis rather than belong to the sentence, and
   the lead-ins a learner naturally types in front of it. */
const ANALYSE_NOISE = new RegExp(
  '^(?:this|that|these|those|the|a|an|of|for|in|on|about|please|below|following|' +
  'sentence|sentences|grammar|structure|role|roles|word|words|verb|verbs|noun|nouns|' +
  'subject|object|me|it|and|to|do|does|can|you|my|its|its\\s+grammar|sentence\\s+grammar|' +
  'the\\s+grammar|the\\s+structure|از|را|این|آن|جمله|جملهٔ|گرامری|گرامر|رو)\\s+', 'i');

/* A determiner is only the request's, never the sentence's: "the structure of
   this sentence: The book was written by George" loses the first "the", while
   "analyse this: The book was written by George" keeps the one that belongs to
   the sentence. */
const ANALYSE_DETERMINER = ['the', 'this', 'that', 'these', 'those', 'a', 'an'];

/* Pull the sentence out of the request. The sentence is what the learner
   pasted: the longest run of Latin words left once the request itself is
   gone. Persian around it is dropped, and a request with no sentence in it
   returns '' rather than a guess. */
function extractSentence(text) {
  const raw = String(text);
  /* A colon is the learner showing us where the sentence begins, so it is
     trusted before anything is guessed at. */
  const colon = raw.lastIndexOf(':');
  if (colon !== -1) {
    const tail = raw.slice(colon + 1).trim();
    const words = (tail.match(/[A-Za-z][A-Za-z0-9'’\-]*/g) || []);
    if (words.length > 1) return tail.replace(ANALYSE_INTENT, ' ').replace(/\s+/g, ' ').trim();
  }
  let rest = raw.replace(ANALYSE_INTENT, ' ').replace(/[؟?،,]+/g, ' ');
  const runs = (rest.match(/[A-Za-z][A-Za-z0-9'’\-]*(?:[ \t]+[A-Za-z0-9'’\-]+)*[.!?…]*/g) || [])
    .map((s) => s.replace(/[ \t]+/g, ' ').trim())
    .filter((s) => s.length > 1);
  if (!runs.length) return '';
  let best = runs.reduce((a, b) => (b.length > a.length ? b : a), '');
  let guard = 0;
  while (guard++ < 14) {
    const m = best.match(ANALYSE_NOISE);
    if (!m) break;
    const word = m[0].trim().toLowerCase();
    const next = best.slice(m[0].length).trim().split(/\s+/)[0].toLowerCase();
    if (ANALYSE_DETERMINER.indexOf(word) !== -1 && !ANALYSE_NOISE.test(next + ' ')) break;
    best = best.slice(m[0].length);
  }
  // The learner's own punctuation is part of the sentence, so only the
  // separators the request left behind come off.
  best = best.replace(/[\s:;,]+$/, '').trim();
  // one Latin word on its own is not a sentence to analyse
  return /[A-Za-z]/.test(best) && best.split(/\s+/).length > 1 ? best : '';
}

/* The sentence types the analyser can name, in the order they beat each other:
   "Can you help me?" is a question whatever else is true of it. */
const SENTENCE_TYPES = ['question', 'yes_no_question', 'imperative', 'exclamative',
                        'declarative'];

/* Structures that describe a word class rather than the sentence's grammar.
   They are still listed under Structures; they are not what "check my
   grammar" is asking about. */
const GRAMMAR_GENERIC = ['pronouns', 'articles', 'adjectives', 'adverbs',
                         'conjunction', 'prepositional_phrase', 'negation',
                         'third_person_s', 'gerund', 'infinitive', 'past_participle',
                         'comparison', 'modal_verbs', 'wh_question'];

/* The grammar of the sentence, written out as words: what kind of sentence it
   is, which construction it uses, and the pattern to copy. A word table answers
   "what is each word?" - it never answers "what is this sentence?", which is
   what was actually asked.

   The construction is the tagger's own claim, never ours. Among the claims
   that state a form ("has/have been + -ing: ...") the last one wins, because
   the tagger adds a structure once it covers more of the sentence: a
   conditional is claimed after the tenses of its two halves, so "If it rains,
   we will stay home" is a First conditional rather than a Future Simple. With
   no stated form, the first specific claim stands, so a copular "They was
   happy" is told it is "be + complement" rather than being told nothing. */
function grammarReadout(r) {
  const details = (r.structureDetails || []).filter((d) => d.label_en);
  const type = details.filter((d) => SENTENCE_TYPES.indexOf(d.id) !== -1)[0];
  const specific = details.filter((d) =>
    (!type || d.id !== type.id) && GRAMMAR_GENERIC.indexOf(d.id) === -1);
  const stated = specific.filter((d) =>
    d.note_en && d.note_en.indexOf(':') !== -1 && /\+/.test(d.note_en.split(':')[0]));
  const form = stated[stated.length - 1] || specific[0];

  const out = ['<div class="ngram">'];
  if (form) {
    const bits = form.note_en ? form.note_en.split(':') : [''];
    const pattern = (bits.length > 1 ? bits[0] : '').trim();
    const rest = (bits.length > 1 ? bits.slice(1).join(':') : bits[0] || '').trim();
    out.push('<div class="ngram-kind">' + escapeHtml(form.label_en) +
      '<small>' + escapeHtml(form.label_fa || '') + '</small></div>');
    if (pattern) out.push('<div class="ngram-form">' + escapeHtml(pattern) + '</div>');
    if (rest) out.push('<div class="ngram-note">' + escapeHtml(rest) + '</div>');
    if (form.note_fa) out.push('<div class="ngram-note fa">' + escapeHtml(form.note_fa) + '</div>');
  } else {
    out.push('<div class="ngram-kind">Simple sentence<small>جملهٔ ساده</small></div>');
    out.push('<div class="ngram-note">No tense or construction is claimed for this ' +
      'sentence — the words are below.</div>');
    out.push('<div class="ngram-note fa">برای این جمله ساختار خاصی ادعا نمی‌شود؛ ' +
      'کلمه‌ها در جدول پایین آمده‌اند.</div>');
  }
  if (type) {
    out.push('<div class="ngram-type">' + escapeHtml(type.label_en) +
      (type.label_fa ? ' · ' + escapeHtml(type.label_fa) : '') + '</div>');
  }
  out.push('</div>');
  return out.join('');
}

/* The analysis, rendered once and used twice: in the chat and in the panel.
   Every field is escaped; nothing from the tagger is trusted as markup. */
function renderAnalysis(r, opts) {
  const o = opts || {};
  const words = r.tokens.filter((t) => ['PUNCT', 'SYM'].indexOf(t.pos) === -1);
  const out = [];

  out.push(grammarReadout(r));

  out.push('<div class="nhead"><b>' + escapeHtml(r.analysedSentence || r.originalSentence) +
    '</b>' + (r.analysedSentence && r.analysedSentence !== r.originalSentence
      ? '<div class="dfa">فقط بخش انگلیسی همین جمله تحلیل شد.</div>' : '') + '</div>');

  out.push('<div class="nlabel">Words — <bdi class="fa" lang="fa" dir="rtl">کلمات</bdi></div><div class="ntable">');
  for (const t of words) {
    out.push('<div class="nrow">' +
      '<span class="nw">' + escapeHtml(t.text) + '</span>' +
      '<span class="npos">' + escapeHtml(t.posLabel) + '<small>' + escapeHtml(t.posLabelFa) + '</small></span>' +
      '<span class="nlemma">' + (t.lemma && t.lemma !== t.text.toLowerCase()
        ? '→ ' + escapeHtml(t.lemma) : '') + '</span>' +
      '<span class="nrole">' + (t.grammaticalRole
        ? escapeHtml(t.roleLabel || t.grammaticalRole) + '<small>' + escapeHtml(t.roleLabelFa || '') + '</small>'
        : '<span class="nunknown">role: not claimed</span>') + '</span>' +
      '</div>');
  }
  out.push('</div>');

  const details = (r.structureDetails || []).filter((d) => d.label_en);
  if (details.length) {
    out.push('<div class="nlabel">Structures — <bdi class="fa" lang="fa" dir="rtl">ساختارها</bdi></div>');
    for (const d of details) {
      const topic = NLP.TOPIC[d.id];
      const words2 = (d.evidence || []).map((i) => (r.tokens[i] ? r.tokens[i].text : ''))
        .filter(Boolean).join(' ');
      out.push('<div class="ncard">' +
        '<div class="ntitle">' + escapeHtml(d.label_en) + '<small>' + escapeHtml(d.label_fa || '') + '</small></div>' +
        (words2 ? '<div class="nev">' + escapeHtml(words2) + '</div>' : '') +
        '<div class="nnote2">' + escapeHtml(d.note_en || '') + '</div>' +
        (d.note_fa ? '<div class="dfa">' + escapeHtml(d.note_fa) + '</div>' : '') +
        (topic ? '<button type="button" class="nchip" data-ask="' + escapeHtml(topic) +
          '">📘 ' + escapeHtml(topic) + ' · <bdi class="fa" lang="fa" dir="rtl">درس</bdi></button>' : '') +
        '</div>');
    }
  }

  /* The tagger ships one standing caveat about its own method. It describes
     the engine rather than the sentence on screen, so the panel prints only
     the caveats this analysis earned — "read" that is also a present, a
     contraction the tagger expanded, a paste that was cut to length. */
  const caveats = (r.limitations || []).filter((l) => !/dependency parser/.test(l));
  if (caveats.length) {
    out.push('<div class="nlabel">What this cannot do — <bdi class="fa" lang="fa" dir="rtl">محدودیت‌ها</bdi></div><ul class="nlim">');
    for (const l of caveats) out.push('<li>' + escapeHtml(l) + '</li>');
    out.push('</ul>');
  }

  return out.join('');
}

/* One click on a lesson chip asks the existing Knowledge Base for the topic.
   Bound once, on the document, so it works for a bubble and for the panel. */
document.addEventListener('click', (ev) => {
  const chip = ev.target.closest && ev.target.closest('.nchip');
  if (!chip) return;
  ev.preventDefault();
  send(chip.getAttribute('data-ask'));
});

/* The sentences the panel offers as a first click: three the analyser is
   confidently right about, and one question, which is the shape learners
   most often want explained. */
const ANALYSE_EXAMPLES = [
  'She has been learning English.',
  'The book was written by George.',
  'If it rains, we will stay home.',
  'Can you help me?',
];

const Analyser = (() => {
  let mounted = false;
  const paint = (html) => { const el = document.getElementById('nresult'); if (el) el.innerHTML = html; };

  async function run(sentence) {
    mount();
    const box = document.getElementById('ninput');
    const text = (sentence || (box ? box.value : '') || '').trim();
    if (!text) { box && box.focus(); return; }
    if (box) box.value = text;
    paint('<div class="nbusy">🔬 analyzing on this device… · <bdi class="fa" lang="fa" dir="rtl">در حال تحلیل…</bdi></div>');
    try {
      paint(renderAnalysis(await NLP.analyze(text)));
    } catch (e) {
      paint('<div class="nfail">⚠️ ' + escapeHtml(e.message) +
        '<br><bdi class="fa" lang="fa" dir="rtl">تحلیل انجام نشد.</bdi></div>');
    }
  }

  /* The same analysis the chat bubble just showed, kept in the panel so it can
     be re-read after the conversation has moved on. */
  function show(result, sentence) {
    const box = document.getElementById('ninput');
    if (box && sentence) box.value = sentence;
    open();
    paint(renderAnalysis(result));
  }

  function mount() {
    if (mounted) return;
    mounted = true;
    const go = document.getElementById('ngo');
    const box = document.getElementById('ninput');
    if (go) go.onclick = () => run();
    if (box) box.onkeydown = (ev) => { if (ev.key === 'Enter') { ev.preventDefault(); run(); } };
    const row = document.getElementById('nexamples');
    if (row) {
      row.textContent = '';
      ANALYSE_EXAMPLES.forEach((s) => {
        const b = document.createElement('button');
        b.type = 'button';
        b.className = 'nex';
        b.textContent = s;
        b.onclick = () => run(s);
        row.appendChild(b);
      });
    }
  }

  function open() {
    const panel = document.getElementById('npanel');
    if (panel && !panel.classList.contains('open')) document.getElementById('ntoggle').onclick();
    mount();
  }

  return {run, show, mount, open};
})();

/* A grammar-analysis request is answered here, on the device, before the
   Knowledge Base is consulted at all: it costs nothing from the daily seed
   and it works with the aeroplane mode on.

   Three pieces of context matter, and keywords alone cannot see any of them:
   a request with no sentence in it is a promise to send one, "what about this
   one" means the sentence in the same message, and "that sentence" means the
   one the learner just sent. Each is tracked below. */

/* Asked for a sentence and not given one yet: one message, then forgotten. */
let analyseWaiting = false;
/* The sentence taken apart most recently, so a follow-up has something to
   compare against and "what about it?" is not a dead end. */
let lastAnalysed = '';
/* The last ordinary message the learner typed - the sentence "the one I just
   sent" points at. */
let lastTyped = '';

const ANALYSE_CANCEL = /^(?:no|cancel|never\s*mind|forget\s*it|stop|not\s*now|بیخیال|نه|لغو|ولش|الان\s*نه)$/i;

/* Follow-ups: "what about this one", "and this:", «و این یکی». Only counts
   when something is already in play, so a cold "what about" is still chat. */
const ANALYSE_FOLLOWUP = new RegExp(
  '^(?:and|what\\s+about|how\\s+about|also|now)\\b|' +
  '^(?:و|در\\s*مورد|حالا)\\b|' +
  '(?:this|that|it|these|those)\\s+one|همین\\s*(?:یکی|جمله)|این\\s*یکی', 'i');

/* "the sentence I just sent", "my last message", «جملهٔ قبلی». */
const ANALYSE_PREVIOUS = new RegExp(
  '(?:the\\s+)?(?:sentence|message|text|one)\\s+(?:that\\s+)?(?:i\\s+)?(?:just\\s+)?' +
  '(?:sent|typed|wrote|said|pasted)|previous\\s+(?:sentence|message)|' +
  'last\\s+(?:sentence|message)|جمله(?:\\u0654|\\s)*(?:قبلی|اخیر|بالا)|پیام\\s*قبلی', 'i');

/* Two Latin words are the floor for "this is a sentence to analyse": one word
   is a lookup, and a Persian-only message is not something the English tagger
   can take apart. */
function looksLikeSentence(text) {
  const latin = ((text || '').match(/[A-Za-z][A-Za-z0-9'’-]*/g) || []);
  return latin.length > 1 && String(text).length <= 300;
}

/* Run the tagger, show the analysis, keep the context straight. */
async function analyseSentence(sentence) {
  showTyping();
  try {
    const result = await NLP.analyze(sentence);
    hideTyping();
    lastAnalysed = sentence;
    Analyser.show(result, sentence);
    add(renderAnalysis(result), 'bot', {html: true});
  } catch (e) {
    hideTyping();
    add('⚠️ ' + e.message + '\n' +
        'تحلیل انجام نشد — این بخش نباید به اینترنت نیاز داشته باشد.', 'bot', {err: true});
  }
}

/* The message after a bare "check my grammar" is the sentence. It is taken
   before the sections and the tutor, because at that moment the learner has
   already told us what the message is. */
async function takePendingSentence(text) {
  if (!analyseWaiting) return false;
  const t = (text || '').trim();
  if (!t) return false;
  if (ANALYSE_CANCEL.test(t)) {
    analyseWaiting = false;
    add(t, 'user');
    add('No problem — nothing analysed. Ask again whenever you like.\n' +
        'باشه، تحلیلی انجام نشد. هر وقت خواستی دوباره بپرس.', 'bot');
    return true;
  }
  /* One message is the window: if it is not a sentence, the request lapses
     rather than lying in wait for a sentence an hour later. */
  if (!looksLikeSentence(t) || ANALYSE_INTENT.test(t)) { analyseWaiting = false; return false; }
  add(t, 'user');
  analyseWaiting = false;
  await analyseSentence(t);
  return true;
}

async function matchAnalyseCommand(text) {
  const t = (text || '').trim();
  if (!t || t.length > 300) return false;
  const asked = ANALYSE_INTENT.test(t);
  /* A follow-up only counts when there is something to follow up on. */
  const followUp = !asked && (lastAnalysed || analyseWaiting) && ANALYSE_FOLLOWUP.test(t);
  if (!asked && !followUp) return false;

  add(t, 'user');
  let sentence = extractSentence(t);

  /* "check the grammar of the sentence I just sent" - the sentence is not in
     this message, so the last thing they typed is the subject. The extractor
     happily reports "I just sent" as a sentence, which is why the reference
     wins over whatever it found: a message pointing at a previous sentence has
     no sentence of its own unless one follows a colon. */
  if (ANALYSE_PREVIOUS.test(t) && !/:\s*\S/.test(t)) {
    if (lastTyped && looksLikeSentence(lastTyped)) sentence = lastTyped;
    else if (lastAnalysed) sentence = lastAnalysed;
  }
  /* "what about it?" with nothing new in the message: re-open the last
     analysis rather than pretend the learner pasted something. */
  if (!sentence && followUp && lastAnalysed && !/[A-Za-z]{2,}/.test(t.replace(ANALYSE_FOLLOWUP, ''))) {
    sentence = lastAnalysed;
  }

  if (!sentence) {
    analyseWaiting = true;
    Analyser.open();
    add('🔬 Send me one English sentence and I will take it apart word by word: ' +
        'the grammar, the tense, and what each word is doing. Nothing leaves your device.\n' +
        'یک جملهٔ انگلیسی بفرست تا گرامر و نقش کلمه‌هایش را بگویم؛ همه‌چیز روی دستگاه خودت انجام می‌شود.\n' +
        'Try: **check my grammar: She has been learning English.**', 'bot');
    return true;
  }
  analyseWaiting = false;
  await analyseSentence(sentence);
  return true;
}

const OPEN_VERB = new RegExp(
  '(?:^|\\s)(?:open|show|display|bring\\s*up|go\\s*to|take\\s*me\\s*to|view|' +
  'switch\\s*to|activate)' +
  '|باز\\s*کن|باز\\s*کردن|نشان\\s*بده|نشون\\s*بده|نشانم\\s*بده|برو\\s*به|ببر|بیا\\s*به' +
  '(?:\\s|$)', 'i');
/* …or the message is basically just the section's name */
const SECTION_MARKER = new RegExp(
  '(?:section|panel|tab|part|بخش|تب|قسمت)', 'i');

function matchSectionCommand(text) {
  const t = (text || '').trim();
  if (!t || t.length > 70) return null;          // too long to be a command
  const low = t.toLowerCase();
  let found = null;
  for (const [id, s] of Object.entries(SECTIONS)) {
    if (s.kw.some((k) => low.includes(k))) { found = [id, s]; break; }
  }
  if (!found) return null;
  const [id, s] = found;
  const bare = new RegExp(
    '^(?:the\\s+|منظره\\s+)?(?:' + s.kw.map((k) => k.replace(/ /g, '\\s')).join('|') +
    ')\\s*(?:' + SECTION_MARKER.source + ')?\\s*[\\s.!?؟!]*$', 'i');
  if (OPEN_VERB.test(t) || SECTION_MARKER.test(t) || bare.test(t)) return [id, s];
  return null;
}

/* Opens the panel and keeps it open. Typing "listening" twice must not close
   it again — that was the other half of "doesn't work properly". */
function openSection(id, s, echo) {
  const panel = document.getElementById(s.panel);
  if (!panel) return false;
  const alreadyOpen = panel.classList.contains('open');
  if (!alreadyOpen) {
    // reuse the topbar toggle so only ever one panel is open
    document.getElementById(s.btn).onclick();
  }
  if (id === 'review') {
    Review.mode = 'cards';
    Review.at = 0;
    Review.flipped = false;
    Review.paint();
  }
  if (echo) {
    add(echo, 'user');
    add(`${s.icon} **${s.en}** section is open (${s.fa}).\n` +
        (id === 'review' && !Review.items.length
          ? 'No words saved yet — open any word card and tap ☆ Save to review.'
          : `بخش ${s.fa} باز شد.`) +
        '\nType the section name again any time to bring it back.',
        'bot');
  }
  return true;
}

/* ---------- review commands typed in chat ---------- */
const SAVE_RE = new RegExp(
  // …save X (to|for|in) [my] review [list]
  '^(?:please\\s+|لطفا\\s*)?(?:save|add|star|bookmark|keep|put)\\s+' +
  '(?:the\\s+(?:word\\s+)?)?["\'«"]?([^"\'«»!?؟]{1,40}?)["\'»"]?\\s*' +
  '(?:to|in|into|for)\\s+(?:my\\s+)?review(?:\\s+list)?\\s*[!.؟]*$' +
  // …a bare, deliberate save — "save apple", never "add apple"
  '|^(?:please\\s+|لطفا\\s*)?(?:save|star|bookmark)\\s+' +
  '(?:the\\s+word\\s+)?["\'«"]?([^"\'«»!?؟]{1,40}?)["\'»"]?\\s*[!.؟]*$' +
  // Persian: ذخیره کردن X برای مرور
  '|^(?:ذخیره|اضافه)\\s+کردن(?:\\s+کلمه)?\\s*["«]?([^"»!?؟]{1,40}?)["»]?\\s*' +
  '(?:برای\\s+مرور|به\\s+مرور)?\\s*[!.؟]*$', 'i');

/* "save time is money" is a sentence, not a command — reject anything that
   looks like more than a word or two, or that carries filler words.
   (up/out stay out of the list: "give up", "look it up" are real entries.) */
const SAVE_STOPWORDS = /\b(?:is|are|the|a|an|to|for|my|me|it|that|this|and|of)\b/i;
function looksLikeWord(s) {
  const parts = s.trim().split(/\s+/);
  return parts.length <= 3 && !SAVE_STOPWORDS.test(s);
}

const REVIEW_OPEN_RE = new RegExp(
  '^(?:please\\s+|لطفا\\s*)?(?:open\\s+)?(?:my\\s+)?' +
  '(?:review(?:\\s+(?:list|words|section))?|flashcards?|starred\\s+words?)' +
  '|^(?:بخش\\s+)?مرور(?:\\s+(?:کلمات|لیست))?|کارت\\s*های\\s*مرور' +
  '\\s*[!.؟]*$', 'i');

async function matchReviewCommand(text) {
  const t = (text || '').trim();

  if (REVIEW_OPEN_RE.test(t)) {
    add(t, 'user');
    if (!Review.items.length) {
      add('⭐ Your review list is empty. Open any word card and tap **☆ Save to review**.', 'bot');
      return true;
    }
    const panel = document.getElementById('rpanel');
    const btn = document.getElementById('rtoggle');
    if (!panel.classList.contains('open')) btn.onclick();   // open it
    Review.mode = 'cards';
    Review.at = 0;
    Review.flipped = false;
    Review.paint();
    add(`🃏 Reviewing ${Review.items.length} word(s) — tap **Show meaning**, then grade yourself.`, 'bot');
    return true;
  }

  const m = SAVE_RE.exec(t);
  if (!m) return false;
  if (!looksLikeWord((m[1] || m[2] || m[3] || '').trim())) return false;
  const word = (m[1] || m[2] || m[3] || '').trim().replace(/[.!?؟,]+$/, '');
  if (!word || !looksLikeWord(word)) {
    add(t, 'user');
    add('I could not tell which word to save. Try **"save apple to review"**.', 'bot');
    return true;
  }
  const key = word.toLowerCase();

  // word_arch.json is fetched lazily now, so saving a word before the
  // Sentences panel has ever been opened would find nothing and tell the
  // learner the word is not in the vocabulary. Fetch it here instead - only on
  // this path, so an ordinary message never pays for it.
  if (!wordArchLoaded) await loadWordArch();

  // keep the Persian and the form family by looking the word up
  let entry = null;
  for (const list of Object.values(wordArch)) {
    const hit = list.find((e) => e.en.toLowerCase() === key);
    if (hit) { entry = hit; break; }
  }
  add(t, 'user');
  if (!entry) {
    add(`I don't have **${word}** in the vocabulary to save yet — look for it in the Sentences panel first.`, 'bot');
    return true;
  }
  if (Review.has(word)) {
    add(`⭐ **${entry.en}** is already in your review list (${Review.items.length} word(s)).`, 'bot');
    return true;
  }
  Review.add(entry);
  add(`⭐ Saved **${entry.en}** (${entry.fa}) — ${Review.items.length} word(s) in your review list.\n` +
      `Open ⭐ Review in the top bar to drill it.`, 'bot');
  return true;
}

/* ---------- keyboard: the shortcuts people expect ---------- */
input.addEventListener('keydown', (ev) => {
  // ↑/↓ walk back through what you typed, like every messenger
  if (ev.key === 'ArrowUp') {
    ev.preventDefault();
    if (!history.length) return;
    if (historyAt === -1) historyAt = history.length;
    historyAt = Math.max(0, historyAt - 1);
    input.value = history[historyAt];
    setTimeout(() => input.setSelectionRange(input.value.length, input.value.length), 0);
  } else if (ev.key === 'ArrowDown') {
    ev.preventDefault();
    if (historyAt === -1) return;
    historyAt = Math.min(history.length, historyAt + 1);
    input.value = historyAt === history.length ? '' : history[historyAt];
  }
});

document.addEventListener('keydown', (ev) => {
  if (ev.key === 'Escape') {
    // Esc closes whichever panel is open, then stops any audio
    const open = document.querySelector('#vpanel.open, #gpanel.open, #fpanel.open, #lpanel.open, #phpanel.open, #bpanel.open');
    if (open) { open.classList.remove('open'); return; }
    Speech.stop();
  }
});

/* ---------- stop auto-scrolling once the reader scrolls up ---------- */
chat.addEventListener('scroll', () => {
  pinned = chat.scrollHeight - chat.scrollTop - chat.clientHeight < 90;
  paintJump();
});


/* boot */
Review.load();          // after every declaration above
Review.paint();         // and paint once here as well as on open, so the
                        // panel can never be reached in a blank state even if
                        // the on-open hook is missed
add(WELCOME, 'bot');
renderStarters();
Seed.load();
input.focus();
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def _send_text(self, body: str, content_type: str,
                   cache_seconds: int = 0, status: int = 200) -> None:
        """Reply with a plain body. `_send_json` covers everything else."""
        raw = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        if cache_seconds:
            self.send_header("Cache-Control", f"public, max-age={cache_seconds}")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _send_json(self, payload, cache_seconds: int = 300) -> None:
        """Reply with JSON. Anything read from a file on disk is cached
        briefly, because those files are re-read on every request and only
        change when a build tool rewrites them."""
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        if cache_seconds:
            self.send_header("Cache-Control", f"public, max-age={cache_seconds}")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        # Lighthouse flagged robots.txt as invalid because the 404 page was
        # being parsed as one. This app is a personal tool and has nothing to
        # index, so say so explicitly rather than leaving a 404 to be read.
        if self.path == "/robots.txt":
            return self._send_text("User-agent: *\nDisallow: /\n",
                                   "text/plain; charset=utf-8")
        if self.path.startswith("/fonts/"):
            # The two faces the page is set in. Whitelisted by name: a static
            # path handler is the one place a traversal could be typed in.
            name = self.path[len("/fonts/"):]
            if not re.fullmatch(r"[a-z0-9-]+\.woff2", name):
                return self._send_text("not found", "text/plain; charset=utf-8",
                                       status=404)
            path = ROOT / "fonts" / name
            if not path.exists():
                return self._send_text("not found", "text/plain; charset=utf-8",
                                       status=404)
            body = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "font/woff2")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "public, max-age=31536000, immutable")
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path.startswith("/nlp/"):
            # The bundled grammar engine. It is served from a whitelisted name
            # for the same reason the fonts are: this is the one place a path
            # could be typed in, and the file is 3.5 MB of local model data
            # that must travel with the app rather than be fetched from
            # anywhere else. The APK carries the identical file.
            name = self.path[len("/nlp/"):]
            if not re.fullmatch(r"[a-z0-9-]+\.js", name):
                return self._send_text("not found", "text/plain; charset=utf-8",
                                       status=404)
            path = ROOT / "nlp" / name
            if not path.exists():
                return self._send_text("not found", "text/plain; charset=utf-8",
                                       status=404)
            body = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/javascript; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "public, max-age=31536000, immutable")
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path.startswith("/brand/"):
            # The mascot. Whitelisted by name for the same reason the fonts are:
            # this is the one place a path could be typed in, and the APK
            # carries the identical files.
            name = self.path[len("/brand/"):]
            if not re.fullmatch(r"[a-z0-9-]+\.png", name):
                return self._send_text("not found", "text/plain; charset=utf-8",
                                       status=404)
            path = ROOT / "brand" / name
            if not path.exists():
                return self._send_text("not found", "text/plain; charset=utf-8",
                                       status=404)
            body = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "public, max-age=604800")
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path.startswith("/api/wordarch"):
            # Word architecture: for every vocabulary word, its verified form
            # family. The Sentences panel groups these under each CEFR level.
            arch = json.loads(
                (ROOT / "word_arch.json").read_text(encoding="utf-8"))["words"]
            bands: dict[str, list] = {}
            for word, entry in arch.items():
                bands.setdefault(entry.get("level", "A1"), []).append(entry)
            for items in bands.values():
                items.sort(key=lambda e: e["en"].lower())
            body = json.dumps(bands, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path.startswith("/api/phonetics"):
            # Phonetics sections for the 🗣 panel — straight from the JSON,
            # so adding a topic only ever means editing phonetics.json
            data = json.loads((ROOT / "phonetics.json").read_text(encoding="utf-8"))
            sections = [{
                "id": s["id"],
                "icon": s.get("icon", "🔊"),
                "level": s.get("level", "A1"),
                "title_en": s["title"]["en"],
                "title_fa": s["title"]["fa"],
                "blurb_en": s["blurb"]["en"],
                "tip_en": s.get("tip", {}).get("en", ""),
                "groups": [{
                    "name_en": g["name"]["en"],
                    "rows": g.get("rows", []),
                } for g in s.get("groups", [])],
            } for s in data["sections"]]
            body = json.dumps(sections, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path.startswith("/api/collocations"):
            # word partners for the practice sheet. Curated, not generated, so
            # it is served as it is written - and cached hard, because it only
            # changes when a person edits the file.
            body = (ROOT / "collocations.json").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "public, max-age=3600")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path.startswith("/api/register"):
            # the register bank the register drill reads. Same file the chat
            # answers from, so the drill cannot teach a different formality
            # than the chat does.
            body = (ROOT / "register.json").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "public, max-age=3600")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path.startswith("/api/stt"):
            # the speech-to-text configuration, read by the page and by the
            # CLI, so the three surfaces cannot drift apart
            self._send_json(stt_config())
        elif self.path.startswith("/api/bbc"):
            # the graded BBC 6 Minute English catalogue (links only - no media)
            self._send_json(bbc_catalogue(), 300)
        elif self.path.startswith("/api/listening"):
            # CEFR A1-C2 listening sentences for the 🎧 panel
            levels = [{
                "id": lv["id"],
                "title_en": lv["title"]["en"],
                "title_fa": lv["title"]["fa"],
                "blurb_en": lv["blurb"]["en"],
                "blurb_fa": lv["blurb"]["fa"],
                "sentences": lv["sentences"],
            } for lv in bot.listening]
            body = json.dumps(levels, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path.startswith("/api/emojis"):
            # The composer's emoji picker. The offline bundle reads this same
            # file as data/emojis.json; here it needs a route, because the web
            # build has no data/ directory to fetch from.
            self._send_json(json.loads((ROOT / "emojis.json").read_text(encoding="utf-8")),
                            3600)
        elif self.path.startswith("/api/books"):
            # The library: books, their lessons, and each lesson's words with a
            # Persian meaning, a definition and examples. Served off disk
            # rather than through the bot - it is content the page draws - and
            # the offline APK reads the same file out of assets/www/data, so the
            # two cannot drift apart about what a word means.
            body = (ROOT / "books.json").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path.startswith("/api/reading"):
            # The Reading panel's six strategies, straight off disk: the
            # passages and their answer keys are content the page draws, not
            # something the bot has an opinion about. The offline APK carries
            # the same file in assets/www/data/reading.json.
            body = (ROOT / "reading.json").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path.startswith("/api/stories"):
            # Mini stories: the English story, the Persian beside each
            # sentence, the notes and the answer keys. Content, not chat, so
            # it is read off disk; the offline APK carries the same file.
            body = (ROOT / "stories.json").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path.startswith("/api/level_test"):
            # The monthly level check: a banded item bank marked in the page.
            # Content, not chat, so it is read off disk like the stories, and
            # the offline APK carries the same file.
            body = (ROOT / "level_test.json").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path.startswith("/api/path"):
            # The learning path: seven level spaces, the A1 course and its
            # examination paper. Content, so it is read off disk and the
            # offline APK carries the same file.
            body = (ROOT / "path.json").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path.startswith("/api/vocabulary"):
            # Vocabulary domains for the UI panel, grouped for a tidy layout
            groups = []
            for g in bot.glossary_groups:
                items = []
                for dom_id in g["domains"]:
                    d = bot.glossary[dom_id]
                    items.append({
                        "title_en": d["list_label"]["en"],
                        "title_fa": d["list_label"]["fa"],
                        "query_en": d["keywords"]["en"][0],
                        "query_fa": d["keywords"]["fa"][0],
                        "count": len(d["words"]),
                        "level": d.get("level", "A1"),
                        "id": dom_id,
                    })
                groups.append({"en": g["en"], "fa": g["fa"], "items": items})
            body = json.dumps(groups, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path.startswith("/api/phrases"):
            # Practical sentence topics for the footer
            topics = []
            for t in bot.phrases.values():
                topics.append({
                    "title_en": t["title"]["en"],
                    "title_fa": t["title"]["fa"],
                    "query": t["keywords"]["en"][0],
                    "count": len(t["phrases"]),
                    "level": t.get("level", "A1"),
                })
            body = json.dumps(topics, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path.startswith("/api/grammar"):
            # Grammar topics for the UI panel (bilingual)
            topics = []
            for t_id, t in bot.grammar.items():
                topics.append({
                    "title_en": t["title"]["en"],
                    "title_fa": t["title"]["fa"],
                    "query_en": t["keywords"]["en"][0],
                    "query_fa": t["keywords"]["fa"][0],
                    "practice_en": f"{t['keywords']['en'][0]} exercises",
                    "practice_fa": f"تمرین {t['keywords']['fa'][0]}",
                    "exam_en": f"{t['keywords']['en'][0]} exam",
                    "exam_fa": f"آزمون {t['keywords']['fa'][0]}",
                    "practice_n": len(t.get("practice", [])),
                    "exam_n": len(t.get("exam", [])),
                    "unlocked": t_id in bot.practice_done,
                    "level": t.get("level", ""),
                })
            body = json.dumps(topics, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path.startswith("/api/daily"):
            # Daily English: the whole curated catalogue. Which three items a
            # given day gets is a function of the local date, and the page
            # works it out itself - the same arithmetic runs in the APK with no
            # server at all, so keeping the choice out of here is what makes
            # the two agree.
            body = json.dumps(bot.daily, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path.startswith("/api/foxes"):
            # The composer's fox stickers. Pure content that the page draws,
            # so it is served straight off disk rather than through the bot.
            body = (ROOT / "foxes.json").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path.startswith("/api/correct"):
            # GEC-BART Base answers here and the page only draws the result. A
            # model that is missing or unwell is a JSON refusal, not a
            # traceback: the page has to be able to say why it got nothing.
            query = parse_qs(urlparse(self.path).query)
            message = query.get("message", [""])[0]
            try:
                row = gec.correct(message)
            except Exception as exc:   # one bad sentence must not end the server
                row = {"available": False, "input": message, "output": "",
                       "changed": False,
                       "refused": f"The correction model failed: {exc}"}
            body = json.dumps(row, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path.startswith("/api/chat"):
            query = parse_qs(urlparse(self.path).query)
            message = query.get("message", [""])[0]
            reply = bot.respond(message)
            body = json.dumps({"reply": reply}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            body = render_page().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def log_message(self, *args):
        pass  # quiet


if __name__ == "__main__":
    # Fetch the checkpoint before anyone asks for a correction. With storage
    # keys and an empty disk this is what makes a fresh server work without the
    # model ever being committed, bundled, or copied here by hand.
    gec.prefetch()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Chatbot preview running at http://localhost:{PORT}")
    server.serve_forever()
