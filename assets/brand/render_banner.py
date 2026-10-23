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

"""Render the repository banner from the canonical AINTOLOGIC marks.

Usage: py assets/brand/render_banner.py "iRacing Paints" "Open source" "SIM RACING / CUSTOM LIVERIES" ""
Requires Pillow. Does not build paint files or product assets.
"""
from pathlib import Path
import argparse
from PIL import Image, ImageDraw, ImageFont

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('title')
p.add_argument('status')
p.add_argument('category')
p.add_argument('notice', nargs='?', default='',
               help="optional small notice under the status")
a = p.parse_args()
root = Path(__file__).resolve().parent
BLACK, PAPAYA, WHITE, GRAPHITE = '#0C0C0D', '#FF7A00', '#ECECEC', '#2E3034'
im = Image.new('RGBA', (1800, 600), BLACK)
d = ImageDraw.Draw(im)

def font(size, display=False):
    f = ImageFont.truetype(str(root / 'fonts' / ('Orbitron-Variable.ttf' if display else 'BarlowCondensed-SemiBold.ttf')), size, layout_engine=ImageFont.Layout.BASIC)
    if display:
        f.set_variation_by_axes([800])
    return f

def paste_mark(name, xy, width):
    mark = Image.open(root / name).convert('RGBA')
    mark = mark.resize((width, round(mark.height * width / mark.width)), Image.Resampling.LANCZOS)
    im.alpha_composite(mark, xy)

paste_mark('wordmark.png', (80, 48), 660)
d.text((88, 215), 'Turn AI Into Logic', font=font(32), fill=WHITE)
d.line((80, 282, 1720, 282), fill=GRAPHITE, width=2)
d.text((80, 314), a.title, font=font(76, True), fill=WHITE)
d.text((84, 425), a.category, font=font(32), fill=WHITE)
d.text((1270, 86), a.status.upper(), font=font(38), fill=PAPAYA)
if a.notice:
    d.text((1270, 144), a.notice, font=font(28), fill=WHITE)
paste_mark('checker-rule.png', (180, 480), 1440)
im.convert('RGB').save(root / 'banner.png', optimize=True)
print('Rendered', root / 'banner.png')
