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
from piaps.domain.entities.employee import EmployeeId
from piaps.domain.entities.user import User, UserId
from piaps.domain.value_objects.username import Username


class UserFilterField(StrEnum):
    USERNAME = "username"
    ROLE = "role"


class UserSortField(StrEnum):
    USERNAME = "username"
    ROLE = "role"


class IUserReader(Protocol):
    @abstractmethod
    async def find_by_id(self, id: UserId) -> User | None: ...

    @abstractmethod
    async def find_by_username(self, username: Username) -> User | None: ...


    @abstractmethod
    async def find_by_employee_id(self, employee_id: EmployeeId) -> User | None: ...

    @abstractmethod
    async def search(
        self,
        filter: Filter[UserFilterField] | None = None,
        sort: Sort[UserSortField] | None = None,
        pagination: Pagination = DEFAULT_PAGINATION,
    ) -> PaginationResult[User]: ...
