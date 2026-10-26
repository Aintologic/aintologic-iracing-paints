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

"""Tick probe: thin numbered cross-lines over the LIVE stripe, one reload.

    python tools/probe_ticks.py team_rsr HOOD:215,744:X:1306:25 COVER:153,443:Y:318:25 ... --id 123456

Spec NAME:a,b:AXIS:centre:step.  AXIS X: the stripe runs along x, centred on
row `centre`; a magenta 2-texel line is drawn ACROSS the stripe (centre+-110)
at every x = a, a+step, ...; every 4th tick is cyan and carries its texture
x as a label beside the stripe.  AXIS Y: the same with the roles swapped.
Purpose (RSR, 2026-09-14): measure the RENDERED width of the existing stripe
per texture column, so the band widths can be set per column and the stripe
reads one width through islands of different texel density.
--id is your customer ID (default: the IRACING_CUSTOMER_ID setting): the probe
is saved as car_<id>.tga, the only name iRacing loads.
Any paint file already there is backed up into out/backup/ first.
"""
import importlib, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from PIL import Image, ImageDraw, ImageFont
from paintfolder import save_tga
import iracingpaths

FONT = os.path.join(ROOT, "fonts", "ArchivoBlack-Regular.ttf")
HALF = 110


def main():
    cid = iracingpaths.take_id()
    B = importlib.import_module(sys.argv[1])
    out = iracingpaths.test_paint(B.PAINT_DIR, cid)
    img = B.build(spec=False).convert("RGBA")
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, 22)
    for spec in sys.argv[2:]:
        name, ab, axis, c, step = spec.split(":")
        a, b = map(int, ab.split(","))
        c, step = int(c), int(step)
        for i, v in enumerate(range(a, b + 1, step)):
            big = (i % 4 == 0)
            col = (0, 220, 255, 255) if big else (255, 0, 220, 255)
            if axis.upper() == "X":
                d.rectangle([v, c - HALF, v + 1, c + HALF], fill=col)
                if big:
                    d.text((v - 10, c + HALF + 4), str(v), font=f, fill=col)
            else:
                d.rectangle([c - HALF, v, c + HALF, v + 1], fill=col)
                if big:
                    d.text((c + HALF + 4, v - 10), str(v), font=f, fill=col)
        print(name, "ticks", a, "..", b, "step", step)
    save_tga(img.convert("RGB"), out)
    print("wrote probe to", out)


if __name__ == "__main__":
    main()
