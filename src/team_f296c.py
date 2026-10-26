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

"""TEAM SCHEME - Ferrari 296 Challenge (#203).  Fifth car on the scheme.

LOCKED as releases/ferrari-296-challenge/v1.0-2026-09-16/ - APPROVED by
the designer on the render 2026-09-16 (issue #4); the modern-GT adaptation.  Do
not change the design without the designer; a change is a new version, and the
release TGA (not a rebuild) is the lock.  The AINTOLOGIC team livery (docs/PAINT-SCHEME.md)
placed on the 296 Challenge's own panel map
(docs/car-maps/ferrari-296-challenge.md).  Every mark comes from
src/teamscheme.py and src/sponsors.py; this file holds ONLY this car's
geometry and placements.  Structure copied from src/team_rsr.py (a closed
body) with every RSR number deleted - no UV is shared with any other car.

    python src/team_f296c.py            -> out/ in the project folder
    python src/team_f296c.py --here     -> the cwd instead
    python src/team_f296c.py --no-spec  -> colour map only
    python src/team_f296c.py --png      -> also write the flat texture as PNG

Writes car_<id>.tga (+ car_spec_<id>.tga); see src/personalize.py for
--id / --driver / --logo1 / --logo2 / --out / --profile / --design, and
src/design.py for a design's colours, team name and stripe style.

Template: 203_template_F296C.zip
("Ferrari 296 Challenge.psd", 2048x2048).  NOT 173_template_F296.zip - that
zip is "Ferrari 296 GT3.psd", a different car.  Car ID #203 confirmed in
the Car Info panel 2026-09-16.  Paint folder:
%USERPROFILE%\\Documents\\iRacing\\paint\\ferrari296challenge\\.

THE RULE OF THIS UV (measured 2026-09-16, tools/mirror_row.py, 12 island
pairs at 92-100 % mask overlap): the two sides mirror about texture row
1236 - other-side pixel row = 2472 - row, x identical, nose at LOW x.
Rows > 1236 are the car's LEFT (read upright from a level left view: +x
rearward, +y down); rows < 1236 are the car's RIGHT (ROTATE_180).  So the
left side is drawn, the GEOMETRY is mirrored in one operation
(mirror_geometry) and TEXT is composited afterwards, ROTATE_180 on the right
(place).  The hood, windscreen banner, roof and the strip behind the roof
are centred on row 1236 (+x rearward, +y = car's LEFT).  The rear deck lip
and the rear bumper are centred on column ~555 (+x = car's RIGHT).
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
PAINT_DIR = iracingpaths.paint_folder("ferrari296challenge")
# personalization, set from the CLI/profile in __main__ before build() runs:
DRIVER_NAME = ""                       # blank driver strip by default
LOGO1 = sponsors.placeholder_logo      # Cats Don't Suck slot
LOGO2 = sponsors.placeholder_logo      # FreakFarm slot
DESIGN = design.EXAMPLE                # your own design (--design); apply_design() sets it
W = H = 2048
MIRROR = 2472                        # other-side pixel row = MIRROR - row
CL = 1236                            # centre row of hood / banner / roof / E strip

# --- template anchor blocks (PSD "Number Blocks" layer, tools/template_layers.py)
NUMBER_BLOCKS = {"N1": (468, 216, 60, 37),     # rear bumper, left of the fog light
                 "N2": (985, 633, 95, 57),     # RIGHT door, lower front
                 "N3": (879, 1010, 38, 62),    # windscreen banner, car's right end
                 "N4": (615, 1420, 51, 92),    # hood, car's LEFT rear corner
                 "N5": (985, 1785, 95, 57)}    # LEFT door, lower front
PANELLED = ("N1", "N2", "N3", "N4", "N5")    # N3: the sim stamps a plate on the banner too (concept pass 1 render)

BODY, LINE, ACCENT = T.BLACK, T.WHITE, T.PAPAYA


def apply_design(ds):
    """Build with design ds (src/design.py): its colours, lettering and stripe
    style.  The names here predate it: LINE is the design's trim (the thin
    lines and the roof ring), ACCENT its graphic (the wide stripe).  The hood
    vent gap is body colour, so it follows BODY."""
    global DESIGN, BODY, LINE, ACCENT
    DESIGN = ds
    BODY, LINE, ACCENT = ds.body, ds.trim, ds.graphic

# =============================================================================
# PLACEMENTS - locked v1.0, 2026-09-16 (issue #4).  Band recipe: orange =
# 2x white, small body-colour gaps.  Probe references are in the car map.
#
#   * CENTRE STRIPE nose -> hood -> roof, through the ROOF ROUNDEL node (the
#     hood's rear corner carries the number and its centre is the vent) ->
#     the strip behind the roof -> rear deck lip.  The hood's vent sits ON
#     the centre line: painted through, its slats read as ladder rungs, so
#     the stripe stops at the vent and resumes behind it (HOOD_VENT_SKIP).
#     The 296 Challenge's engine bay is an open window: the stripe stops at
#     it and picks up on the lip behind it.  AINTOLOGIC on the wing top.
#   * the SASH on each front fender behind the arch, ahead of the door
#     number panel (lower front of the door).
#   * AINTOLOGIC along the lower door / under the side intake, behind the
#     number; the banner wordmark on the windscreen sun strip; FreakFarm on
#     the rear haunch above the rear wheel; driver strip on the window sill.
#   * Cats Don't Suck: the hood's RIGHT rear corner, balancing the hood
#     number panel on the left corner (reads from the front and from above).
CS = (40, 20, 5)                     # orange, white, gap (texels) - centre-line panels
HOOD_X = (245, 843)                  # nose lip .. cowl
HOOD_VENT_SKIP = (405, 575)          # the three vent slats: painted, they read as ladder rungs - the vent is a deliberate black gap
BANNER_WM_W, BANNER_WM_CXY = 300, (897, CL)
ROOF_X = (950, 1348)                 # starts BEHIND the banner island (853..942 sits inside the roof bbox)
ROOF_BADGE_D, ROOF_BADGE_CX = 180, 1100
RING_GAP, RING_W = 6, 12
ESTRIP_X = (1358, 1484)              # the strip between the rear glass and the engine window
LIP_CX, LIP_Y = 555, (69, 164)       # rear deck lip (island 9): +x = car's right; rows 69..163 at the centre column
TAIL_WM_W, TAIL_WM_CXY = 170, (555, 188)   # rear bumper upper band (island 8): only rows 173..210 at the centre column
# A TEAM NAME at the tail can't use the wordmark's 170x36 box: island 8's top
# edge is an arch - row 172 only for x 504..608, then 176 at x 488/620, 180 at
# 480/630, 185 at 470/640 - and a name that fills the box loses the tops of its
# end letters above it (the wordmark's own sloped shape fits).  These boxes all
# sit under the arch and end at row 206, above the N1 panel margin (row 208);
# the name goes in whichever draws it biggest (_tail_name).
TAIL_NAME_BOXES = (((555, 190), (104, 34)),   # x 503..606, rows 173..206: short names
                   ((555, 192), (134, 30)),   # x 488..621, rows 177..206
                   ((555, 194), (150, 26)))   # x 480..629, rows 181..206: long two-line names
WING_WM_W, WING_WM_CXY = 440, (1698, 70)   # rear wing TOP (island 4 rows 10..129): art ROTATE_180 reads upright from behind / chase cam
                                           # (pass 4 flipped it to upright after misreading a low-res frame; full-res crops of both
                                           # renders showed ROTATE_180 correct - judge text orientation from full-res crops only)
                                           # (rows 129..248 are the trailing face seen from a level dead-rear view: ~3.4x squashed, not used)
HOOD_CDS_D, HOOD_CDS_CXY = 92, (640, MIRROR - 1466)   # mirror of the N4 panel's centre
SASH = dict(xc=850, tilt=0.28, orange=46, white=23, gap=5)   # xc at the top row; left side texture
SASH_Y = (1650, 1905)
NUM_MARGIN = 8
DOOR_WM_W, DOOR_WM_CXY = 440, (1325, 1792)   # 1345 put the final C on the rear arch lip (pass 2 render)
DOOR_DRIVER_W, DOOR_DRIVER_XY = 130, (1030, 1652)   # the side island starts at row ~1644 under the window; 1615 was off-island
Q_FF_W, Q_FF_CXY = 210, (1560, 1655)   # above the rear arch: at x 1700 the island ends at row 1691


def specify(im, rgb=T.SPEC_DECAL):
    out = Image.new("RGBA", im.size, tuple(rgb) + (255,))
    out.putalpha(im.getchannel("A"))
    return out


def _col(c, spec):
    return tuple(T.SPEC_LINE if spec else c) + (255,)


def _band_offsets(widths):
    """[line, stripe, line] offsets; the design's stripe style drops bands
    (classic keeps all three), the rest stay where they were measured."""
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
    """Three bands across the front fender behind the arch, shoulder to sill,
    leaning top-forward (forward = lower x on the left side)."""
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
    the small "made with AINTOLOGIC" line - the doors carry it; the banner,
    tail and wing spots are secondary and pass credit=False."""
    wm = DESIGN.wordmark(int(w * 0.17))
    wm = wm.resize((w, int(wm.height * w / wm.width)), Image.LANCZOS)
    wm = DESIGN.lettering_box(wm, credit=credit)
    return specify(wm) if spec else wm


def _tail_name(spec):
    """A team name at the tail, in the TAIL_NAME_BOXES box that draws it
    biggest (most ink: same letters, so more ink = bigger letters).  Only
    called when the design has a team name; the wordmark keeps TAIL_WM_*."""
    best = None
    for cxy, size in TAIL_NAME_BOXES:
        im = DESIGN.lettering_box(Image.new("RGBA", size), credit=False)
        ink = int(np.asarray(im.getchannel("A"), dtype=np.int64).sum())
        if best is None or ink > best[0]:
            best = (ink, cxy, im)
    _, cxy, im = best
    return (specify(im) if spec else im), cxy


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


def centre_panels(img, spec):
    S = (lambda im: specify(im)) if spec else (lambda im: im)
    d = ImageDraw.Draw(img)
    # hood: one constant stripe, nose lip -> cowl; the vent slots occlude it
    hbands(d, CL, CS, HOOD_X[0], HOOD_X[1], spec, skips=[HOOD_VENT_SKIP])
    # Cats Don't Suck on the hood's right rear corner (reads from the front)
    cat = S(sponsors.logo_slot(LOGO1, HOOD_CDS_D, **DESIGN.logo_colours)).transpose(Image.ROTATE_270)
    img.alpha_composite(cat, (HOOD_CDS_CXY[0] - cat.width // 2, HOOD_CDS_CXY[1] - cat.height // 2))
    # windscreen banner wordmark, read from the front
    bw_ = _wm(BANNER_WM_W, spec, credit=False).transpose(Image.ROTATE_270)   # the credit rides on the doors
    img.alpha_composite(bw_, (BANNER_WM_CXY[0] - bw_.width // 2, BANNER_WM_CXY[1] - bw_.height // 2))
    d = ImageDraw.Draw(img)
    # roof through the roundel node, then the strip behind the rear glass
    cx, cy = ROOF_BADGE_CX, CL
    r_ring = ROOF_BADGE_D / 2.0 + RING_GAP + RING_W
    hbands(d, CL, CS, ROOF_X[0], ROOF_X[1], spec,
           skips=[(int(cx - r_ring - RING_GAP), int(cx + r_ring + RING_GAP))])
    if DESIGN.lines_on:                  # the ring is one of the thin lines
        d.ellipse([cx - r_ring, cy - r_ring, cx + r_ring, cy + r_ring], fill=_col(LINE, spec))
    r_in = ROOF_BADGE_D / 2.0 + RING_GAP
    d.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in],
              fill=tuple(T.SPEC_BODY if spec else BODY) + (255,))
    badge = S(DESIGN.roundel(ROOF_BADGE_D)).transpose(Image.ROTATE_270)
    img.alpha_composite(badge, (cx - badge.width // 2, cy - badge.height // 2))
    d = ImageDraw.Draw(img)
    hbands(d, CL, CS, ESTRIP_X[0], ESTRIP_X[1], spec)
    # rear deck lip behind the engine window, and the tail wordmark
    vbands(d, LIP_CX, CS, LIP_Y[0], LIP_Y[1], spec)
    if DESIGN.team_name is None:
        wm, tcxy = _wm(TAIL_WM_W, spec, credit=False), TAIL_WM_CXY
    else:                                # a name fills its box: keep it under the arch
        wm, tcxy = _tail_name(spec)
    img.alpha_composite(wm, (tcxy[0] - wm.width // 2, tcxy[1] - wm.height // 2))
    ww = _wm(WING_WM_W, spec, credit=False).transpose(Image.ROTATE_180)
    img.alpha_composite(ww, (WING_WM_CXY[0] - ww.width // 2, WING_WM_CXY[1] - ww.height // 2))


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
# unchanged from the MX-5 / F4 / RSR / Ray and locked with v1.0.  No per-car
# A/B was run on this car (see the car map, "Spec map").
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
