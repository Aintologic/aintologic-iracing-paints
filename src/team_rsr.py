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

"""TEAM SCHEME - Porsche 911 RSR (#102).  Third car on the scheme.

The AINTOLOGIC team livery (docs/PAINT-SCHEME.md) placed on the RSR's panel
map (docs/car-maps/porsche-911-rsr.md).  Every mark comes from
src/teamscheme.py and src/sponsors.py; this file holds ONLY the RSR's
geometry and placements.  Pattern copied from the F4 build (src/team_f4.py)
with every F4 number deleted - the RSR shares no UV with the F4 or the MX-5.

    python src/team_rsr.py            -> out/ in the project folder
    python src/team_rsr.py --here     -> the cwd instead
    python src/team_rsr.py --no-spec  -> colour map only
    python src/team_rsr.py --png      -> also write the flat texture as PNG

Writes car_<id>.tga (+ car_spec_<id>.tga); see src/personalize.py for
--id / --driver / --logo1 / --logo2 / --out / --profile / --design, and
src/design.py for a design's colours, team name and stripe style.

Template: 102_template_RSR.zip
("Porsche 911 RSR.psd", 2048x2048).  Car ID #102 confirmed in the Car Info
panel 2026-09-14.  Paint folder: %USERPROFILE%\\Documents\\iRacing\\paint\\porsche991rsr\\.

THE ONE RULE OF THIS UV (car map, measured 2026-09-14 on the sill, door,
quarter and fender pairs): every right-side island is the left one mirrored
about texture row 1305.5 - right y = 2611 - left y (per pixel row), x
identical, nose at low x on both sides.  From a level side view the LEFT
islands read upright and the RIGHT islands read ROTATE_180.  So the left
side is drawn in LEFT texture space, the GEOMETRY is mirrored to the right
in one operation (mirror_geometry), and TEXT is composited afterwards,
ROTATE_180 on the right (place).  Centre-line islands (hood, bumper, roof,
engine cover, tail) are each drawn once, symmetric about their own centre.
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
import teamscheme as T
import sponsors
import personalize
import iracingpaths
import design

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUSTOMER = personalize.DEFAULT_ID
PAINT_DIR = iracingpaths.paint_folder("porsche991rsr")
# personalization, set from the CLI/profile in __main__ before build() runs:
DRIVER_NAME = ""                       # blank driver strip by default
LOGO1 = sponsors.placeholder_logo      # Cats Don't Suck slot
LOGO2 = sponsors.placeholder_logo      # FreakFarm slot
DESIGN = design.EXAMPLE                # your own design (--design); apply_design() sets it
W = H = 2048
MIRROR = 2611                        # right pixel row = MIRROR - left pixel row

# --- template anchor blocks (PSD "Number Blocks" layer, tools/template_layers.py)
NUMBER_BLOCKS = {"N1": (921, 772, 87, 73),      # RIGHT door, front, mid-height
                 "N2": (487, 1251, 107, 113),   # hood, on the centre line (bbox of a rotated block)
                 "N3": (921, 1766, 87, 73)}     # LEFT door, front, mid-height

BODY, LINE, ACCENT = T.BLACK, T.WHITE, T.PAPAYA


def apply_design(ds):
    """Build with design ds (src/design.py): its colours, lettering and stripe
    style.  The names here predate it: LINE is the design's trim (the thin
    lines, the hood V's wedges, the roof ring), ACCENT its graphic colour (the
    wide stripe)."""
    global DESIGN, BODY, LINE, ACCENT
    DESIGN = ds
    BODY, LINE, ACCENT = ds.body, ds.trim, ds.graphic

# --- islands (docs/car-maps/porsche-911-rsr.md), LEFT texture space -----------
DOOR = (843, 1655, 491, 262)         # x 843 = front shut line, ~1290 = rear shut line; y 1655 sill .. 1917 bottom
SILL = (773, 1888, 712, 141)         # rocker under the door, two strips
QUARTER = (1255, 1492, 658, 396)     # rear quarter: 1492..1624 fender top, 1624..1756 haunch, 1756..1888 lower
FENDER = (288, 1481, 507, 309)       # front fender: 1481..1584 inner top, 1584..1687 crown, 1687..1790 side face
HOOD = (215, 1036, 529, 540)         # +x rearward (215 = nose lip), centre row 1306
HOOD_CY = 1306
BUMPER = (10, 805, 230, 1002)        # front bumper: y ACROSS the car (centre 1306), x = height (240 top .. 10 splitter)
BUMPER_CY = 1306
ROOF = (807, 1000, 624, 500)         # roof + rear glass: +x rearward, centre row ~1300 (measured, +-10)
ROOF_CY = 1300
COVER = (125, 153, 377, 290)         # engine cover: +x = car's RIGHT, +y rearward (153 front edge, 443 tail crease)
COVER_CX = 319                       # 318 read ~1 texel left of the exhaust centre from dead rear (pass 6)
TAIL = (952, 12, 1087, 191)          # rear bumper: +x = car's RIGHT; 12..~100 panel between the lights, 107..202 lower band
BANNER = (834, 1058, 100, 496)       # windscreen sun strip: +y = car's LEFT, centre 1306
BANNER_CY = 1306

# =============================================================================
# PLACEMENTS - first pass 2026-09-14 (issue #2, milestone 1).  Band recipe
# everywhere: orange = 2x white, small body-colour gaps; the texel widths
# differ per island because each island renders at its own scale (the tail
# strip is ~1.6x the texel density of the engine cover) - tuned on the render.
#
#   * CENTRE STRIPES nose -> tail: bumper face, hood (through the hood
#     number panel), roof + rear glass through the ROOF ROUNDEL as the node,
#     engine cover, tail panel between the lights, then the rear wordmark.
#   * the SASH: three bands across the front fender's side face behind the
#     wheel arch, crown to arch lip, leaning top-forward, ahead of the door
#     number panel (the MX-5's fender sash, on a 911 fender).
#   * AINTOLOGIC on the door behind the number panel; the sun-strip
#     wordmark on the windscreen banner; FreakFarm on the rear-quarter
#     haunch behind the side intake; Cats Don't Suck on the lower rear
#     quarter behind the door (both sides); driver strip on the window sill.
#     The sim's own decal layer already draws the cutoff + extinguisher marks
#     at the windscreen base corners, so none are drawn here.
# ONE stripe recipe for every centre-line panel.  Tick probes (pass 6,
# 2026-09-14, tools/probe_ticks.py + scratch\rsr\measure.py) showed the hood,
# roof and engine cover all render ~0.61-0.65 px per texel from above and the
# bumper matches the hood lip at the crest, so the same texel widths give the
# same physical width everywhere; the earlier per-panel guesses (48 on the
# cover, 50-56 on the bumper) were the mismatches the designer saw.
CS = (44, 22, 5)                     # orange, white, gap - texels, every centre-line panel
HOOD_CS = CS
HOOD_X = (215, 666)                  # nose lip .. just short of the LOUVRE-FRAME islands (667,1180,77,120) /
                                     # (667,1312,77,120): probed 2026-09-14, they are the two louvre lips flanking
                                     # the stripe ahead of the number panel - any stripe drawn at x >= 667 shows up
                                     # there as bright bars (the "mismatched white sections" of the first pass).
                                     # ~645..744 is otherwise under the cowl and never seen.
LIP_R = (667, 1180, 77, 120)         # louvre lip, car's RIGHT: inner end y 1300 = hood row 1279 (white's inner edge)
LIP_L = (667, 1312, 77, 120)         # louvre lip, car's LEFT: inner end y 1312 = hood row 1333
LIP_SCALE = 0.82                     # lip texels per hood texel across the car: 27 lip texels rendered 46 px
                                     # where the hood's 22-texel white renders 30 px (pass 4, dead front); the
                                     # rainbow band count had suggested 1.21 - the lip's inner rows are stretched
HOOD_NUM_MARGIN = 8
# THE HOOD V (pass 5, the designer's red guide lines, 2026-09-14): the white bands
# are wedges - full width (22) at the rear of the visible hood and tapering
# to nothing at the nose lip, the orange constant; the bumper is orange
# only.  Passes 2-4 (constant-width tape through the louvres) are dead -
# the louvre geometry made a parallel stripe read as stacked fragments.
HOOD_V_X0 = 215                      # white width 0 here (nose lip)
HOOD_V_X1 = 640                      # full white width from here to the cowl
HOOD_V_WMAX = 22                     # white wedge width at HOOD_V_X1 (22 = the recipe's white; ~55 = the bold spear)
HOOD_LIP_X = 470                     # hood column the louvre lips sit at (just ahead of the panel)
LIP_WHITE = True                     # lips carry the wedge at its local width (False = body black)
BUMPER_CS = (42, 21, 5)              # the bumper face renders ~5 % larger per texel than the hood lip at the crest
BUMPER_X = (10, 240)
ROOF_CS = CS
ROOF_X = (945, 1431)                 # starts BEHIND the banner island Z (834..934 sits inside M's bbox)
ROOF_BADGE_D, ROOF_BADGE_CX = 200, 1150
RING_GAP, RING_W = 6, 14
COVER_CS = CS
COVER_Y = (153, 443)
TAIL_CX = 1496                       # stub measured 18-20 px right of the exhaust / light centre from dead rear at 1512 (pass 6)
TAIL_CS = CS
TAIL_STRIPE_Y = (12, 44)             # a stub under the rain-light housing, above the wordmark
TAIL_WM_W, TAIL_WM_CXY = 260, (TAIL_CX, 74)   # on the panel BETWEEN the lights (the lower band hides behind the diffuser); 300 crowded the lights
TAIL_NAME_TOP = 13                   # a team name (--design) skips the box's top 13 rows (the wordmark's I-dot band,
                                     # rows 45..57 under the stub ending at 44): it keeps the example's clearance
BANNER_WM_W, BANNER_WM_CXY = 320, (884, 1306)
SASH = dict(xc=682, tilt=0.28, orange=46, white=23, gap=5)   # xc at the crown row; rear edge clears x 795
SASH_Y = (1584, 1790)
DOOR_NUM_MARGIN = 8
DOOR_WM_W, DOOR_WM_CXY = 260, (1160, 1798)
DOOR_DRIVER_W, DOOR_DRIVER_XY = 130, (1140, 1662)
Q_FF_W, Q_FF_CXY = 240, (1560, 1690)
Q_CDS_D, Q_CDS_CXY = 76, (1385, 1828)      # lower quarter under the side intake, clear of the door seam


def specify(im, rgb=T.SPEC_DECAL):
    out = Image.new("RGBA", im.size, tuple(rgb) + (255,))
    out.putalpha(im.getchannel("A"))
    return out


def _col(c, spec):
    return tuple(T.SPEC_LINE if spec else c) + (255,)


def _band_offsets(spec_widths):
    """(lo, hi, colour) of the bands relative to the centre line: the three
    bands the design's stripe style keeps (all three in classic); a dropped
    band leaves the others exactly where they were measured."""
    ow, ww, g = spec_widths
    return DESIGN.bands([(-ow / 2.0 - g - ww, -ow / 2.0 - g, LINE),
                         (-ow / 2.0, ow / 2.0, ACCENT),
                         (ow / 2.0 + g, ow / 2.0 + g + ww, LINE)])


def _cut(lo, hi, skips):
    """Split the run lo..hi by the (a, b) skips; yield the kept runs."""
    x = lo
    for a, b in sorted(skips):
        if a > x:
            yield x, min(a, hi)
        x = max(x, b)
    if x < hi:
        yield x, hi


def hbands(d, cy, widths, x0, x1, spec, skips=(), white_skips=()):
    """White|orange|white running along x, centred on row cy.  `skips` cut
    all three bands; `white_skips` cut only the two white bands (the RSR
    hood louvres swallow the outer half of the whites - the whites stop
    cleanly at the louvres and the orange runs through)."""
    for lo, hi, c in _band_offsets(widths):
        cuts = list(skips) + (list(white_skips) if c is LINE else [])
        for a, b in _cut(x0, x1, cuts):
            d.rectangle([a, int(round(cy + lo)), b - 1, int(round(cy + hi)) - 1], fill=_col(c, spec))


def vbands(d, cx, widths, y0, y1, spec, skips=()):
    """White|orange|white running along y, centred on column cx."""
    for lo, hi, c in _band_offsets(widths):
        for a, b in _cut(y0, y1, skips):
            d.rectangle([int(round(cx + lo)), a, int(round(cx + hi)) - 1, b - 1], fill=_col(c, spec))


def place(img, el, x, y, right):
    """TEXT and anything that must never mirror (playbook Rule 4).  (x, y) is
    the element's top-left in LEFT texture space; on the right it goes in
    ROTATE_180 at the mirrored rows, so it reads upright on both sides."""
    if right:
        img.alpha_composite(el.transpose(Image.ROTATE_180), (x, MIRROR + 1 - y - el.height))
    else:
        img.alpha_composite(el, (x, y))


def mirror_geometry(layer):
    """Reflect a LEFT-side-only layer to the right: pixel row y -> MIRROR - y.
    The layer must hold nothing but left-side marks (rows > 1306)."""
    a = np.array(layer)
    flipped = np.zeros_like(a)
    ys = np.arange(1306, H)
    dst = MIRROR - ys
    ok = (dst >= 0) & (dst < H)
    flipped[dst[ok]] = a[ys[ok]]
    return Image.alpha_composite(layer, Image.fromarray(flipped, "RGBA"))


def draw_sash(d, spec, k=1):
    """Three bands across the front fender's side face, crown to arch lip,
    top-forward lean (forward = lower x on the left island)."""
    s = SASH
    top, bot = SASH_Y
    for a, b, c in _band_offsets((s["orange"], s["white"], s["gap"])):
        pts = []
        for Y in (top, bot):
            xc = s["xc"] + s["tilt"] * (Y - top)
            pts.append(((xc + a) * k, Y * k))
        for Y in (bot, top):
            xc = s["xc"] + s["tilt"] * (Y - top)
            pts.append(((xc + b) * k, Y * k))
        d.polygon(pts, fill=_col(c, spec))


def wedge_w(x):
    """White wedge width (hood texels) at hood column x: 0 at the nose lip
    HOOD_V_X0, the full white width at HOOD_V_X1 and beyond."""
    ww = HOOD_V_WMAX
    t = (x - HOOD_V_X0) / float(HOOD_V_X1 - HOOD_V_X0)
    return ww * min(1.0, max(0.0, t))


def hood_wedges(spec):
    """The two white wedges of the hood V, supersampled 3x for clean
    diagonal edges.  Inner edge = the orange's gap (constant); outer edge
    tapers linearly from full width at HOOD_V_X1 to nothing at HOOD_V_X0."""
    K = 3
    ow, _, g = HOOD_CS
    ww = HOOD_V_WMAX
    big = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    inner = ow / 2.0 + g
    x0, x1, xe = HOOD_V_X0, HOOD_V_X1, HOOD_X[1]
    for sgn in (-1, 1):
        pts = [(x0, HOOD_CY + sgn * inner),
               (xe, HOOD_CY + sgn * inner),
               (xe, HOOD_CY + sgn * (inner + ww)),
               (x1, HOOD_CY + sgn * (inner + ww)),
               (x0, HOOD_CY + sgn * inner)]
        d.polygon([(px * K, py * K) for px, py in pts], fill=_col(LINE, spec))
    return big.resize((W, H), Image.LANCZOS)


def side_geometry(spec):
    """Everything on the LEFT side that mirrors: the fender sash.
    Supersampled 3x for clean diagonal edges, then mirrored to the right."""
    K = 3
    big = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    draw_sash(d, spec, k=K)
    layer = big.resize((W, H), Image.LANCZOS)
    return mirror_geometry(layer)


def side_text(img, spec):
    """Every side mark that must read upright on both sides (Rule 4)."""
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    wm = DESIGN.wordmark(int(DOOR_WM_W * 0.17))
    wm = wm.resize((DOOR_WM_W, int(wm.height * DOOR_WM_W / wm.width)), Image.LANCZOS)
    wm = S(DESIGN.lettering_box(wm))     # your team name in the same box + the "made with" credit
    ff = S(sponsors.logo_slot(LOGO2, Q_FF_W, ink=DESIGN.lettering, accent=DESIGN.graphic))
    ds = S(sponsors.driver_strip(DOOR_DRIVER_W, DRIVER_NAME, face=DESIGN.body,
                                 ink=DESIGN.lettering, accent=DESIGN.graphic))
    cat = S(sponsors.logo_slot(LOGO1, Q_CDS_D, **DESIGN.logo_colours))
    for right in (False, True):
        place(img, wm, DOOR_WM_CXY[0] - wm.width // 2, DOOR_WM_CXY[1] - wm.height // 2, right)
        place(img, ff, Q_FF_CXY[0] - ff.width // 2, Q_FF_CXY[1] - ff.height // 2, right)
        place(img, ds, *DOOR_DRIVER_XY, right=right)
        place(img, cat, Q_CDS_CXY[0] - cat.width // 2, Q_CDS_CXY[1] - cat.height // 2, right)
    # door number panels: drawn on the template blocks themselves (+ margin)
    m = DOOR_NUM_MARGIN
    for key in ("N1", "N3"):
        bx, by, bw, bh = NUMBER_BLOCKS[key]
        npnl = T.number_panel(bw + 2 * m, bh + 2 * m, fill=(T.SPEC_NUM if spec else T.WHITE))
        img.alpha_composite(npnl, (bx - m, by - m))


def centre_panels(img, spec):
    """Nose -> tail centre stripes and everything that sits on them."""
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    d = ImageDraw.Draw(img)
    # front bumper face: stripe runs along x (down the face), centred on row 1306
    # PASS 5 (the designer, 2026-09-14): the hood gets its OWN treatment - a tapered
    # V / spear.  The papaya centre band stays constant and centred nose ->
    # cowl and straight down the bumper; the two white bands are WEDGES:
    # full width at the rear of the visible hood (HOOD_V_X1), tapering
    # linearly to nothing at the nose lip (HOOD_V_X0), inner edge always the
    # orange's gap.  The bumper carries the orange only.  The louvres, their
    # lips and the number panel sit in the black / on top; nothing wraps them.
    # The design's stripe style: the orange is the wide stripe (stripe_on),
    # the wedges and the lips are the thin lines (lines_on); either may go,
    # the other stays exactly where it was measured.
    ow, ww, g = HOOD_CS
    if DESIGN.stripe_on:
        d.rectangle([BUMPER_X[0], int(round(BUMPER_CY - BUMPER_CS[0] / 2.0)),
                     BUMPER_X[1] - 1, int(round(BUMPER_CY + BUMPER_CS[0] / 2.0)) - 1], fill=_col(ACCENT, spec))
        d.rectangle([HOOD_X[0], int(round(HOOD_CY - ow / 2.0)), HOOD_X[1] - 1,
                     int(round(HOOD_CY + ow / 2.0)) - 1], fill=_col(ACCENT, spec))
    if DESIGN.lines_on:
        img.alpha_composite(hood_wedges(spec))
    d = ImageDraw.Draw(img)
    bx, by, bw, bh = NUMBER_BLOCKS["N2"]
    m = HOOD_NUM_MARGIN
    # The two LOUVRE-LIP islands render as thin ledges right in front of the
    # number panel, crossing the wedges (rainbow-probed, pass 4: lip y runs
    # the hood's way, inner end 1300 / 1312 = the white's inner edge, and
    # LIP_SCALE lip texels per hood texel).  They carry the wedge at its
    # local width there so the ledge does not read as a black bar; if the designer
    # would rather see them black, set LIP_WHITE = False.
    if LIP_WHITE and DESIGN.lines_on:
        lip_w = int(round(wedge_w(HOOD_LIP_X) * LIP_SCALE))
        if lip_w > 0:
            rx, ry, rw, rh = LIP_R
            d.rectangle([rx, ry + rh - lip_w, rx + rw - 1, ry + rh - 1], fill=_col(LINE, spec))
            lx, ly, lw, lh = LIP_L
            d.rectangle([lx, ly, lx + lw - 1, ly + lip_w - 1], fill=_col(LINE, spec))
    npnl = T.number_panel(bw + 2 * m, bh + 2 * m, fill=(T.SPEC_NUM if spec else T.WHITE))
    img.alpha_composite(npnl, (bx - m, by - m))
    d = ImageDraw.Draw(img)
    # roof + rear glass, through the roundel node
    cx, cy = ROOF_BADGE_CX, ROOF_CY
    r_ring = ROOF_BADGE_D / 2.0 + RING_GAP + RING_W
    hbands(d, ROOF_CY, ROOF_CS, ROOF_X[0], ROOF_X[1], spec,
           skips=[(int(cx - r_ring - RING_GAP), int(cx + r_ring + RING_GAP))])
    if DESIGN.lines_on:                  # the ring is one of the thin lines
        d.ellipse([cx - r_ring, cy - r_ring, cx + r_ring, cy + r_ring], fill=_col(LINE, spec))
    r_in = ROOF_BADGE_D / 2.0 + RING_GAP
    d.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in],
              fill=tuple(T.SPEC_BODY if spec else BODY) + (255,))
    # +x rearward, +y = car's left: read from the FRONT of the car = ROTATE_270
    badge = S(DESIGN.roundel(ROOF_BADGE_D)).transpose(Image.ROTATE_270)
    img.alpha_composite(badge, (cx - badge.width // 2, cy - badge.height // 2))
    d = ImageDraw.Draw(img)
    # engine cover: stripe runs along y (rearward), centred on column 318
    vbands(d, COVER_CX, COVER_CS, COVER_Y[0], COVER_Y[1], spec)
    # tail: stripe on the panel between the lights, wordmark + rule below
    vbands(d, TAIL_CX, TAIL_CS, TAIL_STRIPE_Y[0], TAIL_STRIPE_Y[1], spec)
    wm = DESIGN.wordmark(int(TAIL_WM_W * 0.17))
    wm = wm.resize((TAIL_WM_W, int(wm.height * TAIL_WM_W / wm.width)), Image.LANCZOS)
    tx, ty = TAIL_WM_CXY[0] - wm.width // 2, TAIL_WM_CXY[1] - wm.height // 2
    if DESIGN.team_name:
        # your team name takes the band the wordmark's AI caps fill, not the
        # top TAIL_NAME_TOP rows where only the I's dots sit (beside the stub):
        # a name filling the whole box would touch the stripe stub above it
        box = Image.new("RGBA", (wm.width, wm.height - TAIL_NAME_TOP), (0, 0, 0, 0))
        wm, ty = DESIGN.lettering_box(box, credit=False), ty + TAIL_NAME_TOP   # the credit rides on the doors
    img.alpha_composite(S(wm), (tx, ty))
    # (a tow arrow at (1130,160) on the lower band never showed on the render -
    # that band is hidden under the lights / diffuser.  Milestone 2: probe the
    # rear corners (T1 / T7) for a visible tow-arrow spot.)
    # windscreen banner: wordmark across the sun strip, read from the front
    bw_ = DESIGN.wordmark(int(BANNER_WM_W * 0.17))
    bw_ = bw_.resize((BANNER_WM_W, int(bw_.height * BANNER_WM_W / bw_.width)), Image.LANCZOS)
    bw_ = S(DESIGN.lettering_box(bw_, credit=False))  # the credit rides on the doors
    bw_ = bw_.transpose(Image.ROTATE_270)
    img.alpha_composite(bw_, (BANNER_WM_CXY[0] - bw_.width // 2, BANNER_WM_CXY[1] - bw_.height // 2))


def build(spec=False):
    img = Image.new("RGBA", (W, H), tuple(T.SPEC_BODY if spec else BODY) + (255,))
    img.alpha_composite(side_geometry(spec))
    side_text(img, spec)
    centre_panels(img, spec)
    img = img.convert("RGB")
    if spec:
        d = ImageDraw.Draw(img)
        for x, y, w, h in NUMBER_BLOCKS.values():
            d.rectangle([x, y, x + w - 1, y + h - 1], fill=T.SPEC_NUM)
    return img


# --- spec map: the MX-5 v4.1 "Satin-True" (B3) hierarchy, carried over
# unchanged (validated on the F4).  NOT yet validated on the RSR - milestone 1
# stops before spec work; the A/B against no spec map is a milestone-2 job.
SPEC_VARIANTS = {
    "B3": {"body": (0, 170, 200), "orange": (0, 35, 16), "white": (0, 55, 30),
           "decal": (0, 120, 150), "num": (0, 60, 110)},
}
SPEC_DEFAULT = "B3"
SPEC_ORANGE_GROW = 3


# A LOCAL spec-map helper for designs (the Spec Racer Ford's): the number
# panels keep the car's own B3 white (see spec_from_colour).  A no-op in the
# example scheme, so the ready-made spec map is untouched byte for byte.
def _panel_cover():
    """Every texel the white number panels cover: the doors' N1 / N3
    (side_text()) and the hood's N2 (centre_panels())."""
    cov = np.zeros((H, W), dtype=bool)
    for key, m in (("N1", DOOR_NUM_MARGIN), ("N2", HOOD_NUM_MARGIN), ("N3", DOOR_NUM_MARGIN)):
        bx, by, bw, bh = NUMBER_BLOCKS[key]
        p = np.asarray(T.number_panel(bw + 2 * m, bh + 2 * m).getchannel("A")) > 0
        cov[by - m:by - m + p.shape[0], bx - m:bx - m + p.shape[1]] |= p
    return cov


def spec_from_colour(img, variant=SPEC_DEFAULT):
    P0 = SPEC_VARIANTS[variant]
    P = DESIGN.spec_values(P0)              # the design's finishes, where it names any
    a = np.asarray(img.convert("RGB")).astype(np.int16)
    keys = DESIGN.material_keys(BODY, ACCENT)
    dist = np.stack([np.abs(a - np.array(c, dtype=np.int16)).sum(axis=2) for _, c in keys], axis=0)
    best = dist.argmin(axis=0)
    close = dist.min(axis=0) <= 200
    out = np.empty(a.shape, dtype=np.uint8)
    out[...] = P["decal"]
    for i, (name, _) in enumerate(keys):
        out[(best == i) & close] = P[name]
    # The panels are T.WHITE, which material_keys sorts into the "white" slot
    # that a design's trim finish replaces: a chrome or matte trim would rim
    # every number.  Put the panel texels back to the car's own B3 white
    # (what the example gives them, so a no-op there).
    panel_white = np.array([tuple(c) == tuple(T.WHITE) for _, c in keys])[best] & close
    out[_panel_cover() & panel_white] = P0["white"]
    orange_ish = DESIGN.stripe_mask(a)      # papaya's hue test in the example scheme
    m = orange_ish
    g = SPEC_ORANGE_GROW
    if g:
        pad = np.pad(m, g)
        acc = np.zeros_like(m)
        for dy in range(-g, g + 1):
            for dx in range(-g, g + 1):
                if dx * dx + dy * dy <= g * g:
                    acc |= pad[g + dy:g + dy + m.shape[0], g + dx:g + dx + m.shape[1]]
        m = acc
    out[m] = P["orange"]
    spec = Image.fromarray(out, "RGB")
    d = ImageDraw.Draw(spec)
    for x, y, w, h in NUMBER_BLOCKS.values():
        d.rectangle([x, y, x + w - 1, y + h - 1], fill=P["num"])
    return spec


def check_number_blocks(img):
    """A block may be base colour or the flat white number panel.  Anything
    else - a stripe, a mark, an antialiased edge drifting in - fails."""
    px = img.load()
    ok = (BODY, T.WHITE)
    bad = []
    for name, (x, y, w, h) in NUMBER_BLOCKS.items():
        off = sum(1 for yy in range(y, y + h) for xx in range(x, x + w)
                  if min(sum(abs(a - b) for a, b in zip(px[xx, yy], c))
                         for c in ok) > 6)
        print("  %s %s %d bad / %d px" % (name, "DIRTY" if off else "clean",
                                         off, w * h))
        if off:
            bad.append(name)
    return bad


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--here", action="store_true")
    ap.add_argument("--no-spec", action="store_true")
    ap.add_argument("--png", action="store_true")
    personalize.add_args(ap)
    args = ap.parse_args()
    cfg = personalize.resolve(args)
    apply_design(cfg.design)
    CUSTOMER = cfg.id
    DRIVER_NAME = cfg.driver
    LOGO1, LOGO2 = cfg.logo1, cfg.logo2
    out_dir = cfg.out_dir or (os.getcwd() if args.here else personalize.default_out_dir())
    os.makedirs(out_dir, exist_ok=True)
    colour = build(spec=False)
    print("number blocks:")
    bad = check_number_blocks(colour)
    if bad:
        sys.exit("FAIL: artwork is inside %s - fix the geometry, do not mask it."
                 % ", ".join(bad))
    print("  RESULT: PASS")
    out = os.path.join(out_dir, "car_%s.tga" % CUSTOMER)
    colour.save(out, compression="tga_rle")
    with open(out, "rb") as fh:
        head = fh.read(18)
    assert head[2] == 10 and head[16] == 24, "bad TGA header: %r" % head[:18]
    print("wrote", out, "(RLE 24-bit, header verified)")
    if args.png:
        colour.save(os.path.join(out_dir, "car_%s.png" % CUSTOMER))
    if not args.no_spec:
        s = os.path.join(out_dir, "car_spec_%s.tga" % CUSTOMER)
        spec_from_colour(colour).save(s, compression="tga_rle")
        with open(s, "rb") as fh:
            head = fh.read(18)
        assert head[2] == 10 and head[16] == 24, "bad spec TGA header: %r" % head[:18]
        print("wrote", s, "(spec B3 Satin-True, RLE 24-bit, header verified)")
