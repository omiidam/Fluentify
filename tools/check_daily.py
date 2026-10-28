#!/usr/bin/env python3
"""Daily English: is the catalogue sound, does every engine pick the same day?

The feature has three copies of one idea - which three items a local date gets:
daily_index() in chatbot.py, dailyIndex() in bot.js, and dayIndex() in the page.
Copying is what makes the offline APK work at all, and it is also how the three
drift apart without anybody noticing, so this suite ties them together:

  catalogue     every entry has the fields its renderer reads, ids are unique,
                English is English and Persian is Persian, no placeholders
  coverage      how long the rotation really runs before it reuses anything,
                reported as the numbers are - the catalogue does NOT hold 365
                distinct entries per category and this says so out loud
  rotation      each category steps through every entry before repeating, and
                the three engines pick the same item for 365 dates
  clock         the local date and the next-midnight timer across four
                timezones, including both 2026 daylight-saving changes, run in
                node with that zone as the process timezone
  store         completion survives a new day, a corrupt record does not throw,
                and an id that is no longer in the catalogue cannot tick a card
  wiring        the panel, its tile, the /api/daily route and the offline bundle
                all exist, and the built page carries the catalogue

    python3 tools/check_daily.py
"""

import json
import math
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
WEBAPP = ROOT / "webapp.py"
BOT = ROOT / "android/app/src/main/assets/www/bot.js"
BUILT = ROOT / "android/app/src/main/assets/www/index.html"
DATA = ROOT / "android/app/src/main/assets/www/data"
CACHE = ROOT / "tools/.cache"
CATALOGUE = ROOT / "daily.json"

KINDS = ("words", "expressions", "conversations")
LEVELS = {"A1", "A2", "B1", "B2", "C1", "C2"}
PLACEHOLDERS = ("lorem", "todo", "tbd", "xxx", "placeholder", "example.com",
                "fixme", "???")
PERSIAN = re.compile(r"[\u0600-\u06FF]")
LATIN = re.compile(r"[A-Za-z]")

problems: list[str] = []


def fail(what: str) -> None:
    problems.append(what)


def check(ok: bool, what: str) -> bool:
    if not ok:
        fail(what)
    return ok


def text_ok(value, where: str, *, lang: str, min_len: int = 1) -> bool:
    """A required string, in the script it claims to be in."""
    if not isinstance(value, str) or len(value.strip()) < min_len:
        fail(f"{where}: missing or too short ({value!r})")
        return False
    if lang == "en" and PERSIAN.search(value):
        fail(f"{where}: Persian text in an English field ({value[:40]!r})")
        return False
    if lang == "fa" and not PERSIAN.search(value):
        fail(f"{where}: no Persian in a Persian field ({value[:40]!r})")
        return False
    low = value.lower()
    for bad in PLACEHOLDERS:
        if bad in low:
            fail(f"{where}: placeholder text {bad!r}")
            return False
    return True


def pair_ok(value, where: str) -> bool:
    if not isinstance(value, dict):
        fail(f"{where}: expected {{en, fa}}")
        return False
    return text_ok(value.get("en"), f"{where}.en", lang="en") and \
        text_ok(value.get("fa"), f"{where}.fa", lang="fa")


def pair_list_ok(value, where: str, minimum: int, maximum: int = 99) -> bool:
    if not isinstance(value, list) or not (minimum <= len(value) <= maximum):
        fail(f"{where}: expected {minimum}-{maximum} rows, got "
             f"{len(value) if isinstance(value, list) else type(value).__name__}")
        return False
    ok = True
    for i, row in enumerate(value):
        ok = pair_ok(row, f"{where}[{i}]") and ok
    return ok


# --------------------------------------------------------------------------
#  catalogue
# --------------------------------------------------------------------------
def validate(cat: dict) -> None:
    for key in ("version",) + KINDS:
        if key not in cat:
            fail(f"daily.json: missing top-level {key!r}")
    if problems:
        return

    ids: dict[str, str] = {}
    seen_text: dict[str, set] = {k: set() for k in KINDS}

    for word in cat.get("words") or []:
        wid = word.get("id")
        where = f"word {wid}"
        if not check(isinstance(wid, str) and re.fullmatch(r"w\d{3,}", wid),
                     f"{where}: id should look like w001"):
            continue
        check(wid not in ids, f"{where}: duplicate id (also in {ids.get(wid)})")
        ids[wid] = "words"
        text_ok(word.get("en"), f"{where}.en", lang="en")
        text_ok(word.get("fa"), f"{where}.fa", lang="fa")
        text_ok(word.get("pos"), f"{where}.pos", lang="en")
        ipa = word.get("ipa") or ""
        check(isinstance(ipa, str) and ipa.startswith("/") and ipa.endswith("/")
              and len(ipa) > 2, f"{where}: ipa should be /…/ ({ipa!r})")
        check(word.get("level") in LEVELS, f"{where}: bad level {word.get('level')!r}")
        pair_ok(word.get("def"), f"{where}.def")
        pair_list_ok(word.get("examples"), f"{where}.examples", 2, 3)
        for field in ("syn", "ant"):
            row = word.get(field)
            if row is None:
                continue
            check(isinstance(row, list) and all(isinstance(x, str) and x.strip()
                                                for x in row),
                  f"{where}.{field}: should be a list of words")
        term = (word.get("en") or "").strip().lower()
        check(term not in seen_text["words"], f"{where}: duplicate word {term!r}")
        seen_text["words"].add(term)

    for expr in cat.get("expressions") or []:
        eid = expr.get("id")
        where = f"expression {eid}"
        if not check(isinstance(eid, str) and re.fullmatch(r"e\d{3,}", eid),
                     f"{where}: id should look like e001"):
            continue
        check(eid not in ids, f"{where}: duplicate id (also in {ids.get(eid)})")
        ids[eid] = "expressions"
        text_ok(expr.get("en"), f"{where}.en", lang="en")
        text_ok(expr.get("fa"), f"{where}.fa", lang="fa")
        check(expr.get("level") in LEVELS, f"{where}: bad level")
        check(expr.get("register") in {"casual", "neutral", "polite", "formal"},
              f"{where}: register {expr.get('register')!r} is not one the UI names")
        pair_ok(expr.get("use"), f"{where}.use")
        pair_ok(expr.get("when"), f"{where}.when")
        pair_list_ok(expr.get("examples"), f"{where}.examples", 2, 3)
        if expr.get("alt") is not None:
            pair_ok(expr.get("alt"), f"{where}.alt")
        term = (expr.get("en") or "").strip().lower()
        check(term not in seen_text["expressions"],
              f"{where}: duplicate expression {term!r}")
        seen_text["expressions"].add(term)

    for conv in cat.get("conversations") or []:
        cid = conv.get("id")
        where = f"conversation {cid}"
        if not check(isinstance(cid, str) and re.fullmatch(r"c\d{3,}", cid),
                     f"{where}: id should look like c001"):
            continue
        check(cid not in ids, f"{where}: duplicate id (also in {ids.get(cid)})")
        ids[cid] = "conversations"
        pair_ok(conv.get("topic"), f"{where}.topic")
        pair_ok(conv.get("setting"), f"{where}.setting")
        check(conv.get("level") in LEVELS, f"{where}: bad level")
        pair_list_ok(conv.get("turns"), f"{where}.turns", 6, 10)
        pair_list_ok(conv.get("key"), f"{where}.key", 3, 6)
        pair_list_ok(conv.get("notes"), f"{where}.notes", 1, 3)
        speakers = {(t.get("who") or "").strip()
                    for t in conv.get("turns") or [] if isinstance(t, dict)}
        check(len(speakers) >= 2, f"{where}: a dialogue needs two speakers, "
                                  f"found {sorted(speakers)}")
        # Alternate speakers: two lines in a row from one person is a
        # monologue with a label, not a conversation.
        speakers_in_order = [t.get("who") for t in conv.get("turns") or []]
        check(all(a != b for a, b in zip(speakers_in_order, speakers_in_order[1:])),
              f"{where}: the same speaker has two turns in a row")
        topic = ((conv.get("topic") or {}).get("en") or "").strip().lower()
        check(topic not in seen_text["conversations"],
              f"{where}: duplicate topic {topic!r}")
        seen_text["conversations"].add(topic)

    reported = cat.get("coverage")
    if isinstance(reported, dict):
        for kind in KINDS:
            check(reported.get(kind) == len(cat[kind]),
                  f"daily.json: coverage.{kind} claims {reported.get(kind)} "
                  f"but there are {len(cat[kind])}")


# --------------------------------------------------------------------------
#  coverage + rotation
# --------------------------------------------------------------------------
def coverage(cat: dict) -> dict:
    counts = {k: len(cat.get(k) or []) for k in KINDS}
    spans = {k: counts[k] for k in KINDS}
    triple = math.lcm(*[max(1, counts[k]) for k in KINDS])
    # Honest floors: the catalogue may grow, but it must not quietly shrink.
    # 24 conversations is what the rotation was verified with.
    for kind, floor in (("words", 60), ("expressions", 55),
                        ("conversations", 24)):
        check(counts[kind] >= floor,
              f"daily.json: only {counts[kind]} {kind}, the verified floor is {floor}")
    return {"counts": counts, "spans": spans, "triple": triple}


def cycles(cat: dict) -> None:
    """Every category must walk all of its entries before reusing one."""
    sys.path.insert(0, str(ROOT))
    from chatbot import daily_index, daily_step  # noqa: E402

    for kind, salt in (("words", 3), ("expressions", 11), ("conversations", 5)):
        size = len(cat[kind])
        if not size:
            continue
        step = daily_step(size, salt)
        check(math.gcd(step, size) == 1,
              f"{kind}: step {step} is not coprime with {size}, so the rotation "
              f"will skip entries and repeat early")
        walked = [daily_index(day, size, salt) for day in range(size)]
        check(len(set(walked)) == size,
              f"{kind}: {size - len(set(walked))} entries are never chosen in a "
              f"full rotation")
        # ...and no item comes back the next day
        adjacent = [a for a, b in zip(walked, walked[1:]) if a == b]
        check(not adjacent, f"{kind}: the same item on two days in a row")


# --------------------------------------------------------------------------
#  the three engines, on real dates
# --------------------------------------------------------------------------
def page_block(src: str, marker: str) -> str:
    start = src.index(f"/* --- {marker}")
    end = src.index("/* --- end", start)
    return src[start:end]


HARNESS = r"""
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const root = process.argv[2];
const cases = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const outPath = process.argv[4];

/* ---- the page's own copies, exactly as shipped ------------------------- */
__STORE__

/* ---- the APK engine, whole, exactly as shipped ------------------------- */
const botSrc = fs.readFileSync(path.join(root,
  'android/app/src/main/assets/www/bot.js'), 'utf8');
const data = {
  memory: JSON.parse(fs.readFileSync(path.join(root, 'memory.json'), 'utf8')),
  glossary: JSON.parse(fs.readFileSync(path.join(root, 'glossary.json'), 'utf8')),
  grammar: JSON.parse(fs.readFileSync(path.join(root, 'grammar.json'), 'utf8')),
  phrases: JSON.parse(fs.readFileSync(path.join(root, 'phrases.json'), 'utf8')),
  jokes: JSON.parse(fs.readFileSync(path.join(root, 'jokes.json'), 'utf8')),
  listening: JSON.parse(fs.readFileSync(path.join(root, 'listening.json'), 'utf8')),
  distinctions: JSON.parse(fs.readFileSync(path.join(root, 'distinctions.json'), 'utf8')),
  idioms: JSON.parse(fs.readFileSync(path.join(root, 'idioms.json'), 'utf8')),
  corrections: JSON.parse(fs.readFileSync(path.join(root, 'corrections.json'), 'utf8')),
  phonetics: JSON.parse(fs.readFileSync(path.join(root, 'phonetics.json'), 'utf8')),
  register: JSON.parse(fs.readFileSync(path.join(root, 'register.json'), 'utf8')),
  daily: JSON.parse(fs.readFileSync(path.join(root, 'daily.json'), 'utf8')),
};
const ctx = { module: {}, exports: {}, console };
vm.createContext(ctx);
vm.runInContext(botSrc + '\n;this.Fluentify = Fluentify; this.rot = ' +
  '{dailyIndex, dailyDayNumber, localDateKey, DAILY_SALTS};', ctx);
const bot = new ctx.Fluentify(data);
const cat = data.daily;

const problems = [];
const check = (ok, what) => { if (!ok) problems.push(what); return ok; };

/* 1) picks: the engine's selection and the page's arithmetic, same date */
const picks = cases.dates.map((date) => {
  const sel = bot.dailySelection(date);
  const day = dayNumber(date);      // the page's own copy of the arithmetic
  const page = {};
  for (const kind of ['words', 'expressions', 'conversations']) {
    const rows = cat[kind] || [];
    const idx = dayIndex(day, rows.length, DAY_SALTS[kind]);
    page[kind] = rows.length ? rows[idx].id : null;
    check(sel[kind] && sel[kind].id === page[kind],
      `the page and the APK engine disagree on ${kind} for ${date}: ` +
      `${page[kind]} vs ${sel[kind] && sel[kind].id}`);
  }
  return {date, words: sel.words && sel.words.id,
          expressions: sel.expressions && sel.expressions.id,
          conversations: sel.conversations && sel.conversations.id};
});

/* 2) the clock: local date and the next-midnight timer in this timezone */
const clock = (cases.instants || []).map((iso) => {
  const now = new Date(iso);
  const key = dayKey(now);
  const apkKey = ctx.rot.localDateKey(now);
  check(key === apkKey, `local date key differs: page ${key} vs APK ${apkKey} ` +
    `for ${iso} in ${process.env.TZ}`);
  const wait = untilLocalMidnight(now);
  const next = dayKey(new Date(now.getTime() + wait));
  return {iso, key, wait, next};
});

/* 3) completion store: a new day does not erase the last one */
const mem = {};
global.localStorage = {
  getItem: (k) => (k in mem ? mem[k] : null),
  setItem: (k, v) => { mem[k] = String(v); },
  removeItem: (k) => { delete mem[k]; },
};
const store = [];
const DAY1 = '2026-01-05';
const DAY2 = '2026-01-06';
const IDS1 = ['w001', 'e001', 'c001'];

let s = DailyStore.read();
check(Object.keys(s.days).length === 0, 'a fresh store should be empty');
DailyStore.setDone(s, DAY1, IDS1[0], true);
DailyStore.setDone(s, DAY1, IDS1[1], true);
DailyStore.write(s);

s = DailyStore.read();
check(DailyStore.isDone(s, DAY1, IDS1[0]), 'a tick did not survive a write/read');
check(DailyStore.count(s, DAY1, IDS1) === 2, 'count should be 2, got ' +
  DailyStore.count(s, DAY1, IDS1));

// the next day starts empty, and the previous day is still recorded
check(DailyStore.count(s, DAY2, IDS1) === 0, 'a new day should start unmarked');
check(DailyStore.count(s, DAY1, IDS1) === 2, 'the new day erased the old record');

// an id that is no longer in the catalogue cannot tick a card
check(DailyStore.count(s, DAY1, ['gone', 'gone2']) === 0,
  'ids that are not on screen were counted');

// unticking removes the id, and the empty day disappears
DailyStore.setDone(s, DAY1, IDS1[0], false);
DailyStore.write(s);
s = DailyStore.read();
check(!DailyStore.isDone(s, DAY1, IDS1[0]), 'unticking did not stick');
DailyStore.setDone(s, DAY1, IDS1[1], false);
DailyStore.write(s);
s = DailyStore.read();
check(!(DAY1 in s.days), 'an empty day was left behind');

// a corrupt record must not throw, and must not leave junk behind
mem[DailyStore.KEY] = '{not json at all';
s = DailyStore.read();
check(Object.keys(s.days).length === 0, 'a corrupt record was not ignored');
mem[DailyStore.KEY] = '{"days":{"2026-01-05":"w001","2026-01-06":["w002",7]}}';
s = DailyStore.read();
check(!('2026-01-05' in s.days), 'a non-array day survived the clean-up');
check(JSON.stringify(s.days['2026-01-06']) === '["w002"]',
  'non-string ids were not filtered out: ' + JSON.stringify(s.days['2026-01-06']));

/* 4) the offer: skipping a day and switching the card off. The daily set is a
   suggestion, so both answers have to be remembered and both have to be
   reversible - and the per-day record must not grow without bound. */
mem[DailyStore.KEY] = '';
mem[DailyStore.CARD_KEY] = '';
delete mem[DailyStore.KEY];
delete mem[DailyStore.CARD_KEY];

let p = DailyStore.readCard();
check(p.hidden === false && Object.keys(p.skipped).length === 0,
  'a fresh learner should be offered the card and to skip nothing');
check(!DailyStore.isSkipped(p, DAY1), 'a fresh day should not read as skipped');

DailyStore.writeCard(DailyStore.setSkipped(p, DAY1, true));
p = DailyStore.readCard();
check(DailyStore.isSkipped(p, DAY1), 'skipping today did not survive a write/read');
check(!DailyStore.isSkipped(p, DAY2), 'skipping one day skipped the next as well');

// and it is reversible: the learner can ask for today back
DailyStore.writeCard(DailyStore.setSkipped(DailyStore.readCard(), DAY1, false));
check(!DailyStore.isSkipped(DailyStore.readCard(), DAY1),
  'a skipped day could not be un-skipped');

// switching the card off is separate from skipping a day
p = DailyStore.readCard();
p.hidden = true;
DailyStore.writeCard(p);
check(DailyStore.readCard().hidden === true, 'switching the card off did not stick');
p = DailyStore.readCard();
p.hidden = false;
DailyStore.writeCard(p);
check(DailyStore.readCard().hidden === false, 'the card could not be switched back on');

// a corrupt preference record must not hide the feature
mem[DailyStore.CARD_KEY] = 'not json';
p = DailyStore.readCard();
check(p.hidden === false && Object.keys(p.skipped).length === 0,
  'a corrupt preference record hid the daily card');
mem[DailyStore.CARD_KEY] = '{"hidden":"yes","skipped":{"2026-01-05":true,"2026-01-06":0}}';
p = DailyStore.readCard();
check(p.hidden === true, 'a truthy hidden flag was dropped');
check(Object.keys(p.skipped).length === 1 && p.skipped['2026-01-05'] === true,
  'falsy skip flags were not filtered: ' + JSON.stringify(p.skipped));

// skipped days are pruned when written, so a daily user cannot fill storage
const many = {hidden: false, skipped: {}};
for (let i = 0; i < 200; i++) {
  const d = new Date(Date.UTC(2026, 0, 1) + i * 86400000).toISOString().slice(0, 10);
  many.skipped[d] = true;
}
const kept = DailyStore.writeCard(many).skipped;
check(Object.keys(kept).length === 60, 'skipped days were not pruned: ' +
  Object.keys(kept).length);
check(kept['2026-07-19'], 'pruning kept the oldest instead of the newest');

fs.writeFileSync(outPath, JSON.stringify({picks, clock, problems}));
console.log('checked', picks.length, 'dates,', clock.length, 'instants,',
  'and the skip/opt-out store');
"""


def run_engines(dates: list[str]) -> dict[str, dict]:
    """Ask the APK engine and the page which items each date gets."""
    if not shutil.which("node"):
        print("SKIP  node is not installed - rotation parity was not exercised")
        return {}

    src = WEBAPP.read_text(encoding="utf-8")
    try:
        store = page_block(src, "daily store: pure, executed by tools/check_daily.py")
        rotation = page_block(src, "daily rotation: pure, executed by tools/check_daily.py")
    except ValueError:
        fail("webapp.py: the daily rotation/store block markers are gone")
        return {}

    CACHE.mkdir(parents=True, exist_ok=True)
    script = CACHE / "daily_check.js"
    script.write_text(
        HARNESS.replace("__STORE__", rotation + "\n" + store), encoding="utf-8")
    cases = CACHE / "daily_cases.json"
    out = CACHE / "daily_out.json"

    results: dict[str, dict] = {}
    zones = [None, "Asia/Tehran", "America/New_York", "Europe/London",
             "Pacific/Auckland"]
    for zone in zones:
        # 23:30 and 00:05 on the nights the clocks change, plus an ordinary
        # evening a hair before midnight, which is where an off-by-one day
        # shows up first.
        instants = [
            "2026-01-15T23:59:59.500", "2026-06-15T00:00:00",
            "2026-03-07T23:30:00", "2026-03-08T00:30:00",
            "2026-03-08T23:30:00", "2026-03-09T00:05:00",
            "2026-10-24T23:30:00", "2026-10-25T00:30:00",
            "2026-10-25T23:30:00", "2026-10-26T00:05:00",
            "2026-11-01T00:30:00", "2026-12-31T23:59:00",
        ]
        cases.write_text(json.dumps({"dates": dates, "instants": instants}),
                         encoding="utf-8")
        env = dict(os.environ)
        if zone:
            env["TZ"] = zone
        proc = subprocess.run(["node", str(script), str(ROOT), str(cases),
                               str(out)], capture_output=True, text=True, env=env)
        if proc.returncode != 0:
            fail(f"node failed for TZ={zone or 'system'}: "
                 f"{(proc.stderr or proc.stdout).strip()[:300]}")
            continue
        payload = json.loads(out.read_text())
        for p in payload.get("problems") or []:
            fail(p)
        label = zone or "system"
        if not results.get("picks"):
            results["picks"] = {row["date"]: row for row in payload["picks"]}
        results.setdefault("clock", {})[label] = payload["clock"]

    for f in (script, cases, out):
        f.unlink(missing_ok=True)
    return results


def expected_picks(cat: dict, dates: list[str]) -> dict[str, dict]:
    sys.path.insert(0, str(ROOT))
    from chatbot import ChatBot  # noqa: E402

    bot = ChatBot()
    out = {}
    for date in dates:
        picked = bot.daily_selection(date)
        out[date] = {k: (picked[k]["id"] if picked[k] else None) for k in KINDS}
    return out


def clock_expectations(zone: str | None, instants: list[str]) -> dict[str, dict]:
    """What the local date and the wait to midnight must be, per instant.

    Both sides are asked the same question: the local wall time, and how long
    until the *next* local midnight - which on a daylight-saving night is not
    24 hours away, and is exactly the case a naive `+ 86400000` gets wrong.
    """
    tz = ZoneInfo(zone) if zone else None
    out = {}
    for iso in instants:
        naive = datetime.fromisoformat(iso)
        now = naive.replace(tzinfo=tz) if tz else naive.astimezone()
        midnight = datetime(now.year, now.month, now.day, tzinfo=now.tzinfo)
        nxt = midnight + timedelta(days=1)   # wall clock: next local midnight
        # Subtracting two aware datetimes that share one tzinfo object is a
        # *wall-clock* difference in CPython - it skips utcoffset() entirely, so
        # on a daylight-saving night it answers 23 or 25 hours with the hour
        # still attached. Timestamps are absolute, which is what the timer is.
        wait = int(round((nxt.timestamp() - now.timestamp() + 1) * 1000))
        out[iso] = {"key": now.date().isoformat(), "wait": wait,
                    "next": nxt.date().isoformat()}
    return out


# --------------------------------------------------------------------------
#  wiring
# --------------------------------------------------------------------------
def wiring(src: str, cat: dict) -> None:
    for needle, what in (
        ('id="dpanel"', "the Daily English panel"),
        ('id="dtoggle"', "its tile in the toolbar"),
        ('id="dcards"', "the card container"),
        ('id="dbadge"', "the tile badge"),
        ('id="dfill"', "the progress bar"),
        ("dpanel: 'dtoggle'", "the panel-to-tile map"),
        ("dpanel: () => Daily.refresh(true)", "the repaint-on-open hook"),
        ("document.getElementById('dtoggle').onclick", "the tile's click handler"),
        ("['Today', loadDaily]", "the boot step that fills it"),
        ("Daily.init();", "the midnight/resume watcher"),
        ('self.path.startswith("/api/daily")', "the /api/daily route"),
    ):
        check(needle in src, f"webapp.py: {what} is missing ({needle!r})")

    # The panel is RTL-aware or the Persian is unreadable next to English.
    persian_rule = re.search(r"\.dfa, \.dline\.fa, \.dbubble \.dfa \{[^}]*\}", src)
    check(bool(persian_rule), "the Persian line styles are gone")
    if persian_rule:
        body = persian_rule.group(0)
        check("direction: rtl" in body, "the Persian lines are not set rtl")
        check("unicode-bidi: plaintext" in body,
              "a Persian line starting with a Latin word will be laid out wrong")
    # The Persian toggle has to hide the very class the renderer emits, or the
    # button flips its own label and nothing on the card changes.
    check(re.search(r"\.dcard\.persian-off \.dfa \{ display: none; \}", src)
          is not None, "the Persian toggle does not hide .dfa")

    # every card renderer must exist, or a category silently paints nothing
    for fn in ("wordBody", "expressionBody", "conversationBody", "paintCard",
               "tools", "bind"):
        check(f"function {fn}(" in src, f"the Daily module has no {fn}()")

    # No voice in this section. Three items a day is reading material; audio is
    # the Listening panel's job, and a speaker under every line made the daily
    # card look like a player instead of a card. Asserted on the two strings the
    # removed controls owned, because a future edit that reintroduces one would
    # otherwise look like a feature.
    for gone, what in (("data-say", "a per-line speaker button"),
                       ("data-play", "a \"listen to it all\" button"),
                       ("Listen to it all", "the listen-all control")):
        check(gone not in src, f"the Daily feature has {what} again")

    # The card in the conversation. Every one of its rows was styled and the
    # box around them was not, so it inherited the transcript's handwriting
    # face with no padding, border or background and read as loose text wedged
    # into the chat. The container rule is a hard requirement, not boilerplate.
    box = re.search(r"\n  \.dinline \{[^}]*\}", src)
    check(bool(box), "the .dinline card in the chat has no rule at all")
    if box:
        for prop, what in (("background:", "no background"),
                           ("border:", "no border"),
                           ("padding:", "no padding"),
                           ("border-radius:", "no radius")):
            check(prop in box.group(0),
                  f"the .dinline container has {what} and reads as bare text")
    check("node.id = 'dailyset'" in src and "chatEl.appendChild(node)" in src,
          "the daily card is not mounted into the transcript any more")

    # One control per action: the card shipped four, two of which skipped the
    # same day. And "read all three" has to open the rows in place, because
    # the point of the card is reading the day without leaving the chat.
    card = re.search(r"function cardHtml\(prefs, key\) \{(.*?)\n  \}\n", src, re.S)
    check(bool(card), "the daily card has no renderer")
    if card:
        body = card.group(1)
        check(body.count('data-skip="1"') == 1,
              "the daily card offers %d ways to skip one day"
              % body.count('data-skip="1"'))
        check('data-learn="1"' in body and "dpanel" not in body,
              "\"Read all three\" jumps to the panel instead of opening the rows")

    # the offline bundle has to carry the catalogue and hand it to the engine
    build = (ROOT / "build_apk_ui.py").read_text(encoding="utf-8")
    check('"daily.json"' in build, "build_apk_ui.py does not bundle daily.json")
    check("loadJSON('daily')" in build, "the offline boot does not read daily.json")
    check(re.search(r"\bword_arch,\s*daily\]", build) is not None,
          "the offline destructure does not take daily")

    if BUILT.exists():
        built = BUILT.read_text(encoding="utf-8")
        check("loadJSON('daily')" in built,
              "the built page never loads the daily catalogue")
        check("const Daily = (() =>" in built, "the built page has no Daily module")
        check("id=\"dcards\"" in built, "the built page has no card container")
        check("data/daily.json" not in built, "the built page hard-codes a data path")
    else:
        check(False, "the built page is missing - run build_apk_ui.py")

    bundled = DATA / "daily.json"
    check(bundled.exists(), f"{bundled} is missing from the offline bundle")
    if bundled.exists():
        check(json.loads(bundled.read_text(encoding="utf-8")) == cat,
              "the bundled daily.json differs from the repository's - rebuild the APK")


# --------------------------------------------------------------------------
def main() -> int:
    raw = CATALOGUE.read_text(encoding="utf-8")
    cat = json.loads(raw)
    validate(cat)

    stats = coverage(cat)
    cycles(cat)

    # 365 consecutive dates from the start of a year, so the run crosses both
    # daylight-saving changes and a year boundary.
    start = datetime(2026, 1, 1).date()
    dates = [(start + timedelta(days=i)).isoformat() for i in range(365)]

    engines = run_engines(dates)
    if engines.get("picks"):
        expected = expected_picks(cat, dates)
        for date in dates:
            want = expected[date]
            got = engines["picks"].get(date) or {}
            for kind in KINDS:
                check(got.get(kind) == want[kind],
                      f"CLI and app disagree on {kind} for {date}: "
                      f"{want[kind]} vs {got.get(kind)}")

    if engines.get("clock"):
        instants = [row["iso"] for row in next(iter(engines["clock"].values()))]
        for label, rows in engines["clock"].items():
            zone = None if label == "system" else label
            want = clock_expectations(zone, instants)
            for row in rows:
                w = want[row["iso"]]
                check(row["key"] == w["key"],
                      f"[{label}] {row['iso']}: local date is {row['key']}, "
                      f"expected {w['key']}")
                check(abs(row["wait"] - w["wait"]) <= 1,
                      f"[{label}] {row['iso']}: waits {row['wait']}ms to midnight, "
                      f"expected {w['wait']}ms")
                check(row["next"] == w["next"],
                      f"[{label}] {row['iso']}: the timer lands on {row['next']}, "
                      f"expected {w['next']} - a late-night tap would keep "
                      f"yesterday's lesson")

    wiring(WEBAPP.read_text(encoding="utf-8"), cat)

    if problems:
        for p in problems[:40]:
            print("FAIL  " + p)
        if len(problems) > 40:
            print(f"      ... and {len(problems) - 40} more")
        print(f"\nFAIL  {len(problems)} problem(s) with the Daily English feature")
        return 1

    counts = stats["counts"]
    print(f"PASS  {counts['words']} words, {counts['expressions']} expressions, "
          f"{counts['conversations']} conversations; a category recurs after "
          f"{min(counts.values())}-{max(counts.values())} days and the whole "
          f"set not for {stats['triple']} days")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
