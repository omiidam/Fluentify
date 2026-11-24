/* The loading page's own markup and stylesheet.
 *
 * The overlay, its card and both of their stylesheets lived in webapp.py's page
 * template, which is a Python string: no formatter, no linter, no check that
 * the rule a comment describes is the rule written. They live here now, beside
 * the module that drives them, and tools/build_boot.py writes them out as
 * web/boot/boot.html and web/boot/boot.css for the page to inline.
 *
 * Both of them are still inlined as markup and CSS rather than injected by the
 * script: the loader has to be in the first frame a phone paints, and an
 * overlay created after the first long frame is exactly the blank screen it
 * exists to cover.
 */

export const BOOT_CSS = `
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
    /* Solid first, gradients second. A background made only of gradients is
       transparent until those gradients rasterise, so the very first frame of
       the cold start showed the page's own field, not this screen's; the
       colour underneath is the gradient's own middle stop, so a late raster
       is invisible rather than a flash of something else. */
    background-color: var(--surf-3);
    background-image:
      radial-gradient(95% 70% at 50% -10%, var(--surf-1) 0%, transparent 62%),
      radial-gradient(80% 60% at 108% 108%, var(--surf-3) 0%, transparent 58%),
      linear-gradient(158deg, var(--surf-2) 0%, var(--surf-3) 52%, var(--surf-3) 100%);
    transition: opacity .4s cubic-bezier(.22,1,.36,1), visibility .4s;
  }
  .boot.gone { opacity: 0; visibility: hidden; pointer-events: none; }

  /* Static color, moving light. No filter on an animated layer: a blur here
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
    /* The same two-step as the backdrop, for the same reason: the card has to
       be an opaque rounded rect in its first raster, and a gradient alone is
       not opaque until it has been rasterised. */
    background-color: var(--surf-2);
    background-image: linear-gradient(168deg, var(--surf-1), var(--surf-2) 58%, var(--surf-3));
    border: 1px solid rgba(205,159,60,.30);
    overflow: hidden;
    /* No entrance animation. It was a .72s rise-and-settle, and it cost the
       first frame the whole card's contents: a transform animation promotes
       the card to its own compositor layer, and on a cold renderer that layer
       rasterises a frame after the backdrop - the phone showed a rounded rect
       with nothing in it, then the fox, the wordmark and a bar at 0%. The
       loading screen is the first thing anyone sees; it arrives complete. */
  }
  /* The card's drop shadow - a 90px blur under a 460px rounded rect - is its
     most expensive paint, and the part of the card the eye reads last. Like
     the sweep below, it is added one frame after the card has painted. */
  html.boot-lit .boot-in {
    box-shadow: 0 40px 90px -28px rgba(74,58,30,.42),
      0 2px 0 var(--edge-light) inset;
  }
  /* One slow band of light crosses the card, so the surface is never still
     even while the bar is waiting. Transform only, and behind the content.

     It is created by html.boot-lit, one frame after the card has painted,
     rather than with the markup: a full-card gradient inside an animated
     pseudo-element is rastered into a layer of its own, and on a cold renderer
     that layer lands after the card it crosses. The band is transparent for
     the first 3.5 s of its 6.5 s cycle, so a frame of delay costs the
     animation nothing and saves the first frame a second full-card gradient. */
  .boot-in::after { content: none; }
  html.boot-lit .boot-in::after {
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

  /* Every line in the brand block is centred on the card's axis: the wordmark,
     the English line and the Persian one under it. The Persian line is its own
     rtl run, so it needs the alignment said out loud as well as the direction -
     rtl on its own puts it against the right edge, which is what made the two
     lines look like two separate columns. */
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
    font-size: 12px; line-height: 1.95; text-align: center;
  }

  /* A bouncing tile with its shadow on the floor. The shape is borrowed from
     a well-known loading animation; the color is the tutor's. Transform
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

  /* ---- the child's loading page ---------------------------------------
     The adult boot is a glass card with a tagline, three labelled tiles, a
     rotating fact and a footer: four sentences to read before the app has
     opened. A child gets none of them. What is left is a cream sticker with
     the mascot on a sun blob, three hopping letters and a rainbow bar - one
     picture, no prose, legible to someone who cannot read either language.
     The band is set in the document head from the stored account, so this is
     painted on the first frame; nothing here waits for the app to boot. */
  .boot-kid { display: none; }
  html[data-band="kids"] .boot {
    background:
      radial-gradient(60% 40% at 8% 0%, rgba(255, 138, 61, .30), transparent 70%),
      radial-gradient(55% 36% at 96% 6%, rgba(52, 120, 246, .22), transparent 72%),
      radial-gradient(62% 42% at 50% 106%, rgba(237, 106, 168, .26), transparent 72%),
      linear-gradient(160deg, var(--k-bg) 0%, var(--k-surface) 55%, var(--k-surface-2) 100%);
  }
  html[data-band="kids"] .boot-aurora { display: none; }
  html[data-band="kids"] .boot-in {
    width: min(100%, 420px); min-height: min(58vh, 500px); gap: 10px;
    padding: 34px 26px 22px; border-radius: 38px;
    border: 3px solid var(--k-boot-edge);
    background: linear-gradient(170deg, var(--k-surface) 0%, var(--k-surface-2) 100%);
    box-shadow: 0 10px 0 var(--k-boot-foot),
      0 34px 60px -26px rgba(120, 70, 20, .50),
      0 0 0 12px rgba(255, 255, 255, .40),
      0 0 74px rgba(255, 176, 64, .28);
    /* it arrives with a bounce instead of a fade: the first thing a child sees
       should feel like it landed, not like it loaded */
    animation: bkCardIn .9s cubic-bezier(.2, 1.5, .4, 1) both;
  }
  @keyframes bkCardIn {
    0% { opacity: 0; transform: scale(.78) translateY(14px); }
    62% { opacity: 1; transform: scale(1.035) translateY(0); }
    100% { opacity: 1; transform: scale(1); }
  }
  /* the card's own glint is replaced by a slow warm pulse behind everything */
  html[data-band="kids"] .boot-in::after {
    display: block; content: ''; position: absolute; inset: -30%; z-index: 0;
    background: radial-gradient(circle at 50% 24%, rgba(255, 190, 80, .30), transparent 62%);
    animation: bkGlow 4.2s ease-in-out infinite; pointer-events: none;
  }
  html[data-band="kids"] .boot-mark {
    position: relative; isolation: isolate;
    width: 156px; height: 156px; border-radius: 46% 54% 52% 48% / 50% 46% 54% 50%;
    background: radial-gradient(circle at 34% 26%, var(--k-c8-w), var(--k-c8) 74%);
    box-shadow: 0 7px 0 var(--k-boot-sun), inset 0 -8px 0 rgba(255, 255, 255, .32),
      0 0 46px rgba(255, 196, 80, .55);
    animation: bkBob 2.4s ease-in-out infinite;
  }
  /* the sun's rays, a ring of soft wedges turning behind the mascot */
  html[data-band="kids"] .boot-mark::before {
    content: ''; position: absolute; inset: -46%; z-index: -1; border-radius: 50%;
    background: repeating-conic-gradient(from 0deg,
      rgba(255, 176, 60, .34) 0deg 6deg, transparent 6deg 21deg);
    -webkit-mask: radial-gradient(circle, transparent 46%, rgba(0, 0, 0, 1) 48%, rgba(0, 0, 0, 1) 60%, transparent 62%);
    mask: radial-gradient(circle, transparent 46%, rgba(0, 0, 0, 1) 48%, rgba(0, 0, 0, 1) 60%, transparent 62%);
    animation: bkSpin 26s linear infinite;
  }
  /* and a breathing glow under it, so the card is never a still picture */
  html[data-band="kids"] .boot-mark::after {
    content: ''; position: absolute; inset: -30%; z-index: -2; border-radius: 50%;
    background: radial-gradient(circle, rgba(255, 190, 80, .60), rgba(255, 190, 80, 0) 68%);
    animation: bkGlow 2.8s ease-in-out infinite;
  }
  html[data-band="kids"] .boot-halo { display: none; }
  html[data-band="kids"] .boot-fox { width: 146px; height: 146px; }
body.kids .boot-fox { content: url("brand/kids-fox.png"); }html[data-band="kids"] .boot-name { font-size: 34px; letter-spacing: -.4px; }.boot-burst { position: absolute; inset: 0; pointer-events: none; z-index: -1; }.boot-burst i {
    position: absolute; left: 50%; top: 50%; width: 9px; height: 9px; border-radius: 50%;
    background: var(--k-c1); box-shadow: 0 0 10px rgba(255, 255, 255, .9);
    transform: translate(-50%, -50%) rotate(var(--a)) translateY(-40px) scale(.2);
    opacity: 0;
    animation: bkBurst 2.9s cubic-bezier(.2, .7, .3, 1) infinite;
    animation-delay: var(--d, 0s);
  }.boot-burst i:nth-child(2) { background: var(--k-c8); }.boot-burst i:nth-child(3) { background: var(--k-c3); }.boot-burst i:nth-child(4) { background: var(--k-c6); }.boot-burst i:nth-child(5) { background: var(--k-c5); }.boot-burst i:nth-child(6) { background: var(--k-c7); }.boot-burst i:nth-child(7) { background: var(--k-c2); }.boot-burst i:nth-child(8) { background: var(--k-c4); }html[data-band="kids"] .boot-tag,
  html[data-band="kids"] .boot-trio,
  html[data-band="kids"] .boot-facts,
  html[data-band="kids"] .boot-foot,
  html[data-band="kids"] .boot-meta,
  html[data-band="kids"] .loader { display: none; }html[data-band="kids"] .boot-wait { gap: 12px; }html[data-band="kids"] .boot-loading { gap: 0; }html[data-band="kids"] .boot-track {
    height: 18px; border-radius: 999px; background: var(--k-boot-track);
    box-shadow: inset 0 2px 0 rgba(120, 70, 20, .08), 0 0 18px rgba(255, 176, 64, .28);
  }html[data-band="kids"] .boot-track i {
    position: relative;
    background: linear-gradient(90deg, var(--k-c1) 0%, var(--k-c8) 34%,
      var(--k-c7) 62%, var(--k-c6) 100%);
    border-radius: 999px;
    box-shadow: 0 0 16px rgba(255, 176, 64, .55);
  }html[data-band="kids"] .boot-track i::before {
    content: ''; position: absolute; right: -4px; top: 50%; width: 22px; height: 22px;
    transform: translateY(-50%); border-radius: 50%;
    background: radial-gradient(circle, var(--k-c8) 0%, rgba(255, 205, 95, .85) 40%, rgba(255, 200, 90, 0) 74%);
    box-shadow: 0 0 22px rgba(255, 180, 60, .95);
    animation: bkGlow 1.7s ease-in-out infinite;
  }html[data-band="kids"] .boot-kid {
    position: relative; display: flex; align-items: flex-end; justify-content: center;
    width: 100%; height: 78px;
  }.boot-kid .bk-letters { display: flex; gap: 10px; align-items: flex-end; }.boot-kid .bk-letters i {
    width: 58px; height: 58px; display: grid; place-items: center;
    border-radius: 18px; font-style: normal; font-size: 32px; font-weight: 800;
    color: var(--k-on-primary);
    box-shadow: 0 6px 0 rgba(90, 45, 10, .24), 0 0 26px rgba(255, 255, 255, .70),
      inset 0 -5px 0 rgba(0, 0, 0, .10);
    animation: bkHop 1.35s cubic-bezier(.4, 1.5, .5, 1) infinite;
  }.boot-kid .bk-letters i:nth-child(1) { background: var(--k-c1); }.boot-kid .bk-letters i:nth-child(2) { background: var(--k-c3); animation-delay: .16s; }.boot-kid .bk-letters i:nth-child(3) { background: var(--k-c6); animation-delay: .32s; }.boot-kid .bk-fly { position: absolute; font-size: 20px; opacity: .95;
    animation: bkFloat 5.2s ease-in-out infinite; }.boot-kid .bk-a { left: 3%; top: 6px; animation-delay: -1s; }.boot-kid .bk-b { right: 5%; top: 0; animation-delay: -2.4s; }.boot-kid .bk-c { left: 15%; bottom: 2px; font-size: 18px; animation-delay: -3.3s; }.boot-kid .bk-d { right: 16%; bottom: 0; font-size: 17px; animation-delay: -.6s; }@keyframes bkHop {
    0%, 100% { transform: translateY(0) scale(1, 1); }
    35% { transform: translateY(-13px) scale(.96, 1.04); }
    60% { transform: translateY(0) scale(1.04, .96); }
  }@keyframes bkBurst {
    0% { opacity: 0; transform: translate(-50%, -50%) rotate(var(--a)) translateY(-42px) scale(.2); }
    18% { opacity: 1; }
    62% { opacity: 0; transform: translate(-50%, -50%) rotate(var(--a)) translateY(-104px) scale(1.15); }
    100% { opacity: 0; transform: translate(-50%, -50%) rotate(var(--a)) translateY(-104px) scale(.2); }
  }@keyframes bkSpin { to { transform: rotate(1turn); } }@keyframes bkGlow {
    0%, 100% { opacity: .55; }
    50% { opacity: 1; }
  }@keyframes bkFloat {
    0%, 100% { transform: translateY(0) rotate(-7deg); }
    50% { transform: translateY(-9px) rotate(9deg); }
  }@keyframes bkBob {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
  }@media (prefers-reduced-motion: reduce) {
    html[data-band="kids"] .boot-in,
    html[data-band="kids"] .boot-mark,
    html[data-band="kids"] .boot-in::after,
    html[data-band="kids"] .boot-mark::before,
    html[data-band="kids"] .boot-mark::after,
    html[data-band="kids"] .boot-track i::before,
    .boot-burst i,
    .boot-kid .bk-letters i,
    .boot-kid .bk-fly { animation: none; }
  }.boot-loading {
    width: 100%; display: flex; align-items: center; gap: 15px;
    margin-top: 2px;
  }
  /* ---- the chronograph ------------------------------------------------
     A luxury loader is an object, not a spinner. A minute track, a seconds
     hand sweeping without a tick, a sub-dial counting in steps. It says the
     same thing as the bar beside it - work is being measured - and it says
     it in the app's own materials: gold, slate, warm glass. */
  .chrono { width: 42px; height: 42px; flex: 0 0 42px; position: relative; }
  .ch-face {
    position: absolute; inset: 0; border-radius: 50%;
    background: radial-gradient(circle at 34% 26%, var(--surf-1) 0%, var(--surf-3) 76%);
    border: 1px solid var(--line2);
    box-shadow: inset 0 1px 0 var(--edge-light), 0 6px 16px rgba(74,58,30,.20);
  }
  /* the minute track: sixty hairlines, one repeating conic at the rim */
  .ch-face::before {
    content: ''; position: absolute; inset: 3px; border-radius: 50%;
    background: repeating-conic-gradient(from 0deg,
      var(--ink-4) 0 1deg, transparent 1deg 6deg);
    /* the minute track is cut out of the dial with a mask, and a mask reads
       alpha, not colour: --mask is the token that stays black in both themes */
    -webkit-mask: radial-gradient(circle, transparent 0 63%, var(--mask) 65%);
    mask: radial-gradient(circle, transparent 0 63%, var(--mask) 65%);
    opacity: .55;
  }
  .ch-face::after {
    content: ''; position: absolute; inset: 8px; border-radius: 50%;
    border: 1px solid var(--line);
    opacity: .7;
  }
  .ch-hand {
    position: absolute; left: 50%; bottom: 50%;
    width: 1.5px; height: 40%; margin-left: -.75px; border-radius: 1px;
    background: linear-gradient(180deg, var(--gold-ink), var(--gold-line));
    transform-origin: 50% 100%;
    animation: chSweep 6s linear infinite;
  }
  .ch-cap {
    position: absolute; left: 50%; top: 50%; width: 6px; height: 6px;
    margin: -3px 0 0 -3px; border-radius: 50%;
    background: var(--gold-ink); box-shadow: 0 0 0 2px var(--surf-1);
  }
  .ch-sub {
    position: absolute; right: -3px; bottom: -3px; width: 15px; height: 15px;
    border-radius: 50%; overflow: hidden; background: var(--surf-1);
    border: 1px solid var(--line2);
  }
  .ch-sub i {
    position: absolute; inset: 0; border-radius: 50%;
    background: conic-gradient(var(--gold-ink) 0 22%, transparent 22% 100%);
    animation: chSub 6s steps(8, end) infinite;
  }
  @keyframes chSweep { to { transform: rotate(1turn); } }
  @keyframes chSub { to { transform: rotate(1turn); } }
  html[data-band="kids"] .chrono { display: none; }

  /* the counter lands with a small overshoot, the way a chronograph counter
     does; the class is re-applied only when the whole number changes */
  .boot-meta #bootpct.tick { animation: bootTick .22s cubic-bezier(.2, 1.7, .5, 1); }
  @keyframes bootTick {
    0% { transform: scale(1); }
    45% { transform: scale(1.16); }
    100% { transform: scale(1); }
  }

  /* ---- opening titles: the card's parts arrive in sequence ------------
     One block of glass fading in is a splash screen. The mark, the wordmark,
     the three tiles, the reading line and the footer each land a beat after
     the one above, so the eye is led down the card while the app boots under
     it. Adults only: a child's screen is one picture, not a sequence. */
  .boot-eyebrow {
    display: inline-flex; align-items: center; gap: 8px;
    font-size: 9.5px; font-weight: 600; letter-spacing: .22em;
    text-transform: uppercase; color: var(--ink-4);
  }
  .boot-eyebrow::before, .boot-eyebrow::after {
    content: ''; width: 22px; height: 1px; background: currentColor; opacity: .45;
  }
  html[data-band="kids"] .boot-eyebrow { display: none; }
  html:not([data-band="kids"]) .boot-mark,
  html:not([data-band="kids"]) .boot-brand,
  html:not([data-band="kids"]) .boot-tile,
  html:not([data-band="kids"]) .boot-wait,
  html:not([data-band="kids"]) .boot-foot { animation: bootRise .62s cubic-bezier(.22,1,.36,1) both; }
  html:not([data-band="kids"]) .boot-mark { animation-delay: .04s; }
  html:not([data-band="kids"]) .boot-brand { animation-delay: .16s; }
  html:not([data-band="kids"]) .boot-tile:nth-child(1) { animation-delay: .24s; }
  html:not([data-band="kids"]) .boot-tile:nth-child(2) { animation-delay: .30s; }
  html:not([data-band="kids"]) .boot-tile:nth-child(3) { animation-delay: .36s; }
  html:not([data-band="kids"]) .boot-wait { animation-delay: .44s; }
  html:not([data-band="kids"]) .boot-foot { animation-delay: .54s; }
  @keyframes bootRise {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: none; }
  }

  /* ---- the curtain ----------------------------------------------------
     The exit is part of the loader, not a fade after it. The card lifts and
     dims, then the sheet over the app lifts from the bottom edge; the app
     itself settles in from a slow zoom behind it, so the loading screen
     becomes the page instead of being swapped for it. (No Barba.js here: this
     is one document with no navigations to intercept, and the APK has no
     network for a CDN.) */
  html:not([data-band="kids"]) .boot.gone {
    opacity: 1; visibility: visible;
    animation: bootCurtain .72s cubic-bezier(.62,0,.36,1) both;
  }
  /* The card fades where it stands. It used to lift 14px at the same time as
     the sheet began its .34s late sweep, and the two upward moves read as the
     loading page leaving twice. One thing moves up now, and it is the sheet. */
  html:not([data-band="kids"]) .boot.gone .boot-in {
    animation: bootCardOut .3s ease-in both;
  }
  @keyframes bootCardOut {
    to { opacity: 0; }
  }
  @keyframes bootCurtain {
    from { clip-path: inset(0 0 0 0); }
    to   { clip-path: inset(0 0 100% 0); }
  }
  .app.boot-settle { animation: bootSettle 1.15s cubic-bezier(.22,1,.36,1) both; }
  @keyframes bootSettle {
    from { opacity: .55; transform: scale(1.024); }
    to   { opacity: 1; transform: none; }
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
    .ch-hand, .ch-sub i, .boot-meta #bootpct.tick { animation: none; }
    .boot-track i { transition: none; }
    /* reduced motion still gets out, but by the shortest route: no curtain,
       no rise, no zoom - the sheet is just gone */
    html:not([data-band="kids"]) .boot.gone { animation: none; opacity: 0; visibility: hidden; }
    html:not([data-band="kids"]) .boot.gone .boot-in { animation: none; }
    html:not([data-band="kids"]) .boot-mark, html:not([data-band="kids"]) .boot-brand,
    html:not([data-band="kids"]) .boot-tile, html:not([data-band="kids"]) .boot-wait,
    html:not([data-band="kids"]) .boot-foot { animation: none; }
    .app.boot-settle { animation: none; }
  }

`;

export const BOOT_MARKUP = `<div class="boot" id="boot" role="status" aria-live="polite"
     aria-label="Loading Fluentify / در حال بارگذاری">
    <div class="boot-aurora" aria-hidden="true"><i></i><i></i><i></i></div>
    <div class="boot-in">
      <div class="boot-mark" aria-hidden="true">
        <span class="boot-halo"></span>
        <!-- the burst: eight sparks thrown outward from the mascot, each its
             own hue, staggered so the ring never fires all at once -->
        <span class="boot-burst"><i style="--a:0deg;--d:0s"></i><i style="--a:45deg;--d:.35s"></i><i style="--a:90deg;--d:.7s"></i><i style="--a:135deg;--d:1.05s"></i><i style="--a:180deg;--d:1.4s"></i><i style="--a:225deg;--d:1.75s"></i><i style="--a:270deg;--d:2.1s"></i><i style="--a:315deg;--d:2.45s"></i></span>
        <span class="boot-fox-bob">
          <img class="boot-fox" src="brand/fox-mark.png" alt="" width="100"
               height="100" fetchpriority="high" decoding="sync">
        </span>
      </div>
      <div class="boot-brand">
        <span class="boot-eyebrow" aria-hidden="true">English · Persian · every day</span>
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
          <!-- A chronograph instead of a spinner: a minute track, a seconds
               hand on a continuous sweep, and a sub-dial that ticks. The bar
               beside it is the same measurement in the plain. -->
          <div class="chrono">
            <span class="ch-face"><i class="ch-hand"></i><i class="ch-cap"></i></span>
            <span class="ch-sub"><i></i></span>
          </div>
          <div class="boot-track"><i id="bootfill"></i></div>
        </div>
        <div class="boot-meta">
          <span class="boot-left">Getting your day ready</span>
          <span id="bootpct">0%</span>
        </div>
      </div>
      <!-- The child's loading page: a sticker, a mascot, three bouncing
           letters and a rainbow bar. No sentence anywhere - the words on the
           adult version (tagline, three tiles, rotating facts, footer) are
           hidden by CSS when the account is a child's. -->
      <div class="boot-kid" aria-hidden="true">
        <span class="bk-fly bk-a">✏️</span>
        <span class="bk-fly bk-b">🌟</span>
        <span class="bk-fly bk-c">🎈</span>
        <span class="bk-fly bk-d">📚</span>
        <span class="bk-letters"><i>A</i><i>B</i><i>C</i></span>
      </div>
      <div class="boot-foot">
        Reading, listening and stories at your level
        <span dir="rtl" lang="fa">خواندن، شنیدن و داستان، در سطح خودت</span>
      </div>
    </div>
  </div>
`;
