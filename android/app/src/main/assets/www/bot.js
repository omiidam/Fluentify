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

/* ---------------------------------------------------------------- numbers */

const UNITS = { zero: 0, one: 1, two: 2, three: 3, four: 4, five: 5, six: 6,
  seven: 7, eight: 8, nine: 9, ten: 10, eleven: 11, twelve: 12, thirteen: 13,
  fourteen: 14, fifteen: 15, sixteen: 16, seventeen: 17, eighteen: 18,
  nineteen: 19 };
const TENS = { twenty: 20, thirty: 30, forty: 40, fifty: 50, sixty: 60,
  seventy: 70, eighty: 80, ninety: 90 };
const SCALES = { hundred: 100, thousand: 1000, million: 1000000,
  billion: 1000000000 };
const ENGLISH_ONES = ['zero', 'one', 'two', 'three', 'four', 'five', 'six',
  'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen',
  'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen'];
const ENGLISH_TENS = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty',
  'seventy', 'eighty', 'ninety'];

function toEnglishDigits(n) {
  if (n < 20) return ENGLISH_ONES[n];
  if (n < 100) {
    const h = Math.floor(n / 10), t = n % 10;
    return ENGLISH_TENS[h] + (t ? '-' + ENGLISH_ONES[t] : '');
  }
  if (n < 1000) {
    const h = Math.floor(n / 100), t = n % 100;
    return ENGLISH_ONES[h] + ' hundred' + (t ? ' and ' + toEnglishDigits(t) : '');
  }
  for (const [scale, name] of [[1e9, 'billion'], [1e6, 'million'], [1000, 'thousand']]) {
    if (n >= scale) {
      const h = Math.floor(n / scale), t = n % scale;
      return toEnglishDigits(h) + ' ' + name + (t ? ' ' + toEnglishDigits(t) : '');
    }
  }
  return String(n);
}

function numberFromWords(phrase) {
  const words = phrase.trim().toLowerCase().split(/[\s-]+/).filter(Boolean);
  if (!words.length || words.length > 8) return null;
  if (words.length === 2 && words[0] === 'a' && words[1] === 'hundred') return 100;
  let total = 0, current = 0, seen = false;
  for (const w of words) {
    if (w === 'and') continue;
    if (w in UNITS) { current += UNITS[w]; seen = true; }
    else if (w in TENS) { current += TENS[w]; seen = true; }
    else if (w in SCALES) {
      current = (current || 1) * SCALES[w];
      total += current; current = 0; seen = true;
    } else return null;
  }
  return seen ? total + current : null;
}

/* ---------------------------------------------------------- corrections */

const PAST_PARTICIPLES = {
  went: 'gone', gone: 'gone', ate: 'eaten', saw: 'seen', made: 'made',
  took: 'taken', said: 'said', came: 'come', did: 'done', got: 'got',
  found: 'found', knew: 'known', thought: 'thought', bought: 'bought',
  gave: 'given', wrote: 'written', spoke: 'spoken', drove: 'driven',
  broke: 'broken', felt: 'felt', kept: 'kept', left: 'left', met: 'met',
  paid: 'paid', put: 'put', set: 'set', sat: 'sat', stood: 'stood',
  understood: 'understood', worn: 'worn', run: 'run', ran: 'run',
  written: 'written', chosen: 'chosen', eaten: 'eaten', seen: 'seen',
  hidden: 'hidden', built: 'built', sent: 'sent', spent: 'spent', lost: 'lost',
  won: 'won', taught: 'taught', caught: 'caught', sought: 'sought',
  brought: 'brought', sang: 'sung', drank: 'drunk', swam: 'swum',
  began: 'begun', rose: 'risen', fell: 'fallen', led: 'led', fed: 'fed',
  flew: 'flown', threw: 'thrown', grew: 'grown', blew: 'blown',
  drew: 'drawn', wore: 'worn', tore: 'torn', stole: 'stolen' };

const BASE_FORMS = {
  went: 'go', came: 'come', saw: 'see', ate: 'eat', made: 'make',
  took: 'take', said: 'say', got: 'get', gave: 'give', knew: 'know',
  thought: 'think', bought: 'buy', wrote: 'write', spoke: 'speak',
  drove: 'drive', broke: 'break', felt: 'feel', kept: 'keep',
  left: 'leave', met: 'meet', had: 'have', did: 'do', was: 'were',
  gone: 'go', eaten: 'eat', seen: 'see', taken: 'take', given: 'give',
  known: 'know', written: 'write', spoken: 'speak', driven: 'drive',
  broken: 'break', informations: 'information', knowledges: 'knowledge',
  equipments: 'equipment', furnitures: 'furniture', advices: 'advice',
  softwares: 'software', researches: 'research', homeworks: 'homework' };

const VOWEL_SOUND_EXCEPTIONS = ['s', 'x', 'z', 'ch', 'sh'];

function pastParticiple(verb) {
  const v = String(verb || '').toLowerCase().replace(/'/g, '');
  if (v in PAST_PARTICIPLES) return PAST_PARTICIPLES[v];
  if (v.endsWith('e')) return v + 'd';
  if (v.length > 2 && v.endsWith('y') && !'aeiou'.includes(v[v.length - 2]))
    return v.slice(0, -1) + 'ied';
  return v + 'ed';
}

function singular(word) {
  const w = String(word || '').toLowerCase();
  if (w in BASE_FORMS) return BASE_FORMS[w];
  if (w.endsWith('ies') && w.length > 4) return w.slice(0, -3) + 'y';
  if (w.endsWith('sses') || w.endsWith('shes') || w.endsWith('ches'))
    return w.slice(0, -2);
  if (w.endsWith('s') && !w.endsWith('ss')) return w.slice(0, -1);
  return word;
}

function thirdPerson(verb) {
  const v = String(verb || '').toLowerCase();
  if (VOWEL_SOUND_EXCEPTIONS.some((x) => v.endsWith(x)) || v.endsWith('o'))
    return v + 'es';
  if (v.endsWith('y') && v.length > 1 && !'aeiou'.includes(v[v.length - 2]))
    return v.slice(0, -1) + 'ies';
  return v + 's';
}

/* --------------------------------------------------------------- stress */

const VOWELS = 'aeiouy';
const STRESS_BEFORE = ['ical', 'tion', 'sion', 'ture', 'sure', 'ity', 'ial',
  'ious', 'eous', 'ian', 'uous', 'ify', 'ise', 'ize', 'ate', 'ogy', 'ology',
  'graphy', 'meter', 'itude', 'ative'];
const UNSTRESSED_PREFIXES = ['be', 'con', 'com', 'de', 'dis', 'en', 'em', 'ex',
  'im', 'in', 'mis', 'per', 'pre', 'pro', 're', 'sub', 'sur', 'un', 'up',
  'ob', 'for', 'fore', 'with'];
const VOICELESS = 'ptkfvszxcgq';
const VOICED = 'bdjlmnrwygv';

function syllables(word) {
  const w = String(word || '').toLowerCase().replace(/[^a-z]/g, '');
  if (!w) return [];
  if (w.length <= 2) return [w];
  let ends = [...w.matchAll(/[aeiouy]+/g)];
  if (!ends.length) return [w];
  // a final "e" after a consonant is silent and does not start a syllable
  if (w.endsWith('e') && !w.endsWith('le') && !w.endsWith('ee') &&
      !w.endsWith('ye')) {
    const last = ends[ends.length - 1];
    if (last[0] === 'e' && last.index === w.length - 1) ends.pop();
  }
  if (!ends.length) return [w];
  const parts = [];
  let prev = 0;
  ends.forEach((g, i) => {
    const end = i < ends.length - 1 ? g.index + g[0].length : w.length;
    parts.push(w.slice(prev, end));
    prev = g.index + g[0].length;
  });
  return parts.filter(Boolean);
}

function stressIndex(word) {
  const parts = syllables(word);
  const n = parts.length;
  if (n <= 1) return 0;
  const w = String(word).toLowerCase();
  let idx = 0;
  const hit = STRESS_BEFORE.some((s) => {
    if (w.endsWith(s) && n >= 2) { idx = n - 2; return true; }
    return false;
  });
  if (!hit) {
    idx = 0;
    const head = parts[0];
    if (UNSTRESSED_PREFIXES.some((p) => head.startsWith(p) &&
        head.length >= p.length && head.length > 1)) idx = 1;
    if (w.endsWith('ee') || w.endsWith('eer') || w.endsWith('eese') ||
        w.endsWith('ette')) idx = 0;
  }
  return Math.min(idx, n - 1);
}

function markStress(word) {
  const parts = syllables(word);
  if (!parts.length) return word;
  const i = stressIndex(word);
  return parts.map((p, k) => {
    if (k === i) return p.toUpperCase();
    if (k === 0) return p.charAt(0).toUpperCase() + p.slice(1);
    return p;
  }).join('-');
}

function firstSoundNote(word) {
  const w = String(word || '').toLowerCase().replace(/[^a-z]/g, '');
  if (!w) return '';
  const ch = w[0];
  if (VOICELESS.includes(ch))
    return `it starts with /${ch}/ — no voice on your throat, just airflow`;
  if (VOICED.includes(ch)) return `it starts with /${ch}/ — put your voice on it`;
  if (VOWELS.includes(ch))
    return `it starts with the vowel /${ch}/ — open your mouth on it`;
  if (ch === 'y')
    return 'it starts with /y/ — your tongue is already in place';
  return `it starts with /${ch}/`;
}

/* -------------------------------------------------------------- phrases */

const CORE_PHRASES = {
  'thank you': ['Thank you.', 'ممنونم.'], 'thanks': ['Thanks!', 'مرسی!'],
  'hello': ['Hello!', 'سلام!'], 'hi': ['Hi!', 'سلام!'],
  'goodbye': ['Goodbye!', 'خداحافظ!'], 'bye': ['Bye!', 'خداحافظ!'],
  'excuse me': ['Excuse me.', 'ببخشید.'], 'sorry': ['Sorry.', 'ببخشید.'],
  'please': ['Please.', 'لطفاً.'], 'yes': ['Yes.', 'بله.'],
  'no': ['No.', 'نه.'], 'of course': ['Of course.', 'البته.'],
  'you are welcome': ["You're welcome.", 'خواهش می‌کنم.'],
  'how are you': ['How are you?', 'حالت چطور است؟'],
  'how are you today': ['How are you today?', 'امروز حالت چطور است؟'],
  'see you': ['See you later.', 'بدرود.'],
  'good luck': ['Good luck!', 'موفق باشی!'],
  'welcome': ['Welcome!', 'خوش آمدی!'],
  'i am sorry': ["I'm sorry.", 'متأسفم.'],
  'nice to meet you': ['Nice to meet you.', 'خوشحالم که آشنا شدیم.'],
  'no problem': ['No problem.', 'اشکالی ندارد.'],
  'good morning': ['Good morning.', 'صبح بخیر.'],
  'good night': ['Good night.', 'شب بخیر.'],
  'how do you do': ['How do you do?', 'حالت چطور است؟'],
  'what do you do': ['What do you do?', 'چه کار می‌کنی؟'],
  'long time no see': ['Long time no see!', 'دیر کردی!'],
  'see you tomorrow': ['See you tomorrow.', 'فردا می‌بینمت.'],
  'i am hungry': ["I'm hungry.", 'گرسنه‌ام.'],
  'i am thirsty': ["I'm thirsty.", 'تشنه‌ام.'],
  'i am tired': ["I'm tired.", 'خسته‌ام.'],
  'how old are you': ['How old are you?', 'چند سالته؟'],
  'what time is it': ['What time is it?', 'ساعت چند است؟'],
};

const stripArticle = (word) =>
  String(word || '').trim().replace(/^(?:a|an|the)\s+/i, '');

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
    this.listening = (data.listening && data.listening.levels) || data.listening || [];
    this.distinctions = {};
    if (data.distinctions)
      for (const t of (data.distinctions.topics || data.distinctions))
        this.distinctions[t.id] = t;
    this.idioms = {};
    if (data.idioms)
      for (const t of (data.idioms.topics || data.idioms)) this.idioms[t.id] = t;
    this.corrections = (data.corrections && data.corrections.rules) ||
      data.corrections || [];

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
    this.practiceDone = new Set();   // topics whose practice stage is cleared
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

  formatTopic(topic, lang, topicId = '') {
    const long = topic.title_long || topic.title;
    const parts = [`📘 English Grammar — ${long.en} (${long.fa})`];
    parts.push('\n1️⃣ Structure / ساختار');
    topic.structure.forEach((s) => parts.push(`• ${s.en}\n  ↳ ${s.fa}`));
    if (topic.tip) parts.push(`\n💡 Tip: ${topic.tip.en}\n   ↳ ${topic.tip.fa}`);
    parts.push('\n2️⃣ Function / کاربرد');
    topic.function.forEach((f) => parts.push(`• ${f.en}\n  ↳ ${f.fa}`));
    parts.push('\n3️⃣ Examples / مثال‌ها');
    topic.examples.forEach((e, i) => parts.push(`${i + 1}. ${e.en}\n   ↳ ${e.fa}`));
    const practiceN = (topic.practice || []).length;
    const examN = (topic.exam || []).length;
    const done = this.practiceDone.has(topicId);
    parts.push('\n4️⃣ Exercises / تمرین');
    if (lang === 'fa') {
      const pS = toPersianDigits(practiceN), eS = toPersianDigits(examN);
      parts.push(`۱) تمرین: ${pS} سوال — بنویس: 'تمرین ${topic.title.fa}'`);
      parts.push(done
        ? `۲) آزمون: ${eS} سوال — بنویس: 'آزمون ${topic.title.fa}'`
        : `۲) آزمون: ${eS} سوال (🔒 تا وقتی تمرین رو تموم کنی)`);
    } else {
      parts.push(`1) Practice: ${practiceN} questions — type: '${topic.title.en.toLowerCase()} exercises'`);
      parts.push(done
        ? `2) Exam: ${examN} questions — type: '${topic.title.en.toLowerCase()} exam'`
        : `2) Exam: ${examN} questions 🔒 (finish the practice first)`);
    }
    return parts.join('\n');
  }

  formatExerciseCard(topic, index, lang, stage = 'practice') {
    const questions = stage === 'exam' ? (topic.exam || []) : (topic.practice || []);
    const q = questions[index];
    const total = questions.length;
    const n = lang === 'fa' ? toPersianDigits(index + 1) : String(index + 1);
    const totalS = lang === 'fa' ? toPersianDigits(total) : String(total);
    const question = q.q[lang] || q.q.en;
    if (lang === 'fa') {
      const head = stage === 'exam' ? '🎓 آزمون' : '✏️ تمرین';
      return `${head} ${n} از ${totalS}\n${question}\n` +
        "پاسخ خودت رو بنویس. ('جواب' برای دیدن جواب، 'گرامر' برای خروج)";
    }
    const head = stage === 'exam' ? '🎓 Exam' : '✏️ Practice';
    return `${head} ${n}/${totalS}\n${question}\n` +
      "Type your answer. ('show answer' to reveal it, 'grammar' to exit)";
  }

  wantsExam(text, lowered, lang) {
    if (lang === 'en') {
      return ['exam', 'test', 'final test'].some((w) => lowered.includes(w));
    }
    return ['آزمون', 'امتحان', 'تست نهایی'].some((w) => text.includes(w));
  }

  handleGrammar(text, lowered, lang) {
    const found = this.matchGrammarTopic(text, lowered, lang);
    if (found) {
      const [topicId, topic] = found;
      if (this.wantsExam(text, lowered, lang)) {
        if (!this.practiceDone.has(topicId)) {
          const n = (topic.practice || []).length;
          const nStr = lang === 'fa' ? toPersianDigits(n) : String(n);
          const title = lang === 'fa' ? topic.title.fa : topic.title.en;
          return lang === 'fa'
            ? `🔒 آزمون قفل است — اول تمرین (${nStr} سوال) را کامل کن.\nبنویس: 'تمرین ${title}'`
            : `🔒 The exam is locked — finish the practice first (${nStr} questions).\n` +
              `Type: '${topic.title.en.toLowerCase()} exercises'`;
        }
        this.exercise = { topic: topicId, index: 0, lang, stage: 'exam' };
        this.exerciseScore = 0;
        const intro = lang === 'fa'
          ? `🎓 شروع آزمون «${topic.title.fa}» — موفق باشی!\n`
          : `🎓 Starting the '${topic.title.en}' exam — good luck!\n`;
        return intro + this.formatExerciseCard(topic, 0, lang, 'exam');
      }
      if (this.wantsExercises(text, lowered, lang)) {
        this.exercise = { topic: topicId, index: 0, lang, stage: 'practice' };
        this.exerciseScore = 0;
        const intro = lang === 'fa'
          ? `✏️ شروع تمرین «${topic.title.fa}» — موفق باشی!\n`
          : `✏️ Starting '${topic.title.en}' practice — good luck!\n`;
        return intro + this.formatExerciseCard(topic, 0, lang, 'practice');
      }
      return this.formatTopic(topic, lang, topicId);
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

  isShowCommand(text, lowered) {
    // Strict: substring matching revealed the answer for any message
    // containing "answer" (e.g. "I have no answer").
    const stripped = lowered.replace(/[.!?؟,;:"'«»()\[\]]/g, '').trim();
    if (!stripped) return false;
    if (SHOW_WORDS.includes(stripped) || SHOW_WORDS_FA.includes(stripped)) return true;
    const prefixes = ['show answer', 'reveal answer', 'show me', 'help me answer'];
    if (prefixes.some((w) => stripped === w || stripped.startsWith(w + ' '))) return true;
    return ['نشون بده', 'جواب بده'].some((w) => stripped.startsWith(w));
  }

  looksLikeAnswer(text, lowered, lang) {
    // Without this, anything typed mid-quiz ("what's the capital of France?")
    // is rejected with "Not quite" instead of being answered normally.
    if (text.includes('?') || text.includes('؟')) return false;
    if (this.matchPhraseTopic(text, lowered)) return false;
    if (this.matchGrammarTopic(text, lowered, 'en') ||
        this.matchGrammarTopic(text, lowered, 'fa')) return false;
    if (this.handleDomainList(text, lowered, lang)) return false;
    if (this.matchIntent(text, lang)) return false;
    return true;
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
    const stage = this.exercise.stage || 'practice';
    const questions = stage === 'exam' ? (topic.exam || []) : (topic.practice || []);
    const question = questions[index];

    // A correct answer always wins — some legit answers ARE command words
    const guess = this.normAnswer(text);
    const expected = question['a'].map((a) => this.normAnswer(a));
    if (this.answerMatches(guess, expected)) {
      this.exerciseScore += 1;
      const praise = sessLang === 'fa'
        ? pick(['✅ آفرین!', '✅ درسته!', '✅ عالی!'])
        : pick(['✅ Correct!', '✅ Well done!', '✅ Exactly!']);
      return praise + '\n' + this.advanceExercise(topic, sessLang, topicId, stage);
    }

    if (this.isExitCommand(text, lowered)) {
      this.exercise = null;
      if (/\b(bye|goodbye)\b/.test(lowered) || text.includes('خداحافظ')) return null;
      // "tell me a joke" / "help" are exit words *and* real requests —
      // close the quiz but still answer them properly.
      if (!this.looksLikeAnswer(text, lowered, lang)) return null;
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

    // Reveal / skip (either language)
    const reveal = this.isShowCommand(text, lowered);
    if (!reveal) {
      // Only reject it as a wrong answer if it reads like one; otherwise
      // let the normal handlers answer it and keep the quiz open.
      if (!this.looksLikeAnswer(text, lowered, lang)) return null;
      return sessLang === 'fa'
        ? "❌ نه، درست نیست. دوباره امتحان کن — یا بنویس 'جواب'."
        : "❌ Not quite. Try again — or type 'show answer'.";
    }

    const answer = question['a'].join(' / ');
    const revealMsg = sessLang === 'fa' ? '💡 جواب: ' + answer : '💡 Answer: ' + answer;
    return revealMsg + '\n' + this.advanceExercise(topic, sessLang, topicId, stage);
  }

  advanceExercise(topic, lang, topicId, stage = 'practice') {
    this.exercise.index += 1;
    const index = this.exercise.index;
    const questions = stage === 'exam' ? (topic.exam || []) : (topic.practice || []);
    if (index >= questions.length) {
      const total = questions.length;
      const score = this.exerciseScore;
      this.exercise = null;
      if (stage === 'practice') {
        this.practiceDone.add(topicId);
        return this.practiceUnlocked(topic, lang);
      }
      return this.formatScoreReport(topic, score, total, lang, stage);
    }
    return this.formatExerciseCard(topic, index, lang, stage);
  }

  practiceUnlocked(topic, lang) {
    const examN = (topic.exam || []).length;
    if (lang === 'fa') {
      return '✅ تمرین تمام شد! آزمون باز شد. 🎓\n' + '─'.repeat(30) + '\n' +
        `${toPersianDigits(examN)} سوال باقی مانده — بنویس: 'آزمون ${topic.title.fa}'\n` +
        'هر پاسخ درست یک امتیاز. آخرش کارت نتیجه با سطح می‌گیری.';
    }
    return '✅ Practice complete! Your exam is now open. 🎓\n' + '─'.repeat(30) + '\n' +
      `${examN} questions to go — type: '${topic.title.en.toLowerCase()} exam'\n` +
      "Each correct answer scores a point; you'll get a graded result card at the end.";
  }

  /* Score bands — each result gets its own "theme" */
  static SCORE_BANDS = [
    [90, '🌟', 'Excellent', 'عالی',
     'Outstanding — this grammar is yours. / فوق‌العاده — این گرامر مال توئه.'],
    [75, '🌿', 'Very good', 'خیلی خوب',
     'Strong and accurate. / قوی و دقیق.'],
    [60, '💧', 'Good', 'خوب',
     'Solid, with a few slips to polish. / خوب، فقط چند نکته برای صیقل.'],
    [40, '🔥', 'Almost there', 'نزدیک شدی',
     'You have the idea — another round will lock it in. / ایده رو داری — یه دور دیگه کاملش می‌کنه.'],
    [0, '🌱', 'Keep going', 'ادامه بده',
     'Every expert started here. Read the lesson again and retry. / هر متخصصی از همین‌جا شروع کرد.'],
  ];

  formatScoreReport(topic, score, total, lang, stage = 'exam') {
    const pct = total ? Math.round((score / total) * 100) : 0;
    let band = Fluentify.SCORE_BANDS[Fluentify.SCORE_BANDS.length - 1];
    for (const b of Fluentify.SCORE_BANDS) {
      if (pct >= b[0]) { band = b; break; }
    }
    const [cut, icon, en, fa, note] = band;
    const barLen = 20;
    const filled = Math.max(0, Math.min(barLen, Math.round((pct / 100) * barLen)));
    const bar = '█'.repeat(filled) + '░'.repeat(barLen - filled);
    const rule = '─'.repeat(34);

    if (lang === 'fa') {
      return `${icon} نتیجه آزمون — ${topic.title.fa}\n${rule}\n` +
        `امتیاز:  ${toPersianDigits(score)} / ${toPersianDigits(total)}   (${toPersianDigits(pct)}٪)\n` +
        `${bar}\nسطح: ${fa}\n${note}\n` +
        `برای درس برگرد: 'گرامر' — یا دوباره: 'آزمون ${topic.title.fa}'`;
    }
    return `${icon} Exam result — ${topic.title.en}\n${rule}\n` +
      `Score:   ${score}/${total}   (${pct}%)\n${bar}\nLevel:   ${en}\n${note}\n` +
      `Back to lessons: 'grammar' — or retry: '${topic.title.en.toLowerCase()} exam'`;
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

  /* --------------------------------------------------------- listening */

  matchListeningLevel(text, lowered) {
    for (const level of this.listening) {
      const lid = level.id.toLowerCase();
      if (wordRe(lid).test(lowered)) return level;
      if (new RegExp('\\b(?:listen|speak|say|audio|voice)\\s+' + lid + '\\b').test(lowered)) {
        return level;
      }
    }
    return null;
  }

  formatListeningLevel(level) {
    const parts = [`\u{1F3A7} ${level.title.en} (${level.title.fa})`,
                   `${level.blurb.en} / ${level.blurb.fa}`];
    level.sentences.forEach((s, i) => {
      parts.push(`${i + 1}. ${s.en}\n   \u21b3 ${s.fa}`);
    });
    return parts.join('\n');
  }

  handleListening(text, lowered, lang) {
    const asked = /\b(listen|listening|audio|voice|speak)\b/.test(lowered) ||
      ['گوش دادن', 'آواز', 'بگو'].some((w) => text.includes(w));
    // a learner often just types the band itself: "A1", "b2", "C2"
    const bare = /^\s*([abc][12])\s*[?!.؟]*\s*$/.exec(lowered);
    if (!asked && !bare) return null;
    let level = this.matchListeningLevel(text, lowered);
    if (!level && bare) level = this.matchListeningLevel(bare[1], bare[1]);
    if (level) return this.formatListeningLevel(level);
    const names = this.listening.map((l) => l.title.en.split(' · ')[0]).join(' · ');
    return `\u{1F3A7} Listening levels — سطح شنیدن: ${names}\n` +
      "Ask: 'listen A1' or 'گوش دادن A1'";
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
      `   ↳ سطح: ${topic.level}`, '', topic.why];
    for (const side of topic.sides) {
      lines.push('');
      lines.push(`  • ${side.en}`);
      if (side.fa) lines.push(`    ↳ ${side.fa}`);
    }
    return lines.join('\n');
  }

  handleDistinction(text, lowered, lang) {
    const gate = /(?:\b(?:difference|differ|confus|compare|versus|vs|which one|tell .*\bfrom\b|when (?:do|should|would) (?:i|we) use|when to use|usage of)\b|تفاوت|فرق|کدام|چه تفاوتی|کی به کار ببرم)/;
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
    return `🗯  “${row.en}” — ${row.fa}\n   ↳ ${row.meaning}\n   e.g. ${row.example}`;
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
          ? '✅ That sentence is correct English.  ↳ این جمله درست است.'
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
        '   ↳ کلمه را بگو تا با هم تلفظش کنیم.\n' +
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
      lines.push("   ↳ For the full guide ask: 'phonetics'");
      return lines.join('\n');
    }

    const phrase = this.lookupPhrase(key);
    if (phrase) {
      const lines = [`🗣  “${phrase.en}”`, `   ↳ ${phrase.fa}`];
      if (phrase.en.length <= 24)
        lines.push(`   Say it slowly: ${phrase.en.split('').join(' · ')}`);
      lines.push("   ↳ For the full guide ask: 'phonetics'");
      return lines.join('\n');
    }

    const slow = word.split('').join(' · ');
    return `🗣  “${word}” is not in my vocabulary list yet, so I cannot give you its Persian meaning.\n` +
      `   ↳ «${word}» هنوز در واژگان من نیست.\n` +
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
      `   • Phrases: ${Object.keys(this.phrases).length} banks · Listening: ${this.listening.length} levels\n` +
      `   • Idioms: ${idiomCount} · Distinctions: ${Object.keys(this.distinctions).length} confusable pairs`;
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
    if (result === null) result = this.handleNumber(text, lang);
    if (result === null) result = this.handlePronounce(text, lowered, lang);
    if (result === null) result = this.handleDistinction(text, lowered, lang);
    if (result === null) result = this.handleIdioms(text, lowered, lang);
    if (result === null) result = this.handleCorrection(text, lowered, lang);
    if (result === null) result = this.handleStat(text, lowered, lang);
    if (result === null) result = this.handleGrammar(text, lowered, lang);
    if (result === null) result = this.handlePhrases(text, lowered, lang);
    if (result === null) result = this.handleListening(text, lowered, lang);
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