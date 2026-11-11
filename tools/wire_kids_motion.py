#!/usr/bin/env python3
"""Wire the shared kids motion system into every kid section of webapp.py.

Each anchor below is asserted to occur exactly once, so this stops instead of
double-inserting when it is run again.
"""
import sys
from pathlib import Path

P = Path(__file__).parent.parent / "webapp.py"
src = P.read_text(encoding="utf-8")
assert "KIDS MOTION AND CHARACTERS" in src, "the css/js block is not in place"
if "KAnim.art(w.word" in src:
    print("already wired")
    sys.exit(0)


def sub(old, new):
    global src
    n = src.count(old)
    assert n == 1, (old.splitlines()[0][:70], n)
    src = src.replace(old, new, 1)


# 1. the say button carries a wave that follows the voice
sub("""  function sayButton(text) {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'ksay';
    b.textContent = '🔊';
    b.title = 'Hear it — بشنو';
    b.setAttribute('aria-label', 'Hear ' + text);
    b.onclick = () => Speech.speak(text);
    return b;
  }""",
"""  /* A say button and the wave that shows a voice is running. The wave is
     decoration over a control that already says what it does. */
  function sayButton(text) {
    const wrap = document.createElement('span');
    wrap.className = 'ksaywrap';
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'ksay';
    b.textContent = '🔊';
    b.title = 'Hear it — بشنو';
    b.setAttribute('aria-label', 'Hear ' + text);
    const wv = KAnim.wave();
    b.onclick = () => KAnim.say(text, wv, b);
    wrap.append(b, wv);
    return wrap;
  }""")

# 2. a right answer earns a burst; a wrong one only nudges
sub("""          if (right) {
            wrap.classList.add('kspark');""",
"""          if (right) {
            wrap.classList.add('kspark');
            KAnim.celebrate(wrap);""")
sub("""            wrap.appendChild(win);
          }
        };
        opts.appendChild(b);""",
"""            wrap.appendChild(win);
          } else {
            wrap.classList.add('knudge');
            setTimeout(() => wrap.classList.remove('knudge'), 400);
          }
        };
        opts.appendChild(b);""")

# 3. the home: the mascot waves, a calm switch, staggered doors
sub("""    face.innerHTML = '<img src="brand/fox-face.png" alt="" width="56" height="56">';""",
"""    /* The mascot herself, drawn as parts so she can wave. The PNG stays on
       the loading screen; this is the same fox in a form that can move. */
    face.appendChild(KAnim.fox('wave', 56));""")
sub("""    el.append(level, days);""",
"""    /* The one control a child needs to make the app quieter. It remembers,
       and once touched it overrides the system setting either way. */
    const calm = document.createElement('button');
    calm.type = 'button';
    calm.className = 'kchip kcalm';
    calm.setAttribute('aria-pressed', KAnim.calm() ? 'true' : 'false');
    calm.innerHTML = '<b>Calm mode</b><i>حرکت کمتر</i>';
    calm.onclick = () => {
      const on = KAnim.toggle();
      calm.setAttribute('aria-pressed', on ? 'true' : 'false');
    };
    el.append(level, days, calm);""")
sub("""      grid.appendChild(b);
    });
    return grid;""",
"""      grid.appendChild(b);
    });
    KAnim.stagger(grid);
    return grid;""")
sub("""    panel.innerHTML = '';
    if (!d) {""",
"""    panel.innerHTML = '';
    KAnim.boot();
    if (!d) {""")

# 4. every section list arrives in one staggered entrance
for anchor in ("""        () => themeWords(d, theme), (theme.words || []).length + ' words'));""",
               """        () => grammarLesson(d, lesson), (lesson.quiz || []).length + ' games'));""",
               """      wrap.appendChild(listButton('story', item, () => storyView(item), ''));""",
               """        () => passageView(passage), ''));""",
               """        () => clipView(clip), (clip.lines || []).length + ' lines'));""",
               """        () => phraseSet(set), (set.items || []).length + ' sentences'));"""):
    sub(anchor + "\n    });\n    box.appendChild(wrap);",
        anchor + "\n    });\n    box.appendChild(wrap);\n    KAnim.stagger(wrap);")

# 5. words: a picture that moves the way the word means
sub("""      row.append(body, fa(w.fa), sayButton(w.word + '. ' + w.example_en));""",
"""      row.append(KAnim.art(w.word, theme.emoji), body, fa(w.fa),
        sayButton(w.word + '. ' + w.example_en));""")

# 6. grammar: a thinking fox, and the example as moving word tiles
sub("""    card.appendChild(fa(lesson.title_fa, 'kfa-h'));""",
"""    card.appendChild(fa(lesson.title_fa, 'kfa-h'));
    card.appendChild(KAnim.hint('think',
      'Read the example, then watch its words move into place.',
      'نمونه را بخوان، بعد ببین واژه‌هایش سر جایشان می‌نشینند.'));""")
sub("""      en.className = 'ken';
      en.textContent = e.en;""",
"""      en.className = 'ken kseq';
      String(e.en || '').split(/\\s+/).forEach((word) => {
        const tile = document.createElement('i');
        tile.textContent = word;
        en.appendChild(tile);
      });""")

# 7. stories: a scene, and one press that reads it line by line
sub("""    box.appendChild(back('All stories', stories));""",
"""    box.appendChild(back('All stories', stories));
    box.appendChild(KAnim.scene('Story time', 'وقت داستان', 'read'));""")
sub("""    (st.lines || []).forEach((line) => {
      const row = document.createElement('div');
      row.className = 'krow';""",
"""    const rows = [];
    const texts = [];
    (st.lines || []).forEach((line) => {
      const row = document.createElement('div');
      row.className = 'krow kline';
      rows.push(row);
      texts.push(line.en);""")
sub("""    card.appendChild(fa(st.title_fa, 'kfa-h'));""",
"""    card.appendChild(fa(st.title_fa, 'kfa-h'));
    /* One press reads the whole story and lights the line being spoken. The
       same engine and the same strings, so it reads the same offline. */
    const readAll = document.createElement('button');
    readAll.type = 'button';
    readAll.className = 'kbtn kc-coral';
    readAll.innerHTML = '<span class="kico">🔊</span><b>Read the story to me</b>' +
      '<span class="kfa" dir="rtl" lang="fa">داستان را برایم بخوان</span>';
    const readWave = KAnim.wave();
    readAll.onclick = () => {
      if (readAll.dataset.on === '1') {
        KAnim.stopLines();
        readAll.dataset.on = '0';
        readWave.classList.remove('on');
        return;
      }
      readAll.dataset.on = '1';
      readWave.classList.add('on');
      KAnim.playLines(rows, texts, () => {
        readAll.dataset.on = '0';
        readWave.classList.remove('on');
      });
    };
    card.append(readAll, readWave);""")

# 8. reading: a scene above the passage
sub("""    box.appendChild(back('All passages', reading));""",
"""    box.appendChild(back('All passages', reading));
    box.appendChild(KAnim.scene('Reading time', 'وقت خواندن', 'read'));""")

# 9. listening: a listening fox, and a wave on the clip it plays
sub("""    box.appendChild(back('All clips', listening));""",
"""    box.appendChild(back('All clips', listening));
    box.appendChild(KAnim.scene('Listen closely', 'خوب گوش کن', 'listen'));""")
sub("""    playAll.onclick = () => Speech.speak((clip.lines || []).join(' '));
    card.appendChild(playAll);""",
"""    const allWave = KAnim.wave();
    playAll.onclick = () => KAnim.say((clip.lines || []).join(' '), allWave, playAll);
    card.append(playAll, allWave);""")

# 10. sentences: read it out loud, then listen
sub("""    card.appendChild(fa(set.title_fa, 'kfa-h'));""",
"""    card.appendChild(fa(set.title_fa, 'kfa-h'));
    card.appendChild(KAnim.hint('speak', 'Read it out loud, then listen and compare.',
      'بلند بخوان، بعد گوش کن و مقایسه کن.'));""")

# 11. the fox listens while the child is typing
sub("""      ADVANCED.forEach((id) => { const b = $(id); if (b) b.classList.add('kadv'); });
    }
    const more = $('kidsmore');""",
"""      ADVANCED.forEach((id) => { const b = $(id); if (b) b.classList.add('kadv'); });
    }
    /* The fox on the home card listens while the child is typing and waves
       again when they leave. Nothing is stored: it follows the field. */
    const field = $('input');
    if (field && !field.dataset.kfox) {
      field.dataset.kfox = '1';
      const face = () => document.querySelector('.khero .kface .kchar');
      field.addEventListener('focus', () => {
        const f = face();
        if (f) f.setAttribute('data-mood', 'listen');
      });
      field.addEventListener('blur', () => {
        const f = face();
        if (f) f.setAttribute('data-mood', 'wave');
      });
    }
    KAnim.apply();
    const more = $('kidsmore');""")

P.write_text(src, encoding="utf-8")
print("wired every kids section")
