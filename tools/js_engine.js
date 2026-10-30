/* Checks the JS engine against the Python bot on a set of real inputs.
 * Run: node tests_js_vs_python.js  (writes the python replies to /tmp) */
const fs = require('fs');
const path = require('path');
const root = path.join(__dirname, '..');

const vm = require('vm');
const botSrc = fs.readFileSync(path.join(root, 'android/app/src/main/assets/www/bot.js'), 'utf8');
const data = {
  memory: JSON.parse(fs.readFileSync(path.join(root, 'memory.json'), 'utf8')),
  glossary: JSON.parse(fs.readFileSync(path.join(root, 'glossary.json'), 'utf8')),
  grammar: JSON.parse(fs.readFileSync(path.join(root, 'grammar.json'), 'utf8')),
  phrases: JSON.parse(fs.readFileSync(path.join(root, 'phrases.json'), 'utf8')),
  jokes: JSON.parse(fs.readFileSync(path.join(root, 'jokes.json'), 'utf8')),
  listening: JSON.parse(fs.readFileSync(path.join(root, 'listening.json'), 'utf8')),
  distinctions: JSON.parse(fs.readFileSync(path.join(root, 'distinctions.json'), 'utf8')),
  idioms: JSON.parse(fs.readFileSync(path.join(root, 'idioms.json'), 'utf8')),
  corrections: JSON.parse(fs.readFileSync(path.join(root, 'corrections.json'), 'utf8')),
  phonetics: JSON.parse(fs.readFileSync(path.join(root, 'phonetics.json'), 'utf8')),
  register: JSON.parse(fs.readFileSync(path.join(root, 'register.json'), 'utf8')),
  daily: JSON.parse(fs.readFileSync(path.join(root, 'daily.json'), 'utf8')),
  slang: JSON.parse(fs.readFileSync(path.join(root, 'slang.json'), 'utf8')),
  // The daily rotation is a function of the local date, so pinning it keeps
  // the Python/JS comparison from depending on when the suite is run.
  today: process.env.FLUENTIFY_TODAY || null,
};

/* The dictionary is a directory of shards. In the app the page fetches the
 * shards a message touches; here the same loader reads them from disk, and the
 * same lazy path is exercised - so a shard name the engine asks for but the
 * build never wrote shows up as a missing answer rather than as a test that
 * quietly used a different route. */
const lexDir = path.join(root, 'lexicon');
const lexLoaded = new Map();
data.lexLoader = (name) => {
  if (lexLoaded.has(name)) return Promise.resolve(lexLoaded.get(name));
  let shard = null;
  try {
    const file = path.join(lexDir, String(name).replace(/^lex\//, '') + '.json');
    shard = JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch (err) {
    shard = null;
  }
  lexLoaded.set(name, shard);
  return Promise.resolve(shard);
};
try {
  data.lexFa = JSON.parse(fs.readFileSync(path.join(lexDir, '_fa.json'), 'utf8'));
} catch (err) {
  data.lexFa = null;
}

const ctx = { module: {}, exports: {}, console };
vm.createContext(ctx);
vm.runInContext(botSrc + '\n;this.Fluentify = Fluentify;', ctx);

const cases = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));

/* Two shapes reach this file, told apart by an explicit key so a one-word
 * case can never be mistaken for a flow:
 *   {input: "hello"}                 — one message, one reply
 *   {flow: ["simple present", ...]}  — one bot, replies in order
 * Both get a fresh bot, so state cannot leak between cases.
 *
 * respond() is synchronous, so the dictionary is fetched first for that one
 * message and awaited — which is exactly the order the page uses. */
const out = [];
(async () => {
  for (const entry of cases) {
    const bot = new ctx.Fluentify(data);
    if (Array.isArray(entry.flow)) {
      const replies = [];
      for (const m of entry.flow) {
        await bot.loadLexiconFor(m);
        replies.push(bot.respond(m));
      }
      out.push(replies);
      continue;
    }
    await bot.loadLexiconFor(entry.input);
    out.push(bot.respond(entry.input));
  }
  fs.writeFileSync(process.argv[3], JSON.stringify(out));
  console.log('js replies written:', out.length);
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
