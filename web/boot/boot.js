var Boot = (() => {
  const noop = { say() {}, step() {}, ready() {}, hide() {} };
  const el = document.getElementById("boot");
  if (!el)
    return noop;
  const frame = typeof requestAnimationFrame === "function" ? requestAnimationFrame : (fn) => setTimeout(fn, 16);
  frame(() => frame(() => document.documentElement.classList.add("boot-lit")));
  const FLOOR_MS = 5000;
  const CEILING_MS = 8000;
  const fill = document.getElementById("bootfill");
  const pct = document.getElementById("bootpct");
  const factBox = document.getElementById("bootfacts");
  const fact = document.getElementById("bootfact");
  const factFa = document.getElementById("bootfactfa");
  const FACTS = [
    ["50 graded stories, A1 to C1", "۵۰ داستان سطح‌بندی‌شده، از A1 تا C1"],
    [
      "A word, an expression, a conversation — every day",
      "هر روز یک واژه، یک عبارت، یک گفت‌وگو"
    ],
    [
      "A level check across five skills, once a month",
      "سنجش سطح در پنج مهارت، ماهی یک بار"
    ],
    [
      "Listening from A1 to C2, read aloud on your device",
      "شنیدن از A1 تا C2، با صدای دستگاه"
    ],
    [
      "48 grammar lessons and an analyser that runs offline",
      "۴۸ درس گرامر و تحلیل‌گری که آفلاین کار می‌کند"
    ]
  ];
  const calm = window.matchMedia("(prefers-reduced-motion: reduce)");
  let factAt = 0;
  let factTimer = 0;
  function showFact(k) {
    const pair = FACTS[k % FACTS.length];
    if (!factBox || !fact || !factFa)
      return;
    factBox.classList.add("swap");
    setTimeout(() => {
      fact.textContent = pair[0];
      factFa.textContent = pair[1];
      factBox.classList.remove("swap");
    }, 320);
  }
  if (!calm.matches && FACTS.length > 1) {
    factTimer = setInterval(() => showFact(++factAt), 2100);
  }
  let gone = false;
  let floorUp = false;
  let dataIn = false;
  let deadline = 0;
  let target = 0;
  let shown = 0;
  let timer = 0;
  let last = 0;
  let lastPct = -1;
  function paint() {
    if (fill)
      fill.style.transform = "scaleX(" + shown + ")";
    if (pct) {
      const n = Math.round(shown * 100);
      if (n === lastPct)
        return;
      lastPct = n;
      pct.textContent = n + "%";
      pct.classList.remove("tick");
      pct.offsetWidth;
      pct.classList.add("tick");
    }
  }
  function tick() {
    timer = 0;
    const now = performance.now();
    const dt = last ? Math.min(400, now - last) : 16;
    last = now;
    const gap = target - shown;
    if (gap < 0.0006) {
      shown = target;
      paint();
      maybe();
      return;
    }
    shown += gap * (1 - Math.pow(0.5, dt / 90));
    paint();
    timer = setTimeout(tick, 16);
  }
  function aim(next) {
    const want = Number.isFinite(next) ? next : 0;
    target = Math.max(target, Math.min(1, Math.max(0, want)));
    if (gone)
      return;
    if (calm.matches) {
      shown = target;
      paint();
      maybe();
      return;
    }
    if (!timer && shown !== target) {
      last = 0;
      timer = setTimeout(tick, 0);
    }
  }
  paint();
  function hide() {
    if (gone)
      return;
    gone = true;
    clearTimeout(timer);
    timer = 0;
    clearTimeout(deadline);
    clearInterval(factTimer);
    if (factBox)
      factBox.classList.remove("swap");
    const kid = document.documentElement.dataset.band === "kids";
    const app = document.querySelector(".app");
    if (!kid && app) {
      app.classList.add("boot-settle");
      setTimeout(() => app.classList.remove("boot-settle"), 1500);
    }
    el.classList.add("gone");
    setTimeout(() => {
      if (el.parentNode)
        el.parentNode.removeChild(el);
    }, kid ? 400 : 1250);
    try {
      ChatFox.mount();
    } catch (e) {}
    try {
      composerFocus();
    } catch (e) {}
  }
  function maybe() {
    if (floorUp && dataIn && shown >= 1)
      hide();
  }
  setTimeout(() => {
    floorUp = true;
    maybe();
  }, FLOOR_MS);
  deadline = setTimeout(hide, CEILING_MS);
  window.addEventListener("error", hide);
  window.addEventListener("unhandledrejection", hide);
  return {
    say() {},
    step(done, total) {
      if (!total || total <= 0) {
        aim(0);
        return;
      }
      aim(Math.min(1, Math.max(0, done) / total));
    },
    ready() {
      dataIn = true;
      maybe();
    },
    hide
  };
})();
