![AÏntologic iRacing paints](assets/brand/banner.png)

# AÏntologic iRacing paints

Code-generated racing liveries for iRacing. One design system — the **AÏntologic
team scheme** (papaya / black / white, drawn entirely in Python) — retargeted
across many cars, so the same marks and materials move from car to car by
changing only the panel map. No hand-painting, no imported artwork: every stripe,
wordmark, badge and material value is drawn in code and reproducible.

You can use it two ways:

- **Grab a ready-made paint** and drop it in iRacing (no Python needed), or
- **Personalize** — build your own copy with your iRacing customer ID, your name
  on the driver strip, and your own two logo images.

## The cars

Ten cars wear the scheme. **On-track verified** means the paint has been raced
in iRacing and accepted; the rest are approved on the render.

| car | iRacing # | paint folder | on-track verified |
|---|---|---|---|
| Global Mazda MX-5 Cup | 67 | `mx5 mx52016` | ✅ yes |
| FIA F4 | 148 | `formulair04` | ✅ yes |
| SCCA Spec Racer Ford | 23 | `specracer` | ✅ yes |
| Aston Martin Vantage GT3 EVO | 206 | `amvantageevogt3` | ✅ yes |
| Porsche 911 RSR | 102 | `porsche991rsr` | render-approved |
| Ferrari 296 Challenge | 203 | `ferrari296challenge` | render-approved |
| Ray FF1600 | 163 | `raygr22` | render-approved |
| Lotus 79 | 25 | `lotus79` | render-approved |
| HPD ARX-01c | 39 | `hpdarx01c` | render-approved |
| Skip Barber Formula 2000 | 1 | `rt2000` | render-approved |

## Gallery

In-sim previews of the ready-made paints, in their neutral default (blank driver
strip, "YOUR LOGO" placeholders). ✅ = on-track verified. The full set is in
[`docs/gallery/`](docs/gallery/).

**Global Mazda MX-5 Cup ✅**

![MX-5](docs/gallery/mx5-2016-global-cup.jpg)

**FIA F4 ✅**

![FIA F4](docs/gallery/fia-f4.jpg)

**SCCA Spec Racer Ford ✅**

![Spec Racer Ford](docs/gallery/spec-racer-ford.jpg)

**Aston Martin Vantage GT3 EVO ✅**

![Aston Martin](docs/gallery/aston-martin-vantage-gt3-evo.jpg)

Porsche 911 RSR, Ferrari 296 Challenge, Ray FF1600, HPD ARX-01c, Lotus 79 and
Skip Barber Formula 2000 are in [`docs/gallery/`](docs/gallery/) too — all ten
cars.

## Quick start (no coding)

Every car ships a ready-made paint under `paints/<car>/`, drawn with the neutral
defaults (a blank driver strip and a "YOUR LOGO" placeholder in both logo slots).

1. Open `paints/<car>/` and take `car_CUSTOMERID.tga`.
2. Rename it to `car_<your iRacing customer ID>.tga` — e.g. `car_123456.tga`.
   (Your customer ID is on your iRacing account page.)
3. Copy it into your iRacing paint folder for that car:
   `%USERPROFILE%\Documents\iRacing\paint\<paint folder>\`
   (the folder names are in the table above).
4. In iRacing, make sure custom paints are enabled. Your car now wears it.

Optional: the companion `car_spec_CUSTOMERID.tga` is the material (spec) map —
rename it the same way to `car_spec_<id>.tga` and drop it in the same folder for
the satin/gloss finish.

## Personalize it (one command)

With Python installed (see **Build from source**), build your own copy with your
ID, name and logos:

```
python src/team_mx5.py --id 123456 --driver "A. DRIVER" --logo1 mylogo1.png --logo2 mylogo2.png --out .
```

- `--id` names the output file `car_<id>.tga`.
- `--driver` sets the name on the cockpit strip (omit it for a blank strip).
- `--logo1` / `--logo2` drop your own PNG into the two per-car logo slots (slot 1
  is the position the example uses for a roundel; slot 2 for a wordmark). Omit
  them for the neutral "YOUR LOGO" placeholder.
- `--out` is the output folder (default `./out`).

Swap `team_mx5.py` for any car's builder in `src/` (`team_f4.py`, `team_rsr.py`,
`team_f296c.py`, `team_l79.py`, `team_hpd.py`, `team_srf.py`, `team_ray.py`,
`team_sbf2000.py`, `team_amv.py`).

An **optional example logo set** ships in `examples/logos/` if you want to see
real marks in the slots instead of the placeholder.

## Build from source

```
pip install -r requirements.txt
python src/team_mx5.py --id 123456 --out .
```

Requires Python 3 and Pillow (plus numpy; scipy is only needed to regenerate car
geometry, below). The four bundled fonts (`fonts/`) are under the SIL Open Font
License — see `fonts/OFL.txt`.

### Cars that need a one-time geometry step

Four cars — MX-5, Porsche 911 RSR, Ferrari 296, Lotus 79 — build straight away;
their panel geometry is measured inline in the code.

The other six — FIA F4, Ray FF1600, HPD ARX-01c, Spec Racer Ford, Skip Barber,
Aston Martin — read their panel shapes from the iRacing template's own UV
outline, which is iRacing's intellectual property and is **not** included here.
Download your own template for the car from iRacing and regenerate the geometry
once, with a single command:

```
python tools/first_run.py <car> <your-template.zip>
```

(`<car>` is `f4` / `ray` / `hpd` / `srf` / `sbf2000` / `amv`.) Then build the car
normally. See [`docs/REGENERATING-GEOMETRY.md`](docs/REGENERATING-GEOMETRY.md).

## How it works

The method and the per-car panel maps are documented in `docs/`:

- `docs/PROJECT.md` — what this is and the design goals.
- `docs/PAINT-SCHEME.md` — the livery language (palette, every mark).
- `docs/IRACING-PAINTING-PLAYBOOK.md` — the build method.
- `docs/PANEL-PROBING.md` — how a car's UV layout is discovered.
- `docs/car-maps/` — the verified panel map for each car.

## Notice

This is an unofficial, fan-made project. It is **not affiliated with, endorsed by,
or sponsored by iRacing or any car manufacturer**. iRacing car templates are
iRacing's intellectual property and are **not included** — download your own from
iRacing. The paints add no manufacturer logos; iRacing draws its own.

When you put your own logo on a car (`--logo1` / `--logo2`), **use only logos you
own or have written permission to use.** iRacing's
[Custom Paint Policy](https://ir-core-sites.iracing.com/members/pdfs/20240926-iRacing_Custom_Paint_Policy_dated_Sept_09_2024.pdf)
bars third-party trademarks or logos without the owner's written permission, and
bans political, offensive, and tobacco / alcohol / drug content. Use is personal
and non-commercial.

## License

- **Code** — everything in `src/` and `tools/`, and `assets/brand/render_banner.py`:
  GNU **AGPL-3.0-or-later**. See [`LICENSE`](LICENSE).
- **Ready-made paints** (`paints/`) and the **example logos** (`examples/logos/`):
  **CC BY-NC-SA 4.0**, subject to the trademark terms — see each folder's
  `LICENSE.txt` and [`TRADEMARKS.md`](TRADEMARKS.md).
- **Fonts** (`fonts/`): SIL **Open Font License 1.1**. See [`fonts/OFL.txt`](fonts/OFL.txt).
- **Names and logos** — AÏntologic, Freak Farm Racing, Cats Don't Suck — are
  **not** covered by any of the above. See [`TRADEMARKS.md`](TRADEMARKS.md).
