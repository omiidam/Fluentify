# Third-party notices — offline grammar analyser

`nlp/fluentify-nlp.js` is a generated bundle. It contains **only** these two
packages, both MIT licensed, both included as source in the bundle (there is no
runtime CDN, no remote model download and no server call):

| Package | Version | Licence | Copyright | Weight in the bundle |
| --- | --- | --- | --- | --- |
| [`wink-nlp`](https://github.com/winkjs/wink-nlp) | 2.4.0 | MIT | © 2017–25 GRAYPE Systems Private Limited | ~0.5 MB |
| [`wink-eng-lite-web-model`](https://github.com/winkjs/wink-eng-lite-web-model) — the bundled English model | 1.8.1 | MIT | © 2017–20 GRAYPE Systems Private Limited | ~3.0 MB |

`esbuild` (MIT, © 2020 Evan Wallace) is a build-time-only devDependency: it is
used to produce the bundle and is **not** part of it.

Both MIT licences permit commercial use, modification and redistribution
provided the copyright notice and permission notice ship with the software. The
full text below is therefore reproduced in this file **and** embedded at the top
of the generated bundle itself, so the notice travels wherever the APK goes.

---

## The MIT License

Copyright (c) 2017-25  GRAYPE Systems Private Limited   (`wink-nlp` 2.4.0)
Copyright (c) 2017-20  GRAYPE Systems Private Limited   (`wink-eng-lite-web-model` 1.8.1)

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## What the bundled model is, and is not

`wink-eng-lite-web-model` is a rule- and lexicon-based English model shipped as
plain JavaScript data. It tokenises, sentence-splits, tags parts of speech,
lemmatises, flags negations and contractions, and recognises a set of named
entities.

It does **not** contain a syntactic dependency parser. Nothing in Fluentify
claims otherwise: the analyser never emits a dependency label (`nsubj`, `dobj`,
`ROOT`, …), the only roles it reports are subject and object inferred from word
order, and each of those is labelled `roleStatus: "inferred"` with the phone's
own wording. `tools/check_analyser.py` fails the build if a dependency label
ever appears in the output.
