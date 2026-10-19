#!/usr/bin/env python3
"""Web preview for the bilingual chatbot — stdlib only, no dependencies.

Run:  python3 webapp.py   →  http://localhost:8765
"""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from chatbot import ChatBot

PORT = 8765
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
    # never serve transcript text: it is BBC's copyright, and the page links
    # to the official PDF instead
    for ep in doc.get("episodes", []):
        ep.pop("transcript", None)
    doc["count"] = len(doc.get("episodes", []))
    return doc
bot = ChatBot()  # shared session memory for the preview

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fluentify — English &amp; Persian</title>
<meta name="description" content="A bilingual English and Persian tutor: graded vocabulary, grammar, sentence patterns, pronunciation and 1126 BBC listening episodes, with speech-to-text and an offline Android app.">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>
  :root {
    /* base theme sampled from imagecolorpicker.com/color-code/0b102e */
    --base: #0b102e;
    --bg1: #0b102e; --bg2: #131a3f; --bg3: #1b2350;
    --panel: rgba(17, 24, 58, .88); --panel2: #1a2350;
    --accent: #6d8cff; --accent2: #34d399; --accent3: #a78bfa;
    --text: #eef1fb; --muted: #aab7d8; --dim: #8a97bb;
    --bot: #1c2450;
    /* The learner's own side. It was indigo->violet, which on a navy base
       read as the same family as the chrome and left both sides of the
       conversation looking alike. Teal is the one cool hue the wheel was
       missing between the indigo chrome and the emerald used for "correct",
       and it separates the two speakers at a glance.
       Every stop is at least 4.5:1 against white text. The violet it
       replaces was not: #a855f7 is 3.96 and #4f6ef7 is 4.28, both under the
       AA threshold for 15px text. */
    --user1: #0e7490; --user2: #0f766e; --user3: #115e59;
    /* accents, one per section. All are >= 6.8:1 on --base, and only one
       section is ever open at a time, so they read as a wayfinding key
       rather than a spectrum. */
    --teal: #2dd4bf; --cyan: #67e8f9; --violet: #c4b5fd;
    --emerald: #6ee7b7; --amber: #fcd34d; --rose: #ff8dc4;
    --line: rgba(148, 163, 184, .16);
    --line2: rgba(148, 163, 184, .28);
    --shadow: 0 40px 100px rgba(3, 6, 20, .7);
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { height: 100%; }
  body {
    font-family: "Segoe UI", Tahoma, "Vazirmatn", "IranSans", sans-serif;
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
      radial-gradient(46% 44% at 16% 20%, rgba(109,140,255,.62), transparent 72%),
      radial-gradient(42% 40% at 84% 16%, rgba(167,139,250,.52), transparent 72%),
      radial-gradient(52% 50% at 74% 84%, rgba(52,211,153,.34), transparent 72%),
      radial-gradient(46% 44% at 22% 86%, rgba(56,189,248,.40), transparent 72%),
      radial-gradient(38% 34% at 52% 52%, rgba(255,141,196,.20), transparent 74%),
      linear-gradient(160deg, #0b102e 0%, #151d4a 42%, #1d2660 100%);
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
                rgba(160,180,255,.16), transparent 68%);
    pointer-events: none;
  }

  /* Grounds the composer instead of letting the gradient run flat to the edge. */
  .vignette {
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background: radial-gradient(120% 90% at 50% 42%,
                transparent 52%, rgba(4,7,24,.55) 100%);
  }

  /* Grain. Large gradients band visibly on an OLED phone, and the banding is
     what makes a background look cheap. One static tiled SVG turbulence
     costs a small texture and nothing per frame. */
  .grain {
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    opacity: .035; mix-blend-mode: overlay;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3'/%3E%3C/filter%3E%3Crect width='140' height='140' filter='url(%23n)'/%3E%3C/svg%3E");
    background-size: 140px 140px;
  }


  /* ---- the boot screen ----
     Shown on every cold start, before anything else paints. It is in the
     markup rather than added by script on purpose: the boot reads about a
     megabyte of JSON, and a script-added overlay arrives after the first
     long frame - which is the blank screen it was meant to cover.

     It always goes away. Three ways out, because a loader that cannot be
     dismissed is the one bug worse than no loader at all: the boot finishing,
     a window error, and a deadline that fires whatever happened in between.
  */
  .boot {
    position: fixed; inset: 0; z-index: 9998;
    display: grid; place-items: center;
    background: radial-gradient(120% 90% at 50% 18%, #1b2350 0%, #0b102e 62%);
    transition: opacity .34s cubic-bezier(.22,1,.36,1), visibility .34s;
  }
  .boot.gone { opacity: 0; visibility: hidden; pointer-events: none; }
  .boot-in { display: grid; justify-items: center; gap: 14px; }
  .boot-bird {
    width: 74px; height: 74px;
    animation: bootBob 2.6s cubic-bezier(.45,0,.55,1) infinite;
  }
  @keyframes bootBob {
    0%, 100% { transform: translateY(0); }
    50%      { transform: translateY(-7px); }
  }
  /* A bouncing tile with its shadow on the floor. The shape is borrowed from
     a well-known loading animation; the colour is the tutor's. Transform
     only, so it stays on the compositor. */
  .loader {
    width: 34px; height: 34px; position: relative;
  }
  .loader::before {
    content: ''; width: 34px; height: 4px;
    background: rgba(255,92,157,.42);
    position: absolute; top: 42px; left: 0;
    border-radius: 50%;
    animation: bootShadow .5s linear infinite;
  }
  .loader::after {
    content: ''; width: 100%; height: 100%;
    background: linear-gradient(140deg, #ffc2e2, #ff5c9d);
    position: absolute; top: 0; left: 0;
    border-radius: 4px;
    animation: bootJump .5s linear infinite;
  }
  @keyframes bootJump {
    15%  { border-bottom-right-radius: 3px; }
    25%  { transform: translateY(8px) rotate(22.5deg); }
    50%  { transform: translateY(15px) scale(1, .9) rotate(45deg); border-bottom-right-radius: 22px; }
    75%  { transform: translateY(8px) rotate(67.5deg); }
    100% { transform: translateY(0) rotate(90deg); }
  }
  @keyframes bootShadow {
    0%, 100% { transform: scale(1, 1); }
    50%      { transform: scale(1.18, 1); }
  }
  .boot-txt { display: grid; justify-items: center; gap: 3px; margin-top: 6px; }
  .boot-txt b { font-size: 16px; color: #eef1fb; letter-spacing: .2px; }
  .boot-txt span { font-size: 12px; color: #9fb0ef; }
  /* The bar counts sections that have actually landed, so it has to be a
     real width rather than an animation on a fixed timeline. Transform
     only, so filling it costs no layout on a phone. */
  .boot-track {
    width: 172px; height: 3px; border-radius: 3px;
    background: rgba(255,255,255,.13); overflow: hidden;
  }
  .boot-track i {
    display: block; width: 100%; height: 100%; border-radius: inherit;
    background: linear-gradient(90deg, #ff8dc4, #a78bfa);
    transform: scaleX(0); transform-origin: 0 50%;
    transition: transform .45s cubic-bezier(.22,1,.36,1);
  }
  @media (prefers-reduced-motion: reduce) {
    .boot { transition: none; }
    .boot-bird { animation: none; }
    .loader::before, .loader::after { animation: none; }
    .boot-track i { transition: none; }
  }

  /* ---- the emoji picker ---- */
  .emoji-panel {
    margin: 0 0 6px;
    border-radius: 16px; overflow: hidden;
    background: linear-gradient(180deg, rgba(20,27,63,.97), rgba(14,19,48,.97));
    border: 1px solid var(--line2);
    box-shadow: 0 18px 44px rgba(3,6,20,.55);
    -webkit-backdrop-filter: blur(20px) saturate(150%);
    backdrop-filter: blur(20px) saturate(150%);
    animation: emojiIn .2s cubic-bezier(.22,1,.36,1);
  }
  .emoji-panel[hidden] { display: none; }
  @keyframes emojiIn {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: none; }
  }
  .esearch {
    width: 100%; border: 0; border-bottom: 1px solid var(--line);
    background: rgba(255,255,255,.04); color: var(--text);
    padding: 11px 14px; font-size: 14px; font-family: inherit;
    outline: none;
  }
  .esearch::placeholder { color: #7e8caf; }
  .esearch::-webkit-search-cancel-button { filter: invert(.7); }
  .ebody {
    max-height: 46vh; overflow-y: auto;
    padding: 8px 10px 10px;
    overscroll-behavior: contain;
  }
  .ebody::-webkit-scrollbar { width: 7px; }
  .ebody::-webkit-scrollbar-thumb { background: #2f3a6b; border-radius: 6px; }
  .ehead {
    font-size: 10px; letter-spacing: .09em; text-transform: uppercase;
    color: #8a97bb; font-weight: 700;
    padding: 9px 2px 5px; position: sticky; top: -8px;
    background: linear-gradient(180deg, rgba(16,22,52,.99), rgba(16,22,52,.9));
  }
  .etile {
    width: 38px; height: 38px; padding: 0; margin: 1px;
    font-size: 21px; line-height: 1; border: 0; border-radius: 9px;
    background: transparent; cursor: pointer;
    transition: background .13s, transform .13s cubic-bezier(.22,1,.36,1);
  }
  .etile:hover { background: rgba(255,255,255,.1); transform: scale(1.12); }
  .etile:active { transform: scale(.9); }
  .etile:focus-visible { outline: 2px solid #ff8dc4; outline-offset: 1px; }
  .eempty { padding: 22px 8px; text-align: center; color: #8a97bb; font-size: 13px; }
  /* Touch has no hover, and a tap that only shows a tooltip teaches nothing:
     the tile presses, the emoji goes in. */
  @media (hover: none) {
    .etile:hover { background: transparent; transform: none; }
  }

  /* ---- the watermark bird ------------------------------------------------
     The backdrop lived behind .app, which is 58-72% opaque and blurs whatever
     is behind it - so on a phone, where .app is full-bleed, none of it was
     visible at all. Whatever draws here has to be a child of .app to be seen,
     and a child is painted after the backdrop-filter, so it stays crisp.

     One bird, dead centre, drawn from the icon's own geometry so it is
     unmistakably the same bird rather than a generic one, filled flat instead
     of in the mascot's colours so it reads as a watermark and not as artwork
     competing with the conversation.

     Three things keep it from interrupting anything. It is small, it is at 6%,
     and it is masked: the radial gradient dissolves the outline to nothing
     before the edge, so the bird has no hard boundary to catch the eye. A
     solid silhouette, however faint, still has an edge; this one has a falloff.

     The six drifting birds that were here before are gone. Moving marks at
     13-20% read as clutter behind a transcript, not as ambience.
  */
  .flock {
    position: absolute; inset: 0; z-index: 0; overflow: hidden;
    pointer-events: none; border-radius: inherit;
  }
  .flock i {
    position: absolute; display: block;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'%3E%3Cpath fill='%23ffffff' d='M10 27 L3.5 20 L5.5 31 Z'/%3E%3Cellipse cx='23' cy='27' rx='16' ry='13.5' fill='%23ffffff'/%3E%3Cpath fill='%23ffffff' d='M13 23.5 q8.5 2.5 8.5 10.5 q-8.5-2.5-8.5-10.5Z'/%3E%3Cpath fill='%23ffffff' d='M21.5 13.5 q1-6.5 4.5-6.5 q-1.2 4-2 6 q2.8-4 6-3 q-2 3-4.5 4.2Z'/%3E%3Cpath fill='%23ffffff' d='M36 22.5 L42.5 25.5 L36 28.5 Z'/%3E%3Ccircle cx='31' cy='21.5' r='3.3' fill='%230e1338'/%3E%3C/svg%3E") no-repeat center / contain;
    -webkit-mask-image: radial-gradient(closest-side, #000 0%, #000 34%, rgba(0,0,0,.45) 58%, transparent 80%);
    mask-image: radial-gradient(closest-side, #000 0%, #000 34%, rgba(0,0,0,.45) 58%, transparent 80%);
  }
  .flock i.wm {
    width: min(30%, 260px); height: auto; aspect-ratio: 1;
    left: 50%; top: 50%;
    margin: 0;
    opacity: .06;
    translate: -50% -50%;
    animation: breathe 96s cubic-bezier(.22,1,.36,1) infinite alternate;
  }
  /* The only motion left: a slow swell, so the bird breathes rather than sits.
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
    background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.03));
    border: 1px solid rgba(255,255,255,.13);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.16), 0 10px 28px rgba(3,6,20,.34);
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
    border-radius: 50%; border: 1px solid rgba(255,255,255,.14);
    background: linear-gradient(180deg, rgba(255,255,255,.13), rgba(255,255,255,.05));
    color: #ffe6f3; cursor: pointer; padding: 0;
    transition: transform .16s cubic-bezier(.22,1,.36,1), background .16s;
  }
  .plbtn:hover { background: linear-gradient(180deg, rgba(255,255,255,.2), rgba(255,255,255,.08)); }
  .plbtn:active { transform: scale(.93); }
  .plbtn svg { width: 18px; height: 18px; fill: currentColor; }
  .plbtn:focus-visible { outline: 2px solid #ff8dc4; outline-offset: 2px; }
  .plbtn.ghost { width: 32px; height: 32px; color: #c9cbe6; }
  .plbtn.ghost svg { width: 14px; height: 14px; }
  .plbody { flex: 1 1 auto; min-width: 0; }
  .plhead { display: flex; align-items: baseline; gap: 8px; min-width: 0; }
  .plkind {
    flex: 0 0 auto; font-size: 10px; letter-spacing: .09em; text-transform: uppercase;
    color: #ff8dc4; font-weight: 700;
  }
  .pltitle {
    font-size: 13px; color: #eef0ff; white-space: nowrap;
    overflow: hidden; text-overflow: ellipsis; min-width: 0;
  }
  .pltrack {
    position: relative; height: 6px; margin-top: 6px; border-radius: 99px;
    background: rgba(255,255,255,.12); cursor: pointer;
    touch-action: none; overflow: hidden;
  }
  .pltrack:focus-visible { outline: 2px solid #ff8dc4; outline-offset: 3px; }
  .pltrack i {
    position: absolute; inset: 0 auto 0 0; width: 0%; border-radius: 99px;
    background: linear-gradient(90deg, #ff8dc4, #ff5c9d);
  }
  /* Speech has no duration to scrub, so the bar breathes instead of lying
     about a position. */
  .player.speech .pltrack i {
    width: 100% !important;
    background: linear-gradient(90deg, transparent, #ff8dc4 40%, #ff5c9d 60%, transparent);
    animation: plScan 2.4s cubic-bezier(.45,0,.55,1) infinite;
  }
  @keyframes plScan {
    0%   { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
  }
  .player.speech .pltrack { cursor: default; }
  .pltime {
    flex: 0 0 auto; font-size: 12px; color: #a9adcf;
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
    .etile { transition: none; }
    .player.speech .pltrack i { animation: none; opacity: .7; }
    .plbtn { transition: none; }
  }

  .orb {
    position: fixed; border-radius: 50%; pointer-events: none; z-index: 0;
    opacity: .40; will-change: transform;
  }
  .orb.o1 { width: 420px; height: 420px; top: -100px; left: -80px;
            background: radial-gradient(circle, rgba(109,140,255,.85) 0%,
                        rgba(109,140,255,.28) 42%, transparent 72%);
            animation: float1 18s cubic-bezier(.22,1,.36,1) infinite alternate; }
  .orb.o2 { width: 360px; height: 360px; bottom: -90px; right: -70px;
            background: radial-gradient(circle, rgba(167,139,250,.80) 0%,
                        rgba(167,139,250,.26) 42%, transparent 72%);
            animation: float2 22s cubic-bezier(.22,1,.36,1) infinite alternate; }
  .orb.o3 { width: 240px; height: 240px; top: 46%; right: 16%;
            background: radial-gradient(circle, rgba(52,211,153,.55) 0%,
                        rgba(52,211,153,.18) 44%, transparent 72%);
            opacity: .32;
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
    /* 44px, not 38. This is the one control in a panel you press with a thumb
       to get out of it, and the app already reserves --tap: 44px on phones
       for everything else. The button looked generous at desktop width and
       was not, at the width it is actually used. */
    flex: 0 0 44px; width: 44px; height: 44px; border-radius: 13px;
    display: grid; place-items: center; cursor: pointer;
    background: #18204a; border: 1px solid #33427c; color: #c3ceff;
    font-size: 17px; line-height: 1;
    transition: background .16s, border-color .16s, transform .14s;
  }
  .pclose:hover { background: #222c60; border-color: #6f86d6; color: #fff; }
  .pclose:focus-visible { outline: 2px solid #a8b8ff; outline-offset: 2px; }
  .pclose:active { transform: scale(.93); }
  .pclose svg { width: 15px; height: 15px; display: block; }

  /* the search box every panel now shares */
  .psearch { margin-bottom: 10px; flex: none; }
  .psearch input {
    width: 100%; padding: 10px 13px; border-radius: 12px;
    background: #18204a; border: 1px solid #33427c; color: var(--text);
    font-size: 14px; font-family: inherit; outline: none;
  }
  .psearch input::placeholder { color: #7583bd; }
  .psearch input:focus {
    border-color: #6f86d6;
    box-shadow: 0 0 0 3px rgba(111, 134, 214, .18);
  }

  /* the one empty state, used by every panel */
  .pempty {
    padding: 26px 18px; text-align: center; line-height: 1.7;
    color: #9fb0ef; font-size: 13.5px;
    background: #141c46; border: 1px dashed #33427c; border-radius: 14px;
  }
  .pempty b { color: #dbe3ff; }

  .pcount {
    flex: none; margin: -2px 2px 10px; font-size: 11.5px; color: #93a3e0;
    letter-spacing: .01em;
  }

  /* Grouped runs: the avatar collapses to a thin stem and the speaker name is
     dropped, so a multi-part answer reads as one turn. */
  /* Hide only the bird, not the avatar box. Hiding the box with visibility
     would hide the stem drawn on it as well, since a pseudo-element cannot be
     more visible than its parent - so the bird fades and the stem stays. */
  .row.grouped .mav { position: relative; }
  .row.grouped .mav > svg { opacity: 0; }
  .row.grouped .mav::before {
    content: ''; position: absolute; left: 50%; top: 15px; bottom: -15px;
    width: 2px; transform: translateX(-50%); border-radius: 1px;
    background: linear-gradient(rgba(255,141,196,.34), rgba(255,141,196,.05));
  }
  .row + .row.grouped { margin-top: -6px; }
  .row.grouped .meta > span:first-child,
  .row.grouped .meta > i { display: none; }
  .row.grouped .meta { justify-content: flex-end; }

  /* A cue that the panels scroll, or they just stop mid-button and read as a
     rendering fault. Painted on the clipping box rather than on :last-child,
     which PanelSearch appends to and so is not stable. */
  #vpanel, #gpanel, #fpanel, #lpanel, #phpanel, #rpanel {
    box-shadow: inset 0 -16px 16px -16px rgba(0,0,0,.62);
  }

  /* "Show more" for the 1126-episode BBC list */
  .bbc-more {
    display: block; width: 100%; margin-top: 10px; padding: 11px 14px;
    border-radius: 12px; cursor: pointer; font-family: inherit;
    font-size: 12.5px; color: #b9c6ff;
    background: rgba(109,140,255,.13); border: 1px solid rgba(109,140,255,.3);
    transition: background .16s, border-color .16s;
  }
  .bbc-more:hover { background: rgba(109,140,255,.22); border-color: #6f86d6; }
  .bbc-more:focus-visible { outline: 2px solid #a8b8ff; outline-offset: 2px; }

  /* ---- the app is a pane of frosted glass ---- */
  .app {
    position: relative; z-index: 1;
    width: min(1180px, 100%); height: min(94vh, 980px);
    display: flex; flex-direction: column; overflow: hidden;
    border-radius: 26px;
    background:
      linear-gradient(150deg, rgba(255,255,255,.09), rgba(255,255,255,.02) 45%, rgba(255,255,255,.05)),
      linear-gradient(180deg, rgba(9,13,38,.72), rgba(9,13,38,.58));
    border: 1px solid rgba(255,255,255,.14);
    box-shadow:
      0 40px 100px rgba(3, 6, 20, .7),
      0 0 0 1px rgba(255,255,255,.05),
      inset 0 1px 0 rgba(255,255,255,.22),
      inset 0 -1px 0 rgba(255,255,255,.06);
    -webkit-backdrop-filter: blur(24px) saturate(150%) brightness(92%);
    backdrop-filter: blur(24px) saturate(150%) brightness(92%);
  }
  /* thicker, brighter edge at the bottom = sense of glass depth */
  .app::after {
    content: ''; position: absolute; left: 12%; right: 12%; bottom: 0; height: 3px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,.5), transparent);
    pointer-events: none; z-index: 5;
  }

  /* ---------- header ---------- */
  /* frosted header — the .hb layer is oversized + masked so the blur also
   picks up pixels *near* the bar, which is what real frosted glass does */
  header {
    position: relative;
    display: flex; align-items: center; gap: 12px;
    padding: 15px 20px;
    background: linear-gradient(100deg,
      rgba(109,140,255,.20), rgba(167,139,250,.15) 40%, rgba(52,211,153,.11)),
      linear-gradient(180deg, rgba(8,12,34,.55), rgba(8,12,34,.35));
    border-bottom: 1px solid rgba(255,255,255,.12);
    flex: none;
  }
  .hb {
    position: absolute; inset: 0; height: 200%; z-index: -1;
    pointer-events: none;
    -webkit-backdrop-filter: blur(18px) saturate(170%) brightness(120%);
    backdrop-filter: blur(18px) saturate(170%) brightness(120%);
    -webkit-mask-image: linear-gradient(to bottom, #000 0% 50%, transparent 50% 100%);
    mask-image: linear-gradient(to bottom, #000 0% 50%, transparent 50% 100%);
  }
  .avatar {
    width: 46px; height: 46px; border-radius: 15px; flex: none;
    background: linear-gradient(150deg, rgba(255,255,255,.20), rgba(255,141,196,.16));
    border: 1px solid rgba(255,255,255,.24);
    display: grid; place-items: center;
    box-shadow: 0 8px 22px rgba(255,92,157,.28), inset 0 1px 0 rgba(255,255,255,.45);
  }
  .avatar svg { width: 38px; height: 38px; display: block; }
  /* the bird reacts to the daily seed */
  @keyframes bob { 0%,100% { transform: translateY(0) rotate(0deg); }
                   50% { transform: translateY(-4px) rotate(-4deg); } }
  @keyframes bloom { 0% { transform: scale(1); }
                      35% { transform: scale(1.18) rotate(6deg); }
                      60% { transform: scale(1.06) rotate(-4deg); }
                      100% { transform: scale(1); } }
  .avatar svg { animation: bob 1.7s ease-in-out infinite; }
  .avatar.full svg { animation: bob .9s ease-in-out infinite; }
  .avatar.bloom { animation: bloom 1.6s ease; }
  .avatar.full {
    box-shadow: 0 8px 26px rgba(255,141,196,.5), 0 0 0 2px rgba(255,141,196,.45),
                inset 0 1px 0 rgba(255,255,255,.5);
  }

  /* daily seed meter */
  #seedmeter {
    position: relative; flex: none; width: 66px; height: 20px; border-radius: 999px;
    background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.14);
    overflow: hidden; display: flex; align-items: center; justify-content: flex-end;
  }
  #seedmeter i {
    position: absolute; inset: 0 auto 0 0; border-radius: 999px;
    background: linear-gradient(90deg, #ff8dc4, #a78bfa);
    transition: width .45s cubic-bezier(.34,1.3,.64,1);
  }
  #seedmeter span {
    position: relative; font-size: 10.5px; font-weight: 700; padding: 0 7px;
    color: #fff; text-shadow: 0 1px 2px rgba(0,0,0,.45); white-space: nowrap;
  }
  header h1 { font-size: 17.5px; letter-spacing: .3px; font-weight: 700; }
  header p { font-size: 11.5px; color: var(--muted); margin-top: 2px; }
  .spacer { flex: 1; }
  .status {
    display: flex; align-items: center; gap: 6px;
    font-size: 12px; color: #6ee7b7;
    background: linear-gradient(120deg, rgba(52,211,153,.16), rgba(52,211,153,.06));
    border: 1px solid rgba(52,211,153,.35);
    padding: 6px 11px; border-radius: 999px; font-weight: 600;
  }
  .status i { width: 8px; height: 8px; border-radius: 50%; background: #34d399;
              box-shadow: 0 0 8px #34d399; animation: pulse 1.6s infinite; display: inline-block; }
  @keyframes pulse { 50% { opacity: .35; } }
  /* Section tiles: icon over a tiny caption. Seven of these fit across a
     phone without scrolling, where the old full-width pills overflowed. */
  /* Borderless on purpose. Seven outlined boxes in a row is a rack of
     buttons, not a toolbar; what separates them is the fill and the space
     between, which is what a toolbar actually is. The states carry
     themselves on background and shadow instead of on a coloured outline. */
  .hbtn {
    position: relative;
    background: linear-gradient(140deg, rgba(255,255,255,.13), rgba(255,255,255,.05));
    color: var(--text);
    border: 0; border-radius: 12px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,.10);
    width: 46px; height: 46px; padding: 4px 2px;
    display: inline-flex; flex-direction: column;
    align-items: center; justify-content: center; gap: 2px;
    cursor: pointer; transition: .15s; flex: none;
    font-family: inherit;
  }
  .hbtn i { font-style: normal; font-size: 16px; line-height: 1; }
  .hbtn span {
    font-size: 8.5px; font-weight: 700; letter-spacing: -.05px;
    line-height: 1; color: var(--muted); max-width: 100%;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }
  /* Without an outline to recolour, the open state has to say itself louder
     than the closed one: a deeper fill and a glow, not a line. */
  .hbtn:hover {
    background: linear-gradient(140deg, rgba(109,140,255,.30), rgba(167,139,250,.18));
  }
  .hbtn.on {
    background: linear-gradient(140deg, rgba(109,140,255,.46), rgba(167,139,250,.28));
    box-shadow: inset 0 1px 0 rgba(255,255,255,.16), 0 4px 16px rgba(109,140,255,.34);
  }
  .hbtn.on i, .hbtn.on span { color: #fff; }
  /* Keyboard users need to know which section button has focus now that
     there is no border to lose. */
  .hbtn:focus-visible {
    outline: 2px solid #ff8dc4;
    outline-offset: 2px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,.16), 0 0 0 3px rgba(255,141,196,.25);
  }
  .hbtn.danger:hover {
    border-color: rgba(248,113,113,.6);
    background: rgba(248,113,113,.2);
  }

  /* ---------- vocabulary / grammar / phrases panels ---------- */
  #vpanel, #gpanel, #fpanel, #lpanel, #phpanel, #rpanel {
    display: none; padding: 14px 20px;
    background: linear-gradient(160deg, rgba(255,255,255,.06), rgba(255,255,255,.015)),
                linear-gradient(180deg, rgba(8,12,34,.86), rgba(8,12,34,.74));
    -webkit-backdrop-filter: blur(20px) saturate(150%);
    backdrop-filter: blur(20px) saturate(150%);
    border-bottom: 1px solid rgba(255,255,255,.10);
    flex: none; animation: fade .18s ease;
    max-height: 52%; overflow-y: auto;
    /* fade the bottom edge so it reads as scrollable rather than clipped */
    -webkit-mask-image: linear-gradient(to bottom, #000 calc(100% - 22px), transparent);
    mask-image: linear-gradient(to bottom, #000 calc(100% - 22px), transparent);
  }
  #vpanel.open, #gpanel.open, #fpanel.open, #lpanel.open { display: block; }
  /* #phpanel gets its own flex layout below, so it is not listed here */
  @keyframes fade { from { opacity: 0; transform: translateY(-4px); } }
  #vpanel h3, #gpanel h3, #fpanel h3, #lpanel h3, #phpanel h3, #rpanel h3 {
    font-size: 12px; color: #a9b8de; margin-bottom: 9px; font-weight: 600;
  }
  /* A coloured rule per section. Only one panel is ever open, so this is a
     wayfinding cue rather than a palette to look at - it tells you where you
     are before you have read a word. */
  #vpanel h3  { border-inline-start: 3px solid var(--teal);    padding-inline-start: 9px; }
  #gpanel h3  { border-inline-start: 3px solid var(--violet);  padding-inline-start: 9px; }
  #fpanel h3  { border-inline-start: 3px solid var(--rose);    padding-inline-start: 9px; }
  #lpanel h3  { border-inline-start: 3px solid var(--cyan);    padding-inline-start: 9px; }
  #phpanel h3 { border-inline-start: 3px solid var(--emerald); padding-inline-start: 9px; }
  #rpanel h3  { border-inline-start: 3px solid var(--amber);   padding-inline-start: 9px; }

  /* ---------- listening: level tabs + playable sentences ---------- */
  .ltabs { display: flex; gap: 5px; margin-bottom: 10px; flex-wrap: wrap; }
  .ltab {
    background: linear-gradient(140deg, rgba(255,141,196,.14), rgba(167,139,250,.10));
    color: #ffc4e2; border: 1px solid rgba(255,141,196,.3);
    border-radius: 8px; padding: 4px 12px; font-size: 12px; font-weight: 700;
    cursor: pointer; transition: .12s; font-family: inherit;
  }
  .ltab:hover { background: rgba(255,141,196,.28); transform: translateY(-1px); }
  .ltab.on {
    background: linear-gradient(140deg, #ff8dc4, #a78bfa); color: #fff;
    border-color: transparent; box-shadow: 0 3px 12px rgba(255,141,196,.35);
  }
  .llist { display: flex; flex-direction: column; gap: 4px; }
  .lrow {
    display: flex; align-items: center; gap: 10px;
    background: rgba(255,255,255,.05); border: 1px solid rgba(255,255,255,.1);
    border-radius: 10px; padding: 7px 11px; transition: .12s;
  }
  .lrow:hover { background: rgba(255,255,255,.09); border-color: rgba(255,141,196,.35); }
  .lrow.playing {
    background: rgba(255,141,196,.16); border-color: rgba(255,141,196,.6);
  }
  .lplay {
    width: 28px; height: 28px; flex: none; border-radius: 50%;
    background: linear-gradient(135deg, #ff8dc4, #a78bfa); border: none;
    color: #fff; font-size: 12px; cursor: pointer;
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
    color: #9fb0dd; margin-bottom: 5px; font-weight: 600;
  }
  .vgroup-head .fa { color: #7f8fbd; text-transform: none; letter-spacing: 0; font-weight: 400; }
  .vgroup-head .count {
    background: rgba(255,255,255,.07); border-radius: 999px;
    padding: 0 6px; font-size: 10px; margin-inline-start: auto;
  }
  .vrow { display: flex; flex-wrap: wrap; gap: 4px; }
  .vbtn {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(109,140,255,.1); color: #c3cdff;
    border: 1px solid rgba(109,140,255,.26);
    border-radius: 8px; padding: 3px 9px; font-size: 11.5px;
    cursor: pointer; transition: .12s; font-family: inherit;
  }
  .vbtn:hover {
    background: rgba(109,140,255,.26); border-color: rgba(109,140,255,.5);
    transform: translateY(-1px); color: #e2e8ff;
  }
  .vbtn .n {
    background: rgba(255,255,255,.1); border-radius: 5px;
    padding: 0 5px; font-size: 10px; color: var(--muted);
    font-variant-numeric: tabular-nums;
  }
  /* grammar panel: compact, grouped by CEFR level */
  .glevel { margin-bottom: 8px; }
  .glevel:last-child { margin-bottom: 0; }
  .glevel-head {
    display: flex; align-items: center; gap: 7px;
    font-size: 11px; color: var(--muted); letter-spacing: .05em;
    text-transform: uppercase; margin-bottom: 6px;
  }
  /* CEFR level chip in the group header */
  .vgroup-head .lv {
    font-size: 9.5px; font-weight: 800; letter-spacing: .05em;
    padding: 2px 6px; border-radius: 5px;
    background: linear-gradient(135deg, rgba(109,140,255,.34), rgba(167,139,250,.28));
    color: #dbe2ff; border: 1px solid rgba(109,140,255,.38);
  }
  /* in-panel search (56 domains needs one) */
  .psearch { margin-bottom: 9px; }
  .psearch input {
    width: 100%; padding: 9px 13px; font-size: 15px; font-family: inherit;
    color: var(--text); outline: none; border-radius: 10px;
    background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.14);
  }
  .psearch input:focus {
    border-color: rgba(109,140,255,.7); background: rgba(255,255,255,.09);
    box-shadow: 0 0 0 3px rgba(109,140,255,.16);
  }
  .psearch input::placeholder { color: #7e8caf; }
  .pempty { font-size: 12.5px; color: var(--muted); padding: 10px 2px; }
  .ftopic .n {
    background: rgba(255,255,255,.1); border-radius: 5px;
    padding: 0 5px; font-size: 10px; color: var(--muted);
  }
  .glevel-head b { color: #a5b6ff; font-weight: 700; }
  .glevel-head .count {
    background: rgba(255,255,255,.07); border-radius: 999px;
    padding: 1px 7px; font-size: 10.5px;
  }
  .gtopic {
    display: flex; flex-wrap: wrap; gap: 5px;
  }
  .gbtn {
    display: inline-flex; align-items: stretch;
    background: rgba(52,211,153,.09);
    border: 1px solid rgba(52,211,153,.3);
    border-radius: 999px; overflow: hidden;
    transition: .15s; white-space: nowrap;
  }
  .gbtn:hover { background: rgba(52,211,153,.2); transform: translateY(-1px); }
  .gmain {
    background: none; border: none; cursor: pointer;
    display: inline-flex; align-items: baseline; gap: 5px;
    color: #6ee7b7; padding: 4px 4px 4px 11px; font-size: 12px;
    font-family: inherit;
  }
  .gmain .fa { color: var(--muted); font-size: 11px; }
  .go {
    background: rgba(167,139,250,.18); color: #ddd6fe;
    border: none; border-left: 1px solid rgba(167,139,250,.32);
    padding: 0 8px; font-size: 11px; cursor: pointer;
  }
  .go:hover { background: rgba(167,139,250,.38); }
  .gsep { color: var(--muted); font-size: 11px; width: 100%; }

  /* ---------- chat area ---------- */
  #chat {
    flex: 1; overflow-y: auto; padding: 22px 22px 10px;
    display: flex; flex-direction: column; gap: 16px;
    scroll-behavior: smooth;
    /* Firefox: backdrop-filter can flicker inside overflow+border-radius parents */
    overscroll-behavior: none;
  }
  #chat::-webkit-scrollbar, .domains::-webkit-scrollbar { width: 9px; }
  #chat::-webkit-scrollbar-thumb, .domains::-webkit-scrollbar-thumb {
    background: #2f3a6b; border-radius: 8px;
  }
  #chat::-webkit-scrollbar-track { background: transparent; }
  .row { display: flex; gap: 10px; align-items: flex-end; animation: pop .2s ease; }
  @keyframes pop { from { opacity: 0; transform: translateY(8px); } }
  .row.user { flex-direction: row-reverse; }
  .mav {
    width: 32px; height: 32px; border-radius: 11px; flex: none;
    display: grid; place-items: center; font-size: 16px;
    background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.14);
  }
  .mav svg { width: 26px; height: 26px; display: block; }
  .mav.bot {
    background: linear-gradient(150deg, rgba(255,255,255,.16), rgba(255,141,196,.14));
    border-color: rgba(255,141,196,.3);
  }
  .mav.me {
    background: linear-gradient(150deg, rgba(255,255,255,.16), rgba(255,210,87,.16));
    border-color: rgba(255,210,87,.34);
  }
  .row.user .mav {
    background: linear-gradient(150deg, rgba(255,255,255,.18), rgba(255,210,87,.18));
    border-color: rgba(255,210,87,.38);
    box-shadow: 0 4px 12px rgba(245,165,36,.3);
  }
  .row.user .mav {
    background: linear-gradient(135deg, var(--user1), var(--user2));
    border: none; box-shadow: 0 4px 12px rgba(79,110,247,.35);
  }
  .bubble-wrap { max-width: min(78%, 760px); display: flex; flex-direction: column; gap: 5px; }
  .row.user .bubble-wrap { align-items: flex-end; }
  .msg {
    position: relative;
    padding: 12px 16px; border-radius: 17px;
    font-size: 15px; line-height: 1.68; white-space: pre-wrap; word-wrap: break-word;
    border: 1px solid var(--line);
  }
  /* The tutor's own bubbles carry the bird's colour. Neutral white glass made
     every reply look like a system message; the tutor is the one voice in the
     conversation and should be the one that looks like a voice. Anthropomorphic
     styling measurably raises perceived empathy and trust, and trust is what
     drives whether people stay in a tutor (Frontiers 2025, n=160). */
  .msg.bot {
    background:
      linear-gradient(150deg, rgba(255,141,196,.16), rgba(167,139,250,.11) 55%,
                              rgba(255,255,255,.05));
    border: 1px solid rgba(255,141,196,.22);
    border-bottom-left-radius: 6px;
    -webkit-backdrop-filter: blur(14px);
    backdrop-filter: blur(14px);
    box-shadow: 0 3px 14px rgba(3,6,20,.34), inset 0 1px 0 rgba(255,255,255,.15);
  }
  /* a hairline of the tutor's colour down the leading edge */
  .msg.bot::before {
    content: ''; position: absolute; inset-block: 11px; inset-inline-start: 0;
    width: 2px; border-radius: 0 2px 2px 0;
    background: linear-gradient(rgba(255,141,196,.75), rgba(167,139,250,.35));
    pointer-events: none;
  }
  /* the tutor's pink hairline down one edge, the learner's teal down the
     other: the shape of the corner already says who spoke, and this makes it
     say it in colour too */
  .msg.user::before { background: linear-gradient(rgba(45,212,191,.65), rgba(14,116,144,.35)); }

  /* Terms the tutor is pointing at. Yellow on pink glass was the weakest
     pairing on the page; this reads at a glance and stays legible on the
     user's violet bubble too. */
  .msg b, .msg strong {
    color: #ffd9ec; font-weight: 700;
    background: rgba(255,141,196,.16);
    border-radius: 5px; padding: 0 4px; margin: 0 -1px;
    box-shadow: inset 0 0 0 1px rgba(255,141,196,.28);
  }
  .msg.user b, .msg.user strong {
    color: #e8ecff; background: rgba(255,255,255,.15);
    box-shadow: inset 0 0 0 1px rgba(255,255,255,.22);
  }
  .msg.user {
    background: linear-gradient(135deg, var(--user1) 0%, var(--user2) 55%,
                                        var(--user3) 100%);
    color: #fff; border: none; border-bottom-right-radius: 6px;
    box-shadow: 0 6px 20px rgba(14,116,144,.38), inset 0 1px 0 rgba(255,255,255,.3);
  }
  .msg.rtl { direction: rtl; text-align: right; }
  /* mixed bilingual text: each line picks its own direction */
  .msg { unicode-bidi: plaintext; text-align: start; }
  .msg b, .msg strong { color: #fcd34d; font-weight: 700; }
  .msg.long { max-height: 420px; overflow-y: auto; }
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
  .mtool:hover { color: var(--text); background: rgba(255,255,255,.09);
                 border-color: rgba(255,255,255,.14); }
  .mtool.on { color: #ff8dc4; border-color: rgba(255,141,196,.4);
              background: rgba(255,141,196,.14); }
  @media (hover: none) {
    .mtool:hover { background: none; color: var(--dim); border-color: transparent; }
  }
  .msg.err { border-color: #f87171; color: #fecaca; background: #7f1d1d55; }

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
    background: linear-gradient(135deg, rgba(109,140,255,.94), rgba(167,139,250,.9));
    border: 1px solid rgba(255,255,255,.24);
    box-shadow: 0 6px 18px rgba(0,0,0,.45);
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
  .jump:focus-visible { outline: 2px solid #a8b8ff; outline-offset: 3px; }
  .jump svg { width: 17px; height: 17px; display: block; }

  /* how many replies have arrived while you were reading further up */
  .jump b {
    position: absolute; top: -3px; inset-inline-end: -3px;
    min-width: 19px; height: 19px; padding: 0 5px;
    display: grid; place-items: center;
    border-radius: 10px; font-size: 10.5px; font-weight: 700;
    background: #ff5c9d; color: #fff;
    border: 1.5px solid #101538;
    box-shadow: 0 2px 6px rgba(0,0,0,.4);
  }
  .jump b[hidden] { display: none; }

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
    background: linear-gradient(0deg, rgba(11,16,46,.55), transparent);
    flex: none;
  }
  /* The box is the field now. The input used to carry its own border, focus
     ring and background, which drew a second outline inside the first. It is
     bare now and .messageBox:focus-within does the talking. */
  #input {
    flex: 1; background: transparent; border: 0;
    padding: 0 2px; color: var(--text);
    font-size: 15.5px; outline: none; transition: .15s;
    font-family: inherit;
  }
  #input::placeholder { color: #7e8caf; }
  /* ---------- the message box ----------
     The shape is borrowed from a plain chat composer: one rounded container
     with the controls inside it rather than a row of separate pills. The
     greys are the app's own - the shell is the same glass as the panels, and
     the focus ring is the tutor's pink, so typing into it reads the same way
     as the bird answering.
  */
  .messageBox {
    display: flex; align-items: center; gap: 3px;
    padding: 3px 4px 3px 3px; border-radius: 14px;
    background: linear-gradient(180deg, rgba(255,255,255,.075), rgba(255,255,255,.035));
    border: 1px solid var(--line2);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.12);
    transition: border-color .18s, box-shadow .18s;
  }
  .messageBox:focus-within {
    border-color: rgba(255,141,196,.5);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.12), 0 0 0 3px rgba(255,141,196,.13);
  }
  .ico {
    flex: 0 0 auto; width: 36px; height: 36px; padding: 0;
    display: grid; place-items: center; border: 0; border-radius: 10px;
    background: transparent; color: var(--muted); cursor: pointer;
    transition: background .16s, color .16s, transform .16s cubic-bezier(.22,1,.36,1);
  }
  .ico svg { width: 19px; height: 19px; }
  .ico:hover { background: rgba(255,255,255,.08); color: #fff; }
  .ico:active { transform: scale(.9); }
  .ico:focus-visible { outline: 2px solid #ff8dc4; outline-offset: 2px; }
  #emojibtn[aria-expanded="true"] { background: rgba(255,141,196,.16); color: #ffc4e2; }
  .send {
    flex: 0 0 auto; width: 40px; height: 40px; padding: 0;
    display: grid; place-items: center;
    background: linear-gradient(135deg, #6d8cff 0%, #a78bfa 100%);
    border: 0; border-radius: 12px; color: #fff; cursor: pointer;
    transition: filter .15s, transform .16s cubic-bezier(.22,1,.36,1);
    /* Flat, like the other two controls in the row. The old drop shadow read
       as an outline at this size and made the button look boxed. */
    box-shadow: inset 0 1px 0 rgba(255,255,255,.22);
    font-family: inherit;
  }
  .send svg { width: 19px; height: 19px; }
  .send:hover { filter: brightness(1.12); transform: translateY(-1px); }
  .send:disabled { opacity: .55; cursor: not-allowed; transform: none; }

  /* ---------- phrases panel pills ---------- */
  .ftopic {
    background: rgba(109,140,255,.1); color: #b9c6ff;
    border: 1px solid rgba(109,140,255,.3);
    border-radius: 999px; padding: 6px 13px; font-size: 12.5px; font-weight: 500;
    cursor: pointer; transition: .15s; white-space: nowrap;
    display: inline-flex; align-items: baseline; gap: 6px;
  }
  .ftopic:hover { background: rgba(109,140,255,.24); transform: translateY(-1px); }
  .ftopic .fa { color: var(--muted); font-size: 11.5px; }

  /* ---------- word architecture: clickable chips + detail card ---------- */
  .wd-slot { margin-top: 9px; padding-top: 9px;
             border-top: 1px dashed rgba(255,255,255,.12); }
  .wd-lab {
    font-size: 10.5px; letter-spacing: .04em; color: #9fb0dd;
    font-weight: 600; margin-bottom: 6px;
  }
  .wd-lab b { color: var(--muted); font-weight: 400; }
  .wd-chips { display: flex; flex-wrap: wrap; gap: 4px; }
  .wchip {
    background: rgba(52,211,153,.1); color: #a7f3d0;
    border: 1px solid rgba(52,211,153,.28); border-radius: 7px;
    padding: 4px 9px; font-size: 11.5px; cursor: pointer;
    transition: .12s; font-family: inherit;
  }
  .wchip:hover { background: rgba(52,211,153,.24); color: #d1fae5;
                 border-color: rgba(52,211,153,.55); }
  .wchip.on { background: linear-gradient(135deg, #34d399, #6d8cff);
              color: #fff; border-color: transparent; }
  .wd-more { font-size: 10.5px; color: var(--dim); margin-top: 5px; }
  .wd-more.btn {
    background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.14);
    border-radius: 8px; padding: 5px 10px; cursor: pointer;
    font-family: inherit; color: var(--muted);
  }
  .wd-more.btn:hover { background: rgba(255,255,255,.12); color: var(--text); }

  .wdetail {
    display: none; margin-bottom: 11px; padding: 12px;
    border-radius: 13px; position: relative;
    background: linear-gradient(150deg, rgba(52,211,153,.14), rgba(109,140,255,.10));
    border: 1px solid rgba(52,211,153,.34);
    box-shadow: 0 6px 20px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.14);
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
    background: rgba(255,255,255,.14); color: #d7e2ff;
  }
  .wd-close {
    background: none; border: none; color: var(--dim); cursor: pointer;
    font-size: 14px; padding: 4px 6px; border-radius: 6px; line-height: 1;
    font-family: inherit;
  }
  .wd-close:hover { color: var(--text); background: rgba(255,255,255,.1); }
  .wd-mean {
    font-size: 14px; line-height: 1.6; margin: 7px 0 4px; color: var(--text);
  }
  .wd-mean b { color: #6ee7b7; }
  .wd-forms {
    display: grid; grid-template-columns: 1fr; gap: 4px; margin-top: 5px;
  }
  .wd-form {
    display: flex; align-items: baseline; gap: 8px;
    padding: 6px 9px; border-radius: 8px;
    background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.1);
  }
  .wd-form b {
    font-family: "SF Mono", Consolas, "DejaVu Sans Mono", monospace;
    font-size: 13px; color: #fcd34d; font-weight: 700; flex: none;
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

  /* ---------- review: saved words + flashcards ---------- */
  /* Inside the tile. A negative offset puts it outside a 46px button, and
     being a span it then inherits .hbtn span's overflow:hidden and is clipped
     in half - a sliver on the edge rather than a badge. */
  .rbadge {
    position: absolute; top: 3px; inset-inline-end: 3px; z-index: 1;
    display: inline-flex; align-items: center; justify-content: center;
    min-width: 15px; height: 15px; padding: 0 3px; border-radius: 999px;
    font-size: 9px; font-weight: 800; line-height: 1; color: #3a2400;
    background: #ffc44d; border: 1px solid rgba(11,16,46,.55);
    box-shadow: 0 1px 3px rgba(0,0,0,.35);
    /* .hbtn span sets ellipsis and a nowrap overflow; a number needs neither */
    text-overflow: clip; max-width: none;
  }
  .rbadge[hidden] { display: none; }
  .rtop { display: flex; align-items: center; gap: 7px; flex-wrap: wrap; margin-bottom: 10px; }
  .rprog {
    flex: 1 1 120px; height: 7px; border-radius: 999px; overflow: hidden;
    background: rgba(255,255,255,.09); border: 1px solid rgba(255,255,255,.12);
  }
  .rprog i {
    display: block; height: 100%; border-radius: 999px;
    background: linear-gradient(90deg, #34d399, #6d8cff);
    transition: width .35s cubic-bezier(.34,1.3,.64,1);
  }
  .rcount { font-size: 11.5px; color: var(--muted); white-space: nowrap; }
  .rtab {
    background: rgba(255,255,255,.07); color: var(--muted);
    border: 1px solid rgba(255,255,255,.14); border-radius: 8px;
    padding: 5px 11px; font-size: 11.5px; cursor: pointer;
    font-family: inherit; transition: .12s;
  }
  .rtab.on { background: linear-gradient(135deg, #34d399, #6d8cff); color: #fff; border-color: transparent; }
  .rtab:hover { color: var(--text); }
  .rtab.on:hover { color: #fff; }
  .rdanger:hover { background: rgba(248,113,113,.25); border-color: rgba(248,113,113,.5); }

  /* flashcard */
  .rcard {
    padding: 18px 14px 14px; border-radius: 15px; text-align: center;
    background: linear-gradient(155deg, rgba(255,255,255,.10), rgba(255,255,255,.03));
    border: 1px solid rgba(255,255,255,.14);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.14), 0 8px 24px rgba(0,0,0,.28);
    min-height: 176px; display: flex; flex-direction: column;
    justify-content: center; gap: 8px;
  }
  .rcard .rword { font-size: 26px; font-weight: 700; letter-spacing: .2px; line-height: 1.2; }
  .rcard .rpos {
    align-self: center; font-size: 10px; font-weight: 700; padding: 2px 8px;
    border-radius: 999px; background: rgba(255,255,255,.13); color: #d7e2ff;
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
    margin-top: 4px; background: none; border: 1px dashed rgba(255,255,255,.28);
    color: var(--muted); border-radius: 9px; padding: 7px 12px; font-size: 12px;
    cursor: pointer; font-family: inherit;
  }
  .rflip:hover { background: rgba(255,255,255,.08); color: var(--text); }
  .racts { display: flex; gap: 8px; margin-top: 11px; }
  .rbtn {
    flex: 1; min-height: 44px; border-radius: 11px; cursor: pointer;
    font-family: inherit; font-size: 13px; font-weight: 700;
    border: 1px solid rgba(255,255,255,.14); color: #fff;
  }
  .rbtn.know { background: linear-gradient(135deg, #34d399, #10b981); }
  .rbtn.again { background: linear-gradient(135deg, #fb923c, #f43f5e); }
  .rbtn.play { background: rgba(255,255,255,.1); flex: 0 0 52px; font-size: 16px;
               line-height: 1; padding: 0; }
  .rbtn:hover { filter: brightness(1.1); }
  .rdots { display: flex; gap: 3px; justify-content: center; margin-top: 10px; flex-wrap: wrap; }
  .rdot { width: 6px; height: 6px; border-radius: 50%; background: rgba(255,255,255,.2); }
  .rdot.on { background: #34d399; }
  .rdot.now { background: #ffc44d; transform: scale(1.5); }

  /* list mode */
  .rlist { display: flex; flex-direction: column; gap: 6px; }
  .rrow {
    display: grid; grid-template-columns: 1fr auto auto; gap: 9px; align-items: center;
    padding: 8px 10px; border-radius: 10px;
    background: linear-gradient(150deg, rgba(255,255,255,.06), rgba(255,255,255,.02));
    border: 1px solid rgba(255,255,255,.1);
  }
  .rrow .rmain { min-width: 0; }
  .rrow .ren { font-size: 13.5px; font-weight: 600; }
  .rrow .rfa2 { font-size: 11.5px; color: var(--muted); margin-top: 1px; }
  .rrow.ok { border-color: rgba(52,211,153,.4); }
  .rrow.ok .ren::after { content: ' \2713'; color: #34d399; }
  .ricon {
    width: 30px; height: 30px; border-radius: 8px; border: 1px solid rgba(255,255,255,.14);
    background: rgba(255,255,255,.07); color: var(--text); font-size: 13px;
    cursor: pointer; display: grid; place-items: center; font-family: inherit;
  }
  .ricon:hover { background: rgba(255,255,255,.14); }
  .ricon.del:hover { background: rgba(248,113,113,.25); border-color: rgba(248,113,113,.5); }
  .rempty { text-align: center; padding: 26px 10px; color: var(--muted); font-size: 13px; line-height: 1.7; }
  .rempty .big { font-size: 30px; display: block; margin-bottom: 8px; }

  /* the "save to review" toggle inside the word card */
  .rstar {
    background: rgba(255,196,77,.14); border: 1px solid rgba(255,196,77,.34);
    color: #fcd34d; border-radius: 9px; padding: 6px 11px; font-size: 12px;
    cursor: pointer; font-family: inherit; font-weight: 600;
  }
  .rstar:hover { background: rgba(255,196,77,.26); }
  .rstar.on { background: linear-gradient(135deg, #ffc44d, #fb923c); color: #3a2400; border-color: transparent; }
  .wd-star { margin-top: 10px; display: flex; gap: 7px; align-items: center; flex-wrap: wrap; }
  .wd-star .why { font-size: 11px; color: var(--dim); }

  /* ---------- phonetics: topic rail + dense symbol cards ----------
     Designed so a whole lesson fits on one phone screen: the rail is one
     scroll line, rows are a single column, and every ▶ speaks the example. */
  .phrail {
    display: flex; gap: 6px; overflow-x: auto; padding: 2px 0 9px;
    margin-bottom: 4px; border-bottom: 1px solid rgba(255,255,255,.1);
    -webkit-overflow-scrolling: touch; overscroll-behavior-x: contain;
    scrollbar-width: none;
  }
  .phrail::-webkit-scrollbar { display: none; }
  .phtab {
    flex: none; display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255,255,255,.06); color: var(--muted);
    border: 1px solid rgba(255,255,255,.14); border-radius: 999px;
    padding: 6px 12px; font-size: 12px; font-weight: 600;
    cursor: pointer; transition: .14s; font-family: inherit; white-space: nowrap;
  }
  .phtab i {
    font-style: normal; font-size: 9px; font-weight: 800; letter-spacing: .04em;
    padding: 2px 5px; border-radius: 5px;
    background: rgba(255,255,255,.1); color: #a9b8de;
  }
  .phtab:hover { background: rgba(255,255,255,.12); color: var(--text); }
  .phtab.on {
    background: linear-gradient(135deg, #ff8dc4, #a78bfa);
    color: #fff; border-color: transparent;
    box-shadow: 0 4px 14px rgba(255,141,196,.4);
  }
  .phtab.on i { background: rgba(0,0,0,.22); color: #fff; }

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
    background: linear-gradient(135deg, rgba(109,140,255,.35), rgba(167,139,250,.3));
    color: #dbe2ff; border: 1px solid rgba(109,140,255,.4);
  }
  .phead .ptitle .pfa { font-size: 13px; color: var(--muted); font-weight: 500; }
  .pblurb {
    font-size: 12.5px; line-height: 1.65; color: var(--muted); margin-top: 6px;
  }

  .ptip {
    display: flex; gap: 9px; align-items: flex-start;
    padding: 10px 12px; margin-bottom: 14px; border-radius: 12px;
    background: linear-gradient(135deg, rgba(255,196,77,.14), rgba(255,141,196,.08));
    border: 1px solid rgba(255,196,77,.28);
  }
  .ptip .pk { font-size: 14px; line-height: 1.3; flex: none; }
  .ptip .pt { font-size: 12.5px; line-height: 1.6; color: #ffe6b0; }
  .ptip .pt b { color: #fff; }

  .pgroup { margin-bottom: 14px; }
  .pgroup:last-child { margin-bottom: 0; }
  .pgroup > .ghead {
    font-size: 10.5px; letter-spacing: .06em; text-transform: uppercase;
    color: #9fb0dd; font-weight: 700; margin-bottom: 7px;
  }
  .pgroup > .ghead .fa {
    color: #7f8fbd; text-transform: none; letter-spacing: 0; font-weight: 400;
  }
  .prows {
    display: grid; grid-template-columns: 1fr; gap: 7px;
  }
  .prow {
    display: grid; grid-template-columns: 1fr auto; gap: 10px; align-items: center;
    padding: 9px 11px; border-radius: 11px;
    background: linear-gradient(150deg, rgba(255,255,255,.07), rgba(255,255,255,.025));
    border: 1px solid rgba(255,255,255,.1);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.09);
  }
  .prow:hover { background: rgba(255,255,255,.1); border-color: rgba(255,141,196,.32); }
  .pmain { min-width: 0; }
  .pip {
    font-family: "SF Mono", "Cascadia Mono", Consolas, "DejaVu Sans Mono", monospace;
    font-size: 13.5px; font-weight: 700; color: #ffc4e2;
    word-break: break-word; line-height: 1.35;
  }
  .psub { font-size: 11px; color: #a9b8de; margin-top: 1px; line-height: 1.4; }
  .psay { font-size: 13px; color: var(--text); margin-top: 3px; line-height: 1.45; }
  .pfa { font-size: 12px; color: var(--muted); margin-top: 2px; line-height: 1.55; }
  .pwords {
    font-size: 11px; color: #8a97bb; margin-top: 3px; line-height: 1.5;
    font-family: "SF Mono", Consolas, "DejaVu Sans Mono", monospace;
  }
  .pnote {
    font-size: 11px; color: #ffd6a0; margin-top: 4px; line-height: 1.5;
    padding-inline-start: 13px; position: relative;
  }
  .pnote::before { content: '💡'; position: absolute; inset-inline-start: 0; font-size: 10px; }
  .pplay {
    width: 34px; height: 34px; flex: none; border-radius: 50%;
    background: linear-gradient(135deg, #ff8dc4, #a78bfa); border: none;
    color: #fff; font-size: 12px; cursor: pointer;
    display: grid; place-items: center; transition: .12s;
    box-shadow: 0 3px 10px rgba(255,141,196,.35);
  }
  .pplay:hover { filter: brightness(1.12); transform: scale(1.06); }
  .pplay.playing { background: linear-gradient(135deg, #34d399, #6d8cff); }

  @media (min-width: 600px) {
    .prows { grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 8px; }
    .phead .ptitle { font-size: 17.5px; }
    .pblurb, .ptip .pt { font-size: 13px; }
    .phtab { padding: 7px 14px; font-size: 12.5px; }
    .pplay { width: 36px; height: 36px; }
  }

  /* ---------- everyday-sentence cards ----------
     A phrase bank used to arrive as one run-on pre-wrap block, so the
     translations collided. Each "• en / ↳ fa" pair is its own card now. */
  .msg.plist { white-space: normal; padding: 12px; }
  .msg.plist .plist-head {
    font-size: 14px; font-weight: 700; color: #ffc4e2;
    padding: 2px 4px 10px; margin-bottom: 8px;
    border-bottom: 1px solid rgba(255,255,255,.12);
  }
  .pcard {
    display: flex; flex-direction: column; gap: 3px;
    padding: 10px 12px; margin-bottom: 7px;
    border-radius: 12px;
    background: linear-gradient(150deg, rgba(255,255,255,.085), rgba(255,255,255,.03));
    border: 1px solid rgba(255,255,255,.11);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.1);
  }
  .pcard:last-child { margin-bottom: 0; }
  .pcard .pen { font-size: 14px; line-height: 1.5; color: var(--text); }
  .pcard .pen::before {
    content: '▸'; color: #ff8dc4; font-size: 11px; margin-inline-end: 7px;
    vertical-align: 1px;
  }
  .pcard .pfa { font-size: 13px; line-height: 1.6; color: var(--muted); }
  .pcard .pfa::before {
    content: '↳'; color: #7f8fbd; font-size: 11px; margin-inline-end: 7px;
  }
  @media (min-width: 600px) {
    .msg.plist { padding: 14px 16px; }
    .pcard { padding: 11px 14px; margin-bottom: 8px; }
    .pcard .pen { font-size: 14.5px; }
    .pcard .pfa { font-size: 13.5px; }
  }

  /* ---------- graceful fallback where backdrop-filter is unsupported ---------- */
  @supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
    .app { background: linear-gradient(160deg, #141c46, #1b2350); }
    header { background: linear-gradient(100deg, #24306b, #2a2170); }
    #vpanel, #gpanel, #fpanel, #phpanel, #rpanel { background: #131a3d; }
    .msg.bot { background: #1c2450; }
    #input { background: #141c46; }
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
  header h1 { font-size: 16px; }
  .avatar { width: 42px; height: 42px; border-radius: 14px; }
  .avatar svg { width: 34px; height: 34px; }
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
  /* 38x40, not 44x46: still well past the 24px WCAG 2.5.8 minimum, and
     seven of them plus gaps now fit without a scroll on a 360dp phone. */
  .hbtn { width: 38px; height: 40px; border-radius: 10px; padding: 3px 0; }
  .hbtn i { font-size: 14px; }
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

  /* ---- panels: nearly full height, edge-to-edge, own scroll area ---- */
  #vpanel, #gpanel, #fpanel, #lpanel, #phpanel, #rpanel {
    padding: 10px calc(var(--pad) + var(--sar)) 11px calc(var(--pad) + var(--sal));
    max-height: 66%;
    overscroll-behavior: contain;
    -webkit-overflow-scrolling: touch;
  }
  #vpanel h3, #gpanel h3, #fpanel h3, #lpanel h3, #phpanel h3, #rpanel h3 {
    font-size: 11.5px; margin-bottom: 8px; line-height: 1.5;
  }
  .domains { max-height: 46vh; }

  /* every tappable pill in a panel gets a real touch target */
  .vbtn, .gbtn, .ftopic, .ltab {
    min-height: 32px; padding: 6px 11px; font-size: 12px;
  }
  .gbtn { padding: 0; }
  .gmain { padding: 6px 3px 6px 10px; font-size: 12px; min-height: 32px; }
  .go { padding: 0 12px; font-size: 13px; }
  .go.exam {
    background: rgba(255,196,77,.14); color: #fcd34d;
    border-left-color: rgba(255,196,77,.34);
  }
  .go.exam:not(.locked):hover { background: rgba(255,196,77,.34); }
  .go.exam.locked {
    background: rgba(148,163,184,.12); color: #8a97bb;
    border-left-color: rgba(148,163,184,.26);
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
  .mav svg { width: 20px; height: 20px; }
  /* font-size deliberately unchanged: denser, not smaller to read */
  .msg { padding: 9px 12px; font-size: 15px; border-radius: 14px; }
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
    height: 3px; border-radius: 2px; background: rgba(255,255,255,.09);
  }
  /* how much of the day is spent */
  .limitfill {
    position: absolute; left: 0; top: 8px; height: 3px; border-radius: 2px;
    width: calc(var(--p, 0) * (100% - 20px) + 10px);
    background: linear-gradient(90deg, rgba(109,140,255,.85), rgba(167,139,250,.85));
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
    color: #9fb0ef;
  }
  .limitxt:empty { display: none; }

  .limitenote.warn .limitfill {
    background: linear-gradient(90deg, rgba(167,139,250,.9), rgba(255,141,196,.9));
  }
  .limitenote.warn .lockic { filter: none; }
  .limitenote.warn .limitxt { color: #e9c6ff; }

  .limitenote.full .limitfill {
    background: linear-gradient(90deg, rgba(255,141,196,.95), rgba(255,92,157,.95));
  }
  .limitenote.full .lockic { filter: none; }
  .limitenote.full {
    padding: 9px 12px; border-radius: 11px;
    background: linear-gradient(135deg, rgba(167,139,250,.18), rgba(255,141,196,.10));
    border: 1px solid rgba(167,139,250,.34);
    animation: fade .2s ease;
  }
  .limitenote.full .limitrail { height: 14px; }
  .limitenote.full .limitfill { top: 6px; height: 3px; }
  .limitenote.full .lockic { top: -4px; }
  .limitenote b { color: #fff; }
  form.locked #input {
    opacity: .45; cursor: not-allowed; background: rgba(255,255,255,.03);
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
  /* The mic used to be an emoji on a #141c46 disc with a #3a4a86 ring -
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
    color: #dbe3ff; background: #29356e;
    border: 0;
    box-shadow: 0 2px 10px rgba(4, 8, 26, .5), inset 0 1px 0 rgba(255, 255, 255, .16);
    transition: background .18s, color .18s, transform .1s, box-shadow .18s;
  }
  .mic svg { width: 19px; height: 19px; display: block; }
  .mic svg * { stroke: currentColor; }
  /* The outline used to carry every state - default, hover, listening,
     unavailable - so removing it is not just deleting a line: each of those
     states now has to be legible from the fill alone. They are, because the
     fills differ in hue, not just in brightness. */
  .mic:hover {
    background: #3a4b93; color: #fff;
    box-shadow: 0 4px 16px rgba(4, 8, 26, .6), inset 0 1px 0 rgba(255, 255, 255, .22);
  }
  .mic:focus-visible { outline: 2px solid #a8b8ff; outline-offset: 2px; }
  .mic:active { transform: scale(.94); }
  /* Teal, not pink. Pink is the tutor; when the mic pulses in the tutor's
     own colour it reads as though the app is talking at you. */
  .mic.rec {
    background: #0f766e; color: #fff;
    box-shadow: 0 2px 10px rgba(4, 8, 26, .5), 0 0 0 1px rgba(94, 234, 212, .35);
    animation: micPulse 1.4s ease-out infinite;
  }
  .mic.rec svg { transform: scale(1.06); }
  /* aria-disabled, not disabled: a disabled button swallows its own click
     events, so on touch the control would sit there doing nothing and the
     explanation in its title would be unreachable. aria-disabled announces
     the state to a screen reader while leaving the tap working. */
  .mic[aria-disabled="true"] {
    background: #1e2748; color: #8794c9;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, .05);
  }
  .mic[aria-disabled="true"]:hover {
    background: #26314f; color: #a7b3e0;
  }
  /* a hint, once, so the button is noticed rather than rediscovered */
  @keyframes micHint {
    0%, 100% { box-shadow: 0 2px 10px rgba(4,8,26,.5), 0 0 0 0 rgba(168,184,255,.5); }
    60%      { box-shadow: 0 2px 10px rgba(4,8,26,.5), 0 0 0 9px rgba(168,184,255,0); }
  }
  .mic.hint { animation: micHint 2.6s ease-out 3; }
  @keyframes micPulse {
    0%   { box-shadow: 0 0 0 0 rgba(255, 111, 156, .55); }
    100% { box-shadow: 0 0 0 16px rgba(255, 111, 156, 0); }
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
    background: rgba(20, 28, 70, .82); border: 1px solid #33427c;
    border-radius: 14px; color: #b9c6ff;
  }
  .stt-panel[hidden] { display: none; }
  .stt-dot {
    width: 9px; height: 9px; border-radius: 50%; background: #ff6f9c;
    flex: 0 0 9px; animation: micBlink 1.1s ease-in-out infinite;
  }
  @keyframes micBlink { 0%, 100% { opacity: 1; } 50% { opacity: .25; } }
  .stt-label { color: #8fa2e8; font-size: 12.5px; }
  .stt-interim { color: #9fb0ef; font-style: italic; }
  .stt-final { color: #fff; }

  /* ------------------------------------------------ BBC listening ------- */
  .bbc-open {
    display: block; width: 100%; margin-bottom: 10px; padding: 11px 14px;
    border-radius: 13px; border: 1px solid #3a4a86; background: #141c46;
    color: #cfd8ff; font-size: 13.5px; text-align: left; cursor: pointer;
  }
  .bbc-open:hover { border-color: #6f86d6; }
  .bbc-head { display: flex; flex-direction: column; gap: 7px; margin-bottom: 10px; }
  .bbc-back {
    align-self: flex-start; min-height: 40px; padding: 8px 13px; border-radius: 11px;
    border: 1px solid #3a4a86; background: #141c46; color: #cfd8ff;
    font-size: 12.5px; cursor: pointer;
  }
  .bbc-note { font-size: 12px; color: #8fa2e8; line-height: 1.5; }
  .bbc-tabs { display: flex; gap: 6px; overflow-x: auto; padding-bottom: 9px; }
  .bbc-tab {
    flex: 0 0 auto; padding: 6px 12px; border-radius: 999px; font-size: 12.5px;
    border: 1px solid #33427c; background: transparent; color: #b9c6ff; cursor: pointer;
  }
  .bbc-tab.on { background: #27356e; border-color: #6f86d6; color: #fff; }
  .bbc-list { display: flex; flex-direction: column; gap: 9px; }
  .bbc-row {
    padding: 12px 14px; border-radius: 14px; background: #141c46;
    border: 1px solid #2b3768;
  }
  .bbc-row-head { display: flex; gap: 9px; align-items: baseline; }
  .bbc-lvl {
    flex: 0 0 auto; font-size: 11px; font-weight: 700; padding: 2px 8px;
    border-radius: 999px; background: #27356e; color: #cfd8ff;
  }
  .bbc-lvl.lvl-A2 { background: #1f4a3d; color: #a8f0cd; }
  .bbc-lvl.lvl-B1 { background: #1e4470; color: #a8d4ff; }
  .bbc-lvl.lvl-B2 { background: #4a3a72; color: #dcc4ff; }
  .bbc-lvl.lvl-C1 { background: #6e2b4c; color: #ffc4dd; }
  .bbc-lvl.lvl-none { background: #33385c; color: #9aa3cc; }
  .bbc-title { font-size: 14.5px; color: #fff; font-weight: 600; }
  .bbc-blurb { margin-top: 5px; font-size: 12.5px; color: #9fb0ef; line-height: 1.5; }
  .bbc-meta { margin-top: 6px; font-size: 11.5px; color: #7d8fd4; }
  .bbc-actions { display: flex; gap: 7px; margin-top: 9px; flex-wrap: wrap; align-items: center; }
  .bbc-play {
    padding: 8px 14px; min-height: 40px; border-radius: 11px; font-size: 13px;
    border: 1px solid #6f86d6; background: #27356e; color: #fff; cursor: pointer;
  }
  .bbc-play.on { background: #7d2b52; border-color: #ff6f9c; }
  .bbc-play.nofile { background: #2a2f52; border-color: #4a5a92; color: #a9b7ef; }
  .bbc-play.nofile:hover { border-color: #7f92d8; color: #dfe6ff; }
  .bbc-link { font-size: 12px; color: #9fb0ef; text-decoration: none; padding: 6px 4px; }
  .bbc-link:hover { color: #fff; text-decoration: underline; }
  .bbc-empty { font-size: 12px; color: #7d8fd4; padding: 4px 2px; }
  /* 40, not 46: this min-height was the floor for the whole composer row,
     input and mic included, so the button set the height of the form. */
  .send { width: 36px; height: 36px; border-radius: 10px; }

  /* ---------- tablets: two comfortable columns ---------- */
  @media (min-width: 600px) {
    :root { --pad: 18px; }
    .app { border-radius: 22px; border: 1px solid rgba(255,255,255,.14); }
    body { padding: 16px; align-items: center; justify-content: center; }
    .app { height: min(94vh, 980px); width: min(1180px, 100%); }
    .app::after { left: 12%; right: 12%; }
    header { padding: 14px 20px; flex-wrap: nowrap; }
    header h1 { font-size: 17.5px; }
    .avatar { width: 46px; height: 46px; border-radius: 15px; }
    .avatar svg { width: 38px; height: 38px; }
    .tools { order: 0; width: auto; margin: 0; padding: 0; overflow: visible; }
    .hbtn { width: 48px; height: 48px; }
    .hbtn i { font-size: 16px; }
    .hbtn span { font-size: 8.5px; }
    #chat { padding: 20px 22px 10px; gap: 16px; }
    .bubble-wrap { max-width: 80%; }
    .mav { width: 32px; height: 32px; border-radius: 11px; }
    .mav svg { width: 26px; height: 26px; }
    .msg { padding: 12px 16px; font-size: 15px; }
    #vpanel, #gpanel, #fpanel, #lpanel, #phpanel, #rpanel { padding: 14px 20px; max-height: 52%; }
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
      rgba(255,255,255,.30) 50%, transparent 70%);
    transform: translate3d(-120%, 0, 0);
  }
  .row.bot .msg.bot::after { animation: sheen .85s .16s ease-out; }

  /* ---------- 3. the bird -------------------------------------------
     Idle: a slow breath. Blink: the eye squashes. Speaking: the whole
     bird pulses on the beat of whatever is being read aloud. */
  @keyframes breathe {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    50%      { transform: translateY(-2px) rotate(-1.2deg); }
  }
  @keyframes blink {
    0%, 92%, 100% { transform: scaleY(1); }
    95%           { transform: scaleY(.08); }
  }
  @keyframes talkPulse {
    0%, 100% { transform: scale(1); }
    50%      { transform: scale(1.09); }
  }
  .mav.bot { animation: breathe 4.2s ease-in-out infinite; }
  .mav.bot svg .eye,
  .mav.bot svg [class~="eye"] { transform-origin: center; animation: blink 5.5s infinite; }
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
    background: linear-gradient(90deg, #6d8cff, #ff8dc4, #6d8cff);
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
    background: radial-gradient(circle, rgba(255,255,255,.55), rgba(255,255,255,0) 70%);
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
    background-image: linear-gradient(100deg, #27356e 20%, #4d63b8 45%, #27356e 70%);
    background-size: 220% 100%;
    animation: pillShimmer 4.6s ease-in-out infinite;
  }
  .bbc-lvl.lvl-A1 { background-image: linear-gradient(100deg,#1f4a3d,#3f9c76,#1f4a3d); background-size:220% 100%; }
  .bbc-lvl.lvl-A2 { background-image: linear-gradient(100deg,#1e4470,#3f86d9,#1e4470); background-size:220% 100%; }
  .bbc-lvl.lvl-B1 { background-image: linear-gradient(100deg,#3a2a6b,#8a6ae0,#3a2a6b); background-size:220% 100%; }
  .bbc-lvl.lvl-B2 { background-image: linear-gradient(100deg,#5a2a63,#c06ae0,#5a2a63); background-size:220% 100%; }
  .bbc-lvl.lvl-C1 { background-image: linear-gradient(100deg,#6e2b4c,#ff6f9c,#6e2b4c); background-size:220% 100%; }
  .bbc-lvl { animation: pillShimmer 7s ease-in-out infinite; }

  /* ---------- 8. audio ----------------------------------------------
     While something is playing: bars in the play button and the speak
     tool, and a conic ring on the track button for real progress. */
  @keyframes eq { 0%,100% { transform: scaleY(.3); } 50% { transform: scaleY(1); } }
  /* the 🔊 tool glows while it is the thing making noise */
  @keyframes speakGlow {
    0%, 100% { box-shadow: 0 0 0 0 rgba(255,111,156,.0); }
    50%      { box-shadow: 0 0 0 4px rgba(255,111,156,.22); }
  }
  .mtool.on { animation: speakGlow 1.5s ease-in-out infinite; }

  .playing, .bbc-play.on {
    position: relative;
  }
  .playing::before, .bbc-play.on::before {
    content: ''; position: absolute; inset: -1px; border-radius: inherit;
    background: conic-gradient(from -90deg, #ff6f9c var(--p, 0turn), transparent 0);
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
    background: linear-gradient(140deg, rgba(52,66,138,.97), rgba(30,39,86,.97));
    border: 1px solid #6f86d6; color: #e6ebff;
    font-size: 13px; line-height: 1.5; text-align: center;
    box-shadow: 0 14px 40px rgba(3, 6, 20, .6);
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
    .eqbar i, .mtool.on { animation: none !important; }
    button, .ltab, .bbc-tab, .lrow { transition: none !important; }
    * { scroll-behavior: auto !important; }
  }
</style>
</head>
<body>
<div class="boot" id="boot" role="status" aria-live="polite"
     aria-label="Loading Fluentify / در حال بارگذاری">
    <div class="boot-in">
      <svg class="boot-bird" viewBox="0 0 48 48" aria-hidden="true">
        <defs>
          <linearGradient id="bootBirdG" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stop-color="#ffc2e2"/><stop offset="55%" stop-color="#ff8dc4"/>
            <stop offset="100%" stop-color="#ff5c9d"/></linearGradient>
        </defs>
        <path d="M10 27 L3.5 20 L5.5 31 Z" fill="#ff5c9d"/>
        <ellipse cx="23" cy="27" rx="16" ry="13.5" fill="url(#bootBirdG)"/>
        <path d="M21.5 13.5 q1-6.5 4.5-6.5 q-1.2 4-2 6 q2.8-4 6-3 q-2 3-4.5 4.2Z" fill="#ff9ccb"/>
        <path d="M36 22.5 L42.5 25.5 L36 28.5 Z" fill="#ffc44d"/>
        <circle cx="31" cy="21.5" r="3.3" fill="#4a1030"/>
        <circle cx="32.3" cy="20.3" r="1.15" fill="#fff"/>
      </svg>
      <div class="loader" aria-hidden="true"></div>
      <div class="boot-track" aria-hidden="true"><i id="bootfill"></i></div>
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
      <svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="bodyGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stop-color="#ffc2e2"/>
            <stop offset="55%" stop-color="#ff8dc4"/>
            <stop offset="100%" stop-color="#ff5c9d"/>
          </linearGradient>
          <linearGradient id="bellyGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#fff6fb"/>
            <stop offset="100%" stop-color="#ffd9ec"/>
          </linearGradient>
        </defs>
        <!-- tail feathers -->
        <path d="M10 27 L3.5 20 L5.5 31 Z" fill="#ff5c9d"/>
        <!-- body -->
        <ellipse cx="23" cy="27" rx="16" ry="13.5" fill="url(#bodyGrad)"/>
        <!-- belly -->
        <ellipse cx="23" cy="30.5" rx="9.5" ry="7.5" fill="url(#bellyGrad)" opacity=".92"/>
        <!-- wing -->
        <path d="M13 23.5 q8.5 2.5 8.5 10.5 q-8.5-2.5-8.5-10.5Z" fill="#ff6fae"/>
        <!-- head tuft -->
        <path d="M21.5 13.5 q1-6.5 4.5-6.5 q-1.2 4-2 6 q2.8-4 6-3 q-2 3-4.5 4.2Z" fill="#ff9ccb"/>
        <!-- beak -->
        <path d="M36 22.5 L42.5 25.5 L36 28.5 Z" fill="#ffc44d"/>
        <!-- eye -->
        <circle cx="31" cy="21.5" r="3.3" fill="#4a1030"/>
        <circle cx="32.3" cy="20.3" r="1.15" fill="#fff"/>
        <!-- blush -->
        <ellipse cx="34.5" cy="27.5" rx="3.2" ry="2.1" fill="#ff4f93" opacity=".4"/>
      </svg>
    </div>
    <div>
      <h1>Fluentify</h1>
    </div>
    <div class="spacer"></div>
    <div id="seedmeter" title="Daily seed"></div>
    <div class="status"><i></i> online</div>
    <nav class="tools" aria-label="Study panels">
      <button class="hbtn" id="vtoggle" aria-expanded="false" title="Vocabulary — واژگان" aria-label="Vocabulary">
        <i>📚</i><span>Vocab</span></button>
      <button class="hbtn" id="gtoggle" aria-expanded="false" title="Grammar — گرامر" aria-label="Grammar">
        <i>📘</i><span>Grammar</span></button>
      <button class="hbtn" id="ftoggle" aria-expanded="false" title="Sentences — جملات کاربردی" aria-label="Say — everyday sentences / جملات کاربردی">
        <i>💬</i><span>Say</span></button>
      <button class="hbtn" id="ltoggle" aria-expanded="false" title="Listening A1–C2 — شنیدن" aria-label="Listening">
        <i>🎧</i><span>Listen</span></button>
      <button class="hbtn" id="phtoggle" aria-expanded="false" title="Phonetics — تلفظ و آهنگ" aria-label="Sounds — pronunciation and rhythm / تلفظ و آهنگ">
        <i>🗣</i><span>Sounds</span></button>
      <button class="hbtn" id="rtoggle" aria-expanded="false" title="Review saved words — واژه‌های مرور" >
        <i>⭐</i><span>Review</span><span class="rbadge" id="rbadge" hidden>0</span></button>
      <button class="hbtn danger" id="clear" title="Clear conversation — پاک کردن گفتگو" aria-label="Clear conversation">
        <i>🗑</i><span>Clear</span></button>
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

  <div id="vpanel">
    <h3>Vocabulary A1 → C2 — روی هر دسته کلیک کنید تا واژه‌ها را ببینید</h3>
    <div class="psearch">
      <input id="vsearch" type="search" placeholder="Search 56 domains… / جست‌وجوی دسته‌ها…"
             autocomplete="off" aria-label="Search vocabulary domains">
    </div>
    <div class="domains" id="domains"></div>
    <div class="pempty" id="vempty" hidden>No domain matches that search. / دسته‌ای با این جست‌وجو پیدا نشد.</div>
  </div>

  <div id="gpanel">
    <h3>English grammar lessons &amp; practice — درس‌ها و تمرین‌های گرامر انگلیسی (کلیک = درس · ✏️ = تمرین)</h3>
    <div class="domains" id="gtopics"></div>
  </div>

  <div id="fpanel">
    <h3>Everyday sentences A1 → C2 — جملات کاربردی روزمره</h3>
    <div class="wdetail" id="wdetail" aria-live="polite"></div>
    <div class="domains" id="ftopics"></div>
  </div>

  <div id="lpanel">
    <h3>Listening practice A1 → C2 — گوش دادن و تلفظ</h3>
    <div id="llevels"></div>
  </div>

  <div id="phpanel">
    <h3>The sounds that make English fluent — صداهایی که انگلیسی را روان می‌کنند</h3>
    <div class="phrail" id="phrail" role="tablist" aria-label="Pronunciation topics"></div>
    <div class="phview" id="phview"></div>
  </div>

  <div id="rpanel">
    <h3>Your review list — واژه‌هایی که برای مرور ذخیره کردی</h3>
    <div class="rtop" id="rtop"></div>
    <div class="rbody" id="rbody"></div>
  </div>

  <div class="chatwrap">
    <div id="chat" role="log" aria-live="polite"
         aria-relevant="additions" aria-label="Conversation"></div>
    <button id="jump" class="jump" aria-label="Scroll to the latest message"
            title="Latest ↓"><svg viewBox="0 0 16 16" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round"
            stroke-linejoin="round" aria-hidden="true"><path d="M8 3v10M3.5 8.5L8 13l4.5-4.5"/></svg><b id="jumpn" hidden></b></button>
  </div>

  <div class="stt-panel" id="stt" hidden></div>
  <form id="composer">
    <div class="messageBox" id="messageBox">
      <button type="button" class="ico" id="emojibtn"
              aria-label="Emoji / ایموجی" title="Emoji / ایموجی"
              aria-haspopup="dialog" aria-expanded="false" aria-controls="emojipanel">
        <svg viewBox="0 0 24 24" aria-hidden="true" fill="none">
          <circle cx="12" cy="12" r="8.6" stroke="currentColor" stroke-width="1.7"/>
          <circle cx="9.2" cy="10.1" r="1.1" fill="currentColor"/>
          <circle cx="14.8" cy="10.1" r="1.1" fill="currentColor"/>
          <path d="M8.3 14.1a4.5 4.5 0 0 0 7.4 0" stroke="currentColor"
                stroke-width="1.7" stroke-linecap="round"/>
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
    <div id="emojipanel" class="emoji-panel" role="dialog"
         aria-label="Emoji picker / انتخاب ایموجی" hidden></div>
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
/* Fluentify's mascot — a cute pink bird (shared by the header and messages) */
const BIRD =
  '<svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' +
  '<defs>' +
  '<linearGradient id="bgA" x1="0" y1="0" x2="1" y2="1">' +
  '<stop offset="0" stop-color="#ffc2e2"/><stop offset="55%" stop-color="#ff8dc4"/>' +
  '<stop offset="100%" stop-color="#ff5c9d"/></linearGradient>' +
  '<linearGradient id="blA" x1="0" y1="0" x2="0" y2="1">' +
  '<stop offset="0" stop-color="#fff6fb"/><stop offset="100%" stop-color="#ffd9ec"/>' +
  '</linearGradient></defs>' +
  '<path d="M10 27 L3.5 20 L5.5 31 Z" fill="#ff5c9d"/>' +
  '<ellipse cx="23" cy="27" rx="16" ry="13.5" fill="url(#bgA)"/>' +
  '<ellipse cx="23" cy="30.5" rx="9.5" ry="7.5" fill="url(#blA)" opacity=".92"/>' +
  '<path d="M13 23.5 q8.5 2.5 8.5 10.5 q-8.5-2.5-8.5-10.5Z" fill="#ff6fae"/>' +
  '<path d="M21.5 13.5 q1-6.5 4.5-6.5 q-1.2 4-2 6 q2.8-4 6-3 q-2 3-4.5 4.2Z" fill="#ff9ccb"/>' +
  '<path d="M36 22.5 L42.5 25.5 L36 28.5 Z" fill="#ffc44d"/>' +
  '<circle cx="31" cy="21.5" r="3.3" fill="#4a1030"/>' +
  '<circle cx="32.3" cy="20.3" r="1.15" fill="#fff"/>' +
  '<ellipse cx="34.5" cy="27.5" rx="3.2" ry="2.1" fill="#ff4f93" opacity=".4"/>' +
  '</svg>';

const chat = document.getElementById('chat');
const input = document.getElementById('input');
const jump = document.getElementById('jump');
let pinned = true;   // false once the reader scrolls up
/* How many replies have arrived below the fold. A scroll-to-latest button
   that cannot say how much you are missing is a button you have to press
   speculatively - the count is the whole point of it. */
let unread = 0;
function paintJump() {
  jump.classList.toggle('show', !pinned && chat.scrollHeight > chat.clientHeight + 40);
  const n = document.getElementById('jumpn');
  if (!n) return;
  n.textContent = unread > 99 ? '99+' : String(unread);
  n.hidden = unread < 1;
  jump.setAttribute('aria-label', unread > 0
    ? `Scroll to the latest message, ${unread} new`
    : 'Scroll to the latest message');
}
jump.onclick = () => {
  chat.scrollTo({top: chat.scrollHeight, behavior: 'smooth'});
  pinned = true;
  unread = 0;
  paintJump();
};
const sendbtn = document.getElementById('sendbtn');
const isFa = s => /[\u0600-\u06FF]/.test(s);
/* The learner is the second bird — same shape, sunny yellow instead of pink. */
const YELLOW_BIRD =
  '<svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' +
  '<defs>' +
  '<linearGradient id="ybA" x1="0" y1="0" x2="1" y2="1">' +
  '<stop offset="0" stop-color="#ffe9a8"/><stop offset="55%" stop-color="#ffd257"/>' +
  '<stop offset="100%" stop-color="#f5a524"/></linearGradient>' +
  '<linearGradient id="ylA" x1="0" y1="0" x2="0" y2="1">' +
  '<stop offset="0" stop-color="#fffdf2"/><stop offset="100%" stop-color="#fff0c2"/>' +
  '</linearGradient></defs>' +
  '<path d="M10 27 L3.5 20 L5.5 31 Z" fill="#f5a524"/>' +
  '<ellipse cx="23" cy="27" rx="16" ry="13.5" fill="url(#ybA)"/>' +
  '<ellipse cx="23" cy="30.5" rx="9.5" ry="7.5" fill="url(#ylA)" opacity=".95"/>' +
  '<path d="M13 23.5 q8.5 2.5 8.5 10.5 q-8.5-2.5-8.5-10.5Z" fill="#ffbe3d"/>' +
  '<path d="M21.5 13.5 q1-6.5 4.5-6.5 q-1.2 4-2 6 q2.8-4 6-3 q-2 3-4.5 4.2Z" fill="#ffd979"/>' +
  '<path d="M36 22.5 L42.5 25.5 L36 28.5 Z" fill="#f97316"/>' +
  '<circle cx="31" cy="21.5" r="3.3" fill="#4a2b00"/>' +
  '<circle cx="32.3" cy="20.3" r="1.15" fill="#fff"/>' +
  '<ellipse cx="34.5" cy="27.5" rx="3.2" ry="2.1" fill="#f97316" opacity=".35"/>' +
  '</svg>';

const WELCOME = "Hey ! Fluently here. Let's learn English together.";

function now() {
  return new Date().toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
}

function escapeHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
function renderText(s) {
  // escape first (safe), then turn **...** markers into bold
  return escapeHtml(s).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>');
}

/* A phrase bank arrives as "💬 Title\n• english\n  ↳ فارسی" pairs.
   Render it as separate cards instead of one run-on pre-wrap block.
   Only the 💬 banner marks a phrase bank — grammar lessons also use • and ↳,
   and must stay as plain text or the parser tears them apart. */
function parsePhraseList(text) {
  if (!text.trimStart().startsWith('💬')) return null;
  const head = [];
  const pairs = [];
  let cur = null;
  for (const raw of text.split('\n')) {
    const line = raw.replace(/\s+$/, '');
    const bullet = line.match(/^\s*[•·]\s+(.*)$/);
    const arrow = line.match(/^\s*↳\s*(.*)$/);
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
  av.innerHTML = who === 'bot' ? BIRD : YELLOW_BIRD;

  const wrap = document.createElement('div');
  wrap.className = 'bubble-wrap';

  const bubble = document.createElement('div');
  bubble.className = 'msg ' + who;
  if (opts.err) bubble.classList.add('err');
  if (isFa(text) && !/[A-Za-z]/.test(text.slice(0, 40))) bubble.classList.add('rtl');
  if (text.split('\n').length > 10) bubble.classList.add('long');
  const phrases = who === 'bot' && !opts.err ? parsePhraseList(text) : null;
  if (phrases) renderPhraseList(bubble, phrases);
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

    const speakBtn = document.createElement('button');
    speakBtn.className = 'mtool';
    speakBtn.textContent = '🔊';
    speakBtn.title = 'Listen to this message — گوش بده';
    speakBtn.setAttribute('aria-label', 'Listen to this message');
    speakBtn.onclick = () => {
      if (Speech.isPlaying(text)) { Speech.stop(); speakBtn.classList.remove('on'); return; }
      [...chat.querySelectorAll('.mtool.on')].forEach((n) => n.classList.remove('on'));
      speakBtn.classList.add('on');
      if (!Speech.speak(text, () => speakBtn.classList.remove('on'))) {
        speakBtn.classList.remove('on');
      }
    };

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

    tools.append(speakBtn, copyBtn, againBtn);
    meta.appendChild(tools);
  }

  wrap.appendChild(bubble);
  wrap.appendChild(meta);
  row.appendChild(av);
  row.appendChild(wrap);
  chat.appendChild(row);
  if (pinned) chat.scrollTop = chat.scrollHeight;
  else if (who === 'bot') { unread++; paintJump(); }
  return bubble;
}

function showTyping() {
  const row = document.createElement('div');
  row.className = 'row bot';
  row.id = 'typing';
  row.innerHTML =
    '<div class="mav bot">' + BIRD + '</div>' +
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

document.getElementById('composer').addEventListener('submit', e => {
  e.preventDefault();
  send(input.value);
});
/* ---------- motion seed: the bird fills up with daily usage ---------- */
const SEED_GOAL = 50;                     // messages allowed per session
const SEED_RESET_UTC = 3.5;               // session rolls over at 03:30 GMT
const Seed = {
  state: { day: '', count: 0, streak: 0, best: 0 },
  warned: false,                 // only explain the limit once per session
  /* A session starts at 03:30 GMT, so the "day" is counted from that point —
     otherwise a user studying at 02:00 would lose their progress at midnight. */
  key(d = new Date()) {
    const shifted = new Date(d.getTime() - SEED_RESET_UTC * 3600 * 1000);
    return shifted.getUTCFullYear() + '-' +
           String(shifted.getUTCMonth() + 1).padStart(2, '0') + '-' +
           String(shifted.getUTCDate()).padStart(2, '0');
  },
  /* when the current session ends (for the countdown in the tooltip) */
  msLeft() {
    // the boundary is 03:30 UTC — the same instant at which key() rolls over
    const now = new Date();
    let ms = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(),
                      3, 30, 0, 0) - now.getTime();
    if (ms <= 0) ms += 24 * 3600 * 1000;   // today's boundary passed
    return ms;
  },
  msText() {
    const ms = Math.max(0, this.msLeft());
    return Math.floor(ms / 3600000) + 'h ' +
           String(Math.floor((ms % 3600000) / 60000)).padStart(2, '0') + 'm';
  },
  load() {
    try {
      const raw = localStorage.getItem('fluentify.seed');
      if (raw) this.state = Object.assign(this.state, JSON.parse(raw));
    } catch (e) { /* private mode: keep in memory only */ }
    this.rollDay();
    this.paint();
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
  /* Checked on every send, so a tab left open past 03:30 GMT unlocks itself. */
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
        `Your next ${SEED_GOAL} messages arrive in ${this.msText()} (03:30 GMT).\n` +
        `امروز هر ${SEED_GOAL} پیام را استفاده کردی. پیام‌های بعدی ${this.msText()} دیگر فعال می‌شوند.`,
        'bot');
    this.paint();
  },
  celebrate() {
    const av = document.querySelector('.avatar');
    if (av) { av.classList.add('bloom'); setTimeout(() => av.classList.remove('bloom'), 1600); }
    add(`🌱 Today's seed is full — ${SEED_GOAL} messages done! You have finished ` +
        `for today; the next session starts in ${this.msText()} (03:30 GMT).\n` +
        `امروز تمام شد. ${this.msText()} دیگر بخش بعدی شروع می‌شود.`, 'bot');
  },
  paint() {
    const pct = Math.min(100, Math.round((this.state.count / SEED_GOAL) * 100));
    const full = pct >= 100;
    const av = document.querySelector('.avatar');
    const bird = av && av.querySelector('svg');
    if (bird) {
      // the seed ring around the bird grows through the day
      bird.style.setProperty('--seed', pct + '%');
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
      meter.title = `Seed ${pct}% · streak ${this.state.streak} session(s) · ` +
        `${this.state.count}/${SEED_GOAL} messages · resets in ` +
        `${this.msText()} (03:30 GMT)`;
    }
    this.lockUI(full);
  },
  /* Grey out the composer so the block is visible, not just enforced */
  lockUI(full) {
    const box = document.getElementById('composer');
    if (!box) return;
    box.classList.toggle('locked', full);
    const note = document.getElementById('limitenote');
    if (note) {
      const used = Math.min(this.state.count, SEED_GOAL);
      const left = SEED_GOAL - used;
      const pct = used / SEED_GOAL;
      // The moon's position is the whole point of the row: one property,
      // and the track does the rest. 0 is the left end, 1 the right.
      note.style.setProperty('--p', pct.toFixed(4));

      // Warn over the last fifth, where a learner can still do something
      // about it, and say nothing at all before that. A bar that announces
      // itself on every message is a bar people stop reading.
      const warn = pct >= 0.8;
      note.classList.toggle('warn', warn && !full);
      note.classList.toggle('full', !!full);

      const txt = note.querySelector('.limitxt');
      if (txt) {
        txt.innerHTML = full
          ? `Daily limit reached — <b>${SEED_GOAL}/${SEED_GOAL}</b> messages used. ` +
            `The next ${SEED_GOAL} arrive in <b>${this.msText()}</b> (03:30 GMT).<br>` +
            `سقف پیام امروز پر شد. ${this.msText()} دیگر بخش بعدی فعال می‌شود.`
          : warn
            // "1 messages left" is the sort of thing that makes a learner stop
            // trusting the rest of the copy
            ? `<b>${left}</b> ${left === 1 ? 'message' : 'messages'} left today — ` +
              `the next ${SEED_GOAL} arrive in <b>${this.msText()}</b> (03:30 GMT).<br>` +
              `${left} پیام باقی مانده. ${this.msText()} دیگر بخش بعدی.`
            : '';
      }
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

/* ==================================================================== EMOJI
 * The picker's contents come from emojis.json, not from here - same rule as
 * every other piece of content in this project: adding an emoji is an edit to
 * a data file, never to code.
 *
 * Search matches the emoji itself, its name, its category and its keywords,
 * so "happy", "check" and "teacher" all find something. That matters more
 * here than in a phone keyboard: the people using this are learners, and
 * looking for a word they already know is faster than hunting a grid.
 */
const Emoji = (() => {
  const SEARCH = /[\p{L}\p{N}\s'-]/u;   // \w is ASCII-only; Persian would not match
  let data = null;
  let open = false;
  let lastFocus = null;
  let els = {};

  const norm = (s) => String(s || '').toLowerCase().trim();

  /* Emoji carry no text of their own, so each one gets its name as an
     accessible label. A grid of unlabelled glyphs is a wall of nothing to a
     screen reader. */
  function tile(e) {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'etile';
    b.textContent = e.e;
    b.dataset.emoji = e.e;
    const label = norm(e.name).replace(/-/g, ' ');
    b.title = label;
    b.setAttribute('aria-label', label);
    return b;
  }

  function matches(e, q, cat) {
    if (!q) return true;
    const hay = norm(e.e + ' ' + e.name + ' ' + (e.kw || '') + ' ' + cat);
    return q.split(/\s+/).every((word) => hay.includes(word));
  }

  function renderGrid(host, list, catLabel) {
    const frag = document.createDocumentFragment();
    list.forEach((e) => frag.appendChild(tile(e)));
    host.appendChild(frag);
  }

  function build() {
    els.panel = document.getElementById('emojipanel');
    els.btn = document.getElementById('emojibtn');
    els.input = document.getElementById('input');
    if (!els.panel || !els.btn) return false;

    els.search = document.createElement('input');
    els.search.type = 'search';
    els.search.className = 'esearch';
    els.search.placeholder = 'Search emoji… / جست‌وجوی ایموجی…';
    els.search.setAttribute('aria-label', 'Search emoji / جست‌وجوی ایموجی');
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
      const t = ev.target.closest('.etile');
      if (!t) return;
      insert(t.dataset.emoji);
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

  function paint() {
    const q = norm(els.search.value);
    els.body.textContent = '';
    let shown = 0;

    if (!q) {
      renderGrid(els.body, data.recent.emojis, 'recent');
      shown += data.recent.emojis.length;
      data.categories.forEach((c) => {
        const h = document.createElement('div');
        h.className = 'ehead';
        h.textContent = c.label + ' · ' + c.label_fa;
        els.body.appendChild(h);
        renderGrid(els.body, c.emojis, c.label);
        shown += c.emojis.length;
      });
    } else {
      data.categories.forEach((c) => {
        const hits = c.emojis.filter((e) => matches(e, q, c.label));
        if (!hits.length) return;
        const h = document.createElement('div');
        h.className = 'ehead';
        h.textContent = hits.length + ' · ' + c.label;
        els.body.appendChild(h);
        renderGrid(els.body, hits, c.label);
        shown += hits.length;
      });
    }

    if (!shown) {
      const none = document.createElement('div');
      none.className = 'eempty';
      none.textContent = 'No emoji matches “' + els.search.value.trim() + '”';
      els.body.appendChild(none);
    }
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
      data = await loadJSON('emojis');
    } catch (e) {
      // No picker is a smaller problem than a composer that cannot send.
      if (els.btn) els.btn.hidden = true;
      data = null;
      return false;
    }
    return true;
  }

  return { mount: build, open: show, close, get open() { return open; } };
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
   * page already marks an active speaker with .on, so this only has to
   * watch for that rather than know anything about audio.
   */
  function watchSpeaking() {
    const set = () => {
      const on = !!document.querySelector('.mtool.on, .bbc-play.on');
      document.body.classList.toggle('speaking', on);
    };
    new MutationObserver(set).observe(document.getElementById('chat') || document.body,
      {subtree: true, attributes: true, attributeFilter: ['class']});
    // the listening panel lives outside #chat
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
    vpanel: 'vtoggle', gpanel: 'gtoggle', fpanel: 'ftoggle',
    lpanel: 'ltoggle', phpanel: 'phtoggle', rpanel: 'rtoggle',
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
 * Only Vocabulary had a search box; 37 grammar lessons and 39 sentence banks
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
      'Search 37 lessons… / جست‌وجوی درس‌ها…', {group: '.glevel'});
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
    blurb.textContent = sec.blurb_en + ' — ' + sec.blurb_fa;
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
      t.textContent = sec.tip_en + ' — ' + sec.tip_fa;
      tip.append(k, t);
      view.appendChild(tip);
    }

    (sec.groups || []).forEach((g) => {
      const wrap = document.createElement('div');
      wrap.className = 'pgroup';
      const gh = document.createElement('div');
      gh.className = 'ghead';
      gh.textContent = g.name_en;
      const gfa = document.createElement('span');
      gfa.className = 'fa';
      gfa.textContent = g.name_fa;
      gh.appendChild(gfa);
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
        add('pfa', r.fa);
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
      blurb.textContent = lv.blurb_en + ' — ' + lv.blurb_fa;
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
   A catalogue, not a download: every clip, transcript and worksheet stays on
   BBC's servers and the player streams from there. Nothing BBC publishes is
   copied into this repository or into the APK.

   Each episode is graded A2→C1 by tools/fetch_bbc_6min.py, which reads the
   official transcript and blends vocabulary stretch, the share of B2+ words,
   sentence length, clause density and speaking rate. The grade comes from the
   transcript, so the band is what you actually hear, not the topic. */
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
    // Keep transcript-only episodes too. BBC retired the player on its older
    // 6 Minute English pages, so roughly a third of the archive has a graded
    // transcript and a worksheet link but no streamable audio - hiding those
    // would quietly drop two thirds of the catalogue.
    const all = doc.episodes || [];
    const episodes = all.filter((e) => e.audio || e.transcript_url);
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
    // '?' means "no transcript", not a level - it must not be listed as one
    const spread = Object.keys(dist).filter((k) => k && k !== '?').sort().join(' · ');
    const ungradedN = episodes.filter((e) => !e.level).length;
    const tail = ungradedN ? ` ${ungradedN} have no transcript, so no grade.` : '';
    // Count what is actually listed, not doc.count. Three of the 1126 carry
    // neither a stream nor a transcript and are filtered out above, so
    // quoting the catalogue total claimed 1123 episodes were on screen when
    // 1126 was - and no level tab ever added up to the number in the header.
    const hidden = (doc.count || 0) - episodes.length;
    const dropped = hidden > 0
      ? ` ${hidden} have neither audio nor transcript and are not listed.`
      : '';
    note.textContent = spread
      ? `${episodes.length} BBC episodes — ${episodes.length - ungradedN} graded ` +
        `${spread}. Each grade comes from the official transcript: vocabulary, ` +
        `sentence length and speaking pace.${tail}${dropped} ` +
        'Audio plays from bbc.co.uk. / صدا از سایت بی‌بی‌سی پخش می‌شود.'
      : `${episodes.length} episodes from BBC Learning English. ` +
        'Audio plays from bbc.co.uk.';
    head.appendChild(note);
    wrap.appendChild(head);

    // Level filter. Episodes without a transcript cannot be graded - the
    // one-line blurb is too short to score honestly - so they get their own
    // tab rather than being silently lumped into "All" as if they were A2.
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
        if (!ep.level) lvl.title = 'No transcript, so no honest grade';
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
        if (!ep.level) bits.push('no transcript to grade from');
        if (st.avg_sentence) bits.push('sentences ~' + st.avg_sentence + ' words');
        if (st.challenge_pct != null) bits.push(st.challenge_pct + '% B2+');
        if (st.c1c2_pct) bits.push(st.c1c2_pct + '% C1');
        meta.textContent = bits.join(' · ');
        card.appendChild(meta);

        const bar2 = document.createElement('div');
        bar2.className = 'bbc-actions';

        const play = document.createElement('button');
        play.className = 'bbc-play';
        if (!ep.audio) {
          // no stream: BBC removed the player from these older pages, so the
          // official transcript is the way in
          play.textContent = '📄  Transcript only';
          play.classList.add('nofile');
          play.title = 'BBC no longer streams this episode. Open the transcript.';
          play.onclick = () => window.open(ep.transcript_url, '_blank',
                                           'noopener');
          bar2.appendChild(play);
          card.appendChild(bar2);
          list.appendChild(card);
          continue;
        }
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

        if (ep.transcript_url) {
          const tr = document.createElement('a');
          tr.className = 'bbc-link';
          tr.href = ep.transcript_url;
          tr.target = '_blank';
          tr.rel = 'noopener noreferrer';
          tr.textContent = 'Transcript';
          tr.title = 'The official transcript, as a PDF from BBC Learning English';
          bar2.appendChild(tr);
        }
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
  mean.innerHTML = '<b>' + escapeHtml(entry.en) + '</b> — ' + escapeHtml(entry.fa);

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
    const filter = (window.__vFilter != null ? window.__vFilter
      : (document.getElementById('vsearch')?.value || '')).trim().toLowerCase();

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
};
document.getElementById('vtoggle').onclick = () => togglePanel('vpanel', 'vtoggle');
document.getElementById('gtoggle').onclick = () => togglePanel('gpanel', 'gtoggle');
document.getElementById('ftoggle').onclick = () => togglePanel('fpanel', 'ftoggle');
document.getElementById('ltoggle').onclick = () => togglePanel('lpanel', 'ltoggle');
document.getElementById('phtoggle').onclick = () => togglePanel('phpanel', 'phtoggle');
document.getElementById('rtoggle').onclick = () => togglePanel('rpanel', 'rtoggle');

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
  const note = document.getElementById('bootnote');
  let gone = false;
  let floorUp = false;
  let dataIn = false;
  let deadline = 0;

  function hide() {
    if (gone) return;
    gone = true;
    clearTimeout(deadline);
    el.classList.add('gone');
    // Removed as well as faded: left in the tree it stays a full-screen
    // element that a later focus can land on.
    setTimeout(() => { if (el.parentNode) el.parentNode.removeChild(el); }, 400);
    try { input.focus(); } catch (e) { /* the field may not exist yet */ }
  }

  // Both conditions, in whichever order they arrive. The floor is on a timer
  // rather than on a promise so that a slow section cannot extend it.
  function maybe() { if (floorUp && dataIn) hide(); }
  setTimeout(() => { floorUp = true; maybe(); }, FLOOR_MS);

  deadline = setTimeout(hide, CEILING_MS);
  window.addEventListener('error', hide);
  window.addEventListener('unhandledrejection', hide);

  return {
    /* What is loading, in the reader's words. */
    say(text) { if (note) note.textContent = text; },
    step(done, total, label) {
      if (fill) fill.style.transform = 'scaleX(' + (total ? done / total : 0) + ')';
      if (note && label) note.textContent = label + ' · ' + done + ' / ' + total;
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
  const steps = [
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
Emoji.mount();
Player.mount();
Motion.init();
Panels.init();
PanelSearch.attachAll();

/* clear conversation */
/* ---------- clear: button or typed ---------- */
function clearChat() {
  chat.innerHTML = '';
  history.length = 0;
  historyAt = -1;
  add(WELCOME, 'bot');
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
    flip.style.background = 'rgba(255,255,255,.10)';
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
    const open = document.querySelector('#vpanel.open, #gpanel.open, #fpanel.open, #lpanel.open, #phpanel.open');
    if (open) { open.classList.remove('open'); return; }
    Speech.stop();
  }
});

/* ---------- stop auto-scrolling once the reader scrolls up ---------- */
chat.addEventListener('scroll', () => {
  pinned = chat.scrollHeight - chat.scrollTop - chat.clientHeight < 90;
  // Reaching the bottom is what clears the count, not merely scrolling.
  if (pinned) unread = 0;
  paintJump();
});


/* boot */
Review.load();          // after every declaration above
Review.paint();         // and paint once here as well as on open, so the
                        // panel can never be reached in a blank state even if
                        // the on-open hook is missed
add(WELCOME, 'bot');
Seed.load();
input.focus();
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def _send_text(self, body: str, content_type: str,
                   cache_seconds: int = 0) -> None:
        """Reply with a plain body. `_send_json` covers everything else."""
        raw = body.encode("utf-8")
        self.send_response(200)
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
                "blurb_fa": s["blurb"]["fa"],
                "tip_en": s.get("tip", {}).get("en", ""),
                "tip_fa": s.get("tip", {}).get("fa", ""),
                "groups": [{
                    "name_en": g["name"]["en"],
                    "name_fa": g["name"]["fa"],
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
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Chatbot preview running at http://localhost:{PORT}")
    server.serve_forever()
