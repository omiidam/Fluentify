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

/* Fold Persian writing variations that carry no meaning — ZWNJ ("می‌خواهم" vs
 * "میخواهم"), the Arabic yeh/kaf and heh forms, and bidi marks. Applied to the
 * message and to every keyword, so it can only ever add matches. */
const FA_FOLD = {
  '\u064a': '\u06cc', '\u0643': '\u06a9', '\u06c0': '\u0647', '\u0629': '\u0647',
  '\u200c': '', '\u200d': '', '\u200e': '', '\u200f': '',
};
const foldFa = (text) => String(text).replace(
  /[\u064a\u0643\u06c0\u0629\u200c\u200d\u200e\u200f]/g, (ch) => FA_FOLD[ch] ?? '');

/* A message that names the lookup it wants ("translate X", "معنی X") asks for a
 * word, not for a phrase bank that happens to share the word. The Persian side
 * is a substring test: \b is ASCII-only here, so it cannot anchor Persian. */
const LOOKUP_ASK_RE = /\b(?:translate|define|definition of|meaning of|what does|means)\b/;
const LOOKUP_ASK_FA = ['معنی', 'ترجمه', 'به انگلیسی'];

/* "speak english", "reply in persian", "english please" — a request about the
 * language of the answer, not a word to translate. */
const SWITCH_ASK_RE = /^\s*(?:please\s+)?(?:speak|reply|answer|respond|write|talk|continue)\b[^.!?]*?\bin\s+(?:english|persian|farsi)\b|^\s*(?:english|persian|farsi)\s+please\b/i;
const isLookupAsk = (text, lowered) => LOOKUP_ASK_RE.test(lowered) ||
  LOOKUP_ASK_FA.some((w) => text.includes(w));

/* -------------------------------------------------------- daily english ---
 * One word, one expression and one conversation per local calendar day.
 * Selection is a pure function of the local date, mirrored from daily_index()
 * in chatbot.py: both engines must land on the same three items, and they are
 * compared on exactly that by tests_js_vs_python.py.
 *
 * Calendar days from a fixed epoch, counted in UTC arithmetic so a 23- or
 * 25-hour day across a daylight-saving change still counts as one day. */
const DAILY_EPOCH = Date.UTC(2024, 0, 1);
const DAILY_SALTS = { words: 3, expressions: 11, conversations: 5 };

const localDateKey = (d) => {
  const p = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
};

function dailyDayNumber(key) {
  const [y, m, d] = String(key).split('-').map(Number);
  return Math.round((Date.UTC(y, m - 1, d) - DAILY_EPOCH) / 86400000);
}

function dailyGcd(a, b) {
  while (b) { const t = a % b; a = b; b = t; }
  return a;
}

/* A step coprime with the catalogue size: `day * step % size` then walks every
 * entry before it repeats one, whatever the size is. */
function dailyStep(size, salt) {
  if (size <= 1) return 1;
  let step = 1 + (salt % 9);
  while (dailyGcd(step, size) !== 1) {
    step += 1;
    if (step > size + 1) return 1;
  }
  return step;
}

const dailyIndex = (day, size, salt) =>
  (size <= 0 ? 0 : (day * dailyStep(size, salt) + salt) % size);

/* Narrow on purpose: "practice" alone belongs to the grammar session and
 * "lesson" alone to the grammar menu, so only these phrases name the daily
 * rotation and none of them can take a request from the section that had it. */
const DAILY_WORD_RE = /\b(?:today'?s? word|word of the day|(?:today'?s?|the) vocabulary word|daily word)\b/;
const DAILY_EXPRESSION_RE = /\b(?:today'?s? (?:expression|phrase|sentence)|(?:expression|phrase|sentence|idiom) of the day|daily (?:expression|phrase))\b/;
const DAILY_CONVERSATION_RE = /\b(?:today'?s? (?:conversation|dialogue)|(?:conversation|dialogue) of the day|daily (?:conversation|dialogue))\b/;
const DAILY_ANY_RE = /\b(?:daily english|daily lesson|daily practice|english of the day|today'?s? (?:lesson|english)|what(?:'s| is) today)\b/;
const DAILY_WORD_FA = ['لغت امروز', 'کلمه امروز', 'واژه امروز', 'لغت روز', 'کلمهٔ امروز', 'واژهٔ امروز'];
const DAILY_EXPRESSION_FA = ['عبارت امروز', 'جمله امروز', 'اصطلاح امروز', 'عبارت روز', 'جملهٔ امروز', 'عبارت امروز چیه'];
const DAILY_CONVERSATION_FA = ['مکالمه امروز', 'گفتگوی امروز', 'مکالمه روز', 'دیالوگ امروز', 'مکالمهٔ امروز'];
const DAILY_ANY_FA = ['انگلیسی روزانه', 'انگلیسی امروز', 'درس امروز', 'روزانه چی', 'امروز چی یاد', 'امروز چی بخونم'];
const PRACTICE_ASK = ['practice', 'roleplay', 'role play', 'drill', 'تمرین', 'باهام', 'با من', 'نقش بازی'];
const EXAMPLES_ASK = ['example', 'examples', 'sentence', 'sentence with', 'مثال', 'جمله بساز', 'چند جمله'];

/* Does what the learner said count as the dialogue's line? Exact match is too
 * strict for a spoken drill and substring alone is too loose, so the line
 * passes when either contains the other or four fifths of the expected words
 * are there. */
function sameSpoken(spoken, expected) {
  const norm = (s) => String(s).toLowerCase()
    .replace(/[^\w' ]+/gu, ' ').replace(/\s+/g, ' ').trim();
  const said = norm(spoken);
  const want = norm(expected);
  if (!said || !want) return false;
  if (said === want || said.includes(want)) return true;
  const have = new Set(said.split(' '));
  const need = want.split(' ');
  let hits = 0;
  for (const w of new Set(need)) if (have.has(w)) hits += 1;
  return hits / Math.max(1, new Set(need).size) >= 0.8;
}

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

/* Past-simple forms that are NOT also participles. "I have seen" is right, so
 * the present-perfect rule must only fire on these - on "seen" or "gone" the
 * learner already used the participle and there is nothing to correct. */
const PAST_SIMPLE_ONLY = new Set(['went', 'ate', 'saw', 'came', 'did', 'got',
  'found', 'knew', 'thought', 'bought', 'gave', 'wrote', 'spoke', 'drove',
  'broke', 'left', 'met', 'ran', 'wore', 'tore', 'stole', 'sang', 'drank',
  'swam', 'began', 'rose', 'fell', 'fed', 'flew', 'threw', 'grew', 'blew',
  'drew', 'shook', 'hid', 'bit', 'hung', 'rode', 'woke', 'froze', 'struck',
  'brought', 'caught', 'taught', 'sought', 'understood']);

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
  // the verb of asking is not a word to translate: "به فارسی بگو" (say it in
  // Persian) is a request about the reply, not a lookup for «بگو»
  'بگو', 'بگویم', 'بگم', 'بگید', 'بگین', 'بگویید',
]);

const EN_LOOKUP_PATTERNS = [
  /explain (?:the )?(?:word |meaning of )?(.+)/i,
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
  /معنی\s+(.+)/,
  /(.+?)\s*یعنی\s*چه/,
  /(?:چطوری|چطور|چجوری)\s+(.+?)\s+بگم/,
  /(.+?)\s*رو\s*(?:بگو|بگویم|بگید|بگین)\s*[؟?.!]*$/,
  /ترجمه\s+(.+)/,
  /کلمه\s+(.+?)\s*(?:چیه|چیست)/,
  /(.+?)\s+به\s+(?:انگلیسی|فارسی)/,
  /به\s+(?:انگلیسی|فارسی)\s+(.+)/,
  /(.+?)\s*(?:چیه|چیست)$/,
];

/* ---------------------------------------------------------------- dictionary
 * The sharded lexicon (tools/build_lexicon.py). Shards are fetched on demand
 * for the words of one message and cached, so the 20,602-headword dictionary
 * is never parsed at startup and never held whole. The Python engine reads the
 * same files with the same rules: every string below is a mirror of
 * chatbot.py, which is what the parity suite compares.
 */
const LEX_POS_FA = {
  noun: 'اسم', verb: 'فعل', adjective: 'صفت', adverb: 'قید',
};

const LEX_FORM_LABEL = {
  past: 'past', past_participle: 'past participle', '3rd_present': '3rd person',
  gerund: '-ing form', plural: 'plural', comparative: 'comparative',
  superlative: 'superlative', non_3rd_present: 'present',
};

const lexShardNames = (word) => {
  const w = String(word || '').toLowerCase().replace(/[^a-z]/g, '');
  if (w.length >= 3) return [w.slice(0, 3), w.slice(0, 2)];
  if (w.length === 2) return [w];
  if (w.length === 1) return [`${w}_`];
  return [];
};

const DEFINITION_ASK_RE = /\b(?:define|definition of|meaning of|what does|what's the meaning|what is the meaning)\b/i;

const LEX_SYNONYMS_RE = /\b(?:synonyms?|similar words?|other words? for|another word for|words? like)\b/i;
const LEX_SYNONYMS_FA = ['مترادف', 'هم معنی', 'هم‌معنی', 'هممعنی'];
const LEX_ANTONYMS_RE = /\b(?:antonyms?|opposite of|opposite to|opposites|contrary of)\b/i;
const LEX_ANTONYMS_FA = ['متضاد', 'مخالف', 'برعکس'];
const LEX_FORMS_RE = /\b(?:forms? of|inflections? of|verb forms? of)\b/i;
const LEX_FORM_ASKS = [
  [/\bpast participle of\b/i, 'past_participle'],
  [/\bpast (?:simple|tense|form) of\b/i, 'past'],
  [/\b(?:plural|plural form) of\b/i, 'plural'],
  [/\b(?:ing form|-ing form|gerund) of\b/i, 'gerund'],
  [/\bcomparative of\b/i, 'comparative'],
  [/\bsuperlative of\b/i, 'superlative'],
  [/\bthird person(?: singular)?(?: form)? of\b/i, '3rd_present'],
];
const LEX_CONTEXT_RE = /\b(?:in|inside|within)\s+(?:the\s+|a\s+|an\s+)?(.{2,50})$/i;

const LEX_SYN_PATTERNS = [
  /synonyms? (?:of|for)\s+(.+)/i,
  /(?:similar|other) words? (?:for|to)\s+(.+)/i,
  /another word for\s+(.+)/i,
  /words? like\s+(.+)/i,
  /(?:مترادف|هم‌?معنی)\s*(?:های|ها|ی|کلمه|واژه)?\s*(.+)/,
];
const LEX_ANT_PATTERNS = [
  /antonyms? (?:of|for)\s+(.+)/i,
  /(?:opposite|contrary) (?:of|to)\s+(.+)/i,
  /(?:متضاد|مخالف|برعکس)\s*(?:های|ها|ی|کلمه|واژه)?\s*(.+)/,
];
const LEX_FORM_PATTERNS = {
  past: [/past (?:simple|tense|form) of\s+(.+)/i, /(?:ماضی|گذشته)\s*(.+)/],
  past_participle: [/past participle of\s+(.+)/i, /اسم مفعول\s*(.+)/],
  plural: [/plural of\s+(.+)/i, /جمع\s*(.+)/],
  gerund: [/(?:ing form|-ing form|gerund) of\s+(.+)/i],
  comparative: [/comparative of\s+(.+)/i],
  superlative: [/superlative of\s+(.+)/i],
  '3rd_present': [/third person(?: singular)?(?: form)? of\s+(.+)/i],
};
const LEX_EXAMPLE_PATTERNS = [
  /examples? (?:with|of|for|using)\s+(.+)/i,
  /sentences? (?:with|using)\s+(.+)/i,
  /(?:use|using) (.+?) in (?:a|the|one) sentence/i,
  /چند مثال با\s+(.+)/,
  /مثال(?:ی|های)? با\s+(.+)/,
];
const LEX_TARGET_TRIM = /\s*(?:رو\s*)?(?:بگو|بگویید|بگین|بگید|چیه|چیست|چی|هست|را|کلمه|واژه|یعنی|چه)\s*$/u;

const LEX_STOP = new Set([
  'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'of', 'to',
  'for', 'with', 'from', 'by', 'as', 'is', 'are', 'was', 'were', 'be',
  'been', 'being', 'it', 'its', 'this', 'that', 'these', 'those', 'i',
  'you', 'he', 'she', 'we', 'they', 'my', 'your', 'his', 'her', 'our',
  'their', 'me', 'him', 'them', 'do', 'does', 'did', 'what', 'which',
  'mean', 'means', 'meaning', 'word', 'sentence', 'use', 'used', 'using',
  'say', 'said', 'tell', 'explain', 'please', 'can', 'could', 'would',
  'should', 'how', 'when', 'where', 'why', 'there', 'here', 'not',
]);

const VAGUE_MEANING_EN = /^(?:what(?:'s|s| is)?\s+(?:the\s+)?meaning(?:\s+of\s+(?:this|that|it))?|what\s+does\s+(?:this|that|it|this\s+word|that\s+word)\s+mean|what\s+do\s+you\s+mean(?:\s+by\s+(?:this|that|it))?)\s*[?.!]*$/i;
const VAGUE_MEANING_FA = /^(?:(?:این|اون|آن)\s*یعنی\s*(?:چی|چه)|یعنی\s*(?:چی|چه)|معنی\s*(?:این|اون|آن)\s*(?:چیه|چیست|هست)|منظورت\s*(?:از\s*(?:این|اون|آن))?\s*(?:چیه|چیست))\s*[؟?.!]*$/;

/* Is `short` the longer word with letters missing?
 *
 * "resilent" is one edit from both "resident" (a substitution) and
 * "resilient" (a dropped letter), and distance alone cannot choose between
 * them. A dropped letter is the commoner typo of the two, so the candidate
 * that keeps every letter the learner typed, in order, is offered first. */
function isSubsequence(short, long) {
  let at = 0;
  for (const ch of short) {
    at = long.indexOf(ch, at);
    if (at === -1) return false;
    at += ch.length;
  }
  return true;
}

function editDistance(a, b) {
  if (a === b) return 0;
  if (a.length < b.length) [a, b] = [b, a];
  let previous = Array.from({ length: b.length + 1 }, (_, i) => i);
  for (let i = 1; i <= a.length; i++) {
    const current = [i];
    for (let j = 1; j <= b.length; j++) {
      current.push(Math.min(
        previous[j] + 1,
        current[j - 1] + 1,
        previous[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1),
      ));
    }
    previous = current;
  }
  return previous[b.length];
}

const REGISTER_STOPWORDS = new Set([
  'a', 'an', 'the', 'and', 'or', 'but', 'if', 'in', 'on', 'at', 'to',
  'for', 'of', 'with', 'from', 'by', 'as', 'is', 'am', 'are', 'was',
  'were', 'be', 'been', 'being', 'do', 'does', 'did', 'have', 'has',
  'had', 'i', 'me', 'my', 'we', 'us', 'our', 'you', 'your', 'he',
  'him', 'his', 'she', 'her', 'it', 'its', 'they', 'them', 'their',
  'this', 'that', 'these', 'those', 'please', 'can', 'could', 'would',
  'should', 'will', 'just', 'very', 'really', 'so', 'not', 'no',
]);

function contentTokens(text) {
  const out = new Set();
  for (let word of (text.toLowerCase().match(/[a-z]+/g) || [])) {
    if (word.length <= 2 || REGISTER_STOPWORDS.has(word)) continue;
    if (word.length > 4 && word.endsWith('s')) word = word.slice(0, -1);
    out.add(word);
  }
  return out;
}

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
    "- Pronunciation      → ask: 'how do you pronounce hospital'\n" +
    "- Register           → ask: 'how do I say sorry formally'\n" +
    "- Listening practice → ask: 'listen A1' or 'گوش دادن A1'\n" +
    "- Sounds guide       → ask: 'phonetics' or 'تلفظ'\n" +
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
    "- تلفظ             → بپرس: 'تلفظ hospital' یا 'how do you pronounce hospital'\n" +
    "- سطح رسمیت        → بپرس: 'چطور بگم ببخشید دیر کردم رسمی'\n" +
    "- تمرین شنیدن      → بپرس: 'گوش دادن A1' یا 'listen A1'\n" +
    "- راهنمای صداها    → بپرس: 'تلفظ' یا 'phonetics'\n" +
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
    this.phonetics = (data.phonetics && data.phonetics.sections) ||
      data.phonetics || [];
    this.register = data.register || null;
    this.daily = Object.assign(
      { version: 1, words: [], expressions: [], conversations: [] },
      data.daily || {});
    this.today = data.today || null;   // injectable for the tests
    this.dailyPractice = null;

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
    this.cleanAnswers();
    this.lastJokeId = null;
    // What the learner is looking at right now. Without this, "exercises"
    // after a lesson is a dictionary miss instead of "start that lesson".
    this.lastLesson = null;
    this.lastPhrase = null;
    this.lastLevel = null;
    this.lastExamples = [];
    // The dictionary is ~20k headwords, so it is read one shard at a time for
    // the words of the current message and cached — never parsed at boot.
    // Where no loader or shards exist (the node tests, an old APK) every
    // lookup falls through to the glossary and then to not-found, exactly as
    // before the dictionary was added.
    this.lexShards = new Map();
    this.lexLoading = new Set();
    this.lexIndex = null;   // filled by the first loadLexiconFor()
    this.lexFa = data.lexFa || null;
    this.lexFaCache = null;
    this.lexLoader = data.lexLoader || ((path) => fetch(`${data.lexBase || 'data/'}${path}.json`)
      .then((r) => (r.ok ? r.json() : null)));
  }

  /* Drop blank answer slots at load time. An empty string in a question's
   * answers is invisible in the JSON but very visible to a learner: "show
   * answer" printed " / no article / zero" with a leading blank. A blank is
   * also never something anyone can type, so in the data it can only be a
   * mistake. */
  cleanAnswers() {
    for (const topic of Object.values(this.grammar)) {
      for (const stage of ['practice', 'exam']) {
        for (const q of (topic[stage] || [])) {
          if (!Array.isArray(q.a)) continue;
          const cleaned = q.a.map((a) => String(a).trim()).filter(Boolean);
          if (cleaned.length && cleaned.join('\u0000') !== q.a.join('\u0000'))
            q.a = cleaned;
        }
      }
    }
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
    const foldedFa = foldFa(text);
    let best = null;
    let bestScore = 0;
    for (const intent of this.intents) {
      let score = 0;
      for (const kw of intent.keywords[lang] || []) {
        const weight = kw.trim().split(/\s+/).length > 1 ? 3 : 2;
        if (lang === 'en') {
          if (wordRe(kw, true).test(lowered)) score += weight;
        } else if (foldedFa.includes(foldFa(kw))) {
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
        let hit = lang === 'en' ? wordRe(kw).test(lowered) : text.includes(kw);
        // "I have to go now" is a learner leaving, not a request for the modals
        // lesson: a keyword that names a verb phrase stops naming the topic
        // once a subject stands in front of it.
        if (hit && lang === 'en' &&
            new RegExp('\\b(?:i|you|we|they|he|she|it)\\s+' + esc(kw) + '\\b').test(lowered)) {
          hit = false;
        }
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
    topic.structure.forEach((s) => parts.push(`• ${s.en}\n  ↲ ${s.fa}`));
    if (topic.tip) parts.push(`\n💡 Tip: ${topic.tip.en}\n   ↲ ${topic.tip.fa}`);
    const notes = topic.explain || [];
    if (notes.length) {
      parts.push('\n2️⃣ Explanation / توضیح');
      notes.forEach((n) => parts.push(`• ${n.en}\n  ↲ ${n.fa}`));
    }
    parts.push('\n3️⃣ Function / کاربرد');
    topic.function.forEach((f) => parts.push(`• ${f.en}\n  ↲ ${f.fa}`));
    parts.push('\n4️⃣ Examples / مثال‌ها');
    topic.examples.forEach((e, i) => parts.push(`${i + 1}. ${e.en}\n   ↲ ${e.fa}`));
    const practiceN = (topic.practice || []).length;
    const examN = (topic.exam || []).length;
    const done = this.practiceDone.has(topicId);
    parts.push('\n5️⃣ Exercises / تمرین');
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

  startGrammarSession(topicId, stage, lang) {
    const topic = this.grammar[topicId];
    this.lastLesson = topicId;
    if (stage === 'exam') {
      if (!this.practiceDone.has(topicId)) {
        const n = lang === 'fa'
          ? toPersianDigits((topic.practice || []).length)
          : String((topic.practice || []).length);
        const title = lang === 'fa' ? topic.title.fa : topic.title.en;
        return lang === 'fa'
          ? `🔒 آزمون قفل است — اول تمرین (${n} سوال) را کامل کن.\nبنویس: 'تمرین ${title}'`
          : `🔒 The exam is locked — finish the practice first (${n} questions).\nType: '${topic.title.en.toLowerCase()} exercises'`;
      }
      const intro = lang === 'fa'
        ? `🎓 شروع آزمون «${topic.title.fa}» — موفق باشی!\n`
        : `🎓 Starting the '${topic.title.en}' exam — good luck!\n`;
      this.exercise = { topic: topicId, index: 0, lang, stage: 'exam' };
      this.exerciseScore = 0;
      return intro + this.formatExerciseCard(topic, 0, lang, 'exam');
    }
    const intro = lang === 'fa'
      ? `✏️ شروع تمرین «${topic.title.fa}» — موفق باشی!\n`
      : `✏️ Starting '${topic.title.en}' practice — good luck!\n`;
    this.exercise = { topic: topicId, index: 0, lang, stage: 'practice' };
    this.exerciseScore = 0;
    return intro + this.formatExerciseCard(topic, 0, lang, 'practice');
  }

  handleGrammar(text, lowered, lang) {
    // A Persian question can name an English grammar term — "میشه present
    // perfect رو برام explain کنی؟" — so try the detected language first and
    // the other one after it. The lesson still renders in the question's
    // language.
    const found = this.matchGrammarTopic(text, lowered, lang) ||
      this.matchGrammarTopic(text, lowered, lang === 'fa' ? 'en' : 'fa');
    if (found) {
      const [topicId, topic] = found;
      if (this.wantsExam(text, lowered, lang))
        return this.startGrammarSession(topicId, 'exam', lang);
      if (this.wantsExercises(text, lowered, lang))
        return this.startGrammarSession(topicId, 'practice', lang);
      // remember what they are reading, so "exercises" and "show answer"
      // work on the next message
      this.lastLesson = topicId;
      this.lastExamples = exampleAnswers(topic);
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
        // The gate is real: a reveal or a retry leaves the score short and the
        // exam closed. Only a clean run opens it.
        if (score < total) return this.practiceRetry(topic, score, total, lang);
        this.practiceDone.add(topicId);
        return this.practiceUnlocked(topic, lang);
      }
      return this.formatScoreReport(topic, score, total, lang, stage);
    }
    return this.formatExerciseCard(topic, index, lang, stage);
  }

  practiceRetry(topic, score, total, lang) {
    if (lang === 'fa') {
      return `🔒 تمرین تمام شد، ولی نمره‌ات ${toPersianDigits(score)} از ` +
        `${toPersianDigits(total)} است.\n${'─'.repeat(30)}\n` +
        "آزمون فقط وقتی باز می‌شود که همه‌ی پاسخ‌ها درست باشند.\n" +
        `دوباره تلاش کن: 'تمرین ${topic.title.fa}'`;
    }
    return `🔒 Practice finished — ${score}/${total} correct.\n` +
      `${'─'.repeat(30)}\n` +
      'The exam opens only after a perfect run: every answer right.\n' +
      `Try again: '${topic.title.en.toLowerCase()} exercises'`;
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
    const lookupAsk = isLookupAsk(text, lowered);
    for (const topic of Object.values(this.phrases)) {
      for (const lang of ['en', 'fa']) {
        for (const kw of topic.keywords[lang] || []) {
          if (lang === 'en') {
            if (wordRe(kw).test(lowered)) {
              if (lookupAsk && !kw.trim().includes(' ')) continue;
              return topic;
            }
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
    // remember the bank, so "repeat that" works on the next message
    this.lastPhrase = topic.id;
    const parts = [`💬 ${topic.title.en} (${topic.title.fa})`];
    topic.phrases.forEach((p) => parts.push(`• ${p.en}\n  ↲ ${p.fa}`));
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
      parts.push(`${i + 1}. ${s.en}\n   \u21b2 ${s.fa}`);
    });
    return parts.join('\n');
  }

  handleListening(text, lowered, lang) {
    // "speak" and the Persian verb of asking are not listening words: "speak
    // english" is a switch request and "speak more slowly" is a speed request,
    // and the band list is the wrong answer for both. They count only when a
    // band is named with them — "speak A1", "B1 رو بگو" — or "سطح b1 چیه"
    // would come back as a listening lesson instead of its explanation.
    let level = this.matchListeningLevel(text, lowered);
    const asked = /\b(listen|listening|audio|voice)\b/.test(lowered) ||
      ['گوش دادن', 'آواز'].some((w) => text.includes(w)) ||
      (level !== null && (/\bspeak\b/.test(lowered) || text.includes('بگو')));
    // a learner often just types the band itself: "A1", "b2", "C2"
    const bare = /^\s*([abc][12])\s*[?!.؟]*\s*$/.exec(lowered);
    if (!asked && !bare) return null;
    if (!level && bare) level = this.matchListeningLevel(bare[1], bare[1]);
    if (level) { this.lastLevel = level; return this.formatListeningLevel(level); }
    const names = this.listening.map((l) => l.title.en.split(' · ')[0]).join(' · ');
    return `\u{1F3A7} Listening levels — سطح شنیدن: ${names}\n` +
      "Ask: 'listen A1' or 'گوش دادن A1'";
  }

  /* ------------------------------------------------- daily english ------- */

  dailyKey(dateKey) {
    return dateKey || this.today || localDateKey(new Date());
  }

  /* Today's three items. A pure function of the date, so the panel, the CLI
   * and this engine all show the same card on the same day. */
  dailySelection(dateKey) {
    const key = this.dailyKey(dateKey);
    const day = dailyDayNumber(key);
    const picked = { date: key, version: this.daily.version || 1 };
    for (const [name, salt] of Object.entries(DAILY_SALTS)) {
      const rows = this.daily[name] || [];
      picked[name] = rows.length ? rows[dailyIndex(day, rows.length, salt)] : null;
    }
    return picked;
  }

  _examplesBlock(entry, lang, head) {
    const lines = [head];
    (entry.examples || []).forEach((ex, i) => {
      lines.push(`   ${i + 1}. ${ex.en}`, `      ↲ ${ex.fa}`);
    });
    return lines;
  }

  formatDailyWord(entry, lang) {
    const head = lang === 'en'
      ? '\u{1F4C5}  Word of the Day — لغت امروز'
      : '\u{1F4C5}  لغت امروز — Word of the Day';
    const lines = [head, ''];
    lines.push(`  ${entry.en}   ${entry.ipa || ''}`.replace(/\s+$/, ''));
    const meta = [entry.pos, entry.level].filter(Boolean).join(' · ');
    if (meta) lines.push(`  ${meta}`);
    lines.push(`  ↲ ${entry.fa}`);
    if (entry.def) lines.push(`  ${entry.def.en || ''}`, `  ↲ ${entry.def.fa || ''}`);
    lines.push('');
    lines.push(...this._examplesBlock(entry, lang,
      lang === 'en' ? '  Examples — مثال‌ها:' : '  مثال‌ها — Examples:'));
    if (entry.syn) lines.push(`  Synonyms — مترادف: ${entry.syn.join(' · ')}`);
    if (entry.ant) lines.push(`  Antonyms — متضاد: ${entry.ant.join(' · ')}`);
    return lines.join('\n');
  }

  formatDailyExpression(entry, lang, examplesOnly = false) {
    const head = lang === 'en'
      ? '\u{1F4C5}  Expression of the Day — عبارت امروز'
      : '\u{1F4C5}  عبارت امروز — Expression of the Day';
    const meta = [entry.register, entry.level].filter(Boolean).join(' · ');
    const lines = [head, '', `  “${entry.en}”`, `  ↲ ${entry.fa}`];
    if (meta) lines.push(`  ${meta}`);
    if (!examplesOnly) {
      for (const [field, label] of [['use', 'Means'], ['when', 'When']]) {
        const body = entry[field];
        if (body) lines.push('', `  ${label}: ${body.en || ''}`, `  ↲ ${body.fa || ''}`);
      }
    }
    lines.push('');
    lines.push(...this._examplesBlock(entry, lang,
      lang === 'en' ? '  Examples — مثال‌ها:' : '  مثال‌ها — Examples:'));
    if (entry.alt) {
      lines.push('', `  Also say: “${entry.alt.en || ''}”`, `  ↲ ${entry.alt.fa || ''}`);
    }
    return lines.join('\n');
  }

  formatDailyConversation(entry, lang) {
    const head = lang === 'en'
      ? '\u{1F4C5}  Conversation of the Day — مکالمه امروز'
      : '\u{1F4C5}  مکالمه امروز — Conversation of the Day';
    const topic = entry.topic || {};
    const setting = entry.setting || {};
    const lines = [head, '',
      `  ${topic.en || ''} — ${topic.fa || ''}   (${entry.level || ''})`];
    if (setting.en || setting.fa) lines.push(`  ${setting.en || ''}`, `  ↲ ${setting.fa || ''}`);
    lines.push('');
    for (const turn of entry.turns || []) {
      lines.push(`  ${turn.who}: ${turn.en}`, `      ↲ ${turn.fa}`);
    }
    if ((entry.key || []).length) {
      lines.push('', lang === 'en'
        ? '  Useful phrases — عبارت‌های کلیدی:'
        : '  عبارت‌های کلیدی — Useful phrases:');
      for (const row of entry.key) lines.push(`   • ${row.en}  —  ${row.fa}`);
    }
    for (const note of entry.notes || []) {
      lines.push(`  ↲ ${note.en}`, `    ↲ ${note.fa}`);
    }
    lines.push('', lang === 'en'
      ? "  Practice it: ‘practice today's conversation’"
      : '  تمرینش کن: «مکالمه امروز رو باهام تمرین کن»');
    return lines.join('\n');
  }

  formatDailyDigest(picked, lang) {
    const head = lang === 'en'
      ? '\u{1F4C5}  Today\'s English — انگلیسی امروز'
      : '\u{1F4C5}  انگلیسی امروز — Today\'s English';
    const parts = [head, `  ${picked.date}`, ''];
    const word = picked.words;
    if (word) parts.push(`\u{1F9E0}  ${word.en}  ${word.ipa || ''}  —  ${word.fa}`);
    const expr = picked.expressions;
    if (expr) parts.push(`\u{1F5E3}  “${expr.en}”  —  ${expr.fa}`);
    const conv = picked.conversations;
    if (conv) {
      const topic = conv.topic || {};
      parts.push(`\u{1F4AC}  ${topic.en || ''}  —  ${topic.fa || ''}   (${conv.level || ''})`);
    }
    parts.push('');
    if (lang === 'en') {
      parts.push("Ask: ‘explain today's word’, ‘today's expression’, " +
        "‘today's conversation’");
      parts.push('   ↲ بپرس: «لغت امروز»، «عبارت امروز»، «مکالمه امروز»');
    } else {
      parts.push('بپرس: «لغت امروز»، «عبارت امروز»، «مکالمه امروز»');
      parts.push("   ↲ Or in English: today's word / expression / conversation");
    }
    return parts.join('\n');
  }

  wantsDaily(text, lowered) {
    if (DAILY_WORD_RE.test(lowered) || DAILY_WORD_FA.some((w) => text.includes(w))) return 'word';
    if (DAILY_EXPRESSION_RE.test(lowered) || DAILY_EXPRESSION_FA.some((w) => text.includes(w))) return 'expression';
    if (DAILY_CONVERSATION_RE.test(lowered) || DAILY_CONVERSATION_FA.some((w) => text.includes(w))) return 'conversation';
    if (DAILY_ANY_RE.test(lowered) || DAILY_ANY_FA.some((w) => text.includes(w))) return 'all';
    return null;
  }

  handleDaily(text, lowered, lang) {
    const which = this.wantsDaily(text, lowered);
    if (!which) return null;
    const picked = this.dailySelection();
    const wantsPractice = PRACTICE_ASK.some((w) => lowered.includes(w) || text.includes(w));
    const wantsMore = EXAMPLES_ASK.some((w) => lowered.includes(w) || text.includes(w));
    if (which === 'word' && picked.words) return this.formatDailyWord(picked.words, lang);
    if (which === 'expression' && picked.expressions) {
      return this.formatDailyExpression(picked.expressions, lang, wantsMore);
    }
    if (which === 'conversation' && picked.conversations) {
      if (wantsPractice) return this.startDailyPractice(picked.conversations, lang);
      return this.formatDailyConversation(picked.conversations, lang);
    }
    if (!Object.keys(DAILY_SALTS).some((k) => picked[k])) {
      return 'The daily catalogue is empty. / کاتالوگ روزانه خالی است.';
    }
    return this.formatDailyDigest(picked, lang);
  }

  startDailyPractice(entry, lang) {
    const turns = entry.turns || [];
    if (turns.length < 2) {
      this.dailyPractice = null;
      return this.formatDailyConversation(entry, lang);
    }
    this.dailyPractice = { id: entry.id, turn: 1, right: 0, said: 0 };
    const topic = entry.topic || {};
    const head = lang === 'en'
      ? '\u{1F5E3}  Practice — تمرین مکالمه'
      : '\u{1F5E3}  تمرین مکالمه — Practice';
    const first = turns[0];
    const mine = turns[1];
    return [head, '', `  ${topic.en || ''} — ${topic.fa || ''}`, '',
      `  ${first.who}: ${first.en}`, `      ↲ ${first.fa}`, '',
      lang === 'fa'
        ? `  Your line — ${mine.who} چه می‌گوید؟`
        : `  Your line — what does ${mine.who} say?`,
      '  (say ‘stop’ to leave / برای خروج بنویس «متوقف»)',
    ].join('\n');
  }

  handleDailyPractice(text, lowered, lang) {
    if (!this.dailyPractice) return null;
    const session = this.dailyPractice;
    const entry = (this.daily.conversations || [])
      .find((c) => c.id === session.id);
    if (!entry) { this.dailyPractice = null; return null; }
    const leaving = EXIT_WORDS.some((w) => wordRe(w).test(lowered)) ||
      EXIT_WORDS_FA.some((w) => text.includes(w));
    if (leaving) {
      this.dailyPractice = null;
      return lang === 'en' ? '👍 Practice ended. / تمرین تمام شد.'
        : '👍 تمرین تمام شد. / Practice ended.';
    }
    // A new daily question leaves the drill rather than being graded as an
    // answer to the line on screen: somebody reading the cards can ask
    // "لغت امروز" half way through the dialogue, and "not quite" is the wrong
    // answer to a question.
    if (this.wantsDaily(text, lowered)) {
      this.dailyPractice = null;
      return null;
    }
    const turns = entry.turns || [];
    const index = session.turn;
    if (index >= turns.length) { this.dailyPractice = null; return null; }
    const expected = turns[index].en;
    session.said += 1;
    const lines = [];
    if (sameSpoken(text, expected)) {
      session.right += 1;
      lines.push(lang === 'en' ? '✅ Well said — آفرین.' : '✅ آفرین — well said.');
    } else {
      lines.push((lang === 'en' ? '❌ Not quite — نه دقیقاً. ' : '❌ نه دقیقاً — not quite. ') +
        `${turns[index].who}: ${expected}`);
      lines.push(`      ↲ ${turns[index].fa}`);
    }
    const follow = index + 1;
    if (follow + 1 < turns.length) {
      session.turn = follow + 1;
      lines.push('', `  ${turns[follow].who}: ${turns[follow].en}`,
        `      ↲ ${turns[follow].fa}`, '',
        lang === 'fa'
          ? `  Your line — ${turns[follow + 1].who} چه می‌گوید؟`
          : `  Your line — what does ${turns[follow + 1].who} say?`);
    } else {
      this.dailyPractice = null;
      lines.push('', lang === 'en'
        ? '\u{1F389} Conversation complete — مکالمه تمام شد.'
        : '\u{1F389} مکالمه تمام شد — conversation complete.',
        `  Lines said back: ${session.right}/${session.said}`);
    }
    return lines.join('\n');
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

  /* ------------------------------------------------------------ dictionary */
  attachLexicon(shards) {
    for (const [name, shard] of Object.entries(shards || {}))
      this.lexShards.set(name, shard);
  }

  /* Fetch the shards this message could touch - and only those. Called by the
   * page before respond(), because a fetch cannot be synchronous and respond()
   * must stay so. Already-loaded shards resolve without a request. */
  async loadLexiconFor(text) {
    if (!this.lexLoader) return;
    // Which shards exist: only some three-letter prefixes have one, so without
    // the list every word costs a wasted 404 on its three-letter candidate.
    // A missing list (an older bundle) simply means asking for both.
    if (this.lexIndex === null) {
      let index = null;
      try {
        index = await this.lexLoader('lex/_index');
      } catch (err) {
        index = null;
      }
      this.lexIndex = new Set((index && index.names) || []);
    }
    // A Persian question is answered from the reverse index, which is a file of
    // its own; it is read on the first Persian message, not at boot.
    if (this.lexFa === null && /[\u0600-\u06FF]/.test(String(text || ''))) {
      try {
        this.lexFa = await this.lexLoader('lex/_fa');
      } catch (err) {
        this.lexFa = null;
      }
      this.lexFaCache = null;
    }
    const words = String(text || '').match(/[A-Za-z][A-Za-z'’-]*/g) || [];
    const pending = [];
    for (const word of words) {
      for (const name of lexShardNames(word)) {
        if (this.lexIndex.size && !this.lexIndex.has(name)) continue;
        if (this.lexShards.has(name) || this.lexLoading.has(name)) continue;
        this.lexLoading.add(name);
        pending.push(this.lexLoader(`lex/${name}`)
          .then((shard) => this.lexShards.set(name, shard || null))
          .catch(() => this.lexShards.set(name, null)));
      }
    }
    if (pending.length) await Promise.all(pending);
  }

  lexShard(name) {
    return this.lexShards.has(name) ? this.lexShards.get(name) : null;
  }

  lexFind(word) {
    const key = normalizeWord(word);
    if (!key || !/^[a-z][a-z' -]*$/.test(key)) return null;
    for (const name of lexShardNames(key)) {
      const shard = this.lexShard(name);
      if (shard && shard.w && Object.prototype.hasOwnProperty.call(shard.w, key))
        return [key, shard.w[key]];
    }
    for (const name of lexShardNames(key)) {
      const shard = this.lexShard(name);
      if (!shard || !shard.f) continue;
      const base = shard.f[key];
      if (base && shard.w && shard.w[base]) return [base, shard.w[base]];
    }
    return null;
  }

  lexNear(word, limit = 3) {
    const key = normalizeWord(word);
    if (key.length < 3) return [];
    const maxDist = key.length <= 5 ? 1 : 2;
    const found = [];
    for (const name of lexShardNames(key)) {
      const shard = this.lexShard(name);
      if (!shard || !shard.w) continue;
      for (const candidate of Object.keys(shard.w)) {
        if (Math.abs(candidate.length - key.length) > maxDist) continue;
        const dist = editDistance(key, candidate);
        if (!dist || dist > maxDist) continue;
        // "resilent" is one edit from both "resident" and "resilient"; the
        // longer shared prefix is the one the learner was typing towards.
        let shared = 0;
        while (shared < key.length && shared < candidate.length
          && key[shared] === candidate[shared]) shared++;
        found.push([dist, isSubsequence(key, candidate) ? 0 : 1, -shared, candidate]);
      }
    }
    found.sort((a, b) => a[0] - b[0] || a[1] - b[1] || a[2] - b[2]
      || (a[3] < b[3] ? -1 : a[3] > b[3] ? 1 : 0));
    const out = [];
    for (const [, , , candidate] of found) {
      if (!out.includes(candidate)) out.push(candidate);
      if (out.length === limit) break;
    }
    return out;
  }

  lexPersian(word) {
    if (this.lexFaCache === null)
      this.lexFaCache = (this.lexFa && this.lexFa.p) || {};
    const key = normalizeFa(word);
    return this.lexFaCache[key] || [];
  }

  _lexPosText(entry, lang) {
    const pos = entry.p || [];
    if (!pos.length) return '';
    return lang === 'fa'
      ? pos.map((p) => LEX_POS_FA[p] || p).join('، ')
      : pos.join(', ');
  }

  _lexIpa(entry) {
    const ipa = entry.i || {};
    const us = ipa.us, uk = ipa.uk;
    if (us && uk && us !== uk) return ` /${us}/ (US) · /${uk}/ (UK)`;
    if (us || uk) return ` /${us || uk}/`;
    return '';
  }

  _lexSenseScore(sense, tokens) {
    const hay = [sense[1] || '', sense[3] || '', sense[2] || ''].join(' ');
    const words = hay.toLowerCase().match(/[a-z']{2,}/g) || [];
    let score = 0;
    for (const w of new Set(words)) if (tokens.has(w)) score++;
    return score;
  }

  formatLexEntry(head, entry, asked, lang, context = null, contextText = '') {
    const senses = entry.s || [];
    let best = null;
    if (context && context.size) {
      const scored = senses.map((s, i) => [this._lexSenseScore(s, context), i])
        .sort((a, b) => (a[0] !== b[0] ? b[0] - a[0] : a[1] - b[1]));
      if (scored.length && scored[0][0] > 0) best = scored[0][1];
    }

    const askedNorm = normalizeWord(asked);
    const label = askedNorm === head ? `**${head}**` : `**${asked}** → **${head}**`;
    let line = `📖 ${label}${this._lexIpa(entry)}`;
    const posText = this._lexPosText(entry, lang);
    if (posText) line += ` — ${posText}`;
    if (senses.length > 1) {
      line += lang === 'fa'
        ? ` · ${toPersianDigits(senses.length)} معنی`
        : ` · ${senses.length} meanings`;
    }
    const lines = [line];

    const shownCount = Math.min(senses.length,
      Math.max(3, (best === null ? 0 : best) + 1));
    for (let i = 0; i < shownCount; i++) {
      const shown = i + 1;
      const sense = senses[i] || [];
      const definition = sense[1] || '';
      const meaning = sense[2] || '';
      const example = sense[3] || '';
      const lead = meaning && definition ? `${meaning} — ${definition}`
        : (meaning || definition);
      const mark = best !== null && i === best ? ' ★' : '';
      const num = lang === 'fa' ? toPersianDigits(shown) : String(shown);
      lines.push(`   ${num}. ${lead}${mark}`);
      if (example) lines.push(`      ▸ ${example}`);
    }
    if (context && best !== null) {
      const num = lang === 'fa' ? toPersianDigits(best + 1) : String(best + 1);
      lines.push(lang === 'fa'
        ? `   ↲ در جمله تو، معنی ${num} مناسب‌تر است.`
        : `   ↲ In your sentence, sense ${num} fits best.`);
    } else if (context) {
      const said = String(contextText || '')
        .replace(/^[ .?!؟،]+|[ .?!؟،]+$/g, '');
      lines.push(lang === 'fa'
        ? `   ↲ برای «${said}» معنی‌ای ثبت نکرده‌ام — این‌ها معنی‌های موجودند.`
        : `   ↲ I have no sense recorded for “${said}” — these are the meanings I have.`);
    }
    return lines.join('\n');
  }

  formatLexRelations(head, entry, lang, kind) {
    const groups = entry[kind] || {};
    const syn = kind === 'y';
    const title = lang === 'fa'
      ? `${syn ? '🔗 مترادف‌های' : '⚖️ متضادهای'} **${head}**`
      : `${syn ? '🔗 synonyms of' : '⚖️ opposites of'} **${head}**`;
    if (!Object.keys(groups).length) {
      const empty = lang === 'fa'
        ? '   ↲ در واژه‌نامه ثبت نشده است.'
        : '   ↲ none are recorded in my dictionary.';
      return `${title}\n${empty}`;
    }
    const lines = [title];
    for (const pos of Object.keys(groups)) {
      const words = groups[pos] || [];
      if (!words.length) continue;
      const label = lang === 'fa' ? (LEX_POS_FA[pos] || pos) : pos;
      lines.push(`   • (${label}) ${words.slice(0, 8).join(' · ')}`);
    }
    return lines.join('\n');
  }  formatLexExamples(head, entry, lang) {
    /* English only. The source's Persian sentence for a sense is an
       independent sentence about the word, not a translation of its English
       example - "I sautéed the mushroom with garlic and butter" sat above "I
       bought mushrooms at the market yesterday" - and printed underneath the
       English one it read as a mistranslation. A learner asking for an
       example wants a correct one, not a second sentence beside it. */
    const examples = (entry.s || []).map((s) => s[3] || '').filter(Boolean);
    if (!examples.length) {
      return lang === 'fa'
        ? `🔎 برای **${head}** جمله‌ای ثبت نشده.`
        : `🔎 My dictionary records no example sentence for **${head}**.`;
    }
    const lines = [lang === 'fa'
      ? `📖 **${head}** — مثال‌ها`
      : `📖 **${head}** — examples`];
    for (const example of examples.slice(0, 2)) {
      lines.push(`   ▸ ${example}`);
    }
    return lines.join('\n');
  }

  formatLexForms(head, entry, lang, only = null) {
    const forms = entry.f || [];
    if (only) {
      const hits = forms.filter((f) => f[1] === only).map((f) => f[0]);
      const label = LEX_FORM_LABEL[only] || only;
      if (hits.length) {
        return lang === 'fa'
          ? `🔤 **${head}** — ${label}: ${hits.join('، ')}`
          : `🔤 ${label} of **${head}** → ${hits.join(', ')}`;
      }
      return lang === 'fa'
        ? `🔤 برای **${head}** شکل «${label}» ثبت نشده.`
        : `🔤 My dictionary records no ${label} for **${head}**.`;
    }
    if (!forms.length) {
      return lang === 'fa'
        ? `🔤 برای **${head}** شکلی ثبت نشده.`
        : `🔤 My dictionary records no inflected forms for **${head}**.`;
    }
    const lines = [lang === 'fa'
      ? `🔤 صورت‌های **${head}**`
      : `🔤 forms of **${head}**`];
    for (const [name, ftype] of forms.slice(0, 8)) {
      const label = LEX_FORM_LABEL[ftype] || ftype || 'form';
      lines.push(`   • ${label}: ${name}`);
    }
    return lines.join('\n');
  }

  extractLookupTarget(text, lang) {
    const patterns = lang === 'fa'
      ? FA_LOOKUP_PATTERNS.concat(EN_LOOKUP_PATTERNS)
      : EN_LOOKUP_PATTERNS.concat(FA_LOOKUP_PATTERNS);
    for (const p of patterns) {
      const m = text.match(p);
      if (!m) continue;
      const target = m[1]
        .replace(/^[\s.?!؟،,;:"'«»()[\]]+|[\s.?!؟،,;:"'«»()[\]]+$/g, '')
        .trim();
      if (target) return target;
    }
    return null;
  }

  _lexTarget(text, patterns) {
    for (const p of patterns) {
      const m = text.match(p);
      if (!m) continue;
      let target = m[1]
        .replace(/^[ .?!؟،,;:"'«»()[\]]+|[ .?!؟،,;:"'«»()[\]]+$/g, '');
      for (let i = 0; i < 3; i++) {
        const trimmed = target.replace(LEX_TARGET_TRIM, '').trim();
        if (trimmed === target) break;
        target = trimmed;
      }
      if (target) return target;
    }
    return null;
  }

  _lexResolve(target) {
    const candidates = [target].concat(target.split(/\s+/).reverse());
    for (const candidate of candidates) {
      const found = this.lexFind(candidate);
      if (found) return [candidate, found[0], found[1]];
    }
    return null;
  }

  lexOrNotFound(word, lang) {
    let found = this.lexFind(word);
    if (found) return this.formatLexEntry(found[0], found[1], word, lang);
    if (detectLang(word) === 'fa') {
      const heads = this.lexPersian(word);
      if (heads.length) {
        found = this.lexFind(heads[0]);
        if (found) return this.formatLexEntry(found[0], found[1], word, lang);
      }
    }
    const near = this.lexNear(word);
    if (near.length) {
      found = this.lexFind(near[0]);
      if (found) {
        const [head, entry] = found;
        const lead = lang === 'fa'
          ? `🤔 «${word}» را ندارم — منظورت **${head}** بود؟`
          : `🤔 I don't have "${word}" — did you mean **${head}**?`;
        return `${lead}\n${this.formatLexEntry(head, entry, head, lang)}`;
      }
    }
    return this.notFound(word, lang);
  }

  handleLexicon(text, lowered, lang) {
    // 0) the word in a sentence: "examples with achieve"
    let target = this._lexTarget(text, LEX_EXAMPLE_PATTERNS);
    if (target) {
      const resolved = this._lexResolve(target);
      if (resolved) return this.formatLexExamples(resolved[1], resolved[2], lang);
    }
    // 1) a form of the word: "past tense of seek"
    for (const [pattern, formType] of LEX_FORM_ASKS) {
      if (!pattern.test(text)) continue;
      target = this._lexTarget(text, LEX_FORM_PATTERNS[formType] || []);
      const resolved = target ? this._lexResolve(target) : null;
      if (!resolved) continue;
      return this.formatLexForms(resolved[1], resolved[2], lang, formType);
    }
    // 2) every form the dictionary holds
    if (LEX_FORMS_RE.test(text) || text.includes('صورت‌های')) {
      target = this._lexTarget(text, [/forms? of\s+(.+)/i, /inflections? of\s+(.+)/i]);
      const resolved = target ? this._lexResolve(target) : null;
      if (resolved) return this.formatLexForms(resolved[1], resolved[2], lang);
    }
    // 3) synonyms and opposites
    for (const [patterns, kind, marker, markerFa] of [
      [LEX_SYN_PATTERNS, 'y', LEX_SYNONYMS_RE, LEX_SYNONYMS_FA],
      [LEX_ANT_PATTERNS, 'a', LEX_ANTONYMS_RE, LEX_ANTONYMS_FA],
    ]) {
      const askedNow = marker.test(text) || markerFa.some((w) => text.includes(w));
      if (!askedNow) continue;
      target = this._lexTarget(text, patterns);
      const resolved = target ? this._lexResolve(target) : null;
      if (resolved) return this.formatLexRelations(resolved[1], resolved[2], lang, kind);
    }
    // 4) "what does bank mean in river bank" - a sentence picks the sense
    if (isLookupAsk(text, lowered)) {
      const context = text.match(LEX_CONTEXT_RE);
      target = this.extractLookupTarget(text, lang);
      if (context && target && target.split(/\s+/).length === 1) {
        const found = this.lexFind(target);
        if (found && (found[1].s || []).length > 1) {
          const [head, entry] = found;
          const tokens = new Set(((context[1] || '').toLowerCase()
            .match(/[a-z']{2,}/g) || [])
            .filter((w) => !LEX_STOP.has(w) && w !== normalizeWord(target)));
          if (tokens.size)
            return this.formatLexEntry(head, entry, target, lang, tokens, context[1]);
        }
      }
    }
    return null;
  }

  handleGlossaryLookup(text, lang) {
    // Philosophy, not vocabulary: otherwise "meaning of life" becomes a
    // failed lookup for the word "life".
    if (/\b(?:meaning|purpose) of life\b/i.test(text)) return null;
    // "reply in english" is a request about the reply, not a lookup for the
    // word "reply" — the "<X> in <language>" pattern would translate it.
    if (SWITCH_ASK_RE.test(text)) return null;
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

    // "what does X mean" asks for a definition and the dictionary has one;
    // the glossary holds a translation, which is a different answer.
    if ((DEFINITION_ASK_RE.test(text) || text.includes('معنی'))
      && target.split(/\s+/).length === 1 && detectLang(target) !== 'fa') {
      const found = this.lexFind(target);
      if (found) return this.formatLexEntry(found[0], found[1], target, lang);
    }

    const entries = this.lookupWord(target);
    if (!entries.length) {
      if (target.split(/\s+/).length > 1) return null;
      // The glossary is the curated core; the dictionary behind it covers the
      // rest of English, including the typo suggestion at the end.
      return this.lexOrNotFound(target, lang);
    }
    return this.formatLookup(target, entries, lang);
  }

  _suggestWords(target, limit = 3) {
    const key = normalizeWord(target);
    if (!key) return [];
    const targetFa = detectLang(target) === 'fa';
    const pool = targetFa ? this.glossaryFa : this.glossaryEn;
    const maxDist = key.length <= 5 ? 1 : 2;
    const found = [];
    for (const [normalized, entries] of pool) {
      if (!normalized || Math.abs(normalized.length - key.length) > maxDist) continue;
      const dist = editDistance(key, normalized);
      if (!dist || dist > maxDist) continue;
      for (const entry of entries) {
        const display = targetFa ? entry[2] : entry[1];
        // "aple" should lead to "apple", not the phrase "a pile".
        if (display && (target.includes(' ') || !display.includes(' ')))
          found.push([dist, display.includes(' '), display.toLowerCase(), display]);
      }
    }
    found.sort((a, b) => a[0] - b[0]
      || (a[1] === b[1] ? 0 : a[1] ? 1 : -1)
      || (a[2] < b[2] ? -1 : a[2] > b[2] ? 1 : 0)
      || (a[3] < b[3] ? -1 : a[3] > b[3] ? 1 : 0));
    const out = [], seen = new Set();
    for (const [, , folded, display] of found) {
      if (seen.has(folded)) continue;
      seen.add(folded);
      out.push(display);
      if (out.length === limit) break;
    }
    return out;
  }

  notFound(target, lang) {
    const suggestions = this._suggestWords(target);
    if (lang === 'fa') {
      let hint, example;
      if (suggestions.length) {
        const names = suggestions.map((s) => `«${s}»`).join('، ');
        hint = `منظورت ${names} بود؟`;
        example = ` این‌طور بپرس: «معنی ${suggestions[0]} چیه».`;
      } else {
        hint = 'شکل ساده کلمه را امتحان کن (مثلاً go به‌جای went) '
          + 'یا یک دامنه بپرس: رنگ‌ها، حیوانات، میوه‌ها.';
        example = '';
      }
      return `«${target}» توی واژه‌نامه من نیست 📚\n   ↲ ${hint}${example}`;
    }
    let hint, example;
    if (suggestions.length) {
      const names = suggestions.map((s) => `"${s}"`).join(', ');
      hint = `Did you mean ${names}?`;
      example = ` Ask: 'translate ${suggestions[0]}'.`;
    } else {
      hint = "Try the base form (e.g. 'go', not 'went'), or ask for a "
        + 'domain: colors, animals, fruits, numbers.';
      example = '';
    }
    return `I don't have "${target}" in my glossary yet 📚\n   ↲ ${hint}${example}`;
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
      `   ↲ سطح: ${topic.level}`, '', topic.why];
    for (const side of topic.sides) {
      lines.push('');
      lines.push(`  • ${side.en}`);
      if (side.fa) lines.push(`    ↲ ${side.fa}`);
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
    return `🗯  “${row.en}” — ${row.fa}\n   ↲ ${row.meaning}\n   e.g. ${row.example}`;
  }

  _regLabel(key) {
    const reg = ((this.register && this.register.registers) || {})[key] || {};
    const lab = reg.label || {};
    return `${lab.en || key} / ${lab.fa || key}`;
  }

  _regRenderPair(pair, only) {
    const keys = ['formal', 'consultative', 'casual'].includes(only)
      ? [only] : ['formal', 'consultative', 'casual'];
    const out = [`“${pair.meaning.en}” — ${pair.meaning.fa}`, ''];
    for (const k of keys) {
      const body = pair[k];
      if (!body) continue;
      out.push(this._regLabel(k));
      out.push(`  ${body.en}`);
      out.push(`  ↲ ${body.fa}`);
      out.push('');
    }
    if (!only && pair.note) {
      out.push(`↲ ${pair.note.en}`);
      out.push(`↲ ${pair.note.fa}`);
    }
    return out.join('\n').trim();
  }

  /* Character bigrams, not whole words: word overlap works in English and
     fails in Persian, where the inflected form rarely matches the stored
     meaning. Bigrams compare shape and need no stemmer for either script. */
  _regMatch(thing) {
    // \p{L}\p{N}, not \w: JavaScript's \w is ASCII-only, so a negated
    // [^\w\s] class replaces every Persian letter with a space and the
    // query comes back empty. Python's \w is Unicode-aware, so the two
    // engines silently disagreed on exactly the Persian queries.
    const t = (thing.toLowerCase().replace(/[^\p{L}\p{N}\s]/gu, ' ')
      .replace(/\s+/g, ' ').trim());
    if (t.length < 2) return null;
    const grams = (s) => {
      const flat = s.replace(/ /g, '');
      const out = new Set();
      for (let i = 0; i < flat.length - 1; i++) out.add(flat.slice(i, i + 2));
      return out;
    };
    const probe = grams(t);
    if (!probe.size) return null;
    const probeWords = contentTokens(t);
    let best = null, score = 0;
    for (const pair of (this.register && this.register.pairs) || []) {
      const hay = (pair.meaning.en + ' ' + pair.meaning.fa).toLowerCase();
      let s;
      if (hay.includes(t)) s = 1;
      else {
        const target = grams(hay);
        let hit = 0;
        for (const g of probe) if (target.has(g)) hit++;
        s = hit / probe.size;
        // too little signal to be a match: "a word" is four bigrams and two
        // of them land inside "order", which is not the same request
        if (hit < 3) s = 0;
        // Bigrams alone match short courtesy phrases to unrelated sentences
        // ("thank you" vs "can you help me"). Require a real content word.
        if (s && probeWords.size) {
          const hayWords = contentTokens(hay);
          let sharedWord = false;
          for (const w of probeWords) if (hayWords.has(w)) { sharedWord = true; break; }
          if (!sharedWord) s = 0;
        }
      }
      if (s > score) { best = pair; score = s; }
    }
    return score >= 0.45 ? best : null;
  }

  handleRegister(text, lowered, lang) {
    if (!this.register) return null;

    const sit = lowered.match(
      /(?:\bin\b|\bat\b|\bduring\b|\bfor\b)\s+(?:a|an|the)?\s*([\w\s]{3,40}?)\s*[?.!]?$/);
    if (sit && /\b(interview|meeting|email|class|conference|restaurant|shop|doctor|manager|boss|professor)s?\b/
        .test(sit[1])) {
      const asked = sit[1].split(' ');
      for (const s of this.register.situations || []) {
        const blob = (s.situation.en + ' ' + s.situation.fa).toLowerCase();
        // "at a doctors appointment" has to reach "a visit to the doctor":
        // learners type the plural and the app stores the singular.
        if (asked.some((w) => blob.includes(w) || blob.includes(w.replace(/s$/, '')))) {
          return `“${s.situation.en}” — ${s.situation.fa}\n`
            + `→ ${this._regLabel(s.register)}\n`
            + `${s.note.en}\n↲ ${s.note.fa}`;
        }
      }
      return null;
    }

    const m = lowered.match(
      /(?:how (?:do|can|should) (?:i|you|we) say|how to say|how would you say|what (?:do|should) i say|چطور بگم|چطور بگویم|چی بگم)\s+(.+?)\s*(formally|informally|casually|polite|politely|official|رسمی|رسمیانه|خودمانی|محاوره|مؤدبانه)?\s*[?.!]*$/);
    if (m) {
      const thing = m[1].trim()
        .replace(/\s+(formally|informally|casually|polite|politely|official|رسمی|رسمیانه|خودمانی|محاوره|مؤدبانه)$/, '')
        .replace(/[? ]+$/, '').trim();
      const tail = m[2] || '';
      let only = null;
      if (['formally', 'informally', 'casually', 'official', 'رسمی', 'رسمیانه'].includes(tail))
        only = ['informally', 'casually', 'محاوره'].includes(tail) ? 'casual' : 'formal';
      else if (['polite', 'politely', 'مؤدبانه', 'خودمانی'].includes(tail))
        only = tail === 'خودمانی' ? 'casual' : 'consultative';
      // A dictionary word or a stored phrase is a pronunciation question,
      // not a register request: "how do you say thank you".
      if (!tail && (this.lookupWord(thing).length
        || this.lookupPhrase(normalizeWord(thing)))) return null;
      const pair = this._regMatch(thing);
      if (pair) return this._regRenderPair(pair, only);
      // Only claim the query when it actually named a register. "How do you
      // say a word" is a pronunciation question, and swallowing it here took
      // the stress marks with it.
      if (!tail) return null;
      const avail = (this.register.pairs || []).slice(0, 6)
        .map((p) => `*${p.meaning.en}*`).join(', ');
      return `I do not have "${thing}" in the register list yet.\n`
        + `I do have: ${avail}\n↲ هنوز این مورد را ندارم.`;
    }

    if (/\bregisters?\b|formal vs|formal or casual|سطح رسمیت|رسمی یا محاوره|محاوره یا رسمی/
        .test(lowered)) {
      const lines = ['**Register** — one meaning, three ways to say it. / '
        + '**سطح رسمیت** — یک معنا، سه راه برای گفتن.', ''];
      for (const c of this.register.channels || []) {
        lines.push(`• **${c.title.en}** — ${c.blurb.en}`);
        lines.push(`  ↲ ${c.title.fa}: ${c.blurb.fa}`);
      }
      const pairs = this.register.pairs || [];
      if (pairs.length) {
        lines.push('');
        lines.push('Try: ' + pairs.slice(0, 4)
          .map((p) => `*${p.meaning.en}*`).join(', '));
      }
      return lines.join('\n');
    }
    return null;
  }

  handleLifeMeaning(text, lang) {
    if (!(/\b(?:meaning|purpose) of life\b|\bwhy are we here\b/i.test(text)
      || ['معنی زندگی', 'هدف زندگی', 'برای چی اومدیم'].some((p) => text.includes(p))))
      return null;
    const intent = this.intents.find((i) => i.name === 'meaning');
    return intent ? this.replyFromIntent(intent, lang) : null;
  }

  handleVagueMeaning(text, lang) {
    const cleaned = text.trim().replace(/\s+/g, ' ');
    if (!VAGUE_MEANING_EN.test(cleaned) && !VAGUE_MEANING_FA.test(cleaned))
      return null;
    if (lang === 'fa') {
      return 'کدام کلمه یا جمله را می‌پرسید؟ این‌طور بنویسید: '
        + '«معنی <کلمه> چیه» یا «<کلمه> به انگلیسی» '
        + 'تا معنی دقیق و مثال بدهم.';
    }
    return 'Which word or sentence do you mean? Send it like this: '
      + '"define <word>" or "what does <word> mean" — '
      + 'then I can give the exact meaning and an example.';
  }

  handleIdioms(text, lowered, lang) {
    // The idiom on its own is a question about it - "break a leg" is a wish for
    // a good performance, never an instruction about a leg. Kept identical to
    // the Python engine; tests_js_vs_python.py compares the two on it.
    const bare = lowered.replace(/[^\w' \-]+/g, ' ').trim();
    if (bare.split(/\s+/).length >= 2) {
      const hit = this.matchIdiom(bare);
      if (hit) return this.formatIdiom(hit);
    }
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
      if (rule.fix.includes('{pp}')) {
        // only fire when the verb is a past simple that is not also a
        // participle - "have seen" and "have gone" are both correct
        const hit = (m[0].toLowerCase().match(/[a-z']+/g) || []);
        if (!hit.length || !PAST_SIMPLE_ONLY.has(hit[hit.length - 1])) continue;
      }
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
    // "میشه" (could you) opens any polite Persian request, so it is not a
    // check-this-sentence marker: "میشه present perfect رو برام explain کنی؟"
    // is a question about English, not an English sentence to mark.
    const asked = /\b(is (?:this|that|it) (?:correct|right|wrong)|check my|correct (?:my|this|these|the)|fix (?:my|this|my sentence)|is this ok|grammatically|درسته|درست است|غلطه)/.test(lowered)
      || /درسته|غلط/.test(text);
    const sentence = text.replace(
      /^\s*(?:is (?:this|that|it) (?:sentence )?(?:correct|right|ok|wrong)\b[?:]?|(?:please\s+)?correct (?:this|my|these|the)?\s*(?:sentence|text)?\b[:]?|check (?:this|that|my)\s*(?:sentence|text)?\b[:]?|fix (?:my|this)\s*(?:sentence)?\b[:]?|آیا این جمله درسته[؟?]?)\s*/i,
      '').replace(/^[\s.?!؟،,]+|[\s.?!؟،,]+$/g, '');
    if (!sentence) return null;
    if (FA_RE.test(sentence) && !asked) return null;
    // The rules are English rules. A Persian-dominant message asks *about*
    // English; answering it with "this sentence is correct English" was wrong.
    const latin = (sentence.match(/[A-Za-z]/g) || []).length;
    const persian = (sentence.match(/[\u0600-\u06FF]/g) || []).length;
    if (persian && latin < persian) {
      return asked
        ? "Send me the English sentence and I'll mark it. / جملهٔ انگلیسی را بفرست تا بررسی کنم."
        : null;
    }
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
      `   • Phrases: ${Object.keys(this.phrases).length} banks · Listening: ${this.listening.length} levels\n` +
      `   • Idioms: ${idiomCount} · Distinctions: ${Object.keys(this.distinctions).length} confusable pairs`;
  }

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
    // NB: hasOwnProperty on an array tests the INDEX, so "5" would match
    // element 5 of a long list. A plain set-like array needs includes().
    const has = (k) => (Array.isArray(table)
      ? table.includes(k)
      : Object.prototype.hasOwnProperty.call(table, k));
    const val = (k) => (Array.isArray(table) ? k : table[k]);
    const s = lowered.replace(/[.!?؟,;:"'«»()[\]]/g, '').trim();
    if (has(s)) return val(s);
    const m = /^(?:please\s+)?(?:can you\s+|could you\s+)?(?:give me|tell me|show me|let me|start|begin|open)\s+[\w' ]{0,24}$/
      .exec(s);
    if (m) {
      const last = s.split(/\s+/).pop();
      if (has(last)) return val(last);
    }
    return null;
  }

  handleFollowup(text, lowered, lang) {
    if (this.exercise) return null;   // a live quiz owns every message

    const which = this.bare(lowered, this.bareTable('exercise'));
    if (which) {
      if (!this.lastLesson) {
        return lang === 'en'
          ? "Open a lesson first, then say 'exercises'.\n   ↲ اول یک درس را باز کن، بعد بنویس «تمرین».\n   Write 'grammar' for the list of lessons."
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
          ? `💡 Answer: ${this.lastExamples.join(' / ')}\n   ↲ جواب: ${this.lastExamples.join(' / ')}`
          : `💡 جواب: ${this.lastExamples.join(' / ')}\n   Answer: ${this.lastExamples.join(' / ')}`;
      if (this.lastLevel) return this.formatListeningLevel(this.lastLevel);
      return lang === 'en'
        ? 'Nothing to reveal yet — open a lesson or ask me a question.\n   ↲ هنوز چیزی برای نمایش نیست — یک درس را باز کن.'
        : 'هنوز چیزی برای نمایش نیست — یک درس را باز کن.';
    }

    if (this.bare(lowered, this.bareTable('examples'))) {
      const topic = this.grammar[this.lastLesson];
      if (topic) {
        const rows = topic.examples || [];
        this.lastExamples = exampleAnswers(topic);
        return '📝 More examples — مثال‌های بیشتر:\n' + rows.map((r, i) =>
          `   ${i + 1}. ${r.en}\n      ↲ ${r.fa}`).join('\n');
      }
      return 'Open a lesson first and ask for examples.\n   ↲ اول یک درس را باز کن.';
    }

    if (this.bare(lowered, this.bareTable('again'))) return this.tellJoke(text, lang);

    if (this.bare(lowered, this.bareTable('repeat'))) {
      if (this.lastLevel) return this.formatListeningLevel(this.lastLevel);
      if (this.lastPhrase) {
        const topic = this.phrases[this.lastPhrase];
        if (topic) return 'Say it again — دوباره گوش کن:\n' + topic.phrases.slice(0, 4)
          .map((r) => `   • ${r.en}\n     ↲ ${r.fa}`).join('\n');
      }
      return lang === 'en'
        ? 'Tell me what to repeat — a listening band or a sentence bank.\n   ↲ بگو کدام را تکرار کنم.'
        : 'بگو کدام را تکرار کنم.';
    }

    if (this.bare(lowered, this.bareTable('next')) && this.lastLesson)
      return this.startGrammarSession(this.lastLesson, 'practice', lang);

    return null;
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

    // ...and so does the conversation drill, for the same reason
    const dailyDrill = this.handleDailyPractice(text, lowered, lang);
    if (dailyDrill !== null) return dailyDrill;

    const learned = this.learnName(text);

    const section = this.handleSection(text, lowered, lang);
    if (section !== null) return section;

    const followup = this.handleFollowup(text, lowered, lang);
    if (followup !== null) return followup;

    // Daily asks are specific phrases ("today's word"), so they can sit this
    // early without taking anything from the panels below - and they must,
    // because "conversation" and "lesson" belong to sections that would
    // otherwise answer first with a list of everything.
    const daily = this.handleDaily(text, lowered, lang);
    if (daily !== null) return daily;

    let result = this.handleAlphabet(text, lowered);
    if (result === null) result = this.handleLetterLookup(text);
    if (result === null) result = this.handleNumber(text, lang);
    // The dictionary answers four asks nothing above it had: synonyms,
    // opposites, a word's inflected forms, and one word's meaning read in the
    // learner's own sentence. It runs here, ahead of the panels that claim
    // nearby words - "similar words" is a distinction topic, "past tense" is a
    // grammar lesson, but "synonyms for X" and "past tense of seek" are
    // lookups, and the phrase has to win over the topic.
    if (result === null) result = this.handleLexicon(text, lowered, lang);
    // ahead of handlePronounce, which also answers "how do I say X" -
    // a register question is the more specific reading of that phrase
    if (result === null) result = this.handleRegister(text, lowered, lang);
    if (result === null) result = this.handlePronounce(text, lowered, lang);
    if (result === null) result = this.handleDistinction(text, lowered, lang);
    if (result === null) result = this.handleLifeMeaning(text, lang);
    if (result === null) result = this.handleIdioms(text, lowered, lang);
    if (result === null) result = this.handleCorrection(text, lowered, lang);
    if (result === null) result = this.handleStat(text, lowered, lang);
    if (result === null) result = this.handleGrammar(text, lowered, lang);
    if (result === null) result = this.handlePhrases(text, lowered, lang);
    if (result === null) result = this.handleListening(text, lowered, lang);
    if (result === null) result = this.handleGlossaryLookup(text, lang);
    if (result === null) result = this.handleVagueMeaning(text, lang);
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
      if (word && normalizeWord(word)) return this.lexOrNotFound(word, lang);
    }

    if (lang === 'fa') {
      return 'متوجه نشدم 😅 ترجیح می‌دهم حدس نزنم. یکی از این‌ها را امتحان کن:\n'
        + '   • ترجمه کلمه → «سیب به انگلیسی»\n'
        + '   • واژگان → «رنگ‌ها» یا «حیوانات»\n'
        + '   • گرامر → «حال ساده» یا «گرامر»\n'
        + '   • تلفظ → «تلفظ hospital»\n'
        + '   • فهرست کامل → «راهنما»';
    }
    return "I'm not sure I understand yet — I'd rather ask than guess. 😊\n"
      + '   Try one of these:\n'
      + "   • translate a word → 'translate apple'\n"
      + "   • vocabulary → 'colors' or 'what are the fruits'\n"
      + "   • grammar → 'simple present' or 'grammar'\n"
      + "   • pronunciation → 'how do you pronounce hospital'\n"
      + "   • full menu → 'help'";
  }
}

/* The taught forms inside a lesson's examples, for 'show answer'.
 * Each example is written as 'He **goes** to work.' so the bolded span is the
 * answer; if an example has no bold, the whole line is offered. */
function exampleAnswers(topic) {
  const out = [];
  for (const row of (topic.examples || []).slice(0, 4)) {
    const en = row.en || '';
    const bold = en.match(/\*\*(.+?)\*\*/g);
    if (bold) out.push(bold.map((b) => b.replace(/\*\*/g, '')).join(' / '));
    else if (en) out.push(en.replace(/\.$/, ''));
  }
  return out;
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