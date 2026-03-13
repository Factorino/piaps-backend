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
from piaps.application.interfaces.readers.user import (
    UserFilterField,
    UserSortField,
)
from piaps.domain.entities.employee import EmployeeId
from piaps.domain.entities.user import User, UserId
from piaps.domain.value_objects.username import Username
from piaps.infrastructure.database.common.mapper import get_mapper
from piaps.infrastructure.database.models.user import UserORM
from piaps.infrastructure.database.readers.base import SAAbstractReader


_to_domain: Callable[[UserORM], User] = get_mapper(
    UserORM,
    User,
    recipe=[
        link(P[UserORM].username, P[User].username, coercer=lambda u: Username(value=u)),
    ],
)


class SAUserReader(SAAbstractReader[User, UserORM]):
    _model = UserORM

    _filter_map: ClassVar[MappingProxyType[StrEnum, InstrumentedAttribute]] = MappingProxyType(
        {
            UserFilterField.USERNAME: UserORM.username,
            UserFilterField.ROLE: UserORM.role,
        }
    )

    _sort_map: ClassVar[MappingProxyType[StrEnum, InstrumentedAttribute]] = MappingProxyType(
        {
            UserSortField.USERNAME: UserORM.username,
            UserSortField.ROLE: UserORM.role,
        }
    )

    async def find_by_id(self, id: UserId) -> User | None:
        return await self._find(UserORM.id == id)

    async def find_by_username(self, username: Username) -> User | None:
        return await self._find(UserORM.username == username.value)

    async def find_by_employee(self, employee_id: EmployeeId) -> User | None:
        return await self._find(UserORM.employee_id == employee_id)

    async def search(
        self,
        filter: Filter[UserFilterField] | None = None,
        sort: Sort[UserSortField] | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
    ) -> PaginationResult[User]:
        return await self._search(filter, sort, pagination)

    def _to_domain(self, orm_obj: UserORM) -> User:
        return _to_domain(orm_obj)
