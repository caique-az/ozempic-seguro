import pytest

from ozempic_seguro.application.pagination import Page, offset_for


@pytest.mark.parametrize(
    ("total", "per_page", "pages"),
    [(0, 10, 1), (1, 10, 1), (10, 10, 1), (11, 10, 2), (95, 20, 5)],
)
def test_total_pages(total, per_page, pages):
    assert Page([], total, 1, per_page).total_pages == pages


def test_navigation_flags():
    first, middle, last = (Page([], 30, page, 10) for page in (1, 2, 3))

    assert (first.has_previous, first.has_next) == (False, True)
    assert (middle.has_previous, middle.has_next) == (True, True)
    assert (last.has_previous, last.has_next) == (True, False)


def test_offset_for():
    assert offset_for(1, 20) == 0
    assert offset_for(3, 20) == 40


@pytest.mark.parametrize(("page", "per_page"), [(0, 10), (1, 0)])
def test_offset_rejects_non_positive_values(page, per_page):
    with pytest.raises(ValueError, match="positive"):
        offset_for(page, per_page)
