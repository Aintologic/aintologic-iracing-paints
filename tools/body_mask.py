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

"""Write a committed body mask: the union of the UV islands that actually mirror.

    python tools/body_mask.py out/tpl/hpd3 assets/hpd-body-mask.png 0 1 6 7

A car whose two sides are a texture mirror is painted by drawing one side and
reflecting it. That is only safe for the islands that really are mirrors of each
other — on the HPD ARX-01c (2026-09-17) the body islands mirror about row 1197
but the engine-cover flanks, the wing, the endplates and the splitter are packed
independently, so a whole-half reflection splatters paint across them.

This writes a 1-channel PNG of the chosen islands (dilated 3 texels so a stripe
can still run to a real panel edge), which the build commits and uses to mask
the mirrored layer. The templates are not in git, so the mask is — it is
generated data, like tools/island_edges.py's tables, not artwork.

Island indices are the ones `tools/probe_islands.py <mod> <tpl> list` prints.

`leak:x,y,w,h` (Aston Martin Vantage GT3 EVO, 2026-09-28) adds the texels of
that rect that belong to NO listed island - a panel whose green outline leaks
into the background (the Aston's rear deck, like the Ferrari's hood and the
SRF's tail face) - so a build can paint it without touching the real islands
packed next to it.

    python tools/body_mask.py <tpl> assets/amv-centre-mask.png 3 5 14 4 6 leak:1390,940,470,640
"""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_islands import islands

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DILATE = 3

if len(sys.argv) < 4:
    sys.exit(__doc__)
tpl, out = sys.argv[1], sys.argv[2]
want = [int(a) for a in sys.argv[3:] if not a.startswith("leak:")]
leaks = [tuple(map(int, a[5:].split(","))) for a in sys.argv[3:] if a.startswith("leak:")]
if not os.path.isabs(out):
    out = os.path.join(ROOT, out)
lab, isl = islands(tpl)
by_idx = {k: l for k, l, x, y, w, h, a in isl}
missing = [k for k in want if k not in by_idx]
if missing:
    sys.exit("no such island(s): %s" % missing)
m = np.zeros(lab.shape, bool)
for k in want:
    m |= (lab == by_idx[k])
m = ndimage.binary_dilation(m, iterations=DILATE)
if leaks:
    listed = np.isin(lab, [l for k, l, x, y, w, h, a in isl])
    for x, y, w, h in leaks:
        box = np.zeros(lab.shape, bool)
        box[y:y + h, x:x + w] = True
        m |= box & ~listed
os.makedirs(os.path.dirname(out), exist_ok=True)
Image.fromarray((m * 255).astype(np.uint8), "L").save(out, optimize=True)
print("wrote %s - islands %s, dilated %d, %d texels"
      % (out, want, DILATE, int(m.sum())))
