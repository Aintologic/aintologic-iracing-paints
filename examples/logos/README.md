# Example logo set (optional)

The two per-car logo slots default to a neutral **YOUR LOGO** placeholder
(`placeholder.png`). If you'd rather drop in real marks, this folder has an
example pair you are free to use:

- `cats-dont-suck.png` - a calico-cat roundel (slot 1 position)
- `freakfarm.png` - a code-drawn partner mark (slot 2 position)

Use them two ways:

```
# by the built-in example tokens (cats_dont_suck uses assets/CatsDontSuck.png):
python src/team_mx5.py --id 123456 --logo1 cats_dont_suck --logo2 freakfarm --out .

# or by any image file of your own:
python src/team_mx5.py --id 123456 --logo1 examples/logos/cats-dont-suck.png --logo2 mylogo.png --out .
```

Swap in your own PNGs the same way. With no `--logo1`/`--logo2`, every car
carries the YOUR LOGO placeholder instead.
