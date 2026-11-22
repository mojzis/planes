from planes.models import arrow, dart
from planes.spec import Series, SeriesPlane

SERIES = Series(
    slug="lab",
    file="arrow-lab",
    order=10,
    title="ARROW LAB",
    intro="Four paper planes that are almost the same. Each one changes "
    "<b>one thing</b>, so you can find out what makes a plane fly far.",
    description="Four almost identical paper planes, each changing one thing: find "
    "out what makes a plane fly far.",
    teaser_title="Be a plane scientist",
    teaser="Four almost identical planes, each changing one thing: wing size, nose "
    "weight. Guess, fly, compare, with a score card to fill in.",
    howto="<b>How to be a plane scientist</b><ol>"
    "<li>Fold plane A first, then B, C and D. Write the letter on each.</li>"
    "<li>Before you throw, <b>guess</b>: which will fly farthest? Write it down.</li>"
    "<li>Throw each plane 3 times from the same spot, the same way. Count your steps "
    "to where it lands.</li>"
    "<li>Then try the experiments on the score card: change one thing, throw again, "
    "compare.</li>"
    "<li>Was your guess right? Why do you think so?</li></ol>",
    found="<b>What scientists found</b> (read it after testing!)<br>Bigger wings hold "
    "the plane up longer but slow it down. Small wings are fast but drop sooner. "
    "Weight in the nose keeps the plane pointing forward; too much makes it dive. "
    "Stabilizers (bent-up wing tips) stop it swerving. Bending the back edges up "
    "lifts the nose.",
    tips="<b>Fair test:</b> same thrower, same spot, same strength. Throw each plane 3 "
    "times and count steps to where it lands. Then try the experiments on the score "
    "card.",
    experiments=(
        "Paper clip on the nose",
        "Stabilizers: wing tips bent up 1 cm",
        "Back edges bent UP 3 mm",
        "Back edges bent DOWN 3 mm",
        "Wings in a V (tips a bit higher)",
        "Your own idea:",
    ),
    planes=(
        SeriesPlane(
            slug="lab-a-base",
            letter="A",
            title="BASE DART",
            sub="The plane we compare everything with. Fold it first.",
            changed="Nothing: this is the base. Wings folded 1.6 cm from the middle.",
            guess="How many steps far will it fly? Write your guess on the score card.",
            model=lambda: dart(16),
        ),
        SeriesPlane(
            slug="lab-b-big-wings",
            letter="B",
            title="BIG WINGS",
            sub="Same as the base dart, but the wings are folded only 0.8 cm from the "
            "middle.",
            changed="Bigger wings, smaller body.",
            guess="Will big wings fly farther, or float longer, or wobble more?",
            model=lambda: dart(8),
        ),
        SeriesPlane(
            slug="lab-c-small-wings",
            letter="C",
            title="SMALL WINGS",
            sub="Same as the base dart, but the wings are folded 3 cm from the middle.",
            changed="Smaller wings, deeper body.",
            guess="Will small wings go faster? Farther? Will it dive?",
            model=lambda: dart(30),
        ),
        SeriesPlane(
            slug="lab-d-heavy-nose",
            letter="D",
            title="HEAVY NOSE",
            sub="The front is folded down and in twice, so the nose has many layers "
            "of paper.",
            changed="Lots more paper in the nose (the wing shape changes a little "
            "too).",
            guess="Does a heavy nose fly farther, or does it dive?",
            model=lambda: arrow(beak=False),
        ),
    ),
)
