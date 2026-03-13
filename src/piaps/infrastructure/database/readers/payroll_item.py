from enum import StrEnum
from types import MappingProxyType
from typing import ClassVar

from sqlalchemy.orm import InstrumentedAttribute

from piaps.application.common.dto.query.filter import Filter
from piaps.application.common.dto.query.pagination import (
    DEFAULT_PAGINATION,
    Pagination,
    PaginationResult,
)
from piaps.application.common.dto.query.sort import Sort
from piaps.application.interfaces.readers.payroll_item import (
    PayrollItemFilterField,
    PayrollItemSortField,
)
from piaps.domain.entities.payroll_item import PayrollItem, PayrollItemId
from piaps.domain.value_objects.code import Code
from piaps.domain.value_objects.name import Name
from piaps.infrastructure.database.models.payroll_item import PayrollItemORM
from piaps.infrastructure.database.readers.base import SAAbstractReader


class SAPayrollItemReader(SAAbstractReader[PayrollItem, PayrollItemORM]):
    _model = PayrollItemORM

    _filter_map: ClassVar[MappingProxyType[StrEnum, InstrumentedAttribute]] = MappingProxyType(
        {
            PayrollItemFilterField.CODE: PayrollItemORM.code,
            PayrollItemFilterField.NAME: PayrollItemORM.name,
            PayrollItemFilterField.PAYROLL_TYPE: PayrollItemORM.payroll_type,
            PayrollItemFilterField.CALC_TYPE: PayrollItemORM.calc_type,
        }
    )

    _sort_map: ClassVar[MappingProxyType[StrEnum, InstrumentedAttribute]] = MappingProxyType(
        {
            PayrollItemSortField.CODE: PayrollItemORM.code,
            PayrollItemSortField.NAME: PayrollItemORM.name,
            PayrollItemSortField.PAYROLL_TYPE: PayrollItemORM.payroll_type,
            PayrollItemSortField.CALC_TYPE: PayrollItemORM.calc_type,
        }
    )

    async def find_by_id(self, id: PayrollItemId) -> PayrollItem | None:
        return await self._find(PayrollItemORM.id == id)

    async def find_by_code(self, code: Code) -> PayrollItem | None:
        return await self._find(PayrollItemORM.code == code.value)

    async def find_by_name(self, name: Name) -> PayrollItem | None:
        return await self._find(PayrollItemORM.name == name.value)

    async def search(
        self,
        filter: Filter[PayrollItemFilterField] | None = None,
        sort: Sort[PayrollItemSortField] | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
    ) -> PaginationResult[PayrollItem]:
        return await self._search(filter, sort, pagination)

    def _to_domain(self, orm_obj: PayrollItemORM) -> PayrollItem:
        raise NotImplementedError  # TODO: adaptix converter
