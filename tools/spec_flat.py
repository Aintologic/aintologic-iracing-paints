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

"""Write a uniform spec map: python spec_flat.py R G B --id 123456   (or 'none' to remove)

Writes the MX-5's car_spec_<id>.tga, the only name iRacing loads (--id is your
customer ID; default: the IRACING_CUSTOMER_ID setting).
Backs up any spec map already there into out/backup/ first; 'none' moves it there."""
from PIL import Image
import sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from paintfolder import move_aside, save_tga
import iracingpaths

cid = iracingpaths.take_id()
if len(sys.argv) < 2:
    sys.exit(__doc__)
TGA = iracingpaths.test_paint(iracingpaths.paint_folder("mx5 mx52016"), cid, spec=True)
MIP = os.path.splitext(TGA)[0] + ".mip"

if sys.argv[1] == "none":
    moved = [p for p in (TGA, MIP) if move_aside(p)]
    print("spec map removed (kept in out/backup/)" if moved
          else "no spec map there - nothing to remove")
else:
    r, g, b = (int(v) for v in sys.argv[1:4])
    save_tga(Image.new("RGB", (2048, 2048), (r, g, b)), TGA)
    print("uniform spec map (%d,%d,%d) -> %s" % (r, g, b, TGA))
