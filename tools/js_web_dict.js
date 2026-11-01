/* Formats one dictionary entry with the APK engine, so the checker can compare
 * it byte for byte with chatbot.py's format_api_entry().
 *
 *   node tools/js_web_dict.js <entry.json>
 *
 * The entry is the normalised shape both formatters take - not the raw API
 * payload - because that shape is what the two sides have to agree on. The
 * engine is built with no lexicon loader and no localStorage, so nothing here
 * touches the network or the phone's storage.
 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const root = path.join(__dirname, '..');
const load = (name) => JSON.parse(fs.readFileSync(path.join(root, name), 'utf8'));

const ctx = { module: {}, exports: {}, console };
vm.createContext(ctx);
vm.runInContext(
  fs.readFileSync(
    path.join(root, 'android/app/src/main/assets/www/bot.js'), 'utf8')
    + '\n;this.Fluentify = Fluentify;',
  ctx);

const data = {
  memory: load('memory.json'),
  glossary: load('glossary.json'),
  grammar: load('grammar.json'),
  phrases: load('phrases.json'),
  jokes: load('jokes.json'),
  listening: load('listening.json'),
  distinctions: load('distinctions.json'),
  idioms: load('idioms.json'),
  corrections: load('corrections.json'),
  phonetics: load('phonetics.json'),
  register: load('register.json'),
  daily: load('daily.json'),
  slang: load('slang.json'),
  lexFa: null,
  lexLoader: () => Promise.resolve(null),
  today: null,
};

const bot = new ctx.Fluentify(data);
const entry = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const asked = process.argv[3] || entry.word;

process.stdout.write(JSON.stringify({
  en: bot.formatApiEntry(entry.word, entry, asked, 'en'),
  fa: bot.formatApiEntry(entry.word, entry, asked, 'fa'),
  keys: {
    phrase: bot._apiKey('ice cream'),
    word: bot._apiKey('Serendipity!'),
    persian: bot._apiKey('زبان'),
    empty: bot._apiKey(''),
  },
  targets: {
    bare: bot.wordApiTarget('quokka', 'en'),
    ask: bot.wordApiTarget('what does quokka mean', 'en'),
    phrase: bot.wordApiTarget('ice cream', 'en'),
    persian: bot.wordApiTarget('معنی quokka چیه', 'en'),
    stopword: bot.wordApiTarget('it', 'en'),
  },
}, null, 0));
