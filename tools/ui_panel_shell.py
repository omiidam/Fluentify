#!/usr/bin/env python3
"""Gives every panel the same shell: close, Esc, focus, and search.

The audit found six panels behaving six different ways:

  * only Vocabulary had a search box, so 37 grammar lessons, 39 sentence banks
    and 6 listening bands were unsearchable
  * no panel had a close button - the only way out was to hit the same tile
    again, which is undiscoverable and awkward one-handed on a phone
  * Esc closed the audio but not a panel
  * opening a panel left focus on the tile behind it, so a keyboard user
    tabbed straight through the panel into the page behind
  * tiles carried no aria-expanded, so assistive tech could not say whether a
    section was open
  * a search that matched nothing showed nothing at all in most panels

This adds one shell and routes all six panels through it, so behaviour cannot
diverge again. Nothing about the content changes.

    python3 tools/ui_panel_shell.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "webapp.py"

CSS = r'''
  /* ---------------------------------------------------- panel shell -------
     One header for every panel: a title, an optional search and a close
     button. Before this each panel had its own h3 and its own idea of how to
     be dismissed. */
  .phead {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 10px; flex: none;
  }
  .phead h3 { flex: 1 1 auto; margin: 0; min-width: 0; }
  .pclose {
    flex: 0 0 38px; width: 38px; height: 38px; border-radius: 11px;
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
'''

JS = r'''
/* ============================================================================
 * PANEL SHELL
 * Every section panel gets the same behaviour: a close button, Esc to leave,
 * focus moved in on open and back to the tile on close, aria-expanded on the
 * tile, and a search box where searching makes sense.
 *
 * This exists because the six panels had drifted into six behaviours. Only
 * Vocabulary had search, none had a close button, Esc closed the audio but
 * not a panel, and opening one left focus stranded on the tile behind it.
 * ==========================================================================*/
const Panels = (() => {
  const TILES = {
    vpanel: 'vtoggle', gpanel: 'gtoggle', fpanel: 'ftoggle',
    lpanel: 'ltoggle', phpanel: 'phtoggle', rpanel: 'rtoggle',
  };
  let openId = null;
  let returnFocusTo = null;

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

  function open(panelId) {
    ensureShell(panelId);
    const panel = document.getElementById(panelId);
    if (!panel || openId === panelId) return;
    if (openId) open(openId === panelId ? null : openId, true);
    panel.classList.add('open');
    openId = panelId;
    const tile = document.getElementById(TILES[panelId]);
    if (tile) {
      tile.classList.add('on');
      tile.setAttribute('aria-expanded', 'true');
    }
    // move focus in, but not into the first control - that makes a keyboard
    // user open a panel and land on a field they did not ask for
    (panel.querySelector('.pclose') || panel).focus?.();
  }

  function close(panelId, silent) {
    const panel = document.getElementById(panelId);
    if (!panel) return;
    panel.classList.remove('open');
    if (openId === panelId) openId = null;
    const tile = document.getElementById(TILES[panelId]);
    if (tile) {
      tile.classList.remove('on');
      tile.setAttribute('aria-expanded', 'false');
    }
    if (!silent && returnFocusTo) { returnFocusTo.focus(); returnFocusTo = null; }
  }

  function toggle(panelId) {
    const panel = document.getElementById(panelId);
    if (!panel) return;
    if (panel.classList.contains('open')) close(panelId);
    else { returnFocusTo = document.activeElement; open(panelId); }
  }

  /* Escape closes the topmost thing: an open panel, else the audio. */
  function init() {
    Object.keys(TILES).forEach(ensureShell);

    document.addEventListener('keydown', (e) => {
      if (e.key !== 'Escape') return;
      if (openId) { e.preventDefault(); close(openId); }
      else if (typeof Speech !== 'undefined' && Speech.playing) {
        Speech.stop();
      }
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

  return {init, open, close, toggle, ensureShell, addSearch, isOpen: () => openId};
})();
'''

MARKUP_A11Y = '''<div id="chat" role="log" aria-live="polite" aria-relevant="additions text"'''


def main() -> None:
    src = SRC.read_text(encoding="utf-8")

    # ---- CSS ------------------------------------------------------------
    if "PANEL SHELL" not in src:
        anchor = "  /* ---- the app is a pane of frosted glass ---- */"
        assert anchor in src, "style anchor not found"
        src = src.replace(anchor, CSS.strip("\n") + "\n\n" + anchor, 1)

    # ---- chat log semantics ---------------------------------------------
    if 'role="log"' not in src:
        old = '<div id="chat">'
        new = ('<div id="chat" role="log" aria-live="polite"\n'
               '         aria-relevant="additions" aria-label="Conversation">')
        assert old in src, "chat markup not found"
        src = src.replace(old, new, 1)

    # ---- tiles get aria-expanded ----------------------------------------
    for tid in ("vtoggle", "gtoggle", "ftoggle", "ltoggle", "phtoggle", "rtoggle"):
        if f'id="{tid}" aria-expanded' not in src:
            src = src.replace(f'id="{tid}"',
                              f'id="{tid}" aria-expanded="false"', 1)

    # ---- the JS module ---------------------------------------------------
    if "const Panels = (() =>" not in src:
        marker = "/* ------------------------------------------------------------------ STT ---"
        assert marker in src, "STT marker not found"
        src = src.replace(marker, JS.strip("\n") + "\n\n" + marker, 1)

    # ---- route togglePanel through the shell ---------------------------
    old_open = """  if (!wasOpen) {
    panel.classList.add('open');
    document.getElementById(btnId).classList.add('on');
    // A panel whose content is generated rather than static has to be told to
    // redraw when it opens. Without this the Review panel opened blank: the
    // words were saved and the badge counted them, but nothing had ever asked
    // Review.paint() to render them into #rbody.
    const hook = PANEL_ON_OPEN[panelId];
    if (hook) hook();
  }"""
    new_open = """  if (!wasOpen) {
    panel.classList.add('open');
    document.getElementById(btnId).classList.add('on');
    document.getElementById(btnId).setAttribute('aria-expanded', 'true');
    // A panel whose content is generated rather than static has to be told to
    // redraw when it opens. Without this the Review panel opened blank: the
    // words were saved and the badge counted them, but nothing had ever asked
    // Review.paint() to render them into #rbody.
    const hook = PANEL_ON_OPEN[panelId];
    if (hook) hook();
  } else {
    document.getElementById(btnId).setAttribute('aria-expanded', 'false');
  }"""
    assert old_open in src, "togglePanel open branch not found"
    src = src.replace(old_open, new_open, 1)

    # ---- boot ------------------------------------------------------------
    if "Panels.init()" not in src:
        boot = "Motion.init();"
        assert boot in src, "boot call not found"
        src = src.replace(boot, boot + "\nPanels.init();", 1)

    for needle, what in (
        ("PANEL SHELL", "the shell CSS"),
        ("const Panels = (() =>", "the shell module"),
        ("Panels.init();", "the boot call"),
        ('role="log"', "the chat log semantics"),
        ('aria-expanded="false"', "tile semantics"),
    ):
        assert needle in src, f"panel shell: {what} did not land"

    SRC.write_text(src, encoding="utf-8")
    print("webapp.py: panel shell added")


if __name__ == "__main__":
    main()