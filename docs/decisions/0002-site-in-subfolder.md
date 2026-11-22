# 0002 Site lives in site/

Date: 2026-11-22
Status: accepted

## Context

deedum drops every module an App imported from under the site root after loading it,
so a rebuild reads fresh code. With the site root at the repo root that includes
`.venv`, so numpy (via shapely) was dropped and failed to load again
("cannot load module more than once per process").

## Decision

The site (config, App, templates, static) lives in `site/`. It imports the installed
`planes` package; the output still goes to `_site/` at the repo root.

## Consequences

- `poe site` / `poe serve` pass `--config site/deedum.toml`.
- Can move back to the root once deedum skips virtualenvs when it forgets modules:
  [mojzis/deedum#2](https://github.com/mojzis/deedum/issues/2).
