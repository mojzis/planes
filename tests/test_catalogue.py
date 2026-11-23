import pytest

from planes.build import build
from planes.catalogue import plane, planes, series, series_planes
from planes.models import dart
from planes.printing import (
    PER_PAGE,
    all_sheets_document,
    card_document,
    card_path,
    panel_html,
    score_card_page,
    series_document,
    sheet_document,
    steps_document,
)
from planes.spec import Flaps, Spec, Stabilizers

ORDER = ["arrow", "arrow-lock", "arrow-blunt", "stingray", "albatross", "tube"]
LAB = ["lab-a-base", "lab-b-big-wings", "lab-c-small-wings", "lab-d-heavy-nose"]


def lab():
    return series()[0]


@pytest.mark.parametrize("slug", ORDER + LAB)
def test_steps_are_numbered_in_order(slug):
    numbers = [p.n for p in plane(slug).panels if p.n is not None]
    assert numbers == list(range(1, len(numbers) + 1))


@pytest.mark.parametrize("slug", ORDER + LAB)
def test_line_sheet_has_creases_and_a_footer(slug):
    sheet = plane(slug).line_sheet
    assert sheet.count("<line ") >= 3
    assert f"{plane(slug).title}: fold with this side up." in sheet


def test_landscape_sheets_are_rotated_onto_the_page():
    assert "rotate(90)" in plane("albatross").line_sheet
    assert "rotate(90)" not in plane("arrow").line_sheet


def test_only_scissor_planes_have_cut_lines():
    cuts = {p.slug for p in planes() if 'stroke="#212529"' in p.line_sheet}
    assert cuts == {p.slug for p in planes() if p.scissors} == {"stingray", "albatross"}


def test_arrow_beak_is_optional_and_left_off_the_line_sheet():
    arrow = plane("arrow")
    assert [p.n for p in arrow.panels if p.optional] == [7]
    assert "opt-tag" in panel_html(arrow.panels[6])
    assert ">7</text>" not in arrow.line_sheet


def test_unknown_plane_names_the_known_ones():
    with pytest.raises(KeyError, match="arrow-lock"):
        plane("concorde")


def test_steps_document_splits_panels_into_pages():
    stingray = plane("stingray")
    doc = steps_document(stingray)
    pages = -(-(len(stingray.panels) + 1) // PER_PAGE)
    assert doc.count('class="page inst"') == pages
    assert doc.count(f"/ {pages}</span>") == pages
    assert stingray.tips in doc


def test_sheet_document_is_one_page():
    assert sheet_document(plane("tube")).count('class="page') == 1


def test_all_sheets_document_has_one_page_per_plane():
    doc = all_sheets_document(planes())
    assert doc.count('class="page lines"') == len(ORDER)


def test_social_card_shows_the_title_and_each_picture():
    doc = card_document("Stingray", ["<svg>a</svg>", "<svg>b</svg>"])
    assert "<h1>Stingray</h1>" in doc
    assert doc.count("<svg>") == 2


def test_home_card_sits_at_the_site_root():
    assert [card_path(""), card_path("tube")] == ["social.png", "tube/social.png"]


def test_plane_files_are_found_in_order():
    assert [p.slug for p in planes()] == ORDER
    assert [s.slug for s in series()] == ["lab"]
    assert [p.slug for p in series_planes(lab())] == LAB


def test_series_planes_get_the_series_box_and_badges():
    a = plane("lab-a-base")
    assert a.title == "ARROW LAB A: BASE DART"
    assert a.series == "lab"
    assert a.badges[0] == "Plane A"
    assert "What changed:" in (a.box or "")
    assert "Write <b>A</b>" in a.panels[-1].text
    assert "1.6 cm" in a.panels[4].text


def test_stabilizers_get_their_own_step_or_join_the_open_step():
    assert plane("arrow").panels[-1].text.startswith("<b>Stabilizers:</b>")
    assert "<b>Stabilizers:</b>" in plane("albatross").panels[-2].text


def test_series_document_has_intro_every_plane_and_score_card():
    planes_ = series_planes(lab())
    doc = series_document(lab())
    assert doc.count('class="page lines"') == len(planes_)
    assert doc.count("SCORE CARD") == 1
    for p in planes_:
        assert p.title in doc


def test_score_card_lists_each_plane():
    card = score_card_page(lab())
    assert "1. The four planes" in card
    for letter in "ABCD":
        assert f"<b>{letter}</b>" in card


def test_a_new_plane_needs_only_a_spec():
    p = build(
        Spec(
            slug="test-dart",
            title="TEST DART",
            sub="A test.",
            badges=("Test",),
            tips="Throw it.",
            model=lambda: dart(20),
            stabilizers=Stabilizers(10, "Bend the tips up.", sheet_from=250),
            flaps=Flaps(20, 40, 15, "Cut two slits."),
        )
    )
    assert [x.n for x in p.panels] == [1, 2, 3, 4, 5, 6, 7, 8]
    assert p.scissors
    assert 'stroke="#212529"' in p.line_sheet
