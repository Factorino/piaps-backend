import math
from typing import ClassVar

from pydantic import computed_field

from piaps.application.common.dto.base import dto
from piaps.domain.errors.base import ValidationError


@dto
class BasePagination:
    _MIN_PAGE: ClassVar[int] = 1
    _MIN_PAGE_SIZE: ClassVar[int] = 1
    _MAX_PAGE_SIZE: ClassVar[int] = 100

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
        if self.page < self._MIN_PAGE:
            raise ValidationError(f"Page must be greater or equal {self._MIN_PAGE}")

        if self.page_size < self._MIN_PAGE_SIZE:
            raise ValidationError(f"Page size must be greater or equal {self._MIN_PAGE_SIZE}")

        if self.page_size > self._MAX_PAGE_SIZE:
            raise ValidationError(f"Page size must be less or equal {self._MAX_PAGE_SIZE}")


@dto
class Pagination(BasePagination):
    page: int = 1
    page_size: int = 25


@dto
class PaginationResultMeta(BasePagination):
    total: int

    @computed_field
    @property
    def total_pages(self) -> int:
        return math.ceil(self.total / self.page_size)

    @computed_field
    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @computed_field
    @property
    def has_prev(self) -> bool:
        return self.page > 1


@dto
class PaginationResult[DataT]:
    data: list[DataT]
    meta: PaginationResultMeta


DEFAULT_PAGINATION = Pagination()
