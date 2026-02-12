from abc import abstractmethod
from enum import StrEnum
from typing import Protocol
from uuid import UUID

from piaps.application.common.query.filter import Filter
from piaps.application.common.query.pagination import Pagination, PaginationResult
from piaps.application.common.query.sort import Sort
from piaps.domain.entities.salary_item import SalaryItem
from piaps.domain.value_objects.code import Code


class SalaryItemFilterField(StrEnum):
    ID = "id"
    CODE = "code"
    NAME = "name"
    ITEM_TYPE = "item_type"
    CALC_TYPE = "calc_type"


class SalaryItemSortField(StrEnum):
    ID = "id"
    CODE = "code"
    NAME = "name"
    ITEM_TYPE = "item_type"
    CALC_TYPE = "calc_type"


class ISalaryItemReader(Protocol):
    @abstractmethod
    async def find_by_id(self, id: UUID) -> SalaryItem | None: ...

    @abstractmethod
    async def find_by_code(self, code: Code) -> SalaryItem | None: ...

    @abstractmethod
    async def find_all(
        self,
        filter: Filter[SalaryItemFilterField] | None = None,
        sort: Sort[SalaryItemSortField] | None = None,
        pagination: Pagination | None = None,
    ) -> PaginationResult[SalaryItem]: ...
