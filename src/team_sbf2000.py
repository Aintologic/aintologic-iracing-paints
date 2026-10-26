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

"""TEAM SCHEME - Skip Barber Formula 2000 (#1).  Ninth car.  v1.0 LOCKED 2026-10-08.

APPROVED by the designer on the render 2026-10-08, as first shown; frozen as
releases/skip-barber-formula-2000/v1.0-2026-10-08-claude/ (tag
skip-barber-formula-2000/v1.0-2026-10-08-claude).  Any pixel change is a v1.1.

The AINTOLOGIC team livery
(docs/PAINT-SCHEME.md) on the Skip Barber's panel map
(docs/car-maps/skip-barber-formula-2000.md).  Marks come from
src/teamscheme.py and src/sponsors.py; this file holds ONLY this car's
geometry and placements.  Nothing here is inherited from another car - every
constant was measured on this car (probes 2026-10-08).

    python src/team_sbf2000.py            -> out/ in the project folder
    python src/team_sbf2000.py --here     -> the cwd instead
    python src/team_sbf2000.py --no-spec  -> colour map only

Writes car_<id>.tga (+ car_spec_<id>.tga); see src/personalize.py for
--id / --driver / --logo1 / --logo2 / --out / --profile / --design, and
src/design.py for a design's colours, team name and stripe style.

Car #1 (Car Info 2026-10-08: "Car Info: Skip Barber Formula 2000", #1);
template 1_template_SBRS.zip
("Formula Skip Barber 2000.psd", 2048x2048); paint folder
%USERPROFILE%\\Documents\\iRacing\\paint\\rt2000.

THE RULE OF THIS UV (measured 2026-10-08):
  * Side islands mirror about texture row 1347.5 - right y = 2695 - left y,
    x identical (mask correlation: 9/8 100.0 %, 29/27, 31/30, 33/32, 37/40,
    38/39, 59/60 at 2694-2696).  Rows > 1347 are the car's LEFT side and read
    UPRIGHT from a level left view; rows < 1347 are the RIGHT side and read
    ROTATE_180.  On BOTH sides texture +x is REARWARD (coordinate grid).
  * The CENTRE islands (nose tip 47, nose top 3, latch plate 96, scuttle /
    cockpit surround 6, engine-cover spine 17, tail 18) are each symmetric
    about row 1345.5 (2691) - two texels off the side mirror.  Centre marks
    use CENTRE, side marks use MIRROR.
  * The engine-cover side panels (15 left, 16 right) are packed outside the
    main mirror and mirror each other locally: right y = 398 - left y.
  * Leaky islands (green outline open, so not in the island list): the nose
    sides ahead of x 511, the LEFT lower front flank (rows ~1697..1865) and the
    RIGHT sidepod face (rows ~663..863).  The mirror still paints them.
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
import setup_check
setup_check.require("sbf2000")

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUSTOMER = personalize.DEFAULT_ID
PAINT_DIR = iracingpaths.paint_folder("rt2000")
# personalization, set from the CLI/profile in __main__ before build() runs:
DRIVER_NAME = ""                       # blank driver strip by default
LOGO1 = sponsors.placeholder_logo      # Cats Don't Suck slot
LOGO2 = sponsors.placeholder_logo      # FreakFarm slot
DESIGN = design.EXAMPLE                # your own design (--design); apply_design() sets it
W = H = 2048
MIRROR = 2695                         # side islands: right y = MIRROR - left y
CENTRE = 2691 / 2.0                   # 1345.5, centre islands' own symmetry row
CENTRE_MASK = os.path.join(_ROOT, "assets", "sbf2000-centre-mask.png")  # 47 3 96 6 17 18
POD_IDS = os.path.join(_ROOT, "assets", "sbf2000-pod-islands.png")      # 8 = pod top, 5 = pod face

# Template "Number Blocks" layer, three blocks; all three stamp (magenta probe
# 2026-10-08): N1 / N2 on the rear-wing endplate OUTER faces (left / right),
# N3 on the nose top, reading from the front.
NUMBER_BLOCKS = {
    "N1": (436, 299, 123, 87),        # island 24, LEFT endplate outer face
    "N2": (864, 299, 123, 87),        # island 25, RIGHT endplate outer face
    "N3": (333, 1278, 98, 135),       # island 3, nose top, on the centre line
}

BODY, LINE, ACCENT = T.BLACK, T.WHITE, T.PAPAYA
NUM_MARGIN = 8


def apply_design(ds):
    """Build with design ds (src/design.py): its colours, lettering and stripe
    style.  The names here predate it: LINE is the design's trim (the thin
    lines and the node ring), ACCENT its graphic colour (the wide stripe)."""
    global DESIGN, BODY, LINE, ACCENT
    DESIGN = ds
    BODY, LINE, ACCENT = ds.body, ds.trim, ds.graphic

# =============================================================================
# PLACEMENTS - APPROVED and locked v1.0 2026-10-08.  Comments name what the
# earlier passes on the render did and why it changed.
# Side placements are in LEFT texture coordinates (y > 1347).
# Band recipe everywhere: orange = 2x white, small body-colour gaps.
# -----------------------------------------------------------------------------
# Centre stripes on the nose: tip (island 47, pointed at x 22) -> nose top
# (island 3) up to the nose number panel; resume behind it to the AI roundel
# node on the scuttle (island 6) just ahead of the cockpit (rim at x ~920).
# A chrome nose latch stands on the centre line over island 96 (x 671..749;
# 3D, over the paint) - the stripe runs under it and the node sits behind it.
STRIPE_CS = (36, 18, 6)               # orange, white, gap
NOSE_TIP_X, NOSE_TAPER_X = 22, 200    # tip island narrower than the band set;
                                      # a long linear taper reads smoother than
                                      # one that only clears the tip (v1: 104)
NUM_GAP = 12                          # body gap either side of the nose panel
NODE_BADGE_D, NODE_CX = 92, 822       # v1/v2 100 @ 790: the latch (its plate is
RING_GAP, RING_W = 5, 10              # island 96, x 671..749) sat on the ring
COCKPIT_X = 916                       # stop short of the cockpit rim

# Engine cover: the spine (island 17) runs behind the roll hoop and its filler
# cap (island 93, x 1427..1471) and TAPERS from 219 rows at x 1480 to 38 at
# x 1830; then the tail cover (18, ~240 rows) up to its three centre vent slots
# (x 1926..2002 - a gap, not painted through).  The stripes shrink to stay
# inside the spine and carry the spine's end width down the tail: ONE tapering
# stripe from the hoop to the vents.  (v1 ran the tail at full width and the
# step at the spine / tail joint read as broken blocks from behind - rejected.)
COVER_RUN = (1480, 1831)
TAIL_RUN = (1834, 1918)
SPINE_HW = [(1480, 109.5), (1505, 104.5), (1530, 97.0), (1555, 86.5),
            (1580, 75.0), (1605, 63.0), (1630, 53.5), (1655, 45.5),
            (1680, 38.5), (1705, 33.5), (1730, 29.5), (1755, 26.5),
            (1780, 23.5), (1805, 20.5), (1831, 19.0)]
SPINE_MARGIN = 5
SPINE_MIN = 0.4                       # never thinner than 0.4 x the band set

# Sidepod sash (LEFT space): white | papaya | white across the pod's leading
# edge, wrapping from the pod TOP (island 8, rows 1676 inboard .. ~1812 outer
# edge) down the pod FACE (island 5, rows ~1833 .. 2032).  Both islands share
# texture x (X-band probe: bands line up across the seam).  Leaning
# top-forward / bottom-rearward.  The unmapped seam between them (~21 rows)
# is skipped, so the lean is continuous on the car.
SASH_X = 1222                         # band centre at the face's top row
SASH_TILT = 0.28                      # x per row (+x rearward, +y outward / down)
SASH_TOP_REF, SASH_FACE_REF = 1812, 1835
SASH_BANDS = (40, 20, 6)

# AINTOLOGIC on the tub flank above the sidepod (island 2 left / 0 right),
# beside and behind the cockpit; the flank is a clean vertical panel from the
# cockpit rim (~1530) down to the pod top (1665).
FLANK_WM_W, FLANK_WM_CXY = 380, (1352, 1578)   # v1 440 @ (1388, 1601): its lower
                                      # third hid behind the pod top's rounded
                                      # inboard edge (visible flank ends ~1625)
# The mirror stalk comes down onto the flank at x ~965..980, row ~1585 (both
# sides): the driver strip sits AHEAD of it, the cutoff + extinguisher marks
# behind it.  (v3 had the strip at x 928 and the stalk crossed the driver name.)
DRIVER_W, DRIVER_XY = 118, (818, 1560)
CUTOFF_H, CUTOFF_XY = 26, (996, 1559)
EXT_D, EXT_XY = 26, (1034, 1559)

# FreakFarm on the sidepod face behind the sash, in the lower part of the face
# (a groove crosses the face's rear half at rows ~1885..1915 from x ~1400).
FF_W, FF_CXY = 250, (1470, 1972)

# Cats Don't Suck on the sidepod TOP, aft of the sash - reads from above and
# every 3/4.  (The rear-wing endplates are filled by the number blocks.)
CDS_D, CDS_CXY = 100, (1528, 1744)


# =============================================================================
def specify(im, rgb=T.SPEC_DECAL):
    out = Image.new("RGBA", im.size, tuple(rgb) + (255,))
    out.putalpha(im.getchannel("A"))
    return out


def _col(c, spec):
    return tuple(T.SPEC_LINE if spec else c) + (255,)


def _band_rects(cx, widths, s=1.0):
    """white | papaya | white about cx, orange = 2x white, small gaps; s scales.
    The design's stripe style keeps the bands it draws (classic: all three);
    the ones it keeps stay exactly where they were measured."""
    ow, ww, g = (v * s for v in widths)
    return DESIGN.bands([(cx - ow / 2.0 - g - ww, cx - ow / 2.0 - g, LINE),
                         (cx - ow / 2.0, cx + ow / 2.0, ACCENT),
                         (cx + ow / 2.0 + g, cx + ow / 2.0 + g + ww, LINE)])


def _half(widths):
    ow, ww, g = widths
    return ow / 2.0 + g + ww


def _mask(path):
    return np.asarray(Image.open(path).convert("L")) > 127


def masked(layer, path):
    a = np.array(layer)
    a[..., 3] = np.where(_mask(path), a[..., 3], 0)
    return Image.fromarray(a, "RGBA")


def mirror_left(layer):
    """Copy every LEFT-half texel (y > 1347) of `layer` onto the right half
    (y' = MIRROR - y), leaving the left half as it is."""
    a = np.array(layer)
    out = a.copy()
    y0 = MIRROR // 2 + 1                           # 1348
    for y in range(y0, H):
        yy = MIRROR - y
        if 0 <= yy < H:
            take = a[y, :, 3] > 0
            out[yy, take] = a[y, take]
    return Image.fromarray(out, "RGBA")


def place(img, el, x, y, left):
    """TEXT / any upright mark.  (x, y) = top-left in LEFT texture space.
    The right side renders ROTATE_180, so the element rotated 180 and dropped
    at the mirrored rows lands upright, the same distance from the nose
    (playbook Rule 4)."""
    if left:
        img.alpha_composite(el, (x, y))
    else:
        img.alpha_composite(el.transpose(Image.ROTATE_180),
                            (x, MIRROR - y - el.height + 1))


# --- side geometry -------------------------------------------------------------
def pod_sash(spec):
    """The sidepod sash, drawn in LEFT space on the pod top + face, mirrored."""
    K = 3
    big = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    ids = np.asarray(Image.open(POD_IDS))
    layers = []
    for isl, (y0, y1), xc in (
            (8, (1670, 1822), lambda y: SASH_X - SASH_TILT * (SASH_TOP_REF - y)),
            (5, (1826, 2040), lambda y: SASH_X + SASH_TILT * (y - SASH_FACE_REF))):
        big.paste((0, 0, 0, 0), (0, 0, W * K, H * K))
        for a, b, c in _band_rects(0, SASH_BANDS):
            d.polygon([((xc(y0) + a) * K, y0 * K), ((xc(y1) + a) * K, y1 * K),
                       ((xc(y1) + b) * K, y1 * K), ((xc(y0) + b) * K, y0 * K)],
                      fill=_col(c, spec))
        lay = np.array(big.resize((W, H), Image.LANCZOS))
        lay[..., 3] = np.where(ids == isl, lay[..., 3], 0)
        layers.append(lay)
    out = layers[0]
    take = layers[1][..., 3] > 0
    out[take] = layers[1][take]
    return mirror_left(Image.fromarray(out, "RGBA"))


def side_text(img, spec):
    """AINTOLOGIC + driver strip + safety marks on the tub flank, FreakFarm on
    the pod face, the cat on the pod top - both sides (place()).  With a team
    name, the name goes in the wordmark's box with the small "made with
    AINTOLOGIC" credit under it: the flank is this car's main lettering.  The
    cutoff triangle and extinguisher mark keep their conventional safety
    colours (red / blue / white, white disc with a black E) in every design."""
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    wm = DESIGN.wordmark(int(FLANK_WM_W * 0.2))
    wm = wm.resize((FLANK_WM_W, int(wm.height * FLANK_WM_W / wm.width)), Image.LANCZOS)
    wm = S(DESIGN.lettering_box(wm))     # your team name in the same box, if you gave one
    ds = S(sponsors.driver_strip(DRIVER_W, DRIVER_NAME, face=DESIGN.body,
                                 ink=DESIGN.lettering, accent=DESIGN.graphic))
    cut = S(sponsors.cutoff_triangle(CUTOFF_H, spark=T.WHITE, edge=T.WHITE))
    ext = S(sponsors.extinguisher_mark(EXT_D, face=T.WHITE, ink=T.BLACK))
    ff = S(sponsors.logo_slot(LOGO2, FF_W, ink=DESIGN.lettering, accent=DESIGN.graphic))
    cat = S(sponsors.logo_slot(LOGO1, CDS_D, **DESIGN.logo_colours))
    for left in (True, False):
        place(img, wm, FLANK_WM_CXY[0] - wm.width // 2, FLANK_WM_CXY[1] - wm.height // 2, left)
        place(img, ds, DRIVER_XY[0], DRIVER_XY[1], left)
        place(img, cut, CUTOFF_XY[0], CUTOFF_XY[1], left)
        place(img, ext, EXT_XY[0], EXT_XY[1], left)
        place(img, ff, FF_CXY[0] - ff.width // 2, FF_CXY[1] - ff.height // 2, left)
        place(img, cat, CDS_CXY[0] - cat.width // 2, CDS_CXY[1] - cat.height // 2, left)


# --- centre line ---------------------------------------------------------------
def _spine_scale(x):
    xs, hw = zip(*SPINE_HW)
    h = float(np.interp(x, xs, hw)) - SPINE_MARGIN
    return min(1.0, max(SPINE_MIN, h / _half(STRIPE_CS)))


def _stripe_cols(a, x0, x1, spec, scale=lambda x: 1.0, K=4):
    """Paint the band set column by column (supersampled K x K) into the
    RGBA array `a`, centred on CENTRE, scaled per column by scale(x)."""
    sub = (np.arange(K) + 0.5) / K
    lo = int(np.floor(CENTRE - _half(STRIPE_CS))) - 1
    hi = int(np.ceil(CENTRE + _half(STRIPE_CS))) + 1
    yf = (np.arange(lo, hi + 1)[:, None] + sub[None, :]).ravel()   # rows x K
    for x in range(x0, x1):
        acc = np.zeros((len(yf), 3))
        cov = np.zeros(len(yf))
        for sx in sub:
            for p, q, c in _band_rects(CENTRE, STRIPE_CS, scale(x + sx)):
                m = (yf >= p) & (yf < q)
                acc[m] += np.array(T.SPEC_LINE if spec else c, float)
                cov[m] += 1
        acc = acc.reshape(-1, K, 3).sum(axis=1)
        cov = cov.reshape(-1, K).sum(axis=1)
        rows = np.where(cov > 0)[0]
        a[lo + rows, x, :3] = np.clip(acc[rows] / cov[rows, None], 0, 255).astype(np.uint8)
        a[lo + rows, x, 3] = np.round(255.0 * cov[rows] / (K * K)).astype(np.uint8)


def centre_line(img, spec):
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    a = np.zeros((H, W, 4), np.uint8)
    bx, by, bw, bh = NUMBER_BLOCKS["N3"]
    px0, px1 = bx - NUM_MARGIN, bx + bw + NUM_MARGIN
    tip = lambda x: min(1.0, 0.35 + 0.65 * max(0.0, x - NOSE_TIP_X) / float(NOSE_TAPER_X - NOSE_TIP_X))
    _stripe_cols(a, NOSE_TIP_X, px0 - NUM_GAP, spec, tip)
    r_in = NODE_BADGE_D / 2.0 + RING_GAP
    r_ring = r_in + RING_W
    _stripe_cols(a, px1 + NUM_GAP, int(NODE_CX - r_ring - RING_GAP), spec)
    _stripe_cols(a, int(np.ceil(NODE_CX + r_ring + RING_GAP)), COCKPIT_X, spec)
    _stripe_cols(a, COVER_RUN[0], COVER_RUN[1], spec, _spine_scale)
    end = _spine_scale(COVER_RUN[1])
    _stripe_cols(a, TAIL_RUN[0], TAIL_RUN[1], spec, lambda x: end)
    img.alpha_composite(masked(Image.fromarray(a, "RGBA"), CENTRE_MASK))
    # the node: body-colour gap, white ring, body-colour gap, the roundel
    cx, cy = NODE_CX, CENTRE
    K = 4
    big = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0))
    bd = ImageDraw.Draw(big)
    if DESIGN.lines_on:                  # the ring is one of the thin lines
        bd.ellipse([(cx - r_ring) * K, (cy - r_ring) * K, (cx + r_ring) * K,
                    (cy + r_ring) * K], fill=_col(LINE, spec))
    bd.ellipse([(cx - r_in) * K, (cy - r_in) * K, (cx + r_in) * K,
                (cy + r_in) * K], fill=tuple(T.SPEC_BODY if spec else BODY) + (255,))
    img.alpha_composite(big.resize((W, H), Image.LANCZOS))
    # letters read from the FRONT of the car: image-up -> texture +x (rearward).
    # The example badge, or your colours / initials (src/design.py).
    badge = S(DESIGN.roundel(NODE_BADGE_D)).transpose(Image.ROTATE_270)
    img.alpha_composite(badge, (int(round(cx - badge.width / 2.0)),
                                int(round(cy - badge.height / 2.0))))


def number_panels(img, spec):
    m = NUM_MARGIN
    for bx, by, bw, bh in NUMBER_BLOCKS.values():
        p = T.number_panel(bw + 2 * m, bh + 2 * m, fill=(T.SPEC_NUM if spec else T.WHITE))
        img.alpha_composite(p, (bx - m, by - m))


def build(spec=False):
    img = Image.new("RGBA", (W, H), tuple(T.SPEC_BODY if spec else BODY) + (255,))
    img.alpha_composite(pod_sash(spec))
    centre_line(img, spec)
    side_text(img, spec)
    number_panels(img, spec)
    img = img.convert("RGB")
    if spec:
        d = ImageDraw.Draw(img)
        for x, y, w, h in NUMBER_BLOCKS.values():
            d.rectangle([x, y, x + w - 1, y + h - 1], fill=T.SPEC_NUM)
    return img


def check_number_blocks(img):
    """A block may be base colour or the flat white number panel only."""
    a = np.asarray(img.convert("RGB")).astype(int)
    bad = []
    for name, (x, y, w, h) in NUMBER_BLOCKS.items():
        blk = a[y:y + h, x:x + w]
        dist = np.min([np.abs(blk - np.array(c)).sum(axis=2) for c in (BODY, T.WHITE)], axis=0)
        off = int((dist > 6).sum())
        print("  %s %s %d bad / %d px" % (name, "DIRTY" if off else "clean", off, w * h))
        if off:
            bad.append(name)
    return bad


# --- spec map: the approved "Satin-True" (B3) hierarchy, carried over.
# Not A/B-validated on this car; accepted at the v1.0 lock.
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
    """Every texel the white number panels cover (number_panels() geometry)."""
    cov = np.zeros((H, W), dtype=bool)
    m = NUM_MARGIN
    for bx, by, bw, bh in NUMBER_BLOCKS.values():
        p = np.asarray(T.number_panel(bw + 2 * m, bh + 2 * m).getchannel("A")) > 0
        cov[by - m:by - m + p.shape[0], bx - m:bx - m + p.shape[1]] |= p
    return cov


def spec_from_colour(img, variant=SPEC_DEFAULT):
    """The design's finishes (src/design.py) swapped into the B3 table where
    the settings file names them: body, graphic ("orange": the wide stripe
    and everything in the graphic colour), trim ("white": the thin lines,
    the node ring and the lettering).  The number panels keep the car's own
    B3 white in every design."""
    P0 = SPEC_VARIANTS[variant]
    P = DESIGN.spec_values(P0)
    a = np.asarray(img.convert("RGB")).astype(np.int16)
    keys = DESIGN.material_keys(BODY, ACCENT)
    dist = np.stack([np.abs(a - np.array(c, dtype=np.int16)).sum(axis=2)
                     for _, c in keys], axis=0)
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
    m = DESIGN.stripe_mask(a)          # papaya's hue test in the example scheme
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
