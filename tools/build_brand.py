#!/usr/bin/env python3
"""Builds Fluentify's mark from one illustration.

The mascot is a picture now, not geometry. One source file
(brand/fox-source.png - the illustration the brand was chosen from) produces
everything that draws it:

    brand/fox-mark.png          the whole character, round - boot screen
    brand/fox-face.png          the head, round - header + message avatars
    android/.../mipmap-*/       the launcher icon, every density, both shapes

Nothing is drawn per surface. Every copy is the same crop of the same file, so
the icon in the launcher cannot drift from the picture in the app - which is
exactly what happened when the boot screen carried a hand-redrawn copy of the
header's SVG: the two were meant to be one animal and were not.

Crops are recorded here once, in source pixel coordinates, so a re-cut is an
edit to this file rather than an afternoon of eyeballing a canvas.

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

# The cream the illustration is printed on. The icon background uses the
# picture's own paper rather than the app's --base, so the art has no seam.
CREAM = (253, 250, 241, 255)

# The whole character inside its circular backdrop. The square is the picture's
# own: 1082 px wide, from the backdrop's top-left to its bottom-right corner.
MARK_BOX = (116, 74, 1198, 1156)

# The head: beret, spectacles, muzzle and the neckerchief under it. Square, and
# centred on the face rather than on the figure - at 26 px in a message row a
# full-length portrait reads as an orange smudge, a face reads as a fox.
FACE_BOX = (352, 100, 848, 596)

# Android: the icon is generated at every density rather than scaled by the
# launcher. mdpi is the baseline, and each step is 1.5x the one before it.
DENSITIES = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
MIPMAP = ROOT / "android/app/src/main/res"

# Adaptive icons are a 108dp layer whose visible viewport is the central 72dp
# (66dp is the guaranteed safe zone). The art is exactly that 72dp: the mask
# then lands on the portrait's own circular edge - no cream ring around a
# picture that is already a circle - while the character inside it keeps a
# margin, so no mask shape and no launcher's crop can take the hat or the tail
# with it. At 80dp the beret was already touching the top of the mask.
ADAPTIVE_DP = 108
ART_DP = 72

# Legacy (API 24-25) icons are drawn as-is, so they carry their own shape and
# padding: a rounded square of paper with the round portrait inset.
LEGACY_ART = 0.86
LEGACY_RADIUS = 0.22


def circle(im: Image.Image) -> Image.Image:
    """The crop, cut to a circle with an antialiased edge."""
    im = im.convert("RGBA")
    ss = 4                                    # supersample the mask, not the art
    big = im.resize((im.width * ss, im.height * ss), Image.LANCZOS)
    mask = Image.new("L", big.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, big.width - 1, big.height - 1), fill=255)
    big.putalpha(mask)
    return big.resize(im.size, Image.LANCZOS)


def art(src: Image.Image, box: tuple[int, int, int, int], size: int) -> Image.Image:
    crop = circle(src.crop(box))
    return crop.resize((size, size), Image.LANCZOS)


def composed(art_im: Image.Image, size: int, shape: str) -> Image.Image:
    """The portrait inset on its paper, in a rounded square or a disc."""
    canvas = Image.new("RGBA", (size, size), CREAM)
    d = int(round(size * LEGACY_ART))
    scaled = art_im.resize((d, d), Image.LANCZOS)
    canvas.alpha_composite(scaled, ((size - d) // 2, (size - d) // 2))
    if shape == "round":
        mask = Image.new("L", (size * 4, size * 4), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size * 4 - 1, size * 4 - 1), fill=255)
        out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        out.paste(canvas, (0, 0), mask.resize((size, size), Image.LANCZOS))
        return out
    mask = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, size * 4 - 1, size * 4 - 1), radius=int(size * 4 * LEGACY_RADIUS),
        fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(canvas, (0, 0), mask.resize((size, size), Image.LANCZOS))
    return out


def main() -> int:
    if not SOURCE.exists():
        return _fail(f"{SOURCE.relative_to(ROOT)} is missing - it is the one "
                     "picture every Fluentify mark is cut from")
    src = Image.open(SOURCE).convert("RGB")
    w, h = src.size
    for name, box in (("mark", MARK_BOX), ("face", FACE_BOX)):
        if not (0 <= box[0] < box[2] <= w and 0 <= box[1] < box[3] <= h):
            return _fail(f"the {name} crop {box} falls outside the {w}x{h} source")

    # ---- what the app draws ------------------------------------------------
    # 400 px covers the boot mark at 3x density; 256 the message avatar at 4x
    # (26 CSS px). Both are round, so the tile behind them shows through the
    # corners instead of squaring the picture off.
    mark = art(src, MARK_BOX, 400)
    face = art(src, FACE_BOX, 256)
    BRAND.mkdir(exist_ok=True)
    mark.save(BRAND / "fox-mark.png", optimize=True)
    face.save(BRAND / "fox-face.png", optimize=True)

    # ---- what the launcher draws -------------------------------------------
    written = []
    for density, px in DENSITIES.items():
        folder = MIPMAP / f"mipmap-{density}"
        folder.mkdir(parents=True, exist_ok=True)
        # The portrait is cut once per density: the foreground layer is 108dp,
        # so its art is ART_DP of that at the same scale as the icons beside it.
        fg_px = int(round(px * ADAPTIVE_DP / 48))
        small = art(src, MARK_BOX, px)
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
    print(f"brand: fox-mark.png {mark.size[0]}px, fox-face.png {face.size[0]}px")
    print(f"launcher: {len(written)} files, {total / 1024:.0f} KB, "
          f"{DENSITIES['mdpi']}-{DENSITIES['xxxhdpi']} px, art {ART_DP}/{ADAPTIVE_DP} dp")
    return 0


def _fail(message: str) -> int:
    print(f"build_brand: {message}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
