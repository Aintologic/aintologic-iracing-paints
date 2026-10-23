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

"""Write a committed island-ID mask: each chosen UV island's texels = a value.

    python tools/island_id_mask.py srf/tpl assets/srf-sash-islands.png 1=1 14=14 12=12

Each argument is ISLAND=VALUE (indices as `tools/probe_islands.py ... list`
prints them; VALUE 1..255).  Unlike tools/body_mask.py (a union, one bit) this
keeps the islands apart, so a build can treat each island with its own
texture->car mapping - the Spec Racer Ford's front-fender sash crosses three
islands (shoulder, a stretched flank strip, the lower flank) that each render
at a different scale and offset (2026-09-27).  Islands are dilated DILATE
texels, never into each other.  The templates are not in git, so the mask is:
generated data, not artwork.
"""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_islands import islands

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DILATE = 2

if len(sys.argv) < 4:
    sys.exit(__doc__)
tpl, out = sys.argv[1], sys.argv[2]
pairs = [tuple(int(v) for v in a.split("=")) for a in sys.argv[3:]]
if not os.path.isabs(out):
    out = os.path.join(ROOT, out)
lab, isl = islands(tpl)
by_idx = {k: l for k, l, x, y, w, h, a in isl}
res = np.zeros(lab.shape, np.uint8)
for k, v in pairs:
    if k not in by_idx:
        sys.exit("no such island: %d" % k)
    m = ndimage.binary_dilation(lab == by_idx[k], iterations=DILATE)
    res[m & (res == 0)] = v
os.makedirs(os.path.dirname(out), exist_ok=True)
Image.fromarray(res, "L").save(out, optimize=True)
print("wrote %s - %s, dilated %d" % (out, pairs, DILATE))
