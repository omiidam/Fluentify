/* Fluentify offline English grammar analyser.
 *
 * Part-of-speech tags and lemmas come from winkNLP + wink-eng-lite-web-model,
 * running entirely on the device. Everything above that — sentence type,
 * tense/aspect/voice patterns, non-finite forms, conditionals, and the rough
 * subject/object roles — is a rule in this file, computed from those tags. The
 * two are kept apart on purpose:
 *
 *   tokens[].pos, tokens[].lemma          model predictions
 *   structures[].basis: 'model' | 'pattern'
 *   tokens[].roleStatus: 'inferred' | 'unknown'
 *
 * winkNLP has **no dependency parser**, so no nsubj/dobj/ROOT labels are ever
 * produced here. A role is only reported when a short, checkable pattern
 * supports it, and it is always marked "inferred" — an NP before the first
 * finite verb is *probably* the subject, not certainly one. Where a pattern
 * cannot decide (a contraction that could be "had" or "would", an -ing word
 * that could be a noun), the doubt is written into limitations[] instead of
 * being hidden behind a confident-looking label.
 *
 * This file is bundled with both libraries into fluentify-nlp.js and loaded
 * lazily by the page; see nlp/README.md.
 */

'use strict';

var nlpFactory = require('wink-nlp');
var model = require('wink-eng-lite-web-model');

var ENGINE = 'wink-nlp 2.4.0 + wink-eng-lite-web-model 1.8.1';
var MAX_TOKENS = 40;          // one sentence, not a paragraph
var MAX_CHARS = 400;

/* Part of speech: the tag, the English name a learner reads, the Persian
   grammatical term, and what the category actually does. The Persian is the
   term a Persian speaker learns in school — دترمینر is not a word, حرف تعیین
   is — so these are context-sensitive labels, not transliterations. */
var POS_INFO = {
  NOUN:  {en: 'Noun', fa: 'اسم', note: 'names a person, place, thing or idea'},
  PROPN: {en: 'Proper noun', fa: 'اسم خاص', note: 'a name — a person, place or brand'},
  PRON:  {en: 'Pronoun', fa: 'ضمیر', note: 'stands in for a noun'},
  VERB:  {en: 'Verb', fa: 'فعل', note: 'the action or state'},
  AUX:   {en: 'Auxiliary verb', fa: 'فعل کمکی', note: 'carries tense, aspect, voice or mood'},
  ADJ:   {en: 'Adjective', fa: 'صفت', note: 'describes a noun'},
  ADV:   {en: 'Adverb', fa: 'قید', note: 'says how, when or where'},
  DET:   {en: 'Determiner', fa: 'حرف تعیین', note: 'introduces a noun: a, the, this, my, some'},
  ADP:   {en: 'Adposition', fa: 'حرف اضافه', note: 'links a noun to the rest: in, on, by, for'},
  CCONJ: {en: 'Coordinating conjunction', fa: 'حرف ربط هم‌پایه', note: 'joins equals: and, but, or'},
  SCONJ: {en: 'Subordinating conjunction', fa: 'حرف ربط وابسته', note: 'opens a dependent clause: if, because, that'},
  PART:  {en: 'Particle', fa: 'جزء', note: 'a function word: to, not, ’s'},
  NUM:   {en: 'Numeral', fa: 'عدد', note: 'a number'},
  INTJ:  {en: 'Interjection', fa: 'شبه‌جمله', note: 'an exclamation: oh, wow'},
  PUNCT: {en: 'Punctuation', fa: 'نشانه‌گذاری', note: 'marks the structure of the sentence'},
  SYM:   {en: 'Symbol', fa: 'نماد', note: 'a sign rather than a word'},
  X:     {en: 'Other', fa: 'نامشخص', note: 'the tagger could not classify this word'},
};

var MODALS = ['can', 'could', 'may', 'might', 'must', 'shall', 'should', 'will', 'would'];
var BE = ['be', 'am', 'is', 'are', 'was', 'were', 'been', 'being'];
var HAVE = ['have', 'has', 'had', 'having'];
var WH = ['what', 'who', 'whom', 'whose', 'which', 'when', 'where', 'why', 'how'];
var GERUND_VERBS = ['enjoy', 'finish', 'avoid', 'mind', 'suggest', 'keep', 'stop',
                    'dislike', 'practise', 'practice', 'consider', 'imagine', 'risk'];
var INFINITIVE_VERBS = ['want', 'need', 'decide', 'hope', 'plan', 'promise',
                        'agree', 'refuse', 'expect', 'learn', 'manage', 'offer'];
var NEG_WORDS = ['not', 'n’t', "n't", 'never', 'no', 'none', 'nobody', 'nothing'];

/* A verb whose past form is spelled like its base form: "I read a book
   yesterday" cannot be settled from the spelling, so the tense is reported as
   present and the ambiguity is named in the limitations. */
var PAST_BASE_SAME = ['read', 'put', 'cut', 'hit', 'let', 'set', 'cost', 'shut',
                      'spread', 'quit', 'bet', 'burst', 'hurt'];

/* he reads / he goes / he studies — the third-person -s is not always a bare
   "s" on the lemma, so the shape is checked rather than assumed. */
function isThirdPerson(form, lemma) {
  if (!lemma) return false;
  if (form === lemma + 's' || form === lemma + 'es') return true;
  if (lemma.slice(-1) === 'y' && form === lemma.slice(0, -1) + 'ies') return true;
  return false;
}


var PRONOUN_KINDS = {
  personal: ['i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'],
  possessive: ['my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs'],
  reflexive: ['myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves', 'themselves'],
  demonstrative: ['this', 'that', 'these', 'those'],
  relative: ['who', 'whom', 'whose', 'which', 'that'],
  interrogative: ['who', 'whom', 'whose', 'which', 'what'],
};

/* ---------------------------------------------------------------- helpers */

function posInfo(tag) {
  return POS_INFO[tag] || POS_INFO.X;
}

function isWord(tag) {
  return tag !== 'PUNCT' && tag !== 'SYM' && tag !== 'X';
}

function has(tokens, i) {
  return i >= 0 && i < tokens.length ? tokens[i] : null;
}

function finiteish(token) {
  return !!token && (token.pos === 'VERB' || token.pos === 'AUX');
}

/* The sentence's own text is the source of truth for offsets: each token is
   placed by its own leading spaces, then checked against the slice it was
   taken from. A mismatch (a ligature, a stray combining mark) falls back to a
   forward search, and failing that the span is reported as unknown rather than
   invented. */
function placeTokens(nlp, doc, sentence) {
  var tokens = [];
  var cursor = 0;
  var its = nlp.its;
  doc.tokens().each(function (tk) {
    var text = tk.out();
    var tag = tk.out(its.pos);
    var lemma = tk.out(its.lemma);
    var spaces = tk.out(its.precedingSpaces);
    spaces = typeof spaces === 'number' ? spaces : (spaces ? String(spaces).length : 0);
    var start = Math.min(sentence.length, cursor + spaces);
    if (sentence.slice(start, start + text.length) !== text) {
      var found = sentence.indexOf(text, cursor);
      start = found === -1 ? start : found;
    }
    var end = start + text.length;
    cursor = end;
    tokens.push({
      text: text,
      start: start,
      end: end,
      pos: tag,
      lemma: typeof lemma === 'string' ? lemma : text.toLowerCase(),
      negation: tk.out(its.negationFlag) === true,
      contraction: tk.out(its.contractionFlag) === true,
    });
  });
  return tokens;
}

/* A run of tokens that can act as a noun phrase: an optional determiner, any
   adjectives, then a noun/pronoun/numeral. Deliberately shallow — this is a
   phrase *guess* used only to label a role as "inferred". */
function nounPhraseAt(tokens, i, stop) {
  var j = i;
  var seenHead = false;
  var start = i;
  while (j < tokens.length && j < stop) {
    var tag = tokens[j].pos;
    if (tag === 'DET' || tag === 'ADJ' || tag === 'NUM') { j += 1; continue; }
    if (tag === 'NOUN' || tag === 'PROPN' || tag === 'PRON') {
      seenHead = true; j += 1;
      // a noun may be modified by a following noun ("train ticket")
      while (j < tokens.length && j < stop && tokens[j].pos === 'NOUN') j += 1;
      break;
    }
    break;
  }
  if (!seenHead) return null;
  return {start: start, end: j, indices: range(start, j)};
}

function range(start, end) {
  var out = [];
  for (var i = start; i < end; i += 1) out.push(i);
  return out;
}

function indicesOf(tokens, predicate) {
  var out = [];
  for (var i = 0; i < tokens.length; i += 1) if (predicate(tokens[i], i)) out.push(i);
  return out;
}

function textOf(tokens, indices) {
  return indices.map(function (i) { return tokens[i].text; }).join(' ');
}

function lower(token) {
  return token.text.toLowerCase();
}

/* ------------------------------------------------------------------ rules */

/* Each rule returns either null or a structure. `basis` says where the claim
   comes from: 'model' when the tagger's own tags decide it, 'pattern' when a
   hand-written sequence does. */
function sentenceShape(tokens) {
  var words = indicesOf(tokens, function (t) { return isWord(t.pos); });
  if (!words.length) return [];
  var first = tokens[words[0]];
  var last = tokens[tokens.length - 1];
  var qMark = last && last.pos === 'PUNCT' && last.text === '?';
  var bang = last && last.pos === 'PUNCT' && last.text === '!';
  var out = [];

  var whStart = first.pos === 'PRON' || first.pos === 'ADV' || first.pos === 'DET'
    ? WH.indexOf(lower(first)) !== -1 : WH.indexOf(lower(first)) !== -1;
  var auxStart = first.pos === 'AUX';

  if (qMark) {
    out.push({
      id: whStart ? 'wh_question' : 'yes_no_question',
      label_en: whStart ? 'Wh- question' : 'Yes / No question',
      label_fa: whStart ? 'سؤال با کلمهٔ پرسشی' : 'سؤال بله/خیر',
      evidence: [words[0]],
      basis: 'pattern',
      note_en: whStart
        ? 'The sentence opens with a question word and the auxiliary comes before the subject.'
        : 'The auxiliary comes before the subject and the question expects yes or no.',
      note_fa: whStart
        ? 'جمله با کلمهٔ پرسشی شروع می‌شود و فعل کمکی پیش از فاعل می‌آید.'
        : 'فعل کمکی پیش از فاعل آمده و پاسخ، بله یا خیر است.',
    });
  } else if (bang) {
    out.push({
      id: 'exclamative', label_en: 'Exclamative', label_fa: 'جملهٔ تعجبی',
      evidence: [tokens.length - 1], basis: 'model',
      note_en: 'An exclamation rather than a statement.',
      note_fa: 'به‌جای خبر، تعجب را بیان می‌کند.',
    });
  }

  // imperative: a base-form verb first, no subject, no auxiliary in front
  var imperative = !qMark && first.pos === 'VERB' && !auxStart &&
    indicesOf(tokens, function (t) { return t.pos === 'PRON'; }).length === 0 &&
    (lower(first) === first.lemma);
  if (imperative) {
    out.push({
      id: 'imperative', label_en: 'Imperative', label_fa: 'جملهٔ امری',
      evidence: [words[0]], basis: 'pattern',
      note_en: 'A bare verb opens the sentence and the subject is understood as "you".',
      note_fa: 'فعل بدون فاعل در آغاز جمله آمده و فاعل «تو» در نظر گرفته می‌شود.',
    });
  } else if (!qMark && !imperative && !bang) {
    out.push({
      id: 'declarative', label_en: 'Declarative', label_fa: 'جملهٔ خبری',
      evidence: [], basis: 'pattern',
      note_en: 'A statement: subject first, then the verb.',
      note_fa: 'جملهٔ خبری: نخست فاعل، سپس فعل.',
    });
  }
  return out;
}

/* Tense, aspect and voice from the auxiliary + verb sequence. This is the part
   a learner actually wants, and it is reliable *because* it keys on tags the
   model already assigned rather than on the meaning of the sentence. */
function verbPhrases(tokens) {
  var out = [];
  var i = 0;
  while (i < tokens.length) {
    var t = tokens[i];
    if (!finiteish(t)) { i += 1; continue; }
    // A bare verb that follows "to" or another verb is a complement, not a
    // tense: "he decided to stay" is past simple, and "stay" is an infinitive
    // (named as such by nonFinite), not a present-tense claim.
    var before = tokens[i - 1];
    if (before && (before.pos === 'VERB' ||
        (before.pos === 'PART' && lower(before) === 'to'))) { i += 1; continue; }
    var seq = [];
    var j = i;
    var stepped = 0;
    while (j < tokens.length) {
      var cur = tokens[j];
      if (cur.pos === 'AUX' || cur.pos === 'VERB') {
        // A second verb is a complement, not part of this group: "enjoy
        // reading" is a present verb plus a gerund, and each gets its own
        // entry rather than one wrong four-word tense.
        var haveVerb = false;
        for (var s = 0; s < seq.length; s += 1) if (seq[s].pos === 'VERB') haveVerb = true;
        if (cur.pos === 'VERB' && haveVerb) break;
        seq.push(cur); j += 1; continue;
      }
      if (cur.pos === 'ADV' || (cur.pos === 'PART' && lower(cur) === 'not')) { j += 1; continue; }
      // A question inverts subject and auxiliary ("Can you help me?"), so the
      // subject sits between the auxiliary and its verb. One word — the
      // subject — is stepped over, and only when a verb form really follows it
      // (adverbs may sit in between). A conjunction is never stepped over, so
      // "he is running and she is swimming" stays two groups.
      var onlyAux = seq.length > 0 && !haveVerb;
      if (onlyAux && isWord(cur.pos) && cur.pos !== 'CCONJ' && stepped < 1) {
        var k = j + 1;
        while (k < tokens.length && tokens[k].pos === 'ADV') k += 1;
        var nxt = tokens[k];
        if (nxt && (nxt.pos === 'AUX' || nxt.pos === 'VERB')) { j += 1; stepped += 1; continue; }
      }
      break;
    }
    if (!seq.length) { i += 1; continue; }
    out.push({start: i, end: j, tokens: seq});
    i = Math.max(j, i + 1);
  }
  return out;
}

function aspectFrom(group) {
  var texts = group.tokens.map(function (t) { return t.text.toLowerCase(); });
  var lemmas = group.tokens.map(function (t) { return t.lemma; });
  var tags = group.tokens.map(function (t) { return t.pos; });
  var lastIdx = group.tokens.length - 1;
  var lastForm = texts[lastIdx];
  var lastTag = tags[lastIdx];
  var lastLemma = lemmas[lastIdx] || lastForm;
  var auxes = 0;
  for (var a = 0; a < tags.length; a += 1) if (tags[a] === 'AUX') auxes += 1;

  /* Every form below is read off the surface spelling against the model's
     lemma. Nothing here guesses a tense from what the sentence means, which
     is why a bare "-ed" verb with no auxiliary is called past simple and the
     same verb after "have" is called a past participle. */
  var ing = lastTag === 'VERB' && lastForm.length > 4 && lastForm.slice(-3) === 'ing';
  var inflected = lastTag === 'VERB' && !ing && lastForm !== lastLemma;
  // "been" and "had" are past participles of be and have in their own right,
  // and a group can end on one: "I have been to London", "I had been there".
  var participleLike = inflected ||
    (lastTag === 'AUX' && (lastForm === 'been' || lastForm === 'had'));
  var third = lastTag === 'VERB' && isThirdPerson(lastForm, lastLemma);

  var isBe = lemmas.indexOf('be') !== -1;
  var isWill = texts.indexOf('will') !== -1 || texts.indexOf("'ll") !== -1;
  var had = texts.indexOf('had') !== -1 || texts.indexOf("'d") !== -1;
  var been = texts.indexOf('been') !== -1;
  // "she's been working" can only be "she has been working": "is been" is not
  // English, so the 's contraction is resolved here rather than guessed at.
  var isHave = lemmas.indexOf('have') !== -1 ||
    (been && (texts.indexOf("'s") !== -1 || texts.indexOf("'ve") !== -1));
  var wasWere = texts.indexOf('was') !== -1 || texts.indexOf('were') !== -1;
  var did = texts.indexOf('did') !== -1;
  var doing = texts.indexOf('do') !== -1 || texts.indexOf('does') !== -1;
  // "will" and "shall" are the future markers here, not modals: they have their
  // own branches, and counting them as modals would label "will have finished"
  // as a modal perfect instead of the future perfect it is.
  var modal = MODALS.filter(function (m) {
    return m !== 'will' && m !== 'shall' && lemmas.indexOf(m) !== -1;
  });
  var found = [];

  function add(id, en, fa, note_en, note_fa, extra) {
    found.push(Object.assign({
      id: id, label_en: en, label_fa: fa, basis: 'pattern',
      evidence: range(group.start, group.end),
      note_en: note_en, note_fa: note_fa,
    }, extra || {}));
  }

  // Most specific construction first: at most one tense / aspect claim is made
  // for a verb group, so a sentence never gets two contradictory tenses.
  if (modal.length && isHave && inflected) {
    add('modal_perfect', 'Modal + have + past participle', 'فعل وجهی + have + قسمت سوم فعل',
      'A modal with "have" and a past participle: ability, certainty or regret about something earlier.',
      'فعل وجهی با «have» و قسمت سوم فعل: توانایی، قطعیت یا پشیمانی دربارهٔ چیزی پیش‌تر.');
  } else if (isWill && texts.indexOf('have') !== -1 && participleLike && !ing) {
    add('future_perfect', 'Future Perfect', 'آیندهٔ کامل',
      'will have + past participle: finished before a point in the future.',
      'will have + قسمت سوم فعل: تا نقطه‌ای در آینده تمام می‌شود.');
  } else if (isHave && been && ing) {
    if (isWill) {
      add('future_perfect_continuous', 'Future Perfect Continuous', 'آیندهٔ کامل استمراری',
        'will have been + -ing: still in progress up to a future moment.',
        'will have been + فعل ing‌دار: تا لحظه‌ای در آینده همچنان ادامه دارد.');
    } else if (had) {
      add('past_perfect_continuous', 'Past Perfect Continuous', 'گذشتهٔ کامل استمراری',
        'had been + -ing: an action was in progress up to a point in the past.',
        'had been + فعل ing‌دار: کاری پیش از نقطه‌ای در گذشته در جریان بود.');
    } else {
      add('present_perfect_continuous', 'Present Perfect Continuous', 'حال کامل استمراری',
        'has/have been + -ing: the action started earlier and is still in progress.',
        'has/have been + فعل ing‌دار: کار پیش‌تر شروع شده و هنوز ادامه دارد.');
    }
  } else if (had && participleLike) {
    add('past_perfect', 'Past Perfect', 'گذشتهٔ کامل',
      'had + past participle: the earlier of two past actions.',
      'had + قسمت سوم فعل: کارِ پیش‌تر در میان دو کار گذشته.');
  } else if (isHave && participleLike) {
    add('present_perfect', 'Present Perfect', 'حال کامل',
      'has/have + past participle: a past action with a present result.',
      'has/have + قسمت سوم فعل: کاری گذشته با نتیجه‌ای در حال.');
  } else if (isWill && isBe && ing) {
    add('future_continuous', 'Future Continuous', 'آیندهٔ استمراری',
      'will be + -ing: in progress at a future moment.',
      'will be + فعل ing‌دار: در لحظه‌ای در آینده در جریان است.');
  } else if (isWill) {
    add('future_simple', 'Future Simple', 'آیندهٔ ساده',
      'will + base verb: a prediction, promise or decision.',
      'will + فعل ساده: پیش‌بینی، قول یا تصمیم.');
  } else if (isBe && ing) {
    add(wasWere ? 'past_continuous' : 'present_continuous',
      wasWere ? 'Past Continuous' : 'Present Continuous',
      wasWere ? 'گذشتهٔ استمراری' : 'حال استمراری',
      (wasWere ? 'was/were' : 'am/is/are') + ' + -ing: happening ' +
        (wasWere ? 'at a past moment.' : 'now or around now.'),
      (wasWere ? 'was/were' : 'am/is/are') + ' + فعل ing‌دار: ' +
        (wasWere ? 'در لحظه‌ای در گذشته.' : 'همین حالا یا این روزها.'));
  } else if (isBe && inflected) {
    add('passive_voice', 'Passive voice', 'مجهول',
      'be + past participle: the subject receives the action instead of doing it.',
      'be + قسمت سوم فعل: فاعل پذیرندهٔ کار است، نه انجام‌دهندهٔ آن.');
  } else if (modal.length) {
    add('modal_verb', 'Modal verb', 'فعل وجهی',
      'A modal (' + modal.join(', ') + ') with a base verb: ability, permission, obligation or possibility.',
      'فعل وجهی (' + modal.join('، ') + ') با فعل ساده: توانایی، اجازه، اجبار یا احتمال.');
  } else if (did) {
    add('past_simple', 'Past Simple', 'گذشتهٔ ساده',
      'did + base verb: a finished action in the past, in a negative sentence or a question.',
      'did + فعل ساده: کار تمام‌شده در گذشته، در جملهٔ منفی یا پرسشی.');
  } else if (doing) {
    add('simple_present', 'Simple Present', 'حال ساده',
      'do/does + base verb: a fact, habit or routine in the present.',
      'do/does + فعل ساده: واقعیت، عادت یا کار روزمره در زمان حال.');
  } else if (!auxes && lastTag === 'VERB' && !ing) {
    if (third) {
      add('simple_present', 'Simple Present', 'حال ساده',
        'A present fact, habit or routine.',
        'واقعیت، عادت یا کار روزمره در زمان حال.');
      add('third_person_s', 'Third-person -s', 'علامت سوم‌شخص مفرد',
        'he / she / it takes an -s on the present verb.',
        'با he / she / it در زمان حال به فعل s- اضافه می‌شود.');
    } else if (inflected) {
      add('past_simple', 'Past Simple', 'گذشتهٔ ساده',
        'The verb carries its own past form and there is no auxiliary.',
        'فعل شکل گذشتهٔ خودش را دارد و فعل کمکی ندارد.');
    } else {
      add('simple_present', 'Simple Present', 'حال ساده',
        'The base form with "I" or a plural subject: a fact, habit or routine.',
        'شکل سادهٔ فعل با «I» یا فاعل جمع: واقعیت، عادت یا کار روزمره.');
    }
  }
  return found;
}

function nonFinite(tokens) {
  var out = [];
  // to + base verb = infinitive
  for (var i = 0; i < tokens.length - 1; i += 1) {
    var t = tokens[i];
    var n = tokens[i + 1];
    if (t.pos === 'PART' && lower(t) === 'to' && n.pos === 'VERB' && lower(n) === n.lemma) {
      out.push({
        id: 'infinitive', label_en: 'Infinitive', label_fa: 'مصدر با to',
        evidence: [i, i + 1], basis: 'pattern',
        note_en: '"to" + base verb: the uninflected form used after many verbs and for purpose.',
        note_fa: '"to" + فعل ساده: صورتی که پس از بسیاری فعل‌ها و برای بیان هدف می‌آید.',
      });
    }
  }
  // verb + -ing after a verb that takes a gerund
  for (var k = 0; k < tokens.length; k += 1) {
    var cur = tokens[k];
    if (cur.pos !== 'VERB' && cur.pos !== 'NOUN') continue;
    if (cur.text.slice(-3) !== 'ing') continue;
    var prev = tokens[k - 1];
    var prevVerb = prev && prev.pos === 'VERB' ? prev : null;
    if (prevVerb && GERUND_VERBS.indexOf(prevVerb.lemma) !== -1) {
      out.push({
        id: 'gerund', label_en: 'Gerund (-ing form)', label_fa: 'اسم مصدر (فعل + ing)',
        evidence: [k - 1, k], basis: 'pattern',
        note_en: '"' + prevVerb.text + '" takes an -ing form here, so "' + cur.text +
          '" works as a noun, not as a tense.',
        note_fa: '«' + prevVerb.text + '» در این ساختار فعل ing‌دار می‌گیرد، پس «' + cur.text +
          '» نقش اسم دارد نه زمان.',
      });
      break;
    }
  }
  // past participle standing alone (no auxiliary anywhere)
  var anyAux = indicesOf(tokens, function (t) { return t.pos === 'AUX'; }).length > 0;
  if (!anyAux) {
    var part = indicesOf(tokens, function (t) {
      return t.pos === 'VERB' && t.text.slice(-2) === 'en' && t.text !== t.lemma;
    });
    if (part.length) {
      out.push({
        id: 'past_participle', label_en: 'Past participle', label_fa: 'قسمت سوم فعل',
        evidence: part, basis: 'model',
        note_en: 'The -ed / -en form used without an auxiliary.',
        note_fa: 'شکل -ed / -en که بدون فعل کمکی آمده است.',
      });
    }
  }
  return out;
}

function conditionals(tokens) {
  var ifAt = indicesOf(tokens, function (t) {
    return t.pos === 'SCONJ' && (lower(t) === 'if' || lower(t) === 'unless');
  });
  if (!ifAt.length) return [];
  var after = tokens.slice(ifAt[0] + 1);
  var hasWill = indicesOf(after, function (t) { return t.lemma === 'will'; }).length > 0;
  var hasWould = indicesOf(after, function (t) { return t.lemma === 'would'; }).length > 0;
  var hasHad = indicesOf(after, function (t) { return t.lemma === 'have' && t.text === 'had'; }).length > 0;
  var hasWouldHave = hasWould && indicesOf(after, function (t) { return t.lemma === 'have'; }).length > 0;
  var pastInIf = indicesOf(after, function (t) {
    return t.pos === 'VERB' && t.text !== t.lemma && t.text.slice(-3) !== 'ing' &&
      t.text.slice(-2) !== 'en';
  }).length > 0;

  if (hasHad && hasWouldHave) {
    return [{
      id: 'third_conditional', label_en: 'Third conditional', label_fa: 'شرطی نوع سوم',
      evidence: [ifAt[0]], basis: 'pattern',
      note_en: 'if + had + past participle, … would have + past participle: an imagined past that did not happen.',
      note_fa: 'if + had + قسمت سوم فعل، … would have + قسمت سوم فعل: گذشتهٔ خیالی که رخ نداده است.',
    }];
  }
  if (hasWould) {
    return [{
      id: 'second_conditional', label_en: 'Second conditional', label_fa: 'شرطی نوع دوم',
      evidence: [ifAt[0]], basis: 'pattern',
      note_en: 'if + past simple, … would + base verb: an unlikely or imaginary present.',
      note_fa: 'if + گذشتهٔ ساده، … would + فعل ساده: وضعیت بعید یا خیالی در زمان حال.',
    }];
  }
  if (hasWill) {
    return [{
      id: 'first_conditional', label_en: 'First conditional', label_fa: 'شرطی نوع اول',
      evidence: [ifAt[0]], basis: 'pattern',
      note_en: 'if + present simple, … will + base verb: a real possibility in the future.',
      note_fa: 'if + حال ساده، … will + فعل ساده: احتمال واقعی در آینده.',
    }];
  }
  if (pastInIf) {
    return [{
      id: 'second_conditional', label_en: 'Second conditional', label_fa: 'شرطی نوع دوم',
      evidence: [ifAt[0]], basis: 'pattern',
      note_en: 'A past form inside the if-clause usually signals an imaginary condition.',
      note_fa: 'شکل گذشته در جملهٔ شرطی معمولاً شرط خیالی را نشان می‌دهد.',
    }];
  }
  return [{
    id: 'zero_conditional', label_en: 'Zero / open conditional', label_fa: 'شرطی صفر (عمومی)',
    evidence: [ifAt[0]], basis: 'pattern',
    note_en: 'if + present simple, … present simple: something generally true.',
    note_fa: 'if + حال ساده، … حال ساده: چیزی که به‌طور کلی درست است.',
  }];
}

function wordClassNotes(tokens) {
  var out = [];
  var arts = indicesOf(tokens, function (t) {
    return t.pos === 'DET' && ['a', 'an', 'the'].indexOf(lower(t)) !== -1;
  });
  if (arts.length) {
    out.push({
      id: 'articles', label_en: 'Articles', label_fa: 'حروف تعریف',
      evidence: arts, basis: 'model',
      note_en: 'a / an for one unspecified thing, the for something already known.',
      note_fa: 'a / an برای چیزی نامشخص و the برای چیزی شناخته‌شده.',
    });
  }
  var preps = indicesOf(tokens, function (t) { return t.pos === 'ADP'; });
  if (preps.length) {
    out.push({
      id: 'prepositional_phrase', label_en: 'Prepositional phrase', label_fa: 'گروه حرف اضافه',
      evidence: preps, basis: 'model',
      note_en: 'A preposition plus its noun: it adds place, time, reason or agent.',
      note_fa: 'حرف اضافه با اسم پس از آن: مکان، زمان، دلیل یا کنندهٔ کار را می‌افزاید.',
    });
  }
  var prons = indicesOf(tokens, function (t) { return t.pos === 'PRON'; });
  if (prons.length) {
    var kinds = [];
    prons.forEach(function (i) {
      var w = lower(tokens[i]);
      Object.keys(PRONOUN_KINDS).forEach(function (kind) {
        if (PRONOUN_KINDS[kind].indexOf(w) !== -1 && kinds.indexOf(kind) === -1) kinds.push(kind);
      });
    });
    var fa = {personal: 'شخصی', possessive: 'ملکی', reflexive: 'انعکاسی',
              demonstrative: 'اشاره‌ای', relative: 'موصولی', interrogative: 'پرسشی'};
    out.push({
      id: 'pronouns', label_en: 'Pronouns', label_fa: 'ضمیرها',
      evidence: prons, basis: 'model',
      note_en: 'Pronoun type here: ' + (kinds.length ? kinds.join(', ') : 'personal') + '.',
      note_fa: 'نوع ضمیر در این جمله: ' +
        (kinds.length ? kinds.map(function (k) { return fa[k]; }).join('، ') : 'شخصی') + '.',
    });
  }
  var adjs = indicesOf(tokens, function (t) { return t.pos === 'ADJ'; });
  if (adjs.length) {
    var comparative = indicesOf(tokens, function (t) {
      return (t.pos === 'ADJ' || t.pos === 'ADV') &&
        (/(er|est)$/.test(lower(t)) && lower(t).length > 3 ||
         ['more', 'most', 'less', 'least'].indexOf(lower(t)) !== -1);
    });
    out.push({
      id: 'adjectives', label_en: 'Adjectives', label_fa: 'صفت‌ها',
      evidence: adjs, basis: 'model',
      note_en: 'They describe the noun they sit next to.',
      note_fa: 'اسم کنار خود را توصیف می‌کنند.',
    });
    if (comparative.length) {
      out.push({
        id: 'comparison', label_en: 'Comparison', label_fa: 'مقایسه',
        evidence: comparative, basis: 'model',
        note_en: '-er / -est or more / most forms a comparison.',
        note_fa: 'شکل -er / -est یا more / most مقایسه می‌سازد.',
      });
    }
  }
  var advs = indicesOf(tokens, function (t) { return t.pos === 'ADV'; });
  if (advs.length) {
    out.push({
      id: 'adverbs', label_en: 'Adverbs', label_fa: 'قیدها',
      evidence: advs, basis: 'model',
      note_en: 'They say how, when, how often or how much.',
      note_fa: 'چگونگی، زمان، تکرار یا میزان را می‌گویند.',
    });
  }
  var conjs = indicesOf(tokens, function (t) {
    return t.pos === 'CCONJ' || t.pos === 'SCONJ';
  });
  if (conjs.length) {
    out.push({
      id: 'conjunction', label_en: 'Conjunction', label_fa: 'حرف ربط',
      evidence: conjs, basis: 'model',
      note_en: 'It joins two words, phrases or clauses.',
      note_fa: 'دو واژه، گروه یا جمله را به هم پیوند می‌دهد.',
    });
  }
  var modalTokens = indicesOf(tokens, function (t) {
    return t.pos === 'AUX' && MODALS.indexOf(t.lemma) !== -1;
  });
  if (modalTokens.length) {
    out.push({
      id: 'modal_verbs', label_en: 'Modal verbs', label_fa: 'فعل‌های وجهی',
      evidence: modalTokens, basis: 'model',
      note_en: 'A modal adds ability, permission, obligation or possibility and takes no -s.',
      note_fa: 'فعل وجهی توانایی، اجازه، اجبار یا احتمال می‌افزاید و s- نمی‌گیرد.',
    });
  }
  var copular = indicesOf(tokens, function (t) { return t.pos === 'AUX' && t.lemma === 'be'; });
  if (copular.length) {
    var after = tokens[copular[0] + 1];
    if (after && (after.pos === 'ADJ' || after.pos === 'NOUN' || after.pos === 'PROPN')) {
      out.push({
        id: 'copular', label_en: 'be + complement', label_fa: 'فعل ربطی be + متمم',
        evidence: [copular[0], copular[0] + 1], basis: 'pattern',
        note_en: '"be" links the subject to an adjective or noun instead of showing an action.',
        note_fa: '«be» فاعل را به صفت یا اسم پیوند می‌دهد، نه به یک کار.',
      });
    }
  }
  // verb + infinitive (want to go, decide to leave…)
  for (var i = 0; i < tokens.length - 1; i += 1) {
    var v = tokens[i];
    if (v.pos === 'VERB' && INFINITIVE_VERBS.indexOf(v.lemma) !== -1) {
      var next = tokens[i + 1];
      if (next && next.pos === 'PART' && lower(next) === 'to') {
        out.push({
          id: 'verb_infinitive', label_en: 'verb + infinitive', label_fa: 'فعل + مصدر با to',
          evidence: [i, i + 1], basis: 'pattern',
          note_en: '"' + v.text + '" takes "to" + base verb.',
          note_fa: '«' + v.text + '» با «to» و فعل ساده می‌آید.',
        });
        break;
      }
    }
  }
  return out;
}

function negationRule(tokens) {
  var flags = indicesOf(tokens, function (t) { return t.negation === true; });
  var words = indicesOf(tokens, function (t) {
    return t.pos === 'PART' && NEG_WORDS.indexOf(lower(t)) !== -1 ||
      (t.pos === 'ADV' && NEG_WORDS.indexOf(lower(t)) !== -1);
  });
  var idx = flags.length ? flags : words;
  if (!idx.length) return [];
  return [{
    id: 'negation', label_en: 'Negation', label_fa: 'منفی‌سازی',
    evidence: idx, basis: flags.length ? 'model' : 'pattern',
    note_en: 'Not / n’t flips the meaning, and the auxiliary stays in front of the subject in questions.',
    note_fa: 'not / n’t معنی را منفی می‌کند و در سؤال، فعل کمکی پیش از فاعل می‌ماند.',
  }];
}

/* Roles: only what a short pattern can defend, and always marked inferred. */
function roles(tokens) {
  var finite = -1;
  for (var i = 0; i < tokens.length; i += 1) {
    if (tokens[i].pos === 'VERB') { finite = i; break; }
  }
  if (finite === -1) return [];

  var out = [];
  var subj = nounPhraseAt(tokens, 0, finite);
  // a leading adverb ("Yesterday I went") is not part of the subject
  if (!subj) {
    var firstWord = tokens.findIndex(function (t) { return isWord(t.pos); });
    if (firstWord !== -1 && firstWord < finite) {
      subj = nounPhraseAt(tokens, firstWord, finite);
    }
  }
  if (subj) {
    out.push({
      indices: subj.indices,
      role: 'subject',
      label_en: 'subject (inferred)',
      label_fa: 'فاعل (استنباطی)',
      note_en: 'The noun phrase before the first main verb. Inferred from word order, not from a parse.',
      note_fa: 'گروه اسمی پیش از نخستین فعل اصلی. از ترتیب واژه‌ها استنباط شده، نه از تجزیهٔ نحوی.',
    });
  }
  out.push({
    indices: [finite],
    role: 'verb',
    label_en: 'main verb (inferred)',
    label_fa: 'فعل اصلی (استنباطی)',
    note_en: 'The first verb that is not an auxiliary.',
    note_fa: 'نخستین فعلی که کمکی نیست.',
  });

  // direct object: an NP right after the verb, with no preposition between
  var obj = nounPhraseAt(tokens, finite + 1, tokens.length);
  if (obj && tokens[finite + 1] && tokens[finite + 1].pos !== 'ADP') {
    out.push({
      indices: obj.indices,
      role: 'object',
      label_en: 'object (inferred)',
      label_fa: 'مفعول (استنباطی)',
      note_en: 'The noun phrase directly after the verb. A prepositional phrase or a second verb ends it.',
      note_fa: 'گروه اسمی که بی‌واسطه پس از فعل می‌آید؛ گروه حرف اضافه یا فعل دوم آن را پایان می‌دهد.',
    });
  }
  return out;
}

/* ---------------------------------------------------------------- analyse */

function createAnalyser() {
  var nlp = nlpFactory(model);
  nlp.its.pos; // touch once so a bad model fails here, not mid-sentence

  function analyzeEnglishGrammar(input) {
    var original = typeof input === 'string' ? input : String(input == null ? '' : input);
    var trimmed = original.trim();
    var limitations = [];
    var structures = [];
    var tokens = [];
    var rolesOut = [];

    if (!trimmed) {
      return {
        originalSentence: original, language: 'en', source: 'offline',
        engine: ENGINE, tokens: [], detectedStructures: [], structureDetails: [],
        limitations: ['Empty input: there is no sentence to analyse.'],
      };
    }

    // One sentence, bounded. A pasted paragraph is cut, not silently mangled.
    var doc = nlp.readDoc(trimmed);
    var sentences = doc.sentences().out();
    var working = trimmed;
    if (sentences.length > 1) {
      working = sentences[0];
      limitations.push('There are several sentences here; only the first one was analysed.');
    }
    doc = nlp.readDoc(working);
    var count = doc.tokens().length();
    if (count > MAX_TOKENS) {
      var all = [];
      doc.tokens().each(function (tk) { all.push(tk.out()); });
      var head = all.slice(0, MAX_TOKENS);
      // keep trailing punctuation with the head so the sentence still reads
      while (head.length > 1 && /^[.?!,;:]$/.test(head[head.length - 1])) head.pop();
      working = head.join(' ').replace(/\s+([.,;:!?])/g, '$1');
      doc = nlp.readDoc(working);
      limitations.push('Longer than ' + MAX_TOKENS + ' words: only the first ' +
        MAX_TOKENS + ' were analysed.');
    }
    if (working.length > MAX_CHARS) {
      working = working.slice(0, MAX_CHARS);
      doc = nlp.readDoc(working);
      limitations.push('Longer than ' + MAX_CHARS + ' characters: it was cut at the limit.');
    }

    tokens = placeTokens(nlp, doc, working);

    var tagCounts = {};
    tokens.forEach(function (t) { tagCounts[t.pos] = (tagCounts[t.pos] || 0) + 1; });
    if (tagCounts.X) {
      limitations.push(tagCounts.X + ' word(s) could not be tagged; they are marked "Other".');
    }

    structures = structures.concat(sentenceShape(tokens));
    verbPhrases(tokens).forEach(function (group) {
      structures = structures.concat(aspectFrom(group));
    });
    structures = structures.concat(nonFinite(tokens));
    structures = structures.concat(conditionals(tokens));
    structures = structures.concat(wordClassNotes(tokens));
    structures = structures.concat(negationRule(tokens));

    // one entry per id, keeping the first evidence
    var seen = {};
    structures = structures.filter(function (s) {
      if (seen[s.id]) return false;
      seen[s.id] = true;
      return true;
    });

    rolesOut = roles(tokens);
    var roleByIndex = {};
    rolesOut.forEach(function (r) {
      r.indices.forEach(function (i) { roleByIndex[i] = r; });
    });

    tokens = tokens.map(function (t, i) {
      var info = posInfo(t.pos);
      var role = roleByIndex[i];
      var token = {
        text: t.text,
        start: t.start,
        end: t.end,
        pos: t.pos,
        posLabel: info.en,
        posLabelFa: info.fa,
        posNote: info.note,
        lemma: t.lemma && t.lemma !== t.text ? t.lemma : (t.lemma || ''),
        negation: t.negation,
        contraction: t.contraction,
        roleStatus: role ? 'inferred' : 'unknown',
      };
      if (role) {
        token.grammaticalRole = role.role;
        token.roleLabel = role.label_en;
        token.roleLabelFa = role.label_fa;
      }
      return token;
    });

    // Honest, always-on caveats. These are not warnings about a bug: they are
    // the real limits of an on-device tagger with no dependency parser.
    limitations.unshift(
      'Parts of speech and lemmas come from winkNLP on the device. It has no ' +
      'dependency parser, so no syntactic tree is claimed: subject and object ' +
      'are word-order inferences, and everything else is left unlabelled.');
    var barePast = tokens.filter(function (t) {
      return t.pos === 'VERB' && t.text === t.lemma && PAST_BASE_SAME.indexOf(t.lemma) !== -1;
    });
    if (barePast.length) {
      limitations.push('"' + barePast[0].text + '" is spelled the same in the present and the ' +
        'past, so the tense below was read as present; only the surrounding text ' +
        'can settle which one it is.');
    }
    if (tokens.some(function (t) { return t.contraction; })) {
      limitations.push('A contraction was expanded by the tagger (\u2019s, \u2019d, n\u2019t); ' +
        'one form can still have two readings (she\u2019d = she had / she would).');
    }
    var gerund = structures.filter(function (s) { return s.id === 'gerund'; })[0];
    if (gerund) {
      var gi = gerund.evidence[1];
      if (tokens[gi] && tokens[gi].pos === 'NOUN') {
        limitations.push('The tagger reads "' + tokens[gi].text +
          '" as a noun; the -ing form after "' + tokens[gerund.evidence[0]].text +
          '" is why it is also described as a gerund.');
      }
    }

    var words = tokens.filter(function (t) { return isWord(t.pos); });
    return {
      originalSentence: original,
      analysedSentence: working,
      language: 'en',
      source: 'offline',
      engine: ENGINE,
      tokenCount: words.length,
      tokens: tokens,
      detectedStructures: structures.map(function (s) { return s.id; }),
      structureDetails: structures,
      roles: rolesOut.map(function (r) {
        return {
          role: r.role,
          words: r.indices.map(function (i) { return tokens[i].text; }),
          indices: r.indices,
          status: 'inferred',
          label_en: r.label_en, label_fa: r.label_fa,
          note_en: r.note_en, note_fa: r.note_fa,
        };
      }),
      limitations: limitations,
    };
  }

  return {analyzeEnglishGrammar: analyzeEnglishGrammar};
}

module.exports = {
  createAnalyser: createAnalyser,
  ENGINE: ENGINE,
  POS_INFO: POS_INFO,
  MAX_TOKENS: MAX_TOKENS,
};
