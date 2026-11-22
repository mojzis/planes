from planes.models import arrow_lock
from planes.spec import Spec

from ._arrow_stabilizers import ARROW_STABILIZERS
from ._texts import ARROW_TIPS, GOES_FAR

PLANE = Spec(
    slug="arrow-lock",
    order=20,
    title="ARROW LOCK",
    sub="An Arrow with a blunt nose held by a lock flap. Tough, and it flies far "
    "and straight.",
    badges=GOES_FAR,
    tips=ARROW_TIPS,
    model=arrow_lock,
    stabilizers=ARROW_STABILIZERS,
)
