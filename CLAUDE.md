# Paper planes

Original paper planes for kids: one page per plane (steps + 3D views) and two A4 PDFs
(steps, line sheet), published with deedum to GitHub Pages. See README.md and
docs/architecture.md; decisions in docs/decisions/ (newest wins).

## Project

- `uv run poe site` — build site + PDFs into `_site/` and lint it (`deedum check`).
  PDFs need Chromium once: `uv run playwright install chromium`.
- `uv run poe serve` — live preview, `PLANES_PDF=0` (no PDFs or social images, so check reports the PDFs missing).
- The deedum site is in `site/`, not the repo root (decision 0002).
- Pictures come only from the fold model (`planes/models.py`). Never hand-draw a step.
- New plane: one file in `planes/data/` with `PLANE = Spec(...)` (fields in
  `planes/spec.py`); a new series: `SERIES = Series(...)`. Fold steps go in `models.py`
  when shared, else in the file itself. Then look at the page and both PDFs before
  committing.
- After changing a model or renderer, look at the result (screenshot the page, rasterize
  the PDF with `pdftoppm`); tests only check structure.


## Commands

- `uv run poe check` — runs `madoqua check`: the commit hook's checks on the whole repo (ruff incl. `S` security rules, ty, biston, zorilla), plus the full test suite and a non-blocking vulns scan. Configured in `[tool.madoqua]` (`full_cmd`, `when`)
- `uv run poe fix` — auto-format and fix lint issues
- `uv run poe test` — run tests only
- `uv run poe check-all` — run all checks including dead-code, single-use abstractions (dermestes) and unused-deps

## Stack

uv, ruff (lint/format), ty (type check), pytest, poethepoet (task runner)

Package lives in `planes/` (no `src/`).

## Standards

Unless told otherwise, follow [docs/standards/](docs/standards/README.md): CLI = typer + rich, web = FastAPI + htmx, plus LLM, data and testing defaults. Read the relevant file before adding a CLI, web UI, LLM call, storage or tests.

## Toolbox

The [aesop toolbox](https://mojzis.github.io/aesop/llms.txt) is wired in here. Every
tool explains itself — run `uv run <tool> guide` before reaching for flags, and
`uv run <tool> guide tune` before changing a threshold. Call them as `uv run <tool>`;
ty-find's binary is `tyf`.

### On every commit

**madoqua** is the only commit hook (`hooks/pre-commit`, `core.hooksPath=hooks`). It
acts on staged `.py`/`.pyi` files only — a commit without one is a silent no-op, not a
verified hook.

| phase | steps |
| --- | --- |
| fix (rewrites and re-stages) | `ruff check --fix`, `ruff format` |
| check (blocks) | `ruff check`, `ty check`, `biston scan --focus-args`, `zorilla check`, `gerenuk run` |

Whole hook runs in ~0.3 s on this repo (gerenuk ~0.27 s of that; `uv run madoqua stats`
for current numbers). Don't commit with `--no-verify` or `MADOQUA_SKIP` to get past a
check that is telling the truth.

Two changes from the hook this replaced:

- `ty check` was repo-wide, it is now **staged-only**. Repo-wide diagnostics no longer
  block a clean commit, but a file with existing diagnostics blocks the first commit
  that touches it. `uv run poe typecheck` still checks everything.
- **bandit is gone.** Security checks are ruff's flake8-bandit `S` rules, so they now run
  on commit via `ruff check`; `tests/**` ignores S101/S105/S106 in `per-file-ignores`.

### Every now and then

- `uv run pycoati . --format pretty` — scores every test for suspicion and prints a
  remediation ladder. Run it before a test-cleanup session. Never put it in a hook or
  CI: it runs the suite three times. It needs pytest-cov or coverage is silently null.

### On demand — instead of grep

- `uv run tyf find <symbol>` / `tyf refs` / `tyf list <file>` / `tyf calls` — type-aware
  symbol lookup. **Use these instead of grep** for definitions and references; grep
  cannot tell a definition from a string that happens to match.
- `uv run gerenuk audit <file>` — lists symbols in a module that nothing references.
- `uv run gerenuk impacted-tests` — which tests a working-tree diff reaches, and why.
- `uv run dermestes` — flags single-use abstractions your working-tree changes introduced
  (an ABC/Protocol with one implementation, a function with one caller, a parameter
  nobody varies) as deletion candidates. Run it after adding a layer of indirection;
  `uv run dermestes guide` prints triage instructions for its findings. `--all` audits
  the whole repo (`uv run poe abstractions`, also part of `check-all`).

### Fresh clone

```
uv sync
uv run madoqua install    # once; core.hooksPath is local config, not tracked
```

### Refreshing the toolbox

```
uv lock --refresh --upgrade-package madoqua --upgrade-package gerenuk --upgrade-package biston --upgrade-package zorilla --upgrade-package pycoati --upgrade-package ty-find --upgrade-package dermestes && uv sync
```

`--refresh` matters: without it uv may serve a cached index and miss a release
published minutes ago.

## CI

`ci.yml` runs `poe check`; `pages.yml` builds and deploys the site.

## Actions versions

When starting a new project from this template, set up a GitHub Actions CI pipeline
(`.github/workflows/ci.yml`) that runs `uv sync` and `uv run poe check` on push and pull
request.

**Use the newest version of every action.** Versions remembered from training data are
usually outdated, so look each one up before writing it:
`gh release view --repo <owner/repo>` (or the latest-release / list-tags tool from the
GitHub integration). This covers at least `actions/checkout` and `astral-sh/setup-uv`.

Then check that the tag you write exists: `gh api repos/<owner/repo>/git/ref/tags/<tag>`.
Use the major tag (`@v7`) if it exists, otherwise the full version. Not every action
publishes major tags: `setup-uv` doesn't, so `@v10` fails with "unable to find version"
and it needs e.g. `@v10.3.3`.
Use `setup-uv` to install uv and Python instead of `actions/setup-python`, and turn on its
cache. Don't copy version tags from older workflows or from memory.

## Notes

- ty is in beta — may produce false positives. Prefer `# ty: ignore[rule]` over blanket suppression.
- The commit hook auto-fixes and restages files. Only blocks on unfixable issues.
- gerenuk diffs the **working tree** against `origin/main`, so unstaged edits count, and
  any commit touching `pyproject.toml` or `uv.lock` runs the full suite. `--base HEAD`
  scopes it to the commit itself.
- ty-find's index goes stale after the hook's `ruff format` rewrites a file. The tell is
  `tyf refs <sym>` listing only the definition, or gerenuk reporting `selected` with an
  empty list. `uv run tyf daemon restart` fixes it.
