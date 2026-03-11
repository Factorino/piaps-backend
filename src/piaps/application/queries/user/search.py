from piaps.application.common.dto.base import dto
from piaps.application.common.dto.query.filter import Filter
from piaps.application.common.dto.query.pagination import (
    DEFAULT_PAGINATION,
    Pagination,
    PaginationResult,
)
from piaps.application.common.dto.query.sort import Sort
from piaps.application.common.dto.views.user import UserView
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.readers.user import IUserReader, UserFilterField, UserSortField
from piaps.domain.entities.user import User
from piaps.domain.enums.user_role import UserRole


@dto
class SearchUsersRequest:
    filter: Filter[UserFilterField] | None = None
    sort: Sort[UserSortField] | None = None
    pagination: Pagination = DEFAULT_PAGINATION


@dto
class SearchUsersResponse:
    result: PaginationResult[UserView]


class SearchUsers(Interactor[SearchUsersRequest, SearchUsersResponse]):
    def __init__(
        self,
        user_reader: IUserReader,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._user_reader: IUserReader = user_reader
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: SearchUsersRequest) -> SearchUsersResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        result: PaginationResult[User] = await self._user_reader.search(
            filter=request.filter,
            sort=request.sort,
            pagination=request.pagination,
        )

        data: list[UserView] = [UserView.from_domain(user) for user in result.data]
        return SearchUsersResponse(result=PaginationResult(data=data, meta=result.meta))

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ADMINISTRATOR:
            raise AccessDeniedError("You don't have permission to read users")
