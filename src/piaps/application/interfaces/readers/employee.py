from abc import abstractmethod
from enum import StrEnum
from typing import Protocol
from uuid import UUID

from piaps.application.common.query.filter import Filter
from piaps.application.common.query.pagination import Pagination, PaginationResult
from piaps.application.common.query.sort import Sort
from piaps.domain.entities.employee import Employee
from piaps.domain.value_objects.code import Code


class EmployeeFilterField(StrEnum):
    ID = "id"
    CODE = "code"
    FULL_NAME = "full_name"
    HIRE_DATE = "hire_date"
    POSITION_ID = "position_id"
    DEPARTMENT_ID = "department_id"


class EmployeeSortField(StrEnum):
    ID = "id"
    CODE = "code"
    FULL_NAME = "full_name"
    HIRE_DATE = "hire_date"


class IEmployeeReader(Protocol):
    @abstractmethod
    async def find_by_id(self, id: UUID) -> Employee | None: ...

    @abstractmethod
    async def find_by_code(self, code: Code) -> Employee | None: ...

    @abstractmethod
    async def find_all(
        self,
        filter: Filter[EmployeeFilterField] | None = None,
        sort: Sort[EmployeeSortField] | None = None,
        pagination: Pagination | None = None,
    ) -> PaginationResult[Employee]: ...
