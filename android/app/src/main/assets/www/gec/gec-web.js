/* On-device grammatical correction with Unbabel/gec-t5_small.
 *
 * The checkpoint is a T5-small fine-tuned on learner errors, exported to ONNX
 * and quantised to int8 (encoder 34 MB, decoder 56 MB). It runs here, in the
 * page, with WebAssembly - no server, no network, which is why the same file
 * works in the desktop chat and inside the Android WebView.
 *
 * Two pieces had to be written because the model is not a browser format:
 *   - the T5 tokeniser (SentencePiece unigram), rebuilt from tokenizer.json:
 *     metaspace pre-tokenisation, Viterbi segmentation over 32,100 pieces;
 *   - a greedy decoder loop over the encoder and decoder graphs.
 *
 * The loop feeds the whole decoder sequence back on every step instead of
 * carrying a key/value cache. That costs a little time and saves 56 MB of a
 * second decoder graph, which is the right trade for a phone.
 *
 * Greedy rather than the model card's five beams: five beams is five forward
 * passes per token, and on a phone that turns a correction into a wait.
 */
(() => {
  const DIR = 'gec/';
  const MAX_NEW = 48;
  const EOS = 1;
  const PAD = 0;
  const UNK = 2;

  let booting = null;

  /* ---------------------------------------------------------------- tokeniser */
  function makeTokenizer(json) {
    const pieces = json.model.vocab;              // [[piece, score], ...]
    const idOf = new Map(pieces.map(([p], i) => [p, i]));
    const floor = Math.min(...pieces.map(([, s]) => s));
    const unkScore = floor - 10;

    function encode(text) {
      // T5's normaliser is a SentencePiece "precompiled" map. NFKC is what it
      // approximates for the Latin text this model is used on, and the parity
      // check in tools/check_gec_js.py compares the ids it produces with the
      // ids Python produces for the same sentence.
      const clean = text.normalize('NFKC').replace(/\s+/g, ' ').trim();
      const words = clean.split(' ').filter(Boolean);
      const s = '\u2581' + words.join('\u2581');
      const n = s.length;
      const best = new Float64Array(n + 1).fill(-Infinity);
      const back = new Int32Array(n + 1).fill(-1);
      best[0] = 0;
      for (let i = 1; i <= n; i++) {
        for (let j = Math.max(0, i - 24); j < i; j++) {
          if (best[j] === -Infinity) continue;
          const piece = s.slice(j, i);
          const id = idOf.get(piece);
          let score;
          if (id === undefined) score = i - j === 1 ? unkScore : -Infinity;
          else score = pieces[id][1];
          if (score === -Infinity) continue;
          if (best[j] + score > best[i]) { best[i] = best[j] + score; back[i] = j; }
        }
      }
      const ids = [];
      for (let i = n; i > 0;) {
        const j = back[i];
        if (j < 0) { ids.push(UNK); break; }
        const id = idOf.get(s.slice(j, i));
        ids.push(id === undefined ? UNK : id);
        i = j;
      }
      ids.reverse();
      ids.push(EOS);                               // T5 closes its input with </s>
      return ids;
    }

    function decode(ids) {
      return ids
        .filter((i) => i !== PAD && i !== EOS && i !== UNK && i < 32000)
        .map((i) => pieces[i][0]).join('')
        .replace(/\u2581/g, ' ')
        .trim();
    }

    return {encode, decode};
  }

  /* ------------------------------------------------------------------ runtime */
  async function boot() {
    if (typeof ort === 'undefined') throw new Error('onnxruntime-web is not loaded');
    ort.env.wasm.wasmPaths = DIR;
    ort.env.wasm.numThreads = 1;                   // no cross-origin isolation here
    ort.env.logLevel = 'error';
    const open = (file) => ort.InferenceSession.create(DIR + file, {
      executionProviders: ['wasm'], graphOptimizationLevel: 'all',
    });
    const [encoder, decoder, tokenizerJson, fixesJson] = await Promise.all([
      open('encoder_model.onnx'),
      open('decoder_model.onnx'),
      fetch(DIR + 'tokenizer.json').then((r) => r.json()),
      fetch(DIR + 'gec_fixes.json').then((r) => r.json()).catch(() => ({rules: []})),
    ]);
    return {encoder, decoder, tok: makeTokenizer(tokenizerJson), fixes: fixesJson.rules};
  }

  /* The rule pass gec_fixes.json carries: applied to the sentence before the
     model sees it and to its answer, exactly as tools/gec.py does. */
  function applyFixes(text, rules) {
    let out = text;
    for (const rule of rules || []) {
      if (!rule || !rule.pattern) continue;
      try {
        // gec_fixes.json is written for Python, where a group is \1; in
        // JavaScript that is a literal "1", so the references are translated
        // before the rule runs. (It shipped for an hour as "She 1 eaten".)
        const replacement = String(rule.replace || '').replace(/\\(\d)/g, '$$$1');
        out = out.replace(new RegExp(rule.pattern, rule.flags || ''), replacement);
      } catch (e) { /* a rule that does not compile must not take the page */ }
    }
    if (text[0] && text[0] === text[0].toUpperCase() && out[0] === out[0].toLowerCase()) {
      out = out[0].toUpperCase() + out.slice(1);
    }
    return out;
  }

  const ready = () => (booting ||= boot());

  async function correct(sentence) {
    const text = (sentence || '').replace(/\s+/g, ' ').trim();
    if (!text) return {input: '', output: '', changed: false, seconds: 0,
                       refused: 'Nothing to correct — the sentence is empty.'};
    if (!/[A-Za-z]/.test(text)) {
      return {input: text, output: '', changed: false, seconds: 0,
              refused: 'The model corrects English only. / این مدل فقط انگلیسی را اصلاح می‌کند.'};
    }
    const started = performance.now();
    const {encoder, decoder, tok, fixes} = await ready();
    const cleaned = applyFixes(text, fixes);
    const ids = tok.encode('gec: ' + cleaned);
    const n = ids.length;
    const inputIds = new ort.Tensor('int64', BigInt64Array.from(ids.map(BigInt)), [1, n]);
    const mask = new ort.Tensor('int64', BigInt64Array.from(ids.map(() => 1n)), [1, n]);
    const hidden = (await encoder.run({input_ids: inputIds, attention_mask: mask}))[
      encoder.outputNames[0]];

    const out = [PAD];                             // T5 starts decoding on <pad>
    for (let step = 0; step < MAX_NEW; step++) {
      const stepIds = new ort.Tensor('int64',
        BigInt64Array.from(out.map(BigInt)), [1, out.length]);
      const result = await decoder.run({
        encoder_hidden_states: hidden,
        encoder_attention_mask: mask,
        input_ids: stepIds,
      });
      const logits = result.logits;
      const vocab = logits.dims[2];
      const base = (out.length - 1) * vocab;
      let bestId = EOS, bestVal = -Infinity;
      for (let v = 0; v < vocab; v++) {
        const val = logits.data[base + v];
        if (val > bestVal) { bestVal = val; bestId = v; }
      }
      out.push(bestId);
      if (bestId === EOS) break;
    }

    const output = applyFixes(tok.decode(out.slice(1)), fixes);
    const norm = (s) => s.replace(/[.!?]+\s*$/, '').toLowerCase();
    return {
      input: text, output,
      changed: !!output && norm(output) !== norm(text),
      seconds: Math.round((performance.now() - started)) / 1000,
      refused: null,
    };
  }

  window.GECWeb = {correct, ready, version: 'gec-t5_small-int8'};
})();
