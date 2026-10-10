/* Fluentify — chatbot engine (JavaScript port of chatbot.py)
 *
 * Mirrors the Python implementation 1:1 so the offline APK behaves exactly
 * like the CLI / web preview: same intent scoring, same keyword precedence,
 * same exercise session, same glossary and grammar formatting.
 * All content comes from the JSON files next to this file in /data.
 */

const FA_RE = /[؀-ۿ]/;
const FA_DAREG = /[ً-ْٰ]/g;

const toPersianDigits = (n) => String(n).replace(/\d/g, (d) => '۰۱۲۳۴۵۶۷۸۹'[d]);
const fromPersianDigits = (s) => s.replace(/[۰-۹]/g, (d) => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d));

const detectLang = (text) => (FA_RE.test(text) ? 'fa' : 'en');

function normalizeFa(text) {
  let t = fromPersianDigits(text);
  t = t.replace(/‌/g, '').replace(/ي/g, 'ی').replace(/ك/g, 'ک');
  t = t.replace(FA_DAREG, '');
  return t.replace(/\s+/g, '').trim();
}

function normalizeEn(text) {
  // NOTE: JS \w is ASCII-only, but Python's \w (re.UNICODE) includes Persian
  // letters. Without \p{L} here every Persian string normalises to "" and
  // substring checks match everything.
  return text.toLowerCase().replace(/[^\p{L}\p{N}_\s']/gu, '').trim();
}

const normalizeWord = (text) => normalizeEn(normalizeFa(text));

/* Escape a string for literal use inside a RegExp. */
const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

/* \b<word>\b with optional simple plural. */
const wordRe = (kw, plural = false) =>
  new RegExp('\\b' + esc(kw) + (plural && kw.length >= 3 ? '(?:s|es)?' : '') + '\\b');

const LOOKUP_STOPWORDS = new Set([
  'it', 'this', 'that', 'is', 'are', 'mean', 'means', 'the', 'a', 'an',
  'what', 'which', 'word', 'translate', 'define',
  'این', 'اون', 'است', 'چیه', 'چیست', 'کلمه', 'معنی',
  'اسمت', 'نامت', 'اسم', 'تو', 'شما', 'من', 'خودت',
]);

const EN_LOOKUP_PATTERNS = [
  /what is the (?:english|persian|farsi) (?:word|translation) for\s+(.+)/i,
  /how do (?:i|you) say\s+(.+?)\s+in\s+(?:english|persian|farsi)/i,
  /what does\s+(.+?)\s+means?\b/i,
  /meaning of\s+(.+)/i,
  /define\s+(.+)/i,
  /translate\s+(.+?)(?:\s+(?:to|in)\s+(?:english|persian|farsi))?$/i,
  /what(?:'s| is| are)\s+(.+?)\s+in\s+(english|persian|farsi)\s*[?.!]*$/i,
  /(.+?)\s+in\s+(english|persian|farsi)\s*[?.!]*$/i,
];

const FA_LOOKUP_PATTERNS = [
  /معنی\s+(.+?)\s*(?:چیه|چیست|هست)/,
  /(.+?)\s*یعنی\s*چه/,
  /(?:چطوری|چطور|چجوری)\s+(.+?)\s+بگم/,
  /ترجمه\s+(.+)/,
  /کلمه\s+(.+?)\s*(?:چیه|چیست)/,
  /(.+?)\s+به\s+(?:انگلیسی|فارسی)/,
  /به\s+(?:انگلیسی|فارسی)\s+(.+)/,
  /(.+?)\s*(?:چیه|چیست)$/,
];

const HELP_TEXT = {
  en:
    "I can do all of this:\n" +
    "- Chat about daily things (how are you, I'm bored, tell me a joke...)\n" +
    "- English alphabet  → ask: 'english alphabet'\n" +
    "- Persian alphabet  → ask: 'persian alphabet' or 'الفبای فارسی'\n" +
    "- Letter lookup      → ask: 'what letter is A' or 'حرف ب'\n" +
    "- Translate words    → ask: 'translate apple' or 'سیب به انگلیسی'\n" +
    "- Define words       → ask: 'what does خوشحال mean' or 'define شیر'\n" +
    "- Vocabulary domains → ask: 'what are the colors' or 'حیوانات'\n" +
    "- Grammar lessons    → ask: 'grammar', then 'simple present' or 'حال ساده'\n" +
    "- Everyday sentences → ask: 'travel sentences' or 'جملات سفر'\n" +
    "- Grammar practice   → ask: 'simple present exercises' or 'تمرین حال ساده'\n" +
    "- Current time/date  → ask: 'what time is it' or 'ساعت چنده'\n" +
    "- Remember your name → say: 'my name is ...' or 'اسم من ... است'\n" +
    "Type 'bye' to exit.",
  fa:
    "من این کارها رو بلدم:\n" +
    "- مکالمه روزمره (حال تو چطوره، جوک بگو، حوصله‌ام سر رفته...)\n" +
    "- الفبای انگلیسی  → بپرس: 'english alphabet'\n" +
    "- الفبای فارسی    → بپرس: 'الفبای فارسی'\n" +
    "- جست‌وجوی حرف     → بپرس: 'حرف ب' یا 'what letter is A'\n" +
    "- ترجمه کلمات     → بپرس: 'سیب به انگلیسی' یا 'translate apple'\n" +
    "- معنی کلمات      → بپرس: 'معنی خوشحال چیه' یا 'what does شیر mean'\n" +
    "- دامنه‌های واژگان → بپرس: 'رنگها' یا 'what are the animals'\n" +
    "- درس گرامر        → بپرس: 'گرامر' بعد 'حال ساده' یا 'simple present'\n" +
    "- جملات کاربردی    → بپرس: 'جملات سفر' یا 'daily routine'\n" +
    "- تمرین گرامر      → بپرس: 'تمرین حال ساده' یا 'simple present exercises'\n" +
    "- ساعت و تاریخ     → بپرس: 'ساعت چنده' یا 'what time is it'\n" +
    "- یادآوری اسمت    → بگو: 'اسم من ... است' یا 'my name is ...'\n" +
    "برای خروج 'bye' یا 'خروج' رو بنویس.",
};

const EXIT_WORDS = [
  'bye', 'goodbye', 'exit', 'quit', 'stop', 'cancel', 'help', 'joke', 'menu', 'thanks',
];
const EXIT_WORDS_FA = ['خروج', 'خداحافظ', 'لغو', 'متوقف', 'توقف', 'راهنما', 'جوک', 'مرسی'];
const SHOW_WORDS = ['show answer', 'answer', 'skip', 'next', 'reveal', 'solution'];
const SHOW_WORDS_FA = ['جواب', 'حل کن', 'بعدی', 'نشون بده', 'رد شو'];

const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];

class Fluentify {
  constructor(data) {
    this.memory = data.memory;
    this.intents = this.memory.intents;
    // grammar / phrases: accept the whole file or just the inner map
    this.grammar = unwrapTopics(data.grammar);
    this.phrases = unwrapTopics(data.phrases);
    this.jokes = Array.isArray(data.jokes) ? data.jokes : data.jokes.jokes || [];

    // glossary: accept either the whole file or just its "domains" map
    const rawGlossary = data.glossary && data.glossary.domains ? data.glossary.domains : data.glossary;
    this.glossary = Object.assign({}, rawGlossary);
    this.glossaryGroups = this.glossary._groups || [];
    delete this.glossary._groups;

    this.glossaryEn = new Map();
    this.glossaryFa = new Map();
    for (const [domId, dom] of Object.entries(this.glossary)) {
      for (const w of dom.words) {
        const entry = [domId, w[0], w[1]];
        push(this.glossaryEn, normalizeWord(w[0]), entry);
        push(this.glossaryFa, normalizeWord(w[1]), entry);
        if (w.length > 2) push(this.glossaryEn, normalizeWord(w[2]), entry);
      }
    }

    this.userName = null;
    this.history = [];
    this.exercise = null;
    this.exerciseScore = 0;
    this.lastJokeId = null;
  }

  /* -------------------------------------------------------------- core */

  lookupWord(target) {
    const key = normalizeWord(target);
    if (!key) return [];
    const a = this.glossaryEn.get(key);
    if (a && a.length) return a;
    const b = this.glossaryFa.get(key);
    return b || [];
  }

  remember(text) {
    this.history.push(text);
    if (this.history.length > 100) this.history.shift();
  }

  learnName(text) {
    const m = text.match(
      /(?:my name is|call me|اسم من|اسمم|من هستم)\s+([^\s.,!?؟]+(?:\s+[^\s.,!?؟]+)?)/i
    );
    if (!m) return false;
    let name = m[1].trim().replace(/\s+(است|هستم|is)$/i, '');
    if (name) {
      this.userName = name;
      return true;
    }
    return false;
  }

  /* ---------------------------------------------------------- intents */

  matchIntent(text, lang) {
    const lowered = text.toLowerCase();
    let best = null;
    let bestScore = 0;
    for (const intent of this.intents) {
      let score = 0;
      for (const kw of intent.keywords[lang] || []) {
        const weight = kw.trim().split(/\s+/).length > 1 ? 3 : 2;
        if (lang === 'en') {
          if (wordRe(kw, true).test(lowered)) score += weight;
        } else if (text.includes(kw)) {
          score += weight;
        }
      }
      if (score > bestScore) {
        best = intent;
        bestScore = score;
      }
    }
    return bestScore >= 2 ? best : null;
  }

  replyFromIntent(intent, lang) {
    const responses = intent.responses[lang] || intent.responses.en;
    let reply = pick(responses);
    const name = this.userName || (lang === 'fa' ? 'دوست من' : 'friend');

    if (intent.name === 'greeting' && this.userName) {
      reply = reply.replace(/[!؛. ]+$/, '') + ' ' + this.userName + '!';
    }
    if (intent.name === 'time') {
      const now = new Date();
      if (lang === 'fa') {
        const hh = String(now.getHours()).padStart(2, '0');
        const mm = String(now.getMinutes()).padStart(2, '0');
        return 'الان ساعت ' + toPersianDigits(hh + ':' + mm) + ' است.';
      }
      let h = now.getHours();
      const ampm = h >= 12 ? 'PM' : 'AM';
      h = h % 12 || 12;
      return `It's ${h}:${String(now.getMinutes()).padStart(2, '0')} ${ampm}.`;
    }
    if (intent.name === 'date') {
      const now = new Date();
      if (lang === 'fa') {
        const ymd = `${now.getFullYear()}/${String(now.getMonth() + 1).padStart(2, '0')}/${String(now.getDate()).padStart(2, '0')}`;
        return 'امروز ' + toPersianDigits(ymd) + ' است.';
      }
      return 'Today is ' + now.toLocaleDateString('en-US', {
        weekday: 'long', month: 'long', day: 'numeric', year: 'numeric',
      }) + '.';
    }
    if (intent.name === 'help') return HELP_TEXT[lang];
    if ((intent.name === 'yes' || intent.name === 'no') && this.userName) reply += ' ' + name;
    return reply;
  }

  /* -------------------------------------------------------- alphabets */

  letters(language) {
    const info = this.memory.alphabets[language];
    return `${info.description_en} (${info.description_fa})\n${info.letters.join(' ')}`;
  }

  handleAlphabet(text, lowered) {
    if (this.matchGrammarTopic(text, lowered, 'fa') || this.matchGrammarTopic(text, lowered, 'en')) {
      return null;
    }
    const wantsPersian = lowered.includes('persian') || lowered.includes('farsi') || text.includes('فارسی');
    const wantsEnglish = lowered.includes('english') || text.includes('انگلیسی');
    const wantsAlphabet =
      ['alphabet', 'letters', 'abc', 'abjad'].some((w) => lowered.includes(w)) ||
      ['الفبا', 'حروف', 'ابجد'].some((w) => text.includes(w));
    if (!wantsAlphabet) return null;
    if (wantsPersian && !wantsEnglish) return this.letters('persian');
    if (wantsEnglish && !wantsPersian) return this.letters('english');
    return 'English: ' + this.letters('english') + '\n\nPersian: ' + this.letters('persian');
  }

  handleLetterLookup(text) {
    // \b is ASCII-only in JS, so it would never match after a Persian letter;
    // (?=\s|$) expresses "end of word" for any script.
    const m = text.match(/(?:letter|حرف)\s+(?:is\s+)?([a-z]|[؀-ۿ])(?=\s|$)/i);
    if (!m) return null;
    const ch = m[1];
    if (/^[a-z]$/i.test(ch)) {
      const letters = this.memory.alphabets.english.letters;
      const up = ch.toUpperCase();
      const idx = letters.indexOf(up);
      if (idx !== -1) return `'${up}' is letter number ${idx + 1} in the English alphabet.`;
    } else {
      const letters = this.memory.alphabets.persian.letters;
      const idx = letters.indexOf(ch);
      if (idx !== -1) return `«${ch}» حرف شماره ${toPersianDigits(idx + 1)} در الفبای فارسی است.`;
      return `«${ch}» در الفبای فارسی وجود ندارد.`;
    }
    return null;
  }

  /* ---------------------------------------------------------- grammar */

  matchGrammarTopic(text, lowered, lang) {
    let best = null;
    let bestLen = -1;
    for (const [topicId, topic] of Object.entries(this.grammar)) {
      for (const kw of topic.keywords[lang] || []) {
        const hit = lang === 'en' ? wordRe(kw).test(lowered) : text.includes(kw);
        if (hit && kw.length > bestLen) {
          best = [topicId, topic];
          bestLen = kw.length;
        }
      }
    }
    return best;
  }

  wantsGrammarMenu(text, lowered, lang) {
    if (lang === 'en') return ['grammar', 'grammer'].some((k) => wordRe(k).test(lowered));
    return ['گرامر', 'دستور زبان', 'قواعد'].some((k) => text.includes(k));
  }

  wantsExercises(text, lowered, lang) {
    if (lang === 'en') {
      return ['exercise', 'practice', 'quiz', 'problem'].some((w) => lowered.includes(w));
    }
    return ['تمرین', 'تست'].some((w) => text.includes(w));
  }

  formatGrammarMenu(lang) {
    const lines = Object.values(this.grammar).map((t) => `• ${t.title.en} / ${t.title.fa}`);
    if (lang === 'fa') {
      return '📗 موضوعات گرامر انگلیسی:\n' + lines.join('\n') +
        "\n\nبرای دیدن درس بنویس: 'simple present' یا 'حال ساده'\n" +
        "برای تمرین: 'تمرین حال ساده'";
    }
    return '📗 English grammar topics:\n' + lines.join('\n') +
      "\n\nAsk for a lesson: 'simple present'\n" +
      "Practice it: 'simple present exercises'";
  }

  formatTopic(topic, lang) {
    const long = topic.title_long || topic.title;
    const parts = [`📘 English Grammar — ${long.en} (${long.fa})`];
    parts.push('\n1️⃣ Structure / ساختار');
    topic.structure.forEach((s) => parts.push(`• ${s.en}\n  ↳ ${s.fa}`));
    parts.push('\n2️⃣ Function / کاربرد');
    topic.function.forEach((f) => parts.push(`• ${f.en}\n  ↳ ${f.fa}`));
    parts.push('\n3️⃣ Examples / مثال‌ها');
    topic.examples.forEach((e, i) => parts.push(`${i + 1}. ${e.en}\n   ↳ ${e.fa}`));
    const n = topic.exercises.length;
    parts.push('\n4️⃣ Exercises / تمرین');
    if (lang === 'fa') {
      parts.push(`${toPersianDigits(n)} سوال آماده دارم — بنویس: 'تمرین ${topic.title.fa}'`);
    } else {
      parts.push(`${n} questions ready — type: '${topic.title.en.toLowerCase()} exercises'`);
    }
    return parts.join('\n');
  }

  formatExerciseCard(topic, index, lang) {
    const q = topic.exercises[index];
    const total = topic.exercises.length;
    const n = lang === 'fa' ? toPersianDigits(index + 1) : String(index + 1);
    const totalS = lang === 'fa' ? toPersianDigits(total) : String(total);
    const question = q.q[lang] || q.q.en;
    if (lang === 'fa') {
      return `✏️ تمرین ${n} از ${totalS}\n${question}\n` +
        "پاسخ خودت رو بنویس. ('جواب' برای دیدن جواب، 'گرامر' برای خروج)";
    }
    return `✏️ Exercise ${n}/${totalS}\n${question}\n` +
      "Type your answer. ('show answer' to reveal it, 'grammar' to exit)";
  }

  handleGrammar(text, lowered, lang) {
    const found = this.matchGrammarTopic(text, lowered, lang);
    if (found) {
      const [topicId, topic] = found;
      if (this.wantsExercises(text, lowered, lang)) {
        this.exercise = { topic: topicId, index: 0, lang };
        this.exerciseScore = 0;
        const intro = lang === 'fa'
          ? `🎯 شروع تمرین «${topic.title.fa}» — موفق باشی!\n`
          : `🎯 Starting '${topic.title.en}' practice — good luck!\n`;
        return intro + this.formatExerciseCard(topic, 0, lang);
      }
      return this.formatTopic(topic, lang);
    }
    if (this.wantsGrammarMenu(text, lowered, lang)) return this.formatGrammarMenu(lang);
    return null;
  }

  normAnswer(s) {
    let out = s.toLowerCase().replace(/[’‘]/g, "'").replace(/['`]/g, '');
    out = out.replace(/[^\p{L}\p{N}_\s]/gu, ' ');
    return out.replace(/\s+/g, ' ').trim();
  }

  answerMatches(guess, expected) {
    if (expected.includes(guess)) return true;
    const g = new Set(guess.split(' ').filter(Boolean));
    return expected.some((e) => {
      const parts = e.split(' ').filter(Boolean);
      if (parts.length < 2) return false;
      return parts.length === g.size && parts.every((p) => g.has(p));
    });
  }

  isExitCommand(text, lowered) {
    return EXIT_WORDS.some((w) => wordRe(w).test(lowered)) ||
      EXIT_WORDS_FA.some((w) => text.includes(w));
  }

  handleExercise(text, lowered, lang) {
    if (!this.exercise) return null;

    const topicId = this.exercise.topic;
    const topic = this.grammar[topicId];
    const sessLang = this.exercise.lang || lang;
    const index = this.exercise.index;
    const question = topic.exercises[index];

    // A correct answer always wins — some legit answers ARE command words
    const guess = this.normAnswer(text);
    const expected = question['a'].map((a) => this.normAnswer(a));
    if (this.answerMatches(guess, expected)) {
      this.exerciseScore += 1;
      const praise = sessLang === 'fa'
        ? pick(['✅ آفرین!', '✅ درسته!', '✅ عالی!'])
        : pick(['✅ Correct!', '✅ Well done!', '✅ Exactly!']);
      return praise + '\n' + this.advanceExercise(topic, sessLang);
    }

    if (this.isExitCommand(text, lowered)) {
      this.exercise = null;
      if (/\b(bye|goodbye)\b/.test(lowered) || text.includes('خداحافظ')) return null;
      const score = this.exerciseScore;
      this.exerciseScore = 0;
      return sessLang === 'fa'
        ? `📘 تمرین لغو شد — از ${toPersianDigits(score)} پاسخ درست خوش آمدی! بنویس 'grammar' برای منو / type 'grammar' for the menu`
        : `📘 Practice closed — ${score} correct answer(s). Type 'grammar' for the menu`;
    }
    if (
      this.matchGrammarTopic(text, lowered, 'en') ||
      this.matchGrammarTopic(text, lowered, 'fa') ||
      this.wantsGrammarMenu(text, lowered, 'en') ||
      this.wantsGrammarMenu(text, lowered, 'fa')
    ) {
      this.exercise = null;
      return null;
    }

    const reveal =
      SHOW_WORDS.some((w) => lowered.includes(w)) ||
      SHOW_WORDS_FA.some((w) => text.includes(w));
    if (!reveal) {
      return sessLang === 'fa'
        ? "❌ نه، درست نیست. دوباره امتحان کن — یا بنویس 'جواب'."
        : "❌ Not quite. Try again — or type 'show answer'.";
    }

    const answer = question['a'].join(' / ');
    const revealMsg = sessLang === 'fa' ? '💡 جواب: ' + answer : '💡 Answer: ' + answer;
    return revealMsg + '\n' + this.advanceExercise(topic, sessLang);
  }

  advanceExercise(topic, lang) {
    this.exercise.index += 1;
    const index = this.exercise.index;
    if (index >= topic.exercises.length) {
      const total = topic.exercises.length;
      const score = this.exerciseScore;
      this.exercise = null;
      const totalS = lang === 'fa' ? toPersianDigits(total) : String(total);
      const scoreS = lang === 'fa' ? toPersianDigits(score) : String(score);
      if (lang === 'fa') {
        return `🎉 تمرین تموم شد! امتیازت: ${scoreS} از ${totalS}\n` +
          "برای درس برگرد: 'گرامر' — یا دوباره تمرین: 'تمرین حال ساده'";
      }
      return `🎉 Exercise finished! Your score: ${scoreS}/${totalS}\n` +
        "Back to lessons: 'grammar' — or practice again: 'simple present exercises'";
    }
    return this.formatExerciseCard(topic, index, lang);
  }

  /* ------------------------------------------------------------- jokes */

  jokeMatches(joke, text, lowered) {
    for (const kw of joke.keywords || []) {
      if (FA_RE.test(kw)) {
        if (text.includes(kw)) return true;
      } else if (wordRe(kw).test(lowered)) {
        return true;
      }
    }
    return false;
  }

  tellJoke(text, lang) {
    if (!this.jokes.length) return '😄';
    const lowered = text.toLowerCase();
    let candidates = this.jokes.filter((j) => this.jokeMatches(j, text, lowered));
    if (!candidates.length) candidates = this.jokes;
    const fresh = candidates.filter((j) => j.id !== this.lastJokeId);
    const joke = pick(fresh.length ? fresh : candidates);
    this.lastJokeId = joke.id;

    if (lang === 'fa') {
      const setup = joke.translation.setup;
      const punch = joke.translation.punchline || '';
      const category = joke.category_fa || joke.category;
      return [`😂 ${setup}`, punch, `🏷️ ${category}`].filter(Boolean).join('\n');
    }
    const setup = joke.setup;
    const punch = joke.punchline || '';
    return [`😂 ${setup}`, punch, `🏷️ ${joke.category}`].filter(Boolean).join('\n');
  }

  /* ----------------------------------------------------------- phrases */

  matchPhraseTopic(text, lowered) {
    const normText = normalizeWord(text);
    for (const topic of Object.values(this.phrases)) {
      for (const lang of ['en', 'fa']) {
        for (const kw of topic.keywords[lang] || []) {
          if (lang === 'en') {
            if (wordRe(kw).test(lowered)) return topic;
          } else if (normText.includes(normalizeWord(kw))) {
            return topic;
          }
        }
      }
    }
    return null;
  }

  handlePhrases(text, lowered, lang) {
    const topic = this.matchPhraseTopic(text, lowered);
    if (!topic) return null;
    const parts = [`💬 ${topic.title.en} (${topic.title.fa})`];
    topic.phrases.forEach((p) => parts.push(`• ${p.en}\n  ↳ ${p.fa}`));
    return parts.join('\n');
  }

  /* ---------------------------------------------------------- glossary */

  handleDomainList(text, lowered, lang) {
    const normText = normalizeWord(text);
    for (const dom of Object.values(this.glossary)) {
      for (const kw of dom.keywords[lang] || []) {
        const matched = lang === 'en'
          ? wordRe(kw, true).test(lowered)
          : normText.includes(normalizeWord(kw));
        if (matched) return this.formatDomain(dom, lang);
      }
    }
    return null;
  }

  formatDomain(dom, lang) {
    const count = lang === 'fa' ? toPersianDigits(dom.words.length) : String(dom.words.length);
    const lines = [`${dom.list_label[lang]} (${count}):`];
    for (const w of dom.words) {
      lines.push(lang === 'fa' ? `${w[1]} — ${w[0]}` : `${w[0]} — ${w[1]}`);
    }
    return lines.join('\n');
  }

  handleGlossaryLookup(text, lang) {
    let target = null;
    const patterns = lang === 'fa'
      ? FA_LOOKUP_PATTERNS.concat(EN_LOOKUP_PATTERNS)
      : EN_LOOKUP_PATTERNS.concat(FA_LOOKUP_PATTERNS);
    for (const p of patterns) {
      const m = text.match(p);
      if (m) {
        target = m[1].trim();
        break;
      }
    }
    if (!target) return null;
    target = target.replace(/^[\s.?!؟،,;:"'«»()[\]]+|[\s.?!؟،,;:"'«»()[\]]+$/g, '').trim();
    if (!target || LOOKUP_STOPWORDS.has(normalizeWord(target))) return null;

    const entries = this.lookupWord(target);
    if (!entries.length) {
      if (target.split(/\s+/).length > 1) return null;
      return this.notFound(target, lang);
    }
    return this.formatLookup(target, entries, lang);
  }

  notFound(target, lang) {
    if (lang === 'fa') {
      return `«${target}» توی واژه‌نامه من نیست هنوز 📚 ` +
        'یکی از این دامنه‌ها رو امتحان کن: رنگها، حیوانات، میوهها، اعداد، مشاغل.';
    }
    return `I don't have "${target}" in my glossary yet 📚 ` +
      'Try one of my domains: colors, animals, fruits, numbers, jobs, sports...';
  }

  formatLookup(target, entries, lang) {
    const [domId, en, fa] = entries[0];
    const label = this.glossary[domId].label;
    if (lang === 'fa') {
      const extra = entries.length > 1
        ? ' — چند معنی دیگر: ' + entries.slice(1, 3).map((e) => e[1] + '، ' + e[2]).join(', ')
        : '';
      return `«${target}» → ${en} / ${fa} (${label.fa} / ${label.en})${extra}`;
    }
    const extra = entries.length > 1
      ? ' — also: ' + entries.slice(1, 3).map((e) => e[1] + ' (' + e[2] + ')').join(', ')
      : '';
    return `"${target}" → ${fa}  (${label.en} / ${label.fa})${extra}`;
  }

  /* ------------------------------------------------------------ respond */

  respond(userInput) {
    const text = (userInput || '').trim();
    this.remember(text);
    if (!text) return 'Please say something 🙂 / یه چیزی بگو 🙂';

    const lang = detectLang(text);
    const lowered = text.toLowerCase();

    const exerciseReply = this.handleExercise(text, lowered, lang);
    if (exerciseReply !== null) return exerciseReply;

    const learned = this.learnName(text);

    let result = this.handleAlphabet(text, lowered);
    if (result === null) result = this.handleLetterLookup(text);
    if (result === null) result = this.handleGrammar(text, lowered, lang);
    if (result === null) result = this.handlePhrases(text, lowered, lang);
    if (result === null) result = this.handleGlossaryLookup(text, lang);
    if (result === null) result = this.handleDomainList(text, lowered, lang);
    if (result) {
      if (learned) {
        result += lang === 'en' ? `\nNice to meet you, ${this.userName}!` : `\nخوشبختم ${this.userName}!`;
      }
      return result;
    }
    if (learned) {
      return lang === 'en'
        ? `Nice to meet you, ${this.userName}!`
        : `خوشبختم ${this.userName} جان!`;
    }

    const intent = this.matchIntent(text, lang);
    if (intent) {
      if (intent.name === 'joke') return this.tellJoke(text, lang);
      return this.replyFromIntent(intent, lang);
    }

    if (text.split(/\s+/).length === 1) {
      const word = text.replace(/^[ .!?؟،"'«»]+|[ .!?؟،"'«»]+$/g, '');
      const entries = this.lookupWord(word);
      if (entries.length) return this.formatLookup(word, entries, lang);
      if (word && normalizeWord(word)) return this.notFound(word, lang);
    }

    if (lang === 'fa') {
      return 'متوجه نشدم 😅 می‌تونی درباره الفبای فارسی، جوک، ساعت، ترجمه کلمات ' +
        "(مثل 'سیب به انگلیسی') یا واژگان (مثل 'رنگها' و 'حیوانات') بپرسی. " +
        "برای راهنما بنویس 'راهنما'.";
    }
    return "I'm not sure I understand 😅 Try asking about the alphabets, a joke, " +
      "translating a word ('translate apple'), a vocabulary domain " +
      "('what are the colors'), or the time. Type 'help' for options.";
  }
}

function push(map, key, value) {
  if (!map.has(key)) map.set(key, []);
  map.get(key).push(value);
}

/* The JSON files wrap their content in {"topics": {...}} / {"domains": {...}};
 * accept both the wrapped file and the bare inner map. */
function unwrapTopics(data) {
  if (!data) return {};
  return data.topics ? data.topics : data;
}