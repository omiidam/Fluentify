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
};
const ctx = { module: {}, exports: {}, console };
vm.createContext(ctx);
vm.runInContext(botSrc + '\n;this.Fluentify = Fluentify;', ctx);

const cases = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const bot = new ctx.Fluentify(data);
const out = cases.map(([input]) => bot.respond(input));
fs.writeFileSync(process.argv[3], JSON.stringify(out));
console.log('js replies written:', out.length);