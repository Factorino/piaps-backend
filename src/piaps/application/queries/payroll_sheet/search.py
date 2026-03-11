from typing import TYPE_CHECKING

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.payroll_sheet import PayrollSheetDTO
from piaps.application.common.query.filter import Filter
from piaps.application.common.query.pagination import (
    DEFAULT_PAGINATION,
    Pagination,
    PaginationResult,
)
from piaps.application.common.query.sort import Sort
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.readers.payroll_sheet import (
    IPayrollSheetReader,
    PayrollSheetFilterField,
    PayrollSheetSortField,
)
from piaps.domain.entities.user import User
from piaps.domain.enums.user_role import UserRole


if TYPE_CHECKING:
    from piaps.domain.entities.payroll_sheet import PayrollSheet


@dto
class SearchPayrollSheetsRequest:
    filter: Filter[PayrollSheetFilterField] | None = None
    sort: Sort[PayrollSheetSortField] | None = None
    pagination: Pagination = DEFAULT_PAGINATION


@dto
class SearchPayrollSheetsResponse:
    result: PaginationResult[PayrollSheetDTO]


class SearchPayrollSheets(Interactor[SearchPayrollSheetsRequest, SearchPayrollSheetsResponse]):
    def __init__(
        self,
        payroll_sheet_reader: IPayrollSheetReader,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._payroll_sheet_reader: IPayrollSheetReader = payroll_sheet_reader
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: SearchPayrollSheetsRequest) -> SearchPayrollSheetsResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        result: PaginationResult[PayrollSheet] = await self._payroll_sheet_reader.search(
            filter=request.filter,
            sort=request.sort,
            pagination=request.pagination,
        )

        data: list[PayrollSheetDTO] = [PayrollSheetDTO.from_domain(sheet) for sheet in result.data]
        return SearchPayrollSheetsResponse(result=PaginationResult(data=data, meta=result.meta))

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ACCOUNTANT:
            raise AccessDeniedError("You don't have permission to read payroll sheets")
