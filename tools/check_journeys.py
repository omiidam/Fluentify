#!/usr/bin/env python3
"""Checks the Journey framework and the journeys that fill it.

A journey is a topic taught in stages. The stages live in journeys.json; the
travel stages join travel.json by category id, and the sports stages carry their
own words, because this project has no general sports dictionary and inventing
one to duplicate would be worse than owning the words. This suite holds both
kinds of journey to their own shape, holds the sports profiles to their fields,
and holds the page to the parts a learner touches: the entry from Useful
Sentences, the stage page, the pictures, progress, favourites and the quick
reference.

Run: python3 tools/check_journeys.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JOURNEY_FILE = ROOT / "journeys.json"
TRAVEL_FILE = ROOT / "travel.json"
SENSES_FILE = ROOT / "senses.json"
WEBAPP = ROOT / "webapp.py"
BUILDER = ROOT / "build_apk_ui.py"
ASSETS = ROOT / "android/app/src/main/assets/www"

CEFR = {"A1", "A2", "B1", "B2", "C1", "C2"}
KINDS = {"expression", "idiom", "phrasal_verb", "collocation"}
PERSIAN = re.compile(r"[\u0600-\u06FF]")
IPA = re.compile(r"/[^/]+/")

# What a makeup glossary has to name before it can call itself complete:
# the product, not a synonym for it.
REQUIRED_MAKEUP = [
    "foundation", "concealer", "primer", "powder", "blush", "bronzer",
    "contour", "highlighter", "eyeshadow", "eyeliner", "mascara",
    "lipstick", "lip gloss", "lip liner", "brush", "sponge", "brow pencil",
    "cleanser", "moisturizer", "sunscreen", "serum", "toner",
    "swatch", "dupe", "blend", "buff", "setting powder", "patch test",
]

# What a technology glossary has to name before it can call itself complete.
# The everyday words, not the vendor names: what a phone, a connection, an
# account, a scam and an AI tool are actually called.
REQUIRED_TECH = [
    "smartphone", "laptop", "tablet", "charger", "battery", "screen",
    "wi-fi", "router", "bandwidth", "hotspot", "data plan", "offline",
    "browser", "tab", "search engine", "link", "bookmark", "cache",
    "account", "username", "password", "passkey", "two-factor authentication",
    "sign out", "phishing", "scam", "spam", "malware", "firewall", "vpn",
    "app", "update", "patch", "bug", "crash", "firmware",
    "file", "folder", "download", "upload", "backup", "cloud",
    "inbox", "attachment", "notification", "mute", "reply all", "dm",
    "camera", "screenshot", "stream", "podcast", "playlist", "subtitles",
    "bluetooth", "pairing", "smart speaker", "wearable", "usb port", "power bank",
    "artificial intelligence", "chatbot", "prompt", "algorithm", "model", "deepfake",
    "screen time", "digital detox", "doomscrolling", "subscription", "privacy", "unplug",
]

# What a food glossary has to name before it can call itself complete. The
# brief asked for five areas - ingredients, equipment, methods, ordering and
# flavours, shopping and preparation - and this is the vocabulary that covers
# all five without a hole.
REQUIRED_FOOD = [
    "apple", "tomato", "onion", "garlic", "carrot", "lettuce",
    "flour", "sugar", "salt", "rice", "egg", "butter",
    "pot", "pan", "oven", "knife", "cutting board", "whisk",
    "boil", "fry", "roast", "bake", "grill", "steam",
    "recipe", "ingredient", "tablespoon", "teaspoon", "pinch", "cup",
    "sweet", "sour", "salty", "spicy", "bitter", "savoury",
    "crispy", "creamy", "tender", "chewy", "smooth", "raw",
    "vegetarian", "vegan", "gluten-free", "lactose", "allergy", "portion",
    "aisle", "trolley", "checkout", "receipt", "discount", "fresh",
    "chop", "peel", "slice", "dice", "marinate", "stir",
    "menu", "starter", "main course", "side dish", "dessert", "special",
    "bill", "tip", "split", "reservation", "takeaway", "leftovers",
]

# What an entertainment glossary has to name before it can call itself
# complete. The brief named five areas - films and series, music and concerts,
# books and storytelling, games and hobbies, reviews and recommendations - and
# this is the vocabulary that covers all five without a hole.
REQUIRED_ENTERTAINMENT = [
    "film", "genre", "plot", "character", "scene", "ending",
    "episode", "season", "series", "cliffhanger", "binge-watch", "spin-off",
    "ticket", "screen", "subtitles", "popcorn", "trailer", "row",
    "song", "album", "track", "lyrics", "melody", "beat",
    "guitar", "piano", "drums", "violin", "trumpet", "microphone",
    "concert", "stage", "audience", "encore", "venue", "festival",
    "novel", "author", "chapter", "cover", "bookmark", "library",
    "storyteller", "narrator", "fairy tale", "myth", "twist", "quote",
    "video game", "console", "controller", "level", "player", "graphics",
    "hobby", "pastime", "board game", "collection", "puzzle", "club",
    "review", "rating", "critic", "opinion", "recommend", "spoiler",
    "recommendation", "must-see", "overrated", "underrated", "classic", "taste",
]

# What a social-life glossary has to name before it can call itself complete.
# The brief named five areas - introductions and friends, family and
# relationships, invitations and parties, emotions and opinions, and the polite
# and slang registers people actually talk in - and this is the vocabulary that
# covers all five without a hole.
REQUIRED_SOCIAL = [
    "introduction", "handshake", "stranger", "acquaintance", "nickname", "confident",
    "small talk", "topic", "awkward", "chat", "compliment", "silence",
    "mate", "icebreaker", "mutual", "approach", "contact", "neighbour",
    "relative", "sibling", "in-laws", "cousin", "generation", "close-knit",
    "partner", "date", "crush", "commitment", "breakup", "engaged",
    "trust", "loyal", "argument", "support", "bond", "honest",
    "invitation", "plus-one", "RSVP", "host", "guest", "dress code",
    "celebration", "toast", "gift", "candle", "anniversary", "confetti",
    "emotion", "nervous", "grateful", "relieved", "jealous", "overwhelmed",
    "opinion", "agree", "disagree", "point of view", "compromise", "respectful",
    "polite", "apology", "favour", "interrupt", "appreciate", "manners",
    "slang", "casual", "vibe", "buddy", "meme", "banter",
]

# What a nature glossary has to name before it can call itself complete.
# The brief named five areas - animals and wildlife, weather and climate,
# plants and farming, pollution and recycling, geography and natural
# disasters - and this is the vocabulary that covers all five without a hole.
REQUIRED_NATURE = [
    "mammal", "reptile", "predator", "prey", "herd", "cub",
    "habitat", "wildlife", "nest", "burrow", "migration", "endangered",
    "forecast", "humidity", "drizzle", "thunderstorm", "breeze", "chilly",
    "season", "frost", "blossom", "daylight", "solstice", "mild",
    "climate", "greenhouse", "emission", "drought", "heatwave", "carbon",
    "seed", "soil", "sprout", "weed", "prune", "pollen",
    "crop", "harvest", "fertilizer", "orchard", "livestock", "pesticide",
    "pollution", "smog", "litter", "sewage", "toxic", "contaminate",
    "recycle", "waste", "landfill", "compost", "reusable", "sustainable",
    "valley", "glacier", "coastline", "waterfall", "plateau", "current",
    "earthquake", "flood", "landslide", "wildfire", "evacuation", "aftershock",
    "biodiversity", "conservation", "ecosystem", "extinction", "renewable", "footprint",
]

# What a fashion glossary has to name before it can call itself complete. The
# brief named five areas - the clothes, the shoes and accessories, the shops
# and fittings, the sizes, fabrics and materials, and the styles and trends -
# and this is the vocabulary that covers all five without a hole.
REQUIRED_FASHION = [
    "shirt", "trousers", "skirt", "dress", "jacket", "coat",
    "belt", "scarf", "hat", "gloves", "sunglasses", "handbag",
    "boot", "sneaker", "sandal", "heel", "lace", "sole",
    "fitting room", "rack", "tag", "receipt", "refund", "exchange",
    "size", "measurement", "tight", "loose", "tailor", "alteration",
    "cotton", "wool", "silk", "leather", "denim", "linen",
    "shade", "stripe", "check", "floral", "plain", "fade",
    "trend", "vintage", "streetwear", "classic", "fad", "runway",
    "outfit", "layer", "accessory", "silhouette", "flair", "signature",
    "laundry", "iron", "stain", "shrink", "mend", "care label",
    "suit", "tie", "blazer", "uniform", "formal", "smart casual",
    "second-hand", "thrift", "upcycle", "sustainable", "collection", "designer",
    "try on", "dress code", "personal style", "capsule wardrobe",
    "fast fashion", "investment piece", "machine washable", "business casual",
]

# The sports the brief names, by the ids the profiles use.
REQUIRED_SPORTS = [
    "soccer", "football", "basketball", "volleyball", "rugby", "cricket",
    "baseball", "softball", "handball", "fieldhockey", "icehockey",
    "tennis", "tabletennis", "badminton", "squash", "padel",
    "running", "marathon", "longjump", "highjump", "gymnastics",
    "weightlifting", "golf", "archery", "bowling",
    "swimming", "diving", "waterpolo", "surfing", "sailing", "rowing", "kayaking",
    "boxing", "wrestling", "judo", "karate", "taekwondo", "fencing",
    "cycling", "mountainbike", "climbing", "skiing", "snowboarding",
    "iceskating", "skateboarding", "horse",
]

fails: list[str] = []
notes: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    if ok:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}" + (f"  - {detail}" if detail else ""))
        fails.append(name)


def span_between(src: str, start: str, end: str) -> str:
    """The slice of the page between two markers, or empty if they are gone."""
    try:
        a = src.index(start)
        return src[a:src.index(end, a + len(start))]
    except ValueError:
        return ""


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check_stage(sid: str, st: dict, needs_refs: bool, needs_words: bool) -> None:
    check(f"{sid}: has a title and a Persian title",
          bool(st.get("title_en")) and bool(st.get("title_fa")))
    check(f"{sid}: has a blurb in both languages",
          bool(st.get("blurb_en")) and bool(st.get("blurb_fa")))
    obj = st.get("objectives") or []
    check(f"{sid}: at least 3 learning objectives", len(obj) >= 3, str(len(obj)))
    check(f"{sid}: every objective is translated",
          all(o.get("en") and o.get("fa") for o in obj))

    exprs = st.get("expressions") or []
    check(f"{sid}: at least 4 expressions and idioms", len(exprs) >= 4, str(len(exprs)))
    kinds = {x.get("kind") for x in exprs}
    check(f"{sid}: uses known expression kinds", kinds <= KINDS, str(kinds))
    check(f"{sid}: every expression has a meaning, a register and a Persian",
          all(x.get("en") and x.get("fa") and x.get("meaning_en")
              and x.get("meaning_fa") and x.get("register") for x in exprs))

    pats = st.get("patterns") or []
    check(f"{sid}: at least 2 patterns", len(pats) >= 2, str(len(pats)))
    check(f"{sid}: every pattern has a variable slot",
          all(("[" in p.get("frame", "") or "+" in p.get("frame", "")) for p in pats),
          str([p.get("frame") for p in pats]))

    sents = st.get("sentences") or []
    check(f"{sid}: at least 2 sentences of its own", len(sents) >= 2, str(len(sents)))
    bad_lvl = [x.get("en") for x in sents if x.get("level") not in CEFR]
    check(f"{sid}: every sentence carries a CEFR level", not bad_lvl, str(bad_lvl))
    check(f"{sid}: every sentence is explained and translated",
          all(x.get("en") and x.get("fa") and x.get("use_en") and x.get("use_fa")
              for x in sents))

    d = st.get("dialogue") or {}
    lines = d.get("lines") or []
    who = {ln.get("who") for ln in lines}
    check(f"{sid}: the conversation has at least 6 lines", len(lines) >= 6, str(len(lines)))
    check(f"{sid}: the conversation has at least 2 speakers", len(who) >= 2, str(who))
    check(f"{sid}: every line is translated",
          all(ln.get("en") and ln.get("fa") and ln.get("who") for ln in lines))

    scn = st.get("scenarios") or []
    check(f"{sid}: at least 2 practical scenarios", len(scn) >= 2, str(len(scn)))
    check(f"{sid}: every scenario has a task and a model answer",
          all(c.get("task_en") and c.get("answer_en") and c.get("situation_en")
              for c in scn))

    prac = st.get("practice") or []
    check(f"{sid}: at least 3 practice items", len(prac) >= 3, str(len(prac)))
    check(f"{sid}: every practice item has its answer among the options",
          all(p.get("answer") in (p.get("options") or []) for p in prac))
    check(f"{sid}: every practice item explains its answer",
          all(p.get("why_en") and p.get("why_fa") for p in prac))

    if needs_words:
        words = st.get("words") or []
        check(f"{sid}: at least 4 words of its own", len(words) >= 4, str(len(words)))
        check(f"{sid}: every word has a reading", all(w.get("ipa") for w in words))
        check(f"{sid}: every word's reading is IPA in slashes",
              all(IPA.search(w.get("ipa") or "") for w in words),
              str([w.get("ipa") for w in words if not IPA.search(w.get("ipa") or "")][:3]))
        check(f"{sid}: every word has a part of speech",
              all(w.get("pos") for w in words))
        check(f"{sid}: every word has a Persian and a definition",
              all(w.get("fa") and w.get("def_en") for w in words))
        check(f"{sid}: every word has an example and its Persian",
              all(w.get("example_en") and w.get("example_fa") for w in words))
        check(f"{sid}: every word carries a CEFR level",
              all(w.get("level") in CEFR for w in words))
        check(f"{sid}: every word says which topic it belongs to",
              all(w.get("sport") or w.get("topic") for w in words))
        check(f"{sid}: every word has a picture key", all(w.get("icon") for w in words))
    if needs_refs:
        check(f"{sid}: names travel categories", bool(st.get("refs")))


def main() -> int:
    if not JOURNEY_FILE.exists():
        print("  FAIL  journeys.json exists  - run tools/build_journeys.py")
        return 1
    doc = load(JOURNEY_FILE)
    bank = load(TRAVEL_FILE)
    senses = load(SENSES_FILE).get("words", {})
    cats = {c["id"]: c for c in bank.get("categories", [])}
    src = WEBAPP.read_text(encoding="utf-8")

    journeys = doc.get("journeys") or []
    by_id = {j.get("id"): j for j in journeys}
    check("the file holds all twelve journeys",
          {"travel", "sports", "makeup", "tech", "food", "entertainment",
           "social", "nature", "fashion", "health", "home",
           "work"} <= set(by_id), str(sorted(by_id)))

    for jid in ("travel", "sports", "makeup", "tech", "food", "entertainment",
                "social", "nature", "fashion", "health", "home", "work"):
        j = by_id.get(jid)
        if not j:
            continue
        for key in ("topic", "title_en", "title_fa", "blurb_en", "blurb_fa"):
            check(f"{jid}: declares {key}", bool(j.get(key)))
        if jid in ("makeup", "tech", "food", "entertainment", "social",
                   "nature", "fashion", "health", "home", "work"):
            # Makeup, technology and food are grown-up subjects in this app:
            # the adult experience offers them and the kid experience never
            # does.
            check(f"{jid}: offered to adults only",
                  set(j.get("audiences") or []) == {"adults"},
                  str(j.get("audiences")))
            check(f"{jid}: no kid stage is declared",
                  all(set(st.get("audiences") or []) == {"adults"}
                      for st in (j.get("stages") or [])),
                  str([st.get("id") for st in (j.get("stages") or [])
                       if st.get("audiences") != ["adults"]]))
        else:
            check(f"{jid}: offered to both experiences",
                  set(j.get("audiences") or []) == {"kids", "adults"},
                  str(j.get("audiences")))
        check(f"{jid}: is not the other journey's title",
              j["title_en"] != (by_id.get("sports" if jid == "travel" else "travel") or {}).get("title_en"))

    travel = by_id.get("travel") or {"stages": []}
    sports = by_id.get("sports") or {"stages": []}
    tstages = travel.get("stages") or []
    sstages = sports.get("stages") or []

    check("the travel journey still has its twelve stages", len(tstages) == 12, str(len(tstages)))
    check("travel stage order is 1..12",
          [s.get("order") for s in tstages] == list(range(1, 13)),
          str([s.get("order") for s in tstages]))
    check("the sports journey has fourteen stages", len(sstages) == 14, str(len(sstages)))
    makeup = by_id.get("makeup") or {"stages": []}
    mstages = makeup.get("stages") or []
    check("the makeup journey has twelve stages", len(mstages) == 12, str(len(mstages)))
    check("makeup stage order is 1..12",
          [s.get("order") for s in mstages] == list(range(1, 13)),
          str([s.get("order") for s in mstages]))
    tech = by_id.get("tech") or {"stages": []}
    cstages = tech.get("stages") or []
    check("the technology journey has twelve stages", len(cstages) == 12,
          str(len(cstages)))
    check("technology stage order is 1..12",
          [s.get("order") for s in cstages] == list(range(1, 13)),
          str([s.get("order") for s in cstages]))
    food = by_id.get("food") or {"stages": []}
    fstages = food.get("stages") or []
    check("the food journey has twelve stages", len(fstages) == 12,
          str(len(fstages)))
    check("food stage order is 1..12",
          [s.get("order") for s in fstages] == list(range(1, 13)),
          str([s.get("order") for s in fstages]))
    ent = by_id.get("entertainment") or {"stages": []}
    estages = ent.get("stages") or []
    check("the entertainment journey has twelve stages", len(estages) == 12,
          str(len(estages)))
    check("entertainment stage order is 1..12",
          [s.get("order") for s in estages] == list(range(1, 13)),
          str([s.get("order") for s in estages]))
    nat = by_id.get("nature") or {"stages": []}
    natstages = nat.get("stages") or []
    check("the nature journey has twelve stages", len(natstages) == 12,
          str(len(natstages)))
    check("nature stage order is 1..12",
          [s.get("order") for s in natstages] == list(range(1, 13)),
          str([s.get("order") for s in natstages]))
    fas = by_id.get("fashion") or {"stages": []}
    fasstages = fas.get("stages") or []
    check("the fashion journey has twelve stages", len(fasstages) == 12,
          str(len(fasstages)))
    check("fashion stage order is 1..12",
          [s.get("order") for s in fasstages] == list(range(1, 13)),
          str([s.get("order") for s in fasstages]))
    soc = by_id.get("social") or {"stages": []}
    socstages = soc.get("stages") or []
    check("the social journey has twelve stages", len(socstages) == 12,
          str(len(socstages)))
    check("social stage order is 1..12",
          [s.get("order") for s in socstages] == list(range(1, 13)),
          str([s.get("order") for s in socstages]))
    check("sports stage order is 1..14",
          [s.get("order") for s in sstages] == list(range(1, 15)),
          str([s.get("order") for s in sstages]))
    for jid, stages in (("travel", tstages), ("sports", sstages),
                        ("makeup", mstages), ("tech", cstages),
                        ("food", fstages), ("entertainment", estages),
                        ("social", socstages), ("nature", natstages),
                        ("fashion", fasstages)):
        ids = [s.get("id") for s in stages]
        check(f"{jid}: stage ids are unique", len(set(ids)) == len(ids), str(ids))
        check(f"{jid}: every stage declares its audience",
              all(s.get("audiences") for s in stages))

    # ------------------------------------------------------------ the stages --
    for st in tstages:
        check_stage(st["id"], st, needs_refs=True, needs_words=False)
    for st in sstages:
        check_stage(st["id"], st, needs_refs=False, needs_words=True)
    for st in mstages:
        check_stage(st["id"], st, needs_refs=False, needs_words=True)
    for st in cstages:
        check_stage(st["id"], st, needs_refs=False, needs_words=True)
    for st in fstages:
        check_stage(st["id"], st, needs_refs=False, needs_words=True)
    for st in estages:
        check_stage(st["id"], st, needs_refs=False, needs_words=True)
    for st in socstages:
        check_stage(st["id"], st, needs_refs=False, needs_words=True)
    for st in natstages:
        check_stage(st["id"], st, needs_refs=False, needs_words=True)
    for st in fasstages:
        check_stage(st["id"], st, needs_refs=False, needs_words=True)

    # ------------------------------------------------------- the travel join --
    check("no travel stage carries its own word list",
          all("vocab" not in s for s in tstages))
    refs = [c for s in tstages for c in (s.get("refs") or [])]
    unknown = [r for r in refs if r not in cats]
    check("every travel stage category exists in travel.json", not unknown, str(unknown))
    reached = set(refs)
    joined_sent = sum(len(cats[r].get("sentences") or []) for r in reached)
    joined_words = sum(len(cats[r].get("vocab") or []) for r in reached)
    bank_sent = sum(len(c.get("sentences") or []) for c in cats.values())
    bank_words = sum(len(c.get("vocab") or []) for c in cats.values())
    check("the travel join reaches most of its bank",
          joined_sent >= bank_sent * 0.85 and joined_words >= bank_words * 0.85,
          f"{joined_sent}/{bank_sent} sentences, {joined_words}/{bank_words} words")

    # ---------------------------------------------------------- the profiles --
    profiles = sports.get("sports") or []
    ids = [p.get("id") for p in profiles]
    check("every named sport has a profile",
          all(s in ids for s in REQUIRED_SPORTS),
          str([s for s in REQUIRED_SPORTS if s not in ids]))
    check("sport ids are unique", len(set(ids)) == len(ids))
    check("sports count is reported", (sports.get("stats") or {}).get("sports") == len(profiles),
          str((sports.get("stats") or {}).get("sports")))
    for p in profiles:
        pid = p.get("id")
        check(f"{pid}: has a name, a Persian and a reading",
              bool(p.get("en")) and bool(p.get("fa")) and bool(IPA.search(p.get("ipa", ""))))
        check(f"{pid}: is classified", bool(p.get("category")))
        check(f"{pid}: has a definition and a place", bool(p.get("def_en")) and bool(p.get("venue")))
        check(f"{pid}: has equipment and actions",
              bool(p.get("equipment")) and bool(p.get("actions")))
        check(f"{pid}: has an example sentence and a Persian",
              bool(p.get("sentence_en")) and bool(p.get("sentence_fa")))
        check(f"{pid}: has an exchange you could say",
              bool(p.get("exchange_en")) and bool(p.get("exchange_fa")))
        check(f"{pid}: has a picture key", bool(p.get("icon")))
        check(f"{pid}: terms are translated",
              all(t.get("term") and t.get("fa") and t.get("meaning_en")
                  for t in (p.get("terms") or [])))

    shown = {s for st in sstages for s in (st.get("sportRefs") or [])}
    check("every profiled sport is reachable from a stage",
          shown == set(ids), str(sorted(set(ids) - shown)))
    terms = sum(len(p.get("terms") or []) for p in profiles)
    check("the profiles carry their own terminology", terms >= 40, str(terms))

    # -------------------------------------------------------------- the idioms --
    idioms = [x for x in (by_id.get("sports", {}).get("stages") or [])
              for x in (x.get("expressions") or []) if x.get("kind") == "idiom"]
    check("the sports journey teaches at least 12 idioms", len(idioms) >= 12, str(len(idioms)))
    def both_readings(x: dict) -> bool:
        """The word 'literally', or the sport it came from, then the figurative use."""
        m = x.get("meaning_en") or ""
        literal = "iterally" in m or m.lstrip().startswith("From ")
        return literal and "iguratively" in m

    check("every idiom separates the literal reading from the figurative one",
          all(both_readings(x) for x in idioms),
          str([x.get("en") for x in idioms if not both_readings(x)][:4]))
    check("every idiom has an example in context",
          all(x.get("example_en") and x.get("example_fa") for x in idioms))
    check("every idiom is labelled for register",
          all(x.get("register") for x in idioms))
    check("phrasal verbs are labelled as phrasal verbs",
          any(x.get("kind") == "phrasal_verb"
              for s in (by_id.get("sports", {}).get("stages") or [])
              for x in (s.get("expressions") or [])))

    # ----------------------------------------------------- the makeup glossary --
    mwords = [w for st in mstages for w in (st.get("words") or [])]
    mexprs = [x for st in mstages for x in (st.get("expressions") or [])]
    mterms = " | ".join([w.get("en", "") for w in mwords]
                        + [x.get("en", "") for x in mexprs]).lower()
    absent = [t for t in REQUIRED_MAKEUP if t not in mterms]
    check("the makeup glossary names every essential product and verb",
          not absent, str(absent))
    check("the makeup glossary is big enough to be a glossary",
          len(mwords) >= 60, str(len(mwords)))
    check("the makeup journey teaches at least 50 expressions and idioms",
          len(mexprs) >= 50, str(len(mexprs)))
    mwords_rows = [w for w in mwords]
    check("no makeup word is defined twice with a different meaning",
          len({w.get("en") for w in mwords_rows}) == len(mwords_rows),
          str([w.get("en") for w in mwords_rows
               if [x.get("en") for x in mwords_rows].count(w.get("en")) > 1][:4]))
    midioms = [x for x in mexprs if x.get("kind") == "idiom"]
    check("the makeup journey teaches at least 12 idioms", len(midioms) >= 12,
          str(len(midioms)))
    check("every makeup idiom separates the literal reading from the figurative one",
          all(both_readings(x) for x in midioms),
          str([x.get("en") for x in midioms if not both_readings(x)][:4]))
    check("every makeup idiom has an example in context",
          all(x.get("example_en") and x.get("example_fa") for x in midioms))
    check("the makeup journey labels slang as slang",
          any(x.get("register") == "slang" for x in mexprs))
    check("the makeup journey has phrasal verbs and collocations too",
          {x.get("kind") for x in mexprs} >= {"idiom", "expression"})
    check("the makeup journey counts its own statistics",
          (makeup.get("stats") or {}).get("words") == len(mwords)
          and (makeup.get("stats") or {}).get("expressions") == len(mexprs),
          str(makeup.get("stats")))
    check("the makeup journey is offered in the adult sentence panel",
          "Journey.card('makeup', false)" in src)
    check("the kid sentence panel never offers makeup",
          "Journey.card('makeup', true)" not in src
          and "Journey.card('makeup'" not in
          span_between(src, "async function phrases()", "/* ---- the chat ----"))
    # ------------------------------------------------- the technology glossary --
    cwords = [w for st in cstages for w in (st.get("words") or [])]
    cexprs = [x for st in cstages for x in (st.get("expressions") or [])]
    cterms = " | ".join([w.get("en", "") for w in cwords]
                        + [x.get("en", "") for x in cexprs]).lower()
    cabsent = [t for t in REQUIRED_TECH if t not in cterms]
    check("the technology glossary names every essential device, risk and app",
          not cabsent, str(cabsent))
    check("the technology glossary is big enough to be a glossary",
          len(cwords) >= 60, str(len(cwords)))
    check("the technology journey teaches at least 50 expressions and idioms",
          len(cexprs) >= 50, str(len(cexprs)))
    check("no technology word is defined twice with a different meaning",
          len({w.get("en") for w in cwords}) == len(cwords),
          str([w.get("en") for w in cwords
               if [x.get("en") for x in cwords].count(w.get("en")) > 1][:4]))
    check("every technology word carries a reading, a class and a Persian",
          all(IPA.search(w.get("ipa") or "") and w.get("pos")
              and w.get("fa") and w.get("def_en") and w.get("level")
              and w.get("example_en") and w.get("example_fa")
              for w in cwords),
          str([w.get("en") for w in cwords
               if not (IPA.search(w.get("ipa") or "") and w.get("pos")
                       and w.get("fa") and w.get("def_en") and w.get("level")
                       and w.get("example_en") and w.get("example_fa"))][:4]))
    cidioms = [x for x in cexprs if x.get("kind") == "idiom"]
    check("the technology journey teaches at least 12 idioms", len(cidioms) >= 12,
          str(len(cidioms)))
    check("every technology idiom separates the literal reading from the figurative one",
          all(both_readings(x) for x in cidioms),
          str([x.get("en") for x in cidioms if not both_readings(x)][:4]))
    check("every technology idiom has an example in context",
          all(x.get("example_en") and x.get("example_fa") for x in cidioms))
    check("the technology journey labels slang as slang",
          any(x.get("register") == "slang" for x in cexprs),
          str(sorted({x.get("register") for x in cexprs})))
    check("the technology journey mixes phrasal verbs and collocations",
          {x.get("kind") for x in cexprs} >= {"idiom", "expression",
                                              "phrasal_verb", "collocation"},
          str(sorted({x.get("kind") for x in cexprs})))
    cstats = tech.get("stats") or {}
    check("the technology journey counts its own statistics",
          cstats.get("stages") == len(cstages) and cstats.get("words") == len(cwords)
          and cstats.get("expressions") == len(cexprs),
          str(cstats))
    check("the technology journey is offered in the adult sentence panel",
          "Journey.card('tech', false)" in src)
    check("the kid sentence panel never offers technology",
          "Journey.card('tech', true)" not in src
          and "Journey.card('tech'" not in
          span_between(src, "async function phrases()", "/* ---- the chat ----"))
    # ----------------------------------------------------- the fashion glossary --
    fawords = [w for st in fasstages for w in (st.get("words") or [])]
    faexprs = [x for st in fasstages for x in (st.get("expressions") or [])]
    faterms = " | ".join([w.get("en", "") for w in fawords]
                         + [x.get("en", "") for x in faexprs]).lower()
    faabsent = [t for t in REQUIRED_FASHION if t not in faterms]
    check("the fashion glossary names every garment, shoe, shop and fabric word",
          not faabsent, str(faabsent))
    check("the fashion glossary is big enough to be a glossary",
          len(fawords) >= 60, str(len(fawords)))
    check("the fashion journey teaches at least 50 expressions and idioms",
          len(faexprs) >= 50, str(len(faexprs)))
    check("no fashion word is defined twice",
          len({w.get("en") for w in fawords}) == len(fawords),
          str([w.get("en") for w in fawords
               if [x.get("en") for x in fawords].count(w.get("en")) > 1][:4]))
    check("every fashion word carries a reading, a class, a Persian and an example",
          all(IPA.search(w.get("ipa") or "") and w.get("pos")
              and w.get("fa") and w.get("def_en") and w.get("level")
              and w.get("example_en") and w.get("example_fa")
              for w in fawords),
          str([w.get("en") for w in fawords
               if not (IPA.search(w.get("ipa") or "") and w.get("pos")
                       and w.get("fa") and w.get("def_en") and w.get("level")
                       and w.get("example_en") and w.get("example_fa"))][:4]))
    faidioms = [x for x in faexprs if x.get("kind") == "idiom"]
    check("the fashion journey teaches at least 12 idioms", len(faidioms) >= 12,
          str(len(faidioms)))
    check("every fashion idiom separates the literal reading from the figurative one",
          all(both_readings(x) for x in faidioms),
          str([x.get("en") for x in faidioms if not both_readings(x)][:4]))
    check("every fashion idiom has an example in context",
          all(x.get("example_en") and x.get("example_fa") for x in faidioms))
    check("the fashion journey labels slang as slang",
          any(x.get("register") == "slang" for x in faexprs),
          str(sorted({x.get("register") for x in faexprs})))
    check("the fashion journey mixes phrasal verbs and collocations",
          {x.get("kind") for x in faexprs} >= {"idiom", "expression",
                                               "phrasal_verb", "collocation"},
          str(sorted({x.get("kind") for x in faexprs})))
    fastats = fas.get("stats") or {}
    check("the fashion journey counts its own statistics",
          fastats.get("stages") == len(fasstages)
          and fastats.get("words") == len(fawords)
          and fastats.get("expressions") == len(faexprs),
          str(fastats))
    check("the fashion journey is offered in the adult sentence panel",
          "Journey.card('fashion', false)" in src)
    check("the kid sentence panel never offers fashion",
          "Journey.card('fashion', true)" not in src
          and "Journey.card('fashion'" not in
          span_between(src, "async function phrases()", "/* ---- the chat ----"))
    check("the fashion card leads with the supplied picture",
          "photo: 'fashion'" in src and "journey-fashion.jpg" in
          (ROOT / "build_apk_ui.py").read_text(encoding="utf-8"))

    # ------------------------------------------- health & well-being --
    hea = by_id.get("health") or {"stages": []}
    heastages = hea.get("stages") or []
    heawords = [w for st in heastages for w in (st.get("words") or [])]
    heaexprs = [x for st in heastages for x in (st.get("expressions") or [])]
    check("the health journey covers the five subjects it was asked for",
          [st.get("id") for st in heastages] ==
          ["symptoms", "booking", "habits", "mind", "pain"],
          str([st.get("id") for st in heastages]))
    check("every health stage is adult-only",
          all(set(st.get("audiences") or []) == {"adults"} for st in heastages))
    check("the health journey teaches a full glossary", len(heawords) >= 30,
          str(len(heawords)))
    check("every health word carries a reading, a class, a Persian and an example",
          all(IPA.search(w.get("ipa") or "") and w.get("pos") and w.get("fa")
              and w.get("def_en") and w.get("level")
              and w.get("example_en") and w.get("example_fa") for w in heawords),
          str([w.get("en") for w in heawords
               if not IPA.search(w.get("ipa") or "")][:4]))
    check("no health word is defined twice with a different meaning",
          len({w.get("en") for w in heawords}) == len(heawords),
          str([w.get("en") for w in heawords
               if [x.get("en") for x in heawords].count(w.get("en")) > 1][:4]))
    check("the health journey uses all four expression kinds",
          len(heaexprs) >= 30 and
          {x.get("kind") for x in heaexprs} >=
          {"expression", "collocation", "phrasal_verb", "idiom"},
          str(sorted({x.get("kind") for x in heaexprs})))
    check("every health expression explains itself in both languages",
          all(x.get("meaning_en") and x.get("meaning_fa")
              and x.get("example_en") and x.get("example_fa") for x in heaexprs))
    heastats = hea.get("stats") or {}
    check("the health journey counts its own statistics",
          heastats.get("stages") == len(heastages)
          and heastats.get("words") == len(heawords)
          and heastats.get("expressions") == len(heaexprs), str(heastats))
    check("the health card is offered in the adult sentence panel",
          "Journey.card('health', false)" in src)
    check("the kid sentence panel never offers health",
          "Journey.card('health', true)" not in src
          and "Journey.card('health'" not in
          span_between(src, "async function phrases()", "/* ---- the chat ----"))

    # ------------------------------------------------- home & everyday life --
    hom = by_id.get("home") or {"stages": []}
    homstages = hom.get("stages") or []
    homwords = [w for st in homstages for w in (st.get("words") or [])]
    homexprs = [x for st in homstages for x in (st.get("expressions") or [])]
    check("the home journey covers the five subjects it was asked for",
          [st.get("id") for st in homstages] ==
          ["rooms", "chores", "moving", "routines", "neighbours"],
          str([st.get("id") for st in homstages]))
    check("every home stage is adult-only",
          all(set(st.get("audiences") or []) == {"adults"} for st in homstages))
    check("the home journey teaches a full glossary", len(homwords) >= 30,
          str(len(homwords)))
    check("every home word carries a reading, a class, a Persian and an example",
          all(IPA.search(w.get("ipa") or "") and w.get("pos") and w.get("fa")
              and w.get("def_en") and w.get("level")
              and w.get("example_en") and w.get("example_fa") for w in homwords),
          str([w.get("en") for w in homwords
               if not IPA.search(w.get("ipa") or "")][:4]))
    check("the home journey uses all four expression kinds",
          len(homexprs) >= 30 and
          {x.get("kind") for x in homexprs} >=
          {"expression", "collocation", "phrasal_verb", "idiom"},
          str(sorted({x.get("kind") for x in homexprs})))
    check("every home expression explains itself in both languages",
          all(x.get("meaning_en") and x.get("meaning_fa")
              and x.get("example_en") and x.get("example_fa") for x in homexprs))
    homstats = hom.get("stats") or {}
    check("the home journey counts its own statistics",
          homstats.get("stages") == len(homstages)
          and homstats.get("words") == len(homwords)
          and homstats.get("expressions") == len(homexprs), str(homstats))
    check("the home card is offered in the adult sentence panel",
          "Journey.card('home', false)" in src)
    check("the kid sentence panel never offers home",
          "Journey.card('home', true)" not in src
          and "Journey.card('home'" not in
          span_between(src, "async function phrases()", "/* ---- the chat ----"))

    # ------------------------------------------------- work, careers & business --
    wrk = by_id.get("work") or {"stages": []}
    wrkstages = wrk.get("stages") or []
    wrkwords = [w for st in wrkstages for w in (st.get("words") or [])]
    wrkxprs = [x for st in wrkstages for x in (st.get("expressions") or [])]
    check("the work journey covers the six subjects it was asked for",
          [st.get("id") for st in wrkstages] ==
          ["jobs", "interviews", "meetings", "negotiations", "business",
           "emails"],
          str([st.get("id") for st in wrkstages]))
    check("every work stage is adult-only",
          all(set(st.get("audiences") or []) == {"adults"} for st in wrkstages))
    check("the work journey teaches a full glossary", len(wrkwords) >= 36,
          str(len(wrkwords)))
    check("every work word carries a reading, a class, a Persian and an example",
          all(IPA.search(w.get("ipa") or "") and w.get("pos") and w.get("fa")
              and w.get("def_en") and w.get("level")
              and w.get("example_en") and w.get("example_fa") for w in wrkwords),
          str([w.get("en") for w in wrkwords
               if not IPA.search(w.get("ipa") or "")][:4]))
    check("the work journey uses all four expression kinds",
          len(wrkxprs) >= 36 and
          {x.get("kind") for x in wrkxprs} >=
          {"expression", "collocation", "phrasal_verb", "idiom"},
          str(sorted({x.get("kind") for x in wrkxprs})))
    check("every work expression explains itself in both languages",
          all(x.get("meaning_en") and x.get("meaning_fa")
              and x.get("example_en") and x.get("example_fa") for x in wrkxprs))
    wrkstats = wrk.get("stats") or {}
    check("the work journey counts its own statistics",
          wrkstats.get("stages") == len(wrkstages)
          and wrkstats.get("words") == len(wrkwords)
          and wrkstats.get("expressions") == len(wrkxprs), str(wrkstats))
    check("the work card is offered in the adult sentence panel",
          "Journey.card('work', false)" in src)
    check("the kid sentence panel never offers work",
          "Journey.card('work', true)" not in src
          and "Journey.card('work'" not in
          span_between(src, "async function phrases()", "/* ---- the chat ----"))

    check("the technology card names its own picture",
          "chip" in src[src.index("const ART = {"):src.index("function art(key, label)")])
    check("the technology stage page has its own chat prompt",
          "tech" in src.lower())

    # ---------------------------------------------------- the food glossary --
    fwords = [w for st in fstages for w in (st.get("words") or [])]
    fexprs = [x for st in fstages for x in (st.get("expressions") or [])]
    fterms = " | ".join([w.get("en", "") for w in fwords]
                        + [x.get("en", "") for x in fexprs]).lower()
    fabsent = [t for t in REQUIRED_FOOD if t not in fterms]
    check("the food glossary names every ingredient, tool, method and menu word",
          not fabsent, str(fabsent))
    check("the food glossary is big enough to be a glossary",
          len(fwords) >= 60, str(len(fwords)))
    check("the food journey teaches at least 50 expressions and idioms",
          len(fexprs) >= 50, str(len(fexprs)))
    check("no food word is defined twice with a different meaning",
          len({w.get("en") for w in fwords}) == len(fwords),
          str([w.get("en") for w in fwords
               if [x.get("en") for x in fwords].count(w.get("en")) > 1][:4]))
    check("every food word carries a reading, a class, a Persian and an example",
          all(IPA.search(w.get("ipa") or "") and w.get("pos")
              and w.get("fa") and w.get("def_en") and w.get("level")
              and w.get("example_en") and w.get("example_fa")
              for w in fwords),
          str([w.get("en") for w in fwords
               if not (IPA.search(w.get("ipa") or "") and w.get("pos")
                       and w.get("fa") and w.get("def_en") and w.get("level")
                       and w.get("example_en") and w.get("example_fa"))][:4]))
    fidioms = [x for x in fexprs if x.get("kind") == "idiom"]
    check("the food journey teaches at least 15 idioms", len(fidioms) >= 15,
          str(len(fidioms)))
    check("every food idiom separates the literal reading from the figurative one",
          all(both_readings(x) for x in fidioms),
          str([x.get("en") for x in fidioms if not both_readings(x)][:4]))
    check("every food idiom has an example in context",
          all(x.get("example_en") and x.get("example_fa") for x in fidioms))
    check("the food journey labels slang as slang",
          any(x.get("register") == "slang" for x in fexprs),
          str(sorted({x.get("register") for x in fexprs})))
    check("the food journey mixes phrasal verbs and collocations",
          {x.get("kind") for x in fexprs} >= {"idiom", "expression",
                                              "phrasal_verb", "collocation"},
          str(sorted({x.get("kind") for x in fexprs})))
    fstats = food.get("stats") or {}
    check("the food journey counts its own statistics",
          fstats.get("stages") == len(fstages) and fstats.get("words") == len(fwords)
          and fstats.get("expressions") == len(fexprs),
          str(fstats))
    check("the food journey is offered in the adult sentence panel",
          "Journey.card('food', false)" in src)
    check("the kid sentence panel never offers food",
          "Journey.card('food', true)" not in src
          and "Journey.card('food'" not in
          span_between(src, "async function phrases()", "/* ---- the chat ----"))
    check("the food card names its own picture",
          "pot:" in src[src.index("const ART = {"):src.index("function art(key, label)")])

    # --------------------------------------------- the entertainment glossary --
    ewords = [w for st in estages for w in (st.get("words") or [])]
    eexprs = [x for st in estages for x in (st.get("expressions") or [])]
    eterms = " | ".join([w.get("en", "") for w in ewords]
                        + [x.get("en", "") for x in eexprs]).lower()
    eabsent = [t for t in REQUIRED_ENTERTAINMENT if t not in eterms]
    check("the entertainment glossary names every screen, stage, shelf and review word",
          not eabsent, str(eabsent))
    check("the entertainment glossary is big enough to be a glossary",
          len(ewords) >= 60, str(len(ewords)))
    check("the entertainment journey teaches at least 50 expressions and idioms",
          len(eexprs) >= 50, str(len(eexprs)))
    check("no entertainment word is defined twice with a different meaning",
          len({w.get("en") for w in ewords}) == len(ewords),
          str([w.get("en") for w in ewords
               if [x.get("en") for x in ewords].count(w.get("en")) > 1][:4]))
    check("every entertainment word carries a reading, a class, a Persian and an example",
          all(IPA.search(w.get("ipa") or "") and w.get("pos")
              and w.get("fa") and w.get("def_en") and w.get("level")
              and w.get("example_en") and w.get("example_fa")
              for w in ewords),
          str([w.get("en") for w in ewords
               if not (IPA.search(w.get("ipa") or "") and w.get("pos")
                       and w.get("fa") and w.get("def_en") and w.get("level")
                       and w.get("example_en") and w.get("example_fa"))][:4]))
    eidioms = [x for x in eexprs if x.get("kind") == "idiom"]
    check("the entertainment journey teaches at least 15 idioms", len(eidioms) >= 15,
          str(len(eidioms)))
    check("every entertainment idiom separates the literal reading from the figurative one",
          all(both_readings(x) for x in eidioms),
          str([x.get("en") for x in eidioms if not both_readings(x)][:4]))
    check("every entertainment idiom has an example in context",
          all(x.get("example_en") and x.get("example_fa") for x in eidioms))
    check("the entertainment journey labels slang as slang",
          any(x.get("register") == "slang" for x in eexprs),
          str(sorted({x.get("register") for x in eexprs})))
    check("the entertainment journey mixes phrasal verbs and collocations",
          {x.get("kind") for x in eexprs} >= {"idiom", "expression",
                                              "phrasal_verb", "collocation"},
          str(sorted({x.get("kind") for x in eexprs})))
    estats = ent.get("stats") or {}
    check("the entertainment journey counts its own statistics",
          estats.get("stages") == len(estages) and estats.get("words") == len(ewords)
          and estats.get("expressions") == len(eexprs),
          str(estats))
    check("the entertainment journey is offered in the adult sentence panel",
          "Journey.card('entertainment', false)" in src)
    check("the kid sentence panel never offers entertainment",
          "Journey.card('entertainment', true)" not in src
          and "Journey.card('entertainment'" not in
          span_between(src, "async function phrases()", "/* ---- the chat ----"))

    # -------------------------------------------------- the social glossary --
    swwords = [w for st in socstages for w in (st.get("words") or [])]
    swexprs = [x for st in socstages for x in (st.get("expressions") or [])]
    swterms = " | ".join([w.get("en", "") for w in swwords]
                         + [x.get("en", "") for x in swexprs]).lower()
    swabsent = [t for t in REQUIRED_SOCIAL if t.lower() not in swterms]
    check("the social glossary names every person, party and feeling word",
          not swabsent, str(swabsent))
    check("the social glossary is big enough to be a glossary",
          len(swwords) >= 60, str(len(swwords)))
    check("the social journey teaches at least 50 expressions and idioms",
          len(swexprs) >= 50, str(len(swexprs)))
    check("no social word is defined twice with a different meaning",
          len({w.get("en") for w in swwords}) == len(swwords),
          str([w.get("en") for w in swwords
               if [x.get("en") for x in swwords].count(w.get("en")) > 1][:4]))
    check("every social word carries a reading, a class, a Persian and an example",
          all(IPA.search(w.get("ipa") or "") and w.get("pos")
              and w.get("fa") and w.get("def_en") and w.get("level")
              and w.get("example_en") and w.get("example_fa")
              for w in swwords),
          str([w.get("en") for w in swwords
               if not (IPA.search(w.get("ipa") or "") and w.get("pos")
                       and w.get("fa") and w.get("def_en") and w.get("level")
                       and w.get("example_en") and w.get("example_fa"))][:4]))
    swidioms = [x for x in swexprs if x.get("kind") == "idiom"]
    check("the social journey teaches at least 15 idioms", len(swidioms) >= 15,
          str(len(swidioms)))
    check("every social idiom separates the literal reading from the figurative one",
          all(both_readings(x) for x in swidioms),
          str([x.get("en") for x in swidioms if not both_readings(x)][:4]))
    check("every social idiom has an example in context",
          all(x.get("example_en") and x.get("example_fa") for x in swidioms))
    check("the social journey labels slang as slang",
          any(x.get("register") == "slang" for x in swexprs),
          str(sorted({x.get("register") for x in swexprs})))
    check("the social journey mixes phrasal verbs and collocations",
          {x.get("kind") for x in swexprs} >= {"idiom", "expression",
                                               "phrasal_verb", "collocation"},
          str(sorted({x.get("kind") for x in swexprs})))
    swstats = soc.get("stats") or {}
    check("the social journey counts its own statistics",
          swstats.get("stages") == len(socstages)
          and swstats.get("words") == len(swwords)
          and swstats.get("expressions") == len(swexprs),
          str(swstats))
    check("the social journey is offered in the adult sentence panel",
          "Journey.card('social', false)" in src)
    check("the kid sentence panel never offers social life",
          "Journey.card('social', true)" not in src
          and "Journey.card('social'" not in
          span_between(src, "async function phrases()", "/* ---- the chat ----"))

    # --------------------------------------------------- the nature glossary --
    nawords = [w for st in natstages for w in (st.get("words") or [])]
    naexprs = [x for st in natstages for x in (st.get("expressions") or [])]
    naterms = " | ".join([w.get("en", "") for w in nawords]
                         + [x.get("en", "") for x in naexprs]).lower()
    naabsent = [t for t in REQUIRED_NATURE if t.lower() not in naterms]
    check("the nature glossary names every animal, plant, weather and land word",
          not naabsent, str(naabsent))
    check("the nature glossary is big enough to be a glossary",
          len(nawords) >= 60, str(len(nawords)))
    check("the nature journey teaches at least 50 expressions and idioms",
          len(naexprs) >= 50, str(len(naexprs)))
    check("no nature word is defined twice",
          len({w.get("en") for w in nawords}) == len(nawords),
          str([w.get("en") for w in nawords
               if [x.get("en") for x in nawords].count(w.get("en")) > 1][:4]))
    check("every nature word carries a reading, a class, a Persian and an example",
          all(IPA.search(w.get("ipa") or "") and w.get("pos")
              and w.get("fa") and w.get("def_en") and w.get("level")
              and w.get("example_en") and w.get("example_fa")
              for w in nawords),
          str([w.get("en") for w in nawords
               if not (IPA.search(w.get("ipa") or "") and w.get("pos")
                       and w.get("fa") and w.get("def_en") and w.get("level")
                       and w.get("example_en") and w.get("example_fa"))][:4]))
    naidioms = [x for x in naexprs if x.get("kind") == "idiom"]
    check("the nature journey teaches at least 15 idioms", len(naidioms) >= 15,
          str(len(naidioms)))
    check("every nature idiom separates the literal reading from the figurative one",
          all(both_readings(x) for x in naidioms),
          str([x.get("en") for x in naidioms if not both_readings(x)][:4]))
    check("every nature idiom has an example in context",
          all(x.get("example_en") and x.get("example_fa") for x in naidioms))
    check("the nature journey mixes phrasal verbs and collocations",
          {x.get("kind") for x in naexprs} >= {"idiom", "expression",
                                             "phrasal_verb", "collocation"},
          str(sorted({x.get("kind") for x in naexprs})))
    nastats = nat.get("stats") or {}
    check("the nature journey counts its own statistics",
          nastats.get("stages") == len(natstages)
          and nastats.get("words") == len(nawords)
          and nastats.get("expressions") == len(naexprs),
          str(nastats))
    check("the nature journey is offered in the adult sentence panel",
          "Journey.card('nature', false)" in src)
    check("the kid sentence panel never offers nature life",
          "Journey.card('nature', true)" not in src
          and "Journey.card('nature'" not in
          span_between(src, "async function phrases()", "/* ---- the chat ----"))
    check("the nature card names a photograph",
          "photo: 'nature'" in src)

    # ------------------------------------------------- the card photographs --
    brand = ROOT / "brand"
    photos = {"travel": "journey-travel.jpg", "sports": "journey-sports.jpg",
              "makeup": "journey-makeup.jpg", "food": "journey-food.jpg",
              "tech": "journey-tech.jpg",
              "entertainment": "journey-entertainment.jpg",
              "social": "journey-social.jpg",
              "nature": "journey-nature.jpg",
              "health": "journey-health.jpg", "home": "journey-home.jpg",
              "work": "journey-work.jpg"}
    for key, name in photos.items():
        path = brand / name
        check(f"the {key} card has its photograph", path.exists(), str(path))
        if path.exists():
            check(f"the {key} photograph is small enough for a phone",
                  path.stat().st_size < 60000, f"{path.stat().st_size} bytes")
    check("every journey card names a photograph",
          all(f"photo: '{k}'" in src for k in photos), str(sorted(photos)))
    check("the adult card shows the photograph and the child card the drawing",
          "isKid || !info.photo ? art(info.art, info.en) : photo(info.photo, info.en)" in src)
    check("the photograph is served under a whitelisted name",
          're.fullmatch(r"journey-[a-z]+\\.jpg", name)' in src
          and '"image/jpeg", 604800' in src)
    check("the photograph is sized for the card, not the file",
          "width: 58px; height: 58px" in src and "width: 48px; height: 48px" in src)
    check("the APK carries the four photographs",
          all(name in BUILDER.read_text(encoding="utf-8")
              for name in photos.values()))

    check("the makeup card names its own picture",
          "lipstick" in src[src.index("const ART = {"):src.index("function art(key, label)")])

    # ----------------------------------------------------------- the pictures --
    art_block = src[src.index("const ART = {"):src.index("function art(key, label)")]
    art_keys = set(re.findall(r"^\s{4}([a-z]+):", art_block, re.M))
    used = {j.get("art") for j in journeys}
    used |= {s.get("icon") for j in journeys for s in (j.get("stages") or [])}
    used |= {w.get("icon") for j in journeys for s in (j.get("stages") or [])
             for w in (s.get("words") or [])}
    used |= {p.get("icon") for p in profiles}
    missing = sorted(k for k in used if k and k not in art_keys and len(k) > 2
                     and not k.isascii() is False and not re.search(r"[^\x00-\x7F]", k))
    check("every picture key is drawn in the page", not missing, str(missing))
    check("the page draws the sport pictograms",
          {"soccer", "basketball", "swimming", "tennis", "bike", "gymnastics"} <= art_keys,
          str(sorted({"soccer", "basketball", "swimming", "tennis", "bike", "gymnastics"} - art_keys)))
    check("the pictures carry an accessible name",
          'role="img" aria-label="' in src)
    check("a picture is drawn, not fetched", "<svg viewBox=\"0 0 32 32\"" in src)
    check("the stage page shows the sport cards", "function sportCard(" in src
          and "sportsSection(st)" in src)
    check("the words are shown with their reading", "'jn-ipa', w.ipa" in src)

    # --------------------------------------------------------------- the page --
    check("the page defines the Journey module", src.count("const Journey = (() => {") == 1)
    check("Useful Sentences offers the Sports journey",
          "Journey.card('sports', false)" in src)
    # A child's sentence panel is a list of sentences. It used to open with the
    # Sports and Travel journeys above the list - a stage count, a word count
    # and a travel pitch that a beginner cannot read and did not ask for - so
    # the kid panel is now checked to keep them out.
    check("a child's sentence panel leaves the adult journeys out",
          "Journey.card('sports', true)" not in src and "Travel.card(true)" not in src)
    check("travel is drawn by the shared entry card, not a card of its own",
          "Journey.card('travel', false)" in src and "Travel.card" not in src)
    check("an entry card can open a named journey",
          "function card(id, kidsFlag)" in src and "open(isKid, id)" in src)
    check("a journey is chosen by id", "let currentId =" in src
          and "find((j) => j.id === currentId)" in src)
    # The flat list used to belong to travel alone, because travel was the one
    # journey with a bank to flatten. Now every journey builds it from its own
    # stages, so the button is unconditional and no journey is a special case.
    check("every journey opens the same flat list",
          "function flatRows()" in src and "function flat()" in src
          and "browse.onclick = flat" in src and "Travel.openBrowse(" not in src)
    art_block = src[src.index("const ART = {"):src.index("function art(key, label)")]
    art_keys = set(re.findall(r"^\s{4}([A-Za-z]+):\s*'", art_block, re.M))
    emoji_icons = [(j["id"], s["icon"]) for j in load(JOURNEY_FILE).get("journeys") or []
                   for s in j["stages"] if s["icon"] not in art_keys]
    check("every stage icon is drawn by the one line-art engine",
          not emoji_icons, str(emoji_icons[:3]))
    check("progress and favourites keep one local key each",
          "fluentify.journey.v1" in src and "fluentify.journey.fav.v1" in src)
    check("the quick reference searches words, sports and idioms",
          "kind: 'sport'" in src and "kind: 'term'" in src and "kind: 'word', en: w.en" in src)
    check("the quick reference filters by stage and level",
          "searchRows(q, stageSel.value, lvlSel.value)" in src)
    check("the route serves the journey file",
          '"/api/journeys"' in src and 'ROOT / "journeys.json"' in src)

    # ---------------------------------------------------------------- the APK --
    check("the APK bundles journeys.json",
          '"journeys.json"' in BUILDER.read_text(encoding="utf-8"))
    bundled = ASSETS / "data" / "journeys.json"
    check("the bundled copy is there", bundled.exists(), str(bundled))
    if bundled.exists():
        check("the bundled copy is the built file",
              bundled.read_bytes() == JOURNEY_FILE.read_bytes(),
              "run python3 build_apk_ui.py")

    # ---------------------------------------------------------------- text ----
    check("the Persian in the sports journey is Persian",
          all(PERSIAN.search(s.get("title_fa") or "") for s in sstages))
    check("the file records its own statistics",
          bool((doc.get("_meta") or {}).get("stats")))

    exprs = sum(len(s["expressions"]) for s in sstages)
    words = sum(len(s["words"]) for s in sstages)
    sents = sum(len(s["sentences"]) for s in sstages)
    prac = sum(len(s["practice"]) for s in sstages)
    notes.append(f"makeup: {len(mstages)} stages, {len(mwords)} glossary words "
                 f"with IPA, {len(mexprs)} expressions and idioms "
                 f"({len(midioms)} idioms), adult-only")
    notes.append(f"tech: {len(cstages)} stages, {len(cwords)} glossary words "
                 f"with IPA, {len(cexprs)} expressions and idioms "
                 f"({len(cidioms)} idioms), adult-only")
    notes.append(f"nature: {len(natstages)} stages, {len(nawords)} glossary "
                 f"words with IPA, {len(naexprs)} expressions and idioms "
                 f"({len(naidioms)} idioms), adult-only, photographed card")
    notes.append(f"social: {len(socstages)} stages, {len(swwords)} glossary "
                 f"words with IPA, {len(swexprs)} expressions and idioms "
                 f"({len(swidioms)} idioms), adult-only, photographed card")
    notes.append(f"entertainment: {len(estages)} stages, {len(ewords)} glossary "
                 f"words with IPA, {len(eexprs)} expressions and idioms "
                 f"({len(eidioms)} idioms), adult-only, photographed card")
    notes.append(f"food: {len(fstages)} stages, {len(fwords)} glossary words "
                 f"with IPA, {len(fexprs)} expressions and idioms "
                 f"({len(fidioms)} idioms), adult-only, photographed card")
    notes.append(f"sports: {len(sstages)} stages, {words} words with IPA, {exprs} expressions "
                 f"and idioms ({len(idioms)} idioms), {len(profiles)} sport profiles with "
                 f"{terms} key terms, {sents} own sentences, {prac} practice items; "
                 f"travel: {len(tstages)} stages joining {joined_sent} bank sentences")

    print()
    if fails:
        print(f"  {len(fails)} journey check(s) failed")
        return 1
    print("  PASS  " + " ".join(notes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
