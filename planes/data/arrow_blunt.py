from planes.models import arrow_blunt
from planes.spec import Spec

from ._arrow_stabilizers import ARROW_STABILIZERS
from ._texts import ARROW_TIPS, GOES_FAR

PLANE = Spec(
    slug="arrow-blunt",
    order=30,
    title="ARROW BLUNT",
    sub="The heavy Arrow with its point folded back: safer indoors, still fast.",
    badges=GOES_FAR,
    tips=ARROW_TIPS,
    model=arrow_blunt,
    stabilizers=ARROW_STABILIZERS,
)
