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

"""Open an iRacing template zip and write the layers a paint job needs.

    python tools/template_layers.py 148_template_iR04.zip out/tpl/f4

Writes to OUT_DIR: Wire.png, Number_Blocks.png, Sponsor_Blocks.png, Mask.png,
Car_Mandatory.png, Base.png, Car_decal.png (each on a transparent 2048 canvas,
invisible layers included), overview.png / overview_1k.jpg (wire over the base
with number blocks red, sponsor blocks magenta, a 256-px grid), and prints the
layer tree plus the number / sponsor block rects.  This is how the F4's
number blocks and islands were found (2026-09-14); read the wire picture, then
PROBE - the wire tells you where an island is, never which surface it is.
Needs psd-tools, numpy, scipy, Pillow.
"""
import os, sys, zipfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from psd_tools import PSDImage
from scipy import ndimage

if len(sys.argv) < 3:
    sys.exit(__doc__)
ZIP, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
with zipfile.ZipFile(ZIP) as z:
    z.extractall(OUT)
    psd_name = next(n for n in z.namelist() if n.lower().endswith(".psd"))
psd = PSDImage.open(os.path.join(OUT, psd_name))
W, H = psd.size
print("template", psd_name, "size", psd.size)


def walk(layer, depth=0):
    for l in layer:
        print("%s%s [%s] vis=%s bbox=%s" % ("  " * depth, l.name, l.kind, l.visible, l.bbox))
        if l.is_group():
            walk(l, depth + 1)


def find(name, node=None):
    """Case-insensitive, space/underscore-insensitive layer lookup.

    Template authors are not consistent: the F4 has `Car_Mandatory` / `Base`,
    the RSR `Base Scheme` / `Car Decal`, the Ray FF1600 `Car Mandatory` /
    `base` / `Car_decal`.  Normalising here stops a real layer being reported
    as missing (Ray FF1600, 2026-09-14)."""
    def norm(s):
        return s.lower().replace("_", " ").strip()
    want = norm(name)
    for l in (psd if node is None else node):
        if norm(l.name) == want:
            return l
        if l.is_group():
            r = find(name, l)
            if r is not None:
                return r


def full(layer):
    im = layer.topil().convert("RGBA")
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    canvas.alpha_composite(im, (layer.left, layer.top))
    return canvas


walk(psd)
saved = {}
ALIASES = {"Number Blocks": ["Number Block Locations"], "Sponsor Blocks": ["Sponsor Block Locations"]}
for nm in ["Wire", "Number Blocks", "Sponsor Blocks", "Mask", "Car_Mandatory", "Base", "Car_decal"]:
    L = find(nm)
    for alt in ALIASES.get(nm, []):   # Lotus 79 (2026-09-17): "Number Block Locations"
        L = L if L is not None else find(alt)
    if L is None:
        print("no layer named", nm)
        continue
    saved[nm] = full(L)
    saved[nm].save(os.path.join(OUT, nm.replace(" ", "_") + ".png"))


def blocks(nm):
    if nm not in saved:
        return
    a = np.asarray(saved[nm])
    lab, n = ndimage.label(a[..., 3] > 0)
    print(nm, "components:", n)
    for i, sl in enumerate(ndimage.find_objects(lab)):
        ys, xs = sl
        if (lab[sl] == i + 1).sum() < 50:
            continue
        print("  #%d x=%d y=%d w=%d h=%d" % (i + 1, xs.start, ys.start, xs.stop - xs.start, ys.stop - ys.start))


blocks("Number Blocks")
blocks("Sponsor Blocks")

bg = Image.new("RGBA", (W, H), (120, 120, 120, 255))
if "Base" in saved:
    bg.alpha_composite(saved["Base"])
if "Car_Mandatory" in saved:
    bg.alpha_composite(saved["Car_Mandatory"])


def tint(im, col):
    t = Image.new("RGBA", im.size, col + (0,))
    t.putalpha(im.getchannel("A").point(lambda v: int(v * 0.6)))
    return t


if "Sponsor Blocks" in saved:
    bg.alpha_composite(tint(saved["Sponsor Blocks"], (255, 0, 200)))
if "Number Blocks" in saved:
    bg.alpha_composite(tint(saved["Number Blocks"], (255, 0, 0)))
if "Wire" in saved:
    bg.alpha_composite(saved["Wire"])
d = ImageDraw.Draw(bg)
FONT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts", "ArchivoBlack-Regular.ttf")
f = ImageFont.truetype(FONT, 28)
for v in range(0, W, 256):
    d.line([(v, 0), (v, H - 1)], fill=(0, 255, 255, 160), width=2)
    d.line([(0, v), (W - 1, v)], fill=(0, 255, 255, 160), width=2)
    d.text((v + 4, 4), str(v), font=f, fill=(0, 255, 255, 255))
    d.text((4, v + 4), str(v), font=f, fill=(0, 255, 255, 255))
bg.convert("RGB").save(os.path.join(OUT, "overview.png"))
bg.convert("RGB").resize((1024, 1024), Image.LANCZOS).save(os.path.join(OUT, "overview_1k.jpg"), quality=85)
print("wrote", OUT)
