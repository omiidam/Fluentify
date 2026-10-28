#!/usr/bin/env python3
"""Builds Fluentify's mark from one illustration.

The mascot is a picture now, not geometry. One source file
(brand/fox-source.png - the illustration the brand was chosen from) produces
everything that draws it:

    brand/fox-mark.png          the whole figure, transparent - boot screen
    brand/fox-face.png          the head, transparent - header + message avatars
    android/.../mipmap-*/       the launcher icon, every density, both shapes

Nothing is drawn per surface. Every copy is the same crop of the same file, so
the icon in the launcher cannot drift from the picture in the app - which is
exactly what happened when the boot screen carried a hand-redrawn copy of the
header's SVG: the two were meant to be one animal and were not.

The source is a cut-out with a transparent background, so no circular mask is
applied to what the app draws: the picture already carries its own silhouette,
and a disc around it would put back the border the artwork does not have. Only
the launcher's legacy icons - which have no background layer of their own - are
composited onto paper.

Crops are recorded here once, as fractions of the source, so a re-cut is an
edit to this file rather than an afternoon of eyeballing a canvas, and a new
export of the same artwork at another size still lines up.

    python3 tools/build_brand.py
"""

import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:                                  # pragma: no cover
    # Only this generator needs Pillow; the app, the CI build and every check
    # run on the standard library alone, so this is a tool you install when you
    # re-cut the art, not a dependency of the project.
    raise SystemExit("build_brand: needs Pillow to cut the pictures - "
                     "pip install pillow")

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "brand" / "fox-source.png"
BRAND = ROOT / "brand"

# The paper the launcher composites legacy icons onto: the illustration's own
# cream, so the cut-out has no seam against the tile it stands on.
CREAM = (253, 250, 241, 255)

# Alpha below this is export dust around the artwork, not the artwork: it is
# what "trim to the picture" ignores when it finds the figure's edges.
ALPHA_FLOOR = 24

# Air around the figure inside its square, as a fraction of the longest side.
# The cut-out is 1136x1207 of picture, so trimming alone would leave the tail
# touching one edge and the beret the other.
MARK_PAD = 0.04

# The head: beret, spectacles, muzzle, and the neckerchief under it. In
# fractions of the source, so it survives a re-export at another resolution.
# Centred on the face rather than on the figure - at 26 px in a message row a
# full-length portrait reads as an orange smudge, a face reads as a fox.
FACE_BOX = (0.235, 0.010, 0.645, 0.402)
FACE_PAD = 0.020

# Android: the icon is generated at every density rather than scaled by the
# launcher. mdpi is the baseline, and each step is 1.5x the one before it.
DENSITIES = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
MIPMAP = ROOT / "android/app/src/main/res"

# Adaptive icons are a 108dp layer whose visible viewport is the central 72dp
# (66dp is the guaranteed safe zone). The art is that 72dp including its own
# padding, so the figure lands at roughly 66dp: no mask shape and no launcher's
# crop can take the hat or the tail with it, while the icon still looks filled.
ADAPTIVE_DP = 108
ART_DP = 72

# Legacy (API 24-25) icons are drawn as-is, so they carry their own shape and
# padding: a rounded square of paper with the character standing on it.
LEGACY_ART = 0.88
LEGACY_RADIUS = 0.22


def trimmed(im: Image.Image) -> Image.Image:
    """The picture without the empty margin around it."""
    box = im.getchannel("A").point(
        lambda v: 255 if v > ALPHA_FLOOR else 0).getbbox()
    if box is None:
        raise ValueError("the crop contains no visible pixels")
    return im.crop(box)


def square(im: Image.Image, size: int, pad: float) -> Image.Image:
    """The crop, trimmed, scaled to fit a transparent square of air."""
    im = trimmed(im)
    inner = max(1, int(round(size * (1 - 2 * pad))))
    scale = min(inner / im.width, inner / im.height)
    im = im.resize((max(1, int(round(im.width * scale))),
                    max(1, int(round(im.height * scale)))), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.alpha_composite(im, ((size - im.width) // 2, (size - im.height) // 2))
    return out


def composed(art_im: Image.Image, size: int, shape: str) -> Image.Image:
    """The character standing on paper, in a rounded square or a disc."""
    canvas = Image.new("RGBA", (size, size), CREAM)
    d = int(round(size * LEGACY_ART))
    canvas.alpha_composite(art_im.resize((d, d), Image.LANCZOS),
                           ((size - d) // 2, (size - d) // 2))
    mask = Image.new("L", (size * 4, size * 4), 0)
    draw = ImageDraw.Draw(mask)
    if shape == "round":
        draw.ellipse((0, 0, size * 4 - 1, size * 4 - 1), fill=255)
    else:
        draw.rounded_rectangle((0, 0, size * 4 - 1, size * 4 - 1),
                               radius=int(size * 4 * LEGACY_RADIUS), fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(canvas, (0, 0), mask.resize((size, size), Image.LANCZOS))
    return out


def box_px(box: tuple[float, float, float, float], w: int, h: int):
    """A fractional crop as source pixels, snapped inward."""
    return (int(round(box[0] * w)), int(round(box[1] * h)),
            int(round(box[2] * w)), int(round(box[3] * h)))


def main() -> int:
    if not SOURCE.exists():
        return _fail(f"{SOURCE.relative_to(ROOT)} is missing - it is the one "
                     "picture every Fluentify mark is cut from")
    src = Image.open(SOURCE).convert("RGBA")
    w, h = src.size
    face_box = box_px(FACE_BOX, w, h)
    for name, box in (("face", face_box),):
        if not (0 <= box[0] < box[2] <= w and 0 <= box[1] < box[3] <= h):
            return _fail(f"the {name} crop {box} falls outside the {w}x{h} source")

    # ---- what the app draws ------------------------------------------------
    # 400 px covers the boot mark at 3x density; 256 the message avatar at 4x
    # (26 CSS px). Both keep their transparency, so whatever is behind them -
    # the boot screen's glow, the header's sand - shows through the gaps in the
    # silhouette instead of being squared off by an opaque tile.
    mark = square(src, 400, MARK_PAD)
    face = square(src.crop(face_box), 256, FACE_PAD)
    BRAND.mkdir(exist_ok=True)
    mark.save(BRAND / "fox-mark.png", optimize=True)
    face.save(BRAND / "fox-face.png", optimize=True)

    # ---- what the launcher draws -------------------------------------------
    written = []
    for density, px in DENSITIES.items():
        folder = MIPMAP / f"mipmap-{density}"
        folder.mkdir(parents=True, exist_ok=True)
        # The character is cut once per density: the foreground layer is 108dp,
        # so its art is ART_DP of that at the same scale as the icons beside it.
        fg_px = int(round(px * ADAPTIVE_DP / 48))
        small = square(src, px, MARK_PAD)
        foreground = Image.new("RGBA", (fg_px, fg_px), (0, 0, 0, 0))
        d = int(round(fg_px * ART_DP / ADAPTIVE_DP))
        foreground.alpha_composite(small.resize((d, d), Image.LANCZOS),
                                   ((fg_px - d) // 2, (fg_px - d) // 2))
        for name, image in (
            ("ic_launcher.png", composed(small, px, "square")),
            ("ic_launcher_round.png", composed(small, px, "round")),
            ("ic_launcher_foreground.png", foreground),
        ):
            image.save(folder / name, optimize=True)
            written.append(f"mipmap-{density}/{name}")

    total = sum((MIPMAP / p).stat().st_size for p in written)
    print(f"brand: fox-mark.png {mark.size[0]}px, fox-face.png {face.size[0]}px, "
          "both transparent")
    print(f"launcher: {len(written)} files, {total / 1024:.0f} KB, "
          f"{DENSITIES['mdpi']}-{DENSITIES['xxxhdpi']} px, art {ART_DP}/{ADAPTIVE_DP} dp")
    return 0


def _fail(message: str) -> int:
    print(f"build_brand: {message}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
