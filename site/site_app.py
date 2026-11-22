"""deedum App for the planes site: a catalogue page and one page per plane.

Each plane page links two PDFs, printed in ``after_build`` along with the social
preview images. Set ``PLANES_PDF=0`` to skip them (quicker ``deedum serve``;
``deedum check`` then reports the missing links).
"""

import os
import re
from pathlib import Path
from typing import Any

import deedum
from deedum import Page
from markupsafe import Markup

from planes.catalogue import Plane, planes, series, series_planes
from planes.printing import COUNT, card_path, panel_html, write_build_files
from planes.sheets import defs, legend


def _intro(plane: Plane) -> str:
    steps = sum(1 for p in plane.panels if p.n)
    return f"{plane.sub} {steps} steps, one A4 sheet."


class PlanesApp(deedum.App):
    """Pages made from the fold model in ``planes``."""

    def __init__(self, site: deedum.Site) -> None:
        """Build every plane once; the pages and the PDFs share them."""
        super().__init__(site)
        self.planes = planes()
        self.series = {f"{s.slug}/": s for s in series()}
        grouped = [p for s in self.series.values() for p in series_planes(s)]
        self.by_url = {f"{p.slug}/": p for p in self.planes + grouped}

    def load_pages(self) -> list[Page]:
        """The catalogue, one page per plane, plus any markdown in ``content/``."""
        pages = [p for p in super().load_pages() if p.url != ""]
        pages.append(
            self.page(
                "",
                title="Paper planes",
                description="Original paper planes for kids: step-by-step pictures "
                "and printable PDFs.",
                template="home.html",
                image=card_path(""),
            )
        )
        pages.extend(
            self.page(
                url,
                title=plane.name,
                description=_intro(plane),
                template="plane.html",
                source=_markdown(plane),
                image=card_path(plane.slug),
            )
            for url, plane in self.by_url.items()
        )
        pages.extend(
            self.page(
                url,
                title=s.name,
                description=s.description,
                template="series.html",
                image=card_path(s.slug),
            )
            for url, s in self.series.items()
        )
        return pages

    def context(self, page: Page) -> dict[str, Any]:
        """``plane`` on a plane page, its pictures marked safe."""
        if s := self.series.get(page.url):
            return {
                "series": s,
                "intro": Markup(s.intro),  # noqa: S704
                "howto": Markup(s.howto),  # noqa: S704
                "found": Markup(s.found),  # noqa: S704
                "count": COUNT.get(len(s.planes), len(s.planes)),
                "series_cards": self._cards(series_planes(s)),
            }
        plane = self.by_url.get(page.url)
        if plane is None:
            return {}
        return {
            "plane": plane,
            "panels": [Markup(panel_html(p)) for p in plane.panels],  # noqa: S704
            "finished": Markup(plane.finished or ""),  # noqa: S704
            "tips": Markup(plane.tips),  # noqa: S704
            "defs": Markup(defs(plane.width, plane.height)),  # noqa: S704
            "box": Markup(plane.box or ""),  # noqa: S704
            "back": self.series.get(f"{plane.series}/"),
        }

    @staticmethod
    def _cards(group: list[Plane]) -> list[dict[str, Any]]:
        return [
            {
                "plane": p,
                "url": f"{p.slug}/",
                "picture": Markup(p.finished or ""),  # noqa: S704
            }
            for p in group
        ]

    def globals(self) -> dict[str, Any]:
        """The plane list for the catalogue and the line legend."""
        return {
            "cards": self._cards(self.planes),
            "teasers": [
                {"series": s, "picture": Markup(series_planes(s)[0].finished or "")}  # noqa: S704
                for s in self.series.values()
            ],
            "legend": Markup(legend()),  # noqa: S704
        }

    def after_build(self, out: Path) -> None:
        """Print the two PDFs of every plane and the social previews."""
        if os.environ.get("PLANES_PDF", "1") != "0":
            write_build_files(self.planes, list(self.series.values()), out)


def _plain(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def _markdown(plane: Plane) -> str:
    """Plain-text steps, for ``index.md`` and ``llms-full.txt``."""
    lines = [f"# {plane.name}", "", plane.sub, ""]
    lines += [f"{p.n or 'Done'}. {_plain(p.text)}" for p in plane.panels]
    lines += ["", _plain(plane.tips), ""]
    return "\n".join(lines)
