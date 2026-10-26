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
  default settings and finishes without an error. All ten are checked, the
  six that need the one-time setup step included, on a computer that has
  iRacing's templates (`tools/check_builds.py --all`).
- [ ] **Default builds are byte-identical to `paints/`.** Each car built with
  its default settings produces files that match its ready-made paint in
  `paints/` exactly, byte for byte. If a paint was meant to change, `paints/`
  was updated in the same release and the change log says so.
- [ ] **Every car reads the design settings.** Built with each sample design
  in `examples/designs/`, every car builds; the example-scheme sample gives
  exactly its default paint, and every other sample a different one
  (`tools/check_builds.py --all` checks this too).
- [ ] **The privacy check passes** (`tools/privacy_check.py --history`). It
  looks through the project's files, and every older version of them, for
  things that must never be published: numbers shaped like customer IDs,
  folder paths from someone's computer, race results, links to AI chat
  sessions, iRacing template files and anything generated from them, keys.
  It also checks commit and tag details for the same things. Tags must be
  version numbers such as `v0.1.0` (it checks that) and sit on a commit in
  `main`. Names can't be spotted by a pattern, so the maintainer also runs it
  with their own private word list.
- [ ] **The release notes and the zip pass the privacy check too.** They are
  made outside the project's tracked files, so the check on the project never
  sees them: the notes file, `INSTALL.txt`, `NOTICE.txt` and every file in the
  unzipped download are checked for the same things
  (`tools/privacy_check.py --path`).
- [ ] **The Checks run on GitHub is green on the exact commit being
  released,** on both Windows and Linux: the privacy check, the license check
  (`tools/license_check.py`) and the four car builds GitHub can do, with
  their design check.
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

GitHub builds only the four cars that need no setup step, because iRacing's
templates can't be published. The other six (FIA F4, Ray FF1600, HPD
ARX-01c, Spec Racer Ford, Skip Barber Formula 2000 and Aston Martin Vantage
GT3 EVO) are checked before every release on a computer that has the
templates, with the command below, which builds all ten.

Those six need their one-time setup step first
(`python tools/first_run.py <car> <template.zip>`; see
[`REGENERATING-GEOMETRY.md`](REGENERATING-GEOMETRY.md)). Then, with the exact
Pillow and numpy versions the paints were made with
(`tools/requirements-checks.txt`), run:

```
python tools/check_builds.py --all
```

It builds every car with its default settings in a fresh Python, checks that
each build writes exactly `car_CUSTOMERID.tga` and `car_spec_CUSTOMERID.tga`,
and compares both with the same files in that car's folder in `paints/` by
SHA-256 hash. Every car must say MATCH. With `--all`, a car whose setup step
hasn't been run is a failure, not skipped. If a car differs, find out why
before going on; if its paint was meant to change, update `paints/` in the
same change.

Then it does the design check: it builds every car again with each sample
design in `examples/designs/`. `example-scheme.json` must make exactly the
same files as the default build, and every other sample must build and make
a different paint; a paint that comes out unchanged means that car isn't
reading the design. Every sample on every car must say OK.

### 3. Run the privacy check

```
python tools/privacy_check.py --history
```

It checks every file, and every commit, tag and older file version in the
history. It must end with "nothing private found". Findings the maintainer
has already looked at and accepted are listed in
`tools/privacy-accepted.txt` and counted, not reported; never add a line to
that file yourself.

The maintainer also runs it with their own private word list: names, IDs and
computer names that no pattern can know. That list lives only on their
computer (`profiles/private-words.txt`, which git ignores, or any file given
with `--words <file>`), and the check never prints a word from it in full.
The maintainer's public GitHub identity, which every commit carries, goes in
the same list as one line, `public: <name> <<email>>`, exactly as git shows
it; private words are then not reported in a commit or tag made by that
identity, while every other author, committer and tagger is still checked.
Report what you changed and wait for the maintainer's result before going
further.

### 4. Write the change log entry and release notes

Add the new version at the top of [`CHANGELOG.md`](../CHANGELOG.md): what is
new or fixed and why it matters to the reader, then any known issues, and
commit it to `main`. Write the release notes in a file that is never
committed, for example `out/release/notes-vX.Y.Z.md` (git ignores the `out`
folder, so it's never committed), in this order:

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
run the privacy check on the release notes and the unzipped folder:

```
python tools/privacy_check.py --path out/release/notes-vX.Y.Z.md --path out/release/unzip-check
```

It must end with "nothing private found". Ask the maintainer to run the same
command with their private word list too, and wait for the result. Don't
build a source zip: GitHub attaches one to every release automatically. Never
commit the zip.

### 6. Create a draft release

The commit you release is the one on `main` with the change log entry from
step 4. Push `main`, then wait for that commit's **Checks** run on GitHub to
finish. It must be green, on both Windows and Linux, for that exact commit:

```
gh run list --workflow checks.yml --commit <full commit hash>
```

Only then make the draft. Use that full commit hash as the target, not the
branch name. A draft's tag is only created when it's published, so with
`main` as the target the tag would land on whatever `main` is by then.

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

If the date in the change log entry isn't today's, fix it first: commit the
fix, push `main`, wait for a green **Checks** run on the new commit (as in
step 6), and point the draft at it:

```
gh release edit vX.Y.Z --target <new full commit hash>
```

Then publish:

```
gh release edit vX.Y.Z --draft=false
```

Confirm the tag exists and points at the commit hash the draft targets:

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
