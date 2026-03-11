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
from piaps.domain.entities.payroll_item import PayrollItem, PayrollItemId
from piaps.domain.value_objects.code import Code
from piaps.domain.value_objects.name import Name


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
    async def find_by_name(self, name: Name) -> PayrollItem | None: ...

    @abstractmethod
    async def search(
        self,
        filter: Filter[PayrollItemFilterField] | None = None,
        sort: Sort[PayrollItemSortField] | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
    ) -> PaginationResult[PayrollItem]: ...
