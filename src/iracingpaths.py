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

"""Where iRacing looks for paint files on this computer, and the name it loads.

    documents_folder()          the real Documents folder (Windows lets people
                                move it, into OneDrive for example)
    paint_folder(car_folder)    <Documents>/iRacing/paint/<car_folder>
    take_id(argv)               take --id <customer ID> out of a command line
    test_paint(folder, cid)     the full path of car_<id>.tga in that folder,
                                once the ID and the folder are checked

The builders name their paint folder with paint_folder(). The measuring tools
(the probes, coord_grid.py, spec_flat.py and spec_ladder.py) take --id and
write through test_paint(), because iRacing loads only car_<customer ID>.tga:
a test pattern under any other name never shows on the car.
tools/check_setup.py reports the paint folder with documents_folder().

Standard library only: tools/check_setup.py imports it before any add-on is
installed.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILES = os.path.join(ROOT, "profiles")
ID_SETTING = "IRACING_CUSTOMER_ID"      # the same setting src/calibrate.py reads


def documents_folder():
    """The real Documents folder.  Windows lets people move it (into OneDrive,
    for example), so ask Windows where it is; anywhere else, or if that fails,
    the Documents folder in the home folder."""
    if os.name == "nt":
        try:
            import ctypes
            from ctypes import wintypes

            class GUID(ctypes.Structure):
                _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD),
                            ("Data3", wintypes.WORD), ("Data4", ctypes.c_ubyte * 8)]

            # FOLDERID_Documents = {FDD39AD0-238F-46AF-ADB4-6C85480369C7}
            folder = GUID(0xFDD39AD0, 0x238F, 0x46AF,
                          (ctypes.c_ubyte * 8)(0xAD, 0xB4, 0x6C, 0x85, 0x48, 0x03, 0x69, 0xC7))
            get = ctypes.windll.shell32.SHGetKnownFolderPath
            get.argtypes = [ctypes.POINTER(GUID), wintypes.DWORD, wintypes.HANDLE,
                            ctypes.POINTER(ctypes.c_wchar_p)]
            get.restype = ctypes.c_long
            path = ctypes.c_wchar_p()
            ok = get(ctypes.byref(folder), 0, None, ctypes.byref(path)) == 0
            found = path.value if ok else None
            ctypes.windll.ole32.CoTaskMemFree(path)     # Windows asks for this either way
            if found:
                return found
        except Exception:
            pass
    return os.path.join(os.path.expanduser("~"), "Documents")


def paint_folder(car_folder):
    """One car's folder in iRacing's paint folder, e.g. paint_folder("lotus79")."""
    return os.path.join(documents_folder(), "iRacing", "paint", car_folder)


def take_id(argv=None):
    """Take `--id <customer ID>` (or `--id=<customer ID>`) out of `argv`
    (default sys.argv) and return the ID, so the tool reads the rest of its
    command line exactly as before.  Without one: the IRACING_CUSTOMER_ID
    setting if there is one, else None."""
    argv = sys.argv if argv is None else argv
    cid = None
    i = 1
    while i < len(argv):
        if argv[i] == "--id":
            if i + 1 == len(argv):
                raise SystemExit("--id needs your iRacing customer ID after it, "
                                 "for example --id 123456")
            cid = argv[i + 1]
            del argv[i:i + 2]
        elif argv[i].startswith("--id="):
            cid = argv[i][len("--id="):]
            del argv[i]
        else:
            i += 1
    return cid if cid is not None else os.environ.get(ID_SETTING)


def protected_ids():
    """Every customer ID a saved profile lists under protect_ids (the list
    src/personalize.py refuses to build for): a measuring tool never writes
    a paint under one of them either."""
    ids = set()
    try:
        names = os.listdir(PROFILES)
    except OSError:
        return ids
    for name in names:
        if name.endswith(".json"):
            try:
                with open(os.path.join(PROFILES, name), encoding="utf-8") as fh:
                    ids.update(str(i) for i in json.load(fh).get("protect_ids", []))
            except (OSError, ValueError, AttributeError, TypeError):
                pass
    return ids


def test_paint(folder, cid, spec=False):
    """The full path of car_<cid>.tga in `folder` (car_spec_<cid>.tga with
    spec=True): the only name iRacing loads.  Stops with a plain message,
    before anything is built or written, when there is no customer ID, when
    it isn't a number, when a profile protects it, or when the folder isn't
    there."""
    if not cid:
        raise SystemExit(
            "Which customer ID? iRacing loads only car_<your customer ID>.tga, so a "
            "test pattern saved under any other name never shows on the car. Add "
            "--id <your customer ID>, or set %s once. The ID is on the My Account "
            "page of the iRacing app; leave out the #." % ID_SETTING)
    cid = str(cid)
    if not re.fullmatch(r"[0-9]+", cid):
        raise SystemExit("%r isn't a customer ID: that's a number, such as 123456 "
                         "(leave out the #)." % cid)
    if cid in protected_ids():
        raise SystemExit("Refusing to write over the paint for customer ID %s: a "
                         "profile in profiles/ lists it under protect_ids." % cid)
    if not os.path.isdir(folder):
        raise SystemExit("iRacing's paint folder for this car isn't there: %s\n"
                         "Make that folder, then run this again." % folder)
    return os.path.join(folder, "car_%s%s.tga" % ("spec_" if spec else "", cid))
