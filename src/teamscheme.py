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

"""THE TEAM PAINT SCHEME.  One module, every car.

AINTOLOGIC's team livery language - black body, papaya accent, white type - drawn
entirely in code so the identical marks retarget to the next car by changing
only the panel map.  Spec: docs/PAINT-SCHEME.md.  Read that before using this.

    palette          PAPAYA / BLACK / WHITE / GRAPHITE, and the spec values
    wordmark()       AINTOLOGIC - white type, orange A-bar and slanted diaeresis
    ai_mark()        the big AI badge glyph on its own
    checker_rule()   the line - checkers - line accent under a mark
    roundel()        the round team badge: black disc, orange ring, AI, name
    number_panel()   white rounded panel that sits UNDER iRacing's stamped number
    coachline()      helper for the white edge line along the black/papaya split

Every function takes colours as keyword arguments so the same geometry can
emit the colour map (brand colours) and the spec map (material values).

Reference artwork: the project evidence folder -
AI-generated concept images.  They are the SPEC for these marks, nothing from
them ships as raster.
"""
import os
from PIL import Image, ImageDraw, ImageFont

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_FONTS = os.path.join(_ROOT, "fonts")
F_WIDE = os.path.join(_FONTS, "Orbitron-Variable.ttf")     # the logo face
F_WIDE_WEIGHT = 800                                          # ExtraBold
F_COND = os.path.join(_FONTS, "BarlowCondensed-SemiBold.ttf")


def wide_font(size):
    f = ImageFont.truetype(F_WIDE, size, layout_engine=ImageFont.Layout.BASIC)
    f.set_variation_by_axes([F_WIDE_WEIGHT])
    return f

# --- palette ------------------------------------------------------------------
PAPAYA   = (255, 122,   0)   # #FF7A00  THE ACCENT, never a field.  McLaren-adjacent
BLACK    = ( 12,  12,  13)   # #0C0C0D  THE BODY, and the ground every mark sits on
WHITE    = (236, 236, 236)   # #ECECEC  the type.  Not pure white - reads as vinyl
GRAPHITE = ( 46,  48,  52)   # #2E3034  secondary, for checker cells on black
SAFETY_RED  = (190, 40, 34)
SAFETY_BLUE = (40, 78, 140)

# --- spec map (R metallic BINARY, G roughness, B clearcoat INVERTED: 16 = max)
SPEC_BODY  = (0,  40, 16)    # papaya paint: deep gloss
SPEC_BAND  = (0,  75, 16)    # black bands: satin, so they separate as a material
SPEC_DECAL = (0,  95, 16)    # every mark and sticker: semi-matte vinyl
SPEC_NUM   = (0,  40, 16)    # number blocks: plain gloss, the stamp inherits this
SPEC_LINE  = (0,   0, 16)    # the white coachline: mirror smooth, reads wet


def _S(k=4):
    return k


BOLD = 0.0       # fake-bold stroke as a fraction of font size.  Michroma only
                 # ships Regular; the logo face is heavy


def _glyph(text, font, fill, bold=BOLD):
    """Render text tight-cropped to its ink."""
    sw = int(font.size * bold)
    bb = font.getbbox(text, stroke_width=sw)
    im = Image.new("RGBA", (bb[2] - bb[0] + 4, bb[3] - bb[1] + 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2 - bb[0], 2 - bb[1]), text, font=font,
                            fill=tuple(fill) + (255,), stroke_width=sw,
                            stroke_fill=tuple(fill) + (255,))
    return im.crop(im.getbbox())


def _crossbar_rows(a_alpha):
    """Rows of an 'A' glyph that are its crossbar: one solid run, wide."""
    px = a_alpha.load()
    w, h = a_alpha.size
    rows = []
    for y in range(h // 2, h):
        runs, run = [], 0
        for x in range(w):
            if px[x, y] > 128:
                run += 1
            elif run:
                runs.append(run)
                run = 0
        if run:
            runs.append(run)
        if len(runs) == 1 and runs[0] > w * 0.45:
            rows.append(y)
    return rows


def _stroke_width(a_alpha):
    """Leg stroke width of an 'A' glyph, measured on a row above the crossbar."""
    px = a_alpha.load()
    w, h = a_alpha.size
    y = int(h * 0.42)
    runs, run = [], 0
    for x in range(w):
        if px[x, y] > 128:
            run += 1
        elif run:
            runs.append(run)
            run = 0
    if run:
        runs.append(run)
    return max(runs) if runs else max(2, w // 8)


def _pointed_a(H, sw, ink, accent, width=1.02, apex=0.35, bar=(0.62, 0.82),
               inset=0.03):
    """The logo's A.  Cap height H, leg stroke sw (horizontal thickness).

    A pointed triangle with a small flat apex, hollow, with the orange
    trapezoid filling the crossbar band between the legs.  Proportions from
    the reference logo: wider than tall, bar in the lower third."""
    W = int(H * width)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    a = int(sw * apex)                        # half-width of the flat apex
    outer = [(0, H), (W // 2 - a, 0), (W // 2 + a, 0), (W, H)]
    d.polygon(outer, fill=tuple(ink) + (255,))
    # hollow: inner triangle with the same leg slope, offset by the stroke
    slope = (W / 2.0 - a) / float(H)          # dx per dy of the outer leg
    import math
    th = sw / math.cos(math.atan(slope))      # horizontal thickness of a leg
    tv = sw * 1.15                            # apex thickness, a touch heavier
    inner_top = int(tv * (1 + slope * 0.6))
    inner = [(int(th), H), (W // 2, inner_top), (W - int(th), H)]
    hole = Image.new("L", (W, H), 0)
    ImageDraw.Draw(hole).polygon(inner, fill=255)
    alpha = im.getchannel("A")
    alpha.paste(0, mask=hole)
    im.putalpha(alpha)
    # the orange bar, between the inner leg edges, inset a hair
    y0, y1 = int(H * bar[0]), int(H * bar[1])
    g = int(H * inset)
    def inner_x(y):
        t = (y - inner_top) / float(H - inner_top)
        return W / 2.0 - (W / 2.0 - th) * t
    d = ImageDraw.Draw(im)
    for y in range(y0, y1):
        l = int(inner_x(y)) + g
        r = W - int(inner_x(y)) - g
        if r > l:
            d.line([(l, y), (r, y)], fill=tuple(accent) + (255,))
    return im


def ai_letters(h, ink=WHITE, accent=PAPAYA, k=4):
    """The 'AI' pair: A with the orange bar in its crossbar, I with the slanted
    orange diaeresis.  h is the cap height in output pixels."""
    H = h * k
    f = wide_font(int(H * 1.0))
    I = _glyph("I", f, ink)
    # scale the I to cap height H, and read the face's stroke width off it
    s = H / float(_glyph("N", f, ink).height)
    I = I.resize((max(1, int(I.width * s)), H), Image.LANCZOS)
    sw = I.width
    # --- the A is DRAWN, not typed: the logo's A is a pointed triangle with
    # the orange trapezoid sitting in the crossbar, and Orbitron's A is
    # square-topped.  Same stroke as the face so it belongs with the I.
    A = _pointed_a(H, sw, ink, accent)
    # --- the diaeresis: two parallelograms leaning right, above the I -------
    gap = int(H * 0.09)
    dh, dw, lean = int(H * 0.22), int(sw * 1.1), int(H * 0.08)
    top = Image.new("RGBA", (I.width + dw * 3 + lean, dh), (0, 0, 0, 0))
    td = ImageDraw.Draw(top)
    cx = I.width // 2 + dw  # the pair sits over the I, biased right as drawn
    for i in (0, 1):
        x = cx - dw - int(dw * 0.35) + i * (dw + int(dw * 0.7))
        td.polygon([(x + lean, 0), (x + lean + dw, 0), (x + dw, dh), (x, dh)],
                   fill=tuple(accent) + (255,))
    spacing = int(H * 0.06)
    W = A.width + spacing + max(I.width, top.width)
    out = Image.new("RGBA", (W, H + dh + gap), (0, 0, 0, 0))
    out.alpha_composite(A, (0, dh + gap))
    out.alpha_composite(I, (A.width + spacing, dh + gap))
    out.alpha_composite(top, (A.width + spacing - dw, 0))
    out = out.crop(out.getbbox())
    return out.resize((max(1, out.width // k), max(1, out.height // k)),
                      Image.LANCZOS)


def wordmark(h, ink=WHITE, accent=PAPAYA, tail="NTOLOGIC", tail_scale=0.72,
             track=0.10, k=4):
    """AINTOLOGIC.  h = cap height of the big AI, in output pixels.
    NTOLOGIC sits on the same baseline at tail_scale of that height."""
    ai = ai_letters(h, ink, accent, k)
    H = h * k
    f = wide_font(int(H * tail_scale))
    sp = int(H * tail_scale * track)
    glyphs = [_glyph(c, f, ink) for c in tail]
    # normalise tail glyph heights to the font's cap height so O/G/C don't bob
    cap = _glyph("N", f, ink).height
    tw = sum(g.width for g in glyphs) + sp * (len(glyphs) - 1)
    tail_im = Image.new("RGBA", (tw, cap + 4), (0, 0, 0, 0))
    x = 0
    for g in glyphs:
        tail_im.alpha_composite(g, (x, cap - g.height + 2))
        x += g.width + sp
    tail_im = tail_im.resize((max(1, tw // k), max(1, tail_im.height // k)),
                             Image.LANCZOS)
    gapx = max(1, int(h * 0.10))
    W = ai.width + gapx + tail_im.width
    out = Image.new("RGBA", (W, ai.height), (0, 0, 0, 0))
    out.alpha_composite(ai, (0, 0))
    # baselines align: both images are ink-tight at the bottom
    out.alpha_composite(tail_im, (ai.width + gapx, ai.height - tail_im.height))
    return out


def checker_rule(w, accent=PAPAYA, dark=GRAPHITE, line=WHITE, cells=6, k=4):
    """line - slanted checker block - line.  The accent under the wordmark.
    On black: accent=PAPAYA, dark=GRAPHITE.  On papaya: accent=WHITE, dark=BLACK."""
    W = w * k
    H = int(W * 0.075)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lw = max(k, int(H * 0.16))
    cw = int(W * 0.30)                   # checker block width
    cx0 = (W - cw) // 2
    d.line([(int(W * 0.02), H // 2), (cx0 - int(W * 0.03), H // 2)],
           fill=tuple(line) + (255,), width=lw)
    d.line([(cx0 + cw + int(W * 0.03), H // 2), (int(W * 0.98), H // 2)],
           fill=tuple(line) + (255,), width=lw)
    cell = cw / float(cells)
    rows = 2
    ch = H / float(rows)
    lean = int(H * 0.35)
    for r in range(rows):
        for c in range(cells):
            col = accent if (r + c) % 2 == 0 else dark
            x = cx0 + c * cell
            y = r * ch
            d.polygon([(x + lean * (1 - r / rows), y),
                       (x + cell + lean * (1 - r / rows), y),
                       (x + cell + lean * (1 - (r + 1) / rows), y + ch),
                       (x + lean * (1 - (r + 1) / rows), y + ch)],
                      fill=tuple(col) + (255,))
    return im.resize((w, max(1, H // k)), Image.LANCZOS)


def roundel(d, ground=BLACK, ring=PAPAYA, ink=WHITE, accent=PAPAYA, k=4):
    """The team badge: black disc, papaya ring, big AI, AINTOLOGIC, checkers."""
    D = d * k
    im = Image.new("RGBA", (D, D), (0, 0, 0, 0))
    g = ImageDraw.Draw(im)
    rw = max(k, int(D * 0.045))
    g.ellipse([0, 0, D - 1, D - 1], fill=tuple(ring) + (255,))
    g.ellipse([rw, rw, D - 1 - rw, D - 1 - rw], fill=tuple(ground) + (255,))
    ai = ai_letters(int(d * 0.30), ink, accent, k)
    ai = ai.resize((ai.width * k, ai.height * k), Image.LANCZOS)
    im.alpha_composite(ai, (D // 2 - ai.width // 2, int(D * 0.22)))
    wm = wordmark(int(d * 0.065), ink, accent, k=k)
    wm = wm.resize((wm.width * k, wm.height * k), Image.LANCZOS)
    im.alpha_composite(wm, (D // 2 - wm.width // 2, int(D * 0.645)))
    cr = checker_rule(int(d * 0.50), accent, GRAPHITE, ink, k=k)
    cr = cr.resize((cr.width * k, cr.height * k), Image.LANCZOS)
    im.alpha_composite(cr, (D // 2 - cr.width // 2, int(D * 0.765)))
    return im.resize((d, d), Image.LANCZOS)


def number_panel(w, h, fill=WHITE, radius=None, k=4):
    """Flat white rounded panel.  iRacing stamps the number on top of it; the
    build guard allows exactly this fill inside a number block."""
    r = radius if radius is not None else int(min(w, h) * 0.10)
    im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, w * k - 1, h * k - 1],
                                         radius=r * k, fill=tuple(fill) + (255,))
    return im.resize((w, h), Image.LANCZOS)


def small_caps(text, h, ink=WHITE, track=0.08, k=4):
    """Condensed caps for secondary text (driver strip, supplier lines)."""
    H = h * k
    f = ImageFont.truetype(F_COND, H, layout_engine=ImageFont.Layout.BASIC)
    sp = int(H * track)
    glyphs = [_glyph(c, f, ink) if c != " " else None for c in text]
    W = sum((g.width if g else H // 3) for g in glyphs) + sp * (len(glyphs) - 1)
    im = Image.new("RGBA", (W, H + 4), (0, 0, 0, 0))
    x = 0
    for g in glyphs:
        if g:
            im.alpha_composite(g, (x, H - g.height + 2))
            x += g.width + sp
        else:
            x += H // 3 + sp
    im = im.crop(im.getbbox())
    return im.resize((max(1, im.width // k), max(1, im.height // k)), Image.LANCZOS)


if __name__ == "__main__":
    # proof sheet: every mark on black and on papaya
    sheet = Image.new("RGB", (1600, 900), BLACK)
    ImageDraw.Draw(sheet).rectangle([800, 0, 1600, 900], fill=PAPAYA)
    for x0, ink, acc in ((40, WHITE, PAPAYA), (840, WHITE, BLACK)):
        sheet.paste(wordmark(120, ink, acc), (x0, 40), wordmark(120, ink, acc))
        w2 = wordmark(50, ink, acc)
        sheet.paste(w2, (x0, 260), w2)
        c = (checker_rule(400, PAPAYA, GRAPHITE, WHITE) if acc == PAPAYA
             else checker_rule(400, WHITE, BLACK, WHITE))
        sheet.paste(c, (x0, 340), c)
        r = roundel(300, BLACK, PAPAYA, WHITE, PAPAYA)
        sheet.paste(r, (x0, 420), r)
        a = ai_letters(160, ink, acc)
        sheet.paste(a, (x0 + 380, 480), a)
        n = number_panel(148, 130)
        sheet.paste(n, (x0 + 560, 500), n)
        s = small_caps("DRIVER NAME", 28, ink)
        sheet.paste(s, (x0 + 380, 760), s)
    sheet.save(r"scratch\scheme_proof.png")
    print("wrote scratch/scheme_proof.png")
