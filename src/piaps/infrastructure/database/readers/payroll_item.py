from enum import StrEnum
from types import MappingProxyType
from typing import ClassVar

from sqlalchemy import Result, Select, select
from sqlalchemy.orm import InstrumentedAttribute

from piaps.application.common.query.filter import Filter
from piaps.application.common.query.pagination import (
    DEFAULT_PAGINATION,
    Pagination,
    PaginationResult,
)
from piaps.application.common.query.sort import Sort
from piaps.application.interfaces.readers.payroll_item import (
    IPayrollItemReader,
    PayrollItemFilterField,
    PayrollItemSortField,
)
from piaps.domain.entities.payroll_item import PayrollItem, PayrollItemId
from piaps.domain.enums.payroll_calculation_type import PayrollCalculationType
from piaps.domain.enums.payroll_item_type import PayrollItemType
from piaps.domain.value_objects.code import Code
from piaps.infrastructure.database.models.payroll_item import PayrollItemORM
from piaps.infrastructure.database.readers.base import SAAbstractReader


class SAPayrollItemReader(IPayrollItemReader, SAAbstractReader[PayrollItem, PayrollItemORM]):
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
        query: Select[tuple[PayrollItemORM]] = select(PayrollItemORM).where(
            PayrollItemORM.id == id
        )
        result: Result[tuple[PayrollItemORM]] = await self._execute(query)
        row: PayrollItemORM | None = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def find_by_code(self, code: Code) -> PayrollItem | None:
        query: Select[tuple[PayrollItemORM]] = select(PayrollItemORM).where(
            PayrollItemORM.code == code.value
        )
        result: Result[tuple[PayrollItemORM]] = await self._execute(query)
        row: PayrollItemORM | None = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def search(
        self,
        filter: Filter[PayrollItemFilterField] | None = None,
        sort: Sort[PayrollItemSortField] | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
    ) -> PaginationResult[PayrollItem]:
        return await self._search(filter, sort, pagination)

    async def search_by_type(
        self,
        payroll_type: PayrollItemType,
        calc_type: PayrollCalculationType | None = None,
        sort: Sort[PayrollItemSortField] | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
    ) -> PaginationResult[PayrollItem]:
        base_query: Select[tuple[PayrollItemORM]] = select(PayrollItemORM).where(
            PayrollItemORM.payroll_type == payroll_type
        )
        if calc_type is not None:
            base_query = base_query.where(PayrollItemORM.calc_type == calc_type)
        return await self._search(sort=sort, pagination=pagination, base_query=base_query)

    def _to_domain(self, orm_obj: PayrollItemORM) -> PayrollItem:
        raise NotImplementedError  # TODO: adaptix converter
