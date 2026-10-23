# Regenerating car geometry from your own template

Four cars build with **no extra step** — their panel geometry is measured inline
in the code: MX-5 (`team_mx5.py`), Porsche 911 RSR (`team_rsr.py`), Ferrari 296
(`team_f296c.py`), Lotus 79 (`team_l79.py`).

The other six read their panel shapes from the iRacing **template's own UV
outline** (the green "wire" layer in the template PSD). That outline is iRacing's
intellectual property, so the generated geometry files are **not shipped**.
Regenerate them once, from **your own** template, with one command.

## One command

```
python tools/first_run.py <car> <your-template.zip>
```

`<car>` is one of `f4` / `ray` / `hpd` / `srf` / `sbf2000` / `amv` (the full
release slugs work too). Download the template zip for the car from iRacing — you
do not redistribute it; it stays on your machine. The command extracts the
template and writes the geometry where the builder reads it:

| car | template | writes |
|---|---|---|
| `f4` | `148_template_iR04.zip` | `src/f4_islands.py` |
| `ray` | `163_template_GR22.zip` | `src/ray_islands.py` |
| `hpd` | `39_template_ARX.zip` | `assets/hpd-body-mask.png` |
| `amv` | `206_template_AMGT3.zip` | `assets/amv-centre-mask.png` |
| `sbf2000` | `1_template_SBRS.zip` | `assets/sbf2000-centre-mask.png`, `assets/sbf2000-pod-islands.png` |
| `srf` | `23_template_SRF.zip` | `assets/srf-centre-mask.png`, `assets/srf-side-mask.png`, `assets/srf-sash-islands.png` |

Then build the car as usual:

```
python src/team_f4.py --id <your-id> --out .
```

Needs `psd-tools`, `numpy`, `scipy`, `Pillow` (all in `requirements.txt`).

## What it does under the hood

`first_run.py` runs `tools/template_layers.py` to extract the template's layers
(it needs `Wire.png`, the green UV outline), then the per-car extractors below.
The island indices are the ones `tools/probe_islands.py` prints for the reference
templates:

```
# f4   -> src/f4_islands.py
python tools/f4_islands_gen.py <tpl> src/f4_islands.py

# ray  -> src/ray_islands.py
python tools/island_edges.py <tpl> src/ray_islands.py 2053 \
    NOSE_TIP=7 NOSE=4 COWL=8 DECK=20 FLANK=2 REAR=6 LOWER=11 POD=0 SILL=13

# hpd  -> assets/hpd-body-mask.png
python tools/body_mask.py <tpl> assets/hpd-body-mask.png 0 1 6 7

# amv  -> assets/amv-centre-mask.png
python tools/body_mask.py <tpl> assets/amv-centre-mask.png 3 5 14 4 6 leak:1390,940,470,640

# sbf2000 -> two files
python tools/body_mask.py <tpl> assets/sbf2000-centre-mask.png 47 3 96 6 17 18
python tools/island_id_mask.py <tpl> assets/sbf2000-pod-islands.png 8=8 5=5

# srf  -> three files
python tools/body_mask.py <tpl> assets/srf-centre-mask.png 5 10 4
python tools/body_mask.py <tpl> assets/srf-side-mask.png 0 1 6 7 2 3 12 13 14 15 9 8 18 17
python tools/island_id_mask.py <tpl> assets/srf-sash-islands.png 1=1 14=14 12=12
```

## If iRacing repacked a template

If an index no longer matches your template, list them with
`python tools/probe_islands.py <car-module> <tpl> list` and compare against the
car's panel map in `docs/car-maps/`, which explains what each island is. The
Spec Racer's `srf-side-mask.png` is the union of every mirrored body island, and
each car map's "how to edit this car later" section names its constants.
