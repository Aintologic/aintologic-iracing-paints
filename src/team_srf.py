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

"""TEAM SCHEME - SCCA Spec Racer Ford (#23).  Eighth car.  v1.0 LOCKED 2026-09-28.

APPROVED by the designer ON TRACK 2026-09-28; frozen as
releases/spec-racer-ford/v1.0-2026-09-28-claude/ (tag
spec-racer-ford/v1.0-2026-09-28-claude).  Any pixel change is a v1.1.

The AINTOLOGIC team livery (docs/PAINT-SCHEME.md) on the Spec Racer Ford's
panel map (docs/car-maps/spec-racer-ford.md).  Marks come from
src/teamscheme.py and src/sponsors.py; this file holds ONLY this car's
geometry and placements.  Nothing here is inherited from the MX-5, F4, RSR,
Ray, Ferrari, Lotus or HPD - every constant was measured on this car.

    python src/team_srf.py            -> out/ in the project folder
    python src/team_srf.py --here     -> the cwd instead
    python src/team_srf.py --no-spec  -> colour map only

Writes car_<id>.tga (+ car_spec_<id>.tga); see src/personalize.py for
--id / --driver / --logo1 / --logo2 / --out / --profile.

Car #23 (Car Info 2026-09-27: "Car Info: SCCA Spec Racer Ford", #23);
template 23_template_SRF.zip
("Spec Racer.psd", 2048x2048); paint folder %USERPROFILE%\\Documents\\iRacing\\paint\\specracer.

THE RULE OF THIS UV (measured 2026-09-27; mask correlation on eleven island
pairs, 98.8-99.9 %):  the body is mirror-symmetric about texture row 1183.5 -
right y = 2367 - left y, x identical.  Rows > 1183 are the car's LEFT side and
render UPRIGHT from a level left view; rows < 1183 are the RIGHT side and
render ROTATE_180.  On BOTH sides texture +x is REARWARD (coordinate grid:
the left flank reads 1,15 -> 13,14 nose to tail upright, the right flank reads
the same columns upside down).  The UV is unwrapped as if from above: the
centre islands (nose front 5, nose top 10, cockpit surround 11, rear deck 4)
straddle row 1183.5; each side goes shoulder (0/1, 7/6, 3/2) -> crease ->
vertical flank (15/14 + 13/12, 8/9, 17/18) outward from it.
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
import teamscheme as T
import sponsors
import personalize
import setup_check
setup_check.require("srf")

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUSTOMER = personalize.DEFAULT_ID
PAINT_DIR = os.path.join(os.path.expanduser("~"), "Documents", "iRacing",
                         "paint", "specracer")
# personalization, set from the CLI/profile in __main__ before build() runs:
DRIVER_NAME = ""                       # blank driver strip by default
LOGO1 = sponsors.placeholder_logo      # Cats Don't Suck slot
LOGO2 = sponsors.placeholder_logo      # FreakFarm slot
W = H = 2048
MIRROR = 2367                         # right y = MIRROR - left y
CENTRE = MIRROR / 2.0                 # 1183.5, the car's centre line
CENTRE_MASK = os.path.join(_ROOT, "assets", "srf-centre-mask.png")   # islands 5, 10, 4
SIDE_MASK = os.path.join(_ROOT, "assets", "srf-side-mask.png")       # every mirrored body island

# The template ships THREE number-block configurations (PSD groups "Sponsor
# Number Package 1..3").  The sim stamps CONFIG 3 on this account - probed
# 2026-09-27 with all three outlined in different colours: the stamped number
# sat inside the green (config 3) boxes, on the nose top, the tail face and
# the rear flank behind each rear wheel.  Configs 1/2 (door numbers) are NOT
# used; if the designer ever switches package in Paint Shop, re-probe.
NB_CONFIGS = {
    1: {"REAR": (208, 57, 123, 82), "SIDE_R": (1069, 374, 199, 131),
        "NOSE": (202, 1080, 127, 209), "SIDE_L": (1069, 1863, 199, 131)},
    2: {"REAR": (208, 57, 123, 82), "SIDE_R": (1174, 431, 169, 130),
        "NOSE": (251, 1539, 100, 117), "SIDE_L": (1173, 1806, 170, 131)},
    3: {"REAR": (208, 57, 123, 82), "SIDE_R": (1683, 530, 129, 93),
        "NOSE": (572, 1100, 118, 167), "SIDE_L": (1683, 1745, 129, 93)},
}
NUMBER_BLOCKS = NB_CONFIGS[3]

BODY, LINE, ACCENT = T.BLACK, T.WHITE, T.PAPAYA
NUM_MARGIN = 8

# =============================================================================
# PLACEMENTS - APPROVED and locked v1.0 2026-09-28 (commit 5793e17 pixels).
# Side placements are in LEFT texture coordinates (y > 1183).
# Band recipe everywhere: orange = 2x white, small body-colour gaps.
# -----------------------------------------------------------------------------
# Centre stripes.  Nose front face (island 5, x 10 = chin .. 338 = top edge)
# then the nose top (island 10, pointed at x 352) up to the nose number panel.
# The number sits ON the centre line of the nose top, so the node cannot live
# there - it moves to the rear deck (the RSR / Ferrari lesson: the node goes
# where the number is not).  Masked to the centre islands, so the pointed nose
# top tapers the stripes by itself.
STRIPE_CS = (34, 17, 6)               # orange, white, gap (texels)
NOSE_RUNS = [(10, 339), (352, 556)]   # stops at the nose number panel (564..698)

# Rear deck (island 4, x 1326..1885; a shut line at x 1528..1542 is its own
# thin island and stays black).  The AI roundel node sits on the deck behind
# the shut line; the stripes enter it from the front and leave to the tail.
DECK_RUN = (1326, 1885)
DECK_BADGE_D, DECK_BADGE_CX = 150, 1712
RING_GAP, RING_W = 6, 12

# Tail face (the unindexed top-left island: its outline leaks, so it is drawn
# unmasked).  Three vent slots at x 75..195, 345..572, 722..841 (y 78..121) -
# the tail centre is x 458 (slot symmetry).  The rear number block (208..331)
# is left of centre; the cat takes the mirror spot right of centre.
TAIL_CX = 458
TAIL_WM_W, TAIL_WM_CY = 210, 47       # AINTOLOGIC above the centre slot

# Front-fender sash (LEFT texture space), leaning top-forward, just behind the
# front wheel.  It crosses THREE islands that each render differently -
# measured 2026-09-27 with an X-band probe (tools/probe_bands.py 14:X / 12:X /
# 1:X, 20-texel bands) read from a level left view:
#   island 1  shoulder, inner edge ~1360 .. crease ~1690.  x lines up with
#             island 14 across the crease.
#   island 14 a thin strip under the crease (~1790..1860): only ~45 rows but
#             it renders ~2.5x taller per row than island 12 (0.85 vs 0.34 px
#             per row) - a constant texture tilt goes near-vertical here.
#   island 12 the lower flank (~1840..2026) ahead of the door.  Its x is
#             OFFSET from island 14's: the same car position is island-14
#             x = x12 + 0.19 * (730 - x12)  (0 at the rear, ~40 texels at the
#             front), and it renders at 0.46 px/texel against island 14's 0.54.
# v1 drew one texture-space parallelogram through all three and the render
# showed two steps (tried and rejected).  Now the shoulder keeps a texture tilt
# (it reads from above) and the flank piece is evaluated per texel in a common
# car frame (u = island-14 x, v = rendered rows), so the band is one straight
# line from a level side.  Island IDs: assets/srf-sash-islands.png.
SASH_IDS = os.path.join(_ROOT, "assets", "srf-sash-islands.png")
SASH_C1 = 640                         # band centre x at the crease (island 1 / 14)
SASH_TOP_TILT = 0.45                  # shoulder: x per row, top-forward.  0.22 read
                                      # from above as a flat transverse bar - a
                                      # "+" with the centre stripe; 0.45 makes the
                                      # two crowns a forward chevron at the number
SASH_Y0, SASH_CREASE = 1300, 1690
SASH_LEAN = 0.30                      # flank: screen dx per screen dy, bottom rearward
SASH_S14, SASH_S12, SASH_PXU = 0.85, 0.34, 0.54   # px/row (14, 12), px per island-14 texel
SASH_OFF_K, SASH_OFF_X = 0.19, 730    # island-12 -> island-14 x offset
SASH_BANDS = (44, 22, 7)

# AINTOLOGIC on the door - island 9 (x 857..1395 at mid-door, y 1809..2024),
# the flat vertical panel between the wheels.  The only big clean side face:
# configs 1/2 would have put the number here; config 3 leaves it free.
DOOR_WM_W, DOOR_WM_CXY = 460, (1126, 1905)
DRIVER_W, DRIVER_XY = 120, (880, 1826)

# FreakFarm on each REAR fender top (shoulder island 2, x 1325..1862), outboard
# half, so it reads from above, from every rear 3/4 and from behind.
FF_W, FF_CXY = 300, (1600, 1580)

# Cats Don't Suck on the tail face, the mirror spot of the rear number panel.
CDS_D, CDS_CXY = 96, (647, 92)


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


def _ceil(v):
    return int(np.ceil(v - 1e-9))


def _mask(path):
    return np.asarray(Image.open(path).convert("L")) > 127


def masked(layer, path):
    a = np.array(layer)
    a[..., 3] = np.where(_mask(path), a[..., 3], 0)
    return Image.fromarray(a, "RGBA")


def mirror_left(layer):
    """Copy every LEFT-half texel (y > 1183) of `layer` onto the right half
    (y' = MIRROR - y), leaving the left half as it is."""
    a = np.array(layer)
    out = a.copy()
    y0 = int(np.floor(CENTRE)) + 1                 # 1184
    src = a[y0:, :]
    flip = src[::-1]                               # last row first
    d0 = MIRROR - (H - 1)                          # row 2047 -> 320
    dst = out[d0:d0 + flip.shape[0], :]
    take = flip[..., 3] > 0
    dst[take] = flip[take]
    return Image.fromarray(out, "RGBA")


def place(img, el, x, y, left):
    """TEXT / any upright mark.  (x, y) = top-left in LEFT texture space.
    The right side renders ROTATE_180, so the element rotated 180 and dropped
    at the mirrored row lands upright, the same distance from the nose
    (playbook Rule 4)."""
    if left:
        img.alpha_composite(el, (x, y))
    else:
        img.alpha_composite(el.transpose(Image.ROTATE_180),
                            (x, MIRROR - y - el.height))


def _sash_shoulder(spec):
    """Shoulder piece (island 1): a texture-space parallelogram, centre SASH_C1
    at the crease, leaning forward toward the inner edge."""
    K = 3
    big = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    y0, y1 = SASH_Y0, SASH_CREASE + 6
    xc = lambda y: SASH_C1 - SASH_TOP_TILT * (SASH_CREASE - y)
    for a, b, c in _band_rects(0, SASH_BANDS):
        d.polygon([((xc(y0) + a) * K, y0 * K), ((xc(y1) + a) * K, y1 * K),
                   ((xc(y1) + b) * K, y1 * K), ((xc(y0) + b) * K, y0 * K)],
                  fill=_col(c, spec))
    layer = np.array(big.resize((W, H), Image.LANCZOS))
    ids = np.asarray(Image.open(SASH_IDS))
    layer[..., 3] = np.where(ids == 1, layer[..., 3], 0)
    return layer


def _sash_flank(spec, X0=440, X1=900, Y0=1700, Y1=2040, SS=4):
    """Flank piece (islands 14 + 12), evaluated per texel in the car frame
    (u = island-14 x, v = rendered rows below the crease), 4x supersampled."""
    ids = np.asarray(Image.open(SASH_IDS))[Y0:Y1, X0:X1]
    cols = {}
    for x in range(X1 - X0):
        c14 = np.where(ids[:, x] == 14)[0]
        c12 = np.where(ids[:, x] == 12)[0]
        if len(c14) and len(c12):
            cols[x] = (c14.min(), c14.max(), c12.min())
    bands = _band_rects(0, SASH_BANDS)
    out = np.zeros((Y1 - Y0, X1 - X0, 4), np.float32)
    sub = (np.arange(SS) + 0.5) / SS
    for x, (t14, b14, t12) in cols.items():
        col = ids[:, x]
        for sx in sub:
            xf = x + X0 + sx
            for y in np.where((col == 14) | (col == 12))[0]:
                for sy in sub:
                    yf = y + sy
                    if col[y] == 14:
                        u, v = xf, SASH_S14 * (yf - t14)
                    else:
                        u = xf + SASH_OFF_K * max(0.0, SASH_OFF_X - xf)
                        v = SASH_S14 * (b14 + 1 - t14) + SASH_S12 * (yf - t12)
                    du = u - (SASH_C1 + SASH_LEAN / SASH_PXU * v)
                    for a, b, c in bands:
                        if a <= du < b:
                            rgb = T.SPEC_LINE if spec else c
                            out[y, x, :3] += np.array(rgb) / (SS * SS)
                            out[y, x, 3] += 255.0 / (SS * SS)
                            break
    a = out[..., 3:4]
    rgb = np.where(a > 0, out[..., :3] * 255.0 / np.maximum(a, 1e-6), 0)
    layer = np.zeros((H, W, 4), np.uint8)
    layer[Y0:Y1, X0:X1, :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    layer[Y0:Y1, X0:X1, 3] = np.clip(a[..., 0], 0, 255).astype(np.uint8)
    return layer


def side_geometry(spec):
    """The front-fender sash, drawn once in LEFT space and mirrored, masked to
    the body islands."""
    top = _sash_shoulder(spec)
    flank = _sash_flank(spec)
    take = flank[..., 3] > 0
    top[take] = flank[take]
    return masked(mirror_left(Image.fromarray(top, "RGBA")), SIDE_MASK)


def _stripe_run(d, x0, x1, spec):
    for a, b, c in _band_rects(CENTRE, STRIPE_CS):
        d.rectangle([x0, _ceil(a), x1 - 1, _ceil(b) - 1], fill=_col(c, spec))


def centre_line(img, spec):
    """Nose face + nose top up to the number panel; the rear deck through
    the AI roundel node.  Masked to islands 5, 10 and 4."""
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x0, x1 in NOSE_RUNS:
        _stripe_run(d, x0, x1, spec)
    cx, cy = DECK_BADGE_CX, CENTRE
    r_in = DECK_BADGE_D / 2.0 + RING_GAP
    r_ring = r_in + RING_W
    _stripe_run(d, DECK_RUN[0], int(cx - r_ring - RING_GAP), spec)
    _stripe_run(d, int(np.ceil(cx + r_ring + RING_GAP)), DECK_RUN[1], spec)
    img.alpha_composite(masked(layer, CENTRE_MASK))
    # the node: body-colour gap, white ring, body-colour gap, the roundel
    K = 4
    big = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0))
    bd = ImageDraw.Draw(big)
    bd.ellipse([(cx - r_ring) * K, (cy - r_ring) * K, (cx + r_ring) * K,
                (cy + r_ring) * K], fill=_col(LINE, spec))
    bd.ellipse([(cx - r_in) * K, (cy - r_in) * K, (cx + r_in) * K,
                (cy + r_in) * K], fill=tuple(T.SPEC_BODY if spec else BODY) + (255,))
    img.alpha_composite(big.resize((W, H), Image.LANCZOS))
    # letters read from BEHIND the car: image-up -> texture -x (forward)
    badge = S(T.roundel(DECK_BADGE_D)).transpose(Image.ROTATE_90)
    img.alpha_composite(badge, (int(cx - badge.width / 2), int(round(cy - badge.height / 2))))


def door_text(img, spec):
    """AINTOLOGIC + the driver strip on each door (mirrored placement)."""
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    wm = T.wordmark(int(DOOR_WM_W * 0.2), ink=T.WHITE, accent=T.PAPAYA)
    wm = S(wm.resize((DOOR_WM_W, int(wm.height * DOOR_WM_W / wm.width)), Image.LANCZOS))
    ds = S(sponsors.driver_strip(DRIVER_W, DRIVER_NAME, face=T.BLACK,
                                 ink=T.WHITE, accent=T.PAPAYA))
    ff = S(LOGO2(FF_W, ink=T.WHITE, accent=T.PAPAYA))
    for left in (True, False):
        place(img, wm, DOOR_WM_CXY[0] - wm.width // 2, DOOR_WM_CXY[1] - wm.height // 2, left)
        place(img, ds, DRIVER_XY[0], DRIVER_XY[1], left)
        place(img, ff, FF_CXY[0] - ff.width // 2, FF_CXY[1] - ff.height // 2, left)


def tail(img, spec):
    """AINTOLOGIC above the centre vent slot; the cat right of centre, the
    mirror spot of the rear number panel.  The tail face renders upright."""
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    wm = T.wordmark(int(TAIL_WM_W * 0.2), ink=T.WHITE, accent=T.PAPAYA)
    wm = S(wm.resize((TAIL_WM_W, int(wm.height * TAIL_WM_W / wm.width)), Image.LANCZOS))
    img.alpha_composite(wm, (TAIL_CX - wm.width // 2, TAIL_WM_CY - wm.height // 2))
    cat = S(LOGO1(CDS_D))
    img.alpha_composite(cat, (CDS_CXY[0] - cat.width // 2, CDS_CXY[1] - cat.height // 2))


def number_panels(img, spec):
    m = NUM_MARGIN
    for bx, by, bw, bh in NUMBER_BLOCKS.values():
        p = T.number_panel(bw + 2 * m, bh + 2 * m, fill=(T.SPEC_NUM if spec else T.WHITE))
        img.alpha_composite(p, (bx - m, by - m))


def build(spec=False):
    img = Image.new("RGBA", (W, H), tuple(T.SPEC_BODY if spec else BODY) + (255,))
    img.alpha_composite(side_geometry(spec))
    centre_line(img, spec)
    door_text(img, spec)
    tail(img, spec)
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
                  if min(sum(abs(a - b) for a, b in zip(px[xx, yy], c)) for c in ok) > 6)
        print("  %s %s %d bad / %d px" % (name, "DIRTY" if off else "clean", off, w * h))
        if off:
            bad.append(name)
    return bad


# --- spec map: the approved "Satin-True" (B3) hierarchy, carried over.
# Not A/B-validated on this car; the designer accepted it on track (v1.0).
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
    print("number blocks (config 3):")
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
