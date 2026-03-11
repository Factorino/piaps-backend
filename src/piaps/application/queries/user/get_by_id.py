from piaps.application.common.dto.base import dto
from piaps.application.common.dto.views.user import UserView
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.readers.user import IUserReader
from piaps.domain.entities.user import User, UserId
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import NotFoundError


@dto
class GetUserByIdRequest:
    id: UserId


@dto
class GetUserByIdResponse:
    user: UserView


class GetUserById(Interactor[GetUserByIdRequest, GetUserByIdResponse]):
    def __init__(
        self,
        user_reader: IUserReader,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._user_reader: IUserReader = user_reader
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: GetUserByIdRequest) -> GetUserByIdResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user, request.id)

        user: User | None = await self._user_reader.find_by_id(request.id)
        if user is None:
            raise NotFoundError(f"User with id '{request.id}' not found")

        return GetUserByIdResponse(user=UserView.from_domain(user))

    def _check_access(self, current_user: User, target_user_id: UserId) -> None:
        if current_user.role < UserRole.ADMINISTRATOR and current_user.id != target_user_id:
            raise NotFoundError(f"User with id '{target_user_id}' not found")
