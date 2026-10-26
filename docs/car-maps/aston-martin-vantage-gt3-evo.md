# Aston Martin Vantage GT3 EVO (#206) — panel map

## Status — LOCKED v1.1, ON TRACK VERIFIED (2026-10-10)

- **Current:** v1.1. The ready-made paint is in `paints/aston-martin-vantage-gt3-evo/`.
  Accepted — looks good in the viewer and on track.
- **v1.1 vs v1.0:** one change. The rear-deck stripe is one constant stripe,
  x 1550..1862 on row 1249 at the full recipe. v1.0 drew the part behind the
  seam at x 1700 on row 1258 at 38/19/5; on the car that rendered narrower
  and stepped ~9 texels toward the car's left (top + dead-rear shots).
  See trap 1.
- **v1.0** (`v1.0-2026-10-10`, approved on the render the same day) is
  superseded — kept frozen, never uploaded.
- **Paint Shop:** set all three Car Number chips to `#0C0C0D`, otherwise the
  stamped numbers render white on the white panels.
- **Known and accepted (not defects):** a black curved lip (sim geometry)
  crosses the deck stripe behind the rear window; the spec map is B3
  "Satin-True" carried over with no A/B on this car.
- **Centre mask not shipped:** this car's `assets/amv-centre-mask.png` is
  template-derived and is NOT in the repo. Regenerate it from your own iRacing
  template with `tools/body_mask.py` (step 6 below) before the first build.
- A change is v1.2 — start at "How to edit this car later" below and the v1.1
  `RELEASE.md`.

## Identity

| | |
|---|---|
| car id | **#206** — read in the Car Info panel; the dialog is titled **"Car Info: Aston Martin Vantage GT3 EVO"** (`car-info-206.png` in the m1 folder) |
| template | your own iRacing template `206_template_AMGT3.zip` → **`Aston Martin Vantage EVO GT3.psd`**, 2048×2048. Not `150_template_AMV4.zip` (the GT4) or `64_template_AM1.zip` (the DBR9) |
| paint folder | `%USERPROFILE%\Documents\iRacing\paint\amvantageevogt3\` (created by the sim; it was empty) |
| file | `car_<id>.tga` — named from your iRacing customer ID (`--id`) |
| build | `src/team_amv.py` |
| layers | `Paintable Area` (`Base`, `Car Patterns`, `Carbon Fiber`, `Car_decal`, `IMSA Car_decal`, `Pitboard`, `Pitbox Colors`), `Turn Off Before Exporting TGA` (`Car Mandatory`, `Sponsor Blocks`, `Number Blocks`, `Mask`, `Wire`), `Spec` group. Green island outlines in the Wire layer this time |

## The rule of this UV

Mirror-symmetric about texture row **1260**:

    other-side pixel row = 2520 − row,  x identical

Measured by mask correlation on twelve island pairs (0/1, 10/9, 17/16, 19/18,
26/27, 35/34, 37/36, 41/40, 48/47, 71/70, 65/66, 74/73) — every one peaks at
**M = 2520**, overlap 99.4–100 % (19/18, the hood vents, 91.8 %):
`python tools/mirror_row.py out/tpl 2505 2535 0/1 10/9 ...`.

- **rows > 1260 = the car's LEFT side**, upright from a level left view
- **rows < 1260 = the car's RIGHT side**, ROTATE_180 from a level right view
- **+x is REARWARD on both sides** — the body is unwrapped as if from above
  (like the HPD and the SRF). Proved with the 128-texel coordinate grid: the
  left flank reads `6,13 → 10,13` nose to tail upright, the right flank the
  same columns upside down.
- Centre-line panels (hood, windscreen banner, roof, rear deck, tail) are
  centred on row 1260 with **+y = the car's LEFT**. The front bumper is the
  exception: it is unwrapped across x, centred on **column 543.5**, +x = the
  car's LEFT, +y DOWN the face.

So side geometry is drawn once in LEFT texture space and mirrored
(`mirror_geometry`); text is composited afterwards with `place()` (playbook
Rule 4). Art that reads from the FRONT on a centre panel is ROTATE_270; art
that reads from BEHIND on the deck / tail is ROTATE_90; the wing top reads
from behind with ROTATE_270 (its +x runs FORWARD).

## Islands that matter

`python tools/probe_islands.py team_amv out/tpl list` (98 islands).
Named with a whole-inventory flood (a one-off flood script, not in this project) and
read from level sides, dead front, dead rear and top.

| idx | bbox (x,y,w,h) | what it is |
|---|---|---|
| **0 / 1** | `(513,1468,1331,491)` / `(513,562,1331,491)` | LEFT / RIGHT **body side**: one island from just behind the front-fender gill to the tail — door, rear quarter, haunch. Coverage below |
| **3** | `(53,943,617,636)` | **hood** — the whole clamshell incl. the fender tops. x 53 = nose lip, ~606 = windscreen base on the centre row. Holes: the two big fender vents (islands 18/19 sit in them), two small triangular openings either side of the centre at y ≈ 1107..1143 / 1377..1413 around x 400..525 (clear of a ±45-texel stripe). N4 on the centre line |
| **5** | `(13,25,1061,324)` | **front bumper / fascia**, wraps round to the sides ahead of the front wheels. Centre column 543.5; at that column it exists only at y 135..197 (above the grille, under the Aston badge) and y 327..349 (the lip under the grille) — the grille is a hole |
| 12 | `(162,7,763,116)` | chin / splitter top strip under the bumper — not painted |
| 15, 28, 43, 96 | inside 5's bbox | grille surround / inner grille parts — not painted |
| 11 | `(10,843,231,835)` | thin C-shaped strip round the hood's front edge — mostly hidden |
| 29 | `(622,1170,98,182)` | dark oval at the hood's rear edge (cowl) — not painted |
| 13 | `(800,1012,79,497)` | inside the windscreen area; never seen from outside |
| **14** | `(893,1011,79,499)` | **windscreen sun strip (banner)** — renders as a band across the top of the windscreen |
| **4** | `(720,897,669,727)` | **roof**: x 985 (behind the banner) .. 1388 (rear-window top edge) on the centre row; wraps down both roof rails. Islands 13/14/55 sit inside its bbox |
| (leaky) | `~(1390..1860, 1000..1520)` | **rear deck / boot lid**, NOT in the island list (outline leaks). The rear window is an open glass hole (the cage and engine show through); on the centre row x ≈ 1550 is just behind the window, 1860 the ducktail lip. x < 1550 is hidden inside the window frame. Painted through `assets/amv-centre-mask.png` (template-derived, not shipped — regenerate it with `tools/body_mask.py`, step 6 below) |
| **6** | `(1840,792,199,937)` | **tail panel**, from under the light bar down to the diffuser: +x = DOWN the face (visible x ≈ 1865..2038), +y = car's LEFT, centre row 1260. On the centre row there is a round sensor at x 1924..1939 and the rain light at 1963..2006 (holes) |
| **2** | `(1699,12,334,722)` | **rear wing**: the TOP surface is x 1699 (trailing edge) .. ~1860 (leading edge), **+x FORWARD**; x > ~1870 is the underside. Span along y, y 12 = the car's LEFT tip, centre y ≈ 373 |
| 21 / 23, 22 / 24 | `(1588,184,97,164)` / `(1588,11,97,164)`, `(190,372,164,97)` / `(17,372,164,96)` | rear-wing **endplate** faces (they took the flood colours — paintable). Black in concept 1 |
| **16 / 17** | `(1424,487,246,206)` / `(1424,1828,245,207)` | the **front-fender gill** blades behind each front wheel (renders on the fender, not where the texture sits). Black |
| **10 / 9** | `(138,1684,441,354)` / `(138,483,441,354)` | LEFT / RIGHT **front fender side** above and ahead of the gill, round the front wheel arch |
| 18 / 19 | `(220,981,354,150)` / `(220,1390,354,150)` | the hood's two big fender vents |
| 30, 25, 26/27, 34/35, 40/41, 49/50 … | — | sills, arch lips, mirror parts; nothing that carries artwork |

### Body side coverage (island 0, LEFT; X ruler every 50, Y ruler on the right side mirrored)

| texture | on the car (level left view) |
|---|---|
| x 513..600 | behind the front wheel, mostly under the gill |
| x ~600..660 | the gill (sim geometry, islands 16/17) covers it |
| x 650..750 | clean strip behind the gill, full height — the sash lives here |
| x ~750 | door front shut line |
| x 750..1265 | the door; the mirror base sits at its top front (x ~850..900) |
| x ~1270..1300, low | a small black intake at the door's rear lower corner |
| x 1300..1700 | rear quarter / haunch over the rear wheel; the rear arch starts at row ~1731 at x 1500..1600 |
| y ~1660 | the side-window bottom edge (right side y 860) |
| y 1731..1805 | N6, the door number |
| y 1820..1910 | the lower door band (right side y 610..700) |
| y > ~1915 | the sill crease; the black sill below is mostly other islands |

## Number blocks — one layer, the sim stamps four of its six blocks

The PSD has **one** `Number Blocks` layer (no "config" groups like the SRF's)
plus an `IMSA Car_decal` layer but no IMSA number blocks. Probed: every block
painted magenta over a coordinate grid, walked round — the stamp rendered on
four of them.

| block | rect | where | stamped? |
|---|---|---|---|
| N2 | `(1111,716,102,75)` | RIGHT door, upper middle | yes |
| N6 | `(1111,1731,102,75)` | LEFT door, upper middle | yes |
| N4 | `(342,1212,71,98)` | hood, ON the centre line, mid-hood | yes |
| N5 | `(1971,1316,66,86)` | tail, car's LEFT, low | yes |
| N1 | `(576,449,83,61)` | on no island (`island_runs` = background) | no |
| N3 | `(18,803,61,82)` | on no island | no |

The build panels N2/N4/N5/N6 (white, block + 8) and its guard checks all six.
If you ever change the number package in Paint Shop, re-probe.
`tools/checkblocks.py` is MX-5-only — use the build's own guard.

## Where everything is placed (v1.1, locked 2026-10-10 — the first concept of 2026-09-28 with the deck stripe fixed)

All named constants at the top of `src/team_amv.py`. Side placements are LEFT
texture space (rows > 1260); `place()` / `mirror_geometry()` do the right.

- **Centre stripe** white | papaya | white, one recipe `CS = (44, 22, 6)`:
  front bumper at column 543.5, rows 135..197 (up to the Aston badge) and the
  lip 327..349 under the grille; hood x 53..606 on row 1260 with the **N4
  number panel composited on top** (the RSR rule — one constant stripe, the
  plate is an occluder); roof x 985..1389 through the **AÏ roundel node**
  (d 200 at x 1185, gap 6, white ring 12, reads from the front); rear deck
  x 1550..1862 on row **1249** at the full recipe (v1.1; v1.0 split it at
  x 1700 — see "Traps"). All masked through `assets/amv-centre-mask.png`.
- **Why the node is on the roof:** the hood number sits on the centre line
  (the RSR / Ferrari lesson).
- **Windscreen banner** AÏNTOLOGIC 270 px on island 14, reads from the front.
- **Sash** (46 / 23 / 6, tilt 0.28, top-forward) just behind the front-fender
  gill: `xc 700` at row 1668, rows 1668..1930 — it crosses the door shut line.
- **AÏNTOLOGIC** 400 px on the lower door band, centred (1055, 1866).
- **Driver strip** the `--driver` name (blank by default) 130 px at
  (950, 1676), under the window, behind the mirror base.
- **Logo slot 2** (`--logo2`) 250 px on the rear haunch, centred (1540, 1652).
- **Tail:** AÏNTOLOGIC 250 px above the centre sensor at (1894, 1260); number
  N5 left; **logo slot 1** (`--logo1`) 72 px at (2000, 1161) — the mirror spot
  of the N5 panel (the SRF's rule), read from dead rear.
- **Rear wing top:** AÏNTOLOGIC 440 px at (1778, 373), ROTATE_270, reads from
  behind / above.
- **Black by choice:** endplates, gill blades, front fender sides (islands
  9/10), sills, splitter, the hood vents.
- **Spec:** B3 "Satin-True" carried over; no A/B yet.

## Traps on this car

1. **The rear deck is a leaky island and its centre is not row 1260.** The
   outline merges with the background, so it is painted through a mask
   (`tools/body_mask.py ... leak:1390,940,470,640`). A Y-band ruler read
   from dead rear, against the Aston badge and the deck's own edges, put the
   car's centre at row ~1248; a stripe on row 1260 visibly jogged at the lip.
   **v1.0 over-read that ruler:** it put the lip behind x 1700 on row 1258 at
   ~14 % narrower widths, believing the lip renders wider per texel. It does
   not — top and dead-rear shots showed the lip stripe narrower and stepped
   ~9 texels to the car's left. v1.1: one stripe on row 1249, full width,
   x 1550..1862, continuous from every angle checked.
2. **The rear window is an open hole** (cage and engine visible). The roof
   stripe ends at its top edge (x 1388); the deck stripe starts behind it
   (x 1550 — x 1480..1550 lands on the inside of the window frame and read as
   a floating patch).
3. **The front-fender gill** (islands 16/17) stands proud of the fender behind
   the front wheel and hides island 0's x ~600..660. The sash sits behind it.
4. **The wing's top surface is the LOW-x half of island 2** (x 1699..~1860,
   +x forward). A wordmark at x 1960 rendered nothing — that is the underside.
5. **Two number blocks are dead** (N1, N3 — no mesh).
6. **Driving the viewer:** `python tools/view2.py` clicks into the pane; `+`
   wheel ticks zoom IN (`python tools/view2.py --no-reload --wheel N`). A
   16-frame walk took ~110 s with the old PowerShell walk;
   `python tools/walk.py --reload` did 12 frames in 65.5 s (2026-10-24) —
   still over a 60-s tool-bridge call, so run it in the background and wait
   for its `DONE <n> frames` line.

## How to edit this car later

Any change is a new version: **v1.2** next. Keep the
approved v1.1 paint untouched and build the change as a separate version.

1. **Build:** `python src/team_amv.py` writes colour + spec to the paint
   folder (`--here` for the cwd, `--no-spec`, `--png`) and refuses to write if
   artwork lands in a number block. Personalize with `--id` (your iRacing
   customer ID), `--driver` (the name on the strip) and `--logo1` / `--logo2`
   (your two logo images); with no flags it writes a neutral `YOUR LOGO`
   placeholder in both slots and a blank driver strip.
2. **Restore the approved car first** if the paint folder holds anything
   else: copy the ready-made paint from `paints/aston-martin-vantage-gt3-evo/`.
3. **Every placement is a named constant at the top of `src/team_amv.py`:**
   - UV rule: `MIRROR` 2520, `CL` 1260 (centre row), `FCX` 543.5 (bumper
     centre column), `CENTRE_MASK` (`assets/amv-centre-mask.png`).
   - Number blocks: `NUMBER_BLOCKS`, `PANELLED` (N2 N4 N5 N6), `NUM_MARGIN`.
   - Centre stripe: `CS` (orange, white, gap), `BUMPER_Y`, `HOOD_X`,
     `ROOF_X`, `DECK_X`, `DECK_CY` (one stripe on row 1249, full
     recipe — trap 1).
   - Roof roundel: `ROOF_BADGE_D`, `ROOF_BADGE_CX`, `RING_GAP`, `RING_W`.
   - Wordmarks: `BANNER_WM_W` / `BANNER_WM_CXY`, `TAIL_WM_W` / `TAIL_WM_CXY`,
     `WING_WM_W` / `WING_WM_CXY`, `DOOR_WM_W` / `DOOR_WM_CXY`.
   - Logo slot 1 (tail): `TAIL_LOGO1_D`, `TAIL_LOGO1_CXY` (the mirror spot of
     the N5 panel).
   - Sides (LEFT texture space, mirrored): `SASH`, `SASH_Y`,
     `DOOR_DRIVER_W` / `DOOR_DRIVER_XY`, `Q_LOGO2_W` / `Q_LOGO2_CXY`
     (logo slot 2).
   - Spec: `SPEC_DEFAULT` ("B3") and the table above `spec_from_colour()`.
4. **Verify on the 3D car**, not the flat texture: Ctrl+R twice in the viewer
   (`python tools/view2.py`), then walk it (`python tools/walk.py`,
   `tools/contact_sheet.py`) and compare against the v1.1 `preview.png`.
5. **Re-probe** only if a placement lands somewhere unexpected:
   `python tools/template_layers.py 206_template_AMGT3.zip out/tpl`,
   `python tools/probe_islands.py team_amv out/tpl list`,
   `python tools/coord_grid.py team_amv 128`, then masked probes
   (`tools/probe_bands.py`, `tools/probe_islands.py`).
6. **Mask:** `python tools/body_mask.py out/tpl assets/amv-centre-mask.png 3 5 14 4 6 leak:1390,940,470,640`
   regenerates `assets/amv-centre-mask.png` (template-derived, not shipped).
7. **Your own design (`--design`, `src/design.py`, issue #5):**
   `apply_design()` sets `DESIGN` and `BODY` / `LINE` / `ACCENT` = the
   design's body / trim / graphic before `build()`. Stripes: `_band_offsets()`
   goes through `DESIGN.bands`, so the sash, bumper, hood, roof and rear-deck
   bands all follow the stripe style; a kept band stays exactly where it was
   measured (the deck stripe stays on row 1249). The roof ring is a trim line,
   drawn only when `DESIGN.lines_on`. Lettering: `_wm()` = `DESIGN.wordmark` +
   `DESIGN.lettering_box`; the door lettering carries the "made with
   AINTOLOGIC" credit (`credit=True`), the windscreen banner, tail and wing
   top pass `credit=False`. Badge: `DESIGN.roundel` on the roof node. Logos:
   `sponsors.logo_slot` — logo slot 1 (tail) with `DESIGN.logo_colours`, logo
   slot 2 (rear haunch) in lettering / graphic. Driver strip: face body, ink
   lettering, outline graphic. Spec map: `DESIGN.spec_values` /
   `material_keys` / `stripe_mask`, and `_panel_cover()` puts the panels'
   white texels back to the car's own white finish, so a design's trim
   finish (chrome, matte) never rims the numbers (a no-op in the example
   scheme). Left fixed: the white number panels (under the sim's number
   stamp; the number-block check accepts body or that white). No design, or
   `--design example-scheme`, builds the v1.1 paint byte for byte.

## Milestone-1 pictures

`paints/aston-martin-vantage-gt3-evo/wip-2026-09-28-m1/`:
`preview-11-angles.jpg` (level left / right, top, front, rear, all four level
3/4s, high rear, high left), `closeups.jpg` (both sides, tail, front, roof,
deck + wing), `flat-1k.jpg` (the concept texture), `car-info-206.jpg`,
`template-overview-1k.jpg`, and the probes that settled the map:
`probe-coord-grid-128.jpg` (grid + magenta number blocks, 12-frame walk),
`probe-island-flood.jpg` (every island flooded + labelled),
`probe-deck-x-ruler-top.jpg` and `probe-deck-y-ruler-dead-rear.jpg` (the
leaky rear deck).
