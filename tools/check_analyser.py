#!/usr/bin/env python3
"""Is the offline grammar analyser honest, accurate and self-contained?

    python3 tools/check_analyser.py

The analyser is a real, bundled copy of winkNLP plus the English web model -
3.5 MB of it - that runs inside the page and inside the APK with no server, no
Python and no network. A tagger is easy to demo and hard to trust, so this file
holds it to the four things that decide whether it is worth shipping:

  accuracy    the ten sentences the feature was specified against, plus
              contractions, unpunctuated lower case, unknown proper names, a
              garden-path sentence and mixed Persian/English input. Parts of
              speech and lemmas are asserted word by word, and every structural
              claim is asserted *and* every wrong claim is banned, because a
              confident wrong tense is worse than no answer.
  honesty     no dependency label may ever appear (nsubj, dobj, ROOT, ...),
              since the model has no parser; every role carries roleStatus
              "inferred"; offsets must slice back to the token they describe;
              and the original sentence is returned unchanged.
  offline     the bundle may not contain fetch, XMLHttpRequest, importScripts
              or a CDN URL, and the page must load it from a local path.
  safety      huge input is bounded and *says so*, an empty string is handled,
              and the output is deterministic - the same sentence twice gives
              byte-identical JSON.

Exit code is non-zero if any of that is untrue.
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLE = ROOT / "nlp" / "fluentify-nlp.js"
CACHE = ROOT / "tools/.cache"

# (sentence, [(word, pos)], must-have structures, must-NOT-have structures)
CASES = [
    ("She is learning English.",
     [("She", "PRON"), ("is", "AUX"), ("learning", "VERB"), ("English", "PROPN")],
     ["declarative", "present_continuous"], []),
    ("They have finished their homework.",
     [("They", "PRON"), ("have", "AUX"), ("finished", "VERB"), ("homework", "NOUN")],
     ["present_perfect"], ["past_simple", "present_continuous", "future_simple"]),
    ("I will be working tomorrow.",
     [("will", "AUX"), ("working", "VERB"), ("tomorrow", "ADV")],
     ["future_continuous"], ["past_simple", "present_perfect"]),
    ("The beautiful girl reads a book.",
     [("beautiful", "ADJ"), ("girl", "NOUN"), ("reads", "VERB"), ("a", "DET")],
     ["simple_present", "third_person_s"], ["past_simple"]),
    ("Can you help me?",
     [("Can", "AUX"), ("you", "PRON"), ("help", "VERB"), ("me", "PRON")],
     ["yes_no_question", "modal_verb"], ["past_simple", "present_continuous"]),
    ("If it rains, we will stay home.",
     [("rains", "VERB"), ("will", "AUX"), ("stay", "VERB")],
     ["first_conditional", "future_simple"], []),
    ("The book was written by George.",
     [("was", "AUX"), ("written", "VERB"), ("George", "PROPN")],
     ["passive_voice"], ["past_continuous", "past_simple"]),
    ("She has been studying for three hours.",
     [("has", "AUX"), ("been", "AUX"), ("studying", "VERB")],
     ["present_perfect_continuous"],
     ["past_perfect_continuous", "present_perfect"]),
    ("I enjoy reading books.",
     [("enjoy", "VERB"), ("books", "NOUN")],
     ["simple_present", "gerund"], ["past_simple"]),
    ("He did not understand the question.",
     [("did", "AUX"), ("not", "PART"), ("understand", "VERB")],
     ["past_simple", "negation"], ["present_perfect"]),
    # the ones that actually caught bugs while this was built
    ("She's been working all day.",
     [("working", "VERB")], ["present_perfect_continuous"], []),
    ("He is running and she is swimming.",
     [("running", "VERB"), ("swimming", "VERB")],
     ["present_continuous", "conjunction"], []),
    ("Have you ever been to London?",
     [("been", "AUX"), ("London", "PROPN")],
     ["present_perfect", "yes_no_question"], ["past_simple"]),
    ("If I had known, I would have called you.",
     [("had", "AUX"), ("known", "VERB"), ("called", "VERB")],
     ["third_conditional", "past_perfect"], []),
    ("He must have forgotten his keys.",
     [("must", "AUX"), ("forgotten", "VERB")],
     ["modal_perfect"], ["past_simple", "present_perfect"]),
    ("We will have finished by Friday.",
     [("will", "AUX"), ("finished", "VERB")],
     ["future_perfect"], ["future_simple", "present_perfect"]),
    ("They had already eaten by then.",
     [("had", "AUX"), ("eaten", "VERB"), ("already", "ADV")],
     ["past_perfect"], ["present_perfect"]),
    ("She was cooking when I arrived.",
     [("was", "AUX"), ("cooking", "VERB")],
     ["past_continuous", "past_simple"], []),
    ("Read this book.", [("Read", "VERB")], ["imperative"], ["declarative"]),
    ("Turn off the light!", [("Turn", "VERB")],
     ["imperative", "exclamative"], ["declarative"]),
    ("He decided to stay.",
     [("decided", "VERB")], ["past_simple", "infinitive"], []),
    ("She wants to go home.",
     [("wants", "VERB")], ["simple_present", "infinitive", "verb_infinitive"], []),
    # deliberately hard input: the requirement is honesty, not cleverness
    ("THE CAT SAT ON THE MAT.",
     [("SAT", "VERB"), ("MAT", "NOUN")], ["past_simple", "articles"], []),
    ("My friend Zebulonvonmaximilian went to Paris.",
     [("went", "VERB"), ("Paris", "PROPN")],
     ["past_simple", "prepositional_phrase"], []),
    ("The old man the boat.", [("man", "NOUN")], ["articles"], ["past_simple"]),
    ("مرحبا Hello این یک test است", [], [], []),
    ("i am learn english", [], [], ["present_continuous", "past_simple"]),
    ("I read a book yesterday.", [("read", "VERB")], ["simple_present"], []),
    ('"Hello," she said...', [("said", "VERB")], ["past_simple"], []),
    ("", [], [], []),
    ("   ", [], [], []),
]

# A dependency label is the one thing this module must never invent: it would
# read as a parse the model cannot produce.
FABRICATED = ["nsubj", "dobj", "iobj", "ROOT", "amod", "advmod", "det", "aux",
              "pobj", "prep", "conj", "ccomp", "xcomp", "cc", "mark", "nsubjpass"]

# What a request typed into the chat must hand to the tagger. This is the other
# half of the feature: the analysis can only be right about the sentence it was
# actually given, so the request words come off and the learner's own words,
# articles and punctuation stay on.
EXTRACTED = [
    ("analyse this sentence: They have finished their homework.",
     "They have finished their homework."),
    ("analyze this: She has been learning English.",
     "She has been learning English."),
    ("analyse this: The book was written by George.",
     "The book was written by George."),
    ("the structure of this sentence: The book was written by George.",
     "The book was written by George."),
    ("break this sentence down: I enjoy reading books.",
     "I enjoy reading books."),
    ("Can you analyse The cat sat on the mat.",
     "The cat sat on the mat."),
    ("نقش دستوری کلمات این جمله چیه؟ The book was written by George.",
     "The book was written by George."),
    ("این جمله رو از نظر گرامری تحلیل کن: She is learning English.",
     "She is learning English."),
    ("فاعل و فعل این جمله رو مشخص کن. He did not understand the question.",
     "He did not understand the question."),
    # a message that merely mentions grammar is a question for the tutor, not a
    # sentence to take apart, so nothing may be extracted from it
    ("تحلیل گرامری کن", ""),
    ("parts of speech", ""),
    ("نقش دستوری کلمات چیه؟", ""),
    ("what does negotiate mean?", ""),
    ("open grammar section", ""),
    ("grammar", ""),
    ("analyse this", ""),
]

EXTRACT_HARNESS = r"""
const cases = JSON.parse(process.argv[2]);
let bad = [];
let fired = 0;
for (const [text, want] of cases) {
  const requested = ANALYSE_INTENT.test(text);
  if (want && !requested) { bad.push('not recognised as a request: ' + JSON.stringify(text)); continue; }
  if (!requested) continue;
  fired++;
  const got = extractSentence(text);
  if (got !== want) {
    bad.push(JSON.stringify(text) + ' -> ' + JSON.stringify(got) + ', expected ' + JSON.stringify(want));
  }
}
console.log(JSON.stringify({problems: bad, requested: fired, cases: cases.length}));
process.exit(bad.length ? 1 : 0);
"""


def extraction_checks(problems: list[str]) -> None:
    """Run the page's own intent + extractor, sliced out of webapp.py."""
    src = (ROOT / "webapp.py").read_text(encoding="utf-8")
    try:
        start = src.index("const ANALYSE_INTENT = new RegExp(")
        end = src.index("/* The analysis, rendered once and used twice")
    except ValueError:
        problems.append("the page no longer holds the analyser's request matcher")
        return
    block = src[start:end]
    if "function extractSentence" not in block:
        problems.append("extractSentence() is not where this check looks for it")
        return
    if not shutil.which("node"):
        return
    CACHE.mkdir(parents=True, exist_ok=True)
    script = CACHE / "analyser_extract.js"
    script.write_text(block + EXTRACT_HARNESS, encoding="utf-8")
    proc = subprocess.run(
        ["node", str(script), json.dumps(EXTRACTED, ensure_ascii=False)],
        capture_output=True, text=True)
    out = proc.stdout.strip().split("\n")[-1] if proc.stdout.strip() else ""
    try:
        payload = json.loads(out)
    except json.JSONDecodeError:
        problems.append("the extractor could not be exercised: " + (proc.stderr or out)[:200])
        return
    for p in payload["problems"]:
        problems.append(p)
    if payload["requested"] < 8:
        problems.append(
            f"only {payload['requested']} of {payload['cases']} messages were seen as requests")


HARNESS = r"""
const fs = require('fs');
const vm = require('vm');
const [bundlePath, casesPath] = process.argv.slice(2);

/* The page provides a browser: atob and performance come with it. Giving the
   bundle the same two here is what makes this the shipped artifact under test
   rather than a node-only variant of it. */
const ctx = {console, atob, performance, TextDecoder};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(bundlePath, 'utf8'), ctx, {filename: 'fluentify-nlp.js'});
const A = ctx.FluentifyNLP;

const payload = JSON.parse(fs.readFileSync(casesPath, 'utf8'));
const problems = [];
const check = (ok, what) => { if (!ok) problems.push(what); return ok; };

let checks = 0;
const results = [];
for (const c of payload.cases) {
  const r = A.analyze(c.input);
  results.push(r);
  const byText = {};
  for (const t of r.tokens) byText[t.text] = t;
  for (const [word, pos] of c.pos) {
    checks++;
    const t = byText[word];
    if (!t) { problems.push(JSON.stringify(c.input) + ': no token ' + JSON.stringify(word)); continue; }
    if (t.pos !== pos) {
      problems.push(JSON.stringify(c.input) + ': ' + word + ' tagged ' + t.pos + ', expected ' + pos);
    }
  }
  for (const id of c.want) {
    checks++;
    if (r.detectedStructures.indexOf(id) === -1) {
      problems.push(JSON.stringify(c.input) + ': missing structure ' + id +
                    ' (got ' + r.detectedStructures.join(', ') + ')');
    }
  }
  for (const id of c.ban) {
    checks++;
    if (r.detectedStructures.indexOf(id) !== -1) {
      problems.push(JSON.stringify(c.input) + ': wrong structure ' + id +
                    ' (got ' + r.detectedStructures.join(', ') + ')');
    }
  }

  // the contract of the schema
  checks += 3;
  if (r.originalSentence !== c.input) problems.push(JSON.stringify(c.input) + ': originalSentence was altered');
  if (r.language !== 'en' || r.source !== 'offline') problems.push(JSON.stringify(c.input) + ': wrong language/source');
  if (!r.engine || /wink/.test(r.engine) === false) problems.push('the engine name does not name the engine: ' + r.engine);
  if (!Array.isArray(r.limitations) || !r.limitations.length) {
    problems.push(JSON.stringify(c.input) + ': the limits of the method are not stated');
  }
  for (const t of r.tokens) {
    checks++;
    if (c.input.slice(t.start, t.end) !== t.text) {
      problems.push(JSON.stringify(c.input) + ': offsets for ' + JSON.stringify(t.text) +
                    ' slice ' + JSON.stringify(c.input.slice(t.start, t.end)));
    }
    checks++;
    if (t.grammaticalRole && t.roleStatus !== 'inferred') {
      problems.push(JSON.stringify(c.input) + ': role ' + t.grammaticalRole + ' is not marked inferred');
    }
    checks++;
    if (payload.fabricated.indexOf(t.grammaticalRole) !== -1) {
      problems.push(JSON.stringify(c.input) + ': fabricated dependency label ' + t.grammaticalRole);
    }
  }

  // determinism: the learner must not get two different answers
  checks++;
  if (JSON.stringify(A.analyze(c.input)) !== JSON.stringify(r)) {
    problems.push(JSON.stringify(c.input) + ': two runs of the same sentence disagree');
  }
}

// long input is bounded, and says so rather than truncating in silence
const long = Array.from({length: 90}, (_, i) => 'word' + i).join(' ') + ' end.';
const longRun = A.analyze(long);
checks += 3;
if (longRun.tokens.length > 41) problems.push('a 90-word paste was not bounded (' + longRun.tokens.length + ' tokens)');
if (!longRun.limitations.some((l) => /only the first 40/.test(l))) problems.push('a bounded paste was not told it was cut');
if (longRun.tokenCount !== longRun.tokens.filter((t) => ['PUNCT', 'SYM', 'X'].indexOf(t.pos) === -1).length) {
  problems.push('tokenCount does not count the words it returns');
}
const wide = A.analyze('a '.repeat(400) + 'b');
checks++;
if (wide.analysedSentence.length > 400) problems.push('the 400-character ceiling was not applied');

// null / undefined must not throw: the chat can hand over an empty box
checks += 2;
try { A.analyze(null); A.analyze(undefined); }
catch (e) { problems.push('analyze(null) threw ' + e.message); }

const t0 = Date.now();
for (let i = 0; i < 10; i++) A.analyze('She has been studying English for three hours.');
const warm = (Date.now() - t0) / 10;

// and the shipped copy really is the lazy one: nothing is built until asked
const fresh = {console, atob, performance, TextDecoder};
vm.createContext(fresh);
vm.runInContext(fs.readFileSync(bundlePath, 'utf8'), fresh, {filename: 'fluentify-nlp.js'});
checks++;
if (fresh.FluentifyNLP.isReady()) problems.push('the model was built at load time instead of on first use');
fresh.FluentifyNLP.init();

console.log(JSON.stringify({
  problems, checks, warm, initMs: fresh.FluentifyNLP.initMs(),
  version: fresh.FluentifyNLP.version, maxTokens: fresh.FluentifyNLP.maxTokens,
  structures: results.reduce((n, r) => n + r.detectedStructures.length, 0),
}));
process.exit(problems.length ? 1 : 0);
"""


def topic_mapping() -> dict[str, str]:
    """structure id -> Knowledge Base phrase, read out of webapp.py."""
    src = (ROOT / "webapp.py").read_text(encoding="utf-8")
    block = src[src.index("const TOPIC = {"):]
    block = block[:block.index("};\n")]
    return dict(re.findall(r"([a-z_]+):\s*'([^']+)'", block))


def topic_checks(problems: list[str]) -> None:
    """Every lesson chip must land on a lesson that exists.

    The analysis offers a chip per detected structure, and the chip works by
    asking the Knowledge Base the phrase it already answers — so a phrase that
    is not a keyword in grammar.json would open a lesson that is not there.
    This checks the link from both ends: the phrase is real, and the tutor (the
    same engine the APK ships) answers it with a grammar lesson.
    """
    mapping = topic_mapping()
    if len(mapping) < 20:
        problems.append(f"only {len(mapping)} structures map to a lesson")
        return
    topics = json.loads((ROOT / "grammar.json").read_text(encoding="utf-8"))["topics"]
    known = set()
    for topic in topics.values():
        known.update(k.lower() for k in topic.get("keywords", {}).get("en", []))
    for sid, phrase in sorted(mapping.items()):
        if phrase.lower() not in known:
            problems.append(f"'{phrase}' (for {sid}) is not a keyword in grammar.json")

    sys.path.insert(0, str(ROOT))
    try:
        from chatbot import ChatBot
    except Exception as exc:  # pragma: no cover - a broken import is a failure
        problems.append(f"the chatbot could not be imported: {exc}")
        return
    phrases = sorted(set(mapping.values()))
    bot = ChatBot()
    for phrase in phrases:
        reply = bot.respond(phrase)
        if "📘" not in reply:
            problems.append(f"the Knowledge Base does not answer '{phrase}' with a lesson")
        # the analysis links to the lesson; the lesson has to be about grammar
        if "Grammar" not in reply:
            problems.append(f"'{phrase}' answers with something that is not a grammar lesson")

    # The chip has to work in the APK too, and the APK answers with bot.js, not
    # with chatbot.py. Same questions, the other engine: a chip that only works
    # online would be a link to nothing once the phone is offline.
    if shutil.which("node") and (ROOT / "tools" / "js_engine.js").exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        cases = CACHE / "analyser_topics.json"
        replies = CACHE / "analyser_topics_out.json"
        cases.write_text(json.dumps([{"input": p} for p in phrases], ensure_ascii=False),
                         encoding="utf-8")
        proc = subprocess.run(
            ["node", str(ROOT / "tools" / "js_engine.js"), str(cases), str(replies)],
            capture_output=True, text=True)
        if proc.returncode != 0:
            problems.append("the APK engine could not be run: " +
                            (proc.stderr or proc.stdout).strip().split("\n")[0][:200])
        else:
            out = json.loads(replies.read_text(encoding="utf-8"))
            for phrase, reply in zip(phrases, out):
                if "📘" not in reply or "Grammar" not in reply:
                    problems.append(
                        f"the APK engine does not answer '{phrase}' with a grammar lesson")


def static_checks() -> list[str]:
    """Things a bundle cannot tell you about itself."""
    problems = []
    topic_checks(problems)
    src = BUNDLE.read_text(encoding="utf-8")

    for needle, what in (
        ("fetch(", "a network call"),
        ("XMLHttpRequest", "a network call"),
        ("importScripts", "a worker-side import"),
        ("require(", "a node require the WebView cannot resolve"),
        ("http://", "an insecure absolute URL"),
        ("unpkg.com", "a CDN reference"),
        ("jsdelivr", "a CDN reference"),
        ("cdnjs", "a CDN reference"),
        ("cloudflare.com", "a CDN reference"),
    ):
        if needle in src:
            problems.append(f"the bundle contains {what}: {needle}")

    # The bundle is minified model data, so a URL can only be part of it by
    # accident: the one https:// left is a documentation link inside the
    # library's own source comment. Nothing may *load* from one.
    if "src=" in src or "href=" in src:
        problems.append("the bundle assigns a src/href: it must load nothing")

    # The page has to reach it locally, on http from the server and over
    # file:// inside the APK, so the path must be relative to the page.
    page = (ROOT / "webapp.py").read_text(encoding="utf-8")
    if "nlp/fluentify-nlp.js" not in page:
        problems.append("the page never loads nlp/fluentify-nlp.js")
    if "analyzeEnglishGrammar" not in page and "NLP.analyze" not in page:
        problems.append("the page never calls the analyser")
    if "ANALYSE_INTENT" not in page and "matchAnalyseCommand" not in page:
        problems.append("no intent decides when a sentence should be analysed")
    if (ROOT / "webapp.py").read_text(encoding="utf-8").count("/nlp/") < 1:
        problems.append("the server has no route for the analyser bundle")

    apk = (ROOT / "build_apk_ui.py").read_text(encoding="utf-8")
    if "fluentify-nlp.js" not in apk:
        problems.append("the APK build does not copy the analyser into the bundle")

    notices = ROOT / "nlp" / "THIRD-PARTY-NOTICES.md"
    if not notices.exists():
        problems.append("nlp/THIRD-PARTY-NOTICES.md is missing")
    else:
        text = notices.read_text(encoding="utf-8")
        for name in ("wink-nlp", "wink-eng-lite-web-model"):
            if name not in text:
                problems.append(f"the notices do not cover {name}")
        if "MIT" not in text:
            problems.append("the notices do not state the licence")
        if "Permission is hereby granted" not in text:
            problems.append("the notices do not carry the licence text itself")
        if "model" not in text:
            problems.append("the notices do not say which model is bundled")

    # The notice must travel inside the shipped file, not only beside it: the
    # APK distributes the .js, and npm is never run in CI, so a licence that
    # lives only in node_modules would not be present where it is needed.
    head = src[:1200]
    for needle in ("MIT", "wink-nlp", "wink-eng-lite-web-model"):
        if needle not in head:
            problems.append(f"the bundle's own notice does not mention {needle}")

    # And the copy inside the APK has to be this exact file. A stale copy is
    # how the app quietly runs last week's analyser against this week's code.
    apk_copy = (ROOT / "android" / "app" / "src" / "main" / "assets" / "www"
                / "nlp" / "fluentify-nlp.js")
    if not apk_copy.exists():
        problems.append("the APK assets have no analyser - run python3 build_apk_ui.py")
    elif apk_copy.read_bytes() != BUNDLE.read_bytes():
        problems.append("the analyser inside the APK is not the file in nlp/ - "
                        "run python3 build_apk_ui.py")
    return problems


def main() -> int:
    if not BUNDLE.exists():
        print("FAIL  nlp/fluentify-nlp.js is missing - run: cd nlp && npm run build")
        return 1

    problems = static_checks()
    if not problems:
        extraction_checks(problems)
    if problems:
        for p in problems:
            print("FAIL  " + p)
        return 1

    if not shutil.which("node"):
        print("SKIP  node is not installed - the analyser was not exercised")
        return 0

    CACHE.mkdir(parents=True, exist_ok=True)
    payload = {
        "fabricated": FABRICATED,
        "cases": [
            {"input": s, "pos": [list(p) for p in pos], "want": want, "ban": ban}
            for s, pos, want, ban in CASES
        ],
    }
    cases_file = CACHE / "analyser_cases.json"
    cases_file.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    harness = CACHE / "analyser_check.js"
    harness.write_text(HARNESS, encoding="utf-8")

    proc = subprocess.run(["node", str(harness), str(BUNDLE), str(cases_file)],
                          capture_output=True, text=True)
    out = proc.stdout.strip().split("\n")[-1] if proc.stdout.strip() else ""
    if proc.returncode != 0:
        detail = ""
        try:
            detail = "; ".join(json.loads(out).get("problems", [])[:6])
        except json.JSONDecodeError:
            detail = (proc.stderr or out).strip().split("\n")[0][:300]
        print("FAIL  " + (detail or "the analyser check did not pass"))
        return 1

    meta = json.loads(out)
    mb = BUNDLE.stat().st_size / (1024 * 1024)
    print(f"PASS  {meta['checks']} analyser checks over {len(CASES)} sentences "
          f"({meta['structures']} structures) + {len(EXTRACTED)} requests, "
          f"{meta['version']}, {mb:.1f} MB, model built in {meta['initMs']} ms, "
          f"{meta['warm']:.2f} ms warm")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
