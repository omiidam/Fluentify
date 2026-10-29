#!/usr/bin/env python3
"""Correct a learner's sentence with GEC-BART Base, on this machine.

    python3 tools/gec.py --check
    python3 tools/gec.py --install          # fetch the checkpoint (ArvanCloud first)
    python3 tools/gec.py "I like to swimming"
    python3 tools/gec.py "he don't like it" --json
    printf 'I have went there\\nShe have a car\\n' | python3 tools/gec.py --stdin

The checkpoint is gotutiyan/gec-bart-base - BART-base fine-tuned on BEA-2019,
CoNLL-2014 and FCE (Katsumata & Komachi, AACL 2020), MIT. Its weights are 558 MB
of safetensors, which is why they live in ArvanCloud object storage and on the
server's disk, and why no browser or APK ever loads them: the page and the phone
ask `/api/correct`, and this module answers on the server.

Where the weights come from, in order:

  1. the persistent cache (`FLUENTIFY_GEC_DIR`, else tools/.cache/gec-bart);
  2. ArvanCloud object storage, with the bucket's manifest checked against
     gec.json's pinned revision;
  3. Hugging Face - only when asked for with --from-hub, because a server in
     Iran should not need it.

Once the files are there nothing reaches the network again: the manifest is
checked, `HF_HUB_OFFLINE` is set, and every correction is computed locally.

Dependencies are optional and probed, never assumed, the way
tools/transcribe.py probes its backends. If torch/transformers are missing the
tool says which command installs them; if a project venv exists at `.venv/gec`,
this script re-runs itself inside it so the system Python never grows a 2 GB
dependency.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import threading
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
# One generate() at a time. BART is 558 MB of weights and three concurrent
# sentences on a CPU box is three times the latency and the same throughput.
_GENERATE = threading.Lock()


# --------------------------------------------------------------------------
# config
# --------------------------------------------------------------------------
def load_config() -> dict:
    """gec.json, with the documented defaults if a key has been removed."""
    cfg = json.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}
    model = cfg.setdefault("model", {})
    run = cfg.setdefault("run", {})
    env = cfg.setdefault("env", {})
    store = cfg.setdefault("storage", {})
    model.setdefault("id", "gotutiyan/gec-bart-base")
    model.setdefault("revision", "main")
    model.setdefault("license", "MIT")
    model.setdefault("architecture", "BartForConditionalGeneration")
    model.setdefault("prefix", "")
    model.setdefault("files", ["model.safetensors", "config.json",
                               "tokenizer.json", "tokenizer_config.json",
                               "vocab.json", "merges.txt",
                               "special_tokens_map.json"])
    model.setdefault("attribution", "README.md")
    run.setdefault("num_beams", 4)
    run.setdefault("max_length", 128)
    run.setdefault("min_length", 2)
    run.setdefault("no_repeat_ngram_size", 3)
    run.setdefault("length_penalty", 1.0)
    run.setdefault("early_stopping", True)
    run.setdefault("max_input_words", 64)
    run.setdefault("cache_dir", "tools/.cache/gec-bart")
    run.setdefault("load_timeout_seconds", 300)
    run.setdefault("infer_timeout_seconds", 120)
    env.setdefault("venv", ".venv/gec")
    env.setdefault("flag", "FLUENTIFY_GEC")
    env.setdefault("model_dir", "FLUENTIFY_GEC_DIR")
    store.setdefault("endpoint", "https://s3.ir-thr-at1.arvanstorage.ir")
    store.setdefault("region", "ir-thr-at1")
    store.setdefault("bucket", "fluentify-bbc")
    store.setdefault("prefix", "GEC-BART BASE/")
    store.setdefault("manifest", "manifest.json")
    store.setdefault("env_file", ".arvan-storage.env")
    return cfg


def model_dir(cfg: dict | None = None) -> Path:
    """The cache the service reads: an env override wins, so a server can put
    the checkpoint on a persistent disk without editing a tracked file."""
    cfg = cfg or load_config()
    override = os.environ.get(cfg["env"]["model_dir"], "").strip()
    if override:
        return Path(override)
    path = Path(cfg["run"]["cache_dir"])
    return path if path.is_absolute() else ROOT / path


def cache_dir(cfg: dict | None = None) -> Path:
    """Kept for callers written against the old name."""
    return model_dir(cfg)


def manifest_path(cfg: dict | None = None) -> Path:
    cfg = cfg or load_config()
    return model_dir(cfg) / cfg["storage"].get("manifest", "manifest.json")


def manifest(cfg: dict | None = None) -> dict | None:
    try:
        return json.loads(manifest_path(cfg).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def venv_python(cfg: dict | None = None) -> Path:
    cfg = cfg or load_config()
    return ROOT / cfg["env"]["venv"] / "bin" / "python"


# --------------------------------------------------------------------------
# what is installed
# --------------------------------------------------------------------------
def probe() -> dict:
    found = {}
    for name in ("torch", "transformers", "safetensors", "boto3"):
        try:
            found[name] = importlib.util.find_spec(name) is not None
        except (ImportError, ValueError):
            found[name] = False
    found["weights"] = weights_present()
    found["venv"] = venv_python().exists()
    return found


def weights_present(cfg: dict | None = None) -> bool:
    """Every required file, with the size the manifest recorded for it.

    Existence alone is not enough: an interrupted 558 MB download leaves a file
    of the right name and the wrong length, and that fails at load time with an
    error that says nothing about the download.
    """
    cfg = cfg or load_config()
    base = model_dir(cfg)
    sizes = {row["name"]: row.get("bytes") for row in
             (manifest(cfg) or {}).get("files", [])}
    for name in cfg["model"]["files"]:
        path = base / name
        if not path.is_file() or path.stat().st_size == 0:
            return False
        want = sizes.get(name)
        if want and path.stat().st_size != want:
            return False
    return True


def weights_size_mb(cfg: dict | None = None) -> float:
    base = model_dir(cfg)
    return round(sum(p.stat().st_size for p in base.glob("*") if p.is_file())
                 / (1024 * 1024), 1)


def model_identity(cfg: dict | None = None) -> dict:
    """What the service is actually running, not what the config wishes it ran.

    Read from the manifest that shipped with the weights, so a cache left over
    from a different checkpoint is reported as that checkpoint.
    """
    cfg = cfg or load_config()
    doc = manifest(cfg) or {}
    return {"model": doc.get("model") or cfg["model"]["id"],
            "revision": doc.get("revision") or cfg["model"]["revision"],
            "license": doc.get("license") or cfg["model"].get("license", ""),
            "dir": str(model_dir(cfg))}


def ensure_environment(argv: list[str]) -> None:
    """Re-run inside `.venv/gec` when the model's dependencies live there.

    A 2 GB dependency does not belong in the system Python of a project whose
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
# install
# --------------------------------------------------------------------------
def install(cfg: dict | None = None, from_hub: bool = False) -> int:
    """Fetch the checkpoint into the cache and write its manifest.

    ArvanCloud first: the bucket is the copy this project owns, it is in Iran,
    and the server should not need hf.co on every rebuild. Hugging Face is the
    fallback only when asked for.
    """
    cfg = cfg or load_config()
    dest = model_dir(cfg)
    dest.mkdir(parents=True, exist_ok=True)
    tools = str(Path(__file__).resolve().parent)
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import gec_store

    if not from_hub:
        try:
            code = gec_store.download(cfg, dest)
            if code == 0:
                return 0
        except Exception as exc:
            print(f"  storage unavailable ({exc}); trying Hugging Face", file=sys.stderr)

    from huggingface_hub import snapshot_download

    patterns = list(cfg["model"]["files"]) + [cfg["model"].get("attribution", "README.md")]
    print(f"  fetching {cfg['model']['id']} @ {cfg['model']['revision']} from Hugging Face")
    snapshot_download(repo_id=cfg["model"]["id"], revision=cfg["model"]["revision"],
                      local_dir=str(dest), allow_patterns=patterns)
    doc = gec_store.build_manifest(cfg, dest)
    (dest / cfg["storage"]["manifest"]).write_text(json.dumps(doc, indent=1),
                                                  encoding="utf-8")
    print(f"PASS  {len(doc['files'])} files, {doc['total_bytes'] / 1048576:.1f} MB "
          f"in {dest}")
    return 0


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
            "GEC-BART needs " + " and ".join(missing) + ":\n"
            "    pip install torch --index-url https://download.pytorch.org/whl/cpu\n"
            "    pip install transformers safetensors\n"
            "  or keep them in the project venv: .venv/gec\n"
            "  `python3 tools/gec.py --check` shows the current state."
        )
    if not weights_present(cfg):
        raise RuntimeError(
            f"the checkpoint is not in {model_dir(cfg)} - install it with\n"
            "    python3 tools/gec.py --install\n"
            "  (or `python3 tools/gec_store.py --check` to see the storage state)")

    # Everything is local by now, so nothing should reach the network - not
    # even a revision check. This has to happen before transformers is
    # imported: huggingface_hub reads the flag when it loads.
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

    from transformers import AutoTokenizer, BartForConditionalGeneration

    started = time.time()
    where = str(model_dir(cfg))
    _TOKENIZER = AutoTokenizer.from_pretrained(where, local_files_only=True)
    _MODEL = BartForConditionalGeneration.from_pretrained(where, local_files_only=True)
    _MODEL.eval()
    _LOADED_AT = round(time.time() - started, 2)
    return _MODEL, _TOKENIZER


def load_seconds() -> float:
    return _LOADED_AT


def load_fixes() -> list[dict]:
    """Deterministic rules that run before and after the model.

    They are model-agnostic error classes that are cheap to state as a rule and
    expensive to leave to a corrector - pronoun case, "It is me", "I wish I
    was", have + simple past. gec_fixes.json is data, not a model dependency.
    A rule that does not compile is skipped rather than taking the sentence
    down with it.
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
        return ("That sentence is mostly Persian, and GEC-BART was trained on "
                "English. Send an English sentence. / جملهٔ انگلیسی بفرست.")
    limit = int(cfg["run"]["max_input_words"])
    words = len(text.split())
    if words > limit:
        return (f"{words} words is past the {limit}-word limit — a corrector "
                "degrades on a sentence longer than that.")
    return None


def correct(sentence: str, cfg: dict | None = None) -> dict:
    """One sentence in, one correction out, plus what it cost.

    Returns {"input", "output", "changed", "refused", "seconds"} so callers (the
    CLI, webapp's /api/correct, the worker, the chat's second opinion) never
    parse a printed line.
    """
    cfg = cfg or load_config()
    text = " ".join((sentence or "").split())
    reason = refuse(text, cfg)
    if reason:
        return {"input": text, "output": "", "changed": False,
                "refused": reason, "seconds": 0.0}
    model, tokenizer = load_model(cfg)
    started = time.time()
    # Rules first: a pronoun fixed before the model is asked is one it cannot
    # get wrong, and the model then has less to do.
    cleaned = apply_fixes(text)
    prefix = cfg["model"].get("prefix", "")
    batch = tokenizer([prefix + cleaned], return_tensors="pt", truncation=True,
                      max_length=cfg["run"]["max_length"])
    import torch

    with _GENERATE, torch.inference_mode():
        ids = model.generate(
            input_ids=batch["input_ids"],
            attention_mask=batch["attention_mask"],
            max_length=cfg["run"]["max_length"],
            min_length=cfg["run"]["min_length"],
            num_beams=cfg["run"]["num_beams"],
            early_stopping=cfg["run"]["early_stopping"],
            length_penalty=cfg["run"]["length_penalty"],
            no_repeat_ngram_size=cfg["run"]["no_repeat_ngram_size"],
        )
    # clean_up_tokenization_spaces is what puts " ." and "n't" back together:
    # without it every answer reads as "She went to school yesterday ."
    out = tokenizer.decode(ids[0], skip_special_tokens=True,
                           clean_up_tokenization_spaces=True)
    out = apply_fixes(" ".join(out.split()))
    elapsed = round(time.time() - started, 3)
    return {"input": text, "output": out, "changed": not equivalent(out, text),
            "refused": None, "seconds": elapsed}


# --------------------------------------------------------------------------
# the chat's opt-in second opinion
# --------------------------------------------------------------------------
def second_opinion(sentence: str, cfg: dict | None = None) -> str:
    """The corrected sentence, or "" - and only when FLUENTIFY_GEC asks for it.

    The flag exists because a correction line in every grammar reply would put
    the CLI and the rule engine of the APK out of step: the APK carries no
    model, and `tests_js_vs_python.py` holds the two engines to the same words.
    Off by default, so the shipped conversation is the one that ships.

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
        try:
            row = correct(text, cfg)
        except RuntimeError:
            row = {"output": "", "changed": False}
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
            capture_output=True, text=True, timeout=300,
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


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def report(cfg: dict) -> int:
    have = probe()
    ident = model_identity(cfg)
    print("GEC-BART Base — grammatical error correction on this machine")
    print(f"  model      {ident['model']} @ {ident['revision']}")
    print(f"  licence    {ident['license']} · {cfg['model'].get('architecture', '')}")
    print(f"  cache      {ident['dir']}")
    print(f"  storage    s3://{cfg['storage']['bucket']}/{cfg['storage']['prefix']}")
    for name in ("torch", "transformers", "safetensors", "boto3"):
        print(f"  {name:<10} {'installed' if have[name] else 'missing'}")
    if have["weights"]:
        print(f"  weights    present ({weights_size_mb(cfg)} MB, offline)")
    else:
        where = model_dir(cfg)
        print(f"  weights    not installed ({where})")
        print("             python3 tools/gec.py --install")
    print(f"  venv       {venv_python(cfg)}"
          f"{'' if have['venv'] else ' (absent)'}")
    print(f"  surfaces   /api/correct on this server, the CLI, and the chat's "
          f"second opinion with {cfg['env']['flag']}=1")
    if not (have["torch"] and have["transformers"]):
        print("\n  Install the dependencies:")
        print("    python3 -m venv .venv/gec")
        print("    .venv/gec/bin/pip install torch --index-url "
              "https://download.pytorch.org/whl/cpu")
        print("    .venv/gec/bin/pip install transformers safetensors boto3")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    cfg = load_config()
    parser = argparse.ArgumentParser(
        description="Correct English sentences with GEC-BART Base (gotutiyan/gec-bart-base).")
    parser.add_argument("sentence", nargs="*", help="the sentence to correct")
    parser.add_argument("--check", action="store_true",
                        help="report the model, the dependencies and the cache")
    parser.add_argument("--install", action="store_true",
                        help="fetch the checkpoint into the cache")
    parser.add_argument("--from-hub", action="store_true",
                        help="with --install: use Hugging Face instead of object storage")
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
    if args.install:
        return install(cfg, from_hub=args.from_hub)
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

    try:
        rows = [correct(line, cfg) for line in lines]
    except RuntimeError as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 3
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
    "She go to school yesterday.",
    "He don't like coffee.",
    "I has a book.",
    "They was happy.",
    "I like to swimming",
    "I have went there",
    "She have a car",
    "I have many informations",
    "I am agree with you",
    "despite of the rain we went out",
    # already correct: a corrector that rewrites good English is worse than none
    "She speaks English very well.",
    "She watches TV every day",
    "The book is on the table",
    "I have seen him before",
]


def bench(cfg: dict, as_json: bool = False) -> int:
    """Sentences whose answers are already known, timed."""
    try:
        rows = [correct(s, cfg) for s in BENCH]
    except RuntimeError as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 3
    if as_json:
        print(json.dumps({"load_seconds": load_seconds(),
                          "identity": model_identity(cfg), "rows": rows},
                         ensure_ascii=False, indent=1))
        return 0
    print(f"load {load_seconds()}s · {model_identity(cfg)['model']}")
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
