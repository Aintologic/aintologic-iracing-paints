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

"""Measure a car's UV mirror row instead of guessing it from bounding boxes.

    python tools/mirror_row.py scratch/ray/tpl 2040 2065 6/5 2/1 13/12 20/19

For each island pair (indices as `tools/probe_islands.py ... list` prints
them) it flips the second island's mask about every candidate row M in the
given range and reports the M with the most overlap, plus the median over all
pairs.  Bounding boxes are ±2 because the wire outline is antialiased and
dilated, and the template author's number / sponsor boxes disagree with each
other; the mask correlation does not.  Written for the Ray FF1600 (2026-09-14),
where twelve pairs all peaked at 2051-2052 with 98-100% overlap.
"""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

if len(sys.argv) < 5:
    sys.exit(__doc__)
TPL, LO, HI = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
PAIRS = [tuple(int(v) for v in s.split("/")) for s in sys.argv[4:]]

# Same island finder as every other probe (green wire outlines, or the Mask
# layer when the wire has no green - HPD ARX-01c, 2026-09-17), so the indices
# here are the ones `tools/probe_islands.py ... list` prints.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_islands import islands
lab, isl = islands(TPL)
rows = [(area, l) for k, l, x, y, w, h, area in isl]

H = lab.shape[0]
best_all = []
for ra, rb in PAIRS:
    A = lab == rows[ra][1]
    B = lab == rows[rb][1]
    best, bestm = -1, None
    for M in range(LO, HI + 1):
        idx = M - np.arange(H)
        ok = (idx >= 0) & (idx < H)
        Bf = np.zeros_like(B)
        Bf[ok] = B[idx[ok]]
        ov = int((A & Bf).sum())
        if ov > best:
            best, bestm = ov, M
    print("islands %3d / %-3d  best M = %d  overlap %d / %d (%.1f%%)"
          % (ra, rb, bestm, best, A.sum(), 100.0 * best / max(1, A.sum())))
    best_all.append(bestm)
print("median M = %d   (left y = M - right y, x identical)"
      % int(np.median(best_all)))
