from abc import abstractmethod
from enum import StrEnum
from typing import Protocol
from uuid import UUID

from piaps.application.common.query.filter import Filter
from piaps.application.common.query.pagination import Pagination, PaginationResult
from piaps.application.common.query.sort import Sort
from piaps.domain.entities.department import Department
from piaps.domain.value_objects.code import Code


class DepartmentFilterField(StrEnum):
    ID = "id"
    CODE = "code"
    NAME = "name"


class DepartmentSortField(StrEnum):
    ID = "id"
    CODE = "code"
    NAME = "name"


class IDepartmentReader(Protocol):
    @abstractmethod
    async def find_by_id(self, id: UUID) -> Department | None: ...

    @abstractmethod
    async def find_by_code(self, code: Code) -> Department | None: ...

    @abstractmethod
    async def search(
        self,
        filter: Filter[DepartmentFilterField] | None = None,
        sort: Sort[DepartmentSortField] | None = None,
        pagination: Pagination | None = None,
    ) -> PaginationResult[Department]: ...
