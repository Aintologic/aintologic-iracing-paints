# Templates

## What and why

iRacing publishes a paint template for each car: a layered image of the car's
body laid out flat. This project reads each car's panel outlines from that
template. You need it:

- for **any car the project hasn't measured yet**, so the AI can measure it, and
- once, for a short setup step, for six of the cars already measured.

The templates are iRacing's property, so they are **not included** in this
project. Download your own from iRacing. Keep it on your computer and don't
share it or commit it to git.

Measured cars that need it for setup: FIA F4, Ray FF1600, HPD ARX-01c, SCCA
Spec Racer Ford, Skip Barber Formula 2000 and Aston Martin Vantage GT3 EVO. The
other four measured cars build without one.

## What "done" looks like

- You have the right template zip for your car saved on your computer.
- For a measured car: you ran its one-time setup step, and it finished without
  errors.
- For a new car: the AI has the template it needs to start measuring.

## For the AI agent

- Template zips are named `<carId>_template_<CODE>.zip`. The car ID is shown in
  iRacing under the car's **Car Info** (for example `#67`).
- Using the wrong template is the most expensive mistake in this project: the
  panel shapes won't match and graphics land in the wrong places. Check the car
  ID in the file name before using it.
- Measured cars: run `python tools/first_run.py <car> <template.zip>` (template
  table in `docs/REGENERATING-GEOMETRY.md`). New cars: follow "Measuring a new
  car" in `AGENTS.md`. The template can live anywhere on the client's computer.
- Never commit, upload or share a template or the files generated from it.
