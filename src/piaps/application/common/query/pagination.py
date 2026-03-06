import math

from piaps.application.common.dto import dto
from piaps.domain.errors.base import ValidationError


@dto
class BasePagination:
    page: int
    page_size: int

    def __post_init__(self) -> None:
        self._validate()

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size

    def _validate(self) -> None:
        if self.page_size <= 0:
            raise ValidationError("page_size must be positive")
        if self.page <= 0:
            raise ValidationError("page must be positive")


@dto
class Pagination(BasePagination):
    page: int = 1
    page_size: int = 25


@dto
class PaginationResultMeta(BasePagination):
    total: int

    @property
    def total_pages(self) -> int:
        return math.ceil(self.total / self.page_size)

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1


@dto
class PaginationResult[DataT]:
    data: list[DataT]
    meta: PaginationResultMeta
