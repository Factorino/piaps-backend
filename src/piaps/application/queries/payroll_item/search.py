from typing import TYPE_CHECKING

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.query.filter import Filter
from piaps.application.common.dto.query.pagination import (
    DEFAULT_PAGINATION,
    Pagination,
    PaginationResult,
)
from piaps.application.common.dto.query.sort import Sort
from piaps.application.common.dto.views.payroll_item import PayrollItemView
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.readers.payroll_item import (
    IPayrollItemReader,
    PayrollItemFilterField,
    PayrollItemSortField,
)
from piaps.domain.entities.user import User
from piaps.domain.enums.user_role import UserRole


if TYPE_CHECKING:
    from piaps.domain.entities.payroll_item import PayrollItem


@dto
class SearchPayrollItemsRequest:
    filter: Filter[PayrollItemFilterField] | None = None
    sort: Sort[PayrollItemSortField] | None = None
    pagination: Pagination = DEFAULT_PAGINATION


@dto
class SearchPayrollItemsResponse:
    result: PaginationResult[PayrollItemView]


class SearchPayrollItems(Interactor[SearchPayrollItemsRequest, SearchPayrollItemsResponse]):
    def __init__(
        self,
        payroll_item_reader: IPayrollItemReader,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._payroll_item_reader: IPayrollItemReader = payroll_item_reader
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: SearchPayrollItemsRequest) -> SearchPayrollItemsResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        result: PaginationResult[PayrollItem] = await self._payroll_item_reader.search(
            filter=request.filter,
            sort=request.sort,
            pagination=request.pagination,
        )

        data: list[PayrollItemView] = [PayrollItemView.from_domain(item) for item in result.data]
        return SearchPayrollItemsResponse(result=PaginationResult(data=data, meta=result.meta))

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ACCOUNTANT:
            raise AccessDeniedError("You don't have permission to read payroll items")
