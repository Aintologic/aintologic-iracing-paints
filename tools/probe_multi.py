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

"""Labelled-cell probe over SEVERAL rects at once, on top of the live livery.

    python tools/probe_multi.py team_f4 SR:67,234,838,210:6,2 SL:71,1830,838,193:6,2 ...

Each spec is NAME:x,y,w,h:cols,rows.  Cells are labelled NAME + index
(row-major, 1-based), filled from an 8-colour palette, with a RED bar on the
texture-TOP edge and a BLUE bar on the texture-LEFT edge (playbook Rule 3),
so orientation and mirroring read in one look.  Written 2026-09-14 for the
F4, whose UV has ~20 islands worth probing - one rect per reload (probe.py)
would have cost a reload per island.  The build module must expose
build(spec=False), PAINT_DIR and CUSTOMER.  Read from a LEVEL camera.
Any paint file already there is backed up into out/backup/ first.
"""
import importlib, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from PIL import ImageDraw, ImageFont
from paintfolder import save_tga

FONT = os.path.join(ROOT, "fonts", "ArchivoBlack-Regular.ttf")
PAL = [(255, 0, 220), (0, 255, 90), (255, 230, 0), (0, 200, 255),
       (255, 120, 0), (255, 255, 255), (150, 0, 255), (0, 255, 220)]


def cell(d, x0, y0, w, h, label, col):
    d.rectangle([x0, y0, x0 + w - 1, y0 + h - 1], fill=col)
    d.rectangle([x0, y0, x0 + w - 1, y0 + max(3, h // 10)], fill=(255, 0, 0))
    d.rectangle([x0, y0, x0 + max(3, w // 10), y0 + h - 1], fill=(0, 0, 255))
    fs = max(10, min(h * 2 // 3, int(w * 1.6 / max(2, len(label)))))
    f = ImageFont.truetype(FONT, fs)
    bb = f.getbbox(label)
    d.text((x0 + (w - (bb[2] - bb[0])) // 2 - bb[0], y0 + (h - (bb[3] - bb[1])) // 2 - bb[1]),
           label, font=f, fill=(0, 0, 0))


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    B = importlib.import_module(sys.argv[1])
    img = B.build(spec=False)
    d = ImageDraw.Draw(img)
    k = 0
    for spec in sys.argv[2:]:
        name, rect, grid = spec.split(":")
        x, y, w, h = map(int, rect.split(","))
        cols, rows = map(int, grid.split(","))
        cw, ch = w // cols, h // rows
        for r in range(rows):
            for c in range(cols):
                cell(d, x + c * cw, y + r * ch, cw, ch, "%s%d" % (name, r * cols + c + 1), PAL[k % 8])
                k += 1
        print("%s: %dx%d cells of %dx%d at (%d,%d)" % (name, cols, rows, cw, ch, x, y))
    out = os.path.join(B.PAINT_DIR, "car_%s.tga" % B.CUSTOMER)
    save_tga(img, out)
    print("wrote probe to", out)


if __name__ == "__main__":
    main()
