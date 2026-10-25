# Releasing a new version

## What and why

A release is a numbered snapshot of this project with a download attached.
Whoever downloads it should get exactly what the change log describes, built
the same way every time, with nothing private inside. This checklist is how
every release gets there, the first one included.

It's short on purpose. Each line is there because getting it wrong in public
is hard to take back: once a download is out, people keep copies.

How version numbers are chosen is explained in the README's
[Versions](../README.md#versions) section.

## What "done" looks like

A release is ready to publish when every box is ticked:

- [ ] **All cars build cleanly.** Every car's builder in `src/` runs with its
  default settings and finishes without an error.
- [ ] **Default builds are byte-identical to `paints/`.** Each car built with
  its default settings produces files that match its ready-made paint in
  `paints/` exactly, byte for byte. If a paint was meant to change, `paints/`
  was updated in the same release and the change log says so.
- [ ] **The privacy check passes.** It looks through the project's files for
  anything that must never be published: customer IDs, names, folder paths
  from someone's computer, links to AI chat sessions, iRacing template files
  and anything generated from them. It also checks commit and tag details for
  customer IDs, machine names and chat links. The only tags allowed are
  version numbers such as `v0.1.0`, on a commit in `main`.
- [ ] **The release notes and the zip pass the privacy check too.** They are
  made outside the project's tracked files, so the check on the project never
  sees them: the notes file, `INSTALL.txt`, `NOTICE.txt` and every file in the
  unzipped download are checked for the same things.
- [ ] **A change log entry and release notes are written,** in plain English.
- [ ] **The ready-made paints zip carries its license files:** `LICENSE.txt` in
  every car folder, and `TRADEMARKS.md` and a `NOTICE.txt` at the top.
- [ ] **The gallery is still right.** If a paint changed, its picture in
  `docs/gallery/` was taken again in iRacing's car viewer.
- [ ] **The maintainer reviewed the draft release** on GitHub before
  publishing it.

## For the AI agent

You can prepare everything up to a draft release. Publishing is the
maintainer's decision: stop at the draft and wait for an explicit yes.

### 1. Pick the version number

Follow the rules in the README's Versions section. The tag is the version
with a `v` in front (`v0.1.0`). Once a release is published, its tag is never
moved and its number is never used again. A mistake gets fixed in a new
version.

While the first number is 0, every release is an early preview: it is marked
as a pre-release on GitHub, and its title ends in "(early preview)", for
example "iRacing Paints 0.1.0 (early preview)". From 1.0.0 on, releases are
not marked that way.

### 2. Check the builds

Six cars need their one-time setup step first
(`python tools/first_run.py <car> <template.zip>`; see
[`REGENERATING-GEOMETRY.md`](REGENERATING-GEOMETRY.md)). Then build every car
with its default settings, choosing only the output folder:

```
python src/team_<builder>.py --out out/release-check/<builder>
```

`team_<builder>.py` is the builder named in the README's table, for example
`team_mx5.py`. Compare `car_CUSTOMERID.tga` and `car_spec_CUSTOMERID.tga` with
the same files in that car's folder in `paints/` (for `team_mx5.py`, that is
`paints/mx5-2016-global-cup/`) by SHA-256 hash. A default build writes only
those two files; if a folder holds anything else, find out why before going
on.

### 3. Run the privacy check

The privacy check isn't in this repository yet
([issue #12](https://github.com/Aintologic/aintologic-iracing-paints/issues/12)
is about adding it and running it automatically), so today the maintainer runs
it. Report what you changed and wait for the result before going further.

### 4. Write the change log entry and release notes

Add the new version at the top of [`CHANGELOG.md`](../CHANGELOG.md): what is
new or fixed and why it matters to the reader, then any known issues. Write
the release notes in a file that is never committed, for example
`out/release/notes-vX.Y.Z.md` (git ignores the `out` folder, so it's never committed), in this
order:

1. what this is, in a few plain sentences (while the first number is 0, say
   first that it's an early preview and what isn't in yet);
2. what's in this version;
3. how to use the ready-made paints download;
4. known issues;
5. a short license summary.

Technical detail goes after that, never before.

### 5. Build the ready-made paints zip

Name it `iracing-paints-vX.Y.Z-ready-made-paints.zip` and build it under
`out/release/`. It holds:

- one folder per car, named like its folder in `paints/`, with
  `car_CUSTOMERID.tga`, `car_spec_CUSTOMERID.tga` and a copy of
  `paints/LICENSE.txt`;
- `INSTALL.txt` at the top: extracting the zip, renaming the files with your
  customer ID, the iRacing paint folder for each car (from the README's
  table), where to copy them, and opening the car in the car viewer fresh;
- `TRADEMARKS.md` and `NOTICE.txt` at the top. The notice says the project is
  unofficial, isn't affiliated with iRacing or any car manufacturer, and that
  you should use only logos you own or have permission to use.

Start `INSTALL.txt` and `NOTICE.txt` from the previous release's zip
(`gh release download <previous tag> --pattern "*.zip"`) and change only the
version and whatever actually changed, so the steps people know stay the same.

Unzip it into a folder under `out/` (for example `out/release/unzip-check/`),
compare every paint file's hash with `paints/`, and list the contents. Then
ask the maintainer to run the privacy check on the release notes and the
unzipped folder, and wait for the result. Don't build a source zip: GitHub
attaches one to every release automatically. Never commit the zip.

### 6. Create a draft release

Use the full commit hash that passed the checks as the target, not the branch
name. A draft's tag is only created when it's published, so with `main` as the
target the tag would land on whatever `main` is by then.

While the first number is 0, it's an early preview: add `--prerelease` and
end the title with "(early preview)":

```
gh release create vX.Y.Z --draft --prerelease --target <full commit hash> --title "iRacing Paints X.Y.Z (early preview)" --notes-file out/release/notes-vX.Y.Z.md out/release/iracing-paints-vX.Y.Z-ready-made-paints.zip
```

From 1.0.0 on, leave out `--prerelease` and the "(early preview)" in the
title.

A draft is visible only to the repository's maintainers. Links in the notes
that point at the new tag only work once the release is published. Give the
maintainer the draft's link and stop.

### 7. Publish, after the maintainer says yes

If the date in the change log entry isn't today's, fix it first and run the
checks again. Then:

```
gh release edit vX.Y.Z --draft=false
```

Confirm the tag exists and points at the commit hash from step 6:

```
git fetch --tags
git rev-list -n 1 vX.Y.Z
```

Tags are only ever made by `gh release`. Push `main` only, never `--tags`.

### Undo

Only when the maintainer asks for it, take a release back down:

```
gh release delete vX.Y.Z --cleanup-tag
```

That removes the release, its download and its tag. Remove the tag from your
own copy of the repository too (`git tag -d vX.Y.Z`), so it can't be pushed
again by accident. Don't use that version number again: anyone who already
downloaded it keeps their copy. Keep its change log entry, add a line saying
it was withdrawn and why, then fix the problem and release it as a new
version.

If the problem is private data, stop and tell the maintainer: removing a
release doesn't remove anything from the project's history.
