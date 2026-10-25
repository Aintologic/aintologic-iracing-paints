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

"""TEAM SCHEME - Lotus 79 (#25).  Sixth car on the scheme.  v1.0 LOCKED 2026-09-17.

APPROVED by the designer 2026-09-17 with no changes; frozen as
releases/lotus-79/v1.0-2026-09-17/ (tag lotus-79/v1.0-2026-09-17).  The HISTORIC
FORMULA 1 adaptation.  Any pixel change is a v1.1, never an edit of v1.0.
To edit it later start at docs/car-maps/lotus-79.md, "How to edit this car later".

The AINTOLOGIC team livery (docs/PAINT-SCHEME.md) placed on the Lotus 79's
panel map (docs/car-maps/lotus-79.md).  Every mark comes from src/teamscheme.py
and src/sponsors.py; this file holds ONLY the Lotus's geometry and placements.
No MX-5 / F4 / RSR / Ray / Ferrari coordinate is reused.

    python src/team_l79.py            -> out/ in the project folder
    python src/team_l79.py --here     -> the cwd instead
    python src/team_l79.py --no-spec  -> colour map only
    python src/team_l79.py --png      -> also write the flat texture as PNG

Writes car_<id>.tga (+ car_spec_<id>.tga); see src/personalize.py for
--id / --driver / --logo1 / --logo2 / --out / --profile.

Car ID #25 confirmed in Car Info 2026-09-17 (; the account
shows "License Required" but the car viewer loads custom paint regardless).
Template: 25_template_L79.zip
("Lotus 79.psd", 2048x2048).  Paint folder: %USERPROFILE%\\Documents\\iRacing\\paint\\lotus79.

THE RULE OF THIS UV (car map, measured 2026-09-17 by mask correlation on
fifteen island pairs, 98-100 % overlap): the body is mirror-symmetric about
texture row 1259 - **right y = 2518 - left y, x identical**.  Islands with
y > 1259 are the car's LEFT side and read UPRIGHT from a level left view,
texture +x = REARWARD.  Their mirrors (y < 1259) are the RIGHT side and render
ROTATE_180 from a level right view.  So side geometry is drawn in LEFT texture
space and mirrored in one copy; text is composited afterwards (upright on the
left, ROTATE_180 at the mirrored row on the right - playbook Rule 4).

NOT mirrored (they live in rows < 480, outside the body mirror): the rear
wing (island 0, span along y, chord along x, +x rearward, y 0 = car's right),
the four rear-wing endplate faces (11 R outer, 12 R inner, 13 L inner,
14 L outer - both outer faces read upright from their own side) and the
headrest fairing (17).
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
import teamscheme as T
import sponsors
import personalize

CUSTOMER = personalize.DEFAULT_ID
PAINT_DIR = os.path.join(os.path.expanduser("~"), "Documents", "iRacing",
                         "paint", "lotus79")
# personalization, set from the CLI/profile in __main__ before build() runs:
DRIVER_NAME = ""                       # blank driver strip by default
LOGO1 = sponsors.placeholder_logo      # Cats Don't Suck slot
LOGO2 = sponsors.placeholder_logo      # FreakFarm slot
W = H = 2048
MIRROR = 2518                        # right y = MIRROR - left y
CENTRE = MIRROR // 2                 # 1259, the car's centre line in texture

# --- template anchor blocks (PSD "Number Block Locations") -------------------
NUMBER_BLOCKS = {"N1": (1300, 574, 116, 102),    # RIGHT sidepod face, rear
                 "N2": (261, 1202, 93, 116),     # nose top, astride the centre line
                 "N3": (1300, 1844, 116, 101)}   # LEFT sidepod face, rear

BODY, LINE, ACCENT = T.BLACK, T.WHITE, T.PAPAYA

# LEFT half (rows 1260..2040) is copied flipped onto rows 478..1258.
MIRROR_SRC = (0, 1260, 2048, 781)

# =============================================================================
# PLACEMENTS - approved and locked v1.0 2026-09-17 (issue #5).
# Side placements in LEFT texture coordinates (y > 1259).
# Band recipe everywhere: orange = 2x white, small body-colour gaps.
# -----------------------------------------------------------------------------
# nose centre stripes: island 1 (NOSE, top visible from x ~140) + island 46
# (the scuttle / cockpit coaming, x 619..731)
NOSE_X = (138, 732)
NOSE_CS = (40, 20, 6)                # orange, white, gap (texels)
NOSE_NUM_MARGIN = 8
NOSE_NUM_GAP = 12                    # stripes stop this far from the panel
NOSE_BADGE_D, NOSE_BADGE_CX = 110, 508   # template's nose sponsor block 437..579
RING_GAP, RING_W = 5, 11

# engine cover (island 10) centre stubs either side of the exposed intake
# trumpets (x ~1570..1745 on the render) - a gap, not something to paint over
COVER_STUBS = [(1440, 1562), (1752, 1850)]
COVER_CS = (30, 15, 5)

# sidepod sash: island 2 (pod TOP, y 1627 inboard .. 1807 outboard) wraps
# straight onto island 5 (pod FACE, y 1815 top .. 1969 bottom).  Lean:
# top-forward, so xc grows with y.
POD_SASH = dict(xc=640, tilt=0.25, orange=44, white=22, gap=6)
POD_SASH_Y = (1627, 1972)

# marks
POD_WM_W, POD_WM_CXY = 430, (1022, 1900)     # AINTOLOGIC, pod face (block 747..1287)
TUB_FF_W, TUB_FF_CXY = 290, (1170, 1452)     # FreakFarm, tub side (island 6)
TUB_DRIVER_W, TUB_DRIVER_XY = 118, (770, 1392)
WING_WM_W, WING_WM_CXY = 380, (407, 239)     # AINTOLOGIC, rear wing top, reads from behind
# The wing is one closed profile unwrapped along x: top surface LE ~260 -> TE ~509
# (+x rearward), then the steep REAR FACE of the flap from the TE at x ~5 down to
# ~120 (+x DOWN the face, read from a level dead-rear view), then the underside.
WING_TE_X, WING_TE_CS = 25, (12, 6, 3)       # band set along the top of the REAR face
WING_REAR_WM_W, WING_REAR_WM_CXY = 300, (82, 239)   # AINTOLOGIC on the rear face
WING_SPAN = (8, 471)                         # island 0 bbox rows (nothing else lives in x 470..500 there)
# Cats Don't Suck: rear-wing endplate OUTER faces, upper panel above the tyre
EP_CDS_D = 116
EP_CDS_L = (648, 118)                        # island 14, left outer, +x rearward
EP_CDS_R = (908, 117)                        # island 11, right outer, +x forward
NUM_MARGIN = 8


# =============================================================================
def specify(im, rgb=T.SPEC_DECAL):
    out = Image.new("RGBA", im.size, tuple(rgb) + (255,))
    out.putalpha(im.getchannel("A"))
    return out


def _col(c, spec):
    return tuple(T.SPEC_LINE if spec else c) + (255,)


def _band_rects(cx, widths):
    ow, ww, g = widths
    return [(cx - ow / 2.0 - g - ww, cx - ow / 2.0 - g, LINE),
            (cx - ow / 2.0, cx + ow / 2.0, ACCENT),
            (cx + ow / 2.0 + g, cx + ow / 2.0 + g + ww, LINE)]


def place(img, el, x, y, left):
    """TEXT (playbook Rule 4).  (x, y) = top-left in LEFT texture space."""
    if left:
        img.alpha_composite(el, (x, y))
    else:
        img.alpha_composite(el.transpose(Image.ROTATE_180), (x, MIRROR - y - el.height))


def mirror_geometry(layer):
    a = np.array(layer)
    x0, y0, w, h = MIRROR_SRC
    src = a[y0:y0 + h, x0:x0 + w]
    d0 = MIRROR - (y0 + h - 1)
    a[d0:d0 + h, x0:x0 + w] = src[::-1]
    return Image.fromarray(a, "RGBA")


def draw_pod_sash(d, spec, k=1):
    s = POD_SASH
    y0, y1 = POD_SASH_Y
    for a, b, c in _band_rects(0, (s["orange"], s["white"], s["gap"])):
        xa0, xa1 = s["xc"] + a, s["xc"] + s["tilt"] * (y1 - y0) + a
        xb0, xb1 = s["xc"] + b, s["xc"] + s["tilt"] * (y1 - y0) + b
        d.polygon([(xa0 * k, y0 * k), (xa1 * k, y1 * k),
                   (xb1 * k, y1 * k), (xb0 * k, y0 * k)], fill=_col(c, spec))


def side_geometry(spec):
    K = 3
    big = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0))
    draw_pod_sash(ImageDraw.Draw(big), spec, k=K)
    layer = big.resize((W, H), Image.LANCZOS)
    return mirror_geometry(layer)


def _stripes(d, x0, x1, widths, spec, skips=()):
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
            d.rectangle([r0, int(round(a)), r1 - 1, int(round(b)) - 1], fill=_col(c, spec))


def centre_panels(img, spec):
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    d = ImageDraw.Draw(img)
    bx, by, bw, bh = NUMBER_BLOCKS["N2"]
    m = NOSE_NUM_MARGIN
    r_ring = NOSE_BADGE_D / 2.0 + RING_GAP + RING_W
    skips = [(bx - m - NOSE_NUM_GAP, bx + bw + m + NOSE_NUM_GAP),
             (NOSE_BADGE_CX - r_ring - RING_GAP, NOSE_BADGE_CX + r_ring + RING_GAP)]
    _stripes(d, NOSE_X[0], NOSE_X[1], NOSE_CS, spec, skips)
    for x0, x1 in COVER_STUBS:
        _stripes(d, x0, x1, COVER_CS, spec)
    cx, cy = NOSE_BADGE_CX, CENTRE
    d.ellipse([cx - r_ring, cy - r_ring, cx + r_ring, cy + r_ring], fill=_col(LINE, spec))
    r_in = NOSE_BADGE_D / 2.0 + RING_GAP
    d.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in],
              fill=tuple(T.SPEC_BODY if spec else BODY) + (255,))
    badge = S(T.roundel(NOSE_BADGE_D)).transpose(Image.ROTATE_270)
    img.alpha_composite(badge, (cx - badge.width // 2, cy - badge.height // 2))
    img.alpha_composite(T.number_panel(bw + 2 * m, bh + 2 * m,
                                       fill=(T.SPEC_NUM if spec else T.WHITE)),
                        (bx - m, by - m))


def side_text(img, spec):
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    wm = T.wordmark(int(POD_WM_W * 0.2), ink=T.WHITE, accent=T.PAPAYA)
    wm = S(wm.resize((POD_WM_W, int(wm.height * POD_WM_W / wm.width)), Image.LANCZOS))
    ff = S(LOGO2(TUB_FF_W, ink=T.WHITE, accent=T.PAPAYA))
    ds = S(sponsors.driver_strip(TUB_DRIVER_W, DRIVER_NAME, face=T.BLACK,
                                 ink=T.WHITE, accent=T.PAPAYA))
    for left in (True, False):
        place(img, wm, POD_WM_CXY[0] - wm.width // 2, POD_WM_CXY[1] - wm.height // 2, left)
        place(img, ff, TUB_FF_CXY[0] - ff.width // 2, TUB_FF_CXY[1] - ff.height // 2, left)
        place(img, ds, TUB_DRIVER_XY[0], TUB_DRIVER_XY[1], left)


def wing_and_endplates(img, spec):
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    wm = T.wordmark(int(WING_WM_W * 0.2), ink=T.WHITE, accent=T.PAPAYA)
    wm = S(wm.resize((WING_WM_W, int(wm.height * WING_WM_W / wm.width)), Image.LANCZOS))
    wm = wm.transpose(Image.ROTATE_90)       # reads from BEHIND the car
    img.alpha_composite(wm, (WING_WM_CXY[0] - wm.width // 2, WING_WM_CXY[1] - wm.height // 2))
    rw = T.wordmark(int(WING_REAR_WM_W * 0.2), ink=T.WHITE, accent=T.PAPAYA)
    rw = S(rw.resize((WING_REAR_WM_W, int(rw.height * WING_REAR_WM_W / rw.width)), Image.LANCZOS))
    rw = rw.transpose(Image.ROTATE_90)       # same transform: reads from a dead-rear view
    img.alpha_composite(rw, (WING_REAR_WM_CXY[0] - rw.width // 2, WING_REAR_WM_CXY[1] - rw.height // 2))
    # white | papaya | white along the top of the rear face, full span
    d = ImageDraw.Draw(img)
    for a, b, c in _band_rects(WING_TE_X, WING_TE_CS):
        d.rectangle([int(round(a)), WING_SPAN[0], int(round(b)) - 1, WING_SPAN[1]],
                    fill=_col(c, spec))
    cat = S(LOGO1(EP_CDS_D))
    for cx, cy in (EP_CDS_L, EP_CDS_R):
        img.alpha_composite(cat, (cx - cat.width // 2, cy - cat.height // 2))


def number_panels(img, spec):
    m = NUM_MARGIN
    for nm in ("N1", "N3"):
        bx, by, bw, bh = NUMBER_BLOCKS[nm]
        p = T.number_panel(bw + 2 * m, bh + 2 * m, fill=(T.SPEC_NUM if spec else T.WHITE))
        img.alpha_composite(p, (bx - m, by - m))


def build(spec=False):
    img = Image.new("RGBA", (W, H), tuple(T.SPEC_BODY if spec else BODY) + (255,))
    img.alpha_composite(side_geometry(spec))
    side_text(img, spec)
    centre_panels(img, spec)
    wing_and_endplates(img, spec)
    number_panels(img, spec)
    img = img.convert("RGB")
    if spec:
        d = ImageDraw.Draw(img)
        for x, y, w, h in NUMBER_BLOCKS.values():
            d.rectangle([x, y, x + w - 1, y + h - 1], fill=T.SPEC_NUM)
    return img


# --- spec map: the approved "Satin-True" (B3) hierarchy, unchanged.  VALIDATED
# on this car 2026-09-17 by an A/B against no spec map at one level-left pose
# (releases/lotus-79/v1.0-2026-09-17/closeups-spec-ab.jpg).
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
    dist = np.stack([np.abs(a - np.array(c, dtype=np.int16)).sum(axis=2) for _, c in keys], axis=0)
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


def check_number_blocks(img):
    """A block may be base colour or the flat white number panel only."""
    px = img.load()
    ok = (BODY, T.WHITE)
    bad = []
    for name, (x, y, w, h) in NUMBER_BLOCKS.items():
        off = sum(1 for yy in range(y, y + h) for xx in range(x, x + w)
                  if min(sum(abs(a - b) for a, b in zip(px[xx, yy], c)) for c in ok) > 6)
        print("  %s %s %d bad / %d px" % (name, "DIRTY" if off else "clean", off, w * h))
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
    CUSTOMER = cfg.id
    DRIVER_NAME = cfg.driver
    LOGO1, LOGO2 = cfg.logo1, cfg.logo2
    out_dir = cfg.out_dir or (os.getcwd() if args.here else personalize.default_out_dir())
    os.makedirs(out_dir, exist_ok=True)
    colour = build(spec=False)
    print("number blocks:")
    bad = check_number_blocks(colour)
    if bad:
        sys.exit("FAIL: artwork is inside %s - fix the geometry, do not mask it." % ", ".join(bad))
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
