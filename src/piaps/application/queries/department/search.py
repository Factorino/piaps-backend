from typing import TYPE_CHECKING

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.query.filter import Filter
from piaps.application.common.dto.query.pagination import (
    DEFAULT_PAGINATION,
    Pagination,
    PaginationResult,
)
from piaps.application.common.dto.query.sort import Sort
from piaps.application.common.dto.views.department import DepartmentView
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.readers.department import (
    DepartmentFilterField,
    DepartmentSortField,
    IDepartmentReader,
)
from piaps.domain.entities.user import User
from piaps.domain.enums.user_role import UserRole


if TYPE_CHECKING:
    from piaps.domain.entities.department import Department


@dto
class SearchDepartmentsRequest:
    filter: Filter[DepartmentFilterField] | None = None
    sort: Sort[DepartmentSortField] | None = None
    pagination: Pagination = DEFAULT_PAGINATION


@dto
class SearchDepartmentsResponse:
    result: PaginationResult[DepartmentView]


class SearchDepartments(Interactor[SearchDepartmentsRequest, SearchDepartmentsResponse]):
    def __init__(
        self,
        department_reader: IDepartmentReader,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._department_reader: IDepartmentReader = department_reader
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: SearchDepartmentsRequest) -> SearchDepartmentsResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        result: PaginationResult[Department] = await self._department_reader.search(
            filter=request.filter,
            sort=request.sort,
            pagination=request.pagination,
        )

        data: list[DepartmentView] = [DepartmentView.from_domain(dep) for dep in result.data]
        return SearchDepartmentsResponse(result=PaginationResult(data=data, meta=result.meta))

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ACCOUNTANT:
            raise AccessDeniedError("You don't have permission to read departments")
