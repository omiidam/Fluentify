/* Bundle entry for the offline grammar analyser.
 *
 * Exposes exactly one global — FluentifyNLP — with a lazy init, because the
 * model is 3.5 MB of JSON-backed JS and must not be built at page load. The
 * page injects this file on the first analysis request, then calls init() once
 * and reuses the instance; see tools/check_analyser.py for the shipped-artifact
 * tests.
 */

'use strict';

var core = require('./analyser.js');

var instance = null;
var initMs = 0;

function now() {
  if (typeof performance !== 'undefined' && performance && performance.now) {
    return performance.now();
  }
  return Date.now();
}

function init() {
  if (instance) return instance;
  var started = now();
  instance = core.createAnalyser();
  initMs = Math.round(now() - started);
  return instance;
}

function analyze(sentence) {
  return init().analyzeEnglishGrammar(sentence);
}

module.exports = {
  analyze: analyze,
  init: init,
  version: core.ENGINE,
  maxTokens: core.MAX_TOKENS,
  posInfo: core.POS_INFO,
  initMs: function () { return initMs; },
  isReady: function () { return instance !== null; },
};
