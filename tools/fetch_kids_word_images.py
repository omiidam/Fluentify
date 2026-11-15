#!/usr/bin/env python3
"""Fetch one picture for every word a child is taught.

    python3 tools/fetch_kids_word_images.py            # everything missing
    python3 tools/fetch_kids_word_images.py apple cat  # only these
    python3 tools/fetch_kids_word_images.py --all      # refetch what exists

Where the pictures come from, and why that source:

  * Openverse (api.openverse.org) indexes Flickr, Wikimedia Commons and the
    rest, and can be asked for one licence class at a time. This asks for CC0
    and public domain only, so a card shown to a child carries no attribution
    obligation and no share-alike that would reach the app itself.
  * The query is written per word rather than taken from the word: "book"
    returns someone's book cover, "open book" returns a book. Each word's
    query lives in the table below, which is also the place to fix one that
    came back wrong.

What it writes:

  kids/words/<word>.jpg     480x360 centre crop, JPEG, under ~40 KB each, so
                            the whole set is a couple of megabytes inside the
                            APK rather than a download at first run
  kids/words/credits.json   title, creator, licence and the page each picture
                            came from - the record of what shipped, and the
                            file that makes a licence question answerable

The script is idempotent: a word that already has a file is skipped unless
--all is passed, so re-running it after fixing one query only fetches that one.
"""

from __future__ import annotations

import io
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "kids" / "words"
CREDITS = OUT / "credits.json"
API = "https://api.openverse.org/v1/images/"

WIDTH, HEIGHT = 480, 360
JPEG_QUALITY = 80

# word -> what to ask the index for. The query carries the disambiguator, so
# "bat" would become "bat animal" here rather than a sports bag of results.
QUERIES: dict[str, str] = {
    # at school
    "book": "open book pages",
    "pencil": "colored pencils",
    "teacher": "teacher classroom children",
    "desk": "wooden desk table",
    "bag": "backpack",
    "class": "classroom children learning",
    # family
    "mother": "mother and daughter walking",
    "father": "father and child",
    "sister": "sisters",
    "brother": "two brothers boys",
    "grandmother": "grandmother portrait",
    "cousin": "children",
    # animals
    "cat": "cat sitting looking at camera",
    "dog": "golden retriever dog",
    "bird": "robin bird on branch",
    "rabbit": "rabbit animal",
    "horse": "horse field",
    "fish": "goldfish fish tank",
    # food
    "apple": "red apple fruit",
    "bread": "sliced bread loaf",
    "milk": "glass of white milk",
    "rice": "bowl of rice",
    "egg": "chicken egg",
    "cake": "birthday cake",
    # play
    "ball": "soccer ball on grass",
    "game": "children playing game",
    "jump": "jumping",
    "run": "child running",
    "swim": "child swimming pool",
    "ride": "child riding bicycle",
    # weather
    "sun": "sunny sky",
    "rain": "rain falling on window",
    "cloud": "white clouds sky",
    "wind": "wind blowing tree",
    "snow": "snow winter",
    "star": "stars night sky",
    # feelings
    "tired": "yawning",
    "excited": "excited children",
    "scared": "scared child",
    "proud": "proud child",
    "calm": "relaxing nature",
    "lonely": "lonely child alone",
    # nature
    "tree": "big tree",
    "flower": "pink flower petals",
    "leaf": "green leaf",
    "river": "river landscape",
    "mountain": "mountain landscape",
    "grass": "green grass field",
    # body
    "head": "child head shoulders portrait",
    "hand": "open hand palm",
    "eye": "eye",
    "ear": "ear",
    "mouth": "child smiling face",
    "tooth": "human tooth",
    # clothes
    "shirt": "shirt clothes",
    "shoes": "pair of shoes",
    "hat": "hat cap",
    "socks": "pair of socks",
    "coat": "coat",
    "dress": "summer dress woman",
    # home
    "room": "bedroom room",
    "door": "wooden door",
    "window": "window house",
    "bed": "bed pillow bedroom",
    "chair": "single wooden chair",
    "kitchen": "kitchen cooking",
    # space
    "moon": "full moon",
    "planet": "planet space",
    "rocket": "rocket launch",
    "astronaut": "astronaut spacesuit",
    "spaceship": "space shuttle launch",
    "telescope": "telescope tripod sky",
    # tech
    "computer": "laptop computer on desk",
    "phone": "smartphone in hand",
    "tablet": "tablet computer",
    "screen": "laptop screen desk",
    "button": "red push button switch",
    "robot": "robot",
    # places
    "shop": "shop storefront",
    "park": "park green trees bench",
    "library": "library bookshelves",
    "hospital": "hospital emergency entrance",
    "bus": "yellow school bus",
    "street": "city street",
    # opposites
    "big": "big elephant",
    "small": "small flower close up macro",
    "happy": "happy smiling child",
    "sad": "sad child",
    "hot": "hot desert sun",
    "cold": "cold snow winter",
}


def api(query: str, source: str = "") -> list[dict]:
    params = {
        "q": query,
        "license": "cc0,pdm",
        "page_size": "20",
        "mature": "false",
    }
    if source:
        params["source"] = source
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Fluentify-kids-images/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r).get("results") or []
    except Exception:
        return []                                   # one dead source, not a dead run


# Results whose title says what they are and are not a photograph of the thing.
# The CC0 Flickr pool is full of scanned manuscripts, and "book" without a
# filter returns a wall of illuminated maps from Baltimore.
NOT_A_PICTURE = (
    "manuscript", "illuminat", "cartograph", "calligraph", "folio",
    "leaf from", "map of", "engrav", "woodcut", "etching", "lithograph",
    "painting", "drawing of", "sketch", "diagram", "uml", "chart", "graph",
    "banner", "logo", "poster", "clipart", "screenshot", "textbook",
    "document", "page of text", "stamp", "coin", "sign of",
)

# Stock libraries are shot for exactly this purpose: one concept, centred,
# clean light. Flickr is the wide net underneath them, Wikimedia the last
# resort (its files are often diagrams or museum scans).
SOURCES = (("stocksnap,rawpixel", 4), ("flickr", 1), ("wikimedia", 0))


# A handful of words where the best automatic pick was still wrong when the
# sheet was looked at: a city street for "eye", an engraving for "cousin".
# Each entry names the query that surfaces the picture and the index id to take
# from it, so the fix is recorded here instead of living in someone's shell
# history.
CHOSEN: dict[str, tuple[str, str]] = {
    "eye": ("eye", "0239f62d"),        # Eye Closeup
    "cousin": ("children friends playing", "4a49a440"),   # Children Happy
    "sister": ("sister", "c52bec5f"),   # Sisters Children
    "ear": ("ear", "00c86f0e"),         # Ear Earring
    "chair": ("wooden chair", "79adc2ee"),   # Wooden Chair
    "jump": ("jump", "1c44b0a3"),         # Jump Leap
}


def chosen_item(word: str) -> dict | None:
    query, prefix = CHOSEN[word]
    for item in api(query, "stocksnap,rawpixel"):
        if str(item.get("id") or "").startswith(prefix):
            return item
    return None


def score(item: dict, word: str, hint: str) -> int:
    tags = " ".join(str(t.get("name") or "") for t in (item.get("tags") or []))
    text = ((item.get("title") or "") + " " + tags).lower()
    s = 0
    if word in text:
        s += 6
    s += 2 * sum(1 for t in hint.split() if len(t) > 3 and t in text)
    if any(bad in text for bad in NOT_A_PICTURE):
        s -= 10
    w, h = item.get("width") or 0, item.get("height") or 0
    if min(w, h) < 400:
        s -= 4
    if w and h and 0.75 <= w / h <= 1.9:
        s += 2
    return s


def pick(word: str, hint: str) -> dict | None:
    """The best candidate over the sources, by what its title and tags say."""
    best, best_score = None, -99
    for source, bonus in SOURCES:
        for item in api(word + " " + hint, source):
            s = score(item, word, hint) + bonus
            if s > best_score:
                best, best_score = item, s
        if best_score >= 12:                      # a stock photo of the word itself
            break
        time.sleep(0.8)
    return best


def download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Fluentify-kids-images/1.0"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read()


def crop(raw: bytes) -> bytes:
    im = Image.open(io.BytesIO(raw))
    im = im.convert("RGB")
    target = WIDTH / HEIGHT
    w, h = im.size
    if w / h > target:                       # too wide: trim the sides
        new_w = int(h * target)
        left = (w - new_w) // 2
        im = im.crop((left, 0, left + new_w, h))
    else:                                    # too tall: trim top and bottom
        new_h = int(w / target)
        top = (h - new_h) // 3               # a little above centre: faces
        im = im.crop((0, top, w, top + new_h))
    im = im.resize((WIDTH, HEIGHT), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
    return buf.getvalue()


def load_credits() -> dict:
    if CREDITS.exists():
        try:
            return json.loads(CREDITS.read_text(encoding="utf-8"))
        except ValueError:
            return {}
    return {}


def keep(credits: dict, word: str, item: dict, query: str) -> None:
    credits[word] = {
        "q": query,
        "title": item.get("title") or "",
        "creator": item.get("creator") or "",
        "license": item.get("license") or "",
        "license_version": item.get("license_version") or "",
        "source": item.get("source") or "",
        "page": item.get("foreign_landing_url") or "",
        "file": "kids/words/" + word + ".jpg",
    }


def main(argv: list[str]) -> int:
    every = "--all" in argv
    only = [a for a in argv if not a.startswith("-")]
    OUT.mkdir(parents=True, exist_ok=True)
    credits = load_credits()

    words = [w for w in QUERIES if not only or w in only]
    missing = [w for w in words if every or only or not (OUT / (w + ".jpg")).exists()]
    print(f"{len(QUERIES)} words known, {len(words)} in scope, {len(missing)} to fetch")

    done = 0
    for i, word in enumerate(missing, 1):
        query = QUERIES[word]
        try:
            item = chosen_item(word) if word in CHOSEN else pick(word, query)
            if not item:
                print(f"  {i:3d}/{len(missing)}  {word:11s} no result for {query!r}")
                continue
            url = item.get("thumbnail") or item.get("url")
            raw = download(url)
            data = crop(raw)
            (OUT / (word + ".jpg")).write_bytes(data)
            keep(credits, word, item, query)
            done += 1
            print(f"  {i:3d}/{len(missing)}  {word:11s} {len(data)//1024:3d} KB  "
                  f"{item.get('license','?').upper():4s} {item.get('source','?')}")
        except Exception as exc:                      # one bad result, not 90
            print(f"  {i:3d}/{len(missing)}  {word:11s} failed: {exc}")
        time.sleep(1.2)                              # be a polite anonymous client

    CREDITS.write_text(json.dumps(credits, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                       encoding="utf-8")
    print(f"\n{done} fetched, {len(credits)} credited in {CREDITS.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
