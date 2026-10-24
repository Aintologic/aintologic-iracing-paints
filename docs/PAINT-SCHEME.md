# The example paint scheme

**Read this before putting the example scheme on a car.** This is the scheme. A new
car gets *this*, placed on *that car's* panel map. Nothing here is re-designed
per car; only the placements change.

This repo ships the AÏntologic scheme as a worked **example** you personalize.
Pass your own `--id` (your iRacing customer ID — the build writes
`car_<id>.tga`), `--driver` (the name on the driver strip) and two logo images
(`--logo1`, `--logo2`) for the two logo slots. With **no** flags the build
carries a neutral **"YOUR LOGO"** placeholder in both slots and a blank driver
strip, so it renders cleanly out of the box and is obviously yours to fill in.

Adopted 13 September 2026; **re-cut 14 September 2026 as v4.0** — the full-length
ribbon stripe was scrapped for a Sebring/Cobra language (fender
sashes + centred stripes through the hood roundel). First car: Global Mazda
MX-5 Cup (#67), ready-made paint in `paints/mx5-2016-global-cup/` — **the gold master** (v4.0 was the same design before the spec map, the logo slot 2 treatment and the quarter placement were finished).
(v3.0 was the papaya-body first pass, "much too orange"; v3.4–v3.6 were the
ribbon.) **Second car: FIA F4 (#148), ready-made paint in `paints/fia-f4/`** — the approved open-wheel adaptation
of this language. **Third car: Porsche 911 RSR (#102), ready-made paint in `paints/porsche-911-rsr/`** — the approved GT adaptation.
**Fourth car: Ray FF1600 (#163), ready-made paint in `paints/ray-ff1600/`** — the approved wingless / Formula
Ford adaptation, and the car that established the per-side placement rule
(section "The reference cars" below). **Fifth car: Ferrari 296 Challenge
(#203), ready-made paint in `paints/ferrari-296-challenge/`** — the
approved modern-GT adaptation. **Sixth car: Lotus 79 (#25), ready-made paint in `paints/lotus-79/`** — the approved historic Formula 1
adaptation. **Seventh car: HPD ARX-01c (#39), ready-made paint in `paints/hpd-arx-01c/`** — the approved **sports-prototype**
adaptation, and the car that proved a chassis can have *no usable rear-facing
surface at all*. **Eighth car: SCCA Spec Racer Ford (#23), ready-made paint in `paints/spec-racer-ford/`** — the approved **small
sports-racer** adaptation, approved on track. **Ninth car: Skip Barber
Formula 2000 (#1), ready-made paint in `paints/skip-barber-formula-2000/`** — the approved
**Formula 2000 school car** adaptation (the Ray layout on a car with small
wings), approved on the render. **Tenth car: Aston Martin Vantage GT3 EVO
(#206), ready-made paint in `paints/aston-martin-vantage-gt3-evo/`** — the
approved **modern-GT3** adaptation, approved on track. To put the
scheme on another car, start with "Measuring a new car" in `AGENTS.md`.

Why: the scheme takes its cue from McLaren's F1 colours — McLaren-style **black
with papaya as the accent** and white type — built around the AÏntologic logo
concepts (concept images kept outside the repo; they are the *spec* for the
marks, nothing from them ships as raster).

---

## The code

    src/teamscheme.py     the palette, every mark
    src/team_mx5.py       the MX-5 build - COPY THIS as the pattern for the
                          next car.  Rects, placements, the sash / centre
                          stripe geometry, the rear-quarter decals and the
                          spec-map variants (SPEC_VARIANTS) all live here.
    tools/probe.py        car-agnostic panel probe (grid / rect / bands)
    tools/contact.py      six-angle contact sheet out of the car viewer
    tools/zoom.py         crop + upscale a capture to read detail

Every mark is drawn in code from `fonts/Orbitron-Variable.ttf` (OFL) at
weight 800, plus geometry. `teamscheme.py` run on its own writes a proof
sheet of every mark on black and on papaya to `scheme_proof.png` in a scratch
folder.

## Palette

| name | hex | use |
|---|---|---|
| BLACK | `#0C0C0D` | **the body.** Dominant. Every mark sits on it, as the logo does. |
| PAPAYA | `#FF7A00` | **the accent.** The stripe, the A-bar, the diaeresis, the ring. Never a field. |
| WHITE | `#ECECEC` | all type, the coachline, the number panel |
| GRAPHITE | `#2E3034` | dark checker cells when the checkers sit on black |

Papaya is McLaren-adjacent by eye, not sampled from anything. Don't "correct"
it to a sampled value without looking at it on the car.

## The marks (all in `teamscheme.py`)

- **`wordmark(h)`** — AÏNTOLOGIC. Big "AÏ": a *drawn* pointed A with the
  papaya trapezoid in its crossbar, an Orbitron I with two papaya
  parallelograms leaning right as the diaeresis. "NTOLOGIC" in Orbitron on
  the same baseline at 72% of the AÏ cap height. **On black: ink WHITE,
  accent PAPAYA. On papaya: ink WHITE, accent BLACK.** Never papaya-on-papaya.
- **`ai_letters(h)`** — just the AÏ, for badges.
- **`checker_rule(w)`** — line / slanted 2×6 checker block / line. Goes
  *under* a wordmark. On black: PAPAYA + GRAPHITE cells. On papaya: WHITE +
  BLACK cells.
- **`roundel(d)`** — the team badge: black disc, papaya ring, AÏ, small
  wordmark, checker rule. Fender-crown scale (60–80 px on a 2048 map).
- **`number_panel(w, h)`** — flat white rounded panel, sized to cover the
  car's number block *completely*. iRacing stamps the number on top. **Set
  all three Car Number chips to `#0C0C0D`** in Paint Shop → Paint Your Car.
- **`small_caps(text, h)`** — condensed caps for secondary text.

Race-car furniture comes from `src/sponsors.py`, recoloured: `driver_strip`
(black face, white ink, papaya edge — the name comes from `--driver`, blank
with no flag), `cutoff_triangle`, `extinguisher_mark`, `tow_arrow` (white on
black), and the two **logo slots** — logo slot 1 (`--logo1`) and logo slot 2
(`--logo2`), each a user-supplied image that falls back to a neutral
"YOUR LOGO" placeholder.

## The layout language — v4.0, Sebring/Cobra

From a distance the car must read as: **a black car with a white | papaya |
white sash across each front fender and the same three bands running down
the centre line — nose, hood, boot lid, tail — through the orange-ringed
team badge on the hood; white AÏNTOLOGIC on the door; white number panel.**
That's the whole identity. Everything else is small.

Orange is the *subtle* colour. If a panel is mostly orange, it is wrong.
The band recipe everywhere is **orange = 2x white, small body-colour gaps**.

1. **The fender sash.** Three parallel bands on each FRONT fender only,
   at the rear of the fender, tucked behind the number panel (the panel
   sits in front of it), leaning top-forward / bottom-rearward (0.28), from
   the hood shut line down to the bottom of the number panel. Drawn in
   texels on the flank islands, not through a car-space table — the fender
   renders uniformly in texels (car map, v4.0). Both sides mirrored; the
   islands are not symmetric, so each side carries its own trim.
2. **The centre stripes.** White | papaya | white down the exact centre of
   the car: nose fascia + bumper faces, hood (front lip to cowl), boot lid
   up to the third brake light, tail face — interrupted deliberately by the
   rear wordmark, never painted over it. Centre every panel on the CAR
   (tail lights / Mazda badges), not on the panel's own graphics. Widths per
   panel are set so the rendered orange is the same fraction of car width
   front and rear (MX-5: 7.0%).
3. **The hood node.** The team badge (`roundel`, 250 px on the MX-5) with a
   body-colour gap, a WHITE ring, another gap. The centre stripes enter it
   from the front and leave it to the rear; the two sashes continue across
   the hood as feeders that bend to meet the ring radially. The seam where
   feeder meets sash is a real body crease — tune the join on the render
   from the poses you review from; identical texture widths and straight
   lines are not enough (car map, v4.0).
4. **AÏNTOLOGIC on the door**, white + papaya, ~45% of the door, centred.
   Text rule (Rule 4): upright on both sides, same distance from the nose.
5. **Number panel** on the number block, white; the sash passes behind it.
6. **Tail:** centre stripes above and below AÏNTOLOGIC + `checker_rule`;
   papaya tow arrow.
7. **Boot lid:** centre stripe through the Mazda badge; **logo slot 1**
   beside it, off the centre line — the boot lid is the MX-5's placement for
   that slot; the F4 uses its endplates (see the logo-slot-1 placement table
   below).
8. **Small stuff, restraint:** driver strip + cutoff + extinguisher at the
   belt at the door's leading edge; **logo slot 2 on each rear quarter, same
   rendered size and place both sides (placed as a screen rectangle through
   each island's fitted affine — the rear-quarter logo affine), nothing else
   there** (the team roundel and logo slot 1 came off the sides on
   2026-09-14). No AI clichés, no lore text (see the style rules).

## Material / spec map — APPROVED hierarchy (v4.1, "Satin-True")

R metallic is binary (and darkens the colour — never on papaya, never on
anything dark), G roughness, **B is clearcoat and INVERTED (16 = max
shine)**. `team_mx5.spec_from_colour()` derives the whole map from the
colour map by nearest colour, grows a 3-texel halo of the orange material
around every papaya mark (so the A-bar and the Ï dots survive texture
filtering), and writes every variant in `SPEC_VARIANTS`; B3 is the
default and the approved one:

    1. black body   (0, 170, 200)  the quiet background: satin-matte, low glare,
                                   no hotspot, no wet look
    2. white        (0,  55,  30)  brighter, crisp, catches light
    3. papaya       (0,  35,  16)  the strongest pop: glossiest surface, max coat
    4. logo faces   (0, 120, 150)  semi-matte vinyl; number blocks (0, 60, 110)
    orange brand marks (A-bar, dots, ring) = the papaya material

The hierarchy is the point: the black stays calm while the white and
especially the orange catch the light. B1/B2/B4 are kept in the code as the
history of how this was found (see playbook Rule 8). Note for a flat
vertical panel (a door): the orange there shows no highlight in the viewer
because nothing bright is reflected in it — that is geometry, not material;
the same material flashes on the fender crown and will on track.

## LOGO SLOT 1 — where the secondary logo sits, per car

Logo slot 1 is the secondary-logo position on the body. It takes your `--logo1`
image; with no flag it renders the neutral "YOUR LOGO" placeholder. Placement is
chassis-specific — the table below records where it reads well on each reference
car, so you have a worked example to copy from when you place your own logo.

Do not force it into a bad spot just to copy another car; find a clean,
readable secondary-logo location, keep the logo's aspect when practical, and
keep it visually subordinate to the AÏNTOLOGIC wordmark. Placements used on the
reference cars:

| car | where | why there |
|---|---|---|
| MX-5 #67 (v4.1) | boot lid, beside the centre stripe, off the centre line | the only flat rear surface that reads from behind |
| FIA F4 #148 (v1.1) | under the number on BOTH rear-wing endplate outer faces, 70 px | the endplates are the F4's cleanest small readable panels; a small wordmark there read truncated behind the tyre, the logo does not |
| Porsche 911 RSR #102 (v1.0) | lower rear quarter under the side intake, just behind the door seam, both sides, 76 px | a clean flat panel that reads from a level side; the RSR's wing endplates are not paintable |
| Ray FF1600 #163 (v1.0) | the sidepod TOP, aft of the sash, both sides, 92 px | **a Formula Ford has no wings and therefore no endplates** — the pod top is the Ray's cleanest flat readable secondary panel, and it reads from above and from any 3/4 |
| Ferrari 296 Challenge #203 (v1.0) | the hood's RIGHT rear corner, 92 px, reading from the front | the mirror spot of the hood number panel on the left corner; the rear is an open engine bay and the quarters already carry the intake + logo slot 2, so the hood corner is the Ferrari's cleanest readable secondary panel (reads from the front and from above) |
| Lotus 79 #25 (v1.0) | BOTH rear-wing endplate OUTER faces, upper panel above the tyre, 116 px | the endplates are the Lotus's biggest clean flat secondary panels and read from a level side and every rear 3/4; the pod faces carry AÏNTOLOGIC + the number, the tub sides logo slot 2, and the nose the number + logo slot 1 |
| HPD ARX-01c #39 (v1.0) | BOTH rear-wing endplate OUTER faces, **96 px left / 112 px right — deliberately different** | the endplates are the only clean flat rear-facing panels on the car (the rear is diffuser, exhaust and crash structure, and the wing has no usable rear face). The two endplates are **different UV islands with different sizes and aspect**, so logo slot 1 takes per-side coordinates and per-side sizes — the per-side placement rule below. Do not "correct" it |
| SCCA Spec Racer Ford #23 (v1.0) | the TAIL FACE, right of centre, 96 px — the mirror spot of the rear number panel | the tail face is the car's only flat rear-facing panel; its centre vent carries a small AÏNTOLOGIC and the rear number sits left of centre, so logo slot 1 balances it on the right; the doors carry AÏNTOLOGIC and the rear quarters the side numbers |
| Skip Barber Formula 2000 #1 (v1.0) | BOTH sidepod TOPS, aft of the sash, 100 px | the car has rear-wing endplates but the number blocks fill them, the sim forces a BFGoodrich decal on the wing top, and the tail is a narrow vented cover; the pod tops are the cleanest flat secondary panels and read from above and every 3/4 (the Ray's placement, chosen again on this chassis) |
| Aston Martin Vantage GT3 EVO #206 (v1.1) | the TAIL panel, right of centre, 72 px — the mirror spot of the rear number panel | the Spec Racer's rule on a GT3: the tail carries a small AÏNTOLOGIC above the centre sensor and the rear number left of centre, so logo slot 1 balances it on the right and reads from dead rear; the doors carry AÏNTOLOGIC, the haunches logo slot 2, the wing top AÏNTOLOGIC |

## THE PER-SIDE PLACEMENT RULE (established on the Ray, 2026-09-14)

Sponsor marks are normally mirrored to the same coordinates on both sides. On a
car whose **bodywork is asymmetric** — a blister, fairing or intake on one
flank only — that rule loses to legibility:

> **Do not force exact mirrored coordinates side-to-side. Optimise each side
> for visible fit.**

The Ray FF1600 is the first car to use it: its AÏNTOLOGIC wordmark sits at
texture x 1095 on the left and 1330 on the right, because a fairing blister
covers x ≈ 800..1090 on the right flank and nothing equivalent exists on the
left. **That asymmetry is approved and deliberate — a later rebuild that
"corrects" it to matching coordinates is a regression.** Where a car is
symmetric, keep the marks mirrored; the rule is an exception earned by
geometry, not a licence to place things by eye.

**The HPD ARX-01c (2026-09-17) extended it to the UV itself.** Its bodywork is
symmetric, but its two rear-wing endplates are packed as *different islands* —
the left outer face is 111×160 texels, the right is 130×174. Logo slot 1 is
therefore 96 px on the left and 112 px on the right, at unrelated coordinates,
so that it renders at the same size and place on screen. **Asymmetric texture
numbers in service of a symmetric render are the rule working, not a bug.**

## The reference cars (ten) — learn from all, copy none

**Tenth: the Aston Martin Vantage GT3 EVO v1.1** (2026-10-10, approved on
track; v1.0 the same day fixed one stripe) — the **modern-GT3** adaptation, the Ferrari's
structure on a UV unwrapped from above like the HPD (mirror row 1260, +x
rearward both sides). Centre stripe bumper → hood with the hood number panel
on top of it → windscreen banner AÏNTOLOGIC → the AÏ roundel node on the
roof (the hood number is on the centre line) → the open rear window → the
rear deck to the ducktail lip. The deck is a **leaky island whose car centre
is not the texture centre row** (1249, not 1260) — measured, not inherited;
v1.0 also split the stripe at a seam on a separate row at narrower widths,
which rendered narrower and stepped — one constant stripe was right. Sash behind the front-fender gill; AÏNTOLOGIC on the lower door;
logo slot 2 on the haunch; AÏNTOLOGIC on the wing top (the low-x half of the
wing island — the high-x half is the underside); tail = AÏNTOLOGIC + number +
logo slot 1. Two of the six template number blocks sit on no mesh.

**Ninth: the Skip Barber Formula 2000 v1.0** (2026-10-08, approved on the
render) — the **Formula 2000 school car** adaptation of the Ray layout. Side
islands mirror at row 1347.5 but the centre islands are self-symmetric at
1345.5 — **two mirror rows, four texels apart**. Nose centre stripes taper into
the tip, run through the nose number panel and under the nose latch to the AÏ
roundel node at the scuttle; behind the hoop **one stripe shrinks with the
tapering engine-cover spine** and carries that width down the tail to the
vents. Sash over each sidepod's leading edge (pod top → face); AÏNTOLOGIC on
the tub flank; logo slot 2 on the pod face; logo slot 1 on both pod tops because
the small rear-wing endplates are full of number. The sim forces BFGoodrich
on the wing top, and the endplate numbers stamp white until the chips are set.

**Eighth: the SCCA Spec Racer Ford v1.0** (2026-09-28, approved on track) — the
**small sports-racer** adaptation. Unwrapped from above like the HPD (mirror
row 1183.5, +x rearward both sides). The nose number sits ON the centre line,
so the roundel node lives on the rear deck; the front-fender sash crosses three
islands with different offsets and scales and is drawn in a car frame so it
renders straight; AÏNTOLOGIC on the doors; logo slot 2 on the rear fender tops;
logo slot 1 on the tail face opposite the rear number. Its template ships three
number-block configurations — probe which one the sim stamps.

The **MX-5 v4.1** stays the gold master: the brand and livery language,
the hood roundel as the node the stripes pass through, the white | orange |
white band recipe, the sponsor hierarchy and the Satin-True spec hierarchy
all come from it. The **FIA F4 v1.1** is the approved example of adapting
that language to a radically different chassis: the mapping / calibration
workflow (probe everything, read the render, per-column island edges, one
mirrored side), the formula-car stripe routing (nose centre stripes →
cockpit → twin ridge stripes on the engine cover), the sidepod sash + wordmark,
logo slot 2 on the engine cover, logo slot 1 on the endplates. The **Porsche 911
RSR v1.0** is the approved **GT / closed-body adaptation**: one continuous
centre stripe bumper → hood → roof roundel (the node moves to the ROOF on a
coupé whose hood carries the number) → rear glass → engine cover → tail
wordmark; a windscreen banner; the fender sash ahead of the door number
panel; logo slot 2 on the rear-quarter haunch; logo slot 1 on the lower rear
quarter — and, learned the hard way, **a chassis may earn its own local
treatment when the geometry defeats the recipe**: the RSR's hood louvres
made a constant-width stripe read as stacked fragments, so its hood is a
tapered V (constant papaya, white wedges tapering to the nose, bumper
orange only). That is a Porsche rule, not a family rule. The **Ray FF1600 v1.0** is
the approved **wingless / Formula Ford adaptation**: centre stripes that
**taper into the nose tip** (the tip island is a point — a constant-width
stripe swallows it), the nose number panel and the AÏ roundel node on the
nose top, the F4's sash retargeted over each sidepod's shoulder, twin papaya
lines hung off the tail-spine island's centre edge, AÏNTOLOGIC on the tub
flank, logo slot 2 on the sidepod face, logo slot 1 on the sidepod TOP because
there are no endplates — and **the per-side placement rule above**, the first car
where the two sides are deliberately not mirrored. The **Ferrari 296 Challenge v1.0** is the approved **modern-GT
adaptation**: the RSR's roof roundel and windscreen banner on a mid-engined
coupé; a centre stripe that **stops at the hood vent and resumes behind it**
(painted through, the slats read as ladder rungs — a vent is a gap, not an
obstacle to force); stripe stubs either side of the open engine window
instead of a forced route; the fender sash ahead of the door number;
AÏNTOLOGIC on the lower door band, the rear bumper and the wing top (the
rear view is mostly exposed mechanicals); logo slot 2 above the rear arch;
logo slot 1 on the hood corner opposite the hood number. Its sides are mirrored
— no asymmetry. The **Lotus 79 v1.0** is the approved **historic Formula 1
adaptation**: nose centre stripes through the nose number panel and the AÏ
roundel node; short engine-cover stubs either side of the exposed intake
trumpets (the Ferrari's gap rule again); the sash wrapping from the sidepod
top straight down the sidepod face; AÏNTOLOGIC on the tall pod faces and on
the rear wing — top surface and the flap's rear face, which is all a dead
rear view gets; logo slot 2 on the tub sides; logo slot 1 on both rear-wing
endplate outer faces. Mirrored, no asymmetry, and restrained enough that it
still reads as a black 1978 F1 car. The **HPD ARX-01c v1.0** is the approved
**sports-prototype** adaptation, and the first closed-bodywork / open-cockpit
car: a UV unwrapped as if from above (x longitudinal, y lateral from a single
centre row, +x rearward on **both** sides); nose centre stripes through the AÏ
roundel node, resuming on the engine cover with a black gap at the airbox mouth
and running to the tail; a sash across each front fender **crown** rather than
its side face; AÏNTOLOGIC large on the sidepod flank; logo slot 2 on the
engine-cover top shoulders; AÏNTOLOGIC on the wing top; logo slot 1 on both
endplate outer faces at per-side sizes. Its real lesson: **a chassis can have no
usable rear-facing surface at all** — this car's wing rear face is a ~2 px edge
and its tail is diffuser and crash structure, so the dead-rear read had to come
from the engine-cover centre stripe. Read all seven releases and
car maps before starting a new car. **No car's UV coordinates, rects, affines,
edge tables, mirror rows or per-side trims apply to another chassis** — the
next car gets its own.

**What ships vs. what you regenerate.** The example build ships the MX-5
geometry and the shared scheme code (`src/teamscheme.py`, `src/sponsors.py`).
The template-derived island-edge tables and body masks that the F4, Ray, HPD,
Spec Racer Ford, Skip Barber and Aston builds rely on are **not** shipped —
they came off specific iRacing templates. Regenerate them from your own
template with the probing tools (the retargeting checklist below) before you
build those cars.

## The adaptation rule — read this before the next car

**Future cars inherit the DESIGN LANGUAGE, not the MX-5's geometry.** Every
number in `src/team_mx5.py` — rects, affines, the sash's X/Y, the stripe
widths per panel, the per-side trims, the logo slot 2 rectangles — belongs to
the MX-5's UV layout and is wrong on any other chassis. A formula car, a GT
car or a prototype needs: new UV discovery, new panel mapping, new stripe
routing (where does the "sash" live on a car with no front fender? where
can a centre stripe run?), new sponsor regions, and chassis-specific tuning
on the render. The MX-5 is the gold-master *visual reference* — its gallery
picture (`docs/gallery/mx5-2016-global-cup.jpg`) is what the next car must
*feel* like. "Measuring a new car" in `AGENTS.md` is the starting point for
that job.

---

## Retargeting checklist — the F4, the RSR, anything after

1. **Car ID first** — confirm it in iRacing's Car Info before anything. Template
   from your own iRacing template.
2. Read `docs/IRACING-PAINTING-PLAYBOOK.md` and `docs/PANEL-PROBING.md`.
3. `cp src/team_mx5.py src/team_<car>.py`. Change `PAINT_DIR`, the rects,
   `NUMBER_BLOCKS`. Delete every placement constant — you will re-measure
   them all.
4. **Probe before placing anything:** `python tools/probe.py team_<car>
   grid --n 8`, then `rect` / `bands` on what you find. Read from a level
   camera. Both sides. Write the map into `docs/car-maps/<car>.md` as you go,
   including what turned out to be wrong.
5. **Find the centre line and the shut lines with tick rulers before
   drawing a stripe.** Colour/tick probes on every centre-line panel (nose,
   hood, lid, tail) read against the car's own symmetric features (badges,
   tail lights) from DEAD front/rear frames; tick rulers either side of the
   hood/fender shut line for the sash join. Expect islands to be
   anisotropic and not mirror-symmetric; expect the join to need tuning on
   the render. Walk around it with `tools/sheet.py` before any mark goes on.
6. Number blocks must PASS. Don't mask — move geometry.
7. `tools/contact.py` six angles → look at every one zoomed with
   `tools/zoom.py`. Then on track.
8. Save the approved paint: the exact TGA bytes with a sha256, plus a preview
   image, so it can be restored pixel for pixel.

### Things the MX-5 taught that will bite the next car

- Rect names like "LEFT flank" in a car map are not trustworthy. Define
  sides by *what the viewer shows* and note which rect renders where.
- Panels keep rendering **past a rect's edge** (the MX-5's quarters run 60
  rows below the valance rect; the rocker lip is 48 rows past the flank).
  If a thin strip of base colour survives at a panel edge, paint past it.
- A tall band changes which rects matter. Rects that "sit above the stripe"
  for a low stripe are *inside* a tall one.
- Text and pictures need different transforms on the mirrored flank
  (playbook Rule 4 / 4a). Everything in this scheme is text-rule except
  nothing — there are no directional pictures in it, on purpose.
