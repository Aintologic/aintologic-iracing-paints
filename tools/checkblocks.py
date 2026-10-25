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

"""Check that the MX-5's three number blocks are left plain black.

    python tools/checkblocks.py [paint.tga]

Written for the first MX-5 liveries (v1.x), which left the blocks black. The
team scheme paints white number panels into N1 and N2, so a team-scheme MX-5
reports those two DIRTY by design. Without a file it reads
out/car_CUSTOMERID.tga in the project folder (a builder's default output when
run from there).
"""
from PIL import Image
import numpy as np, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLACK = (11, 12, 14)
BLOCKS = {"N1": (493, 577, 123, 105), "N2": (493, 1810, 123, 105), "N3": (777, 214, 89, 74)}
p = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "out", "car_CUSTOMERID.tga")
if not os.path.isfile(p):
    sys.exit("no paint file at %s - give the path of the paint to check" % p)
a = np.asarray(Image.open(p).convert("RGB")).astype(int)
bad = 0
for n, (x, y, w, h) in BLOCKS.items():
    sub = a[y:y+h, x:x+w]
    d = np.abs(sub - np.array(BLACK)).sum(2)
    n_off = int((d > 6).sum())
    tot = w * h
    if n_off:
        cols = np.unique(sub[d > 6].reshape(-1, 3), axis=0)[:4]
        print("%s DIRTY  %d/%d px  sample colours %s" % (n, n_off, tot, cols.tolist()))
        bad += 1
    else:
        print("%s clean  0/%d px" % (n, tot))
print("RESULT:", "FAIL" if bad else "PASS")
