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

"""Top-down sweep: tip the camera to look straight down (+600 = top-down), then
walk around the car in --step drags, cropping each frame like tools/walk.py.

    python tools/walk_top.py --prefix t_ --step 65 --frames 8

The sweep starts from wherever the camera is pointing; this tool never
reloads, and a reload would not help: Ctrl+R does NOT reset the camera (the
RSR, Ray and Ferrari car maps say so, and a check on 2026-10-24 left the pose
pixel-identical). Read frame 0 to see where the sweep began.

Writes <prefix><i>.png (the whole iRacing window) and <prefix><i>.jpg (the 3D
view, cut a little taller than walk.py's crop: from 12% down, 76% of the
window's height). Tile the .jpg frames with tools/contact_sheet.py.
"""
import sys

import walk

# the 3D view inside the window, as fractions: left, top, width, height
CROP = (0.03, 0.12, 0.94, 0.76)

if __name__ == "__main__":
    sys.exit(walk.run(None, "Top-down sweep around the car; saves every frame.",
                      {"prefix": "t_", "frames": 8, "drag_y": 600},
                      CROP, with_reload=False))
