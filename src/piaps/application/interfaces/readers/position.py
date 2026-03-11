from abc import abstractmethod
from enum import StrEnum
from typing import Protocol

from piaps.application.common.query.filter import Filter
from piaps.application.common.query.pagination import (
    DEFAULT_PAGINATION,
    Pagination,
    PaginationResult,
)
from piaps.application.common.query.sort import Sort
from piaps.domain.entities.position import Position, PositionId
from piaps.domain.value_objects.code import Code
from piaps.domain.value_objects.name import Name


class PositionFilterField(StrEnum):
    CODE = "code"
    NAME = "name"
    BASE_SALARY = "base_salary"


class PositionSortField(StrEnum):
    CODE = "code"
    NAME = "name"
    BASE_SALARY = "base_salary"


class IPositionReader(Protocol):
    @abstractmethod
    async def find_by_id(self, id: PositionId) -> Position | None: ...

    @abstractmethod
    async def find_by_code(self, code: Code) -> Position | None: ...

    @abstractmethod
    async def find_by_name(self, name: Name) -> Position | None: ...

    @abstractmethod
    async def search(
        self,
        filter: Filter[PositionFilterField] | None = None,
        sort: Sort[PositionSortField] | None = None,
        pagination: Pagination | None = DEFAULT_PAGINATION,
    ) -> PaginationResult[Position]: ...
