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

"""Keep a copy of a file in the iRacing paint folder before a tool replaces it.

Every tool that writes into the iRacing paint folder goes through here (the
measuring tools: the probes, coord_grid.py, spec_flat.py and spec_ladder.py).
Before a file there is replaced, a copy is kept in
out/backup/<car folder>/<name>.<date>-<time><ext>, and the tool prints where the
copy is and how to put it back. An existing backup is never overwritten.

Probes get rerun dozens of times while a car is being measured, and a full copy
on every rerun would pile up multi-MB files. So the project remembers what it
last wrote to each path (out/backup/written.json: path -> sha256). When the
file there is still byte-for-byte what this project wrote, it is not copied
again: there is nothing of yours in it. Anything else - your own paint, a
download, a file the sim wrote - is always copied first.

    save_tga(img, path)   back up, save a PIL image as RLE TGA, remember it
    copy_in(src, dst)     back up, copy a file in, remember it
    move_aside(path)      move a file out of its folder into out/backup/
    backup(path)          only the backup step;  record(path)  only the remember

Standard library only.
"""
import datetime
import hashlib
import json
import os
import shutil
import stat

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP = os.path.join(ROOT, "out", "backup")     # a test may point this elsewhere


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _key(path):
    """The written.json key for a destination: its absolute path (case-folded on
    Windows, so the same file always gets the same key)."""
    return os.path.normcase(os.path.abspath(path))


def _ledger():
    return os.path.join(BACKUP, "written.json")


def _load():
    """path -> sha256 of what this project last wrote there. A missing or
    unreadable record counts as empty, which can only mean MORE backups."""
    try:
        with open(_ledger(), encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _store(data):
    os.makedirs(BACKUP, exist_ok=True)
    tmp = _ledger() + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=1, sort_keys=True)
    os.replace(tmp, _ledger())


def _copy_new(path, digest):
    """Copy `path` to a NEW file in out/backup/<its folder>/ and return its path.

    The name carries the date and time; if that name is taken a counter is
    added (-2, -3, ...). The file is created exclusively, so an existing backup
    is never overwritten, and the copy is checked against `digest` (the
    original's sha256) before anyone relies on it."""
    folder = os.path.basename(os.path.dirname(os.path.abspath(path))) or "files"
    stem, ext = os.path.splitext(os.path.basename(path))
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    dest_dir = os.path.join(BACKUP, folder)
    os.makedirs(dest_dir, exist_ok=True)
    n = 1
    while True:
        tag = stamp if n == 1 else "%s-%d" % (stamp, n)
        dest = os.path.join(dest_dir, "%s.%s%s" % (stem, tag, ext))
        try:
            out = open(dest, "xb")
        except FileExistsError:
            n += 1
            continue
        try:
            with out, open(path, "rb") as src:
                shutil.copyfileobj(src, out, 1 << 20)
            shutil.copystat(path, dest)
            if _sha256(dest) != digest:
                raise OSError("the backup copy of %s does not match the original" % path)
        except BaseException:
            os.remove(dest)
            raise
        return dest


def _how_to_undo(path, dest):
    print("  The copy is at: %s" % dest)
    print("  To put it back: copy that file into %s and rename it %s"
          % (os.path.dirname(os.path.abspath(path)), os.path.basename(path)))


def backup(path):
    """Copy the file at `path`, if there is one, into out/backup/ before it is
    replaced, and say where the copy is. Returns the copy's path, or None when
    there was no file, or when the file is exactly what this project last
    wrote there (then there is nothing of yours to lose)."""
    if not os.path.isfile(path):
        return None
    digest = _sha256(path)
    name = os.path.basename(path)
    if _load().get(_key(path)) == digest:
        print("No backup needed: the %s there is the file this project wrote "
              "there last time, unchanged since, so nothing of yours is "
              "replaced." % name)
        return None
    dest = _copy_new(path, digest)
    print("Backed up the existing %s before replacing it." % name)
    _how_to_undo(path, dest)
    return dest


def record(path):
    """Remember that this project just wrote `path` (its sha256 in
    out/backup/written.json), so the next write there can skip the backup
    while the file is still unchanged."""
    try:
        data = _load()
        data[_key(path)] = _sha256(path)
        _store(data)
    except OSError as e:
        print("note: could not update %s (%s); the next run will simply make a "
              "backup copy again." % (_ledger(), e))


def save_tga(img, path):
    """Back up whatever is at `path`, save the PIL image `img` there as RLE TGA
    (the same save call the tools always used, so the bytes are unchanged),
    and remember it. Returns the backup's path or None."""
    kept = backup(path)
    img.save(path, compression="tga_rle")
    record(path)
    return kept


def copy_in(src, dst):
    """Back up whatever is at `dst`, copy the file `src` there (with its
    timestamps), and remember it. `dst` may be a folder: the file then keeps
    its own name. Returns the backup's path or None."""
    if os.path.isdir(dst):      # else the backup would look for a file that isn't there
        dst = os.path.join(dst, os.path.basename(src))
    kept = backup(dst)
    shutil.copy2(src, dst)
    record(dst)
    return kept


def move_aside(path):
    """Take the file at `path` out of its folder: it is moved into
    out/backup/<folder>/, named like a backup (it is the backup), and the tool
    says where it went and how to put it back. Returns the new path, or None if
    there was no file."""
    if not os.path.isfile(path):
        return None
    dest = _copy_new(path, _sha256(path))
    try:
        os.remove(path)
    except PermissionError as e:
        os.chmod(dest, stat.S_IWRITE)   # the copy took the original's read-only flag
        os.remove(dest)     # the original stays put, so the copy isn't needed
        if getattr(e, "winerror", None) == 32:
            why = ("another program has it open. Close the iRacing car viewer and "
                   "run this again.")
        else:
            why = "Windows would not let this tool delete it (is the file read-only?)."
        raise SystemExit("Could not move %s: %s" % (os.path.basename(path), why))
    try:
        data = _load()
        if data.pop(_key(path), None) is not None:
            _store(data)
    except OSError:
        pass        # a stale entry is harmless: it only matches bytes we wrote
    print("Moved %s out of the paint folder." % os.path.basename(path))
    _how_to_undo(path, dest)
    return dest
