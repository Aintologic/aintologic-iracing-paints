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

"""Check that the project's files carry the licenses they should.

    python tools/license_check.py
    python tools/license_check.py --root <another copy of the project>

Why: "free to download" isn't "do anything you like". The README's License
section promises three licenses: the code is under the GNU AGPL 3.0 (or
later), the ready-made paints and example logos under Creative Commons
BY-NC-SA 4.0, and the fonts under the SIL Open Font License 1.1. This makes
sure every file that needs its license text or notice still has it.

The checks:

  1. LICENSE holds the full GNU AGPL 3.0 text.
  2. Every Python file carries the AGPL notice at its top: the line
     "SPDX-License-Identifier: AGPL-3.0-or-later" and the words "GNU Affero
     General Public License".
  3. TRADEMARKS.md is there.
  4. paints/LICENSE.txt and examples/logos/LICENSE.txt are there and name
     CC BY-NC-SA 4.0.
  5. fonts/OFL.txt holds the SIL Open Font License 1.1 and, for every font in
     fonts/, a copyright line naming the font's family and the font's file name.
  6. Any other font file has an Open Font License text in its own folder that
     names its family.

It checks the files git would commit (tracked files, plus new files that git
doesn't ignore), or every file when the folder isn't a git repository (except
the files the one-time setup step makes on your own computer, which are never
shipped).

It only reads. It changes nothing and never connects to the internet. Exit
code: 0 when every check passes, 1 when any fails, 2 when it couldn't run.

It uses nothing but Python itself and git.
"""
import argparse
import ast
import os
import re
import struct
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Lines only the full AGPL 3.0 text has (the same ones the release checks use).
AGPL_MARKERS = [
    "GNU AFFERO GENERAL PUBLIC LICENSE",
    "Version 3, 19 November 2007",
    "13. Remote Network Interaction",
    "END OF TERMS AND CONDITIONS",
]
SPDX_LINE = "SPDX-License-Identifier: AGPL-3.0-or-later"
AGPL_NAME = "GNU Affero General Public License"
HEADER_REACH = 2000     # the notice must sit in the first this-many characters

CC_FOLDERS = ["paints", os.path.join("examples", "logos")]
CC_NAMES = ["CC BY-NC-SA 4.0", "Attribution-NonCommercial-ShareAlike 4.0"]

# Lines only the full OFL 1.1 text has.
OFL_MARKERS = [
    "SIL OPEN FONT LICENSE Version 1.1",
    "PREAMBLE",
    "PERMISSION & CONDITIONS",
    "TERMINATION",
    "DISCLAIMER",
]
FONT_EXTS = (".ttf", ".otf")
SKIP_DIRS = {".git", "out", "venv", ".venv", "env", "__pycache__", "build", "dist", "node_modules"}


def flat(text):
    """Text with every run of spaces and line breaks made one space."""
    return re.sub(r"\s+", " ", text)


def read(root, rel):
    path = os.path.join(root, *rel.split("/"))
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return None


def setup_files(root):
    """The files the one-time setup step makes from iRacing's templates, read
    from src/setup_check.py (parsed, never run). They are made on your own
    computer, never shipped, so they need no license notice."""
    try:
        with open(os.path.join(root, "src", "setup_check.py"), encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
    except (OSError, SyntaxError, ValueError):
        return set()
    for node in tree.body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and getattr(node.targets[0], "id", None) == "NEEDS"):
            try:
                return {p for _, _, files in ast.literal_eval(node.value).values() for p in files}
            except (ValueError, TypeError):
                break
    return set()


def project_files(root):
    """Relative paths of every file git would commit, or every file in the folder."""
    try:
        # git writes UTF-8; read it as bytes so a folder name with an accent
        # in it is never misread through the console's code page
        top = subprocess.run(["git", "-c", "core.fsmonitor=false", "rev-parse",
                              "--show-toplevel"], cwd=root, capture_output=True)
        if (top.returncode == 0
                and os.path.samefile(top.stdout.decode("utf-8", "replace").strip(), root)):
            out = subprocess.run(["git", "-c", "core.quotepath=off", "-c", "core.fsmonitor=false",
                                  "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                                 cwd=root, capture_output=True)
            if out.returncode == 0:
                return sorted({p for p in out.stdout.decode("utf-8", "replace").split("\x00")
                               if p and os.path.isfile(os.path.join(root, *p.split("/")))})
    except OSError:
        pass
    # not a git repository (an unzipped download, say): every file, except
    # working folders and what the setup step made here
    skip = setup_files(root)
    found = []
    for dp, dn, fs in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fs:
            rel = os.path.relpath(os.path.join(dp, f), root).replace("\\", "/")
            if rel not in skip:
                found.append(rel)
    return sorted(found)


def font_family(path):
    """A font file's family name from its 'name' table, or None if it can't be read.

    Uses the typographic family (name 16) when the font has one, else the
    family (name 1)."""
    try:
        with open(path, "rb") as fh:
            data = fh.read()
        count = struct.unpack(">H", data[4:6])[0]
        for i in range(count):
            tag, _, offset, _ = struct.unpack(">4sIII", data[12 + 16 * i:28 + 16 * i])
            if tag != b"name":
                continue
            _, n, strings = struct.unpack(">HHH", data[offset:offset + 6])
            names = {}
            for j in range(n):
                rec = data[offset + 6 + 12 * j:offset + 18 + 12 * j]
                platform, _, _, name_id, length, start = struct.unpack(">HHHHHH", rec)
                raw = data[offset + strings + start:offset + strings + start + length]
                if name_id in (1, 16):
                    text = raw.decode("utf-16-be" if platform in (0, 3) else "latin-1", "replace")
                    names.setdefault(name_id, text.strip())
            return names.get(16) or names.get(1)
    except (OSError, struct.error, IndexError):
        return None
    return None


def check_license(root, files):
    text = read(root, "LICENSE")
    if text is None:
        return ["there's no LICENSE file"]
    missing = [m for m in AGPL_MARKERS if m not in text]
    return ["LICENSE isn't the full GNU AGPL 3.0 text (missing: %s)" % "; ".join(missing)] if missing else []


def check_py_headers(root, files):
    bad = []
    for rel in files:
        if not rel.endswith(".py"):
            continue
        top = (read(root, rel) or "")[:HEADER_REACH]
        if SPDX_LINE not in top or AGPL_NAME not in top:
            bad.append(rel)
    return ["%s has no AGPL notice at its top" % rel for rel in bad]


def check_trademarks(root, files):
    return [] if read(root, "TRADEMARKS.md") is not None else ["there's no TRADEMARKS.md"]


def check_cc(root, files):
    problems = []
    for folder in CC_FOLDERS:
        rel = folder.replace(os.sep, "/") + "/LICENSE.txt"
        text = read(root, rel)
        if text is None:
            problems.append("there's no %s" % rel)
        elif not any(n in flat(text) for n in CC_NAMES):
            problems.append("%s doesn't name CC BY-NC-SA 4.0" % rel)
    return problems


def check_ofl(root, files):
    problems = []
    text = read(root, "fonts/OFL.txt")
    if text is None:
        return ["there's no fonts/OFL.txt"]
    missing = [m for m in OFL_MARKERS if m.lower() not in text.lower()]
    if missing:
        problems.append("fonts/OFL.txt isn't the full SIL Open Font License 1.1 (missing: %s)"
                        % "; ".join(missing))
    copyright_lines = [l.lower() for l in text.splitlines() if l.strip().lower().startswith("copyright")]
    for rel in files:
        folder, name = os.path.split(rel)
        if folder != "fonts" or not name.lower().endswith(FONT_EXTS):
            continue
        family = font_family(os.path.join(root, *rel.split("/")))
        if not family:
            problems.append("%s: its family name can't be read" % rel)
            continue
        first = family.split()[0].lower()
        if not any(first in l for l in copyright_lines):
            problems.append("fonts/OFL.txt has no copyright line for %s (%s)" % (family, rel))
        if name not in text:
            problems.append("fonts/OFL.txt doesn't list %s" % name)
    return problems


def check_other_fonts(root, files):
    """A font outside fonts/ needs an OFL text in its own folder that names its family."""
    problems = []
    for rel in files:
        folder, name = os.path.split(rel)
        if folder == "fonts" or not name.lower().endswith(FONT_EXTS):
            continue
        family = font_family(os.path.join(root, *rel.split("/")))
        first = family.split()[0].lower() if family else os.path.splitext(name)[0].lower()
        texts = [read(root, f) or "" for f in files
                 if os.path.split(f)[0] == folder and f.lower().endswith(".txt")]
        if not any("open font license" in flat(t).lower() and first in t.lower() for t in texts):
            problems.append("%s has no Open Font License text naming it in %s/" % (rel, folder))
    return problems


CHECKS = [
    ("LICENSE is the full GNU AGPL 3.0", check_license),
    ("every Python file carries the AGPL notice", check_py_headers),
    ("TRADEMARKS.md is there", check_trademarks),
    ("the paints and example logos carry CC BY-NC-SA 4.0", check_cc),
    ("fonts/OFL.txt covers every font in fonts/", check_ofl),
    ("every other font has its Open Font License text", check_other_fonts),
]


def main(argv=None):
    try:
        sys.stdout.reconfigure(errors="backslashreplace")
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser(
        description="Check that the code, paints, logos and fonts carry the licenses the "
                    "README promises. It only reads.",
        epilog="Exit code 0 when every check passes, 1 when any fails, 2 when it couldn't run.")
    ap.add_argument("--root", default=ROOT, metavar="FOLDER",
                    help="the copy of the project to check (default: the one this tool is in)")
    args = ap.parse_args(argv)
    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print("Can't check: the folder %s doesn't exist." % args.root)
        return 2

    files = project_files(root)
    n_py = sum(1 for f in files if f.endswith(".py"))
    print("License check (%d files, %d of them Python)" % (len(files), n_py))
    print()
    failed = 0
    for name, check in CHECKS:
        problems = check(root, files)
        print(("PASS  " if not problems else "FAIL  ") + name)
        for p in problems:
            print("        " + p)
        failed += bool(problems)
    print()
    if failed:
        print("Result: %d of %d license checks failed. Put the missing license text or "
              "notice back before anything is published." % (failed, len(CHECKS)))
        return 1
    print("Result: every license check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
