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

"""Panel-mapping tool. Generates test textures that reveal a car's UV layout.

The whole point: never guess where a graphic will land. Paint a test pattern,
load it in iRacing's car viewer, and read the answer off the car.

Usage
-----
    python src/calibrate.py grid                       8x8 labelled grid (coarse map)
    python src/calibrate.py zones  --psd <template.psd>  the template's own sponsor/
                                                       number blocks, colour-coded
    python src/calibrate.py rects  --rects "A,12,880,706,732" ...
                                                       named rectangles + F-glyph

Every mode writes car_<CUSTOMER_ID>.tga into out/calibrate/ in the project
folder, no matter which folder you run it from, or into the folder given with
--out.
Copy it to
  %USERPROFILE%\\Documents\\iRacing\\paint\\<carfolder>\\   then press Ctrl+R in the car viewer.

Reading the result
------------------
Each patch carries a big label, an F glyph, a RED bar on its texture-TOP edge and
a BLUE bar on its texture-LEFT edge. From where those land you get the panel's
rotation and mirroring in one look:

    F upright,     red on top,   blue on left   -> no transform
    F upside down, red on bottom, blue on right -> 180 deg
    F on its side, red on right,  blue on top   -> 90 deg clockwise
    F mirrored                                  -> the panel is UV-mirrored
                                                   (usually the far side of the car)
"""
import argparse, colorsys, os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# the label font, named here so this tool needs no other module
F_GEO = os.path.join(ROOT, "fonts", "Poppins-Bold.ttf")

SIZE = 2048
BG = (14, 14, 16)


def _label(d, x, y, w, h, text, fill, edges=True):
    d.rectangle([x, y, x + w, y + h], fill=fill)
    fs = max(28, int(min(w, h) * 0.55))
    f = ImageFont.truetype(F_GEO, fs, layout_engine=ImageFont.Layout.BASIC)
    bb = d.textbbox((0, 0), text, font=f)
    lum = 0.299 * fill[0] + 0.587 * fill[1] + 0.114 * fill[2]
    tc = (0, 0, 0) if lum > 140 else (255, 255, 255)
    d.text((x + w / 2 - (bb[2] - bb[0]) / 2, y + h / 2 - (bb[3] - bb[1]) / 2 - bb[1]),
           text, font=f, fill=tc)
    if edges:
        d.rectangle([x, y, x + w, y + max(3, int(h * 0.08))], fill=(210, 40, 40))
        d.rectangle([x, y, x + max(3, int(w * 0.08)), y + h], fill=(40, 90, 220))


def grid(n=8):
    im = Image.new("RGB", (SIZE, SIZE), BG)
    d = ImageDraw.Draw(im)
    cell = SIZE // n
    rows = "ABCDEFGHIJKLMNOP"
    for r in range(n):
        for c in range(n):
            k = r * n + c
            col = tuple(int(v * 255) for v in colorsys.hsv_to_rgb(
                (k * 0.6180339887) % 1.0, 0.9 if k % 2 else 0.5, 0.97 if k % 3 else 0.62))
            _label(d, c * cell, r * cell, cell - 1, cell - 1, f"{rows[r]}{c+1}", col)
    return im


def rects(specs):
    im = Image.new("RGB", (SIZE, SIZE), BG)
    d = ImageDraw.Draw(im)
    for k, (name, x, y, w, h) in enumerate(specs):
        col = tuple(int(v * 255) for v in colorsys.hsv_to_rgb(
            (k * 0.6180339887) % 1.0, 0.9 if k % 2 else 0.55, 0.97 if k % 3 else 0.62))
        _label(d, x, y, w, h, name, col)
    return im


def zones_from_psd(psd_path):
    """Colour-code the template's own Sponsor Blocks / Number Blocks layers."""
    import numpy as np
    from scipy import ndimage
    from psd_tools import PSDImage
    psd = PSDImage.open(psd_path)
    found, specs = {}, []

    def walk(node):
        for layer in node:
            if layer.is_group():
                walk(layer); continue
            if layer.name.strip() in ("Sponsor Blocks", "Number Blocks"):
                img = layer.topil()
                if img is None: continue
                canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
                canvas.paste(img.convert("RGBA"), (layer.left, layer.top))
                found[layer.name.strip()] = canvas
    walk(psd)

    for kind, canvas in found.items():
        prefix = "S" if kind.startswith("Sponsor") else "N"
        a = np.array(canvas)[..., 3] > 20
        lab, n = ndimage.label(a)
        objs = ndimage.find_objects(lab)
        idx = 0
        for i in range(1, n + 1):
            sl = objs[i - 1]
            if sl is None or (lab[sl] == i).sum() < 3000: continue
            y, x = sl
            specs.append((f"{prefix}{idx+1}", x.start, y.start,
                          x.stop - x.start, y.stop - y.start))
            idx += 1
    for s in specs:
        print("%-4s x=%4d y=%4d w=%4d h=%4d" % s)
    return rects(specs)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["grid", "zones", "rects"])
    ap.add_argument("--psd", help="template .psd (zones mode)")
    ap.add_argument("--rects", nargs="*", default=[],
                    help='"NAME,x,y,w,h" entries (rects mode)')
    ap.add_argument("--n", type=int, default=8, help="grid divisions")
    ap.add_argument("--id", default=os.environ.get("IRACING_CUSTOMER_ID", "CUSTOMERID"))
    ap.add_argument("--out", default=os.path.join(ROOT, "out", "calibrate"),
                    help="folder to write the test texture to (default: %(default)s)")
    a = ap.parse_args()

    if a.mode == "grid":
        im = grid(a.n)
    elif a.mode == "zones":
        if not a.psd: ap.error("zones mode needs --psd")
        im = zones_from_psd(a.psd)
    else:
        specs = []
        for r in a.rects:
            p = r.split(",")
            specs.append((p[0], int(p[1]), int(p[2]), int(p[3]), int(p[4])))
        im = rects(specs)

    os.makedirs(a.out, exist_ok=True)
    out = os.path.join(a.out, f"car_{a.id}.tga")
    im.save(out, compression="tga_rle")
    print("wrote", out)


if __name__ == "__main__":
    main()
