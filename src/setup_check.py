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

"""One-time setup check for the cars whose panel shapes come from your own iRacing template.

Six cars need ``tools/first_run.py`` once before their first build. It reads that car's
paint template (iRacing's property, so not included in this project) and writes a few
files the builder needs. If they are missing, ``require()`` stops the build with a plain
message saying what is missing, why, and the exact command to run, instead of a Python
error.

The file lists here must match what ``tools/first_run.py`` writes for each car.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# car -> (display name, template file iRacing publishes, files tools/first_run.py writes)
NEEDS = {
    "f4": ("FIA F4", "148_template_iR04.zip", ["src/f4_islands.py"]),
    "ray": ("Ray FF1600", "163_template_GR22.zip", ["src/ray_islands.py"]),
    "hpd": ("HPD ARX-01c", "39_template_ARX.zip", ["assets/hpd-body-mask.png"]),
    "srf": ("SCCA Spec Racer Ford", "23_template_SRF.zip",
            ["assets/srf-centre-mask.png", "assets/srf-side-mask.png",
             "assets/srf-sash-islands.png"]),
    "sbf2000": ("Skip Barber Formula 2000", "1_template_SBRS.zip",
                ["assets/sbf2000-centre-mask.png", "assets/sbf2000-pod-islands.png"]),
    "amv": ("Aston Martin Vantage GT3 EVO", "206_template_AMGT3.zip",
            ["assets/amv-centre-mask.png"]),
}


def missing(car, root=ROOT):
    """The setup files for `car` that are not on disk yet."""
    return [p for p in NEEDS[car][2]
            if not os.path.isfile(os.path.join(root, *p.split("/")))]


def require(car, root=ROOT):
    """Return quietly if the car's setup step has been run; otherwise explain and exit."""
    gone = missing(car, root)
    if not gone:
        return
    name, template, _ = NEEDS[car]
    sys.stderr.write("\n".join([
        "",
        "The %s needs a one-time setup step before its first build." % name,
        "",
        "Missing: " + ", ".join(gone),
        "",
        "Why: this car's panel shapes come from your own copy of its iRacing paint",
        "template (%s). Templates belong to iRacing, so they aren't" % template,
        "included in this project.",
        "",
        "Run this once, then build again:",
        "",
        "    python tools/first_run.py %s <path to %s>" % (car, template),
        "",
        "Where to get the template: templates/README.md",
        "",
        "",
    ]))
    sys.exit(2)
