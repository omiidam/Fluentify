#!/usr/bin/env python3
"""Serves GEC-BART Base over stdin/stdout, one sentence per line.

    .venv/gec/bin/python tools/gec_worker.py

The model costs seconds to load and about a third of a second to use, so a
process that starts, answers one sentence and exits spends almost all of its
time loading. This keeps the model resident and answers until stdin closes:

    {"sentence": "he don't like it"}         in
    {"input": "he don't like it", "output": "He doesn't like it.", ...}   out

The first line on stdout is `{"ready": true, "load_seconds": …}`, so a caller
knows the weights are in memory rather than guessing from a timeout.

No network is involved once the checkpoint is cached: tools/gec.py verifies the
manifest and sets HF_HUB_OFFLINE before transformers is imported, and the only
thing that ever fetches is an explicit install.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gec  # noqa: E402  (after the path insert, and imports torch lazily)


def serve() -> int:
    cfg = gec.load_config()
    try:
        gec.load_model(cfg)          # load once, before announcing readiness
    except RuntimeError as exc:      # missing torch/transformers or weights
        print(json.dumps({"ready": False, "error": str(exc)}), flush=True)
        return 3
    print(json.dumps({"ready": True, "load_seconds": gec.load_seconds(),
                      "model": gec.model_identity(cfg)}), flush=True)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            sentence = json.loads(line).get("sentence", "")
        except (ValueError, AttributeError):
            sentence = line
        try:
            row = gec.correct(sentence, cfg)
        except Exception as exc:     # one bad sentence must not end the process
            row = {"input": sentence, "output": "", "changed": False,
                   "refused": f"the model failed on this sentence: {exc}",
                   "seconds": 0.0}
        print(json.dumps(row, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    try:
        gec.ensure_environment(sys.argv[1:])
    except OSError:
        pass
    raise SystemExit(serve())
