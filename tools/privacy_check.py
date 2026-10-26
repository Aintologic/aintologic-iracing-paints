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

"""Look through the project for anything private before it is published.

    python tools/privacy_check.py                 # the project's files
    python tools/privacy_check.py --history       # ... and every commit, tag and old file version
    python tools/privacy_check.py --path out/release/notes-v1.2.3.md --path out/release/unzip-check
    python tools/privacy_check.py --history --words <your private word list>

Why: once something is published, people keep copies. A customer ID, a real
name, a folder path from someone's computer or a link to an AI chat can't be
taken back. This tool looks for the SHAPE of those things (patterns), so it
needs no private information of its own, and it is safe to run in public:
whatever it finds is printed with all but the first and last character of
each word hidden.

What it looks for, each reported under a plain name:

  * folder paths from a computer: a path that starts with a drive letter
    (also written the Git Bash or WSL way, such as /c/<folder> or
    /mnt/c/<folder>), a network path (two slashes or backslashes, a computer
    name and a share, or an smb:// or file:// link to one), or a home folder
    such as /home/<name> or /Users/<name>, also when the text is URL-encoded.
    %USERPROFILE%, ~ and paths inside the project are fine;
  * numbers shaped like an iRacing customer ID: in file names such as
    car_<digits>.tga, helmet_<digits>.tga or suit_<digits>.tga (or a long run
    of digits in a picture, paint, zip or .json file name, dates aside), and
    in text: car_<digits>, --id <digits>, "customer ID <digits>", an "id"
    field, and iRacing or Trading Paints profile links with an ID in them.
    The documented example ID, 123456, is fine;
  * race results: a starting, finishing or qualifying position, a position
    change written with an arrow or "to", iRating and safety-rating values,
    and iRacing's telemetry, replay and results files;
  * private folders and files: anything in a profiles folder (except its
    README) or an out folder, .env files, *.local.json files, private keys, a
    numbered scratch-area folder ("area" and two digits) and an evidence
    folder;
  * links to AI chats: shared or saved conversations, tasks and published
    artifacts;
  * iRacing template files, and the files the one-time setup step makes from
    them (listed in src/setup_check.py), wherever they turn up;
  * passwords, tokens and keys;
  * your own private words (see below);
  * inside pictures, fonts, zips and other binary files: folder paths from a
    computer, chat links, tokens and your private words. Zips (and .gz files
    and PDF streams) are opened and everything inside is checked too;
  * with --history: tags that aren't version numbers like v1.2.3.

Names can't be recognised by a pattern. Your own private words are the
names, IDs and computer names that no pattern can know. They come from a file
that only exists on your computer and is never committed:
profiles/private-words.txt (one word or phrase per line, '#' starts a
comment), or the file given with --words. The "id", "driver" and
"protect_ids" values in any profiles/*.json are added too. Git ignores the
profiles folder, so none of this is ever published. Words of four letters or
fewer only count as whole words. A line "public: Name <email>" in the list
names a commit identity you publish on purpose, such as your GitHub account:
your private words aren't reported in a commit's or tag's author, committer
or tagger when it is exactly that identity (everything else still is).

Findings the maintainer has looked at and accepted are listed in
tools/privacy-accepted.txt: one line per accepted finding, the git hash of
one version of one file and the kind of finding (for example "race"). Only
that kind, in exactly that version of the file, is accepted; anything else is
still reported.

What it checks:

  default    every file git would commit: tracked files as they are in the
             folder and, when that differs, as git has them staged (a file
             deleted from the folder but not from git too), plus new files
             that git doesn't ignore. In a folder that isn't a git
             repository, every file in it.
  --history  also every commit message, author and committer, every tag and
             branch name, and every version of every file reachable from any
             branch or tag, so something that was deleted later is still found.
  --path     also a folder or file outside git, such as release notes or an
             unzipped download (repeatable).

It only reads. It changes nothing, writes nothing and never connects to the
internet. Exit code: 0 when nothing is found, 1 when something is, 2 when it
couldn't run.

It uses nothing but Python itself and git.
"""
import argparse
import ast
import bisect
import glob
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import urllib.parse
import zipfile
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The documented example customer ID (README, guides). Never a real one.
EXAMPLE_ID = "123456"
# The README's example profile values: never treated as private words, so a
# profile copied from the README doesn't flag the README itself.
EXAMPLE_WORDS = {EXAMPLE_ID, "a. driver"}
ACCEPTED_FILE = "tools/privacy-accepted.txt"

# class key -> the plain-English name printed with each finding
CLASSES = {
    "path": "folder path from a computer",
    "id": "number shaped like a customer ID",
    "race": "race result",
    "private": "private folder or file",
    "chat": "link to an AI chat",
    "template": "iRacing template or a file made from one",
    "secret": "password, token or key",
    "word": "word from your private list",
    "tag": "tag that isn't a version number",
    "unreadable": "file that couldn't be checked",
}

# --- patterns in text ----------------------------------------------------------
# Each is (class, pattern, allow, in_binary). allow(match) -> True means "this
# one is fine". in_binary: also looked for in the readable strings inside
# binary files (only patterns that never turn up by chance in picture data).
# Several patterns are put together from pieces, so this file never contains
# the very things it looks for.

_SEP = r"[\\/]"             # a path separator, either way round


def _not_example(m):
    """Allow the documented example ID."""
    return m.group(1) == EXAMPLE_ID


def _around(m, extra=1):
    """The line a match is on, with `extra` lines either side."""
    s = m.string
    a = m.start()
    for _ in range(extra + 1):
        a = s.rfind("\n", 0, a)
        if a <= 0:
            a = 0
            break
    b = m.end()
    for i in range(extra + 1):
        nb = s.find("\n", b + (1 if i else 0))
        if nb < 0:
            b = len(s)
            break
        b = nb
    return s[a:b]


# words that show a line is about a race (looked for on the line and the lines
# either side); a bare "finished" and an ordinal is only a race result with one
RACE_CONTEXT = re.compile(r"(?i)\b(?:race[ds]?|laps?|grid|split|podium|pole|heat|qualif\w*|started|"
                          r"i-?rating|safety[ -]rating|incidents?|overtak\w*|positions?|on track)\b")
_MONTH = re.compile(r"(?i)\s*(?:of\s+)?(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b")


def _race_context(m):
    return bool(RACE_CONTEXT.search(_around(m)))


def _date_follows(m):
    return bool(_MONTH.match(m.string, m.end()))


def _allow_place(m):
    """A starting, finishing or qualifying place. A P-number or a start/qualify
    place in digits is always a result; a finishing place in digits or words
    only on a line about a race; an ordinal before a month is a date."""
    if m.group("p"):
        return int(m.group("p")[1:]) == 0
    if _date_follows(m):
        return True
    if m.group("o") and m.group("verb").lower().startswith(("start", "qualif")):
        return False
    return not _race_context(m)


def _allow_p_change(m):
    """P0 is never a race position (it is a priority label); small numbers
    only count on a line about a race."""
    a, b = int(m.group(1)), int(m.group(2))
    if 0 in (a, b):
        return True
    return max(a, b) < 5 and not _race_context(m)


def _allow_ordinal_change(m):
    if _date_follows(m):
        return True
    if _race_context(m):
        return False
    a, b = int(m.group(1)), int(m.group(3))
    arrow = m.group(2).lower() != "to"
    after_from = re.search(r"(?i)\bfrom\s*$", m.string[max(0, m.start() - 8):m.start()])
    return not (max(a, b) >= 5 and (arrow or after_from))


def _allow_no_context(m):
    return not _race_context(m)


_ORDINAL_WORDS = (r"(?:(?:twenty|thirty|forty)[- ])?(?:first|second|third|fourth|fifth|sixth|seventh|"
                  r"eighth|ninth)|tenth|eleventh|twelfth|(?:thir|four|fif|six|seven|eigh|nine)teenth|"
                  r"twentieth|thirtieth|fortieth")
_ARROW = ("(?:-+>|=+>|>>|[" + chr(0x2013) + chr(0x2014) + chr(0x2212) + "]+>|["
          + chr(0x2192) + chr(0x21D2) + chr(0x2794) + chr(0x279C) + chr(0x27F6) + "])")
_PLACE = re.compile(
    r"(?i)\b(?P<verb>start(?:ed|s|ing)?|finish(?:ed|es|ing)?|qualif(?:ied|ies|ying|y)|won|placed|came)\b"
    r"(?:[\s:,]+(?:in|from|on|at|as|the\s+race\s+from)\b)*[\s:,]*"
    r"(?:(?P<p>P\d{1,2})|(?P<o>\d{1,2}(?:st|nd|rd|th))|(?P<w>" + _ORDINAL_WORDS + r")"
    r"|position\s*[:#]?\s*(?P<n>\d{1,2}))(?![\w-])")

# AI chat products: the host, and the part of a link that points at one
# conversation, task or published artifact
_D = r"(?:\.|\[\.\]|%2e)"   # a dot, also written [.] or %2E


def _host(*parts):
    return _D.join(parts)


_CHAT_LINKS = [
    (_host("chat" + "gpt", "com"), r"(?:share|c|g|s|codex|canvas)/"),
    (_host("chat", "open" + "ai", "com"), r"(?:share|c|g)/"),
    (_host("claude", "ai"), r"(?:share|chat|code|project|public|artifacts?)/"),
    (_host("claude", "site"), r"(?:artifacts?|public)/"),
    (_host("claude", "com"), r"(?:share|chat)/"),
    (_host("gemini", "google", "com"), r"(?:share|app|gem)/"),
    (_host("g", "co"), r"gemini/"),
    (_host("aistudio", "google", "com"), r"(?:app/)?prompts/"),
    (_host("bard", "google", "com"), r"(?:share|chat)/"),
    (_host("copilot", "microsoft", "com"), r"(?:shares?|chats?)/"),
    (_host("github", "com"), r"copilot/(?:c|shares?)/"),
    (_host("perplexity", "ai"), r"(?:search|page)/"),
    (_host("grok", "com"), r"(?:share|chat|c)/"),
    (_host("x", "com"), r"i/grok"),
    (_host("twitter", "com"), r"i/grok"),
    (_host("chat", "mistral", "ai"), r"chat/"),
    (_host("chat", "deepseek", "com"), r""),
    (_host("poe", "com"), r"s/"),
    (_host("meta", "ai"), r"c/"),
    (_host("chat", "qwen", "ai"), r"(?:s|c)/"),
    (_host("huggingface", "co"), r"chat/(?:r|conversation)/"),
    (_host("m365", "cloud", "microsoft"), r"chat/"),
    (_host("you", "com"), r"search\?[^\s]*\bcid="),
]
_CHAT_RE = (r"(?i)(?<![\w-])(?:[\w-]+" + _D + r")*(?:"
            + "|".join(host + r"(?::\d+)?/+" + path.replace("/", "/+") for host, path in _CHAT_LINKS)
            + r")[^\s)\"'<>`\]]*")

_AREA = "are" + "a"         # the scratch-area folder name is "area" and two digits

TEXT_PATTERNS = [
    # a drive letter, a colon and a separator (doubled when escaped), then the rest
    ("path", r"(?<![A-Za-z0-9])[A-Za-z]:" + _SEP + r"{1,4}[\w.$%~-][^\s\"'`<>|*?:]*", None, False),
    # ... a user folder on a drive even with a letter glued in front
    ("path", r"(?i)[a-z]:\\{1,4}(?:users|documents and settings)\\{1,4}[^\s\"'`<>|*?:\\]+", None, False),
    # a drive the Git Bash or WSL way: /c/<folder>, /mnt/c/<folder>
    ("path", r"(?<![\w.:/~-])/(?:mnt/)?[A-Za-z]/[A-Za-z0-9_.$-]{2,}", None, False),
    # a network path: two backslashes (four when escaped in code), host, share
    # (not straight after a setting such as %USERPROFILE%, which is fine)
    ("path", r"(?<![\w\\%}~])\\{2,4}[A-Za-z0-9][\w.$-]*\\{1,2}[\w$.-]+", None, False),
    # ... or two forward slashes, or an smb:// or file:// link to a computer
    ("path", r"(?<![\w:/])//[A-Za-z0-9][\w.$-]*/[\w$.-]+", None, False),
    ("path", r"(?i)\b(?:smb|afp|nfs|file)://(?!/)(?!localhost/)[A-Za-z0-9][\w.$-]*/[\w$.-]*", None, False),
    # a home folder with a real-looking name in it
    ("path", r"(?i)(?<![\w.~:/-])/(?:home|users)/[A-Za-z0-9._-]+", None, False),
    # customer-ID-shaped numbers
    ("id", r"(?i)(?:car(?:_spec|_num|_decal)?|(?<![a-z])(?:helmet|suit))_(\d{4,})(?!\d)", _not_example, True),
    ("id", r"(?i)--id(?:\s*[=:]\s*|\s+)[\"']?(\d{4,})(?!\d)", _not_example, False),
    ("id", r"(?i)(?<![a-z])(?:cust(?:omer)?|member)[ _-]?(?:id|number|no\.?)(?![a-z])"
           r"\s*(?:is\s+|was\s+|of\s+|[:=#])?\s*[#\"'`]?(\d{4,})(?!\d)", _not_example, True),
    ("id", r"(?i)tradingpaints" + _D + r"com/+profile/+(\d{4,})", _not_example, True),
    ("id", r"(?i)\"id\"\s*:\s*\"?(\d{5,})(?!\d)", _not_example, False),
    # race results
    ("race", _PLACE, _allow_place, False),
    ("race", r"(?i)\b(?:qualif(?:ied|ies|ying|y)|start(?:ed|s|ing)?)\s+(?:on\s+)?(?:the\s+)?pole\b",
     None, False),
    ("race", r"(?i)\bP(\d{1,2})\s*(?:" + _ARROW + r"|to)\s*P(\d{1,2})\b", _allow_p_change, False),
    ("race", r"(?i)\b(\d{1,2})(?:st|nd|rd|th)\s*(" + _ARROW + r"|to)\s*(\d{1,2})(?:st|nd|rd|th)\b(?!-)",
     _allow_ordinal_change, False),
    ("race", r"(?i)\bi-?rating\b\s*(?:(?:of|is|was|at|:|=)\s*)?(?:\d{1,2},\d{3}|\d{3,5})\b", None, False),
    ("race", r"(?i)\b(?:\d{1,2},\d{3}|\d{3,5})\s*i-?rating\b", None, False),
    ("race", r"\biR\b\s*[:=]?\s*(?:\d{1,2},\d{3}|\d{4,5})\b", None, False),
    ("race", r"(?i)\bsafety[ -]rating\b\s*(?:(?:of|is|was|:|=)\s*)?(?:[A-DR]\s?)?\d\.\d{1,2}\b", None, False),
    ("race", r"\b[RDCBA]\s?\d\.\d{2}\s*(?i:SR)\b", None, False),
    ("race", r"(?i)\bSR\b\s*[:=]?\s*[RDCBA]\s?\d\.\d{2}\b", None, False),
    ("race", r"(?i)\b(?:licen[cs]e|class)\s*(?:class\s*)?[RDCBA]\s?\d\.\d{2}\b", None, False),
    ("race", r"(?i)\bSR\b\s*[:=]?\s*\d\.\d{2}\b", _allow_no_context, False),
    ("race", r"\b[RDCBA]\d\.\d{2}\b", _allow_no_context, False),
    # private folders written into text
    ("private", r"(?i:" + _AREA + r")(?:[._\u200b-]|%20)?\d{2}(?!\d)|\b(?:Are|ARE)[aA] \d{2}(?!\d)",
     None, True),
    # an evidence folder in a path, or named on its own (the word and a
    # slash), but not the word in a sentence such as evidence-slash-proof
    ("private", r"(?i)" + _SEP + r"evidence(?:" + _SEP + r"|(?![\w.-]))|(?<![\w.-])evidence"
                + _SEP + r"(?![\w.-])", None, False),
    # links to one AI chat
    ("chat", _CHAT_RE, None, True),
    # tokens and keys
    ("secret", r"(?i)\bgh[pousr]_[A-Za-z0-9]{36,}", None, True),
    ("secret", r"(?i)\bgithub_pat_[A-Za-z0-9_]{22,}", None, True),
    ("secret", r"\bAKIA[0-9A-Z]{16}\b", None, True),
    ("secret", r"\bsk-(?:ant|proj)-[A-Za-z0-9_-]{20,}", None, True),
    ("secret", r"\bsk-[A-Za-z0-9]{40,}", None, True),
    ("secret", r"\bglpat-[A-Za-z0-9_-]{20,}", None, True),
    ("secret", r"\bxox[abpres]-[A-Za-z0-9-]{10,}", None, True),
    ("secret", "-" * 5 + "BEGIN " + r"(?:[A-Z0-9]+ )*" + "PRIVATE" + " KEY", None, True),
    ("secret", r"PuTTY-User-Key-File-\d", None, True),
    ("secret", r"(?i)\bpass(?:word|wd)\s*[:=]\s*[\"']?[^\s\"'<>(){}\[\],;.]{6,}(?![\w(\[.])", None, False),
]
TEXT_PATTERNS = [(c, p if hasattr(p, "finditer") else re.compile(p), a, b)
                 for c, p, a, b in TEXT_PATTERNS]
_PCT_LINE = re.compile(r"[^\n]*%[0-9A-Fa-f]{2}[^\n]*")

# --- patterns inside binary files (pictures, fonts, zips) ------------------------
BINARY_PATTERNS = [
    re.compile(rb"(?i)[a-z]:[\\/]{1,4}(?:users|documents and settings)[\\/]{1,4}[^\\/\x00-\x1f]{1,40}"),
    re.compile(rb"(?i)[a-z]\x00:\x00(?:[\\/]\x00){1,2}u\x00s\x00e\x00r\x00s\x00[\\/]\x00"),
    re.compile(rb"/(?:home|Users)/[A-Za-z0-9._-]{2,32}/"),
    # a drive path with a real folder name, such as one under DATA
    re.compile(rb"(?<![A-Za-z0-9])[A-Za-z]:[\\/]{1,2}[A-Za-z0-9_$~-]{3,}[\\/]{1,2}[A-Za-z0-9_$~-]{3,}"),
]
_ASCII_RUN = re.compile(rb"[\x20-\x7e]{8,}")
_UTF16_RUN = re.compile(rb"(?:[\x20-\x7e]\x00){8,}")
_UTF16BE_RUN = re.compile(rb"(?:\x00[\x20-\x7e]){8,}")

BINARY_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".ico", ".tga", ".dds",
               ".mip", ".zip", ".ttf", ".otf", ".woff", ".woff2", ".pdf", ".psd", ".gz"}
# file names where a long run of digits looks like a customer ID
ID_NAME_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tga", ".dds", ".mip",
                ".zip", ".json"}
# iRacing telemetry, replay and results files
RACE_EXTS = {".ibt", ".rpy", ".olap", ".blap"}
# file types an iRacing paint template comes as (or is unpacked to)
TEMPLATE_EXTS = {".zip", ".psd", ".tga", ".png", ".jpg", ".jpeg", ".dds"}
KEY_EXTS = {".pem", ".key", ".p12", ".pfx", ".ppk", ".jks", ".keystore"}
KEY_NAMES = {"id_rsa", "id_dsa", "id_ecdsa", "id_ed25519", ".netrc", "_netrc", ".pypirc",
             ".git-credentials"}

# The files the one-time setup step makes from iRacing's templates. Read from
# src/setup_check.py when it is there (without running it), else this list.
SETUP_FILES_BUILTIN = [
    "src/f4_islands.py", "src/ray_islands.py", "assets/hpd-body-mask.png",
    "assets/srf-centre-mask.png", "assets/srf-side-mask.png", "assets/srf-sash-islands.png",
    "assets/sbf2000-centre-mask.png", "assets/sbf2000-pod-islands.png",
    "assets/amv-centre-mask.png",
]

MAX_DEPTH = 6               # zips (and .gz files) inside each other: how deep to open
MAX_UNPACK = 256 << 20      # the most one packed file may unpack to
MAX_EXCERPT = 60


def setup_files(roots):
    """The setup-step outputs, read from the first src/setup_check.py found.

    The file is parsed, never run: a privacy check must not run code from the
    folder it is checking."""
    for root in roots:
        path = os.path.join(root, "src", "setup_check.py")
        try:
            with open(path, encoding="utf-8") as fh:
                tree = ast.parse(fh.read())
        except (OSError, SyntaxError, ValueError):
            continue
        for node in tree.body:
            if (isinstance(node, ast.Assign) and len(node.targets) == 1
                    and getattr(node.targets[0], "id", None) == "NEEDS"):
                try:
                    needs = ast.literal_eval(node.value)
                    return sorted({p for _, _, files in needs.values() for p in files})
                except (ValueError, TypeError):
                    break
    return list(SETUP_FILES_BUILTIN)


# --- reading text ------------------------------------------------------------------

def decode_text(data):
    """A file's bytes as text, or None when they look binary.

    UTF-8 (with or without a byte-order mark) and UTF-16 (with a byte-order
    mark, or without one when every other byte is zero, as Windows PowerShell
    writes it) are read as text."""
    if data[:3] == b"\xef\xbb\xbf":
        return data[3:].decode("utf-8", "replace")
    if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return data.decode("utf-16", "replace")
    head = data[:4096]
    if b"\x00" not in head:
        return data.decode("utf-8", "replace")
    if len(head) >= 4:
        even, odd = head[0::2], head[1::2]
        if odd.count(0) >= 0.9 * len(odd) and even.count(0) <= 0.1 * len(even):
            return data.decode("utf-16-le", "replace")
        if even.count(0) >= 0.9 * len(even) and odd.count(0) <= 0.1 * len(odd):
            return data.decode("utf-16-be", "replace")
    return None


def read_list_file(path):
    """A small text file someone saved by hand (a word list, a profile, the
    accepted list): UTF-8 or UTF-16. Raises ValueError in plain words."""
    try:
        with open(path, "rb") as fh:
            data = fh.read()
    except OSError as e:
        raise ValueError("it can't be opened (%s)" % e.strerror)
    if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return data.decode("utf-16", "replace")
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = decode_text(data)
        if text is not None and b"\x00" in data[:4096]:
            return text
        raise ValueError("it isn't saved as UTF-8 or UTF-16 text; save it as UTF-8")


def _is_date(digits):
    """A run of digits in a file name that is a date (and maybe a time): 20261025."""
    if len(digits) not in (8, 12, 14):
        return False
    y, mo, d = int(digits[:4]), int(digits[4:6]), int(digits[6:8])
    return 1990 <= y <= 2099 and 1 <= mo <= 12 and 1 <= d <= 31


# --- showing findings without repeating them -------------------------------------

def mask(text):
    """Hide all but the first and last character of every word of 3+ letters or digits."""
    def one(m):
        s = m.group(0)
        return s[0] + "*" * (len(s) - 2) + s[-1]
    text = text.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    if len(text) > MAX_EXCERPT:
        text = text[:MAX_EXCERPT] + "..."
    return re.sub(r"[^\W_]{3,}", one, text)


_WORD_GAP = r"(?:[\W_]|%[0-9A-Fa-f]{2})*"
_WORD_GAP_BYTES = rb"(?:[^A-Za-z0-9\x80-\xff]|%[0-9A-Fa-f]{2}){0,3}"
_WORD_GAP_UTF16 = rb"(?:[^A-Za-z0-9]\x00){0,3}"
_WORD_GAP_UTF16BE = rb"(?:\x00[^A-Za-z0-9]){0,3}"


def word_pattern(word):
    """One private word as a pattern: its parts may be joined by any spaces,
    punctuation or %-codes (or nothing), and a short word only counts whole."""
    parts = re.findall(r"[^\W_]+", word)
    if not parts:
        return re.escape(word)
    core = _WORD_GAP.join(re.escape(p) for p in parts)
    if len("".join(parts)) <= 4:
        core = r"(?<![^\W_])" + core + r"(?![^\W_])"
    return core


def word_byte_patterns(word):
    """The same, as bytes in UTF-8 and UTF-16 (both byte orders), for binary
    files. Words shorter than five letters are left out there: they turn up in
    picture data by chance."""
    parts = re.findall(r"[^\W_]+", word)
    if len("".join(parts)) < 5:
        return []
    return [re.compile(_WORD_GAP_BYTES.join(re.escape(p.encode("utf-8")) for p in parts), re.I),
            re.compile(_WORD_GAP_UTF16.join(re.escape(p.encode("utf-16-le")) for p in parts), re.I),
            re.compile(_WORD_GAP_UTF16BE.join(re.escape(p.encode("utf-16-be")) for p in parts), re.I)]


def _identity(text):
    return re.sub(r"\s+", " ", text).strip().lower()


class Report:
    """Collects findings; masks private words and long numbers in file names."""

    def __init__(self, words, public_ids=(), accepted=(), setup=()):
        self.word_re = (re.compile("|".join(word_pattern(w) for w in words), re.I)
                        if words else None)
        self.word_bytes = [p for w in words for p in word_byte_patterns(w)]
        self.public_ids = {_identity(i) for i in public_ids}
        self.accepted = set(accepted)
        self.accepted_used = set()
        self.accepted_count = 0
        self.setup = {p.lower() for p in setup}
        self.setup_names = {p.lower().rsplit("/", 1)[-1] for p in setup}
        self.blob = ()          # git hashes of the file version being checked now
        self.scanned = set()    # git hashes of every file version already checked
        self.findings = []
        self._seen = set()
        self.counts = {"files": 0, "staged": 0, "commits": 0, "tags": 0, "versions": 0}

    def where(self, path):
        """A file name made safe to print: private words and numbers of four or
        more digits hidden, and the names of saved profiles (often a person's
        name) too."""
        if self.word_re:
            path = self.word_re.sub(lambda m: mask(m.group(0)), path)

        def profile(m):
            name = m.group(2)
            return m.group(1) + (name if name.lower() in ("readme.md", ".gitkeep") else mask(name))
        path = re.sub(r"(?i)(profiles[\\/])([^\\/!]+)", profile, path)
        return re.sub(r"\d{4,}", lambda m: mask(m.group(0)), path)

    def add(self, cls, where, shown="", note=""):
        """One finding: `shown` is the matched text (printed masked), `note` a plain description."""
        text = " ".join(t for t in (note, mask(shown) if shown else "") if t)
        for b in self.blob:
            if (b, cls) in self.accepted:
                self.accepted_used.add((b, cls))
                key = ("accepted", cls, where, text)
                if key not in self._seen:
                    self._seen.add(key)
                    self.accepted_count += 1
                return
        key = (cls, where, text)
        if key in self._seen:
            return
        self._seen.add(key)
        self.findings.append((cls, where, text))


# --- the checks ------------------------------------------------------------------

def check_name(rep, where, path):
    """Problems with a file's name or folder."""
    p = path.replace("\\", "/")
    low = p.lower()
    parts = [s for s in low.split("/") if s]
    if not parts:
        return
    name, folders = parts[-1], parts[:-1]
    ext = os.path.splitext(name)[1]
    m = re.search(r"(?:car(?:_spec|_num|_decal)?|(?<![a-z])(?:helmet|suit))_\d+", name)
    if m:
        rep.add("id", where, m.group(0))
    elif ext in ID_NAME_EXTS:
        for m in re.finditer(r"\d{5,}", name):
            if not _is_date(m.group(0)):
                rep.add("id", where, m.group(0))
                break
    if ext in RACE_EXTS:
        rep.add("race", where, note="an iRacing %s file" % ext)
    if "profiles" in folders and name not in ("readme.md", ".gitkeep"):
        rep.add("private", where, note="a file in a profiles folder, where saved settings stay")
    if "out" in folders:
        rep.add("private", where, note="a file in an out folder, the working folder")
    if (name == ".env" or name.endswith(".env")
            or (name.startswith(".env.") and name != ".env.example")):
        rep.add("private", where, note="a .env settings file")
    if name.endswith(".local.json"):
        rep.add("private", where, note="a .local.json settings file")
    if name in KEY_NAMES or ext in KEY_EXTS:
        rep.add("secret", where, note="a key or credentials file")
    if any(re.match(r"evidence(?:[\W_]|$)", f) for f in folders):
        rep.add("private", where, note="an evidence folder")
    if re.match(r"(?:users|home)/[^/]+/", low):
        rep.add("path", where, note="a home folder from a computer")
    if "_template_" in low or (ext in TEMPLATE_EXTS and re.search(r"(?:^|[\W_])template[\W_]", name)):
        rep.add("template", where, note="named like an iRacing paint template")
    if ext == ".psd":
        rep.add("template", where, note="a Photoshop file, the format of iRacing's templates")
    if ext == ".mip":
        rep.add("template", where, note="a .mip file, which iRacing makes from a paint")
    if "template-overview" in low:
        rep.add("template", where, note="a picture of an iRacing template")
    if low in rep.setup or name in rep.setup_names:
        rep.add("template", where, note="made from iRacing's template by the one-time setup step")
    # the name itself: a folder path, scratch folder, chat link or word in it
    check_text(rep, where, p, lines=False)


def check_text(rep, where, text, lines=True, words=True, binary=False):
    """Every text pattern, plus the private words, in one piece of text.

    binary: the text is strings pulled out of a binary file, so only the
    patterns that can't turn up there by chance are used."""
    newlines = []

    def at(offset):
        if not lines:
            return where
        if not newlines:
            newlines.append([m.start() for m in re.finditer("\n", text)])
        return "%s:%d" % (where, bisect.bisect_left(newlines[0], offset) + 1)

    def look(piece, offset, original=None):
        spans = {}          # class -> spans already reported, so one path isn't reported twice
        for cls, pattern, allow, in_binary in TEXT_PATTERNS:
            if binary and not in_binary:
                continue
            for m in pattern.finditer(piece):
                if allow and allow(m):
                    continue
                if original is not None and m.group(0) in original:
                    continue        # already seen without the decoding
                seen = spans.setdefault(cls, [])
                i = bisect.bisect_right(seen, (m.start(), len(piece) + 1))
                if any(seen[j][1] >= m.end() for j in range(max(0, i - 16), i)):
                    continue
                bisect.insort(seen, m.span())
                rep.add(cls, at(offset + (0 if original is not None else m.start())), m.group(0))
        if words and rep.word_re:
            for m in rep.word_re.finditer(piece):
                if original is not None and m.group(0) in original:
                    continue
                rep.add("word", at(offset + (0 if original is not None else m.start())), m.group(0))

    look(text, 0)
    # URL-encoded text (%5C, %3A, %2F ...): look again at those lines, decoded
    if "%" in text:
        for m in _PCT_LINE.finditer(text):
            decoded = urllib.parse.unquote(m.group(0), errors="replace")
            if decoded != m.group(0):
                look(decoded, m.start(), original=m.group(0))


def _png_text(data):
    """The text chunks of a PNG (tEXt, zTXt, iTXt), unpacked."""
    out, pos = [], 8
    while pos + 8 <= len(data):
        n = int.from_bytes(data[pos:pos + 4], "big")
        kind, body = data[pos + 4:pos + 8], data[pos + 8:pos + 8 + n]
        pos += 12 + n
        try:
            if kind == b"tEXt":
                key, _, text = body.partition(b"\x00")
                out.append((key + b" " + text).decode("latin-1"))
            elif kind == b"zTXt":
                key, rest = body.split(b"\x00", 1)
                out.append((key + b" " + _unpack(rest[1:])).decode("latin-1"))
            elif kind == b"iTXt":
                key, rest = body.split(b"\x00", 1)
                compressed = rest[:1] == b"\x01"
                lang_and_text = rest[2:].split(b"\x00", 2)
                text = lang_and_text[2] if len(lang_and_text) == 3 else b""
                out.append((key + b" " + (_unpack(text) if compressed else text))
                           .decode("utf-8", "replace"))
        except (ValueError, zlib.error):
            pass
        if kind == b"IEND":
            break
    return out


def _unpack(data, wbits=zlib.MAX_WBITS):
    """zlib (or with wbits=31, gzip) data unpacked, up to MAX_UNPACK bytes."""
    return zlib.decompressobj(wbits).decompress(data, MAX_UNPACK)


def _pdf_streams(data):
    """The packed (Flate) streams of a PDF, unpacked."""
    out = []
    for m in re.finditer(rb"stream\r?\n", data):
        end = data.find(b"endstream", m.end())
        if end < 0:
            break
        try:
            out.append(_unpack(data[m.end():end]))
        except zlib.error:
            pass
    return out


def check_binary(rep, where, data):
    """Folder paths, chat links, tokens and private words inside a binary file."""
    inside = where + " (inside the file)"
    chunks = [data]
    if data[:5] == b"%PDF-":
        chunks += _pdf_streams(data)
    for chunk in chunks:
        for pattern in BINARY_PATTERNS:
            m = pattern.search(chunk)
            if m:
                shown = m.group(0).replace(b"\x00", b"").decode("latin-1")
                rep.add("path", inside, shown)
        for pattern in rep.word_bytes:
            m = pattern.search(chunk)
            if m:
                shown = m.group(0).replace(b"\x00", b"").decode("utf-8", "replace")
                rep.add("word", inside, shown)
        strings = [m.group(0).decode("latin-1") for m in _ASCII_RUN.finditer(chunk)]
        strings += [m.group(0).decode("utf-16-le") for m in _UTF16_RUN.finditer(chunk)]
        strings += [m.group(0).decode("utf-16-be") for m in _UTF16BE_RUN.finditer(chunk)]
        if strings:
            check_text(rep, inside, "\n".join(strings), lines=False, words=False, binary=True)
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        for text in _png_text(data):
            check_text(rep, where + " (text stored in the picture)", text, lines=False)


def check_content(rep, where, path, data, depth=0):
    """Check one file's contents: open zips and .gz files, scan binaries, read text."""
    low = path.lower()
    packed = low.endswith((".zip", ".gz")) or data[:4] == b"PK\x03\x04" or data[:2] == b"\x1f\x8b"
    if packed and depth >= MAX_DEPTH:
        rep.add("unreadable", where, note="packed inside %d other zip or .gz files; only its raw "
                "bytes were checked" % depth)
        check_binary(rep, where, data)
        return
    if data[:2] == b"\x1f\x8b":
        try:
            inner = _unpack(data, 31)
        except zlib.error:
            rep.add("unreadable", where, note="a damaged .gz file")
            check_binary(rep, where, data)
            return
        inner_path = path[:-3] if low.endswith(".gz") else path
        check_content(rep, where + " (unpacked)", inner_path, inner, depth + 1)
        return
    if low.endswith(".zip") or data[:4] == b"PK\x03\x04":
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                if z.comment:
                    check_text(rep, where + " (zip comment)", z.comment.decode("utf-8", "replace"),
                               lines=False)
                for info in z.infolist():
                    inner = "%s!%s" % (where, rep.where(info.filename))
                    check_name(rep, inner, info.filename)
                    if info.comment:
                        check_text(rep, inner + " (comment)", info.comment.decode("utf-8", "replace"),
                                   lines=False)
                    if info.is_dir():
                        continue
                    if info.file_size > MAX_UNPACK:
                        rep.add("unreadable", inner, note="too big to unpack here")
                        continue
                    try:
                        inner_data = z.read(info)
                    except (RuntimeError, zipfile.BadZipFile, NotImplementedError, OSError,
                            zlib.error):
                        rep.add("unreadable", inner, note="a locked or damaged file in the zip")
                        continue
                    check_content(rep, inner, info.filename, inner_data, depth + 1)
        except zipfile.BadZipFile:
            check_binary(rep, where, data)
            if low.endswith(".zip"):
                rep.add("unreadable", where, note="a damaged zip")
        return
    if os.path.splitext(low)[1] not in BINARY_EXTS:
        text = decode_text(data)
        if text is not None:
            check_text(rep, where, text)
            return
    check_binary(rep, where, data)


def blob_hash(data, algo="sha1"):
    """The git hash of a file with these bytes."""
    h = hashlib.new(algo)
    h.update(b"blob %d\x00" % len(data))
    h.update(data)
    return h.hexdigest()


def blob_ids(data, algo="sha1"):
    """The git hashes these bytes can have: as they are, and with Windows line
    endings made plain (git stores text that way when it changes them)."""
    ids = {blob_hash(data, algo)}
    if b"\r\n" in data:
        ids.add(blob_hash(data.replace(b"\r\n", b"\n"), algo))
    return ids


def check_blob(rep, where, path, data, ids):
    """Check one version of a file, remembering which git hashes it covers."""
    rep.blob = tuple(ids)
    try:
        check_content(rep, where, path, data)
    finally:
        rep.blob = ()
    rep.scanned.update(ids)


def check_file(rep, where, full, rel, algo="sha1"):
    """Check one file on disk: its name, then its contents. Returns its git hashes."""
    check_name(rep, where, rel)
    if os.path.islink(full):
        target = os.readlink(full)
        ids = {blob_hash(target.encode("utf-8", "replace"), algo)}
        rep.blob = tuple(ids)
        check_text(rep, where, target, lines=False)
        rep.blob = ()
        rep.scanned.update(ids)
        return ids
    try:
        with open(full, "rb") as fh:
            data = fh.read()
    except OSError:
        rep.add("unreadable", where, note="it can't be opened")
        return set()
    rep.counts["files"] += 1
    ids = blob_ids(data, algo)
    check_blob(rep, where, rel, data, ids)
    return ids


# --- git ---------------------------------------------------------------------------

class GitError(Exception):
    pass


def git(root, *args, input_text=None):
    """Run a read-only git command in `root` and return its output as bytes."""
    cmd = ["git", "-c", "core.quotepath=off", "-c", "core.fsmonitor=false"] + list(args)
    try:
        r = subprocess.run(cmd, cwd=root, capture_output=True,
                           input=None if input_text is None else input_text.encode())
    except OSError as e:
        raise GitError("git couldn't be started (%s). Is git installed?" % e)
    if r.returncode != 0:
        raise GitError((r.stderr.decode("utf-8", "replace").strip().splitlines() or ["?"])[-1])
    return r.stdout


def is_git_top(root):
    """True when `root` is the top folder of a git repository (or worktree)."""
    try:
        top = git(root, "rev-parse", "--show-toplevel").decode("utf-8", "replace").strip()
        return os.path.samefile(top, root)
    except (GitError, OSError):
        return False


def object_format(root):
    """The hash git uses in this repository: sha1, or sha256."""
    try:
        fmt = git(root, "rev-parse", "--show-object-format").decode().strip()
        return fmt if fmt in ("sha1", "sha256") else "sha1"
    except GitError:
        return "sha1"


def read_blobs(root, shas):
    """(hash, bytes) for each file version, read through one git process
    (bytes is None when git doesn't have it)."""
    if not shas:
        return
    proc = subprocess.Popen(["git", "-c", "core.fsmonitor=false", "cat-file", "--batch"],
                            cwd=root, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        for sha in shas:
            proc.stdin.write((sha + "\n").encode())
            proc.stdin.flush()
            header = proc.stdout.readline().split()
            if len(header) < 3:
                yield sha, None
                continue
            data = proc.stdout.read(int(header[2]))
            proc.stdout.read(1)
            yield sha, (data if header[1] == b"blob" else None)
    finally:
        proc.stdin.close()
        proc.stdout.close()
        proc.wait()


def walk(folder):
    found = []
    for dp, dn, fs in os.walk(folder):
        dn[:] = [d for d in dn if d != ".git"]
        for f in fs:
            found.append(os.path.relpath(os.path.join(dp, f), folder).replace("\\", "/"))
    return sorted(found)


def check_project(rep, root):
    """Every file git would commit (or every file, outside git). Returns their paths."""
    if not is_git_top(root):
        files = walk(root)
        for rel in files:
            check_file(rep, rep.where(rel), os.path.join(root, *rel.split("/")), rel)
        return files
    algo = object_format(root)
    index = {}
    for rec in git(root, "ls-files", "-s", "-z").decode("utf-8", "replace").split("\x00"):
        meta, _, path = rec.partition("\t")
        fields = meta.split()
        if path and len(fields) >= 2 and fields[0] != "160000":    # 160000: a submodule
            index.setdefault(path, []).append(fields[1])
    others = [p for p in git(root, "ls-files", "-z", "--others", "--exclude-standard")
              .decode("utf-8", "replace").split("\x00") if p]
    files = sorted(set(index) | set(others))
    pending = []        # (path, hash, what) of versions git has that the folder doesn't
    for rel in files:
        full = os.path.join(root, *rel.split("/"))
        if os.path.isfile(full) or os.path.islink(full):
            ids = check_file(rep, rep.where(rel), full, rel, algo)
            pending += [(rel, sha, "git's version, which differs from the folder")
                        for sha in index.get(rel, [])
                        if sha not in ids]
        else:
            pending += [(rel, sha, "deleted here, but still in git") for sha in index.get(rel, [])]
    for (rel, sha, what), (_, data) in zip(pending, read_blobs(root, [s for _, s, _ in pending])):
        where = "%s (%s)" % (rep.where(rel), what)
        if what.startswith("deleted"):
            check_name(rep, where, rel)
        if data is None:
            rep.add("unreadable", where, note="git can't read it")
            continue
        rep.counts["staged"] += 1
        check_blob(rep, where, rel, data, {sha})
    return files


def check_history(rep, root, current_paths):
    """Commits, tags, branch names and every old version of every file."""
    def person(label, who):
        # a commit identity listed as public in the word list: patterns only
        check_text(rep, label, who, lines=False, words=_identity(who) not in rep.public_ids)

    # commit messages, authors and committers
    log = git(root, "log", "--all", "--format=%H%x1f%an <%ae>%x1f%cn <%ce>%x1f%B%x1e")
    for rec in log.decode("utf-8", "replace").split("\x1e"):
        rec = rec.strip("\n")
        if not rec:
            continue
        sha, author, committer, body = (rec.split("\x1f", 3) + ["", "", ""])[:4]
        short = sha[:7]
        rep.counts["commits"] += 1
        person("commit %s author" % short, author)
        person("commit %s committer" % short, committer)
        check_text(rep, "commit %s message" % short, body)
    # tags: version numbers only; nothing private in the tagger or message (a
    # lightweight tag has neither: it is only a name for a commit)
    tags = git(root, "for-each-ref", "refs/tags", "--format=%(refname:strip=2)%1f%(objecttype)"
               "%1f%(taggername) %(taggeremail)%1f%(contents)%1e")
    for rec in tags.decode("utf-8", "replace").split("\x1e"):
        rec = rec.strip("\n")
        if not rec:
            continue
        name, kind, tagger, body = (rec.split("\x1f", 3) + ["", "", ""])[:4]
        rep.counts["tags"] += 1
        shown = rep.where(name)
        if not re.fullmatch(r"v\d+\.\d+\.\d+", name):
            rep.add("tag", "tag " + shown, note="only version numbers such as v1.2.3 are allowed")
        check_text(rep, "tag " + shown, name, lines=False)
        if kind == "tag":
            person("tag %s tagger" % shown, tagger)
            check_text(rep, "tag %s message" % shown, body)
    # branch names
    for ref in git(root, "for-each-ref", "--format=%(refname)", "refs/heads",
                   "refs/remotes").decode("utf-8", "replace").splitlines():
        check_text(rep, "branch " + rep.where(ref), ref, lines=False)

    # every file version reachable from any branch or tag
    objects = git(root, "rev-list", "--objects", "--all").decode("utf-8", "replace")
    first_path = {}
    for line in objects.splitlines():
        sha, _, path = line.partition(" ")
        if sha and sha not in first_path:
            first_path[sha] = path
    names = set(p for p in first_path.values() if p)
    names.update(p for p in git(root, "log", "--all", "--format=", "--name-only")
                 .decode("utf-8", "replace").splitlines() if p)
    for path in sorted(names - set(current_paths)):
        check_name(rep, "history: " + rep.where(path), path)

    kinds = git(root, "cat-file", "--batch-check=%(objectname) %(objecttype)",
                input_text="\n".join(first_path) + "\n")
    # only the versions whose bytes haven't been checked already
    blobs = [l.split()[0] for l in kinds.decode().splitlines()
             if l.endswith(" blob") and l.split()[0] not in rep.scanned]
    for sha, data in read_blobs(root, blobs):
        if data is None:
            continue
        path = first_path.get(sha) or sha
        rep.counts["versions"] += 1
        check_blob(rep, "history: %s (old version %s)" % (rep.where(path), sha[:7]), path, data, {sha})


# --- private words and the accepted list -------------------------------------------

class ListError(Exception):
    pass


def load_words(root, word_files):
    """The private words: from --words (or profiles/private-words.txt) and profiles/*.json.

    Returns (words, public identities, sources, notes). Words shorter than 3
    characters are dropped: they would match almost anything."""
    files = list(word_files)
    if not files:
        default = os.path.join(root, "profiles", "private-words.txt")
        if os.path.isfile(default):
            files.append(default)
    words, public, sources, notes = [], [], [], []
    for path in files:
        try:
            text = read_list_file(path)
        except ValueError as e:
            raise ListError("can't read the word list %s: %s." % (os.path.basename(path), e))
        for line in text.splitlines():
            w = line.split("#", 1)[0].strip()
            if w.lower().startswith("public:"):
                if w[7:].strip():
                    public.append(w[7:].strip())
            elif w:
                words.append(w)
        sources.append(os.path.basename(path))
    profiles = 0
    for path in sorted(glob.glob(os.path.join(root, "profiles", "*.json"))):
        try:
            data = json.loads(read_list_file(path))
        except ValueError:
            notes.append("a saved profile, profiles/%s, couldn't be read, so its values aren't "
                         "looked for" % mask(os.path.basename(path)))
            continue
        if not isinstance(data, dict):
            continue
        found = False
        for key in ("id", "driver"):
            if isinstance(data.get(key), (str, int)) and str(data[key]).strip():
                words.append(str(data[key]).strip())
                found = True
        protect = data.get("protect_ids") or []
        for value in [protect] if isinstance(protect, (str, int)) else protect:
            if isinstance(value, (str, int)) and str(value).strip():
                words.append(str(value).strip())
                found = True
        profiles += found
    if profiles:
        sources.append("%d saved profile%s in profiles/" % (profiles, "" if profiles == 1 else "s"))
    unique = {}
    for w in words:
        if len(w) >= 3 and w.lower() not in EXAMPLE_WORDS:
            unique.setdefault(w.lower(), w)
    return sorted(unique.values(), key=len, reverse=True), public, sources, notes


def load_accepted(path):
    """{(git hash, kind)} from the accepted list."""
    try:
        text = read_list_file(path)
    except ValueError as e:
        raise ListError("can't read the accepted list %s: %s." % (os.path.basename(path), e))
    accepted = set()
    for n, line in enumerate(text.splitlines(), 1):
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        fields = line.split()
        if (len(fields) != 2 or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", fields[0].lower())
                or fields[1] not in CLASSES):
            raise ListError("line %d of the accepted list %s isn't '<full git hash> <kind>' (the "
                            "kinds are: %s)." % (n, os.path.basename(path), ", ".join(CLASSES)))
        accepted.add((fields[0].lower(), fields[1]))
    return accepted


# --- main --------------------------------------------------------------------------

def main(argv=None):
    try:
        sys.stdout.reconfigure(errors="backslashreplace")
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser(
        description="Look for things that look private (numbers shaped like customer IDs, "
                    "folder paths from a computer, race results, links to AI chats, iRacing "
                    "template files, keys) before the project is published. Names can't be "
                    "recognised by a pattern: put them in your private word list. It only reads.",
        epilog="Exit code 0 when nothing is found, 1 when something is, 2 when it "
               "couldn't run. Whatever it finds is printed with all but the first and "
               "last character of each word hidden.")
    ap.add_argument("--history", action="store_true",
                    help="also check every commit message, author and committer, every tag "
                         "and branch name, and every version of every file in the history")
    ap.add_argument("--path", action="append", default=[], metavar="FOLDER",
                    help="also check this folder or file, which isn't in git (for example "
                         "release notes or an unzipped download); zips inside are opened. "
                         "Can be given more than once")
    ap.add_argument("--words", action="append", default=[], metavar="FILE",
                    help="your private words, one per line, '#' starts a comment (default: "
                         "profiles/private-words.txt if it exists). A line 'public: Name "
                         "<email>' names a commit identity you publish on purpose. The id, "
                         "driver and protect_ids values in profiles/*.json are always added")
    ap.add_argument("--accepted", metavar="FILE",
                    help="the list of findings already looked at and accepted (default: "
                         + ACCEPTED_FILE + " in the copy being checked, if it is there)")
    ap.add_argument("--root", default=ROOT, metavar="FOLDER",
                    help="the copy of the project to check (default: the one this tool is in)")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print("Can't check: the folder %s doesn't exist." % args.root)
        return 2
    for p in args.path:
        if not os.path.exists(p):
            print("Can't check: %s doesn't exist." % p)
            return 2
    for w in args.words:
        if not os.path.isfile(w):
            print("Can't check: the word list %s doesn't exist." % w)
            return 2
    accepted_path = args.accepted or os.path.join(root, *ACCEPTED_FILE.split("/"))
    if args.accepted and not os.path.isfile(args.accepted):
        print("Can't check: the accepted list %s doesn't exist." % args.accepted)
        return 2

    try:
        words, public, sources, notes = load_words(root, args.words)
        accepted = load_accepted(accepted_path) if os.path.isfile(accepted_path) else set()
    except ListError as e:
        print("Can't check: %s" % e)
        return 2
    rep = Report(words, public, accepted, setup_files([root, ROOT]))

    print("Privacy check")
    if words:
        print("  private words: %d, from %s (never shown)" % (len(words), ", ".join(sources)))
    else:
        print("  private words: none (no profiles/private-words.txt, no --words), so names "
              "can't be looked for")
    for note in notes:
        print("  note: " + note)

    try:
        files = check_project(rep, root)
    except GitError as e:
        print("Can't check: git said: %s" % e)
        return 2

    for target in args.path:
        base = os.path.basename(os.path.normpath(target)) or target
        if os.path.isfile(target):
            check_file(rep, rep.where(base), target, base)
            continue
        for rel in walk(target):
            check_file(rep, rep.where(base + "/" + rel), os.path.join(target, *rel.split("/")), rel)

    if args.history:
        if not is_git_top(root):
            print("Can't check the history: this folder isn't a git repository.")
            return 2
        try:
            check_history(rep, root, files)
        except GitError as e:
            print("Can't check the history: git said: %s" % e)
            return 2

    def count(n, what):
        return "%d %s%s" % (n, what, "" if n == 1 else "s")
    c = rep.counts
    checked = [count(c["files"], "file")]
    if c["staged"]:
        checked.append(count(c["staged"], "staged or deleted version"))
    if args.history:
        checked += [count(c["commits"], "commit"), count(c["tags"], "tag"),
                    count(c["versions"], "older file version")]
    print("  checked: " + ", ".join(checked))
    if rep.accepted_count:
        print("  accepted: %s already looked at and accepted (%s)"
              % (count(rep.accepted_count, "finding"), os.path.basename(accepted_path)))
    unused = len(rep.accepted - rep.accepted_used)
    if args.history and unused:
        print("  note: %s in %s matched nothing here. That's expected in a copy without the "
              "project's whole history; in the published project, a line that matches nothing "
              "can be removed." % (count(unused, "line"), os.path.basename(accepted_path)))
    print()
    for cls, where, shown in rep.findings:
        print("FOUND  %s  [%s]  %s" % (where, CLASSES[cls], shown))
    if rep.findings:
        print()
        n = len(rep.findings)
        print("Result: found %d thing%s that look%s private. Fix each one, or be sure it's "
              "fine, before anything is published." % (n, "" if n == 1 else "s",
                                                      "s" if n == 1 else ""))
        return 1
    print("Result: nothing private found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
