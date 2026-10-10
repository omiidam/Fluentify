#!/usr/bin/env python3
"""Web preview for the bilingual chatbot — stdlib only, no dependencies.

Run:  python3 webapp.py   →  http://localhost:8765
"""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from chatbot import ChatBot

PORT = 8765
bot = ChatBot()  # shared session memory for the preview

HTML = r"""<!DOCTYPE html>
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
  .hbtn {
    background: linear-gradient(140deg, rgba(255,255,255,.10), rgba(255,255,255,.04));
    color: var(--text);
    border: 1px solid rgba(255,255,255,.16); border-radius: 11px;
    padding: 8px 14px; font-size: 13px; font-weight: 600;
    cursor: pointer; transition: .15s; white-space: nowrap;
    font-family: inherit;
  }
  .hbtn:hover {
    border-color: rgba(109,140,255,.7); color: #dfe6ff;
    background: linear-gradient(140deg, rgba(109,140,255,.28), rgba(167,139,250,.16));
    transform: translateY(-1px);
  }
  .hbtn.on {
    border-color: rgba(109,140,255,.8); color: #fff;
    background: linear-gradient(140deg, rgba(109,140,255,.42), rgba(167,139,250,.26));
    box-shadow: 0 0 0 1px rgba(109,140,255,.25), 0 4px 14px rgba(109,140,255,.25);
  }

  /* ---------- vocabulary / grammar / phrases panels ---------- */
  #vpanel, #gpanel, #fpanel {
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
  #vpanel.open, #gpanel.open, #fpanel.open { display: block; }
  @keyframes fade { from { opacity: 0; transform: translateY(-4px); } }
  #vpanel h3, #gpanel h3, #fpanel h3 {
    font-size: 12px; color: #a9b8de; margin-bottom: 9px; font-weight: 600;
  }
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
  .meta { font-size: 10.5px; color: var(--dim); padding: 0 5px; font-weight: 500; }
  .msg.err { border-color: #f87171; color: #fecaca; background: #7f1d1d55; }

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

  /* ---------- graceful fallback where backdrop-filter is unsupported ---------- */
  @supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
    .app { background: linear-gradient(160deg, #141c46, #1b2350); }
    header { background: linear-gradient(100deg, #24306b, #2a2170); }
    #vpanel, #gpanel, #fpanel { background: #131a3d; }
    .msg.bot { background: #1c2450; }
    #input { background: #141c46; }
    .hb { display: none; }
  }

  @media (max-width: 720px) {
    .app { height: 100vh; border-radius: 0; width: 100%; }
    body { padding: 0; }
    .status { display: none; }
    header { flex-wrap: wrap; padding: 12px 14px; }
    #chat { padding: 16px 14px 8px; }
    .bubble-wrap { max-width: 88%; }
    .domains { max-height: 160px; }
  }
  @media (max-width: 460px) {
    .hbtn { padding: 7px 10px; font-size: 12px; }
    header h1 { font-size: 15px; }
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
    <div class="status"><i></i> online</div>
    <button class="hbtn" id="vtoggle" title="Browse vocabulary domains">📚 Vocabulary</button>
    <button class="hbtn" id="gtoggle" title="English grammar lessons — درس‌های گرامر">📘 Grammar</button>
    <button class="hbtn" id="ftoggle" title="Useful everyday sentences — جملات کاربردی">💬 Sentences</button>
    <button class="hbtn" id="clear" title="Clear conversation">🗑 Clear</button>
  </header>

  <div id="vpanel">
    <h3>Click any domain to get its word list — روی هر دامنه کلیک کنید</h3>
    <div class="domains" id="domains"></div>
  </div>

  <div id="gpanel">
    <h3>English grammar lessons &amp; practice — درس‌ها و تمرین‌های گرامر انگلیسی (کلیک = درس · ✏️ = تمرین)</h3>
    <div class="domains" id="gtopics"></div>
  </div>

  <div id="fpanel">
    <h3>Useful everyday sentences — جملات کاربردی روزمره</h3>
    <div class="domains" id="ftopics"></div>
  </div>

  <div id="chat"></div>

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

  <form id="form">
    <input id="input" autocomplete="off" placeholder="Type a message… / پیام بنویسید…">
    <button class="send" id="sendbtn" type="submit">Send</button>
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
const sendbtn = document.getElementById('sendbtn');
const isFa = s => /[\u0600-\u06FF]/.test(s);
const WELCOME = "Hi, I'm Fluentify!";

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

function add(text, who, opts = {}) {
  const row = document.createElement('div');
  row.className = 'row ' + who;

  const av = document.createElement('div');
  av.className = 'mav' + (who === 'bot' ? ' bot' : '');
  if (who === 'bot') {
    av.innerHTML = BIRD;
  } else {
    av.textContent = '🙂';
  }

  const wrap = document.createElement('div');
  wrap.className = 'bubble-wrap';

  const bubble = document.createElement('div');
  bubble.className = 'msg ' + who;
  if (opts.err) bubble.classList.add('err');
  if (isFa(text) && !/[A-Za-z]/.test(text.slice(0, 40))) bubble.classList.add('rtl');
  if (text.split('\n').length > 10) bubble.classList.add('long');
  bubble.innerHTML = renderText(text);

  const meta = document.createElement('div');
  meta.className = 'meta';
  meta.textContent = (who === 'bot' ? 'Bot' : 'You') + ' · ' + now();

  wrap.appendChild(bubble);
  wrap.appendChild(meta);
  row.appendChild(av);
  row.appendChild(wrap);
  chat.appendChild(row);
  chat.scrollTop = chat.scrollHeight;
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
  chat.scrollTop = chat.scrollHeight;
}
function hideTyping() { document.getElementById('typing')?.remove(); }

let busy = false;
async function send(text) {
  text = (text || '').trim();
  if (!text || busy) return;
  busy = true;
  sendbtn.disabled = true;
  add(text, 'user');
  input.value = '';
  showTyping();
  try {
    const r = await fetch('/api/chat?message=' + encodeURIComponent(text));
    const data = await r.json();
    hideTyping();
    add(data.reply, 'bot');
  } catch (e) {
    hideTyping();
    add('⚠️ connection lost — is the server running?', 'bot', {err: true});
  }
  busy = false;
  sendbtn.disabled = false;
  input.focus();
}

document.getElementById('form').addEventListener('submit', e => {
  e.preventDefault();
  send(input.value);
});
document.getElementById('chips').addEventListener('click', e => {
  if (e.target.classList.contains('chip')) send(e.target.textContent);
});

/* phrases panel (fetched from phrases.json via the server) */
async function loadPhrases() {
  try {
    const r = await fetch('/api/phrases');
    const topics = await r.json();
    const box = document.getElementById('ftopics');
    box.innerHTML = '';
    topics.forEach(t => {
      const b = document.createElement('button');
      b.className = 'ftopic';
      b.title = t.count + ' sentences';
      b.innerHTML = '';
      const en = document.createElement('span');
      en.textContent = t.title_en;
      const fa = document.createElement('span');
      fa.className = 'fa';
      fa.textContent = t.title_fa;
      b.append(en, fa);
      b.onclick = () => send(t.query);
      box.appendChild(b);
    });
  } catch (e) { /* panel stays empty offline */ }
}

/* vocabulary panel — grouped, one compact pill per domain */
async function loadVocabulary() {
  try {
    const r = await fetch('/api/vocabulary');
    const groups = await r.json();
    const box = document.getElementById('domains');
    box.innerHTML = '';
    groups.forEach(g => {
      const sec = document.createElement('div');
      sec.className = 'vgroup';
      const head = document.createElement('div');
      head.className = 'vgroup-head';
      head.append(
        document.createTextNode(g.en),
        Object.assign(document.createElement('span'), {className:'fa', textContent: g.fa}),
        Object.assign(document.createElement('span'), {
          className: 'count', textContent: g.items.length,
        }),
      );
      sec.appendChild(head);
      const row = document.createElement('div');
      row.className = 'vrow';
      g.items.forEach(d => {
        const b = document.createElement('button');
        b.className = 'vbtn';
        b.title = d.title_fa + ' — ' + d.count + ' words';
        b.append(
          Object.assign(document.createElement('span'), {textContent: d.title_en}),
          Object.assign(document.createElement('span'), {className:'n', textContent: d.count}),
        );
        // alt-click / right area → ask in Persian instead
        b.onclick = (ev) => send(ev.altKey ? d.query_fa : d.query_en);
        row.appendChild(b);
      });
      sec.appendChild(row);
      box.appendChild(sec);
    });
  } catch (e) { /* panel stays empty offline */ }
}
/* only one panel open at a time; the active header button is highlighted */
function togglePanel(panelId, btnId) {
  const panel = document.getElementById(panelId);
  const wasOpen = panel.classList.contains('open');
  ['vpanel', 'gpanel', 'fpanel'].forEach(id => document.getElementById(id).classList.remove('open'));
  ['vtoggle', 'gtoggle', 'ftoggle'].forEach(id => document.getElementById(id).classList.remove('on'));
  if (!wasOpen) {
    panel.classList.add('open');
    document.getElementById(btnId).classList.add('on');
  }
}
document.getElementById('vtoggle').onclick = () => togglePanel('vpanel', 'vtoggle');
document.getElementById('gtoggle').onclick = () => togglePanel('gpanel', 'gtoggle');
document.getElementById('ftoggle').onclick = () => togglePanel('fpanel', 'ftoggle');

/* grammar lessons panel (fetched from grammar.json via the server) */
const LEVEL_NAMES = {
  A1: 'مبانی · Beginner',
  A2: 'پایه · Elementary',
  B1: 'متوسط · Intermediate',
  B2: 'پیشرفته · Upper-Int.',
  C1: 'پیشرفته · Advanced',
  C2: 'تسلط · Proficiency',
};
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
        go.title = 'Practice — ' + t.title_en;
        go.setAttribute('aria-label', 'Practice ' + t.title_en);
        go.onclick = () => send(t.practice_en);

        pill.append(b, go);
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

/* clear conversation */
document.getElementById('clear').onclick = () => {
  chat.innerHTML = '';
  add(WELCOME, 'bot');
  input.focus();
};

/* boot */
add(WELCOME, 'bot');
input.focus();
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/vocabulary"):
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
            for t in bot.grammar.values():
                topics.append({
                    "title_en": t["title"]["en"],
                    "title_fa": t["title"]["fa"],
                    "query_en": t["keywords"]["en"][0],
                    "query_fa": t["keywords"]["fa"][0],
                    "practice_en": f"{t['keywords']['en'][0]} exercises",
                    "practice_fa": f"تمرین {t['keywords']['fa'][0]}",
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
            body = HTML.encode("utf-8")
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
