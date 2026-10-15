"""The documentation is plain Markdown, so nothing else catches a broken relative link."""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
PAGES = [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md"))]
LINK = re.compile(r"\]\(([^)\s]+)\)")


def relative_links(page: Path) -> list[str]:
    targets = (match.group(1).split("#")[0] for match in LINK.finditer(page.read_text("utf-8")))
    return [target for target in targets if target and "://" not in target]


@pytest.mark.parametrize("page", PAGES, ids=lambda page: page.relative_to(ROOT).as_posix())
def test_relative_links_point_to_existing_files(page):
    missing = [link for link in relative_links(page) if not (page.parent / link).exists()]

    assert missing == []
