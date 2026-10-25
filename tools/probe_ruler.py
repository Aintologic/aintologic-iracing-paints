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

"""Ruler probe: thin numbered bands along ONE axis of several rects, one reload.

    python tools/probe_ruler.py team_rsr HOOD:215,1036,529,540:X:44 TAIL:952,12,1087,191:X:60 ...

Each spec is NAME:x,y,w,h:AXIS:step[:c=v].  AXIS X = vertical bands stepping
along texture x (a ruler for "where along the car"); AXIS Y = horizontal bands
stepping along y.  Bands cycle magenta / yellow / cyan with every 5th band
white, each carrying its index (1-based) repeated down its length, so a band
can be named from a foreshortened view.  c=v draws a 3-texel black line at
texture x=v (AXIS X) or y=v (AXIS Y) - use it to check a centre line.
Written 2026-09-14 for the RSR, whose hood / bumper / tail islands needed
"which texel column is the centre line and where does the panel end" rather
than which-island-is-which (that is tools/probe_multi.py).
Any paint file already there is backed up into out/backup/ first.
"""
import importlib, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from PIL import Image, ImageDraw, ImageFont
from paintfolder import save_tga

FONT = os.path.join(ROOT, "fonts", "ArchivoBlack-Regular.ttf")
PAL = [(255, 0, 220), (255, 230, 0), (0, 200, 255)]


def label_img(text, w, h):
    """Black text sized to fit w x h, upright."""
    fs = max(8, min(h, int(w * 1.7 / max(1, len(text)))))
    f = ImageFont.truetype(FONT, fs)
    bb = f.getbbox(text)
    im = Image.new("RGBA", (max(1, bb[2] - bb[0] + 2), max(1, bb[3] - bb[1] + 2)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((1 - bb[0], 1 - bb[1]), text, font=f, fill=(0, 0, 0, 255))
    return im


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    B = importlib.import_module(sys.argv[1])
    img = B.build(spec=False).convert("RGBA")
    d = ImageDraw.Draw(img)
    for spec in sys.argv[2:]:
        parts = spec.split(":")
        name, rect, axis, step = parts[0], parts[1], parts[2].upper(), int(parts[3])
        centre = None
        for p in parts[4:]:
            if p.startswith("c="):
                centre = int(p[2:])
        x, y, w, h = map(int, rect.split(","))
        n = (w if axis == "X" else h) // step
        for i in range(n):
            col = (255, 255, 255) if (i + 1) % 5 == 0 else PAL[i % 3]
            if axis == "X":
                bx, by, bw, bh = x + i * step, y, step, h
            else:
                bx, by, bw, bh = x, y + i * step, w, step
            d.rectangle([bx, by, bx + bw - 1, by + bh - 1], fill=col + (255,))
            lab = label_img(str(i + 1), bw - 2 if axis == "X" else 60, min(bh, 40) if axis == "X" else bh - 2)
            if axis == "X":
                # repeat the number down the band
                k = max(1, bh // (lab.height + 30))
                for j in range(k):
                    yy = by + 10 + j * ((bh - 20) // k)
                    img.alpha_composite(lab, (bx + (bw - lab.width) // 2, yy))
            else:
                k = max(1, bw // (lab.width + 40))
                for j in range(k):
                    xx = bx + 10 + j * ((bw - 20) // k)
                    img.alpha_composite(lab, (xx, by + (bh - lab.height) // 2))
            d = ImageDraw.Draw(img)
        # red bar on the texture-top edge, blue on the texture-left edge (Rule 3)
        d.rectangle([x, y, x + w - 1, y + 5], fill=(255, 0, 0, 255))
        d.rectangle([x, y, x + 5, y + h - 1], fill=(0, 0, 255, 255))
        if centre is not None:
            if axis == "X":
                d.rectangle([centre - 1, y, centre + 1, y + h - 1], fill=(0, 0, 0, 255))
            else:
                d.rectangle([x, centre - 1, x + w - 1, centre + 1], fill=(0, 0, 0, 255))
        print("%s: %d bands of %d along %s from %d" % (name, n, step, axis, x if axis == "X" else y))
    out = os.path.join(B.PAINT_DIR, "car_%s.tga" % B.CUSTOMER)
    save_tga(img.convert("RGB"), out)
    print("wrote probe to", out)


if __name__ == "__main__":
    main()
