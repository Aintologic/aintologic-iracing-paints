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

"""Paint the WHOLE texture as a labelled coordinate grid, over the live build.

    python tools/coord_grid.py team_hpd [cell]

Every `cell`-texel square (default 128) is tinted in a 4-colour checker so
neighbours always differ, and carries its own texture coordinate as "COL,ROW"
in units of `cell` — so a render can be read back to exact texels ANYWHERE on
the car. A red bar marks each cell's texture-TOP edge and a blue bar its
texture-LEFT edge, so orientation is readable per cell (playbook Rule 3).

Why this and not a per-island probe: on a car with many islands, one reload of
this answers *every* "which texel is this point on the car" question at once,
instead of a probe per question. It is how the HPD ARX-01c's whole layout was
settled in one pass (2026-09-17) — mirror row, which half is which side, which
direction +x runs, and where each panel lives — on a car whose template Wire
layer is blank. Read it from LEVEL side / dead front / dead rear / top frames
(playbook Rule 3a), then zoom with tools/zoom.py to read the labels.

Coordinates are COL,ROW in units of `cell`; texel x = COL * cell.
The build module must expose build(spec=False), PAINT_DIR and CUSTOMER.
"""
import importlib, os, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
FONT = os.path.join(ROOT, "fonts", "ArchivoBlack-Regular.ttf")
TINTS = [(250, 250, 250), (255, 210, 120), (150, 235, 255), (200, 255, 190)]


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    B = importlib.import_module(sys.argv[1])
    cell = int(sys.argv[2]) if len(sys.argv) > 2 else 128
    img = B.build(spec=False).convert("RGB")
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, int(cell * 0.30))
    n = img.width // cell
    for r in range(n):
        for c in range(n):
            x0, y0 = c * cell, r * cell
            d.rectangle([x0, y0, x0 + cell - 1, y0 + cell - 1],
                        fill=TINTS[(r % 2) * 2 + (c % 2)])
            d.rectangle([x0, y0, x0 + cell - 1, y0 + max(2, cell // 12)],
                        fill=(220, 0, 0))                       # texture TOP
            d.rectangle([x0, y0, x0 + max(2, cell // 12), y0 + cell - 1],
                        fill=(0, 0, 220))                       # texture LEFT
            t = "%d,%d" % (c, r)
            bb = f.getbbox(t)
            d.text((x0 + cell / 2 - (bb[2] - bb[0]) / 2 - bb[0],
                    y0 + cell / 2 - (bb[3] - bb[1]) / 2 - bb[1]),
                   t, font=f, fill=(0, 0, 0))
    out = os.path.join(B.PAINT_DIR, "car_%s.tga" % B.CUSTOMER)
    img.save(out, compression="tga_rle")
    print("wrote", out, "- cell", cell, "->", n, "x", n,
          "; labels are COL,ROW in units of", cell)


if __name__ == "__main__":
    main()
