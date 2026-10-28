#!/usr/bin/env python3
"""Draw the fox sticker set from the reference sheet, into foxes.json.

The picker is one sheet of 36 drawings: six rows of six. Content stays content
- the page still reads foxes.json and nothing here runs at app time - but the
drawings are built from a shared vocabulary (one face, one side head, four
bodies) instead of 36 hand-typed blobs, so a change to the palette or to the
eyes reaches every sticker that uses them.

    python3 tools/build_foxes.py

The 64x64 viewBox belongs to the wrapper the page draws (`.stk`), so nothing
here may carry one; and nothing here may carry a script, an href or an event
attribute - the page inserts these with innerHTML.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "foxes.json"

RED = "#d2603e"      # the fox
SHADE = "#b74b2c"    # the same fox, a step darker
DARK = "#2b1a12"     # eyes, nose, ear leather
CREAM = "#fff5e8"    # muzzle, chest, tail tip

# ---------------------------------------------------------------- primitives

EAR_L = f'<path d="M13 22 L9 3 L27 13 Z" fill="{RED}"/>'
EAR_R = f'<path d="M51 22 L55 3 L37 13 Z" fill="{RED}"/>'
INNER_L = f'<path d="M15.4 19 L12.8 7.2 L23.6 14 Z" fill="{DARK}" opacity=".85"/>'
INNER_R = f'<path d="M48.6 19 L51.2 7.2 L40.4 14 Z" fill="{DARK}" opacity=".85"/>'
SKULL = (f'<path d="M12 21 C12 13.5 20 9 32 9 C44 9 52 13.5 52 21 C52 30.5 '
         f'42.5 44 32 44 C21.5 44 12 30.5 12 21 Z" fill="{RED}"/>')
MUZZLE = (f'<path d="M20 25 C20 20.5 25 18 32 18 C39 18 44 20.5 44 25 C44 32.5 '
          f'38.5 40.5 32 40.5 C25.5 40.5 20 32.5 20 25 Z" fill="{CREAM}"/>')
NOSE = f'<path d="M29 25.2 h6 l-3 3.2 z" fill="{DARK}"/>'
SMIRK = (f'<path d="M29.1 32.2 q2.9 3 5.8 0" fill="none" stroke="{DARK}" '
         f'stroke-width="1.5" stroke-linecap="round"/>')


def eyes(mood: str = "calm") -> str:
    """One pair of eyes; the mood is the whole character budget of a sticker."""
    arc = ('M22.4 23.4 q2.6 -3.4 5.2 0" fill="none" stroke="{}" '
           'stroke-width="1.9" stroke-linecap="round"/>')
    up = (f'<path d="{arc.format(DARK)}'
          f'<path d="M36.4 23.4 q2.6 -3.4 5.2 0" fill="none" stroke="{DARK}" '
          f'stroke-width="1.9" stroke-linecap="round"/>')
    shut = up.replace("-3.4", "3.2")
    if mood == "happy":
        return up
    if mood == "sleep":
        return shut
    if mood == "wide":
        return (f'<circle cx="25" cy="22.4" r="2.7" fill="{DARK}"/>'
                f'<circle cx="39" cy="22.4" r="2.7" fill="{DARK}"/>'
                f'<circle cx="25.9" cy="21.5" r=".9" fill="{CREAM}"/>'
                f'<circle cx="39.9" cy="21.5" r=".9" fill="{CREAM}"/>')
    if mood == "star":
        star = (f'<path d="M25 18.6 l1.3 3.1 3.1 1.3 -3.1 1.3 -1.3 3.1 '
                f'-1.3 -3.1 -3.1 -1.3 3.1 -1.3 Z" fill="{DARK}"/>')
        star2 = (f'<path d="M39 18.6 l1.3 3.1 3.1 1.3 -3.1 1.3 -1.3 3.1 '
                 f'-1.3 -3.1 -3.1 -1.3 3.1 -1.3 Z" fill="{DARK}"/>')
        return star + star2
    if mood == "angry":
        return (f'<path d="M21 18.6 L28.6 21.6" stroke="{DARK}" stroke-width="2.2" '
                f'stroke-linecap="round"/>'
                f'<path d="M43 18.6 L35.4 21.6" stroke="{DARK}" stroke-width="2.2" '
                f'stroke-linecap="round"/>'
                f'<circle cx="25.5" cy="24" r="1.9" fill="{DARK}"/>'
                f'<circle cx="38.5" cy="24" r="1.9" fill="{DARK}"/>')
    if mood == "wink":
        return (f'<path d="M22.4 23.4 q2.6 -3.4 5.2 0" fill="none" '
                f'stroke="{DARK}" stroke-width="1.9" stroke-linecap="round"/>'
                f'<circle cx="39" cy="22.4" r="2" fill="{DARK}"/>')
    return (f'<circle cx="25" cy="22.3" r="2" fill="{DARK}"/>'
            f'<circle cx="39" cy="22.3" r="2" fill="{DARK}"/>')


def face(mood: str = "calm", tf: str = "") -> str:
    """The front head: two ears, the skull, the cream muzzle, eyes, nose, mouth."""
    inner = (f'<g transform="{tf}">' if tf else "<g>") + \
        EAR_L + EAR_R + SKULL + MUZZLE + eyes(mood) + NOSE + SMIRK + "</g>"
    return inner


def side_head(mood: str = "calm", tf: str = "", ear: str = "back") -> str:
    """The head in profile, looking right, with the snout as a point."""
    eye = (f'<circle cx="29" cy="21.6" r="2.1" fill="{DARK}"/>' if mood != "sleep"
           else f'<path d="M26.6 21.8 q2.4 2.6 4.8 0" fill="none" stroke="{DARK}" '
                f'stroke-width="1.8" stroke-linecap="round"/>')
    if mood == "happy":
        eye = (f'<path d="M26.8 22.4 q2.4 -3 4.8 0" fill="none" stroke="{DARK}" '
               f'stroke-width="1.9" stroke-linecap="round"/>')
    return (
        (f'<g transform="{tf}">' if tf else "<g>") +
        f'<path d="M14 22 L10 4 L29 14 Z" fill="{RED}"/>'
        f'<path d="M16.4 20 L13.8 7.6 L26 15 Z" fill="{DARK}" opacity=".82"/>'
        f'<circle cx="27" cy="25" r="12.6" fill="{RED}"/>'
        f'<path d="M36 19.4 L54 25 L36 30 Z" fill="{RED}"/>'
        f'<path d="M37.6 24.6 L52.4 25.2 L37.6 28.6 Z" fill="{CREAM}"/>'
        + eye +
        f'<path d="M50.4 23.4 l3.6 1.6 -3.6 1.8 z" fill="{DARK}"/>'
        "</g>")


def tail_up(tf: str = "", flip: bool = False) -> str:
    """A bushy tail sweeping up and out, cream tip - the standing silhouette."""
    s = -1 if flip else 1
    cx = 32

    def x(v: float) -> float:
        return cx + s * (v - cx)

    return (f'<g transform="{tf}">'
            f'<path d="M{x(16)} 38 C{x(4)} 34 {x(2)} 22 {x(8)} 12 '
            f'C{x(10)} 20 {x(16)} 27 {x(24)} 30 Z" fill="{RED}"/>'
            f'<path d="M{x(9)} 16 C{x(10)} 20 {x(13)} 24 {x(17)} 26 '
            f'C{x(13)} 24 {x(10)} 21 {x(9)} 16 Z" fill="{CREAM}"/>'
            "</g>")


def legs(y: int = 45, h: int = 13) -> str:
    return "".join(
        f'<rect x="{ax}" y="{y}" width="5" height="{h}" rx="2.5" fill="{RED}"/>'
        f'<rect x="{ax + 3}" y="{y + h - 3}" width="2" height="3" rx="1" fill="{DARK}"/>'
        for ax in (17, 27, 36, 45))


def body_stand(tf: str = "", belly: bool = True) -> str:
    """In profile, on all fours, facing right - walk, hunt, run, sneak."""
    return (f'<g transform="{tf}">'
            + legs() +
            f'<ellipse cx="33" cy="38" rx="18" ry="12" fill="{RED}"/>'
            + (f'<ellipse cx="34" cy="43" rx="13" ry="6.4" fill="{CREAM}"/>' if belly else "") +
            "</g>")


def body_sit(tf: str = "", paws: bool = True, tail: bool = True) -> str:
    """Sitting upright: a bell of a body with two front paws on the ground."""
    out = (f'<g transform="{tf}">'
           f'<path d="M9 58 C5 45.5 17 33.5 32 33.5 C47 33.5 59 45.5 55 58 Z" fill="{RED}"/>'
           f'<path d="M20 56 C18.6 47 24 40.5 32 40.5 C40 40.5 45.4 47 44 56 Z" fill="{CREAM}"/>')
    if paws:
        out += (f'<ellipse cx="22.6" cy="56" rx="5" ry="3.4" fill="{CREAM}"/>'
                f'<ellipse cx="41.4" cy="56" rx="5" ry="3.4" fill="{CREAM}"/>')
    if tail:
        out += (f'<path d="M46 57 C61 57.5 67 44 59 33.5 C56.5 29.6 50.6 30.6 51 35.4 '
                f'C51.6 42 46.5 46.6 40 49.4 Z" fill="{RED}"/>'
                f'<path d="M56.6 33.6 C58.6 28.8 63.6 30 63.2 35 C62.6 40 57.6 41.4 '
                f'54 39.2 Z" fill="{CREAM}"/>')
    return out + "</g>"


def body_curl(tf: str = "") -> str:
    """Curled into a ball, tail wrapped round the front."""
    return (f'<g transform="{tf}">'
            f'<path d="M54 40 C59 27 48 16 35 16 C22 16 11 26 12 40 '
            f'C13 51.5 23 58 35 57 C46 56 51.6 49 54 40 Z" fill="{RED}"/>'
            f'<path d="M17.5 47 C22 55 33 57.5 42.5 53.5 C47.5 51.2 50.5 46.5 51.5 42 '
            f'C47 51 35 54.5 27 51.5 C22.5 49.8 19.6 48 17.5 47 Z" fill="{CREAM}"/>'
            "</g>")


def big_tail(tf: str = "", flip: bool = False) -> str:
    """The tail on its own, thick as the fox - the sheet's TAIL and RELAX poses."""
    s = -1 if flip else 1

    def x(v: float) -> float:
        return 32 + s * (v - 32)

    return (f'<g transform="{tf}">'
            f'<path d="M{x(20)} 46 C{x(6)} 44 {x(2)} 30 {x(10)} 18 '
            f'C{x(14)} 26 {x(20)} 32 {x(28)} 35 Z" fill="{RED}"/>'
            f'<path d="M{x(11)} 22 C{x(12)} 28 {x(16)} 33 {x(21)} 36 '
            f'C{x(15)} 34 {x(11)} 29 {x(11)} 22 Z" fill="{CREAM}"/>'
            "</g>")


def zzz(x: int = 40, y: int = 10, o: float = .5) -> str:
    return (f'<path d="M{x} {y} h7 l-7 5.2 h7" fill="none" stroke="{DARK}" '
            f'stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round" '
            f'opacity="{o}"/>')


def sparkle(cx: float, cy: float, r: float, o: float = .9) -> str:
    """A four-point star: two quadratics per arm, so it reads at 46px."""
    a, b = round(r * .3, 2), round(r * .7, 2)
    return (f'<path d="M{cx} {cy - r} q{a} {b} {r} {r} q-{b} {a} -{r} {r} '
            f'q-{a} -{b} -{r} -{r} q{b} -{a} {r} -{r} Z" fill="{DARK}" '
            f'opacity="{o}"/>')


def bow(cx: float, cy: float, s: float = 1.0, on_cream: bool = False) -> str:
    """A bow. It changes colour with what is under it: cream on the red body,
    shade on the cream chest, or it disappears into its own background."""
    fill, line = (SHADE, DARK) if on_cream else (CREAM, SHADE)
    wing = (f'fill="{fill}" stroke="{line}" stroke-width="1.2" '
            f'stroke-linejoin="round"')
    return (f'<g transform="translate({cx},{cy}) scale({s})">'
            f'<path d="M0 0 C-9 -6 -15 -1 -13 3 C-11 7 -4 5 0 0 Z" {wing}/>'
            f'<path d="M0 0 C9 -6 15 -1 13 3 C11 7 4 5 0 0 Z" {wing}/>'
            f'<circle cx="0" cy="1" r="2.3" fill="{line}"/>'
            "</g>")


def fit(art: str, s: float = .9) -> str:
    """Scale a finished drawing about the box's centre.

    The poses are composed from parts, so a head lifted onto a body can push
    an ear past y=0 - which the SVG viewport then cuts flat. Every sticker goes
    through here at the end, so the set shares one margin and no ear is a
    straight line.
    """
    return (f'<g transform="translate(32,32) scale({s}) translate(-32,-32)">'
            f'{art}</g>')


# The seated poses all lift the same head onto the same bell of a body.
#
# Scaled about the face's own centre, not the box corner: scale(.84) alone
# multiplies every x by .84 too, so the head slid 5px left of the body it was
# standing on - visible as a fox leaning away from its own chest.
SIT_HEAD = 'translate(32,19) scale(.84) translate(-32,-21)'


def book(y: int = 39) -> str:
    return (f'<path d="M8 {y} C17.5 {y - 4} 26.5 {y - 3} 32 {y + 1} '
            f'C37.5 {y - 3} 46.5 {y - 4} 56 {y} L56 {y + 18} '
            f'C46.5 {y + 14} 37.5 {y + 15} 32 {y + 19} '
            f'C26.5 {y + 15} 17.5 {y + 14} 8 {y + 18} Z" fill="{CREAM}" '
            f'stroke="{SHADE}" stroke-width="1.7" stroke-linejoin="round"/>'
            f'<path d="M32 {y + 1} v18" stroke="{SHADE}" stroke-width="1.7"/>'
            f'<path d="M13 {y + 6} h14 M13 {y + 10} h14 M37 {y + 6} h14 M37 {y + 10} h14" '
            f'stroke="{SHADE}" stroke-width="1.4" stroke-linecap="round" opacity=".5"/>')


# ------------------------------------------------------------------ the set
#
# One entry per drawing on the sheet, six rows of six, in reading order. The
# ids are the sheet's own labels; where a label appears twice (three FUNNY,
# three WALKING, two CUTE, two COOL, two GLAMOUR, two RELAX, two SLEEP) the
# second keeps a suffix, because [fox:id] needs them to differ.

HANDLE = (f'<path d="M20 9 C24 -1 40 -1 44 9" fill="none" stroke="{SHADE}" '
          f'stroke-width="2.6" stroke-linecap="round"/>')
ASK = (f'<path d="M47 6.5 C47 2.5 51.5 1.4 54 3.4 C56.4 5.4 54.2 8 52 9.2 '
       f'L52 12" fill="none" stroke="{DARK}" stroke-width="2.1" '
       f'stroke-linecap="round"/>'
       f'<circle cx="52" cy="16.4" r="1.4" fill="{DARK}"/>')
RUFF = (f'<path d="M17 43 l4 -10 4 10 4 -10 4 10 4 -10 4 10 4 -10 4 10 Z" '
        f'fill="{RED}"/>')
MASK = (f'<path d="M11 18.6 C11 15 20 13 32 13 C44 13 53 15 53 18.6 '
        f'L53 24.4 C53 28 44 30 32 30 C20 30 11 28 11 24.4 Z" '
        f'fill="{DARK}" opacity=".86"/>'
        f'<circle cx="25" cy="21.6" r="2.1" fill="{CREAM}"/>'
        f'<circle cx="39" cy="21.6" r="2.1" fill="{CREAM}"/>')


def build() -> list[dict]:
    out: list[dict] = []

    def add(sid: str, name: str, fa: str, kw: str, svg: str) -> None:
        out.append({"id": sid, "name": name, "fa": fa, "kw": kw, "svg": svg})

    # 1-6 ------------------------------------------------------------- row one
    add("cute", "cute", "ناز",
        "cute sweet adorable sitting paw ناز بامزه دوست‌داشتنی نشسته",
        body_sit() + face(tf=SIT_HEAD))

    add("walking", "walking", "در حال راه رفتن",
        "walking walk stroll side در حال راه رفتن قدم زدن",
        tail_up() + body_stand() + side_head(tf="translate(7,-1) scale(.9)"))

    add("fashion", "fashion", "مد روز",
        "fashion style chic looking back مد روز خوش‌استایل",
        body_curl(tf="translate(2,4) scale(.9)")
        + side_head(tf="translate(-4,-2) scale(.9)") + sparkle(54, 9, 4.2))

    add("baby", "baby", "بچه‌روباه",
        "baby small cub tiny little بچه روباه کوچک نوزاد",
        body_curl(tf="translate(3,4) scale(.88)") + face(tf="translate(7,3) scale(.46)")
        + zzz(52, 12, .38))

    add("funny", "funny", "خنده‌دار",
        "funny silly goofy wide eyes خنده‌دار بامزه شیطون",
        face(mood="wide", tf="translate(0,3)"))

    add("funny-sit", "funny sit", "بامزه نشسته",
        "funny sitting wink playful بامزه نشسته شیطون چشمک",
        body_sit() + face(mood="wink", tf=SIT_HEAD))

    # 7-12 ------------------------------------------------------------- row two
    add("winner", "winner", "برنده",
        "winner gold star best first برنده ستاره بهترین اول",
        body_curl(tf="translate(0,4) scale(.94)") + face(mood="happy", tf="translate(-2,-4) scale(.62)")
        + sparkle(49, 12, 4.6) + sparkle(58, 21, 3))

    add("cool", "cool", "خفن",
        "cool proud confident raised head خفن مغرور با اعتماد به نفس",
        tail_up() + body_stand() + side_head(tf="translate(6,-7) scale(.92)"))

    add("mask", "mask", "ماسک",
        "mask bandit band mask disguise ماسک دزد نقاب",
        face(tf="translate(0,2)") + MASK)

    add("glamour", "glamour", "شیک",
        "glamour bow pretty fancy elegant شیک زیبا پاپیون",
        body_sit() + face(mood="happy", tf=SIT_HEAD) + bow(32, 49, .5, on_cream=True))

    add("hunter", "hunter", "شکارچی",
        "hunter hunt prowl low stalking شکارچی شکار خزیدن",
        body_stand(tf="scale(1.05,.9) translate(0,4)")
        + side_head(tf="translate(1,6) scale(.86)")
        + f'<path d="M6 22 h9 M4 28 h8" stroke="{DARK}" stroke-width="2" '
          f'stroke-linecap="round" opacity=".35"/>')

    add("shopping", "shopping", "خرید",
        "shopping bag shop buy خرید خرید کردن کیسه",
        face(tf="translate(0,4)") + HANDLE)

    # 13-18 ----------------------------------------------------------- row three
    add("angry", "angry", "عصبانی",
        "angry cross grumpy upset عصبانی بداخلاق",
        body_sit() + face(mood="angry", tf=SIT_HEAD))

    add("relax", "relax", "آرام",
        "relax calm rest easy آرام ریلکس استراحت",
        body_curl(tf="translate(0,3) scale(.92)")
        + face(mood="sleep", tf="translate(-6,-2) scale(.64)") + zzz(52, 7, .42))

    add("read", "read", "مطالعه",
        "read book study lesson کتاب درس مطالعه",
        face(tf="translate(0,-5) scale(.84)") + book())

    add("question", "question", "سؤال",
        "question why curious confused سوال چرا کنجکاو گیج",
        face(tf="translate(-4,-3) scale(.9)") + ASK)

    add("dog", "dog", "شبیه سگ",
        "dog puppy sitting loyal سگ توله وفادار",
        tail_up(tf="translate(0,7)") + body_stand(tf="scale(1.02,.78) translate(0,12)")
        + side_head(tf="translate(3,10) scale(.82)"))

    add("sleep", "sleep", "خواب",
        "sleep tired night bedtime zzz خواب خسته شب",
        body_curl() + face(mood="sleep", tf="translate(-5,-2) scale(.6)")
        + zzz(44, 11, .5) + zzz(52, 4, .32))

    # 19-24 ----------------------------------------------------------- row four
    add("tail", "tail", "دُم",
        "tail bushy brush fluffy دُم پشمالو",
        # a tail the size of its fox, with the fox as the small part
        f'<path d="M22 58 C8 54 2 38 8 21 C12 9 20 5 26 9 C30 34 28 48 34 58 Z" '
        f'fill="{RED}"/>'
        f'<path d="M11 23 C12 35 17 45 24 51 C16 47 10 37 11 23 Z" fill="{CREAM}"/>'
        + face(tf="translate(24,32) scale(.5)"))

    add("happy", "happy", "خوشحال",
        "happy smile joy grin شاد خوشحال لبخند",
        body_sit() + face(mood="happy", tf=SIT_HEAD))

    add("holidays", "holidays", "تعطیلات",
        "holidays run jumping excited تعطیلات دویدن شادی",
        body_stand(tf="rotate(-9 32 38)") + side_head(mood="happy", tf="translate(6,-5) scale(.9)")
        + sparkle(9, 16, 3.4, .45) + sparkle(56, 12, 2.6, .4))

    add("fuzzy", "fuzzy", "پشمالو",
        "fuzzy fluffy fur ruff پشمالو کرکی یال",
        RUFF + face(tf="translate(0,-2) scale(.9)"))

    add("nice-view", "nice view", "منظره قشنگ",
        "nice view behind back looking away منظره پشت روباه",
        # From behind: the back of the head, and the tail held up in front of
        # it. The tail is a shade darker on purpose - same colour on same body
        # was an egg with ears, not a fox.
        f'<path d="M12 40 C12 26 21 17 32 17 C43 17 52 26 52 40 C52 54 43 61 32 61 '
        f'C21 61 12 54 12 40 Z" fill="{RED}"/>'
        f'<path d="M11 27 L6 7 L27 19 Z" fill="{RED}"/>'
        f'<path d="M53 27 L58 7 L37 19 Z" fill="{RED}"/>'
        f'<path d="M12 40 C12 30 20 23 32 23 C44 23 52 30 52 40 C45 34 39 32 32 32 '
        f'C25 32 19 34 12 40 Z" fill="{SHADE}" opacity=".45"/>'
        # the tail in front of the back, outlined so the two separate
        f'<path d="M30 58 C24 44 24 24 31 10 C34 5 38 5 41 10 C48 24 47 44 41 58 Z" '
        f'fill="{RED}" stroke="{SHADE}" stroke-width="2"/>'
        f'<path d="M31 15 C34 9 38 9 40 15 C42 21 37 25 34 21 Z" fill="{CREAM}"/>')

    add("fly", "fly", "پرواز",
        "fly flying leap jump wings پرواز پریدن جهش",
        body_stand(tf="rotate(-17 32 40)") + tail_up()
        + side_head(mood="happy", tf="translate(4,-9) scale(.88)")
        + f'<path d="M4 44 h10 M6 50 h8" stroke="{DARK}" stroke-width="2" '
          f'stroke-linecap="round" opacity=".3"/>')

    # 25-30 ----------------------------------------------------------- row five
    add("eyes", "eyes", "چشم‌ها",
        "eyes look stare glance چشم نگاه",
        f'<path d="M18 34 C18 14 25 5 32 5 C39 5 46 14 46 34 C46 51 39 59 32 59 '
        f'C25 59 18 51 18 34 Z" fill="{RED}"/>'
        f'<path d="M18 30 L11 4 L33 21 Z" fill="{RED}"/>'
        f'<path d="M46 30 L53 4 L31 21 Z" fill="{RED}"/>'
        f'<path d="M26 52 C28 46 36 46 38 52 C36 56 28 56 26 52 Z" fill="{CREAM}"/>'
        f'<circle cx="26.6" cy="30" r="2.5" fill="{DARK}"/>'
        f'<circle cx="37.4" cy="30" r="2.5" fill="{DARK}"/>'
        f'<path d="M30 50 h4 l-2 2.4 Z" fill="{DARK}"/>')

    add("cute-sit", "cute sitting", "ناز نشسته",
        "cute sitting paw raised sweet ناز نشسته پنجه",
        body_sit() + face(mood="happy", tf=SIT_HEAD)
        + f'<path d="M47 47 C54 43 57 36 55 29" fill="none" stroke="{RED}" '
          f'stroke-width="4.6" stroke-linecap="round"/>'
        + f'<path d="M53 28 C55 25 58 26 58 29 C58 32 55 33.4 52.6 32 Z" fill="{CREAM}"/>')

    add("face", "face", "چهره",
        "face head portrait front چهره صورت روباه",
        face(tf="translate(0,2)"))

    add("sneak", "walking low", "راه رفتن آهسته",
        "sneak walk low crawl careful آهسته راه رفتن خزیدن",
        tail_up(tf="translate(0,2)") + body_stand(tf="scale(1.08,.82) translate(-1,8)")
        + side_head(tf="translate(3,7) scale(.84)"))

    add("relax-curl", "relax curled", "لم دادن",
        "relax curled lying lazy لم دادن دراز کشیدن",
        body_curl(tf="translate(0,3)")
        + f'<path d="M12 42 C8 30 16 20 30 18 C34 17.4 36 20 33 22 C24 26 18 34 18 44 Z" '
          f'fill="{CREAM}"/>'
        + face(mood="sleep", tf="translate(-5,-3) scale(.62)"))

    add("glamour-bow", "glamour bow", "شیک با پاپیون",
        "glamour bow fancy pretty شیک پاپیون خوش‌پوش",
        body_sit() + face(mood="happy", tf=SIT_HEAD) + bow(32, 7, .58)
        + sparkle(52, 22, 3.2, .5))

    # 31-36 ----------------------------------------------------------- row six
    add("logo", "logo", "لوگو",
        "logo mark simple minimal لوگو نشان ساده",
        f'<path d="M12 42 L18 8 L32 27 L46 8 L52 42 C44 55 20 55 12 42 Z" fill="{RED}"/>'
        f'<path d="M23 44 C25 38 39 38 41 44 C38 51 26 51 23 44 Z" fill="{CREAM}"/>'
        f'<circle cx="26" cy="32" r="1.9" fill="{DARK}"/>'
        f'<circle cx="38" cy="32" r="1.9" fill="{DARK}"/>'
        f'<path d="M30 40.4 h4 l-2 2.4 Z" fill="{DARK}"/>')

    add("funny-head", "funny head", "سر بامزه",
        "funny head tall ears goofy سر بامزه گوش بلند",
        f'<path d="M10 30 L4 2 L26 17 Z" fill="{RED}"/>'
        f'<path d="M54 30 L60 2 L38 17 Z" fill="{RED}"/>'
        + face(mood="wide", tf="translate(0,4)"))

    add("cool-sit", "cool sitting", "خفن نشسته",
        "cool sitting confident side خفن نشسته",
        body_sit() + face(mood="calm", tf=SIT_HEAD)
        + f'<path d="M20 16.4 h11.4 v4.6 a3.4 3.4 0 0 1 -3.4 3.4 h-4.6 a3.4 3.4 0 0 1 '
          f'-3.4 -3.4 Z" fill="{DARK}"/>'
        + f'<path d="M34 16.4 h11.4 v4.6 a3.4 3.4 0 0 1 -3.4 3.4 h-4.6 a3.4 3.4 0 '
          f'0 1 -3.4 -3.4 Z" fill="{DARK}"/>'
        + f'<path d="M31.2 17.6 h3" stroke="{DARK}" stroke-width="1.8"/>')

    add("walk-tall", "walking tall", "راه رفتن ایستاده",
        "walking tall upright standing راه رفتن ایستاده بلند",
        tail_up(tf="translate(0,2)")
        + f'<path d="M21 28 C15 35 14 47 17 58 L47 58 C50 47 49 35 43 28 Z" fill="{RED}"/>'
        + f'<path d="M26 34 C24 43 24 51 25 58 L39 58 C40 51 40 43 38 34 Z" fill="{CREAM}"/>'
        + face(tf=SIT_HEAD))

    add("sleep-curl", "sleep curled", "خوابیده",
        "sleep curled ball night zzz خواب خوابیده توپ",
        body_curl(tf="translate(0,4)") + face(mood="sleep", tf="translate(1,-1) scale(.56)")
        + zzz(50, 12, .45))

    add("cute-face", "cute face", "چهره ناز",
        "cute face happy sweet چهره ناز خوشحال",
        face(mood="happy", tf="translate(0,3)") + sparkle(54, 10, 3.4, .5))

    return out


def main() -> int:
    stickers = build()
    ids = [s["id"] for s in stickers]
    assert len(set(ids)) == len(ids), "duplicate sticker ids"
    for s in stickers:
        art = s["svg"]
        assert "viewBox" not in art and "<script" not in art and "href" not in art
        assert not any(f" on{w}=" in art for w in ("load", "error", "click"))
        assert len(art) < 4000, s["id"]
        s["svg"] = fit(art)

    doc = {
        "_readme": (
            "Fox stickers for the composer's picker. Content, not code: add or "
            "edit an entry here and the picker, the web app and the APK all "
            "follow. Each sticker draws inside a 64x64 box, is inserted into a "
            "message as [fox:id], and is rendered back to the picture in the "
            "bubble. Keywords are lowercase and also carry the Persian so a "
            "learner can search in either language. The drawings are generated "
            "by tools/build_foxes.py from one shared fox vocabulary, so edit the "
            "pose there and re-run it rather than hand-patching a path here."),
        "label": "Foxes",
        "label_fa": "روباه‌ها",
        "stickers": stickers,
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {OUT} - {len(stickers)} stickers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
