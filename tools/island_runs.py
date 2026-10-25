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

"""Which UV island owns each run of one texture column or row?

    python tools/island_runs.py out/tpl/f296c y:555:0:320 x:1236:0:2048

`y:X:Y0:Y1` walks texture COLUMN X from row Y0 to Y1; `x:Y:X0:X1` walks
texture ROW Y from column X0 to X1.  Prints (island index, first, last) for
every run of 3+ texels, island indices as `tools/probe_islands.py ... list`
prints them, -1 = background / wire line / an island whose outline leaks
(the Ferrari 296 Challenge hood, the Ray FF1600 left sidepod).

Answers the edge questions a probe render is too coarse for: how tall a
band really is at the centre column (the 296 Challenge rear bumper is only
rows 173..210 there), where a wheel-arch cutout starts, whether a mark's
rows are on the island at all (a driver strip at row 1615 on the 296
Challenge sat on nothing; the island starts at 1643).  Written 2026-09-16.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_islands import islands

if len(sys.argv) < 3:
    sys.exit(__doc__)
lab, isl = islands(sys.argv[1])
l2i = {l: k for k, l, *_ in isl}
for spec in sys.argv[2:]:
    axis, fixed, lo, hi = spec.split(":")
    fixed, lo, hi = int(fixed), int(lo), int(hi)
    runs, cur, start = [], None, lo
    for v in range(lo, hi):
        p = lab[v, fixed] if axis == "y" else lab[fixed, v]
        k = l2i.get(int(p), -1)
        if k != cur:
            if cur is not None:
                runs.append((cur, start, v - 1))
            cur, start = k, v
    runs.append((cur, start, hi - 1))
    print(spec, [r for r in runs if r[2] - r[1] >= 2])
