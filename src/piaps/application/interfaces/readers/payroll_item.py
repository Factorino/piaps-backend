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
from piaps.domain.entities.payroll_item import PayrollItem, PayrollItemId
from piaps.domain.enums.payroll_calculation_type import PayrollCalculationType
from piaps.domain.enums.payroll_item_type import PayrollItemType
from piaps.domain.value_objects.code import Code


class PayrollItemFilterField(StrEnum):
    CODE = "code"
    NAME = "name"
    PAYROLL_TYPE = "payroll_type"
    CALC_TYPE = "calc_type"


class PayrollItemSortField(StrEnum):
    CODE = "code"
    NAME = "name"
    PAYROLL_TYPE = "payroll_type"
    CALC_TYPE = "calc_type"


class IPayrollItemReader(Protocol):
    @abstractmethod
    async def find_by_id(self, id: PayrollItemId) -> PayrollItem | None: ...

    @abstractmethod
    async def find_by_code(self, code: Code) -> PayrollItem | None: ...

    @abstractmethod
    async def search(
        self,
        filter: Filter[PayrollItemFilterField] | None = None,
        sort: Sort[PayrollItemSortField] | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
    ) -> PaginationResult[PayrollItem]: ...

    @abstractmethod
    async def search_by_type(
        self,
        payroll_type: PayrollItemType,
        calc_type: PayrollCalculationType | None = None,
        sort: Sort[PayrollItemSortField] | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
    ) -> PaginationResult[PayrollItem]: ...
