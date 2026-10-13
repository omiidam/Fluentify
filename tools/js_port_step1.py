#!/usr/bin/env python3
"""Port the round-1/2 engine features from chatbot.py into bot.js.

The APK ships bot.js, so every capability added to the Python bot has to be
mirrored here or the two apps drift apart. This rewrites bot.js from the
Python source so the port stays mechanical rather than hand-copied, then
tests_js_vs_python.py proves the two agree.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JS = ROOT / "android/app/src/main/assets/www/bot.js"


def main() -> None:
    src = JS.read_text(encoding="utf-8")

    # ---------------------------------------------------------- helpers ----
    helpers = r'''
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
'''

    anchor = "const LOOKUP_STOPWORDS = new Set(["
    assert anchor in src
    src = src.replace(anchor, helpers.strip() + "\n\n" + anchor, 1)

    # ------------------------------------------------------- constructor ---
    old_ctor = """    this.listening = (data.listening && data.listening.levels) || data.listening || [];"""
    new_ctor = """    this.listening = (data.listening && data.listening.levels) || data.listening || [];
    this.distinctions = {};
    if (data.distinctions)
      for (const t of (data.distinctions.topics || data.distinctions))
        this.distinctions[t.id] = t;
    this.idioms = {};
    if (data.idioms)
      for (const t of (data.idioms.topics || data.idioms)) this.idioms[t.id] = t;
    this.corrections = (data.corrections && data.corrections.rules) ||
      data.corrections || [];"""
    assert old_ctor in src
    src = src.replace(old_ctor, new_ctor, 1)

    JS.write_text(src, encoding="utf-8")
    print("bot.js: helpers + constructor wired")
    print("next: run tools/js_port_step2.py for the handler methods")


if __name__ == "__main__":
    main()