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
  /* Gulzar (googlefonts/Gulzar, OFL) is the Persian face of the whole app. It
     is a Nastaliq, so it sits deeper than a naskh face and the Persian surfaces
     carry the line height to match (below). The unicode-range keeps it to the
     Arabic script, so Latin stays in Baloo2/Kalam and a mixed line keeps two
     voices on purpose. */
  @font-face {
    font-family: 'Gulzar';
    font-style: normal;
    font-weight: 400;
    font-display: swap;
    src: url('fonts/gulzar.woff2') format('woff2');
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
    --ink: #2b3049; --navy: #3c405b; --navy2: #2a2d45;
    --gold: #e8bf5f; --gold2: #cf9f3c; --gold-soft: #f7e6bd;
    /* the poster's first band, as a surface rather than an accent */
    --sand: #ebe2b7; --sand2: #ddd2a2;
    /* the poster's water: the cool note the lavender chip used to carry */
    --ice: #e4ecf3; --ice2: #d4e1ed; --ice-ink: #33526e;
    --success: #4a4fa0; --red: #a8493a;
    /* Kalam is the handwritten body face of the reference; Baloo 2 the
       rounded display face of its headings. Tahoma carries the Persian. */
    --font-body: 'Gulzar', 'Kalam', 'Segoe Print', 'Comic Sans MS', Tahoma, 'Vazirmatn', 'IranSans', sans-serif;
    --font-fa: 'Gulzar', Tahoma, 'Vazirmatn', 'IranSans', sans-serif;
    --font-display: 'Gulzar', 'Baloo2', 'Trebuchet MS', Tahoma, 'Vazirmatn', 'IranSans',
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
    --line: rgba(43,48,73,0.136);
    --line2: rgba(43,48,73,0.238);
    --shadow: 0 40px 100px rgba(74,58,30, .7);
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
    background:
      radial-gradient(58% 52% at 12% 4%, rgba(232,191,95,.20), transparent 72%),
      radial-gradient(52% 48% at 90% 2%, rgba(150,175,200,.38), transparent 72%),
      radial-gradient(56% 50% at 84% 96%, rgba(235,226,183,.9), transparent 74%),
      linear-gradient(165deg, #fbf6e7 0%, #f7f0dc 55%, #f1e7cf 100%);
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
    background:
      radial-gradient(95% 70% at 50% -10%, #fdf9f0 0%, transparent 62%),
      radial-gradient(80% 60% at 108% 108%, #f6ecda 0%, transparent 58%),
      linear-gradient(158deg, #fbf6ec 0%, #f5ecda 52%, #efe5cd 100%);
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

  .boot-in {
    position: relative; width: min(100%, 384px);
    display: grid; justify-items: center; gap: 18px;
    padding: 34px 28px 24px;
    border-radius: 30px;
    background: linear-gradient(160deg, #fffdf4, #fbf3df);
    border: 1px solid rgba(205,159,60,.28);
    box-shadow:
      0 34px 80px rgba(74,58,30,.18),
      0 2px 0 rgba(255,255,255,.9) inset;
    animation: bootCardIn .72s cubic-bezier(.22,1,.36,1) both;
  }
  @keyframes bootCardIn {
    from { opacity: 0; transform: translateY(14px) scale(.975); }
    to   { opacity: 1; transform: none; }
  }

  /* The mark: the mascot inside a slowly turning gradient ring, with a soft
     inner well so the bird reads against the card rather than floating. */
  .boot-mark {
    position: relative; width: 108px; height: 108px;
    display: grid; place-items: center;
  }
  .boot-halo {
    position: absolute; inset: 0; border-radius: 50%;
    background: conic-gradient(from 0deg,
      #3c405b, #e8bf5f, #d4e1ed, #3c405b, #8a5a00, #3c405b);
    opacity: .95;
    box-shadow: 0 0 42px rgba(232,191,95,.38), 0 0 80px rgba(60,64,91,.12);
    animation: bootSpin 7s linear infinite;
  }
  .boot-halo::after {
    content: ''; position: absolute; inset: 4px; border-radius: 50%;
    background: radial-gradient(circle at 32% 24%, #fffdf4, #f4ebd2 72%);
    box-shadow: 0 1px 0 rgba(255,255,255,.9) inset;
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
    width: 86px; height: 86px; display: block;
    filter: drop-shadow(0 7px 12px rgba(74,58,30,.30));
  }
  @keyframes bootBob {
    0%, 100% { transform: translateY(0) rotate(-1.5deg); }
    50%      { transform: translateY(-6px) rotate(1.5deg); }
  }

  .boot-brand { display: grid; justify-items: center; gap: 5px; text-align: center; }
  .boot-name {
    font-size: 29px; font-weight: 700; letter-spacing: -.6px;
    line-height: 1.05;
    background: linear-gradient(102deg, #2b3049 8%, #3c405b 58%, #b8872a 96%);
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
    display: block; margin-top: 2px; color: #8a5a00; font-style: normal;
    font-family: var(--font-fa); direction: rtl; unicode-bidi: isolate;
    font-size: 12px; line-height: 1.95;
  }

  /* A bouncing tile with its shadow on the floor. The shape is borrowed from
     a well-known loading animation; the colour is the tutor's. Transform
     only, so it stays on the compositor. */
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
    background: linear-gradient(140deg, #e8bf5f, #cf9f3c);
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
    height: 5px; border-radius: 999px;
    background: rgba(43,48,73,.14); overflow: hidden;
    box-shadow: 0 1px 0 rgba(43,48,73,.06) inset;
  }
  /* No transition here: the bar is repainted from the one eased ratio every
     frame (see Boot), and a transition on top of that would put the bar and
     the percentage back on two different clocks. */
  .boot-track i {
    display: block; width: 100%; height: 100%; border-radius: inherit;
    background: linear-gradient(90deg, #3c405b, #8a5a00 55%, #e8bf5f 100%);
    box-shadow: 0 0 12px rgba(232,191,95,.55);
    transform: scaleX(0); transform-origin: 0 50%;
  }
  .boot-meta {
    width: 100%; display: flex; justify-content: flex-end;
    margin-top: -6px;
    font-size: 11.5px; color: var(--muted);
  }
  .boot-meta #bootpct {
    flex: none; color: #8a5a00; font-weight: 700;
    font-variant-numeric: tabular-nums;
  }

  @media (prefers-reduced-motion: reduce) {
    .boot { transition: none; }
    .boot-in { animation: none; }
    .boot-aurora i, .boot-halo { animation: none; }
    .boot-fox-bob { animation: none; }
    .loader::before, .loader::after { animation: none; }
    .boot-track i { transition: none; }
  }

  /* ---- the emoji picker ---- */
  .emoji-panel {
    margin: 0 0 6px;
    border-radius: 16px; overflow: hidden;
    background: #fffcef;
    border: 1px solid rgba(43,48,73,.14);
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
    background: rgba(43,48,73,0.034); color: var(--text);
    padding: 11px 14px; font-size: 14px; font-family: inherit;
    outline: none;
  }
  .esearch::placeholder { color: #7c8496; }
  .esearch::-webkit-search-cancel-button { filter: invert(.7); }
  .ebody {
    max-height: 46vh; overflow-y: auto;
    padding: 8px 10px 10px;
    overscroll-behavior: contain;
  }
  .ebody::-webkit-scrollbar { width: 7px; }
  .ebody::-webkit-scrollbar-thumb { background: #dccfb4; border-radius: 6px; }
  .ehead {
    font-size: 10px; letter-spacing: .09em; text-transform: uppercase;
    color: var(--dim); font-weight: 700;
    padding: 9px 2px 5px; position: sticky; top: -8px;
    background: linear-gradient(180deg, #fffdf4, #fdf8ea);
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
  .stile:hover { background: rgba(43,48,73,0.07); transform: scale(1.1); }
  .stile:active { transform: scale(.92); }
  .stile:focus-visible { outline: 2px solid #3c405b; outline-offset: 1px; }
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
    -webkit-mask-image: radial-gradient(closest-side, #000 0%, #000 34%, rgba(74,58,30,.45) 58%, transparent 80%);
    mask-image: radial-gradient(closest-side, #000 0%, #000 34%, rgba(74,58,30,.45) 58%, transparent 80%);
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
    background: linear-gradient(180deg, rgba(43,48,73,0.068), rgba(43,48,73,0.0255));
    border: 1px solid rgba(43,48,73,0.111);
    box-shadow: inset 0 1px 0 rgba(43,48,73,0.136), 0 10px 28px rgba(74,58,30,.34);
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
    border-radius: 50%; border: 1px solid rgba(43,48,73,0.119);
    background: linear-gradient(180deg, rgba(43,48,73,0.111), rgba(43,48,73,0.0425));
    color: var(--ink); cursor: pointer; padding: 0;
    transition: transform .16s cubic-bezier(.22,1,.36,1), background .16s;
  }
  .plbtn:hover { background: linear-gradient(180deg, rgba(43,48,73,0.17), rgba(43,48,73,0.068)); }
  .plbtn:active { transform: scale(.93); }
  .plbtn svg { width: 18px; height: 18px; fill: currentColor; }
  .plbtn:focus-visible { outline: 2px solid #3c405b; outline-offset: 2px; }
  .plbtn.ghost { width: 32px; height: 32px; color: var(--muted); }
  .plbtn.ghost svg { width: 14px; height: 14px; }
  .plbody { flex: 1 1 auto; min-width: 0; }
  .plhead { display: flex; align-items: baseline; gap: 8px; min-width: 0; }
  .plkind {
    flex: 0 0 auto; font-size: 10px; letter-spacing: .09em; text-transform: uppercase;
    color: #8a5a00; font-weight: 700;
  }
  .pltitle {
    font-size: 13px; color: var(--ink); white-space: nowrap;
    overflow: hidden; text-overflow: ellipsis; min-width: 0;
  }
  .pltrack {
    position: relative; height: 6px; margin-top: 6px; border-radius: 99px;
    background: rgba(43,48,73,0.102); cursor: pointer;
    touch-action: none; overflow: hidden;
  }
  .pltrack:focus-visible { outline: 2px solid #3c405b; outline-offset: 3px; }
  .pltrack i {
    position: absolute; inset: 0 auto 0 0; width: 0%; border-radius: 99px;
    background: linear-gradient(90deg, #3c405b, #424765);
  }
  /* Speech has no duration to scrub, so the bar breathes instead of lying
     about a position. */
  .player.speech .pltrack i {
    width: 100% !important;
    background: linear-gradient(90deg, transparent, #cf9f3c 40%, #cf9f3c 60%, transparent);
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
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 10px; flex: none;
  }
  /* The titles are bilingual and can be long. Without min-width: 0 the h3
     refuses to shrink below its content and pushes the close button past the
     edge of the panel on a narrow phone. */
  .phead h3 { min-width: 0; overflow-wrap: anywhere; }
  .phead h3 { flex: 1 1 auto; margin: 0; min-width: 0; }
  .pclose {
    /* 40px, not 44. A panel header is a title and one button, and at 44 the
       button was the loudest thing in it - it took more width than the close
       icon needs and left the bilingual titles with less room than they have
       lines. 40 is still a comfortable thumb target and still clears --tap
       once its own padding is counted. */
    flex: 0 0 40px; width: 40px; height: 40px; border-radius: 12px;
    display: grid; place-items: center; cursor: pointer;
    background: var(--ice); border: 1px solid rgba(51,82,110,.22); color: var(--ice-ink);
    font-size: 17px; line-height: 1;
    transition: background .16s, border-color .16s, transform .14s;
  }
  .pclose:hover { background: var(--navy); border-color: var(--navy); color: #fffcef; }
  .pclose:focus-visible { outline: 2px solid #3c405b; outline-offset: 2px; }
  .pclose:active { transform: scale(.93); }
  .pclose svg { width: 15px; height: 15px; display: block; }

  /* the search box every panel now shares */
  .psearch { margin-bottom: 10px; flex: none; }
  .psearch input {
    width: 100%; padding: 8px 13px; border-radius: 12px;
    background: #fffdf4; border: 1px solid rgba(43,48,73,.16); color: var(--text);
    font-size: 14px; font-family: inherit; outline: none;
  }
  .psearch input::placeholder { color: #7c8496; }
  .psearch input:focus {
    border-color: #3c405b;
    box-shadow: 0 0 0 3px rgba(60,64,91, .18);
  }

  /* the one empty state, used by every panel */
  .pempty {
    padding: 26px 18px; text-align: center; line-height: 1.7;
    color: var(--muted); font-size: 13.5px;
    background: #fdf8ea; border: 1px dashed rgba(43,48,73,.18); border-radius: 14px;
  }
  .pempty b { color: #2b3049; }

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
  #vpanel, #gpanel, #fpanel, #lpanel, #phpanel, #rpanel, #dpanel, #npanel, #bpanel {
    box-shadow: inset 0 -16px 16px -16px rgba(74,58,30,.62);
  }

  /* "Show more" for the 1126-episode BBC list */
  .bbc-more {
    display: block; width: 100%; margin-top: 10px; padding: 11px 14px;
    border-radius: 12px; cursor: pointer; font-family: inherit;
    font-size: 12.5px; color: #4a5170;
    background: rgba(60,64,91,.13); border: 1px solid rgba(60,64,91,.3);
    transition: background .16s, border-color .16s;
  }
  .bbc-more:hover { background: rgba(60,64,91,.22); border-color: #3c405b; }
  .bbc-more:focus-visible { outline: 2px solid #3c405b; outline-offset: 2px; }

  /* ---- the app is a pane of frosted glass ---- */
  .app {
    position: relative; z-index: 1;
    width: min(1180px, 100%); height: min(94vh, 980px);
    display: flex; flex-direction: column; overflow: hidden;
    border-radius: 26px;
    background:
      linear-gradient(150deg, #fffdf4, #fffcef 45%, #fbf4e1);
    border: 1px solid rgba(205,159,60,.30);
    box-shadow:
      0 30px 70px rgba(74,58,30,.16),
      0 1px 0 #ffffff inset;
  }
  /* thicker, brighter edge at the bottom = sense of glass depth */
  .app::after {
    content: ''; position: absolute; left: 12%; right: 12%; bottom: 0; height: 3px;
    background: linear-gradient(90deg, transparent, rgba(43,48,73,.10), transparent);
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
    background: linear-gradient(180deg, #fdf8e7 0%, #f8f0d8 100%);
    border-bottom: 1px solid rgba(205,159,60,.32);
    flex: none;
  }
  /* the frosted layer belonged to the glass theme; paper needs no refraction */
  .hb { display: none; }
  /* The portrait sits on the header's own sand rather than in a badge. A ring
     plus a border plus a drop shadow made it look pasted on: three edges for
     one circular picture. What is left is the paper it is printed on. */
  .avatar {
    width: 46px; height: 46px; border-radius: 15px; flex: none;
    background: #fbf3dd;
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
    background: linear-gradient(150deg, #f7e6bd, #ecd39a);
    box-shadow: 0 0 0 2px rgba(207,159,60,.5);
  }

  /* daily seed meter */
  #seedmeter {
    position: relative; flex: none; width: 66px; height: 20px; border-radius: 999px;
    background: rgba(43,48,73,.08); border: 1px solid rgba(43,48,73,.14);
    overflow: hidden; display: flex; align-items: center; justify-content: flex-end;
  }
  #seedmeter i {
    position: absolute; inset: 0 auto 0 0; border-radius: 999px;
    background: linear-gradient(90deg, #cf9f3c, #e8bf5f 70%, #f2e2b4);
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
    font-size: 11.5px; color: #4a4fa0;
    padding: 4px 2px; font-weight: 600;
  }
  .status i { width: 8px; height: 8px; border-radius: 50%; background: #4a4fa0;
              box-shadow: 0 0 8px #4a4fa0; animation: pulse 1.6s infinite; display: inline-block; }
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
    background: #fffcef;
    color: var(--ink);
    border: 1px solid rgba(43,48,73,.10); border-radius: 13px;
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
  .hbtn span {
    font-size: 8.5px; font-weight: 700; letter-spacing: -.05px;
    line-height: 1; color: var(--muted); max-width: 100%;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }
  .hbtn:hover {
    background: #fbf4e1; border-color: rgba(205,159,60,.42);
    transform: translateY(-1px);
    box-shadow: 0 6px 14px rgba(74,58,30,.12);
  }
  .hbtn.on {
    background: linear-gradient(150deg, #464b69, #3c405b 60%, #2a2d45);
    border-color: transparent;
    box-shadow: 0 6px 16px rgba(60,64,91,.26), inset 0 1px 0 rgba(255,255,255,.12);
  }
  .hbtn.on i, .hbtn.on span { color: #fffcef; }
  .hbtn.on i svg { stroke-width: 1.85; }
  .hbtn:focus-visible {
    outline: 2px solid #3c405b;
    outline-offset: 2px;
    box-shadow: 0 0 0 4px rgba(232,191,95,.45);
  }
  .hbtn.danger { color: var(--red); }
  .hbtn.danger:hover {
    border-color: rgba(168,73,58,.45);
    background: #fdf1ee;
  }

  /* ---------- vocabulary / grammar / phrases panels ----------
     Every panel is here, and every panel must be: #dpanel and #npanel were
     added to the markup without being added to this rule, so they had no
     display:none at all and simply sat in the flow. The Today panel is 2400px
     of cards on an 844px phone, which left #chat sixteen pixels tall - the
     daily feature did not sit beside the conversation, it was the page.
     tools/check_ui.py now derives the list from the markup and fails on any
     panel that is missing here. */
  #vpanel, #gpanel, #fpanel, #lpanel, #phpanel, #rpanel, #dpanel, #npanel, #bpanel {
    display: none; padding: 14px 20px;
    background: #fffcef;
    border-bottom: 1px solid rgba(43,48,73,.12);
    flex: none; animation: fade .18s ease;
    max-height: 52%; overflow-y: auto;
    /* fade the bottom edge so it reads as scrollable rather than clipped */
    -webkit-mask-image: linear-gradient(to bottom, #000 calc(100% - 22px), transparent);
    mask-image: linear-gradient(to bottom, #000 calc(100% - 22px), transparent);
  }
  #vpanel.open, #gpanel.open, #fpanel.open, #lpanel.open,
  #dpanel.open, #npanel.open, #bpanel.open { display: block; }
  /* #phpanel gets its own flex layout below, so it is not listed here */
  @keyframes fade { from { opacity: 0; transform: translateY(-4px); } }
  #vpanel h3, #gpanel h3, #fpanel h3, #lpanel h3, #phpanel h3, #rpanel h3,
  #bpanel h3 {
    font-size: 13px; color: var(--ink); margin-bottom: 9px; font-weight: 700;
    font-family: var(--font-display); letter-spacing: .1px;
  }
  /* A coloured rule per section. Only one panel is ever open, so this is a
     wayfinding cue rather than a palette to look at - it tells you where you
     are before you have read a word. */
  #vpanel h3  { border-inline-start: 3px solid var(--teal);    padding-inline-start: 9px; }
  #gpanel h3  { border-inline-start: 3px solid var(--violet);  padding-inline-start: 9px; }
  #fpanel h3  { border-inline-start: 3px solid var(--rose);    padding-inline-start: 9px; }
  #lpanel h3  { border-inline-start: 3px solid var(--cyan);    padding-inline-start: 9px; }
  #phpanel h3 { border-inline-start: 3px solid var(--indigo); padding-inline-start: 9px; }
  #bpanel h3 { border-inline-start: 3px solid var(--navy);   padding-inline-start: 9px; }
  #rpanel h3  { border-inline-start: 3px solid var(--amber);   padding-inline-start: 9px; }

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
    background: var(--navy); color: #fffcef;
    border-color: transparent; box-shadow: 0 3px 10px rgba(43,48,73,.2);
  }
  .llist { display: flex; flex-direction: column; gap: 4px; }
  .lrow {
    display: flex; align-items: center; gap: 10px;
    background: #fdf8ea; border: 1px solid rgba(43,48,73,.10);
    border-radius: 10px; padding: 7px 11px; transition: .12s;
  }
  .lrow:hover { background: #f9f1e2; border-color: rgba(43,48,73,.2); }
  .lrow.playing {
    background: var(--ice); border-color: rgba(51,82,110,.4);
  }
  .lplay {
    width: 28px; height: 28px; flex: none; border-radius: 50%;
    background: var(--navy); border: none;
    color: #fffcef; font-size: 12px; cursor: pointer;
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
    color: #555a78; margin-bottom: 5px; font-weight: 600;
  }
  .vgroup-head .fa { color: var(--dim); text-transform: none; letter-spacing: 0; font-weight: 400; }
  .vgroup-head .count {
    background: rgba(43,48,73,0.0595); border-radius: 999px;
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
    background: rgba(43,48,73,0.085); border-radius: 4px;
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
    margin-top: 10px; border: 1px solid rgba(43,48,73,0.17);
    border-radius: 14px; overflow: hidden;
    background: linear-gradient(180deg, rgba(255,255,255,.55), rgba(255,252,239,.34));
    box-shadow: 0 1px 2px rgba(43,48,73,.05);
  }
  .gsec {
    margin: 0; border: 0; border-radius: 0;
    background: transparent; box-shadow: none;
  }
  .gsec + .gsec {
    border-top: 1px solid rgba(43,48,73,0.135);
  }
  .gsec-h {
    display: flex; align-items: center; gap: 7px;
    padding: 6px 11px 6px 10px;
    font-family: var(--font-display); font-size: 12.5px; font-weight: 700;
    letter-spacing: .015em; color: var(--navy);
    background: rgba(43,48,73,0.038);
    border-bottom: 1px solid rgba(43,48,73,0.105);
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
  /* Gulzar is the Persian face wherever Persian appears: the language the
     renderer writes on a line, the islands it emits inside an English one, the
     translation lines, and any element the app marks as Persian. A font stack
     is easy to override by accident; naming the surfaces it applies to is not. */
  [lang="fa"], .fa, .dfa, .bl[dir="rtl"], .dline.fa, .msg.rtl, .gsec-b bdi.fa {
    font-family: var(--font-fa);
  }
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
  .gsec[data-kind="exercises"]   .gsec-h { border-inline-start-color: var(--slate-rail, #3c405b); }
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
    background: rgba(43,48,73,0.051); border: 1px solid rgba(43,48,73,0.119);
  }
  .psearch input:focus {
    border-color: rgba(60,64,91,.7); background: rgba(43,48,73,0.0765);
    box-shadow: 0 0 0 3px rgba(60,64,91,.16);
  }
  .psearch input::placeholder { color: #7c8496; }
  .pempty { font-size: 12.5px; color: var(--muted); padding: 10px 2px; }
  .ftopic .n {
    background: rgba(43,48,73,0.085); border-radius: 5px;
    padding: 0 5px; font-size: 10px; color: var(--muted);
  }
  .glevel-head b { color: var(--ink); font-weight: 700; }
  .glevel-head .count {
    background: rgba(43,48,73,0.0595); border-radius: 999px;
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
    background: rgba(232,191,95,.34); color: #7a5000;
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
  .bbook {
    display: grid; gap: 2px; width: 100%; text-align: start; cursor: pointer;
    font-family: inherit; color: var(--ink);
    background: #fffcef; border: 1px solid rgba(43,48,73,.13);
    border-radius: 12px; padding: 9px 11px 10px;
    border-inline-start: 3px solid var(--navy); transition: .15s;
  }
  .bbook:hover { transform: translateY(-1px); border-color: rgba(60,64,91,.42); }
  .bbook b { font-size: 13.5px; font-weight: 700; }
  .bbook .bfa { font-size: 12px; color: #3f4a6b; line-height: 1.9; }
  .bbook .bmeta { font-size: 10.5px; color: var(--muted); }
  .bback {
    display: inline-flex; align-items: center; gap: 5px;
    background: none; border: none; cursor: pointer; font-family: inherit;
    color: #4a4fa0; font-size: 11.5px; font-weight: 700; padding: 0 0 7px;
  }
  .bback:hover { text-decoration: underline; }
  .bhead2 { font-size: 12px; font-weight: 700; color: var(--ink); padding-bottom: 6px; }
  .blesson {
    display: flex; align-items: center; gap: 8px; width: 100%;
    font-family: inherit; cursor: pointer; text-align: start;
    background: #fffcef; border: 1px solid rgba(43,48,73,.13);
    border-radius: 10px; padding: 8px 11px; color: var(--ink);
  }
  .blesson:hover { border-color: rgba(60,64,91,.42); }
  .blesson .bn { font-size: 12.5px; font-weight: 700; }
  .blesson .bfa { font-size: 11.5px; color: var(--muted); }
  .blesson .n {
    margin-inline-start: auto; font-size: 10px; color: var(--muted);
    background: rgba(43,48,73,.085); border-radius: 5px; padding: 0 5px;
  }
  .bwords { display: flex; flex-direction: column; gap: 8px; }
  .bword {
    background: #fffcef; border: 1px solid rgba(43,48,73,.11);
    border-radius: 12px; padding: 9px 11px 10px;
    border-inline-start: 3px solid var(--teal);
  }
  .bwh { display: flex; align-items: baseline; gap: 6px; flex-wrap: wrap; }
  .bwh b { font-size: 15px; }
  .bwh .ipa { font-size: 11px; color: var(--muted); }
  .bwh .pos {
    font-size: 9.5px; font-style: normal; color: #4a4fa0;
    background: rgba(79,70,160,.10); border-radius: 5px; padding: 1px 6px;
  }
  .bwh .bsay {
    margin-inline-start: auto; background: none; cursor: pointer;
    border: 1px solid rgba(43,48,73,.16); border-radius: 8px;
    font-size: 11px; line-height: 1; padding: 4px 6px; color: var(--ink);
  }
  .bwh .bsay:hover { background: rgba(43,48,73,.07); }
  .bword .bfa { font-size: 12.5px; color: #3f4a6b; margin-top: 3px; line-height: 1.95; }
  .bword .bdef { font-size: 12px; color: var(--ink); margin-top: 3px; }
  .bex { margin: 5px 0 0; padding: 0; list-style: none; }
  .bex li {
    display: flex; gap: 6px; align-items: baseline;
    font-size: 11.5px; color: #3f4a6b;
    padding: 2px 0 2px 9px; border-inline-start: 2px solid #e6dcc4;
  }
  .bex li button {
    flex: none; background: none; border: none; cursor: pointer;
    color: #4a4fa0; font-size: 10px; padding: 0; font-family: inherit;
  }

  /* ---------- chat area ---------- */
  #chat {
    flex: 1; overflow-y: auto; padding: 22px 22px 10px;
    display: flex; flex-direction: column; gap: 16px;
    /* The transcript is its own sheet, a shade deeper than the card it sits
       in: without it the header, the conversation and the composer were one
       unbroken field of cream with three horizontal rules in it. */
    background: #faf4e2;
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
    background: #dccfb4; border-radius: 8px;
  }
  #chat::-webkit-scrollbar-track { background: transparent; }
  .row { display: flex; gap: 10px; align-items: flex-end; animation: pop .2s ease; }
  @keyframes pop { from { opacity: 0; transform: translateY(8px); } }
  .row.user { flex-direction: row-reverse; }
  .mav {
    width: 32px; height: 32px; border-radius: 11px; flex: none;
    display: grid; place-items: center; font-size: 16px;
    background: rgba(43,48,73,0.0595); border: 1px solid rgba(43,48,73,0.119);
  }
  .mav svg, .mav img { width: 26px; height: 26px; display: block; }
  /* the tutor's face is a round portrait, so the tile reads as a frame */
  .mav img { border-radius: 50%; }
  .mav.bot {
    background: linear-gradient(150deg, rgba(235,226,183,.95), rgba(221,210,162,.9));
    border-color: rgba(205,159,60,.38);
    /* The tutor's portrait is round, so its tile is too: a circle sitting in a
       rounded square reads as a picture that missed its frame. The picture
       fills the tile, so the gold edge is the only frame it gets. */
    border-radius: 50%;
  }
  .mav.bot img { width: 100%; height: 100%; }
  .mav.me {
    background: linear-gradient(150deg, rgba(233,229,248,.9), rgba(43,48,73,.06));
    border-color: rgba(51,82,110,.28);
  }
  /* One rule, not three. The two lavender ones above were dead - a later rule
     with the same selector always won - and the shadow that survived was the
     old indigo rgba(79,110,247): a blue glow on the calmer, warmer page. */
  .row.user .mav {
    background: linear-gradient(135deg, var(--user1), var(--user2));
    border: none; box-shadow: 0 4px 12px rgba(43,48,73,.22);
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
    background: #fffcef;
    color: var(--ink);
    border: 1px solid rgba(43,48,73,.13);
    border-bottom-left-radius: 6px;
    box-shadow: 0 4px 16px rgba(74,58,30,.09), inset 0 1px 0 #ffffff;
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
    color: #8a5a00; font-weight: 700;
    background: rgba(232,191,95,.34);
    border-radius: 5px; padding: 0 4px; margin: 0 -1px;
    box-shadow: inset 0 0 0 1px rgba(207,159,60,.45);
  }
  .msg.user b, .msg.user strong {
    color: #fff6e2; background: rgba(255,255,255,.16);
    box-shadow: inset 0 0 0 1px rgba(255,255,255,.22);
  }
  .msg.user {
    background: linear-gradient(135deg, var(--user1) 0%, var(--user2) 55%,
                                        var(--user3) 100%);
    color: #fdf7ea; border: none; border-bottom-right-radius: 6px;
    box-shadow: 0 6px 18px rgba(43,48,73,.24), inset 0 1px 0 rgba(255,255,255,.14);
  }
  .msg.rtl { direction: rtl; text-align: right; }
  /* mixed bilingual text: each line picks its own direction */
  .msg { unicode-bidi: plaintext; text-align: start; }
  .msg b, .msg strong { color: #8a5a00; font-weight: 700; }
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
  .mtool:hover { color: var(--text); background: rgba(43,48,73,0.0765);
                 border-color: rgba(43,48,73,0.119); }
  @media (hover: none) {
    .mtool:hover { background: none; color: var(--dim); border-color: transparent; }
  }
  .msg.err { border-color: #c98f82; color: #8f3626; background: #f9e7e1; }

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
  .schip:focus-visible { outline: 2px solid #3c405b; outline-offset: 2px; }
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
    color: #fff; font-family: inherit; line-height: 1;
    background: linear-gradient(135deg, #3c405b, #4a4f6e);
    border: 1px solid rgba(43,48,73,0.204);
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
  .jump:focus-visible { outline: 2px solid #3c405b; outline-offset: 3px; }
  .jump svg { width: 17px; height: 17px; display: block; }

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
    display: flex; gap: 10px; padding: 14px 20px 18px;
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
  #input::placeholder { color: #7c8496; }
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
    background: #fffcef;
    border: 1px solid rgba(205,159,60,.30);
    box-shadow: 0 2px 8px rgba(74,58,30,.07), inset 0 1px 0 #ffffff;
    transition: border-color .18s, box-shadow .18s;
  }
  .messageBox:focus-within {
    border-color: rgba(60,64,91,.45);
    box-shadow: 0 0 0 4px rgba(232,191,95,.30), 0 2px 10px rgba(74,58,30,.10);
  }
  .ico {
    flex: 0 0 auto; width: 36px; height: 36px; padding: 0;
    display: grid; place-items: center; border: 0; border-radius: 10px;
    background: transparent; color: var(--muted); cursor: pointer;
    transition: background .16s, color .16s, transform .16s cubic-bezier(.22,1,.36,1);
  }
  .ico svg { width: 19px; height: 19px; }
  .ico:hover { background: rgba(43,48,73,.08); color: var(--ink); }
  .ico:active { transform: scale(.9); }
  .ico:focus-visible { outline: 2px solid #3c405b; outline-offset: 2px; }
  #stickerbtn[aria-expanded="true"] { background: var(--ice); color: var(--ice-ink); }
  /* Round, because it sits inside a pill. A 12px rectangle in a 999px
     capsule looked like a button that had been dropped in. */
  .send {
    flex: 0 0 auto; width: 38px; height: 38px; padding: 0;
    display: grid; place-items: center;
    background: linear-gradient(150deg, #464b69 0%, #3c405b 100%);
    border: 0; border-radius: 50%; color: #fffcef; cursor: pointer;
    transition: filter .15s, transform .16s cubic-bezier(.22,1,.36,1),
                box-shadow .18s;
    box-shadow: 0 2px 8px rgba(60,64,91,.28), inset 0 1px 0 rgba(255,255,255,.14);
    font-family: inherit;
  }
  .send svg { width: 18px; height: 18px; }
  .send:hover { filter: brightness(1.1); transform: translateY(-1px);
                box-shadow: 0 5px 14px rgba(60,64,91,.32), inset 0 1px 0 rgba(255,255,255,.14); }
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
             border-top: 1px dashed rgba(43,48,73,0.102); }
  .wd-lab {
    font-size: 10.5px; letter-spacing: .04em; color: #555a78;
    font-weight: 600; margin-bottom: 6px;
  }
  .wd-lab b { color: var(--muted); font-weight: 400; }
  .wd-chips { display: flex; flex-wrap: wrap; gap: 4px; }
  .wchip {
    background: rgba(79,70,160,.10); color: #2c3169;
    border: 1px solid rgba(79,70,160,.28); border-radius: 7px;
    padding: 4px 9px; font-size: 11.5px; cursor: pointer;
    transition: .12s; font-family: inherit;
  }
  .wchip:hover { background: rgba(79,70,160,.18); color: #1f2456;
                 border-color: rgba(79,70,160,.55); }
  .wchip.on { background: linear-gradient(135deg, #4a4fa0, #3c405b);
              color: #fff; border-color: transparent; }
  .wd-more { font-size: 10.5px; color: var(--dim); margin-top: 5px; }
  .wd-more.btn {
    background: rgba(43,48,73,0.051); border: 1px solid rgba(43,48,73,0.119);
    border-radius: 8px; padding: 5px 10px; cursor: pointer;
    font-family: inherit; color: var(--muted);
  }
  .wd-more.btn:hover { background: rgba(43,48,73,0.102); color: var(--text); }

  .wdetail {
    display: none; margin-bottom: 11px; padding: 12px;
    border-radius: 13px; position: relative;
    background: linear-gradient(150deg, rgba(79,70,160,.14), rgba(60,64,91,.10));
    border: 1px solid rgba(79,70,160,.34);
    box-shadow: 0 6px 20px rgba(74,58,30,.28), inset 0 1px 0 rgba(43,48,73,0.119);
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
    background: rgba(43,48,73,0.119); color: #3b405e;
  }
  .wd-close {
    background: none; border: none; color: var(--dim); cursor: pointer;
    font-size: 14px; padding: 4px 6px; border-radius: 6px; line-height: 1;
    font-family: inherit;
  }
  .wd-close:hover { color: var(--text); background: rgba(43,48,73,0.085); }
  .wd-mean {
    font-size: 14px; line-height: 1.6; margin: 7px 0 4px; color: var(--text);
  }
  .wd-mean b { color: #4a4fa0; }
  .wd-forms {
    display: grid; grid-template-columns: 1fr; gap: 4px; margin-top: 5px;
  }
  .wd-form {
    display: flex; align-items: baseline; gap: 8px;
    padding: 6px 9px; border-radius: 8px;
    background: rgba(43,48,73,0.0595); border: 1px solid rgba(43,48,73,0.085);
  }
  .wd-form b {
    font-family: "SF Mono", Consolas, "DejaVu Sans Mono", monospace;
    font-size: 13px; color: #8a5a00; font-weight: 700; flex: none;
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
    color: #6b4a00; padding: 3px 9px; border-radius: 999px;
    background: var(--gold-soft); border: 1px solid rgba(138,90,0,.2);
    letter-spacing: .2px;
  }
  .dtrack {
    flex: 1 1 80px; height: 7px; border-radius: 999px; overflow: hidden;
    background: rgba(43,48,73,0.0765); border: 1px solid rgba(43,48,73,0.102);
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
  .dlvl { background: rgba(43,48,73,.119); color: #3b405e; }
  .dreg { background: rgba(110,90,168,.14); color: #33526e; }
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
  .dfa { font-size: 13px; color: var(--text); line-height: 1.55; margin-top: 3px; }
  .dline { font-size: 13px; color: var(--text); line-height: 1.5; }
  .dline.fa { font-size: 12.5px; color: var(--muted); }
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
    background: rgba(43,48,73,.0425); border: 1px solid rgba(43,48,73,.085);
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
    background: rgba(43,48,73,.045); border: 1px solid rgba(43,48,73,.085);
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
      0 1px 0 rgba(255,255,255,.9) inset,
      0 2px 5px rgba(74,58,30,.055),
      0 20px 38px -26px rgba(74,58,30,.75);
    font-family: var(--font-body);
  }
  /* A gold rule across the top edge rather than a bar down the side: the card
     is something you read, and the rule marks where the day starts without
     turning its left edge into a permanent stripe. */
  .dinline::before {
    content: ""; position: absolute; inset: 0 0 auto; height: 3px; z-index: 1;
    background: linear-gradient(90deg, var(--gold2), var(--gold) 42%, #f8e2b4);
  }
  .dinline.complete { border-color: rgba(79,70,160,.32); }
  .dinline.complete::before {
    background: linear-gradient(90deg, var(--success), #7175c0 55%, #bcbfe6);
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
    background:
      radial-gradient(130% 160% at 0% 0%, rgba(232,191,95,.26), transparent 64%),
      linear-gradient(180deg, #fdf9e9, #fbf3df);
  }
  .diico {
    width: 28px; height: 28px; border-radius: 9px; flex: none;
    display: grid; place-items: center;
    background: linear-gradient(180deg, #fdf1d6, var(--gold-soft));
    border: 1px solid rgba(138,90,0,.26); color: #7d5200;
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
    overflow: hidden; background: rgba(43,48,73,.06);
    box-shadow: inset 0 1px 2px rgba(43,48,73,.07);
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
    font-size: 15px; line-height: 1; color: rgba(82,96,119,.8);
    border: 1px solid transparent; background: transparent;
    transition: background .15s, color .15s;
  }
  /* The header band is warm, so the ✕ darkens toward the navy on hover rather
     than sitting in the flat grey the rows below use. */
  .dix:hover { background: rgba(138,90,0,.12); color: var(--navy); }
  .dirow {
    display: flex; align-items: flex-start; gap: 8px;
    padding: 8px 13px 7px 14px;
    border-top: 1px solid rgba(43,48,73,.075);
    transition: background .15s;
  }
  /* The meter already draws the line above the first row. */
  .dump + .dirow { border-top: 0; }
  @media (hover: hover) { .dirow:hover { background: rgba(43,48,73,.024); } }
  .dirow .grow { flex: 1 1 auto; min-width: 0; cursor: pointer; }
  /* A tinted chip per kind, so the three rows are told apart at a glance
     without a label repeating what the row already says. */
  .dikind {
    flex: none; width: 24px; height: 24px; border-radius: 7px; margin-top: 1px;
    display: grid; place-items: center;
  }
  .dikind svg { width: 13px; height: 13px; }
  .dirow[data-kind="words"] .dikind { background: var(--gold-soft); color: #8a5a00; }
  .dirow[data-kind="expressions"] .dikind { background: var(--ice); color: var(--ice-ink); }
  .dirow[data-kind="conversations"] .dikind {
    background: rgba(42,90,122,.13); color: #2a5a7a;
  }
  .dimain {
    font-family: var(--font-display); font-size: 14.5px; font-weight: 700;
    color: var(--navy2); line-height: 1.3; word-break: break-word;
  }
  .dirow.done .dimain { color: #3d4289; }
  .disub {
    direction: rtl; text-align: right; unicode-bidi: plaintext;
    font-family: var(--font-fa);
    font-size: 12px; color: var(--muted); margin-top: 3px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  /* The opened body is an inset of the card, not a second card: warm paper,
     a hairline, and slightly looser leading than the rows above it. */
  .dibody { margin-top: 7px; padding: 9px 11px; border-radius: 12px;
            background: linear-gradient(180deg, #fffdf8, #fdf8ec);
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
    border: 1px solid rgba(43,48,73,.13); background: #fffcef;
    transition: background .15s, border-color .15s, color .15s;
  }
  /* A done item is a filled disc, not a lightly tinted outline: at a glance
     the day is either three unfilled boxes or three filled ones. */
  .ditick.on, .dtick.on {
    background: var(--success); border-color: var(--success); color: #fff;
  }
  .ditick:hover, .dimore:hover { border-color: rgba(43,48,73,.24); }
  .dimore svg { width: 11px; height: 11px; transition: transform .18s; }
  .dirow.open .dimore svg { transform: rotate(180deg); }
  .difoot {
    display: flex; align-items: center; gap: 4px; flex-wrap: wrap;
    margin: 0; padding: 8px 12px 9px 14px;
    border-top: 1px solid rgba(43,48,73,.075);
    background: rgba(43,48,73,.022);
  }
  .dibtn {
    font-family: var(--font-body); font-size: 11px; padding: 5px 9px;
    border-radius: 999px; cursor: pointer; color: var(--navy2);
    border: 1px solid rgba(43,48,73,.14); background: #fffcef;
  }
  .dibtn:hover { background: var(--gold-soft); }
  .dibtn.ghost {
    border-color: transparent; background: transparent; color: var(--dim);
    padding-inline: 6px;
  }
  .dibtn.ghost:hover { background: rgba(43,48,73,.05); color: var(--navy); }
  .difoot .spacer { flex: 1 1 auto; }

  /* ---------- the Today panel, scannable rather than scrollable ---------- */
  .dlead { margin-top: 2px; }
  .dmore {
    flex: none; width: 26px; height: 26px; border-radius: 8px; cursor: pointer;
    display: grid; place-items: center; padding: 0; font-family: inherit;
    color: var(--dim); border: 1px solid rgba(43,48,73,.13); background: #fffcef;
  }
  .dmore svg { width: 11px; height: 11px; transition: transform .18s; }
  .dcard.open .dmore svg { transform: rotate(180deg); }
  .dcard .dbody { display: none; }
  .dcard.open .dbody { display: block; }
  .dtick {
    flex: none; width: 26px; height: 26px; border-radius: 8px; cursor: pointer;
    display: grid; place-items: center; padding: 0; font-family: inherit;
    font-size: 12px; color: var(--dim);
    border: 1px solid rgba(43,48,73,.13); background: #fffcef;
  }
  .dtick.on { background: rgba(79,70,160,.14); border-color: rgba(79,70,160,.4); color: #3d4289; }
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
  .nfail { color: #a4451f; }
  .nhead b { font-family: var(--font-display); font-size: 15px; color: var(--navy2); }
  .nhead { margin-bottom: 2px; }
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
    font-family: var(--font-body); font-size: 11px; font-weight: 400; color: var(--muted);
  }
  .nev {
    font-size: 11.5px; color: var(--gold-ink, #8a6d1f); margin-top: 4px;
    font-style: italic; word-break: break-word;
  }
  .nnote2 { font-size: 12.5px; color: var(--text); margin-top: 5px; line-height: 1.5; }
  .nchip {
    margin-top: 8px; font-family: var(--font-body); font-size: 11.5px;
    padding: 5px 10px; border-radius: 999px; cursor: pointer;
    border: 1px solid rgba(79,70,160,.35); background: rgba(79,70,160,.08);
    color: #3d4289;
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
    background: #fffcef; border: 1px solid rgba(43,48,73,.14);
    transition: background .15s, border-color .15s;
  }
  .dbtn:hover { background: var(--gold-soft); }
  .dbtn.on, .dbtn[aria-pressed="true"] {
    background: rgba(79,70,160,.12); border-color: rgba(79,70,160,.35);
    color: #30356f;
  }
  .dfoot { font-size: 10px; color: var(--dim); margin-inline-start: auto; }
  .dnote { font-size: 12px; color: var(--muted); line-height: 1.5; margin-top: 6px; }
  .dnone { font-size: 13px; color: var(--muted); line-height: 1.6; }
  @media (min-width: 620px) {
    .dcards { gap: 12px; }
    .dword { font-size: 23px; }
    .dwho { min-width: 74px; }
  }
  @media (max-width: 420px) {
    .dwho { min-width: 46px; font-size: 10px; }
    .dturn { gap: 6px; }
  }

  /* ---------- review: saved words + flashcards ---------- */
  /* Inside the tile. A negative offset puts it outside a 46px button, and
     being a span it then inherits .hbtn span's overflow:hidden and is clipped
     in half - a sliver on the edge rather than a badge. */
  .rbadge {
    position: absolute; top: 3px; inset-inline-end: 3px; z-index: 1;
    display: inline-flex; align-items: center; justify-content: center;
    min-width: 15px; height: 15px; padding: 0 3px; border-radius: 999px;
    font-size: 9px; font-weight: 800; line-height: 1; color: #33260a;
    background: #e8bf5f; border: 1px solid rgba(250,244,232,.55);
    box-shadow: 0 1px 3px rgba(74,58,30,.35);
    /* .hbtn span sets ellipsis and a nowrap overflow; a number needs neither */
    text-overflow: clip; max-width: none;
  }
  /* .hbtn span (0,1,1) outranked .rbadge (0,1,0), so the count inherited the
     label's grey on a gold pill - 3.8:1 at 9px. The badge needs its own ink. */
  .hbtn span.rbadge { color: #33260a; }
  .rbadge[hidden] { display: none; }
  .rtop { display: flex; align-items: center; gap: 7px; flex-wrap: wrap; margin-bottom: 10px; }
  .rprog {
    flex: 1 1 120px; height: 7px; border-radius: 999px; overflow: hidden;
    background: rgba(43,48,73,0.0765); border: 1px solid rgba(43,48,73,0.102);
  }
  .rprog i {
    display: block; height: 100%; border-radius: 999px;
    background: linear-gradient(90deg, #4a4fa0, #3c405b);
    transition: width .35s cubic-bezier(.34,1.3,.64,1);
  }
  .rcount { font-size: 11.5px; color: var(--muted); white-space: nowrap; }
  .rtab {
    background: rgba(43,48,73,0.0595); color: var(--muted);
    border: 1px solid rgba(43,48,73,0.119); border-radius: 8px;
    padding: 5px 11px; font-size: 11.5px; cursor: pointer;
    font-family: inherit; transition: .12s;
  }
  .rtab.on { background: linear-gradient(135deg, #4a4fa0, #3c405b); color: #fff; border-color: transparent; }
  .rtab:hover { color: var(--text); }
  .rtab.on:hover { color: #fff; }
  .rdanger:hover { background: rgba(168,73,58,.25); border-color: rgba(168,73,58,.5); }

  /* flashcard */
  .rcard {
    padding: 18px 14px 14px; border-radius: 15px; text-align: center;
    background: linear-gradient(155deg, rgba(43,48,73,0.085), rgba(43,48,73,0.0255));
    border: 1px solid rgba(43,48,73,0.119);
    box-shadow: inset 0 1px 0 rgba(43,48,73,0.119), 0 8px 24px rgba(74,58,30,.28);
    min-height: 176px; display: flex; flex-direction: column;
    justify-content: center; gap: 8px;
  }
  .rcard .rword { font-size: 26px; font-weight: 700; letter-spacing: .2px; line-height: 1.2; }
  .rcard .rpos {
    align-self: center; font-size: 10px; font-weight: 700; padding: 2px 8px;
    border-radius: 999px; background: rgba(43,48,73,0.111); color: #3b405e;
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
    margin-top: 4px; background: none; border: 1px dashed rgba(43,48,73,0.238);
    color: var(--muted); border-radius: 9px; padding: 7px 12px; font-size: 12px;
    cursor: pointer; font-family: inherit;
  }
  .rflip:hover { background: rgba(43,48,73,0.068); color: var(--text); }
  .racts { display: flex; gap: 8px; margin-top: 11px; }
  .rbtn {
    flex: 1; min-height: 44px; border-radius: 11px; cursor: pointer;
    font-family: inherit; font-size: 13px; font-weight: 700;
    border: 1px solid rgba(43,48,73,0.119); color: #fff;
  }
  .rbtn.know { background: linear-gradient(135deg, #4a4fa0, #8e92da); }
  .rbtn.again { background: linear-gradient(135deg, #b4552f, #a8493a); }
  .rbtn.play { background: rgba(43,48,73,0.085); flex: 0 0 52px; font-size: 16px;
               line-height: 1; padding: 0; }
  .rbtn:hover { filter: brightness(1.1); }
  .rdots { display: flex; gap: 3px; justify-content: center; margin-top: 10px; flex-wrap: wrap; }
  .rdot { width: 6px; height: 6px; border-radius: 50%; background: rgba(43,48,73,0.17); }
  .rdot.on { background: #4a4fa0; }
  .rdot.now { background: #e8bf5f; transform: scale(1.5); }

  /* list mode */
  .rlist { display: flex; flex-direction: column; gap: 6px; }
  .rrow {
    display: grid; grid-template-columns: 1fr auto auto; gap: 9px; align-items: center;
    padding: 8px 10px; border-radius: 10px;
    background: linear-gradient(150deg, rgba(43,48,73,0.051), rgba(43,48,73,0.017));
    border: 1px solid rgba(43,48,73,0.085);
  }
  .rrow .rmain { min-width: 0; }
  .rrow .ren { font-size: 13.5px; font-weight: 600; }
  .rrow .rfa2 { font-size: 11.5px; color: var(--muted); margin-top: 1px; }
  .rrow.ok { border-color: rgba(79,70,160,.4); }
  .rrow.ok .ren::after { content: ' \2713'; color: #4a4fa0; }
  .ricon {
    width: 30px; height: 30px; border-radius: 8px; border: 1px solid rgba(43,48,73,0.119);
    background: rgba(43,48,73,0.0595); color: var(--text); font-size: 13px;
    cursor: pointer; display: grid; place-items: center; font-family: inherit;
  }
  .ricon:hover { background: rgba(43,48,73,0.119); }
  .ricon.del:hover { background: rgba(168,73,58,.25); border-color: rgba(168,73,58,.5); }
  .rempty { text-align: center; padding: 26px 10px; color: var(--muted); font-size: 13px; line-height: 1.7; }
  .rempty .big { font-size: 30px; display: block; margin-bottom: 8px; }

  /* the "save to review" toggle inside the word card */
  .rstar {
    background: rgba(201,138,22,.14); border: 1px solid rgba(201,138,22,.34);
    color: #8a5a00; border-radius: 9px; padding: 6px 11px; font-size: 12px;
    cursor: pointer; font-family: inherit; font-weight: 600;
  }
  .rstar:hover { background: rgba(201,138,22,.26); }
  .rstar.on { background: linear-gradient(135deg, #e8bf5f, #b4552f); color: #33260a; border-color: transparent; }
  .wd-star { margin-top: 10px; display: flex; gap: 7px; align-items: center; flex-wrap: wrap; }
  .wd-star .why { font-size: 11px; color: var(--dim); }

  /* ---------- phonetics: topic rail + dense symbol cards ----------
     Designed so a whole lesson fits on one phone screen: the rail is one
     scroll line, rows are a single column, and every ▶ speaks the example. */
  .phrail {
    display: flex; gap: 6px; overflow-x: auto; padding: 2px 0 9px;
    margin-bottom: 4px; border-bottom: 1px solid rgba(43,48,73,0.085);
    -webkit-overflow-scrolling: touch; overscroll-behavior-x: contain;
    scrollbar-width: none;
  }
  .phrail::-webkit-scrollbar { display: none; }
  .phtab {
    flex: none; display: inline-flex; align-items: center; gap: 6px;
    background: rgba(43,48,73,0.051); color: var(--muted);
    border: 1px solid rgba(43,48,73,0.119); border-radius: 999px;
    padding: 6px 12px; font-size: 12px; font-weight: 600;
    cursor: pointer; transition: .14s; font-family: inherit; white-space: nowrap;
  }
  .phtab i {
    font-style: normal; font-size: 9px; font-weight: 800; letter-spacing: .04em;
    padding: 2px 5px; border-radius: 5px;
    background: rgba(43,48,73,0.085); color: #555a78;
  }
  .phtab:hover { background: rgba(43,48,73,0.102); color: var(--text); }
  .phtab.on {
    background: var(--navy);
    color: #fffcef; border-color: transparent;
    box-shadow: 0 4px 12px rgba(43,48,73,.22);
  }
  .phtab.on i { background: rgba(255,255,255,.18); color: #fffcef; }

  /* the view scrolls inside the panel; the rail stays pinned so you never
     lose your place when drilling through a list */
  .phview { padding-top: 12px; overflow-y: auto; flex: 1; min-height: 0;
            overscroll-behavior: contain; -webkit-overflow-scrolling: touch; }
  #phpanel, #rpanel { display: none; flex-direction: column; }
  #phpanel.open, #rpanel.open { display: flex; }
  .phead { margin-bottom: 12px; }
  .phead .ptitle {
    display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
    font-size: 16px; font-weight: 700; letter-spacing: .2px;
  }
  .phead .ptitle .lvl {
    font-size: 9.5px; font-weight: 800; letter-spacing: .06em;
    padding: 2px 7px; border-radius: 999px;
    background: var(--ice);
    color: #2b3049; border: 1px solid rgba(60,64,91,.4);
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
    color: #555a78; font-weight: 700; margin-bottom: 7px;
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
    background: linear-gradient(150deg, rgba(43,48,73,0.0595), rgba(43,48,73,0.0213));
    border: 1px solid rgba(43,48,73,0.085);
    box-shadow: inset 0 1px 0 rgba(43,48,73,0.0765);
  }
  .prow:hover { background: rgba(43,48,73,0.085); border-color: rgba(60,64,91,.3)); }
  .pmain { min-width: 0; }
  .pip {
    font-family: "SF Mono", "Cascadia Mono", Consolas, "DejaVu Sans Mono", monospace;
    font-size: 13.5px; font-weight: 700; color: #8a5a00;
    word-break: break-word; line-height: 1.35;
  }
  .psub { font-size: 11px; color: #555a78; margin-top: 1px; line-height: 1.4; }
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
    background: var(--navy); border: none;
    color: #fffcef; font-size: 12px; cursor: pointer;
    display: grid; place-items: center; transition: .12s;
    box-shadow: 0 3px 10px rgba(43,48,73,.2);
  }
  .pplay:hover { filter: brightness(1.12); transform: scale(1.06); }
  .pplay.playing { background: linear-gradient(135deg, #4a4fa0, #3c405b); }

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
    font-size: 13px; font-weight: 700; color: #8a5a00;
    padding: 1px 3px 6px; margin-bottom: 6px;
    border-bottom: 1px solid rgba(43,48,73,0.102);
  }
  .pcard {
    display: flex; flex-direction: column; gap: 2px;
    padding: 8px 10px; margin-bottom: 5px;
    border-radius: 10px;
    background: linear-gradient(150deg, rgba(43,48,73,0.0723), rgba(43,48,73,0.0255));
    border: 1px solid rgba(43,48,73,0.0935);
    box-shadow: inset 0 1px 0 rgba(43,48,73,0.085);
  }
  .pcard:last-child { margin-bottom: 0; }
  .pcard .pen { font-size: 13px; line-height: 1.45; color: var(--text); }
  .pcard .pen::before {
    content: '▸'; color: #8a5a00; font-size: 10px; margin-inline-end: 6px;
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
    .app { background: #fffcef; }
    header { background: #fffcef; }
    #vpanel, #gpanel, #fpanel, #phpanel, #rpanel, #dpanel, #npanel, #bpanel { background: #fffcef; }
    .msg.bot { background: #fffcef; }
    #input { background: #fffdf4; }
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

  /* ---- panels: nearly full height, edge-to-edge, own scroll area ---- */    #vpanel, #gpanel, #fpanel, #lpanel, #phpanel, #rpanel, #dpanel, #npanel, #bpanel {
    padding: 10px calc(var(--pad) + var(--sar)) 11px calc(var(--pad) + var(--sal));
    max-height: 66%;
    overscroll-behavior: contain;
    -webkit-overflow-scrolling: touch;
  }
  #vpanel h3, #gpanel h3, #fpanel h3, #lpanel h3, #phpanel h3, #rpanel h3,
  #bpanel h3 {
    font-size: 11.5px; margin-bottom: 8px; line-height: 1.5;
  }
  .domains { max-height: 46vh; }

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
    background: rgba(201,138,22,.14); color: #8a5a00;
    border-left-color: rgba(201,138,22,.34);
  }
  .go.exam:not(.locked):hover { background: rgba(201,138,22,.34); }
  .go.exam.locked {
    /* --muted, not --dim: the locked chip sits on the lavender bar, where the
       lighter grey measured 4.1:1 at 11.5px. */
    background: rgba(43,48,73,0.102); color: var(--muted);
    border-left-color: rgba(43,48,73,0.221);
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
    gap: 8px; flex-direction: column;
  }
  /* The composer holds three things: the input, the mic and Send. The input is
     the only one allowed to shrink, so the mic can never be squeezed off a
     narrow screen - min-width:0 states that explicitly rather than relying on
     the input's intrinsic width being small. */
  #input { min-width: 0; }
  @media (max-width: 420px) {
    .messageBox { gap: 2px; padding: 3px 4px 3px 3px; }
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
    height: 3px; border-radius: 2px; background: rgba(43,48,73,0.0765);
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
  .limitenote.warn .limitxt { color: #8a5a00; }

  .limitenote.full .limitfill {
    background: linear-gradient(90deg, rgba(168,73,58,.95), rgba(168,73,58,.95));
  }
  .limitenote.full .lockic { filter: none; }
  .limitenote.full {
    padding: 9px 12px; border-radius: 11px;
    background: #fdf5ea;
    border: 1px solid rgba(168,73,58,.28);
    animation: fade .2s ease;
  }
  .limitenote.full .limitrail { height: 14px; }
  .limitenote.full .limitfill { top: 6px; height: 3px; }
  .limitenote.full .lockic { top: -4px; }
  .limitenote b { color: var(--ink); }
  form.locked #input {
    opacity: .45; cursor: not-allowed; background: rgba(43,48,73,0.0255);
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
    color: #fffcef; background: #3c405b;
    border: 0;
    box-shadow: 0 2px 8px rgba(43,48,73,.22), inset 0 1px 0 rgba(255,255,255,.16);
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
    background: #424765; color: #fffcef;
    box-shadow: 0 4px 16px rgba(74,58,30, .6), inset 0 1px 0 rgba(43,48,73,0.187);
  }
  .mic:focus-visible { outline: 2px solid #3c405b; outline-offset: 2px; }
  .mic:active { transform: scale(.94); }
  /* Teal, not pink. Pink is the tutor; when the mic pulses in the tutor's
     own colour it reads as though the app is talking at you. */
  .mic.rec {
    background: #a8493a; color: #fffcef;
    box-shadow: 0 2px 10px rgba(168,73,58,.3), 0 0 0 1px rgba(168,73,58,.35);
    animation: micPulse 1.4s ease-out infinite;
  }
  .mic.rec svg { transform: scale(1.06); }
  /* aria-disabled, not disabled: a disabled button swallows its own click
     events, so on touch the control would sit there doing nothing and the
     explanation in its title would be unreachable. aria-disabled announces
     the state to a screen reader while leaving the tap working. */
  .mic[aria-disabled="true"] {
    background: #e6dfd0; color: var(--dim);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.6);
  }
  .mic[aria-disabled="true"]:hover {
    background: #ddd5c4; color: #5c6a82;
  }
  /* a hint, once, so the button is noticed rather than rediscovered */
  @keyframes micHint {
    0%, 100% { box-shadow: 0 2px 8px rgba(43,48,73,.22), 0 0 0 0 rgba(232,191,95,.6); }
    60%      { box-shadow: 0 2px 8px rgba(43,48,73,.22), 0 0 0 9px rgba(232,191,95,0); }
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
    background: #fffcef; border: 1px solid rgba(43,48,73,.14);
    border-radius: 14px; color: var(--ice-ink);
  }
  .stt-panel[hidden] { display: none; }
  .stt-dot {
    width: 9px; height: 9px; border-radius: 50%; background: #a8493a;
    flex: 0 0 9px; animation: micBlink 1.1s ease-in-out infinite;
  }
  @keyframes micBlink { 0%, 100% { opacity: 1; } 50% { opacity: .25; } }
  .stt-label { color: #5c6a82; font-size: 12.5px; }
  .stt-interim { color: #616a8b; font-style: italic; }
  /* white on the cream speech card: the transcript arrived invisible */
  .stt-final { color: var(--ink); }

  /* ------------------------------------------------ BBC listening ------- */
  .bbc-open {
    display: block; width: 100%; margin-bottom: 10px; padding: 11px 14px;
    border-radius: 13px; border: 1px solid #cfc1a4; background: #f5eedb;
    color: #4a4f6e; font-size: 13.5px; text-align: left; cursor: pointer;
  }
  .bbc-open:hover { border-color: #3c405b; }
  .bbc-head { display: flex; flex-direction: column; gap: 7px; margin-bottom: 10px; }
  .bbc-back {
    align-self: flex-start; min-height: 40px; padding: 8px 13px; border-radius: 11px;
    border: 1px solid #cfc1a4; background: #f5eedb; color: #4a4f6e;
    font-size: 12.5px; cursor: pointer;
  }
  .bbc-note { font-size: 12px; color: #5c6a82; line-height: 1.5; }
  .bbc-tabs { display: flex; gap: 6px; overflow-x: auto; padding-bottom: 9px; }
  .bbc-tab {
    flex: 0 0 auto; padding: 6px 12px; border-radius: 999px; font-size: 12.5px;
    border: 1px solid #dccfb6; background: transparent; color: #4a5170; cursor: pointer;
  }
  .bbc-tab.on { background: var(--navy); border-color: var(--navy); color: #fffcef; }
  .bbc-list { display: flex; flex-direction: column; gap: 9px; }
  .bbc-row {
    padding: 12px 14px; border-radius: 14px; background: #f5eedb;
    /* a hairline, not the #2b3768 outline the dark list used */
    border: 1px solid rgba(43,48,73,.13);
    box-shadow: 0 2px 8px rgba(74,58,30,.07);
  }
  .bbc-row-head { display: flex; gap: 9px; align-items: baseline; }
  .bbc-lvl {
    flex: 0 0 auto; font-size: 11px; font-weight: 700; padding: 2px 8px;
    border-radius: 999px; background: #eadfc7; color: #4a4f6e;
  }
  .bbc-lvl.lvl-A2 { background: #e4e6f8; color: #383d80; }
  .bbc-lvl.lvl-B1 { background: #dce8f6; color: #2f5c96; }
  .bbc-lvl.lvl-B2 { background: #ece6f8; color: #33526e; }
  .bbc-lvl.lvl-C1 { background: #f6dfe8; color: #a03a63; }
  /* the unrated chip belongs to the same family as the others; it was a navy
     pill left over from the dark list, sitting on a cream card */
  .bbc-lvl.lvl-none { background: #eadfc7; color: #4a4f6e; }
  .bbc-title { font-size: 14.5px; color: var(--ink); font-weight: 600; }
  .bbc-blurb { margin-top: 5px; font-size: 12.5px; color: #616a8b; line-height: 1.5; }
  .bbc-meta { margin-top: 6px; font-size: 11.5px; color: #5c6a82; }
  .bbc-actions { display: flex; gap: 7px; margin-top: 9px; flex-wrap: wrap; align-items: center; }
  .bbc-play {
    padding: 8px 14px; min-height: 40px; border-radius: 11px; font-size: 13px;
    border: 1px solid var(--navy); background: var(--navy); color: #fffcef;
    cursor: pointer; font-family: var(--font-display);
  }
  .bbc-play.on { background: #8a5a00; border-color: #8a5a00; }
  .bbc-play.nofile { background: #efe4d1; border-color: rgba(43,48,73,.18); color: var(--muted); }
  .bbc-play.nofile:hover { border-color: rgba(43,48,73,.4); color: var(--ink); }
  .bbc-link { font-size: 12px; color: var(--ice-ink); text-decoration: none; padding: 6px 4px; }
  .bbc-link:hover { color: var(--navy); text-decoration: underline; }
  .bbc-empty { font-size: 12px; color: #5c6a82; padding: 4px 2px; }
  /* 40, not 46: this min-height was the floor for the whole composer row,
     input and mic included, so the button set the height of the form. */
  .send { width: 36px; height: 36px; border-radius: 50%; }

  /* ---------- tablets: two comfortable columns ---------- */
  @media (min-width: 600px) {
    :root { --pad: 18px; }
    .app { border-radius: 22px; border: 1px solid rgba(43,48,73,0.119); }
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
    #vpanel, #gpanel, #fpanel, #lpanel, #phpanel, #rpanel, #dpanel, #npanel, #bpanel { padding: 14px 20px; max-height: 52%; }
    .domains { max-height: 230px; }
    form { padding: 14px 20px 18px; gap: 8px; }
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
      rgba(43,48,73,0.255) 50%, transparent 70%);
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
    background: linear-gradient(90deg, #3c405b, #b8872a, #3c405b);
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
    background: radial-gradient(circle, rgba(43,48,73,0.468), rgba(43,48,73,0) 70%);
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
    background-image: linear-gradient(100deg, #eadfc7 20%, #4d63b8 45%, #eadfc7 70%);
    background-size: 220% 100%;
    animation: pillShimmer 4.6s ease-in-out infinite;
  }
  .bbc-lvl.lvl-A1 { background-image: linear-gradient(100deg,#e4e6f8,#797dc8,#e4e6f8); background-size:220% 100%; }
  .bbc-lvl.lvl-A2 { background-image: linear-gradient(100deg,#dce8f6,#3f86d9,#dce8f6); background-size:220% 100%; }
  .bbc-lvl.lvl-B1 { background-image: linear-gradient(100deg,#dbe6f0,#8a6ae0,#dbe6f0); background-size:220% 100%; }
  .bbc-lvl.lvl-B2 { background-image: linear-gradient(100deg,#f0e3ea,#c06ae0,#f0e3ea); background-size:220% 100%; }
  .bbc-lvl.lvl-C1 { background-image: linear-gradient(100deg,#f6dfe8,#a03a63,#f6dfe8); background-size:220% 100%; }
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
    background: conic-gradient(from -90deg, #8a5a00 var(--p, 0turn), transparent 0);
    -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 2px), #000 calc(100% - 1px));
    mask: radial-gradient(farthest-side, transparent calc(100% - 2px), #000 calc(100% - 1px));
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
    background: var(--navy);
    border: 1px solid var(--navy); color: #fffcef;
    font-size: 13px; line-height: 1.5; text-align: center;
    box-shadow: 0 14px 40px rgba(74,58,30, .6);
    animation: toastIn .32s cubic-bezier(.22,1,.36,1) both;
  }
  .toast.out { animation: toastOut .26s ease-in forwards; }
  @media (min-width: 900px) {
    .toast-host { bottom: 96px; }
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
          <img class="boot-fox" src="brand/fox-mark.png" alt="" width="86"
               height="86" decoding="async">
        </span>
      </div>
      <div class="boot-brand">
        <div class="boot-name">Fluentify</div>
        <div class="boot-tag">A step a day, a win a day
          <em dir="rtl" lang="fa">هرروز یک قدم هرروز یک برد</em></div>
      </div>
      <div class="boot-loading" aria-hidden="true">
        <div class="loader"></div>
        <div class="boot-track"><i id="bootfill"></i></div>
      </div>
      <div class="boot-meta">
        <span id="bootpct">0%</span>
      </div>
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
      <button class="hbtn" id="dtoggle" aria-expanded="false" title="Today's English — انگلیسی امروز" aria-label="Today — word, expression and conversation of the day">
        <i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3.4" y="4.8" width="17.2" height="16" rx="2.4"/><path d="M3.4 9.6h17.2M8.2 3.2v3.2M15.8 3.2v3.2"/><path d="M7.6 13.4h3.2v3.2H7.6z"/></svg></i><span>Today</span><span class="rbadge" id="dbadge" hidden>0</span></button>
      <button class="hbtn" id="ntoggle" aria-expanded="false" title="Analyse a sentence — تحلیل گرامری جمله" aria-label="Analyse a sentence">
        <i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="10.8" cy="10.6" r="5.8"/><path d="M15.2 15.2 20 20"/><path d="M8 12.4V9.2M10.8 12.4V7.4M13.6 12.4v-3"/></svg></i><span>Analyse</span></button>
      <button class="hbtn" id="vtoggle" aria-expanded="false" title="Vocabulary — واژگان" aria-label="Vocabulary">
        <i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="8" y="3.2" width="12.4" height="13.6" rx="2.2"/><path d="M15.4 19.4h.6a2 2 0 0 0 2-2V8"/><path d="M16 20.8H5.6a2 2 0 0 1-2-2V8.4"/></svg></i><span>Vocab</span></button>
      <button class="hbtn" id="btoggle" aria-expanded="false" title="Books — کتاب‌ها" aria-label="Books — lesson words from the course books">
        <i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4.4 5.2a1.8 1.8 0 0 1 1.8-1.8h3.2A1.8 1.8 0 0 1 11.2 5.2v13.4H6.2a1.8 1.8 0 0 0-1.8 1.8Z"/><path d="M19.6 5.2a1.8 1.8 0 0 0-1.8-1.8h-3.2a1.8 1.8 0 0 0-1.8 1.8v13.4h5a1.8 1.8 0 0 1 1.8 1.8Z"/></svg></i><span>Books</span></button>
      <button class="hbtn" id="gtoggle" aria-expanded="false" title="Grammar — گرامر" aria-label="Grammar">
        <i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4.2 19.4V5.6a1.8 1.8 0 0 1 1.8-1.8h8.6l4.6 4.6v11a1.8 1.8 0 0 1-1.8 1.8H6a1.8 1.8 0 0 1-1.8-1.8Z"/><path d="M14.2 3.8v4.8h4.6"/><path d="M8 12.4h7M8 16.2h4.6"/></svg></i><span>Grammar</span></button>
      <button class="hbtn" id="ftoggle" aria-expanded="false" title="Sentences — جملات کاربردی" aria-label="Say — everyday sentences / جملات کاربردی">
        <i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.6 11.6a8.2 8.2 0 0 1-8.4 8.2 8.6 8.6 0 0 1-3.2-.6l-4.6 1.4 1.4-4.2a8.2 8.2 0 1 1 14.8-4.8Z"/><path d="M8.8 11.6h.01M12.2 11.6h.01M15.6 11.6h.01"/></svg></i><span>Say</span></button>
      <button class="hbtn" id="ltoggle" aria-expanded="false" title="Listening A1–C2 — شنیدن" aria-label="Listening">
        <i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4.4 15.2v-3.4a7.6 7.6 0 0 1 15.2 0v3.4"/><rect x="2.6" y="13.8" width="4.4" height="6.6" rx="2.2"/><rect x="17" y="13.8" width="4.4" height="6.6" rx="2.2"/></svg></i><span>Listen</span></button>
      <button class="hbtn" id="phtoggle" aria-expanded="false" title="Phonetics — تلفظ و آهنگ" aria-label="Sounds — pronunciation and rhythm / تلفظ و آهنگ">
        <i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2.8 12h1.4M7.2 7.6v8.8M11.4 4.6v14.8M15.6 8.6v6.8M19.8 10.6v2.8"/></svg></i><span>Sounds</span></button>
      <button class="hbtn" id="rtoggle" aria-expanded="false" title="Review saved words — واژه‌های مرور" >
        <i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m12 3.4 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17.4l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9L12 3.4Z"/></svg></i><span>Review</span><span class="rbadge" id="rbadge" hidden>0</span></button>
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
             aria-label="Sentence to analyse">
      <button type="button" id="ngo" class="nbtn">Analyse · تحلیل</button>
    </div>
    <div class="nexamples" id="nexamples"></div>
    <div class="nresult" id="nresult" aria-live="polite"></div>
  </div>

  <div id="dpanel">
    <h3>Today's English: one word, one expression, one conversation — انگلیسی امروز</h3>
    <div class="dpanelbar">
      <span class="ddate" id="ddate"></span>
      <div class="dtrack" role="progressbar" aria-label="Today's progress"
           aria-valuemin="0" aria-valuemax="3" aria-valuenow="0" id="dtrack"><i id="dfill"></i></div>
      <span class="dcount" id="dcount">0 / 3</span>
    </div>
    <div class="dcards" id="dcards"></div>
    <div class="disk">
      <button type="button" class="dibtn" id="dcardtoggle" aria-pressed="true">Keep
      today&rsquo;s English out of the chat — پنهان کردن کارت روزانه</button>
    </div>
  </div>

  <div id="vpanel">
    <h3>Vocabulary A1 → C2</h3>
    <div class="psearch">
      <input id="vsearch" type="search" placeholder="Search 70 domains… / جست‌وجوی دسته‌ها…"
             autocomplete="off" aria-label="Search vocabulary domains">
    </div>
    <div class="domains" id="domains"></div>
    <div class="pempty" id="vempty" hidden>No domain matches that search. / دسته‌ای با این جست‌وجو پیدا نشد.</div>
  </div>

  <div id="bpanel">
    <h3>Books — کتاب‌ها</h3>
    <div class="bbooks" id="bbooks" aria-live="polite"></div>
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
  </div>

  <div class="stt-panel" id="stt" hidden></div>
  <form id="composer">
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
const YELLOW_BIRD =
  '<svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' +
  '<defs>' +
  '<linearGradient id="ybA" x1="0" y1="0" x2="1" y2="1">' +
  '<stop offset="0" stop-color="#ffe9a8"/><stop offset="55%" stop-color="#ffd257"/>' +
  '<stop offset="100%" stop-color="#b8872a"/></linearGradient>' +
  '<linearGradient id="ylA" x1="0" y1="0" x2="0" y2="1">' +
  '<stop offset="0" stop-color="#fffdf2"/><stop offset="100%" stop-color="#fff0c2"/>' +
  '</linearGradient></defs>' +
  '<path d="M10 27 L3.5 20 L5.5 31 Z" fill="#b8872a"/>' +
  '<ellipse cx="23" cy="27" rx="16" ry="13.5" fill="url(#ybA)"/>' +
  '<ellipse cx="23" cy="30.5" rx="9.5" ry="7.5" fill="url(#ylA)" opacity=".95"/>' +
  '<path d="M13 23.5 q8.5 2.5 8.5 10.5 q-8.5-2.5-8.5-10.5Z" fill="#ffbe3d"/>' +
  '<path d="M21.5 13.5 q1-6.5 4.5-6.5 q-1.2 4-2 6 q2.8-4 6-3 q-2 3-4.5 4.2Z" fill="#ffd979"/>' +
  '<path d="M36 22.5 L42.5 25.5 L36 28.5 Z" fill="#b8872a"/>' +
  '<circle cx="31" cy="21.5" r="3.3" fill="#4a2b00"/>' +
  '<circle cx="32.3" cy="20.3" r="1.15" fill="#fff"/>' +
  '<ellipse cx="34.5" cy="27.5" rx="3.2" ry="2.1" fill="#b8872a" opacity=".35"/>' +
  '</svg>';

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
  av.innerHTML = who === 'bot' ? MASCOT : YELLOW_BIRD;

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
  if (busy) return;                      // real message, but one is in flight
  // daily limit reached — refuse the message, don't queue it
  if (Seed.spent()) { Seed.block(); return; }
  busy = true;
  sendbtn.disabled = true;
  lastUserText = text;
  add(text, 'user');
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
          ? '🔇 This clip could not be decoded. / این کلیپ پخش نشد.'
          : '🔇 Could not reach the audio — check your connection. / ' +
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
    bpanel: 'btoggle', rpanel: 'rtoggle',
  };
  let openId = null;

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
      // Only pull focus back if it is still inside the panel being closed -
      // otherwise Escape from the composer would steal it. The destination is
      // the panel's own tile rather than whatever was focused on open, because
      // a mouse click does not reliably focus the button it lands on and the
      // remembered element would sometimes be <body>.
      if (panel.contains(document.activeElement)) {
        document.getElementById(TILES[panelId])?.focus();
      }
      return;
    }

    // one panel at a time, the way it has always worked
    if (openId && openId !== panelId) set(openId, false);

    panel.classList.add('open');
    tile?.classList.add('on');
    tile?.setAttribute('aria-expanded', 'true');
    openId = panelId;

    // A panel whose content is generated rather than static has to be told to
    // redraw when it opens. Without this the Review panel opened blank.
    if (hook) hook();

    // focus the close button, not the first field: opening a panel should not
    // drop a keyboard user into a search box they did not ask for
    (panel.querySelector('.pclose') || panel).focus?.();
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

  return {init, set, toggle, ensureShell, addSearch, isOpen: () => openId,
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
      node.textContent = q
        ? `${shown} of ${state.items.length} · ${needle}`
        : `${state.items.length} · نمایش همه`;
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
    live.textContent = q
      ? `… · ${q}` : `${items.length} · نمایش همه`;
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
      'not-allowed': 'دسترسی به میکروفون داده نشد. / Microphone permission was denied.',
      'service-not-allowed': 'سرویس گفتار در دسترس نیست. / The speech service is unavailable.',
      'no-speech': 'چیزی نشنیدم — دوباره بگو. / Nothing heard — try again.',
      'audio-capture': 'میکروفون پیدا نشد. / No microphone found.',
      'network': 'شبکه لازم است برای این مرورگر. / This browser needs a network connection.',
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
    if (!this.listening && !this.interim && !this.final) {
      panel.hidden = true;
      panel.innerHTML = '';
      return;
    }
    panel.hidden = false;
    const bits = [];
    if (this.listening) {
      bits.push('<span class="stt-dot"></span><span class="stt-label">در حال شنیدن… / listening</span>');
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
  const LABEL = 'با میکروفون تایپ کن / dictate';
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
      || 'این مرورگر گفتار را تشخیص نمی‌دهد — تایپ کن. / This browser has no speech recognition — type instead.';
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
    view.innerHTML = '<div class="pblurb">Phonetics unavailable offline. / آموزش تلفظ در دسترس نیست.</div>';
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
        'Audio plays from the offline mirror. / صدا از نسخه آفلاین پخش می‌شود.'
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
    lab.textContent = 'Word architecture / ساختار واژه';
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
      lab.innerHTML = '🧩 New words / <b>واژه‌های این سطح</b> — tap one to see its architecture';
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
    box.innerHTML = '<div class="pblurb">Sentences unavailable offline. / جملات در دسترس نیست.</div>';
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
  head.append(
    b,
    document.createTextNode(name.en),
    Object.assign(document.createElement('span'), {className: 'fa', textContent: name.fa}),
    Object.assign(document.createElement('span'), {
      className: 'count',
      textContent: count + (noun || '') + (nounFa ? ' · ' + nounFa : ''),
    }),
  );
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
        b.title = d.title_fa + ' — ' + d.count + ' words';
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
    box.innerHTML = '<div class="pblurb">Vocabulary unavailable offline. / واژگان در دسترس نیست.</div>';
  }
}
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
};
document.getElementById('dtoggle').onclick = () => togglePanel('dpanel', 'dtoggle');
document.getElementById('ntoggle').onclick = () => togglePanel('npanel', 'ntoggle');
document.getElementById('vtoggle').onclick = () => togglePanel('vpanel', 'vtoggle');
document.getElementById('gtoggle').onclick = () => togglePanel('gpanel', 'gtoggle');
document.getElementById('ftoggle').onclick = () => togglePanel('fpanel', 'ftoggle');
document.getElementById('ltoggle').onclick = () => togglePanel('lpanel', 'ltoggle');
document.getElementById('phtoggle').onclick = () => togglePanel('phpanel', 'phtoggle');
document.getElementById('btoggle').onclick = () => togglePanel('bpanel', 'btoggle');
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
    return rows ? '<div class="dlabel">Examples — مثال‌ها</div><div class="dex">' +
      rows + '</div>' : '';
  }

  function cardShell(kind, level, extraHead, body) {
    return '<div class="dtop"><span class="dico">' + CARD_ICON[kind] + '</span>' +
      '<span class="dkind">' + KIND_EN[kind] + '<small>' + KIND_FA[kind] +
      '</small></span><span class="spacer"></span>' + (extraHead || '') +
      (level ? '<span class="dlvl">' + esc(level) + '</span>' : '') +
      '</div>' + body;
  }

  function wordBody(entry) {
    let html = '';
    const def = entry.def || {};
    if (def.en || def.fa) {
      html += '<div class="dlabel">Meaning — معنی</div>' +
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
    [['use', 'Means — یعنی'], ['when', 'When — کجا به کار می‌رود']].forEach(([f, label]) => {
      const body = entry[f] || {};
      if (!body.en && !body.fa) return;
      html += '<div class="dlabel">' + label + '</div><div class="dline">' +
        esc(body.en) + '</div>' + faLine(body.fa, 'dline fa');
    });
    html += examples(entry);
    const alt = entry.alt || {};
    if (alt.en) {
      html += '<div class="dlabel">Also say — این هم می‌شود</div><div class="drow">' +
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
        'aria-pressed="true">فارسی: روشن / Persian: on</button></div>'
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
      '<span class="dkind">' + KIND_EN[kind] + '<small>' + KIND_FA[kind] +
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
          'this panel again.<br>درس امروز بارگذاری نشد — یک بار دیگر این بخش را باز کن.' +
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
        html += '<div class="dlabel">Example — مثال</div><div class="dline">' +
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
        html += '<div class="dlabel">Example — مثال</div><div class="dline">' +
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
        ' more lines in the panel. / ادامهٔ مکالمه در بخش امروز.' + '</div>';
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
      '<button type="button" class="dibtn ghost" data-learn="1">Read all three — هر سه</button>' +
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
        b.textContent = open ? 'Close all — بستن همه' : 'Read all three — هر سه';
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
    b.textContent = hidden
      ? 'Show today\u2019s English in the chat — نمایش کارت روزانه'
      : 'Keep today\u2019s English out of the chat — پنهان کردن کارت روزانه';
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
        b.textContent = off ? 'فارسی: خاموش / Persian: off' : 'فارسی: روشن / Persian: on';
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
}

/* grammar lessons panel (fetched from grammar.json via the server) */
const LEVEL_NAMES = {
  A1: 'مبانی · Beginner',
  A2: 'پایه · Elementary',
  B1: 'متوسط · Intermediate',
  B2: 'پیشرفته · Upper-Int.',
  C1: 'پیشرفته · Advanced',
  C2: 'تسلط · Proficiency',
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
      head.append(
        document.createTextNode(lv + ' · '),
        Object.assign(document.createElement('b'), {textContent: LEVEL_NAMES[lv] || lv}),
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
  const calm = window.matchMedia('(prefers-reduced-motion: reduce)');
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
    el.classList.add('gone');
    // Removed as well as faded: left in the tree it stays a full-screen
    // element that a later focus can land on.
    setTimeout(() => { if (el.parentNode) el.parentNode.removeChild(el); }, 400);
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
    step(done, total) { aim(total ? done / total : 0); },
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
  const steps = [
    ['Today', loadDaily],
    ['Stickers', () => Stickers.load()],
    ['Vocabulary', loadVocabulary],
    ['Grammar', loadGrammar],
    ['Sentences', loadPhrases],
    ['Listening', loadListening],
    ['Sounds', loadPhonetics],
    ['Word index', loadWordArch],
    ['Audio', bbcDoc],
  ];
  let done = 0;
  Boot.step(0, steps.length, 'Preparing');
  await Promise.all(steps.map(async ([label, run]) => {
    try { await run(); } catch (e) { /* one thin section beats no app */ }
    Boot.step(++done, steps.length, label);
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
    this.paintBadge();
  },
  save() {
    try { localStorage.setItem(this.KEY, JSON.stringify(this.items)); } catch (e) {}
    this.paintBadge();
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
  paintBadge() {
    const b = document.getElementById('rbadge');
    if (!b) return;
    b.textContent = this.items.length;
    b.hidden = !this.items.length;
  },

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
        'هنوز واژه‌ای ذخیره نشده. هر کارت واژه را باز کنید و ☆ را بزنید.</div>';
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
    const cardsTab = mk('button', 'rtab' + (this.mode === 'cards' ? ' on' : ''), '🃏 Cards');
    cardsTab.onclick = () => { this.mode = 'cards'; this.at = 0; this.flipped = false; this.paint(); };
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

    top.append(cardsTab, listTab, prog, count, restart, wipe);
    (this.mode === 'cards' ? this.paintCard : this.paintList).call(this, body);
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
      box.innerHTML = '<div class="pblurb">Reading the library… / در حال خواندن کتاب‌ها…</div>';
      try {
        this.data = await loadJSON('books');
      } catch (e) {
        box.innerHTML = '<div class="pblurb">The books could not be read. / کتاب‌ها خوانده نشدند.</div>';
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
    else this.paintWords(box, book);
  },

  /* the word count of a book, computed once so all three depths agree */
  wordsOf(book) {
    return (book.lessons || []).reduce((n, l) => n + (l.words || []).length, 0);
  },

  back(label, fn) {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'bback';
    b.textContent = '← ' + label;
    b.onclick = fn;
    return b;
  },

  /* shelf: one card per book */
  paintBooks(box, books) {
    if (!books.length) {
      box.innerHTML = '<div class="pblurb">No book is in the library yet. / هنوز کتابی در کتابخانه نیست.</div>';
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
      meta.textContent = (book.author ? book.author + ' · ' : '') + lessons +
        (lessons === 1 ? ' lesson' : ' lessons') + ' · ' + this.wordsOf(book) + ' words';
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
    box.appendChild(this.back('Books · کتاب‌ها', () => {
      this.bookId = null;
      this.lesson = null;
      this.paint();
    }));
    const head = document.createElement('div');
    head.className = 'bhead2';
    head.dir = 'ltr';
    head.textContent = book.title;
    box.appendChild(head);
    if (book.about_fa) {
      const about = document.createElement('div');
      about.className = 'pblurb';
      about.dir = 'rtl';
      about.lang = 'fa';
      about.textContent = book.about_fa;
      box.appendChild(about);
    }
    const list = document.createElement('div');
    list.className = 'bbooks';
    (book.lessons || []).forEach((lesson) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'blesson';
      const name = document.createElement('span');
      name.className = 'bn';
      name.dir = 'ltr';
      name.textContent = lesson.title || ('Lesson ' + lesson.n);
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
      n.textContent = (lesson.words || []).length + ' words';
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
    box.appendChild(this.back('Lessons · درس‌ها', () => {
      this.lesson = null;
      this.paint();
    }));
    const head = document.createElement('div');
    head.className = 'bhead2';
    head.dir = 'ltr';
    head.textContent = book.title + ' · ' + (lesson.title || ('Lesson ' + lesson.n)) +
      ' · ' + (lesson.words || []).length + ' words';
    box.appendChild(head);

    const list = document.createElement('div');
    list.className = 'bwords';
    (lesson.words || []).forEach((w) => {
      const card = document.createElement('div');
      card.className = 'bword';

      const h = document.createElement('div');
      h.className = 'bwh';
      h.dir = 'ltr';
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
    panel: 'npanel', btn: 'ntoggle', en: 'Sentence analyser', fa: 'تحلیل جمله',
    icon: '🔬',
    kw: ['analyser', 'analyzer', 'sentence analyser', 'sentence analyzer',
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
  'تحلیل\\s*گرامری|آنالیز\\s*گرامری|گرامر\\s*این\\s*جمله|' +
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

/* The analysis, rendered once and used twice: in the chat and in the panel.
   Every field is escaped; nothing from the tagger is trusted as markup. */
function renderAnalysis(r, opts) {
  const o = opts || {};
  const words = r.tokens.filter((t) => ['PUNCT', 'SYM'].indexOf(t.pos) === -1);
  const out = [];

  out.push('<div class="nhead"><b>' + escapeHtml(r.analysedSentence || r.originalSentence) +
    '</b>' + (r.analysedSentence && r.analysedSentence !== r.originalSentence
      ? '<div class="dfa">فقط بخش انگلیسی همین جمله تحلیل شد.</div>' : '') + '</div>');

  out.push('<div class="nlabel">Words — کلمات</div><div class="ntable">');
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
    out.push('<div class="nlabel">Structures — ساختارها</div>');
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
          '">📘 ' + escapeHtml(topic) + ' · درس</button>' : '') +
        '</div>');
    }
  }

  /* The tagger ships one standing caveat about its own method. It describes
     the engine rather than the sentence on screen, so the panel prints only
     the caveats this analysis earned — "read" that is also a present, a
     contraction the tagger expanded, a paste that was cut to length. */
  const caveats = (r.limitations || []).filter((l) => !/dependency parser/.test(l));
  if (caveats.length) {
    out.push('<div class="nlabel">What this cannot do — محدودیت‌ها</div><ul class="nlim">');
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
    paint('<div class="nbusy">🔬 analysing on this device… · در حال تحلیل…</div>');
    try {
      paint(renderAnalysis(await NLP.analyze(text)));
    } catch (e) {
      paint('<div class="nfail">⚠️ ' + escapeHtml(e.message) + '<br>تحلیل انجام نشد.</div>');
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
   and it works with the aeroplane mode on. */
async function matchAnalyseCommand(text) {
  const t = (text || '').trim();
  if (!t || t.length > 300 || !ANALYSE_INTENT.test(t)) return false;
  add(t, 'user');
  // Only the request itself: a request with no sentence in it asks for one
  // rather than silently re-analysing whatever the panel last held.
  const sentence = extractSentence(t);
  if (!sentence) {
    Analyser.open();
    add('🔬 Send me one English sentence and I will take it apart word by word. ' +
        'Nothing leaves your device.\n' +
        'یک جملهٔ انگلیسی بفرست تا کلمه‌به‌کلمه تحلیل کنم؛ همه‌چیز روی دستگاه خودت انجام می‌شود.\n' +
        'Try: **analyse this: She has been learning English.**', 'bot');
    return true;
  }
  showTyping();
  try {
    const result = await NLP.analyze(sentence);
    hideTyping();
    Analyser.show(result, sentence);
    add(renderAnalysis(result), 'bot', {html: true});
  } catch (e) {
    hideTyping();
    add('⚠️ ' + e.message + '\n' +
        'تحلیل انجام نشد — این بخش نباید به اینترنت نیاز داشته باشد.', 'bot', {err: true});
  }
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
