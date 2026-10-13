#!/usr/bin/env python3
"""Gives Grammar, Sentences, Listening and Sounds the same search Vocabulary has.

The audit found that only one of six panels could be searched. That is not a
cosmetic gap: the Sentences panel holds 39 banks and 445 sentences, and
Grammar holds 37 lessons. Neither can be found by anything but scrolling and
reading every heading.

The search is deliberately generic - hide the items that do not match, count
what is left, and say so plainly when nothing does - rather than one bespoke
filter per panel, which is how the six panels ended up behaving six different
ways in the first place.

    python3 tools/ui_panel_search.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "webapp.py"

# (loader, panel, selector of the repeated items, where to hang the search,
#  placeholder, what a "match" means)
PANELS = [
    ("loadGrammar", "gpanel", ".gcat, .gitem",
     "Search 37 lessons… / جست‌وجوی درس‌ها…",
     "Greetings and Introducing  Daily Routine  Travel & Airport  Directions"),
    ("loadPhrases", "fpanel", ".fcat",
     "Search 39 sentence banks… / جست‌وجوی موضوع‌ها…",
     "Vocabulary  Numbers  Time  Days  Months  Family  Food  Colours"),
    ("loadListening", "lpanel", ".lrow",
     None, None),          # handled separately: it has level tabs
    ("loadPhonetics", "phpanel", ".phsec, .phrow",
     "Search the sounds… / جست‌وجوی صداها…",
     "schwa  stress  vowels  voiced  rhythm  intonation"),
]


def main() -> None:
    src = SRC.read_text(encoding="utf-8")

    if "const PanelSearch = (() =>" in src:
        print("panel search already added")
        return

    MODULE = r'''
/* ============================================================================
 * PANEL SEARCH
 * Vocabulary had a search box and the other five panels did not, so 37
 * grammar lessons and 39 sentence banks could only be found by scrolling.
 *
 * This is generic on purpose: hide what does not match, report what is left,
 * and say so when nothing does. One implementation means the panels cannot
 * drift apart again the way they did.
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

    const box = emptyFor(panelId);
    if (state.tabs) state.tabs(q, shown);

    if (q && shown === 0) {
      box.innerHTML = 'Nothing matches <b>' + (needle.length > 28
        ? needle.slice(0, 28) + '…' : needle) + '</b>.<br>' +
        'چیزی پیدا نشد — املای دیگری را امتحان کن.';
      box.hidden = false;
    } else {
      box.hidden = true;
    }

    if (state.status && document.getElementById(state.status)) {
      const node = document.getElementById(state.status);
      node.textContent = q
        ? `${shown} of ${state.items.length} · ${needle}`
        : `${state.items.length} · نمایش همه`;
    }
  }

  /* selector: what the panel repeats. tabs: optional level filter to keep in
     step, because a search that leaves every level visible looks broken. */
  function attach(panelId, selector, placeholder, opts = {}) {
    const panel = document.getElementById(panelId);
    if (!panel || attached.has(panelId)) return;
    const items = [...panel.querySelectorAll(selector)];
    if (!items.length) return;      // content not loaded yet; boot calls again
    attached.set(panelId, {items, tabs: opts.tabs, status: opts.status});

    const status = document.createElement('div');
    status.className = 'pcount';
    status.id = panelId + 'count';
    status.textContent = `${items.length} · نمایش همه`;

    Panels.addSearch(panelId, placeholder, (v) => apply(panelId, v));
    const box = panel.querySelector('.psearch');
    if (box && box.nextSibling) box.after(status);
    else panel.prepend(status);
  }

  function attachAll() {
    attach('gpanel', '.gcat, .gitem',
      'Search 37 lessons… / جست‌وجوی درس‌ها…');
    attach('fpanel', '.fcat, .frow',
      'Search 39 sentence banks… / جست‌وجوی موضوع‌ها…');
    attach('phpanel', '.phsec, .phrow, .phgroup',
      'Search the sounds… / جست‌وجوی صداها…');
    // Listening has level tabs of its own; search the sentences inside them.
    attach('lpanel', '.lrow',
      'Search the sentences… / جست‌وجوی جمله‌ها…',
      {tabs: (q) => { document.querySelectorAll('#lpanel .ltab').forEach((t) => {
        t.hidden = !!q && !t.title.toLowerCase().includes(q);
      }); }});
  }

  return {attachAll, apply};
})();
'''

    # ---- CSS ---------------------------------------------------------
    css = r'''
  .pcount {
    flex: none; margin: -4px 2px 8px; font-size: 11.5px; color: #7d8fd4;
    letter-spacing: .01em;
  }
'''
    anchor = "  /* ---- the app is a pane of frosted glass ---- */"
    assert anchor in src, "style anchor missing"
    src = src.replace(anchor, css.strip("\n") + "\n\n" + anchor, 1)

    # ---- the module ---------------------------------------------------
    marker = "/* ------------------------------------------------------------------ STT ---"
    assert marker in src, "STT marker missing"
    src = src.replace(marker, MODULE.strip("\n") + "\n\n" + marker, 1)

    # ---- run it after every panel finishes loading --------------------
    old = "Panels.init();"
    new = ("Panels.init();\n"
           "PanelSearch.attachAll();   // once the panels have content")
    assert old in src
    src = src.replace(old, new, 1)

    # ...and again when a panel is opened, in case it loaded later
    old_hook = """const PANEL_ON_OPEN = {
  rpanel: () => { Review.load(); Review.paint(); },
};"""
    new_hook = """const PANEL_ON_OPEN = {
  rpanel: () => { Review.load(); Review.paint(); },
  // search is attached on first open rather than at boot, because the panels
  // are filled asynchronously and a search with nothing to filter is useless
  gpanel: () => PanelSearch.attachAll(),
  fpanel: () => PanelSearch.attachAll(),
  lpanel: () => PanelSearch.attachAll(),
  phpanel: () => PanelSearch.attachAll(),
};"""
    assert old_hook in src, "PANEL_ON_OPEN not found"
    src = src.replace(old_hook, new_hook, 1)

    # ---- re-apply the live filter after a panel re-renders --------------
    src = src.replace("""    render(levels[0], 0);""",
                      """    render(levels[0], 0);
    PanelSearch.attachAll();""", 1)

    SRC.write_text(src, encoding="utf-8")
    print("webapp.py: panel search added")


if __name__ == "__main__":
    main()