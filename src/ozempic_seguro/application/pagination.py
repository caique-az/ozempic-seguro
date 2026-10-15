from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Page[T]:
    items: list[T]
    total: int
    page: int
    per_page: int

    @property
    def total_pages(self) -> int:
        return max(1, -(-self.total // self.per_page))

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        return self.page > 1


def offset_for(page: int, per_page: int) -> int:
    if page < 1 or per_page < 1:
        raise ValueError("page and per_page must be positive")
    return (page - 1) * per_page
