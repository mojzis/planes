from planes.models import albatross
from planes.spec import CUT_NOTE, Flaps, Spec, Stabilizers

PLANE = Spec(
    slug="albatross",
    order=50,
    title="ALBATROSS",
    sub="A wide, long-winged glider with stabilizers and trim flaps.",
    badges=("Glides far", "Medium", "Scissors for 4 small cuts"),
    tips="<b>Throw</b> gently and level, let it go rather than throw it. Launch from "
    "high up for the longest glides. <b>Dives?</b> Bend the flaps up more. "
    "<b>Stalls (swoops up and drops)?</b> Flatten the flaps. <b>Turns left?</b> "
    "Bend the right flap up a bit more, and the other way round.",
    model=albatross,
    open_text="Open the wings flat.",
    dihedral=4,
    stabilizers=Stabilizers(
        size=25,
        text="<b>Stabilizers:</b> bend the last 2.5 cm of each wing tip straight up.",
        own_panel=False,
        sheet_from=80,
    ),
    flaps=Flaps(
        35,
        65,
        20,
        "With a grown-up, cut 2 slits 2 cm long, 3 cm apart, into the back of "
        "each wing. Bend the flaps up a little.",
    ),
    finish_view=(125, 30),
    sheet_note=CUT_NOTE,
)
