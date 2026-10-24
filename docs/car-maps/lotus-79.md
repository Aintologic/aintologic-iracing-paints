# Panel map — Lotus 79

- iRacing car ID: **25** (Car Info panel shows `#25`, verified 2026-09-17). The
  account may show **"License Required"** if you do not own the car yet. **The
  car viewer loads custom paint anyway** (proved with a full-texture probe), so
  mapping and the concept did not need the licence. On-track verification will.
- Template: your own iRacing Lotus 79 template zip (`25_template_L79.zip`) ->
  **`Lotus 79.psd`**, 2048x2048. Layer names are different again:
  `Main Car Body`, `Car_Mandatory`, **`Number Block Locations`**, **`Sponsor
  Block Locations`**, `Mask`, `Wire`, plus `Car Patterns` and `Custom Spec Map`
  groups. `tools/template_layers.py` now accepts those two block-layer names.
- Paint folder: `%USERPROFILE%\Documents\iRacing\paint\lotus79\` (created by the
  sim when the car was first viewed; it was empty).
- Paint file: `car_<id>.tga`, where `<id>` is your iRacing customer ID (pass it
  with `--id`).
- Build: `src/team_l79.py`.
- Status: **ready-made paint in `paints/lotus-79/`** — the first concept was approved on the render
  2026-09-17 with no changes; spec B3 A/B-validated; on-track verification
  pending (needs the licence). A change is a new version, never an edit of
  v1.0. **The historic Formula 1 adaptation** in the reference set.

**Chassis note:** 1978 ground-effect F1. Long blade nose with a separate
front wing each side; a narrow monocoque with tall tub sides; wide sidepods
whose flat TOPS carry radiator ducts and louvres and whose tall outer FACES
run between the wheels; a headrest fairing behind the cockpit; an engine cover
with the intake trumpets exposed through it; a big rear wing on two tall flat
endplates. The rear view is mostly gearbox and suspension.

Every row below was read off the car in the viewer from probes
(`tools/probe_islands.py` masked flood/grid probes, and the ruler overlay in
now `tools/probe_bands.py`) on 2026-09-17, unless it says
otherwise.

## Template anchor blocks (from the PSD layers)

| block | x | y | w | h | lands on |
|---|---|---|---|---|---|
| N1 | 1300 | 574 | 116 | 102 | **RIGHT** sidepod face, rear end (island 4) |
| N2 | 261 | 1202 | 93 | 116 | nose top, astride the centre line, near the tip (island 1) |
| N3 | 1300 | 1844 | 116 | 101 | **LEFT** sidepod face, rear end (island 5) |

All three verified by painting the blocks magenta: the sim's stamp renders
over each. The nose stamp reads from the car's side, not from the front.

Sponsor blocks (the template author's suggested spots): pod faces
`(747,564,540,99)` R / `(747,1856,540,99)` L; tub sides `(932,1019,516,93)` R /
`(932,1407,516,93)` L; nose `(369,1163,39,194)` + `(437,1163,142,194)`;
nose sides `(303,911,46,219)` / `(303,1390,46,219)`; rear wing top
`(334,12,146,456)`; endplate outer faces `(557,122,197,39)` (L, island 14) and
`(804,122,196,39)` (R, island 11).

## THE RULE OF THIS UV — mirror about texture row 1259

**Right side = left side reflected about row 1259: `right y = 2518 - left y`,
x identical.** Measured with `tools/mirror_row.py <tpl-dir> 2505 2530
2/3 5/4 6/7 8/9 15/16 18/19 21/22 23/24 26/27 28/29 31/30 37/36 39/40 42/43
45/44`: fourteen pairs peak at 2518, one at 2519, 98.1–100 % overlap.

**Islands with y > 1259 are the car's LEFT side** and read **upright** from a
level left view with **texture +x = REARWARD**. The y < 1259 islands are the
RIGHT side and render **ROTATE_180** from a level right view. (This is the
opposite half from the Ray FF1600, where the upper half was the right side —
do not carry that over. It was settled from a top-down frame, nose left, where
the lower-half pod-top labels sat on the bottom = left side.)

**Not in the mirror** (rows < 480, one island each): the rear wing (0), the
four endplate faces (11–14) and the headrest fairing (17). The build copies
rows 1260..2040 onto 478..1258 and never touches them.

## Islands (LEFT side unless noted; right = mirror)

Indices as `python tools/probe_islands.py team_l79 <tpl-dir> list`
prints them.

| idx (L / R) | bbox (left) | what it is |
|---|---|---|
| 1 (centre) | (47,1051,554,418) | **nose**: tip at low x, cockpit at x ~600. Top visible from x ~140; centre line row 1259 (verified with a white line). Carries N2. |
| 46 (centre) | (619,1191,112,136) | scuttle / coaming in front of the cockpit |
| 5 / 4 | (605,1815,837,154) | **sidepod outer FACE** — the biggest side-facing panel. Both rows fully visible from a level side; top edge y 1815. Carries N3 at the rear. |
| 2 / 3 | (602,1627,905,181) | **sidepod TOP**: y 1627 = inboard edge by the tub, y 1807 = outer edge, which meets the face's top edge (1815) — the two islands wrap continuously. Radiator duct opening around x 830..1060; louvres around x 1280..1400. |
| 26 / 27 | (710,2000,750,37) | skirt strip under the pod face |
| 6 / 7 | (706,1383,639,206) | **tub side** above the pod: rows y 1383..1520 visible from a level side, the rest is under the pod top. Mirror pods sit on it near x ~830. |
| 15 / 16 | (1347,1341,593,168) | engine-cover side, behind the tub side; tapers up toward the rear |
| 10 (centre) | (1301,1136,561,247) | **engine cover top**: +x rearward, centre row 1259. The intake trumpets stand through it at x ~1570..1745; the headrest fairing covers its front. |
| 18 / 19 | (1501,1511,340,221) | sidepod top, rear section by the rear wheel |
| 8 / 9 | (76,1353,291,262) | **front wing** (left / right): +x rearward, row 1 inboard |
| 0 (single) | (12,8,497,463) | **rear wing**, one closed profile unwrapped along x, span along y (**y 0 = car's RIGHT tip**, centre 239). Top surface: leading edge x ~260 -> trailing edge ~509 (+x rearward). **Rear face of the flap: trailing edge at x ~5, +x running DOWN the face to ~120** — that is what a dead-rear view sees. Front face ~250..300. |
| 14 | (526,40,243,311) | **LEFT endplate OUTER face**, upright from the left, +x rearward; upper row (y 40..195) clear above the tyre |
| 11 | (786,39,243,311) | **RIGHT endplate OUTER face**, upright from the right, +x FORWARD |
| 13 / 12 | (1040,106,..) / (1296,106,..) | left / right endplate INNER faces |
| 17 (single) | (1825,9,213,336) | headrest fairing behind the cockpit (both sides + top in one island) |

Wheels, suspension, gearbox, radiators, mirrors: `Car_Mandatory`, not paintable.

## Viewer loop — Lotus specifics (2026-09-17)

- The Car Info dialog may carry a "License Required" banner; the 3D pane still
  works. `tools/view2.ps1` / `walk.ps1` / `contact_sheet.py` / `zoom.py` work
  unchanged (window 1728x1037).
- `tools/view2.ps1 -Wheel 4` then `-Wheel -2` gives a size where the whole car
  fits a top-down frame and a level side reads.
- A 12-frame walk can take longer than a short shell-bridge call limit: launch
  it detached and poll for the `.done` file.
- `probe_islands.py` labels are NAME + cell number — a flood probe named "4"
  reads "41". Name floods with letters.

## The design — locked v1.0 (2026-09-17) — every constant is at the top of `src/team_l79.py`

| element | constant(s) | lands on |
|---|---|---|
| nose centre stripes | `NOSE_X` (138..732), `NOSE_CS` (40, 20, 6) | nose + scuttle, row 1259, stopping around the number panel and the roundel ring |
| nose number panel | N2 + `NOSE_NUM_MARGIN` 8, `NOSE_NUM_GAP` 12 | nose tip |
| AÏ roundel node | `NOSE_BADGE_D` 110, `NOSE_BADGE_CX` 508, `RING_GAP` 5, `RING_W` 11, art ROTATE_270 (reads from the front) | nose, in the template's nose sponsor block |
| engine-cover stubs | `COVER_STUBS` (1440..1562, 1752..1850), `COVER_CS` (30, 15, 5) | either side of the intake trumpets — a gap, not painted through (Ferrari lesson) |
| sidepod sash | `POD_SASH` (xc 640, tilt 0.25, 44/22/6), `POD_SASH_Y` (1627..1972) | pod TOP wrapping straight down the pod FACE at the pod's leading edge, top-forward lean |
| AÏNTOLOGIC (sides) | `POD_WM_W` 430, `POD_WM_CXY` (1022, 1900) | pod face, the template's pod-face sponsor block; mirrored, same place both sides |
| logo slot 2 | `TUB_LOGO2_W` 290, `TUB_LOGO2_CXY` (1170, 1452) | tub side above the pod, both sides |
| driver strip | `TUB_DRIVER_W` 118, `TUB_DRIVER_XY` (770, 1392) | tub side at the cockpit rim |
| AÏNTOLOGIC (wing top) | `WING_WM_W` 380, `WING_WM_CXY` (407, 239), ROTATE_90 | rear wing top, reads from behind / above |
| AÏNTOLOGIC (wing rear face) + band set | `WING_REAR_WM_W` 300 at (82, 239), ROTATE_90; `WING_TE_X` 25, `WING_TE_CS` (12, 6, 3) | the flap's rear face — the only branding a dead-rear view gets |
| logo slot 1 | `EP_LOGO1_D` 116 at `EP_LOGO1_L` (648, 118) and `EP_LOGO1_R` (908, 117) | **rear-wing endplate outer faces**, upper panel above the tyre, both sides |
| pod number panels | N1 / N3 + `NUM_MARGIN` 8 | pod faces, rear |

Left black on purpose: front wings, headrest fairing, pod tops beyond the
sash, tub/cover sides beyond logo slot 2, endplate inner faces, skirts.

## How to edit this car later — the breadcrumbs (v1.0, 2026-09-17)

**Ready-made paint:** `paints/lotus-79/` (approved on the render; spec
A/B-validated; on track pending). To get it back exactly, copy it from `paints/lotus-79/`. Do not change the design
without sign-off; anything experimental goes on a branch and a new release
folder, never over v1.0.

**Build entrypoint:** `python src/team_l79.py` — writes `car_<id>.tga` +
`car_spec_<id>.tga` into `%USERPROFILE%\Documents\iRacing\paint\lotus79\`.
Personalize it with `--id <your iRacing customer ID>`, `--driver "<name>"` for
the driver strip, and `--logo1 <image>` / `--logo2 <image>` for the two logo
slots; with no flags the output carries a neutral "YOUR LOGO" placeholder in
both slots and a blank driver strip. Other flags: `--here` for the cwd, `--png`
for a flat PNG, `--no-spec` for the colour map only. It imports
`src/teamscheme.py` (palette + marks) and `src/sponsors.py` (logo slot 2, driver
strip, logo slot 1 art). No island table file is needed on this car: every
placement is a plain constant. Rebuilding reproduces the release bytes
(`22152afe…` / `4f818a61…`, checked at lock time); on another Pillow/font it will
not — the release TGA is the lock. The sim writes `car_spec_<id>.mip` on the next
viewer reload; that .mip is what Trading Paints takes.

**How the build is layered (`build()`):**

1. `side_geometry()` — the pod sash, drawn at 3x in LEFT texture space, then
   `mirror_geometry()` copies rows 1260..2040 flipped onto 478..1258
   (`right y = 2518 - left y`). Nothing else is mirrored as geometry.
2. `side_text()` — AÏNTOLOGIC (pod face), logo slot 2 (tub side), driver strip,
   through `place()`: upright at (x, y) on the left, ROTATE_180 at
   (x, 2518 - y - h) on the right. **Text is never mirrored.**
3. `centre_panels()` — nose stripes, cover stubs, roundel node, nose number panel,
   drawn once on the centre row 1259 (the nose and cover islands are symmetric).
4. `wing_and_endplates()` — wing-top and rear-face wordmarks (ROTATE_90), the
   rear-face band set, the two endplate logo-slot-1 marks. These islands sit
   outside the mirror and each is placed directly.
5. `number_panels()` — white panels on N1 / N3 (N2's is in step 3).
6. `check_number_blocks()` — refuses to write if anything but body or panel white
   is inside a block.

**To move or resize something:** change its constant, rebuild, Ctrl+R, and judge
from a level side AND the mirrored side (and dead rear for the wing). Only the
LEFT coordinate exists for side marks — the right follows automatically.

| to change | edit | notes |
|---|---|---|
| nose stripe width / extent | `NOSE_CS`, `NOSE_X` | the nose top becomes visible at x ~140; x 600..619 is the gap to the scuttle island |
| roundel size / position | `NOSE_BADGE_D`, `NOSE_BADGE_CX`, `RING_GAP`, `RING_W` | the ring must stay inside the nose top (template block 437..579) |
| nose number panel | `NUMBER_BLOCKS["N2"]`, `NOSE_NUM_MARGIN`, `NOSE_NUM_GAP` | never move the block — it is where the sim stamps |
| cover stubs | `COVER_STUBS`, `COVER_CS` | the trumpets occupy x ~1570..1745; the headrest hides x < ~1440 |
| pod sash | `POD_SASH` (xc at the pod-top inboard edge, tilt, widths), `POD_SASH_Y` | one polygon crosses pod top (1627..1807) and pod face (1815..1969) |
| side wordmark | `POD_WM_W`, `POD_WM_CXY` | keep it between the sash (ends ~780) and N3 (starts 1292 with margin) |
| logo slot 2 | `TUB_LOGO2_W`, `TUB_LOGO2_CXY` | tub side island 6; visible rows ~1383..1520, the island ends at x 1345 |
| driver strip | `TUB_DRIVER_W`, `TUB_DRIVER_XY` | at the cockpit rim, ahead of the mirror stalk |
| wing top wordmark | `WING_WM_W`, `WING_WM_CXY` | top surface x ~260..509, span y 8..471, centre 239 |
| wing rear face | `WING_REAR_WM_W`, `WING_REAR_WM_CXY`, `WING_TE_X`, `WING_TE_CS` | rear face x ~5..120, +x DOWN the face |
| logo slot 1 | `EP_LOGO1_D`, `EP_LOGO1_L` (island 14), `EP_LOGO1_R` (island 11) | upper panel y 40..195 clears the tyre from a level side |
| spec map | `SPEC_VARIANTS["B3"]`, `SPEC_ORANGE_GROW` | nearest-colour from the colour map + a 3-texel papaya halo; number blocks (0,60,110) |

**Number treatment:** three blocks, all flat white panels (`T.number_panel`) that
cover the block completely plus an 8-texel margin; iRacing stamps the number on
top. N1 right pod face rear, N3 left pod face rear, N2 nose tip (the stamp there
reads from the car's side). Set all three Car Number chips to `#0C0C0D`.

**Spec treatment:** B3 "Satin-True" — body (0,170,200), white (0,55,30), papaya
(0,35,16) with a 3-texel halo, logo faces (0,120,150), number blocks (0,60,110).
Validated with an A/B comparison at a level-left pose.

**Hidden / occluded — don't put anything that matters here:**
- tub side rows below ~1520 (under the pod top) and the nose underside;
- the front of the engine cover under the headrest fairing (x < ~1440) and the
  trumpet opening (x ~1570..1745);
- the lower half of each endplate outer face (y > ~195) — behind the rear tyre
  from a level side;
- the wing's top-surface trailing edge from a dead rear (use the rear face);
- the pod tops' radiator duct openings (~830..1060) and louvres (~1280..1400);
- the skirts (26 / 27) — a sliver from a level side, nothing from elsewhere;
- endplate inner faces (12 / 13) — only glimpsed through the wing gap.

**To probe again:** `python tools/template_layers.py <your Lotus 79 template
zip> <tpl-dir>`, then
`python tools/probe_islands.py team_l79 <tpl-dir> list` (island indices above),
`... 5:P:8,2 2:T:8,3 ...` (masked grids), `python tools/probe_bands.py team_l79
<tpl-dir> 0:X:0:520:25 line:1,10:1259 blocks` (texel rulers, centre line, stamp
positions), `python tools/mirror_row.py <tpl-dir> 2505 2530 2/3 5/4 6/7` (the
mirror). Sweep with `tools/walk.ps1` (level, `-DragY -600`) and top
(`-DragY 600`), tile with `tools/contact_sheet.py`, read with `tools/zoom.py`.
**Rebuild the livery after any probe** — probes overwrite the paint file.

## Tried / to remember

- A trailing-edge band set drawn at the TOP of the wing's trailing edge
  (x 470..500) was invisible from a dead-rear view. The rear view sees the
  flap's rear face, which is the LOW-x end of island 0 (x ~5..120), found with
  a 25-texel chord ruler read from dead rear. Moved there.
- Spec map: B3 carried over unchanged and validated by an A/B at lock time —
  no ladder was needed.
- Approved with no changes after the first concept: nothing on this car was
  rejected at review. The only rework was the wing band (above), found on the
  render before review.
