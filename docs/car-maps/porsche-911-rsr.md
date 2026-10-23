# Panel map — Porsche 911 RSR

- iRacing car ID: **102** (Car Info panel shows `#102`, verified 2026-09-14).
- Template: your own iRacing RSR template (`102_template_RSR.zip` ->
  `Porsche 911 RSR.psd`, 2048x2048). Layer names differ from the F4 template:
  the base is `Base Scheme`, the decal layer is `Car Decal`, there is no
  `Car_Mandatory`; extra layers `IMSA Number Blocks` and `IMSA Leaderboard
  Blocks` exist (invisible; the IMSA series stamps numbers elsewhere).
- Paint folder: `%USERPROFILE%\Documents\iRacing\paint\porsche991rsr\` (the sim
  creates it when the car is first viewed; nothing else lives there).
- Paint file: `car_<id>.tga` (your iRacing customer ID, `--id`).
- Build: `src/team_rsr.py`.
- Status: **LOCKED as `releases/porsche-911-rsr/v1.0-2026-09-14/`** (approved on the
  render 2026-09-14 evening; on-track verification pending — a change is a new version).

Every row below was read off the car in iRacing's car viewer from labelled
probes (`tools/probe_multi.py` island grids 2026-09-14, then
`tools/probe_ruler.py` numbered bands). Unprobed rows say so.

## Template anchor blocks (from the PSD layers)

| block | x | y | w | h | lands on |
|---|---|---|---|---|---|
| N1 | 921 | 772 | 87 | 73 | RIGHT door, front, just below the window sill (island A) |
| N2 | 487 | 1251 | 107 | 113 | hood, centred on the centre line 1306 (the block is drawn ROTATED in the PSD; this is its bbox) |
| N3 | 921 | 1766 | 87 | 73 | LEFT door, front (island D) |

IMSA number blocks (not used by the WEC-style stamp seen in the viewer):
`(1646,69,98,73)`, `(916,772,98,73)`, `(540,1255,73,98)`, `(916,1766,98,73)`.
IMSA leaderboard blocks `(270,705,65,57)`, `(615,705,64,56)`.

Sponsor blocks (magenta, the template author's suggested spots): rear wing
`(1356,96,279,27)`?, wing `(872,317,643,43)` + `(872,454,643,79)`, doors
`(905,707,297,55)` R + `(905,1849,297,55)` L, quarters `(1006,893,311,47)` R +
`(1006,1674,311,47)` L, front bumper `(87,1193,27,225)`.

## THE RULE OF THIS UV — mirror about texture row 1306

**Right side = left side reflected about row 1306: right y = 2612 − left y,
x identical.** Measured on the template's green island outlines (sill strips
583/1951 and 658/1888, quarters 724/1492, fenders 822/1481, small pairs
803/1687, 1144/1340, 1180/1312 — every pair sums to 2611–2612) and confirmed
on the render (door cells A / D, quarter cells B / E, sill cells C / F land
in mirrored spots). Centre-line panels are centred on 1306: the hood island
(1036..1576), the roof / rear window island M, the rear deck island P, the
windscreen banner Z, the front bumper island K.

From a level side view the LEFT islands read upright (texture +x = rearward,
+y = DOWN the car) and the RIGHT islands read ROTATE_180 (+x = rearward,
+y = UP the car). Same recipe as the F4: draw the left side, mirror the
geometry, composite text afterwards (ROTATE_180 on the right).

## Islands (LEFT side unless noted; right = mirror)

| island | rect (bbox) | render | what it is |
|---|---|---|---|
| D door | (843,1655,491,262) | upright, level side | the door: x 843 = front shut line, ~1300 = rear shut line; y 1655 = window sill, 1917 = bottom of the door (top of the sill strip). N3 in its front-top corner. |
| F sill | (773,1888,712,141) two strips: (785,1951,711,78) lower, (773,1888,712,66) upper | upright | rocker / sill under the door, wheel arch to wheel arch (F1 behind the front wheel, F6 ahead of the rear wheel) |
| E rear quarter | (1255,1492,658,396) | upright | rear quarter: row 1492..1624 = the top of the fender / engine-cover shoulder up to the rear light; 1624..1756 = the haunch with the side intake at its front (x ~1255..1400); 1756..1888 = the lower quarter behind the door, above the rear wheel |
| U front fender | (288,1481,507,309) | from above: +x rearward, +y outboard | front fender: row 1481..1584 inner (against the hood), 1584..1687 = the crown, 1687..1790 = the side face down to the arch. U1 (x 288..414) = the headlight tip, U4 (666..795) = the rear of the fender at the A-pillar / door shut. |
| A / B / C / S | mirrors of D / E / F / U at y' = 2612 − y | ROTATE_180 | right door / quarter / sill / fender |
| H hood | (215,1036,529,540), centre row 1306 | from above with the nose down: +x = rearward, +y = car's LEFT | the front lid. x 215 = nose lip, cols toward 744 = windscreen base (exact x extents: ruler probe, below). N2 sits in it at x 487..594. |
| K front bumper | (10,805,230,1002), centre row 1306 | upright from the front; +y = car's LEFT | the whole front bumper / apron, unwrapped as a tall strip: y runs ACROSS the car (1002 texels for the full width — good resolution), x (2 x 115) runs down the face. (ruler probe below) |
| Z windscreen banner | (834,1058,100,496), centre 1306 | from above: +y = car's LEFT | the sun-strip band at the top of the windscreen |
| M roof + rear window | (807,1000,624,500), centre 1306 | from above: +x rearward, +y = car's LEFT | roof (cols x ~963..1275 visible on the roof) and the rear glass / cover |
| P rear deck | (1431,1079,536,453), centre 1306 | from above | the rear deck under the wing (P4..P8 read from the top) |
| Q engine cover | (125,153,377,290) | ROTATE_180 from the rear | the sloping engine cover / tail top under the wing between the rear lights |
| T rear bumper | (952,12,1087,191) | upright from the rear; +x = car's RIGHT | row 12..107 = the tail panel between the lights (T3 / T4 at the centre, boundary x 1495); row 107..202 = the lower bumper band wrapping both corners (T7 = left corner, T12 = right corner) |
| R rear wing | (854,313,678,247) | from behind / above | wing plane: top row = the rear face, bottom row 436..560 = the top surface, span along x |
| wing endplates | not found yet | — | render carbon-black with everything probed so far — likely `Car Decal`/unpaintable. **Not a logo-slot-1 spot on this car.** |
| I11 (8,379,832,264), X (10,10,496,102), W (1579,247,436,95), L (9,568,255,115), J (476,1072,215,151) | — | — | probed 2026-09-14 pass 3; nothing readable landed on a surface read from the level / top sweeps. Leave black. |

Wheels, splitter, diffuser, wing endplates, mirrors' stalks, cage: carbon,
not paintable.

## Ruler probes (tools/probe_ruler.py, pass 4, 2026-09-14) — centre lines and extents

| panel | what the ruler showed |
|---|---|
| hood H | x bands from 215: bands 1–3 (215..314) are the nose lip curling down to the bumper, 4..15 (314..710) the flat lid from the headlights to the windscreen base; the black line at y=1306 runs through the Porsche crest and between the two louvre vents (vents at x ~350..480 either side of the centre, sim geometry). Number stamp lands centred on N2. |
| front bumper K | y bands of 40 from 805: bands 4..23 (925..1725) are the visible face, band 13 holds the centre — **1306 confirmed** on the crest / intake centre; 800 texels ≈ the full 2.0 m width. Labels read rotated 90° CCW from the front: **texture +x = UP the face** (x 240 = hood lip, x 10 = splitter), +y = car's LEFT. |
| tail T | x bands of 45 from 952 read upright from dead rear, band 1 at the car's LEFT corner: **+x = car's RIGHT**. Centre ≈ **1500** (the black line at 1495 sat ~15 texels left of the exhaust / light-bar centre — refine with the stripe on the render). Row 12..~100 exists only between the lights (x ~1312..1680); rows ~70..202 run the full width under the lights and wrap both corners. |
| engine cover Q | x bands of 25 from 125 read upright from dead rear and from above with the nose up: +x = car's RIGHT, **+y = rearward** (153 = front edge under the rear glass, 443 = the crease onto the tail panel). Centre ≈ **318**. Rows 153..~300 carry the three louvre grilles (sim geometry, the centre one on the centre line); the oil-filler cap sits at ~(318, 400). Told apart from P by label size (single digits big, double digits small = X bands). |
| roof M | y bands of 25 from 1000: bands 3/4..20 (1050..1500) span the roof between the rails; centre ≈ **1300 ±10** (yaw in the frame; verify with the stripe). x: the roof starts at the windscreen header (~840) and M runs unbroken over the rear glass to 1431 where Q's front edge (red bar) begins. |
| P (1431,1079,536,453) | only its rear column (x ~1833..1967) showed, on the deck lip under the wing mounts; the rest is hidden. Not painted in v1. |
| windscreen banner Z | Z1 (low y) at the car's right, Z4 at the left from the front; paints solid (not glass). |
| Car Decal layer | the sim draws the cutoff triangle + extinguisher "E" at both windscreen-base corners (texture ~(676,1066) / (676,1554)) and the Michelin arch decals; the WEC / PRO / iRacing door and hood decals of the default paint are NOT drawn over a custom paint. |

## Viewer loop — RSR specifics (2026-09-14)

- `tools/view2.ps1` works unchanged. Window 1728 px wide.
- **Ctrl+R does NOT reset the camera pose** — it is cumulative across
  reloads and you move it too. Sweep and pick, never assume a pose.
- `tools/walk.ps1 -DragY -600` (level, 12 frames) and the new
  `tools/walk_top.ps1` (top-down, 8 frames) tile with `tools/contact_sheet.py`;
  a reload + both sweeps takes ~2.5 min — start it in the background and poll.
- The viewer-zoom helper (`-Wheel N`) zooms; +3 from the default fills the pane
  with a level side; top-down needs −2 back out to fit the car.

## How to edit this car later — the breadcrumbs (v1.0, 2026-09-14)

**Locked:** `releases/porsche-911-rsr/v1.0-2026-09-14/` (approved on the
render; on track pending). Restore with
`python src/restore.py v1.0-2026-09-14 --car porsche-911-rsr`. Keep anything
experimental on a branch and a new release folder, never over v1.0.

**Build entrypoint:** `python src/team_rsr.py` (writes `car_<id>.tga` +
`car_spec_<id>.tga` into `%USERPROFILE%\Documents\iRacing\paint\porsche991rsr\`;
`--id` sets your customer ID, `--driver` the name on the door strip, `--logo1`
and `--logo2` the two logo images, `--here` for the cwd, `--png` for a flat PNG,
`--no-spec`). With no flags the output carries a neutral "YOUR LOGO" placeholder
in each logo slot and a blank driver strip. It imports `src/teamscheme.py`
(palette + marks) and `src/sponsors.py` (logo slots, driver strip, logo
loader). Rebuilding on the same Pillow/font reproduces the release bytes; on
another it will not — the release TGA is the lock. Lock a new version with
`tools/lock_release.py <car> <version> <folder>`.

**Every placement is a constant at the top of `src/team_rsr.py`.** Side
elements are in LEFT texture coordinates; the right side is the mirror
(pixel row y' = 2611 − y, `mirror_geometry`) and text is composited
ROTATE_180 there (`place`). Centre-line panels are drawn once on their own
islands. What each constant is, and the surface it lands on:

| element | constant(s) | placement | lands on |
|---|---|---|---|
| ONE stripe recipe | `CS` = (44, 22, 5) orange / white / gap texels | used by the hood, roof, engine cover and tail; they all render the same px per texel (tick-probed) | — |
| front bumper | `BUMPER_CS` (42, 21, 5) → **orange only** (42 wide), `BUMPER_X` (10..240), row `BUMPER_CY` 1306 | down the whole face into the intake | K island; x = height (240 = hood lip, 10 = splitter), y across the car |
| **hood V** | `HOOD_X` (215..666), `HOOD_CY` 1306, `HOOD_V_X0` 215, `HOOD_V_X1` 640, `HOOD_V_WMAX` 22; drawn by `hood_wedges()` + the orange rectangle in `centre_panels()` | orange 44 constant nose lip → cowl; each white is a wedge, inner edge on the orange's 5-texel gap, outer edge linear from 22 wide at x 640 to 0 at x 215 | H island; stops at 666 — x ≥ 667 is the louvre-lip islands |
| louvre lips | `LIP_R` (667,1180,77,120), `LIP_L` (667,1312,77,120), `LIP_SCALE` 0.82, `HOOD_LIP_X` 470, `LIP_WHITE` True | white at each lip's inner end, `wedge_w(470) × 0.82` texels wide, so the ledge continues the wedge instead of printing a black bar; `LIP_WHITE = False` for black lips | the two thin ledges in front of the number plate |
| hood number panel | N2 (487,1251,107,113) + `HOOD_NUM_MARGIN` 8 | white plate composited ON TOP of the stripe, no gap | hood, centred on 1306; the stamp lands centred |
| windscreen banner | `BANNER_WM_W` 320, `BANNER_WM_CXY` (884,1306), art ROTATE_270 | reads from the front | Z island (834..934 × 1058..1554) |
| roof + rear glass | `ROOF_CS` = CS, `ROOF_X` (945..1431), `ROOF_CY` 1300 | starts BEHIND the Z island (which sits inside M's bbox), runs unbroken to the engine cover | M island |
| roof roundel | `ROOF_BADGE_D` 200, `ROOF_BADGE_CX` 1150, `RING_GAP` 6, `RING_W` 14, art ROTATE_270 (reads from the front) | the node the roof stripe passes through | M island, roof centre |
| engine cover | `COVER_CS` = CS, `COVER_Y` (153..443), `COVER_CX` 319 | over the centre louvre and the filler to the tail crease | Q island (+x = car's right, +y rearward) |
| tail | `TAIL_CX` 1496, `TAIL_CS` = CS, `TAIL_STRIPE_Y` (12..44), `TAIL_WM_W` 260 at (1496, 74) | stripe stub under the rain-light housing, AÏNTOLOGIC on the panel between the lights | T island (+x = car's right); the lower band 107..202 is hidden behind the diffuser — nothing goes there |
| fender sash | `SASH` (xc 682, tilt 0.28, 46/23/5), `SASH_Y` (1584..1790) | three bands, crown to arch lip, top-forward lean; rear edge clears the island edge at x 795 | U (left) / S (right) fender side face behind the arch |
| door number panels | N3 (921,1766,87,73) left, N1 (921,772,87,73) right, + `DOOR_NUM_MARGIN` 8 | drawn on the blocks themselves (not mirrored) | front of each door, mid-height |
| AÏNTOLOGIC door | `DOOR_WM_W` 260, `DOOR_WM_CXY` (1160,1798) | behind the number panel, centred on it | D / A door islands |
| driver strip | `DOOR_DRIVER_W` 130, `DOOR_DRIVER_XY` (1140,1662) | the driver name (`--driver`; blank by default) on the window sill | top of the door |
| logo slot 2 | `Q_LOGO2_W` 240, `Q_LOGO2_CXY` (1560,1690) | rear-quarter haunch behind the side intake, above the rear wheel, same both sides | E / B quarter islands |
| logo slot 1 | `Q_LOGO1_D` 76, `Q_LOGO1_CXY` (1385,1828) | lower rear quarter under the intake, just behind the door seam, both sides, upright (text rule) | E / B quarter islands |
| spec map | `SPEC_VARIANTS["B3"]`, `SPEC_ORANGE_GROW` 3 | Satin-True, derived from the colour map by nearest colour; number blocks forced to `num` | everything — validated on the RSR by A/B (release `closeups-spec-ab.jpg`) |

**Not painted and why:** the rear wing (restraint, black like the F4's
wings); the sills; the rear bumper's lower band (hidden); the P deck lip; the
mirrors; the front-bumper whites (the V ends at the crest by design); the
louvre openings (geometry, they sit in the black).

**Hidden / occluded areas to remember:** hood x > ~660 (under the cowl);
the louvre openings x ~335..465 hide anything beyond ±36 texels of the
centre line; the tail's lower band y 107..202 behind the diffuser; the rear
~120 texels of nothing — the quarter's E12 cell is cut by the rear arch; the
roof's Z banner island lives inside the M bbox.

**Seams that matter:** the crest (hood lip x 215 ↔ bumper x 240) — the
orange widths were matched on the render there (44 vs 42); the roof → engine
cover transition (M x 1431 ↔ Q y 153) — same recipe both sides, centres 1300
/ 319 measured; the tail stub ↔ cover (1496 / 319). Judge centres from DEAD
front / rear frames only — 3/4 frames lied twice on this car.

**Paint Shop setting:** set all three Car Number chips to `#0C0C0D` in Paint
Shop → Paint Your Car (per car).

**To probe again:** `python tools/probe_multi.py team_rsr NAME:x,y,w,h:cols,rows ...`
(island grids), `tools/probe_ruler.py` (numbered bands, centre lines),
`tools/probe_ticks.py` (ticks across the live stripe for width measurement),
then `tools/walk.ps1` / `tools/walk_top.ps1` + `tools/contact_sheet.py`, read
from level sides / dead front / dead rear / top. `tools/template_layers.py
<zip> <dir>` regenerates the wire / block pictures.

## Tried and wrong / not to re-litigate

- Roof stripe from x 840 painted across the windscreen banner: the Z island
  (834..934) sits INSIDE the roof island's bbox (807..1431). Start the roof
  stripe at 945.
- Tail wordmark on the lower band (y 107..202): invisible, the diffuser
  covers it. Only the outer corners of that band show from behind.
- Tail centre 1495 (the strip's midpoint) is ~15 texels left of the car's
  centre; 1512 measured against the rain-light housing with a 10-texel tick
  ruler from dead rear.
- Logo slot 1 at (1345,1815) straddled the door / quarter seam; moved
  rearward under the intake.

## Pass 2 (2026-09-14, review red boxes): one stripe width, the louvre lips

- **Per-panel stripe widths were guesses and wrong.** Tick probes
  (`tools/probe_ticks.py` over the live stripe + a measurement script on
  top-down frames) showed the hood, roof and engine cover all render
  the same px per texel from above (0.61–0.65 at one zoom, 0.80/0.81 roof
  vs cover at another), and the bumper matches the hood lip at the crest
  from dead front (rendered ratio = texel ratio). So ONE recipe, `CS =
  (44, 22, 5)`, on every centre-line panel; the bumper 42/21/5 (renders
  ~5 % larger per texel than the lip). The old 48 on the cover and 50–56 on
  the bumper were the roof→cover step and the nose step flagged in review.
- **The two islands (667,1180,77,120) / (667,1312,77,120) are the LOUVRE
  LIPS** (probed magenta / green, 2026-09-14): they flank the stripe just
  ahead of the number panel. They sit inside the hood island's bbox at its
  rear, so the hood stripe drawn to x 744 painted its white bands onto them
  — the "wide white sections" under the panel. Hood stripe now ends at
  x 662. Anything you want on the louvre lips is drawn there deliberately.
- **The louvre openings (x ~335..465) swallow the outer half of the white
  bands** (only ±36 texels of flat hood between them). Pass 2 stopped the
  whites at x 331 with an orange-only bridge to the panel — **that was
  rejected (pass 3 rule): the stripe is ONE constant graphic from
  bumper to windscreen; louvres, seams and the number panel are occluders
  and must never change the stripe geometry.** The hood stripe is now
  drawn full width and full length (215..666) with no skips, and the
  number panel is composited on top of it with no gap. Do not re-litigate.
- **Pass 4 — the louvre lips are painted, not black.** From dead front the
  two lip islands render as thin horizontal LEDGES right in front of the
  number panel, spanning the louvres' width, crossing the stripe. Black
  lips were the "black step-in / shoulders" flagged in review. Rainbow probe
  (lip-band probe): each lip's texture y runs the hood's way
  (+y = car's left); the inner end (1300 / 1312) sits on the white band's
  inner edge; the lip renders ~1.2x LARGER per texel than the hood
  (27 lip texels read 46 px where 22 hood texels read 30) → `LIP_SCALE`
  0.82, `lip_w` 18 texels of white at the inner end of each lip, rest
  body. The white bands now run unbroken nose → lips → panel from the
  front. The louvre OPENINGS still clip the outer part of each white
  (tapering slivers) — that is real geometry and stays.
- **Pass 5 — CHANGE OF DIRECTION (2026-09-14 late): the hood gets
  its own tapered V / spear.** Constant-width whites through the louvre
  geometry never read as one stripe from the front, whatever was done
  with the lips. New hood rule, this chassis only: the papaya centre band
  stays constant (44) and centred nose → cowl and straight down the
  bumper; the two whites are WEDGES — inner edge on the orange's gap,
  outer edge tapering linearly from full width (`HOOD_V_WMAX` 22) at
  `HOOD_V_X1` 640 to nothing at the nose lip `HOOD_V_X0` 215 (the red
  guide lines); the bumper is orange only. Louvres, lips and the number
  panel sit in the black / on top; nothing wraps them. The lips carry the
  wedge at its local width (`LIP_WHITE`, `HOOD_LIP_X` 470) — set
  `LIP_WHITE = False` for black lips. A bolder spear (`HOOD_V_WMAX` 50,
  `HOOD_V_X1` 660) was rendered too: the louvre openings swallow its wide
  part between x 335..465 and the V reads broken from above — not offered
  as the default.
- The visible hood is x ~215..~660 from above; the ticks 665..740 never
  showed (under the cowl).
- Tail centre: 1512 measured 18–20 px right of the exhaust / light centre
  from dead rear → **1496**. Engine cover 318 → 319. Do not judge centres
  from 3/4 frames; the first 1500→1512 move came from one.
