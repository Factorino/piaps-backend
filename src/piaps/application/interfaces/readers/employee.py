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
from piaps.domain.entities.department import DepartmentId
from piaps.domain.entities.employee import Employee, EmployeeId
from piaps.domain.entities.position import PositionId
from piaps.domain.value_objects.code import Code


class EmployeeFilterField(StrEnum):
    CODE = "code"
    FULL_NAME = "full_name"
    HIRE_DATE = "hire_date"
    POSITION_ID = "position_id"
    DEPARTMENT_ID = "department_id"


class EmployeeSortField(StrEnum):
    CODE = "code"
    FULL_NAME = "full_name"
    HIRE_DATE = "hire_date"


class IEmployeeReader(Protocol):
    @abstractmethod
    async def find_by_id(self, id: EmployeeId) -> Employee | None: ...

    @abstractmethod
    async def find_by_code(self, code: Code) -> Employee | None: ...

    @abstractmethod
    async def search(
        self,
        filter: Filter[EmployeeFilterField] | None = None,
        sort: Sort[EmployeeSortField] | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
    ) -> PaginationResult[Employee]: ...

    @abstractmethod
    async def search_by_department(
        self,
        department_id: DepartmentId,
        sort: Sort[EmployeeSortField] | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
    ) -> PaginationResult[Employee]: ...

    @abstractmethod
    async def search_by_position(
        self,
        position_id: PositionId,
        sort: Sort[EmployeeSortField] | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
    ) -> PaginationResult[Employee]: ...
