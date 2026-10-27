/* Builds nlp/fluentify-nlp.js — the single file the page and the APK load.
 *
 *   cd nlp && npm install && npm run build
 *
 * The licence notice is embedded as the bundle's first lines rather than left
 * to a file beside it: the APK ships the .js, so the notice has to ride along
 * with it. esbuild is a devDependency and is not bundled.
 */
import {build} from 'esbuild';
import {readFileSync} from 'node:fs';

const NOTICE = `/* Fluentify offline English grammar analyser - generated, do not edit.
 * Bundled runtime: wink-nlp 2.4.0 + wink-eng-lite-web-model 1.8.1
 * Both MIT, (c) 2017-25 GRAYPE Systems Private Limited.
 * Full MIT text, and what the model can and cannot do: nlp/THIRD-PARTY-NOTICES.md
 * Sources: nlp/src/*.js   Rebuild: cd nlp && npm run build
 * Everything in this file runs on the device. It makes no network request. */
`;

const result = await build({
  entryPoints: ['src/entry.js'],
  bundle: true,
  format: 'iife',
  globalName: 'FluentifyNLP',
  minify: true,
  target: 'es2017',
  legalComments: 'none',
  banner: {js: NOTICE},
  outfile: 'fluentify-nlp.js',
  metafile: true,
});

const out = Object.values(result.metafile.outputs)[0];
console.log('wrote fluentify-nlp.js', (out.bytes / (1024 * 1024)).toFixed(2), 'MB');
const inputs = Object.keys(result.metafile.inputs).filter((p) => p.includes('node_modules'));
console.log('bundled packages:',
  [...new Set(inputs.map((p) => p.split('node_modules/')[1].split('/')[0]))].join(', '));
