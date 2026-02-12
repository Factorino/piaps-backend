from abc import abstractmethod
from enum import StrEnum
from typing import Protocol
from uuid import UUID

from piaps.application.common.query.filter import Filter
from piaps.application.common.query.pagination import Pagination, PaginationResult
from piaps.application.common.query.sort import Sort
from piaps.domain.entities.position import Position
from piaps.domain.value_objects.code import Code


class PositionFilterField(StrEnum):
    ID = "id"
    CODE = "code"
    NAME = "name"


class PositionSortField(StrEnum):
    ID = "id"
    CODE = "code"
    NAME = "name"


class IPositionReader(Protocol):
    @abstractmethod
    async def find_by_id(self, id: UUID) -> Position | None: ...

    @abstractmethod
    async def find_by_code(self, code: Code) -> Position | None: ...

    @abstractmethod
    async def search(
        self,
        filter: Filter[PositionFilterField] | None = None,
        sort: Sort[PositionSortField] | None = None,
        pagination: Pagination | None = None,
    ) -> PaginationResult[Position]: ...
