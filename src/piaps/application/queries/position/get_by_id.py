from piaps.application.common.dto.base import dto
from piaps.application.common.dto.views.position import PositionView
from piaps.application.errors.auth import AccessDeniedError
from piaps.application.interfaces.auth.identity_provider import IIdentityProvider
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.readers.position import IPositionReader
from piaps.domain.entities.position import Position, PositionId
from piaps.domain.entities.user import User
from piaps.domain.enums.user_role import UserRole
from piaps.domain.errors.base import NotFoundError


@dto
class GetPositionByIdRequest:
    id: PositionId


@dto
class GetPositionByIdResponse:
    user: PositionView


class GetPositionById(Interactor[GetPositionByIdRequest, GetPositionByIdResponse]):
    def __init__(
        self,
        position_reader: IPositionReader,
        identity_provider: IIdentityProvider,
    ) -> None:
        self._position_reader: IPositionReader = position_reader
        self._idp: IIdentityProvider = identity_provider

    async def execute(self, request: GetPositionByIdRequest) -> GetPositionByIdResponse:
        current_user: User = await self._idp.get_user()
        self._check_access(current_user)

        position: Position | None = await self._position_reader.find_by_id(request.id)
        if position is None:
            raise NotFoundError(f"Position with id '{request.id}' not found")

        return GetPositionByIdResponse(user=PositionView.from_domain(position))

    def _check_access(self, current_user: User) -> None:
        if current_user.role < UserRole.ACCOUNTANT:
            raise AccessDeniedError("You don't have permission to read positions")
