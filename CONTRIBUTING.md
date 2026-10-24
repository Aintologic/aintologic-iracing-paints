# Contributing

## What and why

Thanks for helping. This page explains how we write things here and how
changes get into the project. Most people who use this project don't code, and
many are wary of AI, so everything we publish is written to be clear, honest and
easy to skip past the technical parts.

## What "done" looks like

- Your question, problem or idea is filed as an issue using one of the issue
  forms, in plain language.
- Nothing private is in it: no iRacing customer ID, real name, folder path,
  private screenshot, or logo you don't have the rights to.
- If you offered a change, it is clear what it does and that you have the right
  to share it.

## How we write

These rules apply to every guide, issue and release note.

1. **Lead with the person.** Start with what the reader can do, not with our
   own paint scheme.
2. **Plain language first.** Open with a short, jargon-free explanation anyone
   can follow. Put technical detail in a clearly marked section below it.
3. **Keep AI instructions separate.** Anything meant for an AI agent goes under
   a heading called "For the AI agent", so people can skip it.
4. **Neutral tone.** Explain what the AI does and does not do. Never oversell.
5. **Nothing installs itself.** Tell people what they need and where to get it.
   They install it.
6. **Professional releases.** Every release gets a version number, a change log
   entry and release notes.

Issues and user-facing docs use three sections, in this order:

- **What and why**: plain English, no jargon.
- **What "done" looks like**: how we'll know it's finished.
- **For the AI agent**: technical detail and instructions.

## Reporting a problem or asking for something

Open a [new issue](https://github.com/Aintologic/aintologic-iracing-paints/issues/new/choose)
and pick a form:

- **Something isn't working**: a bug, an error, or a paint that looks wrong.
- **Request or idea**: a feature, a better explanation, or a car you'd like
  added to the measured list.

Before you post, remove your customer ID and any personal folder names from
error messages and screenshots. Replace them with something like `123456` or
`<my folder>`.

## Offering a change

This repository is published from a separate working copy, so pull requests
can't be merged here directly.

1. Open an issue first and describe the change.
2. If it's accepted, we bring the change in ourselves and credit you in the
   change log.
3. If you open a pull request anyway, we'll read it, but we'll still bring it in
   that way.

## Licensing

By offering a change, you agree it can be published under the same license as
the part of the project it belongs to:

- Code (`src/`, `tools/`): **AGPL-3.0-or-later**.
- Paints and example logos: **CC BY-NC-SA 4.0**, subject to `TRADEMARKS.md`.

Only offer work you have the right to share. Never include iRacing template
files or anything generated from them, fonts without an open license, or
third-party logos.

## For the AI agent

If you are helping someone contribute:

- Use the issue forms and keep the three sections in order.
- Write the "What and why" section for a non-technical reader.
- Strip customer IDs, real names, machine names and folder paths from anything
  you paste, including error output.
- If the change touches a car's builder, build that car before and after, and
  say in the issue what changed in the output.
- Follow `AGENTS.md` for everything else.
