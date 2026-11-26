/* ---- the boot screen ----
 * The first thing a learner sees is the fox walking in, and it is her four
 * seconds that hold the screen: the walk is the design, so it is never cut
 * short, and the sections are counted behind it so the screen never claims to
 * be ready before it is.
 *
 * It always comes down. Four ways out, and the point of listing them is that
 * any one of them failing still leaves the app usable. A loader that cannot
 * be dismissed is worse than no loader: it is a blank screen with an
 * animation on it, and there is no way to tell that from a crash.
 *
 *   1. the walk finishing and the sections landing, both
 *   2. an uncaught error, which otherwise leaves the overlay over a page that
 *      is mostly working and so looks broken
 *   3. a rejected promise, which would otherwise be silent
 *   4. a deadline, for the case where a fetch simply never settles
 *
 * Authored in TypeScript and built to web/boot/boot.js, which both the web
 * page and the offline build inline as it is shipped. Python used to hold this
 * module as a string inside the page template; a string is not a language
 * anything can check, so the loader - the one screen that must never fail on
 * the way in - had no compile step, no types, and no way to catch a typo
 * before a learner's first frame. The build is tools/build_boot.py.
 */

declare const ChatFox: { mount(): void };
declare function composerFocus(): void;

interface BootApi {
  /** Kept for callers that want to explain the wait. */
  say(): void;
  /** A section landed: `done` of `total` have their data. */
  step(done: number, total: number): void;
  /** Every section is in; the floor and the bar still decide the exit. */
  ready(): void;
  /** Take the card down now. Idempotent. */
  hide(): void;
}

const Boot: BootApi = (() => {
  const noop: BootApi = { say() {}, step() {}, ready() {}, hide() {} };
  const el = document.getElementById('boot');
  if (!el) return noop;

  /* The card's sweep and drop shadow wait for html.boot-lit, so the first
     raster carries the card and the fox instead of a second full-card gradient
     on top of them. Two frames, not one: a single requestAnimationFrame
     callback runs before that frame is painted, which would put the sweep back
     into the frame this keeps it out of. */
  const frame = typeof requestAnimationFrame === 'function'
    ? requestAnimationFrame : (fn: FrameRequestCallback) => setTimeout(fn, 16);
  frame(() => frame(() => document.documentElement.classList.add('boot-lit')));

  /* The card is the app's opening screen and it runs for five seconds, by the
     owner's decision. The reads behind it usually finish first; if one does
     not, the screen stays until the bar actually reaches 100%, which is what
     makes the number honest, and the ceiling below still bounds the wait. An
     error or a rejection takes it down at once. */
  const FLOOR_MS = 5000;     // the card's own time, not the load's
  const CEILING_MS = 8000;   // past this the user is watching a spinner, not a load

  const fill = document.getElementById('bootfill') as HTMLElement | null;
  const pct = document.getElementById('bootpct') as HTMLElement | null;
  const factBox = document.getElementById('bootfacts') as HTMLElement | null;
  const fact = document.getElementById('bootfact') as HTMLElement | null;
  const factFa = document.getElementById('bootfactfa') as HTMLElement | null;
  /* What the app is, not which file is being read: the three tiles above say
     what the day holds, and this line says what the rest of the shelf does.
     Both languages are written here so they cannot drift apart. */
  const FACTS: ReadonlyArray<readonly [string, string]> = [
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

  function showFact(k: number): void {
    const pair = FACTS[k % FACTS.length];
    if (!factBox || !fact || !factFa) return;
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

  let lastPct = -1;

  function paint(): void {
    if (fill) fill.style.transform = 'scaleX(' + shown + ')';
    if (pct) {
      const n = Math.round(shown * 100);
      if (n === lastPct) return;
      lastPct = n;
      pct.textContent = n + '%';
      /* the counter lands, it does not slide: the class is re-applied only
         when the whole number changes, so the overshoot fires once per percent
         instead of once per frame */
      pct.classList.remove('tick');
      void pct.offsetWidth;
      pct.classList.add('tick');
    }
  }

  /* Timed, not frame-based. A rAF loop stops dead whenever the page is hidden —
     and this overlay covers the very moment a phone is still locked or the tab
     is still in the background — so a frame-counter would leave the bar parked
     at whatever it had reached and never arrive. Elapsed time is used instead,
     with a 90ms half-life, so a tick that arrives late (a throttled timer, a
     janky frame) closes the same share of the gap a smooth one would. */
  function tick(): void {
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

  function aim(next: number): void {
    const want = Number.isFinite(next) ? next : 0;
    /* never goes backwards, never past full: a caller that reports more
       sections than it announced still cannot paint 107% */
    target = Math.max(target, Math.min(1, Math.max(0, want)));
    if (gone) return;                               // nothing left to paint on
    if (calm.matches) { shown = target; paint(); maybe(); return; }
    if (!timer && shown !== target) { last = 0; timer = setTimeout(tick, 0); }
  }

  paint();   // 0% over an empty bar, before the first section lands

  function hide(): void {
    if (gone) return;
    gone = true;
    clearTimeout(timer);
    timer = 0;
    clearTimeout(deadline);
    clearInterval(factTimer);
    if (factBox) factBox.classList.remove('swap');
    /* Adults get the curtain: card out, sheet lifted, app settling in from a
       slow zoom behind it. A child gets the plain fade, which is the screen
       they already know. Both still leave the tree. */
    const kid = document.documentElement.dataset.band === 'kids';
    const app = document.querySelector('.app');
    if (!kid && app) {
      app.classList.add('boot-settle');
      setTimeout(() => app.classList.remove('boot-settle'), 1500);
    }
    el.classList.add('gone');
    /* How long the sheet takes to clear the screen: bootCurtain in the
       stylesheet, which moves the whole overlay up by its own height. It is
       not the removal timer below - that only takes the empty element out of
       the tree. */
    const lift = kid ? 0 : 660;
    // Removed as well as faded: left in the tree it stays a full-screen
    // element that a later focus can land on.
    setTimeout(() => {
      if (el.parentNode) el.parentNode.removeChild(el);
    }, kid ? 400 : 1250);
    /* The page is hers now: she climbs out of the composer once the boot card
       is off the screen, so the first thing seen after loading is not a
       static corner. Timed to the sheet clearing rather than to hide() being
       called: mounted at once, she and the welcome card played their entrance
       underneath a loader that was still half over the chatroom. */
    setTimeout(() => {
      try { ChatFox.mount(); } catch (e) { /* a boot without a composer */ }
      try { composerFocus(); } catch (e) { /* a boot without a text field */ }
    }, lift);
  }

  /* Three conditions now, in whichever order they arrive: the floor the design
     asks for, the sections being in, and the bar having actually arrived at
     100%. The third is what makes the number honest at the end - the bar used
     to be able to show 96% and then be whisked away under a label that had
     already said 100%, because the dismissal and the paint were on separate
     clocks. The floor is on a timer rather than on a promise so that a slow
     section cannot extend it, and the ceiling still gets the screen down if
     the data never lands (the bar then says so, by stopping short). */
  function maybe(): void { if (floorUp && dataIn && shown >= 1) hide(); }

  setTimeout(() => { floorUp = true; maybe(); }, FLOOR_MS);

  deadline = setTimeout(hide, CEILING_MS);
  window.addEventListener('error', hide);
  window.addEventListener('unhandledrejection', hide);

  return {
    /* Kept for callers that want to explain the wait; the card itself now
       shows only the bar and its percentage. */
    say() {},
    step(done: number, total: number): void {
      /* A section list that reported nothing is a load with no steps, and an
         unknown total must not become a division by zero and a NaN bar. */
      if (!total || total <= 0) { aim(0); return; }
      aim(Math.min(1, Math.max(0, done) / total));
    },
    /* Every section is in. The overlay still holds until the floor passes. */
    ready(): void { dataIn = true; maybe(); },
    hide,
  };
})();
