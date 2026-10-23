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

"""Race car furniture for the AINTOLOGIC MX-5.

The concept: an AI company taking the piss out of AI. The car should be quietly,
deliberately wrong in the specific ways AI is wrong - but the wrongness lives
inside real race car furniture. Scrutineering roundels, contingency decals,
tech-inspection plates. Correct racing typography, correct decal proportions,
correct placement. Nothing floating in space.

Test for every element: would someone who works with AI actually smile? If it
just looks technical, it failed - cut it.

This is NOT the lore text that got killed. "PROJECT REGISTRY // ENTRY 001" was
earnest - decoration pretending to mean something. These are jokes, and a joke
either lands or it doesn't.

At 100mph none of this is visible. It all lives at walking pace.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

_FONTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")
F_COND = os.path.join(_FONTS, "BarlowCondensed-SemiBold.ttf")
F_GEO = os.path.join(_FONTS, "Poppins-Bold.ttf")

BONE = (239, 228, 208)
RUST = (192, 85, 42)
BLACK = (11, 12, 14)


def hand_roundel(d, ring=RUST, face=BONE, ink=BLACK):
    """Scrutineering-style roundel carrying a hand with six fingers.

    The oldest tell in AI image generation, rendered as the most mundane object
    on a race car. Reads as a certification sticker from two paces.
    """
    S = 4
    D = d * S
    im = Image.new("RGBA", (D, D), (0, 0, 0, 0))
    k = ImageDraw.Draw(im)
    k.ellipse([0, 0, D - 1, D - 1], fill=ring + (255,))
    inset = int(D * 0.11)
    k.ellipse([inset, inset, D - 1 - inset, D - 1 - inset], fill=face + (255,))

    # palm, sat low so the fingers have room to read as separate strokes
    pw, ph = int(D * 0.46), int(D * 0.20)
    px, py = (D - pw) // 2, int(D * 0.58)
    k.rounded_rectangle([px, py, px + pw, py + ph], radius=int(D * 0.05), fill=ink + (255,))
    # six fingers. count them.
    n = 6
    fw = D * 0.045
    gap = (pw - n * fw) / (n - 1.0)
    for i in range(n):
        fx = px + i * (fw + gap)
        tall = D * (0.30 if i in (2, 3) else 0.25 if i in (1, 4) else 0.19)
        k.rounded_rectangle([fx, py - tall, fx + fw, py + D * 0.03],
                            radius=fw / 2, fill=ink + (255,))
    return im.resize((d, d), Image.LANCZOS)


def plate(w, h, top, bottom, face=BONE, ink=BLACK):
    """Tech-inspection plate. Two lines, small label over a bold value."""
    S = 4
    W, H = w * S, h * S
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    k = ImageDraw.Draw(im)
    k.rounded_rectangle([0, 0, W - 1, H - 1], radius=int(H * 0.13), fill=face + (255,))
    f1 = ImageFont.truetype(F_COND, int(H * 0.30), layout_engine=ImageFont.Layout.BASIC)
    f2 = ImageFont.truetype(F_GEO, int(H * 0.36), layout_engine=ImageFont.Layout.BASIC)
    for txt, fnt, cy in ((top, f1, H * 0.28), (bottom, f2, H * 0.66)):
        bb = k.textbbox((0, 0), txt, font=fnt)
        k.text((W / 2 - (bb[2] - bb[0]) / 2, cy - (bb[3] - bb[1]) / 2 - bb[1]),
               txt, font=fnt, fill=ink + (255,))
    return im.resize((w, h), Image.LANCZOS)


def decal_text(text, h, color=BONE, track=0.05, font=F_COND):
    """Plain condensed decal lettering, letterspaced like a real sticker."""
    S = 3
    f = ImageFont.truetype(font, h * S, layout_engine=ImageFont.Layout.BASIC)
    sp = h * S * track
    widths = [f.getlength(c) for c in text]
    W = int(sum(widths) + sp * (len(text) - 1)) + 4
    Hh = int(h * S * 1.6)
    im = Image.new("RGBA", (W, Hh), (0, 0, 0, 0))
    k = ImageDraw.Draw(im)
    x = 2.0
    for c, cw in zip(text, widths):
        k.text((x, 0), c, font=f, fill=color + (255,))
        x += cw + sp
    return im.crop(im.getbbox()).resize(
        (max(1, W // S), max(1, im.crop(im.getbbox()).height // S)), Image.LANCZOS)


def melt(im, frac_start=0.62, frac_end=0.78, sag=0.14, wobble=0.05):
    """Sag one glyph of an otherwise correct wordmark.

    The other great tell: generated text that is almost a word. The wordmark is
    rendered correctly on the doors. This one, small and low on the sill, has a
    single letter that has gone slightly soft. Nobody notices until they do.
    """
    w, h = im.size
    x0, x1 = int(w * frac_start), int(w * frac_end)
    band = im.crop((x0, 0, x1, h))
    bw, bh = band.size
    if bw < 2 or bh < 2:
        return im
    # stretch it taller and squeeze it narrower, then let the edges go soft
    band = band.resize((max(1, int(bw * (1 - wobble))), int(bh * (1 + sag))), Image.BICUBIC)
    band = band.filter(ImageFilter.GaussianBlur(radius=max(0.6, h * 0.020)))
    out = im.copy()
    out.paste((0, 0, 0, 0), (x0, 0, x1, h))
    out.alpha_composite(band, (x0 + int(bw * wobble * 0.5), int(h * 0.035)))
    return out
