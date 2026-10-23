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

"""Tile viewer captures into one sheet, cropped to the car.

    python tools/sheet.py OUT.png in1.png in2.png ... [--cols 3] [--box l t r b]
"""
import argparse
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("out")
ap.add_argument("inputs", nargs="+")
ap.add_argument("--cols", type=int, default=3)
ap.add_argument("--box", type=float, nargs=4, default=[0.15, 0.30, 0.85, 0.72])
ap.add_argument("--tw", type=int, default=700)
a = ap.parse_args()
crops = []
for p in a.inputs:
    im = Image.open(p).convert("RGB")
    w, h = im.size
    l, t, r, b = a.box
    crops.append(im.crop((int(w * l), int(h * t), int(w * r), int(h * b))))
tw = a.tw
th = int(crops[0].height * tw / crops[0].width)
rows = (len(crops) + a.cols - 1) // a.cols
sheet = Image.new("RGB", (tw * a.cols, th * rows), (20, 20, 20))
for i, c in enumerate(crops):
    sheet.paste(c.resize((tw, th), Image.LANCZOS), ((i % a.cols) * tw, (i // a.cols) * th))
sheet.save(a.out)
print("wrote", a.out, sheet.size)
