#!/usr/bin/env python3
"""Step 2 of the bot.js port: the round-1/2 handler methods.

Mirrors chatbot.py one method at a time. Run tools/js_port_step1.py first.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JS = ROOT / "android/app/src/main/assets/www/bot.js"

METHODS = r'''
  /* ------------------------------------------------------------ numbers */

  handleNumber(text, lang) {
    const m = /^\s*(?:what(?:'s| is)|چند است|چنده)?\s*(?:the number\s+)?([a-z\- ]+?)\s*(?:in (?:english|فارسی))?\s*[?!؟]*\s*$/i
      .exec(text);
    if (!m) return null;
    const phrase = m[1].trim().toLowerCase();
    const value = numberFromWords(phrase);
    if (value === null) return null;
    const en = String(value);
    const fa = toPersianDigits(value);
    if (lang === 'fa')
      return `«${phrase}» → ${fa}  (${en})\nعدد ${en} به فارسی: ${fa}`;
    return `"${phrase}" → ${en} (${fa})\n${toEnglishDigits(value)}`;
  }

  /* -------------------------------------------------- confusable pairs */

  matchDistinction(text) {
    const flat = normalizeFa(text);
    let best = null, bestScore = 0;
    for (const [topicId, topic] of Object.entries(this.distinctions)) {
      const sets = [[3, topic.keywords.en], [2, topic.keywords.fa]];
      for (const [score, kws] of sets) {
        for (const kw of kws) {
          if (flat.includes(normalizeFa(kw)) && score > bestScore) {
            best = topicId; bestScore = score;
          }
        }
      }
    }
    return best;
  }

  formatDistinction(topicId) {
    const topic = this.distinctions[topicId];
    const lines = [`⚖️  ${topic.title.en}  ·  (${topic.title.fa})`,
      `   ↲ سطح: ${topic.level}`, '', topic.why];
    for (const side of topic.sides) {
      lines.push('');
      lines.push(`  • ${side.en}`);
      if (side.fa) lines.push(`    ↲ ${side.fa}`);
    }
    return lines.join('\n');
  }

  handleDistinction(text, lowered, lang) {
    const gate = /\b(difference|differ|confus|compare|versus|vs\b|which one|tell .*\bfrom\b|when (?:do|should|would) (?:i|we) use|when to use|usage of|تفاوت|فرق|کدام|چه تفاوتی|کی به کار ببرم)/;
    if (!gate.test(lowered + ' ' + text)) return null;
    const topicId = this.matchDistinction(text);
    if (topicId) return this.formatDistinction(topicId);
    const names = Object.values(this.distinctions).slice(0, 8)
      .map((t) => t.title.en).join(' · ');
    return `⚖️  Confusable pairs I can explain — جفت‌هایی که قاطی می‌شوند:\n${names}\n` +
      "Ask: 'difference between affect and effect' or 'تفاوت since و for'";
  }

  /* ------------------------------------------------------------- idioms */

  matchIdiom(word) {
    const key = normalizeWord(word);
    if (!key) return null;
    const bare = normalizeWord(stripArticle(word));
    for (const topic of Object.values(this.idioms)) {
      for (const row of topic.idioms) {
        const rowKey = normalizeWord(row.en);
        if (rowKey === key ||
            (bare && normalizeWord(stripArticle(row.en)) === bare)) return row;
        const head = key.split(' ');
        if (head.length >= 2 && rowKey.startsWith(head[0]) &&
            head.every((h) => rowKey.split(' ').includes(h))) return row;
      }
    }
    return null;
  }

  formatIdiom(row) {
    return `🗯  “${row.en}” — ${row.fa}\n   ↲ ${row.meaning}\n   e.g. ${row.example}`;
  }

  handleIdioms(text, lowered, lang) {
    let target = null;
    let m = /(?:meaning|mean|means|idiom|یعنی|معنی|معنی اصطلاح)\s*(?:of\s*)?["'‘’]?([a-z][a-z' \-]{2,30}?)["'‘’]?\s*[?!.؟]*\s*$/i
      .exec(lowered.trim());
    if (m) target = m[1];
    if (!target) {
      m = /["'‘’]([a-z][a-z' \-]{2,30}?)["'’]/.exec(lowered);
      if (m) target = m[1];
    }
    if (!target) {
      m = /^\s*(?:what is|what are|what's)\s+["'‘’]?([a-z][a-z' \-]{2,30}?)["'‘’]?\s*[?!.؟]*\s*$/i
        .exec(lowered);
      if (m && this.matchIdiom(m[1])) target = m[1];
    }
    if (!target) {
      m = /(?:what (?:does|do|is|are) |meaning of |یعنی |معنی |معنیِ )["'‘’]?([a-z][a-z' \-]{2,30}?)["'‘’]?\s+(?:mean|means|یعنی|چه معنی)/i
        .exec(lowered.trim());
      if (m) target = m[1];
    }
    if (target) {
      target = target.trim()
        .replace(/^(?:the\s+|what(?:'s| is| does)?\s+|meaning of\s+|mean\s+|یعنی\s+|معنی\s+)/i, '');
      const row = this.matchIdiom(target);
      if (row) return this.formatIdiom(row);
      return null;
    }

    const wantsList = /\b(idioms?|sayings?|phrases? (?:in english|list))\b/.test(lowered)
      || /اصطلاح|ضرب المثل انگلیسی/.test(text);
    if (!wantsList) return null;
    const rows = [];
    for (const t of Object.values(this.idioms)) rows.push(...t.idioms);
    const lines = ['🗯  Idioms & sayings — اصطلاح‌ها و ضرب‌المثل‌ها:'];
    for (const row of rows) lines.push(`   • ${row.en}  —  ${row.fa}`);
    lines.push('');
    lines.push("Ask: 'meaning of once in a blue moon' or 'معنی hit the books'");
    return lines.join('\n');
  }

  /* ---------------------------------------------------------- corrections */

  checkGrammar(sentence) {
    const found = [], seen = new Set();
    for (const rule of this.corrections) {
      let m;
      try { m = new RegExp(rule.pattern, 'i').exec(sentence); } catch (e) { continue; }
      if (!m) continue;
      if (rule.fix.includes('{sg}') && !/\w*s$/i.test(m[0])) continue;
      if (seen.has(rule.label)) continue;
      seen.add(rule.label);
      const was = m[0].replace(/\s+/g, ' ').trim();
      found.push({
        label: rule.label,
        fix: this.renderFix(rule.fix, m, sentence),
        why: rule.why,
        was,
        whole: this.applyFix(sentence, m, rule.fix),
      });
    }
    return found;
  }

  renderFix(fix, m, sentence) {
    if (!fix.includes('{')) return fix;
    const groups = (m.slice(1) || []).filter((g) => g !== undefined && g !== null);
    const words = (m[0].match(/[a-z']+/gi) || []);
    const pick = (i) => {
      if (i < groups.length) return groups[i].trim();
      if (!words.length) return '';
      return words[i < words.length ? i : words.length - 1];
    };
    const verb = words.length ? words[words.length - 1] : '';
    let out = fix;
    for (let i = 2; i >= 0; i--) out = out.split('{' + i + '}').join(pick(i));
    out = out.split('{base}').join(BASE_FORMS[verb.toLowerCase()] || verb);
    out = out.split('{pp}').join(pastParticiple(verb));
    out = out.split('{sg}').join(singular(verb));
    out = out.split('{th}').join(thirdPerson(pick(1)));
    return out.replace(/\s{2,}/g, ' ').trim();
  }

  applyFix(sentence, m, fix) {
    if (fix.includes('reorder') || fix.includes(' / ') || !m[0].trim()) return '';
    const rendered = this.renderFix(fix, m, sentence);
    if (rendered.includes('{') || !rendered) return '';
    const idx = sentence.indexOf(m[0]);
    if (idx < 0) return '';
    return (sentence.slice(0, idx) + rendered + sentence.slice(idx + m[0].length))
      .replace(/ {2,}/g, ' ').trim();
  }

  handleCorrection(text, lowered, lang) {
    const asked = /\b(is (?:this|that|it) (?:correct|right|wrong)|check my|correct (?:my|this|these|the)|fix (?:my|this|my sentence)|is this ok|grammatically|درسته|درست است|میشه|غلطه)/.test(lowered)
      || /درسته|غلط/.test(text);
    const sentence = text.replace(
      /^\s*(?:is (?:this|that|it) (?:sentence )?(?:correct|right|ok|wrong)\b[?:]?|(?:please\s+)?correct (?:this|my|these|the)?\s*(?:sentence|text)?\b[:]?|check (?:this|that|my)\s*(?:sentence|text)?\b[:]?|fix (?:my|this)\s*(?:sentence)?\b[:]?|آیا این جمله درسته[؟?]?)\s*/i,
      '').replace(/^[\s.?!؟،,]+|[\s.?!؟،,]+$/g, '');
    if (!sentence) return null;
    if (FA_RE.test(sentence) && !asked) return null;
    const looksLikeQuestion = sentence.includes('?') || sentence.includes('؟');
    let problems = asked ? this.checkGrammar(sentence) : this.checkGrammar(sentence);
    if (!asked && !problems.length) return null;
    if (looksLikeQuestion && !asked) return null;
    if (!asked && sentence.split(/\s+/).length < 2) return null;

    if (!problems.length) {
      return asked
        ? (lang === 'en'
          ? '✅ That sentence is correct English.  ↲ این جمله درست است.'
          : '✅ این جمله درست است. / That sentence is correct English.')
        : null;
    }
    const head = problems.length > 1
      ? '✏️  A couple of things to fix — چند نکته برای اصلاح:'
      : '✏️  One thing to fix — یک نکته برای اصلاح:';
    const lines = [head];
    for (const p of problems) {
      let whole = p.whole;
      const isSg = this.corrections.some((r) => r.fix.includes('{sg}') &&
        r.label === p.label);
      if (whole && isSg) {
        whole = whole.replace(
          /\b(many|a|an|several|few)\s+(information|advice|equipment|furniture|software|research|homework|knowledge)\b/gi,
          (mm, det, noun) =>
            (det.toLowerCase() === 'many' ? 'much ' : 'some ') + noun);
      }
      lines.push(`   • ${p.was}  →  ${p.fix}`);
      lines.push(`     ${p.why}`);
      if (whole) whole = whole;
      p.resolved = whole;
    }
    const whole = problems.map((p) => p.resolved).find(Boolean);
    if (whole) {
      lines.push('');
      lines.push(`✅ Better: ${whole}`);
    }
    return lines.join('\n');
  }

  /* ---------------------------------------------------------- pronounce */

  lookupPhrase(phrase) {
    const key = normalizeWord(phrase);
    const bare = normalizeWord(stripArticle(phrase));
    if (!key || key.length < 3) return null;
    for (const [k, v] of Object.entries(CORE_PHRASES)) {
      const nk = normalizeWord(k);
      if (nk === key || nk === bare) return { en: v[0], fa: v[1] };
    }
    let best = null;
    for (const topic of Object.values(this.phrases)) {
      for (const line of topic.phrases) {
        const norm = normalizeWord(line.en);
        if (norm === key) return line;
        if (norm.includes(key)) {
          if (!best || norm.length < best[0].length) best = [norm, line];
        }
      }
    }
    return best ? best[1] : null;
  }

  handlePronounce(text, lowered, lang) {
    let word = null;
    const m = /(?:how (?:do (?:you|i|we) )?(?:say|pronounce|read)|how to (?:say|pronounce)|تلفظ|چطور\s*(?:بگویم|بگم)|چگونه\s*بگویم)\s*(?:کلمه|the word|word)?\s*["'‘’]?([^"'‘’]*?)["'‘’]?\s*[?!.؟]*\s*$/i
      .exec(lowered);
    if (m) {
      word = m[1].trim().replace(/^(?:the\s+|word\s+|کلمه\s+|این\s+کلمه\s+)/i, '').trim();
    } else {
      const faReq = /تلفظ|چطور\s*(?:بگویم|بگم)|چگونه\s*بگویم/.test(text);
      const fa = faReq ? /[؀-ۿ]{2,20}/.exec(text) : null;
      if (!fa) return null;
      word = fa[0];
    }

    const tokens = word.split(/\s+/).filter(Boolean);
    const stopish = (w) => LOOKUP_STOPWORDS.has(w.toLowerCase()) ||
      ['word', 'words', 'this', 'that', 'it'].includes(w.toLowerCase());
    if (!tokens.length || tokens.every(stopish)) {
      return '🗣  Give me the word and I\'ll help you say it.\n' +
        '   ↲ کلمه را بگو تا با هم تلفظش کنیم.\n' +
        "   Try: 'how do you pronounce hospital'";
    }

    const key = normalizeWord(word);
    const entries = this.lookupWord(key);
    if (entries.length) {
      const [, en, fa] = entries[0];
      const lines = [`🗣  ${en}  —  ${fa}`,
        `   Say it slowly: ${en[0].toUpperCase()} · ${en.slice(1).split('').join(' · ')}`,
        `   Stress: ${markStress(en)} — the capital part carries the beat`];
      const note = firstSoundNote(en);
      if (note) lines.push(`   Tip: ${note}.`);
      lines.push("   ↲ For the full guide ask: 'phonetics'");
      return lines.join('\n');
    }

    const phrase = this.lookupPhrase(key);
    if (phrase) {
      const lines = [`🗣  “${phrase.en}”`, `   ↲ ${phrase.fa}`];
      if (phrase.en.length <= 24)
        lines.push(`   Say it slowly: ${phrase.en.split('').join(' · ')}`);
      lines.push("   ↲ For the full guide ask: 'phonetics'");
      return lines.join('\n');
    }

    const slow = word.split('').join(' · ');
    return `🗣  “${word}” is not in my vocabulary list yet, so I cannot give you its Persian meaning.\n` +
      `   ↲ «${word}» هنوز در واژگان من نیست.\n` +
      `   Say it slowly: ${slow} · stress: ${markStress(key)}\n` +
      `   Ask 'idioms' or 'difference between ${word} and ...' to look it up from another angle.`;
  }

  /* --------------------------------------------------------------- stat */

  handleStat(text, lowered, lang) {
    const gate = /how many (words|things|sentences|lessons)|what can you do|your (vocabulary|stats|abilities)|چند (کلمه|لغت|جمله)|چه کارهایی|توانایی|آمار|your vocabulary/;
    if (!gate.test(lowered + ' ' + text)) return null;
    const n = (x) => (lang === 'fa' ? toPersianDigits(x) : String(x));
    let words = 0;
    for (const dom of Object.values(this.glossary)) words += dom.words.length;
    const domains = Object.keys(this.glossary).length;
    const topics = Object.keys(this.grammar).length;
    let qs = 0;
    for (const t of Object.values(this.grammar))
      qs += (t.practice || []).length + (t.exam || []).length;
    let idiomCount = 0;
    for (const t of Object.values(this.idioms)) idiomCount += t.idioms.length;
    return `📊 What I know — چه چیزهایی می‌دانم:\n` +
      `   • Vocabulary: ${n(words)} words in ${n(domains)} domains (A1 → C2)\n` +
      `   • Grammar: ${n(topics)} lessons, ${n(qs)} exercises\n` +
      `   • Phrases: ${this.phrases.length} banks · Listening: ${this.listening.length} levels\n` +
      `   • Idioms: ${idiomCount} · Distinctions: ${Object.keys(this.distinctions).length} confusable pairs`;
  }

'''


def main() -> None:
    src = JS.read_text(encoding="utf-8")

    anchor = "  /* ------------------------------------------------------------ respond */"
    assert anchor in src, "respond marker not found"
    src = src.replace(anchor, METHODS.strip("\n") + "\n\n" + anchor, 1)

    # bare CEFR level → that listening band (mirrors chatbot.py)
    old = """    if (!asked) return null;
    const level = this.matchListeningLevel(text, lowered);
    if (level) return this.formatListeningLevel(level);"""
    new = """    // a learner often just types the band itself: "A1", "b2", "C2"
    const bare = /^\\s*([abc][12])\\s*[?!.؟]*\\s*$/.exec(lowered);
    if (!asked && !bare) return null;
    let level = this.matchListeningLevel(text, lowered);
    if (!level && bare) level = this.matchListeningLevel(bare[1], bare[1]);
    if (level) return this.formatListeningLevel(level);"""
    assert old in src, "listening gate not found"
    src = src.replace(old, new, 1)

    # the new handlers must sit before the glossary lookup, exactly as in
    # chatbot.py's respond()
    old_resp = """    let result = this.handleAlphabet(text, lowered);
    if (result === null) result = this.handleLetterLookup(text);
    if (result === null) result = this.handleGrammar(text, lowered, lang);"""
    new_resp = """    let result = this.handleAlphabet(text, lowered);
    if (result === null) result = this.handleLetterLookup(text);
    if (result === null) result = this.handleNumber(text, lang);
    if (result === null) result = this.handlePronounce(text, lowered, lang);
    if (result === null) result = this.handleDistinction(text, lowered, lang);
    if (result === null) result = this.handleIdioms(text, lowered, lang);
    if (result === null) result = this.handleCorrection(text, lowered, lang);
    if (result === null) result = this.handleStat(text, lowered, lang);
    if (result === null) result = this.handleGrammar(text, lowered, lang);"""
    assert old_resp in src, "respond dispatch not found"
    src = src.replace(old_resp, new_resp, 1)

    JS.write_text(src, encoding="utf-8")
    print("bot.js: handlers + dispatch wired")


if __name__ == "__main__":
    main()