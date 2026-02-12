from abc import abstractmethod
from enum import StrEnum
from typing import Protocol
from uuid import UUID

from piaps.application.common.query.filter import Filter
from piaps.application.common.query.pagination import Pagination, PaginationResult
from piaps.application.common.query.sort import Sort
from piaps.domain.entities.payroll import Payroll


class PayrollFilterField(StrEnum):
    ID = "id"
    EMPLOYEE_ID = "employee_id"
    PERIOD_YEAR = "period.year"
    PERIOD_MONTH = "period.month"
    STATUS = "status"
    BASE_SALARY = "base_salary"
    NET_SALARY = "net_salary"


class PayrollSortField(StrEnum):
    ID = "id"
    EMPLOYEE_ID = "employee_id"
    PERIOD_YEAR = "period.year"
    PERIOD_MONTH = "period.month"
    STATUS = "status"
    BASE_SALARY = "base_salary"
    NET_SALARY = "net_salary"


class IDepartmentReader(Protocol):
    @abstractmethod
    async def find_by_id(self, id: UUID) -> Payroll | None: ...

    @abstractmethod
    async def search(
        self,
        filter: Filter[PayrollFilterField] | None = None,
        sort: Sort[PayrollSortField] | None = None,
        pagination: Pagination | None = None,
    ) -> PaginationResult[Payroll]: ...
