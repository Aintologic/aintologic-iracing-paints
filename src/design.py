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

"""Your own design: colours, finishes, stripes and team name for a team car.

A design is a small settings file (JSON) that all ten team-car builders
(every ``src/team_*.py``) read with ``--design``.  The same file works on
every car: each builder draws it through that car's own panels.  On every
car the number panels stay white, because iRacing prints the number on them.

    {
      "team_name": "EXAMPLE RACING",
      "colors":   { "body": "#14306E", "graphic": "#FFC20E",
                    "trim": "#F2F2F2", "lettering": "#F2F2F2" },
      "finishes": { "body": "metallic", "graphic": "gloss", "trim": "gloss" },
      "stripes":  "classic",
      "logo1": "my-logo.png",
      "logo2": "none"
    }

Every field is optional.  Anything left out keeps the example scheme, so an
empty file (or no ``--design`` at all) builds the black, papaya and white
example byte for byte.

    layout      classic   the example's stripes (the default, and the only
                          layout)
    team_name   your team name, in place of the big AINTOLOGIC lettering.  A
                small "made with AINTOLOGIC" line stays under it.
    badge_text  one to three characters for the round badge (on the hood,
                nose, roof, deck or just in front of the cockpit, depending on
                the car); default: your team name's initials.
    colors      body       the main colour of the car
                graphic    the wide stripe, and the small details that
                           match it
                trim       the thin lines either side of the stripe, and the
                           ring round the badge (not the number panels)
                lettering  your team name, the driver name, logo outlines
                Each is "#RRGGBB".
    finishes    body, graphic and trim, each one of: gloss, satin, matte,
                metallic, pearl, chrome, brushed (the lettering takes the
                trim's finish).  This is the finish map iRacing reads (the
                spec map): how each surface takes the light.
    stripes     classic (wide stripe and two thin lines), stripe-only,
                lines-only or none
    logo1/2     what goes in the car's two logo spots: an image file, "none"
                to leave the spot empty, or "placeholder" for YOUR LOGO.
                The spots themselves are fixed per car (its car map says
                where).

Where it lives: ``profiles/designs/<name>.json`` (profiles/ is never
committed, so your team name stays on your computer), or any path.  The
samples in ``examples/designs/`` work too: ``--design blue-and-yellow``.

Every shape is drawn through the car's measured panel map, so a line still
meets itself across every panel seam whatever the colours.  Colours, finishes
and the name are inputs; no car's geometry changes.
"""
import json
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import teamscheme as T

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESIGN_DIRS = [os.path.join(_ROOT, "profiles", "designs"),
               os.path.join(_ROOT, "examples", "designs")]

ROLES = ("body", "graphic", "trim", "lettering")
EXAMPLE_COLOURS = {"body": T.BLACK, "graphic": T.PAPAYA,
                   "trim": T.WHITE, "lettering": T.WHITE}
LAYOUTS = ("classic",)
STYLES = {"classic": (True, True), "stripe-only": (True, False),
          "lines-only": (False, True), "none": (False, False)}
# The finish map (spec map) value per finish: R metallic, G roughness
# (0 mirror .. 255 rough), B clear coat (0 none, 16 the shiniest .. 255 dull).
FINISHES = {
    "gloss":    (0, 35, 16),       # deep shine, like fresh paint
    "satin":    (0, 170, 200),     # a soft sheen: the example's body finish
    "matte":    (0, 225, 0),       # no clear coat, rough: flat
    "metallic": (215, 62, 16),     # metal flake under a full clear coat
    "pearl":    (110, 48, 16),     # a little flake: a softer glow than metallic
    "chrome":   (255, 4, 0),       # mirror metal
    "brushed":  (255, 105, 0),     # rough metal: a dull steel sheen
}
# what each layout uses when a finish is left out
DEFAULT_FINISHES = {
    "classic": {"body": "satin", "graphic": "gloss", "trim": "gloss", "lettering": "gloss"},
}
PARTS = ROLES                      # the parts a design can colour
FINISH_PARTS = ("body", "graphic", "trim")   # ... and finish (the lettering takes the trim's)
KEYS = ("layout", "team_name", "badge_text", "colors", "colours", "finishes",
        "stripes", "logo1", "logo2", "note")


class Design:
    """One car's resolved design.  The builders read its colours and finishes
    and ask it for the lettering, the badge and which stripe bands to draw."""

    def __init__(self, body=T.BLACK, graphic=T.PAPAYA, trim=T.WHITE,
                 lettering=T.WHITE, team_name=None, badge_text=None,
                 stripes="classic", logo1=None, logo2=None, source=None,
                 layout="classic", finishes=None):
        self.body, self.graphic = tuple(body), tuple(graphic)
        self.trim, self.lettering = tuple(trim), tuple(lettering)
        self.team_name = team_name or None
        self.badge_text = badge_text or None
        self.stripes = stripes
        self.stripe_on, self.lines_on = STYLES[stripes]
        self.logo1, self.logo2 = logo1, logo2
        self.source = source
        self.layout = layout
        self.finish_names = dict(finishes or {})       # only the ones the file named

    def finish(self, role):
        """The spec-map value for one part: the finish the settings file
        named, else the layout's default."""
        name = self.finish_names.get(role) or DEFAULT_FINISHES[self.layout][role]
        return FINISHES[name]

    @property
    def example_colours(self):
        return all(getattr(self, r) == EXAMPLE_COLOURS[r] for r in ROLES)

    @property
    def example(self):
        """True when this builds the example scheme exactly."""
        return (self.example_colours and self.team_name is None and self.layout == "classic"
                and self.stripes == "classic" and not self.finish_names)

    @property
    def shade(self):
        """The dark checker cells: graphite on the example's black, else a
        step from the body toward the lettering."""
        if self.example_colours:
            return T.GRAPHITE
        return mix(self.body, self.lettering, 0.16)

    @property
    def logo_colours(self):
        """Colours for a logo spot's mark (the YOUR LOGO placeholder's outline
        and tab).  Empty in the example scheme, so each spot keeps the colours
        it was locked with; your own image logos ignore them."""
        if self.example_colours:
            return {}
        return {"ink": self.lettering, "accent": self.graphic}

    # --- stripes (classic layout) ------------------------------------------
    def bands(self, triple):
        """Keep the bands of one stripe group that this style draws.  triple
        is [outer, middle, outer] in drawing order; the result keeps that
        order.  classic returns it unchanged."""
        if self.stripes == "classic":
            return triple
        out1, mid, out2 = triple
        keep = []
        if self.lines_on:
            keep.append(out1)
        if self.stripe_on:
            keep.append(mid)
        if self.lines_on:
            keep.append(out2)
        return keep

    # --- lettering and badge ------------------------------------------------
    def wordmark(self, h, **kw):
        """The AINTOLOGIC wordmark in this design's lettering and graphic
        colours (the example's white and papaya)."""
        return T.wordmark(h, ink=self.lettering, accent=self.graphic, **kw)

    def lettering_box(self, wm, credit=True):
        """The big lettering.  wm is the example wordmark the builder has
        already sized for this spot; with no team name it is returned as it
        is.  With one, the team name is drawn into the SAME box (so it lands
        wherever the wordmark was measured to land), with the small "made
        with AINTOLOGIC" line under it when credit is True."""
        if self.team_name is None:
            return wm
        return team_lettering(self.team_name, wm.size, self.lettering,
                              self.graphic, credit_line=credit)

    def roundel(self, d):
        """The round badge (hood, nose, roof, deck or scuttle, by car).
        The example badge by default; in your colours if you chose colours;
        your badge_text, or your initials once you give a team name."""
        text = self.badge_text or (initials(self.team_name) if self.team_name else None)
        if self.example_colours and text is None:
            return T.roundel(d)
        return team_badge(d, text, self.team_name or "", self.body,
                          self.graphic, self.lettering, self.graphic, self.shade)

    # --- the finish (spec map), classic layout ------------------------------
    def material_keys(self, body, graphic):
        """The colours the classic spec map sorts pixels by: body, graphic
        ("orange", the gloss pop) and the whites.  The example's list exactly
        by default."""
        keys = [("body", body), ("orange", graphic), ("white", T.WHITE)]
        if self.example_colours:
            return keys
        for c in (self.trim, self.lettering):
            if c != T.WHITE:
                keys.append(("white", c))
        return keys

    def spec_values(self, P):
        """The classic spec map's material table with this design's finishes
        swapped in where the settings file named them.  P is the car's own
        table; it comes back unchanged when no finish was named."""
        if not self.finish_names:
            return P
        P = dict(P)
        for role, slot in (("body", "body"), ("graphic", "orange"), ("trim", "white")):
            if role in self.finish_names:
                P[slot] = self.finish(role)
        return P

    def stripe_mask(self, a):
        """Pixels with a graphic-colour component, including the anti-aliased
        edges of small marks.  a is an int16 HxWx3 array.  The example scheme
        keeps its locked papaya hue test (which also catches the red safety
        marks); any other colours use the body-to-graphic line, so a red or
        orange BODY is never mistaken for stripe paint.  A blend of the body
        and a dark trim or lettering colour on a light body can lie the same
        way from the body as the graphic does; a pixel nearer the body-to-trim
        or body-to-lettering line than the body-to-graphic line is the soft
        edge of a thin line or a letter, not stripe paint."""
        if self.example_colours:
            return (a[..., 0] > 100) & (a[..., 0] - a[..., 2] > 80) & (a[..., 1] < a[..., 0] - 40)
        s = np.array(self.graphic, dtype=np.float32)
        b = np.array(self.body, dtype=np.float32)
        v = s - b
        vv = float((v * v).sum()) or 1.0
        p = a.astype(np.float32) - b
        t = (p * v).sum(axis=2) / vv
        off = np.sqrt(((p - t[..., None] * v) ** 2).sum(axis=2))
        m = (t >= 0.45) & (off <= 0.25 * np.sqrt(vv) + 12)
        if not (v * v).sum():
            return m
        for c in {tuple(self.trim), tuple(self.lettering)}:
            d = _off_line(a, self.body, c)
            if d is not None:
                m &= ~(d + STRIPE_EDGE_MARGIN < off)
        return m

    def warnings(self):
        """Plain-English notes about colour choices that will be hard to see."""
        out = []
        if contrast(self.lettering, self.body) < 3.0:
            out.append("the lettering colour is close to the body colour, so your "
                       "team name and driver name may be hard to read")
        shows, what = self.stripe_on, "wide stripe"
        if shows and contrast(self.graphic, self.body) < 1.25 and self.finish("graphic") == self.finish("body"):
            out.append("the graphic colour and finish are close to the body's, so the "
                       "%s will barely show" % what)
        if self.lines_on and contrast(self.trim, self.body) < 1.25 and self.finish("trim") == self.finish("body"):
            out.append("the trim colour and finish are close to the body's, so the thin "
                       "lines will barely show")
        return out


EXAMPLE = Design()


# --- colour helpers ---------------------------------------------------------
def mix(a, b, t):
    return tuple(int(round(x + (y - x) * t)) for x, y in zip(a, b))


def _lum(c):
    def ch(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


STRIPE_EDGE_MARGIN = 2.0    # stripe_mask(): a tie between two blends stays stripe paint


def _off_line(a, c0, c1):
    """Distance of every pixel of a (int16 HxWx3) from the colour line through
    c0 and c1 (stripe_mask's own 'off' measure); None if c0 == c1."""
    b = np.array(c0, dtype=np.float32)
    v = np.array(c1, dtype=np.float32) - b
    vv = float((v * v).sum())
    if not vv:
        return None
    p = a.astype(np.float32) - b
    t = (p * v).sum(axis=2) / vv
    return np.sqrt(((p - t[..., None] * v) ** 2).sum(axis=2))


def contrast(a, b):
    """WCAG contrast ratio, 1 (same) .. 21 (black on white)."""
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def parse_colour(v, where):
    if isinstance(v, (list, tuple)) and len(v) == 3 and all(isinstance(x, int) and 0 <= x <= 255 for x in v):
        return tuple(v)
    if isinstance(v, str):
        s = v.strip().lstrip("#")
        if len(s) == 6:
            try:
                return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))
            except ValueError:
                pass
    raise SystemExit('design: %s should be a colour like "#1A2B3C", not %r' % (where, v))


# --- the team name ----------------------------------------------------------
def _font(size):
    return T.wide_font(size)


def unsupported(text):
    """Characters the lettering font can't draw (it would print empty boxes)."""
    f = _font(64)

    def pixels(c):
        im = Image.new("L", (128, 128), 0)
        ImageDraw.Draw(im).text((16, 16), c, font=f, fill=255)
        return im.tobytes()

    blank = pixels(chr(0xE000))                # a private-use code: never in the font
    return sorted({c for c in text if c != " " and pixels(c) == blank})


def initials(name):
    words = [w for w in name.replace("-", " ").split() if w[:1].isalnum()]
    if not words:
        return name[:2].upper()
    if len(words) == 1:
        return (words[0] if len(words[0]) <= 3 else words[0][:2]).upper()
    return "".join(w[0] for w in words[:3]).upper()


def _line(text, cap, ink, track=0.08, k=4):
    """One line of the team name in the logo face, tight-cropped, at cap
    height `cap` output px.  Set glyph by glyph like the wordmark's tail
    (ink-tight widths, even tracking) but every glyph keeps its own height on
    one baseline, so hyphens, dots, descenders and accents sit where the font
    puts them.  BASIC layout: the same pixels on every computer."""
    H = max(4, int(round(cap * k)))
    probe = _font(200)
    nb = probe.getbbox("N")
    f = _font(max(4, int(round(200 * H / float(nb[3] - nb[1])))))
    nb = f.getbbox("N")
    capH = nb[3] - nb[1]
    sp = int(capH * track)
    space = int(capH * 0.45)
    boxes = [None if c == " " else f.getbbox(c) for c in text]
    ink_boxes = [b for b in boxes if b and b[2] > b[0]]
    if not ink_boxes:
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    top = min(b[1] for b in ink_boxes)
    bottom = max(b[3] for b in ink_boxes)
    w = sum((b[2] - b[0]) if b else space for b in boxes) + sp * max(0, len(text) - 1)
    im = Image.new("RGBA", (max(1, w) + 4, bottom - top + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 2
    for c, b in zip(text, boxes):
        if b is None:
            x += space + sp
            continue
        d.text((x - b[0], 2 - top), c, font=f, fill=tuple(ink) + (255,))
        x += (b[2] - b[0]) + sp
    im = im.crop(im.getbbox())
    return im.resize((max(1, im.width // k), max(1, im.height // k)), Image.LANCZOS)


def credit(h, ink, accent):
    """The small "made with AINTOLOGIC" line, h output px tall."""
    ai = int(round(h / 1.29))                # the wordmark's height is ~1.29x its AI cap
    wm = T.wordmark(max(4, ai), ink=ink, accent=accent)
    mw = T.small_caps("MADE WITH", max(3, int(round(ai * 0.72))), ink=ink)
    gap = max(2, int(h * 0.30))
    im = Image.new("RGBA", (mw.width + gap + wm.width, max(mw.height, wm.height)), (0, 0, 0, 0))
    im.alpha_composite(mw, (0, im.height - mw.height))       # both ink-tight at the bottom:
    im.alpha_composite(wm, (mw.width + gap, im.height - wm.height))   # one baseline
    return im


def team_lettering(name, box, ink, accent, credit_line=True):
    """The team name fitted into box (w, h), centred, on one line or two,
    whichever reads bigger; the credit line under it, right-aligned."""
    bw, bh = box
    bad = unsupported(name)
    if bad:
        raise SystemExit("design: the lettering font can't draw %s in the team name; "
                         "use plain letters, numbers and simple punctuation"
                         % " ".join(repr(c) for c in bad))
    area_h = bh * (0.74 if credit_line else 1.0)
    gap = bh * 0.07

    def fit(lines):
        probe = [_line(t, 100, ink) for t in lines]
        lh = max(p.height for p in probe) / 100.0          # line height per unit cap
        lw = max(p.width for p in probe) / 100.0
        n = len(lines)
        cap = min(bw / lw, (area_h - gap * (n - 1)) / (lh * n))
        return cap, lines

    options = [fit([name])]
    words = name.split()
    if len(words) > 1:
        best = min(range(1, len(words)),
                   key=lambda i: abs(len(" ".join(words[:i])) - len(" ".join(words[i:]))))
        options.append(fit([" ".join(words[:best]), " ".join(words[best:])]))
    cap, lines = max(options, key=lambda o: o[0])
    rows = [_line(t, cap, ink) for t in lines]
    block_w = max(r.width for r in rows)
    block_h = sum(r.height for r in rows) + int(gap) * (len(rows) - 1)
    cr = None
    if credit_line:
        ch = max(6, min(int(bh * 0.20), int(cap * 0.55)))
        cr = credit(ch, ink, accent)
        if cr.width > bw:
            cr = cr.resize((bw, max(1, int(cr.height * bw / cr.width))), Image.LANCZOS)
    total_h = block_h + ((int(gap) + cr.height) if cr else 0)
    im = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    y = max(0, (bh - total_h) // 2)
    for r in rows:
        im.alpha_composite(r, ((bw - r.width) // 2, y))
        y += r.height + int(gap)
    if cr:
        right = (bw + block_w) // 2
        im.alpha_composite(cr, (max(0, min(bw - cr.width, right - cr.width)), min(bh - cr.height, y)))
    return im


def team_badge(d, text, name, ground, ring, ink, accent, dark, k=4):
    """The round badge in the example's layout: disc, ring, a big mark, a
    small name line and the checker rule.  With text=None the big mark is the
    example AI and the name line is the AINTOLOGIC wordmark, in these colours;
    otherwise your initials and your team name."""
    D = d * k
    im = Image.new("RGBA", (D, D), (0, 0, 0, 0))
    g = ImageDraw.Draw(im)
    rw = max(k, int(D * 0.045))
    g.ellipse([0, 0, D - 1, D - 1], fill=tuple(ring) + (255,))
    g.ellipse([rw, rw, D - 1 - rw, D - 1 - rw], fill=tuple(ground) + (255,))
    if text is None:
        big = T.ai_letters(int(d * 0.30), ink, accent, k)
        small = T.wordmark(int(d * 0.065), ink, accent, k=k)
    else:
        big = _line(text, d * 0.30, ink)
        if big.width > d * 0.62:
            big = big.resize((int(d * 0.62), max(1, int(big.height * d * 0.62 / big.width))),
                             Image.LANCZOS)
        small = _line(name, d * 0.055, ink)
        if small.width > d * 0.66:
            small = small.resize((int(d * 0.66), max(1, int(small.height * d * 0.66 / small.width))),
                                 Image.LANCZOS)
    big = big.resize((big.width * k, big.height * k), Image.LANCZOS)
    by = int(D * 0.22) if text is None else int(D * 0.40 - big.height / 2)
    im.alpha_composite(big, (D // 2 - big.width // 2, by))
    if small.height >= 3:
        small = small.resize((small.width * k, small.height * k), Image.LANCZOS)
        im.alpha_composite(small, (D // 2 - small.width // 2, int(D * 0.645)))
    cr = T.checker_rule(int(d * 0.50), accent, dark, ink, k=k)
    cr = cr.resize((cr.width * k, cr.height * k), Image.LANCZOS)
    im.alpha_composite(cr, (D // 2 - cr.width // 2, int(D * 0.765)))
    return im.resize((d, d), Image.LANCZOS)


# --- loading ----------------------------------------------------------------
def find(spec):
    """A --design value -> the settings file's path: a path as given, else
    profiles/designs/<name>.json, else examples/designs/<name>.json."""
    if os.path.isfile(spec):
        return spec
    name = spec[:-5] if spec.lower().endswith(".json") else spec
    for d in DESIGN_DIRS:
        p = os.path.join(d, name + ".json")
        if os.path.isfile(p):
            return p
    raise SystemExit("design: no settings file %r (looked for it as a path, then in "
                     "profiles/designs/ and examples/designs/)" % spec)


def load(spec):
    """Read a design settings file.  None -> the example scheme."""
    if not spec:
        return EXAMPLE
    path = find(spec)
    # utf-8-sig: a file saved as "UTF-8 with BOM" (a Notepad choice, and what
    # Windows PowerShell 5.1 writes) reads the same as plain UTF-8
    with open(path, encoding="utf-8-sig") as fh:
        try:
            data = json.load(fh)
        except UnicodeDecodeError:
            raise SystemExit("design: %s is not saved as UTF-8 text; open it in Notepad, "
                             "choose File > Save as, set Encoding to UTF-8 and save it again"
                             % path)
        except ValueError as e:
            raise SystemExit("design: %s is not valid JSON (%s)" % (path, e))
    return from_dict(data, path)


def from_dict(data, source=None):
    if not isinstance(data, dict):
        raise SystemExit("design: the settings file should hold one { ... } object")
    unknown = sorted(set(data) - set(KEYS))
    if unknown:
        raise SystemExit("design: unknown setting(s) %s; the settings are %s"
                         % (", ".join(unknown), ", ".join(k for k in KEYS if k not in ("colours", "note"))))
    layout = data.get("layout", "classic")
    if layout not in LAYOUTS:
        raise SystemExit("design: layout should be one of %s, not %r" % (", ".join(LAYOUTS), layout))
    cols = data.get("colors", data.get("colours", {})) or {}
    if not isinstance(cols, dict):
        raise SystemExit('design: "colors" should be { "body": "#...", ... }')
    bad = sorted(set(cols) - set(PARTS))
    if bad:
        raise SystemExit("design: unknown colour(s) %s; the colours are %s"
                         % (", ".join(bad), ", ".join(PARTS)))
    c = dict(EXAMPLE_COLOURS)
    for r in ROLES:
        if r in cols:
            c[r] = parse_colour(cols[r], "colors." + r)
    fin = data.get("finishes", {}) or {}
    if not isinstance(fin, dict):
        raise SystemExit('design: "finishes" should be { "body": "metallic", ... }')
    bad = sorted(set(fin) - set(FINISH_PARTS))
    if bad:
        raise SystemExit("design: unknown part(s) in finishes: %s; the parts are %s%s"
                         % (", ".join(bad), ", ".join(FINISH_PARTS),
                            " (the lettering takes the trim's finish)" if "lettering" in bad else ""))
    for r, f in fin.items():
        if f not in FINISHES:
            raise SystemExit("design: finishes.%s should be one of %s, not %r"
                             % (r, ", ".join(FINISHES), f))
    style = data.get("stripes", "classic")
    if style not in STYLES:
        raise SystemExit("design: stripes should be one of %s, not %r"
                         % (", ".join(STYLES), style))
    name = data.get("team_name")
    if name is not None and not isinstance(name, str):
        raise SystemExit("design: team_name should be text")
    name = " ".join(name.split()) if name else None
    badge = data.get("badge_text")
    if badge is not None:
        badge = str(badge).strip()
        if not 1 <= len(badge) <= 3:
            raise SystemExit("design: badge_text should be one to three characters")
    for t in (name, badge):
        if t:
            u = unsupported(t)
            if u:
                raise SystemExit("design: the lettering font can't draw %s; use plain "
                                 "letters, numbers and simple punctuation"
                                 % " ".join(repr(x) for x in u))
    ds = Design(c["body"], c["graphic"], c["trim"], c["lettering"], name, badge,
                style, data.get("logo1"), data.get("logo2"), source, layout, fin)
    return ds
