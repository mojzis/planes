"""What a plane file says: the words, the fold model and a few finishing choices.

A plane is one file in ``planes/data/`` that sets ``PLANE = Spec(...)``; a series of
planes (like the Arrow lab) sets ``SERIES = Series(...)``. Everything else (steps
pages, 3D views, line sheet, PDFs, web page) is generated from it by
``planes.build``.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

Model = Callable[[], dict[str, Any]]

LAYERS_NOTE = "Some later folds go through layers: follow the steps pages."
CUT_NOTE = "Cut the black lines with a grown-up."


@dataclass(frozen=True)
class Stabilizers:
    """Wing tips bent straight up at the back.

    ``size`` is how far in from the wing tip they are bent, in mm. With
    ``own_panel`` they get a step of their own (with two 3D views); otherwise their
    text joins the "open the wings" step. ``sheet_from`` is the y (mm) where their
    bend line starts on the line sheet and the top views; ``None`` leaves it off.
    """

    size: float
    text: str
    own_panel: bool = True
    sheet_from: float | None = None


@dataclass(frozen=True)
class Flaps:
    """Two trim flaps cut into the back of each wing: slits at ``x0`` and ``x1`` mm
    from the body, ``depth`` mm long."""

    x0: float
    x1: float
    depth: float
    text: str


@dataclass(frozen=True)
class Spec:
    """One plane. ``model`` returns the fold model (see ``planes.models``).

    Wing planes (the model returns a ``hinge``) get the "open the wings" step,
    stabilizers and flaps from the fields below. Any other plane passes ``finish``:
    a function of the model that returns its closing panels and finished picture.
    """

    slug: str
    title: str
    sub: str
    badges: tuple[str, ...]
    tips: str
    model: Model
    order: int = 100
    open_text: str = (
        "Open the wings so they are flat or in a very shallow V. Pinch the body "
        "together under the wings."
    )
    dihedral: float = 6
    stabilizers: Stabilizers | None = None
    flaps: Flaps | None = None
    finish_view: tuple[float, float] = (120, 32)
    sheet_note: str = LAYERS_NOTE
    flat_height: float = 210
    finish: Callable[[dict[str, Any]], tuple[list[Any], str]] | None = None
    box: str | None = None  # extra HTML box under the title (series planes)
    series: str | None = None  # slug of the series the plane belongs to


@dataclass(frozen=True)
class SeriesPlane:
    """One plane of a series: what is different about it."""

    slug: str
    letter: str
    title: str
    sub: str
    changed: str
    guess: str
    model: Model


@dataclass(frozen=True)
class Series:
    """Planes that differ in one thing each, with an intro and a score card.

    The series gets a page at ``<slug>/``, a PDF with everything
    (``<slug>/<file>.pdf``) and a score card (``<slug>/<file>-score-card.pdf``).
    """

    slug: str
    file: str
    title: str
    intro: str
    howto: str
    found: str
    teaser: str
    teaser_title: str
    description: str
    tips: str
    experiments: tuple[str, ...]
    planes: tuple[SeriesPlane, ...]
    order: int = 100
    badges: tuple[str, ...] = ("Change one thing", "No scissors")
    dihedral: float = 4

    @property
    def name(self) -> str:
        """The title in normal case."""
        return self.title.capitalize()

    @property
    def pdf(self) -> str:
        """Site path of the whole-series PDF."""
        return f"{self.slug}/{self.file}.pdf"

    @property
    def score_pdf(self) -> str:
        """Site path of the score card PDF."""
        return f"{self.slug}/{self.file}-score-card.pdf"

    def specs(self) -> list[Spec]:
        """A ``Spec`` for each plane of the series."""
        return [
            Spec(
                slug=p.slug,
                title=f"{self.title} {p.letter}: {p.title}",
                sub=p.sub,
                badges=(f"Plane {p.letter}", *self.badges),
                tips=self.tips,
                model=p.model,
                open_text=f"Open the wings flat. Write <b>{p.letter}</b> on both "
                "wings so you know which plane is which.",
                dihedral=self.dihedral,
                box=f"<div><b>What changed:</b> {p.changed}</div>"
                f"<div><b>Guess first:</b> {p.guess}</div>",
                series=self.slug,
            )
            for p in self.planes
        ]
