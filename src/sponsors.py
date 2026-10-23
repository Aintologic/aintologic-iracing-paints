# AÏntologic iRacing paints
# Copyright (C) 2026 AÏntologic
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License
# for more details. You should have received a copy of the GNU Affero General
# Public License along with this program. If not, see
# <https://www.gnu.org/licenses/>.
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Race car furniture that is NOT a joke.

What makes a livery read as a real race car is not logo count. It is the safety
and scrutineering marks every real car carries, in the places they always sit:
the electrical cutoff triangle, the extinguisher circle, tow arrows, a driver
name strip. The eye reads those as authentic before it reads any sponsor.

Everything here is drawn in code, in the AINTOLOGIC palette, so it retargets to
the next car by changing only placement. Nothing is imported raster art - the
one exception is the real Cats Don't Suck mark in assets/, which is the designer's own
brand and is used as supplied.
"""
import inspect, os
from PIL import Image, ImageDraw, ImageFont

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_FONTS = os.path.join(_ROOT, "fonts")
ASSETS = os.path.join(_ROOT, "assets")

F_COND = os.path.join(_FONTS, "BarlowCondensed-SemiBold.ttf")
F_GEO = os.path.join(_FONTS, "Poppins-Bold.ttf")
F_HEAVY = os.path.join(_FONTS, "ArchivoBlack-Regular.ttf")

BONE = (239, 228, 208)
RUST = (192, 85, 42)
GOLD = (198, 154, 63)
FOREST = (29, 58, 49)
BLACK = (11, 12, 14)
SAFETY_RED = (190, 40, 34)
SAFETY_BLUE = (40, 78, 140)


def cutoff_triangle(h, red=SAFETY_RED, spark=BONE, edge=BONE):
    """FIA electrical master-cutoff mark: red-edged triangle, blue field, spark.

    Sits by the windscreen base and on the rear panel on every real race car.
    Nothing says 'this is a scrutineered race car' faster than this mark.
    """
    S = 4
    H = h * S
    W = int(H * 1.15)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    k = ImageDraw.Draw(im)
    tri = [(W / 2, 0), (W, H), (0, H)]
    k.polygon(tri, fill=SAFETY_BLUE + (255,))
    k.line(tri + [tri[0]], fill=red + (255,), width=int(H * 0.11), joint="curve")
    # lightning bolt
    cx, cy = W / 2, H * 0.60
    u = H * 0.20
    bolt = [(cx + u * 0.20, cy - u * 1.05), (cx - u * 0.55, cy + u * 0.10),
            (cx - u * 0.05, cy + u * 0.10), (cx - u * 0.25, cy + u * 1.05),
            (cx + u * 0.55, cy - u * 0.15), (cx + u * 0.02, cy - u * 0.15)]
    k.polygon(bolt, fill=spark + (255,))
    return im.resize((W // S, h), Image.LANCZOS)


def extinguisher_mark(d, ring=SAFETY_RED, face=BONE, ink=BLACK):
    """Circular 'E' marking the fire extinguisher / suppression pull."""
    S = 4
    D = d * S
    im = Image.new("RGBA", (D, D), (0, 0, 0, 0))
    k = ImageDraw.Draw(im)
    k.ellipse([0, 0, D - 1, D - 1], fill=ring + (255,))
    ins = int(D * 0.13)
    k.ellipse([ins, ins, D - 1 - ins, D - 1 - ins], fill=face + (255,))
    f = ImageFont.truetype(F_HEAVY, int(D * 0.58), layout_engine=ImageFont.Layout.BASIC)
    bb = k.textbbox((0, 0), "E", font=f)
    k.text((D / 2 - (bb[2] - bb[0]) / 2 - bb[0], D / 2 - (bb[3] - bb[1]) / 2 - bb[1]),
           "E", font=f, fill=ink + (255,))
    return im.resize((d, d), Image.LANCZOS)


def tow_arrow(w, label="TOW", color=BONE, ink=BLACK):
    """Tow-point marker: arrow into a small labelled tab."""
    S = 4
    W = w * S
    H = int(W * 0.46)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    k = ImageDraw.Draw(im)
    ah = H * 0.92
    k.polygon([(0, H / 2), (ah * 0.72, H * 0.04), (ah * 0.72, H * 0.96)], fill=color + (255,))
    k.rounded_rectangle([ah * 0.66, H * 0.16, W - 1, H * 0.84],
                        radius=int(H * 0.16), fill=color + (255,))
    f = ImageFont.truetype(F_COND, int(H * 0.52), layout_engine=ImageFont.Layout.BASIC)
    bb = k.textbbox((0, 0), label, font=f)
    tx = ah * 0.66 + (W - ah * 0.66) / 2 - (bb[2] - bb[0]) / 2 - bb[0]
    k.text((tx, H / 2 - (bb[3] - bb[1]) / 2 - bb[1]), label, font=f, fill=ink + (255,))
    return im.resize((w, H // S), Image.LANCZOS)


def driver_strip(w, name, flag=None, face=BLACK, ink=BONE, accent=GOLD):
    """Driver name strip for the cockpit surround. Real cars all carry one."""
    S = 4
    W = w * S
    H = int(W * 0.20)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    k = ImageDraw.Draw(im)
    k.rounded_rectangle([0, 0, W - 1, H - 1], radius=int(H * 0.18), fill=face + (255,))
    k.rounded_rectangle([0, 0, W - 1, H - 1], radius=int(H * 0.18),
                        outline=accent + (255,), width=int(H * 0.07))
    x = H * 0.34
    if flag:
        fw, fh = H * 0.62, H * 0.42
        fy = H / 2 - fh / 2
        for i, band in enumerate(flag):
            k.rectangle([x, fy + i * fh / len(flag), x + fw, fy + (i + 1) * fh / len(flag)],
                        fill=band + (255,))
        x += fw + H * 0.26
    f = ImageFont.truetype(F_COND, int(H * 0.54), layout_engine=ImageFont.Layout.BASIC)
    bb = k.textbbox((0, 0), name, font=f)
    k.text((x, H / 2 - (bb[3] - bb[1]) / 2 - bb[1]), name, font=f, fill=ink + (255,))
    return im.resize((w, H // S), Image.LANCZOS)


def supplier(w, top, bottom=None, face=None, ink=BONE, rule=GOLD):
    """A plausible motorsport supplier mark. Not a joke - just a good fake logo.

    Real cars are covered in these: a name, sometimes a category line under it,
    set in condensed caps. Kept flat and typographic so they read at scale and
    never compete with the primary identity.
    """
    S = 4
    W = w * S
    H = int(W * (0.34 if bottom else 0.26))
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    k = ImageDraw.Draw(im)
    if face:
        k.rounded_rectangle([0, 0, W - 1, H - 1], radius=int(H * 0.14), fill=face + (255,))
    f1 = ImageFont.truetype(F_GEO, int(H * (0.44 if bottom else 0.62)), layout_engine=ImageFont.Layout.BASIC)
    bb = k.textbbox((0, 0), top, font=f1)
    k.text((W / 2 - (bb[2] - bb[0]) / 2 - bb[0], H * (0.28 if bottom else 0.5)
            - (bb[3] - bb[1]) / 2 - bb[1]), top, font=f1, fill=ink + (255,))
    if bottom:
        k.line([(W * 0.20, H * 0.53), (W * 0.80, H * 0.53)],
               fill=rule + (255,), width=max(1, int(H * 0.045)))
        f2 = ImageFont.truetype(F_COND, int(H * 0.30), layout_engine=ImageFont.Layout.BASIC)
        bb2 = k.textbbox((0, 0), bottom, font=f2)
        k.text((W / 2 - (bb2[2] - bb2[0]) / 2 - bb2[0], H * 0.76
                - (bb2[3] - bb2[1]) / 2 - bb2[1]), bottom, font=f2, fill=ink + (255,))
    return im.resize((w, H // S), Image.LANCZOS)


def freakfarm(w, ink=BONE, accent=RUST):
    """FreakFarm as a technical-partner mark, redrawn in OUR palette.

    The supplied pack put FreakFarm in electric blue and orange as a competing
    primary identity. On this car it is a small partner mark and it wears the
    AINTOLOGIC palette so it belongs here. The helmet-cat mascots from that pack
    are not used - at sill scale they read as a pile of triangles.
    """
    S = 4
    W = w * S
    H = int(W * 0.30)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    k = ImageDraw.Draw(im)
    # shield with FF
    sw = H * 0.78
    pts = [(0, H * 0.10), (sw, H * 0.10), (sw, H * 0.52), (sw / 2, H * 0.92), (0, H * 0.52)]
    k.polygon(pts, outline=ink + (255,), width=max(1, int(H * 0.055)))
    f0 = ImageFont.truetype(F_HEAVY, int(H * 0.34), layout_engine=ImageFont.Layout.BASIC)
    bb0 = k.textbbox((0, 0), "FF", font=f0)
    k.text((sw / 2 - (bb0[2] - bb0[0]) / 2 - bb0[0], H * 0.42
            - (bb0[3] - bb0[1]) / 2 - bb0[1]), "FF", font=f0, fill=ink + (255,))
    f1 = ImageFont.truetype(F_GEO, int(H * 0.36), layout_engine=ImageFont.Layout.BASIC)
    f2 = ImageFont.truetype(F_COND, int(H * 0.26), layout_engine=ImageFont.Layout.BASIC)
    x = sw + H * 0.28
    # the designer, 2026-09-14: the name is one word, "FreakFarm", mixed case
    k.text((x, H * 0.16), "FreakFarm", font=f1, fill=ink + (255,))
    k.text((x, H * 0.60), "RACING", font=f2, fill=accent + (255,))
    return im.resize((w, H // S), Image.LANCZOS)


def cats_dont_suck(w, roundel_only=True, wordmark_ink=BONE):
    """the designer's real Cats Don't Suck mark. The one imported raster on the car.

    roundel_only: the supplied art is cat-circle over a "CatsDon'tSuck" wordmark
    set in near-black. On a near-black car that wordmark disappears, so by
    default only the roundel is used - it is the strong half and it is
    self-contained. Set False to get the full lockup with the wordmark
    recoloured to `wordmark_ink` so it survives on a dark body.
    """
    im = Image.open(os.path.join(ASSETS, "CatsDontSuck.png")).convert("RGBA")
    im = im.crop(im.getbbox())
    if roundel_only:
        # the cat circle occupies the upper ~72% of the lockup
        im = im.crop((0, 0, im.width, int(im.height * 0.72)))
        im = im.crop(im.getbbox())
    else:
        px = im.load()
        for y in range(int(im.height * 0.72), im.height):
            for x in range(im.width):
                r, g, b, a = px[x, y]
                if a > 30 and r + g + b < 260:          # the dark wordmark strokes
                    px[x, y] = wordmark_ink + (a,)
    return im.resize((w, max(1, int(im.height * w / im.width))), Image.LANCZOS)


# --- logo slots ---------------------------------------------------------------
# Every team car places two marks at fixed per-car coordinates: a Cats Don't
# Suck slot and a FreakFarm slot. The builders feed those slots a callable
# resolved from --logo1 / --logo2 (see src/personalize.py). The default is the
# neutral placeholder below; cats_dont_suck() / freakfarm() above stay as the
# opt-in example marks. This keeps nobody's personal mark in the default output.

def placeholder_logo(w, label="YOUR LOGO", ink=BONE, accent=RUST, **_):
    """The neutral, code-drawn 'YOUR LOGO' placeholder for an unfilled slot.

    A bordered plate with the label and a small accent tab so it reads as a
    logo lockup. Returns an RGBA image of width w (height ~0.42 w). Extra
    keyword args (e.g. a slot's ink/accent) are honoured; anything else is
    ignored, so the same placeholder drops into any slot."""
    S = 4
    W = w * S
    H = int(W * 0.42)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    k = ImageDraw.Draw(im)
    bw = max(S, int(H * 0.07))
    k.rounded_rectangle([bw // 2, bw // 2, W - 1 - bw // 2, H - 1 - bw // 2],
                        radius=int(H * 0.14), outline=tuple(ink) + (255,), width=bw)
    k.rounded_rectangle([bw * 2, bw * 2, int(W * 0.17), int(H * 0.27)],
                        radius=int(H * 0.06), fill=tuple(accent) + (255,))
    target = W * 0.80
    fs = max(6, int(H * 0.40))
    f = ImageFont.truetype(F_COND, fs, layout_engine=ImageFont.Layout.BASIC)
    while fs > 6 and k.textlength(label, font=f) > target:
        fs -= 2
        f = ImageFont.truetype(F_COND, fs, layout_engine=ImageFont.Layout.BASIC)
    bb = k.textbbox((0, 0), label, font=f)
    k.text((W / 2 - (bb[2] - bb[0]) / 2 - bb[0], H / 2 - (bb[3] - bb[1]) / 2 - bb[1]),
           label, font=f, fill=tuple(ink) + (255,))
    return im.resize((w, max(1, H // S)), Image.LANCZOS)


def image_logo(path):
    """Return a f(width, **_) -> RGBA that drops the user's own image into a slot.

    The image is cropped to its ink and fitted to the slot width, keeping its
    aspect - the same shape the builders expect from the example marks."""
    if not os.path.isfile(path):
        raise SystemExit("no such logo image: %s" % path)

    def _render(w, **_):
        im = Image.open(path).convert("RGBA")
        bb = im.getbbox()
        if bb:
            im = im.crop(bb)
        return im.resize((w, max(1, int(im.height * w / im.width))), Image.LANCZOS)

    return _render


def logo_slot(spec, w, **kw):
    """Resolve a logo-slot value and render it at width w.

    spec may be a callable f(w, **kw), None/'placeholder' (-> placeholder_logo),
    'cats_dont_suck' / 'freakfarm' (-> the example marks), or a path to an image
    file. Keyword args are forwarded only where the resolved function accepts
    them, so a slot can pass its palette without breaking a mark that ignores it.
    """
    fn = spec if callable(spec) else {
        None: placeholder_logo, "": placeholder_logo, "placeholder": placeholder_logo,
        "cats_dont_suck": cats_dont_suck, "freakfarm": freakfarm,
    }.get(spec)
    if fn is None:
        fn = image_logo(spec)
    try:
        params = inspect.signature(fn).parameters
        if any(p.kind == p.VAR_KEYWORD for p in params.values()):
            use = kw
        else:
            use = {k: v for k, v in kw.items() if k in params}
    except (TypeError, ValueError):
        use = kw
    return fn(w, **use)
