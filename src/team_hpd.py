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

"""TEAM SCHEME - HPD ARX-01c (#39).  Seventh car.  v1.0 LOCKED 2026-09-17.

APPROVED by the designer 2026-09-17; frozen as releases/hpd-arx-01c/v1.0-2026-09-17/
(tag hpd-arx-01c/v1.0-2026-09-17).  The SPORTS-PROTOTYPE adaptation.  Any pixel
change is a v1.1, never an edit of v1.0.  To edit it later start at
docs/car-maps/hpd-arx-01c.md, "How to edit this car later".

REBUILT FROM SCRATCH 2026-09-17.  An earlier attempt on this car was rejected
and is abandoned: its placements were "on the UV" but wrong on the render.
Nothing here is inherited from it - every constant below was measured again on
this car, and no MX-5 / F4 / RSR / Ray / Ferrari / Lotus coordinate is reused.

The AINTOLOGIC team livery (docs/PAINT-SCHEME.md) on the HPD's panel map
(docs/car-maps/hpd-arx-01c.md).  Marks come from src/teamscheme.py and
src/sponsors.py; this file holds ONLY the HPD's geometry and placements.

    python src/team_hpd.py            -> out/ in the project folder
    python src/team_hpd.py --here     -> the cwd instead
    python src/team_hpd.py --no-spec  -> colour map only

Writes car_<id>.tga (+ car_spec_<id>.tga); see src/personalize.py for
--id / --driver / --logo1 / --logo2 / --out / --profile.

Car #39; template 39_template_ARX.zip
("Honda Performance Development ARX01C.psd", 2048x2048); paint folder
%USERPROFILE%\\Documents\\iRacing\\paint\\hpdarx01c (created by the sim).

THE RULE OF THIS UV (measured 2026-09-17, mask correlation on three island
pairs at 99.8-99.9 %):  the BODY is mirror-symmetric about texture row 1197 -
right y = 2394 - left y, x identical.  Rows > 1197 are the car's LEFT side and
render UPRIGHT from a level left view; rows < 1197 are the RIGHT side and
render ROTATE_180.  **On BOTH sides texture +x is REARWARD** (proved from the
coordinate-grid probe: the left flank reads 9,12 -> 10,12 -> 11,12 nose to
tail upright, the right flank reads the same sequence upside down).

Only islands 0 (front body) and 1 (rear/side body) obey that mirror.  The
engine-cover flanks, the wing, the endplates and the splitter are packed
independently and get PER-SIDE coordinates - see docs/car-maps/hpd-arx-01c.md.
assets/hpd-body-mask.png is islands 0+1, and it masks the mirrored layer so
side geometry cannot bleed onto those independent islands.
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
import teamscheme as T
import sponsors
import personalize
import setup_check
setup_check.require("hpd")

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUSTOMER = personalize.DEFAULT_ID
PAINT_DIR = os.path.join(os.path.expanduser("~"), "Documents", "iRacing",
                         "paint", "hpdarx01c")
# personalization, set from the CLI/profile in __main__ before build() runs:
DRIVER_NAME = ""                       # blank driver strip by default
LOGO1 = sponsors.placeholder_logo      # Cats Don't Suck slot
LOGO2 = sponsors.placeholder_logo      # FreakFarm slot
W = H = 2048
MIRROR = 2394                         # right y = MIRROR - left y
CENTRE = MIRROR // 2                  # 1197, the car's centre line in texture
BODY_MASK = os.path.join(_ROOT, "assets", "hpd-body-mask.png")

# --- template anchor blocks (PSD "Number Blocks"), measured 2026-09-17 -------
NUMBER_BLOCKS = {"N1": (442, 408, 100, 52),     # RIGHT side, ahead of the pod
                 "N2": (232, 610, 52, 100),     # portrait, front of the car
                 "N3": (442, 1934, 100, 52)}    # LEFT side (mirror of N1)

BODY, LINE, ACCENT = T.BLACK, T.WHITE, T.PAPAYA
NUM_MARGIN = 10

# =============================================================================
# PLACEMENTS - APPROVED and locked v1.0 2026-09-17 (issue #6).
# Side placements are in LEFT texture coordinates (y > 1197).
# Band recipe everywhere: orange = 2x white, small body-colour gaps.
# -----------------------------------------------------------------------------
# Centre stripes.  Island 0 carries the nose from its tip (x ~40) back to the
# cockpit scuttle; island 1 picks the line up on the engine cover behind the
# roll hoop and runs it to the tail.  Row 1197 is the car's centre line.
NOSE_X = (46, 700)
NOSE_CS = (46, 23, 7)                 # orange, white, gap (texels)
COVER_X = (1180, 2010)
COVER_CS = (40, 20, 6)
COVER_SKIP = [(1330, 1470)]           # the airbox mouth - a gap, not painted through

# The AI roundel node on the nose top; the centre stripes enter and leave it.
NOSE_BADGE_D, NOSE_BADGE_CX = 168, 330
RING_GAP, RING_W = 7, 14

# Front-fender sash (LEFT texture space), leaning top-forward.  Island 0's
# left front fender crown wraps down the fender's outer face over these rows.
SASH_XC, SASH_TILT = 430, 0.30
SASH_BANDS = (54, 27, 8)              # orange, white, gap
SASH_Y = (1520, 1815)

# AINTOLOGIC on the sidepod flank - the car's biggest side-facing surface.
# v1 ran off the back of the panel into the rear arch on BOTH sides (the
# mirror is fine; the box was simply too long and too low).  v2: shorter,
# further forward, higher.
FLANK_WM_W, FLANK_WM_CXY = 455, (1310, 1520)
FLANK_DRIVER_W, FLANK_DRIVER_XY = 150, (1040, 1440)

# Sash on the vertical panel ahead of the sidepod - islands 6 (R) / 7 (L),
# which carry the flank number block and ARE true mirrors, so this is drawn
# in LEFT space and mirrored with everything else.
POD_SASH_XC, POD_SASH_TILT = 615, 0.34
POD_SASH_BANDS = (46, 23, 7)
POD_SASH_Y = (1700, 2020)

# FreakFarm: the engine-cover TOP shoulder, just outboard of the centre
# stripes, on island 1 - so it mirrors cleanly and reads from above and from
# every 3/4.  TRIED AND REJECTED 2026-09-17: the engine-cover FLANK (islands
# 4 and 5).  Those two islands are not mirrors of each other, they take
# opposite rotations, and from a LEVEL side the mark is swallowed by the rear
# wheel and the pod shoulder - it only ever read from a rear 3/4.
FF_W, FF_CXY = 330, (1470, 1352)

# Rear wing (island 3) and the endplates.  The left endplate outer face is its
# own island (11); the right one is packed inside the wing island.
# The two endplate OUTER faces are different islands, different sizes, and
# each island also carries the INNER face next to it - measured 2026-09-17
# from labelled grids read on a level left and a level right view:
#   island 11 = LEFT endplate;  x 1818..1929 inner, 1929..2040 OUTER
#   island  3 = wing + RIGHT endplate;  x 530..660 OUTER, 660..790 inner
# Both outer faces take UPRIGHT artwork.  v1 centred the cat on the island
# instead of on the outer face, so half of it landed on the inner face.
CDS_L_D, CDS_L_CXY = 96, (1984, 1928)
CDS_R_D, CDS_R_CXY = 112, (595, 96)

# The wing's main plane is island 3 x 14..525 (span) unwrapped in three
# chordwise bands, measured with a 1x3 chord probe read from a DEAD REAR and a
# top-down frame (2026-09-17):
#   y   9..96  leading edge / underside
#   y  96..183 TOP surface        <- the wordmark
#   y 183..270 TRAILING / REAR face  <- renders as a ~2 px edge, unusable
# The wordmark on the top surface reads from ABOVE and from every high rear
# 3/4; letter tops point rearward so it also reads the right way up from behind.
WING_WM_W, WING_WM_CXY = 430, (270, 139)


# =============================================================================
def specify(im, rgb=T.SPEC_DECAL):
    out = Image.new("RGBA", im.size, tuple(rgb) + (255,))
    out.putalpha(im.getchannel("A"))
    return out


def _col(c, spec):
    return tuple(T.SPEC_LINE if spec else c) + (255,)


def _band_rects(cx, widths):
    """white | papaya | white about cx, orange = 2x white, small gaps."""
    ow, ww, g = widths
    return [(cx - ow / 2.0 - g - ww, cx - ow / 2.0 - g, LINE),
            (cx - ow / 2.0, cx + ow / 2.0, ACCENT),
            (cx + ow / 2.0 + g, cx + ow / 2.0 + g + ww, LINE)]


def place(img, el, x, y, left):
    """TEXT / any upright mark.  (x, y) = top-left in LEFT texture space.

    The right side renders ROTATE_180, so the same element rotated 180 and
    dropped at the mirrored row lands upright, the same distance from the
    nose (playbook Rule 4)."""
    if left:
        img.alpha_composite(el, (x, y))
    else:
        img.alpha_composite(el.transpose(Image.ROTATE_180),
                            (x, MIRROR - y - el.height))


def _body_mask():
    return Image.open(BODY_MASK).convert("L")


def mirror_geometry(layer):
    """Copy the LEFT half of `layer` onto the RIGHT half about row MIRROR,
    masked to islands 0+1 so nothing lands on an independently packed island."""
    a = np.array(layer)
    out = a.copy()
    src = a[CENTRE + 1:, :]                      # rows 1198..2047
    flip = src[::-1]                             # row y -> MIRROR - y
    d0 = MIRROR - (H - 1)                        # = 347
    dst = out[d0:d0 + flip.shape[0], :]
    take = flip[..., 3] > 0
    dst[take] = flip[take]
    m = np.asarray(_body_mask()) > 127
    out[..., 3] = np.where(m, out[..., 3], 0)
    return Image.fromarray(out, "RGBA")


def draw_sash(d, spec, k=1):
    """Front-fender sash, LEFT texture space.  Leans top-forward: xc grows
    with y, and on this UV +y is outboard/down the fender, +x is rearward."""
    y0, y1 = SASH_Y
    for a, b, c in _band_rects(0, SASH_BANDS):
        xa0 = SASH_XC + a
        xa1 = SASH_XC + SASH_TILT * (y1 - y0) + a
        xb0 = SASH_XC + b
        xb1 = SASH_XC + SASH_TILT * (y1 - y0) + b
        d.polygon([(xa0 * k, y0 * k), (xa1 * k, y1 * k),
                   (xb1 * k, y1 * k), (xb0 * k, y0 * k)], fill=_col(c, spec))


def draw_pod_sash(d, spec, k=1):
    """Sash on the panel ahead of the sidepod, LEFT texture space."""
    y0, y1 = POD_SASH_Y
    for a, b, c in _band_rects(0, POD_SASH_BANDS):
        xa0 = POD_SASH_XC + a
        xa1 = POD_SASH_XC + POD_SASH_TILT * (y1 - y0) + a
        xb0 = POD_SASH_XC + b
        xb1 = POD_SASH_XC + POD_SASH_TILT * (y1 - y0) + b
        d.polygon([(xa0 * k, y0 * k), (xa1 * k, y1 * k),
                   (xb1 * k, y1 * k), (xb0 * k, y0 * k)], fill=_col(c, spec))


def side_geometry(spec):
    """Everything that mirrors: drawn once in LEFT space, then reflected."""
    K = 3
    big = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0))
    draw_sash(ImageDraw.Draw(big), spec, k=K)
    # TRIED AND REJECTED 2026-09-17: a second sash on islands 6/7 (the panel
    # that carries the flank number).  Almost all of that island's bbox is
    # hidden behind the front wheel and the pod's leading edge - only a narrow
    # strip around the number block is visible, and the sash never appeared.
    layer = big.resize((W, H), Image.LANCZOS)
    return mirror_geometry(layer)


def _stripes(d, x0, x1, widths, spec, skips=()):
    """Centre stripes: bands about row CENTRE, running along texture x."""
    for a, b, c in _band_rects(CENTRE, widths):
        runs, x = [], x0
        for s0, s1 in sorted(skips):
            if s1 <= x or s0 >= x1:
                continue
            if s0 > x:
                runs.append((x, int(s0)))
            x = max(x, int(s1))
        if x < x1:
            runs.append((x, x1))
        for r0, r1 in runs:
            d.rectangle([r0, int(round(a)), r1 - 1, int(round(b)) - 1],
                        fill=_col(c, spec))


def centre_line(img, spec):
    """Nose stripes -> the AI roundel node -> scuttle; engine cover -> tail."""
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    d = ImageDraw.Draw(img)
    r_ring = NOSE_BADGE_D / 2.0 + RING_GAP + RING_W
    skips = [(NOSE_BADGE_CX - r_ring - RING_GAP, NOSE_BADGE_CX + r_ring + RING_GAP)]
    _stripes(d, NOSE_X[0], NOSE_X[1], NOSE_CS, spec, skips)
    _stripes(d, COVER_X[0], COVER_X[1], COVER_CS, spec, COVER_SKIP)
    cx, cy = NOSE_BADGE_CX, CENTRE
    d.ellipse([cx - r_ring, cy - r_ring, cx + r_ring, cy + r_ring],
              fill=_col(LINE, spec))
    r_in = NOSE_BADGE_D / 2.0 + RING_GAP
    d.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in],
              fill=tuple(T.SPEC_BODY if spec else BODY) + (255,))
    badge = S(T.roundel(NOSE_BADGE_D)).transpose(Image.ROTATE_270)
    img.alpha_composite(badge, (cx - badge.width // 2, cy - badge.height // 2))


def side_text(img, spec):
    """AINTOLOGIC + driver strip on each sidepod flank (mirrored placement)."""
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    wm = T.wordmark(int(FLANK_WM_W * 0.2), ink=T.WHITE, accent=T.PAPAYA)
    wm = S(wm.resize((FLANK_WM_W, int(wm.height * FLANK_WM_W / wm.width)),
                     Image.LANCZOS))
    ds = S(sponsors.driver_strip(FLANK_DRIVER_W, DRIVER_NAME, face=T.BLACK,
                                 ink=T.WHITE, accent=T.PAPAYA))
    for left in (True, False):
        place(img, wm, FLANK_WM_CXY[0] - wm.width // 2,
              FLANK_WM_CXY[1] - wm.height // 2, left)
        place(img, ds, FLANK_DRIVER_XY[0], FLANK_DRIVER_XY[1], left)


def cover_flanks(img, spec):
    """FreakFarm on each engine-cover top shoulder (island 1, so it mirrors)."""
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    ff = S(LOGO2(FF_W, ink=T.WHITE, accent=T.PAPAYA))
    for left in (True, False):
        place(img, ff, FF_CXY[0] - ff.width // 2, FF_CXY[1] - ff.height // 2,
              left)


def wing_and_endplates(img, spec):
    """AINTOLOGIC across the rear wing and the cat on both endplate outer
    faces.  Transforms here are VERIFIED ON THE RENDER, not inferred - the
    wing is a closed profile unwrapped in one island."""
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    wm = T.wordmark(int(WING_WM_W * 0.2), ink=T.WHITE, accent=T.PAPAYA)
    wm = S(wm.resize((WING_WM_W, int(wm.height * WING_WM_W / wm.width)),
                     Image.LANCZOS))
    img.alpha_composite(wm, (WING_WM_CXY[0] - wm.width // 2,
                             WING_WM_CXY[1] - wm.height // 2))
    # TRIED AND REJECTED 2026-09-17: a white|papaya|white band on the wing's
    # rear face (row 2).  Unlike the Lotus, the HPD's wing has essentially NO
    # rear-facing area - dead astern it is a ~2 px dark edge, and the band only
    # showed as two specks where the profile thickens at the endplate mounts.
    # The dead-rear read comes from the engine-cover centre stripes instead.
    for d_, (cx, cy) in ((CDS_L_D, CDS_L_CXY), (CDS_R_D, CDS_R_CXY)):
        cat = S(LOGO1(d_))
        img.alpha_composite(cat, (cx - cat.width // 2, cy - cat.height // 2))


def number_panels(img, spec):
    m = NUM_MARGIN
    for bx, by, bw, bh in NUMBER_BLOCKS.values():
        p = T.number_panel(bw + 2 * m, bh + 2 * m,
                           fill=(T.SPEC_NUM if spec else T.WHITE))
        img.alpha_composite(p, (bx - m, by - m))


def build(spec=False):
    img = Image.new("RGBA", (W, H), tuple(T.SPEC_BODY if spec else BODY) + (255,))
    img.alpha_composite(side_geometry(spec))
    centre_line(img, spec)
    side_text(img, spec)
    cover_flanks(img, spec)
    wing_and_endplates(img, spec)
    number_panels(img, spec)
    img = img.convert("RGB")
    if spec:
        d = ImageDraw.Draw(img)
        for x, y, w, h in NUMBER_BLOCKS.values():
            d.rectangle([x, y, x + w - 1, y + h - 1], fill=T.SPEC_NUM)
    return img


def check_number_blocks(img):
    """A block may be base colour or the flat white number panel only."""
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


# --- spec map: the approved "Satin-True" (B3) hierarchy.  NOT yet A/B-validated
# on this car - that happens after the designer approves the look.
SPEC_VARIANTS = {
    "B3": {"body": (0, 170, 200), "orange": (0, 35, 16), "white": (0, 55, 30),
           "decal": (0, 120, 150), "num": (0, 60, 110)},
}
SPEC_DEFAULT = "B3"
SPEC_ORANGE_GROW = 3


def spec_from_colour(img, variant=SPEC_DEFAULT):
    P = SPEC_VARIANTS[variant]
    a = np.asarray(img.convert("RGB")).astype(np.int16)
    keys = [("body", BODY), ("orange", ACCENT), ("white", T.WHITE)]
    dist = np.stack([np.abs(a - np.array(c, dtype=np.int16)).sum(axis=2)
                     for _, c in keys], axis=0)
    best = dist.argmin(axis=0)
    close = dist.min(axis=0) <= 200
    out = np.empty(a.shape, dtype=np.uint8)
    out[...] = P["decal"]
    for i, (name, _) in enumerate(keys):
        out[(best == i) & close] = P[name]
    m = (a[..., 0] > 100) & (a[..., 0] - a[..., 2] > 80) & (a[..., 1] < a[..., 0] - 40)
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
