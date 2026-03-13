from collections.abc import Callable
from enum import StrEnum
from types import MappingProxyType
from typing import ClassVar

from adaptix import P
from adaptix.conversion import link
from sqlalchemy.orm import InstrumentedAttribute

from piaps.application.common.dto.query.filter import Filter
from piaps.application.common.dto.query.pagination import (
    DEFAULT_PAGINATION,
    Pagination,
    PaginationResult,
)
from piaps.application.common.dto.query.sort import Sort
from piaps.application.interfaces.readers.department import (
    DepartmentFilterField,
    DepartmentSortField,
)
from piaps.domain.entities.department import Department, DepartmentId
from piaps.domain.value_objects.code import Code
from piaps.domain.value_objects.name import Name
from piaps.infrastructure.database.common.mapper import get_mapper
from piaps.infrastructure.database.models.department import DepartmentORM
from piaps.infrastructure.database.readers.base import SAAbstractReader


_to_domain: Callable[[DepartmentORM], Department] = get_mapper(
    DepartmentORM,
    Department,
    recipe=[
        link(P[DepartmentORM].code, P[Department].code, coercer=Code.from_str),
        link(P[DepartmentORM].name, P[Department].name, coercer=lambda n: Name(value=n)),
    ],
)


class SADepartmentReader(SAAbstractReader[Department, DepartmentORM]):
    _model = DepartmentORM

    _filter_map: ClassVar[MappingProxyType[StrEnum, InstrumentedAttribute]] = MappingProxyType(
        {
            DepartmentFilterField.CODE: DepartmentORM.code,
            DepartmentFilterField.NAME: DepartmentORM.name,
        }
    )

    _sort_map: ClassVar[MappingProxyType[StrEnum, InstrumentedAttribute]] = MappingProxyType(
        {
            DepartmentSortField.CODE: DepartmentORM.code,
            DepartmentSortField.NAME: DepartmentORM.name,
        }
    )

    async def find_by_id(self, id: DepartmentId) -> Department | None:
        return await self._find(DepartmentORM.id == id)

    async def find_by_code(self, code: Code) -> Department | None:
        return await self._find(DepartmentORM.code == code.value)

    async def find_by_name(self, name: Name) -> Department | None:
        return await self._find(DepartmentORM.name == name.value)

    async def search(
        self,
        filter: Filter[DepartmentFilterField] | None = None,
        sort: Sort[DepartmentSortField] | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
    ) -> PaginationResult[Department]:
        return await self._search(filter, sort, pagination)

    def _to_domain(self, orm_obj: DepartmentORM) -> Department:
        return _to_domain(orm_obj)
