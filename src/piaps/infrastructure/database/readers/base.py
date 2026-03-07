from abc import ABC, abstractmethod
from collections.abc import Callable
from enum import StrEnum
from types import MappingProxyType
from typing import Any, ClassVar, Final

from sqlalchemy import Result, Select, asc, desc, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql import operators
from sqlalchemy.sql.operators import OperatorType

from piaps.application.common.query.filter import (
    Filter,
    OperatorList,
    OperatorNull,
    OperatorScalar,
    OperatorStr,
)
from piaps.application.common.query.pagination import (
    DEFAULT_PAGINATION,
    Pagination,
    PaginationResult,
    PaginationResultMeta,
)
from piaps.application.common.query.sort import Sort, SortDirection
from piaps.application.errors.base import OperationFailedError
from piaps.domain.entities.base import Entity
from piaps.infrastructure.database.models.base import BaseORM


_OPERATORS_MAP: Final[MappingProxyType[StrEnum, OperatorType]] = MappingProxyType(
    {
        OperatorScalar.EQ: operators.eq,
        OperatorScalar.NE: operators.ne,
        OperatorScalar.GT: operators.gt,
        OperatorScalar.GE: operators.ge,
        OperatorScalar.LT: operators.lt,
        OperatorScalar.LE: operators.le,
        OperatorStr.LIKE: operators.like_op,
        OperatorStr.ILIKE: operators.ilike_op,
        OperatorList.IN: operators.in_op,
        OperatorList.NOT_IN: operators.not_in_op,
        OperatorNull.IS_NULL: operators.is_,
        OperatorNull.IS_NOT_NULL: operators.is_not,
    }
)


_SORT_DIRECTION_MAP: Final[MappingProxyType[StrEnum, Callable]] = MappingProxyType(
    {
        SortDirection.ASC: asc,
        SortDirection.DESC: desc,
    }
)


class SAAbstractReader[EntityT: Entity, ORMT: BaseORM](ABC):
    _model: ClassVar[type[BaseORM]]

    _filter_map: ClassVar[MappingProxyType[StrEnum, InstrumentedAttribute]]
    _sort_map: ClassVar[MappingProxyType[StrEnum, InstrumentedAttribute]]

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    @abstractmethod
    def _to_domain(self, orm_obj: ORMT) -> EntityT:
        raise NotImplementedError

    async def _execute[T](self, query: Select[tuple[T]]) -> Result[tuple[T]]:
        try:
            return await self._session.execute(query)
        except SQLAlchemyError as e:
            raise OperationFailedError from e

    async def _search(
        self,
        filter: Filter | None = None,
        sort: Sort | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
        *,
        base_query: Select[tuple[ORMT]] | None = None,
    ) -> PaginationResult[EntityT]:
        query: Select | None = base_query
        if query is None:
            query = select(self._model)

        query = self._apply_filter(query, filter)
        query = self._apply_sort(query, sort)

        # Count total before pagination
        total: int = await self._count(query)

        query = self._apply_pagination(query, pagination)

        result: Result[tuple[ORMT]] = await self._execute(query)
        items: list[EntityT] = [self._to_domain(row) for row in result.scalars().unique().all()]

        meta = PaginationResultMeta(
            page=pagination.page,
            page_size=pagination.page_size,
            total=total,
        )
        return PaginationResult(data=items, meta=meta)

    async def _count(self, query: Select[tuple[ORMT]]) -> int:
        count_query: Select[tuple[int]] = select(func.count()).select_from(query.subquery())
        result: Result[tuple[int]] = await self._execute(count_query)
        return result.scalar_one()

    def _apply_filter(
        self,
        query: Select[tuple[ORMT]],
        filter: Filter | None,
    ) -> Select[tuple[ORMT]]:
        if filter is None or not filter.params:
            return query

        for param in filter.params:
            operator: OperatorType = _OPERATORS_MAP[param.operator]
            column: InstrumentedAttribute = self._filter_map[param.field]
            query = query.where(operator(column, param.value))

        return query

    def _apply_sort(
        self,
        query: Select[tuple[ORMT]],
        sort: Sort | None,
    ) -> Select[tuple[ORMT]]:
        if sort is None or not sort.params:
            return query

        for param in sort.params:
            direction: Callable = _SORT_DIRECTION_MAP[param.direction]
            column: InstrumentedAttribute = self._sort_map[param.field]
            query = query.order_by(direction(column))

        return query

    def _apply_pagination(
        self,
        query: Select[tuple[ORMT]],
        pagination: Pagination,
    ) -> Select[tuple[ORMT]]:
        return query.offset(pagination.offset).limit(pagination.limit)
