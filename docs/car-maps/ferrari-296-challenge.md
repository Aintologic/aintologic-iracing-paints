# Panel map — Ferrari 296 Challenge

- iRacing car ID: **203** (Car Info panel shows `#203`, verified 2026-09-16).
- Template: your own iRacing template `203_template_F296C.zip` ->
  **`Ferrari 296 Challenge.psd`**, 2048x2048. **Not** `173_template_F296.zip`,
  which is `Ferrari 296 GT3.psd` — a different car with a different UV.
- Layer names differ again: `body base`, `Car Patterns` group, `Color Change`,
  `car decal`, `Pitbox Colors`, a `Turn Off Before Exporting TGA` group holding
  `Car Mandatory`, `Number Blocks` (invisible), `Mask`, `Wire` (invisible), and a
  `Custom Spec Map` group. **There is no `Sponsor Blocks` layer.**
- Paint folder: `%USERPROFILE%\Documents\iRacing\paint\ferrari296challenge\`.
- Paint file: `car_<id>.tga` (where `<id>` is your iRacing customer ID).
- Build: `src/team_f296c.py`.
- Status: **LOCKED as `releases/ferrari-296-challenge/v1.0-2026-09-16/`** —
  concept pass 1 approved on the render 2026-09-16 with no changes;
  on-track verification pending. A change is a new version, never an edit of v1.0.

Every row below was read off the car in the viewer from labelled probes
(2026-09-16: an 8x8 whole-texture grid, then `tools/probe_islands.py` masked
floods of 21 islands + a 6x6 rect grid over the hood) unless it says otherwise.

## Template anchor blocks (Number Blocks layer)

| block | x | y | w | h | lands on |
|---|---|---|---|---|---|
| N1 | 468 | 216 | 60 | 37 | rear bumper, just LEFT of the centre fog light (the car centre is x ≈ 555) |
| N2 | 985 | 633 | 95 | 57 | RIGHT door, lower front |
| N3 | 879 | 1010 | 38 | 62 | windscreen banner, car's RIGHT end — **the sim stamps a plate here too** (grey box on the first render) |
| N4 | 615 | 1420 | 51 | 92 | hood, car's LEFT rear corner (not on the centre line) |
| N5 | 985 | 1785 | 95 | 57 | LEFT door, lower front |

The `car decal` layer is the default livery's sponsor art (Adler banner,
Shell, Pirelli, 2elle…); **none of it is drawn over a custom paint** — the
all-black test paint rendered with no body decals. The sim adds only the tow
hooks (red, sim geometry) and the Pirelli tyre text.

## THE RULE OF THIS UV — mirror about texture row 1236

**Other side = this side reflected about row 1236: `y' = 2472 − y`, x
identical, nose at low x on both sides.** Measured with `tools/mirror_row.py
<tpl-dir> 2460 2485 1/0 16/15 18/19 27/28 39/38 53/52 55/54 59/60 65/64
43/42 47/46 24/25`: ten pairs peak at 2472 and two at 2473, overlap 92.7–99.9 %.
The centre-line panels (hood, banner, roof, the strip behind the roof) are
centred on row 1236 — confirmed on the render by the hood's prancing-horse
badge sitting on the H13/H19 cell boundary (y 1240) from dead front, and by
the stripe landing on the badge.

**Rows > 1236 are the car's LEFT.** Proved from a top-down frame (nose left,
the `R` island grid on the image-bottom side) and from dead front (hood cells
with y > 1236 render on the viewer's right = car's left; N4 stamps there).
From a level LEFT view the left side island reads **upright** (+x rearward,
+y down); the right side reads **ROTATE_180**. So the build draws the left,
mirrors the geometry, and composites text afterwards (playbook Rule 4).

## Islands (indices from `python tools/probe_islands.py team_f296c <tpl-dir> list`)

| idx | probe name | bbox | what it is |
|---|---|---|---|
| 0 | R | (484,1578,1484,333) | the LEFT body side, one island front arch → tail: see coverage below |
| 1 | L | (484,563,1484,332) | the RIGHT body side (mirror of 0) |
| — | H (rect grid) | hood ≈ (245..843, 880..1600) | **the hood is not in the island list** — its green outline leaks into the background (like the Ray's left sidepod). +x rearward (x 245 = nose lip above the grille), +y = car's LEFT, centre row 1236. The vent: three slats on the centre line at x ≈ 405..575 (slat islands 66 / 50 / 48 at x 424 / 477 / 535). x 575..843 is flat hood up to the cowl. N4 at its left rear corner. |
| 11 | — | (270,957,149,559) | nose top strip across the car in front of the hood proper (x 270..340 on the centre line) |
| 31 | — | (770,1073,73,327) | cowl strip at the hood's rear edge (x 810..840 on the centre line) |
| 10 | Z | (853,991,89,491) | windscreen banner (sun strip). N3 at its right end. Art ROTATE_270 reads from the front. |
| 2 | M | (800,868,548,737) | roof + rear glass frame: +x rearward, +y = car's LEFT, centre 1236, x 953..1347 on the centre line. **Island 10 sits inside its bbox** — start roof art behind x 942. |
| 3 | E | (1358,801,628,871) | the frame round the open engine window: its front column (x 1362..1485 on the centre line) is the strip between the rear glass and the engine window; the rest rings the window |
| 7 | C | (1489,1001,412,472) | engine-window inner surround / louvre faces — mostly hidden |
| 13 | V | (1165,13,171,174) | the black scoop / frame over the engine window (reads on the top view); left black |
| 4 | T / WG | (1356,9,685,241) | **rear wing**: rows 10..129 the TOP surface (+x = car's LEFT), rows 129..248 the trailing face seen from a level dead rear (rendered ~3.4x squashed vertically) |
| 9 | X | (301,12,510,152) | rear deck lip behind the engine window, above the tail lights; +x = car's RIGHT, centre x ≈ 555; rows 69..163 on the centre column |
| 8 | B | (67,110,977,185) | rear bumper band under the engine / exhausts; centre x ≈ 555 (the fog light); only rows 173..210 of it at the centre column, taller toward the corners. N1 left of centre. |
| 68 | — | (536,214,40,64) | the fog-light housing |
| 6 | N | (13,676,212,1121) | front bumper corners / lower nose sides (N7 / N8 cells under the headlight) — not painted |
| 5, 12, 14, 16, 18, 20, 21, 22, 24, 27 | D, K, J, Q, P, A, F, U, S, W | — | flooded 2026-09-16; nothing that reads from the level / top sweeps carries artwork in v1. The wing endplates render carbon black — not paintable. |

### Side island coverage (island 0, LEFT; probe `0:R:12,4`, cells 124 x 83)

| texture | on the car (level left view) |
|---|---|
| x 484..731 | front fender above / behind the front arch |
| x 731..979 | front fender behind the arch, ahead of the door — **the sash lives here** |
| x 979..1350 | door (N5 at its lower front) |
| x 1350..1474 | the side intake in the door's rear; its lower half (rows ≥ 1744) is flat |
| x 1474..1721 | rear quarter above / ahead of the rear wheel |
| x 1721..1968 | rear fender behind the rear wheel, into the tail |
| y 1578..1661 | shoulder / window sill band (the island's top edge is ~1643 under the window at x 1040..1100) |
| y 1661..1744 | belt band, continuous front arch → rear arch |
| y 1744..1828 | the lower door band, continuous front arch → rear arch (the AÏNTOLOGIC row) |
| y 1828..1911 | rocker |
| rear arch | at x 1700 the island ends at row 1691; at x 1560 it still runs to 1896 |

## Viewer loop — 296 Challenge specifics (2026-09-16)

- Car Info / Car Model tabs are HTML: a bare `mouse_event` click is ignored —
  move the cursor across the target first (a small local click helper).
- `tools/view2.ps1`, `walk.ps1`, `walk_top.ps1`, `contact_sheet.py` work
  unchanged; window 1728x1037. Ctrl+R does not reset the camera.
- A local scratch `sweep` script (`<prefix>`) = reload + 12 level + 8 top frames
  (~2.5 min — start in the background and poll). A companion `preview` script
  is the zoomed 16-level / 8-elevated / 8-top preview sweep.
- `python tools/island_runs.py <tpl> y:<x>:<y0>:<y1> x:<y>:<x0>:<x1>`
  (committed) prints which island owns each run of a texture column / row —
  used here for the tail band height, the rear-arch cutout and the
  window-sill edge. (The scratch scripts above are local, not in git.)

## The design — locked v1.0 (concept pass 1, approved unchanged), every constant in `src/team_f296c.py`

Side elements are in LEFT texture coordinates (rows > 1236); the right side
is the mirror (`mirror_geometry`, row → 2472 − row) and text is composited
ROTATE_180 there (`place`). Centre-line panels are drawn once.

| element | constant(s) | lands on |
|---|---|---|
| one stripe recipe | `CS` (40, 20, 5) orange / white / gap | hood, roof, E strip, rear lip |
| hood stripe | `HOOD_X` (245..843), `HOOD_VENT_SKIP` (405..575) | nose lip → vent, then vent rear → cowl. **The vent is a deliberate black gap** (see tried-and-rejected) |
| banner wordmark | `BANNER_WM_W` 300 at (897, 1236), ROTATE_270 | windscreen sun strip, reads from the front; N3 plate at its right end |
| roof stripe + roundel node | `ROOF_X` (950..1348), `ROOF_BADGE_D` 180 at x 1100, `RING_GAP` 6, `RING_W` 12, art ROTATE_270 | roof (island 2), starting behind the banner island |
| E strip stub | `ESTRIP_X` (1358..1484) | between the rear glass and the open engine window |
| rear lip stub | `LIP_CX` 555, `LIP_Y` (69..164) | deck lip above the tail lights (island 9), centred on the fog light |
| tail wordmark | `TAIL_WM_W` 170 at (555, 188) | rear bumper band above the number plate / fog light |
| wing wordmark | `WING_WM_W` 440 at (1698, 70), ROTATE_180 | rear wing TOP, reads from behind / chase cam and from above |
| fender sash | `SASH` (xc 850 at the top row, tilt 0.28, 46/23/5), `SASH_Y` (1650..1905) | front fender behind the arch, ahead of the door number panel, top-forward lean |
| number panels | `PANELLED` N1..N5 + `NUM_MARGIN` 8 | doors, hood, banner, rear bumper |
| AÏNTOLOGIC side | `DOOR_WM_W` 440 at (1325, 1792) | lower door band behind the number, under the side intake |
| logo slot 2 | `Q_LOGO2_W` 210 at (1560, 1655) | rear quarter above the rear arch, both sides |
| driver strip | `DOOR_DRIVER_W` 130 at (1030, 1652) | top of the door under the window |
| **logo slot 1** | `HOOD_LOGO1_D` 92 at (640, 1006), ROTATE_270 | hood, car's RIGHT rear corner — the mirror spot of the hood number panel; reads from the front and from above |
| spec | `SPEC_VARIANTS["B3"]`, `SPEC_ORANGE_GROW` 3 | everything — Satin-True, derived from the colour map by nearest colour; number blocks forced to `num` |

Inherited unchanged from the system: palette, marks, band recipe, the roof
roundel as the node (RSR), text-vs-geometry mirroring, the sash ahead of the
door number (RSR / MX-5), wordmark on the biggest side-facing band, logo slot 2
on the rear quarter, banner wordmark (RSR), B3 Satin-True spec.

Adapted for this Ferrari: the vent gap on the hood; the stripe stopping at
the open engine window and resuming on the rear lip; logo slot 1 on the hood
corner opposite the number (no clean flat rear or quarter panel — the rear is
an open engine bay and the quarters carry the intake + logo slot 2); the
wordmark on the lower door band rather than centred on the door (the door
is short and the intake takes its rear); AÏNTOLOGIC on the wing top,
because from behind the car is mostly exposed mechanicals.

## Tried and rejected (pass 1)

- **Stripe painted straight through the hood vent:** the three slat tops
  took the paint and read as a ladder of short rungs from the front — the
  RSR louvre problem again. The vent is now a clean black gap
  (`HOOD_VENT_SKIP`). A different hood treatment is a second-pass option, not
  a fix to force.
- logo slot 2 at (1600, 1702) w 230: clipped by the rear arch (the island ends
  at row 1691 at x 1700) — the logo's leading edge survived, its trailing
  lettering hidden on the right.
- AÏNTOLOGIC centred at x 1345: the final C sat on the rear arch lip.
- Driver strip at row 1615: off-island (the side island starts at ~1643 there).
- Tail wordmark 190 wide at row 192: touched the number plate; the bumper
  band is only 38 rows tall at the centre column.
- Wing wordmark orientation was flipped to upright after misreading a
  low-resolution contact-sheet tile; full-resolution crops of both renders
  proved ROTATE_180 right. Read text orientation from full-res crops only.

## Known gaps at lock (v1.0) — not raised defects, just unmeasured

- Number stamp colours: all chips must be set to `#0C0C0D` in the iRacing
  Paint Shop (Paint Your Car); the renders show the default light numbers on
  the white panels. Where exactly each stamp lands inside its panel is not yet
  probed with magenta blocks.
- Rendered stripe widths are not tick-measured yet (`tools/probe_ticks.py`):
  the nose stripe reads wider than the roof stripe from dead front.
- The rear wing trailing face (rows 129..248) and the engine-window surround
  (islands 3 / 7) are unpainted; the rear reads mostly black by design.
- The nose top strip (island 11) and cowl strip (island 31) take the stripe
  from the rect draw; their exact seam with the hood was judged by eye only.
- Spec map not A/B tested on this car (B3 shipped unchanged; the lock-time
  attempt was abandoned because the iRacing UI was in use). Not verified
  on track.

## Milestone-1 pictures (committed evidence; the release folder has the finals)

`paints/ferrari-296-challenge/wip-2026-09-16-m1/`: `preview-9-angles.jpg`
(level left / right, top, front, both front 3/4, rear, both rear 3/4, plus
each as its own jpg), `preview-closeups.jpg`, `car-info-203.jpg`,
`template-overview-1k.jpg`, `flat.png` (the concept texture), the pass-2
probe (`probe-pass2-*.jpg`) and the rejected hood ladder
(`rejected-pass1-hood-ladder.jpg`).

## How to edit this car later — the breadcrumbs (v1.0, 2026-09-16)

**Locked:** `releases/ferrari-296-challenge/v1.0-2026-09-16/` (approved on the
render; on track pending). Restore with
`python src/restore.py v1.0-2026-09-16 --car ferrari-296-challenge`. Do not
change the design on a whim; anything experimental goes on a branch and a
new release folder (v1.1, v2.0 …), never over v1.0.

**Build entrypoint:** `python src/team_f296c.py` → `car_<id>.tga` +
`car_spec_<id>.tga` in `%USERPROFILE%\Documents\iRacing\paint\ferrari296challenge\`.
Personalize with `--id <your iRacing customer ID>`, `--driver "<name>"` and
`--logo1` / `--logo2` for the two logo slots; with no flags the output carries
a neutral `YOUR LOGO` placeholder in both slots and a blank driver strip.
Other flags: `--here` for the cwd, `--png` for a flat PNG, `--no-spec`. It
imports `src/teamscheme.py` (palette + marks) and `src/sponsors.py` (the two
logo slots and the driver strip). No generated island table is needed on this
car — every placement is a constant. Rebuilding with the same Pillow / font
versions reproduced the release bytes at lock time (`10a378ed…` / `64a79345…`);
another Pillow / font version will not — the release TGA is the lock. Lock a
new version with
`python tools/lock_release.py ferrari-296-challenge <version>-<date> ferrari296challenge`
after the car has been loaded once in the viewer (so the sim writes the .mip).

**The one rule of the UV:** rows > 1236 are the car's LEFT (upright from a
level left view, +x rearward, +y down); rows < 1236 the RIGHT; mirror
`y' = 2472 − y`, x identical. Side geometry is drawn on the LEFT and mirrored
(`mirror_geometry`); text goes through `place()` (ROTATE_180 on the right).
Centre-line panels (hood, banner, roof, E strip) are centred on row 1236 with
+x rearward and +y = car's LEFT — art that reads from the front is ROTATE_270
(banner, roof roundel, hood logo). Tail panels (rear lip, bumper) are centred on
column 555 with +x = car's RIGHT. The wing top reads from behind with ROTATE_180.
**No deliberate left/right asymmetry on this car** — every side mark is mirrored.

**Number treatment:** a white `T.number_panel` of block + 8 texels on all five
blocks (`PANELLED`); the build refuses to write if anything else lands inside
a block (`check_number_blocks`). In the spec map the blocks are forced to
`num` (0, 60, 110). Set all three Car Number chips to `#0C0C0D`.

**Spec map:** `spec_from_colour()` — nearest of body / papaya / white gets
B3's body (0,170,200) / orange (0,35,16) / white (0,55,30); everything else
(the logo-slot art) gets decal (0,120,150); a 3-texel orange halo
(`SPEC_ORANGE_GROW`) keeps the A-bar, the Ï dots and the logo lettering glossy.

**Hidden / occluded areas to remember:**
- the hood vent x 405..575 across the centre (slats; the stripe skips it);
- the open engine window behind the roof — nothing paintable between
  `ESTRIP_X` and the rear lip on the centre line; island 13 over it is a black scoop;
- the side island's top edge sits at row ~1643 under the window (x 1040..1100);
  anything above it lands on nothing;
- the rear arch cuts the side island: at x 1700 it ends at row 1691, at x 1560
  it still runs to 1896 — keep side marks forward of ~1665 below row 1690;
- the rear bumper band is only rows 173..210 at the centre column (taller at
  the corners); rows 214..277 there are the fog light / plate recess;
- the wing trailing face (rows 129..248) renders ~3.4x squashed from a level
  rear view; the endplates are carbon, not paintable;
- the banner island (853..942) sits inside the roof island's bbox — start roof
  art at x ≥ 950;
- the hood itself is NOT in the island list (outline leaks) — probe it with a
  rect grid, not `probe_islands.py`.

**To probe again:** `python tools/template_layers.py
<path to your 203_template_F296C.zip> <tpl-dir>`, then
`python tools/probe_islands.py team_f296c <tpl-dir> list`, masked grids
(`... 0:R:12,4 2:M:4,4 ...`), `tools/probe_multi.py team_f296c NAME:x,y,w,h:c,r`
for the hood, `tools/island_runs.py` for edges, `tools/mirror_row.py <tpl-dir>
2460 2485 1/0 16/15 ...` for the mirror; then `tools/walk.ps1 -DragY -600` /
`tools/walk_top.ps1` + `tools/contact_sheet.py`, reading from level sides,
dead front, dead rear and top, and **judging text orientation from full-res
crops only**. Check nobody else is using the iRacing UI before driving it —
the viewer scripts click into the window.
