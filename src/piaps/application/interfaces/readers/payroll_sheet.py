from abc import abstractmethod
from datetime import date
from enum import StrEnum
from typing import Protocol

from piaps.application.common.dto.query.filter import Filter
from piaps.application.common.dto.query.pagination import (
    DEFAULT_PAGINATION,
    Pagination,
    PaginationResult,
)
from piaps.application.common.dto.query.sort import Sort
from piaps.domain.entities.employee import EmployeeId
from piaps.domain.entities.payroll_sheet import PayrollSheet, PayrollSheetId


class PayrollSheetFilterField(StrEnum):
    EMPLOYEE_ID = "employee_id"
    PERIOD = "period"
    STATUS = "status"


class PayrollSheetSortField(StrEnum):
    PERIOD = "period"
    STATUS = "status"


class IPayrollSheetReader(Protocol):
    @abstractmethod
    async def find_by_id(self, id: PayrollSheetId) -> PayrollSheet | None: ...

    @abstractmethod
    async def find_by_employee_and_period(
        self,
        employee_id: EmployeeId,
        period: date,
    ) -> PayrollSheet | None: ...

    @abstractmethod
    async def search(
        self,
        filter: Filter[PayrollSheetFilterField] | None = None,
        sort: Sort[PayrollSheetSortField] | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
    ) -> PaginationResult[PayrollSheet]: ...
