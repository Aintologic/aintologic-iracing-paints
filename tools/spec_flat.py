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

"""Write a uniform spec map: python spec_flat.py R G B   (or 'none' to remove)"""
from PIL import Image
import sys, os

DEST = os.path.join(os.path.expanduser("~"), "Documents", "iRacing", "paint", "mx5 mx52016")
TGA = os.path.join(DEST, "car_spec_CUSTOMERID.tga")
MIP = os.path.join(DEST, "car_spec_CUSTOMERID.mip")

if sys.argv[1] == "none":
    for p in (TGA, MIP):
        if os.path.exists(p):
            os.replace(p, os.path.join(r"scratch", "parked_" + os.path.basename(p)))
    print("spec map removed (parked in scratch)")
else:
    r, g, b = (int(v) for v in sys.argv[1:4])
    Image.new("RGB", (2048, 2048), (r, g, b)).save(TGA, compression="tga_rle")
    print("uniform spec map (%d,%d,%d) -> %s" % (r, g, b, TGA))
