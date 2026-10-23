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

"""TEAM SCHEME - FIA F4 (#148).  Second car on the scheme.

The AINTOLOGIC team livery (docs/PAINT-SCHEME.md) placed on the F4's panel
map (docs/car-maps/fia-f4.md).  Every mark comes from src/teamscheme.py and
src/sponsors.py; this file holds ONLY the F4's geometry and placements.
Copied from the MX-5 gold master (src/team_mx5.py) with every MX-5 number
deleted - the F4 is an open-wheel car and shares no UV with it.

    python src/team_f4.py            -> the iRacing paint folder
    python src/team_f4.py --here     -> the cwd instead
    python src/team_f4.py --no-spec  -> colour map only
    python src/team_f4.py --png      -> also write the flat texture as PNG

Writes car_<id>.tga (+ car_spec_<id>.tga); see src/personalize.py for
--id / --driver / --logo1 / --logo2 / --out / --profile.

Template: 148_template_iR04.zip
(the car was the Formula iR-04 before the FIA licence; same UV, "Formula
IR04.psd", 2048x2048).

THE ONE RULE OF THIS UV (car map, measured 2026-09-14 on the flank, pod
and engine-cover pairs): every right-side island is the left one mirrored
about texture row 1128.5 - right y = 2257 - left y, x identical, nose at
low x on both.  So the whole left side is drawn in LEFT texture space, the
GEOMETRY is mirrored to the right in one operation (mirror_geometry), and
TEXT is composited afterwards, ROTATE_180 on the right, at the mirrored spot
(playbook Rule 4).  Island edges per column: src/f4_islands.py (generated
from the template; the template itself is not in git).
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
import teamscheme as T
import sponsors
import personalize
import f4_islands as ISL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUSTOMER = personalize.DEFAULT_ID
PAINT_DIR = os.path.join(os.path.expanduser("~"), "Documents", "iRacing",
                         "paint", "formulair04")
# personalization, set from the CLI/profile in __main__ before build() runs:
DRIVER_NAME = ""                       # blank driver strip by default
LOGO1 = sponsors.placeholder_logo      # Cats Don't Suck slot
LOGO2 = sponsors.placeholder_logo      # FreakFarm slot
W = H = 2048
MIRROR = ISL.MIRROR                  # 2257

# --- template anchor blocks (PSD "Number Blocks" layer) ----------------------
NUMBER_BLOCKS = {"N1": (1124, 74, 101, 102),     # right rear endplate, outer
                 "N2": (1845, 74, 101, 102),     # left rear endplate, outer
                 "N3": (322, 1072, 101, 115)}    # nose top, on the centre line

BODY, LINE, ACCENT = T.BLACK, T.WHITE, T.PAPAYA

# --- islands, LEFT texture space (docs/car-maps/fia-f4.md) -------------------
# The side islands are mirrored to the right as a block; the two rects below
# are the regions that get mirrored (everything left-side lives inside them).
MIRROR_RECTS = [(0, 1220, 1000, 828),      # flank + sidepod + sidepod top
                (1000, 1129, 1048, 919)]   # engine cover halves
NOSE = (60, 1030, 860, 210)          # nose top; x along the car, tip at low x
NOSE_CY = 1128 - NOSE[1]             # centre line = row 1128 (island edges + N3)
EP_L_OUT = (1782, 25, 244, 267)      # rear endplates, OUTER faces (upright); the
EP_R_OUT = (1045, 25, 244, 267)      # faces are mirrors: x_L = 3071 - x_R

# =============================================================================
# PLACEMENTS - first pass 2026-09-14 (issue #1, milestone 1), all in LEFT
# texture coordinates.  Band recipe everywhere: orange = 2x white, small
# body-colour gaps.
#
#   * CENTRE STRIPES down the nose top (the F4's "hood"): tip -> number
#     panel -> the team roundel as the node -> the cockpit.
#   * ENGINE COVER: the same three bands along the UPPER SLOPE of the cover
#     on each side, hung from the ridge edge of the island (EC_B), so both
#     sides are the same by construction (second pass, the designer's symmetry
#     note: the first pass had one side at the ridge and one at the crease
#     because the two islands' rects had been guessed, not measured).
#   * the SASH: the MX-5's fender sash becomes a sash across the FRONT of
#     each sidepod, just behind the inlet, leaning top-forward, crease to
#     floor.  The wordmark sits behind it.
#   * AINTOLOGIC dominant on the sidepod flank; FreakFarm on the engine
#     cover's upper slope under the stripes; number panels on the nose and
#     the endplates; driver strip under the cockpit rim.  The sim's own
#     mandatory decals already put the cutoff + extinguisher marks at the
#     front of the engine cover, so none are drawn here.
POD_X0, POD_Y0 = 71, 1830            # pod car-space origin (front edge, crease)
SASH = dict(xc=215, tilt=0.28, orange=40, white=20, gap=5)   # X at the crease row
POD_WM_W, POD_WM_CXY = 440, (540, 105)      # car-space, from the pod origin
NOSE_CS = (36, 18, 5)                # orange, white, gap on the nose top (texels)
NOSE_NUM = (254, 34, 117, 131)       # white panel: N3 local (262,42,101,115) + 8 margin
NOSE_NUM_GAP = 12                    # stripes stop this far from the panel
NOSE_BADGE_D, NOSE_BADGE_CX = 110, 600
RING_GAP, RING_W = 5, 12
EC_X = (1465, 1945)                  # ridge stripes: behind the F4 decal -> the tail tip
EC_CS = dict(top_gap=6, orange=24, gap=4, white=12)   # texels DOWN from the ridge edge
EC_FF_W, EC_FF_CXY = 250, (1600, 1262)   # FreakFarm on the upper slope, under the stripes
FLANK_DRIVER_W, FLANK_DRIVER_XY = 110, (837, 1400)
EP_NUM_MARGIN = 8
# Cats Don't Suck under the number on each endplate's outer face (the designer,
# 2026-09-14 review: the small wordmark there read truncated; the cat
# replaces it).  The clean quad of the face below the number block runs from
# the tall FRONT edge to the sloping rear edge: at row 224 it is x 1065..1195
# on the right face; the left face is its mirror, x_L = 3071 - x_R (the
# number blocks: 1124..1225 <-> 1846..1947).  Centre biased 34 texels forward
# of the block centre so the disc clears the sloping rear edge.
EP_CDS_D = 70
EP_CDS_CXY_R = (1140, 224)
EP_CDS_CXY_L = (3071 - 1140, 224)


def specify(im, rgb=T.SPEC_DECAL):
    out = Image.new("RGBA", im.size, tuple(rgb) + (255,))
    out.putalpha(im.getchannel("A"))
    return out


def _col(c, spec):
    return tuple(T.SPEC_LINE if spec else c) + (255,)


def _band_rects(cx, spec_widths):
    ow, ww, g = spec_widths
    return [(cx - ow / 2.0 - g - ww, cx - ow / 2.0 - g, LINE),
            (cx - ow / 2.0, cx + ow / 2.0, ACCENT),
            (cx + ow / 2.0 + g, cx + ow / 2.0 + g + ww, LINE)]


def _hbands(draw, cy, widths, x0, x1, spec, skips=()):
    """Horizontal white|orange|white bands, y centred at cy, columns x0..x1,
    leaving every (a, b) in skips untouched."""
    cuts = sorted(skips)
    for y0, y1, c in _band_rects(cy, widths):
        x = x0
        for a, b in cuts:
            if a > x:
                draw.rectangle([x, y0, min(a, x1) - 1, y1 - 1], fill=_col(c, spec))
            x = max(x, b)
        if x < x1:
            draw.rectangle([x, y0, x1 - 1, y1 - 1], fill=_col(c, spec))


def _edge(table, x):
    """(top, bottom) of an island at column x, linearly interpolated."""
    ks = sorted(table)
    if x <= ks[0]:
        return table[ks[0]]
    if x >= ks[-1]:
        return table[ks[-1]]
    import bisect
    i = bisect.bisect_right(ks, x)
    a, b = ks[i - 1], ks[i]
    (t0, b0), (t1, b1) = table[a], table[b]
    f = (x - a) / float(b - a)
    return (t0 + (t1 - t0) * f, b0 + (b1 - b0) * f)


def place(img, el, x, y, right):
    """TEXT and anything that must never mirror (playbook Rule 4).  (x, y) is
    the element's top-left in LEFT texture space; on the right it goes in
    ROTATE_180 at the mirrored rows, so it reads upright on both sides."""
    if right:
        img.alpha_composite(el.transpose(Image.ROTATE_180), (x, MIRROR - y - el.height))
    else:
        img.alpha_composite(el, (x, y))


def mirror_geometry(layer):
    """Copy the LEFT-side geometry in MIRROR_RECTS to the right, y' = MIRROR - y."""
    a = np.array(layer)
    for x0, y0, w, h in MIRROR_RECTS:
        src = a[y0:y0 + h, x0:x0 + w]
        d0 = MIRROR - (y0 + h - 1)
        a[d0:d0 + h, x0:x0 + w] = src[::-1]
    return Image.fromarray(a, "RGBA")


def draw_sash(d, spec, k=1):
    """Three bands across the pod front, crease to floor, top-forward lean.
    Drawn straight in left texture space (the island's own edges clip it)."""
    s = SASH
    top, bot = POD_Y0, POD_Y0 + 210
    for a, b, c in _band_rects(0, (s["orange"], s["white"], s["gap"])):
        pts = []
        for Y in (top, bot):
            xc = POD_X0 + s["xc"] + s["tilt"] * (Y - POD_Y0)
            pts.append(((xc + a) * k, Y * k))
        for Y in (bot, top):
            xc = POD_X0 + s["xc"] + s["tilt"] * (Y - POD_Y0)
            pts.append(((xc + b) * k, Y * k))
        d.polygon(pts, fill=_col(c, spec))


def draw_ec_stripes(d, spec):
    """The engine cover's upper slope (island EC_B): orange then white,
    hung from the island's RIDGE edge, per column, so the band follows the
    island's taper and lands identically on both sides after the mirror."""
    s = EC_CS
    for x in range(EC_X[0], EC_X[1]):
        top, bot = _edge(ISL.EC_B, x)
        y = top + s["top_gap"]
        d.rectangle([x, int(round(y)), x, int(round(y + s["orange"])) - 1], fill=_col(ACCENT, spec))
        y += s["orange"] + s["gap"]
        d.rectangle([x, int(round(y)), x, int(round(y + s["white"])) - 1], fill=_col(LINE, spec))


def side_geometry(spec):
    """Everything on the LEFT side that mirrors: sash, engine-cover stripes.
    Supersampled 3x for clean diagonal edges, then mirrored to the right."""
    K = 3
    big = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    draw_sash(d, spec, k=K)
    layer = big.resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(layer)
    draw_ec_stripes(d, spec)
    return mirror_geometry(layer)


def side_text(img, spec):
    """Every mark that must read upright on both sides (Rule 4)."""
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    wm = T.wordmark(int(POD_WM_W * 0.17), ink=T.WHITE, accent=T.PAPAYA)
    wm = S(wm.resize((POD_WM_W, int(wm.height * POD_WM_W / wm.width)), Image.LANCZOS))
    ff = S(LOGO2(EC_FF_W, ink=T.WHITE, accent=T.PAPAYA))
    ds = S(sponsors.driver_strip(FLANK_DRIVER_W, DRIVER_NAME, face=T.BLACK,
                                 ink=T.WHITE, accent=T.PAPAYA))
    for right in (False, True):
        place(img, wm, POD_X0 + POD_WM_CXY[0] - wm.width // 2,
              POD_Y0 + POD_WM_CXY[1] - wm.height // 2, right)
        place(img, ff, EC_FF_CXY[0] - ff.width // 2, EC_FF_CXY[1] - ff.height // 2, right)
        place(img, ds, *FLANK_DRIVER_XY, right=right)


def nose_panel(spec):
    """Nose top: centre stripes tip -> number panel -> roundel node -> cockpit.
    Texture x runs along the car (tip at 0), +y is the car's LEFT.  A mark
    read by someone standing in FRONT of the car has its top toward the
    cockpit (+x) and reads toward +y: ROTATE_270 of the upright art."""
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    nx, ny, nw, nh = NOSE
    panel = Image.new("RGBA", (nw, nh), (0, 0, 0, 0))
    d = ImageDraw.Draw(panel)
    px, py, pw, ph = NOSE_NUM
    r_ring = NOSE_BADGE_D / 2.0 + RING_GAP + RING_W
    skips = [(px - NOSE_NUM_GAP, px + pw + NOSE_NUM_GAP),
             (int(NOSE_BADGE_CX - r_ring - RING_GAP), int(NOSE_BADGE_CX + r_ring + RING_GAP))]
    _hbands(d, NOSE_CY, NOSE_CS, 0, nw, spec, skips)
    panel.alpha_composite(T.number_panel(pw, ph, fill=(T.SPEC_NUM if spec else T.WHITE)), (px, py))
    cx, cy = NOSE_BADGE_CX, NOSE_CY
    d.ellipse([cx - r_ring, cy - r_ring, cx + r_ring, cy + r_ring], fill=_col(LINE, spec))
    r_in = NOSE_BADGE_D / 2.0 + RING_GAP
    d.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in],
              fill=tuple(T.SPEC_BODY if spec else BODY) + (255,))
    badge = S(T.roundel(NOSE_BADGE_D)).transpose(Image.ROTATE_270)
    panel.alpha_composite(badge, (cx - badge.width // 2, cy - badge.height // 2))
    return panel


def endplate(img, spec, block, cds_cxy):
    """Rear-wing endplate outer face: white number panel over the block, the
    Cats Don't Suck roundel under it.  Both faces read upright from outside
    the car (probed), so the same upright art goes on both - no transform."""
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    bx, by, bw, bh = block
    m = EP_NUM_MARGIN
    npnl = T.number_panel(bw + 2 * m, bh + 2 * m, fill=(T.SPEC_NUM if spec else T.WHITE))
    img.alpha_composite(npnl, (bx - m, by - m))
    cat = S(LOGO1(EP_CDS_D))
    cx, cy = cds_cxy
    img.alpha_composite(cat, (cx - cat.width // 2, cy - cat.height // 2))


def build(spec=False):
    img = Image.new("RGBA", (W, H), tuple(T.SPEC_BODY if spec else BODY) + (255,))
    img.alpha_composite(side_geometry(spec))
    side_text(img, spec)
    n = nose_panel(spec)
    img.alpha_composite(n, (NOSE[0], NOSE[1]))
    endplate(img, spec, NUMBER_BLOCKS["N2"], EP_CDS_CXY_L)
    endplate(img, spec, NUMBER_BLOCKS["N1"], EP_CDS_CXY_R)
    img = img.convert("RGB")
    if spec:
        d = ImageDraw.Draw(img)
        for x, y, w, h in NUMBER_BLOCKS.values():
            d.rectangle([x, y, x + w - 1, y + h - 1], fill=T.SPEC_NUM)
    return img


# --- spec map: the MX-5 v4.1 "Satin-True" (B3) hierarchy, carried over
# unchanged.  VALIDATED on the F4 2026-09-14 by an A/B in the viewer at the
# same top-lit pose with and without the spec map (scratch\f4\spec_ab.jpg):
# with B3 the body is a neutral satin (mean RGB 40/40/41, blue-red bias
# +1.6) with no hotspot; without it the black goes glossy and reflects the
# sky (bias +6.2).  White crisp, orange the pop.  No F4-specific tuning
# was needed, so no ladder was run - B3 is the approved value set here too.
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
    orange_ish = (a[..., 0] > 100) & (a[..., 0] - a[..., 2] > 80) & (a[..., 1] < a[..., 0] - 40)
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
    CUSTOMER = cfg.id
    DRIVER_NAME = cfg.driver
    LOGO1, LOGO2 = cfg.logo1, cfg.logo2
    out_dir = cfg.out_dir or (os.getcwd() if args.here else os.path.join(os.getcwd(), "out"))
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
