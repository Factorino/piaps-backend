from abc import abstractmethod
from enum import StrEnum
from typing import Protocol

from piaps.application.common.dto.query.filter import Filter
from piaps.application.common.dto.query.pagination import (
    DEFAULT_PAGINATION,
    Pagination,
    PaginationResult,
)
from piaps.application.common.dto.query.sort import Sort
from piaps.domain.entities.department import Department, DepartmentId
from piaps.domain.value_objects.code import Code
from piaps.domain.value_objects.name import Name


class DepartmentFilterField(StrEnum):
    CODE = "code"
    NAME = "name"


class DepartmentSortField(StrEnum):
    CODE = "code"
    NAME = "name"


class IDepartmentReader(Protocol):
    @abstractmethod
    async def find_by_id(self, id: DepartmentId) -> Department | None: ...

    @abstractmethod
    async def find_by_code(self, code: Code) -> Department | None: ...

    @abstractmethod
    async def find_by_name(self, name: Name) -> Department | None: ...

    @abstractmethod
    async def search(
        self,
        filter: Filter[DepartmentFilterField] | None = None,
        sort: Sort[DepartmentSortField] | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
    ) -> PaginationResult[Department]: ...
