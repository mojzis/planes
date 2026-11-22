import pytest

from planes.catalogue import LAB_ORDER, ORDER, lab_planes, plane, planes
from planes.printing import (
    PER_PAGE,
    all_sheets_document,
    card_document,
    card_path,
    lab_document,
    panel_html,
    score_card_page,
    sheet_document,
    steps_document,
)


@pytest.mark.parametrize("slug", ORDER + LAB_ORDER)
def test_steps_are_numbered_in_order(slug):
    numbers = [p.n for p in plane(slug).panels if p.n is not None]
    assert numbers == list(range(1, len(numbers) + 1))


@pytest.mark.parametrize("slug", ORDER + LAB_ORDER)
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


def test_lab_planes_are_kept_off_the_main_list():
    assert [p.slug for p in planes()] == ORDER
    assert [p.slug for p in lab_planes()] == LAB_ORDER
    assert all(p.lab for p in lab_planes())


def test_lab_wings_differ_only_in_size():
    titles = [p.title for p in lab_planes()]
    assert titles[0] == "ARROW LAB A: BASE DART"
    assert "1.6 cm" in plane("lab-a-base").panels[4].text


def test_lab_document_has_intro_every_plane_and_score_card():
    lab = lab_planes()
    doc = lab_document(lab)
    assert doc.count('class="page lines"') == len(lab)
    assert doc.count("SCORE CARD") == 1
    for p in lab:
        assert p.title in doc


def test_score_card_lists_each_plane():
    card = score_card_page(lab_planes())
    for letter in "ABCD":
        assert f"<b>{letter}</b>" in card
