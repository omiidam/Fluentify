#!/usr/bin/env python3
"""Correct a learner's sentence with Unbabel/gec-t5_small, on this machine.

    python3 tools/gec.py --check
    python3 tools/gec.py "I like to swimming"
    python3 tools/gec.py "he don't like it" --json
    printf 'I have went there\\nShe have a car\\n' | python3 tools/gec.py --stdin

Unbabel/gec-t5_small is T5-small fine-tuned for grammatical error correction
(apache-2.0). It is asked for a correction the way its model card says: the
sentence prefixed with "gec: ", five beams, 128 tokens.

This tool is the whole integration. Nothing in the shipped app imports it: the
web page and the APK run the stdlib/browser engines (`chatbot.py`, `bot.js`),
neither of which can load a T5, so the model lives beside them instead of
inside them. That is also why it is not on the default chat path - see
`second_opinion()` in chatbot.py, which needs FLUENTIFY_GEC=1.

Dependencies are optional and probed, never assumed, the way
tools/transcribe.py probes its backends. If torch/transformers are missing the
tool says which command installs them; if a project venv exists at
`.venv/gec`, this script re-runs itself inside it so the system Python never
grows a 900 MB dependency.

The first run downloads ~242 MB of weights into tools/.cache/models (gitignored).
After that every correction is offline.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "gec.json"
FIXES = ROOT / "gec_fixes.json"

PERSIAN = re.compile(r"[\u0600-\u06FF]")
LATIN = re.compile(r"[A-Za-z]")

_MODEL = None
_TOKENIZER = None
_LOADED_AT = 0.0


# --------------------------------------------------------------------------
# config
# --------------------------------------------------------------------------
def load_config() -> dict:
    """gec.json, with the documented defaults if a key has been removed."""
    cfg = json.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}
    model = cfg.setdefault("model", {})
    run = cfg.setdefault("run", {})
    env = cfg.setdefault("env", {})
    model.setdefault("id", "Unbabel/gec-t5_small")
    model.setdefault("tokenizer", "t5-small")
    model.setdefault("prefix", "gec: ")
    model.setdefault("revision", "main")
    run.setdefault("num_beams", 5)
    run.setdefault("max_length", 128)
    run.setdefault("early_stopping", True)
    run.setdefault("no_repeat_ngram_size", 3)
    run.setdefault("max_input_words", 40)
    run.setdefault("cache_dir", "tools/.cache/models")
    env.setdefault("venv", ".venv/gec")
    env.setdefault("flag", "FLUENTIFY_GEC")
    return cfg


def cache_dir(cfg: dict | None = None) -> Path:
    cfg = cfg or load_config()
    path = Path(cfg["run"]["cache_dir"])
    return path if path.is_absolute() else ROOT / path


def venv_python(cfg: dict | None = None) -> Path:
    cfg = cfg or load_config()
    return ROOT / cfg["env"]["venv"] / "bin" / "python"


# --------------------------------------------------------------------------
# environment
# --------------------------------------------------------------------------
def probe() -> dict:
    """What is importable in *this* interpreter, and whether the weights are here."""
    found = {}
    for name, module in (("torch", "torch"), ("transformers", "transformers"),
                         ("sentencepiece", "sentencepiece")):
        try:
            found[name] = importlib.util.find_spec(module) is not None
        except (ImportError, ValueError):
            found[name] = False
    found["weights"] = weights_present()
    found["venv"] = venv_python().exists()
    return found


def weights_present() -> bool:
    """A downloaded checkpoint, not merely an empty cache directory."""
    base = cache_dir()
    if not base.exists():
        return False
    for folder in base.glob("models--*gec-t5_small*"):
        if (folder / "snapshots").exists() and any(
                folder.glob("snapshots/*/*.safetensors")):
            return True
        if (folder / "snapshots").exists() and any(
                folder.glob("snapshots/*/pytorch_model.bin")):
            return True
    return any(base.glob("**/gec-t5_small*/**/config.json"))


def weights_size_mb() -> float:
    base = cache_dir()
    total = 0
    for folder in base.glob("models--*gec-t5_small*"):
        for f in folder.rglob("*"):
            if f.is_file():
                total += f.stat().st_size
    return round(total / (1024 * 1024), 1)


def ensure_environment(argv: list[str]) -> None:
    """Re-run inside `.venv/gec` when the model's dependencies live there.

    A 900 MB dependency does not belong in the system Python of a project whose
    selling point is "stdlib only" - so the venv is opt-in by existing, and this
    keeps the invocation (`python3 tools/gec.py …`) the same either way.
    """
    if sys.platform == "win32":
        return
    target = venv_python()
    if not target.exists():
        return
    # Compare prefixes, not resolved paths: a venv's `python` is a symlink to
    # the system interpreter, so resolve() would call the two the same program
    # and skip the re-exec that gives the venv its packages.
    if Path(sys.prefix) == target.parent.parent:
        return
    if importlib.util.find_spec("torch") and importlib.util.find_spec("transformers"):
        return  # this interpreter can already do the job
    os.execv(str(target), [str(target), str(Path(__file__).resolve())] + argv)


# --------------------------------------------------------------------------
# the model
# --------------------------------------------------------------------------
def load_model(cfg: dict | None = None):
    """Load (once) and return (model, tokenizer), cached for the process."""
    global _MODEL, _TOKENIZER, _LOADED_AT
    if _MODEL is not None and _TOKENIZER is not None:
        return _MODEL, _TOKENIZER
    cfg = cfg or load_config()
    have = probe()
    missing = [k for k in ("torch", "transformers") if not have[k]]
    if missing:
        raise RuntimeError(
            "the GEC model needs " + " and ".join(missing) + ":\n"
            "    pip install torch --index-url https://download.pytorch.org/whl/cpu\n"
            "    pip install transformers sentencepiece\n"
            "  or keep them in the project venv: .venv/gec\n"
            "  `python3 tools/gec.py --check` shows the current state."
        )
    # Once the weights are here, nothing should reach the network - not even
    # the hub's revision check. This has to happen before transformers is
    # imported, because huggingface_hub reads the flag when it is loaded.
    if weights_present():
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
    from transformers import T5ForConditionalGeneration, T5Tokenizer

    started = time.time()
    cache = cache_dir(cfg)
    cache.mkdir(parents=True, exist_ok=True)
    _TOKENIZER = T5Tokenizer.from_pretrained(
        cfg["model"]["tokenizer"], cache_dir=str(cache),
        legacy=False,  # the fast tokenizer's sentencepiece path
    )
    _MODEL = T5ForConditionalGeneration.from_pretrained(
        cfg["model"]["id"], cache_dir=str(cache),
        revision=cfg["model"]["revision"],
    )
    _MODEL.eval()
    _LOADED_AT = round(time.time() - started, 2)
    return _MODEL, _TOKENIZER


def load_seconds() -> float:
    return _LOADED_AT


def load_fixes() -> list[dict]:
    """The deterministic rules that run before and after the model.

    A 60M-parameter corrector has classes it never fixes - pronoun case,
    "It is me", "I wish I was", have + simple past. They are cheap to state as
    rules and expensive to leave to the model, so they live in gec_fixes.json,
    which the page reads too. A rule that does not compile is skipped rather
    than taking the sentence down with it.
    """
    if not FIXES.exists():
        return []
    try:
        return json.loads(FIXES.read_text(encoding="utf-8")).get("rules", [])
    except ValueError:
        return []


def apply_fixes(text: str) -> str:
    """Rules applied in order, then the sentence's capital restored.

    Restoring it is not decoration: "Me and my brother went out" becomes
    "my brother and I went out" once the pronoun rule fires, and a correction
    that starts a sentence in lower case looks broken however right it is.
    """
    out = text
    for rule in load_fixes():
        flags = re.IGNORECASE if "i" in (rule.get("flags") or "") else 0
        try:
            out = re.sub(rule["pattern"], rule["replace"], out, flags=flags)
        except re.error:
            continue
    if text[:1].isupper() and out[:1].islower():
        out = out[0].upper() + out[1:]
    return out


def equivalent(a: str, b: str) -> bool:
    """Same sentence, ignoring what a corrector is allowed to tidy.

    The model capitalises the first word and closes the sentence, so a correct
    sentence comes back as "The book is on the table." - a difference of
    punctuation, not of grammar. Counting that as a correction would make every
    already-correct sentence look repaired, and the bench useless.
    """
    def norm(text: str) -> str:
        return re.sub(r"[.!?]+\s*$", "", " ".join(text.split())).strip().casefold()

    return norm(a) == norm(b)


def refuse(sentence: str, cfg: dict | None = None) -> str | None:
    """The cases the model must not be asked about, or it will invent an answer.

    They are answered before anything is loaded, so a bad request costs nothing
    and the message names the reason instead of returning a mangled sentence.
    """
    cfg = cfg or load_config()
    text = (sentence or "").strip()
    if not text:
        return "Nothing to correct — the sentence is empty."
    if not LATIN.search(text):
        return ("The model corrects English only. / این مدل فقط انگلیسی را "
                "اصلاح می‌کند.")
    persian = len(PERSIAN.findall(text))
    if persian > len(LATIN.findall(text)):
        return ("That sentence is mostly Persian, and gec-t5_small was trained "
                "on English. Send an English sentence. / جملهٔ انگلیسی بفرست.")
    limit = int(cfg["run"]["max_input_words"])
    words = len(text.split())
    if words > limit:
        return (f"{words} words is past the {limit}-word limit — a T5-small "
                "correction degrades long before 128 tokens.")
    return None


def correct(sentence: str, cfg: dict | None = None) -> dict:
    """One sentence in, one correction out, plus what it cost.

    Returns {"input", "output", "changed", "refused", "seconds"} so callers (the
    CLI, the harness, the chat's second opinion) never parse a printed line.
    """
    cfg = cfg or load_config()
    text = " ".join((sentence or "").split())
    reason = refuse(text, cfg)
    if reason:
        return {"input": text, "output": "", "changed": False,
                "refused": reason, "seconds": 0.0}
    model, tokenizer = load_model(cfg)
    started = time.time()
    # rules first: the model corrects what it was trained on, and a pronoun
    # fixed before it is asked is one it cannot get wrong
    cleaned = apply_fixes(text)
    batch = tokenizer([cfg["model"]["prefix"] + cleaned],
                      max_length=cfg["run"]["max_length"], truncation=True,
                      padding="max_length", return_tensors="pt")
    ids = model.generate(
        input_ids=batch.input_ids,
        attention_mask=batch.attention_mask,
        max_length=cfg["run"]["max_length"],
        num_beams=cfg["run"]["num_beams"],
        early_stopping=cfg["run"]["early_stopping"],
        no_repeat_ngram_size=cfg["run"]["no_repeat_ngram_size"],
    )
    out = tokenizer.decode(ids[0], skip_special_tokens=True,
                           clean_up_tokenization_spaces=True)
    out = apply_fixes(" ".join(out.split()))
    elapsed = round(time.time() - started, 3)
    return {"input": text, "output": out, "changed": not equivalent(out, text),
            "refused": None, "seconds": elapsed}


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# the chat's opt-in second opinion
# --------------------------------------------------------------------------
def second_opinion(sentence: str, cfg: dict | None = None) -> str:
    """The corrected sentence, or "" - and only when FLUENTIFY_GEC asks for it.

    The flag exists because a correction line in every grammar reply would put
    the CLI and the JS engine of the APK out of step: the APK cannot load a T5,
    and `tests_js_vs_python.py` holds the two to the same words. Off by
    default, so the shipped conversation is the one that ships.

    `python3 chatbot.py` runs on the system interpreter, which has no torch -
    by design. Rather than ask anyone to run the chat from the venv, this asks
    the venv for the answer and keeps its own process stdlib-only.
    """
    cfg = cfg or load_config()
    flag = cfg["env"]["flag"]
    if os.environ.get(flag, "").strip().lower() not in ("1", "on", "true", "yes"):
        return ""
    text = " ".join((sentence or "").split())
    if not text or refuse(text, cfg):
        return ""

    have = probe()
    if have["torch"] and have["transformers"]:
        row = correct(text, cfg)
    elif venv_python(cfg).exists():
        row = _ask_venv(text, cfg)
    else:
        row = {"output": "", "refused": "no model environment", "changed": False}
    if row.get("refused") or not row.get("changed"):
        return ""
    return row["output"]


def _ask_venv(sentence: str, cfg: dict) -> dict:
    """One sentence through the project venv, as JSON."""
    try:
        proc = subprocess.run(
            [str(venv_python(cfg)), str(Path(__file__).resolve()),
             sentence, "--json"],
            capture_output=True, text=True, timeout=180,
            env={k: v for k, v in os.environ.items()
                 if k.lower() not in ("all_proxy",)},
        )
    except (OSError, subprocess.SubprocessError):
        return {"output": "", "refused": "the model process did not start",
                "changed": False}
    if proc.returncode != 0:
        return {"output": "", "refused": "the model process failed",
                "changed": False}
    # The tool prints indented JSON, so this parses the whole stream rather
    # than its last line - that shortcut reported every answer as unreadable.
    text = proc.stdout.strip()
    if not text:
        return {"output": "", "refused": "the model printed nothing",
                "changed": False}
    try:
        rows = json.loads(text)
    except ValueError:
        start = min((i for i in (text.find("["), text.find("{")) if i >= 0), default=-1)
        try:
            rows = json.loads(text[start:]) if start >= 0 else None
        except ValueError:
            rows = None
    if rows is None:
        return {"output": "", "refused": "unreadable model output",
                "changed": False}
    row = rows[0] if isinstance(rows, list) and rows else {}
    # The venv is told to re-exec itself; when it is already the interpreter it
    # answers directly, and both shapes have to decode here.
    if "rows" in row:
        row = row["rows"][0] if row["rows"] else {}
    return row or {"output": "", "refused": "empty answer", "changed": False}


def report(cfg: dict) -> int:
    have = probe()
    print("gec-t5_small — local grammatical error correction")
    print(f"  model      {cfg['model']['id']} (tokenizer {cfg['model']['tokenizer']})")
    print(f"  cache      {cache_dir(cfg)}")
    print(f"  torch      {'installed' if have['torch'] else 'missing'}")
    print(f"  transformers {'installed' if have['transformers'] else 'missing'}")
    print(f"  sentencepiece {'installed' if have['sentencepiece'] else 'missing'}")
    if have["weights"]:
        print(f"  weights    present ({weights_size_mb()} MB, offline)")
    else:
        print("  weights    not downloaded yet (the first run fetches ~242 MB)")
    print(f"  venv       {venv_python(cfg)}"
          f"{'' if have['venv'] else ' (absent)'}")
    print(f"  surfaces   CLI only; enable the chat's second opinion with "
          f"{cfg['env']['flag']}=1")
    if not (have["torch"] and have["transformers"]):
        print("\n  Install the dependencies:")
        print("    python3 -m venv .venv/gec")
        print("    .venv/gec/bin/pip install torch --index-url "
              "https://download.pytorch.org/whl/cpu")
        print("    .venv/gec/bin/pip install transformers sentencepiece")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    cfg = load_config()
    parser = argparse.ArgumentParser(
        description="Correct English sentences locally with Unbabel/gec-t5_small.")
    parser.add_argument("sentence", nargs="*", help="the sentence to correct")
    parser.add_argument("--check", action="store_true",
                        help="report the model, the dependencies and the cache")
    parser.add_argument("--stdin", action="store_true",
                        help="read one sentence per line and correct each")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--beams", type=int, help="override run.num_beams")
    parser.add_argument("--max-words", type=int, help="override run.max_input_words")
    parser.add_argument("--bench", action="store_true",
                        help="time the model over a few known sentences")
    args = parser.parse_args(argv)

    if args.check:
        return report(cfg)
    if args.beams:
        cfg["run"]["num_beams"] = args.beams
    if args.max_words:
        cfg["run"]["max_input_words"] = args.max_words

    if args.bench:
        return bench(cfg, as_json=args.json)

    if args.stdin:
        lines = [line.strip() for line in sys.stdin if line.strip()]
    elif args.sentence:
        lines = [" ".join(args.sentence)]
    else:
        parser.print_help()
        return 2
    if not lines:
        print("Nothing to correct.", file=sys.stderr)
        return 2

    rows = [correct(line, cfg) for line in lines]
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return 0
    for row in rows:
        if row["refused"]:
            print(f"⚠  {row['input']}\n   {row['refused']}")
        elif row["changed"]:
            print(f"✏️  {row['input']}\n   → {row['output']}   ({row['seconds']}s)")
        else:
            print(f"✅ {row['input']}\n   no change   ({row['seconds']}s)")
    print(f"   loaded in {load_seconds()}s · {len(rows)} sentence(s)")
    return 0


BENCH = [
    "I like to swimming",
    "he don't like it",
    "I have went there",
    "She have a car",
    "I have many informations",
    "They was happy yesterday",
    "I am agree with you",
    "despite of the rain we went out",
    "She watches TV every day",
    "The book is on the table",
    "I have seen him before",
]


def bench(cfg: dict, as_json: bool = False) -> int:
    """Sentences whose answers are already known, timed.

    Most are wrong on purpose and three are already correct: a corrector that
    rewrites good English is worse than none, and this is where that shows.
    """
    rows = [correct(s, cfg) for s in BENCH]
    if as_json:
        print(json.dumps({"load_seconds": load_seconds(), "rows": rows},
                         ensure_ascii=False, indent=1))
        return 0
    print(f"load {load_seconds()}s")
    kept = 0
    for row in rows:
        mark = "=" if not row["changed"] else "→"
        print(f"  {mark} {row['input']}")
        if row["changed"]:
            print(f"      {row['output']}   ({row['seconds']}s)")
        else:
            kept += 1
    total = sum(r["seconds"] for r in rows)
    print(f"  {kept}/{len(rows)} left alone, {total:.2f}s total")
    return 0


if __name__ == "__main__":
    try:
        ensure_environment(sys.argv[1:])
    except OSError:
        pass
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(3)
    except KeyboardInterrupt:
        raise SystemExit(130)
