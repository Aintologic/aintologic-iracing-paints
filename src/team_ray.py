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

"""TEAM SCHEME - Ray FF1600 (#163).  Fourth car on the scheme.

The AINTOLOGIC team livery (docs/PAINT-SCHEME.md) placed on the Ray's panel
map (docs/car-maps/ray-ff1600.md).  Every mark comes from src/teamscheme.py
and src/sponsors.py; this file holds ONLY the Ray's geometry and placements.
No MX-5 / F4 / RSR coordinate is reused - a Formula Ford shares no UV with
any of them, and it has NO WINGS, so the F4's endplate placements do not
exist here.

    python src/team_ray.py            -> the iRacing paint folder
    python src/team_ray.py --here     -> the cwd instead
    python src/team_ray.py --no-spec  -> colour map only
    python src/team_ray.py --png      -> also write the flat texture as PNG

Writes car_<id>.tga (+ car_spec_<id>.tga); see src/personalize.py for
--id / --driver / --logo1 / --logo2 / --out / --profile.

Template: 163_template_GR22.zip
("Ray FF1600.psd", 2048x2048).  Car ID #163 confirmed in Car Info 2026-09-14.

THE ONE RULE OF THIS UV (car map, measured 2026-09-14 by mask correlation on
twelve island pairs, 98-100% overlap): the car is mirror-symmetric in UV about
texture row 1026 - **left y = 2052 - right y, x identical**, and the islands
with y < 1026 are the car's RIGHT side (proved from a dead-front frame).  From
a level RIGHT-side view the right islands render ROTATE_180 (texture +x =
REARWARD, +y = UP the car); the left islands read upright.  So everything is
drawn in RIGHT texture space, the GEOMETRY is mirrored to the left in one
operation (mirror_geometry), and TEXT is composited afterwards - ROTATE_180 on
the right, upright at the mirrored row on the left (playbook Rule 4).

Island edges per column: src/ray_islands.py (generated from the template by
tools/island_edges.py; the template itself is not in git).
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
import teamscheme as T
import sponsors
import personalize
import ray_islands as ISL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUSTOMER = personalize.DEFAULT_ID
PAINT_DIR = os.path.join(os.path.expanduser("~"), "Documents", "iRacing",
                         "paint", "raygr22")
# personalization, set from the CLI/profile in __main__ before build() runs:
DRIVER_NAME = ""                       # blank driver strip by default
LOGO1 = sponsors.placeholder_logo      # Cats Don't Suck slot
LOGO2 = sponsors.placeholder_logo      # FreakFarm slot
W = H = 2048
MIRROR = ISL.MIRROR                  # 2052; left y = MIRROR - right y
CENTRE = MIRROR // 2                 # 1026, the car's centre line in texture

# --- template anchor blocks (PSD "Number Blocks" layer) ----------------------
NUMBER_BLOCKS = {"N1": (1688, 625, 106, 95),     # RIGHT rear body side
                 "N2": (454, 974, 95, 106),      # nose top, on the centre line
                 "N3": (1688, 1332, 106, 95)}    # LEFT rear body side

BODY, LINE, ACCENT = T.BLACK, T.WHITE, T.PAPAYA

# Everything above the centre line is the car's RIGHT side and gets mirrored
# down.  Rows 6..1026 -> 1026..2046 (the whole half in one copy, which also
# carries the LEFT sidepod, whose own UV island leaks into the background in
# the template wire and so has no entry in ray_islands.py).
MIRROR_RECT = (0, 6, 2048, 1021)

# =============================================================================
# PLACEMENTS - first pass 2026-09-14 (issue #3, milestone 1), ALL in RIGHT
# texture coordinates (y < 1026).  Band recipe everywhere: orange = 2x white,
# small body-colour gaps.
#
#   * CENTRE STRIPES down the nose top - the Ray's only long centre-line
#     surface - from the tip, past the nose number panel, through the AI
#     roundel node, to the scuttle in front of the cockpit.  The nose tip
#     island is a point, so the stripe TAPERS into it instead of running off
#     the end as a full-width slab.
#   * THE SASH across the front of each sidepod, wrapping over the pod's
#     outer shoulder, leaning top-forward - the F4's sidepod sash retargeted.
#   * AINTOLOGIC dominant on the tub flank beside the cockpit (the biggest
#     side-facing panel on this car); FreakFarm secondary on the sidepod
#     flank; Cats Don't Suck on the rear body side; driver strip on the
#     cockpit rim; white number panels on all three blocks.
# -----------------------------------------------------------------------------
# nose centre stripes: islands NOSE_TIP (33..421) + NOSE (426..930)
NOSE_X = (96, 930)
NOSE_CS = (46, 23, 6)                # orange, white, gap (texels)
NOSE_TAPER_X = 300                   # full width from here back; tapers ahead
NOSE_NUM = (446, 966, 111, 122)      # N2 + 8 texels of margin
NOSE_NUM_GAP = 14                    # the stripes stop this far from it
NOSE_BADGE_D, NOSE_BADGE_CX = 132, 742
RING_GAP, RING_W = 6, 13

# scuttle in front of the cockpit: island COWL (879..1291), pointed at 879
COWL_X = (940, 1180)
COWL_CS = (30, 15, 5)

# sidepod sash: island POD.  Rows 500 (the pod's inboard top edge) down to 30
# (the bottom of the outer face); the top of the sash is FORWARD.
POD_SASH = dict(xc=1046, tilt=0.30, orange=54, white=27, gap=6)
POD_SASH_Y = (30, 500)

# rear deck: island DECK is a tapering sliver whose HIGH-y edge is the car's
# centre line behind the cockpit.  The band is hung off that edge per column
# so the two halves meet at the spine and taper with it to the tail.
DECK_X = (1372, 1826)
DECK_CS = dict(gap=3, orange=17, mid=4, white=9)   # texels DOWN from the edge

# marks
# AINTOLOGIC.  THE TWO SIDES ARE NOT AT THE SAME X - see the car map.  A
# fairing blister stands proud of the RIGHT flank over texture x ~800..1090
# and eats the front of the wordmark there; the left flank reads clean at
# 1095, which the designer approved 2026-09-14.  The right side is therefore pushed
# rearward past the blister, which takes it across the TUB -> REAR island
# seam; REAR's rows sit TUB_REAR_DY higher-numbered at that seam, so the part
# aft of it is stepped to stay on the same line of the car.
TUB_WM_W = 470
TUB_WM_CXY = (1095, 642)                    # LEFT side (approved)
TUB_WM_CXY_R = (1330, 642)                  # RIGHT side only
TUB_REAR_SEAM = 1342                        # texture x: tub flank -> rear body
TUB_REAR_DY = 5                             # tuned ON THE RENDER, not from the
                                            # island edges: the edge tables say
                                            # +21 (TUB 599/754 <-> REAR 620/777)
                                            # and that stepped the aft half ~16
                                            # texels too high on the car.
POD_FF_W, POD_FF_CXY = 250, (1340, 262)     # FreakFarm, sidepod flank
POD_CDS_D, POD_CDS_CXY = 92, (1332, 420)    # Cats Don't Suck, sidepod TOP
TUB_DRIVER_W, TUB_DRIVER_XY = 118, (1180, 700)
NUM_MARGIN = 8


# =============================================================================
def specify(im, rgb=T.SPEC_DECAL):
    out = Image.new("RGBA", im.size, tuple(rgb) + (255,))
    out.putalpha(im.getchannel("A"))
    return out


def _col(c, spec):
    return tuple(T.SPEC_LINE if spec else c) + (255,)


def _band_rects(cx, widths):
    """(a, b, colour) for white | orange | white about cx."""
    ow, ww, g = widths
    return [(cx - ow / 2.0 - g - ww, cx - ow / 2.0 - g, LINE),
            (cx - ow / 2.0, cx + ow / 2.0, ACCENT),
            (cx + ow / 2.0 + g, cx + ow / 2.0 + g + ww, LINE)]


def place(img, el, x, y, right):
    """TEXT and anything that must never mirror (playbook Rule 4).  (x, y) is
    the element's top-left in RIGHT texture space.  The right islands render
    ROTATE_180, so the art is rotated there; the left side takes the upright
    art at the mirrored rows.  Same spot on the car, upright on both."""
    if right:
        img.alpha_composite(el.transpose(Image.ROTATE_180), (x, y))
    else:
        img.alpha_composite(el, (x, MIRROR - y - el.height))


def place_across_seam(img, el, x, y):
    """RIGHT-side text that crosses the TUB -> REAR island seam.

    The two islands are adjacent pieces of one continuous flank, but REAR's
    rows are TUB_REAR_DY higher-numbered at the join (TUB 599..754 at x 1340,
    REAR 620..777 at x 1344, heights 155 / 157).  So the mark is cut at the
    seam column and the aft half is stepped down by that offset, which puts
    both halves on the same line of the car."""
    el = el.transpose(Image.ROTATE_180)
    cut = TUB_REAR_SEAM - x
    if cut <= 0 or cut >= el.width:
        img.alpha_composite(el, (x, y if cut <= 0 else y + TUB_REAR_DY))
        return
    img.alpha_composite(el.crop((0, 0, cut, el.height)), (x, y))
    img.alpha_composite(el.crop((cut, 0, el.width, el.height)),
                        (x + cut, y + TUB_REAR_DY))


def mirror_geometry(layer):
    """Copy the RIGHT-side geometry (rows 6..1026) to the left, y' = MIRROR - y."""
    a = np.array(layer)
    x0, y0, w, h = MIRROR_RECT
    src = a[y0:y0 + h, x0:x0 + w]
    d0 = MIRROR - (y0 + h - 1)
    a[d0:d0 + h, x0:x0 + w] = src[::-1]
    return Image.fromarray(a, "RGBA")


def draw_pod_sash(d, spec, k=1):
    """Three bands across the front of the sidepod, wrapping over its outer
    shoulder (texture y 500 = the pod's top, inboard edge; y 150 = the bottom
    of the visible outer face).  Top-forward lean, so xc grows as y falls."""
    s = POD_SASH
    ytop, ybot = POD_SASH_Y[1], POD_SASH_Y[0]
    for a, b, c in _band_rects(0, (s["orange"], s["white"], s["gap"])):
        pts = []
        for Y in (ytop, ybot):
            xc = s["xc"] + s["tilt"] * (ytop - Y)
            pts.append(((xc + a) * k, Y * k))
        for Y in (ybot, ytop):
            xc = s["xc"] + s["tilt"] * (ytop - Y)
            pts.append(((xc + b) * k, Y * k))
        d.polygon(pts, fill=_col(c, spec))


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


def draw_deck_stripes(d, spec):
    """Orange then white, hung off the DECK island's centre-line edge (its
    HIGH-y edge), per column, so the band follows the tail's taper and lands
    identically on both sides after the mirror."""
    s = DECK_CS
    for x in range(DECK_X[0], DECK_X[1]):
        top, bot = _edge(ISL.DECK, x)
        if bot - top < s["gap"] + s["orange"] + 2:
            continue
        y = bot - s["gap"] - s["orange"]
        d.rectangle([x, int(round(y)), x, int(round(y + s["orange"])) - 1],
                    fill=_col(ACCENT, spec))
        y -= s["mid"] + s["white"]
        if y > top:
            d.rectangle([x, int(round(y)), x, int(round(y + s["white"])) - 1],
                        fill=_col(LINE, spec))


def _taper(x):
    """Fraction of full stripe width at nose column x - the tip is a point,
    so the three bands converge into it instead of over-running the island."""
    x0, x1 = NOSE_X[0], NOSE_TAPER_X
    if x >= x1:
        return 1.0
    return max(0.0, (x - x0) / float(x1 - x0)) ** 0.75


def nose_stripes(d, spec):
    """White | papaya | white down the nose centre line, tapering into the
    tip, skipping the number panel and the roundel node."""
    ow, ww, g = NOSE_CS
    px, py, pw, ph = NOSE_NUM
    r_ring = NOSE_BADGE_D / 2.0 + RING_GAP + RING_W
    skips = [(px - NOSE_NUM_GAP, px + pw + NOSE_NUM_GAP),
             (NOSE_BADGE_CX - r_ring - RING_GAP, NOSE_BADGE_CX + r_ring + RING_GAP)]
    for x in range(NOSE_X[0], NOSE_X[1]):
        if any(a <= x < b for a, b in skips):
            continue
        f = _taper(x)
        if f <= 0.02:
            continue
        for a, b, c in _band_rects(CENTRE, (ow * f, ww * f, g * f)):
            if b - a < 0.8:
                continue
            d.rectangle([x, int(round(a)), x, int(round(b)) - 1], fill=_col(c, spec))


def cowl_stripes(d, spec):
    """The same bands on the scuttle between the nose and the cockpit."""
    for x in range(COWL_X[0], COWL_X[1]):
        for a, b, c in _band_rects(CENTRE, COWL_CS):
            d.rectangle([x, int(round(a)), x, int(round(b)) - 1], fill=_col(c, spec))


def centre_panels(img, spec):
    """Nose: stripes, the number panel and the roundel node.  These islands are
    symmetric about the centre line, so they are drawn once, not mirrored."""
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    d = ImageDraw.Draw(img)
    nose_stripes(d, spec)
    cowl_stripes(d, spec)
    # the roundel node: body-colour gap, white ring, gap, badge
    cx, cy = NOSE_BADGE_CX, CENTRE
    r_ring = NOSE_BADGE_D / 2.0 + RING_GAP + RING_W
    d.ellipse([cx - r_ring, cy - r_ring, cx + r_ring, cy + r_ring], fill=_col(LINE, spec))
    r_in = NOSE_BADGE_D / 2.0 + RING_GAP
    d.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in],
              fill=tuple(T.SPEC_BODY if spec else BODY) + (255,))
    badge = S(T.roundel(NOSE_BADGE_D)).transpose(Image.ROTATE_270)
    img.alpha_composite(badge, (cx - badge.width // 2, cy - badge.height // 2))
    # the nose number panel (the stamp lands centred on it)
    px, py, pw, ph = NOSE_NUM
    img.alpha_composite(T.number_panel(pw, ph, fill=(T.SPEC_NUM if spec else T.WHITE)),
                        (px, py))


def side_geometry(spec):
    """Everything on the RIGHT side that mirrors.  Supersampled 3x for clean
    diagonals, then copied to the left."""
    K = 3
    big = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    draw_pod_sash(d, spec, k=K)
    layer = big.resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(layer)
    draw_deck_stripes(d, spec)
    return mirror_geometry(layer)


def side_text(img, spec):
    """Every mark that must read upright on both sides (Rule 4)."""
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    wm = T.wordmark(int(TUB_WM_W * 0.17), ink=T.WHITE, accent=T.PAPAYA)
    wm = S(wm.resize((TUB_WM_W, int(wm.height * TUB_WM_W / wm.width)), Image.LANCZOS))
    ff = S(LOGO2(POD_FF_W, ink=T.WHITE, accent=T.PAPAYA))
    cat = S(LOGO1(POD_CDS_D))
    ds = S(sponsors.driver_strip(TUB_DRIVER_W, DRIVER_NAME, face=T.BLACK,
                                 ink=T.WHITE, accent=T.PAPAYA))
    # AINTOLOGIC: per-side X (the right flank's fairing blister, car map).
    place_across_seam(img, wm, TUB_WM_CXY_R[0] - wm.width // 2,
                      TUB_WM_CXY_R[1] - wm.height // 2)
    place(img, wm, TUB_WM_CXY[0] - wm.width // 2,
          TUB_WM_CXY[1] - wm.height // 2, right=False)
    for right in (True, False):
        place(img, ff, POD_FF_CXY[0] - ff.width // 2,
              POD_FF_CXY[1] - ff.height // 2, right)
        place(img, cat, POD_CDS_CXY[0] - cat.width // 2,
              POD_CDS_CXY[1] - cat.height // 2, right)
        place(img, ds, TUB_DRIVER_XY[0], TUB_DRIVER_XY[1], right)


def number_panels(img, spec):
    """White panels under iRacing's stamped numbers on the two body blocks
    (the nose block is drawn with the centre panels)."""
    m = NUM_MARGIN
    for nm in ("N1", "N3"):
        bx, by, bw, bh = NUMBER_BLOCKS[nm]
        p = T.number_panel(bw + 2 * m, bh + 2 * m,
                           fill=(T.SPEC_NUM if spec else T.WHITE))
        img.alpha_composite(p, (bx - m, by - m))


def build(spec=False):
    img = Image.new("RGBA", (W, H), tuple(T.SPEC_BODY if spec else BODY) + (255,))
    img.alpha_composite(side_geometry(spec))
    side_text(img, spec)
    centre_panels(img, spec)
    number_panels(img, spec)
    img = img.convert("RGB")
    if spec:
        d = ImageDraw.Draw(img)
        for x, y, w, h in NUMBER_BLOCKS.values():
            d.rectangle([x, y, x + w - 1, y + h - 1], fill=T.SPEC_NUM)
    return img


# --- spec map: the MX-5 v4.1 "Satin-True" (B3) hierarchy, carried over.  NOT
# validated on this car yet - milestone 1 is the colour map and the concept.
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
