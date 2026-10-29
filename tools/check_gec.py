#!/usr/bin/env python3
"""The grammar corrector: GEC-BART Base, server-side, and absent from the app.

The model is a 558 MB BART, which makes it the one thing in this repo that
needs torch and the one thing that cannot ship in an APK. This suite is what
keeps it on the right side of both:

  config      gec.json names gotutiyan/gec-bart-base at a pinned revision, MIT,
              asks for safetensors and not the duplicate pytorch_model.bin, and
              carries no "enabled" switch for the chat path
  storage     the ArvanCloud location is the bucket the model was uploaded to,
              credentials are never read from a tracked file, and a missing key
              is a message rather than a traceback
  tool        `--check` reports without a model, and a request it cannot answer
              is refused *before* 558 MB is loaded
  guards      empty, Persian and over-long input are turned away with a reason
  default path with FLUENTIFY_GEC unset the chat reply is the rule-based one,
              and torch is never imported
  invisible   bot.js, the built page and the Kotlin name no checkpoint and hold
              no weights - there is no .onnx, no .safetensors, no inference
              runtime in the APK, and the page asks an endpoint instead
  wireless    the pen button still spends no daily message

When the checkpoint is installed it also runs the bench and the 73-sentence
corpus through the real model, because a suite that only reads config would
pass against a cache that cannot load.

    python3 tools/check_gec.py
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "gec.json"
GEC = ROOT / "tools/gec.py"
STORE = ROOT / "tools/gec_store.py"
WEBAPP = ROOT / "webapp.py"
BOT = ROOT / "android/app/src/main/assets/www/bot.js"
BUILT = ROOT / "android/app/src/main/assets/www/index.html"
ASSETS = ROOT / "android/app/src/main/assets/www"
KOTLIN = ROOT / "android/app/src/main/java"

MODEL_ID = "gotutiyan/gec-bart-base"
PREFIX = "GEC-BART BASE/"
FLAG = "FLUENTIFY_GEC"
checks = 0
failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> bool:
    global checks
    checks += 1
    if not ok:
        failures.append(label + (f" — {detail}" if detail else ""))
    return bool(ok)


def fail(message: str) -> None:
    global checks
    checks += 1
    failures.append(message)


def summary_line() -> str:
    return (f"{checks - len(failures)}/{checks} checks over gec.json, the storage "
            f"location, the tool's guards and the shipped surfaces")


# --------------------------------------------------------------------------
# config
# --------------------------------------------------------------------------
def run_config() -> dict:
    check("gec.json exists", CONFIG.exists())
    if not CONFIG.exists():
        fail("gec.json is missing, so nothing can read the model's settings")
        return {}
    try:
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"gec.json does not parse: {exc}")
        return {}

    for key in ("model", "storage", "run", "env"):
        check(f"gec.{key} present", key in cfg)

    model = cfg.get("model", {})
    check("the checkpoint is GEC-BART Base", model.get("id") == MODEL_ID,
          str(model.get("id")))
    revision = str(model.get("revision", ""))
    check("the revision is pinned to a commit", bool(re.fullmatch(r"[0-9a-f]{40}", revision)),
          revision or "(unset) - 'main' can move under a running service")
    check("the licence is recorded", model.get("license") == "MIT",
          str(model.get("license")))
    check("the architecture is BART's",
          model.get("architecture") == "BartForConditionalGeneration",
          str(model.get("architecture")))
    files = model.get("files", [])
    check("safetensors is the weights file", "model.safetensors" in files, str(files))
    check("the duplicate pytorch_model.bin is not fetched",
          "pytorch_model.bin" not in files, str(files))
    for name in ("config.json", "tokenizer.json", "vocab.json", "merges.txt",
                 "tokenizer_config.json"):
        check(f"the tokenizer needs {name}", name in files)
    check("no prefix is invented for this checkpoint", model.get("prefix", "") == "",
          repr(model.get("prefix")))
    check("the model card is kept as attribution",
          bool(model.get("attribution")), str(model.get("attribution")))

    store = cfg.get("storage", {})
    check("the storage region is ir-thr-at1", store.get("region") == "ir-thr-at1",
          str(store.get("region")))
    check("the storage bucket is the one the model was uploaded to",
          store.get("bucket") == "fluentify-bbc", str(store.get("bucket")))
    check("the storage prefix is the requested folder", store.get("prefix") == PREFIX,
          repr(store.get("prefix")))
    check("the endpoint is the S3 API, not the console",
          str(store.get("endpoint", "")).startswith("https://s3.") and
          "console" not in str(store.get("endpoint", "")), str(store.get("endpoint")))
    check("no credentials are stored in gec.json",
          not any("secret" in k.lower() or "access_key" in k.lower() for k in store),
          str(list(store)))

    run = cfg.get("run", {})
    check("beams between 1 and 10", 1 <= int(run.get("num_beams", 0)) <= 10,
          str(run.get("num_beams")))
    check("max_length within BART's 1024 positions",
          32 <= int(run.get("max_length", 0)) <= 1024, str(run.get("max_length")))
    check("a sentence limit below the token limit",
          5 <= int(run.get("max_input_words", 0)) <= 80,
          str(run.get("max_input_words")))
    cache = str(run.get("cache_dir", ""))
    check("the weights land in the gitignored cache", cache.startswith("tools/.cache/"),
          cache)
    check("generation is deterministic in cost (no sampling)",
          "do_sample" not in run and "temperature" not in run, str(sorted(run)))

    env = cfg.get("env", {})
    check("the venv is outside the repo", env.get("venv", "").startswith(".venv/"),
          str(env.get("venv")))
    check("the flag is the one chatbot.py reads", env.get("flag") == FLAG,
          str(env.get("flag")))
    check("the cache can be repointed at a server disk",
          bool(env.get("model_dir")), str(env.get("model_dir")))

    # The absence of this key is the point: a config switch would put a model
    # line in every grammar reply, which the APK cannot produce.
    check("gec.json carries no global enable switch", "enabled" not in cfg,
          "a global switch would drift the CLI from the APK")
    return cfg


# --------------------------------------------------------------------------
# storage
# --------------------------------------------------------------------------
def _env_file_values() -> dict:
    """The env file's KEY=VALUE pairs, read without printing any of them."""
    path = ROOT / "gec.json"
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
        env_file = ROOT / cfg.get("storage", {}).get("env_file", ".arvan-storage.env")
        pairs = {}
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                pairs[key.strip()] = value.strip()
        return pairs
    except (OSError, ValueError):
        return {}


def run_storage(cfg: dict) -> None:
    """The upload tool must be usable and must not leak what it is given."""
    check("tools/gec_store.py exists", STORE.exists())
    if not STORE.exists():
        return
    # Two states, both must be honest. The first run hides the keys *and* the
    # env file: a machine that has credentials must still be able to prove what
    # the missing-credential path says, because that is what a fresh checkout
    # and a misconfigured server both see.
    absent_env = {k: v for k, v in os.environ.items()
                  if k not in ("ARVAN_S3_ACCESS_KEY_ID", "ARVAN_S3_SECRET_ACCESS_KEY")}
    absent_env["ARVAN_S3_ENV_FILE"] = str(ROOT / "tools/.cache/no-such-storage.env")
    proc = subprocess.run([sys.executable, str(STORE), "--check"], cwd=ROOT,
                          capture_output=True, text=True, timeout=120, env=absent_env)
    out = proc.stdout + proc.stderr
    check("--check names the bucket and the folder",
          "fluentify-bbc" in out and PREFIX in out, out[:160])
    check("without credentials it says which keys to set",
          "ARVAN_S3_ACCESS_KEY_ID" in out, out[:160])
    check("without credentials it does not pretend to have uploaded",
          "PASS" not in out, out[:160])
    check("without credentials it does not raise",
          "Traceback" not in out, out[-160:])

    # Second run, real settings: if this machine has keys, the bucket has to
    # answer; if it has none, the message is the truthful one.
    proc = subprocess.run([sys.executable, str(STORE), "--check"], cwd=ROOT,
                          capture_output=True, text=True, timeout=120)
    live = proc.stdout + proc.stderr
    if proc.returncode == 0:
        check("with credentials, the bucket is reachable", "PASS" in live, live[-200:])
    else:
        check("with no credentials on the machine, --check says so",
              "ARVAN_S3_ACCESS_KEY_ID" in live, live[:160])
    for source in (os.environ, _env_file_values()):
        secret = source.get("ARVAN_S3_SECRET_ACCESS_KEY", "")
        if secret:
            check("the secret is never printed", secret not in live)

    # Uploading is opt-in by invoking the tool, never a side effect of a test.
    check("the upload tool does not run on import",
          "upload(" not in (STORE.read_text(encoding="utf-8").split('if __name__')[0]
                            .split("def upload")[0]), "an import must not upload")


# --------------------------------------------------------------------------
# the tool, without a model
# --------------------------------------------------------------------------
def run_tool(cfg: dict) -> None:
    def call(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(GEC), *args], cwd=ROOT,
                              capture_output=True, text=True, timeout=180,
                              env={k: v for k, v in os.environ.items() if k != FLAG})

    proc = call("--check")
    check("--check exits 0", proc.returncode == 0, proc.stderr.strip()[-200:])
    out = proc.stdout
    check("--check names the checkpoint", MODEL_ID in out)
    check("--check names the pinned revision",
          str(cfg.get("model", {}).get("revision", "")) in out)
    check("--check names the venv it will use", ".venv/" in out)
    check("--check names the storage location",
          "fluentify-bbc" in out and PREFIX in out)
    check("--check names the opt-in flag", FLAG in out)
    check("--check points at the cache", "tools/.cache/gec-bart" in out)

    proc = call()
    check("no sentence is a usage error, not a crash", proc.returncode == 2,
          str(proc.returncode))

    proc = call("--help")
    check("--help works and names the model",
          proc.returncode == 0 and "GEC-BART" in proc.stdout, proc.stdout[:120])


# --------------------------------------------------------------------------
# the guards, which must answer before the model is loaded
# --------------------------------------------------------------------------
def run_guards(cfg: dict) -> None:
    if str(ROOT / "tools") not in sys.path:
        sys.path.insert(0, str(ROOT / "tools"))
    try:
        import gec
    except Exception as exc:  # pragma: no cover - the tool must import cleanly
        fail(f"tools/gec.py does not import: {exc}")
        return

    rows = {
        "empty": gec.correct("   ", cfg),
        "persian": gec.correct("این جمله فارسی است", cfg),
        "mostly persian": gec.correct("I said سلام و درود به همه دوستان امروز", cfg),
        "too long": gec.correct(" ".join(["word"] * 80), cfg),
    }
    for label, row in rows.items():
        check(f"{label} input is refused", bool(row.get("refused")), str(row)[:120])
        check(f"{label} refusal is explained, not silent",
              len(row.get("refused") or "") > 10, str(row.get("refused")))
    check("no refusal loaded the model", gec._MODEL is None)

    check("a plain English sentence passes the guards",
          gec.refuse("he don't like it", cfg) is None,
          str(gec.refuse("he don't like it", cfg)))
    check("the configured cache is where the loader looks",
          gec.model_dir(cfg) == ROOT / cfg["run"]["cache_dir"], str(gec.model_dir(cfg)))
    check("the identity reports the pinned model",
          gec.model_identity(cfg)["model"] == MODEL_ID,
          str(gec.model_identity(cfg)))


# --------------------------------------------------------------------------
# the default path: the chat the app ships
# --------------------------------------------------------------------------
def run_default(cfg: dict) -> None:
    os.environ.pop(FLAG, None)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import chatbot

    check("with no flag, the second opinion is empty",
          chatbot.second_opinion("I have went there") == "")
    check("with no flag, torch is never imported", "torch" not in sys.modules)

    reply = chatbot.ChatBot().respond("is this correct? I have went there")
    check("the rule-based reply is unchanged", "One thing to fix" in reply,
          reply[:120])
    check("no model line on the default path", "🧠" not in reply, reply[:120])
    check("the corrected verb still comes from the rule set", "have gone" in reply,
          reply[:160])


# --------------------------------------------------------------------------
# the opt-in path: on when asked, and safe when the model is absent
# --------------------------------------------------------------------------
def run_optin(cfg: dict) -> None:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import chatbot

    os.environ[FLAG] = "1"
    try:
        line = chatbot.second_opinion("I have went there")
        check("with the flag, asking never raises", isinstance(line, str))
        if line:
            check("an opt-in line is labelled", "🧠" in line, line[:80])
            check("an opt-in line carries a participle correction",
                  any(w in line.lower() for w in ("have gone", "have been")),
                  line[:120])
        else:
            check("no model, no line", True)
            print("  (no model environment: the opt-in path returned nothing, "
                  "which is what it must do)")
        wrong = chatbot.second_opinion("این جمله فارسی است")
        check("the opt-in path still refuses Persian", wrong == "", wrong[:80])
    finally:
        os.environ.pop(FLAG, None)

    reply = chatbot.ChatBot().respond("is this correct? I have went there")
    check("the flag's effect ended with the flag", "🧠" not in reply, reply[:120])


# --------------------------------------------------------------------------
# invisible: the shipped app carries no model
# --------------------------------------------------------------------------
MARKERS = ("gotutiyan", "safetensors", "gec-bart-base", "GECWeb", "onnxruntime",
           FLAG)
WEIGHT_SUFFIXES = (".onnx", ".safetensors", ".wasm", ".bin", ".pt")


def run_invisible() -> None:
    for path in (BOT, BUILT):
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for marker in MARKERS:
            # The offline page names FLUENTIFY_GEC_API - the build-time backend
            # hook - and that is deliberately not the chat's opt-in flag, so the
            # flag is matched as a whole word rather than as a prefix.
            hit = (re.search(r"\bFLUENTIFY_GEC\b(?!_)", text) if marker == FLAG
                   else marker in text)
            check(f"{path.name} does not mention {marker}", not hit)
    if KOTLIN.exists():
        for path in KOTLIN.rglob("*.kt"):
            text = path.read_text(encoding="utf-8", errors="replace")
            for marker in MARKERS:
                hit = (re.search(r"\bFLUENTIFY_GEC\b(?!_)", text) if marker == FLAG
                       else marker in text)
                check(f"{path.name} does not mention {marker}", not hit)
            check(f"{path.name} loads no model", "onnx" not in text.lower())

    check("the old asset directory is gone", not (ASSETS / "gec").exists(),
          "android/app/src/main/assets/www/gec still exists")
    weights = [p.relative_to(ROOT) for p in ASSETS.rglob("*")
               if p.suffix in WEIGHT_SUFFIXES]
    check("the APK bundle holds no model weights", not weights, str(weights[:3]))
    size = sum(p.stat().st_size for p in ASSETS.rglob("*") if p.is_file())
    check("the offline bundle is the app, not the model (< 60 MB)",
          size < 60 * 1024 * 1024, f"{size / 1048576:.1f} MB")

    # The phone must not be handed a loopback address: it cannot reach this
    # machine, and a silent failure there is a correction that never arrives.
    if BUILT.exists():
        match = re.search(r"const GEC_API = '([^']*)'", BUILT.read_text(encoding="utf-8"))
        check("the offline page has a corrector entry point", bool(match),
              "no GEC_API in the built page")
        if match and match.group(1):
            check("a configured backend is https, not a local address",
                  match.group(1).startswith("https://") and
                  not any(h in match.group(1) for h in ("127.0.0.1", "localhost")),
                  match.group(1))


def run_web() -> None:
    """The preview hosts the model; the offline page must not pretend to."""
    if not WEBAPP.exists():
        return
    text = WEBAPP.read_text(encoding="utf-8", errors="replace")
    check("the preview serves a correction endpoint", '"/api/correct"' in text)
    check("the preview runs the model as a resident worker",
          "gec_worker.py" in text and "class LocalGec" in text)
    # A server with keys and an empty disk must serve without the checkpoint
    # being committed or copied there by hand: the install is the service's job.
    check("the server installs the checkpoint from storage at boot",
          "def prefetch" in text and "gec.prefetch()" in text and
          "def _install" in text, "webapp.py does not fetch the model itself")
    check("a failed install is a message, not a crash",
          "could not be installed from storage" in text)
    check("the bind address is configurable for a deployed backend",
          "FLUENTIFY_HOST" in text)
    check("the page asks the endpoint instead of loading weights",
          "fetch('/api/correct" in text and "window.GECWeb" not in text)
    check("the old model route is gone", '"/gec/"' not in text,
          "webapp.py still serves /gec/")
    check("the pen button is still wired", 'id="gecbtn"' in text)
    check("the pen does not spend one of the daily messages",
          "Seed.add" not in text.split("async function checkEnglish")[1].split("\n}")[0])
    check("a model failure is JSON, not a traceback",
          "The correction model failed" in text)

    if BUILT.exists():
        built = BUILT.read_text(encoding="utf-8", errors="replace")
        check("the offline page routes the pen through correctSentence",
              "correctSentence(text)" in built)
        check("the offline page no longer fetches the endpoint directly",
              "fetch('/api/correct" not in built, "the fetch survived the build")


# --------------------------------------------------------------------------
# the real model, when it is here
# --------------------------------------------------------------------------
BROKEN = {
    "She go to school yesterday.": ("went",),
    "He don't like coffee.": ("doesn't", "does not"),
    "I has a book.": ("have a book",),
    "They was happy.": ("were",),
    "I like to swimming": ("like swimming",),
}
CORRECT = ["She speaks English very well.", "She watches TV every day",
           "The book is on the table", "I have seen him before"]


def run_model(cfg: dict) -> None:
    proc = subprocess.run([sys.executable, str(GEC), "--bench", "--json"], cwd=ROOT,
                          capture_output=True, text=True, timeout=600,
                          env={k: v for k, v in os.environ.items()
                               if k.lower() != "all_proxy"})
    if proc.returncode != 0:
        fail("the bench did not run: "
             + (proc.stderr.strip().splitlines() or ["no output"])[-1])
        return
    try:
        data = json.loads(proc.stdout[proc.stdout.index("{"):])
    except ValueError:
        fail("the bench did not print JSON")
        return
    rows = {r["input"].lower(): r for r in data["rows"]}

    identity = data.get("identity", {})
    check("the loaded checkpoint is the pinned one",
          identity.get("model") == MODEL_ID and
          str(identity.get("revision")) == str(cfg["model"]["revision"]),
          str(identity))
    check("the model reports how long it took to load",
          0 < data.get("load_seconds", 0) < 300, str(data.get("load_seconds")))
    for sentence, wants in BROKEN.items():
        row = rows.get(sentence.lower())
        if not row:
            fail(f"the bench lost the sentence {sentence!r}")
            continue
        out = row["output"].lower()
        check(f"{sentence!r} is corrected", row["changed"], repr(row["output"]))
        check(f"{sentence!r} is corrected the right way",
              any(w in out for w in wants), repr(row["output"]))
        # BART's byte-level decode leaves " ." and "does n't" unless the
        # tokenizer is asked to clean up. That shipped once as
        # "She went to school yesterday ." and looks like broken English.
        check(f"{sentence!r} is decoded cleanly",
              " ." not in row["output"] and " n't" not in row["output"],
              repr(row["output"]))
    for sentence in CORRECT:
        row = rows.get(sentence.lower())
        if not row:
            fail(f"the bench lost the sentence {sentence!r}")
            continue
        check(f"correct English is left alone: {sentence!r}", not row["changed"],
              repr(row["output"]))

    import gec
    check("a closing full stop is not counted as a correction",
          gec.equivalent("The book is on the table", "The book is on the table."))
    check("a capitalised first word is not counted as a correction",
          gec.equivalent("he is here", "He is here."))
    check("a real repair is still a change",
          not gec.equivalent("I like to swimming", "I like swimming."))
    print(f"  model load {data['load_seconds']}s, "
          f"{sum(r['seconds'] for r in data['rows']):.2f}s for {len(data['rows'])} sentences")


CORPUS = ROOT / "tools/gec_corpus.json"


def run_corpus() -> None:
    """Every error class the app promises to correct, not eleven sentences."""
    if not CORPUS.exists():
        return
    rows = json.loads(CORPUS.read_text(encoding="utf-8"))
    proc = subprocess.run(
        [sys.executable, str(GEC), "--stdin", "--json"], cwd=ROOT,
        input="\n".join(r[1] for r in rows), capture_output=True, text=True,
        timeout=900, env={k: v for k, v in os.environ.items()
                          if k.lower() != "all_proxy"})
    if proc.returncode != 0:
        check("the corpus run completed", False,
              (proc.stderr or proc.stdout or "").strip()[:200])
        return
    text = proc.stdout
    try:
        results = json.loads(text)
    except ValueError:
        start = text.find("[")
        results = json.loads(text[start:]) if start >= 0 else []
    if not results:
        check("the corpus produced answers", False, "no rows came back")
        return
    ok, misses = 0, []
    for (cat, wrong, keys), row in zip(rows, results):
        out = (row.get("output") or "").lower()
        if any(k.lower() in out for k in keys):
            ok += 1
        else:
            misses.append(f"[{cat}] {wrong!r}")
    check(f"the corrector handles the {len(rows)}-sentence corpus",
          ok / len(rows) >= 0.9,
          f"{ok}/{len(rows)}; missed {', '.join(misses[:4])}")
    print(f"  corpus {ok}/{len(rows)}")


def weights_here() -> bool:
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        import gec
        return gec.weights_present()
    except Exception:
        return False


# --------------------------------------------------------------------------
def main() -> int:
    print("Grammar correction — GEC-BART Base, server-side\n")
    cfg = run_config()
    if cfg:
        run_storage(cfg)
        run_tool(cfg)
        run_guards(cfg)
        run_default(cfg)
        run_optin(cfg)
        run_invisible()
        run_web()
        if weights_here():
            run_model(cfg)
            run_corpus()
        else:
            print("  (checkpoint not installed: the inference checks were skipped — "
                  "run `python3 tools/gec.py --install` once to fetch it)")

    print()
    if failures:
        print(f"FAIL  {len(failures)} of {checks} checks failed")
        for message in failures:
            print(f"  ✗ {message}")
        return 1
    print(f"PASS  {summary_line()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
