# 0002 Site lives at the repo root

Date: 2026-11-23 (was 2026-11-22: site in `site/`)
Status: accepted

## Context

deedum drops the modules an App imported from under the site root after loading it,
so a rebuild reads fresh code. It used to drop packages from `.venv` too, so numpy
(via shapely) failed to load again ("cannot load module more than once per process"),
and the site lived in `site/` to keep `.venv` outside its root. deedum now leaves
installed packages alone ([mojzis/deedum#2](https://github.com/mojzis/deedum/issues/2),
fixed in mojzis/deedum#3).

## Decision

The repo root is the site: config in `[tool.deedum]` of `pyproject.toml`, the App in
`site_app.py`, plus `templates/`, `static/` and `icon.svg`. Output goes to `_site/`.

## Consequences

- `poe site` / `poe serve` need no `--config`.
- `planes/` is under the site root, so `deedum serve` re-reads it on every rebuild.
