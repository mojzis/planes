from dataclasses import replace

from planes.models import arrow_lock
from planes.spec import CUT_NOTE, Flaps, Spec

from ._arrow_stabilizers import ARROW_STABILIZERS
from ._texts import FLAP_TIPS

PLANE = Spec(
    slug="stingray",
    order=40,
    title="STINGRAY",
    sub="A wide, slow glider with a locked blunt nose, stabilizers and trim flaps.",
    badges=("Floats far", "Medium", "Scissors for 4 small cuts"),
    tips="<b>Throw</b> gently and level, like letting go of a bird. "
    + FLAP_TIPS
    + " Keep the stabilizers equal and straight up.",
    model=lambda: arrow_lock(22),
    stabilizers=replace(ARROW_STABILIZERS, sheet_from=235),
    flaps=Flaps(
        30,
        52,
        18,
        "With a grown-up, cut 2 slits 1.8 cm long, 2 cm apart, into the back of "
        "each wing. Bend the flaps up a little.",
    ),
    sheet_note=CUT_NOTE,
)
