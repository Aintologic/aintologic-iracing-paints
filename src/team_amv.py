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

"""TEAM SCHEME - Aston Martin Vantage GT3 EVO (#206).  v1.1 LOCKED 2026-10-10.

APPROVED by the designer ON TRACK 2026-10-10.  Frozen as
releases/aston-martin-vantage-gt3-evo/v1.1-2026-10-10-claude/ (tag
aston-martin-vantage-gt3-evo/v1.1-2026-10-10-claude).  v1.1 = v1.0 (approved
on the render the same day) with the rear-deck stripe as one constant stripe
(DECK_CY).  Any pixel change is a v1.2.  Panel map: docs/car-maps/aston-martin-vantage-gt3-evo.md.  The AINTOLOGIC team
livery (docs/PAINT-SCHEME.md) placed on this car's own panel map.  Every mark
comes from src/teamscheme.py and src/sponsors.py; this file holds ONLY this
car's geometry and placements.  Structure follows src/team_f296c.py (a closed
body); every number here was measured on THIS car - no UV is shared with any
other car.

    python src/team_amv.py            -> out/ in the project folder
    python src/team_amv.py --here     -> the cwd instead
    python src/team_amv.py --no-spec  -> colour map only
    python src/team_amv.py --png      -> also write the flat texture as PNG

Writes car_<id>.tga (+ car_spec_<id>.tga); see src/personalize.py for
--id / --driver / --logo1 / --logo2 / --out / --profile / --design, and
src/design.py for a design's colours, team name and stripe style.

Template: 206_template_AMGT3.zip
("Aston Martin Vantage EVO GT3.psd", 2048x2048).  NOT 150_template_AMV4.zip
(the Vantage GT4) or 64_template_AM1.zip (the DBR9).  Car ID #206 read in the
Car Info panel 2026-09-28 ("Car Info: Aston Martin Vantage GT3 EVO").  Paint
folder: %USERPROFILE%\\Documents\\iRacing\\paint\\amvantageevogt3\\.

THE RULE OF THIS UV (measured 2026-09-28, tools/mirror_row.py, 12 island
pairs at 91.8-100 % mask overlap, all at M = 2520): the two sides mirror
about texture row 1260 - other-side pixel row = 2520 - row, x identical.
Rows > 1260 are the car's LEFT (upright from a level left view, +x
REARWARD, +y down the side); rows < 1260 the RIGHT (ROTATE_180).  Unwrapped
as if from above: the hood, windscreen banner, roof, rear deck and tail are
centred on row 1260 with +y = the car's LEFT; the front bumper is centred on
COLUMN 543.5 with +x = the car's LEFT and +y DOWN the face.
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
setup_check.require("amv")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUSTOMER = personalize.DEFAULT_ID
PAINT_DIR = iracingpaths.paint_folder("amvantageevogt3")
# personalization, set from the CLI/profile in __main__ before build() runs:
DRIVER_NAME = ""                       # blank driver strip by default
LOGO1 = sponsors.placeholder_logo      # Cats Don't Suck slot
LOGO2 = sponsors.placeholder_logo      # FreakFarm slot
DESIGN = design.EXAMPLE                # your own design (--design); apply_design() sets it
W = H = 2048
MIRROR = 2520                        # other-side pixel row = MIRROR - row
CL = 1260                            # centre row: hood / banner / roof / deck / tail
FCX = 543.5                          # centre COLUMN of the front bumper (island 5)
CENTRE_MASK = os.path.join(ROOT, "assets", "amv-centre-mask.png")   # islands 3 5 14 4 6 + the leaky rear deck

# --- template anchor blocks (PSD "Number Blocks" layer, tools/template_layers.py).
# There is ONE number-block layer in this PSD (no config groups).  Probed
# 2026-09-28 with every block painted magenta: the sim stamps N2, N4, N5 and
# N6.  N1 and N3 sit on NO island (texture no mesh uses) - never stamped.
NUMBER_BLOCKS = {"N1": (576, 449, 83, 61),     # unused - no mesh there
                 "N2": (1111, 716, 102, 75),   # RIGHT door, upper middle
                 "N3": (18, 803, 61, 82),      # unused - no mesh there
                 "N4": (342, 1212, 71, 98),    # hood, ON the centre line
                 "N5": (1971, 1316, 66, 86),   # tail, car's LEFT, low
                 "N6": (1111, 1731, 102, 75)}  # LEFT door, upper middle
PANELLED = ("N2", "N4", "N5", "N6")

BODY, LINE, ACCENT = T.BLACK, T.WHITE, T.PAPAYA


def apply_design(ds):
    """Build with design ds (src/design.py): its colours, lettering and stripe
    style.  The names here predate it: LINE is the design's trim (the thin
    lines and the roof ring), ACCENT its graphic (the wide stripe)."""
    global DESIGN, BODY, LINE, ACCENT
    DESIGN = ds
    BODY, LINE, ACCENT = ds.body, ds.trim, ds.graphic

# =============================================================================
# PLACEMENTS - v1.1 (the first concept of 2026-09-28; deck stripe fixed in v1.1).  Band recipe: orange = 2x white,
# small body-colour gaps.  Probe references are in the car map.
#
#   * CENTRE STRIPE bumper (above the grille) -> hood, the hood number panel
#     composited ON TOP of it (RSR rule: one constant stripe, the plate is an
#     occluder) -> windscreen banner AINTOLOGIC -> roof, through the ROOF
#     ROUNDEL node (the hood carries the number on the centre line: RSR /
#     Ferrari lesson) -> the rear window is an open glass hole -> rear deck
#     to the ducktail lip.  Tail: AINTOLOGIC above the centre sensor, the
#     number left, Cats Don't Suck right (the SRF's mirror-spot rule).
#   * the SASH just behind the front-fender gill, across the door shut line.
#   * AINTOLOGIC on the lower door band under the door number; driver strip
#     under the window; FreakFarm on the rear haunch above the rear wheel.
CS = (44, 22, 6)                     # orange, white, gap (texels) - every centre-line panel
BUMPER_Y = [(135, 197), (327, 349)]  # island 5 at the centre column: above and below the grille
HOOD_X = (53, 606)                   # island 3 on row 1260: nose lip .. windscreen base
BANNER_WM_W, BANNER_WM_CXY = 270, (932, CL)     # island 14 = the windscreen sun strip (893..971)
ROOF_X = (985, 1389)                 # island 4 on row 1260, behind the banner
ROOF_BADGE_D, ROOF_BADGE_CX = 200, 1185
RING_GAP, RING_W = 6, 12
DECK_X = (1550, 1862)                # the leaky rear-deck region (masked): x 1550 = just behind the rear window, 1862 = the ducktail lip; x < 1550 is hidden inside the window frame
DECK_CY = [(1550, 1862, 1249, CS)]   # (x0, x1, centre row, widths). v1.1: ONE stripe on row 1249 at the full recipe. v1.0 split it at x 1700 (row 1258, widths (38, 19, 5) behind the seam) on the theory the lip renders ~15 % wider per texel; on the car that drew the lip stripe narrower AND ~9 texels toward the car's left (the designer, 2026-10-10)
TAIL_WM_W, TAIL_WM_CXY = 250, (1894, CL)        # island 6 upper band, above the centre sensor (1924..1939)
TAIL_CDS_D, TAIL_CDS_CXY = 72, (2000, MIRROR - 1359)   # mirror spot of the N5 panel
WING_WM_W, WING_WM_CXY = 440, (1778, 373)       # island 2 (wing) TOP surface = x 1699 (trailing edge) .. ~1860 (leading edge), +x FORWARD; x > ~1870 is the underside (x 1960 rendered nothing)
SASH = dict(xc=700, tilt=0.28, orange=46, white=23, gap=6)   # xc at SASH_Y[0]; LEFT texture space
SASH_Y = (1668, 1930)                # 1650 left a sliver on the fender top above the belt crease
NUM_MARGIN = 8
DOOR_WM_W, DOOR_WM_CXY = 400, (1055, 1866)      # lower door band under N6 (rows 1822..1910)
DOOR_DRIVER_W, DOOR_DRIVER_XY = 130, (950, 1676)   # behind the mirror base (x ~850..900)
Q_FF_W, Q_FF_CXY = 250, (1540, 1652)            # rear haunch; the arch starts at row ~1731 at x 1500


def specify(im, rgb=T.SPEC_DECAL):
    out = Image.new("RGBA", im.size, tuple(rgb) + (255,))
    out.putalpha(im.getchannel("A"))
    return out


def _col(c, spec):
    return tuple(T.SPEC_LINE if spec else c) + (255,)


def _band_offsets(widths):
    """[line, stripe, line] offsets; the design's stripe style drops bands
    (classic keeps all three), the rest stay where they were measured.  Every
    stripe on the car - sash, bumper, hood, roof, rear deck - comes through here."""
    ow, ww, g = widths
    return DESIGN.bands([(-ow / 2.0 - g - ww, -ow / 2.0 - g, LINE),
                         (-ow / 2.0, ow / 2.0, ACCENT),
                         (ow / 2.0 + g, ow / 2.0 + g + ww, LINE)])


def _cut(lo, hi, skips):
    x = lo
    for a, b in sorted(skips):
        if a > x:
            yield x, min(a, hi)
        x = max(x, b)
    if x < hi:
        yield x, hi


def hbands(d, cy, widths, x0, x1, spec, skips=()):
    """White|orange|white running along x, centred on row cy."""
    for lo, hi, c in _band_offsets(widths):
        for a, b in _cut(x0, x1, skips):
            d.rectangle([a, int(round(cy + lo)), b - 1, int(round(cy + hi)) - 1], fill=_col(c, spec))


def vbands(d, cx, widths, y0, y1, spec, skips=()):
    """White|orange|white running along y, centred on column cx."""
    for lo, hi, c in _band_offsets(widths):
        for a, b in _cut(y0, y1, skips):
            d.rectangle([int(round(cx + lo)), a, int(round(cx + hi)) - 1, b - 1], fill=_col(c, spec))


def place(img, el, x, y, right):
    """TEXT: (x, y) top-left in LEFT texture space; ROTATE_180 at the
    mirrored rows on the right, so it reads upright on both sides."""
    if right:
        img.alpha_composite(el.transpose(Image.ROTATE_180), (x, MIRROR + 1 - y - el.height))
    else:
        img.alpha_composite(el, (x, y))


def mirror_geometry(layer):
    """Reflect a LEFT-side-only layer (rows > CL) to the right: row -> MIRROR - row."""
    a = np.array(layer)
    flipped = np.zeros_like(a)
    ys = np.arange(CL + 1, H)
    dst = MIRROR - ys
    ok = (dst >= 0) & (dst < H)
    flipped[dst[ok]] = a[ys[ok]]
    return Image.alpha_composite(layer, Image.fromarray(flipped, "RGBA"))


def draw_sash(d, spec, k=1):
    """Three bands across the rear of the front fender / front of the door,
    window line to sill, leaning top-forward (forward = lower x)."""
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


def side_geometry(spec):
    K = 3
    big = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0))
    draw_sash(ImageDraw.Draw(big), spec, k=K)
    return mirror_geometry(big.resize((W, H), Image.LANCZOS))


def _wm(w, spec, credit=False):
    """The big lettering at width w: the wordmark in the design's colours, or
    the team name in the same box (DESIGN.lettering_box).  credit=True adds
    the small "made with AINTOLOGIC" line - the doors carry it; the windscreen
    banner, tail and wing spots are secondary and pass credit=False."""
    wm = DESIGN.wordmark(int(w * 0.17))
    wm = wm.resize((w, int(wm.height * w / wm.width)), Image.LANCZOS)
    wm = DESIGN.lettering_box(wm, credit=credit)
    return specify(wm) if spec else wm


def side_text(img, spec):
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    wm = _wm(DOOR_WM_W, spec, credit=True)
    ff = S(sponsors.logo_slot(LOGO2, Q_FF_W, ink=DESIGN.lettering, accent=DESIGN.graphic))
    ds = S(sponsors.driver_strip(DOOR_DRIVER_W, DRIVER_NAME, face=DESIGN.body,
                                 ink=DESIGN.lettering, accent=DESIGN.graphic))
    for right in (False, True):
        place(img, wm, DOOR_WM_CXY[0] - wm.width // 2, DOOR_WM_CXY[1] - wm.height // 2, right)
        place(img, ff, Q_FF_CXY[0] - ff.width // 2, Q_FF_CXY[1] - ff.height // 2, right)
        place(img, ds, *DOOR_DRIVER_XY, right=right)


def number_panels(img, spec):
    m = NUM_MARGIN
    for key in PANELLED:
        bx, by, bw, bh = NUMBER_BLOCKS[key]
        npnl = T.number_panel(bw + 2 * m, bh + 2 * m, fill=(T.SPEC_NUM if spec else T.WHITE))
        img.alpha_composite(npnl, (bx - m, by - m))


def _centred(img, el, cxy):
    img.alpha_composite(el, (int(round(cxy[0] - el.width / 2.0)), int(round(cxy[1] - el.height / 2.0))))


def centre_stripes(spec):
    """Every centre-line stripe on one layer, masked to the centre islands
    (hood, bumper, banner, roof, tail) + the leaky rear deck, so nothing
    lands on a neighbouring island packed inside those bboxes."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for y0, y1 in BUMPER_Y:
        vbands(d, FCX, CS, y0, y1, spec)
    hbands(d, CL, CS, HOOD_X[0], HOOD_X[1], spec)
    cx = ROOF_BADGE_CX
    r_ring = ROOF_BADGE_D / 2.0 + RING_GAP + RING_W
    hbands(d, CL, CS, ROOF_X[0], ROOF_X[1], spec,
           skips=[(int(cx - r_ring - RING_GAP), int(cx + r_ring + RING_GAP))])
    for x0, x1, cy, cs in DECK_CY:
        hbands(d, cy, cs, x0, x1, spec)
    m = Image.open(CENTRE_MASK).convert("L")
    lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.getchannel("A")), np.asarray(m)), "L"))
    return lay


def centre_panels(img, spec):
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    img.alpha_composite(centre_stripes(spec))
    d = ImageDraw.Draw(img)
    # roof roundel node: body gap, white ring, gap, badge (reads from the front)
    cx, cy = ROOF_BADGE_CX, CL
    r_ring = ROOF_BADGE_D / 2.0 + RING_GAP + RING_W
    if DESIGN.lines_on:                  # the ring is one of the thin lines
        d.ellipse([cx - r_ring, cy - r_ring, cx + r_ring, cy + r_ring], fill=_col(LINE, spec))
    r_in = ROOF_BADGE_D / 2.0 + RING_GAP
    d.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in],
              fill=tuple(T.SPEC_BODY if spec else BODY) + (255,))
    _centred(img, S(DESIGN.roundel(ROOF_BADGE_D)).transpose(Image.ROTATE_270), (cx, cy))
    # windscreen banner, reads from the front (the credit rides on the doors)
    _centred(img, _wm(BANNER_WM_W, spec, credit=False).transpose(Image.ROTATE_270), BANNER_WM_CXY)
    # tail: wordmark above the centre sensor, reads from behind (+x down, +y = car's left)
    _centred(img, _wm(TAIL_WM_W, spec, credit=False).transpose(Image.ROTATE_90), TAIL_WM_CXY)
    _centred(img, S(sponsors.logo_slot(LOGO1, TAIL_CDS_D, **DESIGN.logo_colours)).transpose(Image.ROTATE_90),
             TAIL_CDS_CXY)
    # rear wing top (provisional)
    _centred(img, _wm(WING_WM_W, spec, credit=False).transpose(Image.ROTATE_270), WING_WM_CXY)


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


# --- spec map: the approved "Satin-True" (B3) hierarchy, carried over
# unchanged.  NOT validated on this car yet (first milestone = concept only).
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
    for key in PANELLED:
        bx, by, bw, bh = NUMBER_BLOCKS[key]
        p = np.asarray(T.number_panel(bw + 2 * m, bh + 2 * m).getchannel("A")) > 0
        cov[by - m:by - m + p.shape[0], bx - m:bx - m + p.shape[1]] |= p
    return cov


def spec_from_colour(img, variant=SPEC_DEFAULT):
    """The design's finishes go in through DESIGN.spec_values (body, graphic
    -> "orange", trim -> "white"); the example scheme gets B3 unchanged.  The
    number panels keep the car's own B3 white in every design."""
    P0 = SPEC_VARIANTS[variant]
    P = DESIGN.spec_values(P0)
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
    m = DESIGN.stripe_mask(a)            # papaya's hue test in the example scheme
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
