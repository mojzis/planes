"""All planes and series, found in ``planes/data/`` and built from their files."""

import importlib
import pkgutil
from functools import cache

from . import data
from .build import Panel, Plane, build
from .spec import Series, Spec

__all__ = ["Panel", "Plane", "Series", "plane", "planes", "series", "series_planes"]


@cache
def _files() -> tuple[dict[str, Spec], list[Series]]:
    specs: list[Spec] = []
    found: list[Series] = []
    for info in pkgutil.iter_modules(data.__path__):
        if info.name.startswith("_"):
            continue
        mod = importlib.import_module(f"{data.__name__}.{info.name}")
        if spec := getattr(mod, "PLANE", None):
            specs.append(spec)
        if s := getattr(mod, "SERIES", None):
            found.append(s)
    found.sort(key=lambda s: (s.order, s.slug))
    specs.sort(key=lambda s: (s.order, s.slug))
    specs += [sp for s in found for sp in s.specs()]
    by_slug = {sp.slug: sp for sp in specs}
    if len(by_slug) != len(specs):
        msg = "two plane files use the same slug"
        raise ValueError(msg)
    return by_slug, found


@cache
def plane(slug: str) -> Plane:
    """Build one plane by its slug."""
    specs = _files()[0]
    if slug not in specs:
        msg = f"unknown plane {slug!r}; known: {', '.join(specs)}"
        raise KeyError(msg)
    return build(specs[slug])


def planes() -> list[Plane]:
    """The catalogue planes, in order (planes of a series are listed with it)."""
    return [plane(s) for s, sp in _files()[0].items() if sp.series is None]


def series() -> list[Series]:
    """Every series of planes, in order."""
    return _files()[1]


def series_planes(s: Series) -> list[Plane]:
    """The planes of one series."""
    return [plane(p.slug) for p in s.planes]
