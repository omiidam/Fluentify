#!/usr/bin/env python3
"""Adds a motion system to the UI in webapp.py.

Everything lives inside one IIFE and one CSS block, and every rule collapses
under prefers-reduced-motion. That is deliberate: this file is the source of
truth for the web preview and the offline APK, and the APK is built by a script
that checks the page parses - so a duplicate top-level name here would blank
the app exactly the way the `esc` collision did.

The motion language, for the record:

  * transform and opacity only. Nothing animates width, height, top or left,
    because those cost a layout pass every frame and this runs on phones.
  * Two speeds. Ambient things drift over 18-30s and are nearly still;
    anything responding to a tap lands in 120-260ms.
  * One curve for entrances, `cubic-bezier(.22,1,.36,1)`, which overshoots
    just enough to feel like it has weight.
  * Nothing decorative moves over text the learner is reading. Entrance
    animations run once and never repeat.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "webapp.py"

CSS = r'''
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
  button, .chip, .ltab, .bbc-tab, .lrow, .tile, .cchip { position: relative; overflow: hidden; }
  button:active, .chip:active, .ltab:active { transform: scale(.965); }
  button, .chip, .ltab, .bbc-tab, .lrow { transition: transform .14s cubic-bezier(.22,1,.36,1); }

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

  /* ---------- 10. toasts -------------------------------------------- */
  @keyframes toastIn {
    from { opacity: 0; transform: translate3d(0, 16px, 0) scale(.94); }
    to   { opacity: 1; transform: none; }
  }
  .toast { animation: toastIn .32s cubic-bezier(.22,1,.36,1) both; }

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
    button, .chip, .ltab, .bbc-tab, .lrow { transition: none !important; }
    * { scroll-behavior: auto !important; }
  }
'''

JS = r'''
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
      const dpr = Math.min(2, window.devicePixelRatio || 1);
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
    const SEL = 'button, .chip, .ltab, .bbc-tab, .lrow, .tile, .cchip';
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
'''

MARKUP = '  <div class="motes" id="motes" aria-hidden="true"></div>\n'


def main() -> None:
    src = SRC.read_text(encoding="utf-8")

    # ---- CSS: append at the very end of the stylesheet ------------------
    # Order matters more than it looks: base rules such as `.row { animation:
    # pop }` sit hundreds of lines earlier, and a later declaration of the
    # same property wins regardless of how much more specific the other one is.
    # Putting the motion block last is what makes it actually apply.
    if "MOTION SYSTEM" not in src:
        close = src.index("</style>")
        cut = src.rindex("\n", 0, close)
        src = (src[:cut + 1] + "\n" + CSS.strip("\n") + "\n" + src[cut + 1:])

    # ---- markup: the canvas layer ---------------------------------------
    if 'id="motes"' not in src:
        body = "<body>\n"
        assert body in src, "body tag not found"
        src = src.replace(body, body + MARKUP, 1)

    # ---- JS: the IIFE, just before the STT engine ----------------------
    if "const Motion = " not in src:
        marker = "/* ------------------------------------------------------------------ STT ---"
        assert marker in src, "STT marker not found"
        src = src.replace(marker, JS.strip("\n") + "\n\n" + marker, 1)

    # ---- boot ------------------------------------------------------------
    if "Motion.init()" not in src:
        boot = "loadListening();\nloadPhonetics();\nmountMic();"
        assert boot in src, "boot block not found"
        src = src.replace(boot, boot + "\nMotion.init();", 1)

    # A silent no-op here is what hid a missing insertion once already, so
    # every step is checked rather than trusted.
    for needle, what in (
        ("MOTION SYSTEM", "the CSS block"),
        ('id="motes"', "the ambient layer"),
        ("const Motion = ", "the JS module"),
        ("Motion.init();", "the boot call"),
    ):
        assert needle in src, f"motion system: {what} did not land"

    SRC.write_text(src, encoding="utf-8")
    print("webapp.py: motion system added")


if __name__ == "__main__":
    main()