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
from piaps.application.interfaces.readers.employee import (
    EmployeeFilterField,
    EmployeeSortField,
)
from piaps.domain.entities.employee import Employee, EmployeeId
from piaps.domain.value_objects.code import Code
from piaps.domain.value_objects.full_name import FullName
from piaps.infrastructure.database.common.mapper import get_mapper
from piaps.infrastructure.database.models.employee import EmployeeORM
from piaps.infrastructure.database.readers.base import SAAbstractReader


_to_domain: Callable[[EmployeeORM], Employee] = get_mapper(
    EmployeeORM,
    Employee,
    recipe=[
        link(P[EmployeeORM].code, P[Employee].code, coercer=Code.from_str),
        link(P[EmployeeORM].full_name, P[Employee].full_name, coercer=FullName.from_str),
    ],
)


class SAEmployeeReader(SAAbstractReader[Employee, EmployeeORM]):
    _model = EmployeeORM

    _filter_map: ClassVar[MappingProxyType[StrEnum, InstrumentedAttribute]] = MappingProxyType(
        {
            EmployeeFilterField.CODE: EmployeeORM.code,
            EmployeeFilterField.FULL_NAME: EmployeeORM.full_name,
            EmployeeFilterField.HIRE_DATE: EmployeeORM.hire_date,
            EmployeeFilterField.DEPARTMENT_ID: EmployeeORM.department_id,
            EmployeeFilterField.POSITION_ID: EmployeeORM.position_id,
        }
    )

    _sort_map: ClassVar[MappingProxyType[StrEnum, InstrumentedAttribute]] = MappingProxyType(
        {
            EmployeeSortField.CODE: EmployeeORM.code,
            EmployeeSortField.FULL_NAME: EmployeeORM.full_name,
            EmployeeSortField.HIRE_DATE: EmployeeORM.hire_date,
        }
    )

    async def find_by_id(self, id: EmployeeId) -> Employee | None:
        return await self._find(EmployeeORM.id == id)

    async def find_by_code(self, code: Code) -> Employee | None:
        return await self._find(EmployeeORM.code == code.value)

    async def search(
        self,
        filter: Filter[EmployeeFilterField] | None = None,
        sort: Sort[EmployeeSortField] | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
    ) -> PaginationResult[Employee]:
        return await self._search(filter, sort, pagination)

    def _to_domain(self, orm_obj: EmployeeORM) -> Employee:
        return _to_domain(orm_obj)
