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

"""Personalization for the team-scheme builders: one code path for every car.

Every ``src/team_*.py`` builder exposes the same options through this module:

    --id       the iRacing customer ID that names the output files (car_<id>.tga)
    --driver   the name in the cockpit driver strip (blank strip when omitted)
    --logo1    logo spot 1
    --logo2    logo spot 2
    --out      the output folder (default: out in the project folder, wherever
               the builder is run from)
    --profile  load a saved profile from profiles/<name>.json (local only)

Defaults are neutral: a placeholder ID in the filename, a blank driver strip,
and a code-drawn "YOUR LOGO" placeholder in both slots. Nobody's personal mark
is ever the default.

A logo slot value is either a path to an image file, or one of the built-in
example-mark tokens ``placeholder`` / ``cats_dont_suck`` / ``freakfarm`` (the
last two are drawn by src/sponsors.py). ``resolve_logo`` turns a slot value into
a ``f(width, **kwargs) -> RGBA`` callable that the builders drop in exactly where
their fixed per-car logo placements expect it.

profiles/ is ignored by git: it holds your customer ID and name, so it stays on
your computer. The example tokens let a profile reproduce a build without
storing any image path.
"""
import json
import os

import sponsors

DEFAULT_ID = "CUSTOMERID"
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PROFILES = os.path.join(_ROOT, "profiles")
_TOKENS = {"placeholder": sponsors.placeholder_logo,
           "cats_dont_suck": sponsors.cats_dont_suck,
           "freakfarm": sponsors.freakfarm}


class Config:
    """The resolved per-build personalization."""

    def __init__(self, id, driver, logo1, logo2, out_dir):
        self.id = id
        self.driver = driver
        self.logo1 = logo1
        self.logo2 = logo2
        self.out_dir = out_dir


def add_args(ap):
    """Add the shared personalization options to an ArgumentParser."""
    ap.add_argument("--id", default=None,
                    help="iRacing customer ID for the output filename (default: a placeholder)")
    ap.add_argument("--driver", default=None,
                    help="driver name for the cockpit strip (blank strip if omitted)")
    ap.add_argument("--logo1", default=None,
                    help="logo spot 1: an image file, or a token "
                         "placeholder/cats_dont_suck/freakfarm")
    ap.add_argument("--logo2", default=None,
                    help="logo spot 2: an image file, or a token "
                         "placeholder/cats_dont_suck/freakfarm")
    ap.add_argument("--out", default=None,
                    help="output folder (default: out in the project folder)")
    ap.add_argument("--profile", default=None,
                    help="load a saved profile for the above (local only)")


def default_out_dir():
    """The project's own out folder (git ignores it), whichever folder the
    builder is run from."""
    return os.path.join(_ROOT, "out")


def load_profile(name):
    """Read profiles/<name>.json and return its dict."""
    path = os.path.join(_PROFILES, name + ".json")
    if not os.path.isfile(path):
        raise SystemExit("no such profile: %s" % path)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def profile_id(name, default=DEFAULT_ID):
    """The customer ID stored in a profile."""
    try:
        return load_profile(name).get("id", default)
    except SystemExit:
        return default


def _aspect(mark):
    """Height / width of a code-drawn mark."""
    im = mark(1000)
    return im.height / float(im.width)


def resolve_logo(spec, slot=None):
    """Turn a logo-slot value into a ``f(width, **kwargs) -> RGBA`` callable.

    ``None`` / ``""`` / ``"placeholder"`` -> the neutral YOUR LOGO placeholder;
    ``"cats_dont_suck"`` / ``"freakfarm"`` -> the code-drawn example marks;
    anything else is treated as a path to an image file. A user image is fitted
    inside the shape its slot was designed for, so it never spills off its panel:
    logo spot 1 was laid out for the near-round example mark, logo spot 2 for the
    wide YOUR LOGO plate.
    """
    if spec in (None, ""):
        return sponsors.placeholder_logo
    if spec in _TOKENS:
        return _TOKENS[spec]
    box = {1: sponsors.cats_dont_suck, 2: sponsors.placeholder_logo}.get(slot)
    return sponsors.image_logo(spec, _aspect(box) if box else None)


def resolve(args):
    """Resolve CLI args (+ an optional profile) into a Config.

    CLI values override profile values; a profile fills in anything left at its
    default. Refuses any customer ID listed in the profile's ``protect_ids``.
    """
    prof = load_profile(args.profile) if args.profile else {}
    cid = args.id if args.id is not None else prof.get("id", DEFAULT_ID)
    driver = args.driver if args.driver is not None else prof.get("driver", "")
    logo1 = args.logo1 if args.logo1 is not None else prof.get("logo1")
    logo2 = args.logo2 if args.logo2 is not None else prof.get("logo2")
    protect = set(prof.get("protect_ids", []))
    if str(cid) in protect:
        raise SystemExit("refusing to build with protected ID %s (see the profile's "
                         "protect_ids)" % cid)
    return Config(str(cid), driver, resolve_logo(logo1, 1), resolve_logo(logo2, 2), args.out)
