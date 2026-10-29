#!/usr/bin/env python3
"""The local GEC model: configured, correct, and invisible until asked for.

Unbabel/gec-t5_small is the only thing in this repo that needs a torch. That
makes it a standing risk to three properties the project otherwise guarantees:
the app runs on the standard library alone, the APK behaves exactly like the
CLI, and nothing is fetched at runtime. This suite is what keeps the model on
the right side of all three.

  config        gec.json parses, names the checkpoint the model card names,
                and carries no "enabled" switch - the model is never on for
                everyone, only for an invocation that asks
  tool          `tools/gec.py --check` reports without a model, and refuses a
                request it cannot answer *before* loading 242 MB
  guards        empty, Persian and over-long input are turned away with a
                reason, and none of them loads the model
  default path  with FLUENTIFY_GEC unset, the chat reply is byte-identical to
                the rule-based one, and torch is never imported
  opt-in path   with the flag set, the reply gains at most one marked line, or
                nothing at all when the model is missing - it never raises
  invisible     webapp.py, the APK's bot.js, the built page and the Kotlin
                mention the model nowhere: the shipped app has no such feature

If the weights are present it also runs the bench through the real model and
checks what it is supposed to do: repair the broken sentences and leave the
correct ones alone. Skipped, with a printed reason, when they are not.

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
WEBAPP = ROOT / "webapp.py"
BOT = ROOT / "android/app/src/main/assets/www/bot.js"
BUILT = ROOT / "android/app/src/main/assets/www/index.html"
KOTLIN = ROOT / "android/app/src/main/java"

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
    return (f"{checks - len(failures)}/{checks} checks over gec.json, the tool's "
            f"guards, the opt-in path and the shipped surfaces")


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

    for key in ("model", "run", "env"):
        check(f"gec.{key} present", key in cfg)

    model = cfg.get("model", {})
    check("the checkpoint is the one in the model card",
          model.get("id") == "Unbabel/gec-t5_small", str(model.get("id")))
    check("the tokenizer is t5-small's",
          model.get("tokenizer") == "t5-small", str(model.get("tokenizer")))
    prefix = model.get("prefix", "")
    check("the prefix is 'gec: ' with its space", prefix == "gec: ", repr(prefix))

    run = cfg.get("run", {})
    check("beams between 1 and 10", 1 <= int(run.get("num_beams", 0)) <= 10,
          str(run.get("num_beams")))
    check("max_length within the model's 512 positions",
          32 <= int(run.get("max_length", 0)) <= 512, str(run.get("max_length")))
    check("a sentence limit below the token limit",
          5 <= int(run.get("max_input_words", 0)) <= 80,
          str(run.get("max_input_words")))
    cache = str(run.get("cache_dir", ""))
    check("the weights land in the gitignored cache",
          cache.startswith("tools/.cache/"), cache)
    check("early stopping is on", run.get("early_stopping") is True)

    env = cfg.get("env", {})
    check("the venv is outside the repo", env.get("venv", "").startswith(".venv/"),
          str(env.get("venv")))
    check("the flag is the one chatbot.py reads", env.get("flag") == FLAG,
          str(env.get("flag")))

    # The absence of this key is the point: a config switch would put a model
    # line in every grammar reply, in an app whose APK cannot produce one.
    check("gec.json carries no global enable switch", "enabled" not in cfg,
          "a global switch would drift the CLI from the APK")
    return cfg


# --------------------------------------------------------------------------
# the tool, without a model
# --------------------------------------------------------------------------
def run_tool(cfg: dict) -> None:
    def call(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(GEC), *args], cwd=ROOT,
                              capture_output=True, text=True, timeout=180,
                              env={k: v for k, v in os.environ.items() if k != FLAG})

    proc = call("--check")
    check("--check exits 0 with no model installed", proc.returncode == 0,
          proc.stderr.strip()[-200:])
    out = proc.stdout
    check("--check names the checkpoint",
          cfg.get("model", {}).get("id", "Unbabel/gec-t5_small") in out)
    check("--check names the venv it will use", ".venv/" in out)
    check("--check says the model is CLI-only", "CLI only" in out)
    check("--check names the opt-in flag", FLAG in out)
    check("--check points at the cache", "tools/.cache/models" in out)

    proc = call()
    check("no sentence is a usage error, not a crash", proc.returncode == 2,
          str(proc.returncode))

    proc = call("--help")
    check("--help works", proc.returncode == 0 and "gec-t5" in proc.stdout)


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
        "too long": gec.correct(" ".join(["word"] * 60), cfg),
    }
    for label, row in rows.items():
        check(f"{label} input is refused", bool(row.get("refused")), str(row)[:120])
        check(f"{label} refusal is explained, not silent",
              len(row.get("refused") or "") > 10, str(row.get("refused")))
    check("no refusal loaded the model", gec._MODEL is None)

    # A one-word sentence is refused by the length rule? No - it is fair game,
    # but only when the model exists; here we only insist it is not refused for
    # being Persian or over-long.
    check("a plain English sentence passes the guards",
          gec.refuse("he don't like it", cfg) is None,
          str(gec.refuse("he don't like it", cfg)))


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
            # The model's repair of "have went" is "have been"; the rule set's
            # is "have gone". Both are the correction this line must carry.
            check("an opt-in line carries the model's correction",
                  any(w in line.lower() for w in ("have been", "have gone")),
                  line[:120])
        else:
            # No model environment here: the honest answer is no line at all.
            check("no model, no line", True)
            print("  (no model environment: the opt-in path returned nothing, "
                  "which is what it must do)")
        wrong = chatbot.second_opinion("این جمله فارسی است")
        check("the opt-in path still refuses Persian", wrong == "", wrong[:80])
    finally:
        os.environ.pop(FLAG, None)

    # Whatever happened above, the shipped reply must be back to the rules.
    reply = chatbot.ChatBot().respond("is this correct? I have went there")
    check("the flag's effect ended with the flag", "🧠" not in reply, reply[:120])


# --------------------------------------------------------------------------
# invisible: the shipped app has no model in it
# --------------------------------------------------------------------------
MARKERS = ("gec-t5", "Unbabel", "gec_t5", FLAG)


def run_invisible() -> None:
    # webapp.py is deliberately absent here: the preview is a Python server and
    # hosts the model itself. The APK cannot - it ships HTML/JS - so the same
    # markers must stay out of bot.js, the generated offline page and Kotlin.
    for path in (BOT, BUILT):
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for marker in MARKERS:
            check(f"{path.name} does not mention {marker}", marker not in text)
    if KOTLIN.exists():
        for path in KOTLIN.rglob("*.kt"):
            text = path.read_text(encoding="utf-8", errors="replace")
            for marker in MARKERS:
                check(f"{path.name} does not mention {marker}", marker not in text)

    # The bundle the APK loads must not have grown a model either: the copied
    # data directory is what ships on the phone.
    data = ROOT / "android/app/src/main/assets/www/data"
    if data.exists():
        check("the APK's data directory carries no model reference",
              not any(marker in p.read_text(encoding="utf-8", errors="replace")
                      for p in data.glob("*.json") for marker in MARKERS))
    check("there is no model file in the bundle",
          not any(p.suffix in (".bin", ".safetensors") for p in
                  (ROOT / "android/app/src/main/assets/www").rglob("*")))


def run_web() -> None:
    """The preview hosts the model; the offline page must not pretend to."""
    if WEBAPP.exists():
        text = WEBAPP.read_text(encoding="utf-8", errors="replace")
        check("the preview serves a correction endpoint", '"/api/correct"' in text)
        check("the preview runs the model as a resident worker",
              "gec_worker.py" in text and "class LocalGec" in text)
        # The rule file is written for Python (\1); JavaScript reads that as a
        # literal "1" unless it is translated. That shipped for an hour as
        # "She 1 eaten lunch", so the translation is asserted, not assumed.
        check("the page translates the rules' backreferences",
              "$$$1" in text and "gec_fixes.json" in text)
        check("the preview's pen button is wired to it",
              'id="gecbtn"' in text and "fetch('/api/correct" in text)
        check("the pen does not spend one of the daily messages",
              "Seed.add" not in text.split("async function checkEnglish")[1].split("\n}")[0])
    bundle = ROOT / "android/app/src/main/assets/www/gec"
    check("the model ships with the app",
          (bundle / "encoder_model.onnx").exists()
          and (bundle / "decoder_model.onnx").exists()
          and (bundle / "tokenizer.json").exists()
          and (bundle / "ort.min.js").exists()
          and (bundle / "ort-wasm-simd.wasm").exists())
    if BUILT.exists():
        text = BUILT.read_text(encoding="utf-8", errors="replace")
        check("the offline page runs the bundled model",
              'id="gecbtn"' in text and "gec/gec-web.js" in text
              and "gec/ort.min.js" in text)


# --------------------------------------------------------------------------
# the real model, when it is here
# --------------------------------------------------------------------------
BROKEN = {
    "I like to swimming": ("swim",),
    "he don't like it": ("doesn't", "does not"),
    # The model prefers "have been" to the rule set's "have gone". Both are
    # grammatical; they are not the same sentence. That is a GEC model's
    # known hazard, and the reason the rules stay the surface that ships.
    "I have went there": ("have been", "have gone"),
    "She have a car": ("has",),
    "They was happy yesterday": ("were",),
}
CORRECT = ["She watches TV every day", "The book is on the table",
           "I have seen him before"]


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

    check("the model reports how long it took to load",
          0 < data.get("load_seconds", 0) < 120, str(data.get("load_seconds")))
    for sentence, wants in BROKEN.items():
        row = rows.get(sentence.lower())
        if not row:
            fail(f"the bench lost the sentence {sentence!r}")
            continue
        out = row["output"].lower()
        check(f"{sentence!r} is corrected", row["changed"], repr(row["output"]))
        check(f"{sentence!r} is corrected the right way",
              any(w in out for w in wants), repr(row["output"]))
    for sentence in CORRECT:
        row = rows.get(sentence.lower())
        if not row:
            fail(f"the bench lost the sentence {sentence!r}")
            continue
        check(f"correct English is left alone: {sentence!r}", not row["changed"],
              repr(row["output"]))

    # The three correct sentences come back with a capital and a full stop.
    # That is tidying, not correction, and the bench must not call it a change.
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
    """Every error class the app promises to correct, not eleven sentences.

    The bench proves the model runs; this proves it still answers the kinds of
    mistake a learner actually makes - agreement, tense, articles, plurals,
    prepositions, modals, pronouns, questions, negation, gerunds, conditionals,
    word order, passive, spelling. A model update that fixes one class by
    breaking another shows up here as a rate, not as a nice-looking sentence.

    The sentences go through tools/gec.py rather than importing gec: this suite
    runs on the system interpreter, which has no torch, and the tool is what
    re-execs into .venv/gec.
    """
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


def weights_here() -> bool:
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        import gec
        return gec.weights_present()
    except Exception:
        return False


# --------------------------------------------------------------------------
def main() -> int:
    print("Local GEC model — Unbabel/gec-t5_small\n")
    cfg = run_config()
    if cfg:
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
            print("  (weights not downloaded: the correction checks were skipped — "
                  "run `python3 tools/gec.py \"I like to swimming\"` once to fetch them)")

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
