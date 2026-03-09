from typing import TYPE_CHECKING

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.position import PositionDTO
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
from piaps.application.interfaces.readers.position import (
    IPositionReader,
    PositionFilterField,
    PositionSortField,
)
from piaps.domain.entities.user import User
from piaps.domain.enums.user_role import UserRole


if TYPE_CHECKING:
    from piaps.domain.entities.position import Position


@dto
class SearchPositionsRequest:
    filter: Filter[PositionFilterField] | None = None
    sort: Sort[PositionSortField] | None = None
    pagination: Pagination = DEFAULT_PAGINATION


@dto
class SearchPositionsResponse:
    result: PaginationResult[PositionDTO]


class SearchPositions(Interactor[SearchPositionsRequest, SearchPositionsResponse]):
    def __init__(
        self,
        position_reader: IPositionReader,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._position_reader: IPositionReader = position_reader
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: SearchPositionsRequest) -> SearchPositionsResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        result: PaginationResult[Position] = await self._position_reader.search(
            filter=request.filter,
            sort=request.sort,
            pagination=request.pagination,
        )

        data: list[PositionDTO] = [PositionDTO.from_domain(pos) for pos in result.data]
        return SearchPositionsResponse(result=PaginationResult(data=data, meta=result.meta))

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ACCOUNTANT:
            raise AccessDeniedError("You don't have permission to read positions")
