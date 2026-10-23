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

"""Read the band edge straight off the designer's approved side flat.

No more eyeballing.  For every column of the flat, find the top of the
continuous cream / orange / teal lower field, then convert to flank-local with
the transform measured by the ruler probe on the car:

    flank_x = (flat_x - 451) * 0.913     flank_y = (flat_y - 300) * 0.847
"""
import os
from PIL import Image

FLAT = (r"the repo\Area51"
        r"\AINTOLOGIC-MX5-Claude-Code-Handoff-v1\views"
        r"\aintologic-mx5-technical-flat-left-side-v1.png")
BAND = [(243, 232, 210), (255, 100, 25), (95, 168, 174), (23, 104, 121),
        (247, 238, 220), (240, 226, 200)]
TOL = 46
RUN = 18            # a real band is a long vertical run, not a decal edge


def is_band(p):
    return any(sum(abs(a - b) for a, b in zip(p[:3], c)) < TOL for c in BAND)


im = Image.open(FLAT).convert("RGB")
W, H = im.size
px = im.load()
print("flat", W, H)

prof = []
for x in range(0, W, 8):
    top = None
    for y in range(int(H * 0.30), int(H * 0.92)):
        if all(is_band(px[x, yy]) for yy in range(y, min(H, y + RUN))):
            top = y
            break
    prof.append((x, top))

# report in flat coords and in flank coords
print("flat_x  flat_y   flank_x  flank_y")
for x, y in prof:
    fx = (x - 451) * 0.913
    if y is None:
        print("%5d   none   %7.0f      -" % (x, fx))
    else:
        fy = (y - 300) * 0.847
        print("%5d %6d   %7.0f  %7.0f" % (x, y, fx, fy))
