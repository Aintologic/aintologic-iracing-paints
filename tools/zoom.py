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

"""Crop the car out of a viewer capture and upscale it, for reading detail.

    python tools/zoom.py scratch/contact/1.png scratch/z1.png [--box l t r b]

Default box is the middle of the 3D pane where the car sits.  Output is
resized to 1400 wide so Desktop Commander's read_file can return it.
"""
import argparse
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("out")
ap.add_argument("--box", type=float, nargs=4, default=[0.10, 0.28, 0.90, 0.78],
                help="fractions of width/height: left top right bottom")
a = ap.parse_args()
im = Image.open(a.src).convert("RGB")
w, h = im.size
l, t, r, b = a.box
c = im.crop((int(w * l), int(h * t), int(w * r), int(h * b)))
c = c.resize((1400, int(c.height * 1400 / c.width)), Image.LANCZOS)
c.save(a.out)
print("wrote", a.out, c.size)
