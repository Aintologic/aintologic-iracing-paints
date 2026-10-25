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

"""Check what this computer has, and what it still needs, to build the paints.

    python tools/check_setup.py

It only looks. It installs nothing, changes nothing and never runs pip. It
reports, in plain words:

  * Python: its version, and whether it is new enough;
  * the four Python add-ons listed in requirements.txt (numpy, Pillow, scipy,
    psd-tools): installed or missing, the version, and whether it is too old,
    with the install command for anything missing;
  * iRacing's paint folder: whether it is there;
  * the cars with a one-time setup step (six today): whether it is done, and
    the command to run for each car where it isn't.

Exit code: 0 when Python and all four add-ons are ready, so the builders can
run; 1 when any of them is missing, too old or won't load, or when this copy of
the project is missing requirements.txt or src/setup_check.py.  The paint
folder and the setup step are reported but don't change the exit code: you can
build without the paint folder and copy the files over later, and each setup
step is needed only for its own car.

It uses nothing but Python itself (its standard library and
src/setup_check.py), so it runs before any add-on is installed.
"""
import importlib
import os
import re
import sys
import warnings

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIREMENTS = os.path.join(ROOT, "requirements.txt")
sys.path.insert(0, os.path.join(ROOT, "src"))
try:
    import setup_check          # standard library only, like this file
except ImportError:
    setup_check = None

# The oldest Python the add-ons support.  On PyPI, numpy 1.24.0, Pillow 10.0.0
# and scipy 1.10.0 each say "Requires-Python >=3.8"; psd-tools 1.9.0 sets no
# limit.  Raise this if requirements.txt ever asks for newer add-ons.
MIN_PYTHON = (3, 8)

# add-on -> (the name Python imports it by, what it is in one line: the
# README's words).  The minimum versions are read from requirements.txt.
# Listed in the README's install order.
ADDONS = {
    "numpy": ("numpy", "fast math on large grids of numbers"),
    "pillow": ("PIL", "opens, draws and saves pictures"),
    "scipy": ("scipy", "scientific tools built on numpy"),
    "psd-tools": ("psd_tools", "reads Photoshop (.psd) files"),
}
README_HINT = ("The README's \"What you need\" section explains each add-on "
               "and the order to install them.")


def say(label, text):
    print("  %-10s%s" % (label, text))


def count_cars():
    """How many cars are measured so far: one src/team_<car>.py builder each."""
    src = os.path.join(ROOT, "src")
    return len([f for f in os.listdir(src) if f.startswith("team_") and f.endswith(".py")])


def _key(name):
    """An add-on name in one spelling: 'Pillow' -> 'pillow', 'psd_tools' -> 'psd-tools'."""
    return re.sub(r"[-_.]+", "-", name).lower()


def _numbers(version):
    """'1.26.4' -> (1, 26, 4); stops at the first part that isn't a number ('2.0rc1' -> (2, 0))."""
    m = re.match(r"\d+(?:\.\d+)*", version or "")
    return tuple(int(x) for x in m.group(0).split(".")) if m else ()


def _older(version, minimum):
    """True when `version` is below `minimum`; '1.24' and '1.24.0' count as the same."""
    a, b = _numbers(version), _numbers(minimum)
    n = max(len(a), len(b))
    return a + (0,) * (n - len(a)) < b + (0,) * (n - len(b))


def read_requirements(path=REQUIREMENTS):
    """[(add-on, minimum version or None, the line as written)] from requirements.txt."""
    reqs = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.split("#", 1)[0].strip()
            m = re.match(r"([A-Za-z0-9][A-Za-z0-9._-]*)\s*(?:>=\s*([0-9][0-9.]*))?", line)
            if m:
                reqs.append((m.group(1), m.group(2), line))
    order = list(ADDONS)
    reqs.sort(key=lambda r: order.index(_key(r[0])) if _key(r[0]) in order else len(order))
    return reqs


def _installed_version(name):
    """The installed version of add-on `name`, or None if it isn't installed."""
    try:
        from importlib import metadata
    except ImportError:         # Python older than 3.8 has no importlib.metadata
        return None
    for n in (name, name.lower(), name.replace("-", "_"), name.lower().replace("-", "_")):
        try:
            return metadata.version(n)
        except metadata.PackageNotFoundError:
            pass
    return None


def _load_error(module):
    """None if `module` imports cleanly, else what went wrong, in one line."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            importlib.import_module(module)
        return None
    except Exception as e:      # a broken install can fail in more ways than ImportError
        return ("%s: %s" % (type(e).__name__, e)).splitlines()[0]


def check_python(version=sys.version_info):
    """Report the Python version; return the problems found (empty when it is new enough)."""
    print("Python")
    have = "%d.%d.%d" % tuple(version[:3])
    need = "%d.%d" % MIN_PYTHON
    if tuple(version[:2]) >= MIN_PYTHON:
        say("OK", "Python %s (needs %s or newer)" % (have, need))
        return []
    say("TOO OLD", "Python %s - the add-ons need Python %s or newer" % (have, need))
    say("", "Get a newer one from python.org/downloads; the README's \"What you need\"")
    say("", "section explains it.")
    return ["Python is too old"]


def check_addons(path=REQUIREMENTS):
    """Report each add-on in requirements.txt; return the problems found."""
    print("Python add-ons (from requirements.txt)")
    if not os.path.isfile(path):
        say("MISSING", "requirements.txt - it belongs in the project folder.")
        say("", "Is this a complete copy of the project?")
        return ["requirements.txt is missing"]
    problems = []
    for name, minimum, line in read_requirements(path):
        module, what = ADDONS.get(_key(name), (_key(name).replace("-", "_"),
                                               "listed in requirements.txt"))
        version = _installed_version(name)
        error = _load_error(module)
        need = " (needs %s or newer)" % minimum if minimum else ""
        install = "python -m pip install \"%s\"" % line
        if error and version is None:
            say("MISSING", "%s - %s" % (name, what))
            say("", "Install it with:  " + install)
            problems.append("%s is missing" % name)
            continue
        if error:
            say("BROKEN", "%s %s is installed, but Python can't load it:" % (name, version))
            say("", error)
            say("", "Install it again with:  python -m pip install --force-reinstall \"%s\"" % line)
            problems.append("%s won't load" % name)
            continue
        version = version or getattr(sys.modules.get(module), "__version__", None)
        if version and minimum and _older(version, minimum):
            say("TOO OLD", "%s %s%s - %s" % (name, version, need, what))
            say("", "Update it with:  " + install)
            problems.append("%s is too old" % name)
        else:
            say("OK", "%s %s%s" % (name, version or "(version not known)", need))
    if problems:
        print("  " + README_HINT)
    return problems


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


def check_paint_folder():
    """Report iRacing's paint folder; return a note for the summary, or None."""
    print("iRacing paint folder")
    if os.name != "nt":
        say("NOTE", "Building paints works on this computer, but iRacing runs on Windows.")
        say("", "Copy the finished files to the Windows PC that runs iRacing.")
        return "Copy the files to the Windows PC that runs iRacing."
    iracing = os.path.join(documents_folder(), "iRacing")
    paint = os.path.join(iracing, "paint")
    if os.path.isdir(paint):
        say("OK", paint)
        return None
    say("NOT FOUND", paint)
    if os.path.isdir(iracing):
        say("", "The iRacing folder is there, but not the paint folder inside it.")
        say("", "You can make it yourself: a new folder named paint, in")
        say("", iracing)
    else:
        say("", "iRacing makes its iRacing folder in your Documents folder when it runs.")
        say("", "If iRacing is installed here, start it once. You can also make the paint")
        say("", "folder by hand. If iRacing runs on another PC, build the paints here and")
        say("", "copy them to that PC.")
    return "The iRacing paint folder was not found."


def check_setup_step(root=ROOT):
    """Report the one-time setup step per car; return the cars where it isn't
    done, or None if src/setup_check.py itself is missing."""
    if setup_check is None:
        print("One-time setup step")
        say("MISSING", "src/setup_check.py - it belongs in the project folder.")
        say("", "Is this a complete copy of the project?")
        return None
    need = len(setup_check.NEEDS)
    print("One-time setup step (%d of the measured cars need it; the other %d don't)"
          % (need, count_cars() - need))
    not_done = []
    for car, (name, template, _) in setup_check.NEEDS.items():
        gone = setup_check.missing(car, root)
        if not gone:
            say("DONE", name)
            continue
        not_done.append(car)
        say("NOT DONE", "%s - missing %s" % (name, ", ".join(gone)))
        say("", "Run once:  python tools/first_run.py %s <path to %s>" % (car, template))
    if not_done:
        print("  Replace <path to ...>, angle brackets included, with the zip's full path")
        print("  in quotes. templates/README.md says where to get each car's template.")
    return not_done


def summary(problems, not_done, paint_note):
    """The one-line verdict."""
    if problems:
        line = ("Summary: NOT READY. Fix these first: %s. Then run this check again."
                % ", ".join(problems))
    elif not_done:
        cars = count_cars()
        line = ("Summary: READY to build %d of the %d measured cars. %s first (see above)."
                % (cars - len(not_done), cars,
                   "The other one needs its one-time setup step" if len(not_done) == 1 else
                   "The other %d need their one-time setup step" % len(not_done)))
    else:
        line = ("Summary: READY. Everything needed to build all %d measured cars is here."
                % count_cars())
    return line + (" " + paint_note if paint_note else "")


def main():
    try:
        sys.stdout.reconfigure(errors="replace")    # an odd letter in a folder name never stops it
    except Exception:
        pass
    print("Setup check for the paint builders")
    print("This only looks. It changes nothing and installs nothing.")
    print("")
    problems = check_python()
    print("")
    problems += check_addons()
    print("")
    paint_note = check_paint_folder()
    print("")
    not_done = check_setup_step()
    if not_done is None:
        problems.append("src/setup_check.py is missing")
    print("")
    print(summary(problems, not_done, paint_note))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
