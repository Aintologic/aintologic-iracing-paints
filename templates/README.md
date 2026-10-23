# Templates

iRacing paint templates are **not** in this repo. They are iRacing's assets, and
the full pack is about 5.7 GB.

They live in `Area51/templates/`, which is gitignored:

    Area51/templates/all_iracing_templates/     the full pack, unzipped
    Area51/templates/all_iracing_templates.zip  the pack as downloaded
    Area51/templates/used/                      templates for cars we have painted

Copy `Area51/` between machines by hand (robocopy / USB / file share) — never
through the cloud.

## Finding the right template

Naming is `<carId>_template_<CODE>.zip`. Get the car ID from iRacing:
`Racing -> My Content -> My Licensed Cars -> View Car -> Car Info` — it is shown
top right as `#67`.

| car | ID | file |
|---|---|---|
| Global Mazda MX-5 Cup | 67 | `Area51/templates/used/67_template_MX16.zip` |

Using the wrong template is the most expensive mistake in this project — see
`docs/IRACING-PAINTING-PLAYBOOK.md` Rule 1.
