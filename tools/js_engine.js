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
  // The daily rotation is a function of the local date, so pinning it keeps
  // the Python/JS comparison from depending on when the suite is run.
  today: process.env.FLUENTIFY_TODAY || null,
};
const ctx = { module: {}, exports: {}, console };
vm.createContext(ctx);
vm.runInContext(botSrc + '\n;this.Fluentify = Fluentify;', ctx);

const cases = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));

/* A case is either [[msg]] (one message) or [msg, msg, ...] (a flow).
 * Flows get a FRESH bot each, so state cannot leak between cases — which is
 * exactly what tests_flow_parity.py checks on the Python side. */
/* Two shapes reach this file, told apart by an explicit key so a one-word
 * case can never be mistaken for a flow:
 *   {input: "hello"}                 — one message, one reply
 *   {flow: ["simple present", ...]}  — one bot, replies in order
 * Both get a fresh bot, so state cannot leak between cases. */
const out = cases.map((entry) => {
  const isFlow = Array.isArray(entry.flow);
  const bot = new ctx.Fluentify(data);
  if (isFlow) return entry.flow.map((m) => bot.respond(m));
  return bot.respond(entry.input);
});
fs.writeFileSync(process.argv[3], JSON.stringify(out));
console.log('js replies written:', out.length);