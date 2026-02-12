from abc import abstractmethod
from enum import StrEnum
from typing import Protocol
from uuid import UUID

from piaps.application.common.query.filter import Filter
from piaps.application.common.query.pagination import Pagination, PaginationResult
from piaps.application.common.query.sort import Sort
from piaps.domain.entities.user import User


class UserFilterField(StrEnum):
    ID = "id"
    LOGIN = "login"
    ROLE = "role"
    EMPLOYEE_ID = "employee_id"


class UserSortField(StrEnum):
    ID = "id"
    LOGIN = "login"
    ROLE = "role"


class IUserReader(Protocol):
    @abstractmethod
    async def find_by_id(self, id: UUID) -> User | None: ...

    @abstractmethod
    async def find_all(
        self,
        filter: Filter[UserFilterField] | None = None,
        sort: Sort[UserSortField] | None = None,
        pagination: Pagination | None = None,
    ) -> PaginationResult[User]: ...
