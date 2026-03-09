from typing import TYPE_CHECKING

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.user import UserDTO
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor


if TYPE_CHECKING:
    from piaps.domain.entities.user import User


@dto
class GetCurrentUserResponse:
    user: UserDTO


class GetCurrentUser(Interactor[None, GetCurrentUserResponse]):
    def __init__(
        self,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: None = None) -> GetCurrentUserResponse:  # noqa: ARG002
        current_user: User = await self._idp.get_user()
        return GetCurrentUserResponse(user=UserDTO.from_domain(current_user))
