#!/usr/bin/env python3
"""Step 3 of the bot.js port: conversation memory, follow-up commands, sections.

Round 3 of the harness drove multi-turn flows; the JS engine needs the same
behaviour or the APK bot answers "exercises" with a dictionary miss.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JS = ROOT / "android/app/src/main/assets/www/bot.js"

BLOCK = r'''
  /* --------------------------------------------- conversation memory ----- */

  sectionWords() {
    if (!this._sections) {
      this._sections = {
        vocabulary: ['\u{1F4DA} Vocabulary', 'واژگان'],
        words: ['\u{1F4DA} Vocabulary', 'واژگان'],
        'واژگان': ['\u{1F4DA} Vocabulary', 'واژگان'],
        'کلمات': ['\u{1F4DA} Vocabulary', 'واژگان'],
        sentences: ['\u{1F4AC} Sentence banks', 'جملات'],
        phrases: ['\u{1F4AC} Sentence banks', 'جملات'],
        'جملات': ['\u{1F4AC} Sentence banks', 'جملات'],
        'جمله': ['\u{1F4AC} Sentence banks', 'جملات'],
        phonetics: ['\u{1F5E3} Sounds & phonetics', 'تلفظ'],
        'تلفظ': ['\u{1F5E3} Sounds & phonetics', 'تلفظ'],
        'آوا': ['\u{1F5E3} Sounds & phonetics', 'تلفظ'],
        grammar: ['\u{1F4D8} Grammar lessons', 'گرامر'],
        'گرامر': ['\u{1F4D8} Grammar lessons', 'گرامر'],
        listening: ['\u{1F3A7} Listening', 'شنیدن'],
        'شنیدن': ['\u{1F3A7} Listening', 'شنیدن'],
      };
    }
    return this._sections;
  }

  /* A bare section name has to return content, not a panel hint: the terminal
   * has no top bar, so pointing at one would be useless. */
  handleSection(text, lowered, lang) {
    let s = lowered.replace(/[.!?؟,;:"'«»()[\]]/g, '').trim();
    s = s.replace(/^(?:open|show|باز کن|نشان بده|نمایش)\s+/i, '').trim();
    const key = this.sectionWords()[s];
    if (!key) return null;
    const [title, titleFa] = key;

    if (title.startsWith('\u{1F4DA}')) {
      let groups = this.glossaryGroups.length ? this.glossaryGroups : [
        { id: 'all', en: 'All domains', fa: 'همه دامنه‌ها',
          domains: Object.keys(this.glossary) }];
      let total = 0;
      for (const dom of Object.values(this.glossary)) total += dom.words.length;
      const lines = [`${title} — ${titleFa} · ${Object.keys(this.glossary).length} domains, ${total} words`];
      for (const g of groups.slice(0, 8)) {
        const names = (g.domains || []).filter((d) => this.glossary[d])
          .map((d) => this.glossary[d].label.en);
        if (!names.length) continue;
        lines.push(`   • ${g.en}: ${names.slice(0, 6).join(', ')}` +
          (names.length > 6 ? '…' : ''));
      }
      lines.push('');
      lines.push("Ask for one by name — 'fruits', 'colors', 'advanced adjectives'.");
      return lines.join('\n');
    }

    if (title.startsWith('\u{1F4AC}')) {
      const lines = [`${title} — ${titleFa} · ${Object.keys(this.phrases).length} banks`];
      for (const topic of Object.values(this.phrases))
        lines.push(`   • ${topic.title.en} (${topic.title.fa})`);
      lines.push('');
      lines.push("Ask for one by name — 'travel sentences', 'daily routine'.");
      return lines.join('\n');
    }

    if (title.startsWith('\u{1F5E3}')) {
      const lines = [`${title} — ${titleFa} · ${this.phonetics.length} sections`];
      for (const sec of this.phonetics) {
        const ts = sec.title || {};
        lines.push(`   ${sec.icon || '•'} ${ts.en || '?'} (${ts.fa || ''}) — ${sec.level || ''}`);
      }
      lines.push('');
      lines.push('Open 🗣 Sounds in the app for the rows and the audio.');
      return lines.join('\n');
    }

    if (title.startsWith('\u{1F4D8}')) return this.handleGrammar(text, lowered, lang);
    if (title.startsWith('\u{1F3A7}')) return this.handleListening(text, lowered, lang);
    return null;
  }

  /* -------------------------------------------- contextual follow-ups ---- */

  bareTable(name) {
    if (!this._bare) this._bare = {};
    if (this._bare[name]) return this._bare[name];
    const t = {
      exercise: {
        exercises: 'practice', exercise: 'practice', practice: 'practice',
        'lets practice': 'practice', 'let us practice': 'practice',
        'i want to practice': 'practice', 'start practice': 'practice',
        'begin practice': 'practice', 'practice exercises': 'practice',
        quiz: 'exam', exam: 'exam', test: 'exam',
        'lets take the exam': 'exam', 'i want the exam': 'exam',
        'give me the exam': 'exam', 'final exam': 'exam',
        'تمرین': 'practice', 'تمرین کن': 'practice', 'تمرین بده': 'practice',
        'امتحان': 'exam', 'آزمون': 'exam', 'آزمون بده': 'exam' },
      cancel: ['cancel', 'stop', 'quit', 'exit', 'close', 'enough', 'never mind',
        'nevermind', 'end', 'finish', 'i give up', 'give up', 'بیخیال', 'لغو',
        'کنسل', 'بس کن', 'توقف', 'رد کن'],
      next: ['next', 'next question', 'next one', 'continue', 'go on', 'skip',
        'skip this', 'another question', 'بعدی', 'سوال بعدی', 'ادامه',
        'برو بعدی', 'رد کن اینو'],
      again: ['another one', 'again', 'one more', 'another joke',
        'tell me another', 'tell me another joke', 'another', 'more jokes',
        'again please', 'یکی دیگه', 'یکی دیگه بگو', 'دوباره', 'جوک دیگه',
        'یه جوک دیگه'],
      repeat: ['repeat that', 'say that again', 'say it again', 'again please',
        'one more time', 'pardon', 'come again', 'what did you say', 'what',
        '听不懂', 'دوباره بگو', 'تکرار کن', 'چی گفتی'],
      show: ['show answer', 'the answer', 'answer please',
        'what is the answer', 'give me the answer', 'answer', 'solution',
        'جواب', 'جواب بده', 'پاسخ', 'پاسخ درست'],
      examples: ['examples', 'more examples', 'give me examples',
        'show examples', 'another example', 'example sentences',
        'more examples please', 'مثال', 'مثال بیشتر', 'مثال بده'],
    };
    this._bare[name] = t[name];
    return t[name];
  }

  /* Bare words need an exact hit: 'next' must not fire inside 'what is the
   * next colour', or the bot would skip ahead while answering a question. */
  bare(lowered, table) {
    const s = lowered.replace(/[.!?؟,;:"'«»()[\]]/g, '').trim();
    if (Object.prototype.hasOwnProperty.call(table, s)) return table[s];
    const m = /^(?:please\s+)?(?:can you\s+|could you\s+)?(?:give me|tell me|show me|let me|start|begin|open)\s+[\w' ]{0,24}$/
      .exec(s);
    if (m) {
      const last = s.split(/\s+/).pop();
      if (Object.prototype.hasOwnProperty.call(table, last)) return table[last];
    }
    return null;
  }

  handleFollowup(text, lowered, lang) {
    if (this.exercise) return null;   // a live quiz owns every message

    const which = this.bare(lowered, this.bareTable('exercise'));
    if (which) {
      if (!this.lastLesson) {
        return lang === 'en'
          ? "Open a lesson first, then say 'exercises'.\n   ↳ اول یک درس را باز کن، بعد بنویس «تمرین».\n   Write 'grammar' for the list of lessons."
          : 'اول یک درس را باز کن، بعد بنویس «تمرین».\n   For the list of lessons write \'گرامر\'.';
      }
      return this.startGrammarSession(this.lastLesson, which, lang);
    }

    if (this.bare(lowered, this.bareTable('cancel'))) {
      this.lastLesson = null;
      this.lastExamples = [];
      return lang === 'en' ? '👍 Canceled. / لغو شد.' : '👍 لغو شد. / Canceled.';
    }

    if (this.bare(lowered, this.bareTable('show'))) {
      if (this.lastExamples && this.lastExamples.length)
        return lang === 'en'
          ? `💡 Answer: ${this.lastExamples.join(' / ')}\n   ↳ جواب: ${this.lastExamples.join(' / ')}`
          : `💡 جواب: ${this.lastExamples.join(' / ')}\n   Answer: ${this.lastExamples.join(' / ')}`;
      if (this.lastLevel) return this.formatListeningLevel(this.lastLevel);
      return lang === 'en'
        ? 'Nothing to reveal yet — open a lesson or ask me a question.\n   ↳ هنوز چیزی برای نمایش نیست — یک درس را باز کن.'
        : 'هنوز چیزی برای نمایش نیست — یک درس را باز کن.';
    }

    if (this.bare(lowered, this.bareTable('examples'))) {
      const topic = this.grammar[this.lastLesson];
      if (topic) {
        const rows = topic.examples || [];
        this.lastExamples = exampleAnswers(topic);
        return '📝 More examples — مثال‌های بیشتر:\n' + rows.map((r, i) =>
          `   ${i + 1}. ${r.en}\n      ↳ ${r.fa}`).join('\n');
      }
      return 'Open a lesson first and ask for examples.\n   ↳ اول یک درس را باز کن.';
    }

    if (this.bare(lowered, this.bareTable('again'))) return this.tellJoke(text, lang);

    if (this.bare(lowered, this.bareTable('repeat'))) {
      if (this.lastLevel) return this.formatListeningLevel(this.lastLevel);
      if (this.lastPhrase) {
        const topic = this.phrases[this.lastPhrase];
        if (topic) return 'Say it again — دوباره گوش کن:\n' + topic.phrases.slice(0, 4)
          .map((r) => `   • ${r.en}\n     ↳ ${r.fa}`).join('\n');
      }
      return lang === 'en'
        ? 'Tell me what to repeat — a listening band or a sentence bank.\n   ↳ بگو کدام را تکرار کنم.'
        : 'بگو کدام را تکرار کنم.';
    }

    if (this.bare(lowered, this.bareTable('next')) && this.lastLesson)
      return this.startGrammarSession(this.lastLesson, 'practice', lang);

    return null;
  }

'''


def main() -> None:
    src = JS.read_text(encoding="utf-8")

    # the module-level helper Python has as a staticmethod
    src = src.replace(
        "function push(map, key, value) {",
        """/* The taught forms inside a lesson's examples, for 'show answer'.
 * Each example is written as 'He **goes** to work.' so the bolded span is the
 * answer; if an example has no bold, the whole line is offered. */
function exampleAnswers(topic) {
  const out = [];
  for (const row of (topic.examples || []).slice(0, 4)) {
    const en = row.en || '';
    const bold = en.match(/\\*\\*(.+?)\\*\\*/g);
    if (bold) out.push(bold.map((b) => b.replace(/\\*\\*/g, '')).join(' / '));
    else if (en) out.push(en.replace(/\\.$/, ''));
  }
  return out;
}

function push(map, key, value) {""", 1)

    anchor = "  /* ------------------------------------------------------------ respond */"
    assert anchor in src
    src = src.replace(anchor, BLOCK.strip("\n") + "\n\n" + anchor, 1)

    # state
    src = src.replace(
        "    this.lastJokeId = null;",
        """    this.lastJokeId = null;
    // What the learner is looking at right now. Without this, "exercises"
    // after a lesson is a dictionary miss instead of "start that lesson".
    this.lastLesson = null;
    this.lastPhrase = null;
    this.lastLevel = null;
    this.lastExamples = [];""", 1)

    src = src.replace(
        "    this.corrections = (data.corrections && data.corrections.rules) ||\n      data.corrections || [];",
        """    this.corrections = (data.corrections && data.corrections.rules) ||
      data.corrections || [];
    this.phonetics = (data.phonetics && data.phonetics.sections) ||
      data.phonetics || [];""", 1)

    # remember what we just showed
    src = src.replace(
        "    if (level) return this.formatListeningLevel(level);",
        "    if (level) { this.lastLevel = level; return this.formatListeningLevel(level); }", 1)

    # one shared entry point for both the named and the bare quiz routes
    old_grammar_head = "  handleGrammar(text, lowered, lang) {"
    start_grammar = '''  startGrammarSession(topicId, stage, lang) {
    const topic = this.grammar[topicId];
    this.lastLesson = topicId;
    if (stage === 'exam') {
      if (!this.practiceDone.has(topicId)) {
        const n = lang === 'fa'
          ? toPersianDigits((topic.practice || []).length)
          : String((topic.practice || []).length);
        const title = lang === 'fa' ? topic.title.fa : topic.title.en;
        return lang === 'fa'
          ? `🔒 آزمون قفل است — اول تمرین (${n} سوال) را کامل کن.\\nبنویس: 'تمرین ${title}'`
          : `🔒 The exam is locked — finish the practice first (${n} questions).\\nType: '${topic.title.en.toLowerCase()} exercises'`;
      }
      const intro = lang === 'fa'
        ? `🎓 شروع آزمون «${topic.title.fa}» — موفق باشی!\\n`
        : `🎓 Starting the '${topic.title.en}' exam — good luck!\\n`;
      this.exercise = { topic: topicId, index: 0, lang, stage: 'exam' };
      this.exerciseScore = 0;
      return intro + this.formatExerciseCard(topic, 0, lang, 'exam');
    }
    const intro = lang === 'fa'
      ? `✏️ شروع تمرین «${topic.title.fa}» — موفق باشی!\\n`
      : `✏️ Starting '${topic.title.en}' practice — good luck!\\n`;
    this.exercise = { topic: topicId, index: 0, lang, stage: 'practice' };
    this.exerciseScore = 0;
    return intro + this.formatExerciseCard(topic, 0, lang, 'practice');
  }

  handleGrammar(text, lowered, lang) {'''
    assert old_grammar_head in src
    src = src.replace(old_grammar_head, start_grammar, 1)

    # dispatch
    src = src.replace(
        """    let result = this.handleAlphabet(text, lowered);
    if (result === null) result = this.handleLetterLookup(text);""",
        """    const section = this.handleSection(text, lowered, lang);
    if (section !== null) return section;

    const followup = this.handleFollowup(text, lowered, lang);
    if (followup !== null) return followup;

    let result = this.handleAlphabet(text, lowered);
    if (result === null) result = this.handleLetterLookup(text);""", 1)

    JS.write_text(src, encoding="utf-8")
    print("bot.js: conversation memory + follow-ups + sections wired")
    print("now collapse handleGrammar's inline quiz branches onto startGrammarSession")


if __name__ == "__main__":
    main()