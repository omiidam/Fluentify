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
<style>
  :root {
    /* base theme sampled from imagecolorpicker.com/color-code/0b102e */
    --base: #0b102e;
    --bg1: #0b102e; --bg2: #131a3f; --bg3: #1b2350;
    --panel: rgba(17, 24, 58, .88); --panel2: #1a2350;
    --accent: #6d8cff; --accent2: #34d399; --accent3: #a78bfa;
    --text: #eef1fb; --muted: #aab7d8; --dim: #8a97bb;
    --bot: #1c2450; --user1: #4f6ef7; --user2: #7c4dff;
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
  .backdrop { position: fixed; inset: 0; z-index: 0; overflow: hidden; }
  .backdrop::before {
    content: ''; position: absolute; inset: -20%;
    background:
      radial-gradient(45% 45% at 18% 22%, rgba(109,140,255,.55), transparent 70%),
      radial-gradient(40% 40% at 82% 18%, rgba(167,139,250,.45), transparent 70%),
      radial-gradient(50% 50% at 72% 82%, rgba(52,211,153,.30), transparent 70%),
      radial-gradient(45% 45% at 25% 85%, rgba(56,189,248,.32), transparent 70%),
      linear-gradient(160deg, #0b102e 0%, #141c46 45%, #1b2350 100%);
    filter: blur(40px) saturate(140%);
    animation: drift 26s ease-in-out infinite alternate;
  }
  @keyframes drift {
    from { transform: translate3d(-2%, -1%, 0) scale(1); }
    to   { transform: translate3d(3%, 2%, 0) scale(1.12); }
  }
  @media (prefers-reduced-motion: reduce) {
    .backdrop::before { animation: none; }
  }
  .orb {
    position: fixed; border-radius: 50%; filter: blur(60px);
    opacity: .38; z-index: 0; pointer-events: none;
  }
  .orb.o1 { width: 380px; height: 380px; top: -90px; left: -70px;
            background: radial-gradient(circle, #6d8cff, transparent 70%);
            animation: float1 18s ease-in-out infinite alternate; }
  .orb.o2 { width: 320px; height: 320px; bottom: -80px; right: -60px;
            background: radial-gradient(circle, #a78bfa, transparent 70%);
            animation: float2 22s ease-in-out infinite alternate; }
  .orb.o3 { width: 260px; height: 260px; top: 45%; right: 18%;
            background: radial-gradient(circle, #34d399, transparent 70%);
            opacity: .3; animation: float1 26s ease-in-out infinite alternate-reverse; }
  @keyframes float1 { to { transform: translate(60px, 40px) scale(1.15); } }
  @keyframes float2 { to { transform: translate(-50px, -40px) scale(1.1); } }

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
  .hbtn {
    position: relative;
    background: linear-gradient(140deg, rgba(255,255,255,.10), rgba(255,255,255,.04));
    color: var(--text);
    border: 1px solid rgba(255,255,255,.16); border-radius: 12px;
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
  .hbtn:hover {
    border-color: rgba(109,140,255,.7);
    background: linear-gradient(140deg, rgba(109,140,255,.28), rgba(167,139,250,.16));
  }
  .hbtn.on {
    border-color: rgba(109,140,255,.8);
    background: linear-gradient(140deg, rgba(109,140,255,.42), rgba(167,139,250,.26));
    box-shadow: 0 0 0 1px rgba(109,140,255,.25), 0 4px 14px rgba(109,140,255,.25);
  }
  .hbtn.on i, .hbtn.on span { color: #fff; }
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
    padding: 12px 16px; border-radius: 17px;
    font-size: 15px; line-height: 1.68; white-space: pre-wrap; word-wrap: break-word;
    border: 1px solid var(--line);
  }
  .msg.bot {
    background: linear-gradient(150deg, rgba(255,255,255,.10), rgba(255,255,255,.04));
    border: 1px solid rgba(255,255,255,.12);
    border-bottom-left-radius: 6px;
    -webkit-backdrop-filter: blur(12px);
    backdrop-filter: blur(12px);
    box-shadow: 0 2px 10px rgba(3,6,20,.3), inset 0 1px 0 rgba(255,255,255,.12);
  }
  .msg.user {
    background: linear-gradient(135deg, #4f6ef7 0%, #7c4dff 60%, #a855f7 100%);
    color: #fff; border: none; border-bottom-right-radius: 6px;
    box-shadow: 0 6px 20px rgba(79,110,247,.38), inset 0 1px 0 rgba(255,255,255,.3);
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

  /* scroll-to-latest — only appears once you scroll up */
  .jump {
    position: absolute; right: 50%; transform: translate(50%, 8px);
    bottom: 78px; z-index: 6; width: 38px; height: 38px;
    border-radius: 50%; cursor: pointer; font-size: 15px;
    display: grid; place-items: center;
    color: #fff; font-family: inherit;
    background: linear-gradient(135deg, rgba(109,140,255,.9), rgba(167,139,250,.85));
    border: 1px solid rgba(255,255,255,.22);
    box-shadow: 0 6px 18px rgba(0,0,0,.4);
    opacity: 0; pointer-events: none; transition: .18s;
  }
  .jump.show { opacity: 1; pointer-events: auto; transform: translate(50%, 0); }
  .jump:hover { filter: brightness(1.12); }
  @media (max-width: 599px) { .jump { bottom: 92px; } }

  /* typing indicator */
  .typing { display: inline-flex; gap: 5px; padding: 13px 16px !important; }
  .typing span {
    width: 7px; height: 7px; border-radius: 50%; background: var(--muted);
    animation: bounce 1.2s infinite;
  }
  .typing span:nth-child(2) { animation-delay: .15s; }
  .typing span:nth-child(3) { animation-delay: .3s; }
  @keyframes bounce { 30% { transform: translateY(-6px); opacity: 1; } }

  /* ---------- chips ---------- */
  .chips {
    display: flex; gap: 8px; padding: 11px 20px; overflow-x: auto;
    border-top: 1px solid var(--line);
  }
  .chips::-webkit-scrollbar { height: 6px; }
  .chips::-webkit-scrollbar-thumb { background: #2f3a6b; border-radius: 6px; }
  .chip {
    background: linear-gradient(140deg, rgba(109,140,255,.14), rgba(167,139,250,.08));
    color: #c3cdff;
    border: 1px solid rgba(109,140,255,.28);
    border-radius: 999px; padding: 7px 14px; font-size: 12.5px;
    cursor: pointer; transition: .15s; white-space: nowrap; flex: none;
  }
  .chip:hover {
    background: linear-gradient(140deg, rgba(109,140,255,.3), rgba(167,139,250,.18));
    transform: translateY(-1px); border-color: rgba(109,140,255,.55);
  }

  /* ---------- input ---------- */
  form {
    display: flex; gap: 10px; padding: 14px 20px 18px;
    background: linear-gradient(0deg, rgba(11,16,46,.55), transparent);
    flex: none;
  }
  #input {
    flex: 1; background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.14);
    border-radius: 15px; padding: 14px 17px; color: var(--text);
    font-size: 15.5px; outline: none; transition: .15s;
    font-family: inherit;
  }
  #input:focus {
    border-color: rgba(109,140,255,.7);
    background: rgba(255,255,255,.09);
    box-shadow: 0 0 0 3px rgba(109,140,255,.18);
  }
  #input::placeholder { color: #7e8caf; }
  .send {
    background: linear-gradient(135deg, #6d8cff 0%, #a78bfa 100%);
    border: none; border-radius: 15px; color: #fff;
    padding: 0 28px; font-size: 15px; font-weight: 700; cursor: pointer;
    transition: .15s; box-shadow: 0 8px 22px rgba(109,140,255,.45);
    font-family: inherit;
  }
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
  .rbadge {
    position: absolute; top: -3px; inset-inline-end: -3px;
    display: inline-flex; align-items: center; justify-content: center;
    min-width: 15px; height: 15px; padding: 0 4px; border-radius: 999px;
    font-size: 9px; font-weight: 800; color: #3a2400;
    background: #ffc44d; border: 1px solid rgba(11,16,46,.6);
  }
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
    flex-wrap: wrap; gap: 10px;
    padding: calc(10px + var(--sat)) calc(var(--pad) + var(--sar)) 10px
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
    overflow: visible;
    scrollbar-width: none; padding-bottom: 0;
    /* let the row bleed into the side padding so tiles can use the full width */
    margin-inline: calc(var(--pad) * -1); padding-inline: var(--pad);
  }
  .tools::-webkit-scrollbar { display: none; }
  .hbtn { width: 44px; height: 46px; border-radius: 11px; padding: 4px 1px; }
  .hbtn i { font-size: 15px; }
  .hbtn span { font-size: 8px; }
  /* no hover affordances on touch — they'd stick after a tap */
  @media (hover: none) {
    .hbtn:hover, .chip:hover, .ftopic:hover, .vbtn:hover,
    .gbtn:hover, .go:hover, .ltab:hover, .lrow:hover, .lplay:hover,
    .send:hover { transform: none; filter: none; }
    .hbtn:active, .chip:active, .ftopic:active, .vbtn:active,
    .gbtn:active, .go:active, .ltab:active, .lrow:active, .send:active {
      transform: scale(.96);
    }
  }

  /* ---- panels: nearly full height, edge-to-edge, own scroll area ---- */
  #vpanel, #gpanel, #fpanel, #lpanel, #phpanel, #rpanel {
    padding: 12px calc(var(--pad) + var(--sar)) 14px calc(var(--pad) + var(--sal));
    max-height: 62%;
    overscroll-behavior: contain;
    -webkit-overflow-scrolling: touch;
  }
  #vpanel h3, #gpanel h3, #fpanel h3, #lpanel h3, #phpanel h3, #rpanel h3 {
    font-size: 11.5px; margin-bottom: 8px; line-height: 1.5;
  }
  .domains { max-height: 46vh; }

  /* every tappable pill in a panel gets a real touch target */
  .vbtn, .gbtn, .ftopic, .ltab {
    min-height: 36px; padding: 7px 12px; font-size: 12px;
  }
  .gbtn { padding: 0; }
  .gmain { padding: 8px 4px 8px 12px; font-size: 12px; min-height: 36px; }
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
  .lrow { padding: 9px 11px; gap: 12px; }
  .lplay { width: 36px; height: 36px; font-size: 14px; }
  .ltext .en { font-size: 14px; }
  .ltext .fa { font-size: 12px; margin-top: 2px; }
  .ltabs { gap: 6px; }

  /* ---- chat ---- */
  #chat { padding: 14px calc(var(--pad) + var(--sar)) 8px calc(var(--pad) + var(--sal));
          gap: 13px; }
  .bubble-wrap { max-width: 92%; }
  .mav { width: 28px; height: 28px; border-radius: 10px; }
  .mav svg { width: 23px; height: 23px; }
  .msg { padding: 11px 14px; font-size: 15px; border-radius: 16px; }
  .msg.long { max-height: 52vh; }
  .row { gap: 8px; }

  /* ---- chips: edge-to-edge scroll strip ---- */
  .chips {
    gap: 7px; padding: 9px calc(var(--pad) + var(--sar)) 9px calc(var(--pad) + var(--sal));
    -webkit-overflow-scrolling: touch; overscroll-behavior-x: contain;
  }
  .chip { min-height: 38px; padding: 9px 14px; }

  /* ---- input: 16px stops iOS zooming on focus, safe area clears the bar ---- */
  form {
    padding: 10px calc(var(--pad) + var(--sar))
             calc(10px + var(--sab)) calc(var(--pad) + var(--sal));
    gap: 8px; flex-direction: column;
  }
  .prow-form { display: flex; gap: 8px; }

  /* ---- daily limit reached: the composer goes quiet ---- */
  .limitenote {
    display: flex; align-items: center; gap: 8px;
    padding: 9px 12px; border-radius: 11px; font-size: 12.5px; line-height: 1.5;
    background: linear-gradient(135deg, rgba(167,139,250,.18), rgba(255,141,196,.10));
    border: 1px solid rgba(167,139,250,.34); color: #ddd6fe;
    animation: fade .2s ease;
  }
  .limitenote .lockic { font-size: 15px; flex: none; }
  .limitenote b { color: #fff; }
  form.locked #input {
    opacity: .45; cursor: not-allowed; background: rgba(255,255,255,.03);
  }
  form.locked .send {
    opacity: .4; cursor: not-allowed; filter: grayscale(.5); transform: none;
    box-shadow: none;
  }
  /* every control that would send a message is visibly retired */
  .chip.locked, .ftopic.locked, .vbtn.locked, .gmain.locked, .go.locked {
    opacity: .35; cursor: not-allowed; pointer-events: none;
    filter: grayscale(.6);
  }
  #input { padding: 12px 15px; font-size: 16px; border-radius: 14px; }

  /* ------------------------------------------------------------ speech ---- */
  .mic {
    width: 44px; height: 44px; flex: 0 0 44px; border-radius: 50%;
    border: 1px solid #3a4a86; background: #141c46; color: #cfd8ff;
    font-size: 18px; cursor: pointer; display: grid; place-items: center;
    transition: background .18s, border-color .18s, transform .1s;
  }
  .mic:hover { border-color: #6f86d6; background: #1b2557; }
  .mic:active { transform: scale(.94); }
  .mic.rec {
    background: #7d2b52; border-color: #ff6f9c; color: #fff;
    box-shadow: 0 0 0 0 rgba(255, 111, 156, .55);
    animation: micPulse 1.4s ease-out infinite;
  }
  @keyframes micPulse {
    0%   { box-shadow: 0 0 0 0 rgba(255, 111, 156, .55); }
    100% { box-shadow: 0 0 0 16px rgba(255, 111, 156, 0); }
  }
  @media (prefers-reduced-motion: reduce) {
    .mic.rec { animation: none; }
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
  .bbc-title { font-size: 14.5px; color: #fff; font-weight: 600; }
  .bbc-blurb { margin-top: 5px; font-size: 12.5px; color: #9fb0ef; line-height: 1.5; }
  .bbc-meta { margin-top: 6px; font-size: 11.5px; color: #7d8fd4; }
  .bbc-actions { display: flex; gap: 7px; margin-top: 9px; flex-wrap: wrap; align-items: center; }
  .bbc-play {
    padding: 8px 14px; min-height: 40px; border-radius: 11px; font-size: 13px;
    border: 1px solid #6f86d6; background: #27356e; color: #fff; cursor: pointer;
  }
  .bbc-play.on { background: #7d2b52; border-color: #ff6f9c; }
  .bbc-link { font-size: 12px; color: #9fb0ef; text-decoration: none; padding: 6px 4px; }
  .bbc-link:hover { color: #fff; text-decoration: underline; }
  .bbc-empty { font-size: 12px; color: #7d8fd4; padding: 4px 2px; }
  .send { padding: 0 20px; font-size: 14px; border-radius: 14px; min-height: 46px; }

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
    .prow-form { gap: 10px; }
    #input { padding: 14px 17px; font-size: 15.5px; }
    .send { padding: 0 28px; font-size: 15px; min-height: 0; }
  }

  /* ---------- desktop: full-size meter + the status pill ---------- */
  @media (min-width: 900px) {
    .status { display: flex; }
    #seedmeter { width: 66px; height: 20px; }
    #seedmeter span { font-size: 10.5px; padding: 0 7px; }
  }
</style>
</head>
<body>
<div class="backdrop"></div>
<div class="orb o1"></div>
<div class="orb o2"></div>
<div class="orb o3"></div>

<div class="app">
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
      <button class="hbtn" id="vtoggle" title="Vocabulary — واژگان" aria-label="Vocabulary">
        <i>📚</i><span>Vocab</span></button>
      <button class="hbtn" id="gtoggle" title="Grammar — گرامر" aria-label="Grammar">
        <i>📘</i><span>Grammar</span></button>
      <button class="hbtn" id="ftoggle" title="Sentences — جملات کاربردی" aria-label="Sentences">
        <i>💬</i><span>Say</span></button>
      <button class="hbtn" id="ltoggle" title="Listening A1–C2 — شنیدن" aria-label="Listening">
        <i>🎧</i><span>Listen</span></button>
      <button class="hbtn" id="phtoggle" title="Phonetics — تلفظ و آهنگ" aria-label="Phonetics">
        <i>🗣</i><span>Sounds</span></button>
      <button class="hbtn" id="rtoggle" title="Review saved words — واژه‌های مرور" aria-label="Review">
        <i>⭐</i><span>Review</span><span class="rbadge" id="rbadge" hidden>0</span></button>
      <button class="hbtn danger" id="clear" title="Clear conversation — پاک کردن گفتگو" aria-label="Clear conversation">
        <i>🗑</i><span>Clear</span></button>
    </nav>
  </header>

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

  <div id="chat"></div>
  <button id="jump" class="jump" aria-label="Scroll to the latest message" title="Latest ↓">↓</button>

  <div class="chips" id="chips">
    <span class="chip">how are you?</span>
    <span class="chip">translate apple</span>
    <span class="chip">رنگها</span>
    <span class="chip">define شیر</span>
    <span class="chip">الفبای فارسی</span>
    <span class="chip">tell me a joke</span>
    <span class="chip">ساعت چنده</span>
    <span class="chip">my name is Ali</span>
  </div>

  <div class="stt-panel" id="stt" hidden></div>
  <form id="composer">
    <div class="prow-form">
      <input id="input" autocomplete="off" placeholder="Type a message… / پیام بنویسید…">
      <button class="send" id="sendbtn" type="submit">Send</button>
    </div>
    <div class="limitenote" id="limitenote" hidden>
      <span class="lockic">🌙</span>
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
jump.onclick = () => { chat.scrollTo({top: chat.scrollHeight, behavior: 'smooth'}); pinned = true; };
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

function add(text, who, opts = {}) {
  const row = document.createElement('div');
  row.className = 'row ' + who;

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
  meta.append(
    document.createTextNode(who === 'bot' ? 'Fluentify' : 'You'),
    Object.assign(document.createElement('i'), {textContent: now()}),
  );

  // Every bot message gets its tools: hear it, copy it, retry it.
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

    tools.append(speakBtn, copyBtn);
    meta.appendChild(tools);
  }

  wrap.appendChild(bubble);
  wrap.appendChild(meta);
  row.appendChild(av);
  row.appendChild(wrap);
  chat.appendChild(row);
  if (pinned) chat.scrollTop = chat.scrollHeight;
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
  if (matchReviewCommand(text)) { input.value = ''; return; }
  if (busy) return;                      // real message, but one is in flight
  // daily limit reached — refuse the message, don't queue it
  if (Seed.spent()) { Seed.block(); return; }
  busy = true;
  sendbtn.disabled = true;
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
    add('⚠️ connection lost — is the server running?', 'bot', {err: true});
  }
  busy = false;
  sendbtn.disabled = false;
  input.focus();
}

document.getElementById('composer').addEventListener('submit', e => {
  e.preventDefault();
  send(input.value);
});
document.getElementById('chips').addEventListener('click', e => {
  if (e.target.classList.contains('chip')) send(e.target.textContent);
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
      note.hidden = !full;
      const txt = note.querySelector('.limitxt');
      if (txt && full) {
        txt.innerHTML = `Daily limit reached — <b>${SEED_GOAL}/${SEED_GOAL}</b> messages used. ` +
          `The next ${SEED_GOAL} arrive in <b>${this.msText()}</b> (03:30 GMT).<br>` +
          `سقف پیام امروز پر شد. ${this.msText()} دیگر بخش بعدی فعال می‌شود.`;
      }
    }
    if (full) {
      input.disabled = true;
      sendbtn.disabled = true;
      document.querySelectorAll('.chip, .ftopic, .vbtn, .gmain, .go').forEach((n) => {
        n.classList.add('locked');
      });
    } else {
      input.disabled = false;
      sendbtn.disabled = false;
      document.querySelectorAll('.chip.locked, .ftopic.locked, .vbtn.locked, .gmain.locked, .go.locked')
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
      setTimeout(() => { this.playing = null; if (onEnd) onEnd(); },
                 Math.max(2200, text.length * 62));
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
    u.onend = () => { this.playing = null; if (onEnd) onEnd(); };
    u.onerror = () => { this.playing = null; if (onEnd) onEnd(); };
    this.playing = { text, utter: u };
    speechSynthesis.cancel();
    speechSynthesis.speak(u);
    return true;
  },
  stop() {
    if (this.playing && this.playing.utter) speechSynthesis.cancel();
    if (window.AndroidTTS && window.AndroidTTS.stop) window.AndroidTTS.stop();
    this.playing = null;
  },
  isPlaying(text) { return !!this.playing && this.playing.text === text; },
};
/*__STT_CONFIG__*/

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

  begin() {
    if (this.listening) return true;
    const engine = this.engine();
    if (!engine) return false;

    if (engine === 'android') {
      this.listening = true;
      this.interim = '';
      this.render();
      window.AndroidSTT.start(this.lang(), (partial) => {
        this.interim = partial || '';
        if (this.cfg.show_interim !== false) this.render();
      }, (final) => {
        this.listening = false;
        this.interim = '';
        this.final = final || '';
        this.render();
        if (this.final && this.cfg.submit_on_final) this.commit();
      }, (err) => {
        this.listening = false;
        this.interim = '';
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
    this.rec = rec;
    this.listening = true;
    this.startedAt = Date.now();
    this.interim = '';
    this.final = '';

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
  },

  commit() {
    const text = (this.final + ' ' + this.interim).trim();
    this.final = '';
    this.interim = '';
    if (!text) return false;
    const box = document.getElementById('input');
    if (box) {
      box.value = text;
      box.dispatchEvent(new Event('input'));
      box.focus();
    }
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
    if (this.interim) bits.push('<span class="stt-interim">' + esc(this.interim) + '</span>');
    if (this.final) bits.push('<span class="stt-final">' + esc(this.final) + '</span>');
    panel.innerHTML = bits.join(' ');
  },
};
function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

/* A single mic button in the composer: tap to talk, tap to stop. */
function mountMic() {
  const box = document.getElementById('input');
  if (!box || !STT.supported()) return;
  const btn = document.createElement('button');
  btn.id = 'mic';
  btn.className = 'mic';
  btn.type = 'button';
  btn.title = STT.engine() === 'android'
    ? 'با میکروفون تایپ کن / dictate'
    : 'با میکروفون تایپ کن / dictate';
  btn.setAttribute('aria-label', btn.title);
  btn.textContent = '🎙';
  btn.addEventListener('click', () => {
    if (STT.listening) {
      STT.stop();
      STT.commit();
    } else {
      STT.begin();
    }
  });
  box.parentNode.insertBefore(btn, box.nextSibling);
  STT.render();
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
            add('🔇 No speech engine is available on this device — ' +
                'the sentence is still here to practise. / روی این دستگاه صدایی در دسترس نیست.',
                'bot');
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
async function loadBBC() {
  const box = document.getElementById('llevels');
  if (!box) return;
  try {
    const r = await fetch('/api/bbc');
    const doc = await r.json();
    const episodes = (doc.episodes || []).filter((e) => e.audio);
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
    const spread = Object.keys(dist).sort().join(' · ');
    note.textContent = spread
      ? `${doc.count} BBC episodes graded ${spread}. Each grade comes from the ` +
        'official transcript — vocabulary, sentence length and speaking pace. ' +
        'Audio plays from bbc.co.uk. / صدا از سایت بی‌بی‌سی پخش می‌شود.'
      : `${doc.count} episodes from BBC Learning English. Audio plays from bbc.co.uk.`;
    head.appendChild(note);
    wrap.appendChild(head);

    // level filter
    const levels = [...new Set(episodes.map((e) => e.level).filter(Boolean))].sort();
    const bar = document.createElement('div');
    bar.className = 'bbc-tabs';
    let current = 'all';
    const list = document.createElement('div');
    list.className = 'bbc-list';

    const paint = () => {
      list.innerHTML = '';
      const rows = episodes
        .filter((e) => current === 'all' || e.level === current)
        .slice(0, current === 'all' ? 60 : 200);
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
        lvl.className = 'bbc-lvl lvl-' + (ep.level || '?');
        lvl.textContent = ep.level || '?';
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
        const audio = new Audio();
        audio.preload = 'none';
        audio.crossOrigin = 'anonymous';
        play.onclick = () => {
          if (window.AndroidTTS && window.AndroidTTS.stop) window.AndroidTTS.stop();
          Speech.stop();
          if (!audio.paused && audio.currentTime > 0) {
            audio.pause();
            play.textContent = '▶  Play';
            play.classList.remove('on');
            return;
          }
          audio.src = ep.audio;
          audio.play().catch(() => {
            play.textContent = '▶  Play';
            play.classList.remove('on');
            add('🔇 Could not play that clip — the stream needs a network ' +
                'connection. / پخش این کلیپ به اینترنت نیاز دارد.', 'bot');
          });
          play.textContent = '❚❚  Pause';
          play.classList.add('on');
        };
        audio.onended = () => {
          play.textContent = '▶  Play';
          play.classList.remove('on');
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
      const more = document.createElement('div');
      more.className = 'bbc-empty';
      const shown = rows.length;
      const total = episodes.filter((e) => current === 'all' || e.level === current).length;
      more.textContent = total > shown
        ? `Showing ${shown} of ${total} — pick a level to narrow it down.`
        : '';
      list.appendChild(more);
    };

    const addTab = (id, label) => {
      const b = document.createElement('button');
      b.className = 'bbc-tab';
      b.textContent = label;
      b.dataset.level = id;
      b.onclick = () => {
        current = id;
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

async function loadWordArch() {
  if (wordArchLoaded) return;
  try {
    const r = await fetch('/api/wordarch');
    const bands = await r.json();
    Object.assign(wordArch, bands);
    wordArchLoaded = true;
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
  } catch (e) {
    document.querySelectorAll('#ftopics [data-words]').forEach((slot) => {
      slot.innerHTML = '<div class="wd-more">Word forms unavailable offline.</div>';
    });
  }
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
    loadWordArch();
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
  const panel = document.getElementById(panelId);
  const wasOpen = panel.classList.contains('open');
  ['vpanel', 'gpanel', 'fpanel', 'lpanel', 'phpanel', 'rpanel'].forEach(id => document.getElementById(id).classList.remove('open'));
  ['vtoggle', 'gtoggle', 'ftoggle', 'ltoggle', 'phtoggle', 'rtoggle'].forEach(id => document.getElementById(id).classList.remove('on'));
  if (!wasOpen) {
    panel.classList.add('open');
    document.getElementById(btnId).classList.add('on');
  }
}
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
loadGrammar();
loadPhrases();
loadVocabulary();

/* live-filter the vocabulary panel as you type */
document.getElementById('vsearch').addEventListener('input', (ev) => {
  window.__vFilter = ev.target.value;
  loadVocabulary();
});
loadListening();
loadPhonetics();
mountMic();

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
  add(entry) {
    if (!entry || !entry.en) return false;
    if (this.has(entry.en)) return false;
    this.items.push({
      en: entry.en, fa: entry.fa || '', pos: entry.pos || '',
      forms: (entry.forms || []).map((f) => f.f),
      level: entry.level || 'A1', ok: false, streak: 0,
    });
    this.save();
    return true;
  },
  remove(word) {
    const w = (word || '').toLowerCase();
    this.items = this.items.filter((i) => i.en.toLowerCase() !== w);
    this.save();
    this.paint();
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

function matchReviewCommand(text) {
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
  jump.classList.toggle('show', !pinned);
});

/* boot */
Review.load();          // after every declaration above
add(WELCOME, 'bot');
Seed.load();
input.focus();
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
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
            self._send_json(bbc_catalogue(), 3600)
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
