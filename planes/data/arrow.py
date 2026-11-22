from planes.models import arrow
from planes.spec import Spec

from ._arrow_stabilizers import ARROW_STABILIZERS
from ._texts import ARROW_TIPS, GOES_FAR

PLANE = Spec(
    slug="arrow",
    order=10,
    title="ARROW",
    sub="A heavy-nosed dart made for distance, with wing-tip stabilizers and an "
    "optional fin.",
    badges=GOES_FAR,
    tips=ARROW_TIPS,
    model=arrow,
    stabilizers=ARROW_STABILIZERS,
)
