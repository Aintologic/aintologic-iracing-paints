# Panel map — FIA F4

- iRacing car ID: **148** (Car Info panel shows `#148`, verified 2026-09-14)
- Template: `148_template_iR04.zip` (your own iRacing template) ->
  `Formula IR04.psd`, 2048x2048. **The FIA F4 is the former Formula iR-04**
  (iRacing re-badged the car when it took the FIA licence; Trading Paints lists
  the template as `148_template_F4.zip`). Same UV, same paint folder.
- Paint folder: `%USERPROFILE%\Documents\iRacing\paint\formulair04\`
- Paint file: `car_<id>.tga`, where `<id>` is your iRacing customer ID (passed
  with `--id`). Nothing else lives in that folder.
- Build: `src/team_f4.py`.
  **ready-made paint in `paints/fia-f4/` (approved on the render
  and ON TRACK, 2026-09-14; v1.0 is the same paint before the on-track
  sign-off).** The engine-cover spine island is deliberately unmapped and
  black — the twin ridge stripes were chosen over a spine stripe.
  Island edges per column: `src/f4_islands.py`, generated from the template
  wire by `tools/f4_islands_gen.py`. **Neither the template nor the generated
  table ships — regenerate `src/f4_islands.py` from your own iRacing template
  before you build.**

Every row below was read off the car in iRacing's car viewer from labelled
probes (`tools/probe_multi.py`, 2026-09-14: an 8x8 elimination grid, 6x2 / 8x2
island grids, 10x4 / 12x5 fine grids, then edge bands on the engine cover).
Nothing is inferred from the wireframe alone except the per-column island
edge table, which was then checked on the render. Unprobed rows say so.

## Template anchor blocks (from the PSD layers)

| block | x | y | w | h | lands on |
|---|---|---|---|---|---|
| N1 | 1124 | 74 | 101 | 102 | RIGHT rear-wing endplate, outer face (island E, its left shape) |
| N2 | 1845 | 74 | 101 | 102 | LEFT rear-wing endplate, outer face (island J, its right shape) |
| N3 | 322 | 1072 | 101 | 115 | nose top, centred on the car's centre line |

Sponsor blocks (magenta in the PSD, the template author's suggested logo
spots): sidepod flanks `(304,287,502,80)` R and `(304,1891,502,80)` L; front
wing `(1407,538,246,106)` + `(1764,538,247,106)`; nose top `(570,1053,141,153)`;
rear wing `(1020,1650,390,62)`; engine cover lower flanks `(1403,875,194,35)` R
and `(1403,1348,194,35)` L; nose tip `(202,1083,76,93)`.

**The sim's own decal layer** (`Car_decal`) already puts the FIA F4 logo on the
engine cover's upper slope just behind the roll hoop (both sides) and the
cutoff triangle + extinguisher "E" at the front of the engine cover (texture
`(1385..1420, 1015..1035)` right / `(1385..1420, 1230..1245)` left). Don't
draw those again.

## THE RULE THAT MAKES THIS CAR EASY — read it before placing anything

**The right side of the car is the left side mirrored about texture row
1128.5: right y = 2257 − left y, x identical.** Measured on three island
pairs from the template's green island outlines (flank front tip 1562/695,
sidepod, engine cover ridge 1137/1119 and crease 1332/924 — every pair sums
to 2257 ±1) and confirmed on the render. Texture x runs nose -> tail on both
sides. So from a level side view the left islands read upright and the right
islands read ROTATE_180; from directly above both halves read upright.

Consequence, exactly the MX-5 flank rule (playbook Rule 4 / 4a), done once
for the whole side in `team_f4.py`:

    geometry:  draw the LEFT side in texture space, then copy every
               left-side rect to the right flipped (mirror_geometry)
    text:      composite AFTER that; on the right ROTATE_180 at
               y' = 2257 - y - h  (place)

Placing the same texture un-flipped on the right puts the top of the design
at the bottom of the car. **The nose top is its own island symmetric about the
same row: its centre line is texture y 1128** (the N3 block is centred on it,
1129.5; the island's own edges say 1128).

## Islands (LEFT side; right = mirror). Edges per column in `src/f4_islands.py`

| island | where (left) | render (level side view) | what it is |
|---|---|---|---|
| POD | x 96..908, top edge 1823 (front) rising to 1906 (rear), bottom 1977 | upright | sidepod outer flank. x ~150 = the inlet lip (col 1 curls in), x ~900 = the pod's rear at the rear tyre. The rear ~120 texels are behind the rear tyre from a level side view — keep the wordmark forward of x ~780. |
| PODTOP | x 160..900, y 1635..1819 | upright from above | sidepod top. Low y = inner edge (against the engine cover), high y = outer edge (meets the pod crease). Its rear rows drop down the pod's rear face. |
| FLANK | x 67..1007, y 1240..1610 | upright | nose + monocoque side. Only **y 1388..1610** is the visible flank; y 1240..1388 is hidden except the last ~250 texels (x > 700), the cockpit surround. The nose tip at x 67 has only y 1462..1610. |
| NOSE | (60,1030,860,210), centre row **1128** | upright from above, tip at low x, +y = car's LEFT | nose top. At the tip (x ~100) only y ~1082..1186 exists; by the number (x 320..420) the flat top is the full 1041..1215; x ~920 is the cockpit opening. |
| EC_B (engine cover UPPER SLOPE) | x 1345..1953; **top edge = the ridge** 1135 (front) -> 1177 (x 1860) -> 1233 (tail tip), **bottom edge = the crease** 1332 (x 1420) -> 1278 (x 1860). 195 rows tall at the front, 100 at the rear. | upright from the side and from above | the sloped upper flank between the spine and the crease, with the FIA F4 decal at its front (x 1350..1457). The mirror is 195/100 tall too — the islands are the same size, the FIRST-PASS RECTS WERE NOT (see below). |
| EC_A (engine cover LOWER FLANK) | x 1408..1952; y 1336..1383 at x 1408 (50 rows!), 1373..1450 from x 1720 (78 rows) | upright | the near-vertical lower flank above the sidepod. There is a GAP of unmapped texture between EC_B's bottom edge and EC_A's top edge (e.g. rows 1305..1347 at x 1600) — anything drawn there does not exist on the car. |
| spine | not found | — | the ridge strip between the two EC_B islands renders black with everything in this map painted. Candidates by shape: `(639,117,326,23)`, the strip `(1437,1473,74,562)` (its cells landed on the halo). Probe before relying on it. |
| EP_L | (1538,25,488,267) | upright | rear-wing endplate. **x 1782..2026 (right half, with N2) = OUTER face**; x 1538..1782 = inner face. On the outer face +x runs toward the FRONT. y 25 = top, 292 = bottom. |
| EP_R | (1045,25,488,267) | upright | rear-wing endplate. **x 1045..1289 (left half, with N1) = OUTER face**, 1289..1533 = inner. +x runs toward the REAR. |
| FW | (1397,524,623,265) | upright from the front | front wing main plane, upper surface. Not painted in v1. |
| FW endplates | (1216,427,397,88) / (1624,427,398,88) | — | front wing endplates. Not painted in v1. |
| RW | (1011,1625,407,233) / (1009,1867,407,165) | — | rear wing plane / flap surfaces. Not painted in v1. |
| (1437,1473,74,562) | — | — | probe colours turned up on the HALO / roll hoop. Leave black. |
| (388,896,339,133) (733,898,329,130) (388,1229,339,132) (733,1229,329,131) (970,1045,121,168) | — | — | small islands; nothing readable landed on a surface anyone looks at. Leave black. |

Wheels, suspension, floor, diffuser, halo, mirrors: `Car_Mandatory` carbon,
not paintable.

## Number blocks

N1 / N2 on the endplates' OUTER faces; N3 on the nose top. The build guard
(`check_number_blocks`) allows base colour or the flat white number panel and
nothing else. **Stamps probed 2026-09-14** (magenta over the three blocks,
reloaded): every stamp lands inside its block, centred on the white panels.
**Chips**: all three Car Number chips were set to black in the Paint Shop
and the stamped 404 verified on the car; which chip drives which stamp was
therefore not needed and is not recorded.

## Rear-wing endplates — the logo slot 1 spot (v1.0)

Each endplate's outer face is a slanted hexagon: top edge y ~30, a tall
FRONT edge, a sloping REAR edge, bottom y ~285; the number block sits in the
upper half. The two faces are exact mirrors in x: **x_L = 3071 − x_R**
(blocks 1124..1225 <-> 1846..1947; the fan of stretched UV at the lower
front corner has its apex at (1211, 210) / (1860, 210)). Both faces read
UPRIGHT from outside the car, so one piece of upright art goes on both with
no transform. The clean quad below the number at row 224 spans x 1065..1195
on the right face; the 70 px logo slot 1 mark sits at (1140, 224) /
(1931, 224) — 34 texels forward of the block centre, clear of the sloping
rear edge and of the tyre from a level side view. A 200-px wordmark there
(first pass) read truncated behind the tyre; it was replaced with the smaller
logo slot 1 mark.

## Spec map — VALIDATED 2026-09-14, B3 unchanged

A/B at one top-lit pose, spec TGA present vs parked: with B3 the body renders a neutral
satin (mean RGB 40/40/41, blue−red +1.6, no hotspot); without it the black
goes glossy and picks up the sky (blue−red +6.2). White crisp, orange the pop.
No ladder was needed on this car. The sim writes `car_spec_<id>.mip` ~3 s
after the TGA lands; that .mip is what Trading Paints takes.

## How to edit this car later — the breadcrumbs (v1.1, 2026-09-14)

**Ready-made paint:** `paints/fia-f4/` (on-track verified). To get it back exactly, copy it from `paints/fia-f4/`. Do not change the
design without sign-off; anything experimental goes on a branch and a new
release folder, never over v1.1.

**Build entrypoint:** `python src/team_f4.py` (writes `car_<id>.tga` +
`car_spec_<id>.tga` into `%USERPROFILE%\Documents\iRacing\paint\formulair04\`;
`--here` for the cwd, `--png` for a flat PNG, `--no-spec`). Personalize it with
`--id <your customer ID>`, `--driver "<name>"` and `--logo1 <image>` /
`--logo2 <image>`; with no flags the output carries a neutral YOUR LOGO
placeholder in both logo slots and a blank driver strip. It imports
`src/teamscheme.py` (palette + marks), `src/sponsors.py` (logo slots, driver
strip, logo loader) and `src/f4_islands.py` (the island edge table —
regenerate it from your own template first, see above). Rebuilding with the
committed fonts reproduces the release bytes; on another Pillow/font it will
not — the release TGA is the lock.

**Every placement is a constant at the top of `src/team_f4.py`, in LEFT
texture coordinates; the right side is the mirror (y' = 2257 − y) and text
is composited ROTATE_180 there.** What each one is, and the surface it lands on:

| element | constant(s) | left-texture placement | lands on |
|---|---|---|---|
| sidepod sash | `SASH` (xc 215, tilt 0.28, orange 40, white 20, gap 5), `POD_X0/Y0` (71, 1830) | three bands from the crease row 1830 down to 2040, centre x = 71+215 at the crease, +0.28 per row (top-forward lean); the island's own edges clip it | POD, front of the pod just behind the inlet |
| AÏNTOLOGIC | `POD_WM_W` 440, `POD_WM_CXY` (540, 105) from `POD_X0/Y0` → centre (611, 1935) | 440 texels wide, ~75 tall | POD flank, ahead of the rear tyre (x > ~780 hides behind it) |
| nose centre stripes | `NOSE` (60,1030,860,210), `NOSE_CY` 98 (= row 1128), `NOSE_CS` (36,18,5) | rows 1128±41, x 60..920, skipping the number panel ±12 and the roundel node | NOSE top, tip to cockpit |
| nose number panel | `NOSE_NUM` (254,34,117,131) local → texture (314,1064) | white rounded panel = N3 + 8 margin | NOSE, the stamp lands centred on it |
| team roundel | `NOSE_BADGE_D` 110, `NOSE_BADGE_CX` 600 (→ texture x 660), `RING_GAP` 5, `RING_W` 12 | body gap / white ring / gap / badge, art ROTATE_270 so it reads from the FRONT of the car | NOSE top between the number and the cockpit |
| engine-cover stripes | `EC_X` (1465, 1945), `EC_CS` (top_gap 6, orange 24, gap 4, white 12) | per column: orange rows ridge+6..+30, white +34..+46 below the island's ridge edge from `f4_islands.EC_B` | EC_B upper slope, both sides, behind the F4 decal to the tail tip |
| logo slot 2 | `EC_LOGO2_W` 250, `EC_LOGO2_CXY` (1600, 1262) | centred, ~78 tall | EC_B under the stripes (NOT EC_A — see the clip lesson below) |
| driver strip | `FLANK_DRIVER_W` 110, `FLANK_DRIVER_XY` (837, 1400) | the `--driver` name (blank by default) | FLANK upper rows just ahead of the cockpit opening |
| endplate number panels | `NUMBER_BLOCKS` N1 (1124,74) right, N2 (1845,74) left, `EP_NUM_MARGIN` 8 | white panel = block + 8 | endplate outer faces |
| logo slot 1 | `EP_LOGO1_D` 70, `EP_LOGO1_CXY_R` (1140,224), `EP_LOGO1_CXY_L` (1931,224) | same upright art both sides, no transform (both faces read upright); faces mirror as x_L = 3071 − x_R | under each endplate number, forward-biased 34 texels |
| spec map | `SPEC_VARIANTS["B3"]`, `SPEC_ORANGE_GROW` 3 | derived from the colour map by nearest colour; number blocks forced to the `num` value | everything |

Things that are NOT painted and why: front wing / front endplates / rear
wing (restraint, approved black); the engine-cover spine (unmapped, black by
design — do not add a stripe there); cutoff triangle + extinguisher
(the sim's own decal layer draws them at the front of the engine cover);
the sidepod tops (black).

**Hidden / occluded areas to remember:** FLANK rows 1240..1388 (invisible
except the cockpit surround); the rear ~120 texels of each POD behind the
rear tyre from a level side view; the gap between EC_B's crease edge and
EC_A's top edge (rows ~1305..1347 at x 1600 — nothing drawn there renders);
EC_A itself is only 50 rows tall ahead of x 1720; the lower-front corner of
each endplate face (the UV fan under the number) is stretched.

**Seams that matter:** the ridge edge of EC_B (the top of the twin stripes)
is the crease between the spine strip and the upper slope — hang things off
`f4_islands.EC_B` per column, never a constant row; the pod crease (row
1830 at the front, 1906 at the rear) is where the sash starts; the nose
centre row 1128 is also the global mirror axis (1128.5).

**To probe again:** `python tools/probe_multi.py team_f4 NAME:x,y,w,h:cols,rows ...`
then `python tools/walk.py` + `tools/contact_sheet.py` (+ `tools/zoom.py`), read
from level sides / dead front / top. `tools/template_layers.py <zip> <dir>`
regenerates the wire / block pictures; `tools/f4_islands_gen.py` regenerates
`src/f4_islands.py` from that wire.

## What was tried and is wrong / not to re-litigate

- **First pass (2026-09-14 afternoon): the engine-cover stripe rode the crease
  on one side and the ridge on the other.** Cause: the two engine-cover rects
  had been taken from a bounding-box guess (`(1010,780,1010,230)` and
  `(1010,1180,1010,270)`) with the mirror axis assumed at their edges. The real
  islands are two tapered pieces per side (EC_B / EC_A above), mirrored about
  row 1128.5, and the ridge edge is a SLOPED line in texture space. Fixed by
  generating the per-column edge table and hanging the stripe from the ridge
  edge of EC_B (`draw_ec_stripes`), then mirroring — identical on both sides by
  construction, checked on level left / right, top and rear-3/4 frames.
- The logo slot 2 mark drawn at rows 1306..1384 on the left "clipped in half"
  on the render: its top half sat in the unmapped gap between EC_B and EC_A.
  Moved onto EC_B under the stripe. Anything that disappears along a straight
  line is off-island — check the edge table before suspecting the code.
- The 8x8 grid's labels on the right side LOOK mirrored at a glance; they are
  rotated 180, not mirrored - zoom before concluding.
- Frame 8 of a walk came back black once (capture raced the redraw). Re-shoot.

## Viewer loop — F4 specifics (2026-09-14)

- `tools/view2.py` works unchanged. The iRacing window was 1296 px wide at
  the start of the session and 1728 px wide after that — crop the 3D pane
  PROPORTIONALLY (`tools/walk.py`: 3%..97% of the width, 18%..87% of the
  height), never with fixed pixels.
- With the wide window a horizontal drag of **65 px ~ 30 deg** on average, but
  the response is non-linear: it lingers around the side views and rushes
  through the fronts/rears. Sweep 12 frames and pick; `tools/contact_sheet.py`
  tiles them with frame numbers.
- Default zoom shows the car small;
  `python tools/view2.py --no-reload --wheel 5` (five ticks in) fills the
  pane with a level side view. The viewer gets driven between calls (zoom
  and pose both change) — never assume a pose.
- `--drag-y -600` is level, `+600` top-down (pitch clamps). A top-down frame
  with the nose at the frame's LEFT has the car's RIGHT side at the frame's
  TOP.
- If your shell/file bridge answers within ~60 s per call, anything longer
  (a 12-frame walk was ~70 s with the old PowerShell walk, 65.5 s with
  `python tools/walk.py --reload` on 2026-10-24) must be started in the
  background, then polled with its read-output / a follow-up sleep call
  until it prints `DONE 12 frames`.
