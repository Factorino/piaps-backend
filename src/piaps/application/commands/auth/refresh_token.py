from typing import TYPE_CHECKING

from piaps.application.common.dto.base import dto
from piaps.application.common.dto.views.user import UserView
from piaps.application.errors.auth import AuthenticationError, InvalidTokenError
from piaps.application.interfaces.auth.jwt_provider import (
    IJWTProvider,
    TokenData,
    TokenPayload,
    TokenType,
)
from piaps.application.interfaces.common.interactor import Interactor
from piaps.application.interfaces.readers.user import IUserReader


if TYPE_CHECKING:
    from piaps.domain.entities.user import User


@dto
class RefreshTokenRequest:
    refresh_token: str


@dto
class RefreshTokenResponse:
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"  # noqa: S105
    user: UserView


class RefreshToken(Interactor[RefreshTokenRequest, RefreshTokenResponse]):
    def __init__(
        self,
        user_reader: IUserReader,
        jwt_provider: IJWTProvider,
    ) -> None:
        self._user_reader: IUserReader = user_reader
        self._jwt_provider: IJWTProvider = jwt_provider

    async def execute(self, request: RefreshTokenRequest) -> RefreshTokenResponse:
        decoded: TokenData = self._jwt_provider.decode_token(request.refresh_token)

        if decoded.type != TokenType.REFRESH:
            raise InvalidTokenError(f"Token type must be '{TokenType.REFRESH}'")

        user: User | None = await self._user_reader.find_by_id(decoded.sub)
        if user is None:
            raise AuthenticationError("User no longer exists")

        payload = TokenPayload(sub=user.id, role=user.role)
        access_token: str = self._jwt_provider.create_access_token(payload)
        refresh_token: str = self._jwt_provider.create_refresh_token(payload)

        return RefreshTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserView.from_domain(user),
        )
