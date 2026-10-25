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

"""Hue-coded cell probe over one UV rect, on top of the live livery.

    python tools/probe_affine.py team_mx5 1297,600,355,200 5 4

Paints cols x rows cells over the rect, cell i coloured hue i/N, and writes
the paint file.  Reload the viewer, capture a LEVEL side (or the view you
place from), then run fit_affine.py on the capture to get the texture ->
screen affine for that island.  That affine is what lets a decal be placed
as a SCREEN rectangle (same size, same spot on both sides) and inverse-mapped
onto the texels - see rear_quarter_ff_affine() in src/team_mx5.py.

Why: the MX-5's rear quarters are different islands on the two sides, with
different scale, orientation and anisotropy.  Placing by eye per island
never matched; fitting the mapping did (2026-09-14).
Any paint file already there is backed up into out/backup/ first.
"""
import sys, os, colorsys, importlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from PIL import Image, ImageDraw
from paintfolder import save_tga

if len(sys.argv) < 5:
    sys.exit(__doc__)
B = importlib.import_module(sys.argv[1])
x0, y0, w, h = map(int, sys.argv[2].split(","))
cols, rows = int(sys.argv[3]), int(sys.argv[4])
img = B.build(spec=False)
d = ImageDraw.Draw(img)
N = cols * rows
cw, ch = w // cols, h // rows
for r in range(rows):
    for c in range(cols):
        i = r * cols + c
        rgb = tuple(int(255 * v) for v in colorsys.hsv_to_rgb(i / float(N), 1.0, 1.0))
        d.rectangle([x0 + c * cw + 2, y0 + r * ch + 2, x0 + c * cw + cw - 3, y0 + r * ch + ch - 3], fill=rgb)
out = os.path.join(B.PAINT_DIR, "car_%s.tga" % B.CUSTOMER)
save_tga(img, out)
print("wrote", out, "-", N, "cells of", cw, "x", ch, "texels; reload the viewer and capture")
