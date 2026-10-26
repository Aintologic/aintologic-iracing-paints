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

"""Labelled-grid probe over the LIVE livery of any build.  Car-agnostic.

    python tools/probe.py team_mx5 grid --n 8 --id 123456
    python tools/probe.py team_mx5 rect 1280 1536 256 256 --n 4 --id 123456
    python tools/probe.py team_mx5 bands 1280 1536 256 256 --n 6 --id 123456

grid   N x N cells over the whole 2048 texture (playbook Rule 3d, elimination)
rect   N x N cells over one rect, labels A1.. row-major
bands  N horizontal bands of distinct colour down one rect (height probe)

Each cell carries its label, a RED bar on its texture-TOP edge and a BLUE
bar on its texture-LEFT edge, so rotation and mirroring read in one look
(playbook Rule 3).  The build module must expose build(spec=False) and
PAINT_DIR.  --id is your customer ID (default: the IRACING_CUSTOMER_ID
setting): the probe is saved as car_<id>.tga, the only name iRacing loads.
Then run view2.py / contact.py and READ FROM A LEVEL CAMERA.  Any paint file
already there is backed up into out/backup/ first.
"""
import argparse, importlib, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from PIL import ImageDraw, ImageFont
from paintfolder import save_tga
import iracingpaths

FONT = os.path.join(ROOT, "fonts", "ArchivoBlack-Regular.ttf")
PAL = [(255, 0, 220), (0, 255, 90), (255, 230, 0), (0, 200, 255),
       (255, 120, 0), (255, 255, 255), (150, 0, 255), (0, 255, 220)]


def cell(d, x0, y0, w, h, label, col, fsize):
    d.rectangle([x0, y0, x0 + w - 1, y0 + h - 1], fill=col)
    d.rectangle([x0, y0, x0 + w - 1, y0 + max(3, h // 12)], fill=(255, 0, 0))
    d.rectangle([x0, y0, x0 + max(3, w // 12), y0 + h - 1], fill=(0, 0, 255))
    f = ImageFont.truetype(FONT, fsize)
    d.text((x0 + w // 6, y0 + h // 6), label, font=f, fill=(0, 0, 0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("module")
    ap.add_argument("mode", choices=["grid", "rect", "bands"])
    ap.add_argument("rect", type=int, nargs="*")
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--outline", action="store_true",
                    help="grid mode: outline cells instead of filling them")
    ap.add_argument("--id", default=os.environ.get("IRACING_CUSTOMER_ID"),
                    help="your iRacing customer ID: the probe is saved as car_<id>.tga "
                         "(default: the IRACING_CUSTOMER_ID setting)")
    a = ap.parse_args()
    B = importlib.import_module(a.module)
    out = iracingpaths.test_paint(B.PAINT_DIR, a.id)
    img = B.build(spec=False)
    d = ImageDraw.Draw(img)
    if a.mode == "grid":
        C = 2048 // a.n
        for r in range(a.n):
            for c in range(a.n):
                col = PAL[(r * 3 + c) % 8]
                lab = "%s%d" % ("ABCDEFGH"[c], r + 1)
                if a.outline:
                    d.rectangle([c * C + 4, r * C + 4, c * C + C - 5, r * C + C - 5],
                                outline=col, width=6)
                    d.text((c * C + 18, r * C + 14), lab,
                           font=ImageFont.truetype(FONT, C // 3), fill=col)
                else:
                    cell(d, c * C, r * C, C, C, lab, col, C // 3)
    else:
        x, y, w, h = a.rect
        if a.mode == "rect":
            cw, ch = w // a.n, h // a.n
            for r in range(a.n):
                for c in range(a.n):
                    cell(d, x + c * cw, y + r * ch, cw, ch,
                         "%s%d" % ("ABCDEFGH"[c], r + 1), PAL[(r * 3 + c) % 8],
                         max(12, min(cw, ch) // 2))
        else:
            bh = h // a.n
            for i in range(a.n):
                cell(d, x, y + i * bh, w, bh, str(i + 1), PAL[i % 8],
                     max(12, bh // 2))
            print("bands:", [(i + 1, y + i * bh, y + (i + 1) * bh - 1)
                             for i in range(a.n)])
    save_tga(img, out)
    print("wrote probe to", out)


if __name__ == "__main__":
    main()
