from typing import TYPE_CHECKING

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.query.filter import Filter
from piaps.application.common.dto.query.pagination import (
    DEFAULT_PAGINATION,
    Pagination,
    PaginationResult,
)
from piaps.application.common.dto.query.sort import Sort
from piaps.application.common.dto.views.employee import EmployeeView
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.readers.employee import (
    EmployeeFilterField,
    EmployeeSortField,
    IEmployeeReader,
)
from piaps.domain.entities.user import User
from piaps.domain.enums.user_role import UserRole


if TYPE_CHECKING:
    from piaps.domain.entities.employee import Employee


@dto
class SearchEmployeesRequest:
    filter: Filter[EmployeeFilterField] | None = None
    sort: Sort[EmployeeSortField] | None = None
    pagination: Pagination = DEFAULT_PAGINATION


@dto
class SearchEmployeesResponse:
    result: PaginationResult[EmployeeView]


class SearchEmployees(Interactor[SearchEmployeesRequest, SearchEmployeesResponse]):
    def __init__(
        self,
        employee_reader: IEmployeeReader,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._employee_reader: IEmployeeReader = employee_reader
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: SearchEmployeesRequest) -> SearchEmployeesResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        result: PaginationResult[Employee] = await self._employee_reader.search(
            filter=request.filter,
            sort=request.sort,
            pagination=request.pagination,
        )

        data: list[EmployeeView] = [EmployeeView.from_domain(empl) for empl in result.data]
        return SearchEmployeesResponse(result=PaginationResult(data=data, meta=result.meta))

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ACCOUNTANT:
            raise AccessDeniedError("You don't have permission to read employees")
