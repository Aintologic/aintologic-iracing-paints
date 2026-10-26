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

"""TEAM SCHEME - Global Mazda MX-5 Cup (#67).  First car on the scheme.

The AINTOLOGIC team livery (docs/PAINT-SCHEME.md) placed on the MX-5's
verified panel map (docs/car-maps/mx5-2016-global-cup.md).  Every mark comes
from src/teamscheme.py; this file holds ONLY the MX-5's geometry and
placements.  Copy this file as the pattern for the F4 and the RSR - change
the rects and the placements, nothing else.

    python src/team_mx5.py --id <id>    -> out/car_<id>.tga in the project folder, blank driver, YOUR LOGO slots
    python src/team_mx5.py --id <id> --driver "A. DRIVER" --logo1 cds.png --logo2 ff.png
    python src/team_mx5.py --design my-mx5   -> your own colours, team name, stripes
    python src/team_mx5.py --here       -> write to the cwd instead of out/
    python src/team_mx5.py --no-spec    -> colour map only
    python src/team_mx5.py --png        -> also write the flat texture as PNG
    python src/team_mx5.py --spec-variant B1   -> put test finish B1 in car_spec_<id>.tga
    python src/team_mx5.py --finish-tests      -> also write the four test finishes
                                                  as car_spec_<id>_B1.tga .. _B4.tga

Writes car_<id>.tga (+ car_spec_<id>.tga, the approved B3 finish).  Nothing
else unless you ask: the four test finishes were for comparing finishes during
development and are written only with --finish-tests.  The personalization flags
(--id/--driver/--logo1/--logo2/--out/--profile/--design) are defined in
src/personalize.py; a design's colours, team name and stripe style come from
src/design.py.
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageChops, ImageDraw
import teamscheme as T
import sponsors
import personalize
import iracingpaths
import design

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUSTOMER = personalize.DEFAULT_ID
PAINT_DIR = iracingpaths.paint_folder("mx5 mx52016")
# personalization, set from the CLI/profile in __main__ before build() runs:
DRIVER_NAME = ""                       # blank driver strip by default
LOGO1 = sponsors.placeholder_logo      # Cats Don't Suck slot (boot lid)
LOGO2 = sponsors.placeholder_logo      # FreakFarm slot (rear quarters)
DESIGN = design.EXAMPLE                # your own design (--design); apply_design() sets it
W = H = 2048

# --- verified panel map (docs/car-maps/mx5-2016-global-cup.md) ----------------
FLANK_R = (386, 1679, 884, 306)   # upright
FLANK_L = (386,  507, 884, 306)   # renders ROTATE_180
HOOD    = ( 12,  880, 706, 732)   # renders 90 CW -> draw ROTATE_90
DECK    = (1132, 130, 747, 456)   # ROTATE_180, visible area is a diagonal band
DECK_CDS_D = 150                            # Cats Don't Suck on the boot lid (position below)
VALANCE = (16, 11, 1179, 441)     # upright; x 0..940 runs straight across the tail
NOSE    = (768, 1024, 1280, 384)  # upright; local y=0 just under the headlights
QUARTER_R = (1280, 1536, 256, 256)  # the rear quarter the valance does NOT carry
FW, FH  = FLANK_R[2], FLANK_R[3]

NUMBER_BLOCKS = {"N1": (493, 577, 123, 105),
                 "N2": (493, 1810, 123, 105),
                 "N3": (777, 214, 89, 74)}

# REVERSED 2026-09-13 on the designer's review of the first pass: "much too
# orange".  BLACK is the body, papaya is the ACCENT - a stripe along the
# band edge with a thin white line above it - and every mark sits on black
# the way the logo does.  The lower band is the same black in colour and
# separates only as a MATERIAL (satin) in the spec map.
BODY, BAND, LINE, ACCENT = T.BLACK, T.BLACK, T.WHITE, T.PAPAYA


def apply_design(ds):
    """Build with design ds (src/design.py): its colours, lettering and stripe
    style.  The names here predate it: LINE is the design's accent (the thin
    lines), ACCENT its stripe colour, and the lower band stays body colour."""
    global DESIGN, BODY, BAND, LINE, ACCENT
    DESIGN = ds
    BODY, BAND, LINE, ACCENT = ds.body, ds.body, ds.trim, ds.graphic

# --- flank layout, car-space: x = 0 at 20.6% of car length (just behind the
# front wheel), x = 884 at 71.5% (just behind the door); y = 0 belt line,
# y = 271 bottom of sill, below ~250 is not visible from outside.
BAND_EDGE = [(0, 132), (884, 98)]     # top of the black band, rising aft
LINE_W = 4                            # white coachline above the stripe
ACC_W = 16                            # papaya stripe on the band edge
LIP = 48                              # rocker lip rows past the flank rect
NUM_PANEL = (94, 118, 148, 130)       # covers N2 (107,131,123,105) fully
WM_W, WM_CXY = 400, (555, 176)        # AINTOLOGIC across the door, on black
DRIVER_W, DRIVER_XY = 118, (322, 12)  # driver strip at the belt, door front
CUTOFF_H, CUTOFF_XY = 26, (452, 10)   # cutoff triangle beside it
EXT_D, EXT_XY = 24, (488, 11)
ROUNDEL_D, ROUNDEL_XY = 66, (150, 30)  # team badge: above the 404, behind the sash
FF_W, FF_XY = 112, (745, 206)         # Freak Farm, small, on the band aft
CDS_D, CDS_XY = 40, (268, 196)        # Cats Don't Suck, small, band forward

# MEASURED 2026-09-13 with a 6x6 grid over the hood rect, read from above:
# texture x runs ALONG the car (col A = nose, col F = cowl), texture y runs
# ACROSS it.  The visible bonnet is columns B..E (texture x 129..597) and
# rows 1..6 less a sliver at the far edge.  Column F and beyond is the cowl
# and the windscreen-header sun shade - a 460px badge at +125 spilled onto
# it.  The visible centre is the CANVAS CENTRE: (365, 351) on the 732x706
# canvas.  The old "+125 toward the cowl" note was wrong.
HOOD_BADGE_D, HOOD_WM_DY = 250, 0   # 400 filled the bonnet and left no room for the stripes (2026-09-14)
NOSE_BAND = (40, 134)                 # local y of the black band on the fascia
NOSE_TOW = (500, 300)
# bumper corners: the outer columns of the nose rect.  The stripe rises
# there to meet the fender stripe at the seam (seam probe 2026-09-13).
NOSE_RISE, NOSE_SEAM_Y, NOSE_MIRROR = 130, 4, 240
# PROBED 2026-09-13 (tools/probe.py, 8x8 grid then rect/bands probes, read
# from level rear three-quarters on BOTH sides):
#   * the valance rect's LOW-x columns (local x 0..~250) are one rear quarter
#     behind the wheel, and its HIGH-x columns (local x ~1008..1179) are the
#     other.  The old "narrow col 1 to 0..180, it hits the plate recess" note
#     was a misread: the plate recess is at local x ~500..750.
#   * local y 280 on the valance is the SAME screen height as the door band's
#     top edge at the rear of the door, so one band at 280 down reads as
#     continuous from door to quarter to tail.
#   * the quarters keep rendering BELOW the rect's bottom edge: texture rows
#     452..512 in those columns are also the lower quarter (VAL_BELOW).
#   * (1280,1536,256,256) is the shoulder ABOVE the arch on the upright-flank
#     side and (1536,768,256,256) the same on the other; both sit above the
#     band line and stay papaya.  Painting (1280,1536) was the "patch too
#     high" in the first pass.
VAL_BAND = (276, 441)   # local; tex 287: line 287..292, orange 292..314
VAL_COLS = (250, 1000)  # local; texture 266..1016, under both quarter islands
VAL_BELOW = [(16, 270), (1024, 1195)]  # texture x ranges, y 452..512
VAL_WM_W, VAL_WM_CXY = 280, (560, 160)
VAL_CHK_W, VAL_CHK_CXY = 200, (560, 206)
VAL_TOW = (150, 372)


# =============================================================================
# FENDER STRIPES - Sebring/Cobra style.  2026-09-13, the designer's new direction.
#
# The front-to-rear ribbon is GONE (it lives in git history and in
# releases v3.4..v3.5).  In its place: three
# parallel bands across each FRONT fender only - white | PAPAYA | white,
# the orange twice a white - running from the top of the fender down its
# outer face, roughly across the car, just behind the front wheel arch.
# Drawn straight onto the two flank islands in car-side terms (X along the
# car in flank px, X 0 = door front, negative = forward; Y down from the
# belt), through the measured fender x-table below.  Nothing global.
FLANK_X = [(-310, 0), (-283, 100), (-267, 130), (-240, 160), (-202, 200),
           (-152, 250), (-101, 300), (-50, 350), (0, 386), (884, 1270)]
FLANK_TEX = [(t, X) for X, t in FLANK_X]      # texture x -> X

def _interp(v, table):
    if v <= table[0][0]:
        (a, fa), (b, fb) = table[0], table[1]
    elif v >= table[-1][0]:
        (a, fa), (b, fb) = table[-2], table[-1]
    else:
        for (a, fa), (b, fb) in zip(table, table[1:]):
            if a <= v <= b:
                break
    return fa + (fb - fa) * (v - a) / float(b - a)

FENDER_ARCH = (-136, 240, 136, 162)   # the front arch lip: centre, rx, ry (measured)
# PROBED 2026-09-13 (scratch\probeTop2.py): the fender's TOP surface is the
# 64 texture rows just past the flank rect's belt edge - rows 1615..1678
# above FLANK_R, rows 814..877 below FLANK_L - and the hood rect's outer
# rows beyond those are the hood's own edge strip.  So Y runs to -64.
# the designer's red box 2026-09-13: the sash sits at the fender's REAR edge, over
# the front of the 404, leaning top-forward / bottom-rearward, from the
# hood shut line down to the sill.
FS_XC = 2            # X of the group's centre line at the belt (refinement 2026-09-14: 12 forward)
FS_TILT = 0.28       # dX per Y: top forward, bottom rearward
FS_BOTTOM = 250      # Y where the bands stop: the 404 panel's bottom (sill lip ~271)
FS_ORANGE = 40       # papaya band, X units (refinement: +18%)
FS_WHITE = 20        # each white band (orange = 2x white)
FS_GAP = 5           # body-colour gap between bands
FS_TOP = -64         # Y where the bands start: the hood shut line
FS_LIP = 6           # stop this far above the arch lip
FS_SUPER = 3         # AA subsamples per texture px, each axis
# SEAM PASS 2026-09-14 (scratch\probeSeam.py, tick rulers either side of
# the shut line, scanned with scanseam/scanorange):
#  * the fender renders UNIFORMLY in texture px (1.08 frame px per texel at
#    the seam, same as the hood's 1.09 per canvas px), so the FLANK_X
#    table's squeeze between X -50..0 (36 texels for 50 X) is not physical
#    there - it made the front white render 15 px against the rear's 22.
#    The sash is therefore laid out in TEXELS from the door front (X 0 =
#    texel 386), FS_X_SCALE per X, not through the table.
#  * the shut line is a real crease, so NO pair of texture directions looks
#    straight from every viewpoint.  The join was tuned on the render in the
#    poses the designer judges from (side, slightly elevated; elevated front 3/4):
#    the sash centre line eases from FS_TILT_TOP at the shut line to FS_TILT
#    by FS_EASE_Y, and the hood feeder leaves the seam at FEED_TILT0 and
#    bends (quadratic Bezier) to radial at the node.
FS_X_SCALE = 1.0     # texels per X (uniform)
FS_X0_TEX = 386      # texel of X 0 (door front) in the flank rects
FS_EASE_Y = 0        # tilt is fully FS_TILT from this Y down; FS_TILT_TOP at FS_TOP
FS_TILT_TOP = 0.0    # dX per Y at the shut line (tuned against the render with FEED_TILT0)
FS_XC_SIDE = {"R": 0, "L": 15}   # per-side shift of the whole sash in texels.  NOTE the keys are
                                 # the FLANK RECTS: "L" (FLANK_L, the rotated rect, 813-Y) renders on
                                 # the car's RIGHT side.  15 is the state the designer approved from the
                                 # render (scratch\fin\sR4_side.jpg, 2026-09-14) - at 15 the orange
                                 # spans texels 374..413 on row 877 (scratch\texcheck.py).  The car's
                                 # LEFT ("R" rect, 0) is approved and locked.


def _sash_centre(Y):
    """X of the group's centre line at Y, and its slope dX/dY."""
    if Y >= FS_EASE_Y:
        return FS_XC + FS_TILT * Y, FS_TILT
    span = float(FS_EASE_Y - FS_TOP)
    d = FS_EASE_Y - Y
    k = FS_TILT - FS_TILT_TOP
    return FS_XC + FS_TILT * Y + k * d * d / (2.0 * span), FS_TILT - k * d / span


def _fender_bands():
    """[(x0, x1, colour)] offsets across the group, in X at Y = 0."""
    half = FS_ORANGE / 2.0
    return DESIGN.bands([(-half - FS_GAP - FS_WHITE, -half - FS_GAP, LINE),
                         (-half, half, ACCENT),
                         (half + FS_GAP, half + FS_GAP + FS_WHITE, LINE)])


def _arch_top(X):
    cx, cy, rx, ry = FENDER_ARCH
    t = (X - cx) / float(rx)
    return cy - ry * (1.0 - t * t) ** 0.5 if abs(t) < 1.0 else 10 ** 6


# =============================================================================
# CENTRE STRIPES - Cobra style, white | PAPAYA | white down the middle of the
# car, nose -> hood -> (cockpit) -> boot lid -> tail.  Same 2:1 language as
# the sash.  the designer's mockup 2026-09-14.  Each panel is drawn in its own
# texture terms with the group width scaled to that panel's texel density;
# the hood roundel is a NODE: the stripes stop at a white outer ring and
# restart behind it.
#
# PROBED 2026-09-14 (scratch\probeCentre.py, probeDeck.py):
#   hood canvas: x = across the car (centre hw/2), y = along it, y 0 = nose,
#                visible bonnet y 129..597 (columns B..E)
#   nose rect:   the fascia centre is local x 585 (the corners are symmetric
#                about it); a vertical band there sits under the Mazda badge
#   deck rect:   texture x = across the car, y = fore-aft with y 456 at the
#                boot's trailing edge; the car centre is column D, x ~434;
#                rows above ~228 are NOT the lid (they map to the lower rear
#                quarters) - keep off them
#   valance:     local x 560 is the tail centre (the wordmark's centre)
CS_HOOD = (60, 30, 7)      # orange, white, gap on the hood canvas (px)
CS_NOSE = (62, 31, 7)      # on the nose rect - same texel density as the hood (probeFront 2026-09-14)
CS_DECK = (54, 27, 7)      # on the boot lid.  REAR PASS 2026-09-14 (scratch\widthcmp.py, dead front
                           # and dead rear at the same zoom): the nose orange renders 7.0% of the
                           # car's width; at 64 the rear rendered 8.4%, at 48 6.2%; 54 -> 7.0%
CS_TAIL = (54, 27, 7)      # on the tail face (valance rect); a dead-rear frame renders lid and
                           # bumper at the same px/texel, so the same widths as the lid
CS_HOOD_X = None           # None = canvas centre
CS_HOOD_Y = (0, 610)       # from the hood's front lip (column A shows from the front) to the cowl
CS_NOSE_X = 585
# PROBED 2026-09-14 (scratch\probeFront.py): nose rows 0..255 are the fascia
# around the Mazda badge; rows 256..383 are the MIRROR CAPS (both); texture
# rows 940..1023 above the rect are the bumper's upper face under the
# headlights; rows 1408..1500 below it are the lower lip.
CS_NOSE_ROWS = (0, 250)
CS_BUMPER_TOP = (940, 1024)
CS_LIP = (1408, 1500)
CS_DECK_X, CS_DECK_Y = 415, (104, 456)   # lid rows run up to ~100 at the third brake light (probeLid).
                           # X: rear pass 2026-09-14, dead-rear frame (scratch\rearref.py): lid orange
                           # centre vs the tail-light centre line = +5 px at 420 -> 415 puts it on
                           # the car's centre line (and the Mazda badge) within 0.5 px
CS_TAIL_X = 591            # same frame: bumper orange was +8 px at 599 -> 591 sits on the same line
                           # as the lid; the wordmark (560) and the plate recess are both off-centre
CS_TAIL_SKIP = (118, 240)  # rows around the AINTOLOGIC wordmark + checker: stripes stop / restart
RING_GAP, RING_W = 6, 26   # dark gap then white ring outside the hood roundel
# the sash meets the hood shut line at canvas y ~425 (probeFront top view,
# labels L8/L9); from there it continues across the hood, aimed at the
# roundel, and stops at the node's gap - the sash and the centre stripes
# become one system.  Widths: the hood canvas runs ~1.3x the flank's texels.
FEED_Y = 434               # seam pass: hood 1.09 px/unit vs fender 1.08 px/texel; the sash centre
                           # at the shut line measured 19 frame px rearward of the feeder at 408,
                           # plus 9 texels for the tilt ease (FS_EASE_Y)
FEED_Y_DX0, FEED_Y_DXW = -5, 10  # per-edge trim of FEED_Y: canvas x=0 is the LEFT (driver) side,
                                 # which rendered 5 px rearward of its sash with the shared value;
                                 # the RIGHT edge (x=hw) rendered ~10 px forward of its sash
FEED_TILT0 = 0.2           # feeder direction at the seam, canvas dy per dx inward.  Tuned on
                           # the RENDER (seamrun.py, two camera poses per side): +0.2 makes the
                           # hood's lean match the sash's on both sides of the shut line; the
                           # textbook guesses (-0.12 "seam perpendicular", 0.15 radial) both kinked
FEED_TILT_DX0, FEED_TILT_DXW = 0.0, -0.3  # per-edge trim of FEED_TILT0: the hood island is not
                                          # mirror-symmetric; the right edge needs a steeper exit
                                          # (-0.1 net) to run into its sash (right-side pass 2026-09-14)
FEED_BLEND = 0.45          # how far (fraction of the run) the seam direction persists before radial
FEED_W = (40, 20, 5)       # rendered 1.3x wider than the sash at (45,22,5): the hood's
                           # texels are the flank's size after all (ref screenshot 02)

DECK_CDS_CXY = (600, 285)  # the cat moves off the centre line (was 558)


def _band_rects(cx, spec_widths):
    """Three (x0, x1, colour) spans across x for a white|orange|white group."""
    ow, ww, g = spec_widths
    return DESIGN.bands([(cx - ow / 2.0 - g - ww, cx - ow / 2.0 - g, LINE),
                         (cx - ow / 2.0, cx + ow / 2.0, ACCENT),
                         (cx + ow / 2.0 + g, cx + ow / 2.0 + g + ww, LINE)])


def _vbands(draw, cx, widths, y0, y1, spec, skip=None):
    """Vertical white|orange|white bands on a Draw, x centred at cx, rows y0..y1,
    optionally leaving rows skip=(a, b) untouched."""
    for x0, x1, c in _band_rects(cx, widths):
        col = tuple(T.SPEC_LINE if spec else c) + (255,)
        if skip:
            draw.rectangle([x0, y0, x1 - 1, skip[0] - 1], fill=col)
            draw.rectangle([x0, skip[1], x1 - 1, y1 - 1], fill=col)
        else:
            draw.rectangle([x0, y0, x1 - 1, y1 - 1], fill=col)



def _feeders(hood, hcx, hcy, spec):
    """The sash's continuation across the hood: three bands from each hood
    edge at FEED_Y, aimed at the roundel centre, supersampled."""
    import math
    hw, hh = hood.size
    K = 3
    big = Image.new("RGBA", (hw * K, hh * K), (0, 0, 0, 0))
    bd = ImageDraw.Draw(big)
    ow, ww, g = FEED_W
    for x_edge in (0, hw):
        sgn = 1.0 if x_edge == 0 else -1.0
        # quadratic Bezier: P0 on the seam (extended FEED_BLEED beyond it),
        # initial direction (inward, FEED_TILT0 along per across), control
        # point P1 down that direction, P2 = node centre so the end tangent
        # is radial.
        fy = FEED_Y + (FEED_Y_DX0 if x_edge == 0 else FEED_Y_DXW)
        p0 = (x_edge, fy)
        d0 = (sgn, FEED_TILT0 + (FEED_TILT_DX0 if x_edge == 0 else FEED_TILT_DXW))
        dl = math.hypot(*d0)
        d0 = (d0[0] / dl, d0[1] / dl)
        Ltot = math.hypot(hcx - x_edge, hcy - fy)
        p1 = (p0[0] + d0[0] * Ltot * FEED_BLEND, p0[1] + d0[1] * Ltot * FEED_BLEND)
        p2 = (hcx, hcy)
        N = 80
        cl, tn = [], []
        for k in range(-6, N + 1):
            s = k / float(N)
            if s < 0:                      # straight bleed past the seam
                cl.append((p0[0] + d0[0] * s * Ltot, p0[1] + d0[1] * s * Ltot))
                tn.append(d0)
                continue
            x = (1 - s) ** 2 * p0[0] + 2 * (1 - s) * s * p1[0] + s * s * p2[0]
            y = (1 - s) ** 2 * p0[1] + 2 * (1 - s) * s * p1[1] + s * s * p2[1]
            tx_ = 2 * (1 - s) * (p1[0] - p0[0]) + 2 * s * (p2[0] - p1[0])
            ty_ = 2 * (1 - s) * (p1[1] - p0[1]) + 2 * s * (p2[1] - p1[1])
            tl = math.hypot(tx_, ty_) or 1.0
            cl.append((x, y)); tn.append((tx_ / tl, ty_ / tl))
        for a, b, c in DESIGN.bands([(-ow / 2.0 - g - ww, -ow / 2.0 - g, LINE), (-ow / 2.0, ow / 2.0, ACCENT),
                                     (ow / 2.0 + g, ow / 2.0 + g + ww, LINE)]):
            col = tuple(T.SPEC_LINE if spec else c) + (255,)
            left, right = [], []
            for (x, y), (ux, uy) in zip(cl, tn):
                nx, ny = -uy, ux
                left.append(((x + nx * a) * K, (y + ny * a) * K))
                right.append(((x + nx * b) * K, (y + ny * b) * K))
            bd.polygon(left + right[::-1], fill=col)
    big = big.resize((hw, hh), Image.LANCZOS)
    hood.alpha_composite(big, (0, 0))

def draw_fender_stripes(img, spec):
    """Both front fenders.  Per texture pixel of the fender region, invert
    the flank x-table to X, test the band polygons in car space, supersample
    for the edges.  Upright side: rows 1679 + Y; rotated side: 813 - Y."""
    bands = _fender_bands()
    if spec:
        bands = [(x0, x1, T.SPEC_LINE) for x0, x1, c in bands]
    import math
    px = img.load()
    xs = range(int(FS_X0_TEX + (FS_XC - 110) * FS_X_SCALE), int(FS_X0_TEX + (FS_XC + 110) * FS_X_SCALE) + 1)
    n = FS_SUPER
    for side in ("R", "L"):
        for tx in xs:
            for Y in range(FS_TOP, FS_BOTTOM):
                ty = 1679 + Y if side == "R" else 813 - Y
                hits = {}
                for i in range(n):
                    for j in range(n):
                        txx = tx + (i + 0.5) / n
                        X = (txx - FS_X0_TEX) / FS_X_SCALE          # uniform texel mapping
                        Xa = _interp(txx, FLANK_TEX)                # table X, for the arch only
                        Yy = Y + (j + 0.5) / n
                        if Yy >= _arch_top(Xa) - FS_LIP or Yy < FS_TOP or Yy >= FS_BOTTOM:
                            continue
                        xc, sl = _sash_centre(Yy)
                        xc += FS_XC_SIDE[side]
                        u = (X - xc) * math.cos(math.atan(sl))     # across the group, perpendicular
                        for x0, x1, c in bands:
                            if x0 <= u < x1:
                                hits[c] = hits.get(c, 0) + 1
                                break
                if hits:
                    tot = n * n
                    base = px[tx, ty]
                    r = g = bb = 0.0
                    cov = 0
                    for c, k in hits.items():
                        r += c[0] * k; g += c[1] * k; bb += c[2] * k; cov += k
                    f = cov / float(tot)
                    px[tx, ty] = (int(round((r / cov) * f + base[0] * (1 - f))),
                                  int(round((g / cov) * f + base[1] * (1 - f))),
                                  int(round((bb / cov) * f + base[2] * (1 - f))))


def place(panel, el, x, y, left):
    """TEXT and anything that must never mirror.  Playbook Rule 4."""
    if left:
        panel.alpha_composite(el.transpose(Image.ROTATE_180),
                              (x, FH - y - el.height))
    else:
        panel.alpha_composite(el, (x, y))


def place_pic(panel, el, x, y, left):
    """DIRECTIONAL artwork.  Playbook Rule 4a."""
    if left:
        panel.alpha_composite(el.transpose(Image.FLIP_TOP_BOTTOM),
                              (x, FH - y - el.height))
    else:
        panel.alpha_composite(el, (x, y))


def specify(im, rgb=T.SPEC_DECAL):
    out = Image.new("RGBA", im.size, tuple(rgb) + (255,))
    out.putalpha(im.getchannel("A"))
    return out


def flank_panel(spec, left):
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    panel = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
    # --- number panel on N2 --------------------------------------------------
    npx, npy, npw, nph = NUM_PANEL
    place(panel, T.number_panel(npw, nph, fill=(T.SPEC_NUM if spec else T.WHITE)),
          npx, npy, left)
    # --- marks ----------------------------------------------------------------
    wm = DESIGN.wordmark(int(WM_W * 0.17))
    wm = wm.resize((WM_W, int(wm.height * WM_W / wm.width)), Image.LANCZOS)
    wm = DESIGN.lettering_box(wm)          # your team name in the same box, if you gave one
    place(panel, S(wm), WM_CXY[0] - wm.width // 2, WM_CXY[1] - wm.height // 2, left)
    place(panel, S(sponsors.driver_strip(DRIVER_W, DRIVER_NAME, face=DESIGN.body,
                                         ink=DESIGN.lettering, accent=DESIGN.graphic)),
          *DRIVER_XY, left)
    place(panel, S(sponsors.cutoff_triangle(CUTOFF_H, spark=T.WHITE,
                                            edge=T.WHITE)), *CUTOFF_XY, left)
    place(panel, S(sponsors.extinguisher_mark(EXT_D, face=T.WHITE,
                                              ink=T.BLACK)), *EXT_XY, left)
    # 2026-09-14: the team roundel, Freak Farm and Cats Don't Suck moved off
    # the door to the rear quarter - see rear_quarter_decals().
    return panel


# --- rear quarter decals ------------------------------------------------------
# the designer, 2026-09-14: the three small decals (team roundel, Freak Farm, Cats
# Don't Suck) move off the door onto the rear quarter, larger and stacked
# like a race car's sponsor block.  The door wordmark stays where it is.
# PROBED 2026-09-14 (scratch\probeRQ.py, 5x4 / 4x2 labelled grids, read from
# level sides).  The two quarters are NOT the same islands:
#   car's LEFT  = (1280,1536,380,266) upright.  5 cols x 4 rows of 76x66:
#                 col 0 starts at the door edge, col 4 ends at the tail light,
#                 row 0 is the shoulder crease, row 3 is the arch.  The arch
#                 eats rows 2-3 under cols 1-2; cols 0 and 3-4 are tall.
#                 Renders ~0.57 px/texel across, ~0.45 down (level side, this
#                 zoom) - so a round mark needs texture w:h = 0.79.
#   car's RIGHT = two islands.  (1297,600,355,200) ROTATE_180 is the LOWER
#                 band next to the door (its rows 2-3, raw y 700..800, are the
#                 visible skin; cols 0-2 reach the crease, cols 3-4 sit under
#                 the S island).  (1536,768,256,96) ROTATE_180 is the UPPER
#                 shoulder from mid-quarter to the tail light.  ~0.45 px/texel
#                 both ways, so w:h ~1.0 there.
# Decals are placed per island in raw texture px: (kind, cx, cy, w, aniso,
# rot) - w is the texture width, aniso = (px per texel across) / (px per
# texel down) for that island, so texture height = w * native_aspect * aniso
# and the mark keeps its shape on the car.
# the designer 2026-09-14 (second pass): ONLY Freak Farm on the quarters, same size
# and place both sides.  The right quarter's usable single island is the R
# rect's rows 2-3 next to the door (213 x 100 texels, ~100 x 40 screen px),
# so that sets the size; the left copy is placed to land on the same screen
# spot: just behind the door edge, top of the face.  Both ~100 x 33 px.
RQ_PLACE = [
    # car's LEFT (upright island): row 0 (y 1536..1602) is the shoulder TOP,
    # not visible from the side; the face is rows 1-3, y ~1620..1800
    # measured against the right (scratch\ffbox.py, level sides): first cut was
    # 24% smaller, 3% of car length too far forward and ~25 px too high
    ("ff",      1428, 1712, 217, 1.15, False),
    # car's RIGHT (rotated R island, rows 2-3 = raw y 700..800)
    ("ff",      1403,  750, 212, 1.17, True),
]


# --- 2026-09-14, third pass: SAME size and place both sides, bigger. ---------
# Each quarter island was probed with hue-coded cells and a texture->screen
# affine fitted from LEVEL side captures at one zoom (scratch\probeAff.py,
# fitAff.py; residuals 4 px).  The logo is then defined ONCE as a screen
# rectangle per side (same pixel size both sides, same fraction of the
# quarter: centre 45% from the door edge toward the light, 55% from the
# crease toward the arch) and every texel of the island is filled by
# inverse-mapping through the affine - no per-island guessing of scale,
# rotation or anisotropy, and text orientation comes out right by itself.
#   screen_x = a*u + b*v + c ;  screen_y = d*u + e*v + f      (u, v = texture)
RQ_AFFINE = {
    # car's RIGHT: (1297,600,355,200), rows 2-3 (v 700..800) are the visible band
    # (the island runs on above the rect's nominal top to v ~840 - probed
    # 2026-09-14 - so the rect is extended and the logo raised 12 px to sit
    # at the same height below the crease as the left one)
    "R": {"rect": (1297, 600, 355, 250), "A": ((-0.6581, 0.0925, 1130.52), (-0.0393, -0.5927, 924.65)),
          "logo": (222.0, 411.0, 175.0, 58.0)},          # screen cx, cy, w, h at the probe zoom
    # car's LEFT: (1280,1536,380,266), rows 1-3 (v ~1620..1800) are the face
    "U": {"rect": (1280, 1536, 380, 266), "A": ((0.5963, 0.1607, -74.20), (-0.0281, 0.4988, -408.27)),
          "logo": (1068.0, 401.0, 175.0, 58.0)},
}
RQ_USE_AFFINE = True


def rear_quarter_ff_affine(img, spec):
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    art = S(sponsors.logo_slot(LOGO2, 1200, ink=DESIGN.lettering,
                               accent=DESIGN.graphic)).convert("RGBA")
    ar = art.height / float(art.width)
    px = img.load()
    for side, M in RQ_AFFINE.items():
        x0, y0, w, h = M["rect"]
        (a, b, c), (d, e, f) = M["A"]
        cx, cy, lw, lh = M["logo"]
        lh = lw * ar                                  # keep the logo's own aspect on screen
        L = art.resize((int(lw * 4), int(lh * 4)), Image.LANCZOS)   # 4 samples per screen px
        Lpx = L.load()
        for v in range(y0, y0 + h):
            for u in range(x0, x0 + w):
                sx = a * u + b * v + c
                sy = d * u + e * v + f
                fx = (sx - (cx - lw / 2.0)) / lw
                fy = (sy - (cy - lh / 2.0)) / lh
                if 0.0 <= fx < 1.0 and 0.0 <= fy < 1.0:
                    r, g, bb, al = Lpx[int(fx * L.width), int(fy * L.height)]
                    if al:
                        base = px[u, v]
                        k = al / 255.0
                        px[u, v] = (int(r * k + base[0] * (1 - k)), int(g * k + base[1] * (1 - k)), int(bb * k + base[2] * (1 - k)))


def rear_quarter_decals(img, spec):
    if RQ_USE_AFFINE:
        return rear_quarter_ff_affine(img, spec)
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    for kind, cx, cy, w, aniso, rot in RQ_PLACE:
        if kind == "roundel":
            art = DESIGN.roundel(2 * w)
        elif kind == "ff":
            art = sponsors.logo_slot(LOGO2, 2 * w, ink=DESIGN.lettering, accent=DESIGN.graphic)
        else:
            art = sponsors.logo_slot(LOGO1, 2 * w, **DESIGN.logo_colours)
        art = S(art)
        h = max(1, int(round(w * (art.height / float(art.width)) * aniso)))
        el = art.resize((w, h), Image.LANCZOS)
        if rot:
            el = el.transpose(Image.ROTATE_180)
        img.paste(el, (int(round(cx - el.width / 2.0)), int(round(cy - el.height / 2.0))), el)


def build(spec=False):
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    band_col = T.SPEC_BAND if spec else BAND
    line_col = T.SPEC_LINE if spec else LINE
    acc_col = T.SPEC_LINE if spec else ACCENT
    img = Image.new("RGB", (W, H), T.SPEC_BODY if spec else BODY)

    # the sash goes down FIRST: the 404 panel and the marks sit in front of it
    draw_fender_stripes(img, spec)
    for left in (False, True):
        p = flank_panel(spec, left)
        r = FLANK_L if left else FLANK_R
        img.paste(p, (r[0], r[1]), p)
    # PROBED 2026-09-13: the rocker LIP under the door is the texture rows
    # just past each flank rect's sill edge - below FLANK_R (upright) and
    # ABOVE FLANK_L (it renders ROTATE_180, so raw low y is low on the car).
    # Left papaya it reads as an orange pinstripe under the black band.
    d = ImageDraw.Draw(img)
    d.rectangle([FLANK_R[0], FLANK_R[1] + FLANK_R[3],
                 FLANK_R[0] + FLANK_R[2] - 1, FLANK_R[1] + FLANK_R[3] + LIP],
                fill=band_col)
    d.rectangle([FLANK_L[0], FLANK_L[1] - LIP,
                 FLANK_L[0] + FLANK_L[2] - 1, FLANK_L[1] - 1], fill=band_col)
    rear_quarter_decals(img, spec)

    # --- hood: TEXT mark, ROTATE_180 then the panel's ROTATE_90 --------------
    hw, hh = HOOD[3], HOOD[2]
    hood = Image.new("RGBA", (hw, hh), (0, 0, 0, 0))
    # The full team badge, not the bare wordmark - the designer: the plain wordmark
    # "looks too plain" on the bonnet.  ROTATE_180 so its text reads from in
    # front of the car (car map: text mark on the hood).
    hd = ImageDraw.Draw(hood)
    hcx, hcy = hw // 2, hh // 2 + HOOD_WM_DY
    _vbands(hd, hcx, CS_HOOD, CS_HOOD_Y[0], CS_HOOD_Y[1], spec)
    _feeders(hood, hcx, hcy, spec)
    # the node: body-colour disc cuts the stripes, white ring, then the badge
    r_ring = HOOD_BADGE_D / 2.0 + RING_GAP + RING_W
    hd.ellipse([hcx - r_ring - RING_GAP, hcy - r_ring - RING_GAP,
                hcx + r_ring + RING_GAP, hcy + r_ring + RING_GAP],
               fill=tuple(T.SPEC_BODY if spec else BODY) + (255,))
    if DESIGN.lines_on:                    # the ring is one of the thin lines
        hd.ellipse([hcx - r_ring, hcy - r_ring, hcx + r_ring, hcy + r_ring],
                   fill=tuple(T.SPEC_LINE if spec else LINE) + (255,))
    r_in = HOOD_BADGE_D / 2.0 + RING_GAP
    hd.ellipse([hcx - r_in, hcy - r_in, hcx + r_in, hcy + r_in],
               fill=tuple(T.SPEC_BODY if spec else BODY) + (255,))
    hwm = S(DESIGN.roundel(HOOD_BADGE_D)).transpose(Image.ROTATE_180)
    hood.alpha_composite(hwm, (hw // 2 - hwm.width // 2,
                               hh // 2 - hwm.height // 2 + HOOD_WM_DY))
    hood = hood.transpose(Image.ROTATE_90)
    img.paste(hood, (HOOD[0], HOOD[1]), hood)

    # --- rear deck: Cats Don't Suck roundel.  the designer asked for it here.  The
    # panel renders ROTATE_180 and the visible boot is a diagonal band, so a
    # round mark is the only thing that survives (car map).  Centre of the
    # visible band, measured 2026-08-17.
    deck = Image.new("RGBA", (DECK[2], DECK[3]), (0, 0, 0, 0))
    _vbands(ImageDraw.Draw(deck), CS_DECK_X, CS_DECK, CS_DECK_Y[0], CS_DECK_Y[1], spec)
    cds = S(sponsors.logo_slot(LOGO1, DECK_CDS_D, **DESIGN.logo_colours))
    deck.alpha_composite(cds, (DECK_CDS_CXY[0] - cds.width // 2,
                               DECK_CDS_CXY[1] - cds.height // 2))
    img.paste(deck, (DECK[0], DECK[1]), deck)

    # --- nose / front fascia: the black band wraps the whole fascia ----------
    nx, ny, nw, nh = NOSE
    nose = Image.new("RGBA", (nw, nh), (0, 0, 0, 0))
    nd = ImageDraw.Draw(nose)
    _vbands(nd, CS_NOSE_X, CS_NOSE, CS_NOSE_ROWS[0], CS_NOSE_ROWS[1], spec)
    # No tow arrow on the nose: local (500,300) in this rect is the MIRROR
    # CAP, and the arrow rendered as "TOW" on the mirror.  Seen 2026-09-13.
    img.paste(nose, (nx, ny), nose)
    # the bumper's upper face and the lower lip continue the same columns
    _vbands(ImageDraw.Draw(img), nx + CS_NOSE_X, CS_NOSE, CS_BUMPER_TOP[0], CS_BUMPER_TOP[1], spec)
    _vbands(ImageDraw.Draw(img), nx + CS_NOSE_X, CS_NOSE, CS_LIP[0], CS_LIP[1], spec)

    # --- lower rear quarters continue BELOW the valance rect ------------------
    qd = ImageDraw.Draw(img)
    for x0, x1 in VAL_BELOW:
        qd.rectangle([x0, VALANCE[1] + VALANCE[3], x1 - 1, 512], fill=band_col)

    # --- rear valance: one band carries both quarters and the tail -----------
    vx, vy, vw, vh = VALANCE
    val = Image.new("RGBA", (vw, vh), (0, 0, 0, 0))
    vd = ImageDraw.Draw(val)
    _vbands(vd, CS_TAIL_X, CS_TAIL, 0, vh, spec, skip=CS_TAIL_SKIP)
    vwm = DESIGN.wordmark(int(VAL_WM_W * 0.17))
    vwm = vwm.resize((VAL_WM_W, int(vwm.height * VAL_WM_W / vwm.width)),
                     Image.LANCZOS)
    vwm = S(DESIGN.lettering_box(vwm, credit=False))   # the credit rides on the doors
    val.alpha_composite(vwm, (VAL_WM_CXY[0] - vwm.width // 2,
                              VAL_WM_CXY[1] - vwm.height // 2))
    chk = S(T.checker_rule(VAL_CHK_W, accent=DESIGN.graphic, dark=DESIGN.shade, line=DESIGN.trim))
    val.alpha_composite(chk, (VAL_CHK_CXY[0] - chk.width // 2,
                              VAL_CHK_CXY[1] - chk.height // 2))
    val.alpha_composite(S(sponsors.tow_arrow(92, color=DESIGN.graphic, ink=DESIGN.body)),
                        VAL_TOW)
    img.paste(val, (vx, vy), val)

    if spec:
        d = ImageDraw.Draw(img)
        for x, y, w, h in NUMBER_BLOCKS.values():
            d.rectangle([x, y, x + w - 1, y + h - 1], fill=T.SPEC_NUM)
    return img


def _near(img, rgb, tol=20):
    d = ImageChops.difference(img, Image.new("RGB", img.size, tuple(rgb)))
    r, g, b = d.split()
    m = ImageChops.lighter(ImageChops.lighter(r, g), b)
    return m.point(lambda v: 255 if v <= tol else 0).convert("1")


# --- spec map: "Option B - satin race finish" (the designer, 2026-09-14) -------------
# Channels per playbook Rule 8: R metallic (binary), G roughness (0 mirror ..
# 255 flat), B clearcoat INVERTED (16 = maximum shine).  Material by COLOUR of
# the colour map, nearest-colour classification so anti-aliased edges inherit
# the neighbour's material instead of falling through to a default:
#   body black   satin - a smooth sheen, not flat, not showroom gloss
#   papaya       the "pop": smoother than everything else; B2 adds metallic
#   white        crisp satin, a step glossier than the body, less than orange
#   anything else (logo faces, greys, the cat) semi-matte vinyl
#   number blocks plain gloss - the stamped number inherits it
SPEC_VARIANTS = {
    "B1": {"body": (0, 115, 16), "orange": (0, 45, 16),   "white": (0, 80, 16), "decal": (0, 95, 16), "num": (0, 40, 16)},
    "B2": {"body": (0, 115, 16), "orange": (255, 45, 16), "white": (0, 80, 16), "decal": (0, 95, 16), "num": (0, 40, 16)},
    # B3/B4 "Satin-True" (the designer 2026-09-14, second brief): the black is the quiet
    # background, white and papaya are the highlights.  Viewer ladder
    # (scratch\specladder*.cmd): in the viewer the CLEARCOAT channel is what
    # makes or kills the gleam - G barely shows - so the body's B goes to 200
    # (dull coat: soft broad sheen, no hotspot; 235 starts to grey the black,
    # 0 = coat off reads slightly dusty).  Orange keeps max coat and a smooth
    # surface so it catches the light; white a step behind it.  B4's metallic
    # orange goes darker / redder (metal darkens the albedo) but gets a
    # metallic flash - richer, less vivid.
    "B3": {"body": (0, 170, 200), "orange": (0, 35, 16),   "white": (0, 55, 30), "decal": (0, 120, 150), "num": (0, 60, 110)},
    "B4": {"body": (0, 170, 200), "orange": (255, 35, 16), "white": (0, 55, 30), "decal": (0, 120, 150), "num": (0, 60, 110)},
}
SPEC_DEFAULT = "B3"        # APPROVED 2026-09-14 ("Satin-True"); B1/B2/B4 are kept as history
SPEC_ORANGE_GROW = 3       # texels of orange-material halo around every papaya mark (see below)


# A LOCAL spec-map helper for designs (the Spec Racer Ford's): the number
# panels keep the car's own white finish (see spec_from_colour).  A no-op in
# the example scheme, so the ready-made spec map is untouched byte for byte.
def _panel_cover():
    """Every texel the two door number panels cover (NUM_PANEL, placed by
    flank_panel(): upright in FLANK_R, ROTATE_180 in FLANK_L)."""
    import numpy as np
    cov = np.zeros((H, W), dtype=bool)
    npx, npy, npw, nph = NUM_PANEL
    p = T.number_panel(npw, nph)
    for r, y, im in ((FLANK_R, npy, p), (FLANK_L, FH - npy - nph, p.transpose(Image.ROTATE_180))):
        a = np.asarray(im.getchannel("A")) > 0
        cov[r[1] + y:r[1] + y + a.shape[0], r[0] + npx:r[0] + npx + a.shape[1]] |= a
    return cov


def spec_from_colour(img, variant=SPEC_DEFAULT):
    import numpy as np
    P0 = SPEC_VARIANTS[variant]
    P = DESIGN.spec_values(P0)
    a = np.asarray(img.convert("RGB")).astype(np.int16)
    keys = DESIGN.material_keys(BODY, ACCENT)
    dist = np.stack([np.abs(a - np.array(c, dtype=np.int16)).sum(axis=2) for _, c in keys], axis=0)
    best = dist.argmin(axis=0)
    close = dist.min(axis=0) <= 200         # else: some other colour (the cat) -> vinyl
    out = np.empty(a.shape, dtype=np.uint8)
    out[...] = P["decal"]
    for i, (name, _) in enumerate(keys):
        out[(best == i) & close] = P[name]
    # The panels are T.WHITE, which material_keys sorts into the "white" slot
    # that a design's trim finish replaces: a chrome or matte trim would rim
    # every number.  Put the panel texels back to the car's own white finish
    # (what the example gives them, so a no-op there).
    panel_white = np.array([tuple(c) == tuple(T.WHITE) for _, c in keys])[best] & close
    out[_panel_cover() & panel_white] = P0["white"]
    # Small orange marks (the A-bar, the dots, "RACING") are a few texels
    # wide; the sim's texture filtering averages their glossy material with
    # the matte black around them and they read flat (the designer, 2026-09-14).
    # Give every papaya pixel a SPEC_ORANGE_GROW-texel halo of the orange
    # material, and count any pixel with a papaya component (anti-aliased
    # edges of the marks) as orange too.  On the stripes the halo lands on
    # the white (also glossy) and a 3-texel rim of the black - invisible.
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
    # The small marks can carry their own material ("orange_small"): the
    # stripes are the big connected orange areas (survive an 8-texel erosion),
    # everything orange that does not is a logo mark.
    if "orange_small" in P:
        def _erode(b, r):
            pad = np.pad(b, r, constant_values=False); acc2 = np.ones_like(b)
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if dx * dx + dy * dy <= r * r:
                        acc2 &= pad[r + dy:r + dy + b.shape[0], r + dx:r + dx + b.shape[1]]
            return acc2
        def _dilate(b, r):
            pad = np.pad(b, r, constant_values=False); acc2 = np.zeros_like(b)
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if dx * dx + dy * dy <= r * r:
                        acc2 |= pad[r + dy:r + dy + b.shape[0], r + dx:r + dx + b.shape[1]]
            return acc2
        big = _dilate(_erode(orange_ish, 8), 8 + g + 2)
        out[m & ~big] = P["orange_small"]
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
    ap.add_argument("--spec-variant", default=SPEC_DEFAULT, choices=sorted(SPEC_VARIANTS),
                    help="which finish goes in car_spec_<id>.tga (default %s, the approved one)" % SPEC_DEFAULT)
    ap.add_argument("--finish-tests", action="store_true",
                    help="also write the four test finishes as car_spec_<id>_B1.tga .. _B4.tga, to compare them")
    personalize.add_args(ap)
    args = ap.parse_args()
    args.debug = False
    cfg = personalize.resolve(args)
    apply_design(cfg.design)
    CUSTOMER = cfg.id
    DRIVER_NAME = cfg.driver
    LOGO1, LOGO2 = cfg.logo1, cfg.logo2
    out_dir = cfg.out_dir or (os.getcwd() if args.here else personalize.default_out_dir())
    os.makedirs(out_dir, exist_ok=True)
    colour = build(spec=False)
    if args.debug:
        print("DEBUG BUILD - magenta centre line - do not lock")
    print("number blocks:")
    bad = check_number_blocks(colour)
    if bad and not args.debug:
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
    if args.no_spec and args.finish_tests:
        print("note: --finish-tests does nothing with --no-spec; no finish files written")
    if not args.no_spec:
        if args.finish_tests:       # the development test finishes, only when asked
            for v in sorted(SPEC_VARIANTS):
                sv = os.path.join(out_dir, "car_spec_%s_%s.tga" % (CUSTOMER, v))
                spec_from_colour(colour, v).save(sv, compression="tga_rle")
                print("wrote", sv)
        s = os.path.join(out_dir, "car_spec_%s.tga" % CUSTOMER)
        spec_from_colour(colour, args.spec_variant).save(s, compression="tga_rle")
        with open(s, "rb") as fh:
            head = fh.read(18)
        assert head[2] == 10 and head[16] == 24, "bad spec TGA header: %r" % head[:18]
        print("wrote", s, "(variant %s, RLE 24-bit, header verified)" % args.spec_variant)
