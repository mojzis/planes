from planes import iso
from planes.build import Panel, view
from planes.models import tube
from planes.sheets import TUBE_THROW, TUBE_TUCK
from planes.spec import Spec


def _finish(d):
    """Roll the band into a tube and tuck it; no wings to open."""

    def tube3d(frac):
        return iso.tube3d(d["m"].facets, d["w"], frac=frac)

    panels = [
        Panel(
            4,
            "Gently bend the sheet into a round tube, with the band on the inside.",
            None,
            view(tube3d(0.6), 25, 18, h=260, outline=False),
        ),
        Panel(
            5,
            "Slide one end of the band about 3 cm into the other end so the tube "
            "holds. Make it nice and round.",
            TUBE_TUCK,
            view(tube3d(1.0), 25, 18, h=190, outline=False),
        ),
        Panel(
            None,
            "<b>Throw it band first</b>: hold the back end from below and push it off "
            "forward with a little spin.",
            TUBE_THROW,
        ),
    ]
    return panels, view(tube3d(1.0), 25, 18, 600, 330, outline=False)


PLANE = Spec(
    slug="tube",
    order=60,
    title="TUBE",
    sub="Doesn't look like a plane at all, but it flies straight and far.",
    badges=("Weird & fun", "Easy", "No scissors"),
    tips="<b>Throw</b> it like a gentle dart, band first, level. Hold it underneath "
    "at the plain end. <b>Wobbles?</b> Make the tube rounder and the overlap even. "
    "<b>Drops fast?</b> Throw it a bit harder. Try: who can throw it through a hula "
    "hoop?",
    model=tube,
    flat_height=200,
    sheet_note="Fold on lines 1, 2, 3 in order.",
    finish=_finish,
)
