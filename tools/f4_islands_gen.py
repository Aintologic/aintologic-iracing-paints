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

"""Generate src/f4_islands.py: LEFT-side island edges per texture column,
read from the template's green island outlines.  Right side = mirror,
y' = 2257 - y (verified on the flank, pod and engine-cover pairs).

    python tools/f4_islands_gen.py <tpl-dir> [out.py]

<tpl-dir> is the folder tools/template_layers.py wrote (it must contain
Wire.png, the PSD "Wire" layer).  [out.py] defaults to src/f4_islands.py.
The template is iRacing's IP and is not shipped; this generated table is."""
import os, sys, numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else "tpl"   # the extracted template (Wire.png)
DEST = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "src", "f4_islands.py")
a = np.asarray(Image.open(os.path.join(OUT, "Wire.png"))).astype(int)
al = a[..., 3] > 40
green = al & (a[..., 1] > 150) & (a[..., 0] < 120) & (a[..., 2] < 120)
gd = ndimage.binary_dilation(green, iterations=1)
lab, n = ndimage.label(~gd)

def runs_of(mask, x0):
    col = np.where(mask[:, x0])[0]
    if not len(col):
        return []
    runs, s, p = [], col[0], col[0]
    for v in col[1:]:
        if v != p + 1:
            runs.append((int(s), int(p))); s = v
        p = v
    runs.append((int(s), int(p)))
    return runs

def comp(x, y):
    return ndimage.binary_dilation(lab == lab[y, x], iterations=1)

ec = comp(1600, 1200)          # left engine cover, B (upper slope) + A (lower flank)
pod = comp(500, 1930)          # left sidepod outer flank
flank = comp(500, 1500)        # left nose/monocoque flank (front part)
nose = comp(500, 1130)         # nose top
podtop = comp(500, 1730)

lines = ['"""FIA F4 (#148) LEFT-side UV island edges, per texture column, generated',
         'from the template wire (tools/f4_islands_gen.py, 2026-09-14).  The',
         'template is not in git; this table is.  RIGHT side = y\' = 2257 - y.',
         'Each entry: x -> (y_top, y_bottom) of the island at that column."""',
         '']
def table(name, mask, x_from, x_to, pick):
    d = {}
    for x0 in range(x_from, x_to, 8):
        r = runs_of(mask, x0)
        v = pick(r)
        if v:
            d[x0] = v
    lines.append("%s = {" % name)
    items = list(d.items())
    for i in range(0, len(items), 6):
        lines.append("    " + ", ".join("%d: (%d, %d)" % (k, v[0], v[1]) for k, v in items[i:i + 6]) + ",")
    lines.append("}")
    print(name, len(d), items[0], items[-1])

# engine cover B: the run that contains y ~1200 (upper slope: top = ridge, bottom = crease)
table("EC_B", ec, 1344, 1960, lambda r: next(((s, e) for s, e in r if s <= 1200 <= e or (s < 1240 and e - s > 40)), None))
# engine cover A: the run below the gap (lower flank), only where separate
table("EC_A", ec, 1344, 1960, lambda r: next(((s, e) for s, e in r if s >= 1330), None))
table("POD", pod, 96, 908, lambda r: (r[0][0], r[-1][1]) if r else None)
table("FLANK_FRONT", flank, 68, 532, lambda r: (r[0][0], r[-1][1]) if r else None)
table("NOSE_TOP", nose, 440, 792, lambda r: (r[0][0], r[-1][1]) if r else None)
table("PODTOP", podtop, 160, 900, lambda r: (r[0][0], r[-1][1]) if r else None)
lines.append("")
lines.append("MIRROR = 2257   # right-side texture y = MIRROR - left y; x is the same")
open(DEST, "w").write("\n".join(lines) + "\n")
print("written", DEST)
